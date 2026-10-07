# Fat Pitch — Process Specification v1 (phase E1)

Date: 2026-10-06. Status: draft for `prereg` registration together with `spec\registry.yaml`, `spec\transition_table.yaml` and the E2 case-corpus hash. Not yet registered.

Scope: rules for an engine that reproduces a documented public investment process (S. Druckenmiller) point-in-time. Output is a process model, not his view; not affiliated or endorsed. Rule text is never rendered in first person.

## 0. Conventions

| Item | Definition |
|---|---|
| Rule id | `R-xx`, stable. R-01..R-55 were fixed before library reading, when `transition_table.yaml` was authored; R-56..R-65 added after reading. Ids are never reused. |
| Tag `stated` | Principle (and any number) appears in a primary or near-primary note as his own statement. Operational formula may still be interpreted; the formula line says so. |
| Tag `interpreted` | Principle or construction is an inference from statements; not his formula. |
| Tag `interpreted-from-article` | Origin is the Automated Alpha article (`RS/2026-03-24_automated-alpha-fat-pitch-filter.md`), no primary support. Default weight 0. |
| Citation | `DS/` = `library\discovered_sources\`, `RS/` = `library\reference_sources\`. Quote ≤ 2 sentences. Reliability per note front-matter: NP = near-primary transcript, P = primary, S = secondary summary. |
| Parameters | Ids in `spec\registry.yaml`. `stated` parameters are fixed; 8 `interpreted` parameters are tunable (E.6 cap). |
| Data ids | FRED/ALFRED series ids unless noted. "TFD" = Treasury Fiscal Data API. "FF" = effective fed funds (`FEDFUNDS` monthly 1954→, `DFF` daily 1954→). |
| PIT | Every input filtered on `published_at <= asof` (PLAN 0.2). H.4.1 series (`WALCL`, `WTREGEN`, `TREAST`, `WSHOMCB`) dated Wednesday, published Thursday 16:30 ET. Revised series (M2SL, INDPRO, UNRATE, NROU, CPI NSA vs SA, GDP) use ALFRED vintages; first-release logic per CBP `research\unemployment_pit.py`. |
| Unknown | Missing input → rule output `unknown`; never counts as fail or as pass. |
| Era | A = 2002→ (daily, direct balance-sheet data); B = pre-2002 (monthly). |

Verified-vs-inference marking: every quote below was read in the cited library note. Notes marked S quote secondary summarizers; their quotes are not verified against audio. Statements in "Formula" lines are design choices unless tagged `stated`.

## 1. Step 1 — Regime & policy

Output per region r ∈ {US, EA, JP, UK}: `policy_direction ∈ {easing, neutral, tightening}`, `liq_impulse` (sign, level, Δ) per rule variant, `policy_error_sign ∈ {too_loose, neutral, too_tight}`, veto flags (R-07, R-08, R-09, R-10), `fragility_level ∈ {low, normal, high}` (non-gating), `fci_state`. A 5-level label exists for display only.

### R-01 Liquidity and the Fed, not earnings, drive the overall market — `stated`
- Cite: `RS/2015-01-18_lost-tree-club-speech.md` (NP): "earnings don't move the overall market; it's the Federal Reserve Board." Also `DS/2019-06-07_cnbc-squawk-box-one-way-bet.md` (NP): "I'm a liquidity guy."
- Formula: framing rule. Index-level equity direction in step 2 is driven by R-02/R-03/R-04 and policy direction; earnings enter only at security level (R-25).
- Params: none. Inputs: outputs of R-02..R-04, R-14.
- Conflicts: none at index level. At security level earnings matter (2000: Hyman model −36% vs Street +18%, Feig 2009). DS/2017-12-12: "stock market is basically a function of central bank policy."
- PIT: n/a.

### R-02 Money growth minus industrial-production growth (liquidity rule i; era-B measure) — `stated`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP): "If you have the money supply growing a lot faster than industrial production, the stock market is generally going to go up."
- Formula (threshold interpreted): `L2_t = yoy(M2SL)_t − yoy(INDPRO)_t` over `liq.growth_window_m`. Impulse positive if `L2 > liq.m2_ip.spread_pp`, negative if `L2 < 0`, else neutral. Transition recorded after `liq.confirm_periods` monthly observations.
- Params: `liq.growth_window_m`, `liq.m2_ip.spread_pp` (tunable), `liq.confirm_periods`.
- Inputs: `M2SL` (1959→), `INDPRO` (1919→). Both ALFRED-vintaged.
- Conflicts: "a lot faster" is unquantified. He does not specify M1/M2/base; M2 chosen as the broad aggregate available 1959→. Feig 2009 also shows the rule overriding a bearish economic view (2008 commodities; 2009 equities).
- PIT: use first-release INDPRO and vintage M2SL as of `asof`; yoy computed within-vintage. No M2 definitional break in May 2020: the Feb-2021 H.6 change (effective May 2020) moved savings deposits into M1 and left M2 unchanged. Flag 2020-03..2021-12 as base-effect outliers (L2 38 pp in 2020-05, −1.6 pp in 2021-05 as IP base effects reversed). IP released ~mid-month for prior month; M2 weekly/monthly H.6 with ~3-week lag.

### R-03 Fed assets − TGA − RRP (liquidity rule ii; era A) — `interpreted`
- Cite: `RS/2020-05-12_economic-club-of-new-york.md` (S, Felder verbatim): "liquidity shrinks as far as the eye can see as the Treasury borrowing crowds out not only the private economy but even overwhelms Fed purchases." DS/2022-09-28 (NP) does liquidity accounting "QE … plus the TGA drawdown."
- Formula: `NL_t = WALCL − WTREGEN − RRPONTSYD`; impulse = `Δ NL` over `liq.netliq.window_w`, sign with `liq.confirm_periods` weekly confirmation. Facility usage (e.g., 2023 BTFP) is included via WALCL (NBIM 2023: SVB facilities "wiped out" months of QT).
- Params: `liq.netliq.window_w`, `liq.confirm_periods`.
- Inputs: `WALCL` (2002-12→), `WTREGEN` (2002→ weekly), `RRPONTSYD` (2003→ daily; 0 before).
- Conflicts: not his formula (PLAN_REVIEW finding 6). Reference doc §3 presents it as the proxy; this spec demotes it to one family member.
- PIT: Thursday 16:30 ET publication; RRP daily published same day ~13:15 ET.

### R-04 Fed purchases − net Treasury issuance (liquidity rule iii) — `interpreted`
- Cite: `RS/2020-05-12_economic-club-of-new-york.md` (S): "So it's the biggest liquidity injection relative to history I've ever seen…" (Fed out-bought issuance by ~$1T Mar–Apr 2020; net goes to zero by May, then negative). DS/2023-10-24 (S): deficit concerns now enter trading decisions.
- Formula: `F_t = Δ(TREAST + WSHOMCB)` (Fed outright Treasury + MBS holdings) over `liq.netliq.window_w`; `I_t = Δ(debt held by the public, marketable)` over same window; impulse = `F − I`. Sign change confirmed per `liq.confirm_periods`.
- Params: `liq.netliq.window_w`, `liq.confirm_periods`.
- Inputs: `TREAST`, `WSHOMCB` (2002-12→); TFD "Debt to the Penny" (1993-04→ daily) or Monthly Statement of the Public Debt; pre-1993 quarterly `FYGFDPUN`.
- Conflicts: the ECNY transcript itself was not reviewed (Medium copy 403; ECNY site search found no transcript). The formula follows Felder's verbatim excerpt only. The May 2020 application of this rule was followed by a large rally and reversed within weeks (DS/2020-06-08); the engine must let R-60 (breadth thrust) and R-29 (chart) override it at the expression stage.
- PIT: Debt to the Penny published next business day; H.4.1 Thursday.

### R-05 Policy error is the main opportunity — `stated`
- Cite: `RS/2015-01-18_lost-tree-club-speech.md` (NP): "about 80 percent of the big, big money we made was in bear markets and equities because crazy things were going on in response to what I would call central bank mistakes."
- Formula: theses triggered by `policy_error_sign ≠ neutral` (T03–T05, T14) receive one extra evidence family in step 5 (R-38).
- Params: `tier.min_independent_evidence`. Inputs: R-06 output.
- Conflicts: RS/2018-09-06 (NP notes): "about 70% of my money … in currencies and bonds." Compatible (bear-market profits were earned in bonds/FX), different metric.
- PIT: n/a.

### R-06 Policy-error sign via unemployment-gap Taylor variant — `interpreted`
- Cite: `RS/2015-01-18_lost-tree-club-speech.md` (NP): "the lowest guess was 3 percent and the highest was 6 percent. So, we had great conviction that the Federal Reserve was making a mistake…" Supporting uses: DS/2016-05-04 (S; Taylor average ~3% vs 0.5%), DS/2017-12-12 (NP; Taylor ~4% vs 1%), RS/2018-09-06 ("came down from Mars" 4–5% vs 1.75%), DS/2015-04-15 (NP; 3.5% / 1.75% vs 0).
- Formula: `i*_t = r* + π_t + a(π_t − π*) + b(NROU_t − UNRATE_t)`, π = CPI yoy (core CPI `CPILFESL` from 1957 as sensitivity). `TG_t = FF_t − i*_t`. `too_loose` if `TG < −policy.tg_threshold_pp`; `too_tight` if `TG > +policy.tg_threshold_pp`.
- Params: `policy.taylor_rstar_pct`, `policy.taylor_pi_target_pct`, `policy.taylor_infl_coef`, `policy.taylor_ugap_coef`, `policy.tg_threshold_pp` (tunable); `policy.taylor_rstar_sensitivity` (sensitivity report only).
- Inputs: `UNRATE` (1948→), `NROU` (CBO; ALFRED vintages sparse), `CPIAUCSL`/`CPILFESL`, FF.
- Conflicts: his 2003 exercise was "from data alone" by staff, not a Taylor formula; later he cites Taylor variants explicitly. He also says unemployment and payrolls are "the most misleading macro variables" (DS/2026-02-27, NP) — conflict with using UNRATE; retained because it is the only long vintaged slack measure. DS/2024-10-16 (NP): judge restrictiveness from markets, "not from real-rate theory" → R-58 runs alongside.
- PIT: UNRATE first release (first Friday); NROU vintage as of asof (CBO publishes ~Jan/Aug); current-vintage gap reported as diagnostic only (PLAN_REVIEW finding 15).

### R-07 No soft landing once inflation exceeds 4.5% — `stated`
- Cite: `RS/2022-06-10_sohn-2022-collison-conversation.md` (S, Blumenthal): "We've never had a soft landing after inflation has got above 4.5%."
- Formula: flag `R07 = CPIAUCSL yoy > infl.soft_landing_pct` at any point in the trailing `infl.lookback_m` months while policy_direction = tightening → recession prior; feeds T07.
- Params: `infl.soft_landing_pct`, `infl.lookback_m`. Inputs: `CPIAUCSL` (1947→; NSA `CPIAUCNS` 1913→ for era B).
- Conflicts: none in sources. Outcome-dependent evidence (2023) not used here.
- PIT: CPI released ~mid-month; SA factors revised each Feb — use vintage.

### R-08 Above 5%, inflation has not fallen without FF above CPI — `stated` (with source caveat)
- Cite: `DS/2022-06-XX_sohn-2022-john-collison.md` (NP fan transcript): "Once inflation gets above 5%, it's never come down unless Fed funds have gotten above the CPI." Same event, RS/2022-06-10 (S, MFO): "this time that will probably be broken."
- Corrected wording: he stated the historical regularity and, in the same conversation, expected it could break in the 2022 cycle because FF would need to exceed ~8%. R-08 is therefore a veto flag (inflation not yet met by policy), not a forecast that FF must exceed CPI.
- Formula: `R08 = (CPI yoy > infl.persist_pct) AND (FF < CPI yoy)`; while true, long-duration and long-equity theses lose one evidence family; T06 may fire.
- Params: `infl.persist_pct`, `infl.r08_expected_to_hold` (= false; display caveat).
- Inputs: `CPIAUCSL`, FF.
- Conflicts: reference doc §7.1 called the "inflation falls without FF > CPI" attribution a summarizer error; two independent summaries plus the fan transcript context support it (see `reference_corrections.md`).
- PIT: as R-07.

### R-09 Above 5%, inflation never tamed without recession — `stated`
- Cite: `DS/2022-06-XX_sohn-2022-john-collison.md` (NP): inflation above 5% "has never been tamed without a recession" (summary wording); he expected this rule to hold.
- Formula: when CPI yoy peak in trailing `infl.lookback_m` months > `infl.persist_pct` and policy tightening, recession prior → T07; no soft-landing expression for long cyclicals.
- Params: `infl.persist_pct`, `infl.lookback_m`. Inputs: `CPIAUCSL`, FF.
- Conflicts: none in sources.
- PIT: as R-07.

### R-10 Rates, oil and USD rising together precede falling earnings and stocks — `stated`
- Cite: `DS/2022-06-XX_sohn-2022-john-collison.md`/RS/2022-06-10 (S): "Every time oil is up, interest rates are up, and the dollar is up … things don't tend to go well." `RS/2024-11-06_nbim-in-good-company-podcast.md` (NP): "…the dollar is up, interest rates are up, and oil is up, three death knells for markets, if you look at history." Origin case 2000 (Feig 2009; RS/2018-09-06).
- Formula (window interpreted): `R10 = Δ DGS10 > 0 AND Δ WTI > 0 AND Δ USD > 0` over `xasset.window_m`. Fires T08. The main rule is direction-only. Reported variant (never the primary score): `R10_mag` additionally requires each change to exceed `xasset.min_move_sd` standard deviations of its own `xasset.window_m` change (sd over the expanding as-of history); fidelity is reported with and without the magnitude floor.
- Params: `xasset.window_m` (tunable), `xasset.min_move_sd` (reported variant only).
- Inputs: `DGS10` (1962→; `GS10` 1953→), `DCOILWTICO` (1986→; `WTISPLC` monthly 1946→), USD = `DTWEXBGS` (2006→) spliced with `DTWEXM` (1973–2019) by ratio on overlap; CBP synthetic DXY 1971→ fallback.
- Conflicts: plan E.1 cites Delivering Alpha 2022 for this rule; the DA 2022 transcript does not state it. Correct citations: Sohn 2022, NBIM 2024, Real Vision 2018.
- PIT: daily series same-day; use close of asof.

### R-11 Fragility gauges (alert, non-gating) — `stated` (gauges) / percentile `interpreted`
- Cite: `RS/2015-01-18_lost-tree-club-speech.md` (NP): "If you look at IPOs, 80 percent of them are unprofitable when they come. The only other time we've been at 80 percent or higher was 1999." Also "I just have the same horrific sense I had back in '04. And by the way, it lasted another two years." `DS/2014-07-16_delivering-alpha-kernen.md` (NP): bubble systemic only once in the banking system. `DS/2015-03-02_cnbc-closing-bell-kelly-evans.md` (NP): corporate debt $3.5T → $7T.
- Formula: composite = mean of as-of expanding-window percentiles of: Ritter unprofitable-IPO share (annual, 1980→), SIFMA HY share of corporate issuance (1996→), `BCNSDODNS`/GDP `fragility.credit_gdp_change_q`-quarter change (1951→), net equity issuance from Z.1 (buybacks), HY OAS `BAMLH0A0HYM2` inverted (1996→; tight = excess), FINRA margin debt/GDP. `fragility_level = high` if composite > `fragility.high_percentile`. Missing components dropped; < `fragility.min_components` components → unknown.
- Params: `fragility.high_percentile` (tunable), `fragility.min_components`, `fragility.credit_gdp_change_q`, reference levels `fragility.*_ref_pct` (display).
- Inputs: as listed (D-19). CAPE excluded (display context only).
- Conflicts: B-rated share 71% (Lost Tree) vs 70% B-or-worse (DA 2014); 1999 unprofitable IPO 80% vs 83%. Cov-lite and B-rated share have no free history (gap). Non-gating per reference §2.4 ("alerts, not timing").
- PIT: Ritter annual published with ~months lag (use publication date or Jan of year+1); Z.1 quarterly ~10 weeks after quarter; SIFMA monthly.

### R-12 Cross-region policy block — `interpreted`
- Cite: `DS/2015-03-02_cnbc-closing-bell-kelly-evans.md` (NP): "The one thing we learned in the United States about QE is it definitely inflates financial asset prices." (net long Japan/Europe where QE was starting). `DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md` (NP): diverging policy is a "textbook" currency opportunity. DS/2013-05-08 (S): Japan QE ~3× US relative to market cap.
- Formula: per region, balance-sheet impulse = Δ assets/GDP over `xregion.window_w` (Fed `WALCL`, ECB `ECBASSETSW`, BoJ `JPNASSETS`, BoE weekly bank return) and policy-rate direction (FF; ECB DFR; BoJ call; Bank Rate). Relative impulse `rel(X,US) = impulse_X − impulse_US`. Long-rate levels `IRLTLT01{US,DE,GB,JP,FR,IT}M156N` (1960→).
- Params: `xregion.window_w`.
- Inputs: as listed (D-8b). Pre-1999 EA = Bundesbank (gap: no free long series in plan).
- Conflicts: none; construction is entirely ours.
- PIT: ECB weekly statement Tuesday; BoJ ~monthly/10-day; OECD long rates monthly with lag.

### R-13 Valuation is context only, judged relative to policy — `stated`
- Cite: `DS/2015-03-02_cnbc-closing-bell-kelly-evans.md` (NP): "By historic fundamental measures we are extremely high." (then "appropriately priced" relative to policy). DS/2014-07-16 (NP): "the bubble is appropriate given monetary policy." NMW (P, unverified wording): valuation tells how far a move can go once a catalyst appears.
- Formula: valuation never sets direction; used only to scale payoff asymmetry (R-28) and in display.
- Params: none. Inputs: none required.
- Conflicts: DS/2023-11-01 (NP) uses 20× vs 15× forward P/E as a reason for a flat decade; DS/2026-02-27 "valuations toward the top of the range." Treated as context.
- PIT: n/a.

### R-14 Stay long until the Fed tightens; QE end and balance-sheet rate of change matter — `stated`
- Cite: `DS/2014-07-16_delivering-alpha-kernen.md` (NP summary of transcript): playbook "stay long until the Fed tightens," setbacks followed QE1, QE2 and Japan's QE exits. `RS/2018-09-06_sokoloff-real-vision-interview.md` (NP notes): central-bank buying ~$1T/yr going to zero within 12 months. `DS/2021-05-11_hustle-mfm-trung-phan.md` (NP): "the minute they start tightening, the equity market should go down a lot."
- Formula: `policy_direction` = Fed cycle state: the direction of the most recent policy-rate change, held until a change in the opposite direction (decision R14-04, 2026-10-07, replacing the sign of a `policy.ff_change_window_m`-month change, which forgot the cycle between moves: 2003-04 and 2014-15 read neutral at 1% and 0% rates before any hike). Policy-rate record: FF target range upper bound `DFEDTARU` (2008-12-16 on), FF target `DFEDTAR` (1982-09-27 to 2008-12-15), Fed discount rate `FED_DISCOUNT_RATE` (`spec\fed_discount_rate_events.yaml`, FRED DISCOUNT, 1948-2002) before; a level difference at a join between records is not a move. When no policy-rate change is on record, the balance-sheet programme component (rate-primary; owner decision 2026-10-07 replacing the sum of the two signs, which read cuts during slowed runoff 2024-09..2025-11 as neutral against DS/2024-10-01 and DS/2024-10-16; the Fed names the FF target its primary means, 2022-01-26 principles; DS/2018-12-16 "double-barreled" is preserved in sign when both tighten). Programme component: the state in force in `spec\fomc_bs_events.yaml` (series `FOMC_BS_STATE`): announced net-purchase or maturity-extension programme in force → easing (taper phases included); announced runoff in force → tightening; otherwise (no programme before 2008-11-25, reinvestment only, technical reserve-management purchases) → neutral. QE-end setback flag: a programme in force within `liq.qe_end_setback_m` months but not now.
- Revision 2026-10-07 (owner decision; evidence `spec\research_R14_balance_sheet.md`): replaces "`policy.holdings_change_window_w`-week change in Fed securities holdings, taper = tightening when second derivative of holdings < 0 after QE". The library holds no statement treating a US taper as tightening (taper read as still easing: DS/2009-XX-XX Citi FXLM, DS/2014-06-19 WSJ op-ed (P), DS/2014-07-16, DS/2022-06-XX); QT read as tightening (DS/2018-11-21, RS/2018-09-06); stimulus read as on/off (DS/2012-04-XX Grant's). The holdings arithmetic read 2004-06 hikes and 2008 cuts as neutral (currency growth, sterilisation) and most of 2010-2019 as taper. Construction overlap: the runoff windows share their source (FOMC statements) with the QT windows of the Fed-cycle check labels (scoring.md §6d); agreement there is by construction, not evidence.
- Params: `liq.qe_end_setback_m` (`policy.ff_change_window_m` and `policy.holdings_change_window_w` retired 2026-10-07). Inputs: `DFEDTARU`, `DFEDTAR`, `FED_DISCOUNT_RATE`, `FOMC_BS_STATE` (federalreserve.gov releases, PIT at release time ET).
- Conflicts: DA 2014: "focus on rate level more than first hike" vs 2021 "minute they start tightening." Engine uses first tightening as transition and rate level via R-06.
- PIT: FOMC statement 14:00 ET on decision day.

### R-56 10-year yield trades around nominal GDP growth — `stated`
- Cite: `DS/2024-10-16_bloomberg-tv-sonali-basak.md` (NP, ASR transcript): "The golden rule I've always had is the ten year's to trade around where nominal GDP is…"
- Formula: `gap = DGS10 − yoy(GDP nominal)`; gap < `rates.ngdp_anchor_gap_pp` adds one evidence family to short-duration theses (T03, T18); gap > +`rates.ngdp_cheap_gap_pp` adds one to long duration (interpreted symmetry).
- Params: `rates.ngdp_anchor_gap_pp`, `rates.ngdp_cheap_gap_pp`. Inputs: `DGS10`, `GDP` (ALFRED vintage; quarterly, advance ~30 days after quarter).
- Conflicts: DS/2026-08-24 (S): 10y "at or below nominal GDP growth" used in same sense. Symmetry for long duration not stated.
- PIT: GDP advance estimate vintage.

### R-58 Financial conditions as the restrictiveness gauge — `stated` (principle) / formula `interpreted`
- Cite: `DS/2024-10-16_bloomberg-tv-sonali-basak.md` (NP): "I'm a market animal. Frankly, we've found over the years that markets are better predictors than professors." `DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md` (NP): "Once financial conditions took off, it became very clear that this thing could go either way. So I exited the position."
- Formula: `fci_state = loose` if `NFCI < fci.loose_threshold` and `fci.change_window_w`-week Δ NFCI < 0; `tight` if NFCI > 0 and rising. Loose FCI during easing → evidence against long duration (premise break for T05/T17); tight FCI with too_tight TG → evidence for T05.
- Params: `fci.loose_threshold`, `fci.change_window_w`. Inputs: `NFCI` (1971→ weekly).
- Conflicts: none.
- PIT: NFCI published Wednesday 08:30 ET for prior week; revised — use vintage (ALFRED has NFCI vintages).

### R-63 Fiscal supply as a duration driver — `interpreted`
- Cite: `DS/2023-11-01_cnbc-squawk-box-yellen-debt-drunken-sailors.md` (NP): "I made a lot of money this year betting on bonds going down because of the debt and had nothing do with the economy." DS/2023-10-24 (S): threw out the rule against letting deficits drive trading.
- Formula: R-04 issuance term `I_t` relative to GDP above its `fiscal.issuance_median_y`-year as-of median, with deficit/GDP (`FYFSGDA188S`, annual) > `fiscal.deficit_gdp_pct`% at UNRATE < NROU → one evidence family for short duration.
- Params: `fiscal.issuance_median_y`, `fiscal.deficit_gdp_pct`, `fiscal.active_from_year` (none tunable). Inputs: TFD, `FYFSGDA188S`, `UNRATE`, `NROU`.
- Conflicts: he described ignoring deficits for most of his career (DS/2023-10-24) → era-dependent; rule active only from `fiscal.active_from_year` in fidelity scoring by design note (registered here before scoring).
- PIT: annual deficit series published with lag; use monthly Treasury statement cumulative where available.

### R-66 Regime probability mapping — `interpreted`
- Added 2026-10-07 (phase E3), before any engine output was scored against a case. Required by the Decision schema 2 regime vector (daily P(easing), P(neutral), P(tightening), each ≥ 0.01; owner decision 2026-10-07). Not his construction; the mapping is a transparent count of the step-1 rule outputs that bear on policy direction.
- Cite: no source statement. Construction rests on R-14 (defines `policy_direction`), R-01 and §9 (liquidity rule family R-02/R-03/R-04 as one family), R-38 (independent evidence families counted with unit weight).
- Formula: evidence families for the US vector: (1) **R-14** — its own output (sign of the FF-target change plus the holdings component) → easing / neutral / tightening; (2) **liquidity family** (PLAN E.4a: era B → R-02; era A → R-03 and R-04, sign of the sum of their confirmed signs; when the era's variant is unknown or not held, the other era's variant, labelled as fallback) → positive impulse = easing, negative = tightening, neutral band = neutral. Each known, held family adds `regime.prob_family_increment` × timeline weight to the class it points to; every class starts with `regime.prob_base_mass`: `mass[c] = base + Σ_f inc × w_f × 1[f → c]`, `P[c] = mass[c] / Σ mass`, floored at `regime.prob_floor` and renormalised. Unknown or not-held families contribute nothing; with no known family the probabilities are unknown (not uniform). `policy_direction = argmax P`; ties go to the R-14 output (the rule that defines `policy_direction`), else neutral, else the first known family's class. Other regions (EA, JP, UK): one family, the R-12 region direction (sign of policy-rate direction minus balance-sheet-impulse sign over `xregion.window_w`, the R-14 construction on the R-12 inputs), same formula and tie rule.
- Resulting values (base 0.1, increment 1, weights 1): both US families agree → 0.913 / 0.043 / 0.043; they disagree → 0.478 / 0.478 / 0.043 with the R-14 class chosen; one family known → 0.846 / 0.077 / 0.077.
- Revision 2026-10-07 (owner decision, before any R-66 score was read; the baseline run of c6fefbd keeps 1.0 as the reference stage): base mass 1.0 → 0.1. With 1.0 the largest attainable probability was 0.6; a forecast with every direction correct then scores RPS 0.10 on each agreeing date against ≈ 0 for the always-easing reference, so Gate 1 (spec\scoring.md §6c) was unpassable by construction. Derived from the RPS formula alone (`fatpitch.cases.regime.rps`), no case outcome read.
- Excluded from the mapping, with reason: R-06 and R-58 measure the stance of policy against a benchmark (level), not its direction (R-21: change, not level), and enter at steps 2/5 (R-05, R-58 premise text); R-07 and R-09 take `policy_direction` as an input (circular); R-08 and R-10 are veto flags; R-11 never sets direction (R-48); R-56 and R-63 are duration evidence; step-1b internals are equity-market evidence for step 2 ("evidence, not confirmation"). R-12 US duplicates R-14 inputs and is not counted for the US.
- Process timeline (`spec\claims\process_timeline.yaml`): a rule is held at date t unless its era code for t's era is `absent` or `n/a`; held rules get weight 1 (`reduced`/`minor` are not converted to fractions: the timeline gives no numbers). Era code `unknown` counts as held (no evidence of absence; PLAN E.4a makes R-02 the era-B measure). A `held_until` that is a plain date ends the rule; a qualified one (R-08, "as a forecast rule") does not gate the R-08 veto flag. Dates before 1977 use the E1 code. Without the file every rule is held at weight 1.
- Params: `regime.prob_base_mass`, `regime.prob_family_increment`, `regime.prob_floor` (none tunable; PLAN E.6 cap of 8 is full). Inputs: outputs of R-02, R-03, R-04, R-12, R-14; process timeline.
- Conflicts: in era A the R-14 holdings component and R-03/R-04 both read Fed holdings (overlap is partial: R-03 nets TGA and RRP, R-04 nets Treasury issuance); counted as separate families because process.md lists them as separate rules. The probabilities are coarse by design (few families, no fitted calibration); calibration is out of scope until E7.
- PIT: as the input rules.

### R-67 Anticipated policy turn — `interpreted` — hybrid track only (warning flag; design v2 V2-B 2026-10-07 after D3 failed §6e)
- Added 2026-10-07 (owner decisions: design D3; hybrid track only; warning flag until it passes scoring.md §6e). Source: `spec\research_market_implied_fed.md`. Not part of the Druckenmiller-faithful track: the library holds no statement of him using market pricing to forecast the Fed; his record is trading against that pricing (2-year trades 2000, 2018-19, 2021, 2023) and calling the market signal impaired under QE (DS/2021-06-10, DS/2022-06-XX). Inflation momentum has support (NMW 1981 (P); DS/2021-01 "inflation relative to what policymakers think"; DS/2024-05-07 six-month annualised), but the owner placed both parts in the hybrid track.
- Revision v2 (2026-10-07; decisions R67-05 design V2-B, INFL-04 weighted inflation composite, R67-06 calculation fixes; source `spec\research_R67_v2_R68.md` §§2, 3 V2-B, 3a). D3 failed §6e on 2026-10-07; the v2 retest is exploratory and in-sample (same Fed history), with predictions written in `spec\decisions.yaml` R67-05 before the run. D3 (bill forward on discount yields, one inflation series, inflation fallback in both directions) is superseded.
- Legs (+1 tightening, −1 easing, 0 neutral):
  - M2 (path, C3): `M2_bp = (DGS2 − FF) × 100` (`DGS1` − FF before `DGS2` exists, 1976-06), FF = `DFF` (`FEDFUNDS` when `DFF` is unavailable), reading at the asof close, no smoothing; tightening if > `antic.path_band_bp`, easing if < −`antic.path_band_bp`.
  - MB (bill forward, C1, decision R67-06): bill prices `P_k = 1 − d_k·t_k/360` from the discount yields `DTB3`, `DTB6` (t3 = 91, t6 = 182 days, bill conventions); `f = (P3/P6 − 1)·360/91`; `r3 = (1/P3 − 1)·360/91`; `MB_bp = (f − r3)·10⁴`, mean over the latest `antic.smooth_d` common trading days; class beyond ±`antic.band_bp`. Replaces `2 × (DTB6 − DTB3)`, which understated the forward by 1.0–64.0 bp at 2–15% rates (research §1 D-6).
  - I4 (inflation composite, C2, decision INFL-04): per measure j — headline CPI (`CPIAUCSL` SA vintage; `CPIAUCNS` before the SA vintage store, 1972-07-21), core CPI (`CPILFESL` SA vintage from 1996-12-12; `CPILFENS` before, where usable: its pre-1996-12 rows are `pre_vintage: unknown`, so core CPI is absent before 1996-12), PCE (`PCEPI`) and core PCE (`PCEPILFE`) (ALFRED vintages from 2000-08-01; absent before) — `π6_j` (`antic.infl_short_m`-month annualised), `π12_j` (`antic.infl_long_m`-month), `I_j = π6_j − π12_j` on the as-of vintage; NSA series use the seasonally neutral form `I_j = (ann6_j(t) − ann6_j(t − 12 months)) / 2` (decision R67-06; `π6_j` itself stays the unadjusted 6-month annualised rate). Precision weight `w_j = 1 / var(ΔI_j)`, the sample variance of the month-to-month change of `I_j` over the trailing `antic.infl_weight_window_m` monthly changes within the as-of vintage, at least `antic.infl_weight_min_n` changes, else the measure is excluded. Composite `I = Σ w_j I_j / Σ w_j` and `π6 = Σ w_j π6_j / Σ w_j` over the known measures, each at its own latest observation (no alignment to a common month); fewer than `antic.infl_min_known` known measures → I4 unknown (absent where fewer measures exist in the era, C4). Class: tightening if `I > antic.infl_band_pp` and `π6 > policy.taylor_pi_target_pct`; easing if `I < −antic.infl_band_pp`; else neutral. Each measure's `I_j`, `π6_j`, `π12_j` and normalised weight are reported. The owner chose weighting over the strict majority recommended in research §2a.
  - Gr (growth/stress, easing side only, research §2b): on if the R-10 flag holds, or (R-15 direction = down, confirmed, and every known R-17 credit spread — `BAA` − `GS10` and, where it exists, `BAMLH0A0HYM2` — is wider than `internals.curve_credit_trend_m` months earlier); off while the R-08 condition holds. Reading of "every known": a spread that exists but is unknown at asof is skipped; with no known spread the conjunct is unknown. R-10, R-15 and R-17 run at their registered values regardless of the process timeline.
  - ZLB: at `DFF` < `antic.zlb_ff_pct` an easing reading of any leg is neutral (Gr off); tightening readings stand.
- Combination (V2-B): (1) M2 non-neutral → M2, except M2 tightening with I4 easing → neutral. (2) Else MB non-neutral → MB, except MB tightening with (I4 easing or Gr on) → neutral. (3) Else T = I4 tightening held, E = Gr on held: T only → tightening; E only → easing; both or neither → neutral. Held = the same reading at 2 consecutive month ends (definition, unchanged from D3): I4 within the as-of vintage (each measure's previous observation, as D3); Gr at the previous month end, read point-in-time through the Source.
- Absent vs unknown (C4): a leg whose input series has no usable data at asof (the series does not exist in that era) is absent and the rule is computed from the remaining legs; a leg whose data exist but are stale or not computable is unknown, and the output is unknown only when the result depends on it (as D3: an unknown market leg passes to the next step; a guard or hold that cannot be evaluated makes the output unknown). With no known leg the output is unknown.
- Output: anticipated direction, the component that decided (M2, MB, I4, Gr, a guard, or fallback), every leg's value and class, the I4 per-measure block, onset date and lead age where computable (M2, MB, I4). The §6e report adds the deciding component per scored turn, the known-measure count per era (C4 check) and the CPI–PCE bias block (research §2a).
- Role: pre-turn warning flag (`anticipated_turn` when R-67 ≠ the R-14 class); no effect on the regime vector, Gate 1 or §6d until it passes §6e; a v2 pass does not make it an R-66 family until a confirmation evaluation also passes (research §5 stopping rule).
- Constants (fixed, none tunable; cap of 8 full): `antic.path_band_bp`, `antic.band_bp`, `antic.horizon_m`, `antic.smooth_d`, `antic.zlb_ff_pct`, `antic.infl_short_m`, `antic.infl_long_m`, `antic.infl_band_pp`, `antic.infl_weight_window_m`, `antic.infl_weight_min_n`, `antic.infl_min_known`, `policy.taylor_pi_target_pct`. Gr reuses `xasset.window_m`, `internals.rs_lookback_m`, `internals.turn_confirm_m`, `internals.curve_credit_trend_m` and `infl.persist_pct` at their registered values (frozen for the retest). Arguments in the registry and research §3a.
- Inputs: `DGS2`, `DGS1`, `DFF`, `FEDFUNDS`, `DTB3`, `DTB6`, `CPIAUCSL`, `CPIAUCNS`, `CPILFESL`, `CPILFENS`, `PCEPI`, `PCEPILFE`; Gr: the R-10, R-15, R-17 and R-08 inputs. Era coverage in the lake: Gr is absent before 1986 (R-10 oil series) and R-10-only until the R-15 sector-ETF history allows the look-back (step1b); I4 has one measure (absent) before 1996-12, two to 2000-08, four after.
- Conflicts: as above; supply shocks move headline measures (1973, 1979, 1990, 2008); weighting damps them where core measures are steadier.
- PIT: bills and yields daily same-day; inflation measures at their release times (as-of vintage); hold readings as stated above.

### R-68 Inflation relative to what policymakers think — `stated` (principle) / formula `interpreted` — hybrid track only, report-only
- Added 2026-10-07 (decision R68-02: hybrid track only; the recommended faithful policy-error placement was not chosen). Source: `spec\research_R67_v2_R68.md` §4.
- Cite: `DS/2021-01-XX_talks-at-gs-great-investors-pasquariello.md` (NP): "my overriding theme is inflation relative to what policymakers think." Context in the same note: the Fed was expected not to let rates rise, so the gap identifies a policy error rather than an imminent move.
- Formula (G1): `G = π6(core PCE) − P_y`. `π6` = `r68.short_m`-month annualised change of `PCEPILFE` (as-of vintage). `P_y` = the SEP core PCE inflation projection (Q4/Q4) for the calendar year containing asof, from the latest SEP published at asof (`FOMC_SEP`, read per statistic as `SEP_CORE_PCE_MEDIAN`, `SEP_CORE_PCE_CT_LOW`, `SEP_CORE_PCE_CT_HIGH`): the median when that SEP publishes one (from 2015-09-17), else the central-tendency midpoint. In January–March before the year's first SEP, the December SEP's next-year column is the current year. Raw class: behind (G > `r68.band_pp`), ahead (G < −`r68.band_pp`), in line. Reported class: behind or ahead when the raw class holds at `r68.hold_month_ends` consecutive month ends (each month end read point-in-time, including the SEP in force then), else in line.
- Unknown: before the first SEP (2007-11-20), when the latest SEP is older than `r68.sep_max_age_d` days, when core PCE is unknown, or when a needed previous month-end reading is unknown.
- Role: report-only evidence line in the hybrid track and a column in the §6e report; not an R-67 input (V2-C not chosen); no effect on the regime vector, Gate 1, §6d or §6e gating.
- Params: `r68.short_m`, `r68.band_pp`, `r68.hold_month_ends`, `r68.sep_max_age_d` (none tunable). Inputs: `PCEPILFE`, `FOMC_SEP`.
- Conflicts: SEP medians and the central-tendency midpoint differ by construction (variant break 2015-09); core PCE first releases are revised within a 6-month window.
- PIT: SEP numbers at their release time (with the minutes to the 2011-01 meeting, meeting day 14:00/14:15 ET after; `spec\fomc_sep_events.yaml` header); core PCE at its release time.

## 2. Step 1b — Market internals

Output: internals vector {leading-industry RS direction and age of turn, breadth state, curve signal, credit signal, cross-asset trend}; input to step 2 as evidence, not confirmation.

### R-15 Internals lead the economy by 6–12 months — `stated`
- Cite: `DS/2022-06-XX_sohn-2022-john-collison.md` (NP): "Stocks tend to lead the fundamentals by somewhere between 6 and 12 months." DS/2019-06-03 (S): "the best economic indicators are inside the stock market."
- Formula: internals direction = sign of the median RS over `internals.rs_lookback_m` of the leading set (R-16) vs the market; a turn is a sign change confirmed for `internals.turn_confirm_m` months. Turn age tracked in months.
- Params: `internals.lead_m`, `internals.rs_lookback_m`, `internals.turn_confirm_m`.
- Inputs: Fama-French 49-industry monthly returns (1926→, CBP); sector ETFs daily (1998→); Alpaca (2021→).
- Conflicts: DS/2015-04-15 (NP): China 2015 equity thrust read as recovery signal "6 to 12 months down the road," which failed; he cut confidence to ~70% himself (immature/policy-driven market). Engine applies R-15 only to US/developed markets.
- PIT: French data posted monthly with ~1-month lag (use posting date or month-end + 30 days); ETF prices same day.

### R-16 Leading industries turning — `stated` (industries) / mapping `interpreted`
- Cite: `RS/2022-06-10_sohn-2022-collison-conversation.md` (S) and `DS/2022-06-XX_sohn-2022-john-collison.md` (NP): homebuilders −50%, trucking −40% despite record earnings, retail. `DS/2019-06-03_econclub-ny-bessent.md` (S): retail −24%, Russell 2000 −15%, metals −20%. `DS/2018-12-16_wsj-oped-warsh-fed-tightening-not-now.md` (S): banks, housing, transports, industrials down double digits.
- Formula: leading set `internals.leading_set` mapped to French-49 {Rtail, Trans, Banks, Steel/Mines, Chips} plus homebuilding via `BldMt`/`Cnstr` and small caps via size factor; ETFs XHB, IYT/XTN, XRT, KBE, XME, IWM, SMH (2006→). RS = industry return − market return over `internals.rs_lookback_m`; aggregate = median.
- Params: `internals.leading_set`, `internals.rs_lookback_m` (tunable).
- Inputs: as R-15.
- Conflicts: "leading" is defined by examples, not a list; the set is fixed here before scoring. DS/2026-02-27 (NP): company-level mosaics and leader/lagger comparison remain the main macro input; mosaics are not mechanizable (gap).
- PIT: as R-15.

### R-17 Bond market and credit signal (impaired under QE) — `stated`
- Cite: `DS/2022-06-XX_sohn-2022-john-collison.md` (NP summary): bond-market signal corrupted by central-bank buying for 10–11 years. `DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md` (NP): yield curve as a trade is "over-rated."
- Formula: curve signal = `DGS10 − DGS2` (1976→; `GS10 − TB3MS` 1934→ era B) direction over `internals.curve_credit_trend_m` months; credit signal = `BAA − DGS10` (1962→; `BAA−GS10` 1953→) and `BAMLH0A0HYM2` (1996→) trend over `internals.curve_credit_trend_m` months. Weight × `internals.qe_signal_weight` when a purchase programme is in force (`FOMC_BS_STATE` = EXPAND, the R-14 programme table) — interpreted implementation of "impaired." Revision 2026-10-07 (owner decision): replaces "Fed securities holdings/GDP rising", which flagged QE in ordinary pre-2008 currency-driven growth.
- Params: `internals.curve_credit_trend_m`, `internals.qe_signal_weight` (none tunable). Inputs: as listed.
- Conflicts: "prescient historically" (reference §2.3, Sohn 2022) vs "over-rated" (2026). Retained as evidence, never a trigger alone.
- PIT: daily same-day; BAA monthly average (era B) embeds intra-month info.

### R-18 Momentum bottoms 12–18 months before fundamentals; multi-horizon charts — `stated`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP summary): daily charts predict 8–20 days, weekly 8–20 weeks, monthly 8–20 months; momentum tools bottom 12–18 months before fundamentals.
- Formula: second-derivative momentum = Δ(rate of change) on monthly closes (`chart.monthly_roc_m`-month ROC, its `chart.monthly_roc_change_m`-month change) for each class index; a momentum bottom = ROC 2nd derivative turns positive while ROC < 0. Used by T16.
- Params: `internals.momentum_bottom_lead_m`, `chart.monthly_roc_m`, `chart.monthly_roc_change_m`.
- Inputs: S&P 500 monthly (Shiller/CBP 1871→ display; `SP500` FRED 10-year only), class indices.
- Conflicts: 12–18m (Feig) vs 6–12m (Sohn 2022). Different objects; both kept.
- PIT: monthly close.

### R-19 Cross-asset trend — `interpreted`
- Cite: `DS/2023-04-24_nbim-annual-investment-conference.md` (NP): "The technical provides a discipline on the fundamental and the fundamental provides a discipline on the technical."
- Formula: `chart.monthly_roc_m`-month and `chart.trend_lookback_w`-week trend sign for SPY/US equity, 10y yield, USD, gold, WTI, copper; vector input to expression ranking and chart veto.
- Params: `chart.trend_lookback_w`, `chart.monthly_roc_m`. Inputs: FRED daily series; CBP World Bank monthly commodities 1960→; `DEX*` FX 1971→.
- Conflicts: none.
- PIT: same-day closes.

### R-59 Leadership narrowing is a necessary (not sufficient) bear-market condition — `stated`
- Cite: `RS/2024-11-06_nbim-in-good-company-podcast.md` (NP): "We've never had a bear market start without the leadership narrowing... it's a yellow light, it's not a red light."
- Formula: share of French-49 industries above `internals.industry_trend_w`-week trend falls by ≥ `internals.narrowing_drop_pts` over `internals.narrowing_window_m` months while market index above trend → `narrowing = true` (fires T22). Equal-weight vs cap-weight (RSP/SPY, 2003→) as era-A cross-check.
- Params: `internals.narrowing_drop_pts`, `internals.industry_trend_w`, `internals.narrowing_window_m`.
- Inputs: French-49 daily/monthly; RSP, SPY.
- Conflicts: none.
- PIT: as R-15.

### R-60 Breadth thrust signals recovery 6–12 months out — `stated` (principle) / construction `interpreted`
- Cite: `DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md` (NP): "Whenever I've seen a stock market explode on record volume and record breadth… 6 to 12 months down the road, you're out of recession." `DS/2020-06-08_cnbc-squawk-box-humbled-underestimated-fed.md` (S): breadth thrust changed his mind in June 2020.
- Formula: `internals.breadth_thrust` (classic Zweig breadth thrust on advancing/declining issues; definition in the registry) by source segment: NYSE issues 1965-03-01 → 2020-02-10 and from the start of forward collection; S&P 500 members 2021-09-22 → with thresholds `internals.breadth_thrust_spx_low` / `internals.breadth_thrust_spx_high` (provisional); gap 2020-02-11 → 2021-09-21 uses `internals.breadth_thrust_industry_fallback` (above trend per `internals.industry_trend_w`), output flagged `breadth_source`. A thrust overrides a negative liquidity impulse (R-04) for equity direction for `internals.thrust_override_m` months (premise break for T02/T10/T20). Sensitivities, report only: `internals.breadth_sensitivity_upvolume`, `internals.breadth_sensitivity_pct50_thrust`.
- Params: `internals.breadth_thrust`, `internals.breadth_thrust_spx_low`, `internals.breadth_thrust_spx_high`, `internals.breadth_thrust_industry_fallback`, `internals.industry_trend_w`, `internals.thrust_override_m`, `internals.breadth_sensitivity_upvolume`, `internals.breadth_sensitivity_pct50_thrust`.
- Inputs: NYSE advancing/declining/unchanged issues and up/down volume, Unicorn archive `http://unicorn.us.com/advdec/NYSE_*.csv` (1965-03-01 → 2020-02-10; frozen, free, no licence text; cache once). S&P 500 member breadth from amber: Alpaca daily bars × N-PORT SPX holdings (`S000004310`, quarter-end; 2021-09-22 →): % advancing, % above 50/200-day average. French-49 daily (1926→) for the gap segment. Forward: daily WSJ Markets Diary snapshot (NYSE/Nasdaq adv/dec, volume, new highs/lows; personal research only, WSJ terms restrict automated use; live only, no history). Gap: no free survivorship-free breadth 2020-02-11 → 2021-09-21.
- Conflicts: failed in China 2015 (his own example); restrict to US.
- PIT: daily. Unicorn and WSJ counts available after the 16:00 ET close (WSJ snapshot taken after 16:30 ET). S&P 500 membership from an N-PORT snapshot is used only from its SEC filing date (`filed`), not its report date; Alpaca bars after the close.

