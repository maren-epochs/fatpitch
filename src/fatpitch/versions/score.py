"""Scoring glue for the version runner. Scoring itself is ``fatpitch.cases`` of the CURRENT checkout, held constant
across versions; this module only feeds it precomputed predictions and serialises results.

Gates (spec/scoring.md sections 6c, 7), research split:

| Gate | Set | Rule |
|---|---|---|
| ``gate1`` (regime staging, option B + C, owner decisions 2026-10-07) | research cases with a regime target, era A and era B | RPS of the daily as-of regime probabilities at asof; episode-first mean; pass iff, for EACH of LOEO climatology, ``null_trend_12m`` and ``null_always_risk_on``, RPS skill > 0 and exact one-sided episode sign-flip p < 0.10 (``fatpitch.cases.regime.regime_gate``); binding reference = largest p |
| ``gate2`` | era-A cases with thesis targets | thesis recall; paired sign-flip vs ``null_trend_12m`` p < 0.10 and recall >= 0.50 |

Diagnostics (reported, not gated; ``fatpitch.cases.regime``): #8 bracketed daily path agreement (holdout-episode date
ranges masked), #9 turning-point matching on regime changes, #5 kappa / balanced accuracy, #7 AUC on P(tightening).
The section 3 regime agreement is reported in ``overall``; the retired agreement (6a) and timing (6b) gates are not
computed.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path

import polars as pl

import fatpitch
from fatpitch.cases import Corpus, Prediction, Result, aggregate, paired_sign_flip_test, run
from fatpitch.cases import fedcycles as fc
from fatpitch.cases import regime as rg
from fatpitch.cases.scoring import COMPONENTS, CaseScore, PredictionCache

GATE2 = {"component": "thesis", "floor": 0.50, "alpha": 0.10}
GATE1_DEF = "rps-skill-v3"   # v2: beat each of three references; v3: era A + era B set (option C), 2026-10-07
CLIMATOLOGY = "climatology_loeo"
GATE1_REFERENCES = (CLIMATOLOGY, "null_trend_12m", "null_always_risk_on")
N_PERM = 10000
SEED = 20261006

# Files whose bytes define "the scoring code" (fingerprint, held constant across versions).
SCORING_FILES = ("cases/scoring.py", "cases/schema.py", "cases/holdout.py", "cases/nulls.py", "cases/regime.py",
                 "cases/fedcycles.py", "dates.py", "versions/adapter.py", "versions/score.py", "versions/nullsource.py")


def scoring_fingerprint() -> dict:
    """sha256 over the scoring files of the installed (current) package: sorted ``path NUL sha256 LF`` lines."""
    pkg = Path(fatpitch.__file__).resolve().parent
    h = hashlib.sha256()
    files = {}
    for rel in sorted(SCORING_FILES):
        b = (pkg / rel).read_bytes()
        files[rel] = hashlib.sha256(b).hexdigest()
        h.update(f"{rel}\0{files[rel]}\n".encode())
    from fatpitch.versions import gitops

    try:
        top = gitops.toplevel(pkg)
        git = {"head": gitops.head(top),
               "dirty_scoring_files": gitops.dirty_paths(top, [str(pkg / r) for r in SCORING_FILES])}
    except (gitops.GitError, OSError) as exc:  # not a git checkout (e.g. installed wheel)
        git = {"error": str(exc)}
    return {"sha256": h.hexdigest(), "files": files, "package_dir": str(pkg), "git": git}


def gate_ids(corpus: Corpus) -> dict[str, list[str]]:
    return {"gate1": sorted(c.id for c in rg.regime_cases(corpus.cases)),
            "gate2": sorted(c.id for c in corpus.cases if c.era == "A" and c.targets.theses),
            "full": sorted(c.id for c in corpus.cases)}


def holdout_ranges(corpus: Corpus) -> list:
    return rg.holdout_date_ranges(corpus.root) if corpus.root else []


def window_dates(corpus: Corpus, fed: fc.FedKey | None = None) -> list[_dt.date]:
    """Every date the scorer asks about: case windows and asofs, the #8 bracketed days and the #9 transition
    windows."""
    ds: set[_dt.date] = set()
    for c in corpus.cases:
        ds.update(c.window.dates(c.asof_date))
        ds.add(c.asof_date)
    ds.update(rg.bracketed_labels(corpus.cases, holdout_ranges(corpus)))
    for t in rg.transitions(corpus.cases):
        ds.update(rg.transition_window(t))
    if fed is not None:
        ds.update(fc.month_end_dates(fed.labels).values())
    return sorted(ds)


@dataclass
class TableEngine:
    """Engine over precomputed predictions by date. A date outside the table is an error, not unknown."""

    name: str
    table: dict[_dt.date, Prediction] = field(repr=False)

    def predict(self, asof: _dt.datetime, source) -> Prediction:
        return self.table[asof.date()]


def record(engine, source, dates: list[_dt.date]) -> dict[_dt.date, Prediction]:
    cache = PredictionCache(engine, source)
    return {d: cache(d) for d in dates}


def score(name: str, table: dict[_dt.date, Prediction], corpus: Corpus) -> Result:
    return run(TableEngine(name, table), corpus)


# -------------------------------------------------------------------- serialisation helpers


def case_scores_from(rows: list[dict]) -> list[CaseScore]:
    return [CaseScore(**r) for r in rows]


def subset_scores(scores: list[CaseScore], ids) -> dict:
    keep = set(ids)
    return aggregate([s for s in scores if s.case_id in keep])


def paired(a: list[CaseScore], b: list[CaseScore], component: str, ids=None) -> dict | None:
    """One-sided paired sign-flip test of A > B on ``component`` over cases scored by both (within ``ids``)."""
    try:
        pr = paired_sign_flip_test(Result("a", list(a), {}), Result("b", list(b), {}), component, case_ids=ids,
                                   n_perm=N_PERM, seed=SEED)
    except ValueError:
        return None
    return asdict(pr)


def rps_rows(corpus: Corpus, table: dict[_dt.date, Prediction]) -> list[rg.CaseRPS]:
    return rg.case_rps(rg.regime_cases(corpus.cases), lambda c: table[c.asof_date].regime_probs)


def climatology_rows(corpus: Corpus) -> list[rg.CaseRPS]:
    cases = rg.regime_cases(corpus.cases)
    return rg.case_rps(cases, lambda c: rg.loeo_climatology(cases, c.episode_id))


def rps_to_json(rows: list[rg.CaseRPS]) -> list[dict]:
    return [{**asdict(r), "probs": None if r.probs is None else list(r.probs)} for r in rows]


def rps_from_json(rows: list[dict]) -> list[rg.CaseRPS]:
    return [rg.CaseRPS(**{**r, "probs": None if r["probs"] is None else tuple(r["probs"])}) for r in rows]


def gate_dict(gr: rg.RegimeGateResult) -> dict:
    return {**asdict(gr), "research_pass": gr.passed}


def diagnostics(corpus: Corpus, table: dict[_dt.date, Prediction], rows: list[rg.CaseRPS]) -> dict:
    labels = rg.bracketed_labels(corpus.cases, holdout_ranges(corpus))
    direction = lambda d: table[d].regime_direction
    targets = [r.target for r in rows]
    preds = [table[c.asof_date].regime_direction for c in rg.regime_cases(corpus.cases)]
    return {
        "path_agreement_8": rg.path_agreement(labels, direction),
        "turning_points_9": [rg.match_transition(t, direction) for t in rg.transitions(corpus.cases)],
        "turning_points_9_excluded": [
            {"from": t.from_regime, "to": t.to_regime, "last_old": t.last_old.isoformat(),
             "first_new": t.first_new.isoformat(), "reason": f"interval > {rg.MAX_TRANSITION_MONTHS} months"}
            for t in rg.transitions(corpus.cases, max_months=None) if t not in rg.transitions(corpus.cases)],
        "classification_5": rg.kappa_ba(targets, preds),
        "auc_tightening_7": rg.auc_tightening(targets, [None if r.probs is None else r.probs[2] for r in rows]),
        "masked_holdout_ranges": [[e, lo.isoformat(), hi.isoformat()] for e, lo, hi in holdout_ranges(corpus)],
    }


def gate1_counts(rows: list[rg.CaseRPS]) -> dict:
    """Cases per era and target class, and episodes per era (option C report)."""
    out: dict = {}
    for era in (*rg.ERAS, "all"):
        sub = [r for r in rows if era == "all" or r.era == era]
        out[era] = {"n_cases": len(sub), "k": len({r.episode_id for r in sub}),
                    **{c: sum(r.target == c for r in sub) for c in rg.CLASSES}}
    return out


def episode_table(rows: list[rg.CaseRPS], refs: dict[str, list[rg.CaseRPS]]) -> list[dict]:
    """Per episode: era(s), target classes, n cases, model mean RPS and each reference's mean RPS."""
    em = rg.episode_means(rows)
    er = {n: rg.episode_means(r) for n, r in refs.items()}
    out = []
    for e in sorted(em):
        sub = [r for r in rows if r.episode_id == e]
        out.append({"episode_id": e, "era": "/".join(sorted({r.era for r in sub})),
                    "classes": {c: sum(r.target == c for r in sub) for c in rg.CLASSES if any(r.target == c for r in sub)},
                    "n": len(sub), "rps_model": em[e], **{f"rps[{n}]": m.get(e) for n, m in er.items()}})
    return out


