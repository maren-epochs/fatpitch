"""Step 1 rules (spec\\process.md section 1): pure functions of one point-in-time snapshot.

Each function takes a ``Ctx`` and returns a ``RuleOutput``. Sign convention for policy classes: +1 =
tightening, -1 = easing, 0 = neutral. Liquidity impulse sign: +1 = positive (expansionary), -1 = negative.

Units (lake as stored): WALCL, WTREGEN, TREAST, WSHOMCB and debt held by the public in $ millions;
RRPONTSYD in $ billions (x1000 here). Reported liquidity levels are in $ billions (R-03, R-04) or
percentage points (R-02).
"""

from __future__ import annotations

import datetime as _dt
import weakref
from dataclasses import dataclass, field

import numpy as np

from fatpitch.rules.outputs import MissingParam, Params, RuleOutput, ok, unknown
from fatpitch.rules.series import (
    Series,
    Snap,
    date_of,
    day,
    months_back,
    months_back_arr,
    sign,
)

ERA_A_START = _dt.date(2002, 1, 1)  # process.md section 0: era A = 2002 onward, era B = pre-2002
# process.md R-02 PIT line: flag 2020-03..2021-12 as base-effect outliers (flag only; the rule still runs)
R02_OUTLIER = (_dt.date(2020, 3, 1), _dt.date(2021, 12, 31))
NROU_MAX_AGE_DAYS = 730  # mechanical PIT guard: an NROU value for a period > 2 years before asof is unknown
MAX_CONFIRM_LOOKBACK = 36  # observations searched backwards for a confirmed run (computational bound)

_FR_CACHE: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


@dataclass
class Ctx:
    asof: _dt.datetime
    snap: Snap
    p: Params
    source: object = None
    memo: dict = field(default_factory=dict)

    @property
    def asof_day(self) -> int:
        return self.snap.asof_day

    @property
    def era(self) -> str:
        return "A" if self.asof.date() >= ERA_A_START else "B"


def _guard(fn):
    """Missing registry parameter -> unknown (never a guess)."""
    rule = fn.__name__.split("_")[0].upper().replace("R", "R-", 1)

    def wrapper(ctx: Ctx, *args) -> RuleOutput:
        try:
            return fn(ctx, *args)
        except MissingParam as e:
            return unknown(rule, f"registry parameter {e.args[0]} missing")

    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    wrapper.rule = rule
    return wrapper


def snapshot_one(source, when: _dt.datetime, sid: str):
    try:
        snap = source.snapshot(when, series=[sid])
    except TypeError:
        snap = source.snapshot(when)
    return snap.get(sid)


def _run_state(raws, k: int):
    """Newest-first raw states -> (confirmed state of the most recent run of >= k equal known states, its
    length so far). None when no such run within the list."""
    run_v, run_n = None, 0
    for v in raws:
        if v is None:
            run_v, run_n = None, 0
            continue
        if v == run_v:
            run_n += 1
        else:
            run_v, run_n = v, 1
        if run_n >= k:
            return run_v
    return None


# ------------------------------------------------------------------ R-02


def ip_first_release_yoy(ctx: Ctx, period_day: int, months: int) -> float | None:
    """INDPRO growth for month ``period_day`` within the vintage that first released that month: the month's
    value is its first release (INDPRO_FR) and the base month comes from the same vintage (process.md R-02
    PIT line: first-release INDPRO, yoy computed within-vintage)."""
    fr = ctx.snap.raw("INDPRO_FR")
    if fr is None or ctx.source is None:
        return None
    i = fr.nearest_idx(period_day, tol=3)
    if i is None:
        return None
    key = (int(fr.days[i]), int(fr.pub_us[i]), months)
    try:
        cache = _FR_CACHE.setdefault(ctx.source, {})
    except TypeError:
        cache = ctx.memo.setdefault("_fr", {})
    if key not in cache:
        frame = snapshot_one(ctx.source, fr.published_at(i), "INDPRO")
        vint = Series.from_frame("INDPRO", frame)
        val = None
        if vint is not None:
            v_t = vint.nearest(int(fr.days[i]), tol=3)
            v_0 = vint.nearest(months_back(int(fr.days[i]), months), tol=3)
            if v_t is not None and v_0 is not None and v_0 != 0:
                val = (v_t / v_0 - 1.0) * 100.0
        cache[key] = val
    return cache[key]


