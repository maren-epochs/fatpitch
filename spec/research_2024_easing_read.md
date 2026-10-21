# Research: the 2024 pre-cut easing read (EP20-2024-CUT)

Date: 2026-10-07. Scope: why the library's 2024 reads of the US policy regime are easing before the first cut (2024-09-18) while the faithful-track engine reads tightening from January to August 2024. Read-only research. No case file, `results\versions\` run directory or `spec\fed_cycles.yaml` was opened. From `results\versions\LEADERBOARD.md`, only the EP20 row was read (era A, 4 cases, LOEO climatology 0.059, c6fefbd 0.450, 8bb7d11 0.723, null_fed_direction 0.229). The EP20 case dates are not known to this note.

## 1. Library evidence, 2023-10 to 2024-12, and later retrospectives

Reliability codes follow the library index (`primary`, `near-primary (transcript)`, `secondary summary`). "Verbatim" means the quote is a direct quotation in the cited note.

| Date | File | Reliability | Verbatim | Quote (short) | Drivers named | Read of policy |
|---|---|---|---|---|---|---|
| 2023-10-24 | DS/2023-10-24_robin-hood-paul-tudor-jones.md | secondary summary (Fortune direct quotes, attendee notes) | Y (fiscal quotes only) | "When the debt rolls over by 2033, interest expense is going to be 4.5% of GDP if rates are where they are now." | Fiscal deficits and Treasury term-out; "something will break"; massive leveraged 2-year long | Tightening / fragility (not easing) |
| 2023-11-01 | DS/2023-11-01_cnbc-squawk-box-yellen-debt-drunken-sailors.md | near-primary (transcript) | Y | "I made a lot of money this year betting on bonds going down because of the debt and had nothing do with the economy." / "We now have a hurdle rate for investment in this country." | Fiscal supply (term premium); Powell's normalisation restores a hurdle rate | Tightening (restrictive rates) |
| 2024-05-07 (covers Dec 2023 to May 2024) | DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md | near-primary (transcript) | Y | "I feel like they fumbled on the five-yard line…" / "Instead, they set financial conditions on fire again." / "Once financial conditions took off, it became very clear that this thing could go either way. So I exited the position." | (1) December 2023 dovish pivot and forward guidance, asymmetric "we expect to cut" bias; (2) financial conditions loosening (equities, credit, bitcoin); (3) six-month annualised inflation turning up; (4) 7% deficit at full employment, Fed "the great enabler" through the QT taper and a $7T balance-sheet floor (paraphrase in the note, not verbatim) | Easing bias in guidance; stance too loose. The only contemporaneous pre-cut 2024 statement in the library |
| 2024-10-01/02 | DS/2024-10-01_grants-fall-conference-2024.md | secondary summary | N (HFA paraphrase) | "a reckless monetary gamble with overtly reflationary policies" | The September 50bp cut; reflation | Easing, too loose (post-cut) |
| 2024-10-06 | RS/2024-10-06_actionable-news-horizon-quote.md | secondary summary | Y (older undated interview) | "imagine the world the way it's going to be in 18 to 24 months" | Horizon only | No policy read |
| 2024-10-16 | DS/2024-10-16_bloomberg-tv-sonali-basak.md | near-primary (ASR transcript) | Y | "Equities at record high, gold at a record high, GDP above trend, credit tight… we don't see any restriction whatsoever." / "markets are better predictors than professors" / "We shorted bonds the day the Fed cut fifty because we thought it was a mistake." | Financial conditions read from asset prices and credit; forward-guidance trap (2021 precedent); 1970s second-wave analogue; 10-year vs nominal GDP | Easing, too loose. Post-cut, but the "no restriction" judgement covers the pre-cut stance |
| 2024-11-05/06 | RS/2024-11-06_nbim-in-good-company-podcast.md (DS stub 2024-11-06_nbim-in-good-company-tangen.md) | near-primary (transcript) | Y | "I've switched to being more worried about inflation going forward than the economy itself." Summary: financial conditions "loose despite the hiking cycle" | Inflation second wave; the Fed declared victory early; financial conditions; 7% deficit; narrowing leadership (equity internals, "yellow light") | Easing, too loose (post-cut) |
| 2025-01-20 | DS/2025-01-20_cnbc-inauguration-animal-spirits.md | secondary summary | partial | "animal spirits" | Political regime | No 2024 policy read |
| 2026 (01-30, 02-27, 08-24, 09-10) | DS/2026-* and RS/2026-* | mixed | n/a | Piper Sandler 2026-09-10: calling policy restrictive is "absurd" (secondary) | Same restrictiveness-from-markets principle, applied to 2026 | No retrospective on 2024 located |

