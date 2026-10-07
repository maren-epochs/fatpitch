"""R-67 v2 anticipated policy turn and R-68 (process.md R-67, R-68; hybrid track) and the Fed anticipation test
(scoring.md 6e). Fake-lake fixtures only; no amber data, no network."""

from __future__ import annotations

import datetime as dt

import numpy as np
import polars as pl
import pytest
from regime_fixtures import REG, ctx, et, frame, months

from fatpitch import FixtureSource, evaluate
from fatpitch.cases import anticipation as A
from fatpitch.dates import NY
from fatpitch.rules import anticipation as R
from fatpitch.rules.anticipation import (
    ABSENT,
    anticipated_turn,
    r67_anticipated_turn,
    r68_inflation_vs_projection,
)

ASOF = dt.date(2021, 2, 3)          # 400 calendar days of daily data from 2020-01-01 end on 2021-02-03
N_DAYS = 400
START = dt.date(2020, 1, 1)


def daily(sid, values, n=N_DAYS, start=START):
    vals = values if isinstance(values, list) else [values] * n
    days = [start + dt.timedelta(days=i) for i in range(len(vals))]
    pubs = [dt.datetime.combine(d, dt.time(15, 0), tzinfo=NY) for d in days]
    return {sid: frame(days, vals, pubs=pubs)}


def bills(spread, level=3.0, n=N_DAYS):
    """DTB3 flat at ``level``; DTB6 = DTB3 + spread (a number or a per-day list)."""
    sp = spread if isinstance(spread, list) else [spread] * n
    return {**daily("DTB3", [level] * len(sp)), **daily("DTB6", [level + s for s in sp])}


def dff(level, n=N_DAYS):
    return daily("DFF", level, n)


def path(spread_pp, ff=3.0):
    """DGS2 = FF + spread (percentage points), DFF = FF."""
    return {**daily("DGS2", ff + spread_pp), **dff(ff)}


def index(growth, end=dt.date(2020, 12, 31), lag_days=15, noise=0.0, seed=0):
    """Monthly index from monthly growth rates (%), last period ``end``; published ``lag_days`` later."""
    rng = np.random.RandomState(seed)
    g = np.asarray(growth, dtype=float) + noise * rng.standard_normal(len(growth))
    n = len(g) + 1
    y, m = divmod(end.year * 12 + end.month - 1 - (n - 1), 12)
    periods = months(dt.date(y, m + 1, 1), n)
    lvl = 100.0 * np.cumprod(np.r_[1.0, 1.0 + g / 100.0])
    return frame(periods, lvl.tolist(), lag_days=lag_days)


FLAT = [0.17] * 72                   # about 2% a year, I = 0
ACCEL = [0.1] * 66 + [0.4] * 6       # pi6 ~ 4.9, pi12 ~ 3.0 -> tightening, held
ACCEL_ONE = [0.1] * 71 + [0.9]       # only the latest month accelerates
DECEL = [0.4] * 66 + [0.05] * 6      # easing


def four(growth, noise=0.01, **kw):
    """All four I4 measures from the same growth path (independent small noise)."""
    ids = ("CPIAUCSL", "CPILFESL", "PCEPI", "PCEPILFE")
    return {sid: index(growth, noise=noise, seed=i, **kw) for i, sid in enumerate(ids)}


def neutral_market(ff=3.0):
    return {**path(0.0, ff), **bills(0.0, level=ff)}


def run(frames, asof=ASOF):
    return r67_anticipated_turn(ctx(asof, frames))


# ----------------------------------------------------------------- C1 bill-price forward (decision R67-06)


@pytest.mark.parametrize("rate, want", [(2, 1.0), (4, 4.2), (6, 9.5), (8, 17.2), (10, 27.3), (15, 64.0)])
def test_bill_price_forward_vs_discount_basis(rate, want):
    # equal discount yields: the discount-basis formula 2 x (DTB6 - DTB3) gives 0; the price-correct forward
    # exceeds spot by the research file D-6 amounts (1.0 / 4.2 / 9.5 / 17.2 / 27.3 / 64.0 bp)
    assert float(R.bill_forward_bp(rate, rate)) == pytest.approx(want, abs=0.06)


def test_bill_price_forward_numeric_at_ten_percent():
    p3, p6 = 1 - 0.10 * 91 / 360, 1 - 0.10 * 182 / 360
    f, r3 = (p3 / p6 - 1) * 360 / 91, (1 / p3 - 1) * 360 / 91
    assert float(R.bill_forward_bp(10.0, 10.0)) == pytest.approx((f - r3) * 1e4)
    assert float(R.bill_forward_bp(10.0, 10.0)) > 25.0           # tightening reading at flat 10% bills