## 3. Step 2 — Thesis generation

Mechanism: `spec\transition_table.yaml` (25 rows, authored before reading case outcomes). A thesis exists only on a *transition* (R-21). Each thesis carries class, direction, region, premises, invalidation events, horizon.

### R-20 Never invest in the present; horizon 18 months to 3 years — `stated`
- Cite: `RS/2015-01-18_lost-tree-club-speech.md` (NP): "you have to visualize the situation 18 months from now, and whatever that is, that's where the price will be, not where it is today." `DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md` (NP): trades conceived on 18-month to 3-year horizons. `RS/2024-11-06_nbim-in-good-company-podcast.md` (NP): envision 18–24 months; looks for 2–4 year trends.
- Formula: thesis horizon = [`horizon.min_m`, `horizon.max_m`]; forward view uses R-23 and trend of regime inputs, never current levels alone.
- Params: `horizon.min_m`, `horizon.max_m`, `horizon.trend_y`.
- Conflicts: 12–18m (Sohn 2022 summary), 6–12m (Bloomberg 2015 "what security prices might look at 6 to 12 months"), "a year or two" (NBIM 2023). Range widened per library; reference §7.1 updated.
- PIT: n/a.

### R-21 Change, not level — `stated`
- Cite: `RS/2022-06-10_sohn-2022-collison-conversation.md` (S): "Do not invest in the present. The present doesn't move stock prices, change does."
- Formula: transition table triggers are state changes; a persisting state yields no new thesis (T24).
- Params: `liq.confirm_periods`. Inputs: step 1/1b vectors at asof and prior.
- Conflicts: none.
- PIT: prior-state vector must itself be computed as-of the prior date (no revised recomputation).