def gate1_breakdowns(rows: list[rg.CaseRPS], refs: dict[str, list[rg.CaseRPS]]) -> dict:
    """Option C report: counts, class-balanced RPS (model and references), the gate statistic on era A only and era
    B only (reported; the gate decision uses the combined set), and the per-episode table."""
    by_era = {}
    for era in rg.ERAS:
        sub = [r for r in rows if r.era == era]
        if sub:
            ids = {r.case_id for r in sub}
            by_era[era] = gate_dict(rg.regime_gate(sub, {n: [x for x in v if x.case_id in ids] for n, v in refs.items()}))
    return {"counts": gate1_counts(rows), "class_balanced_rps": rg.class_balanced(rows),
            "reference_class_balanced_rps": {n: rg.class_balanced(v) for n, v in refs.items()},
            "by_era": by_era, "episodes": episode_table(rows, refs)}


def fed_rows(fed: fc.FedKey, table: dict[_dt.date, Prediction]) -> list[fc.MonthScore]:
    me = fc.month_end_dates(fed.labels)
    return fc.score_months(fed.labels, lambda m: table[me[m]].regime_probs, lambda m: table[me[m]].regime_direction)


def fed_climatology_rows(fed: fc.FedKey) -> list[fc.MonthScore]:
    clim = fc.loeo_cycle_climatology(fed.labels)
    return fc.score_months(fed.labels, lambda m: clim[m])


