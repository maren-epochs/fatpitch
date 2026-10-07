"""D3 supplement: frequency of joint rises when each change must exceed k
standard deviations of its own w-month change (full-sample sd; descriptive)."""
import numpy as np, sys
sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import d3_xasset_stats as s
import polars as pl, datetime as dt

def panel():
    usd_d = s.chain(s.fred("DTWEXM"), s.fred("DTWEXBGS"), "DTWEXM", "DTWEXBGS", dt.date(2006, 1, 2), "usd")
    r_d = s.fred("DGS10").rename({"DGS10": "r"}); wti_d = s.fred("DCOILWTICO").rename({"DCOILWTICO": "oil"})
    m = (s.month_end(r_d).join(s.month_end(wti_d), on="m").join(s.month_end(usd_d), on="m")
         .filter(pl.col("m") <= dt.date(2026, 9, 1)).sort("m"))
    return m

m = panel()
r, o, u = (m[c].to_numpy() for c in ("r", "oil", "usd"))
print(f"monthly 1986-01..2026-09 n={len(r)}")
print("w   k=0     k=0.25  k=0.5   k=1.0   (share of months all three changes > k*sd)  | sd: d10y(pp) oil% usd%")
for w in (1, 3, 6, 12):
    dr, do, du = r[w:] - r[:-w], np.log(o[w:] / o[:-w]), np.log(u[w:] / u[:-w])
    row = []
    for k in (0, 0.25, 0.5, 1.0):
        a = (dr > k * dr.std()) & (do > k * do.std()) & (du > k * du.std())
        row.append(f"{a.mean()*100:5.1f}%({len(s.runs(a))})")
    print(f"{w:<3} " + "  ".join(row) + f"  | {dr.std():.2f} {do.std()*100:.1f} {du.std()*100:.1f}")
