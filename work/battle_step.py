"""Launch a fight, attack periodically, and verify damage/resolve/HP changes.

Normal server data only (no weak_enemy flag). Writes
tests/smoke/battle_step.json. Used by nightly; exits 0 only when the client
sent resolve-match and at least one HP/damage field changed.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
REQ = ROOT / "server" / "requests.jsonl"
OUT = ROOT / "tests" / "smoke" / "battle_step.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(*args, timeout=120):
    return subprocess.run([ADB, *args], capture_output=True, timeout=timeout)


def request_rows():
    try:
        return [json.loads(l) for l in REQ.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait", type=int, default=75)
    ap.add_argument("--no-launch", action="store_true")
    args = ap.parse_args()

    before = len(request_rows())
    cmd = [sys.executable, str(ROOT / "work" / "smoke_test.py"), "--plus", "--fight", "--no-memory"]
    if args.no_launch:
        cmd.append("--no-launch")
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
    print(p.stdout[-1500:])
    if p.returncode != 0:
        print(p.stderr[-800:])

    resolved = None
    deadline = time.time() + args.wait
    while time.time() < deadline:
        rows = request_rows()[before:]
        resolved = next((r for r in rows if (r.get("path") or "").startswith("/matches/resolve-match")), None)
        if resolved:
            break
        # tap the right-hand attack control to keep the fight moving
        adb("shell", "input", "tap", "2000", "940", timeout=20)
        time.sleep(0.45)

    body = (resolved or {}).get("body") or {}
    gs = body.get("game_stats") or {}
    p0 = gs.get("player_0_stats") or {}
    p1 = gs.get("player_1_stats") or {}

    def num(stats, *keys):
        for k in keys:
            v = stats.get(k)
            if isinstance(v, (int, float)):
                return float(v)
        return 0.0

    dmg0 = num(p0, "dmg_atk_total")
    dmg1 = num(p1, "dmg_atk_total")
    hp0_start, hp0_rem = num(p0, "hp_start"), num(p0, "hp_remaining")
    hp1_start, hp1_rem = num(p1, "hp_start"), num(p1, "hp_remaining")
    damage_nonzero = dmg0 > 0 or dmg1 > 0 or hp0_rem < hp0_start or hp1_rem < hp1_start
    hp_decreases = hp0_rem < hp0_start or hp1_rem < hp1_start
    result = ((body.get("results") or {}).get("result")) if isinstance(body.get("results"), dict) else None
    completed = bool(resolved and damage_nonzero and hp_decreases)
    check = {
        "resolve_match": bool(resolved),
        "fight_ends": bool(resolved),
        "damage_nonzero": bool(damage_nonzero),
        "hp_decreases": bool(hp_decreases),
        "completed": completed,
        "outcome": result,
        "result": result,
        "player_0": {"hp_start": hp0_start, "hp_remaining": hp0_rem, "dmg_atk_total": dmg0},
        "player_1": {"hp_start": hp1_start, "hp_remaining": hp1_rem, "dmg_atk_total": dmg1},
        "status": "COMPLETED" if completed else "FAIL",
    }
    OUT.write_text(json.dumps(check, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(check, ensure_ascii=False, indent=2))
    print("report", OUT)
    return 0 if completed else 1


if __name__ == "__main__":
    sys.exit(main())