@_guard
def r02_m2_minus_ip(ctx: Ctx) -> RuleOutput:
    """R-02: L2 = yoy(M2SL) - yoy(INDPRO); positive if L2 > liq.m2_ip.spread_pp, negative if L2 < 0, else
    neutral; state changes after liq.confirm_periods monthly observations."""
    win, thr, k = ctx.p.int("liq.growth_window_m"), ctx.p.num("liq.m2_ip.spread_pp"), ctx.p.int("liq.confirm_periods")
    m2, fr = ctx.snap.get("M2SL"), ctx.snap.get("INDPRO_FR")
    if m2 is None or fr is None:
        return unknown("R-02", ctx.snap.reason("M2SL", "INDPRO_FR"), variant="R-02")
    months = [int(d) for d in fr.days[fr.days <= m2.last_day + 3]][::-1][:MAX_CONFIRM_LOOKBACK + 1]
    levels, raws = [], []
    state = None
    for t in months:
        a, b = m2.nearest(t, tol=3), m2.nearest(months_back(t, win), tol=3)
        ipy = ip_first_release_yoy(ctx, t, win)
        if a is None or b is None or b == 0 or ipy is None:
            lvl = None
        else:
            lvl = (a / b - 1.0) * 100.0 - ipy
        levels.append(lvl)
        raws.append(None if lvl is None else (1 if lvl > thr else (-1 if lvl < 0 else 0)))
        if levels[0] is None:
            break
        state = _run_state(raws, k)
        if state is not None:
            break
    if not levels or levels[0] is None:
        return unknown("R-02", "M2 or first-release IP growth not computable at the latest common month",
                       variant="R-02")
    if state is None:
        return unknown("R-02", f"no {k}-month confirmed state within {MAX_CONFIRM_LOOKBACK} months",
                       variant="R-02", level=levels[0])
    t0 = date_of(months[0])
    change = levels[0] - levels[1] if len(levels) > 1 and levels[1] is not None else None
    return ok("R-02", variant="R-02", sign=state, raw_sign=raws[0], level=levels[0], change=change,
              period=t0.isoformat(), base_effect_outlier=R02_OUTLIER[0] <= t0 <= R02_OUTLIER[1], units="pp")


# ------------------------------------------------------------------ weekly helpers (R-03, R-04, R-14)


def _confirmed_on_grid(values: np.ndarray, k: int) -> tuple[int | None, int | None]:
    raws = [sign(float(v)) if np.isfinite(v) else None for v in values[::-1][:MAX_CONFIRM_LOOKBACK + k]]
    if not raws or raws[0] is None:
        return None, None
    return _run_state(raws, k), raws[0]


def holdings(ctx: Ctx):
    """Fed outright securities holdings H = TREAST + WSHOMCB on TREAST's own dates (weekly H.4.1 from
    2002-12-18; Z.1 quarterly fallback before). WSHOMCB is 0 before its first observation (catalogue)."""
    if "holdings" in ctx.memo:
        return ctx.memo["holdings"]
    tr = ctx.snap.get("TREAST")
    out = None
    if tr is not None:
        grid = tr.days[-400:]
        h = tr.values[-400:].copy()
        mbs = ctx.snap.get("WSHOMCB", fresh=False)
        if mbs is not None:
            add = mbs.asof_array(grid, max_age=6)
            add = np.where(grid < mbs.days[0], 0.0, add)
            h = h + add
        elif tr.spacing() <= 10 and int(grid[-1]) >= day(_dt.date(2002, 12, 18)):
            h = h * np.nan  # weekly era without the MBS series: unknown
        out = (grid, h, tr.tol())
    ctx.memo["holdings"] = out
    return out


def _lagged(grid: np.ndarray, vals: np.ndarray, lag_days: int, tol: float) -> np.ndarray:
    s = Series("grid", grid, vals, np.zeros(len(grid), dtype=np.int64))
    return s.nearest_array(grid - lag_days, tol=tol)


# ------------------------------------------------------------------ R-03


@_guard
def r03_net_liquidity(ctx: Ctx) -> RuleOutput:
    """R-03: NL = WALCL - WTREGEN - RRPONTSYD; impulse = change in NL over liq.netliq.window_w weeks; sign with
    liq.confirm_periods weekly confirmation. RRP is 0 before its first observation and on days without an
    operation (process.md R-03)."""
    w, k = ctx.p.int("liq.netliq.window_w"), ctx.p.int("liq.confirm_periods")
    walcl, tga = ctx.snap.get("WALCL"), ctx.snap.get("WTREGEN")
    if walcl is None or tga is None:
        return unknown("R-03", ctx.snap.reason("WALCL", "WTREGEN"), variant="R-03")
    if walcl.spacing() > 10 or tga.spacing() > 10:
        return unknown("R-03", "weekly H.4.1 inputs required (era A)", variant="R-03")
    grid = walcl.days[-300:]
    a = walcl.values[-300:]
    t = tga.nearest_array(grid, tol=3)
    rrp = ctx.snap.get("RRPONTSYD", fresh=False)
    r = np.zeros(len(grid)) if rrp is None else np.nan_to_num(rrp.asof_array(grid, max_age=3), nan=0.0) * 1000.0
    nl = a - t - r
    imp = nl - _lagged(grid, nl, 7 * w, 3)
    state, raw = _confirmed_on_grid(imp, k)
    if raw is None:
        return unknown("R-03", "impulse not computable at the latest H.4.1 week", variant="R-03")
    if state is None:
        return unknown("R-03", "no confirmed state", variant="R-03")
    prev = imp[-2] if len(imp) > 1 and np.isfinite(imp[-2]) else None
    return ok("R-03", variant="R-03", sign=state, raw_sign=raw, level=float(imp[-1]) / 1000.0,
              change=None if prev is None else float(imp[-1] - prev) / 1000.0,
              net_liquidity=float(nl[-1]) / 1000.0, period=date_of(int(grid[-1])).isoformat(), units="$bn")


