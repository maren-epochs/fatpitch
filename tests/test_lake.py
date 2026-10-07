"""AmberLakeSource on a fake lake: point-in-time property, vintage selection, first release, proxy
flagging, splicing, ingested_at replay, lag rules, and the catalogue file itself."""

import datetime as dt
import re
import warnings
from pathlib import Path

import numpy as np
import polars as pl
import pytest

from fatpitch.dates import NY
from fatpitch.lake import (
    EXT_COLUMNS,
    EXT_SCHEMA,
    METHODS,
    AmberLakeSource,
    canonical_method,
    catalogue_ids,
    clear_cache,
    load_catalogue,
)
from fatpitch.source import PointInTimeWarning, Source

UTC = dt.UTC
REPO = Path(__file__).resolve().parents[1]


def et(y, m, d, hh=16, mm=0):
    return dt.datetime(y, m, d, hh, mm, tzinfo=NY)


def utc(y, m, d, hh=0, mm=0):
    return dt.datetime(y, m, d, hh, mm, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_cache()
    yield
    clear_cache()


def write(root: Path, rel: str, df: pl.DataFrame) -> None:
    p = root / "lake" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(p)


def series_table(rows, ingested=None):
    """rows: (period_end, value, published_at_utc, src)."""
    return pl.DataFrame(
        {
            "period_end": [r[0] for r in rows],
            "value": [float(r[1]) for r in rows],
            "preliminary": [False] * len(rows),
            "as_of": [dt.date(2026, 10, 6)] * len(rows),
            "published_at": pl.Series([r[2] for r in rows], dtype=pl.Datetime("us", "UTC")),
            "published_at_src": [r[3] for r in rows],
            "ingested_at": pl.Series(
                [ingested or utc(2026, 10, 6)] * len(rows), dtype=pl.Datetime("us", "UTC")
            ),
            "published_at_method": ["vintage" if r[3] == "alfred_first" else "lag_rule" for r in rows],
        }
    )


def alfred_table(spells):
    """spells: (period_start, realtime_start, value)."""
    return pl.DataFrame(
        {
            "date": [s[0] for s in spells],
            "realtime_start": [s[1] for s in spells],
            "realtime_end": [dt.date(9999, 12, 31)] * len(spells),
            "value": [float(s[2]) for s in spells],
        }
    )


def rtdsm_table(rows):
    """rows: (period_end, vintage, vintage_date, value)."""
    return pl.DataFrame(
        {
            "period_end": [r[0] for r in rows],
            "vintage": [r[1] for r in rows],
            "vintage_date": [r[2] for r in rows],
            "value": [float(r[3]) for r in rows],
            "published_at": pl.Series(
                [dt.datetime.combine(r[2] + dt.timedelta(days=1), dt.time(4, 59), tzinfo=UTC) for r in rows],
                dtype=pl.Datetime("us", "UTC"),
            ),
            "published_at_src": ["vintage_rule"] * len(rows),
            "ingested_at": pl.Series([utc(2026, 10, 6)] * len(rows), dtype=pl.Datetime("us", "UTC")),
            "published_at_method": ["vintage"] * len(rows),
        }
    )


# ---------------------------------------------------------------- fixtures


@pytest.fixture
def lake(tmp_path):
    """M2-like revised series: ALFRED from 1980-02-08, RTDSM from 1975-02-28, latest series file."""
    write(
        tmp_path,
        "fred/series/M2.parquet",
        series_table(
            [
                (dt.date(1970, 1, 31), 100, utc(1970, 2, 13, 21, 30), "lag_model"),
                (dt.date(1979, 12, 31), 200, utc(1980, 1, 11, 21, 30), "lag_model"),
                (dt.date(1980, 1, 31), 202, utc(1980, 2, 8, 21, 30), "alfred_first"),
                (dt.date(1980, 2, 29), 205, utc(1980, 3, 7, 21, 30), "alfred_first"),
            ]
        ),
    )
    write(
        tmp_path,
        "fred/vintages/M2.parquet",
        alfred_table(
            [
                (dt.date(1979, 12, 1), dt.date(1980, 2, 8), 198.0),  # initial ALFRED vintage
                (dt.date(1980, 1, 1), dt.date(1980, 2, 8), 201.0),
                (dt.date(1979, 12, 1), dt.date(1980, 3, 7), 199.0),  # revision of Dec published with Feb
                (dt.date(1980, 1, 1), dt.date(1980, 3, 7), 201.5),
                (dt.date(1980, 2, 1), dt.date(1980, 3, 7), 204.0),
            ]
        ),
    )
    write(
        tmp_path,
        "longhist/rtdsm/m2.parquet",
        rtdsm_table(
            [
                (dt.date(1974, 12, 31), "M275Q1", dt.date(1975, 2, 28), 150.0),
                (dt.date(1979, 11, 30), "M279Q4", dt.date(1979, 11, 30), 190.0),
                (dt.date(1974, 12, 31), "M279Q4", dt.date(1979, 11, 30), 151.0),
            ]
        ),
    )
    # proxy files and a primary that starts late
    write(
        tmp_path,
        "fred/cenb/WAL.parquet",
        pl.DataFrame(
            {
                "date": [dt.date(2003, 1, 1), dt.date(2003, 1, 8)],
                "value": [700.0, 710.0],
                "published_at": pl.Series(
                    [utc(2003, 1, 2, 21, 30), utc(2003, 1, 9, 21, 30)], dtype=pl.Datetime("us", "UTC")
                ),
                "published_at_src": ["h41_rule"] * 2,
                "published_at_method": ["release_calendar"] * 2,
            }
        ),
    )
    for name, grade in [("pd", "D"), ("pb", "B")]:
        write(
            tmp_path,
            f"proxies/{name}/{name}.parquet",
            pl.DataFrame(
                {
                    "period_end": [dt.date(1990, 1, 31), dt.date(2002, 12, 31)],
                    "value": [1.0, 2.0],
                    "published_at": pl.Series(
                        [utc(1990, 3, 1), utc(2003, 3, 1)], dtype=pl.Datetime("us", "UTC")
                    ),
                    "published_at_method": ["lag_rule"] * 2,
                    "proxy_grade": [grade] * 2,
                }
            ),
        )
    # table without published_at (CBP-style) -> lag rule
    write(
        tmp_path,
        "cbp/x/ind.parquet",
        pl.DataFrame({"date": [dt.date(1990, 1, 31), dt.date(1990, 2, 28)], "Shops": [1.5, -0.5]}),
    )
    return tmp_path


def m2_entry(**kw):
    e = {
        "step": "1",
        "freq": "M",
        "status": "available",
        "pit_method": "vintage",
        "source": {"kind": "table", "path": "fred/series/M2.parquet"},
        "vintages": [
            {
                "kind": "alfred",
                "path": "fred/vintages/M2.parquet",
                "freq": "M",
                "time_from": "fred/series/M2.parquet",
            },
            {"kind": "rtdsm", "path": "longhist/rtdsm/m2.parquet"},
        ],
        "pre_vintage": "unknown",
    }
    e.update(kw)
    return e


def catalogue(**entries):
    return {"version": "test", "series": entries}


# ---------------------------------------------------------------- vintage selection


def test_vintage_chain_alfred_then_rtdsm_then_unknown(lake):
    src = AmberLakeSource(lake, catalogue=catalogue(M2=m2_entry()))
    assert isinstance(src, Source)
    # before any vintage store: latest values, usable=False, vintage_id latest:
    f = src.snapshot(et(1975, 1, 15))["M2"]
    assert f.columns == EXT_COLUMNS and f.schema == pl.Schema(EXT_SCHEMA)
    assert f["value"].to_list() == [100.0]
    assert f["vintage_id"][0].startswith("latest:") and not f["usable"].any()
    # RTDSM era: quarterly vintage in force
    f = src.snapshot(et(1979, 6, 1))["M2"]
    assert f["vintage_id"].to_list() == ["rtdsm:M275Q1"] and f["value"].to_list() == [150.0]
    f = src.snapshot(et(1980, 1, 31))["M2"]
    assert dict(zip(f["period_end"], f["value"], strict=True)) == {
        dt.date(1974, 12, 31): 151.0,
        dt.date(1979, 11, 30): 190.0,
    }
    assert set(f["method"]) == {"vintage"} and f["usable"].all()
    # ALFRED era: released at the series' modal first-release time (16:30 ET)
    assert src.snapshot(et(1980, 2, 8, 16, 29))["M2"]["vintage_id"][0].startswith("rtdsm:")
    f = src.snapshot(et(1980, 2, 8, 16, 30))["M2"]
    assert f["value"].to_list() == [198.0, 201.0]
    assert f["published_at"][0] == et(1980, 2, 8, 16, 30)
    # revision visible only after its publication; within-vintage values
    f = src.snapshot(et(1980, 3, 7, 17))["M2"]
    assert f["value"].to_list() == [199.0, 201.5, 204.0]
    assert set(f["vintage_id"]) == {"alfred:1980-03-07"}


def test_pre_vintage_usable_policy_keeps_rows_usable(lake):
    src = AmberLakeSource(lake, catalogue=catalogue(M2=m2_entry(pre_vintage="usable")))
    f = src.snapshot(et(1975, 1, 15))["M2"]
    assert f["usable"].all() and f["vintage_id"][0].startswith("latest:")


def test_first_release_view(lake):
    cat = catalogue(M2FR=m2_entry(view="first_release", source=None, vintages=[m2_entry()["vintages"][0]]))
    f = AmberLakeSource(lake, catalogue=cat).snapshot(et(1990, 1, 1))["M2FR"]
    assert f["value"].to_list() == [198.0, 201.0, 204.0]  # earliest spell per period
    assert f["published_at"][0] == et(1980, 2, 8, 16, 30)


# ---------------------------------------------------------------- proxies and splicing


def _wal(**kw):
    e = {
        "step": "1",
        "freq": "W",
        "status": "available",
        "pit_method": "release_calendar",
        "source": {"kind": "table", "path": "fred/cenb/WAL.parquet"},
    }
    e.update(kw)
    return e


def _proxy(name, grade, splice):
    return {
        "source": {"kind": "table", "path": f"proxies/{name}/{name}.parquet", "grade_col": "proxy_grade"},
        "proxy_grade": grade,
        "splice": splice,
    }


def test_d_graded_proxy_is_flagged_unusable(lake):
    src = AmberLakeSource(lake, catalogue=catalogue(W=_wal(fallback=[_proxy("pd", "D", False)])))
    f = src.snapshot(et(1995, 1, 1))["W"]
    assert f["proxy_grade"].to_list() == ["D"] and f["usable"].to_list() == [False]
    f = src.snapshot(et(2003, 1, 3))["W"]  # primary visible -> no fallback
    assert f["proxy_grade"].to_list() == ["A"] and f["usable"].all()


def test_b_graded_splice_prepends_only_earlier_periods(lake):
    src = AmberLakeSource(lake, catalogue=catalogue(W=_wal(fallback=[_proxy("pb", "B", True)])))
    f = src.snapshot(et(2003, 6, 1))["W"]
    assert f["period_end"].to_list() == [
        dt.date(1990, 1, 31),
        dt.date(2002, 12, 31),
        dt.date(2003, 1, 1),
        dt.date(2003, 1, 8),
    ]
    assert f["proxy_grade"].to_list() == ["B", "B", "A", "A"] and f["usable"].all()
    assert (f["published_at"] <= et(2003, 6, 1)).all()


def test_fallback_by_id_overrides_grade(lake):
    cat = catalogue(
        W=_wal(fallback=[{"id": "P", "proxy_grade": "D", "splice": False}]),
        P=_wal(source={"kind": "table", "path": "proxies/pb/pb.parquet"}),
    )
    f = AmberLakeSource(lake, catalogue=cat).snapshot(et(1995, 1, 1))["W"]
    assert f["proxy_grade"].to_list() == ["D"] and not f["usable"].any()


def test_lag_rule_for_table_without_published_at(lake):
    cat = catalogue(
        S={
            "step": "1b",
            "freq": "M",
            "status": "substitute",
            "pit_method": "lag_rule",
            "proxy_grade": "D",
            "usable": False,
            "source": {
                "kind": "table",
                "path": "cbp/x/ind.parquet",
                "date_col": "date",
                "value_col": "Shops",
                "lag": {"anchor": "month_end", "days": 30, "time": "23:59:59"},
            },
        }
    )
    src = AmberLakeSource(lake, catalogue=cat)
    assert src.snapshot(et(1990, 3, 2, 12))["S"].is_empty()
    f = src.snapshot(et(1990, 3, 3, 0, 0))["S"]
    assert f["value"].to_list() == [1.5] and f["method"].to_list() == ["lag_rule"]
    assert f["published_at"][0] == dt.datetime(1990, 3, 2, 23, 59, 59, tzinfo=NY)
    assert not f["usable"].any() and f["proxy_grade"][0] == "D"


# ---------------------------------------------------------------- replay


def test_ingested_at_replay_hides_later_fix(tmp_path):
    rows = [(dt.date(2020, 1, 31), 1.0, utc(2020, 2, 14, 13, 30), "lag_model")]
    first = series_table(rows, ingested=utc(2021, 1, 1))
    fix = series_table(
        [
            (dt.date(2020, 1, 31), 1.25, utc(2020, 2, 14, 13, 30), "lag_model"),
            (dt.date(2020, 2, 29), 2.0, utc(2020, 3, 13, 13, 30), "lag_model"),
        ],
        ingested=utc(2022, 6, 1),
    )
    write(tmp_path, "fred/series/X.parquet", pl.concat([first, fix]))
    cat = catalogue(
        X={
            "step": "1",
            "freq": "M",
            "status": "available",
            "pit_method": "lag_rule",
            "source": {"kind": "table", "path": "fred/series/X.parquet"},
        }
    )
    asof = et(2023, 1, 3)
    live = AmberLakeSource(tmp_path, catalogue=cat).snapshot(asof)["X"]
    assert live["value"].to_list() == [1.25, 2.0]
    replay = AmberLakeSource(tmp_path, catalogue=cat, run_time=et(2021, 6, 1)).snapshot(asof)["X"]
    assert replay["value"].to_list() == [1.0]
    with pytest.raises(ValueError):
        AmberLakeSource(tmp_path, catalogue=cat, run_time=dt.datetime(2021, 6, 1))  # noqa: DTZ001


def test_replay_vintage_store_uses_meta_fetch_date(lake):
    (lake / "lake/fred/vintages/M2.meta.json").write_text('{"fetched": "2026-10-06"}', encoding="utf-8")
    src = AmberLakeSource(lake, catalogue=catalogue(M2=m2_entry()), run_time=et(2026, 10, 1))
    f = src.snapshot(et(1990, 1, 1))["M2"]
    # no store was in the lake on 2026-10-01 (ALFRED, RTDSM and the series file all ingested later)
    assert f.is_empty()
    f = AmberLakeSource(lake, catalogue=catalogue(M2=m2_entry()), run_time=et(2026, 10, 7)).snapshot(
        et(1990, 1, 1)
    )
    assert f["M2"]["vintage_id"][0].startswith("alfred:")


# ---------------------------------------------------------------- property test


def _random_lake(root: Path, rng: np.random.Generator, n_series: int) -> dict:
    entries, raw = {}, {}
    for i in range(n_series):
        n = int(rng.integers(5, 120))
        months = sorted({int(x) for x in rng.integers(0, 240, n)})
        spells = []
        for mth in months:
            start = dt.date(2000 + mth // 12, mth % 12 + 1, 1)
            for _ in range(int(rng.integers(1, 4))):
                rs = start + dt.timedelta(days=int(rng.integers(20, 3000)))
                spells.append((start, rs, float(rng.normal())))
        write(root, f"fred/vintages/S{i}.parquet", alfred_table(spells))
        tab = series_table(
            [
                (
                    dt.date(2000 + m // 12, m % 12 + 1, 28),
                    0.0,
                    None
                    if rng.random() < 0.1
                    else utc(2000 + m // 12, m % 12 + 1, 28) + dt.timedelta(days=int(rng.integers(1, 90))),
                    "lag_model",
                )
                for m in months
            ]
        )
        write(root, f"fred/series/S{i}.parquet", tab)
        entries[f"S{i}"] = {
            "step": "1",
            "freq": "M",
            "status": "available",
            "pit_method": "vintage",
            "source": {"kind": "table", "path": f"fred/series/S{i}.parquet"},
            "vintages": [
                {
                    "kind": "alfred",
                    "path": f"fred/vintages/S{i}.parquet",
                    "freq": "M",
                    "release_time": "08:30",
                }
            ],
            "pre_vintage": "unknown",
        }
        raw[f"S{i}"] = spells
    return catalogue(**entries) | {"_raw": raw}


def test_property_lake_source_never_returns_future_rows(tmp_path):
    rng = np.random.default_rng(20261007)
    for trial in range(8):
        root = tmp_path / f"t{trial}"
        cat = _random_lake(root, rng, int(rng.integers(1, 4)))
        raw = cat.pop("_raw")
        src = AmberLakeSource(root, catalogue=cat)
        for _ in range(12):
            asof = (
                utc(2000, 1, 1) + dt.timedelta(minutes=int(rng.integers(0, 60 * 24 * 365 * 30)))
            ).astimezone(NY)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", PointInTimeWarning)
                snap = src.snapshot(asof)
            for sid, f in snap.items():
                assert f.schema == pl.Schema(EXT_SCHEMA)
                assert f["published_at"].null_count() == 0
                assert (f["published_at"] <= asof).all(), f"{sid}: future row"
                assert f["period_end"].is_unique().all()
                assert set(f["method"]).issubset(METHODS)
                first_vintage = min(dt.datetime.combine(s[1], dt.time(8, 30), tzinfo=NY) for s in raw[sid])
                if asof >= first_vintage:
                    # brute-force as-of vintage
                    want = {}
                    for start, rs, v in sorted(raw[sid], key=lambda s: s[1]):
                        if dt.datetime.combine(rs, dt.time(8, 30), tzinfo=NY) <= asof:
                            pe = dt.date(
                                start.year + start.month // 12, start.month % 12 + 1, 1
                            ) - dt.timedelta(days=1)
                            want[pe] = v
                    got = dict(zip(f["period_end"], f["value"], strict=True))
                    assert got == pytest.approx(want)
                    assert f["usable"].all()
                else:
                    assert not f["usable"].any()


# ---------------------------------------------------------------- misc


def test_lake_change_during_load_raises(lake, monkeypatch):
    import fatpitch.lake as lk

    calls = iter(range(10_000))
    monkeypatch.setattr(lk, "_stamp", lambda files: next(calls))
    with pytest.raises(RuntimeError, match="consistent"):
        AmberLakeSource(lake, catalogue=catalogue(M2=m2_entry()), max_retries=2).snapshot(et(1990, 1, 1))


def test_unknown_series_and_naive_asof_rejected(lake):
    src = AmberLakeSource(lake, catalogue=catalogue(M2=m2_entry()))
    with pytest.raises(KeyError):
        src.snapshot(et(1990, 1, 1), series=["NOPE"])
    with pytest.raises(ValueError):
        src.snapshot(dt.datetime(1990, 1, 1))  # noqa: DTZ001


@pytest.mark.parametrize(
    "method,src,want",
    [
        ("vintage", "alfred_first", "first_release"),
        ("lag_rule", "lag_model", "lag_rule"),
        ("release_calendar", "h41_rule", "release_calendar"),
        ("unknown", "cftc_release_rule", "release_calendar"),
        ("fetch_time", "fetch_cap", "fetch_time"),
        ("vintage", "vintage_rule", "vintage"),
        (None, None, "lag_rule"),
        ("lag_rule", "interpreted", "lag_rule"),
    ],
)
def test_canonical_method(method, src, want):
    assert canonical_method(method, src) == want


# ---------------------------------------------------------------- the catalogue file

PROCESS_IDS = [
    "M2SL",
    "INDPRO",
    "WALCL",
    "WTREGEN",
    "RRPONTSYD",
    "TREAST",
    "WSHOMCB",
    "FEDFUNDS",
    "DFF",
    "DFEDTARU",
    "CPIAUCSL",
    "CPIAUCNS",
    "CPILFESL",
    "UNRATE",
    "NROU",
    "GDP",
    "DGS1",
    "DGS2",
    "DGS10",
    "GS10",
    "TB3MS",
    "BAA",
    "AAA",
    "BAMLH0A0HYM2",
    "NFCI",
    "DCOILWTICO",
    "WTISPLC",
    "USD_BROAD",
    "DTWEXBGS",
    "DTWEXM",
    "ECBASSETSW",
    "JPNASSETS",
    "BOE_ASSETS",
    "FRENCH49",
    "ZWEIG_EMA10",
    "RITTER_UNPROF_IPO",
    "SIFMA_HY_SHARE_A",
    "BCNSDODNS",
    "FINRA_MARGIN_DEBT",
    "TFD_DEBT_HELD_PUBLIC",
    "FYGFDPUN",
    "FYFSGDA188S",
    "COT_6E",
    "NBER_CYCLES",
    "DEXUSUK",
    "DEXJPUS",
    *[f"IRLTLT01{c}M156N" for c in ["US", "DE", "GB", "JP", "FR", "IT"]],
]


def test_catalogue_file_is_well_formed():
    cat = load_catalogue(REPO / "spec" / "data_catalogue.yaml")
    series = cat["series"]
    for sid in PROCESS_IDS:
        assert sid in series, sid
    for sid, e in series.items():
        assert e["status"] in {"available", "partial", "substitute", "proxy_only", "missing"}, sid
        assert str(e["step"]) in {"1", "1b", "later", "label"}, sid
        assert e["pit_method"] in METHODS, sid
        if e["status"] == "missing":
            assert not e.get("source") and not e.get("vintages"), sid
        else:
            assert e.get("source") or e.get("vintages") or e.get("fallback"), sid
        for fb in e.get("fallback") or []:
            assert fb.get("proxy_grade") in {"A", "B", "C", "D"}, sid
            if "id" in fb:
                assert fb["id"] in series, sid
        if e.get("revised") and e.get("vintages"):
            assert (
                e.get("pre_vintage", "unknown") in {"unknown", "usable"} or e.get("view") == "first_release"
            )
    assert set(catalogue_ids(cat, step="1")) <= set(series)
    # every FRED-style id named in process.md Inputs lines is catalogued (or an alias is)
    text = (REPO / "spec" / "process.md").read_text(encoding="utf-8")
    named = set(re.findall(r"`([A-Z][A-Z0-9]{3,}(?:[A-Z0-9]*))`", text))
    aliases = {"DTWEXBGS", "DTWEXM"}
    skip = {"WSJ", "S000004310"}  # N-PORT series id of the SPX holdings (breadth input, not a series)
    missing = sorted(n for n in named - skip - aliases if n not in series and not n.startswith("IRLTLT01"))
    assert missing == [], missing
