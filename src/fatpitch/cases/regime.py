"""Regime-stage evaluation, option B (owner decision 2026-10-07; spec/scoring.md section 6c).

Gate 1 (regime staging gate, research split) scores the engine's daily as-of regime probabilities with the ranked
probability score (RPS) and compares them, episode first, with three references: leave-one-episode-out (LOEO)
climatology, the 12-month trend null and the constant always-easing null; the engine must beat each. Diagnostics (reported, not gated): bracketed daily path agreement (#8),
turning-point matching on regime changes (#9), Cohen's kappa and balanced accuracy (#5), AUC on P(tightening) (#7).

Pre-registered constants are module-level and copied into spec/scoring.md section 6c.
"""

from __future__ import annotations

import datetime as _dt
import itertools
import math
import re
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from fatpitch.cases.schema import Case, _add_months
from fatpitch.dates import shift_trading_days, trading_days

# -------------------------------------------------------------------- pre-registered constants

CLASSES = ("easing", "neutral", "tightening")    # ordinal order for the RPS
EPS = 0.01                                      # probability floor
NULL_CONFIDENCE = 0.9                           # deterministic null: P(predicted class); rest split equally
CLIM_SMOOTHING = 1.0                            # add-one (Laplace) smoothing of LOEO class counts
ALPHA = 0.10
BRACKET_MAX_MONTHS = 12                         # #8: two agreeing statements at most 12 calendar months apart
MASK_PAD_TRADING_DAYS = 20                      # #8: holdout-episode date ranges padded by the default case window
BOOT_N = 2000                                   # #8: episode-level bootstrap draws
SEED = 20261006
MIN_SPELL_TRADING_DAYS = 63                     # #9: Bry-Boschan minimum spell, 3 months of trading days
TURN_PRE_MONTHS = 12                            # #9: search window starts 12 months before the change interval
TURN_POST_MONTHS = 6                            # #9: and ends 6 months after it
MAX_TRANSITION_MONTHS = 36                      # #9: change intervals longer than 3 years are not matched

Probs = tuple[float, float, float]


# -------------------------------------------------------------------- probabilities


def floor_probs(p: Sequence[float], eps: float = EPS) -> Probs:
    """Normalise to sum 1, then clip-and-rescale: classes below ``eps`` are set to ``eps`` and the remaining
    classes are rescaled proportionally to fill 1 - (#clipped) * eps; repeated until no class is below ``eps``.
    A vector already normalised with every class >= eps is returned unchanged."""
    a = np.asarray(p, dtype=float)
    if a.shape != (3,) or np.any(~np.isfinite(a)) or np.any(a < 0) or a.sum() <= 0:
        raise ValueError(f"invalid probability vector {p!r}")
    a = a / a.sum()
    clipped = np.zeros(3, dtype=bool)
    for _ in range(3):
        low = (a < eps - 1e-15) & ~clipped
        if not low.any():
            break
        clipped |= low
        a[clipped] = eps
        rest = ~clipped
        a[rest] = a[rest] * (1 - eps * clipped.sum()) / a[rest].sum()
    return (float(a[0]), float(a[1]), float(a[2]))


def deterministic_probs(direction: str | None, confidence: float = NULL_CONFIDENCE) -> Probs | None:
    """Deterministic null forecast -> probabilities: ``confidence`` on the predicted class, the rest split
    equally, then floored. None stays None (missing)."""
    if direction is None:
        return None
    k = CLASSES.index(direction)
    rest = (1 - confidence) / (len(CLASSES) - 1)
    return floor_probs(tuple(confidence if i == k else rest for i in range(len(CLASSES))))


def argmax_class(p: Sequence[float] | None) -> str | None:
    if p is None:
        return None
    return CLASSES[int(np.argmax(np.asarray(p)))]


# -------------------------------------------------------------------- RPS