### R-22 Theses carry premises; premise end ends the thesis — `stated`
- Cite: `DS/2016-11-10_cnbc-squawk-box-post-election-sold-gold.md` (NP): "I sold all my gold the night of the election. All the reasons I have owned it for the last couple years, it seems to me they may be ending."
- Formula: each thesis stores premises as predicates over regime/internals/event flags (see table); R-50 evaluates them daily.
- Params: `exit.premise_check_freq_bd`, `pit.election_result_time`. Inputs: event calendar (FOMC, elections, policy announcements as manual event flags).
- Conflicts: none.
- PIT: event flags carry their own timestamp; election results as of `pit.election_result_time` (interpreted).

### R-23 Replay-safe forward policy view from the curve — `interpreted`
- Cite: `DS/2023-04-24_nbim-annual-investment-conference.md` (NP summary): 2-year below 4% with FF at 5.25% made owning duration a bet on a hard landing. PLAN_REVIEW finding 4.
- Formula: market-implied path `MP = DGS2 − FF` (1976→), `DGS1 − FF` (1962→) before; `MP < −curve.cut_pricing_bp` = cuts priced; `> +curve.cut_pricing_bp` = hikes priced. Futures (ZQ/SR3) only as live refinement that must reduce to MP when absent; fidelity report states which variant scored each case.
- Params: `curve.cut_pricing_bp` (tunable). Inputs: `DGS2`, `DGS1`, FF.
- Conflicts: none.
- PIT: daily.

