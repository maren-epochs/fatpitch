"""Case corpus schema (PLAN E.3; PLAN_REVIEW section B).

One YAML file per case, ``cases/<YYYY-MM-DD>_<slug>.yaml``::

    id: 1992-09-16_sterling-size-up
    asof: '1992-09-16T16:00:00-04:00'   # ET close; date-only -> 16:00 ET; naive datetime = ET
    era: B                              # A (2002->, daily) | B (pre-2002, monthly)
    episode_id: EP04-1992-ERM
    truth_type: action                  # process | action
    mechanizable: no                    # yes | partial | no (YAML booleans accepted)
    source_reliability: near-primary    # primary | near-primary | secondary (library front matter)
    retrospective: true                 # optional: statement made after the decision date
    targets:
      regime_direction: null            # easing | neutral | tightening | null (policy direction)
      theses:
        - {asset_class: fx, direction: short, region: GBP}
      expression: [fx_gbp]              # target families; str or list
      action: size_up                   # enter | size_up | reduce | exit | reverse | flat | hold
      size_band: {low: 70, high: 100, unit: pct_nav}   # optional
    window: {unit: business_days, n: 20}   # default; {unit: quarters, n: 1} for 13F cases
    citation: "DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md; RS/2015-01-18_lost-tree-club-speech.md"
    date_basis: "conservative: ..."     # pinned: ... | conservative: ...  (how asof was resolved)

Vocabularies. ``asset_class``: rates | fx | equity | commodity | credit | crypto. ``region``: country or
area code for rates/equity/credit (US, GB, DE, JP, EA, BR, AR, KR); ISO currency code for fx (GBP, EUR,
USD, ...); commodity or coin code for commodity/crypto (GOLD, COPPER, OIL, BTC); omitted = any region.
Expression families: ``<asset_class>_<region lower>`` (``rates_us``, ``fx_gbp``, ``commodity_gold``,
``commodity_global``), 13F sector families ``equity_us_<sector>``.

Metadata keys (``citation``, ``date_basis``, ``retrospective``, ``seed_id``, ``notes``, ``derivation``)
are not scored and never read by engines. Outcome or hindsight fields are not allowed: any key outside
the schema is rejected. A null or absent target is not scored (unknown never counts as a fail). For
``process`` cases the targets are the stated rule's output, not the action taken; ``flat`` there means
"no new position in the target family" (e.g. the rule blocks a short or a re-entry).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from fatpitch.dates import NY, et_close, is_trading_day, shift_trading_days, trading_days
from fatpitch.decision import SizeBand

ERAS = {"A", "B"}
TRUTH_TYPES = {"process", "action"}
RELIABILITY = {"primary", "near-primary", "secondary"}
MECHANIZABLE = {"yes", "partial", "no"}
REGIME_DIRECTIONS = {"easing", "neutral", "tightening"}
ASSET_CLASSES = {"rates", "fx", "equity", "commodity", "credit", "crypto"}
DIRECTIONS = {"long", "short"}
ACTIONS = {"enter", "size_up", "reduce", "exit", "reverse", "flat", "hold"}
WINDOW_UNITS = {"business_days", "quarters"}
DATE_BASIS = ("pinned", "conservative")
CASE_KEYS = {"id", "asof", "era", "episode_id", "truth_type", "mechanizable", "source_reliability",
             "targets", "window"}
META_KEYS = {"citation", "date_basis", "retrospective", "seed_id", "notes", "derivation"}
FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_[A-Za-z0-9][A-Za-z0-9_\-]*\.ya?ml$")


class CaseError(ValueError):
    pass


@dataclass(frozen=True)
class ThesisTarget:
    asset_class: str
    direction: str
    region: str | None = None

    def matches(self, other: ThesisTarget) -> bool:
        """Class and direction must match; region only when this target names one."""
        if (self.asset_class, self.direction) != (other.asset_class, other.direction):
            return False
        return self.region is None or self.region == other.region


@dataclass(frozen=True)
class Targets:
    regime_direction: str | None = None
    theses: tuple[ThesisTarget, ...] = ()
    expression: tuple[str, ...] = ()
    action: str | None = None
    size_band: SizeBand | None = None
    tilt: tuple[tuple[str, int], ...] = ()       # 13F: (family, +1 | -1) QoQ weight-change signs

    @property
    def asset_classes(self) -> frozenset[str]:
        """Asset classes the targets name: thesis classes, else expression-family prefixes."""
        if self.theses:
            return frozenset(t.asset_class for t in self.theses)
        return frozenset(e.split("_")[0] for e in self.expression if e)


@dataclass(frozen=True)
class Window:
    unit: str = "business_days"
    n: int = 20

    def dates(self, center: _dt.date) -> list[_dt.date]:
        """NYSE trading days in the window around ``center`` (inclusive)."""
        if self.unit == "business_days":
            return trading_days(shift_trading_days(center, -self.n), shift_trading_days(center, self.n))
        lo, hi = _add_months(center, -3 * self.n), _add_months(center, 3 * self.n)
        return trading_days(lo, hi)


def _add_months(d: _dt.date, months: int) -> _dt.date:
    m = d.month - 1 + months
    y, m = d.year + m // 12, m % 12 + 1
    last = (_dt.date(y + (m == 12), m % 12 + 1, 1) - _dt.timedelta(days=1)).day
    return _dt.date(y, m, min(d.day, last))


@dataclass(frozen=True)
class Case:
    id: str
    asof: _dt.datetime
    era: str
    episode_id: str
    truth_type: str
    mechanizable: str
    source_reliability: str
    targets: Targets
    window: Window = field(default_factory=Window)
    path: str | None = None
    citation: str = ""
    date_basis: str = ""
    retrospective: bool = False
    baseline_tilt: tuple[tuple[str, int], ...] = ()

    @property
    def asof_date(self) -> _dt.date:
        return self.asof.date()

    def window_dates(self, center: _dt.date | None = None) -> list[_dt.date]:
        return self.window.dates(center or self.asof_date)


# -------------------------------------------------------------------- parsing


def _req(d: dict, key: str, cid: str):
    if key not in d or d[key] is None:
        raise CaseError(f"{cid}: missing required field '{key}'")
    return d[key]


def _one_of(v, allowed: set, name: str, cid: str):
    if v not in allowed:
        raise CaseError(f"{cid}: {name}={v!r} not in {sorted(allowed)}")
    return v


def _asof(v, cid: str) -> _dt.datetime:
    if isinstance(v, _dt.datetime):
        t = v
    elif isinstance(v, _dt.date):
        return et_close(v)
    else:
        s = str(v)
        if len(s) == 10:
            return et_close(_dt.date.fromisoformat(s))
        t = _dt.datetime.fromisoformat(s)
    return t.replace(tzinfo=NY) if t.tzinfo is None else t.astimezone(NY)


def _mech(v, cid: str) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    s = str(v).lower()
    s = {"true": "yes", "false": "no"}.get(s, s)
    if s not in MECHANIZABLE:
        raise CaseError(f"{cid}: mechanizable={v!r} must be yes|partial|no")
    return s


def _targets(d: dict, cid: str) -> Targets:
    if not isinstance(d, dict):
        raise CaseError(f"{cid}: targets must be a mapping")
    unknown = set(d) - {"regime_direction", "theses", "expression", "action", "size_band", "tilt"}
    if unknown:
        raise CaseError(f"{cid}: unknown target keys {sorted(unknown)}")
    rd = d.get("regime_direction")
    if rd is not None:
        _one_of(rd, REGIME_DIRECTIONS, "regime_direction", cid)
    theses = []
    for t in d.get("theses") or []:
        if not isinstance(t, dict):
            raise CaseError(f"{cid}: each thesis target must be a mapping")
        theses.append(ThesisTarget(asset_class=_one_of(str(_req(t, "asset_class", cid)), ASSET_CLASSES,
                                                       "asset_class", cid),
                                   direction=_one_of(_req(t, "direction", cid), DIRECTIONS, "direction", cid),
                                   region=None if t.get("region") is None else str(t["region"])))
    ex = d.get("expression")
    expr = () if ex is None else ((str(ex),) if isinstance(ex, str) else tuple(str(x) for x in ex))
    act = d.get("action")
    if act is not None:
        _one_of(act, ACTIONS, "action", cid)
    sb = d.get("size_band")
    try:
        size = SizeBand(**sb) if sb else None
    except (TypeError, ValueError) as e:
        raise CaseError(f"{cid}: size_band invalid: {e}") from e
    raw_tilt = d.get("tilt") or {}
    if not isinstance(raw_tilt, dict) or any(v not in (1, -1) or isinstance(v, bool) for v in raw_tilt.values()):
        raise CaseError(f"{cid}: tilt must map family -> +1 | -1")
    tilt = tuple(sorted((str(k), int(v)) for k, v in raw_tilt.items()))
    return Targets(regime_direction=rd, theses=tuple(theses), expression=expr, action=act, size_band=size,
                   tilt=tilt)


def _window(v, cid: str) -> Window:
    if v is None:
        return Window()
    if isinstance(v, int):
        return Window("business_days", v)
    if not isinstance(v, dict):
        raise CaseError(f"{cid}: window must be an int or {{unit, n}}")
    w = Window(_one_of(v.get("unit", "business_days"), WINDOW_UNITS, "window.unit", cid), int(v.get("n", 20)))
    if w.n < 0:
        raise CaseError(f"{cid}: window.n must be >= 0")
    return w


def _baseline_tilt(derivation, cid: str) -> tuple[tuple[str, int], ...]:
    """``derivation.prior_tilt`` (13F cases): family -> sign of the previous quarter's change (-1, 0, +1),
    computed from filings published before the case's earlier filing. Read only by the tilt baseline."""
    if not isinstance(derivation, dict) or not derivation.get("prior_tilt"):
        return ()
    pt = derivation["prior_tilt"]
    if not isinstance(pt, dict) or any(v not in (-1, 0, 1) for v in pt.values()):
        raise CaseError(f"{cid}: derivation.prior_tilt must map family -> -1 | 0 | +1")
    return tuple(sorted((str(k), int(v)) for k, v in pt.items()))


