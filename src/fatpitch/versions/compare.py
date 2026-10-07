"""Pairwise comparison of runs and the leaderboard (``results\\versions\\LEADERBOARD.md`` + ``.json``).

Identifiers accepted by ``resolve``: a null name (``null_trend_12m`` ...; the cached null run for the current
corpus sha), a label (``spec-v0.1``, ``wip``; its latest run) or a run id (``20261006T210000Z-03cf1be0``).
"""

from __future__ import annotations

import json
from pathlib import Path

from fatpitch.cases import Corpus
from fatpitch.cases import regime as rg
from fatpitch.cases.scoring import COMPONENTS
from fatpitch.versions import score, trials
from fatpitch.versions.nullsource import BEST_NULL, NULL_NAMES
from fatpitch.versions.runner import Paths, _write_json, load_research, nulls_dir, safe_label

COMPARE_SETS = (("gate1", "regime"), ("gate2", "thesis")) + tuple(("full", c) for c in COMPONENTS)


def _load(run_dir: Path) -> dict:
    return {"dir": run_dir, "meta": json.loads((run_dir / "meta.json").read_text(encoding="utf-8")),
            "scores": json.loads((run_dir / "scores.json").read_text(encoding="utf-8"))}


def _complete(d: Path) -> bool:
    return (d / "scores.json").exists() and (d / "meta.json").exists()


def latest_runs(paths: Paths) -> list[dict]:
    out = []
    if not paths.results.exists():
        return out
    for lab in sorted(p for p in paths.results.iterdir() if p.is_dir() and p.name != "nulls"):
        runs = sorted(d for d in lab.iterdir() if d.is_dir() and _complete(d))
        if runs:
            out.append(_load(runs[-1]))
    return out


def null_runs(paths: Paths, corpus_sha: str) -> list[dict]:
    d = nulls_dir(paths, corpus_sha)
    return [_load(d / n) for n in NULL_NAMES if _complete(d / n)]


def resolve(paths: Paths, ident: str, corpus_sha: str) -> dict:
    if ident in NULL_NAMES:
        d = nulls_dir(paths, corpus_sha) / ident
        if not _complete(d):
            raise FileNotFoundError(f"null {ident} not scored for corpus {corpus_sha[:16]}; run `run-nulls`")
        return _load(d)
    lab = paths.results / safe_label(ident)
    if lab.is_dir():
        runs = sorted(d for d in lab.iterdir() if d.is_dir() and _complete(d))
        if runs:
            return _load(runs[-1])
    hits = sorted(d for d in paths.results.glob(f"*/{ident}") if _complete(d))
    if len(hits) == 1:
        return _load(hits[0])
    raise FileNotFoundError(f"no run, label or null named {ident!r} under {paths.results}")


def _name(r: dict) -> str:
    m = r["meta"]
    return m["label"] if m["kind"] == "null" else f"{m['label']}@{m['run_id']}"




# -------------------------------------------------------------------- compare


def _rps(r: dict) -> list[rg.CaseRPS] | None:
    t = r["scores"].get("regime_rps")
    return None if t is None else score.rps_from_json(t)


def _compare_rps(ra: dict, rb: dict) -> dict | None:
    """Gate 1 statistic, A vs B: episode-first RPS of each, skill of A vs B, exact episode sign-flip p both ways,
    per-episode RPS and per-case RPS that differ."""
    a, b = _rps(ra), _rps(rb)
    if a is None or b is None:
        return None
    ea, eb = rg.episode_means(a), rg.episode_means(b)
    common = sorted(set(ea) & set(eb))
    if not common:
        return None
    d = [eb[e] - ea[e] for e in common]
    by_b = {x.case_id: x for x in b}
    return {"k": len(common), "rps_a": rg.episode_first(a), "rps_b": rg.episode_first(b),
            "skill_a_vs_b": rg.skill(rg.episode_first(a), rg.episode_first(b)),
            "p_a_better": rg.exact_sign_flip_p(d), "p_b_better": rg.exact_sign_flip_p([-x for x in d]),
            "a_wins": sum(x > 1e-12 for x in d), "b_wins": sum(x < -1e-12 for x in d),
            "episodes": [{"episode_id": e, "rps_a": ea[e], "rps_b": eb[e]} for e in common],
            "cases_differ": [{"case_id": x.case_id, "target": x.target, "rps_a": x.rps, "rps_b": by_b[x.case_id].rps}
                             for x in a if x.case_id in by_b and abs(x.rps - by_b[x.case_id].rps) > 1e-12]}


