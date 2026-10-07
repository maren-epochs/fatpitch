"""Coverage report for the step-1/1b inputs over amber's lake: ``python -m fatpitch.lake_coverage``.

Writes ``spec\\data_coverage.md``: per input the first date usable point-in-time, frequency, method and gaps;
per research era-B case date (asof < 2002, holdout episodes excluded) which inputs and rule families are
available point-in-time. Case files are read only for their ``asof`` and ``episode_id`` lines; targets are
never parsed. Uses ``AmberLakeSource`` (``AMBER_DATA``) and the catalogue; read-only.
"""

from __future__ import annotations

import datetime as _dt
import re
import sys
import time
import warnings
from pathlib import Path

from fatpitch.dates import NY
from fatpitch.lake import AmberLakeSource, catalogue_ids, load_catalogue

REPO = Path(__file__).resolve().parents[2]
STALE_DAYS = {"D": 10, "W": 21, "M": 75, "Q": 200, "A": 760}
ZERO_BEFORE = {"RRPONTSYD": _dt.date(2003, 2, 7), "WSHOMCB": _dt.date(2002, 12, 18)}  # process.md R-03/R-04

# rule family -> list of requirements; each requirement is a tuple of alternatives (any one suffices)
RULES: dict[str, list[tuple[str, ...]]] = {
    "R-02 M2-IP": [("M2SL",), ("INDPRO", "INDPRO_FR")],
    "R-03 net liquidity": [("WALCL",), ("WTREGEN",), ("RRPONTSYD",)],
    "R-03 proxy (NETLIQ)": [("NETLIQ",)],
    "R-04 purchases-issuance": [("TREAST",), ("WSHOMCB",), ("TFD_DEBT_HELD_PUBLIC",)],
    "R-06 Taylor gap": [("UNRATE", "UNRATE_FR"), ("NROU",), ("CPIAUCSL",), ("FEDFUNDS", "DFF")],
    "R-07/R-09 inflation": [("CPIAUCSL",), ("DFEDTARU", "FEDFUNDS")],
    "R-08 FF vs CPI": [("CPIAUCSL",), ("FEDFUNDS", "DFF")],
    "R-10 rates+oil+USD": [("DGS10",), ("DCOILWTICO",), ("USD_BROAD",)],
    "R-11 fragility (>=2)": [],
    "R-12 US": [("WALCL",), ("FEDFUNDS",), ("IRLTLT01USM156N",)],
    "R-12 EA (Bundesbank pre-1999)": [
        ("ECBASSETSW", "DE_CB_ASSETS"),
        ("ECB_DFR", "DE_POLICY_RATE"),
        ("IRLTLT01DEM156N",),
    ],
    "R-12 JP": [("JPNASSETS",), ("JP_POLICY_RATE", "JP_CALL_RATE_M"), ("IRLTLT01JPM156N",)],
    "R-12 UK": [("BOE_ASSETS",), ("UK_BANK_RATE",), ("IRLTLT01GBM156N",)],
    "R-14 policy direction": [("DFEDTARU", "FEDFUNDS"), ("TREAST",)],
    "R-56 10y vs NGDP": [("DGS10",), ("GDP",)],
    "R-58 FCI": [("NFCI",)],
    "R-63 fiscal": [("TFD_DEBT_HELD_PUBLIC",), ("FYFSGDA188S",), ("UNRATE",), ("NROU",)],
    "R-15/16/59 industries": [("FRENCH49",)],
    "R-17 curve+credit": [("DGS10", "GS10"), ("DGS2", "TB3MS"), ("BAA",)],
    "R-18 momentum": [("SHILLER_SP",)],
    "R-19 cross-asset": [
        ("US_EQ_FUT_PROXY", "NASDAQCOM"),
        ("DGS10",),
        ("USD_BROAD",),
        ("GOLD_LBMA",),
        ("DCOILWTICO",),
        ("PCOPPUSDM",),
    ],
    "R-60 breadth": [("ZWEIG_EMA10",)],
}
FRAGILITY = [
    "RITTER_UNPROF_IPO",
    "SIFMA_HY_SHARE_A",
    "BCNSDODNS",
    "NCBCEBQ027S",
    "BAMLH0A0HYM2",
    "FINRA_MARGIN_DEBT",
]
DEFINITIONS = (
    "Definitions. *First usable PIT*: earliest date on which a snapshot at 16:00 ET returns at least one "
    "row with `usable = true` (published_at <= asof; D-graded proxies and pre-vintage rows under policy "
    "`unknown` excluded); fallbacks count, with their grade shown. *Method / grade at start*: method and "
    "proxy grade of the newest usable row on that date. *Largest gap*: largest spacing between consecutive "
    "usable periods in the full-history snapshot, shown when above 2.5x the nominal spacing. Availability "
    "at a case date additionally requires the newest usable period to be no older than the larger of "
    "{bounds} (by catalogue frequency) and the rows' own cadence (median publication lag + 1.5 x median "
    "spacing + 7 d; freshness bound). RRPONTSYD and WSHOMCB count as available (zero) before their first "
    "observation (process.md R-03, R-04)."
)
INPUT_HEADER = (
    "| Id | Step | Rules | Status | Freq | First usable PIT | Method / grade at start "
    "| Vintage source by era | Largest gap | Catalogue gaps |"
)
FINDINGS = [  # (item, effect on era B)
    (
        "WTREGEN before 2002-12: only LDGUST (legacy TGA), graded D on the overlap",
        "R-03 primary unknown; NETLIQ proxy (Z.1 CB assets - TGA, quarterly, grade C) is the usable variant",
    ),
    (
        "NROU: lake stamps periods 1990-Q1..2010 with the 2011-02-02 ALFRED initial vintage",
        "asofs 1990-2011: newest visible NROU period 1989-Q4 (stale gap in R-06, R-63; needs CBO vintages)",
    ),
    ("NFCI first published 2011-05-25; earlier values are a backcast", "R-58 unknown before 2011-05"),
    (
        "FYFSGDA188S, CPILFESL, French-49, historical FOMC calendar, SP500 not in the lake",
        "R-63 fiscal term, R-06 core sensitivity, R-15/R-16/R-59 industry rules unknown in every era-B case",
    ),
    (
        "HY OAS, SIFMA HY share, FINRA margin debt start 1996-1997",
        "R-11 runs on 3 of 6 components before 1997 (Ritter, Z.1 debt, Z.1 net equity issuance)",
    ),
    (
        "CPIAUCSL before 1972-07-21: CPIAUCNS fallback, grade C",
        "no era-B research case is affected (first case 1981)",
    ),
    ("IRLTLT01JPM156N starts 1989-01", "R-12 JP long rate unknown for cases before 1989"),
]


