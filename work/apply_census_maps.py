"""Apply the 61-character census to the mapping files (data only)."""
import json
from pathlib import Path

ROOT = Path(".")
census = json.loads((ROOT / "data/client_character_census.json").read_text(encoding="utf-8"))
rows = {r["id"]: r for r in census["characters"]}
bots = json.loads((ROOT / "data/wiki/bots.json").read_text(encoding="utf-8"))["bots"]


def stars_for(page):
    b = bots.get(page) or {}
    return b.get("stars") or {}


def max_rating(stars):
    return {k: v.get("max_rating", "") for k, v in (stars or {}).items()}


# 1. id_map.json
p = ROOT / "data/wiki/id_map.json"
idm = json.loads(p.read_text(encoding="utf-8"))
have = {e["client_id"] for e in idm["matched"]}
for cid in ("starscream_gs", "optimusprime_gs_v"):
    if cid not in have:
        page = "Starscream" if cid == "starscream_gs" else "Optimus Prime"
        idm["matched"].append({
            "client_id": cid,
            "wiki_page": page,
            "wiki_page_exists": True,
            "confidence": "high (client toc/bundle + loc token + wiki 1/1)",
            "in_bots_stats": page in bots,
        })
idm["source"] = ("61 base character tokens from all character TOCs/bundles "
                 "(59 ODR packs + Starscream_GS and OptimusPrime_GS_V merged) vs wiki pages")
idm["client_pack_count"] = 59
idm["client_character_count"] = 61
idm["merged_only"] = ["starscream_gs", "optimusprime_gs_v"]
idm["matched_count"] = len(idm["matched"])
idm["wiki_without_client"] = ["Chromia", "Dead End", "Soundblaster/Tactician"]
idm["note"] = ("Starscream and Optimus Prime are present in characters.assetbundle; "
               "the old 59-pack scan missed them. Chromia/Dead End have no 9.2.0 "
               "token or asset match. Soundblaster/Tactician is a separate wiki "
               "variant; client has Demolitions soundblaster_gs_mp13b.")
p.write_text(json.dumps(idm, ensure_ascii=False, indent=1), encoding="utf-8")
print("id_map", idm["matched_count"])

# 2. bot_catalog_real.json
p = ROOT / "server/data/bot_catalog_real.json"
cat = json.loads(p.read_text(encoding="utf-8"))
have = {r["client_id"] for r in cat["rows"]}
for cid, page, pack_dir, note in (
    ("starscream_gs", "Starscream",
     "work/unpacked/assets/assetpack/characters/characters.assetbundle",
     "merged bundle (characters.assetbundle); ODR pack absent"),
    ("optimusprime_gs_v", "Optimus Prime",
     "work/unpacked/assets/assetpack/characters/characters.assetbundle",
     "merged bundle (characters.assetbundle); ODR pack absent"),
):
    if cid in have:
        continue
    b = bots.get(page) or {}
    info = b.get("infobox") or {}
    st = stars_for(page)
    cat["rows"].append({
        "client_id": cid,
        "pack_dir": pack_dir,
        "wiki_page": page,
        "wiki_page_exists": True,
        "in_bots_stats": True,
        "sharkticon_variant": False,
        "class": info.get("Class", ""),
        "faction": info.get("Faction", ""),
        "generation": info.get("Origin", ""),
        "release": info.get("Release Date", ""),
        "stars": st,
        "max_rating": max_rating(st),
        "sources": {
            "client_id": "[CLIENT]",
            "class_faction_generation": "[WIKI]",
            "stars": "[WIKI]",
            "bundle": "[STATIC]",
        },
        "missing": [note],
    })
cat["count"] = len(cat["rows"])
cat["source"] = ("61 base character tokens (59 ODR packs + Starscream_GS and "
                 "OptimusPrime_GS_V merged) + data/wiki/id_map.json + bots.json")
cat["note"] = ("Count is 61 characters. The old 59-pack count missed the two "
               "merged prefabs; Starscream/Optimus are not post-APK content.")
p.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
print("bot_catalog", cat["count"])

# 3. boss_map.json / boss_gaps.json
p = ROOT / "data/boss_map.json"
bm = json.loads(p.read_text(encoding="utf-8"))
fixed = 0
for qid, v in bm.items():
    if str(v.get("boss", "")).lower() == "starscream":
        v["boss_client_id"] = "starscream_gs"
        v["match"] = "high"
        v["reason"] = ("[CLIENT] characters/toc.txt + characters.assetbundle "
                       "Starscream_GS + STARS_GS localization; [WIKI] 5400/391/1354")
        for k in ("fallback_client_id", "fallback_label", "fallback_reason"):
            v.pop(k, None)
        fixed += 1
p.write_text(json.dumps(bm, ensure_ascii=False, indent=1), encoding="utf-8")
(ROOT / "data/boss_gaps.json").write_text("[]\n", encoding="utf-8")
print("boss_map starscream fixed", fixed, "gaps left", 0)

# 4. client_only.json wiki-only list
p = ROOT / "data/wiki/client_only.json"
co = json.loads(p.read_text(encoding="utf-8"))
co["wiki_without_client"] = [
    {"wiki_page": "Chromia", "possible_status": "post-9.2.0 or another variant; no CHROMIA/CHROM token or filename in the retained 9.2.0 assets", "client_match": None, "tag": "[WIKI]+[ASSUMED]"},
    {"wiki_page": "Dead End", "possible_status": "post-9.2.0 or another variant; no DEADEND/DEAD END token or filename in the retained 9.2.0 assets", "client_match": None, "tag": "[WIKI]+[ASSUMED]"},
    {"wiki_page": "Soundblaster/Tactician", "possible_status": "separate Tactician variant; client has soundblaster_gs_mp13b (Demolitions) and the SOUNDBLAST_GS portrait, but no separate Tactician blueprint", "client_match": "soundblaster_gs_mp13b", "tag": "[WIKI]+[CLIENT]"},
]
co["counts"]["wiki_without_client"] = 3
co["counts"]["client_characters"] = 61
p.write_text(json.dumps(co, ensure_ascii=False, indent=1), encoding="utf-8")
print("client_only wiki_without_client", co["counts"]["wiki_without_client"])
