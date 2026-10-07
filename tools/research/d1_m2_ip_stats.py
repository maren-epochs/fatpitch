"""D1: descriptive statistics of L2 = yoy(M2SL) - yoy(INDPRO).

Descriptive only: no returns, no cases, no engine outputs are read.
Real-time construction: at each month-end as-of date, take the ALFRED
vintage of each series in force on that date, use its latest observation,
and compute growth within that vintage. M2SL vintages start 1980-02; before
that the current-vintage series is used (flagged). Also reports the
latest-vintage (revised) series and alternative growth windows.
"""
from __future__ import annotations
import datetime as dt
import numpy as np
import polars as pl

LAKE = r"C:\Users\<user>\Documents\amber\data\lake"


def realtime_growth(vint: pl.DataFrame, asofs: list[dt.date], window_m: int, annualize: bool) -> dict:
    out = {}
    v = vint.drop_nulls("value").sort("date")
    for a in asofs:
        snap = v.filter((pl.col("realtime_start") <= a) & (pl.col("realtime_end") >= a))
        if snap.height < window_m + 1:
            continue
        dates = snap["date"].to_list(); vals = snap["value"].to_list()
        last = dates[-1]
        y, m = last.year, last.month - window_m
        while m <= 0:
            m += 12; y -= 1
        prev = dt.date(y, m, 1)
        try:
            i = dates.index(prev)
        except ValueError:
            continue
        g = vals[-1] / vals[i]
        out[a] = ((g ** (12 / window_m)) - 1) * 100 if annualize else (g - 1) * 100
    return out


def final_growth(ser: pl.DataFrame, window_m: int, annualize: bool) -> pl.DataFrame:
    s = ser.sort("period_end").with_columns(
        (pl.col("value") / pl.col("value").shift(window_m)).alias("g"))
    expr = ((pl.col("g") ** (12 / window_m)) - 1) * 100 if annualize else (pl.col("g") - 1) * 100
    return s.with_columns(expr.alias("growth")).select(
        pl.col("period_end").dt.month_start().alias("m"), "growth")


def runs(mask: np.ndarray) -> list[int]:
    out, n = [], 0
    for x in mask:
        if x:
            n += 1
        elif n:
            out.append(n); n = 0
    if n:
        out.append(n)
    return out


def describe(name: str, x: np.ndarray) -> None:
    x = x[~np.isnan(x)]
    pct = np.percentile(x, [5, 10, 25, 50, 75, 90, 95])
    print(f"\n== {name}: n={len(x)} mean={x.mean():.2f} sd={x.std():.2f}")
    print("pctiles 5/10/25/50/75/90/95:", " ".join(f"{p:.2f}" for p in pct))
    for t in [0, 1, 2, 3, 4, 5, 6, 7]:
        m = x > t
        r = runs(m)
        print(f"  >{t}pp: share={m.mean()*100:5.1f}%  spells={len(r):3d}  "
              f"median_len={np.median(r) if r else 0:4.1f}m  mean_len={np.mean(r) if r else 0:4.1f}m  "
              f"max_len={max(r) if r else 0}")
    neg = runs(x < 0)
    print(f"  <0pp: share={(x<0).mean()*100:5.1f}% spells={len(neg)} median_len={np.median(neg):.1f}m")
    ac = [np.corrcoef(x[:-k], x[k:])[0, 1] for k in (1, 3, 6, 12)]
    print("  autocorr lag1/3/6/12:", " ".join(f"{a:.2f}" for a in ac))
    # sign flips of the 3-state impulse at threshold 2 (diagnostic of noise)


def flips(x: np.ndarray, thr: float) -> int:
    state = np.where(x > thr, 1, np.where(x < 0, -1, 0))
    return int((np.diff(state) != 0).sum())


