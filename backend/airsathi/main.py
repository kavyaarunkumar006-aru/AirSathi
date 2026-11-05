"""AirSathi API (FastAPI).

Run on your laptop (from the backend/ folder):   uvicorn airsathi.main:app --reload --port 8000
Then open http://127.0.0.1:8000/docs to try every endpoint in the browser.
"""
import datetime as dt
import json
import os
import secrets
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import advice as adv
from . import auth, db, emailer, planner, views
from .aqi import category
from .messages import SOURCES, t
from .stations import BY_ID, STATIONS, nearest

app = FastAPI(title="AirSathi API", version="1.0",
              description="Air quality forecasts (CSH-AQI) and personal health advice for 8 KSPCB stations in Karnataka.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
ADMIN_EMAILS = {e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()}
WEB = Path(__file__).resolve().parents[2] / "web"
SYMPTOMS = ["cough", "wheeze", "breathless", "headache", "eye_irritation", "sore_throat", "chest_tight", "tired"]


@app.on_event("startup")
def _startup():
    db.init()


# ---------------- helpers ----------------
def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def current_user(authorization: Optional[str] = Header(None)):
    uid = auth.read_token(authorization.split(" ", 1)[1]) if authorization and authorization.startswith("Bearer ") else None
    if not uid:
        raise HTTPException(401, "Please log in again")
    u = db.one("SELECT * FROM users WHERE id = ?", (uid,))
    if not u:
        raise HTTPException(401, "Account not found")
    db.execute("INSERT INTO visits (user_id, day) VALUES (?, ?) ON CONFLICT (user_id, day) DO NOTHING",
               (uid, dt.date.today().isoformat()))
    return u


def optional_user(authorization: Optional[str] = Header(None)):
    try:
        return current_user(authorization)
    except HTTPException:
        return None


def admin_user(u=Depends(current_user)):
    if not u["is_admin"]:
        raise HTTPException(403, "Admins only")
    return u


def _member(u, member_id):
    m = db.one("SELECT * FROM members WHERE id = ? AND user_id = ?", (member_id, u["id"]))
    if not m:
        raise HTTPException(404, "Family member not found")
    return m


def _member_out(m):
    conds = json.loads(m["conditions"] or "[]")
    groups = adv.groups_for(m["age"], conds)
    return {"id": m["id"], "name": m["name"], "age": m["age"], "conditions": conds, "station": m["station"],
            "is_self": bool(m["is_self"]), "alerts_on": bool(m["alerts_on"]), "groups": groups,
            "alert_threshold": adv.alert_threshold(groups, m["alert_threshold"]),
            "default_threshold": adv.default_alert_threshold(groups)}


def _view(station, mode, period, at):
    if station not in BY_ID:
        raise HTTPException(404, "Unknown station")
    if mode == "demo":
        if period not in views.demo_pack()["periods"]:
            raise HTTPException(400, "Unknown demo period")
        return views.demo_station(station, period, at)
    return views.live_station(station)


# ---------------- stations, forecasts, advice ----------------
@app.get("/api/health")
def health():
    return {"ok": True, "time": _now(), "database": "postgres" if db.IS_PG else "sqlite"}


@app.get("/api/stations")
def stations(mode: str = "live", period: str = "spring", at: Optional[str] = None):
    """All 8 stations with their current AQI (for the map and the station picker)."""
    out = []
    for s in STATIONS:
        v = _view(s["id"], mode, period, at)
        out.append({**s, "now": v["now"]})
    return out


@app.get("/api/stations/nearest")
def station_nearest(lat: float, lon: float):
    return nearest(lat, lon)


@app.get("/api/stations/{station}")
def station_detail(station: str, mode: str = "live", period: str = "spring", at: Optional[str] = None):
    """Current AQI + forecast (+1, +6, +12, +24 h) for one station."""
    return views.public(_view(station, mode, period, at))


@app.get("/api/advice")
def advice(station: str, mode: str = "live", period: str = "spring", at: Optional[str] = None, lang: str = "en",
           member_id: Optional[int] = None, age: Optional[int] = None, conditions: str = "", u=Depends(optional_user)):
    """Personal advice for the current AQI and for the worst forecast in the next 12 hours.
    Logged in: pass member_id. Guest: pass age and conditions (comma-separated: lung,heart,pregnant,outdoor_worker,athlete)."""
    if member_id is not None:
        if not u:
            raise HTTPException(401, "Log in to use family members")
        m = _member(u, member_id)
        age, conds = m["age"], json.loads(m["conditions"])
    else:
        conds = [c for c in conditions.split(",") if c in adv.CONDITIONS]
    v = _view(station, mode, period, at)
    now_aqi = v["now"]["aqi"]
    soon = [f for f in v["forecast"] if f["h"] <= 12 and f["aqi"] is not None]
    worst = max(soon, key=lambda f: f["aqi"]) if soon else None
    seed = int(dt.datetime.fromisoformat(v["now"]["ts"]).timestamp() // 3600) if v["now"]["ts"] else 0
    return {
        "station": v["station"], "now": v["now"],
        "advice_now": adv.personal_advice(now_aqi, age, conds, lang, seed) if now_aqi is not None else None,
        "advice_next12h": adv.personal_advice(worst["aqi"], age, conds, lang, seed) if worst else None,
        "worst_next12h": worst, "disclaimer": t("disclaimer", lang), "sources": SOURCES,
    }


@app.get("/api/plan")
def plan(station: str, activity: str = "walk", mode: str = "live", period: str = "spring", at: Optional[str] = None):
    """Cleanest 1-3 hour windows in the next 36 hours (6 am to 9 pm) for an activity: walk, school_run, exercise, outdoor_work."""
    v = _view(station, mode, period, at)
    pi = v["plan_input"]
    cat = v["now"]["category"]
    return planner.plan(pi["now"], activity, pi["future"], pi["history"], cat["index"] if cat else 0)


@app.get("/api/summary/weekly")
def weekly(station: str, mode: str = "live", period: str = "spring", at: Optional[str] = None):
    """Average hourly AQI for each of the last 7 days (a day needs at least 16 valid hours)."""
    if mode == "demo":
        per = views.demo_pack()["periods"][period]
        s = per["stations"][station]
        i = views.demo_index(period, at)
        t0 = dt.datetime.fromisoformat(per["t0"])
        rows = [((t0 + dt.timedelta(hours=k)), s["obs"][k]) for k in range(max(0, i - 7 * 24), i + 1)]
    else:
        since = (views.now_ist() - dt.timedelta(days=7)).isoformat()
        rows = [(dt.datetime.fromisoformat(r["ts"]), r["aqi"]) for r in
                db.query("SELECT ts, aqi FROM hourly WHERE station = ? AND source = 'station' AND ts >= ? ORDER BY ts", (station, since))]
    days = {}
    for ts, a in rows:
        if a is not None:
            days.setdefault(ts.date().isoformat(), []).append(a)
    out = [{"day": d, "aqi": round(sum(v) / len(v)), "category": category(sum(v) / len(v)), "hours": len(v)}
           for d, v in sorted(days.items()) if len(v) >= 16]
    best = min(out, key=lambda r: r["aqi"]) if out else None
    worst = max(out, key=lambda r: r["aqi"]) if out else None
    return {"station": BY_ID[station], "days": out, "cleanest": best, "worst": worst}


@app.get("/api/demo/periods")
def demo_periods():
    return views.demo_periods()


@app.get("/api/status")
def status():
    """Which data source each station is using right now, and the last hourly job run."""
    rows = {r["station"]: r for r in db.query("SELECT * FROM station_now")}
    job = db.one("SELECT * FROM job_runs ORDER BY id DESC LIMIT 1")
    return {"stations": [{"id": s["id"], "name": s["name"], **({k: rows[s["id"]][k] for k in ("tier", "label", "ts", "updated_at")}
                          if s["id"] in rows else {"tier": "none", "label": views.TIER_LABELS["none"]})} for s in STATIONS],
            "last_job": job}


# ---------------- accounts ----------------
class SignUp(BaseModel):
    email: str
    name: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=8)
    lang: str = "en"
    age: Optional[int] = None
    conditions: List[str] = []
    station: str = "silkboard"


class Login(BaseModel):
    email: str
    password: str


@app.post("/api/auth/signup")
def signup(b: SignUp):
    email = b.email.strip().lower()
    if "@" not in email:
        raise HTTPException(400, "Enter a valid e-mail address")
    if db.one("SELECT id FROM users WHERE email = ?", (email,)):
        raise HTTPException(409, "An account with this e-mail already exists")
    is_admin = 1 if email in ADMIN_EMAILS or not db.one("SELECT id FROM users LIMIT 1") else 0   # first account = admin
    uid = db.execute("INSERT INTO users (email, name, pw_hash, is_admin, lang, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                     (email, b.name.strip(), auth.hash_password(b.password), is_admin, b.lang, _now()))
    db.execute("INSERT INTO members (user_id, name, age, conditions, station, is_self, created_at) VALUES (?, ?, ?, ?, ?, 1, ?)",
               (uid, b.name.strip(), b.age, json.dumps([c for c in b.conditions if c in adv.CONDITIONS]),
                b.station if b.station in BY_ID else "silkboard", _now()))
    return {"token": auth.make_token(uid)}


@app.post("/api/auth/login")
def login(b: Login):
    u = db.one("SELECT * FROM users WHERE email = ?", (b.email.strip().lower(),))
    if not u or not auth.check_password(b.password, u["pw_hash"]):
        raise HTTPException(401, "Wrong e-mail or password")
    return {"token": auth.make_token(u["id"])}


class Forgot(BaseModel):
    email: str


class Reset(BaseModel):
    email: str
    code: str
    password: str = Field(min_length=8)


@app.post("/api/auth/forgot")
def forgot(b: Forgot):
    """E-mails a 6-digit code (valid 30 minutes). Always answers the same, so nobody can test which e-mails exist."""
    u = db.one("SELECT * FROM users WHERE email = ?", (b.email.strip().lower(),))
    if u:
        code = f"{secrets.randbelow(10**6):06d}"
        exp = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=30)).isoformat()
        db.execute("UPDATE users SET reset_code = ?, reset_expires = ? WHERE id = ?", (auth.hash_password(code), exp, u["id"]))
        emailer.send(u["email"], "AirSathi password reset code",
                     f"Your AirSathi reset code is {code}. It is valid for 30 minutes. If you did not ask for it, ignore this e-mail.")
    return {"ok": True, "message": "If this e-mail has an account, a reset code has been sent."}


