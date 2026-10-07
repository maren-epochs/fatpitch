# Article provenance: where the Automated Alpha filter's non-Druckenmiller elements come from

Date: 2026-10-07. Subject: "I Built Druckenmiller's Fat Pitch Filter. 923 Stocks Go In. 4 Come Out." (Jurgis Pocius, Automated Alpha, 2026-03-24; PDF `library/source_article/automated-alpha-fat-pitch-filter-2026-03-24.pdf`). Element ids `A-xx` follow `spec/article_coverage.md`.

Question: why does the article contain filters, modules and requirements absent from the Druckenmiller record? Hypotheses tested per element:

| Code | Hypothesis |
|---|---|
| (a) | Author added it from his own house framework or from other published frameworks |
| (b) | Druckenmiller discussed it and the library missed it |
| (c) | Duquesne did it, but he rarely spoke about it |
| (d) | Table-stakes practice too obvious for him to mention in an interview |

Markers: **[D]** documented (source read, quoted or cited); **[I]** inference.

## 1. Bottom line

1. **(a) dominates.** [D] Most non-Druckenmiller modules appear in the author's earlier posts, before 2026-03-24 and unrelated to Druckenmiller: options-flow thresholds, insider cluster buys, patent velocity "20%+ YoY", ROIC and Debt/EBITDA, multi-source convergence gates, stop/target brackets, and the "manual version" prompt template. He also packages forensic accounting, insider-transaction scoring and macro regime as reusable "universal" Claude Code skills. The Druckenmiller label sits on top of a generic house stack that has been re-badged for several investors (Buffett/Munger, Paulson, Dalio, PTJ).
2. **(b) is small.** [D] The extended search found stock-level Druckenmiller statements not yet in the spec's citations: the "triple screen" with the Toggle AI screener (Hustle 2021), "never buy something that doesn't have a great chart and fundamentals", "I completely endorse analysis of fundamentals", the 1987 S&P-futures speculator-positioning study (NMW), and breadth narrowness as a 1987 sell input. None of these supports the article's specific thresholds or modules. One new source, the GE purchase amid fraud allegations (CNBC 2019-08-15), contradicts the forensic veto.
3. **(c) cannot be tested well.** [D] Druckenmiller "never spoke publicly while actively managing money" (A Letter a Day intro, Feig transcript). In his own words: "I'm a private person, as you know if you try and find anything out on Duquesne" (Feig 2009). No former employee describes Duquesne's stock-screening mechanics. Bessent, Cummins and others were searched; nothing found.
4. **(d) is real but narrow.** Liquidity limits, catalyst calendars, earnings-expectation work, basic fundamental diligence, crowding awareness and risk limits are standard. Duquesne evidence exists for most of them, mostly indirect. The article does not implement them as hygiene. It implements them as alpha gates with aggressive thresholds. Gate 3 alone removes 571 of 915 names (62%), which is not hygiene by any standard.
5. **Explicit conflicts** [D]: price stops and R:R brackets (A-129..A-132), nightly Bayesian re-weighting, the contrarian or "smart money" reading of positioning, the hard forensic veto, and static quality thresholds. Sources: "never used a stop loss", "we don't have models", "never had a fancy quantitative risk management control system", the Teva 6× P/E rerating, "underearning", GE 2019.

## 2. Author and outlet

