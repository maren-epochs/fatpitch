"""The E2 case corpus in cases\\: loads, meets PLAN E.7 acceptance, carries no outcome fields, citations resolve,
manifest hash matches. Reads repository files only (no network). Content checks run on the research split (the
default load); the sealed holdout (spec/HOLDOUT.md) is checked through its hash and recorded counts only."""

import datetime as dt
import re
from collections import Counter
from pathlib import Path

import pytest
import yaml

from fatpitch import prereg
from fatpitch.cases import Trend12m, load_corpus
from fatpitch.cases.holdout import case_files, full_digest, read_spec
from fatpitch.cases.schema import CASE_KEYS, META_KEYS
from fatpitch.dates import NY
from fatpitch.registry import CITE_RE, resolve_citation
from fatpitch.source import FixtureSource

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "cases"


@pytest.fixture(scope="module")
def corpus():
    return load_corpus(CASES)


def test_acceptance_counts(corpus):
    n_cases, n_eps, _ = full_digest(CASES)
    assert n_cases >= 30 and n_eps >= 10                                       # PLAN E.7 (E2), full corpus
    assert corpus.split == "research"
    eras = Counter(c.era for c in corpus.cases)
    assert eras["A"] > 0 and eras["B"] > 0
    assert all((c.era == "A") == (c.asof_date.year >= 2002) for c in corpus.cases)


def test_every_case_has_citation_and_date_basis(corpus):
    for c in corpus.cases:
        assert c.citation and c.date_basis.split(":")[0] in ("pinned", "conservative"), c.id
        assert c.asof.hour == 16 and c.asof.tzinfo.key == "America/New_York"


def test_no_outcome_or_hindsight_keys():
    allowed = CASE_KEYS | META_KEYS
    pat = re.compile(r"outcome|result|return|pnl|p&l|profit|loss|hindsight|afterward_market", re.IGNORECASE)
    for f in case_files(CASES):                # structural key check only; raw files, no scoring
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        assert set(doc) <= allowed, f.name
        keys = set(doc["targets"]) | set(doc)
        assert not [k for k in keys if pat.search(k)], f.name


def test_library_citations_resolve(corpus):
    for c in corpus.cases:
        refs = [(m.group(1), m.group(2)) for m in CITE_RE.finditer(c.citation)]
        for kind, name in refs:
            assert resolve_citation(kind, name, ROOT) is not None, (c.id, name)
        assert refs or "SEC EDGAR" in c.citation, c.id


def test_thirteen_f_cases_use_quarter_window_and_filed_date(corpus):
    f13 = [c for c in corpus.cases if "13F" in c.citation and "EDGAR" in c.citation]
    assert len(f13) == 1 and read_spec(CASES)["counts_full_corpus_turning"]["holdout"]["thirteen_f_cases"] == 1
    assert all(c.window.unit == "quarters" and c.window.n == 1 for c in f13)
    assert {c.asof_date for c in f13} <= {dt.date(2020, 8, 14), dt.date(2026, 2, 17)}


def test_manifest_matches_corpus(corpus):
    manifest = ROOT / "spec" / "corpus_manifest.txt"
    text = manifest.read_text(encoding="utf-8")
    assert f"corpus_sha256 {full_digest(CASES)[2]}" in text
    assert "HOLDOUT.yaml" not in text
    for f in case_files(CASES):
        assert f"{prereg.sha256_file(f)}  cases/{f.name}" in text


def test_trend_null_inverts_yield_series():
    import polars as pl
    pe = [dt.date(2007, 9, 14), dt.date(2008, 9, 12)]
    src = FixtureSource({"DGS10": pl.DataFrame({
        "value": [4.5, 3.7], "period_end": pe,
        "published_at": [dt.datetime.combine(p, dt.time(17), tzinfo=NY) for p in pe]})})
    p = Trend12m(series={"DGS10": ("rates", "US", -1)}, regime_series="DGS10").predict(
        dt.datetime(2008, 9, 15, 16, tzinfo=NY), src)
    assert p.regime_direction == "easing" and p.theses[0].direction == "long"


def test_turning_points_derived_from_targets(corpus):
    """Power checks on the sealed holdout's recorded counts. Owner decision 2026-10-07 (timing gate): at least 4
    holdout era-A turning-point cases with a regime target (min sign-flip p 2^-4 = 0.0625 < 0.10). Owner decision
    2026-10-07 (option B, spec/scoring.md section 6c) retired the timing gate; the regime gate's unit is the episode,
    so the holdout also needs at least 4 era-A episodes for an exact episode-level p < 0.10 (1/16 = 0.0625) in the
    one-time E7 report. The turning-point count is kept as a breakdown check."""
    from fatpitch.cases import turning_point_ids

    assert corpus.turning == turning_point_ids(corpus.cases)          # research split: derived on research only
    counts = read_spec(CASES)["counts_full_corpus_turning"]
    assert sum(counts[s]["gate1_cases"] for s in counts) >= 8         # full corpus Gate 1 sample (scoring.md 7)
    assert counts["holdout"]["gate1_cases"] >= 4                      # timing Gate 1: min p 2^-4 = 0.0625 < 0.10
    assert counts["holdout"]["era_A_episodes"] >= 4                   # option B: exact episode p floor 1/16


def test_thirteen_f_cases_carry_tilt_and_baseline(corpus):
    f13 = [c for c in corpus.cases if c.targets.tilt]
    assert len(f13) == 1 and all(c.baseline_tilt for c in f13)
    assert all({f for f, _ in c.targets.tilt} <= {f for f, _ in c.baseline_tilt} for c in f13)