# ------------------------------------------------------------------ R-04


@_guard
def r04_purchases_minus_issuance(ctx: Ctx) -> RuleOutput:
    """R-04: F = change in (TREAST + WSHOMCB) over liq.netliq.window_w weeks; I = change in debt held by the
    public over the same window; impulse = F - I; sign change confirmed per liq.confirm_periods."""
    w, k = ctx.p.int("liq.netliq.window_w"), ctx.p.int("liq.confirm_periods")
    hold = holdings(ctx)
    debt = ctx.snap.get("TFD_DEBT_HELD_PUBLIC")
    if hold is None or debt is None:
        return unknown("R-04", ctx.snap.reason("TREAST", "TFD_DEBT_HELD_PUBLIC"), variant="R-04")
    grid, h, tol = hold
    keep = grid <= debt.last_day + debt.tol()
    grid, h = grid[keep], h[keep]
    if len(grid) == 0:
        return unknown("R-04", "no common dates", variant="R-04")
    d = debt.nearest_array(grid)
    f = h - _lagged(grid, h, 7 * w, tol)
    i = d - debt.nearest_array(grid - 7 * w)
    imp = f - i
    state, raw = _confirmed_on_grid(imp, k)
    if raw is None:
        return unknown("R-04", "impulse not computable at the latest common date", variant="R-04")
    if state is None:
        return unknown("R-04", "no confirmed state", variant="R-04")
    prev = imp[-2] if len(imp) > 1 and np.isfinite(imp[-2]) else None
    freq = "weekly" if tol <= 5 else "quarterly"
    return ok("R-04", variant="R-04", sign=state, raw_sign=raw, level=float(imp[-1]) / 1000.0,
              change=None if prev is None else float(imp[-1] - prev) / 1000.0,
              fed_purchases=float(f[-1]) / 1000.0, net_issuance=float(i[-1]) / 1000.0,
              period=date_of(int(grid[-1])).isoformat(), grid=freq, units="$bn")


# ------------------------------------------------------------------ liquidity family (E.4a)


def liquidity_family(ctx: Ctx, r02: RuleOutput, r03: RuleOutput, r04: RuleOutput,
                     weights: dict[str, float]) -> RuleOutput:
    """Era-labelled liquidity family (PLAN E.4a): era B -> R-02 (the era-B measure); era A -> R-03 and R-04
    (sign of the sum of their confirmed signs when both are known). When the era's own variant is unknown or
    inactive, the other era's variant is used and the variant label says so. Rules with timeline weight 0 are
    skipped."""
    def usable(o):
        return o.ok and weights.get(o.rule, 1.0) > 0

    a_parts = [o for o in (r03, r04) if usable(o)]
    a = None
    if a_parts:
        s = sign(sum(o.values["sign"] for o in a_parts))
        drv = a_parts[0] if len(a_parts) == 1 else r03
        a = ok("LIQ", variant="+".join(o.rule for o in a_parts), sign=s, level=drv.values["level"],
               change=drv.values.get("change"), units=drv.values.get("units"),
               weight=min(weights.get(o.rule, 1.0) for o in a_parts))
    b = None
    if usable(r02):
        b = ok("LIQ", variant="R-02", sign=r02.values["sign"], level=r02.values["level"],
               change=r02.values.get("change"), units="pp", weight=weights.get("R-02", 1.0))
    first, second = (a, b) if ctx.era == "A" else (b, a)
    if first is not None:
        first.values["era"] = ctx.era
        return first
    if second is not None:
        second.variant = f"{second.variant} (fallback, era {ctx.era})"
        second.values["era"] = ctx.era
        return second
    return unknown("LIQ", "no liquidity variant known or active", variant=None)


# ------------------------------------------------------------------ R-14


RATE_EPS = 1e-9
POLICY_RATE_CHAIN = ("DFEDTARU", "DFEDTAR", "FED_DISCOUNT_RATE")  # newest record first


