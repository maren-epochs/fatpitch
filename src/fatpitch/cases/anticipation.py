"""Fed anticipation test (spec\\scoring.md section 6e; owner decision 2026-10-07; design source
``spec\\research_market_implied_fed.md`` section 6).

Measures whether a signal points to the coming Fed move before the first move, how early, and at what false-alarm
cost. Answer key: the section 6d Fed cycle key (``spec\\fed_cycles.yaml``, ``fedcycles.load_fed_key``); no case
target is read. The signals (R-67 and the references) are computed point-in-time at month ends and never see the
key.

Constants are fixed by scoring.md 6e and may not change after the first run without a new decision.

Spec readings (scoring.md 6e is explicit on the formulas; the points below are where it is silent):

* Turns: every rate cycle of the key, in key order; first move = the cycle's ``start`` month, last move = its
  ``end`` month. The previous turn's last move is the immediately preceding cycle's ``end``.
* Empty window: when the previous cycle ended in the month before the first move (every pre-1982 turning-point
  cycle, by construction), ``max(first_move - 12, last_move_prev + 1)`` exceeds ``W_end``. The window is then
  ``[W_end, W_end]`` (lead at most 1). Reason: research file 9 expects 1970-1982 turns to be scored at month
  precision; consecutive cycles alternate in direction (``fedcycles.merge_cycles``), so a same-direction
  carry-over, which the window opening exists to block, cannot occur at that month end.
* Target changes for the false-alarm horizon: the months of the key's listed changes (target era); for months
  covered by FEDFUNDS turning-point cycles (before 1982-09), every month of a cycle of direction d counts as a
  d-direction change month (research file 6a: "FEDFUNDS turning points before 1982-09"). Runs dropped by the key's
  0.25 pp minimum-move rule are not changes.
* Evaluated months (false-alarm denominator): month ends with a known signal, inside the key's labelled months,
  whose 6-month horizon lies inside the labelled months. The (m, m + 6] horizon is in months m + 1 .. m + 6.
* Episodes: maximal runs of consecutive month ends with signal d inside the evaluated months; false when no
  d-direction change falls in months (run start, run end + 3]; evaluated when run end + 3 is inside the key.
* Pass rule 2 with ``naive_2y_ff`` lacking hits (median lead None): the lead comparison holds.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import statistics
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from fatpitch.cases.fedcycles import Month, add_months, month_range, months_between, mparse, mstr

# -------------------------------------------------------------------- fixed constants (scoring.md 6e)

WINDOW_MONTHS = 12
FA_HORIZON_MONTHS = 6
EPISODE_AFTER_MONTHS = 3
PASS_HIT_RATE = 0.6
PASS_MIN_LEAD = 1.0
PASS_FA_MAX = 3.0
PASS_FA_VS_NAIVE = 1.0
ERAS = (("1959-1981", (1959, 1), (1981, 12)), ("1982-1993", (1982, 1), (1993, 12)),
        ("1994-2008", (1994, 1), (2008, 12)), ("2009-", (2009, 1), (9999, 12)))
DIRECTIONS = ("tightening", "easing")
SIGNALS = ("R-67", "null_fed_direction", "null_always_risk_on", "naive_2y_ff", "naive_bill_ff", "R-14")
NAIVE = "naive_2y_ff"
TP_SPLICE = (1982, 9)       # fedcycles.SPLICE_DFEDTAR month: FEDFUNDS turning points before it
NAIVE_2Y_BAND_BP = 50.0     # scoring.md 6e: naive_2y_ff beyond +-50 bp
NAIVE_BILL_BAND_BP = 25.0   # scoring.md 6e: naive_bill_ff beyond +-25 bp
START_MONTH = (1959, 12)


def era_of(m: Month) -> str:
    return next(name for name, a, b in ERAS if a <= m <= b)


# -------------------------------------------------------------------- answer key -> turns and change months


@dataclass(frozen=True)
class Turn:
    direction: str
    first_move: Month
    last_move: Month
    prev_last_move: Month | None

    @property
    def w_end(self) -> Month:
        return add_months(self.first_move, -1)

    @property
    def w_start(self) -> Month:
        s = add_months(self.first_move, -WINDOW_MONTHS)
        if self.prev_last_move is not None:
            s = max(s, add_months(self.prev_last_move, 1))
        return min(s, self.w_end)   # empty window -> [W_end, W_end] (module docstring)

    @property
    def era(self) -> str:
        return era_of(self.first_move)


def _m(x) -> Month:
    return mparse(str(x))


def turns_from_cycles(cycles: Sequence[dict]) -> list[Turn]:
    cs = sorted(cycles, key=lambda c: _m(c["start"]))
    out, prev = [], None
    for c in cs:
        out.append(Turn(c["direction"], _m(c["start"]), _m(c["end"]), prev))
        prev = _m(c["end"])
    return out


def change_months(cycles: Sequence[dict]) -> dict[str, set[Month]]:
    out: dict[str, set[Month]] = {d: set() for d in DIRECTIONS}
    for c in cycles:
        d = c["direction"]
        for ch in c.get("changes") or []:
            out[d].add(_m(ch["date"]))
        if "FEDFUNDS" in str(c.get("source", "")):
            end = min(_m(c["end"]), add_months(TP_SPLICE, -1))
            if _m(c["start"]) <= end:
                out[d].update(month_range(_m(c["start"]), end))
    return out


@dataclass(frozen=True)
class AnswerKey:
    turns: list[Turn]
    changes: dict[str, set[Month]]
    first: Month             # first labelled month
    last: Month              # last labelled month
    sha256: str = ""


def answer_key(cycles: Sequence[dict], first: Month, last: Month, sha256: str = "") -> AnswerKey:
    return AnswerKey(turns_from_cycles(cycles), change_months(cycles), first, last, sha256)


def load_answer_key(path: str | Path) -> AnswerKey | None:
    """Answer key from ``spec\\fed_cycles.yaml`` through ``fedcycles.load_fed_key`` (scorer only)."""
    from fatpitch.cases.fedcycles import load_fed_key

    k = load_fed_key(path)
    if k is None or not k.labels:
        return None
    ms = sorted(k.labels)
    return answer_key(k.rate_cycles, ms[0], ms[-1], k.sha256)


# -------------------------------------------------------------------- scorer

Signal = dict[Month, str | None]


@dataclass
class TurnResult:
    direction: str
    first_move: str
    w_start: str
    w_end: str
    era: str
    status: str               # hit | miss | not_evaluable
    signal_at_w_end: str | None
    onset: str | None = None
    lead_months: int | None = None
    reason: str = ""


def score_turn(t: Turn, s: Signal) -> TurnResult:
    base = {"direction": t.direction, "first_move": mstr(t.first_move), "w_start": mstr(t.w_start),
            "w_end": mstr(t.w_end), "era": t.era}
    v = s.get(t.w_end)
    if t.w_end not in s:
        return TurnResult(**base, status="not_evaluable", signal_at_w_end=None, reason="no signal month end at W_end")
    if v is None:
        return TurnResult(**base, status="not_evaluable", signal_at_w_end=None, reason="signal unknown at W_end")
    if v != t.direction:
        return TurnResult(**base, status="miss", signal_at_w_end=v, lead_months=0)
    o = t.w_end
    while add_months(o, -1) >= t.w_start and s.get(add_months(o, -1)) == t.direction:
        o = add_months(o, -1)
    return TurnResult(**base, status="hit", signal_at_w_end=v, onset=mstr(o), lead_months=months_between(o, t.first_move))


def _eval_months(s: Signal, key: AnswerKey) -> list[Month]:
    last_ok = add_months(key.last, -FA_HORIZON_MONTHS)
    return [m for m in sorted(s) if s[m] is not None and key.first <= m <= last_ok]


def false_alarms(s: Signal, key: AnswerKey, d: str) -> dict:
    ev = _eval_months(s, key)
    ch = key.changes[d]
    fa = [m for m in ev if s[m] == d and not any(add_months(m, k) in ch for k in range(1, FA_HORIZON_MONTHS + 1))]
    years = len(ev) / 12.0
    # episodes: maximal runs of consecutive evaluated month ends with signal d
    runs, cur = [], []
    for m in ev:
        if s[m] == d and (cur and add_months(cur[-1], 1) == m):
            cur.append(m)
        elif s[m] == d:
            if cur:
                runs.append(cur)
            cur = [m]
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    n_ep = n_false = 0
    for r in runs:
        end = add_months(r[-1], EPISODE_AFTER_MONTHS)
        if end > key.last:
            continue
        n_ep += 1
        if not any(add_months(r[0], k) in ch for k in range(1, months_between(r[0], end) + 1)):
            n_false += 1
    return {"eval_months": len(ev), "signal_months": sum(s[m] == d for m in ev), "fa_months": len(fa),
            "fa_per_year": (len(fa) / years) if years else None, "episodes": n_ep, "false_episodes": n_false,
            "false_episodes_per_year": (n_false / years) if years else None,
            "fa_month_list": [mstr(m) for m in fa]}


def score_signal(s: Signal, key: AnswerKey) -> dict:
    """Per direction: turns, hit rate, median lead over hits, false alarms, era strata."""
    out: dict = {}
    for d in DIRECTIONS:
        rows = [score_turn(t, s) for t in key.turns if t.direction == d]
        ev = [r for r in rows if r.status != "not_evaluable"]
        hits = [r for r in ev if r.status == "hit"]
        eras = {}
        for name, _a, _b in ERAS:
            e = [r for r in ev if r.era == name]
            h = sum(r.status == "hit" for r in e)
            eras[name] = {"evaluable": len(e), "hits": h, "hit_rate": (h / len(e)) if e else None,
                          "not_evaluable": sum(r.era == name and r.status == "not_evaluable" for r in rows)}
        out[d] = {"turns": len(rows), "evaluable": len(ev), "not_evaluable": len(rows) - len(ev),
                  "hits": len(hits), "hit_rate": (len(hits) / len(ev)) if ev else None,
                  "median_lead": float(statistics.median([r.lead_months for r in hits])) if hits else None,
                  **false_alarms(s, key, d), "eras": eras, "rows": [asdict(r) for r in rows]}
    return out


def pass_rule(res: dict, naive: dict | None) -> dict:
    """scoring.md 6e pass rule, per direction (all four must hold). A criterion that cannot be computed is False."""
    out = {}
    for d in DIRECTIONS:
        r = res[d]
        h, lead, fa = r["hit_rate"], r["median_lead"], r["fa_per_year"]
        c1 = h is not None and lead is not None and h >= PASS_HIT_RATE and lead >= PASS_MIN_LEAD
        if naive is None:
            c2 = False
        else:
            n = naive[d]
            c2 = (h is not None and n["hit_rate"] is not None and h >= n["hit_rate"]
                  and lead is not None and (n["median_lead"] is None or lead >= n["median_lead"])
                  and fa is not None and n["fa_per_year"] is not None and fa <= n["fa_per_year"] + PASS_FA_VS_NAIVE)
        c3 = fa is not None and fa <= PASS_FA_MAX
        c4 = all(e["hit_rate"] != 0 for e in r["eras"].values() if e["evaluable"])
        out[d] = {"1": bool(c1), "2": bool(c2), "3": bool(c3), "4": bool(c4), "pass": bool(c1 and c2 and c3 and c4)}
    out["pass"] = all(out[d]["pass"] for d in DIRECTIONS)
    return out


def score_all(signals: dict[str, Signal], key: AnswerKey, subject: str = "R-67") -> dict:
    res = {n: score_signal(s, key) for n, s in signals.items()}
    return {"results": res, "pass": pass_rule(res[subject], res.get(NAIVE)) if subject in res else None}


# -------------------------------------------------------------------- reference signals (point-in-time)


def _cls_bp(x: float | None, band: float) -> str | None:
    if x is None or not np.isfinite(x):
        return None
    return "tightening" if x > band else ("easing" if x < -band else "neutral")


def _ff_now(ctx) -> float | None:
    """FF for the naive references: DFF (daily, as the market legs), FEDFUNDS when DFF is unavailable
    (process.md section 0: FF = FEDFUNDS monthly or DFF daily)."""
    s = ctx.snap.get("DFF") or ctx.snap.get("FEDFUNDS")
    return None if s is None else s.last


def naive_2y_ff(ctx) -> tuple[str | None, float | None]:
    """sign of DGS2 - FF beyond +-50 bp; DGS1 - FF before DGS2 exists (1976-06); no smoothing (scoring.md 6e)."""
    y = ctx.snap.get("DGS2") or ctx.snap.get("DGS1")
    ff = _ff_now(ctx)
    if y is None or ff is None:
        return None, None
    bp = (y.last - ff) * 100.0
    return _cls_bp(bp, NAIVE_2Y_BAND_BP), bp


def naive_bill_ff(ctx) -> tuple[str | None, float | None]:
    """DTB6 - DFF beyond +-25 bp (no bond-equivalent conversion; scoring.md 6e)."""
    b, ff = ctx.snap.get("DTB6"), ctx.snap.get("DFF")
    if b is None or ff is None:
        return None, None
    bp = (b.last - ff.last) * 100.0
    return _cls_bp(bp, NAIVE_BILL_BAND_BP), bp


class _Frames:
    """Adapter: a precomputed snapshot as a Source for the nulls (one snapshot per month end)."""

    def __init__(self, frames: dict):
        self.frames = frames

    def snapshot(self, asof):
        return self.frames


R67_FIELDS = ("component", "m2_bp", "m2_class", "m2_series", "mb_bp", "mb_class", "i4_i", "i4_pi6", "i4_class",
              "i4_prev_class", "i4_known", *(f"{m}_{k}" for m in ("cpi", "core_cpi", "pce", "core_pce")
                                             for k in ("series", "status", "i", "pi6", "pi12", "w")),
              "gr", "gr_prev", "gr_r10", "gr_r15_down", "gr_credit_wider", "gr_r08", "dff")
R68_FIELDS = ("r68_state", "r68_raw_state", "r68_gap", "r68_core_pce_pi6", "r68_projection", "r68_projection_stat",
              "r68_sep_published", "r68_reason")


def month_end_signals(asof: _dt.datetime, frames: dict, reg, source=None) -> dict:
    """R-67 (v2, every leg and the deciding component), R-68 (report-only), and every reference at one month
    end, from one point-in-time snapshot."""
    from fatpitch.cases.nulls import FedDirectionOnly
    from fatpitch.rules import step1
    from fatpitch.rules.anticipation import (
        anticipated_turn,
        r67_anticipated_turn,
        r68_inflation_vs_projection,
    )
    from fatpitch.rules.outputs import Params
    from fatpitch.rules.series import Snap

    ctx = step1.Ctx(asof, Snap(frames, asof), Params(reg), source)
    r67 = r67_anticipated_turn(ctx)
    r68 = r68_inflation_vs_projection(ctx)
    r14 = step1.r14_policy_direction(ctx)
    n2, n2bp = naive_2y_ff(ctx)
    nb, nbbp = naive_bill_ff(ctx)
    fd = FedDirectionOnly().predict(asof, _Frames(frames)).regime_direction
    v, v68 = r67.values, r68.values
    row = {"asof": asof.isoformat(), "R-67": r67.get("direction"), **{k: v.get(k) for k in R67_FIELDS},
           "onset_date": r67.get("onset_date"), "lead_age_m": r67.get("lead_age_m"), "r67_reason": r67.reason,
           "R-14": r14.get("direction"), "anticipated_turn": anticipated_turn(r67, r14.get("direction")),
           "null_fed_direction": fd, "null_always_risk_on": "easing", "naive_2y_ff": n2, "naive_2y_bp": n2bp,
           "naive_bill_ff": nb, "naive_bill_bp": nbbp,
           "r68_state": r68.get("state"), "r68_raw_state": v68.get("raw_state"), "r68_gap": v68.get("gap"),
           "r68_core_pce_pi6": v68.get("core_pce_pi6"), "r68_projection": v68.get("projection"),
           "r68_projection_stat": v68.get("projection_stat"), "r68_sep_published": v68.get("sep_published"),
           "r68_reason": r68.reason}
    if not r67.ok:
        row["component"] = None
    return row


# -------------------------------------------------------------------- real-lake run (CLI)

SNAPSHOT_SERIES = ("DTB3", "DTB6", "DFF", "CPILFESL", "CPILFENS", "CPIAUCSL", "CPIAUCNS", "PCEPI", "PCEPILFE",
                   "DGS2", "DGS1", "FEDFUNDS", "DFEDTARU", "FOMC_BS_STATE", "DGS10", "DCOILWTICO", "USD_BROAD",
                   "ETF_SPY", "ETF_XHB", "ETF_IYT", "ETF_XTN", "ETF_XRT", "ETF_KBE", "ETF_IWM", "ETF_XME", "ETF_SMH",
                   "BAA", "GS10", "BAMLH0A0HYM2", "TB3MS", "SEP_CORE_PCE_MEDIAN", "SEP_CORE_PCE_CT_LOW",
                   "SEP_CORE_PCE_CT_HIGH")


def eval_months(start: Month, today: _dt.date) -> list[Month]:
    from fatpitch.dates import last_trading_day

    out, m = [], start
    while last_trading_day(_dt.date(m[0], m[1], 1)) <= today:
        out.append(m)
        m = add_months(m, 1)
    if out and last_trading_day(_dt.date(*out[-1], 1)) == today:
        out.pop()   # today's close may not have passed; the month is complete only after it
    return out


def stream_signals(source, months: Iterable[Month], reg) -> Iterator[tuple[Month, dict]]:
    """One snapshot per month end (16:00 ET, last NYSE trading day), released after use."""
    from fatpitch.dates import et_close, last_trading_day

    ids = [s for s in SNAPSHOT_SERIES if s in getattr(source, "entries", {s: None for s in SNAPSHOT_SERIES})]
    for m in months:
        asof = et_close(last_trading_day(_dt.date(m[0], m[1], 1)))
        try:
            frames = source.snapshot(asof, series=ids)
        except TypeError:
            frames = source.snapshot(asof)
        yield m, month_end_signals(asof, frames, reg, source)
        del frames


def _fmt(x, nd=2) -> str:
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def pass_table(scored: dict) -> str:
    res, ps = scored["results"], scored["pass"]
    lines = [("| Direction | Hit rate (hits/evaluable) | Median lead (m) | FA months/yr | FA episodes/yr | "
              "naive_2y_ff hit / lead / FA | Era hits (hits/evaluable) | Not evaluable | 1 | 2 | 3 | 4 | Result |"),
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for d in DIRECTIONS:
        r, n, p = res["R-67"][d], res[NAIVE][d], ps[d]
        eras = "; ".join(f"{k} {e['hits']}/{e['evaluable']}" for k, e in r["eras"].items())
        lines.append(f"| {d} | {_fmt(r['hit_rate'])} ({r['hits']}/{r['evaluable']}) | {_fmt(r['median_lead'], 1)} | "
                     f"{_fmt(r['fa_per_year'])} | {_fmt(r['false_episodes_per_year'])} | "
                     f"{_fmt(n['hit_rate'])} / {_fmt(n['median_lead'], 1)} / {_fmt(n['fa_per_year'])} | {eras} | "
                     f"{r['not_evaluable']} | {'P' if p['1'] else 'F'} | {'P' if p['2'] else 'F'} | "
                     f"{'P' if p['3'] else 'F'} | {'P' if p['4'] else 'F'} | {'PASS' if p['pass'] else 'FAIL'} |")
    lines.append(f"\nOverall: {'PASS' if ps['pass'] else 'FAIL'} (all four criteria, both directions)")
    return "\n".join(lines)


def reference_table(scored: dict) -> str:
    lines = [("| Signal | Direction | Hit rate (hits/evaluable) | Median lead | FA months/yr | False episodes/yr | "
              "Not evaluable |"), "|---|---|---|---|---|---|---|"]
    for n, res in scored["results"].items():
        for d in DIRECTIONS:
            r = res[d]
            lines.append(f"| {n} | {d} | {_fmt(r['hit_rate'])} ({r['hits']}/{r['evaluable']}) | "
                         f"{_fmt(r['median_lead'], 1)} | {_fmt(r['fa_per_year'])} | "
                         f"{_fmt(r['false_episodes_per_year'])} | {r['not_evaluable']} |")
    return "\n".join(lines)


def _num(x) -> float | None:
    if x is None or x == "":
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if np.isfinite(v) else None


def supplementary_md(rows: dict[str, dict], scored: dict, target: float) -> str:
    """Report blocks required by research_R67_v2_R68.md section 5 step 6 and decision R67-05: the component that
    decided R-67 at each scored turn, components over all month ends, known I4 measures per era (C4 check), the
    CPI-PCE bias block (section 2a, items i and ii), and R-68 (hybrid, report-only). ``rows``: 'YYYY-MM' -> row."""
    out = ["## R-67 component that decided", "", "| Direction | Component at W_end | Hits | Misses |",
           "|---|---|---|---|"]
    tally: dict[tuple, list[int]] = {}
    for d in DIRECTIONS:
        for r in scored["results"]["R-67"][d]["rows"]:
            if r["status"] == "not_evaluable":
                continue
            c = (rows.get(r["w_end"]) or {}).get("component") or "-"
            t = tally.setdefault((d, c), [0, 0])
            t[0 if r["status"] == "hit" else 1] += 1
    out += [f"| {d} | {c} | {h} | {m} |" for (d, c), (h, m) in sorted(tally.items())]
    comp: dict[str, int] = {}
    for r in rows.values():
        k = r.get("component") or "unknown"
        comp[k] = comp.get(k, 0) + 1
    out += ["", "Month ends by deciding component: " + "; ".join(f"{k} {v}" for k, v in sorted(comp.items())), ""]
    out += ["## I4 known measures per era (C4)", "", "| Era | 0 | 1 | 2 | 3 | 4 | I4 absent | I4 unknown |",
            "|---|---|---|---|---|---|---|---|"]
    for name, a, b in ERAS:
        rs = [r for m, r in rows.items() if a <= mparse(m) <= b]
        if not rs:
            continue
        cnt = [sum(int(_num(r.get("i4_known")) or 0) == k for r in rs) for k in range(5)]
        ab = sum(r.get("i4_class") == "absent" for r in rs)
        un = sum(r.get("i4_class") in (None, "") for r in rs)
        out.append(f"| {name} | " + " | ".join(str(c) for c in cnt) + f" | {ab} | {un} |")
    out += ["", "## CPI-PCE bias (research section 2a; reported, not gated)", ""]
    for cpi, pce in (("cpi", "pce"), ("core_cpi", "core_pce")):
        lines = {}
        for h in ("pi6", "pi12"):
            w = [_num(r.get(f"{cpi}_{h}")) - _num(r.get(f"{pce}_{h}")) for r in rows.values()
                 if _num(r.get(f"{cpi}_{h}")) is not None and _num(r.get(f"{pce}_{h}")) is not None]
            lines[h] = (f"{statistics.fmean(w):.2f}" if w else "-", len(w))
        out.append(f"- {cpi} - {pce}: mean wedge on pi6 {lines['pi6'][0]} pp, on pi12 {lines['pi12'][0]} pp "
                   f"({lines['pi6'][1]} month ends)")
    both = 0
    for r in rows.values():
        v = [_num(r.get(f"{m}_pi6")) for m in ("cpi", "core_cpi", "pce", "core_pce")]
        if all(x is not None for x in v) and v[0] > target and v[1] > target and v[2] <= target and v[3] <= target:
            both += 1
    out += [f"- month ends where both CPI measures have pi6 > {target:g} and both PCE measures do not: {both}",
            "- item iii (I4 class with a PCE-consistent condition for the CPI measures): not computed (gap)", ""]
    out += ["## R-68 inflation vs the Fed's projection (hybrid, report-only; decision R68-02)", ""]
    st: dict[str, int] = {}
    for r in rows.values():
        k = r.get("r68_state") or "unknown"
        st[k] = st.get(k, 0) + 1
    out.append("Month ends by state: " + "; ".join(f"{k} {v}" for k, v in sorted(st.items())))
    runs: list[list[str]] = []
    cur: list[str] | None = None
    for m in sorted(rows):
        k = rows[m].get("r68_state")
        if k in ("behind", "ahead"):
            if cur and cur[0] == k and add_months(mparse(cur[2]), 1) == mparse(m):
                cur[2] = m
            else:
                cur = [k, m, m]
                runs.append(cur)
        else:
            cur = None
    if runs:
        out += ["", "| State | From | To |", "|---|---|---|"] + [f"| {k} | {a} | {b} |" for k, a, b in runs]
    return "\n".join(out) + "\n"


def report_md(scored: dict, meta: dict, components: dict[str, str | None], extra: str = "") -> str:
    out = ["# Fed anticipation test (scoring.md 6e): R-67 hybrid track", "",
           ("Process model output, hybrid track; not any person's view; not affiliated or endorsed. R-67 is a warning "
            "flag only until this test passes (no effect on the regime vector, Gate 1 or 6d)."), ""]
    out += [f"- {k}: {v}" for k, v in meta.items()]
    out += ["", "## Pass table (R-67)", "", pass_table(scored), "", "## All signals", "", reference_table(scored), "",
            "## R-67 per turn", "", ("| Turn | Direction | Era | Window | s(W_end) | Status | Onset | Lead | "
                                     "Component at W_end | Reason |"), "|---|---|---|---|---|---|---|---|---|---|"]
    rows = sorted(scored["results"]["R-67"]["tightening"]["rows"] + scored["results"]["R-67"]["easing"]["rows"],
                  key=lambda r: r["first_move"])
    for r in rows:
        out.append(f"| {r['first_move']} | {r['direction']} | {r['era']} | {r['w_start']}..{r['w_end']} | "
                   f"{_fmt(r['signal_at_w_end'])} | {r['status']} | {_fmt(r['onset'])} | {_fmt(r['lead_months'])} | "
                   f"{_fmt(components.get(r['w_end']))} | {r['reason'] or '-'} |")
    if extra:
        out += ["", extra]
    out += ["", "Not reported (gap): the supplementary daily variant (1994 onward, research file 6b)."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    from fatpitch import registry as _registry
    from fatpitch.dates import today
    from fatpitch.lake import AmberLakeSource, load_catalogue
    from fatpitch.versions import gitops, trials

    ap = argparse.ArgumentParser(prog="python -m fatpitch.cases.anticipation",
                                 description="Fed anticipation test (spec/scoring.md 6e) for R-67 on the amber lake")
    ap.add_argument("--out", help="output parent directory (default results\\anticipation)")
    ap.add_argument("--amber-data", help="amber data root (default AMBER_DATA or the amber default)")
    ap.add_argument("--no-trial", action="store_true", help="do not append to results\\versions\\trials.jsonl")
    a = ap.parse_args(argv)

    root = _registry.project_root()
    key = load_answer_key(root / "spec" / "fed_cycles.yaml")
    if key is None:
        print("answer key spec/fed_cycles.yaml missing or empty", file=sys.stderr)
        return 2
    reg = _registry.load_default()
    cat = load_catalogue()
    ids = [s for s in SNAPSHOT_SERIES if s in cat["series"]]
    src = AmberLakeSource(root=a.amber_data, series=ids, catalogue=cat)
    started = _dt.datetime.now(_dt.UTC)
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(a.out) if a.out else root / "results" / "anticipation"
    out_dir = out_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=False)

    months = eval_months(START_MONTH, today())
    signals: dict[str, Signal] = {n: {} for n in SIGNALS}
    comp: dict[str, str | None] = {}
    fields = ["month", "asof", *SIGNALS, *R67_FIELDS, "onset_date", "lead_age_m", "anticipated_turn",
              "naive_2y_bp", "naive_bill_bp", "r67_reason", *R68_FIELDS]
    kept: dict[str, dict] = {}
    with (out_dir / "monthly.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for m, row in stream_signals(src, months, reg):
            for n in SIGNALS:
                signals[n][m] = row[n]
            comp[mstr(m)] = row["component"]
            kept[mstr(m)] = {k: row.get(k) for k in R67_FIELDS + R68_FIELDS}
            w.writerow({"month": mstr(m), **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}})
    scored = score_all(signals, key)
    with (out_dir / "turns.csv").open("w", encoding="utf-8", newline="") as fh:
        tf = ["signal", "direction", "first_move", "w_start", "w_end", "era", "status", "signal_at_w_end", "onset",
              "lead_months", "reason"]
        w = csv.DictWriter(fh, fieldnames=tf)
        w.writeheader()
        for n, res in scored["results"].items():
            for d in DIRECTIONS:
                for r in res[d]["rows"]:
                    w.writerow({"signal": n, **r})
    commit = gitops.head(root)
    dirty = bool(gitops.dirty_paths(root, ["src", "spec"]))
    meta = {"run_id": run_id, "months": f"{mstr(months[0])}..{mstr(months[-1])} ({len(months)} month ends)",
            "answer_key_sha256": key.sha256, "answer_key_months": f"{mstr(key.first)}..{mstr(key.last)}",
            "registry_sha": reg.sha256, "commit": commit, "uncommitted_src_spec": dirty}
    meta["design"] = "R-67 v2 V2-B (decisions R67-05, INFL-04, R67-06); R-68 hybrid report-only (R68-02)"
    extra = supplementary_md(kept, scored, float(reg["policy.taylor_pi_target_pct"].value))
    (out_dir / "report.md").write_text(report_md(scored, meta, comp, extra), encoding="utf-8", newline="\n")
    slim = {n: {d: {k: v for k, v in r[d].items() if k not in ("rows", "fa_month_list")} for d in DIRECTIONS}
            for n, r in scored["results"].items()}
    (out_dir / "scores.json").write_text(json.dumps({"meta": meta, "pass": scored["pass"], "results": slim},
                                                    indent=1, default=str), encoding="utf-8", newline="\n")
    if not a.no_trial:
        r67 = scored["results"]["R-67"]
        summary = {"anticipation_pass": scored["pass"]["pass"]}
        for d in DIRECTIONS:
            summary.update({f"{d}_hit_rate": r67[d]["hit_rate"], f"{d}_median_lead": r67[d]["median_lead"],
                            f"{d}_fa_per_year": r67[d]["fa_per_year"], f"{d}_not_evaluable": r67[d]["not_evaluable"],
                            f"{d}_pass": scored["pass"][d]["pass"]})
        trials.append(root / "results" / "versions" / "trials.jsonl",
                      {"kind": "anticipation", "label": "R-67", "design": "v2 V2-B", "run_id": run_id,
                       "commit": commit,
                       "wip_fingerprint": gitops.wip_fingerprint(root) if dirty else None,
                       "registry_sha": reg.sha256, "answer_key_sha256": key.sha256,
                       "path": str(out_dir.relative_to(root)) if out_dir.is_relative_to(root) else str(out_dir),
                       "summary": summary})
    print(pass_table(scored))
    print()
    print(reference_table(scored))
    print(f"\nwritten: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
