"""Fed cycle check (fatpitch.cases.fedcycles; owner decision 2026-10-07, option A; spec/scoring.md section 6d)."""

import datetime as dt
import itertools

import pytest
import yaml

from fatpitch.cases import fedcycles as fc
from fatpitch.cases import regime as rg
from fatpitch.versions.score import overall_regime_pass

# -------------------------------------------------------------------- chronology mechanics (fixture series)


def test_target_events_and_min_run_rule():
    d = dt.date
    series = [(d(1985, 1, 2), 8.0), (d(1985, 2, 1), 8.25), (d(1985, 3, 1), 8.5),      # +0.50 run: kept
              (d(1985, 4, 1), 8.4375),                                               # -0.0625: dropped
              (d(1985, 5, 1), 8.75),                                                 # +0.3125 run: kept, merges
              (d(1985, 9, 1), 8.25), (d(1985, 10, 1), 7.75)]                         # -1.0 run: kept
    ev = fc.target_events(series)
    assert ev[0] == (d(1985, 2, 1), 0.25) and len(ev) == 6
    lvl = dict(series)
    cyc = fc.cycles_from_events([(x, ch, lvl[x], "DFEDTAR") for x, ch in ev])
    assert [(c.direction, c.start, c.end) for c in cyc] == [("tightening", (1985, 2), (1985, 5)),
                                                           ("easing", (1985, 9), (1985, 10))]
    assert cyc[0].level_start == 8.0 and cyc[0].level_end == 8.75


def test_monthly_turning_points_rule():
    vals = [5.0] * 8 + [4.0, 3.0, 2.0] + [3.0, 4.0, 5.0, 6.0, 7.0] + [7.0] * 8 + [6.8] + [7.0] * 8
    months = [fc.add_months((1970, 1), i) for i in range(len(vals))]
    tps = fc.monthly_turning_points(list(zip(months, vals, strict=True)))
    kinds = [(t, round(v, 2)) for _, t, v in tps]
    assert ("trough", 2.0) in kinds
    # the 0.2 pp dip at the plateau is not a cycle (< 1.0 pp)
    assert all(abs(b[2] - a[2]) >= 1.0 for a, b in itertools.pairwise(tps))
    cyc = fc.cycles_from_turning_points(tps)
    assert any(c.direction == "tightening" and c.start == fc.add_months(months[10], 1) for c in cyc)


def test_labels_easing_dominates_and_qt_counts_as_tightening():
    cycles = [fc.Cycle("tightening", (2015, 12), (2018, 12), "x"), fc.Cycle("easing", (2019, 8), (2020, 3), "x"),
              fc.Cycle("easing", (2024, 9), (2025, 12), "x")]
    qt = [((2017, 10), (2019, 7)), ((2022, 6), (2025, 11))]
    lab = fc.monthly_labels(cycles, qt, (2015, 1), (2026, 1))
    assert lab[(2015, 11)] == "neutral" and lab[(2016, 6)] == "tightening"
    assert lab[(2019, 3)] == "tightening"                    # pause after the last hike, during QT
    assert lab[(2019, 8)] == "easing" and lab[(2021, 1)] == "neutral"
    assert lab[(2023, 10)] == "tightening"                   # pause with QT
    assert lab[(2024, 10)] == "easing"                       # cuts during QT: easing dominates
    assert lab[(2026, 1)] == "neutral"


def test_splice_merge_and_splice_step_is_a_cut():
    ffm = [(fc.add_months((1960, 1), i), 5.0) for i in range(12 * 22 + 8)]          # flat pre-1982
    tar = [(dt.date(1982, 9, 27), 10.0), (dt.date(1990, 1, 2), 9.0), (dt.date(2008, 12, 15), 1.0)]
    taru = [(dt.date(2008, 12, 16), 0.25), (dt.date(2015, 12, 17), 0.5)]
    cyc = fc.build_cycles(ffm, tar, taru)
    assert [(c.direction, fc.mstr(c.start), fc.mstr(c.end)) for c in cyc] == [
        ("easing", "1990-01", "2008-12"), ("tightening", "2015-12", "2015-12")]


# -------------------------------------------------------------------- the check


def _labels():
    seq = ["easing"] * 12 + ["neutral"] * 6 + ["tightening"] * 12 + ["easing"] * 12 + ["tightening"] * 12
    return {fc.add_months((1990, 1), i): lab for i, lab in enumerate(seq)}


def test_loeo_cycle_climatology_excludes_own_block():
    lab = _labels()
    clim = fc.loeo_cycle_climatology(lab)
    # month in the first tightening block: excluded own 12 tightening months -> counts E 24, N 6, T 12
    p = clim[(1991, 7)]
    assert p == pytest.approx(rg.floor_probs(((24 + 1) / 45, (6 + 1) / 45, (12 + 1) / 45)))
    assert len(set(fc.label_blocks(lab).values())) == 5


def test_detection_lead_lag_and_incomplete_window():
    lab = _labels()
    cycles = [{"start": "1991-07", "end": "1992-06"}, {"start": "1993-07", "end": "1994-06"},
              {"start": "1994-05", "end": "1994-06"}]
    # engine turns tightening 2 months before the first cycle, never for the second
    rows = fc.score_months(lab, lambda m: (0.05, 0.05, 0.9) if (1991, 5) <= m <= (1992, 6) else (0.9, 0.05, 0.05))
    det = fc.detection(rows, cycles)
    assert det[0]["detected"] and det[0]["lead_lag_months"] == -2 and det[0]["evaluated"]
    assert not det[1]["detected"] and det[1]["evaluated"]
    assert det[2]["evaluated"] is False                       # window runs past the last labelled month


