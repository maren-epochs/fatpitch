# Data coverage: step 1 and 1b inputs (amber lake, point-in-time)

Generated 2026-10-07 by `python -m fatpitch.lake_coverage` from `spec\data_catalogue.yaml` over `<AMBER_DATA>\lake` through `fatpitch.lake.AmberLakeSource`. Do not edit by hand.

Definitions. *First usable PIT*: earliest date on which a snapshot at 16:00 ET returns at least one row with `usable = true` (published_at <= asof; D-graded proxies and pre-vintage rows under policy `unknown` excluded); fallbacks count, with their grade shown. *Method / grade at start*: method and proxy grade of the newest usable row on that date. *Largest gap*: largest spacing between consecutive usable periods in the full-history snapshot, shown when above 2.5x the nominal spacing. Availability at a case date additionally requires the newest usable period to be no older than the larger of D 10 d, W 21 d, M 75 d, Q 200 d, A 760 d (by catalogue frequency) and the rows' own cadence (median publication lag + 1.5 x median spacing + 7 d; freshness bound). RRPONTSYD and WSHOMCB count as available (zero) before their first observation (process.md R-03, R-04).

Snapshot performance: step-1 set (67 ids), weekly asofs 1960-01-04 -> 2026-10-07 (3483 snapshots), warm cache: **9.5 ms per snapshot** (target < 50 ms).

## 1. Inputs

