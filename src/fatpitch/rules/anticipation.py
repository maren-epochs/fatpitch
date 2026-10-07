"""R-67 anticipated policy turn, design v2 (V2-B), and R-68 inflation relative to the Fed's projection
(spec\\process.md section 1, R-67 and R-68; hybrid track only).

Design source: ``spec\\research_R67_v2_R68.md`` sections 2, 3 (V2-B), 3a and 4; owner decisions R67-05 (V2-B),
INFL-04 (weighted inflation composite), R67-06 (bill-price forward, seasonally neutral NSA form) and R68-02
(R-68 hybrid only, report-only). Not part of the faithful track: no effect on the regime vector, Gate 1 or the
Fed cycle check until R-67 passes the Fed anticipation test (spec\\scoring.md 6e); until then a warning flag.

Legs (sign convention as step 1: +1 tightening, -1 easing, 0 neutral):

* M2 (path): ``M2_bp = (DGS2 - FF) x 100`` (``DGS1 - FF`` before DGS2 exists, 1976-06), reading at the asof
  close, no smoothing; class beyond +-``antic.path_band_bp``.
* MB (bill forward, C1): bill prices ``P_k = 1 - d_k t_k / 360`` (t3 = 91, t6 = 182 days),
  ``f = (P3/P6 - 1) 360/91``, ``r3 = (1/P3 - 1) 360/91``, ``MB_bp = (f - r3) 1e4``, mean over the latest
  ``antic.smooth_d`` common trading days; class beyond +-``antic.band_bp``.
* I4 (inflation composite, INFL-04): per measure j (headline CPI, core CPI, PCE, core PCE) ``I_j = pi6_j -
  pi12_j`` (SA vintage) or the seasonally neutral ``(ann6_j(t) - ann6_j(t-12)) / 2`` (NSA series), precision
  weight ``w_j = 1 / var(month-to-month change of I_j)`` over the trailing ``antic.infl_weight_window_m``
  changes (at least ``antic.infl_weight_min_n``, else excluded); ``I = sum w I / sum w``, ``pi6 = sum w pi6 /
  sum w`` over at least ``antic.infl_min_known`` known measures. Tightening if ``I > antic.infl_band_pp`` and
  ``pi6 > policy.taylor_pi_target_pct``; easing if ``I < -antic.infl_band_pp``; else neutral.
* Gr (growth/stress, easing side only): R-10 flag OR (R-15 direction down AND every known R-17 credit spread wider
  than ``internals.curve_credit_trend_m`` months earlier); off while the R-08 condition holds.
* ZLB: at DFF < ``antic.zlb_ff_pct`` an easing reading of any leg is neutral (Gr: off); hike readings stand.

V2-B: (1) M2 non-neutral -> M2, except M2 tightening with I4 easing -> neutral. (2) Else MB non-neutral -> MB,
except MB tightening with (I4 easing or Gr on) -> neutral. (3) Else T = I4 tightening held at 2 month ends,
E = Gr on held at 2 month ends: T only -> tightening, E only -> easing, both or neither -> neutral.

C4 (research section 2): a leg whose input series has no usable data at asof (the series does not exist in the
era) is *absent* and the rule is computed from the remaining legs; a leg whose data exist but are stale or not
computable is *unknown*, and the output is unknown only when the result depends on it. As in D3 (process.md R-67
before v2: "if M neutral or unknown -> I"), an unknown market leg passes to the next step.
"""

from __future__ import annotations

import datetime as _dt

import numpy as np

from fatpitch.rules.outputs import RuleOutput, ok, unknown
from fatpitch.rules.series import Series, Snap, date_of, months_back, months_back_arr
from fatpitch.rules.step1 import Ctx, _cls, _guard

ABSENT = "absent"            # C4: input series has no usable data at asof (not in the era)

BILL_IDS = ("DTB3", "DTB6")
BILL_DAYS = {3: 91, 6: 182}  # bill day counts (C1): conventions of the 13- and 26-week bills, not parameters
PATH_IDS = ("DGS2", "DGS1")
FF_IDS = ("DFF", "FEDFUNDS")
# I4 measures: (name, SA vintage series, NSA series used before the SA vintage store, or None)
MEASURES = (("cpi", "CPIAUCSL", "CPIAUCNS"), ("core_cpi", "CPILFESL", "CPILFENS"),
            ("pce", "PCEPI", None), ("core_pce", "PCEPILFE", None))
