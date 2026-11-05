# AirSathi backend: what each file does

| File | Job |
| --- | --- |
| `airsathi/main.py` | All API endpoints (FastAPI). Open `/docs` on the running server to see and try them |
| `airsathi/aqi.py` | CPCB AQI: breakpoints, sub-index, categories and colours, 24 h / 8 h running means with the 16-of-24 and 6-of-8 rules |
| `airsathi/advice.py` | Who is vulnerable (conditions, child < 14, older adult >= 60), alert levels, the personal advice list |
| `airsathi/messages.py` | Every health sentence in English, Kannada, Hindi, with its source number |
| `airsathi/planner.py` | "Best time to go out" from hourly PM2.5/PM10 (forecast or the station's usual pattern) |
| `airsathi/views.py` | Builds one station's screen data, in Live mode (database) or Demo mode (`data/demo.json.gz`) |
| `airsathi/datajob.py` | The hourly job: fetch, choose the source (live / recent / estimate), forecasts, push alerts |
| `airsathi/sources.py` | Downloads OpenAQ station readings and Open-Meteo CAMS model data; applies the CAMS correction |
| `airsathi/push.py` | Sends Android notifications through Firebase Cloud Messaging |
| `airsathi/db.py` | Database: SQLite on the laptop, PostgreSQL (Neon) online. Table definitions are at the top |
| `airsathi/auth.py` | Password hashing (PBKDF2) and login tokens (JWT) |
| `airsathi/emailer.py` | Sends the password-reset code by e-mail (Gmail SMTP), or prints it when e-mail is not set up |
| `data/demo.json.gz` | Demo mode: the research project's real out-of-sample CSH-AQI forecasts (built by `job/make_demo_pack.py`) |
| `data/ranges_persistence.json` | 80 % likely ranges for live forecasts, from the research data |
| `data/calibration.json` | CAMS correction per station (created by `job/calibrate_cams.py`; until then CAMS is used uncorrected) |
| `tests/` | `python -m tests.test_logic` and `python -m tests.test_routes`: 51 checks, no internet needed |

Environment variables: `DATABASE_URL`, `JWT_SECRET`, `ADMIN_EMAILS`, `OPENAQ_API_KEY`, `FCM_SERVICE_ACCOUNT`, `SMTP_HOST`, `SMTP_PORT`,
`SMTP_USER`, `SMTP_PASSWORD`. None are needed to run the tests or Demo mode on your laptop.
