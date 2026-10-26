"""Sweep all BOTS pages (12 cards/page) with screenshot-based page change."""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
OUT = ROOT / "tests" / "sweep"
OUT.mkdir(parents=True, exist_ok=True)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
cards = [(row, col, x, y) for row, y in enumerate((450, 900))
         for col, x in enumerate((294, 643, 993, 1342, 1691, 2040))]


def adb(*args, timeout=60):
    return subprocess.run([ADB] + [str(a) for a in args], capture_output=True,
                          text=True, timeout=timeout)


def shot(name):
    remote = f"/sdcard/{name}.png"
    local = OUT / f"{name}.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    return local


def digest(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except Exception:
        return None


def blocker_open():
    p = subprocess.run([sys.executable, str(ROOT / "work" / "dump_odr_blocker.py")],
                       capture_output=True, text=True, timeout=120)
    return "FuseODRBlocker window" in p.stdout and "state 4" in p.stdout


results = []
start_blocked = blocker_open()
print("blocked_by_odr", start_blocked, flush=True)
# Go to BOTS from home; tolerate a blocked screen.
adb("shell", "input", "tap", "456", "160")
time.sleep(4)
page_hash = None
for page in range(5):
    page_shot = shot(f"page_{page:02d}")
    h = digest(page_shot)
    print("page", page, "hash", h, flush=True)
    if page > 0 and h == page_hash:
        print("page did not change; stop", flush=True)
        break
    page_hash = h
    for i, (row, col, x, y) in enumerate(cards):
        idx = page * 12 + i
        if idx >= 59:
            break
        adb("shell", "input", "tap", "456", "160")
        time.sleep(0.8)
        adb("logcat", "-c")
        adb("shell", "input", "tap", str(x), str(y))
        time.sleep(1.5)
        p1 = shot(f"bot_{idx:02d}_popup")
        err1 = p1.stat().st_size < 150000
        adb("shell", "input", "tap", "1140", "671")
        time.sleep(1.5)
        p2 = shot(f"bot_{idx:02d}_info")
        err2 = p2.stat().st_size < 150000
        log = adb("logcat", "-d", "-s", "Unity:V", timeout=30).stdout
        nre = [l for l in log.splitlines() if "NullReferenceException" in l or "Exception:" in l][-3:]
        results.append({"index": idx, "page": page, "row": row, "col": col,
                        "popup_error": err1, "info_error": err2, "nre": nre})
        print(idx, "popup_error", err1, "info_error", err2, "nre", len(nre), flush=True)
        adb("shell", "input", "keyevent", "4")
        time.sleep(0.8)
    # next page: swipe left across the grid
    adb("shell", "input", "swipe", "2000", "540", "250", "540", "300")
    time.sleep(2)

(OUT / "sweep_59.json").write_text(json.dumps({
    "blocked_by_odr": start_blocked,
    "count": len(results),
    "results": results,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", OUT / "sweep_59.json", "count", len(results))
