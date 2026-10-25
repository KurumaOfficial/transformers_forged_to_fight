"""SQLite persistence for the TFTF stub (T2).

The default server still reads JSON payloads from server/data. This module is
opt-in: set TFTF_DB=<path> to enable mutable player state. It is deliberately
small and migration-friendly; the wire protocol is unchanged.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS account (
  uid TEXT PRIMARY KEY,
  name TEXT,
  level INTEGER DEFAULT 0,
  xp INTEGER DEFAULT 0,
  stoken TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS wallet (
  uid TEXT PRIMARY KEY,
  gold INTEGER DEFAULT 0,
  energon INTEGER DEFAULT 0,
  crystals INTEGER DEFAULT 0,
  arena_chips INTEGER DEFAULT 0,
  shanix INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS roster (
  uid TEXT NOT NULL,
  bid TEXT NOT NULL,
  rank INTEGER DEFAULT 1,
  level INTEGER DEFAULT 1,
  sig_lvl INTEGER DEFAULT 0,
  xp INTEGER DEFAULT 0,
  stamina INTEGER DEFAULT 0,
  stamina_ts INTEGER DEFAULT 0,
  pvpb TEXT DEFAULT '{}',
  forge_level INTEGER DEFAULT 0,
  PRIMARY KEY (uid, bid)
);
CREATE TABLE IF NOT EXISTS active_team (
  uid TEXT NOT NULL,
  activity_id TEXT NOT NULL,
  type TEXT,
  modes TEXT DEFAULT '[]',
  expire INTEGER DEFAULT 0,
  heroes_json TEXT DEFAULT '{}',
  PRIMARY KEY (uid, activity_id)
);
CREATE TABLE IF NOT EXISTS quest_run (
  uid TEXT NOT NULL,
  qid TEXT NOT NULL,
  run_id TEXT NOT NULL,
  mode TEXT,
  phase TEXT,
  start_time INTEGER DEFAULT 0,
  expiry INTEGER DEFAULT 0,
  team_json TEXT DEFAULT '{}',
  state_json TEXT DEFAULT '{}',
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (uid, qid, run_id)
);
CREATE TABLE IF NOT EXISTS reward_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT NOT NULL,
  source TEXT NOT NULL,
  source_id TEXT,
  payload_json TEXT DEFAULT '{}',
  applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS match (
  uid TEXT NOT NULL,
  match_id TEXT NOT NULL,
  match_type TEXT,
  qid TEXT,
  fighter_init_json TEXT DEFAULT '{}',
  state TEXT,
  result_json TEXT DEFAULT '{}',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  resolved_at TEXT,
  PRIMARY KEY (uid, match_id)
);
"""


def db_path() -> Path | None:
    raw = os.environ.get("TFTF_DB", "").strip()
    return Path(raw) if raw else None


@contextmanager
def connect(path: str | Path | None = None):
    p = Path(path) if path else db_path()
    if not p:
        raise RuntimeError("TFTF_DB is not set and no path was supplied")
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db(path: str | Path | None = None) -> None:
    with connect(path) as con:
        con.executescript(SCHEMA)
        con.execute(
            "INSERT INTO schema_meta(key,value) VALUES('schema_version',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(SCHEMA_VERSION),),
        )


def _j(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def upsert_account(uid: str, name: str = "", level: int = 0, xp: int = 0,
                   stoken: str = "", path=None) -> None:
    with connect(path) as con:
        con.execute(
            "INSERT INTO account(uid,name,level,xp,stoken) VALUES(?,?,?,?,?) "
            "ON CONFLICT(uid) DO UPDATE SET name=excluded.name, level=excluded.level, "
            "xp=excluded.xp, stoken=excluded.stoken",
            (uid, name, level, xp, stoken),
        )
        con.execute("INSERT OR IGNORE INTO wallet(uid) VALUES(?)", (uid,))


def get_account(uid: str, path=None) -> dict | None:
    with connect(path) as con:
        row = con.execute("SELECT * FROM account WHERE uid=?", (uid,)).fetchone()
        return dict(row) if row else None


def upsert_roster(uid: str, bid: str, rank: int = 1, level: int = 1,
                  sig_lvl: int = 0, xp: int = 0, stamina: int = 0,
                  stamina_ts: int = 0, pvpb=None, forge_level: int = 0, path=None) -> None:
    with connect(path) as con:
        con.execute(
            "INSERT INTO roster(uid,bid,rank,level,sig_lvl,xp,stamina,stamina_ts,pvpb,forge_level) "
            "VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(uid,bid) DO UPDATE SET "
            "rank=excluded.rank, level=excluded.level, sig_lvl=excluded.sig_lvl, "
            "xp=excluded.xp, stamina=excluded.stamina, stamina_ts=excluded.stamina_ts, "
            "pvpb=excluded.pvpb, forge_level=excluded.forge_level",
            (uid, bid, rank, level, sig_lvl, xp, stamina, stamina_ts, _j(pvpb or {}), forge_level),
        )


def get_roster(uid: str, path=None) -> list[dict]:
    with connect(path) as con:
        return [dict(r) for r in con.execute("SELECT * FROM roster WHERE uid=? ORDER BY bid", (uid,))]


def save_quest_run(uid: str, qid: str, run_id: str, mode: str = "", phase: str = "",
                   start_time: int = 0, expiry: int = 0, team=None, state=None, path=None) -> None:
    with connect(path) as con:
        con.execute(
            "INSERT INTO quest_run(uid,qid,run_id,mode,phase,start_time,expiry,team_json,state_json,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(uid,qid,run_id) DO UPDATE SET "
            "mode=excluded.mode, phase=excluded.phase, start_time=excluded.start_time, "
            "expiry=excluded.expiry, team_json=excluded.team_json, state_json=excluded.state_json, "
            "updated_at=CURRENT_TIMESTAMP",
            (uid, qid, run_id, mode, phase, start_time, expiry, _j(team or {}), _j(state or {})),
        )


def get_quest_run(uid: str, qid: str, run_id: str, path=None) -> dict | None:
    with connect(path) as con:
        row = con.execute(
            "SELECT * FROM quest_run WHERE uid=? AND qid=? AND run_id=?", (uid, qid, run_id)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["team"] = json.loads(d.pop("team_json") or "{}")
        d["state"] = json.loads(d.pop("state_json") or "{}")
        return d


def add_reward(uid: str, source: str, source_id: str = "", payload=None, path=None) -> int:
    with connect(path) as con:
        cur = con.execute(
            "INSERT INTO reward_ledger(uid,source,source_id,payload_json) VALUES(?,?,?,?)",
            (uid, source, source_id, _j(payload or {})),
        )
        return int(cur.lastrowid)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="SQLite file path")
    ap.add_argument("--init", action="store_true")
    args = ap.parse_args()
    if args.init:
        init_db(args.path)
        print("initialized", args.path, "schema", SCHEMA_VERSION)
    else:
        print("use --init")


if __name__ == "__main__":
    main()
