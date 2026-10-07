# Turning-point source search: Druckenmiller dated policy reads in corpus gaps

Search date: 2026-10-06. Scope: search and report only. No files in `cases/` or `spec/` were changed. New library notes are in `library/discovered_sources/` and appended to its `_index.md`.

Method: about 35 WebSearch queries in extended mode (English and Chinese), WebFetch, and curl (including web.archive.org `id_` raw captures). Each URL got at most two fetch attempts. Before searching, both source indexes were checked to avoid duplicating existing notes.

Assumption about `regime_direction`: the corpus field records Druckenmiller's read of the policy stance at the information date. "easing" means policy is loose or loosening, "tightening" means tight or tightening, "neutral" and null as defined in the cases. The read was inferred from his words, not from Fed actions. A "turning point" here means a dated era-A read whose regime differs from his previous dated non-null read within 18 months, as the task defines it.

Reliability labels: primary = his own text, or an event listing; near-primary = transcript or first-person adaptation; secondary = press summary or paraphrase.

## 1. Candidates by target period

### 1a. Late 2015 – early 2016 (Fed liftoff 2015-12-16)

| Date | Source | Reliability | Policy read | Thesis / action | Quote (≤2 sentences) | Day pinned |
|---|---|---|---|---|---|---|
| 2016-05-04 | Sohn 2016 "The Endgame", full prepared text, archived sohnconference.org PDF (`The_Endgame_Sohn.pdf`), [note](../discovered_sources/2016-05-04_sohn-the-endgame-archived-transcript.md) | primary (prepared text) | easing (too loose) | Equities (US/global) risk/reward negative; gold is the largest currency allocation | "Simply put, this is the biggest and longest dovish deviation from historical norms I have seen in my career." / "...the bull market is exhausting itself." / "...it remains our largest currency allocation." | yes |
| 2016-11-29 | Robin Hood Investors Conference fireside with Paul Tudor Jones. Date pinned by Robin Hood's past-agendas PDF (2016 agenda, Tue Nov 29); content per existing note `2016-XX-XX_robin-hood-paul-tudor-jones.md` | event: primary (agenda). Content: secondary teaser only | unverified. Teaser: "betting on rising interest rates" | US rates up / bonds short (HFA teaser), size unknown | No verbatim Druckenmiller quote accessible (Scribd and HFA are walled; Podwise has metadata only) | yes (event) |

No statement from Dec 2015 – Apr 2016 was located. Searches covering liftoff reaction, Jan–Apr 2016 interviews, China/yuan and negative rates returned only Sohn 2016 coverage and 2015 items already in the corpus (2015-03-02, 2015-04-15/16, 2015-11-04).

### 1b. H2 2019 (cuts 2019-07-31, 09-18, 10-30)

| Date | Source | Reliability | Policy read | Thesis / action | Quote | Day pinned |
|---|---|---|---|---|---|---|
| none new | — | — | — | — | — | — |

Only the 2019-12-18 Bloomberg/Schatzker interview, already in the corpus, was found. Its quote via moneyandmarkets.com is "We have negative real rates everywhere and negative absolute rates in a lot of places. With that kind of unprecedented monetary stimulus relative to the circumstances, it's hard to have anything other than a constructive view on the market's risk and the economy, intermediate term." The Robin Hood 2019 agenda (Oct 28–29) does not list him. A search-engine summary attributed "We shorted bonds the day the Fed cut 50" to September 2019. That quote is from his October 2024 Bloomberg interview and refers to the September 2024 cut, so it was rejected.

### 1c. Nov 2021 – Mar 2022 (taper, first hike 2022-03-16)

| Date | Source | Reliability | Policy read | Thesis / action | Quote | Day pinned |
|---|---|---|---|---|---|---|
| none located | — | — | — | — | — | — |

Every search for a contemporaneous statement (English and Chinese) came back empty. The only material covering this window is retrospective (Delivering Alpha 2022-09-28; NBIM 2024 on the front-end short). Retrospective accounts are not dated views.

### 1d. H2 2025

