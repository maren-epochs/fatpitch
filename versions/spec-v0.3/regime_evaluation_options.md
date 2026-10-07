# Fat Pitch — Regime-Stage Evaluation Options (Gate 1 redesign input)

Date: 2026-10-07. Status: research note for an owner decision. Changes nothing in `spec\scoring.md`, `PLAN.md` or code. Tags: **[D]** documented (repo file or cited source), **[I]** inference or arithmetic by the author of this note. All corpus numbers below are from the **research split only** (`load_corpus` default, sha `cbc5936cac102800`, 48 cases); no holdout target was read. Null predictions at `asof` are from `results\versions\nulls\cbc5936cac102800\*\predictions.parquet`.

## 0. Facts used

| Item | Value | Tag |
|---|---|---|
| Research era-A cases with a regime target | 27 cases, 8 episodes: 25 easing, 2 tightening, 0 neutral | [D] corpus |
| Episodes containing a non-easing target (research, era A) | 1 of 8 (`EP18-2022-INFL`, both tightening cases) | [D] corpus |
| Gate 1 set (era-A turning points with regime target) | research 2 cases / 2 episodes (turning points derived on research only); holdout 4 cases / 3 episodes (`spec\HOLDOUT.md` v3; `HOLDOUT.md` also shows research 4/3 when turning points are derived on the full corpus) | [D] |
| Research Gate 1 cases | `2008-06-30_commodities-exit-2008`, `2019-06-07_fed-repivot-equities-2019`: both target **easing**, both turning points by rule (b)/(c) (action), not by rule (a) (regime change) | [D] corpus, `LEADERBOARD.md` |
| Gate 1 headroom on research vs `null_always_risk_on` | 0 winnable cases | [D] `LEADERBOARD.md` |
| Regime transitions in his research-split reads | 2 (easing→tightening between 2019-12-18 and 2022-06-10; tightening→easing between 2022-09-28 and 2024-05-07) | [D] corpus dates |

Null behaviour at `asof`, research era-A regime cases (n = 27), computed for this note [D, computed]:

| Null | Confusion (target→pred) | Accuracy | Cohen's κ | Balanced accuracy (classes present) | Daily agreement in ±20-day windows |
|---|---|---|---|---|---|
| `null_always_risk_on` | E→E 25, T→E 2 | 0.926 | 0.000 | 0.500 | 0.926 |
| `null_trend_12m` | E→E 16, E→T 9, T→T 2 | 0.667 | 0.208 | 0.820 | 0.680 |
| `null_fed_direction` | E→E 12, E→T 11, E→N 2, T→T 2 | 0.519 | 0.129 | 0.740 | 0.483 |
| `null_persistence` | E→E 13, E→None 11, T→E 2, E→T 1 | 0.481 | −0.074 | 0.260 | 0.455 |

(Leaderboard regime scores, e.g. 0.800 for always-easing, are episode-first with the 0.5 window credit and include era B; the table above is case-level at `asof`.)

## 1. Why the current Gate 1 designs fail

