"""Decision schema v1 (PLAN 0.2, E.1 outputs).

A ``Decision`` is the full output of one ``fatpitch.evaluate(asof, source)`` call. It serialises to
JSON (``to_json`` / ``from_json``) and to parquet (``write_parquet`` / ``read_parquet``; one row per
decision, nested fields as Arrow structs and lists, schema derived from the dataclasses).

Vocabularies are validated on construction. ``None`` means unknown; unknown is never a fail.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import types
import typing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from fatpitch.dates import NY

SCHEMA_VERSION = "2"  # 2: RegimeVector daily probabilities (owner decision 2026-10-07, spec/scoring.md 6c)
PROB_FLOOR = 0.01

POLICY_DIRECTIONS = {"easing", "neutral", "tightening"}
DIRECTIONS = {"long", "short"}
TIERS = {"fat_pitch", "starter", "watch"}
PREMISE_STATUS = {"intact", "broken", "unknown"}
TAGS = {"stated", "interpreted", "interpreted-from-article"}
SIZE_UNITS = {"pct_nav", "pct_nav_10y_eq", "risk_units"}


def _check(value, allowed: set, name: str) -> None:
    if value is not None and value not in allowed:
        raise ValueError(f"{name}={value!r} not in {sorted(allowed)}")


@dataclass
class RegimeVector:
    region: str
    policy_direction: str | None = None
    liquidity_impulse: float | None = None
    liquidity_change: float | None = None
    policy_error_sign: int | None = None          # -1 too tight, 0 none, +1 too loose
    veto_flags: list[str] = field(default_factory=list)
    fragility_level: float | None = None          # non-gating
    display_label: str | None = None              # 5-level label, display only
    # schema 2: as-of probabilities at 16:00 ET, each >= PROB_FLOOR, summing to 1; policy_direction = argmax
    p_easing: float | None = None
    p_neutral: float | None = None
    p_tightening: float | None = None
    # additive (E3, 2026-10-07; optional, absent in older decisions): process.md step-1 outputs
    liquidity_sign: int | None = None             # +1 positive impulse, 0 neutral, -1 negative
    liquidity_variant: str | None = None          # rule variant that drove the impulse (R-02 | R-03+R-04 | ...)
    fci_state: str | None = None                  # R-58: loose | neutral | tight
    fragility_state: str | None = None            # R-11: normal | high (low is not defined by the rule)
    relative_impulse: float | None = None         # R-12: impulse_X - impulse_US
    evidence: list[str] = field(default_factory=list)  # one summary line per rule output (unknown included)

    def __post_init__(self):
        _check(self.policy_direction, POLICY_DIRECTIONS, "policy_direction")
        _check(self.liquidity_sign, {-1, 0, 1}, "liquidity_sign")
        _check(self.fci_state, {"loose", "neutral", "tight"}, "fci_state")
        _check(self.fragility_state, {"low", "normal", "high"}, "fragility_state")
        _check(self.policy_error_sign, {-1, 0, 1}, "policy_error_sign")
        probs = (self.p_easing, self.p_neutral, self.p_tightening)
        if any(p is not None for p in probs):
            if any(p is None for p in probs):
                raise ValueError("regime probabilities: all three or none")
            if min(probs) < PROB_FLOOR - 1e-9 or abs(sum(probs) - 1.0) > 1e-6:
                raise ValueError(f"regime probabilities {probs} must each be >= {PROB_FLOOR} and sum to 1")
            names = ("easing", "neutral", "tightening")
            top = names[max(range(3), key=lambda i: probs[i])]
            tied = {n for n, p in zip(names, probs, strict=True) if p >= max(probs) - 1e-9}
            if self.policy_direction is None:
                self.policy_direction = top
            elif self.policy_direction not in tied:  # ties: the engine's tie rule picks (process.md R-66)
                raise ValueError(f"policy_direction {self.policy_direction!r} != argmax of probabilities ({top!r})")

    @property
    def probabilities(self) -> tuple[float, float, float] | None:
        if self.p_easing is None:
            return None
        return (self.p_easing, self.p_neutral, self.p_tightening)


@dataclass
class InternalsComponent:
    name: str
    direction: str | None = None                  # up | down | flat
    turn_age_days: int | None = None
    value: float | None = None

    def __post_init__(self):
        _check(self.direction, {"up", "down", "flat"}, "direction")


@dataclass
class InternalsVector:
    direction: str | None = None
    turn_age_days: int | None = None
    components: list[InternalsComponent] = field(default_factory=list)

    def __post_init__(self):
        _check(self.direction, {"up", "down", "flat"}, "direction")


@dataclass
class Premise:
    premise_id: str
    text: str
    status: str = "unknown"

    def __post_init__(self):
        _check(self.status, PREMISE_STATUS, "status")


@dataclass
class Thesis:
    thesis_id: str
    asset_class: str
    direction: str
    region: str | None = None
    premises: list[Premise] = field(default_factory=list)
    invalidation_events: list[str] = field(default_factory=list)
    rationale_rule_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        _check(self.direction, DIRECTIONS, "direction")


@dataclass
class Expression:
    thesis_id: str
    instrument: str
    family: str
    direction: str
    rank: int
    sensitivity: float | None = None
    asymmetry: float | None = None

    def __post_init__(self):
        _check(self.direction, DIRECTIONS, "direction")


@dataclass
class Veto:
    thesis_id: str
    instrument: str | None
    gate: str
    passed: bool | None                           # None = unknown, never a fail
    reason: str = ""
    tag: str = "stated"

    def __post_init__(self):
        _check(self.tag, TAGS, "tag")


@dataclass
class SizeBand:
    low: float
    high: float
    unit: str = "pct_nav"                         # pct_nav | pct_nav_10y_eq | risk_units

    def __post_init__(self):
        _check(self.unit, SIZE_UNITS, "unit")
        if self.low > self.high:
            raise ValueError("size band low > high")


@dataclass
class Signal:
    signal_id: str
    thesis_id: str
    instrument: str
    direction: str
    tier: str
    size_band: SizeBand | None = None
    catalyst_date: _dt.date | None = None
    evidence: list[str] = field(default_factory=list)

    def __post_init__(self):
        _check(self.tier, TIERS, "tier")
        _check(self.direction, DIRECTIONS, "direction")


@dataclass
class Exit:
    signal_id: str
    broken_premise_id: str | None
    reason: str
    flagged_at: _dt.datetime


@dataclass
class ConsumedInput:
    series_id: str
    value: float | None
    period_end: _dt.date | None
    published_at: _dt.datetime | None
    source: str
    vintage_id: str | None = None


@dataclass
class Decision:
    asof: _dt.datetime
    engine_version: str
    registry_sha: str
    schema_version: str = SCHEMA_VERSION
    regime: list[RegimeVector] = field(default_factory=list)
    internals: InternalsVector = field(default_factory=InternalsVector)
    theses: list[Thesis] = field(default_factory=list)
    expressions: list[Expression] = field(default_factory=list)
    vetoes: list[Veto] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    exits: list[Exit] = field(default_factory=list)
    consumed_inputs: list[ConsumedInput] = field(default_factory=list)
    no_pitch: bool = True
    nearest_misses: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.asof.tzinfo is None:
            raise ValueError("Decision.asof must be tz-aware")

    # ---------------------------------------------------------------- dict / JSON

    def to_dict(self) -> dict:
        return _to_plain(self)

    @classmethod
    def from_dict(cls, d: dict) -> Decision:
        return _from_plain(cls, d)

    def to_json(self, **kw) -> str:
        return json.dumps(self.to_dict(), **kw)

    @classmethod
    def from_json(cls, s: str) -> Decision:
        return cls.from_dict(json.loads(s))

    def region(self, name: str) -> RegimeVector | None:
        return next((r for r in self.regime if r.region == name), None)


# -------------------------------------------------------------------- plain conversion


def _to_plain(obj) -> Any:
    if dataclasses.is_dataclass(obj):
        return {f.name: _to_plain(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, list):
        return [_to_plain(x) for x in obj]
    if isinstance(obj, _dt.datetime):
        return obj.astimezone(NY).isoformat()
    if isinstance(obj, _dt.date):
        return obj.isoformat()
    return obj


def _hints(cls) -> dict:
    return typing.get_type_hints(cls)


def _unwrap_optional(tp):
    if typing.get_origin(tp) in (typing.Union, types.UnionType):
        args = [a for a in typing.get_args(tp) if a is not type(None)]
        if len(args) == 1:
            return args[0], True
    return tp, False


def _from_value(tp, v):
    tp, _ = _unwrap_optional(tp)
    if v is None:
        return None
    if typing.get_origin(tp) is list:
        (inner,) = typing.get_args(tp)
        return [_from_value(inner, x) for x in v]
    if dataclasses.is_dataclass(tp):
        return _from_plain(tp, v)
    if tp is _dt.datetime:
        t = v if isinstance(v, _dt.datetime) else _dt.datetime.fromisoformat(v)
        if t.tzinfo is None:
            raise ValueError(f"naive datetime {v!r} in decision payload")
        return t.astimezone(NY)
    if tp is _dt.date:
        return v if isinstance(v, _dt.date) else _dt.date.fromisoformat(v)
    if tp is float:
        return float(v)
    return v


def _from_plain(cls, d: dict):
    hints = _hints(cls)
    kwargs = {f.name: _from_value(hints[f.name], d[f.name]) for f in dataclasses.fields(cls) if f.name in d}
    return cls(**kwargs)


# -------------------------------------------------------------------- arrow schema


def _arrow_type(tp) -> pa.DataType:
    tp, _ = _unwrap_optional(tp)
    if typing.get_origin(tp) is list:
        (inner,) = typing.get_args(tp)
        return pa.list_(_arrow_type(inner))
    if dataclasses.is_dataclass(tp):
        hints = _hints(tp)
        return pa.struct([pa.field(f.name, _arrow_type(hints[f.name])) for f in dataclasses.fields(tp)])
    mapping = {str: pa.string(), float: pa.float64(), int: pa.int64(), bool: pa.bool_(),
               _dt.date: pa.date32(), _dt.datetime: pa.timestamp("us", tz="America/New_York")}
    if tp in mapping:
        return mapping[tp]
    raise TypeError(f"no arrow mapping for {tp!r}")


def arrow_schema() -> pa.Schema:
    hints = _hints(Decision)
    return pa.schema([pa.field(f.name, _arrow_type(hints[f.name])) for f in dataclasses.fields(Decision)])


def _to_arrow_obj(obj):
    if dataclasses.is_dataclass(obj):
        return {f.name: _to_arrow_obj(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, list):
        return [_to_arrow_obj(x) for x in obj]
    return obj


def to_arrow(decisions: list[Decision]) -> pa.Table:
    return pa.Table.from_pylist([_to_arrow_obj(d) for d in decisions], schema=arrow_schema())


def from_arrow(table: pa.Table) -> list[Decision]:
    return [Decision.from_dict(row) for row in table.to_pylist()]


def write_parquet(decisions: Decision | list[Decision], path: str | Path) -> None:
    ds = [decisions] if isinstance(decisions, Decision) else list(decisions)
    pq.write_table(to_arrow(ds), Path(path))


def read_parquet(path: str | Path) -> list[Decision]:
    return from_arrow(pq.read_table(Path(path)))