def test_mb_leg_band_and_twenty_day_mean():
    o = run({**path(0.0), **bills(0.15), **four(FLAT)})
    want = float(R.bill_forward_bp(3.0, 3.15))
    assert o.values["mb_bp"] == pytest.approx(want) and want > 25
    assert o.values["mb_class"] == "tightening" and o.values["direction"] == "tightening"
    assert o.values["component"] == "MB"
    sm = run({**path(0.0), **bills([0.15] * 395 + [0.0] * 5), **four(FLAT)})
    w = 15 / 20 * float(R.bill_forward_bp(3.0, 3.15)) + 5 / 20 * float(R.bill_forward_bp(3.0, 3.0))
    assert sm.values["mb_bp"] == pytest.approx(w)


# ----------------------------------------------------------------- M2 path leg


@pytest.mark.parametrize("spread, want", [(0.6, "tightening"), (0.4, "neutral"), (-0.6, "easing")])
def test_m2_band(spread, want):
    o = run({**path(spread), **bills(0.0), **four(FLAT)})
    assert o.values["m2_bp"] == pytest.approx(spread * 100) and o.values["m2_class"] == want
    assert o.values["m2_series"] == "DGS2"
    if want != "neutral":
        assert o.values["direction"] == want and o.values["component"] == "M2"


def test_m2_dgs1_before_dgs2_and_zlb():
    f = {**daily("DGS1", 3.7), **dff(3.0), **bills(0.0), **four(FLAT)}
    o = run(f)
    assert o.values["m2_series"] == "DGS1" and o.values["m2_class"] == "tightening"
    z = run({**path(-0.6, ff=0.1), **bills(0.0, level=0.1), **four(FLAT)})
    assert z.values["m2_class"] == "neutral"                    # easing at DFF < 0.25 -> neutral


def test_m2_absent_vs_unknown():
    absent = run({**dff(3.0), **bills(0.15), **four(FLAT)})
    assert absent.values["m2_class"] == ABSENT and absent.values["component"] == "MB"
    stale = {**daily("DGS2", 3.6, n=380), **dff(3.0), **bills(0.15), **four(FLAT)}   # DGS2 ends 2021-01-14
    o = run(stale)
    assert o.values["m2_class"] is None and o.values["component"] == "MB"   # D3: unknown market leg passes on


# ----------------------------------------------------------------- I4 inflation composite (INFL-04)


def test_nsa_seasonally_neutral_form():
    # a pure seasonal pattern (sums to zero over a year) on a 2% trend: the NSA form reads 0, pi6 - pi12 does not
    season = [0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4, 0.1, 0.1, 0.0]
    g = [0.165 + season[i % 12] for i in range(72)]
    f = index(g)
    days = f["period_end"].to_physical().to_numpy().astype(np.int64)
    vals = f["value"].to_numpy()
    _, _, i_nsa = R.momentum(days, vals, nsa=True)
    _, _, i_sa = R.momentum(days, vals, nsa=False)
    assert np.nanmax(np.abs(i_nsa[-24:])) < 0.01
    assert np.nanmax(np.abs(i_sa[-24:])) > 0.5
    o = run({**neutral_market(), "CPIAUCNS": f, "CPILFESL": index(FLAT, noise=0.01)})
    assert o.values["cpi_series"] == "CPIAUCNS" and abs(o.values["cpi_i"]) < 0.01


def test_precision_weights_steadier_measure_counts_more():
    f = {**neutral_market(), "CPIAUCSL": index(FLAT, noise=0.25, seed=1), "CPILFESL": index(ACCEL, noise=0.01)}
    o = run(f)
    v = o.values
    assert v["i4_known"] == 2 and v["core_cpi_w"] > v["cpi_w"] and v["core_cpi_w"] + v["cpi_w"] == pytest.approx(1)
    assert v["i4_i"] == pytest.approx(v["cpi_w"] * v["cpi_i"] + v["core_cpi_w"] * v["core_cpi_i"])
    assert v["i4_pi6"] == pytest.approx(v["cpi_w"] * v["cpi_pi6"] + v["core_cpi_w"] * v["core_cpi_pi6"])


def test_precision_weight_function():
    days = np.array([R.months_back(18_000, k) for k in range(60, -1, -1)], dtype=np.int64)
    rng = np.random.RandomState(3)
    steady, noisy = rng.standard_normal(61) * 0.05, rng.standard_normal(61) * 0.5
    ws, n = R.precision_weight(days, steady, 60, 120, 36)
    wn, _ = R.precision_weight(days, noisy, 60, 120, 36)
    assert n == 60 and ws > wn
    assert R.precision_weight(days, steady, 30, 120, 36) == (None, 30)        # fewer than 36 changes
    assert R.precision_weight(days, steady, 60, 20, 36)[0] is None             # window shorter than the minimum