def compare(paths: Paths, a: str, b: str, corpus: Corpus | None = None) -> dict:
    corpus = corpus or load_research(paths)
    ra, rb = resolve(paths, a, corpus.sha256), resolve(paths, b, corpus.sha256)
    sa = score.case_scores_from(ra["scores"]["case_scores"])
    sb = score.case_scores_from(rb["scores"]["case_scores"])
    ids = score.gate_ids(corpus)
    by_b = {s.case_id: s for s in sb}
    rows = []
    for subset, comp in COMPARE_SETS:
        keep = set(ids[subset])
        pairs = [(x, by_b[x.case_id]) for x in sa if x.case_id in keep and x.case_id in by_b
                 and x.get(comp) is not None and by_b[x.case_id].get(comp) is not None]
        ab = score.paired(sa, sb, comp, keep)
        ba = score.paired(sb, sa, comp, keep)
        flips = [{"case_id": x.case_id, "a": x.get(comp), "b": y.get(comp)} for x, y in pairs if x.get(comp) != y.get(comp)]
        rows.append({"subset": subset, "component": comp, "n": len(pairs),
                     "a_score": score.subset_scores(sa, keep).get(comp), "b_score": score.subset_scores(sb, keep).get(comp),
                     "delta": None if not ab else ab["mean_diff"],
                     "p_a_gt_b": ab["p_value"] if ab else None, "p_b_gt_a": ba["p_value"] if ba else None,
                     "a_better": [f["case_id"] for f in flips if f["a"] > f["b"]],
                     "b_better": [f["case_id"] for f in flips if f["b"] > f["a"]], "flipped": flips})
    warn = []
    for r in (ra, rb):
        if r["meta"]["corpus"]["sha256"] != corpus.sha256:
            warn.append(f"{_name(r)} was scored on corpus {r['meta']['corpus']['sha256'][:16]}, current is "
                        f"{corpus.sha256[:16]}; compared on common cases only")
    if ra["meta"]["scoring"]["sha256"] != rb["meta"]["scoring"]["sha256"]:
        warn.append("A and B were scored with different scoring code (scoring sha differs)")
    return {"a": _name(ra), "b": _name(rb), "corpus_sha": corpus.sha256, "gate1_rps": _compare_rps(ra, rb),
            "rows": rows, "warnings": warn,
            "test": f"score components: one-sided paired sign-flip, N {score.N_PERM}, seed {score.SEED}, case-level; "
                    "Gate 1 RPS: exact episode-level sign-flip; score columns are episode-first aggregates"}


