"""Null-model pipeline check over the case corpus (UNLOGGED; not a scoring run, no engine involved).

Runs the four pre-registration-candidate nulls (spec\\scoring.md section 4) on cases\\ with the v1 null
inputs built from amber's lake (read-only), prints overall and per-era regime/thesis/expression/action
scores and the era-A regime permutation test. Owner decision 2026-10-06: run outside
``prereg.record_run`` until the registration set is reviewed and registered.

    .\\.venv\\Scripts\\python.exe tools\\null_smoke.py [--n-perm 1000] [--split research]

Default: the research split (spec\\HOLDOUT.md). ``--split holdout|all`` needs ``--unseal-reason`` and the
environment variable FATPITCH_UNSEAL=1, and appends a line to cases\\UNSEAL_LOG.txt.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path

import polars as pl

from fatpitch.cases import (
    AlwaysRiskOn,
    FedDirectionOnly,
    Persistence,
    Trend12m,
    load_corpus,
    permutation_test,
    run,
    tilt_baselines,
)
from fatpitch.cases.scoring import PredictionCache
from fatpitch.source import FixtureSource

ROOT = Path(__file__).resolve().parents[1]
AMBER = Path(os.environ.get("AMBER_DATA", r"C:\Users\<user>\Documents\amber\data"))
NY = "America/New_York"


def _fred(sid: str) -> pl.DataFrame:
    df = pl.read_parquet(AMBER / "lake" / "fred" / "series" / f"{sid}.parquet")
    return (df.filter(pl.col("published_at").is_not_null() & pl.col("value").is_not_null())
              .select("value", "period_end", pl.col("published_at").dt.convert_time_zone(NY),
                      pl.col("as_of").cast(pl.Utf8).alias("vintage_id")))


def _us_market() -> pl.DataFrame:
    """US market total-return index from Ken French daily factors (Mkt-RF + RF), published at 18:00 ET of
    the return date (closing prices are observable that day). SPY proxy for the 12-month trend null."""
    ff = pl.read_parquet(AMBER / "lake" / "french" / "daily" / "ff5_mom.parquet").sort("date")
    idx = ff.select(pl.col("date").alias("period_end"),
                    (1 + pl.col("Mkt-RF") + pl.col("RF")).cum_prod().mul(100).alias("value"))
    return idx.with_columns(
        pl.col("period_end").cast(pl.Datetime("us")).dt.offset_by("18h").dt.replace_time_zone(NY).alias("published_at"),
        pl.lit("french-ff5-daily").alias("vintage_id"))


def _usd_broad() -> pl.DataFrame:
    """DTWEXM (major currencies) to 2005-12-30, DTWEXBGS (broad) from 2006-01-02, the later series rescaled to
    match DTWEXM on the first common date (no data after that date is used for the scale)."""
    old, new = _fred("DTWEXM"), _fred("DTWEXBGS")
    start = new["period_end"].min()
    common = old.filter(pl.col("period_end") == start)
    scale = common["value"][0] / new.filter(pl.col("period_end") == start)["value"][0]
    return pl.concat([old.filter(pl.col("period_end") < start),
                      new.with_columns(pl.col("value") * scale)]).sort("period_end")


def source() -> FixtureSource:
    return FixtureSource({"FEDFUNDS": _fred("FEDFUNDS"), "DGS10": _fred("DGS10"), "USD_BROAD": _usd_broad(),
                          "US_MKT": _us_market()})


def nulls(corpus) -> list:
    return [AlwaysRiskOn(), FedDirectionOnly(series_id="FEDFUNDS"),
            Trend12m(series={"US_MKT": ("equity", "US", 1), "DGS10": ("rates", "US", -1),
                             "USD_BROAD": ("fx", "USD", 1)}, regime_series="DGS10"),
            Persistence(corpus)]


def _f(x) -> str:
    return "  n/a" if x is None else f"{x:5.3f}"


def _n_scored(res, comp: str) -> tuple[int, int]:
    sc = [x for x in res.case_scores if x.get(comp) is not None]
    return len(sc), len({x.episode_id for x in sc})


def _block(title, subsets, nulls_, src, a) -> None:
    """Scores of every null on each subset; permutation test (regime and thesis) on the gate subset."""
    names = list(subsets)
    print(f"\n== {title}")
    print(f"{'null':22s} {'comp':10s} " + " ".join(f"{k:>12s}" for k in names))
    for n in nulls_:
        cache = PredictionCache(n, src)
        res = {k: run(n, v, src, cache=cache) for k, v in subsets.items()}
        for comp in ("regime", "thesis", "expression", "action"):
            print(f"{n.name:22s} {comp:10s} " + " ".join(f"{_f(res[k].overall[comp]):>12s}" for k in names))
        gate = subsets[names[1]]
        for comp in ("regime", "thesis"):
            pt = permutation_test(n, gate, src, component=comp, n_perm=a.n_perm, seed=a.seed, cache=cache)
            print(f"{n.name:22s} perm {names[1]} {comp} observed {pt.observed:.3f} p {pt.p_value:.3f} "
                  f"(N {a.n_perm}, seed {a.seed})")
    first = run(nulls_[0], subsets[names[1]], src)
    for comp in ("regime", "thesis"):
        nc, ne = _n_scored(first, comp)
        print(f"scored on {names[1]}: {comp} {nc} cases / {ne} episodes")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261006)
    ap.add_argument("--split", choices=("research", "holdout", "all"), default="research")
    ap.add_argument("--unseal-reason", default=None)
    a = ap.parse_args(argv)
    corpus = load_corpus(ROOT / "cases", split=a.split, unseal=a.split != "research", reason=a.unseal_reason)
    src = source()
    tp = corpus.subset(turning_point=True)
    print(f"UNLOGGED null-model pipeline check {dt.datetime.now(dt.UTC).isoformat(timespec='seconds')}; "
          f"split {corpus.split}; corpus {corpus.sha256[:16]}; cases {len(corpus)}; episodes {len(corpus.episodes)}; "
          f"turning points {len(tp)} (A {len(tp.subset(era='A'))}, B {len(tp.subset(era='B'))})")
    _block("full corpus", {"all": corpus, "era A": corpus.subset(era="A"), "era B": corpus.subset(era="B")},
           nulls(corpus), src, a)
    _block("turning-point cases (Gate 1 subset = era A)",
           {"TP all": tp, "TP era A": tp.subset(era="A"), "TP era B": tp.subset(era="B")}, nulls(corpus), src, a)
    f13 = [c for c in corpus.cases if c.targets.tilt]
    print("\n== 13F tilt-sign agreement (reported, not gated)")
    for n in tilt_baselines(corpus):
        res = run(n, f13, src)
        per = ", ".join(f"{s.case_id[:10]} {_f(s.tilt)}" for s in res.case_scores)
        print(f"{n.name:24s} tilt {_f(res.overall['tilt'])}  ({per})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