def main() -> None:
    m2v = pl.read_parquet(f"{LAKE}/fred/vintages/M2SL.parquet")
    ipv = pl.read_parquet(f"{LAKE}/fred/vintages/INDPRO.parquet")
    m2f = pl.read_parquet(f"{LAKE}/fred/series/M2SL.parquet")
    ipf = pl.read_parquet(f"{LAKE}/fred/series/INDPRO.parquet")

    # latest-vintage (revised) L2, monthly, 1960-2026
    for w, ann in [(12, False), (6, True), (3, True), (24, True)]:
        a = final_growth(m2f, w, ann).rename({"growth": "m2"})
        b = final_growth(ipf, w, ann).rename({"growth": "ip"})
        j = a.join(b, on="m").drop_nulls().filter(pl.col("m") >= dt.date(1960, 1, 1)).sort("m")
        j = j.with_columns((pl.col("m2") - pl.col("ip")).alias("L2"))
        x = j["L2"].to_numpy()
        lab = f"REVISED L2, window={w}m{' annualized' if ann else ''}"
        describe(lab, x)
        print(f"  3-state flips per decade at thr 2pp: {flips(x, 2.0) / (len(x) / 120):.1f}; "
              f"thr 0 (sign only): {flips(x, 0.0) / (len(x) / 120):.1f}")
        if w == 12:
            rev = j
            ex = j.filter(pl.col("m") < dt.date(2020, 3, 1))["L2"].to_numpy()
            describe("REVISED L2 12m, excluding 2020-03..2021-12 (COVID/M2 break)",
                     np.concatenate([ex, j.filter(pl.col("m") >= dt.date(2022, 1, 1))["L2"].to_numpy()]))
            for lo, hi in [(1960, 1979), (1980, 1999), (2000, 2019), (2022, 2026)]:
                seg = j.filter((pl.col("m") >= dt.date(lo, 1, 1)) & (pl.col("m") <= dt.date(hi, 12, 31)))
                s = seg["L2"].to_numpy()
                print(f"  era {lo}-{hi}: median={np.median(s):.2f} p25={np.percentile(s,25):.2f} "
                      f"p75={np.percentile(s,75):.2f} p90={np.percentile(s,90):.2f} share>2={np.mean(s>2)*100:.0f}% "
                      f"share>5={np.mean(s>5)*100:.0f}% share<0={np.mean(s<0)*100:.0f}%")
            # components
            print("  component medians: M2 yoy", f"{np.median(j['m2'].to_numpy()):.2f}",
                  "IP yoy", f"{np.median(j['ip'].to_numpy()):.2f}",
                  "sd M2", f"{j['m2'].std():.2f}", "sd IP", f"{j['ip'].std():.2f}")
            print("  share of L2 variance from IP:",
                  f"{j['ip'].var() / j['L2'].var():.2f}; from M2: {j['m2'].var() / j['L2'].var():.2f}; "
                  f"corr(m2,ip)={np.corrcoef(j['m2'], j['ip'])[0,1]:.2f}")
            print("  2020-2021 path:")
            print(j.filter((pl.col("m") >= dt.date(2020, 1, 1)) & (pl.col("m") <= dt.date(2021, 12, 1)))
                  .select("m", pl.col("m2").round(1), pl.col("ip").round(1), pl.col("L2").round(1)).to_numpy().tolist())

    # real-time (vintage-aware) 12m L2 at month-ends 1980-02..2026-09
    asofs = []
    y, m = 1980, 3
    while (y, m) <= (2026, 9):
        nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
        asofs.append(nxt - dt.timedelta(days=1))
        y, m = (y + (m == 12), m % 12 + 1)
    m2r = realtime_growth(m2v, asofs, 12, False)
    ipr = realtime_growth(ipv, asofs, 12, False)
    keys = [a for a in asofs if a in m2r and a in ipr]
    rt = np.array([m2r[a] - ipr[a] for a in keys])
    describe("REAL-TIME L2 12m (vintage in force at each month-end), 1980-2026", rt)
    # revision noise: real-time vs revised for the same reference month is not aligned exactly
    # (latest obs month differs); compare at as-of level with revised L2 lagged 1 month
    revd = {r[0]: r[1] for r in rev.select("m", "L2").iter_rows()}
    diffs = []
    for a in keys:
        ref = dt.date(a.year, a.month, 1)
        ym = (ref.year * 12 + ref.month - 1) - 1  # latest M2 obs is ~1 month before as-of month
        refm = dt.date(ym // 12, ym % 12 + 1, 1)
        if refm in revd:
            diffs.append(m2r[a] - ipr[a] - revd[refm])
    diffs = np.array(diffs)
    print(f"\nreal-time minus revised (approx aligned): mean={diffs.mean():.2f} "
          f"MAD={np.median(np.abs(diffs)):.2f} p90|d|={np.percentile(np.abs(diffs),90):.2f}")


if __name__ == "__main__":
    main()


def m2_ngdp() -> None:
    """Companion: yoy(M2SL, quarter avg) - yoy(GDP nominal), quarterly, revised data."""
    m2 = pl.read_parquet(f"{LAKE}/fred/series/M2SL.parquet")
    gdp = pl.read_parquet(f"{LAKE}/fred/series/GDP.parquet")
    q = (m2.with_columns(pl.col("period_end").dt.truncate("1q").alias("q")).group_by("q")
         .agg(pl.col("value").mean().alias("m2"), pl.len().alias("k")).filter(pl.col("k") == 3).sort("q"))
    g = gdp.with_columns(pl.col("period_end").dt.truncate("1q").alias("q")).select("q", pl.col("value").alias("gdp")).sort("q")
    j = q.join(g, on="q").sort("q").with_columns(
        ((pl.col("m2") / pl.col("m2").shift(4) - 1) * 100 - (pl.col("gdp") / pl.col("gdp").shift(4) - 1) * 100).alias("x")).drop_nulls()
    x = j.filter(pl.col("q") >= dt.date(1960, 1, 1))["x"].to_numpy()
    print(f"\n== M2 yoy minus nominal GDP yoy (Marshallian-k growth), quarterly 1960-2026: n={len(x)}")
    print("pctiles 5/10/25/50/75/90/95:", " ".join(f"{p:.2f}" for p in np.percentile(x, [5, 10, 25, 50, 75, 90, 95])))
    print("share >0/2/5:", " ".join(f"{np.mean(x > t) * 100:.0f}%" for t in (0, 2, 5)))


if __name__ == "__main__":
    m2_ngdp()
