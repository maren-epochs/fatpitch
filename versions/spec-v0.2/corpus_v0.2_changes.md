# Corpus changes for spec-v0.2

Date: 2026-10-06. Scope: owner decisions of 2026-10-06 on the label audit (`spec\label_audit_2026-10-06.md`) and the turning-point source search (`library\research\turning_point_sources.md`). Nothing was committed or tagged.

Blindness. `spec\scoring.md`, the gate, turning-point and null code under `src\fatpitch\cases\`, and `results\` were not read. No turning points were computed, and no engine or null was run. Every label and target below was decided from sources before the re-seal. Three exposures are disclosed. (1) Opening `cases\HOLDOUT.yaml` for its episode list and `spec\HOLDOUT.md` for its re-seal log also showed their version-2 count blocks. (2) `tools\make_holdout.py` prints counts; its output went to a scratch file and only the non-gate lines were displayed. (3) After the re-seal, a failing assertion in `tests\test_corpus.py` printed one holdout Gate 1 count. All label decisions had been made by then.

Labeling rule. `regime_direction` is the monetary-policy stance as he read it at the information date (easing, neutral or tightening). It is not his prescription and not the later outcome. The label follows the thesis region; when the source states no read for that region, the corpus uses his stated US read (precedent: X-10, C22). Targets contain only what the source supports.

## 1. Summary of changes

| Case (seed) | Split (v3) | Change | Field(s) |
|---|---|---|---|
| `2018-12-17_pause-oped-2018` (C33) | holdout | Thesis rates/long/US and expression `rates_us` dropped; it is now a regime-only case | targets, notes |
| `2005-12-30_riding-policy-2005` (C14) | research | Regime null → easing; citation widened | regime, citation, notes |
| `2006-12-29_left-the-party-2006` (C15) | research | Regime tightening → null | regime, citation, notes |
| `2022-03-07_hold-front-end-short-process-2022` (C44) | holdout (EP17) | Regime tightening → easing; Sohn 2022 cited | regime, citation, notes |
| `2026-09-10_ai-trim-fx-short-2026` (C56) | research | Regime null → easing | regime, notes |
| `1999-12-31_internet-short-process` → `1999-02-26_internet-short-process` (C09) | research | Re-dated (owner choice: late February 1999) | asof, id, date_basis |
| `2016-05-04_endgame-gold-2016` (C29) | research | Cites the archived full Sohn 2016 text; reliability secondary → primary; notes quote it | citation, reliability, notes |
| `2021-02-26_short-usd-goldman-2021` → `2021-02-05_short-usd-goldman-2021` (X-08) | holdout (EP17) | Cites Talks at GS; regime null → easing; theses + rates/short/US and commodity/long; action hold; reliability secondary → near-primary; re-dated | all targets, asof, id |
| `2014-06-19_asset-rich-income-poor-2014` (X-13) | research | New (regime-only, easing) | new |
| `2023-05-01_fiscal-horror-show-2023` (X-14) | holdout (EP19) | New (regime-only, tightening) | new |
| `2024-10-02_grants-gold-argentina-japan-2024` (X-15) | research | New (easing; gold, Argentina, Japan) | new |
| Talks at GS, Jan 2021 | — | Not added as a separate case: same event as X-08, which it upgrades | — |
| Sohn 2016 full transcript | — | Not added as a separate case: same event as C29, which it enriches | — |
| `library\discovered_sources\2016-05-04_sohn-the-endgame.md` | library | Reversed PDF links corrected; "Volcker and Bernanke" corrected to "Volcker and Greenspan"; correction note added | note |

Counts: 71 cases (68 + 3 new; 2 re-dated files replace their old ids), 20 episodes. After the re-seal (version 3): 48 research and 23 holdout cases; 13 research and 7 holdout episodes.

## 2. C33: the December 2018 op-ed with Warsh (research item 1)

### What the op-ed says

Title "Fed Tightening? Not Now" (WSJ Opinion, online Sunday 2018-12-16, print 2018-12-17, co-authored with Kevin Warsh). The full WSJ text was not reachable: the WSJ and Hoover pages return 401, and no syndicated full text was found. Verbatim passages come from coverage that quotes it:

| Passage (≤2 sentences) | Where quoted |
|---|---|
| "We believe the U.S. economy can sustain strong performance next year, but it can ill afford a major policy error, either from the Fed or the rest of the administration. Given recent economic and market developments, the Fed should cease—for now—its double-barreled blitz of higher interest rates and tighter liquidity." | CNBC 2018-12-17, https://www.cnbc.com/2018/12/17/stanley-druckenmiller-says-fed-must-pause-because-the-economy-can-ill-afford-a-major-policy-error.html |
| "The Fed should stop this option-limiting exercise entirely. And if data dependence is the Fed's new mantra, it should actually incorporate recent data into its forthcoming policy decision." | same |
| "The time to be dovish was when the crisis struck, and the economy needed extraordinary monetary accommodation. The time to be more hawkish was earlier in this decade, when the economic cycle had a long runway..." | ETF Trends / Validea (republished by Fox Business 2019-02-12), https://www.etftrends.com/equity-etf-content-hub/drunkenmiller-and-warsh-perspective-on-fed-tightening/ |
| "No ocean is large enough to insulate the U.S. economy from slowdowns abroad." | same |

What he meant. The op-ed reads the Fed's stance at the information date as a double tightening: rate hikes plus balance-sheet runoff, with global QE turning into global QT ("that was more than offset by other central banks' still-growing asset purchases," ETF Trends summary). It calls the timing wrong because ex-US growth and trade were slowing and US cyclicals and banks were falling. It prescribes a pause ("for now"), not cuts, and it criticizes the Fed for not hiking earlier in the decade. On the corpus rule, his read is tightening, so the label is kept. The pause is a prescription and is not coded.

### Is a position stated on or before the as-of (2018-12-17 16:00 ET)?

| Source | Date | Position content | Usable for C33? |
|---|---|---|---|
| WSJ op-ed | 2018-12-16/17 | None. Policy advocacy only | No position |
| Real Vision with Sokoloff (`RS/2018-09-06_sokoloff-real-vision-interview.md`) | filmed 2018-09-06 | Global QE going to zero as a headwind for equities; long Google; retail/staples shorts against tech longs. No Treasury position | No bond position |
| Grant's Fall 2018 (`DS/2018-10-09_grants-fall-conference-jim-grant.md`) | 2018-10-09 | "It's all about liquidity, and liquidity is going down"; notes snippet "We are going to higher interest rates" (not verbatim) | Points away from a long-rates position in October |
| Bloomberg TV with Schatzker (`DS/2018-12-18_bloomberg-tv-erik-schatzker.md`) | 2018-12-18 | "This time, Druckenmiller said he owns two-, five- and 10-year Treasuries." He "has been buying U.S. Treasuries on the expectation that yields will keep dropping" (Bloomberg article, below) | After the as-of |

The Treasury position is first stated in the 2018-12-18 Bloomberg interview: "Even Stan Druckenmiller Doesn't Know Where Markets Go Next," https://www.bloomberg.com/news/articles/2018-12-18/even-stan-druckenmiller-doesn-t-know-where-markets-go-next (syndicated text read at https://www.thewealthadvisor.com/article/even-stan-druckenmiller-doesnt-know-where-markets-go-next; video clip "Druckenmiller Says 'Even at These Yields, I Like Treasuries'," https://www.bloomberg.com/news/videos/2018-12-18/druckenmiller-says-even-at-these-yields-i-like-treasuries-video). One quote from it: "If the Fed tightens policy too much and is forced to reverse course, 'it's not inconceivable to me at all that the 2-years are back to 50 to 60 basis points in a couple of years.'" The interview aired one trading day after the as-of. The library note on it was written before this text was found and says no positions could be verified.

Decision: drop the thesis (rates/long/US) and the expression (`rates_us`). C33 is now a regime-only case (`tightening`, action null), like X-06. Reason: no source dated on or before the as-of states a position, and the only earlier rates comment (Grant's, October) points the other way. The 2018-12-18 Treasury long is real, but it belongs to a later information date. Coding it at a new 2018-12-18 case is open for the owner. `REJECTED` in `tools\build_cases_v2.py` now records that option instead of calling the Bloomberg interview "already cited."

### What contemporaneous and later commentators said

| Commentator (date) | What it said about the op-ed or its positioning implication | URL |
|---|---|---|
| Bloomberg News (2018-12-17) | Urged the Fed to pause its "double-barreled blitz" of higher rates and tighter liquidity "when economies are slowing and markets are falling." No positioning inference | https://www.bloomberg.com/news/articles/2018-12-17/druckenmiller-urges-fed-to-pause-tightening-blitz-in-wsj-op-ed (archived BloombergQuint copy read) |
| CNBC (2018-12-17) | Reported that the indicators suggest the economy "might need some monetary accommodation," and set it against market pricing (78% odds of a hike on 12-19). No positioning inference | CNBC URL above |
| Bloomberg News (2018-12-18) | Tied the op-ed to his book: he prefers owning Treasuries when the Fed may have to cut, owns 2s/5s/10s, is short "all the financials" and long cloud names | Bloomberg / WealthAdvisor URLs above |
| Republished market commentary (ugebrev.dk flash news, repost of a US market blog, Dec 2018) | Said he argued "that Trump has a point" and that the Fed "already missed its opportunity to safely tighten." Read his positioning as "owning the front end of the Treasury curve will pay off if the Fed is forced to reverse course." Relies on the 12-18 interview | https://ugebrev.dk/flashnews/investering/de-bedste-oekonomer-jeg-kender-siger-at-der-er-noget-galt/ |
| ETF Trends / Validea (republished 2019-02-12) | Summary of the argument: global QT, timing "could scarcely be worse." No positioning inference | ETF Trends URL above |
| Tim Duy, Fed Watch (2018-12-18) | Described the Fed as "stuck in an uncomfortable situation" (weak equities, solid data, presidential pressure). The op-ed is not mentioned | https://blogs.uoregon.edu/timduyfedwatch/2018/12/18/fed-stuck-in-an-uncomfortable-situation/ |
| Gryning Times (2020-09-10, retrospective) | Says he was "on red alert" in early December 2018 as Fed hikes and the end of ECB QE coincided. No source given for the phrase; the closest verbatim is the 12-18 "not red yet, but... definitely amber" | https://thegryningtimes.substack.com/p/drunkenmiller-and-liquidity |
| Employ America (2026, retrospective) | Political-consistency critique of Warsh: in 2018, with inflation at target and unemployment at 3.7%, he "rushed to the pages of the Wall Street Journal to call for an end to any prospect of tightening." No positioning inference | https://www.employamerica.org/monetary-policy/kevin-warsh-the-words-of-today-or-the-deeds-over-decades/ |
| Rudy Havenstein (2026-08-24, retrospective) | Cites the op-ed as evidence that "Warsh isn't hawkish." No positioning inference | https://rudy.substack.com/p/a-time-for-choosing |

Gaps: no contemporaneous Reuters, FT, MarketWatch or academic-economist commentary on the op-ed was found (several searches, including "talking his book"). No commentator dated on or before 2018-12-17 linked the op-ed to a position of his.

## 3. C15, C44, C14, C56 (research item 2)

| Case | Old → new label | Strongest text found (≤2 sentences) | Source | Reasoning |
|---|---|---|---|---|
| C15 `2006-12-29_left-the-party-2006` | tightening → **null** | "'06 I stunk. I had made some money but I left the party." / "My returns weren't very good in '06 because I was a little early." / "'06, I was wrong for six months, it drove me crazy." | DA 2014 CNBC transcript; Lost Tree gist OCR; Sohn 2022 transcript (A Letter a Day) | None of the three texts states his read of 2006 policy. The tightening label rested on Kernen's "until they raise rates you're going to dance" line, which is the host's framing of 2014. Under the rule, no direct statement means null. The exit target is kept. |
| C44 `2022-03-07_hold-front-end-short-process-2022` | tightening → **easing** | "I thought they were slow, not recognizing it in April of 21. But they were still buying bonds in March of 22." | Sohn 2022 with Collison, transcript (DS/2022-06-XX_sohn-2022-john-collison.md; https://aletteraday.substack.com/p/letter-40-john-collison-and-stan) | His read of the stance in March 2022 was still-loose policy: QE still running and no hike yet. The old label matched the rule's mechanics (hike imminent) and the audit flagged it. The notes now say the label is his retrospective read. The same transcript supports the held short ("a matrix of short fixed income, short stocks" over "the last six or eight months"). No contemporaneous statement exists (`turning_point_sources.md` §1c). Confidence medium. |
| C14 `2005-12-30_riding-policy-2005` | null → **easing** | "I made a lot of money in '05 because I wanted to ride the overly aggressive policy." / "At the 2005 Ira Sohn Conference, looking at a more muted but similar deviation, I argued that the Greenspan Fed was sowing the seeds of an historical housing bubble..." | DA 2014 transcript; Sohn 2016 prepared text (archived note); Lost Tree ("engendered by the Federal Reserve's too-loose monetary policy," figured out "by mid-'05") | Three texts state his 2005 read: policy too loose ("overly aggressive," a dovish Taylor deviation). The read is retrospective, but its content is dated to 2005 (Sohn 2005 talk, mid-2005 analysis). Corpus convention codes too-loose as easing (C13, X-12). Confidence medium. |
| C56 `2026-09-10_ai-trim-fx-short-2026` | null → **easing** | US rates "at best too low"; rate cuts "no longer necessary"; claims policy is restrictive are "absurd." | FT report via aggregators (DS/2026-09-10_piper-sandler-closed-door-event.md) | His only stated policy read is the Fed's, and it is too loose. The FX theses (short EUR, GBP) have no ECB or BoE read. The case's action (reduce US AI equities) is a US expression, and the corpus uses the US read when the thesis region has none (X-10, C22). No transcript exists, so reliability stays secondary. Confidence medium-low. |

## 4. C09 date (item 3)

| Field | Old | New |
|---|---|---|
| id / file | `1999-12-31_internet-short-process` | `1999-02-26_internet-short-process` |
| asof | 1999-12-31 16:00 ET | 1999-02-26 16:00 ET (last NYSE trading day of February 1999) |
| date_basis | "notes date the internet short only to 1999" | Lost Tree "about February" 1999; Feig and Sohn 2022 give "March of '99"; February chosen by owner decision 2026-10-06 |

Source quotes: "I put 200 million in them in about February and by mid-march the 200 million short I had lost $600 million on" (Lost Tree). "sometime I believe in like, March of 99, I got the brilliant idea to short like 10 Internet stocks" (Sohn 2022). Targets are unchanged (process case, rule output flat).

## 5. Citation upgrades and new cases (item 4)

| Case | Source | Key quote (≤2 sentences) | Targets | Date basis |
|---|---|---|---|---|
| C29 `2016-05-04_endgame-gold-2016` (enriched) | `DS/2016-05-04_sohn-the-endgame-archived-transcript.md` (primary) + old note | "Simply put, this is the biggest and longest dovish deviation from historical norms I have seen in my career." / gold "remains our largest currency allocation." | Unchanged: easing; gold long; US equity short; hold | Unchanged (pinned) |
| X-08 `2021-02-05_short-usd-goldman-2021` (upgraded) | `DS/2021-01-XX_talks-at-gs-great-investors-pasquariello.md` (TIE Winter 2021 adaptation, read in full) | "Basically, to play potential inflation, I have a short Treasury position, primarily at the long end." / "...I have a very, very short dollar position." | easing; fx/short/USD, rates/short/US, commodity/long; expression fx_usd, rates_us, commodity_global; hold | Recorded "late January 2021"; first dated publication 2021-02-06 (Saturday); asof 2021-02-05 close, the last trading day before publication and certainly after recording |
| X-13 `2014-06-19_asset-rich-income-poor-2014` (new) | `DS/2014-06-19_wsj-oped-warsh-asset-rich-income-poor.md`; Hoover repost read in full | "Extraordinarily loose monetary policy will continue in force." / "The sooner and more predictably the Fed exits its extraordinary monetary accommodation, the sooner businesses can get back to business..." | easing; regime-only (no position) | Pinned: WSJ 2014-06-19; the text refers to the FOMC meeting "earlier this week" (June 17–18) |
| X-14 `2023-05-01_fiscal-horror-show-2023` (new) | `DS/2023-05-01_tie-spring-2023-coming-fiscal-horror-show.md`; TIE PDF read | "In an attempt to correct the biggest mistake in Fed history, the Fed in the last year has raised rates 500 basis points. Better late than never." | tightening; regime-only | Pinned to the USC keynote 2023-05-01. The printed issue cites the June 2023 CBO outlook (a figure), so only the policy read is coded. The 500bp figure also appears at NBIM on 2023-04-24 (C47), so it is not post-speech information |
| X-15 `2024-10-02_grants-gold-argentina-japan-2024` (new) | `DS/2024-10-01_grants-fall-conference-2024.md`; HFA teaser and Hedgeweek read | Fed "has taken a reckless monetary gamble with overtly reflationary policies" (HFA paraphrase); "he owns gold but not gold miners" (Hedgeweek, via Barron's) | easing; commodity/long/GOLD, equity/long/AR, equity/long/JP; hold | Conservative: HFA gives 2024-10-01, Hedgeweek 2024-10-02; later date used |

Not added: Talks at GS is the same event as X-08, and the Sohn 2016 transcript is the same event as C29. Three new cases were added instead of five. Episodes follow existing naming: EP12-2014-15-DIVERGE, EP19-2023-RATES and EP20-2024-CUT; X-08 stays in EP17-2021-MANIA. COHR and the Taiwan/Korea/China single names are not coded (single names, not market theses).

Library correction: `2016-05-04_sohn-the-endgame.md` now labels `The_EndGame.pdf` as the slide deck and `The_Endgame_Sohn.pdf` as the prepared text (they were reversed). The Taylor benchmark now reads "an average of Volcker's and Greenspan's response to data," and a correction note points to the archived-transcript note. In this session web.archive.org returned a Squarespace 404 page for the PDF, so the C29 quotes rely on the archived-transcript note's full-text reading.

## 6. Application (item 5)

| Step | Result |
|---|---|
| `cases\UNSEAL_LOG.txt` before the re-seal | Absent |
| Generators | `tools\build_cases.py` (C09, C14, C15, C29, C33, C44, C56; constants `SOHN16`, `SOHN22`) and `tools\build_cases_v2.py` (X-08; new X-13 to X-15; `REJECTED` updated). Old ids `1999-12-31_internet-short-process` and `2021-02-26_short-usd-goldman-2021` deleted |
| Byte check | Regenerating all 69 non-13F cases into a scratch directory matches `cases\` byte for byte. Case files are CRLF; `build_cases.py` stays LF and `build_cases_v2.py` stays CRLF |
| Re-seal | `tools\make_holdout.py --reseal --reason "spec-v0.2 corpus corrections (owner decisions 2026-10-06); holdout never opened"` → version 3, created 2026-10-06T21:01:57Z |
| Manifest | `python -m fatpitch.prereg manifest`: 71 cases, 20 episodes, corpus_sha256 `7117930e54ff4518b362431157958ac0c473eae1da50486bce6c9e89b064e904` |
| Docs | `spec\HOLDOUT.md` (v3 draw, counts written by script, hashes, re-seal row and paragraph); `spec\PREREG.md` (pending snapshot, v3 seal paragraph, null-run disclosure); `spec\cases_seed.md` (v0.2 corrections table) |

| Version | Holdout episodes | Cases holdout / research / all | Holdout files sha256 | `HOLDOUT.yaml` sha256 |
|---|---|---|---|---|
| 2 | EP07, EP09, EP11, EP14, EP15, EP16, EP18 | 26 / 42 / 68 | `9d33be6b3a853f7d6b54df94c5aa2c3e1d6634329cc76af0316f0a26e5f54c1b` | `49e48edb139e65a675f9e9617cd578117e5831cfcfb0e9df5081d9331dfda2b8` |
| 3 | EP02, EP07, EP10, EP14, EP16, EP17, EP19 | 23 / 48 / 71 | `e2a0f283c1cee71d7360525c51a3406993056a7d4aafff16e2c2fbfcda4152fd` | `f72f81a2d52d1bb18ed49cca2e0ceb1d5fdf1c913e26a342089b73a1b3c0e079` |

Consequences for the owner:

- Four episodes left the holdout (EP09, EP11, EP15, EP18) and are now research. Their targets were sealed but never loaded by an engine.
- Four entered (EP02, EP10, EP17, EP19). The unlogged null run of 2026-10-06T20:17Z covered all four as research episodes, and the best-null choice was made with them in view (`spec\PREREG.md`).
- X-08, C44 and X-14, edited or added in this step, sit in the v3 holdout. They were decided from sources only.

## 7. Tests

`pytest -q`: 170 passed, 1 failed. The failure is `tests\test_corpus.py::test_turning_points_derived_from_targets`, the assertion `counts["holdout"]["gate1_cases"] >= 5` (the `spec\HOLDOUT.md` power check). The v3 holdout falls below that threshold. Meeting it would need a design decision: change the threshold, add Gate 1 cases from new sources, or accept a smaller holdout Gate 1. Changing labels to reach it would be outcome-driven and was not done. `ruff check src tests`: clean.

## 8. Addition 2026-10-07: the 2018-12-18 Treasury long as its own case (X-16)

Owner decision 2026-10-07: code the Treasury long first stated in the 2018-12-18 Bloomberg TV interview (section 2) as a separate case. C33 is unchanged (regime-only).

Blindness. `spec\scoring.md`, gate, turning-point and null code, and `results\` were not read, and no turning points were computed. Two exposures are disclosed. (1) While checking the allowed target vocabulary in `src\fatpitch\cases\schema.py`, a grep output also showed the lines that define turning-point membership from action targets. The action label (hold) had already been chosen from the source before that output was seen, and it was not changed. (2) `spec\HOLDOUT.md` shows the non-gate count rows (thesis-target, truth type, mechanizable, reliability) of the v4 block when its diff was reviewed. The gate and turning-point rows were written by script and not displayed, and `make_holdout.py` output went to a scratch file filtered to version, hashes and case/episode counts.

| Field | Value | Basis |
|---|---|---|
| id | `2018-12-18_treasury-long-bloomberg-2018` (seed X-16, `tools\build_cases_v2.py`) | |
| asof | 2018-12-18 16:00 ET | Bloomberg News article on the interview published 2018-12-18 09:00 UTC (04:00 ET, page metadata), before the open. The interview aired the same day; air time unverified. The positions were public before that close whatever the broadcast time |
| episode | `EP14-2018-QT` (holdout) | |
| regime_direction | tightening | Urged the Fed to hold off the 2018-12-19 hike; "You want this bubble to unwind slowly now"; same read as the 2018-12-16 op-ed (C33) |
| theses | rates/long/US | "Druckenmiller said he owns two-, five- and 10-year Treasuries"; "it's not inconceivable to me at all that the 2-years are back to 50 to 60 basis points in a couple of years" |
| expression | `rates_us`, `equity_us_financials` | Financials leg stated: "he has been short 'all the financials,' including banks." The thesis vocabulary has no sector region, and an equity/short/US thesis would misstate a sector short by someone who says he avoids shorting the market ("you get squeezed out of shorts"), so the leg is coded in the expression only |
| action | hold | He states ownership. The article's "has been buying U.S. Treasuries" is the reporter's summary with no entry date, and no earlier source states the long (section 2), so `enter` is not supported by a dated entry |
| size_band | none | Not stated |
| reliability | secondary | News article with direct quotes; the video and any transcript were not accessed (library note: `secondary summary`, access now `partial`) |
| not coded | Long cloud names (MSFT, CRM, NOW, WDAY) | Single names (convention of X-08, X-15) |

Source: "Even Stan Druckenmiller Doesn't Know Where Markets Go Next," https://www.bloomberg.com/news/articles/2018-12-18/even-stan-druckenmiller-doesn-t-know-where-markets-go-next; full text read in the syndicated copy https://www.thewealthadvisor.com/article/even-stan-druckenmiller-doesnt-know-where-markets-go-next. The library note `library\discovered_sources\2018-12-18_bloomberg-tv-erik-schatzker.md` was updated with these quotes and URLs, and its `_index.md` row now reads `partial`. `REJECTED` in `tools\build_cases_v2.py` no longer lists the interview.

| Step | Result |
|---|---|
| Generator | `tools\build_cases_v2.py` (CRLF kept). Regenerating all 70 non-13F cases into a scratch directory matches `cases\` byte for byte; the new case file is CRLF |
| `cases\UNSEAL_LOG.txt` before the re-seal | Absent |
| Re-seal | `tools\make_holdout.py --reseal --reason "spec-v0.2: add 2018-12-18 Treasury-long case (owner decision 2026-10-07); holdout never opened"` → version 4, created 2026-10-07T05:35:12Z. Episodes unchanged from v3 |
| Manifest | `python -m fatpitch.prereg manifest`: 72 cases, 20 episodes, corpus_sha256 `bd2c44cbc91ffdd1bece3f1a4c1469a5f677869f4fc7d4f58c23ca68b6c6c1c1` |
| Docs | `spec\HOLDOUT.md` (v4 draw, script-written counts, hashes, re-seal row and paragraph); `spec\PREREG.md` (snapshot recomputed 2026-10-07T05:36:59Z, v4 seal paragraph); `spec\cases_seed.md` (X-16 row) |

| Version | Holdout episodes | Cases holdout / research / all | Holdout files sha256 | `HOLDOUT.yaml` sha256 |
|---|---|---|---|---|
| 3 | EP02, EP07, EP10, EP14, EP16, EP17, EP19 | 23 / 48 / 71 | `e2a0f283c1cee71d7360525c51a3406993056a7d4aafff16e2c2fbfcda4152fd` | `f72f81a2d52d1bb18ed49cca2e0ceb1d5fdf1c913e26a342089b73a1b3c0e079` |
| 4 | EP02, EP07, EP10, EP14, EP16, EP17, EP19 | 24 / 48 / 72 | `891120244c786d0b3cb90bf290a5085b26b4975ea6374adcf25a929260913269` | `ed247f26f81a3fbf93b263b9aff77cec0a8f64b3bbb43399e63b2a86c78cf1f3` |

Research files sha256 unchanged (`cbc5936cac10280066e0c8fdd2a55175a1bf4b93a8a38b8e593bb8d46c206fb3`).

Tests: `pytest -q` 180 passed (including the holdout power test); `ruff check src tests` clean.