@app.post("/api/auth/reset")
def reset(b: Reset):
    u = db.one("SELECT * FROM users WHERE email = ?", (b.email.strip().lower(),))
    ok = (u and u["reset_code"] and u["reset_expires"] and dt.datetime.fromisoformat(u["reset_expires"]) > dt.datetime.now(dt.timezone.utc)
          and auth.check_password(b.code.strip(), u["reset_code"]))
    if not ok:
        raise HTTPException(400, "The code is wrong or has expired")
    db.execute("UPDATE users SET pw_hash = ?, reset_code = NULL, reset_expires = NULL WHERE id = ?", (auth.hash_password(b.password), u["id"]))
    return {"token": auth.make_token(u["id"])}


class MeUpdate(BaseModel):
    name: Optional[str] = None
    lang: Optional[str] = None


@app.get("/api/me")
def me(u=Depends(current_user)):
    members = [_member_out(m) for m in db.query("SELECT * FROM members WHERE user_id = ? ORDER BY is_self DESC, id", (u["id"],))]
    return {"id": u["id"], "email": u["email"], "name": u["name"], "lang": u["lang"], "is_admin": bool(u["is_admin"]),
            "members": members}


@app.put("/api/me")
def me_update(b: MeUpdate, u=Depends(current_user)):
    if b.name:
        db.execute("UPDATE users SET name = ? WHERE id = ?", (b.name.strip(), u["id"]))
    if b.lang in ("en", "kn", "hi"):
        db.execute("UPDATE users SET lang = ? WHERE id = ?", (b.lang, u["id"]))
    return me(db.one("SELECT * FROM users WHERE id = ?", (u["id"],)))


