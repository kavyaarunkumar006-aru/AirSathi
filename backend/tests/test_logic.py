"""Offline tests for the AirSathi backend logic (no internet needed).
Run from the backend/ folder:   python -m tests.test_logic
"""
import datetime as dt
import os
import random
import sys
import tempfile
from pathlib import Path

os.environ["SQLITE_PATH"] = str(Path(tempfile.mkdtemp()) / "test.db")
os.environ.pop("DATABASE_URL", None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from airsathi import advice, aqi, auth, datajob, db, planner, sources, views  # noqa: E402

ok = 0


def check(cond, msg):
    global ok
    if not cond:
        raise AssertionError(msg)
    ok += 1
    print("  ok -", msg)


print("CPCB AQI")
check(round(aqi.subindex(45, "pm25")) == 75, "PM2.5 45 ug/m3 -> sub-index 75")
check(round(aqi.subindex(120, "pm10")) == 113, "PM10 120 ug/m3 -> sub-index 113")
check(aqi.aqi_from_averages({"pm25": 45, "pm10": 120})[0] is None, "AQI needs 3 pollutants")
check(aqi.aqi_from_averages({"no2": 10, "o3": 10, "co": 0.5})[0] is None, "AQI needs PM2.5 or PM10")
check(aqi.category(100)["key"] == "satisfactory" and aqi.category(101)["key"] == "moderate", "category edges 100/101")
rows = [{"pm25": 30.0, "pm10": 60.0, "no2": 20.0}] * 16
check(aqi.running_aqi(rows)[-1][0] == 60 and aqi.running_aqi(rows[:15])[-1][0] is None, "16-of-24 rule")

print("Advice")
a = advice.personal_advice(150, age=8, conditions=["lung"])
check(a["vulnerable"] and a["threshold"] == 101 and a["alert"], "child with asthma: vulnerable, alert from 101")
check(advice.personal_advice(150, age=30)["alert"] is False, "healthy adult: no alert at 150")
check(advice.alert_threshold([], 300) == 201, "threshold cannot be raised above the default")
check(not any("N95" in x["text"] for x in advice.personal_advice(250, 30)["actions"]), "no N95 advice below Very Poor")
check(advice.personal_advice(80, lang="hi")["headline"]["text"].startswith("संवेदनशील"), "Hindi text")

print("Auth")
h = auth.hash_password("secret123")
check(auth.check_password("secret123", h) and not auth.check_password("wrong", h), "password hash")
check(auth.read_token(auth.make_token(7)) == 7 and auth.read_token("bad") is None, "JWT token")

print("Demo mode")
v = views.demo_station("silkboard", "spring")
check(v["now"]["aqi"] is not None and len(v["forecast"]) == 4, "demo station has now + 4 forecasts")
check(all(f["lo"] <= f["aqi"] <= f["hi"] for f in v["forecast"]), "likely range contains the forecast")
p = planner.plan(v["plan_input"]["now"], "walk", None, v["plan_input"]["history"], 2)
check(p["mode"] == "typical" and p["message_id"] in ("best_times", "no_clear_time"), "planner typical mode")
check(planner.plan(v["plan_input"]["now"], "walk", None, [], 4)["message_id"] == "limit_all_day", "Very Poor -> limit all day")

print("Hourly job with fake sources")
db.init()
NOW = dt.datetime.now(datajob.IST).replace(tzinfo=None)
H0 = NOW.replace(minute=0, second=0, microsecond=0)


def fake_station(age_h):
    def f(location_id, hours=72):
        if age_h is None:
            return {}
        out = {}
        for k in range(48):
            t = H0 - dt.timedelta(hours=age_h + k)
            out[t] = {"pm25": 30 + random.random() * 5, "pm10": 80 + random.random() * 10, "no2": 20.0, "so2": 5.0, "o3": 30.0, "co": 0.6}
        return out
    return f


def fake_cams(lat, lon, past_days=2, forecast_days=3):
    return {H0 + dt.timedelta(hours=k): {"pm25": 25.0, "pm10": 70.0 + k, "no2": 15.0, "so2": 4.0, "o3": 40.0, "co": 0.4}
            for k in range(-48, 72)}


sources.cams_hourly = fake_cams
for age, expect in [(1, "live"), (10, "recent"), (40, "estimate"), (None, "estimate")]:
    sources.openaq_hourly = fake_station(age)
    log = datajob.process_station(views.BY_ID["hebbal"], NOW)
    lv = views.live_station("hebbal")
    check(log["tier"] == expect and lv["now"]["tier"] == expect and len(lv["forecast"]) == 4,
          f"station data {age} h old -> tier '{expect}' with 4 forecasts")
check(views.live_station("hebbal")["forecast"][0]["method"] == "cams", "estimate tier uses CAMS")
check(views.live_station("hebbal")["plan_input"]["future"], "planner gets CAMS hourly forecast")


def no_cams(*a, **k):
    raise RuntimeError("offline")


sources.cams_hourly = no_cams
sources.openaq_hourly = fake_station(None)
check(datajob.process_station(views.BY_ID["mysuru"], NOW)["tier"] == "none", "no source at all -> tier 'none'")
check(datajob.main() in ("ok", "partial"), "full job run finishes")
check(db.one("SELECT status FROM job_runs ORDER BY id DESC LIMIT 1")["status"] in ("ok", "partial"), "job run recorded")

print(f"\nALL {ok} CHECKS PASSED")