| Id | Step | Rules | Status | Freq | First usable PIT | Method / grade at start | Vintage source by era | Largest gap | Catalogue gaps |
|---|---|---|---|---|---|---|---|---|---|
| M2SL | 1 | R-02 | available | M | 1971-06-01 | vintage / A | asof >= 1980-02-08 ALFRED; 1971-05-31 <= asof < 1980-02-08 Philadelphia Fed RTDSM (m2, quarterly vintages, pre-1980 M2 definition); earlier: none |  |  |
| INDPRO | 1 | R-02 | available | M | 1927-01-26 | vintage / A | asof >= 1927-01-26 ALFRED (RTDSM ipt 1962-11 never reached) |  |  |
| INDPRO_FR | 1 | R-02 | available | M | 1927-01-26 | vintage / A | earliest ALFRED spell per period (1927-01-26 ->); periods before 1927 carry the 1927 initial vintage, not a true first release |  |  |
| WALCL | 1 | R-03, R-12 | available | W | 1915-02-14 | lag_rule / B | latest lake values (release_calendar) |  |  |
| US_CB_ASSETS_M | 1 | R-03, R-12 | available | M | 1915-02-14 | lag_rule / A | latest lake values (lag_rule) |  |  |
| WTREGEN | 1 | R-03 | available | W | 2002-12-20 | release_calendar / A | latest lake values (release_calendar) |  |  |
| LDGUST | 1 | R-03 | available | W | 1915-01-16 | lag_rule / A | latest lake values (lag_rule) | 1975-07-30 -> 1975-08-20 (21 d) |  |
| RRPONTSYD | 1 | R-03 | available | D | 2003-02-08 | lag_rule / A | latest lake values (first_release) | 2004-01-09 -> 2007-04-26 (1203 d) | sparse before 2013-09 (operation days only); none before 2003-02-07 (process.md: 0 before) |
| NETLIQ | 1 | R-03 | proxy_only | Q | 1946-03-17 | lag_rule / C | latest lake values (lag_rule) | 1947-12-31 -> 1948-12-31 (366 d) |  |
| TREAST | 1 | R-04, R-14 | available | W | 1946-03-14 | lag_rule / C | latest lake values (release_calendar) |  |  |
| BOGZ1FL713061103Q | 1 | R-04 | available | Q | 1946-03-14 | lag_rule / A | latest lake values (lag_rule) | 1947-12-31 -> 1948-12-31 (366 d) |  |
| WSHOMCB | 1 | R-04, R-14 | available | W | 2002-12-20 | release_calendar / A | latest lake values (release_calendar) |  |  |
| TFD_DEBT_HELD_PUBLIC | 1 | R-04, R-63 | available | D | 1970-06-07 | lag_rule / C | latest lake values (release_calendar) | 1997-09-30 -> 1998-09-30 (365 d) | held-public split null 1993-04..1997-09 (total debt only) |
| TFD_NET_ISSUANCE_13W | 1 | R-04, R-63 | available | D | 2005-07-01 | release_calendar / A | latest lake values (release_calendar) |  |  |
| TFD_NET_MARKETABLE_M | 1 | R-04, R-63 | available | M | 2001-03-07 | release_calendar / A | latest lake values (release_calendar) |  |  |
| FYGFDPUN | 1 | R-04 | available | Q | 1970-06-07 | lag_rule / A | latest lake values (first_release) |  |  |
| FEDFUNDS | 1 | R-06, R-08, R-14, R-23 | available | M | 1954-08-04 | lag_rule / A | latest lake values (first_release) |  |  |
| DFF | 1 | R-06, R-08, R-23 | available | D | 1954-07-03 | lag_rule / A | latest lake values (first_release) |  |  |
| DFEDTARU | 1 | R-14 | available | D | 1982-09-29 | lag_rule / A | latest lake values (first_release) |  | no target series before 1982-09-27 (use FEDFUNDS) |
| DFEDTAR | 1 | R-14 | available | D | 1982-09-29 | lag_rule / A | latest lake values (lag_rule) |  |  |
| DFEDTARL | 1 | R-14 | available | D | 2008-12-18 | first_release / A | latest lake values (first_release) |  |  |
| CPIAUCSL | 1 | R-06, R-07, R-08, R-09 | available | M | 1913-02-20 | lag_rule / C | asof >= 1972-07-21 ALFRED; earlier: CPIAUCNS (NSA, unrevised) fallback |  |  |
| CPIAUCNS | 1 | R-07 | available | M | 1913-02-20 | lag_rule / A | latest lake values (first_release) |  |  |
| CPILFESL | 1 | R-06 | **missing** | M | - | - | - | - | Not in the lake (sensitivity input only, process.md R-06). Gap. |
| UNRATE | 1 | R-06, R-63 | available | M | 1960-03-15 | vintage / A | asof >= 1960-03-15 ALFRED (RTDSM ruc 1965-11 never reached); earlier: none |  |  |
| UNRATE_FR | 1 | R-06 | available | M | 1960-03-15 | vintage / A | latest lake values (first_release) |  |  |
| NROU | 1 | R-06, R-63 | available | Q | 1949-04-01 | lag_rule / A | asof >= 2011-02-02 ALFRED (25 vintages); earlier: latest CBO vintage, usable (approximation accepted in process.md 10.3, R-06) |  |  |
| GDPPOT | 1 | R-06 | available | Q | 1991-01-31 | vintage / A | asof >= 1991-01-30 ALFRED; earlier: none |  |  |
| GDP | 1 | R-11, R-56 | available | Q | 1965-12-01 | vintage / A | asof >= 1991-12-04 ALFRED; 1965-11-30 <= asof < 1991-12-04 RTDSM noutput (quarterly vintages; GNP before 1992); earlier: none |  |  |
| DGS10 | 1 | R-10, R-17, R-56 | available | D | 1953-05-04 | lag_rule / B | latest lake values (first_release) |  |  |
| DGS2 | 1b | R-17, R-23 | available | D | 1976-06-03 | lag_rule / A | latest lake values (first_release) |  |  |
| DGS1 | 1b | R-23 | available | D | 1962-01-04 | lag_rule / A | latest lake values (first_release) |  |  |
| DGS3MO | 1b | R-17 | available | D | 1981-09-03 | lag_rule / A | latest lake values (first_release) |  |  |
| GS10 | 1 | R-10, R-17 | available | M | 1953-05-04 | lag_rule / A | latest lake values (first_release) |  |  |
| TB3MS | 1b | R-17 | available | M | 1934-02-04 | lag_rule / A | latest lake values (first_release) |  |  |
| BAA | 1b | R-17 | available | M | 1919-02-04 | lag_rule / A | latest lake values (first_release) |  |  |
| AAA | 1b | R-17 | available | M | 1919-02-04 | lag_rule / A | latest lake values (first_release) |  |  |
| DCOILWTICO | 1 | R-10, R-19 | available | D | 1946-02-07 | lag_rule / B | latest lake values (first_release) | 1999-09-01 -> 1999-09-15 (14 d) |  |
| WTISPLC | 1 | R-10 | available | M | 1946-02-07 | lag_rule / A | latest lake values (lag_rule) |  |  |
| USD_BROAD | 1 | R-10, R-19 | available | D | 1973-01-09 | lag_rule / A | latest lake values (first_release) |  | none before 1973-01-02; CBP synthetic DXY (1971->) not in the lake |
| DTWEXBGS | 1 | R-10 | available | D | 2006-01-08 | lag_rule / A | latest lake values (first_release) |  |  |
| DTWEXM | 1 | R-10 | available | D | 1973-01-09 | lag_rule / A | latest lake values (lag_rule) |  |  |
| RITTER_UNPROF_IPO | 1 | R-11 | available | A | 1981-02-01 | lag_rule / A | latest lake values (lag_rule) |  |  |
| SIFMA_HY_SHARE_A | 1 | R-11 | available | A | 1997-02-14 | lag_rule / A | latest lake values (lag_rule) |  |  |
| SIFMA_HY_SHARE_Q | 1 | R-11 | available | Q | 2022-05-15 | lag_rule / A | latest lake values (lag_rule) |  | quarterly only 2022-> |
| BCNSDODNS | 1 | R-11 | available | Q | 1946-03-12 | lag_rule / A | latest lake values (lag_rule) | 1947-12-31 -> 1948-12-31 (366 d) | annual before 1951-Q4 |
| NCBCEBQ027S | 1 | R-11 | available | Q | 1947-03-13 | lag_rule / A | latest lake values (lag_rule) | 1947-12-31 -> 1948-12-31 (366 d) |  |
| BAMLH0A0HYM2 | 1 | R-11, R-17 | available | D | 1997-01-02 | lag_rule / A | latest lake values (lag_rule) |  | none before 1996-12-31 (FRED keeps 3 years; earlier rows from Wayback FRED captures) |
| FINRA_MARGIN_DEBT | 1 | R-11 | available | M | 1997-02-21 | lag_rule / A | latest lake values (lag_rule) |  | none before 1997-01 (NYSE margin history not in the lake) |
| ECBASSETSW | 1 | R-12 | available | W | 1999-01-05 | release_calendar / A | latest lake values (first_release) |  |  |
| EUROSYSTEM_TOTAL_ASSETS | 1 | R-12 | available | W | 1999-01-05 | release_calendar / A | latest lake values (release_calendar) |  |  |
| DE_CB_ASSETS | 1 | R-12 | available | M | 1948-12-15 | lag_rule / A | latest lake values (lag_rule) |  |  |
| JPNASSETS | 1 | R-12 | available | M | 1953-04-17 | lag_rule / B | latest lake values (first_release) |  |  |
| JP_BOJ_TOTAL_ASSETS | 1 | R-12 | available | M | 1998-05-08 | lag_rule / A | latest lake values (lag_rule) |  |  |
| JP_CB_ASSETS_BIS | 1 | R-12 | available | M | 1953-04-17 | lag_rule / A | latest lake values (lag_rule) |  |  |
| BOE_ASSETS | 1 | R-12 | partial | M | <= 1913-01-01 | lag_rule / A | latest lake values (lag_rule) |  | BoE weekly bank return (process.md R-12) not in the lake; monthly BIS series served instead |
| CB_ASSETS_GDP_US | 1 | R-12 | available | Q | 1948-04-30 | lag_rule / A | latest lake values (lag_rule) |  |  |
| CB_ASSETS_GDP_XM | 1 | R-12 | available | Q | 1999-05-01 | lag_rule / A | latest lake values (lag_rule) |  |  |
| CB_ASSETS_GDP_DE | 1 | R-12 | available | Q | 1961-05-01 | lag_rule / A | latest lake values (lag_rule) |  |  |
| CB_ASSETS_GDP_GB | 1 | R-12 | available | Q | 1956-04-30 | lag_rule / A | latest lake values (lag_rule) |  |  |
| CB_ASSETS_GDP_JP | 1 | R-12 | available | Q | 1956-07-30 | lag_rule / A | latest lake values (lag_rule) |  |  |
| ECB_DFR | 1 | R-12 | available | D | 1999-01-02 | release_calendar / A | latest lake values (release_calendar) |  |  |
| DE_POLICY_RATE | 1 | R-12 | available | D | 1948-07-02 | release_calendar / A | latest lake values (release_calendar) |  |  |
| UK_BANK_RATE | 1 | R-12 | available | D | 1946-01-02 | release_calendar / A | latest lake values (release_calendar) |  |  |
| GB_POLICY_RATE_BIS | 1 | R-12 | available | D | 1946-01-02 | release_calendar / A | latest lake values (release_calendar) |  |  |
| JP_POLICY_RATE | 1 | R-12 | available | D | 1946-01-02 | release_calendar / A | latest lake values (release_calendar) | 2001-03-18 -> 2006-03-09 (1817 d) | no rows 1999-02-12 -> 2006-03 (zero-rate / QE period); JP_CALL_RATE_M covers it |
| JP_CALL_RATE_M | 1 | R-12 | available | M | 1960-02-04 | lag_rule / C | latest lake values (lag_rule) |  |  |
| IRLTLT01USM156N | 1 | R-12 | available | M | 1953-05-14 | lag_rule / A | latest lake values (lag_rule) |  |  |
| IRLTLT01DEM156N | 1 | R-12 | available | M | 1956-06-14 | lag_rule / A | latest lake values (lag_rule) |  |  |
| IRLTLT01GBM156N | 1 | R-12 | available | M | 1960-02-16 | lag_rule / A | latest lake values (lag_rule) |  |  |
| IRLTLT01JPM156N | 1 | R-12 | available | M | 1989-02-17 | lag_rule / A | latest lake values (lag_rule) |  |  |
| IRLTLT01FRM156N | 1 | R-12 | available | M | 1960-02-16 | lag_rule / A | latest lake values (lag_rule) |  |  |
| IRLTLT01ITM156N | 1 | R-12 | available | M | 1991-05-03 | lag_rule / A | latest lake values (lag_rule) |  |  |
| FOMC_CALENDAR | 1 | R-14, R-38 | **missing** | event | - | - | - | - | No historical FOMC event table in the lake (amber calendars are forward-looking). Gap; manual event flags per process.md R-22. |
| NFCI | 1 | R-58 | available | W | 2011-05-25 | vintage / A | asof >= 2011-05-25 ALFRED (first publication of the index); earlier: index not published |  |  |
| FYFSGDA188S | 1 | R-63 | **missing** | A | - | - | - | - | Not in the lake. Gap (R-63 fiscal term unknown). |
| FRENCH49 | 1b | R-15, R-16, R-59, R-60 | **missing** | M | - | - | - | - | Not in the lake (only 10- and 12-industry copies from CBP). Leading set Rtail, Trans, Banks, Steel/Mines, Chips, BldMt/Cnstr cannot be formed. French-12 served as FRENCH12_* with proxy_grade D (no overlap with the 49 set to validate) and usable=False. |
| FRENCH12_NoDur | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Durbl | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Manuf | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Enrgy | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Chems | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_BusEq | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Telcm | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Utils | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Shops | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Hlth | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Money | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FRENCH12_Other | 1b | R-15, R-16, R-59 | substitute | M | never | - | latest lake values (lag_rule) |  |  |
| FF_MKT_RF_D | 1b | R-15, R-19 | available | D | 1926-08-31 | lag_rule / A | latest lake values (lag_rule) | 1933-03-03 -> 1933-03-15 (12 d) |  |
| FF_RF_D | 1b | R-15 | available | D | 1926-08-31 | lag_rule / A | latest lake values (lag_rule) | 1933-03-03 -> 1933-03-15 (12 d) |  |
| US_EQ_FUT_PROXY | 1b | R-19 | proxy_only | D | 1926-08-31 | lag_rule / B | latest lake values (lag_rule) | 1933-03-03 -> 1933-03-15 (12 d) |  |
| ETF_SPY | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_IWM | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_RSP | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_XHB | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_IYT | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_XTN | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_XRT | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_KBE | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_XME | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| ETF_SMH | 1b | R-15, R-16, R-59 | partial | D | 2021-09-22 | lag_rule / A | latest lake values (lag_rule) |  | 2021-09-21 -> only; ETF history from launch (1993-2006) to 2021 not in the lake |
| SHILLER_SP | 1b | R-18, R-61 | available | M | <= 1913-01-01 | lag_rule / A | latest lake values (lag_rule) |  |  |
| SP500 | 1b | R-18 | **missing** | D | - | - | - | - | Not in the lake; FRED carries 10 years only (process.md R-18). SHILLER_SP (monthly 1871->) and US_EQ_FUT_PROXY (daily) cover the role. |
| NASDAQCOM | 1b | R-19 | available | D | 1971-02-06 | lag_rule / A | latest lake values (first_release) |  |  |
| GOLD_LBMA | 1b | R-19 | available | D | 1968-04-02 | lag_rule / A | latest lake values (lag_rule) |  |  |
| PCOPPUSDM | 1b | R-19 | available | M | 1960-02-08 | lag_rule / B | latest lake values (first_release) |  |  |
| ZWEIG_EMA10 | 1b | R-60 | partial | D | 1965-03-02 | lag_rule / A | latest lake values (lag_rule) | 2020-02-10 -> 2021-09-22 (590 d) | 2020-02-11 -> 2021-09-21 no free breadth (gap rows usable=False) |
| NYSE_ADV | 1b | R-60 | partial | D | 1965-03-02 | release_calendar / A | latest lake values (release_calendar) |  | frozen archive 1965-03-01 -> 2020-02-10 |
| NYSE_DEC | 1b | R-60 | partial | D | 1965-03-02 | release_calendar / A | latest lake values (release_calendar) |  | frozen archive 1965-03-01 -> 2020-02-10 |
| NYSE_UPVOL | 1b | R-60 | partial | D | 1965-03-02 | release_calendar / A | latest lake values (release_calendar) |  | frozen archive 1965-03-01 -> 2020-02-10 |
| NYSE_DNVOL | 1b | R-60 | partial | D | 1965-03-02 | release_calendar / A | latest lake values (release_calendar) |  | frozen archive 1965-03-01 -> 2020-02-10 |
| SPX_PCT_ADV | 1b | R-60 | partial | D | 2021-09-23 | release_calendar / A | latest lake values (release_calendar) |  | 2021-09-22 -> only |
| SPX_PCT_ABOVE_50DMA | 1b | R-60 | partial | D | 2021-12-01 | release_calendar / A | latest lake values (release_calendar) |  | 2021-09-22 -> only |
| SPX_PCT_ABOVE_200DMA | 1b | R-60 | partial | D | 2022-07-08 | release_calendar / A | latest lake values (release_calendar) |  | 2021-09-22 -> only |