def test_false_alarms_and_fed_check_requires_every_criterion():
    lab = _labels()
    cycles = [{"start": "1991-07", "end": "1992-06"}, {"start": "1993-07", "end": "1994-06"}]
    perfect = fc.score_months(lab, lambda m: {"easing": (0.9, 0.05, 0.05), "neutral": (0.05, 0.9, 0.05),
                                              "tightening": (0.05, 0.05, 0.9)}[lab[m]])
    clim = fc.loeo_cycle_climatology(lab)
    refs = {"climatology_cycle_loeo": fc.score_months(lab, lambda m: clim[m]),
            "null_trend_12m": fc.score_months(lab, lambda m: (0.4, 0.2, 0.4)),
            "null_always_risk_on": fc.score_months(lab, lambda m: rg.deterministic_probs("easing")),
            "null_fed_direction": fc.score_months(lab, lambda m: rg.deterministic_probs(_lagged(lab, m, 1)))}
    ok = fc.fed_check(perfect, refs, cycles)
    assert ok.passed and ok.skill_pass and ok.detection_pass and ok.false_alarm_pass and ok.false_alarm_share == 0.0
    assert ok.vs_fed_direction_pass and ok.detected_count == 2 and ok.median_lead_months == 0.0
    assert ok.fed_direction_detected_count == 2 and ok.fed_direction_median_lead_months == -1.0
    # always tightening: detects every cycle but false-alarms every easing month
    alarm = fc.score_months(lab, lambda m: (0.05, 0.05, 0.9))
    r = fc.fed_check(alarm, refs, cycles)
    assert r.detection_pass and r.false_alarm_share == 1.0 and not r.false_alarm_pass and not r.passed
    # no probabilities: worst RPS, nothing detected
    r2 = fc.fed_check(fc.score_months(lab, lambda m: None), refs, cycles)
    assert not r2.skill_pass and r2.detected_share == 0.0 and not r2.passed
    # a missing reference makes (a) not evaluable
    assert not fc.fed_check(perfect, {k: v for k, v in refs.items() if k != "null_trend_12m"}, cycles).skill_pass
    assert [d["decade"] for d in ok.decades] == ["1990s"]


def _lagged(lab, m, k):
    """Label of the month k months earlier (a rate reader that recognises each change k months late)."""
    return lab.get(fc.add_months(m, -k), lab[m])


def test_engine_must_detect_at_least_as_well_as_fed_direction():
    """Owner decision 2026-10-07: the engine must read Fed tightening better than simply reading rate changes."""
    lab = _labels()
    cycles = [{"start": "1991-07", "end": "1992-06"}, {"start": "1993-07", "end": "1994-06"}]
    clim = fc.loeo_cycle_climatology(lab)
    fd = fc.score_months(lab, lambda m: rg.deterministic_probs(_lagged(lab, m, 1)))
    refs = {"climatology_cycle_loeo": fc.score_months(lab, lambda m: clim[m]),
            "null_trend_12m": fc.score_months(lab, lambda m: (0.4, 0.2, 0.4)),
            "null_always_risk_on": fc.score_months(lab, lambda m: rg.deterministic_probs("easing")),
            "null_fed_direction": fd}
    late = fc.score_months(lab, lambda m: rg.deterministic_probs(_lagged(lab, m, 2)))   # two months late
    r = fc.fed_check(late, refs, cycles)
    assert r.detection_pass and r.detected_count == 2 and r.median_lead_months == -2.0
    assert not r.vs_fed_direction_pass and not r.passed
    # without the fed_direction reference (b') and (a) are not evaluable
    r2 = fc.fed_check(late, {k: v for k, v in refs.items() if k != "null_fed_direction"}, cycles)
    assert not r2.vs_fed_direction_pass and not r2.skill_pass


def test_overall_pass_requires_both_checks():
    assert overall_regime_pass(True, True) is True
    assert overall_regime_pass(True, False) is False
    assert overall_regime_pass(False, True) is False
    assert overall_regime_pass(None, True) is None and overall_regime_pass(True, None) is None


def test_answer_key_loads(tmp_path):
    p = tmp_path / "fed_cycles.yaml"
    p.write_text(yaml.safe_dump({"monthly_labels": {"1990-01": "easing", "1990-02": "tightening"},
                                 "rate_cycles": [{"direction": "tightening", "start": "1990-02", "end": "1990-02"},
                                                 {"direction": "easing", "start": "1989-06", "end": "1990-01"}]}),
                 encoding="utf-8")
    key = fc.load_fed_key(p)
    assert key.labels == {(1990, 1): "easing", (1990, 2): "tightening"} and len(key.tightening_cycles) == 1
    assert fc.month_end_dates(key.labels)[(1990, 2)] == dt.date(1990, 2, 28)
    assert fc.load_fed_key(tmp_path / "missing.yaml") is None

def test_call_of_uses_stated_direction_on_ties():
    from fatpitch.cases import fedcycles as fc
    tied = (0.478, 0.043, 0.478)
    assert fc.call_of(tied, "tightening") == "tightening"                  # R-66 tie rule (decision SCORE-01)
    assert fc.call_of(tied, None) == "easing"                               # no stated call: first class
    assert fc.call_of((0.913, 0.043, 0.043), "tightening") == "easing"      # not tied: stated call ignored
    assert fc.call_of(None, "easing") is None
