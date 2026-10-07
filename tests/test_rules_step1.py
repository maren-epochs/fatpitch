"""Step-1 rules (spec/process.md section 1): hand-computed fixtures, unknown propagation, point-in-time."""

import datetime as dt

import polars as pl
import pytest
from regime_fixtures import (
    REG,
    annual,
    ctx,
    daily,
    et,
    frame,
    months,
    quarterly,
    weekly,
)

from fatpitch import FixtureSource, registry
from fatpitch.dates import NY
from fatpitch.rules import step1
from fatpitch.rules.series import confirmed_state
from fatpitch.rules.step1 import _run_state

# ------------------------------------------------------------------ confirmation filter


def test_confirmation_filter():
    assert _run_state([1, 1, -1], 2) == 1                 # newest first: latest run of 2 is +1
    assert _run_state([-1, 1, 1], 2) == 1                 # one contrary observation does not flip
    assert _run_state([-1, -1, 1, 1], 2) == -1
    assert _run_state([1, None, 1], 2) is None            # unknown breaks a run
    assert confirmed_state([1, 1, -1, 1, 1], 2) == (1, 0)  # interruption without confirmation keeps the turn date
    assert confirmed_state([1, 1, -1, -1, 0], 2) == (-1, 2)


# ------------------------------------------------------------------ R-02


def _r02_frames():
    ms = months(dt.date(2000, 1, 31), 24)
    m2 = frame(ms, [100 * 1.10 ** (k / 12) for k in range(24)], lag_days=25)
    ip_first = [100 * 1.02 ** (k / 12) for k in range(24)]
    fr_pubs = [dt.datetime.combine(p + dt.timedelta(days=15), dt.time(9, 15), tzinfo=NY) for p in ms]
    # annual revision 2001-06-28: every month of 2000 revised up 1%
    rev_pub = dt.datetime(2001, 6, 28, 9, 15, tzinfo=NY)
    rev = [(p, v * 1.01) for p, v in zip(ms[:12], ip_first[:12], strict=True)]
    indpro = pl.concat([frame(ms, ip_first, pubs=fr_pubs),
                        frame([p for p, _ in rev], [v for _, v in rev], pubs=[rev_pub] * len(rev))])
    return {"M2SL": m2, "INDPRO": indpro, "INDPRO_FR": frame(ms, ip_first, pubs=fr_pubs)}


def test_r02_first_release_ip_within_its_vintage():
    f = _r02_frames()
    # before the revision: M2 yoy 10%, IP yoy 2% -> L2 = 8 > 3.5 for two months -> positive
    o = step1.r02_m2_minus_ip(ctx(dt.date(2001, 6, 26), f))
    assert o.ok and o.values["sign"] == 1 and o.values["period"] == "2001-05-31"
    assert o.values["level"] == pytest.approx(8.0, abs=1e-9)
    # after the revision: July first released in the revised vintage -> base month revised -> 1.02/1.01 - 1
    o = step1.r02_m2_minus_ip(ctx(dt.date(2001, 8, 31), f))
    assert o.values["period"] == "2001-07-31"
    assert o.values["level"] == pytest.approx(10.0 - (1.02 / 1.01 - 1) * 100, abs=1e-9)
    assert o.variant == "R-02" and o.values["base_effect_outlier"] is False


def test_r02_thresholds_and_confirmation():
    ms = months(dt.date(2000, 1, 31), 24)
    # M2 yoy 10% then 2% growth (L2 = 0 -> neutral band) in the last month only: state stays positive
    m2 = [100 * 1.10 ** (k / 12) for k in range(23)]
    m2.append(m2[11] * 1.04)  # month 24 vs month 12: 4% -> L2 = 2 (neutral band, 0 <= L2 <= 3.5)
    f = {"M2SL": frame(ms, m2, lag_days=25), "INDPRO": frame(ms, [100 * 1.02 ** (k / 12) for k in range(24)], lag_days=15),
         "INDPRO_FR": frame(ms, [100 * 1.02 ** (k / 12) for k in range(24)], lag_days=15)}
    o = step1.r02_m2_minus_ip(ctx(dt.date(2002, 2, 28), f))
    assert o.values["raw_sign"] == 0 and o.values["sign"] == 1
    assert o.values["level"] == pytest.approx(2.0, abs=1e-6)


