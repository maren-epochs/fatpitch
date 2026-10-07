"""Catalogue-driven point-in-time source over amber's parquet lake (PLAN 0.2, D).

``AmberLakeSource(root).snapshot(asof)`` returns ``{series_id: frame}`` for the ids in
``spec\\data_catalogue.yaml``. Frame columns, in order:

    value         Float64
    period_end    Date
    published_at  Datetime(us, America/New_York)   never null; always <= asof
    vintage_id    Utf8      store-qualified: ``alfred:<realtime_start>``, ``rtdsm:<vintage>``,
                            ``lake:<fetch date>``; prefix ``latest:`` = latest-revision values
                            used before any vintage store exists (see ``pre_vintage``)
    method        Utf8      vintage | first_release | release_calendar | lag_rule | fetch_time
    proxy_grade   Utf8      A native; B/C/D per library\\research\\data_practices.md 4.2
    usable        Boolean   False for D-graded proxies and for pre-vintage rows whose catalogue
                            policy is ``unknown``; rules must treat such rows as unknown

The first four columns are the ``fatpitch.source`` contract; the rest are appended.

Rules (in addition to ``fatpitch.source``):

* Revised series with a vintage store are read from the store in force at ``asof``: ALFRED when
  ``asof`` is on or after its first vintage, else the Philadelphia Fed RTDSM when on or after its
  first vintage, else the lake's latest-revision series (``pre_vintage`` policy). One store per
  frame, so growth rates are computed within one vintage.
* ``view: first_release`` keeps, per period, the earliest published value across the chain.
* Replay: ``run_time`` (tz-aware) additionally drops rows with ``ingested_at > run_time`` before the
  as-of vintage is chosen, so a past run can be reproduced after a data fix.
* Fallbacks: ``splice: true`` prepends fallback rows for periods before the first visible primary
  period; ``splice: false`` uses the fallback only when the primary has no visible row at ``asof``.
* Loaded files are cached per process (key: path, mtime, size, read spec). A snapshot reads only
  memory after the first load, so every series in it comes from one consistent read.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import warnings
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl
import yaml

from fatpitch.dates import require_et
from fatpitch.source import DEFAULT_AMBER_DATA, FRAME_SCHEMA, TZ, PointInTimeWarning

EXT_SCHEMA: dict[str, pl.DataType] = {
    **FRAME_SCHEMA,
    "method": pl.Utf8(),
    "proxy_grade": pl.Utf8(),
    "usable": pl.Boolean(),
}
EXT_COLUMNS = list(EXT_SCHEMA)
METHODS = ("vintage", "first_release", "release_calendar", "lag_rule", "fetch_time")
CATALOGUE_PATH = Path(__file__).resolve().parents[2] / "spec" / "data_catalogue.yaml"
_INF = np.iinfo(np.int64).max
_EPOCH = _dt.datetime(1970, 1, 1, tzinfo=_dt.UTC)
_INTERNAL = [
    "value",
    "period_end",
    "published_at",
    "vintage_id",
    "method",
    "proxy_grade",
    "usable",
    "ingested_at",
]

_RELEASE_SRC = {
    "h41_rule",
    "release_calendar",
    "effective_date",
    "cftc_release_rule",
    "nber_announcement",
    "release_rule",
    "dttp_release_rule",
    "after_close_rule",
    "eod_conservative",
    "derived",
}


def canonical_method(method: str | None, src: str | None) -> str:
    """Map amber's ``published_at_method`` / ``published_at_src`` labels onto the five methods."""
    m, s = (method or "").strip(), (src or "").strip()
    if s in ("alfred_first", "alfred_initial_vintage"):
        return "first_release"
    if s == "vintage_rule":
        return "vintage"
    if "fetch" in s or m == "fetch_time":
        return "fetch_time"
    if m == "vintage":  # one row per period stamped with its ALFRED first release
        return "first_release"
    if m in ("release_calendar", "lag_rule"):
        return m
    if s in _RELEASE_SRC:
        return "release_calendar"
    return "lag_rule"


