"""Step 1b rules, R-66 probability mapping, process timeline, evaluate() wiring and the version driver source."""

import datetime as dt
import math

import polars as pl
import pytest
from regime_fixtures import REG, ctx, daily, et, frame, monthly, months, weekly

import fatpitch
from fatpitch import FixtureSource
from fatpitch.dates import NY
from fatpitch.decision import Decision, RegimeVector
from fatpitch.rules import step1b, timeline
from fatpitch.rules.probability import Family, liquidity_class, regime_probabilities

# ------------------------------------------------------------------ step 1b


def test_r15_leading_set_turns_down():
    start = dt.date(2022, 1, 3)
    n = 500
    f = {"ETF_SPY": daily(start, [100.0] * n)}
    for i, sid in enumerate(("ETF_XHB", "ETF_IYT", "ETF_XRT", "ETF_KBE", "ETF_IWM", "ETF_XME", "ETF_SMH")):
        vals = [100.0 * (1 + 0.0005 * k) if k < 300 else 100.0 * (1 + 0.0005 * 300) * (1 - 0.001 * (k - 300))
                for k in range(n)]
        f[sid] = daily(start, vals)
    asof = start + dt.timedelta(days=n)
    o = step1b.r15_leading_industries(ctx(asof, f))
    assert o.ok and o.values["direction"] == "down" and o.values["members"] == 7
    assert o.values["turn_age_days"] is not None and 0 < o.values["turn_age_days"] < 200


def test_r15_unknown_without_history():
    assert step1b.r15_leading_industries(ctx(dt.date(2022, 1, 3), {})).status == "unknown"


def test_r60_zweig_thrust_segments():
    # S&P member segment (thresholds 0.40 / 0.646)
    start = dt.date(2022, 1, 1)
    ema = [0.5] * 100 + [0.38, 0.42, 0.48, 0.55, 0.60, 0.65, 0.66] + [0.6] * 20
    f = {"ZWEIG_EMA10": daily(start, ema)}
    o = step1b.r60_breadth_thrust(ctx(start + dt.timedelta(days=len(ema) - 1), f))
    assert o.values["thrust_active"] is True and o.values["breadth_source"] == "spx_members"
    assert o.values["last_thrust"] == (start + dt.timedelta(days=105)).isoformat()
    # NYSE segment (0.40 / 0.615): 0.62 crosses NYSE high
    start = dt.date(1990, 1, 1)
    ema = [0.5] * 100 + [0.38, 0.45, 0.55, 0.62] + [0.55] * 20
    o = step1b.r60_breadth_thrust(ctx(start + dt.timedelta(days=len(ema) - 1), {"ZWEIG_EMA10": daily(start, ema)}))
    assert o.values["thrust_active"] is True and o.values["breadth_source"] == "nyse"
    # slow rise (more than 10 rows from <0.40 to >0.615): no thrust
    ema = [0.5] * 100 + [0.38] + [0.39 + 0.02 * k for k in range(12)] + [0.55] * 10
    o = step1b.r60_breadth_thrust(ctx(start + dt.timedelta(days=len(ema) - 1), {"ZWEIG_EMA10": daily(start, ema)}))
    assert o.values["thrust_active"] is False


def test_r60_gap_rows_unusable_is_unknown():
    start = dt.date(2019, 6, 1)
    f = {"ZWEIG_EMA10": daily(start, [0.5] * 400).with_columns(
        pl.Series("usable", [d <= dt.date(2020, 2, 10) for d in [start + dt.timedelta(days=i) for i in range(400)]]))}
    o = step1b.r60_breadth_thrust(ctx(dt.date(2020, 6, 30), f))
    assert o.status == "unknown"


def test_r17_curve_and_credit():
    start = dt.date(2010, 1, 1)
    f = {"DGS10": daily(start, [3.0 + 0.002 * i for i in range(200)]), "DGS2": daily(start, [1.0] * 200),
         "BAMLH0A0HYM2": daily(start, [5.0 - 0.001 * i for i in range(200)])}
    o = step1b.r17_curve_credit(ctx(start + dt.timedelta(days=199), f), True)
    assert o.values["d_curve"] > 0 and o.values["d_credit_hy"] < 0 and o.values["weight"] == 0.5
    assert o.variant == "DGS10-DGS2"


def test_r18_momentum_bottom():
    vals = [100 * (1 - 0.02 * k) for k in range(18)] + [100 * (1 - 0.02 * 17) * (1 + 0.03 * k) for k in range(1, 7)]
    f = {"SHILLER_SP": monthly(dt.date(2008, 1, 31), vals, lag_days=5)}
    o = step1b.r18_momentum(ctx(dt.date(2010, 1, 15), f))
    assert o.values["us_equity_roc"] < 0 and o.values["us_equity_droc"] > 0 and o.values["us_equity_bottom"] is True


