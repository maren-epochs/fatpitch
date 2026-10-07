# Data practices of systematic and macro managers — implications for Fat Pitch (free data only)

Date: 2026-10-06. Scope: how elite quant/macro managers and the academic work they publish acquire, construct, clean and extend market and macro data; translated into recommendations for amber (data lake) and `fatpitch` (engine). Project context: `PLAN.md` §0 and §D, `spec\process.md` §0.

Evidence tags used throughout:

| Tag | Meaning |
|---|---|
| **[D]** | Documented practice: stated in a paper, firm publication, official documentation, court record or interview at the cited URL (text read this session unless noted) |
| **[I]** | Inference or design recommendation by this report; not stated by the cited source |
| **[G]** | Gap: searched for, not found or not verifiable this session |

---

## Executive summary

1. Every long-history backtest published by AQR and Man AHL uses the same splice rule: futures/forwards when they exist; before that, cash index returns minus the local short rate, bond returns scaled to constant duration, and FX spot plus the interest differential. [D] Hurst-Ooi-Pedersen ([AQR via trendfollowing.com](https://www.trendfollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf)); Hamill-Rattray-van Hemert ([Man AHL](https://static.twentyoverten.com/593e8a9e7299b471eaecf644/rJ3CvIT7f/Trend-Following-Equity-and-Bond-Crisis-Alpha.pdf)). The same recipes can be built from free inputs (FRED/GSW yields, FRED/ECB FX, OECD/BIS short rates, French/Shiller equity).
2. Most pre-1990 history at funds comes from paid Global Financial Data (GFD) and hand-transcribed exchange records. [D] ([Ilmanen et al. 2021](https://www.aqr.com/-/media/AQR/Documents/Journal-Articles/JOIM_How-Do-Factor-Premia-Vary-Over-Time.pdf)). Free substitutes exist and are close: Swinkels' FRED-yield bond returns reach R² 0.996 against GFD over 1962–2018. [D] ([Swinkels 2019](https://repub.eur.nl/pub/117405/Swinkels-2019-Data.pdf)).
3. AQR publishes free monthly series (TSMOM factors, VME, Century of Factor Premia, Commodities for the Long Run back to 1877). [D] ([AQR datasets](https://www.aqr.com/Insights/Datasets/Century-of-Factor-Premia-Monthly), [Commodities LR](https://www.aqr.com/Insights/Datasets/Commodities-for-the-Long-Run-Index-Level-Data-Monthly)). Fat Pitch can use them as targets to check its own proxies against.
4. Revised macro data inflate backtests. Ghysels-Horan-Moench find that revisions account for a sizeable share of macro predictability of Treasury returns. [D] ([NY Fed SR581](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr581.pdf)). Compustat restandardization changes published anomaly returns. [D] ([Lyle-Siano-Yohn 2024](https://som.yale.edu/sites/default/files/2024-07/Re-Standardized%20Financial%20Statement%20Data.pdf)).
5. ALFRED alone is not a sufficient point-in-time spine. Its release dates fall back to "the date the series first appeared in FRED" when the source date is unknown. [D] ([ALFRED help](https://alfred.stlouisfed.org/help)). Other free vintage sources fill gaps: Philadelphia Fed RTDSM (vintages from Nov 1965), Dallas Fed OECD real-time (1962–1998) plus OECD ORDRD (1999→), Tealbook (5-year lag) and SPF (1968→). [D].
6. The funds store data bitemporally: valid time (the period a value describes) and knowledge time (when it was known), held in an immutable, versioned store. Man's ArcticDB "time travel" exists so that vendor restatements can be undone back to what was known at decision time. [D] ([ArcticDB](https://arcticdb.io/blog/time-travel-in-arcticdb/)). Two Sigma treats data as code, with versioning, tests, lineage and CI. [D] ([Two Sigma](https://www.twosigma.com/articles/treating-data-as-code-at-two-sigma/)).
7. Free "static" files are also revised. Ken French reconstructs the portfolios every month, so historical returns change when CRSP is revised. [D] ([French library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)). Each download must be stored as a hashed snapshot, never overwritten.
8. ICE BofA OAS series on FRED keep only 3 years of observations from April 2026. [D] ([FRED BAMLH0A1HYBB](https://fred.stlouisfed.org/data/BAMLH0A1HYBB)). Long credit history must come from Moody's BAA/AAA on FRED, and any OAS history already captured is irreplaceable. FRED marks copyrighted series and allows personal use only. [D] ([FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html)).
9. For Druckenmiller-relevant global liquidity, the highest-value free additions are BIS central bank total assets (annual median start 1942), BIS policy rates (from 1946), BIS total credit (from the 1940s, quarterly), Fed Z.1 (1945/1952→), H.4.1 scans on FRASER (1940→), the JST Macrohistory database (1870→, annual) and the BoE "Millennium" file. [D] (sources in §7).
10. Market-internals breadth before 2021 has no free daily NYSE advance-decline file. [G] ([StockCharts gallery](https://alb.stockcharts.com/freecharts/historical/marketbreadth.html) has charts only). A breadth proxy from Ken French daily industry portfolios (1926→) is the practical substitute. [I] It must be tagged `interpreted` and validated against Alpaca-based breadth on 2021→.

---

## 1. Long-history reconstruction

### 1.1 AQR — "A Century of Evidence on Trend-Following Investing" (Hurst, Ooi, Pedersen)

| Item | Practice | Tag / source |
|---|---|---|
| Universe | 67 markets, 1880–2013 | [D] [paper, App. A](https://www.trendfollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf) |
| Rule | "We use futures returns when they are available. Prior to the availability of futures data, we rely on cash index returns financed at local short-term interest rates for each country." | [D] same |
| Equities | Futures from Datastream/Bloomberg; before futures, MSCI country returns, then Ibbotson, GFD and Yale School of Management | [D] same |
| Bonds | Futures from Morgan Markets/Bloomberg; before futures, cash bond returns from Datastream, Ibbotson, GFD. GFD/Ibbotson monthly returns are "scaled ... to a constant duration of 4 years", with assumed durations of 2y (UST 2y), 4y (UST 5y, REX), 20y (long bond) and 7y (all others) | [D] same |
| FX | Citigroup spot and forward rates from 1989 (CAD 1992, NZD 1996); before that, Datastream spot plus LIBOR short rates (spot + carry) | [D] same |
| Commodities | Bloomberg futures; before Bloomberg, Commodity Systems Inc. and Chicago Board of Trade historical records | [D] same |
| Costs | One-way transaction costs at 2012 estimates, ×2 for 1993–2002 and ×6 for 1880–1992 (per Jones 2002) | [D] same, App. B |
| Caveat | The authors do not claim the strategy was implementable in the 1880s; commodities are the most realistic leg because they are based on traded futures prices | [D] same, fn. 6 |

### 1.2 Moskowitz-Ooi-Pedersen, "Time Series Momentum" (JFE 2012)

- 58 instruments, 1965–2009. Each day the return of the "most liquid futures contract (typically the nearest or next nearest-to-delivery contract)" is compounded into an index. For equity indices, the futures series are "almost perfectly correlated" with cash index returns in excess of T-bills. [D] ([paper](https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf), §2.1)
- Appendix A splices MSCI country returns before equity futures and JP Morgan country bond indices before bond futures. Bond returns are scaled to constant duration: 2y for 2–3y futures, 4y for 5y, 7y for 10y and 20y for 30y. FX uses Citigroup forwards from 1989; before that, Datastream spot plus IBOR from Bloomberg. [D] same, App. A
- Ex-ante volatility is an EWMA of squared daily returns with a 60-day center of mass, "chosen ... due to its simplicity and lack of look-ahead bias". [D] same, §2.4

### 1.3 Asness-Moskowitz-Pedersen, "Value and Momentum Everywhere" (JF 2013)

- FX: Datastream spot for 10 currencies, 1979–2011, with Germany spliced with the euro. Returns come "from currency forward contracts or MSCI spot price data and Libor rates ... implicitly include the local interest rate differential". [D] ([paper, App. A.3](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf))
- Bonds: index returns from Bloomberg/Morgan Markets; 10y yields and short rates from Bloomberg; inflation forecasts from Consensus Economics. Value is the real bond yield, i.e. the 10y yield minus the 5y inflation forecast. [D] same, A.4
- Commodities: 27 futures, 1972–2011. The minimum number of commodities at any date is 10. Daily excess return of the most liquid contract, compounded. [D] same, A.5
- Free data: AQR publishes the original and updated factor and portfolio series. [D] ([AQR VME data](https://www.aqr.com/Insights/Datasets/Value-and-Momentum-Everywhere-Original-Paper-Data))

### 1.4 Levine & Pedersen, "Which Trend Is Your Friend?" (FAJ 2016)

- Extends the MOP 58 instruments to 1985–2015. Signals are computed "from a return index (rather than from prices directly) that was formed by rolling futures and forward prices", so carry and roll-down are included implicitly and returns are "naturally excess of cash". Before 1989, FX returns use Datastream spot combined with IBOR. [D] ([CBS PDF](https://research-api.cbs.dk/ws/files/60084063/lasse_heje_pedersen_et_al_which_trend_is_your_friend_publishersversion.pdf), Data and App. C)
- Implication [I]: Fat Pitch trend and chart rules (R-29) should run on excess-return indices, not raw spot prices, wherever carry is material (FX, commodities, bonds).

### 1.5 Man AHL — Hamill, Rattray, van Hemert, "Trend Following: Equity and Bond Crisis Alpha" (2016)

- Covers 1960–2015 on monthly data. The history is extended "with proxies based on cash returns, financed at the local short-term rate". Equity and bond cash data come from GFD, and "We deduct the local short rate from the return to make it comparable to the return of an unfunded instrument like a future." Before futures, FX uses spot "corrected for the short-rate differential". Data start in 1950 to give a warm-up period, and series starting after 1960 get a one-year warm-up. [D] ([paper](https://static.twentyoverten.com/593e8a9e7299b471eaecf644/rJ3CvIT7f/Trend-Following-Equity-and-Bond-Crisis-Alpha.pdf), §1)
- **Regime-exclusion filter**: securities are excluded while their rolling 12-month volatility falls to 0.05× its average. This flagged silver (included only from 1972) and the JGB and Australian 10y (included from 1972 and 1977) because of pegs, capital controls and intervention. Pre-1973 FX is excluded because of Bretton Woods. Before 1960, commodities face a choice between omitting them, intermittent data, or "spot returns thus ignoring the roll yield". [D] same
- Validation by benchmark: the monthly momCTA proxy has a 0.62 correlation with BTOP50 excess returns over 1987–2015. [D] same

### 1.6 Other long backtests

| Work | Data practice | Tag |
|---|---|---|
| CFM, Lempérière et al., "Two Centuries of Trend Following" (2014) | Futures from 1960; spot series back to 1800 for commodities and indices | [D] [arXiv 1404.3274](https://arxiv.org/abs/1404.3274) |
| Greyserman (ISAM) & Kaminski (Campbell), *Trend Following with Managed Futures* | Multi-century trend evidence | [D] existence only ([Wiley listing](https://www.amazon.com/Trend-Following-Managed-Futures-Trading/dp/1118890973)); data appendix not read [G] |
| Baltas & Kosowski | 71 futures contracts; monthly, weekly and daily TSMOM; transaction-cost model split into roll-over and rebalancing costs | [D] [EFMA 2012 paper](https://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2012-Barcelona/papers/BK_MOMF_Full.pdf), [EDHEC summary](https://climateinstitute.edhec.edu/publications/momentum-strategies-futures-markets-and-trend-following-funds); exact roll convention not verified [G] |
| Winton | No public data-methodology paper located | [G] |
| Levine-Ooi-Richardson-Sasseville, "Commodities for the Long Run" (AQR) | Daily futures 1877–1951 transcribed by hand from CBOT Annual Reports, Commodity Systems Inc. 1951–2012, Bloomberg after 2012; free monthly index data published | [D] [NBER w22793](https://www.nber.org/system/files/working_papers/w22793/w22793.pdf), [AQR dataset](https://www.aqr.com/Insights/Datasets/Commodities-for-the-Long-Run-Index-Level-Data-Monthly) |
| Gorton-Rouwenhorst, "Facts and Fantasies" | Equal-weighted rolled commodity futures index, Jul 1959–2004, from Commodity Research Bureau and LME data | [D] [NBER w10595](https://www.nber.org/papers/w10595.pdf) |

### 1.7 Ilmanen-Israel-Lee-Moskowitz-Thapar, "How Do Factor Premia Vary Over Time? A Century of Evidence" (JOIM 2021)

The most explicit published recipe set for pre-futures construction ([PDF](https://www.aqr.com/-/media/AQR/Documents/Journal-Articles/JOIM_How-Do-Factor-Premia-Vary-Over-Time.pdf)):

- Data run as far back as Feb 1877, with the analysis starting in 1926. "Our main data source is Global Financial Data, supplemented by Bloomberg and DataStream." [D]
- Equities: for each of 43 markets, the index chosen is "investible, has the most representative coverage ... and has the longest history". Total returns minus local cash give excess returns. [D]
- Bonds: GFD 10y yields and total returns plus 3m rates. "Between 1920 and 1960, the database uses the closest available tenor to 10-year, while before 1920 ... individual bonds." [D]
- FX: forwards rolled at IMM dates, rolling three business days before maturity. "Before 1990 ... changes in spot exchange rates plus the carry of the currency (difference in local interest rates)." Coverage starts Aug 1971. [D]
- Commodities: hold the nearest contract with delivery at least 2 months away. If that contract has no return, step out to the fifth contract at most. Contiguous limit moves are collapsed into the first move. [D]
- Equity carry before 1990 is the excess-of-cash dividend yield. Bond carry is the 10y minus 3m spread. [D]
- Pre-sample tests check performance before each factor's discovery sample, to separate data-mining from real effects. [D] Fat Pitch's case-corpus discipline (E.3) is analogous. [I]

### 1.8 Bridgewater

- *Daily Observations* has been published for 50 years. The firm states that its research "utilizes data and information from public, private, and internal sources", and that historical case studies inform the process. [D] ([Bridgewater](https://www.bridgewater.com/50-years-of-the-bridgewater-daily-observations))
- *Big Debt Crises* compiles 48 debt-crisis cases over roughly 100 years into archetypes, by averaging many cases of the same event type. [D] ([CFA Institute review](https://rpc.cfainstitute.org/blogs/enterprising-investor/2019/book-review-principles-for-navigating-big-debt-crises); [Funds Society](https://www.fundssociety.com/en/style/ray-dalio-to-release-new-book-on-the-10th-anniversary-of-the-2008-financial-crisis)). An earlier Bridgewater deleveraging paper charts US total debt/GDP from 1918. [D] ([Dalio 2012 PDF](https://hold.hu/holdblog/wp-content/uploads/2012/03/an-in-depth-look-at-deleveragings--ray-dalio-bridgewater.pdf))
- *Changing World Order* reportedly uses country-level estimates spliced together, drawing on Maddison and the BoE "Millennium of Macroeconomic Data"; the citations document lists sources. [D, secondary] ([search summary of CWO bibliography](https://www.economicprinciples.org/downloads/cwo-citations-and-bibliography.pdf); the PDF itself redirected and was not read [G])
- Bridgewater splice and proxy rules are not public. [G]
- The transferable practice is the archetype method: align many episodes on an event date and average them. [I] This matches Fat Pitch's event corpus.

### 1.9 Reference datasets (academic and paid)

| Dataset | Content | Access | Tag |
|---|---|---|---|
| Jordà-Schularick-Taylor Macrohistory (R6) | 18 advanced economies, 1870→, annual, 48 variables: credit, house prices, total returns on equity/housing/bonds/bills, money, rates, crisis dummies | Free, CC BY-NC-SA 4.0; commercial providers barred from integrating it | [D] [macrohistory.net](https://www.macrohistory.net/database/) |
| Global Financial Data | 1700→ bond indices; total-return indices for 50+ countries; splices, e.g. munis extended with Massachusetts notes 1789–1815 and corporates with canal and railroad bonds | Paid; reference only | [D] [GFD munis/corporates](https://globalfinancialdata.com/global-financial-data-provides-longer-histories-for-its-united-states-corporate-and-muni-bonds), [GFD TR](https://globalfinancialdata.com/global-financial-data-adds-total-returns-to-its-gfd-indices) |
| Ilmanen, *Expected Returns* (2011) | Long-history synthesis; relies on Dimson-Marsh-Staunton-type data | Book | [D] existence ([O'Reilly](https://www.oreilly.com/library/view/expected-returns-an/9781119990772/)); data appendix not read [G] |
| S&P GSCI | Launched 1991; history to Jan 1970 is back-tested using the methodology in effect at launch | Paid index; levels visible | [D] [Wikipedia](https://en.wikipedia.org/wiki/S%26P_GSCI) |
| Bloomberg Commodity Index | Launched 1998, history back to 1960; weights 2/3 liquidity and 1/3 production; roll on business days 6–10; TR = ER + collateral (now SOFR) | Paid; methodology public | [D] [Bloomberg press](https://www.bloomberg.com/company/press/bloomberg-commodity-index-2024-target-weights-announced), [BCOM SOFR TR methodology](https://assets.bbhub.io/professional/sites/27/20250718_BCOM-SOFR-TR-Tech-Doc-Methodology-October-2025.pdf) |

Common splice rules across 1.1–1.7 [I, synthesized from the [D] items above]:

| # | Rule |
|---|---|
| 1 | Use the most tradable instrument available at each date: futures, then forwards, then cash plus financing, then spot only |
| 2 | Convert everything to excess-of-cash returns before splicing. Splice returns, never price levels |
| 3 | Rescale bond legs to a constant duration |
| 4 | Admit an instrument only when it trades freely (vol filter, peg and capital-control exclusions) |
| 5 | Warm-up periods for volatility estimators; no in-sample volatility |
| 6 | Cost multipliers that rise further back in history |
| 7 | Validate each splice on the overlap |

---

## 2. Point-in-time and vintage discipline

### 2.1 Evidence that revisions bias results

| Case | Finding | Tag |
|---|---|---|
| Ghysels-Horan-Moench (NY Fed SR 581) | "data revisions account for a sizeable share of in-sample and out-of-sample predictive power for Treasury returns found in macroeconomic data"; real-time survey forecasts carry information about future revised data | [D] [SR581](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr581.pdf) |
| Lyle-Siano-Yohn (2024) | Compustat restandardization "introduces a form of look-ahead bias". Hedge returns on earnings surprise and accrual deciles differ depending on download date; exact replication from common Compustat products is "nearly impossible" | [D] [paper](https://som.yale.edu/sites/default/files/2024-07/Re-Standardized%20Financial%20Statement%20Data.pdf) |
| Compustat Point-in-Time | Vendor PIT product from Dec 1986 for ~29,000 companies | [D] [Global Custodian](https://www.globalcustodian.com/?p=26067) |
| Deutsche Bank, "Seven Sins of Quantitative Investing" (Luo et al. 2014) | Survivorship and look-ahead are sins 1 and 2; point-in-time tracking of all companies that ever existed is recommended | [D] [PDF](https://columbia.edu/~nyc2107/papers/seven_sins_of_quantitative_investing.pdf), [Palomar summary](https://bookdown.org/palomar/portfoliooptimizationbook/8.2-seven-sins.html) |

### 2.2 Free vintage sources

| Source | Coverage | Notes | Tag |
|---|---|---|---|
| ALFRED / FRED API real-time periods | `realtime_start`/`realtime_end` return data as known on past dates | Release date = source date if known, else the provider's date, else "the date the series first appeared in FRED". Vintages are "verified with the original source" where possible | [D] [ALFRED help](https://alfred.stlouisfed.org/help), [FRED API](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) |
| Philadelphia Fed RTDSM | Vintages from Nov 1965, each as of the ~15th of the month (data available to a forecaster on 15 Nov 1965); "first-, second-, third-release values" files; updated monthly | Fills the period before ALFRED coverage | [D] [Croushore-Stark WP 99-4](https://www.philadelphiafed.org/-/media/FRBP/Assets/working-papers/1999/wp99-4.pdf?sc_lang=en), [RTDSM page](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists) |
| Dallas Fed international real-time | 26 OECD countries, 13 variables (GDP, IP, CPI, money, unemployment ...), quarterly vintages 1962Q1–1998Q4 transcribed from hard-copy MEI | Splices to OECD ORDRD | [D] [Dallas Fed](https://www.dallasfed.org/research/international/oecd) |
| OECD MEI ORDRD | Monthly vintages from Jan 1999 | Via OECD Data Explorer | [D] [OECD](https://www.oecd.org/en/publications/undertaking-revisions-and-real-time-data-analysis-using-the-oecd-main-economic-indicators-original-release-data-and-revisions-database_146528313656.html) |
| Tealbook (Greenbook) data sets | Fed staff projections for 15 variables, released after a 5-year lag; separate file of real-time output gap and financial assumptions | Shows what the Fed believed at each meeting | [D] [Philadelphia Fed](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/greenbook) |
| SPF | Quarterly, from 1968 | Real-time expectations | [D] [Philadelphia Fed SPF](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters) |
| IMF WEO vintages | Vintages back to 2007, data from 1980; `weohistorical.xlsx` holds historical forecasts | International real-time forecasts | [D] [IMF transition guide](https://data.imf.org/-/media/iData/External-Storage/Documents/2C2B2F3E671A4B11ABE756E2441FD6F0/en/WEO-Database-Transition-Guide.pdf), [weo package](https://pypi.org/project/weo) |
| NBER cycle announcements | Peaks and troughs announced 5–21 months after the turning point (e.g. 2001 trough announced Jul 2003) | Recession labels need `published_at` = announcement date | [D] [NBER Nov 2001 announcement](https://www.nber.org/cycles/november2001), [NBER chronology](https://nber.org/research/data/us-business-cycle-expansions-and-contractions) |

### 2.3 Publication-lag modeling where no vintage exists [I]

- The precedence for `published_at` should be: (a) source vintage (ALFRED/RTDSM/ORDRD); (b) the release calendar for that period (FRED release dates, H.4.1 Thursday 16:30 ET, H.6, Z.1 dates in ALFRED [release 52](https://alfred.stlouisfed.org/release?rid=52)); (c) a conservative lag rule per series (e.g. monthly macro data = period end + 45 days, quarterly = + 90 days); (d) unknown, which the engine treats as unknown.
- Store the method in a `published_at_method` column. In ALFRED, a release date equal to the series' FRED-addition date is a fallback, not a true release date; such rows should be flagged rather than trusted. [I, from the ALFRED fallback rule above]
- First-release versus revised: keep both. Rules that emulate what a discretionary manager saw (R-02 M2−IP) use the vintage as of `asof`. Ground-truth labels (recession dates, regime outcomes) may use revised data, but only as labels, never as engine inputs. [I] The Ghysels finding that survey expectations carry information about revisions [D] supports adding SPF/Tealbook as real-time expectation inputs. [I]

### 2.4 Bitemporal storage

- ArcticDB, open-sourced by Man Group, keeps immutable versions and named snapshots. `as_of` reads by version, timestamp or snapshot reconstruct "what information was available when past decisions were made" after a vendor restatement. [D] ([ArcticDB blog](https://arcticdb.io/blog/time-travel-in-arcticdb/); [Arctic PyPI "AHL Research Versioned TimeSeries"](https://pypi.python.org/pypi/arctic/1.5.0))
- In bitemporal databases, valid time is used for analysis and transaction (system) time for audit. "How did my data look as-of ... as it was known at the time" requires both axes. [D] ([XTDB docs](https://v1-docs.xtdb.com/concepts/bitemporality/); [Capgemini white paper](https://www.capgemini.com/ch-en/wp-content/uploads/sites/43/2017/07/Enhancing_Time_Series_Data_by_Applying_Bitemporality.pdf))
- Mapping to amber [I]:

| Concept | Column |
|---|---|
| Valid time | `period_end` (plus `obs_time` with timezone for intraday closes) |
| Public knowledge time | `published_at` |
| Lake knowledge time | `ingested_at` |
| Grouping | `vintage_id` |

  Backtests filter on `published_at <= asof`. Reproducibility of a past engine run also filters on `ingested_at <= run_time`. Without the second filter, a run cannot be replayed after a data fix.

---

## 3. Survivorship and constituent history

| Practice | Detail | Tag |
|---|---|---|
| CRSP delisting returns | Most negative-reason delisting returns since 1962 are missing from CRSP and large and negative | [D] [Shumway 1997 (RePEc)](https://ideas.repec.org/a/bla/jfinan/v52y1997i1p327-40.html) |
| Nasdaq correction | Shumway-Warther use −55% for missing performance-related Nasdaq delisting returns; after correction, the Nasdaq size effect disappears | [D] [JF 1999 (RePEc)](https://ideas.repec.org/a/bla/jfinan/v54y1999i6p2361-2379.html) |
| Free S&P 500 history | Community files reconstruct membership from 1996 using Wikipedia change tables | [D] [hanshof/sp500_constituents](https://github.com/hanshof/sp500_constituents), [Robot Wealth method](https://robotwealth.com/how-to-get-historical-spx-constituents-data-for-free/) |
| Fund holdings | N-PORT: monthly XML filings; quarter-end report public, SEC data sets updated quarterly. N-Q (quarterly, 2004–2019) rescinded effective 1 Aug 2019 | [D] [SEC N-PORT data sets](https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets), [Dechert](https://dechert.com/knowledge/onpoint/2017/8/sec-staff-issues-faqs-on-the-investment-company-reporting-modern.html), [Fidelity N-Q 2004 example](https://www.sec.gov/Archives/edgar/data/0001303459/000130345905000002/main.htm) |
| Delisting dates | Form 25 on EDGAR; delisting effective 10 days after filing | [D] [SEC Form 25](https://www.sec.gov/about/forms/form25.pdf) |

Implications for Fat Pitch [I]:

- **v1 macro scope is mostly survivorship-free by construction.** Index-level, futures, FX, rates and Fama-French portfolio returns already include dead firms; French builds from CRSP "all NYSE, AMEX, and NASDAQ firms" ([French](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)). Survivorship matters only for the equities expression stage (E5).
- **Pre-2021 S&P 500 membership** (D-9): build from IVV/SPY holdings in N-Q (2004–2019) and N-PORT (2019→) filings, cross-checked against the Wikipedia change table. The current N-PORT pipeline (2021-06→) extends back to 2004 with N-Q text parsing. Before 2004, label results survivorship-biased.
- **Delisted names**: Alpaca's 775 delisted symbols start in 2021. For older delistings, Form 25 gives the date. Where the final price is missing, apply −30% (NYSE/AMEX-type) or −55% (Nasdaq, per Shumway-Warther) and flag `interpreted`. The −30% figure is commonly attributed to Shumway 1997 but was not verified this session. [G]

---

## 4. Proxy construction and validation

### 4.1 Documented recipes

| Target | Documented recipe | Source |
|---|---|---|
| Treasury total return from yields | Par bond: monthly return = Y(t−1)/12 − D·ΔY + ½·C·(ΔY)². Modified duration and convexity from yield and maturity. Full monthly repricing captures convexity. Against GFD: R² 0.996 (1962–2018); against CRSP and Ibbotson: R² 0.93–0.95. Not valid for defaultable bonds ("overestimation of investor returns") | [D] [Swinkels 2019](https://repub.eur.nl/pub/117405/Swinkels-2019-Data.pdf); [NMOF approxBondReturn](https://r-packages.io/packages/NMOF/approxBondReturn); [treasuryTR](https://www.rdocumentation.org/packages/treasuryTR/versions/0.1.6) |
| Zero-coupon curve | Fed GSW daily yield curve from 1961 (zero, par, forward), updated weekly | [D] [Fed FEDS 2006-28](https://www.federalreserve.gov/pubs/feds/2006/200628/feds200628.html) |
| FX excess return pre-forwards | Spot change plus the short-rate differential (CIP: forward premium ≈ rate differential) | [D] Ilmanen et al. 2021; AHL 2016; MOP 2012 (above); [interest rate parity](https://en.wikipedia.org/wiki/Interest_rate_parity) |
| Commodity excess return | Roll the nearest contract with ≥2 months to delivery; excess return = spot change + roll-down | [D] Ilmanen et al. 2021; MOP 2012 decompose futures return = price change + roll return |
| Commodity index history | GSCI back-tested to 1970 and BCOM to 1960 using launch-date methodology | [D] (§1.9) |
| Credit excess return | Credit premium measured after removing rate exposure (duration-matched Treasuries), 1936–2014: IG ~0.11%/month, Sharpe 0.37 | [D] [Asvanunt-Richardson (AQR)](https://www.aqr.com/Insights/Datasets/Credit-Risk-Premium-Preliminary-Paper-Data), [CXO summary](https://www.cxoadvisory.com/economic-indicators/credit-risk-premium-magnitude-and-dynamics/) |
| Spread return | Excess ≈ spread/12 − spread duration × Δspread; DTS (duration × spread) as the risk unit | [D] [Robeco DTS](https://www.robeco.com/docm/docu-201708-duration-times-spread.pdf) |
| Equity excess pre-futures | Total return minus local cash | [D] Ilmanen et al. 2021; Hurst et al. |
| Equity sectors | Fama-French 5–49 industries, daily and monthly from Jul 1926 | [D] [French library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) |
| Implied vol | VXO (S&P 100, at-the-money, old method), daily 1986 to 23 Sep 2021; VIX (new method) from 1990 | [D] [FRED VXOCLS](https://fred.stlouisfed.org/series/VXOCLS), [Eurex history](https://www.eurexchange.com/resource/blob/36578/1baafe8647977b991c16f3f62782cc42/data/the-evolution-of-volatility-products.pdf) |
| Asynchronous closes | Correlations from asynchronous closes are biased toward zero; Burns-Engle-Mezrich synchronize to the NYSE 4pm close with an MA(1) model | [D] [r-bloggers summary](https://www.r-bloggers.com/2011/11/asynchrony-in-market-data/) |

### 4.2 Validation methods

| Method | Documented use | Tag |
|---|---|---|
| Regression of proxy on benchmark (intercept≈0, slope≈1, R²) and Wald test | Swinkels: R² > 0.92 against all alternatives, but the Wald test often rejects equality because the confidence intervals are tiny. Judge economic, not statistical, significance | [D] Swinkels 2019 |
| Correlation with a live benchmark | AHL momCTA vs BTOP50: 0.62 | [D] AHL 2016 |
| Futures vs cash correlation on overlap | MOP: equity futures "almost perfectly correlated" with cash excess returns | [D] MOP 2012 |
| Pre-/post-sample comparison | Ilmanen et al. 2021 | [D] |
| Grading tiers | Not found as a published fund practice | [G]; tiers proposed in §8 [I] |

Proposed grading for amber (`proxy_grade` in `sources.yaml`), computed on the overlap with monthly returns unless stated [I]:

| Grade | Criteria | Engine use |
|---|---|---|
| A | Native series (exact instrument or official index) | Full weight |
| B | Corr ≥ 0.95, beta 0.9–1.1, annualized TE ≤ 2% (or ≤ 0.25×target vol), sign agreement ≥ 90% | Full weight; era flag |
| C | Corr 0.80–0.95 or sign agreement 75–90% | Direction and regime only, no sizing |
| D | Corr < 0.80, or no overlap available | Display only; `unknown` for gating rules |

Grades are recomputed on each rebuild and stored with the manifest. E.4a data-era stratification reports results by grade.

---

## 5. Data operations

| Practice | Documented evidence | Tag |
|---|---|---|
| Data as code: versioned datasets and pipelines, automated tests, coverage metrics from data checks, lineage, CI/CD, data contracts | Two Sigma | [D] [Two Sigma](https://www.twosigma.com/articles/treating-data-as-code-at-two-sigma/) |
| Immutable storage, versions, snapshots, `as_of` reads | Man Group / ArcticDB | [D] [ArcticDB](https://arcticdb.io/blog/time-travel-in-arcticdb/) |
| 10,000+ sources ingested daily; tools for dataset health | Two Sigma | [D] [Two Sigma engineering](https://www.twosigma.com/careers/engineering/) (via search summary) |
| Vendor comparison on integrity, coverage and aggregation methodology | Man Group data team | [D] [Man job description](https://builtin.com/job/data-science-analyst/3130594) (secondary) |
| Free "static" files are revised | French reconstructs monthly; Shiller interpolates monthly earnings and dividends and uses monthly averages of daily closes | [D] [French](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html), [Shiller data description (R doc)](https://search.r-project.org/CRAN/refmans/neverhpfilter/html/SP500.html) |
| Regime filters | AHL: 0.05× average-volatility exclusion | [D] AHL 2016 |
| Limit-move handling | Contiguous limit moves collapsed into the first move | [D] Ilmanen et al. 2021 |
| Calendars | `exchange_calendars` (50+ exchanges); `pandas_market_calendars` adds futures product calendars with breaks, early closes and late opens | [D] [exchange-calendars](https://pypi.org/project/exchange-calendars/3.3/), [pandas_market_calendars](https://pandas-market-calendars.readthedocs.io) |
| Timezone/close alignment | Asynchronous closes understate correlation; synchronize to one clock | [D] Burns-Engle-Mezrich (above) |

Recommended amber operations [I]:

1. **Raw zone, immutable.** `lake/raw/<source>/<yyyy-mm-dd>/<file>` holds bytes exactly as downloaded, plus `manifest.json` (URL, HTTP headers, ETag/Last-Modified, sha256, bytes, fetched_at, parser version). Raw is never overwritten. A source change produces a new snapshot.
2. **Normalized zone.** Parquet with `series_id, period_end, obs_time(tz), value, unit, published_at, published_at_method, ingested_at, vintage_id, source_sha256, proxy_grade`. Rebuildable deterministically from raw.
3. **Derived zone.** Proxies, splices and composites, with a recipe id and version and input sha list (lineage). The `fatpitch` run row already stores the registry sha (PLAN 0); it should also store the derived-zone manifest sha.
4. **Revision tracking.** When a re-download changes history (French, Shiller, World Bank CMO, AQR), record a diff summary (rows changed, max |Δ|) in `revisions.parquet`. Alert when a change exceeds a threshold.
5. **Dual-source cross-checks.** Run nightly where two free sources overlap; examples in the table below.
6. **Bad-print and outlier rules.** Flag (never auto-delete in raw):
   - |return| > k × rolling MAD, with k = 8 daily and 5 monthly as the starting values;
   - zero-volume prints;
   - stale runs of more than N identical closes;
   - negative prices except where valid (WTI 2020-04-20);
   - unit/scale jumps (the CBP VX ×10 scale pre-2007 is the in-house example).
   Flagged values are excluded at the derived layer, with a reason code.
7. **Corporate actions** (equities): adjust from raw unadjusted prices plus a dividends/splits table, as of the date. Never store only vendor-adjusted closes, because adjustment factors change retroactively.
8. **Futures continuous series** (D-5): store individual contracts. Build back-adjusted and ratio-adjusted continuous series as of the date, with the roll rule recorded (MOP "most liquid", or Ilmanen "nearest ≥2 months"). Returns are computed within a contract, never across the roll gap.
9. **Monitoring.** Per series: freshness against the expected release calendar, gap %, `published_at` coverage, z-score of the latest print, and cross-source diff. This extends amber's existing gap/freshness tools into a daily data-quality table.

Dual-source cross-check pairs (item 5):

| Primary | Cross-check |
|---|---|
| FRED DGS10 | Treasury par yield curve / GSW |
| FRED DEXUSEU | ECB reference rate |
| H.4.1 WALCL | Fed DDP |
| IBKR futures settle | Massive / CBP |
| BLS API | FRED copy |

---

## 6. Alternative data

| Item | Evidence | Tag |
|---|---|---|
| Satellite car counts | 7.6M images of 86,000 stores of 44 retailers. Access let sophisticated investors trade ahead of earnings (up to ~5% abnormal return) and shifted informed short-selling | [D] [Katona et al. JFQA](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/2F5F99D68D1F8940F61578F198D6C005/S0022109023001448a.pdf/on-the-capital-market-consequences-of-big-data-evidence-from-outer-space.pdf), [Berkeley Haas](https://newsroom.haas.berkeley.edu/how-hedge-funds-use-satellite-images-to-beat-wall-street-and-main-street/) |
| Regulatory | SEC Examinations listed alternative data diligence and MNPI controls as priorities and found inconsistent vendor diligence | [D] [Lowenstein Sandler](https://www.lowenstein.com/news-insights/publications/articles/key-considerations-for-alternative-data-and-ai-vendors-to-investment-firms-demonstrating-compliance-in-the-face-of-an-evolving-regulatory-environment) |
| Scraping law | hiQ v. LinkedIn: the Ninth Circuit (Apr 2022) held the CFAA does not reach public web data. The district court later found breach of the user agreement; the settlement included a permanent injunction, deletion of data and code, and $500k | [D] [Wikipedia](https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn), [Proskauer](https://newmedialaw.proskauer.com/2022/12/08/hiq-and-linkedin-reach-proposed-settlement-in-landmark-scraping-case/), [ZwillGen](https://www.zwillgen.com/alternative-data/hiq-v-linkedin-wrapped-up-web-scraping-lessons-learned/) |
| EDGAR access | Up to 10 requests/second; a declared User-Agent with contact details | [D] [SEC](https://www.sec.gov/os/accessing-edgar-data) |
| FRED licensing | Copyrighted series (marked "Copyright" in notes) need owner permission for anything beyond personal use; no app replicating FRED; endorsement disclaimer required | [D] [FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html), [FRED legal](https://fred.stlouisfed.org/legal/) |
| JST license | CC BY-NC-SA 4.0 | [D] [macrohistory.net](https://www.macrohistory.net/database/) |

Free alternative data achievable now:

| Data | Coverage | Tag |
|---|---|---|
| IMF PortWatch | Daily AIS port calls, trade-volume estimates and chokepoint transits; multi-day lag; no authentication | [D] [IMF WP](https://www.imf.org/en/publications/wp/issues/2019/12/13/big-data-on-vessel-traffic-nowcasting-trade-flows-in-real-time-48837), [OpenBB port_volume](https://docs.openbb.co/python/reference/economy/shipping/port_volume), [UNGP slides](https://unstats.un.org/bigdata/events/2025/ai-data-science/webinar1/presentations/Mario%20and%20Alessandra%20-%20PortWatch%20-%20UNGP.pdf) |
| NASA Black Marble night lights | Daily, monthly and yearly, 2012→; World Bank `blackmarblepy` | [D] [LAADS DAAC](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/science-domain/nighttime-lights/), [World Bank blog](https://blogs.worldbank.org/en/opendata/illuminating-insights-harnessing-nasas-black-marble-r-and-python-packages) |
| Already planned in D-20 | NOAA/MODIS, WARN, H-1B, Polymarket | — |

Recommendation [I]: alternative data stays weight 0 (PLAN D-20). Each source carries `license`, `tos_url`, `redistribution` and `scraping: api|bulk|html` fields in `sources.yaml`. Sources whose ToS prohibit automated access are not ingested. Nothing derived from copyrighted FRED series or IBKR is redistributed.

---

## 7. Druckenmiller-style macro: what long series matter, and free sources

Documented emphasis:

- On liquidity: "Earnings don't move the overall market; it's the Federal Reserve board ... focus on the movement of liquidity." [D] ([Advisor Perspectives, Lost Tree](https://www.advisorperspectives.com/commentaries/2015/04/20/on-my-radar-the-speech-at-lost-tree-club); [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/druckenmiller-lost-tree-club/))
- On market internals: the "inside of the stock market" (trucking, retail, housing, autos, durables) is described as his best economic predictor. [D, secondary] ([Felder Report](https://thefelderreport.com/?p=41213); [Seeking Alpha](https://seekingalpha.com/article/4231256-druckenmiller-what-indicators-does-he-use))
- Project rules R-01 to R-04 and R-60 already encode both. Primary citations are in `spec\process.md`.

The series a discretionary macro process would value most [I], ranked by value to the engine:

1. Central bank balance sheets (global) and policy rates
2. Money supply versus activity (M2−IP)
3. Credit growth (bank and total, global)
4. Treasury issuance and the TGA
5. Yield curves (level, slope, real)
6. FX (dollar index, crosses, carry)
7. Commodities (spot and excess return)
8. Credit spreads
9. Breadth and sector leadership
10. Expectations (SPF, Tealbook, WEO) and recession-dating announcement dates

The source-by-source table appears below in "Free long-history sources to add".

---

## 8. Recommendations for this project

| # | Practice | Why | How (amber / fatpitch) | Priority | Effort |
|---|---|---|---|---|---|
| 1 | Bitemporal columns: add `ingested_at`, `published_at_method`, `source_sha256`, `proxy_grade` to the normalized schema | Replay of past runs after data fixes; honors the PLAN 0.2 contract and makes PIT quality explicit (ArcticDB/XTDB practice) | Extend the `Source.snapshot` frame; property test: no row with `published_at > asof`, and replay with `ingested_at <= run_time` reproduces the stored Decision | High | M |
| 2 | Immutable raw zone plus hashed snapshot manifest for every download, especially revisable "static" files (French, Shiller, World Bank CMO, AQR, JST) | French rebuilds monthly; restandardization bias shown for Compustat | `lake/raw/<src>/<date>/` + `manifest.json`; derived layers rebuild from a manifest sha; run row stores the manifest sha | High | S |
| 3 | `published_at` precedence: vintage → release calendar → lag rule → unknown; flag ALFRED fallback dates | ALFRED falls back to the FRED-addition date; NBER announces 5–21 months late | Release-calendar table (D-2a) plus per-series lag rules in `sources.yaml`; NBER announcement-date table | High | M |
| 4 | Pre-ALFRED vintages: Philadelphia RTDSM (1965→) for US; Dallas Fed OECD real-time (1962–1998) + ORDRD (1999→) for EA/JP/UK | Era B (pre-2002) rules otherwise run on revised data, the bias Ghysels et al. document | New loaders `rtdsm`, `oecd_rt`; map variables to R-02 inputs (M2, IP, CPI, unemployment) | High | M |
| 5 | Proxy library with fixed, versioned recipes (table below) and overlap grading A–D | All published long backtests splice this way; free inputs reach R² ~0.99 for Treasuries | `core\proxies.py` in amber; each recipe outputs a series plus a validation row (corr, beta, TE, sign agreement, R²); E.4a stratifies by grade | High | M |
| 6 | Splice rules: excess-return space, ratio/return splice at a documented date, both legs kept, no splice across definitional breaks (M2 May 2020, DTWEXM→DTWEXBGS, DEM→EUR) | Prevents level jumps and silent regime mixing | `splice(series_a, series_b, method, date)` writes a lineage record; D-8 dollar splice is the first user | High | S |
| 7 | Capture ICE BofA OAS daily now and retain it; long-history credit from Moody's BAA/AAA (FRED, 1919→) and BAA−DGS10 (1953→) | FRED keeps 3 years of ICE data from Apr 2026; ICE series are copyrighted | Nightly append-only capture; `redistribution: none`; D-7 uses BAA−AAA and BAA−DGS10 for era B | High | S |
| 8 | Global liquidity long series: BIS CBTA, BIS policy rates, BIS total credit, Z.1, H.4.1 FRASER (pre-2002 weekly, manual extraction), BoJ API, ECB Data Portal, BoE IADB | R-03/R-04 cross-region and era-B liquidity; Druckenmiller's stated liquidity focus | BIS SDMX API loader; BoJ API (since Feb 2026, no key); ECB/BoE CSV endpoints; H.4.1 pre-2002 only for the case-study windows | High | M |
| 9 | Data-quality monitor: freshness against the calendar, gap %, MAD outlier flags, stale runs, scale jumps, dual-source diffs, AHL-style low-vol regime filter (0.05× average vol) for pegged/controlled eras | Bad prints and pegs create false signals; AHL documents the filter | Nightly `dq_report.parquet`; engine treats flagged inputs as `unknown`; exclude FX before 1973-03 and JGB before 1972 from trend rules | High | M |
| 10 | Real-time expectations as inputs: SPF (1968→), Tealbook (5-year lag; research only), IMF WEO vintages (2007→) | Ghysels et al.: real-time survey expectations carry information about revisions; policy-error rules (R-05) need the expectations of the time | Loaders with `published_at` = release date; Tealbook flagged `available_publicly_at` = meeting + 5 years (not usable live; usable only for "what the Fed believed" labels) | Medium | S |
| 11 | Breadth pre-2021 proxy from French daily industries (1926→): % of 49 industries above their 200d average; leadership ranks of transports, retail, homebuilders and autos | No free daily NYSE A/D file; R-60 breadth thrust needs history | `interpreted` tag; validate against Alpaca-built breadth 2021→ (grade per §4.2) | Medium | M |
| 12 | Volatility proxy pre-1986/1990: realized vol from the French daily market return (Mkt-RF+RF, 1926→); VXO 1986–2021; VIX 1990→ | Vol-regime rules need history before 1990 | Fit VIX ≈ a + b·RV21 on the 1990→ overlap; grade C at most (variance risk premium varies) | Medium | S |
| 13 | AQR free series as external validation targets (TSMOM factors, VME, Century of Factor Premia, Commodities for the Long Run) | Independent checks on in-house proxies; AQR built them with paid data | Correlate in-house proxy-era trend/carry returns with AQR series per asset class; record in the validation table; respect AQR terms (credit AQR) | Medium | S |
| 14 | Calendar and timezone layer: `exchange_calendars`/`pandas_market_calendars`; every price carries `obs_time` with tz; cross-market signals on synchronized or lagged closes | Asynchronous closes bias correlations; H.10 noon NY vs ECB 14:15 CET reference | Calendar module in amber; daily cross-asset features shift non-US closes by one session | Medium | S |
| 15 | Survivorship for E5 equities: N-Q (2004–2019) + N-PORT for ETF membership; Form 25 delisting dates; delisting-return assumption flagged | D-9 otherwise survivorship-biased | Extend `core\holders.py` with an N-Q text parser; delisting table | Low | L |
| 16 | `sources.yaml` legal fields: `license`, `tos_url`, `redistribution`, `copyright_owner`, `access_method` | FRED copyright, JST NC license, IBKR non-redistributable, EDGAR fair access | Schema validation in CI; release builds refuse to bundle `redistribution: none` data | Medium | S |
| 17 | Free alternative data: IMF PortWatch (daily, no key) and Black Marble (2012→) at weight 0 | Low-cost nowcasting context; PIT by construction from capture date | Add to D-20 loaders | Low | S |

---

## 9. Free long-history sources to add

"PIT" values:

| Value | Meaning |
|---|---|
| Vintages | Real vintages exist |
| Unrevised | Market data, effectively not revised |
| Revised | Only current revised values; requires a lag rule |
| Snapshot | Revisable file; amber must store each download |

Start years and frequencies are from the cited pages unless marked (nv) = not verified this session.

| Series | Source | URL | Start | Freq | PIT | Automation notes |
|---|---|---|---|---|---|---|
| Central bank total assets, 50+ economies | BIS CBTA | https://data.bis.org/topics/CBTA | Annual median 1942, some 19th c.; monthly later | A/Q/M | Revised | BIS SDMX REST API ([docs](https://stats.bis.org/api-doc/v2/)); lag rule by country |
| Policy rates, 40+ economies | BIS CBPOL | https://data.bis.org/topics/CBPOL | 1946 (several); most daily after 1980 | D/M | Unrevised (decision dates) | SDMX; `published_at` = decision date + announcement time |
| Total credit to private non-financial sector, 40+ economies | BIS | https://www.bis.org/publ/qtrpdf/r_qt1303h.htm | 1940s–1950s for some | Q | Revised | SDMX; credit-to-GDP gap |
| Credit, money, rates, returns, crises, 18 economies | JST Macrohistory R6 | https://www.macrohistory.net/database/ | 1870 | A | Snapshot | Single xlsx/dta; CC BY-NC-SA; context and archetypes only |
| Fed balance sheet weekly (pre-2002) | H.4.1 on FRASER | https://fraser.stlouisfed.org/title/h41-factors-affecting-reserve-balances-depository-institutions-condition-statement-federal-reserve-banks-83/september-10-1964-66734 | 1940 | W | Unrevised (as published) | PDF scans; manual extraction for case windows only |
| Monetary base | FRED BOGMBASE (H.6) | https://fred.stlouisfed.org/series/BOGMBASE | 1959 (nv) | M | Vintages (ALFRED) | FRED API |
| Bank credit, all commercial banks | FRED TOTBKCR (H.8) | https://fred.stlouisfed.org/series/TOTBKCR | 1973 (nv) | W | Vintages | FRED API; H.8 Friday release |
| Financial Accounts (sector debt, equity issuance) | Fed Z.1 | https://www.federalreserve.gov/releases/z1/20150918/data.htm | 1945 annual; 1952Q1 quarterly | A/Q | Vintages (ALFRED release 52) | DDP zip; FRED for key series |
| UST yield curve (zero, par, forward) | Fed GSW | https://www.federalreserve.gov/pubs/feds/2006/200628/feds200628.html | 1961 | D | Model refit; snapshot | CSV, weekly update; input for bond TR proxy |
| Treasury bond returns from CMT | Swinkels method on FRED GS10 | https://repub.eur.nl/pub/117405/Swinkels-2019-Data.pdf | 1962 | M | Unrevised | Compute in amber; validate against GSW-based returns |
| Public debt, monthly | Treasury MSPD (Fiscal Data) | https://fiscaldata.treasury.gov/datasets/monthly-statement-public-debt/ | 2001-01 | M | Unrevised | API; 4th business day |
| Daily Treasury Statement (TGA, issuance) | Treasury DTS | https://catalog.data.gov/dataset/daily-treasury-statement-dts | 2005-10 | D | Unrevised | Fiscal Data API `/v1/accounting/dts/` |
| UK macro and finance, 130+ variables | BoE "Millennium of Macroeconomic Data" | https://www.bankofengland.co.uk/statistics/research-datasets | 1086 (annual); quarterly and monthly subsets | A/Q/M | Snapshot | Single xlsx; [datahub mirror](https://datahub.io/economic-history/millennium-macroeconomic-data-uk) |
| BoE Bank Rate, gilts, money, credit | BoE IADB | https://cran.r-project.org/web/packages/boe/refman/boe.html | Varies | D/M | Revised (money/credit) | CSV endpoint |
| Euro-area money, credit, rates, ECB balance sheet | ECB Data Portal | https://data.ecb.europa.eu/help/api/data | 1999 (EA); some earlier | D/W/M | Revised | SDMX API (`data-api.ecb.europa.eu`) |
| BoJ accounts, money stock, rates | BoJ Time-Series Data Search API | https://www.boj.or.jp/en/statistics/outline/notice_2026/not260218a.htm | Varies | D/M | Revised | API since 2026-02-18, no key |
| Global macro (IFS-derived), WEO | IMF Data Portal | https://www.imf.org/en/Data | 1948+ for some IFS (nv); WEO vintages 2007→ | M/Q/A | WEO vintages; others revised | New portal and API (May 2025); free |
| OECD MEI incl. long rates and CLI | OECD Data Explorer / FRED | https://data-explorer.oecd.org/ | 1960 (IRLTLT01) | M | ORDRD vintages 1999→ | SDMX; FRED mirrors |
| International real-time vintages | Dallas Fed (OECD MEI hard copies) | https://www.dallasfed.org/research/international/oecd | Vintages 1962Q1–1998Q4 | Q | Vintages | Excel per country and variable; splice to ORDRD |
| US real-time vintages | Philadelphia Fed RTDSM | https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists | Vintages from 1965-11 | M/Q | Vintages | Excel; first/second/third-release files |
| Professional forecasts | Philadelphia Fed SPF | https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters | 1968 | Q | Vintages (as published) | Excel |
| Fed staff forecasts | Tealbook data sets | https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/greenbook | 1966 (nv) | Per FOMC | Public after 5 years | Excel; research labels only |
| Recession dating with announcement dates | NBER | https://nber.org/research/data/us-business-cycle-expansions-and-contractions | 1854 | M/Q | Announcement dates | Static table |
| Pre-WWII US/UK/FR/DE series (3,500) | NBER Macrohistory | https://news.research.stlouisfed.org/2012/08/3036-nber-macrohistory-series-added-to-fred/ | 19th c. | M/Q/A | Unrevised (historic) | 3,036 series on FRED |
| US equity prices, dividends, earnings, CPI, rates | Shiller `ie_data.xls` | http://www.econ.yale.edu/~shiller/data/ie_data.xls | 1871 | M | Snapshot (monthly averages; interpolated E/D) | Site refused connection this session; mirror via [datahub](https://datahub.io/core/s-and-p-500) |
| Industry and factor returns (5–49 industries) | Ken French library | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html | 1926-07 | D/M | Snapshot (rebuilt monthly) | Zip CSV; store each download |
| Commodity futures excess-return index | AQR Commodities for the Long Run | https://www.aqr.com/Insights/Datasets/Commodities-for-the-Long-Run-Index-Level-Data-Monthly | 1877 | M | Snapshot | xlsx; validation target |
| TSMOM, VME, Century of Factor Premia | AQR datasets | https://www.aqr.com/Insights/Datasets/Century-of-Factor-Premia-Monthly | 1926 (factor premia); 1985 (TSMOM) (nv) | M | Snapshot | xlsx; credit AQR |
| Credit excess returns | AQR Credit Risk Premium data | https://www.aqr.com/Insights/Datasets/Credit-Risk-Premium-Preliminary-Paper-Data | 1936 (paper) | M | Snapshot | xlsx; validates the BAA spread proxy |
| Commodity prices (spot) | IMF PCPS via FRED (`PALLFNFINDEXM`) | https://fred.stlouisfed.org/series/PALLFNFINDEXM | 1992 (index) | M | Revised (minor) | FRED API; World Bank CMO (1960) already in D-16 |
| Implied vol (old method) | FRED VXOCLS | https://fred.stlouisfed.org/series/VXOCLS | 1986 (nv), ended 2021-09-23 | D | Unrevised | FRED API; one-time pull |
| HY/IG OAS | FRED ICE BofA | https://fred.stlouisfed.org/data/BAMLH0A1HYBB | Rolling 3 years from 2026-04 | D | Unrevised | Copyrighted; append-only nightly capture |
| Breadth (charts only) | StockCharts historical gallery | https://alb.stockcharts.com/freecharts/historical/marketbreadth.html | 1926–1927 (charts) | D | — | Not machine-usable; proxy instead (rec. 11) |
| Port calls and chokepoints | IMF PortWatch | https://docs.openbb.co/python/reference/economy/shipping/port_volume | 2019 (nv) | D | Capture date | ArcGIS REST; weight 0 |

---

## 10. Proxy recipes

Notation: r = monthly or daily simple return; y = yield (decimal p.a.); D = modified duration; C = convexity; s = spread; rf = local short rate.

| Target series | Proxy formula | Inputs (free) | Overlap validation | Known biases |
|---|---|---|---|---|
| UST 10y total return (pre-futures, 1962→) | r = y(t−1)/12 − D·Δy + ½·C·Δy²; D and C for a par bond at 10y maturity (Swinkels) | FRED GS10 (M), DGS10 (D); GSW for daily | vs GSW-zero-based TR and vs ZN futures (IBKR 2017→): corr, slope, R² (target R² ≥ 0.99 vs GFD per Swinkels) | CMT is on-the-run par; ignores the on/off-the-run spread and exact roll-down |
| UST futures excess return pre-futures | r_TR − rf/12, rescaled to target duration (MOP: 2/4/7/20y) | Above + TB3MS / DTB3 | vs ZN/ZB/ZF continuous excess returns 2017→ (IBKR) and 2000→ if available | CTD optionality missing; repo ≠ T-bill |
| Foreign 10y bond excess return | Same formula with IRLTLT01xx and local 3m rate (IR3TIB01xx) | OECD via FRED (1960→ for DE, GB, JP, FR, IT, CA, AU) | vs Bund/Gilt/JGB futures where available; vs AQR VME bond series | Monthly average yields (OECD) rather than end-of-month; peg/control eras need the AHL vol filter |
| FX excess return (pre-forwards, 1971→) | r = ΔS/S (USD per FCY) + (rf_foreign − rf_US)/12 | FRED DEX* daily 1971→; OECD/BIS short rates | vs CME FX futures (6E/6J/6B...) continuous excess return 2017→; sign agreement ≥ 90% | IBOR/T-bill basis; CIP deviations after 2008; Bretton Woods (exclude pre-1973) |
| Dollar index long history | Ratio-splice DTWEXM (1973–2019) → DTWEXBGS (2006→) on the 2006–2019 overlap (D-8) | FRED | Corr of monthly returns on the overlap; level-ratio stability | Basket weights differ (major vs broad) |
| Commodity excess return (single, pre-IBKR) | r = Δ(front ≥2m contract) within contract, rolled monthly (Ilmanen et al.); where only spot exists: r ≈ ΔSpot − carry proxy (zero) → grade C | World Bank CMO (1960→, spot); EIA; IBKR 2017→ | vs AQR Commodities-for-the-Long-Run index and GSCI/BCOM published levels: corr of monthly returns | Spot-only ignores roll yield, a large component for energy and ags (AHL note) |
| Broad commodity index pre-2017 | Equal or production-weighted average of the single-commodity proxies | Same | vs AQR CLR (1877→), PALLFNFINDEXM (1992→) | Weights drift; spot vs futures |
| IG credit excess return | r_xs ≈ s(t−1)/12 − D_s·Δs, with s = BAA − DGS10 (or BAA − AAA for the quality spread) and D_s ≈ 7–8 (assumption) | FRED BAA, AAA (1919→), DGS10/GS10 | vs AQR credit premium series (1936→); vs LQD − IEF excess return (2002→) | Moody's yields are long-maturity seasoned bonds; no default loss in the formula (overstates; Swinkels caution); duration assumed |
| HY excess return pre-1996 | Not reconstructable from free data | — | — | Mark `unknown` (grade D); use BAA−AAA as the stress proxy |
| Equity index excess return | r = TR − rf/12 | French Mkt-RF (1926→ daily); Shiller (1871 monthly) | vs SPY/ES excess return 2017→: corr ≥ 0.99 expected | French market is CRSP all-share value-weighted, not S&P 500; Shiller prices are monthly averages (smoothing) |
| Sector leadership | Relative return of FF49 industries (transports, retail, homebuilding, autos, banks) vs market | French 49 industries daily 1926→ | vs SPDR sector ETFs (1998→) relative returns: corr, rank agreement | SIC-based industries ≠ GICS; composition drift |
| Breadth | % of FF49 industries above 200d MA; up-industries/(up+down) thrust | French daily | vs Alpaca-built NYSE-like breadth 2021→ | 49 portfolios are not about 3,000 issues; overstates breadth persistence |
| Implied vol pre-1990 | VIX_hat = a + b·RV21(market) fitted on 1990→; VXO 1986–1990 directly | French daily market; FRED VXOCLS, VIXCLS | Fit R² and residual vol on 1990→; sign of Δ agreement | Variance risk premium is time-varying; VXO ≠ VIX (OEX at-the-money vs SPX strip) |
| Net liquidity pre-2002 (era B) | ΔWRESBAL/BOGMBASE-based proxy, or H.4.1 FRASER extracts for case windows; else M2−IP (R-02) | FRED BOGMBASE (1959→), H.4.1 scans | Overlap 2002→: corr(Δ proxy, Δ(WALCL − WTREGEN − RRP)) | Base ≠ net liquidity; TGA unavailable pre-1993 except from scans |

---

## 11. Gaps recorded

- Bridgewater splice and proxy methodology is not public. The CWO bibliography PDF did not load (redirect). [G]
- Winton and Campbell data-construction papers were not located. The Greyserman/Kaminski book was not read. [G]
- Ilmanen *Expected Returns* data appendix: not read. [G]
- Baltas-Kosowski roll convention: not verified. [G]
- Shiller site refused connection on this date; the data description comes from secondary R documentation. [G]
- No published fund "grading tier" scheme for proxies was found. §4.2 is a design proposal. [I]
- Start years marked (nv) in §9 need confirmation from the API's `observation_start` during ingest.