def policy_rate_moves(ctx: Ctx) -> tuple[np.ndarray, np.ndarray, np.ndarray, str] | None:
    """Policy-rate record up to asof as (days, levels, variant), spliced newest first: the FF target range upper
    bound (DFEDTARU, 2008-12-16 on), the FF target (DFEDTAR, 1982-09-27 to 2008-12-15), the Fed discount rate
    (FED_DISCOUNT_RATE event table, 1948-2002) for dates before the first row of the newer record. None when no
    series has a row. Read without the freshness guard: a rate stays in force until it is changed. The third
    array numbers the source series, so a level difference at a join (discount rate 10.00 on 1982-08-27 vs FF
    target 10.25 on 1982-09-27) is never read as a move."""
    days, vals, segs, variant, cut = [], [], [], None, None
    for sid in POLICY_RATE_CHAIN:
        s = ctx.snap.get(sid, fresh=False)
        if s is None:
            continue
        keep = s.days <= ctx.asof_day
        if cut is not None:
            keep &= s.days < cut
        if not keep.any():
            continue
        days.insert(0, s.days[keep])
        vals.insert(0, s.values[keep])
        segs.insert(0, np.full(int(keep.sum()), len(segs)))
        variant = variant or sid
        cut = int(s.days[keep][0])
    if not days:
        return None
    return np.concatenate(days), np.concatenate(vals), np.concatenate(segs), variant


@_guard
def r14_policy_direction(ctx: Ctx) -> RuleOutput:
    """R-14: policy_direction = Fed cycle state: the direction of the most recent policy-rate change, held until a
    change in the opposite direction ("stay long until the Fed tightens", DS/2014-07-16; "the minute they start
    tightening", DS/2021-05-11). Decision R14-04 (2026-10-07) replacing the sign of a 6-month window, which
    forgot the cycle between moves. Policy-rate record: ``policy_rate_moves``.

    Programme component (decision R14-01, spec/research_R14_balance_sheet.md design A): the state in force in
    FOMC_BS_STATE (spec/fomc_bs_events.yaml): purchase or maturity-extension programme -> easing; runoff ->
    tightening; otherwise neutral. Rate-primary (R14-02): it decides only when no policy-rate change is on
    record. QE-end setback flag: a programme was in force within liq.qe_end_setback_m months but not now.

    ``qe_active`` (read by R-17) = a purchase programme in force (EXPAND), decision R17-01."""
    setback_m = ctx.p.int("liq.qe_end_setback_m")
    rate, last_move, level, rate_src = None, None, None, None
    rec = policy_rate_moves(ctx)
    if rec is not None:
        days, vals, seg, rate_src = rec
        level = float(vals[-1])
        steps = np.flatnonzero((np.abs(np.diff(vals)) > RATE_EPS) & (seg[1:] == seg[:-1]))
        if len(steps):
            i = int(steps[-1]) + 1
            rate, last_move = (1 if vals[i] > vals[i - 1] else -1), date_of(int(days[i])).isoformat()
    bs, programme, setback = programme_state(ctx, setback_m)
    if rate is None and bs is None:
        return unknown("R-14", ctx.snap.reason("FED_DISCOUNT_RATE", "DFEDTAR", "DFEDTARU", "FOMC_BS_STATE"),
                       variant="R-14")
    direction = rate if rate or bs is None else bs  # rate-primary (decision R14-02)
    return ok("R-14", variant=rate_src or "programme", direction=_cls(direction), rate_sign=rate,
              last_move=last_move, policy_rate=level, holdings_sign=bs, programme=programme,
              qe_active=None if bs is None else bs == -1, qe_end_setback=setback)


PROGRAMME_NAMES = {-1: "EXPAND", 0: "NONE", 1: "RUNOFF"}


def programme_state(ctx: Ctx, setback_m: int) -> tuple[int | None, str | None, bool | None]:
    """Balance-sheet programme in force at asof from FOMC_BS_STATE (value = R-14 sign: -1 EXPAND, 0 NONE,
    +1 RUNOFF; period_end = effective date, published_at = announcement). Returns (sign, name, QE-end setback
    flag). An event table is sparse by nature, so the freshness guard does not apply. Unknown when absent."""
    s = ctx.snap.get("FOMC_BS_STATE", fresh=False)
    if s is None:
        return None, None, None
    now = s.asof_value(ctx.asof_day)
    if now is None:
        return None, None, None
    sg = round(now)
    since = months_back(ctx.asof_day, setback_m)
    recent = s.values[(s.days > since) & (s.days <= ctx.asof_day)]
    was = s.asof_value(since)
    expanded = (was is not None and round(was) == -1) or bool(np.any(np.round(recent) == -1))
    return sg, PROGRAMME_NAMES.get(sg), sg != -1 and expanded