CPI_IDS = tuple(s for _, sa, nsa in MEASURES for s in (sa, nsa) if s)
LEADING_ETFS = ("ETF_SPY", "ETF_XHB", "ETF_IYT", "ETF_XTN", "ETF_XRT", "ETF_KBE", "ETF_IWM", "ETF_XME", "ETF_SMH")
GR_IDS = ("DGS10", "DCOILWTICO", "USD_BROAD", *LEADING_ETFS, "BAA", "GS10", "BAMLH0A0HYM2", "DGS2", "TB3MS",
          "CPIAUCSL", "FEDFUNDS", "DFF")
SEP_MEDIAN, SEP_CT_LOW, SEP_CT_HIGH = "SEP_CORE_PCE_MEDIAN", "SEP_CORE_PCE_CT_LOW", "SEP_CORE_PCE_CT_HIGH"
SEP_IDS = (SEP_MEDIAN, SEP_CT_LOW, SEP_CT_HIGH)
R68_IDS = ("PCEPILFE", *SEP_IDS)
SERIES = tuple(dict.fromkeys((*BILL_IDS, *PATH_IDS, *FF_IDS, *CPI_IDS, *GR_IDS, *R68_IDS)))
PREV_IDS = tuple(dict.fromkeys((*GR_IDS, *R68_IDS)))
# Hold: process.md R-67 "held = same class at 2 consecutive month ends". A design count (D3 definition, unchanged
# under v2, research section 3a "Hold | 2 month ends | Definition").
I_HOLD_MONTH_ENDS = 2
ONSET_LOOKBACK_D = 800       # computational bound: trading days searched back for the onset of a market run
ONSET_LOOKBACK_M = 60        # computational bound: months searched back for the onset of an I4 run
DFF_MAX_AGE_D = 10           # mechanical PIT guard: a DFF value older than 10 days is not a current level
FEDFUNDS_MAX_AGE_D = 45      # same guard for the monthly FEDFUNDS fallback (one month plus publication)
VAR_FLOOR = 1e-12            # numerical guard: a zero-variance momentum series gets a finite (dominant) weight


# ------------------------------------------------------------------------------------------------ helpers


def _bill_class(x: float, band: float) -> int:
    return 1 if x > band else (-1 if x < -band else 0)


def _zlb(cls, ff: float | None, zlb: float):
    """Easing reading at FF < zlb -> neutral. Easing with FF unknown -> unknown (the reading depends on it)."""
    if cls != -1:
        return cls
    if ff is None or not np.isfinite(ff):
        return None
    return 0 if ff < zlb else -1


def _lbl(x) -> str | None:
    if x is ABSENT or x == ABSENT:
        return ABSENT
    if isinstance(x, bool):
        return "on" if x else "off"
    return _cls(x)


def _known(x) -> bool:
    return x is not None and x is not ABSENT and x != ABSENT


def _ff_series(snap: Snap) -> tuple[Series | None, float, bool]:
    """FF for the legs: DFF (daily), FEDFUNDS when DFF is unavailable (process.md section 0). Returns the series,
    its max age for a current level, and whether any FF series has usable data."""
    s = snap.get("DFF")
    if s is not None:
        return s, DFF_MAX_AGE_D, True
    s = snap.get("FEDFUNDS")
    if s is not None:
        return s, FEDFUNDS_MAX_AGE_D, True
    return None, DFF_MAX_AGE_D, any(snap.raw(x) is not None for x in FF_IDS)


def _dff_now(ctx: Ctx) -> float | None:
    s = ctx.snap.get("DFF", fresh=False)
    v = None if s is None else s.asof_value(ctx.asof_day, max_age=DFF_MAX_AGE_D)
    return v


def prev_month_end(asof: _dt.datetime) -> _dt.datetime:
    """16:00 ET on the last NYSE trading day of the month before asof's month (the previous month end)."""
    from fatpitch.dates import et_close, last_trading_day

    d = asof.date().replace(day=1) - _dt.timedelta(days=1)
    return et_close(last_trading_day(d))


def prev_ctx(ctx: Ctx) -> Ctx | None:
    """Point-in-time context at the previous month end, through the same Source (data enter only through a
    Source); None without a source. Cached in ``ctx.memo``."""
    if "prev_ctx" in ctx.memo:
        return ctx.memo["prev_ctx"]
    out = None
    src = ctx.source
    if src is not None:
        when = prev_month_end(ctx.asof)
        entries = getattr(src, "entries", None)
        ids = [s for s in PREV_IDS if entries is None or s in entries]
        try:
            frames = src.snapshot(when, series=ids)
        except TypeError:
            frames = src.snapshot(when)
        out = Ctx(when, Snap(frames, when), ctx.p, src)
    ctx.memo["prev_ctx"] = out
    return out


