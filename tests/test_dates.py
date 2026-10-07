"""fatpitch.dates (port of CBP tests/test_dates.py; lists / polars instead of pandas)."""

import datetime as dt

import polars as pl
import pytest

from fatpitch import dates
from fatpitch.dates import (
    drop_incomplete_month,
    et_close,
    is_trading_day,
    last_business_day,
    last_trading_day,
    require_et,
    shift_trading_days,
    trading_days,
)

D = dt.date


def test_last_business_day_weekday_and_weekend():
    assert last_business_day(D(2026, 9, 30)) == D(2026, 9, 30)
    assert last_business_day(D(2026, 5, 31)) == D(2026, 5, 29)


def test_mid_month_row_dropped():
    assert drop_incomplete_month([D(2026, 8, 31), D(2026, 9, 30)], asof=D(2026, 9, 21)) == [D(2026, 8, 31)]


def test_rebalance_day_counts_as_complete():
    assert len(drop_incomplete_month([D(2026, 8, 31), D(2026, 9, 30)], asof=D(2026, 9, 30))) == 2


def test_weekend_month_end_complete_from_friday():
    assert drop_incomplete_month([D(2026, 5, 31)], asof=D(2026, 5, 28)) == []
    assert len(drop_incomplete_month([D(2026, 5, 31)], asof=D(2026, 5, 29))) == 1


def test_polars_input_not_modified_and_empty_ok():
    df = pl.DataFrame({"period_end": [D(2026, 9, 30)], "value": [1.0]})
    assert drop_incomplete_month(df, asof=D(2026, 9, 1)).is_empty()
    assert df.height == 1
    assert drop_incomplete_month(df.head(0)).is_empty()


def test_default_asof_uses_frozen_today():
    assert dates.today() == D(2026, 10, 6)           # tests/golden.py freezes the clock
    assert drop_incomplete_month([D(2026, 9, 30), D(2026, 10, 31)]) == [D(2026, 9, 30)]


def test_nyse_holidays_move_last_trading_day():
    assert last_trading_day(D(2024, 3, 31)) == D(2024, 3, 28)
    assert last_trading_day(D(2027, 5, 31)) == D(2027, 5, 28)
    assert last_trading_day(D(2026, 9, 30)) == D(2026, 9, 30)
    assert not is_trading_day("2026-12-25") and not is_trading_day("2026-07-03")
    assert is_trading_day("2027-12-31")
    assert not is_trading_day("2026-06-19") and is_trading_day("2021-06-18")


def test_holiday_month_complete_on_real_last_trading_day():
    assert drop_incomplete_month([D(2027, 5, 31)], asof=D(2027, 5, 27)) == []
    assert len(drop_incomplete_month([D(2027, 5, 31)], asof=D(2027, 5, 28))) == 1


@pytest.mark.parametrize("year,count", [(2019, 252), (2023, 250), (2024, 252)])
def test_trading_day_counts_match_nyse(year, count):
    assert len(trading_days(D(year, 1, 1), D(year, 12, 31))) == count


def test_mlk_from_1998_only():
    assert is_trading_day(D(1997, 1, 20)) and not is_trading_day(D(1998, 1, 19))


def test_shift_and_et_close():
    assert shift_trading_days(D(2024, 3, 27), 1) == D(2024, 3, 28)
    assert shift_trading_days(D(2024, 3, 28), 1) == D(2024, 4, 1)
    assert shift_trading_days(D(2024, 4, 1), -1) == D(2024, 3, 28)
    assert shift_trading_days(D(2024, 3, 30), 0) == D(2024, 3, 28)
    t = et_close(D(2024, 7, 1))
    assert t.hour == 16 and require_et(t) is t
    with pytest.raises(ValueError):
        require_et(dt.datetime(2024, 7, 1, 16))  # noqa: DTZ001
