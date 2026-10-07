"""Null models (PLAN E.4), scored identically to the engine through the ``Engine`` interface.

Regime output uses the policy-direction vocabulary of the cases (easing | neutral | tightening).
Expression families use ``<asset_class>_<region lower>`` (e.g. ``equity_us``, ``rates_us``).
Series ids are constructor arguments; defaults name the series the data lift is expected to
provide. A missing series yields an empty (unknown) prediction component. Definitions are
pre-registered in ``spec/scoring.md``.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field

import polars as pl

from fatpitch.cases.regime import deterministic_probs
from fatpitch.cases.schema import Case, Corpus, ThesisTarget
from fatpitch.cases.scoring import Prediction


def _with_probs(p: Prediction) -> Prediction:
    """Deterministic regime -> probabilities (spec/scoring.md 6c: NULL_CONFIDENCE 0.9 on the predicted class)."""
    return Prediction(p.regime_direction, p.theses, p.expressions, p.action, p.tilts,
                      deterministic_probs(p.regime_direction))


def value_at(frame: pl.DataFrame | None, d: _dt.date) -> float | None:
    """Last value with period_end <= d in an as-of frame."""
    if frame is None or frame.is_empty():
        return None
    sub = frame.filter(pl.col("period_end") <= d)
    return None if sub.is_empty() else sub["value"][-1]


def _family(asset_class: str, region: str | None) -> str:
    return f"{asset_class}_{(region or 'global').lower()}"


@dataclass
class AlwaysRiskOn:
    """Constant risk-on state: policy easing, long US equities, action enter."""

    name: str = "null_always_risk_on"

    def predict(self, asof: _dt.datetime, source) -> Prediction:
        return _with_probs(Prediction("easing", (ThesisTarget("equity", "long", "US"),), ("equity_us",), "enter"))


@dataclass
class FedDirectionOnly:
    """Policy-rate change over ``lookback_days``: falling -> easing, long rates and equity, enter;
    rising -> tightening, short rates and equity, enter; |change| <= threshold -> neutral, hold."""

    series_id: str = "FEDFUNDS"
    lookback_days: int = 182
    threshold: float = 0.0
    name: str = "null_fed_direction"

    def predict(self, asof: _dt.datetime, source) -> Prediction:
        snap = source.snapshot(asof) if source is not None else {}
        f = snap.get(self.series_id)
        now = value_at(f, asof.date())
        then = value_at(f, asof.date() - _dt.timedelta(days=self.lookback_days))
        if now is None or then is None:
            return Prediction()
        chg = now - then
        if chg < -self.threshold:
            return _with_probs(Prediction(
                "easing", (ThesisTarget("rates", "long", "US"), ThesisTarget("equity", "long", "US")),
                ("rates_us", "equity_us"), "enter"))
        if chg > self.threshold:
            return _with_probs(Prediction(
                "tightening", (ThesisTarget("rates", "short", "US"), ThesisTarget("equity", "short", "US")),
                ("rates_us", "equity_us"), "enter"))
        return _with_probs(Prediction("neutral", (), (), "hold"))


@dataclass
class Trend12m:
    """12-month trend (sign of the 365-day change) of each series. ``series`` maps a series id to
    ``(asset_class, region, sign)``; ``sign = -1`` for yield series used as price proxies (yield down
    = bond price up). One thesis per series (long if signed change > 0), ranked by |relative change|;
    expressions follow the thesis order. Regime from ``regime_series`` (the rates series): signed change
    > 0 (bond prices up, yields down) -> easing, else tightening."""

    series: dict[str, tuple] = field(default_factory=lambda: {
        "SPY": ("equity", "US", 1), "IEF": ("rates", "US", 1), "DXY": ("fx", "USD", 1)})
    regime_series: str = "IEF"
    name: str = "null_trend_12m"

    def predict(self, asof: _dt.datetime, source) -> Prediction:
        snap = source.snapshot(asof) if source is not None else {}
        d, back = asof.date(), asof.date() - _dt.timedelta(days=365)
        moves: list[tuple[float, ThesisTarget]] = []
        regime = None
        for sid, spec in self.series.items():
            cls, region = spec[0], spec[1]
            sign = spec[2] if len(spec) > 2 else 1
            now, then = value_at(snap.get(sid), d), value_at(snap.get(sid), back)
            if now is None or then is None or then == 0:
                continue
            r = sign * (now / then - 1)
            moves.append((abs(r), ThesisTarget(cls, "long" if r > 0 else "short", region)))
            if sid == self.regime_series:
                regime = "easing" if r > 0 else "tightening"
        if not moves:
            return Prediction()
        moves.sort(key=lambda m: -m[0])
        theses = tuple(t for _, t in moves)
        return _with_probs(Prediction(regime, theses, tuple(_family(t.asset_class, t.region) for t in theses), "enter"))


@dataclass
class Persistence:
    """Predicts the targets of the most recent case documented at least ``embargo_days`` before the
    prediction date (the last known documented state persists). The embargo exceeds the widest
    case window (+-1 quarter), so a case's own targets are never visible inside its own window."""

    corpus: Corpus | list[Case]
    embargo_days: int = 120
    name: str = "null_persistence"
    _cases: list[Case] = field(init=False, repr=False)

    def __post_init__(self):
        cases = self.corpus.cases if isinstance(self.corpus, Corpus) else self.corpus
        self._cases = sorted(cases, key=lambda c: c.asof)

    def predict(self, asof: _dt.datetime, source) -> Prediction:
        cutoff = asof - _dt.timedelta(days=self.embargo_days)
        prior = [c for c in self._cases if c.asof < cutoff]
        if not prior:
            return Prediction()
        t = prior[-1].targets
        return _with_probs(Prediction(t.regime_direction, t.theses, t.expression, t.action))


def default_nulls(corpus: Corpus | list[Case]) -> list:
    return [AlwaysRiskOn(), FedDirectionOnly(), Trend12m(), Persistence(corpus)]


# -------------------------------------------------------------------- 13F tilt baselines (PLAN E.4)


@dataclass
class NoChangeTilt:
    """13F baseline: no change in any family (every predicted sign 0). Scores 0 on the tilt component by
    construction; any correct sign beats it."""

    name: str = "null_tilt_no_change"

    def predict(self, asof: _dt.datetime, source) -> Prediction:
        return Prediction()


@dataclass
class PriorTiltPersistence:
    """13F baseline: the previous quarter's family change signs persist. Uses ``Case.baseline_tilt``
    (derived from the two filings before the case's own pair, both filed before the case's earlier filing)
    of the latest 13F case with asof <= the prediction date."""

    corpus: Corpus | list[Case]
    name: str = "null_tilt_persistence"
    _cases: list[Case] = field(init=False, repr=False)

    def __post_init__(self):
        cases = self.corpus.cases if isinstance(self.corpus, Corpus) else self.corpus
        self._cases = sorted((c for c in cases if c.baseline_tilt), key=lambda c: c.asof)

    def predict(self, asof: _dt.datetime, source) -> Prediction:
        prior = [c for c in self._cases if c.asof <= asof]
        return Prediction(tilts=prior[-1].baseline_tilt) if prior else Prediction()


def tilt_baselines(corpus: Corpus | list[Case]) -> list:
    return [NoChangeTilt(), PriorTiltPersistence(corpus)]
