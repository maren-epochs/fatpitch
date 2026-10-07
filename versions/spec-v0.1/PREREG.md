# Fat Pitch — Pre-registration record

## Pending — not registered (awaiting owner review)

Owner decision 2026-10-06: nothing is registered with `fatpitch.prereg` until the owner has reviewed the rules. `prereg\preregistrations.csv` and `prereg\run_log.csv` do not exist yet. No engine scoring run and no logged run has taken place.

Would-be registration set (`fatpitch.prereg.PREREG_SET`, six files since 2026-10-06: `cases/HOLDOUT.yaml` added), sha256 of the file bytes, computed 2026-10-06T20:23:54Z after the corpus expansion and holdout re-seal (SNAPSHOT; superseded by any later edit):

| Would-be id | File | sha256 |
|---|---|---|
| PR-0001 | `spec/process.md` | `27fa06b56734dd33f89098386e92c124aafdaa98bf0d42c80e3238348bdf0408` |
| PR-0002 | `spec/registry.yaml` | `c1600c4aace9ba51b8bf367a58d9e093011aad3ec24d8fd2ff925b51d63698d4` |
| PR-0003 | `spec/transition_table.yaml` | `2e320815a183da3751f65f63eaa15e38abdf981bc61f4a7caff8dae1fa43282e` |
| PR-0004 | `spec/corpus_manifest.txt` | `1051a54bd38ac4a91d247c69464ecafb056d2b93b683c391dcaa6c8b2e893ba6` |
| PR-0005 | `spec/scoring.md` | `bfb7d8e7a7c8c424664909a39e743e5c37974f3992d10b2f235be30174774f09` |
| PR-0006 | `cases/HOLDOUT.yaml` (sealed research/holdout split, version 2, `spec/HOLDOUT.md`) | `49e48edb139e65a675f9e9617cd578117e5831cfcfb0e9df5081d9331dfda2b8` |

| Derived value | Value |
|---|---|
| Case corpus sha256, all case files (`fatpitch.cases.holdout.full_digest`; sorted `relative_path NUL file_sha256 LF` lines over `cases\*.yaml`) | `f22261e8d9727ca2ffde328b8a7954710e1a27d18135a00e7308c4460ac1dc73` (68 cases, 20 episodes; 17 turning points, derived, not stored). Before the expansion: `8ff13ad73aceed22cfcb86180946c485d6c35547153966bd5f0b342eb3f87bae` (56 cases, 19 episodes) |
| Holdout split (`cases/HOLDOUT.yaml` version 2) | 7 of 20 episodes, 26 of 68 cases; holdout files sha256 `9d33be6b3a853f7d6b54df94c5aa2c3e1d6634329cc76af0316f0a26e5f54c1b`; research files sha256 at sealing `113024a092cda35461186507b7713886db4040262900ae3e63732845ebf504af`. Version 1 (superseded, kept under `previous`): 6 of 19 episodes, holdout files `867913efb0ba0fb67a59051b5563fc809adbdf2fc7f8fa72480b7c6eab061807`, file `902bf4aae713d566d2b1a0f8cbdc46a40badbfe7a3078f2f57f0b3eb3f9a896a` |
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

## Unlogged pipeline check after the expansion

`tools\null_smoke.py` ran once more on 2026-10-06T20:17Z on the research split only (42 cases, 13 episodes), unlogged, nulls only, no engine; the holdout was not loaded. Results are in `spec\scoring.md` section 7 (best-null re-check).
