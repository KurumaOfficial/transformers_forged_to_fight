from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''                "team": [{
                    "id": "bumblebee_cin_dotm_2",
                    "bid": "bumblebee_cin_dotm_2",
                    "hero": "bumblebee_cin_dotm_2",
                    "level": 1,
                    "rank": 1,
                    "sig_lvl": 0,
                    "flvl": 0
                }]'''
new = '''                "team": {
                    "bumblebee_cin_dotm_2": {
                        "hp": 1000.0,
                        "pi": 100,
                        "sig_lvl": 0,
                        "stat_mods": [],
                        "sig_mods": []
                    }
                }'''
if old not in s:
    raise SystemExit("team block not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("team dict patched")
