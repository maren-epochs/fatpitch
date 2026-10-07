# Spec changelog

Versions are created for important changes only (owner, 2026-10-06). Each version = git tag `spec-vX.Y` + snapshot folder `versions\spec-vX.Y\` (spec files, registry, thesis table, scoring, holdout seal). Minor edits ride along until the next version.

## spec-v0.3 — 2026-10-07

- Gate 1 set includes era-B (pre-2002) research regime cases (owner option C): 28 cases / 10 episodes (25 easing, 3 tightening); LOEO climatology over the combined set.
- Hard tightening requirement (owner decision): on research tightening cases the engine's mean RPS must beat always-easing's (0.856 for the reference). Tightening subset = 3 cases in 2 episodes (EP01 1981, EP18 2022).
- Reported: Gate 1 by era, class-balanced RPS, tightening-subset scores, per-episode table. Turn matching excludes change intervals > 36 months.
- Decided before any engine emitted probabilities.

## spec-v0.2 — 2026-10-07

- Corpus v0.2: blind label audit (2015-03-02 neutral → easing; notes corrected on six cases); research decisions C33 (thesis dropped; regime-only), C15 (label removed), C44 (→ easing), C14 and C56 (→ easing); C09 re-dated 1999-02-26; Sohn 2016 and Goldman Jan 2021 citations upgraded (Goldman case re-dated 2021-02-05, easing); new cases WSJ 2014-06-19, IE 2023-05-01, Grant's 2024-10-02, Bloomberg 2018-12-18 Treasury long. 72 cases / 20 episodes; holdout v4 (24 cases / 7 episodes), never opened.
- Gate 1 replaced (owner decision B): engine emits daily regime probabilities; ranked probability score skill > 0 and exact episode sign-flip p < 0.10 against each of LOEO climatology, 12-month trend and always-easing (binding = max p). Holdout scored once at E7 with a Bayes factor. Gate 2 (thesis recall) unchanged as hard go/no-go. Earlier agreement-margin, paired, turning-point and timing gates retired (insufficient power: era-A reads ~93% easing, ~6 true turns).
- Decision schema 2 (regime probabilities). Diagnostics: bracketed daily agreement, regime-change turn matching, kappa/balanced accuracy, AUC.
- Version runner (`fatpitch.versions`), trial log, leaderboard.
- Registry unchanged from v0.1 (111 parameters, 8 tunable).

## spec-v0.1 — 2026-10-06 (baseline)

- Process spec E1: 65 rules (50 stated / 11 interpreted / 4 article-origin at weight 0), seven-step thesis-first model.
- Registry: 111 parameters, 8 tunable. Owner decisions D1–D17 and G1 applied, including D1 `liq.m2_ip.spread_pp` = 3.5 [1, 7]; D3 `xasset.window_m` = 6 [3, 12] with magnitude-floor variant; D5 monthly ROC change 6; D7 classic Zweig breadth thrust (NYSE A/D 1965–2020, S&P 500 members 2021+, industry fallback in the gap); D11 neutral size 0.75; D17 cut-pricing range [25, 50]; G1 COT crowding 90th percentile.
- Transition table: 25 rows, authored before case reading (frozen).
- Scoring: paired sign-flip Gate 1 on era-A turning points (best null `null_trend_12m`, p < 0.10, floor 0.80); Gate 2 same form on thesis recall (floor 0.50).
- Corpus: 68 cases / 20 episodes; holdout v2 sealed (26 cases / 7 episodes), never opened.
- Status: research mode; not pre-registered.
