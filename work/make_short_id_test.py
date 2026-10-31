import copy
import json
from pathlib import Path

root = Path(".")
cat = json.loads((root / "server/data/bcg_login_data.json").read_text(encoding="utf-8"))
bp = copy.deepcopy(cat["blueprints"]["windblade_gs"])
bp["blueprint"] = "windb_gs_2"
bp["character"] = "windblade_gs"
bp["modelId"] = "windblade_gs"
bp["friendly_name"] = "Windblade"
bp["friendly_name_short"] = "Windblade"
bp["id"] = "windb_gs_2"
heroes = copy.deepcopy(cat["heroes"]["windblade_gs"])
for rank, h in heroes.items():
    h["blueprint"] = "windb_gs_2"
    h["id"] = "windb_gs_2"
roster = next(h for h in cat["userData"]["heroes"] if h.get("bid") == "windblade_gs")
roster = copy.deepcopy(roster)
roster["bid"] = "windb_gs_2"
roster["hero"] = "windb_gs_2"
roster["blueprint"] = "windb_gs_2"
patch = {
    "reason": "test whether short loc-token blueprint ids are the client's real key (Windblade = WINDB_GS)",
    "blueprints": {"windb_gs_2": bp},
    "heroes": {"windb_gs_2": heroes},
    "replace_roster": {"windblade_gs": roster},
}
(root / "server/data/short_id_test.json").write_text(
    json.dumps(patch, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", len(json.dumps(patch)))