def _run_start(hist: list, value) -> int:
    """Index of the first element of the uninterrupted run of ``value`` ending at the last element."""
    j = len(hist) - 1
    while j - 1 >= 0 and hist[j - 1] == value:
        j -= 1
    return j


def _months_between(a: int, b: int) -> int:
    da, db = date_of(a), date_of(b)
    return (db.year - da.year) * 12 + (db.month - da.month)


# ------------------------------------------------------------------------------------------------ M2 (path)


def path_spread(snap: Snap) -> tuple[float | None, str | None, object]:
    """``(DGS2 - FF) x 100`` at the latest observations (DGS1 before DGS2 exists). Returns (bp, series id,
    status) with status ABSENT when no yield or FF series has usable data, None when stale."""
    y = snap.get("DGS2") or snap.get("DGS1")
    ff, _, ff_exists = _ff_series(snap)
    if y is None or ff is None:
        exists = any(snap.raw(x) is not None for x in PATH_IDS) and ff_exists
        return None, None, (None if exists else ABSENT)
    return (y.last - ff.last) * 100.0, y.sid, "ok"


def path_part(ctx: Ctx) -> dict:
    """M2 leg. ``cls`` is ABSENT, None (unknown) or the ZLB-adjusted class; ``hist`` the daily class history."""
    band, zlb = ctx.p.num("antic.path_band_bp"), ctx.p.num("antic.zlb_ff_pct")
    bp, sid, st = path_spread(ctx.snap)
    if st != "ok":
        return {"cls": st, "bp": None, "series": None}
    y = ctx.snap.get(sid)
    ff, age, _ = _ff_series(ctx.snap)
    dff_now = _dff_now(ctx)
    raw = _bill_class(bp, band)
    days = y.days[-ONSET_LOOKBACK_D:]
    ffh = ff.asof_array(days, max_age=age)
    dffh = (ctx.snap.get("DFF", fresh=False).asof_array(days, max_age=DFF_MAX_AGE_D)
            if ctx.snap.raw("DFF") is not None else np.full(len(days), np.nan))
    sp = (y.values[-ONSET_LOOKBACK_D:] - ffh) * 100.0
    hist = [None if not np.isfinite(x) else _zlb(_bill_class(float(x), band), float(f), zlb)
            for x, f in zip(sp, dffh, strict=True)]
    return {"cls": _zlb(raw, dff_now, zlb), "raw": raw, "bp": float(bp), "series": sid, "days": days, "hist": hist}


# ------------------------------------------------------------------------------------------------ MB (bills)


def bill_forward_bp(d3, d6, t3: int = 91, t6: int = 182):
    """C1: 3m->6m forward minus 3-month spot from bill prices (discount yields in percent), basis points."""
    d3, d6 = np.asarray(d3, dtype=float), np.asarray(d6, dtype=float)
    p3 = 1.0 - d3 / 100.0 * t3 / 360.0
    p6 = 1.0 - d6 / 100.0 * t6 / 360.0
    f = (p3 / p6 - 1.0) * 360.0 / (t6 - t3)
    r3 = (1.0 / p3 - 1.0) * 360.0 / t3
    return (f - r3) * 1e4


def bill_part(ctx: Ctx) -> dict:
    """MB leg on the bills' common trading days (20-day mean). ABSENT when a bill has no usable data, None when a
    bill is stale or fewer than ``antic.smooth_d`` common days exist."""
    band, n = ctx.p.num("antic.band_bp"), ctx.p.int("antic.smooth_d")
    h1, h2 = (int(x) for x in ctx.p("antic.horizon_m"))
    zlb = ctx.p.num("antic.zlb_ff_pct")
    if any(ctx.snap.raw(s) is None for s in BILL_IDS):
        return {"cls": ABSENT, "bp": None}
    if h1 not in BILL_DAYS or h2 not in BILL_DAYS:
        return {"cls": None, "bp": None, "why": f"bill horizon {h1}/{h2} months has no day-count convention"}
    b3, b6 = ctx.snap.get("DTB3"), ctx.snap.get("DTB6")
    if b3 is None or b6 is None:
        return {"cls": None, "bp": None, "why": ctx.snap.reason(*BILL_IDS)}
    common, i3, i6 = np.intersect1d(b3.days, b6.days, assume_unique=True, return_indices=True)
    if len(common) < n:
        return {"cls": None, "bp": None, "why": f"fewer than {n} common bill days"}
    keep = slice(-(ONSET_LOOKBACK_D + n), None)
    days, v3, v6 = common[keep], b3.values[i3][keep], b6.values[i6][keep]
    raw = bill_forward_bp(v3, v6, BILL_DAYS[h1], BILL_DAYS[h2])
    c = np.cumsum(np.insert(raw, 0, 0.0))
    sm = (c[n:] - c[:-n]) / n
    sm_days = days[n - 1:]
    dff = ctx.snap.get("DFF", fresh=False)
    ffh = dff.asof_array(sm_days, max_age=DFF_MAX_AGE_D) if dff is not None else np.full(len(sm_days), np.nan)
    hist = [_zlb(_bill_class(float(x), band), float(f), zlb) for x, f in zip(sm, ffh, strict=True)]
    return {"cls": hist[-1], "raw": _bill_class(float(sm[-1]), band), "bp": float(sm[-1]),
            "days": sm_days, "hist": hist}