def test_r19_compounds_return_proxy():
    start = dt.date(2010, 1, 1)
    f = {"US_EQ_FUT_PROXY": daily(start, [0.001] * 500, lag_days=30)}
    o = step1b.r19_cross_asset_trend(ctx(start + dt.timedelta(days=520), f))
    assert o.values["us_equity_source"] == "US_EQ_FUT_PROXY"
    assert o.values["us_equity_12m"] == pytest.approx(1.001 ** 365 - 1, rel=0.02)


def test_r59_unknown_without_french49():
    assert step1b.r59_narrowing(ctx(dt.date(2023, 1, 3), {})).status == "unknown"


# ------------------------------------------------------------------ R-66


def test_r66_counts_and_ties():
    agree = regime_probabilities([Family("R-14", "tightening"), Family("LIQ", "tightening")], "tightening", 1, 1, 0.01)
    assert agree.as_tuple() == pytest.approx((0.2, 0.2, 0.6)) and agree.direction == "tightening"
    split = regime_probabilities([Family("R-14", "tightening"), Family("LIQ", "easing")], "tightening", 1, 1, 0.01)
    assert split.as_tuple() == pytest.approx((0.4, 0.2, 0.4)) and split.direction == "tightening"
    neutral_tie = regime_probabilities([Family("R-14", "neutral"), Family("LIQ", "easing")], "neutral", 1, 1, 0.01)
    assert neutral_tie.direction == "neutral"
    one = regime_probabilities([Family("R-14", None), Family("LIQ", "easing")], None, 1, 1, 0.01)
    assert one.as_tuple() == pytest.approx((0.5, 0.25, 0.25)) and one.direction == "easing"
    assert regime_probabilities([Family("R-14", None), Family("LIQ", None)], None, 1, 1, 0.01) is None
    inactive = regime_probabilities([Family("R-14", "easing", 0.0), Family("LIQ", "neutral")], "easing", 1, 1, 0.01)
    assert inactive.direction == "neutral"                                   # weight 0 = not held -> no evidence
    floored = regime_probabilities([Family("a", "easing")], None, 0.0, 1.0, 0.01)
    assert floored.as_tuple() == pytest.approx((0.98, 0.01, 0.01))
    RegimeVector("US", p_easing=floored.p_easing, p_neutral=floored.p_neutral, p_tightening=floored.p_tightening)
    assert math.isclose(sum(floored.as_tuple()), 1.0)
    assert liquidity_class(1) == "easing" and liquidity_class(-1) == "tightening" and liquidity_class(None) is None


def test_r66_registry_mapping_can_beat_always_easing():
    """Structural check (no case data): with the registry constants, a correct call by both families must score
    a lower RPS than the always-easing reference does when the target is tightening, and stay close to it when
    the target is easing (spec/process.md R-66 revision 2026-10-07)."""
    from fatpitch.cases.regime import score_rps
    base, inc, floor = (REG[k].effective for k in
                        ("regime.prob_base_mass", "regime.prob_family_increment", "regime.prob_floor"))
    ease = regime_probabilities([Family("R-14", "easing"), Family("LIQ", "easing")], "easing", base, inc, floor)
    tight = regime_probabilities([Family("R-14", "tightening"), Family("LIQ", "tightening")], "tightening",
                                 base, inc, floor)
    always = (1.0, 0.0, 0.0)
    assert score_rps(ease.as_tuple(), "easing") < 0.01
    assert score_rps(tight.as_tuple(), "tightening") < score_rps(always, "tightening")
    assert max(ease.as_tuple()) > 0.9


def test_regime_vector_accepts_tied_argmax():
    RegimeVector("US", "tightening", p_easing=0.4, p_neutral=0.2, p_tightening=0.4)
    with pytest.raises(ValueError):
        RegimeVector("US", "neutral", p_easing=0.4, p_neutral=0.2, p_tightening=0.4)


# ------------------------------------------------------------------ timeline


def test_timeline_era_codes(tmp_path):
    p = tmp_path / "tl.yaml"
    p.write_text(
        "eras: {E1: '1977-1987 a', E2: '1988-2000 b', E3: '2001-2010 c'}\n"
        "rules:\n"
        "  - id: R-03\n    weight: {E1: absent, E2: absent, E3: active}\n"
        "  - id: R-02\n    weight: {E1: unknown, E2: 'core (x)', E3: reduced}\n"
        "  - id: R-08\n    held_until: 2005-06-10 (as a forecast rule)\n    weight: {E1: core, E2: core, E3: core}\n"
        "  - id: R-09\n    held_until: 2005-06-10\n    weight: {E1: n/a, E2: core, E3: core}\n", encoding="utf-8")
    tl = timeline.load(p)
    assert tl.weight("R-03", dt.date(1995, 1, 1)) == 0.0 and tl.weight("R-03", dt.date(2005, 1, 1)) == 1.0
    assert tl.weight("R-03", dt.date(2030, 1, 1)) == 1.0                       # after the last era: last code
    assert tl.weight("R-02", dt.date(1965, 1, 1)) == 1.0                       # before E1: E1 code (unknown = held)
    assert tl.weight("R-08", dt.date(2008, 1, 1)) == 1.0                       # qualified held_until does not gate
    assert tl.weight("R-09", dt.date(2008, 1, 1)) == 0.0 and tl.weight("R-09", dt.date(1980, 1, 1)) == 0.0
    assert tl.weight("R-99", dt.date(1980, 1, 1)) == 1.0                       # not named: held


