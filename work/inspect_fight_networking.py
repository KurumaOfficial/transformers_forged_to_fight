import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

with open(r".\work\string_literals.txt", "r", encoding="utf-8") as f:
    literals = f.readlines()

# Search for classes with Fight in name
fight_classes = [c for c in classes if "fight" in c["full_name"].lower() or "battle" in c["full_name"].lower()]
print(f"Total fight/battle classes: {len(fight_classes)}")

# Look for Fight controllers / models / managers
for c in fight_classes:
    fn = c["full_name"]
    fn_lower = fn.lower()
    if any(k in fn_lower for k in ["manager", "controller", "service", "model", "result", "network", "api", "data", "rpc"]):
        print(f"\nClass: {fn}")
        methods = [m for m in c["methods"] if not m.startswith("get_") and not m.startswith("set_")]
        fields = c["fields"]
        print(f"  Methods ({len(methods)}): {methods[:10]}")
        print(f"  Fields ({len(fields)}): {fields[:10]}")

# Look in string literals for fight RPC calls
print("\n=== Fight related string literals ===")
fight_lits = [l.strip() for l in literals if any(k in l.lower() for k in ["startfight", "endfight", "finishfight", "fightresult", "combatresult", "battle/start", "battle/end", "quest/fight", "pvp/fight"])]
print(f"Fight literals count: {len(fight_lits)}")
for fl in fight_lits[:30]:
    print(f"  {fl}")
