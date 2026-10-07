"""Spec-version runner (fatpitch.versions): adapter, trial log, worktree logic, end-to-end on a temp git repo."""

import json
import subprocess

import pytest
import yaml

from fatpitch.cases import Prediction, ThesisTarget
from fatpitch.dates import et_close
from fatpitch.decision import Decision, Exit, Expression, RegimeVector, Signal, Thesis
from fatpitch.source import FixtureSource
from fatpitch.versions import compare as cmp
from fatpitch.versions import gitops, trials
from fatpitch.versions.adapter import decision_to_prediction
from fatpitch.versions.runner import Paths, run_version

# -------------------------------------------------------------------- adapter


def _decision(**kw):
    import datetime as dt
    return Decision(asof=et_close(dt.date(2015, 3, 2)), engine_version="t", registry_sha="r", **kw)


def test_adapter_stub_decision_is_flat_and_empty():
    p = decision_to_prediction(_decision())
    assert p == Prediction(None, (), (), "flat", ())


def test_adapter_maps_fields_and_prefers_us_regime():
    d = _decision(regime=[RegimeVector("EA", "tightening"), RegimeVector("US", "easing")],
                  theses=[Thesis("t1", "rates", "long", "US"), Thesis("t2", "fx", "short", "JPY")],
                  expressions=[Expression("t2", "6J", "fx_jpy", "short", 2), Expression("t1", "ZN", "rates_us", "long", 1),
                               Expression("t1", "ZF", "rates_us", "long", 3)],
                  signals=[Signal("s1", "t1", "ZN", "long", "starter")], no_pitch=False)
    p = decision_to_prediction(d)
    assert p.regime_direction == "easing"
    assert p.theses == (ThesisTarget("rates", "long", "US"), ThesisTarget("fx", "short", "JPY"))
    assert p.expressions == ("rates_us", "fx_jpy")
    assert p.action == "enter"
    assert decision_to_prediction(d.to_dict()) == p  # dict form (driver output) maps identically


def test_adapter_action_priority():
    import datetime as dt
    ex = [Exit("s0", None, "premise broken", et_close(dt.date(2016, 11, 9)))]
    assert decision_to_prediction(_decision(exits=ex, no_pitch=False)).action == "exit"
    assert decision_to_prediction(_decision(exits=ex, signals=[Signal("s1", "t", "GC", "short", "starter")],
                                            no_pitch=False)).action == "reverse"
    assert decision_to_prediction(_decision(signals=[Signal("s1", "t", "GC", "long", "fat_pitch")],
                                            no_pitch=False)).action == "size_up"
    assert decision_to_prediction(_decision(signals=[Signal("s1", "t", "GC", "long", "watch")])).action == "flat"
    assert decision_to_prediction({"no_pitch": False}).action is None


# -------------------------------------------------------------------- trial log


def test_holm_and_bonferroni():
    assert trials.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert trials.holm([0.5, None]) == [pytest.approx(1.0), None]
    assert trials.bonferroni(0.03, 5) == pytest.approx(0.15)
    assert trials.bonferroni(0.5, 5) == 1.0


def test_trial_log_counts_engine_runs_only(tmp_path):
    p = tmp_path / "trials.jsonl"
    assert trials.count(p) == 0
    trials.append(p, {"kind": "null", "label": "null_x"})
    r1 = trials.append(p, {"kind": "tag", "label": "v1", "commit": "a", "summary": {"gate1_p": 0.02}})
    r2 = trials.append(p, {"kind": "wip", "label": "wip", "commit": "a", "wip_fingerprint": "f",
                           "summary": {"gate1_p": 0.2}})
    trials.append(p, {"kind": "tag", "label": "v1", "commit": "a", "summary": {"gate1_p": 0.02}})
    assert (r1["trial"], r2["trial"]) == (1, 2)
    assert trials.count(p) == 3 and trials.distinct(p) == 2
    adj = trials.adjusted(p, "gate1_p")
    assert adj[1]["bonferroni"] == pytest.approx(0.06) and adj[1]["n"] == 3
    assert p.read_bytes().count(b"\r") == 0


# -------------------------------------------------------------------- git fixture


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false",
                    *args], check=True, capture_output=True)


FAKE_DATES = '''
import datetime as dt
from zoneinfo import ZoneInfo

def et_close(d):
    return dt.datetime(d.year, d.month, d.day, 16, tzinfo=ZoneInfo("America/New_York"))
'''

FAKE_SOURCE = '''
class AmberSource:
    def __init__(self, root=None):
        self.root = root

    def snapshot(self, asof):
        return {}
'''

