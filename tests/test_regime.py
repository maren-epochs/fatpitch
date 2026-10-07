"""Regime-stage evaluation, option B (fatpitch.cases.regime; owner decision 2026-10-07, spec/scoring.md 6c)."""

import datetime as dt
import itertools

import numpy as np
import pytest
import yaml

from fatpitch.cases import AlwaysRiskOn, parse_case
from fatpitch.cases import regime as rg
from fatpitch.dates import et_close, shift_trading_days, trading_days
from fatpitch.decision import Decision, RegimeVector
from fatpitch.versions.adapter import decision_to_prediction


def _case(cid, asof, regime, episode, era="A"):
    return parse_case({"id": cid, "asof": asof, "era": era, "episode_id": episode, "truth_type": "action",
                       "mechanizable": "yes", "source_reliability": "primary",
                       "targets": {"regime_direction": regime}})


# -------------------------------------------------------------------- probabilities


def test_floor_and_normalisation():
    assert rg.floor_probs((0.9, 0.05, 0.05)) == pytest.approx((0.9, 0.05, 0.05))      # valid: unchanged
    p = rg.floor_probs((1.0, 0.0, 0.0))
    assert min(p) >= rg.EPS - 1e-12 and sum(p) == pytest.approx(1.0)
    assert p == pytest.approx((0.98, 0.01, 0.01))
    assert sum(rg.floor_probs((2, 1, 1))) == pytest.approx(1.0)                       # renormalised
    q = rg.floor_probs((0.985, 0.0095, 0.0055))                                       # clip, rescale, re-check
    assert min(q) >= rg.EPS - 1e-12 and sum(q) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        rg.floor_probs((0.5, -0.1, 0.6))


def test_deterministic_null_probabilities():
    assert rg.deterministic_probs("tightening") == pytest.approx((0.05, 0.05, 0.9))
    assert rg.deterministic_probs(None) is None
    p = AlwaysRiskOn().predict(et_close(dt.date(2015, 3, 2)), None)
    assert p.regime_probs == pytest.approx((0.9, 0.05, 0.05))


# -------------------------------------------------------------------- RPS


def test_rps_values():
    assert rg.rps((1, 0, 0), "easing") == 0.0
    assert rg.rps((0, 0, 1), "easing") == 1.0
    assert rg.rps((0, 1, 0), "easing") == pytest.approx(0.5)          # one ordinal step away
    # hand computation: F = (0.6, 0.9), O for tightening = (0, 0): (0.36 + 0.81) / 2
    assert rg.rps((0.6, 0.3, 0.1), "tightening") == pytest.approx((0.36 + 0.81) / 2)
    assert rg.worst_rps("easing") == rg.worst_rps("tightening") == 1.0
    assert rg.worst_rps("neutral") == 0.5
    assert rg.score_rps(None, "easing") == 1.0
    assert rg.score_rps((1, 0, 0), "easing") == pytest.approx(rg.rps((0.98, 0.01, 0.01), "easing"))


def test_loeo_climatology_excludes_own_episode():
    cases = [_case("a", "2015-03-02", "easing", "E1"), _case("b", "2016-03-02", "easing", "E1"),
             _case("c", "2017-03-02", "tightening", "E2")]
    # scoring E1: only E2's tightening counts -> (0+1, 0+1, 1+1) / (1+3)
    assert rg.loeo_climatology(cases, "E1") == pytest.approx((0.25, 0.25, 0.5))
    # scoring E2: two easing -> (3, 1, 1) / 5
    assert rg.loeo_climatology(cases, "E2") == pytest.approx((0.6, 0.2, 0.2))


