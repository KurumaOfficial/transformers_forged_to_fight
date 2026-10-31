from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''            def fill_hp(h):
                if isinstance(h, dict):
                    h["hp"] = 1000.0
                    h["pi"] = 100
                    h.setdefault("sig_lvl", 0)
                    h.setdefault("stat_mods", [])
                    h.setdefault("sig_mods", [])
'''
new = '''            def fill_hp(h):
                if isinstance(h, dict):
                    h["hp"] = 1000.0
                    h["max_hp"] = 1000.0
                    h["pi"] = 100
                    h.setdefault("sig_lvl", 0)
                    h.setdefault("stat_mods", [])
                    h.setdefault("sig_mods", [])
                    h.setdefault("blueprint", h.get("bid") or h.get("id") or h.get("hero") or "")
                    h.setdefault("rank", 1)
                    h.setdefault("level", 1)
'''
if old not in s:
    raise SystemExit("fill_hp marker not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("blueprint fields patched")
