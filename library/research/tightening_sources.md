# Tightening and neutral policy-read source search

Search date: 2026-10-07. Scope: search and report only. No files in `cases/` or `spec/` were changed, and `spec/scoring.md`, `spec/HOLDOUT.md`, `cases/HOLDOUT.yaml` and `results/` were not opened. Three new library notes are in `library/discovered_sources/`, appended to its `_index.md`.

Method: about 30 WebSearch queries in extended mode, WebFetch, and curl with a browser user agent. Two book sources were read directly. The New Market Wizards chapter came from an openly downloadable archive.org OCR text, read in full. The Lost Tree 2015 transcript came from a GitHub gist; its Fed passages were read. Each URL got at most two attempts. Before searching, `discovered_sources/_index.md`, `reference_sources/_index.md` and `research/turning_point_sources.md` were read to avoid duplicates.

Definitions (same convention as `turning_point_sources.md`):
- "Policy read" is his read of the stance at the information date, inferred from his words. It is not his prescription and not a Fed action. tightening = policy tight or being tightened. easing = loose or loosening. neutral = neither, in his words.
- Contemporaneous = said at or near the information date. Retrospective = a later account of a past read, flagged in the C/R column.
- Reliability: primary = his own text or a full book/transcript text. Near-primary = transcript of speech or interview. Secondary = press summary or relay.
- "Existing case?" is judged by filename date only (cases/ filename list). Case targets were not read.

## 1. Finds by target period

Column key: Pin = information date pinned (day / month / quarter / no). C/R = contemporaneous / retrospective.

### 1a. 1981 (outside the target list; found in the same book text)

| Info date | Source | Reliability | Read | Thesis / action | Quote (≤2 sentences) | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| mid-1981 (June) | Schwager, New Market Wizards, interview Dec 1991 ([note](../discovered_sources/1992-XX-XX_new-market-wizards-full-chapter-text.md)) | primary (book text) | tightening (rates at 19%) | US equities bearish; 50% cash; "unbelievably bearish in June 1981" | "By mid-1981, stocks were up to the top of their valuation range, while at the same time, interest rates had soared to 19 percent. It was one of the more obvious sell situations in the history of the market." | month (June 1981) | R (10 yrs) | No (1981-12-31 is the Q4 bond trade) |
| Q4 1981 | same | primary | tightening ("extremely tight") | 50% cash, 50% long bonds | "We loved the long bond position because it was yielding 15 percent, the Fed was extremely tight, and inflation was already coming down sharply." | quarter | R | Yes (1981-12-31) |

### 1b. 1987 (pre-crash tightening)

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| June 1987 | New Market Wizards (Dec 1991 interview) | primary | tightening | Switched from bullish to net short US equities. Valuation (2.6% dividend yield, record P/B) set the magnitude; liquidity plus narrow breadth set the timing | "The Fed had been tightening since January 1987, and the dollar was tanking, which suggested that the Fed was going to tighten some more." | month | R (4.5 yrs) | No |
| 1987-10-16 | same | primary | (no new read) | Reversed to 130% long on technical support; sold in the first hour of 10-19 and went short | "On Friday afternoon, October 16, 1987." | day | R | No. The action contradicts the June read; it is a technical override, not a policy-read change |

### 1c. 1988–89

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| 1988-03-28 | Barron's "Still Bearish" (via Frederik Gieschen on X; HFA walled) | secondary (fragment) | none dated. Framework only: the Fed turns from ally to tightener once the economy accelerates | Bearish US equities | "The major thing we look at is liquidity, meaning as a combination of an economic overview and how the Fed is responding to that economic situation." | day | C | Yes (1988-03-28). No policy read recovered |
| Aug 1989 | New Market Wizards | primary | not stated | Long bonds (Soros sold the position) | "Events came to a head in August 1989 when Soros sold out a bond position that I had put on." | month | R | No. No read; not a case candidate |
| late 1989 | New Market Wizards | primary | tightening (Bank of Japan, not the Fed) | Short Nikkei: "the best risk/reward trade I had ever seen" | "Finally, and most important—three times as important as everything I just said—the Bank of Japan had started to dramatically tighten monetary policy." | quarter | R (2 yrs) | No |
| Nov 1989 – early 1991 | New Market Wizards; Lost Tree 2015 | primary / near-primary | tightening (Bundesbank) plus expansionary fiscal | Long DEM vs USD | "The basic premise of the trade was that the Germans would adhere to a combined expansionary fiscal policy and tight monetary policy—a bullish combination for their currency." | month | R | Yes (1988-12-30, 1989-11-30) |

