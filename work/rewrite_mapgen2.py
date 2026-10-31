from pathlib import Path

p = Path(r".\work\build_quest_list_full.py")
s = p.read_text(encoding="utf-8")
start = s.index("def make_map(")
end = s.index("def quest_obj(", start)
new = '''def make_map(qid, act, chapter, mission, boss_id):
    # exact validated template; only the hash changes for now
    template = json.loads((ROOT / "server" / "data" / "quest_detail.json").read_text(encoding="utf-8"))["map"]
    out = json.loads(json.dumps(template))
    out["mapHash"] = f"{qid}_map"
    return out


'''
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("template exact")
