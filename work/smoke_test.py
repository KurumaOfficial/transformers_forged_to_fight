import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
ADB = ROOT / "work" / "platform-tools" / "adb.exe"
OUT = ROOT / "tests" / "smoke"
REQ = ROOT / "server" / "requests.jsonl"
PKG = "com.kabam.bigrobot"
ACT = "com.kabam.bigrobot/com.explodingbarrel.Activity"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(*args, timeout=120):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def adb(*args, timeout=120):
    return run(ADB, *args, timeout=timeout)


def tap(x, y, wait=1.0):
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def shot(name):
    OUT.mkdir(parents=True, exist_ok=True)
    remote = f"/sdcard/smoke_{name}.png"
    local = OUT / f"{name}.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    return local


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


def memory_probe():
    script = ROOT / "work" / "read_prefight_state.py"
    if not script.exists():
        return ""
    try:
        _, out = run(sys.executable, script, timeout=90)
        return out
    except Exception as exc:
        return f"probe failed: {exc}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-launch", action="store_true")
    ap.add_argument("--no-memory", action="store_true")
    ap.add_argument("--plus", action="store_true", help="after the battle tile, tap the + slot")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    steps = []

    def step(name, note=""):
        p = shot(name)
        steps.append({"name": name, "note": note, "screenshot": str(p), "bytes": p.stat().st_size if p.exists() else 0})
        print(f"[smoke] {name} {note}")

    if not args.no_launch:
        adb("shell", "am", "force-stop", PKG)
        adb("logcat", "-c")
        time.sleep(2)
        adb("shell", "am", "start", "-n", ACT)
        time.sleep(38)
        step("01_title")
        tap(1138, 892, 25)
        step("02_home")
        tap(1124, 145, 5)
        step("03_fight")
        tap(529, 354, 5)
        step("04_story")
        tap(1436, 405, 7)
        step("05_quest")
        tap(2126, 946, 12)
        step("06_map")
        # The tile is the left-lower neighbour of the start tile on act 1 map.
        tap(850, 732, 16)
        step("07_battle_tile")
    else:
        step("07_battle_tile")

    if args.plus:
        tap(1209, 857, 5)
        step("08_plus")

    rows = read_requests()
    new_paths = paths_since(rows, start)
    lc = logcat()
    prefight = bool(re.search(r"PrefightScreenPresentation|SELECT YOUR BOT", lc, re.I))
    nre = "GetNewScale" in lc or "NullReferenceException" in lc
    key = {
        "login": any(p.endswith("/bcg/getLoginData") for p in new_paths),
        "quest_begin": any("/quests/quest-begin" in p for p in new_paths),
        "movedir": any("/quests/quest-movedir" in p for p in new_paths),
        "activate_match": any("/matches/activate-match" in p for p in new_paths),
        "bugs": any(p == "/bugs" for p in new_paths),
    }
    plus_shot = OUT / "08_plus.png"
    plus_error = bool(plus_shot.exists() and plus_shot.stat().st_size < 150_000) or key["bugs"]
    mem = "" if args.no_memory else memory_probe()
    team_count = None
    m = re.search(r"team[^0-9]{0,20}(\d+)", mem, re.I)
    if m:
        team_count = int(m.group(1))
    result = {
        "started": start,
        "finished": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "steps": steps,
        "paths": new_paths[-40:],
        "checks": key,
        "prefight_detected": prefight,
        "nre_get_new_scale": nre,
        "plus_clicked": bool(args.plus),
        "plus_error": plus_error,
        "memory_team_count": team_count,
        "memory_probe": mem[-4000:],
        "status": "PASS" if (key["login"] and key["quest_begin"] and key["movedir"] and steps) else "FAIL",
        "note": "PASS means the scripted flow reached the battle tile and produced a screenshot; combat may still be blocked.",
    }
    report = OUT / "latest.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "checks", "prefight_detected", "nre_get_new_scale", "memory_team_count")}, ensure_ascii=False, indent=2))
    print(f"[smoke] report: {report}")


if __name__ == "__main__":
    main()