The library research notes agree. `library\research\tightening_sources.md` dates his tightening read to late 2023 ("financial conditions tightening before the Dec 2023 pivot"; 2-year long exited after the pivot) and lists 2024 among the periods in which he calls policy "too loose". `library\research\turning_point_sources.md` lists Grant's 2024-10-01 as an easing read.

What drives the read, by driver:

| Driver | Library support for 2024 | Strength |
|---|---|---|
| Fed pivot / December 2023 dot plot / forward guidance | 2024-05-07 (NP, verbatim). The "pivot" is the December 2023 guidance change. The 2-year exit at about 4.30% puts his flip in mid-to-late December 2023 | Strong. The only contemporaneous driver |
| Financial conditions (generic; NFCI never named) | 2024-05-07, 2024-10-16, 2024-11-05 (NP, verbatim) | Strong as a stance judgement (restrictiveness), not as policy direction |
| Inflation | 2024-05-07 (six-month annualised turning up), 2024-11-05 (second wave) | Medium. It argues that easing is a mistake, not that policy is easing |
| Fiscal deficits / issuance | 2023-10-24, 2023-11-01, 2024-05-07, 2024-11-05 | Strong for duration (bond short). No link to an easing read |
| Liquidity (TGA/RRP drawdown) | None in 2023-2024. The nearest is DS/2022-09-28 (TGA drawdown accounting) | Gap |
| QT taper | 2024-05-07 paraphrase only ("great enabler") | Weak. Not verbatim |
| Equity internals | 2024-10-16 (election forecasting), 2024-11-05 (narrowing leadership) | Not a policy-direction driver |

Gap: no pre-cut 2024 statement says "the Fed is easing". The one contemporaneous source (2024-05-07) describes a dovish guidance bias plus loose markets, and in the same interview he says the Fed should keep the option to hike. The label "easing" is therefore an interpretation of guidance plus stance, made by whoever set the case labels.

## 2. Drivers mapped to process.md rules

| Driver | Rule | In the R-66 direction vote today? | Reason (process.md R-66 "Excluded from the mapping" and rule text) |
|---|---|---|---|
| Last policy-rate move; balance-sheet programme | R-14 | Yes (family 1) | Defines `policy_direction`. Rate-primary: last move = 2023-07-26 hike, so tightening until the cut. The slowed runoff from June 2024 is still RUNOFF, so tightening |
| Net liquidity incl. RRP/TGA drawdown | R-03 | Yes (family 2, with R-04, era A) | Sign of the sum of R-03 and R-04 confirmed signs |
| Fed purchases − net issuance | R-04 | Yes (family 2) | Same as above |
| Policy error (stance vs Taylor) | R-06 | No | Level, not direction (R-21). Enters at steps 2/5 (R-05) |
| Financial conditions | R-58 | No | Level of restrictiveness, not direction. Enters as premise text for T05/T17 |
| 10-year vs nominal GDP | R-56 | No | Duration evidence |
| Fiscal supply | R-63 | No | Duration evidence |
| Cross-region block | R-12 | No for the US | US duplicates the R-14 inputs. Counted only for EA, JP, UK |
| Forward guidance / SEP path; market-implied path; inflation momentum | R-67, R-68 | No | Hybrid track only (R67-02 chose C; R68-02). R-67 is a warning flag until it passes §6e; R-68 is report-only |
| Dovish pivot as a policy act | none | n/a | No faithful-track rule reads Fed guidance. R-68 reads the SEP (core PCE only) in the hybrid track |

## 3. Point-in-time computation, month ends 2023-09 to 2024-10

Method: `AmberLakeSource(series=ENGINE_SERIES)`, `regime.run(a, src.snapshot(a), registry.load_default(), source=src, timeline=tlm.load())` at `et_close(last business day)`, faithful track. Hybrid columns come from the same call with `track="hybrid"` and all catalogue series. Registered parameters: `liq.netliq.window_w` 13, `liq.confirm_periods` 2, `policy.tg_threshold_pp` 2.0, `fci.loose_threshold` 0.0, `fci.change_window_w` 13, `rates.ngdp_anchor_gap_pp` 0.0. Units: R-03 and R-04 in $bn.

