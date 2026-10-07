"""Source contract: point-in-time filter, normalisation, atomic reads, AmberSource on a fake lake.

Includes the E0 acceptance property test (randomised, no hypothesis): no row with
published_at > asof (or null published_at) is ever returned.
"""

import datetime as dt
import warnings

import numpy as np
import polars as pl
import pytest

from fatpitch.dates import NY
from fatpitch.source import COLUMNS, FRAME_SCHEMA, AmberSource, FixtureSource, PointInTimeWarning, Source

UTC = dt.UTC
BASE = dt.datetime(2000, 1, 1, tzinfo=NY)


def _random_frame(rng: np.random.Generator, n: int, null_frac: float = 0.1) -> pl.DataFrame:
    """Random vintaged series: several vintages per period, publication after period end, some nulls."""
    periods = sorted(rng.choice(3000, size=n, replace=True))
    pe = [dt.date(2000, 1, 1) + dt.timedelta(days=int(p)) for p in periods]
    lag_minutes = rng.integers(0, 60 * 24 * 120, n)
    pub = [(dt.datetime.combine(d, dt.time(13, 30), tzinfo=UTC) + dt.timedelta(minutes=int(m))).astimezone(NY)
           for d, m in zip(pe, lag_minutes, strict=True)]
    pub = [None if rng.random() < null_frac else p for p in pub]
    return pl.DataFrame({"value": rng.normal(size=n), "period_end": pe,
                         "published_at": pl.Series(pub, dtype=pl.Datetime("us", "America/New_York")),
                         "vintage_id": [f"v{i}" for i in range(n)]})


def _random_asof(rng) -> dt.datetime:
    return (BASE.astimezone(UTC) + dt.timedelta(minutes=int(rng.integers(0, 60 * 24 * 3200)))).astimezone(NY)


def _check_pit(snap: dict, raw: dict, asof: dt.datetime):
    for sid, f in snap.items():
        assert f.columns == COLUMNS
        assert f.schema == pl.Schema(FRAME_SCHEMA)
        assert f["published_at"].null_count() == 0
        assert (f["published_at"] <= asof).all(), f"{sid}: row published after asof returned"
        assert f["period_end"].is_unique().all()
        # completeness: every period with an eligible row is present, with its latest eligible value
        r = raw[sid].filter(pl.col("published_at").is_not_null() & (pl.col("published_at") <= asof))
        assert set(f["period_end"].to_list()) == set(r["period_end"].to_list())
        latest = r.sort("published_at").group_by("period_end").agg(pl.col("published_at").last())
        got = dict(zip(f["period_end"].to_list(), f["published_at"].to_list(), strict=True))
        for pe, pa in latest.iter_rows():
            assert got[pe] == pa


def test_property_fixture_source_never_returns_future_rows():
    rng = np.random.default_rng(20261006)
    for _ in range(40):
        raw = {f"S{i}": _random_frame(rng, int(rng.integers(1, 200))) for i in range(int(rng.integers(1, 5)))}
        src = FixtureSource(raw)
        for _ in range(10):
            asof = _random_asof(rng)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", PointInTimeWarning)
                _check_pit(src.snapshot(asof), raw, asof)


def _write_lake(root, frames: dict, with_published_at: bool):
    d = root / "lake" / "fred" / "series"
    d.mkdir(parents=True)
    for sid, f in frames.items():
        out = f.with_columns(pl.lit(False).alias("preliminary"),
                             pl.lit(dt.date(2026, 10, 6)).alias("as_of")).drop("vintage_id")
        if not with_published_at:
            out = out.drop("published_at")
        out.write_parquet(d / f"{sid}.parquet")


def test_property_amber_source_never_returns_future_rows(tmp_path):
    rng = np.random.default_rng(7)
    for trial in range(15):
        raw = {f"SER{i}": _random_frame(rng, int(rng.integers(1, 150))) for i in range(int(rng.integers(1, 4)))}
        root = tmp_path / f"lake{trial}"
        _write_lake(root, raw, with_published_at=True)
        src = AmberSource(root)
        for _ in range(8):
            asof = _random_asof(rng)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", PointInTimeWarning)
                snap = src.snapshot(asof)
            assert set(snap) == set(raw)
            _check_pit(snap, raw, asof)
            for f in snap.values():
                assert (f["vintage_id"] == "2026-10-06").all()      # as_of used as vintage id


def test_amber_without_published_at_excludes_all_rows_with_warning(tmp_path):
    rng = np.random.default_rng(1)
    raw = {"DGS2": _random_frame(rng, 50, null_frac=0.0)}
    _write_lake(tmp_path, raw, with_published_at=False)
    with pytest.warns(PointInTimeWarning, match="DGS2: 50 row"):
        snap = AmberSource(tmp_path).snapshot(dt.datetime(2030, 1, 1, tzinfo=NY))
    assert snap["DGS2"].is_empty()


def test_amber_root_from_env_and_series_filter(tmp_path, monkeypatch):
    rng = np.random.default_rng(2)
    _write_lake(tmp_path, {"A": _random_frame(rng, 5, 0), "B": _random_frame(rng, 5, 0)}, True)
    monkeypatch.setenv("AMBER_DATA", str(tmp_path))
    src = AmberSource(series=["B"])
    assert src.root == tmp_path
    assert list(src.snapshot(dt.datetime(2030, 1, 1, tzinfo=NY))) == ["B"]


