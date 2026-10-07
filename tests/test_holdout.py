"""Sealed research/holdout split (fatpitch.cases.holdout; spec/HOLDOUT.md): deterministic stratified draw, default
research load, sealed refusal, tamper detection, unseal logging. Synthetic corpora in tmp_path; the project
holdout is checked through its hash only."""

import datetime as dt
import hashlib
import shutil
from pathlib import Path

import pytest
import yaml

from fatpitch.cases import HoldoutError, load_corpus
from fatpitch.cases import holdout as ho
from fatpitch.cases.schema import _load_files
from fatpitch.dates import is_trading_day

ROOT = Path(__file__).resolve().parents[1]


def _td(y: int, m: int, d: int) -> str:
    day = dt.date(y, m, d)
    while not is_trading_day(day):
        day += dt.timedelta(days=1)
    return day.isoformat()


def _write(root: Path, cid: str, date: str, episode: str, era: str, targets: dict) -> Path:
    d = {"id": cid, "asof": date, "era": era, "episode_id": episode, "truth_type": "action", "mechanizable": "yes",
         "source_reliability": "primary", "targets": targets}
    p = root / f"{date}_{cid}.yaml"
    p.write_text(yaml.safe_dump(d, sort_keys=False), encoding="utf-8")
    return p


def _corpus(root: Path) -> Path:
    """10 episodes: 4 Gate 1 (era A, easing -> tightening within the episode), 2 with 13F cases, 2 era B,
    2 era-A fillers. Episodes are >= 2 years apart so the 18-month lookback never crosses episodes."""
    root.mkdir(parents=True, exist_ok=True)
    for i, y in enumerate((2004, 2007, 2010, 2013)):
        ep = f"G{i}"
        _write(root, f"g{i}a", _td(y, 3, 3), ep, "A",
               {"regime_direction": "easing", "theses": [{"asset_class": "rates", "direction": "long"}]})
        _write(root, f"g{i}b", _td(y, 6, 2), ep, "A",
               {"regime_direction": "tightening", "theses": [{"asset_class": "rates", "direction": "short"}]})
    for i, y in enumerate((2016, 2019)):
        _write(root, f"f{i}", _td(y, 8, 14), f"F{i}", "A", {"tilt": {"equity_us_tech": 1}})
    for i, y in enumerate((1990, 1995)):
        _write(root, f"b{i}", _td(y, 5, 1), f"B{i}", "B", {"theses": [{"asset_class": "fx", "direction": "short"}]})
    for i, y in enumerate((2022, 2025)):
        _write(root, f"x{i}", _td(y, 4, 1), f"X{i}", "A", {"action": "hold"})
    return root


@pytest.fixture
def sealed(tmp_path):
    root = _corpus(tmp_path / "cases")
    spec = ho.create(root, seed=ho.SEED, now=dt.datetime(2026, 10, 6, tzinfo=dt.UTC))
    return root, spec


def test_draw_is_deterministic_and_stratified(tmp_path):
    a, b = _corpus(tmp_path / "a"), _corpus(tmp_path / "b")
    ca, cb = _load_files(ho.case_files(a), a), _load_files(ho.case_files(b), b)
    hold = ho.draw(ca)
    assert hold == ho.draw(cb) == ho.draw(list(reversed(ca)))
    assert sum(e.startswith("G") for e in hold) == 2                  # ceil(4 / 2) Gate 1 episodes
    assert sum(e.startswith("F") for e in hold) == 1                  # 13F episodes split across sets
    assert any(e.startswith("B") for e in hold)                       # at least one era-B episode
    assert len(hold) >= round(10 / 3)
    assert any(ho.draw(ca, seed=s) != hold for s in range(1, 30))     # the seed matters


def test_create_records_hashes_and_refuses_redraw(sealed):
    root, spec = sealed
    research, hold = ho.partition(root, spec["holdout_episodes"])
    assert spec["holdout_sha256"] == ho.corpus_sha256(hold, root)
    assert spec["research_sha256"] == ho.corpus_sha256(research, root)
    assert spec["holdout_n_cases"] + spec["research_n_cases"] == 14
    assert {ho.episode_of(f) for f in hold} == set(spec["holdout_episodes"])   # episodes never split
    assert not {ho.episode_of(f) for f in hold} & {ho.episode_of(f) for f in research}
    with pytest.raises(HoldoutError, match="sealed once"):
        ho.create(root)


def test_reseal_redraws_and_keeps_previous_version(sealed, monkeypatch):
    root, v1 = sealed
    with pytest.raises(HoldoutError, match="reason"):
        ho.reseal(root, " ")
    # a case added to a held-out episode breaks the seal; a documented re-seal restores a consistent split
    _write(root, "add1", _td(2016, 9, 1), v1["holdout_episodes"][0], "A", {"action": "hold"})
    with pytest.raises(HoldoutError, match="hash mismatch"):
        load_corpus(root)
    v1_bytes = (root / ho.HOLDOUT_FILE).read_bytes()
    v2 = ho.reseal(root, "corpus expansion before scoring", now=dt.datetime(2026, 10, 7, tzinfo=dt.UTC))
    assert v2["version"] == 2 and v2["seed"] == v1["seed"] and v2["method"] == v1["method"]
    prev = v2["previous"][-1]
    assert prev["version"] == 1 and prev["holdout_sha256"] == v1["holdout_sha256"]
    assert prev["holdout_episodes"] == v1["holdout_episodes"] and prev["full_sha256"] == v1["full_sha256"]
    assert prev["holdout_yaml_sha256"] == hashlib.sha256(v1_bytes).hexdigest()
    assert v2["holdout_n_cases"] + v2["research_n_cases"] == 15
    assert ho.read_spec(root)["version"] == 2 and len(load_corpus(root)) == v2["research_n_cases"]
    # once opened, the holdout can no longer be re-sealed
    monkeypatch.setenv(ho.UNSEAL_ENV, "1")
    load_corpus(root, split="holdout", unseal=True, reason="final test")
    with pytest.raises(HoldoutError, match="opened"):
        ho.reseal(root, "again")


