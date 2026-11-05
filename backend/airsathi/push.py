"""Send Android notifications with Firebase Cloud Messaging (FCM HTTP v1).

Needs FCM_SERVICE_ACCOUNT = the whole JSON text of a Firebase service-account key
(Firebase console -> Project settings -> Service accounts -> Generate new private key). Never commit that file.
"""
import json
import os
import time

import jwt
import requests

_token = {"value": None, "exp": 0}


def _sa():
    raw = os.environ.get("FCM_SERVICE_ACCOUNT")
    return json.loads(raw) if raw else None


def enabled():
    return _sa() is not None


def _access_token(sa):
    if _token["value"] and _token["exp"] > time.time() + 60:
        return _token["value"]
    now = int(time.time())
    assertion = jwt.encode({"iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/firebase.messaging",
                            "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 3600},
                           sa["private_key"], algorithm="RS256")
    r = requests.post("https://oauth2.googleapis.com/token",
                      data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion}, timeout=30)
    r.raise_for_status()
    _token.update(value=r.json()["access_token"], exp=now + 3500)
    return _token["value"]


def send(device_token, title, body, data=None):
    """Returns 'sent', 'invalid_token' (remove it) or 'error:<code>'."""
    sa = _sa()
    if not sa:
        return "disabled"
    msg = {"message": {"token": device_token, "notification": {"title": title, "body": body},
                       "data": {k: str(v) for k, v in (data or {}).items()},
                       "android": {"priority": "high", "notification": {"channel_id": "air_alerts"}}}}
    r = requests.post(f"https://fcm.googleapis.com/v1/projects/{sa['project_id']}/messages:send",
                      headers={"Authorization": f"Bearer {_access_token(sa)}"}, json=msg, timeout=30)
    if r.status_code == 200:
        return "sent"
    if r.status_code in (400, 404) and ("UNREGISTERED" in r.text or "INVALID_ARGUMENT" in r.text):
        return "invalid_token"
    return f"error:{r.status_code}"
