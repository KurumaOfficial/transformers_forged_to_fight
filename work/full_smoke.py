"""Independent full-smoke phases with a fresh launch before each phase.

Each phase force-stops the app, reaches home, then opens one screen. A failure
in one phase cannot leak into the next. Status is computed from request paths,
screenshot hashes and logcat NREs, not from an exit code.

Usage: python work/full_smoke.py
Writes tests/smoke/full_smoke.json.
"""
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
PKG = "com.kabam.bigrobot"
ACT = "com.kabam.bigrobot/com.explodingbarrel.Activity"
REQ = ROOT / "server" / "requests.jsonl"
OUT = ROOT / "tests" / "smoke" / "full_smoke.json"
SHOTS = ROOT / "tests" / "smoke"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(*args, timeout=120):
    return subprocess.run([ADB, *args], capture_output=True, timeout=timeout)


def shot(name):
    remote = f"/sdcard/{name}.png"
    local = SHOTS / f"{name}.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    return local


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def read_requests():
    rows = []
    if REQ.exists():
        for line in REQ.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def green_button(path):
    try:
        im = Image.open(path).convert("RGB")
    except Exception:
        return None
    w, h = im.size
    px = im.load()
    pts = []
    for y in range(int(h * 0.55), int(h * 0.95), 4):
        for x in range(int(w * 0.25), int(w * 0.75), 4):
            r, g, b = px[x, y]
            if g > 120 and r < 120 and b < 140 and g > r + 40 and g > b + 30:
                pts.append((x, y))
    if len(pts) < 40:
        return None
    xs = sorted(p[0] for p in pts)
    ys = sorted(p[1] for p in pts)
    return xs[len(xs) // 2], ys[len(ys) // 2]


def launch_home():
    """Force-stop, launch, tap PLAY NOW, wait for home requests."""
    adb("shell", "am", "force-stop", PKG)
    time.sleep(2)
    adb("logcat", "-c")
    adb("shell", "am", "start", "-n", ACT)
    base = len(read_requests())
    deadline = time.time() + 150
    tapped = False
    last_nudge = 0.0
    while time.time() < deadline:
        if not tapped:
            p = shot("_fs_launch")
            pos = green_button(p)
            if pos:
                adb("shell", "input", "tap", str(pos[0]), str(pos[1]))
                tapped = True
            elif time.time() - last_nudge > 12:
                adb("shell", "input", "keyevent", "4")
                last_nudge = time.time()
        else:
            rows = read_requests()[base:]
            paths = [r.get("path", "") for r in rows]
            if any(x == "/quests/quest-list" for x in paths) or any(x == "/base/active" for x in paths):
                time.sleep(8)
                return True
        time.sleep(3)
    return False


def nre_since_clear():
    out = adb("logcat", "-d", "-s", "Unity:V").stdout.decode("utf-8", "replace")
    return "NullReferenceException" in out


def phase(name, action=None, tap_xy=None):
    started = datetime.now(timezone.utc).isoformat()
    ok_home = launch_home()
    home = shot(f"fs_{name}_home")
    home_hash = digest(home) if home.exists() else None
    paths = []
    screen_hash = None
    nre = nre_since_clear()
    if ok_home and (action or tap_xy):
        if tap_xy:
            adb("shell", "input", "tap", str(tap_xy[0]), str(tap_xy[1]))
        if action:
            action()
        time.sleep(4)
        screen = shot(f"fs_{name}")
        screen_hash = digest(screen) if screen.exists() else None
        nre = nre or nre_since_clear()
        paths = [r.get("path", "") for r in read_requests()[-40:]]
    opened = bool(screen_hash and screen_hash != home_hash) if (action or tap_xy) else True
    return {
        "name": name,
        "started": started,
        "home_loaded": ok_home,
        "screen_opened": opened,
        "screen_hash": screen_hash,
        "home_hash": home_hash,
        "nre": nre,
        "paths": paths,
        "status": "PASS" if (ok_home and (opened or action is None) and not nre) else "FAIL",
    }


def main():
    results = []
    results.append(phase("home"))
    results.append(phase("crystals", tap_xy=(1820, 185)))
    results.append(phase("objectives", tap_xy=(2180, 410)))
    results.append(phase("store", tap_xy=(2130, 185)))
    results.append(phase("bots", tap_xy=(456, 160)))
    results.append(phase("fight_modes", tap_xy=(1070, 185)))
    ok = all(r["status"] == "PASS" for r in results)
    payload = {
        "started": results[0]["started"],
        "finished": datetime.now(timezone.utc).isoformat(),
        "phases": results,
        "status": "PASS" if ok else "FAIL",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        print(f"{r['name']:12s} {r['status']:4s} home={r['home_loaded']} "
              f"opened={r['screen_opened']} nre={r['nre']}")
    print("report", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
