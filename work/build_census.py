"""Build data/client_character_census.json from bundles, TOC, localization.

Read-only over the client assets; writes only data/.
"""
import json
import os
import re
from collections import Counter

ROOT = os.getcwd()
ASSETS = os.path.join(ROOT, "work", "unpacked", "assets")
ASSETPACK = os.path.join(ASSETS, "assetpack")

MAP = {
    "arcee_gs_deluxe2014": "ARCEE_GS",
    "barricade_cin_dotm": "BARRI_C",
    "blaster_gs_leader2016": "BLASTR_GS",
    "bludgeon_gs_rd20": "BLUDGE_GS",
    "bonecrusher_cin_rotf": "BONEC_C",
    "bumblebee_cin_dotm": "BUMBL_C",
    "bumblebee_gs_kabam": "BUMBL_GS",
    "cheetor_bw_transmetal": "CHEETOR_BW",
    "cliffjumper_gs_kabam": "CLIFFJUMP_GS",
    "cyclonus_gs_uw06": "CYCLON_GS",
    "dinobot_bw_kabam": "DINOB_BW",
    "dirge_gs_deluxe2008": "DIRGE_GS",
    "drift_cin_aoe": "DRIFT_C",
    "galvatron_gs_voyager2016": "GALVATRON_GS",
    "grimlock_gs_mp08": "GRIML_GS",
    "grindor_cin_rotf": "GRIND_C_ROTF",
    "hotrod_cin_tlk": "HOTRO_C",
    "hound_cin_tlk": "HOUND_C",
    "ironhide_cin_rotf": "IRONH_C_ROTF",
    "ironhide_gs_kabam": "IRONH_GS",
    "jazz_gs_twm05": "JAZZ_GS",
    "jetfire_gs_leader2014": "JETFIRE_GS",
    "kickback_gs_kabam": "KICKB_GS",
    "megatron_cin_rotf": "MEGAT_C",
    "megatron_gs_leader2015": "MEGAT_GS",
    "megatronus_gs_kabam": "MEGATRO_GS",
    "mirage_gs_deluxe2016": "MIRAG_GS",
    "mixmaster_cin_rotf": "MIXMA_C_ROTF",
    "motormaster_gs_voyager2015": "MOTORM_GS",
    "necrotronus_gs_kabam": "NECROTRO_GS",
    "nemesisprime_gs_voyager2015": "NEMESIS_GS",
    "optimusprimal_bw_mp32": "OPRIMAL_BW",
    "optimusprime_cin_tf": "OPTIMUS_C_TF",
    "optimusprime_gs_v": "OPTIMUS_GS",
    "prowl_gs_deluxe2016": "PROWL_GS",
    "ramjet_gs_deluxe2008": "RAMJET_GS",
    "ratchet_gs_kabam": "RATCH_GS",
    "rhinox_gs_voyager2014": "RHINO_BW",
    "rodimusprime_gs_mp09": "RODIMUS_GS",
    "scorponok_bw_kabam": "SCORPO_BW",
    "sharkticon_gs_brawler": "SHARK_BRAW",
    "sharkticon_gs_demolition": "SHARK_DEMO",
    "sharkticon_gs_kabam": "SHARK_GOLD",
    "sharkticon_gs_scout": "SHARK_SCOU",
    "sharkticon_gs_tactician": "SHARK_TACT",
    "sharkticon_gs_tech": "SHARK_TECH",
    "sharkticon_gs_warrior": "SHARK_WARR",
    "shockwave_gs": "SHOCK_C",
    "sideswipe_gs": "SIDES_GS",
    "skywarp_gs_leader2015": "SKYWARP_GS",
    "slipstream_gs": "SLIPSTREAM_GS",
    "soundblaster_gs_mp13b": "SOUNDBLAST_GS",
    "soundwave_gs": "SOUND_GS",
    "starscream_gs": "STARS_GS",
    "sunstreaker_gs_deluxe2008": "SUNSTREAK_GS",
    "tantrum_gs_kabam": "TANTRUM_GS",
    "thundercracker_gs_leader2015": "THUNDERCRACKER_GS",
    "ultramagnus_gs_leader": "ULTRAM_GS",
    "waspinator_gs_deluxe": "WASP_BW",
    "wheeljack_gs_mp20": "WHEELJ_GS",
    "windblade_gs": "WINDB_GS",
}