def rps(p: Sequence[float], target: str) -> float:
    """Ranked probability score over the ordered classes, normalised by K - 1 (range 0 best .. 1 worst):
    sum_k (F_k - O_k)^2 / (K - 1) over the first K - 1 cumulative probabilities."""
    k = CLASSES.index(target)
    f = np.cumsum(np.asarray(p, dtype=float))[:-1]
    o = np.array([1.0 if i >= k else 0.0 for i in range(len(CLASSES))])[:-1]
    return float(np.sum((f - o) ** 2) / (len(CLASSES) - 1))


def worst_rps(target: str) -> float:
    """RPS of a missing forecast: the worst attainable RPS for the target (all mass on the farthest class)."""
    k = CLASSES.index(target)
    far = 0 if k >= (len(CLASSES) - 1) / 2 else len(CLASSES) - 1
    p = [0.0] * len(CLASSES)
    p[far] = 1.0
    return rps(p, target)


def score_rps(p: Sequence[float] | None, target: str) -> float:
    """RPS of a floored forecast; a missing forecast (None) scores ``worst_rps``."""
    return worst_rps(target) if p is None else rps(floor_probs(p), target)


# -------------------------------------------------------------------- climatology


def loeo_climatology(cases: Sequence[Case], exclude_episode: str | None, smoothing: float = CLIM_SMOOTHING) -> Probs:
    """Class frequencies of the regime targets of ``cases`` outside ``exclude_episode``, add-``smoothing``
    smoothed, then floored."""
    counts = dict.fromkeys(CLASSES, 0)
    for c in cases:
        t = c.targets.regime_direction
        if t is not None and c.episode_id != exclude_episode:
            counts[t] += 1
    n = sum(counts.values())
    return floor_probs(tuple((counts[k] + smoothing) / (n + smoothing * len(CLASSES)) for k in CLASSES))


# -------------------------------------------------------------------- gate


ERAS = ("A", "B")   # option C (owner decision 2026-10-07): era-B research cases join the Gate 1 set


def regime_cases(cases: Sequence[Case], eras: Sequence[str] = ERAS) -> list[Case]:
    """Gate 1 set: cases with a regime target in ``eras`` (default era A and era B; option C, 2026-10-07)."""
    return [c for c in cases if c.era in eras and c.targets.regime_direction is not None]


@dataclass(frozen=True)
class CaseRPS:
    case_id: str
    episode_id: str
    target: str
    probs: Probs | None
    rps: float
    era: str = ""


def case_rps(cases: Sequence[Case], probs_on: Callable[[Case], Sequence[float] | None]) -> list[CaseRPS]:
    """``probs_on(case)`` returns the forecast at the case asof (or None)."""
    out = []
    for c in cases:
        p = probs_on(c)
        fp = None if p is None else floor_probs(p)
        out.append(CaseRPS(c.id, c.episode_id, c.targets.regime_direction, fp, score_rps(fp, c.targets.regime_direction),
                           c.era))
    return out


def episode_means(rows: Sequence[CaseRPS]) -> dict[str, float]:
    by: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        by[r.episode_id].append(r.rps)
    return {e: float(np.mean(v)) for e, v in sorted(by.items())}


def episode_first(rows: Sequence[CaseRPS]) -> float | None:
    m = episode_means(rows)
    return float(np.mean(list(m.values()))) if m else None


def class_balanced(rows: Sequence[CaseRPS]) -> float | None:
    """Mean over the target classes present of the case-level mean RPS within each class (reported, not gated)."""
    by: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        by[r.target].append(r.rps)
    return float(np.mean([np.mean(v) for v in by.values()])) if by else None


def skill(model: float | None, ref: float | None) -> float | None:
    """1 - RPS_model / RPS_ref (episode-first means); > 0 = better than the reference."""
    if model is None or ref is None or ref == 0:
        return None
    return 1 - model / ref


