"""Timing luck: how much of a result depends on the signal/fill date.

Ported from multi-strategy ``cbp/research/timing_luck.py`` and the helpers it imported from
``cbp/research/signal_timing.py`` (``offset_day``, ``nw_t``, ``stats``, ``monthly_returns``).
Changes: pandas removed (dates are ``datetime.date`` lists, prices and weights numpy arrays); the
CBP universe, asset classes, PR-0017 candidate cell, file outputs and report writer are stripped.
Kept: the NAV path with per-asset contributions and trading cost, placebo rule, day-relative-to-
month-end buckets, NW t-statistic, path statistics, and the two registered timing-luck rules as a
generic ``luck_summary``.

Path (k, j): signal k trading days before month-end T, fill j trading days after the signal,
i.e. fill offset f = -k + j relative to T.
"""

from __future__ import annotations

import bisect
import datetime as _dt
import math
from collections.abc import Callable, Sequence

import numpy as np

TC = 0.0010
ANCHORS = range(16)
LAGS = (1, 2)


def placebo(k: int, j: int, threshold: int = -5) -> bool:
    """Fill at least 5 trading days before month-end (f = -k + j <= -5)."""
    return -k + j <= threshold


def offset_day(days: Sequence[_dt.date], month_end: _dt.date, j: int) -> _dt.date | None:
    """Trading day T+j where T = last trading day on/before ``month_end`` (from ``days``)."""
    pos = bisect.bisect_right(days, month_end) - 1
    k = pos + j
    return days[k] if 0 <= k < len(days) else None


def nav_with_contrib(book_dates: Sequence[_dt.date], weights: np.ndarray, days: Sequence[_dt.date],
                     prices: np.ndarray, f: int, tc: float = TC):
    """Daily NAV of target weights set at each ``book_dates[i]`` and filled at T+f, with drift.

    Returns (days_out, nav, contrib, cost): contrib[t, a] = start-of-day drifted weight x daily
    return (fraction of start-of-day NAV); cost[t] = tc x sum |target - drifted| on fill days.
    """
    days = list(days)
    prices = np.asarray(prices, dtype=float)
    R = np.vstack([np.zeros(prices.shape[1]), prices[1:] / prices[:-1] - 1])
    R = np.nan_to_num(R, nan=0.0)
    fills: dict[_dt.date, np.ndarray] = {}
    for t, w in zip(book_dates, np.asarray(weights, dtype=float), strict=True):
        F = offset_day(days, t, f)
        if F is not None:
            fills[F] = np.nan_to_num(w, nan=0.0)
    if not fills:
        raise ValueError("no fill date falls inside the price index")
    start = min(fills)
    w, nav = None, 1.0
    out_days, navs, contrib, cost = [], [], [], []
    for i, day in enumerate(days):
        if day < start:
            continue
        c = np.zeros(prices.shape[1])
        if w is not None:
            c = w * R[i]
            gross = w * (1 + R[i])
            nav *= 1 + c.sum()
            w = gross / gross.sum() if gross.sum() > 0 else w
        cst = 0.0
        if day in fills:
            tgt = fills[day]
            cst = tc * np.abs(tgt - (w if w is not None else np.zeros_like(tgt))).sum()
            nav *= 1 - cst
            w = tgt.copy()
        out_days.append(day)
        navs.append(nav)
        contrib.append(c)
        cost.append(cst)
    return out_days, np.array(navs), np.array(contrib), np.array(cost)


def monthly_returns(days: Sequence[_dt.date], nav: np.ndarray) -> tuple[list[_dt.date], np.ndarray]:
    """Month-end-to-month-end returns of a daily NAV (last observation in each month)."""
    last: dict[tuple[int, int], tuple[_dt.date, float]] = {}
    for d, v in zip(days, nav, strict=True):
        last[(d.year, d.month)] = (d, float(v))
    ends = [last[k] for k in sorted(last)]
    vals = np.array([v for _, v in ends])
    return [d for d, _ in ends][1:], vals[1:] / vals[:-1] - 1


def day_bucket(days: Sequence[_dt.date]) -> dict[_dt.date, str]:
    """Position of each trading day relative to month-end T: 'T-4..T-2', 'T-1..T', 'T+1..T+3', 'other'."""
    days = sorted(days)
    pos = {d: i for i, d in enumerate(days)}
    last_of_month: dict[tuple[int, int], _dt.date] = {}
    for d in days:
        last_of_month[(d.year, d.month)] = d
    month_ends = sorted(last_of_month.values())
    out = {}
    for d in days:
        to_T = pos[last_of_month[(d.year, d.month)]] - pos[d]
        k = bisect.bisect_left(month_ends, d) - 1
        after = pos[d] - pos[month_ends[k]] if k >= 0 else 99
        if 1 <= after <= 3:
            out[d] = "T+1..T+3"
        elif to_T <= 1:
            out[d] = "T-1..T"
        elif to_T <= 4:
            out[d] = "T-4..T-2"
        else:
            out[d] = "other"
    return out


def nw_t(x) -> float:
    """Newey-West (Bartlett) t-statistic of the mean; NaN when fewer than 10 observations."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 10:
        return float("nan")
    L = math.floor(4 * (n / 100) ** (2 / 9))
    d = x - x.mean()
    v = d @ d / n
    for j in range(1, L + 1):
        v += 2 * (1 - j / (L + 1)) * (d[j:] @ d[:-j]) / n
    return float(x.mean() / math.sqrt(v / n)) if v > 0 else float("nan")


def stats(r, periods_per_year: int = 12) -> dict:
    r = np.asarray(r, dtype=float)
    eq = np.cumprod(1 + r)
    return {"cagr": float(eq[-1] ** (periods_per_year / len(r)) - 1),
            "vol": float(r.std(ddof=1) * math.sqrt(periods_per_year)),
            "sharpe_raw": float(r.mean() / r.std(ddof=1) * math.sqrt(periods_per_year)),
            "max_dd": float((eq / np.maximum.accumulate(eq) - 1).min())}


def luck_summary(paths: dict[tuple[int, int], np.ndarray], baseline: tuple[int, int],
                 candidate: tuple[int, int], is_placebo: Callable[[int, int], bool] = placebo) -> dict:
    """Registered CBP rules on aligned per-period path returns.

    Rule 1: candidate's mean gain over baseline > every placebo path's mean gain.
    Rule 2: candidate minus the equal-weight placebo average has mean > 0 and NW t >= 2.
    """
    base = paths[baseline]
    gain = {key: float(np.mean(r - base) * 1e4) for key, r in paths.items()}
    plac = [key for key in paths if is_placebo(*key)]
    if not plac:
        raise ValueError("no placebo paths")
    tp = np.mean([paths[key] for key in plac], axis=0)
    c_minus_tp = (paths[candidate] - tp) * 1e4
    cagr = {key: stats(r)["cagr"] for key, r in paths.items()}
    rule1 = gain[candidate] > max(gain[key] for key in plac)
    rule2 = bool(c_minus_tp.mean() > 0 and nw_t(c_minus_tp) >= 2)
    return {"spread_cagr_pp": (max(cagr.values()) - min(cagr.values())) * 100,
            "cand_gain_bp": gain[candidate], "placebo_max_gain_bp": max(gain[key] for key in plac),
            "cand_rank": int(sum(v > gain[candidate] for v in gain.values()) + 1), "n_paths": len(paths),
            "n_placebo": len(plac), "cand_minus_placebo_bp": float(c_minus_tp.mean()),
            "cand_minus_placebo_t": nw_t(c_minus_tp), "rule1": bool(rule1), "rule2": rule2,
            "passes": bool(rule1 and rule2)}