| Date | Source | Reliability | Policy read | Thesis / action | Quote | Day pinned |
|---|---|---|---|---|---|---|
| 2025-10-XX (after 10-09) | Spokesperson statement responding to NYT, via Snopes 2025-10-24, [note](../discovered_sources/2025-10-XX_spokesperson-not-invested-argentina-at-intervention.md) | secondary (spokesperson, relayed) | none | Argentina: no exposure as of 2025-10-09 (exit date unknown) | "was not invested in Argentina at the time of Treasury intervention." | no |

Nothing else was located: no interviews, X posts, Bloomberg Invest 2025 session, or CNBC appearance between Jul and Dec 2025. Robin Hood's 2025 conference (2025-10-15) press release does not mention him. Aggregators (Phemex, BigGo, search summaries) sometimes date the Piper Sandler "rates too low / AI earnings bubble" remarks to September 2025. Those remarks belong to 2026-09-10, already in the corpus: they refer to Warsh as Fed Chair and are dated 2026 by ceoworld.biz. They are not an H2 2025 candidate. The 13F filings for Q2 and Q3 2025 are holdings data with no commentary by him.

### 1e. Other dated reads found outside the four windows (for completeness)

| Date | Source | Reliability | Policy read | Thesis / action | Quote | Day pinned |
|---|---|---|---|---|---|---|
| 2014-06-19 | WSJ op-ed with Warsh, "The Asset-Rich, Income-Poor Economy" (Hoover repost 06-20) | primary (fragments) | easing (extraordinarily loose; exit sooner) | none | "The sooner and more predictably the Fed exits its extraordinary monetary accommodation, the sooner businesses can get back to business and labor can get back to work." | yes |
| 2020-10-27 | Robin Hood 2020 fireside with PTJ (agenda only) | primary (listing) | unknown | unknown | none | yes (event) |
| late Jan 2021 (published by 2021-02-06) | Talks at GS "Insights from Great Investors" (Pasquariello); TIE Winter 2021 adaptation | near-primary | easing (Fed suppressing rates, "friendliness") | Short UST long end; large long commodities; "very, very short" USD; long selected Taiwan/Korea/China equities | "Basically, to play potential inflation, I have a short Treasury position, primarily at the long end." / "...I have a very, very short dollar position." | no (bounded) |
| 2021-06-16 | Robin Hood 2021 "Fireside Chat: The Fed" (Warsh/Druckenmiller, agenda only) | primary (listing) | unknown | unknown | none | yes (event) |
| 2023-05-01 | "Coming Fiscal Horror Show", TIE Spring 2023 (USC keynote text) | primary | tightening (late: "Better late than never") | none | "...the Fed in the last year has raised rates 500 basis points. Better late than never." | yes (speech) |
| 2024-10-01/02 | Grant's Fall 2024 conference | secondary (paraphrase) | easing (reckless, reflationary) | Long Argentina, Japan, gold (not miners), COHR; avoid China | no verbatim; paraphrase: "a reckless monetary gamble with overtly reflationary policies" | yes (±1 day between sources) |

## 2. Known-but-not-located items: status

