"""Fetch air-quality data from the two live sources.

1. OpenAQ v3 (real KSPCB station readings, 15-minute). Needs a free key in OPENAQ_API_KEY.
2. Open-Meteo Air Quality (CAMS model, hourly, any location, history + 4-day forecast). No key needed.

Hours are labelled by their START (an hour 10:00 = readings from 10:00 to 10:59), local Indian time, the same as the research data.
Units: concentrations in ug/m3, CO in mg/m3 (as CPCB publishes; same convention as the research project).
"""
import datetime as dt
import os
import time

import requests

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
POLL = ["pm25", "pm10", "no2", "so2", "o3", "co"]
SENTINELS = {999.99, -99.99, 9999.0, -999.0, 999.0, -9999.0}
OPENAQ = "https://api.openaq.org/v3"
CAMS = "https://air-quality-api.open-meteo.com/v1/air-quality"
CAMS_VARS = {"pm25": "pm2_5", "pm10": "pm10", "no2": "nitrogen_dioxide", "so2": "sulphur_dioxide", "o3": "ozone", "co": "carbon_monoxide"}


def _hour(ts):
    return ts.replace(minute=0, second=0, microsecond=0)


# ---------------- OpenAQ ----------------
def _oaq(path, params=None):
    key = os.environ.get("OPENAQ_API_KEY")
    if not key:
        raise RuntimeError("OPENAQ_API_KEY is not set")
    for attempt in range(3):
        try:
            r = requests.get(OPENAQ + path, params=params, headers={"X-API-Key": key}, timeout=40)
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(5)
            continue
        if r.status_code == 429:                  # free tier: 60 requests per minute
            time.sleep(20)
            continue
        if r.status_code >= 500 and attempt < 2:  # OpenAQ hiccup: wait and try again
            time.sleep(5)
            continue
        r.raise_for_status()
        time.sleep(1.1)
        return r.json()
    raise RuntimeError("OpenAQ did not answer after 3 tries")


def openaq_sensors(location_id):
    """{pollutant: sensor_id}, choosing for each pollutant the sensor with the newest reading."""
    best = {}
    for s in _oaq(f"/locations/{location_id}/sensors")["results"]:
        p = s["parameter"]["name"].lower().replace(".", "")
        if p not in POLL:
            continue
        last = (s.get("datetimeLast") or {}).get("utc") or ""
        if p not in best or last > best[p][1]:
            best[p] = (s["id"], last)
    return {p: v[0] for p, v in best.items()}


def openaq_hourly(location_id, hours=48):
    """Hourly means of the last `hours` hours for one station: {hour_start(IST, naive): {pollutant: value}}.
    An hour needs at least 2 valid 15-minute readings (research rule)."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    buckets = {}
    newest = None
    for p, sid in openaq_sensors(location_id).items():
        js = _oaq(f"/sensors/{sid}/measurements", {"datetime_from": since, "limit": 1000})
        for m in js.get("results", []):
            v = m.get("value")
            if v is None or v in SENTINELS or v < 0 or (p in ("pm25", "pm10") and v == 0):
                continue
            # 'datetimeFrom' is the start of the 15-minute reading period
            t_utc = dt.datetime.fromisoformat(m["period"]["datetimeFrom"]["utc"].replace("Z", "+00:00"))
            t = _hour(t_utc.astimezone(IST).replace(tzinfo=None))
            buckets.setdefault(t, {}).setdefault(p, []).append(float(v))
            newest = t if newest is None or t > newest else newest
    out = {t: {p: (sum(vs) / len(vs) if len(vs) >= 2 else None) for p, vs in d.items()} for t, d in buckets.items()}
    # PM2.5 consistency rule from the research cleaning (PM2.5 > 1.5 x PM10 + 20 is rejected)
    for d in out.values():
        if d.get("pm25") is not None and d.get("pm10") is not None and d["pm25"] > 1.5 * d["pm10"] + 20:
            d["pm25"] = None
    return out


# ---------------- Open-Meteo CAMS ----------------
def cams_hourly(lat, lon, past_days=2, forecast_days=3):
    """{hour(IST, naive): {pollutant: value}} from CAMS. CO arrives in ug/m3 and is converted to mg/m3."""
    params = {"latitude": lat, "longitude": lon, "hourly": ",".join(CAMS_VARS.values()), "timezone": "Asia/Kolkata",
              "past_days": past_days, "forecast_days": forecast_days}
    for attempt in range(3):                      # Open-Meteo sometimes times out: try up to 3 times
        try:
            r = requests.get(CAMS, params=params, timeout=60)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(5)
    h = r.json()["hourly"]
    out = {}
    for i, ts in enumerate(h["time"]):
        row = {}
        for p, var in CAMS_VARS.items():
            v = h.get(var, [None] * len(h["time"]))[i]
            row[p] = None if v is None else (v / 1000.0 if p == "co" else float(v))
        out[dt.datetime.fromisoformat(ts)] = row
    return out


def correct(row, cal):
    """Apply a per-station linear correction {pollutant: {a, b}} (value = a + b * cams). Missing -> unchanged."""
    out = {}
    for p, v in row.items():
        c = (cal or {}).get(p)
        out[p] = None if v is None else (max(0.0, c["a"] + c["b"] * v) if c else v)
    return out
