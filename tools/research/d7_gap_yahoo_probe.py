"""D7 gap probe (2020-02 .. 2021-09): how many S&P 500 members on 2020-06-01
(fja05680/sp500, MIT licence) still return 2020 daily bars from Yahoo's public
chart endpoint (no login). Measures survivorship loss; writes counts only."""
import csv, io, json, time, urllib.request, urllib.parse, datetime as dt
UA = {"User-Agent": "Mozilla/5.0"}
SRC = "https://raw.githubusercontent.com/fja05680/sp500/master/S%26P%20500%20Historical%20Components%20%26%20Changes%20(Updated).csv"

def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
        return r.read()

rows = list(csv.DictReader(io.StringIO(get(SRC).decode())))
target = dt.date(2020, 6, 1)
best = max((r for r in rows if dt.date.fromisoformat(r["date"]) <= target), key=lambda r: r["date"])
tick = sorted(t.strip() for t in best["tickers"].split(","))
print(f"constituents file rows={len(rows)} first={rows[0]['date']} last={rows[-1]['date']}; snapshot {best['date']} n={len(tick)}")
p1, p2 = int(dt.datetime(2020, 2, 1).timestamp()), int(dt.datetime(2021, 9, 30).timestamp())
ok, miss = 0, []
for t in tick:
    y = t.replace(".", "-")
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(y)}?period1={p1}&period2={p2}&interval=1d"
    try:
        j = json.loads(get(u)); res = j["chart"]["result"]
        n = len(res[0].get("timestamp") or []) if res else 0
    except Exception:
        n = 0
    if n > 300:
        ok += 1
    else:
        miss.append(t)
    time.sleep(0.4)
# retry misses once, slower, to separate throttling from true absence
retry = []
for t in miss:
    time.sleep(1.5)
    y = t.replace(".", "-")
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(y)}?period1={p1}&period2={p2}&interval=1d"
    try:
        j = json.loads(get(u)); res = j["chart"]["result"]
        n = len(res[0].get("timestamp") or []) if res else 0
    except Exception:
        n = 0
    if n > 300:
        ok += 1
    else:
        retry.append(t)
miss = retry
print(f"Yahoo returned >300 bars for {ok}/{len(tick)} ({ok/len(tick):.1%}); missing {len(miss)}: {' '.join(miss)}")
