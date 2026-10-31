import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

with open(r".\work\string_literals.txt", "r", encoding="utf-8") as f:
    literals = f.readlines()

def print_class_info(name):
    matches = [c for c in classes if c["full_name"] == name or c["full_name"].endswith("." + name)]
    for c in matches:
        print(f"\n==========================================")
        print(f"CLASS: {c['full_name']} (Image: {c['image']})")
        print(f"METHODS ({len(c['methods'])}):")
        for m in c["methods"][:25]:
            print(f"  {m}")
        print(f"FIELDS ({len(c['fields'])}):")
        for f in c["fields"][:25]:
            print(f"  {f}")

target_classes = [
    "EB.Sparx.TuningManager",
    "EB.Sparx.LoginManager",
    "CharacterDamageManager",
    "AIController",
    "CombatManager",
    "FightManager",
    "QuestManager",
    "RosterManager",
    "GameModel",
    "GameConfig",
    "CombatEngine"
]

for tc in target_classes:
    print_class_info(tc)
