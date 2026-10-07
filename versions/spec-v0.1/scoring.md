# Fat Pitch — Scoring Rule, Null Models and Gates v1 (phase E2)

Date: 2026-10-06. Status: candidate for pre-registration together with `spec\process.md`, `spec\registry.yaml`, `spec\transition_table.yaml` and `spec\corpus_manifest.txt` (`python -m fatpitch.prereg register-all`). Not registered (awaiting owner review). This file describes what PLAN E.4 requires and what `src\fatpitch\cases\scoring.py`, `src\fatpitch\cases\nulls.py` and `src\fatpitch\cases\schema.py` implement; where the two differ, the implemented rule is stated and the difference is listed in section 8. Any change after the first scoring run is a design change (re-register, new report).

## 1. Units

| Item | Definition |
|---|---|
| Case | One YAML file in `cases\` (schema `fatpitch.cases.schema`). Fields used for scoring: `asof`, `era`, `episode_id`, `truth_type`, `mechanizable`, `source_reliability`, `targets`, `window`. Metadata (`citation`, `date_basis`, `retrospective`, `seed_id`, `notes`, `derivation`) is never read by scoring or engines |
| Engine | Any object with `name` and `predict(asof, source) -> Prediction`. Receives only an ET-close `asof` and a `Source`; never a case, a target or an outcome |
| Prediction | `regime_direction` (easing / neutral / tightening / None), `theses` (asset_class, direction long/short, region), `expressions` (ranked families, best first), `action` (enter / size_up / reduce / exit / reverse / flat / hold / None), `tilts` (13F family → −1/0/+1) |
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

Series ids for nulls 2 and 3 are constructor arguments; the v1 mapping above is the registered one (`tools\null_smoke.py` builds it from the amber lake, read-only). A series missing at a date yields an empty prediction component for that date.

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

Per case scored by both the engine and the null on the gate component: d_i = engine_i − null_i. Statistic: mean(d). Null distribution: mean(s_i · d_i) with independent signs s_i ∈ {−1, +1}, equal probability, drawn as an (N × n) array by `numpy.random.default_rng(20261006).choice([-1, 1])`, N = 10000. One-sided p = (1 + #{permuted ≥ observed − 1e-12}) / (1 + N). Case-level, unweighted (not episode-first).

## 7. Gates (PLAN E.4, E.7)

Owner decision 2026-10-06: both gates use a case-by-case (paired) comparison with one pre-chosen best null, plus an absolute floor. The "+15 points over the best null" margin is no longer a gate; `margin_over_best_null` stays as a reported number.

| Gate | Phase | Subset | Best null (fixed before any engine run) | Condition (both required) | Fail |
|---|---|---|---|---|---|
| Gate 1 | E3 | Era-A turning-point cases (section 5a) with a regime target: 12 cases, 8 episodes (full corpus; final test on the holdout split, section 9) | `null_trend_12m` (highest subset regime score in the unlogged check: 0.812) | (1) paired sign-flip test (section 6a) of the engine's per-case regime scores against `null_trend_12m`'s per-case regime scores, one-sided, N 10000, seed 20261006: p < 0.10; (2) engine regime agreement (episode-first aggregate, section 5) on the subset ≥ 0.80 | back to E1 |
| Gate 2 | E4 | Era-A cases with thesis targets, full corpus: 43 cases, 14 episodes (final test on the holdout split, section 9) | `null_trend_12m` (highest era-A thesis score in the unlogged check: 0.461) | (1) paired sign-flip test of per-case thesis scores against `null_trend_12m`, one-sided, N 10000, seed 20261006: p < 0.10; (2) engine thesis recall (episode-first aggregate) ≥ 0.50. Same paired form as Gate 1, applied for consistency | back to E1/E3 |
| Expression | E4 | all | — | reported against nulls; no gate in v1 | — |
| 13F QoQ tilt-change sign agreement | E4 | 13F cases | — | tilt component reported against `null_tilt_no_change` and `null_tilt_persistence`; no gate | — |
| Era B, cash fidelity, size band | E6 | — | — | reported per case; no gate | — |
| Fat-pitch frequency | E7 | — | — | calibration target only; scored on held-out years only | — |

Implementation: `fatpitch.cases.paired_gate(engine_result, best_null_result, component, floor)` with both results run on the gate subset (`Corpus.subset(era="A", turning_point=True)` for Gate 1; `Corpus.subset(era="A")` for Gate 2). Reported alongside, not gated: full-corpus and all-era scores; the date-shuffle permutation test (section 6); margins over every null; thesis recall on era-A turning points (best null there: `null_trend_12m` 0.453).

Best-null choice: fixed here from the unlogged pipeline check of 2026-10-06 (`tools\null_smoke.py`; era-A turning-point regime: trend 0.812, always-risk-on 0.562, fed-direction 0.500, persistence 0.250; era-A thesis, full corpus: trend 0.461, always-risk-on 0.301, fed-direction 0.211, persistence 0.164). It is not re-selected after the engine runs. If the corpus or a null definition changes before registration, the choice is re-made from a null-only run and recorded here before any engine run.

Re-check after the 2026-10-06 corpus expansion (68 cases; holdout re-sealed, `spec\HOLDOUT.md` Re-seal log): null-only, unlogged `tools\null_smoke.py` run on the research split only (2026-10-06T20:17Z; the full corpus cannot be run without unsealing). Research era-A turning-point regime (6 cases, 4 episodes): trend 0.812, fed-direction 0.500, always-risk-on 0.250, persistence 0.125. Research era-A thesis (27 cases, 8 episodes): trend 0.607, always-risk-on 0.324, fed-direction 0.234, persistence 0.108. `null_trend_12m` remains the highest on both gate components; the best-null choice is unchanged.

Power: era A has 16 turning points (above the 8-case threshold, so no pooled A+B report is required), but only 12 carry a regime target, in 8 episodes; era B adds one turning point without a regime target, so pooling would not enlarge the regime sample. With 12 pairs, cases where engine and null score the same contribute nothing to the sign-flip statistic; the smallest attainable p is about 2^-k for k informative pairs, so p < 0.10 needs at least 4 cases with a difference. The paired test treats cases as independent; cases in the same episode are not (8 episodes), so p is optimistic relative to an episode-level test.

Every scoring run (engine or null) after registration goes through `fatpitch.prereg.record_run`; the count of logged runs is the DSR `n_trials`.

## 8. Differences from PLAN text and open points

| Item | PLAN / review text | Implemented v1 rule |
|---|---|---|
| Thesis | 1 if class+direction(+region) match in window | Fraction of target theses matched (identical for single-thesis cases) |
| Expression | review: top-3 "at the first matching thesis date" | Top-3 on any window day |
| Action | "tier/exit implies same action" | Equality of the engine's `action` field; mapping tier/exit → action is an engine-side responsibility (E6) |
| Log-score variant | where probabilities exist | Not implemented; no engine emits probabilities in v1 |
| Regime vocabulary | review: easing / tightening / neutral | Same; null 1 maps "risk-on" to easing; null 3 takes regime from the rates trend |
| 13F tilt-sign metric | beats no-change persistence | Tilt component (section 3) at `asof` only, against two baselines: no change (scores 0 by construction) and previous-quarter change persistence; the expression component is also scored |
| Gate 1 | PLAN E.4 before owner decisions: all era-A cases, ≥ best null + 15 points, date-permutation p < 0.10 | Era-A turning-point cases with a regime target; paired sign-flip vs pre-chosen best null (p < 0.10, N 10000) and agreement ≥ 0.80 (section 7) |
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
| Final Gate 1 subset | Holdout era-A turning-point cases with a regime target: 6 cases, 4 episodes (research: 6 cases, 4 episodes) |
| Final Gate 2 subset | Holdout era-A cases with thesis targets: 16 cases, 6 episodes (research: 27 cases, 8 episodes) |
| Paired test power | Smallest attainable one-sided p on the holdout Gate 1 subset = 2^-6 ≈ 0.0156 when all 6 pairs differ; p < 0.10 needs at least 4 non-tied pairs. Research Gate 1 subset: 2^-6 ≈ 0.0156 |
| Best null | The section 7 best-null choice was made on the full corpus before the split (null-only run, no engine) and re-checked on the research split after the expansion (section 7); it stands and is not re-selected on either split |

The counts in sections 5a and 7 describe the full corpus; the gate decision uses the holdout counts above.
