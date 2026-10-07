"""D3: how often 10y yield, oil and USD all rise together over w months.

Descriptive only: no equity returns, earnings, cases or engine outputs read.
Monthly panel 1973-01..2026-09 (month-end):
  rates  = DGS10 month-end (FRED daily, 1962+)
  oil    = DCOILWTICO month-end (1986+); before 1986 World Bank CMO monthly
           average ('Crude oil, WTI' 1982+, 'Crude oil, average' 1973-81),
           chained by ratio at the join month
  USD    = DTWEXM (major currencies, 1973-2019) chained by ratio to DTWEXBGS
           (broad, 2006+) at 2006-01
Daily panel 1986+ uses business-day windows 21/63/126/252.
"""
from __future__ import annotations
import datetime as dt
import numpy as np
import polars as pl

LAKE = r"C:\Users\<user>\Documents\amber\data\lake"


def fred(sid: str) -> pl.DataFrame:
    return (pl.read_parquet(f"{LAKE}/fred/series/{sid}.parquet")
            .select(pl.col("period_end").alias("d"), pl.col("value").alias(sid)).drop_nulls().sort("d"))


def chain(old: pl.DataFrame, new: pl.DataFrame, col_old: str, col_new: str, at: dt.date, name: str) -> pl.DataFrame:
    o = old.filter(pl.col("d") <= at); n = new.filter(pl.col("d") >= at)
    r = n[col_new][0] / o[col_old][-1]
    return pl.concat([o.select("d", (pl.col(col_old) * r).alias(name)).filter(pl.col("d") < n["d"][0]),
                      n.select("d", pl.col(col_new).alias(name))])


def month_end(df: pl.DataFrame) -> pl.DataFrame:
    return (df.with_columns(pl.col("d").dt.month_start().alias("m"))
            .group_by("m").agg(pl.all().exclude("d").last()).sort("m"))


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


def main() -> None:
    usd_d = chain(fred("DTWEXM"), fred("DTWEXBGS"), "DTWEXM", "DTWEXBGS", dt.date(2006, 1, 2), "usd")
    r_d = fred("DGS10").rename({"DGS10": "r"})
    wti_d = fred("DCOILWTICO").rename({"DCOILWTICO": "oil"})

    cmo = pl.read_parquet(f"{LAKE}/cbp/worldbank_cmo/monthly_prices.parquet")
    avg = cmo.filter(pl.col("commodity") == "Crude oil, average").select(pl.col("date").dt.month_start().alias("m"), pl.col("value").alias("a"))
    wti_cmo = cmo.filter(pl.col("commodity") == "Crude oil, WTI").drop_nulls("value").select(pl.col("date").dt.month_start().alias("m"), pl.col("value").alias("w"))
    pre = avg.join(wti_cmo, on="m", how="left").sort("m")
    j82 = pre.filter(pl.col("m") == dt.date(1982, 1, 1))
    k = j82["w"][0] / j82["a"][0]
    pre = pre.with_columns(pl.when(pl.col("w").is_not_null()).then(pl.col("w")).otherwise(pl.col("a") * k).alias("oil")).select("m", "oil")
    oil_m_daily = month_end(wti_d)
    j86 = oil_m_daily.filter(pl.col("m") == dt.date(1986, 1, 1))["oil"][0] / pre.filter(pl.col("m") == dt.date(1986, 1, 1))["oil"][0]
    oil_m = pl.concat([pre.filter(pl.col("m") < dt.date(1986, 1, 1)).with_columns(pl.col("oil") * j86), oil_m_daily]).sort("m")

    m = (month_end(r_d).join(oil_m, on="m").join(month_end(usd_d), on="m")
         .filter((pl.col("m") >= dt.date(1973, 1, 1)) & (pl.col("m") <= dt.date(2026, 9, 1))).sort("m"))
    print(f"monthly panel {m['m'][0]}..{m['m'][-1]} n={m.height}")
    r, o, u = (m[c].to_numpy() for c in ("r", "oil", "usd"))
    months = m["m"].to_list()
    print("\nMONTHLY, all three up over w months (rates in pp change > 0, oil and USD % change > 0)")
    print("w   share_all3  indep_expect  spells  spells/decade  median_len  mean_len  max_len  share_r share_o share_u")
    for w in (1, 3, 6, 12):
        dr, do, du = r[w:] - r[:-w], o[w:] / o[:-w] - 1, u[w:] / u[:-w] - 1
        a = (dr > 0) & (do > 0) & (du > 0)
        sp = runs(a)
        yrs = len(a) / 12
        print(f"{w:<3} {a.mean()*100:9.1f}%  {(dr>0).mean()*(do>0).mean()*(du>0).mean()*100:10.1f}%  {len(sp):6d}  "
              f"{len(sp)/yrs*10:12.1f}  {np.median(sp):9.1f}  {np.mean(sp):8.1f}  {max(sp):7d}  "
              f"{(dr>0).mean()*100:6.0f}% {(do>0).mean()*100:6.0f}% {(du>0).mean()*100:6.0f}%")
        # pairwise correlations of changes
        c = np.corrcoef(np.vstack([dr, do, du]))
        print(f"     corr(dr,doil)={c[0,1]:.2f} corr(dr,dusd)={c[0,2]:.2f} corr(doil,dusd)={c[1,2]:.2f}")
        # spell start months listing for w in (3,6,12)
        if w in (3, 6, 12):
            starts, n = [], 0
            for i, x in enumerate(a):
                if x and (i == 0 or not a[i - 1]):
                    j = i
                    while j < len(a) and a[j]:
                        j += 1
                    starts.append((months[i + w].strftime("%Y-%m"), j - i))
            long_ = [f"{s}({L}m)" for s, L in starts if L >= 3]
            print(f"     spells >=3 months ({len(long_)}): {', '.join(long_)}")
        # by decade
        dec = {}
        for i, x in enumerate(a):
            dkey = (months[i + w].year // 10) * 10
            dec.setdefault(dkey, []).append(x)
        print("     share by decade:", " ".join(f"{k}s={np.mean(v)*100:.0f}%" for k, v in sorted(dec.items())))

    # daily panel 1986+
    d = r_d.join(wti_d, on="d").join(usd_d, on="d").sort("d").filter(pl.col("oil") > 0)
    r, o, u = (d[c].to_numpy() for c in ("r", "oil", "usd"))
    print(f"\nDAILY panel {d['d'][0]}..{d['d'][-1]} n={d.height}; on/off flips per year (signal evaluated every business day)")
    for w, lab in ((21, "1m"), (63, "3m"), (126, "6m"), (252, "12m")):
        a = (r[w:] - r[:-w] > 0) & (o[w:] / o[:-w] > 1) & (u[w:] / u[:-w] > 1)
        sp = runs(a)
        flips = int((np.diff(a.astype(int)) != 0).sum())
        print(f"  {lab:>3}: share={a.mean()*100:5.1f}%  spells={len(sp):4d}  median_len={np.median(sp):5.0f}bd  "
              f"mean_len={np.mean(sp):5.0f}bd  flips/yr={flips/(len(a)/252):5.1f}  spells>=20bd={sum(1 for s in sp if s>=20)}")


if __name__ == "__main__":
    main()