def _us(t: _dt.datetime) -> int:
    """tz-aware datetime -> int64 microseconds since the Unix epoch (UTC)."""
    d = t - _EPOCH
    return (d.days * 86_400 + d.seconds) * 1_000_000 + d.microseconds


# ---------------------------------------------------------------- catalogue


def load_catalogue(path: str | Path | None = None) -> dict:
    with open(path or CATALOGUE_PATH, encoding="utf-8") as fh:
        cat = yaml.safe_load(fh)
    if not isinstance(cat, dict) or "series" not in cat:
        raise ValueError("catalogue: top-level 'series' mapping required")
    return cat


def catalogue_ids(
    catalogue: dict | None = None, step: str | Iterable[str] | None = None, include_missing: bool = False
) -> list[str]:
    """Ids in the catalogue, optionally restricted to a process step ('1', '1b', 'later', 'label')."""
    cat = catalogue or load_catalogue()
    steps = None if step is None else ({step} if isinstance(step, str) else set(step))
    out = []
    for sid, e in cat["series"].items():
        if steps is not None and str(e.get("step")) not in steps:
            continue
        if not include_missing and e.get("status") == "missing":
            continue
        out.append(sid)
    return out


# ---------------------------------------------------------------- reading


PROJECT_ROOT = CATALOGUE_PATH.parents[1]
SPEC_KINDS = ("spec_events", "spec_events_rate", "spec_events_sep")
SPEC_EVENT_STATES = {"EXPAND": -1.0, "NONE": 0.0, "RUNOFF": 1.0}  # R-14 sign convention: -1 easing, +1 tightening


def _spec_files(spec: dict) -> list[Path]:
    """Files of a ``kind: spec_events`` source: paths relative to the project root, not the lake."""
    p = PROJECT_ROOT / Path(spec["path"])
    return [p] if p.exists() else []


def read_spec_events_sep(path: Path, flt: dict | None) -> pl.DataFrame:
    """``kind: spec_events_sep`` (``spec/fomc_sep_events.yaml``: one row per release x variable x statistic x
    horizon) -> internal long format for one ``variable`` and ``statistic`` (the catalogue entry's ``filter``;
    optional ``horizon_year`` restricts the years). Period = 31 December of ``horizon_year``, so the as-of view
    keeps, per projection year, the latest release published at asof; longer-run rows (``LR``) have no period
    and are dropped. ``published_at`` (ET) is the release time. Without a ``variable``/``statistic`` filter
    the rows of different statistics would collide on one period, so the result is empty."""
    flt = flt or {}
    ing = _file_ingested(path)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = []
    if flt.get("variable") and flt.get("statistic"):
        years = flt.get("horizon_year")
        years = None if years is None else {int(y) for y in (years if isinstance(years, list) else [years])}
        for r in doc.get("events") or []:
            if str(r["variable"]) != flt["variable"] or str(r["statistic"]) != flt["statistic"]:
                continue
            h = str(r["horizon_year"])
            if not h.isdigit() or (years is not None and int(h) not in years):
                continue
            rows.append(r)
    pub = [_dt.datetime.fromisoformat(str(r["published_at"])).replace(tzinfo=None) for r in rows]
    return pl.DataFrame({
        "value": [float(r["value"]) for r in rows],
        "period_end": [_dt.date(int(r["horizon_year"]), 12, 31) for r in rows],
        "published_at": pl.Series(pub, dtype=pl.Datetime("us")).dt.replace_time_zone(TZ),
        "vintage_id": [f"spec:{doc.get('version', '')}:{r['meeting']}" for r in rows],
        "method": ["release_calendar"] * len(rows),
        "ingested_at": pl.Series([ing] * len(rows), dtype=pl.Datetime("us", "UTC")),
    }, schema={**{c: t for c, t in EXT_SCHEMA.items() if c not in ("proxy_grade", "usable")},
               "ingested_at": pl.Datetime("us", "UTC")})


