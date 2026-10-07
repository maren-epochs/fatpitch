"""Step 1b rules (spec\\process.md section 2): market internals, pure functions of one snapshot.

Inputs that process.md names but the lake does not carry (French-49 industries; French-12 is served as an
unusable D-graded substitute) make the dependent outputs unknown: R-59 industry narrowing always, R-15/R-16
before sector-ETF history allows the look-back (ETF data from 2021-09-22), and the R-60 industry fallback for
the 2020-02-11..2021-09-21 breadth gap.
"""

from __future__ import annotations

import datetime as _dt
import re

import numpy as np

from fatpitch.rules.outputs import RuleOutput, ok, unknown
from fatpitch.rules.series import Series, confirmed_state, date_of, day, months_back, months_back_arr, sign
from fatpitch.rules.step1 import Ctx, _guard

# process.md R-16: leading set -> sector ETFs (French-49 mapping not available in the lake)
LEADING_ETF = {
    "homebuilding": ("ETF_XHB",),
    "trucking_transport": ("ETF_IYT", "ETF_XTN"),
    "retail": ("ETF_XRT",),
    "banks": ("ETF_KBE",),
    "small_caps": ("ETF_IWM",),
    "metals": ("ETF_XME",),
    "semis": ("ETF_SMH",),
}
MARKET_ETF = "ETF_SPY"
# process.md R-60 source segments (data boundaries, not parameters)
NYSE_SEGMENT_END = _dt.date(2020, 2, 10)
SPX_SEGMENT_START = _dt.date(2021, 9, 22)
TURN_LOOKBACK_POINTS = 36

TREND_ASSETS = {  # R-19 vector: (series candidates, is_price)
    "us_equity": (("ETF_SPY", "US_EQ_FUT_PROXY"), True),
    "ust10y_yield": (("DGS10",), False),
    "usd": (("USD_BROAD",), True),
    "gold": (("GOLD_LBMA",), True),
    "wti": (("DCOILWTICO",), True),
    "copper": (("PCOPPUSDM",), True),
}
MOMENTUM_ASSETS = {"us_equity": ("SHILLER_SP",), "usd": ("USD_BROAD",), "gold": ("GOLD_LBMA",),
                   "wti": ("DCOILWTICO",), "copper": ("PCOPPUSDM",)}


def _dir(x: float | None) -> str | None:
    s = sign(x)
    return None if s is None else {1: "up", -1: "down", 0: "flat"}[s]


def _month_points(s: Series, n: int) -> np.ndarray:
    """Latest observation plus the last observation of each earlier month (oldest first)."""
    m = s.days.astype("datetime64[D]").astype("datetime64[M]").astype(np.int64)
    last_of_month = np.flatnonzero(np.r_[m[1:] != m[:-1], True])
    return s.days[last_of_month[-n:]]


# ------------------------------------------------------------------ R-15 / R-16


@_guard
def r15_leading_industries(ctx: Ctx) -> RuleOutput:
    """R-15/R-16: RS_i = industry return - market return over internals.rs_lookback_m months for the leading
    set; aggregate = median; direction = sign; a turn is a sign change confirmed for internals.turn_confirm_m
    months; turn age in days since the confirming run began. US only (R-15 conflicts line)."""
    lb, k = ctx.p.int("internals.rs_lookback_m"), ctx.p.int("internals.turn_confirm_m")
    names = list(ctx.p("internals.leading_set"))
    mkt = ctx.snap.get(MARKET_ETF)
    if mkt is None:
        return unknown("R-15", ctx.snap.reason(MARKET_ETF) + "; French-49 not in the lake")
    members = {}
    for nm in names:
        s = ctx.snap.first(*LEADING_ETF.get(nm, ()))
        if s is not None:
            members[nm] = s
    if not members:
        return unknown("R-15", "no leading-set series available")
    pts = _month_points(mkt, TURN_LOOKBACK_POINTS)
    base_pts = months_back_arr(pts, lb)
    mret = mkt.nearest_array(pts, tol=3) / mkt.nearest_array(base_pts, tol=3) - 1.0
    rs = []
    for s in members.values():
        r = s.nearest_array(pts, tol=3) / s.nearest_array(base_pts, tol=3) - 1.0
        rs.append(r - mret)
    rs = np.vstack(rs)
    with np.errstate(all="ignore"):
        med = np.array([np.nanmedian(c) if np.any(np.isfinite(c)) else np.nan for c in rs.T])
    raws = [sign(float(v)) if np.isfinite(v) else None for v in med]
    if raws[-1] is None:
        return unknown("R-15", f"leading-set RS not computable ({lb}-month look-back exceeds ETF history)")
    state, start = confirmed_state(raws, k)
    direction = None if state is None else {1: "up", -1: "down", 0: "flat"}[state]
    age = None if start is None else ctx.asof_day - int(pts[start])
    return ok("R-15", variant="sector ETFs", direction=direction, raw_direction=_dir(float(med[-1])),
              median_rs=float(med[-1]), turn_age_days=age, members=len(members))


