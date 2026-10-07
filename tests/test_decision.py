"""Decision schema v1: validation and JSON / parquet round trips."""

import datetime as dt
import json

import pyarrow.parquet as pq
import pytest

from fatpitch import decision as d
from fatpitch.dates import NY


def _full() -> d.Decision:
    asof = dt.datetime(2022, 6, 15, 16, 0, tzinfo=NY)
    return d.Decision(
        asof=asof, engine_version="0.0.1", registry_sha="ab" * 32,
        regime=[d.RegimeVector("US", "tightening", -1.2, -0.4, -1, ["inflation"], 0.7, "risk-off"),
                d.RegimeVector("JP", "easing", 0.3, None, None, [], None, None)],
        internals=d.InternalsVector("down", 45, [d.InternalsComponent("semis_rs", "down", 30, -0.12),
                                                 d.InternalsComponent("credit", None, None, None)]),
        theses=[d.Thesis("T1", "rates", "short", "US",
                         [d.Premise("P1", "Fed behind the curve", "intact"), d.Premise("P2", "CPI > 5%")],
                         ["CPI below 4%"], ["R-INFL-01", "R-POL-02"])],
        expressions=[d.Expression("T1", "ZN", "rates_us", "short", 1, 0.9, 2.5)],
        vetoes=[d.Veto("T1", "ZN", "chart_quality", True, "trend down", "stated"),
                d.Veto("T1", "ZN", "smart_money_13f", None, "unknown", "interpreted-from-article")],
        signals=[d.Signal("SIG-2022-06-15-ZN", "T1", "ZN", "short", "starter", d.SizeBand(5.0, 10.0, "pct_nav"),
                          dt.date(2022, 7, 27), ["policy error", "trend"])],
        exits=[d.Exit("SIG-2021-01-01-X", "P9", "premise broken", dt.datetime(2022, 6, 15, 10, 0, tzinfo=NY))],
        consumed_inputs=[d.ConsumedInput("CPIAUCSL", 291.5, dt.date(2022, 5, 31),
                                         dt.datetime(2022, 6, 10, 8, 30, tzinfo=NY), "FixtureSource", "v1"),
                         d.ConsumedInput("DGS2", None, None, None, "FixtureSource")],
        no_pitch=False, nearest_misses=["long JPY: vetoed by chart"], notes=["test"])


def test_json_round_trip_full():
    x = _full()
    s = x.to_json()
    assert json.loads(s)["schema_version"] == "2"
    y = d.Decision.from_json(s)
    assert y == x
    assert y.asof.tzinfo.key == "America/New_York"
    assert isinstance(y.signals[0].size_band, d.SizeBand)
    assert y.region("JP").policy_direction == "easing"


def test_json_round_trip_empty():
    x = d.Decision(asof=dt.datetime(2020, 1, 2, 16, tzinfo=NY), engine_version="0", registry_sha="0")
    assert d.Decision.from_json(x.to_json()) == x


def test_parquet_round_trip(tmp_path):
    a, b = _full(), d.Decision(asof=dt.datetime(2020, 1, 2, 16, tzinfo=NY), engine_version="0", registry_sha="0")
    p = tmp_path / "decisions.parquet"
    d.write_parquet([a, b], p)
    back = d.read_parquet(p)
    assert back == [a, b]
    schema = pq.read_schema(p)
    assert str(schema.field("asof").type) == "timestamp[us, tz=America/New_York]"
    assert schema.field("signals").type.value_type.get_field_index("size_band") >= 0


def test_parquet_single_decision(tmp_path):
    p = tmp_path / "one.parquet"
    d.write_parquet(_full(), p)
    assert d.read_parquet(p)[0] == _full()


@pytest.mark.parametrize("ctor", [
    lambda: d.Signal("s", "t", "X", "long", "monster"),
    lambda: d.Signal("s", "t", "X", "sideways", "starter"),
    lambda: d.RegimeVector("US", "loosening"),
    lambda: d.RegimeVector("US", policy_error_sign=2),
    lambda: d.Premise("p", "x", "maybe"),
    lambda: d.Veto("t", None, "g", True, tag="guess"),
    lambda: d.SizeBand(5, 1),
    lambda: d.Decision(asof=dt.datetime(2020, 1, 1), engine_version="0", registry_sha="0"),  # noqa: DTZ001
])
def test_vocabulary_validation(ctor):
    with pytest.raises(ValueError):
        ctor()


def test_naive_datetime_in_payload_rejected():
    s = _full().to_dict()
    s["asof"] = "2022-06-15T16:00:00"
    with pytest.raises(ValueError, match="naive"):
        d.Decision.from_dict(s)
