"""Resolve quest boss ids to real blueprint ids (1.3).

A boss id must be a key in `blueprints`; a character id alone (for example
`bumblebee_cin_dotm`) cannot be loaded as a blueprint.  Prefer an exact
blueprint, then `<id>_2`, then a blueprint whose `character` is the id.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "server" / "data"
CAT = json.loads((DATA / "bcg_login_data.json").read_text(encoding="utf-8"))
BP = CAT["blueprints"]
CH = CAT["characters"]
BOSSMAP = ROOT / "data" / "boss_map.json"
QL = DATA / "quest_list.json"
GAPS = ROOT / "data" / "boss_gaps.json"

by_character = {}
for bid, b in BP.items():
    c = b.get("character")
    if c:
        by_character.setdefault(c, []).append(bid)


def resolve(bid):
    if not bid:
        return None, "no boss id"
    if bid in BP:
        return bid, "exact blueprint"
    cand = bid + "_2"
    if cand in BP:
        return cand, "blueprint variant _2"
    c = by_character.get(bid) or []
    if len(c) == 1:
        return c[0], "blueprint by character id"
    return None, "no blueprint for id"


changed = []
bossmap = json.loads(BOSSMAP.read_text(encoding="utf-8"))
for qid, v in bossmap.items():
    old = v.get("boss_client_id")
    new, why = resolve(old)
    if new and new != old:
        v["boss_client_id"] = new
        v["reason"] = (v.get("reason") or "") + f"; fixed: {why} ({old} -> {new})"
        changed.append((qid, old, new, why))
    elif not new:
        v["reason"] = (v.get("reason") or "") + f"; unresolved: {why}"
BOSSMAP.write_text(json.dumps(bossmap, ensure_ascii=False, indent=1), encoding="utf-8")

sets = json.loads(QL.read_text(encoding="utf-8"))
patched = 0
for s in sets:
    for q in s.get("availableQuests", []):
        boss = q.get("finalBoss") or {}
        old = boss.get("id")
        new, why = resolve(old)
        if new and new != old:
            boss["id"] = new
            patched += 1
        elif old and not new:
            pass
QL.write_text(json.dumps(sets, ensure_ascii=False, indent=1), encoding="utf-8")

gaps = []
for qid, v in bossmap.items():
    if not v.get("boss_client_id") or v["boss_client_id"] not in BP:
        gaps.append({"qid": qid, "boss": v.get("boss"),
                     "boss_client_id": v.get("boss_client_id"),
                     "reason": v.get("reason")})
GAPS.write_text(json.dumps(gaps, ensure_ascii=False, indent=1), encoding="utf-8")

print("boss_map fixes", len(changed), "quest_list fixes", patched, "gaps", len(gaps))
for row in changed:
    print(" ", row)
for g in gaps:
    print(" GAP", g["qid"], g["boss"], g["reason"])
