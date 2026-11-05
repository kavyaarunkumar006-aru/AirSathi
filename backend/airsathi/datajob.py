"""The hourly job: fetch data, choose the best source per station, write 'now' + forecasts, send alerts.

Run:  python -m airsathi.datajob        (from the backend/ folder; GitHub Actions runs it every hour)

Source choice for every station (the 'never blank, always honest' rule):
  live      newest station reading < 3 h old   -> now = station AQI; forecast = station AQI + CAMS trend
  recent    3 to 24 h old                       -> same, labelled with the age
  estimate  older than 24 h or no station data  -> now and forecast from bias-corrected CAMS, labelled 'Estimated'
As soon as the station feed comes back, the station switches back to 'live' by itself.
"""
import datetime as dt
import json
import traceback
from pathlib import Path

from . import advice as adv
from . import db, push, sources
from .aqi import POLLUTANTS, category, running_aqi
from .stations import STATIONS
from .views import TIER_LABELS

DATA = Path(__file__).resolve().parents[1] / "data"
HORIZONS = [1, 6, 12, 24]
IST = sources.IST
QUIET_FROM, QUIET_TO = 22, 7            # no notifications between 10 pm and 7 am
COOLDOWN_H = 12


def _load(name, default):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default


RANGES = _load("ranges_persistence.json", {"ranges": {}})["ranges"]
CAL = _load("calibration.json", {"stations": {}})


def _band(v):
    return "low" if v < 60 else ("mid" if v < 100 else "high")


def _series(hourly_map, start, end):
    """Continuous hourly list from start to end (inclusive); missing hours are empty dicts."""
    out, t = [], start
    while t <= end:
        out.append((t, hourly_map.get(t, {})))
        t += dt.timedelta(hours=1)
    return out


def _with_aqi(series):
    res = running_aqi([row for _, row in series])
    return [(t, row, a, d) for (t, row), (a, d) in zip(series, res)]


