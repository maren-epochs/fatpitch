# Fat Pitch — Pre-registration record

## Pending — not registered (awaiting owner review)

Owner decision 2026-10-06: nothing is registered with `fatpitch.prereg` until the owner has reviewed the rules. `prereg\preregistrations.csv` and `prereg\run_log.csv` do not exist yet. No engine scoring run and no logged run has taken place.

Would-be registration set (`fatpitch.prereg.PREREG_SET`, six files since 2026-10-06: `cases/HOLDOUT.yaml` added), sha256 of the file bytes, computed 2026-10-07T07:25:07Z after the spec-v0.3 corpus addition (8 tightening/easing cases, X-17 to X-24) and holdout re-seal version 5 (`spec\corpus_v0.3_changes.md`) (SNAPSHOT; superseded by any later edit):

| Would-be id | File | sha256 |
|---|---|---|
| PR-0001 | `spec/process.md` | `27fa06b56734dd33f89098386e92c124aafdaa98bf0d42c80e3238348bdf0408` |
| PR-0002 | `spec/registry.yaml` | `c1600c4aace9ba51b8bf367a58d9e093011aad3ec24d8fd2ff925b51d63698d4` |
| PR-0003 | `spec/transition_table.yaml` | `2e320815a183da3751f65f63eaa15e38abdf981bc61f4a7caff8dae1fa43282e` |
| PR-0004 | `spec/corpus_manifest.txt` | `04b5471960ba892c18210b92088cab35c233714837620f5a555c0c8d7d437069` |
| PR-0005 | `spec/scoring.md` | `0b367a5282790010be0b1d850aed5c6676d3e9283b67e7a1424f3588eb68ac3a` |
| PR-0006 | `cases/HOLDOUT.yaml` (sealed research/holdout split, version 5, `spec/HOLDOUT.md`) | `071850950c2530334db99f4bc171938899bd49d5a0e9d6e8d467859383b68c18` |

| Derived value | Value |
|---|---|
| Case corpus sha256, all case files (`fatpitch.cases.holdout.full_digest`; sorted `relative_path NUL file_sha256 LF` lines over `cases\*.yaml`) | `d7b08bb894591e07c23844b493274aae8313e14078e6f93b267cf14bb61bd1de` (80 cases, 23 episodes; turning points derived, not stored, not recounted in the v0.2 and v0.3 steps). Before the spec-v0.3 cases: `bd2c44cbc91ffdd1bece3f1a4c1469a5f677869f4fc7d4f58c23ca68b6c6c1c1` (72 cases, 20 episodes). Before the 2018-12-18 case: `7117930e54ff4518b362431157958ac0c473eae1da50486bce6c9e89b064e904` (71 cases). Spec-v0.1 corpus: `f22261e8d9727ca2ffde328b8a7954710e1a27d18135a00e7308c4460ac1dc73` (68 cases, 20 episodes). Before the expansion: `8ff13ad73aceed22cfcb86180946c485d6c35547153966bd5f0b342eb3f87bae` (56 cases, 19 episodes) |
| Holdout split (`cases/HOLDOUT.yaml` version 5) | 8 of 23 episodes, 32 of 80 cases; holdout files sha256 `471996871e2bafb6fee5e34a0691bd1eda741373273795ca0693fb7c19ad6963`; research files sha256 at sealing `b4dd6e0cd0c9eb3269ce41da47d473d9112ef0f8524ca4d9c474a5abe0590bb8`. Superseded, kept under `previous`: version 4 (7 of 20 episodes, 24 of 72 cases, holdout files `891120244c786d0b3cb90bf290a5085b26b4975ea6374adcf25a929260913269`, file `ed247f26f81a3fbf93b263b9aff77cec0a8f64b3bbb43399e63b2a86c78cf1f3`); version 3 (same 7 episodes, 23 of 71 cases, holdout files `e2a0f283c1cee71d7360525c51a3406993056a7d4aafff16e2c2fbfcda4152fd`, file `f72f81a2d52d1bb18ed49cca2e0ceb1d5fdf1c913e26a342089b73a1b3c0e079`); version 2 (7 of 20 episodes, 26 of 68 cases, holdout files `9d33be6b3a853f7d6b54df94c5aa2c3e1d6634329cc76af0316f0a26e5f54c1b`, file `49e48edb139e65a675f9e9617cd578117e5831cfcfb0e9df5081d9331dfda2b8`); version 1 (6 of 19 episodes, holdout files `867913efb0ba0fb67a59051b5563fc809adbdf2fc7f8fa72480b7c6eab061807`, file `902bf4aae713d566d2b1a0f8cbdc46a40badbfe7a3078f2f57f0b3eb3f9a896a`) |
| Parameter registry content sha (`fatpitch.registry.Registry.sha256`, formatting-independent) | recompute with `python -c "from fatpitch import registry; print(registry.load_default().sha256)"` at registration time |

