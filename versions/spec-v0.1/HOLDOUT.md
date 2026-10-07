# Fat Pitch — Sealed Holdout

Date: 2026-10-06. Split file: `cases\HOLDOUT.yaml`, version 2 (written by `tools\make_holdout.py`; version 1 superseded by the documented re-seal below). Code: `src\fatpitch\cases\holdout.py`. Scoring rules: `spec\scoring.md` section 9.

## Purpose

The rules in `spec\` will change many times during research. Every engine run on a case that informs a rule change uses that case up as test evidence. About one third of the episodes are therefore sealed now; research runs the engine freely on the remaining cases; the sealed set is opened once, at the end, for the real Gate 1 and Gate 2 test.

## Rules

| Rule | Detail |
|---|---|
| Unit | Episodes (`episode_id`); an episode is never split |
| Default | `fatpitch.cases.load_corpus(root)` returns the research split; `tools\null_smoke.py` defaults to it |
| Sealed | `split="holdout"` or `split="all"` raises unless `unseal=True` is passed, the environment variable `FATPITCH_UNSEAL=1` is set and a non-empty `reason` is given |
| Unseal log | Each unseal appends one line to `cases\UNSEAL_LOG.txt`: UTC timestamp, user, split, holdout sha256, `sha_verified=yes`, reason. Append-only; never edited |
| Tamper check | Every load (research included) recomputes the holdout hash and raises `HoldoutError` on a mismatch with `HOLDOUT.yaml`: a changed byte, an added, removed or renamed holdout file, or a case moved into or out of a holdout episode |
| Research isolation | A research load reads only `episode_id` and the bytes of holdout files; their targets are never parsed or returned. Research turning points are derived on research cases only |
| Seal once | `holdout.create` refuses when `HOLDOUT.yaml` exists. `holdout.reseal` (`tools\make_holdout.py --reseal --reason ...`) redraws with the same method and seed and writes version n+1 with every earlier version's episodes and hashes under `previous`; it refuses when `cases\UNSEAL_LOG.txt` exists, so the split is never redrawn after the holdout has been opened |
| New cases | A new case in a research episode or a new episode lands in research. A new case in a holdout episode breaks the tamper check; adding holdout cases requires a documented re-seal (Re-seal log) before any unseal |
| Not registered | Nothing is registered with `fatpitch.prereg` and no run is logged by this step. `cases\HOLDOUT.yaml` is now in `fatpitch.prereg.PREREG_SET` (would-be PR-0006, `spec\PREREG.md`) and is registered with the rest of the set |

## Draw (version 2)

Seed 20261006, `numpy.random.default_rng`, every list sorted before each draw (method text in `HOLDOUT.yaml`, unchanged from version 1). Target: round(20 / 3) = 7 episodes. Strata, in order: (1) half (rounded up) of the 8 Gate 1 episodes, i.e. episodes with an era-A turning-point case with a regime target (`turning_point_ids` on the full corpus): 4 drawn (`EP09`, `EP14`, `EP15`, `EP16`); (2) exactly one of the two 13F episodes: `EP16` (C40) already drawn, `EP21` (C55) stays in research; (3) at least one era-B episode: `EP07` drawn; (4) fill to the target from the remaining episodes: `EP11`, `EP18`.

Holdout episodes: `EP07-2000-RATES`, `EP09-2008-CRISIS`, `EP11-2012-13-QE`, `EP14-2018-QT`, `EP15-2019-TARIFF`, `EP16-2020-COVID`, `EP18-2022-INFL`.

## Counts (version 2; turning points derived on the full corpus)

| Count | Research | Holdout | Total |
|---|---|---|---|
| Cases | 42 | 26 | 68 |
| Episodes | 13 | 7 | 20 |
| Era A cases / episodes | 32 / 8 | 25 / 6 | 57 / 14 |
| Era B cases / episodes | 10 / 5 | 1 / 1 | 11 / 6 |
| Turning points | 11 | 6 | 17 |
| Turning points with a regime target | 6 | 6 | 12 |
| Gate 1 subset (era A, turning point, regime target): cases / episodes | 6 / 4 | 6 / 4 | 12 / 8 |
| Thesis-target cases | 34 | 17 | 51 |
| Gate 2 subset (era A, thesis target): cases / episodes | 27 / 8 | 16 / 6 | 43 / 14 |
| 13F cases | 1 | 1 | 2 |
| truth_type process / action | 5 / 37 | 2 / 24 | 7 / 61 |
| mechanizable yes / partial / no | 34 / 1 / 7 | 24 / 1 / 1 | 58 / 2 / 8 |
| source_reliability primary / near-primary / secondary | 2 / 32 / 8 | 1 / 13 / 12 | 3 / 45 / 20 |

Research turning points derived on research cases only (the research-load definition): 10 (era A 9, era B 1); Gate 1 subset 6 cases in 4 episodes (same as the full-corpus derivation). Gate 1 cases by split: research `2006-12-29_left-the-party-2006` (EP08), `2015-03-02_long-japan-europe-2015` and `2015-04-16_just-like-2004-ruhle-2015` (EP12), `2022-03-07_hold-front-end-short-process-2022` (EP17), `2023-10-24_massive-two-year-long-2023` and `2023-12-28_two-year-exit-2023` (EP19); holdout: 6 cases in EP09, EP14, EP15, EP16 (ids not listed here; they are recorded in `HOLDOUT.yaml` counts only).

## Hashes (version 2)

Method: sha256 over sorted `relative_path NUL sha256(file bytes) LF` lines, paths relative to `cases\` (`fatpitch.cases.schema.corpus_sha256`, the same method as the corpus sha in `spec\corpus_manifest.txt`).

| Item | sha256 |
|---|---|
| Holdout case files (26) | `9d33be6b3a853f7d6b54df94c5aa2c3e1d6634329cc76af0316f0a26e5f54c1b` |
| Research case files at sealing (42) | `113024a092cda35461186507b7713886db4040262900ae3e63732845ebf504af` |
| All case files (68; equals `corpus_sha256` in `spec\corpus_manifest.txt`) | `f22261e8d9727ca2ffde328b8a7954710e1a27d18135a00e7308c4460ac1dc73` |
| `cases\HOLDOUT.yaml` file bytes (version 2) | `49e48edb139e65a675f9e9617cd578117e5831cfcfb0e9df5081d9331dfda2b8` |

Created 2026-10-06T20:14:51Z. The research hash is a record of the sealing state only; research cases may change without tripping the seal.

## Re-seal log

| Version | Created (UTC) | Episodes held out | Cases (holdout / research / all) | Holdout files sha256 | Research files sha256 | All files sha256 | `HOLDOUT.yaml` sha256 |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-06T19:59:33Z | EP01, EP09, EP13, EP15, EP16, EP17 | 19 / 37 / 56 | `867913efb0ba0fb67a59051b5563fc809adbdf2fc7f8fa72480b7c6eab061807` | `907861d5fab5cf2b4e510c12713b100edd46abc72a2aa268a567b732ae517430` | `8ff13ad73aceed22cfcb86180946c485d6c35547153966bd5f0b342eb3f87bae` | `902bf4aae713d566d2b1a0f8cbdc46a40badbfe7a3078f2f57f0b3eb3f9a896a` |
| 2 | 2026-10-06T20:14:51Z | EP07, EP09, EP11, EP14, EP15, EP16, EP18 | 26 / 42 / 68 | `9d33be6b3a853f7d6b54df94c5aa2c3e1d6634329cc76af0316f0a26e5f54c1b` | `113024a092cda35461186507b7713886db4040262900ae3e63732845ebf504af` | `f22261e8d9727ca2ffde328b8a7954710e1a27d18135a00e7308c4460ac1dc73` | `49e48edb139e65a675f9e9617cd578117e5831cfcfb0e9df5081d9331dfda2b8` |

v1 → v2 (2026-10-06). Reason: owner decision 2026-10-06 — expand the case corpus now and redraw the holdout with the same seeded method so both sets grow; done once, before any engine scoring. 12 cases added (`tools\build_cases_v2.py`, seed ids X-01 to X-12; 4 of them in v1 holdout episodes EP15, EP16, EP17, which broke the v1 tamper check by design). Preconditions checked: `cases\UNSEAL_LOG.txt` did not exist at the re-seal (the v1 holdout was never opened through `load_corpus`); no engine had been scored on any case; nothing was registered with `fatpitch.prereg` and no run was logged. Method and seed unchanged (`METHOD` text identical in both versions). The v1 record is kept in `HOLDOUT.yaml` under `previous` and in the table above. Disclosure: the v1 holdout targets were read by the pipeline only to compute v1 counts (no engine, no null on the holdout); the expansion cases were mined from library notes, not from v1 holdout files. A further re-seal is permitted only before the first unseal and only with a new row here.

## Power check (final Gate 1 on the holdout, version 2)

| Item | Value |
|---|---|
| Holdout Gate 1 cases (k) / episodes | 6 / 4 (v1: 7 / 5) |
| Smallest attainable one-sided paired p (2^-k, all 6 pairs differ in the engine's favour) | 2^-6 = 0.0156 (v1: 2^-7 = 0.0078) |
| Non-tied pairs needed for p < 0.10 | at least 4 (2^-3 = 0.125 fails; 2^-4 = 0.0625 passes) |
| Research Gate 1 cases / episodes (for iteration) | 6 / 4 (v1: 4 / 3) |

k = 6 meets the 5-case threshold, but the holdout Gate 1 subset is smaller than in v1 (7 / 5 → 6 / 4) while research grew (4 / 3 → 6 / 4): the expansion added one net Gate 1 case (12 vs 11; see below) and the stratified draw holds out ceil(8 / 2) = 4 of the 8 Gate 1 episodes, which this time hold 6 of the 12 cases. With 6 pairs, p < 0.10 needs at least 4 non-tied pairs, so at most 2 of the 6 holdout cases may tie with `null_trend_12m`. The 6 cases sit in 4 episodes, so the case-level p is optimistic relative to an episode-level test (`spec\scoring.md` section 7).

Target of the expansion (≥ 8 Gate 1 cases in each split) is not reached. Full corpus: 12 Gate 1 cases; ≥ 16 is the arithmetic minimum for 8 + 8, and because the draw is by episode (half of Gate 1 episodes, not cases) the realized split of a 16-case corpus need not be 8 / 8. At least 4 more era-A turning-point cases with a regime target are needed, and in practice more (6–8) with several new Gate 1 episodes, so that the episode draw leaves ≥ 8 cases on each side. Era-B cases do not count (Gate 1 is era A).

Net Gate 1 change from the expansion: +2 (`2015-04-16_just-like-2004-ruhle-2015`, rule (a) vs the neutral regime target of `2015-03-02_long-japan-europe-2015`; `2018-06-29_global-qe-to-zero-bearish-2018`, rule (a) vs the easing target of `2017-12-12_taylor-gap-radicalism-2017`), −1 (`2016-05-04_endgame-gold-2016` is no longer a turning point: its most recent earlier regime target is now the 2015-04-16 easing case, not the 2015-03-02 neutral case). Both the added 2015 turning point and the removed 2016 one turn on the `neutral` label of `2015-03-02_long-japan-europe-2015`, whose source states the same view (zero rates too loose, Fed should hike) as the 2015-01-20 and 2015-04-16 cases labelled `easing`; this label is flagged for owner review.

## How unsealing works (once, at the end)

1. Freeze the rules: register `spec\process.md`, `spec\registry.yaml`, `spec\transition_table.yaml`, `spec\corpus_manifest.txt`, `spec\scoring.md` and `cases\HOLDOUT.yaml` with `fatpitch.prereg` (`spec\PREREG.md`; `register-all` covers all six).
2. In PowerShell: `$env:FATPITCH_UNSEAL = "1"`.
3. Load: `load_corpus(r"cases", split="holdout", unseal=True, reason="final Gate 1/Gate 2 test, registration PR-....")`. The hash is verified first; a mismatch raises and nothing is logged.
4. Run the engine and the pre-chosen best null on the holdout Gate 1 and Gate 2 subsets through `fatpitch.prereg.record_run`; apply `paired_gate` (`spec\scoring.md` section 7).
5. Report the result whatever it is. Any rule change after this point is a design change: the holdout is spent and a new holdout would be needed for another confirmatory test.

`cases\UNSEAL_LOG.txt` is the audit trail: every line is an unseal; an empty or absent log means the holdout has not been opened.

## Candidate expansion (v1 list; disposition in version 2)

The nine era-A rows listed with version 1 (library survey 2026-10-06), with what the expansion did. DS = `library\discovered_sources\`, RS = `library\reference_sources\`.

| v1 candidate (date, source) | Disposition in v2 |
|---|---|
| ~2015-04-15, DS/2015-04-15_bloomberg-tv-stephanie-ruhle.md | Added: X-02 `2015-04-16_just-like-2004-ruhle-2015` (easing; Gate 1) |
| ~mid-2018, RS/2018-09-06_sokoloff-real-vision-interview.md | Added: X-04 `2018-06-29_global-qe-to-zero-bearish-2018` (tightening; Gate 1), with X-03 `2017-12-12_taylor-gap-radicalism-2017` (easing) as the earlier view |
| Q4 2019, DS/2019-12-18_bloomberg-schatzker-couldnt-have-been-more-wrong.md | Added: X-05 `2019-12-18_constructive-turn-q4-2019` (easing; not a turning point: same regime as 2019-06-07) |
| Aug–Oct 2020, DS/2021-05-11_cnbc-squawk-box-raging-mania-dollar.md; DS/2023-11-01_cnbc-squawk-box-yellen-debt-drunken-sailors.md | Added: X-07 `2020-10-30_relative-bets-commodities-short-bonds-2020` (easing; not a turning point) |
| 2020-09-09, DS/2020-09-09_cnbc-squawk-box-absolute-raging-mania.md | Added: X-06 `2020-09-09_raging-mania-inflation-2020` (easing, regime-only; not a turning point) |
| ~2021-02, DS/2021-02-XX_goldman-sachs-interview.md | Added: X-08 `2021-02-26_short-usd-goldman-2021` (thesis only; no regime call in the note) |
| Jun 2022 – Apr 2023 short USD | Not added: covered by existing 2022-06-10 and 2023-04-24 cases; no entry date in the notes |
| 2024-11-05/06, RS/2024-11-06_nbim-in-good-company-podcast.md | Added: X-11 `2024-11-06_inflation-second-wave-short-2024` (easing; not a turning point: same regime as 2024-09-18) |
| 2026-08-24, DS/2026-08-24_wsj-oped-let-the-bond-market-speak.md | Added: X-12 `2026-08-24_let-bond-market-speak-2026`, regime `easing` (policy judged too loose: Treasury-run QE, 10y ≤ nominal GDP), not `tightening` as the v1 row proposed: the corpus labels the policy stance as read (2003 and 2021 too-loose cases are `easing`), not the prescription; not a turning point |

Further cases added in v2 outside this list: X-01 `1988-03-28_still-bearish-barrons-1988` (era B, new episode use EP02-1988-BEAR), X-09 `2023-05-09_ai-long-hard-landing-sohn-2023`, X-10 `2024-05-07_japan-copper-long-2024`. Rejected candidates and reasons: `REJECTED` in `tools\build_cases_v2.py`.

Sources for further Gate 1 cases (not in the library; not fetched): events listed under "Known but not located" in `library\discovered_sources\_index.md` that could carry an era-A policy-direction call — the ~2005 Sohn Taylor-rule presentation (housing; would precede the 2005-12-30 and 2006-12-29 cases), the Feb 2021 Goldman Sachs interview recording, the mid-2014 WSJ op-ed with Warsh, the ~May 2021 WSJ op-ed with Broda, the Morgan Stanley US Financials conference (2022 or 2023), the ~2017-10-09 II-reported conference and a June 2017 Bloomberg Invest session, the 2023 "Coming Fiscal Horror Show" article, the Sohn 2016 transcript PDF and the ECNY 2020 Medium transcript (full text of existing events). Suggestions beyond that list, chosen because the corpus has no dated view where the Fed's direction changed: late 2015 to early 2016 (first hike of the cycle), H2 2019 (cuts), Nov 2021 to Mar 2022 (hawkish pivot), H2 2025 (cuts), and full transcripts of the 2016 Robin Hood conversation with Paul Tudor Jones, the 2018-12-18 Bloomberg interview and the 2019-12-18 Bloomberg interview (would pin dates now resolved conservatively).
