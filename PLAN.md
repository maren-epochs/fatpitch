# Fat Pitch — Build Plan

Version 0.4 — 2026-10-06. Status: draft, review merged.
Inputs: spec `druckenmiller_fatpitch_reference_1.md`; library `library\reference_sources\` (20 events) and `library\discovered_sources\` (60 events); amber, CBP and wifey inventories; Fable 5.1 review `PLAN_REVIEW.md` (30 findings — disposition in Appendix A).

---

## 0. Structure

| Lift | Purpose | Lives in | Priority |
|---|---|---|---|
| **E — Evaluation** | Engine that reproduces Druckenmiller's decision process point-in-time, and measures fidelity against his documented decisions versus trivial baselines | `druckenmiller` project, Python package `fatpitch` | Primary — decides whether the product ships |
| **D — Data** | Point-in-time data, free sources only | amber (`data\lake`, `core\*`, daily job) | Supporting |
| **V — Delivery** | `FP` function in the amber terminal, nightly run, signal log | amber (`api\main.py`, `apps\terminal`, `cli.ingest_daily`) | Supporting |

Separate package rationale: fidelity needs its own corpus, pre-registration and versioning, independent of amber's release cadence. Amber's only touchpoint is a thin `core\fatpitch_store.py`. Development uses an editable install; **the nightly job imports a pinned tagged build** (local wheel), and every run row stores `fatpitch.__version__` and the parameter-registry sha.

### 0.1 Global constraints

| Constraint | Source |
|---|---|
| Free data only | User 2026-10-06 |
| IBKR via IB Gateway 127.0.0.1:4002 (paper, data sharing on); free delayed feed covers futures/OPRA, not US stocks; Gateway auto-restart + start at logon, weekly 2FA by user; no stored IBKR password | User; amber research |
| IBKR daily bars for v1 roots stored locally (~5 MB) under amber's curve exception, non-redistributable, not sent to AI | User 2026-10-06 (U3 = D) |
| Thesis-break exits, no stop-losses; long and short; cash when no pitch | Reference §2.6; library |
| Every parameter tagged `stated` (primary citation), `interpreted`, or `interpreted-from-article` | Review finding 2 |
| Unknown never counts as fail | Reference §4.2 |
| Point-in-time: no input used before its `published_at` | Review findings 14, 15, 22 |
| Output is a process model, not his view; never first person; not affiliated or endorsed | Review §G |

### 0.2 Interfaces

```
D (amber parquet lake) ──► E: fatpitch.evaluate(asof) -> Decision ──► V: amber persists, serves, renders
        ▲                              │
        └──── data requirements ───────┘
