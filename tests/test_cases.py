"""Case schema, corpus hash, scoring rule, aggregation, nulls and permutation test (synthetic cases)."""

import datetime as dt
from dataclasses import dataclass, field

import polars as pl
import pytest
import yaml

from fatpitch.cases import (
    AlwaysRiskOn,
    CaseError,
    FedDirectionOnly,
    Persistence,
    Prediction,
    ScoringRule,
    ThesisTarget,
    Trend12m,
    aggregate,
    default_nulls,
    load_case,
    load_corpus,
    margin_over_best_null,
    parse_case,
    permutation_test,
    run,
    score_case,
)
from fatpitch.cases.scoring import CaseScore
from fatpitch.dates import NY, shift_trading_days
from fatpitch.source import FixtureSource


def _case(cid="c1", asof="2008-09-15", episode="gfc", era="A", truth="action", mech="yes", rel="primary",
          targets=None, window=None) -> dict:
    d = {"id": cid, "asof": asof, "era": era, "episode_id": episode, "truth_type": truth, "mechanizable": mech,
         "source_reliability": rel,
         "targets": targets if targets is not None else {
             "regime_direction": "tightening", "theses": [{"asset_class": "rates", "direction": "long", "region": "US"}],
             "expression": ["rates_us"], "action": "enter"}}
    if window is not None:
        d["window"] = window
    return d


def _write(root, d: dict, name: str | None = None):
    p = root / (name or f"{d['asof']}_{d['id']}.yaml")
    p.write_text(yaml.safe_dump(d), encoding="utf-8")
    return p


@dataclass
class ScheduleEngine:
    """Synthetic engine: prediction by date from a function; records every asof it is asked about."""

    fn: object
    name: str = "schedule"
    seen: list = field(default_factory=list)

    def predict(self, asof, source):
        self.seen.append(asof)
        return self.fn(asof.date())


# -------------------------------------------------------------------- schema


def test_parse_valid_case_and_defaults():
    c = parse_case(_case())
    assert c.asof == dt.datetime(2008, 9, 15, 16, 0, tzinfo=NY)
    assert c.mechanizable == "yes" and c.window.unit == "business_days" and c.window.n == 20
    assert c.targets.theses == (ThesisTarget("rates", "long", "US"),)
    days = c.window_dates()
    assert len(days) == 41 and days[20] == dt.date(2008, 9, 15)


def test_yaml_booleans_and_string_expression(tmp_path):
    d = _case(mech="no")
    d["targets"]["expression"] = "rates_us"
    p = tmp_path / "2008-09-15_c1.yaml"
    p.write_text(yaml.safe_dump(d).replace("mechanizable: 'no'", "mechanizable: no"), encoding="utf-8")
    c = load_case(p)
    assert c.mechanizable == "no" and c.targets.expression == ("rates_us",)


@pytest.mark.parametrize("mech", ["yes", "partial", "no"])
def test_mechanizable_three_levels_and_new_vocab(mech):
    d = _case(mech=mech, rel="near-primary")
    d["targets"]["action"] = "size_up"
    d.update(citation="DS/x.md", date_basis="pinned: note date", retrospective=True, seed_id="C99", notes="n")
    c = parse_case(d)
    assert c.mechanizable == mech and c.source_reliability == "near-primary" and c.targets.action == "size_up"
    assert c.retrospective is True and c.date_basis.startswith("pinned") and c.citation == "DS/x.md"


def test_ten_year_equivalent_size_unit():
    d = _case()
    d["targets"]["size_band"] = {"low": 300, "high": 350, "unit": "pct_nav_10y_eq"}
    assert parse_case(d).targets.size_band.unit == "pct_nav_10y_eq"


def test_quarter_window_for_13f():
    c = parse_case(_case(window={"unit": "quarters", "n": 1}))
    days = c.window_dates()
    assert days[0] >= dt.date(2008, 6, 15) and days[-1] <= dt.date(2008, 12, 15) and len(days) > 120


@pytest.mark.parametrize("mut,msg", [
    (lambda d: d.update(era="C"), "era"),
    (lambda d: d.pop("episode_id"), "episode_id"),
    (lambda d: d.update(truth_type="vibes"), "truth_type"),
    (lambda d: d.update(mechanizable="maybe"), "mechanizable"),
    (lambda d: d["targets"].update(theses=[{"asset_class": "stocks", "direction": "long"}]), "asset_class"),
    (lambda d: d["targets"].update(action="cash"), "action"),
    (lambda d: d["targets"].update(regime_direction="risk_off"), "regime_direction"),
    (lambda d: d.update(source_reliability="tertiary"), "source_reliability"),
    (lambda d: d.update(date_basis="guessed"), "date_basis"),
    (lambda d: d.update(source_reliability="blog"), "source_reliability"),
    (lambda d: d.update(asof="2008-09-13"), "not an NYSE trading day"),
    (lambda d: d["targets"].update(regime_direction="up"), "regime_direction"),
    (lambda d: d["targets"].update(action="buy"), "action"),
    (lambda d: d["targets"].update(theses=[{"asset_class": "fx", "direction": "up"}]), "direction"),
    (lambda d: d["targets"].update(size_band={"low": 5, "high": 1}), "size_band"),
    (lambda d: d.update(outcome_return=0.3), "unknown keys"),
])
def test_validation_errors(mut, msg):
    d = _case()
    mut(d)
    with pytest.raises(CaseError, match=msg):
        parse_case(d)


