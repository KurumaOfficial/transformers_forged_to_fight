import json
from pathlib import Path
out = Path(r".\work\variants")
hero = "bumblebee_cin_dotm"
h = {"bid": hero, "blueprint": hero, "rank": 1, "level": 1, "sig_lvl": 0,
     "max_hp": 1000.0, "hp": 1000.0, "attack": 120, "rating_hp": 50,
     "rating_attack": 50, "special_attacks": 3, "user_owned": True,
     "pvpb": {}, "synergyBonuses": [], "forge_level": 0}
team = {"aid": "story", "activityID": "story", "type": "story",
        "modes": ["Story"], "expire": 0, "heroes": {hero: h}}
variants = [
    {"name": "v07_dict_team", "description": "login activeTeams as dict keyed story.", "login_active_teams": {"story": team}},
    {"name": "v08_heroes_list", "description": "active team heroes as list, not dict.", "login_active_teams": [team], "heroes_list": True},
    {"name": "v09_story_qid_hero", "description": "aid story, hero key bumblebee_cin_dotm_2.", "login_active_teams": [dict(team, heroes={"bumblebee_cin_dotm_2": dict(h, bid="bumblebee_cin_dotm_2", blueprint="bumblebee_cin_dotm_2")})]},
    {"name": "v10_empty_control", "description": "control: no active teams.", "login_active_teams": []},
]
for v in variants:
    (out / f"{v['name']}.json").write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", len(variants))
