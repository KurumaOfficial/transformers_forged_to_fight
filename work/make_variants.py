import json
from pathlib import Path
root = Path(r"C:\Users\gameg\Desktop\TFTF")
out = root / "work" / "variants"
out.mkdir(parents=True, exist_ok=True)
hero = "bumblebee_cin_dotm"
heroes = {
    hero: {
        "bid": hero, "blueprint": hero, "rank": 1, "level": 1, "sig_lvl": 0,
        "max_hp": 1000.0, "hp": 1000.0, "attack": 120,
        "rating_hp": 50, "rating_attack": 50, "special_attacks": 3,
        "user_owned": True, "pvpb": {}, "synergyBonuses": [], "forge_level": 0,
    }
}
team = {
    "aid": "story", "activityID": "story", "type": "story",
    "modes": ["Story"], "expire": 0, "heroes": heroes,
}
variants = [
    {"name": "v01_baseline", "description": "Текущая база: activeTeams list, story clone, heroes dict."},
    {"name": "v02_canonical_hero_key", "description": "Ключ героя без _2: bumblebee_cin_dotm; heroes dict.",
     "hero_key": hero, "hero_extra": {"bid": hero, "blueprint": hero}},
    {"name": "v03_mode_team_only", "description": "Одна active team с aid=story и полными hero fields.",
     "login_active_teams": [team]},
    {"name": "v04_hero_details_full", "description": "Hero details с rating_hp/rating_attack/special_attacks/forge_level.",
     "hero_key": hero, "hero_extra": {"rating_hp": 50, "rating_attack": 50, "special_attacks": 3,
                                       "user_owned": True, "forge_level": 0, "blueprint": hero}},
    {"name": "v05_quest_team_flat", "description": "quest-begin team = dict bid->hp/pi/sig_lvl/stat_mods/sig_mods.",
     "quest_team": {hero: {"hp": 1000.0, "pi": 100, "sig_lvl": 0, "stat_mods": [], "sig_mods": []}}},
    {"name": "v06_modes_expire", "description": "Type=Story, modes=[story,Story], expire=999999.",
     "team_extra": {"type": "Story", "modes": ["story", "Story"], "expire": 999999}},
]
for v in variants:
    (out / f"{v['name']}.json").write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n".join(str(p) for p in sorted(out.glob("*.json"))))