def test_short_history_measure_excluded_and_two_known_required():
    short = index([0.17] * 40, noise=0.01)                    # 41 months: about 28 changes of I < 36
    o = run({**neutral_market(), "CPIAUCSL": index(FLAT, noise=0.01), "CPILFESL": short})
    assert o.values["core_cpi_status"] == "excluded" and o.values["core_cpi_w"] is None
    assert o.values["i4_known"] == 1 and o.values["i4_class"] == ABSENT          # one measure exists: absent


def test_i4_unknown_when_existing_measure_is_stale():
    stale = index(FLAT, end=dt.date(2019, 12, 31), noise=0.01)
    o = run({**neutral_market(), "CPIAUCSL": index(FLAT, noise=0.01), "PCEPI": stale})
    assert o.values["pce_status"] == "unknown" and o.values["i4_class"] is None
    assert o.status == "unknown"                              # fallback depends on I4 (market neutral)


def test_i4_tightening_held_fills():
    o = run({**neutral_market(), **four(ACCEL)})
    v = o.values
    assert v["i4_class"] == "tightening" and v["i4_prev_class"] == "tightening" and v["i4_known"] == 4
    assert v["direction"] == "tightening" and v["component"] == "I4"
    for m in ("cpi", "core_cpi", "pce", "core_pce"):
        assert v[f"{m}_i"] > 0.5 and v[f"{m}_pi6"] > 2.0 and v[f"{m}_w"] > 0
    one = run({**neutral_market(), **four(ACCEL_ONE)})
    assert one.values["i4_class"] == "tightening" and one.values["i4_prev_class"] == "neutral"
    assert one.values["direction"] == "neutral" and one.values["component"] == "fallback (neither)"


def test_i4_easing_never_fills():
    o = run({**neutral_market(), **four(DECEL)})
    assert o.values["i4_class"] == "easing" and o.values["direction"] == "neutral"


# ----------------------------------------------------------------- Gr growth/stress leg


def rising(sid, a, b, n=N_DAYS):
    return daily(sid, list(np.linspace(a, b, n)))


def r10_on():
    return {**rising("DGS10", 1.0, 2.0), **rising("DCOILWTICO", 40, 60), **rising("USD_BROAD", 100, 110)}


def test_gr_on_and_suppressed_by_r08():
    hot = {"CPIAUCSL": index([0.6] * 72)}                    # CPI yoy ~ 7.4 > 5
    on = R.growth_reading(ctx(ASOF, {**r10_on(), **hot, **dff(8.0)}))
    assert on["r10"] is True and on["r15_down"] == ABSENT and on["credit_wider"] == ABSENT
    assert on["r08"] is False and on["gr"] is True
    sup = R.growth_reading(ctx(ASOF, {**r10_on(), **hot, **dff(3.0)}))   # FF < CPI yoy: R-08 holds
    assert sup["raw"] is True and sup["r08"] is True and sup["gr"] is False
    unk = R.growth_reading(ctx(ASOF, {**r10_on(), **dff(8.0)}))           # R-08 not computable
    assert unk["raw"] is True and unk["gr"] is None


def test_gr_absent_unknown_and_zlb():
    mild = {"CPIAUCSL": index(FLAT)}
    no_oil = {k: v for k, v in r10_on().items() if k != "DCOILWTICO"}
    assert R.growth_reading(ctx(ASOF, {**no_oil, **mild, **dff(3.0)}))["gr"] == ABSENT
    stale_oil = {**r10_on(), **rising("DCOILWTICO", 40, 60, n=380)}
    assert R.growth_reading(ctx(ASOF, {**stale_oil, **mild, **dff(3.0)}))["gr"] is None
    assert R.growth_reading(ctx(ASOF, {**r10_on(), **mild, **dff(0.1)}))["gr"] is False   # ZLB


def test_credit_wider_every_known_spread():
    baa = {"BAA": index([0.3] * 30, lag_days=1), "GS10": index([0.0] * 30, lag_days=1)}
    assert R._credit_wider(ctx(ASOF, baa)) is True
    hy = {**baa, **rising("BAMLH0A0HYM2", 6.0, 4.0)}
    assert R._credit_wider(ctx(ASOF, hy)) is False
    assert R._credit_wider(ctx(ASOF, {})) == ABSENT
    assert R._and3(True, ABSENT) == ABSENT and R._or3(ABSENT, None) is None and R._or3(False, ABSENT) is False