def test_amber_snapshot_retries_then_fails_when_lake_keeps_changing(tmp_path, monkeypatch):
    rng = np.random.default_rng(3)
    _write_lake(tmp_path, {"A": _random_frame(rng, 5, 0)}, True)
    src = AmberSource(tmp_path, max_retries=2)
    calls = iter(range(100))
    monkeypatch.setattr(AmberSource, "_stamp", staticmethod(lambda files: next(calls)))
    with pytest.raises(RuntimeError, match="no consistent multi-series read"):
        src.snapshot(dt.datetime(2030, 1, 1, tzinfo=NY))


def test_asof_must_be_new_york_aware():
    src = FixtureSource({"X": pl.DataFrame({"value": [1.0], "period_end": [dt.date(2020, 1, 31)],
                                            "published_at": [dt.datetime(2020, 2, 1, tzinfo=UTC)]})})
    assert isinstance(src, Source)
    with pytest.raises(ValueError, match="America/New_York"):
        src.snapshot(dt.datetime(2020, 3, 1))  # noqa: DTZ001
    with pytest.raises(ValueError, match="America/New_York"):
        src.snapshot(dt.datetime(2020, 3, 1, tzinfo=UTC))
    with pytest.raises(TypeError):
        src.snapshot(dt.date(2020, 3, 1))


def test_filter_uses_published_at_not_period_end():
    # period ended long ago but published later: invisible before publication
    f = pl.DataFrame({"value": [1.0], "period_end": [dt.date(2020, 1, 31)],
                      "published_at": [dt.datetime(2020, 3, 15, 8, 30, tzinfo=NY)]})
    src = FixtureSource({"X": f})
    assert src.snapshot(dt.datetime(2020, 3, 15, 8, 29, tzinfo=NY))["X"].is_empty()
    assert src.snapshot(dt.datetime(2020, 3, 15, 8, 30, tzinfo=NY))["X"].height == 1


def test_revision_returns_vintage_known_at_asof():
    f = pl.DataFrame({"value": [100.0, 101.5], "period_end": [dt.date(2020, 1, 31)] * 2,
                      "published_at": [dt.datetime(2020, 2, 20, 8, 30, tzinfo=NY),
                                       dt.datetime(2020, 3, 20, 8, 30, tzinfo=NY)],
                      "vintage_id": ["first", "second"]})
    src = FixtureSource({"X": f})
    assert src.snapshot(dt.datetime(2020, 3, 1, tzinfo=NY))["X"]["vintage_id"].to_list() == ["first"]
    assert src.snapshot(dt.datetime(2020, 4, 1, tzinfo=NY))["X"]["value"].to_list() == [101.5]


def test_timestamp_normalisation_rules():
    # utc-aware -> ET; naive -> ET; date-only -> end of day ET
    f = pl.DataFrame({"value": [1.0, 2.0], "period_end": [dt.date(2020, 1, 1), dt.date(2020, 1, 2)],
                      "published_at": [dt.datetime(2020, 2, 1, 14, 0, tzinfo=UTC),
                                       dt.datetime(2020, 2, 1, 14, 0, tzinfo=UTC)]})
    out = FixtureSource({"X": f}).snapshot(dt.datetime(2020, 2, 1, 9, 0, tzinfo=NY))["X"]
    assert out.height == 2                                       # 14:00 UTC = 09:00 EST
    naive = f.with_columns(pl.col("published_at").dt.replace_time_zone(None))
    assert FixtureSource({"X": naive}).snapshot(dt.datetime(2020, 2, 1, 9, 0, tzinfo=NY))["X"].is_empty()
    dated = f.with_columns(pl.col("published_at").dt.date())
    src = FixtureSource({"X": dated})
    assert src.snapshot(dt.datetime(2020, 2, 1, 23, 59, tzinfo=NY))["X"].is_empty()
    assert src.snapshot(dt.datetime(2020, 2, 2, 0, 0, tzinfo=NY))["X"].height == 2


def test_fixture_from_csv_and_parquet_directory(tmp_path):
    (tmp_path / "CPI.csv").write_text(
        "value,period_end,published_at,vintage_id\n"
        "1.5,2020-01-31,2020-02-13T08:30:00-05:00,a\n"
        "1.6,2020-02-29,2020-03-11,b\n"
        "1.7,2020-03-31,,c\n", encoding="utf-8")
    pl.DataFrame({"value": [3.0], "period_end": [dt.date(2020, 1, 1)],
                  "published_at": [dt.datetime(2020, 1, 2, tzinfo=NY)]}).write_parquet(tmp_path / "GDP.parquet")
    src = FixtureSource(tmp_path)
    assert src.series_ids == ["CPI", "GDP"]
    with pytest.warns(PointInTimeWarning, match="CPI: 1 row"):
        snap = src.snapshot(dt.datetime(2020, 12, 31, tzinfo=NY))
    assert snap["CPI"]["value"].to_list() == [1.5, 1.6]
    assert snap["GDP"]["vintage_id"].to_list() == [None]


def test_fixture_long_format_file(tmp_path):
    p = tmp_path / "long.csv"
    p.write_text("series_id,value,period_end,published_at\nA,1,2020-01-01,2020-01-02T10:00:00\n"
                 "B,2,2020-01-01,2020-01-05T10:00:00\n", encoding="utf-8")
    snap = FixtureSource(p).snapshot(dt.datetime(2020, 1, 3, tzinfo=NY))
    assert snap["A"].height == 1 and snap["B"].is_empty()


def test_missing_required_column_raises():
    with pytest.raises(ValueError, match="missing columns"):
        FixtureSource({"X": pl.DataFrame({"value": [1.0]})})
