"""The 8 KSPCB monitoring stations used by AirSathi (same as the research project)."""

STATIONS = [
    {"id": "silkboard", "name": "Silk Board", "city": "Bengaluru", "openaq_id": 6975, "lat": 12.917348, "lon": 77.622813},
    {"id": "hebbal", "name": "Hebbal", "city": "Bengaluru", "openaq_id": 6984, "lat": 13.029152, "lon": 77.585901},
    {"id": "jayanagar", "name": "Jayanagar 5th Block", "city": "Bengaluru", "openaq_id": 6973, "lat": 12.920984, "lon": 77.584908},
    {"id": "chikkaballapura", "name": "Chikkaballapur Rural", "city": "Chikkaballapur", "openaq_id": 6954, "lat": 13.428828, "lon": 77.731418},
    {"id": "chikkamagaluru", "name": "Kalyana Nagara", "city": "Chikkamagaluru", "openaq_id": 10902, "lat": 13.328028, "lon": 75.797056},
    {"id": "mysuru", "name": "Hebbal 1st Stage", "city": "Mysuru", "openaq_id": 7289, "lat": 12.21041, "lon": 76.37376},
    {"id": "ramanagara", "name": "Vijay Nagar", "city": "Ramanagara", "openaq_id": 10909, "lat": 12.733409, "lon": 77.298051},
    {"id": "madikeri", "name": "Stuart Hill", "city": "Madikeri", "openaq_id": 11582, "lat": 12.415911, "lon": 75.73505},
]
BY_ID = {s["id"]: s for s in STATIONS}


def nearest(lat, lon):
    """Nearest station to a point (simple flat-earth distance is fine at this scale)."""
    import math
    def d(s):
        return (s["lat"] - lat) ** 2 + ((s["lon"] - lon) * math.cos(math.radians(lat))) ** 2
    return min(STATIONS, key=d)
