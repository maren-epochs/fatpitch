# Research: D1, D3, D7 (open parameter questions)

Date: 2026-10-06. Scope: `liq.m2_ip.spread_pp` (and `liq.growth_window_m`) for R-02; `xasset.window_m` for R-10; the breadth source and definition behind `internals.breadth_thrust` for R-60. Nothing in `registry.yaml`, `process.md`, `transition_table.yaml`, `cases\`, `src\` or `tests\` was changed.

Leakage control: no value below was chosen by checking engine output, market returns, or agreement with Druckenmiller's calls in `cases\`. The evidence used is limited to (1) his own words, (2) literature and practitioner definitions, and (3) descriptive statistics of the input series (distribution, persistence, crossing frequency). One point needs stating. Some evidence comes from his own description of the 2000 episode (what he saw on returning from the summer break). That is his account of his reasoning. It was used for the horizon he described. No test was run of whether the rule fires on that date.

Scripts and raw outputs (all in `tools\research\`, reading amber's lake read-only):

| File | Purpose |
|---|---|
| `d1_m2_ip_stats.py` / `.out.txt` | L2 = yoy(M2SL) − yoy(INDPRO): distributions, thresholds, spells; real-time (ALFRED) and revised; alternative windows; M2 − nominal GDP companion |
| `d3_xasset_stats.py` / `.out.txt` | joint rise of DGS10, WTI, USD over 1/3/6/12 months, 1973–2026 monthly and 1986–2026 daily |
| `d3_magnitude.py` / `.out.txt` | same, with each move required to exceed k standard deviations |
| `d7_breadth_loader.py` | prototype loader: Unicorn NYSE A/D archive (1965–2020) and WSJ Markets Diary live JSON |
| `d7_breadth_stats.py` / `.out.txt` | data-quality checks; Zweig thrust counts on NYSE; S&P 500 member breadth from Alpaca × N-PORT 2021+ |
| `d7_threshold_mapping.out.txt` | NYSE vs S&P-member EMA distributions; frequency-matched Zweig thresholds |
| `d7_gap_yahoo_probe.py` / `.out.txt` | survivorship probe for filling 2020-02..2021-09 from Yahoo prices |
| `sample_data\` | `unicorn_nyse_breadth.csv` (13,867 days), `sp500_breadth_alpaca.csv` (1,264 days), `wsj_marketsdiary_snapshots.csv` (1 row) |

---

## D1 — `liq.m2_ip.spread_pp` (R-02) and `liq.growth_window_m`

### Evidence: his words

| Source | What he says | Number? |
|---|---|---|
| Feig 2009 (`DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md`; transcript at aletteraday Letter #300) | "But this liquidity that they're putting in there, you can't go, Oh, the economy stinks so I hate the stock market. It doesn't work. This thing--if you have the money supply growing a lot faster than industrial production, the stock market is generally going to go up. That's just the way it works. That's where the money goes." | none; no aggregate, window or magnitude |
| Barron's 1988 / New Market Wizards (via Macro Ops) | "Earnings don't move the overall market; it's the Federal Reserve Board… focus on the movement of liquidity." | none |
| ECNY 2020 (Felder excerpt) | net liquidity = Fed purchases vs Treasury issuance (~$1T Mar–Apr 2020) | dollar flows, not a growth spread |
| Sohn 2023 (GuruFocus notes) | "Money supply was still far above pre-COVID levels" | level comparison, no threshold |
| Bloomberg 2024 | "the ten year's to trade around where nominal GDP is" | a rates anchor, not money vs output |

A search of the library notes and the web found no other place where he puts a number on excess liquidity: no M2-vs-IP figure, no M2-vs-nominal-GDP figure, no Marshallian K. "A lot faster" is unquantified. The context of the quote matters, though. He is contrasting money growth with a weak economy, so the comparison is directional and relative ("faster than"), and "a lot" implies a margin above the usual relationship.

### Evidence: literature and practitioner conventions

| Source | Measure | Window | Threshold |
|---|---|---|---|
| SentimenTrader (J. Goepfert, 2021-06-04) | M2 growth minus industrial production growth (the R-02 construction) | not stated (yoy implied) | 10 pp flagged as the strong zone. This is a return-fitted threshold, cited here only as a convention. |
| Ned Davis-style "excess liquidity" (NelsonCorp) | yoy M2 − (yoy IP + yoy PPI commodities) | 12 m | brackets not published |
| Simon Ward (Janus Henderson, moneymovesmarkets.com, 2024-11-08) | real narrow money growth − industrial output growth | 6 m preferred | 0 (sign) |
| Simon White (Bloomberg) | G7 real M1 yoy − IP yoy, read as deviation from trend | 12 m | sign of deviation |
| Baks & Kramer (1999, IMF WP/99/168); Rüffer & Stracca (2006, ECB WP 696) | money growth − nominal GDP growth (Marshallian k growth) / P-star money gap | yoy | continuous, no threshold |

The academic and practitioner convention is the sign (threshold 0) on a measure that has no structural drift: real money vs real output, or nominal money vs nominal GDP. R-02 mixes nominal M2 with real IP, so it carries a positive drift equal to inflation plus the growth gap between GDP and IP. A 0 threshold on R-02 therefore does not mean what 0 means in the literature.

### Evidence: descriptive statistics of L2 (12-month window)

Data: FRED M2SL and INDPRO from amber's lake. Real-time = the ALFRED vintage in force at each month-end (M2SL vintages start 1980-02). Revised = current vintage.

| Statistic | Revised 1960–2026 | Revised, excl. 2020-03..2021-12 | Real-time 1980–2026 |
|---|---|---|---|
| n (months) | 800 | 778 | 559 |
| mean / sd | 4.42 / 6.12 | 3.98 / 5.23 | 4.35 / 6.68 |
| p10 / p25 / p50 / p75 / p90 | −1.96 / 0.89 / 3.37 / 6.84 / 11.86 | −2.01 / 0.80 / 3.31 / 6.55 / 10.67 | −2.48 / 0.35 / 3.37 / 6.69 / 12.31 |

Share of months above each threshold, with spell lengths (real-time 1980–2026):

| Threshold (pp) | Share above | Spells | Median spell (months) |
|---|---|---|---|
| 0 | 77% | 22 | 15.5 |
| 1 | 67% | 20 | 19.5 |
| 2 (current) | 58% | 18 | 18.5 |
| 3 | 53% | 19 | 13.0 |
| 4 | 44% | 21 | 8.0 |
| 5 | 35% | 22 | 7.5 |
| 6 | 29% | 17 | 8.0 |
| 7 | 23% | 12 | 9.5 |

Further facts:

- **Drift by era.** The median L2 differs by period: 1960–79 2.8, 1980–99 2.5, 2000–19 4.2 (IP stagnated as manufacturing's share fell), 2022–26 2.5. Over 1960–2026, M2 yoy has a median of 6.6 and IP yoy a median of 2.6.
- **Which side drives L2.** IP drives most of the variance: var(IP)/var(L2) = 0.60 and var(M2)/var(L2) = 0.38, with corr(M2, IP) ≈ 0. Recessions, through IP collapses, push L2 up as much as monetary expansion does.
- **Revision noise.** Real-time minus revised L2 has a median absolute difference of 1.25 pp, and the 90th percentile of the absolute difference is 2.9 pp. Threshold differences under about 1 pp are inside revision noise.
- **Persistence.** Autocorrelation is 0.96 at 1 month, 0.83 at 3, 0.62 at 6 and 0.11–0.16 at 12. The 12-month window gives a regime-length signal.
- **2020–21.** L2 peaked at 38.0 pp in 2020-05, then fell to 1.7 in 2021-04 and −1.6 in 2021-05 as IP base effects reversed, before returning to 7–10 in late 2021. This is a base-effect episode, not a data break.
- **Correction to the R-02 PIT note.** The Feb-2021 H.6 change (savings deposits moved into M1 from May 2020) raised M1 by about $11.2T and **left M2 unchanged** (Federal Reserve H.6 technical Q&A). M2SL has no definitional break in May 2020. `process.md` R-02 should drop the "definitional break" wording and keep a flag for the 2020-03..2021-12 base-effect outliers. The change was not made here because process.md is out of scope.
- **M2 − nominal GDP (Marshallian k growth), quarterly 1960–2026.** Median 0.05 pp, p75 2.3, p90 4.5; 50% of quarters are above 0. This confirms that the drift in R-02 comes from using real IP.

Alternative windows (revised L2): changes in the 3-state impulse at a 2 pp threshold:

| Window | Changes per decade | Sign changes per decade | Lag-6 autocorrelation |
|---|---|---|---|
| 12 m | 15.0 | 4.6 | 0.62 |
| 6 m annualised | 24.3 | 10.9 | 0.21 |
| 3 m annualised | 30.3 | 19.3 | — |
| 24 m annualised | 8.8 | 2.7 | 0.81 |

### Recommendation

**Point value 3.5 pp, tunable over [1, 7] (the owner's range).**

- **Why 3.5.** "A lot faster" has to mean faster than M2 normally outgrows IP. The normal gap is about 3.4 pp (the real-time and revised median). 3.5 is the smallest round value above that median. It makes the positive impulse "above the historical norm": about half of months (53% at 3; 44% at 4). The negative leg stays at < 0 (about 23% of months), and the neutral band covers the rest.
- **Why [1, 7].** The range runs from the real-time 27th percentile to the 77th. Below 1, the positive leg covers two-thirds of all months and nearly coincides with "any excess at all". Above 7, positive states become short (median about 9 months), and the threshold sits where the 2020-type outliers dominate. Step 1 pp; finer steps are inside revision noise.
- **Window: keep `liq.growth_window_m` = 12.** It matches the practitioner convention for M2 vs IP (SentimenTrader, Ned Davis), removes seasonality, and halves state changes relative to 6 m (15 vs 24 per decade). Ward's 6 m preference applies to real narrow money, which is a different aggregate. 24 m would lag regime changes by about a year.

### Options (recommended first)

| Option | Value / range | Note |
|---|---|---|
| **A (recommended)** | 3.5, tunable [1, 7] | "a lot faster" = above the historical median gap; owner's range = p27–p77 |
| B | keep 2.0, tunable [0, 6] | 2.0 sits at about the 42nd percentile, below the typical gap, so "a lot faster" fires in a majority of months |
| C | 5.0 fixed | top third of months; frees a tunable slot; no source for "a third" |
| D | relative threshold: L2 above its trailing 120-month median (spec change) | removes the era drift (2000–19 median 4.2 vs 2.5 elsewhere); closest to the Bloomberg "deviation from trend" convention; needs a process.md edit and is not a single number |

Caveats: M2SL vintages begin in 1980, so 1960–79 L2 is revised data only. The pre-1980 M2 is the 1980 definition back-cast. The structural drift means any fixed pp threshold is stricter in low-inflation, high-IP eras.

---

## D3 — `xasset.window_m` (R-10: rates, oil and USD all rising)

### Evidence: his words, with time frame

| Source | Words | Horizon described |
|---|---|---|
| Feig 2009 (aletteraday #300) | "I came back in late August, right around Labor Day. And oil was screaming upward, interest rates were screaming upward." Hyman: "Earnings are going to be down 36% in the next 12 months." The break: "The four months off had really helped." | moves seen **since he left about four months earlier** (summer 2000); 12 months is the *earnings forecast* horizon, not the input window |
| NBIM *In Good Company* 2024 (podscripts transcript) | "I come back and… the dollar is up, interest rates are up, and oil is up, three death knells for markets, if you look at history." Hyman regression "50%, I think, currency, 25% oil and 25% interest rates, and it looks one year forward." | "come back" = since the summer break (he refused to look at markets that summer); the forecast looks one year forward |
| Sohn 2022 (aletteraday #40) | "Oil is up. Interest rates are up. And the dollar is up. By the way, that might sound a little familiar." Hyman "plugged in the percentages… and the dollar up this amount, earnings the next year forward… go down 35%." | inputs are percentage changes of unstated length; the forecast is one year forward |
| Real Vision 2018 (HFA notes) | "the price of oil is going up, the dollar is going way up, and interest rates were going up… this particular cocktail had always been negative for earnings" | none; "way up" implies magnitude |

Conclusions from his words:

- The only time-anchored account is the summer-2000 break: about 4 months (Feig: "four months off"). That points to a 3–6 month window.
- "Screaming upward" and "way up" describe large moves, not any positive change.
- The one-year horizon he names is Hyman's forecast horizon. It is not the change window. The input window of Hyman's regression was not found. ISI's usual practice would be year-over-year changes, but that is unverified.
- He does not say which rate. In 2000 the policy rate rose through May while long yields fell after January. R-10 uses DGS10, which is an interpretation. This was not tested against the episode.

### Evidence: literature

- BCA Research (2023-09-21, "Triple whammy for US stocks"): rising oil, a rising dollar and rising US yields as a joint headwind. No window was found in the public summary.
- Financial conditions indices (Goldman FCI: policy rate, 10y, credit, equities, trade-weighted USD) are weighted by estimated impact on GDP growth over the following year. FCI "impulse" is usually read over 12 months.
- Hamilton (1996, 2003) "net oil price increase": oil above its 12-month (or 36-month) maximum. That is a 12 m convention for oil shocks.

The literature therefore leans to 12 m, while his own account leans to about 4 m.

### Evidence: descriptive statistics

Monthly 1973-01..2026-09. Rates = DGS10 month-end. Oil = DCOILWTICO 1986+, chained to World Bank CMO WTI (1982–85) and the crude average (1973–81). USD = DTWEXM chained to DTWEXBGS at 2006-01.

| Window | Share of months all three up | Expected if independent | Spells | Median / max spell (months) |
|---|---|---|---|---|
| 1 m | 12.9% | 11.4% | 73 | 1 / 3 |
| 3 m | 14.2% | 14.1% | 46 | 2 / 5 |
| 6 m | 15.6% | 14.6% | 39 | 2 / 8 |
| 12 m | 16.6% | 14.6% | 24 | 3.5 / 14 |

Daily evaluation 1986–2026 (business-day windows):

| Window | Share of days | On/off changes per year | Spells ≥ 20 days |
|---|---|---|---|
| 21 bd | 13.6% | 17.3 | 5 |
| 63 bd | 15.6% | 11.2 | 24 |
| 126 bd | 13.6% | 7.0 | 15 |
| 252 bd | 15.8% | 3.3 | 13 |

Magnitude floor (1986–2026 monthly; each move > k × its own w-month change sd):

| Window | k = 0 | k = 0.25 | k = 0.5 |
|---|---|---|---|
| 3 m | 14.4% | 8.0% | 4.1% |
| 6 m | 14.9% | 7.7% | 3.5% |
| 12 m | 15.5% | 7.8% | 3.6% |

Findings:

- **Frequency barely depends on the window.** The pure-sign condition holds in about 1 month in 7 at every window, close to what independence would give. Pairwise correlations of changes are 0.1–0.27 between rates and the other two, and −0.1 to −0.15 between oil and USD. On its own the sign condition is weakly selective.
- **What the window changes is persistence.** At 3 m the daily signal switches on or off about 11 times a year, with a median spell of 2 business days. At 6 m it is 7 times a year; at 12 m, 3.3. Because R-10 fires T08 directly with no confirmation, a 3 m window produces many short firings.
- **A magnitude floor, not the window, sets selectivity.** A floor of 0.25 sd halves frequency at every window. This matches his "screaming"/"way up" wording, but it is a new parameter and a spec change.

### Recommendation

**Point value 6 months, tunable over [3, 12].** 6 m is the nearest standard window to his only dated account: moves seen over a summer break of about 4 months. It halves daily state changes compared with 3 m (7 vs 11 per year) and stays inside the range from his anchor to the 12 m FCI and oil-shock conventions. Keep [3, 12] so leave-one-episode-out covers both readings. A separate proposal, outside this parameter: add a magnitude floor, e.g. each move > 0.25 sd of its w-month change, as a new interpreted parameter. His words describe large moves, and without a floor the rule fires about 15% of the time at any window.

### Options (recommended first)

| Option | Value / range | Note |
|---|---|---|
| **A (recommended)** | 6, tunable [3, 12] | nearest to his ~4-month account; halves daily state changes vs 3 m |
| B | keep 3, tunable [3, 12] | also consistent with ~4 months; about 11 daily state changes per year, median spell 2 business days |
| C | 12 fixed | literature convention (FCI impulse, Hamilton); fewest state changes; farthest from his own account |
| D | 3, tunable [1, 12] | adds 1 m, which is mostly noise (median spell 1 month, 17 daily state changes per year) |

Caveats: the USD splice changes basket in 2006 (major-currency to broad). Pre-1986 oil is monthly average, not month-end. The choice of rate tenor (DGS10 vs a policy or short rate) is open and not addressed by this parameter.

---

## D7 — breadth data source and breadth-thrust definition (R-60)

### Evidence: his words

- Bloomberg 2015: "Whenever I've seen a stock market explode on record volume and record breadth… 6 to 12 months down the road, you're out of recession."
- CNBC 2020-06-08: a "breadth thrust" changed his mind.
- Feig 2009: "13 new highs and 242 new lows" (2000), an exchange-level new-highs/new-lows read.
- NBIM 2024: leadership narrowing as a necessary condition for a bear market.

His language is exchange-level breadth plus volume. That favours NYSE advance/decline and up/down volume over industry proxies.

### Sources checked

| Source | Coverage | Frequency | Licence / terms | Automation without login | Survivorship | Verdict |
|---|---|---|---|---|---|---|
| **Unicorn Research advdec archive** `http://unicorn.us.com/advdec/NYSE_{advn,decln,unchn,advv,declv,unchv,newhi,newlo}.csv` (also AMEX, NASDAQ) | NYSE issues and volume 1965-03-01..2020-02-10 (13,867 days; only 1968 short at 226 days, the paperwork-crisis closures; one gap, 9/11). New highs/lows from 2005-10. | daily | free download, no licence text; site says it "stopped functioning… Historical data up to 10 February 2020 can still be downloaded" | **yes**: plain HTTP (the HTTPS certificate has expired); fetched by the prototype | none (exchange counts) | **primary for 1965–2020** |
| **WSJ Markets Diary JSON** `wsj.com/market-data/stocks/marketsdiary?id={"application":"WSJ","marketsDiaryType":"overview"}&type=mdc_marketsdiary` | today only: NYSE and Nasdaq advancing, declining, unchanged, new highs/lows, up/down/total volume | daily snapshot | WSJ terms restrict automated and commercial use; personal-research use only | **yes** for today; date parameters are ignored, so no history. Old `mdc/public/page/2_3021-tradingdiary2-YYYYMMDD.html` archive pages return 403; Wayback was offline when checked, so not verified | none | **forward collector** (daily job from 2026-10) |
| **amber: Alpaca daily bars × N-PORT SPX holdings** (`alpaca_basic\bars_daily`, `sec_edgar\nport_hist\S000004310-*`) | 2021-09-22..2026-10-05 (Alpaca basic starts 2021-09-21); 21 quarter-end snapshots; 488–502 of about 503 members priced | daily | owner's existing data | yes (local) | point-in-time membership (quarterly; carried forward) | **primary for S&P 500 % advancing and % above 50/200 dma, 2021-09+** (% > 50dma from about 2021-12; % > 200dma from 2022-07) |
| fja05680/sp500 constituents (GitHub, MIT) + Yahoo chart API prices | membership 1996-01-02..2026-08-18; prices only for tickers still on Yahoo | daily | MIT (membership); Yahoo terms restrict automated use | yes, unofficial endpoint | **material**: for 2020-05-22 members, 441/505 (87%) returned 2020–21 bars. Missing names are renames (FB, ANTM, ABC, BLL), acquisitions (ATVI, XLNX, TWTR, CERN, KSU, MXIM…), failures (SIVB, FRC), and some live tickers lost to throttling | **fallback for the 2020-02..2021-09 gap only**, flagged |
| Dow 30 (Wikipedia change list + Yahoo) | 1990s+ feasible; older members mostly not on Yahoo | daily | as above | yes | low for recent decades; granularity 1/30 | not recommended: 30 names make a coarse thrust and his words are exchange-level |
| Nasdaq Data Link `URC/*` (Unicorn mirror) | historical | — | free account needed | no (anonymous limit; bot-blocked) | — | rejected (login) |
| FRED | — | — | — | — | — | no exchange breadth series found |
| Yahoo `^ADD`/`C:ISSU` style symbols | — | — | — | `^ADD` not found; `C:ISSU` returns zeros | — | rejected |
| Stooq | — | — | — | now behind a JavaScript proof-of-work page | — | rejected |
| Barchart `$ADVN` / `$ADRN`, McClellan, Pinnacle | 2000+ / long | daily | download requires membership or purchase | no | none | rejected (paid or login) |
| CBP copies in amber (`cbp\`) | no breadth data (FRED monthly, FX, French, Shiller, CMO, VIX) | — | — | — | — | none |

### Data checks (descriptive)

- **Zweig thrusts on NYSE (Unicorn).** The rule is a 10-day EMA of adv/(adv+dec) rising from < 0.40 to > 0.615 within 10 days. It finds 11 thrusts in 1965–2020: 1971-12, 1974-10, 1975-01, 1982-08, 1984-08, 2004-05, 2009-03, 2011-10, 2013-10, 2015-10, 2019-01. The list includes the widely reported Aug-1982, Aug-1984, Mar-2009, Oct-2015 and Jan-2019 signals, which supports the integrity of the data. The EMA is below 0.40 on 6.3% of days and above 0.615 on 2.1%.
- **NYSE thresholds do not carry over to S&P 500 members.** On S&P 500 members (2021-09+) the EMA is more dispersed: p99 0.658 vs 0.629 on NYSE, and above 0.615 on 6.6% of days vs 2.1%. Raw Zweig thresholds fire 3 times in 4 years. Thresholds matched to NYSE crossing frequency are lo = 0.40 and hi = 0.646, which gives one thrust (2022-10-25). The sample is short (4 years), so the matched hi is provisional.
- **% of S&P 500 above 50 dma**, thrust from < 20% to > 80% within 50 days: 3 occurrences in 2021-11..2026-10.
- **Gap.** No free survivorship-free breadth exists for **2020-02-11..2021-09-21**. The 2020-06-08 statement cited by R-60 falls in this gap. This is a stated data gap, not a test result.

### Recommended source plan

1. **Primary, 1965-03 → 2020-02-10:** Unicorn NYSE issues and up/down volume (prototype `d7_breadth_loader.py unicorn`). These are exchange-level counts with no survivorship bias, and they are the inputs Zweig defined the thrust on.
2. **Primary, 2021-09-22 → now:** S&P 500 members from amber (Alpaca × N-PORT SPX): % advancing, % above 50/200 dma. Use the PIT rule that membership takes effect at the N-PORT filing date, not the report date.
3. **Forward, 2026-10 → :** a daily WSJ Markets Diary snapshot (`d7_breadth_loader.py wsj`, run after 16:30 ET). This restores NYSE adv/dec/volume going forward, so the NYSE series can resume as primary once enough history builds.
4. **Gap 2020-02-11 → 2021-09-21:** the existing industry proxy (French-49, current `internals.breadth_thrust`). The fallback is S&P 500 members from fja05680 + Yahoo with about 13% of names missing, flagged `survivorship_affected`.

### Recommended definition

**R-60 thrust = classic Zweig breadth thrust**, computed on the NYSE source where it exists:

- 10-day EMA of adv/(adv+dec) rises from < 0.40 to > 0.615 within 10 trading days.
- On S&P 500 member data, use frequency-matched thresholds: < 0.40 to > 0.646, reported provisional.
- In the gap, use the industry adaptation.
- Optional volume confirmation for his "record volume": up-volume share of NYSE volume, from the same Unicorn and WSJ files.
- Report "% of S&P 500 above 50 dma rising from < 20% to > 80% within 50 days" as a sensitivity.

How far back each definition can be computed:

| Definition | Free history |
|---|---|
| Zweig on NYSE issues | 1965-03 → 2020-02; then 2026-10 → (forward collection) |
| Up-volume thrust on NYSE | 1965-03 → 2020-02; 2026-10 → |
| NYSE new highs / new lows | 2005-10 → 2020-02; 2026-10 → |
| Zweig on S&P 500 members | 2021-09 → |
| % S&P 500 above 50 dma thrust | 2021-12 → (1996 → with Yahoo, survivorship-biased) |
| % S&P 500 above 200 dma | 2022-07 → |
| Industry thrust (current) | 1926 → (French-49 daily) |

### Options (recommended first)

| Option | Definition / source | Note |
|---|---|---|
| **A (recommended)** | Zweig on NYSE A/D (Unicorn 1965–2020; WSJ forward); S&P-member Zweig with matched thresholds 2021-09+; industry proxy in the 2020-02..2021-09 gap; % > 50dma thrust and up-volume reported as sensitivities | closest to his "record breadth/volume"; free; the gap is explicit |
| B | keep the industry definition (< 20% → > 80% of industries above trend within 10 weeks) everywhere; report NYSE Zweig as sensitivity | one consistent series 1926→, but not his measure |
| C | % of S&P 500 above 50 dma thrust only | short free history (2021-12→) unless Yahoo survivorship bias is accepted |
| D | Dow 30 reconstructed | small, easy, but coarse (1/30 steps) and not exchange-level |

Caveats:

- NYSE issue counts include closed-end funds, preferreds and ETFs. The Zweig thresholds were set on this mix, which is why they do not port unchanged to S&P members.
- The Unicorn archive is frozen and has no licence text. Cache it once; do not rely on the site staying up.
- The WSJ endpoint is undocumented and may change. Its terms restrict automated use.
- Alpaca basic bars appear unadjusted, so a split day shows as a false decline for that stock (a few per year among 500 names).
- N-PORT membership is quarterly, so intra-quarter index changes are missed.

---

Sources: [Letter #300, Druckenmiller–Feig 2009](https://aletteraday.substack.com/p/letter-300-stan-druckenmiller-and) · [Letter #40, Sohn 2022 Collison](https://aletteraday.substack.com/p/letter-40-john-collison-and-stan) · [NBIM In Good Company 2024 transcript](https://podscripts.co/podcasts/in-good-company-with-nicolai-tangen/stan-druckenmiller-inside-the-mind-of-a-legendary-investor) · [Macro Ops on Druckenmiller liquidity](https://macro-ops.com/stanley-druckenmiller-on-liquidity-macro-margins/) · [Fed H.6 technical Q&A](https://www.federalreserve.gov/RELEASES/h6/h6_technical_qa.htm) · [SentimenTrader excess liquidity](https://sentimentrader.com/blog/excess-liquidity-is-draining-from-the-market) · [NelsonCorp excess liquidity](https://nelsoncorp.com/indicator-insights/excess-liquidity/) · [Money Moves Markets, assessing excess liquidity](https://moneymovesmarkets.com/insight/nsp-assessing-excess-liquidity-reasons-for-caution/) · [BCA triple whammy](https://www.bcaresearch.com/reports/triple-whammy-us-stocks-21-09-2023/110281) · [BIS on FCIs](https://bis.org/publ/qtrpdf/r_qt1812s.htm) · [Hamilton, What is an oil shock?](https://projects.nber.org/papers/w7755) · [Unicorn advdec](http://unicorn.us.com/advdec/) · [WSJ Markets Diary](https://www.wsj.com/market-data/stocks/marketsdiary) · [fja05680/sp500](https://github.com/fja05680/sp500)
