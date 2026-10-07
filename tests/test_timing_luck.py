"""fatpitch.stats.timing_luck (port of CBP tests/test_timing_luck.py on synthetic prices).

The CBP NAV test compared against ``signal_timing.nav_path`` (not ported); the reference here is an
independent loop written from the documented rule.
"""

import datetime as dt

import numpy as np

from fatpitch.dates import trading_days
from fatpitch.stats import timing_luck as tl


def _daily():
    days = [d for d in (dt.date(2020, 1, 1) + dt.timedelta(i) for i in range(182)) if d.weekday() < 5]
    rng = np.random.default_rng(0)
    px = 100 * np.cumprod(1 + rng.normal(0, 0.01, (len(days), 3)), axis=0)
    return days, px


def _book():
    dates = [dt.date(2020, 1, 31), dt.date(2020, 2, 29), dt.date(2020, 3, 31), dt.date(2020, 4, 30),
             dt.date(2020, 5, 31)]
    w = np.array([[0.6, 0.4, 0.0], [0.2, 0.5, 0.3], [0.0, 1.0, 0.0], [0.5, 0.0, 0.5], [0.3, 0.3, 0.4]])
    return dates, w


def _ref_nav(book_dates, w, days, px, f, tc=tl.TC):
    fills = {}
    for t, row in zip(book_dates, w, strict=True):
        T = max(i for i, d in enumerate(days) if d <= t)
        if 0 <= T + f < len(days):
            fills[T + f] = row
    start = min(fills)
    hold, nav, out = None, 1.0, []
    for i in range(start, len(days)):
        if hold is not None:
            r = px[i] / px[i - 1] - 1
            nav *= 1 + float(hold @ r)
            g = hold * (1 + r)
            hold = g / g.sum()
        if i in fills:
            prev = hold if hold is not None else np.zeros(3)
            nav *= 1 - tc * np.abs(fills[i] - prev).sum()
            hold = fills[i].copy()
        out.append(nav)
    return np.array(out)


def test_nav_matches_independent_reference():
    days, px = _daily()
    bd, w = _book()
    for f in (-2, -1, 0, 1):
        _, nav, _, _ = tl.nav_with_contrib(bd, w, days, px, f)
        assert np.allclose(nav, _ref_nav(bd, w, days, px, f))


def test_contributions_rebuild_nav():
    days, px = _daily()
    bd, w = _book()
    _, nav, con, cost = tl.nav_with_contrib(bd, w, days, px, -1)
    rebuilt = np.cumprod((1 + con.sum(axis=1)) * (1 - cost))
    assert np.allclose(rebuilt, nav)


def test_placebo_set_has_19_paths():
    assert sum(tl.placebo(k, j) for k in tl.ANCHORS for j in tl.LAGS) == 19
    assert not tl.placebo(3, 2) and not tl.placebo(0, 1)


def test_day_buckets():
    b = tl.day_bucket([d for d in (dt.date(2020, 1, 1) + dt.timedelta(i) for i in range(91)) if d.weekday() < 5])
    assert b[dt.date(2020, 1, 31)] == "T-1..T"
    assert b[dt.date(2020, 1, 30)] == "T-1..T"
    assert b[dt.date(2020, 1, 29)] == "T-4..T-2"
    assert b[dt.date(2020, 2, 3)] == "T+1..T+3"
    assert b[dt.date(2020, 2, 5)] == "T+1..T+3"
    assert b[dt.date(2020, 2, 6)] == "other"


def test_offset_day_and_monthly_returns():
    days = trading_days("2020-01-01", "2020-03-31")
    assert tl.offset_day(days, dt.date(2020, 2, 29), 0) == dt.date(2020, 2, 28)
    assert tl.offset_day(days, dt.date(2020, 2, 29), 1) == dt.date(2020, 3, 2)
    assert tl.offset_day(days, dt.date(2020, 3, 31), 5) is None
    nav = np.linspace(1, 1.1, len(days))
    ends, r = tl.monthly_returns(days, nav)
    assert ends == [dt.date(2020, 2, 28), dt.date(2020, 3, 31)] and len(r) == 2


def test_nw_t_and_stats():
    assert np.isnan(tl.nw_t(np.ones(5)))
    rng = np.random.default_rng(5)
    assert tl.nw_t(rng.normal(1.0, 0.1, 200)) > 50
    s = tl.stats(np.array([0.1, -0.2, 0.1] + [0.0] * 9))
    assert abs(s["max_dd"] + 0.2) < 1e-12


def test_luck_summary_rules():
    rng = np.random.default_rng(11)
    n = 120
    base = rng.normal(0.005, 0.02, n)
    paths = {(k, j): base + rng.normal(0, 0.001, n) for k in tl.ANCHORS for j in tl.LAGS}
    paths[(0, 1)] = base
    paths[(3, 2)] = base + 0.002 + rng.normal(0, 0.0005, n)       # clear edge for the candidate
    s = tl.luck_summary(paths, (0, 1), (3, 2))
    assert s["n_placebo"] == 19 and s["rule1"] and s["rule2"] and s["passes"] and s["cand_rank"] == 1
    paths[(3, 2)] = base
    assert not tl.luck_summary(paths, (0, 1), (3, 2))["passes"]