def compare_markdown(c: dict) -> str:
    out = [f"# {c['a']} (A) vs {c['b']} (B)", "", f"Research split, corpus `{c['corpus_sha'][:16]}`. {c['test']}.", ""]
    out += [f"Warning: {w}" for w in c["warnings"]] + ([""] if c["warnings"] else [])
    g = c.get("gate1_rps")
    if g:
        out += ["## Gate 1 statistic: regime RPS (lower is better), episode level", "",
                (f"RPS A {_f(g['rps_a'])}, B {_f(g['rps_b'])}; skill of A vs B {_f(g['skill_a_vs_b'], signed=True)}; "
                 f"episodes A better {g['a_wins']}, B better {g['b_wins']} of k = {g['k']}; exact p (A better) "
                 f"{_p(g['p_a_better'])}, p (B better) {_p(g['p_b_better'])}."), "",
                "| episode | RPS A | RPS B |", "|---|---|---|"]
        out += [f"| {e['episode_id']} | {_f(e['rps_a'])} | {_f(e['rps_b'])} |" for e in g["episodes"]]
        out += ["", "## Score components", ""]
    out += ["| subset | component | n pairs | A | B | mean diff (A-B) | p (A>B) | p (B>A) | A better | B better |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for r in c["rows"]:
        out.append(f"| {r['subset']} | {r['component']} | {r['n']} | {_f(r['a_score'])} | {_f(r['b_score'])} | "
                   f"{_f(r['delta'], signed=True)} | {_p(r['p_a_gt_b'])} | {_p(r['p_b_gt_a'])} | "
                   f"{len(r['a_better'])} | {len(r['b_better'])} |")
    out += ["", "## Flipped cases", ""]
    for r in c["rows"]:
        if r["flipped"]:
            out.append(f"{r['subset']} / {r['component']}: " + "; ".join(
                f"`{f['case_id']}` A {_f(f['a'])} B {_f(f['b'])}" for f in r["flipped"]))
    if all(not r["flipped"] for r in c["rows"]):
        out.append("None: A and B score identically on every case.")
    return "\n".join(out) + "\n"


# -------------------------------------------------------------------- headroom


def gate1_headroom(paths: Paths, corpus: Corpus) -> dict:
    """Gate 1 headroom: k = episodes in the Gate 1 set (research cases with a regime target, era A and B). Against each
    reference an episode is winnable while the reference's episode RPS > 0 (always: forecasts are floored); the
    maximum attainable exact one-sided p is 1 / 2^w for w winnable episodes, and the gate needs it below alpha
    against every reference, so the binding headroom is the smallest w."""
    cases = rg.regime_cases(corpus.cases)
    eps_ = sorted({c.episode_id for c in cases})
    refs = {score.CLIMATOLOGY: rg.episode_means(score.climatology_rows(corpus))}
    for n in score.GATE1_REFERENCES[1:]:
        d = nulls_dir(paths, corpus.sha256) / n
        if _complete(d):
            refs[n] = rg.episode_means(score.rps_from_json(json.loads((d / "scores.json").read_text(encoding="utf-8"))
                                                           ["regime_rps"]))
    win = {n: sum(1 for e in eps_ if m.get(e, 1.0) > 1e-12) for n, m in refs.items()}
    w = min(win.values()) if win else len(eps_)
    return {"k": len(eps_), "n_cases": len(cases), "episodes": eps_, "winnable": w, "winnable_by_reference": win,
            "min_p_exact": (0.5 ** w) if w else None, "alpha": rg.ALPHA, "reachable": bool(w) and 0.5 ** w < rg.ALPHA,
            "reference_episode_rps": refs,
            "class_counts": {k_: sum(c.targets.regime_direction == k_ for c in cases) for k_ in rg.CLASSES},
            "era_counts": {era: {"n_cases": sum(c.era == era for c in cases),
                                 "k": len({c.episode_id for c in cases if c.era == era}),
                                 **{k_: sum(c.era == era and c.targets.regime_direction == k_ for c in cases)
                                    for k_ in rg.CLASSES}} for era in rg.ERAS},
            "tightening_n": sum(c.targets.regime_direction == "tightening" for c in cases),
            "tightening_k": len({c.episode_id for c in cases if c.targets.regime_direction == "tightening"}),
            "tightening_low_power": sum(c.targets.regime_direction == "tightening" for c in cases)
            < rg.TIGHTENING_MIN_CASES}


# -------------------------------------------------------------------- leaderboard


def _f(x, signed: bool = False) -> str:
    if x is None:
        return "-"
    return f"{x:+.3f}" if signed else f"{x:.3f}"


def _p(x) -> str:
    return "-" if x is None else (f"{x:.4f}" if x < 0.001 else f"{x:.3f}")


def leaderboard(paths: Paths, corpus: Corpus | None = None) -> dict:
    corpus = corpus or load_research(paths)
    n = trials.count(paths.trials)
    adj1 = trials.adjusted(paths.trials, "gate1_binding_p")
    adj2 = trials.adjusted(paths.trials, "gate2_p")
    rows = []
    clim = None
    for r in latest_runs(paths) + null_runs(paths, corpus.sha256):
        m, s = r["meta"], r["scores"]
        g1, g2 = s["gates"]["gate1"], s["gates"]["gate2"]
        cur = g1.get("definition") == score.GATE1_DEF
        dg = s.get("diagnostics", {}) if cur else {}
        t = m.get("trial")
        if cur and clim is None and m["corpus"]["sha256"] == corpus.sha256:
            clim = score.ref_value(g1, score.CLIMATOLOGY, "rps")
        pa = dg.get("path_agreement_8") or {}
        tp = dg.get("turning_points_9") or []
        rows.append({
            "version": m["label"], "kind": m["kind"], "run_id": m["run_id"],
            "date": (m.get("run", {}).get("started_utc") or "")[:10],
            "commit": (m.get("version") or {}).get("commit"), "registry_sha": m.get("registry_sha"),
            "corpus_sha": m["corpus"]["sha256"], "current_corpus": m["corpus"]["sha256"] == corpus.sha256,
            "scoring_sha": m["scoring"]["sha256"], "gate1_def": g1.get("definition", "agreement (pre-2026-10-07)"),
            "gate1_n": g1.get("n_cases"), "gate1_k": g1.get("k") if cur else None,
            "gate1_rps": g1.get("rps_model") if cur else None,
            "gate1_refs": {n: {"skill": score.ref_value(g1, n, "skill"), "p": score.ref_value(g1, n, "p_value"),
                               "wins": score.ref_value(g1, n, "wins")} for n in score.GATE1_REFERENCES} if cur else {},
            "gate1_binding": g1.get("binding_reference") if cur else None,
            "gate1_p": g1.get("binding_p") if cur else None,
            "gate1_pass": g1.get("research_pass") if cur else None,
            "gate1_cb_rps": g1.get("class_balanced_rps") if cur else None,
            "gate1_ref_cb_rps": g1.get("reference_class_balanced_rps") if cur else {},
            "gate1_by_era": {e: {"binding_p": v.get("binding_p"), "k": v.get("k"), "rps": v.get("rps_model"),
                                 "skills": {n: (v.get("references", {}).get(n) or {}).get("skill")
                                            for n in score.GATE1_REFERENCES}}
                             for e, v in (g1.get("by_era") or {}).items()} if cur else {},
            "gate1_tightening": g1.get("tightening") if cur else None,
            "gate1_episodes": g1.get("episodes") if cur else None,
            "fed_check": s.get("fed_check"),
            "overall_regime_pass": s.get("overall_regime_pass"),
            "gate1_p_holm": adj1.get(t, {}).get("holm") if t else None,
            "gate1_p_bonferroni": adj1.get(t, {}).get("bonferroni") if t else None,
            "path_agreement": pa.get("agreement"), "path_chance": pa.get("chance"), "path_ci95": pa.get("ci95"),
            "kappa": (dg.get("classification_5") or {}).get("kappa"),
            "balanced_accuracy": (dg.get("classification_5") or {}).get("balanced_accuracy"),
            "ba_chance": (dg.get("classification_5") or {}).get("ba_chance"),
            "auc_tightening": (dg.get("auc_tightening_7") or {}).get("auc"),
            "turns": [f"{x['from'][:1]}>{x['to'][:1]} {x['position']}"
                      + ("" if x["lead_trading_days"] is None else f" {x['lead_trading_days']:+d}") for x in tp],
            "extra_turns": sum(x["extra_turns"] for x in tp) if tp else None,
            "gate2_score": g2["score"], "gate2_n": g2["n_cases"], "gate2_p": (g2.get("vs_best_null") or {}).get("p_value"),
            "gate2_p_holm": adj2.get(t, {}).get("holm") if t else None,
            "gate2_p_bonferroni": adj2.get(t, {}).get("bonferroni") if t else None,
            **{c: s["overall"].get(c) for c in ("regime", "thesis", "expression", "action")},
            "trial": t, "path": str(r["dir"].relative_to(paths.results))})
    eng = [r for r in rows if r["kind"] != "null"]
    eng.sort(key=lambda r: ((r["gate1_p"] if r["gate1_p"] is not None else 2.0),
                            -(r["gate2_score"] if r["gate2_score"] is not None else -1), r["version"]))
    nul = [r for r in rows if r["kind"] == "null"]
    return {"corpus_sha": corpus.sha256, "n_cases": len(corpus), "n_trials": n,
            "n_distinct": trials.distinct(paths.trials), "best_null": BEST_NULL,
            "gate1_references": list(score.GATE1_REFERENCES),
            "rps_climatology": clim, "headroom": gate1_headroom(paths, corpus), "rows": eng + nul}


def leaderboard_markdown(lb: dict) -> str:
    h = lb["headroom"]
    out = ["# Spec-version leaderboard (research split)", "",
           ("Generated by `python -m fatpitch.versions leaderboard` (rewritten after every `run`). Research split only; "
            "the holdout is sealed and never loaded; holdout-episode date ranges are masked from daily labels. Not "
            "pre-registered: exploratory research trials, counted in `trials.jsonl`."), ""]
    cc = h["class_counts"]
    p_txt = f"{h['min_p_exact']:.4f} (1/2^{h['winnable']})" if h["min_p_exact"] is not None else "n/a"
    out += ["## Gate 1 headroom (research; regime RPS skill gate, option B, owner decisions 2026-10-07)", "",
            (f"Gate 1 set (option C: era A and era B): {h['n_cases']} research cases with a regime target (easing "
             f"{cc['easing']}, neutral {cc['neutral']}, tightening {cc['tightening']}) in k = {h['k']} episodes; "
             + "; ".join(f"era {e}: {v['n_cases']} cases / {v['k']} episodes (E {v['easing']}, N {v['neutral']}, "
                         f"T {v['tightening']})" for e, v in h["era_counts"].items())
             + ". The engine must beat EACH "
             "reference (LOEO climatology, `null_trend_12m`, `null_always_risk_on`) with RPS skill > 0 and an exact "
             f"one-sided episode sign-flip p < {h['alpha']}. Maximum attainable p against each = {p_txt} (engine "
             f"better in every episode); winnable episodes {h['winnable']} of {h['k']}; Gate 1 is "
             f"{'reachable' if h['reachable'] else 'NOT reachable'} on research (p < {h['alpha']} needs at least 4 "
             "episodes, all won, or more episodes with a few losses). LOEO climatology episode-first RPS: "
             f"{_f(lb['rps_climatology'])}."), "",
            (f"Hard tightening requirement (owner decision 2026-10-07): on the {h['tightening_n']} tightening cases "
             f"({h['tightening_k']} episodes) the engine's mean RPS must be below `null_always_risk_on`'s. "
             + ("LOW POWER: fewer than 3 tightening cases; the rule still applies." if h["tightening_low_power"]
                else "")), ""]
    out += ["## Runs", "",
            (f"Corpus (research) `{lb['corpus_sha'][:16]}`, {lb['n_cases']} cases. Trials N = {lb['n_trials']} engine "
             f"runs ({lb['n_distinct']} distinct configurations); Holm and Bonferroni adjust each gate's p over all N "
             "logged trials (a trial without a p under the current definition counts as p = 1). Gate 1 (spec\\scoring.md "
             "section 6c): RPS of the as-of regime probabilities at each case asof (missing = worst), episode-first; "
             "skill = 1 - RPS / RPS_ref and exact one-sided episode sign-flip p against each reference: clim = LOEO "
             "climatology, trend = `null_trend_12m`, easing = `null_always_risk_on` (wins/k in brackets); pass = all "
             "three skills > 0 and all three p < 0.10 and the tightening requirement (T-skill vs easing > 0, n in "
             "brackets); binding p = the largest of the three (Holm/Bonferroni on it); CB-RPS = class-balanced RPS "
             "(mean of per-class mean RPS; reported). "
             "Gate 2: thesis recall on era-A cases "
             f"with thesis targets vs `{lb['best_null']}` (paired sign-flip, floor 0.50). Full-corpus columns are "
             "section 3 episode-first aggregates."),
            "",
            ("| version | date | trial # | registry sha | G1 RPS | G1 CB-RPS | G1 skill clim / trend / easing | "
             "G1 p clim (wins/k) | G1 p trend (wins/k) | G1 p easing (wins/k) | G1 binding p | G1 p Holm | G1 p Bonf | "
             "G1 T-skill vs easing (n) | G1 pass | Gate 2 (n) | G2 p | G2 p Holm | regime | thesis | expression | "
             "action |"),
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in lb["rows"]:
        v = r["version"] if r["kind"] != "null" else f"*{r['version']}*"
        if not r["current_corpus"]:
            v += f" (corpus {r['corpus_sha'][:8]})"
        if r["gate1_def"] != score.GATE1_DEF:
            v += f" (scored under Gate 1 definition {r['gate1_def']}; re-run to score Gate 1)"
        reg = f"`{r['registry_sha'][:12]}`" if r["registry_sha"] else "-"
        refs = r["gate1_refs"]
        sk = " / ".join(_f((refs.get(n) or {}).get("skill"), signed=True) for n in score.GATE1_REFERENCES)
        pc = [_p((refs.get(n) or {}).get("p")) + ("" if (refs.get(n) or {}).get("wins") is None
                                                  else f" ({refs[n]['wins']}/{r['gate1_k']})")
              for n in score.GATE1_REFERENCES]
        ps = "-" if r["gate1_pass"] is None else ("yes" if r["gate1_pass"] else "no")
        tc = r["gate1_tightening"] or {}
        ts = "-" if not tc else (f"{_f(tc.get('skill_vs_reference'), signed=True)} ({tc.get('n')})"
                                 + (" low power" if tc.get("low_power") else ""))
        out.append(f"| {v} | {r['date']} | {r['trial'] or '-'} | {reg} | {_f(r['gate1_rps'])} | "
                   f"{_f(r['gate1_cb_rps'])} | {sk} | "
                   f"{pc[0]} | {pc[1]} | {pc[2]} | {_p(r['gate1_p'])} | {_p(r['gate1_p_holm'])} | "
                   f"{_p(r['gate1_p_bonferroni'])} | {ts} | {ps} | "
                   f"{_f(r['gate2_score'])} ({r['gate2_n']}) | {_p(r['gate2_p'])} | {_p(r['gate2_p_holm'])} | "
                   f"{_f(r['regime'])} | {_f(r['thesis'])} | {_f(r['expression'])} | {_f(r['action'])} |")
    out += _era_tables(lb)
    out += _fed_tables(lb)
    out += ["", "## Regime diagnostics (reported, not gated)", "",
            ("#8 bracketed daily path agreement (days between two agreeing statements <= 12 months apart, holdout "
             "ranges masked; chance from the marginals; 95% CI episode bootstrap); #5 kappa (chance 0) and balanced "
             "accuracy at asof; #7 AUC of P(tightening) (chance 0.5); #9 his regime changes: engine turn position "
             "(before / inside / after his change interval, missed) and lead in trading days to his first new-view "
             "statement, extra turns in the windows (minimum spell 63 trading days)."), "",
            "| version | #8 agreement (chance) [CI] | #5 kappa | #5 BA (chance) | #7 AUC | #9 turns | #9 extra turns |",
            "|---|---|---|---|---|---|---|"]
    for r in lb["rows"]:
        v = r["version"] if r["kind"] != "null" else f"*{r['version']}*"
        ci = "-" if not r["path_ci95"] else f"[{r['path_ci95'][0]:.3f}, {r['path_ci95'][1]:.3f}]"
        out.append(f"| {v} | {_f(r['path_agreement'])} ({_f(r['path_chance'])}) {ci} | {_f(r['kappa'], signed=True)} | "
                   f"{_f(r['balanced_accuracy'])} ({_f(r['ba_chance'])}) | {_f(r['auc_tightening'])} | "
                   f"{'; '.join(r['turns']) or '-'} | {'-' if r['extra_turns'] is None else r['extra_turns']} |")
    out += ["", ("Nulls in italics (baselines, not trials); deterministic nulls are scored as probabilities with 0.9 on "
                 "the predicted class; a reference null is not compared with itself and has no pass value. A version shows "
                 "its latest run; every run is in `trials.jsonl`.")]
    return "\n".join(out) + "\n"


def _fed_tables(lb: dict) -> list[str]:
    """Fed cycle check (spec/scoring.md 6d): required alongside Gate 1; overall regime pass = Gate 1 AND this check."""
    rows = [r for r in lb["rows"] if r.get("fed_check")]
    if not rows:
        return ["", "## Fed cycle check", "", "No answer key (`spec\\fed_cycles.yaml`) or no run scored with it yet."]
    fc0 = rows[0]["fed_check"]
    k = fc0["constants"]
    out = ["", "## Fed cycle check (required; owner decision 2026-10-07, option A)", "",
           (f"Answer key `spec\\fed_cycles.yaml` (sha `{fc0['answer_key_sha256'][:12]}`): the Fed's own history, "
            f"monthly 1970 -> latest month ({fc0['n_months']} months: easing {fc0['label_counts']['easing']}, neutral "
            f"{fc0['label_counts']['neutral']}, tightening {fc0['label_counts']['tightening']}); public facts, not "
            "documented reads, so holdout-period dates are used. Scored at each month end with the RPS. Required: (a) "
            "mean RPS skill > 0 vs LOEO-by-cycle climatology, `null_trend_12m`, `null_always_risk_on` and "
            "`null_fed_direction` (fourth reference, owner decision 2026-10-07); (b) argmax "
            f"tightening within [first hike - {k['detect_before_months']}, + {k['detect_after_months']}] months in >= "
            f"{k['detect_share']:.0%} of tightening rate cycles (cycles without a full window excluded); (c) easing "
            f"months with argmax tightening <= {k['false_alarm_max']:.0%}; (b') detected cycles >= `null_fed_direction`'s "
            "and median first-hike lead >= its median lead. Overall regime pass = Gate 1 AND this check."),
           "",
           ("| version | RPS | skill clim / trend / easing / fed-dir | detected (cycles) | median lead (months) | "
            "false alarms | (a) / (b) / (b') / (c) | Fed pass | Gate 1 pass | overall regime pass |"),
           "|---|---|---|---|---|---|---|---|---|---|"]

    def yn(x):
        return "-" if x is None else ("yes" if x else "no")

    for r in rows:
        f = r["fed_check"]
        sk = " / ".join(_f((f["references"].get(n) or {}).get("skill"), signed=True)
                        for n in ("climatology_cycle_loeo", "null_trend_12m", "null_always_risk_on",
                                  "null_fed_direction"))
        ev = [c for c in f["cycles"] if c["evaluated"]]
        bp = "-" if r["version"] == "null_fed_direction" else yn(f.get("vs_fed_direction_pass"))
        out.append(f"| {r['version']} | {_f(f['rps'])} | {sk} | {_f(f['detected_share'])} ({sum(c['detected'] for c in ev)}"
                   f"/{len(ev)}) | {_f(f.get('median_lead_months'))} | {_f(f['false_alarm_share'])} | "
                   f"{yn(f['skill_pass'])} / {yn(f['detection_pass'])} / {bp} / "
                   f"{yn(f['false_alarm_pass'])} | {yn(f['passed'])} | {yn(r['gate1_pass'])} | "
                   f"{yn(r['overall_regime_pass'])} |")
    clim = (fc0["references"].get("climatology_cycle_loeo") or {}).get("rps")
    out.append(f"| LOEO-by-cycle climatology | {_f(clim)} | - | - | - | - | - | - | - | - |")
    out += ["", ("References (no pass value when scoring themselves): LOEO-by-cycle climatology, `null_trend_12m`, "
                 "`null_always_risk_on`, `null_fed_direction`. Median lead = median of (first-hike month - first "
                 "detection month) over detected cycles; > 0 = before the first hike.")]
    names = [r["version"] for r in rows]
    out += ["", ("Per tightening rate cycle: lead (-) / lag (+) in months of the first month-end with argmax tightening "
                 "within the detection window; 'no' = not detected; 'n/a' = window incomplete."), "",
            "| first hike | last hike | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    for i, c in enumerate(fc0["cycles"]):
        cells = []
        for r in rows:
            x = r["fed_check"]["cycles"][i]
            cells.append("n/a" if not x["evaluated"] else (f"{x['lead_lag_months']:+d}" if x["detected"] else "no"))
        out.append(f"| {c['start']} | {c['end']} | " + " | ".join(cells) + " |")
    out += ["", "Per-decade RPS skill vs LOEO-by-cycle climatology:", "",
            "| decade | months | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    for i, d in enumerate(fc0["decades"]):
        cells = [_f(r["fed_check"]["decades"][i].get("skill[climatology_cycle_loeo]"), signed=True) for r in rows]
        out.append(f"| {d['decade']} | {d['n_months']} | " + " | ".join(cells) + " |")
    return out


def _era_tables(lb: dict) -> list[str]:
    """Gate 1 by era (reported; the decision uses the combined set), reference class-balanced RPS, tightening
    subset, and the per-episode table (references and the latest run of each version)."""
    cur = [r for r in lb["rows"] if r["gate1_rps"] is not None]
    out = ["", "## Gate 1 by era (reported; the gate decision uses the combined set)", "",
           ("| version | era A: k / RPS / skill clim, trend, easing / binding p | era B: k / RPS / skill clim, trend, "
            "easing / binding p |"), "|---|---|---|"]
    for r in cur:
        cells = []
        for e in ("A", "B"):
            v = r["gate1_by_era"].get(e)
            cells.append("-" if not v else f"{v['k']} / {_f(v['rps'])} / "
                         + ", ".join(_f(v["skills"].get(n), signed=True) for n in score.GATE1_REFERENCES)
                         + f" / {_p(v['binding_p'])}")
        out.append(f"| {r['version']} | {cells[0]} | {cells[1]} |")
    ref_row = next((r for r in cur if r["gate1_ref_cb_rps"]), None)
    tc_row = next((r for r in cur if r["gate1_tightening"]), None)
    out += ["", "## Tightening subset and class-balanced RPS (reported; tightening skill vs always-easing is gated)", "",
            "| version | CB-RPS | tightening n (k) | tightening RPS | T-skill vs easing | requirement met |",
            "|---|---|---|---|---|---|"]
    for r in cur:
        tc = r["gate1_tightening"] or {}
        met = "-" if not tc or r["kind"] == "null" and r["version"] in score.GATE1_REFERENCES else (
            "yes" if tc.get("passed") else "no")
        out.append(f"| {r['version']} | {_f(r['gate1_cb_rps'])} | {tc.get('n', '-')} ({tc.get('k', '-')}) | "
                   f"{_f(tc.get('rps_model'))} | {_f(tc.get('skill_vs_reference'), signed=True)} | {met} |")
    if ref_row:
        cb = ref_row["gate1_ref_cb_rps"].get(score.CLIMATOLOGY)
        tr = (tc_row["gate1_tightening"]["rps_references"] or {}).get(score.CLIMATOLOGY) if tc_row else None
        out.append(f"| LOEO climatology | {_f(cb)} | - | {_f(tr)} | - | - |")
    eng_eps = [(r["version"], {e["episode_id"]: e for e in (r["gate1_episodes"] or [])}) for r in cur]
    base = next((e for _, e in eng_eps if e), {})
    if base:
        names = [n for n, _ in eng_eps]
        out += ["", "## Gate 1 per episode (mean RPS; lower is better)", "",
                "| episode | era | targets | n | LOEO climatology | " + " | ".join(names) + " |",
                "|---|---|---|---|---|" + "---|" * len(names)]
        for ep, row in sorted(base.items(), key=lambda kv: (kv[1]["era"], kv[0])):
            tg = ", ".join(f"{k[0].upper()} {v}" for k, v in row["classes"].items())
            vals = " | ".join(_f(e.get(ep, {}).get("rps_model")) for _, e in eng_eps)
            out.append(f"| {ep} | {row['era']} | {tg} | {row['n']} | {_f(row.get('rps[' + score.CLIMATOLOGY + ']'))} | "
                       f"{vals} |")
    return out


def write_leaderboard(paths: Paths, corpus: Corpus | None = None) -> dict:
    lb = leaderboard(paths, corpus)
    paths.results.mkdir(parents=True, exist_ok=True)
    paths.leaderboard.write_text(leaderboard_markdown(lb), encoding="utf-8", newline="\n")
    _write_json(paths.results / "LEADERBOARD.json", lb)
    return lb
