"""Child-process driver: evaluate one version's own engine on a list of dates.

Run as a script by ``fatpitch.versions.runner`` in a separate interpreter, never imported by it:

    python driver.py <request.json>

Request keys: ``version_src`` (the version's ``src`` directory), ``version_root``, ``registry`` (path to the
version's ``spec/registry.yaml`` or null), ``amber_data``, ``dates`` (ISO dates), ``out_dir``. The driver puts
``version_src`` first on ``sys.path``, drops every other path that would provide a ``fatpitch`` package (the
editable install of the current checkout), imports the version's ``fatpitch`` and asserts it came from
``version_src``. It then builds the version's own ``AmberLakeSource`` (``AmberSource`` for versions without
``fatpitch.lake``) and calls the version's
``fatpitch.evaluate(et_close(date), source, registry=...)`` for each date.

Writes ``decisions.jsonl.gz`` (one ``Decision.to_dict()`` per line, in date order) and ``driver_info.json``.
Only standard library at module level: nothing from the current checkout is imported here.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import gzip
import inspect
import json
import sys
import time
import warnings
from pathlib import Path


def _isolate(version_src: Path) -> None:
    here = Path(__file__).resolve().parent
    keep = []
    for p in sys.path:
        try:
            rp = Path(p or ".").resolve()
        except OSError:
            keep.append(p)
            continue
        if rp == here or (rp / "fatpitch" / "__init__.py").exists():
            continue
        keep.append(p)
    sys.path[:] = [str(version_src), *keep]
    for name in [m for m in sys.modules if m == "fatpitch" or m.startswith("fatpitch.")]:
        del sys.modules[name]


def _memoize_reads(src) -> bool:
    """Speed-up for lake sources that expose ``_read(files)`` (amber ``AmberSource``): cache parsed files by
    (name, mtime, size). The source's own consistency check (stamp before/after) still runs on every call."""
    if not hasattr(src, "_read"):
        return False
    orig, memo = src._read, {}

    def cached(files):
        key = tuple((str(f), f.stat().st_mtime_ns, f.stat().st_size) for f in files)
        if key not in memo:
            memo.clear()
            memo[key] = orig(files)
        return memo[key]

    src._read = cached
    return True


def _engine_source(amber_data: str):
    """The version's own catalogue-driven ``AmberLakeSource`` (E3 onward), restricted to the series its engine
    reads (``fatpitch.rules.ENGINE_SERIES``, else the step-1/1b catalogue ids); versions without
    ``fatpitch.lake`` fall back to their ``AmberSource``. The null models keep their own inputs (nullsource)."""
    try:
        from fatpitch.lake import AmberLakeSource, catalogue_ids, load_catalogue
    except ImportError:
        from fatpitch.source import AmberSource
        return AmberSource(root=amber_data)
    cat = load_catalogue()
    try:
        from fatpitch.rules import ENGINE_SERIES
        ids = [s for s in ENGINE_SERIES if s in cat["series"]]
    except ImportError:
        ids = catalogue_ids(cat, step=["1", "1b"])
    return AmberLakeSource(root=amber_data, series=ids, catalogue=cat)


def _plain(decision):
    if hasattr(decision, "to_dict"):
        return decision.to_dict()
    if dataclasses.is_dataclass(decision):
        return dataclasses.asdict(decision)
    return dict(decision)


def main(argv: list[str]) -> int:
    req = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    version_src = Path(req["version_src"]).resolve()
    _isolate(version_src)
    warnings.simplefilter("ignore")

    import fatpitch
    from fatpitch.dates import et_close

    origin = Path(fatpitch.__file__).resolve()
    if version_src not in origin.parents:
        raise SystemExit(f"isolation failed: fatpitch imported from {origin}, expected under {version_src}")

    src = _engine_source(req["amber_data"])
    memo = _memoize_reads(src)
    evaluate = fatpitch.evaluate
    kw = {}
    if req.get("registry") and "registry" in inspect.signature(evaluate).parameters:
        kw["registry"] = req["registry"]
    out_dir = Path(req["out_dir"])
    dates = [_dt.date.fromisoformat(d) for d in req["dates"]]
    t0, first = time.time(), None
    with gzip.open(out_dir / "decisions.jsonl.gz", "wt", encoding="utf-8", newline="\n") as fh:
        for i, d in enumerate(dates):
            dec = _plain(evaluate(et_close(d), src, **kw))
            first = first or dec
            fh.write(json.dumps(dec, default=str, sort_keys=True) + "\n")
            if (i + 1) % 200 == 0:
                print(f"  driver: {i + 1}/{len(dates)} dates, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    info = {
        "fatpitch_file": str(origin),
        "package_version": getattr(fatpitch, "__version__", None),
        "engine_version": (first or {}).get("engine_version"),
        "schema_version": (first or {}).get("schema_version"),
        "registry_sha": (first or {}).get("registry_sha"),
        "registry_arg": kw.get("registry"),
        "source_class": f"{type(src).__module__}.{type(src).__qualname__}",
        "source_root": str(getattr(src, "root", req["amber_data"])),
        "read_memoized": memo,
        "n_dates": len(dates),
        "seconds": round(time.time() - t0, 1),
        "python": sys.version.split()[0],
    }
    (out_dir / "driver_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
