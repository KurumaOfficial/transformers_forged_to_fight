import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

# Find all classes related to combat calculation, fight resolution, and damage
combat_keywords = ["combat", "battle", "fight", "damage", "health", "hit", "attack", "buff", "stat"]

results = []
for c in classes:
    fn = c["full_name"]
    fn_lower = fn.lower()
    if any(k in fn_lower for k in combat_keywords):
        # filter out UI / View classes
        if not any(skip in fn_lower for skip in ["view", "widget", "ui", "hud", "popup", "panel", "screen", "button", "label", "icon"]):
            results.append(c)

print(f"Total core combat classes (excluding UI): {len(results)}")
for c in sorted(results, key=lambda x: x["full_name"])[:40]:
    print(f"\n{c['full_name']}")
    methods = [m for m in c["methods"] if not m.startswith("get_") and not m.startswith("set_")][:6]
    fields = [f for f in c["fields"]][:8]
    if methods:
        print(f"  Methods: {methods}")
    if fields:
        print(f"  Fields: {fields}")
