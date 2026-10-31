"""Navigate to the 1.1 map and step on the battle node an arbitrary number of times.

Usage: python work/experiment_12.py [label] [--no-restart]

Assumes the stub server is already running. Screenshots go to
work/exp12_<label>_*.png; request tail is printed.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(r".")
ADB = ROOT / "work" / "platform-tools" / "adb.exe"
PKG = "com.kabam.bigrobot"
ACT = "com.kabam.bigrobot/com.explodingbarrel.Activity"
REQ = ROOT / "server" / "requests.jsonl"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(*args, timeout=120):
    return subprocess.run([str(a) for a in (ADB,) + args], capture_output=True, text=True, timeout=timeout)


def tap(x, y, wait=1.0):
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def shot(name):
    remote = f"/sdcard/{name}.png"
    local = ROOT / "work" / f"{name}.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    return local


def green_center(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    pts = []
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            r, g, b = px[x, y]
            if g > 135 and r < 115 and b < 140 and g > r + 45 and g > b + 35:
                pts.append((x, y))
    if len(pts) < 40:
        return None
    xs = sorted(p[0] for p in pts)
    ys = sorted(p[1] for p in pts)
    return xs[len(xs) // 2], ys[len(ys) // 2]


def read_reqs():
    if not REQ.exists():
        return []
    rows = []
    for line in REQ.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    restart = "--no-restart" not in sys.argv
    if restart:
        adb("shell", "am", "force-stop", PKG)
        time.sleep(1)
        adb("shell", "am", "start", "-n", ACT)
        time.sleep(30)
        p = shot(f"exp12_{label}_00")
        c = green_center(p)
        if c:
            tap(*c, wait=2)
        time.sleep(25)
    p = shot(f"exp12_{label}_01_home")
    start_idx = len(read_reqs())
    tap(1124, 160, 6)
    shot(f"exp12_{label}_02_fightmode")
    tap(883, 441, 7)
    shot(f"exp12_{label}_03_story")
    tap(1379, 570, 5)
    shot(f"exp12_{label}_04_detail")
    tap(2107, 971, 12)
    shot(f"exp12_{label}_05_map")
    tap(1441, 881, 8)
    shot(f"exp12_{label}_06_after_move")
    rows = read_reqs()[start_idx:]
    print("requests:")
    for r in rows:
        print(" ", r.get("timestamp"), r.get("method"), r.get("path"))
    print("shots:", sorted(str(x) for x in (ROOT / "work").glob(f"exp12_{label}_*.png")))


if __name__ == "__main__":
    main()