FAKE_INIT = '''
__version__ = "{version}"
REGIME = "{regime}"

def evaluate(asof, source, registry=None):
    return {{"asof": asof.isoformat(), "engine_version": __version__, "registry_sha": "reg-" + __version__,
            "regime": [{{"region": "US", "policy_direction": REGIME}}],
            "theses": [{{"asset_class": "rates", "direction": "long", "region": "US"}}],
            "expressions": [{{"family": "rates_us", "rank": 1}}], "signals": [], "exits": [], "no_pitch": True}}
'''


def _write_version(repo, version, regime):
    pkg = repo / "src" / "fatpitch"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text(FAKE_INIT.format(version=version, regime=regime), encoding="utf-8")
    (pkg / "dates.py").write_text(FAKE_DATES, encoding="utf-8")
    (pkg / "source.py").write_text(FAKE_SOURCE, encoding="utf-8")
    (repo / "spec").mkdir(exist_ok=True)
    (repo / "spec" / "registry.yaml").write_text(f"# registry {version}\n", encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "master")
    _write_version(r, "9.9", "easing")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "v9.9")
    _git(r, "tag", "spec-v9.9")
    _write_version(r, "10.0", "tightening")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "v10")
    return r


def test_worktree_materialises_tag_and_cleans_up(repo):
    c = gitops.resolve_commit(repo, "spec-v9.9")
    assert gitops.is_tag(repo, "spec-v9.9") and not gitops.is_tag(repo, "master")
    with gitops.worktree(repo, c) as wt:
        assert 'REGIME = "easing"' in (wt / "src" / "fatpitch" / "__init__.py").read_text(encoding="utf-8")
        assert gitops.head(wt) == c
    assert not wt.exists()
    assert len(gitops.git(repo, "worktree", "list").splitlines()) == 1
    assert 'REGIME = "tightening"' in (repo / "src" / "fatpitch" / "__init__.py").read_text(encoding="utf-8")


def test_worktree_removed_on_error(repo):
    with pytest.raises(RuntimeError), gitops.worktree(repo, gitops.head(repo)) as wt:
        raise RuntimeError("boom")
    assert not wt.exists()
    assert len(gitops.git(repo, "worktree", "list").splitlines()) == 1


def test_wip_fingerprint_tracks_uncommitted_changes(repo):
    clean = gitops.wip_fingerprint(repo)
    (repo / "spec" / "new.md").write_text("x", encoding="utf-8")
    assert gitops.wip_fingerprint(repo) != clean
    assert "spec/new.md" in gitops.dirty_paths(repo, ["spec"])


# -------------------------------------------------------------------- end to end


def _case(cid, asof, regime, episode, era="A"):
    return {"id": cid, "asof": asof, "era": era, "episode_id": episode, "truth_type": "action", "mechanizable": "yes",
            "source_reliability": "primary",
            "targets": {"regime_direction": regime, "theses": [{"asset_class": "rates", "direction": "long", "region": "US"}],
                        "expression": ["rates_us"], "action": "enter"}}


@pytest.fixture
def paths(tmp_path, repo):
    cases = tmp_path / "cases"
    cases.mkdir()
    for d in (_case("c0", "1995-03-01", "tightening", "E0", era="B"), _case("c1", "2015-03-02", "easing", "E1"), _case("c2", "2016-01-04", "tightening", "E2"),
              _case("c3", "2016-06-01", "easing", "E3")):
        (cases / f"{d['asof']}_{d['id']}.yaml").write_text(yaml.safe_dump(d), encoding="utf-8")
    amber = tmp_path / "amber"
    amber.mkdir()
    return Paths(repo=repo, cases_root=cases, results=tmp_path / "results" / "versions", amber_data=amber)