def _cls(s: int | None) -> str | None:
    return None if s is None else {1: "tightening", -1: "easing", 0: "neutral"}[s]


# ------------------------------------------------------------------ inflation helpers


def cpi_yoy(ctx: Ctx, n: int = 40):
    """CPI yoy (CPIAUCSL as-of vintage, within-vintage; CPIAUCNS fallback in the lake) for the latest ``n``
    months: (period days, yoy %)."""
    if "cpi" in ctx.memo:
        return ctx.memo["cpi"]
    cpi = ctx.snap.get("CPIAUCSL")
    out = None
    if cpi is not None:
        days = cpi.days[-n:]
        base = cpi.nearest_array(months_back_arr(days, 12), tol=3)
        yoy = (cpi.values[-n:] / base - 1.0) * 100.0
        out = (days, yoy)
    ctx.memo["cpi"] = out
    return out


def fed_funds(ctx: Ctx) -> tuple[float | None, str | None]:
    """FF = effective fed funds (process.md section 0): FEDFUNDS monthly average (latest published month),
    DFF when FEDFUNDS is unavailable. Monthly average matches the monthly CPI and UNRATE inputs."""
    s = ctx.snap.get("FEDFUNDS")
    if s is not None:
        return s.last, "FEDFUNDS"
    s = ctx.snap.get("DFF")
    return (s.last, "DFF") if s is not None else (None, None)


# ------------------------------------------------------------------ R-06


def nrou_index(nrou: Series, u_day: int) -> int | None:
    """Index of the NROU quarter containing the UNRATE month (first quarter end on or after it, within one
    quarter); else the latest earlier quarter."""
    j = int(np.searchsorted(nrou.days, u_day))
    if j < len(nrou.days) and int(nrou.days[j]) - u_day <= 92:
        return j
    return j - 1 if j - 1 >= 0 else None


@_guard
def r06_policy_error(ctx: Ctx) -> RuleOutput:
    """R-06: i* = r* + pi + a(pi - pi*) + b(NROU - UNRATE); TG = FF - i*; too_loose if TG < -thr, too_tight
    if TG > +thr. UNRATE = first release (PIT line); NROU = as-of vintage value for the UNRATE quarter;
    NROU older than 2 years relative to asof -> unknown (mechanical PIT guard)."""
    rstar, pistar = ctx.p.num("policy.taylor_rstar_pct"), ctx.p.num("policy.taylor_pi_target_pct")
    a, b, thr = ctx.p.num("policy.taylor_infl_coef"), ctx.p.num("policy.taylor_ugap_coef"), ctx.p.num("policy.tg_threshold_pp")
    cy = cpi_yoy(ctx)
    u = ctx.snap.get("UNRATE_FR")
    nrou = ctx.snap.get("NROU", fresh=False)
    ff, ff_src = fed_funds(ctx)
    if cy is None or u is None or nrou is None or ff is None:
        return unknown("R-06", ctx.snap.reason("CPIAUCSL", "UNRATE_FR", "NROU", "FEDFUNDS"))
    pi = float(cy[1][-1])
    if not np.isfinite(pi):
        return unknown("R-06", "CPI yoy not computable")
    i = nrou_index(nrou, u.last_day)
    if i is None:
        return unknown("R-06", "no NROU period at or before the UNRATE month")
    n_day = int(nrou.days[i])
    if ctx.asof_day - n_day > NROU_MAX_AGE_DAYS:
        return unknown("R-06", f"NROU stale: newest usable period {date_of(n_day)} is more than 2 years before asof "
                               "(mechanical PIT guard)")
    n = float(nrou.values[i])
    istar = rstar + pi + a * (pi - pistar) + b * (n - u.last)
    tg = ff - istar
    err = "too_loose" if tg < -thr else ("too_tight" if tg > thr else "neutral")
    return ok("R-06", variant=ff_src, policy_error=err, sign={"too_loose": 1, "too_tight": -1, "neutral": 0}[err],
              tg=tg, taylor_rate=istar, ff=ff, cpi_yoy=pi, unrate_first_release=u.last, nrou=n,
              nrou_period=date_of(n_day).isoformat())


# ------------------------------------------------------------------ R-07, R-08, R-09


