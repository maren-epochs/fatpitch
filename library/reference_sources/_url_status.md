# URL status — reference doc §9 (excluding "Retrieved but not relevant" and FRED)

Fetched 2026-10-06. Method: direct HTTP fetch (WebFetch or curl); on failure, one archive.org attempt (`https://web.archive.org/web/2024/<url>`). WebFetch cannot reach archive.org, so archive attempts used curl. Several archive attempts initially returned HTTP 429 (rate limit) and were retried with pacing; "blocked" means the origin refused (403/JS-only) and the archive had no usable copy.

Status vocabulary: full-text-read | partial (paywall or truncated) | summary-only (metadata/description/landing page) | paywalled | blocked | dead.

| # | URL | Event file | Status | Note |
|---|---|---|---|---|
| 1 | https://automatedalpha.substack.com/p/i-built-druckenmillers-fat-pitch | 2026-03-24_automated-alpha-fat-pitch-filter.md | partial | Free portion read; paywall at "Complete Druckenmiller Alpha System" |
| 2 | https://automatedalpha.substack.com/p/i-built-druckenmillers-fat-pitch?r=6efi&utm_medium=ios | 2026-03-24_automated-alpha-fat-pitch-filter.md | partial | Same article as #1 |
| 3 | https://druckenmiller-alpha.vercel.app | 2026-03-24_automated-alpha-fat-pitch-filter.md | partial | Navigation shell only; no data views |
| 4 | https://gist.github.com/timhwang21/e6a2b24e064182dd9099ad00e4f4f9a6 | 2015-01-18_lost-tree-club-speech.md | full-text-read | Raw OCR transcript downloaded and searched |
| 5 | http://covestreetcapital.com/Blog/wp-content/uploads/2015/03/Druckenmiller-_Speech.pdf | 2015-01-18_lost-tree-club-speech.md | dead | 404; archive snapshot also 404 |
| 6 | https://podcasts.apple.com/no/podcast/stan-druckenmiller-inside-the-mind-of-a-legendary-investor/id1614211565?i=1000675883446 | 2024-11-06_nbim-in-good-company-podcast.md | summary-only | Episode metadata: 2024-11-06, 58 min, S1 E97 |
| 7 | https://podscripts.co/podcasts/in-good-company-with-nicolai-tangen/stan-druckenmiller-inside-the-mind-of-a-legendary-investor | 2024-11-06_nbim-in-good-company-podcast.md | full-text-read | Full ASR transcript |
| 8 | https://podwise.ai/episodes/2262853 | 2024-11-06_nbim-in-good-company-podcast.md | summary-only | Generic AI takeaways; no specifics |
| 9 | https://sv.player.fm/series/series-3330248/highlights-stan-druckenmiller | 2024-11-06_nbim-in-good-company-podcast.md | blocked | 403; archive 429 (rate-limited) on both tries |
| 10 | https://wkt-1-d85j.onrender.com/wkt/watch/-5Weeox0Xus | 2024-11-06_nbim-in-good-company-podcast.md | summary-only | Mirror of NBIM YouTube video; metadata only. YouTube description fetched directly (recorded 2024-11-05) |
| 11 | https://www.nbim.no/en/publications/podcast/ | 2024-11-06_nbim-in-good-company-podcast.md | summary-only | Index lists only the 2024 Druckenmiller episode |
| 12 | https://www.youtube.com/watch?v=G-MlrpoMig0 | 2018-09-06_sokoloff-real-vision-interview.md | summary-only | Description/chapters; filmed 2018-09-06; captions not downloadable; no public transcript linked |
| 13 | https://www.youtube.com/watch?v=-7sWLIybWnQ | 2022-06-10_sohn-2022-collison-conversation.md | summary-only | Identified as Sohn 2022 / John Collison; chapters only; captions not downloadable |
| 14 | https://www.bloomberg.com/news/articles/2019-06-03/druckenmiller-piles-into-treasuries-on-possible-fed-rate-drop | 2019-06-03_bloomberg-treasuries-tariff-tweet.md | blocked | 403; archive captured Bloomberg block page. Headline only |
| 15 | https://www.cnbc.com/2022/09/28/stanley-druckenmiller-sees-hard-landing-in-2023-with-a-possible-deeper-recession-than-many-expect.html | 2022-09-28_cnbc-delivering-alpha.md | full-text-read | WebFetch 403; curl succeeded |
| 16 | https://www.cnbc.com/2020/11/09/stanley-druckenmiller-says-he-wouldnt-want-to-be-short-market-sees-stock-rotation-continuing.html | 2020-11-09_cnbc-the-exchange-rotation.md | full-text-read | WebFetch 403; curl succeeded |
| 17 | https://thefelderreport.com/2020/05/27/why-brrr-doesnt-mean-what-you-think-it-means | 2020-05-12_economic-club-of-new-york.md | full-text-read | Verbatim ECNY excerpt |
| 18 | https://thefelderreport.com/?p=51626 | 2020-05-12_economic-club-of-new-york.md | full-text-read | Same post as #17 |
| 19 | https://thefelderreport.com/?p=30214 | 2015-01-18_lost-tree-club-speech.md | full-text-read | "Goldilocks And The Liquidity Bears" 2018-03-09; quotes Lost Tree |
| 20 | https://app.hedgeye.com/insights/84926-why-money-printer-go-brrr-doesn-t-mean-what-you-think-it-means | 2020-05-12_economic-club-of-new-york.md | blocked | 403; archive 404 |
| 21 | https://app.hedgeye.com/insights/84926-why-money-printer-go-brrr-doesn-t-mean-what-you-think-it-means/print | 2020-05-12_economic-club-of-new-york.md | blocked | 403; archive 404 |
| 22 | https://mutualfundobserver.com/discuss/showthread.php?tid=51737 | 2022-06-10_sohn-2022-collison-conversation.md | full-text-read | Timestamped notes (forum, 2022-07-05) |
| 23 | https://www.mutualfundobserver.com/discuss/showthread.php?tid=51737 | 2022-06-10_sohn-2022-collison-conversation.md | full-text-read | Identical to #22 |
| 24 | https://hedgefundalpha.com/?p=2149781 | 2022-06-10_sohn-2022-collison-conversation.md | full-text-read | Redirects to #25 |
| 25 | https://hedgefundalpha.com/strategies/on-my-radar-stanley-druckenmiller/ | 2022-06-10_sohn-2022-collison-conversation.md | full-text-read | Blumenthal OMR notes, 2022-07-20 |
| 26 | https://actionablenews.substack.com/p/aia-october-2024 | 2024-10-06_actionable-news-horizon-quote.md | partial | Paywall after intro; 18–24 month quote read |
| 27 | https://actionablenews.substack.com/p/free-weekly-email-111224 | 2024-11-06_nbim-in-good-company-podcast.md | full-text-read | Short note on NBIM 2024 |
| 28 | https://hedgefundalpha.com/stocks/stanley-druckenmiller-focus-on-what-makes-a-stock-go-up-or-down/ | 1992-XX-XX_new-market-wizards-chapter.md | full-text-read | Verbatim NMW excerpt |
| 29 | https://hedgefundalpha.com/strategies/my-notes-on-the-druckenmiller-real-vision-interview/ | 2018-09-06_sokoloff-real-vision-interview.md | full-text-read | Macro Ops notes with long verbatim passages |
| 30 | https://hedgefundalpha.com/strategies/stanley-druckenmiller-buy-first-analyze-later/ | 2023-XX-XX_nbim-investment-conference-2023.md | full-text-read | Verbatim NBIM 2023 passage |
| 31 | https://hedgefundalpha.com/strategies/stanley-druckenmiller-bulls-make-money-bears-make-money-and-pigs-get-slaughtered-im-here-to-tell-you-i-was-a-pig/ | 2015-01-18_lost-tree-club-speech.md | full-text-read | Lost Tree concentration excerpt |
| 32 | https://hedgefundalpha.com/strategies/just-under-22-trillion-sits-on-the-cumulative-central-bank-balance-sheet-of-the-big-six/ | 2015-01-18_lost-tree-club-speech.md | full-text-read | Blumenthal 2018-08-13; quotes Lost Tree liquidity line; body is Camp Kotok notes |
| 33 | https://hedgefundalpha.com/interview-stan-druckenmiller/ | 1988-03-28_barrons-still-bearish-interview.md | paywalled | Live 404; archive shows teaser + member wall |
| 34 | https://www.investingbythebooks.com/columns/2018/12/3/stanley-druckenmiller | 2018-09-06_sokoloff-real-vision-interview.md | full-text-read | Timestamp list |
| 35 | https://magica.com/youtube-summarizer/stan-druckenmiller-shares-hard-lessons-and-investment-insights-from-a-legendary-career-z_pk4eBDaLA | 2026-01-30_morgan-stanley-hard-lessons.md | full-text-read | AI summary of Morgan Stanley video (not a transcript) |
| 36 | https://members.delphidigital.io/feed/druck-interview-tldr | 2023-XX-XX_nbim-investment-conference-2023.md | full-text-read | 2023-05-03 summary with quotes |
| 37 | https://blog.validea.com/?p=28196 | 2021-XX-XX_the-hustle-interview.md | dead | Redirects to Validea homepage; archive 404. Assumed alt URL of #38 |
| 38 | https://blog.validea.com/stanley-druckenmiller-insights-on-the-market-and-its-greatest-investors/ | 2021-XX-XX_the-hustle-interview.md | full-text-read | Live redirects to homepage; read via archive (2024-09-14) |
| 39 | https://blog.validea.com/druckenmiller-says-very-unhappy-ending-may-await-investors/ | 2015-01-18_lost-tree-club-speech.md | full-text-read | Live redirects to homepage; read via archive (2024-11-13) |
| 40 | https://dailyspeculations.com/wordpress/?p=13988 | XXXX-XX-XX_mauboussin-sizing-dailyspec.md | dead | Connection failure; archive 404 |
| 41 | https://dailyspeculations.com/wordpress/?p=10192 | 2015-01-18_lost-tree-club-speech.md | full-text-read | Connection failure live; archive (2019) read; short reader comment |
| 42 | https://www.cardplayer.com/?p=1027762 | 1992-XX-XX_new-market-wizards-chapter.md | full-text-read | "Press Your Winners" (Greg Dinkin) |
| 43 | https://www.nasdaq.com/articles/how-do-stocks-react-rate-cuts | XXXX-XX-XX_secondary-profiles-and-commentary.md | blocked | curl 403; WebFetch timeout; archive 404 |
| 44 | https://www.advisorperspectives.com/commentaries/2017/12/04/on-my-radar-it-feels-like-1999-all-over-again | 2015-01-18_lost-tree-club-speech.md | full-text-read | 403 live; archive (2025-03-22) read; quotes Lost Tree liquidity line |
| 45 | https://www.advisorperspectives.com/commentaries/2015/04/20/on-my-radar-the-speech-at-lost-tree-club | 2015-01-18_lost-tree-club-speech.md | blocked | 403; archive 404 |
| 46 | https://www.fxstreet.com/analysis/thoughts-from-the-frontline/2015/05/21 | 2015-01-18_lost-tree-club-speech.md | dead | 404; archive (2018) also 404 |
| 47 | https://www.benzinga.com/analyst-ratings/analyst-color/15/04/5403650/druckenmiller-joins-fed-bashers-this-will-end-badly | 2015-01-18_lost-tree-club-speech.md | full-text-read | 2015-04-13 |
| 48 | https://aryadeniz.substack.com/p/stanley-druckenmillers-lost-tree | 2015-01-18_lost-tree-club-speech.md | full-text-read | Second full transcript conversion (2025-09-01) |
| 49 | https://theideafarm.com/miscellaneous/speech-at-lost-tree-club/ | 2015-01-18_lost-tree-club-speech.md | summary-only | Landing page with takeaways; 48-page PDF not opened |
| 50 | https://www.mauldineconomics.com/overmyshoulder/article/stanley-druckenmiller-at-the-lost-tree-club | 2015-01-18_lost-tree-club-speech.md | paywalled | Live 404; archive (2016) shows subscriber wall |
| 51 | https://www.businessinsider.in/miscellaneous/slidelist/68189821.cms | XXXX-XX-XX_secondary-profiles-and-commentary.md | dead | DNS failure (ENOTFOUND); archive 404 |
| 52 | https://ugebrev.dk/?p=11467 | 2015-01-18_lost-tree-club-speech.md | full-text-read | 2015-04-12; partial transcript in English |
| 53 | https://www.bnnbloomberg.ca/druckenmiller-says-risk-reward-in-stocks-is-worst-he-s-ever-seen-1.1435356 | 2020-05-12_economic-club-of-new-york.md | full-text-read | Live redirects to homepage; archive (2024-05-26) read |
| 54 | https://bnnbloomberg.ca/investing/2024/12/20/ceo-of-norways-18-trillion-fund-reveals-perks-of-podcast-gig | 2024-11-06_nbim-in-good-company-podcast.md | full-text-read | Live redirects to homepage; archive read; only passing mention of Druckenmiller |
| 55 | https://sites.duke.edu/tech/?p=95 | 2024-11-06_nbim-in-good-company-podcast.md | dead | 404; archive 404 |
| 56 | https://moiglobal.com/latticework-stanley-druckenmiller-202503 | 2025-03-21_moi-latticework-profile.md | summary-only | Live 404; archive landing page (audio not accessible) |
| 57 | https://www.fool.com/investing/how-to-invest/famous-investors/stanley-druckenmiller | XXXX-XX-XX_secondary-profiles-and-commentary.md | full-text-read | curl failed (308 loop); WebFetch on trailing-slash URL succeeded |
| 58 | https://longportapp.cn/news/277289579 | 2026-01-30_morgan-stanley-hard-lessons.md | blocked | Client-side rendered; no article text via fetch; archive 404 |
| 59 | https://traderlion.com/quotes/druckenmiller-quotes/ | XXXX-XX-XX_secondary-profiles-and-commentary.md | blocked | 403 (curl and WebFetch); archive 429 on all retries |
| 60 | https://daytrading.com/stanley-druckenmiller | XXXX-XX-XX_secondary-profiles-and-commentary.md | full-text-read | Updated 2026-02-28; contains "tight stop losses" error |
| 61 | https://finmasters.com/?p=150923 | XXXX-XX-XX_secondary-profiles-and-commentary.md | full-text-read | 403 live; archive (2024-04-06) read |
| 62 | https://www.hustlefund.vc/post/angel-squad-stanley-druckenmiller-investments-the-macro-master-who-generated-30-annual-returns-without-a-single-down-year | XXXX-XX-XX_secondary-profiles-and-commentary.md | full-text-read | |
| 63 | https://www2.hustlefund.vc/post/angel-squad-stanley-druckenmiller-investments-the-macro-master-who-generated-30-annual-returns-without-a-single-down-year | XXXX-XX-XX_secondary-profiles-and-commentary.md | full-text-read | Identical to #62 |
| 64 | https://simplefunctions.dev/opinions/soros-pound-theo-trump-conviction-macro-prediction-markets | XXXX-XX-XX_secondary-profiles-and-commentary.md | full-text-read | 503 live; archive (2026-07-10) read |
| 65 | https://www.bilanz.ch/invest/marktrotation-value-aktien-und-kleine-titel-im-fokus/nr85l42 | 2026-02-26_bilanz-q4-2025-rotation.md | full-text-read | German |
| 66 | https://www.gurufocus.com/news/1212234 | 2020-08-18_gurufocus-q2-2020-13f.md | full-text-read | 403 live; archive (2020-11-21) read |
| 67 | https://aaoresearch.substack.com/p/fear-of-missing-out-cost-him-3-billion | XXXX-XX-XX_secondary-profiles-and-commentary.md | partial | Paywall after intro |
| 68 | https://www.zacks.com/commentary/2300264/is-thursdays-market-rotation-here-to-stay | XXXX-XX-XX_secondary-profiles-and-commentary.md | full-text-read | 2024-07-11 |

## Counts

| Status | Count |
|---|---|
| full-text-read | 39 |
| partial | 5 |
| summary-only | 8 |
| paywalled | 2 |
| blocked | 8 |
| dead | 6 |
| Total | 68 |

Of the 39 full-text reads, 11 required the archive.org fallback or a non-WebFetch client.

Additional URL used (not in §9): https://www.youtube.com/watch?v=z_pk4eBDaLA (Morgan Stanley Hard Lessons; description only), discovered via #35.
