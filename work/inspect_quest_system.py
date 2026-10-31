import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

# Find Quest classes
quest_classes = [c for c in classes if "quest" in c["full_name"].lower()]
print(f"Total quest classes: {len(quest_classes)}")

# Group by important quest managers/models
for c in sorted(quest_classes, key=lambda x: x["full_name"]):
    fn = c["full_name"]
    fn_lower = fn.lower()
    if any(k in fn_lower for k in ["manager", "model", "data", "map", "node", "board", "act", "chapter", "enemy", "summary", "service"]):
        print(f"\nClass: {fn}")
        methods = [m for m in c["methods"] if not m.startswith("get_") and not m.startswith("set_")][:8]
        fields = c["fields"][:10]
        if methods:
            print(f"  Methods: {methods}")
        if fields:
            print(f"  Fields: {fields}")