@app.delete("/api/me")
def me_delete(u=Depends(current_user)):
    """Delete the account and ALL its data (members, diary, devices)."""
    for tbl in ("diary", "devices", "visits"):
        db.execute(f"DELETE FROM {tbl} WHERE user_id = ?", (u["id"],))
    for m in db.query("SELECT id FROM members WHERE user_id = ?", (u["id"],)):
        db.execute("DELETE FROM alerts_sent WHERE member_id = ?", (m["id"],))
    db.execute("DELETE FROM members WHERE user_id = ?", (u["id"],))
    db.execute("DELETE FROM users WHERE id = ?", (u["id"],))
    return {"ok": True}


# ---------------- family members ----------------
class MemberIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    age: Optional[int] = Field(None, ge=0, le=120)
    conditions: List[str] = []
    station: str = "silkboard"
    alert_threshold: Optional[int] = Field(None, ge=51, le=500)
    alerts_on: bool = True


@app.get("/api/members")
def members(u=Depends(current_user)):
    return me(u)["members"]


@app.post("/api/members")
def member_add(b: MemberIn, u=Depends(current_user)):
    if len(db.query("SELECT id FROM members WHERE user_id = ?", (u["id"],))) >= 6:
        raise HTTPException(400, "You can add up to 5 family members")
    mid = db.execute("INSERT INTO members (user_id, name, age, conditions, station, alert_threshold, alerts_on, created_at) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     (u["id"], b.name.strip(), b.age, json.dumps([c for c in b.conditions if c in adv.CONDITIONS]),
                      b.station if b.station in BY_ID else "silkboard", b.alert_threshold, int(b.alerts_on), _now()))
    return _member_out(_member(u, mid))