def exact_sign_flip_p(d: Sequence[float]) -> float:
    """One-sided exact sign-flip p of mean(d) > 0: share of all 2^k sign patterns s with mean(s * d) >= mean(d)
    (1e-12 tolerance). Zero differences (ties) contribute 0 under every pattern."""
    arr = np.asarray(d, dtype=float)
    k = arr.size
    if k == 0:
        raise ValueError("no episode")
    if k > 20:
        raise ValueError(f"exact enumeration limited to 20 episodes (got {k})")
    obs = arr.mean()
    signs = np.array(list(itertools.product((-1.0, 1.0), repeat=k)))
    return float(np.mean((signs * arr).mean(axis=1) >= obs - 1e-12))


def bayes_factor_wins(wins: int, losses: int) -> float:
    """BF10 for theta = P(win) ~ Uniform(0, 1) vs theta = 0.5 on paired wins/losses (ties dropped)."""
    n = wins + losses
    return math.exp(math.lgamma(wins + 1) + math.lgamma(losses + 1) - math.lgamma(n + 2) + n * math.log(2))


@dataclass(frozen=True)
class ReferenceResult:
    name: str
    rps: float | None                        # reference episode-first mean RPS
    skill: float | None                      # 1 - RPS_model / RPS_ref
    p_value: float | None                    # exact one-sided episode sign-flip, model better than reference
    wins: int                                # episodes where the model's mean RPS < the reference's
    losses: int
    ties: int
    bayes_factor: float | None               # reported (holdout form), wins vs losses
    episode_diffs: dict[str, float] = field(default_factory=dict)   # RPS_ref - RPS_model per episode


@dataclass(frozen=True)
class RegimeGateResult:
    passed: bool
    k: int                                   # episodes
    n_cases: int
    rps_model: float | None                  # episode-first mean RPS
    references: dict[str, ReferenceResult]
    binding_reference: str | None            # reference with the largest p (ties: smallest skill)
    binding_p: float | None
    min_attainable_p: float | None           # 1 / 2^k
    every_reference_pass: bool = False
    tightening: dict = field(default_factory=dict)   # hard tightening requirement (2026-10-07), see tightening_check


TIGHTENING_REFERENCE = "null_always_risk_on"
TIGHTENING_MIN_CASES = 3                 # below this the rule still applies; low power is flagged


def tightening_check(model: Sequence[CaseRPS], references: dict[str, Sequence[CaseRPS]],
                     reference: str = TIGHTENING_REFERENCE) -> dict:
    """Hard tightening requirement (owner decision 2026-10-07): on the cases whose target is tightening, the model's
    case-level mean RPS must be lower than ``reference``'s mean RPS on the same cases (skill > 0). No tightening case,
    or no reference rows, = not met. Reports each reference's tightening-subset mean RPS."""
    tm = [r for r in model if r.target == "tightening"]
    ids = {r.case_id for r in tm}
    ref_rps = {}
    for n, rows in references.items():
        sub = [r.rps for r in rows if r.case_id in ids]
        ref_rps[n] = float(np.mean(sub)) if sub else None
    m = float(np.mean([r.rps for r in tm])) if tm else None
    r0 = ref_rps.get(reference)
    sk = skill(m, r0)
    return {"n": len(tm), "k": len({r.episode_id for r in tm}), "eras": sorted({r.era for r in tm}),
            "case_ids": sorted(ids), "rps_model": m, "rps_references": ref_rps, "reference": reference,
            "skill_vs_reference": sk, "passed": sk is not None and sk > 0,
            "low_power": len(tm) < TIGHTENING_MIN_CASES}


def compare_reference(model: Sequence[CaseRPS], ref: Sequence[CaseRPS], name: str) -> ReferenceResult:
    em, er = episode_means(model), episode_means(ref)
    common = sorted(set(em) & set(er))
    d = {e: er[e] - em[e] for e in common}
    vals = list(d.values())
    w = sum(v > 1e-12 for v in vals)
    lo = sum(v < -1e-12 for v in vals)
    rm, rr = episode_first(model), episode_first(ref)
    return ReferenceResult(name, rr, skill(rm, rr), exact_sign_flip_p(vals) if vals else None, w, lo,
                           len(vals) - w - lo, bayes_factor_wins(w, lo), d)


