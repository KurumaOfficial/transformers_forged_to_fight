import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

# Find combat core classes
exact_names = [
    "PlayerController", "CombatPlayer", "CharacterModel", "CharacterState",
    "CombatManager", "FightManager", "FightModel", "FightResult",
    "DamageCalculator", "CombatAttributes", "HitData", "HitReaction",
    "BuffManager", "BuffEffect", "MoveSequencer", "MoveData",
    "ActionManager", "ActionSequencer", "CombatEngine", "BattleEngine"
]

for name in exact_names:
    matches = [c for c in classes if c["full_name"] == name or c["full_name"].endswith("." + name)]
    for c in matches:
        print(f"\n==========================================")
        print(f"CLASS: {c['full_name']}")
        methods = [m for m in c["methods"] if not m.startswith("get_") and not m.startswith("set_")]
        fields = [f for f in c["fields"]]
        print(f"  Methods ({len(methods)}): {methods[:15]}")
        print(f"  Fields ({len(fields)}): {fields[:15]}")

calc_classes = [c for c in classes if any(k in c["full_name"].lower() for k in ["calc", "formula", "attribute", "damage", "health"])]
print(f"\nCalculator / Formula / Attribute classes: {len(calc_classes)}")
for c in calc_classes[:30]:
    print(f"  {c['full_name']} (Methods: {len(c['methods'])}, Fields: {len(c['fields'])})")