def test_r02_unknown_when_m2_missing_or_unusable():
    f = _r02_frames()
    assert step1.r02_m2_minus_ip(ctx(dt.date(2001, 8, 31), {k: v for k, v in f.items() if k != "M2SL"})).status == "unknown"
    f["M2SL"] = f["M2SL"].with_columns(pl.lit(False).alias("usable"))
    o = step1.r02_m2_minus_ip(ctx(dt.date(2001, 8, 31), f))
    assert o.status == "unknown" and "unusable" in o.reason


def test_missing_parameter_is_unknown():
    o = step1.r02_m2_minus_ip(ctx(dt.date(2001, 8, 31), _r02_frames(), reg=registry.empty()))
    assert o.status == "unknown" and "liq.growth_window_m" in o.reason


# ------------------------------------------------------------------ R-03, R-04


WED = dt.date(2020, 1, 1)


def test_r03_net_liquidity_units_and_sign():
    n = 30
    f = {"WALCL": weekly(WED, [4_000_000 + 10_000 * k for k in range(n)]),
         "WTREGEN": weekly(WED, [400_000] * n),
         "RRPONTSYD": weekly(WED, [100.0] * n, lag_days=0)}            # $bn -> x1000
    asof = WED + dt.timedelta(weeks=n - 1, days=2)
    o = step1.r03_net_liquidity(ctx(asof, f))
    assert o.ok and o.values["sign"] == 1
    assert o.values["level"] == pytest.approx(130.0)                     # 13 weeks x $10bn
    assert o.values["net_liquidity"] == pytest.approx((4_000_000 + 10_000 * (n - 1) - 400_000 - 100_000) / 1000)


def test_r03_unknown_without_weekly_tga():
    f = {"WALCL": weekly(WED, [4e6] * 30)}
    assert step1.r03_net_liquidity(ctx(WED + dt.timedelta(weeks=29, days=2), f)).status == "unknown"


def test_r04_purchases_minus_issuance():
    n = 30
    f = {"TREAST": weekly(WED, [2_000_000 + 20_000 * k for k in range(n)]),
         "WSHOMCB": weekly(WED, [1_000_000] * n),
         "TFD_DEBT_HELD_PUBLIC": weekly(WED, [20_000_000 + 30_000 * k for k in range(n)], lag_days=1)}
    o = step1.r04_purchases_minus_issuance(ctx(WED + dt.timedelta(weeks=n - 1, days=2), f))
    assert o.ok and o.values["sign"] == -1
    assert o.values["fed_purchases"] == pytest.approx(260.0) and o.values["net_issuance"] == pytest.approx(390.0)
    assert o.values["level"] == pytest.approx(-130.0) and o.values["grid"] == "weekly"


def test_liquidity_family_era_variant_and_fallback():
    pos = step1.ok("R-02", "R-02", sign=1, level=5.0)
    neg = step1.ok("R-03", "R-03", sign=-1, level=-10.0, units="$bn")
    unk = step1.unknown("R-04", "x")
    c_a = ctx(dt.date(2010, 1, 4), {})
    c_b = ctx(dt.date(1995, 1, 4), {})
    assert step1.liquidity_family(c_a, pos, neg, unk, {}).variant == "R-03"
    assert step1.liquidity_family(c_b, pos, neg, unk, {}).variant == "R-02"
    fb = step1.liquidity_family(c_a, pos, neg, unk, {"R-03": 0.0})          # R-03 not held -> R-02 fallback
    assert fb.variant.startswith("R-02 (fallback") and fb.values["sign"] == 1
    both = step1.liquidity_family(c_a, pos, neg, step1.ok("R-04", sign=1, level=1.0), {})
    assert both.values["sign"] == 0 and both.variant == "R-03+R-04"        # conflicting era-A members -> neutral


# ------------------------------------------------------------------ R-14


def _r14_frames(holdings_step):
    n = 60
    start = dt.date(2019, 1, 2)
    days = 400
    tgt = [1.00 if i < 300 else 1.25 for i in range(days)]
    return {"DFEDTARU": daily(dt.date(2019, 1, 1), tgt),
            "TREAST": weekly(start, [2_000_000 + holdings_step * k for k in range(n)]),
            "WSHOMCB": weekly(start, [0.0] * n),
            "GDP": quarterly(dt.date(2018, 1, 1), [20_000.0] * 8)}


def _programme(rows):
    """FOMC_BS_STATE fixture: rows of (announced datetime ET, effective date, value)."""
    return frame([r[1] for r in rows], [r[2] for r in rows], pubs=[r[0] for r in rows])


def _at(y, m, d, h=14):
    return dt.datetime(y, m, d, h, 0, tzinfo=NY)