def test_gr_held_fills_easing_through_previous_month_end():
    f = {**r10_on(), "CPIAUCSL": index(FLAT, noise=0.01), **path(0.0, ff=3.0), **bills(0.0)}
    o = run(f)
    v = o.values
    assert v["gr"] == "on" and v["gr_prev"] == "on" and v["i4_class"] == ABSENT
    assert v["direction"] == "easing" and v["component"] == "Gr"


# ----------------------------------------------------------------- V2-B steps and guards (stubbed legs)


def _stub(monkeypatch, m2, mb, i4, i4_prev, gr, gr_prev=None):
    def leg(c):
        return {"cls": c, "bp": None, "series": None, "days": np.array([0, 1, 2]), "hist": [c, c, c]}

    monkeypatch.setattr(R, "path_part", lambda ctx: leg(m2))
    monkeypatch.setattr(R, "bill_part", lambda ctx: leg(mb))
    hist = [] if i4 == ABSENT else [i4_prev, i4]
    monkeypatch.setattr(R, "inflation_part", lambda ctx: {"cls": i4, "hist": hist, "measures": [], "n_known": 0,
                                                         "i": None, "pi6": None, "weights": {}})
    main = object()
    monkeypatch.setattr(R, "prev_ctx", lambda ctx: main)
    monkeypatch.setattr(R, "growth_reading", lambda c: {"gr": gr_prev if c is main else gr, "raw": None,
                                                         "r10": None, "r15_down": None, "credit_wider": None,
                                                         "r08": None})
    o = R.r67_anticipated_turn(ctx(ASOF, dff(3.0)))
    return o.status, o.values.get("direction"), o.values.get("component")


@pytest.mark.parametrize("legs, want", [
    # step 1: M2 first; guard on M2 tightening = I4 easing
    ((1, 0, 0, 0, False), ("ok", "tightening", "M2")),
    ((1, 0, -1, -1, False), ("ok", "neutral", "M2 guard (I4 easing)")),
    ((1, 0, None, None, False), ("unknown", None, None)),               # guard depends on unknown I4
    ((1, 0, ABSENT, None, False), ("ok", "tightening", "M2")),          # C4: absent I4, no guard
    ((-1, 1, None, None, None), ("ok", "easing", "M2")),                # easing needs no guard
    ((1, 0, 0, 0, True), ("ok", "tightening", "M2")),                   # Gr does not guard M2
    # step 2: MB when M2 is neutral, unknown or absent; guard = I4 easing or Gr on
    ((0, 1, 0, 0, False), ("ok", "tightening", "MB")),
    ((0, 1, 0, 0, True), ("ok", "neutral", "MB guard (Gr on)")),
    ((0, 1, -1, -1, False), ("ok", "neutral", "MB guard (I4 easing)")),
    ((0, 1, 0, 0, None), ("unknown", None, None)),
    ((0, 1, -1, -1, None), ("ok", "neutral", "MB guard (I4 easing)")),  # guard fires regardless of Gr
    ((None, 1, ABSENT, None, ABSENT), ("ok", "tightening", "MB")),
    ((ABSENT, -1, 0, 0, False), ("ok", "easing", "MB")),
    # step 3: fallback
    ((0, 0, 1, 1, False), ("ok", "tightening", "I4")),
    ((0, 0, 1, 0, False), ("ok", "neutral", "fallback (neither)")),
    ((0, 0, 1, None, False), ("unknown", None, None)),                  # hold not computable
    ((0, 0, -1, -1, False), ("ok", "neutral", "fallback (neither)")),   # inflation never produces easing
    ((0, 0, 0, 0, None), ("unknown", None, None)),
    ((0, 0, ABSENT, None, ABSENT), ("ok", "neutral", "fallback (neither)")),
    ((None, ABSENT, ABSENT, None, ABSENT), ("unknown", None, None)),    # no leg known
])
def test_v2b_steps(monkeypatch, legs, want):
    assert _stub(monkeypatch, *legs) == want


@pytest.mark.parametrize("gr, gr_prev, i4, i4_prev, want", [
    (True, True, 0, 0, ("ok", "easing", "Gr")),
    (True, False, 0, 0, ("ok", "neutral", "fallback (neither)")),
    (True, None, 0, 0, ("unknown", None, None)),
    (True, True, 1, 1, ("ok", "neutral", "fallback (both)")),
    (False, None, 1, 1, ("ok", "tightening", "I4")),
])
def test_v2b_fallback_gr_hold(monkeypatch, gr, gr_prev, i4, i4_prev, want):
    assert _stub(monkeypatch, 0, 0, i4, i4_prev, gr, gr_prev) == want