# ------------------------------------------------------------------------------------------------ I4 (inflation)


def _lag_index(days: np.ndarray, months: int) -> np.ndarray:
    """Index of the observation ``months`` months before each day (within 3 days), -1 when none."""
    tgt = months_back_arr(days, months)
    i = np.searchsorted(days, tgt)
    lo, hi = np.clip(i - 1, 0, len(days) - 1), np.clip(i, 0, len(days) - 1)
    pick = np.where(np.abs(days[hi] - tgt) < np.abs(days[lo] - tgt), hi, lo)
    return np.where(np.abs(days[pick] - tgt) <= 3, pick, -1)


def momentum(days: np.ndarray, vals: np.ndarray, nsa: bool, s_m: int = 6, l_m: int = 12):
    """Per observation: pi6 (``s_m``-month annualised %), pi12 (``l_m``-month %), I. SA: ``I = pi6 - pi12``.
    NSA (seasonally neutral, R67-06): ``I = (ann6(t) - ann6(t - 12 months)) / 2``, the same six calendar months a
    year apart."""
    js, jl = _lag_index(days, s_m), _lag_index(days, l_m)
    with np.errstate(divide="ignore", invalid="ignore"):
        base_s = np.where(js >= 0, vals[np.clip(js, 0, None)], np.nan)
        base_l = np.where(jl >= 0, vals[np.clip(jl, 0, None)], np.nan)
        pi6 = ((vals / base_s) ** (12.0 / s_m) - 1.0) * 100.0
        pi12 = ((vals / base_l) ** (12.0 / l_m) - 1.0) * 100.0
        if nsa:
            j12 = _lag_index(days, 12)
            prev = np.where(j12 >= 0, pi6[np.clip(j12, 0, None)], np.nan)
            i_pp = (pi6 - prev) / 2.0
        else:
            i_pp = pi6 - pi12
    return pi6, pi12, i_pp


def precision_weight(days: np.ndarray, i_pp: np.ndarray, end: int, window: int, min_n: int) -> tuple[float | None, int]:
    """INFL-04: 1 / var of the month-to-month change of I over the trailing ``window`` changes ending at index
    ``end`` (consecutive monthly observations only, within the as-of vintage). None when fewer than ``min_n``
    changes are available."""
    lo = max(1, end - window + 1)
    if end < 1:
        return None, 0
    idx = np.arange(lo, end + 1)
    gap = days[idx] - days[idx - 1]
    d = i_pp[idx] - i_pp[idx - 1]
    d = d[(gap >= 27) & (gap <= 32) & np.isfinite(d)]
    if len(d) < max(min_n, 2):
        return None, len(d)
    return 1.0 / max(float(np.var(d, ddof=1)), VAR_FLOOR), len(d)


def _measure(ctx: Ctx, name: str, sa: str, nsa: str | None) -> dict:
    """One I4 measure: status known | unknown (data exist but stale or not computable) | absent (no usable data
    at asof) | excluded (fewer than ``antic.infl_weight_min_n`` changes; history too short in the era)."""
    s_m, l_m = ctx.p.int("antic.infl_short_m"), ctx.p.int("antic.infl_long_m")
    window, min_n = ctx.p.int("antic.infl_weight_window_m"), ctx.p.int("antic.infl_weight_min_n")
    out = {"name": name, "series": None, "form": None, "status": ABSENT}
    for sid, form in ((sa, "SA"), (nsa, "NSA")):
        if sid is None or ctx.snap.raw(sid) is None:
            continue
        out.update(series=sid, form=form)
        s = ctx.snap.get(sid)
        if s is None:
            out.update(status="unknown", why=ctx.snap.reason(sid))
            return out
        tail = window + ONSET_LOOKBACK_M + 2 * l_m + 4
        days, vals = s.days[-tail:], s.values[-tail:]
        pi6, pi12, i_pp = momentum(days, vals, form == "NSA", s_m, l_m)
        out.update(days=days, pi6=pi6, pi12=pi12, i_pp=i_pp, period=date_of(int(days[-1])).isoformat())
        w, n_ch = precision_weight(days, i_pp, len(days) - 1, window, min_n)
        out["n_changes"] = n_ch
        if not np.isfinite(i_pp[-1]) or not np.isfinite(pi6[-1]):
            need = s_m + 12 if form == "NSA" else max(s_m, l_m)
            short = int(s.days[0]) > months_back(int(days[-1]), need)
            out["status"] = "excluded" if short else "unknown"
            return out
        out["status"] = "known" if w is not None else "excluded"
        return out
    return out


