"""Live persistence check: start server with TFTF_DB, write, kill, restart, read."""
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "work" / "persist_live.db"
LOG = ROOT / "work" / "persist_live.log"
URL = "http://127.0.0.1:8099"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def start():
    env = dict(os.environ, TFTF_DB=str(DB), PYTHONIOENCODING="utf-8")
    p = subprocess.Popen([sys.executable, str(ROOT / "server" / "stub_server.py"), "8099"],
                         cwd=str(ROOT), env=env,
                         stdout=open(LOG, "a", encoding="utf-8"),
                         stderr=subprocess.STDOUT)
    time.sleep(2)
    return p


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(URL + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def rows():
    con = sqlite3.connect(DB)
    try:
        out = {}
        for table in ("quest_run", "account", "roster", "wallet", "schema_meta"):
            try:
                out[table] = con.execute(f"SELECT * FROM {table}").fetchall()
            except sqlite3.Error as exc:
                out[table] = f"error: {exc}"
        return out
    finally:
        con.close()


DB.unlink(missing_ok=True)
LOG.write_text("", encoding="utf-8")
p = start()
try:
    r1 = post("/quests/quest-begin/story_act1_ch1_m1",
              {"tm0": "bumblebee_cin_dotm_2", "api": 11, "nonce": "persist1"})
    print("first response keys", sorted(r1.keys()))
    before = rows()
    print("before counts", {k: (len(v) if isinstance(v, list) else v) for k, v in before.items()})
finally:
    p.terminate()
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()
time.sleep(1)
mid = rows()
print("after kill", {k: (len(v) if isinstance(v, list) else v) for k, v in mid.items()})
p = start()
try:
    r2 = post("/quests/quest-begin/story_act1_ch1_m1",
              {"tm0": "bumblebee_cin_dotm_2", "api": 11, "nonce": "persist2"})
    print("second response keys", sorted(r2.keys()))
    after = rows()
    print("after restart", {k: (len(v) if isinstance(v, list) else v) for k, v in after.items()})
finally:
    p.terminate()
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()
print("db bytes", DB.stat().st_size if DB.exists() else None)
