# AirSathi: air-quality forecasts and health advice for everyone

AirSathi is an Android app and website. It shows India's official **CPCB Air Quality Index (AQI)** for 8 KSPCB stations in
Karnataka and forecasts it 1 to 24 hours ahead with the **CSH-AQI model** (from the research project). It turns the AQI into simple
advice from CPCB, MoHFW (NCDC) and WHO, for every person in the family.

| Part | Folder | What it is |
| --- | --- | --- |
| Android app | `android/` | Kotlin + Jetpack Compose. Home, Plan (map + best time), Health (advice, diary, weekly), Me (family, settings) |
| Website | `web/` | One page, also works on iPhone. Includes the admin dashboard |
| Backend API | `backend/airsathi/` | Python FastAPI. Accounts, family, advice, planner, diary, badges, Demo mode |
| Hourly job | `backend/airsathi/datajob.py` | Fetches data, chooses the best source, writes forecasts, sends phone alerts. Runs on GitHub Actions |
| Research code (reused) | `model/` | `aq_clean.py`, `aq_model.py`: CPCB AQI and the CSH-AQI model |
| Tools | `job/` | `make_demo_pack.py` (Demo mode data), `calibrate_cams.py` (CAMS correction) |

## How it works

```
OpenAQ (station readings) ─┐                                   ┌─> Firebase ──> phone notifications
                           ├─> hourly job (GitHub Actions) ────┤
Open-Meteo CAMS (model) ───┘        writes                      └─> PostgreSQL (Neon) <── FastAPI (Render) <── app + website
```

**Live data, never blank, always honest.** Every hour the job checks each station:

| Station reading age | What the app shows | Label in the app |
| --- | --- | --- |
| under 3 h | station AQI, forecast = station AQI + CAMS trend | Live station data |
| 3 to 24 h | the same | Last station reading, x h ago |
| older than 24 h | AQI computed from bias-corrected CAMS model data | Estimated (CAMS model), not official CPCB AQI |

It switches back to live station data by itself when the KSPCB feed comes back. (In Oct 2026 OpenAQ's CPCB feed stopped nationwide.)

**Demo mode** replays the research project's real CSH-AQI forecasts hour by hour (spring 2026 validation period and the official
summer 2026 test period). Nothing is retrained. Use it in the viva.

---

# Step-by-step guide

Do the steps in order. Each step says how to check that it worked.

## Step 1. Put the code on GitHub

1. Install **GitHub Desktop** (desktop.github.com) and sign in with your GitHub account.
2. GitHub Desktop: **File → Clone repository →** pick `kavyaarunkumar006-aru/airsathi` → Local path e.g. `C:\Users\kavya\Documents\GitHub\airsathi` → **Clone**.
3. Unzip `airsathi.zip`. Open the unzipped `airsathi` folder, select **everything inside it** (Ctrl+A, including the `.github` folder)
   and copy it into the cloned folder from step 2.
4. Back in GitHub Desktop you now see about 70 changed files. Bottom left, Summary: `First version of AirSathi` → **Commit to main** → **Push origin**.
5. Check: open github.com/kavyaarunkumar006-aru/airsathi. You see the folders `.github`, `android`, `backend`, `web`...

The `.gitignore` file keeps secrets (`.env`, `google-services.json`, the Firebase key) out of GitHub. Never remove those lines.

## Step 2. Try the backend on your laptop (optional, 10 min)

In VS Code open the `airsathi` folder, then in the terminal (PowerShell):
```
cd backend
pip install -r requirements.txt
python -m tests.test_logic
python -m tests.test_routes
uvicorn airsathi.main:app --reload --port 8000
```
Check: both tests print `ALL ... PASSED`; then open http://127.0.0.1:8000 (website) and http://127.0.0.1:8000/docs (every API endpoint,
with a "Try it out" button). Press Ctrl+C to stop the server. Locally the data is stored in `backend/data/airsathi.db`.

## Step 3. Create the database (Neon)

1. neon.tech → your project `airsathi` → **Dashboard → Connect**.
2. Copy the **connection string**. It starts with `postgresql://` and contains a password. Keep it secret.
3. Keep it in Notepad for steps 4 and 5.

## Step 4. Put the API online (Render)

1. render.com → **New → Blueprint** → connect GitHub → choose the `airsathi` repo → **Apply**. It reads `render.yaml`.
2. It asks for values:
   - `DATABASE_URL` = the Neon connection string
   - `ADMIN_EMAILS` = your e-mail (that account gets the admin dashboard)
   - `SMTP_USER` / `SMTP_PASSWORD` = optional, for "forgot password" e-mails (Gmail address + a Gmail App Password). Leave empty for now if you like.
3. Wait for the build (3 to 5 min). Render shows your address, e.g. `https://airsathi-api.onrender.com`.
4. Check: open `https://<your address>/api/health` → `{"ok": true, ..., "database": "postgres"}`. Then open the address itself: the website.

Free Render servers sleep after 15 minutes without visitors; the first visit then takes about a minute. Open the website once before the viva.

## Step 5. Start the hourly job (GitHub Actions)

1. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**. Add three secrets:
   - `DATABASE_URL` = the Neon connection string
   - `OPENAQ_API_KEY` = your OpenAQ key
   - `FCM_SERVICE_ACCOUNT` = open `firebase-service-account.json` in Notepad, select all (Ctrl+A), copy, paste
2. Repo → **Actions** tab → if asked, click **I understand my workflows, go ahead and enable them**.
3. Click **hourly-data-job → Run workflow → Run workflow**.
4. Check: after about 2 minutes the run has a green tick. Click it → **run** → the last step prints one line per station, e.g.
   `{'station': 'silkboard', 'tier': 'estimate', 'aqi': 74, ...}`. The website in Live mode now shows numbers.
   From now on it runs every hour by itself.