# Portrait/dialogue token aliases that differ from the localization token.
PORTRAIT_TOKEN = {
    "thundercracker_gs_leader2015": "thunder_gs",
    "optimusprime_cin_tf": "optimus_c_tf",
    "optimusprime_gs_v": "optimus_gs",
    "soundblaster_gs_mp13b": "soundblast_gs",
    "megatronus_gs_kabam": "megatro_gs",
}
for _cid in list(MAP):
    PORTRAIT_TOKEN.setdefault(_cid, MAP[_cid].lower())
PORTRAIT_TOKEN.update({
    "cyclonus_gs_uw06": "cyclon_gs",
    "hotrod_cin_tlk": "hotrod_c",
    "sharkticon_gs_brawler": "npc_shark_braw",
    "sharkticon_gs_demolition": "npc_shark_demo",
    "sharkticon_gs_kabam": "npc_shark_gold",
    "sharkticon_gs_scout": "npc_shark_scou",
    "sharkticon_gs_tactician": "npc_shark_tact",
    "sharkticon_gs_tech": "npc_shark_tech",
    "sharkticon_gs_warrior": "npc_shark_warr",
})

TOKEN_ALIASES = {
    "BUMBLE_GS": "bumblebee_gs_kabam",
    "DINOB_GS": "dinobot_bw_kabam",
    "MIXMA_GS": "mixmaster_cin_rotf",
    "CLYCLON_GS": "cyclonus_gs_uw06",
    "NPC_SHARK_BRAW": "sharkticon_gs_brawler",
    "NPC_SHARK_BRAWL": "sharkticon_gs_brawler",
    "NPC_SHARK_DEMO": "sharkticon_gs_demolition",
    "NPC_SHARK_GOLD": "sharkticon_gs_kabam",
    "NPC_SHARK_GOLD2": "sharkticon_gs_kabam",
    "NPC_SHARK_SCOU": "sharkticon_gs_scout",
    "NPC_SHARK_TACT": "sharkticon_gs_tactician",
    "NPC_SHARK_TECH": "sharkticon_gs_tech",
    "NPC_SHARK_WARR": "sharkticon_gs_warrior",
    "SHARK_GOLD2": "sharkticon_gs_kabam",
    "HOTROD_C": "hotrod_cin_tlk",
}