def regime_gate(model: Sequence[CaseRPS], references: dict[str, Sequence[CaseRPS]],
                alpha: float = ALPHA) -> RegimeGateResult:
    """Pass iff (1) for EVERY reference, RPS skill > 0 AND exact one-sided episode sign-flip p < alpha, and (2) the
    hard tightening requirement holds (``tightening_check`` vs ``null_always_risk_on``; when that reference is not
    among ``references``, e.g. a reference null scoring itself, (2) is evaluated against nothing and fails).
    References (spec/scoring.md 6c): LOEO climatology, ``null_trend_12m`` and ``null_always_risk_on``; the binding
    reference is the one with the largest p."""
    res = {n: compare_reference(model, r, n) for n, r in references.items()}
    ok = bool(res) and all(r.skill is not None and r.skill > 0 and r.p_value is not None and r.p_value < alpha
                           for r in res.values())
    bind = max(res.values(), key=lambda r: (1.0 if r.p_value is None else r.p_value,
                                            -(r.skill if r.skill is not None else -1e9)), default=None)
    k = len(episode_means(model))
    tc = tightening_check(model, references)
    return RegimeGateResult(ok and tc["passed"], k, len(model), episode_first(model), res,
                            None if bind is None else bind.name, None if bind is None else bind.p_value,
                            (0.5 ** k) if k else None, ok, tc)


# -------------------------------------------------------------------- #5, #7 classification diagnostics


def kappa_ba(targets: Sequence[str], preds: Sequence[str | None]) -> dict:
    """Cohen's kappa and balanced accuracy (mean recall over target classes present) of argmax predictions; a
    missing prediction is its own wrong class. Chance levels: kappa 0, balanced accuracy 1 / #classes present."""
    n = len(targets)
    if n == 0:
        return {"kappa": None, "balanced_accuracy": None, "kappa_chance": 0.0, "ba_chance": None, "n": 0}
    labels = sorted({*targets, *[p or "none" for p in preds]})
    pr = [p or "none" for p in preds]
    po = sum(t == p for t, p in zip(targets, pr, strict=True)) / n
    pe = sum((targets.count(lab) / n) * (pr.count(lab) / n) for lab in labels)
    kappa = None if pe >= 1 else (po - pe) / (1 - pe)
    present = sorted(set(targets))
    rec = [sum(t == p == c for t, p in zip(targets, pr, strict=True)) / targets.count(c) for c in present]
    return {"kappa": kappa, "balanced_accuracy": float(np.mean(rec)), "kappa_chance": 0.0,
            "ba_chance": 1 / len(present), "n": n, "accuracy": po}


def auc_tightening(targets: Sequence[str], p_tight: Sequence[float | None]) -> dict:
    """AUC of P(tightening) for tightening vs other targets (ties count 1/2); cases without a forecast are
    excluded (n reported). Chance level 0.5. None when either group is empty."""
    pos = [p for t, p in zip(targets, p_tight, strict=True) if p is not None and t == "tightening"]
    neg = [p for t, p in zip(targets, p_tight, strict=True) if p is not None and t != "tightening"]
    if not pos or not neg:
        return {"auc": None, "chance": 0.5, "n_pos": len(pos), "n_neg": len(neg)}
    s = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in pos for b in neg)
    return {"auc": s / (len(pos) * len(neg)), "chance": 0.5, "n_pos": len(pos), "n_neg": len(neg)}


# -------------------------------------------------------------------- holdout masking


_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})_")


def holdout_date_ranges(root: str | Path, pad: int = MASK_PAD_TRADING_DAYS) -> list[tuple[str, _dt.date, _dt.date]]:
    """Date ranges of the sealed holdout episodes, from holdout file NAMES and episode ids only (no target is
    parsed): [first case date - pad, last case date + pad] trading days per episode. Empty when the corpus has
    no ``HOLDOUT.yaml``."""
    from fatpitch.cases.holdout import case_files, episode_of, read_spec

    spec = read_spec(root)
    if spec is None:
        return []
    hold = set(spec["holdout_episodes"])
    by: dict[str, list[_dt.date]] = defaultdict(list)
    for f in case_files(root):
        m = _DATE.match(f.name)
        if not m:
            continue
        ep = episode_of(f)
        if ep in hold:
            by[ep].append(_dt.date.fromisoformat(m.group(1)))
    return [(ep, shift_trading_days(min(ds), -pad), shift_trading_days(max(ds), pad)) for ep, ds in sorted(by.items())]


