"""Fit the per-station CAMS bias correction and measure how good the 'Estimated' AQI is. Run ONCE on your laptop (needs internet).

    python job/calibrate_cams.py research_inputs/clean_hourly_all_stations.csv

What it does, for each station:
1. Downloads CAMS hourly concentrations (Open-Meteo, free, no key) for the dates where we have real station data.
2. Fits value_station = a + b * value_cams for each pollutant on the FIRST half of the dates.
3. Tests it honestly on the SECOND half: CPCB AQI from corrected CAMS vs the real station AQI (MAE, correlation, category accuracy).
4. Refits on all dates and writes backend/data/calibration.json (used by the hourly job).
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from airsathi.aqi import running_aqi, category  # noqa: E402
from airsathi.stations import STATIONS  # noqa: E402
from airsathi.sources import CAMS_VARS  # noqa: E402

URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
POLL = list(CAMS_VARS)


def fetch_cams(lat, lon, start, end):
    frames = []
    s, end = pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize()
    while s <= end:                                        # download in 90-day pieces
        e = min(s + pd.Timedelta(days=89), end)
        r = requests.get(URL, params={"latitude": lat, "longitude": lon, "hourly": ",".join(CAMS_VARS.values()), "timezone": "Asia/Kolkata",
                                      "start_date": s.date().isoformat(), "end_date": e.date().isoformat()}, timeout=60)
        r.raise_for_status()
        h = r.json()["hourly"]
        df = pd.DataFrame({p: h[v] for p, v in CAMS_VARS.items()}, index=pd.to_datetime(h["time"]))
        frames.append(df)
        s = e + pd.Timedelta(days=1)
        time.sleep(1)
    df = pd.concat(frames)
    df = df[~df.index.duplicated()].astype(float)
    df["co"] = df["co"] / 1000.0                           # ug/m3 -> mg/m3
    return df


def aqi_series(df):
    rows = [{p: (None if pd.isna(v) else float(v)) for p, v in r.items()} for r in df[POLL].to_dict("records")]
    return pd.Series([a for a, _ in running_aqi(rows)], index=df.index, dtype=float)


def fit(x, y):
    m = x.notna() & y.notna()
    if m.sum() < 200:
        return None
    b, a = np.polyfit(x[m], y[m], 1)
    if b <= 0:                                             # never invert the signal; fall back to a pure offset
        b, a = 1.0, float((y[m] - x[m]).mean())
    return {"a": round(float(a), 4), "b": round(float(b), 4), "r": round(float(np.corrcoef(x[m], y[m])[0, 1]), 3), "n": int(m.sum())}


def main(csv):
    H = pd.read_csv(csv, parse_dates=["datetime"])
    out = {"note": "value_station = a + b * value_cams per pollutant; fitted on all overlapping hours. 'test' = honest check on the "
                   "second half after fitting on the first half.", "stations": {}, "test": {}, "aqi_residual": {}}
    resid = []
    for st in STATIONS:
        g = H[H.station == st["id"]].set_index("datetime").sort_index()
        g = g[~g.index.duplicated()].asfreq("h")
        print(f"{st['id']}: downloading CAMS {g.index.min().date()} -> {g.index.max().date()} ...", flush=True)
        cams = fetch_cams(st["lat"], st["lon"], g.index.min(), g.index.max()).reindex(g.index)
        mid = g.index[len(g) // 2]
        first, second = g.index < mid, g.index >= mid
        cal_half = {p: fit(cams.loc[first, p], g.loc[first, p]) for p in POLL}
        corr = pd.DataFrame({p: (cal_half[p]["a"] + cal_half[p]["b"] * cams[p]).clip(lower=0) if cal_half[p] else cams[p] for p in POLL})
        est = aqi_series(corr)
        raw = aqi_series(cams)
        true = g["AQI"]
        m = second & true.notna() & est.notna()
        cat_ok = np.mean([category(a)["key"] == category(b)["key"] for a, b in zip(est[m], true[m])])
        out["test"][st["id"]] = {"hours": int(m.sum()), "mae_raw": round(float((raw[m] - true[m]).abs().mean()), 1),
                                 "mae_corrected": round(float((est[m] - true[m]).abs().mean()), 1),
                                 "r": round(float(np.corrcoef(est[m], true[m])[0, 1]), 3), "category_accuracy": round(float(cat_ok), 3)}
        resid.extend((true[m] - est[m]).dropna().tolist())    # error of the estimate on the test half
        out["stations"][st["id"]] = {p: c for p, c in ((p, fit(cams[p], g[p])) for p in POLL) if c}
        print("   test:", out["test"][st["id"]], flush=True)
    # 80% likely range of the estimate (10th and 90th percentile of true - estimate). CAMS forecasts get the same range at
    # every lead time, which is optimistic for later hours, so the app labels CAMS forecasts 'low confidence'.
    q = [round(float(np.quantile(resid, 0.1)), 1), round(float(np.quantile(resid, 0.9)), 1)]
    out["aqi_residual"] = {str(h): q for h in (1, 6, 12, 24)}
    dest = ROOT / "backend" / "data" / "calibration.json"
    dest.write_text(json.dumps(out, indent=1))
    print("written", dest)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "research_inputs" / "clean_hourly_all_stations.csv"))
