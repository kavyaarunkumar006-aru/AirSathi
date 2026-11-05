"""Personal health advice for one person (a family member) and an AQI value.

Rules come from docs/health_advisory_reference.md:
- groups: lung, heart, pregnant, outdoor_worker, athlete (ticked), child (age < 14, NCDC [4]), older (age >= 60, a design choice)
- thresholds (design decision from the sources): vulnerable -> advice from 51, alert from 101; healthy adult -> advice from 101,
  alert from 201; everyone -> alert from 301. A user may lower an alert threshold but never raise it above the default.
"""
from .aqi import category
from .messages import t

CONDITIONS = ["lung", "heart", "pregnant", "outdoor_worker", "athlete"]
CHILD_UNDER, OLDER_FROM = 14, 60
VULNERABLE = {"lung", "heart", "pregnant", "child", "older", "outdoor_worker", "athlete"}

TIPS_BY_LEVEL = {   # lowest category index (0 = Good) from which each tip is shown
    "tip_check": 1, "tip_traffic": 1, "tip_fuel": 1, "tip_burn": 1, "tip_smoke": 1,
    "tip_windows": 3, "tip_mop": 3, "tip_coils": 3, "tip_cloth": 3,
    "tip_eyes": 4, "tip_purifier": 4, "tip_ac": 4,
}


def groups_for(age, conditions):
    g = [c for c in CONDITIONS if c in (conditions or [])]
    if age is not None and age < CHILD_UNDER:
        g.append("child")
    if age is not None and age >= OLDER_FROM:
        g.append("older")
    return g


def is_vulnerable(groups):
    return any(g in VULNERABLE for g in groups)


def default_alert_threshold(groups):
    return 101 if is_vulnerable(groups) else 201


def alert_threshold(groups, chosen=None):
    """The user may lower the threshold, never raise it above the default."""
    d = default_alert_threshold(groups)
    return min(int(chosen), d) if chosen else d


def personal_advice(aqi, age=None, conditions=None, lang="en", seed=0):
    """Return {category, headline, actions[], tip, doctor, alert, threshold} for one person."""
    cat = category(aqi)
    if cat is None:
        return None
    k, lvl = cat["key"], cat["index"]          # lvl: 0 Good ... 5 Severe
    groups = groups_for(age, conditions)
    vul = is_vulnerable(groups)
    thr = alert_threshold(groups)
    actions = [t(("vul_" if vul else "gen_") + k, lang)]

    if "lung" in groups or "heart" in groups:
        if lvl in (1, 2, 3):
            actions.append(t("lh_meds", lang))
        if lvl >= 4:
            actions.append(t("lh_symptoms", lang))
    if "child" in groups or "older" in groups or "pregnant" in groups:
        step = {1: "vg_reduce", 2: "vg_avoid_prolonged", 3: "vg_avoid_outdoor"}.get(lvl, "vg_indoors" if lvl >= 4 else None)
        if step:
            actions.append(t(step, lang))
    if "pregnant" in groups and lvl >= 1:
        actions.append(t("preg_risk", lang))
    if "outdoor_worker" in groups and lvl >= 1:
        actions.append(t("work_time", lang))
        if lvl >= 2:
            actions.append(t("work_water", lang))
    if "athlete" in groups and lvl >= 1:
        actions.append(t("ex_poor" if lvl >= 3 else "ex_adapt", lang))
    if lvl >= 4 and "child" in groups:
        actions.append(t("who_child_resp", lang))
    if lvl >= 4 and ("lung" in groups or "heart" in groups):
        actions.append(t("who_lh_resp", lang))

    # remove exact duplicates, keep order
    seen, uniq = set(), []
    for a in actions:
        if a["id"] not in seen:
            seen.add(a["id"])
            uniq.append(a)

    tips = [tid for tid, frm in TIPS_BY_LEVEL.items() if lvl >= frm]
    tip = t(tips[seed % len(tips)], lang) if tips else None
    at_alert = aqi >= thr or aqi >= 301
    return {
        "aqi": round(aqi), "category": cat, "groups": groups, "vulnerable": vul, "threshold": thr,
        "headline": t("impact_" + k, lang), "actions": uniq, "tip": tip,
        "doctor": t("doctor", lang) if at_alert else None, "alert": at_alert,
    }
