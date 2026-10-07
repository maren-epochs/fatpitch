"""Inputs for the four null models (spec/scoring.md section 4) from amber's lake, read-only.

Same construction as ``tools\\null_smoke.py`` (the v1 mapping in spec/scoring.md section 4):

| Series id | Content |
|---|---|
| ``FEDFUNDS`` | FRED ``FEDFUNDS`` (``null_fed_direction``) |
| ``DGS10`` | FRED ``DGS10``, sign -1 in ``null_trend_12m`` (IEF proxy; regime series) |
| ``USD_BROAD`` | FRED ``DTWEXM`` to 2005-12-30, ``DTWEXBGS`` from 2006-01-02 rescaled on the first common date (DXY proxy) |
| ``US_MKT`` | Ken French daily Mkt-RF + RF total-return index, published 18:00 ET of the return date (SPY proxy) |
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import polars as pl

from fatpitch.cases import AlwaysRiskOn, FedDirectionOnly, Persistence, Trend12m
from fatpitch.source import FixtureSource

NY = "America/New_York"
FRED_SERIES = ("FEDFUNDS", "DGS10", "DTWEXM", "DTWEXBGS")
FRENCH_FILE = ("french", "daily", "ff5_mom.parquet")
NULL_NAMES = ("null_always_risk_on", "null_fed_direction", "null_trend_12m", "null_persistence")
BEST_NULL = "null_trend_12m"  # Gate 2 best null, pre-chosen, spec/scoring.md section 7; never re-selected
# Gate 1 (regime RPS skill, option B, owner decisions 2026-10-07): references are LOEO climatology (computed in
# fatpitch.versions.score), null_trend_12m and null_always_risk_on (score.GATE1_REFERENCES); spec/scoring.md 6c
TREND_NULL = "null_trend_12m"


def input_files(amber_data: str | Path) -> list[Path]:
    lake = Path(amber_data) / "lake"
    return [lake / "fred" / "series" / f"{s}.parquet" for s in FRED_SERIES] + [lake.joinpath(*FRENCH_FILE)]


def lake_stamp(files: list[Path]) -> dict:
    """Data snapshot note: name, size, mtime of each file and a sha256 over them (not over the bytes)."""
    rows = []
    for f in sorted(files):
        st = f.stat() if f.exists() else None
        rows.append({"file": str(f), "size": st.st_size if st else None, "mtime_ns": st.st_mtime_ns if st else None})
    h = hashlib.sha256(repr([(r["file"], r["size"], r["mtime_ns"]) for r in rows]).encode()).hexdigest()
    return {"files": rows, "stamp_sha256": h}


def _fred(amber: Path, sid: str) -> pl.DataFrame:
    df = pl.read_parquet(amber / "lake" / "fred" / "series" / f"{sid}.parquet")
    return (df.filter(pl.col("published_at").is_not_null() & pl.col("value").is_not_null())
              .select("value", "period_end", pl.col("published_at").dt.convert_time_zone(NY),
                      pl.col("as_of").cast(pl.Utf8).alias("vintage_id")))


def _us_market(amber: Path) -> pl.DataFrame:
    ff = pl.read_parquet(amber.joinpath("lake", *FRENCH_FILE)).sort("date")
    idx = ff.select(pl.col("date").alias("period_end"),
                    (1 + pl.col("Mkt-RF") + pl.col("RF")).cum_prod().mul(100).alias("value"))
    return idx.with_columns(
        pl.col("period_end").cast(pl.Datetime("us")).dt.offset_by("18h").dt.replace_time_zone(NY).alias("published_at"),
        pl.lit("french-ff5-daily").alias("vintage_id"))


def _usd_broad(amber: Path) -> pl.DataFrame:
    old, new = _fred(amber, "DTWEXM"), _fred(amber, "DTWEXBGS")
    start = new["period_end"].min()
    scale = old.filter(pl.col("period_end") == start)["value"][0] / new.filter(pl.col("period_end") == start)["value"][0]
    return pl.concat([old.filter(pl.col("period_end") < start),
                      new.with_columns(pl.col("value") * scale)]).sort("period_end")


def null_source(amber_data: str | Path) -> FixtureSource:
    amber = Path(amber_data)
    return FixtureSource({"FEDFUNDS": _fred(amber, "FEDFUNDS"), "DGS10": _fred(amber, "DGS10"),
                          "USD_BROAD": _usd_broad(amber), "US_MKT": _us_market(amber)})


def null_engines(corpus) -> list:
    """The four nulls with the v1 series mapping (order = ``NULL_NAMES``)."""
    return [AlwaysRiskOn(), FedDirectionOnly(series_id="FEDFUNDS"),
            Trend12m(series={"US_MKT": ("equity", "US", 1), "DGS10": ("rates", "US", -1),
                             "USD_BROAD": ("fx", "USD", 1)}, regime_series="DGS10"),
            Persistence(corpus)]
