# R-14 holdings component: how Druckenmiller read Fed balance-sheet policy

Research date 2026-10-07. Scope: research only. No engine run, no `fatpitch.versions` run; `cases\`, `cases\HOLDOUT.yaml` and `results\` not opened. Only this file was written. `spec\fed_cycles.yaml` was opened to its `qt_periods` block only (see section 5, conflict K5).

Reliability codes follow `spec\process.md` line 15 (front-matter of each note): **P** = primary (his own text), **NP** = near-primary transcript, **S** = secondary summary or relay. The brief's "S = source transcript / NP = notes" reading is the reverse of the library convention; the library convention is used here. Column "Vb" marks whether the quoted text is verbatim from him (Y) or the note's paraphrase (N).

## 0. Current rule and its defects

`src\fatpitch\rules\step1.py` `r14_policy_direction` (line 307): `policy_direction = sign(sign(ΔFF target, 6 m) + bs)`, where H = TREAST + WSHOMCB, window 13 w (`policy.holdings_change_window_w`), "QE active" = H/GDP rising over 13 w, and bs = +1 (tightening) if ΔH < 0 or (QE active and ΔH < previous 13 w ΔH); −1 if QE active otherwise; 0 if not QE active. QE-end setback flag: QE active within `liq.qe_end_setback_m` = 6 months but not now.

| Period | Current bs | Mechanism | Combined effect |
|---|---|---|---|
| 2004-06 | −1 or +1 alternating | Currency-driven H growth exceeds GDP growth in some windows; noise in ΔH vs previous ΔH | Cancels the hikes (neutral) |
| 2007-12 .. 2008-12 | +1 | Fed redeemed/sold ~$300bn of Treasuries to sterilise TAF/PDCF/swap lending (H fell while total assets were flat, then doubled) | Cancels the cuts |
| 2009-2014 | Flips weekly | Lumpy MBS settlement makes ΔH vs previous ΔH a coin toss; any slower quarter = "taper" | Most dates tightening or neutral in a QE regime |

The defects share one cause: the component reads week-level arithmetic of a series that also moves for non-policy reasons (currency demand, sterilisation, settlement timing), and treats any deceleration as tightening. No library statement supports deceleration-as-tightening for the US Fed (section 1, rows 6, 10, 11, 20).

## 1. Druckenmiller statements on balance-sheet policy

| # | Date | File | Rel | Vb | Quote (short) | Implication for R-14 |
|---|---|---|---|---|---|---|
| 1 | 2009 (Q4 est.) | `DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md` | NP | Y | "If you have the money supply growing a lot faster than industrial production, the stock market is generally going to go up." | Liquidity flow vs activity (R-02). In Q4 2009 QE1 purchases were being "gradually slowed" (FOMC 2009-08-12, 2009-09-23) and his read was still easing: a taper phase is not tightening. |
| 2 | 2012-04 (inferred month) | `DS/2012-04-XX_grants-spring-conference-jim-grant.md` | S | Y (fragment) | Only way to trade is to "trade the monetary stimulus. I think we'll have a problem starting in a month or two." | Regime on/off reading. Problem dated to the scheduled end of Operation Twist (June 2012): a maturity-extension programme counts as "stimulus", and its scheduled end is the risk event. |
| 3 | 2012-04 | same | S | N | QE rallies (QE1, QE2, Japan) came apart within about six months of ending. | QE end = setback, horizon ~6 months (source of `liq.qe_end_setback_m`). Event = implementation end, not announcement. |
| 4 | 2012-04 | same | S | Y | "When monetary stimulus is on, I'm long gold. When stimulus is off, I'm less long." | Binary programme state, not a flow gradient. |
| 5 | 2013-05-08 | `DS/2013-05-08_sohn-commodities-conundrum.md` | S | N | QE produces a near-term "melt-up"; damage comes when the Fed tightens; Japan QE ~3x the US relative to market cap. | Active QE = easing. Relative intensity matters across regions (R-12, not R-14). |
| 6 | 2013-09-19 | `DS/2013-09-19_cnbc-squawk-box-fed-wealth-transfer.md` | S | Y | "This is fantastic for every rich person." (day after the no-taper surprise; "I had a very good day yesterday") | Announcement effect: a decision not to taper traded as easing on the statement day. Supports announcement timing for programme changes. |
| 7 | 2014-06-19 | `DS/2014-06-19_wsj-oped-warsh-asset-rich-income-poor.md` | P | Y | "The sooner and more predictably the Fed exits its extraordinary monetary accommodation..." | Read during the 2014 taper (purchases $45bn/month): policy still "extraordinary accommodation". Taper ≠ exit. |
| 8 | 2014-07-16 | `DS/2014-07-16_delivering-alpha-kernen.md` | NP (claim from note summary; speech part secondary) | N | Playbook: stay long until the Fed tightens; watch the end of QE, since setbacks followed QE1, QE2 and Japan's QE exits. | Strongest single statement. Mid-taper ($35bn/month), the Fed had not yet "tightened". The end of purchases (implementation) is the risk event. |
| 9 | 2014-07-16 | same | NP | Y | "I am still dancing… I can get out in a week." | Taper phase read as still-easy regime. |
| 10 | 2015-03-02 | `DS/2015-03-02_cnbc-closing-bell-kelly-evans.md` | NP | Y | "The one thing we learned in the United States about QE is it definitely inflates financial asset prices." | QE active = easing; positioned where QE was beginning (Japan, Europe). Start of a programme matters. |
| 11 | 2015-04-15 | `DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md` | NP | N | Diverging policy (Fed tapering vs ECB QE and negative rates) is a "textbook" currency opportunity. | Taper used in a relative (cross-region) sense: Fed less easy than ECB. Supports R-12 relative impulse, not taper = absolute tightening. |
| 12 | 2017-12-12 | `DS/2017-12-12_cnbc-closing-bell-kelly-evans.md` | NP | Y | "I think the stock market is basically a function of central bank policy." | Read easing (Taylor gap) while QT1 had run 2 months at $10bn/month caps. Small initial runoff did not change his read of the level. |
| 13 | 2018-05-03 | `DS/2018-05-03_manhattan-institute-hamilton-award-speech.md` | P | Y | "...kept interest rates below inflation but have accumulated an unprecedented $4.5 trillion on their balance sheet by doing QE." | Stock (level) used for "how easy", during QT1 ramp ($30bn/month caps). Level belongs to R-06-type judgement; direction rule unaffected. |
| 14 | 2018-09-06 | `RS/2018-09-06_sokoloff-real-vision-interview.md` | NP (notes) | N | Global QE ~$1T/yr going to zero within 12 months (Fed $50bn/month runoff, ECB €30bn/month to zero). | Rate of change of the (global) flow matters; read as tightening. The US part is QT at full pace (flow negative), not a taper. The taper part is the ECB (R-12). |
| 15 | 2018-09 | same, via `library/research/tightening_sources.md` | NP | Y | "Some of the things that tend to happen early in a monetary tightening are responding to the QE shrinkage." | QT = tightening (explicit). |
| 16 | 2018-10-09 | `DS/2018-10-09_grants-fall-conference-jim-grant.md` | S | N (HFA headline) | "It's all about liquidity, and liquidity is going down." | QT + hikes + end of foreign QE = liquidity falling. |
| 17 | 2018-11-21 | `DS/2018-11-21_wsj-interview-risky-to-be-tightening.md` | S | Y (relay) | "As quantitative easing turns to quantitative tightening, all these zombies are going to be exposed." | QT = tightening; regime language (QE turns to QT). |
| 18 | 2018-12-16 | `DS/2018-12-16_wsj-oped-warsh-fed-tightening-not-now.md` | S | Y (via coverage) | Fed should pause its "double-barreled blitz of higher interest rates and tighter liquidity." | Rate and balance-sheet tightening are two additive barrels (supports the sum form, not a rate-only rule). |
| 19 | 2019-06-07 | `DS/2019-06-07_cnbc-squawk-box-one-way-bet.md` | NP | Y | "I'm a liquidity guy." | Re-risked on the Fed pivot (pause; QT slowdown announced 2019-03-20; QT end pending) before any cut. Announced wind-down of QT read as no longer tightening. |
| 20 | 2019-12-18 | `DS/2019-12-18_bloomberg-schatzker-couldnt-have-been-more-wrong.md` | S | N | Three Fed cuts plus trade de-escalation drove his turn to risk. | Q4 2019 easing read attributed to cuts; no mention of the October 2019 bill purchases. No statement on reserve-management purchases exists in the library (gap). |
| 21 | 2020-05-12 | `RS/2020-05-12_economic-club-of-new-york.md` | S (Felder verbatim) | Y | "...liquidity shrinks as far as the eye can see as the Treasury borrowing crowds out not only the private economy but even overwhelms Fed purchases…" | Flow framing (Fed purchases vs Treasury net issuance): net liquidity is R-03/R-04's job. Gross purchases alone were not his read; the call was reversed 2020-06-08. |
| 22 | 2020-06-08 | `DS/2020-06-08_cnbc-squawk-box-humbled-underestimated-fed.md` | NP | N | Underestimated "how many red lines, and how far, the Fed would go." | Programme scale and open-endedness (2020-03-23 "in the amounts needed") dominate. |
| 23 | 2021-05-10/11 | `DS/2021-05-10_wsj-oped-fed-emergency-policy-bubbles.md`, `DS/2021-05-11_hustle-mfm-trung-phan.md` | S / NP | Y (Hustle) | "The minute they start tightening, the equity market should go down a lot." | Trigger is the start of tightening. Purchases at $120bn/month = easing. |
| 24 | 2022-06 (late May/early June) | `DS/2022-06-XX_sohn-2022-john-collison.md` | NP | N | The Fed was very late, still buying bonds in March 2022. | Taper phase (Nov 2021 - Mar 2022) still counted as buying = easing (retrospective). |
| 25 | 2022-09-28 | `DS/2022-09-28_delivering-alpha-kernen-transcript.md` | NP | N | QT offset by TGA drawdown and SPR releases until ~Q1 2023. | QT = tightening in gross terms; net effect is R-03's job. |
| 26 | 2023-04-24 | `RS/2023-XX-XX_nbim-investment-conference-2023.md` / `DS/2023-04-24_nbim-annual-investment-conference.md` | S / NP | Y (S) | "In 4 days, they printed enough money to wipe out the entire reduction in the balance sheet that had been done over 4 months." | Total assets (incl. lending facilities) is what he watches, not securities only. Supports WALCL over TREAST+WSHOMCB for any data measure. He still read the Fed as tightening overall (500bp). |
| 27 | 2023-10-24 | `DS/2023-10-24_robin-hood-paul-tudor-jones.md` | S | N | Bernanke's "temporary" balance sheet went from $800bn to $9T. | Stock/credibility point; no direction implication. |
| 28 | 2024-10-01 / 10-16 | `DS/2024-10-01_grants-fall-conference-2024.md`, `DS/2024-10-16_bloomberg-tv-sonali-basak.md` | S / NP | N | Sept 2024 50bp cut reflationary; policy too loose. | Read easing while QT (slowed, $25bn Treasury cap) was still running. Cuts dominate a slowed QT. |
| 29 | 1989 (retro., said 1991) | `DS/1992-XX-XX_new-market-wizards-full-chapter-text.md` | P | Y | BoJ tightening "three times as important as everything I just said". | Foreign central banks matter (R-12). |
| 30 | 2014-07-16 | `DS/2014-07-16_delivering-alpha-kernen.md` | NP | N | Setbacks followed Japan's QE exits. | Foreign QE exits (BoJ 2006-03) are QE-end events; R-12 scope, not R-14. |

### 1a. Synthesis

| Question | His reading | Support | Confidence |
|---|---|---|---|
| Stock vs flow vs flow-change | Direction from the flow regime (QE on / off / QT); stock used for "how easy" and misallocation, not direction; flow-change cited once (2018), for a global flow going to zero alongside US QT | rows 2-4, 8, 13, 14 | Medium |
| Announcement vs implementation | Starts and surprises trade on announcement (2013-09-19); the QE-end setback is dated to the implementation end | rows 3, 6, 8 | Medium |
| QE end | Setback within ~6 months | rows 3, 8, 30 | Medium (secondary for the 6 months) |
| QT | Tightening | rows 15-18 | High (several, two verbatim) |
| Taper | Not tightening while purchases continue (2009 Q4, mid-2014, Mar 2022 retrospective); "tapering" used only as relative policy divergence (2015) | rows 1, 7-9, 11, 24 | Medium; no statement calls a US taper tightening |
| Twist / maturity extension | "Monetary stimulus"; its scheduled end is a QE-end event | row 2 | Low-medium (single S source) |
| Emergency lending (2008, 2023) | Counts as balance-sheet expansion ("printed money") | row 26 | Medium |
| Reserve-management purchases (2019-10, 2025-12) | No statement located | — | Gap |
| QT slowdown / end | Implicit only: 2019 pivot and 2024 cuts read as easing while slowed QT continued | rows 19, 28 | Low |
| Foreign QE | Matters, including QE exits (BoJ) | rows 5, 11, 14, 29, 30 | R-12 scope |

## 2. Fed balance-sheet policy events 2008-2025

Verified = text of the federalreserve.gov release fetched on 2026-10-07 (WebFetch). Release times: given where the release page states one; otherwise "≈" times are from memory and marked UNVERIFIED. All weekday releases listed occur before 16:00 ET, so a 16:00 ET snapshot sees them the same day; exceptions are noted.

| Date | Time (ET) | Event | Content | State change (design A) | URL | Status |
|---|---|---|---|---|---|---|
| 2008-11-25 | 08:15 | QE1 announced (Board release, not an FOMC statement) | Up to $100bn GSE debt, $500bn agency MBS | NONE → EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20081125b.htm | Verified (time stated) |
| 2008-12-16 | ≈14:15 | FOMC: FF 0-0.25; "large quantities" of agency debt and MBS; evaluating Treasury purchases | — | (EXPAND) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20081216b.htm | Verified; time UNVERIFIED |
| 2009-03-18 | ≈14:15 | QE1 expanded | +$750bn MBS (to $1.25T), +$100bn agency (to $200bn), $300bn Treasuries over 6 months | EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20090318a.htm | Verified; time UNVERIFIED |
| 2009-08-12 | ≈14:15 | Treasury purchases slowed, complete end-Oct 2009 | taper of Treasury leg | EXPAND (taper sub-state) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20090812a.htm | Verified; time UNVERIFIED |
| 2009-09-23 | ≈14:15 | MBS/agency purchases slowed, complete end-Q1 2010 | taper of MBS leg | EXPAND (taper) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20090923a.htm | Verified; time UNVERIFIED |
| 2010-03-16 | ≈14:15 | QE1 purchases "executed by the end of this month" | $1.25T MBS, ~$175bn agency | EXPAND → NONE at 2010-03-31 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20100316a.htm | Verified; time UNVERIFIED |
| 2010-08-10 | ≈14:15 | Reinvest MBS/agency paydowns into Treasuries | holdings held constant | NONE (stops passive runoff) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20100810a.htm | Verified; time UNVERIFIED |
| 2010-11-03 | ≈14:15 | QE2 | $600bn Treasuries by end-Q2 2011, ~$75bn/month | NONE → EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20101103a.htm | Verified; time UNVERIFIED |
| 2011-06-22 | ≈12:30 (press-conference meeting) | QE2 to complete "by the end of this month" | reinvestment continues | EXPAND → NONE at 2011-06-30 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20110622a.htm | Verified; time UNVERIFIED |
| 2011-09-21 | ≈14:15 | Operation Twist (maturity extension) | Buy $400bn 6-30y, sell equal ≤3y, by end-June 2012; MBS paydowns into MBS | NONE → EXPAND (duration programme; see K2) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20110921a.htm | Verified; time UNVERIFIED |
| 2012-06-20 | ≈12:30 | Twist extended through end-2012 | ~$267bn (amount from memory, UNVERIFIED) | EXPAND (scheduled end moved) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20120620a.htm | Verified; amount and time UNVERIFIED |
| 2012-09-13 | ≈12:30 | QE3 (MBS) | $40bn/month MBS, open-ended | EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20120913a.htm | Verified; time UNVERIFIED |
| 2012-12-12 | ≈12:30 | QE3 Treasuries | $45bn/month from end of Twist (Jan 2013) | EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20121212a.htm | Verified; time UNVERIFIED |
| 2013-05-22 / 2013-06-19 | — | Bernanke JEC testimony / press conference taper roadmap ("taper tantrum") | communication only | none (not a statement decision) | not fetched | UNVERIFIED |
| 2013-09-18 | 14:00 | No taper | $40bn MBS + $45bn Tsy unchanged | EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20130918a.htm | Verified; time UNVERIFIED (14:00 standard from 2013) |
| 2013-12-18 | 14:00 | Taper announced | from Jan 2014: $35bn MBS + $40bn Tsy (−$10bn/month) | EXPAND (taper) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20131218a.htm | Verified; time UNVERIFIED |
| 2014-10-29 | 14:00 | Purchases concluded "this month"; reinvestment continues | — | EXPAND → NONE at 2014-10-31 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20141029a.htm | Verified; time UNVERIFIED |
| 2017-06-14 | 14:00 | Addendum to Normalization Principles: caps $6bn Tsy / $4bn MBS, +6/+4 per quarter to $30bn / $20bn | plan, no start date | none | https://www.federalreserve.gov/newsevents/pressreleases/monetary20170614c.htm | Verified (time stated) |
| 2017-09-20 | 14:00 | QT1 to start in October 2017 | caps per addendum | NONE → RUNOFF (announcement) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20170920a.htm | Verified (time stated) |
| 2019-01-30 | 14:00 | Statement on implementation and normalization: ample reserves; ready to alter balance sheet | pivot communication | RUNOFF (no change) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20190130c.htm | Verified; time UNVERIFIED |
| 2019-03-20 | 14:00 | QT slowdown and end plan | Tsy cap $30bn → $15bn from May 2019; runoff ends end-Sept 2019; MBS paydowns into Tsy from Oct (≤$20bn) | RUNOFF (slowed sub-state) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20190320c.htm | Verified (time stated) |
| 2019-07-31 | 14:00 | QT ends in August, two months early; FF cut | runoff ends 2019-08-01 | RUNOFF → NONE at 2019-08-01 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20190731a.htm | Verified (time stated); effective day 08-01 per `spec/fed_cycles.yaml` basis text |
| 2019-10-11 | 11:00 | Reserve-management T-bill purchases from 2019-10-15 "at least into the second quarter"; "purely technical… do not represent a change in the stance of monetary policy" | pace ~$60bn/month (NY Fed statement; UNVERIFIED) | NONE (technical) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20191011a.htm | Verified (time stated); pace UNVERIFIED |
| 2020-03-15 (Sun) | 17:00 | QE4 | ≥$500bn Tsy, ≥$200bn MBS; FF 0-0.25 | NONE → EXPAND, effective in the 2020-03-16 snapshot | https://www.federalreserve.gov/newsevents/pressreleases/monetary20200315a.htm | Verified (time stated) |
| 2020-03-23 | 08:00 | Purchases "in the amounts needed" | open-ended | EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20200323b.htm | Verified (time stated) |
| 2020-06-10 | 14:00 | "At least at the current pace" | ~$80bn Tsy + $40bn MBS (amounts from memory) | EXPAND | https://www.federalreserve.gov/newsevents/pressreleases/monetary20200610a.htm | Verified (time stated) |
| 2021-11-03 | 14:00 | Taper announced | −$10bn Tsy, −$5bn MBS per month from November | EXPAND (taper) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20211103a.htm | Verified (time stated) |
| 2021-12-15 | 14:00 | Taper doubled | −$20bn Tsy, −$10bn MBS per month; Jan 2022 $40bn + $20bn | EXPAND (taper) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20211215a.htm | Verified (time stated) |
| 2022-01-26 | 14:00 | Purchases end "in early March"; Principles for Reducing the Size of the Balance Sheet (FF is primary tool; runoff after liftoff) | — | EXPAND → NONE in early March 2022 (final purchase date ≈2022-03-09, UNVERIFIED) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20220126a.htm ; https://www.federalreserve.gov/newsevents/pressreleases/monetary20220126c.htm | Verified (time stated for statement) |
| 2022-03-16 | 14:00 | First hike | — | (NONE) | not fetched | date known, page not fetched |
| 2022-05-04 | 14:00 | QT2 plan: start 2022-06-01; caps $30bn Tsy / $17.5bn MBS, rising to $60bn / $35bn after three months | — | NONE → RUNOFF (announcement) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20220504b.htm | Verified; time UNVERIFIED |
| 2024-05-01 | 14:00 | QT slowdown | Tsy cap $60bn → $25bn from June 2024; MBS cap $35bn | RUNOFF (slowed) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20240501a.htm | Verified (time stated) |
| 2025-03-19 | 14:00 | Further slowdown | Tsy cap $25bn → $5bn from April 2025 | RUNOFF (slowed) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20250319a.htm | Verified (time stated) |
| 2025-10-29 | 14:00 | QT ends 2025-12-01 | aggregate reduction concluded; MBS paydowns into bills (from memory, UNVERIFIED) | RUNOFF → NONE at 2025-12-01 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm | Verified (time stated) |
| 2025-12-10 | 14:00 | Reserve-management purchases of T-bills | first schedule 2025-12-11, ~$40bn in the first month, purchases from 2025-12-12 (NY Fed operating policy https://www.newyorkfed.org/markets/opolicy/operating_policy_251210a, search snippet) | NONE (technical) | https://www.federalreserve.gov/newsevents/pressreleases/monetary20251210a.htm | Verified (statement); pace from NY Fed snippet, page not fetched |

Not policy events but relevant to data designs: 2007-12 .. 2008-08 sterilisation (Treasury redemptions/sales offsetting TAF, PDCF, swap lines; TREAST roughly $780bn → $480bn, figures from memory, UNVERIFIED; checkable in the lake TREAST series); 2008-09 .. 2008-12 emergency lending (WALCL ~$0.9T → ~$2.2T, memory); 2009 H1 facility runoff (WALCL fell while securities rose); 2019-09-17 repo operations; 2023-03-12 BTFP and discount-window surge.

PIT: event effective at release time; a 16:00 ET snapshot uses same-day state for every weekday release above. Implementation-end transitions (EXPAND → NONE, RUNOFF → NONE) take effect on the stated completion date, which is always published before it occurs, so no look-ahead.

## 3. Free data that can measure purchase flow

| Series | What it measures | Weekly from | Before | Use | Issue |
|---|---|---|---|---|---|
| `TREAST` + `WSHOMCB` | Outright Treasury + MBS holdings (H.4.1, Wed level, Thu 16:30 ET) | 2002-12-18 | Z.1 quarterly fallback (grade C) | Securities purchase flow | Includes bills (RMPs 2019, 2025 count as purchases); sterilisation 2007-08 reads as sales; MBS settlement lumpiness |
| `WALCL` | Total assets incl. lending facilities, swaps, repo | 2002-12-18 | BIS monthly `US_CB_ASSETS_M` 1914→ (grade B) | Total balance-sheet flow; matches row 26 | Facility runoff early 2009 reads as contraction during QE1 ramp; 2019 repo, 2023 BTFP read as expansion; already the base of R-03 (overlap) |
| `CB_ASSETS_GDP_US` | BIS CB assets / GDP, quarterly | — | 1947→ | Stock/GDP context | Too coarse for direction |
| `GDP` | Nominal GDP (ALFRED vintage) | quarterly | 1947→ | Normaliser for flow/GDP | Advance release lag ~30 days |
| `FOMC_CALENDAR` | Event table | — | — | Design A/C | **Missing** in catalogue (`spec/data_catalogue.yaml` line 1572); would be built from section 2 |
| Bills split (`WSHOBL`, `WSHONBNL` on FRED) | Bills vs notes/bonds | 2002-12 (FRED, not verified) | — | Excluding RMP bill purchases | Not in the catalogue or lake (gap) |

## 4. Candidate designs

Notation: bs ∈ {−1 easing, 0 neutral, +1 tightening}; combination unchanged: `policy_direction = sign(sign(ΔFF, policy.ff_change_window_m) + bs)`. No design adds a registry parameter; constants are fixed in the formula and argued below.

### Design A: announced programme regime (event-driven)

Plain words: the Fed is either running an announced net-purchase programme (easing), running an announced runoff (tightening), or neither (neutral). Taper and slowdown phases keep the sign of the flow until the stated end. Technical purchases (pre-2008 open-market operations, 2019-10 and 2025-12 reserve management) are neither.

Formula:
- `state(t)` from an event table `spec\fomc_bs_events.yaml` (rows of section 2: date, release time ET, URL, new state, effective date).
- EXPAND: from announcement of a net purchase or maturity-extension programme until its stated completion date. bs = −1.
- RUNOFF: from announcement of a runoff start until its stated completion date. bs = +1.
- NONE: otherwise, including reinvestment-only periods and technical/reserve-management purchases the FOMC labels as not a change of stance. bs = 0.
- Sub-state flags (diagnostic, no sign effect): `taper` (EXPAND after an announced pace reduction), `slowed` (RUNOFF after an announced cap reduction).
- QE-end setback flag: EXPAND → NONE transition within `liq.qe_end_setback_m` (6) months.
- Constants: none.

Support: rows 2-4 (stimulus on/off), 3 and 8 (QE end as the event), 6 (announcements trade), 1, 7-9, 24 (taper still easing), 15-18 (QT = tightening), Fed's own label for RMPs (2019-10-11 release).

Tag: `interpreted` (component mapping; events are public Fed facts). R-14 header remains `stated`.

### Design B: purchase flow as share of GDP (data-driven)

Plain words: annualised 13-week change in Fed assets as % of nominal GDP; easing above +1 %, tightening below −1 %, neutral in between; a taper is the flow falling below half of its 52-week peak while still positive.

Formula:
- `f(t) = 4 × (X_t − X_{t−13w}) / GDP_t × 100`, X = `WALCL` (B2) or `TREAST+WSHOMCB` (B1).
- bs = −1 if f ≥ +1 and f ≥ 0.5 × max(f over prior 52 w); bs = 0 if 0 < f and f < 0.5 × peak (taper; see K3 for the +1 alternative); bs = +1 if f ≤ −1; else 0.
- Constants: m = 1 % of GDP/yr (argued: pre-2008 currency-driven growth ~0.2-0.4 %/yr sits below it; every announced programme pace except the last taper month and the 2025 $5bn cap sits above it; e.g. QE2 $75bn/month ≈ 6 %, QT1 full pace $50bn/month ≈ 3 %, QT2 full pace $95bn/month ≈ 4.5 %, using GDP $15-26T). Taper ratio 0.5 and peak lookback 52 w: no source; convention only.
- QE-end flag: f crosses below +m after ≥ 13 w above.

Support: row 14 (rate of change), row 21 (flow framing), row 26 (total assets, B2). Tag: `interpreted`, three uncited constants (m, 0.5, 52 w) under a full tunable cap: they must be fixed and cannot be justified by any library statement.

### Design C: hybrid (event regime, data materiality on runoff)

Plain words: Design A, except a RUNOFF state counts as tightening only when actual runoff is material (f_B1 ≤ −1 % of GDP/yr over 13 w); otherwise 0. EXPAND keeps counting from announcement (announcement effect, row 6).

Formula: bs = A's bs, except RUNOFF with f_B1 > −1 → 0. Constants: m = 1 % (as B).

Support: rows 12-13 (easing read during the $10-30bn/month QT ramp), 14-18 (tightening once runoff near full pace), 28 (easing read during slowed QT). Tag: `interpreted`, one uncited constant. Asymmetry (materiality on runoff, none on purchases) is itself uncited.

### Design D: minimal repair of the current rule (reference only)

Current rule with (i) "QE active" from Design A's EXPAND state instead of H/GDP rising, (ii) taper removed (QE active → −1). Holdings falling outside QE still → +1. Fixes 2009-2014 noise and pre-2008 easing; does not fix 2008 sterilisation (H falling → +1 cancels cuts). Listed to show that the 2008 defect needs either the event regime or WALCL.

### 4a. Readings by period (reasoned from section 2 and known balance-sheet history; engine not run)

| Period | FF component | A | B1 (securities) | B2 (WALCL) | C | Notes |
|---|---|---|---|---|---|---|
| 2004-06 hikes | +1 | 0 → **tightening** | f ≈ +0.2-0.4 → 0 → tightening | same → tightening | 0 → tightening | All fix defect 1 |
| 2008-01 .. 2008-11-24 cuts | −1 | 0 → **easing** | f ≈ −2 to −4 (sterilisation) → +1 → **neutral** | flat to 2008-08 (0), surge Sep-Dec (−1) → easing | 0 → easing | B1 keeps defect 2 |
| 2008-11-25 .. 2008-12 | −1 | −1 → easing | still ≤0 until MBS buying (Jan 2009) → easing via FF | −1 → easing | −1 → easing | — |
| 2009 H1 | −1 then 0 (window) | −1 → easing | −1 → easing | facility runoff: f negative → +1 → **neutral/tightening** | −1 | B2 defect in 2009 |
| 2009-08 .. 2010-03 (QE1 taper) | 0 | −1 → easing | taper rule → 0 from ~Q1 2010 → neutral | similar | −1 | A matches row 1 |
| 2010-04 .. 2010-11-02 | 0 | 0 + setback flag → neutral | MBS paydowns Apr-Aug (~−1.3 %) → **tightening** | same | 0 | No library read for this window |
| 2010-11 .. 2011-06 (QE2) | 0 | −1 → easing | −1 → easing | −1 | −1 | — |
| 2011-07 .. 2011-09-20 | 0 | 0 + setback flag | ~0 | ~0 | 0 | — |
| 2011-09-21 .. 2012-12 (Twist) | 0 | −1 → easing | net ~0 → neutral | ~0 → neutral | −1 | Row 2 treats Twist as stimulus: A/C match, B does not |
| 2013 .. 2014-06 (QE3, taper from Jan 2014) | 0 | −1 → easing | −1, taper → 0 from ~mid-2014 | same | −1 | B's taper timing depends on MBS settlement noise |
| 2014-07-16 (his "stay long") | 0 | −1 easing | 0 neutral | 0 neutral | −1 | Both compatible with "stay long until the Fed tightens"; neither reads tightening |
| 2014-11 .. 2015-12 | 0 | 0 + setback flag to 2015-04 | 0 | 0 | 0 | — |
| 2015-12 .. 2017-09 (hikes) | +1 (windowed) | 0 → tightening when FF moved | 0 | 0 | 0 | — |
| 2017-10 .. 2018-Q1 (QT ramp) | +1 | +1 → tightening | f ≈ −0.6 → 0 → tightening (FF) | similar | 0 → tightening (FF) | Combined result identical; his easing reads (rows 12-13) are level reads |
| 2018-Q2 .. 2019-04 (QT near full) | +1 | +1 | +1 | +1 | +1 | All match rows 14-18 |
| 2019-05 .. 2019-07-31 (slowed QT) | +1 to 06-19, then 0 | +1 → tightening to 07-31 | f ≈ −1.5 to −2 → +1 | same | +1 (still > m) | Conflict with row 19 in all designs; driven by the 6-month FF window and the sum (K4) |
| 2019-08 .. 2019-10-10 | −1 | 0 → easing | ~0 → easing | repo from 09-17: −1 → easing | 0 | — |
| 2019-10-11 .. 2020-02 (RMP) | −1 | 0 → easing | bills ≈ +3-4 % → −1 → easing | −1 → easing | 0 → easing | Combined identical; differs only if FF flat (from ~2020-04 the QE4 regime takes over) |
| 2020-03 .. 2021-10 | −1 then 0 | −1 → easing | −1 | −1 | −1 | — |
| 2021-11-03 .. early 2022-03 (taper) | 0 | −1 → easing | taper → 0 from ~Jan 2022 → neutral | same | −1 | Row 24 (retrospective) reads still buying = easing: A/C match |
| 2022-03-16 .. 2022-05-03 | +1 | 0 + setback flag → tightening | 0 | 0 | 0 | — |
| 2022-05-04 .. 2024-05 (QT2) | +1 then 0 after 2023-07 | +1 → tightening | +1 from ~2022-08 (13 w accumulation) | +1, except 2023-03..05 BTFP (≈0 or −1) | +1 from ~2022-08 | Row 26 matches B2's 2023 dip only in direction of offset |
| 2024-06 .. 2024-09-17 (slowed QT, FF flat) | 0 | +1 → **tightening** | f ≈ −1.8 → +1 → tightening | same | +1 | No library read in this window |
| 2024-09-18 .. 2025-03 (cuts, slowed QT) | −1 | +1 → **neutral** | +1 → neutral | +1 → neutral | +1 → neutral | Conflict with row 28 in A, B, C (K4) |
| 2025-04 .. 2025-11 ($5bn Tsy cap) | −1 / 0 | +1 → neutral or tightening | f ≈ −0.8 → 0 | similar | 0 → easing/neutral | C matches row 28 best |
| 2025-12 → (QT end, RMP) | −1 | 0 → easing | bills +1.8 % → −1 | −1 | 0 | Fed labels RMP technical; no Druckenmiller read |

## 5. Conflicts

| ID | Conflict | Bearing |
|---|---|---|
| K1 | `process.md` R-14 formula text "taper = tightening when second derivative of holdings < 0 after QE" vs rows 1, 7-9, 24 (taper read as still easing). The text appears derived from row 14, where the flow going to zero is global (ECB taper) and the US part is QT | Adopting A, B (taper → 0) or C changes the R-14 formula text: a design change, re-registration required (CLAUDE.md pre-registration rule) |
| K2 | Twist as stimulus rests on one secondary note (row 2) | A and C classify maturity extension as EXPAND; B cannot see it |
| K3 | Taper value in B: 0 (chosen) vs −1 (keep easing until end) vs +1 (current) | No source supports +1; −1 collapses B toward A |
| K4 | The sum `sign(rate + bs)` yields neutral whenever cuts coincide with runoff (2019-07-31 is the only overlap day in QT1; 2024-09-18 .. 2025-11-30 in QT2) and tightening during slowed QT with a flat FF. Row 28 reads 2024-Q4 as easing; row 19 reads mid-2019 as a pivot. Row 18 ("double-barreled") supports additivity when both tighten | Not fixable inside the holdings component without uncited thresholds (C partly does, from 2025-04 only). The alternative is a combination change (rate sign primary, bs only when rate sign is 0), citing the Fed's own "primary means" language (2022-01-26 principles) and row 8; that is outside this brief's scope and a separate design change |
| K5 | `spec\fed_cycles.yaml` (Fed cycle check answer key, scoring.md 6d) labels QT periods 2017-10 .. 2019-07 and 2022-06 .. 2025-11 as tightening. Design A's RUNOFF state is built from the same FOMC statements | A mechanically agrees with that answer key on QT windows (except announcement-to-start weeks). The rationale here rests on rows 15-18, not on the key; the agreement is a construction overlap, not evidence, and should be disclosed in the re-registration |
| K6 | R-17 uses "QE active = holdings/GDP rising", the same definition being replaced | Should switch to A's EXPAND state for consistency (separate change) |
| K7 | R-03 (WALCL − TGA − RRP) and R-04 (securities flow − issuance) already read balance-sheet flows; R-66 counts R-14 and R-02/03/04 as separate families | B overlaps R-03 (B2) or R-04 (B1) more than A does; A adds information (programme regime) the flow rules lack |
| K8 | Emergency lending (2008, 2023) | A ignores it (0); FF carries 2008. Row 26 suggests it counts; effect in 2023 would only move bs from +1 toward 0 during Mar-May 2023 |
| K9 | Pre-2008 / era B | A: NONE throughout (no programmes); 1932 open-market purchases and 1940s yield cap not modelled (gap) |

## 6. Recommendation

Design A (announced programme regime), with the QE-end setback flag re-based on EXPAND → NONE transitions.

Reasoning:
1. His statements are regime-shaped: stimulus "on/off" (rows 2-4), QE "turns to" QT (row 17), stay long until the Fed tightens and watch the end of QE (row 8). None is a week-level flow comparison.
2. It removes all three known defects without a single new constant: 2004-06 and 2008 fall to the FF component; 2009-2014 is continuously easing through taper phases, matching rows 1, 7-9 and the retrospective row 24.
3. It is the only design that captures Operation Twist as stimulus (row 2) and treats reserve-management purchases the way the FOMC itself classified them.
4. PIT is exact: statement release times are published, the event table is small (≈35 rows, section 2) and fully cited to federalreserve.gov.
5. B needs three uncited constants under a full tunable cap, B1 keeps the 2008 defect and B2 creates a 2009 defect; C's materiality gate improves only 2025-04 .. 2025-11 and rests on one uncited constant and an uncited asymmetry.

Residual weakness: K4 (cuts with slowed QT read neutral, 2024-09 .. 2025-11). It belongs to the combination rule, not the holdings component, and needs an owner decision.

Owner decisions needed (A-D format; recommendation first):

Q1. Holdings component design.
- A. Design A, event regime (Recommended: regime-shaped evidence, no new constants, fixes all three defects).
- B. Design C, event regime with 1 % GDP runoff materiality.
- C. Design B2, WALCL flow/GDP with taper → 0.
- D. Design D, minimal repair of the current rule.

Q2. Combination rule (K4).
- A. Keep `sign(rate + bs)` now; treat K4 as a known conflict, revisit after the re-registered run (Recommended: within the scope of the R-14 holdings change; avoids a second simultaneous design change).
- B. Rate-primary: bs counts only when the FF component is 0.
- C. Sum, but `slowed` RUNOFF counts 0.

## 7. Unverified items and gaps

| Item | Status |
|---|---|
| Release times for statements 2008-2012 (≈14:15 ET; ≈12:30 ET at 2011-2012 press-conference meetings) and several 2013-2022 pages without a stated time | UNVERIFIED (from memory); all before 16:00 ET, so same-day PIT is unaffected |
| 2012-06-20 Twist extension amount (~$267bn) | UNVERIFIED |
| 2019-10 RMP pace (~$60bn/month) | UNVERIFIED (NY Fed statement not fetched) |
| 2025-12 RMP pace (~$40bn first month, start 2025-12-12) | Search snippet of NY Fed operating policy page; page not fetched |
| Final QE4 purchase date (≈2022-03-09) | UNVERIFIED |
| QE3 last purchase date (end-October 2014) | Month verified; day UNVERIFIED |
| 2025-10-29 MBS paydown reinvestment into bills | UNVERIFIED (summary did not state it) |
| 2013-05-22 / 2013-06-19 taper-talk communications | UNVERIFIED, not fetched |
| 2008 sterilisation magnitudes (TREAST ~$780bn → ~$480bn) and WALCL 2008-09 path | From memory; checkable in lake series |
| Flow/GDP figures in section 4a | Approximate arithmetic from announced paces, not computed from the lake |
| Druckenmiller statements on 2013 taper tantrum, 2019-10 RMPs, 2021-11 taper (contemporaneous), QT slowdowns 2019/2024/2025, QT end 2025, 2025-12 RMPs | None located in the library |
| Bills/notes split series (`WSHOBL`, `WSHONBNL`) | Not in catalogue or lake |
| `FOMC_CALENDAR` | Missing in the catalogue; Design A requires building it from section 2 |