def _composite(ms: list[dict], k: int, ctx: Ctx) -> tuple[float | None, float | None, dict[str, float]]:
    """Weighted composite of the measures' readings ``k`` observations before their latest (each measure its
    own latest observation, no alignment: research section 2a)."""
    window, min_n = ctx.p.int("antic.infl_weight_window_m"), ctx.p.int("antic.infl_weight_min_n")
    min_known = ctx.p.int("antic.infl_min_known")
    num_i = num_p = den = 0.0
    ws: dict[str, float] = {}
    for m in ms:
        end = len(m["days"]) - 1 - k
        if end < 0 or not np.isfinite(m["i_pp"][end]) or not np.isfinite(m["pi6"][end]):
            continue
        w = m["w"] if k == 0 else precision_weight(m["days"], m["i_pp"], end, window, min_n)[0]
        if w is None:
            continue
        ws[m["name"]] = w
        num_i += w * float(m["i_pp"][end])
        num_p += w * float(m["pi6"][end])
        den += w
    if len(ws) < min_known:
        return None, None, ws
    return num_i / den, num_p / den, ws


def inflation_part(ctx: Ctx) -> dict:
    """I4 leg: per-measure readings and weights, the composite at asof and its class history (one reading per
    observation step back, ZLB at the month end at which that step was the latest; the D3 within-vintage hold)."""
    band, target = ctx.p.num("antic.infl_band_pp"), ctx.p.num("policy.taylor_pi_target_pct")
    zlb, min_known = ctx.p.num("antic.zlb_ff_pct"), ctx.p.int("antic.infl_min_known")
    window, min_n = ctx.p.int("antic.infl_weight_window_m"), ctx.p.int("antic.infl_weight_min_n")
    ms = [_measure(ctx, *m) for m in MEASURES]
    known = [m for m in ms if m["status"] == "known"]
    for m in known:
        m["w"] = precision_weight(m["days"], m["i_pp"], len(m["days"]) - 1, window, min_n)[0]
    n_unknown = sum(m["status"] == "unknown" for m in ms)
    out = {"measures": ms, "n_known": len(known), "n_unknown": n_unknown, "i": None, "pi6": None, "weights": {}}
    if len(known) < min_known:
        out["cls"] = None if len(known) + n_unknown >= min_known else ABSENT
        out["hist"] = []
        return out
    dff = ctx.snap.get("DFF", fresh=False)
    hist: list = []
    for k in range(ONSET_LOOKBACK_M, -1, -1):
        i, p6, ws = _composite(known, k, ctx)
        if k == 0:
            out.update(i=i, pi6=p6, weights=ws)
        if i is None:
            hist.append(None)
            continue
        raw = 1 if (i > band and p6 > target) else (-1 if i < -band else 0)
        me = months_back(ctx.asof_day, k)
        ff = dff.asof_value(me, max_age=DFF_MAX_AGE_D) if dff is not None else None
        hist.append(_zlb(raw, ff, zlb))
    out["cls"] = hist[-1]
    out["hist"] = hist
    return out


# ------------------------------------------------------------------------------------------------ Gr (stress)


def _r15_down(ctx: Ctx):
    from fatpitch.rules import step1b

    lb = ctx.p.int("internals.rs_lookback_m")
    mkt = ctx.snap.raw(step1b.MARKET_ETF)
    members = [s for nm in ctx.p("internals.leading_set") for s in step1b.LEADING_ETF.get(nm, ())
               if ctx.snap.raw(s) is not None]
    if mkt is None or not members or int(mkt.days[0]) > months_back(ctx.asof_day, lb):
        return ABSENT
    r = step1b.r15_leading_industries(ctx)
    return None if not r.ok else r.get("direction") == "down"


