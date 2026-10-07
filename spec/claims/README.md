# Testable claims catalogue

Date: 2026-10-07. Files: `claims.yaml` (76 claims, C-01..C-76), `process_timeline.yaml` (R-01..R-65 dated by era), this README.

Purpose: formalize every general statement by S. Druckenmiller about how markets and economies behave as a falsifiable historical hypothesis, dated by when he held it, so that (a) each claim can be tested on free data with an out-of-sample split after its first public statement, and (b) the engine can apply "the process as of date t" when replayed backwards. One-off market calls are excluded unless they embed a general rule. Process norms about his own behaviour are recorded and marked untestable.

## Method

1. Sources read: `spec\process.md` (rules and citations), every note in `library\discovered_sources\` and `library\reference_sources\`, the Lost Tree OCR transcript and Delivering Alpha 2014 transcript text that those notes cite, `library\research\data_practices.md`, and `spec\data_catalogue.yaml` (version 2026-10-07.1). Not read, by instruction: `cases\`, `spec\scoring.md`, `spec\HOLDOUT.md`, `results\`. No claim or threshold was chosen with reference to fidelity cases or scores.
2. Inclusion: a statement qualifies if it asserts a regularity ("never", "always", "every time", "tends to", "historically", "golden rule") or a mechanism that implies one. 20 regularities named in the task brief were confirmed in the library and included; the other 56 came from reading the notes. Policy opinions (tariffs above 10% harmful, entitlement reform), single forecasts (2023 recession, Dow flat for ten years) and biographical figures (sterling sizes) were excluded, except where a forecast carries a general rule (for example, the flat-decade forecast as a valuation rule, C-61).
3. Formalization: each claim lists variables with catalogue series ids, definitions, and thresholds. His own numbers are tagged `stated` and fixed. Where he gave no number, a pre-registered default and a sensitivity range are tagged `interpreted`. Each test gives the event definition, sample, frequency, outcome measure, and pass/fail criteria: a counterexample count for "never" claims, conditional vs unconditional returns for "tends to" claims, and hit rate vs base rate for signal claims.
4. Out of sample: the split date is `first_public_statement.date`. Retrospective claims ("I've always…") have an in-sample period covering all history before that date. Many claims were first stated in 2022–2026, so their out-of-sample windows are four years or shorter. Treat those results as anecdotal.
5. Timeline: `held_from` is the earliest dated evidence that he held or used the belief. Retrospective accounts (for example, "my first mentor taught me…" or "in mid-1981 rates had soared to 19 percent") are dated to the event they describe. Basis `stated` means he gives the date; basis `inferred` means the date was deduced from an action or from context. `changes` records dated revisions, and `held_until` records abandonment. `dating: thin` marks beliefs whose start date rests on weak evidence (38 of 76 claims; 29 of 61 rules that are his).
6. Data: series ids follow `spec\data_catalogue.yaml`. `NEW` marks a free series not yet in the catalogue (a loader is needed), and `MISSING` marks a series with no known free source. Two run modes are pre-registered for point-in-time handling. The primary mode conditions on vintage or first-release inputs. The sensitivity mode uses latest revisions. Outcome labels (NBER dates, realized returns) may use revised data.
7. Reliability: of the best quote per claim, 58 come from near-primary transcripts (NP), 6 from primary text (P) and 12 from secondary summaries (S). Quotes marked "note summary wording" are the note's paraphrase, not verbatim.

## Counts

By testability:

| Testability | Count |
|---|---|
| testable (free data in catalogue, or a free NEW loader) | 51 |
| partially_testable (proxy-only, manual event list, or definitional ambiguity) | 17 |
| untestable_free_data | 8 |
| Total | 76 |

By topic:

| Topic | Testable | Partial | Untestable | Total |
|---|---|---|---|---|
| liquidity_policy | 8 | 1 | 0 | 9 |
| bubbles_fragility | 5 | 3 | 1 | 9 |
| internals_breadth | 6 | 1 | 0 | 7 |
| cross_asset | 6 | 1 | 0 | 7 |
| fx | 3 | 3 | 0 | 6 |
| technicals_timing | 3 | 3 | 0 | 6 |
| process_self | 0 | 0 | 6 | 6 |
| inflation | 4 | 1 | 0 | 5 |
| rates_bonds | 5 | 0 | 0 | 5 |
| policy_error | 2 | 1 | 1 | 4 |
| cycle_fundamentals | 2 | 2 | 0 | 4 |
| valuation | 3 | 0 | 0 | 3 |
| political | 1 | 1 | 0 | 2 |
| fiscal_record | 2 | 0 | 0 | 2 |
| positioning | 1 | 0 | 0 | 1 |

Why the 8 claims are untestable with free data:

| Claim | Reason |
|---|---|
| C-69 hot/cold | Needs his fund's P&L |
| C-70 sizing 70–80% | Needs position-level history |
| C-71 concentration | Needs conviction-weighted holdings |
| C-72 no stops | Thesis exits are discretionary |
| C-73 fat pitches per year | "Truly exciting" is his own label |
| C-74 bear-market profits | No public fund returns by asset class |
| C-75 split pops | No pre-2021 split-event file |
| C-76 bear ends when the problem is attacked | No operational definition |

## Top 15 claims by importance to the process

Ranked with liquidity, policy and inflation first.

| Rank | Id | Claim | Rules | First public | Testability |
|---|---|---|---|---|---|
| 1 | C-01 | Liquidity and the Fed, not earnings, move the overall market | R-01, R-13 | 1991-12 | testable |
| 2 | C-04 | Stay long until the Fed tightens; tightening onset ends liquidity rallies (rate-level and post-bubble variants) | R-14, R-06 | 1991-12 | testable |
| 3 | C-03 | Liquidity overrides a bearish economic view | R-01, R-02, R-04, R-14, R-60 | 2009-Q4 | testable |
| 4 | C-02 | M2 growing much faster than industrial production lifts stocks | R-02 | 2009-Q4 | testable |
| 5 | C-10 | Bear markets (and his big money) come from central-bank mistakes | R-05, R-06 | 2014-07-16 | partial |
| 6 | C-11 | Persistently too-loose policy (Taylor gap) ends in a bust 1.5–3 years later | R-06, R-11, R-48 | 2005-05 | testable |
| 7 | C-07 | Rate of change of global central-bank balance sheets drives risk assets | R-03, R-12, R-14 | 2018-09-06 | testable |
| 8 | C-08 | Net liquidity (Fed purchases minus Treasury issuance) governs equity risk/reward | R-03, R-04 | 2020-05-12 | testable |
| 9 | C-05 | QE inflates financial asset prices | R-12, R-14, R-24 | 2012-04 | testable |
| 10 | C-06 | Setbacks follow within ~6 months of QE ending | R-14 | 2012-04 | partial |
| 11 | C-15 | Inflation above 5% has not fallen without fed funds above CPI | R-08 | 2022-06-10 | testable |
| 12 | C-16 | Inflation above 5% never tamed without recession | R-09 | 2022-06-10 | testable |
| 13 | C-14 | No soft landing after inflation above 4.5% | R-07 | 2022-06-10 | testable |
| 14 | C-12 | Financial conditions gauge restrictiveness better than real-rate theory | R-58, R-06 | 2019-06-03 | testable |
| 15 | C-40 | Rates, oil and the dollar rising together precede falling earnings and stocks | R-10 | 2009-Q4 | testable |

Next in order: C-27 (stocks lead fundamentals by 6–12m), C-31 (breadth thrust), C-32 (leadership narrowing), C-35 (10y vs nominal GDP), C-36 (deficits and long yields), C-53 (technicals decay), C-47 (currency trends of at least 2 years), C-21 (post-bubble bears last more than 6 months).

Known out-of-sample evidence, recorded in the claims' caveats and taken from the notes rather than from tests:

| Claim | Evidence |
|---|---|
| C-08 | Failed in its first month (2020-05 → 2020-06) |
| C-14, C-16 | The 2022–24 disinflation had no NBER-dated recession as of 2026-09. Unless a recession is later dated inside the window, this is a counterexample to both |
| C-15 | He predicted the break himself |
| C-37 | The 2022 inversion was followed by no recession |

## Timeline view: process as of date t

Era weights for rules and the claims linked to them. Codes: C = core; A = active; R = reduced; M = minor or display; – = absent (for R-63, absent by his own stated rule); ? = no evidence (the belief may have been held but cannot be dated). Weights before a rule's first public statement are inferred from retrospective accounts. Per-rule evidence is in `process_timeline.yaml`.

| Rule (claims) | 1977–1987 | 1988–2000 Soros/Duquesne | 2001–2010 | 2011–2019 family office | 2020–2026 |
|---|---|---|---|---|---|
| R-01 liquidity not earnings (C-01, C-03) | C | C | C | C | C (+ company mosaics from 2024) |
| R-02 M2 − IP (C-02) | ? | ? | C (2008→) | R | R |
| R-03/R-04 net liquidity (C-07, C-08) | – | – | – | – | A (2020→; reduced after 2020-06) |
| R-05 policy error (C-10) | C (1981→) | C | C | C | C |
| R-06 Taylor gap (C-11) | ? | ? | C (2003→) | C | R (2024: markets over theory) |
| R-07/08/09 inflation rules (C-14..C-16) | ? | ? | ? | ? | C (2022→; R-08 as a veto flag only) |
| R-10 rates + oil + USD (C-40) | ? | A (2000) | C | C | C |
| R-11 fragility alerts (C-19..C-24) | ? (1988 LBO, thin) | M | A (2004→) | A | A |
| R-12/R-24 cross-region (C-09, C-48, C-49) | ? | C (1989→) | A | C | C |
| R-13 valuation as context (C-60, C-61) | context | context | context | context + secular view (2016→) | context + secular view |
| R-14 stay long until tightening; QE end; balance-sheet rate of change (C-04..C-07) | C (1981→) | C | C | C | C |
| R-15/R-16 internals, leading industries (C-27, C-29) | A | A | A | C (RS doubts 2018) | C |
| R-17 bond/credit signal (C-37, C-38) | ? | C (1989→) | A (suppressed from 2009) | R | R (curve "over-rated" 2026) |
| R-18/R-29 charts, momentum, chart veto (C-30, C-53, C-54) | A (Drelles) | C | C | C | C veto / R timing |
| R-20 horizon (C-28) | 18m | 18m | 18m | 6–18m | 12m–3y (lengthening) |
| R-21 change not level (C-62) | C | C | C | C | C |
| R-22/R-50 premise exits (C-72) | C (1987-10) | C | C | C | C |
| R-26 multi-asset menu (C-41) | A (from ~1983) | C | C | C | C |
| R-28/R-57 asymmetry sizing | ? | C (1992→) | C | C | C |
| R-30/R-51 price vs news (C-55) | C (from ~1983) | C | C | R (2018→) | R (~20%) |
| R-31 no contrarian fade (C-56) | ? | C (1988→) | C | C | C (crowding affects entry only) |
| R-32 technicals decay (C-53) | – | – | – | A (2018→) | C (2026: ~20%) |
| R-38 invest then investigate (C-57) | ? | C (1992→) | C | C | C |
| R-41..R-45 caps and leverage | A | A | A | ? | ? (FX "smaller size", 2026) |
| R-46/R-47 hot/cold, house money (C-69) | C | C | C | C, lower base aggression | C, lower base aggression |
| R-49 no stops (C-72) | C | C | C | C | C |
| R-54/R-55 no pitch no play, no long bias (C-73) | C (1981→) | C | C | C | C |
| R-56 10y vs nominal GDP (C-35) | ? | ? | ? | ? | A (2023→; "always", undated) |
| R-58 financial conditions (C-12, C-13) | ? | ? | ? | A (2019) | C (2024) |
| R-59 leadership narrowing (C-32) | ? | A (2000, thin) | ? | ? | A (2024) |
| R-60 breadth thrust (C-31) | ? | ? | ? | A (2015) | C (2020) |
| R-61 post-bubble bear > 6m (C-21) | ? | ? | ? | ? | A (2022) |
| R-62 sidestep, short rallies (C-42, C-43) | ? (net short 1987–88) | ? (1999 internet short) | ? | A (2015) | C |
| R-63 fiscal supply (C-36) | – (stated rule) | – (1991 exception) | – | – | A (2023→) |
| R-64 political cycle (C-66) | ? | ? | ? | ? | M |
| R-65 currency trends ≥ 2y (C-47) | A | C | C | C | C |
| R-34..R-37 article gates | n/a | n/a | n/a | n/a | n/a |

Documented revisions that change replay behaviour:

| Date | Revision | Source |
|---|---|---|
| 2003-12 → 2005 | Policy error assessed from data alone, then a formal Taylor rule | Lost Tree 2015; Sohn 2016 |
| 2014-07-16 vs 2021-05-11 | Rate level matters more than the first hike, vs "the minute they start tightening" after a bubble | DA 2014; Hustle 2021 |
| 2016-05-04 | Valuation enters as a secular (multi-year) input; still never a timing input | Sohn 2016 |
| 2018-09-06 → 2026-01-30 | Price vs news and relative strength cancelled by algos, then technicals "about 20% as effective" | Real Vision 2018; Sohn 2022; NBIM 2023; MS 2026 |
| 2020-06-08 | Net-liquidity read overridden by Fed scale and a breadth thrust | CNBC 2020 |
| 2022-06-10 | FF > CPI rule stated together with his expectation that it would break | Sohn 2022 |
| 2023-10-24 | Lifelong rule against trading on deficits abandoned. Counter-evidence: a 1991 warning on long bonds cited deficits | Robin Hood 2023; NMW |
| 2024-10-16 | Markets preferred over real-rate theory for judging restrictiveness | Bloomberg 2024 |
| 2015 → 2024 → 2026 | Horizon moves from 18m (Lost Tree) through 6–12m (2015) and 12–18m (2022) to 18–24m (2024) and 18m–3y (2026) | as listed |
| 2026-01-30 | Gold rationale moves from monetary to geopolitical | MS 2026 |

Evidence too thin to date the belief: R-02 before 2008; R-07, R-08 and R-09 before 2022 (the "never" wording implies an older historical reading but is undated); R-56 ("always", undated); R-41..R-45 after 2010; R-59 before 2024; R-60 before 2015; R-61 before 2022; R-62 in 1977–2000, where his behaviour (net short in 1987–88, the 1999 internet short) contradicts a sidestep rule; R-63, where the 1991 counter-evidence conflicts with the stated lifelong rule. For replay, unknown-era cells should be scored both ways (rule on and rule off) rather than assumed.

## Data gaps that block or weaken tests

| Gap | Affects |
|---|---|
| FRENCH49 missing; only the French 12 substitute (homebuilding, trucking, retail and steel not separable; breadth across 12 industries is coarse) | C-29, C-32, C-31 fallback segment |
| Shiller earnings, CPI and CAPE fields not loaded (only SHILLER_SP price) | C-01, C-18, C-27, C-28, C-30, C-40, C-60, C-61 |
| NEW free series: CP (corporate profits), AHETPI, PAYEMS, UMCSENT, ACM term premium (NY Fed), deficit/GDP (FYFSGDA188S, catalogue status missing), JST Macrohistory, BIS credit gap, OECD foreign share prices, G.17 chemical capacity, NIPA information-processing investment | C-17, C-20, C-33, C-36, C-50, C-63, C-64, C-65, C-67, C-68, C-09, C-26 |
| MISSING: B-rated issuance share, covenant-lite share, consensus macro and earnings surprises, business bankruptcy series (free status unverified), pre-2021 split events, fund P&L | C-23, C-24, C-25, C-55, C-75, C-69..C-74 |
| Pre-1954 policy rate | C-14, C-15 long sample |
| SP500 daily missing | French market return used as the equity proxy throughout |
| FOMC calendar missing | Onset and QE-end dating uses rate series and manual event lists |
| ICE BofA OAS retained on FRED for only 3 years from 2026-04 | C-23; capture is required |
