"""fatpitch.evaluate stub: no-pitch Decision with consumed inputs, point-in-time."""

import datetime as dt
from pathlib import Path

import polars as pl
import pytest

import fatpitch
from fatpitch import registry
from fatpitch.dates import NY
from fatpitch.decision import Decision

EXAMPLE = Path(__file__).resolve().parents[1] / "spec" / "registry.yaml"


def _src():
    return fatpitch.FixtureSource({
        "DFF": pl.DataFrame({"value": [5.25, 2.0], "period_end": [dt.date(2008, 1, 1), dt.date(2008, 9, 1)],
                             "published_at": [dt.datetime(2008, 1, 2, tzinfo=NY), dt.datetime(2008, 9, 2, tzinfo=NY)],
                             "vintage_id": ["a", "b"]}),
        "M2SL": pl.DataFrame({"value": [7.0], "period_end": [dt.date(2008, 8, 31)],
                              "published_at": [dt.datetime(2008, 9, 25, tzinfo=NY)]}),
    })


def test_stub_returns_no_pitch_with_consumed_inputs():
    asof = dt.datetime(2008, 9, 15, 16, tzinfo=NY)
    d = fatpitch.evaluate(asof, _src())
    assert isinstance(d, Decision) and d.no_pitch and d.signals == [] and d.schema_version == "2"
    assert d.engine_version == fatpitch.__version__
    assert d.registry_sha == registry.empty().sha256
    assert [c.series_id for c in d.consumed_inputs] == ["DFF"]          # M2SL not yet published
    c = d.consumed_inputs[0]
    assert (c.value, c.period_end, c.vintage_id, c.source) == (2.0, dt.date(2008, 9, 1), "b", "FixtureSource")
    assert c.published_at <= asof
    assert Decision.from_json(d.to_json()) == d


def test_registry_path_and_series_filter():
    d = fatpitch.evaluate(dt.datetime(2008, 12, 1, 16, tzinfo=NY), _src(), registry=EXAMPLE, series=["M2SL"])
    assert d.registry_sha == registry.load(EXAMPLE).sha256
    assert [c.series_id for c in d.consumed_inputs] == ["M2SL"]


def test_asof_validation():
    with pytest.raises(ValueError):
        fatpitch.evaluate(dt.datetime(2008, 9, 15, 16), _src())  # noqa: DTZ001
