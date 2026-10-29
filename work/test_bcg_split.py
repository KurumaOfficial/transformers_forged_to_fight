"""Offline regression for the BCG route split (no server restart)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from routes import bcg  # noqa: E402

DATA = ROOT / "server" / "data"


def load(name, default=None):
    p = DATA / name
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


details = bcg.base_hero_data({"heroes": [
    {"bid": "bumblebee_cin_dotm_2", "rank": 1, "level": 1, "sig_lvl": 0}
]}, load)
row = details[0]
assert row["bid"] == "bumblebee_cin_dotm_2"
assert row["rank"] == 1 and row["level"] == 1
assert row["max_hp"] == 1050, row["max_hp"]
assert row["attack"] == 115, row["attack"]
assert row["hp"] == 1050.0
assert row["attributeData"]["hpMax"] == 1050
assert row["rating"] == 105 + 57, row["rating"]
assert row["user_owned"] is True

weak = bcg.base_hero_data({"heroes": [
    {"bid": "sideswipe_gs", "rank": 1, "level": 1}
]}, load, True)[0]
assert weak["max_hp"] == 1 and weak["attack"] == 1

payload = bcg.set_saved_team({"teamID": "0", "heroes": ["bumblebee_cin_dotm_2"]}, load)
assert "userData" in payload
assert "updates" in payload["userData"] and "deletes" in payload["userData"]
assert payload["userData"]["userData"]["teamSizeMax"] >= 1
assert payload["userData"]["updates"]["savedTeams"]

login = bcg.login_data(load)
assert "userData" in login
assert bcg.user_data(load)["heroes"]

print(json.dumps({"status": "PASS", "hero": row["bid"], "hp": row["max_hp"],
                  "attack": row["attack"], "rating": row["rating"]}, ensure_ascii=False))
