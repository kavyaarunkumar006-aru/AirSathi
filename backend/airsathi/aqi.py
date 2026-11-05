"""CPCB National AQI in plain Python (no numpy), used by the API and the hourly job.

Same breakpoints as model/aq_clean.py (CPCB NAQI 2014). The top band is given a finite upper limit so the
index can rise above 400 (capped at 500), exactly as in the research code.
"""
import math

BREAKPOINTS = {
    "pm25": [(0, 30, 0, 50), (30, 60, 50, 100), (60, 90, 100, 200), (90, 120, 200, 300), (120, 250, 300, 400), (250, 380, 400, 500)],
    "pm10": [(0, 50, 0, 50), (50, 100, 50, 100), (100, 250, 100, 200), (250, 350, 200, 300), (350, 430, 300, 400), (430, 510, 400, 500)],
    "no2": [(0, 40, 0, 50), (40, 80, 50, 100), (80, 180, 100, 200), (180, 280, 200, 300), (280, 400, 300, 400), (400, 520, 400, 500)],
    "so2": [(0, 40, 0, 50), (40, 80, 50, 100), (80, 380, 100, 200), (380, 800, 200, 300), (800, 1600, 300, 400), (1600, 2400, 400, 500)],
    "o3": [(0, 50, 0, 50), (50, 100, 50, 100), (100, 168, 100, 200), (168, 208, 200, 300), (208, 748, 300, 400), (748, 1000, 400, 500)],
    "co": [(0, 1.0, 0, 50), (1.0, 2.0, 50, 100), (2.0, 10.0, 100, 200), (10.0, 17.0, 200, 300), (17.0, 34.0, 300, 400), (34.0, 51.0, 400, 500)],
}
POLLUTANTS = list(BREAKPOINTS)
WINDOW = {"pm25": 24, "pm10": 24, "no2": 24, "so2": 24, "o3": 8, "co": 8}      # CPCB averaging hours
MIN_VALID = {24: 16, 8: 6}                                                     # CPCB completeness rule

# (upper AQI, key, English name, official CPCB colour)
CATEGORIES = [
    (50, "good", "Good", "#009865"),
    (100, "satisfactory", "Satisfactory", "#A3C853"),
    (200, "moderate", "Moderate", "#FFF833"),
    (300, "poor", "Poor", "#F29C33"),
    (400, "very_poor", "Very Poor", "#E93F33"),
    (math.inf, "severe", "Severe", "#AF2D24"),
]
POLLUTANT_NAMES = {"pm25": "PM2.5", "pm10": "PM10", "no2": "NO2", "so2": "SO2", "o3": "Ozone", "co": "CO"}


def _ok(x):
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def subindex(conc, pollutant):
    if not _ok(conc) or conc < 0:
        return None
    bands = BREAKPOINTS[pollutant]
    for blo, bhi, ilo, ihi in bands:
        if blo <= conc <= bhi:
            return ilo + (ihi - ilo) / (bhi - blo) * (conc - blo)
    return 500.0


def category(aqi):
    """Return a dict {key, name, color, index} for an AQI value, or None."""
    if not _ok(aqi):
        return None
    for i, (hi, key, name, color) in enumerate(CATEGORIES):
        if aqi <= hi:
            return {"key": key, "name": name, "color": color, "index": i}
    return None


def aqi_from_averages(avgs):
    """avgs: {pollutant: averaged concentration or None}. Returns (aqi, dominant, subindices).
    CPCB validity: at least 3 pollutants and at least one of PM2.5 / PM10. Otherwise aqi is None."""
    si = {p: subindex(avgs.get(p), p) for p in POLLUTANTS}
    have = {p: v for p, v in si.items() if v is not None}
    if len(have) < 3 or ("pm25" not in have and "pm10" not in have):
        return None, None, si
    dom = max(have, key=have.get)
    return round(have[dom]), dom, si


def running_aqi(hourly):
    """hourly: list of dicts sorted by time, each {pollutant: value or None}. Returns a list of
    (aqi, dominant) for every hour, using CPCB running means (24 h or 8 h, with the 16-of-24 / 6-of-8 rule)."""
    out = []
    for i in range(len(hourly)):
        avgs = {}
        for p in POLLUTANTS:
            w = WINDOW[p]
            vals = [h.get(p) for h in hourly[max(0, i - w + 1): i + 1]]
            vals = [v for v in vals if _ok(v)]
            avgs[p] = sum(vals) / len(vals) if len(vals) >= MIN_VALID[w] else None
        aqi, dom, _ = aqi_from_averages(avgs)
        out.append((aqi, dom))
    return out
