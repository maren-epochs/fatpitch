"""Point-in-time data sources (PLAN 0.2 contract).

``Source.snapshot(asof)`` returns ``{series_id: frame}``. Frame columns, in order:

    value         Float64
    period_end    Date
    published_at  Datetime(us, America/New_York)   never null in a returned frame
    vintage_id    Utf8 (nullable)

Rules:

* ``asof`` must be a tz-aware datetime in America/New_York.
* Filter is ``published_at <= asof``; ``period_end`` is never used to decide availability.
* Rows with null ``published_at`` are never returned (a warning names the series).
* Per ``period_end`` the most recently published row at ``asof`` is kept (the as-of vintage).
* Atomic: every series in one snapshot comes from one consistent read at one ``asof``.

Timestamp normalisation, package-wide: tz-aware values are converted to America/New_York; naive
datetimes are read as America/New_York; date-only values are read as 23:59:59.999999 ET of that
date (conservative: a same-day release is not visible before the end of the day).
"""

from __future__ import annotations

import datetime as _dt
import os
import warnings
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol, runtime_checkable

import polars as pl

from fatpitch.dates import NY, require_et

TZ = "America/New_York"
FRAME_SCHEMA: dict[str, pl.DataType] = {
    "value": pl.Float64(),
    "period_end": pl.Date(),
    "published_at": pl.Datetime("us", TZ),
    "vintage_id": pl.Utf8(),
}
COLUMNS = list(FRAME_SCHEMA)
DEFAULT_AMBER_DATA = Path.home() / "Documents" / "amber" / "data"


class PointInTimeWarning(UserWarning):
    """Rows were excluded because their publication time is unknown."""


@runtime_checkable
class Source(Protocol):
    def snapshot(self, asof: _dt.datetime) -> dict[str, pl.DataFrame]: ...


# ---------------------------------------------------------------- normalisation


def _to_et(col: pl.Series) -> pl.Series:
    """Normalise a published_at column of any supported dtype to Datetime(us, ET)."""
    dt = col.dtype
    if dt == pl.Null:
        return pl.Series(col.name, [None] * len(col), dtype=FRAME_SCHEMA["published_at"])
    if dt == pl.Utf8:
        vals = [_parse_ts(v) for v in col.to_list()]
        return pl.Series(col.name, vals, dtype=pl.Datetime("us", TZ))
    if dt == pl.Date:
        s = col.cast(pl.Datetime("us")) + _dt.timedelta(days=1) - _dt.timedelta(microseconds=1)
        return s.dt.replace_time_zone(TZ)
    if isinstance(dt, pl.Datetime):
        s = col.cast(pl.Datetime("us", dt.time_zone))
        return s.dt.replace_time_zone(TZ) if dt.time_zone is None else s.dt.convert_time_zone(TZ)
    raise TypeError(f"unsupported published_at dtype {dt}")


def _parse_ts(v) -> _dt.datetime | None:
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    s = str(v).strip()
    if len(s) == 10:
        d = _dt.date.fromisoformat(s)
        return _dt.datetime.combine(d, _dt.time(23, 59, 59, 999999), tzinfo=NY)
    t = _dt.datetime.fromisoformat(s)
    return t.replace(tzinfo=NY) if t.tzinfo is None else t.astimezone(NY)


def normalize_frame(df: pl.DataFrame, series_id: str = "?") -> pl.DataFrame:
    """Coerce a raw frame to FRAME_SCHEMA. Missing ``published_at`` -> null (excluded later);
    missing ``vintage_id`` -> null."""
    missing = {"value", "period_end"} - set(df.columns)
    if missing:
        raise ValueError(f"series {series_id}: missing columns {sorted(missing)}")
    n = df.height
    period_end = df["period_end"]
    if period_end.dtype == pl.Utf8:
        period_end = period_end.str.to_date()
    elif isinstance(period_end.dtype, pl.Datetime):
        period_end = period_end.dt.date()
    pub = _to_et(df["published_at"]) if "published_at" in df.columns else \
        pl.Series("published_at", [None] * n, dtype=FRAME_SCHEMA["published_at"])
    vin = df["vintage_id"].cast(pl.Utf8) if "vintage_id" in df.columns else \
        pl.Series("vintage_id", [None] * n, dtype=pl.Utf8)
    return pl.DataFrame({
        "value": df["value"].cast(pl.Float64),
        "period_end": period_end.cast(pl.Date),
        "published_at": pub.alias("published_at"),
        "vintage_id": vin.alias("vintage_id"),
    })