def masked(d: _dt.date, ranges) -> bool:
    return any(lo <= d <= hi for _, lo, hi in ranges)


# -------------------------------------------------------------------- #8 bracketed daily agreement


def bracketed_labels(cases: Sequence[Case], ranges=(), max_months: int = BRACKET_MAX_MONTHS) -> dict[_dt.date, tuple[str, str]]:
    """Trading day -> (label, episode) for days bracketed by two consecutive regime statements (cases with a
    regime target, era A and B, ordered by asof) that agree and are at most ``max_months`` calendar months apart; endpoints
    included; days inside a holdout-episode range are masked; days with conflicting labels are dropped. The
    episode of a day is the episode of the earlier statement."""
    rc = sorted(regime_cases(cases), key=lambda c: (c.asof, c.id))
    out: dict[_dt.date, tuple[str, str]] = {}
    bad: set[_dt.date] = set()
    for a, b in itertools.pairwise(rc):
        ta, tb = a.targets.regime_direction, b.targets.regime_direction
        if ta != tb or _add_months(a.asof_date, max_months) < b.asof_date:
            continue
        for d in trading_days(a.asof_date, b.asof_date):
            if masked(d, ranges):
                continue
            if d in out and out[d][0] != ta:
                bad.add(d)
            out.setdefault(d, (ta, a.episode_id))
    return {d: v for d, v in sorted(out.items()) if d not in bad}


def path_agreement(labels: dict[_dt.date, tuple[str, str]], direction_on: Callable[[_dt.date], str | None],
                   n_boot: int = BOOT_N, seed: int = SEED) -> dict:
    """Share of bracketed days where the model's daily direction equals the label; chance level from the
    marginals (sum_k share_label_k * share_model_k); 95% CI from an episode-level bootstrap (episodes resampled
    with replacement, days pooled)."""
    if not labels:
        return {"agreement": None, "chance": None, "ci95": None, "n_days": 0, "n_episodes": 0, "n_spells": 0}
    days = sorted(labels)
    lab = [labels[d][0] for d in days]
    ep = [labels[d][1] for d in days]
    pred = [direction_on(d) for d in days]
    hit = np.array([p == t for p, t in zip(pred, lab, strict=True)], dtype=float)
    n = len(days)
    cls = sorted({*lab, *[p or "none" for p in pred]})
    chance = sum((lab.count(c) / n) * ([p or "none" for p in pred].count(c) / n) for c in cls)
    eps_ = sorted(set(ep))
    idx = {e: np.array([i for i, x in enumerate(ep) if x == e]) for e in eps_}
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(len(eps_), size=len(eps_), replace=True)
        sel = np.concatenate([idx[eps_[j]] for j in pick])
        boots.append(hit[sel].mean())
    spells = 1 + sum(1 for i in range(1, n) if lab[i] != lab[i - 1] or ep[i] != ep[i - 1]
                     or (days[i] - days[i - 1]).days > 7)
    return {"agreement": float(hit.mean()), "chance": float(chance),
            "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "n_days": n, "n_episodes": len(eps_), "n_spells": spells,
            "label_counts": {c: lab.count(c) for c in sorted(set(lab))}}


# -------------------------------------------------------------------- #9 turning points


@dataclass(frozen=True)
class Transition:
    from_regime: str
    to_regime: str
    last_old: _dt.date            # last statement of the old view
    first_new: _dt.date           # first statement of the new view
    from_case: str
    to_case: str