def test_onset_and_lead_age_on_mb():
    sp = [0.0] * 300 + [0.15] * 100
    o = run({**path(0.0), **bills(sp), **four(FLAT)})
    assert o.values["direction"] == "tightening" and o.values["component"] == "MB"
    onset = dt.date.fromisoformat(o.values["onset_date"])
    assert dt.date(2020, 10, 27) <= onset <= dt.date(2020, 11, 20)
    assert o.values["lead_age_m"] in (2, 3)


def test_missing_registry_param_is_unknown():
    from fatpitch import registry
    o = r67_anticipated_turn(ctx(ASOF, {**path(0.6), **bills(0.0), **four(FLAT)}, reg=registry.empty()))
    assert o.status == "unknown" and "registry parameter" in o.reason


def test_anticipated_turn_flag():
    o = run({**path(0.6), **bills(0.0), **four(FLAT)})
    assert anticipated_turn(o, "easing") is True and anticipated_turn(o, "tightening") is False
    n = run({**neutral_market(), **four(FLAT)})
    assert anticipated_turn(n, "tightening") is False and anticipated_turn(o, None) is None


def test_pit_release_after_close_not_visible():
    g = [0.1] * 72 + [0.9]
    f = index(g, end=dt.date(2021, 1, 31))
    pubs = f["published_at"].to_list()
    pubs[-1] = dt.datetime(2021, 2, 3, 16, 30, tzinfo=NY)
    f = f.with_columns(pl.Series("published_at", pubs, dtype=pl.Datetime("us", "America/New_York")))
    frames = {**neutral_market(), "CPIAUCSL": f, "CPILFESL": index(FLAT, noise=0.01)}
    assert run(frames).values["cpi_pi6"] < 2.0
    assert run(frames, asof=dt.date(2021, 2, 4)).values["cpi_pi6"] > 2.5


# ----------------------------------------------------------------- R-68 (hybrid, report-only)

R68_ASOF = dt.date(2021, 6, 30)       # previous month end 2021-05-28


def sep(rows):
    """SEP fixture series: rows of (published datetime ET, horizon year, value) -> one frame."""
    return frame([dt.date(y, 12, 31) for _, y, _ in rows], [v for _, _, v in rows], pubs=[p for p, _, _ in rows])


def at(y, m, d, h=14):
    return dt.datetime(y, m, d, h, 0, tzinfo=NY)


def core_pce(monthly_pct, end=dt.date(2021, 5, 31), n=30):
    return {"PCEPILFE": index([monthly_pct] * n, end=end, lag_days=28)}


def r68(frames, asof=R68_ASOF):
    return r68_inflation_vs_projection(ctx(asof, frames))


def test_r68_gap_band_and_hold():
    pce = core_pce(0.33)                                       # pi6 ~ 4.0
    pi6 = ((1.0033 ** 6) ** 2 - 1) * 100
    med = {"SEP_CORE_PCE_MEDIAN": sep([(at(2021, 3, 17), 2021, 2.2), (at(2021, 6, 16), 2021, 3.0)])}
    o = r68({**pce, **med})
    assert o.ok and o.values["projection"] == 3.0 and o.values["projection_stat"] == "median"
    assert o.values["gap"] == pytest.approx(pi6 - 3.0) and o.values["state"] == "behind"
    assert o.values["prev_gap"] == pytest.approx(pi6 - 2.2)    # previous month end: the March SEP was in force
    inline = r68({**pce, "SEP_CORE_PCE_MEDIAN": sep([(at(2021, 3, 17), 2021, 2.2), (at(2021, 6, 16), 2021, 3.8)])})
    assert inline.values["raw_state"] == "in_line" and inline.values["state"] == "in_line"


def test_r68_hold_uses_sep_in_force_at_previous_month_end():
    pce = core_pce(0.33)
    o = r68({**pce, "SEP_CORE_PCE_MEDIAN": sep([(at(2021, 3, 17), 2021, 3.8), (at(2021, 6, 16), 2021, 2.2)])})
    assert o.values["raw_state"] == "behind" and o.values["state"] == "in_line"   # not held: March gap ~0.2
    ahead = r68({**core_pce(0.05), "SEP_CORE_PCE_MEDIAN": sep([(at(2021, 3, 17), 2021, 2.0),
                                                                 (at(2021, 6, 16), 2021, 2.0)])})
    assert ahead.values["state"] == "ahead"