def process_station(st, now):
    log = {"station": st["id"]}
    # 1) station data (OpenAQ)
    obs = {}
    try:
        obs = sources.openaq_hourly(st["openaq_id"], hours=72)
    except Exception as e:
        log["openaq_error"] = f"{type(e).__name__}: {e}"[:200]
    st_rows = []
    if obs:
        series = _with_aqi(_series(obs, min(obs), max(obs)))
        st_rows = [(t, row, a, d) for t, row, a, d in series]
        db.executemany("INSERT INTO hourly (station, ts, source, pm25, pm10, no2, so2, o3, co, aqi) VALUES (?,?,?,?,?,?,?,?,?,?) "
                       "ON CONFLICT (station, ts, source) DO UPDATE SET pm25=excluded.pm25, pm10=excluded.pm10, no2=excluded.no2, "
                       "so2=excluded.so2, o3=excluded.o3, co=excluded.co, aqi=excluded.aqi",
                       [(st["id"], t.isoformat(), "station", *[row.get(p) for p in POLLUTANTS], a) for t, row, a, _ in st_rows if row])
    valid = [(t, a, d) for t, _, a, d in st_rows if a is not None]
    newest = valid[-1] if valid else None
    age_h = (now - newest[0]).total_seconds() / 3600 if newest else None

    # 2) model data (CAMS), bias-corrected per station
    cams = {}
    try:
        cal = CAL.get("stations", {}).get(st["id"], {})
        cams = {t: sources.correct(r, cal) for t, r in sources.cams_hourly(st["lat"], st["lon"], past_days=2, forecast_days=3).items()}
    except Exception as e:
        log["cams_error"] = f"{type(e).__name__}: {e}"[:200]
    cams_aqi = {}
    if cams:
        series = _with_aqi(_series(cams, min(cams), max(cams)))
        cams_aqi = {t: a for t, _, a, _ in series}
        db.executemany("INSERT INTO hourly (station, ts, source, pm25, pm10, no2, so2, o3, co, aqi) VALUES (?,?,?,?,?,?,?,?,?,?) "
                       "ON CONFLICT (station, ts, source) DO UPDATE SET pm25=excluded.pm25, pm10=excluded.pm10, no2=excluded.no2, "
                       "so2=excluded.so2, o3=excluded.o3, co=excluded.co, aqi=excluded.aqi",
                       [(st["id"], t.isoformat(), "cams_corr", *[row.get(p) for p in POLLUTANTS], a) for t, row, a, _ in series])

    # 3) choose the tier
    hour_now = now.replace(minute=0, second=0, microsecond=0)
    if newest and age_h < 24:
        tier = "live" if age_h < 3 else "recent"
        t0, aqi0, dom = newest
        label = TIER_LABELS[tier] if tier == "live" else f"{TIER_LABELS['recent']}, {round(age_h)} h ago"
        base_cams = cams_aqi.get(t0)
        fc = []
        for h in HORIZONS:
            target = t0 + dt.timedelta(hours=h)
            trend = (cams_aqi.get(target) - base_cams) if (base_cams is not None and cams_aqi.get(target) is not None) else 0
            v = max(0, min(500, aqi0 + trend))
            lo_e, hi_e, _ = RANGES.get(str(h), {}).get(_band(aqi0), [-0.25 * aqi0, 0.25 * aqi0, 0])
            fc.append((h, t0, target, round(v), max(0, round(v + lo_e)), min(500, round(v + hi_e)),
                       "station+cams_trend" if base_cams is not None else "persistence"))
    elif cams_aqi.get(hour_now) is not None:
        tier, t0, aqi0, dom = "estimate", hour_now, cams_aqi[hour_now], None
        label = TIER_LABELS["estimate"]
        res = CAL.get("aqi_residual", {})
        fc = []
        for h in HORIZONS:
            target = t0 + dt.timedelta(hours=h)
            v = cams_aqi.get(target)
            if v is None:
                continue
            lo_e, hi_e = res.get(str(h), [-0.35 * v, 0.35 * v])
            fc.append((h, t0, target, round(v), max(0, round(v + lo_e)), min(500, round(v + hi_e)), "cams"))
        # dominant pollutant from the corrected CAMS sub-indices at this hour is not reliable enough to show; leave empty
    else:
        tier, t0, aqi0, dom, label, fc = "none", None, None, None, TIER_LABELS["none"], []

    db.upsert("station_now", ["station"], {"station": st["id"], "ts": t0.isoformat() if t0 else None, "aqi": aqi0, "dominant": dom,
                                            "tier": tier, "label": label, "data_age_h": round(age_h, 1) if age_h is not None else None,
                                            "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    db.execute("DELETE FROM forecasts WHERE station = ?", (st["id"],))
    for h, o, tg, v, lo, hi, m in fc:
        db.execute("INSERT INTO forecasts (station, horizon, origin, target, aqi, lo, hi, method) VALUES (?,?,?,?,?,?,?,?)",
                   (st["id"], h, o.isoformat(), tg.isoformat(), v, lo, hi, m))
    log.update(tier=tier, aqi=aqi0, age_h=None if age_h is None else round(age_h, 1), forecasts=len(fc))
    return log


def send_alerts(now):
    """One notification per family member when the worst forecast in the next 12 h reaches their alert level."""
    if not push.enabled():
        return {"push": "disabled"}
    if now.hour >= QUIET_FROM or now.hour < QUIET_TO:
        return {"push": "quiet hours"}
    sent = 0
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=COOLDOWN_H)).isoformat()
    for m in db.query("SELECT m.*, u.lang FROM members m JOIN users u ON u.id = m.user_id WHERE m.alerts_on = 1"):
        devices = db.query("SELECT * FROM devices WHERE user_id = ?", (m["user_id"],))
        if not devices:
            continue
        groups = adv.groups_for(m["age"], json.loads(m["conditions"] or "[]"))
        thr = adv.alert_threshold(groups, m["alert_threshold"])
        fc = [f for f in db.query("SELECT * FROM forecasts WHERE station = ? AND horizon <= 12", (m["station"],)) if f["aqi"] is not None]
        if not fc:
            continue
        worst = max(fc, key=lambda f: f["aqi"])
        if worst["aqi"] < thr:
            continue
        if db.one("SELECT id FROM alerts_sent WHERE member_id = ? AND station = ? AND sent_at >= ?", (m["id"], m["station"], since)):
            continue
        st_now = db.one("SELECT * FROM station_now WHERE station = ?", (m["station"],))
        est = st_now and st_now["tier"] == "estimate"
        cat = category(worst["aqi"])
        a = adv.personal_advice(worst["aqi"], m["age"], json.loads(m["conditions"] or "[]"), m["lang"] or "en")
        when = dt.datetime.fromisoformat(worst["target"]).strftime("%I %p").lstrip("0").lower()
        name = next(s["name"] for s in STATIONS if s["id"] == m["station"])
        title = f"{'Estimated ' if est else ''}{cat['name']} air (AQI {worst['aqi']}) at {name}"
        body = f"For {m['name']}, around {when}: {a['actions'][0]['text']}"[:230]
        results = []
        for d in devices:
            r = push.send(d["token"], title, body, {"station": m["station"], "member_id": m["id"], "aqi": worst["aqi"]})
            if r == "invalid_token":
                db.execute("DELETE FROM devices WHERE id = ?", (d["id"],))
            results.append(r)
        db.execute("INSERT INTO alerts_sent (member_id, station, sent_at, level, aqi, target, result) VALUES (?,?,?,?,?,?,?)",
                   (m["id"], m["station"], dt.datetime.now(dt.timezone.utc).isoformat(), "estimated" if est else "likely",
                    worst["aqi"], worst["target"], ",".join(results)))
        sent += results.count("sent")
    return {"push": "ok", "sent": sent}


def main():
    db.init()
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    run_id = db.execute("INSERT INTO job_runs (started, status) VALUES (?, ?)", (started, "running"))
    now = dt.datetime.now(IST).replace(tzinfo=None)
    logs, status = [], "ok"
    try:
        for st in STATIONS:
            try:
                logs.append(process_station(st, now))
            except Exception as e:
                status = "partial"
                logs.append({"station": st["id"], "error": f"{type(e).__name__}: {e}"[:200]})
                traceback.print_exc()
        logs.append(send_alerts(now))
        # keep the database small: drop hourly rows older than 60 days
        db.execute("DELETE FROM hourly WHERE ts < ?", ((now - dt.timedelta(days=60)).isoformat(),))
    except Exception as e:
        status = "failed"
        logs.append({"error": f"{type(e).__name__}: {e}"[:300]})
        traceback.print_exc()
    db.execute("UPDATE job_runs SET finished = ?, status = ?, message = ? WHERE id = ?",
               (dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), status, json.dumps(logs)[:4000], run_id))
    for line in logs:
        print(line)
    return status


if __name__ == "__main__":
    raise SystemExit(0 if main() != "failed" else 1)
