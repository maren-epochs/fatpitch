"""Parameter registry (PLAN 0.1 tags, E.6 calibration cap). Canonical file: ``spec\\registry.yaml``.

YAML layout (a top-level list; a mapping ``{registry_version, parameters: [...]}`` is also accepted)::

    - id: liq.m2_ip.spread_pp
      value: 2.0                 # number, list, string or bool; the value used when no calibration ran
      range: [0.0, 6.0]          # search range for tunables; descriptive range (spread across tellings)
                                 # for stated parameters; or null
      tag: interpreted           # stated | interpreted | interpreted-from-article
      citation: "DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md ('...')"
      notes: free text
      tunable: true              # explicit; a range alone does not make a parameter tunable

Validation (``validate``):

* required keys ``id``, ``value``, ``tag``, ``tunable``; no keys outside the layout; ids unique.
* ``stated`` requires a citation containing at least one library reference (``DS/...`` or ``RS/...``).
* ``tunable: true`` requires tag ``interpreted`` and a numeric ``range`` [low, high] containing ``value``.
* At most ``MAX_TUNABLE`` (8) tunable parameters.
* With ``root`` (project root): every ``DS/<name>`` / ``RS/<name>`` reference resolves to a file in
  ``library\\discovered_sources`` / ``library\\reference_sources``; a partial name is accepted when it
  starts with the date prefix and exactly matches the start of an existing file name.

``Registry.sha256`` hashes the canonical JSON of the validated parameters (sorted keys, ids in file
order), so YAML formatting and comments do not change the sha; content changes do.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

TAGS = ("stated", "interpreted", "interpreted-from-article")
MAX_TUNABLE = 8
KEYS = {"id", "value", "range", "tag", "citation", "notes", "tunable"}
REQUIRED = ("id", "value", "tag", "tunable")
LIBRARY_DIRS = {"DS": Path("library") / "discovered_sources", "RS": Path("library") / "reference_sources"}
CITE_RE = re.compile(r"\b(DS|RS)/([0-9X]{4}-[0-9X]{2}-[0-9X]{2}[A-Za-z0-9_.\-]*)")
DATE_PREFIX_RE = re.compile(r"^[0-9X]{4}-[0-9X]{2}-[0-9X]{2}")


class RegistryError(ValueError):
    pass


def project_root() -> Path:
    env = os.environ.get("FATPITCH_ROOT")
    return Path(env) if env else Path(__file__).resolve().parents[2]


DEFAULT_PATH = project_root() / "spec" / "registry.yaml"


@dataclass(frozen=True)
class Parameter:
    id: str
    tag: str
    value: Any = None
    range: tuple[float, float] | None = None
    citation: str = ""
    notes: str = ""
    tunable: bool = False

    @property
    def effective(self) -> Any:
        """Value used when no calibration has run."""
        return self.value

    @property
    def library_refs(self) -> list[tuple[str, str]]:
        """``(DS|RS, name)`` references found in the citation."""
        return [(m.group(1), m.group(2).rstrip(".")) for m in CITE_RE.finditer(self.citation)]


@dataclass
class Registry:
    parameters: list[Parameter]
    version: int = 1
    source_path: str | None = None
    _index: dict[str, Parameter] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._index = {p.id: p for p in self.parameters}

    def __getitem__(self, pid: str) -> Parameter:
        return self._index[pid]

    def __contains__(self, pid: str) -> bool:
        return pid in self._index

    def __len__(self) -> int:
        return len(self.parameters)

    @property
    def tunable(self) -> list[Parameter]:
        return [p for p in self.parameters if p.tunable]

    def canonical(self) -> str:
        body = {"registry_version": self.version,
                "parameters": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(p).items()}
                               for p in self.parameters]}
        return json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical().encode("utf-8")).hexdigest()


def _parse(raw: dict) -> Parameter:
    if not isinstance(raw, dict) or "id" not in raw:
        raise RegistryError(f"parameter entry without id: {raw!r}")
    pid = raw["id"]
    unknown = set(raw) - KEYS
    if unknown:
        raise RegistryError(f"{pid}: unknown keys {sorted(unknown)}")
    missing = [k for k in REQUIRED if k not in raw]
    if missing:
        raise RegistryError(f"{pid}: missing required keys {missing}")
    if not isinstance(raw["tunable"], bool):
        raise RegistryError(f"{pid}: tunable must be true or false")
    rng = raw.get("range")
    if rng is not None:
        if not (isinstance(rng, (list, tuple)) and len(rng) == 2):
            raise RegistryError(f"{pid}: range must be [low, high] or null")
        rng = (rng[0], rng[1])
    return Parameter(id=str(pid), tag=str(raw.get("tag", "")), value=raw.get("value"), range=rng,
                     citation=str(raw.get("citation") or ""), notes=str(raw.get("notes") or ""),
                     tunable=raw["tunable"])


def resolve_citation(kind: str, name: str, root: str | Path) -> Path | None:
    """File for a ``DS/`` or ``RS/`` reference, or None. Exact name (with or without ``.md``) or a
    partial name with a date prefix that matches the start of exactly one file name."""
    d = Path(root) / LIBRARY_DIRS[kind]
    for cand in (d / name, d / f"{name}.md"):
        if cand.is_file():
            return cand
    if not DATE_PREFIX_RE.match(name):
        return None
    stem = name.removesuffix(".md")
    hits = [f for f in d.glob("*.md") if f.name.startswith(stem)] if d.is_dir() else []
    return hits[0] if len(hits) == 1 else None


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate(reg: Registry, root: str | Path | None = None) -> Registry:
    """Raise RegistryError on the first violation; return ``reg`` when valid. ``root``: project root;
    when given, every library reference in a citation must resolve to an existing file."""
    seen: set[str] = set()
    for p in reg.parameters:
        if p.id in seen:
            raise RegistryError(f"duplicate parameter id {p.id}")
        seen.add(p.id)
        if p.tag not in TAGS:
            raise RegistryError(f"{p.id}: tag {p.tag!r} not in {TAGS}")
        if p.value is None:
            raise RegistryError(f"{p.id}: value is required")
        if p.range is not None and all(_num(x) for x in p.range) and p.range[0] > p.range[1]:
            raise RegistryError(f"{p.id}: range low {p.range[0]} > high {p.range[1]}")
        if p.tag == "stated" and not p.library_refs:
            raise RegistryError(f"{p.id}: tag 'stated' requires a citation to a library file (DS/... or RS/...)")
        if p.tunable:
            if p.tag != "interpreted":
                raise RegistryError(f"{p.id}: tunable parameters must be tagged 'interpreted' (got {p.tag!r})")
            if p.range is None or not all(_num(x) for x in p.range):
                raise RegistryError(f"{p.id}: tunable parameters need a numeric range [low, high]")
            if not _num(p.value) or not p.range[0] <= p.value <= p.range[1]:
                raise RegistryError(f"{p.id}: value {p.value!r} outside range {list(p.range)}")
        if root is not None:
            for kind, name in p.library_refs:
                if resolve_citation(kind, name, root) is None:
                    raise RegistryError(f"{p.id}: citation {kind}/{name} not found under {Path(root) / LIBRARY_DIRS[kind]}")
    n = len(reg.tunable)
    if n > MAX_TUNABLE:
        raise RegistryError(f"{n} tunable interpreted parameters; cap is {MAX_TUNABLE} (PLAN E.6)")
    return reg


def loads(text: str, root: str | Path | None = None, source_path: str | None = None) -> Registry:
    doc = yaml.safe_load(text)
    if doc is None:
        doc = []
    if isinstance(doc, dict):
        version, items = int(doc.get("registry_version", 1)), doc.get("parameters") or []
    elif isinstance(doc, list):
        version, items = 1, doc
    else:
        raise RegistryError("registry must be a list of parameters or a mapping with 'parameters'")
    reg = Registry(parameters=[_parse(r) for r in items], version=version, source_path=source_path)
    return validate(reg, root)


def load(path: str | Path, root: str | Path | None = None) -> Registry:
    path = Path(path)
    return loads(path.read_text(encoding="utf-8"), root=root, source_path=str(path))


def load_default(check_citations: bool = True) -> Registry:
    """The canonical registry ``spec\\registry.yaml``, citations checked against the library."""
    return load(DEFAULT_PATH, root=project_root() if check_citations else None)


def empty() -> Registry:
    return Registry(parameters=[])