MOVE_ALIAS = {
    "arcee_gs_deluxe2014": ["arcee"],
    "barricade_cin_dotm": ["barricade"],
    "blaster_gs_leader2016": ["blaster"],
    "bludgeon_gs_rd20": ["bludgeon"],
    "bonecrusher_cin_rotf": ["bonecrusher"],
    "bumblebee_cin_dotm": ["bumblebee"],
    "bumblebee_gs_kabam": ["bumblebee_gs"],
    "cheetor_bw_transmetal": ["cheetor"],
    "cliffjumper_gs_kabam": ["cliffjumper"],
    "cyclonus_gs_uw06": ["cyclonus"],
    "dinobot_bw_kabam": ["dinobot"],
    "dirge_gs_deluxe2008": ["dirge"],
    "drift_cin_aoe": ["drift"],
    "galvatron_gs_voyager2016": ["galvatron"],
    "grimlock_gs_mp08": ["grimlock"],
    "grindor_cin_rotf": ["grindor"],
    "hotrod_cin_tlk": ["hotrod"],
    "hound_cin_tlk": ["hound"],
    "ironhide_cin_rotf": ["ironhide"],
    "ironhide_gs_kabam": ["ironhide_gs"],
    "jazz_gs_twm05": ["jazz"],
    "jetfire_gs_leader2014": ["jetfire"],
    "kickback_gs_kabam": ["kickback"],
    "megatron_cin_rotf": ["megatron"],
    "megatron_gs_leader2015": ["megatron_gs"],
    "megatronus_gs_kabam": ["megatronus"],
    "mirage_gs_deluxe2016": ["mirage"],
    "mixmaster_cin_rotf": ["mixmaster"],
    "motormaster_gs_voyager2015": ["motormaster"],
    "necrotronus_gs_kabam": ["necrotronus"],
    "nemesisprime_gs_voyager2015": ["nemesis_gs"],
    "optimusprimal_bw_mp32": ["primal"],
    "optimusprime_cin_tf": ["optimus"],
    "optimusprime_gs_v": ["optimus_gs"],
    "prowl_gs_deluxe2016": ["prowl"],
    "ramjet_gs_deluxe2008": ["ramjet"],
    "ratchet_gs_kabam": ["ratchet"],
    "rhinox_gs_voyager2014": ["rhinox"],
    "rodimusprime_gs_mp09": ["rodimus_gs"],
    "scorponok_bw_kabam": ["scorponok"],
    "sharkticon_gs_brawler": ["sharkticon_brawler"],
    "sharkticon_gs_demolition": ["sharkticon_demolitions"],
    "sharkticon_gs_kabam": ["sharkticon_gold"],
    "sharkticon_gs_scout": ["sharkticon_scout"],
    "sharkticon_gs_tactician": ["sharkticon_tactician"],
    "sharkticon_gs_tech": ["sharkticon_tech"],
    "sharkticon_gs_warrior": ["sharkticon_warrior"],
    "shockwave_gs": ["shockwave"],
    "sideswipe_gs": ["sideswipe"],
    "skywarp_gs_leader2015": ["skywarp"],
    "slipstream_gs": ["slipstream"],
    "soundblaster_gs_mp13b": ["soundblast"],
    "soundwave_gs": ["soundwave"],
    "starscream_gs": ["starscream"],
    "sunstreaker_gs_deluxe2008": ["sunstreak"],
    "tantrum_gs_kabam": ["tantrum"],
    "thundercracker_gs_leader2015": ["thundercracker"],
    "ultramagnus_gs_leader": ["ultramagnus"],
    "waspinator_gs_deluxe": ["waspinator"],
    "wheeljack_gs_mp20": ["wheeljack"],
    "windblade_gs": ["windblade"],
}

WIKI_EXTRA = {
    "optimusprime_gs_v": "Optimus Prime",
    "starscream_gs": "Starscream",
}