def as_of_view(frame: pl.DataFrame, asof: _dt.datetime, series_id: str = "?",
               warn_null: bool = True) -> pl.DataFrame:
    """Apply the point-in-time rule to one normalised frame."""
    nulls = frame["published_at"].null_count()
    if nulls and warn_null:
        warnings.warn(f"series {series_id}: {nulls} row(s) have no published_at and were excluded "
                      f"(point-in-time rule)", PointInTimeWarning, stacklevel=3)
    cutoff = pl.lit(asof).cast(pl.Datetime("us", TZ))
    out = frame.filter(pl.col("published_at").is_not_null() & (pl.col("published_at") <= cutoff))
    out = (out.sort(["period_end", "published_at"])
              .unique(subset=["period_end"], keep="last", maintain_order=True)
              .sort("period_end"))
    return out.select(COLUMNS)


# ---------------------------------------------------------------- fixture source


def _read_any(path: Path) -> pl.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pl.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pl.read_csv(path, infer_schema_length=0)  # all text; normalised explicitly
    raise ValueError(f"unsupported fixture file {path}")


def _csv_types(df: pl.DataFrame) -> pl.DataFrame:
    if "value" in df.columns and df["value"].dtype == pl.Utf8:
        df = df.with_columns(pl.col("value").replace("", None).cast(pl.Float64))
    return df


class FixtureSource:
    """Source over fixtures: a dict of frames, a directory of ``<series_id>.parquet|.csv`` files,
    or a single long-format file with a ``series_id`` column. Data is loaded once at construction."""

    def __init__(self, data: Mapping[str, pl.DataFrame] | str | Path):
        self._frames: dict[str, pl.DataFrame] = {}
        if isinstance(data, Mapping):
            raw = dict(data)
        else:
            p = Path(data)
            raw = {}
            files = sorted(p.glob("*.parquet")) + sorted(p.glob("*.csv")) if p.is_dir() else [p]
            for f in files:
                df = _csv_types(_read_any(f))
                if "series_id" in df.columns:
                    for (sid,), g in df.group_by(["series_id"], maintain_order=True):
                        raw[str(sid)] = g.drop("series_id")
                else:
                    raw[f.stem] = df
        for sid, df in raw.items():
            self._frames[sid] = normalize_frame(df, sid)

    @property
    def series_ids(self) -> list[str]:
        return sorted(self._frames)

    def snapshot(self, asof: _dt.datetime) -> dict[str, pl.DataFrame]:
        require_et(asof)
        return {sid: as_of_view(f, asof, sid) for sid, f in sorted(self._frames.items())}


# ---------------------------------------------------------------- amber source


class AmberSource:
    """Read-only view of amber's parquet lake. Implemented: FRED series files
    ``<AMBER_DATA>\\lake\\fred\\series\\<SERIES_ID>.parquet``.

    Amber files carry ``period_end, value, preliminary, as_of`` today; ``as_of`` is the fetch date,
    not the publication time, so it is used only as ``vintage_id``. Until the data lift adds a
    ``published_at`` column, every row has null ``published_at`` and is excluded with a warning.
    """

    def __init__(self, root: str | Path | None = None, series: list[str] | None = None,
                 max_retries: int = 3):
        self.root = Path(root or os.environ.get("AMBER_DATA") or DEFAULT_AMBER_DATA)
        self.series = series
        self.max_retries = max_retries

    @property
    def fred_dir(self) -> Path:
        return self.root / "lake" / "fred" / "series"

    def _files(self) -> list[Path]:
        files = sorted(self.fred_dir.glob("*.parquet"))
        if self.series is not None:
            want = set(self.series)
            files = [f for f in files if f.stem in want]
        return files

    @staticmethod
    def _stamp(files: list[Path]) -> tuple:
        return tuple((f.name, f.stat().st_mtime_ns, f.stat().st_size) for f in files)

    def _read(self, files: list[Path]) -> dict[str, pl.DataFrame]:
        out = {}
        for f in files:
            df = pl.read_parquet(f)
            if "vintage_id" not in df.columns and "as_of" in df.columns:
                df = df.with_columns(pl.col("as_of").cast(pl.Utf8).alias("vintage_id"))
            out[f.stem] = normalize_frame(df, f.stem)
        return out

    def snapshot(self, asof: _dt.datetime) -> dict[str, pl.DataFrame]:
        require_et(asof)
        for _ in range(self.max_retries):
            files = self._files()
            before = self._stamp(files)
            frames = self._read(files)
            if self._stamp(self._files()) == before:
                return {sid: as_of_view(f, asof, sid) for sid, f in sorted(frames.items())}
        raise RuntimeError(f"amber lake changed during {self.max_retries} snapshot attempts; "
                           "no consistent multi-series read")
