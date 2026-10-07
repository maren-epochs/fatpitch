# Druckenmiller Fat Pitch Filter — Project Reference

Purpose: reference document for a Claude Code project that builds a multi-asset, Druckenmiller-style "fat pitch" elimination filter. Load this file at project start (place in project root and reference from `CLAUDE.md`, or rename to `CLAUDE.md`).

Environment: Windows 11, PowerShell, Python. IBKR assumed as primary market data source (existing IBKR MCP / ib-async).

Compiled: 2026-10-06.

> **Corrections 2026-10-06** (phase E1; original preserved as `druckenmiller_fatpitch_reference_1.orig.md`; detail and evidence in `spec\reference_corrections.md`). Edits are confined to §2 and §7:
> 1. §2.6 "93% invested → net flat (2019)": the 93% figure is unverified; "over 90% invested … net flat" after the 2019-05-05 tariff tweet is verified (CNBC 2019-06-07 transcript).
> 2. §2.5 "Soros profitable on < 30% of trades": unverified; removed as a fact.
> 3. §2.5 "sizing is 70–80% of the game": his own statement at Sohn 2022, not Mauboussin's account.
> 4. §2.1 / §7.1 inflation rule: the "summarizer error" note was wrong. At Sohn 2022 he stated the fed-funds-above-CPI regularity and expected it could break this cycle; he expected the no-taming-without-recession rule to hold.
> 5. §2.5 sterling sizes vary by telling: $7B fund / $5.5B proposed (Lost Tree); $7.5B fund / ~$7.5B executed (NBIM 2024); $10B (secondary profiles); Soros ~$15B proposed (Feig 2009, NBIM 2024).
> 6. §2.2 / §7.1 horizon widened: 18 months to 3 years (Morgan Stanley 2026), 2–4 year trends (NBIM 2024), alongside 18m (Lost Tree), 18–24m (NBIM 2024), 12–18m (Sohn 2022).
> 7. §2.3 technicals still used for exits ("I'm a technician, so I usually wait for tops", NBIM 2024); ~20% as effective (Morgan Stanley 2026).
> 8. §2.3 the Drelles technical-analysis lesson comes from New Market Wizards, not Lost Tree.
> 9. §7.3 NBIM 2024 now has a full transcript (Podscripts); Sohn 2022, NBIM 2023, Morgan Stanley 2026 and Delivering Alpha 2022 now have near-primary transcripts in the library; ECNY 2020 remains secondary-only.
> 10. Additions from the library: money growth vs industrial production as a stated liquidity rule (Feig 2009); sizing caps (Feig 2009); rates+oil+USD rule cited to Sohn 2022 / NBIM 2024 / Real Vision 2018 (not Delivering Alpha 2022).

---

## Contents

1. Source article analysis (Automated Alpha, "I Built Druckenmiller's Fat Pitch Filter")
2. Druckenmiller criteria — research synthesis from interviews and speeches
3. Translation of criteria into filter components
4. Build plan — multi-asset
5. Gate applicability matrix by asset class
6. Claude Code kickoff prompt
7. Conflicts, assumptions, gaps
8. Next tasks
9. Sources (all links)

---

## 1. Source article analysis

**Source:** Automated Alpha (Jurgis Pocius), "I Built Druckenmiller's Fat Pitch Filter. 923 Stocks Go In. 4 Come Out." Published 2026-03-24. Partially paywalled; the final section ("The Complete Druckenmiller Alpha System") was not accessible. The live dashboard password in the post was valid 24 hours from publication and has expired.

### 1.1 Premise
Druckenmiller's returns came from concentrated bets when macro, sector, technicals, fundamentals and positioning aligned. The author argues the bottleneck is synthesis architecture, not data access. Motivating anecdote: a missed 12% move where all signals existed across separate tools.

### 1.2 System design (as described)
- Universe: 923 assets — 903 equities (S&P 500 + S&P 400), 14 commodities, 6 crypto.
- Nightly run after US close; 10 sequential elimination gates fed by 35 modules; 68 pipeline phases.
- Cascade logic: a name failing a gate is removed and never scored further. Elimination, not ranking.
- Entry point in article: `python -m tools.daily_pipeline`.

| Gate | Function | Stated result (sample night) |
|---|---|---|
| 1 Macro regime | 7 FRED indicators → 5 states (strong_risk_off / risk_off / neutral / risk_on / strong_risk_on) | Neutral, 58/100 |
| 2 Liquidity | Removes thin-volume names | Not quantified |
| 3 Forensics (veto) | Score ≥ 45; accruals, revenue vs cash flow, auditor changes, 10-K delays | −571 |
| 4 Sector rotation | Regime-driven sector tilt | −222 (conflicts with "~546" elsewhere) |
| 5–7 Trend, quality, smart money | Not detailed in free section | 7 remain |
| 8 Convergence | Score > 58 with ≥ 5 modules contributing | 0 pass |
| 9–10 Catalyst, fat-pitch criteria | Not detailed | 0 fat pitches |

