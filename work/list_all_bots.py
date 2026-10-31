import os
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

unpacked = r".\work\unpacked\assets"

# 1. Collect from assetpack folders ending with _odr
bot_folders = [d for d in os.listdir(os.path.join(unpacked, "assetpack")) if any(x in d for x in ["_gs_", "_cin_", "_bw_", "sharkticon"])]

# 2. Collect from portraits in portraits_odr
portraits_dir = os.path.join(unpacked, "assetpack", "portraits_odr")
portrait_files = []
if os.path.exists(portraits_dir):
    for root, dirs, files in os.walk(portraits_dir):
        for f in files:
            if f.endswith(".png") or f.endswith(".assetbundle"):
                portrait_files.append(f)

# 3. Collect from dialogue_odr
dialogue_dir = os.path.join(unpacked, "assetpack", "dialogue_odr")
dialogue_files = []
if os.path.exists(dialogue_dir):
    for root, dirs, files in os.walk(dialogue_dir):
        for f in files:
            if f.endswith(".png"):
                dialogue_files.append(f)

print(f"Bot 3D model assetpacks: {len(bot_folders)}")
for bf in sorted(bot_folders):
    print(f"  {bf}")

print(f"\nDialogue character avatars: {len(dialogue_files)}")
for df in sorted(dialogue_files):
    print(f"  {df}")