def test_filename_rules(tmp_path):
    with pytest.raises(CaseError, match="file date"):
        load_case(_write(tmp_path, _case(), "2008-09-16_c1.yaml"))
    with pytest.raises(CaseError, match="file name"):
        load_case(_write(tmp_path, _case(), "gfc.yaml"))


def test_corpus_load_sha_and_duplicates(tmp_path):
    _write(tmp_path, _case("a", "2008-09-15"))
    _write(tmp_path, _case("b", "2003-06-25", episode="fed-2003"))
    c1 = load_corpus(tmp_path)
    assert [c.id for c in c1.cases] == ["b", "a"] and c1.episodes == ["fed-2003", "gfc"]
    assert load_corpus(tmp_path).sha256 == c1.sha256
    _write(tmp_path, _case("b", "2003-06-25", episode="fed-2003", rel="secondary"))
    assert load_corpus(tmp_path).sha256 != c1.sha256
    _write(tmp_path, _case("b", "2003-06-26", episode="x"))
    with pytest.raises(CaseError, match="duplicate"):
        load_corpus(tmp_path)


# -------------------------------------------------------------------- scoring


def test_regime_exact_window_miss():
    c = parse_case(_case())
    center = c.asof_date
    exact = ScheduleEngine(lambda d: Prediction("tightening"))
    near = ScheduleEngine(lambda d: Prediction("tightening" if d == shift_trading_days(center, 5) else "easing"))
    far = ScheduleEngine(lambda d: Prediction("tightening" if d == shift_trading_days(center, 21) else "easing"))
    for eng, want in ((exact, 1.0), (near, 0.5), (far, 0.0)):
        assert run(eng, [c]).case_scores[0].regime == want


def test_thesis_fraction_region_and_expression_topk_and_action():
    t = {"regime_direction": None,
         "theses": [{"asset_class": "rates", "direction": "long", "region": "US"},
                    {"asset_class": "fx", "direction": "short"}],
         "expression": ["fx_gbp"], "action": "exit"}
    c = parse_case(_case(targets=t))
    p = Prediction(None, (ThesisTarget("rates", "long", "DE"), ThesisTarget("fx", "short", "GB")),
                   ("equity_us", "rates_us", "gold_global", "fx_gbp"), "exit")
    s = run(ScheduleEngine(lambda d: p), [c]).case_scores[0]
    assert s.regime is None                       # no target: not scored
    assert s.thesis == 0.5                        # region mismatch on rates; fx matches (no region in target)
    assert s.expression == 0.0                    # fx_gbp is rank 4
    assert s.action == 1.0
    s2 = score_case(c, lambda d: p, ScoringRule(expression_top_k=4))
    assert s2.expression == 1.0


def test_aggregate_is_episode_first():
    scores = [CaseScore(f"a{i}", "A", 1.0, None, None, None) for i in range(3)] + \
             [CaseScore("b", "B", 0.0, None, None, None)]
    agg = aggregate(scores)
    assert agg["regime"] == 0.5 and agg["thesis"] is None


def test_breakdown_dimensions():
    cases = [parse_case(_case("a", era="A", mech="yes")),
             parse_case(_case("b", asof="1992-09-16", episode="erm", era="B", mech="no", truth="process",
                              rel="secondary"))]
    res = run(AlwaysRiskOn(), cases)
    assert set(res.breakdown) == {"era", "source_reliability", "truth_type", "mechanizable", "turning_point"}
    assert set(res.breakdown["mechanizable"]) == {"yes", "no"}
    assert res.n_cases == 2 and res.n_episodes == 2
    assert res.overall["regime"] == 0.0           # targets risk_off, null says risk_on


def test_engine_called_only_with_et_close_asof():
    c = parse_case(_case())
    eng = ScheduleEngine(lambda d: Prediction())
    run(eng, [c])
    assert all(a.tzinfo.key == "America/New_York" and a.hour == 16 for a in eng.seen)
    assert len(eng.seen) == len(set(eng.seen)) == 41          # cached per date


# -------------------------------------------------------------------- nulls