@_guard
def r07_no_soft_landing(ctx: Ctx, direction: str | None) -> RuleOutput:
    """R-07: CPI yoy > infl.soft_landing_pct at any point in the trailing infl.lookback_m months while
    policy_direction = tightening."""
    lvl, lb = ctx.p.num("infl.soft_landing_pct"), ctx.p.int("infl.lookback_m")
    cy = cpi_yoy(ctx)
    if cy is None:
        return unknown("R-07", ctx.snap.reason("CPIAUCSL"))
    days, yoy = cy
    win = days >= months_back(int(days[-1]), lb)
    vals = yoy[win]
    if not np.all(np.isfinite(vals)) or len(vals) == 0:
        return unknown("R-07", "CPI yoy history incomplete over the lookback")
    above = bool(np.max(vals) > lvl)
    if direction is None:
        return unknown("R-07", "policy direction unknown", cpi_above=above)
    return ok("R-07", flag=above and direction == "tightening", cpi_peak=float(np.max(vals)), cpi_above=above)


@_guard
def r08_ff_below_cpi(ctx: Ctx) -> RuleOutput:
    """R-08: CPI yoy > infl.persist_pct AND FF < CPI yoy (veto flag; infl.r08_expected_to_hold is a display
    caveat)."""
    lvl = ctx.p.num("infl.persist_pct")
    caveat = ctx.p("infl.r08_expected_to_hold")
    cy = cpi_yoy(ctx)
    ff, src = fed_funds(ctx)
    if cy is None or ff is None or not np.isfinite(cy[1][-1]):
        return unknown("R-08", ctx.snap.reason("CPIAUCSL", "FEDFUNDS"))
    pi = float(cy[1][-1])
    return ok("R-08", variant=src, flag=bool(pi > lvl and ff < pi), cpi_yoy=pi, ff=ff, expected_to_hold=caveat)


@_guard
def r09_recession_prior(ctx: Ctx, direction: str | None) -> RuleOutput:
    """R-09: CPI yoy peak in the trailing infl.lookback_m months > infl.persist_pct and policy tightening."""
    lvl, lb = ctx.p.num("infl.persist_pct"), ctx.p.int("infl.lookback_m")
    cy = cpi_yoy(ctx)
    if cy is None:
        return unknown("R-09", ctx.snap.reason("CPIAUCSL"))
    days, yoy = cy
    vals = yoy[days >= months_back(int(days[-1]), lb)]
    if not np.all(np.isfinite(vals)) or len(vals) == 0:
        return unknown("R-09", "CPI yoy history incomplete over the lookback")
    peak = float(np.max(vals))
    if direction is None:
        return unknown("R-09", "policy direction unknown", cpi_peak=peak)
    return ok("R-09", flag=bool(peak > lvl and direction == "tightening"), cpi_peak=peak)


# ------------------------------------------------------------------ R-10


def _window_changes(s: Series, months: int) -> np.ndarray:
    base = s.nearest_array(months_back_arr(s.days, months))
    ch = s.values - base
    return ch[np.isfinite(ch)]


@_guard
def r10_rates_oil_usd(ctx: Ctx) -> RuleOutput:
    """R-10: change in DGS10 > 0 AND change in WTI > 0 AND change in USD > 0 over xasset.window_m months.
    Reported variant R10_mag: each change also exceeds xasset.min_move_sd standard deviations of its own
    window change over the expanding as-of history."""
    m, msd = ctx.p.int("xasset.window_m"), ctx.p.num("xasset.min_move_sd")
    series = {"rates": ctx.snap.get("DGS10"), "oil": ctx.snap.get("DCOILWTICO"), "usd": ctx.snap.get("USD_BROAD")}
    missing = [k for k, v in series.items() if v is None]
    if missing:
        return unknown("R-10", ctx.snap.reason("DGS10", "DCOILWTICO", "USD_BROAD"))
    ch, mag = {}, {}
    for k, s in series.items():
        c = s.change(months=m)
        if c is None:
            return unknown("R-10", f"{k}: no observation {m} months before the latest")
        ch[k] = c
        hist = _window_changes(s, m)
        sd = float(np.std(hist, ddof=1)) if len(hist) > 2 else None
        mag[k] = None if sd is None else c > msd * sd
    flag = all(v > 0 for v in ch.values())
    flag_mag = None if any(v is None for v in mag.values()) else bool(flag and all(mag.values()))
    return ok("R-10", flag=flag, flag_mag=flag_mag, d_rates=ch["rates"], d_oil=ch["oil"], d_usd=ch["usd"])


# ------------------------------------------------------------------ R-11


def _pct_rank(hist: np.ndarray) -> float | None:
    hist = hist[np.isfinite(hist)]
    if len(hist) < 2:
        return None
    return float(np.mean(hist <= hist[-1]) * 100.0)


