"""Steps 1 and 1b orchestration: rule outputs -> regime vectors (US, EA, JP, UK) and the internals vector.

Order: timeline gate -> step-1 rules -> liquidity family (era, E.4a) -> R-14 -> R-66 probabilities (policy
direction) -> rules that take the direction as input (R-07, R-09) -> step 1b.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass, field

from fatpitch import registry as _registry
from fatpitch.decision import InternalsComponent, InternalsVector, RegimeVector
from fatpitch.rules import anticipation, step1, step1b
from fatpitch.rules.outputs import INACTIVE, MissingParam, Params, RuleOutput
from fatpitch.rules.probability import Family, liquidity_class, regime_probabilities
from fatpitch.rules.series import Snap
from fatpitch.rules.timeline import Timeline

# every series the step-1/1b rules read (INDPRO is read separately at first-release times, R-02)
ENGINE_SERIES = (
    "M2SL", "INDPRO_FR", "WALCL", "WTREGEN", "RRPONTSYD", "TREAST", "WSHOMCB", "TFD_DEBT_HELD_PUBLIC",
    "FEDFUNDS", "DFF", "DFEDTARU", "CPIAUCSL", "UNRATE_FR", "NROU", "GDP", "DGS10", "DGS2", "GS10", "TB3MS",
    "BAA", "DCOILWTICO", "USD_BROAD", "RITTER_UNPROF_IPO", "SIFMA_HY_SHARE_A", "BCNSDODNS", "NCBCEBQ027S",
    "BAMLH0A0HYM2", "FINRA_MARGIN_DEBT", "CB_ASSETS_GDP_US", "CB_ASSETS_GDP_XM", "CB_ASSETS_GDP_DE",
    "CB_ASSETS_GDP_JP", "CB_ASSETS_GDP_GB", "ECB_DFR", "DE_POLICY_RATE", "JP_POLICY_RATE", "JP_CALL_RATE_M",
    "UK_BANK_RATE", "GB_POLICY_RATE_BIS", "IRLTLT01USM156N", "IRLTLT01DEM156N", "IRLTLT01JPM156N",
    "IRLTLT01GBM156N", "NFCI", "FYFSGDA188S", "ETF_SPY", "ETF_IWM", "ETF_RSP", "ETF_XHB", "ETF_IYT", "ETF_XTN",
    "ETF_XRT", "ETF_KBE", "ETF_XME", "ETF_SMH", "US_EQ_FUT_PROXY", "SHILLER_SP", "GOLD_LBMA", "PCOPPUSDM",
    "ZWEIG_EMA10", "FOMC_BS_STATE", "DFEDTAR", "FED_DISCOUNT_RATE",
)
VETO_RULES = ("R-07", "R-08", "R-09", "R-10")


@dataclass
class RegimeResult:
    outputs: dict[str, RuleOutput]
    regime: list[RegimeVector]
    internals: InternalsVector
    notes: list[str] = field(default_factory=list)


def _f(x) -> float | None:
    if x is None:
        return None
    x = float(x)
    return x if math.isfinite(x) else None


def _gate(rule: str, w: float, fn, *args) -> RuleOutput:
    if w <= 0:
        return RuleOutput(rule, INACTIVE, reason="not held at this date (process timeline)")
    return fn(*args)


TRACKS = ("faithful", "hybrid")


def run(asof: _dt.datetime, frames: dict, reg: _registry.Registry, source=None,
        timeline: Timeline | None = None, track: str = "faithful") -> RegimeResult:
    """``track``: "faithful" (default; the process model) or "hybrid" (adds R-67 and R-68, process.md hybrid
    track: US evidence lines and an ``anticipated_turn`` note; the regime vector, probabilities and vetoes are
    unchanged)."""
    if track not in TRACKS:
        raise ValueError(f"track={track!r} not in {TRACKS}")
    tl = timeline or Timeline.all_active()
    snap = Snap(frames, asof)
    ctx = step1.Ctx(asof, snap, Params(reg), source)
    d = asof.date()
    W = {r: tl.weight(r, d) for r in ("R-02", "R-03", "R-04", "R-06", "R-07", "R-08", "R-09", "R-10", "R-11",
                                       "R-12", "R-14", "R-15", "R-16", "R-17", "R-18", "R-19", "R-56", "R-58",
                                       "R-59", "R-60", "R-63", "R-66")}
    o: dict[str, RuleOutput] = {}
    o["R-02"] = _gate("R-02", W["R-02"], step1.r02_m2_minus_ip, ctx)
    o["R-03"] = _gate("R-03", W["R-03"], step1.r03_net_liquidity, ctx)
    o["R-04"] = _gate("R-04", W["R-04"], step1.r04_purchases_minus_issuance, ctx)
    liq = step1.liquidity_family(ctx, o["R-02"], o["R-03"], o["R-04"], W)
    o["LIQ"] = liq
    o["R-14"] = _gate("R-14", W["R-14"], step1.r14_policy_direction, ctx)

    p = ctx.p
    notes: list[str] = []
    try:
        base, inc, floor = (p.num("regime.prob_base_mass"), p.num("regime.prob_family_increment"),
                            p.num("regime.prob_floor"))
    except MissingParam as e:
        base = inc = floor = None
        notes.append(f"R-66=unknown (registry parameter {e.args[0]} missing)")
    r14_cls = o["R-14"].get("direction")
    us_probs = None
    if base is not None and W["R-66"] > 0:
        fams = [Family("R-14", r14_cls, W["R-14"]),
                Family("LIQ:" + (liq.variant or "none"), liquidity_class(liq.get("sign")),
                       liq.get("weight", 1.0) if liq.ok else 1.0)]
        us_probs = regime_probabilities(fams, r14_cls, base, inc, floor)
    direction = us_probs.direction if us_probs else None

    o["R-06"] = _gate("R-06", W["R-06"], step1.r06_policy_error, ctx)
    o["R-07"] = _gate("R-07", W["R-07"], step1.r07_no_soft_landing, ctx, direction)
    o["R-08"] = _gate("R-08", W["R-08"], step1.r08_ff_below_cpi, ctx)
    o["R-09"] = _gate("R-09", W["R-09"], step1.r09_recession_prior, ctx, direction)
    o["R-10"] = _gate("R-10", W["R-10"], step1.r10_rates_oil_usd, ctx)
    o["R-11"] = _gate("R-11", W["R-11"], step1.r11_fragility, ctx)
    o["R-56"] = _gate("R-56", W["R-56"], step1.r56_ten_year_vs_ngdp, ctx)
    o["R-58"] = _gate("R-58", W["R-58"], step1.r58_fci, ctx)
    o["R-63"] = _gate("R-63", W["R-63"], step1.r63_fiscal_supply, ctx, o["R-04"])
    if W["R-12"] > 0:
        r12 = step1.r12_cross_region(ctx)
        if isinstance(r12, RuleOutput):  # missing parameter
            r12 = {k: RuleOutput("R-12", r12.status, reason=r12.reason, variant=k) for k in step1.REGIONS}
    else:
        r12 = {k: RuleOutput("R-12", INACTIVE, reason="not held at this date (process timeline)", variant=k)
               for k in step1.REGIONS}
    for k, v in r12.items():
        o[f"R-12:{k}"] = v

    # step 1b
    o["R-15"] = _gate("R-15", min(W["R-15"], W["R-16"]), step1b.r15_leading_industries, ctx)
    o["R-17"] = _gate("R-17", W["R-17"], step1b.r17_curve_credit, ctx, o["R-14"].get("qe_active"))
    o["R-18"] = _gate("R-18", W["R-18"], step1b.r18_momentum, ctx)
    o["R-19"] = _gate("R-19", W["R-19"], step1b.r19_cross_asset_trend, ctx)
    o["R-59"] = _gate("R-59", W["R-59"], step1b.r59_narrowing, ctx)
    o["R-60"] = _gate("R-60", W["R-60"], step1b.r60_breadth_thrust, ctx)

    us_rules = ["R-02", "R-03", "R-04", "LIQ", "R-14", "R-06", "R-07", "R-08", "R-09", "R-10", "R-11", "R-56",
                "R-58", "R-63", "R-12:US"]
    evidence = [o[r].summary() for r in us_rules]
    if us_probs is not None:
        evidence.append("R-66: " + ", ".join(f"{f.name}={f.cls}" for f in us_probs.families)
                        + f" -> {us_probs.direction}")
    if track == "hybrid":
        # hybrid track only (owner decision 2026-10-07): warning flag until R-67 passes scoring.md 6e
        o["R-67"] = anticipation.r67_anticipated_turn(ctx)
        evidence.append(o["R-67"].summary())
        flag = anticipation.anticipated_turn(o["R-67"], r14_cls)
        notes.append(f"anticipated_turn={'unknown' if flag is None else str(flag).lower()} "
                     f"(hybrid track; R-67 {o['R-67'].get('direction')} vs R-14 {r14_cls}; warning flag only)")
        # R-68 inflation vs the Fed's projection: hybrid track only, report-only (decision R68-02)
        o["R-68"] = anticipation.r68_inflation_vs_projection(ctx)
        evidence.append(o["R-68"].summary())
    pe = o["R-06"].get("sign")
    us = RegimeVector(
        region="US", policy_direction=direction,
        liquidity_impulse=_f(liq.get("level")), liquidity_change=_f(liq.get("change")),
        policy_error_sign=pe, veto_flags=[r for r in VETO_RULES if o[r].get("flag")],
        fragility_level=_f(o["R-11"].get("composite")),
        p_easing=us_probs.p_easing if us_probs else None, p_neutral=us_probs.p_neutral if us_probs else None,
        p_tightening=us_probs.p_tightening if us_probs else None,
        liquidity_sign=liq.get("sign"), liquidity_variant=liq.variant if liq.ok else None,
        fci_state=o["R-58"].get("fci_state"), fragility_state=o["R-11"].get("level"),
        relative_impulse=None, evidence=evidence)
    vectors = [us]
    for k in ("EA", "JP", "UK"):
        r = r12[k]
        probs = None
        if base is not None and W["R-66"] > 0:
            cls = r.get("direction")
            probs = regime_probabilities([Family("R-12", cls, W["R-12"])], cls, base, inc, floor)
        vectors.append(RegimeVector(
            region=k, policy_direction=probs.direction if probs else None,
            liquidity_impulse=_f(r.get("impulse")),
            p_easing=probs.p_easing if probs else None, p_neutral=probs.p_neutral if probs else None,
            p_tightening=probs.p_tightening if probs else None,
            relative_impulse=_f(r.get("rel_us")), evidence=[r.summary()]))

    internals = _internals(o, snap)
    notes += [o[r].summary() for r in ("R-15", "R-17", "R-18", "R-19", "R-59", "R-60")]
    notes.append(f"process timeline: {tl.source}")
    return RegimeResult(o, vectors, internals, notes)


def _comp(name: str, direction: str | None = None, age: int | None = None, value=None) -> InternalsComponent:
    return InternalsComponent(name, direction, age, _f(value))


def _internals(o: dict[str, RuleOutput], snap: Snap) -> InternalsVector:
    dirn = step1b._dir
    comps: list[InternalsComponent] = []
    r15 = o["R-15"]
    comps.append(_comp("leading_rs", r15.get("direction"), r15.get("turn_age_days"), r15.get("median_rs")))
    r17 = o["R-17"]
    for k in ("curve", "credit_baa", "credit_hy"):
        v = r17.get(f"d_{k}")
        comps.append(_comp(k, dirn(v), None, v))
    comps.append(_comp("qe_signal_weight", None, None, r17.get("weight")))
    r18 = o["R-18"]
    for a in step1b.MOMENTUM_ASSETS:
        if r18.get(f"{a}_roc") is not None:
            comps.append(_comp(f"momentum_{a}", dirn(r18.get(f"{a}_droc")), None, r18.get(f"{a}_roc")))
            comps.append(_comp(f"momentum_bottom_{a}", None, None, 1.0 if r18.get(f"{a}_bottom") else 0.0))
    r19 = o["R-19"]
    for a in step1b.TREND_ASSETS:
        for suf in ("12m", "vs_ma"):
            v = r19.get(f"{a}_{suf}")
            if v is not None:
                comps.append(_comp(f"trend_{a}_{suf}", dirn(v), None, v))
    r59 = o["R-59"]
    comps.append(_comp("narrowing", None, None, None))
    comps.append(_comp("rsp_spy_rel", dirn(r59.values.get("rsp_spy_rel")), None, r59.values.get("rsp_spy_rel")))
    r60 = o["R-60"]
    age = None
    if r60.get("last_thrust"):
        age = snap.asof_day - (_dt.date.fromisoformat(r60.get("last_thrust")) - _dt.date(1970, 1, 1)).days
    thrust = r60.get("thrust_active")
    comps.append(_comp("breadth_thrust", None, age, None if thrust is None else (1.0 if thrust else 0.0)))
    return InternalsVector(direction=r15.get("direction"), turn_age_days=r15.get("turn_age_days"),
                           components=comps)
