"""Fake-lake fixtures for the step-1/1b rule tests (no amber data, no network)."""

from __future__ import annotations

import calendar
import datetime as dt

import polars as pl

from fatpitch import FixtureSource, registry
from fatpitch.dates import NY
from fatpitch.rules import step1
from fatpitch.rules.outputs import Params
from fatpitch.rules.series import Snap

REG = registry.load_default(check_citations=False)


def month_end(y: int, m: int) -> dt.date:
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def months(start: dt.date, n: int) -> list[dt.date]:
    out, y, m = [], start.year, start.month
    for _ in range(n):
        out.append(month_end(y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def frame(periods, values, pubs=None, lag_days: int = 1, hour: int = 8, usable=None) -> pl.DataFrame:
    pubs = pubs or [dt.datetime.combine(p + dt.timedelta(days=lag_days), dt.time(hour, 30), tzinfo=NY) for p in periods]
    d = {"value": [float(v) for v in values], "period_end": list(periods), "published_at": pubs,
         "vintage_id": ["v"] * len(periods)}
    df = pl.DataFrame(d, schema={"value": pl.Float64, "period_end": pl.Date,
                                 "published_at": pl.Datetime("us", "America/New_York"), "vintage_id": pl.Utf8})
    if usable is not None:
        df = df.with_columns(pl.Series("usable", usable if isinstance(usable, list) else [usable] * len(periods)))
    return df


def monthly(start: dt.date, values, lag_days: int = 15) -> pl.DataFrame:
    return frame(months(start, len(values)), values, lag_days=lag_days)


def daily(start: dt.date, values, lag_days: int = 0) -> pl.DataFrame:
    periods = [start + dt.timedelta(days=i) for i in range(len(values))]
    pubs = [dt.datetime.combine(p + dt.timedelta(days=lag_days), dt.time(15, 0), tzinfo=NY) for p in periods]
    return frame(periods, values, pubs=pubs)


def weekly(start: dt.date, values, lag_days: int = 1) -> pl.DataFrame:
    periods = [start + dt.timedelta(weeks=i) for i in range(len(values))]
    return frame(periods, values, lag_days=lag_days)


def quarterly(start: dt.date, values, lag_days: int = 30) -> pl.DataFrame:
    ps, y, q = [], start.year, (start.month - 1) // 3
    for _ in values:
        ps.append(month_end(y, 3 * q + 3))
        q += 1
        if q == 4:
            y, q = y + 1, 0
    return frame(ps, values, lag_days=lag_days)


def annual(start_year: int, values, lag_days: int = 31) -> pl.DataFrame:
    return frame([dt.date(start_year + i, 12, 31) for i in range(len(values))], values, lag_days=lag_days)


def et(d: dt.date) -> dt.datetime:
    return dt.datetime.combine(d, dt.time(16, 0), tzinfo=NY)


def ctx(asof: dt.date, frames: dict, reg=REG, source=None) -> step1.Ctx:
    """Ctx over the point-in-time view of ``frames`` at ``asof`` (FixtureSource applies published_at <= asof)."""
    src = source or FixtureSource({k: v.drop("usable") if "usable" in v.columns else v for k, v in frames.items()})
    snap = src.snapshot(et(asof))
    for k, v in frames.items():  # keep the usable flag (FixtureSource drops extra columns)
        if "usable" in v.columns:
            view = snap[k].join(v.select("period_end", "usable"), on="period_end", how="left")
            snap[k] = view
    return step1.Ctx(et(asof), Snap(snap, et(asof)), Params(reg), src)