@_guard
def r11_fragility(ctx: Ctx) -> RuleOutput:
    """R-11: composite = mean of expanding as-of percentiles of six gauges; high if composite >
    fragility.high_percentile; fewer than fragility.min_components components -> unknown. ``low`` is not
    defined by the rule and is never emitted (normal otherwise). Non-gating."""
    hp, mc, cq = ctx.p.num("fragility.high_percentile"), ctx.p.int("fragility.min_components"), ctx.p.int("fragility.credit_gdp_change_q")
    s = ctx.snap
    comp: dict[str, float | None] = {}
    r = s.get("RITTER_UNPROF_IPO")
    comp["ritter_unprofitable_ipo"] = None if r is None else _pct_rank(r.values)
    h = s.get("SIFMA_HY_SHARE_A")
    comp["sifma_hy_share"] = None if h is None else _pct_rank(h.values)
    gdp = s.get("GDP")
    debt = s.get("BCNSDODNS")
    if debt is not None and gdp is not None:
        ratio = debt.values / gdp.nearest_array(debt.days, tol=3)
        rs = Series("r", debt.days, ratio, np.zeros(len(ratio), dtype=np.int64))
        chg = ratio - rs.nearest_array(months_back_arr(debt.days, 3 * cq))
        comp["credit_gdp_change"] = _pct_rank(chg) if np.isfinite(chg[-1]) else None
    else:
        comp["credit_gdp_change"] = None
    eq = s.get("NCBCEBQ027S")
    comp["net_equity_issuance_inverted"] = None if eq is None else _pct_rank(-eq.values)
    oas = s.get("BAMLH0A0HYM2")
    comp["hy_oas_inverted"] = None if oas is None else _pct_rank(-oas.values)
    mg = s.get("FINRA_MARGIN_DEBT")
    if mg is not None and gdp is not None:
        ratio = mg.values / gdp.asof_array(mg.days)
        comp["margin_debt_gdp"] = _pct_rank(ratio) if np.isfinite(ratio[-1]) else None
    else:
        comp["margin_debt_gdp"] = None
    vals = [v for v in comp.values() if v is not None]
    if len(vals) < mc:
        return unknown("R-11", f"{len(vals)} of 6 components available (< {mc})", components=len(vals))
    composite = float(np.mean(vals))
    return ok("R-11", composite=composite, level="high" if composite > hp else "normal", components=len(vals),
              **{k: v for k, v in comp.items() if v is not None})


# ------------------------------------------------------------------ R-12


REGIONS = {
    "US": {"bs": ("CB_ASSETS_GDP_US",), "rate": ("DFEDTARU", "FEDFUNDS"), "lr": "IRLTLT01USM156N"},
    "EA": {"bs": ("CB_ASSETS_GDP_XM", "CB_ASSETS_GDP_DE"), "rate": ("ECB_DFR", "DE_POLICY_RATE"),
           "lr": "IRLTLT01DEM156N"},
    "JP": {"bs": ("CB_ASSETS_GDP_JP",), "rate": ("JP_POLICY_RATE", "JP_CALL_RATE_M"), "lr": "IRLTLT01JPM156N"},
    "UK": {"bs": ("CB_ASSETS_GDP_GB",), "rate": ("UK_BANK_RATE", "GB_POLICY_RATE_BIS"), "lr": "IRLTLT01GBM156N"},
}


@_guard
def r12_cross_region(ctx: Ctx) -> dict[str, RuleOutput]:
    """R-12: per region, balance-sheet impulse = change in central-bank assets/GDP over xregion.window_w weeks
    (BIS assets/GDP, quarterly; pre-1999 EA = Germany) and policy-rate direction over the same window;
    rel(X,US) = impulse_X - impulse_US. Region direction (for the regime vector) = sign of (rate sign -
    balance-sheet sign), the R-14 construction applied to the R-12 inputs."""
    w = ctx.p.int("xregion.window_w")
    lag = 7 * w
    out: dict[str, RuleOutput] = {}
    for reg, cfg in REGIONS.items():
        bs_s = ctx.snap.first(*cfg["bs"])
        rate_s = ctx.snap.first(*cfg["rate"])
        imp = None if bs_s is None else bs_s.change(days_back=lag)
        dr = None if rate_s is None else rate_s.change(days_back=lag)
        lr = ctx.snap.get(cfg["lr"])
        if imp is None and dr is None:
            out[reg] = unknown("R-12", ctx.snap.reason(*cfg["bs"], *cfg["rate"]), variant=reg)
            continue
        rs, bsn = sign(dr), sign(imp)
        parts = [x for x in (rs, None if bsn is None else -bsn) if x is not None]
        out[reg] = ok("R-12", variant=reg, impulse=imp, rate_change=dr, rate_sign=rs, bs_sign=bsn,
                      direction=_cls(sign(sum(parts))), long_rate=None if lr is None else lr.last,
                      bs_series=None if bs_s is None else bs_s.sid, rate_series=None if rate_s is None else rate_s.sid)
    us = out["US"].get("impulse")
    for reg, o in out.items():
        if o.ok:
            o.values["rel_us"] = None if (us is None or o.values["impulse"] is None) else o.values["impulse"] - us
    return out