def parse_case(d: dict, path: str | None = None) -> Case:
    if not isinstance(d, dict):
        raise CaseError(f"{path}: case file must be a mapping")
    cid = str(d.get("id") or path)
    unknown = set(d) - CASE_KEYS - META_KEYS
    if unknown:
        raise CaseError(f"{cid}: unknown keys {sorted(unknown)}")
    case = Case(
        id=str(_req(d, "id", cid)),
        asof=_asof(_req(d, "asof", cid), cid),
        era=_one_of(str(_req(d, "era", cid)), ERAS, "era", cid),
        episode_id=str(_req(d, "episode_id", cid)),
        truth_type=_one_of(_req(d, "truth_type", cid), TRUTH_TYPES, "truth_type", cid),
        mechanizable=_mech(_req(d, "mechanizable", cid), cid),
        source_reliability=_one_of(_req(d, "source_reliability", cid), RELIABILITY, "source_reliability", cid),
        targets=_targets(_req(d, "targets", cid), cid),
        window=_window(d.get("window"), cid),
        path=path,
        citation=str(d.get("citation") or ""),
        date_basis=str(d.get("date_basis") or ""),
        retrospective=bool(d.get("retrospective") or False),
        baseline_tilt=_baseline_tilt(d.get("derivation"), cid),
    )
    if case.date_basis and not case.date_basis.startswith(DATE_BASIS):
        raise CaseError(f"{cid}: date_basis must start with one of {DATE_BASIS}")
    if not is_trading_day(case.asof_date):
        raise CaseError(f"{cid}: asof {case.asof_date} is not an NYSE trading day")
    return case