| Item | Finding | Marker / source |
|---|---|---|
| Author | Jurgis Pocius. LinkedIn: "AI + DeFi consultant at Evoa"; consulting clients cited include Nike, HBS, Lacoste, McKinsey and BCG. No disclosed portfolio-management or buy-side track record. Contact jurgis@evoaai.com | [D] https://www.linkedin.com/in/jurgis-pocius/ (search snippet); [D] macro post footer |
| Output cadence | 23 posts 2026-01-30 → 2026-09-29, mostly "I built X" / "I reverse-engineered X" systems | [D] Substack archive API `https://automatedalpha.substack.com/api/v1/archive?sort=new` |
| Build method | Claude Code (subtitle "How I + Claude Code automated…"), plus Google Antigravity and Codex in other posts. "58.4 Billion AI Tokens Later … Lessons from 172 builds with Claude Code and Codex" (2026-09-13) | [D] post subtitles |
| Commercial model | Paid Substack tier gates code and dashboards (dashboard open 24 h with a password, then paid only). Consulting pitch: "If you want help building or adapting systems like this for your own fund … reach out" | [D] article p.2; macro post 2026-04-02 |
| Disclosed Druckenmiller sources | None. No quotes, interviews or books cited. Compare the Buffett/Munger post (2026-04-13), which names the Berkshire letters, Poor Charlie's Almanack and Cunningham | [D] full free text of both posts |
| Post-hoc changes | The post's `updated_at` is 2026-09-25, six months after publication and four days before the follow-up. The follow-up (2026-09-29) calls it "Druckenmiller-inspired". The library PDF may not match the current web version | [D] Substack post API metadata |
| Pre-existing picks | DVN and EOG were already in the author's generic "Alpha Terminal" scan on 2026-02-21 ("24% below Morningstar FV", "19% below FV"), a month before the "fat pitch" night of 2026-03-20 | [D] https://automatedalpha.substack.com/p/alpha-terminal-daily-stock-signals |
| Performance claim | Follow-up: the four energy picks +25.3% (2026-03-25 → 09-25) vs SPY +7.3 pp; MPC +64.2%, PSX +42.9%, DVN −5.4%, EOG −0.5%; "gross of costs, not risk-adjusted" | [D] https://automatedalpha.substack.com/p/i-built-a-druckenmiller-inspired |

### 2.1 House-framework recurrence (evidence for (a))

| Article element | Earlier or parallel appearance in the author's non-Druckenmiller posts | Source |
|---|---|---|
| Opening "While everyone argues about which chatbot is marginally smarter, the real edge is in pipelines" and Before/After block (6–8 hours, "$24k/year Bloomberg seat", "$0 marginal cost per run") | Verbatim in the macro post | [D] https://automatedalpha.substack.com/p/i-replaced-a-250000year-macro-strategist (2026-04-02) |
| Options flow: put/call, unusual volume | "Put/Call ratio below 0.7 = bullish flow, above 1.3 = bearish"; unusual = "volume is 5x+ the open interest" | [D] https://automatedalpha.substack.com/p/i-built-a-200000year-equity-research (2026-02-20) |
| Insider cluster buys (Form 4) | "Insider cluster buys detected"; "for mid-caps, 3+ insider cluster buys above…" | [D] same, 2026-02-20 |
| Patent velocity "20%+ YoY growth = innovation acceleration" (A-91) | "500+ patents with 20%+ YoY growth = strong innovation moat" (EPO API) | [D] same, 2026-02-20 |
| ROIC and Debt/EBITDA quality screen | "ROIC (calculated from EBIT × (1 − tax rate) ÷ invested capital), and Debt/EBITDA"; ML on "net income margin, FCF margin, revenue growth, debt/EBITDA, ROIC" | [D] same, 2026-02-20 |
| Convergence and quality gates | "Every opportunity filtered through three quality gates: multi-source confirmation, identifiable catalyst, and quantifiable edge" | [D] same, 2026-02-20 |
| Five-step manual prompts ending "Conviction level: HIGH / MODERATE / LOW / AVOID" | Same template and wording ("Check the alt-data signals … (1) Options flow, is put/call ratio bullish or bearish? Any unusual volume? (2) Insider transactions…") | [D] same, 2026-02-20 |
| Forensic veto (accruals, auditor changes, going concern) | Claude Code "universal" skill: "accrual quality first, cash conversion consistency second, auditor changes third, going concern…". Six skill files offered: "forensic accounting, DCF, earnings NLP, SEC filing conventions, insider transaction scoring, and macro regime" | [D] https://automatedalpha.substack.com/p/how-to-separate-yourself-from-the (2026-04-07) |
| Forensic method origin | Later stand-alone forensic product explicitly applies "Richard Sloan's 1996 accruals research" and a cash-conversion threshold of 0.60 | [D] https://automatedalpha.substack.com/p/i-built-an-ai-forensic-accountant (2026-09-20) |
| Stops, targets, R:R | "greenlights the position with sizing and stop-loss" (2026-02-20). The PTJ system has "trigger, stop, target, and reward:risk bracket" (2026-08-04) | [D] posts cited |
| Regime classifier → risk-on/off labels; self-scoring and calibration | Macro Command Center: regimes "Risk-On, Risk-Off, Transitional"; models "dynamically calibrate" via Brier score | [D] macro post 2026-04-02 |
| Article's own framing of the checklist | "Every serious investor knows the checklist: macro regime … options flow, accounting forensics, alternative data" | [D] article p.4 |

