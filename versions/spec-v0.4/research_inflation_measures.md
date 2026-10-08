# Inflation and labour-market measures: library evidence, current spec use, free data, assessment

Research date 2026-10-07. Scope: research only. No engine run, no `fatpitch.versions` run, no statistic computed against case labels or Fed-cycle labels. `cases\`, `results\versions\*` run directories and `spec\fed_cycles.yaml` were not opened. Only this file was written.

Read: `CLAUDE.md`, `PLAN.md` §0, §0.1, §0.2, §E (E.4a, E.6, E.7), §D.2; `spec\process.md` §0 and R-06..R-10, R-12..R-14, R-23, R-56, R-58, R-63, R-66, R-67; `spec\registry.yaml` (infl., policy.taylor_*, antic.* entries, tunable list); `spec\data_catalogue.yaml` (CPI, UNRATE, NROU entries; id list); `spec\research_market_implied_fed.md`; `src\fatpitch\rules\step1.py` (R-06..R-09, R-63), `src\fatpitch\rules\anticipation.py` (R-67); library notes listed in §A1/§B1; amber lake listings (`fred\series`, `fred\vintages`, `bls\series`, `longhist\rtdsm`, `philfed\spf`, `cbp\worldbank_cmo`) with date ranges read from the parquet files.

Owner requests: "review all aspects of inflation measures, CPI, PCE, PPI, etc." (Part A) and "payrolls" (Part B).

Conventions. Reliability codes from note front-matter: **P** = primary, **NP** = near-primary (transcript), **S** = secondary summary. **Verbatim Y** = the words appear as a quotation in the note; **N** = the note paraphrases. `DS/` = `library\discovered_sources\`, `RS/` = `library\reference_sources\`. "Lake" = `C:\Users\<user>\Documents\amber\data\lake`. "Catalogued" = has an entry in `spec\data_catalogue.yaml` (required before `AmberLakeSource` serves it). Items marked *(verify)* are from general knowledge of the data sources and were not checked against the source in this session.

Descriptive statistics in §A3.3 and §B3.2 are computed on lake data only (CPI/PCE latest vintages, ALFRED vintage stores); none uses cases, outcomes or the Fed answer key.

---

# Part A — Inflation measures

## A1. Library evidence

Search: `(?i)inflation|CPI|PCE|core|PPI|producer price|wage|AHE|ECI|breakeven|TIPS|expectations|transitory|commodit|oil|food|shelter|rent|deflation|disinflation|price level` over `library\discovered_sources\` and `library\reference_sources\` (53 files with hits; front-matter, index and URL-status lines excluded).

### A1.1 Statements

| Date (statement) | File | Rel. | Verb. | Short quote / content | Measure cited | Horizon | Number | Implication for rules |
|---|---|---|---|---|---|---|---|---|
| 1991-12 (about Q4 1981) | DS/1992-XX-XX_new-market-wizards-full-chapter-text.md | P | Y | "…the Fed was extremely tight, and inflation was already coming down sharply." | Unspecified ("inflation") | Change (momentum) | — | Momentum plus tight stance → easing anticipation (R-67 I leg) |
| 2015-01 (about 1981–82) | RS/2015-01-18_lost-tree-club-speech.md | NP | N | Volcker era: short rates 18%, inflation 12%; 50% in 30-year Treasuries | Unspecified, headline CPI magnitude | Level | 12% | Real-rate framing (FF vs inflation; R-08 shape) |
| 2015-01 (about Q4 2003) | RS/2015-01-18_lost-tree-club-speech.md | NP | N (quote Y for the 3–6% range) | FF 1% vs nominal growth 9%; staff guesses for the right rate 3–6% | Nominal GDP growth, not CPI | yoy | 9% | Policy-error benchmark was nominal growth, not a CPI Taylor rule (R-06 vs R-56) |
| 2000 (told 2009, 2018, 2022, 2024) | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md; RS/2018-09-06; RS/2022-06-10; RS/2024-11-06 | NP; NP; S; NP | N; Y; Y; Y | Oil, rates and dollar up together = "three death knells" | Oil price (commodity), not an inflation index | Change | — | R-10 (already uses WTI) |
| 2012-04 | DS/2012-04-XX_grants-spring-conference-jim-grant.md | S | Y | "The Fed chairman will always find a way to be dovish"; high oil with shrinking GDP would bring QE3 | Oil | Level | — | Oil read as a growth tax, not a tightening trigger |
| 2013-05-08 | DS/2013-05-08_sohn-commodities-conundrum.md | S | Y | "Commodities tend to go down while stocks go up." | Commodities (as assets) | Trend | — | Commodities as expression/cross-asset, not inflation gauge |
| 2015-01-18 | RS/2015-01-18_lost-tree-club-speech.md | NP | N | Inflationary or deflationary outcome both possible; oil to $30 could be deflationary | Oil → headline | Level | $30 | Oil as a headline-deflation channel |
| 2016-11-10 | DS/2016-11-10_cnbc-squawk-box-post-election-sold-gold.md | NP | N | Low rates plus upward growth revision → rates "are going to go up a lot" | Growth expectations | — | — | Nominal-growth reasoning |
| 2017-12-12 | DS/2017-12-12_cnbc-closing-bell-kelly-evans.md | NP | Y | "The 2% inflation target has sort of become a religion initiated by the professors." 1950s: ~1% inflation with 4% FF; Taylor ~4% vs 1% | Unspecified; the Fed's 2% target (PCE since 2012) | Level | 2%, 1%, 4% | 2% is the Fed's benchmark, not his; R-06 uses it as the Fed's reaction function only |
| 2018-05-03 | DS/2018-05-03_manhattan-institute-hamilton-award-speech.md | P | Y | "…the Fed has not only kept interest rates below inflation…"; "…average, average inflation over the last number of centuries." | Unspecified | Level (real rate) | — | Negative real policy rate as error evidence (R-06/R-08 shape) |
| 2019-06-03 | DS/2019-06-03_econclub-ny-bessent.md | S | N | 2% "obsession" misguided; inflation mismeasured (free digital services, productivity) | Measured CPI/PCE (criticised) | Level | 2% | Measurement-bias argument: measured inflation overstates true; no rule change |
| 2019-06-07 | DS/2019-06-07_cnbc-squawk-box-one-way-bet.md | NP | N / Y | Mismeasured productivity → true inflation lower; "…we have deflation in every instance because there was an asset bubble." | Measured CPI (criticised) | Level | — | Deflation follows bubbles (R-11 context) |
| 2020-09-09 | DS/2020-09-09_cnbc-squawk-box-absolute-raging-mania.md | S | N | Inflation risk 5–10% within about five years | Unspecified (scored by note as CPI) | Multi-year | 5–10% | Regime view, not a rule input |
| 2020-11-09 | RS/2020-11-09_cnbc-the-exchange-rotation.md | S | N | Inflation to rise over 5–6 years; hedges gold, bitcoin, miners | Unspecified | Multi-year | — | Expressions (step 3) |
| 2021-01 | DS/2021-01-XX_talks-at-gs-great-investors-pasquariello.md | NP | Y | "my overriding theme is inflation relative to what policymakers think." "…so they have stimulus in the pipeline, the more I win on my commodities." | Inflation vs the Fed's own expectation; commodities as the trade | Gap vs policymaker view | — | Core statement for R-67 I leg; the benchmark is the Fed's projection, not 2% per se. Commodities are the expression, not the signal |
| 2021-05-10/11 | DS/2021-05-10_wsj-oped-fed-emergency-policy-bubbles.md; DS/2021-05-11_cnbc-squawk-box-raging-mania-dollar.md | S; S | N | Emergency policy invites bubbles and inflation; 10% inflation possible (unverified in CNBC text) | Unspecified | — | 10% (unverified) | Policy error (R-05/R-06) |
| 2021-05-11 | DS/2021-05-11_hustle-mfm-trung-phan.md | NP | N | Central case inflation; "the minute they start tightening, the equity market should go down a lot" | Unspecified | — | — | Ties inflation to Fed reaction (R-14) |
| 2021-06-10 | DS/2021-06-10_email-to-cnbc-kernen-market-not-speaking.md | S | Y | Hot May 2021 CPI ignored: "The market is not speaking right now." | CPI release (headline print) | Monthly print | — | Price-vs-news on CPI release days (R-30); market signal impaired |
| 2022-06 | DS/2022-06-XX_sohn-2022-john-collison.md | NP | Y | "Once inflation gets above 5%, it's never come down unless Fed funds have gotten above the CPI." (CPI "is 8%" at the time) | **CPI** (named), headline level (8% matches headline May 2022) | **yoy level** | **5%** | R-08/R-09 measure = headline CPI yoy |
| 2022-06-10 | RS/2022-06-10_sohn-2022-collison-conversation.md | S | Y | "We've never had a soft landing after inflation has got above 4.5%." | Unspecified; context CPI | yoy level | **4.5%** | R-07 |
| 2022-09-28 | DS/2022-09-28_delivering-alpha-kernen-transcript.md | NP | N / Y | Inflation "rotates" through sectors and into wage settlements (1970s); Fed risked credibility for "30bp of inflation"; "You don't cure inflation with an inflationary act." | Breadth across sectors; **wages** | Persistence | 30 bp | Wages as persistence channel; no wage measure named |
| 2023-04-24 | DS/2023-04-24_nbim-annual-investment-conference.md | NP | N | Expected inflation to return after an aggressive easing | Unspecified | — | — | Second-wave risk |
| 2023-05-09 | DS/2023-05-09_sohn-2023-kiril-sokoloff.md | S | N | 9.1% CPI peak attributed to ~$5T stimulus; near term 3–3.5%; case for 8% or deflation | **CPI headline** (9.1% is the headline yoy peak) | yoy | 9.1%, 3–3.5%, 8% | Headline CPI yoy is his reference series |
| 2023-10-24 | DS/2023-10-24_robin-hood-paul-tudor-jones.md | S | N | 8–10% under a Burns-style regime, 3–4% otherwise; 10-year fair value 4.5–5% with 2% inflation | Unspecified | Multi-year | 2%, 3–4%, 8–10% | 10y vs inflation + real yield (R-56 adjacent) |
| 2024-05-07 | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md | NP | N | "Six-month annualized inflation had turned up"; asymmetric easing bias "with inflation at 3%"; 6% possible in 2025 | **6-month annualised** (series unnamed); 3% level | **6m annualised** | 3%, 6% | R-67 I leg horizon (antic.infl_short_m = 6) |
| 2024-10-16 | DS/2024-10-16_bloomberg-tv-sonali-basak.md | NP | N | Risk of re-acceleration in 2025; asymmetric | Unspecified | Momentum | — | Second-wave risk; momentum, not level |
| 2024-11-06 | RS/2024-11-06_nbim-in-good-company-podcast.md | NP | Y / N | "I've switched to being more worried about inflation going forward than the economy itself." 1970s: ~8% → 3% then re-accelerated | Unspecified, magnitudes match headline CPI | Turning point | 8%, 3% | Inflation turning point as object (R-67 I leg) |
| 2026-02-27 | DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md | NP | N | Fed cutting into a booming economy "plus commodities" could drive inflation; bond short as hedge | Commodities as an inflation input | — | — | Only statement treating commodities as a cause of CPI inflation; hedge framing |
| 2026-08-24 | DS/2026-08-24_wsj-oped-let-the-bond-market-speak.md | S | N | Inflation above target since 2021; deficit ~6% at full employment | Fed target measure (PCE) implied | Level vs target | — | Context |
| 2026-09-10 | DS/2026-09-10_piper-sandler-closed-door-event.md | S | Y ("no longer necessary") | Rate cuts "no longer necessary"; rise in long yields justified | Unspecified | — | — | Context |

### A1.2 What the library does and does not contain

| Measure | Statements | Finding |
|---|---|---|
| Headline CPI yoy | 2022-06 (NP, Y, "the CPI"), 2023-05 (9.1%), 2022-06-10 (4.5%), 1981–82 (12%) | The only index he names. Every number he gives (4.5%, 5%, 8%, 9.1%, 12%) matches headline CPI yoy magnitudes |
| Core (ex food and energy), CPI or PCE | None | Zero hits. No statement distinguishes headline from core |
| PCE (headline or core) | None by name; "2% target" (2017-12-12 NP Y; 2018-05-03 P; 2019) refers to the Fed's target, which is PCE-defined since 2012-01 | He discusses the target, never its index |
| 6-month annualised | 2024-05-07 (NP, N) | Single statement; series unnamed |
| PPI / producer prices / import prices | None | Zero hits. No pipeline-inflation statement from producer prices |
| Wages (AHE, ECI, ULC) | 2022-09-28 (NP, N) "into wage settlements" | Persistence channel, no measure, no number |
| Commodities / oil | R-10 cocktail (many); 2012-04 oil as growth tax; 2015-01 oil to $30 deflationary; 2021-01 commodities as the inflation trade; 2026-02 commodities could drive inflation | Oil is an input to R-10 and a headline channel; commodities are mostly an expression, once (2026-02, NP, N) a cause |
| Inflation expectations (breakevens, TIPS, Michigan, SPF) | None | Zero hits. "What policymakers think" (2021-01) points to the Fed's own projection, not market or survey expectations |
| Shelter / rent | None | — |
| Deflation | 2019-06-07 (NP, Y): deflation follows asset bubbles; 2015-01 oil-driven deflation risk | Bubble-driven, not measured-index-driven |

Synthesis. The spec's choice of headline CPI yoy for R-07, R-08, R-09 is the reading best supported by the library: "the CPI" is named, and every threshold or magnitude he cites is a headline CPI yoy figure. Nothing in the library supports core over headline, PCE over CPI, or PPI, breakevens or survey expectations as inputs in the faithful track. Two horizon facts are stated: yoy levels (thresholds) and one 6-month-annualised momentum read (2024). The policy benchmark he uses is "what policymakers think" (2021-01) and, retrospectively, nominal growth (2003 via Lost Tree).

## A2. Current spec use

### A2.1 Rules that read inflation

| Rule | Track | Series in spec | Series in code | Transform | Threshold / params | Vintage / PIT | Tag |
|---|---|---|---|---|---|---|---|
| R-06 Taylor gap | faithful | `CPIAUCSL` yoy; "core CPI `CPILFESL` from 1957 as sensitivity" | `step1.cpi_yoy` → `CPIAUCSL` only (lake fallback `CPIAUCNS` pre-1972-07-21). **Core sensitivity not implemented** | yoy, within as-of vintage | `i* = r* + π + a(π − π*) + b(NROU − UNRATE)`; r* 2.0, π* 2.0 (`policy.taylor_pi_target_pct`), a 0.5, b 1.0; `policy.tg_threshold_pp` 2.0 (tunable 2/8) | ALFRED `CPIAUCSL` 1972-07-21→; `CPIAUCNS` (NSA, unrevised) before | interpreted |
| R-07 no soft landing | faithful | `CPIAUCSL` yoy; NSA `CPIAUCNS` 1913→ for era B | same as R-06 | yoy; max over trailing window | `infl.soft_landing_pct` 4.5 (stated), `infl.lookback_m` 24 (interpreted, fixed) | as R-06 | stated |
| R-08 FF < CPI veto | faithful | `CPIAUCSL` yoy, FF | `CPIAUCSL` yoy vs FF monthly average (`FEDFUNDS`, `DFF` fallback) | yoy level vs FF level | `infl.persist_pct` 5.0 (stated); `infl.r08_expected_to_hold` false | as R-06 | stated |
| R-09 recession prior | faithful | `CPIAUCSL` yoy | same | yoy peak in window | `infl.persist_pct` 5.0, `infl.lookback_m` 24 | as R-06 | stated |
| R-10 cocktail | faithful | `DCOILWTICO` (1986→), `WTISPLC` (1946→) | per catalogue | Δ over `xasset.window_m` | `xasset.window_m` 6 (tunable 3/8) | daily same-day; monthly lag rule | stated |
| R-56 10y vs nominal GDP | faithful | `GDP` yoy (nominal) | `GDP` ALFRED 1991-12→ | yoy | `rates.ngdp_anchor_gap_pp`, `rates.ngdp_cheap_gap_pp` | advance-estimate vintage | stated |
| R-67 anticipated turn, I leg | hybrid | "core CPI when acquired, headline until then" | `CPI_IDS = (CPILFESL, CPIAUCSL, CPIAUCNS)`, first usable wins | `I_pp = π6 − π12`, π6 = 6m annualised, π12 = 12m | `antic.infl_band_pp` 0.5; tightening also needs `π6 > policy.taylor_pi_target_pct` (2.0); `antic.zlb_ff_pct` 0.25; all fixed | `CPILFESL` ALFRED 1996-12-12→; `CPIAUCSL` ALFRED 1972-07-21→; `CPIAUCNS` before | interpreted |
| R-30/R-51 price vs news | faithful | CPI release as a scheduled release | step 4 (not read here) | sign of excess return vs surprise (actual − prior) | `exit.price_vs_news_window_bd` | release time | stated |

No rule reads PCE, PPI, wages, breakevens, Michigan, SPF or the Cleveland Fed model. R-12 (cross-region) reads no inflation series.

### A2.2 Inconsistencies

| # | Finding | Where | Effect | Class |
|---|---|---|---|---|
| I-1 | R-67 I leg uses **core** CPI from asof 1996-12-12 and **headline** before; R-06..R-09 use headline throughout | `anticipation.py` `CPI_IDS`; process.md R-67 | One rule switches measure mid-history: `I_pp` has a level and volatility break at 1996-12-12 (headline–core gap averages 0.4–1.1 pp by decade, max 4.6 pp, §A3.3). Headline and core rules can disagree on the same date | Design (R-67 text says "core when acquired") |
| I-2 | R-67 I leg falls back to **NSA** `CPIAUCNS` before 1972-07-21 and computes a **6-month** change on it | `anticipation.py` `_cpi`, `inflation_part` | NSA 6-month annualised has a calendar-month bias of −1.08 pp (Dec) to +0.61 pp (May) vs SA (1960→, §A3.3), larger than `antic.infl_band_pp` = 0.5. Pre-1972 I-leg classes are seasonal artefacts in part. yoy (R-06..R-09) is unaffected because 12-month changes cancel seasonality | Defect in data handling; the fix changes outputs on scored dates → owner decision (spec text "headline until then" does not specify NSA, so not citable as mechanical) |
| I-3 | R-06 core-CPI sensitivity registered in process.md but not implemented; process.md says "from 1957" but core vintages start 1996-12-12 (catalogue `pre_vintage: unknown`) | process.md R-06; `step1.r06_policy_error` | Spec–code gap; "from 1957" cannot be met point-in-time | Mechanical (implement as registered, 1996-12→, report only) |
| I-4 | π* = 2.0 is the FOMC target defined on **PCE** (2012-01); R-06 and R-67 apply it to **CPI** | registry `policy.taylor_pi_target_pct` notes; R-06 formula; R-67 tightening condition | CPI yoy exceeded PCE yoy by 0.45 pp (headline) and 0.47 pp (core) on average 1960–2026 (latest vintages), range 0.2–0.7 pp by decade. In R-06 the rule rate is overstated by `(1 + a) × wedge` ≈ 0.7 pp → TG biased toward `too_loose` by ~0.7 pp against a 2.0 pp band. In R-67 the π6 > 2.0 condition fires more often than a PCE-consistent 2% would | Design (constant value or measure change) |
| I-5 | Taylor (1993) defined π on the GDP deflator; the spec cites Taylor (1993) for a CPI-based rule | registry `policy.taylor_*` citations | Convention mismatch; same direction as I-4 (CPI above deflator on average) | Documentation |
| I-6 | Catalogue `CPIAUCNS.rules` lists only R-07, but `CPIAUCNS` is consumed as the fallback by R-06, R-08, R-09 and R-67 | `spec\data_catalogue.yaml` | Provenance listing incomplete | Mechanical (catalogue text) |
| I-7 | process.md R-07 says "NSA `CPIAUCNS` 1913→ for era B"; the catalogue applies NSA only before 1972-07-21 (era B also covers 1972–2001, where SA vintages are used) | process.md R-07 vs catalogue | Wording mismatch; catalogue behaviour is the better PIT choice | Documentation |
| I-8 | R-08 compares the latest CPI yoy (month t−1, published mid-month t) with FF as a monthly average | `step1.r08_ff_below_cpi`, `ff_monthly` | Timing offset of up to one month between the two legs; immaterial at the 5% threshold except near crossings | Note only |
| I-9 | Lake series in use or proposed but **not catalogued**: `PCEPI`, `PCEPILFE`, `T5YIE`, `T10YIE`, `DFII10`, `MICH`, `EXPINF1YR`, `EXPINF10YR`, `ICSA`, `CCSA`, `PAYEMS` (vintage store only), `philfed\spf\median` | catalogue id list | Cannot be read through `AmberLakeSource` | Data |
| I-10 | BLS mirror `bls\series\*` (CPI, core CPI, PPI final demand `WPSFD4`, import prices `EIUIR`, AHE, ECI, JOLTS, CES payrolls, CPS rates) covers 2017→ only and has **no `published_at` column** | lake | Unusable point-in-time (rows without `published_at` are excluded by rule) | Data |

## A3. Free measures inventory

### A3.1 Inventory

Release times are ET. "ALFRED from" = first vintage date in the lake store where present, else *(verify)*.

| Series (FRED id) | Content | Start | Freq | Release / lag | Revisions | Real-time vintages | In lake | Catalogued | Caveats |
|---|---|---|---|---|---|---|---|---|---|
| `CPIAUCSL` | CPI-U all items SA | 1947-01 | M | ~10–15th of month t+1, 08:30 | SA factors revised each February (5 years back) | ALFRED 1972-07-21→ (lake); RTDSM `cpi` 1994-08, `pcpi` 1998-11 (lake, never reached) | Yes + vintages | Yes | 1983-01 homeownership switched to rental equivalence (CPI-W 1985-01); 1990s quality and geometric-mean changes (1999); history not restated |
| `CPIAUCNS` | CPI-U all items NSA | 1913-01 | M | as above | Not revised (rare corrections) | Not needed; ALFRED store 2024→ only | Yes | Yes | NSA: yoy usable, sub-annual changes seasonal (§A3.3) |
| `CPILFESL` | Core CPI SA | 1957-01 | M | with CPI | SA revised each Feb | ALFRED 1996-12-12→ (lake) | Yes + vintages | Yes (R-06, R-67) | BLS publication of the ex-food-and-energy aggregate before the 1970s *(verify)*; pre-1996 values are later-vintage |
| `CPILFENS` | Core CPI NSA | 1957-01 | M | with CPI | Not revised | n/a (unrevised) | **No** | No | PIT-clean core before 1996 for yoy; sub-annual changes seasonal |
| `PCEPI` | PCE price index | 1959-01 | M | ~last week of t+1, 08:30 (Personal Income and Outlays) | Revised monthly (2 months), annually (each summer/Sept) and in comprehensive revisions (e.g. 2013, 2018, 2023) | ALFRED exists *(verify start; believed ~2000)*; RTDSM quarterly PCE deflator *(verify)* | Latest only | No | Revisions to history are routine, 0.1–0.3 pp on yoy common *(verify magnitude)*; target measure since 2012-01 |
| `PCEPILFE` | Core PCE | 1959-01 | M | as PCEPI | as PCEPI | ALFRED exists *(verify start)*; lake vintage store only 2024-12→ (76 rows) | Latest + stub vintages | No | Fed's preferred gauge; effectively no PIT history in lake |
| `PCETRIM12M159SFRBDAL` (Dallas trimmed-mean PCE, 12m; 1m and 6m variants exist) | Trimmed mean PCE | 1977-02 *(verify)* | M | same day as PCE | Revised with PCE | No ALFRED vintages *(verify)* | No | No | Revised; PIT only via own archive |
| `MEDCPIM158SFRBCLE`, `TRMMEANCPIM158SFRBCLE` (Cleveland median, 16% trimmed CPI) | Median / trimmed CPI | 1983-01 *(verify)* | M | CPI day, ~11:00 | Revised with CPI SA factors | ALFRED coverage *(verify)* | No | No | Starts after the 1983 shelter change |
| `CORESTICKM159SFRBATL` (Atlanta sticky-price CPI) | Sticky-price CPI | 1968 *(verify)* | M | CPI day | Revised with SA | *(verify)* | No | No | Built from CPI components |
| `PPIACO` | PPI all commodities (NSA) | 1913-01 | M | ~mid-month t+1, 08:30 | Revised 4 months after first release, then fixed | ALFRED *(verify)* | No | No | Commodity-weighted; heavy energy/raw-material share |
| `PPIFGS` | PPI finished goods (SOP) | 1947-04 | M | as PPI | as PPI | ALFRED *(verify)* | No | No | Headline PPI until 2014-01; still published as an FD-ID sub-index *(verify)* |
| `PPIFIS` | PPI final demand | 2009-11 | M | as PPI | as PPI | ALFRED from 2014 *(verify)* | No (BLS `WPSFD4` 2017→, no `published_at`) | No | 2014-01 switch to FD-ID; backcast to 2009-11 only — no splice to SOP is exact |
| `IR` (import price index, all) | Import prices | 1982-09 *(verify)* | M | ~mid-month | Revised 3 months | *(verify)* | BLS `EIUIR` 2017→ only | No | Short history |
| `AHETPI` | AHE production & nonsupervisory | 1964-01 | M | Employment Situation, first Friday | Revised 2 months + annual benchmark | ALFRED *(verify start)* | **No** | No | Composition effects (2020 spike) |
| `CES0500000003` | AHE all private | 2006-03 | M | as above | as above | ALFRED | BLS mirror 2017→, no `published_at` | No | Too short for most cases |
| `ECIWAG` / `ECIALLCIV` | Employment Cost Index | 1975 (wages, private) / 2001 (FRED all civilian) *(verify)* | Q | ~end of month after quarter | Small (SA) | *(verify)* | BLS `CIU101…` 2017→ only | No | Composition-fixed; quarterly |
| `ULCNFB` | Unit labour costs, nonfarm business | 1947 Q | Q | ~5 weeks after quarter, revised twice + annual | Large revisions | ALFRED *(verify)* | No | No | Noisy, revised |
| `T5YIE`, `T10YIE` | Breakevens (nominal − TIPS) | 2003-01-02 | D | next business day (H.15) | Not revised | n/a | Yes | No | TIPS liquidity premium (2008), CPI-NSA indexation; ≠ expectations |
| `T5YIFR` | 5y5y forward breakeven | 2003-01 | D | next day | Not revised | n/a | **No** | No | as above |
| `DFII10` | 10y TIPS real yield | 2003-01-02 | D | next day | Not revised | n/a | Yes | No | — |
| `MICH` | Michigan 1-year expected inflation (median) | 1978-01 | M | prelim ~mid-month, final ~end-month | Not revised after final | n/a | Yes | No | Survey; 5–10-year series from the UMich site (monthly from 1990, sporadic earlier) *(verify)*, not in lake |
| SPF (`philfed\spf\median`) | Professional forecasts | CPI 1981Q3; CPI_10Y 1991Q4; CPI_5Y 2005Q3; CORE_CPI, CORE_PCE, PCE, PCE_10Y 2007Q1; UNRATE 1968Q4 (lake) | Q | mid-quarter | Never revised | n/a (each survey is its own vintage) | Yes | No | Release dates per survey must be attached for PIT |
| `EXPINF1YR`, `EXPINF10YR` | Cleveland Fed model expectations | 1982-01 | M | ~mid-month | **Model re-estimated each release; history revises** | No | Latest only | No | Not PIT-usable without own archive |
| FOMC SEP median core PCE (`PCECTPICTM` etc.) | "What policymakers think" | 2007-10 (central tendency); medians later *(verify)* | 4/yr | FOMC meeting day 14:00 | Never revised | n/a | **No** (`fred\sep` folder empty) | No | Pre-2007: Humphrey-Hawkins central tendency 1979→ in Monetary Policy Reports *(verify)* |
| Oil: `DCOILWTICO`, `WTISPLC`, `DCOILBRENTEU` | WTI daily / monthly, Brent | 1986 / 1946 / 1987 | D/M | same/next day; monthly lag | Not revised | n/a | Yes | WTI yes | Pre-1974 posted prices (regulated) |
| World Bank CMO indices (`cbp\worldbank_cmo\indices.parquet`) | Total, energy, agriculture, metals | 1960-01 | M | ~2nd business day of month t+1 *(verify)* | Occasional | n/a | Yes | No | `published_at_method: unknown` in lake → needs a lag rule |
| `PCOPPUSDM` (IMF copper) | Copper | 1992-01 | M | mid-month t+1 | Rare | n/a | Yes | Yes | — |
| CRB / S&P GSCI | Commodity indices | — | — | — | — | — | No | — | Not free; World Bank CMO and `PPIACO` are the free long proxies |

### A3.2 Era coverage (point-in-time usable today)

| Measure | PIT-usable from (asof) | Before that |
|---|---|---|
| Headline CPI SA vintage | 1972-07-21 | NSA `CPIAUCNS` (yoy exact; sub-annual seasonal) to 1913 |
| Core CPI SA vintage | 1996-12-12 | Nothing PIT in lake; `CPILFENS` (to acquire) would give unrevised core yoy from 1958 |
| Headline / core PCE | 2024-12 (lake vintages) | Nothing PIT in lake; ALFRED vintages to acquire *(start to verify)* |
| PPI | not in lake | `PPIACO` 1913→ to acquire |
| Wages | not in lake | `AHETPI` 1964→ to acquire |
| Breakevens | 2003-01 | — |
| Michigan 1y | 1978-01 | — |
| SPF CPI | 1981Q3 | — |

### A3.3 Descriptive magnitudes (lake data, no labels)

CPI minus PCE yoy (latest vintages), and headline minus core CPI:

| Decade | CPI − PCE headline (pp, mean) | CPI − PCE core (pp, mean) | |headline − core CPI| mean (pp) | max (pp) |
|---|---|---|---|---|
| 1960s | 0.20 | 0.18 | 0.36 | 1.24 |
| 1970s | 0.66 | 0.57 | 1.04 | 4.64 |
| 1980s | 0.52 | 0.78 | 0.86 | 2.58 |
| 1990s | 0.69 | 0.82 | 0.44 | 1.58 |
| 2000s | 0.43 | 0.30 | 1.14 | 3.49 |
| 2010s | 0.24 | 0.26 | 0.68 | 2.00 |
| 2020s | 0.44 | 0.32 | 0.84 | 3.07 |
| 1960–2026 | 0.45 | 0.47 | — | — |

NSA minus SA 6-month annualised headline CPI, by calendar month of the latest observation (1960→, latest vintages): Jan −0.94, Feb −0.59, Mar −0.21, Apr +0.09, May +0.61, Aug +0.60, Sep +0.20, Oct −0.09, Nov −0.60, Dec −1.08 pp (Jun–Jul not printed; same sign pattern). The amplitude exceeds `antic.infl_band_pp` (0.5).

First release vs latest vintage (ALFRED): headline CPI SA yoy mean |revision| 0.06 pp, p90 0.14 pp (1972→); 6-month annualised p90 0.68 pp. Core CPI SA yoy mean 0.03 pp, p90 0.06 pp; 6-month annualised p90 0.41 pp (1996→). yoy is robust to SA revisions; 6-month annualised is not, which is why vintage handling matters more for R-67 than for R-06..R-09.

## A4. Assessment

### A4.1 Per rule

| Rule | Should use | Headline vs core | Reasoning | Change type |
|---|---|---|---|---|
| R-07, R-08, R-09 | Headline CPI yoy, SA vintage 1972-07→, NSA before (current) | Headline | He names "the CPI"; 4.5%, 5%, 8%, 9.1%, 12% are headline yoy magnitudes; yoy is seasonally neutral, so the NSA fallback is exact pre-1972; vintages give 1972→ PIT. The historical regularities he cites (1970s–80s) were observed on headline CPI | None |
| R-06 | Headline CPI yoy primary (current); core CPI sensitivity from 1996-12 (implement as registered); PCE wedge reported | Headline primary, core sensitivity | Faithfulness: his Taylor citations are external calculations whose inflation measure is not stated in the library; the only first-hand benchmark (2003) is nominal growth. PIT: CPI is the only inflation measure with vintages back to 1972. Fed target era: PCE-defined only from 2012-01, and PCE has no PIT history in the lake; switching R-06 to PCE in 2012 would introduce a measure break and look-ahead | I-3 mechanical; any measure or π* change is a design change |
| R-67 I leg (hybrid) | One measure across all scored dates, SA, vintaged | See decision D-A2 | The current chain mixes core (1996-12→), headline SA (1972-07→) and headline NSA (pre-1972) in a 6-month transform that is sensitive to both measure and seasonality | Design change (owner) |
| R-10 | WTI (current) | n/a | Stated as oil price; no index substitution warranted | None |
| R-56 | Nominal GDP (current) | n/a | Stated | None |

### A4.2 Should the Fed's target measure (PCE) drive R-06?

Not as the primary. (i) No statement of his names PCE; he names CPI. (ii) Point-in-time: PCE is revised every summer and in comprehensive revisions, and the lake holds PCE vintages only from 2024-12; any pre-2024 PCE input would be later-vintage data (look-ahead). (iii) A switch at 2012-01 creates a measure break in R-06 inside the scored sample. The defensible handling of the target mismatch is to keep CPI and state the bias (I-4: ~0.7 pp toward `too_loose`) in the fidelity report, with a PCE variant as report-only once PCE vintages are acquired. Adjusting π* to a CPI-equivalent (~2.4–2.5) would be an interpreted constant with no source number and would change scored outputs: design change.

### A4.3 Do PPI, commodities, wages add a distinct signal he cites?

| Input | Cited by him? | Distinct from CPI? | Where it could enter | Assessment |
|---|---|---|---|---|
| PPI (pipeline) | No (zero hits) | Partly (leads CPI goods by 1–3 months in the literature) | R-67 I leg (hybrid) | Not in the faithful track. Hybrid-only candidate; adds a measure, an argued threshold and the 2014 FD-ID break. Not recommended now |
| Oil | Yes (R-10; 2012, 2015 as growth tax / deflation channel) | Yes | Already R-10 | No new rule |
| Broad commodities | Mostly as an expression (2021-01, 2021-05); once as an inflation cause (2026-02, NP, N) | Yes | R-67 I leg (hybrid); R-19 cross-asset trend already reads commodities | No new faithful rule; a single NP paraphrase does not support a gate |
| Wages | Yes as persistence (2022-09, NP, N), no measure, no number | Yes (persistence) | Premise text for R-08/R-09 theses (display); R-67 hybrid | Display/premise only; any gate would be `interpreted` with no anchor |
| Inflation expectations (breakevens, Michigan, SPF) | No | Yes | R-58 adjacent; R-63 | Not supported; "what policymakers think" is better proxied by FOMC projections (SEP 2007→), which would be the faithful benchmark for the 2021 statement — data not in lake |
| R-63 (fiscal supply) | n/a | — | — | No inflation input warranted; his fiscal statements key on deficits at full employment (Part B) |

### A4.4 Era coverage and fallbacks

| Gap | Fallback options | Defensible choice |
|---|---|---|
| Core CPI before 1957 | None exists | Headline only (R-06..R-09 already headline) |
| Core CPI vintages before 1996-12 | (a) `CPILFENS` NSA (unrevised, PIT-clean) — exact for yoy, seasonal for 6-month; (b) `CPILFESL` latest vintage flagged (NROU-style `pre_vintage: usable`) — look-ahead, 6m p90 revision 0.41 pp ≈ the 0.5 band; (c) headline | For yoy uses: (a). For 6-month uses (R-67): headline SA vintage, or (a) with a seasonally neutral formula (annualised 6-month change vs the same six calendar months a year earlier) — a formula change |
| PCE before 1959; PCE vintages before ~2000 *(verify)* | CPI | CPI (no alternative) |
| Headline SA vintages before 1972-07-21 | NSA `CPIAUCNS` | yoy: NSA exact. 6-month: unknown (unknown never counts as fail) |

All `tunable: true` slots (8/8) stay as they are. Every option below either changes no constant or changes a fixed (`tunable: false`) one.

## A5. Decisions (inflation)

**D-A1. R-07/R-08/R-09 measure.**
- A (Recommended): keep headline CPI yoy (SA vintage 1972-07→, NSA before) — matches the named index and every number he gives; yoy is revision- and season-robust.
- B: core CPI yoy — no library support; loses 1947–1956.
- C: PCE yoy — no library support; no PIT history.

**D-A2. R-67 inflation-leg measure (hybrid track; design change).**
- A (Recommended): headline CPI SA vintage on every date from 1972-07-21; I leg `unknown` before (drop the NSA fallback for the 6-month transform); core CPI reported as a variant from 1996-12 — one PIT-clean measure across the scored sample, removes the 1996-12 break (I-1) and the seasonal artefact (I-2).
- B: core CPI only, I leg `unknown` before 1996-12-12 — core matches what the Fed reacts to, but halves era coverage for the anticipation test.
- C: core throughout via `CPILFENS` (to acquire) before 1996-12 with a seasonally neutral 6-month formula — PIT-clean core back to 1958, at the cost of a formula change and one more series.
- D: keep the current chain — retains I-1 and I-2.

**D-A3. π* = 2% applied to CPI (R-06, R-67).**
- A (Recommended): keep 2.0 and CPI; state the ~0.45 pp CPI–PCE wedge and its ~0.7 pp effect on TG in the fidelity report; add a PCE-based R-06 variant as report-only once PCE vintages exist — no scored output changes; bias becomes visible.
- B: CPI-equivalent π* (2.5) for CPI inputs — removes the bias, but the number is interpreted with no source; changes scored outputs (re-registration).
- C: R-06 on core PCE from 2012-01, CPI before — Fed-target-faithful after 2012, but measure break and no PCE vintages (look-ahead).

**D-A4. R-06 core sensitivity (I-3).**
- A (Recommended): implement as registered, core CPI vintage 1996-12→, report-only; correct process.md "from 1957" to "from 1996-12 (vintage)" in the next re-registration — closes a spec–code gap without touching the primary score.
- B: remove the sensitivity line from process.md — less reporting, loses the headline-vs-core check.

**D-A5. Pipeline inputs (PPI, commodities, wages, expectations).**
- A (Recommended): no faithful-track rule; record as hybrid-track candidates only after R-67 passes scoring.md §6e — no library statement supports them as inputs.
- B: add a PPI or commodity leg to R-67 now — adds constants and measures before the current design is tested.
- C: add wage growth as an R-09 confirmation — paraphrased support only (2022-09 NP N), no threshold.

**D-A6. "Inflation relative to what policymakers think" (2021-01, NP, Y).**
- A (Recommended): acquire FOMC SEP projections (2007→) and report the gap (realised core PCE vs SEP median) as display context for R-67 — the only faithful operationalisation of his stated theme; no gate until tested.
- B: no action.

---

# Part B — Labour-market measures

## B1. Library evidence

Search: `(?i)payroll|jobs|employment|unemployment|claims|labor market|labour|wages|Sahm|JOLTS|full employment|hiring|layoff|productiv|slack` (generic "Key claims" headings and "jobs as a money manager" hits excluded).

| Date | File | Rel. | Verb. | Short quote / content | Measure | Implication for rules |
|---|---|---|---|---|---|---|
| 2015-01 (about Q4 2003) | RS/2015-01-18_lost-tree-club-speech.md | NP | N | Staff set the right rate "from data alone": 3–6% vs FF 1% | Unspecified data set; nominal growth 9% cited | R-06 is an interpretation of this exercise |
| 2014-06-19 | DS/2014-06-19_wsj-oped-warsh-asset-rich-income-poor.md | P | Y | "…the sooner businesses can get back to business and labor can get back to work." | Labour broadly | Context, no measure |
| 2018-09-06 | RS/2018-09-06_sokoloff-real-vision-interview.md | NP | N | "If you came down from Mars" FF would be 4–5% given sub-4% unemployment and fiscal stimulus, vs 1.75% | **Unemployment rate level** | Supports UNRATE as the slack term in R-06 (level, not change) |
| 2019-06-03 | DS/2019-06-03_econclub-ny-bessent.md | S | Y | "For the first time in history, we have massive deficits and full employment…" | Full employment (status) | Supports R-63 "deficit at UNRATE < NROU" |
| 2019-06-07 | DS/2019-06-07_cnbc-squawk-box-one-way-bet.md | NP | N | $1T deficit at full employment enabled by the Fed | Full employment | R-63 |
| 2022-09-28 | DS/2022-09-28_delivering-alpha-kernen-transcript.md | NP | N | Inflation rotates into wage settlements | Wages | Persistence (Part A) |
| 2023-06-07 | DS/2023-06-07_bloomberg-invest-sonali-basak.md | S | N | Hard landing held "despite low unemployment" | Unemployment level dismissed as a timing signal | Labour strength not treated as evidence against recession |
| 2024-05-07 | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md | NP | N | 7% deficit at full employment | Full employment | R-63 |
| 2024-11-06 | RS/2024-11-06_nbim-in-good-company-podcast.md | NP | N | Deficit ~7% of GDP at full employment cannot last | Full employment | R-63 |
| 2026-02-27 | DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md | NP | N | **Unemployment and payrolls are the most misleading macro variables because they are lagging.** Macro data used for entries and exits; internals and company mosaics are the main macro inputs | Payrolls, unemployment | Direct statement against payrolls/unemployment as timing or turning-point inputs |
| 2026-02-27 | same | NP | N | A policy response to job losses (printing, universal income) could be inflationary | Job losses (AI) | Scenario only |
| 2026-08-24 | DS/2026-08-24_wsj-oped-let-the-bond-market-speak.md | S | N | Full-employment deficit near 6% of GDP | Full employment | R-63 |

Not found: initial or continuing claims, JOLTS, Sahm rule, temp help, hours, household-vs-establishment discussion, payroll revisions. "Payroll" appears once more only as payroll tax (DS/2013-10-19, fiscal).

Synthesis. Labour data enter his statements in two roles: (i) as a **status level** — "full employment", "sub-4% unemployment" — that conditions policy-error and fiscal judgments (R-06 slack term, R-63 full-employment condition); (ii) as **timing** inputs, which he rejects explicitly: payrolls and unemployment are "the most misleading macro variables because they are lagging" (2026-02-27, NP), and in 2023 he held a recession view despite low unemployment. No statement supports payrolls, claims, JOLTS or the Sahm rule as a signal.

## B2. Current spec use

| Rule | Series | Transform | Params | PIT treatment | Note |
|---|---|---|---|---|---|
| R-06 | `UNRATE_FR` (first release per period, ALFRED 1960-03-15→); `NROU` (CBO, ALFRED 2011-02-02→, latest vintage before, `pre_vintage: usable`) | `b × (NROU − UNRATE)`, b = 1.0 | `policy.taylor_ugap_coef` 1.0 (fixed) | UNRATE first release; NROU quarter containing the UNRATE month; NROU > 2 years old → unknown (`NROU_MAX_AGE_DAYS`) | Before 1960-03-15 no UNRATE vintage → R-06 unknown. RTDSM `ruc` (1965-11→) never reached. Conflict with 2026-02-27 already recorded in process.md R-06 |
| R-63 | `UNRATE_FR`, `NROU` | `UNRATE < NROU` as the "full employment" condition, with deficit/GDP > `fiscal.deficit_gdp_pct` | `fiscal.*` (fixed) | as R-06 | Matches his "deficits at full employment" wording (five statements, §B1) |
| R-09, R-07 | none | — | — | — | Recession prior is inflation-based only |
| R-67 | none | — | — | — | No labour leg |
| Fragility, internals | none | — | — | — | — |

Inconsistencies.

| # | Finding | Effect | Class |
|---|---|---|---|
| L-1 | R-06 uses `UNRATE` first release while `NROU` before 2011-02 is the latest CBO vintage | Look-ahead in the gap term before 2011 (accepted in process.md, flagged in catalogue) | Documented approximation |
| L-2 | process.md R-63 cites no labour statement for the full-employment condition, although five library statements support it | Citation gap only | Documentation |
| L-3 | `PAYEMS` has a vintage store (1955-05-06→, 14,743 rows) but no latest-series file and no catalogue entry; `ICSA`/`CCSA` are in the lake (1967→) but not catalogued, and the `ICSA` vintage store covers only 2025-07→ | Not readable through `AmberLakeSource` | Data |
| L-4 | BLS mirror (`LNS14000000`, `CES0000000001`, `JTS…JOL`, `LNS13327709` U-6, `LNS11300000` participation, `CES0500000002` hours) is 2017→ with no `published_at` | Unusable PIT | Data |

## B3. Free measures inventory

### B3.1 Inventory

| Series | Content | Start | Freq | Release / lag | Revisions | Real-time vintages | In lake | Catalogued | Caveats |
|---|---|---|---|---|---|---|---|---|---|
| `UNRATE` | Unemployment rate (CPS, household) | 1948-01 | M | Employment Situation, usually first Friday of t+1, 08:30 | SA factors revised each January for 5 years; population controls each January (not back-revised) | ALFRED 1960-03-15→ (lake); RTDSM `ruc` 1965-11→ (lake) | Yes + vintages | Yes (`UNRATE`, `UNRATE_FR`) | 1994 CPS redesign; first release vs latest: mean |diff| 0.07 pp, p90 0.20, max 0.40 (1960→, §B3.2) |
| `PAYEMS` | Nonfarm payrolls (CES, establishment) | 1939-01 | M | same release | Two monthly revisions, then annual benchmark (February release, to the prior March; preliminary benchmark announced ~August/September) | ALFRED 1955-05-06→ (lake) | Vintages only | No | Birth–death model; large benchmark revisions around turning points (2008–09; 2024–25 preliminary benchmark) |
| First-release payroll change | `PAYEMS` t minus t−1 within the first vintage containing t | 1955→ | M | — | — | derived from ALFRED | Derivable | No | §B3.2 |
| `ICSA` / `ICNSA` | Initial claims SA / NSA | 1967-01 | W | Thursday 08:30 for week ending prior Saturday | SA factors revised annually (5 years); NSA essentially unrevised | ALFRED `ICSA` *(verify start)*; lake vintages 2025-07→ only | `ICSA` yes; `ICNSA` no | No | Program changes (2020 PUA excluded from ICSA); holiday seasonality |
| `CCSA` / `CCNSA` | Continuing claims | 1967-01 | W | one week later than initial | as ICSA | as ICSA | `CCSA` yes | No | Benefit-duration law changes |
| `JTSJOL` (JOLTS openings), `JTSQUR` (quits) | Job openings, quits | 2000-12 | M | ~5–6 weeks after month end | Monthly + annual benchmark | ALFRED *(verify)* | BLS mirror 2017→ only | No | Short history; response-rate decline after 2020 |
| `SAHMREALTIME` | Sahm rule, real-time (3-month avg UNRATE vs prior 12-month low, computed on each vintage) | 1959-12 *(verify)* | M | with Employment Situation | Real-time by construction (not revised) | Is itself real-time | No | No | Coincident recession indicator, not a lead; 2024 trigger without recession |
| `SAHMCURRENT` | Sahm rule on current vintage | 1949 | M | — | Revised | — | No | No | Look-ahead; not for backtests |
| `CE16OV` / `LNS12000000` | Household employment | 1948 | M | same release | Population-control breaks each January | ALFRED *(verify)* | No | No | Household vs establishment gaps (2023–24 immigration) |
| `TEMPHELPS` | Temporary help services employment | 1990-01 | M | same release | as CES | ALFRED *(verify)* | No | No | Short history; secular decline in share |
| `AWHAETP` / `AWHNONAG` | Average weekly hours, all / production | 2006-03 / 1964-01 | M | same release | as CES | *(verify)* | BLS `CES0500000002` 2017→ only | No | Composition effects |
| `AHETPI`, `CES0500000003`, `ECI*` | Wages | see §A3.1 | | | | | | | Overlap with Part A wages |
| `NROU` | CBO long-term natural rate | 1949 Q | Q | CBO ~Jan/Aug | Re-estimated each vintage | ALFRED 2011-02-02→ (lake) | Yes | Yes | Pre-2011 latest vintage (look-ahead, accepted) |
| SPF `UNRATE` | Forecast unemployment | 1968Q4 | Q | mid-quarter | Never revised | survey vintage | Yes | No | — |

### B3.2 Payroll revision magnitudes (lake ALFRED `PAYEMS`, no labels)

First-release monthly change vs latest-vintage change for the same month (thousands):

| Decade | n | Mean |revision| | p90 |revision| | Mean |change| (latest) | Sign of change flips |
|---|---|---|---|---|---|
| 1960s | 120 | 88 | 171 | 172 | 15.8% |
| 1970s | 120 | 99 | 173 | 222 | 14.2% |
| 1980s | 120 | 93 | 208 | 226 | 5.0% |
| 1990s | 120 | 93 | 184 | 214 | 11.7% |
| 2000s | 120 | 74 | 161 | 186 | 10.8% |
| 2010s | 120 | 49 | 115 | 190 | 1.7% |
| 2020s (to 2026-08) | 78 | 113 | 263 | 668 | 5.1% |

The first print is revised by roughly 40–55% of the typical monthly change; in 2–16% of months the sign flips. Any payroll-based input must use the first release (ALFRED) — latest-vintage payrolls are not usable for backtests.

## B4. Assessment

| Rule | Should use | Reasoning | Change type |
|---|---|---|---|
| R-06 slack term | `UNRATE` first release vs `NROU` vintage (current) | His policy-error statements use the unemployment level ("sub-4% unemployment", 2018) and full employment; UNRATE has the longest vintage history (1960→) and small revisions (p90 0.2 pp, ×b = 1 against a 2 pp band). Payrolls do not give a gap measure; claims have no natural-rate counterpart | None |
| R-63 | `UNRATE < NROU` (current) | Five statements tie his fiscal concern to "deficits at full employment" | Add citations (documentation) |
| R-09 recession prior | No labour input | 2026-02-27: payrolls and unemployment lagging and misleading; 2023: recession view held despite low unemployment. A Sahm-rule or claims confirmation would contradict a stated view and adds a coincident, not leading, signal | None |
| R-67 (hybrid) | No labour leg now | The hybrid track is not bound by fidelity, but the stated rejection of payrolls as timing inputs and the 2024 Sahm false trigger argue against; claims are the only weekly, unrevised (NSA) candidate and would need their own test under §6e | Possible future hybrid candidate |
| R-58 (FCI) | unchanged | NFCI already contains no labour data; his restrictiveness gauge is markets | None |

## B5. Decisions (labour)

**D-B1. R-06 slack measure.**
- A (Recommended): keep `UNRATE` first release vs `NROU` vintage — stated level framing, longest PIT history, small revisions.
- B: payroll-growth gap (first-release `PAYEMS` growth vs trend) — no gap concept in his statements; revisions ~half the monthly change.
- C: Sahm real-time indicator in place of the gap — coincident recession signal, not a slack level.

**D-B2. Labour input for the recession prior (R-09) or a new veto.**
- A (Recommended): none — contradicts 2026-02-27 (payrolls/unemployment lagging, NP) and the 2023 stance.
- B: Sahm real-time ≥ 0.5 as a confirming flag (display only) — useful context in amber, no fidelity role.
- C: initial claims 4-week average rising > X% yoy as an R-09 input — no source, new interpreted constant (cap full).

**D-B3. Labour leg for R-67 (hybrid).**
- A (Recommended): none until R-67 D3 has passed scoring.md §6e — test the registered design first.
- B: claims (NSA, unrevised, weekly, 1967→) as a third component after §6e — the only timely labour series with clean PIT; requires its own pre-registration.

**D-B4. R-63 citation (documentation, next re-registration).**
- A (Recommended): add DS/2019-06-03 (S, Y), DS/2019-06-07 (NP), DS/2024-05-07 (NP), RS/2024-11-06 (NP), DS/2026-08-24 (S) as support for the full-employment condition — anchors an existing interpreted condition in stated text.
- B: leave as is.

---

# Data to acquire (amber lake, with vintages) and catalogue

Priority reflects rule use under the recommended options; all sources are free (FRED/ALFRED, BLS, regional Fed sites, Philadelphia Fed, Federal Reserve Board).

| Priority | Series | Source | Vintages needed | For |
|---|---|---|---|---|
| 1 | Catalogue existing lake series: `PCEPI`, `PCEPILFE`, `T5YIE`, `T10YIE`, `DFII10`, `MICH`, `ICSA`, `CCSA`, `PAYEMS` (vintage view), `philfed\spf\median` (with survey release dates), World Bank CMO (lag rule) | lake | as stored | I-9, L-3 |
| 1 | `CPILFENS` (core CPI NSA, 1957→) | FRED | Not revised; first-release timestamps from the CPI release calendar | D-A2 option C; PIT core yoy pre-1996 |
| 1 | `PCEPI`, `PCEPILFE` full ALFRED vintage history | ALFRED | Yes (start to verify) | D-A3 variant; Fed-target-measure reporting |
| 2 | FOMC SEP medians (core PCE, PCE, unemployment, FF) 2007→; Humphrey-Hawkins central tendencies 1979→ if a free tabulation exists *(verify)* | FRED / Federal Reserve Board | Unrevised; meeting-day 14:00 timestamps | D-A6 ("what policymakers think") |
| 2 | `SAHMREALTIME` | FRED | Real-time by construction | D-B2 option B (display) |
| 2 | `ICNSA`, `CCNSA` (NSA claims) | FRED | Effectively unrevised | D-B3 option B (future) |
| 3 | `PPIACO` (1913→), `PPIFGS` (1947→), `PPIFIS` (2009-11→) | FRED/ALFRED | Yes (4-month revision window) | Hybrid candidate only (D-A5) |
| 3 | `AHETPI` (1964→), `ECIWAG` (1975→ *verify*) | ALFRED | Yes | Wage display / hybrid candidate |
| 3 | `T5YIFR` | FRED | Not revised | Display |
| 3 | `PCETRIM12M159SFRBDAL`, `MEDCPIM158SFRBCLE`, `TRMMEANCPIM158SFRBCLE`, `CORESTICKM159SFRBATL` | FRED | Revised with CPI/PCE; no confirmed vintages — archive going forward | Display only |
| 3 | `JTSJOL`, `TEMPHELPS`, `AWHNONAG`, `CE16OV` | ALFRED | Yes | Display only |
| — | BLS mirror (`bls\series`): add `published_at` from the BLS release schedule, extend history | BLS API | — | I-10, L-4 |

Not proposed: CRB and S&P GSCI histories (not free), Cleveland Fed model expectations as a rule input (history revises).

# Gaps

| Gap | Consequence |
|---|---|
| PCE ALFRED vintage start, Dallas/Cleveland/Atlanta series starts and vintage availability, PPI and AHE ALFRED starts, SAHMREALTIME start: marked *(verify)* | Inventory dates for those rows are unconfirmed |
| Whether BLS published core CPI (ex food and energy) in real time before the 1970s | Affects whether a pre-1975 core series is "available to a contemporary" even when unrevised |
| No primary statement on headline vs core, CPI vs PCE, PPI, expectations, claims, JOLTS | Every choice on these is `interpreted`; library supports headline CPI yoy and UNRATE levels only |
| The 6-month-annualised statement (2024-05-07) is a paraphrase (N) with the series unnamed | R-67 horizon anchor is weak; the measure choice in D-A2 is unanchored |
| Descriptive wedges in §A3.3 use latest vintages | Real-time wedges may differ; direction (CPI above PCE) is stable in every decade |
| Whether R-67 outputs have already been scored under §6e is not visible from the files read (code exists uncommitted; process.md says "not implemented") | If scored, D-A2 is a design change requiring re-registration; if not, it can be folded into the first registration |

# Next steps (PLAN.md)

1. PLAN D.2 (D-2, D-15): add `CPILFENS`, full ALFRED `PCEPI`/`PCEPILFE`, `SAHMREALTIME`, `ICNSA`/`CCNSA` to the lake and catalogue the already-present series listed in "Data to acquire" priority 1; regenerate `spec\data_coverage.md`.
2. PLAN E.2 / pre-registration: owner decisions D-A2, D-A3, D-A4 and D-B4; write the chosen R-67 measure chain, the R-06 core sensitivity (1996-12→) and the R-63 citations into `spec\process.md`; register with `fatpitch.prereg` before the next scoring run.
3. PLAN E3: implement the R-06 core sensitivity and the R-67 measure fix under `record_run`, with fixture tests for the NSA seasonal case (pre-1972 asof → I leg unknown or neutral formula) and the 1996-12-12 boundary; report the CPI–PCE wedge effect on R-06 in the Gate 1 fidelity report.
