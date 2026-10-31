"""Find the green PLAY NOW button on the TFTF start screen and tap it.
Uses adb + PIL. No external services. Tested on 2280x1080 landscape.
"""
import os
import subprocess
import sys
import time
from PIL import Image

ADB = os.path.join(os.path.dirname(__file__), "platform-tools", "adb.exe")
TMP = os.path.join(os.path.dirname(__file__), "auto_play.png")


def adb(*args):
    return subprocess.run([ADB, *args], capture_output=True, text=True)


def main():
    adb("shell", "screencap", "-p", "/sdcard/auto_play.png")
    adb("pull", "/sdcard/auto_play.png", TMP)
    im = Image.open(TMP).convert("RGB")
    w, h = im.size
    px = im.load()
    pts = []
    # green button: high G, low R/B
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            r, g, b = px[x, y]
            if g > 140 and r < 110 and b < 130 and g > r + 50 and g > b + 40:
                pts.append((x, y))
    if len(pts) < 50:
        print("PLAY NOW button not found; points=", len(pts))
        return 2
    xs = sorted(p[0] for p in pts)
    ys = sorted(p[1] for p in pts)
    # use median cluster center
    cx = xs[len(xs) // 2]
    cy = ys[len(ys) // 2]
    print(f"tap {cx} {cy} (points={len(pts)})")
    adb("shell", "input", "tap", str(cx), str(cy))
    return 0


if __name__ == "__main__":
    sys.exit(main())