`spec/process.md` and `spec/registry.yaml` were still being edited by the E1 evidence-pass work stream while these hashes were taken; the values above are a snapshot, not a commitment. The registration step recomputes them.

## Registration procedure (one step, after review)

```powershell
cd C:\Users\<user>\Documents\druckenmiller
.\.venv\Scripts\python.exe -m fatpitch.prereg manifest       # only if cases\ changed; review the diff
.\.venv\Scripts\python.exe -m fatpitch.prereg pending        # hashes that will be registered
.\.venv\Scripts\python.exe -m fatpitch.prereg register-all   # writes prereg\preregistrations.csv, prints ids
```

`register-all` refuses to run if `spec\corpus_manifest.txt` does not match `cases\` or if `spec\registry.yaml` fails validation (citations resolved against `library\`). After registration, replace the "Pending" table with the printed ids and hashes, and route every scoring run (nulls included) through `fatpitch.prereg.record_run`.

## Unlogged pipeline check

`tools\null_smoke.py` ran the nulls over the corpus twice on 2026-10-06 (07:56Z full corpus; 08:06Z full corpus, turning-point subset and 13F tilt baselines) as unlogged pipeline checks (owner decision: outside `record_run`). They are not registered trials and involve no engine.

## Holdout seal

`cases\HOLDOUT.yaml` version 1 was written 2026-10-06T19:59:33Z by `tools\make_holdout.py`; version 2 replaced it at 2026-10-06T20:14:51Z (`tools\make_holdout.py --reseal`) after the owner-approved corpus expansion (12 cases, `tools\build_cases_v2.py`), before any engine scoring and with `cases\UNSEAL_LOG.txt` absent (`spec\HOLDOUT.md` Re-seal log). `fatpitch.prereg.PREREG_SET` now lists `cases/HOLDOUT.yaml`, so `register-all` registers it as PR-0006 together with the other five files. Nothing is registered yet.

Version 3 replaced version 2 at 2026-10-06T21:01:57Z (`tools\make_holdout.py --reseal --reason "spec-v0.2 corpus corrections (owner decisions 2026-10-06); holdout never opened"`), with `cases\UNSEAL_LOG.txt` absent and no engine scoring run. Trigger: the v0.2 corrections changed one v2 holdout file (`2018-12-17_pause-oped-2018`), which breaks the tamper check by design; the same seeded method redrew the episodes (`spec\HOLDOUT.md` Re-seal log, `spec\corpus_v0.2_changes.md`).

Version 4 replaced version 3 at 2026-10-07T05:35:12Z (`tools\make_holdout.py --reseal --reason "spec-v0.2: add 2018-12-18 Treasury-long case (owner decision 2026-10-07); holdout never opened"`), with `cases\UNSEAL_LOG.txt` absent and no engine scoring run. Trigger: the new case `2018-12-18_treasury-long-bloomberg-2018` (X-16) lies in holdout episode `EP14-2018-QT`, which breaks the tamper check by design. The redraw kept the same seven episodes; the research files are unchanged (`spec\HOLDOUT.md` Re-seal log, `spec\corpus_v0.2_changes.md` section 8).

Version 5 replaced version 4 at 2026-10-07T07:24:53Z (`tools\make_holdout.py --reseal --reason "spec-v0.3: 8 tightening/easing cases (owner decision 2026-10-07); holdout never opened"`), with `cases\UNSEAL_LOG.txt` absent and no engine scoring run. Trigger: four of the eight new cases (X-17 to X-24) lie in holdout episodes `EP14-2018-QT` and `EP19-2023-RATES`, which breaks the tamper check by design, and three new episodes raised the episode count from 20 to 23. The redraw holds out EP02, EP03, EP10, EP14, EP15, EP16, EP19 and EP23; EP07 and EP17 returned to research (`spec\HOLDOUT.md` Re-seal log, `spec\corpus_v0.3_changes.md`).

## Unlogged pipeline check after the expansion

`tools\null_smoke.py` ran once more on 2026-10-06T20:17Z on the research split only (42 cases, 13 episodes), unlogged, nulls only, no engine; the holdout was not loaded. Results are in `spec\scoring.md` section 7 (best-null re-check).

Disclosure after re-seal version 3: that run covered the v2 research split, which included episodes that version 3 now holds out (EP02, EP10, EP17, EP19). The nulls (not the engine) have therefore been run on part of the v3 holdout, and the best-null choice in `spec\scoring.md` section 7 was made with those episodes in view. The owner should decide whether that choice is re-made on the v3 research split before registration.

Disclosure after re-seal version 5: EP03-1988-89-DEM, held out from version 5, was part of the v2 research split covered by the 2026-10-06T20:17Z null run. EP15 was held out in version 2 and was not in that run; EP23 is new.
