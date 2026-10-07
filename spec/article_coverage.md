# Article coverage audit: Automated Alpha fat-pitch filter vs fat-pitch spec

Date: 2026-10-07. Status: audit + implementation proposal; no spec file changed. Inputs read: article PDF (all 29 pages, small-text screenshots re-rendered at 220–300 dpi), `library\source_article\comparison_to_reference.md`, reference doc §1, `spec\process.md`, `spec\registry.yaml`, `spec\transition_table.yaml`, `spec\data_coverage.md`, amber lake directory listing (`<AMBER_DATA>\lake`). `spec\claims\` does not exist. Not read (by instruction): `cases\`, `spec\scoring.md`, `spec\HOLDOUT.md`, `results\`.

Owner decision 2026-10-07: "we want all of the ones in that article as well." Every article element below is therefore implemented as an `interpreted-from-article` rule. The original adopt / variant / exclude recommendation is replaced by a track assignment.

## 0. Conventions

| Item | Definition |
|---|---|
| Inventory id | `A-xx`. Proposed article rule id = `RA-xx` (same number, 1:1), tag `interpreted-from-article`. `R-xx` ids are not consumed (process.md: ids never reused; R-01..R-65 taken). |
| Coverage | **a** = covered by a Druckenmiller-sourced rule (R-xx named; difference stated). **b** = present as `interpreted-from-article` at weight 0 (R-34..R-37). **c** = partially covered. **d** = missing. |
| D support | Library note supporting the element (`DS/` discovered_sources, `RS/` reference_sources), or `none`. "Conflict" names the rule it contradicts. |
| Data (amber) | **Y** = input in amber lake with usable history; **P** = partial (short history, proxy, or forward-only); **N** = no free data in amber → rule output `unknown` (never pass, never fail; process.md §0). Equity prices in amber start 2021-09 (Alpaca SIP); article-track single-name backtests are 2021-09→ only. |
| Track | **A** = article track (article-faithful version, weight 1 there). **A+D** = article track, and also a Druckenmiller-track candidate because library support exists (weight 0 in D until registered). **D=R-xx** = Druckenmiller track already covers it with its own rule. **A!** = article track only, because it conflicts with his stated process. |
| Pre-decision rec (summary §9 only) | A+D / D=R-xx ≈ "adopt"; A ≈ "weight-0 article variant"; A! ≈ "exclude". |
| Article numbers | Used as published. Where text, caption and screenshot disagree, the screenshot value is used and the disagreement is listed in §8. |

Undisclosed: Gates 5, 6, 10 criteria, module formulas, regime point maps and the 7 tracked managers sit behind the paywall (p.29). Every such rule below states which part is the article's number and which part is an interpreted construction; interpreted constructions are fixed before scoring and never tuned on cases.

## 1. Universe, pipeline, framing

| id | Article element (p.) | Cat | Cov / spec rule | D support | Data | Track | Implementation (RA rule) | Conflict |
|---|---|---|---|---|---|---|---|---|
| A-01 | Universe 923 = 903 equities (S&P 500 + S&P 400) + 14 commodities + 6 crypto (p.6); screenshot universe 916 (p.7) | UI/data | c: R-26 multi-asset menu (rates/FX first) | RS/2024-11-06 five buckets (supports multi-asset, not this list) | P: S&P 500 PIT via IVV N-PORT 2021-06→; S&P 400 PIT not in amber; commodities via IBKR/Massive; crypto Coinbase | A | Universe = PIT S&P 500 ∪ S&P 400 members (IJH N-PORT loader needed; else current list flagged survivorship-biased) + 14 commodity front futures + 6 crypto; commodity and crypto lists unspecified → choose and freeze | Article omits rates/FX, which R-26 ranks first |
| A-02 | Nightly run after US close; `python -m tools.daily_pipeline`; 68 phases (p.6) | UI | a: PLAN V nightly job | n/a | Y | A | asof = 16:00 ET close; same `evaluate(asof)` entry point | — |
| A-03 | Elimination cascade: fail gate n → never scored at n+1 (p.6) | convergence | d (spec uses evidence families; failed non-veto evidence lowers tier, never removes, R-38) | none | Y | A | Sequential boolean gates G1→G10; output records last gate passed and failing field (as screenshot "Gate 7 (Smart Money): smartmoney=0 < 50 …") | Differs from R-38 tiering (not a stated-process conflict) |
| A-04 | Zero pitches → "wait"; "sits in cash for months" (p.7) | sizing-exit | a: R-54 no pitch no play, R-55 | DS/2023-04-24 (NP) | Y | D=R-54; A | No G10 survivor → Decision "No pitch" | — |
| A-05 | Top-down: read macro → favored/punished sectors → best names, size up (p.14) | regime/rotation | a: steps 1→2→3 | RS/2015-01-18; DS/2016-11-10 (regime shift → long materials, value) | Y | D=steps 1–3; A | Gate order G1→G4→G5–G10 | Article step 3 is single-stock; spec step 3 is multi-asset |
| A-06 | Fat pitch = macro, sector, technical, fundamental, smart money, catalyst aligned at the same time (p.1, p.11) | convergence | c: R-38 fat pitch = starter + ≥ k independent families | DS/2023-04-24 "fat pitch"; R-38 cites | Y | D=R-38; A | Article version = pass all of G1–G10 | Smart money and fundamental quality are not his families |
| A-07 | "Right big", concentration (p.1) | sizing-exit | a: R-40, R-57 | DS/2022-06-XX (NP) | Y | D=R-40 | none needed in A (article gives no sizing rule, see A-131) | — |
| A-08 | 10-item checklist: macro regime, sector rotation, technical trend, fundamental quality, institutional positioning, insider transactions, earnings revision velocity, options flow, accounting forensics, alternative data (p.4–5) | convergence | c: items mapped individually below | per item | per item | A | Covered by gates/modules A-10..A-117 | per item |
| A-09 | Manual-workflow sources: FRED, **Fed minutes**, yield curve; ETF flow data, breadth; charting; EDGAR screener; 13F aggregators; Form 4; options flow tool; FactSet revisions; satellite, shipping, labor (p.5) | data source | c; Fed-minutes item d | none for minutes NLP | P: minutes text not in amber | A | Fed-minutes item: hawkish/dovish NLP score on FOMC minutes (VADER fin dictionary per A-180) → display only (article gives no use) | — |

## 2. The 10 gates and cascade

| id | Article element (p.) | Cat | Cov / spec rule | D support | Data | Track | Implementation (RA rule) | Conflict |
|---|---|---|---|---|---|---|---|---|
| A-10 | G1 Macro regime: 7 indicators → strong_risk_off / risk_off / neutral / risk_on / strong_risk_on; sample 58/100 neutral (p.6, p.24) | regime | c: R-01..R-14, R-58; 5-level label display only in spec | R-01 (Fed drives market) | Y (VIX 1990→, HY OAS 1997→; full gauge 1997-01→) | A | `total = Σ7 components` (A-12..A-18); `score = 50 + total/2` (reproduces +16 → 58); label by A-11 | Point-scored level composite vs his change-based rules (R-21) |
| A-11 | Regime thresholds: ">+30 risk-on" (p.4 panel); neutral = "classifier below threshold" (p.21) | regime | d | none | Y | A | risk_on if total > +30 (article); risk_off if total < −30 (interpreted symmetry); strong_* thresholds undisclosed → interpreted ±60 (= score 80/20), registry `art.regime.strong_total` | — |
| A-12 | Component Fed funds: +4 pts, FF 3.64%, "Cutting = bullish" (p.24) | regime | a: R-14 policy direction | DS/2021-05-11 "minute they start tightening" | Y (DFF) | D=R-14; A | sign of 3-month FF change × `art.regime.ff_pts` (interpreted cap ±10); point map undisclosed | — |
| A-13 | Component M2: +11 pts, +4.29% YoY (p.24) | liquidity | c: R-02 uses M2 minus IP | DS/2009 Feig (M2 vs IP) | Y (M2SL vintaged) | D=R-02; A | M2 YoY mapped linearly, cap ±15 (11 = max observed) | Article uses M2 alone; his rule is M2 relative to IP |
| A-14 | Component real rates: −6 pts, FF 3.64 − CPI 2.66 = +0.98 (p.24) | regime | c: R-06 Taylor gap, R-08 FF vs CPI | DS/2023-11-01 valuation vs real rates; DS/2024-10-16 "not from real-rate theory" | Y | A | real = FF − CPI yoy; positive real → negative points (map undisclosed) | Mild: DS/2024-10-16 prefers market gauges to real-rate theory |
| A-15 | Component yield curve: +5 pts, 10Y 4.25 − 2Y 3.79 = +0.46 (p.24) | regime | a: R-17 curve signal (10Y−2Y) | R-17 cites; DS/2026-02-27 "over-rated" | Y | D=R-17; A | 10Y−2Y level → points | R-17 treats curve as evidence only ("over-rated", 2026) |
| A-16 | Component credit spreads: +10 pts, HY OAS 327 bp (p.24) | regime | a: R-17 credit trend; R-11 HY OAS (inverted, fragility) | R-17 | Y (1997→) | D=R-17; A | HY OAS level → points (tight = bullish) | R-11 reads tight OAS as excess; article reads it as bullish |
| A-17 | Component dollar (DXY): −6 pts, 99.85, "3mo trend" (p.24) | regime | c: R-10 (USD one of three) | RS/2024-11-06 "dollar up … death knell" | P: DXY not in amber; broad USD (DTWEXBGS spliced) as proxy | A | 3-month % change of USD index; rising → negative points | — |
| A-18 | Component VIX: −2 pts, 26.8, "Low + contango = bull" (p.24) | regime | d | none | Y: VIXCLS 1990→, VX term structure CBP 2004→ | A | points = f(VIX level, VX1−spot contango sign) | — |
| A-19 | G1 waterfall effect: 916 → 916 (no elimination; regime selects weight profile) (p.7) | regime | d | none | Y | A | G1 sets weight profile (A-40..A-44) and worldview (A-46..A-60); eliminates nothing | — |
| A-20 | G2 Liquidity: "thin-volume names exit"; 916 → 915 (p.6–7) | liquidity | a: R-33 ADV veto (`liq.instrument_min_adv_usd` 50 M) | DS/2009 Feig (exit cost 1–2% of fund) | Y (Alpaca 2021→; futures OI via IBKR) | D=R-33; A | 20-day ADV < `art.liquidity.min_adv_usd` → out; article threshold undisclosed (removes ~0.1%); interpreted $5 M | Threshold differs from R-33 |
| A-21 | G3 Forensic veto: score ≥ 45; −571 (p.6) | forensics | b: R-34 | none (Steinhoff short DS/2017-12-12 is a thesis, not a screen) | P: SEC facts 2009→ PIT in amber; 8-K/NT filing index partial | A | Equities only; score 0–100 = mean of A-22..A-26 sub-scores; < 45 → eliminated; missing sub-score → unknown (article's −62% suggests missing = fail; not reproduced) | — |
| A-22 | Forensic: accrual inflation (p.6); "accrual ratio abnormalities" (p.28) | forensics | b: R-34 | none | Y (facts) | A | Sloan accruals (NI − CFO)/avg assets, sector percentile → sub-score | — |
| A-23 | Forensic: revenue recognition vs cash flow; "revenue/cash flow divergence last two quarters" (p.6, p.28) | forensics | b: R-34 | none | Y | A | revenue growth − CFO growth, last 2 quarters → sub-score | — |
| A-24 | Forensic: balance-sheet deterioration masked by GAAP (p.6) | forensics | b: R-34 | none | Y | A | DSO and inventory-days change, Beneish-type indices (interpreted) | — |
| A-25 | Forensic: auditor changes (p.6, p.28) | forensics | b: R-34 | none | P: needs 8-K Item 4.01 index | A | 8-K Item 4.01 within 24 months → penalty | — |
| A-26 | Forensic: 10-K delays (p.6) | forensics | b: R-34 | none | P: needs NT 10-K index | A | NT 10-K filed or 10-K later than deadline → penalty | — |
| A-27 | G4 Sector rotation: regime sets sector tailwinds; names in sectors not fitting regime die; −222 (text p.6) / "~546" (p.14) | rotation | c: R-15/R-16 leading-industry RS, T15/T16 | DS/2016-11-10 (fiscal regime → long materials/value); RS/2020-08-18 13F tech→cyclicals; RS/2026-02-26 financials/RSP | Y (sector ETFs 2021→; GICS from profiles) | A+D | sector tilt from active worldview theses (A-58); eliminate names whose sector net tilt < 0 (interpreted; reproduces 344 → 122 only approximately) | Spec has no sector-elimination step; his rotations are thesis-driven, not table-driven |
| A-28 | G4 example: neutral regime + elevated real rates + mixed credit → energy and defensives boosted, unprofitable growth penalized (p.6) | rotation | d | none | Y | A | unprofitable (TTM NI < 0) growth names get −0.35 tilt when real-rate component < 0 | — |
| A-29 | Sector rotation panel: avg signal score per GICS sector, bulls/bears counts; Energy 53.8 top (p.4, p.11) | rotation | d | none | Y | A | sector score = mean convergence (A-118) of members; bull = module-agree ≥ 4 (A-119), bear = convergence < 40 (interpreted) | — |
| A-30 | G5 Technical trend: 122 → 18; tech label BUY/NEUTRAL + score (CTRA BUY 64, FFIN NEUTRAL 43) (p.7, p.8, p.15) | trend | a: R-29 chart veto (3-horizon majority + RS) | DS/2009 Feig "chart stinks, I won't do it"; DS/2021-05-11 | Y | D=R-29; A | tech score 0–100 (price vs 50/200-day MA, 3/6/12-month ROC, RS vs sector); pass if ≥ `art.trend.min` (undisclosed; interpreted 50, consistent with BUY 64 pass) | — |
| A-31 | G6 Fundamental quality: 18 → 18 (criteria paywalled) (p.7) | quality | b: R-35 (ROIC > 15%, Debt/EBITDA < 2.5×, from manual prompt) | conflict: DS/2026-02-27 Teva 6× P/E rerating; DS/2017-12-12 "underearning" | Y (facts) | A! | Equities: pass if ROIC > 15% AND Debt/EBITDA < 2.5× AND 90-day EPS revision ≥ 0 (A-144); non-equities pass | Quality screen excludes his underearning/re-rating setups |
| A-32 | G7 Smart money: fail text "smartmoney=0 < 50, capital_flow=0, insider_net=0" (p.7 screenshot) | smart money | b: R-36 | none | P: 13F 2001→ Y; Form 4 2024Q3→ quarterly; flows P | A | pass if Smart Money module (A-61) ≥ 50 OR Capital Flows (A-65) > 0 OR insider net 90d > 0 (OR-logic interpreted from the fail message) | — |
| A-33 | G8 Signal convergence: convergence ≥ 58 with ≥ 5 modules firing (table p.23; text p.7 "above 58"; fail text "< 58 or modules < 5") | convergence | c: R-38 `tier.min_independent_evidence` (families, not modules) | R-38 cites (invest then investigate; independent evidence) | P (module-dependent) | A | pass if convergence (A-118) ≥ 58 AND count(modules with score ≥ 50) ≥ 5 | — |
| A-34 | G9 Catalyst: fail text "catalyst=0 < 50, options_flow=0, squeeze=0"; all 6 G8 survivors fail (p.7) | catalyst | c: R-38 catalyst family within `tier.catalyst_window_bd` | DS/1992 NMW (catalyst sets timing); DS/2009 Feig (Schlesinger article) | P | A+D | pass if catalyst score ≥ 50 (A-120..A-125) OR options-flow flag OR squeeze flag | Squeeze trigger conflicts with R-31 (positioning never creates a thesis) → squeeze branch A! |
| A-35 | G10 Fat-pitch criteria (paywalled) (p.7) | convergence | d | n/a | n/a | A | undisclosed → interpreted: pass G1–G9 AND R:R ≥ 2.0 (A-129) AND conviction HIGH (A-119); flagged `undisclosed_rule` | — |
| A-36 | Non-equities bypass forensic/quality gates (BTC-USD, ADA-USD, CL=F, ZC=F reach G6–G8) (p.7) | convergence | d | n/a | Y | A | G3 and G6 pass-through for commodity/crypto | — |
| A-37 | Waterfall 2026-03-23: G0 916, G1 916, G2 915, G3 344, G4 122, G5 18, G6 18, G7 7, G8 6, G9 0, G10 0; second run G3 345, G4 200, G5 18, G6 18, G7 6, G8 0 (p.7) | UI | d | n/a | n/a | A | replication check only (not a target): article-faithful version run at 2026-03-23 reports its own waterfall beside these counts | — |
| A-38 | 2026-03-20: four pitches DVN, EOG, MPC, PSX (p.10, p.15) | UI | d | n/a | Y (2021→ prices) | A | replication check only | — |
| A-39 | "Every gate green" description of 2026-03-20: energy 53.8, Energy Intel firing, smart money via options flow, EIA catalyst (p.11) | convergence | d | n/a | P | A | replication check only | — |

## 3. Regime-adaptive weights and learning

| id | Article element (p.) | Cat | Cov / spec rule | D support | Data | Track | Implementation (RA rule) | Conflict |
|---|---|---|---|---|---|---|---|---|
| A-40 | Five regime weight profiles (p.21) | regime | d | none | n/a | A | weight vector per regime label; neutral profile = A-61..A-95 table; others = neutral with emphasis rows ×2 then renormalized (multiplier interpreted) | — |
| A-41 | strong_risk_off: Fed hiking, curve deeply inverted, credit stress → emphasis forensics, variant perception, UCC filings (p.21) | regime | d | none | n/a | A | emphasis multiplier on A-21, A-63, A-93 | — |
| A-42 | risk_off: mixed signals, defensive rotation, NFCI elevated → fundamental quality, smart money, AI regulatory (p.21) | regime | d | none | n/a | A | emphasis on A-31, A-61, A-81 | — |
| A-43 | neutral: balanced; Smart Money and Worldview 9% each, momentum/sentiment 2–3% (p.21) | regime | d | none | n/a | A | neutral = table weights (A-61..A-95) | — |
| A-44 | risk_on: improving breadth, falling credit spreads, M2 expanding → equal weighting baseline (p.21) | regime | d | none | n/a | A | all 35 modules equal weight (Reddit kept 0, A-95) | — |
| A-45 | strong_risk_on: bull trending, expanding earnings, Fed cutting → estimate momentum, digital exhaust, on-chain, retail sentiment (p.21) | regime | d | none | n/a | A | emphasis on A-76, A-86, A-94, A-78 | — |
| A-45a | Nightly Bayesian optimizer: module weights nudged by realized P&L, small moves around a prior (p.22) | convergence | d; spec rejects outcome-tuned weights (PLAN E.6) | none | Y (engine paper P&L, R-53) | A! | conjugate normal update of log-weights on each module's realized 20-day P&L attribution, prior = table, step cap `art.bayes.max_step` (interpreted 5% relative); walk-forward only; frozen variant reported alongside | Outcome-fitted weights conflict with PLAN E.6 / prereg; article track only and reported with and without updates |
| A-45b | Module leaderboard: most predictive modules over last 90 days (p.15) | UI | d | none | Y | A | rank modules by 90-day hit rate of score ≥ 50 vs next-20-day excess return (display) | — |

## 4. Worldview theses (p.22)

Trigger units are gauge points from A-12..A-18 (e.g., "Fed funds score < −5"), except where named otherwise. All triggers are levels, not changes.

| id | Thesis: trigger → favors / avoids | Cat | Cov / spec rule | D support | Data | Track | Implementation (RA rule) | Conflict |
|---|---|---|---|---|---|---|---|---|
| A-46 | tight_money: FF score < −5 AND real-rate score < −3 → Financials, Energy / Tech, Cons Disc, RE | regime | c: T02/T07 (equity reduce/short on tightening) | DS/2021-05-11 (tightening → equities down) | Y | A+D | active while trigger true; sector tilts per A-58 | Level trigger vs R-21; his response is index reduce, not sector swap |
| A-47 | easy_money: FF score > +5 AND M2 score > +3 → Tech, Cons Disc, RE / Financials | regime | c: T01 (LIQ up + easing → equity long) | DS/2014-07-16 "stay long until the Fed tightens" | Y | A+D | as A-46 | Level trigger vs R-21 |
| A-48 | strong_dollar: DXY score < −5 → Utilities, Staples, Healthcare / Materials, Energy, Industrials | regime | c: R-10 USD leg | RS/2024-11-06 | P (USD proxy) | A | as A-46 | — |
| A-49 | weak_dollar: DXY score > +5 → Materials, Energy, Industrials / Staples, Utilities | regime | c: T21 (easing + USD down → commodity long) | DS/1992 NMW 1987 weak dollar; T21 | P | A+D | as A-46 | — |
| A-50 | credit_stress: credit score < −5 → Utilities, Staples, Healthcare / Financials, RE, Cons Disc | regime | c: T19 (credit short on widening) | R-17 | Y | A+D | as A-46 | — |
| A-51 | steepening_curve: curve score > +8 → Financials / Utilities, RE | regime | c: R-17 | conflict-adjacent: DS/2026-02-27 curve "over-rated" | Y | A | as A-46 | — |
| A-52 | risk_off: VIX score < −8 AND total < −20 → Utilities, Staples, Healthcare + Gold / Tech, Cons Disc, Materials | regime | d | partial: gold held as policy hedge until 2016 (DS/2016-11-10) | Y | A | as A-46; Gold tagged symbol (+0.55) | — |
| A-53 | ai_capex_supercycle: "AI research score" > 50 → Tech, Comms + tagged semis/hyperscalers / — | regime | d | DS/2023-05-09, DS/2023-06-07 (AI secular theme held against bearish macro), DS/2024-05-07 (Nvidia sized up after ChatGPT) | N: "AI research score" source undisclosed | A+D | AI score undisclosed → interpreted proxy: SMH 6-month RS vs SPY percentile × 100; tagged list frozen | D-track would need a new secular-theme transition row (re-registration) |
| A-54 | em_slowdown: EM GDP trend < −1.0 → Utilities, Staples, Healthcare / Materials, Industrials, Energy | regime | d | none | P: IMF/OECD folders in amber (series unverified) | A | EM real GDP growth trend (IMF WEO/OECD) change, units undisclosed (interpreted pp) | — |
| A-55 | global_trade_contraction: global trade trend < −2.0 → Utilities, Staples / Industrials, Materials, Tech | regime | c: T23 tariff event flags | DS/2019-06-07 (tariff tweet → net flat), DS/2025-04-06 (tariffs above 10%) | P: CPB World Trade Monitor not in amber; BOPGSTB (US) proxy | A+D | trade-volume yoy trend, units undisclosed (interpreted pp) | His use is event-driven, not a trend threshold |
| A-56 | sovereign_risk: sovereign debt stress > 1.5 → Utilities, Staples, Healthcare + Gold / Financials, RE | regime | c: R-63 fiscal supply | DS/2009 Feig (next crisis sovereign); DS/2023-11-01 | P: definition undisclosed; IRLTLT01 spreads (IT−DE) in amber as proxy | A+D | z-score of IT−DE 10y spread (interpreted proxy) > 1.5 | — |
| A-57 | capital_rotation_to_dm: DM GDP advantage > 1.5 AND DXY score < −3 → Tech, Healthcare, Financials / Materials | regime | c: R-12, R-24 region-relative | DS/2015-03-02 (long Japan/Europe where QE starts) | P | A+D | DM ex-US minus US GDP growth (pp) > 1.5 | His region theses run on policy impulse, not GDP |
| A-58 | Tilt scoring: +0.55 tagged symbols, +0.35 bullish sector, −0.35 bearish sector, summed over active theses | rotation | d | none | Y | A | worldview tilt per name = Σ active-thesis tilts, clipped [−1, +1], rescaled to 0–100 = Worldview module (A-62) | — |
| A-59 | Final score blend: 50% worldview tilt + 30% technical + 20% fundamental | convergence | d | none | Y | A | `wv_final = 0.5·WV + 0.3·tech(A-30) + 0.2·fund(A-31 composite)` | Fundamental leg includes valuation (R-13: valuation context only) |
| A-60 | Top 15 names get a Gemini "Druckenmiller-style narrative" | UI | d | n/a | n/a | A | display only; templated text, never first person, labelled article-origin | Persona narrative must not be presented as his view (process.md scope) |

## 5. 35-module convergence engine (p.23–24; weights = neutral profile)

| id | Module (weight): data sources as printed | Cat | Cov / spec rule | D support | Data | Track | Implementation (RA rule; score 0–100, ≥ 50 = firing) | Conflict |
|---|---|---|---|---|---|---|---|---|
| A-61 | Smart Money (9%): SEC 13F (7 tracked managers), Form 4 insider transactions, capital flow aggregates | smart money | b: R-36 | none (library uses 13F only to record his own holdings) | P: 13F 2001→ Y; Form 4 2024Q3→; manager list undisclosed | A | 0.5·(net 13F share change by 7 frozen managers, lagged 45 d) + 0.5·(insider net $ 90d, A-123); manager list interpreted and frozen | — |
| A-62 | Worldview (9%): macro thesis alignment — Fed policy, sector tilt, geopolitical regime | regime | c: transition table T01–T25 | R-01, R-21 | Y | A | = A-58 rescaled | Level vs change (R-21) |
| A-63 | Variant (7%): consensus deviation — where the view diverges from sell-side | quality | d | partial: DS/2026-02-27 Teva (mismatched shareholder base) | N: no consensus history (Alpha Vantage snapshots 2026-09→ only) | A | (engine fair-value proxy − consensus PT)/price; unknown before consensus history exists | — |
| A-64 | Analyst Intel (5%): rating changes, price-target revisions, consensus shifts | quality | d | none | N (forward snapshots only) | A | 90-day net upgrades + PT revision % | — |
| A-65 | Capital Flows (5%): dark-pool activity, fund-flow proxies, smart-manager accumulation | smart money | c: R-36 | none | P: FINRA Reg SHO short volume, N-PORT holdings Y; dark-pool ATS not in amber | A | N-PORT aggregate holding change + off-exchange volume share change | — |
| A-66 | Short Interest (4%): FINRA short interest, days to cover, squeeze score, borrow cost | smart money | d | conflict: R-31 (DS/2009 "crowd makes money 80% of the time"; DS/2026-02-27 crowding irrelevant if thesis right) | P: FINRA SI 2025-09→; borrow cost N | A! | squeeze score = SI % float × days-to-cover percentile | Positioning as signal contradicts R-31 |
| A-67 | Options Flow (4%): unusual options activity, put/call, large block trades, gamma exposure | smart money | d | none; R-31 conflict for contrarian reading | P: Tradier chains forward-only (2 days); IBKR OPRA delayed (D-12) | A | front-two-expiry volume/OI z-score, put/call; history unknown | Contrarian put/call reading conflicts with R-31; directional (follow) reading does not |
| A-68 | Foreign Intel (3%): ADR premiums, cross-listed equity flows, FX positioning | rotation | c: R-12/R-24 | DS/2015-04-15 diverging policy → FX | P: ADR bars 2021→ + FX Y; home-listing prices N | A | ADR premium vs home listing × FX; FX positioning from COT TFF | — |
| A-69 | Research (3%): earnings estimate revisions, analyst rating changes, PT momentum | quality | d | none | N | A | as A-64 on 30-day window | — |
| A-70 | Displacement (3%): NLP on news — events that structurally reset fundamentals | catalyst | c: R-22/R-50, T23 event flags | DS/2016-11-10 (election ends thesis); DS/2019-06-07 (tariff) | P: GDELT GKG forward snapshots | A+D | news materiality classifier (LLM) on GDELT; history = manual event flags | — |
| A-71 | Sector Expert (3%): sector ETF flow proxy, peer-group relative strength, rotation quadrant | rotation | c: R-15/R-16 leading-industry RS | DS/2022-06-XX (stocks lead fundamentals 6–12 m); R-16 cites | P: ETFs 2021→; flows N | A+D | RRG quadrant (RS ratio, RS momentum) of name vs sector and sector vs SPY | — |
| A-72 | Pairs Trading (3%): relative value vs sector peers — mean reversion and divergence | trend | d | conflict: R-29/R-19 trend discipline | Y (2021→) | A! | z-score of log price ratio vs peer basket; score high when cheap vs peers | Mean reversion against trend contradicts chart veto |
| A-73 | M&A Intel (3%): rumour NLP, deal-premium comps, sector consolidation | catalyst | d | none | P: 8-K Item 1.01/2.01 via EDGAR; rumours N | A | deal stage ladder (A-125) + target profile | — |
| A-74 | Energy Intel (3%): EU gas storage (GIE), ENTSO-G flows, LNG utilisation, EIA storage surprise | catalyst | d | partial: R-25 focus on what moves the security; DS/1992 NMW industry drivers | P: EIA weekly 1982→ Y; GIE/ENTSO-G N (free APIs, no loader) | A | refiner and upstream sub-scores per A-126/A-127; EIA surprise vs 5-year seasonal change (consensus not free) | — |
| A-75 | Patterns/Options (3%): technical patterns (flags, wedges, breakouts) + options flow score | trend | c: R-29 | R-29 cites; R-32 (technicals ~20% as effective) | P | A | breakout above N-day high on volume + A-67 | — |
| A-76 | Est. Momentum (3%): EPS revision momentum, revenue beat rate, guidance trajectory | quality | c: D-14 SUE planned; R-25 | partial: R-25 (banks → earnings, NMW); DS/2017-12-12 underearning | P: SEC facts SUE Y 2009→; consensus N | A | SUE from facts (actual vs seasonal random walk) + beat rate; consensus revisions unknown | — |
| A-77 | Earnings NLP (3%): call transcript NLP — tone, language shift, management confidence | quality | d | partial: DS/2026-02-27, RS/2024-11-06 bottom-up mosaics from listening to companies (spec §10.3: not mechanizable) | P: Alpha Vantage transcripts forward, sparse | A+D | VADER fin-dictionary tone delta vs prior call (A-180) | — |
| A-78 | Retail Sentiment (3%): Stocktwits, retail order-flow proxies, social volume spikes | smart money | d | none; R-31 if read contrarian | N | A | unknown (no free history) | Contrarian use conflicts with R-31 |
| A-79 | Main Signal (2%): primary composite BUY / STRONG BUY / HOLD / SELL from main pipeline | convergence | d | none | n/a | A | undisclosed → interpreted: = A-59 `wv_final` bucketed (≥ 70 STRONG BUY, ≥ 55 BUY, ≥ 40 HOLD, else SELL) | — |
| A-80 | Prediction Mkts (2%): Polymarket macro event probabilities (Fed, CPI, elections) | catalyst | c: PLAN D-20 data at weight 0; R-23 market-implied path | DS/2024-10-16 "markets are better predictors than professors" | P: Polymarket history in amber (2020→ for listed markets) | A+D | Δ implied probability of FOMC cut/hike over 5 days mapped to sector sensitivities (A-176); D variant: alternative to `DGS2 − FF` in R-23 | — |
| A-81 | AI Regulatory (2%): AI/regulatory event risk — patent filings, lobbying activity, agency actions | catalyst | d | none | N | A | unknown | — |
| A-82 | Blindspots (2%): high-quality names below consensus radar — low coverage, underowned | quality | d | partial: DS/2026-02-27 Teva (shareholder-base mismatch) | P: 13F ownership Y; analyst count N history | A | quality pass (A-31) × low institutional ownership percentile | — |
| A-83 | Gov Intel (2%): government contract awards, federal spending, defence procurement | catalyst | d | none | N (USAspending free API, no loader) | A | award $ last 90d / revenue | — |
| A-84 | Labor Intel (2%): job postings (LinkedIn/Indeed proxy), layoff signals, wage data | catalyst | c: PLAN D-20 data | none | P: WARN, DOL H-1B LCA Y; postings N | A | H-1B LCA count yoy (AI-adjacent SOC codes) and WARN notices → sub-scores (A-173) | — |
| A-85 | Supply Chain (2%): supplier network stress, port congestion, freight rate signals | catalyst | d | none | N | A | unknown | — |
| A-86 | Digital Exhaust (2%): app downloads, web traffic, credit-card spend proxies | catalyst | d | none | N | A | unknown | — |
| A-87 | Pharma Intel (2%): FDA calendar, clinical-trial registrations, drug-approval pipeline | catalyst | d | none | N (ClinicalTrials.gov free, no loader) | A | PDUFA date within window → catalyst; trial count yoy | — |
| A-88 | Alt Data (2%): satellite imagery, ENSO/climate signals, web-traffic proxies | catalyst | c: PLAN D-20 (NOAA, MODIS) | none | P: NOAA climdiv, corn-belt weekly, drought, MODIS NDVI Y | A | NDVI anomaly vs 10-year same-week mean (A-177) | — |
| A-89 | AAR Rail (2%): AAR weekly carloads — intermodal, chemicals, grain as economic proxy | catalyst | d | partial: R-16 transports as leading industry (price-based) | N (AAR weekly free, no loader) | A | carload yoy by commodity group | — |
| A-90 | Ship Tracking (2%): AIS vessel tracking, port congestion, dry-bulk/tanker utilisation | catalyst | d | none | N | A | unknown | — |
| A-91 | Patent Intel (2%): USPTO filing velocity by tech class; 20%+ YoY flags innovation acceleration | catalyst | d | none | N (PatentsView free, no loader) | A | applications yoy by assignee; ≥ 20% → firing (article threshold) | — |
| A-92 | UCC Filings (2%): UCC-1 financing statements — secured lending as early distress/growth signal | forensics | d | none | N | A | unknown | — |
| A-93 | Board Interlocks (2%): director network overlap — shared board seats as M&A and governance signal | catalyst | d | none | N (DEF 14A parse, no loader) | A | unknown | — |
| A-94 | On-Chain Intel (2%): on-chain whale flows, exchange net flows, stablecoin supply shifts (Nansen) | smart money | d | none | N (Nansen paid) | A | crypto only; unknown | — |
| A-95 | Reddit (1%): WallStreetBets + Reddit sentiment (unweighted — informational only) | smart money | d | none | N | A | display only, weight 0 in all profiles (article: unweighted) | — |

## 6. Convergence, catalysts, trade cards, breadth, economic indicators

| id | Article element (p.) | Cat | Cov / spec rule | D support | Data | Track | Implementation (RA rule) | Conflict |
|---|---|---|---|---|---|---|---|---|
| A-118 | Convergence score per asset, all 923 ranked, top per sector (p.15; FFIN 50 / 50.3; CTRA modules) | convergence | c: R-38 evidence count | R-38 | P | A | weighted mean of available module scores with regime weights, renormalized over non-unknown modules | — |
| A-119 | Module agreement and conviction: "HIGH conviction: 4 modules agree"; FFIN dossier "4 bullish · 0 bearish · 17 neutral"; firing modules ≥ 50, neutral 26–42 (p.8, p.10, p.16, p.19) | convergence | c: R-38 | R-38 | P | A | firing = score ≥ 50; bearish = score < 25 (interpreted; 26 shown neutral); HIGH ≥ 4 firing, MODERATE 3, LOW 2, AVOID ≤ 1 or bearish > firing (interpreted ladder) | — |
| A-120 | Signal conflicts view: names where modules disagree (p.15) | convergence | c: T25 conflicting theses | R-54 | P | A | flag if firing ≥ 2 AND bearish ≥ 2 | — |
| A-121 | Composite score (FFIN 42.5), distinct from convergence (p.19) | convergence | d | none | n/a | A | undisclosed → = A-59 `wv_final` (interpreted; flagged) | — |
| A-122 | Catalyst: EIA weekly inventory report two sessions out, consensus build vs weekly data implying draw (p.3, p.11) | catalyst | c: R-38 catalyst in window; R-30 price vs news | DS/1992 NMW; R-38 | P: EIA weekly Y; consensus N | A+D | scheduled EIA release within 2 sessions AND sign(model draw) ≠ sign(consensus) — consensus unknown → surprise proxy vs 5-year seasonal | — |
| A-123 | Insider cluster catalyst: INSIDER_CLUSTER 100, $819,858 cluster buy across directors (p.15, p.17) | catalyst | b: R-36 | none | P: Form 4 2024Q3→ quarterly; daily parser D-10 | A | catalyst = 100 if cluster buy (A-124) in last 30 days | — |
| A-124 | Cluster buy = ≥ 3 insiders in 90 d; "Large C-suite" buy; "Unusual volume (6.5x avg)"; panel: buy value 30D, sell value 30D, large buys, top buyer, net insider shares/value 90D (p.4, p.8–9, p.18) | smart money | b: R-36 | none | P | A | cluster = ≥ 3 distinct insiders open-market buys in 90 d (article); large = officer buy ≥ `art.insider.large_usd` (interpreted $100 k); unusual = 30-day buy count ≥ 3× 1-year average (interpreted; 6.5× is an observation) | — |
| A-125 | M&A signal: target profile score (59), deal stage rumor / confirmed_interest / definitive_agreement, credibility (100), expected premium, "profile + rumor convergence"; top-targets list (p.10, p.13–14) | catalyst | d | none | P: 8-K Item 1.01 Y; rumours N | A | stage score: rumor 40, confirmed_interest 70, definitive 100 (interpreted); M&A = 0.5·profile + 0.5·stage | Definitive-agreement targets are deal-spread trades; not his style (no stated rule) |
| A-126 | Energy refiner score = f(margin, demand): VLO/PSX/MPC 69 = margin 44, demand 86 (p.19–20) | catalyst | d | partial: R-25 | P: EIA crack inputs (WPULEUS3 utilisation, product supplied) Y | A | refiner = mean(margin, demand) reproduces 65 not 69 → weights undisclosed; interpreted equal weight, flagged | — |
| A-127 | Energy upstream score = f(inventory 40, production 63, demand 86, flow 44, global 50) = 56 (p.20) | catalyst | d | partial: R-25 | P | A | equal-weight mean = 56.6 (consistent) | — |
| A-128 | Refiners and upstream firing together = macro signal on the energy complex (p.19) | rotation | d | none | P | A | sector flag if both sub-scores ≥ 55 (interpreted) | — |
| A-129 | Trade card entry (last close): CTRA $33.97; FFIN $28.65 (card) / $28.95 (text) (p.8, p.15–16) | sizing-exit | d | n/a | Y | A | entry = asof close | — |
| A-130 | Stop price: CTRA $28.91 (−14.9%); FFIN $26.60 (−7.2%) (p.8, p.16, p.19) | sizing-exit | conflict: R-49 no stop-losses (`exit.stop_loss` = false) | conflict: DS/2009 Feig "never used a stop loss" | Y | A! | stop = min(low, `art.sr.window_d` = 60 d) (support; interpreted); exit at stop | Contradicts R-49 |
| A-131 | Target price: CTRA $44.09; FFIN $38.06 (+32.8%) (p.8, p.16) | sizing-exit | conflict: R-52/R-50 (exit on top or premise break; never on valuation alone) | conflict: R-52 note (Nvidia early sales called mistakes) | Y | A! | target = max(high, 250 d) resistance (interpreted; FFIN target ≈ prior high); exit at target | Fixed profit target caps winners; contradicts R-52 |
| A-132 | R:R: CTRA 2.0×, FFIN 4.6×; "reward-to-risk based on technical support/resistance" (p.8, p.16, p.29) | sizing-exit | c: R-28 asymmetry to premise-break level; `size.asymmetry_min_ratio` | DS/2022-09-28 40:1 one-way bet (asymmetry yes, S/R no) | Y | A | R:R = (target − entry)/(entry − stop) | Denominator is price stop, not premise break (R-28) |
| A-133 | Conviction level HIGH / MODERATE / LOW / AVOID (p.29) | sizing-exit | c: tiers starter / fat pitch (R-38) | R-38 | n/a | A | = A-119 ladder | — |
| A-134 | Position size field shown blank "—" (p.19); no sizing rule disclosed | sizing-exit | a: R-40..R-48, R-57 (spec sizes; article does not) | DS/2022-06-XX | n/a | A | article-faithful: equal weight per pitch, gross ≤ 100% (interpreted, flagged) | — |
| A-135 | Verdict: 1–2 highest-conviction names (p.28) | sizing-exit | a: R-39 (1–2 fat pitches a year — rate, not count per run) | RS/2015-01-18 | n/a | A | keep top 2 G10 survivors by convergence | — |
| A-136 | Status badges MOMENTUM / WATCH / NOTABLE / HIGH; tech BUY / NEUTRAL; gate badge G2/G6/G8 (p.4, p.8, p.15) | UI | d | n/a | n/a | A | display | — |
| A-137 | Breadth: % above 200dma 43.8–44%, A/D ratio 0.23, new 52w highs/lows 21/81; header "BREADTH 0" (p.4, p.24) | trend | c: R-59 narrowing, R-60 thrust (S&P 500 member breadth 2021→) | RS/2024-11-06; DS/2015-04-15 | P: SPX member breadth 2021-09→; NYSE A/D 1965–2020 | A+D | display + risk_on condition "improving breadth" (A-44): 20-day Δ % above 200dma > 0 | Article does not score breadth into the gauge |
| A-138 | Economic Heat Index: 23 FRED indicators → Expansion / Neutral / Contraction; per-indicator MoM, trend, σ-score, improving/stable/deteriorating (p.15, p.25–26) | regime | d (display context in spec only through individual rules) | none | P (see A-139..A-161) | A | per indicator z = trend / σ, signed by economic direction; heat = mean z; Expansion > +0.5, Contraction < −0.5 (interpreted) | — |

Economic Heat Index components (p.25–26). Data column: Y = in amber lake; P = proxy in lake; N = not in lake (FRED, free; loader missing).

| id | Indicator (bucket) | Spec coverage | D support | Data | Track |
|---|---|---|---|---|---|
| A-139 | Initial jobless claims (leading) | d | conflict-adjacent: DS/2026-02-27 payrolls/unemployment "most misleading" | Y ICSA | A |
| A-140 | Continued claims (leading) | d | as A-139 | Y CCSA | A |
| A-141 | Building permits (leading) | c: R-16 homebuilders (price-based) | DS/2022-06-XX homebuilders | Y PERMIT | A |
| A-142 | UMich consumer sentiment (leading) | d | none | Y UMCSENT | A |
| A-143 | Avg weekly hours, manufacturing (leading) | d | none | N AWHMAN | A |
| A-144 | Core capital goods orders (leading) | d | none | P DGORDER (total durables) | A |
| A-145 | Fed balance sheet (leading) | a: R-03, R-14 | DS/2014-07-16, RS/2018-09-06 | Y WALCL | D=R-03; A |
| A-146 | Chicago Fed financial conditions (NFCI) (leading) | a: R-58 | DS/2024-10-16, DS/2024-05-07 | Y NFCI (2011-05→ PIT) | D=R-58; A |
| A-147 | 10Y breakeven inflation (leading) | d | none | Y T10YIE | A |
| A-148 | 5Y forward inflation expectation (leading) | d | none | P T5YIE (5y, not 5y5y) | A |
| A-149 | Sahm rule recession indicator (leading) | d | conflict-adjacent as A-139 | P derivable from UNRATE vintages | A |
| A-150 | 10Y–3M yield curve (leading) | c: R-17 (10Y−2Y; GS10−TB3MS era B) | R-17 | Y DGS10 − DGS3MO | A |
| A-151 | Nonfarm payrolls (coincident) | d | conflict-adjacent: DS/2026-02-27 | Y PAYEMS vintages | A |
| A-152 | Industrial production (coincident) | a: R-02 | DS/2009 Feig | Y INDPRO | D=R-02; A |
| A-153 | Retail sales (coincident) | d | none | Y RSAFS | A |
| A-154 | Real income ex transfers (coincident) | d | none | P PI (nominal) | A |
| A-155 | Unemployment rate (lagging) | a: R-06 | R-06 cites; conflict DS/2026-02-27 | Y UNRATE | D=R-06; A |
| A-156 | Core CPI (lagging) | c: R-06 sensitivity (CPILFESL missing) | R-07..R-09 use headline | N CPILFESL | A |
| A-157 | Core PCE (lagging) | d | none | Y PCEPILFE | A |
| A-158 | Avg duration of unemployment (lagging) | d | none | N UEMPMEAN | A |
| A-159 | Commercial & industrial loans (lagging) | d | none | N BUSLOANS | A |
| A-160 | Reverse repo outstanding (liquidity) | a: R-03 | R-03 cites | Y RRPONTSYD | D=R-03; A |
| A-161 | St. Louis Fed financial stress (liquidity) | c: R-58 (NFCI) | DS/2024-10-16 | N STLFSI4 | A |

## 7. Data sources, LLM layer, manual version

| id | Article element (p.) | Cat | Cov / spec rule | D support | Data | Track | Implementation (RA rule) | Conflict |
|---|---|---|---|---|---|---|---|---|
| A-162 | 40+ sources, PostgreSQL 117 tables, FastAPI, Next.js, 47,358 lines (p.26) | UI | n/a | n/a | n/a | — (descriptive; no rule) | none | — |
| A-163 | FRED: 23 macro indicators + proprietary Economic Heat Index (p.26) | data source | c | see A-138 | P | A | = A-138..A-161 | — |
| A-164 | SEC EDGAR 8-K filings, NLP-scored (p.27) | data source | d | none | P: EDGAR 8-K text not in lake | A | 8-K item codes + VADER tone (A-180) → Displacement / M&A inputs | — |
| A-165 | SEC EDGAR Form 4 insider transactions (p.27) | data source | b: R-36 | none | P (2024Q3→ quarterly; D-10 daily parser) | A | feeds A-61, A-123, A-124 | — |
| A-166 | SEC EDGAR 13F holdings "with the 45–135 day lag caveat" (p.27) | data source | b: R-36 | none | Y 13F 2001→ | A | 13F used only from filing date (`filed` ≤ asof); 45–135 d lag recorded | — |
| A-167 | EIA: production, storage, refining; "draws/builds read two days before most terminals" (p.27) | data source | c: R-25 driver map | partial | Y EIA weekly 1982→ | A | PIT by EIA release timestamp (Wed 10:30 ET); "two days early" claim not reproduced (EIA publishes on a fixed public schedule) | — |
| A-168 | Polymarket: macro and regulatory probabilities; "73% implied probability of a 25 bp cut at the next FOMC"; mapped to sector/stock impacts 30–60 days before consensus revisions (p.11, p.27) | data source | c: D-20 | DS/2024-10-16 | P | A+D | = A-80 | — |
| A-169 | Hyperliquid: weekend perps for Monday gap prediction (p.27) | data source | d (D-6 perps data only) | none | Y perps/hyperliquid | A | Monday gap forecast = weekend perp return (index perps) → display; no gate use disclosed | — |
| A-170 | NOAA + NASA MODIS: weather anomalies and NDVI; corn-belt drought before EIA/USDA reports (p.11, p.27) | data source | c: D-20 | none | Y | A | = A-88, A-177 | — |
| A-171 | BLS + OSHA + EPA + FCC regulatory filings parsed daily (p.27) | data source | d | none | P: BLS Y; OSHA/EPA/FCC N | A | event counts per ticker → AI Regulatory (A-81) | — |
| A-172 | OSHA, WARN, BLS H-1B: labor and innovation shifts 6–12 months before models (p.11) | data source | c: D-20 | none | P: WARN, LCA Y; OSHA N | A | = A-84, A-173 | — |
| A-173 | H-1B spike for AI-adjacent roles = innovation acceleration; WARN layoff filing = cost-structure signal before earnings call (p.11) | catalyst | c: D-20 | none | Y (LCA, WARN) | A | LCA count yoy ≥ `art.h1b.spike_yoy` (interpreted 50%) → +; WARN notice in 90 d → flag | — |
| A-174 | USPTO: patent velocity by tech class, 20%+ YoY = innovation acceleration (p.27) | data source | d | none | N | A | = A-91 | — |
| A-175 | CFTC disaggregated COT: commercial hedger positioning as smart-money proxy (p.11, p.27) | smart money | b: R-37 contrarian COT (weight 0) | conflict: R-31 | Y COT disagg/legacy/TFF | A! | commercial net % OI percentile (3 y); high = bullish (follows commercials, fades speculators) | Contradicts R-31 (no contrarian fade); R-31 keeps COT only as ≤ `crowd.max_entry_delay_bd` entry delay |
| A-176 | Prediction-market probabilities mapped into sector and stock impacts (p.11) | catalyst | d | partial DS/2024-10-16 | P | A | sector beta to Δ cut probability (rolling 1-year regression) | — |
| A-177 | Satellite vegetation indices: drought stress in corn belt before EIA and USDA (p.11) | catalyst | c: D-20 | none | Y | A | NDVI anomaly < −1σ in corn-belt weekly → ag/ethanol flag | — |
| A-178 | Gemini 2.5 Flash: foreign-language market analysis, 6 markets / 6 languages (JA, KO, ZH, DE, FR, IT) (p.27) | data source | d | none | N | A | unknown (paid LLM, no history); display only | — |
| A-179 | Gemini: M&A rumor probability scoring; regulatory event classification across 9 jurisdictions; news materiality; sector expert synthesis; investment memo generation (p.27) | catalyst | d | none | P (GDELT forward) | A | LLM classification on news text; history unknown | LLM outputs are not PIT-reproducible; flag `nondeterministic` |
| A-180 | Earnings sentiment on 8-K filings via VADER with a finance dictionary (p.27) | quality | d | none | P | A | VADER + finance lexicon on 8-K Exhibit 99 text | — |
| A-181 | All quantitative layers deterministic (convergence, cascade, technicals, regime) (p.27) | UI | a: spec determinism | n/a | n/a | D (spec); A | same | — |
| A-182 | Screener tabs: Insider, M&A, Energy, Blindspots, Displacement, Pairs, Estimate Momentum, Alt Data (p.15) | UI | d | n/a | n/a | A | display of module tables | — |
| A-183 | Biggest movers, live news ticker, Full Dossier, signal history (p.4, p.19) | UI | d | n/a | n/a | A | display | — |
| A-184 | Manual Step 1: 10Y–3M spread, VIX level, Chicago Fed NFCI → 5 regimes; sectors the regime historically favors/penalizes (p.28) | regime | c: R-17 curve, R-58 NFCI | R-58 | Y | A | variant regime `art.regime_manual`: z(10Y−3M) − z(VIX) − z(NFCI), 5 quintile-free bands (interpreted ±0.5, ±1.5 σ); reported beside A-10 | — |
| A-185 | Manual Step 2: 2 sectors overweight, 2 underweight; in the 2 favored sectors, top 5 stocks each by ROIC > 15%, Debt/EBITDA < 2.5×, most positive 90-day EPS revision trend (p.28) | rotation/quality | b: R-35 (ROIC, leverage) | conflict R-35 note (Teva, underearning) | P: ROIC, leverage from facts Y; EPS revisions N (SUE proxy) | A! | top-2/bottom-2 sectors by A-58 tilt; screen → 10 names | Quality screen vs underearning (as A-31) |
| A-186 | Manual Step 3: 13F net buyers/sellers; Form 4 net $ and direction; accrual ratio, auditor changes, revenue/cash-flow divergence last two quarters (p.28) | smart money/forensics | b: R-34, R-36 | none | P | A | = A-21..A-26, A-61, A-124 | — |
| A-187 | Manual Step 4: put/call ratio and unusual volume in front two expirations; material news in last 30 days not reflected in consensus PTs; EPS consensus change over 60 days (p.28) | convergence | d | none | P/N | A | = A-67 (2 expiries), A-70 (30 d window), A-76 (60 d window) | — |
| A-188 | Manual Step 5: 1–2 names; count of independent aligned signals; R:R from S/R; expected catalyst and timing; conviction HIGH/MODERATE/LOW/AVOID (p.28–29) | sizing-exit | c: R-38, R-28 | R-38 | Y | A | = A-119, A-132, A-133, A-135 | Price-stop R:R (A-130) |

Section numbering note: A-96..A-117 are unassigned (reserved; ids are not reused).

## 8. Article internal inconsistencies affecting implementation

| Item | Version A | Version B | Treatment |
|---|---|---|---|
| G8 threshold | text "above 58" (p.7) | table "≥ 58", fail text "< 58" (p.7, p.23) | ≥ 58 |
| Cascade stop | text: none of 7 clear G8 (p.7) | waterfall: 6 pass G8, 0 pass G9 (p.7) | screenshot |
| G4 eliminations | −222 (p.6) | "about 546" (p.14) | −222; 546 unreconciled |
| Universe | 923 (p.6) | 916 (p.7) | 916 in replication check |
| Neutral weights | table: Smart Money 9%, Worldview 9% (p.23); caption: "On-Chain Intel, Smart Money and Worldview carry the highest" (p.23) but On-Chain is 2% | FFIN dossier: Smart Money 15%, Worldview 13%, Blindspots 4%, Gov Intel 3%, Supply Chain 3%, Main Signal 3%, Digital Exhaust 2% (p.19) | table weights; dossier implies renormalization or another profile (undisclosed) |
| Weight total | printed weights sum to 109% (9+9+7+5+5+4+4 + 11×3 + 16×2 + 1) | — | renormalize to 100% |
| FFIN | entry $28.95 / stop $26.60 / 4.6× (text) | caption $27.08 / 4.9×, convergence 46; card $28.65 / 4.6×, convergence 50 / 50.3 | card values |
| Regime inputs | gauge: 7 components, 10Y−2Y (p.24) | manual: 10Y−3M, VIX, NFCI (p.28) | both: A-10 primary, A-184 variant |
| "Seven FRED-based indicators" | VIX contango and DXY are not FRED series | — | sources per A-17, A-18 |
| Stale universe | PXD listed (acquired 2024) (p.20) | — | PIT membership required (A-01) |

## 9. Summary

### 9.1 Counts by coverage status

167 counted rows: A-01..A-95 and A-118..A-188 (A-96..A-117 reserved, unused) plus sub-ids A-45a, A-45b; A-162 (descriptive stack, no rule) excluded. Tallied mechanically from the tables above.

| Status | Count | Ids |
|---|---|---|
| a — covered by a Druckenmiller-sourced rule | 17 | A-02, A-04, A-05, A-07, A-12, A-15, A-16, A-20, A-30, A-134, A-135, A-145, A-146, A-152, A-155, A-160, A-181 |
| b — present as weight-0 article rule (R-34..R-37) | 16 | A-21..A-26, A-31, A-32, A-61, A-123, A-124, A-165, A-166, A-175, A-185, A-186 |
| c — partially covered | 50 | A-01, A-06, A-08, A-09, A-10, A-13, A-14, A-17, A-27, A-33, A-34, A-46..A-51, A-55..A-57, A-62, A-65, A-68, A-70, A-71, A-75, A-76, A-80, A-84, A-88, A-118..A-120, A-122, A-132, A-133, A-137, A-141, A-150, A-156, A-161, A-163, A-167, A-168, A-170, A-172, A-173, A-177, A-184, A-188 |
| d — missing | 84 | A-03, A-11, A-18, A-19, A-28, A-29, A-35..A-45b, A-52..A-54, A-58..A-60, A-63, A-64, A-66, A-67, A-69, A-72..A-74, A-77..A-79, A-81..A-83, A-85..A-87, A-89..A-95, A-121, A-125..A-131, A-136, A-138..A-140, A-142..A-144, A-147..A-149, A-151, A-153, A-154, A-157..A-159, A-164, A-169, A-171, A-174, A-176, A-178..A-180, A-182, A-183, A-187 |

A-130 (stops) and A-131 (targets) are counted under d: no spec rule implements them, and R-49/R-52 contradict them.

Data feasibility (amber): Y 64, P 60, N 24, n/a 19. N rows: A-53 (AI score source), A-63, A-64, A-69, A-78, A-81, A-83, A-85..A-87, A-89..A-95, A-143, A-156, A-158, A-159, A-161, A-174, A-178.

### 9.2 Counts by track (owner decision 2026-10-07: every row enters the article track)

| Track | Count | Pre-decision equivalent | Ids |
|---|---|---|---|
| D=R-xx (Druckenmiller track covers it with its own rule; article version also runs in V-AF) | 16 | adopt (already adopted) | A-04..A-07, A-12, A-13, A-15, A-16, A-20, A-30, A-145, A-146, A-152, A-155, A-160, A-181 |
| A+D (article track + Druckenmiller-track candidate; library support exists) | 17 | adopt as D variant, weight 0 until registered | A-27, A-34, A-46, A-47, A-49, A-50, A-53, A-55, A-56, A-57, A-70, A-71, A-77, A-80, A-122, A-137, A-168 |
| A (article track only; no library support, no conflict) | 126 | weight-0 article variant | all other rows |
| A! (article track only; conflicts with stated process) | 8 (+ A-34 squeeze branch) | exclude from D track | A-31, A-45a, A-66, A-72, A-130, A-131, A-175, A-185 |

Total 16 + 17 + 126 + 8 = 167.

### 9.3 Missing items to add as weight-0 article rules (article-faithful build)

Priority 1 (defines the article pipeline; free data exists): A-03 cascade; A-10/A-11 regime score and thresholds; A-12..A-18 seven gauge components (A-18 VIX + VX contango is new); A-19 regime-as-profile-selector; A-20 article liquidity threshold; A-27/A-28 sector elimination; A-30 tech score; A-32 G7 OR-logic; A-33 G8 (≥ 58, ≥ 5 modules); A-34 G9 (≥ 50); A-35 G10 (interpreted); A-36 non-equity bypass; A-40..A-45 five weight profiles; A-46..A-57 twelve worldview theses; A-58 tilt (+0.55 / ±0.35); A-59 50/30/20 blend; A-118/A-119 convergence and module agreement; A-129..A-133 trade card (entry, stop, target, R:R, conviction); A-138..A-161 Economic Heat Index.

Priority 2 (modules with free data in amber): A-61 Smart Money (13F + Form 4), A-65 Capital Flows, A-66 Short Interest, A-68 Foreign Intel, A-71 Sector Expert, A-72 Pairs, A-73 M&A (8-K stage), A-74/A-126/A-127 Energy Intel, A-75 Patterns, A-76 Est. Momentum (SUE proxy), A-80 Prediction Mkts, A-82 Blindspots, A-84/A-173 Labor Intel, A-88/A-177 Alt Data, A-169 Hyperliquid weekend gap, A-175 commercial-hedger COT.

Priority 3 (loader needed, free source exists): A-83 Gov Intel (USAspending), A-87 Pharma (ClinicalTrials.gov, FDA), A-89 AAR Rail, A-91/A-174 Patent Intel (PatentsView), A-74 GIE/ENTSO-G, A-143/A-156/A-158/A-159/A-161 five FRED series (AWHMAN, CPILFESL, UEMPMEAN, BUSLOANS, STLFSI4), A-25/A-26 EDGAR 8-K 4.01 and NT 10-K index.

Priority 4 (no free history → registered as `unknown`): A-63 Variant, A-64 Analyst Intel, A-69 Research, A-67 options history, A-78 Retail Sentiment, A-81 AI Regulatory, A-85 Supply Chain, A-86 Digital Exhaust, A-90 Ship Tracking, A-92 UCC, A-93 Board Interlocks, A-94 On-Chain, A-95 Reddit (weight 0 by the article itself), A-178/A-179 LLM layers (non-reproducible point-in-time).

### 9.4 Items that contradict his stated process (article track only)

| id | Article element | Contradicted rule | Citation |
|---|---|---|---|
| A-130 | Price stop-loss on every trade card | R-49 no stop-losses | DS/2009 Feig: "I have never used a stop loss in my career." |
| A-131 | Fixed profit target exit | R-52 / R-50 (exit on technical top or premise break, never on valuation alone) | RS/2024-11-06; Nvidia early-sale episodes (DS/2024-05-07, DS/2026-02-27) |
| A-132 (denominator) | R:R measured to a price stop | R-28 asymmetry to premise-break level | DS/2022-09-28 40:1 |
| A-175 | Commercial-hedger COT as smart-money proxy (fade speculators) | R-31 no contrarian fade | DS/2009 Feig: "crowd makes money 80% of the time"; DS/2026-02-27 |
| A-66, A-34 squeeze | Short-interest squeeze score as signal / catalyst | R-31 positioning never creates a thesis | as above |
| A-67, A-78 (contrarian reading) | Put/call and retail sentiment read against the crowd | R-31 | as above |
| A-72 | Pairs mean reversion against trend | R-29 chart veto, R-19 trend | DS/2009 Feig "chart stinks, I won't do it" |
| A-31, A-185 | ROIC > 15% / Debt/EBITDA < 2.5× quality gate | process.md R-35 note | DS/2026-02-27 Teva 6× P/E re-rating; DS/2017-12-12 "underearning" |
| A-45a | Nightly Bayesian re-weighting on realized P&L | PLAN E.6 (≤ 8 tunables, no outcome tuning), prereg | design rule, not a Druckenmiller statement |
| A-46..A-57 (trigger form) | Level-triggered theses | R-21 change, not level | RS/2022-06-10: "The present doesn't move stock prices, change does." |
| A-01 (universe) | Equities-heavy universe, no rates/FX | R-26 rates/FX first, R-05 bear-market profits in bonds/FX | RS/2018-09-06; RS/2024-11-06 |
| A-59 (fundamental leg) | Valuation inside the score | R-13 valuation is context only | DS/2015-03-02 |

Mild tensions kept in A+D or A without a ban: A-14 real-rate component (DS/2024-10-16 "not from real-rate theory"); A-15/A-51 curve weighting (DS/2026-02-27 "over-rated"); A-16 tight HY OAS read bullish vs R-11 fragility reading; A-139/A-151/A-155 labor data (DS/2026-02-27 "most misleading").

## 10. Leaderboard structure: three comparable versions

| Item | V-DF Druckenmiller-faithful | V-AF Article-faithful | V-HY Hybrid |
|---|---|---|---|
| Rule set | process.md R-01..R-65; all `interpreted-from-article` weights 0 (current spec) | RA-01..RA-188 at article weights; R-xx unused except PIT/unknown conventions (§0) | V-DF pipeline + A+D rows as extra evidence families; article modules feed step 5 for single-name equity expressions |
| Universe | multi-asset (rates, FX, commodities, equity indices/sectors, credit, crypto) | PIT S&P 500 + 400, 14 commodities, 6 crypto (A-01) | V-DF universe ∪ V-AF single names |
| Regime | R-02/R-03/R-04, R-06, R-58 state vector; 5-level label display only | A-10 gauge (score 0–100, 5 labels), A-184 manual variant reported | V-DF regime primary; A-10 gauge as reported variant and as one evidence family when aligned |
| Theses | transition table T01–T25 (change-triggered) | worldview A-46..A-57 (level-triggered) + sector tilts | T01–T25 primary; A+D worldview rows (A-46, A-47, A-49, A-50, A-53, A-55..A-57) as evidence for matching T-rows; no level-triggered thesis creation |
| Gates / vetoes | R-29 chart, R-30 price vs news, R-31 crowding delay, R-33 liquidity, R-62 short entry | G1–G10 cascade (A-10..A-36): forensic ≥ 45, sector fit, tech, quality, smart money ≥ 50, convergence ≥ 58 with ≥ 5 modules, catalyst ≥ 50, G10 | V-DF vetoes; add A-21 forensic veto for single names only (no D conflict); A-31 quality gate not applied (conflict) |
| Fat pitch | starter + ≥ `tier.min_independent_evidence` families | survives G10; top 1–2 by convergence | V-DF rule; article convergence (A-33 pass) counts as one family; G9 catalyst (excluding squeeze) counts toward catalyst family |
| Sizing | R-40..R-48, R-57 `size_band` | equal weight per pitch, gross ≤ 100% (A-134, interpreted) | V-DF sizing |
| Exits | R-49 no stops, R-50 premise break, R-51, R-52 tops | stop (A-130), target (A-131), plus G-fail on re-run | V-DF exits; A-130/A-131 never used (R-49/R-52 win) |
| Weights learning | none (frozen, prereg) | A-45a Bayesian updates; reported as V-AF (updates on) and V-AF0 (frozen) | none |
| Conflict resolution | n/a | n/a | every A! row disabled; on overlap the R-xx rule governs |

Comparability requirements (proposal; scoring rules in `spec\scoring.md` were not read for this audit and govern where they differ):

1. Same asof set, same `Decision` schema (`fatpitch.evaluate(asof)`), same scorer, same PIT filter and `unknown` semantics for all three versions.
2. Each version has its own registry file and sha (`registry.yaml`, `registry_article.yaml`, `registry_hybrid.yaml`) and its own prereg entry before any holdout evaluation. Article numbers (58, 5, 50, 45, 0.55, 0.35, 50/30/20, 15%, 2.5×, 20%, 90/60/30 days, 3 insiders / 90 d, ">+30") are tagged `interpreted-from-article` and fixed; interpreted constructions (point maps, strong-regime thresholds, G10, stop/target windows) are fixed before scoring and never tuned on cases.
3. Coverage is reported beside every score: share of cases where the version emits a non-`unknown` decision, split by class and era. V-AF has no rates/FX expressions and no single-name price history before 2021-09; its pre-2021 output is limited to G1 regime and commodity/crypto names, and pre-1997 G1 is partial (HY OAS starts 1997, VIX 1990).
4. Ablations for V-HY: V-HY minus each article block (worldview evidence, convergence family, forensic veto, catalyst gate) to attribute any fidelity change.
5. Display: every V-AF and V-HY output carries the tag mix (count of `stated` / `interpreted` / `interpreted-from-article` rules that fired), so article-origin decisions are never shown as his process.

## 11. Gaps

| Gap | Effect |
|---|---|
| Paywalled internals (G5, G6, G10 criteria, module formulas, gauge point maps, 7 managers, regime-profile multipliers) | Interpreted constructions; V-AF is an article-inspired reconstruction, not a replica. Replication checks (A-37..A-39) measure the gap. |
| Equity bars in amber start 2021-09; S&P 400 PIT membership absent | V-AF single-name results limited to 2021-09→; universe partly survivorship-biased until an IJH N-PORT loader exists |
| Consensus estimates, options history, alt data (AIS, card spend, app data, UCC, Nansen, Stocktwits) not free | 14 modules `unknown` for all history; convergence renormalizes over available modules, which inflates the weight of the remaining ones (reported) |
| LLM layers (Gemini) not point-in-time reproducible | A-178/A-179 display only; never gating in any scored version |
| Article reports no backtest or realized P&L | No external performance anchor for V-AF |