def load_case(path: str | Path, check_filename: bool = True) -> Case:
    path = Path(path)
    case = parse_case(yaml.safe_load(path.read_text(encoding="utf-8")), str(path))
    if check_filename:
        m = FILENAME_RE.match(path.name)
        if not m:
            raise CaseError(f"{path.name}: file name must be <YYYY-MM-DD>_<slug>.yaml")
        if m.group(1) != case.asof_date.isoformat():
            raise CaseError(f"{path.name}: file date {m.group(1)} != asof {case.asof_date}")
    return case


@dataclass(frozen=True)
class Corpus:
    """Loaded corpus. ``turning`` holds the ids of turning-point cases, derived at load time
    (``turning_point_ids``; research split: on research cases; holdout and all: on the full corpus) and
    carried unchanged into every subset. ``split``: research | holdout | all | unsplit."""

    cases: tuple[Case, ...]
    sha256: str
    root: str | None = None
    turning: frozenset[str] | None = None
    split: str = "unsplit"

    def __post_init__(self):
        if self.turning is None:
            object.__setattr__(self, "turning", turning_point_ids(self.cases))

    def __len__(self) -> int:
        return len(self.cases)

    @property
    def episodes(self) -> list[str]:
        return sorted({c.episode_id for c in self.cases})

    def is_turning(self, case: Case) -> bool:
        return case.id in self.turning

    def subset(self, turning_point: bool | None = None, **criteria) -> Corpus:
        """Cases whose attributes equal every given value, e.g. ``subset(era="A", turning_point=True)``."""
        keep = tuple(c for c in self.cases if all(getattr(c, k) == v for k, v in criteria.items())
                     and (turning_point is None or (c.id in self.turning) == turning_point))
        return Corpus(keep, self.sha256, self.root, self.turning, self.split)


