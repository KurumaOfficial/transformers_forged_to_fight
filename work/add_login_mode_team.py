import json
from pathlib import Path
p = Path(r"C:\Users\gameg\Desktop\TFTF\server\data\bcg_login_data.json")
d = json.loads(p.read_text(encoding="utf-8"))
u = d.setdefault("userData", {})
ats = u.setdefault("activeTeams", [])
base = next((t for t in ats if isinstance(t, dict) and t.get("aid") == "story_act1_ch1_m1"), None)
if base:
    mode_team = json.loads(json.dumps(base))
    mode_team["aid"] = "story"
    mode_team["activityID"] = "story"
    ats[:] = [t for t in ats if t.get("aid") != "story"]
    ats.append(mode_team)
    for t in ats:
        for h in (t.get("heroes") or {}).values():
            h.setdefault("blueprint", h.get("bid", ""))
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("activeTeams:", [t.get("aid") for t in ats])
