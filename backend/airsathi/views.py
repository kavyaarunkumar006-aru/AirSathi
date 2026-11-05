"""Build what the app shows for one station, in Live mode (from the database) or Demo mode (from demo.json.gz).

Both modes return the SAME shape, so the app does not care where the numbers come from:
{station, mode, now: {ts, aqi, category, dominant, tier, label, age_h}, forecast: [{h, target, aqi, lo, hi, category, confidence}],
 plan_input: {future, history}}
"""
import datetime as dt
import functools
import gzip
import json
from pathlib import Path

from . import db
from .aqi import category
from .stations import BY_ID

DATA = Path(__file__).resolve().parents[1] / "data"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
HORIZONS = [1, 6, 12, 24]

TIER_LABELS = {
    "live": "Live station data",
    "recent": "Last station reading",
    "estimate": "Estimated (CAMS model), not official CPCB AQI",
    "none": "No data available",
    "demo": "Demo mode: replay of real past forecasts",
}


def confidence(h):
    return "high" if h <= 6 else "moderate"


def now_ist():
    return dt.datetime.now(IST).replace(tzinfo=None)


# ---------------- Demo mode ----------------
@functools.lru_cache(maxsize=1)
def demo_pack():
    with gzip.open(DATA / "demo.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def _band(v, bands=("low", "mid", "high")):
    return bands[0] if v < 60 else (bands[1] if v < 100 else bands[2])


def demo_periods():
    p = demo_pack()["periods"]
    out = []
    for k, v in p.items():
        t0 = dt.datetime.fromisoformat(v["t0"])
        out.append({"id": k, "label": v["label"], "note": v["note"],
                    "start": (t0 + dt.timedelta(hours=v["start_index"])).isoformat(),
                    "end": (t0 + dt.timedelta(hours=v["n"] - 1)).isoformat(), "hours": v["n"] - v["start_index"]})
    return out


@functools.lru_cache(maxsize=4)
def _default_index(period):
    """First hour (from 3 days into the period) at which the most stations have a reading and a forecast."""
    per = demo_pack()["periods"][period]
    best, best_n = per["start_index"] + 72, -1
    for i in range(per["start_index"] + 72, per["n"]):
        n = sum(1 for s in per["stations"].values() if s["obs"][i] is not None and s["f"]["24"][i] is not None)
        if n > best_n:
            best, best_n = i, n
        if n == len(per["stations"]):
            break
    return best


def demo_index(period, at=None):
    """Hour index into a period for a simulated time (default: 3 days after the period starts)."""
    per = demo_pack()["periods"][period]
    t0 = dt.datetime.fromisoformat(per["t0"])
    if at is None:
        return _default_index(period)
    i = int((dt.datetime.fromisoformat(at) - t0).total_seconds() // 3600)
    return max(per["start_index"], min(per["n"] - 1, i))


def demo_station(st, period="spring", at=None):
    pack = demo_pack()
    per = pack["periods"][period]
    s = per["stations"][st]
    i = demo_index(period, at)
    t0 = dt.datetime.fromisoformat(per["t0"])
    ts = t0 + dt.timedelta(hours=i)
    # newest observed AQI at or before the simulated hour (a missing hour falls back to the last valid one, up to 24 h)
    j, aqi = i, None
    while j >= max(0, i - 24) and aqi is None:
        aqi = s["obs"][j]
        j -= 1
    age = i - (j + 1)
    fc = []
    for h in HORIZONS:
        v = s["f"][str(h)][i]
        if v is None:
            continue
        lo_e, hi_e, _ = pack["ranges"][str(h)][_band(v)]
        fc.append({"h": h, "target": (ts + dt.timedelta(hours=h)).isoformat(), "aqi": round(v),
                   "lo": max(0, round(v + lo_e)), "hi": min(500, round(v + hi_e)), "category": category(v),
                   "confidence": confidence(h), "method": "CSH-AQI"})
    hist = [(t0 + dt.timedelta(hours=k), s["pm25"][k], s["pm10"][k]) for k in range(max(0, i - 28 * 24), i + 1)]
    return {
        "station": BY_ID[st], "mode": "demo", "period": period, "period_label": per["label"],
        "now": {"ts": ts.isoformat(), "aqi": aqi, "category": category(aqi), "dominant": s["dom"][j + 1] if aqi is not None else None,
                "tier": "demo", "label": TIER_LABELS["demo"], "age_h": age},
        "forecast": fc, "plan_input": {"future": None, "history": hist, "now": ts},
    }


# ---------------- Live mode ----------------
def live_station(st):
    row = db.one("SELECT * FROM station_now WHERE station = ?", (st,))
    now = now_ist()
    if not row:
        return {"station": BY_ID[st], "mode": "live",
                "now": {"ts": None, "aqi": None, "category": None, "dominant": None, "tier": "none",
                        "label": TIER_LABELS["none"], "age_h": None},
                "forecast": [], "plan_input": {"future": None, "history": [], "now": now}}
    fc = []
    for f in db.query("SELECT * FROM forecasts WHERE station = ? ORDER BY horizon", (st,)):
        fc.append({"h": f["horizon"], "target": f["target"], "aqi": f["aqi"], "lo": f["lo"], "hi": f["hi"],
                   "category": category(f["aqi"]), "confidence": confidence(f["horizon"]) if f["method"] != "cams" else "low",
                   "method": f["method"]})
    since = (now - dt.timedelta(days=28)).isoformat()
    hist = [(dt.datetime.fromisoformat(r["ts"]), r["pm25"], r["pm10"])
            for r in db.query("SELECT ts, pm25, pm10 FROM hourly WHERE station = ? AND source = 'station' AND ts >= ? ORDER BY ts",
                              (st, since))]
    future = [(dt.datetime.fromisoformat(r["ts"]), r["pm25"], r["pm10"])
              for r in db.query("SELECT ts, pm25, pm10 FROM hourly WHERE station = ? AND source = 'cams_corr' AND ts > ? ORDER BY ts",
                                (st, now.isoformat()))]
    age = None
    if row["ts"]:
        age = round((now - dt.datetime.fromisoformat(row["ts"])).total_seconds() / 3600, 1)
    return {
        "station": BY_ID[st], "mode": "live",
        "now": {"ts": row["ts"], "aqi": row["aqi"], "category": category(row["aqi"]), "dominant": row["dominant"],
                "tier": row["tier"], "label": row["label"], "age_h": age, "updated_at": row["updated_at"]},
        "forecast": fc, "plan_input": {"future": future or None, "history": hist, "now": now},
    }


def public(view):
    """Drop internal fields before sending to the app."""
    v = dict(view)
    v.pop("plan_input", None)
    return v
