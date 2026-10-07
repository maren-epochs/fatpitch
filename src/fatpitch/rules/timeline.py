"""Time-varying process: which rules were held at a replay date, and with what weight.

Source: ``spec/claims/process_timeline.yaml`` when it exists; otherwise ``Timeline.all_active()`` (every rule
active at every date, weight 1; stated in each Decision's notes).

Layout of the project file (version 2026-10-07.1): top-level ``eras`` {E1: "1977-1987 ...", ...} and ``rules``
[{id, held_from, held_until, weight: {E1: code, ...}, ...}] with era codes core | active | reduced | minor |
context | veto | unknown | absent | n/a (free text may follow the code).

Gate applied here (interpretation, documented in spec/process.md R-66):

* era code ``absent`` or ``n/a`` -> not held in that era (weight 0);
* every other code -> held, weight 1. ``unknown`` ("no evidence; the belief may have been held but cannot be
  dated", claims README) is treated as held: no evidence of absence, and PLAN E.4a designates R-02 as the era-B
  measure, which a stricter reading would contradict. ``reduced`` / ``minor`` are not turned into fractional
  weights (that would need numbers the timeline does not give);
* ``held_until`` that is a plain date ends the rule after that date; a qualified value (free text after the date,
  e.g. R-08 "(as a forecast rule)") is recorded but does not gate;
* dates before the first era use the first era's code; dates after the last era use the last era's code.

A generic layout is also accepted: ``rules`` entries with ``active_from`` / ``active_until`` / numeric
``weight`` (or ``spells`` of those). A rule absent from a present file is active at all dates with weight 1.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

TIMELINE_REL = Path("spec") / "claims" / "process_timeline.yaml"


def default_path() -> Path:
    from fatpitch.registry import project_root
    return project_root() / TIMELINE_REL


def _date(v, end: bool = False) -> _dt.date | None:
    if v is None or v == "":
        return None
    if isinstance(v, _dt.datetime):
        return v.date()
    if isinstance(v, _dt.date):
        return v
    if isinstance(v, int):
        return _dt.date(v, 12, 31) if end else _dt.date(v, 1, 1)
    s = str(v).strip()
    if len(s) == 4 and s.isdigit():
        return _date(int(s), end)
    if len(s) == 7:
        y, m = int(s[:4]), int(s[5:7])
        return _dt.date(y, m, 1)
    return _dt.date.fromisoformat(s[:10])


@dataclass(frozen=True)
class Spell:
    start: _dt.date | None
    end: _dt.date | None
    weight: float = 1.0

    def covers(self, d: _dt.date) -> bool:
        return (self.start is None or d >= self.start) and (self.end is None or d <= self.end)


@dataclass
class Timeline:
    spells: dict[str, list[Spell]] = field(default_factory=dict)
    source: str = "default: every rule active at all dates, weight 1 (no process timeline file)"

    @classmethod
    def all_active(cls) -> Timeline:
        return cls()

    def weight(self, rule: str, d: _dt.date) -> float:
        """0 when the rule is not held at ``d``; else its weight."""
        sp = self.spells.get(rule)
        if sp is None:
            return 1.0
        for s in sp:
            if s.covers(d):
                return s.weight
        return 0.0

    def active(self, rule: str, d: _dt.date) -> bool:
        return self.weight(rule, d) > 0.0


def _entries(doc) -> list[dict]:
    if doc is None:
        return []
    if isinstance(doc, dict) and "rules" in doc:
        doc = doc["rules"]
    if isinstance(doc, dict):
        out = []
        for k, v in doc.items():
            e = dict(v) if isinstance(v, dict) else {"spells": v} if isinstance(v, list) else {}
            e.setdefault("id", k)
            out.append(e)
        return out
    if isinstance(doc, list):
        return [e for e in doc if isinstance(e, dict)]
    raise ValueError("process timeline: unsupported layout")


INACTIVE_CODES = {"absent", "n/a"}


def _era_ranges(eras) -> list[tuple[str, int, int]]:
    out = []
    for k, v in (eras or {}).items():
        m = re.match(r"\s*(\d{4})\s*-\s*(\d{4})", str(v))
        if m:
            out.append((str(k), int(m.group(1)), int(m.group(2))))
    return sorted(out, key=lambda x: x[1])


def _code(v) -> str:
    return str(v).strip().split()[0].lower().rstrip(",;:") if v not in (None, "") else "unknown"


def _plain_date(v) -> _dt.date | None:
    if isinstance(v, (_dt.date, int)):
        return _date(v, end=True)
    s = str(v or "").strip()
    if re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", s):
        return _date(s, end=True)
    return None


def load(path: str | Path | None = None) -> Timeline:
    p = Path(path) if path is not None else default_path()
    if not p.exists():
        return Timeline.all_active()
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    eras = _era_ranges(doc.get("eras") if isinstance(doc, dict) else None)
    spells: dict[str, list[Spell]] = {}
    for e in _entries(doc):
        rid = e.get("id") or e.get("rule") or e.get("rule_id")
        if not rid:
            continue
        rid = str(rid)
        w = e.get("weight")
        if isinstance(w, dict) and eras:
            until = _plain_date(e.get("held_until"))
            for i, (era, y0, y1) in enumerate(eras):
                start = None if i == 0 else _dt.date(y0, 1, 1)
                end = None if i == len(eras) - 1 else _dt.date(y1, 12, 31)
                if until is not None and (end is None or until < end):
                    end = until
                    if start is not None and end < start:
                        continue
                weight = 0.0 if _code(w.get(era)) in INACTIVE_CODES else 1.0
                spells.setdefault(rid, []).append(Spell(start, end, weight))
            continue
        raw = e.get("spells") or [e]
        for s in raw:
            if not isinstance(s, dict):
                continue
            wt = s.get("weight", w if not isinstance(w, dict) else 1.0)
            spells.setdefault(rid, []).append(
                Spell(_date(s.get("active_from")), _date(s.get("active_until"), end=True),
                      float(1.0 if wt is None else wt)))
    return Timeline(spells, source=str(p))