| Month end | R-03 level | R-03 Δ | R-03 sign | R-04 level | R-04 sign | LIQ sign | R-14 | R-06 TG (pp) | R-06 sign | R-58 state | NFCI | ΔNFCI 13w | R-56 gap | R-56 | R-63 | R-66 P(e/n/t) | Direction |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023-09-29 | -127 | 24 | -1 | -1159 | -1 | -1 | tightening | -1.85 | 0 | loose | -0.458 | -0.205 | -1.34 | rich | unknown | .043/.043/.913 | tightening |
| 2023-10-31 | 23 | 11 | +1 | -1047 | -1 | 0 | tightening | -1.83 | 0 | loose | -0.390 | -0.084 | -1.43 | rich | unknown | .043/.478/.478 | tightening |
| 2023-11-30 | 264 | 45 | +1 | -1051 | -1 | 0 | tightening | -1.04 | 0 | loose | -0.504 | -0.157 | -2.01 | rich | unknown | .043/.478/.478 | tightening |
| 2023-12-29 | 284 | -32 | +1 | -817 | -1 | 0 | tightening | -1.07 | 0 | loose | -0.543 | -0.188 | -2.42 | rich | unknown | .043/.478/.478 | tightening |
| 2024-01-31 | 266 | -47 | +1 | -672 | -1 | 0 | tightening | -1.33 | 0 | loose | -0.564 | -0.224 | -1.72 | rich | unknown | .043/.478/.478 | tightening |
| 2024-02-29 | 48 | -40 | +1 | -716 | -1 | 0 | tightening | -1.04 | 0 | loose | -0.518 | -0.114 | -1.51 | rich | unknown | .043/.478/.478 | tightening |
| 2024-03-29 | 2 | 6 | -1 | -843 | -1 | -1 | tightening | -0.93 | 0 | loose | -0.556 | -0.088 | -1.66 | rich | unknown | .043/.043/.913 | tightening |
| 2024-04-30 | -219 | -52 | -1 | -685 | -1 | -1 | tightening | -1.50 | 0 | loose | -0.508 | -0.008 | -0.82 | rich | unknown | .043/.043/.913 | tightening |
| 2024-05-31 | -91 | 52 | -1 | -417 | -1 | -1 | tightening | -1.22 | 0 | loose | -0.580 | -0.105 | -0.77 | rich | unknown | .043/.043/.913 | tightening |
| 2024-06-28 | -189 | -133 | -1 | -295 | -1 | -1 | tightening | -0.96 | 0 | loose | -0.568 | -0.083 | -1.11 | rich | unknown | .043/.043/.913 | tightening |
| 2024-07-31 | 12 | 123 | -1 | -525 | -1 | -1 | tightening | -0.45 | 0 | loose | -0.583 | -0.103 | -1.62 | rich | unknown | .043/.043/.913 | tightening |
| 2024-08-30 | -132 | -136 | -1 | -781 | -1 | -1 | tightening | -0.17 | 0 | loose | -0.553 | -0.031 | -2.03 | rich | unknown | .043/.043/.913 | tightening |
| 2024-09-30 | -118 | 3 | -1 | -736 | -1 | -1 | easing | 0.23 | 0 | loose | -0.577 | -0.062 | -1.90 | rich | unknown | .478/.043/.478 | easing |
| 2024-10-31 | -103 | -22 | -1 | -724 | -1 | -1 | easing | 0.21 | 0 | loose | -0.561 | -0.051 | -0.66 | rich | unknown | .478/.043/.478 | easing |

R-14 detail: `last_move` 2023-07-27 until 2024-09-19; programme RUNOFF throughout (the June 2024 runoff slowdown does not change the state). R-63 is unknown at every date because `FYFSGDA188S` has no rows in the lake (snapshot shape 0×7), a data gap. From public history (not computed): the FY2023 and FY2024 deficits were about 6% of GDP with UNRATE below NROU, so R-63 would likely have fired short-duration evidence. That is duration evidence, not a direction vote.

SEP federal funds median for year-end 2024 (from `spec\fomc_sep_events.yaml`, read as data) against the target midpoint in force (5.375% until 2024-09-18, then 4.875%):