### R-24 Region-relative theses — `interpreted`
- Cite: `DS/2015-03-02_cnbc-closing-bell-kelly-evans.md` (NP): long exposure where QE was starting (Japan, Europe), FX-hedged. `DS/2016-11-10_…` (NP): "I'm short bonds globally."
- Formula: T11–T14 use `rel(X,US)` from R-12; expression may be long X equities hedged + short X currency.
- Params: none. Inputs: R-12.
- Conflicts: none.
- PIT: as R-12.

### R-61 Post-bubble bear markets last more than six months — `stated`
- Cite: `DS/2022-06-XX_sohn-2022-john-collison.md` (NP): "Six months bear markets preceded by asset bubbles don't exist, historically."
- Formula: if fragility_level was high within `bear.fragility_lookback_m` months before a ≥ `bear.decline_pct`% index decline began, long-equity theses from T01/T16 are blocked for `bear.post_bubble_min_m` from decline start, unless R-60 fires.
- Params: `bear.post_bubble_min_m`, `bear.fragility_lookback_m`, `bear.decline_pct`. Inputs: index level, R-11.
- Conflicts: R-60 override (June 2020 breadth thrust) — order: R-60 beats R-61.
- PIT: decline start known only after the fact → use first close `bear.decline_pct`% below the as-of running peak.