## Step 6. Calibrate the CAMS estimate (recommended, 15 min, once)

This fits the per-station correction for the CAMS model and measures honestly how good the "Estimated" AQI is.
```
pip install pandas numpy requests
copy ..\aqi-latest\data\processed\clean_hourly_all_stations.csv research_inputs\
python job\calibrate_cams.py research_inputs\clean_hourly_all_stations.csv
```
(Use the real path of your research project's `data/processed/clean_hourly_all_stations.csv`.) It prints, for each station, the error of
the estimate on data it was not fitted on (`mae_corrected`, `category_accuracy`). Write those numbers in your report. Then commit and
push `backend/data/calibration.json` (GitHub Desktop: write a summary, **Commit**, **Push**). Render redeploys by itself.

## Step 7. The Android app

1. Copy `google-services.json` (from Firebase) into `android/app/` (next to `build.gradle.kts`). Without it the app still works, but there are no notifications.
2. Android Studio → **File → Open** → choose the `android` folder (not the whole repo) → **Trust project**. The first sync downloads
   libraries (10 to 20 minutes; keep the internet on).
3. If Android Studio offers to upgrade the Android Gradle Plugin, you can accept. If it asks for a JDK, choose its bundled JDK (17 or newer).
4. Open `android/app/build.gradle.kts` and change `DEFAULT_SERVER` to your Render address (keep the `/` at the end). You can also change
   the address later inside the app: **Me → Server address**.
5. Plug in your phone (USB debugging on) → choose it at the top → green ▶ **Run**.
6. Check: the app opens with the language screen → Sathi → "Try without an account". Home shows Silk Board in Demo mode.
   Turn Demo mode off in **Me** to see live data.

**Make the APK to share:** Android Studio → **Build → Build App Bundle(s) / APK(s) → Build APK(s)** → click **locate** in the message.
The file is `android/app/build/outputs/apk/debug/app-debug.apk`. Send it by WhatsApp or Drive; on the other phone allow "Install unknown apps".

**Testing the app against the backend on your laptop:** run `uvicorn airsathi.main:app --host 0.0.0.0 --port 8000`, find your
laptop's Wi-Fi address (`ipconfig` → IPv4, e.g. 192.168.1.5), and in the app set Me → Server address to `http://192.168.1.5:8000/`.
Phone and laptop must be on the same Wi-Fi. (The Android emulator uses `http://10.0.2.2:8000/`.)

## Step 8. Make yourself admin and test alerts

1. Create your account in the app with the e-mail you put in `ADMIN_EMAILS`. (The very first account is also admin.)
2. Open the website → **Log in** → the **Admin dashboard** appears: users, phones, data source per station, alerts, job runs.
3. To test a notification: in the app, add yourself a health condition (e.g. asthma) and lower your alert level to 51 (Me → Edit).
   At the next hourly run, if the forecast in the next 12 h reaches 51, the phone gets an alert (not between 10 pm and 7 am; max one per 12 h).

---

## Features (for the report)

| Area | Features |
| --- | --- |
| For all ages | English, Kannada, Hindi · big-text elder mode · read-aloud (phone voice) · Sathi mascot whose face and colour follow the category · colour is never the only signal (number + word too) |
| Forecast | Now + 1, 6, 12, 24 h with an 80 % likely range and a confidence label · "How accurate is this?" with the test results |
| Personal advice | Per family member: age, asthma/lung, heart, pregnancy, outdoor work, exercise; every sentence shows its source [1] [3] [4] [5] |
| Alerts | Push notification when the forecast reaches the person's level (101 vulnerable, 201 healthy; can only be lowered) · quiet hours · 12 h cooldown |
| Plan | OpenStreetMap with coloured station pins · best 1 to 3 h window today/tomorrow for a walk, school run, exercise or outdoor work |
| Health | Symptom diary saved with the AQI at that time, with a summary · 7-day chart · disclaimer and sources |
| Engagement | Daily green tip · badges and streaks |
| Standard app parts | Sign-up, log-in, forgot password (e-mail code), guest mode, settings, dark theme, privacy notice, delete account, offline last-saved data, home-screen widget, data-status page, admin dashboard |
| Honesty | Data source and age always visible · CAMS estimates labelled "not official CPCB AQI" · Demo mode labelled on every screen |

## Data and licences
Station data: KSPCB via OpenAQ (CC BY 4.0). Model data: Copernicus CAMS via Open-Meteo (free for non-commercial use, attribution).
Map: OpenStreetMap contributors. Health sources: see `docs/health_advisory_reference.md`. Kannada and Hindi texts are draft
translations; have a native speaker check them. Not medical advice.

## Troubleshooting
| Problem | Fix |
| --- | --- |
| App says "Could not reach the AirSathi server" | The Render server is waking up: wait a minute and pull Refresh. Check Me → Server address ends with `/` |
| Android Studio: "SDK location not found" | File → Project Structure → SDK Location → pick the Android SDK (Studio shows the default path) |
| Android Studio: Gradle sync failed with a version message | Accept the AGP Upgrade Assistant suggestion, then Sync again |
| GitHub Action red cross | Click it and read the last lines. Usually a secret is missing or has a space at the end |
| Live mode shows "No data available" | The hourly job has not run yet (Step 5) |
| No notifications | `google-services.json` in `android/app/`, `FCM_SERVICE_ACCOUNT` secret set, phone allowed notifications, logged in |