PROGRAMME_ROWS = [(_at(1914, 11, 16, 0), dt.date(1914, 11, 16), 0),
                  (_at(2019, 3, 20), dt.date(2019, 3, 20), -1),             # programme announced
                  (_at(2019, 9, 10), dt.date(2019, 10, 1), 0)]              # end announced in advance


def test_r14_programme_state_and_rate_sum():
    f = _r14_frames(0)
    f["FOMC_BS_STATE"] = _programme(PROGRAMME_ROWS)
    o = step1.r14_policy_direction(ctx(dt.date(2019, 6, 3), f))
    assert o.values["programme"] == "EXPAND" and o.values["holdings_sign"] == -1 and o.values["qe_active"] is True
    o = step1.r14_policy_direction(ctx(dt.date(2019, 9, 20), f))         # end announced, not yet effective
    assert o.values["programme"] == "EXPAND"
    o = step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f))          # hike within 6 m, programme over
    assert o.values["programme"] == "NONE" and o.values["qe_end_setback"] is True
    assert o.values["rate_sign"] == 1 and o.values["direction"] == "tightening"
    f["FOMC_BS_STATE"] = _programme(PROGRAMME_ROWS + [(_at(2019, 12, 11), dt.date(2019, 12, 11), 1)])
    o = step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f))
    assert o.values["programme"] == "RUNOFF" and o.values["direction"] == "tightening"


def test_r14_programme_point_in_time():
    f = _r14_frames(0)
    f["DFEDTARU"] = daily(dt.date(2018, 1, 1), [1.0] * 900)
    f["FOMC_BS_STATE"] = _programme(PROGRAMME_ROWS)
    snap_day = dt.date(2019, 3, 20)                                         # 16:00 close, release at 14:00
    assert step1.r14_policy_direction(ctx(snap_day, f)).values["programme"] == "EXPAND"
    early = dict(f)
    early["FOMC_BS_STATE"] = _programme([PROGRAMME_ROWS[0], (_at(2019, 3, 20, 17), dt.date(2019, 3, 20), -1)])
    o = step1.r14_policy_direction(ctx(snap_day, early))                    # released after the close
    assert o.values["programme"] == "NONE" and o.values["direction"] == "neutral"


def test_r14_rate_move_wins_over_programme():
    f = _r14_frames(0)
    f["DFEDTARU"] = daily(dt.date(2019, 1, 1), [2.0 if i < 300 else 1.75 for i in range(400)])   # cut
    f["FOMC_BS_STATE"] = _programme([PROGRAMME_ROWS[0], (_at(2019, 6, 1), dt.date(2019, 6, 1), 1)])  # runoff
    o = step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f))
    assert o.values["rate_sign"] == -1 and o.values["holdings_sign"] == 1 and o.values["direction"] == "easing"
    f["DFEDTARU"] = daily(dt.date(2019, 1, 1), [2.0] * 400)                                      # rate flat
    assert step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f)).values["direction"] == "tightening"


def test_r14_holdings_arithmetic_no_longer_sets_direction():
    f = _r14_frames(-10_000)                                                # holdings falling, no programme table
    o = step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f))
    assert o.values["holdings_sign"] is None and o.values["direction"] == "tightening"   # rate only
    assert o.values["qe_active"] is None                                    # no programme table: QE state unknown


def test_r14_rate_only_and_unknown():
    f = {"DFEDTARU": daily(dt.date(2019, 1, 1), [1.0 if i < 300 else 0.75 for i in range(400)])}
    o = step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f))
    assert o.values["direction"] == "easing" and o.values["holdings_sign"] is None
    assert step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), {})).status == "unknown"


# ------------------------------------------------------------------ R-06 .. R-10


def _infl_frames(cpi_yoy=0.04, ff=5.0, unrate=4.0, nrou=5.0, nrou_until=dt.date(2006, 12, 31)):
    ms = months(dt.date(2003, 1, 31), 42)
    q = quarterly(dt.date(2004, 1, 1), [nrou] * 12)
    q = q.filter(pl.col("period_end") <= nrou_until)
    return {"CPIAUCSL": frame(ms, [100 * (1 + cpi_yoy) ** (k / 12) for k in range(42)], lag_days=14),
            "UNRATE_FR": frame(ms, [unrate] * 42, lag_days=7),
            "NROU": q.with_columns(pl.lit(dt.datetime(2004, 1, 1, tzinfo=NY)).cast(pl.Datetime("us", "America/New_York"))
                                   .alias("published_at")),
            "FEDFUNDS": frame(ms, [ff] * 42, lag_days=2)}


