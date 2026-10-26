"""Stop the app shortly after activate-match to catch the failing PlayerAttributes."""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "server" / "requests.jsonl"
ADB = ROOT / "work" / "platform-tools" / "adb.exe"
SMOKE = ROOT / "work" / "smoke_test.py"
OUT = ROOT / "work" / "stop_probe.txt"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(*args, timeout=120):
    return subprocess.run([str(ADB)] + list(args), capture_output=True, timeout=timeout)


def lines():
    try:
        return REQ.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return []


DELAY = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
base = len(lines())
print(f"starting smoke, stop delay {DELAY}s", flush=True)
p = subprocess.Popen([sys.executable, str(SMOKE), "--plus", "--fight", "--no-memory"],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
found = None
deadline = time.time() + 300
while time.time() < deadline:
    for r in lines()[base:]:
        if "activate-match" in r:
            found = r
            break
    if found or p.poll() is not None:
        break
    time.sleep(0.2)
print("activate", bool(found), flush=True)
if found:
    time.sleep(DELAY)
    pid = adb("shell", "pidof", "com.kabam.bigrobot").stdout.decode().strip()
    print("pid", pid, "stop", flush=True)
    adb("shell", f"su 0 kill -STOP {pid}")
    with OUT.open("w", encoding="utf-8") as f:
        f.write(f"activate: {found}\nstop delay: {DELAY}\n\n")
        for script in ("scan_playerattrs.py", "probe_fightdata.py", "dump_fightflow.py"):
            f.write(f"\n===== {script} =====\n")
            f.flush()
            r = subprocess.run([sys.executable, str(ROOT / "work" / script)],
                               capture_output=True, text=True, timeout=600)
            f.write(r.stdout)
            f.write(r.stderr)
            f.flush()
    print("scan done", flush=True)
    adb("shell", f"su 0 kill -CONT {pid}")
try:
    out, _ = p.communicate(timeout=420)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()
(ROOT / "work" / "stop_smoke.txt").write_text(out or "", encoding="utf-8")
logcat = adb("logcat", "-d", "-v", "time", "-s", "Unity:V").stdout.decode("utf-8", "replace")
(ROOT / "work" / "stop_logcat.txt").write_text(logcat, encoding="utf-8")
print("nre", "ArgumentNullException" in logcat, flush=True)
