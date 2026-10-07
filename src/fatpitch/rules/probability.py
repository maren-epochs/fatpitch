"""R-66 regime probability mapping (spec\\process.md section 1, R-66; registry ``regime.prob_*``).

Evidence counting over independent rule families:

    mass[c] = regime.prob_base_mass + sum over known families f pointing to class c of
              regime.prob_family_increment x timeline_weight(f)
    P[c]    = mass[c] / sum(mass), floored at regime.prob_floor and renormalised

A family whose output is unknown or inactive contributes nothing. When no family is known the
probabilities are unknown (None), never a guess. ``policy_direction`` = argmax; ties are resolved in favour
of the anchor (the R-14 output for the US, the R-12 output for other regions), else ``neutral``, else the
class of the first known family.
"""

from __future__ import annotations

from dataclasses import dataclass

from fatpitch.rules.outputs import CLASSES


@dataclass(frozen=True)
class Family:
    name: str
    cls: str | None        # easing | neutral | tightening | None (unknown / inactive)
    weight: float = 1.0


@dataclass(frozen=True)
class RegimeProbs:
    p_easing: float
    p_neutral: float
    p_tightening: float
    direction: str
    families: tuple[Family, ...]

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.p_easing, self.p_neutral, self.p_tightening)


def liquidity_class(sign: int | None) -> str | None:
    """Liquidity impulse -> policy class: positive impulse = easing, negative = tightening, neutral band =
    neutral (process.md R-01/R-14: liquidity expansion is the easing condition)."""
    return None if sign is None else {1: "easing", -1: "tightening", 0: "neutral"}[sign]


def regime_probabilities(families: list[Family], anchor: str | None, base: float, increment: float,
                         floor: float) -> RegimeProbs | None:
    known = [f for f in families if f.cls is not None and f.weight > 0]
    if not known:
        return None
    mass = dict.fromkeys(CLASSES, float(base))
    for f in known:
        mass[f.cls] += increment * f.weight
    tot = sum(mass.values())
    p = {c: m / tot for c, m in mass.items()}
    low = {c for c, v in p.items() if v < floor}
    if low:  # floored classes get exactly the floor; the rest share the remaining mass in proportion
        rest = sum(v for c, v in p.items() if c not in low)
        p = {c: floor if c in low else v / rest * (1.0 - floor * len(low)) for c, v in p.items()}
    top = max(p.values())
    tied = [c for c in CLASSES if p[c] >= top - 1e-12]
    if anchor in tied:
        direction = anchor
    elif "neutral" in tied:
        direction = "neutral"
    else:
        direction = next(f.cls for f in known if f.cls in tied)
    return RegimeProbs(p["easing"], p["neutral"], p["tightening"], direction, tuple(families))