def test_default_load_is_research(sealed):
    root, spec = sealed
    c = load_corpus(root)
    assert c.split == "research" and c.sha256 == spec["research_sha256"]
    assert not set(c.episodes) & set(spec["holdout_episodes"])
    assert len(c) == spec["research_n_cases"]
    assert not (root / ho.UNSEAL_LOG).exists()


@pytest.mark.parametrize("split", ["holdout", "all"])
def test_sealed_refusal(sealed, monkeypatch, split):
    root, _ = sealed
    monkeypatch.delenv(ho.UNSEAL_ENV, raising=False)
    with pytest.raises(HoldoutError, match="unseal=True"):
        load_corpus(root, split=split)
    with pytest.raises(HoldoutError, match=ho.UNSEAL_ENV):
        load_corpus(root, split=split, unseal=True, reason="final test")
    monkeypatch.setenv(ho.UNSEAL_ENV, "0")
    with pytest.raises(HoldoutError, match=ho.UNSEAL_ENV):
        load_corpus(root, split=split, unseal=True, reason="final test")
    monkeypatch.setenv(ho.UNSEAL_ENV, "1")
    for reason in (None, "", "   "):
        with pytest.raises(HoldoutError, match="reason"):
            load_corpus(root, split=split, unseal=True, reason=reason)
    assert not (root / ho.UNSEAL_LOG).exists()
    with pytest.raises(ValueError, match="split"):
        load_corpus(root, split="train")


def test_unseal_logs_append_only(sealed, monkeypatch):
    root, spec = sealed
    monkeypatch.setenv(ho.UNSEAL_ENV, "1")
    h = load_corpus(root, split="holdout", unseal=True, reason="final Gate 1\ntest")
    assert h.split == "holdout" and h.sha256 == spec["holdout_sha256"]
    assert set(h.episodes) == set(spec["holdout_episodes"]) and len(h) == spec["holdout_n_cases"]
    full = load_corpus(root, split="all", unseal=True, reason="Gate 2")
    assert len(full) == 14 and full.sha256 == spec["full_sha256"]
    assert h.turning == full.turning                                   # holdout turning derived on the full corpus
    lines = (root / ho.UNSEAL_LOG).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert "split=holdout" in lines[0] and f"holdout_sha256={spec['holdout_sha256']}" in lines[0]
    assert "sha_verified=yes" in lines[0] and "reason=final Gate 1 test" in lines[0] and "user=" in lines[0]
    assert "split=all" in lines[1] and "reason=Gate 2" in lines[1]
    load_corpus(root)                                                   # research loads are not logged
    assert len((root / ho.UNSEAL_LOG).read_text(encoding="utf-8").splitlines()) == 2


def test_tamper_detection(sealed, monkeypatch):
    root, spec = sealed
    _, hold = ho.partition(root, spec["holdout_episodes"])
    original = hold[0].read_bytes()
    hold[0].write_bytes(original.replace(b"primary", b"secondary"))
    with pytest.raises(HoldoutError, match="hash mismatch"):
        load_corpus(root)                                               # research load also refuses
    monkeypatch.setenv(ho.UNSEAL_ENV, "1")
    with pytest.raises(HoldoutError, match="hash mismatch"):
        load_corpus(root, split="holdout", unseal=True, reason="x")
    assert not (root / ho.UNSEAL_LOG).exists()
    hold[0].write_bytes(original)
    load_corpus(root)
    # a research case moved into a holdout episode changes the holdout file set
    research, _ = ho.partition(root, spec["holdout_episodes"])
    d = yaml.safe_load(research[0].read_text(encoding="utf-8"))
    d["episode_id"] = spec["holdout_episodes"][0]
    research[0].write_text(yaml.safe_dump(d, sort_keys=False), encoding="utf-8")
    with pytest.raises(HoldoutError, match="hash mismatch"):
        load_corpus(root)


def test_research_edits_do_not_trip_the_seal(sealed):
    root, spec = sealed
    research, _ = ho.partition(root, spec["holdout_episodes"])
    research[0].write_text(research[0].read_text(encoding="utf-8").replace("primary", "secondary"),
                           encoding="utf-8")
    c = load_corpus(root)
    assert c.sha256 != spec["research_sha256"]


def test_unsplit_dirs_and_missing_project_seal(tmp_path, monkeypatch):
    root = _corpus(tmp_path / "plain")
    assert load_corpus(root).split == "unsplit" and len(load_corpus(root)) == 14
    with pytest.raises(HoldoutError, match="no holdout"):
        load_corpus(root, split="holdout")
    monkeypatch.setattr(ho, "REPO_CASES", root)
    with pytest.raises(HoldoutError, match="missing"):
        load_corpus(root)


def test_project_holdout_verifies(tmp_path):
    spec = ho.read_spec(ROOT / "cases")
    assert spec["seed"] == 20261006 and len(spec["holdout_episodes"]) >= 1
    _, hold, sha = ho.verify(ROOT / "cases")
    assert sha == spec["holdout_sha256"] and len(hold) == spec["holdout_n_cases"]
    copy = tmp_path / "cases"
    shutil.copytree(ROOT / "cases", copy, ignore=shutil.ignore_patterns(ho.UNSEAL_LOG))
    victim = next(f for f in ho.case_files(copy) if f.name == hold[0].name)
    victim.write_bytes(victim.read_bytes() + b"\n")
    with pytest.raises(HoldoutError, match="hash mismatch"):
        load_corpus(copy)
