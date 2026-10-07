"""Case scoring (PLAN E.4): engines, per-case scores, episode-first aggregation, permutation test.

Per case (``ScoringRule`` defaults; the rule object is what gets pre-registered):

    regime      1 if the prediction at asof matches; ``regime_window`` (0.5) if it matches on any
                trading day in the window; else 0
    thesis      fraction of target theses matched (class + direction, + region when the target
                names one) by a predicted thesis on any trading day in the window
    expression  1 if any target family is in the top-k (3) predicted families on any window day
    action      1 if the predicted action equals the target action on any window day
    tilt        13F cases: fraction of target families whose predicted QoQ change sign at asof equals
                the target sign (a family absent from the prediction counts as 0 = no change)

A component with no target is ``None`` and excluded. Aggregation: mean per episode first, then the
mean across episodes. Breakdowns by era, source_reliability, truth_type, mechanizable and turning_point (derived on
the full corpus, ``schema.turning_point_ids``) use the same two-level aggregation inside each subset.

Engines see only ``asof`` and a ``Source``; they never see a case or its targets.
"""

from __future__ import annotations

import datetime as _dt
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np

from fatpitch.cases.schema import Case, Corpus, ThesisTarget, turning_point_ids
from fatpitch.dates import et_close

COMPONENTS = ("regime", "thesis", "expression", "action", "tilt")
BREAKDOWNS = ("era", "source_reliability", "truth_type", "mechanizable", "turning_point")


@dataclass(frozen=True)
class Prediction:
    regime_direction: str | None = None
    theses: tuple[ThesisTarget, ...] = ()
    expressions: tuple[str, ...] = ()        # ranked families, best first
    action: str | None = None
    tilts: tuple[tuple[str, int], ...] = ()  # 13F: (family, -1 | 0 | +1) predicted QoQ change sign
    regime_probs: tuple[float, float, float] | None = None  # P(easing, neutral, tightening); None = missing


@runtime_checkable
class Engine(Protocol):
    name: str

    def predict(self, asof: _dt.datetime, source) -> Prediction: ...


@dataclass(frozen=True)
class ScoringRule:
    regime_exact: float = 1.0
    regime_window: float = 0.5
    expression_top_k: int = 3


DEFAULT_RULE = ScoringRule()


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    episode_id: str
    regime: float | None
    thesis: float | None
    expression: float | None
    action: float | None
    tilt: float | None = None

    def get(self, component: str) -> float | None:
        return getattr(self, component)


PredictFn = Callable[[_dt.date], Prediction]


def score_case(case: Case, predict_on: PredictFn, rule: ScoringRule = DEFAULT_RULE,
               center: _dt.date | None = None) -> CaseScore:
    """Score one case. ``predict_on(date)`` returns the engine prediction at that date's ET close.
    ``center`` re-centres the case on another date (permutation test)."""
    t = case.targets
    center = center or case.asof_date
    days = case.window.dates(center)
    preds = [predict_on(d) for d in days]
    at = predict_on(center)

    regime = None
    if t.regime_direction is not None:
        if at.regime_direction == t.regime_direction:
            regime = rule.regime_exact
        elif any(p.regime_direction == t.regime_direction for p in preds):
            regime = rule.regime_window
        else:
            regime = 0.0

    thesis = None
    if t.theses:
        hit = [any(tt.matches(pt) for p in preds for pt in p.theses) for tt in t.theses]
        thesis = sum(hit) / len(hit)

    expression = None
    if t.expression:
        want = set(t.expression)
        expression = float(any(want & set(p.expressions[: rule.expression_top_k]) for p in preds))

    action = None
    if t.action is not None:
        action = float(any(p.action == t.action for p in preds))

    tilt = None
    if t.tilt:
        pred = dict(at.tilts)
        tilt = sum(pred.get(f, 0) == sgn for f, sgn in t.tilt) / len(t.tilt)

    return CaseScore(case.id, case.episode_id, regime, thesis, expression, action, tilt)


# -------------------------------------------------------------------- aggregation


def _two_level(scores: Sequence[CaseScore], component: str) -> float | None:
    by_ep: dict[str, list[float]] = defaultdict(list)
    for s in scores:
        v = s.get(component)
        if v is not None:
            by_ep[s.episode_id].append(v)
    if not by_ep:
        return None
    return float(np.mean([np.mean(v) for v in by_ep.values()]))


def aggregate(scores: Sequence[CaseScore]) -> dict[str, float | None]:
    return {c: _two_level(scores, c) for c in COMPONENTS}


@dataclass
class Result:
    engine: str
    case_scores: list[CaseScore]
    overall: dict[str, float | None]
    breakdown: dict[str, dict[str, dict[str, float | None]]] = field(default_factory=dict)
    n_cases: int = 0
    n_episodes: int = 0


def breakdown(cases: Sequence[Case], scores: Sequence[CaseScore], turning: frozenset[str] | None = None) -> dict:
    by_id = {s.case_id: s for s in scores}
    turning = turning_point_ids(cases) if turning is None else turning
    out: dict[str, dict[str, dict[str, float | None]]] = {}
    for dim in BREAKDOWNS:
        groups: dict[str, list[CaseScore]] = defaultdict(list)
        for c in cases:
            key = (c.id in turning) if dim == "turning_point" else getattr(c, dim)
            key = ("yes" if key else "no") if isinstance(key, bool) else str(key)
            groups[key].append(by_id[c.id])
        out[dim] = {k: aggregate(v) for k, v in sorted(groups.items())}
    return out