def _close(d: _dt.date) -> _dt.datetime:
    return _dt.datetime.combine(d, _dt.time(16, 0), tzinfo=NY)


def _month_ends(start: _dt.date, end: _dt.date) -> list[_dt.date]:
    out, y, m = [], start.year, start.month
    while True:
        nxt = _dt.date(y + (m == 12), m % 12 + 1, 1)
        d = nxt - _dt.timedelta(days=1)
        if d > end:
            return out
        out.append(d)
        y, m = nxt.year, nxt.month


class _Probe:
    def __init__(self, src: AmberLakeSource, cat: dict):
        self.src, self.cat = src, cat

    def frame(self, sid: str, d: _dt.date):
        return self.src.snapshot(_close(d), series=[sid])[sid]

    def usable(self, sid: str, d: _dt.date, fresh: bool = False) -> bool:
        f = self.frame(sid, d)
        f = f.filter(f["usable"]) if f.height else f
        if not f.height:
            return False
        if not fresh:
            return True
        return (d - f["period_end"].max()).days <= self.bound(sid, f)

    def bound(self, sid: str, f) -> float:
        """Freshness bound in days: the larger of the nominal bound for the catalogue frequency and the
        rows' own cadence (median publication lag + 1.5 x median spacing + 7 d over the last 12 rows), so a
        monthly fallback or a slow-publishing source is judged on its own release pattern."""
        lim = STALE_DAYS.get(str(self.cat["series"][sid].get("freq")), 10_000)
        tail = f.tail(13)
        lag = (tail["published_at"].dt.date() - tail["period_end"]).dt.total_days().median() or 0
        sp = tail["period_end"].diff().dt.total_days().median() if tail.height > 1 else 0
        return max(lim, float(lag) + 1.5 * float(sp or 0) + 7)

    def available(self, sid: str, d: _dt.date) -> bool:
        if sid in ZERO_BEFORE and d < ZERO_BEFORE[sid]:
            return True
        return self.cat["series"][sid].get("status") != "missing" and self.usable(sid, d, fresh=True)

    def first_usable(self, sid: str, end: _dt.date) -> _dt.date | None:
        months = _month_ends(_dt.date(1913, 1, 1), end)
        lo = next((i for i, m in enumerate(months) if self.usable(sid, m)), None)
        if lo is None:
            return None
        start = months[lo - 1] + _dt.timedelta(days=1) if lo else _dt.date(1913, 1, 1)
        d = start
        while d <= months[lo]:
            if self.usable(sid, d):
                return d
            d += _dt.timedelta(days=1)
        return months[lo]


