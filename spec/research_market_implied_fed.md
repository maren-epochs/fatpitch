# Anticipating Fed turns: market-implied path and inflation momentum (proposed R-67 and an anticipation test)

Research date 2026-10-07. Scope: research only. No engine run, no `fatpitch.versions` run, no gate statistic computed. `cases\`, `cases\HOLDOUT.yaml`, `results\` and `spec\fed_cycles.yaml` were not opened. Only this file was written. Read: `CLAUDE.md`, `PLAN.md` §E.4a–E.7, `spec\process.md` (R-06..R-09, R-14, R-17, R-23, R-66), `spec\registry.yaml` (tunable entries), `spec\data_catalogue.yaml`, `spec\data_coverage.md` (sections 1 and 2.1 only), `spec\scoring.md` §6d summary row, `src\fatpitch\cases\fedcycles.py` (module docstring and function signatures, no label data), the amber lake directory listing and series date ranges.

Owner brief (three messages, merged): (1) the engine should anticipate Fed hikes and cuts before they happen ("futures markets for fed rates are very predictive"); (2) inflation reads are a second anticipation input; (3) anticipation is a new rule family and a new evaluation test, not a modification of R-14.

Reliability codes follow the library front-matter: **P** = `reliability: primary`, **NP** = `near-primary (transcript)`, **S** = `secondary summary`. **Verbatim Y** = the quoted words appear as a quotation in the note's "Notable quotes" or body; **N** = the note paraphrases. Paths are relative to `library\` (`DS` = `discovered_sources\`, `RS` = `reference_sources\`).

## 0. Current state relevant to anticipation

| Item | What it does now | Bearing on anticipation |
|---|---|---|
| R-14 | `policy_direction` = sign of 6-month change in the FF target plus a holdings component | Realised only; by construction it turns after the first move (lag ≥ 0) |
| R-23 (exists) | Market-implied path `MP = DGS2 − FF` (1976→), `DGS1 − FF` before; cuts/hikes priced beyond ±`curve.cut_pricing_bp` (50 bp, **tunable 6/8**); ZQ/SR3 only as live refinement that must reduce to MP | Already a market-implied direction rule, but it feeds R-28 asymmetry and horizon logic, not R-66 and not `policy_direction` |
| R-06 | Taylor u-gap rate; `TG = FF − i*`, too loose/too tight beyond `policy.tg_threshold_pp` (2.0, tunable 2/8) | Stance (level), excluded from R-66 because R-21 reads change, not level |
| R-07, R-08, R-09 | CPI yoy level flags (4.5%, 5%), FF vs CPI veto, recession prior | Level flags conditioned on `policy_direction`; none forecasts a Fed move |
| R-66 | Counts R-14 and the liquidity family into P(easing/neutral/tightening) | No forward-looking family |
| Fed cycle check (§6d) | Detection window first-hike month −3 .. +3, median lead vs `null_fed_direction`, false-alarm share ≤ 20% in easing months | Rewards lead only inside ±3 months and only for tightening cycles; does not score easing turns or false alarms outside easing months |
| Tunable cap | `spec\registry.yaml` lists 8 `tunable: true` ids (liq.m2_ip.spread_pp, policy.tg_threshold_pp, xasset.window_m, fragility.high_percentile, internals.rs_lookback_m, curve.cut_pricing_bp, chart.trend_lookback_w, tier.min_independent_evidence) | Full. Every new constant below is fixed (`tunable: false`) or reuses an existing id |

Finding: the market-implied input already exists as R-23. The gap is not the measure but its role: nothing routes a forward-looking direction into the regime vector or into any test that rewards lead.

## 1. Library evidence

### 1a. Reading the market's expectation of Fed policy

| Date (of statement) | Path | Rel. | Verbatim | Quote / content | Implication |
|---|---|---|---|---|---|
| 1991-12 (about 1987) | DS/1992-XX-XX_new-market-wizards-full-chapter-text.md | P | Y | "The Fed had been tightening since January 1987, and the dollar was tanking, which suggested that the Fed was going to tighten some more." | Anticipated further tightening from a market price (FX), not from rate-futures pricing. Retrospective (4 years) |
| 1991-12 (about 1989) | same | P | N | BoJ tightening "three times as important"; JGBs plummeting while the Nikkei made highs | Bond market moved with/ahead of central-bank tightening and he read it against equities |
| 2009 (about Q4 2000) | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md | NP | N | 300% of fund in 10-year equivalents into 2-year notes; oil and rates spiking, Hyman model earnings −36% vs consensus +18%, FF 6.5% | Anticipated cuts before the market priced them; traded against pricing (first cut Jan 2001) |
| 2014-07-16 | DS/2014-07-16_delivering-alpha-kernen.md | NP | N | "Focus on the rate level more than the first hike." | Weakens "first move" as the sole object; level matters (R-06) |
| 2015-03-02 | DS/2015-03-02_cnbc-closing-bell-kelly-evans.md | NP | N | Expected rate hikes are a reason to short bonds, not stocks; urged 25–50 bp now | Expectation of hikes as a rates trade; disagreed with the Fed's timing (hike came Dec 2015) |
| 2015-11-04 | DS/2015-11-04_nyt-dealbook-conference-sorkin.md | S | N | Forward guidance and short-termism criticised | Market pricing in the guidance era partly echoes the Fed |
| 2018-12-18 | DS/2018-12-18_bloomberg-tv-erik-schatzker.md | S | Y | "it's not inconceivable to me at all that the 2-years are back to 50 to 60 basis points in a couple of years"; warning signs include the "inverted short end" | Front-end inversion read as a warning (internals); his own path far below market pricing |
| 2019-06-07 | DS/2019-06-07_cnbc-squawk-box-one-way-bet.md | NP | Y (one-way-bet quote) / N (numbers) | 2-year at ~2.30% a "one-way bet": ~10 bp downside vs 150–200 bp upside; at ~1.85% the asymmetry was gone | Market pricing is the benchmark for payoff asymmetry (R-23/R-28), not the forecast he adopts |
| 2019-06 (reported 2020) | RS/2020-05-12_economic-club-of-new-york.md | S | N | Fed funds to zero within 18 months | Own path more extreme than pricing |
| 2021-06-10 | DS/2021-06-10_email-to-cnbc-kernen-market-not-speaking.md | S | Y | "The market is not speaking right now." "…until the Fed stops canceling market signals." | Market pricing impaired under QE and forward guidance |
| 2022-06 | DS/2022-06-XX_sohn-2022-john-collison.md; RS/2022-06-10_sohn-2022-collison-conversation.md | NP; S | N | Bond-market signal "corrupted"/"suppressed" by central-bank buying for 10–11 years; it "used to be prescient" | Stated basis for R-17's QE impairment; applies equally to market-implied policy paths |
| 2023-04-24 | DS/2023-04-24_nbim-annual-investment-conference.md | NP | N | 2-year below 4% with FF at 5.25% made owning duration a bet on a hard landing | Reads the 2y–FF gap as "cuts already priced"; no fat pitch when pricing already agrees with his view |
| 2023-10-24 / 2024-05-07 | DS/2023-10-24_robin-hood-paul-tudor-jones.md; DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md | S; NP | N; Y | Massive leveraged long 2-year at ~5.10–5.15%; exited ~4.30%: "Once financial conditions took off, it became very clear that this thing could go either way. So I exited the position." | Anticipated cuts before pricing; exit trigger was FCI, not pricing |
| 2024-10-16 | DS/2024-10-16_bloomberg-tv-sonali-basak.md | NP | Y | "I'm a market animal. Frankly, we've found over the years that markets are better predictors than professors." | Strongest support for market-based inputs; context is judging restrictiveness, not forecasting the next FOMC move |
| 2024-11-06 | RS/2024-11-06_nbim-in-good-company-podcast.md | NP | N | Spring 2021 short of 2-year notes at 15 bp, took most off at ~150 bp | Anticipated hikes about a year before the first hike (Mar 2022) while pricing showed none |
| 2026-02-27 | DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md | NP | Y ("over-rated") | Yield curve as a trade is "over-rated"; Fed "certainly not going to hike and probably going to cut" | Discounts the curve as a trade; his own Fed call was contradicted (hike 2026-09-16, per secondary reporting) |
| 2026-09-10 | DS/2026-09-10_piper-sandler-closed-door-event.md | S | Y | Rate cuts "no longer necessary" | Read from inflation/FCI, six days before a hike |

Synthesis. No statement in the library says he read fed funds futures or bill spreads to forecast the next Fed move. The statements split into two groups. (i) Market prices as information: the 1987 dollar, the 1989 JGB sell-off, "markets are better predictors than professors", the inverted front end in 2018. (ii) Market pricing as the consensus he traded against: 2000, 2018–19, spring 2021, late 2023, each a front-end position whose edge was anticipating a turn the curve had not priced, and 2023-04 where the absence of a gap between his view and pricing meant no trade. The second group is the larger and better documented. Consequence for the spec: market-implied direction is defensible as an anticipation input (it reflects public information early, and "the crowd's right 80% of the time", DS/2026-02-27, Y), but it cannot reproduce his edge; his edge came from inputs that moved before pricing (inflation relative to the Fed's view, financial conditions, earnings models). Under QE and forward guidance he treats the market signal as impaired (2021-06-10, 2022-06).

### 1b. Inflation as a driver or predictor of Fed action

| Date | Path | Rel. | Verbatim | Quote / content | Implication |
|---|---|---|---|---|---|
| 1991-12 (about Q4 1981) | DS/1992-XX-XX_new-market-wizards-full-chapter-text.md | P | Y | "We loved the long bond position because it was yielding 15 percent, the Fed was extremely tight, and inflation was already coming down sharply." | Inflation momentum (falling) plus tight stance → anticipated easing. Direct support for a momentum signal |
| 2012-04 | DS/2012-04-XX_grants-spring-conference-jim-grant.md | S | Y | "The Fed chairman will always find a way to be dovish"; high oil with shrinking GDP would bring QE3 | Reaction function biased to ease; inflation-driven tightening signals will lead the Fed by a long, variable margin |
| 2017-12-12 | DS/2017-12-12_cnbc-closing-bell-kelly-evans.md | NP | Y | "The 2% inflation target has sort of become a religion initiated by the professors." Low innovation-driven inflation should not trigger easing | Inflation vs 2% is not his own criterion; but it is the Fed's, so it is a fair input for predicting the Fed |
| 2018-05-03 | DS/2018-05-03_manhattan-institute-hamilton-award-speech.md | P | Y | "…the Fed has not only kept interest rates below inflation but have accumulated an unprecedented $4.5 trillion…" | Fed lagging inflation (behind the curve) |
| 2019-06-07 | DS/2019-06-07_cnbc-squawk-box-one-way-bet.md | NP | N | Mismeasured productivity means true inflation is lower; 2% target "for all seasons" wrong | Same as 2017 |
| 2021-01 | DS/2021-01-XX_talks-at-gs-great-investors-pasquariello.md | NP | Y | "my overriding theme is inflation relative to what policymakers think." | Core statement: the anticipation edge is the gap between inflation and the Fed's stated view |
| 2021-06-10 | DS/2021-06-10_email-to-cnbc-kernen-market-not-speaking.md | S | N | Hot May 2021 CPI ignored by markets under the "transitory" framing | Inflation momentum led both the Fed and market pricing in 2021 |
| 2022-06 | DS/2022-06-XX_sohn-2022-john-collison.md | NP | Y | "Once inflation gets above 5%, it's never come down unless Fed funds have gotten above the CPI." | Level rule (R-08), not a direction forecast |
| 2022-09-28 | DS/2022-09-28_delivering-alpha-kernen-transcript.md | NP | Y / N | "You don't cure inflation with an inflationary act." "Ridiculous theory of transitory"; inflation rotates into wages | Fed behind the curve for 9–10 months after inflation was evident; wages as a persistence channel |
| 2024-05-07 | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md | NP | N / Y | Six-month annualised inflation had turned up; "When you need to raise rates, raise rates. When you need to cut them, cut them." | Explicit use of a 6-month annualised momentum measure; Fed signalled cuts anyway (cut Sep 2024) |
| 2024-10-16 | DS/2024-10-16_bloomberg-tv-sonali-basak.md | NP | N | Risk of re-acceleration in 2025; easing into a melt-up risks a 1970s second wave | Momentum read, not level |
| 2024-11-06 | RS/2024-11-06_nbim-in-good-company-podcast.md | NP | N | 1970s pattern: inflation fell ~8%→3% then re-accelerated; analog bottom "right about now" | Turning point in inflation momentum as the object |
| 2026-02-27 | DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md | NP | N | Fed cutting into a booming economy plus commodities could drive inflation | Inflation risk as a hedge case, not a Fed forecast |
| 2026-08-24 | DS/2026-08-24_wsj-oped-let-the-bond-market-speak.md | S | N | Inflation above target since 2021 | Level context |

Synthesis. His inflation statements are mostly about what the Fed should do (policy-error identification), and he repeatedly records the Fed not doing it (2017–18, 2021, 2024, 2026). One retrospective (Q4 1981) and one contemporaneous (2024-05) statement use inflation momentum directly; the 2021 statement makes inflation relative to the Fed's view the governing theme. Consequence: inflation momentum is a stated driver of his anticipation, but as a forecast of actual Fed action it carries a documented failure mode: a dovish reaction function lets the Fed lag inflation by many months (2012-04 quote; 2021). The signal should be expected to lead tightening by more than market pricing and to produce more false alarms.

## 2. How existing rules use inflation, and whether momentum is distinct from R-06

| Rule | Inflation input | Object | In R-66 |
|---|---|---|---|
| R-06 | CPI yoy (core as sensitivity) inside `i*` | Stance: FF minus Taylor rate (level) | No (level; R-21) |
| R-07 | CPI yoy > 4.5% in trailing window while tightening | Recession prior | No (takes `policy_direction` as input) |
| R-08 | CPI yoy > 5% and FF < CPI | Veto flag | No (veto) |
| R-09 | CPI yoy peak > 5% while tightening | Recession prior | No (circular) |

Assessment. An inflation-momentum signal, e.g. core CPI 6-month annualised minus its own 12-month rate, is a change measure, not a level. In Taylor terms `Δi* = (1 + a)·Δπ + b·Δgap`, so momentum is the direction in which the Fed's own benchmark rate is moving; R-06 reads where FF sits relative to that benchmark. The two are distinct objects: R-06 can say "too loose" for years (2014–2018 in his statements) while momentum is flat, and momentum can turn while R-06 has not crossed its 2 pp band. The R-66 exclusion argument (stance, not direction) does not apply to momentum. Overlap to state: R-06, R-07, R-08 and a momentum rule all read CPI; counting momentum as a separate evidence family is defensible only because it uses a different transformation (second difference vs level) and a different horizon. Legitimate as an anticipation input: yes, tagged `interpreted` with stated support (NMW 1981, GS 2021, CNBC 2024-05).

## 3. Free data inventory

PIT column: daily H.15 series are stamped next business day by the lake (`first_release`/`lag_rule`); "revised" means values change after first publication.

### 3a. Market-implied path inputs

| Series | Content | Start | Freq | PIT / revisions | In lake |
|---|---|---|---|---|---|
| DFF | Effective FF | 1954-07-01 | D | Next business day; not revised (rare corrections) | Yes (`fred/series/DFF`) |
| FEDFUNDS | Effective FF monthly average | 1954-07 | M | First release; not revised | Yes |
| DFEDTAR | FF target (point) | 1982-09-27 | D | lag_rule; target known 14:00 ET decision day (post-1994); pre-1994 changes were not announced and inferred by the market | Yes |
| DFEDTARU / DFEDTARL | Target range | 2008-12-16 | D | First release | Yes |
| Pre-1982 target | Intended FF rate 1974–79 (Cook–Hahn 1989; Rudebusch 1995 tables) | 1974 | event | Reconstructed ex post | No — gap (paper tables only) |
| DTB3 | 3-month bill, secondary market, discount basis | 1954-01-04 | D | Next business day; not revised | Yes (not in catalogue) |
| DTB6 | 6-month bill, discount basis | 1958-12-09 | D | Same | Yes (not in catalogue) |
| TB3MS / TB6MS | Monthly averages | 1934-01 / 1958-12 | M | Monthly average embeds intra-month data; stamp at month end + 1 day | TB3MS yes; TB6MS no (FRED, free) |
| DGS3MO | 3-month CMT | 1981-09-01 | D | Next business day | Yes |
| DGS1 | 1-year CMT | 1962-01-02 | D | Same | Yes |
| DGS2 | 2-year CMT | 1976-06-01 | D | Same | Yes |
| ZQ (30-day FF futures, CBOT/CME) | Settlement prices per contract | 1988-10-03 launch | D | Same-day settle | Live contracts only: `massive_futures/sessions/ZQ*` 14 contracts, history from 2025-09 (ZQZ6 first row 2025-09-03). No free full history located |
| SR3 (3-month SOFR futures) | Settlements | 2018-05 launch | D | Same-day settle | Live contracts only (`massive_futures/sessions/SR3*`, 14 contracts) |
| Eurodollar futures (GE) | 3-month LIBOR futures | 1981-12 launch, delisted 2023 | D | Same-day | No; no free history located |
| IBKR expired futures | Historical bars | — | D | API serves expired futures only up to 2 years after expiration ([IBKR docs](https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data)) | `ibkr/bars_daily` has no ZQ or SR3 root; would yield ~2024→ at most |
| CME settlement archives / FedWatch | Daily settles; FedWatch probabilities | — | D | Current and recent only free; deep history is a paid product (DataMine) | No — not proposed (paid) |
| Barchart / Investing.com / stooq | Continuous FF futures | unverified | D | Continuous roll, unknown adjustment; terms of use restrict scraping; coverage not verified | No — not verified |
| Atlanta Fed Market Probability Tracker | SOFR-options-implied distribution of 3-month SOFR path | History start not stated on the page; the web view compares the prior six weeks ([Atlanta Fed](https://www.atlantafed.org/cenfis/market-probability-tracker)) | D | Previous-day data | No; SOFR-based, so ≤ 2018 at best |
| NY Fed Survey of Primary Dealers / Market Participants | Modal and mean FF path expectations | SPD ~2011, SMP 2014-12 (from memory, unverified) | per FOMC | Published ~3 weeks after each FOMC meeting | No (lake `nyfed/` holds only `nowcast.json`) |
| Kim–Wright term premium (FRED THREEFYTP1..10) | Model term premium by maturity | 1990 | D/W | Model refit; history revises | No |
| ACM term premium (NY Fed) | Term premium 1–10y | 1961-06 | D/M | Refit monthly; revised | No |
| GSW zero curve | Fed zero/par/forward curve | 1961 at source | D | Refit | Lake `fed/gsw.parquet` holds only 60 rows (2026-07→); gap |
| COT_ZQ / COT_SR3 | CFTC positioning | 1988-10 / 2018-07 | W | Friday 15:30 ET | Yes (positioning, not pricing) |

### 3b. Inflation inputs

| Series | Content | Start | Freq | PIT / revisions | In lake |
|---|---|---|---|---|---|
| CPIAUCSL | Headline CPI SA | 1947 | M | Released ~mid-month 08:30; SA factors revised each Feb; ALFRED vintages from 1972-07-21 | Yes, with vintages |
| CPIAUCNS | Headline CPI NSA | 1913 | M | Not revised | Yes |
| CPILFESL | Core CPI SA | 1957-01 | M | Revised (SA); ALFRED vintage start not checked | **Missing** (catalogue: gap) |
| CPILFENS | Core CPI NSA | 1957-01 | M | Not revised; needs own seasonal handling (12-month and 6-month-over-same-6-months avoid SA) | No |
| PCEPILFE | Core PCE price index | 1959-01 | M | ~4 weeks after month end; heavily revised (annual and comprehensive revisions) | Yes (latest); vintage store only 76 rows from 2024-12 — effectively no history |
| PCEPI | Headline PCE | 1959-01 | M | Same | Yes (latest) |
| T5YIE / T10YIE | TIPS breakevens | 2003-01-02 | D | Next day; not revised | Yes (not in catalogue) |
| DFII10 | 10y TIPS real yield | 2003-01-02 | D | Next day | Yes |
| EXPINF1YR / EXPINF10YR | Cleveland Fed model expectations | 1982-01 | M | Model re-estimated each release; history revises | Yes (latest only) |
| MICH | Michigan 1-year expected inflation (median) | 1978-01 | M | Preliminary mid-month, final end-month; not revised after final | Yes |
| SPF median (`philfed/spf/median`) | Professional forecasts (CPI from 1981Q3) | 1968Q4 | Q | Mid-quarter release; never revised | Yes |
| AHETPI | Avg hourly earnings, production and nonsupervisory | 1964-01 | M | First Friday; revised two months; ALFRED vintages | No |
| CES0500000003 | AHE, all private | 2006-03 | M | Same | No |

## 4. Literature (brief)

| Study | Finding relevant here |
|---|---|
| Krueger and Kuttner (1996), *J. Futures Markets* 16(8) | FF futures were an efficient predictor of the target over 1989–1994; little additional information in other variables |
| Kuttner (2001), *J. Monetary Economics* 47(3) | Uses the change in the current-month FF future to split target changes into expected and surprise parts; bill and note yields respond strongly to surprises and little to anticipated changes, i.e. bills already price anticipated moves |
| Söderström (2001), *J. Futures Markets* 21(4) | FF futures predict the next-meeting change well from the mid-1990s; poorer before 1994 when changes were not announced |
| Lange, Sack and Whitesell (2003), *J. Money, Credit and Banking* 35(6) | Anticipation of policy improved after 1994 (statements, gradualism); market rates move ahead of target changes by several months in the 1990s |
| Gürkaynak, Sack and Swanson (2007), *J. Business & Economic Statistics* 25(2) | FF futures dominate term FF loans, eurodollar futures, bills and commercial paper "in forecasting monetary policy at horizons out to six months"; at longer horizons eurodollar futures and other instruments perform similarly; bills are weakest, attributed to supply and liquidity effects; all beat time-series models ([FRBSF WP](https://www.frbsf.org/research-and-insights/publications/working-papers/2006/01/market-based-measures-of-monetary-policy-expectations/)) |
| Piazzesi and Swanson (2008), *J. Monetary Economics* 55(4) | FF futures embed a positive, countercyclical risk premium, rising with horizon (order of a few bp per month of horizon); removing it improves forecasts; implies a hike bias in raw futures and in bills/2y |
| Mankiw and Miron (1986), *QJE* 101(2); Rudebusch (1995), *J. Monetary Economics* 35(2) | After the Fed's founding, the term spread lost power to predict short-rate changes; Rudebusch shows target changes are predictable at horizons of weeks to ~3 months and poorly beyond. Implies short anticipation leads pre-1990s for any market-implied design |
| Kim and Wright (2005), FEDS 2005-33; Adrian, Crump and Moench (2013), *J. Financial Economics* 110(1) | Term premia in 2-year yields were large and positive in the 1980s (order of 50–100 bp) and near zero or negative after 2010; a raw `2y − FF` sign is biased toward "hikes priced" in the 1980s |

Closest free proxy to futures. At the 3–6 month horizon that matters for the next move, the 6-month bill against the 3-month bill (or against FF) is the closest free, long-history proxy; GSS rank bills last among market instruments, mainly because of bill-specific supply and convenience effects, which a bill-vs-bill spread partly nets out. The 2-year note is a 0–24 month average path plus a material term premium; it is a weaker proxy for the next move and a better one for the cumulative cycle. The 1-year CMT (1962→) sits between. No free source located for FF futures history before 2024 (IBKR two-year limit); futures are a live-only refinement, as R-23 already says.

Note on all market measures: they anticipate well when the Fed communicates (1994→, strongly 2003→ with forward guidance). In those eras the signal partly echoes the Fed's own guidance, which is the mechanism he criticises (2015-11-04, 2024-05-07, 2024-11-06); when the Fed is itself behind the curve (2021) the market signal lags with it.

## 5. Proposed rule family R-67 "Anticipated policy turn" — `interpreted`

Separate from R-14 (realised direction). Output per US date: `anticipated_direction ∈ {easing, neutral, tightening, unknown}`, `onset_date` (first date of the current uninterrupted run of that direction), `lead_age_m` (months since onset), and `component` (which inputs voted). Evaluated at month ends for the test (section 6); computed daily where inputs are daily.

### 5a. Components

**M — market-implied path (bill forward).** `M_bp = 2 × (DTB6 − DTB3) × 100`, 20-trading-day mean. Plain words: the 3-month bill rate implied 3 months ahead minus today's 3-month bill rate, i.e. the move the bill market prices over the next quarter. Both legs are bills on the discount basis, so the common bill convenience yield and the discount-vs-yield basis largely cancel; FF does not enter, so 1979–82 FF volatility and pre-1982 target gaps do not matter.
- `tightening` if `M_bp > +25`; `easing` if `M_bp < −25`; else neutral.
- Era coverage: 1958-12 → (one consistent series across all eras; no splice).
- Live refinement: where ZQ/SR3 settles exist (amber live tab), the futures-implied change over the same 3–6 month window replaces M, with the R-23 rule that it must reduce to the bill version when absent; the report states which variant was used.

**I — inflation momentum.** `I_pp = π6 − π12`, where `π6` = 6-month annualised change and `π12` = 12-month change of core CPI (first-release vintage as of `asof`); headline CPI vintage (`CPIAUCSL`, ALFRED 1972-07→; `CPIAUCNS` before) until core is acquired, matching R-06's core-as-sensitivity convention.
- `tightening` if `I_pp > +0.5` and `π6 > policy.taylor_pi_target_pct` (reused, 2.0; not a new tunable); `easing` if `I_pp < −0.5`; else neutral. At DFF < `antic.zlb_ff_pct` an easing reading is set to neutral, as for M.
- Era coverage: headline 1913→ (NSA); core 1957→ once acquired.

### 5b. Fixed constants (cap of 8 is full; none tunable)

| Constant | Value | Argument |
|---|---|---|
| `antic.band_bp` | 25 | One standard Fed move since the late 1980s; a priced move smaller than one step is not a priced move. Also above the typical 6-month-bill term premium (Piazzesi–Swanson order of magnitude), so pure premium does not trip it |
| `antic.horizon` | 3m→6m bill forward | Matches the horizon at which market instruments forecast policy (GSS 2007: out to 6 months) and Rudebusch's predictability window |
| `antic.smooth_d` | 20 trading days | Removes bill-auction, month-end and tax-date noise without adding more than ~2 weeks of lag; one calendar month is the evaluation grain |
| `antic.zlb_ff_pct` | 0.25 | When DFF < 0.25, cuts are not available; an `easing` M reading is set to neutral (hike readings stand). Matches the 0–25 bp floor of 2008-12 → 2015-12 and 2020-03 → 2022-03 |
| `antic.infl_short_m` / `antic.infl_long_m` | 6 / 12 | 6-month annualised is the measure he cited (DS/2024-05-07, N); 12 months is the CPI convention used by R-07..R-09 |
| `antic.infl_band_pp` | 0.5 | Two typical monthly core-CPI surprises (0.1 pp/month ≈ 1.2 pp annualised over one month, ~0.4–0.6 pp over six); smaller gaps are within first-release noise and SA revision range |

Tag: all `interpreted`. Stated support: §1a (markets as predictors, 2024-10-16; crowd right 80%, 2026-02-27) for M; §1b (NMW 1981, GS 2021, CNBC 2024-05) for I. No primary statement gives any of the numbers.

### 5c. Candidate designs

| Id | Plain words | Formula | Era coverage | Main failure modes | Conflicts with his statements |
|---|---|---|---|---|---|
| **D1 Bill-forward only** | Direction the bill market prices for the next quarter | `R67 = M` | 1959→ | Flight to quality and bill scarcity (Aug 2007, late 2008, 1998, 2020-03): 3-month bills collapse more than 6-month → spurious **hike** reading in the forward; debt-ceiling episodes (2011, 2013, 2023) distort specific bill maturities in either direction; pre-1994 short leads (Rudebusch); Volcker 1979–82 bill volatility | Treats pricing as forecast, while his record is trading against pricing; impaired under QE/FG (2021-06-10, 2022-06) |
| **D2 2y − FF (R-23 reuse)** | Cumulative path priced over two years | `MP = DGS2 − FF` (DGS1 − FF 1962–76), band `curve.cut_pricing_bp` (existing tunable, 50) | 1962→ | 1980s term premium (50–100 bp) → persistent hike readings; 2y responds to cycle end-points as much as to the next move; FF 1979–82 noise | Same as D1; additionally 2026-02-27 "yield curve over-rated" (as a trade) |
| **D3 Market first, inflation as confirmation and fallback** | Market sets the direction; inflation confirms tightening, breaks ties, and is the sole input where no bill data exist | If `M ≠ neutral`: `R67 = M`, except `M = tightening` with `I = easing` → neutral (flight-to-quality/scarcity guard: a priced hike against decelerating inflation is suspect). If `M = neutral` or unknown: `R67 = I` only when `I` has held for ≥ 2 consecutive month ends, else neutral | 1959→ (M+I); pre-1959 I only (headline NSA) | Inflation leg: dovish reaction function → long leads and false hike alarms (2004-05 is fine; 2017–18, 2021 long leads); supply shocks (oil 1973, 1979, 1990, 2008) move headline; first-release noise | Inflation-as-forecast conflicts with his own record that the Fed often ignores inflation ("always find a way to be dovish", 2012) — mitigated because I only acts where the market is silent |
| **D4 Two-family vote (M and I as separate families)** | Both inputs vote; agreement strong, disagreement neutral | `R67 = M` if `M = I`; `M` if `I` neutral; `I` if `M` neutral; neutral if opposed | 1959→ | Most false-alarm-prone where I fires alone (2021-type: correct but early); opposed signals frequent around inflation peaks (market prices cuts while inflation still high, e.g. 2007, 2023) → neutral during the turns that matter | Gives inflation momentum equal weight to pricing; no statement weights them |

Guard considered and not adopted: a credit-stress guard (BAA − DGS10 widening) to suppress hike readings during flight to quality. It would add a third input with its own constants and overlap R-17; D3's inflation guard covers the same mechanism with an input already in the rule.

### 5d. Role options for R-67

| Option | Mechanism | Effect on existing gates | Assessment |
|---|---|---|---|
| A. Pre-turn warning flag only (recommended first) | R-67 emits `anticipated_turn` when `anticipated_direction ≠ R-14 class` (e.g. R-14 easing/neutral, R-67 tightening); consumed by premise monitoring (step 6, premise ledger) to mark easing-dependent theses at risk; no change to the regime vector | Gate 1 and Fed cycle check unchanged; scored only by the new anticipation test (section 6) | Cleanest: anticipation is measured on its own terms; no risk of degrading registered results |
| B. Separate voter in R-66 | R-67 becomes a third US family with unit weight | Changes P vectors: with three families, R-14 + liquidity agreement against R-67 → 0.5/0.33/0.17; Fed cycle check (b') leads improve, (c) false alarms likely worsen | A design change to a registered rule; re-registration and a new report required (CLAUDE.md pre-registration rule) |
| C. Both | Flag always; voter only after the flag passes the anticipation test | As B, staged | Recommended path if the owner wants anticipation in the regime vector |
| D. Tie-breaker only | R-67 decides R-66 ties instead of R-14 | Small change; ties occur only when R-14 and liquidity disagree | Low impact; does not deliver lead when the two backward families agree |

## 6. New evaluation: Fed anticipation test

Purpose: measure anticipation itself — does the signal point to the coming move before the first move, by how many months, and at what false-alarm cost. Separate from the Fed cycle check (§6d), which rewards detection inside ±3 months of the first hike. Pre-register this section (with section 5 constants) before any computation; no constant in sections 5–6 may be changed after the first run without re-registration.

### 6a. Label fields required (from the existing Fed answer key; not opened here)

| Field | Content | Source in existing machinery |
|---|---|---|
| `cycle.direction` | tightening / easing | Rate cycles built by `fedcycles.build_cycles` |
| `cycle.first_move` | Date of the first change (1982-09-27 →: FOMC/target change date); month only before 1982-09 (turning-point month + 1) | Same |
| `cycle.last_move` | Date (or month) of the last change | Same |
| `cycle.precision` | `day` or `month` | Derived from the splice dates |
| All target-change events | Date and sign of every change (for the false-alarm horizon) | `target_events` on DFEDTAR/DFEDTARU; FEDFUNDS turning points before 1982-09 |
| QT periods | Not used for the rate-turn test (balance-sheet anticipation is out of scope; reported separately if wanted) | `QT_PERIODS` |

### 6b. Definitions

- Evaluation grain: month-end signal values `s(m)` computed point-in-time at 16:00 ET on the last trading day of month m. The last eligible month-end for a turn is the one before the month of the first move (any month-end in the decision month falls after the decision). A supplementary daily variant (1994→, last trading day before the decision date) is reported, not gated.
- Anticipation window for turn k: month-ends from `W_start = max(first_move_k − 12 months, last_move_{k−1} + 1 month)` to `W_end` = last eligible month-end before `first_move_k`. The opening at the previous cycle's last move stops a hike reading carried over from the previous hiking cycle from counting.
- Hit: `s(W_end) = direction_k`. Onset `O_k` = first month-end of the uninterrupted run of `direction_k` ending at `W_end` (truncated at `W_start`). Lead `L_k = months(O_k → first_move month)`, 1..12. Miss: `s(W_end) ≠ direction_k`, lead 0. Unknown at `W_end`: turn reported as not evaluable, not a miss (unknown never counts as a fail) and excluded from denominators; the count of not-evaluable turns is reported.
- False-alarm month: a month-end m with `s(m) = d ∈ {tightening, easing}` such that no target change of direction d occurs in the following 6 months (m, m + 6]. Rate: false-alarm months per year of evaluated months. Episode version also reported: maximal runs of `s = d` with no d-direction change during the run or within 3 months after it; false episodes per year.
- Strata: tightening turns and easing turns separately; eras 1959–1981 (month precision, reserve/turning-point labels), 1982–1993 (unannounced targets), 1994–2008 (announced), 2009→ (ZLB and guidance). Pre-1970 turns exist only if the answer key is extended (current key starts 1970-01; gap).

### 6c. References (each run through the same scorer)

| Reference | Definition | Expected behaviour (by construction, not computed) |
|---|---|---|
| `null_fed_direction` (realised FF change) | Existing null | Turns only after a move; lead ≤ 0 → hit only via carry-over, blocked by the window rule; floor |
| `null_always_easing` | Constant easing (as `null_always_risk_on`) | Every easing turn hit with maximum lead; every tightening turn missed; false-alarm months high |
| `naive_2y_ff` | R-23 sign rule `DGS2 − FF` beyond ±50 bp (DGS1 − FF before 1976), no smoothing, no guards | The market-based benchmark R-67 must beat; tests whether the bill forward and guards add anything |
| `naive_bill_ff` | `DTB6 − DFF` beyond ±25 bp (bond-equivalent conversion not applied) | Second market benchmark; carries the bill convenience-yield bias (persistent easing readings) |
| R-14 output | Current rule | Same as realised FF change plus holdings |

### 6d. Scoring and pass rule (fixed)

Metrics per stratum: hit rate `H`, median lead over hits `L̃`, false-alarm months per year `FA`.

R-67 passes if all hold on the full sample, computed separately for tightening and easing turns:
1. `H ≥ 0.6` and `L̃ ≥ 1` month. Argument: the literature supports market anticipation of most moves at 1–3 months after 1994 and weaker anticipation before; 0.6 demands better than a coin flip across eras without requiring post-1994 accuracy in the 1970s.
2. Against `naive_2y_ff`: `H ≥ H_naive` and `L̃ ≥ L̃_naive`, and `FA ≤ FA_naive + 1.0` per year (a longer lead may cost at most one extra false-alarm month per year).
3. `FA ≤ 3.0` per year (a quarter of months).
4. No era stratum with evaluable turns has `H = 0`.

Reported, not gated: per-turn table (turn, onset, lead, component that voted), per-era metrics, the daily-variant lead in days for 1994→, and the always-easing and realised-change references. Unknown inputs never count as misses or false alarms.

Interaction with existing checks. Under role A, Gate 1 and the Fed cycle check are untouched. Under role B or C, the Fed cycle check is re-run as registered; its (b′) median-lead criterion will register R-67's effect, and its (c) false-alarm share is the cost check. The anticipation test does not use `cases\` and does not read case targets; it uses the Fed answer key only, like §6d.

## 7. Expected behaviour from public history (qualitative; not computed against any label)

| Episode | D1 bill forward | Inflation momentum (I) | Comment |
|---|---|---|---|
| 1994-02 first hike | Bills steepened in late 1993 → hike reading 1–3 months ahead (approximate recollection) | Core flat/declining → neutral | Market leads; I silent (pre-emptive Fed) |
| 2001-01 first cut | 6m below 3m from ~Nov 2000 → easing reading 1–2 months ahead | Rising headline (oil) → tightening | D3 gives easing (market leads); D4 neutral — D4 misses his signature 2000 trade |
| 2004-06 first hike | Forward rose from ~Apr 2004 → 2–3 months | Core turned up early 2004 → tightening | Agreement |
| 2007-09 first cut | Aug 2007 flight to quality: 3m bills collapse → forward steepens → **spurious hike reading** in D1 | Headline decelerating, core flat → neutral/easing | D3 guard neutralises; D1 fails here |
| 2015-12 liftoff | ZLB; forward rises in autumn 2015 → hike reading 1–2 months | Core firm → tightening for long stretches 2012–2015 | I alone would be a multi-year false alarm |
| 2019-07 first cut | 6m below 3m from ~May 2019 → easing 2 months | Flat → neutral | Market leads |
| 2022-03 first hike | 6m bill above 3m by ~Dec 2021 → 3 months | Core 6m annualised accelerating from ~Apr 2021 → ~11 months | I leads by far (his spring-2021 2y short), at the cost of a long early run |

These are approximate recollections of the public record for design reasoning, not measurements. The test in section 6 is the measurement.

## 8. Recommendation

Adopt **D3 (market first, inflation as confirmation and fallback)** as R-67, with role **A (pre-turn warning flag)** now and **C (voter after passing the anticipation test)** as the staged path. Reasons: (i) the bill forward gives one unspliced series 1959→ at the horizon where market instruments forecast best, with no new tunable; (ii) the inflation leg is the input he cites for anticipating turns before pricing (NMW 1981; GS 2021 "inflation relative to what policymakers think"; CNBC 2024 six-month annualised) and it supplies the guard against the bill market's worst failure (flight to quality producing a false hike reading); (iii) keeping inflation subordinate to pricing respects his record that the Fed often ignores inflation, which would otherwise produce long false-alarm runs; (iv) role A keeps registered gates intact and measures anticipation on its own terms.

Not recommended: D2 as the primary (term-premium bias in the 1980s, weak next-move horizon), D4 (neutral at the turns that matter when inflation and pricing disagree).

## 9. Gaps

| Gap | Consequence |
|---|---|
| No free FF futures history before ~2024 (IBKR two-year limit; CME history paid; Barchart/Investing/stooq not verified) | Futures are a live-only refinement; backtests use bills |
| `CPILFESL` not in the lake; its ALFRED vintage start not checked | Inflation leg runs on headline vintages until core is fetched; oil shocks contaminate headline |
| `PCEPILFE` vintage store covers only 2024-12 → | Core PCE (the Fed's target measure since 2012) unusable point-in-time for history |
| `DTB3`, `DTB6`, `T5YIE`, `T10YIE`, `MICH`, `EXPINF*`, `PCEPILFE` are in the lake but not in `spec\data_catalogue.yaml` | Must be catalogued before any rule can read them through `AmberLakeSource` |
| No pre-1982 target series in the lake; current answer key starts 1970-01 | Turns 1959–1969 cannot be scored; 1970–1982 scored at month precision |
| Term-premium series (Kim–Wright, ACM) not in the lake and revised | Cannot be used point-in-time; diagnostic only |
| NY Fed dealer survey start dates from memory, unverified | Not used in any design |
| Atlanta Fed tracker history start not published on its page | Not used |
| The constants in 5b are argued, not fitted | By design (cap full); sensitivity can be reported, not tuned |
| Section 7 values are recollections | Must not be cited as results |

## 10. Next steps (tied to PLAN.md)

1. PLAN D.2 / E.2: add `DTB3`, `DTB6`, `CPILFESL` (with ALFRED vintages) and `TB6MS` to `spec\data_catalogue.yaml` and the lake, with PIT methods as in section 3, and regenerate `spec\data_coverage.md`.
2. PLAN E.2 / pre-registration: owner decision on R-67 design (D1–D4) and role (A–D); then write R-67 into `spec\process.md`, the six fixed constants into `spec\registry.yaml` (`tunable: false`), and the anticipation test into `spec\scoring.md` as §6e, and register with `fatpitch.prereg` before any run.
3. PLAN E3: implement R-67 in step 1 and the anticipation scorer beside `fatpitch.cases.fedcycles` (reusing its cycle builder and month utilities), with fixture tests for window opening, carry-over blocking, unknown handling and false-alarm counting; run once through `record_run`.
