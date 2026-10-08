# Label audit: full corpus, 2026-10-06

Scope: all 68 case files in `cases\` (42 research, 26 holdout per `cases\HOLDOUT.yaml` v2), checked against their cited library notes and, where a note was ambiguous, the primary transcript. Method and rule as in `spec\label_review_2015-03.md`.

Blindness: `spec\scoring.md`, `spec\HOLDOUT.md`, `tools\make_holdout.py`, `src\fatpitch\cases\`, `results\` and gate/turning-point reports were not read. No turning points were computed and no engine or null was run. `cases\HOLDOUT.yaml` was read only for the holdout episode list.

## Rule applied

`regime_direction` is the monetary-policy stance as he read it at the information date, in {easing, neutral, tightening}. It is not his prescription and not the outcome. For a region-specific thesis the label follows the thesis region. Relative-policy theses are flagged in notes. `null` means no regime target. Process cases (truth_type `process`) carry the stated rule's output (PLAN.md case schema), so "as he read it" is applied loosely there and flagged where his read and the label could differ. Also checked: thesis/expression/action against the source, outcome or hindsight wording in notes, and date_basis.

## Primary texts fetched (2026-10-06, browser user agent)

| Source | Used for |
|---|---|
| Lost Tree gist OCR (timhwang21) | C01, C09, C13, C15, C26 |
| Feig transcript (aletteraday letter 300) | C12, C16, C17, C18, C19 |
| CNBC DA 2014 transcript | C14, C15, C25 |
| CNBC 2015-03-02 transcript | C27 |
| HedgeFundAlpha Ruhle transcript | X-02, C24 |
| Podscripts NBIM 2024 transcript | C42, C44, X-11 |
| CNBC 2021-05-11 article | C43 |
| CNBC 2023-11-01 transcript | C49 |

All other cases were judged on the library note alone (no ambiguity found that a transcript would resolve, or no transcript exists).

## Research split (42 cases)

Verdict `change` = file edited. Confidence refers to the final label.

| Case | Seed | Current label | Verdict | New label | Conf. | Source quote (≤2 sentences) | Region basis |
|---|---|---|---|---|---|---|---|
| 1981-12-31_long-bonds-volcker | C01 | tightening | change (notes) | tightening | high | "he had raised interest rates to 18 percent on the short end, and I could see that there is no way this man was going to let inflation go." | US. Notes said "too tight"; the source does not say that, so the notes were rewritten. |
| 1988-03-28_still-bearish-barrons-1988 | X-01 | null | ok | null | n/a | Teaser only: "Stan's bearish stance, why he believed that the market was due for a correction." | No policy read available. |
| 1988-12-30_dem-short-size-up | C03 | null | ok | null | n/a | "1988: $1B short DM position; Soros: 'You call that a position?' — doubled" (note). | n/a |
| 1989-11-30_dem-long-reunification | C04 | null | ok | null | n/a | "Deutsche mark long after the fall of the Berlin Wall (1989), reasoning through reunification's monetary implications." | n/a |
| 1992-08-31_sterling-starter | C05 | null | ok | null | n/a | "Sterling, Aug 1992: ... initial short 'a billion and a half.'" | n/a |
| 1992-09-16_sterling-size-up | C06 | null | ok | null | n/a | Size-up after "Schlesinger's FT editorial." | n/a |
| 1992-09-30_uk-concentric-circles | C07 | null | ok | null | n/a | "Afterward he bought gilts down two points ..., MATIF futures and UK equities." | n/a |
| 1999-12-31_internet-short-process | C09 | null | ok (date flagged) | null | n/a | "I put 200 million in them in about February and by mid-march the 200 million short I had lost $600 million." | Label fine. date_basis says the notes give only "1999", which is literally true of the notes, but both primary texts date the short (Lost Tree "about February"; Feig "March of '99"). By 1999-12-31 he was long tech. Proposed, not applied (see below). |
| 2000-01-31_tech-exit | C10 | null | ok | null | n/a | "January of 2000 I go into Soros's office and I say I'm selling all the tech stocks." | n/a |
| 2000-03-31_tech-reentry-process | C11 | null | ok | null | n/a | Re-entry after "13 new highs and 242 new lows" (Feig). | n/a |
| 2003-12-31_fed-too-loose-2003 | C13 | easing | ok | easing | high | "fed funds were one percent ... we had great conviction that the Federal Reserve was making a mistake with way too loose monetary policy." | US |
| 2005-12-30_riding-policy-2005 | C14 | null | ok | null | n/a | "I made a lot of money in '05 because I wanted to ride the overly aggressive policy." | US. An `easing` label would be supported; adding a target is left to the owner. |
| 2006-12-29_left-the-party-2006 | C15 | tightening | change (notes) | tightening | low | "'06 I stunk. I had made some money but I left the party." | US. No explicit 2006 policy read. The label rests on the dance-until-they-raise-rates framing of the same exchange. The old notes ("as tightening continued") asserted a cause the source does not state. They now record the basis. Owner may prefer `null`. |
| 2009-12-31_liquidity-long-2009 | C19 | easing | ok | easing | high | "more liquidity, ... buying $20-25bn in either treasuries or mortgages a week." | US |
| 2014-05-08_eur-short-entry-2014 | C24 | null | ok | null | n/a | "the flipping and divergence of monetary policies between the United States and Europe in May of 2014" (Ruhle). | Relative policy; no regime target. |
| 2014-07-24_eur-short-size-up-2014 | C24b | null | ok | null | n/a | "Euro short 2014: did a lot at 139, 'got a lot more brave' at 135." | n/a |
| 2014-07-16_still-dancing-2014 | C25 | easing | ok | easing | high | ZIRP at "once-in-a-century emergency levels"; "I am still dancing." | US |
| 2015-01-20_lost-tree-eur-short-2015 | C26 | easing | change (notes) | easing | high | "And now they're apparently caving in and they're going to print money." | EA (thesis EUR); US also easing. Label basis and relative-policy flag added. |
| 2015-03-02_long-japan-europe-2015 | C27 | neutral | **change (label)** | **easing** | high | "they have monetary policy that is just on the front end is very, very expansive. As you know they're doing QE." | JP/EA (thesis). Relative-policy. Notes per the 2015-03 review. |
| 2015-04-16_just-like-2004-ruhle-2015 | X-02 | easing | change (notes) | easing | high | "we were tapering, ending QE. They were going to start QE. They had gone to a negative deposit rate." | EA (thesis EUR/EA equities). Notes re-grounded on ECB; stale "C27 carries neutral" sentence removed. |
| 2015-11-04_sidelines-2015 | C28 | null | ok | null | n/a | "I could see myself getting really bearish. I can't see myself getting really bullish." | n/a |
| 2016-05-04_endgame-gold-2016 | C29 | easing | ok | easing | high | Fed policy is "the longest dovish deviation from historical norms I have seen in my career." | US |
| 2016-11-09_gold-exit-election | C30 | null | ok | null | n/a | "I sold all my gold the night of the election." | n/a |
| 2016-11-10_post-election-reversal | C31 | null | ok | null | n/a | "I'm short bonds globally." "I really like the dollar. Particularly against the euro." | n/a |
| 2021-06-15_short-front-end-2021 | C42 | easing | ok | easing | medium | "I had a massive short for me in two years ... there were 15 basis points" (spring 2021, money supply "growing 40%"). | US. Retrospective source. |
| 2021-05-11_raging-mania-reduce-2021 | C43 | easing | change (notes) | easing | high | "We've shifted a lot of our relative bets into commodities, into interest rates, into the dollar." | US (Fed "foot on the accelerator"). Leg directions are not stated outright. Long USD is inferred from "our other asset categories ... would be the cause of this stock market bubble popping." Notes now say so. Thesis kept. |
| 2022-03-07_hold-front-end-short-process-2022 | C44 | tightening | ok (flag) | tightening | low | NBIM 2024 gives only "I took most of it off at like 150 basis points." | Process case: the label reads as rule output (taper ending, hike imminent). No contemporaneous read. Notes call the premise "policy too loose", which on his-read terms would point to easing. Flagged for the owner. |
| 2021-02-26_short-usd-goldman-2021 | X-08 | null | ok | null | n/a | "Very short USD (per secondary aggregator; unverified)." | n/a |
| 2023-04-24_no-fat-pitch-2023 | C47 | tightening | ok | tightening | medium | "500bp of hikes in 12 months"; SVB facility "wiped out" months of QT. | US |
| 2023-10-24_massive-two-year-long-2023 | C48 | tightening | ok | tightening | medium | "'massive' leveraged long in 2-year Treasuries" on worry "that something would break." | US |
| 2023-11-01_debt-supply-short-2023 | C49 | tightening | change (notes) | tightening | high (label) / low (action) | "Jerome Powell normalizing interest rates ... We now have a hurdle rate for investment in this country." | US. The short is stated only as a 2023 YTD bet ("I made a lot of money this year betting on bonds going down"). The host describes a curve trade, and C48 has a long 2-year a week earlier. Notes now record this. Action `hold` is low confidence. |
| 2023-12-28_two-year-exit-2023 | C50 | easing | ok | easing | high | The Dec 2023 pivot "set financial conditions on fire again." | US |
| 2023-05-09_ai-long-hard-landing-sohn-2023 | X-09 | tightening | ok | tightening | medium | Hard landing after "the biggest broadest asset bubble ever" and 500bp of hikes. | US |
| 2024-01-31_argentina-invest-then-investigate | C51 | null | ok | null | n/a | "I follow the old Soros rule, invest and then investigate. I bought all of them." | n/a |
| 2024-03-28_nvidia-hold-process-2024 | C52 | null | ok | null | n/a | Cut Nvidia "in late March 2024 after the stock went from about $150 to $900." | n/a |
| 2024-09-18_short-treasuries-at-cut-2024 | C53 | easing | ok | easing | high | "We shorted bonds the day the Fed cut fifty because we thought it was a mistake." | US |
| 2024-05-07_japan-copper-long-2024 | X-10 | easing | ok | easing | medium | "Instead, they set financial conditions on fire again." | US read; the JP thesis has no BoJ read in the source. |
| 2024-11-06_inflation-second-wave-short-2024 | X-11 | easing | ok | easing | high | "to cut 50 basis points with credit spreads tight, gold at new highs, equities roaring." | US |
| 2026-01-30_short-usd-copper-2026 | C54 | easing | ok | easing | medium | "The Fed is unlikely to hike and will probably cut" into a strong economy (note). | US |
| 2026-02-17_duquesne-13f-q4-2025 | C55 | null | ok | null | n/a | 13F-derived; Bilanz has no direct quotes. | n/a (tilt test only) |
| 2026-09-10_ai-trim-fx-short-2026 | C56 | null | ok | null | n/a | Rates are "at best too low"; cuts "no longer necessary." | A US `easing` read is stated. The thesis regions (EA/GB) have no read, so `null` is defensible. Adding a target is left to the owner. |
| 2026-08-24_let-bond-market-speak-2026 | X-12 | easing | ok | easing | medium | Funding long-bond buybacks with bills or the TGA "amounts to Treasury-run QE." | US (Treasury-run yield suppression read as QE) |

### Research proposal not applied

| Case | Proposal | Reason not applied |
|---|---|---|
| 1999-12-31_internet-short-process (C09) | Re-date to the short's entry. Lost Tree gives "about February" 1999; Feig gives "March of '99" with a 13-day loss. A conservative asof is mid-March 1999 (the latest date the short certainly existed) or 1999-03-31. | The fix changes `asof` and therefore the case id/file name. The two primary texts conflict on the month, so the date choice needs an owner decision. |

## Holdout split (26 cases), not edited

| Case | Seed | Current label | Verdict | Proposed label | Conf. | Source quote (≤2 sentences) | Region basis |
|---|---|---|---|---|---|---|---|
| 2000-09-29_two-year-notes-2000 | C12 | tightening | ok | tightening | medium | "oil was screaming upward, interest rates were screaming upward ... So Fed Funds were 6.5%." | US |
| 2008-03-31_commodities-long-2008 | C16 | easing | ok | easing | high | "Bernanke and company, everybody were just going to put pedal the metal after Bear Stern." | US/global |
| 2008-06-30_commodities-exit-2008 | C17 | easing | ok (flag) | easing | low | "around May or June, those charts started to look quite dodgy, and we got out." | US. The source gives no read at the exit date; the label is carried from the March read. |
| 2008-12-31_brazil-rates-process | C18 | null | ok | null | n/a | "I just kept adding because I was, This is the stupidest thing I've ever seen." | n/a |
| 2012-04-30_aud-short-gold-2012 | C20 | easing | ok | easing | medium | Only way to trade is to "trade the monetary stimulus." | US (Twist in force) |
| 2013-05-08_japan-long-sohn-2013 | C21 | easing | ok | easing | high | Kuroda's QE "about three times the US program relative to equity market cap." | JP (thesis) |
| 2013-05-08_aud-short-sohn-2013 | C22 | easing | ok | easing | medium | "His bond buying is controlling the most important price in the US economy." | US/JP read. The AUD thesis is a commodity-cycle thesis with no RBA read. |
| 2013-09-19_no-taper-risk-long-2013 | C23 | easing | ok | easing | high | "This is fantastic for every rich person." (on the no-taper decision) | US |
| 2018-09-06_qt-reduce-2018 | C32 | tightening | ok | tightening | high | Global central bank buying "~$1T/yr going to zero (Fed $50B/month runoff, ECB €30B/month to zero) within 12 months." | US/global (rate of change) |
| 2018-12-17_pause-oped-2018 | C33 | tightening | **change (thesis)** | tightening | medium | Fed should pause its "double-barreled blitz of higher interest rates and tighter liquidity." | US. Label fine. The op-ed states no position, yet the case carries thesis rates/long/US and expression `rates_us`. Proposal: drop the thesis and expression (regime-only case, as X-06), or cite a source for the position. |
| 2017-12-12_taylor-gap-radicalism-2017 | X-03 | easing | ok | easing | medium | A Taylor-rule rate "about 4% in the US (actual 1%)"; "monetary radicalism." | US (level read, while the Fed was hiking) |
| 2018-06-29_global-qe-to-zero-bearish-2018 | X-04 | tightening | ok | tightening | high | Global QE "going to zero within 12 months." | US/global |
| 2019-01-30_fed-pivot-process-2019 | C34 | easing | ok (flag) | easing | low | "Three Fed cuts plus trade de-escalation pushed him to an about-face" (Dec 2019, retrospective). | Process case. On 2019-01-30 the Fed paused; it did not ease. The label is the rule's output and was not verified. |
| 2019-05-08_tariff-net-flat-2019 | C35 | null | ok | null | n/a | "I was over 90% invested. Fat and happy… and decided to go to net flat." | n/a |
| 2019-05-21_two-year-one-way-bet-2019 | C36 | null | ok | null | n/a | "Soros used to have this thing called the one-way bet." | n/a |
| 2019-06-07_fed-repivot-equities-2019 | C37a | easing | ok | easing | high | "I'm a liquidity guy." Re-adding after the Fed "repivot." | US |
| 2019-06-07_two-year-reduce-2019 | C37b | easing | ok | easing | high | At about 1.85% "that asymmetry was gone" (note). | US |
| 2019-12-18_constructive-turn-q4-2019 | X-05 | easing | ok | easing | high | "Three Fed cuts plus trade de-escalation pushed him to an about-face toward risk in Q4." | US |
| 2020-05-12_worst-risk-reward-2020 | C38 | null | ok | null | n/a | "biggest liquidity injection relative to history" but "liquidity shrinks as far as the eye can see." | Mixed read; `null` is appropriate. |
| 2020-06-08_constructive-reversal-2020 | C39 | easing | ok | easing | high | "I underestimated how many red lines, and how far, the Fed would go." | US |
| 2020-08-14_duquesne-13f-q2-2020 | C40 | null | ok | null | n/a | 13F-derived (EDGAR). | n/a |
| 2020-11-09_rotation-bitcoin-2020 | C41 | easing | ok | easing | medium | "Inflation likely to rise over 5–6 years due to Fed stimulus." | US |
| 2020-09-09_raging-mania-inflation-2020 | X-06 | easing | ok | easing | high | "The merging of the Fed and the Treasury ... sets a precedent that we've never seen." | US |
| 2020-10-30_relative-bets-commodities-short-bonds-2020 | X-07 | easing | ok | easing | medium | "We've shifted a lot of our relative bets into commodities, into interest rates, into the dollar." | US |
| 2022-06-10_waiting-for-fat-pitch-2022 | C45 | tightening | ok | tightening | high | "Once inflation gets above 5%, it's never come down unless Fed funds have gotten above the CPI." | US |
| 2022-09-28_sidestep-2022 | C46 | tightening | ok | tightening | high | "You have to slay the dragon." Expects QE to turn to QT once offsets run out. | US |

## Summary counts

| Item | Count |
|---|---|
| Cases checked | 68 (42 research, 26 holdout) |
| ok, research | 35 (including flagged C09 date, C44) |
| Changed in research | 7 files: 1 label change (C27 neutral → easing) and 6 notes-only (C01, C15, C26, X-02, C43, C49) |
| Research proposals not applied | 1 (C09 date/id) |
| ok, holdout | 25 (C17 and C34 flagged low confidence) |
| Proposed for holdout re-seal | 1 (C33 thesis/expression) |
| Optional label additions (owner decision) | 2 (C14 easing; C56 easing, US read) |

## Generator and byte checks

- The seven research files are regenerated from `tools\build_cases.py` (C01, C15, C26, C27, C43, C49) and `tools\build_cases_v2.py` (X-02). A regeneration of all 66 non-13F cases into a scratch directory matches `cases\` byte for byte, and the 26 holdout files are unchanged.
- Line endings: the case files are CRLF, not LF. They are written by `Path.write_text` on Windows, so the existing byte style is CRLF and was kept. `tools\build_cases_v2.py` is CRLF and `tools\build_cases.py` is LF; both were kept.
- `spec\corpus_manifest.txt` was regenerated (`python -m fatpitch.prereg manifest`). No `prereg\` registrations exist.
- The recorded counts in `cases\HOLDOUT.yaml` (`research_sha256`, research turning-point counts) describe the corpus before this audit and will be refreshed at the re-seal.
