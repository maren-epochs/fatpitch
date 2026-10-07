"""Fed cycle check (owner decision 2026-10-07, option A; spec/scoring.md section 6d).

A separate required regime check, independent of the documented reads in ``cases/``: does the engine recognise
when the US Fed is actually tightening? The answer key is the Fed's own history (public facts), labelled monthly
1970 -> latest complete month by a pre-registered mechanical rule and written to ``spec/fed_cycles.yaml`` by
``tools/build_fed_cycles.py``. The labels are ex-post facts; the engine side is evaluated point-in-time at each
month end. Holdout-period dates may be used here: the labels are not the sealed documented reads.

Chronology rule (pre-registered):

* Policy-rate events. 1982-09-27 -> 2008-12-15: every change of FRED ``DFEDTAR`` (target rate); 2008-12-16 ->:
  every change of FRED ``DFEDTARU`` (upper bound of the target range). Before 1982-09-27: turning points of monthly
  FRED ``FEDFUNDS`` (``monthly_turning_points``: a peak (trough) is a month whose value is the maximum (minimum)
  of the months within +-6; alternation enforced, keeping the more extreme of two consecutive same-type points;
  adjacent pairs moving less than 1.0 percentage point removed, smallest first); a tightening cycle runs from the
  month after a trough to the next peak, an easing cycle from the month after a peak to the next trough.
* Rate cycles. Consecutive same-sign events form one cycle (first change to last change). A tightening cycle and an
  easing cycle that straddle the 1982-09 splice in the same direction are merged.
* Balance-sheet tightening (QT): 2017-10 -> 2019-07 and 2022-06 -> 2025-11 (Fed announcements cited in the yaml).
* Monthly label (month m, judged by the month of each event): easing if m lies within an easing cycle (first-cut
  month .. last-cut month); else tightening if m lies within a tightening rate cycle or a QT period; else neutral
  (pause). Easing dominates (cuts during QT, 2024-09 -> 2025-11, are easing).
"""

from __future__ import annotations

import datetime as _dt
import itertools
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import yaml

from fatpitch.cases import regime as rg
from fatpitch.dates import last_trading_day

# -------------------------------------------------------------------- pre-registered constants

TP_WINDOW_MONTHS = 6          # pre-1982 turning points: extreme within +-6 months
TP_MIN_MOVE = 1.0             # pre-1982: adjacent turning points at least 1.0 pp apart
MIN_RUN_MOVE = 0.25           # target era: a run of same-sign changes counts as a cycle if |net| >= 0.25 pp
SPLICE_DFEDTAR = _dt.date(1982, 9, 27)
SPLICE_DFEDTARU = _dt.date(2008, 12, 16)
START_MONTH = (1970, 1)
DETECT_BEFORE_MONTHS = 3      # (b) detection window: first-hike month - 3 ..
DETECT_AFTER_MONTHS = 3       #                       .. first-hike month + 3
DETECT_SHARE = 0.75           # (b) detected in >= 75% of tightening rate cycles
FALSE_ALARM_MAX = 0.20        # (c) share of easing months with argmax tightening <= 20%
QT_PERIODS = (((2017, 10), (2019, 7)), ((2022, 6), (2025, 11)))

Month = tuple[int, int]


def month_of(d: _dt.date) -> Month:
    return (d.year, d.month)