| SEP in force (month ends) | Published | 2023 median | 2024 median | 2024 median − midpoint (pp) | Implied 25bp cuts to end-2024 |
|---|---|---|---|---|---|
| Jun 2023 SEP | 2023-06-14 | 5.6 | 4.6 | -0.775 | 3 (after one projected hike) |
| 2023-09 to 2023-11 | 2023-09-20 | 5.6 | 5.1 | -0.275 | 1 (after one projected 2023 hike) |
| 2023-12 to 2024-02 | 2023-12-13 | 5.4 | 4.6 | -0.775 | 3 |
| 2024-03 to 2024-05 | 2024-03-20 | — | 4.6 | -0.775 | 3 |
| 2024-06 to 2024-08 | 2024-06-12 | — | 5.1 | -0.275 | 1 |
| 2024-09 to 2024-10 | 2024-09-18 | — | 4.4 | -0.475 (vs 4.875) | 2 more |

Hybrid track, for reference only (not part of the vote): R-67 reads easing at every month end from 2023-10 to 2024-10 except 2023-09, 2024-04 and 2024-05 (neutral). The deciding leg is M2 (2-year − FF from -34 to -150bp) from 2023-11 on, and Gr in 2023-10. R-68 gap (core PCE π6 − SEP core PCE projection): -0.73, -0.87, -1.22, -1.33, -0.54 from 2023-09 to 2024-01 (held below the -0.5 band from 2023-10 to 2024-01, so "ahead", meaning inflation is below the Fed's projection), then +0.09 to +0.58 from 2024-02 to 2024-07 (never held above +0.5 for 2 month ends, so in line). These classes are derived from the gap values and `r68.band_pp` 0.5 / `r68.hold_month_ends` 2. The engine's `state` field was not printed.

Additional finding (mechanical, outside the 2024 H1 window): `DFEDTARU` stores the cut at period 2024-09-19 with `published_at` 2024-09-19 23:59 ET. R-14 therefore reads tightening at the 2024-09-18 and 2024-09-19 closes and easing only from 2024-09-20. R-14's PIT text says "FOMC statement 14:00 ET on decision day". `library\research\turning_point_sources.md` names a 2024-09-18 easing case. If that case is in EP20, it is a miss from the publication lag alone. Every decision-day case in other cycles would carry the same 1–2 day lag, because `DFEDTARU` dates a change by its effective date (decision day + 1).

## 4. Candidate faithful-track explanations

| # | Explanation | Supporting statement | Rule that would carry it | Change type | Effect on other periods (reasoned, not computed against cases) | Single-episode fitting risk |
|---|---|---|---|---|---|---|
| C1 | **Accept the miss.** His pre-cut 2024 easing read is a reading of guidance (anticipated cuts) plus a stance judgement (markets show no restriction). Anticipation is hybrid-only (R67-02 = C); stance is excluded from direction by R-66 | 2024-05-07 is the only contemporaneous source. 2024-10/11 are post-cut | None on the faithful track. R-67 (hybrid) already reads easing for most of the window | None. The owner's R-14 rate-primary decision predicted "2024 H1 (EP20) stays wrong" (decisions.yaml, R-14 entry) | None | None |
| C2 | Dovish pivot as policy: SEP current-year FF median below the target midpoint (December SEP's next-year column in Jan–Mar, the R-68 convention) as a third US family | 2024-05-07 (NP verbatim on the pivot and guidance); 2024-10-16 (forward-guidance trap) | New R-66 family | Design change to R-66; re-register | Absent before 2012 (dots) or 2015-09 (median). 2015-18: projected hikes, so tightening (agrees with R-14). Jan–Mar 2019: the Dec 2018 SEP 2019 column of 2.9 > 2.375 reads tightening, against his Jan 2019 pivot read (DS/2019-06-07). 2020-21: neutral at the ZLB. Jan–Mar 2022: reads tightening before the first hike. 2025: easing. In 2024 with the registered base/increment: Jan–Feb masses tie three ways (R-14 T, LIQ N, SEP E), giving 1/3 each with R-14 winning the tie; Mar–Aug gives P(e/n/t) .333/.030/.636. **It does not flip `policy_direction`**; it only raises P(easing) | High. The level form fits 2024 only because the 2023 column (one more hike, Sep 2023 SEP) masks Sep–Nov 2023. The change form (R-21), Sep→Dec 2023 = -0.5 (easing), reads Jun 2024 (+0.5) as tightening, against the 2024 read. It is also anticipation in substance, which collides with R67-02 |
| C3 | R-14 "pivot" state: after the last hike, the cycle state flips to easing when guidance turns to cuts (C2 condition) | As C2 | R-14 | Design change to R-14 (a `stated` rule; its cite is "stay long until the Fed tightens") | Flips argmax in Jan–Aug 2024 (R-14 easing vs LIQ tightening is a tie, and R-14 wins the tie, giving 0.478 easing). Absent before 2012, so 2006-07 and 2000-01 holds are unchanged. 2019 H1: neutral from Mar 2019 (2.4 vs 2.375 inside any band), no gain. Reverses the 2026-10-07 owner decision that made R-14 rate-primary | Very high. One episode drives a change to the rule that defines `policy_direction`. Mechanically this is R-67 using the Fed's own projections, so it re-imports anticipation into the faithful track |
| C4 | Loose financial conditions read as easing (R-58 vote) | 2024-05-07, 2024-10-16, 2024-11-05 (NP verbatim) | R-58 as an R-66 family | Design change to R-66 | R-58 is loose at **every** month end from 2023-09 to 2024-10, including Oct–Nov 2023, when the library dates his read as tightening. Approximation on the latest NFCI vintage with the R-58 formula (weekly, not PIT): loose in 36% of weeks in the 2004-06 hikes, 63% in 2015-18, 30% in 2022-23 and 52% of 2021; tight in 85% of the 2007-08 cutting weeks. A loose = easing vote would pull 2005-06 and 2015-18 toward easing and push 2008 cuts toward tightening. His own use is stance ("no restriction"), which argues that easing is a mistake | High, and contradicted inside the episode (Oct 2023) |
| C5 | RRP/TGA drawdown liquidity (R-03 alone) | None in 2023-24 (gap) | R-03 / E.4a family rule | Design change to E.4a | R-03 is positive only Oct 2023–Feb 2024 and negative Mar–Aug 2024, so it does not cover the window. Positive in Oct–Nov 2023, against his tightening read | High, with no textual support |
| C6 | Policy error too loose (R-06) | 2024-10-16 / 11-05 "too loose" | R-06 into R-66, or a lower `policy.tg_threshold_pp` | Design change (R-66) or tuning | TG ranges from -0.17 to -1.85 and never crosses -2.0. The most negative TG (Sep 2023) coincides with his tightening read. A lower threshold would mark much of 2003-2021 too loose, and the vote would then measure stance, not direction | High |
| C7 | Fiscal (R-63) | 2023-10-24, 2023-11-01 | R-63 | None. Unknown today (data gap) | Duration evidence; it supported his 2023 bond short, which is a tightening-side reading | n/a |

## 5. Assessment

The faithful-track miss on EP20 is structural, not a data error. Every faithful-track input bearing on direction reads tightening or neutral from January to August 2024. The library holds one contemporaneous pre-cut statement, and it describes the December 2023 guidance pivot and loose financial conditions, which are a forecast of cuts and a stance judgement. Both are kept out of the faithful vote by existing owner decisions (R67-02, R-66 exclusions). The candidates that would flip 2024 either change the rule that defines `policy_direction` (C3) or add a vote that misreads Oct 2023 and other hiking cycles (C4). The decision-day lag in `DFEDTARU` is a separate mechanical issue that can be fixed by citing R-14's PIT text.

## 6. Decisions

| Option | Action | Reason |
|---|---|---|
| A (Recommended) | Accept the EP20 miss on the faithful track and record it as anticipation/stance (hybrid, R67-02). Separately, verify and fix the R-14 decision-day lag (`DFEDTARU` effective date + 23:59) as a mechanical fix citing "FOMC statement 14:00 ET on decision day" | Evidence for a faithful easing read before the cut is one interview that describes guidance and stance. The lag fix is spec-cited and affects every cycle turn |
| B | Add an SEP-guidance family to R-66 (C2, level form), re-registered as a design change | Raises P(easing) to 0.33 in 2024 without flipping direction. Partial RPS gain; it carries anticipation into the faithful track and hurts Jan–Mar 2019 |
| C | Redefine R-14 with a guidance "pivot" state (C3) | Flips 2024, but reverses the rate-primary owner decision and fits one episode |
| D | Count R-58 loose/tight as a direction vote (C4) | Not supported: loose in Oct 2023 against his read, and common in hiking cycles |
