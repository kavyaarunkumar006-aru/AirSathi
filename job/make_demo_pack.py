"""Build backend/data/demo.json.gz for Demo mode, from the research project's saved out-of-sample forecasts.

Inputs (from the research project, copied into research_inputs/):
  csh_preds.pkl                    official run's predictions (results/final/csh_preds.pkl)
  clean_hourly_all_stations.csv    cleaned hourly data (data/processed/)
  ranges.json                      80% likely-range rule per horizon and forecast band (backend/ranges.json)
Run once:  python job/make_demo_pack.py research_inputs
Nothing is retrained: Demo mode only replays forecasts made by models fitted before each period started.
"""
import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

src = Path(sys.argv[1] if len(sys.argv) > 1 else "research_inputs")
out = Path(__file__).resolve().parents[1] / "backend" / "data" / "demo.json.gz"
HORIZONS = [1, 6, 12, 24]
PERIODS = {
    "spring": {"split": "val", "label": "Spring 2026 (more polluted)", "note": "validation period, models fitted on earlier data only"},
    "summer": {"split": "test", "label": "Summer 2026 (official test)", "note": "official held-out test period"},
}

preds = pd.read_pickle(src / "csh_preds.pkl")
hourly = pd.read_csv(src / "clean_hourly_all_stations.csv", parse_dates=["datetime"])
ranges = json.loads((src / "ranges.json").read_text())


def num(v, nd=1):
    return None if v is None or not np.isfinite(v) else round(float(v), nd)


pack = {"horizons": HORIZONS, "ranges": ranges["ranges"], "range_bands": ranges["bands"], "periods": {}}
for key, meta in PERIODS.items():
    p1 = preds[1][meta["split"]]
    start, end = p1["datetime"].min(), p1["datetime"].max()
    t0 = start - pd.Timedelta(days=28)                          # 4 weeks of history for the time-of-day planner
    times = pd.date_range(t0, end, freq="h")
    per = {"label": meta["label"], "note": meta["note"], "t0": t0.isoformat(), "start_index": int((start - t0) / pd.Timedelta(hours=1)),
           "n": len(times), "stations": {}}
    for st, g in hourly.groupby("station"):
        g = g.set_index("datetime").reindex(times)
        s = {"obs": [num(v, 0) for v in g["AQI"]], "dom": [d if isinstance(d, str) else None for d in g["dominant"]],
             "pm25": [num(v) for v in g["pm25"]], "pm10": [num(v) for v in g["pm10"]], "f": {}}
        for h in HORIZONS:
            d = preds[h][meta["split"]]
            d = d[d["station"] == st].set_index("datetime")["CSH-AQI ensemble"].reindex(times)
            s["f"][str(h)] = [num(v) for v in d]
        per["stations"][st] = s
    pack["periods"][key] = per
    print(f"{key}: {start} -> {end}, {len(times)} hours x {len(per['stations'])} stations")

out.parent.mkdir(parents=True, exist_ok=True)
with gzip.open(out, "wt", encoding="utf-8") as f:
    json.dump(pack, f, separators=(",", ":"))
print("written", out, f"{out.stat().st_size / 1e6:.2f} MB")
