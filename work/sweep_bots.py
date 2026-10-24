"""Sweep the first 12 BOTS cards: popup + INFO, record NRE per bot."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
OUT = ROOT / "tests" / "sweep"
OUT.mkdir(parents=True, exist_ok=True)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(*args, timeout=60):
    return subprocess.run([ADB] + [str(a) for a in args], capture_output=True, text=True, timeout=timeout)


def tap(x, y, wait=1.0):
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def shot(name):
    remote = f"/sdcard/{name}.png"
    local = OUT / f"{name}.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    return local


def log_nre():
    p = adb("logcat", "-d", "-s", "Unity:V", timeout=40)
    lines = [l for l in p.stdout.splitlines() if "NullReferenceException" in l or "Exception:" in l]
    return lines[-3:]


def is_error_screen(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    n = 0
    for y in range(int(h * 0.35), int(h * 0.55), 3):
        for x in range(int(w * 0.30), int(w * 0.70), 3):
            r, g, b = px[x, y]
            if g > 120 and r < 120 and b < 140 and g > r + 35:
                n += 1
    return n > 200


cards = []
for row, y in enumerate((450, 900)):
    for col, x in enumerate((294, 643, 993, 1342, 1691, 2040)):
        cards.append((row, col, x, y))

results = []
tap(456, 160, 4)
for i, (row, col, x, y) in enumerate(cards):
    tap(456, 160, 1)
    adb("logcat", "-c")
    tap(x, y, 2)
    p1 = shot(f"bot_{i:02d}_popup")
    err1 = p1.stat().st_size < 150000
    # INFO button in the popup (centre column, lower button)
    tap(1140, 671, 3)
    p2 = shot(f"bot_{i:02d}_info")
    err2 = p2.stat().st_size < 150000
    nre = log_nre()
    results.append({"index": i, "row": row, "col": col, "popup_error": err1,
                    "info_error": err2, "nre": nre})
    print(i, "popup_error", err1, "info_error", err2, "nre", len(nre))
    # back to BOTS (INFO -> popup or details -> BOTS); tolerate 1-2 screens
    adb("shell", "input", "keyevent", "4")
    time.sleep(1)

(OUT / "sweep_12.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", OUT / "sweep_12.json")
