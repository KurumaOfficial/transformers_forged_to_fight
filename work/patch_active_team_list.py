from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''            for t in wrapper["updates"].get("activeTeams", []):
                hv = t.get("heroes", {})
                if isinstance(hv, dict):
                    for h in hv.values():
                        fill_hp(h)
                elif isinstance(hv, list):
                    for h in hv:
                        fill_hp(h)
            qd = load_data_json("quest_detail.json")'''
new = '''            for t in wrapper["updates"].get("activeTeams", []):
                hv = t.get("heroes", {})
                if isinstance(hv, dict):
                    hv = list(hv.values())
                if isinstance(hv, list):
                    for h in hv:
                        fill_hp(h)
                    t["heroes"] = hv
                    t["teamHeroes"] = hv
                t["activityID"] = t.get("aid") or t.get("activityID") or qid
                t["estimatedExpire"] = t.get("expire", t.get("estimatedExpire", 0))
            qd = load_data_json("quest_detail.json")'''
if old not in s:
    raise SystemExit("marker not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("active team list patched")