### 1.3 Showcase result
- 2026-03-20: four pitches — DVN, EOG, MPC, PSX (energy).
- Sector rotation: energy top at 53.8.
- Energy module: refiners (VLO, PSX, MPC) 69; upstream (DVN, XOM) 56.
- Smart money: options-flow accumulation.
- Catalyst: EIA report two sessions out; consensus build vs weekly data implying draw.
- No realized P&L reported for these pitches.

### 1.4 Weighting
- Five regime-specific weight profiles. Neutral regime: Smart Money and Worldview 9% each; momentum and sentiment 2–3%.
- Nightly Bayesian optimizer adjusts module weights on realized P&L with small moves around a prior.

### 1.5 Stack and data
- 40+ sources; PostgreSQL (117 tables); FastAPI; Next.js; ~47,358 lines.
- LLM: Gemini 2.5 Flash for text classification (foreign-language news in 6 languages, M&A rumor scoring, regulatory events across 9 jurisdictions, news materiality, memo generation). VADER with financial dictionary for 8-K sentiment. Quantitative layers deterministic.
- Data sources: FRED (23 indicators + Economic Heat Index), SEC EDGAR (8-K, Form 4, 13F with 45–135 day lag), EIA, Polymarket, Hyperliquid weekend perps, NOAA, NASA MODIS NDVI, BLS/OSHA/WARN/H-1B, EPA, FCC, USPTO (patent velocity, 20%+ YoY flag), CFTC disaggregated COT.
- Dashboard features: fat pitches with gate attribution; convergence scores for all assets; screener tabs (insider, M&A, energy, blindspots, displacement, pairs, estimate momentum, alt data); module leaderboard (90-day predictiveness); Economic Heat Index (23 FRED indicators); signal conflicts view.

### 1.6 Free manual version (five prompts, paraphrased)
1. Macro regime: 10Y–3M spread, VIX, Chicago Fed NFCI → classify regime; list favored/penalized sectors.
2. Sector filter: two overweight, two underweight sectors; in favored sectors screen 5 names each on ROIC > 15%, Debt/EBITDA < 2.5x, positive 90-day EPS revisions.
3. Smart money + forensics: 13F changes, Form 4 net direction, accrual/auditor/revenue-cash divergence flags.
4. Convergence: put/call and front-two-expiry unusual volume; material news not in price targets; 60-day EPS consensus change.
5. Verdict: 1–2 names with signal count, R:R from support/resistance, catalyst timing, conviction level.

### 1.7 Internal inconsistencies

| Item | Version A | Version B | Check |
|---|---|---|---|
| Gate 4 eliminations | 222 | "about 546" | Corrected 2026-10-06 from the PDF waterfall (run 2026-03-23): G1 916 → G2 915 → G3 344 (−571) → G4 122 (−222). Survivors 122, not 130; universe 916 in the screenshot vs 923 in text. "546" still not reconcilable |
| FFIN stop / R:R | Text: entry $28.95, stop $26.60, 4.6x | Caption: entry $28.95, stop $27.08, 4.9x; dashboard card: entry $28.65, stop $26.60, 4.6x | Corrected 2026-10-06: 4.6x is consistent with the card's entry $28.65 ((38.06 − 28.65)/(28.65 − 26.60) = 4.6x); the text's $28.95 entry is the inconsistency. 4.9x matches stop $27.08 |
| FFIN convergence | 50 (card), 50.3 (dossier) | 46 (caption) | Different snapshots or error; not stated |
| Gates 7–8 | Text: "by Gate 7 seven remain … none clear" Gate 8 | Waterfall: 7 pass G7, 6 pass G8 (CL=F, CTRA, ZC=F, VAL, KLAC, NFG), 0 pass G9 catalyst | Text and screenshot disagree on where the cascade stopped |
| Headline | "4 come out" | Sample night yields 0 | Headline uses the 2026-03-20 outlier |
| Universe hygiene | — | Energy screener lists PXD (Pioneer, acquired by Exxon 2024) | Stale constituents in the article's universe |

### 1.8 Weak points
- No backtest, hit rate, drawdown, out-of-sample period, or post-signal returns.
- Forensic gate removing ~62% of S&P 500/400 is implausibly high; likely missing data scored as fail, or miscalibrated threshold.
- Nightly Bayesian updates on a handful of fat pitches will fit noise; prior strength undisclosed.
- Ten hand-set thresholds with no stated calibration method → overfitting surface.
- Current-constituent universe → survivorship bias in any historical test.
- Claim of reading EIA data "two days before terminals" is unsupported; EIA releases publicly on a fixed schedule.
- Gates 5–10, module definitions and code are paywalled; not replicable from free content.

---

## 2. Druckenmiller criteria — research synthesis