def test_r68_central_tendency_before_medians_and_year_column():
    ct = {"SEP_CORE_PCE_CT_LOW": sep([(at(2012, 1, 25), 2012, 1.5), (at(2012, 1, 25), 2013, 1.4)]),
          "SEP_CORE_PCE_CT_HIGH": sep([(at(2012, 1, 25), 2012, 1.8), (at(2012, 1, 25), 2013, 1.9)])}
    pce = core_pce(0.15, end=dt.date(2012, 1, 31))
    o = r68({**pce, **ct}, asof=dt.date(2012, 2, 29))
    assert o.values["projection"] == pytest.approx(1.65) and o.values["projection_stat"] == "central_tendency"
    # January 2013, before the first SEP of 2013: the January 2012 release is older than 200 days -> unknown
    late = r68({**core_pce(0.15, end=dt.date(2012, 12, 31)), **ct}, asof=dt.date(2013, 1, 31))
    assert late.status == "unknown" and "older than" in late.reason
    # December SEP's next-year column is the current year in January
    dec = {"SEP_CORE_PCE_MEDIAN": sep([(at(2020, 12, 16), 2020, 1.4), (at(2020, 12, 16), 2021, 1.8)])}
    j = r68({**core_pce(0.15, end=dt.date(2020, 12, 31)), **dec}, asof=dt.date(2021, 1, 29))
    assert j.values["projection"] == 1.8


def test_r68_sep_publication_point_in_time():
    pce = core_pce(0.15, end=dt.date(2021, 5, 31))
    med = {"SEP_CORE_PCE_MEDIAN": sep([(at(2021, 3, 17), 2021, 2.2), (at(2021, 6, 16), 2021, 3.0)])}
    before = r68_inflation_vs_projection(ctx(dt.date(2021, 6, 15), {**pce, **med}))
    assert before.values["projection"] == 2.2
    c = ctx(dt.date(2021, 6, 16), {**pce, **med})              # 16:00 ET, release 14:00 ET the same day
    assert r68_inflation_vs_projection(c).values["projection"] == 3.0
    none = r68({**pce}, asof=dt.date(2007, 6, 29))
    assert none.status == "unknown" and "no SEP" in none.reason


def test_sep_lake_reader(tmp_path):
    from fatpitch.lake import AmberLakeSource, read_spec_events_sep

    y = tmp_path / "sep.yaml"
    y.write_text("""version: t
events:
- {meeting: '2015-06-17', published_at: '2015-06-17 14:15', horizon_year: 2015, variable: core_pce_inflation, statistic: central_tendency_low, value: 1.3}
- {meeting: '2015-09-17', published_at: '2015-09-17 14:00', horizon_year: 2015, variable: core_pce_inflation, statistic: median, value: 1.4}
- {meeting: '2015-09-17', published_at: '2015-09-17 14:00', horizon_year: 2016, variable: core_pce_inflation, statistic: median, value: 1.7}
- {meeting: '2015-12-16', published_at: '2015-12-16 14:00', horizon_year: 2016, variable: core_pce_inflation, statistic: median, value: 1.6}
- {meeting: '2015-12-16', published_at: '2015-12-16 14:00', horizon_year: LR, variable: pce_inflation, statistic: median, value: 2.0}
- {meeting: '2015-12-16', published_at: '2015-12-16 14:00', horizon_year: 2016, variable: pce_inflation, statistic: median, value: 1.6}
""", encoding="utf-8")
    df = read_spec_events_sep(y, {"variable": "core_pce_inflation", "statistic": "median"})
    assert df.height == 3 and df["period_end"].to_list()[0] == dt.date(2015, 12, 31)
    assert df["vintage_id"].to_list()[0] == "spec:t:2015-09-17"
    assert read_spec_events_sep(y, {}).height == 0
    assert read_spec_events_sep(y, {"variable": "pce_inflation", "statistic": "median"}).height == 1  # LR dropped
    cat = {"series": {"SEP_X": {"status": "available", "step": "1", "pit_method": "release_calendar",
                                "source": {"kind": "spec_events_sep", "path": str(y),
                                           "filter": {"variable": "core_pce_inflation", "statistic": "median"}}}}}
    src = AmberLakeSource(root=tmp_path, series=["SEP_X"], catalogue=cat)
    s = src.snapshot(et(dt.date(2015, 12, 15)))["SEP_X"]
    assert s.filter(pl.col("period_end") == dt.date(2016, 12, 31))["value"].to_list() == [1.7]
    s2 = src.snapshot(et(dt.date(2015, 12, 16)))["SEP_X"]
    assert s2.filter(pl.col("period_end") == dt.date(2016, 12, 31))["value"].to_list() == [1.6]
    assert src.snapshot(et(dt.date(2015, 9, 16)))["SEP_X"].height == 0


# ----------------------------------------------------------------- tracks and registry