def _fmt_first(d: _dt.date | None) -> str:
    if d is None:
        return "never"
    return f"<= {d}" if d == _dt.date(1913, 1, 1) else str(d)


def _largest_gap(frame, freq: str) -> str:
    f = frame.filter(frame["usable"]) if frame.height else frame
    if f.height < 2:
        return ""
    pe = f["period_end"].sort()
    gaps = pe.diff().dt.total_days().to_list()[1:]
    i = max(range(len(gaps)), key=lambda k: gaps[k])
    nominal = {"D": 4, "W": 7, "M": 31, "Q": 92, "A": 366}.get(freq, 31)
    if gaps[i] <= 2.5 * nominal:
        return ""
    return f"{pe[i]} -> {pe[i + 1]} ({int(gaps[i])} d)"


def research_era_b_cases(root: Path) -> list[tuple[str, _dt.date]]:
    hold = set()
    hp = root / "cases" / "HOLDOUT.yaml"
    if hp.exists():
        txt = hp.read_text(encoding="utf-8")
        block = re.search(r"^holdout_episodes:\n((?:- .*\n)+)", txt, re.MULTILINE)
        if block:
            hold = {ln[2:].strip() for ln in block.group(1).splitlines()}
    out = []
    for f in sorted((root / "cases").glob("[0-9]*.yaml")):
        asof = ep = None
        with open(f, encoding="utf-8") as fh:
            for ln in fh:
                if ln.startswith("asof:"):
                    asof = _dt.datetime.fromisoformat(ln.split(":", 1)[1].strip().strip("'\"")).date()
                elif ln.startswith("episode_id:"):
                    ep = ln.split(":", 1)[1].strip()
                if asof and ep:
                    break
        if asof and asof < _dt.date(2002, 1, 1) and ep not in hold:
            out.append((f.stem, asof))
    return out


def _rule_ok(p: _Probe, reqs, d: _dt.date) -> tuple[bool, list[str]]:
    miss = []
    for alts in reqs:
        if not any(p.available(a, d) for a in alts):
            miss.append("|".join(alts))
    return not miss, miss