def load(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


loc = load("work/localization_all.json", {})
raw = load("work/census_raw.json", {})
chars = raw.get("chars", {})
moves = raw.get("moves", {})
inv = load("work/bundle_inventory.json", {}).get("bundles", {})
wiki = load("data/wiki/bots.json", {}).get("bots", {})
coverage = {r["client_id"]: r for r in load("data/wiki/stat_coverage.json", {}).get("rows", [])
            if isinstance(r, dict) and r.get("client_id")}
derived = load("data/wiki/derived_level1.json", {}).get("bots", {})
catalog = load("server/data/bcg_login_data.json", {})
blueprints = catalog.get("blueprints", {})
characters = catalog.get("characters", {})
heroes = catalog.get("heroes", {})
roster = {h.get("bid"): h for h in (catalog.get("userData", {}) or {}).get("heroes", [])
          if isinstance(h, dict)}
id_map = load("data/wiki/id_map.json", {}).get("matched", [])
id_map = {e["client_id"]: e for e in id_map if isinstance(e, dict)}
boss_map = load("data/boss_map.json", {})
patch = load("server/data/starscream_patch.json", {})

# Count effective catalog with the load-time patch.
bp_eff = set(blueprints) | set((patch.get("blueprints") or {}).keys())
chars_eff = set(characters) | set((patch.get("characters") or {}).keys())
roster_eff = set(roster) | ({"starscream_gs"} if patch.get("hero") else set())

# TOC prefab paths
toc_prefabs = {}
for dp, dn, fn in os.walk(ASSETS):
    if "toc.txt" not in fn:
        continue
    p = os.path.join(dp, "toc.txt")
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in re.finditer(r'"bundles/characters/merged/([^"]+)":\s*"([^"]+)"', txt):
        toc_prefabs.setdefault(m.group(1), []).append({
            "path": m.group(2), "toc": p.replace("\\", "/")})

# Portrait / dialogue / questboard files by token
asset_files = []
for dp, dn, fn in os.walk(ASSETS):
    for f in fn:
        asset_files.append(os.path.join(dp, f).replace("\\", "/"))

def files_for(token):
    t = token.lower()
    out = {"portrait_large": [], "portrait_small": [], "quest": [], "dialogue": [], "loading": []}
    for p in asset_files:
        n = os.path.basename(p).lower()
        if n == "portrait_%s_large.png" % t:
            out["portrait_large"].append(p)
        elif n == "portrait_%s_small.jpg" % t:
            out["portrait_small"].append(p)
        elif n == "portrait_%s_quest.png" % t:
            out["quest"].append(p)
        elif n in ("%s.png" % t, "sg_%s.png" % t):
            out["dialogue"].append(p)
        elif n in ("%s_fight.jpg" % t, "%s_fight.png" % t):
            out["loading"].append(p)
    return out

bios = {k[len("ID_CHARACTER_BIOS_"):]: k for k in loc if k.startswith("ID_CHARACTER_BIOS_")}
spec = {}
for k in loc:
    m = re.match(r"ID_SPECIAL_ATTACK_(DESCRIPTION_)?([A-Z0-9_]+)_(\d+)$", k)
    if m:
        spec.setdefault(m.group(2), {"names": [], "descriptions": []})
        if m.group(1):
            spec[m.group(2)]["descriptions"].append(k)
        else:
            spec[m.group(2)]["names"].append(k)

base_ids = sorted({k[:-3] if k.endswith("_lw") else k for k in chars})

alias_to_id = {}
for _cid, _aliases in MOVE_ALIAS.items():
    for _a in _aliases:
        alias_to_id[_a] = _cid
moves_by_id = {cid: [] for cid in base_ids}
for _key in moves:
    _rest = _key[5:] if _key.startswith("move_") else _key
    if _rest.startswith("fe_"):
        _rest = _rest[3:]
    for _a in sorted(alias_to_id, key=len, reverse=True):
        if _rest == _a or _rest.startswith(_a + "_"):
            moves_by_id[alias_to_id[_a]].append(_key)
            break

rows = []
for cid in base_ids:
    token = MAP.get(cid, "")
    ptoken = PORTRAIT_TOKEN.get(cid, token.lower())
    variants = sorted(k for k in chars if (k == cid or k == cid + "_lw"))
    prefabs = []
    for v in variants:
        prefabs.extend(toc_prefabs.get(v, []))
    # de-duplicate
    seen = set()
    prefabs = [p for p in prefabs if not (p["path"] in seen or seen.add(p["path"]))]
    move_names = sorted(moves_by_id.get(cid, []))
    special_moves = [m for m in move_names if "_special_" in m]
    if cid in ("starscream_gs", "optimusprime_gs_v"):
        bundle = inv.get("characters", {})
    else:
        bundle = inv.get(cid, {})
    gos = bundle.get("gameobjects", [])
    stem = cid.split("_")[0].lower()
    roots = [g for g in gos if stem in g.lower() and (g.endswith("_lw") or "_lw" not in g)][:20]
    clips = bundle.get("animation_clips", [])
    needles = {stem, cid.lower(), token.lower(), ptoken}
    if cid == "starscream_gs":
        needles |= {"starscream", "stars_gs"}
    if cid == "optimusprime_gs_v":
        needles |= {"optimus"}
    clip_match = [c for c in clips if any(p in c.lower() for p in needles)]
    bio_key = bios.get(token)
    spec_entry = spec.get(token, {"names": [], "descriptions": []})
    page = WIKI_EXTRA.get(cid) or (id_map.get(cid) or {}).get("wiki_page")
    w = wiki.get(page, {}) if page else {}
    cov = coverage.get(cid, {})
    der = derived.get(page, {}) if page else {}
    bp = blueprints.get(cid) or (patch.get("blueprints") or {}).get(cid) or {}
    ch = characters.get(cid) or (patch.get("characters") or {}).get(cid) or {}
    hero = roster.get(cid)
    art = files_for(ptoken)
    boss_quests = sorted(q for q, v in boss_map.items()
                         if (v.get("boss_client_id") == cid or v.get("fallback_client_id") == cid))
    rows.append({
        "id": cid,
        "display_name": ch.get("friendly_name") or ch.get("name") or (page or cid),
        "loc_token": token,
        "portrait_token": ptoken,
        "token_aliases": sorted(t for t, c in TOKEN_ALIASES.items() if c == cid),
        "variants": variants,
        "prefabs": prefabs,
        "bundle": bundle.get("path", ""),
        "bundle_bytes": bundle.get("bytes"),
        "object_types": bundle.get("types", {}),
        "root_candidates": roots,
        "animation_clips": clips,
        "animation_clips_matching": clip_match,
        "move_names": move_names,
        "special_moves": special_moves,
        "portrait_files": art,
        "bio_key": bio_key,
        "bio_present": bool(bio_key),
        "special_attack_names": sorted(spec_entry["names"]),
        "special_attack_descriptions": sorted(spec_entry["descriptions"]),
        "special_attack_present": bool(spec_entry["names"]),
        "wiki": {
            "page": page,
            "exists": bool(w),
            "class": (w.get("infobox") or {}).get("Class", ""),
            "faction": (w.get("infobox") or {}).get("Faction", ""),
            "release": (w.get("infobox") or {}).get("Release Date", ""),
            "level1_hp": cov.get("level1_hp"),
            "level1_attack": cov.get("level1_attack"),
            "stars": w.get("stars", {}),
        },
        "catalog": {
            "blueprint": bool(bp),
            "character": bool(ch),
            "in_roster": bool(hero),
            "class": bp.get("class"),
            "attribute_base_type": bp.get("attribute_base_type"),
            "rarity": bp.get("rarity"),
            "max_rank": bp.get("max_rank"),
        },
        "boss_quests": boss_quests,
        "labels": {
            "assets": "[STATIC]",
            "loc_token": "[STATIC]" if token else "[ASSUMED]",
            "wiki": "[WIKI]" if page else "[ASSUMED]",
            "catalog": "[RUN]" if bp or ch else "[ASSUMED]",
        },
        "notes": [],
    })

# Fix level1 from wiki 1/1 row when stat_coverage has no anchor.
for r in rows:
    if r["wiki"]["level1_hp"] is None and r["wiki"]["exists"]:
        for table in (wiki.get(r["wiki"]["page"], {}).get("stat_tables") or []):
            for row in table:
                if row and str(row[0]).strip() == "1/1" and len(row) >= 3:
                    try:
                        r["wiki"]["level1_hp"] = float(str(row[1]).replace(",", ""))
                        r["wiki"]["level1_attack"] = float(str(row[2]).replace(",", ""))
                    except Exception:
                        pass
                    break

# token table
bot_by_token = {r["loc_token"]: r["id"] for r in rows if r["loc_token"]}
bot_by_ptoken = {r["portrait_token"]: r["id"] for r in rows if r["portrait_token"]}
for _t, _cid in TOKEN_ALIASES.items():
    bot_by_token.setdefault(_t, _cid)
tokens = []
for t in sorted(set(bios) | set(spec) | set(bot_by_ptoken) | set(
        m.group(1) for m in (re.match(r"portrait_(.+)_(?:large\.png|small\.jpg)$", os.path.basename(p))
                             for p in asset_files) if m)):
    if t.startswith("Z_") or t == "HQ1":
        kind = "non_bot"
    elif t in TOKEN_ALIASES:
        kind = "bot_alias"
    elif t in bot_by_token:
        kind = "bot"
    elif t in bot_by_ptoken:
        kind = "bot_portrait_alias"
    else:
        kind = "unmatched"
    tokens.append({
        "token": t,
        "bot_id": bot_by_token.get(t) or bot_by_ptoken.get(t),
        "kind": kind,
        "bio_key": bios.get(t),
        "special_names": sorted((spec.get(t) or {}).get("names", [])),
        "special_descriptions": sorted((spec.get(t) or {}).get("descriptions", [])),
        "portrait_large": any(os.path.basename(p).lower() == "portrait_%s_large.png" % t.lower()
                              for p in asset_files),
        "portrait_small": any(os.path.basename(p).lower() == "portrait_%s_small.jpg" % t.lower()
                              for p in asset_files),
    })

# Missing-string bots: no exact loc token for names/descriptions.
missing_loc = [r["id"] for r in rows if not r["special_attack_present"]]
missing_bio = [r["id"] for r in rows if not r["bio_present"]]

census = {
    "source": "UnityPy 1.25.4 over work/unpacked/assets (toc, characters*.assetbundle, moves, portraits, localization_all)",
    "generated": "2026-10-30",
    "counts": {
        "base_characters": len(rows),
        "character_tokens_with_lw": len(chars),
        "lw_variants": sum(1 for k in chars if k.endswith("_lw")),
        "odr_bot_bundles": sum(1 for cid in base_ids
                               if os.path.exists(os.path.join(ASSETPACK, cid + "_odr", cid + ".assetbundle"))),
        "merged_only": [cid for cid in base_ids
                        if not os.path.exists(os.path.join(ASSETPACK, cid + "_odr", cid + ".assetbundle"))],
        "catalog_blueprints": len(bp_eff),
        "catalog_characters": len(chars_eff),
        "catalog_roster": len(roster_eff),
        "wiki_pages_matched": sum(1 for r in rows if r["wiki"]["exists"]),
        "loc_tokens_with_spec": sum(1 for r in rows if r["special_attack_present"]),
        "loc_tokens_missing_spec": missing_loc,
        "loc_tokens_missing_bio": missing_bio,
        "move_prefixes": len({a for v in MOVE_ALIAS.values() for a in v}),
        "move_textassets": len(moves),
        "boss_quests_with_client_id": sum(1 for q, v in boss_map.items() if v.get("boss_client_id")),
        "boss_quests_without_client_id": sum(1 for q, v in boss_map.items() if not v.get("boss_client_id")),
    },
    "characters": rows,
    "tokens": tokens,
    "unmatched_wiki_pages": ["Chromia", "Dead End", "Optimus Prime", "Soundblaster/Tactician"],
    "unmatched_wiki_reasons": {
        "Chromia": "[WIKI] page release 2023-05-10; no client asset/token/filename match for CHROMIA/CHROM in 9.2.0",
        "Dead End": "[WIKI] page release 2023-05-10; no client asset/token/filename match for DEADEND/DEAD END in 9.2.0",
        "Optimus Prime": "[WIKI] Tactician page; client model/token exists as optimusprime_gs_v / OPTIMUS_GS but it was absent from the 59-pack catalog",
        "Soundblaster/Tactician": "[WIKI] Tactician page; client has soundblaster_gs_mp13b (Demolitions) and SOUNDBLAST_GS portrait, no separate Tactician blueprint",
    },
    "notes": [
        "61 base character tokens = 59 ODR bundles + Starscream_GS and OptimusPrime_GS_V merged into characters.assetbundle.",
        "Each base token has exactly one _lw variant (122 tokens total).",
        "The localization token is not always the full asset id: Windblade=WINDB_GS, Starscream=STARS_GS, Bumblebee DOTM=BUMBL_C.",
        "7 bots have portraits but no ID_SPECIAL_ATTACK_/BIOS keys for their token: see counts.loc_tokens_missing_spec.",
        "The BOTS denominator must come from the effective catalog roster, not the 59 ODR directories.",
    ],
}

os.makedirs("data", exist_ok=True)
open("data/client_character_census.json", "w", encoding="utf-8").write(
    json.dumps(census, ensure_ascii=False, indent=1))
print("rows", len(rows), "tokens", len(tokens))
print("missing spec", missing_loc)
print("missing bio", missing_bio)
print("merged only", census["counts"]["merged_only"])
print("catalog", census["counts"]["catalog_blueprints"],
      census["counts"]["catalog_characters"], census["counts"]["catalog_roster"])