TURNING_LOOKBACK_MONTHS = 18
ENTRY_ACTIONS = {"enter", "size_up"}
STANDBY_ACTIONS = {"flat", "hold"}
BREAK_ACTIONS = {"reverse", "exit"}


def turning_point_ids(cases, lookback_months: int = TURNING_LOOKBACK_MONTHS) -> frozenset[str]:
    """Turning-point cases, computed from targets and asof only (never market data or outcomes).

    Cases are ordered by (asof, id); "earlier" means a strictly earlier asof, within ``lookback_months``
    calendar months before the case. A case is a turning point when any of:

    (a) its regime target is set and differs from the regime target of the most recent earlier case
        that has a regime target;
    (b) its action target is ``reverse`` or ``exit``;
    (c) its action target is ``enter`` or ``size_up`` and the most recent earlier case that shares an
        asset class (``Targets.asset_classes``) and has an action target had ``flat`` or ``hold``.

    The first case (by asof, id) is never a turning point. Cases on the same asof are not "earlier" than
    each other. Interpretation: the 18-month lookback applies to (a) and (c); (a) compares with the most
    recent earlier case that has a regime target.
    """
    ordered = sorted(cases, key=lambda c: (c.asof, c.id))
    out: set[str] = set()
    for i, c in enumerate(ordered):
        if i == 0:
            continue
        lo = _add_months(c.asof_date, -lookback_months)
        prior = [p for p in reversed(ordered[:i]) if p.asof_date < c.asof_date and p.asof_date >= lo]
        t = c.targets
        if t.action in BREAK_ACTIONS:
            out.add(c.id)
            continue
        if t.regime_direction is not None:
            prev = next((p for p in prior if p.targets.regime_direction is not None), None)
            if prev is not None and prev.targets.regime_direction != t.regime_direction:
                out.add(c.id)
                continue
        if t.action in ENTRY_ACTIONS and t.asset_classes:
            prev = next((p for p in prior if p.targets.action is not None
                         and p.targets.asset_classes & t.asset_classes), None)
            if prev is not None and prev.targets.action in STANDBY_ACTIONS:
                out.add(c.id)
    return frozenset(out)


def corpus_sha256(files: list[Path], root: Path) -> str:
    """sha256 over sorted ``relative_path NUL file_sha256 LF`` lines."""
    h = hashlib.sha256()
    for f in sorted(files, key=lambda p: p.relative_to(root).as_posix()):
        h.update(f"{f.relative_to(root).as_posix()}\0{hashlib.sha256(f.read_bytes()).hexdigest()}\n".encode())
    return h.hexdigest()


def _load_files(files: list[Path], root: Path, check_filename: bool = True) -> list[Case]:
    cases = [load_case(f, check_filename) for f in files]
    ids = [c.id for c in cases]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise CaseError(f"duplicate case ids: {sorted(dup)}")
    cases.sort(key=lambda c: (c.asof, c.id))
    return cases


def load_corpus(root: str | Path, check_filename: bool = True, split: str = "research", unseal: bool = False,
                reason: str | None = None) -> Corpus:
    """Load a split of the corpus (``fatpitch.cases.holdout``; spec/HOLDOUT.md).

    ``split="research"`` (default): cases outside the sealed holdout episodes; turning points derived on the
    research cases only. ``split="holdout"`` / ``"all"``: require ``unseal=True``, ``FATPITCH_UNSEAL=1`` and a
    ``reason``; logged to ``UNSEAL_LOG.txt``; turning points derived on the full corpus. Every load checks the
    holdout hash against ``HOLDOUT.yaml`` and raises on a mismatch. A directory without ``HOLDOUT.yaml``
    (other than the project ``cases/``) is unsplit: research and all return every case. ``sha256`` is the hash
    of the returned files."""
    from fatpitch.cases.holdout import select

    root = Path(root)
    files, turning_files, label = select(root, split, unseal, reason)
    cases = _load_files(files, root, check_filename)
    turning = None
    if turning_files is not None:
        by_path = {c.path: c for c in cases}
        extra = [f for f in turning_files if str(f) not in by_path]
        turning = turning_point_ids(cases + _load_files(extra, root, check_filename))
    return Corpus(tuple(cases), corpus_sha256(files, root), str(root), turning, label)