| Design | Failure | Quantification | Tag |
|---|---|---|---|
| Original (PLAN_REVIEW finding 16): era-A regime agreement ≥ best null + 15 points, date-permutation p < 0.10 | Base rate. 92.6% of research reads are easing; a constant scores 0.926. A perfect engine can exceed it by at most 0.074 (2 cases). +15 points is arithmetically unreachable against the majority null | Max margin over always-easing = 7.4 points | [I] |
| Agreement test vs always-easing (any paired form) | Only discordant cases are informative; discordant ≤ 2 on research | Exact McNemar/sign test, 2/2 discordant won: p = 0.25. One-sample binomial vs 0.926: P(27/27) = 0.926^27 = 0.125 > 0.10 | [I] |
| Accuracy CI (finding 5 logic) | Interval too wide to separate engine from baseline | Wilson 95% CI at 25/27: 0.77–0.98 | [I] |
| Paired agreement vs `null_trend_12m` (2026-10-06 version) | Trend null hits both tightening cases; engine gains only on the 9 easing cases trend gets wrong, all in easing episodes. Works in principle, but the decisive minority class sits in one episode | Effective units ≈ 8 episodes; 1 informative minority episode | [I] |
| Timing gate (2026-10-07, §6b) vs `null_always_risk_on` | Degenerate comparator. Always-easing has max lead on every easing case (unwinnable) and no flip on every non-easing case (free win). Gate outcome is set by the holdout's target mix, not by the engine | Research headroom 0 → p ≥ 0.25 unreachable. Holdout: p = 2^-4 = 0.0625 only if all 4 cases are non-easing and all won; one easing case caps p at 0.125 → fail. If each holdout case is non-easing with probability q, a perfect engine passes with probability q^4 (q = 0.5 → 0.06; q = 0.25 → 0.004) | [D] §6b headroom; [I] q^4 |
| Timing gate, episode dependence | 4 holdout cases sit in 3 episodes; at episode level the floor p is 2^-3 = 0.125 | Gate cannot pass at the episode level under any result | [D] counts; [I] |
| Timing gate, staging purpose | Gate 1 is a staging check before E4, but its final test is on the sealed holdout, which is opened once at the end. Either the holdout is opened at E3 (burning it before Gate 2) or Gate 1 cannot stage anything | — | [I] |
| "Turning point" definition | Rules (b)/(c) mark action breaks; the research Gate 1 cases are easing→easing. A regime-timing gate is evaluated on cases with no regime change | 0 of 2 research Gate 1 cases are regime changes | [D] corpus |

Summary [I]: the regime target is nearly constant within the research era, the minority class lives in one episode, and the timing comparator is a constant. No test on this sample can reach p < 0.10 against the majority-class baseline on research; on the holdout the result depends on its unknown target mix.

## 2. Options from the literature, assessed for this setting

Assessment axes: **n** (cases / episodes / spells), **imbalance** (25:2), **autocorrelation** (cases within episodes; daily paths with spells of months to years), **PIT** (point-in-time and leakage).

