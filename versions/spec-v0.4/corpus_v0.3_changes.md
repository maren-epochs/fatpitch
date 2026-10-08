# Corpus changes for spec-v0.3: tightening and easing reads

Date: 2026-10-07. Scope: owner decision of 2026-10-07 (option A) on `library\research\tightening_sources.md`: add its six plausible tightening-read cases (section 2, rows 1 to 6) and its two easing by-product reads (December 1991, 2018-05-03). Built by `tools\build_cases_v2.py` (seed ids X-17 to X-24). Nothing was tagged.

Blindness. `spec\scoring.md`, the gate, turning-point and null code under `src\fatpitch\cases\` (beyond schema field names and vocabularies), and `results\` were not read. No turning points were computed, and no engine or null was run. Every target below was decided from the sources before the re-seal. Exposures, disclosed:

1. While locating sections of `spec\HOLDOUT.md` for editing, a grep displayed the v2 to v4 count blocks, Gate 1 and turning-point rows included. All eight targets had been decided before that output (the generator rows were written afterwards, unchanged in substance).
2. Locating the episode-draw code in `src\fatpitch\cases\holdout.py` (to check that episode ids are free labels) showed the `METHOD` text and the names of the stratification steps, not any counts.
3. After sealing, a post-write check of the new `spec\HOLDOUT.md` v5 count block used a faulty masking filter and displayed its two turning-point rows (Gate 1 and Gate 2 values were cut off). The cases were generated and the holdout sealed before that output.
4. `tools\make_holdout.py` output went to a scratch file; only version, episode list, hashes and non-gate count lines were displayed.

Labeling rule (unchanged from v0.2). `regime_direction` is the US monetary-policy stance as he read it at the information date. It is not his prescription and not the later outcome. The label follows the thesis region; when the source states no read for that region, the corpus uses his stated US read. Targets contain only what the source states.

Source text. The New Market Wizards passages were checked against the archive.org OCR text cited in `library\discovered_sources\1992-XX-XX_new-market-wizards-full-chapter-text.md` (re-downloaded 2026-10-07 to a scratch directory; not stored in the repository).

## 1. Summary

| Seed | Case | Split (v5) | Episode | Regime | Thesis | Expression | Action | Reliability | Retro |
|---|---|---|---|---|---|---|---|---|---|
| X-17 | `1981-06-30_half-cash-19pct-rates-1981` | research | EP01-1981-BONDS | tightening (implied) | equity/short/US | equity_us | reduce | primary | yes |
| X-18 | `1987-06-30_net-short-fed-tightening-1987` | research | EP22-1987-CRASH (new) | tightening | equity/short/US | equity_us | reverse | primary | yes |
| X-19 | `1989-12-29_nikkei-short-boj-1989` | holdout | EP23-1989-NIKKEI (new) | — | equity/short/JP | equity_jp | enter | primary | yes |
| X-20 | `1991-12-31_fed-panic-bond-exit-1991` | research | EP24-1991-EASE (new) | easing | — | rates_us | exit | primary | no |
| X-21 | `2018-05-04_rates-below-inflation-mi-2018` | holdout | EP14-2018-QT | easing | — | — | — | primary | no |
| X-22 | `2018-10-09_liquidity-going-down-grants-2018` | holdout | EP14-2018-QT | tightening | — | — | — | secondary | no |
| X-23 | `2018-11-23_qt-zombies-wsj-2018` | holdout | EP14-2018-QT | tightening | — | — | — | secondary | no |
| X-24 | `2023-06-07_more-shoes-ai-long-bloomberg-2023` | holdout | EP19-2023-RATES | tightening | equity/long/US | equity_us | hold | secondary | no |

All eight are `truth_type: action`, `mechanizable: yes`, no size band. Counts: 80 cases (72 + 8), 23 episodes (20 + 3). After the re-seal (version 5): 48 research and 32 holdout cases; 15 research and 8 holdout episodes.

Episodes. EP22 to EP24 are numbered in order of creation, because existing ids are fixed labels (EP05 stays assigned to the dropped 1997 case). No existing episode fits: EP02-1988-BEAR is the post-crash 1988 bear view, EP03-1988-89-DEM is the DEM trade, and nothing covers 1991. X-17 joins EP01-1981-BONDS, the same 1981 Volcker sequence that ends in the Q4 1981 bond trade (C01).

`REJECTED` in `tools\build_cases_v2.py` no longer lists Grant's 2018-10-09 ("same view and window as C32") or Bloomberg Invest 2023-06-07 ("same content as X-09"): the owner decision overrides both rejections.

## 2. Per case: quotes and reasoning

### X-17, mid-1981: 50% cash on 19% rates (NMW)

Quotes: "By mid-1981, stocks were up to the top of their valuation range, while at the same time, interest rates had soared to 19 percent. It was one of the more obvious sell situations in the history of the market. We went into a 50 percent cash position, which, at the time, I thought represented a really dramatic step. Then we got obliterated in the third quarter of 1981." / "You have to understand that I was unbelievably bearish in June 1981."

Date: conservative. "By mid-1981" plus "unbelievably bearish in June 1981", with Q3 1981 named as the period of the losses on the remaining half, puts the move no later than the end of June. Asof = 1981-06-30 16:00 ET, the last NYSE trading day of June 1981 and the latest date consistent with the text.

Regime: tightening, implied. He names no Fed action for mid-1981; his stated read is that rates "had soared to 19 percent". The owner decision accepted the implied read. Thesis equity/short/US records his stated bear view ("We have never felt more strongly about anything than the bear side of this market"). Action reduce: the move to 50% cash, with the other 50% still long, so no size band is coded (a 50% figure would describe the residual long, not the short view).

Duplicate check against C01 (`1981-12-31_long-bonds-volcker`): C01 is the Q4 1981 trade (remaining stocks dumped, 50% cash and 50% long bonds, "the Fed was extremely tight"). X-17 has a different date (six months earlier), asset (equities, not bonds) and action (reduce, not enter). Not a duplicate.

### X-18, June 1987: net short on Fed tightening (NMW)

Quotes: "In June I changed my stripes and actually went net short." / "The Fed had been tightening since January 1987, and the dollar was tanking, which suggested that the Fed was going to tighten some more." / "I never use valuation to time the market. I use liquidity considerations and technical analysis for timing."

Date: conservative, retrospective (`retrospective: true`). The source gives only the month. Asof = 1987-06-30 16:00 ET, the last NYSE trading day of June 1987. `date_basis` states this.

Targets: regime tightening (his explicit read). Thesis equity/short/US. Action reverse: Schwager's question "before you switched from long to short" and his answer confirm a long-to-short switch. Valuation (2.6% dividend yield, record price/book) and narrow breadth are recorded in notes. The 1987-10-16 switch to 130% long is a later technical trade with no new policy read and is not coded.

### X-19, late 1989: short Nikkei on BoJ tightening (NMW)

Quote: "Finally, and most important—three times as important as everything I just said—the Bank of Japan had started to dramatically tighten monetary policy. ... Shorting the Japanese stock market at that time was just about the best risk/reward trade I had ever seen."

Date: conservative, retrospective. "In late 1989" is read as Q4 1989; asof = 1989-12-29 16:00 ET, the last NYSE trading day of the quarter.

Targets: thesis equity/short/JP, expression equity_jp (Nikkei), action enter. No `regime_direction`: the corpus regime target is a read of US policy, and the source states no US read for late 1989. The BoJ tightening read is in the notes. This is a thesis-only case.

### X-20, December 1991: Fed "in a state of panic", long-bond exit (NMW)

Quotes: "In contrast, now with the economy in decline, the deficit ballooning, and the administration and the Fed in a state of panic, the public should be wary about the risk in holding long-term bonds." / "I was long until late 1991." / "Now, because money market rates are only 4.5 percent, the same poor public is back buying bonds".

Date: conservative. Schwager dates the interview "[at the time of this interview, December 1991]" with no day, and the exit is "late 1991". Asof = 1991-12-31 16:00 ET, the end of December 1991. The read is contemporaneous (`retrospective: false`).

Targets: regime easing (the Fed "in a state of panic" with short rates at 4.5%). Action exit, expression rates_us: the long-bond position was closed by late 1991. No thesis: "the public should be wary about the risk in holding long-term bonds" is advice to the public. He states no short position, so rates/short/US would add a direction the source does not state.

### X-21, 2018-05-03: rates below inflation (Manhattan Institute, primary)

Quotes: "This has meant that years after the Great Recession ended the Fed has not only kept interest rates below inflation but have accumulated an unprecedented $4.5 trillion on their balance sheet by doing QE." / "So, we are seeing an unprecedented, ultra-monetary, radical monetary expansion during a time of average, average inflation over the last number of centuries." / "I have no doubt we would have not gotten such a big increase in fiscal deficits if policy had been normalized already."

Date: conservative. The remarks were given at the Alexander Hamilton Award dinner on 2018-05-03. The source does not state the time, and a dinner can fall after the close. Asof = 2018-05-04 16:00 ET, the next NYSE close. The id therefore carries 2018-05-04.

Targets: regime easing. This is his read of the stance (rates below inflation, the balance sheet not normalized), although the Fed was hiking and runoff had begun. Regime-only: no position is stated. The critique of the 2% target is not coded.

### X-22, 2018-10-09: "liquidity is going down" (Grant's, secondary)

Quotes (HedgeFundAlpha headlines; notes explicitly non-verbatim): "It's all about liquidity, and liquidity is going down." / "The bombs are going to go off and things will be getting ugly."

Date: pinned to the conference day, 2018-10-09 (a daytime conference, as with X-15).

Targets: regime tightening (hikes plus QT plus the end of foreign QE, read as liquidity falling). Regime-only. The notes snippet "We are going to higher interest rates" is not verbatim and states no position or instrument, so no rates thesis is coded. The risk-off warning states no position. Previously rejected as "same view and window as C32" (2018-09-06); added by owner decision.

### X-23, ~2018-11-21: QT exposes zombies (WSJ via ForexLive, secondary relay)

Quotes (ForexLive quoting the WSJ): "As quantitative easing turns to quantitative tightening, all these zombies are going to be exposed." / "They're predicting we're in a very, very late cycle" (on defensives against cyclicals). Headline paraphrase: "Risky to be tightening now".

Date: conservative, resolving the ±1-day uncertainty to the later side. ForexLive relayed the WSJ quotes at 2018-11-22 04:12 GMT (2018-11-21 23:12 ET), so the WSJ text was public by then, probably after the 11-21 close. 2018-11-22 was a NYSE holiday (Thanksgiving). Asof = 2018-11-23, the first close at which the content was certainly public. That session closed early, at 13:00; the asof keeps the corpus 16:00 ET convention, which is noted in `date_basis`.

Targets: regime tightening (QE turning to QT, plus hikes). Regime-only. The call for the Fed to wait and "see what happens" is a prescription and is not coded. The WSJ original was not read.

### X-24, 2023-06-07: more shoes to drop; AI long (Bloomberg Invest, secondary)

Quotes (Fortune): "The biggest broadest asset bubble ever, and then you jack interest rates up 500 basis points in a year… Silicon Valley Bank, Bed Bath & Beyond, they're probably the tip of the iceberg." / "Our central case is there's more shoes to drop, particularly—in addition to the asset markets—economically." / "They haven't separated the wheat from the chaff yet, but I do believe, unlike crypto, that A.I. is real and it could be as transformative as the internet." Bloomberg clip title: "Druckenmiller on How AI is Dominating His Long Portfolio."

Date: pinned to the event, 2023-06-07; Fortune reported it the same day.

Targets: regime tightening (500bp of hikes in a year). Thesis equity/long/US, expression equity_us, action hold: the AI long as stated (the long book is dominated by AI). It is coded as X-09 codes the same holdings; single names (NVDA, MSFT) are not coded. The hard-landing view states no short, so none is coded. The 20-trading-day overlap with X-09 (2023-05-09) is the reason for the earlier rejection; added by owner decision.

## 3. Application

| Step | Result |
|---|---|
| Generator | `tools\build_cases_v2.py` (CRLF kept): constants `NMW`, `MI18`, `GRANTS18`, `WSJ18`, `BBGI23`; rows X-17 to X-24; two `REJECTED` entries removed |
| Validation | All 80 case files load with `fatpitch.cases.schema.load_case` |
| Byte check | Regenerating all 78 non-13F cases (`build_cases.py` 54, `build_cases_v2.py` 24) into a scratch directory matches `cases\` byte for byte; existing files unchanged; new files CRLF |
| `cases\UNSEAL_LOG.txt` before the re-seal | Absent |
| Re-seal | `tools\make_holdout.py --reseal --reason "spec-v0.3: 8 tightening/easing cases (owner decision 2026-10-07); holdout never opened"` → version 5, created 2026-10-07T07:24:53Z |
| Manifest | `python -m fatpitch.prereg manifest`: 80 cases, 23 episodes, corpus_sha256 `d7b08bb894591e07c23844b493274aae8313e14078e6f93b267cf14bb61bd1de` |
| Docs | `spec\HOLDOUT.md` (v5 draw, script-written counts, hashes, re-seal row and paragraph, power-check note); `spec\PREREG.md` (snapshot 2026-10-07T07:25:07Z, v5 seal paragraph, EP03 disclosure); `spec\cases_seed.md` (v0.3 additions) |

| Version | Holdout episodes | Cases holdout / research / all | Holdout files sha256 | Research files sha256 | `HOLDOUT.yaml` sha256 |
|---|---|---|---|---|---|
| 4 | EP02, EP07, EP10, EP14, EP16, EP17, EP19 | 24 / 48 / 72 | `891120244c786d0b3cb90bf290a5085b26b4975ea6374adcf25a929260913269` | `cbc5936cac10280066e0c8fdd2a55175a1bf4b93a8a38b8e593bb8d46c206fb3` | `ed247f26f81a3fbf93b263b9aff77cec0a8f64b3bbb43399e63b2a86c78cf1f3` |
| 5 | EP02, EP03, EP10, EP14, EP15, EP16, EP19, EP23 | 32 / 48 / 80 | `471996871e2bafb6fee5e34a0691bd1eda741373273795ca0693fb7c19ad6963` | `b4dd6e0cd0c9eb3269ce41da47d473d9112ef0f8524ca4d9c474a5abe0590bb8` | `071850950c2530334db99f4bc171938899bd49d5a0e9d6e8d467859383b68c18` |

What this means for the owner:

- Two episodes left the holdout (EP07, EP17) and are now research. Their targets were sealed but never loaded by an engine.
- Three entered (EP03, EP15, EP23). EP03 was in the research split of the unlogged null run of 2026-10-06T20:17Z (`spec\PREREG.md`). EP15 was in the version 2 holdout, so it was not in that run. EP23 is new.
- Five of the eight new cases are held out (X-19, X-21, X-22, X-23, X-24) and three are research (X-17, X-18, X-20).
- Research-split regime targets after v5 (counts only): tightening 6, easing 26, neutral 0, null 16 (48 cases).

## 4. Tests

`pytest -q`: 208 passed, holdout power assertion included. `ruff check` on the tracked files under `src` and `tests`: clean. `ruff check src tests` over the whole working tree reports 16 findings, all in untracked files from another work stream (`src\fatpitch\lake_coverage.py`, `tests\test_lake.py`), which this step neither changed nor committed.
