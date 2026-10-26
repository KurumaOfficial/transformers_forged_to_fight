"""Add hidden base attributes to every heroes[bid][rank] catalog entry.

[STATIC] BCGUserHeroBase..ctor (0xA62348) copies BCGHeroBaseCommon.AttributeData
(+0x48) into BCGUserHeroBase.AttributeData (+0x38) and then overwrites Attack.
BCGHeroBaseCommon..ctor (0xC21EA0) builds that AttributeData from the same rank
dictionary, so armor/crit/block/mana keys on a rank entry are the data source for
the player's quest-battle attributes. Values below are [ASSUMED] defaults.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "server" / "data" / "bcg_login_data.json"
BAK = ROOT / "work" / "bcg_login_data.pre_rank_stats.json"

DEFAULTS = {
    "armor": 50.0,
    "crit_chance": 0.1,
    "crit_damage": 1.5,
    "perfect_block_chance": 0.0,
    "block_proficiency": 0.5,
    "mana_gain": 1.0,
    "mana_start": 0.0,
    "resist_magic": 0.0,
    "resist_physical": 0.0,
    "stun_time": 0.0,
    "stun_chance": 0.0,
    "special_attacks": 3,
}

if not BAK.exists():
    shutil.copy2(PATH, BAK)
data = json.loads(PATH.read_text(encoding="utf-8"))
n = 0
for bid, ranks in (data.get("heroes") or {}).items():
    if not isinstance(ranks, dict):
        continue
    for rk, entry in ranks.items():
        if not isinstance(entry, dict):
            continue
        for k, v in DEFAULTS.items():
            entry.setdefault(k, v)
        n += 1
PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("rank entries updated", n)
print("backup", BAK)

# Also populate the login active-team hero details; quest-begin rebuilds these,
# but they are used outside the quest flow (prefight/display).
teams = 0
for team in ((data.get("userData") or {}).get("activeTeams") or []):
    for hero in (team.get("heroes") or {}).values():
        if not isinstance(hero, dict):
            continue
        for k, v in DEFAULTS.items():
            hero.setdefault(k, v)
        teams += 1
PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("activeTeam heroes updated", teams)