### R-65 Currency trends persist at least two years — `stated`
- Cite: `DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md` (NP): "I've never seen a major currency trend last less than two years, and it's only been ten months." DS/2023-04-24 (NP): "Currency trends tend to run for at least two or three years."
- Formula: FX theses (T12–T14) keep a persistence prior: a counter-trend move inside `fx.trend_persistence_y` does not break the thesis unless a premise breaks.
- Params: `fx.trend_persistence_y`. Inputs: `DEX*`.
- Conflicts: none.
- PIT: daily.

## 4. Step 3 — Expression selection

### R-25 Focus on what moves the security — `stated`
- Cite: `RS/1992-XX-XX_new-market-wizards-chapter.md` (NP excerpt): "Thereafter, I focused my analysis on seeking to identify the factors that were strongly correlated to a stock's price movement as opposed to looking at all the fundamentals."
- Formula: rank instruments by as-of rolling `expr.beta_window_w`-week beta (weekly returns) to the thesis driver (e.g., Δ DGS2 for rate theses, rel balance-sheet impulse for region theses, Δ USD for FX). Industry-specific driver map: banks → earnings; chemicals/materials → capacity (NMW).
- Params: `expr.beta_window_w` (not tunable). Inputs: instrument returns; driver series.
- Conflicts: none.
- PIT: betas use only returns and driver values published ≤ asof.

