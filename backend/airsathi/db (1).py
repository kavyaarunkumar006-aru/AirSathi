"""Tiny database layer: SQLite on your laptop, PostgreSQL (Neon) in the cloud.

Set DATABASE_URL to a postgres:// URL to use PostgreSQL; otherwise a local file backend/data/airsathi.db is used.
All SQL in this project is written with '?' placeholders; for PostgreSQL they are converted to '%s'.
"""
import os
import re
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

DB_URL = os.environ.get("DATABASE_URL", "")
IS_PG = DB_URL.startswith("postgres")
SQLITE_PATH = Path(os.environ.get("SQLITE_PATH", Path(__file__).resolve().parents[1] / "data" / "airsathi.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id {serial}, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, pw_hash TEXT NOT NULL,
  is_admin INTEGER NOT NULL DEFAULT 0, lang TEXT NOT NULL DEFAULT 'en', created_at TEXT NOT NULL,
  reset_code TEXT, reset_expires TEXT);
CREATE TABLE IF NOT EXISTS members (
  id {serial}, user_id INTEGER NOT NULL, name TEXT NOT NULL, age INTEGER, conditions TEXT NOT NULL DEFAULT '[]',
  station TEXT NOT NULL DEFAULT 'silkboard', alert_threshold INTEGER, is_self INTEGER NOT NULL DEFAULT 0,
  alerts_on INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS diary (
  id {serial}, user_id INTEGER NOT NULL, member_id INTEGER NOT NULL, ts TEXT NOT NULL, symptoms TEXT NOT NULL,
  note TEXT, station TEXT, aqi INTEGER);
CREATE TABLE IF NOT EXISTS devices (
  id {serial}, user_id INTEGER NOT NULL, token TEXT UNIQUE NOT NULL, platform TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS visits (user_id INTEGER NOT NULL, day TEXT NOT NULL, PRIMARY KEY (user_id, day));
CREATE TABLE IF NOT EXISTS station_now (
  station TEXT PRIMARY KEY, ts TEXT, aqi INTEGER, dominant TEXT, tier TEXT NOT NULL, label TEXT NOT NULL,
  data_age_h REAL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS forecasts (
  station TEXT NOT NULL, horizon INTEGER NOT NULL, origin TEXT NOT NULL, target TEXT NOT NULL, aqi INTEGER,
  lo INTEGER, hi INTEGER, method TEXT NOT NULL, PRIMARY KEY (station, horizon));
CREATE TABLE IF NOT EXISTS hourly (
  station TEXT NOT NULL, ts TEXT NOT NULL, source TEXT NOT NULL, pm25 REAL, pm10 REAL, no2 REAL, so2 REAL,
  o3 REAL, co REAL, aqi INTEGER, PRIMARY KEY (station, ts, source));
CREATE TABLE IF NOT EXISTS alerts_sent (
  id {serial}, member_id INTEGER NOT NULL, station TEXT NOT NULL, sent_at TEXT NOT NULL, level TEXT NOT NULL,
  aqi INTEGER, target TEXT, result TEXT);
CREATE TABLE IF NOT EXISTS job_runs (
  id {serial}, started TEXT NOT NULL, finished TEXT, status TEXT, message TEXT);
"""


def _connect():
    if IS_PG:
        import psycopg  # installed from requirements.txt in the cloud
        return psycopg.connect(DB_URL, autocommit=False)
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(SQLITE_PATH)
    con.row_factory = sqlite3.Row
    return con


def _sql(q):
    return q.replace("?", "%s") if IS_PG else q


_local = threading.local()      # one PostgreSQL connection per server thread, reused (opening one to Neon takes ~0.3 s)


def _pg_conn():
    c = getattr(_local, "pg", None)
    if c is None or getattr(c, "closed", False):
        c = _connect()
        _local.pg = c
    return c


@contextmanager
def conn():
    if IS_PG:
        c = _pg_conn()
        try:
            yield c
            c.commit()
        except Exception:
            try:
                c.rollback()
            except Exception:
                pass
            if getattr(c, "closed", False) or getattr(c, "broken", False):
                _local.pg = None                   # connection lost (e.g. Neon went to sleep): reconnect next time
            raise
        return
    c = _connect()
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def _rows(cur):
    if IS_PG:
        cols = [d.name for d in cur.description] if cur.description else []
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    return [dict(r) for r in cur.fetchall()]


def _retry(fn):
    """Run fn(); if a reused PostgreSQL connection has dropped, reconnect and try once more."""
    try:
        return fn()
    except Exception as e:
        if IS_PG and type(e).__name__ in ("OperationalError", "InterfaceError"):
            _local.pg = None
            return fn()
        raise


def query(q, params=()):
    def run():
        with conn() as c:
            cur = c.cursor()
            cur.execute(_sql(q), params)
            return _rows(cur)
    return _retry(run)


def one(q, params=()):
    r = query(q, params)
    return r[0] if r else None


ID_TABLES = {"users", "members", "diary", "devices", "alerts_sent", "job_runs"}    # tables that have an 'id' column


def execute(q, params=()):
    """Run an INSERT/UPDATE/DELETE. For INSERTs into a table with an 'id' column, returns the new row id."""
    m = re.match(r"\s*INSERT\s+INTO\s+(\w+)", q, re.IGNORECASE)

    def run():
        with conn() as c:
            cur = c.cursor()
            if IS_PG and m and m.group(1).lower() in ID_TABLES and "RETURNING" not in q.upper() and "ON CONFLICT" not in q.upper():
                cur.execute(_sql(q) + " RETURNING id", params)
                return cur.fetchone()[0]
            cur.execute(_sql(q), params)
            return getattr(cur, "lastrowid", None)
    return _retry(run)


def executemany(q, rows):
    def run():
        with conn() as c:
            c.cursor().executemany(_sql(q), rows)
    return _retry(run)


def upsert(table, keys, row):
    """Insert or replace one row. keys = primary-key column names."""
    cols = list(row)
    ph = ",".join("?" * len(cols))
    upd = ",".join(f"{c}=excluded.{c}" for c in cols if c not in keys)
    q = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({ph}) ON CONFLICT ({','.join(keys)}) DO UPDATE SET {upd}"
    execute(q, tuple(row[c] for c in cols))


def init():
    serial = "SERIAL PRIMARY KEY" if IS_PG else "INTEGER PRIMARY KEY AUTOINCREMENT"
    with conn() as c:
        cur = c.cursor()
        for stmt in SCHEMA.format(serial=serial).split(";"):
            if stmt.strip():
                cur.execute(stmt)
