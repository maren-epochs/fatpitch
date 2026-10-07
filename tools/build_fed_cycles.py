"""Build the Fed cycle answer key ``spec\\fed_cycles.yaml`` (owner decision 2026-10-07, option A; spec\\scoring.md 6d).

Inputs (free, public):

* ``FEDFUNDS`` (monthly effective federal funds rate) and ``DFEDTAR`` (target rate, 1982-09-27 -> 2008-12-15) from
  amber's lake (read-only, latest values; the labels are ex-post facts).
* ``DFEDTARU`` (upper bound of the target range, 2008-12-16 ->) from FRED, cached in ``data\\fed\\DFEDTARU.csv``
  (``--refresh`` re-downloads).
* Cross-check: the Federal Reserve Board's tables of policy-rate changes
  (https://www.federalreserve.gov/monetarypolicy/openmarket.htm and openmarket_archive.htm, 1990 ->), parsed and
  cached in ``data\\fed\\openmarket_changes.csv``.

    .\\.venv\\Scripts\\python.exe tools\\build_fed_cycles.py [--refresh] [--end 2026-09]

Mechanics: ``fatpitch.cases.fedcycles``. The output lists every rate cycle (first to last change, with each
target change in the target era), the QT periods, the monthly labels 1970-01 -> ``--end`` and the cross-check result.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import os
import re
import urllib.request
from pathlib import Path

import polars as pl
import yaml

from fatpitch.cases import fedcycles as fc

ROOT = Path(__file__).resolve().parents[1]
AMBER = Path(os.environ.get("AMBER_DATA", r"C:\Users\<user>\Documents\amber\data"))
CACHE = ROOT / "data" / "fed"
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
FED_PAGES = ("https://www.federalreserve.gov/monetarypolicy/openmarket.htm",
             "https://www.federalreserve.gov/monetarypolicy/openmarket_archive.htm")
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}
QT_SOURCES = [
    {"period": "2017-10 .. 2019-07", "start": "2017-10", "end": "2019-07",
     "basis": "FOMC statement 2017-09-20: balance sheet normalization program initiated in October 2017; FOMC "
              "statement 2019-07-31: reduction of aggregate securities holdings concluded in August 2019 (runoff "
              "ends 2019-08-01, last QT month July)",
     "urls": ["https://www.federalreserve.gov/newsevents/pressreleases/monetary20170920a.htm",
              "https://www.federalreserve.gov/newsevents/pressreleases/monetary20190731a.htm"]},
    {"period": "2022-06 .. 2025-11", "start": "2022-06", "end": "2025-11",
     "basis": "FOMC 2022-05-04: Plans for Reducing the Size of the Balance Sheet, runoff beginning June 1, 2022; FOMC "
              "statement 2025-10-29: reduction of aggregate securities holdings concluded on December 1, 2025 (last "
              "QT month November)",
     "urls": ["https://www.federalreserve.gov/newsevents/pressreleases/monetary20220504b.htm",
              "https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm"]},
]


def _lake(sid: str) -> pl.DataFrame:
    df = pl.read_parquet(AMBER / "lake" / "fred" / "series" / f"{sid}.parquet")
    return df.filter(pl.col("value").is_not_null()).select("period_end", "value").sort("period_end")


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (fatpitch research)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def dfedtaru(refresh: bool) -> list[tuple[dt.date, float]]:
    f = CACHE / "DFEDTARU.csv"
    if refresh or not f.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        f.write_bytes(_get(FRED_CSV.format("DFEDTARU")))
    rows = list(csv.reader(f.read_text(encoding="utf-8").splitlines()))[1:]
    return [(dt.date.fromisoformat(d), float(v)) for d, v in rows if v not in ("", ".")]


def openmarket(refresh: bool) -> list[tuple[dt.date, float]]:
    """(date, change in pp, sign from the Increase/Decrease columns) from the Board's tables."""
    f = CACHE / "openmarket_changes.csv"
    if refresh or not f.exists():
        out = []
        for url in FED_PAGES:
            t = _get(url).decode("utf-8", errors="replace")
            for block in re.split(r"<h4>", t)[1:]:
                y = re.match(r"(\d{4})</h4>", block)
                if not y:
                    continue
                year = int(y.group(1))
                for r in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.DOTALL):
                    c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
                         for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.DOTALL)]
                    if len(c) < 3 or c[0] == "Date":
                        continue
                    m = re.match(r"([A-Za-z]+)\s+(\d+)", c[0])
                    if not m or m.group(1) not in MONTHS:
                        continue
                    inc = re.findall(r"\d+", c[1])
                    dec = re.findall(r"\d+", c[2])
                    bp = int(inc[-1]) if inc and inc[-1] != "0" else -int(dec[-1]) if dec else 0
                    out.append((dt.date(year, MONTHS[m.group(1)], int(m.group(2))).isoformat(), bp / 100))
        CACHE.mkdir(parents=True, exist_ok=True)
        with f.open("w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["date", "change_pp"])
            w.writerows(sorted(set(out)))
    rows = list(csv.reader(f.read_text(encoding="utf-8").splitlines()))[1:]
    return [(dt.date.fromisoformat(d), float(v)) for d, v in rows]


def cross_check(cycles, published) -> dict:
    """Every target-era change from 1990 on vs the Board's list: same sign within 1 calendar day."""
    ours = [(dt.date.fromisoformat(ch["date"]), ch["change_pp"]) for c in cycles for ch in c.changes]
    ours = [(d, x) for d, x in ours if d >= dt.date(1990, 1, 1)]
    pub = [(d, x) for d, x in published if d >= dt.date(1990, 1, 1) and x != 0]
    unmatched_ours = [(d, x) for d, x in ours if not any(abs((d - e).days) <= 1 and (x > 0) == (y > 0) for e, y in pub)]
    unmatched_pub = [(e, y) for e, y in pub if not any(abs((d - e).days) <= 1 and (x > 0) == (y > 0) for d, x in ours)]
    return {"scope": "target-era changes from 1990-01-01, same sign within 1 calendar day",
            "n_ours": len(ours), "n_published": len(pub),
            "unmatched_ours": [[d.isoformat(), x] for d, x in unmatched_ours],
            "unmatched_published": [[d.isoformat(), x] for d, x in unmatched_pub]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--end", default=None, help="last labelled month YYYY-MM (default: last month with FEDFUNDS)")
    a = ap.parse_args(argv)
    ff = _lake("FEDFUNDS")
    ffm = [((d.year, d.month), float(v)) for d, v in ff.iter_rows() if d.year >= 1960]
    tar = [(d, float(v)) for d, v in _lake("DFEDTAR").iter_rows()]
    taru = dfedtaru(a.refresh)
    cycles = fc.build_cycles(ffm, tar, taru)
    end = fc.mparse(a.end) if a.end else ffm[-1][0]
    qt = [(fc.mparse(q["start"]), fc.mparse(q["end"])) for q in QT_SOURCES]
    labels = fc.monthly_labels(cycles, qt, fc.START_MONTH, end)
    cyc = [c for c in cycles if c.end >= fc.START_MONTH or c.start >= (1969, 1)]
    xc = cross_check(cycles, openmarket(a.refresh))
    doc = {
        "purpose": "Fed cycle check answer key (spec/scoring.md section 6d; owner decision 2026-10-07, option A). "
                   "Public Fed facts, not documented reads; holdout-period dates may be used.",
        "built_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "rule": {
            "events": "1982-09-27..2008-12-15 changes of FRED DFEDTAR; 2008-12-16.. changes of FRED DFEDTARU "
                      "(the splice step 1.00 -> 0.25 counts as a cut); before 1982-09: turning points of monthly "
                      f"FEDFUNDS (extreme within +-{fc.TP_WINDOW_MONTHS} months, alternation, adjacent moves >= "
                      f"{fc.TP_MIN_MOVE} pp); tightening = month after trough .. peak, easing = month after peak .. trough",
            "cycles": "consecutive same-sign changes form one cycle (first change month .. last change month); "
                      "same-direction cycles across the 1982-09 and 2008-12 splices are merged",
            "label": "easing if inside an easing cycle; else tightening if inside a tightening rate cycle or a QT "
                     "period; else neutral (pause)",
        },
        "sources": {
            "FEDFUNDS": "https://fred.stlouisfed.org/series/FEDFUNDS (amber lake copy)",
            "DFEDTAR": "https://fred.stlouisfed.org/series/DFEDTAR (amber lake copy)",
            "DFEDTARU": "https://fred.stlouisfed.org/series/DFEDTARU (data/fed/DFEDTARU.csv, sha256 "
                        + hashlib.sha256((CACHE / "DFEDTARU.csv").read_bytes()).hexdigest()[:16] + ")",
            "published_chronology": list(FED_PAGES),
        },
        "cross_check_1990_on": xc,
        "cross_check_pre_1990": "Not cross-checked against a downloaded published table: the Board's tables start in "
                                "1990 and the New York Fed historical page returned no content. The pre-1982 rule "
                                "output is listed in full below for review.",
        "qt_periods": QT_SOURCES,
        "rate_cycles": [{"direction": c.direction, "start": fc.mstr(c.start), "end": fc.mstr(c.end), "source": c.source,
                         "level_start": c.level_start, "level_end": c.level_end, "n_changes": len(c.changes),
                         "changes": c.changes} for c in cyc],
        "monthly_labels": {fc.mstr(m): v for m, v in labels.items()},
        "label_counts": {k: sum(v == k for v in labels.values()) for k in ("easing", "neutral", "tightening")},
    }
    out = ROOT / "spec" / "fed_cycles.yaml"
    out.write_text(yaml.safe_dump(doc, sort_keys=False, width=110, allow_unicode=True), encoding="utf-8", newline="\n")
    print(f"wrote {out}: {len(cyc)} rate cycles, {len(labels)} months {doc['label_counts']}; cross-check "
          f"unmatched ours {len(xc['unmatched_ours'])}, published {len(xc['unmatched_published'])}")
    for c in cyc:
        print(f"  {c.direction:10s} {fc.mstr(c.start)} .. {fc.mstr(c.end)}  {c.level_start} -> {c.level_end}  "
              f"({len(c.changes)} changes, {c.source})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