### R-26 Multi-asset menu; big bets in liquid markets; assets that rise when equities fall — `stated`
- Cite: `RS/2024-11-06_nbim-in-good-company-podcast.md` (NP summary): concentration plus willingness to use "five buckets"; bonds/currencies offer action in equity bear markets and are more liquid. `RS/2018-09-06_sokoloff-real-vision-interview.md` (NP notes): big bets belong in liquid, ideally 24-hour markets.
- Formula: expression universe per thesis includes rates, FX, commodities, equity indices/sectors, credit; ties broken toward the more liquid class (rates/FX first).
- Params: none. Inputs: universe config.
- Conflicts: none.
- PIT: n/a.

### R-27 Concentric circles (second-order expressions) — `stated`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP summary): more money came from gilts, MATIF and UK equities than from the pound. `RS/2024-11-06_…` (NP): after sterling, bought gilts and UK stocks.
- Formula: for each first-order expression, add instruments with |corr| ≥ `expr.second_order_min_abs_corr` to the thesis driver in other classes, ranked by R-25 beta × R-28 asymmetry; top `expr.second_order_top_n` retained.
- Params: `expr.second_order_min_abs_corr`, `expr.second_order_top_n`. Inputs: as R-25.
- Conflicts: none.
- PIT: as R-25.

### R-28 Payoff asymmetry ("one-way bet") — `stated`
- Cite: `DS/2022-09-28_delivering-alpha-kernen-transcript.md` (NP): "If they didn't devalue in the next six months, my fund was going to lose 50 basis points; if they did devalue, I was going to make 2,000 basis points. So it was a 40-1 one-way risk-reward bet." `DS/2019-06-07_cnbc-squawk-box-one-way-bet.md` (NP): "Soros used to have this thing called the one-way bet…"
- Formula: asymmetry = (distance to thesis target) / (distance to premise-break level) using carry/forward cost for FX (sterling: 0.5% forward cost), R-23 for front-end rates (downside ≈ hikes priced vs upside ≈ cuts to R-06 rate), and R-56 for long rates. Rank expressions by asymmetry within top-beta set.
- Params: `size.asymmetry_min_ratio` (used in step 5). Inputs: forward points (FRED `DEX*` + rate differentials), curve.
- Conflicts: none.
- PIT: same-day.

## 5. Step 4 — Veto

Output: candidate admitted to `starter` or vetoed with reason. Order of class implementation: rates/FX → commodities → equities → crypto (PLAN E5).

### R-29 Chart veto: good thesis, bad chart → no trade — `stated`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP): "I will never invest just on a chart. But if I really like a fundamental thesis and the chart stinks, I won't do it." `DS/2021-05-11_hustle-mfm-trung-phan.md` (NP): "I'm never going to buy something that doesn't have a great chart and fundamentals."
- Formula (interpreted): chart quality = majority of {daily: `chart.daily_roc_d`-day ROC sign; weekly: price vs `chart.trend_lookback_w` MA and its slope; monthly: `chart.monthly_roc_m`-month ROC and its `chart.monthly_roc_change_m`-month change} agrees with thesis direction, and relative strength vs class benchmark not in the bottom `chart.rs_bottom_quantile` fraction. Fail → veto.
- Params: `chart.trend_lookback_w` (tunable), `chart.daily_roc_d`, `chart.monthly_roc_m`, `chart.monthly_roc_change_m`, `chart.rs_bottom_quantile`.
- Inputs: instrument daily closes.
- Conflicts: RS/2018-09-06 (NP notes): "Sometimes no price confirmation needed" — 2000 Treasury bet was pure fundamental conviction. Feig 2009: Brazil 2008 added against the chart as a "1 in 100" violation (process error). Engine keeps the veto; violations are scored as `process` cases.
- PIT: closes as of asof.

### R-30 Price vs news (entry and re-check) — `stated`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP summary): "If all the news is great and the stock's not acting well, get out." `DS/2023-04-24_nbim-annual-investment-conference.md` (NP): "If I've got a thesis and it's really bullish and it's playing out and the stock's not going anywhere, makes me go back and check the thesis over and over."
- Formula: after a scheduled thesis-relevant release (CPI, payrolls, FOMC, earnings for single names), sign of instrument excess return over `exit.price_vs_news_window_bd` vs sign of surprise (actual − prior; consensus not free). Contradiction at entry → veto; while held → R-51.
- Params: `exit.price_vs_news_window_bd`, weight `chart.timing_weight`.
- Inputs: release calendar, release values (ALFRED first release), prices.
- Conflicts: degraded per 2018, 2022, 2023, 2026 statements → R-32.
- PIT: release timestamps.

### R-31 No contrarian fade — `stated`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP): "Contrarian investing is way overrated... the crowd makes money 80% of the time." `DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md` (NP): "I don't care if a trade is crowded if I think the thesis is right and the trend is with me."
- Formula: positioning never vetoes or creates a thesis. Crowding (COT net speculative position percentile over trailing 3 years ≥ `crowd.cot_crowded_percentile`) may only delay starter entry by ≤ `crowd.max_entry_delay_bd` business days (entry-point effect stated in 2026).
- Params: `crowd.right_fraction`, `crowd.max_entry_delay_bd`, `crowd.cot_crowded_percentile`. Inputs: CFTC COT (D-4).
- Conflicts: DS/2015-03-02 (NP): bought the Grexit fear dip; DS/2020-05-12 consensus "Fed has your back" faded and failed. Neither is a positioning rule.
- PIT: COT Tuesday positions released Friday 15:30 ET.

### R-32 Technicals ~20% as effective → low timing weight, veto retained — `stated`
- Cite: `DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md` (NP): "I can unequivocally tell you that technical analysis is about 20% as effective today as it was then because no one was using it." RS/2018-09-06 (NP notes): algos cancelled price-vs-news signals.
- Formula: timing evidence (R-30 contradictions, short-horizon chart) weighted `chart.timing_weight` in tier scoring from `chart.timing_cutover_year` (interpreted cutover: algorithmic share; fidelity reported across its range 2005–2015). R-29 veto unchanged.
- Params: `chart.timing_weight`, `chart.timing_cutover_year`.
- Conflicts: NBIM 2024 (NP): "I'm a technician, so I usually wait for tops" — technicals still used for exits (R-52).
- PIT: n/a.

### R-33 Instrument liquidity — `interpreted`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP summary): size relative to market liquidity so exit costs no more than 1–2% of the fund.
- Formula: veto if `liq.adv_window_d`-day ADV < `liq.instrument_min_adv_usd` or if `size.exit_cost_max_pct_nav` cannot be met at minimum starter size (spread + impact model: `size.adv_participation` of ADV per day).
- Params: `liq.instrument_min_adv_usd`, `liq.adv_window_d`, `size.exit_cost_max_pct_nav`, `size.adv_participation`. Inputs: volume/OI (Alpaca, IBKR stored, COT OI).
- Conflicts: none.
- PIT: trailing volume.

