"""Snapshot access for rule functions: numpy views of point-in-time frames, usability and freshness.

A rule never sees a row that is not visible at ``asof`` (the ``Source`` already filtered on
``published_at <= asof``). This module adds three mechanical guards, none of them a process parameter:

* ``usable``: rows with ``usable = False`` (D-graded proxies, pre-vintage rows under policy ``unknown``,
  gap rows; ``fatpitch.lake``) are dropped. A frame without a ``usable`` column (``FixtureSource``) is
  fully usable.
* freshness: a series whose newest usable period is older than the availability bound of
  ``spec\\data_coverage.md`` (the larger of D 10 d, W 21 d, M 75 d, Q 200 d, A 760 d by observed spacing
  and the rows' own cadence = publication lag + 1.5 x median spacing + 7 d) is unknown at
  ``asof`` (a discontinued archive must not be read as a current level). Publication lag here is the largest
  lag among the newest 60 usable rows, not the coverage report's median: batch-published daily series (Ken
  French files, posted monthly) would otherwise read as stale for part of every month.
* lag lookup: the value ``window`` before a date is the observation nearest to the target date within
  half the series' median spacing (minimum 3 days); none -> unknown.

Dates are integer days since 1970-01-01 (period_end); ``asof_day`` is the ET calendar date of ``asof``.
"""

from __future__ import annotations

import calendar
import datetime as _dt
from dataclasses import dataclass, field

import numpy as np
import polars as pl

EPOCH = _dt.date(1970, 1, 1)
US_PER_DAY = 86_400_000_000
FRESH_BOUND_DAYS = ((3, 10), (10, 21), (40, 75), (120, 200), (10**9, 760))  # (max spacing, bound): D W M Q A


def day(d: _dt.date) -> int:
    return (d - EPOCH).days


def date_of(n: int) -> _dt.date:
    return EPOCH + _dt.timedelta(days=int(n))


def add_months(d: _dt.date, months: int) -> _dt.date:
    y, m = divmod(d.year * 12 + (d.month - 1) + months, 12)
    m += 1
    return _dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def months_back(n_day: int, months: int) -> int:
    return day(add_months(date_of(n_day), -months))


def months_back_arr(days: np.ndarray, months: int) -> np.ndarray:
    """Vectorised ``months_back`` (day of month clamped to the target month's end)."""
    d = days.astype("datetime64[D]")
    m = d.astype("datetime64[M]")
    offset = (d - m.astype("datetime64[D]")).astype(np.int64)
    tm = m - np.timedelta64(months, "M")
    month_len = ((tm + np.timedelta64(1, "M")).astype("datetime64[D]") - tm.astype("datetime64[D]")).astype(np.int64)
    out = tm.astype("datetime64[D]") + np.minimum(offset, month_len - 1).astype("timedelta64[D]")
    return out.astype(np.int64)


