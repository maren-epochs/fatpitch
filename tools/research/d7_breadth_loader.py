"""D7 prototype loader: free NYSE breadth sources, no login.

Sources
  unicorn : http://unicorn.us.com/advdec/NYSE_{advn,decln,unchn,advv,declv,unchv,newhi,newlo}.csv
            daily NYSE issues/volume 1965-03-01 .. 2020-02-10 (frozen archive; HTTPS cert
            expired, so plain HTTP is used). New highs/lows from 2005-10.
  wsj     : https://www.wsj.com/market-data/stocks/marketsdiary  JSON endpoint
            (type=mdc_marketsdiary); today's NYSE/Nasdaq advancing, declining,
            unchanged, new highs/lows, up/down volume. Live snapshot only (date
            parameters are ignored), so history must be accumulated by a daily job.

Writes small CSVs under tools/research/sample_data/ (never into amber's lake).
Usage: python d7_breadth_loader.py [unicorn|wsj|all]
"""
from __future__ import annotations
import csv, datetime as dt, json, pathlib, sys, urllib.request

OUT = pathlib.Path(__file__).resolve().parent / "sample_data"
UA = {"User-Agent": "Mozilla/5.0 (research; fatpitch D7 prototype)"}
UNICORN = "http://unicorn.us.com/advdec/NYSE_{}.csv"
FIELDS = ["advn", "decln", "unchn", "advv", "declv", "unchv", "newhi", "newlo"]
WSJ = ("https://www.wsj.com/market-data/stocks/marketsdiary?id=%7B%22application%22%3A%22WSJ%22%2C"
       "%22marketsDiaryType%22%3A%22overview%22%7D&type=mdc_marketsdiary")


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def load_unicorn() -> dict[str, dict[str, float]]:
    """Return {yyyymmdd: {field: value}} for NYSE; zero rows (post-2020-02-10 stubs) dropped."""
    rows: dict[str, dict[str, float]] = {}
    for f in FIELDS:
        for line in get(UNICORN.format(f)).decode().splitlines():
            if "," not in line:
                continue
            d, v = (x.strip() for x in line.split(",", 1))
            rows.setdefault(d, {})[f] = float(v)
    return {d: r for d, r in sorted(rows.items()) if r.get("advn", 0) + r.get("decln", 0) > 0}


def save_unicorn() -> pathlib.Path:
    rows = load_unicorn()
    OUT.mkdir(exist_ok=True)
    p = OUT / "unicorn_nyse_breadth.csv"
    with p.open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["date"] + FIELDS)
        for d, r in rows.items():
            w.writerow([f"{d[:4]}-{d[4:6]}-{d[6:]}"] + [r.get(f, "") for f in FIELDS])
    ds = list(rows)
    print(f"unicorn: {len(rows)} trading days {ds[0]}..{ds[-1]} -> {p}")
    return p


def snapshot_wsj() -> dict:
    j = json.loads(get(WSJ))
    out = {"fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "timestamp": j["data"]["timestamp"]}
    for s in j["data"]["instrumentSets"]:
        label = s["headerFields"][0]["label"]
        for ins in s["instruments"]:
            for exch in ("NYSE", "NASDAQ"):
                out[f"{exch}_{label}_{ins['name']}".replace(" ", "")] = int(ins[exch].replace(",", ""))
    OUT.mkdir(exist_ok=True)
    p = OUT / "wsj_marketsdiary_snapshots.csv"
    new = not p.exists()
    with p.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out)); 
        if new:
            w.writeheader()
        w.writerow(out)
    print(f"wsj: {out['timestamp']} NYSE adv={out['NYSE_Issues_Advancing']} dec={out['NYSE_Issues_Declining']} -> {p}")
    return out


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("unicorn", "all"):
        save_unicorn()
    if which in ("wsj", "all"):
        snapshot_wsj()