def fed_rows_from_json(rows: list[dict]) -> list[fc.MonthScore]:
    return [fc.MonthScore(**{**r, "probs": None if r["probs"] is None else tuple(r["probs"])}) for r in rows]


def fed_section(fed: fc.FedKey | None, table: dict[_dt.date, Prediction], engine: str,
                fed_null_rows: dict[str, list[fc.MonthScore]] | None) -> tuple[list, dict | None]:
    """Fed cycle check (spec/scoring.md 6d): month-end RPS vs the Fed-stance labels; references LOEO-by-cycle
    climatology, null_trend_12m, null_always_risk_on; detection and false alarms. A reference null is not compared
    with itself (its pass value is None)."""
    if fed is None:
        return [], None
    rows = fed_rows(fed, table)
    refs = {fc.FED_REFERENCES[0]: fed_climatology_rows(fed)}
    refs.update({n: v for n, v in (fed_null_rows or {}).items() if n != engine})
    res = fc.fed_check(rows, refs, fed.tightening_cycles).to_dict()
    res["complete"] = all(n in refs for n in fc.FED_REFERENCES)
    if not res["complete"]:
        res["passed"] = None
    res["answer_key_sha256"] = fed.sha256
    res["constants"] = {"detect_before_months": fc.DETECT_BEFORE_MONTHS, "detect_after_months": fc.DETECT_AFTER_MONTHS,
                        "detect_share": fc.DETECT_SHARE, "false_alarm_max": fc.FALSE_ALARM_MAX}
    return rows, res


