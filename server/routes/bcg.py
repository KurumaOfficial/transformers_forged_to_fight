"""BCG response builders (T1 routing split, behavior unchanged).

The attribute values here are [ASSUMED] placeholders; the request/response
schema is [CLIENT]. Keep the arithmetic and envelope identical to the inline
stub implementation.
"""

import json


def login_data(load_data_json):
    return load_data_json("bcg_login_data.json")


def base_hero_data(body, load_data_json, weak_enemy=False):
    heroes_req = []
    if isinstance(body, dict):
        heroes_req = body.get("heroes") or []
    details = []
    base_cat = None
    for h in heroes_req:
        if not isinstance(h, dict):
            continue
        bid = h.get("bid", "")
        rank = int(h.get("rank", 1) or 1)
        level = int(h.get("level", 1) or 1)
        sig = int(h.get("sig_lvl", 0) or 0)
        hp = 800 + rank * 200 + level * 50
        atk = 80 + rank * 30 + level * 5
        if weak_enemy and bid in ("sideswipe_gs", "enemy1"):
            hp = 1
            atk = 1
        rating_hp = int(hp * 0.1)
        rating_attack = int(atk * 0.5)
        if base_cat is None:
            base_cat = load_data_json("bcg_login_data.json")
        bp = (base_cat.get("blueprints") or {}).get(bid, {})
        details.append({
            "bid": bid,
            "blueprint": bid,
            "rank": rank,
            "level": level,
            "sig_lvl": sig,
            "max_hp": hp,
            "hp_max": hp,
            "hpMax": hp,
            "maxHp": hp,
            "hp": float(hp),
            "attack": atk,
            "armor": 0.0,
            "crit_chance": 0.1,
            "crit_damage": 1.5,
            "block_proficiency": 0.5,
            "perfect_block_chance": 0.0,
            "mana_gain": 1.0,
            "mana_start": 0,
            "class_power": 1.0,
            "resist_magic": 0.0,
            "resist_physical": 0.0,
            "stat_mods": [],
            "sig_mods": [],
            "buff_mods": [],
            "tags": list(bp.get("tags") or bp.get("t") or []),
            "rating": rating_hp + rating_attack,
            "rating_hp": rating_hp,
            "rating_attack": rating_attack,
            "rating_hp_base": rating_hp,
            "rating_attack_base": rating_attack,
            "special_attacks": 3,
            "pvpb": {},
            "synergyBonuses": [],
            "attributeData": {
                "hpMaxBase": hp,
                "hpMax": hp,
                "hp": float(hp),
                "attack": atk,
                "attackBase": atk,
                "armor": 0.0,
                "critChance": 0.1,
                "critDamage": 1.5,
                "perfectBlockChance": 0.0,
                "blockProficiency": 0.5,
                "manaGain": 1.0,
                "manaStart": 0,
                "classPower": 1.0,
                "resistMagic": 0.0,
                "resistPhysical": 0.0,
                "stunTime": 0,
                "stunChance": 0.0,
                "heroRating": rating_hp + rating_attack,
                "heroRatingHP": rating_hp,
                "heroRatingAttack": rating_attack,
                "heroRatingHPBase": rating_hp,
                "heroRatingAttackBase": rating_attack,
                "specialAttackCount": 3,
                "statMods": [],
                "sigMods": [],
                "buffMods": []
            },
            "user_owned": True
        })
    return details


def user_data(load_data_json):
    return load_data_json("bcg_user_data.json")


def set_saved_team(body, load_data_json):
    base = load_data_json("bcg_login_data.json")
    ud = json.loads(json.dumps(base.get("userData", {})))
    team_id = "0"
    hero_ids = []
    if isinstance(body, dict):
        team_id = str(body.get("teamID", "0"))
        hero_ids = body.get("heroes") or []
    details = []
    for bid in hero_ids:
        hero = next((h for h in ud.get("heroes", []) if h.get("bid") == bid), None)
        rank = int(hero.get("rank", 1)) if hero else 1
        level = int(hero.get("level", 1)) if hero else 1
        hp = 800 + rank * 200 + level * 50
        atk = 80 + rank * 30 + level * 5
        details.append({
            "bid": bid, "rank": rank, "level": level, "sig_lvl": 0,
            "max_hp": hp, "attack": atk,
            "rating": int(hp * 0.1) + int(atk * 0.5),
            "rating_hp": int(hp * 0.1), "rating_attack": int(atk * 0.5),
            "rating_hp_base": int(hp * 0.1), "rating_attack_base": int(atk * 0.5),
            "special_attacks": 3, "pvpb": {},
            "synergyBonuses": [], "user_owned": True
        })
    saved = ud.get("savedTeams")
    if not isinstance(saved, list):
        saved = []
    saved = [t for t in saved if not (isinstance(t, dict) and str(t.get("sid")) == team_id)]
    saved.append({"sid": team_id, "heroes": details})
    ud["savedTeams"] = saved
    # Same envelope shape as /bcg/getLoginData.result.userData (verified to parse):
    # { userData:{...}, updates:{heroes,...}, deletes:{} }
    wrapper = {
        "userData": {
            "blueprintsMax": ud.get("blueprintsMax", 50),
            "teamSizeMax": ud.get("teamSizeMax", 3),
            "teamCountMax": ud.get("teamCountMax", 3)
        },
        "updates": {
            "heroes": ud.get("heroes", []),
            "savedTeams": ud.get("savedTeams", []),
            "activeTeams": ud.get("activeTeams", []),
            "inventory": ud.get("inventory", {"f": {}, "bp": {}, "max": {}}),
            "heroesScreenList": [],
            "heroes_cta": {}
        },
        "deletes": {}
    }
    payload = json.loads(json.dumps(base))
    payload["userData"] = wrapper
    return payload