# ------------------------------------------------------------------ R-17


@_guard
def r17_curve_credit(ctx: Ctx, qe_active: bool | None) -> RuleOutput:
    """R-17: curve = DGS10 - DGS2 (era B: GS10 - TB3MS) change over internals.curve_credit_trend_m months;
    credit = BAA - GS10 (GS10 = monthly average of DGS10, matching the monthly BAA average) and HY OAS
    changes over the same window; weight internals.qe_signal_weight while QE is active (R-14 QE test)."""
    m, qw = ctx.p.int("internals.curve_credit_trend_m"), ctx.p.num("internals.qe_signal_weight")
    s = ctx.snap
    out = {}
    y10, y2 = s.get("DGS10"), s.get("DGS2")
    curve_var = None
    if y10 is not None and y2 is not None:
        days = y2.days[y2.days >= months_back(y2.last_day, m) - 10]
        spread = y10.nearest_array(days, tol=3) - y2.values[-len(days):]
        sp = Series("curve", days, spread, np.zeros(len(days), dtype=np.int64))
        out["curve"], curve_var = sp.change(months=m), "DGS10-DGS2"
    else:
        g10, tb = s.get("GS10"), s.get("TB3MS")
        if g10 is not None and tb is not None:
            spread = g10.values - tb.nearest_array(g10.days, tol=3)
            sp = Series("curve", g10.days, spread, np.zeros(len(spread), dtype=np.int64))
            out["curve"], curve_var = sp.change(months=m), "GS10-TB3MS"
    baa, g10 = s.get("BAA"), s.get("GS10")
    if baa is not None and g10 is not None:
        cs = baa.values - g10.nearest_array(baa.days, tol=3)
        sp = Series("baa", baa.days, cs, np.zeros(len(cs), dtype=np.int64))
        out["credit_baa"] = sp.change(months=m)
    oas = s.get("BAMLH0A0HYM2")
    if oas is not None:
        out["credit_hy"] = oas.change(months=m)
    out = {k: v for k, v in out.items() if v is not None and np.isfinite(v)}
    if not out:
        return unknown("R-17", s.reason("DGS10", "DGS2", "BAA", "GS10", "BAMLH0A0HYM2"))
    weight = None if qe_active is None else (qw if qe_active else 1.0)
    return ok("R-17", variant=curve_var, weight=weight, **{f"d_{k}": v for k, v in out.items()})


# ------------------------------------------------------------------ R-18


def _monthly_closes(s: Series) -> Series:
    if s.spacing() >= 20:
        return s
    pts = _month_points(s, 10**6)
    idx = np.searchsorted(s.days, pts)
    return Series(s.sid, pts, s.values[idx], s.pub_us[idx])


@_guard
def r18_momentum(ctx: Ctx) -> RuleOutput:
    """R-18: on monthly closes, ROC = chart.monthly_roc_m-month rate of change, dROC = its
    chart.monthly_roc_change_m-month change; momentum bottom = dROC > 0 while ROC < 0. Price indices only
    (the 10-year yield is not a price index and is left to R-19)."""
    rm, cm = ctx.p.int("chart.monthly_roc_m"), ctx.p.int("chart.monthly_roc_change_m")
    vals = {}
    for name, sids in MOMENTUM_ASSETS.items():
        s = ctx.snap.first(*sids)
        if s is None:
            continue
        mc = _monthly_closes(s)
        if len(mc) < rm + cm + 1:
            continue
        roc = mc.values / mc.nearest_array(months_back_arr(mc.days, rm), tol=16) - 1.0
        rs = Series("roc", mc.days, roc, mc.pub_us)
        droc = rs.change(months=cm)
        if droc is None or not np.isfinite(roc[-1]) or not np.isfinite(droc):
            continue
        vals[f"{name}_roc"] = float(roc[-1])
        vals[f"{name}_droc"] = float(droc)
        vals[f"{name}_bottom"] = bool(droc > 0 and roc[-1] < 0)
    if not vals:
        return unknown("R-18", "no monthly class index available")
    return ok("R-18", **vals)


# ------------------------------------------------------------------ R-19


RETURN_SERIES = {"US_EQ_FUT_PROXY"}  # daily excess returns (French Mkt-RF); compounded into an index here


def _as_index(s: Series) -> Series:
    if s.sid not in RETURN_SERIES:
        return s
    return Series(s.sid, s.days, np.cumprod(1.0 + s.values) * 100.0, s.pub_us)