@dataclass
class Series:
    """One series at ``asof``: usable rows sorted by period_end."""

    sid: str
    days: np.ndarray            # int64 period_end days
    values: np.ndarray          # float64
    pub_us: np.ndarray          # int64 publication time, microseconds since the epoch (UTC)
    grades: tuple = ()
    _spacing: float | None = field(default=None, repr=False)

    @classmethod
    def from_frame(cls, sid: str, frame: pl.DataFrame) -> Series | None:
        if frame is None or frame.is_empty():
            return None
        f = frame
        if "usable" in f.columns:
            f = f.filter(pl.col("usable").fill_null(False))
        f = f.filter(pl.col("value").is_not_null() & pl.col("value").is_not_nan())
        if f.is_empty():
            return None
        days = f["period_end"].to_physical().to_numpy().astype(np.int64)
        vals = f["value"].to_numpy().astype(np.float64)
        pub = f["published_at"].to_physical().to_numpy().astype(np.int64)
        order = np.argsort(days, kind="stable")
        if not np.all(order == np.arange(len(order))):
            days, vals, pub = days[order], vals[order], pub[order]
        grades = tuple(f["proxy_grade"].unique().to_list()) if "proxy_grade" in f.columns else ()
        return cls(sid, days, vals, pub, grades)

    @property
    def pub_days(self) -> np.ndarray:
        return self.pub_us.astype(np.float64) / US_PER_DAY

    def published_at(self, i: int) -> _dt.datetime:
        from fatpitch.dates import NY
        return (_dt.datetime(1970, 1, 1, tzinfo=_dt.UTC) + _dt.timedelta(microseconds=int(self.pub_us[i]))).astimezone(NY)

    def __len__(self) -> int:
        return len(self.days)

    @property
    def last_day(self) -> int:
        return int(self.days[-1])

    @property
    def last(self) -> float:
        return float(self.values[-1])

    def spacing(self) -> float:
        if self._spacing is None:
            d = np.diff(self.days[-31:])
            self._spacing = float(np.median(d)) if len(d) else 1.0
        return self._spacing

    def fresh(self, asof_day: int) -> bool:
        sp = self.spacing()
        bound = next(b for lim, b in FRESH_BOUND_DAYS if sp <= lim)
        tail = slice(-60, None)
        lag = float(np.max(self.pub_days[tail] - self.days[tail])) if len(self) else 0.0
        cadence = lag + 1.5 * sp + 7.0
        return asof_day - self.last_day <= max(bound, cadence)

    def tol(self) -> float:
        return max(3.0, self.spacing() / 2.0)

    def nearest_idx(self, target: int, tol: float | None = None) -> int | None:
        tol = self.tol() if tol is None else tol
        i = int(np.searchsorted(self.days, target))
        best, bd = None, None
        for j in (i - 1, i):
            if 0 <= j < len(self.days):
                dd = abs(int(self.days[j]) - target)
                if dd <= tol and (bd is None or dd < bd):
                    best, bd = j, dd
        return best

    def nearest(self, target: int, tol: float | None = None) -> float | None:
        j = self.nearest_idx(target, tol)
        return None if j is None else float(self.values[j])

    def asof_value(self, target: int, max_age: float | None = None) -> float | None:
        """Last value with period_end <= target (optionally no older than ``max_age`` days)."""
        i = int(np.searchsorted(self.days, target, side="right")) - 1
        if i < 0:
            return None
        if max_age is not None and target - int(self.days[i]) > max_age:
            return None
        return float(self.values[i])

    def asof_array(self, targets: np.ndarray, max_age: float | None = None) -> np.ndarray:
        idx = np.searchsorted(self.days, targets, side="right") - 1
        out = np.where(idx >= 0, self.values[np.clip(idx, 0, None)], np.nan)
        if max_age is not None:
            age = targets - self.days[np.clip(idx, 0, None)]
            out = np.where(age <= max_age, out, np.nan)
        return out

    def nearest_array(self, targets: np.ndarray, tol: float | None = None) -> np.ndarray:
        tol = self.tol() if tol is None else tol
        i = np.searchsorted(self.days, targets)
        lo = np.clip(i - 1, 0, len(self.days) - 1)
        hi = np.clip(i, 0, len(self.days) - 1)
        dlo = np.abs(self.days[lo] - targets)
        dhi = np.abs(self.days[hi] - targets)
        pick = np.where(dhi < dlo, hi, lo)
        dist = np.minimum(dlo, dhi)
        return np.where(dist <= tol, self.values[pick], np.nan)

    def change(self, months: int | None = None, days_back: int | None = None,
               end_idx: int = -1) -> float | None:
        """value[end] - value nearest to (end - window)."""
        end = int(self.days[end_idx])
        target = months_back(end, months) if months is not None else end - int(days_back)
        v0 = self.nearest(target)
        return None if v0 is None else float(self.values[end_idx]) - v0


class Snap:
    """Lazy numpy views of one snapshot. ``get`` returns None when the series is absent, has no usable
    row, or (``fresh=True``, default) fails the freshness guard; the reason is kept in ``why``."""

    def __init__(self, frames: dict[str, pl.DataFrame], asof: _dt.datetime):
        self.frames = frames
        self.asof = asof
        self.asof_day = day(asof.date())
        self._cache: dict[str, Series | None] = {}
        self.why: dict[str, str] = {}
        self.used: set[str] = set()

    def raw(self, sid: str) -> Series | None:
        if sid not in self._cache:
            self._cache[sid] = Series.from_frame(sid, self.frames.get(sid))
        return self._cache[sid]

    def get(self, sid: str, fresh: bool = True) -> Series | None:
        s = self.raw(sid)
        if s is None:
            self.why[sid] = "missing" if sid not in self.frames or self.frames[sid].is_empty() else "unusable"
            return None
        if fresh and not s.fresh(self.asof_day):
            self.why[sid] = f"stale (newest usable period {date_of(s.last_day)})"
            return None
        self.used.add(sid)
        return s

    def first(self, *sids: str, fresh: bool = True) -> Series | None:
        for sid in sids:
            s = self.get(sid, fresh=fresh)
            if s is not None:
                return s
        return None

    def reason(self, *sids: str) -> str:
        return "; ".join(f"{s}: {self.why.get(s, 'unavailable')}" for s in sids)


def sign(x: float | None, eps: float = 0.0) -> int | None:
    if x is None or not np.isfinite(x):
        return None
    return 1 if x > eps else (-1 if x < -eps else 0)


def confirmed_state(raw: list[int | None], k: int) -> tuple[int | None, int | None]:
    """Confirmation filter (liq.confirm_periods, internals.turn_confirm_m): the state changes only after
    ``k`` consecutive equal raw observations. Equivalent closed form: the value of the most recent run of
    at least ``k`` equal, known raw states. Returns (state, index where that run started); (None, None)
    when no such run exists in ``raw`` (oldest first)."""
    run_val, run_len = None, 0
    best = (None, None)
    start = None
    for i, v in enumerate(raw):
        if v is not None and v == run_val:
            run_len += 1
        else:
            run_val, run_len, start = v, (1 if v is not None else 0), i
        if run_val is not None and run_len == max(k, 1) and run_val != best[0]:
            best = (run_val, start)
    return best