def _r10_flag(ctx: Ctx):
    from fatpitch.rules import step1

    m = ctx.p.int("xasset.window_m")
    raws = [ctx.snap.raw(s) for s in ("DGS10", "DCOILWTICO", "USD_BROAD")]
    if any(s is None for s in raws) or any(int(s.days[0]) > months_back(ctx.asof_day, m) for s in raws):
        return ABSENT
    r = step1.r10_rates_oil_usd(ctx)
    return None if not r.ok else bool(r.get("flag"))


def _credit_wider(ctx: Ctx):
    """Every known R-17 credit spread (BAA - GS10; HY OAS where it exists) wider than
    ``internals.curve_credit_trend_m`` months earlier. Spec reading: "every known" - spreads that exist but are
    unknown at asof are skipped; at least one known spread is required (none known -> unknown)."""
    from fatpitch.rules import step1b

    exists = {"credit_baa": all(ctx.snap.raw(s) is not None for s in ("BAA", "GS10")),
              "credit_hy": ctx.snap.raw("BAMLH0A0HYM2") is not None}
    if not any(exists.values()):
        return ABSENT
    r = step1b.r17_curve_credit(ctx, None)
    vals = [r.get(f"d_{k}") for k, e in exists.items() if e]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return all(v > 0 for v in vals)


def _and3(a, b):
    if a is ABSENT or b is ABSENT:
        return ABSENT
    if a is False or b is False:
        return False
    if a is None or b is None:
        return None
    return True


def _or3(a, b):
    if a is ABSENT and b is ABSENT:
        return ABSENT
    if a is True or b is True:
        return True
    if a is None or b is None:
        return None
    return False


def growth_reading(ctx: Ctx) -> dict:
    """Gr at one context: on (True), off (False), unknown (None) or ABSENT, with its parts."""
    from fatpitch.rules import step1

    zlb = ctx.p.num("antic.zlb_ff_pct")
    r10, r15, cr = _r10_flag(ctx), _r15_down(ctx), _credit_wider(ctx)
    raw = _or3(r10, _and3(r15, cr))
    r08o = step1.r08_ff_below_cpi(ctx)
    r08 = bool(r08o.get("flag")) if r08o.ok else None
    gr = raw
    if raw is True:
        if r08 is True:
            gr = False
        elif r08 is None:
            gr = None
        else:
            ff = _dff_now(ctx)
            gr = None if ff is None else not ff < zlb
    return {"gr": gr, "raw": raw, "r10": r10, "r15_down": r15, "credit_wider": cr, "r08": r08}


# ------------------------------------------------------------------------------------------------ R-67 v2


def _held(cur, prev, value):
    """Three-valued "cur == value at 2 consecutive month ends"; ABSENT never holds."""
    if not _known(cur):
        return None if cur is None else False
    if cur != value:
        return False
    if not _known(prev):
        return None if prev is None else False
    return prev == value


