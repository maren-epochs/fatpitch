"""Convert spec\\cases_seed.md rows into cases\\<asof>_<slug>.yaml (phase E2).

The case table below is the reviewed transcription of the seed list. Targets describe what the source
says was believed or done at the time; outcome and hindsight columns of the seed and of the library
notes are not transcribed. The 13F cases (C40, C55) are built by ``tools\\build_13f_cases.py``.

Date resolution (``date_basis``):

* ``pinned``: the cited note gives the day (statement, publication or trade date). Weekend/holiday
  publication -> next NYSE trading day close (first close at which the information exists).
* ``conservative``: the note gives only a period (year, month, season, "around"); asof = last NYSE
  trading day of the stated period, or the latest date in it consistent with an anchor stated in the
  note (a price level, read from the FRED series named in the basis; or a later documented event that
  the decision preceded). Later is conservative: no information after the decision is attributed to a
  date before it.

    .\\.venv\\Scripts\\python.exe tools\\build_cases.py
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import yaml

from fatpitch.dates import et_close, is_trading_day

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cases"

LT = "RS/2015-01-18_lost-tree-club-speech.md"
FEIG = "DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md"
NBIM24 = "RS/2024-11-06_nbim-in-good-company-podcast.md"
DA14 = "DS/2014-07-16_delivering-alpha-kernen.md"
SOKO = "RS/2018-09-06_sokoloff-real-vision-interview.md"
OWB = "DS/2019-06-07_cnbc-squawk-box-one-way-bet.md"
CNBC24 = "DS/2024-05-07_cnbc-squawk-box-forward-guidance-ai-argentina.md"
SOHN16 = "DS/2016-05-04_sohn-the-endgame-archived-transcript.md"
SOHN22 = "DS/2022-06-XX_sohn-2022-john-collison.md"


def T(cls, direction, region=None):
    d = {"asset_class": cls, "direction": direction}
    if region:
        d["region"] = region
    return d


# seed, slug, asof, date_basis, episode, truth, mech, reliability, retrospective, regime, theses,
# expression, action, size_band, citation, notes
CASES = [
    ("C01", "long-bonds-volcker", "1981-12-31",
     ("conservative: Lost Tree gives the trade only as early Duquesne, Volcker era (short rates 18%, 30y at 14%); "
     "year 1981 per seed; asof = last trading day of 1981"),
     "EP01-1981-BONDS", "action", "yes", "near-primary", True, "tightening", [T("rates", "long", "US")],
     ["rates_us"], "enter", {"low": 50, "high": 50, "unit": "pct_nav"}, LT,
     ("Volcker's tightening (short rates 18%) read as credible ('there is no way this man was going to let "
      "inflation go'); 50% of capital in 30-year Treasuries.")),
    ("C03", "dem-short-size-up", "1988-12-30",
     "conservative: CardPlayer account (via NMW note) dates the deutsche-mark short only to 1988; last trading day of 1988",
     "EP03-1988-89-DEM", "action", "no", "secondary", True, None, [T("fx", "short", "DEM")],
     ["fx_dem"], "size_up", None, "RS/1992-XX-XX_new-market-wizards-chapter.md",
     "$1B short DM position doubled after Soros's challenge."),
    ("C04", "dem-long-reunification", "1989-11-30",
     "conservative: NMW note gives 'after the Berlin Wall fell' (1989-11-09) without a trade day; last trading day of Nov 1989",
     "EP03-1988-89-DEM", "action", "no", "primary", True, None, [T("fx", "long", "DEM")],
     ["fx_dem"], "enter", None, "DS/1992-XX-XX_new-market-wizards-schwager-chapter.md",
     "Long deutsche mark on reunification's monetary implications. Wording of the chapter unverified."),
    ("C05", "sterling-starter", "1992-08-31",
     "conservative: Lost Tree gives 'Sterling, Aug 1992' for the initial $1.5B short; last trading day of Aug 1992",
     "EP04-1992-ERM", "action", "no", "near-primary", True, None, [T("fx", "short", "GBP")],
     ["fx_gbp"], "enter", {"low": 20, "high": 25, "unit": "pct_nav"}, f"{FEIG}; {LT}; {NBIM24}",
     "Starter short GBP (ERM peg premise); invest-then-investigate."),
    ("C06", "sterling-size-up", "1992-09-16",
     ("conservative: escalation followed Schlesinger's comments and preceded sterling's ERM exit (all tellings); "
     "no day given; the latest defensible day is the ERM exit, 1992-09-16 (CardPlayer gives Sept. 15; later date used)"),
     "EP04-1992-ERM", "action", "no", "near-primary", True, None, [T("fx", "short", "GBP")],
     ["fx_gbp"], "size_up", {"low": 70, "high": 100, "unit": "pct_nav"}, f"{FEIG}; {LT}; {NBIM24}",
     "Size-up on the Bundesbank catalyst; band spans tellings ($5B of $7B to $7.5B of $7.5B)."),
    ("C07", "uk-concentric-circles", "1992-09-30",
     ("conservative: Feig note says gilts, MATIF and UK equities were bought 'afterward' (after the ERM exit); "
     "last trading day of Sep 1992"),
     "EP04-1992-ERM", "action", "partial", "near-primary", True, None,
     [T("rates", "long", "GB"), T("equity", "long", "GB")], ["rates_gb", "equity_gb"], "enter", None, FEIG,
     "Second-order expressions (concentric circles)."),
    ("C09", "internet-short-process", "1999-02-26",
     ("conservative: Lost Tree dates the $200M internet short to 'about February' 1999; asof = last NYSE trading "
      "day of Feb 1999. Feig and Sohn 2022 give 'March of '99'; February chosen by owner decision 2026-10-06 "
      "(spec/corpus_v0.2_changes.md)"),
     "EP06-1999-2000-TECH", "process", "yes", "near-primary", True, None, [], ["equity_us"], "flat", None,
     f"{LT}; {FEIG}",
     "Process target: rules R-29/R-62 block an equity short against an uptrend (no new short). His action was a short."),
    ("C10", "tech-exit", "2000-01-31",
     "conservative: Lost Tree/NBIM 2024 give 'Jan 2000' for selling all tech; last trading day of Jan 2000",
     "EP06-1999-2000-TECH", "action", "yes", "near-primary", True, None, [], ["equity_us"], "exit", None, LT,
     "Sold ~$6B of tech equities."),
    ("C11", "tech-reentry-process", "2000-03-31",
     "conservative: re-entry dated only to March 2000 (Lost Tree; Soros-exit note); last trading day of Mar 2000",
     "EP06-1999-2000-TECH", "process", "yes", "near-primary", True, None, [], ["equity_us"], "flat", None,
     f"{LT}; DS/2000-04-28_soros-quantum-exit-overplayed-hand.md",
     "Process target: weak internals (breadth) and chart veto block re-entry (R-29). His action was a re-entry."),
    ("C12", "two-year-notes-2000", "2000-09-29",
     ("conservative: 'after returning from sabbatical around Labor Day' (Feig) / 'Sept 2000' (NBIM 2024); "
     "last trading day of Sep 2000"),
     "EP07-2000-RATES", "action", "yes", "near-primary", True, "tightening", [T("rates", "long", "US")],
     ["rates_us"], "enter", {"low": 300, "high": 350, "unit": "pct_nav_10y_eq"},
     f"{FEIG}; DS/2022-06-XX_sohn-2022-john-collison.md; {NBIM24}",
     "Rates, oil and USD rising together (R-10); FF 6.5%; band spans 300% (Feig) to 350% (Sohn 2022, NBIM 2024)."),
    ("C13", "fed-too-loose-2003", "2003-12-31",
     "conservative: Lost Tree gives Q4 2003 for the fed-funds exercise; last trading day of 2003",
     "EP08-2003-06-LOOSE", "process", "yes", "near-primary", True, "easing", [], [], None, None, LT,
     "Process target: policy direction easing (FF 1%); policy-error sign too_loose (R-06) is not a scored component."),
    ("C14", "riding-policy-2005", "2005-12-30",
     "conservative: DA 2014 gives only 'made money in 2005 riding the policy'; last trading day of 2005",
     "EP08-2003-06-LOOSE", "action", "yes", "near-primary", True, "easing", [T("equity", "long", "US")],
     ["equity_us"], "hold", None, f"{DA14}; {SOHN16}; {LT}",
     ("Long equities riding loose policy ('I made a lot of money in '05 because I wanted to ride the overly "
      "aggressive policy'). Regime label easing: his 2005 read was a too-loose Fed (Sohn 2016 text: 'At the 2005 "
      "Ira Sohn Conference, looking at a more muted but similar deviation, I argued that the Greenspan Fed was "
      "sowing the seeds of an historical housing bubble'; Lost Tree: housing bust 'engendered by the Federal "
      "Reserve's too-loose monetary policy', figured out by mid-'05). Retrospective sources.")),
    ("C15", "left-the-party-2006", "2006-12-29",
     "conservative: DA 2014 gives only 'left the party in 2006'; last trading day of 2006",
     "EP08-2003-06-LOOSE", "action", "yes", "near-primary", True, None, [], ["equity_us"], "exit", None,
     f"{DA14}; {LT}",
     ("Left the party in 2006 ('I made a lot of money in '05 because I wanted to ride the overly aggressive "
      "policy. '06 I stunk. I had made some money but I left the party.'). No source states his read of 2006 "
      "policy (Lost Tree: returns 'weren't very good in '06 because I was a little early'), so no regime target; "
      "the dance-until-they-raise-rates line in DA 2014 is the host's framing of 2014, not a 2006 read.")),
    ("C16", "commodities-long-2008", "2008-03-31",
     "conservative: Feig gives 'In March 2008 ... after Bear Stearns'; last trading day of Mar 2008",
     "EP09-2008-CRISIS", "action", "yes", "near-primary", True, "easing", [T("commodity", "long")],
     ["commodity_global"], "enter", None, FEIG,
     "Long commodities: charts agreed with expected global liquidity, despite a bearish economic view."),
    ("C17", "commodities-exit-2008", "2008-06-30",
     "conservative: Feig gives 'around May/June' when charts turned 'dodgy'; last trading day of Jun 2008",
     "EP09-2008-CRISIS", "action", "yes", "near-primary", True, "easing", [], ["commodity_global"], "exit", None,
     FEIG, "Exit on chart deterioration (price action as exit input)."),
    ("C18", "brazil-rates-process", "2008-12-31",
     "conservative: Feig dates the Brazil add only to 2008; last trading day of 2008",
     "EP09-2008-CRISIS", "process", "yes", "near-primary", True, None, [], ["rates_br"], "hold", None, FEIG,
     "Process target: chart veto (R-29) blocks adding; existing position held. His action was an add against the chart."),
    ("C19", "liquidity-long-2009", "2009-12-31",
     "conservative: Feig talk dated by internal evidence to Q4 2009; last trading day of 2009",
     "EP10-2009-LIQ", "action", "yes", "near-primary", False, "easing", [T("equity", "long", "US")],
     ["equity_us"], "hold", None, FEIG,
     "Money growth above IP growth (R-02): stocks go up until a signal appears, despite a bearish macro view."),
    ("C20", "aud-short-gold-2012", "2012-04-30",
     "conservative: Grant's Spring Conference note dated 2012-04-XX; last trading day of Apr 2012",
     "EP11-2012-13-QE", "action", "yes", "secondary", False, "easing",
     [T("fx", "short", "AUD"), T("fx", "long", "USD"), T("commodity", "long", "GOLD")],
     ["fx_aud", "fx_usd", "commodity_gold"], "hold", None, "DS/2012-04-XX_grants-spring-conference-jim-grant.md",
     "Short AUD, long USD, gold via options (attendee notes)."),
    ("C21", "japan-long-sohn-2013", "2013-05-08",
     "pinned: Sohn 2013 talk date (note date)",
     "EP11-2012-13-QE", "action", "yes", "secondary", False, "easing", [T("equity", "long", "JP")],
     ["equity_jp"], "hold", None, "DS/2013-05-08_sohn-commodities-conundrum.md",
     "Long Japan (real estate, banks) as BoJ QE starts."),
    ("C22", "aud-short-sohn-2013", "2013-05-08",
     "pinned: Sohn 2013 talk date (note date)",
     "EP11-2012-13-QE", "action", "yes", "secondary", False, "easing", [T("fx", "short", "AUD")],
     ["fx_aud"], "hold", None, "DS/2013-05-08_sohn-commodities-conundrum.md",
     "Short AUD; commodity producers vs consumers."),
    ("C23", "no-taper-risk-long-2013", "2013-09-19",
     "pinned: CNBC interview date (note date)",
     "EP11-2012-13-QE", "action", "yes", "secondary", False, "easing", [T("equity", "long", "US")],
     ["equity_us"], "hold", None, "DS/2013-09-19_cnbc-squawk-box-fed-wealth-transfer.md",
     "Risk assets held under continued QE (implied)."),
    ("C24", "eur-short-entry-2014", "2014-05-08",
     ("conservative: Sokoloff notes give 'did a lot at 139' in 2014 without a day; latest 2014 date with EURUSD "
     "(FRED DEXUSEU) in 1.385-1.395 is 2014-05-08"),
     "EP12-2014-15-DIVERGE", "action", "yes", "near-primary", True, None, [T("fx", "short", "EUR")],
     ["fx_eur"], "enter", None, f"{SOKO}; DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md",
     "Short EUR on ECB easing vs Fed taper (policy divergence)."),
    ("C24b", "eur-short-size-up-2014", "2014-07-24",
     ("conservative: Sokoloff notes give 'got a lot more brave at 135' in 2014; latest 2014 date with EURUSD "
     "(FRED DEXUSEU) in 1.345-1.355 is 2014-07-24"),
     "EP12-2014-15-DIVERGE", "action", "yes", "near-primary", True, None, [T("fx", "short", "EUR")],
     ["fx_eur"], "size_up", None, SOKO, "Size-up of the EUR short (split from seed C24)."),
    ("C25", "still-dancing-2014", "2014-07-16",
     "pinned: Delivering Alpha 2014 interview date (note date)",
     "EP12-2014-15-DIVERGE", "action", "yes", "near-primary", False, "easing", [T("equity", "long", "US")],
     ["equity_us"], "hold", None, DA14, "Long equities with fragility alert; liquid book ('I can get out in a week')."),
    ("C26", "lost-tree-eur-short-2015", "2015-01-20",
     "pinned: Lost Tree speech 2015-01-18 (Sunday); next trading day close (2015-01-19 market holiday)",
     "EP12-2014-15-DIVERGE", "action", "yes", "near-primary", False, "easing", [T("fx", "short", "EUR")],
     ["fx_eur"], "hold", None, LT,
     ("Not net short equities (alerts, not timing); EUR short held. Regime label easing: ECB 'going to print "
      "money' (thesis region EUR); US zero rates judged too loose. Relative-policy case.")),
    ("C27", "long-japan-europe-2015", "2015-03-02",
     "pinned: CNBC Closing Bell interview date (note date)",
     "EP12-2014-15-DIVERGE", "action", "yes", "near-primary", False, "easing",
     [T("equity", "long", "JP"), T("equity", "long", "EA")], ["equity_jp", "equity_ea"], "hold", None,
     "DS/2015-03-02_cnbc-closing-bell-kelly-evans.md",
     ("Most net long outside the US, where QE is starting (FX-hedged). Regime label easing refers to BoJ/ECB "
      "('very, very expansive... they're doing QE'), the thesis region; US read was 'most aggressive monetary "
      "policy since 1913' with tightening anticipated, not yet begun. Relative-policy (divergence) rationale.")),
    ("C28", "sidelines-2015", "2015-11-04",
     "pinned: DealBook conference date (note date)",
     "EP12-2014-15-DIVERGE", "action", "yes", "secondary", False, None, [T("fx", "short", "EUR")],
     ["fx_eur"], "flat", None, "DS/2015-11-04_nyt-dealbook-conference-sorkin.md",
     "Equities flat ('sidelines') with a bearish skew; EUR short."),
    ("C29", "endgame-gold-2016", "2016-05-04",
     "pinned: Sohn 2016 talk date (note date)",
     "EP13-2016-REGIME", "action", "yes", "primary", False, "easing",
     [T("commodity", "long", "GOLD"), T("equity", "short", "US")], ["commodity_gold"], "hold", None,
     f"{SOHN16}; DS/2016-05-04_sohn-the-endgame.md",
     ("Policy too loose ('the biggest and longest dovish deviation from historical norms I have seen in my "
      "career'); gold 'remains our largest currency allocation'; equities: 'the bull market is exhausting itself', "
      "risk/reward 'negative without substantially lower prices'. Source: full prepared text (archived Sohn PDF).")),
    ("C30", "gold-exit-election", "2016-11-09",
     "pinned: gold sold on election night 2016-11-08 after the close; first close after the sale is 2016-11-09",
     "EP13-2016-REGIME", "action", "no", "near-primary", False, None, [], ["commodity_gold"], "exit", None,
     "DS/2016-11-10_cnbc-squawk-box-post-election-sold-gold.md",
     "Premise break on the election result (political catalyst)."),
    ("C31", "post-election-reversal", "2016-11-10",
     "pinned: CNBC interview date (note date)",
     "EP13-2016-REGIME", "action", "no", "near-primary", False, None,
     [T("rates", "short"), T("fx", "long", "USD"), T("fx", "short", "EUR"), T("equity", "long", "US")],
     ["rates_us", "fx_usd", "fx_eur"], "enter", None,
     "DS/2016-11-10_cnbc-squawk-box-post-election-sold-gold.md",
     "Short global bonds (UST, Bunds, gilts, BTPs); long USD vs EUR; long value and materials."),
    ("C32", "qt-reduce-2018", "2018-09-06",
     "pinned: Real Vision interview date per RS note",
     "EP14-2018-QT", "action", "yes", "near-primary", False, "tightening", [], ["equity_us"], "reduce", None,
     f"{SOKO}; DS/2018-10-09_grants-fall-conference-jim-grant.md",
     "QT plus hikes while global QE goes to zero: reduce equities."),
    ("C33", "pause-oped-2018", "2018-12-17",
     "pinned: WSJ op-ed online Sunday 2018-12-16 afternoon; next trading day close",
     "EP14-2018-QT", "action", "yes", "secondary", False, "tightening", [], [], None, None,
     "DS/2018-12-16_wsj-oped-warsh-fed-tightening-not-now.md",
     ("Fed should 'cease--for now--its double-barreled blitz of higher interest rates and tighter liquidity' "
      "(regime read tightening). The op-ed states no position; no source dated on or before the asof states one, "
      "so no thesis or expression (regime-only case). His Treasury long is first stated in the Bloomberg TV "
      "interview of 2018-12-18, after the asof.")),
    ("C34", "fed-pivot-process-2019", "2019-01-30",
     "pinned: FOMC pivot date named in the seed (Fed pause); statement source is retrospective (Dec 2019)",
     "EP15-2019-TARIFF", "process", "yes", "secondary", True, "easing", [T("equity", "long", "US")],
     ["equity_us"], "enter", None, "DS/2019-12-18_bloomberg-schatzker-couldnt-have-been-more-wrong.md",
     "Process target: T01 (policy easing) implies long equities. His positioning was timid."),
    ("C35", "tariff-net-flat-2019", "2019-05-08",
     ("conservative: de-risking after the 2019-05-05 tariff tweet was spread over three days (note); third trading "
     "day 2019-05-08"),
     "EP15-2019-TARIFF", "action", "no", "near-primary", True, None, [], ["equity_us"], "flat", None, OWB,
     "From over 90% invested to net flat on a political event."),
    ("C36", "two-year-one-way-bet-2019", "2019-05-21",
     ("conservative: entry after the tariff tweet with 2y at ~2.30% (note); latest May 2019 date with DGS2 in "
     "2.25-2.35 is 2019-05-21"),
     "EP15-2019-TARIFF", "action", "yes", "near-primary", True, None, [T("rates", "long", "US")],
     ["rates_us"], "enter", None, OWB, "One-way bet: cuts not priced vs FF."),
    ("C37a", "fed-repivot-equities-2019", "2019-06-07",
     "pinned: CNBC interview date (note date)",
     "EP15-2019-TARIFF", "action", "yes", "near-primary", False, "easing", [T("equity", "long", "US")],
     ["equity_us"], "size_up", None, OWB, "Re-risk equities on the Fed repivot (split from seed C37)."),
    ("C37b", "two-year-reduce-2019", "2019-06-07",
     "pinned: CNBC interview date (note date)",
     "EP15-2019-TARIFF", "action", "yes", "near-primary", False, "easing", [], ["rates_us"], "reduce", None, OWB,
     "Reduce the 2y long: asymmetry gone at 1.85% (split from seed C37)."),
    ("C38", "worst-risk-reward-2020", "2020-05-12",
     "pinned: Economic Club of New York webcast date (note date)",
     "EP16-2020-COVID", "action", "yes", "secondary", False, None, [], ["equity_us"], "reduce", None,
     "RS/2020-05-12_economic-club-of-new-york.md; DS/2020-05-12_econclub-ny-webcast.md",
     "Equity risk/reward the worst of his career; liquidity read turning negative."),
    ("C39", "constructive-reversal-2020", "2020-06-08",
     "pinned: CNBC interview date (note date)",
     "EP16-2020-COVID", "action", "yes", "secondary", False, "easing", [T("equity", "long", "US")],
     ["equity_us"], "reverse", None, "DS/2020-06-08_cnbc-squawk-box-humbled-underestimated-fed.md",
     "Reversal to constructive (Fed support, breadth thrust)."),
    ("C41", "rotation-bitcoin-2020", "2020-11-09",
     "pinned: CNBC interview date (note date)",
     "EP16-2020-COVID", "action", "yes", "secondary", False, "easing",
     [T("equity", "long", "US"), T("commodity", "long", "GOLD"), T("crypto", "long", "BTC")],
     ["equity_us", "commodity_gold", "crypto_btc"], "hold", None, "RS/2020-11-09_cnbc-the-exchange-rotation.md",
     "Long value (not net short), gold and miners, bitcoin."),
    ("C42", "short-front-end-2021", "2021-06-15",
     ("conservative: NBIM 2024 gives 'spring 2021' with 2y at 15 bp; latest date to 2021-06-18 (end of spring) "
     "with DGS2 in 0.13-0.17 is 2021-06-15"),
     "EP17-2021-MANIA", "action", "yes", "near-primary", True, "easing", [T("rates", "short", "US")],
     ["rates_us"], "enter", None, NBIM24, "Policy too loose with inflation rising: short 2-year notes."),
    ("C43", "raging-mania-reduce-2021", "2021-05-11",
     "pinned: CNBC interview date (note date)",
     "EP17-2021-MANIA", "action", "yes", "near-primary", False, "easing",
     [T("rates", "short", "US"), T("commodity", "long"), T("fx", "long", "USD")], ["equity_us"], "reduce", None,
     "DS/2021-05-11_cnbc-squawk-box-raging-mania-dollar.md; DS/2021-05-11_hustle-mfm-trung-phan.md",
     ("Equity exposure far below four or five months earlier; relative bets 'into commodities, into interest "
      "rates, into the dollar'. Leg directions are inferred from 'our other asset categories... would be the "
      "cause of this stock market bubble popping' (commodities, rates and dollar up); USD direction not stated "
      "outright.")),
    ("C44", "hold-front-end-short-process-2022", "2022-03-07",
     ("conservative: NBIM 2024 says most of the 2y short was taken off at ~150 bp, no date; latest Q1 2022 date with "
     "DGS2 in 1.40-1.60 is 2022-03-07"),
     "EP17-2021-MANIA", "process", "yes", "near-primary", True, "easing", [T("rates", "short", "US")],
     ["rates_us"], "hold", None, f"{NBIM24}; {SOHN22}",
     ("Process target: premise (policy too loose, inflation) intact, so the short is held (R-49). His action took "
      "most off. Regime label easing: his read of policy in March 2022 was still loose ('they were still buying "
      "bonds in March of 22', Sohn 2022, retrospective); no contemporaneous statement.")),
    ("C45", "waiting-for-fat-pitch-2022", "2022-06-10",
     "pinned: Sohn 2022 release date 2022-06-10 (RS note); recording date unknown, release date is the latest defensible",
     "EP18-2022-INFL", "action", "yes", "near-primary", False, "tightening",
     [T("commodity", "long", "OIL"), T("commodity", "long", "COPPER")], ["commodity_oil", "commodity_copper"],
     "flat", None, "DS/2022-06-XX_sohn-2022-john-collison.md; RS/2022-06-10_sohn-2022-collison-conversation.md",
     "Low conviction; equities flat-to-short; waiting for a fat pitch."),
    ("C46", "sidestep-2022", "2022-09-28",
     "pinned: Delivering Alpha 2022 interview date (note date)",
     "EP18-2022-INFL", "action", "yes", "near-primary", False, "tightening", [], ["equity_us"], "flat", None,
     "DS/2022-09-28_delivering-alpha-kernen-transcript.md", "Do not short, sidestep."),
    ("C47", "no-fat-pitch-2023", "2023-04-24",
     "pinned: NBIM 2023 conference date (note date)",
     "EP19-2023-RATES", "action", "yes", "near-primary", False, "tightening",
     [T("fx", "short", "USD"), T("commodity", "long", "GOLD"), T("rates", "short", "JP")],
     ["fx_usd", "commodity_gold", "rates_jp"], "flat", None, "DS/2023-04-24_nbim-annual-investment-conference.md",
     "No fat pitch; net equity about -3%; small relative positions."),
    ("C48", "massive-two-year-long-2023", "2023-10-24",
     "pinned: Robin Hood conference fireside date (note date)",
     "EP19-2023-RATES", "action", "yes", "near-primary", False, "tightening", [T("rates", "long", "US")],
     ["rates_us"], "enter", None, f"DS/2023-10-24_robin-hood-paul-tudor-jones.md; {CNBC24}",
     "Massive leveraged long 2-year notes (something breaks, Fed cuts)."),
    ("C49", "debt-supply-short-2023", "2023-11-01",
     "pinned: CNBC interview date (note date)",
     "EP19-2023-RATES", "action", "yes", "near-primary", False, "tightening", [T("rates", "short", "US")],
     ["rates_us"], "hold", None, "DS/2023-11-01_cnbc-squawk-box-yellen-debt-drunken-sailors.md",
     ("Short long-end Treasuries on debt supply (R-63): 'I made a lot of money this year betting on bonds going "
      "down because of the debt'. Whether the short was still held on 2023-11-01 is not stated (the host "
      "describes a curve trade; C48 records a long 2-year a week earlier).")),
    ("C50", "two-year-exit-2023", "2023-12-28",
     ("conservative: exit after the Dec 2023 pivot (FOMC 2023-12-13) at ~4.30% (CNBC 2024-05-07); latest Dec 2023 "
     "date with DGS2 in 4.25-4.35 is 2023-12-28"),
     "EP19-2023-RATES", "action", "yes", "near-primary", True, "easing", [], ["rates_us"], "exit", None, CNBC24,
     "Exit: the tight-financial-conditions premise broke after the pivot (R-58)."),
    ("C51", "argentina-invest-then-investigate", "2024-01-31",
     "conservative: entry after Milei's Davos speech (Jan 2024), no day; last trading day of Jan 2024",
     "EP20-2024-CUT", "action", "no", "near-primary", True, None, [T("equity", "long", "AR")], ["equity_ar"],
     "enter", None, CNBC24, "Five most liquid Argentine ADRs on a political catalyst."),
    ("C52", "nvidia-hold-process-2024", "2024-03-28",
     "conservative: CNBC 2024-05-07 note dates the Nvidia cut to late March 2024; last trading day of Mar 2024",
     "EP20-2024-CUT", "process", "yes", "near-primary", True, None, [T("equity", "long", "US")], ["equity_us"],
     "hold", None, f"{CNBC24}; DS/2024-10-16_bloomberg-tv-sonali-basak.md; DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md",
     "Process target: no exit on valuation while premises intact (R-49/R-52). His action sold."),
    ("C53", "short-treasuries-at-cut-2024", "2024-09-18",
     "pinned: 'We shorted bonds the day the Fed cut fifty' (Bloomberg 2024-10-16); FOMC 2024-09-18",
     "EP20-2024-CUT", "action", "yes", "near-primary", True, "easing", [T("rates", "short", "US")],
     ["rates_us"], "enter", {"low": 25, "high": 25, "unit": "pct_nav_10y_eq"},
     f"DS/2024-10-16_bloomberg-tv-sonali-basak.md; {NBIM24}",
     "Easing into loose financial conditions; 10y below nominal GDP (R-56)."),
    ("C54", "short-usd-copper-2026", "2026-01-30",
     "pinned: Morgan Stanley interview recorded 2026-01-30 (note; released 2026-02-27)",
     "EP21-2025-26-ROTATE", "action", "yes", "near-primary", False, "easing",
     [T("fx", "short", "USD"), T("commodity", "long", "COPPER"), T("rates", "short", "US"),
      T("equity", "long", "JP"), T("equity", "long", "KR")], ["fx_usd", "commodity_copper", "equity_jp"], "hold",
     None, "DS/2026-02-27_morgan-stanley-hard-lessons-bouzali.md",
     "Short USD, long copper, UST short as hedge, long Japan/Korea."),
    ("C56", "ai-trim-fx-short-2026", "2026-09-10",
     "pinned: Piper Sandler event date (note date)",
     "EP21-2025-26-ROTATE", "action", "yes", "secondary", False, "easing",
     [T("fx", "short", "EUR"), T("fx", "short", "GBP")], ["equity_us", "fx_eur", "fx_gbp"], "reduce", None,
     "DS/2026-09-10_piper-sandler-closed-door-event.md",
     ("Reduce AI holdings to ~20% of the level six months earlier; short EUR and GBP at smaller size. Regime label "
      "easing: US rates 'at best too low', cuts 'no longer necessary' (FT report via aggregators). The only policy "
      "read stated is the Fed's; none for the ECB or BoE (FX theses), so the US read is used, as in X-10.")),
]

DROPPED = {
    "C02": "process target is the R-02 output at 1988-03-28, which depends on the tunable "
           "liq.m2_ip.spread_pp; no fixed target exists before calibration, and his stance is not the target",
    "C08": "process target is a size constraint (R-45) with no numeric band; the cited note does not state the "
           "rupiah position's direction",
}


def build(rows=None, out: Path | None = None) -> list[Path]:
    """Write one YAML per row (default: ``CASES`` into ``cases/``). ``tools/build_cases_v2.py`` reuses this
    writer for the 2026-10-06 expansion rows, so both sets share one serialization."""
    rows = CASES if rows is None else rows
    out = OUT if out is None else out
    out.mkdir(exist_ok=True)
    written = []
    for (seed, slug, asof, basis, ep, truth, mech, rel, retro, regime, theses, expr, action, size, cite,
         notes) in rows:
        d = dt.date.fromisoformat(asof)
        if not is_trading_day(d):
            raise SystemExit(f"{seed}: {asof} is not a trading day")
        cid = f"{asof}_{slug}"
        doc = {
            "id": cid,
            "asof": et_close(d).isoformat(),
            "era": "A" if d.year >= 2002 else "B",
            "episode_id": ep,
            "truth_type": truth,
            "mechanizable": mech,
            "source_reliability": rel,
            "retrospective": retro,
            "targets": {"regime_direction": regime, "theses": theses, "expression": expr, "action": action,
                        **({"size_band": size} if size else {})},
            "window": {"unit": "business_days", "n": 20},
            "citation": cite,
            "date_basis": basis,
            "seed_id": seed,
            "notes": notes,
        }
        path = out / f"{cid}.yaml"
        path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":
    files = build()
    print(f"wrote {len(files)} cases; dropped {sorted(DROPPED)}")