@_guard
def r19_cross_asset_trend(ctx: Ctx) -> RuleOutput:
    """R-19: chart.monthly_roc_m-month trend sign and chart.trend_lookback_w-week trend sign (price vs its
    moving average, the R-29 weekly construction) for US equity, 10-year yield, USD, gold, WTI, copper. For
    each asset the first candidate series that supports the 12-month change is used (ETF_SPY history starts
    2021-09; the French-based futures proxy is compounded from daily excess returns)."""
    rm, tw = ctx.p.int("chart.monthly_roc_m"), ctx.p.int("chart.trend_lookback_w")
    vals = {}
    for name, (sids, is_price) in TREND_ASSETS.items():
        for sid in sids:
            s = ctx.snap.get(sid)
            if s is None:
                continue
            s = _as_index(s)
            ch = s.change(months=rm)
            if ch is None:
                continue
            base = s.last - ch
            vals[f"{name}_12m"] = (s.last / base - 1.0) if (is_price and base) else ch
            win = s.values[s.days > s.last_day - 7 * tw]
            if len(win) >= 2:
                vals[f"{name}_vs_ma"] = float(s.last - np.mean(win))
            vals[f"{name}_source"] = s.sid
            break
    if not any(k.endswith(("_12m", "_vs_ma")) for k in vals):
        return unknown("R-19", "no trend input available")
    return ok("R-19", **vals)


# ------------------------------------------------------------------ R-59


@_guard
def r59_narrowing(ctx: Ctx) -> RuleOutput:
    """R-59: share of French-49 industries above trend falling by internals.narrowing_drop_pts over
    internals.narrowing_window_m months while the index is above trend -> narrowing. French-49 is not in the
    lake -> unknown. RSP/SPY relative return over the window is reported as the era-A cross-check."""
    wm = ctx.p.int("internals.narrowing_window_m")
    rsp, spy = ctx.snap.get("ETF_RSP"), ctx.snap.get("ETF_SPY")
    cross = None
    if rsp is not None and spy is not None:
        a, b = rsp.change(months=wm), spy.change(months=wm)
        if a is not None and b is not None:
            cross = (rsp.last / (rsp.last - a)) - (spy.last / (spy.last - b))
    return unknown("R-59", "FRENCH49 not in the lake (industry share above trend cannot be formed)",
                   rsp_spy_rel=cross)


# ------------------------------------------------------------------ R-60


def zweig_thresholds(defn: str) -> tuple[float, float, int] | None:
    m = re.search(r"<\s*([0-9.]+).*?>\s*([0-9.]+).*?within\s+(\d+)\s+trading days", str(defn))
    return (float(m.group(1)), float(m.group(2)), int(m.group(3))) if m else None


@_guard
def r60_breadth_thrust(ctx: Ctx) -> RuleOutput:
    """R-60: Zweig breadth thrust (10-day EMA of advances/(advances+declines) rises from below the low to above
    the high threshold within the registry's number of trading days). NYSE thresholds from
    internals.breadth_thrust (to 2020-02-10); S&P 500 member thresholds internals.breadth_thrust_spx_low/high
    (from 2021-09-22); the gap uses the industry fallback, which needs French-49 (absent) -> unknown. Thrust
    active for internals.thrust_override_m months after it fires."""
    nyse = zweig_thresholds(ctx.p("internals.breadth_thrust"))
    if nyse is None:
        return unknown("R-60", "internals.breadth_thrust definition not parseable")
    lo_s, hi_s = ctx.p.num("internals.breadth_thrust_spx_low"), ctx.p.num("internals.breadth_thrust_spx_high")
    om = ctx.p.int("internals.thrust_override_m")
    z = ctx.snap.get("ZWEIG_EMA10")
    if z is None:
        return unknown("R-60", ctx.snap.reason("ZWEIG_EMA10") + "; industry fallback needs FRENCH49 (absent)")
    n = nyse[2]
    nyse_end, spx_start = day(NYSE_SEGMENT_END), day(SPX_SEGMENT_START)
    since = months_back(ctx.asof_day, om)
    start = max(int(np.searchsorted(z.days, since)) - n - 1, 0)
    d, v = z.days[start:], z.values[start:]
    last_thrust = None
    for i in range(n, len(d)):
        if d[i] < since:
            continue
        if d[i] <= nyse_end:
            lo, hi = nyse[0], nyse[1]
        elif d[i] >= spx_start:
            lo, hi = lo_s, hi_s
        else:
            continue
        if v[i] > hi and v[i - 1] <= hi and np.min(v[i - n:i]) < lo:
            last_thrust = int(d[i])
    source = "nyse" if z.last_day <= nyse_end else ("spx_members" if z.last_day >= spx_start else None)
    return ok("R-60", variant=source, thrust_active=last_thrust is not None, breadth_source=source,
              last_thrust=None if last_thrust is None else date_of(last_thrust).isoformat(), ema10=z.last)