```

| Contract | Owner | Definition |
|---|---|---|
| `Source.snapshot(asof: datetime[America/New_York]) -> dict[series_id, Frame]` | E defines; D implements; E ships `FixtureSource` | Frame columns: `value, period_end, published_at, vintage_id`. Filter is `published_at <= asof`, never `period_end`. Atomic across series. Property test at E0: no row with `published_at > asof` is ever returned |
| `fatpitch.evaluate(asof) -> Decision` | E | `schema_version`, regime vector, internals vector, theses (with premise ledger), expressions, vetoes, tiers, `size_band`, exits, every consumed input with value/provenance, engine version, registry sha |
| Persistence | V | Parquet full trace + SQLite rows; stable `signal_id` for the exit ledger |

---

## E. Evaluation lift (primary)

### E.1 Process model (revised per review; sources in library)

Thesis-first, with price action as a leading input, an entry veto and an exit trigger — not a late confirmation stage.

| Step | Principle (source) | Engine stage | Output |
|---|---|---|---|
| 1 | Liquidity and policy drive markets: money growth vs industrial production (Feig 2009, `stated`); Fed net of Treasury (ECNY 2020); policy error is the main opportunity (Lost Tree); inflation rules (Sohn 2022); rates+oil+USD (Delivering Alpha 2022); fragility gauges (Delivering Alpha 2014, CNBC 2015-03) | **Regime & policy** — liquidity rule family (era-labelled, E.4a), policy-error sign (unemployment-gap Taylor variant, vintaged), inflation veto, cross-asset warning, fragility level (non-gating); **cross-region block**: Fed/ECB/BoJ/BoE balance-sheet change and policy direction, OECD long rates | Regime vector per region: policy direction, liquidity impulse and change, policy-error sign, veto flags, fragility level. 5-level label for display only |
| 1b | Internals lead the economy; leading industries; bond market prescient; momentum bottoms 12–18 months before fundamentals (Feig 2009; reference §2.3) | **Market internals** — leading-industry relative-strength turns (French industries 1926→, sector ETFs), curve and credit signals, cross-asset trend | Internals vector with direction and age of turn; input to step 2 |
| 2 | Never invest in the present; change, not level; horizon 18 months to 3 years (Lost Tree; NBIM 2024; Morgan Stanley 2026); theses carry premises (2016 gold) | **Thesis generation** — pre-registered transition→thesis table over regime *and* internals; replay-safe forward view (DGS2−FF 1976→, DGS1−FF 1962→, trend in inputs; futures path only as live refinement that reduces to the curve measure); region-relative theses allowed | 0–N theses: class, direction, region, premises, invalidation events |
| 3 | Focus on what moves the security; multi-asset menu; assets that rise when equities fall; concentric circles (sterling 1992) | **Expression selection** — rank by sensitivity to the thesis driver and payoff asymmetry; second-order expressions across classes | Ranked expressions, long and short |
| 4 | "Thesis good, chart stinks — I won't do it"; price vs news; no contrarian fade (Feig 2009); technicals ~20% as effective as before (Morgan Stanley 2026) → lower weight on timing, veto retained | **Veto** — chart quality (trend/RS daily-weekly-monthly), price-vs-news, instrument liquidity. Article-origin gates (forensics, ROIC, Form 4/13F smart money, contrarian COT) `interpreted-from-article`, weight 0 by default | Admitted to *starter*, or vetoed with reason |
| 5 | Small bet, size up on confirmation and catalyst (sterling: $1.5B → full size after Schlesinger); 1–2 per year; sizing 70–80% of the game (Sohn 2022); size to liquidity, gross ≤ 4:1, class caps, hot/cold (Feig 2009) | **Tier and size** — starter → fat pitch when independent evidence converges and a catalyst is near; failed non-veto evidence lowers tier, does not remove; `size_band` = tier × class cap × liquidity cap × hot/cold multiplier | Tier, `size_band` (% NAV / risk units), catalyst date, evidence list |
| 6 | Exit when the reason changes; reverse within hours on a premise break (2016 election; 2019 tariffs); price vs news; "I'm a technician, I wait for tops" (NBIM 2024); know hot or cold | **Monitoring** — premise ledger checked daily against calendar events and price-vs-news; regime/thesis re-run nightly; self-scorecard feeds size | Exit flags naming the broken premise; scorecard |
| 7 | No pitch, no play; no long bias | **Cash default** | "No pitch" with nearest misses and blocking vetoes |

### E.2 Process specification (before any engine code)

`spec\process.md`: per rule — primary citation (library file), tag, formula, parameters, inputs, conflicts. Library corrections to apply to reference §2/§7 at the same time: 93%→flat 2019 unverified; Soros <30% unverified; "sizing 70–80%" is his own statement (Sohn 2022), not Mauboussin; inflation-rule "summarizer error" note is wrong — he expected the fed-funds-above-CPI rule to break this cycle and it did; sterling sizes vary across tellings ($7B/$7.5B/$10B fund); horizon range widens to 18m–3y and 2–4y trends.

`spec\process.md`, the transition→thesis table and the case corpus hash are **registered via `prereg` before any case is scored**. Engine and calibrator never read outcome columns. Post-scoring changes to the table are design changes requiring re-registration and a new report.

E1 acceptance requires full extraction of: Lost Tree 2015, Feig 2009, ECNY 2020, Sohn 2022, NBIM 2023, NBIM 2024, Delivering Alpha 2014/2022, Morgan Stanley 2026, New Market Wizards. Sokoloff 2018 and Sohn 2022 lack public transcripts — secondary notes only, tagged.

### E.3 Ground truth

| Corpus | Use |
|---|---|
| Documented trades (1981 bonds; 1992 sterling; 2000 tech mistake; 2000 2-year notes; 2003 Fed too loose; 2013 short AUD/yen; 2015 long Japan/Europe; 2016 global bonds/gold exit; 2019 and 2023 2-year Treasuries; 2022 short bonds; Nvidia trims) | Primary: thesis + expression + action + size where documented |
| Dated public calls (ledger from library; incl. failures: ECNY 2020 bearish call reversed by Nov 2020) | Regime and thesis agreement |
| Duquesne Family Office 13F (2013 Q2→ from SEC data sets; earlier via raw filings) | Equity-expression test only, on quarter-over-quarter changes, `filed` date as information date |

Case schema (`cases\<date>_<slug>.yaml`): `id, asof (ET close), era (A|B), episode_id, truth_type (process|action), mechanizable (yes|no), source_reliability, targets {regime_direction, theses[], expression, action, size_band}, window (default ±20 business days; ±1 quarter only for 13F)`. For `process` cases (2000 tech, Brazil 2008) the target is the stated rule's output; matching his action counts as a miss.

### E.4 Scoring, nulls, targets

Scoring per case (pre-registered): regime 1 / 0.5 (in window) / 0; thesis 1 if class+direction(+region) match in window; expression 1 if target family in top-3; action 1 if tier/exit implies same action; log-score variant where probabilities exist. Aggregate per episode first, then across episodes. Report by era, reliability, truth_type, mechanizable.

Null models, scored identically: (1) always risk-on; (2) Fed-direction-only; (3) 12-month trend of SPY/IEF/DXY; (4) persistence. Permutation test on case dates.

| Metric | Target |
|---|---|
| Regime stage (research cases with a regime target, era A and era B; owner decisions 2026-10-07, options B + C) | Engine emits daily as-of P(easing/neutral/tightening) (floor 0.01); ranked probability score at each case asof, episode-first; against EACH of leave-one-episode-out climatology, `null_trend_12m` and the constant `null_always_risk_on`: RPS skill > 0 and one-sided exact episode-level sign-flip p < 0.10 (binding p = the largest); and on the tightening cases the engine's mean RPS is below always-easing's (an engine that cannot call tightening fails); staging gate on research; holdout scored once at E7 with a Bayes factor, not re-gated; era A / era B breakdowns, class-balanced RPS and diagnostics (bracketed daily agreement, turning-point matching, κ / balanced accuracy, AUC, each with its chance level) reported (`spec\scoring.md` §6c, §7); plus the required Fed cycle check (owner decision 2026-10-07, option A): monthly 1970→ RPS vs Fed-stance labels from the Fed's own history (`spec\fed_cycles.yaml`), skill > 0 vs LOEO-by-cycle climatology, `null_trend_12m`, always-easing and `null_fed_direction`, tightening detected within ±3 months of the first hike in ≥ 75% of cycles and at least as many cycles, as early (median lead), as `null_fed_direction`, false alarms in easing months ≤ 20% (`spec\scoring.md` §6d); overall regime pass = Gate 1 AND Fed cycle check |
| Thesis recall (era A) | Gate 2: beats the pre-chosen best null case by case (paired sign-flip test, p < 0.10) and recall ≥ 0.50 (spec\scoring.md §6a) |
| Expression hit | Reported vs nulls; no gate in v1 |
| 13F QoQ tilt-change sign agreement | Beats no-change persistence |
| Era B, cash fidelity, size-band agreement | Reported per case/period; no gate |
| Fat-pitch frequency | Calibration target only; scored on held-out years only |

Fidelity ceiling: discretionary/political-catalyst cases tagged `mechanizable: no` are reported separately as the expected ceiling.

### E.4a Data-era stratification

Era A (2002→, daily, direct liquidity measures) vs era B (pre-2002, monthly). Liquidity is a family of rules, scored where each exists: (i) M2 growth − IP growth, 1959→, ALFRED-vintaged, `stated` (Feig 2009) — **the era-B measure**; (ii) Fed assets − TGA − RRP, 2002→, `interpreted` from ECNY 2020; (iii) Fed purchases − net Treasury issuance, `interpreted` (ECNY 2020), Treasury fiscal data. Overlap fit between rules is a diagnostic, not a selection criterion. Cases decided on non-liquidity drivers (1981 real rates; 1992 ERM/Bundesbank) score on the stage that applies. Sensitivity of era-B results to each rule variant reported.

### E.5 Performance (descriptive in v1)

Forward 20/60/250-day returns, payoff ratio and expectancy per pitch; timing-luck and execution-lag (CBP); gate ablation; DSR with `n_trials` from `prereg` run log. Not a go/no-go in v1 — sample too small.

### E.6 Calibration

`stated` fixed. `interpreted` parameters capped at **8** in v1, chosen by **leave-one-episode-out** fidelity across the full corpus; fidelity shown across parameter ranges (±20%). Held-out scoring runs once under `prereg`. Every scoring run logged (`record_run`). Fidelity beats performance on conflict.

### E.7 Phases

| Phase | Deliverable | Acceptance |
|---|---|---|
| E0 | Package skeleton; `Source`/`FixtureSource`; `Decision` schema v1; port CBP `engine\inference.py`, `research\prereg.py`, `research\timing_luck.py`, `research\controls.py` (HAC), `engine\ladder.py` bootstrap, `data\dates.py`, `multi-strategy\tests\golden.py` | Tests pass in both projects; as-of property test; network blocked in tests |
| E1 | `spec\process.md`; parameter registry; reference §2/§7 corrections; prereg registration | Required primary notes extracted; every rule cited and tagged |
| E2 | Case corpus with scoring rule and nulls; corpus hash registered | ≥ 30 cases across ≥ 10 episodes |
| E3 | Steps 1 + 1b: regime, internals, cross-region block; replay 1960→ | **Gate 1 (regime staging gate, options B + C, owner decisions 2026-10-07):** on research cases with a regime target (era A and era B), the engine's daily regime probabilities beat each of leave-one-episode-out climatology, `null_trend_12m` and the constant `null_always_risk_on` (episode-first RPS skill > 0 and one-sided exact episode-level sign-flip p < 0.10 against every one), and beat always-easing on the tightening cases (`spec\scoring.md` §6c); and the required Fed cycle check passes, including beating `null_fed_direction` on skill and cycle detection (`spec\scoring.md` §6d; overall regime pass = Gate 1 AND Fed cycle check) — else back to E1. Holdout regime result reported once at E7; Gate 2 is the hard go/no-go |
| E4 | Steps 2–3: theses, premise ledger, expressions | **Gate 2:** on era-A cases (full corpus), engine thesis recall beats the pre-chosen best null case by case (paired sign-flip, one-sided, N 10000, p < 0.10) and recall ≥ 0.50 — else back to E1/E3 |
| E5 | Step 4 veto per class, order **rates/FX → commodities → equities → crypto** | Veto unit tests; unknown≠fail; article-origin gates off |
| E6 | Steps 5–7: tier, size band, monitoring, cash | Size-band and reversal cases scored; exit tests |
| E7 | Calibration (LOEO) and held-out fidelity report; descriptive performance | Report vs E.4; go/no-go per class |

---

## D. Data lift (amber)

### D.1 Amber today

Equities: Alpaca SIP daily 2021-09→ (13.5k symbols incl. 775 delisted); point-in-time S&P 500 via IVV N-PORT 2021-06→; SEC facts point-in-time (`as_of` 2009→); Form 4 quarterly sets; 13F two complete quarters. Macro: FRED 45 series 2014→, central-bank set 2021→ (net liquidity computed in `cenb.balance_sheets()`), ALFRED vintages for CPI/GDP/payrolls, BLS 2017→. FX: ECB 1999→. Commodities: EIA weekly 1982→, monthly 1920→, WASDE. Futures: Massive individual contracts ~13 months. COT legacy 3 years. Crypto: Coinbase (BTC 2015→). Calendars: earnings, FOMC, BLS, FRED releases, EIA/USDA, ECB/BoE/BoC. Plumbing: rate limits, provider health, keyring, gap/freshness tools.

### D.2 Work items

| # | Item | Needed by | Free source | Amber change |
|---|---|---|---|---|
| D0 | IBKR per-exchange entitlement audit (historical bars, delayed vs live, error codes incl. 354/10168/10089/10197) | D-5 | IBKR | Script; client id 20 |
| D-1 | FRED long history: FEDFUNDS, CPIAUCSL/NS, UNRATE, NROU, GDPPOT, DGS1/2/10/3MO, BAA, AAA, M2SL, INDPRO, BOGMBASE, TOTRESNS; central-bank set 2002→ | E3 | FRED | Widen `econ.refresh_fred` and `cenb._fred(years=5)`; add series |
| D-2 | ALFRED vintages: CPI, UNRATE, INDPRO, M2SL, PAYEMS, NROU, GDPPOT | E3 | ALFRED | Extend `fred\vintages` |
| D-2a | `published_at` for every series from FRED release calendar; H.4.1 (WALCL, WTREGEN) shifted to Thursday 16:30 ET | E3 | FRED (`econ.fred_release_dates`) | Add column to lake |
| D-3 | Duquesne Family Office 13F: 2013 Q2→ via data sets; pre-2013 raw info-table parser optional; confirm CIK | E4 | SEC | Targeted pull in `core\holders.py` |
| D-4 | COT full history 1986→ + TFF + disaggregated (2006→); add 6A/6C/6S/6N/6M | E5 | CFTC Socrata | Extend `core\cot.py` |
| D-5 | IBKR daily bars for v1 futures/FX roots, stored, as-of back-adjustment; Massive + CBP VX/GC as cross-check | E5 | IBKR | New `ibkr\bars_daily`; extend `core\futures.py`; `sources.yaml` non-redistributable |
| D-6 | Crypto perp funding/OI/basis | E5 | Hyperliquid, Binance, OKX, Deribit public | New `core\perps.py` |
| D-7 | Long credit spread: BAA−DGS10 1953→; HY OAS 1996→ (FRED limits ICE history — verify) | E3 | FRED | Via D-1 |
| D-8 | USD index splice: DTWEXM (1973–2019) + DTWEXBGS (2006→), ratio splice on overlap; CBP synthetic DXY monthly 1971→ fallback | E3 | FRED, CBP | Add DTWEXM |
| D-8a | FRED daily FX `DEX*` 1971→ (USUK, JPUS, USEU, SZUS, CAUS, USAL) | E3/E5 | FRED | Add series |
| D-8b | OECD long rates `IRLTLT01*` 1960→ (US, DE, GB, JP, FR, IT); ECB/BoJ assets (in `cenb`) | E3 cross-region | FRED/OECD | Add series |
| D-8c | Treasury net marketable issuance | E3 liquidity rule (iii) | Treasury Fiscal Data API | New fetch |
| D-9 | Pre-2021 S&P 500 membership | E5 equities | Public change lists | Reference table, else label survivorship-biased |
| D-10 | Daily Form 4 parser (extend existing quarterly `core\insiders.py`) | E5 equities (article-origin, low priority) | EDGAR | Extend |
| D-11 | 13F backfill 8+ quarters | E5 equities (low priority) | SEC | `core\holders.py` |
| D-12 | IBKR OPRA OI/volume for equity candidates | E5 | IBKR delayed | Module; client id 20 |
| D-13 | OPEC and token-unlock calendars only (others exist in amber) | E6 | Static config | Config |
| D-14 | Earnings momentum (SUE, acceleration) from facts | E5 equities | SEC facts | `core\pitfund.py` |
| D-15 | Persistent vintage-tracked daily FRED store (amber lake), seeded from CBP fixtures | E3 | FRED + CBP | Fold into amber `fred` |
| D-16 | CBP long-history series as read-only sources: monthly macro 1913→, FX 1971→, World Bank commodities 1960→ (`worldbank_cmo_monthly_research.xlsx`), French industries/factors 1926→, Shiller (display only), VIX 1990→, VX 2004→ (cleaned) | E3 | CBP `cache\research\`, `cache\vx` | Loader + `sources.yaml` |
| D-18 | Unprofitable-IPO share, quarterly, EDGAR-derived (`interpreted`), validated vs Ritter on 2009→ overlap; exclude SPACs, F-1 | E3 overlay (later) | EDGAR + facts | `core\ipo_excess.py` |
| D-20 | Article alt data in amber, weight 0 in fat pitch (owner 2026-10-06): Polymarket FOMC/CPI/election odds; NOAA + NASA MODIS NDVI and drought/anomaly series for the corn belt; WARN, DOL H-1B LCA, OSHA filings mapped to tickers | Display/data only | Polymarket APIs, NOAA/NCEI/CPC, NASA MODIS, state WARN, DOL OFLC, DOL enforcement | `core\polymarket.py`, NOAA/MODIS and labor loaders; daily job; `sources.yaml` |
| D-19 | Fragility overlay inputs: Ritter annual unprofitable-IPO share 1980→ (`stated`); SIFMA HY vs IG issuance 1996→; Z.1 nonfinancial corporate debt (`BCNSDODNS`) and net equity issuance 1951→; HY OAS level; FINRA margin debt | E3 overlay | Ritter, SIFMA (spreadsheets), FRED, FINRA | Loaders; overlay non-gating |

Critical path for E3: D-1, D-2, D-2a, D-7, D-8, D-8a, D-8b, D-15, D-16, D-19. Deferred: D-3 (E4), D-4–D-6, D-9–D-14, D-18.

Acceptance per item: gap-check report (start, end, frequency, missing %, `published_at` coverage), `sources.yaml` entry, offline tests with fixtures.

### D.3 CBP contribution

Long-history monthly series (CPI 1913, AAA/BAA/INDPRO 1919, TB3MS 1934, UNRATE 1948, GS10 1953, FEDFUNDS 1954), FX 1971, World Bank commodities 1960, French 1926, VIX/VX, Shiller; daily FRED only in golden fixture pickles (seed for D-15). ALFRED first-release logic (`research\unemployment_pit.py`, INDPRO first release) — mandatory for the M2−IP rule. Validation tooling per E0. Cautions: pre-1986 inputs are monthly averages; `cache\` Shiller (2023-09) and World Bank (2024-12) copies stale — use `cache\research\`; VX archive needs cleaning (4 missing months, malformed rows, 10× scale pre-2007-03-26, placeholders).

### D.4 wifey contribution

Logic only: VIX term structure (port to ib_async, fix VX roll discovery), 2-of-3 recession block as regime sub-score, VAA/DAA momentum and breadth formulas (rescaled daily) for internals. VolQ thresholds `interpreted`.

### D.5 Decisions (resolved 2026-10-06)

| # | Choice |
|---|---|
| Paid data | None. Alpaca SIP equities; SIC→11 sectors (+ sector-ETF N-PORT holdings); SUE instead of consensus revisions |
| U3 IBKR bars | Store locally (D-5), ~5 MB, curve exception, non-redistributable |
| U4 excess overlay | His gauges via free series (D-19) now; EDGAR quarterly IPO share (D-18) later. CAPE display-only. Overlay sets fragility level affecting tier/size, never direction |
| Gateway login | Unattended paper login: `amber\jobs\ibgateway_login.py` (credentials in Credential Manager, accepts paper warning, minimizes) run by Startup shortcut; Gateway auto-restart on; paper needs no 2FA |
| Free API keys | BLS v2 (`bls_key`), CFTC Socrata app token (`cftc_app_token`), FMP free (`fmp_key`) — owner sets up later; code uses them when present, keyless until then; queued in amber `OWNER-QUEUE.md` |

---

## V. Delivery lift (amber)

### V.1 Integration

Function mnemonic `FP` (alias `FATP`; both verified free). Name "Fat pitch — process model". Template EQS; secondary COT; EQBT inline-SVG curve.

| Touchpoint | Change |
|---|---|
| `api\main.py` | `FUNCTIONS` entry with disclaimer in `desc`; exactly one `CATEGORIES` group; `/fatpitch/*` routes via `core\fatpitch_store.py` (read-only over run outputs) |
| `cli.py` `ingest_daily` | try/except step after `screener.build()` calling the pinned `fatpitch` build |
| Outputs | `data\lake\amber\fatpitch\<date>.parquet` (trace); `data\app\fatpitch.sqlite` (signals, exits, runs; inline DDL; auto-backed-up) |
| `apps\terminal` | `functions\FP.tsx`, `Panel.tsx` case, `api.ts` types |
| `doctor.py` | Freshness check; **run fails if any `stated` input is unknown** |
| `mcp_server.py` (optional) | Tool returns same provenance fields and disclaimer |
| CLI | `amber fatpitch run|backfill|replay --asof` |

### V.2 Views

Regime (per-region vector, net-liquidity chart, attribution) · Internals · Theses (premises and invalidation events — "what would change this") · Pitches (tier, `size_band`, evidence, catalyst, templated rule text "rule R-xx (`stated`, Feig 2009) fired because …", tag mix) · Veto funnel · Open signals (exit flags with broken premise) · Scorecard (hot/cold; fidelity by era with null-model lines; paper ledger) · Drilldown · Data health. Every row shows engine version and registry sha. No performance text before V4 ends.

### V.3 Phases

| Phase | Deliverable | Acceptance |
|---|---|---|
| V0 | Read amber README/RESUME/memory (CLAUDE.md stale) | — |
| V1 | Store + routes on fixture `Decision` | API tests; `test_registry_matches_frontend_panels`; `test_every_function_has_one_category` |
| V2 | `FP.tsx` views on fixtures | `npm run build`; `tools\e2e.py`; `tail_sweep.py`; screenshots |
| V3 | Nightly step + doctor | 20 consecutive unattended runs (after E6) |
| V4 | 60-trading-day paper period; hypothetical fills next-day open via Alpaca/IBKR stored bars, never execution | Operational: runs, exits, data health — not signal counts (≈0 fat pitches expected in 60 days) |

Amber conventions: pytest + ruff (py312, 110); `sources.yaml` for every source; keyring-only secrets entered by owner; tests never touch owner state; update `RESUME.md`/`BUILD-LOG.md`; owner items to `OWNER-QUEUE.md`; no new standing scheduled tasks; IBKR client id 20.

---

## S. Sequencing

```
E0 ─ E1 ─ E2 ─ E3 [Gate 1] ─ E4 [Gate 2] ─ E5 ─ E6 ─ E7 [go/no-go per class]
D0, then E3 critical path (D-1, D-2, D-2a, D-7, D-8, D-8a, D-8b, D-15, D-16, D-19) in parallel with E0–E2; D-3 before E4; D-4..D-6, D-12 before E5
V0 ─ V1 ─ V2 on fixtures from E0; V3 after E6; V4 after E7 go
```

No Gate 1 pass → no V3.

---

## R. Risks

| Risk | Mitigation |
|---|---|
| Effective n ≈ 10 episodes | Episode-level aggregation; LOEO; per-case reporting; results diagnostic |
| Designer leakage (table written knowing outcomes) | prereg of spec, table, corpus hash before scoring; outcome columns stripped |
| Discretionary/political cases unreachable | `mechanizable` tag; ceiling reported |
| Hindsight case selection | Mistakes and failed calls included (2000, Brazil 2008, ECNY 2020) |
| H.4.1 and revised Taylor inputs leak | `published_at`; unemployment-gap Taylor with vintages; current-vintage gap diagnostic only |
| Technicals degraded (his 2026 view) | Veto retained, timing weight low; fidelity measured with and without |
| Short futures/crypto history | Rates/FX and macro first; thin gates → unknown |
| IBKR pacing and Gateway downtime | One-time backfill; nightly top-up only; stale → unknown |
| Endorsement misreading | Name, disclaimer, templated rule text, provenance, no first person, no performance claims before V4 |

---

## Appendix A — Review disposition (`PLAN_REVIEW.md`)

| Findings | Disposition |
|---|---|
| 1, 7, 8 (price action, invest-then-investigate, reversal speed) | Adopted — E.1 steps 1b, 4, 5, 6 |
| 2 (article-origin gates) | Adopted — third tag, weight 0 |
| 3 (size output) | Adopted — `size_band` |
| 4 (replay-safe forward view) | Adopted — curve-based measure |
| 5, 10, 16 (scoring, nulls, LOEO, numeric gates) | Adopted — E.4, E.6, E.7 |
| 6 (liquidity rule family) | Adopted — E.4a; replaces proxy search |
| 9 (mistake cases) | Adopted — `truth_type` |
| 11 (13F changes) | Adopted — E.3 |
| 12 (cross-region) | Adopted — step 1, D-8b |
| 13 (no long free futures) | Adopted for history pre-IBKR coverage; IBKR storage (U3=D) covers live + IBKR-available history |
| 14, 15, 22 (leakage, published_at, Source contract) | Adopted — 0.2, D-2a, E.2 |
| 17–21, 25, 30 (factual fixes) | Adopted — D-3, D-8, D-10, D-16, D-18, E0 paths, V1 acceptance |
| 23 (pinned build) | Adopted — §0 |
| 24 (U4) | Adopted — option C (D-18 + D-19) |
| 26 (5-level regime) | Adopted — vector output |
| 27 (thesis text) | Adopted — templated rule text |
| 28 (E.5 descriptive) | Adopted |
| 29 (U3) | Superseded by user choice D (store IBKR bars) |
| Rates/FX first ordering (§A) | Adopted — E5 order |