Related, outside the targets:
- Dec 1991 (contemporaneous, NMW). Read: easing, "the administration and the Fed in a state of panic." He was out of long bonds by late 1991. This is a dated contemporaneous read that has no case, but it is an easing read.
- Aug 1992 (Lost Tree, retrospective). Bundesbank "was raising rates like crazy." Sterling cases exist.

### 1d. 1994 (bond massacre)

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| none located | — | — | — | — | — | — | — | — |

Only secondary facts were found: the Quantum loss of about $600–650M on 1994-02-14, from a yen short plus long Japanese equities and short JGBs (Wikipedia list of trading losses; Encyclopedia.com SFM entry). Druckenmiller gave a press statement that the loss was "$600 million and no more." That is a statement about the loss, not a policy read. Mallaby's ch. 8 "Hurricane Greenspan" is the obvious source, but every archive.org copy is lending-restricted, search-inside returned "Item not available", the WSO book-club page returned 403, and the Google Books API was over quota. Fortune's "Great Bond Massacre" (1994-10-17) does not mention him. The only 1994 reference in his own words is the 1994–95 soft-landing example in Sohn 2022, a later historical analogy, not a read.

### 1e. 1999–2000 (Fed hikes; 2-year note trade)

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| spring 1999 | NBIM In Good Company 2024-11-06 (moomoo translated transcript; [ref note](../reference_sources/2024-11-06_nbim-in-good-company-podcast.md)) | near-primary | easing (Greenspan loose after the Asia crisis) | Covered internet shorts; went long tech | "Then I turned and realized that Greenspan had adopted loose Monetary Policy due to the Asian financial crisis, while the US economy was strong." (translated wording) | quarter | R | No direct case (1999-02-26 is the internet short) |
| Sep–Q4 2000 | Real Vision / Sokoloff 2018 (macro-ops notes); NBIM 2024; Citi 2009; Sohn 2022 | near-primary (several accounts) | tightening (hawkish speeches, tightening bias in place) | 300–350% of NAV in 10-year-equivalent 2- and 5-year Treasuries, added on each hawkish speech | "So I keep buying these treasuries, and Greenspan keeps giving these hawkish speeches, and they have a bias to tighten." / "...Greenspan's got a tightening directive on, which I think is inappropriate." | month (Sept 2000) | R | Yes (2000-09-29) |

### 1f. 2004–06

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| 2004 (during hikes) | Lost Tree 2015 (gist transcript) | near-primary | easing (still too loose despite hikes) | On alert; housing-bust thesis formed by mid-2005 | "I just have the same horrific sense I had back in '04. And by the way, it lasted another two years." | year | R | Related: 2003-12-31, 2005-12-30, 2006-12-29 |
| 2005 Sohn | Sohn 2016 text (existence only) | primary (reference) | easing (Greenspan Fed "sowing the seeds" of a housing bubble) | — | (see `turning_point_sources.md`) | no | R | 2005-12-30 exists |

No tightening read from 2004–06 was found. Every account frames the 2004–06 hiking cycle as still too loose. "Dance until they raise rates" is 2014 Delivering Alpha language, already the 2014-07-16 case, not a 2004–06 source.

### 1g. 2013 (taper tantrum)

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| none for May–Aug 2013 | — | — | — | — | — | — | — | — |

The 2013-05-08 Sohn talk ("damage comes when the Fed tightens") is conditional, not a read. The 2013-09-19 and 2013-11-22 items are easing reads, already cased or cataloged.

