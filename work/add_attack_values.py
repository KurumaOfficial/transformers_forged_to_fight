"""Add the AttackLevel keys the client actually looks up in attackValues.

[STATIC] PlayerAttributes.kAttackLevelEnums maps:
  Light, Medium, Heavy, Ranged, Special1/2/3, Normal, Special.
Our old attackValues only had basic_melee, so GetAttackPercent returned 0 for
every basic attack and all damage was zero. Values below are [ASSUMED] until a
retail source is found.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "server" / "data" / "bcg_login_data.json"
data = json.loads(PATH.read_text(encoding="utf-8"))
av = data.setdefault("attackValues", {})

DEFAULTS = {
    "Light": (0.7, 0.04, 0.05, 1.5, 0.0),
    "Medium": (1.0, 0.05, 0.05, 1.5, 0.0),
    "Heavy": (1.5, 0.06, 0.05, 1.5, 0.0),
    "Ranged": (0.7, 0.04, 0.05, 1.5, 0.0),
    "Special1": (1.0, 0.0, 0.05, 1.5, 0.0),
    "Special2": (1.5, 0.0, 0.05, 1.5, 0.0),
    "Special3": (2.0, 0.0, 0.05, 1.5, 0.0),
    "Special": (1.5, 0.0, 0.05, 1.5, 0.0),
    "Normal": (1.0, 0.05, 0.05, 1.5, 0.0),
}
for key, (percent, mana, crit, crit_damage, crit_pierce) in DEFAULTS.items():
    av.setdefault(key, {
        "id": key,
        "a": key,
        "percent": percent,
        "p": percent,
        "mana_gain": mana,
        "m": mana,
        "crit_chance": crit,
        "c": crit,
        "crit_damage": crit_damage,
        "d": crit_damage,
        "crit_pierce": crit_pierce,
    })

PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("attackValues keys", sorted(av))
