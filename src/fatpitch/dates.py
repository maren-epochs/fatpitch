"""NYSE calendar and point-in-time time helpers.

Ported from multi-strategy ``cbp/data/dates.py``. Changes from the source:

* pandas removed; holidays are computed with the standard library (same rules as the pandas
  ``AbstractHolidayCalendar`` used in CBP).
* Martin Luther King Jr. Day starts 1998 (first NYSE closure for it); CBP used the pandas rule
  (start 1986), which is wrong for NYSE between 1986 and 1997.
* ``drop_incomplete_month`` works on a list of dates or a polars frame with a date column.
* Added: ``NY`` time zone, ``et_close``, ``trading_days``, ``shift_trading_days``, ``today``.

Rule (unchanged): a month counts as complete once the as-of date is on or after that month's last
NYSE trading day. Regular holidays only: New Year (Sunday -> Monday; Saturday -> no closure), MLK
(1998+), Presidents (1971+), Good Friday, Memorial (1971+), Juneteenth (2022+), Independence,
Labor, Thanksgiving, Christmas (Saturday -> Friday, Sunday -> Monday).

Known gap: pre-1971 Washington's Birthday (Feb 22) and Memorial Day (May 30), election days to
1980, the 1968 paperwork-crisis Wednesdays and unscheduled closures (9/11, hurricanes, national
mourning days) are not modelled.
"""

from __future__ import annotations

import datetime as _dt
from functools import lru_cache
from zoneinfo import ZoneInfo

import polars as pl

NY = ZoneInfo("America/New_York")
CLOSE = _dt.time(16, 0)


def today() -> _dt.date:
    """Current date in New York. Single clock hook: tests freeze it through ``tests/golden.py``."""
    return _dt.datetime.now(NY).date()


def _nearest_workday(d: _dt.date) -> _dt.date:
    if d.weekday() == 5:
        return d - _dt.timedelta(days=1)
    if d.weekday() == 6:
        return d + _dt.timedelta(days=1)
    return d


def _sunday_to_monday(d: _dt.date) -> _dt.date:
    return d + _dt.timedelta(days=1) if d.weekday() == 6 else d


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> _dt.date:
    d = _dt.date(year, month, 1)
    d += _dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + _dt.timedelta(weeks=n - 1)


def _last_weekday(year: int, month: int, weekday: int) -> _dt.date:
    nxt = _dt.date(year + (month == 12), month % 12 + 1, 1)
    d = nxt - _dt.timedelta(days=1)
    return d - _dt.timedelta(days=(d.weekday() - weekday) % 7)


def _easter(year: int) -> _dt.date:
    """Anonymous Gregorian computus."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    month = (h + m - 7 * n + 114) // 31
    day = (h + m - 7 * n + 114) % 31 + 1
    return _dt.date(year, month, day)


@lru_cache(maxsize=512)
def nyse_holidays(year: int) -> frozenset[_dt.date]:
    out = {
        _sunday_to_monday(_dt.date(year, 1, 1)),
        _easter(year) - _dt.timedelta(days=2),
        _dt.date(year, 7, 4),
        _nth_weekday(year, 9, 0, 1),
        _nth_weekday(year, 11, 3, 4),
        _dt.date(year, 12, 25),
    }
    out = {_nearest_workday(d) if d.month in (7, 12) else d for d in out}
    if year >= 1998:
        out.add(_nth_weekday(year, 1, 0, 3))
    if year >= 1971:
        out.add(_nth_weekday(year, 2, 0, 3))
        out.add(_last_weekday(year, 5, 0))
    if year >= 2022:
        out.add(_nearest_workday(_dt.date(year, 6, 19)))
    return frozenset(d for d in out if d.weekday() < 5)


def _as_date(d) -> _dt.date:
    if isinstance(d, _dt.datetime):
        return d.date()
    if isinstance(d, _dt.date):
        return d
    return _dt.date.fromisoformat(str(d)[:10])


def is_trading_day(d) -> bool:
    d = _as_date(d)
    return d.weekday() < 5 and d not in nyse_holidays(d.year)


def last_business_day(month_end) -> _dt.date:
    """Last Mon-Fri date of the month containing ``month_end``."""
    d = _as_date(month_end)
    d = _dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1) - _dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= _dt.timedelta(days=1)
    return d


def last_trading_day(month_end) -> _dt.date:
    """Last NYSE trading day of the month containing ``month_end``."""
    d = last_business_day(month_end)
    while not is_trading_day(d):
        d -= _dt.timedelta(days=1)
    return d


def trading_days(start, end) -> list[_dt.date]:
    """NYSE trading days in [start, end]."""
    d, end = _as_date(start), _as_date(end)
    out = []
    while d <= end:
        if is_trading_day(d):
            out.append(d)
        d += _dt.timedelta(days=1)
    return out


def shift_trading_days(d, n: int) -> _dt.date:
    """Trading day ``n`` sessions after (n > 0) or before (n < 0) ``d``. n = 0 rolls back to a
    trading day if ``d`` is not one."""
    d = _as_date(d)
    step = 1 if n > 0 else -1
    while not is_trading_day(d) and n == 0:
        d -= _dt.timedelta(days=1)
    k = abs(n)
    while k:
        d += _dt.timedelta(days=step)
        if is_trading_day(d):
            k -= 1
    return d


def et_close(d) -> _dt.datetime:
    """16:00 America/New_York on date ``d`` (case as-of convention: ET close)."""
    return _dt.datetime.combine(_as_date(d), CLOSE, tzinfo=NY)


def require_et(asof: _dt.datetime) -> _dt.datetime:
    """Validate that ``asof`` is a tz-aware datetime in America/New_York."""
    if not isinstance(asof, _dt.datetime):
        raise TypeError(f"asof must be a datetime, got {type(asof).__name__}")
    if asof.tzinfo is None or getattr(asof.tzinfo, "key", None) != "America/New_York":
        raise ValueError(f"asof must be tz-aware America/New_York, got tzinfo={asof.tzinfo!r}")
    return asof


def drop_incomplete_month(rows, asof=None, column: str = "period_end"):
    """Remove month-end rows whose month has not finished as of ``asof`` (default: today()).

    ``rows``: list of dates (returns a list) or a polars DataFrame (filters on ``column``).
    """
    asof_d = _as_date(asof) if asof is not None else today()
    if isinstance(rows, pl.DataFrame):
        if rows.is_empty():
            return rows
        keep = [asof_d >= last_trading_day(d) for d in rows[column].to_list()]
        return rows.filter(pl.Series(keep))
    return [d for d in rows if asof_d >= last_trading_day(d)]
