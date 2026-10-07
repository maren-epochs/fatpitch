"""Build the 13F-derived cases (PLAN E.3: Duquesne Family Office 13F, QoQ changes, `filed` date as asof).

Usage (network; SEC requires a descriptive User-Agent)::

    .\\.venv\\Scripts\\python.exe tools\\build_13f_cases.py fetch    # download info tables to data\\edgar\\
    .\\.venv\\Scripts\\python.exe tools\\build_13f_cases.py build    # derive cases\\*.yaml from the cache

Derivation (no outcome data used; only the two filings of each quarter pair):

* Long equity positions only: rows with ``putCall`` set (options) are excluded.
* Weight = position value / sum of long-equity values in the same filing (unit-free, so the 2023 change
  of the 13F value unit from $ thousands to $ is irrelevant).
* Delta weight (percentage points) = weight in the later filing minus weight in the earlier one, by
  CUSIP. Top ``TOP_N`` issuers by |delta| are kept.
* Each kept issuer is mapped to a sector family ``equity_us_<sector>`` (``SECTOR`` below; GICS-style
  sector of the issuer, or the ETF's exposure; non-US ADRs/ETFs map to ``equity_<country>``).
* Target expression = up to three families with the largest positive summed delta among the kept
  issuers. Target tilt = sign of each family's summed delta. Window = +-1 quarter. No regime, thesis or
  action target (equity-expression and tilt-sign tests only).
* Baseline (``derivation.prior_tilt``): sign of the same issuers' summed weight change, by family, over the
  previous quarter pair (prior filing -> earlier filing); 0 when unchanged.
"""

from __future__ import annotations

import os
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import yaml

from fatpitch.dates import et_close

ROOT = Path(__file__).resolve().parents[1]
CIK = "1536411"
CACHE = ROOT / "data" / "edgar" / f"{int(CIK):010d}"
UA = os.environ.get("SEC_USER_AGENT", "fatpitch research (set SEC_USER_AGENT to a contact address)")
TOP_N = 10

# (case id, seed id, episode, earlier filing, later filing, seed citation, prior filing); filing = (accession,
# period, filed). The prior filing (one quarter before the earlier one) feeds only the tilt baseline.
PAIRS = [
    ("2020-08-14_duquesne-13f-q2-2020", "C40", "EP16-2020-COVID",
     ("0001536411-20-000004", "2020-03-31", "2020-05-15"),
     ("0001536411-20-000006", "2020-06-30", "2020-08-14"),
     "RS/2020-08-18_gurufocus-q2-2020-13f.md",
     ("0001536411-20-000002", "2019-12-31", "2020-02-14")),
    ("2026-02-17_duquesne-13f-q4-2025", "C55", "EP21-2025-26-ROTATE",
     ("0001536411-25-000017", "2025-09-30", "2025-11-14"),
     ("0001536411-26-000002", "2025-12-31", "2026-02-17"),
     "RS/2026-02-26_bilanz-q4-2025-rotation.md",
     ("0001536411-25-000011", "2025-06-30", "2025-08-15")),
]

# Sector map (by CUSIP) for issuers that appear among the top movers.
# GICS sector at the filing date; ETFs by exposure; RSP (equal-weight S&P 500) = broad US equity.
SECTOR: dict[str, str] = {
    "64110L106": "equity_us_communication",   # Netflix
    "023135106": "equity_us_consumer_disc",   # Amazon
    "30303M102": "equity_us_communication",   # Facebook
    "872590104": "equity_us_communication",   # T-Mobile US
    "98138H101": "equity_us_tech",            # Workday
    "46625H100": "equity_us_financials",      # JPMorgan Chase
    "594918104": "equity_us_tech",            # Microsoft
    "78464A870": "equity_us_health",          # SPDR S&P Biotech ETF (XBI)
    "00507V109": "equity_us_communication",   # Activision Blizzard
    "02079K305": "equity_us_communication",   # Alphabet
    "81369Y605": "equity_us_financials",      # Financial Select Sector SPDR (XLF)
    "46137V357": "equity_us",                 # Invesco S&P 500 Equal Weight ETF (RSP)
    "881624209": "equity_us_health",          # Teva ADS
    "457669307": "equity_us_health",          # Insmed
    "925050106": "equity_us_health",          # Verona Pharma ADS
    "464286400": "equity_br",                 # iShares MSCI Brazil ETF (EWZ)
    "013872106": "equity_us_materials",       # Alcoa
    "29362U104": "equity_us_tech",            # Entegris
    "518415104": "equity_us_tech",            # Lattice Semiconductor
}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    time.sleep(0.2)  # SEC fair-access: stay well below 10 requests/second
    return data


def fetch() -> None:
    for *_, early, late, _cite, prior in PAIRS:
        for acc, _period, _filed in (prior, early, late):
            out = CACHE / acc / "infotable.xml"
            if out.exists():
                continue
            base = f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc.replace('-', '')}"
            idx = json.loads(_get(f"{base}/index.json"))
            names = [i["name"] for i in idx["directory"]["item"]]
            xml = [n for n in names if n.lower().endswith(".xml") and n.lower() != "primary_doc.xml"]
            if len(xml) != 1:
                raise RuntimeError(f"{acc}: cannot identify the information table among {names}")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(_get(f"{base}/{xml[0]}"))
            (out.parent / "source.txt").write_text(f"{base}/{xml[0]}\n", encoding="utf-8")
            print("fetched", acc, xml[0])


