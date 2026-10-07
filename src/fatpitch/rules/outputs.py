"""Typed rule outputs and parameter access.

Every rule function returns a ``RuleOutput``: ``status`` is ``ok``, ``unknown`` (an input or parameter is
missing, unusable or stale) or ``inactive`` (the rule is outside its active spell in the process timeline).
``unknown`` and ``inactive`` are never a pass or a fail; downstream consumers treat both as no evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fatpitch import registry as _registry

OK, UNKNOWN, INACTIVE = "ok", "unknown", "inactive"
CLASSES = ("easing", "neutral", "tightening")


class MissingParam(KeyError):
    pass


@dataclass
class RuleOutput:
    rule: str
    status: str = UNKNOWN
    values: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    variant: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == OK

    def get(self, key: str, default=None):
        return self.values.get(key, default) if self.ok else default

    def summary(self) -> str:
        if not self.ok:
            return f"{self.rule}={self.status}" + (f" ({self.reason})" if self.reason else "")
        parts = []
        for k, v in self.values.items():
            if isinstance(v, float):
                parts.append(f"{k}={v:.4g}")
            elif isinstance(v, (str, int, bool)) or v is None:
                parts.append(f"{k}={v}")
        var = f" [{self.variant}]" if self.variant else ""
        return f"{self.rule}{var}: " + ", ".join(parts)


def unknown(rule: str, reason: str, variant: str | None = None, **values) -> RuleOutput:
    return RuleOutput(rule, UNKNOWN, dict(values), reason, variant)


def ok(rule: str, variant: str | None = None, **values) -> RuleOutput:
    return RuleOutput(rule, OK, dict(values), "", variant)


class Params:
    """Registry values by id; a missing id raises ``MissingParam`` (the rule returns unknown)."""

    def __init__(self, reg: _registry.Registry):
        self.reg = reg

    def __call__(self, pid: str):
        if pid not in self.reg:
            raise MissingParam(pid)
        return self.reg[pid].value

    def num(self, pid: str) -> float:
        return float(self(pid))

    def int(self, pid: str) -> int:
        return int(self(pid))