def test_r06_taylor_gap_hand_computed():
    o = step1.r06_policy_error(ctx(dt.date(2006, 6, 30), _infl_frames()))
    # i* = 2 + 4 + 0.5 (4 - 2) + 1.0 (5 - 4) = 8; TG = 5 - 8 = -3 < -2 -> too loose (+1)
    assert o.ok and o.values["taylor_rate"] == pytest.approx(8.0, abs=1e-6)
    assert o.values["tg"] == pytest.approx(-3.0, abs=1e-6) and o.values["sign"] == 1
    assert o.values["nrou_period"] == "2006-06-30"                          # quarter containing the May UNRATE month


def test_r06_nrou_staleness_guard():
    f = _infl_frames(nrou_until=dt.date(2004, 3, 31))
    o = step1.r06_policy_error(ctx(dt.date(2006, 6, 30), f))
    assert o.status == "unknown" and "PIT guard" in o.reason


def test_r07_r08_r09_flags():
    c = ctx(dt.date(2006, 6, 30), _infl_frames(cpi_yoy=0.06, ff=5.0))
    assert step1.r08_ff_below_cpi(c).values["flag"] is True                # 6 > 5 and FF 5 < 6
    assert step1.r07_no_soft_landing(c, "tightening").values["flag"] is True
    assert step1.r07_no_soft_landing(c, "easing").values["flag"] is False
    assert step1.r07_no_soft_landing(c, None).status == "unknown"            # unknown direction, never a fail
    assert step1.r09_recession_prior(c, "tightening").values["flag"] is True
    c2 = ctx(dt.date(2006, 6, 30), _infl_frames(cpi_yoy=0.04))
    assert step1.r08_ff_below_cpi(c2).values["flag"] is False
    assert step1.r09_recession_prior(c2, "tightening").values["flag"] is False


def test_r10_three_rising_and_unknown():
    start = dt.date(2005, 1, 1)
    up = [1.0 + 0.01 * i for i in range(400)]
    f = {"DGS10": daily(start, up), "DCOILWTICO": daily(start, up), "USD_BROAD": daily(start, up)}
    asof = start + dt.timedelta(days=399)
    o = step1.r10_rates_oil_usd(ctx(asof, f))
    assert o.ok and o.values["flag"] is True
    f["USD_BROAD"] = daily(start, list(reversed(up)))
    assert step1.r10_rates_oil_usd(ctx(asof, f)).values["flag"] is False
    del f["USD_BROAD"]
    assert step1.r10_rates_oil_usd(ctx(asof, f)).status == "unknown"


# ------------------------------------------------------------------ R-11, R-12, R-56, R-58, R-63


def test_r11_composite_and_min_components():
    start = dt.date(2010, 1, 1)
    f = {"RITTER_UNPROF_IPO": annual(2000, [10 + k for k in range(10)]),
         "BAMLH0A0HYM2": daily(start, [8.0 - 0.01 * i for i in range(300)])}
    asof = start + dt.timedelta(days=299)
    o = step1.r11_fragility(ctx(asof, f))
    assert o.values["composite"] == pytest.approx(100.0) and o.values["level"] == "high" and o.values["components"] == 2
    o = step1.r11_fragility(ctx(asof, {"RITTER_UNPROF_IPO": f["RITTER_UNPROF_IPO"]}))
    assert o.status == "unknown"


def test_r12_regions_and_relative_impulse():
    start = dt.date(2014, 1, 1)
    f = {"CB_ASSETS_GDP_XM": quarterly(start, [20 + k for k in range(10)]),
         "ECB_DFR": daily(start, [0.0] * 900),
         "CB_ASSETS_GDP_US": quarterly(start, [25.0] * 10),
         "DFEDTARU": daily(start, [0.25 if i < 800 else 0.5 for i in range(900)])}
    out = step1.r12_cross_region(ctx(start + dt.timedelta(days=899), f))
    assert out["EA"].values["direction"] == "easing" and out["EA"].values["impulse"] == pytest.approx(2.0)
    assert out["US"].values["direction"] == "tightening"
    assert out["EA"].values["rel_us"] == pytest.approx(2.0)
    assert out["JP"].status == "unknown"