class PredictionCache:
    """Memoises ``engine.predict`` by date (each date evaluated at its 16:00 ET close)."""

    def __init__(self, engine: Engine, source):
        self.engine, self.source = engine, source
        self._cache: dict[_dt.date, Prediction] = {}

    def __call__(self, d: _dt.date) -> Prediction:
        if d not in self._cache:
            self._cache[d] = self.engine.predict(et_close(d), self.source)
        return self._cache[d]


def run(engine: Engine, corpus: Corpus | Sequence[Case], source=None,
        rule: ScoringRule = DEFAULT_RULE, cache: PredictionCache | None = None) -> Result:
    cases = list(corpus.cases if isinstance(corpus, Corpus) else corpus)
    turning = corpus.turning if isinstance(corpus, Corpus) else None
    cache = cache or PredictionCache(engine, source)
    scores = [score_case(c, cache, rule) for c in cases]
    return Result(engine=engine.name, case_scores=scores, overall=aggregate(scores),
                  breakdown=breakdown(cases, scores, turning), n_cases=len(cases),
                  n_episodes=len({c.episode_id for c in cases}))


# -------------------------------------------------------------------- permutation test


@dataclass(frozen=True)
class PermutationResult:
    component: str
    observed: float
    null: np.ndarray
    p_value: float


def permutation_test(engine: Engine, corpus: Corpus | Sequence[Case], source=None, component: str = "regime",
                     n_perm: int = 1000, seed: int = 20261006, rule: ScoringRule = DEFAULT_RULE,
                     cache: PredictionCache | None = None) -> PermutationResult:
    """Shuffle case dates across cases (targets fixed, windows re-centred) and recompute the
    episode-first aggregate of ``component``. p = (1 + #{null >= observed}) / (1 + n_perm)."""
    if component not in COMPONENTS:
        raise ValueError(f"component {component!r} not in {COMPONENTS}")
    cases = list(corpus.cases if isinstance(corpus, Corpus) else corpus)
    cache = cache or PredictionCache(engine, source)
    dates = [c.asof_date for c in cases]

    def stat(centers) -> float:
        v = _two_level([score_case(c, cache, rule, d) for c, d in zip(cases, centers, strict=True)], component)
        return float("nan") if v is None else v

    observed = stat(dates)
    rng = np.random.default_rng(seed)
    null = np.array([stat(list(rng.permutation(np.array(dates, dtype=object)))) for _ in range(n_perm)])
    p = (1 + int(np.sum(null >= observed - 1e-12))) / (1 + n_perm)
    return PermutationResult(component, observed, null, p)


def margin_over_best_null(result: Result, nulls: Sequence[Result], component: str) -> float | None:
    """Engine minus the best null on ``component`` (in score units; 0.15 = 15 points)."""
    e = result.overall.get(component)
    vals = [n.overall.get(component) for n in nulls if n.overall.get(component) is not None]
    if e is None or not vals:
        return None
    return e - max(vals)


# -------------------------------------------------------------------- paired gate (owner decision 2026-10-06)


@dataclass(frozen=True)
class PairedResult:
    component: str
    n: int                      # cases scored by both engine and null
    engine_mean: float          # case-level mean of the engine scores on those cases
    null_mean: float
    mean_diff: float            # engine minus null, case-level mean
    p_value: float              # one-sided: engine > null


def paired_sign_flip_test(engine: Result, null: Result, component: str, case_ids=None, n_perm: int = 10000,
                          seed: int = 20261006) -> PairedResult:
    """One-sided paired sign-flip permutation test of per-case scores, engine vs null.

    d_i = engine_i - null_i over cases scored by both (optionally restricted to ``case_ids``). Statistic:
    mean(d). Null distribution: mean(s_i * d_i) with independent signs s_i = +-1 drawn from
    ``numpy.random.default_rng(seed)``, ``n_perm`` draws. p = (1 + #{perm >= observed - 1e-12}) / (1 + n_perm).
    """
    if component not in COMPONENTS:
        raise ValueError(f"component {component!r} not in {COMPONENTS}")
    keep = None if case_ids is None else set(case_ids)
    nb = {s.case_id: s.get(component) for s in null.case_scores}
    pairs = [(s.get(component), nb.get(s.case_id)) for s in engine.case_scores
             if (keep is None or s.case_id in keep) and s.get(component) is not None
             and nb.get(s.case_id) is not None]
    if not pairs:
        raise ValueError("no case scored by both engine and null")
    e = np.array([a for a, _ in pairs], dtype=float)
    b = np.array([b for _, b in pairs], dtype=float)
    d = e - b
    observed = float(d.mean())
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_perm, len(d)))
    perm = (signs * d).mean(axis=1)
    p = (1 + int(np.sum(perm >= observed - 1e-12))) / (1 + n_perm)
    return PairedResult(component, len(d), float(e.mean()), float(b.mean()), observed, p)


@dataclass(frozen=True)
class GateResult:
    passed: bool
    agreement: float | None     # engine episode-first aggregate on the gate subset
    floor: float
    paired: PairedResult
    alpha: float


def paired_gate(engine: Result, best_null: Result, component: str, floor: float, alpha: float = 0.10,
                n_perm: int = 10000, seed: int = 20261006) -> GateResult:
    """Gate = paired sign-flip p < ``alpha`` (engine beats the pre-chosen best null case by case) AND the
    engine's episode-first aggregate on the same cases >= ``floor``. Both results must be runs on the gate
    subset (spec/scoring.md section 7)."""
    pr = paired_sign_flip_test(engine, best_null, component, n_perm=n_perm, seed=seed)
    agg = engine.overall.get(component)
    ok = pr.p_value < alpha and agg is not None and agg >= floor
    return GateResult(ok, agg, floor, pr, alpha)