def test_exact_sign_flip_enumeration():
    d = [0.3, 0.1, -0.05, 0.2]
    obs = np.mean(d)
    brute = np.mean([np.mean(np.array(s) * d) >= obs - 1e-12 for s in itertools.product((-1, 1), repeat=4)])
    assert rg.exact_sign_flip_p(d) == pytest.approx(brute)
    assert rg.exact_sign_flip_p([0.1] * 8) == pytest.approx(1 / 256)
    assert rg.exact_sign_flip_p([0.1, 0.1, 0.0]) == pytest.approx(2 / 8)    # a tie: both of its signs count
    assert rg.exact_sign_flip_p([0.0, 0.0]) == 1.0


DATES5 = ("2010-03-02", "2011-03-02", "2012-03-02", "2013-03-04", "2014-03-03")


def _mixed_cases():
    cases = [_case(f"c{i}", d, "easing", f"E{i}") for i, d in enumerate(DATES5)]
    return cases + [_case("t", "2015-03-02", "tightening", "E5")]


def _refs(cases):
    return {"climatology_loeo": rg.case_rps(cases, lambda c: rg.loeo_climatology(cases, c.episode_id)),
            "null_trend_12m": rg.case_rps(cases, lambda c: (0.6, 0.2, 0.2)),
            "null_always_risk_on": rg.case_rps(cases, lambda c: rg.deterministic_probs("easing"))}


def test_regime_gate_requires_every_reference_and_bayes_factor():
    cases = _mixed_cases()
    refs = _refs(cases)
    good = rg.case_rps(cases, lambda c: (0.97, 0.02, 0.01) if c.targets.regime_direction == "easing"
                       else (0.01, 0.02, 0.97))
    g = rg.regime_gate(good, refs)
    assert g.k == 6 and g.passed and g.every_reference_pass and g.min_attainable_p == 1 / 64
    for r in g.references.values():
        assert r.wins == 6 and r.p_value == pytest.approx(1 / 64) and r.skill > 0
    assert g.tightening["n"] == 1 and g.tightening["passed"] and g.tightening["low_power"]
    # an engine that beats climatology and trend but not the constant majority forecast fails
    mid = rg.case_rps(cases, lambda c: (0.85, 0.1, 0.05))
    g2 = rg.regime_gate(mid, refs)
    assert g2.references["null_always_risk_on"].p_value >= 0.10 and not g2.passed   # loses 5 of 6 episodes
    assert g2.binding_reference == "null_always_risk_on"
    assert rg.bayes_factor_wins(4, 0) == pytest.approx(3.2)
    assert rg.bayes_factor_wins(6, 0) == pytest.approx(64 / 7)
    assert not rg.regime_gate(rg.case_rps(cases, lambda c: None), refs).passed


def test_engine_that_cannot_call_tightening_fails():
    """Owner decision 2026-10-07: an engine perfect on easing but always easing on tightening cases fails Gate 1,
    whatever its episode-level record, because its tightening-subset RPS is not below always-easing's."""
    cases = _mixed_cases() + [_case("t2", "2016-03-01", "tightening", "E6"), _case("t3", "2017-03-01", "tightening", "E7")]
    refs = _refs(cases)
    easy = rg.case_rps(cases, lambda c: (0.98, 0.01, 0.01))
    g = rg.regime_gate(easy, refs)
    tc = g.tightening
    assert tc["n"] == 3 and not tc["low_power"] and tc["skill_vs_reference"] < 0 and not tc["passed"]
    assert tc["rps_references"]["null_always_risk_on"] < tc["rps_model"]
    assert not g.passed
    assert rg.tightening_check(easy, {})["passed"] is False                 # no reference rows: not met
    assert rg.tightening_check(rg.case_rps(_mixed_cases()[:5], lambda c: (0.98, 0.01, 0.01)), refs)["n"] == 0


def test_constant_majority_forecast_cannot_pass_gate():
    """2026-10-07 closure: a constant 'always easing' forecast must fail the gate whatever the target mix: it is one of
    the references (it cannot beat itself) and it cannot beat itself on the tightening subset either."""
    cases = _mixed_cases()
    refs = _refs(cases)
    g = rg.regime_gate(refs["null_always_risk_on"], refs)
    assert g.references["null_always_risk_on"].p_value == 1.0 and not g.tightening["passed"] and not g.passed


