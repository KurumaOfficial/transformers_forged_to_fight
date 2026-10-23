import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
LOGIN = ROOT / "server" / "data" / "bcg_login_data.json"
QUEST = ROOT / "server" / "data" / "quest_begin_response.json"
SMOKE = ROOT / "work" / "smoke_test.py"
RESULTS = ROOT / "work" / "variant_results.jsonl"
LEDGER = ROOT / "LEDGER.md"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_variant(v):
    login = load(LOGIN)
    quest = load(QUEST)
    ud = login.setdefault("userData", {})
    ats = ud.get("activeTeams") or []
    if not isinstance(ats, list):
        ats = list(ats.values())
    if "login_active_teams" in v:
        supplied = v["login_active_teams"]
        ats = json.loads(json.dumps(list(supplied.values()) if isinstance(supplied, dict) else supplied))
    for t in ats:
        if not isinstance(t, dict):
            continue
        t.update(v.get("team_extra") or {})
        hv = t.get("heroes")
        if isinstance(hv, dict):
            if v.get("hero_key"):
                hv = {v["hero_key"]: val for val in hv.values()}
            for h in hv.values():
                if isinstance(h, dict):
                    h.update(v.get("hero_extra") or {})
            t["heroes"] = hv
        if v.get("heroes_list") and isinstance(t.get("heroes"), dict):
            t["heroes"] = list(t["heroes"].values())
    ud["activeTeams"] = ats
    if "quest_team" in v:
        quest["team"] = json.loads(json.dumps(v["quest_team"]))
    save(LOGIN, login)
    save(QUEST, quest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variants", nargs="+", help="JSON variant files")
    ap.add_argument("--plus", action="store_true")
    args = ap.parse_args()
    b1 = LOGIN.with_suffix(".json.variant_backup")
    b2 = QUEST.with_suffix(".json.variant_backup")
    shutil.copy2(LOGIN, b1)
    shutil.copy2(QUEST, b2)
    try:
        for vf in args.variants:
            v = load(Path(vf))
            name = v.get("name") or Path(vf).stem
            print(f"[variant] {name}: {v.get('description', '')}")
            apply_variant(v)
            cmd = [sys.executable, str(SMOKE)]
            if args.plus:
                cmd.append("--plus")
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
            print(p.stdout[-2000:])
            if p.returncode != 0:
                print(p.stderr[-1000:])
            report_path = ROOT / "tests" / "smoke" / "latest.json"
            report = load(report_path) if report_path.exists() else {}
            row = {
                "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "variant": name,
                "description": v.get("description", ""),
                "status": report.get("status"),
                "paths": report.get("paths"),
                "checks": report.get("checks"),
                "prefight_detected": report.get("prefight_detected"),
                "nre_get_new_scale": report.get("nre_get_new_scale"),
                "plus_clicked": report.get("plus_clicked"),
                "plus_error": report.get("plus_error"),
                "memory_team_count": report.get("memory_team_count"),
                "screenshot_07_bytes": next((s.get("bytes") for s in report.get("steps", []) if s.get("name") == "07_battle_tile"), None),
                "screenshot_08_bytes": next((s.get("bytes") for s in report.get("steps", []) if s.get("name") == "08_plus"), None),
            }
            RESULTS.parent.mkdir(exist_ok=True)
            with RESULTS.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            with LEDGER.open("a", encoding="utf-8") as f:
                f.write(f"\n- A3 variant `{name}`: status={row['status']}, "
                        f"activate_match={row['checks'].get('activate_match') if row['checks'] else None}, "
                        f"plus_error={row['plus_error']}, team_count={row['memory_team_count']}. "
                        f"{row['description']}\n")
            print(json.dumps(row, ensure_ascii=False, indent=2))
    finally:
        shutil.copy2(b1, LOGIN)
        shutil.copy2(b2, QUEST)
        b1.unlink(missing_ok=True)
        b2.unlink(missing_ok=True)
        print("[variant] restored base server data")


if __name__ == "__main__":
    main()