| Item | Status | Detail |
|---|---|---|
| ~2005 Sohn Taylor-rule housing talk | not located (existence confirmed) | Sohn 2016 primary text: "At the 2005 Ira Sohn Conference, looking at a more muted but similar deviation, I argued that the Greenspan Fed was sowing the seeds of an historical housing bubble fed by reckless sub-prime borrowing that would end very badly." No recording, transcript, or exact date. |
| Feb 2021 Goldman Sachs interview | located | "Talks at GS Presents: Insights from Great Investors", recorded late January 2021, interviewer Tony Pasquariello. GS transcript PDF: https://www.goldmansachs.com/pdfs/insights/goldman-sachs-talks/stanley-druckenmiller-f/transcript.pdf (403 to WebFetch, JS shell to curl; not read). Text read via http://www.international-economy.com/TIE_W21_Druckenmiller.pdf. Notes posted 2021-02-06 (offpisteinvesting.com). |
| Mid-2014 WSJ op-ed with Warsh on buybacks | located | "The Asset-Rich, Income-Poor Economy", WSJ 2014-06-19; https://www.hoover.org/research/asset-rich-income-poor-economy |
| May 2021 WSJ op-ed with Christian Broda | identified, not read | "The Fed Is Playing With Fire", WSJ 2021-05-10 (search snippets). Same event as the existing 2021-05-10 catalog file. |
| Morgan Stanley US Financials conf. 2022/2023 | not located | No record of a Druckenmiller session. The only Morgan Stanley appearance found is Hard Lessons (2026-01-30), already in the corpus. |
| 2017 conference reported by Institutional Investor (~2017-10-09) | not located | Not on the Robin Hood 2017 agenda (Oct 19–20). Venue still unknown; II paywalled. |
| Bloomberg Invest sessions 2017+ | partially | Only 2023-06-07 (already in the corpus) confirmed. No session found for 2017, 2018, 2019, 2021, 2022, or 2025. |
| "The Coming Fiscal Horror Show" (TIE 2023) | located | https://www.international-economy.com/TIE_Sp23_Druckenmiller.pdf (Spring 2023; text of the USC 2023-05-01 keynote) |
| Sohn 2016 transcript PDF | located | https://web.archive.org/web/2016id_/http://www.sohnconference.org/wp-content/uploads/2016/05/The_Endgame_Sohn.pdf (8-page prepared text). `The_EndGame.pdf` is the slide deck; the existing note has these two labels reversed. Also corrects "Volcker/Bernanke" to "Volcker and Greenspan" for the Taylor-rule average. |
| ECNY May 2020 full transcript | not located | econclubny.org transcript path 404 for the guessed filenames; legacy archive 403; Medium (lin187) 403; Wayback capture of Medium is a 404 stub. |

## 3. Turning-point count (era A, regime target)

Previous dated non-null reads come from the `regime_direction` values in `cases/`, listed here for reference only. No gate statistics are computed.

| Candidate | His read | Previous dated non-null read (≤18 mo) | Differs? | Assessment |
|---|---|---|---|---|
| Sohn 2016-05-04 (primary text) | easing | 2015-04-16 easing (12.5 mo; 2015-11-04 is null) | no | Not a turning point. It upgrades an existing case's source to primary. The change it records is in his equity thesis (bullish 2013 to bearish 2016), not in his regime read. |
| Robin Hood 2016-11-29 | unverified; teaser says betting on rising rates | 2016-05-04 easing (~7 mo; 2016-11-09/10 are null) | possibly | The only plausible turning point. It requires the content to show a policy read of tightening or normalization, not just a rates-up trade driven by fiscal expectations. Content is inaccessible, so it cannot be scored now. |
| H2 2019 | none new | — | — | 0 |
| Nov 2021 – Mar 2022 | none | — | — | 0 |
| H2 2025 spokesperson | no policy read | — | — | Not eligible (no regime target; spokesperson). |
| GS late Jan 2021 | easing | 2020-11-09 easing | no | 0. It does bound the date of the existing 2021-02-26 case to no later than 2021-02-06, and supplies an easing read where that case has null. These are observations only; no case was edited. |
| WSJ 2014-06-19 | easing | 2013-09-19 easing | no | 0 |
| TIE 2023 / USC 2023-05-01 | tightening | 2023-04-24 tightening | no | 0 |
| Grant's 2024-10-01 | easing | 2024-09-18 easing | no | 0 |
| Robin Hood 2020-10-27, 2021-06-16 | unknown | — | — | Not scoreable (no content). |

Count: 0 confirmed new era-A regime turning points. 1 conditional (Robin Hood 2016-11-29), which counts only if its inaccessible content shows a tightening or normalization read. Every policy read located inside the four gap windows either repeats his previous read or has no content. The two contemporaneous windows around actual Fed turns (H2 2019 cuts; Nov 2021 – Mar 2022 taper and hike) have no public dated Druckenmiller statement that could be found.