# -------------------------------------------------------------------- diagnostics


def test_kappa_ba_auc_against_chance():
    t = ["easing"] * 8 + ["tightening"] * 2
    const = rg.kappa_ba(t, ["easing"] * 10)
    assert const["kappa"] == pytest.approx(0.0) and const["balanced_accuracy"] == 0.5 and const["ba_chance"] == 0.5
    perfect = rg.kappa_ba(t, t)
    assert perfect["kappa"] == pytest.approx(1.0) and perfect["balanced_accuracy"] == 1.0
    assert rg.auc_tightening(t, [0.1] * 8 + [0.9, 0.9])["auc"] == 1.0
    assert rg.auc_tightening(t, [0.1] * 10)["auc"] == 0.5
    assert rg.auc_tightening(["easing"], [0.1])["auc"] is None


def test_bracketed_labels_and_masking():
    cases = [_case("a", "2015-03-02", "easing", "E1"), _case("b", "2015-09-01", "easing", "E1"),
             _case("c", "2017-06-01", "easing", "E2"),                # > 12 months after b: not bracketed
             _case("d", "2017-09-01", "tightening", "E2")]            # disagrees with c: not bracketed
    lab = rg.bracketed_labels(cases)
    assert set(lab) == set(trading_days(dt.date(2015, 3, 2), dt.date(2015, 9, 1)))
    assert all(v == ("easing", "E1") for v in lab.values())
    ranges = [("EPX", dt.date(2015, 5, 1), dt.date(2015, 5, 29))]
    masked = rg.bracketed_labels(cases, ranges)
    assert not any(dt.date(2015, 5, 1) <= d <= dt.date(2015, 5, 29) for d in masked)
    assert len(masked) == len(lab) - len(trading_days(dt.date(2015, 5, 1), dt.date(2015, 5, 29)))
    pa = rg.path_agreement(masked, lambda d: "easing")
    assert pa["agreement"] == 1.0 and pa["chance"] == 1.0 and pa["n_episodes"] == 1


def test_holdout_date_ranges_read_names_and_episodes_only(tmp_path):
    for name, ep in [("2018-06-29_x.yaml", "EPH"), ("2018-09-06_y.yaml", "EPH"), ("2015-03-02_z.yaml", "EPR")]:
        # holdout file content deliberately invalid as a case: only episode_id may be read
        (tmp_path / name).write_text(yaml.safe_dump({"episode_id": ep, "targets": "unparsed"}), encoding="utf-8")
    (tmp_path / "HOLDOUT.yaml").write_text(yaml.safe_dump({"holdout_episodes": ["EPH"], "holdout_sha256": "x"}),
                                           encoding="utf-8")
    r = rg.holdout_date_ranges(tmp_path)
    assert r == [("EPH", shift_trading_days(dt.date(2018, 6, 29), -20), shift_trading_days(dt.date(2018, 9, 6), 20))]
    assert rg.masked(dt.date(2018, 7, 2), r) and not rg.masked(dt.date(2015, 3, 2), r)


def test_censor_spells_and_transition_matching():
    lab = ["easing"] * 100 + ["tightening"] * 10 + ["easing"] * 50 + ["tightening"] * 200
    sp = rg.censor_spells(lab, 63)
    assert [(a, b, x) for a, b, x in sp] == [(0, 160, "easing"), (160, 360, "tightening")]
    cases = [_case("a", "2019-12-18", "easing", "E1"), _case("b", "2022-06-10", "tightening", "E2")]
    (t,) = rg.transitions(cases)
    assert (t.from_regime, t.to_regime, t.last_old, t.first_new) == ("easing", "tightening", dt.date(2019, 12, 18),
                                                                     dt.date(2022, 6, 10))
    turn = dt.date(2021, 6, 1)
    m = rg.match_transition(t, lambda d: "tightening" if d >= turn else "easing")
    assert m["position"] == "inside" and m["turn"] == turn.isoformat() and m["extra_turns"] == 0
    assert m["lead_trading_days"] == len(trading_days(turn, t.first_new)) - 1
    assert rg.match_transition(t, lambda d: None)["position"] == "missed"