def test_r56_r58():
    start = dt.date(2015, 1, 1)
    f = {"DGS10": daily(start, [3.0] * 400), "GDP": quarterly(dt.date(2014, 1, 1), [100, 101, 102, 103, 105, 106])}
    o = step1.r56_ten_year_vs_ngdp(ctx(dt.date(2015, 6, 30), f))
    assert o.values["ngdp_yoy"] == pytest.approx(5.0) and o.values["state"] == "rich"
    nf = {"NFCI": weekly(dt.date(2015, 1, 7), [0.1 + 0.01 * k for k in range(30)])}
    assert step1.r58_fci(ctx(dt.date(2015, 8, 1), nf)).values["fci_state"] == "tight"
    nf = {"NFCI": weekly(dt.date(2015, 1, 7), [-0.1 - 0.01 * k for k in range(30)])}
    assert step1.r58_fci(ctx(dt.date(2015, 8, 1), nf)).values["fci_state"] == "loose"
    assert step1.r58_fci(ctx(dt.date(2015, 8, 1), {})).status == "unknown"


def test_r63_inactive_before_active_year_and_unknown_without_deficit():
    assert step1.r63_fiscal_supply(ctx(dt.date(2020, 6, 30), {}), step1.unknown("R-04", "")).status == "inactive"
    o = step1.r63_fiscal_supply(ctx(dt.date(2024, 6, 28), {}), step1.unknown("R-04", ""))
    assert o.status == "unknown" and "FYFSGDA188S" in o.reason


# ------------------------------------------------------------------ point in time


def test_rows_published_after_asof_are_invisible():
    f = _r14_frames(+10_000)
    late = frame([dt.date(2020, 2, 3)], [3.0], pubs=[dt.datetime(2020, 2, 5, 9, tzinfo=NY)])
    f2 = dict(f)
    f2["DFEDTARU"] = pl.concat([f["DFEDTARU"], late])
    a = step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f)).values
    b = step1.r14_policy_direction(ctx(dt.date(2020, 2, 4), f2)).values
    assert a == b


def test_ctx_era():
    assert ctx(dt.date(2001, 12, 31), {}).era == "B" and ctx(dt.date(2002, 1, 2), {}).era == "A"
    assert isinstance(FixtureSource({}).snapshot(et(dt.date(2001, 1, 2))), dict)
    assert REG["regime.prob_floor"].value == 0.01

def test_r14_cycle_state_holds_until_opposite_move():
    # last move a cut 2 years ago, no move since: still easing (decision R14-04)
    f = {"DFEDTARU": daily(dt.date(2017, 1, 1), [1.0 if i < 30 else 0.75 for i in range(1200)])}
    o = step1.r14_policy_direction(ctx(dt.date(2020, 3, 1), f))
    assert o.values["direction"] == "easing" and o.values["last_move"] == "2017-01-31"
    f["DFEDTARU"] = daily(dt.date(2017, 1, 1), [1.0 if i < 30 else 0.75 if i < 1000 else 1.0 for i in range(1200)])
    assert step1.r14_policy_direction(ctx(dt.date(2020, 3, 1), f)).values["direction"] == "tightening"


def test_r14_splices_discount_rate_before_target():
    disc = frame([dt.date(1979, 10, 8), dt.date(1980, 2, 15), dt.date(1980, 5, 30)], [12.0, 13.0, 12.0],
                 pubs=[dt.datetime(1979, 10, 8, 23, 59, tzinfo=NY), dt.datetime(1980, 2, 15, 23, 59, tzinfo=NY),
                       dt.datetime(1980, 5, 30, 23, 59, tzinfo=NY)])
    f = {"FED_DISCOUNT_RATE": disc}
    o = step1.r14_policy_direction(ctx(dt.date(1980, 4, 30), f))
    assert o.values["direction"] == "tightening" and o.variant == "FED_DISCOUNT_RATE"
    assert step1.r14_policy_direction(ctx(dt.date(1980, 5, 29), f)).values["direction"] == "tightening"  # not yet
    f["DFEDTAR"] = daily(dt.date(1982, 9, 27), [10.25] * 30 + [9.5] * 30)
    o = step1.r14_policy_direction(ctx(dt.date(1982, 10, 10), f))       # 12.0 -> 10.25 at the join: not a move
    assert o.variant == "DFEDTAR" and o.values["direction"] == "easing" and o.values["last_move"] == "1980-05-30"
    o = step1.r14_policy_direction(ctx(dt.date(1982, 11, 20), f))
    assert o.values["direction"] == "easing" and o.values["last_move"] == "1982-10-27"
    f["DFEDTAR"] = daily(dt.date(1982, 9, 27), [13.0] * 30)                    # join up, no move inside: still easing
    assert step1.r14_policy_direction(ctx(dt.date(1982, 10, 20), f)).values["direction"] == "easing"
