"""Corpus expansion v2 (owner decision 2026-10-06): cases mined from every library note, added before any engine
scoring and before the holdout re-seal (``spec/HOLDOUT.md`` "Re-seal log").

Same conventions as ``tools\\build_cases.py`` (row layout, ``date_basis`` rules, serialization: this script calls
its ``build``). Targets record what the source says was believed or done at the time; outcome, P&L and hindsight
wording in the library notes are not transcribed. ``seed_id`` = ``X-nn``; ``citation`` = the source note(s).

Mining survey (2026-10-06, all notes in ``library\\reference_sources`` and ``library\\discovered_sources``):
dated, attributable changes of view not already in ``cases\\`` became rows below. Rejected candidates and the
reason are in ``REJECTED``.

    .\\.venv\\Scripts\\python.exe tools\\build_cases_v2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_cases import NBIM24, SOKO, T, build

RUHLE15 = "DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md"
CNBC21 = "DS/2021-05-11_cnbc-squawk-box-raging-mania-dollar.md"
CNBC23 = "DS/2023-11-01_cnbc-squawk-box-yellen-debt-drunken-sailors.md"
CNBC24 = "DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md"
GS21 = "DS/2021-01-XX_talks-at-gs-great-investors-pasquariello.md"
BBG18 = "DS/2018-12-18_bloomberg-tv-erik-schatzker.md"
NMW = "DS/1992-XX-XX_new-market-wizards-full-chapter-text.md"
MI18 = "DS/2018-05-03_manhattan-institute-hamilton-award-speech.md"
GRANTS18 = "DS/2018-10-09_grants-fall-conference-jim-grant.md"
WSJ18 = "DS/2018-11-21_wsj-interview-risky-to-be-tightening.md"
BBGI23 = "DS/2023-06-07_bloomberg-invest-sonali-basak.md"

# seed, slug, asof, date_basis, episode, truth, mech, reliability, retrospective, regime, theses,
# expression, action, size_band, citation, notes
CASES_V2 = [
    ("X-01", "still-bearish-barrons-1988", "1988-03-28",
     "pinned: Barron's issue date 1988-03-28 (Monday); interview published that day",
     "EP02-1988-BEAR", "action", "yes", "secondary", False, None, [T("equity", "short", "US")],
     ["equity_us"], None, None,
     "DS/1988-03-28_barrons-still-bearish.md; RS/1988-03-28_barrons-still-bearish-interview.md",
     ("Still bearish on US equities five months after the 1987 crash; expected a further correction; buyout "
      "(LBO) excess cited. Teaser-level source; action and size not stated.")),
    ("X-02", "just-like-2004-ruhle-2015", "2015-04-16",
     ("conservative: air date uncertain (Bloomberg clips dated 2015-04-15; transcripts published 2015-04-16 by "
      "HedgeFundAlpha and GuruFocus); the later date is the first close at which the content is certainly public"),
     "EP12-2014-15-DIVERGE", "action", "yes", "near-primary", False, "easing",
     [T("fx", "short", "EUR"), T("equity", "long", "JP"), T("equity", "long", "EA"),
      T("commodity", "long", "OIL")], ["fx_eur", "equity_jp", "equity_ea"], "hold", None, RUHLE15,
     ("Big bets short EUR on US/Europe policy divergence ('we were tapering... They were going to start QE. They "
      "had gone to a negative deposit rate') and long Japan/Europe equities; constructive on oil vs the forward "
      "curve. Regime label easing refers to the thesis region (ECB QE / negative rates); US read also easing "
      "(zero rates 'unnecessary', 'rhymes with 2004'). Relative-policy case.")),
    ("X-03", "taylor-gap-radicalism-2017", "2017-12-12",
     "pinned: CNBC Closing Bell interview date (note date)",
     "EP14-2018-QT", "action", "yes", "near-primary", False, "easing", [T("equity", "long", "US")],
     ["equity_us"], "hold", None, "DS/2017-12-12_cnbc-closing-bell-kelly-evans.md",
     ("Taylor-rule rates far above actual policy rates in the US and Europe ('monetary radicalism'); the stock "
      "market 'a function of central bank policy'; long US equities (prefers AMZN, FB, GOOGL); no crypto. "
      "Episode EP14 taken back to Dec 2017 (Fed balance-sheet runoff began Oct 2017).")),
    ("X-04", "global-qe-to-zero-bearish-2018", "2018-06-29",
     ("conservative: Real Vision interview (filmed 2018-09-06) says he expected global central-bank buying "
      "falling from ~$1T/yr to zero to hit equities from mid-year; no day given; asof = last trading day of "
      "Jun 2018"),
     "EP14-2018-QT", "action", "yes", "near-primary", True, "tightening", [T("equity", "short", "US")],
     ["equity_us"], None, None, SOKO,
     ("Bearish US equities on the rate of change of global QE (Fed runoff plus ECB purchases going to zero "
      "within 12 months). Retrospective account; action and size not stated.")),
    ("X-05", "constructive-turn-q4-2019", "2019-12-18",
     ("pinned: Bloomberg TV interview date; the turn is dated only to Q4 2019 and the holdings are those "
      "reported at the interview, so the interview date is the latest defensible"),
     "EP15-2019-TARIFF", "action", "partial", "secondary", False, "easing",
     [T("commodity", "long", "COPPER"), T("equity", "long", "US"), T("equity", "long", "JP")],
     ["commodity_copper", "equity_us", "equity_jp"], "size_up", None,
     "DS/2019-12-18_bloomberg-schatzker-couldnt-have-been-more-wrong.md",
     ("Turned more constructive after three Fed cuts and trade de-escalation; holdings copper, US and Japan "
      "equities. Unverified recap items (long CAD/AUD, short JPY, short long bonds) not transcribed.")),
    ("X-06", "raging-mania-inflation-2020", "2020-09-09",
     "pinned: CNBC Squawk Box interview date (note date)",
     "EP16-2020-COVID", "action", "yes", "secondary", False, "easing", [], [], None, None,
     "DS/2020-09-09_cnbc-squawk-box-absolute-raging-mania.md",
     ("Fed and Treasury 'merging'; 'absolute raging mania'; first inflation worry in a long while; no view on "
      "the near term, next 3-5 years challenging. No position stated (regime-only case).")),
    ("X-07", "relative-bets-commodities-short-bonds-2020", "2020-10-30",
     ("conservative: CNBC 2021-05-11 says relative bets were shifted into commodities, rates (short bonds) and "
      "the dollar from August to October 2020; asof = last trading day of Oct 2020"),
     "EP16-2020-COVID", "action", "yes", "secondary", True, "easing",
     [T("commodity", "long"), T("rates", "short", "US")], ["commodity_global", "rates_us"], "enter", None,
     f"{CNBC21}; {CNBC23}",
     ("Emergency settings judged no longer warranted (economy booming by Oct 2020, per the 2023 account); relative "
      "bets moved into commodities and short bonds. Dollar leg omitted: direction ambiguous across sources "
      "(C43 codes long USD; a Feb 2021 secondary report says short USD).")),
    ("X-08", "short-usd-goldman-2021", "2021-02-05",
     ("conservative: Talks at GS interview 'recorded in late January 2021' (TIE adaptation), day unknown; first "
      "dated publication of its content is 2021-02-06 (Saturday, Off Piste notes); asof = last NYSE trading day "
      "before that publication, the latest date certainly on or after the recording"),
     "EP17-2021-MANIA", "action", "yes", "near-primary", False, "easing",
     [T("fx", "short", "USD"), T("rates", "short", "US"), T("commodity", "long")],
     ["fx_usd", "rates_us", "commodity_global"], "hold", None,
     f"{GS21}; DS/2021-02-XX_goldman-sachs-interview.md",
     ("Positions stated as held: 'a very, very short dollar position'; 'a short Treasury position, primarily at "
      "the long end'; 'a large position in commodities'. Regime label easing: 'The longer the Fed tries to keep "
      "rates suppressed...'; 'if the Fed continues to push the envelope in terms of friendliness'. Constructive "
      "on stock names in Taiwan, Korea and China (single names; not coded). Source is TIE's edited first-person "
      "adaptation. USD leg conflicts with the long-USD leg of C43.")),
    ("X-09", "ai-long-hard-landing-sohn-2023", "2023-05-09",
     "pinned: Sohn 2023 conversation date (note date)",
     "EP19-2023-RATES", "action", "yes", "secondary", False, "tightening",
     [T("equity", "long", "US"), T("commodity", "long", "GOLD")], ["equity_us", "commodity_gold"], "hold", None,
     "DS/2023-05-09_sohn-2023-kiril-sokoloff.md; DS/2023-06-07_bloomberg-invest-sonali-basak.md",
     ("Hard-landing view after a broad asset bubble and 500bp of hikes; long AI via NVDA and MSFT, long gold and "
      "silver; copper and housing named as recovery ideas.")),
    ("X-10", "japan-copper-long-2024", "2024-05-07",
     "pinned: CNBC Squawk Box interview date (note date)",
     "EP20-2024-CUT", "action", "yes", "near-primary", False, "easing",
     [T("equity", "long", "JP"), T("commodity", "long", "COPPER")], ["equity_jp", "commodity_copper"], "hold",
     None, CNBC24,
     ("Dec 2023 pivot judged to have loosened financial conditions ('set financial conditions on fire'); long "
      "Japan (governance reform, reflation) and copper (12-year greenfield lead time; EV, grid, data-center "
      "demand); no China.")),
    ("X-11", "inflation-second-wave-short-2024", "2024-11-06",
     ("pinned: In Good Company episode recorded 2024-11-05 (US election day) and published 2024-11-06; "
      "publication date used"),
     "EP20-2024-CUT", "action", "yes", "near-primary", False, "easing", [T("rates", "short", "US")],
     ["rates_us"], "hold", {"low": 25, "high": 25, "unit": "pct_nav_10y_eq"}, NBIM24,
     ("More worried about inflation than about the economy; the 50bp cut judged a premature declaration of "
      "victory; ~25% NAV 10y-equivalent Treasury short held; neither long nor short AI.")),
    ("X-12", "let-bond-market-speak-2026", "2026-08-24",
     "pinned: WSJ op-ed publication date (note date)",
     "EP21-2025-26-ROTATE", "action", "yes", "secondary", False, "easing", [T("rates", "short", "US")],
     ["rates_us"], None, None, "DS/2026-08-24_wsj-oped-let-the-bond-market-speak.md",
     ("Treasury's expanded long-dated buybacks judged yield suppression ('Treasury-run QE'); inflation above "
      "target at full employment, 10y at or below nominal GDP; long yields should be allowed to rise. Position "
      "not stated. Regime label easing (policy judged too loose), not tightening as in the HOLDOUT.md v1 "
      "candidate row.")),
    # spec-v0.2 additions (owner decisions 2026-10-06; spec/corpus_v0.2_changes.md). The Talks at GS interview
    # (Jan 2021) is the same event as X-08 and the Sohn 2016 full text the same event as C29: both upgrade those
    # cases instead of adding new ones.
    ("X-13", "asset-rich-income-poor-2014", "2014-06-19",
     ("pinned: WSJ op-ed with Kevin Warsh dated 2014-06-19 (refers to the FOMC meeting 'earlier this week', "
      "2014-06-17/18); Hoover repost 2014-06-20"),
     "EP12-2014-15-DIVERGE", "action", "yes", "primary", False, "easing", [], [], None, None,
     "DS/2014-06-19_wsj-oped-warsh-asset-rich-income-poor.md",
     ("'Extraordinarily loose monetary policy will continue in force'; the Fed should exit 'its extraordinary "
      "monetary accommodation' sooner and more predictably. Buybacks over capex. No position stated "
      "(regime-only case).")),
    ("X-14", "fiscal-horror-show-2023", "2023-05-01",
     ("pinned: USC Marshall keynote 2023-05-01 (TIE Spring 2023 states the article is based on it); the printed "
      "text cites the June 2023 CBO outlook in a figure, so only the policy read, which matches the speech "
      "window (500bp of hikes also cited at NBIM 2023-04-24), is coded"),
     "EP19-2023-RATES", "action", "yes", "primary", False, "tightening", [], [], None, None,
     "DS/2023-05-01_tie-spring-2023-coming-fiscal-horror-show.md; DS/2023-05-01_usc-marshall-keynote.md",
     ("'In an attempt to correct the biggest mistake in Fed history, the Fed in the last year has raised rates "
      "500 basis points. Better late than never.' Fiscal-gap argument; no position stated (regime-only case).")),
    ("X-15", "grants-gold-argentina-japan-2024", "2024-10-02",
     ("conservative: Grant's Fall 2024 conference, 2024-10-01 per HedgeFundAlpha, 2024-10-02 per Hedgeweek; "
      "later date used"),
     "EP20-2024-CUT", "action", "yes", "secondary", False, "easing",
     [T("commodity", "long", "GOLD"), T("equity", "long", "AR"), T("equity", "long", "JP")],
     ["commodity_gold", "equity_ar", "equity_jp"], "hold", None,
     "DS/2024-10-01_grants-fall-conference-2024.md",
     ("Fed paraphrased as taking 'a reckless monetary gamble with overtly reflationary policies' (HFA, not "
      "verbatim). Owns gold, not miners; attention on Argentina and Japan; no China without a leadership change; "
      "likes COHR (single name; not coded).")),
    # spec-v0.2 addition (owner decision 2026-10-07; spec/corpus_v0.2_changes.md section 8): the Treasury long
    # first stated in the 2018-12-18 Bloomberg TV interview, one trading day after C33, as its own case.
    ("X-16", "treasury-long-bloomberg-2018", "2018-12-18",
     ("pinned: Bloomberg News article on the Bloomberg TV interview with Erik Schatzker published 2018-12-18 "
      "04:00 ET (09:00 UTC, page metadata), before the open; the full interview aired on Bloomberg TV the same "
      "day (air time unverified). The positions were public before the 2018-12-18 close, so asof = that close "
      "whatever the broadcast time"),
     "EP14-2018-QT", "action", "yes", "secondary", False, "tightening", [T("rates", "long", "US")],
     ["rates_us", "equity_us_financials"], "hold", None, BBG18,
     ("Says he owns two-, five- and 10-year Treasuries; if the Fed tightens too much and must reverse, 'it's "
      "not inconceivable to me at all that the 2-years are back to 50 to 60 basis points in a couple of years'. "
      "Says he has been short 'all the financials', including banks, for the same rate reasons: coded as the "
      "expression equity_us_financials only, since the thesis vocabulary has no sector region and an "
      "equity/short/US thesis would misstate it (he says he avoids shorting the market: 'you get squeezed out "
      "of shorts'). Regime read tightening: he urged the Fed to hold off the 2018-12-19 hike (same read as C33) "
      "and wants 'this bubble to unwind slowly'. Action hold: he states ownership; the article's 'has been "
      "buying' is the reporter's summary with no entry date. Long cloud names (MSFT, CRM, NOW, WDAY) are "
      "single names, not coded. Indicators 'not red yet, but... definitely amber'.")),
    # spec-v0.3 additions (owner decision 2026-10-07, option A; spec/corpus_v0.3_changes.md): six tightening reads
    # and two easing reads from library/research/tightening_sources.md. Episodes EP22 to EP24 are new (numbered
    # in order of creation; no existing episode covers 1987, the 1989 Nikkei short or December 1991).
    ("X-17", "half-cash-19pct-rates-1981", "1981-06-30",
     ("conservative: NMW (interview Dec 1991) gives 'By mid-1981' for the move to 50% cash and 'unbelievably "
      "bearish in June 1981', with the losses following in Q3 1981; the move is therefore no later than June; "
      "asof = last NYSE trading day of June 1981"),
     "EP01-1981-BONDS", "action", "yes", "primary", True, "tightening", [T("equity", "short", "US")],
     ["equity_us"], "reduce", None, NMW,
     ("'By mid-1981, stocks were up to the top of their valuation range, while at the same time, interest rates "
      "had soared to 19 percent. It was one of the more obvious sell situations in the history of the market. We "
      "went into a 50 percent cash position.' Regime label tightening is implied by his 19% rate read; he names "
      "no Fed action for mid-1981 (the Q4 1981 'the Fed was extremely tight' read belongs to C01). Thesis short "
      "= his stated bear view ('never felt more strongly about anything than the bear side of this market'); the "
      "action is the cut to 50% cash, the other 50% stayed long, so no size band. Distinct from C01 "
      "(1981-12-31: dumped the remaining stocks, 50% long bonds).")),
    ("X-18", "net-short-fed-tightening-1987", "1987-06-30",
     ("conservative: NMW (interview Dec 1991) gives only 'In June I changed my stripes and actually went net "
      "short' (no day); asof = last NYSE trading day of June 1987"),
     "EP22-1987-CRASH", "action", "yes", "primary", True, "tightening", [T("equity", "short", "US")],
     ["equity_us"], "reverse", None, NMW,
     ("Switched from long to net short US equities in June 1987: 'The Fed had been tightening since January "
      "1987, and the dollar was tanking, which suggested that the Fed was going to tighten some more.' Valuation "
      "(2.6% dividend yield, record price/book) set the magnitude; liquidity and narrow breadth set the timing "
      "('I never use valuation to time the market'). Action reverse: 'before you switched from long to short'. "
      "The 1987-10-16 switch to 130% long is a later technical trade and not coded.")),
    ("X-19", "nikkei-short-boj-1989", "1989-12-29",
     ("conservative: NMW (interview Dec 1991) gives 'In late 1989' for the bearish turn and the short; asof = "
      "last NYSE trading day of Q4 1989"),
     "EP23-1989-NIKKEI", "action", "yes", "primary", True, None, [T("equity", "short", "JP")],
     ["equity_jp"], "enter", None, NMW,
     ("Short the Japanese stock market (Nikkei): 'just about the best risk/reward trade I had ever seen'. "
      "Reasons: multiyear overextension, a speculative blow-off, and 'most important—three times as important "
      "as everything I just said—the Bank of Japan had started to dramatically tighten monetary policy' (JGBs "
      "falling while the Nikkei made highs). The BoJ read is tightening; it is recorded here and not as "
      "regime_direction, which is a read of US policy, and the source states no US read for late 1989. "
      "Thesis-only case.")),
    ("X-20", "fed-panic-bond-exit-1991", "1991-12-31",
     ("conservative: NMW interview dated by Schwager '[at the time of this interview, December 1991]' (no day); "
      "the long-bond exit is given as 'late 1991'; asof = last NYSE trading day of December 1991"),
     "EP24-1991-EASE", "action", "yes", "primary", False, "easing", [], ["rates_us"], "exit", None, NMW,
     ("Contemporaneous read: 'now with the economy in decline, the deficit ballooning, and the administration "
      "and the Fed in a state of panic, the public should be wary about the risk in holding long-term bonds'; "
      "money-market rates 'only 4.5 percent'. Long bonds: 'I was long until late 1991.' Regime label easing (Fed "
      "in panic, low short rates). The bond warning is advice to the public, not a stated short, so no thesis "
      "is coded; the action is the exit of the long-bond position. Debt-liquidation view of the economy.")),
    ("X-21", "rates-below-inflation-mi-2018", "2018-05-04",
     ("conservative: Manhattan Institute Alexander Hamilton Award dinner, 2018-05-03; time of the remarks not "
      "stated and a dinner may fall after the close; asof = next NYSE close"),
     "EP14-2018-QT", "action", "yes", "primary", False, "easing", [], [], None, None, MI18,
     ("'Years after the Great Recession ended the Fed has not only kept interest rates below inflation but have "
      "accumulated an unprecedented $4.5 trillion on their balance sheet by doing QE.' / 'an unprecedented, "
      "ultra-monetary, radical monetary expansion'; deficits larger because policy has not 'been normalized'. "
      "Regime label easing: his read of the stance in May 2018, although the Fed was hiking and runoff had "
      "begun. No position stated (regime-only case).")),
    ("X-22", "liquidity-going-down-grants-2018", "2018-10-09",
     "pinned: Grant's Fall 2018 conference conversation with James Grant, 2018-10-09 (note date)",
     "EP14-2018-QT", "action", "yes", "secondary", False, "tightening", [], [], None, None, GRANTS18,
     ("'It's all about liquidity, and liquidity is going down' and 'The bombs are going to go off and things "
      "will be getting ugly' (HedgeFundAlpha headlines; notes not verbatim): hikes plus QT plus the end of "
      "foreign QE read as tightening. A notes snippet 'We are going to higher interest rates' is not verbatim "
      "and states no position, so no thesis is coded. No position stated (regime-only case).")),
    ("X-23", "qt-zombies-wsj-2018", "2018-11-23",
     ("conservative: WSJ interview relayed by ForexLive at 2018-11-22 04:12 GMT (2018-11-21 23:12 ET), so the WSJ "
      "text was public by then but probably after the 11-21 close; 2018-11-22 was a NYSE holiday "
      "(Thanksgiving); asof = 2018-11-23, the first close at which the content is certainly public (a 13:00 "
      "early close; asof kept at the corpus 16:00 ET convention)"),
     "EP14-2018-QT", "action", "yes", "secondary", False, "tightening", [], [], None, None, WSJ18,
     ("'As quantitative easing turns to quantitative tightening, all these zombies are going to be exposed'; "
      "'risky to be tightening now' (ForexLive headline paraphrase); defensives over cyclicals since May mean "
      "'a very, very late cycle'. Regime label tightening (QE turning to QT plus hikes). The call for the Fed to "
      "wait is a prescription and is not coded. WSJ original not read. No position stated (regime-only case).")),
    ("X-24", "more-shoes-ai-long-bloomberg-2023", "2023-06-07",
     "pinned: Bloomberg Invest on-stage interview with Sonali Basak, 2023-06-07 (Fortune report same day)",
     "EP19-2023-RATES", "action", "yes", "secondary", False, "tightening", [T("equity", "long", "US")],
     ["equity_us"], "hold", None, BBGI23,
     ("'The biggest broadest asset bubble ever, and then you jack interest rates up 500 basis points in a year... "
      "Silicon Valley Bank, Bed Bath & Beyond, they're probably the tip of the iceberg'; 'Our central case is "
      "there's more shoes to drop'. Regime label tightening. Long AI as stated: Bloomberg clip title "
      "'Druckenmiller on How AI is Dominating His Long Portfolio'; 'A.I. is real and it could be as "
      "transformative as the internet'. Coded equity/long/US as in X-09 (single names not coded). The "
      "hard-landing view states no short.")),
]

REJECTED = {
    "DS/1992-XX-XX NMW; DS/2009 Feig (1997 rupiah)": "direction of the rupiah position not stated (seed C08)",
    "DS/2009 Feig (Brazil cut at the 2008 low)": "same undated 2008 period as C18; conflicts with its process target",
    "DS/2010-XX-XX Mallaby (1997 baht short)": "book not read; content from general knowledge, not the note",
    "DS/2012-04-XX Grant's (trouble after Twist)": "same event as C20",
    "DS/2013-05-08 Sohn (GOOG long, producers short)": "same event and date as C21/C22",
    "DS/2016-XX-XX Robin Hood PTJ (rising rates)": "year unverified; content duplicates C31 (short bonds)",
    "DS/2019-06-03 ECNY; RS/2019-06-03 Bloomberg": "same window and content as C36/C37",
    "DS/2021-05-10 WSJ op-ed; DS/2021-05-11 Hustle": "same window and content as C43",
    "DS/2021-06-10 email to CNBC": "no position or regime call beyond C42/C43, 3 trading days from C42",
    "DS/2024-10-16 Bloomberg": "same short-UST content as C53, 20 trading days later",
    "DS/2025-01-20 CNBC; DS/2025-04-06 X post": "views on growth and tariffs; no position or policy-direction call",
    "DS/2026-01-30 FT (Warsh)": "same day as C54; no position",
    "fiscal and biographical notes (2010 letter, 2013 op-eds and tour, 2017 Purdue/II, profiles)":
        "no dated market call, thesis or position",
}

if __name__ == "__main__":
    files = build(CASES_V2)
    print(f"wrote {len(files)} cases (v2 expansion); rejected {len(REJECTED)} candidate groups")
