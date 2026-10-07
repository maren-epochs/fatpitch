"""Decision -> Prediction adapter: the single place where an engine ``Decision`` becomes a scorable
``Prediction`` (spec/scoring.md section 1). Engine work (E3-E6) fills ``Decision`` fields; this mapping
turns them into the case vocabulary and is applied identically to every version.

Input is a ``Decision`` or its plain dict (``Decision.to_dict()``, as written by the version driver), so
decisions produced by older or newer schema versions map without importing their classes. Missing keys
are unknown (empty component), never a fail.

| Prediction field | Decision source | Rule |
|---|---|---|
| ``regime_direction`` | ``regime[*].policy_direction`` | region ``US`` first (cases are US-policy labels), else the first regime vector with a direction; None if none |
| ``theses`` | ``theses[*]`` | ``ThesisTarget(asset_class, direction, region)``, in Decision order |
| ``expressions`` | ``expressions[*].family`` | sorted by ``rank`` (ascending = best first), duplicates dropped |
| ``action`` | ``exits``, ``signals[*].tier``, ``no_pitch`` | exits and new signals -> ``reverse``; exits only -> ``exit``; any ``fat_pitch`` signal -> ``size_up``; any ``starter`` signal -> ``enter``; ``watch`` signals only, or ``no_pitch`` with no signal -> ``flat`` (step 7 cash default; ``flat`` = no new position, spec/scoring.md section 3); otherwise None |
| ``tilts`` | ``tilts`` (not in Decision schema v1) | ``(family, sign)`` pairs when present; else empty |
| ``regime_probs`` | ``regime[*].p_easing / p_neutral / p_tightening`` (schema 2) | the same regime vector as ``regime_direction`` (US first); None when absent (scored as missing = worst RPS) |

The action mapping is the E6 placeholder required by spec/scoring.md section 8 ("mapping tier/exit -> action
is an engine-side responsibility"); ``reduce`` and ``hold`` need position state and are not emitted until
the Decision carries it.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fatpitch.cases.schema import ThesisTarget
from fatpitch.cases.scoring import Prediction

ADAPTER_VERSION = "2"


def _plain(decision: Any) -> Mapping:
    if isinstance(decision, Mapping):
        return decision
    if hasattr(decision, "to_dict"):
        return decision.to_dict()
    raise TypeError(f"cannot adapt {type(decision).__name__}; expected Decision or dict")


def _regime(d: Mapping) -> str | None:
    vecs = [r for r in (d.get("regime") or []) if r and r.get("policy_direction")]
    us = [r for r in vecs if str(r.get("region") or "").upper() == "US"]
    pick = us or vecs
    return pick[0]["policy_direction"] if pick else None


def _theses(d: Mapping) -> tuple[ThesisTarget, ...]:
    out = []
    for t in d.get("theses") or []:
        if t and t.get("asset_class") and t.get("direction"):
            out.append(ThesisTarget(t["asset_class"], t["direction"], t.get("region")))
    return tuple(out)


def _expressions(d: Mapping) -> tuple[str, ...]:
    ex = [e for e in (d.get("expressions") or []) if e and e.get("family")]
    ex.sort(key=lambda e: (e.get("rank") if e.get("rank") is not None else 10**9))
    seen: list[str] = []
    for e in ex:
        if e["family"] not in seen:
            seen.append(e["family"])
    return tuple(seen)


def _action(d: Mapping) -> str | None:
    exits = d.get("exits") or []
    tiers = {s.get("tier") for s in (d.get("signals") or []) if s}
    if exits:
        return "reverse" if tiers & {"fat_pitch", "starter"} else "exit"
    if "fat_pitch" in tiers:
        return "size_up"
    if "starter" in tiers:
        return "enter"
    if tiers == {"watch"} or (not tiers and d.get("no_pitch")):
        return "flat"
    return None


def _regime_probs(d: Mapping) -> tuple[float, float, float] | None:
    vecs = [r for r in (d.get("regime") or []) if r and r.get("p_easing") is not None]
    us = [r for r in vecs if str(r.get("region") or "").upper() == "US"]
    pick = us or vecs
    if not pick:
        return None
    r = pick[0]
    return (float(r["p_easing"]), float(r["p_neutral"]), float(r["p_tightening"]))


def _tilts(d: Mapping) -> tuple[tuple[str, int], ...]:
    raw = d.get("tilts") or ()
    items = raw.items() if isinstance(raw, Mapping) else raw
    return tuple((str(f), int(s)) for f, s in items)


def decision_to_prediction(decision: Any) -> Prediction:
    """Map one Decision (object or dict) to the Prediction scored by ``fatpitch.cases.scoring``."""
    d = _plain(decision)
    return Prediction(_regime(d), _theses(d), _expressions(d), _action(d), _tilts(d), _regime_probs(d))