def overall_regime_pass(gate1: bool | None, fed: bool | None) -> bool | None:
    """Overall regime pass = Gate 1 (documented reads) AND the Fed cycle check; None when either is not evaluable."""
    return None if gate1 is None or fed is None else bool(gate1 and fed)


def scores_json(result: Result, corpus: Corpus, table: dict[_dt.date, Prediction],
                best_null: list[CaseScore] | None, best_null_name: str | None,
                null_refs: dict[str, list[rg.CaseRPS]] | None, fed: fc.FedKey | None = None,
                fed_null_rows: dict[str, list[fc.MonthScore]] | None = None) -> dict:
    """``best_null``: Gate 2 best null per-case scores; ``null_refs``: Gate 1 RPS rows of the null references
    (``null_trend_12m``, ``null_always_risk_on``); LOEO climatology is added here. A null is not compared with
    itself; a run that lacks a required reference (a reference null scoring itself) gets ``research_pass`` None."""
    ids = gate_ids(corpus)
    scores = result.case_scores
    rows = rps_rows(corpus, table)
    clim = climatology_rows(corpus)
    out = {"engine": result.engine, "overall": result.overall, "n_cases": result.n_cases,
           "n_episodes": result.n_episodes, "era": result.breakdown.get("era", {}),
           "breakdown": result.breakdown, "gates": {}, "regime_rps": rps_to_json(rows),
           "climatology_rps": rps_to_json(clim)}
    refs = {CLIMATOLOGY: clim}
    refs.update({n: r for n, r in (null_refs or {}).items() if n != result.engine})
    gr = rg.regime_gate(rows, refs)
    g1 = {"definition": GATE1_DEF, "references_required": list(GATE1_REFERENCES), "case_ids": ids["gate1"],
          "alpha": rg.ALPHA, "agreement": subset_scores(scores, ids["gate1"]).get("regime"),
          "complete": all(n in refs for n in GATE1_REFERENCES), **gate_dict(gr)}
    if not g1["complete"]:
        g1["research_pass"] = None
    g1.update(gate1_breakdowns(rows, refs))
    out["gates"]["gate1"] = g1
    out["diagnostics"] = diagnostics(corpus, table, rows)
    frows, fres = fed_section(fed, table, result.engine, fed_null_rows)
    out["fed_rows"] = [asdict(r) for r in frows]
    out["fed_check"] = fres
    out["overall_regime_pass"] = overall_regime_pass(g1.get("research_pass"), None if fres is None else fres.get("passed"))
    comp = GATE2["component"]
    sub = [s for s in scores if s.case_id in set(ids["gate2"]) and s.get(comp) is not None]
    agg = subset_scores(scores, ids["gate2"])
    pr = paired(scores, best_null, comp, ids["gate2"]) if best_null is not None and best_null_name != result.engine \
        else None
    val = agg.get(comp)
    out["gates"]["gate2"] = {
        "component": comp, "floor": GATE2["floor"], "alpha": GATE2["alpha"], "case_ids": ids["gate2"],
        "n_cases": len(sub), "n_episodes": len({s.episode_id for s in sub}), "score": val, "components": agg,
        "best_null": best_null_name, "vs_best_null": pr,
        "meets_floor": None if val is None else val >= GATE2["floor"],
        "research_pass": None if pr is None or val is None else (pr["p_value"] < GATE2["alpha"] and val >= GATE2["floor"]),
    }
    out["case_scores"] = [asdict(s) for s in scores]
    return out