[I] The article's own words describe the 10-item checklist as generic ("every serious investor knows"), not as Druckenmiller's. The Druckenmiller-specific content is the top-down order, waiting for alignment, cash when nothing aligns, and concentration. The rest is the author's reusable stack.

## 3. Element-by-element origin of the non-Druckenmiller items

| Element (A-ids) | Likely origin: named frameworks | Citations |
|---|---|---|
| Forensic veto ≥ 45: accruals, revenue vs cash flow, GAAP-masked balance-sheet deterioration, auditor changes, 10-K delays (A-21..A-26) | Sloan accrual anomaly; Beneish M-score (DSRI, accruals, etc.); commercial accounting-risk scores. MSCI ESG AGR is built on "revenue and expense recognition and asset-liability valuation" plus "officer changes, late or amended filings", which closely matches the article's list. Regulatory hooks: 8-K Item 4.01 (auditor change), Form 12b-25 / NT 10-K (late filing). Author's own Sloan-based skill (above) | Sloan (1996) Accounting Review 71(3) https://www.jstor.org/stable/248290 ; Beneish (1999) FAJ https://doi.org/10.2469/faj.v55.n5.2296 ; MSCI AGR https://www.msci.com/documents/1296102/1636401/MSCI-ESG-AGR.pdf |
| ROIC > 15% & Debt/EBITDA < 2.5× (A-31) | Greenblatt "magic formula" (return on capital); quality-factor literature (Piotroski F, Novy-Marx profitability, AQR Quality-Minus-Junk). 2.5× is a common leverage covenant and rating heuristic. [I] The specific pair is the author's (2026-02-20 post) | Piotroski (2000) JAR https://doi.org/10.2307/2672906 ; Asness, Frazzini, Pedersen QMJ https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2312432 ; https://www.magicformulainvesting.com |
| EPS revision momentum (A-69, A-76) | Earnings-momentum literature; commercial revision ranks (StarMine ARM, Zacks Rank); O'Neil CANSLIM "C/A" earnings acceleration | Chan, Jegadeesh, Lakonishok (1996) JF https://doi.org/10.1111/j.1540-6261.1996.tb05222.x ; StarMine ARM https://www.lseg.com/en/data-analytics/financial-data/analytics/quantitative-analytics/starmine-analyst-revisions-models |
| 13F "smart money" of 7 tracked managers (A-61, A-65) | 13F cloning and guru tracking (Dataroma, WhaleWisdom, GuruFocus, Goldman Sachs Hedge Fund VIP basket); "best ideas" literature. [D] Duquesne is itself a standard 13F-cloning target (library RS/2020-08-18, RS/2026-02-26) | Cohen, Polk, Silli "Best Ideas" https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1364827 ; GS VIP coverage https://www.cnbc.com/2018/08/21/goldman-here-are-the-10-stocks-most-loved-by-hedge-funds.html ; https://www.dataroma.com ; https://whalewisdom.com |
| Form 4 insider clusters, "INSIDER_CLUSTER 100", ≥ 3 insiders in 90 d (A-123, A-124) | Insider-trading literature; OpenInsider "cluster buys" screen; author's 2026-02-20 module | Lakonishok & Lee (2001) RFS https://doi.org/10.1093/rfs/14.1.79 ; Cohen, Malloy, Pomorski (2012) JF https://doi.org/10.1111/j.1540-6261.2012.01740.x ; http://openinsider.com/latest-cluster-buys |
| Options flow: put/call, unusual volume, delta-adjusted flow, gamma (A-67, A-75) | Option-volume information literature; retail "unusual options activity" services (volume/OI ratio is the standard Barchart-style definition); author's 0.7/1.3 and 5× OI rules | Pan & Poteshman (2006) RFS https://doi.org/10.1093/rfs/hhj024 ; https://www.barchart.com/options/unusual-activity |
| COT commercial hedgers as "smart money" (Energy Intel, A-74) | Practitioner COT lore (Briese, *The Commitments of Traders Bible*, Wiley 2008; L. Williams). CFTC disaggregated report | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm |
| 35 alt-data modules: H-1B, WARN, OSHA, USPTO, AIS ship tracking, NDVI, Polymarket, Reddit, UCC-1, board interlocks, AAR rail, on-chain (A-78..A-95) | Alternative-data vendor categories (labor, patents, satellite and agri, shipping, prediction markets, social sentiment, credit filings, governance networks). Patent velocity: innovation-efficiency literature. [I] Module list reflects free-API availability (the article's stated design goal: "mostly free public APIs") rather than a strategy | Hirshleifer, Hsu, Li (2013) JFE https://doi.org/10.1016/j.jfineco.2012.09.011 ; library `research/data_practices.md` §6 |
| Regime classifier: 7 FRED components incl. VIX; breadth panel (% > 200dma, A/D, NH/NL) (A-10..A-18, A-137) | Generic risk-on/risk-off dashboards; Zweig breadth thrust (Zweig, *Winning on Wall Street*, 1986); VIX contango rules from volatility-trading practice. Author's Macro Command Center regime engine (2026-04-02) | macro post cited above |
| Worldview theses table, 12 level-triggered theses (A-46..A-60) | [I] Author's own sector-tilt map with Druckenmiller-style labels; tilt weights +0.55/±0.35 and the 50/30/20 blend are undisclosed constructions; Gemini writes the "Druckenmiller-style narrative" (A-60) | article p.22 |
| Regime-adaptive weights; nightly Bayesian updates from realized P&L (A-40..A-45) | Generic quant practice (regime-conditional factor weights; online and Bayesian model averaging). Author's recurring "self-scoring" motif (Brier ledger in the macro post) | macro post cited above |
| Price stop / target / R:R from support and resistance (A-129..A-132) | Trading-education conventions (R-multiples, Van Tharp; fixed-percent stops, O'Neil). Author's PTJ "entry bracket" | PTJ post https://automatedalpha.substack.com/p/i-built-a-paul-tudor-jonesinspired |
| Convergence > 58 with ≥ 5 modules (A-33, A-118) | Generic multi-factor composite with a breadth-of-agreement count; author's "multi-source confirmation" gate (2026-02-20) | posts cited |

## 4. What Druckenmiller actually said on these topics (search beyond prior citations)

| Topic | Statement (date, venue) | Marker / source | Bearing |
|---|---|---|---|
| What moves a stock | Research director: "This is useless. What makes the stock go up and down?" → "Very often the key factor is related to earnings … Chemical stocks … the key factor seems to be capacity" (NMW, interview Dec 1991) | [D] archive.org OCR, `DS/1992-XX-XX_new-market-wizards-full-chapter-text.md` | Earnings matter, but the driver is stock-specific. This argues against a uniform revision-momentum factor |
| Fundamentals | "I completely endorse analysis of fundamentals. Looking at the balance sheet, trying to figure out a couple years from now, what people are going to think about this company or are the earnings going to be different." "I'm never going to buy something that doesn't have a great chart and fundamentals." (Hustle Q&A, 2021-05-11) | [D] https://thehustle.co/stanley-druckenmiller-q-and-a-trung-phanin | Supports a fundamental-diligence step, meaning forward change versus perception. It does not support static ROIC or leverage thresholds |
| Screening tools | "I have a triple screen to buy, hold or sell a security" (fundamental, technical, Toggle). "I might get a notice one day from Toggle that XYZ looks good. Then I can do my fundamentals. Then I can look at the chart." Earlier: "I used Ned Davis [Research] and other technical services." (Hustle 2021) Caveat: Toggle is a Druckenmiller portfolio company and arranged the interview | [D] same | (b)-type support for machine screening as idea generation (not as a gate) and for vendor technical/breadth services |
| Earnings expectations | "What a company's been earning doesn't mean anything. What you have to look at is what people think it's going to earn." (TheStreet 2024-11-21; original venue not identified). Q4 2000: Hyman model earnings −35% vs consensus +18% → 2-year notes (Sohn 2022; Feig 2009) | [D] secondary; library DS/2022-06-XX, DS/2009 | Supports expected change vs consensus (variant perception, A-63), not backward revision momentum |
| Analysts' role | "I've got to have an expert at Duquesne who is, and trust his judgment … when they're really enthusiastic, that's as important to me as the actual facts" (Morgan Stanley, rec. 2026-01-30). "Invest, then investigate" (NBIM 2023; Sohn 2022) | [D] https://aletteraday.substack.com/p/letter-320-stan-druckenmiller-and | The analyst layer is human judgment after entry, not pre-entry screens |
| Models | "We don't have models, we don't have any of that stuff. We do use macro data for entries and exits" (MS 2026). "I have never had a fancy quantitative risk management control system" — one was imposed by banks after 1998 and he "didn't pay attention to it" (Feig 2009) | [D] letters 320 and 300, A Letter a Day | Conflicts with nightly Bayesian re-weighting and with a 35-module scoring engine as the decision maker |
| Information speed | "If you … analyze a company for four months, and you're not willing to operate with 15-20% of information, you'll often miss a big move" (MS 2026) | [D] letter 320 | Conflicts with cascade logic that blocks entry until ≥ 5 modules agree |
| Information sources | Offered a menu that included "positioning data", he chose market internals and companies: "all my macro is not from macro data, it's from companies … hearing their tones … put the mosaic together" (MS 2026) | [D] letter 320 | Human company-contact mosaic, not alt-data feeds. Positioning was not chosen |
| Accounting and fraud | Steinhoff: "I was lucky enough to … short the stock because someone was kind enough to explain to me that these guys might be crooks" (CNBC 2017-12-12) | [D] https://www.cnbc.com/2017/12/12/cnbc-exclusive-cnbc-transcript-stanley-druckenmiller-speaks-with-cnbcs-kelly-evans-today.html | Accounting concern used as a short thesis via a tip, not as a veto |
| Accounting and fraud | GE: "I believe Culp ... I bought stock today", on the day of Markopolos's "Enron-like fraud" report (2019-08-15) | [D] new note `DS/2019-08-15_cnbc-statement-bought-ge-amid-markopolos-fraud-claims.md` | **Contradicts** a hard forensic veto: he bought into an accounting allegation |
| Quality | Teva bought at 6× earnings while "value investors … were actually selling it"; rerated to 11.5–12× (MS 2026). Prefers "underearning" companies; Apple "probably overearning" (CNBC 2017) | [D] letter 320; CNBC 2017 | Conflicts with a static ROIC > 15% gate. He targets changes in earnings power, often in low-return names. [I] Teva carried heavy acquisition debt; a pass on < 2.5× Debt/EBITDA was not verified |
| Stops | "I have never used a stop loss in my career" (Feig 2009); "the dumbest concept I've ever heard" (Hustle 2021) | [D] | **Contradicts** A-130..A-132 |
| Crowding and contrarianism | "contrarianism is overrated … I don't care if a trade is crowded if I think the thesis is right and the trend is with me. For entry points, I care" (MS 2026); "the crowd makes money 80% of the time" (Feig 2009) | [D] | Positioning affects entry timing only. It conflicts with contrarian COT and smart-money gating used as alpha |
| Positioning (support) | 1987: a study found S&P-futures speculators "had been consistently short until July 1987 and after that point had switched to an increasingly heavy long position", used to support the crash thesis. Jan 1991: "eight out of the eight … money managers … holding their highest cash position in ten years … everyone had already sold" → turned bullish (NMW) | [D] archive.org OCR NMW (not in prior library summary) | (b): positioning and sentiment were used as fragility or confirmation inputs in specific trades. Not the commercial-hedger "smart money" construct |
| Breadth | 1987 bear call: "my technical analysis showed that the breadth wasn't there … strength … concentrated in the high capitalization stocks" (NMW). Breadth/volume thrust (Bloomberg 2015) | [D] NMW OCR; DS/2015-04-15 | Supports the breadth panel (A-137); already in R-15/R-60 |
| Options | Gold "through options, because if it goes it'll go hard" (Grant's 2012). 13F coverage reports IWM and SPY call positions (quarter not pinned in this session) | [D] DS/2012-04-XX; [D, secondary] https://benzinga.com/markets/hedge-funds/25/08/47177810/legendary-investor-stanley-druckenmiller-made-huge-ai-and-chipmaker-bets-in-q2-heres-what-he-knows-that-you-don-t ; options listing https://www.insiderset.com/investor/stanley-druckenmiller-duquesne-family-office/options/q4-2025 | Options as a convex instrument. No evidence of options flow as a signal |
| Liquidity of the instrument | Size "relative to the market … never get so big … I couldn't get out" (Feig 2009); bought "the five most liquid Argentine ADRs" after Milei's Davos speech (CNBC 2024-05-07) | [D] | Supports G2 (already R-33). Liquidity was the selection criterion in a fast trade |
| VIX and sentiment gauges | No Druckenmiller statement on VIX, put/call or survey sentiment located | [D] gap (extended searches, 2026-10-07) | Unknown; no support |
| 13F cloning and insider buying | No statement located on using other managers' 13Fs or insider buying as signals | [D] gap | Unknown; no support |
| Alt data (satellite, H-1B, WARN, patents, ship tracking) | No statement located. The closest are Toggle (above) and AI used to find ADRs (2024) | [D] gap | Unknown; no support |
| Duquesne operations | "He never spoke publicly while actively managing money" (A Letter a Day intro); "I'm a private person, as you know if you try and find anything out on Duquesne" (Feig 2009). At Soros, the equity team was used "more for insights they could provide his macro bets than their own stock picking P&L" (Rupak Ghose, 2026-04-21, commentary, uncited) | [D] letter 300; https://rupakghose.substack.com/p/druckenmiller | (c) is structurally hard to test. Weak secondary support that Quantum's equity analysts fed macro theses rather than running screens |

## 5. Hypothesis (d): too-obvious standard practice

How to tell "too obvious to mention" apart from "not part of his process":

| Test | Reads as "too obvious" (d) | Reads as "not his process" |
|---|---|---|
| T1 Conflict test | No statement contradicts it | He contradicts it in words or a documented trade (stops, GE vs veto, Teva vs ROIC) |
| T2 Hygiene vs alpha | Used as a low-cutoff exclusion that removes a few percent of names | Used as a scored alpha source or an aggressive gate (Gate 3 removed 62%) |
| T3 Indirect trace | Implied by something he does describe (liquidity sizing → ADV screen; analysts → fundamentals; catalyst → calendar) | No adjacent trace at all (VIX, alt data, cloning) |
| T4 Industry baseline | Universal at macro and equity hedge funds (risk limits, liquidity, compliance, earnings calendars) | Niche or vendor-marketed (options flow, Reddit, UCC filings, board interlocks) |
| T5 Style fit | Fits a discretionary concentrated macro/equity book | Fits a diversified systematic multi-factor book |

Standard-practice evidence:

| Practice | Evidence it is standard | Duquesne/Druckenmiller trace |
|---|---|---|
| Liquidity/ADV limits | Universal; Form PF requires portfolio-liquidity reporting by private-fund advisers [I: general regulatory knowledge] | [D] Feig 2009 sizing rule; Argentine ADR selection by liquidity |
| Avoiding accounting frauds | Commercial products sold to institutions (MSCI AGR "designed to help institutional investors … manage accounting risk"; Forensic Alpha Model) | [D] Steinhoff (short), GE (long despite allegations). No screen documented |
| Earnings-expectation work | Revision models (StarMine ARM) are institutional products | [D] NMW earnings as key factor; Hyman 2000; "what people think it's going to earn" (secondary) |
| Basic fundamental diligence | Core of every equity analyst role | [D] "never buy something that doesn't have … fundamentals"; analysts "go into a 10-Q" (MS 2026) |
| Crowding / 13F awareness | GS Hedge Fund Trend Monitor/VIP basket built from 13Fs for clients | [D] "For entry points, I care" (MS 2026) |
| Catalyst calendars | Universal | [D] Schlesinger article (1992), Milei Davos (2024), ChatGPT (2022) as triggers |
| Risk limits | Imposed at Soros by banks after 1998 | [D] Feig 2009; leverage and class caps (R-41..R-44) |

## 6. Conclusion table

Implication codes: **A-only** = keep in the article track only. **A+D(h)** = also a Druckenmiller-track background hygiene flag at weight 0 (logged, never gating). **A+D(e)** = evidence supports a Druckenmiller-track evidence family (interpreted, low weight). **Conflict** = contradicts a stated rule; article track only, and the D-track keeps its rule.

| Element (A-ids) | Origin | Evidence | Likely too-obvious standard practice (d) + evidence | Implication for spec |
|---|---|---|---|---|
| G2 liquidity (A-20) | Druckenmiller-supported + standard | [D] Feig 2009; ADRs 2024 | **Yes**: universal; his sizing rule implies it | Already D=R-33 |
| Forensic veto ≥ 45; accruals, auditor change, 10-K delay (A-21..A-26) | Other framework (Sloan, Beneish, MSCI AGR-type scores) via author's house skill | [D] house skill 2026-04-07; Sloan-based product 2026-09-20; Druckenmiller GE 2019 buy and Steinhoff tip-short | **Partly**: fraud avoidance is table stakes (T4), but a veto removing 62% fails T2, and GE fails T1 | Conflict as a veto. A-only at ≥ 45. Optional A+D(h): log extreme flags only (going-concern opinion, NT 10-K, auditor resignation) at weight 0 |
| ROIC > 15% & Debt/EBITDA < 2.5× (A-31) | Other framework (Greenblatt, quality factor) via author | [D] 2026-02-20 post; Teva, underearning, GE | **Uncertain** for diligence in general (Hustle "fundamentals"); **No** for the thresholds (T1 fails) | Conflict. A-only (`A!` stands) |
| EPS revision momentum (A-69, A-76) | Other framework (earnings momentum, StarMine/Zacks) | [D] NMW earnings; "what people think it's going to earn" (venue unverified); Hyman 2000 | **Yes**: standard; indirect trace | A-only for backward momentum. A+D(e) candidate: forward earnings-change-vs-consensus (variant, A-63), interpreted, low weight |
| 13F smart money, 7 managers (A-61, A-65) | Other framework (13F cloning: Dataroma, WhaleWisdom, GS VIP) | [D] no support; Duquesne is a cloning target; crowding "for entry points" | **Partly**: crowding monitoring is standard; cloning as a buy signal is not (T5) | A-only. At most A+D(h): crowding note for entry timing, weight 0 |
| Form 4 insider clusters (A-123, A-124) | Other framework (insider literature; OpenInsider) via author's module | [D] 2026-02-20 post; no Druckenmiller statement | **Uncertain**: routine in equity research; no Duquesne trace | A-only |
| Options flow, put/call, unusual volume (A-67, A-75) | Author / retail options-flow services | [D] 0.7/1.3 and 5× OI rules in 2026-02-20 post | **No**: options only as instruments (gold 2012, IWM/SPY calls) | A-only |
| COT commercial hedgers as smart money (A-74) | Practitioner COT lore (Briese, Williams) | [D] NMW 1987 speculator study = crowding as fragility, opposite framing; "crowd right 80%" | **Partly**: COT monitoring is standard at macro desks; the "commercials = smart money" reading is not | A-only for the smart-money construct; conflicts with R-31 (as R-37). Spec-owner choice: a speculator-crowding fragility input (NMW 1987) |
| 35 alt-data modules (A-78..A-95) | Alt-data vendor categories, free-API availability, author's prior modules | [D] patent rule verbatim from 2026-02-20; no Druckenmiller statement; mosaic = company contact | **No**: niche (T4), no trace (T3). Toggle 2021 supports machine idea generation only | A-only, weight 0 in D (PLAN D-20 unchanged) |
| Regime classifier incl. VIX (A-10..A-18) | Author's macro engine; generic risk-on/off dashboards | [D] 2026-04-02 macro post | **Yes** for regime dashboards generally; **No** for VIX (no trace) | A-only for the point composite and VIX; D-track keeps R-01..R-14 |
| Breadth panel (A-137) | Zweig-type breadth + Druckenmiller-supported | [D] NMW 1987 breadth; Bloomberg 2015; Ned Davis services | **Yes** | Already D=R-15/R-60 |
| Worldview theses (A-46..A-60) | Author's construction on a Druckenmiller-style idea (top-down themes) | [D] article p.22; Gemini narratives | **No** (bespoke) | A-only. D-track keeps the frozen transition table |
| Nightly Bayesian weights (A-40..A-45) | Author / generic quant | [D] "we don't have models"; no quant risk system | **No** | Conflict. A-only (PLAN E.6 stands) |
| Stops / targets / R:R (A-129..A-132) | Trading-education conventions; author's PTJ bracket | [D] "never used a stop loss" | **No** for him (stops are common elsewhere, but he rejects them explicitly, T1) | Conflict. A-only; R-49 stands |
| Convergence > 58 with ≥ 5 modules (A-33, A-118) | Author's composite ("multi-source confirmation") | [D] 2026-02-20 post; partial analogue in his "triple screen" and fat-pitch alignment; conflicts with "15-20% of information" | **No** | A-only. D-track keeps R-38 evidence-family count |
| Catalyst calendar, EIA report (A-122) | Standard + Druckenmiller-supported (catalyst concept) | [D] Schlesinger 1992, Milei 2024 | **Yes** | Already in R-38 (catalyst window) |
| Sector rotation gate (A-27) | Druckenmiller-supported | [D] NMW oil/defense 70%; chemicals capacity; biotech rotation 2025 | **Yes** | Already D (R-15/R-16, step 2) |
| Gemini "Druckenmiller-style narrative" (A-60) | Author (LLM) | [D] article p.22 | **No** | A-only; display only |

## 7. Open items

| Item | Status |
|---|---|
| Identity of the "7 tracked managers" (A-61) | Paywalled. Unknown whether Duquesne is one of them (circularity risk) |
| Gates 5, 6, 10 internals and module formulas | Paywalled. The free text and the author's other posts are the only evidence; provenance for these is [I] |
| Current web version vs library PDF | The post was edited 2026-09-25; not diffed |
| Former-employee accounts of Duquesne equity process | None found. Mallaby (*More Money Than God*) remains lending-restricted (library status) |
| Origin of the "what people think it's going to earn" quote | Not located; secondary only (TheStreet 2024) |
