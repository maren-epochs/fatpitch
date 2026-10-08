# Numbers review — chosen parameters, ranked

Date: 2026-10-06. Scope: every number in `spec\registry.yaml` tagged `interpreted` (choices made while writing the spec, not numbers Druckenmiller gave), including formula constants moved out of `spec\process.md` in this pass and three entries retagged from `stated`. Nothing was removed, merged or dropped; the four article-origin gates (R-34..R-37) stay at weight 0. No value was chosen or changed by checking how the engine would score the cases; that is reserved for the pre-registered leave-one-episode-out calibration. Evidence and arithmetic for each entry are in its registry `notes`.

Ranking: review priority = evidence weakness (none 3, convention 2, anchored 1, direct 0) + behavioral impact (high 3: changes which theses fire, the veto, tier or size in most periods; medium 2: one rule or a subset of periods; low 1: display, flags, data guards). Ties: tunable first, then impact, then id.

## 1. Decisions (owner decisions recorded 2026-10-06)

Value column = registry value after the decisions. Option A was the value before the decisions. Decisions are applied in `spec\registry.yaml` (notes carry 'Owner decision 2026-10-06'); items marked PENDING are unchanged until research completes.

| # | Rank | Parameter | Value | Meaning | Options | Recommended | Decision (2026-10-06) |
|---|---|---|---|---|---|---|---|
| D1 | 1 | `liq.m2_ip.spread_pp` | 3.5 | M2 growth must beat IP growth by this many points to count as 'a lot faster' | **A** keep 2.0, tunable over [0, 6]<br>**B** 0 (any excess money growth counts)<br>**C** 3.0 fixed<br>**D** tunable over a narrower [1, 4] | **A** — 'a lot faster' has no number; the wide range lets leave-one-episode-out pick within a pre-set band | A (research option A, `specesearch_D1_D3_D7.md`) — 3.5 (was 2.0), tunable [1, 7]; `liq.growth_window_m` stays 12; R-02 PIT note corrected (no M2 break May 2020; 2020-03..2021-12 flagged base-effect outliers) |
| D2 | 2 | `tier.min_independent_evidence` | 3 | evidence families needed to go from starter to fat pitch | **A** keep 3, tunable over [2, 4]<br>**B** 2 fixed<br>**C** 4 fixed | **A** — count is not stated; already tunable | A — 3, tunable [2, 4] |
| D3 | 3 | `xasset.window_m` | 6 | months over which rates, oil and dollar must all rise for the warning | **A** keep 3, tunable over [3, 12]<br>**B** 6 fixed<br>**C** 12 fixed<br>**D** tunable over [1, 12] | **A** — no window stated; range already spans quarterly to annual | A (research option A) — 6 (was 3), tunable [3, 12]; new non-tunable `xasset.min_move_sd` = 0.25, reported [0, 0.5], reported variant only (main rule direction-only) |
| D4 | 4 | `bear.fragility_lookback_m` | 12 | months before a decline in which high fragility marks it post-bubble | **A** keep 12<br>**B** 6<br>**C** 24<br>**D** 12, reported across [6, 24] | **A** — no window stated; 12 months matches the annual cadence of the slowest fragility input (Ritter IPO data) | 12, reported range [6, 24] (non-tunable) |
| D5 | 5 | `chart.monthly_roc_change_m` | 6 | months over which the change in monthly ROC is read | **A** keep 3<br>**B** 1<br>**C** 6 | **A** — no window stated; 3 months = one quarter, the same short window used elsewhere in the registry | 6 (was 3), reported range [3, 12]; report 12 and highlight 3 in sensitivity tables |
| D6 | 6 | `infl.lookback_m` | 24 | months CPI above 4.5%/5% stays 'recent' for the no-soft-landing flags | **A** keep 24, report across [12, 36]<br>**B** 12<br>**C** 36<br>**D** 0 (only while CPI is above the threshold now) | **A** — no window stated; range already set | A — 24, reported [12, 36] |
| D7 | 7 | `internals.breadth_thrust` | classic Zweig on NYSE A/D (10-day EMA of adv/(adv+dec) from <0.40 to >0.615 within 10 days); S&P 500 members 0.40/0.646 from 2021-09; industry fallback in the 2020–21 gap | definition of a breadth thrust (share of industries above trend) | **A** keep: industries above trend <20% -> >80% within 10 weeks<br>**B** Zweig original applied to industries: 10-day average share rising from <40% to >61.5% within 10 days<br>**C** thrust = A or B<br>**D** use A; report fidelity under A and B | **D** — neither definition is his; reporting both shows whether the R-60 override depends on the choice without fitting it | A (research option A) — classic Zweig on NYSE A/D (Unicorn 1965-03-01..2020-02-10); S&P 500 members from 2021-09-22 with `internals.breadth_thrust_spx_low`/`_high` = 0.40/0.646 (provisional); gap 2020-02-11..2021-09-21 = previous industry definition (`internals.breadth_thrust_industry_fallback`), flagged; WSJ Markets Diary snapshot forward; sensitivities: up-volume, % > 50dma thrust |
| D8 | 8 | `liq.confirm_periods` | 2 | readings a liquidity sign change must persist before it counts | **A** keep 2<br>**B** 1 (no confirmation)<br>**C** 3<br>**D** 2, with fidelity reported across [1, 3] | **D** — touches every liquidity transition; reporting the range exposes sensitivity at no fitting cost | A — 2, reported [1, 3] |
| D9 | 9 | `policy.ff_change_window_m` | 6 | Fed direction = sign of fed funds change over this many months | **A** keep 6, report across [3, 12]<br>**B** 3<br>**C** 12<br>**D** direction of the most recent target change (no window) | **A** — 6 flips at the first hike in most cycles; D changes rule mechanics and needs a spec edit | A — 6, reported [3, 12] |
| D10 | 10 | `size.cold_multiplier` | 0.33 | size multiplier when the scorecard is down on the year | **A** keep 0.33 (= starter size)<br>**B** 0.5<br>**C** 0 (no new risk when cold)<br>**D** 0.33, reported across [0, 0.5] | **A** — 'not earned the right to play big' implies small, not zero; 1/3 matches his stated starter size | A — 0.33, no range |
| D11 | 11 | `size.neutral_multiplier` | 0.75 | size multiplier when neither hot nor cold | **A** keep 0.66<br>**B** 0.5<br>**C** 1.0 (only being cold cuts size)<br>**D** 0.66, with size-band agreement reported across [0.5, 1.0] | **D** — applies most of the time and sets size-band agreement; no source magnitude | 0.75 (was 0.66), reported [0.5, 1.0] |
| D12 | 12 | `tier.catalyst_window_bd` | 20 | days ahead a scheduled event counts as a near catalyst | **A** keep 20<br>**B** 10<br>**C** 40<br>**D** 20, with fidelity reported across [10, 40] | **D** — no source window; high impact on fat-pitch tier | A — 20, reported [10, 40] |
| D13 | 13 | `chart.trend_lookback_w` | 40 | weeks in the weekly trend line used by the chart veto | **A** keep 40, tunable over [20, 52]<br>**B** widen range to [10, 52] (covers Feig's 8-20 week horizon) | **A** — Feig's 8-20 weeks is a forecast horizon, not a look-back | A — 40, tunable [20, 52] |
| D14 | 14 | `fragility.high_percentile` | 80 | composite fragility percentile that counts as high | **A** keep 80, tunable over [70, 90]<br>**B** 90 fixed<br>**C** fix 80 (frees one tunable slot) | **A** — already tunable; no source level | A — 80, tunable [70, 90] |
| D15 | 24 | `policy.taylor_rstar_pct` | 2.0 | neutral real rate in the rule rate | **A** keep 2.0 fixed<br>**B** real-time Laubach-Williams r* (vintaged)<br>**C** 2.0 fixed; report fidelity with Laubach-Williams as sensitivity | **C** — he cites the traditional rule, but r* shifts the policy-error sign one-for-one; sensitivity costs nothing | A/C — 2.0 fixed; sensitivity with real-time Laubach-Williams r* (`policy.taylor_rstar_sensitivity`) |
| D16 | 36 | `internals.qe_signal_weight` | 0.5 | weight on bond/credit signals while QE runs | **A** keep 0.5, report across [0, 0.5]<br>**B** 0 (literal 'destroyed')<br>**C** 0.25<br>**D** 1.0 (no impairment) | **A** — his wording points below 0.5 but the spec text says 'halved'; reporting [0, 0.5] covers the literal reading | A — 0.5, reported [0, 0.5] |
| D17 | 41 | `curve.cut_pricing_bp` | 50 | 2y yield this far below/above fed funds = cuts/hikes priced | **A** keep 50, tunable over [25, 100]<br>**B** keep 50, narrow tunable range to [25, 50]<br>**C** fix 50 (frees one tunable slot) | **B** — his 2019 statements bracket the threshold in (8, 53] bp; values above 53 contradict his reading of the 1.85% 2-year | B — 50, tunable range narrowed to [25, 50] |

Gap G1 (decided 2026-10-06): R-31 crowding had no threshold. Options were A leave undefined / B 90 / C 80; recommended A. Decision: B — `crowd.cot_crowded_percentile` = 90, reported range [80, 95], basis = COT net speculative position percentile over trailing 3 years; referenced in R-31.

## 2. Full ranked list

### 2a. Priority 1 — no evidence, high impact (12)

| Rank | Parameter | Value | Plain meaning | Evidence | Impact | Tunable | Recommendation |
|---|---|---|---|---|---|---|---|
| 1 | `liq.m2_ip.spread_pp` | 2.0 | M2 growth must beat IP growth by this many points to count as 'a lot faster' | none | high | yes | see D1 |
| 2 | `tier.min_independent_evidence` | 3 | evidence families needed to go from starter to fat pitch | none | high | yes | see D2 |
| 3 | `xasset.window_m` | 3 | months over which rates, oil and dollar must all rise for the warning | none | high | yes | see D3 |
| 4 | `bear.fragility_lookback_m` | 12 | months before a decline in which high fragility marks it post-bubble | none | high | no | see D4 |
| 5 | `chart.monthly_roc_change_m` | 6 | months over which the change in monthly ROC is read | none | high | no | see D5 |
| 6 | `infl.lookback_m` | 24 | months CPI above 4.5%/5% stays 'recent' for the no-soft-landing flags | none | high | no | see D6 |
| 7 | `internals.breadth_thrust` | share of industries above trend rises from <20% to >80% within 10 weeks | definition of a breadth thrust (share of industries above trend) | none | high | no | see D7 |
| 8 | `liq.confirm_periods` | 2 | readings a liquidity sign change must persist before it counts | none | high | no | see D8 |
| 9 | `policy.ff_change_window_m` | 6 | Fed direction = sign of fed funds change over this many months | none | high | no | see D9 |
| 10 | `size.cold_multiplier` | 0.33 | size multiplier when the scorecard is down on the year | none | high | no | see D10 |
| 11 | `size.neutral_multiplier` | 0.75 | size multiplier when neither hot nor cold | none | high | no | see D11 |
| 12 | `tier.catalyst_window_bd` | 20 | days ahead a scheduled event counts as a near catalyst | none | high | no | see D12 |

### 2b. Priority 2 — convention with high impact, or no evidence with medium impact (28)

Recommendation keep unless a decision is referenced. Conventions are named in each registry note.

| Rank | Parameter | Value | Plain meaning | Evidence | Impact | Tunable | Recommendation |
|---|---|---|---|---|---|---|---|
| 13 | `chart.trend_lookback_w` | 40 | weeks in the weekly trend line used by the chart veto | convention | high | yes | see D13 |
| 14 | `fragility.high_percentile` | 80 | composite fragility percentile that counts as high | convention | high | yes | see D14 |
| 15 | `internals.rs_lookback_m` | 6 | months of relative strength for leading industries | convention | high | yes | keep |
| 16 | `bear.decline_pct` | 20 | index fall that defines a bear market | convention | high | no | keep |
| 17 | `chart.daily_roc_d` | 20 | days in the daily rate of change | convention | high | no | keep |
| 18 | `chart.monthly_roc_m` | 12 | months in the monthly rate of change | convention | high | no | keep |
| 19 | `chart.rs_bottom_quantile` | 0.2 | relative strength in the bottom fifth fails the chart | convention | high | no | keep |
| 20 | `chart.timing_cutover_year` | 2010 | year technicals start counting at reduced weight | convention | high | no | keep |
| 21 | `liq.growth_window_m` | 12 | M2 and IP growth measured year over year | convention | high | no | keep |
| 22 | `liq.netliq.window_w` | 13 | weeks over which Fed-net-liquidity change is measured | convention | high | no | keep |
| 23 | `policy.holdings_change_window_w` | 13 | weeks over which Fed bond-holdings change sets taper/QE direction | convention | high | no | keep |
| 24 | `policy.taylor_rstar_pct` | 2.0 | neutral real rate in the rule rate | convention | high | no | see D15 |
| 25 | `exit.pvn_consecutive_releases` | [1, 2] | bad price reactions in a row that trigger an exit flag [before, after cutover] | none | medium | no | keep |
| 26 | `exit.top_atr_mult` | 1.0 | ATRs below the recent high required for a top | none | medium | no | keep |
| 27 | `exit.top_high_window_w` | 10 | weeks defining the recent high in the top test | none | medium | no | keep |
| 28 | `exit.top_partial_fraction` | 0.5 | share of a winner sold at a technical top | none | medium | no | keep |
| 29 | `exit.top_roc_flat_w` | 4 | weeks of flat momentum that define a top | none | medium | no | keep |
| 30 | `expr.second_order_top_n` | 3 | number of second-order expressions kept | none | medium | no | keep |
| 31 | `fiscal.issuance_median_y` | 5 | years of history defining normal Treasury issuance | none | medium | no | keep |
| 32 | `fragility.size_multiplier_long` | 0.66 | long size multiplier when fragility is high | none | medium | no | keep |
| 33 | `internals.curve_credit_trend_m` | 3 | months over which curve and credit direction is read | none | medium | no | keep |
| 34 | `internals.narrowing_drop_pts` | 20 | fall in share of industries above trend that = narrowing | none | medium | no | keep |
| 35 | `internals.narrowing_window_m` | 6 | months over which narrowing is measured | none | medium | no | keep |
| 36 | `internals.qe_signal_weight` | 0.5 | weight on bond/credit signals while QE runs | none | medium | no | see D16 |
| 37 | `internals.turn_confirm_m` | 2 | months an industry-RS turn must persist | none | medium | no | keep |
| 38 | `liq.instrument_min_adv_usd` | 50000000 | minimum daily dollar volume to trade an instrument | none | medium | no | keep |
| 39 | `rates.ngdp_cheap_gap_pp` | 2.0 | 10y yield this far above nominal GDP growth = bonds cheap | none | medium | no | keep |
| 40 | `xregion.window_w` | 26 | weeks over which regional balance-sheet change is measured | none | medium | no | keep |

### 2c. Approve as-is — lower priority (31; 30 recommended keep without a decision)

Summary: anchored or direct values, medium- and low-impact conventions, and low-impact constants without evidence (flags, data guards, timestamps). Approving this block accepts all rows below except those pointing to a decision.

| Rank | Parameter | Value | Plain meaning | Evidence | Impact | Tunable | Recommendation |
|---|---|---|---|---|---|---|---|
| 41 | `curve.cut_pricing_bp` | 50 | 2y yield this far below/above fed funds = cuts/hikes priced | anchored | high | yes | see D17 |
| 42 | `policy.tg_threshold_pp` | 2.0 | Fed funds this far from the rule rate = policy error | anchored | high | yes | keep |
| 43 | `chart.timing_weight` | 0.2 | weight on timing evidence after the cutover year | anchored | high | no | keep |
| 44 | `internals.thrust_override_m` | 6 | months a breadth thrust overrides bad liquidity | anchored | high | no | keep |
| 45 | `size.asymmetry_full_ratio` | 10 | upside/downside at which size is no longer scaled down | anchored | high | no | keep |
| 46 | `size.asymmetry_min_ratio` | 5 | minimum upside/downside for a fat pitch | anchored | high | no | keep |
| 47 | `exit.price_vs_news_window_bd` | 5 | days after a release over which price reaction is read | convention | medium | no | keep |
| 48 | `expr.beta_window_w` | 156 | weeks of returns used to rank instruments by sensitivity | convention | medium | no | keep |
| 49 | `expr.second_order_min_abs_corr` | 0.5 | minimum correlation for a second-order expression | convention | medium | no | keep |
| 50 | `fci.change_window_w` | 13 | weeks over which NFCI direction is measured | convention | medium | no | keep |
| 51 | `fci.loose_threshold` | 0.0 | NFCI level below which conditions are loose | convention | medium | no | keep |
| 52 | `internals.industry_trend_w` | 40 | weeks in the trend line for 'industry above trend' | convention | medium | no | keep |
| 53 | `policy.taylor_infl_coef` | 0.5 | rule-rate response to inflation above target | convention | medium | no | keep |
| 54 | `policy.taylor_pi_target_pct` | 2.0 | inflation target in the rule rate | convention | medium | no | keep |
| 55 | `policy.taylor_ugap_coef` | 1.0 | rule-rate response to unemployment below its natural rate | convention | medium | no | keep |
| 56 | `size.adv_participation` | 0.1 | share of daily volume assumed tradable when exiting | convention | medium | no | keep |
| 57 | `crowd.cot_crowded_percentile` | 90 | COT positioning percentile (trailing 3 years) at or above which a trade counts as crowded | none | low | no | keep |
| 58 | `crowd.max_entry_delay_bd` | 5 | maximum days crowding can delay an entry | none | low | no | keep |
| 59 | `fragility.min_components` | 2 | minimum gauges needed to compute fragility | none | low | no | keep |
| 60 | `pit.election_result_time` | 06:00 ET next day | time election results are treated as known | none | low | no | keep |
| 61 | `score.deviation_window_d` | 10 | days over which P&L deviation is measured | none | low | no | keep |
| 62 | `exit.premise_check_freq_bd` | 1 | how often premises are checked (business days) | direct | high | no | keep |
| 63 | `fiscal.deficit_gdp_pct` | 5.0 | deficit/GDP above which supply counts against bonds | anchored | medium | no | keep |
| 64 | `size.hot_multiplier` | 1.0 | size multiplier when hot | anchored | medium | no | keep |
| 65 | `exit.atr_window_d` | 14 | days in the ATR calculation | convention | low | no | keep |
| 66 | `fragility.credit_gdp_change_q` | 4 | quarters over which corporate debt/GDP change is measured | convention | low | no | keep |
| 67 | `liq.adv_window_d` | 20 | days in average daily volume | convention | low | no | keep |
| 68 | `score.deviation_sigma` | 2.0 | P&L deviation (sigmas) that raises a scorecard flag | convention | low | no | keep |
| 69 | `fiscal.active_from_year` | 2023 | first year the deficit rule is used | direct | medium | no | keep |
| 70 | `liq.qe_end_setback_m` | 6 | months after QE ends in which an equity setback is expected | direct | medium | no | keep |
| 71 | `rates.ngdp_anchor_gap_pp` | 0.0 | 10y yield below nominal GDP growth = bonds rich | direct | medium | no | keep |

## 3. Retagged stated → interpreted

| Parameter | Value | Reason | Evidence |
|---|---|---|---|
| `chart.timing_weight` | 0.2 | the number (technicals '20% as effective') is his; using it as a weight is a mapping. Arithmetic: pre-algorithm weight 1.0 x 0.20 effectiveness = 0.2. | anchored |
| `rates.ngdp_anchor_gap_pp` | 0.0 | 'the ten year's to trade around where nominal GDP is' -> anchor gap 0 is his; using 0 as a one-sided threshold (below = rich) rather than a band is a mapping. | direct |
| `liq.qe_end_setback_m` | 6 | 'about six months' is his per an attendee write-up (reliability: secondary summary). Spec convention requires a primary or near-primary note for stated. | direct |

Reviewed and kept `stated`: `exit.review_window_w` [2, 3] (his 2-3 weeks of analyst work after entry), `size.exit_cost_max_pct_nav` [1, 2] (stated band; the 1 at starter / 2 at fat pitch split is an interpreted sub-choice noted in the entry), `size.starter_fraction`, all sizing caps, inflation thresholds, horizons and leads. Stated bands added as descriptive ranges: `size.hot_ytd_threshold` [0.20, 0.30], `short.rally_min_pct` [15, 20].

## 4. Not moved

| Item | Constant | Why not moved |
|---|---|---|
| `transition_table.yaml` T03 invalidation | CPI 6-month annualised | Table frozen (authored before case reading); changing it requires re-registration. Evidence: none; impact medium. |
| R-34/R-35 article gates | forensic score ≥ 45; ROIC > 15%, Debt/EBITDA < 2.5× | Article's numbers, not chosen here; weight 0. |
| PIT lags in process.md (French data month-end + 30 days; Ritter Jan of year+1) | data timing | Data-availability assumptions for the data lift, not process parameters. |

## 5. Counts

| Evidence grade | Count |
|---|---|
| direct | 4 |
| anchored | 8 |
| convention | 26 |
| none | 33 |
| **total chosen numbers** | **71** |

Origin: 28 existing interpreted entries, 39 formula constants moved into the registry, 3 retagged from stated, 1 added by owner decision (G1); `policy.taylor_rstar_sensitivity` (D15) is a non-numeric switch and not counted. Tunable: 8 (cap 8; none added). Impact: 31 high, 31 medium, 9 low.
