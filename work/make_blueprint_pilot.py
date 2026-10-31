import copy
import json
from pathlib import Path

root = Path(".")
cat = json.loads((root / "server/data/bcg_login_data.json").read_text(encoding="utf-8"))
old = "windblade_gs"
new = "windb_gs_5"
bp = copy.deepcopy(cat["blueprints"][old])
bp["blueprint"] = new
bp["id"] = new
# Character/model keep the asset id.
bp["character"] = old
bp["modelId"] = old
heroes = copy.deepcopy(cat["heroes"][old])
for rank, h in heroes.items():
    h["blueprint"] = new
    h["id"] = new
roster = next(h for h in cat["userData"]["heroes"] if h.get("bid") == old)
roster = copy.deepcopy(roster)
roster["bid"] = new
roster["hero"] = new
roster["blueprint"] = new
pilot = {
    "reason": "pilot: blueprint id must be <loc_token>_<suffix>; keep asset ModelID",
    "rename": {old: new},
    "blueprints": {new: bp},
    "heroes": {new: heroes},
    "roster": roster,
}
(root / "server/data/blueprint_pilot.json").write_text(
    json.dumps(pilot, ensure_ascii=False, indent=1), encoding="utf-8")
print("pilot", old, "->", new, "bytes", len(json.dumps(pilot)))
