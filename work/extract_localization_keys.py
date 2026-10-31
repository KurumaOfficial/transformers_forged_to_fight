import os
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

data_dir = r".\work\unpacked\assets\bin\Data"

# Scan for English localization asset in Data/
# Let's find files that contain ID_CHARACTER_BIOS or ID_UI_ or D_STAT_
loc_keys = {}

for f in os.listdir(data_dir):
    fp = os.path.join(data_dir, f)
    if os.path.isfile(fp) and f not in ["global-metadata.dat", "sharedassets0.resource", "unity default resources", "globalgamemanagers"]:
        try:
            with open(fp, "rb") as fh:
                data = fh.read()
            if b"ID_CHARACTER_BIOS" in data or b"D_STAT_" in data:
                print(f"Found localization/stat data file: {f} ({len(data)} bytes)")
                # extract all JSON objects
                for m in re.finditer(rb'\{[^{}]*\"k\"\s*:\s*\"([^\"]+)\"[^{}]*\"v\"\s*:\s*\"([^\"]*)\"[^{}]*\}', data):
                    k = m.group(1).decode('utf-8', errors='ignore')
                    v = m.group(2).decode('utf-8', errors='ignore')
                    loc_keys[k] = (f, v)
        except:
            pass

print(f"\nTotal unique localization/stat keys extracted: {len(loc_keys)}")

categories = {
    "Bot Bios": [k for k in loc_keys if "ID_CHARACTER_BIOS" in k or "ID_BIO_" in k],
    "Bot Abilities & Stats": [k for k in loc_keys if "D_STAT_" in k or "ID_STAT_" in k or "ABILITY" in k or "SYNERGY" in k or "SIGNATURE" in k],
    "Story & Missions": [k for k in loc_keys if re.match(r'ID_S\d+_', k) or "QUEST" in k or "MISSION" in k or "CAMPAIGN" in k],
    "Masteries & Buffs": [k for k in loc_keys if "MASTERY" in k or "BUFF" in k],
    "Items & Economy": [k for k in loc_keys if "ITEM" in k or "ORE" in k or "CRYSTAL" in k or "ENERGON" in k or "REWARD" in k],
    "Tutorials": [k for k in loc_keys if "TUT" in k or "FTE" in k],
    "UI & General": [k for k in loc_keys if "ID_UI_" in k]
}

for cat, keys in categories.items():
    print(f"  {cat:25s}: {len(keys)} entries")
    if keys:
        print(f"    Sample: {keys[:3]}")