## 2. Research era-B case dates

Research split only (holdout episodes excluded): 11 cases with asof before 2002 in `cases\` at generation time. Case files were read for `asof` and `episode_id` only.

### 2.1 Rule families computable point-in-time

Y = every requirement has a fresh usable input (alternatives separated by `|`); otherwise the missing requirements are listed.

| Rule family | 1981-06-30 | 1981-12-31 | 1987-06-30 | 1991-12-31 | 1992-08-31 | 1992-09-16 | 1992-09-30 | 1999-02-26 | 2000-01-31 | 2000-03-31 | 2000-09-29 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R-02 M2-IP | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-03 net liquidity | WTREGEN | WTREGEN | WTREGEN | WTREGEN | WTREGEN | WTREGEN | WTREGEN | WTREGEN | WTREGEN | WTREGEN | WTREGEN |
| R-03 proxy (NETLIQ) | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-04 purchases-issuance | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-06 Taylor gap | Y | Y | Y | NROU | NROU | NROU | NROU | NROU | NROU | NROU | NROU |
| R-07/R-09 inflation | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-08 FF vs CPI | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-10 rates+oil+USD | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-11 fragility (>=2) | Y (3/6) | Y (3/6) | Y (3/6) | Y (3/6) | Y (3/6) | Y (3/6) | Y (3/6) | Y (6/6) | Y (6/6) | Y (6/6) | Y (6/6) |
| R-12 US | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-12 EA (Bundesbank pre-1999) | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-12 JP | IRLTLT01JPM156N | IRLTLT01JPM156N | IRLTLT01JPM156N | Y | Y | Y | Y | Y | Y | Y | Y |
| R-12 UK | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-14 policy direction | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-56 10y vs NGDP | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-58 FCI | NFCI | NFCI | NFCI | NFCI | NFCI | NFCI | NFCI | NFCI | NFCI | NFCI | NFCI |
| R-63 fiscal | FYFSGDA188S | FYFSGDA188S | FYFSGDA188S | FYFSGDA188S, NROU | FYFSGDA188S, NROU | FYFSGDA188S, NROU | FYFSGDA188S, NROU | FYFSGDA188S, NROU | FYFSGDA188S, NROU | FYFSGDA188S, NROU | FYFSGDA188S, NROU |
| R-15/16/59 industries | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 | FRENCH49 |
| R-17 curve+credit | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-18 momentum | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-19 cross-asset | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| R-60 breadth | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |

### 2.2 Step-1 inputs missing at each case date

Step-1 inputs named in process.md (rule families R-02..R-14, R-56, R-58, R-63; alternatives separated by `|`, one fresh usable alternative suffices) without a fresh usable row at the case asof. Auxiliary catalogue ids (e.g. GDPPOT, DFEDTARL, TFD_NET_*) are not required.

Requirement groups checked (37): M2SL, INDPRO|INDPRO_FR, WALCL, WTREGEN, RRPONTSYD, TREAST, WSHOMCB, TFD_DEBT_HELD_PUBLIC, UNRATE|UNRATE_FR, NROU, CPIAUCSL, FEDFUNDS|DFF, DFEDTARU|FEDFUNDS, DGS10, DCOILWTICO, USD_BROAD, FEDFUNDS, IRLTLT01USM156N, ECBASSETSW|DE_CB_ASSETS, ECB_DFR|DE_POLICY_RATE, IRLTLT01DEM156N, JPNASSETS, JP_POLICY_RATE|JP_CALL_RATE_M, IRLTLT01JPM156N, BOE_ASSETS, UK_BANK_RATE, IRLTLT01GBM156N, GDP, NFCI, FYFSGDA188S, UNRATE, RITTER_UNPROF_IPO, SIFMA_HY_SHARE_A, BCNSDODNS, NCBCEBQ027S, BAMLH0A0HYM2, FINRA_MARGIN_DEBT.

| Case | Asof | Every step-1 input available | Missing or stale step-1 inputs |
|---|---|---|---|
| 1981-06-30_half-cash-19pct-rates-1981 | 1981-06-30 | no | WTREGEN, IRLTLT01JPM156N, NFCI, FYFSGDA188S, SIFMA_HY_SHARE_A, BAMLH0A0HYM2, FINRA_MARGIN_DEBT |
| 1981-12-31_long-bonds-volcker | 1981-12-31 | no | WTREGEN, IRLTLT01JPM156N, NFCI, FYFSGDA188S, SIFMA_HY_SHARE_A, BAMLH0A0HYM2, FINRA_MARGIN_DEBT |
| 1987-06-30_net-short-fed-tightening-1987 | 1987-06-30 | no | WTREGEN, IRLTLT01JPM156N, NFCI, FYFSGDA188S, SIFMA_HY_SHARE_A, BAMLH0A0HYM2, FINRA_MARGIN_DEBT |
| 1991-12-31_fed-panic-bond-exit-1991 | 1991-12-31 | no | WTREGEN, NROU, NFCI, FYFSGDA188S, SIFMA_HY_SHARE_A, BAMLH0A0HYM2, FINRA_MARGIN_DEBT |
| 1992-08-31_sterling-starter | 1992-08-31 | no | WTREGEN, NROU, NFCI, FYFSGDA188S, SIFMA_HY_SHARE_A, BAMLH0A0HYM2, FINRA_MARGIN_DEBT |
| 1992-09-16_sterling-size-up | 1992-09-16 | no | WTREGEN, NROU, NFCI, FYFSGDA188S, SIFMA_HY_SHARE_A, BAMLH0A0HYM2, FINRA_MARGIN_DEBT |
| 1992-09-30_uk-concentric-circles | 1992-09-30 | no | WTREGEN, NROU, NFCI, FYFSGDA188S, SIFMA_HY_SHARE_A, BAMLH0A0HYM2, FINRA_MARGIN_DEBT |
| 1999-02-26_internet-short-process | 1999-02-26 | no | WTREGEN, NROU, NFCI, FYFSGDA188S |
| 2000-01-31_tech-exit | 2000-01-31 | no | WTREGEN, NROU, NFCI, FYFSGDA188S |
| 2000-03-31_tech-reentry-process | 2000-03-31 | no | WTREGEN, NROU, NFCI, FYFSGDA188S |
| 2000-09-29_two-year-notes-2000 | 2000-09-29 | no | WTREGEN, NROU, NFCI, FYFSGDA188S |

Cases with every step-1 input available point-in-time: 0 of 11.

## 3. Findings

| Item | Effect on era B |
|---|---|
| WTREGEN before 2002-12: only LDGUST (legacy TGA), graded D on the overlap | R-03 primary unknown; NETLIQ proxy (Z.1 CB assets - TGA, quarterly, grade C) is the usable variant |
| NROU: lake stamps periods 1990-Q1..2010 with the 2011-02-02 ALFRED initial vintage | asofs 1990-2011: newest visible NROU period 1989-Q4 (stale gap in R-06, R-63; needs CBO vintages) |
| NFCI first published 2011-05-25; earlier values are a backcast | R-58 unknown before 2011-05 |
| FYFSGDA188S, CPILFESL, French-49, historical FOMC calendar, SP500 not in the lake | R-63 fiscal term, R-06 core sensitivity, R-15/R-16/R-59 industry rules unknown in every era-B case |
| HY OAS, SIFMA HY share, FINRA margin debt start 1996-1997 | R-11 runs on 3 of 6 components before 1997 (Ritter, Z.1 debt, Z.1 net equity issuance) |
| CPIAUCSL before 1972-07-21: CPIAUCNS fallback, grade C | no era-B research case is affected (first case 1981) |
| IRLTLT01JPM156N starts 1989-01 | R-12 JP long rate unknown for cases before 1989 |