def build(today: _dt.date | None = None) -> str:
    warnings.simplefilter("ignore")
    cat = load_catalogue()
    today = today or _dt.datetime.now(NY).date()
    step_ids = [s for s in catalogue_ids(cat, step=("1", "1b"), include_missing=True)]
    src = AmberLakeSource(
        series=[s for s in step_ids if cat["series"][s].get("status") != "missing"], catalogue=cat
    )
    p = _Probe(src, cat)

    # performance: step-1 set, weekly replay 1960 -> today
    s1 = [s for s in catalogue_ids(cat, step="1")]
    src.snapshot(_close(_dt.date(1990, 1, 2)), series=s1)
    dates = [
        _dt.date(1960, 1, 4) + _dt.timedelta(days=7 * i)
        for i in range(((today - _dt.date(1960, 1, 4)).days) // 7)
    ]
    t0 = time.perf_counter()
    for d in dates:
        src.snapshot(_close(d), series=s1)
    per = (time.perf_counter() - t0) / len(dates) * 1000

    bounds = ", ".join(f"{k} {v} d" for k, v in STALE_DAYS.items())
    lines = [
        "# Data coverage: step 1 and 1b inputs (amber lake, point-in-time)",
        "",
        (
            f"Generated {today} by `python -m fatpitch.lake_coverage` from `spec\\data_catalogue.yaml` over "
            "`<AMBER_DATA>\\lake` through `fatpitch.lake.AmberLakeSource`. Do not edit by hand."
        ),
        "",
        DEFINITIONS.format(bounds=bounds),
        "",
        (
            f"Snapshot performance: step-1 set ({len(s1)} ids), weekly asofs 1960-01-04 -> {today} "
            f"({len(dates)} snapshots), warm cache: **{per:.1f} ms per snapshot** (target < 50 ms)."
        ),
        "",
        "## 1. Inputs",
        "",
        INPUT_HEADER,
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    now = _close(today)
    for sid in step_ids:
        e = cat["series"][sid]
        if e.get("status") == "missing":
            lines.append(
                f"| {sid} | {e['step']} | {', '.join(e.get('rules', []))} | **missing** | {e.get('freq')} "
                f"| - | - | - | - | {e.get('notes', '')} |"
            )
            continue
        fu = p.first_usable(sid, today)
        meth = "-"
        if fu:
            f = p.frame(sid, fu)
            f = f.filter(f["usable"])
            last = f.row(-1, named=True)
            meth = f"{last['method']} / {last['proxy_grade']}"
        full = src.snapshot(now, series=[sid])[sid]
        era = e.get("vintage_by_era", "") or ("latest lake values (" + e.get("pit_method", "") + ")")
        gaps = (e.get("gaps") or "").replace("|", "/")
        lines.append(
            f"| {sid} | {e['step']} | {', '.join(e.get('rules', []))} | {e.get('status')} | {e.get('freq')} "
            f"| {_fmt_first(fu)} | {meth} | {era} | {_largest_gap(full, str(e.get('freq')))} | {gaps} |"
        )

    cases = research_era_b_cases(REPO)
    lines += [
        "",
        "## 2. Research era-B case dates",
        "",
        (
            f"Research split only (holdout episodes excluded): {len(cases)} cases with asof before 2002 in "
            "`cases\\` at generation time. Case files were read for `asof` and `episode_id` only."
        ),
        "",
        "### 2.1 Rule families computable point-in-time",
        "",
        (
            "Y = every requirement has a fresh usable input (alternatives separated by `|`); "
            "otherwise the missing requirements are listed."
        ),
        "",
    ]
    rule_names = list(RULES)
    lines.append("| Rule family | " + " | ".join(f"{c[1]}" for c in cases) + " |")
    lines.append("|---|" + "---|" * len(cases))
    all_ok = {c[0]: True for c in cases}
    for rn in rule_names:
        cells = []
        for cid, d in cases:
            if rn.startswith("R-11"):
                n = sum(p.available(s, d) for s in FRAGILITY)
                ok = n >= 2
                cells.append(f"Y ({n}/6)" if ok else f"{n}/6")
            else:
                ok, miss = _rule_ok(p, RULES[rn], d)
                cells.append("Y" if ok else ", ".join(miss))
        lines.append(f"| {rn} | " + " | ".join(cells) + " |")
    groups: list[tuple[str, ...]] = []
    for rn, reqs in RULES.items():
        if rn.startswith(("R-15", "R-17", "R-18", "R-19", "R-60", "R-03 proxy")):
            continue
        for alts in reqs:
            if alts not in groups:
                groups.append(alts)
    groups += [(s,) for s in FRAGILITY if (s,) not in groups]
    lines += [
        "",
        "### 2.2 Step-1 inputs missing at each case date",
        "",
        (
            "Step-1 inputs named in process.md (rule families R-02..R-14, R-56, R-58, R-63; alternatives "
            "separated by `|`, one fresh usable alternative suffices) without a fresh usable row at the case "
            "asof. Auxiliary catalogue ids (e.g. GDPPOT, DFEDTARL, TFD_NET_*) are not required."
        ),
        "",
        f"Requirement groups checked ({len(groups)}): " + ", ".join("|".join(g) for g in groups) + ".",
        "",
        "| Case | Asof | Every step-1 input available | Missing or stale step-1 inputs |",
        "|---|---|---|---|",
    ]
    for cid, d in cases:
        miss = ["|".join(g) for g in groups if not any(p.available(a, d) for a in g)]
        all_ok[cid] = not miss
        lines.append(f"| {cid} | {d} | {'yes' if not miss else 'no'} | {', '.join(miss)} |")
    n_all = sum(all_ok.values())
    lines += [
        "",
        f"Cases with every step-1 input available point-in-time: {n_all} of {len(cases)}.",
        "",
        "## 3. Findings",
        "",
        "| Item | Effect on era B |",
        "|---|---|",
        *[f"| {i} | {e} |" for i, e in FINDINGS],
        "",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    out = REPO / "spec" / "data_coverage.md"
    text = build()
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