def test_timeline_generic_and_missing(tmp_path):
    p = tmp_path / "tl.yaml"
    p.write_text("rules:\n  - {id: R-10, active_from: 2000-09-01, weight: 0.5}\n", encoding="utf-8")
    tl = timeline.load(p)
    assert tl.weight("R-10", dt.date(1999, 1, 1)) == 0.0 and tl.weight("R-10", dt.date(2001, 1, 1)) == 0.5
    assert timeline.load(tmp_path / "absent.yaml").weight("R-03", dt.date(1990, 1, 1)) == 1.0


# ------------------------------------------------------------------ evaluate()


def _engine_frames():
    ms = months(dt.date(2000, 1, 31), 24)
    ip = [100 * 1.02 ** (k / 12) for k in range(24)]
    return {"M2SL": frame(ms, [100 * 1.10 ** (k / 12) for k in range(24)], lag_days=25),
            "INDPRO": frame(ms, ip, lag_days=15), "INDPRO_FR": frame(ms, ip, lag_days=15),
            "DFEDTARU": daily(dt.date(2000, 6, 1), [5.0 if i < 400 else 5.5 for i in range(456)]),
            "WALCL": weekly(dt.date(2001, 1, 3), [1.0] * 30)}


def test_evaluate_fills_us_regime_vector():
    src = FixtureSource(_engine_frames())
    asof = et(dt.date(2001, 8, 31))
    d = fatpitch.evaluate(asof, src, registry=REG, timeline=timeline.Timeline.all_active())
    us = d.region("US")
    # R-14 tightening (hike within 6 months, holdings unknown); LIQ = R-02 positive (era B) -> disagree
    assert us.probabilities == pytest.approx((1.1 / 2.3, 0.1 / 2.3, 1.1 / 2.3)) and us.policy_direction == "tightening"
    assert us.liquidity_variant == "R-02" and us.liquidity_sign == 1
    assert any(e.startswith("R-66") for e in us.evidence)
    assert {r.region for r in d.regime} == {"US", "EA", "JP", "UK"}
    assert d.region("EA").probabilities is None                               # no R-12 input: unknown, not uniform
    assert Decision.from_json(d.to_json()) == d
    assert d.no_pitch and d.schema_version == "2"


def test_evaluate_timeline_gates_rules(tmp_path):
    p = tmp_path / "tl.yaml"
    p.write_text("eras: {E1: '1977-2026 all'}\nrules:\n  - id: R-14\n    weight: {E1: absent}\n", encoding="utf-8")
    d = fatpitch.evaluate(et(dt.date(2001, 8, 31)), FixtureSource(_engine_frames()), registry=REG, timeline=p)
    us = d.region("US")
    assert us.probabilities == pytest.approx((1.1 / 1.3, 0.1 / 1.3, 0.1 / 1.3)) and us.policy_direction == "easing"
    assert any(e.startswith("R-14=inactive") for e in us.evidence)


def test_evaluate_empty_registry_is_unknown_not_guess():
    d = fatpitch.evaluate(et(dt.date(2001, 8, 31)), FixtureSource(_engine_frames()),
                          timeline=timeline.Timeline.all_active())
    assert d.region("US").policy_direction is None and d.region("US").probabilities is None


def test_evaluate_ignores_future_publications():
    f = _engine_frames()
    asof = et(dt.date(2001, 8, 31))
    late = frame([dt.date(2001, 8, 30)], [9.0], pubs=[dt.datetime(2001, 9, 1, 9, tzinfo=NY)])
    f2 = dict(f, DFEDTARU=pl.concat([f["DFEDTARU"], late]))
    tl = timeline.Timeline.all_active()
    a = fatpitch.evaluate(asof, FixtureSource(f), registry=REG, timeline=tl)
    b = fatpitch.evaluate(asof, FixtureSource(f2), registry=REG, timeline=tl)
    assert a.regime == b.regime


def test_driver_engine_source_is_lake(tmp_path):
    from fatpitch.lake import AmberLakeSource
    from fatpitch.rules import ENGINE_SERIES
    from fatpitch.versions import driver

    src = driver._engine_source(str(tmp_path))
    assert isinstance(src, AmberLakeSource)
    assert set(src.series) <= set(ENGINE_SERIES) and "M2SL" in src.series
    snap = src.snapshot(et(dt.date(2005, 1, 3)))
    spec_ids = {"FOMC_BS_STATE", "FED_DISCOUNT_RATE"}                       # project event tables, not the lake
    assert all(f.is_empty() for k, f in snap.items() if k not in spec_ids)
    assert not snap["FOMC_BS_STATE"].is_empty()                       # project event table, not the lake
