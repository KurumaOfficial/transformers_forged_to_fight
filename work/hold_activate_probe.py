"""Catch the battle state while /matches/activate-match is held open."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "server" / "requests.jsonl"
FLAG = ROOT / "work" / "hold_activate.flag"
ADB = ROOT / "work" / "platform-tools" / "adb.exe"
SMOKE = ROOT / "work" / "smoke_test.py"
OUT = ROOT / "work" / "hold_activate_scan.txt"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def lines():
    try:
        return REQ.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return []


base = len(lines())
FLAG.write_text("hold", encoding="utf-8")
print("starting smoke; hold flag set", flush=True)
p = subprocess.Popen([sys.executable, str(SMOKE), "--plus", "--fight", "--no-memory"],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
found = None
deadline = time.time() + 300
while time.time() < deadline:
    rows = lines()[base:]
    for r in rows:
        if "activate-match" in r:
            found = r
            break
    if found or p.poll() is not None:
        break
    time.sleep(0.5)
print("activate found", bool(found), flush=True)
if found:
    print(found[:300], flush=True)
    with OUT.open("w", encoding="utf-8") as f:
        f.write("ACTIVATE REQUEST\n" + found + "\n\n")
        for script in ("scan_playerattrs.py", "probe_fightdata.py", "dump_fightflow.py"):
            f.write(f"\n===== {script} =====\n")
            f.flush()
            r = subprocess.run([sys.executable, str(ROOT / "work" / script)],
                               capture_output=True, text=True, timeout=600)
            f.write(r.stdout)
            f.write(r.stderr)
            f.flush()
    print("scan written", OUT, flush=True)
# release
FLAG.unlink(missing_ok=True)
try:
    out, _ = p.communicate(timeout=420)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()
(ROOT / "work" / "hold_smoke.txt").write_text(out or "", encoding="utf-8")
logcat = subprocess.run([str(ADB), "logcat", "-d", "-v", "time", "-s", "Unity:V"],
                        capture_output=True, text=True, timeout=120).stdout
(ROOT / "work" / "hold_logcat.txt").write_text(logcat, encoding="utf-8")
print("smoke tail", (out or "")[-400:], flush=True)
print("nre", "ArgumentNullException" in logcat, flush=True)