def test_hybrid_track_wiring_leaves_faithful_output_unchanged():
    frames = {**path(0.6), **bills(0.0), **four(FLAT),
              "SEP_CORE_PCE_MEDIAN": sep([(at(2020, 12, 16), 2021, 1.8)])}
    src = FixtureSource(frames)
    f = evaluate(et(ASOF), src, registry=REG)
    h = evaluate(et(ASOF), src, registry=REG, track="hybrid")
    fu, hu = f.region("US"), h.region("US")
    assert not any(e.startswith(("R-67", "R-68")) for e in fu.evidence)
    assert any(e.startswith("R-67") for e in hu.evidence) and any(e.startswith("R-68") for e in hu.evidence)
    assert [e for e in hu.evidence if not e.startswith(("R-67", "R-68"))] == fu.evidence
    assert any(n.startswith("anticipated_turn=") for n in h.notes)
    assert [n for n in h.notes if not n.startswith("anticipated_turn=")] == f.notes
    for a, b in zip(f.regime, h.regime, strict=True):
        assert (a.region, a.policy_direction, a.p_easing, a.p_neutral, a.p_tightening, a.veto_flags) == \
            (b.region, b.policy_direction, b.p_easing, b.p_neutral, b.p_tightening, b.veto_flags)
    assert f.internals == h.internals
    with pytest.raises(ValueError):
        evaluate(et(ASOF), src, registry=REG, track="other")


def test_registry_constants_not_tunable():
    ids = ("antic.band_bp", "antic.horizon_m", "antic.smooth_d", "antic.zlb_ff_pct", "antic.infl_short_m",
           "antic.infl_long_m", "antic.infl_band_pp", "antic.path_band_bp", "antic.infl_weight_window_m",
           "antic.infl_weight_min_n", "antic.infl_min_known", "r68.short_m", "r68.band_pp", "r68.hold_month_ends",
           "r68.sep_max_age_d")
    for i in ids:
        assert i in REG and not REG[i].tunable and REG[i].tag == "interpreted"
    assert (REG["antic.path_band_bp"].value, REG["antic.infl_weight_window_m"].value,
            REG["antic.infl_weight_min_n"].value, REG["antic.infl_min_known"].value) == (50, 120, 36, 2)
    assert len(REG.tunable) == 8


# ----------------------------------------------------------------- scorer (synthetic answer key)


def _key():
    cycles = [
        {"direction": "easing", "start": "2000-01", "end": "2000-06", "source": "DFEDTAR",
         "changes": [{"date": "2000-01-15"}, {"date": "2000-03-15"}, {"date": "2000-06-15"}]},
        {"direction": "tightening", "start": "2001-06", "end": "2001-12", "source": "DFEDTAR",
         "changes": [{"date": "2001-06-15"}, {"date": "2001-09-15"}, {"date": "2001-12-15"}]},
        {"direction": "easing", "start": "2003-01", "end": "2003-02", "source": "DFEDTAR",
         "changes": [{"date": "2003-01-15"}, {"date": "2003-02-15"}]},
    ]
    return A.answer_key(cycles, (1999, 1), (2004, 12))


def _signal():
    from fatpitch.cases.fedcycles import month_range
    s = dict.fromkeys(month_range((1999, 1), (2004, 12)), "neutral")
    for m in month_range((1999, 10), (1999, 12)):
        s[m] = "easing"
    for m in month_range((2000, 5), (2001, 5)):
        s[m] = "tightening"
    s[(2002, 12)] = None
    s[(2003, 6)] = "tightening"
    return s


def test_window_and_turns():
    t = _key().turns
    assert [(x.w_start, x.w_end) for x in t] == [((1999, 1), (1999, 12)), ((2000, 7), (2001, 5)),
                                                 ((2002, 1), (2002, 12))]
    adj = A.turns_from_cycles([{"direction": "easing", "start": "1975-01", "end": "1975-06"},
                               {"direction": "tightening", "start": "1975-07", "end": "1976-01"}])
    assert adj[1].w_start == adj[1].w_end == (1975, 6)       # empty window -> [W_end, W_end]


def test_turn_hit_lead_miss_not_evaluable():
    k, s = _key(), _signal()
    r = [A.score_turn(t, s) for t in k.turns]
    assert (r[0].status, r[0].onset, r[0].lead_months) == ("hit", "1999-10", 3)
    assert (r[1].status, r[1].onset, r[1].lead_months) == ("hit", "2000-07", 11)   # truncated at W_start
    assert r[2].status == "not_evaluable"
    s2 = dict(s)
    s2[(2001, 5)] = "neutral"
    m = A.score_turn(k.turns[1], s2)
    assert (m.status, m.lead_months) == ("miss", 0)
    del s2[(1999, 12)]
    assert A.score_turn(k.turns[0], s2).status == "not_evaluable"


