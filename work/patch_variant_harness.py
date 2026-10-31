from pathlib import Path
p = Path(r".\work\run_variant.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    if "login_active_teams" in v:
        ats = json.loads(json.dumps(v["login_active_teams"]))''', '''    if "login_active_teams" in v:
        supplied = v["login_active_teams"]
        ats = json.loads(json.dumps(list(supplied.values()) if isinstance(supplied, dict) else supplied))''')
s = s.replace('''            for h in hv.values():
                if isinstance(h, dict):
                    h.update(v.get("hero_extra") or {})
            t["heroes"] = hv''', '''            for h in hv.values():
                if isinstance(h, dict):
                    h.update(v.get("hero_extra") or {})
            t["heroes"] = hv
        if v.get("heroes_list") and isinstance(t.get("heroes"), dict):
            t["heroes"] = list(t["heroes"].values())''')
p.write_text(s, encoding="utf-8")
print("patched harness")
