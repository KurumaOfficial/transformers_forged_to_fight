from pathlib import Path
import json
p = Path(r"C:\Users\gameg\Desktop\TFTF\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''            if team:
                quest["team"] = team'''
new = '''            if team:
                quest["team"] = {
                    bid: {"hp": 1000.0, "pi": 100, "sig_lvl": 0, "stat_mods": [], "sig_mods": []}
                    for bid in team
                }'''
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
q = Path(r"C:\Users\gameg\Desktop\TFTF\server\data\quest_begin_response.json")
d = json.loads(q.read_text(encoding="utf-8"))
if isinstance(d.get("team"), list):
    d["team"] = {
        bid: {"hp": 1000.0, "pi": 100, "sig_lvl": 0, "stat_mods": [], "sig_mods": []}
        for bid in d["team"]
    }
q.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("team dicts:", d.get("team"))
