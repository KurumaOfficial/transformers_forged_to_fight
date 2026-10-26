"""Four-run battle matrix: player blueprint x enemy blueprint.

The smoke test always selects the current progress quest `story_act1_ch4_m2`;
we keep the qid and swap the player's active-team bid and that quest's boss id.
Read-mostly: all files are restored afterwards.
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "server" / "data"
LOGIN = DATA / "bcg_login_data.json"
QL = DATA / "quest_list.json"
SMOKE = ROOT / "work" / "smoke_test.py"
RESULTS = ROOT / "work" / "battle_matrix.jsonl"
QID = "story_act1_ch4_m2"
VARIANTS = [
    ("dotm_sideswipe", "bumblebee_cin_dotm_2", "sideswipe_gs"),
    ("dotm_rhinox", "bumblebee_cin_dotm_2", "rhinox_gs_voyager2014"),
    ("kabam_sideswipe", "bumblebee_gs_kabam", "sideswipe_gs"),
    ("kabam_rhinox", "bumblebee_gs_kabam", "rhinox_gs_voyager2014"),
]
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def apply(player_bid, boss_bid):
    login = load(LOGIN)
    teams = login.get("userData", {}).get("activeTeams", [])
    if isinstance(teams, dict):
        teams = list(teams.values())
    for t in teams:
        hv = t.get("heroes")
        if isinstance(hv, dict):
            hv = list(hv.values())
        if not hv:
            continue
        first = hv[0]
        first["bid"] = player_bid
        first["blueprint"] = player_bid
        first["hero"] = player_bid
        t["heroes"] = hv
    login["userData"]["activeTeams"] = teams
    save(LOGIN, login)
    ql = load(QL)
    for qs in ql:
        for q in qs.get("availableQuests", []):
            if q.get("id") == QID:
                q["finalBoss"] = {"id": boss_bid, "level": 1, "rank": 1}
    save(QL, ql)


b1 = LOGIN.with_suffix(".json.matrix_backup")
b2 = QL.with_suffix(".json.matrix_backup")
shutil.copy2(LOGIN, b1)
shutil.copy2(QL, b2)
try:
    for name, player, boss in VARIANTS:
        print(f"[matrix] {name}: {player} vs {boss}")
        apply(player, boss)
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command",
                        f"& '{ROOT / 'work' / 'platform-tools' / 'adb.exe'}' logcat -c"],
                       capture_output=True, timeout=60)
        p = subprocess.run([sys.executable, str(SMOKE), "--plus", "--fight", "--no-memory"],
                           capture_output=True, text=True, timeout=480)
        logcat = subprocess.run([str(ROOT / "work" / "platform-tools" / "adb.exe"),
                                 "logcat", "-d", "-v", "time", "-s", "Unity:V"],
                                capture_output=True, text=True, timeout=120).stdout
        nre = "ArgumentNullException" in logcat
        playerattrs = "PlayerAttributes.Init" in logcat
        req = (ROOT / "server" / "requests.jsonl").read_text(encoding="utf-8", errors="replace")
        row = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "variant": name, "player": player, "boss": boss,
            "smoke_rc": p.returncode,
            "activate_match": "/matches/activate-match" in req,
            "match_loaded": "/matches/match-loaded" in req,
            "nre": nre, "nre_playerattrs": playerattrs,
            "smoke_tail": p.stdout[-500:],
        }
        with RESULTS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps(row, ensure_ascii=False, indent=1))
finally:
    shutil.copy2(b1, LOGIN)
    shutil.copy2(b2, QL)
    b1.unlink(missing_ok=True)
    b2.unlink(missing_ok=True)
    print("[matrix] restored")