@_guard
def r67_anticipated_turn(ctx: Ctx) -> RuleOutput:
    """R-67 v2 (V2-B). Output: ``direction``, ``component`` (the leg or guard that decided), per-leg values and
    classes (``absent`` where C4 applies), the I4 per-measure readings (``<measure>_i``, ``_pi6``, ``_pi12``,
    ``_w``, ``_series``, ``_status``), ``onset_date`` and ``lead_age_m`` where computable (M2, MB, I4)."""
    m2 = path_part(ctx)
    mb = bill_part(ctx)
    i4 = inflation_part(ctx)
    gr = growth_reading(ctx)
    m2c, mbc, i4c, grc = m2["cls"], mb["cls"], i4["cls"], gr["gr"]
    i4h = i4["hist"]
    i4p = i4h[-2] if len(i4h) >= I_HOLD_MONTH_ENDS else (ABSENT if i4c is ABSENT else None)
    vals = {"m2_bp": m2.get("bp"), "m2_class": _lbl(m2c), "m2_series": m2.get("series"),
            "mb_bp": mb.get("bp"), "mb_class": _lbl(mbc),
            "i4_i": i4["i"], "i4_pi6": i4["pi6"], "i4_class": _lbl(i4c), "i4_prev_class": _lbl(i4p),
            "i4_known": i4["n_known"],
            "gr": _lbl(grc), "gr_r10": _lbl(gr["r10"]), "gr_r15_down": _lbl(gr["r15_down"]),
            "gr_credit_wider": _lbl(gr["credit_wider"]), "gr_r08": _lbl(gr["r08"]), "dff": _dff_now(ctx)}
    wsum = sum(i4["weights"].values()) or None
    for m in i4["measures"]:
        nm, end = m["name"], (len(m["days"]) - 1 if "days" in m else None)
        ok_ = end is not None and end >= 0
        vals.update({f"{nm}_series": m["series"], f"{nm}_status": m["status"],
                     f"{nm}_i": float(m["i_pp"][end]) if ok_ and np.isfinite(m["i_pp"][end]) else None,
                     f"{nm}_pi6": float(m["pi6"][end]) if ok_ and np.isfinite(m["pi6"][end]) else None,
                     f"{nm}_pi12": float(m["pi12"][end]) if ok_ and np.isfinite(m["pi12"][end]) else None,
                     f"{nm}_w": (i4["weights"][nm] / wsum) if wsum and nm in i4["weights"] else None})

    def unk(why: str) -> RuleOutput:
        return unknown("R-67", why, variant="hybrid", **vals)

    if not any(_known(x) for x in (m2c, mbc, i4c, grc)):
        return unk(f"no leg known (M2 {_lbl(m2c)}, MB {_lbl(mbc)}, I4 {_lbl(i4c)}, Gr {_lbl(grc)})")

    direction: int
    if m2c in (1, -1):
        if m2c == 1 and i4c is None:
            return unk("M2 prices tightening; I4 guard not computable")
        if m2c == 1 and i4c == -1:
            direction, component = 0, "M2 guard (I4 easing)"
        else:
            direction, component = m2c, "M2"
    elif mbc in (1, -1):
        if mbc == 1:
            if i4c == -1 or grc is True:
                direction, component = 0, "MB guard (" + ("I4 easing" if i4c == -1 else "Gr on") + ")"
            elif i4c is None or grc is None:
                return unk(f"MB prices tightening; guard not computable (I4 {_lbl(i4c)}, Gr {_lbl(grc)})")
            else:
                direction, component = 1, "MB"
        else:
            direction, component = -1, "MB"
    else:
        t = _held(i4c, i4p, 1)
        grp = None
        if grc is True:
            pc = prev_ctx(ctx)
            grp = growth_reading(pc)["gr"] if pc is not None else None
            vals["gr_prev"] = _lbl(grp)
        e = _held(grc, grp, True)
        vals.update(t_held=t, e_held=e)
        if t is None or e is None:
            return unk(f"fallback depends on an unknown hold (I4 tightening held {t}, Gr on held {e})")
        if t and not e:
            direction, component = 1, "I4"
        elif e and not t:
            direction, component = -1, "Gr"
        else:
            direction, component = 0, "fallback (" + ("both" if t else "neither") + ")"

    onset = None
    leg = component if component in ("M2", "MB", "I4") else None
    if direction and leg in ("M2", "MB"):
        src = m2 if leg == "M2" else mb
        j = _run_start(src["hist"], direction)
        onset = int(src["days"][j]) if j > 0 else None   # run reaching the lookback bound: not computable
    elif direction and leg == "I4":
        j = _run_start(i4h, direction)
        if j > 0:
            onset = months_back(ctx.asof_day, len(i4h) - 1 - j)
    vals.update(direction=_cls(direction), component=component,
                onset_date=None if onset is None else date_of(onset).isoformat(),
                lead_age_m=None if onset is None else _months_between(onset, ctx.asof_day))
    return ok("R-67", variant="hybrid", **vals)


def anticipated_turn(r67: RuleOutput, r14_class: str | None) -> bool | None:
    """Warning flag (process.md R-67 role; research_market_implied_fed.md 5d option A): True when R-67 anticipates
    a move (tightening or easing) that differs from the R-14 class; None when either is unknown.

    Spec reading: process.md says "anticipated_turn when R-67 != the R-14 class"; a neutral R-67 against an
    active R-14 is not an anticipated turn and does not raise the flag."""
    d = r67.get("direction")
    if d is None or r14_class is None:
        return None
    return d != "neutral" and d != r14_class


# ------------------------------------------------------------------------------------------------ R-68


