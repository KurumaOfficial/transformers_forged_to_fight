import os
import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

unpacked_dir = r".\work\unpacked"

# Categories
# 1. Bot Models & Prefabs (Unity AssetBundles for bots, characters.assetbundle)
# 2. Animations (character_anim_procedural, etc.)
# 3. Audio & Music (character_audio, sound assetbundles)
# 4. Arenas & Environments (chicago, hongkong, karnak, mine, primordial, ruinedcity, rust, unicron, base)
# 5. UI & 2D Graphics (portraits, dialogue avatars, UI bundles, sprites, upgrade items)
# 6. Localization & Text (chinesesimplified, chinesetraditional, Data text/json assets)
# 7. VFX & Shaders (character_fx, character_fx_procedural, frontendfx)
# 8. Base & Buildings & Relics (buildings_odr, towers_odr, relics_odr, chests_odr)
# 9. Quest & Gameboard (assets_quest_odr, assets_quest_fte_odr, questboard_odr)
# 10. Engine & Code (classes.dex, classes2.dex, libil2cpp.so, libunity.so, global-metadata.dat, etc.)
# 11. Configuration & Manifests (packs.txt, supplierconfig.json, toc.txt, manifest_main.mbin, AndroidManifest.xml)
# 12. Other / Uncategorized

categories = {
    "Bot 3D Models & Roster": {"count": 0, "size": 0, "examples": []},
    "Animations": {"count": 0, "size": 0, "examples": []},
    "Audio & SFX": {"count": 0, "size": 0, "examples": []},
    "Arenas & Battle Stages": {"count": 0, "size": 0, "examples": []},
    "UI, Icons & Portraits": {"count": 0, "size": 0, "examples": []},
    "Localization & Strings": {"count": 0, "size": 0, "examples": []},
    "VFX & Shaders": {"count": 0, "size": 0, "examples": []},
    "Base, Towers & Relics": {"count": 0, "size": 0, "examples": []},
    "Quests & Gameboards": {"count": 0, "size": 0, "examples": []},
    "Code & Native Binaries": {"count": 0, "size": 0, "examples": []},
    "Configs & Manifests": {"count": 0, "size": 0, "examples": []},
    "Unity Engine Data": {"count": 0, "size": 0, "examples": []},
    "Android Resources & Other": {"count": 0, "size": 0, "examples": []}
}

for root, dirs, files in os.walk(unpacked_dir):
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, unpacked_dir).replace("\\", "/")
        rel_l = rel.lower()
        sz = os.path.getsize(fp)
        
        cat = "Android Resources & Other"
        
        if rel_l.endswith((".so", ".dex")) or "global-metadata.dat" in rel_l:
            cat = "Code & Native Binaries"
        elif rel_l.endswith((".xml", ".json", ".txt", ".mbin", "billing.properties")) or "toc.txt" in rel_l:
            cat = "Configs & Manifests"
        elif "anim" in rel_l or "matinee" in rel_l:
            cat = "Animations"
        elif "audio" in rel_l or rel_l.endswith((".wav", ".mp3", ".ogg")):
            cat = "Audio & SFX"
        elif any(ar in rel_l for ar in ["chicago", "hongkong", "karnak", "mine", "primordial", "ruinedcity", "rust", "unicron", "assets/assetpack/base/"]):
            cat = "Arenas & Battle Stages"
        elif any(k in rel_l for k in ["portrait", "dialogue", "upgradeitems", "redeemers", "ui", "fightlanding", "gacha"]):
            cat = "UI, Icons & Portraits"
        elif any(k in rel_l for k in ["chinesesimplified", "chinesetraditional"]) or ("assets/bin/data/" in rel_l and sz < 500*1024):
            cat = "Localization & Strings"
        elif any(k in rel_l for k in ["character_fx", "frontendfx", "characters_fx"]):
            cat = "VFX & Shaders"
        elif any(k in rel_l for k in ["building", "tower", "relic", "chest"]):
            cat = "Base, Towers & Relics"
        elif any(k in rel_l for k in ["quest", "questboard"]):
            cat = "Quests & Gameboards"
        elif any(k in rel_l for k in ["_gs_", "_cin_", "_bw_", "sharkticon", "characters.assetbundle", "moves.assetbundle"]):
            cat = "Bot 3D Models & Roster"
        elif "assets/bin/data/" in rel_l:
            cat = "Unity Engine Data"
            
        categories[cat]["count"] += 1
        categories[cat]["size"] += sz
        if len(categories[cat]["examples"]) < 3:
            categories[cat]["examples"].append(rel)

print(f"{'Category':30s} | {'Files':6s} | {'Size (MB)':10s} | {'Status in APK':15s}")
print("-" * 75)

report_rows = []
for cat, data in categories.items():
    sz_mb = data["size"] / (1024 * 1024)
    # Determine presence status
    status = "Полностью в APK"
    if cat in ["Localization & Strings"]:
        status = "Частично (тексты есть, серверные таблицы отсутствуют)"
    elif cat in ["Quests & Gameboards"]:
        status = "Частично (ассетборды есть, серверные карты отсутствуют)"
    elif cat in ["Base, Towers & Relics"]:
        status = "Частично (модели есть, серверные конфиги отсутствуют)"
        
    print(f"{cat:30s} | {data['count']:6d} | {sz_mb:10.2f} | {status:15s}")
    report_rows.append({
        "Category": cat,
        "FileCount": data["count"],
        "TotalSizeBytes": data["size"],
        "TotalSizeMB": f"{sz_mb:.2f}",
        "StatusInAPK": status,
        "SampleFiles": "; ".join(data["examples"][:2])
    })

# Write CSV to report/inventory.csv
out_csv = r".\report\inventory.csv"
with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Category", "FileCount", "TotalSizeBytes", "TotalSizeMB", "StatusInAPK", "SampleFiles"])
    writer.writeheader()
    writer.writerows(report_rows)

print(f"\nSaved {out_csv} successfully!")
