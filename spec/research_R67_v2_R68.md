# R-67 v2 (anticipated policy turn, redesign) and R-68 (inflation relative to what policymakers think)

Research date 2026-10-07. Design only: no engine run, no `fatpitch.versions` run, no anticipation CLI run, no statistic computed. Only this file was written.

Read: `CLAUDE.md`; `spec\process.md` §0, R-05, R-06, R-10, R-14, R-15, R-17, R-23, R-58, R-66, R-67, §9; `spec\scoring.md` §6c–§6e; `spec\research_market_implied_fed.md`; `spec\research_inflation_measures.md`; `spec\decisions.yaml` (TRACK-01, R67-01..04, R14-04, SCORE-01, INFL-01..03, R68-01, LAB-01); `spec\registry.yaml` (antic.*, curve.cut_pricing_bp, fci.*, internals.*, policy.taylor_pi_target_pct); `src\fatpitch\rules\anticipation.py`; `src\fatpitch\cases\anticipation.py` (docstring, constants, reference signals); `src\fatpitch\rules\step1.py` (R-10, R-58), `step1b.py` (R-15, R-17); library notes DS/2021-01-XX (GS), RS/2022-09-28.

Blindness. Not opened: `spec\fed_cycles.yaml`, `cases\`, `results\`. The first R-67 test is known only from the owner's summary: tightening hit 0.61 vs `naive_2y_ff` 0.78; easing hit 0.17 vs 0.61; named misses 2001-01, 2007-09, 2019-08 (cuts); at 2007-08 the bill forward read "hike" and the inflation guard did not fire (core neutral). No per-turn detail beyond this was sought. The diagnosis below reasons from the rule's construction, bill arithmetic and public history, not from turn-by-turn outcomes. Statements about specific past episodes are recollections of the public record, marked as such, and are not measurements.

Conventions as in the two research files (P / NP / S reliability; Y / N verbatim). "Fixed" = `tunable: false`. The tunable cap (8/8) is full; nothing below adds a tunable.

---

## 1. Diagnosis: why D3 failed §6e

### 1a. Mechanisms

| # | Mechanism | Source in the D3 construction | Direction / era affected | Basis |
|---|---|---|---|---|
| D-1 | Horizon mismatch. M measures only the 3m→6m bill segment (the move priced for the next quarter). Markets price an easing *cycle* (several cuts) once a downturn is seen; the cumulative path appears in 1–2-year yields months before the next-quarter segment moves a full step | `antic.horizon_m` = [3, 6]; band one step (25 bp) on a one-quarter segment | Easing (strongly), tightening (less: hiking cycles are gradual and the next-quarter step is priced early) | GSS (2007): bills weakest of the market measures; beyond 6 months other instruments carry the information. Construction |
| D-2 | Bill-specific distortion in stress. Flight to quality and safe-haven demand concentrate in the shortest bills; DTB3 falls more than DTB6, so the forward rises and reads "hike" exactly when stress precedes a cut. Debt-ceiling and supply events distort single maturities | M uses two bills only | Easing turns preceded by financial stress (the common case) | Research file §5c (D1 failure modes); owner-reported 2007-08 reading |
| D-3 | Guard on the wrong variable. The flight-to-quality guard fires only when inflation momentum is easing. Inflation lags activity; at the onset of stress it is flat or rising (oil). Core CPI (used from 1996-12) is smooth and rarely crosses ±0.5 pp in a few months | D3 guard: M tightening with I easing → neutral | Easing turns after 1996 | Owner-reported 2007-08 (core neutral). General regularity: inflation peaks after the cycle peak (not verified here) |
| D-4 | Inflation leg is tightening-sided. I easing needs `π6 − π12 < −0.5`, which usually arrives after the first cut; when M is neutral, the I fallback can read *tightening* before an easing turn (supply-shock headline) | I fallback when M neutral or unknown | Easing | Construction; R-10 record (oil up before 2000 and 2007-08 cuts, public history) |
| D-5 | Smoothing lag at abrupt turns. The 20-day mean at the month end before the first move averages pre-repricing days. Inter-meeting moves have mostly been cuts (recollection: 1998-10, 2001-01, 2001-04, 2001-09, 2008-01, 2008-10, 2020-03), i.e. easing turns reprice faster than tightening turns | `antic.smooth_d` = 20 | Easing | Construction; public history (recollection) |
| D-6 | Discount-basis arithmetic. `2 × (DTB6 − DTB3)` on discount yields is not the forward rate. With equal discount yields the true 3m→6m forward exceeds the 3m spot rate by 1.0 / 4.2 / 9.5 / 17.2 / 27.3 / 64.0 bp at 2 / 4 / 6 / 8 / 10 / 15% (computed from bill prices, 91/182 days). The research file's "largely cancel" is incorrect | `market_part` uses discount yields | Biases M toward **easing** at high rate levels; costs tightening hits in 1970s–1980s; does not explain easing misses | Arithmetic (this file) |
| D-7 | Measure breaks in I. Headline NSA before 1972-07, headline SA 1972-07 to 1996-12, core SA after; NSA 6-month changes carry a seasonal swing (−1.08 to +0.61 pp) larger than the 0.5 pp band | `CPI_IDS` chain | All eras, unevenly | `research_inflation_measures.md` I-1, I-2 |
| D-8 | Neutral-producing branches. Band, guard and 2-month hold all output neutral; a neutral reading at the last eligible month end is a miss. `naive_2y_ff` has no smoothing, no guard, no hold | D3 combination | Both directions | Construction of §6e (hit = reading at `W_end`) |

### 1b. Why `naive_2y_ff` did better

| Property of `DGS2 − FF` (±50 bp) | Effect in §6e |
|---|---|
| Prices the cumulative 0–24-month path (D-1) | Large negative gap well before an easing cycle; reading held through the window |
| In flight to quality the 2-year falls (safe-haven demand lowers it) | Stress pushes it toward "easing", the correct direction before stress-driven cuts (opposite of D-2) |
| Positive term premium (large in the 1980s; Kim–Wright, ACM) | Biases toward "hike": helps tightening hits, raises false alarms |
| No smoothing, no guard, no hold (D-5, D-8) | Fewer neutral readings at `W_end` |
| The measure he reads for what is priced (R-23 anchors: DS/2023-04-24 NP; DS/2019-06-07 NP) | Library support exceeds that of the bill forward (none) |

Conclusion. The easing failure is structural: one-quarter horizon, bill-specific stress distortion, a guard keyed to a lagging variable, and an inflation leg that cannot point to easing in time. Changing D3's constants would not fix it; the market leg and the easing-side evidence must change. The tightening shortfall is partly D-6 (easing bias at high rates) and partly D-1.

---

## 2. Changes common to every v2 candidate

| Id | Change | Formula / rule | Constants | Class |
|---|---|---|---|---|
| C1 | Bill forward from prices | `P_k = 1 − d_k·t_k/360` (t3 = 91, t6 = 182 days); `f = (P3/P6 − 1)·360/91`; `r3 = (1/P3 − 1)·360/91`; `MB_bp = (f − r3)·10⁴`, 20-day mean, ±`antic.band_bp` | Day counts are the bill conventions, not parameters | Design change (formula); removes D-6 |
| C2 | Four-measure inflation leg `I4` (owner decision INFL-01) | Section 2a | None new | Design change |
| C3 | 2-year path leg `M2` | `M2_bp = (DGS2 − FF)·100` (`DGS1 − FF` before 1976-06), reading at asof close, no smoothing; ±`antic.path_band_bp` | New fixed id `antic.path_band_bp` = 50 (copy of the registered `curve.cut_pricing_bp` value and of the §6e naive band). Decoupled from the tunable `curve.cut_pricing_bp` so later calibration of R-23 on cases cannot move R-67 | Design change |
| C4 | Era-gated absence | A component whose input series does not exist in an era (no data before its start) is *absent*: the rule is computed from the remaining components. A component whose data exist but are missing or stale at asof is *unknown*, with the D3 rule (output unknown only when the result depends on it) | None | Protects the test: §6e excludes unknown turns from denominators, so a design that is unknown more often could raise its hit rate without anticipating better. Report evaluable-turn counts v1 vs v2; a v2 pass with fewer evaluable turns than v1 is flagged |
| C5 | ZLB rule, 2-month hold, `π6 > policy.taylor_pi_target_pct` on tightening | Unchanged from D3 | Reused | — |

### 2a. Four-measure inflation leg (CPI headline, CPI core, PCE headline, PCE core)

Per measure j: `π6_j` (6-month annualised), `π12_j` (12-month), `I_j = π6_j − π12_j` on the as-of vintage. Class: tightening if `I_j > 0.5` and `π6_j > 2.0`; easing if `I_j < −0.5`; else neutral (D3 rule, constants reused). NSA measures use a seasonally neutral form: `I_j^NSA = (ann6_j(t) − ann6_j(t−12)) / 2`, comparing the same six calendar months a year apart; same scale as `π6 − π12` (≈ half the change in the 6-month rate), but a 12-month rather than 6-month comparison lag. Formula change, no constant.

PIT availability (owner-supplied status; starts marked *verify* are not confirmed in this session):

| Measure | Series | Primary PIT form | Usable from (asof) | Before |
|---|---|---|---|---|
| CPI headline | `CPIAUCSL` | ALFRED SA vintage | 1972-07-21 | `CPIAUCNS` (unrevised NSA, seasonally neutral form) |
| CPI core | `CPILFESL` | ALFRED SA vintage | 1996-12-12 | `CPILFENS` (NSA, being acquired; seasonally neutral form) from its first real-time publication. Whether BLS published the ex-food-and-energy aggregate in real time before the 1970s is a gap; before verified publication: absent |
| PCE headline | `PCEPI` | ALFRED vintage | ALFRED start *(verify; being acquired)* | absent |
| PCE core | `PCEPILFE` | ALFRED vintage | ALFRED start *(verify; being acquired)* | absent |

Release timing differs: CPI for month m−1 is published mid-month m; PCE for m−1 near the end of month m (sometimes after month end). Each measure uses its own latest as-of observation; no alignment to a common reference month (alignment would discard the newer CPI print).

Combination options:

| Option | Rule | Behaviour | Assessment |
|---|---|---|---|
| **K1 strict majority (recommended)** | `I4` = class held by more than half of the known measures; minimum 2 known, else `I4` unknown | 4 known: 3 must agree. 2 known (CPI only, pre-PCE vintages): both must agree. An energy shock moves the two headline measures only → 2 of 4 → neutral | A supply shock in headline alone does not produce a reading; a broad move (core and headline, CPI and PCE) does. Discrete, no new constant. Coverage-consistent: the bar rises with the number of measures |
| K2 median | Median of known `I_j` and of known `π6_j`, then the D3 class rule | 4 known: mean of the middle two; 2 known: mean of both | Continuous, but with 4 measures the median mixes one headline and one core reading, so energy shocks still pass at half weight |
| K3 unanimity | All known measures agree | Rarely non-neutral with 4 measures | Too strict: the guard and the tightening fallback would almost never act |
| K4 any two agree, none opposed | ≥ 2 in one class, 0 in the other | Headline pair alone suffices | Admits supply shocks; the problem D-4 describes |

Minimum known = 2 (argued: one index alone cannot separate a broad move from a component shock; 2 is the smallest set with a cross-check). Unknown handling: a measure without a usable vintage at asof is excluded from the count, not counted as neutral; `I4` with fewer than 2 known measures is unknown (or absent where C4 applies: before 1972-07 only NSA CPI measures exist).

CPI–PCE bias (owner: 2% target stays on CPI, report the bias). The `π6 > 2.0` condition is applied to all four measures. For CPI measures it fires more readily (CPI exceeded PCE by 0.45 pp headline and 0.47 pp core on average, 1960–2026, latest vintages). Reported per run, not gated: (i) mean CPI−PCE wedge on `π6` and `π12` over evaluated month ends; (ii) count of month ends where the CPI measures pass `π6 > 2.0` and the PCE measures do not; (iii) count of month ends where `I4` would change class if the CPI measures used a PCE-consistent condition. Under K1 with 4 known, the wedge alone can move at most 2 votes, so it cannot create a majority by itself.

### 2b. Growth / financial-stress leg `Gr` (easing side only)

Built only from existing rules and their registered constants. No new constant.

`Gr = on` at month end m if **R-10 flag** (rates, oil and USD all up over `xasset.window_m`) **or** (**R-15 direction = down**, confirmed turn, **and** every known R-17 credit spread — `BAA − GS10` and, from 1996-12, `BAMLH0A0HYM2` — wider than `internals.curve_credit_trend_m` months earlier). Suppressed when the R-08 condition holds (CPI yoy > `infl.persist_pct` and FF < CPI).

| Element | Library basis | Why included / constraint |
|---|---|---|
| R-10 | `stated`. 2000 is the origin case: oil, rates and USD up while he moved 300% of the fund into 2-year notes ahead of the 2001 cuts (DS/2009-XX-XX Feig, NP; RS/2018-09-06; RS/2024-11-06 NP "three death knells") | The only library episode in which a stated rule preceded an anticipated easing trade |
| R-15 down | `stated` (internals lead the economy 6–12 months, DS/2022-06-XX NP). DS/2018-12-16 (S): banks, housing, transports, industrials down double digits → argued against further tightening; DS/2019-06-03 (S): retail −24%, Russell 2000 −15% | Internals deterioration as a cause for the Fed to stop or cut |
| R-17 credit widening | `stated` principle; process.md R-17: "Retained as evidence, never a trigger alone" | Hence only in conjunction with R-15 |
| R-08 suppression | `stated` (DS/2022-06-XX NP Y: above 5%, inflation has not come down without FF above CPI) | A growth scare does not produce an easing reading while the Fed is bound by R-08 (2022 type). 2000 is not suppressed (CPI below 5%, FF above CPI) |
| R-58 (NFCI) excluded | NFCI rows before first publication (2011-05-25) are unusable (step1.r58_fci) | Would cover only 2011→; reported as a variant, not part of `Gr` |

Era coverage of `Gr` as implemented today: R-10 code reads `DCOILWTICO` (1986→) and `USD_BROAD`; the process.md fallback `WTISPLC` (monthly 1946→) is not implemented (spec–code gap; implementing it cites R-10's inputs line, so it is mechanical). R-15 reads sector ETFs only ("French-49 not in the lake"), so it is absent before about 2000–2006. Hence `Gr` is absent before 1986 (before 1973 even with the WTISPLC fallback, because of the USD series), R-10-only 1986→~2000, full from ~2000.

---

## 3. R-67 v2 candidates

Notation. `M2`, `MB`, `I4`, `Gr` as above; "held" = same class at 2 consecutive month ends (`I_HOLD_MONTH_ENDS`); ZLB rule on all easing readings. Output fields as D3 plus `component` ∈ {M2, MB, I4, Gr, R68, guard}.

### V2-A Market first, inflation as guard and tightening fill (minimal)

1. `M2` non-neutral → `M2` (no guard; preserves the naive reading).
2. Else `MB` non-neutral → `MB`, except `MB` tightening with `I4` easing → neutral.
3. Else `I4` tightening held → tightening; else neutral. Inflation never produces easing.

### V2-B Market first, inflation fills tightening, growth/stress fills easing (recommended)

1. `M2` non-neutral → `M2`, except `M2` tightening with `I4` easing → neutral (D3 guard, now on a broad inflation reading; aimed at 1980s term-premium hike readings).
2. Else `MB` non-neutral → `MB`, except `MB` tightening with (`I4` easing or `Gr` on) → neutral (flight-to-quality guard keyed to stress, the cause of D-2).
3. Else fallback: `T` = `I4` tightening held; `E` = `Gr` on held. `T` only → tightening; `E` only → easing; both or neither → neutral.

### V2-C V2-B with R-68 as the inflation input from 2007-11

As V2-B; from the first SEP publication (2007-11) the inflation input in steps 1–3 is R-68's symmetric class (section 4, hybrid form) instead of `I4`, and `E` = `Gr` on held **or** R-68 easing held. Before 2007-11, identical to V2-B.

### V2-D Bill-primary (keeps the R67-01 market choice)

V2-B without `M2`: step 1 is `MB` (C1 price-correct) with the step-2 guard; step 3 unchanged.

### 3a. Constants

| Constant | Value | Status | Argument |
|---|---|---|---|
| `antic.path_band_bp` | 50 | New, fixed | Two standard moves on a 0–24-month path; identical to the registered R-23 value and the §6e naive band, so the comparison isolates the added legs |
| `antic.band_bp`, `antic.horizon_m`, `antic.smooth_d`, `antic.zlb_ff_pct` | 25, [3, 6], 20, 0.25 | Reused, fixed | Research file §5b; unchanged |
| `antic.infl_short_m`, `antic.infl_long_m`, `antic.infl_band_pp` | 6, 12, 0.5 | Reused, fixed | Unchanged; now per measure |
| `policy.taylor_pi_target_pct` | 2.0 | Reused | INFL-02: stays on CPI; bias reported |
| `I4` minimum known / majority | 2 / > half | Definition | Section 2a |
| Hold | 2 month ends | Definition (D3) | Unchanged |
| `xasset.window_m`, `internals.rs_lookback_m`, `internals.turn_confirm_m`, `internals.curve_credit_trend_m`, `infl.persist_pct` | 6, 6, 2, 3, 5.0 | Reused at registered values | The first two are tunables; the retest freezes them at their registered values. Any later calibration on cases changes R-67 and requires a new §6e run, reported as a new trial |

### 3b. Expected behaviour per era (by construction; qualitative, not computed)

| Era | V2-A | V2-B | V2-C | V2-D |
|---|---|---|---|---|
| 1959–1981 (month precision; windows often one month) | ≈ naive (DGS1 − FF before 1976); FF volatility 1979–82 adds noise | ≈ V2-A; `Gr` absent; `I4` = 2 NSA CPI measures | = V2-B | C1 removes the 27–64 bp easing bias at 10–15% rates: more tightening readings than D3 |
| 1982–1993 | Term premium → long hike runs: tightening hits, false alarms | Guard trims hike readings when `I4` easing (core and headline decelerating together); `Gr` R-10 only from 1986 | = V2-B | Bill forward less exposed to term premium; easing still weak (D-1) |
| 1994–2008 | ≈ naive, plus `MB`/`I4` fills | Adds easing lead where `M2` is still inside ±50 and R-10 or R-15+credit fire (2000 type) | = V2-B | Stress guard cancels 2007-08-type false hikes; easing hits depend on `Gr` |
| 2009→ | ZLB: easing neutral; `M2` reads hikes ahead of liftoffs | As V2-A plus `Gr` easing in growth scares above the ZLB | R-68 leads 2021-type tightening by many months (false-alarm months); undershoot periods read easing above the ZLB | As V2-B without `M2` |

### 3c. Failure modes

| Design | Failure mode | Consequence for §6e |
|---|---|---|
| All | `M2` reduces R-67 toward the naive benchmark | Criterion 2 then tests the added legs, not an independent market signal; the per-hit component attribution must be reported |
| V2-A | Hit rate ≥ naive at `W_end` by construction (naive reading kept when non-neutral) but extra hits may carry short leads; non-neutral set is a superset of naive's | Median lead not guaranteed ≥ naive; false alarms ≥ naive's; criterion 2c (≤ naive + 1.0/yr) is the binding risk |
| V2-B | Guard on `M2` can neutralise a correct naive tightening reading when inflation is decelerating broadly before a hike | Tightening hit may fall below 0.78 |
| V2-B | `Gr` fires in growth scares the Fed sits through (mid-cycle slowdowns; credit events during hiking cycles when `M2` is neutral) | Easing false-alarm months |
| V2-B | R-10 fires late in hiking cycles (rates rising with the Fed); held 2 months it can precede a cut by more than 6 months | False-alarm months before correct easing hits (counted, since the 6-month horizon rule applies) |
| V2-C | R-68 adds ≈ 5 evaluable turns (2015, 2019, 2022, 2024, 2026); its own contribution cannot be tested; his 2021 context expects the Fed *not* to respond to the gap | Long early runs (false alarms) with no measurable benefit at n ≈ 5 |
| V2-D | D-1 remains (one-quarter horizon) | Easing hit rate likely still below naive's |
| All | Tunables (`xasset.window_m`, `internals.rs_lookback_m`) shared with case-scored rules | Coupling between Gate 1/2 calibration and §6e; handled by freezing (3a) |

### 3d. Assessment

V2-B addresses each diagnosed mechanism with existing, cited rules: D-1 and D-5 by the unsmoothed 2-year path, D-2 and D-3 by a stress-keyed guard, D-4 by giving the easing side its own evidence (stated R-10, R-15) and restricting inflation to the tightening side, D-6 by C1, D-7 by C2. V2-A is the smallest change but adds nothing on the easing side beyond the naive reading. V2-C mixes two changes in one test and adds a component that cannot be evaluated at n ≈ 5. V2-D honours the R67-01 bill choice and is the control for "fixes without the 2-year".

Frank note on the 2-year leg. The owner did not choose R67-04 option C (adopt the 2-year rule). V2-A/B/C use the 2-year spread as the primary market leg, which is close to that option with extra legs. The argument for it is construction (D-1, D-2) and library anchoring (R-23), not the first test's result; the result agrees with the argument, which is why the retest is exploratory (section 5).

---

## 4. R-68 "Inflation relative to what policymakers think"

Statement: "my overriding theme is inflation relative to what policymakers think." (DS/2021-01-XX, NP, Y). Context in the same note (Y): "Because the Fed could drive me crazy and not allow the market to drive rate rises to come to fruition, I also have a large position in commodities. The longer the Fed tries to keep rates suppressed…, the more I win on my commodities." The theme is a gap between realised inflation and the Fed's view; his expression assumed the Fed would lag, i.e. the gap identifies a policy error (too loose), not an imminent Fed move.

### 4a. Inputs and PIT

| Input | Series | Timing | Notes |
|---|---|---|---|
| Fed projection | FOMC SEP median core PCE inflation, Q4/Q4, for the calendar year containing asof (current-year column; in January–March before the first SEP of the year, the latest SEP's next-year column) | `published_at` = Board release timestamp of the SEP. 2007-11 to about 2011 the projections were released with the minutes (about 3 weeks after the meeting); from 2011-04 central tendencies at the press conference; full SEP on the meeting day later *(verify each)*. Where the release time is not established, the minutes release date (never earlier than the true release) | Medians believed published from 2015-09 *(verify)*; 2007-11 to 2015-06 the central-tendency midpoint is the stand-in, labelled `variant: central_tendency` |
| Realised inflation | Core PCE `PCEPILFE`, ALFRED as-of vintage, `π6` (6-month annualised) | Personal Income and Outlays release, about 4 weeks after month end | Same measure as the projection: no CPI–PCE wedge inside R-68 |

Mechanical PIT guard: latest SEP older than 200 days → unknown (projections are quarterly; 200 days flags a missing release, not a design choice).

### 4b. Gap definitions

| Option | Formula | Assessment |
|---|---|---|
| **G1 (recommended)** | `G = π6(core PCE) − P_y` | Same units (annual rates); uses the stated 6-month horizon (DS/2024-05-07, NP, N); no new construction |
| G2 required pace | `G = π6 − r_req`, `r_req` = annualised pace needed over the rest of year y to reach `P_y` given realised Q4(y−1)→latest | Closer to "what the projection implies now", but unstable late in the year (few remaining months) |
| G3 projection revision | Sign of `P_y` change between consecutive SEPs | Measures the Fed changing its mind, not the gap; echoes guidance (his criticism, DS/2015-11-04, DS/2024-05-07) |

Class (G1): `G > +0.5` held 2 month ends → **behind the curve** (inflation above the Fed's own view: policy too loose; tightening pressure); `G < −0.5` held → **ahead** (inflation below the Fed's view: easing pressure); else neutral. Before 2007-11: absent (owner brief: unknown before; under C4 it is absent because no SEP exists, so it does not make the host rule unknown).

### 4c. Constants (all fixed; no tunable)

| Id | Value | Argument |
|---|---|---|
| `r68.short_m` | 6 | The 6-month annualised read he cites (DS/2024-05-07, NP, N); equal to `antic.infl_short_m` |
| `r68.band_pp` | 0.5 | Same scale and argument as `antic.infl_band_pp` (two typical monthly surprises over six months); also wider than the typical SEP central-tendency span for core PCE in the current year (about 0.2–0.4 pp, *verify*), so a gap inside ±0.5 is within the Committee's own dispersion |
| `r68.hold_month_ends` | 2 | As the D3 hold; one print can be revised (core PCE 6-month revision size to be measured on the acquired vintages, no labels) |
| `r68.sep_max_age_d` | 200 | Mechanical PIT guard (4a) |

### 4d. Placement options

| Option | Mechanism | Track | Effect on registered results | Assessment |
|---|---|---|---|---|
| **P1 (recommended): policy-error family, one-sided, faithful; anticipation variant hybrid, report-only** | R-68 joins the R-06 evidence family (R-05, R-38 "policy error"). Family sign: R-06 if non-neutral and R-68 not opposite; R-68 `too_loose` if R-06 neutral or unknown; R-06 and R-68 opposite → neutral. Only `G > +0.5` counts (`too_loose`); `G < −0.5` → neutral in the faithful track. R-68's symmetric class is computed and reported beside R-67 (the V2-C input) without entering §6e gating | Faithful (policy error); hybrid (anticipation) | Changes step-5 tiering and R-05 triggers from 2007-11 → Gate 2 era A changes → re-registration and new report. Gate 1 and §6d unaffected | One-sidedness follows his statements: inflation above the Fed's view is the stated theme (2021-01) and the 2021–22 behind-the-curve reads (RS/2022-09-28); inflation *below* target is not a reason to ease in his view ("The 2% inflation target has sort of become a religion", DS/2017-12-12, NP, Y). A symmetric version would read 2012–2019 undershoots as `too_tight` and cancel R-06's `too_loose` evidence in years he called the Fed too loose (DS/2015-04-15, DS/2017-12-12). Same family, not a new one: R-06 and R-68 both measure inflation against a benchmark; separate families would double-count (R-38 unit weights) |
| P2 hybrid only, R-67 input (V2-C) | As V2-C; nothing in the faithful track | Hybrid | §6e only | Uses the statement for the purpose his context argues against (forecasting a Fed move) and leaves the faithful track without the rule built from his stated theme |
| P3 faithful, symmetric | As P1 with `too_tight` when `G < −0.5` | Faithful | As P1, larger | Conflicts with DS/2017-12-12 and DS/2019-06-07 (2% target criticised) |
| P4 R-66 voter or veto | R-68 direction as a third family; or a veto | — | Gate 1 / step 4 | Rejected. Voter: stance gap, not policy direction (the R-66 exclusion argument for R-06 applies); untested. Veto: no statement makes it a veto; vetoes in the spec are stated rules |

Track argument. The faithful track already holds `interpreted` constructions of stated principles (R-06 is `interpreted` and faithful). R-68's principle is a verbatim NP statement, more direct than R-06's support. The anticipation use stays hybrid under R67-02, and the statement's own context (the Fed would "not allow" rates to rise) argues that the gap predicts Fed inaction in the near term rather than a move. Tag: `stated` (principle) / formula `interpreted`, as R-17 and R-58.

### 4e. Expected behaviour (public-history recollection, not measured)

| Period | Expected G sign | Faithful P1 effect | Comment |
|---|---|---|---|
| 2009–2014 | Mostly ≤ 0 (projections repeatedly above outcomes) | Neutral (one-sided); R-06 alone | No conflict with his too-loose reads |
| 2015–2019 | ≤ 0 (undershoot) | Neutral | As above |
| 2021–2022 | Strongly > 0 from about spring 2021 | `too_loose` from mid-2021; agrees with R-06 where R-06 fires; fills where R-06 is inside its 2 pp band | The stated theme |
| 2023 H2–2024 | Near 0 or < 0 | Neutral | Hybrid variant would read easing pressure months before the 2024-09 cut (early) |

Failure modes: SEP medians vs central-tendency midpoint differ by construction (variant break around 2015-09, *verify*); core PCE first-release revisions on a 6-month window (size unknown until vintages are acquired); n of evaluable Fed turns 2007-11→ is about 5, so no anticipation statistic for R-68 alone is meaningful.

---

## 5. Retest protocol

In-sample statement. The retest scores the same Fed history (1970→, the §6d key) on which D3 failed. The v2 designs were written after the aggregate result and four named misses were known; the diagnosis agrees with that result. Any pass is therefore exploratory, not confirmatory.

| Step | Rule |
|---|---|
| 1 Choose one design before computing | The owner selects one R-67 v2 candidate and the R-68 placement from section 6. Other candidates are not run before the report (running several and keeping the best is selection on the test) |
| 2 Data before signals | `CPILFENS`, `PCEPI`/`PCEPILFE` ALFRED vintages and SEP projections acquired and catalogued; vintage start dates recorded in `spec\data_coverage.md` from the data alone. If PCE vintages start late, the number of known `I4` measures per era is stated before the run |
| 3 Write and register | process.md R-67 revision and new R-68; registry fixed entries (`antic.path_band_bp`, `r68.*`); decisions entry with `expected_result` (predictions below) written before the run; `fatpitch.prereg` registration (process.md, transition table, corpus hash) |
| 4 Mechanical tests | Fixtures: C1 bill-price forward (values in D-6), NSA seasonally neutral form, `I4` majority with 2/3/4 known, C4 absent vs unknown, `Gr` suppression under R-08, R-68 year-column switch and SEP staleness |
| 5 One run | Anticipation CLI once, trial appended to `trials.jsonl`; §6e constants and pass rule unchanged |
| 6 Report | Label "exploratory, in-sample, R-67 trial 2 of the family; global trial count N". Show v1 and v2 side by side with all references; per-stratum hit, lead, false alarms; evaluable-turn counts v1 vs v2 (C4 check); component that voted at each hit; exact binomial 90% intervals on hit rates (n ≈ 18 per direction, interval width about ±0.2); CPI–PCE bias block (2a); R-68 hybrid variant beside it (report-only) |
| 7 Stopping rule | No third design on this test. If v2 fails, R-67 stays a warning flag (R67-03). If v2 passes, it does not become an R-66 voter (role C) until a confirmation evaluation also passes |

Confirmation evaluations (no holdout involved; the Fed key is public facts, the case holdout is untouched):

| Option | Content | Independence | Size / cost |
|---|---|---|---|
| **F1 prospective (recommended, always on)** | Every US turn after the registration date scored when it occurs | Full | About one turn per 2–3 years |
| **F2 other central banks (recommended)** | Same v2 formula on BoE, Bank of Canada, ECB (1999→), BoJ turns with local bill or 2-year, local CPI measures and local stress inputs; answer keys built mechanically from published policy-rate histories before any signal is computed | Out-of-sample for the design (never examined) | Data are a gap: free daily local bills/2-year and inflation vintages not verified; R-15/R-10 have no foreign equivalents → `Gr` partly absent |
| F3 pre-1970 US turns | Extend the key to 1959–1969 with the §6d mechanical FEDFUNDS turning-point rule, built before scoring | Never scored by v1 | 4–6 turns; bills from 1958-12, NSA CPI only; small |
| F4 daily variant 1994→ | Lead in days before the decision date | Same turns as the gated test | Not independent; reported only |

Predictions to be written into the decisions entry before the run (for V2-B): easing hit rate rises from 0.17 to at least the naive level (0.61), driven mainly by `M2`; tightening hit rate within about one turn of naive's (0.78), lower if the `M2` guard removes correct readings; median leads at least naive's in both directions; false-alarm months per year above naive's, mainly from `Gr` and the `I4` tightening fill; the binding criteria are 2c (false alarms ≤ naive + 1.0) and 4 (no era with zero hits; 1959–1981 easing is the weakest stratum).

---

## 6. Decisions

**Q1. R-67 v2 design**
- **A (Recommended): V2-B** — addresses every diagnosed mechanism with existing stated rules; inflation confined to the tightening side.
- B: V2-A — smallest change; nothing new on the easing side beyond the naive reading.
- C: V2-D — keeps the R67-01 bill choice; easing likely still fails (one-quarter horizon).
- D: V2-C — adds R-68 to the test; untestable at about 5 turns and against his context.

**Q2. Four-measure combination**
- **A (Recommended): strict majority of known measures, minimum 2** — a headline-only supply shock cannot produce a reading.
- B: median of the known readings — continuous, but energy shocks pass at half weight.
- C: unanimity — the guard and fill would almost never act.
- D: any two agree, none opposed — admits headline-only shocks.

**Q3. R-68 placement**
- **A (Recommended): P1 — faithful policy-error family, one-sided (`too_loose` only); hybrid anticipation variant report-only** — matches the stated theme and his rejection of easing on low inflation; no double counting.
- B: P2 — hybrid R-67 input only.
- C: P3 — faithful, symmetric.
- D: P4 — R-66 voter.

**Q4. Bill forward and pre-1996 core**
- **A (Recommended): adopt C1 (forward from bill prices) and the NSA seasonally neutral form for `CPIAUCNS` and `CPILFENS`** — removes a 9–64 bp rate-level bias and the seasonal artefact with no new constant.
- B: C1 only; NSA measures absent (fewer known measures before 1996).
- C: keep the discount-basis formula; NSA form adopted.
- D: neither.

**Q5. Retest protocol**
- **A (Recommended): one pre-chosen design, single run, exploratory label with trial count, stopping rule, confirmation by F1 + F2** — limits selection on a test whose result is already known.
- B: run all four candidates once and report all — more information, but best-of-four selection on the same history.
- C: F3 (pre-1970 US turns) as the confirmation set — independent but 4–6 turns.
- D: no retest until a confirmation set exists — avoids in-sample use but delays any result.

---

## 7. Gaps

| Gap | Consequence |
|---|---|
| PCE ALFRED vintage starts; SEP median start (believed 2015-09); SEP release-time history 2007–2012 | `I4` known-measure count per era and R-68 variant boundaries unknown until acquired |
| Real-time publication of core CPI before the 1970s | `CPILFENS` may be unusable before BLS published the aggregate |
| R-15 runs on ETFs only (French-49 absent); R-10 lacks the `WTISPLC` fallback in code | `Gr` absent before 1986 and partial to ~2000 |
| Episode statements in sections 1, 3b and 4e are recollections | Not results; the test is the measurement |
| Foreign data for F2 not verified as free and point-in-time | F2 feasibility open |
| Humphrey-Hawkins / Monetary Policy Report central tendencies (1979–2007) could extend R-68 before 2007 with measure changes (CPI, deflator, PCE, core PCE) | Outside the owner's scope (unknown before 2007-10); possible later extension |

## 8. Next steps (PLAN.md)

1. PLAN D.2 / E.2: complete acquisition and cataloguing of `CPILFENS`, PCE ALFRED vintages and SEP projections (with release timestamps); record vintage starts in `spec\data_coverage.md` before any signal is computed.
2. PLAN E.2 / pre-registration: owner decisions Q1–Q5; write R-67 v2 and R-68 into `spec\process.md`, the fixed constants into `spec\registry.yaml`, predictions into `spec\decisions.yaml`; register with `fatpitch.prereg`.
3. PLAN E3: implement C1, `I4`, `Gr`, the chosen v2 combination and R-68 with the section 5 fixture tests; run §6e once through `record_run`; report as exploratory with the trial count; begin F2 answer keys only if the data check succeeds.
