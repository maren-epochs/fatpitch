"""D7: data-quality checks and descriptive thrust counts.

(1) Unicorn NYSE A/D 1965-2020: days per year, gaps, Zweig breadth thrust
    occurrences (10-day EMA of adv/(adv+dec) from <0.40 to >0.615 within 10 days).
(2) S&P 500 members from amber lake (N-PORT SPX holdings, quarter-end, carried
    forward) x Alpaca daily bars 2021+: daily % advancing, % above 50/200-day MA,
    Zweig on members, %>50dma thrust (<=20% to >=80%? reported as counts).
Descriptive only: no returns after signals, no cases.
"""
from __future__ import annotations
import csv, datetime as dt, glob, pathlib
import numpy as np, polars as pl

HERE = pathlib.Path(__file__).resolve().parent
LAKE = r"C:\Users\<user>\Documents\amber\data\lake"


def ema(x: np.ndarray, n: int) -> np.ndarray:
    a = 2 / (n + 1); out = np.empty_like(x); out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def zweig(dates, ratio, lo=0.40, hi=0.615, win=10, n=10):
    e = ema(ratio, n); hits = []; last_lo = None
    for i in range(len(e)):
        if e[i] < lo:
            last_lo = i
        if e[i] > hi and last_lo is not None and i - last_lo <= win:
            hits.append(dates[i]); last_lo = None
    return hits, e


def thrust_level(dates, share, lo, hi, win):
    hits = []; last_lo = None
    for i, s in enumerate(share):
        if np.isnan(s):
            continue
        if s < lo:
            last_lo = i
        if s > hi and last_lo is not None and i - last_lo <= win:
            hits.append(dates[i]); last_lo = None
    return hits


def unicorn():
    rows = list(csv.DictReader(open(HERE / "sample_data" / "unicorn_nyse_breadth.csv")))
    d = [dt.date.fromisoformat(r["date"]) for r in rows]
    adv = np.array([float(r["advn"]) for r in rows]); dec = np.array([float(r["decln"]) for r in rows])
    yrs = {}
    for x in d:
        yrs[x.year] = yrs.get(x.year, 0) + 1
    thin = {y: n for y, n in yrs.items() if n < 245 and y not in (1965, 2020)}
    gaps = [(d[i - 1], d[i]) for i in range(1, len(d)) if (d[i] - d[i - 1]).days > 5]
    print(f"UNICORN NYSE: {len(d)} days {d[0]}..{d[-1]}; years with <245 days: {thin}")
    print(f"  calendar gaps >5 days: {len(gaps)} e.g. {gaps[:6]}")
    print(f"  adv+dec median by decade:", {k: int(np.median((adv+dec)[[x.year//10*10==k for x in d]])) for k in range(1960, 2030, 10) if any(x.year//10*10==k for x in d)})
    r = adv / (adv + dec)
    hits, e = zweig(d, r)
    print(f"  Zweig thrusts (EMA10 <0.40 -> >0.615 within 10d): {len(hits)}: {[h.isoformat() for h in hits]}")
    print(f"  EMA10 share of days <0.40: {(e<0.40).mean()*100:.1f}%  >0.615: {(e>0.615).mean()*100:.2f}%")


def sp500_alpaca():
    fs = sorted(glob.glob(f"{LAKE}/sec_edgar/nport_hist/S000004310-*.parquet"))
    snaps = []
    for f in fs:
        h = pl.read_parquet(f)
        snaps.append((dt.date.fromisoformat(h["report_date"][0]), set(h["symbol"].drop_nulls().to_list()), h.height))
    bars = (pl.scan_parquet(glob.glob(f"{LAKE}/alpaca_basic/bars_daily/*.parquet"))
            .select("symbol", "date", "close").collect())
    allsyms = set().union(*[s for _, s, _ in snaps])
    bars = bars.filter(pl.col("symbol").is_in(list(allsyms))).sort("symbol", "date")
    bars = bars.with_columns(
        (pl.col("close") / pl.col("close").shift(1).over("symbol") - 1).alias("ret"),
        pl.col("close").rolling_mean(50).over("symbol").alias("ma50"),
        pl.col("close").rolling_mean(200).over("symbol").alias("ma200"))
    have = set(bars["symbol"].unique().to_list())
    print(f"\nS&P 500 via N-PORT SPX ({len(snaps)} quarter-end snapshots {snaps[0][0]}..{snaps[-1][0]}) x Alpaca bars")
    for rd, s, n in snaps[::4]:
        print(f"  {rd}: holdings={n} symbols={len(s)} with Alpaca bars={len(s & have)}")
    # membership: snapshot in force = latest report_date <= date (descriptive; PIT would use filing date)
    dates = sorted(bars["date"].unique().to_list())
    snap_for = []
    j = 0
    for x in dates:
        while j + 1 < len(snaps) and snaps[j + 1][0] <= x:
            j += 1
        snap_for.append(j if snaps[j][0] <= x else None)
    memb = pl.DataFrame({"date": dates, "snap": snap_for}).drop_nulls()
    sm = pl.DataFrame([{"snap": i, "symbol": t} for i, (_, s, _) in enumerate(snaps) for t in s])
    panel = bars.join(memb, on="date").join(sm, on=["snap", "symbol"])
    daily = (panel.group_by("date").agg(
        pl.len().alias("n"),
        (pl.col("ret") > 0).sum().alias("adv"), (pl.col("ret") < 0).sum().alias("dec"),
        ((pl.col("close") > pl.col("ma50")).sum() / pl.col("ma50").is_not_null().sum()).alias("pct50"),
        pl.col("ma50").is_not_null().sum().alias("n50"),
        ((pl.col("close") > pl.col("ma200")).sum() / pl.col("ma200").is_not_null().sum()).alias("pct200"),
        pl.col("ma200").is_not_null().sum().alias("n200")).sort("date"))
    daily = daily.filter((pl.col("n") > 400) & (pl.col("adv") + pl.col("dec") > 0))
    out = HERE / "sample_data" / "sp500_breadth_alpaca.csv"
    daily.write_csv(out)
    d = daily["date"].to_list()
    r = (daily["adv"] / (daily["adv"] + daily["dec"])).to_numpy()
    print(f"  daily breadth rows {len(d)} {d[0]}..{d[-1]} median members priced={int(daily['n'].median())} -> {out}")
    hits, e = zweig(d, r)
    print(f"  Zweig on S&P 500 members: {len(hits)} {[h.isoformat() for h in hits]}; EMA<0.40 {(e<0.40).mean()*100:.1f}% >0.615 {(e>0.615).mean()*100:.1f}%")
    p50 = np.where(daily["n50"].to_numpy() > 400, daily["pct50"].to_numpy(), np.nan)
    for lo, hi, win in ((0.20, 0.80, 50), (0.25, 0.75, 30), (0.15, 0.90, 50)):
        h = thrust_level(d, p50, lo, hi, win)
        print(f"  %>50dma thrust <{lo:.0%} -> >{hi:.0%} within {win}d: {len(h)} {[x.isoformat() for x in h]}")
    p200 = daily.filter(pl.col("n200") > 400)
    print(f"  %>200dma available from {p200['date'][0]}; median {p200['pct200'].median():.2f}, p10 {p200['pct200'].quantile(0.1):.2f}, p90 {p200['pct200'].quantile(0.9):.2f}")


if __name__ == "__main__":
    unicorn()
    sp500_alpaca()
