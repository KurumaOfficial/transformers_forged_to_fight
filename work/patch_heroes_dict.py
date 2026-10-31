from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''            ats = wrapper["updates"].get("activeTeams", [])
            if isinstance(ats, list):
                fixed = {}
                for t in ats:
                    hv = t.get("heroes", {})
                    if isinstance(hv, dict):
                        hv = list(hv.values())
                    if isinstance(hv, list):
                        for h in hv:
                            fill_hp(h)
                        t["heroes"] = hv
                        t["teamHeroes"] = hv
                    aid = t.get("aid") or t.get("activityID") or qid
                    t["activityID"] = aid
                    t["estimatedExpire"] = t.get("expire", t.get("estimatedExpire", 0))
                    fixed[aid] = t
                wrapper["updates"]["activeTeams"] = fixed
            elif isinstance(ats, dict):
                for t in ats.values():
                    hv = t.get("heroes", {})
                    if isinstance(hv, dict):
                        hv = list(hv.values())
                    if isinstance(hv, list):
                        for h in hv:
                            fill_hp(h)
                        t["heroes"] = hv
                        t["teamHeroes"] = hv
            qd = load_data_json("quest_detail.json")'''
new = '''            ats = wrapper["updates"].get("activeTeams", [])
            if isinstance(ats, list):
                fixed = {}
                for t in ats:
                    hv = t.get("heroes", {})
                    if isinstance(hv, dict):
                        for h in hv.values():
                            fill_hp(h)
                    elif isinstance(hv, list):
                        for h in hv:
                            fill_hp(h)
                    aid = t.get("aid") or t.get("activityID") or qid
                    t["activityID"] = aid
                    t["estimatedExpire"] = t.get("expire", t.get("estimatedExpire", 0))
                    fixed[aid] = t
                wrapper["updates"]["activeTeams"] = fixed
            elif isinstance(ats, dict):
                for t in ats.values():
                    hv = t.get("heroes", {})
                    if isinstance(hv, dict):
                        for h in hv.values():
                            fill_hp(h)
                    elif isinstance(hv, list):
                        for h in hv:
                            fill_hp(h)
            qd = load_data_json("quest_detail.json")'''
if old not in s:
    raise SystemExit("marker not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("heroes dict restored")