def holdings(acc: str) -> dict[str, tuple[str, float]]:
    """{cusip: (issuer | class, value)} for long equity rows (options excluded)."""
    root = ET.parse(CACHE / acc / "infotable.xml").getroot()
    out: dict[str, list] = {}
    for row in root.iter():
        if not row.tag.endswith("infoTable"):
            continue
        f = {c.tag.split("}")[-1]: (c.text or "").strip() for c in row}
        if f.get("putCall"):
            continue
        label = f"{f['nameOfIssuer'].upper()} | {f['titleOfClass'].upper()}"
        out.setdefault(f["cusip"].upper(), [label, 0.0])[1] += float(f["value"])
    return {k: (v[0], v[1]) for k, v in out.items()}


def weights(acc: str) -> tuple[dict[str, float], dict[str, str]]:
    h = holdings(acc)
    tot = sum(v for _, v in h.values())
    return {k: v / tot * 100 for k, (_, v) in h.items()}, {k: lab for k, (lab, _) in h.items()}


def movers(early: str, late: str) -> list[tuple[str, str, float, float, float]]:
    """Top TOP_N (cusip, label, w_prev, w, delta) by |delta|."""
    (a, la), (b, lb) = weights(early), weights(late)
    labels = {**la, **lb}
    rows = [(k, labels[k], a.get(k, 0.0), b.get(k, 0.0), b.get(k, 0.0) - a.get(k, 0.0)) for k in set(a) | set(b)]
    rows.sort(key=lambda r: (-abs(r[4]), r[0]))
    return rows[:TOP_N]


def build() -> None:
    missing = []
    for _cid, _seed, _episode, early, late, _cite, _prior in PAIRS:
        top = movers(early[0], late[0])
        missing += [f"{k} {lab}" for k, lab, *_ in top if k not in SECTOR]
    if missing:
        print("unmapped issuers:", sorted(set(missing)))
        for _cid, _s, _e, early, late, _c, _p in PAIRS:
            for k, lab, wa, wb, d in movers(early[0], late[0]):
                print(f"  {late[1]} {k} {lab:50s} {wa:6.2f} -> {wb:6.2f}  d={d:+.2f}")
        sys.exit(1)
    for cid, seed, episode, early, late, cite, prior in PAIRS:
        top = movers(early[0], late[0])
        fam: dict[str, float] = defaultdict(float)
        for k, _lab, _wa, _wb, d in top:
            fam[SECTOR[k]] += d
        # tilt target: sign of each family's summed delta among the top movers
        tilt = {f: (1 if d > 0 else -1) for f, d in sorted(fam.items()) if round(d, 6) != 0}
        # baseline: the same issuers' previous-quarter change (prior -> earlier filing), by family
        (wp, _), (we, _) = weights(prior[0]), weights(early[0])
        pfam: dict[str, float] = defaultdict(float)
        for k, *_r in top:
            pfam[SECTOR[k]] += we.get(k, 0.0) - wp.get(k, 0.0)
        prior_tilt = {f: (0 if abs(pfam[f]) < 1e-9 else (1 if pfam[f] > 0 else -1)) for f in sorted(fam)}
        adds = [f for f, d in sorted(fam.items(), key=lambda x: (-x[1], x[0])) if d > 0][:3]
        base = f"https://www.sec.gov/Archives/edgar/data/{CIK}"
        doc = {
            "id": cid,
            "asof": et_close(late[2]).isoformat(),
            "era": "A",
            "episode_id": episode,
            "truth_type": "action",
            "mechanizable": "yes",
            "source_reliability": "primary",
            "retrospective": False,
            "targets": {"regime_direction": None, "theses": [], "expression": adds, "action": None, "tilt": tilt},
            "window": {"unit": "quarters", "n": 1},
            "citation": (f"SEC EDGAR 13F-HR, Duquesne Family Office LLC (CIK {CIK}): {early[0]} (period {early[1]},"
                         f" filed {early[2]}) and {late[0]} (period {late[1]}, filed {late[2]}); "
                         f"{base}/{late[0].replace('-', '')}/ ; seed {seed}: {cite}"),
            "date_basis": f"pinned: EDGAR filingDate {late[2]} of the later 13F-HR (PLAN E.3: `filed` is the information date)",
            "seed_id": seed,
            "derivation": {
                "method": "tools/build_13f_cases.py: long-equity weights, QoQ delta (pp), top "
                          f"{TOP_N} issuers by |delta|, summed by family; positive families are targets",
                "top_movers": [{"cusip": k, "issuer": lab, "w_prev_pct": round(wa, 2), "w_pct": round(wb, 2),
                                "delta_pp": round(d, 2), "family": SECTOR[k]} for k, lab, wa, wb, d in top],
                "family_delta_pp": {f: round(d, 2) for f, d in sorted(fam.items())},
                "prior_filing": f"{prior[0]} (period {prior[1]}, filed {prior[2]})",
                "prior_family_delta_pp": {f: round(pfam[f], 2) for f in sorted(fam)},
                "prior_tilt": prior_tilt,
            },
        }
        out = ROOT / "cases" / f"{cid}.yaml"
        out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
        print("wrote", out.name, adds)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    {"fetch": fetch, "build": build}[cmd]()
