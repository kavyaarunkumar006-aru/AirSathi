"""Passwords and login tokens.

- Passwords are stored as PBKDF2-SHA256 hashes with a random salt (Python standard library), never as plain text.
- After login the app gets a JWT token (valid 30 days) and sends it as  Authorization: Bearer <token>.
"""
import base64
import datetime as dt
import hashlib
import hmac
import os
import secrets

import jwt

SECRET = os.environ.get("JWT_SECRET", "dev-only-change-me")
ITER = 200_000


def hash_password(pw):
    salt = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, ITER)
    return f"pbkdf2${ITER}${base64.b64encode(salt).decode()}${base64.b64encode(h).decode()}"


def check_password(pw, stored):
    try:
        _, it, salt, h = stored.split("$")
        new = hashlib.pbkdf2_hmac("sha256", pw.encode(), base64.b64decode(salt), int(it))
        return hmac.compare_digest(new, base64.b64decode(h))
    except Exception:
        return False


def make_token(user_id, days=30):
    now = dt.datetime.now(dt.timezone.utc)
    return jwt.encode({"sub": str(user_id), "iat": now, "exp": now + dt.timedelta(days=days)}, SECRET, algorithm="HS256")


def read_token(token):
    """Return the user id, or None if the token is missing, wrong or expired."""
    try:
        return int(jwt.decode(token, SECRET, algorithms=["HS256"])["sub"])
    except Exception:
        return None
