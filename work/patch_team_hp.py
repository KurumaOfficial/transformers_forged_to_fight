from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''            wrapper = rebase(wrapper)
            qd = load_data_json("quest_detail.json")'''
new = '''            wrapper = rebase(wrapper)
            def fill_hp(h):
                if isinstance(h, dict):
                    h["hp"] = 1000.0
                    h["pi"] = 100
                    h.setdefault("sig_lvl", 0)
                    h.setdefault("stat_mods", [])
                    h.setdefault("sig_mods", [])
            for h in wrapper["updates"].get("heroes", []):
                fill_hp(h)
            for t in wrapper["updates"].get("activeTeams", []):
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
print("hp patched")