def read_spec_events(path: Path, kind: str = "spec_events") -> pl.DataFrame:
    """Event table in the project's ``spec`` folder -> internal long format. ``announced`` (ET) is the
    publication time; ``effective`` is the period. Value: ``state`` mapped through ``SPEC_EVENT_STATES``
    (``kind: spec_events``) or the ``rate`` column (``kind: spec_events_rate``)."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = doc.get("events") or []
    ing = _file_ingested(path)
    pub = [_dt.datetime.fromisoformat(str(r["announced"])).replace(tzinfo=None) for r in rows]
    return pl.DataFrame({
        "value": [float(r["rate"]) if kind == "spec_events_rate" else SPEC_EVENT_STATES[str(r["state"]).upper()]
                  for r in rows],
        "period_end": [_dt.date.fromisoformat(str(r["effective"])[:10]) for r in rows],
        "published_at": pl.Series(pub, dtype=pl.Datetime("us")).dt.replace_time_zone(TZ),
        "vintage_id": [f"spec:{doc.get('version', '')}"] * len(rows),
        "method": ["release_calendar"] * len(rows),
        "ingested_at": pl.Series([ing] * len(rows), dtype=pl.Datetime("us", "UTC")),
    }, schema={**{c: t for c, t in EXT_SCHEMA.items() if c not in ("proxy_grade", "usable")},
               "ingested_at": pl.Datetime("us", "UTC")})


def _files(root: Path, rel: str) -> list[Path]:
    p = root / Path(rel)
    if any(ch in rel for ch in "*?["):
        return sorted(p.parent.glob(p.name))
    return [p] if p.exists() else []


def _stamp(files: list[Path]) -> tuple:
    out = []
    for f in files:
        st = f.stat()
        out.append((str(f), st.st_mtime_ns, st.st_size))
    return tuple(out)


def _file_ingested(f: Path) -> _dt.datetime:
    """Lake knowledge time of a file without an ``ingested_at`` column: meta.json fetch date (end of
    that day, ET) when present, else the file mtime."""
    meta = f.with_name(f.name.split(".")[0] + ".meta.json")
    if meta.exists():
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
            d = m.get("fetched") or m.get("pit_fetched") or m.get("built")
            if d:
                d = str(d)[:10]
                return _dt.datetime.combine(
                    _dt.date.fromisoformat(d), _dt.time(23, 59, 59, 999999), tzinfo=_dt.UTC
                ).astimezone(_dt.UTC)
        except (ValueError, OSError):
            pass
    return _dt.datetime.fromtimestamp(f.stat().st_mtime, tz=_dt.UTC)


def _ts_col(s: pl.Expr, dtype) -> pl.Expr:
    if isinstance(dtype, pl.Datetime):
        e = s.cast(pl.Datetime("us", dtype.time_zone))
        return e.dt.replace_time_zone(TZ) if dtype.time_zone is None else e.dt.convert_time_zone(TZ)
    if dtype == pl.Date:
        return (
            s.cast(pl.Datetime("us")) + pl.duration(days=1) - pl.duration(microseconds=1)
        ).dt.replace_time_zone(TZ)
    raise TypeError(f"unsupported timestamp dtype {dtype}")


def _hhmm(t: str | None) -> tuple[int, int, int]:
    if not t:
        return 23, 59, 59
    parts = [int(x) for x in str(t).split(":")]
    return (parts + [0, 0])[0], (parts + [0, 0])[1], (parts + [0, 0, 0])[2]


def _lag_expr(date: pl.Expr, lag: dict) -> pl.Expr:
    anchor = date.dt.month_end() if lag.get("anchor") == "month_end" else date
    h, m, s = _hhmm(lag.get("time"))
    return (
        anchor.cast(pl.Datetime("us"))
        + pl.duration(days=int(lag.get("days", 0)), hours=h, minutes=m, seconds=s)
    ).dt.replace_time_zone(TZ)


def _period_end_from_start(date: pl.Expr, freq: str) -> pl.Expr:
    f = (freq or "D").upper()[0]
    if f == "M":
        return date.dt.month_end()
    if f == "Q":
        return date.dt.offset_by("2mo").dt.month_end()
    if f == "A":
        return pl.date(date.dt.year(), 12, 31)
    return date


def _release_time(root: Path, rel: str | None, default: str | None) -> tuple[int, int, int]:
    """Modal ET time of day of ALFRED first-release stamps in the lake series file (used to time an
    ALFRED vintage date); falls back to ``default`` or end of day."""
    if default:
        return _hhmm(default)
    files = _files(root, rel) if rel else []
    if files:
        df = pl.read_parquet(files[0])
        if "published_at" in df.columns and "published_at_src" in df.columns:
            t = df.filter(pl.col("published_at_src") == "alfred_first").select(
                _ts_col(pl.col("published_at"), df.schema["published_at"]).dt.time().alias("t")
            )
            if t.height:
                mode = t["t"].mode().sort()[0]
                return mode.hour, mode.minute, mode.second
    return 23, 59, 59


def read_source(root: Path, spec: dict) -> pl.DataFrame:
    """Read one catalogue source into the internal long format (``_INTERNAL`` columns, minus grade and
    usable which the caller sets). Rows without a publication time are dropped with a warning."""
    kind = spec.get("kind", "table")
    if kind in SPEC_KINDS:
        files = _spec_files(spec)
        if not files:
            return _empty_internal()
        if kind == "spec_events_sep":
            return read_spec_events_sep(files[0], spec.get("filter"))
        return read_spec_events(files[0], kind)
    files = _files(root, spec["path"])
    if not files:
        return _empty_internal()
    frames = []
    for f in files:
        if spec.get("filter") and kind == "table":
            lf = pl.scan_parquet(f)
            for c, v in spec["filter"].items():
                lf = lf.filter(pl.col(c) == v)
            df = lf.collect()
        else:
            df = pl.read_parquet(f)
        ing_default = _file_ingested(f)
        if "ingested_at" in df.columns and isinstance(df.schema["ingested_at"], pl.Datetime):
            ing = (
                _ts_col(pl.col("ingested_at"), df.schema["ingested_at"])
                .dt.convert_time_zone("UTC")
                .fill_null(pl.lit(ing_default).cast(pl.Datetime("us", "UTC")))
            )
        else:
            ing = pl.lit(ing_default).cast(pl.Datetime("us", "UTC"))
        if kind == "alfred":
            hh, mm, ss = _release_time(root, spec.get("time_from"), spec.get("release_time"))
            out = df.select(
                pl.col("value").cast(pl.Float64),
                _period_end_from_start(pl.col("date"), spec.get("freq", "D")).alias("period_end"),
                (
                    pl.col("realtime_start").cast(pl.Datetime("us"))
                    + pl.duration(hours=hh, minutes=mm, seconds=ss)
                )
                .dt.replace_time_zone(TZ)
                .alias("published_at"),
                (pl.lit("alfred:") + pl.col("realtime_start").cast(pl.Utf8)).alias("vintage_id"),
                pl.lit("vintage").alias("method"),
                ing.alias("ingested_at"),
            )
        elif kind == "rtdsm":
            out = df.select(
                pl.col("value").cast(pl.Float64),
                pl.col("period_end").cast(pl.Date),
                _ts_col(pl.col("published_at"), df.schema["published_at"]).alias("published_at"),
                (pl.lit("rtdsm:") + pl.col("vintage").cast(pl.Utf8)).alias("vintage_id"),
                pl.lit("vintage").alias("method"),
                ing.alias("ingested_at"),
            )
        else:
            out = _read_table(df, spec, ing)
        frames.append(out)
    out = pl.concat(frames, how="vertical_relaxed") if len(frames) > 1 else frames[0]
    out = out.filter(pl.col("value").is_not_null() & pl.col("value").is_not_nan())
    nulls = out["published_at"].null_count()
    if nulls:
        warnings.warn(
            f"{spec['path']}: {nulls} row(s) without published_at excluded (point-in-time rule)",
            PointInTimeWarning,
            stacklevel=2,
        )
        out = out.filter(pl.col("published_at").is_not_null())
    return out


def _read_table(df: pl.DataFrame, spec: dict, ing: pl.Expr) -> pl.DataFrame:
    cols = df.columns
    if spec.get("year_col"):
        date = pl.date(pl.col(spec["year_col"]).cast(pl.Int32), 12, 31)
    else:
        dcol = spec.get("date_col") or ("period_end" if "period_end" in cols else "date")
        date = pl.col(dcol)
        if df.schema[dcol] == pl.Utf8:
            date = date.str.to_date()
        elif isinstance(df.schema[dcol], pl.Datetime):
            date = date.dt.date()
    if spec.get("value_map"):
        vm = spec["value_map"]
        value = pl.col(vm["col"]).replace_strict(vm["map"], default=None, return_dtype=pl.Float64)
    else:
        value = pl.col(spec.get("value_col", "value")).cast(pl.Float64)
    lag = spec.get("lag")
    if "published_at" in cols and not (lag and lag.get("force")):
        pub = _ts_col(pl.col("published_at"), df.schema["published_at"])
        meth = pl.col("published_at_method") if "published_at_method" in cols else pl.lit(None, pl.Utf8)
        src = pl.col("published_at_src") if "published_at_src" in cols else pl.lit(None, pl.Utf8)
        key = meth.cast(pl.Utf8).fill_null("") + pl.lit("|") + src.cast(pl.Utf8).fill_null("")
        keys = df.select(key.alias("k"))["k"].unique().to_list()
        mapping = {k: canonical_method(*k.split("|", 1)) for k in keys}
        method = key.replace_strict(mapping, return_dtype=pl.Utf8)
    elif lag:
        pub, method = _lag_expr(date, lag), pl.lit("lag_rule")
    else:
        pub, method = pl.lit(None, pl.Datetime("us", TZ)), pl.lit("lag_rule")
    vcol = spec.get("vintage_col") or ("as_of" if "as_of" in cols else None)
    vin = (
        (pl.lit("lake:") + pl.col(vcol).cast(pl.Utf8))
        if vcol
        else (pl.lit("lake:") + ing.dt.date().cast(pl.Utf8))
    )
    exprs = [
        value.alias("value"),
        date.cast(pl.Date).alias("period_end"),
        pub.alias("published_at"),
        vin.alias("vintage_id"),
        method.alias("method"),
        ing.alias("ingested_at"),
    ]
    if spec.get("grade_col") and spec["grade_col"] in cols:
        exprs.append(pl.col(spec["grade_col"]).cast(pl.Utf8).alias("_grade"))
    elif spec.get("grade_by") and spec["grade_by"]["col"] in cols:
        gb = spec["grade_by"]
        exprs.append(
            pl.col(gb["col"])
            .cast(pl.Utf8)
            .replace_strict(gb["map"], default=None, return_dtype=pl.Utf8)
            .alias("_grade")
        )
    if spec.get("unusable_if") and spec["unusable_if"] in cols:
        exprs.append(pl.col(spec["unusable_if"]).fill_null(False).alias("_unusable"))
    return df.select(exprs)


def _empty_internal() -> pl.DataFrame:
    return pl.DataFrame(schema={**EXT_SCHEMA, "ingested_at": pl.Datetime("us", "UTC")}).drop(
        ["proxy_grade", "usable"]
    )


def _empty_frame() -> pl.DataFrame:
    return pl.DataFrame(schema=EXT_SCHEMA)


# ---------------------------------------------------------------- prepared stores


@dataclass
class _Store:
    """Rows of one source for one usage, sorted by (period_end, published_at). A row is visible at
    ``asof`` iff ``published_at <= asof < superseded_at`` (the next publication of the same period),
    which is the as-of vintage without a sort or group-by per call."""

    df: pl.DataFrame
    first_release: bool = False
    _views: dict = field(default_factory=dict)

    def view(self, run_us: int | None) -> tuple[pl.DataFrame, np.ndarray, np.ndarray]:
        key = run_us
        v = self._views.get(key)
        if v is None:
            df = self.df
            if run_us is not None:
                ing = df["ingested_at"].to_physical().to_numpy()
                df = df.filter(pl.Series(ing <= run_us))
            if self.first_release:
                df = df.sort(["period_end", "published_at"]).unique(
                    subset=["period_end"], keep="first", maintain_order=True
                )
            pub = df["published_at"].to_physical().to_numpy().astype(np.int64, copy=False)
            pe = df["period_end"].to_physical().to_numpy()
            sup = np.full(len(pub), _INF, dtype=np.int64)
            if len(pub) > 1 and not self.first_release:
                same = pe[1:] == pe[:-1]
                sup[:-1] = np.where(same, pub[1:], _INF)
            out = df.select(EXT_COLUMNS)
            v = (out, pub, sup)
            if len(self._views) > 16:
                self._views.clear()
            self._views[key] = v
        return v

    def first_pub(self, run_us: int | None) -> int:
        _, pub, _ = self.view(run_us)
        return int(pub.min()) if len(pub) else _INF

    def visible(self, asof_us: int, run_us: int | None) -> pl.DataFrame:
        df, pub, sup = self.view(run_us)
        idx = np.flatnonzero((pub <= asof_us) & (sup > asof_us))
        n = len(idx)
        if n == 0:
            return df.clear()
        if idx[-1] - idx[0] + 1 == n:  # contiguous (typical for unrevised series): zero-copy slice
            return df.slice(int(idx[0]), n)
        return df[idx]


def _prepare(raw: pl.DataFrame, grade: str, usable: bool, first_release: bool = False) -> _Store:
    g = pl.col("_grade").fill_null(grade) if "_grade" in raw.columns else pl.lit(grade)
    u = pl.lit(usable)
    if "_unusable" in raw.columns:
        u = u & ~pl.col("_unusable")
    df = (
        raw.with_columns(g.alias("proxy_grade"))
        .with_columns((u & (pl.col("proxy_grade") != "D")).alias("usable"))
        .select(_INTERNAL)
        .sort(["period_end", "published_at"], maintain_order=True)
    )
    df = df.with_columns(pl.col(c).cast(t) for c, t in EXT_SCHEMA.items())
    return _Store(df=df, first_release=first_release)


# ---------------------------------------------------------------- source


_RAW_CACHE: dict[tuple, pl.DataFrame] = {}


def clear_cache() -> None:
    _RAW_CACHE.clear()


class AmberLakeSource:
    """Point-in-time ``Source`` over amber's lake, driven by ``spec\\data_catalogue.yaml``.

    ``series``: ids returned by ``snapshot`` (default: every catalogue id with data).
    ``run_time``: replay cut-off on ``ingested_at`` (tz-aware); None = no cut-off.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        series: Iterable[str] | None = None,
        catalogue: dict | str | Path | None = None,
        run_time: _dt.datetime | None = None,
        max_retries: int = 3,
    ):
        base = Path(root or os.environ.get("AMBER_DATA") or DEFAULT_AMBER_DATA)
        self.root = base / "lake" if (base / "lake").is_dir() else base
        self.catalogue = catalogue if isinstance(catalogue, dict) else load_catalogue(catalogue)
        self.entries: dict = self.catalogue["series"]
        self.series = list(series) if series is not None else catalogue_ids(self.catalogue)
        unknown = [s for s in self.series if s not in self.entries]
        if unknown:
            raise KeyError(f"series not in catalogue: {unknown}")
        if run_time is not None and (run_time.tzinfo is None or run_time.utcoffset() is None):
            raise ValueError("run_time must be tz-aware")
        self.run_time = run_time
        self.max_retries = max_retries
        self._stores: dict[tuple, _Store] = {}
        self._raw: dict[str, pl.DataFrame] = {}
        self._ready: set[str] = set()

    # ---- loading

    def _specs_for(self, sid: str, seen: set | None = None) -> list[dict]:
        seen = seen or set()
        if sid in seen:
            raise ValueError(f"catalogue: fallback cycle at {sid}")
        seen.add(sid)
        e = self.entries[sid]
        out = []
        if e.get("source"):
            out.append(e["source"])
        out += list(e.get("vintages") or [])
        for fb in e.get("fallback") or []:
            if "id" in fb:
                out += self._specs_for(fb["id"], set(seen))
            elif "source" in fb:
                out.append(fb["source"])
        return out

    @staticmethod
    def _key(spec: dict) -> str:
        return json.dumps(spec, sort_keys=True, default=str)

    def _load(self, ids: list[str]) -> None:
        specs = {}
        for sid in ids:
            for sp in self._specs_for(sid):
                specs[self._key(sp)] = sp
        todo = {}
        for k, sp in specs.items():
            files = _spec_files(sp) if sp.get("kind") in SPEC_KINDS else _files(self.root, sp["path"])
            extra = _files(self.root, sp["time_from"]) if sp.get("time_from") else []
            todo[k] = (sp, files + extra)
        for _ in range(self.max_retries):
            before = {k: _stamp(fs) for k, (_, fs) in todo.items()}
            got = {}
            for k, (sp, _) in todo.items():
                ck = (k, before[k])
                if ck not in _RAW_CACHE:
                    _RAW_CACHE[ck] = read_source(self.root, sp)
                got[k] = _RAW_CACHE[ck]
            if all(_stamp(fs) == before[k] for k, (_, fs) in todo.items()):
                self._raw.update(got)
                return
        raise RuntimeError(f"amber lake changed during {self.max_retries} load attempts; no consistent read")

    def _store(self, spec: dict, grade: str, usable: bool, first_release: bool = False) -> _Store:
        key = (self._key(spec), grade, usable, first_release)
        st = self._stores.get(key)
        if st is None:
            st = _prepare(self._raw[self._key(spec)], grade, usable, first_release)
            self._stores[key] = st
        return st

    def reload(self) -> None:
        """Drop this source's prepared stores; the next snapshot re-stats files and re-reads changes."""
        self._stores.clear()
        self._raw = {}
        self._ready = set()

    # ---- resolution

    def _primary(self, sid: str, a: int, r: int | None) -> pl.DataFrame:
        e = self.entries[sid]
        grade = str(e.get("proxy_grade", "A"))
        usable = bool(e.get("usable", True))
        vins = e.get("vintages") or []
        if e.get("view") == "first_release":
            parts = [self._store(v, grade, usable, first_release=True).visible(a, r) for v in vins]
            if not parts:
                return _empty_frame()
            df = pl.concat(parts).sort(["period_end", "published_at"])
            return df.unique(subset=["period_end"], keep="first", maintain_order=True)
        for v in vins:
            st = self._store(v, grade, usable)
            if st.first_pub(r) <= a:
                return st.visible(a, r)
        if not e.get("source"):
            return _empty_frame()
        df = self._store(e["source"], grade, usable).visible(a, r)
        if vins and df.height:
            pol = e.get("pre_vintage", "unknown")
            df = df.with_columns(
                (pl.lit("latest:") + pl.col("vintage_id")).alias("vintage_id"),
                (pl.col("usable") & pl.lit(pol == "usable")).alias("usable"),
            )
        return df

    def _resolve(self, sid: str, a: int, r: int | None) -> pl.DataFrame:
        df = self._primary(sid, a, r)
        for fb in self.entries[sid].get("fallback") or []:
            if fb.get("splice") is False and df.height:
                break
            if "id" in fb:
                part = self._resolve(fb["id"], a, r)
                g = fb.get("proxy_grade")
                if g is not None and part.height:
                    part = part.with_columns(
                        pl.lit(str(g)).alias("proxy_grade"),
                        (pl.col("usable") & pl.lit(str(g) != "D")).alias("usable"),
                    )
            else:
                part = self._store(
                    fb["source"], str(fb.get("proxy_grade", "D")), bool(fb.get("usable", True))
                ).visible(a, r)
            if not part.height:
                continue
            if df.height and fb.get("splice", False):
                part = part.filter(pl.col("period_end") < df["period_end"].min())
                df = pl.concat([part, df])
            elif not df.height:
                df = part
        return df

    # ---- public

    def snapshot(self, asof: _dt.datetime, series: Iterable[str] | None = None) -> dict[str, pl.DataFrame]:
        require_et(asof)
        ids = list(series) if series is not None else self.series
        unknown = [s for s in ids if s not in self.entries]
        if unknown:
            raise KeyError(f"series not in catalogue: {unknown}")
        need = [s for s in ids if s not in self._ready]
        if need:
            need = [s for s in need if any(self._key(sp) not in self._raw for sp in self._specs_for(s))]
            if need:
                self._load(need)
            self._ready.update(ids)
        a = _us(asof)
        r = _us(self.run_time) if self.run_time is not None else None
        return {sid: self._resolve(sid, a, r) for sid in sorted(ids)}