### 1h. 2015–18 (liftoff, QT)

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| Jul 2015 (claimed) | Search-engine summary only: "Delivering Alpha July 2015... golden opportunity" | unverified | easing (prescribes hike) | — | The "golden opportunity" quote traces to CNBC 2015-03-02 | no | — | 2015-03-02 exists. Rejected as a separate event |
| 2016-11-29 | Robin Hood with PTJ (Scribd 894505140; AI abstract only) | secondary teaser | unverified: "direction of interest rates," rising rates | Rates-up bet | none accessible | day (event) | C | No. Conditional, as before |
| 2018-05-03 | Manhattan Institute Hamilton Award remarks ([note](../discovered_sources/2018-05-03_manhattan-institute-hamilton-award-speech.md)) | primary | easing (rates below inflation; not normalized) | none | "...years after the Great Recession ended the Fed has not only kept interest rates below inflation but have accumulated an unprecedented $4.5 trillion on their balance sheet by doing QE." | day | C | No. New dated read, but easing |
| 2018-09 | Real Vision / Sokoloff | near-primary | tightening ("early in a monetary tightening", QE shrinkage) | Bearish equities; "dead wrong" for 2–3 months | "Interestingly, some of the things that tend to happen early in a monetary tightening are responding to the QE shrinkage." | month | C | Yes (2018-09-06) |
| 2018-10-09 | Grant's Fall 2018 ([note](../discovered_sources/2018-10-09_grants-fall-conference-jim-grant.md)) | secondary (HFA notes, non-verbatim) | tightening ("liquidity is going down") | Risk-off warning; "higher interest rates" | "It's all about liquidity, and liquidity is going down." | day | C | **No** |
| ~2018-11-21 | WSJ interview via ForexLive ([note](../discovered_sources/2018-11-21_wsj-interview-risky-to-be-tightening.md)) | secondary (relay) | tightening (QE turning to QT) | Late cycle; Fed should pause | "As quantitative easing turns to quantitative tightening, all these zombies are going to be exposed." | day (±1) | C | **No** |
| 2018-12-16 / 12-18 | WSJ op-ed; Bloomberg Schatzker | primary / secondary | tightening ("double-barreled blitz") | Pause; long Treasuries | (in existing notes) | day | C | Yes (2018-12-17, 2018-12-18) |
| 2019-06-03 | ECNY with Bessent (gurufocus 2019-06-18) | secondary | tightening, read about Dec 2018 | — | "Since the founding of the Fed in 1913, they have never raised rates with the magnitude of decline we saw at the end of 2018" | day | R | Covered by the Dec 2018 cases |

### 1i. 2022–23 (hiking)

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| Nov 2021 – Mar 2022 | none located (as in the 2026-10-06 search) | — | — | — | — | — | — | — |
| 2023-06-07 | Bloomberg Invest, Fortune quotes ([note](../discovered_sources/2023-06-07_bloomberg-invest-sonali-basak.md)) | secondary (direct quotes) | tightening (500bp in a year after the bubble) | Hard landing; "more shoes to drop"; AI dominates long book | "The biggest broadest asset bubble ever, and then you jack interest rates up 500 basis points in a year… Silicon Valley Bank, Bed Bath & Beyond, they're probably the tip of the iceberg." | day | C | **No** |
| late 2023 | CNBC 2024-05-07 transcript | near-primary | tightening (financial conditions tightening before the Dec 2023 pivot) | Two-year long; exited after the pivot | (in existing note) | month | R | Yes (2023-10-24, 2023-12-28) |

All other 2022–23 tightening reads found (Sohn 2022, Delivering Alpha 2022-09-28, NBIM 2023-04-24, USC/TIE 2023-05-01, Sohn 2023-05-09, CNBC 2023-11-01) already have cases by filename date.

### 1j. 2025–26

| Info date | Source | Reliability | Read | Thesis / action | Quote | Pin | C/R | Existing case? |
|---|---|---|---|---|---|---|---|---|
| none tightening | — | — | — | — | — | — | — | — |