def _fixture(series: dict[str, list[tuple[str, float]]]) -> FixtureSource:
    frames = {}
    for sid, rows in series.items():
        pe = [dt.date.fromisoformat(d) for d, _ in rows]
        frames[sid] = pl.DataFrame({"value": [v for _, v in rows], "period_end": pe,
                                    "published_at": [dt.datetime.combine(p, dt.time(17), tzinfo=NY) for p in pe]})
    return FixtureSource(frames)


def test_fed_direction_null():
    src = _fixture({"FEDFUNDS": [("2007-06-01", 5.25), ("2008-09-01", 2.0)]})
    p = FedDirectionOnly().predict(dt.datetime(2008, 9, 15, 16, tzinfo=NY), src)
    assert p.regime_direction == "easing" and ThesisTarget("rates", "long", "US") in p.theses
    up = _fixture({"FEDFUNDS": [("2004-01-01", 1.0), ("2004-09-01", 1.75)]})
    assert FedDirectionOnly().predict(dt.datetime(2004, 9, 15, 16, tzinfo=NY), up).regime_direction == "tightening"
    assert FedDirectionOnly().predict(dt.datetime(2004, 9, 15, 16, tzinfo=NY), _fixture({})) == Prediction()


def test_fed_direction_null_respects_publication_time():
    # the cut is published after asof: invisible
    src = _fixture({"FEDFUNDS": [("2007-06-01", 5.25), ("2008-03-01", 5.25)]})
    late = FixtureSource({"FEDFUNDS": pl.concat([src.snapshot(dt.datetime(2030, 1, 1, tzinfo=NY))["FEDFUNDS"],
                                            pl.DataFrame({"value": [2.0], "period_end": [dt.date(2008, 9, 1)],
                                                          "published_at": [dt.datetime(2008, 9, 20, tzinfo=NY)],
                                                          "vintage_id": [None]},
                                                         schema_overrides={"published_at": pl.Datetime("us", "America/New_York"),
                                                                           "vintage_id": pl.Utf8})])})
    p = FedDirectionOnly().predict(dt.datetime(2008, 9, 15, 16, tzinfo=NY), late)
    assert p.regime_direction == "neutral"


def test_trend_null():
    src = _fixture({"SPY": [("2007-09-14", 150.0), ("2008-09-12", 120.0)],
                    "IEF": [("2007-09-14", 85.0), ("2008-09-12", 92.0)]})
    p = Trend12m().predict(dt.datetime(2008, 9, 15, 16, tzinfo=NY), src)
    assert p.regime_direction == "easing"                            # IEF up = yields down
    assert p.theses[0] == ThesisTarget("equity", "short", "US")       # |-20%| ranks above |+8%|
    assert p.expressions == ("equity_us", "rates_us")


def test_persistence_never_sees_own_case():
    cases = [parse_case(_case("a", "2003-06-25", episode="e1", targets={"regime_direction": "easing"})),
             parse_case(_case("b", "2008-09-15", episode="e2", targets={"regime_direction": "tightening"}))]
    null = Persistence(cases)
    res = run(null, cases)
    assert res.case_scores[0].regime is not None and res.case_scores[0].regime == 0.0
    assert res.case_scores[1].regime == 0.0                         # predicts e1's risk_on
    assert null.predict(dt.datetime(2003, 7, 1, 16, tzinfo=NY), None) == Prediction()


def test_default_nulls_and_margin():
    cases = [parse_case(_case())]
    results = [run(n, cases, source=_fixture({})) for n in default_nulls(cases)]
    assert [r.engine for r in results] == ["null_always_risk_on", "null_fed_direction", "null_trend_12m",
                                           "null_persistence"]
    perfect = run(ScheduleEngine(lambda d: Prediction("tightening")), cases)
    assert margin_over_best_null(perfect, results, "regime") == 1.0


# -------------------------------------------------------------------- permutation


def _spread_cases(n=12):
    start = dt.date(2003, 1, 2)
    out = []
    for i in range(n):
        d = shift_trading_days(start, i * 120)
        out.append(parse_case(_case(f"c{i}", d.isoformat(), episode=f"e{i}",
                                    targets={"regime_direction": "tightening" if i % 2 else "easing"})))
    return out


def test_permutation_detects_date_specific_skill():
    cases = _spread_cases()
    truth = {c.asof_date: c.targets.regime_direction for c in cases}

    def fn(d):
        near = min(truth, key=lambda t: abs((t - d).days))
        return Prediction(truth[near])

    res = permutation_test(ScheduleEngine(fn), cases, component="regime", n_perm=200)
    assert res.observed == 1.0 and res.p_value < 0.05


def test_permutation_constant_engine_not_significant():
    res = permutation_test(AlwaysRiskOn(), _spread_cases(), component="regime", n_perm=100)
    assert res.p_value == 1.0
    with pytest.raises(ValueError):
        permutation_test(AlwaysRiskOn(), _spread_cases(), component="size", n_perm=1)
