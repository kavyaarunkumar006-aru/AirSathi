"""Call every API route function directly (no web server) to check the account, family, diary, advice and admin logic.
Run from backend/:  python -m tests.test_routes     (works with the real FastAPI installed)
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ["SQLITE_PATH"] = str(Path(tempfile.mkdtemp()) / "routes.db")
os.environ.pop("DATABASE_URL", None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import HTTPException  # noqa: E402

from airsathi import db, main  # noqa: E402

ok = 0


def check(cond, msg):
    global ok
    if not cond:
        raise AssertionError(msg)
    ok += 1
    print("  ok -", msg)


def raises(code, f, *a, **k):
    try:
        f(*a, **k)
    except HTTPException as e:
        return e.status_code == code
    return False


db.init()
tok = main.signup(main.SignUp(email="Kavya@Example.com", name="Kavya", password="secret123", age=21, conditions=["lung"]))["token"]
u = main.current_user("Bearer " + tok)
check(u["email"] == "kavya@example.com" and u["is_admin"] == 1, "sign-up lower-cases e-mail; first account is admin")
check(raises(409, main.signup, main.SignUp(email="kavya@example.com", name="X", password="secret123")), "duplicate e-mail refused")
check(raises(401, main.login, main.Login(email="kavya@example.com", password="nope")), "wrong password refused")
check("token" in main.login(main.Login(email="kavya@example.com", password="secret123")), "login works")
check(raises(401, main.current_user, "Bearer junk"), "bad token refused")

me = main.me(u)
check(len(me["members"]) == 1 and me["members"][0]["is_self"] and "lung" in me["members"][0]["groups"], "self member created with profile")
gm = main.member_add(main.MemberIn(name="Ajji", age=72, station="mysuru"), u)
check("older" in gm["groups"] and gm["alert_threshold"] == 101, "grandmother: older adult, alert from 101")
kid = main.member_add(main.MemberIn(name="Chinnu", age=6, alert_threshold=400), u)
check(kid["alert_threshold"] == 101, "child threshold cannot be raised")
check(raises(400, main.member_delete, me["members"][0]["id"], u), "cannot delete yourself")

a = main.advice("silkboard", mode="demo", period="spring", member_id=gm["id"], lang="kn", u=u)
check(a["advice_now"]["headline"]["text"] and a["disclaimer"]["text"], "advice for a family member (Kannada) in demo mode")
g = main.advice("hebbal", mode="demo", period="summer", age=35, conditions="athlete,foo", u=None)
check(g["advice_now"] is not None, "guest advice works")

d = main.diary_add(main.DiaryIn(member_id=kid["id"], symptoms=["cough", "made_up"], mode="demo"), u)
check(d["symptoms"] == ["cough"] and d["aqi"] is not None, "diary keeps known symptoms and records AQI")
lst = main.diary_list(None, u)
check(lst["summary"][0]["symptom"] == "cough" and lst["summary"][0]["count"] == 1, "diary summary")

check(len(main.stations("demo", "spring")) == 8, "8 stations in demo")
check(main.station_detail("madikeri", "demo", "summer")["forecast"], "station detail")
check(raises(404, main.station_detail, "nowhere"), "unknown station -> 404")
check(main.plan("silkboard", "exercise", "demo", "spring")["mode"] == "typical", "planner endpoint")
w = main.weekly("jayanagar", "demo", "spring")
check(len(w["days"]) >= 5 and w["cleanest"], "weekly summary")
check(main.badges(u)["badges"][0]["earned"] and main.badges(u)["streak"] == 1, "badges + streak")
check(main.tip_today("hi")["text"], "tip of the day")
check(main.admin_overview(u)["users"] == 1, "admin overview")
check(main.status()["stations"][0]["tier"] == "none", "status before any job run")

main.forgot(main.Forgot(email="kavya@example.com"))
check(raises(400, main.reset, main.Reset(email="kavya@example.com", code="000000", password="newpass123")), "reset with wrong code refused")
main.device_add(main.Device(token="abc"), u)
check(main.admin_overview(u)["devices"] == 1, "device registered")
check(main.me_delete(u)["ok"] and not db.query("SELECT * FROM members"), "delete account removes all data")
print(f"\nALL {ok} ROUTE CHECKS PASSED")