def _sep_projection(ctx: Ctx) -> dict:
    """Core PCE projection for the calendar year of asof from the latest SEP published at asof: median when the
    latest SEP has one (from 2015-09), else the central-tendency midpoint. Rows are year-end periods per horizon
    year (``fatpitch.lake.read_spec_events_sep``); the as-of view keeps the latest release per year."""
    max_age = ctx.p.num("r68.sep_max_age_d")
    series = {sid: ctx.snap.raw(sid) for sid in SEP_IDS}
    pubs = [int(s.pub_us.max()) for s in series.values() if s is not None and len(s)]
    if not pubs:
        return {"why": "no SEP published at asof (first SEP 2007-11-20)"}
    latest = max(pubs)
    pub_dt = _dt.datetime(1970, 1, 1, tzinfo=_dt.UTC) + _dt.timedelta(microseconds=latest)
    pub_dt = pub_dt.astimezone(ctx.asof.tzinfo)
    if ctx.asof_day - (pub_dt.date() - _dt.date(1970, 1, 1)).days > max_age:
        return {"why": f"latest SEP ({pub_dt.date()}) older than {max_age:g} days", "sep_published": pub_dt}
    year_end = (_dt.date(ctx.asof.year, 12, 31) - _dt.date(1970, 1, 1)).days

    def pick(sid):
        s = series[sid]
        if s is None:
            return None
        idx = np.flatnonzero((s.days == year_end) & (s.pub_us == latest))
        return float(s.values[idx[-1]]) if len(idx) else None

    md = pick(SEP_MEDIAN)
    if md is not None:
        return {"proj": md, "stat": "median", "sep_published": pub_dt}
    lo, hi = pick(SEP_CT_LOW), pick(SEP_CT_HIGH)
    if lo is not None and hi is not None:
        return {"proj": (lo + hi) / 2.0, "stat": "central_tendency", "sep_published": pub_dt}
    return {"why": f"latest SEP ({pub_dt.date()}) has no core PCE projection for {ctx.asof.year}",
            "sep_published": pub_dt}


def r68_reading(ctx: Ctx) -> dict:
    """Gap and raw class at one context: ``G = pi6(core PCE, as-of vintage) - P_y``; behind (+1) if G >
    ``r68.band_pp``, ahead (-1) if G < -band, in line (0); None with ``why`` when unknown."""
    s_m, band = ctx.p.int("r68.short_m"), ctx.p.num("r68.band_pp")
    proj = _sep_projection(ctx)
    out = {"proj": proj.get("proj"), "stat": proj.get("stat"),
           "sep_published": proj.get("sep_published").isoformat() if proj.get("sep_published") else None,
           "pi6": None, "gap": None, "cls": None, "period": None}
    if "why" in proj:
        out["why"] = proj["why"]
        return out
    s = ctx.snap.get("PCEPILFE")
    if s is None:
        out["why"] = "core PCE: " + ctx.snap.reason("PCEPILFE")
        return out
    base = s.nearest(months_back(s.last_day, s_m), tol=3)
    if base is None:
        out["why"] = f"core PCE: no observation {s_m} months before the latest"
        return out
    pi6 = ((s.last / base) ** (12.0 / s_m) - 1.0) * 100.0
    gap = pi6 - out["proj"]
    out.update(pi6=pi6, gap=gap, cls=1 if gap > band else (-1 if gap < -band else 0),
               period=date_of(s.last_day).isoformat())
    return out


R68_CLASS = {1: "behind", -1: "ahead", 0: "in_line"}


@_guard
def r68_inflation_vs_projection(ctx: Ctx) -> RuleOutput:
    """R-68 (hybrid track, report-only; decision R68-02): behind / ahead when the raw class held at
    ``r68.hold_month_ends`` consecutive month ends (asof and the previous month end, each read point-in-time
    through the Source), else in line. Unknown before the first SEP (2007-11-20)."""
    hold = ctx.p.int("r68.hold_month_ends")
    cur = r68_reading(ctx)
    vals = {"gap": cur["gap"], "core_pce_pi6": cur["pi6"], "projection": cur["proj"], "projection_stat": cur["stat"],
            "sep_published": cur["sep_published"], "core_pce_period": cur["period"],
            "raw_state": None if cur["cls"] is None else R68_CLASS[cur["cls"]]}
    if cur["cls"] is None:
        return unknown("R-68", cur.get("why", "unknown"), variant="hybrid", **vals)
    state = cur["cls"]
    if state != 0:
        readings = [cur]
        c = ctx
        for _ in range(max(hold - 1, 0)):
            c = prev_ctx(c)
            if c is None:
                return unknown("R-68", "previous month end not computable (no source)", variant="hybrid", **vals)
            readings.append(r68_reading(c))
        vals["prev_gap"] = readings[1]["gap"] if len(readings) > 1 else None
        if any(r["cls"] is None for r in readings[1:]) and all(r["cls"] in (None, state) for r in readings[1:]):
            return unknown("R-68", "previous month-end reading unknown (hold)", variant="hybrid", **vals)
        if not all(r["cls"] == state for r in readings):
            state = 0
    vals["state"] = R68_CLASS[state]
    return ok("R-68", variant="hybrid", **vals)