def transitions(cases: Sequence[Case], max_months: int | None = MAX_TRANSITION_MONTHS) -> list[Transition]:
    """Regime changes between consecutive regime statements (cases with a regime target, era A and B, ordered by asof):
    rule (a) of section 5a without its 18-month lookback (research gaps between statements are 19-30 months).
    The change date is interval-censored to (last_old, first_new]. Intervals longer than ``max_months`` (None = no
    limit) are dropped: they carry no timing information (e.g. 1981-12-31 -> 2003-12-31, 22 years)."""
    rc = sorted(regime_cases(cases), key=lambda c: (c.asof, c.id))
    out = []
    for a, b in itertools.pairwise(rc):
        if a.targets.regime_direction != b.targets.regime_direction and a.asof_date < b.asof_date and (
                max_months is None or _add_months(a.asof_date, max_months) >= b.asof_date):
            out.append(Transition(a.targets.regime_direction, b.targets.regime_direction, a.asof_date, b.asof_date,
                                  a.id, b.id))
    return out


def transition_window(t: Transition) -> list[_dt.date]:
    return trading_days(_add_months(t.last_old, -TURN_PRE_MONTHS), _add_months(t.first_new, TURN_POST_MONTHS))


def censor_spells(labels: Sequence[str | None], min_len: int = MIN_SPELL_TRADING_DAYS) -> list[tuple[int, int, str | None]]:
    """Bry-Boschan-style minimum spell: runs of equal labels as (start, end_exclusive, label); interior runs
    shorter than ``min_len`` are merged into the preceding run (the shortest first) until none remain. The first
    and last runs (truncated by the window) are kept whatever their length."""
    runs: list[list] = []
    for i, x in enumerate(labels):
        if runs and runs[-1][2] == x:
            runs[-1][1] = i + 1
        else:
            runs.append([i, i + 1, x])
    while True:
        short = [j for j in range(1, len(runs) - 1) if runs[j][1] - runs[j][0] < min_len]
        if not short:
            break
        j = min(short, key=lambda j: (runs[j][1] - runs[j][0], j))
        runs[j - 1][1] = runs[j][1]
        del runs[j]
        if j < len(runs) and runs[j - 1][2] == runs[j][2]:   # merge neighbours that now match
            runs[j - 1][1] = runs[j][1]
            del runs[j]
    return [(a, b, x) for a, b, x in runs]


def match_transition(t: Transition, direction_on: Callable[[_dt.date], str | None],
                     min_len: int = MIN_SPELL_TRADING_DAYS) -> dict:
    """Engine turn for one of his transitions. Over the window [last_old - 12m, first_new + 6m] the engine's daily
    direction is censored to spells >= ``min_len``; turn = first start of a censored spell in ``to_regime``
    preceded by a spell in another label. Position: before (< last_old), inside (last_old .. first_new), after
    (> first_new), missed (no turn). Lead = trading days from the turn to first_new (> 0 = earlier than his first
    new-view statement). Extra turns = other censored label changes in the window."""
    days = transition_window(t)
    lab = [direction_on(d) for d in days]
    spells = censor_spells(lab, min_len)
    turns = [(days[a], x) for (a, _, x), prev in zip(spells[1:], spells[:-1], strict=True) if x != prev[2]]
    hit = next((d for d, x in turns if x == t.to_regime), None)
    if hit is None:
        pos, lead = "missed", None
    else:
        pos = "before" if hit < t.last_old else "inside" if hit <= t.first_new else "after"
        lead = (len(trading_days(hit, t.first_new)) - 1) if hit <= t.first_new else -(len(trading_days(t.first_new, hit)) - 1)
    extra = len(turns) - (1 if hit is not None else 0)
    years = len(days) / 252
    return {"from": t.from_regime, "to": t.to_regime, "last_old": t.last_old.isoformat(),
            "first_new": t.first_new.isoformat(), "turn": None if hit is None else hit.isoformat(), "position": pos,
            "lead_trading_days": lead, "extra_turns": extra, "window_years": round(years, 2),
            "extra_per_year": extra / years if years else None}
