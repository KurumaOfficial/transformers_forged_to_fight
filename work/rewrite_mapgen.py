import json
from pathlib import Path

p = Path(r".\work\build_quest_list_full.py")
s = p.read_text(encoding="utf-8")
start = s.index("def make_map(")
end = s.index("def quest_obj(", start)
new = '''def make_map(qid, act, chapter, mission, boss_id):
    """Deterministic map: static 9-tile template + per-qid hash/boss.

    The client's MapTile.Deserialize is strict about the 9-tile graph; the
    template is the already-validated 1.1 map. Layout is [ASSUMED].
    """
    template = json.loads((ROOT / "server" / "data" / "quest_detail.json").read_text(encoding="utf-8"))["map"]
    out = json.loads(json.dumps(template))
    out["mapHash"] = f"{qid}_map"
    for row in out["grid"]:
        for tile in row:
            if tile.get("final"):
                tile["entities"] = ([{
                    "id": boss_id,
                    "hero": boss_id,
                    "level": 1,
                    "rank": 1,
                    "team": "enemy",
                    "ai": "default",
                }] if boss_id else [])
            else:
                tile.pop("entities", None)
    return out


'''
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("rewrote make_map")