### R-34 Accounting forensics gate — `interpreted-from-article` (weight 0)
- Cite: `RS/2026-03-24_automated-alpha-fat-pitch-filter.md` (S): forensic veto score ≥ 45 (accruals, auditor changes). No primary support.
- Formula: computed for single-name equities only, weight `gate.forensics.weight` = 0; logged, never gating.
- Note: closest primary analogue is DS/2017-12-12 Steinhoff short ("might be crooks"), which is a thesis, not a screen.

### R-35 ROIC / fundamental quality gate — `interpreted-from-article` (weight 0)
- Cite: article (ROIC > 15%, Debt/EBITDA < 2.5×). Weight `gate.roic.weight` = 0.
- Note: conflicts with Teva example (DS/2026-02-27: 6× P/E re-rating story) and "underearning" preference (DS/2017-12-12).

### R-36 Smart money (Form 4 / 13F) gate — `interpreted-from-article` (weight 0)
- Cite: article. Weight `gate.smart_money.weight` = 0.

### R-37 Contrarian COT positioning gate — `interpreted-from-article` (weight 0)
- Cite: article. Weight `gate.cot_contrarian.weight` = 0. Contradicts R-31.

### R-62 Short-side entry: sidestep in poor risk/reward; short rallies, not lows — `stated`
- Cite: `DS/2022-09-28_delivering-alpha-kernen-transcript.md` (NP): "I don't think you need to short. Just sidestep it." `DS/2022-06-XX_sohn-2022-john-collison.md` (NP summary): would re-short after a 15–20% rally. DS/2015-11-04 (S): shorting stocks is "playing against the house."
- Formula: equity short theses admitted to starter only after a ≥ `short.rally_min_pct`% rally from the as-of trailing low within the bear regime; otherwise the action is `reduce`/flat (T02, T08, T15). Rates/FX shorts unaffected.
- Params: `short.rally_min_pct`. Inputs: index closes.
- Conflicts: none.
- PIT: closes.

## 6. Step 5 — Tier and size

### R-38 Invest, then investigate (starter → fat pitch) — `stated`
- Cite: `RS/2018-09-06_sokoloff-real-vision-interview.md` (NP notes): "Normally, I'll wait for– I'll go in with, say, a third of a position and then wait for price confirmation. And when I get that, when I get a technical signal, I go." `RS/2023-XX-XX_nbim-investment-conference-2023.md` (S): "I generally go ahead and buy it and then tell the analyst to look into it. And if it turns out I was wrong after they analyze it I get out." `DS/2009-XX-XX_…` (NP): sterling $1.5B → $5B after Schlesinger's comments.
- Formula: starter = thesis + R-29 pass + R-33 pass. Fat pitch = starter + ≥ `tier.min_independent_evidence` families among {regime (R-02/03/04 aligned), policy error (R-06), internals (R-15/16/60), chart confirmation after entry (R-29 on weekly+monthly), catalyst within `tier.catalyst_window_bd`, asymmetry ≥ `size.asymmetry_min_ratio`}. Failed non-veto evidence lowers tier, never removes. Review at `exit.review_window_w`: thesis evidence count re-scored; drop if below starter.
- Params: `tier.min_independent_evidence` (tunable), `tier.catalyst_window_bd`, `size.starter_fraction`, `exit.review_window_w`, `size.asymmetry_min_ratio`.
- Inputs: step 1–4 outputs; event calendar.
- Conflicts: starter size 1/3 (2018) vs 20–25% (NBIM 2024 sterling) vs "meaningful but not earth-shaking" (NBIM 2024). Sohn 2022: "take a large position on intuition." Starter fraction band [0.20, 0.33].
- PIT: catalyst calendar as known at asof (scheduled events only; unscheduled catalysts arrive as event flags).

### R-39 One or two fat pitches a year — `stated`
- Cite: `RS/2015-01-18_lost-tree-club-speech.md` (NP summary): only one or two times a year is something truly exciting.
- Formula: calibration target for the fat-pitch rate across all classes; scored only on held-out years (PLAN E.4).
- Params: `pitch.per_year`.
- Conflicts: none.

### R-40 Sizing dominates (70–80% of the equation) — `stated`
- Cite: `DS/2022-06-XX_sohn-2022-john-collison.md` (NP): "Sizing is probably 70 or 80% of the equation. It's not whether you're right or wrong, it's how much you make when you're right." Corroborated by RS/2022-06-10 (S, Blumenthal).
- Formula: framing rule; implemented by R-41..R-47, R-57. Size-band agreement reported per case.
- Conflicts: reference doc attributed the figure to Mauboussin (dead source); corrected.

### R-41 Gross leverage ≤ 4:1 — `stated`
- Cite: `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` (NP summary): gross leverage rarely exceeded 4:1.
- Formula: Σ |size_band| across theses ≤ `size.gross_max`; scale pro rata if exceeded.
- Params: `size.gross_max`.

### R-42 Equity net caps — `stated`
- Cite: Feig 2009 (NP summary): equities rarely exceeded 100% net long or 50% net short.
- Formula: net equity ∈ [−`size.eq_net_short_max`, +`size.eq_net_long_max`].
- Params: `size.eq_net_long_max`, `size.eq_net_short_max`.

### R-43 FX cap 150–200% — `stated`
- Cite: Feig 2009 (NP summary): historical maxima 150–200% of the fund in a currency.
- Formula: |single-currency exposure| ≤ `size.fx_max`.
- Conflicts: sterling sizes vary by telling ($7B fund/$5.5B proposed, Lost Tree; $7.5B fund/$7.5B executed, NBIM 2024; $10B, secondary profiles; Soros $15B proposed, Feig/NBIM). Cap unaffected.

### R-44 Bonds ≤ 300% 10-year equivalents — `stated`
- Cite: Feig 2009 (NP summary): 300% in 10-year-bond equivalents.
- Formula: DV01-equivalent exposure ≤ `size.bond_10ye_max` × NAV in 10y-equivalents.
- Conflicts: 350% for the same 2000 trade (Sohn 2022, NBIM 2024); Real Vision says "two and five-year." Engine uses 300%.

### R-45 Size to market liquidity: exit cost ≤ 1–2% of fund — `stated`
- Cite: Feig 2009 (NP summary).
- Formula: per position, estimated exit cost (spread + impact at `size.adv_participation` of ADV) ≤ `size.exit_cost_max_pct_nav`; binding cap = min(class cap, liquidity cap).
- Params: `size.exit_cost_max_pct_nav`, `size.adv_participation`.

### R-46 Hot/cold governs size — `stated`
- Cite: `RS/2018-09-06_sokoloff-real-vision-interview.md` (NP notes): "One of my most important jobs as a money manager was to understand whether I was hot or cold." Feig 2009 (NP): "Don't bet big unless a) you love your thesis, and b) you're hot."
- Formula: scorecard = engine's paper P&L YTD on its own signals (R-53). Hot if YTD ≥ `size.hot_ytd_threshold` → `size.hot_multiplier`; cold if YTD < 0 → `size.cold_multiplier`; else `size.neutral_multiplier`.
- Params: `size.hot_ytd_threshold`, `size.hot_multiplier`, `size.cold_multiplier`, `size.neutral_multiplier`.
- Conflicts: his hot/cold referred to his own fund P&L; applying it to a paper scorecard is interpreted.

### R-47 House money; January 1 reset; never bet big to get even — `stated`
- Cite: Feig 2009 (NP): "If you're up 20 or 30%, you're playing the house money--that's when you try and get up 60% or 70%." DS/2022-06-XX (NP): "when you're cold, the last thing you should do is try and make big bets to get back to even."
- Formula: scorecard resets on `size.risk_reset`; no size increase permitted while YTD < 0.
- Params: `size.risk_reset`.

### R-48 Fragility modifies tier and size, never direction — `interpreted`
- Cite: `RS/2015-01-18_lost-tree-club-speech.md` (NP): alert, "it lasted another two years." DS/2014-07-16 (NP): "I am still dancing… I can get out in a week."
- Formula: fragility_level = high → long size × `fragility.size_multiplier_long`; short theses gain one evidence family (T20).
- Params: `fragility.size_multiplier_long`, `fragility.high_percentile`.

### R-57 Size scales with payoff asymmetry — `stated`
- Cite: `DS/2019-06-07_cnbc-squawk-box-one-way-bet.md` (NP summary): size up where downside small and upside large; size down as asymmetry erodes (2y at 2.30% vs 1.85%). DS/2022-09-28 (NP): 40:1.
- Formula: fat-pitch tier requires asymmetry ≥ `size.asymmetry_min_ratio`; size_band = tier fraction × class cap × liquidity cap × hot/cold × min(1, asymmetry / `size.asymmetry_full_ratio`).
- Params: `size.asymmetry_min_ratio`, `size.asymmetry_full_ratio`.
- Conflicts: none.

`size_band` (% NAV) = tier_fraction (`size.starter_fraction` or 1.0) × class cap (R-42/43/44) × liquidity cap (R-45) × hot/cold (R-46) × fragility (R-48) × asymmetry scale (R-57), then portfolio gross scaling (R-41).

## 7. Step 6 — Monitoring and exits

### R-49 No stop-losses; exit when the reason changes — `stated`
- Cite: Feig 2009 (NP): "I have never used a stop loss in my career." `RS/2021-XX-XX_the-hustle-interview.md` (S, Validea): "I've also never hung onto a security if the reason I bought it has changed. That's when you need to sell." `RS/2024-11-06_…` (NP): "If the reason I bought a stock is no longer the case, I don't care what I paid for it."
- Formula: no price-based stops; exit only on R-50, R-51, R-52, or tier falling below starter.
- Params: `exit.stop_loss` = false.

### R-50 Premise break → exit/reverse within one business day — `stated`
- Cite: `DS/2016-11-10_cnbc-squawk-box-post-election-sold-gold.md` (NP): sold all gold election night. `DS/2019-06-07_cnbc-squawk-box-one-way-bet.md` (NP): "I was over 90% invested. Fat and happy… and decided to go to net flat." (after the 2019-05-05 tariff tweet; regretted spreading over three days). DS/2026-02-27 (NP summary): may reverse a three-year trade within five days.
- Formula: daily evaluation of each thesis's premises (transition table); any false premise → exit flag naming the premise; if the break satisfies another row's trigger (e.g., T23 → T01), the new thesis is generated the same day.
- Params: `exit.premise_check_freq_bd`. Inputs: event flags, step 1/1b vectors.
- Conflicts: political-event premises require manual event flags (not mechanizable).
- PIT: event flags timestamped at publication.

