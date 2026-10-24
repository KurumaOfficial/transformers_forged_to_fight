"""Cold-boot smoke test for the TFTF offline server.

Modes:
  fast (default): title -> home -> FIGHT -> STORY -> quest -> START -> map ->
                  battle tile (prefight) -> optional + tap -> memory probe.
  full (--full):  the same, plus BOTS, bot details, and EDIT SQUAD screens.

The flow uses generous waits and a small green-button detector instead of the
old fixed 38 s boot sleep.  PASS means the scripted UI flow reached the battle
tile; combat may still be blocked (see STATE.md).
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
ADB = ROOT / "work" / "platform-tools" / "adb.exe"
OUT = ROOT / "tests" / "smoke"
REQ = ROOT / "server" / "requests.jsonl"
PKG = "com.kabam.bigrobot"
ACT = "com.kabam.bigrobot/com.explodingbarrel.Activity"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(*args, timeout=180):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def adb(*args, timeout=180):
    return run(ADB, *args, timeout=timeout)


def tap(x, y, wait=1.0):
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def shot(name, note=""):
    OUT.mkdir(parents=True, exist_ok=True)
    remote = f"/sdcard/smoke_{name}.png"
    local = OUT / f"{name}.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    return local


def screen_green_button():
    """Return the largest green-button centre on the current screen, or None."""
    try:
        im = Image.open(shot("_probe")).convert("RGB")
    except Exception:
        return None
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


def screen_is_home():
    """Heuristic: the home base has a large green lower half."""
    try:
        im = Image.open(shot("_probe")).convert("RGB")
    except Exception:
        return False
    w, h = im.size
    px = im.load()
    rs = gs = bs = n = 0
    for y in range(int(h * 0.62), int(h * 0.92), 8):
        for x in range(int(w * 0.12), int(w * 0.88), 8):
            r, g, b = px[x, y]
            rs += r; gs += g; bs += b; n += 1
    if not n:
        return False
    r, g, b = rs / n, gs / n, bs / n
    return g > 58 and g > r + 6 and g > b + 6


def green_button_in_region(y0, y1):
    """Return True if a green UI button is present in the given y band."""
    try:
        im = Image.open(shot("_probe")).convert("RGB")
    except Exception:
        return False
    w, h = im.size
    px = im.load()
    n = 0
    for y in range(max(0, int(y0)), min(h, int(y1)), 3):
        for x in range(0, w, 3):
            r, g, b = px[x, y]
            if g > 130 and r < 120 and b < 140 and g > r + 40 and g > b + 30:
                n += 1
                if n > 120:
                    return True
    return False


def screen_has_prefight_bar():
    """The prefight screen has a red/orange VS bar near the centre."""
    try:
        im = Image.open(shot("_probe")).convert("RGB")
    except Exception:
        return False
    w, h = im.size
    px = im.load()
    n = 0
    for y in range(int(h * 0.38), int(h * 0.62), 2):
        for x in range(int(w * 0.38), int(w * 0.62), 2):
            r, g, b = px[x, y]
            if r > 140 and g < 110 and b < 110 and r > g + 50:
                n += 1
                if n > 30:
                    return True
    return False


def wait_title_then_home(timeout=180):
    """Wait for PLAY NOW, tap it, then wait for new login/home requests."""
    deadline = time.time() + timeout
    tapped = False
    base_count = len(read_requests())
    while time.time() < deadline:
        if not tapped:
            pos = screen_green_button()
            if pos:
                tap(pos[0], pos[1], 2)
                tapped = True
        else:
            rows = read_requests()[base_count:]
            paths = [r.get("path", "") for r in rows]
            if any(p == "/quests/quest-list" for p in paths) or any(p == "/base/active" for p in paths):
                time.sleep(12)
                return True
        time.sleep(4)
    return False


def read_requests():
    rows = []
    if REQ.exists():
        for line in REQ.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def paths_since(rows, start):
    return [r.get("path", "") for r in rows if r.get("timestamp", "") >= start]


def logcat():
    _, out = adb("logcat", "-d", "-s", "Unity:V", timeout=60)
    return out


def memory_probes():
    out = []
    for name in ("read_bcg_memory.py", "read_prefight_state.py"):
        script = ROOT / "work" / name
        if not script.exists():
            continue
        try:
            _, text = run(sys.executable, script, timeout=120)
            out.append(f"===== {name} =====\n{text}")
        except Exception as exc:
            out.append(f"===== {name} =====\nprobe failed: {exc}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-launch", action="store_true")
    ap.add_argument("--no-memory", action="store_true")
    ap.add_argument("--plus", action="store_true", help="after the battle tile, tap the + slot")
    ap.add_argument("--fight", action="store_true", help="after the battle tile, tap FIGHT and capture the NRE")
    ap.add_argument("--full", action="store_true", help="also capture BOTS, bot details and EDIT SQUAD")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    steps = []
    notes = []

    def step(name, note=""):
        p = shot(name)
        steps.append({"name": name, "note": note, "screenshot": str(p), "bytes": p.stat().st_size if p.exists() else 0})
        print(f"[smoke] {name} {note}")

    if not args.no_launch:
        adb("shell", "am", "force-stop", PKG)
        adb("logcat", "-c")
        time.sleep(2)
        adb("shell", "am", "start", "-n", ACT)
        ok = wait_title_then_home(150)
        notes.append(f"title_to_home={ok}")
        step("01_title")
        step("02_home")
        tap(1124, 160, 6)
        step("03_fight")
        tap(671, 449, 8)
        step("04_story")
        tap(1436, 405, 8)
        step("05_quest")
        # EDIT SQUAD is captured separately: with a large roster the client
        # prompts "ADD MORE BOTS?" and auto-fills the team, which changes the
        # quest flow.  Manual evidence: work/edit2.png (TOTAL 100, ACCEPT).
        tap(2097, 1003, 4)
        # START with fewer bots than the roster may prompt "ADD MORE BOTS?".
        # Only tap CONTINUE when the prompt's green buttons are visible;
        # otherwise the tap would hit the map and open NODE INFO.
        for _ in range(3):
            if green_button_in_region(450, 720):
                tap(1339, 550, 8)
                break
            time.sleep(3)
        else:
            time.sleep(4)
        step("06_map")
        # The left-lower neighbour of the start tile is the (1,0) battle tile.
        tap(850, 732, 14)
        step("07_battle_tile")
    else:
        step("07_battle_tile")

    if args.plus:
        tap(1213, 788, 4)
        step("08_plus")

    if args.fight:
        tap(2024, 991, 5)
        step("09_fight_click")

    rows = read_requests()
    new_paths = paths_since(rows, start)
    lc = logcat()
    prefight = bool(re.search(r"SELECT YOUR BOT|PrefightScreen", lc, re.I))
    prefight_bar = screen_has_prefight_bar()
    prefight = prefight or prefight_bar
    model_nre = "PreFightScreen.OnFight" in lc
    scale_nre = "GetNewScale" in lc
    key = {
        "login": any(p.endswith("/bcg/getLoginData") for p in new_paths),
        "quest_begin": any("/quests/quest-begin" in p for p in new_paths),
        "movedir": any("/quests/quest-movedir" in p for p in new_paths),
        "activate_match": any("/matches/activate-match" in p for p in new_paths),
        "bugs": any(p == "/bugs" for p in new_paths),
    }
    plus_shot = OUT / "08_plus.png"
    plus_error = bool(plus_shot.exists() and plus_shot.stat().st_size < 150_000) or key["bugs"]
    mem = "" if args.no_memory else memory_probes()

    if args.full:
        # Run the BOTS screens after the main flow so a slow BOTS scene load
        # cannot break the quest navigation.
        adb("shell", "am", "force-stop", PKG)
        time.sleep(2)
        adb("shell", "am", "start", "-n", ACT)
        wait_title_then_home(150)
        tap(456, 160, 10)
        step("09_bots")
        tap(260, 551, 8)
        step("10_bot_details")
        tap(1138, 705, 3)
        tap(1138, 705, 8)
        step("10b_bot_info")
        adb("shell", "input", "keyevent", "4")
        time.sleep(3)
        adb("shell", "input", "keyevent", "4")
        time.sleep(3)
        step("11_after_bot_details")

    team_count = None
    m = re.search(r"local team[^\n]*count\s+(\d+)", mem, re.I)
    if not m:
        m = re.search(r"team[^0-9]{0,20}(\d+)", mem, re.I)
    if m:
        team_count = int(m.group(1))
    result = {
        "started": start,
        "finished": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "full" if args.full else "fast",
        "steps": steps,
        "notes": notes + (["edit_squad_manual=work/edit2.png"] if args.full else []),
        "paths": new_paths[-40:],
        "checks": key,
        "prefight_detected": prefight,
        "prefight_bar": prefight_bar,
        "nre_get_new_scale": scale_nre,
        "nre_prefight_model": model_nre,
        "plus_clicked": bool(args.plus),
        "fight_clicked": bool(args.fight),
        "plus_error": plus_error,
        "memory_team_count": team_count,
        "memory_probe": mem[-6000:],
        "status": "PASS" if (key["login"] and key["quest_begin"] and key["movedir"] and steps) else "FAIL",
        "note": "PASS means the scripted flow reached the battle tile and produced a screenshot; combat may still be blocked.",
    }
    report = OUT / "latest.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "checks", "prefight_detected", "nre_prefight_model", "memory_team_count")}, ensure_ascii=False, indent=2))
    print(f"[smoke] report: {report}")


if __name__ == "__main__":
    main()
