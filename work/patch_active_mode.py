from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''                    uid = load_data_json("quest_begin_response.json").get("uniqueId")
                    if uid:
                        fixed[uid] = t
                wrapper["updates"]["activeTeams"] = fixed'''
new = '''                    qbegin = load_data_json("quest_begin_response.json")
                    uid = qbegin.get("uniqueId")
                    if uid:
                        fixed[uid] = t
                    mode_key = qbegin.get("mode")
                    if mode_key:
                        fixed[mode_key] = t
                wrapper["updates"]["activeTeams"] = fixed'''
if old not in s:
    raise SystemExit("marker not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("mode key patched")
