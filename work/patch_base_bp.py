from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''                "deletes": {}
            }
            qd = load_data_json("quest_detail.json")'''
new = '''                "deletes": {}
            }
            # The prefight asset database is keyed by the base blueprint id.
            # The roster uses a synthetic _2 id; rebase only the battle teamData.
            base_bp = "bumblebee_cin_dotm"
            def rebase(obj):
                if isinstance(obj, dict):
                    return {(base_bp if k == "bumblebee_cin_dotm_2" else k): rebase(v)
                            for k, v in obj.items()}
                if isinstance(obj, list):
                    return [rebase(v) for v in obj]
                if obj == "bumblebee_cin_dotm_2":
                    return base_bp
                return obj
            wrapper = rebase(wrapper)
            qd = load_data_json("quest_detail.json")'''
if old not in s:
    raise SystemExit("marker not found")
s = s.replace(old, new)
s = s.replace('''                "strongestHero": "bumblebee_cin_dotm_2",''', '''                "strongestHero": base_bp,''')
s = s.replace('''                "team": {
                    "bumblebee_cin_dotm_2": {''', '''                "team": {
                    base_bp: {''')
p.write_text(s, encoding="utf-8")
print("base blueprint patched")
