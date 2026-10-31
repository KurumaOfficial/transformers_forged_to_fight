from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''                    aid = t.get("aid") or t.get("activityID") or qid
                    t["activityID"] = aid
                    t["estimatedExpire"] = t.get("expire", t.get("estimatedExpire", 0))
                    fixed[aid] = t
                wrapper["updates"]["activeTeams"] = fixed'''
new = '''                    aid = t.get("aid") or t.get("activityID") or qid
                    t["activityID"] = aid
                    t["estimatedExpire"] = t.get("expire", t.get("estimatedExpire", 0))
                    fixed[aid] = t
                    uid = qb.get("uniqueId") if isinstance(qb, dict) else None
                    if uid:
                        fixed[uid] = t
                wrapper["updates"]["activeTeams"] = fixed'''
if old not in s:
    raise SystemExit("marker not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("uniqueId alias patched")