def ref_value(g1: dict, name: str, key: str):
    return ((g1.get("references") or {}).get(name) or {}).get(key)


def summary(scores: dict) -> dict:
    g1, g2 = scores["gates"]["gate1"], scores["gates"]["gate2"]
    dg = scores.get("diagnostics", {})
    out = {**{c: scores["overall"].get(c) for c in COMPONENTS},
           "gate1_def": g1.get("definition"), "gate1_rps": g1.get("rps_model"), "gate1_k": g1.get("k"),
           "gate1_cb_rps": g1.get("class_balanced_rps"),
           "fed_pass": (scores.get("fed_check") or {}).get("passed"),
           "fed_rps": (scores.get("fed_check") or {}).get("rps"),
           "fed_detected_share": (scores.get("fed_check") or {}).get("detected_share"),
           "fed_false_alarm": (scores.get("fed_check") or {}).get("false_alarm_share"),
           "overall_regime_pass": scores.get("overall_regime_pass"),
           "gate1_tight_n": (g1.get("tightening") or {}).get("n"),
           "gate1_tight_skill": (g1.get("tightening") or {}).get("skill_vs_reference"),
           "gate1_tight_pass": (g1.get("tightening") or {}).get("passed"),
           "gate1_binding_p_A": ((g1.get("by_era") or {}).get("A") or {}).get("binding_p"),
           "gate1_binding_p_B": ((g1.get("by_era") or {}).get("B") or {}).get("binding_p"),
           "gate1_n": g1["n_cases"], "gate1_pass": g1.get("research_pass"),
           "gate1_binding": g1.get("binding_reference"), "gate1_binding_p": g1.get("binding_p"),
           "path_agreement": (dg.get("path_agreement_8") or {}).get("agreement"),
           "kappa": (dg.get("classification_5") or {}).get("kappa"),
           "auc_tightening": (dg.get("auc_tightening_7") or {}).get("auc"),
           "gate2_score": g2["score"], "gate2_p": (g2["vs_best_null"] or {}).get("p_value"), "gate2_n": g2["n_cases"]}
    for n in GATE1_REFERENCES:
        out[f"gate1_skill[{n}]"] = ref_value(g1, n, "skill")
        out[f"gate1_p[{n}]"] = ref_value(g1, n, "p_value")
        out[f"gate1_wins[{n}]"] = ref_value(g1, n, "wins")
    return out


def predictions_frame(corpus: Corpus, table: dict[_dt.date, Prediction]) -> pl.DataFrame:
    """One row per (case, window date): the prediction the scorer saw."""
    rows = []
    for c in corpus.cases:
        days = sorted(set(c.window.dates(c.asof_date)) | {c.asof_date})
        for d in days:
            p = table[d]
            pr = p.regime_probs or (None, None, None)
            rows.append({"case_id": c.id, "episode_id": c.episode_id, "date": d, "is_asof": d == c.asof_date,
                         "regime_direction": p.regime_direction, "p_easing": pr[0], "p_neutral": pr[1],
                         "p_tightening": pr[2],
                         "theses": [f"{t.asset_class}/{t.direction}/{t.region or ''}" for t in p.theses],
                         "expressions": list(p.expressions), "action": p.action,
                         "tilts": [f"{f}:{s}" for f, s in p.tilts]})
    schema = {"case_id": pl.Utf8, "episode_id": pl.Utf8, "date": pl.Date, "is_asof": pl.Boolean,
              "regime_direction": pl.Utf8, "p_easing": pl.Float64, "p_neutral": pl.Float64, "p_tightening": pl.Float64,
              "theses": pl.List(pl.Utf8), "expressions": pl.List(pl.Utf8), "action": pl.Utf8, "tilts": pl.List(pl.Utf8)}
    return pl.DataFrame(rows, schema=schema)
