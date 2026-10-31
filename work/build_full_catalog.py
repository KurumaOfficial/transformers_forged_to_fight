"""Add all 59 client bot packs to the BCG catalog and grant them to the player.

This is a deliberate offline-test deviation: the original server would only
return owned bots.  Class/faction/star values come from
server/data/bot_catalog_real.json (client pack ids + wiki); bots without a
wiki star table get [ASSUMED] rank-1 stats.
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(r".")
LOGIN = ROOT / "server" / "data" / "bcg_login_data.json"
CATALOG = ROOT / "server" / "data" / "bot_catalog_real.json"
BACKUP = ROOT / "server" / "data" / "bcg_login_data.pre_full_catalog.json"

CLASS_BIT = {
    "Brawler": 1,
    "Tactician": 2,
    "Scout": 4,
    "Demolition": 8,
    "Demolitions": 8,
    "Warrior": 16,
    "Tech": 32,
}
SHARKTICON_CLASS = {
    "sharkticon_gs_brawler": "Brawler",
    "sharkticon_gs_demolition": "Demolition",
    "sharkticon_gs_scout": "Scout",
    "sharkticon_gs_tactician": "Tactician",
    "sharkticon_gs_tech": "Tech",
    "sharkticon_gs_warrior": "Warrior",
    "sharkticon_gs_kabam": "Brawler",
}
CLASS_TRIANGLE = {
    "Brawler": {"advantage": "Warrior", "disadvantage": "Tactician"},
    "Warrior": {"advantage": "Scout", "disadvantage": "Brawler"},
    "Scout": {"advantage": "Tech", "disadvantage": "Warrior"},
    "Tech": {"advantage": "Demolition", "disadvantage": "Scout"},
    "Demolition": {"advantage": "Tactician", "disadvantage": "Tech"},
    "Tactician": {"advantage": "Brawler", "disadvantage": "Demolition"},
}
EXISTING = {"bumblebee_cin_dotm": "bumblebee_cin_dotm_2", "optimus_c_tf": "optimus_c_tf_t3"}


def num(v, default=0):
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).replace(",", "").strip()
    try:
        return int(float(s))
    except Exception:
        return default


def main():
    data = json.loads(LOGIN.read_text(encoding="utf-8"))
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    rows = cat["rows"]
    if not BACKUP.exists():
        shutil.copy2(LOGIN, BACKUP)

    tmpl_bp = json.loads(json.dumps(data["blueprints"]["bumblebee_cin_dotm_2"]))
    tmpl_rank = json.loads(json.dumps(data["heroes"]["bumblebee_cin_dotm_2"]["1"]))
    tmpl_char = json.loads(json.dumps(data["characters"]["bumblebee_cin_dotm"]))
    tmpl_hero = json.loads(json.dumps(data["userData"]["heroes"][0]))

    data["blueprintsMax"] = 100
    data["userData"]["blueprintsMax"] = 100
    data["userData"]["userData"]["blueprintsMax"] = 100
    data["userData"]["teamSizeMax"] = 3
    data["userData"]["userData"]["teamSizeMax"] = 3

    # all six classes
    data.setdefault("heroClasses", {})
    for cls, tri in CLASS_TRIANGLE.items():
        key = cls.lower()
        data["heroClasses"][key] = {
            "id": key,
            "name": cls,
            "advantage": tri["advantage"].lower(),
            "disadvantage": tri["disadvantage"].lower(),
        }

    # synergies by faction
    faction_bots = {}
    for row in rows:
        cid = row["client_id"]
        mapped = EXISTING.get(cid, cid)
        faction = (row.get("faction") or "").strip()
        if faction and faction.lower() != "none":
            faction_bots.setdefault(faction, []).append(mapped)
    data.setdefault("synergyBonuses", {})
    for faction, ids in faction_bots.items():
        key = "syn_" + faction.lower() + "s"
        data["synergyBonuses"][key] = {
            "id": key,
            "friendly_name": f"{faction} Allegiance",
            "description": "Increases HP and Attack by 5%",
            "description_value": 5.0,
            "texture": "syn_" + faction.lower(),
            "bonus_heroes": ids,
            "required_heroes": ids,
            "target_tags": [faction.lower()],
            "enabled": True,
            "hero_rating_hp_mod": 1.05,
            "hero_rating_atk_mod": 1.05,
            "hero_rating_stat_mods": [],
        }

    next_uid = 2
    for row in rows:
        cid = row["client_id"]
        bid = EXISTING.get(cid, cid)
        if bid != cid:
            continue  # existing synthetic Bumblebee/Optimus already in the catalog
        cls = SHARKTICON_CLASS.get(cid, row.get("class") or "Scout")
        cls_bit = CLASS_BIT.get(cls, 4)
        faction = row.get("faction") or "Autobot"
        if faction.lower() in ("none", ""):
            faction = "None"
        wiki = row.get("wiki_page") or cid
        name = wiki
        stars = row.get("stars") or {}
        max_rank = 5
        if stars:
            try:
                max_rank = max(int(k) for k in stars)
            except Exception:
                max_rank = 5
        max_rank = max(1, min(5, max_rank))
        star1 = stars.get("1") or {}
        hp = num(star1.get("health"), 1000)
        atk = num(star1.get("attack"), 120)
        rating = num(star1.get("max_rating"), max(100, int(hp * 0.2 + atk)))
        rating_hp = max(1, int(rating * 0.5))
        rating_atk = max(1, rating - rating_hp)

        # blueprint
        bp = json.loads(json.dumps(tmpl_bp))
        bp.update({
            "blueprint": bid,
            "id": bid,
            "entity_type": "hero",
            "character": bid,
            "friendly_name": name,
            "friendly_name_short": name,
            "modelId": bid,
            "map_asset": bid,
            "imgID": bid,
            "gachaFeaturedImg": bid,
            "max_rank": max_rank,
            "rarity": max_rank,
            "class": cls_bit,
            "hero_class": cls_bit,
            "attribute_base_type": cls.lower(),
            "et": "hero",
            "tags": [cls.lower(), faction.lower()],
            "synergy_bonuses": ([] if faction == "None" else ["syn_" + faction.lower() + "s"]),
        })
        data["blueprints"][bid] = bp

        # character
        ch = json.loads(json.dumps(tmpl_char))
        ch.update({"id": bid, "name": name, "friendly_name": name,
                   "faction": 1 if faction == "Autobot" else (2 if faction == "Decepticon" else 0),
                   "subgroup": faction, "generation": row.get("generation") or "",
                   "ai_personality": "aggressive", "victory_stage": "", "special_stage": ""})
        data["characters"][bid] = ch

        # rank entries
        data.setdefault("heroes", {})
        data["heroes"][bid] = {}
        for rank in range(1, max_rank + 1):
            r = json.loads(json.dumps(tmpl_rank))
            r.update({
                "blueprint": bid, "id": bid, "rank": rank,
                "max_level": rank * 10,
                "attr_base": 100 + (rank - 1) * 20,
                "xp_curve": [0, 100, 250, 450, 700, 1000, 1350, 1750, 2200, 2700],
            })
            data["heroes"][bid][str(rank)] = r

        # player hero
        hero = json.loads(json.dumps(tmpl_hero))
        uid = str(next_uid)
        next_uid += 1
        hero.update({
            "bid": bid, "id": uid, "uid": uid, "hero": bid, "blueprint": bid,
            "rank": 1, "level": 1, "sig_lvl": 0,
            "hp": float(hp), "max_hp": float(hp), "attack": atk,
            "rating": rating, "rating_hp": rating_hp, "rating_attack": rating_atk,
            "rating_hp_base": rating_hp, "rating_attack_base": rating_atk,
            "hero_rating_hp": rating_hp, "hero_rating_attack": rating_atk,
        })
        ad = hero.get("attributeData") or {}
        ad.update({
            "hpMaxBase": hp, "hpMax": hp, "hp": float(hp),
            "attack": atk, "attackBase": atk,
            "heroRating": rating, "heroRatingHP": rating_hp,
            "heroRatingAttack": rating_atk, "heroRatingHPBase": rating_hp,
            "heroRatingAttackBase": rating_atk,
        })
        hero["attributeData"] = ad
        data["userData"].setdefault("heroes", []).append(hero)
        data["userData"].setdefault("entities", {}).setdefault("bot", {})[bid] = json.loads(json.dumps(hero))
        updates = data["userData"].setdefault("updates", {})
        updates.setdefault("heroes", []).append(json.loads(json.dumps(hero)))
        updates.setdefault("entities", {}).setdefault("bot", {})[bid] = json.loads(json.dumps(hero))

    def set_team_size(obj):
        if isinstance(obj, dict):
            if "teamSizeMax" in obj:
                obj["teamSizeMax"] = 1
            for v in obj.values():
                set_team_size(v)
        elif isinstance(obj, list):
            for v in obj:
                set_team_size(v)
    set_team_size(data)

    LOGIN.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("blueprints", len(data["blueprints"]), "heroes", len(data["userData"]["heroes"]),
          "entities.bot", len(data["userData"]["entities"]["bot"]),
          "ranks", len(data["heroes"]), "backup", BACKUP.name)


if __name__ == "__main__":
    main()
