"""``fatpitch.evaluate(asof, source) -> Decision`` (PLAN 0.2).

E3: steps 1 and 1b (regime vector per region with R-66 daily probabilities, internals vector) from one
point-in-time snapshot. Steps 2-7 are not implemented: the Decision stays "no pitch" (cash default).
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from fatpitch import registry as _registry
from fatpitch.dates import require_et
from fatpitch.decision import ConsumedInput, Decision
from fatpitch.rules import regime as _regime
from fatpitch.rules import timeline as _timeline
from fatpitch.source import Source

STUB_NOTE = "E3: steps 1 and 1b implemented; steps 2-7 not yet (cash default, no pitch)."
_TL_CACHE: dict = {}


def _source_name(source) -> str:
    return type(source).__name__


def _timeline_for(path: str | Path | None) -> _timeline.Timeline:
    p = Path(path) if path is not None else _timeline.default_path()
    key = (str(p), p.stat().st_mtime_ns if p.exists() else None)
    if key not in _TL_CACHE:
        _TL_CACHE.clear()
        _TL_CACHE[key] = _timeline.load(p)
    return _TL_CACHE[key]


def evaluate(asof: _dt.datetime, source: Source, registry: _registry.Registry | str | Path | None = None,
             series: list[str] | None = None, timeline: _timeline.Timeline | str | Path | None = None,
             track: str = "faithful") -> Decision:
    r"""Evaluate the process model at ``asof`` (tz-aware America/New_York).

    ``registry``: a Registry, a YAML path, or None (empty registry: every rule unknown). ``series``: restrict
    consumed inputs to these ids (default: every series in the snapshot). ``timeline``: a Timeline, a path, or
    None (``spec\claims\process_timeline.yaml`` when present, else every rule active). ``track``: "faithful"
    (default) or "hybrid" (adds the R-67 and R-68 evidence lines and the ``anticipated_turn`` note; regime output
    unchanged).
    """
    from fatpitch import __version__

    require_et(asof)
    reg = registry if isinstance(registry, _registry.Registry) else (
        _registry.load(registry) if registry is not None else _registry.empty())
    tl = timeline if isinstance(timeline, _timeline.Timeline) else _timeline_for(timeline)
    snap = source.snapshot(asof)
    res = _regime.run(asof, snap, reg, source=source, timeline=tl, track=track)
    consumed = []
    for sid in sorted(snap):
        if series is not None and sid not in series:
            continue
        f = snap[sid]
        if f.is_empty():
            continue
        last = f.row(-1, named=True)
        consumed.append(ConsumedInput(series_id=sid, value=last["value"], period_end=last["period_end"],
                                      published_at=last["published_at"], source=_source_name(source),
                                      vintage_id=last["vintage_id"]))
    return Decision(asof=asof, engine_version=__version__, registry_sha=reg.sha256, regime=res.regime,
                    internals=res.internals, consumed_inputs=consumed, no_pitch=True,
                    nearest_misses=[], notes=[STUB_NOTE, *res.notes])