# -------------------------------------------------------------------- schema and adapter


def test_decision_probabilities_validated_and_adapted():
    asof = et_close(dt.date(2015, 3, 2))
    rv = RegimeVector("US", p_easing=0.7, p_neutral=0.2, p_tightening=0.1)
    assert rv.policy_direction == "easing" and rv.probabilities == (0.7, 0.2, 0.1)
    with pytest.raises(ValueError):
        RegimeVector("US", "tightening", p_easing=0.7, p_neutral=0.2, p_tightening=0.1)   # not argmax
    with pytest.raises(ValueError):
        RegimeVector("US", p_easing=0.995, p_neutral=0.004, p_tightening=0.001)           # below floor
    with pytest.raises(ValueError):
        RegimeVector("US", p_easing=0.7, p_neutral=0.2)                                    # incomplete
    d = Decision(asof=asof, engine_version="t", registry_sha="r", regime=[RegimeVector("EA", "tightening"), rv])
    assert d.schema_version == "2"
    p = decision_to_prediction(d)
    assert p.regime_direction == "easing" and p.regime_probs == (0.7, 0.2, 0.1)
    assert decision_to_prediction(Decision.from_json(d.to_json())).regime_probs == (0.7, 0.2, 0.1)
    stub = Decision(asof=asof, engine_version="t", registry_sha="r")
    assert decision_to_prediction(stub).regime_probs is None


# -------------------------------------------------------------------- option C: era B joins the Gate 1 set


def test_gate1_set_includes_era_b_and_climatology_is_combined():
    cases = [_case("a", "1994-03-01", "tightening", "EB", era="B"), _case("b", "2015-03-02", "easing", "E1"),
             _case("c", "2016-03-01", "easing", "E2"), parse_case({
                 "id": "d", "asof": "2017-03-01", "era": "A", "episode_id": "E3", "truth_type": "action",
                 "mechanizable": "yes", "source_reliability": "primary", "targets": {"action": "enter"}})]
    rc = rg.regime_cases(cases)
    assert [c.id for c in rc] == ["a", "b", "c"]                        # era B included, no-regime case excluded
    assert [c.id for c in rg.regime_cases(cases, eras=("A",))] == ["b", "c"]
    # scoring E1: the era-B tightening case counts -> (1+1, 0+1, 1+1) / (2+3)
    assert rg.loeo_climatology(rc, "E1") == pytest.approx((0.4, 0.2, 0.4))
    rows = rg.case_rps(rc, lambda c: (0.98, 0.01, 0.01))
    assert [r.era for r in rows] == ["B", "A", "A"]


def test_class_balanced_rps():
    cases = [_case("a", "1994-03-01", "tightening", "EB", era="B"), _case("b", "2015-03-02", "easing", "E1"),
             _case("c", "2016-03-01", "easing", "E2")]
    rows = rg.case_rps(cases, lambda c: (0.98, 0.01, 0.01))
    easing = rg.rps((0.98, 0.01, 0.01), "easing")
    tight = rg.rps((0.98, 0.01, 0.01), "tightening")
    assert rg.class_balanced(rows) == pytest.approx((easing + tight) / 2)   # not (2 easing + 1 tight) / 3
    assert rg.class_balanced([]) is None


def test_long_transition_intervals_are_not_matched():
    cases = [_case("a", "1981-12-31", "tightening", "EB", era="B"), _case("b", "2003-12-31", "easing", "E1"),
             _case("c", "2005-06-01", "tightening", "E2")]
    assert [(t.from_case, t.to_case) for t in rg.transitions(cases)] == [("b", "c")]
    assert len(rg.transitions(cases, max_months=None)) == 2