The 2026 reads located are easing reads: FT 2026-01-30, and Piper Sandler 2026-09-10 ("Committee members on the Fed who keep saying fed funds rates are restrictive are just ridiculous"). Both have cases. No Druckenmiller statement after the 2026-09-16 Warsh hike was found. Robin Hood 2026-10-21 is in the future.

## 2. Counts

Plausible new tightening-read cases (no case at that filename date):

| # | Info date | Source | Reliability | C/R | Strength |
|---|---|---|---|---|---|
| 1 | June 1987 | New Market Wizards | primary | R | Strong: explicit read, explicit action (net short), month-pinned |
| 2 | mid-1981 (June) | New Market Wizards | primary | R | Medium: read is implied by "rates had soared to 19 percent", not a word about the Fed; action is 50% cash |
| 3 | late 1989 | New Market Wizards | primary | R | Medium: explicit read, but of the Bank of Japan, not the Fed. Use only if the corpus regime field accepts non-Fed central banks |
| 4 | 2018-10-09 | Grant's Fall 2018 | secondary (non-verbatim notes) | C | Medium: headline-level quote only |
| 5 | ~2018-11-21 | WSJ via ForexLive | secondary relay | C | Medium: direct quotes; WSJ original not read |
| 6 | 2023-06-07 | Bloomberg Invest (Fortune) | secondary (direct quotes) | C | Medium-strong: direct quotes, day-pinned |

Total: 6 plausible new tightening-read cases, 3 retrospective and 3 contemporaneous. Excluding the BoJ case leaves 5 Fed-specific ones. The three 2018 items (09-06 existing, 10-09, 11-21, plus 12-17/12-18 existing) would make a dense cluster with the same read. They add count but little independent information.

Conditional (content inaccessible): 2 (Robin Hood 2016-11-29; any 1994 read in Mallaby ch. 8).

Plausible new neutral-read cases: **0**. No source uses neutral language about the stance. He calls policy either too loose (most of 2003–2021 and 2024–26) or tightening (1981, 1987, 2000, 2018, 2022–23).

New dated non-tightening reads found as a by-product: 2 easing reads, both without cases: December 1991 (NMW, contemporaneous, "Fed in a state of panic") and 2018-05-03 (Manhattan Institute, primary).

## 3. Existing library notes with usable tightening reads not yet turned into cases

Judged by matching note dates against the `cases/` filename list only.

| Note | Read | Usable? |
|---|---|---|
| `discovered_sources/2018-10-09_grants-fall-conference-jim-grant.md` | tightening ("liquidity is going down") | Yes, secondary |
| `discovered_sources/2023-06-07_bloomberg-invest-sonali-basak.md` | tightening (500bp after the bubble) | Yes, secondary with direct quotes |
| `discovered_sources/1992-XX-XX_new-market-wizards-schwager-chapter.md` (and the new full-text companion) | tightening 1981, 1987; BoJ 1989 | Yes. The tightening passages are only in the new full-text note; the old note had only the excerpt |
| `discovered_sources/2019-06-03_econclub-ny-bessent.md` | tightening, read retrospectively about Dec 2018 | Redundant with the 2018-12-17/18 cases |
| `reference_sources/2015-01-18_lost-tree-club-speech.md` | Bundesbank tightening 1992; Volcker 1981 | Already covered by the 1992 and 1981 cases |
| `discovered_sources/2021-05-11_hustle-mfm-trung-phan.md`, `2013-05-08_sohn-commodities-conundrum.md`, `2014-07-16_delivering-alpha-kernen.md` | conditional ("when they tighten...") | No. These are conditional statements, not reads of the current stance |

## 4. Gaps that remain

- 1994: no Druckenmiller policy read from the year itself or recalled later. The only plausible source is Mallaby ch. 8, which needs a physical or licensed copy.
- 2004–06 and the 2013 taper tantrum: no tightening read exists in the located record. His accounts treat 2004–06 as still too loose.
- Nov 2021 – Mar 2022 and post-hike 2026: no contemporaneous statements located.
- Robin Hood 2016-11-29: content still walled.
