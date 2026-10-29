"""Force-stop/start the game and reach the home base (BOTS-friendly)."""
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
PKG = "com.kabam.bigrobot"
ACT = "com.kabam.bigrobot/com.explodingbarrel.Activity"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(*args, timeout=120):
    return subprocess.run([ADB, *args], capture_output=True, timeout=timeout, text=True)


def shot():
    p = ROOT / "work" / "_reset_home.png"
    adb("shell", "screencap", "-p", "/sdcard/_reset_home.png")
    adb("pull", "/sdcard/_reset_home.png", str(p))
    return p


def green_button():
    try:
        im = Image.open(shot()).convert("RGB")
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


def main():
    adb("shell", "am", "force-stop", PKG)
    time.sleep(2)
    adb("shell", "am", "start", "-n", ACT)
    deadline = time.time() + 120
    tapped = False
    last_nudge = 0.0
    while time.time() < deadline:
        pos = green_button()
        if pos:
            adb("shell", "input", "tap", str(pos[0]), str(pos[1]))
            tapped = True
            break
        if time.time() - last_nudge > 12:
            adb("shell", "input", "keyevent", "4")
            last_nudge = time.time()
        time.sleep(3)
    if not tapped:
        print("title button not found")
        return 1
    time.sleep(15)
    adb("shell", "input", "tap", "456", "160")  # BOTS
    time.sleep(4)
    print("home reached")
    return 0


if __name__ == "__main__":
    sys.exit(main())
