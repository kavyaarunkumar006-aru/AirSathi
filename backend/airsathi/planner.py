"""'Best time to go out' planner.

The CPCB AQI is a 24-hour average, so it cannot say which HOUR is cleaner. The planner therefore uses hourly PM2.5 and PM10
concentrations (as in docs/health_advisory_reference.md, section 7):
- forecast mode: hourly concentrations forecast for the next 36 h (CAMS model, bias-corrected), when available;
- typical mode: the station's usual time-of-day pattern = median hourly PM per hour of day over the last 28 days.
Only daytime hours (6 am to 9 pm) are suggested. A window is shown only if it is clearly better (>= 20 % lower) than the worst one.
Very Poor / Severe: 'Limit outdoor activity at all times' (NCDC [3]).
"""
import datetime as dt
import statistics

from .aqi import subindex

ACTIVITIES = {"walk": 1, "school_run": 1, "exercise": 2, "outdoor_work": 3}
DAY_FROM, DAY_TO = 6, 21            # first and last hour a window may start/end


def _score(pm25, pm10):
    """Hourly 'dirtiness' on the AQI scale (sub-index of the hourly concentration; NOT an official AQI)."""
    s = [v for v in (subindex(pm25, "pm25"), subindex(pm10, "pm10")) if v is not None]
    return max(s) if s else None


def _blocks(scores, length):
    """scores: list of (datetime, score). Returns [(start, end, mean)] for complete daytime blocks."""
    out = []
    for i in range(len(scores) - length + 1):
        chunk = scores[i:i + length]
        start = chunk[0][0]
        if start.hour < DAY_FROM or start.hour + length > DAY_TO + 1:
            continue
        if any(s is None for _, s in chunk) or (chunk[-1][0] - start) != dt.timedelta(hours=length - 1):
            continue
        out.append((start, start + dt.timedelta(hours=length), sum(s for _, s in chunk) / length))
    return out


def typical_pattern(history):
    """history: list of (datetime, pm25, pm10) for the last 28 days. Returns {hour: median score} for hours with >= 20 days of data."""
    by_hour = {}
    for ts, a, b in history:
        s = _score(a, b)
        if s is not None:
            by_hour.setdefault(ts.hour, []).append(s)
    return {h: statistics.median(v) for h, v in by_hour.items() if len(v) >= 20}


def plan(now, activity="walk", future=None, history=None, current_category_index=0):
    """now: datetime (local IST). future: [(datetime, pm25, pm10)] next hours, or None. history: past 28 days.
    Returns {mode, activity, windows[], worst, message_id}."""
    length = ACTIVITIES.get(activity, 1)
    if current_category_index >= 4:
        return {"mode": "rule", "activity": activity, "windows": [], "message_id": "limit_all_day"}
    if future:
        scores = [(ts, _score(a, b)) for ts, a, b in future if ts > now][:36]
        blocks = _blocks(scores, length)
        mode = "forecast"
    else:
        pat = typical_pattern(history or [])
        scores = []
        for k in range(1, 37):
            ts = (now + dt.timedelta(hours=k)).replace(minute=0, second=0, microsecond=0)
            scores.append((ts, pat.get(ts.hour)))
        blocks = _blocks(scores, length)
        mode = "typical"
    if not blocks:
        return {"mode": mode, "activity": activity, "windows": [], "message_id": "no_data"}
    best = sorted(blocks, key=lambda b: b[2])
    worst = best[-1]
    if best[0][2] > 0.8 * worst[2]:
        return {"mode": mode, "activity": activity, "windows": [], "message_id": "no_clear_time",
                "worst": _fmt(worst)}
    picked = []
    for b in best:                               # up to 3 non-overlapping windows, cleanest first
        if all(b[1] <= p[0] or b[0] >= p[1] for p in picked):
            picked.append(b)
        if len(picked) == 3:
            break
    return {"mode": mode, "activity": activity, "windows": [_fmt(b) for b in sorted(picked)], "worst": _fmt(worst),
            "message_id": "best_times"}


def _fmt(b):
    return {"start": b[0].isoformat(), "end": b[1].isoformat(), "level": round(b[2])}
