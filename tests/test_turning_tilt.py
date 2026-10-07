"""Turning-point derivation (targets only) and the 13F tilt-sign component with its baselines."""

import pytest

from fatpitch.cases import (
    CaseError,
    NoChangeTilt,
    Prediction,
    PriorTiltPersistence,
    parse_case,
    run,
    score_case,
    turning_point_ids,
)
from fatpitch.cases.schema import Corpus


def _c(cid, asof, regime=None, action=None, theses=(), expr=(), tilt=None, derivation=None):
    t = {"regime_direction": regime, "action": action,
         "theses": [{"asset_class": a, "direction": d} for a, d in theses], "expression": list(expr)}
    if tilt is not None:
        t["tilt"] = tilt
    d = {"id": cid, "asof": asof, "era": "A", "episode_id": cid, "truth_type": "action", "mechanizable": "yes",
         "source_reliability": "primary", "targets": t}
    if derivation is not None:
        d["derivation"] = derivation
    return parse_case(d)


def test_regime_change_within_lookback():
    cases = [_c("a", "2010-01-04", regime="easing"), _c("b", "2010-06-01", regime="easing"),
             _c("c", "2011-01-03", regime="tightening"), _c("d", "2013-06-03", regime="easing")]
    assert turning_point_ids(cases) == {"c"}           # d: previous regime case is > 18 months earlier


def test_regime_compares_with_last_case_that_has_a_regime():
    cases = [_c("a", "2010-01-04", regime="easing"), _c("b", "2010-03-01", action="hold", expr=["fx_eur"]),
             _c("c", "2010-06-01", regime="neutral")]
    assert turning_point_ids(cases) == {"c"}


def test_exit_and_reverse_are_turning_except_first_case():
    cases = [_c("a", "2010-01-04", action="exit", expr=["equity_us"]),
             _c("b", "2015-01-05", action="reverse", theses=[("equity", "long")]),
             _c("c", "2016-01-04", action="exit", expr=["rates_us"])]
    assert turning_point_ids(cases) == {"b", "c"}


def test_standby_to_entry_same_asset_class():
    cases = [_c("a", "2010-01-04", action="flat", expr=["equity_us"]),
             _c("b", "2010-03-01", action="hold", expr=["fx_eur"]),
             _c("c", "2010-06-01", action="enter", theses=[("equity", "long")]),   # prior equity case: flat
             _c("d", "2010-07-01", action="size_up", theses=[("fx", "short")]),    # prior fx case: hold
             _c("e", "2010-08-02", action="enter", theses=[("equity", "long")])]   # prior equity: enter
    assert turning_point_ids(cases) == {"c", "d"}


def test_same_day_cases_are_not_earlier():
    cases = [_c("a", "2010-01-04", action="flat", expr=["equity_us"]),
             _c("b", "2010-01-04", action="enter", expr=["equity_us"])]
    assert turning_point_ids(cases) == frozenset()


def test_corpus_subset_keeps_full_corpus_flags():
    cases = (_c("a", "2010-01-04", regime="easing"), _c("b", "2010-06-01", regime="tightening"))
    corpus = Corpus(cases, "x")
    sub = corpus.subset(turning_point=True)
    assert [c.id for c in sub.cases] == ["b"] and sub.turning == corpus.turning
    assert [c.id for c in sub.subset(turning_point=True).cases] == ["b"]   # not re-derived on the subset
    assert run(NoChangeTilt(), corpus).breakdown["turning_point"].keys() == {"no", "yes"}


def test_tilt_component_and_baselines():
    deriv = {"prior_tilt": {"equity_us_tech": 1, "equity_us_health": 0}}
    c = _c("t", "2020-08-14", tilt={"equity_us_tech": -1, "equity_us_health": 1}, derivation=deriv)
    assert c.targets.tilt == (("equity_us_health", 1), ("equity_us_tech", -1))
    assert c.baseline_tilt == (("equity_us_health", 0), ("equity_us_tech", 1))
    assert score_case(c, lambda d: Prediction(tilts=(("equity_us_tech", -1),))).tilt == 0.5
    assert run(NoChangeTilt(), [c]).case_scores[0].tilt == 0.0
    assert run(PriorTiltPersistence([c]), [c]).case_scores[0].tilt == 0.0
    good = _c("u", "2020-11-16", tilt={"equity_us_tech": 1}, derivation=deriv)
    assert run(PriorTiltPersistence([c, good]), [good]).case_scores[0].tilt == 1.0
    assert score_case(_c("v", "2020-08-14"), lambda d: Prediction()).tilt is None


@pytest.mark.parametrize("tilt", [{"x": 2}, {"x": True}, ["x"]])
def test_tilt_validation(tilt):
    with pytest.raises(CaseError, match="tilt"):
        _c("t", "2020-08-14", tilt=tilt)


# -------------------------------------------------------------------- paired gate


def _res(name, vals):
    from fatpitch.cases import Result
    from fatpitch.cases.scoring import CaseScore, aggregate

    scores = [CaseScore(f"c{i}", f"e{i}", v, None, None, None) for i, v in enumerate(vals)]
    return Result(name, scores, aggregate(scores))


def test_paired_sign_flip_detects_case_by_case_advantage():
    from fatpitch.cases import paired_sign_flip_test

    eng = _res("eng", [1.0] * 11)
    null = _res("null", [1.0, 0.5, 0.0, 0.0, 1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.0])
    r = paired_sign_flip_test(eng, null, "regime", n_perm=2000, seed=1)
    assert r.n == 11 and r.engine_mean == 1.0 and r.mean_diff > 0 and r.p_value < 0.01
    same = paired_sign_flip_test(eng, eng, "regime", n_perm=500)
    assert same.mean_diff == 0 and same.p_value == 1.0
    worse = paired_sign_flip_test(null, eng, "regime", n_perm=500)
    assert worse.p_value > 0.5
    sub = paired_sign_flip_test(eng, null, "regime", case_ids={"c0", "c4"}, n_perm=100)
    assert sub.n == 2 and sub.mean_diff == 0.0


def test_paired_sign_flip_is_deterministic_and_validates():
    from fatpitch.cases import paired_sign_flip_test

    eng, null = _res("e", [1, 0, 1, 1]), _res("n", [0, 0, 1, 0])
    a = paired_sign_flip_test(eng, null, "regime", n_perm=1000, seed=20261006)
    b = paired_sign_flip_test(eng, null, "regime", n_perm=1000, seed=20261006)
    assert a == b
    with pytest.raises(ValueError):
        paired_sign_flip_test(eng, null, "size")
    with pytest.raises(ValueError, match="no case"):
        paired_sign_flip_test(eng, null, "thesis")


def test_paired_gate_needs_both_significance_and_floor():
    from fatpitch.cases import paired_gate

    null = _res("n", [0.0] * 6 + [1.0] * 6)
    strong = _res("e", [1.0] * 12)
    assert paired_gate(strong, null, "regime", floor=0.80, n_perm=2000).passed
    weak = _res("e", [0.75] * 12)                  # beats an all-zero null case by case, but 0.75 < floor
    g = paired_gate(weak, _res("n", [0.0] * 12), "regime", floor=0.80, n_perm=2000)
    assert g.paired.p_value < 0.10 and g.agreement == 0.75 and not g.passed
    tie = paired_gate(_res("e", [0.0] * 6 + [1.0] * 6), null, "regime", floor=0.4, n_perm=500)
    assert not tie.passed and tie.agreement >= 0.4