### 2.1 Pesaran–Timmermann directional-accuracy test
- [D] PT (1992) tests independence of predicted and realised direction; null is independence, statistic asymptotically N(0,1); oversized in small samples ([EconPapers](https://econpapers.repec.org/RePEc:bes:jnlbes:v:10:y:1992:i:4:p:561-65); small-sample note in [Assessing the accuracy of directional forecasts, Applied Economics 2024](https://www.tandfonline.com/doi/full/10.1080/00036846.2024.2393902)). PT (2009) extends to multi-category, serially correlated variables via canonical correlations and dynamically augmented reduced-rank regressions ([JASA 104(485)](https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.0113)); Blaskowitz–Herwartz address serial correlation for directional forecasts ([IJF 2014](https://ideas.repec.org/a/eee/intfor/v30y2014i1p30-42.html)).
- Fit [I]: requires variance in the realised series; with 2/27 minority the variance estimate is near zero and the asymptotics do not hold. On daily paths the 2009 version is the correct form, but the effective sample is the number of spells (~3 research). Diagnostic at most.

### 2.2 Harding–Pagan concordance index and test
- [D] Concordance = share of periods both series are in the same phase; Harding–Pagan (2006) test it by regressing one state indicator on the other with HAC/GMM inference because states are serially correlated ([J. Econometrics 132(1)](https://www.researchgate.net/publication/222331123_Synchronization_of_Cycles); exposition and the "inflated when series spend most time in one phase" critique in [Bordon, Reade, Volz](https://www2.gwu.edu/~forcpgm/OxMetrics2014_files/BordonReadeVolz-OxM14-IngoBordon-newmeasure15112013.pdf)). Phase dating via Bry–Boschan / BBQ ([Harding & Pagan 2002](https://econpapers.repec.org/RePEc:eee:moneco:v:49:y:2002:i:2:p:365-381)).
- Fit [I]: under independence E[C] = pq + (1−p)(1−q). With his easing share p ≈ 0.93 and an engine easing share q ≈ 0.90, chance concordance ≈ 0.85. Raw concordance is uninformative here; only the HAC-tested correlation is, and HAC with ~3–6 spells is unreliable. Useful as a reported path statistic next to its chance level, not as a gate.

### 2.3 Cohen's κ, balanced accuracy, MCC vs majority-class baselines
- [D] κ corrects agreement for chance ([Cohen 1960](https://www.agreestat.com/book4/9780970806284_chap2.pdf)); under skewed marginals high agreement coexists with low κ ([Feinstein & Cicchetti 1990](https://www.sciencedirect.com/science/article/abs/pii/089543569090158L)). Balanced accuracy averages per-class recall so majority voting scores 0.5 ([guide citing Brodersen 2010](https://blog.trainindata.com/a-data-scientists-guide-to-balanced-accuracy/); [NeuroImage 2023 on imbalanced decoding](https://www.sciencedirect.com/science/article/pii/S1053811923004044)). MCC argued more informative than κ and Brier on imbalanced binary problems ([Chicco, Jurman, Warrens 2021](https://doaj.org/article/91ef0226db1248cf90447c75247d23bc)). Gwet's AC1 is designed to be stable under extreme prevalence ([agreestat paper](https://agreestat.com/assets/paper-assessing-agreement-nominal-judgement.pdf)).
- Fit [I]: these remove the degenerate baseline (always-easing: κ = 0, BA = 0.5). They do not fix the sample: tightening recall rests on 2 cases from 1 episode, so one episode moves BA by 0.5. AC1 is not suitable for "beat the majority" because it is lenient toward prevalence-driven agreement. Report κ, BA, MCC; do not gate on them alone.

### 2.4 Brier / ranked probability / log scores with probabilistic regime outputs
- [D] Strictly proper scoring rules reward correct probabilities ([Gneiting & Raftery 2007](https://ideas.repec.org/a/bes/jnlasa/v102y2007p359-378.html)). Skill score = 1 − S/S_ref with reference climatology or persistence; climatology is the standard reference for the Brier skill score ([Mason 2004, MWR](https://journals.ametsoc.org/view/journals/mwre/132/7/1520-0493_2004_132_1891_oucaar_2.0.co_2.xml); [CAWCR verification FAQ](https://www.cawcr.gov.au/projects/verification/verif_web_page.html)). Applied to recession probabilities with Brier, log score and ROC ([Lahiri & Wang 2013 listing](https://sites.google.com/view/klahiri/published-papers)); Brier-skill variance under serial correlation ([Lahiri & Yang, CESifo WP 5290](https://www.ifo.de/DocDL/cesifo1_wp5290.pdf)).
- Fit [I]: the one family that uses every regime case and is not gamed by the base rate. A climatology forecast of P(easing) ≈ 0.9 already beats a constant "easing with certainty" on the log score and ties it closely on Brier; an engine beats climatology only by being confidently right in easing episodes **and** shifting probability in the tightening episode. Requires the engine to emit probabilities (not implemented, `spec\scoring.md` §8). RPS (ordinal Brier over easing < neutral < tightening) is finite for deterministic nulls; the log score needs ε-smoothing of deterministic nulls (pre-registered ε). Inference by episode (2.11) handles autocorrelation.

### 2.5 ROC / AUC (Berge–Jordà)
- [D] ROC/AUC evaluates classification of activity into recessions and expansions independently of the threshold and of the base rate; AUC 0.5 = uninformative ([Berge & Jordà 2011, AEJ Macro, summarised in PMC9638394](https://pmc.ncbi.nlm.nih.gov/articles/PMC9638394/)); serially dependent confidence bands exist ([IIF 2013 slides](https://forecasters.org/wp-content/uploads/gravity_forms/7-2a51b93047891f1ec3608bdbd77ca58d/2013/07/Confidence-Bands-for-ROC-Curves-with-Serially-Dependent-Data.pdf)).
- Fit [I]: needs a continuous engine score (P(tightening) or a liquidity index). With 2 minority cases, AUC takes few distinct values (25 × 2 = 50 pairs). Report alongside 2.4.

### 2.6 Windowed daily regime-path agreement around statements (bracketing, block/episode bootstrap)
- [D] Block bootstrap for stationary dependent data ([Künsch 1989](https://projecteuclid.org/journals/annals-of-statistics/volume-17/issue-3/The-Jackknife-and-the-Bootstrap-for-General-Stationary-Observations/10.1214/aos/1176347265.full)); with few clusters, pairs cluster bootstrap over-rejects and the wild cluster bootstrap is preferred ([Cameron, Gelbach, Miller 2008](https://www.researchgate.net/publication/24096179_Bootstrap-Based_Improvments_for_Inference_With_Clustered_Errors); few-large-clusters theory in [Canay, Santos, Shaikh](https://home.uchicago.edu/amshaikh/webfiles/wild.pdf)).
- Fit [I]: label a trading day only when bracketed by two consecutive statements ≤ 12 months apart that agree. Research yields **1,169 bracketed trading days, 1,091 easing / 78 tightening, in 6 spells** [D, computed]. Days are many; independent units are ~6 spells / ~5 episodes. Resampling must be by episode; with Rademacher weights G episodes give only 2^G distinct draws (G = 8 → 256). Good diagnostic of path stability and flicker; weak as a test.

### 2.7 Lead–lag and turning-point dating (LEI, NBER matching, Bry–Boschan)
- [D] Bry–Boschan (1971) algorithmic turning-point selection with minimum phase and cycle lengths ([NBER chapter](https://www.nber.org/system/files/chapters/c2148/c2148.pdf)); leading-index evaluation counts leads at peaks and troughs, extra turns (false signals) and missed turns ([Conference Board BCI Handbook](https://www.conference-board.org/pdf_free/economics/bci/BCI-Handbook.pdf); [Levanon et al. 2015, IJF](https://ideas.repec.org/a/eee/intfor/v31y2015i2p426-445.html)); real-time dating is judged on speed and false positives on vintage data ([Chauvet & Piger 2008, JBES](https://jeremypiger.com/assets/files/Chauvet_Piger_2008_JBES.pdf); [Hamilton 2011, IJF](https://ideas.repec.org/a/eee/intfor/v27y2011i4p1006-1026.html)).
- Fit [I]: the right shape for "did the engine turn before he did, without false alarms" (the original Gate 1 intent). His transitions are interval-censored (change occurred between the last old-view and first new-view statement; research intervals ~30 and ~19 months). Count: 2 research transitions, holdout unknown. Report per transition: engine turn date (after a pre-registered minimum-spell censor, e.g. 3 months, Bry–Boschan style), position relative to the interval (before / inside / after), extra turns per year. Descriptive; no power.

### 2.8 Event-study alignment
- [I] Average the engine's P(target regime) on a grid of trading days −250…+60 around each dated statement where his view changed (or each Gate 1 case). With 2–8 events it is a plot, not a test. Low effort once 2.4 outputs exist.

### 2.9 Bayesian evidence with few cases
- [D] Bayes-factor scale: BF 1–3 "barely worth mentioning", 3–20 "positive", 20–150 "strong" ([Kass & Raftery 1995 scale summary](https://www.statlect.com/fundamentals-of-statistics/Jeffreys-scale); [pcal reference](https://ptfonseca.github.io/pcal/reference/bfactor_interpret.html)).
- Fit [I]: on paired win/loss with θ = P(engine beats comparator), uniform prior vs θ = 0.5: 4/4 wins → BF = (1/5)/(1/16) = 3.2 (positive, barely); 6/6 → BF = (1/7)/(1/64) = 9.1; posterior P(θ > 0.5 | 4/4) = 0.97. States the evidence directly instead of a binary p-gate; does not create information. Suitable as the reported form of any small-n comparison.

### 2.10 Leave-one-episode-out
- [D] Already the PLAN E.6 rule for interpreted-parameter selection; finding 10 sets episodes as the effective unit.
- Fit [I]: turns the 8 research episodes into 8 out-of-fold predictions, which is what makes a research-split gate meaningful during iteration. Climatology references must also be computed leave-one-episode-out (else the reference sees the scored episode's targets). Repeated research use is still multiple testing: keep `trials.jsonl` counts and Holm adjustment.

### 2.11 Continuous labels: his view persists until changed (LOCF)
- [D] Last-observation-carried-forward imputation is biased and over-precise; for binary outcomes it inflates Type I error ([Mavridis et al. 2019, Stat Med](https://onlinelibrary.wiley.com/doi/full/10.1002/sim.8009); [Cochrane Handbook 8.13.2.3](https://handbook-5-1.cochrane.org/chapter_8/8_13_2_3_attempts_to_address_missing_data_in_reports_imputation.htm)). PLAN_REVIEW §B: statements often describe positions already held, so the true change precedes the statement.
- Biases [I]:

| Bias | Direction | Effect on regime evaluation |
|---|---|---|
| Statement lag (view changed before he said it) | LOCF extends the old regime past the true change | Penalises an engine that turns early — the behaviour the original Gate 1 meant to reward |
| Interval censoring | Change date unknown inside a 19–30-month gap | Any day-level score in the gap is label noise |
| Pseudo-replication | ~5,700 era-A days, ~3 research spells | Naive day-level tests overstate significance by orders of magnitude |
| Selection of statement dates | Televised, event-clustered (finding 5, review §B) | Labels dense near events, sparse in quiet easing years |
| Holdout bleed | LOCF from a research statement across a sealed episode (2009–10, 2018, 2020–21, 2023) labels holdout-era days with research views | Contradicts sealed targets; must mask holdout-episode date ranges in research |

- Mitigation [I]: bracketed labels only (2.6); transition gaps left unlabeled and evaluated by 2.7.

### 2.12 Pooling research + holdout for one final test
- [I] Raises Gate 1 cases to 6–8 (4–6 episodes) and regime cases to the full era-A set (14 episodes). Research cases are contaminated by iteration, so the pooled estimate is optimistic; the holdout-only estimate is unbiased but tiny (4 cases / 3 episodes for timing; 5 era-A episodes overall). Acceptable only as a secondary, pre-registered report with the in-sample share stated.

### 2.13 Regime as a non-gating diagnostic; Gate 2 as go/no-go
- [I] Gate 2 has 43 era-A cases / 14 episodes and a non-degenerate comparator (`null_trend_12m`, 0.461), so it carries the statistical decision. A regime stage that is wrong propagates into thesis recall (transition→thesis table reads regime), so Gate 2 already tests the regime foundation indirectly. Cost: a failed Gate 2 is less diagnostic about which stage failed; mitigated by the regime diagnostics reported at E3.

## 3. Comparator choice

| Point | Content | Tag |
|---|---|---|
| Why always-easing is degenerate | It encodes the marginal distribution of the labels and no information about time. Accuracy, agreement and the §6b lead all reward it for prevalence: κ = 0, BA = 0.5 (table §0), yet accuracy 0.926 and maximal lead on every easing case | [D] computed; [I] |
| What the literature uses | Skill relative to a reference forecast: climatology (base-rate probabilities issued every time) and persistence; skill 0 = no improvement over the reference | [D] [Mason 2004](https://journals.ametsoc.org/view/journals/mwre/132/7/1520-0493_2004_132_1891_oucaar_2.0.co_2.xml); [AMS glossary "skill"](https://glossary.ametsoc.org/wiki/skill/); [CAWCR](https://www.cawcr.gov.au/projects/verification/) |
| Chance-corrected classification | κ, BA, MCC put the majority classifier at 0 / 0.5 / 0; under prevalence, κ is low even when agreement is high (paradox), so κ must be read with per-class agreement | [D] [Feinstein & Cicchetti 1990](https://www.sciencedirect.com/science/article/abs/pii/089543569090158L); [Chicco et al. 2021](https://doaj.org/article/91ef0226db1248cf90447c75247d23bc) |
| Recommended reference set | (1) Climatology, leave-one-episode-out class frequencies of his reads — the probabilistic form of always-easing, non-degenerate under a proper score; (2) `null_trend_12m` — best non-constant null (κ 0.21, BA 0.82); (3) persistence of his last read, reported only (the current `null_persistence` 120-day embargo produces 11 None of 27, so it is weak by construction) | [I] |
| Timing comparator | If a timing metric is kept, use the best **non-constant** null (`null_trend_12m`); a constant cannot flip, so lead comparisons against it are determined by target mix (already flagged in `spec\scoring.md` §7) | [D] §7; [I] |

## 4. Options table

Power column: estimate on current counts (research era-A regime: 27 cases / 8 episodes; holdout era-A: ~5 episodes; Gate 1 TP: 2 research + 4 holdout). [I] unless noted.

| # | Option | What it measures | Power with our counts | Bias / leakage risks | Effort | Recommendation |
|---|---|---|---|---|---|---|
| 1 | Current §6b timing gate vs always-easing | Lead of flip to target vs a constant | None on research (headroom 0); holdout pass needs all 4 non-easing and won (p floor 0.0625; perfect-engine pass probability q^4) | Comparator degenerate; outcome set by holdout mix; 3 episodes → episode-level floor 0.125 | Exists | Retire as gate |
| 2 | Agreement margin vs best null (+15 pts) / paired agreement | Accuracy at asof/window | Unreachable vs always-easing (max +7.4 pts; p ≥ 0.25) | Base rate | Exists | Retire |
| 3 | Pesaran–Timmermann (1992 / 2009) | Dependence of predicted and actual direction | Not valid at 2/27 minority; 2009 form on daily path has ~3 spells | Asymptotics fail; oversized | Low | Do not use |
| 4 | Harding–Pagan concordance + HAC test | Share of time in same phase; correlation of states | Chance concordance ≈ 0.85; HAC with ~6 spells unreliable | Inflated by prevalence | Low | Report with chance level, no gate |
| 5 | κ / BA / MCC at asof | Chance-corrected classification | Minority = 2 cases / 1 episode; one episode moves BA by 0.5 | Unstable; κ paradox | Low | Report; no standalone gate |
| 6 | Proper scores (RPS, log, Brier) with skill vs LOEO climatology and `null_trend_12m`; episode-level paired sign-flip | Probability quality: calibration + discrimination over all regime cases | Research: 8 episodes, exact floor p = 1/256; an engine better in ~7 of 8 episodes with similar magnitudes reaches p ≈ 0.05–0.10. Holdout: ~5 episodes, floor 1/32; needs 5/5 or 4/5 with a small loss | Climatology must be LOEO; ε for log score pre-registered; research reuse counted as trials | Medium (engine probabilities, RPS scorer, LOEO climatology; sign-flip code exists) | **Primary (Option B)** |
| 7 | ROC / AUC on P(tightening) | Ranking ability independent of base rate | 50 minority–majority pairs; coarse | Same minority concentration | Low after #6 | Report with #6 |
| 8 | Bracketed daily path agreement + episode wild bootstrap | Day-level agreement where his view is known | 1,169 days but ~6 spells / ~5 episodes; 2^8 distinct Rademacher draws | Pseudo-replication if done by day; holdout-date masking required | Low–medium | **Diagnostic (with #9)** |
| 9 | Turning-point matching (Bry–Boschan censor, LEI-style lead / extra / missed turns) against interval-censored transitions | Whether and when the engine turns relative to his transition intervals; false-alarm rate | 2 research transitions; descriptive only | Statement lag biases "early" turns toward false alarm unless intervals are used | Medium | **Diagnostic (with #8)** |
| 10 | Event-study plot of P(target) around his changes | Shape of the engine's probability path into his changes | 2–8 events; descriptive | Overlapping windows within episodes | Low after #6 | Report |
| 11 | Bayesian win-rate / Bayes factor | Strength of evidence on small paired samples | 4/4 → BF 3.2; 6/6 → BF 9.1 | Prior choice (pre-register uniform) | Low | Reported form for any small-n comparison |
| 12 | LOEO out-of-fold predictions | Makes research-split evaluation out-of-sample per episode | Uses all 8 research episodes | Multiple trials across iterations | Medium (E.6 already plans it) | Required by #6 |
| 13 | LOCF continuous labels | Day-level agreement under persistence assumption | Nominal ~5,700 days; effective ~3 research spells | Statement lag, censoring, pseudo-replication, holdout bleed | Low | Reject in raw form; use #8 instead |
| 14 | Pool research + holdout for a final single test | Larger final n | Gate 1 TP 6–8; era-A regime 14 episodes | Optimistic (research in-sample) | Low | Secondary report only |
| 15 | Regime non-gating; Gate 2 sole go/no-go | Defers statistical decision to thesis recall (43 cases / 14 episodes) | Gate 2 power as already specified | Less stage-specific failure attribution | Lowest | **Option A** (fallback / minimal) |

## 5. Recommendation

Choice for the owner:

| Option | Gate 1 becomes | Diagnostic | Engine must output |
|---|---|---|---|
| **A** — Non-gating regime | No regime gate. E3 → E4 proceeds on a written regime report; Gate 2 is the single go/no-go | #8 + #9 + κ/BA/MCC (#5) | Daily US `policy_direction` (exists) |
| **B** — Probabilistic skill gate (recommended) | Staging gate on research, out-of-fold (LOEO): episode-first mean RPS skill > 0 vs LOEO climatology **and** vs `null_trend_12m`, one-sided exact episode sign-flip on per-episode RPS differentials, p < 0.10 vs `null_trend_12m`. At E7: same statistic on the holdout reported once (with Bayes factor), not re-gated; Gate 2 remains the hard go/no-go | #8 + #9 (bracketed path agreement; transition matching with lead / extra / missed turns) | Daily as-of P(easing), P(neutral), P(tightening) at 16:00 ET, summing to 1, floored at a pre-registered ε (e.g. 0.01); argmax = `policy_direction` |
| **C** — Chance-corrected classification gate | Research LOEO: κ > κ(`null_trend_12m`) and BA ≥ BA(`null_trend_12m`) | #8 + #9 | Daily `policy_direction` (exists) |
| **D** — Timing gate repaired | §6b retained but comparator = `null_trend_12m`, turning points restricted to rule (a) regime changes, transitions interval-censored, research + holdout pooled at E7 | #6 skill scores reported | Daily `policy_direction`; P(·) optional |

Recommended: **B as the primary design, with #8 + #9 as the diagnostic.** Reasons [I]: it is the only option that (i) is not beaten or gamed by the 92.6% base rate, (ii) uses all 27 research regime cases instead of 2, (iii) has a non-trivial attainable p on research (8 episodes, floor 1/256) so it can actually stage E3 → E4 without opening the holdout, (iv) matches the literature's reference-forecast convention (skill vs climatology and a non-constant baseline), and (v) fills the log-score/probability gap already listed in `spec\scoring.md` §8. Choose **A** if the engine will not emit calibrated probabilities in v1; it is defensible because Gate 2 already tests regime indirectly with 14 episodes. **C** is not recommended as a gate (minority class = one episode). **D** is not recommended as a gate (n ≤ 8 cases, ≤ 6 episodes after pooling; best case BF ≈ 9) but its transition table belongs in the diagnostic.

Pre-registration items for B [I]: ε floor; ordinal class order for RPS; LOEO climatology definition (class frequencies of research regime targets excluding the scored episode, with add-one smoothing); episode-first aggregation as §5; exact enumeration of 2^E sign patterns; research-only staging use with every run in `trials.jsonl` and Holm adjustment; holdout-episode date ranges masked from any research daily-path label; minimum-spell censor (e.g. 3 months) for turn dating in #9.

## Sources

- Pesaran & Timmermann 1992: https://econpapers.repec.org/RePEc:bes:jnlbes:v:10:y:1992:i:4:p:561-65
- Directional accuracy, small-sample behaviour: https://www.tandfonline.com/doi/full/10.1080/00036846.2024.2393902
- Pesaran & Timmermann 2009: https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.0113
- Blaskowitz & Herwartz 2014: https://ideas.repec.org/a/eee/intfor/v30y2014i1p30-42.html
- Harding & Pagan 2006: https://www.researchgate.net/publication/222331123_Synchronization_of_Cycles
- Harding & Pagan 2002: https://econpapers.repec.org/RePEc:eee:moneco:v:49:y:2002:i:2:p:365-381
- Bordon, Reade, Volz (concordance critique): https://www2.gwu.edu/~forcpgm/OxMetrics2014_files/BordonReadeVolz-OxM14-IngoBordon-newmeasure15112013.pdf
- Bry & Boschan 1971: https://www.nber.org/system/files/chapters/c2148/c2148.pdf
- Conference Board BCI Handbook: https://www.conference-board.org/pdf_free/economics/bci/BCI-Handbook.pdf
- Levanon et al. 2015: https://ideas.repec.org/a/eee/intfor/v31y2015i2p426-445.html
- Chauvet & Piger 2008: https://jeremypiger.com/assets/files/Chauvet_Piger_2008_JBES.pdf
- Hamilton 2011: https://ideas.repec.org/a/eee/intfor/v27y2011i4p1006-1026.html
- Berge & Jordà 2011 (via PMC9638394): https://pmc.ncbi.nlm.nih.gov/articles/PMC9638394/
- ROC with serially dependent data: https://forecasters.org/wp-content/uploads/gravity_forms/7-2a51b93047891f1ec3608bdbd77ca58d/2013/07/Confidence-Bands-for-ROC-Curves-with-Serially-Dependent-Data.pdf
- Gneiting & Raftery 2007: https://ideas.repec.org/a/bes/jnlasa/v102y2007p359-378.html
- Mason 2004, climatology reference in skill scores: https://journals.ametsoc.org/view/journals/mwre/132/7/1520-0493_2004_132_1891_oucaar_2.0.co_2.xml
- CAWCR forecast verification FAQ: https://www.cawcr.gov.au/projects/verification/verif_web_page.html
- AMS glossary, skill: https://glossary.ametsoc.org/wiki/skill/
- Lahiri publications (Lahiri & Wang 2013): https://sites.google.com/view/klahiri/published-papers
- Lahiri & Yang, Brier score variance under serial correlation: https://www.ifo.de/DocDL/cesifo1_wp5290.pdf
- Cohen 1960 (via Gwet chapter): https://www.agreestat.com/book4/9780970806284_chap2.pdf
- Feinstein & Cicchetti 1990: https://www.sciencedirect.com/science/article/abs/pii/089543569090158L
- Gwet AC1: https://agreestat.com/assets/paper-assessing-agreement-nominal-judgement.pdf
- Balanced accuracy (Brodersen 2010 summary): https://blog.trainindata.com/a-data-scientists-guide-to-balanced-accuracy/
- Imbalanced decoding metrics, NeuroImage 2023: https://www.sciencedirect.com/science/article/pii/S1053811923004044
- Chicco, Jurman, Warrens 2021: https://doaj.org/article/91ef0226db1248cf90447c75247d23bc
- Künsch 1989: https://projecteuclid.org/journals/annals-of-statistics/volume-17/issue-3/The-Jackknife-and-the-Bootstrap-for-General-Stationary-Observations/10.1214/aos/1176347265.full
- Cameron, Gelbach, Miller 2008: https://www.researchgate.net/publication/24096179_Bootstrap-Based_Improvments_for_Inference_With_Clustered_Errors
- Canay, Santos, Shaikh (wild bootstrap, few clusters): https://home.uchicago.edu/amshaikh/webfiles/wild.pdf
- Kass & Raftery 1995 scale: https://www.statlect.com/fundamentals-of-statistics/Jeffreys-scale ; https://ptfonseca.github.io/pcal/reference/bfactor_interpret.html
- LOCF bias: https://onlinelibrary.wiley.com/doi/full/10.1002/sim.8009 ; https://handbook-5-1.cochrane.org/chapter_8/8_13_2_3_attempts_to_address_missing_data_in_reports_imputation.htm

Source-access note: the Conference Board handbook PDF and the Harding–Pagan 2006 full text were not machine-readable through the fetch tool; their content above is as summarised by search results and secondary papers, not verified against the primary text.