def test_end_to_end_tag_wip_compare_leaderboard(paths, repo):
    empty = FixtureSource({})
    d1 = run_version("spec-v9.9", paths, null_source_override=empty, quiet=True)
    meta = json.loads((d1 / "meta.json").read_text(encoding="utf-8"))
    sc = json.loads((d1 / "scores.json").read_text(encoding="utf-8"))
    assert meta["trial"] == 1 and meta["kind"] == "tag"
    assert meta["version"]["commit"] == gitops.resolve_commit(repo, "spec-v9.9")
    assert meta["registry_sha"] == "reg-9.9"                       # the version's own code ran
    assert "wt-" in meta["engine"]["fatpitch_file"]                 # from the temporary worktree
    assert meta["corpus"]["n_cases"] == 4
    assert sc["overall"]["thesis"] == 1.0 and sc["overall"]["expression"] == 1.0
    assert sc["overall"]["regime"] == pytest.approx(0.5)            # easing everywhere: c0, c2 miss
    assert (d1 / "predictions.parquet").exists()
    assert len(gitops.git(repo, "worktree", "list").splitlines()) == 1
    g1 = sc["gates"]["gate1"]                                       # Gate 1 = every regime case, era A and B
    assert g1["definition"] == "rps-skill-v3" and g1["case_ids"] == ["c0", "c1", "c2", "c3"] and g1["k"] == 4
    assert g1["counts"]["B"] == {"n_cases": 1, "k": 1, "easing": 0, "neutral": 0, "tightening": 1}
    assert g1["counts"]["all"]["tightening"] == 2 and set(g1["by_era"]) == {"A", "B"}
    assert g1["class_balanced_rps"] == 1.0 and len(g1["episodes"]) == 4
    assert {e["episode_id"]: e["era"] for e in g1["episodes"]}["E0"] == "B"
    assert g1["rps_model"] == 1.0                                   # fake version emits no probabilities: worst
    refs = g1["references"]
    assert set(refs) == {"climatology_loeo", "null_trend_12m", "null_always_risk_on"} and g1["complete"]
    assert refs["null_trend_12m"]["rps"] == 1.0 and refs["null_trend_12m"]["skill"] == 0.0  # no data: missing
    assert refs["null_trend_12m"]["p_value"] == 1.0 and refs["null_trend_12m"]["wins"] == 0
    assert refs["climatology_loeo"]["skill"] < 0 and refs["null_always_risk_on"]["skill"] < 0
    assert g1["binding_p"] == 1.0 and g1["research_pass"] is False and g1["min_attainable_p"] == 0.0625
    assert "path_agreement_8" in sc["diagnostics"] and len(sc["diagnostics"]["turning_points_9"]) == 2
    assert len(sc["diagnostics"]["turning_points_9_excluded"]) == 1          # 1995 -> 2015: interval > 36 months

    # uncommitted candidate: working tree (v10 regime tightening) plus a dirty spec file
    (repo / "spec" / "draft.md").write_text("draft", encoding="utf-8")
    d2 = run_version(gitops.WIP, paths, null_source_override=empty, quiet=True)
    m2 = json.loads((d2 / "meta.json").read_text(encoding="utf-8"))
    assert m2["label"] == "wip" and m2["kind"] == "wip" and m2["trial"] == 2
    assert m2["registry_sha"] == "reg-10.0" and m2["version"]["wip_fingerprint"]
    assert trials.count(paths.trials) == 2
    g1w = json.loads((d2 / "scores.json").read_text(encoding="utf-8"))["gates"]["gate1"]
    assert g1w["rps_model"] == 1.0 and g1w["research_pass"] is False

    c = cmp.compare(paths, "spec-v9.9", "wip")
    reg = next(r for r in c["rows"] if r["subset"] == "full" and r["component"] == "regime")
    assert reg["n"] == 4 and sorted(reg["a_better"]) == ["c1", "c3"] and sorted(reg["b_better"]) == ["c0", "c2"]
    assert "A better" in cmp.compare_markdown(c)
    g = c["gate1_rps"]
    assert g["k"] == 4 and g["a_wins"] == g["b_wins"] == 0 and "regime RPS" in cmp.compare_markdown(c)
    vs_null = cmp.compare(paths, "spec-v9.9", "null_always_risk_on")
    assert vs_null["b"] == "null_always_risk_on"

    md = paths.leaderboard.read_text(encoding="utf-8")
    assert "spec-v9.9" in md and "wip" in md and "null_trend_12m" in md and "Gate 1 headroom" in md
    lb = json.loads((paths.results / "LEADERBOARD.json").read_text(encoding="utf-8"))
    assert lb["n_trials"] == 2
    assert {r["trial"] for r in lb["rows"] if r["kind"] != "null"} == {1, 2}


def test_failed_run_leaves_no_partial_directory_or_trial(paths, repo):
    (repo / "src" / "fatpitch" / "__init__.py").write_text("def evaluate(*a, **k):\n    raise ValueError('x')\n",
                                                          encoding="utf-8")
    with pytest.raises(RuntimeError, match="driver failed"):
        run_version(gitops.WIP, paths, null_source_override=FixtureSource({}), quiet=True)
    assert trials.count(paths.trials) == 0
    assert not (paths.results / "wip").exists() or not any((paths.results / "wip").iterdir())


def test_headroom_counts_winnable_cases(paths):
    from fatpitch.versions.runner import load_research, run_nulls

    corpus = load_research(paths)
    run_nulls(paths, source=FixtureSource({}), corpus=corpus, quiet=True)
    h = cmp.gate1_headroom(paths, corpus)
    assert h["k"] == 4 and h["winnable"] == 4 and h["min_p_exact"] == pytest.approx(0.0625)
    assert set(h["winnable_by_reference"]) == {"climatology_loeo", "null_trend_12m", "null_always_risk_on"}
    assert h["reachable"] is True and h["class_counts"] == {"easing": 2, "neutral": 0, "tightening": 2}
