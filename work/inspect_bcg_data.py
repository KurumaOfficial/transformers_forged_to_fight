import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

# Find BCG classes and HeroData classes
bcg_classes = [c for c in classes if "bcg" in c["full_name"].lower() or "hero" in c["full_name"].lower() or "botdata" in c["full_name"].lower()]

print(f"Total BCG / Hero classes: {len(bcg_classes)}")
for c in bcg_classes:
    fn = c["full_name"]
    if any(k in fn.lower() for k in ["data", "model", "info", "manager", "service", "config"]):
        print(f"\nClass: {fn}")
        methods = [m for m in c["methods"] if not m.startswith("get_") and not m.startswith("set_")][:6]
        fields = c["fields"]
        if methods:
            print(f"  Methods: {methods}")
        if fields:
            print(f"  Fields: {fields}")
