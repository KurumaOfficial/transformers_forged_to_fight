import os
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

unpacked = r".\work\unpacked\assets"

# Check assets_quest_fte_odr
toc_fte = os.path.join(unpacked, "assets_quest_fte_odr", "toc.txt")
if os.path.exists(toc_fte):
    with open(toc_fte, "r") as f:
        print(f.read())

# Check all string literals for FTE / tutorial quest IDs or names
with open(r".\work\string_literals.txt", "r", encoding="utf-8") as f:
    literals = f.readlines()

fte_lits = [l.strip() for l in literals if any(k in l.lower() for k in ["fte", "tutorial", "act1", "act_01", "act_1", "chapter_1", "quest_01", "quest_1", "pve_"])]
print(f"\nFTE / Quest literals: {len(fte_lits)}")
for l in fte_lits[:35]:
    print(f"  {l}")
