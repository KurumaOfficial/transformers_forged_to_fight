import json
from pathlib import Path

p = Path("spec/openapi.json")
d = json.loads(p.read_text(encoding="utf-8"))
op = d["paths"]["/levelrewards/fetch"]["get"]
op["x-client-behavior"] = (
    "Documented from static code; the verified client flow did not request "
    "this path. LevelRewardsManager.Connect reads levelrewards from login data "
    "if present."
)
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("updated")
