import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

# Find all Sparx classes
sparx_classes = [c for c in classes if "sparx" in c["full_name"].lower()]
print(f"Total Sparx classes: {len(sparx_classes)}")

# Group by category / service
services = [c for c in sparx_classes if "service" in c["full_name"].lower() or "manager" in c["full_name"].lower()]
print(f"\nSparx Services and Managers ({len(services)}):")
for s in sorted(services, key=lambda x: x["full_name"]):
    print(f"  {s['full_name']}")
    methods = [m for m in s["methods"] if not m.startswith("get_") and not m.startswith("set_")][:8]
    fields = s["fields"][:8]
    if methods:
        print(f"    Methods: {methods}")
    if fields:
        print(f"    Fields: {fields}")

# Check all non-Sparx Managers / Controllers / Services
print("\n=== Game Managers & Controllers ===")
game_mgrs = [c for c in classes if any(c["full_name"].endswith(suffix) for suffix in ["Manager", "Controller", "Service", "System", "Model"])]
print(f"Total Game Managers/Controllers: {len(game_mgrs)}")
for m in sorted([c["full_name"] for c in game_mgrs])[:40]:
    print(f"  {m}")