### R-51 Price vs news exit — `stated`
- Cite: Feig 2009 (NP summary): exits when the instrument stops acting well relative to news, or correlations shift.
- Formula: R-30 contradiction while held for `exit.pvn_consecutive_releases` consecutive thesis-relevant releases ([before, from] `chart.timing_cutover_year`) → exit flag (weight `chart.timing_weight` from the cutover year).
- Params: `exit.price_vs_news_window_bd`, `chart.timing_weight`, `chart.timing_cutover_year`, `exit.pvn_consecutive_releases`.

### R-52 Technical tops for exits — `stated`
- Cite: `RS/2024-11-06_nbim-in-good-company-podcast.md` (NP): "I'm a technician, so I usually wait for tops" (top = rate of change flattening; can be a bull flag instead).
- Formula: for winners with intact premises, partial exit (`exit.top_partial_fraction`) when weekly ROC flat or falling for `exit.top_roc_flat_w` weeks and price below its `exit.top_high_window_w`-week high by > `exit.top_atr_mult` × ATR(`exit.atr_window_d`); the remainder exits on premise break only.
- Params: `exit.top_roc_flat_w`, `exit.top_partial_fraction`, `exit.top_high_window_w`, `exit.top_atr_mult`, `exit.atr_window_d`.
- Conflicts: Nvidia episodes (DS/2024-05-07, DS/2024-10-16, DS/2026-02-27): sold winners early on valuation/impatience and called it a mistake → engine never exits on valuation alone.

### R-53 Self-scorecard — `interpreted`
- Cite: DS/2010-08-18 (P): drawdowns' cumulative toll; Feig 2009 (NP summary): watches whether daily P&L behaves as expected.
- Formula: paper P&L of engine signals (next-day open fills, stored bars); feeds R-46/R-47; P&L-vs-expected deviation > `score.deviation_sigma` σ over `score.deviation_window_d` business days → flag (no automatic exit).
- Params: `score.deviation_sigma`, `score.deviation_window_d` (none tunable).

## 8. Step 7 — Cash default

### R-54 No pitch, no play — `stated`
- Cite: `DS/2023-04-24_nbim-annual-investment-conference.md` (NP): "One of the most important things to do is not to play when you don't see a fat pitch. I don't see a fat pitch." DS/2022-06-XX (NP): "I'm waiting for a fat pitch."
- Formula: if no thesis survives step 4, or theses conflict on the same class/region (T25), output "No pitch" with nearest misses (highest evidence count) and blocking vetoes. Starter positions may exist without a fat pitch; cash is the default for the remainder.
- Params: `cash.default`.

### R-55 No long bias — `stated`
- Cite: `DS/2015-03-02_cnbc-closing-bell-kelly-evans.md` (NP): "I don't have any long bias like most investors. I need a reason to be invested in the market."
- Formula: no baseline equity allocation; equity exposure exists only through theses.

### R-64 Political cycle (display only, not used in v1) — `stated`
- Cite: `DS/2022-09-28_delivering-alpha-kernen-transcript.md` (NP summary): buy two years before the election, sell on it.
- Formula: none in v1; recorded to keep the extraction complete. Enabling requires re-registration.

## 9. Cross-source conflicts (summary)

| Topic | Versions | Resolution in spec |
|---|---|---|
| Horizon | 18m (Lost Tree); 18–24m (NBIM 2024, Actionable News); 12–18m (Sohn 2022 summary); 6–12m (Bloomberg 2015); 1–2y (NBIM 2023); 18m–3y (MS 2026); 2–4y trends (NBIM 2024) | 18–36m thesis horizon; 2–4y trend life |
| Lead of internals | 6–12m (Sohn 2022); momentum bottoms 12–18m (Feig 2009); trucking 6–8m (Sohn 2023, S) | Both stored; different objects |
| 2000 Treasury trade | 300% 10y-eq (Feig); 350% (Sohn 2022, NBIM 2024); "two and five-year" (Real Vision); Hyman −36% (Feig, NBIM) vs −25% (Real Vision) vs −35% (Sohn 2022) | Cap 300%; case target band 300–350% |
| Sterling 1992 | $7B fund, $1.5B → $5.5B proposed (Lost Tree); $1.5B → $5B, Soros ~$15B (Feig); $7.5B fund, ~$7.5B done (NBIM 2024); $10B (secondary) | Case target: starter ~20% NAV → ~100% NAV after catalyst |
| Inflation FF>CPI | Rule stated and expected to break (Sohn 2022 both summaries + fan transcript) | R-08 veto flag with caveat |
| Rates+oil+USD citation | Plan cites DA 2022; DA 2022 transcript lacks it | Cite Sohn 2022, NBIM 2024, Real Vision 2018 |
| Technicals | Very effective (NMW); cancelled by algos (2018); weaker (2022, 2023); ~20% (2026); still used for tops (NBIM 2024) | Veto kept; timing weight 0.2; exits via R-52 |
| Price confirmation | Required (2018, 2021); not needed for overwhelming conviction (2000) | Required for fat pitch; 2000 case scored with that exception noted |
| Liquidity measure | M2 vs IP (Feig); Fed vs Treasury net (ECNY 2020, S); QT net of TGA/SPR (DA 2022); global CB rate of change (2018) | Rule family R-02/R-03/R-04, era-labelled |
| Policy-error measure | Staff "data alone" (2003); Taylor variants (2005, 2015, 2016, 2017); "markets better than professors" (2024) | R-06 plus R-58 |
| Contrarian | Rejected (2009, 2026); bought Grexit fear (2015) | No positioning fade |

## 10. Gaps

### 10.1 Required primary sources: status

| Source (PLAN E.2 list) | Library status | Effect |
|---|---|---|
| Lost Tree 2015 | NP OCR transcript, full read | Adequate |
| Feig 2009 | NP fan transcript, full read; summary-level numbers for sizing caps | Adequate; caps quoted from note summary, not verbatim sentences (sentence-level quotes for 4:1, 100%/50%, 150–200%, 300% not reproduced in note) |
| ECNY 2020 | Secondary only (Felder verbatim excerpt; CNBC/Fortune quotes). Medium transcript 403; ECNY transcript not found by web search 2026-10-06 | R-04 formula rests on a secondary excerpt |
| Sohn 2022 | Now NP (A Letter a Day fan transcript, full read) plus two S summaries; video captions not retrieved | PLAN E.2 "lacks public transcript" is outdated |
| NBIM 2023 | NP (Tidalwave lightly edited transcript) plus S (Delphi) | Adequate |
| NBIM 2024 | NP (Podscripts ASR transcript, full read) | Adequate; ASR errors |
| Delivering Alpha 2014 | NP for interview; speech secondary only | Speech charts (100-year percentiles) unavailable |
| Delivering Alpha 2022 | NP (CNBC RealtimeTranscription) | Adequate |
| Morgan Stanley 2026 | NP (A Letter a Day transcript) plus S (Magica AI summary) | Adequate |
| New Market Wizards | Partial: one verbatim excerpt (HFA); Fed/liquidity and "jugular" lines are widely quoted but wording unverified; book not read | R-01 NMW wording unverified; Lost Tree used as primary cite |
| Real Vision 2018 | NP verbatim notes (Macro Ops); no transcript | Usable; not full extraction |
| 1988 Barron's | Paywalled teaser only | No rule content; case only from Feig 2009 retrospective |
| CNBC 2015-03, 2016-11 | NP transcripts | Adequate |

### 10.2 Unverifiable or unsupported claims (not encoded as stated)

| Claim | Status |
|---|---|
| "93% invested → net flat" (2019) | Exact 93% unverified; "over 90% invested … net flat" verified (DS/2019-06-07, NP) |
| Soros profitable on < 30% of trades | No support in any note; source dead |
| Sizing 70–80% attributed to Mauboussin | Source dead; figure is his own statement at Sohn 2022 |
| 2013 short yen | Not in library (only AUD short and long Japan equities sourced); unverified secondary mention of short JPY in Dec 2019 |
| Sohn 2005 Taylor-rule housing call | Referenced in 2016 notes; no recording located |
| Exact quantitative definitions (windows, thresholds) for every rule | Never given by the source; all windows interpreted |

### 10.3 Rules that cannot be fully operationalized with free data

| Rule | Limitation |
|---|---|
| R-11 fragility | No free history for B-rated share of issuance or covenant-lite share; Ritter annual only; SIFMA from 1996; "excess reached the banking system" test (DA 2014) has no defined series |
| R-12 cross-region | No free long Bundesbank/BoE balance-sheet series in plan; pre-1999 EA undefined; BoE weekly return history needs a new loader |
| R-13/R-25 company mosaics | "Bottom-up macro by listening to companies" (NBIM 2024, MS 2026) not mechanizable |
| R-16 leading industries | Industry examples only; mapping to French-49/ETFs is ours |
| R-22/R-50 political premises | Election outcomes, tariff announcements, peg decisions need manual event flags; reversal cases tagged `mechanizable: no` where the event itself is the signal |
| R-30/R-51 price vs news | No free consensus estimates; surprise = actual − prior (weak proxy) |
| R-31 crowding entry delay | COT history needs D-4; crypto/equity crowding not free |
| R-45 liquidity cap | Futures/FX volume history pre-IBKR coverage not free; FX spot volume not public |
| R-60 breadth thrust | Free NYSE A/D 1965-03 to 2020-02 (Unicorn archive) and S&P 500 member breadth from 2021-09-22; gap 2020-02-11 to 2021-09-21 filled by the industry-based fallback, flagged |
| R-04 pre-1993 | Daily net issuance unavailable; quarterly only |
| R-06 NROU vintages | Sparse ALFRED vintages; real-time gap approximated |
| T13 (peg stress) | Requires a manual peg/band flag; ERM 1992 not reproducible from free daily data beyond `DEXUSUK` |
