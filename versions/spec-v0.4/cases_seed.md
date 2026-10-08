# Fat Pitch — Fidelity Case Seed List (input to E2; not scored)

Date: 2026-10-06. Status: candidate list. E2 converts accepted rows to `cases\<date>_<slug>.yaml`, applies PLAN E.3 schema, and registers the corpus hash before any engine run.

Rules for this list:
- `asof` = information date (ET close): trade date when documented, else statement date. `XX` = unknown day/month; E2 must resolve or widen the window.
- `truth_type`: `action` = target is his documented thesis/expression/action; `process` = target is the stated rule's output, and matching his action counts as a miss (PLAN E.3). Failed calls that followed the stated rules remain `action` (outcome is not a process violation).
- `mechanizable: no` = the decisive input is a discretionary or political event (premise flag) the engine does not generate.
- Targets record what he thought/did, never what the market did afterwards. Market-outcome columns from library notes are excluded; E2 must keep outcome fields out of any file the engine or calibrator reads.
- Reliability: NP = near-primary transcript; P = primary; S = secondary summary; R = retrospective statement made later (with the later source's own reliability).
- Leakage note: `spec\transition_table.yaml` was authored before these notes were read. This list was compiled after reading the notes; the table was not edited afterwards.

## Episodes

| episode_id | Era | Description |
|---|---|---|
| EP01-1981-BONDS | B | Volcker-era long Treasuries |
| EP02-1988-BEAR | B | Post-crash bearishness 1988 |
| EP03-1988-89-DEM | B | Deutsche mark trades |
| EP04-1992-ERM | B | Sterling / ERM |
| EP05-1997-ASIA | B | Rupiah loss |
| EP06-1999-2000-TECH | B | Internet shorts, tech exit and re-entry |
| EP07-2000-RATES | B | Q4 2000 Treasury long (rates+oil+USD) |
| EP08-2003-06-LOOSE | A | Fed too loose, housing |
| EP09-2008-CRISIS | A | Commodities long/exit, Brazil rates |
| EP10-2009-LIQ | A | Liquidity vs weak economy |
| EP11-2012-13-QE | A | Trade the stimulus: AUD short, Japan long |
| EP12-2014-15-DIVERGE | A | Policy divergence: EUR short, Japan/Europe long, fragility alerts |
| EP13-2016-REGIME | A | Sohn 2016 bearish/gold → election reversal |
| EP14-2018-QT | A | QT/liquidity drain, Dec 2018 pause call |
| EP15-2019-TARIFF | A | Tariff de-risk, 2y one-way bet, Fed pivot |
| EP16-2020-COVID | A | ECNY bearish → humbled → rotation |
| EP17-2021-MANIA | A | Mania, short front end, de-risk |
| EP18-2022-INFL | A | Inflation bear, hard-landing view, waiting |
| EP19-2023-RATES | A | No fat pitch, 2y long, debt-supply short |
| EP20-2024-CUT | A | Short UST at cut; Nvidia trims; Argentina |
| EP21-2025-26-ROTATE | A | Copper/short USD, AI trim, broadening |

## Cases

| id | asof | episode_id | era | truth_type | mech | reliability | regime dir | thesis (class/dir/region) | expression | action | size (documented) | citation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | 1981-XX-XX | EP01 | B | action | yes | NP-R | tightening (policy too tight) | rates/long/US | 30y UST | enter | 50% NAV (would use ~150% with Soros mindset) | RS/2015-01-18_lost-tree-club-speech.md |
| C02 | 1988-03-28 | EP02 | B | process | yes | S (teaser) + NP-R | computed by R-02 | rule output (R-01/R-02) | — | not short if liquidity impulse positive | — | DS/1988-03-28_barrons-still-bearish.md; DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C03 | 1988-XX-XX | EP03 | B | action | no | S | unknown | fx/short/DEM | DEM | size_up (doubled after Soros) | $1B → ~$2B | RS/1992-XX-XX_new-market-wizards-chapter.md (CardPlayer) |
| C04 | 1989-11-XX | EP03 | B | action | no | P (wording unverified) | unknown | fx/long/DEM (reunification) | DEM | enter | — | DS/1992-XX-XX_new-market-wizards-schwager-chapter.md |
| C05 | 1992-08-XX | EP04 | B | action | no | NP-R | n/a (ERM peg premise) | fx/short/GBP | GBP | enter (starter) | $1.5B of ~$7–7.5B (~20–25% NAV) | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md; RS/2015-01-18_lost-tree-club-speech.md; RS/2024-11-06_nbim-in-good-company-podcast.md |
| C06 | 1992-09-XX | EP04 | B | action | no | NP-R | n/a | fx/short/GBP | GBP | size_up after catalyst (Schlesinger comments) | ~100% NAV ($5–7.5B by telling) | same as C05 |
| C07 | 1992-09-XX | EP04 | B | action | partial | NP-R | n/a | rates/long/UK; equity/long/UK | gilts, MATIF, UK equities | enter (concentric circles) | — | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C08 | 1997-XX-XX | EP05 | B | process | yes | NP-R | unknown | fx/short/IDR | IDR | target: size ≤ liquidity cap (R-45); his action breached it (froze due to size) | lost >$1B | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C09 | 1999-XX-XX | EP06 | B | process | yes | NP-R | computed | rule output: no short against uptrend (R-29/R-62) | internet equities | target: no short; his action shorted | $200M short, lost $600–800M | RS/2015-01-18_lost-tree-club-speech.md; DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C10 | 2000-01-XX | EP06 | B | action | yes | NP-R | computed | equity/exit/US tech | tech equities | exit | sold ~$6B | RS/2015-01-18_lost-tree-club-speech.md |
| C11 | 2000-03-XX | EP06 | B | process | yes | NP-R + S | computed | rule output: no re-entry (internals weak; chart veto) | tech equities | target: no entry; his action bought near top | ~$6B, lost ~$3B | RS/2015-01-18_lost-tree-club-speech.md; DS/2000-04-28_soros-quantum-exit-overplayed-hand.md |
| C12 | 2000-09-XX | EP07 | B | action | yes | NP-R | tightening (FF 6.5%); R-10 true | rates/long/US | 2y notes (10y-equivalent sizing) | enter | 300% (Feig) / 350% (Sohn 2022, NBIM 2024) 10y-eq | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md; DS/2022-06-XX_sohn-2022-john-collison.md; RS/2024-11-06_nbim-in-good-company-podcast.md |
| C13 | 2003-12-XX | EP08 | A | process | yes | NP-R | easing; policy error too_loose | rule output: too_loose (R-06) | — | regime/policy-error agreement only | — | RS/2015-01-18_lost-tree-club-speech.md |
| C14 | 2005-XX-XX | EP08 | A | action | yes | NP-R | easing → tightening | equity/long/US (riding policy) | US equities | hold long | — | DS/2014-07-16_delivering-alpha-kernen.md |
| C15 | 2006-XX-XX | EP08 | A | action | yes | NP-R | tightening | equity/reduce/US | US equities | exit ("left the party") | — | DS/2014-07-16_delivering-alpha-kernen.md |
| C16 | 2008-03-XX | EP09 | A | action | yes | NP-R | easing (post-Bear Stearns liquidity) | commodity/long/global | commodities | enter | — | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C17 | 2008-05-XX | EP09 | A | action | yes | NP-R | easing | commodity/exit | commodities | exit (charts "dodgy") | — | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C18 | 2008-XX-XX | EP09 | A | process | yes | NP-R | unknown | rule output: chart veto (R-29) blocks add | Brazil local rates | target: no add; his action added against chart ("1 in 100"); also cut $200–300M at the low | — | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C19 | 2009-10-XX | EP10 | A | action | yes | NP | easing; R-02 positive | equity/long/US | US equities | hold long ("stocks go up until a signal appears") | fund ~+10% YTD (context only) | DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C20 | 2012-04-XX | EP11 | A | action | yes | S | easing (Twist) | fx/short/AUD; fx/long/USD; commodity/long/gold (options) | AUD, USD, gold options | hold | — | DS/2012-04-XX_grants-spring-conference-jim-grant.md |
| C21 | 2013-05-08 | EP11 | A | action | yes | S | easing (US); JP QE starting | equity/long/JP (relative) | Japan real estate, banks | enter/hold | — | DS/2013-05-08_sohn-commodities-conundrum.md |
| C22 | 2013-05-08 | EP11 | A | action | yes | S | easing | fx/short/AUD; commodity producers/short | AUD; producers vs consumers | hold | — | DS/2013-05-08_sohn-commodities-conundrum.md |
| C23 | 2013-09-19 | EP11 | A | action | yes | S | easing (no taper) | equity/long/US | risk assets | hold long (implied) | — | DS/2013-09-19_cnbc-squawk-box-fed-wealth-transfer.md |
| C24 | 2014-05-XX | EP12 | A | action | yes | NP (notes) | ECB easing vs Fed taper | fx/short/EUR | EUR | enter at ~1.39, size_up at ~1.35 | — | RS/2018-09-06_sokoloff-real-vision-interview.md; DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md |
| C25 | 2014-07-16 | EP12 | A | action | yes | NP | easing; fragility high | equity/long/US with fragility alert | US equities | hold ("still dancing"), liquid book | — | DS/2014-07-16_delivering-alpha-kernen.md |
| C26 | 2015-01-18 | EP12 | A | action | yes | NP | easing; fragility high | equity/not net short; fx/short/EUR | EUR | hold | — | RS/2015-01-18_lost-tree-club-speech.md |
| C27 | 2015-03-02 | EP12 | A | action | yes | NP | US neutral/tightening bias; EA, JP QE starting | equity/long/JP,EA (FX-hedged) | Nikkei/European cyclicals hedged | hold; most net long ex-US | — | DS/2015-03-02_cnbc-closing-bell-kelly-evans.md |
| C28 | 2015-11-04 | EP12 | A | action | yes | S | tightening pending | equity/flat (bearish skew); fx/short/EUR | EUR | flat equities ("sidelines") | — | DS/2015-11-04_nyt-dealbook-conference-sorkin.md |
| C29 | 2016-05-04 | EP13 | A | action | yes | S | easing; policy too_loose | equity/short-bias/US; commodity/long/gold | gold | enter/hold gold (largest currency position) | — | DS/2016-05-04_sohn-the-endgame.md |
| C30 | 2016-11-09 | EP13 | A | action | no | NP | regime change (fiscal) | commodity/exit/gold | gold | exit (premise break, election night) | all gold | DS/2016-11-10_cnbc-squawk-box-post-election-sold-gold.md |
| C31 | 2016-11-10 | EP13 | A | action | no | NP | growth up, rates up | rates/short/global; fx/long/USD vs EUR; equity/long/value+materials | UST, Bunds, gilts, BTPs; EURUSD | enter | "large bet" | DS/2016-11-10_cnbc-squawk-box-post-election-sold-gold.md |
| C32 | 2018-09-06 | EP14 | A | action | yes | NP (notes) | tightening (QT + hikes; global QE → 0) | equity/reduce/US | US equities | reduce | — | RS/2018-09-06_sokoloff-real-vision-interview.md; DS/2018-10-09_grants-fall-conference-jim-grant.md |
| C33 | 2018-12-16 | EP14 | A | action | yes | S | tightening; policy too_tight; internals down | rates/long/US; equity/reduce | — | policy-error view (pause) | — | DS/2018-12-16_wsj-oped-warsh-fed-tightening-not-now.md |
| C34 | 2019-01-30 | EP15 | A | process | yes | S-R | easing (Fed pause/pivot) | rule output: T01 long equities | US equities | target: long; his action timid (self-assessed "couldn't have been more wrong") | — | DS/2019-12-18_bloomberg-schatzker-couldnt-have-been-more-wrong.md |
| C35 | 2019-05-06 | EP15 | A | action | no | NP | event: tariff tweet | equity/flat (hedged) | index hedges | exit to net flat | from >90% invested to net flat | DS/2019-06-07_cnbc-squawk-box-one-way-bet.md |
| C36 | 2019-05-XX | EP15 | A | action | yes | NP | cuts priced vs FF | rates/long/US front end | 2y UST ~2.30% | enter (one-way bet) | — | DS/2019-06-07_cnbc-squawk-box-one-way-bet.md |
| C37 | 2019-06-07 | EP15 | A | action | yes | NP | easing (Fed repivot) | equity/long/US; rates/reduce (asymmetry gone at 1.85%) | US equities; 2y | size_up equities; reduce 2y | — | DS/2019-06-07_cnbc-squawk-box-one-way-bet.md |
| C38 | 2020-05-12 | EP16 | A | action | yes | S | R-04 turning negative | equity/short-bias/US | US equities | reduce (worst risk/reward) | — | RS/2020-05-12_economic-club-of-new-york.md; DS/2020-05-12_econclub-ny-webcast.md |
| C39 | 2020-06-08 | EP16 | A | action | yes | S | easing; breadth thrust | equity/long/US cyclicals | reopening names | reverse (constructive) | — | DS/2020-06-08_cnbc-squawk-box-humbled-underestimated-fed.md |
| C40 | 2020-08-14 | EP16 | A | action | yes | S (13F) | easing | equity tilt: −mega-cap tech, +cyclicals | NFLX, AMZN, FB, GOOGL cut; JPM, SBUX, BKNG added | QoQ tilt change | 13F weights | RS/2020-08-18_gurufocus-q2-2020-13f.md |
| C41 | 2020-11-09 | EP16 | A | action | yes | S | easing | equity/long/US value (not net short); commodity/long/gold, miners; crypto/long/BTC | value, miners, gold, BTC | hold/enter | gold position many times BTC | RS/2020-11-09_cnbc-the-exchange-rotation.md |
| C42 | 2021-04-XX | EP17 | A | action | yes | NP-R | easing; policy too_loose; inflation rising | rates/short/US front end | 2y at ~15bp | enter | — | RS/2024-11-06_nbim-in-good-company-podcast.md |
| C43 | 2021-05-11 | EP17 | A | action | yes | S + NP | easing; too_loose; fragility high | equity/reduce/US; rates/short; commodity/long; fx/long/USD | relative bets | reduce equities | "far less than four or five months earlier" | DS/2021-05-11_cnbc-squawk-box-raging-mania-dollar.md; DS/2021-05-11_hustle-mfm-trung-phan.md |
| C44 | 2022-03-XX | EP17 | A | process | yes | NP-R | tightening begins; R-08 true | rule output: hold short front end (premise intact, R-49) | 2y | target: hold; his action took most off at ~150bp (self-described regret) | — | RS/2024-11-06_nbim-in-good-company-podcast.md |
| C45 | 2022-06-XX | EP18 | A | action | yes | NP | tightening; R-07/R-08/R-09 true; R-10 true | equity/flat-to-short; commodity/long/oil, copper; fx: expect short USD | — | low conviction ("waiting for a fat pitch") | small | DS/2022-06-XX_sohn-2022-john-collison.md |
| C46 | 2022-09-28 | EP18 | A | action | yes | NP | tightening; QT | equity/sidestep (flat) | — | flat ("don't short, just sidestep") | — | DS/2022-09-28_delivering-alpha-kernen-transcript.md |
| C47 | 2023-04-24 | EP19 | A | action | yes | NP | tightening; cuts priced (2y < FF) | fx/short/USD; commodity/long/gold; rates/short/JGB | USD, gold, JGBs | no fat pitch; net equity ~−3% | P&L ≤ 30–40bp/day | DS/2023-04-24_nbim-annual-investment-conference.md |
| C48 | 2023-10-24 | EP19 | A | action | yes | S + NP-R | tightening peak; fragility | rates/long/US front end | 2y at ~5.10–5.15% | enter (massive, leveraged) | "massive leveraged" | DS/2023-10-24_robin-hood-paul-tudor-jones.md; DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md |
| C49 | 2023-11-01 | EP19 | A | action | yes | NP | debt supply (R-63) | rates/short/US long end (YTD) | UST | hold (stated profitable YTD) | — | DS/2023-11-01_cnbc-squawk-box-yellen-debt-drunken-sailors.md |
| C50 | 2023-12-XX | EP19 | A | action | yes | NP-R | easing pivot; FCI loose (R-58) | rates/exit/US front end | 2y at ~4.30% | exit (premise: tight FCI broke) | — | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md |
| C51 | 2024-01-XX | EP20 | A | action | no | NP-R | n/a (political catalyst) | equity/long/AR | 5 most liquid Argentine ADRs | enter (invest then investigate) | — | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md |
| C52 | 2024-03-XX | EP20 | A | process | yes | NP-R | easing expectations | rule output: no exit while premises intact (R-49/R-52) | NVDA | target: hold or partial on technical top; his action sold (self-described mistake) | from ~$150 to ~$800–950 | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md; DS/2024-10-16_bloomberg-tv-sonali-basak.md; DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md |
| C53 | 2024-09-18 | EP20 | A | action | yes | NP | easing into loose FCI; 10y < NGDP (R-56) | rates/short/US | 10y-equivalent UST | enter on day of 50bp cut | ~25% NAV 10y-eq | DS/2024-10-16_bloomberg-tv-sonali-basak.md; RS/2024-11-06_nbim-in-good-company-podcast.md |
| C54 | 2026-01-30 | EP21 | A | action | yes | NP | easing bias; fiscal stimulus | fx/short/USD; commodity/long/copper; rates/short (hedge); equity/long/JP,KR | DXY, copper front month, UST, Japan/Korea | hold | — | DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md |
| C55 | 2026-02-14 | EP21 | A | action | yes | S (13F) | easing bias | equity tilt: +financials, +equal-weight, +Brazil, +airlines; −tech, −health | XLF, RSP, EWZ, UAL/AAL/DAL | QoQ tilt change (Q4 2025 13F) | 13F weights | RS/2026-02-26_bilanz-q4-2025-rotation.md |
| C56 | 2026-09-10 | EP21 | A | action | yes | S | rates too low (too_loose); Fed hike pending | equity/reduce/AI; fx/short/EUR, GBP | AI holdings; EUR, GBP | reduce AI to ~20% of level 6 months earlier | smaller FX size than historically | DS/2026-09-10_piper-sandler-closed-door-event.md |

## Counts

| Dimension | Count |
|---|---|
| Cases | 56 |
| Episodes | 21 (7 era B, 14 era A) |
| Era A / B | 44 / 12 |
| truth_type action / process | 47 / 9 |
| mechanizable yes / partial / no | 47 / 1 / 8 |
| Reliability with NP or P component | 41; S-only 15 |
| Flat/cash/low-conviction periods | C28, C35, C45, C46, C47 |
| Mistakes / failed calls | C02, C08, C09, C11, C18 (process); C29 (2016 bearish, reversed C30); C34; C38 (ECNY 2020, reversed C39/C41); C44; C52 |

## Open items for E2

1. Resolve `XX` dates (C01, C03–C18, C24, C42, C44, C50–C52); where only a month is known, set asof = last business day of the month and widen the window to ±1 month, flagged.
2. 13F cases (C40, C55): use `filed` date; derive QoQ tilts from SEC data sets (D-3), not from the article.
3. Sterling size target: band 20–25% NAV starter → ~100% NAV after catalyst; do not encode $10B secondary figure.
4. C12 size target: band 300–350% 10y-equivalent; rule cap 300% (R-44).
5. Not seeded (no library source or no decision content): 2013 short yen; 1994 bond rout; 1997 baht; 2010 fund closure; 2017 ("worst relative year", no dated action).
6. Era-B cases decided on non-liquidity drivers (C01 real rates; C05–C07 ERM) score on the stage that applies (PLAN E.4a).

## Expansion v2 (2026-10-06; owner decision: expand before any scoring, then re-seal)

Mined from every note in `library\reference_sources\` and `library\discovered_sources\`; built by `tools\build_cases_v2.py` (rows, `date_basis`, rejected candidates with reasons). Holdout re-sealed afterwards (`spec\HOLDOUT.md` Re-seal log). Outcome columns of the notes were not transcribed.

| seed | asof | episode_id | era | reliability | regime dir | thesis (class/dir/region) | action | citation |
|---|---|---|---|---|---|---|---|---|
| X-01 | 1988-03-28 | EP02 | B | S | — | equity/short/US | — | DS/1988-03-28_barrons-still-bearish.md |
| X-02 | 2015-04-16 | EP12 | A | NP | easing | fx/short/EUR; equity/long/JP, EA; commodity/long/OIL | hold | DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md |
| X-03 | 2017-12-12 | EP14 | A | NP | easing | equity/long/US | hold | DS/2017-12-12_cnbc-closing-bell-kelly-evans.md |
| X-04 | 2018-06-29 | EP14 | A | NP-R | tightening | equity/short/US | — | RS/2018-09-06_sokoloff-real-vision-interview.md |
| X-05 | 2019-12-18 | EP15 | A | S | easing | commodity/long/COPPER; equity/long/US, JP | size_up | DS/2019-12-18_bloomberg-schatzker-couldnt-have-been-more-wrong.md |
| X-06 | 2020-09-09 | EP16 | A | S | easing | — | — | DS/2020-09-09_cnbc-squawk-box-absolute-raging-mania.md |
| X-07 | 2020-10-30 | EP16 | A | S-R | easing | commodity/long; rates/short/US | enter | DS/2021-05-11_cnbc-squawk-box-raging-mania-dollar.md |
| X-08 | 2021-02-26 | EP17 | A | S | — | fx/short/USD | — | DS/2021-02-XX_goldman-sachs-interview.md |
| X-09 | 2023-05-09 | EP19 | A | S | tightening | equity/long/US; commodity/long/GOLD | hold | DS/2023-05-09_sohn-2023-kiril-sokoloff.md |
| X-10 | 2024-05-07 | EP20 | A | NP | easing | equity/long/JP; commodity/long/COPPER | hold | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md |
| X-11 | 2024-11-06 | EP20 | A | NP | easing | rates/short/US (25% NAV 10y-eq) | hold | RS/2024-11-06_nbim-in-good-company-podcast.md |
| X-12 | 2026-08-24 | EP21 | A | S | easing | rates/short/US | — | DS/2026-08-24_wsj-oped-let-the-bond-market-speak.md |

EP02-1988-BEAR (listed above) now holds X-01; EP14-2018-QT is taken back to Dec 2017 (X-03). Corpus after v2: 68 cases, 20 episodes.

## Corrections v0.2 (2026-10-06; owner decisions; `spec\corpus_v0.2_changes.md`)

Rows above are kept as the original seed. The built cases differ as follows (generators `tools\build_cases.py`, `tools\build_cases_v2.py`).

| seed | asof | episode_id | era | reliability | regime dir | thesis (class/dir/region) | action | citation |
|---|---|---|---|---|---|---|---|---|
| C09 | 1999-02-26 (was 1999-12-31) | EP06 | B | NP-R | — | — (process) | flat | RS/2015-01-18_lost-tree-club-speech.md; DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md |
| C14 | 2005-12-30 | EP08 | A | NP-R | easing (was null) | equity/long/US | hold | DS/2014-07-16_delivering-alpha-kernen.md; DS/2016-05-04_sohn-the-endgame-archived-transcript.md; RS/2015-01-18_lost-tree-club-speech.md |
| C15 | 2006-12-29 | EP08 | A | NP-R | — (was tightening) | — | exit | DS/2014-07-16_delivering-alpha-kernen.md; RS/2015-01-18_lost-tree-club-speech.md |
| C29 | 2016-05-04 | EP13 | A | P (was S) | easing | commodity/long/GOLD; equity/short/US | hold | DS/2016-05-04_sohn-the-endgame-archived-transcript.md; DS/2016-05-04_sohn-the-endgame.md |
| C33 | 2018-12-17 | EP14 | A | S | tightening | — (rates/long/US dropped) | — | DS/2018-12-16_wsj-oped-warsh-fed-tightening-not-now.md |
| C44 | 2022-03-07 | EP17 | A | NP-R | easing (was tightening) | rates/short/US (process) | hold | RS/2024-11-06_nbim-in-good-company-podcast.md; DS/2022-06-XX_sohn-2022-john-collison.md |
| C56 | 2026-09-10 | EP21 | A | S | easing (was null) | fx/short/EUR, GBP | reduce | DS/2026-09-10_piper-sandler-closed-door-event.md |
| X-08 | 2021-02-05 (was 2021-02-26) | EP17 | A | NP (was S) | easing (was null) | fx/short/USD; rates/short/US; commodity/long | hold | DS/2021-01-XX_talks-at-gs-great-investors-pasquariello.md; DS/2021-02-XX_goldman-sachs-interview.md |
| X-13 | 2014-06-19 | EP12 | A | P | easing | — | — | DS/2014-06-19_wsj-oped-warsh-asset-rich-income-poor.md |
| X-14 | 2023-05-01 | EP19 | A | P | tightening | — | — | DS/2023-05-01_tie-spring-2023-coming-fiscal-horror-show.md; DS/2023-05-01_usc-marshall-keynote.md |
| X-15 | 2024-10-02 | EP20 | A | S | easing | commodity/long/GOLD; equity/long/AR, JP | hold | DS/2024-10-01_grants-fall-conference-2024.md |
| X-16 | 2018-12-18 | EP14 | A | S | tightening | rates/long/US (2s, 5s, 10s); expression also equity_us_financials (short financials) | hold | DS/2018-12-18_bloomberg-tv-erik-schatzker.md |

Corpus after v0.2: 71 cases, 20 episodes (holdout re-sealed, version 3). X-16 added 2026-10-07 (owner decision): 72 cases, 20 episodes (holdout re-sealed, version 4).

## Additions v0.3 (2026-10-07; owner decision, option A; `spec\corpus_v0.3_changes.md`)

Six tightening reads and two easing reads from `library\research\tightening_sources.md`, built by `tools\build_cases_v2.py`. NMW = `DS/1992-XX-XX_new-market-wizards-full-chapter-text.md` (Schwager interview, December 1991).

New episodes (numbered in order of creation, not chronologically):

| episode_id | Era | Description |
|---|---|---|
| EP22-1987-CRASH | B | June 1987 switch to net short on Fed tightening |
| EP23-1989-NIKKEI | B | Late-1989 Nikkei short on Bank of Japan tightening |
| EP24-1991-EASE | B | December 1991: Fed "in a state of panic", long-bond exit |

| seed | asof | episode_id | era | reliability | regime dir | thesis (class/dir/region) | action | citation |
|---|---|---|---|---|---|---|---|---|
| X-17 | 1981-06-30 | EP01 | B | P-R | tightening (implied: rates at 19%) | equity/short/US | reduce (to 50% cash) | NMW |
| X-18 | 1987-06-30 | EP22 | B | P-R | tightening | equity/short/US | reverse | NMW |
| X-19 | 1989-12-29 | EP23 | B | P-R | — (BoJ tightening in notes; regime target is US-only) | equity/short/JP | enter | NMW |
| X-20 | 1991-12-31 | EP24 | B | P | easing | — (expression rates_us) | exit | NMW |
| X-21 | 2018-05-04 | EP14 | A | P | easing | — | — | DS/2018-05-03_manhattan-institute-hamilton-award-speech.md |
| X-22 | 2018-10-09 | EP14 | A | S | tightening | — | — | DS/2018-10-09_grants-fall-conference-jim-grant.md |
| X-23 | 2018-11-23 | EP14 | A | S | tightening | — | — | DS/2018-11-21_wsj-interview-risky-to-be-tightening.md |
| X-24 | 2023-06-07 | EP19 | A | S | tightening | equity/long/US (AI) | hold | DS/2023-06-07_bloomberg-invest-sonali-basak.md |

Corpus after v0.3: 80 cases, 23 episodes (holdout re-sealed, version 5).