# ------------------------------------------------------------------ R-56, R-58, R-63


@_guard
def r56_ten_year_vs_ngdp(ctx: Ctx) -> RuleOutput:
    """R-56: gap = DGS10 - yoy(nominal GDP); gap < rates.ngdp_anchor_gap_pp -> short-duration evidence (rich);
    gap > rates.ngdp_cheap_gap_pp -> long-duration evidence (cheap)."""
    lo, hi = ctx.p.num("rates.ngdp_anchor_gap_pp"), ctx.p.num("rates.ngdp_cheap_gap_pp")
    y, gdp = ctx.snap.get("DGS10"), ctx.snap.get("GDP")
    if y is None or gdp is None:
        return unknown("R-56", ctx.snap.reason("DGS10", "GDP"))
    base = gdp.nearest(months_back(gdp.last_day, 12), tol=3)
    if base is None or base == 0:
        return unknown("R-56", "GDP base quarter missing")
    g = (gdp.last / base - 1.0) * 100.0
    gap = y.last - g
    state = "rich" if gap < lo else ("cheap" if gap > hi else "neutral")
    return ok("R-56", gap=gap, ngdp_yoy=g, dgs10=y.last, state=state)


@_guard
def r58_fci(ctx: Ctx) -> RuleOutput:
    """R-58: loose if NFCI < fci.loose_threshold and its fci.change_window_w-week change < 0; tight if NFCI > 0
    and rising; else neutral. NFCI rows before first publication (2011-05-25) are unusable -> unknown."""
    thr, w = ctx.p.num("fci.loose_threshold"), ctx.p.int("fci.change_window_w")
    s = ctx.snap.get("NFCI")
    if s is None:
        return unknown("R-58", ctx.snap.reason("NFCI"))
    ch = s.change(days_back=7 * w)
    if ch is None:
        return unknown("R-58", "NFCI change window incomplete")
    state = "loose" if (s.last < thr and ch < 0) else ("tight" if (s.last > 0 and ch > 0) else "neutral")
    return ok("R-58", fci_state=state, nfci=s.last, change=ch)


@_guard
def r63_fiscal_supply(ctx: Ctx, r04: RuleOutput) -> RuleOutput:
    """R-63: issuance/GDP above its fiscal.issuance_median_y-year as-of median AND deficit/GDP >
    fiscal.deficit_gdp_pct AND UNRATE < NROU -> short-duration evidence. Active from fiscal.active_from_year."""
    yr = ctx.p.int("fiscal.active_from_year")
    if ctx.asof.year < yr:
        return RuleOutput("R-63", "inactive", reason=f"active from {yr} (fiscal.active_from_year)")
    my, dthr = ctx.p.int("fiscal.issuance_median_y"), ctx.p.num("fiscal.deficit_gdp_pct")
    deficit = ctx.snap.get("FYFSGDA188S")
    debt, gdp, u = ctx.snap.get("TFD_DEBT_HELD_PUBLIC"), ctx.snap.get("GDP"), ctx.snap.get("UNRATE_FR")
    nrou = ctx.snap.get("NROU", fresh=False)
    need = {"FYFSGDA188S": deficit, "TFD_DEBT_HELD_PUBLIC": debt, "GDP": gdp, "UNRATE_FR": u, "NROU": nrou}
    if any(v is None for v in need.values()):
        return unknown("R-63", ctx.snap.reason(*[k for k, v in need.items() if v is None]))
    w = ctx.p.int("liq.netliq.window_w")
    since = months_back(debt.last_day, 12 * my)
    days = debt.days[debt.days >= since]
    iss = debt.nearest_array(days) - debt.nearest_array(days - 7 * w)
    ratio = iss / gdp.asof_array(days)
    ratio = ratio[np.isfinite(ratio)]
    if len(ratio) < 2:
        return unknown("R-63", "issuance/GDP history too short")
    j = nrou_index(nrou, u.last_day)
    if j is None or ctx.asof_day - int(nrou.days[j]) > NROU_MAX_AGE_DAYS:
        return unknown("R-63", "NROU missing or stale (mechanical PIT guard)")
    n = float(nrou.values[j])
    heavy = bool(ratio[-1] > np.median(ratio))
    big_deficit = deficit.last < -dthr  # FYFSGDA188S: surplus (+) / deficit (-) as % of GDP
    return ok("R-63", flag=bool(heavy and big_deficit and u.last < n), issuance_gdp=float(ratio[-1]),
              issuance_gdp_median=float(np.median(ratio)), deficit_gdp=deficit.last)