def test_false_alarms_and_episodes():
    k, s = _key(), _signal()
    fa = A.false_alarms(s, k, "tightening")
    assert fa["eval_months"] == 65 and fa["fa_months"] == 8
    assert fa["fa_per_year"] == pytest.approx(8 / (65 / 12))
    assert (fa["episodes"], fa["false_episodes"]) == (2, 1)
    assert A.false_alarms(s, k, "easing")["fa_months"] == 0


def test_change_months_turning_points():
    cm = A.change_months([{"direction": "tightening", "start": "1980-08", "end": "1980-10",
                           "source": "FEDFUNDS turning points", "changes": []}])
    assert cm["tightening"] == {(1980, 8), (1980, 9), (1980, 10)} and cm["easing"] == set()


def test_score_signal_and_pass_rule():
    k, s = _key(), _signal()
    res = A.score_signal(s, k)
    assert res["tightening"]["hit_rate"] == 1.0 and res["tightening"]["median_lead"] == 11.0
    assert res["easing"]["evaluable"] == 1 and res["easing"]["not_evaluable"] == 1
    assert res["tightening"]["eras"]["1994-2008"]["hits"] == 1
    naive = A.score_signal(dict.fromkeys(s, "neutral"), k)
    p = A.pass_rule(res, naive)
    assert p["easing"]["pass"] and p["easing"]["2"]
    assert p["tightening"]["3"] and not p["tightening"]["2"]       # 1.48 FA/yr: <= 3.0 but > naive 0 + 1.0
    assert p["pass"] is False


def test_pass_rule_criteria():
    def r(h, lead, fa, era_h=1.0):
        d = {"hit_rate": h, "median_lead": lead, "fa_per_year": fa,
             "eras": {"1994-2008": {"evaluable": 2, "hit_rate": era_h}, "2009-": {"evaluable": 0, "hit_rate": None}}}
        return {"tightening": d, "easing": d}
    naive = r(0.5, 2.0, 0.5)
    assert A.pass_rule(r(0.7, 3.0, 1.4), naive)["pass"]
    assert not A.pass_rule(r(0.5, 3.0, 1.0), naive)["tightening"]["1"]        # hit rate < 0.6
    assert not A.pass_rule(r(0.7, 1.0, 1.0), naive)["tightening"]["2"]        # lead below naive
    assert not A.pass_rule(r(0.7, 3.0, 1.6), naive)["tightening"]["2"]        # FA > naive + 1.0
    assert not A.pass_rule(r(0.7, 3.0, 3.2), r(0.5, 2.0, 3.0))["tightening"]["3"]
    assert not A.pass_rule(r(0.7, 3.0, 1.0, era_h=0.0), naive)["tightening"]["4"]
    assert A.pass_rule(r(0.7, 3.0, 1.0), r(0.0, None, 0.5))["tightening"]["2"]   # naive without hits


def test_month_end_signals_on_fixture():
    frames = {**path(0.6, ff=2.9), **bills(0.2, level=3.0), **four(FLAT)}
    src = FixtureSource(frames)
    row = A.month_end_signals(et(ASOF), src.snapshot(et(ASOF)), REG, src)
    assert row["R-67"] == "tightening" and row["component"] == "M2" and row["null_always_risk_on"] == "easing"
    assert row["naive_2y_ff"] == "tightening" and row["naive_2y_bp"] == pytest.approx(60.0)
    assert row["naive_bill_ff"] == "tightening" and row["naive_bill_bp"] == pytest.approx(30.0)
    assert row["m2_bp"] == pytest.approx(60.0) and row["i4_known"] == 4 and row["core_pce_w"] > 0
    assert row["r68_state"] is None and "no SEP" in row["r68_reason"]
    assert set(A.R67_FIELDS) <= set(row) and set(A.R68_FIELDS) <= set(row)


def test_supplementary_report_blocks():
    k, s = _key(), _signal()
    scored = A.score_all({"R-67": s, A.NAIVE: s}, k)
    rows = {A.mstr(m): {"component": "M2" if v == "tightening" else "fallback (neither)", "i4_known": 2,
                        "i4_class": "neutral", "cpi_pi6": 3.0, "core_cpi_pi6": 2.5, "pce_pi6": 1.5,
                        "core_pce_pi6": 1.8, "cpi_pi12": 3.0, "pce_pi12": 2.5,
                        "r68_state": "behind" if m[0] == 2003 else None} for m, v in s.items()}
    md = A.supplementary_md(rows, scored, 2.0)
    assert "| tightening | M2 | 1 | 0 |" in md
    assert "mean wedge on pi6 1.50 pp, on pi12 0.50 pp" in md
    assert "both PCE measures do not: 72" in md
    assert "| behind | 2003-01 | 2003-12 |" in md