@app.put("/api/members/{member_id}")
def member_update(member_id: int, b: MemberIn, u=Depends(current_user)):
    _member(u, member_id)
    db.execute("UPDATE members SET name = ?, age = ?, conditions = ?, station = ?, alert_threshold = ?, alerts_on = ? WHERE id = ?",
               (b.name.strip(), b.age, json.dumps([c for c in b.conditions if c in adv.CONDITIONS]),
                b.station if b.station in BY_ID else "silkboard", b.alert_threshold, int(b.alerts_on), member_id))
    return _member_out(_member(u, member_id))


@app.delete("/api/members/{member_id}")
def member_delete(member_id: int, u=Depends(current_user)):
    m = _member(u, member_id)
    if m["is_self"]:
        raise HTTPException(400, "You cannot remove yourself; delete the account instead")
    db.execute("DELETE FROM diary WHERE member_id = ?", (member_id,))
    db.execute("DELETE FROM alerts_sent WHERE member_id = ?", (member_id,))
    db.execute("DELETE FROM members WHERE id = ?", (member_id,))
    return {"ok": True}


# ---------------- symptom diary ----------------
class DiaryIn(BaseModel):
    member_id: int
    symptoms: List[str]
    note: Optional[str] = Field(None, max_length=300)
    mode: str = "live"
    period: str = "spring"
    at: Optional[str] = None


