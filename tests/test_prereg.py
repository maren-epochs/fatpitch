"""fatpitch.prereg (port of CBP tests/test_prereg.py; csv instead of pandas)."""

import csv

import pytest

from fatpitch import prereg as pr


def _setup(tmp_path):
    design = tmp_path / "design.md"
    design.write_text("design v1\n", encoding="utf-8")
    return design, tmp_path / "reg.csv", tmp_path / "run_log.csv"


def test_default_storage_is_project_prereg_folder():
    assert pr.REGISTRY.parent.name == "prereg" and pr.RUN_LOG.parent == pr.REGISTRY.parent
    assert (pr.ROOT / "pyproject.toml").exists()


def test_a_edit_after_registration_fails(tmp_path):
    design, reg, _ = _setup(tmp_path)
    rid = pr.register(str(design), registry=reg, commit="abc", when="2026-09-23T10:00:00+00:00")
    assert rid == "PR-0001" and pr.verify(rid, registry=reg)["id"] == rid
    design.write_text("design v2\n", encoding="utf-8")
    with pytest.raises(pr.PreregError, match="changed after registration"):
        pr.verify(rid, registry=reg)


def test_b_registration_after_run_start_fails(tmp_path):
    design, reg, _ = _setup(tmp_path)
    rid = pr.register(str(design), registry=reg, commit="abc", when="2026-09-23T10:00:00+00:00")
    with pytest.raises(pr.PreregError, match="not before the run start"):
        pr.verify(rid, run_start_utc="2026-09-23T09:00:00+00:00", registry=reg)
    assert pr.verify(rid, run_start_utc="2026-09-23T11:00:00+00:00", registry=reg)


def test_c_relative_path_resolved_against_root(tmp_path):
    _design, reg, _ = _setup(tmp_path)
    rid = pr.register("design.md", registry=reg, root=tmp_path, commit="x")
    assert pr.verify(rid, registry=reg, root=tmp_path)["design_file"] == "design.md"
    assert pr.register_many(["design.md"], registry=reg, root=tmp_path, commit="x") == ["PR-0002"]


def test_d_run_log_row_and_e_posthoc_flag(tmp_path):
    design, reg, log = _setup(tmp_path)
    out = tmp_path / "out.csv"
    out.write_text("x\n")
    pr.record_run("fatpitch.demo", "--x", [out], log=log)
    with open(log, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1 and "out.csv=" in rows[0]["outputs"]
    assert pr.count_runs("fatpitch.demo", log=log) == 1 and pr.count_runs("other", log=log) == 0
    rid = pr.register(str(design), registry=reg, commit="abc", when="2099-01-01T00:00:00+00:00")
    flags = pr.posthoc_flags(rid, "fatpitch.demo", registry=reg, log=log)
    assert flags and "post-hoc risk" in flags[0]


def test_f_mechanical_needs_citation(tmp_path):
    design, reg, _ = _setup(tmp_path)
    with pytest.raises(pr.PreregError):
        pr.register(str(design), kind="mechanical", registry=reg)
    assert pr.register(str(design), kind="mechanical", cited_text="spec/process.md line 12", registry=reg,
                       commit="x")


def test_g_missing_file_and_unknown_id(tmp_path):
    _, reg, _ = _setup(tmp_path)
    with pytest.raises(pr.PreregError, match="not found"):
        pr.register(str(tmp_path / "nope.md"), registry=reg)
    with pytest.raises(pr.PreregError, match="not registered"):
        pr.verify("PR-9999", registry=reg)


def _project(tmp_path):
    """Minimal project: the E2 registration set (incl. a sealed cases/HOLDOUT.yaml), two cases and the real
    canonical registry."""
    import shutil
    from pathlib import Path

    real = Path(__file__).resolve().parents[1]
    (tmp_path / "spec").mkdir()
    (tmp_path / "cases").mkdir()
    shutil.copytree(real / "library", tmp_path / "library")
    shutil.copy(real / "spec" / "registry.yaml", tmp_path / "spec" / "registry.yaml")
    for f in ("process.md", "transition_table.yaml", "scoring.md"):
        (tmp_path / "spec" / f).write_text(f"{f} v1\n", encoding="utf-8")
    (tmp_path / "cases" / "2008-09-15_c1.yaml").write_text(
        "id: c1\nasof: 2008-09-15\nera: A\nepisode_id: e1\ntruth_type: action\nmechanizable: yes\n"
        "source_reliability: primary\ntargets: {regime_direction: easing}\n", encoding="utf-8")
    # second episode with a Gate 1 turning point: the seeded draw holds out e2, so c1 stays in research
    (tmp_path / "cases" / "2009-03-16_c2.yaml").write_text(
        "id: c2\nasof: 2009-03-16\nera: A\nepisode_id: e2\ntruth_type: action\nmechanizable: yes\n"
        "source_reliability: primary\ntargets: {regime_direction: tightening}\n", encoding="utf-8")
    from fatpitch.cases import holdout as ho

    spec = ho.create(tmp_path / "cases")                  # cases/HOLDOUT.yaml is part of PREREG_SET
    assert spec["holdout_episodes"] == ["e2"]
    return tmp_path


def test_register_all_requires_current_manifest(tmp_path):
    root = _project(tmp_path)
    reg = tmp_path / "prereg" / "reg.csv"
    with pytest.raises(pr.PreregError, match="missing or stale"):
        pr.register_all(root=root, registry=reg, commit="x")
    pr.write_corpus_manifest(root)
    text = (root / pr.MANIFEST).read_text(encoding="utf-8")
    assert "cases/2008-09-15_c1.yaml" in text and "corpus_sha256 " in text
    assert [f for f, _ in pr.pending(root)] == pr.PREREG_SET
    ids = pr.register_all(root=root, registry=reg, commit="x")
    assert ids == [f"PR-{i:04d}" for i in range(1, 7)] and pr.PREREG_SET[-1] == "cases/HOLDOUT.yaml"
    assert [r["design_file"] for r in pr.read_registry(reg)] == pr.PREREG_SET
    # a corpus change after manifest generation is refused
    (root / "cases" / "2008-09-15_c1.yaml").write_text(
        (root / "cases" / "2008-09-15_c1.yaml").read_text(encoding="utf-8").replace("easing", "tightening"),
        encoding="utf-8")
    with pytest.raises(pr.PreregError, match="stale"):
        pr.register_all(root=root, registry=reg, commit="x")
    assert all(pr.verify(i, registry=reg, root=root) for i in ids if i != "PR-0004")
