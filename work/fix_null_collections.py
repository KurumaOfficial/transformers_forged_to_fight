"""Null-safe blueprint collections (1.2 root-cause fix).

`DamageType..ctor(List<string>)` tail-calls `HashSet<string>..ctor(collection)`;
a null `Blueprint.BaseRangedDamageType` therefore throws
`ArgumentNullException("collection")` with `PlayerAttributes.Init` as the
visible caller (tail call). Ensure both damage-type lists are always present.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "server" / "data" / "bcg_login_data.json"
data = json.loads(CAT.read_text(encoding="utf-8"))
changed = 0
for bid, bp in data.get("blueprints", {}).items():
    if not isinstance(bp, dict):
        continue
    melee = bp.get("base_damage")
    if not isinstance(melee, list):
        melee = ["energy"]
        bp["base_damage"] = melee
        changed += 1
    ranged = bp.get("base_ranged_damage")
    if not isinstance(ranged, list):
        # Use the first melee damage type so the HashSet has a valid entry;
        # the exact ranged type is a later fidelity question.
        ranged = list(melee) or ["energy"]
        bp["base_ranged_damage"] = ranged
        changed += 1
    bp.setdefault("baseRangedDamageType", list(ranged))
    bp.setdefault("synergy_bonuses", [])
    bp.setdefault("synergyBonuses", [])
    bp.setdefault("tags", list(bp.get("t") or []))
    bp.setdefault("t", list(bp.get("tags") or []))
for cid, ch in data.get("characters", {}).items():
    if isinstance(ch, dict):
        ch.setdefault("tags", [])
        ch.setdefault("t", [])
CAT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("changed", changed)
for bid in ("bumblebee_cin_dotm_2", "sideswipe_gs", "rhinox_gs_voyager2014"):
    bp = data["blueprints"][bid]
    print(bid, "base_damage", bp["base_damage"], "base_ranged_damage", bp["base_ranged_damage"])