def add_months(m: Month, k: int) -> Month:
    i = m[0] * 12 + (m[1] - 1) + k
    return (i // 12, i % 12 + 1)


def months_between(a: Month, b: Month) -> int:
    return (b[0] * 12 + b[1]) - (a[0] * 12 + a[1])


def month_range(a: Month, b: Month) -> list[Month]:
    return [add_months(a, i) for i in range(months_between(a, b) + 1)]


def mstr(m: Month) -> str:
    return f"{m[0]:04d}-{m[1]:02d}"


def mparse(s: str) -> Month:
    y, mo = s.split("-")[:2]
    return (int(y), int(mo))


# -------------------------------------------------------------------- chronology mechanics


def target_events(series: Sequence[tuple[_dt.date, float]], tol: float = 1e-9) -> list[tuple[_dt.date, float]]:
    """(date, change) for every day the target level differs from the previous observation."""
    out = []
    prev = None
    for d, v in sorted(series):
        if v is None:
            continue
        if prev is not None and abs(v - prev) > tol:
            out.append((d, round(v - prev, 6)))
        prev = v
    return out


def monthly_turning_points(monthly: Sequence[tuple[Month, float]], window: int = TP_WINDOW_MONTHS,
                           min_move: float = TP_MIN_MOVE) -> list[tuple[Month, str, float]]:
    """Peaks and troughs of a monthly series (see module docstring): [(month, 'peak'|'trough', value)]."""
    ms = [m for m, _ in monthly]
    v = np.array([x for _, x in monthly], dtype=float)
    pts: list[list] = []
    for i in range(len(v)):
        lo, hi = max(0, i - window), min(len(v), i + window + 1)
        if i - window < 0 or i + window >= len(v):
            continue                       # incomplete window at the edges
        if v[i] == v[lo:hi].max():
            pts.append([ms[i], "peak", float(v[i])])
        elif v[i] == v[lo:hi].min():
            pts.append([ms[i], "trough", float(v[i])])

    def alternate(p):
        out: list[list] = []
        for x in p:
            if out and out[-1][1] == x[1]:
                better = x[2] > out[-1][2] if x[1] == "peak" else x[2] < out[-1][2]
                if better:
                    out[-1] = x
            else:
                out.append(x)
        return out

    pts = alternate(pts)
    while len(pts) >= 2:
        moves = [abs(pts[i + 1][2] - pts[i][2]) for i in range(len(pts) - 1)]
        j = int(np.argmin(moves))
        if moves[j] >= min_move:
            break
        del pts[j:j + 2]
        pts = alternate(pts)
    return [(m, t, x) for m, t, x in pts]


@dataclass
class Cycle:
    direction: str                     # tightening | easing
    start: Month                       # month of the first change
    end: Month                         # month of the last change
    source: str                        # FEDFUNDS turning points | DFEDTAR | DFEDTARU | mixed
    changes: list[dict] = field(default_factory=list)   # [{date, change_pp, level}] (target era)
    level_start: float | None = None
    level_end: float | None = None


def cycles_from_turning_points(tps: Sequence[tuple[Month, str, float]]) -> list[Cycle]:
    out = []
    for (m0, t0, v0), (m1, _t1, v1) in itertools.pairwise(tps):
        direction = "tightening" if t0 == "trough" else "easing"
        out.append(Cycle(direction, add_months(m0, 1), m1, "FEDFUNDS turning points", [], v0, v1))
    return out


def cycles_from_events(events: Sequence[tuple[_dt.date, float, float, str]],
                       min_move: float = MIN_RUN_MOVE) -> list[Cycle]:
    """events: (date, change, new level, source). Consecutive same-sign events form a run; a run whose net move is
    smaller than ``min_move`` (the 1/16-1/8 pp technical adjustments of the 1980s borrowed-reserves era) is dropped,
    and same-direction runs that become adjacent are merged into one cycle (``merge_cycles``)."""
    runs = _runs(events)
    kept = [c for c in runs if abs((c.level_end or 0) - (c.level_start or 0)) >= min_move - 1e-9]
    return merge_cycles(kept)


def _runs(events: Sequence[tuple[_dt.date, float, float, str]]) -> list[Cycle]:
    out: list[Cycle] = []
    for d, ch, lvl, src in events:
        direction = "tightening" if ch > 0 else "easing"
        rec = {"date": d.isoformat(), "change_pp": ch, "level": lvl, "series": src}
        if out and out[-1].direction == direction:
            c = out[-1]
            c.end = month_of(d)
            c.changes.append(rec)
            c.level_end = lvl
            if src not in c.source:
                c.source = f"{c.source}+{src}"
        else:
            out.append(Cycle(direction, month_of(d), month_of(d), src, [rec], round(lvl - ch, 6), lvl))
    return out


def merge_cycles(cycles: Sequence[Cycle]) -> list[Cycle]:
    """Merge adjacent same-direction cycles (the 1982-09 and 2008-12 splices)."""
    out: list[Cycle] = []
    for c in cycles:
        if out and out[-1].direction == c.direction:
            p = out[-1]
            p.end, p.level_end = c.end, c.level_end
            p.changes += c.changes
            p.source = "+".join(dict.fromkeys(p.source.split("+") + c.source.split("+")))
        else:
            out.append(Cycle(c.direction, c.start, c.end, c.source, list(c.changes), c.level_start, c.level_end))
    return out


def build_cycles(fedfunds_monthly: Sequence[tuple[Month, float]], dfedtar: Sequence[tuple[_dt.date, float]],
                 dfedtaru: Sequence[tuple[_dt.date, float]]) -> list[Cycle]:
    pre = [(m, v) for m, v in fedfunds_monthly if m < month_of(SPLICE_DFEDTAR)]
    tps = monthly_turning_points(pre)
    c_pre = cycles_from_turning_points(tps)
    ev = []
    t1 = [(d, v) for d, v in dfedtar if SPLICE_DFEDTAR <= d < SPLICE_DFEDTARU]
    t2 = [(d, v) for d, v in dfedtaru if d >= SPLICE_DFEDTARU]
    lvl = dict(t1 + t2)
    for d, ch in target_events(t1):
        ev.append((d, ch, lvl[d], "DFEDTAR"))
    # DFEDTARU starts 2008-12-16 at 0.25 vs the last DFEDTAR 1.00: that splice step is a cut
    if t1 and t2:
        ev.append((t2[0][0], round(t2[0][1] - t1[-1][1], 6), t2[0][1], "DFEDTARU"))
    for d, ch in target_events(t2):
        ev.append((d, ch, lvl[d], "DFEDTARU"))
    ev.sort()
    return merge_cycles(c_pre + cycles_from_events(ev))


def monthly_labels(cycles: Sequence[Cycle], qt: Sequence[tuple[Month, Month]], start: Month, end: Month) -> dict[Month, str]:
    """Monthly Fed-stance label (module docstring rule)."""
    out = {}
    for m in month_range(start, end):
        if any(c.direction == "easing" and c.start <= m <= c.end for c in cycles):
            out[m] = "easing"
        elif any(c.direction == "tightening" and c.start <= m <= c.end for c in cycles) or \
                any(a <= m <= b for a, b in qt):
            out[m] = "tightening"
        else:
            out[m] = "neutral"
    return out


# -------------------------------------------------------------------- answer key file


@dataclass(frozen=True)
class FedKey:
    labels: dict[Month, str]
    tightening_cycles: list[dict]       # rate cycles: {start, end, ...}
    sha256: str
    rate_cycles: tuple[dict, ...] = ()  # every rate cycle, both directions, key order (scoring.md 6e)


def load_fed_key(path: str | Path) -> FedKey | None:
    import hashlib

    p = Path(path)
    if not p.is_file():
        return None
    raw = p.read_bytes()
    d = yaml.safe_load(raw.decode("utf-8"))
    labels = {mparse(k): v for k, v in (d.get("monthly_labels") or {}).items()}
    tc = [c for c in d.get("rate_cycles") or [] if c.get("direction") == "tightening"]
    return FedKey(labels, tc, hashlib.sha256(raw).hexdigest(), tuple(d.get("rate_cycles") or []))


def month_end_dates(labels: dict[Month, str]) -> dict[Month, _dt.date]:
    """Evaluation date per labelled month: its last NYSE trading day (16:00 ET close)."""
    return {m: last_trading_day(_dt.date(m[0], m[1], 28)) for m in sorted(labels)}


# -------------------------------------------------------------------- the check


def label_blocks(labels: dict[Month, str]) -> dict[Month, int]:
    """Block id per month: maximal runs of identical labels (the 'cycle' unit for LOEO climatology)."""
    out, b, prev = {}, -1, None
    for m in sorted(labels):
        if labels[m] != prev:
            b += 1
            prev = labels[m]
        out[m] = b
    return out


def loeo_cycle_climatology(labels: dict[Month, str], smoothing: float = rg.CLIM_SMOOTHING) -> dict[Month, rg.Probs]:
    """Per month: class frequencies of all labelled months outside its block, add-one smoothed, floored."""
    blocks = label_blocks(labels)
    tot = dict.fromkeys(rg.CLASSES, 0)
    by_block: dict[int, dict[str, int]] = {}
    for m, lab in labels.items():
        tot[lab] += 1
        by_block.setdefault(blocks[m], dict.fromkeys(rg.CLASSES, 0))[lab] += 1
    out = {}
    for m in labels:
        cnt = {k: tot[k] - by_block[blocks[m]][k] for k in rg.CLASSES}
        n = sum(cnt.values())
        out[m] = rg.floor_probs(tuple((cnt[k] + smoothing) / (n + smoothing * len(rg.CLASSES)) for k in rg.CLASSES))
    return out


@dataclass(frozen=True)
class MonthScore:
    month: str
    label: str
    probs: tuple[float, float, float] | None
    argmax: str | None
    rps: float


def call_of(fp: Sequence[float] | None, direction: str | None) -> str | None:
    """The month's call for (b) and (c): the engine's stated direction when it is one of the tied top classes
    (process.md R-66: "policy_direction = argmax P; ties go to the R-14 output"; decision SCORE-01), else the
    argmax. Without a stated direction a tie resolves to the first class, as before."""
    if fp is None:
        return None
    top = max(fp)
    if direction in rg.CLASSES and fp[rg.CLASSES.index(direction)] >= top - 1e-12:
        return direction
    return rg.argmax_class(fp)


def score_months(labels: dict[Month, str], probs_on: Callable[[Month], Sequence[float] | None],
                 direction_on: Callable[[Month], str | None] | None = None) -> list[MonthScore]:
    out = []
    for m in sorted(labels):
        p = probs_on(m)
        fp = None if p is None else rg.floor_probs(p)
        call = call_of(fp, direction_on(m) if direction_on is not None else None)
        out.append(MonthScore(mstr(m), labels[m], fp, call, rg.score_rps(fp, labels[m])))
    return out


def mean_rps(rows: Sequence[MonthScore]) -> float | None:
    return float(np.mean([r.rps for r in rows])) if rows else None


def detection(rows: Sequence[MonthScore], cycles: Sequence[dict]) -> list[dict]:
    """(b) per tightening rate cycle: detected if the argmax is tightening at some month end within
    [first-hike month - 3, first-hike month + 3]; lead/lag = first such month minus the first-hike month
    (negative = before the first hike). A cycle whose window is not fully inside the labelled months (e.g. a cycle
    that began within the last 3 months) is reported with ``evaluated`` False and excluded from the share."""
    am = {mparse(r.month): r.argmax for r in rows}
    out = []
    for c in cycles:
        m0 = mparse(c["start"])
        hits = [k for k in range(-DETECT_BEFORE_MONTHS, DETECT_AFTER_MONTHS + 1)
                if am.get(add_months(m0, k)) == "tightening"]
        out.append({"start": c["start"], "end": c["end"], "detected": bool(hits),
                    "lead_lag_months": hits[0] if hits else None,
                    "evaluated": all(add_months(m0, k) in am for k in range(-DETECT_BEFORE_MONTHS,
                                                                            DETECT_AFTER_MONTHS + 1))})
    return out


def false_alarm_share(rows: Sequence[MonthScore]) -> float | None:
    e = [r for r in rows if r.label == "easing"]
    return (sum(r.argmax == "tightening" for r in e) / len(e)) if e else None


def per_decade(rows: Sequence[MonthScore], refs: dict[str, Sequence[MonthScore]]) -> list[dict]:
    out = []
    decades = sorted({int(r.month[:4]) // 10 * 10 for r in rows})
    for dec in decades:
        sub = [r for r in rows if int(r.month[:4]) // 10 * 10 == dec]
        rm = mean_rps(sub)
        row = {"decade": f"{dec}s", "n_months": len(sub), "rps": rm,
               "labels": {k: sum(r.label == k for r in sub) for k in rg.CLASSES}}
        for n, rr in refs.items():
            rs = mean_rps([r for r in rr if int(r.month[:4]) // 10 * 10 == dec])
            row[f"skill[{n}]"] = rg.skill(rm, rs)
        out.append(row)
    return out


@dataclass
class FedCheckResult:
    passed: bool
    n_months: int
    rps: float | None
    references: dict[str, dict]
    skill_pass: bool
    cycles: list[dict]
    detected_share: float | None
    detection_pass: bool
    false_alarm_share: float | None
    false_alarm_pass: bool
    decades: list[dict]
    label_counts: dict[str, int]
    detected_count: int = 0
    median_lead_months: float | None = None        # median of -lead_lag over detected cycles (> 0 = before hike)
    fed_direction_detected_count: int | None = None
    fed_direction_median_lead_months: float | None = None
    vs_fed_direction_pass: bool = False            # (b')

    def to_dict(self) -> dict:
        return asdict(self)


FED_REFERENCES = ("climatology_cycle_loeo", "null_trend_12m", "null_always_risk_on", "null_fed_direction")
FED_DIRECTION = "null_fed_direction"   # (b') detection benchmark (owner decision 2026-10-07)


def detection_summary(det: Sequence[dict]) -> tuple[int, float | None]:
    """(detected count, median lead in months over detected cycles; lead = -lead_lag, > 0 = before the first hike),
    evaluated cycles only."""
    ev = [d for d in det if d["evaluated"] and d["detected"]]
    return len(ev), (float(np.median([-d["lead_lag_months"] for d in ev])) if ev else None)


def fed_check(rows: Sequence[MonthScore], refs: dict[str, Sequence[MonthScore]], cycles: Sequence[dict]) -> FedCheckResult:
    """Required: (a) mean monthly RPS skill > 0 vs each of LOEO-by-cycle climatology, ``null_trend_12m``,
    ``null_always_risk_on`` and ``null_fed_direction``; (b) detection in >= 75% of tightening rate cycles; (b')
    detected-cycle count >= ``null_fed_direction``'s and median first-hike lead >= its median lead (owner decision
    2026-10-07); (c) false alarms <= 20%. A reference missing from ``refs`` (a reference null scoring itself) makes
    (a) and, for ``null_fed_direction``, (b') not evaluable (False)."""
    rm = mean_rps(rows)
    rr = {n: {"rps": mean_rps(v), "skill": rg.skill(rm, mean_rps(v))} for n, v in refs.items()}
    skill_ok = all(n in rr and rr[n]["skill"] is not None and rr[n]["skill"] > 0 for n in FED_REFERENCES)
    det = detection(rows, cycles)
    ev = [d for d in det if d["evaluated"]]
    share = (sum(d["detected"] for d in ev) / len(ev)) if ev else None
    det_ok = share is not None and share >= DETECT_SHARE
    fa = false_alarm_share(rows)
    fa_ok = fa is not None and fa <= FALSE_ALARM_MAX
    n_det, lead = detection_summary(det)
    fd_n = fd_lead = None
    bp_ok = False
    if FED_DIRECTION in refs:
        fd_n, fd_lead = detection_summary(detection(refs[FED_DIRECTION], cycles))
        bp_ok = n_det >= fd_n and lead is not None and (fd_lead is None or lead >= fd_lead)
    ok = skill_ok and det_ok and bp_ok and fa_ok
    return FedCheckResult(ok, len(rows), rm, rr, skill_ok, det, share, det_ok, fa, fa_ok,
                          per_decade(rows, refs), {k: sum(r.label == k for r in rows) for k in rg.CLASSES},
                          n_det, lead, fd_n, fd_lead, bp_ok)
