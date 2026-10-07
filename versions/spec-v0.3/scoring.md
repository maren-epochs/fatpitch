# Fat Pitch — Scoring Rule, Null Models and Gates v1 (phase E2)

Date: 2026-10-06. Status: candidate for pre-registration together with `spec\process.md`, `spec\registry.yaml`, `spec\transition_table.yaml` and `spec\corpus_manifest.txt` (`python -m fatpitch.prereg register-all`). Not registered (awaiting owner review). This file describes what PLAN E.4 requires and what `src\fatpitch\cases\scoring.py`, `src\fatpitch\cases\nulls.py` and `src\fatpitch\cases\schema.py` implement; where the two differ, the implemented rule is stated and the difference is listed in section 8. Any change after the first scoring run is a design change (re-register, new report).

## 1. Units

| Item | Definition |
|---|---|
| Case | One YAML file in `cases\` (schema `fatpitch.cases.schema`). Fields used for scoring: `asof`, `era`, `episode_id`, `truth_type`, `mechanizable`, `source_reliability`, `targets`, `window`. Metadata (`citation`, `date_basis`, `retrospective`, `seed_id`, `notes`, `derivation`) is never read by scoring or engines |
| Engine | Any object with `name` and `predict(asof, source) -> Prediction`. Receives only an ET-close `asof` and a `Source`; never a case, a target or an outcome |
| Prediction | `regime_direction` (easing / neutral / tightening / None), `regime_probs` (P(easing), P(neutral), P(tightening) or None; section 6c), `theses` (asset_class, direction long/short, region), `expressions` (ranked families, best first), `action` (enter / size_up / reduce / exit / reverse / flat / hold / None), `tilts` (13F family → −1/0/+1) |
| Prediction date | Each trading day `d` is evaluated at 16:00 America/New_York (`fatpitch.dates.et_close`); predictions are cached per date (`PredictionCache`) |

## 2. Windows

| Case window | Trading days scored |
|---|---|
| `{unit: business_days, n: 20}` (default) | NYSE trading days from `asof` − 20 to `asof` + 20 trading days, inclusive (41 days) |
| `{unit: quarters, n: 1}` (13F cases only) | NYSE trading days from `asof` − 3 calendar months to `asof` + 3 calendar months, inclusive |

## 3. Per-case score (`ScoringRule(regime_exact=1.0, regime_window=0.5, expression_top_k=3)`)

| Component | Score | Not scored when |
|---|---|---|
| regime | 1.0 if the prediction at `asof` equals `targets.regime_direction`; else 0.5 if the prediction equals it on any trading day in the window; else 0.0 | target null |
| thesis | Fraction of target theses matched on any window day. A predicted thesis matches a target when asset_class and direction are equal and, if the target names a region, the region is equal | no target theses |
| expression | 1.0 if any target family is among the top 3 predicted families on any window day; else 0.0 | no target expression |
| action | 1.0 if the predicted action equals `targets.action` on any window day; else 0.0 | target null |
| tilt (13F cases) | Fraction of `targets.tilt` families (family → +1/−1, sign of the family's QoQ weight change among the filing pair's top-10 movers) whose predicted sign at `asof` (`Prediction.tilts`; absent family = 0 = no change) equals the target sign | no tilt target |

A missing prediction component (None, empty) on every day scores 0 for a scored component; an unscored component (null target) is excluded from every aggregate (unknown never counts as a fail). `size_band` targets are recorded for the E6 report and are not scored in v1.

`truth_type: process`: targets are the output of the cited stated rule, not the action taken, so an engine that reproduces the action scores a miss on that component. For these cases `action: flat` means "no new position in the target family", `hold` means "keep the existing position, no add, no exit".

## 4. Null models (`fatpitch.cases.nulls`), scored with the identical rule

| # | Null | Definition | v1 inputs |
|---|---|---|---|
| 1 | `null_always_risk_on` | Every date: regime easing; thesis equity/long/US; expression `equity_us`; action enter | none |
| 2 | `null_fed_direction` | Change of the policy rate over 182 calendar days (latest value with `period_end` ≤ date in the as-of snapshot): < 0 → easing, theses rates/long/US and equity/long/US, expressions `rates_us`, `equity_us`, action enter; > 0 → tightening, rates/short/US and equity/short/US, action enter; 0 → neutral, no thesis, action hold | `FEDFUNDS` (FRED, monthly, published_at per amber lake) |
| 3 | `null_trend_12m` | Sign of the 365-day change of each series (yield series sign-inverted as price proxies): one thesis per series (long if the signed change > 0), ranked by absolute relative change; expressions follow the thesis order (`<class>_<region>`); regime from the rates series: signed change > 0 (yields down) → easing, else tightening; action enter | equity: US market total-return index from Ken French daily factors (Mkt-RF + RF, published 18:00 ET of the return date; SPY proxy); rates: `DGS10`, sign −1 (IEF proxy); USD: `DTWEXM` to 2005-12-30 spliced to `DTWEXBGS` from 2006-01-02, rescaled on the first common date (DXY proxy) |
| 4 | `null_persistence` | Targets of the most recent case whose `asof` is more than 120 calendar days before the date (embargo > widest window, so no case sees its own targets) | the corpus |

13F tilt baselines (tilt component only; PLAN E.4 "beats no-change persistence"):

| Baseline | Definition |
|---|---|
| `null_tilt_no_change` | Predicts no change for every family (sign 0); scores 0 by construction |
| `null_tilt_persistence` | Predicts that each family's previous-quarter change sign persists: sign of the same top-10 issuers' summed weight change, by family, from the filing before the case's earlier filing to the earlier filing (`derivation.prior_tilt`; both filings published before the case's own earlier filing) |

Regime probabilities of the nulls (section 6c): the predicted direction gets 0.9 and the other two classes 0.05 each (`deterministic_probs`); a missing direction is a missing forecast. Series ids for nulls 2 and 3 are constructor arguments; the v1 mapping above is the registered one (`tools\null_smoke.py` builds it from the amber lake, read-only). A series missing at a date yields an empty prediction component for that date.

## 5. Aggregation and reporting

| Item | Rule |
|---|---|
| Aggregate | For each component: mean of scored cases within each episode, then the unweighted mean across episodes (`aggregate`, `_two_level`) |
| Breakdowns | Same two-level aggregate within each value of `era`, `source_reliability`, `truth_type`, `mechanizable`, `turning_point` |
| Margin | Engine aggregate minus the best (maximum) null aggregate on the same component and subset (`margin_over_best_null`); 0.15 = 15 points. Reported only; not a gate (section 7) |
| Ceiling | `mechanizable: no` cases are reported separately as the expected fidelity ceiling |

## 5a. Turning-point cases (`fatpitch.cases.turning_point_ids`; owner decision 2026-10-06)

Derived by code from case targets and `asof` only, never from market data or outcomes; not a hand-edited field. Computed once at load (`Corpus.turning`) on the full corpus (holdout and all splits) or on the research cases (research split, section 9) and carried unchanged into every subset. Cases are ordered by (`asof`, `id`); "earlier" means a strictly earlier `asof` no more than 18 calendar months before the case. A case is a turning point when any of:

| Rule | Condition |
|---|---|
| (a) regime change | its `regime_direction` target is set and differs from the `regime_direction` target of the most recent earlier case that has one |
| (b) break | its `action` target is `reverse` or `exit` |
| (c) standby → entry | its `action` target is `enter` or `size_up`, and the most recent earlier case that shares an asset class (thesis classes, else expression-family prefixes) and has an action target had `flat` or `hold` |

The first case of the corpus is never a turning point; cases on the same `asof` are not earlier than each other. Interpretations (confirmed by the owner 2026-10-06): the 18-month lookback also bounds (c); (a) skips earlier cases without a regime target.

Current corpus (`spec\corpus_manifest.txt`, 68 cases after the 2026-10-06 expansion, `tools\build_cases_v2.py`): 17 turning points, era A 16, era B 1 (`2000-01-31_tech-exit`). Era-A turning points with a regime target (the Gate 1 sample): 12 cases in 8 episodes; era-A turning points with thesis targets: 12 cases in 9 episodes. (Before the expansion: 16 turning points, Gate 1 sample 11 cases in 8 episodes.)

## 6. Permutation test (`permutation_test`)

On the evaluated subset (for Gate 1: era-A turning-point cases only), the `asof` dates are permuted across cases with targets held fixed; each window is re-centred on the assigned date; the episode-first aggregate of the component is recomputed. N = 1000 permutations, generator `numpy.random.default_rng(20261006)`, one `permutation` call per draw. p = (1 + #{permuted ≥ observed − 1e-12}) / (1 + N).

## 6a. Paired sign-flip test (`paired_sign_flip_test`)

Used by Gate 2 and by `compare` for score components. Retired as the Gate 1 test (paired regime agreement) on 2026-10-07 (section 6c; `spec\regime_evaluation_options.md` §1: unreachable against the base rate).

Per case scored by both the engine and the null on the gate component: d_i = engine_i − null_i. Statistic: mean(d). Null distribution: mean(s_i · d_i) with independent signs s_i ∈ {−1, +1}, equal probability, drawn as an (N × n) array by `numpy.random.default_rng(20261006).choice([-1, 1])`, N = 10000. One-sided p = (1 + #{permuted ≥ observed − 1e-12}) / (1 + N). Case-level, unweighted (not episode-first).

## 6b. Gate 1 timing metric — retired 2026-10-07

The timing gate (owner decision 2026-10-07, first version) scored the lead of each model's flip to the target regime against a comparator null on era-A turning-point cases. Retired the same day by the owner's adoption of option B (section 6c; analysis in `spec\regime_evaluation_options.md` §1: degenerate constant comparator, research headroom 0, outcome set by the holdout's target mix, 3 holdout episodes cap the episode-level p at 0.125). The code (`fatpitch.cases.timing`) was removed as redundant: the regime-change timing question is reported by diagnostic #9 (section 6c), which uses true regime changes (rule (a)) with interval-censored change dates instead of action turning points.

## 6c. Regime stage: probabilistic skill gate and diagnostics (option B; owner decision 2026-10-07)

Written 2026-10-07 before any engine emits regime probabilities (the only engine is the E0 stub). Source: `spec\regime_evaluation_options.md` §4 option 6, §5 option B and its pre-registration items. Code: `fatpitch.cases.regime`, glue `fatpitch.versions.score`.

### Pre-registered constants

| Constant | Value | Code |
|---|---|---|
| Ordinal class order for the RPS | easing < neutral < tightening | `CLASSES` |
| Probability floor ε | 0.01 | `EPS`; `fatpitch.decision.PROB_FLOOR` |
| Floor procedure | normalise to sum 1; clip-and-rescale: classes below ε set to ε, the remaining classes rescaled proportionally to fill 1 − (#clipped)·ε, repeated until none is below ε; a valid vector is unchanged | `floor_probs` |
| Deterministic null → probabilities | 0.9 on the predicted class, the remaining 0.1 split equally (0.05 / 0.05), then floored; no value is given in the report, so the owner's default 0.9 applies | `NULL_CONFIDENCE`; `deterministic_probs` |
| Missing forecast (no probabilities at asof) | scores the worst attainable RPS for the target: 1.0 for easing or tightening, 0.5 for neutral (all mass on the farthest class) | `worst_rps` |
| LOEO climatology | class frequencies of the regime targets of the Gate 1 set (research cases with a regime target, era A and era B; option C), excluding the scored case's episode, add-one smoothed: (n_k + 1) / (n + 3), then floored | `loeo_climatology`, `CLIM_SMOOTHING = 1` |
| α | 0.10 | `ALPHA` |
| #8 bracket | two consecutive agreeing statements at most 12 calendar months apart | `BRACKET_MAX_MONTHS = 12` |
| #8 holdout mask | each holdout episode's [first case date − 20, last case date + 20] trading days, from holdout file names and episode ids only (no target parsed) | `holdout_date_ranges`, `MASK_PAD_TRADING_DAYS = 20` |
| #8 bootstrap | episode-level, 2000 draws, `numpy.random.default_rng(20261006)` | `BOOT_N`, `SEED` |
| #9 minimum spell (Bry–Boschan censor) | 63 trading days (3 months; the report's value) | `MIN_SPELL_TRADING_DAYS` |
| #9 search window | last old-view statement − 12 months to first new-view statement + 6 months | `TURN_PRE_MONTHS`, `TURN_POST_MONTHS` |
| #9 maximum change interval | 36 months; his changes whose interval (last old-view to first new-view statement) is longer are listed as excluded, not matched (technical necessity: the era-B 1981-12-31 → 2003-12-31 interval is 22 years and carries no timing information) | `MAX_TRANSITION_MONTHS` |
| Tightening requirement reference / low-power threshold | `null_always_risk_on`; fewer than 3 tightening cases = low power (rule still applied) | `TIGHTENING_REFERENCE`, `TIGHTENING_MIN_CASES` |

### Engine output (Decision schema 2)

The US regime vector carries daily as-of probabilities `p_easing`, `p_neutral`, `p_tightening` at 16:00 ET, each ≥ 0.01, summing to 1 (validated); `policy_direction` = argmax (set when omitted, rejected when inconsistent). `fatpitch.versions.adapter` passes them into `Prediction.regime_probs` (US vector first). The E0 stub emits none, so every case scores the missing-forecast RPS.

### Gate 1 (regime staging gate)

| Item | Rule |
|---|---|
| Set | Research cases with a `regime_direction` target, era A and era B (option C, owner decision 2026-10-07): 28 cases, k = 10 episodes. Era A: 27 cases, 9 episodes (easing 25, tightening 2). Era B: 1 case, 1 episode (`1981-12-31_long-bonds-volcker`, tightening; the only research era-B case with a regime target). Totals: easing 25, neutral 0, tightening 3. Engine and nulls are evaluated point-in-time at each asof; era-B inputs are monthly where the Source provides them; a missing forecast scores the worst RPS. Turning points do not define the set |
| Per-case score | RPS of the floored forecast at the case asof (16:00 ET): RPS = Σ_{k=1}^{K−1} (F_k − O_k)² / (K − 1), F cumulative forecast, O cumulative observation, K = 3; range 0 (best) to 1 |
| Aggregation | Mean RPS per episode, then the unweighted mean over episodes (episode first, as section 5) |
| References | (a) LOEO climatology, (b) `null_trend_12m`, (c) `null_always_risk_on` (constant easing, 0.9 / 0.05 / 0.05) |
| Skill | 1 − RPS_engine / RPS_ref, on the episode-first means, for each reference |
| Test | For each reference: d_e = RPS_ref,e − RPS_engine,e per episode (> 0 = engine better); statistic mean(d); one-sided exact sign-flip: p = share of all 2^k sign patterns s with mean(s·d) ≥ mean(d) − 1e-12; a tie (d_e = 0) contributes 0 under every pattern |
| Pass | For EACH of the three references: skill > 0 AND p < 0.10. Binding reference = the one with the largest p (ties: smallest skill); the binding p is the reported Gate 1 p and the one adjusted by Holm / Bonferroni over trials |
| Engine predictions | Leave-one-episode-out out-of-fold predictions once calibration (PLAN E.6) exists; until then plain predictions |
| Headroom | Against each reference the maximum attainable p with k episodes is 1/2^k (engine better in every episode); every episode is winnable while the reference's episode RPS > 0 (always, since floored forecasts are never certain). The gate needs this below α against all three; research (combined set): k = 10, 1/1024 |
| Reported with it | per reference: RPS, skill, p, wins / losses / ties of k, per-episode differences, Bayes factor BF10 for θ = P(episode win) ~ Uniform(0, 1) vs θ = 0.5 (wins vs losses; ties dropped; the report's form, which measures departure from 0.5 in either direction, so it is read together with wins and losses) |
| Rationale for (c) | Under the first version of this gate (references (a) and (b) only, written earlier on 2026-10-07) the constant majority-class forecast `null_always_risk_on` had RPS skill +0.125 vs climatology and +0.630 vs the trend null and won 6 of 9 research episodes against the trend null (p = 0.164); one more winning episode would have let a constant 'always easing' forecast pass Gate 1 from the base rate alone. Closed on 2026-10-07, before any engine emitted probabilities, by requiring the engine to beat the constant forecast episode by episode as well (owner decision). The constant is now a reference and cannot beat itself |
| Option C (owner decision 2026-10-07, made before any engine emitted probabilities) | Era-B research cases with a regime target join the set to add tightening examples (research era A has 25 easing / 2 tightening, both in `EP18-2022-INFL`). Effect on research: +1 case, +1 episode, +1 tightening case (1981). The gate decision uses the combined set; era A only and era B only are reported, as are class-balanced RPS (mean of the per-class case-level mean RPS) for the engine and each reference and a per-episode table with era and target classes |
| Hard tightening requirement (owner decision 2026-10-07, made before any engine emitted probabilities) | An engine that cannot call tightening fails Gate 1: on all research cases whose target is tightening (era A + era B), the engine's case-level mean RPS must be lower than `null_always_risk_on`'s on the same cases (tightening-subset skill vs always-easing > 0). Applied in addition to the every-reference rule. Reported: tightening n and episodes, the engine's and each reference's tightening-subset RPS, the skill. Research: n = 3 cases in 2 episodes (≥ 3, so not flagged low power, but only 2 episodes); with fewer than 3 tightening cases the rule still applies and low power is flagged here and on the leaderboard |
| Pass (complete) | every-reference rule AND hard tightening requirement |
| Multiple testing | Research staging use only; every engine run is a trial in `results\versions\trials.jsonl`; Holm and Bonferroni over all N trials are shown next to the raw p |
| Holdout | Scored once at E7 with the same statistic and reported with the Bayes factor; not re-gated. Gate 2 remains the hard go/no-go |

### Diagnostics (reported next to their chance levels; not gated)

| # | Diagnostic | Definition | Chance level |
|---|---|---|---|
| 8 | Bracketed daily path agreement | Trading days between two consecutive agreeing regime statements (research cases with a regime target, era A and era B) at most 12 calendar months apart, endpoints included; holdout-episode ranges masked; conflicting days dropped; a day's episode = the earlier statement's. Agreement = share of labelled days where the model's daily `regime_direction` equals the label; 95% CI from the episode-level bootstrap | Σ_k share_label,k × share_model,k |
| 9 | Turning-point matching | His regime changes: consecutive research regime statements with different targets (rule (a) of section 5a without its 18-month lookback, a technical necessity: the research gaps are 19–30 months, so the bounded rule finds none), change date interval-censored to (last old-view, first new-view]. In the search window the model's daily direction is censored to spells ≥ 63 trading days; turn = first censored spell start in the new regime. Position before / inside / after the interval or missed; lead = trading days from the turn to the first new-view statement; extra turns = other censored changes in the window | — (descriptive) |
| 5 | Cohen's κ and balanced accuracy | argmax direction at asof on the Gate 1 set (a missing forecast is its own wrong class); balanced accuracy = mean recall over target classes present | κ 0; BA 1 / #classes present |
| 7 | AUC on P(tightening) | tightening vs other targets at asof; ties ½; cases without a forecast excluded (n reported) | 0.5 |

### Null baselines on the combined set (research, corpus `cbc5936cac102800`, 2026-10-07, `python -m fatpitch.versions run-nulls`)

Gate 1, k = 10 episodes, 28 cases. Cells: skill vs the reference / exact one-sided p / wins-losses-ties. CB-RPS = class-balanced RPS. A reference null is not compared with itself and has no pass value.

| Reference / null | RPS | CB-RPS | vs LOEO climatology | vs `null_trend_12m` | vs `null_always_risk_on` | Binding p | Tightening RPS (n 3) / skill vs easing | Pass |
|---|---|---|---|---|---|---|---|---|
| LOEO climatology | 0.183 | 0.422 | — | — | — | — | 0.817 / — | — |
| `null_always_risk_on` | 0.176 | 0.431 | +0.036 / 0.266 / 8-2-0 | +0.283 / 0.359 / 6-2-2 | (self) | 0.359 | 0.856 / (self) | — (reference) |
| `null_trend_12m` | 0.246 | 0.159 | −0.344 / 0.646 / 4-6-0 | (self) | −0.394 / 0.652 / 2-6-2 | 0.652 | 0.006 / +0.993 | — (reference) |
| `null_fed_direction` | 0.411 | 0.353 | −1.248 / 0.916 / 3-7-0 | −0.673 / 0.844 / 2-5-3 | −1.332 / 0.938 / 1-6-3 | 0.938 | 0.290 / +0.662 | no |
| `null_persistence` | 0.636 | 0.691 | −2.478 / 1.000 / 0-10-0 | −1.588 / 0.975 / 1-8-1 | −2.608 / 1.000 / 0-9-1 | 1.000 | 0.904 / −0.056 | no |

By era (reported): era A (k 9) as before (always-easing RPS 0.101, trend 0.272, fed 0.362, persistence 0.595); era B (k 1, the 1981 tightening case): always-easing 0.856, fed direction 0.856, trend 0.006, persistence 1.000, LOEO climatology 0.781; a single era-B episode gives p ≥ 0.5.

Diagnostics of the nulls:

| Null | #8 agreement (chance) [95% CI] | #5 κ / BA | #7 AUC | #9 (E→T 2019-12-18..2022-06-10; T→E 2022-09-28..2024-05-07) |
|---|---|---|---|---|
| `null_always_risk_on` | 0.933 (0.933) [0.751, 1.000] | 0.000 / 0.500 | 0.500 | missed; missed |
| `null_trend_12m` | 0.600 (0.529) [0.271, 0.917] | 0.276 / 0.820 | 0.820 | inside, lead 327; after, −60 |
| `null_fed_direction` | 0.543 (0.466) [0.268, 0.820] | 0.067 / 0.573 | 0.613 | inside, lead 406, 3 extra; after, −102, 1 extra |
| `null_persistence` | 0.547 (0.574) [0.290, 0.777] | −0.034 / 0.260 | 0.464 | after, −83, 1 extra; after, −83, 2 extra |

#8: no era-B bracket exists (one era-B regime statement), so #8 still covers 1,137 era-A research trading days (easing 1,061, tightening 76) in 7 episodes after masking. #9: the era-B change 1981-12-31 → 2003-12-31 (tightening → easing) is excluded (interval > 36 months). The constant 0.9-easing forecast remains the strongest reference on episode-first RPS and is expected to bind for an engine; on the tightening subset it is the weakest (0.856), which the hard requirement exploits.

## 7. Gates (PLAN E.4, E.7)

Owner decision 2026-10-06: both gates use a case-by-case (paired) comparison with one pre-chosen best null, plus an absolute floor. The "+15 points over the best null" margin is no longer a gate; `margin_over_best_null` stays as a reported number.

| Gate | Phase | Subset | Best null (fixed before any engine run) | Condition (both required) | Fail |
|---|---|---|---|---|---|
| Gate 1 (regime staging gate, options B + C; owner decisions 2026-10-07) | E3 | Research cases with a regime target, era A and era B (28 cases, 10 episodes), research split only | LOEO climatology, `null_trend_12m`, `null_always_risk_on` (references, section 6c) | For each reference: (1) episode-first RPS skill > 0; (2) one-sided exact episode-level sign-flip test p < 0.10; and (3) tightening-subset mean RPS below `null_always_risk_on`'s. Binding p = the largest. Holdout: scored once at E7, reported with a Bayes factor, not re-gated | back to E1 |
| Gate 2 | E4 | Era-A cases with thesis targets, full corpus: 43 cases, 14 episodes (final test on the holdout split, section 9) | `null_trend_12m` (highest era-A thesis score in the unlogged check: 0.461) | (1) paired sign-flip test of per-case thesis scores against `null_trend_12m`, one-sided, N 10000, seed 20261006: p < 0.10; (2) engine thesis recall (episode-first aggregate) ≥ 0.50. Same paired form as Gate 1, applied for consistency | back to E1/E3 |
| Expression | E4 | all | — | reported against nulls; no gate in v1 | — |
| 13F QoQ tilt-change sign agreement | E4 | 13F cases | — | tilt component reported against `null_tilt_no_change` and `null_tilt_persistence`; no gate | — |
| Era B, cash fidelity, size band | E6 | — | — | reported per case; no gate | — |
| Fat-pitch frequency | E7 | — | — | calibration target only; scored on held-out years only | — |

Implementation: Gate 1 `fatpitch.cases.regime.regime_gate(engine_rps, climatology_rps, trend_rps)` with rows from `fatpitch.cases.regime.case_rps` (section 6c); Gate 2 `fatpitch.cases.paired_gate(engine_result, best_null_result, "thesis", 0.50)` with both results run on `Corpus.subset(era="A")`. Research iteration: `python -m fatpitch.versions` (research split only). Reported alongside, not gated: regime diagnostics #5, #7, #8, #9 (section 6c); full-corpus and all-era scores; the date-shuffle permutation test (section 6); margins over every null; thesis recall on era-A turning points (best null there: `null_trend_12m` 0.453).

Best-null choice: fixed here from the unlogged pipeline check of 2026-10-06 (`tools\null_smoke.py`; era-A turning-point regime: trend 0.812, always-risk-on 0.562, fed-direction 0.500, persistence 0.250; era-A thesis, full corpus: trend 0.461, always-risk-on 0.301, fed-direction 0.211, persistence 0.164). It is not re-selected after the engine runs. If the corpus or a null definition changes before registration, the choice is re-made from a null-only run and recorded here before any engine run.

Re-check after the 2026-10-06 corpus expansion (68 cases; holdout re-sealed, `spec\HOLDOUT.md` Re-seal log): null-only, unlogged `tools\null_smoke.py` run on the research split only (2026-10-06T20:17Z; the full corpus cannot be run without unsealing). Research era-A turning-point regime (6 cases, 4 episodes): trend 0.812, fed-direction 0.500, always-risk-on 0.250, persistence 0.125. Research era-A thesis (27 cases, 8 episodes): trend 0.607, always-risk-on 0.324, fed-direction 0.234, persistence 0.108. `null_trend_12m` remains the highest on both gate components; the best-null choice is unchanged.

Gate 1 references (option B, owner decisions 2026-10-07): LOEO climatology and `null_trend_12m` (fixed by the report, `spec\regime_evaluation_options.md` §3) and `null_always_risk_on` (added the same day, section 6c rationale); none is re-selected. They replace the timing comparator chosen earlier the same day (retired with section 6b). Baseline values: section 6c.

Power: Gate 1 (section 6c) uses episodes as the unit: research k = 10 episodes (era A + era B), smallest attainable exact one-sided p = 1/1024; p < 0.10 needs at least 4 episodes all won, or more episodes with a few small losses. Gate 2 (paired, case-level): with n pairs, ties contribute nothing; the smallest attainable p is about 2^-k for k informative pairs. The case-level paired test treats cases as independent; cases in the same episode are not, so its p is optimistic relative to an episode-level test.

Every scoring run (engine or null) after registration goes through `fatpitch.prereg.record_run`; the count of logged runs is the DSR `n_trials`.

## 8. Differences from PLAN text and open points

| Item | PLAN / review text | Implemented v1 rule |
|---|---|---|
| Thesis | 1 if class+direction(+region) match in window | Fraction of target theses matched (identical for single-thesis cases) |
| Expression | review: top-3 "at the first matching thesis date" | Top-3 on any window day |
| Action | "tier/exit implies same action" | Equality of the engine's `action` field; mapping tier/exit → action is an engine-side responsibility (E6) |
| Log-score variant | where probabilities exist | Closed 2026-10-07: regime probabilities are part of Decision schema 2 and scored with the RPS (section 6c), which is finite for deterministic nulls; the log score is not used |
| Regime vocabulary | review: easing / tightening / neutral | Same; null 1 maps "risk-on" to easing; null 3 takes regime from the rates trend |
| 13F tilt-sign metric | beats no-change persistence | Tilt component (section 3) at `asof` only, against two baselines: no change (scores 0 by construction) and previous-quarter change persistence; the expression component is also scored |
| Gate 1 | PLAN E.4 before owner decisions: all era-A cases, ≥ best null + 15 points, date-permutation p < 0.10 | Closed 2026-10-07: RPS skill gate on era-A research regime cases vs LOEO climatology and `null_trend_12m`, exact episode sign-flip p < 0.10 (section 6c). Superseded designs: paired agreement vs best null (section 6a) and the timing gate (section 6b), both retired |
| Regime stage evaluation (review findings 5, 10, 16) | regime agreement vs base rate; episodes as the effective unit | Closed 2026-10-07: proper score with skill vs climatology, episode-level exact test, chance-corrected diagnostics (κ, BA, AUC), bracketed path agreement with holdout masking, interval-censored turning points (section 6c) |
| Turning points for regime timing | rule (a) with 18-month lookback | Diagnostic #9 uses rule (a) without the lookback (research gaps 19–30 months); section 5a is unchanged for breakdowns |
| Gate 2 | thesis recall ≥ best null + 15 points | Era-A full corpus; paired sign-flip vs pre-chosen best null (p < 0.10, N 10000) and recall ≥ 0.50 |
| Turning-point lookback | owner text: 18 months for the regime comparison | 18 months also bounds rule (c); rule (a) compares with the last earlier case that has a regime target (both confirmed by the owner 2026-10-06) |
| Fed-direction input | sign of last fed funds change (review) | 182-day change of `FEDFUNDS` (daily `DFF` not in the lake) |

## 9. Research/holdout split (`fatpitch.cases.holdout`; `spec\HOLDOUT.md`; 2026-10-06)

The corpus is split by episode into a research set and a sealed holdout (`cases\HOLDOUT.yaml` version 2, seed 20261006, stratified draw: 7 of 20 episodes, 26 of 68 cases; version 1 drew 6 of 19 episodes, 19 of 56 cases, and was superseded by the documented re-seal of 2026-10-06 before any unseal or engine run). Rule iteration in `spec\` runs on the research split only; the final Gate 1 and Gate 2 tests (section 7) run once on the holdout split.

| Item | Rule |
|---|---|
| Default load | `load_corpus(root)` = `split="research"`; turning points (section 5a) derived on research cases only, so no holdout target reaches a research label |
| Sealed load | `split="holdout"` or `"all"` requires `unseal=True`, environment `FATPITCH_UNSEAL=1` and a non-empty `reason`; each unseal appends a line to `cases\UNSEAL_LOG.txt`; turning points derived on the full corpus (section 5a as written) |
| Tamper check | Every load recomputes the holdout hash and raises `HoldoutError` if it differs from `HOLDOUT.yaml` |
| Gate 1 set | Research: cases with a regime target, era A and era B, 28 cases, 10 episodes (staging gate, section 6c). Holdout: cases with a regime target, era A and era B, at most 7 episodes (`cases\HOLDOUT.yaml` counts; regime-target counts not inspected), scored once at E7 and reported with a Bayes factor, not re-gated |
| Final Gate 2 subset | Holdout era-A cases with thesis targets: 16 cases, 6 episodes (research: 27 cases, 8 episodes) |
| Gate 1 power | Research: k = 10 episodes, smallest exact p = 1/1024. Holdout: at most 7 episodes, smallest exact p ≥ 1/128 (reported, not gated) |
| Best null | Gate 2: the section 7 best-null choice was made on the full corpus before the split (null-only run, no engine) and re-checked on the research split after the expansion (section 7); it stands. Gate 1: references LOEO climatology and `null_trend_12m` (section 6c), fixed by the owner decision of 2026-10-07 |

The counts in sections 5a and 7 describe the full corpus; the gate decision uses the holdout counts above.