@app.post("/api/diary")
def diary_add(b: DiaryIn, u=Depends(current_user)):
    m = _member(u, b.member_id)
    syms = [s for s in b.symptoms if s in SYMPTOMS]
    v = _view(m["station"], b.mode, b.period, b.at)
    did = db.execute("INSERT INTO diary (user_id, member_id, ts, symptoms, note, station, aqi) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (u["id"], m["id"], _now(), json.dumps(syms), b.note, m["station"], v["now"]["aqi"]))
    return {"id": did, "aqi": v["now"]["aqi"], "symptoms": syms}


@app.get("/api/diary")
def diary_list(member_id: Optional[int] = None, u=Depends(current_user)):
    q, p = "SELECT * FROM diary WHERE user_id = ?", [u["id"]]
    if member_id is not None:
        q += " AND member_id = ?"
        p.append(member_id)
    rows = db.query(q + " ORDER BY id DESC LIMIT 200", tuple(p))
    entries = [{**r, "symptoms": json.loads(r["symptoms"])} for r in rows]
    # simple summary: how often each symptom was logged, and the average AQI on those entries
    summary = {}
    for e in entries:
        for s in e["symptoms"]:
            d = summary.setdefault(s, {"count": 0, "aqi_sum": 0, "aqi_n": 0})
            d["count"] += 1
            if e["aqi"] is not None:
                d["aqi_sum"] += e["aqi"]
                d["aqi_n"] += 1
    summ = [{"symptom": k, "count": v["count"], "avg_aqi": round(v["aqi_sum"] / v["aqi_n"]) if v["aqi_n"] else None}
            for k, v in sorted(summary.items(), key=lambda kv: -kv[1]["count"])]
    return {"entries": entries, "summary": summ, "symptoms": SYMPTOMS}


@app.delete("/api/diary/{diary_id}")
def diary_delete(diary_id: int, u=Depends(current_user)):
    db.execute("DELETE FROM diary WHERE id = ? AND user_id = ?", (diary_id, u["id"]))
    return {"ok": True}


# ---------------- push devices ----------------
class Device(BaseModel):
    token: str
    platform: str = "android"


@app.post("/api/devices")
def device_add(b: Device, u=Depends(current_user)):
    db.execute("DELETE FROM devices WHERE token = ?", (b.token,))
    db.execute("INSERT INTO devices (user_id, token, platform, created_at) VALUES (?, ?, ?, ?)", (u["id"], b.token, b.platform, _now()))
    return {"ok": True}


# ---------------- eco tips and badges ----------------
ECO_TIPS = ["tip_burn", "tip_fuel", "tip_smoke", "tip_traffic", "tip_check", "tip_mop", "tip_coils", "tip_windows"]


@app.get("/api/tips/today")
def tip_today(lang: str = "en"):
    return t(ECO_TIPS[dt.date.today().toordinal() % len(ECO_TIPS)], lang)


def _streak(days):
    s, d = 0, dt.date.today()
    while d.isoformat() in days:
        s += 1
        d -= dt.timedelta(days=1)
    return s


@app.get("/api/badges")
def badges(u=Depends(current_user)):
    days = {r["day"] for r in db.query("SELECT day FROM visits WHERE user_id = ?", (u["id"],))}
    n_diary = len(db.query("SELECT id FROM diary WHERE user_id = ?", (u["id"],)))
    n_members = len(db.query("SELECT id FROM members WHERE user_id = ?", (u["id"],)))
    streak = _streak(days)
    defs = [("welcome", "Welcome aboard", "Created your AirSathi account", True),
            ("streak_3", "3-day streak", "Checked the air 3 days in a row", streak >= 3),
            ("streak_7", "Air watcher", "Checked the air 7 days in a row", streak >= 7),
            ("diary_1", "First note", "Logged your first symptom", n_diary >= 1),
            ("diary_10", "Health tracker", "Logged 10 diary entries", n_diary >= 10),
            ("family", "Family guardian", "Added a family member", n_members >= 2)]
    return {"streak": streak, "badges": [{"id": i, "title": ti, "description": de, "earned": e} for i, ti, de, e in defs]}


# ---------------- admin ----------------
@app.get("/api/admin/overview")
def admin_overview(u=Depends(admin_user)):
    count = lambda q: db.one(q)["n"]
    return {
        "users": count("SELECT COUNT(*) AS n FROM users"),
        "members": count("SELECT COUNT(*) AS n FROM members"),
        "devices": count("SELECT COUNT(*) AS n FROM devices"),
        "diary_entries": count("SELECT COUNT(*) AS n FROM diary"),
        "alerts_last_7d": db.query("SELECT station, level, COUNT(*) AS n FROM alerts_sent WHERE sent_at >= ? GROUP BY station, level",
                                   ((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).isoformat(),)),
        "recent_users": db.query("SELECT id, name, email, created_at FROM users ORDER BY id DESC LIMIT 10"),
        "job_runs": db.query("SELECT * FROM job_runs ORDER BY id DESC LIMIT 24"),
        "status": status()["stations"],
    }


# ---------------- website ----------------
if WEB.exists():
    app.mount("/web", StaticFiles(directory=WEB), name="web")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(WEB / "index.html")
