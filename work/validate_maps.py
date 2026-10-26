"""Validate every quest map against the safe 3x3 template rules."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QL = ROOT / "server" / "data" / "quest_list.json"
OUT = ROOT / "data" / "map_validation.json"
sets = json.loads(QL.read_text(encoding="utf-8"))
errors = []
count = 0
for qs in sets:
    maps = qs.get("QuestMaps") or {}
    for qid, m in maps.items():
        count += 1
        errs = []
        n = m.get("gridDimension")
        grid = m.get("grid") or []
        if n != 3:
            errs.append(f"gridDimension={n}")
        if len(grid) != 3 or any(len(row) != 3 for row in grid):
            errs.append("grid is not 3x3")
        tiles = [t for row in grid for t in row]
        if len(tiles) != 9:
            errs.append(f"tiles={len(tiles)}")
        walk = sum(1 for t in tiles if t.get("walkable"))
        if walk != m.get("walkableCount"):
            errs.append(f"walkableCount {m.get('walkableCount')} != {walk}")
        starts = finals = 0
        for y, row in enumerate(grid):
            for x, t in enumerate(row):
                pos = t.get("position") or {}
                if pos.get("x") != x or pos.get("y") != y:
                    errs.append(f"tile {x},{y} position {pos}")
                if t.get("start"):
                    starts += 1
                if t.get("final"):
                    finals += 1
                for l in t.get("links") or []:
                    lx, ly = l.get("x"), l.get("y")
                    if not (isinstance(lx, int) and isinstance(ly, int)
                            and 0 <= lx < 3 and 0 <= ly < 3):
                        errs.append(f"tile {x},{y} bad link {l}")
        if starts != 1:
            errs.append(f"starts={starts}")
        if finals != 1:
            errs.append(f"finals={finals}")
        if errs:
            errors.append({"qid": qid, "errors": errs})
OUT.write_text(json.dumps({"maps": count, "errors": errors}, ensure_ascii=False, indent=1),
               encoding="utf-8")
print("maps", count, "errors", len(errors))
for e in errors[:20]:
    print(e)