No codified filter has been published by Druckenmiller. Criteria below are compiled from speeches and interviews. As of 2026-10-06 the library (`library\`) holds near-primary transcripts for Lost Tree 2015, Citi/Feig 2009, Delivering Alpha 2014 (interview) and 2022, CNBC 2015-03 and 2016-11, Sohn 2022 (fan transcript), NBIM 2023, NBIM 2024 and Morgan Stanley 2026; ECNY 2020 and Real Vision 2018 rest on secondary verbatim excerpts. Operational rules with citations are in `spec\process.md`.

### 2.1 Macro driver: liquidity and the Fed
- Earnings do not move the overall market; the Federal Reserve and liquidity do. Learned from first mentor Speros Drelles (Lost Tree).
- Stated long-history liquidity rule: "If you have the money supply growing a lot faster than industrial production, the stock market is generally going to go up" (Citi/Feig 2009). "A lot faster" is unquantified.
- Liquidity is net, not gross: in 2020 (Economic Club of New York; secondary, Felder verbatim excerpt) he argued Treasury borrowing would overwhelm Fed purchases and shrink liquidity despite the Fed balance sheet doubling; equity risk/reward among the worst of his career. The call was reversed within weeks (CNBC 2020-06-08 "humbled"; 2020-11-09 not net short).
- Policy error = main opportunity: roughly 80% of his big money came in equity bear markets driven by central bank mistakes (Lost Tree).
- Policy-error test (late 2003): staff estimated the appropriate fed funds rate from economic data alone, ignoring the actual 1%; estimates of 3–6% produced conviction the Fed was too loose.
- Inflation rules (Sohn 2022, conversation with John Collison):
  - No soft landing historically once inflation exceeds 4.5%.
  - Once inflation exceeds 5%, it has not come down without fed funds above CPI — stated as a historical regularity, and in the same conversation he expected this rule could break in the 2022 cycle (fed funds would have needed to exceed ~8%).
  - Once above 5%, never tamed without recession — he expected this rule to hold.
- Cross-asset warning: rates, oil and USD rising together historically precede falling earnings and stocks (Sohn 2022; "three death knells", NBIM 2024; 2000 origin case, Real Vision 2018 and Feig 2009). Not stated in the Delivering Alpha 2022 transcript.

### 2.2 Time horizon
- Never invest in the present; visualize the situation ~18 months ahead (Lost Tree, from Drelles).
- Later framings: 18–24 months (NBIM 2024); 12–18 months (Sohn 2022); "higher in a year or two" (NBIM 2023); trades conceived on 18-month to 3-year horizons (Morgan Stanley 2026); looks for 2–4 year trends (NBIM 2024). Major currency trends last at least two years (Bloomberg 2015; NBIM 2023).
- Change, not level, moves prices.

### 2.3 Market internals and price
- Stock market internals lead economic activity; stocks lead fundamentals by 6–12 months; leading industries (homebuilders, trucking, retail) turning up/down is a signal (Sohn 2022). Momentum tools bottom 12–18 months before fundamentals (Feig 2009). Bond market historically prescient but its signal impaired by central-bank buying (Sohn 2022). Leadership narrowing is a necessary condition for a bear market, "yellow light, not red" (NBIM 2024).
- Focus on factors most correlated with a security's price movement rather than exhaustive fundamentals (New Market Wizards).
- Technical analysis adopted from Drelles and found "very effective" early in career (source: New Market Wizards excerpt; not in the Lost Tree speech).
- Chart as hard entry veto: "if I really like a fundamental thesis and the chart stinks, I won't do it" (Feig 2009). Price vs news as exit tell (Feig 2009).
- Process: build thesis → ~one-third position → wait for price confirmation (Sokoloff / Real Vision 2018).
- Later view: technicals and price-versus-news signals degraded by algorithmic trading (2018) and widespread adoption; "about 20% as effective today" (Morgan Stanley 2026). Still used for exits: "I'm a technician, so I usually wait for tops" (NBIM 2024).
- Contrarianism overrated; the crowd is right ~80% of the time (Feig 2009; Morgan Stanley 2026 transcript).

### 2.4 Excess / fragility indicators (Lost Tree, 2015)

| Indicator | 2006–07 | 2013–14 |
|---|---|---|
| Corporate debt issued | $700B | $1.1T |
| B-rated share of issuance | 28% | 71% |
| Covenant-lite share | < 20% | > 60% |
| Unprofitable IPOs | — | 80% (prior instance at that level: 1999) |

Also: debt-funded buybacks (~$567B) leaving book value flat while debt rose; ~18% of high-yield issuance in energy. Treated as alert signals, not timing triggers — the 2004 warning preceded the bust by about two years.

### 2.5 Concentration and sizing
- One or two opportunities per year are truly exciting; record on those far exceeds the rest; most managers err by spreading across many positions (Lost Tree).
- Soros lesson: what matters is how much is made when right versus lost when wrong, not hit rate. "Sizing is probably 70 or 80% of the equation" — his own statement at Sohn 2022 (fan transcript; Blumenthal notes), not Mauboussin's account (Daily Speculations source dead). The claim that Soros was profitable on < 30% of trades has no support in any source read; unverified.
- Sterling 1992: tellings differ. Lost Tree: $1.5B short of a $7B fund in August; after the Bundesbank signal, proposed $5.5B (100% of fund); Soros argued for 200%. Feig 2009: $1.5B → $5B after Schlesinger's FT comments; Soros pushed ~$15B. NBIM 2024: ~$7.5B fund, $1.5B (~20–25%), then 100%, ~$7.5B executed (names Tietmeyer; Schlesinger is historically correct). Secondary profiles: $10B. More money came from gilts, MATIF and UK equities than from the pound (Feig 2009).
- 1981: 50% of Duquesne capital in 30-year Treasuries at 14%; said he would have used ~150% with Soros's mindset.
- Stated sizing numbers (Feig 2009): gross leverage rarely > 4:1; equities rarely > 100% net long or 50% net short; up to 150–200% of the fund in a currency; up to 300% in 10-year-bond equivalents (the 2000 trade is told as 350% at Sohn 2022 and NBIM 2024); size to market liquidity so exit costs ≤ 1–2% of the fund; bigger when hot / up on the year (house money), small when cold; January 1 resets; never bet big to get even.
- Size scales with payoff asymmetry ("one-way bet"): sterling 50bp downside vs 2,000bp upside (Delivering Alpha 2022); 2-year notes ~10bp vs 150–200bp (CNBC 2019-06-07).
- Prefers a multi-asset menu for concentrated bets, especially assets that rise when equities fall; big bets in liquid (24-hour) markets (Real Vision 2018; NBIM 2024).

### 2.6 Exits, cash, discipline
- No stop losses; exits when the original reason for the position changes.
- Invest then investigate: buy on a strong idea, have analysts verify, exit if thesis fails.
- No pitch, no play: stated at NBIM 2023 (now confirmed in a near-primary transcript: "not to play when you don't see a fat pitch"). In May 2019 moved from "over 90% invested" to net flat after the 2019-05-05 tariff tweet, keeping longs and hedging with other vehicles (CNBC 2019-06-07 transcript); the frequently cited "93%" figure is unverified.
- Reversal on premise break: sold all gold on 2016 election night because "all the reasons I have owned it … may be ending" (CNBC 2016-11-10).
- Biggest mistake: ~$3B lost buying the 2000 tech top after abandoning discipline emotionally.
- Knowing whether one is "hot or cold" is a core job.
- Considers contrarianism overrated.

---

## 3. Criteria → filter components

| Principle | Filter component | Measurable proxy | Basis |
|---|---|---|---|
| Liquidity drives markets | Gate 1 regime | Fed balance sheet − TGA − RRP change; real fed funds | Stated principle; proxy is interpretation |
| Policy-error detection | Gate 1 sub-score | Taylor-rule gap (data-implied rate vs actual) | Interpretation of 2003 exercise |
| Inflation rules | Gate 1 veto | CPI > 5% AND fed funds < CPI → risk-off | Stated |
| Rates + oil + USD rising | Gate 1 flag | 3-month change in 10Y, WTI, DXY all positive | Stated |
| 18–24 month horizon | Signal design | Rate-of-change / revision metrics over levels | Stated principle |
| Internals lead economy | Gate 4 rotation | Leading-industry relative strength turning | Stated; "leading" undefined |
| Price confirmation | Gate 5 trend | Thesis + price confirmation before sizing up | Stated |
| Excess / fragility | Overlay flag | Unprofitable IPO share, B-rated share, cov-lite share | Stated |
| 1–2 pitches per year | Gate 8 threshold | Calibrate pass rate ≈ 1–2 per year per asset class | Interpretation |
| Thesis-break exit | Exit logic | Re-run gates; exit when originating gate fails | Interpretation |
| Bear markets pay most | Short side | Inverted cascade for shorts | Implied by 80% statement |
| Multi-asset menu | Universe | All asset classes, cross-asset ranking | Stated |

---

## 4. Build plan — multi-asset

### 4.1 Universe (v1)

| Asset class | Instruments | Approx count | Price source |
|---|---|---|---|
| Equities | S&P 500 | 500 | IBKR / yfinance fallback |
| Equity indices | ES, NQ, RTY, NKD, FESX + country ETFs | ~15 | IBKR |
| Rates | ZT, ZF, ZN, ZB, Bund, Gilt, JGB | ~8 | IBKR |
| FX | G10 majors + MXN, BRL, ZAR, INR, CNH | ~15 | IBKR |
| Commodities | CL, BZ, NG, RB, HO, GC, SI, HG, PL, ZC, ZS, ZW, KC, SB, CT, LE | ~16 | IBKR |
| Crypto | BTC, ETH, SOL + top 5 by liquidity | ~8 | Exchange APIs (Hyperliquid, Coinbase) |
| Credit | HYG, LQD, EMB (proxies) | 3 | IBKR |

### 4.2 Phases

| Phase | Deliverable | Key rule |
|---|---|---|
| 0 | Project folder, `CLAUDE.md`, `config.yaml` (all thresholds per asset class), `universe.yaml`, Python venv | No hardcoded thresholds |
| 1 | Cached data adapters: IBKR, FRED, EDGAR, CFTC COT, EIA, USDA, crypto exchanges | Every fetch cached and timestamped |
| 2 | Gate 1 regime → asset-class tilt (e.g., risk_off → long duration, USD, gold; short beta). Include net liquidity, Taylor gap, inflation veto, rates/oil/USD flag, excess overlay | Output score + per-indicator attribution |
| 3 | Common module interface `score(instrument, date) → {score, status, reason}` | status ∈ pass / fail / unknown / skip |
| 4 | Gates 2–7 per class, in order: commodities → rates/FX → equities → crypto | Unknown never counts as fail |
| 5 | Convergence: z-score within asset class, then cross-asset ranking | Static weights in v1 |
| 6 | SQLite signal log (date, instrument, entry price, all module scores) + daily HTML report with funnel counts per class | Required before any performance claim |
| 7 | Walk-forward validation per class against 20/60-day forward returns | Adaptive weights only if edge is shown |

Commodities first: COT, EIA and term-structure data are free and structured; no forensic layer required.

---

## 5. Gate applicability matrix

| Gate | Equities | Rates | FX | Commodities | Crypto |
|---|---|---|---|---|---|
| 1 Regime → class tilt | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 Liquidity | ADV | OI / volume | Skip | OI / volume | Volume, depth |
| 3 Quality / veto | Accounting forensics | Skip | Skip | Skip | Exchange / stablecoin risk flags |
| 4 Rotation | Sector tilt | Duration / curve tilt | USD bloc vs carry bloc | Energy / metals / ags tilt | Risk-beta tilt |
| 5 Trend | 200dma, relative strength | Same | Same | Same | Same |
| 6 Fundamental | ROIC, revisions | Real yield, policy path | Rate differential, carry | Term structure, inventories (EIA, USDA) | Funding, basis |
| 7 Positioning | Form 4, 13F | CFTC COT | CFTC COT | CFTC COT (commercials) | Perp funding, OI |
| 8 Convergence | Score > threshold, ≥ N modules | Same | Same | Same | Same |
| 9 Catalyst | Earnings, 8-K | FOMC / CPI calendar | Central bank calendar | EIA / USDA / OPEC calendar | Unlocks, macro calendar |

---

## 6. Claude Code kickoff prompt

```
Build a Python project called fatpitch on Windows: a nightly multi-asset
elimination-cascade filter across equities (S&P 500), equity index futures,
rates futures, G10+EM FX, commodity futures, crypto, and credit ETFs.
Read druckenmiller_fatpitch_reference.md first; it is the specification.

Architecture:
- universe.yaml lists instruments per asset class; config.yaml holds every
  threshold per asset class and the regime->asset-class tilt map. Tag each
  rule in config as "stated" or "interpreted" per section 3 of the reference.
- Common module interface: score(instrument, date) -> {score 0-100,
  status pass/fail/unknown/skip, reason}. "skip" = gate not applicable.
- Adapters: IBKR (prices, futures chains), FRED, SEC EDGAR, CFTC COT
  (disaggregated + financial futures), EIA, USDA, crypto exchange APIs
  (funding, OI, basis).
- Gate 1 must include: net liquidity (Fed balance sheet - TGA - RRP),
  Taylor-rule gap, inflation veto (CPI > 5% and fed funds < CPI),
  rates+oil+USD rising flag, excess overlay.
- Futures: continuous back-adjusted series plus front/second-month spread.
- Convergence: z-score within asset class, then cross-asset ranking.
- Support long and short (inverted cascade).
- Exit logic: re-run gates on open signals; flag exit when originating gate fails.
  No fixed stop-loss logic.
- Unknown data never counts as fail. Cache every API response.
- SQLite signal log with date, instrument, entry price, all module scores.
- Output reports/YYYY-MM-DD.html: funnel counts per class + attribution.
- Entry point: python -m fatpitch.run
- Write CLAUDE.md documenting architecture and conventions.
Build phase by phase; stop after each with test output.
Phase 1: data layer for IBKR futures, FRED, CFTC COT, with tests.
```

---

## 7. Conflicts, assumptions, gaps

### 7.1 Conflicting data
- Horizon: 18 months (Lost Tree) vs 18–24 months (NBIM 2024) vs 12–18 months (Sohn 2022) vs 18 months–3 years (Morgan Stanley 2026), with 2–4 year trends (NBIM 2024). Effective thesis range 18 months–3 years; shorter figures describe the visualization point, not holding period.
- Technicals: core and effective early career (New Market Wizards) vs degraded by algorithms (Real Vision 2018) and ~20% as effective (Morgan Stanley 2026). Still used for exit timing (NBIM 2024). Implies lower timing weight, veto and exit use retained.
- Inflation rule: the earlier note here called the "inflation falls without fed funds exceeding CPI" attribution a likely summarizer error. That was wrong. Two independent summaries (Mutual Fund Observer timestamp list; Blumenthal) and the fan transcript of Sohn 2022 show he stated the historical regularity and expected it could break this cycle, while expecting the no-taming-without-recession rule to hold. Primary audio still not reviewed.
- 2000 Treasury trade: 300% 10-year equivalents (Feig 2009) vs 350% (Sohn 2022, NBIM 2024) vs "two and five-year" Treasuries (Real Vision 2018); Hyman regression −36% (Feig, NBIM 2024) vs −25% (Real Vision) vs −35% (Sohn 2022).
- Sterling 1992 sizes: see §2.5 (fund $7B vs $7.5B; final size $5–5.5B proposed, ~$7.5B executed, or $10B by source).
- Automated Alpha vs Druckenmiller: article uses fixed stops (he rejects stops); 35-module mechanical screen vs his thesis-first, invest-then-investigate process; long-only vs his bear-market-centric returns.

### 7.2 Assumptions
- Fetched article text treated as the complete free portion.
- FFIN discrepancy assumed to come from two snapshots.
- IBKR data subscriptions assumed for CME, CBOT, NYMEX, COMEX, ICE, Eurex; otherwise futures history falls back to delayed/limited sources.
- Crypto outside IBKR via exchange APIs.
- Credit via ETF proxies (cash bond and CDS data not freely available).
- Free FRED API key required.

### 7.3 Gaps
- Few published numeric thresholds: inflation 4.5%/5%, sizing caps (Feig 2009), 1–2 pitches per year, 6–12 / 12–18 month leads, ~20% technical efficacy. All windows and other gate values are interpretation (`spec\registry.yaml`).
- Liquidity definitions: money growth vs industrial production (Feig 2009, stated, unquantified threshold) and Fed purchases vs Treasury issuance (ECNY 2020, secondary only). Fed assets − TGA − RRP is an interpretation.
- Sizing quantified in Feig 2009 (gross ≤ 4:1; equities ≤ 100% net long / 50% net short; FX 150–200%; bonds 300% 10y-eq; exit cost 1–2% of fund; hot/cold); starter ~1/3 (Real Vision 2018) or 20–25% (NBIM 2024 sterling).
- "Leading industries" defined only by examples (homebuilders, trucking, retail, banks, small caps, metals, transports).
- Source status (library, 2026-10-06): NBIM 2024 now has a full transcript (Podscripts ASR). Sohn 2022 (A Letter a Day fan transcript), NBIM 2023 (Tidalwave), Morgan Stanley 2026 (A Letter a Day), Delivering Alpha 2022 (CNBC) and CNBC 2015/2016/2019 transcripts are near-primary. ECNY 2020 remains secondary-only (Medium transcript 403; no ECNY transcript located). Real Vision 2018 rests on verbatim notes, no transcript. New Market Wizards read only via excerpts.
- Unverified claims: "93%" (2019; ">90%" verified); Soros < 30% hit rate; 2013 short yen (not in library).
- No free cross-asset options flow source; IBKR chains give OI/volume, not trade-level flow.
- COT is weekly (Tuesday positions, Friday release); positioning gate is slow.
- Automated Alpha gates 5–10 and code paywalled.

---

## 8. Next tasks

1. Draft `config.yaml` and `universe.yaml` with stated rules (inflation veto, rates/oil/USD flag, net-liquidity formula, excess overlay) tagged stated vs interpreted.
2. Verify secondary-sourced claims against primary NBIM (2023, 2024) and ECNY 2020 recordings, especially the inflation-rule wording and market-internals statements.
3. Backtest stated macro rules (fed funds < CPI with CPI > 5%; rates+oil+DXY all rising; Taylor gap) against 6- and 12-month S&P forward returns, 1970–present.
4. Measure DVN, EOG, MPC, PSX from 2026-03-20 vs XLE and SPY at 5/20/60 days to test the article's only implied performance claim.
5. Audit IBKR futures data subscriptions via the existing IBKR MCP.
6. Decide whether the filter lives inside the Amber terminal as a module or standalone (shared data layer and database choice).

---

## 9. Sources (all links)

### Source article
- Automated Alpha — I Built Druckenmiller's Fat Pitch Filter: https://automatedalpha.substack.com/p/i-built-druckenmillers-fat-pitch
- Shared link variant: https://automatedalpha.substack.com/p/i-built-druckenmillers-fat-pitch?r=6efi&utm_medium=ios
- Live dashboard (password expired; paid only): https://druckenmiller-alpha.vercel.app

### Primary / near-primary
- Lost Tree Club transcript, text (gist): https://gist.github.com/timhwang21/e6a2b24e064182dd9099ad00e4f4f9a6
- Lost Tree Club original PDF (Cove Street Capital; referenced in gist): http://covestreetcapital.com/Blog/wp-content/uploads/2015/03/Druckenmiller-_Speech.pdf
- NBIM In Good Company podcast, Nov 2024 (Apple): https://podcasts.apple.com/no/podcast/stan-druckenmiller-inside-the-mind-of-a-legendary-investor/id1614211565?i=1000675883446
- NBIM podcast transcript (Podscripts): https://podscripts.co/podcasts/in-good-company-with-nicolai-tangen/stan-druckenmiller-inside-the-mind-of-a-legendary-investor
- NBIM podcast (Podwise summary): https://podwise.ai/episodes/2262853
- NBIM podcast highlights (Player FM): https://sv.player.fm/series/series-3330248/highlights-stan-druckenmiller
- NBIM podcast video mirror: https://wkt-1-d85j.onrender.com/wkt/watch/-5Weeox0Xus
- NBIM podcast page: https://www.nbim.no/en/publications/podcast/
- Sokoloff / Real Vision interview (YouTube): https://www.youtube.com/watch?v=G-MlrpoMig0
- June 2022 long-form interview (YouTube): https://www.youtube.com/watch?v=-7sWLIybWnQ
- Bloomberg 2019 — net flat after tariff tweet: https://www.bloomberg.com/news/articles/2019-06-03/druckenmiller-piles-into-treasuries-on-possible-fed-rate-drop
- CNBC 2022 — hard landing view: https://www.cnbc.com/2022/09/28/stanley-druckenmiller-sees-hard-landing-in-2023-with-a-possible-deeper-recession-than-many-expect.html
- CNBC 2020 — rotation, not net short: https://www.cnbc.com/2020/11/09/stanley-druckenmiller-says-he-wouldnt-want-to-be-short-market-sees-stock-rotation-continuing.html

### Secondary summaries and analysis
- Felder Report — ECNY 2020 liquidity: https://thefelderreport.com/2020/05/27/why-brrr-doesnt-mean-what-you-think-it-means
- Felder Report (alt URL): https://thefelderreport.com/?p=51626
- Felder Report — earnings vs Fed: https://thefelderreport.com/?p=30214
- Hedgeye — Felder guest commentary: https://app.hedgeye.com/insights/84926-why-money-printer-go-brrr-doesn-t-mean-what-you-think-it-means
- Hedgeye print version: https://app.hedgeye.com/insights/84926-why-money-printer-go-brrr-doesn-t-mean-what-you-think-it-means/print
- Mutual Fund Observer — June 2022 interview notes: https://mutualfundobserver.com/discuss/showthread.php?tid=51737
- Mutual Fund Observer (alt URL): https://www.mutualfundobserver.com/discuss/showthread.php?tid=51737
- Hedge Fund Alpha — On My Radar 2022: https://hedgefundalpha.com/?p=2149781
- Hedge Fund Alpha — On My Radar: https://hedgefundalpha.com/strategies/on-my-radar-stanley-druckenmiller/
- Actionable News — 18–24 month horizon: https://actionablenews.substack.com/p/aia-october-2024
- Actionable News — NBIM 2024 note: https://actionablenews.substack.com/p/free-weekly-email-111224
- Hedge Fund Alpha — New Market Wizards excerpt: https://hedgefundalpha.com/stocks/stanley-druckenmiller-focus-on-what-makes-a-stock-go-up-or-down/
- Hedge Fund Alpha — Real Vision notes: https://hedgefundalpha.com/strategies/my-notes-on-the-druckenmiller-real-vision-interview/
- Hedge Fund Alpha — Buy first, analyze later: https://hedgefundalpha.com/strategies/stanley-druckenmiller-buy-first-analyze-later/
- Hedge Fund Alpha — "I was a pig": https://hedgefundalpha.com/strategies/stanley-druckenmiller-bulls-make-money-bears-make-money-and-pigs-get-slaughtered-im-here-to-tell-you-i-was-a-pig/
- Hedge Fund Alpha — global liquidity: https://hedgefundalpha.com/strategies/just-under-22-trillion-sits-on-the-cumulative-central-bank-balance-sheet-of-the-big-six/
- Hedge Fund Alpha — 1988 Barron's interview: https://hedgefundalpha.com/interview-stan-druckenmiller/
- Investing by the Books — Sokoloff interview timestamps: https://www.investingbythebooks.com/columns/2018/12/3/stanley-druckenmiller
- Magica — interview summary: https://magica.com/youtube-summarizer/stan-druckenmiller-shares-hard-lessons-and-investment-insights-from-a-legendary-career-z_pk4eBDaLA
- Delphi Digital — NBIM 2023 TLDR: https://members.delphidigital.io/feed/druck-interview-tldr
- Validea — stop losses, dot-com mistake: https://blog.validea.com/?p=28196
- Validea (alt URL): https://blog.validea.com/stanley-druckenmiller-insights-on-the-market-and-its-greatest-investors/
- Validea — Lost Tree coverage: https://blog.validea.com/druckenmiller-says-very-unhappy-ending-may-await-investors/
- Daily Speculations — Mauboussin on sizing: https://dailyspeculations.com/wordpress/?p=13988
- Daily Speculations — Lost Tree discussion: https://dailyspeculations.com/wordpress/?p=10192
- CardPlayer — Soros lesson: https://www.cardplayer.com/?p=1027762
- Nasdaq — liquidity quote context: https://www.nasdaq.com/articles/how-do-stocks-react-rate-cuts
- Advisor Perspectives — 2017 commentary: https://www.advisorperspectives.com/commentaries/2017/12/04/on-my-radar-it-feels-like-1999-all-over-again
- Advisor Perspectives — Lost Tree speech: https://www.advisorperspectives.com/commentaries/2015/04/20/on-my-radar-the-speech-at-lost-tree-club
- FXStreet — 2015 commentary: https://www.fxstreet.com/analysis/thoughts-from-the-frontline/2015/05/21
- Benzinga — Lost Tree coverage: https://www.benzinga.com/analyst-ratings/analyst-color/15/04/5403650/druckenmiller-joins-fed-bashers-this-will-end-badly
- Arya Deniz Substack — Lost Tree lecture: https://aryadeniz.substack.com/p/stanley-druckenmillers-lost-tree
- The Idea Farm — Lost Tree speech: https://theideafarm.com/miscellaneous/speech-at-lost-tree-club/
- Mauldin Economics — Lost Tree (paywalled): https://www.mauldineconomics.com/overmyshoulder/article/stanley-druckenmiller-at-the-lost-tree-club
- Business Insider India — quotes: https://www.businessinsider.in/miscellaneous/slidelist/68189821.cms
- Ugebrev (Danish) — Lost Tree excerpts: https://ugebrev.dk/?p=11467
- BNN Bloomberg — 2020 risk/reward: https://www.bnnbloomberg.ca/druckenmiller-says-risk-reward-in-stocks-is-worst-he-s-ever-seen-1.1435356
- BNN Bloomberg — NBIM podcast context: https://bnnbloomberg.ca/investing/2024/12/20/ceo-of-norways-18-trillion-fund-reveals-perks-of-podcast-gig
- Duke — NBIM interview summary: https://sites.duke.edu/tech/?p=95
- MOI Global — Latticework profile: https://moiglobal.com/latticework-stanley-druckenmiller-202503
- Motley Fool — profile: https://www.fool.com/investing/how-to-invest/famous-investors/stanley-druckenmiller
- LongPort — Morgan Stanley interview coverage: https://longportapp.cn/news/277289579
- TraderLion — quotes: https://traderlion.com/quotes/druckenmiller-quotes/
- DayTrading.com — strategy profile: https://daytrading.com/stanley-druckenmiller
- FinMasters — strategy profile: https://finmasters.com/?p=150923
- Hustle Fund — profile: https://www.hustlefund.vc/post/angel-squad-stanley-druckenmiller-investments-the-macro-master-who-generated-30-annual-returns-without-a-single-down-year
- Hustle Fund (alt URL): https://www2.hustlefund.vc/post/angel-squad-stanley-druckenmiller-investments-the-macro-master-who-generated-30-annual-returns-without-a-single-down-year
- SimpleFunctions — sterling trade analysis: https://simplefunctions.dev/opinions/soros-pound-theo-trump-conviction-macro-prediction-markets
- Bilanz — 2025 Q4 rotation positions: https://www.bilanz.ch/invest/marktrotation-value-aktien-und-kleine-titel-im-fokus/nr85l42
- GuruFocus — 2020 Q2 positioning: https://www.gurufocus.com/news/1212234
- Against All Odds Research — dot-com mistake: https://aaoresearch.substack.com/p/fear-of-missing-out-cost-him-3-billion
- Zacks — rotation commentary: https://www.zacks.com/commentary/2300264/is-thursdays-market-rotation-here-to-stay

### Retrieved but not relevant (listed for completeness)
- Reading Price Charts Bar by Bar (Al Brooks), Ellibs: https://www.ellibs.com/book/9780470464236/reading-price-charts-bar-by-bar-the-technical-analysis-of-price-action-for-the-serious-trader
- Same title, Yukon Libraries: https://search.yukonlibraries.ca/Hoopla/17392955
- Same title, Osiander: https://www.osiander.de/shop/home/artikeldetails/A1033200201
- TradingView — technical analysis critique: https://it.tradingview.com/chart/UNH/mkIEQpgh-The-Ugly-Truth-of-Technical-Analysis
- Zacks (malformed URL variant): https://www.zacks.com/commentary/2300264/{https:/www.zackstrade.com/2019-1-dollar}

### Data source registration
- FRED API key: https://fred.stlouisfed.org
