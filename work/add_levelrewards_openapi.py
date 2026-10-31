import json
from pathlib import Path

p = Path(r".\spec\openapi.json")
d = json.loads(p.read_text(encoding="utf-8"))
paths = d["paths"]
paths["/levelrewards/fetch"] = {
    "get": {
        "summary": "Level rewards status",
        "description": (
            "Documents the statically found endpoint. `LevelRewardsAPI.FetchStatus` "
            "(0x1271694) uses `/levelrewards/fetch`; `LevelRewardsManager.Connect` "
            "(0x12733A0) also reads `user.levelrewards` directly from the login user. "
            "The current stub does not serve this path because the client has not "
            "requested it in the verified flow."
        ),
        "x-evidence": "[STATIC] metadata string index 1298; RVA 0x1271694, 0x12733A0",
        "x-implementation": "not implemented; login user carries levelrewards",
        "responses": {
            "200": {
                "description": "Sparx envelope [STATIC]",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "ts": {"type": "integer"},
                                "result": {
                                    "type": "object",
                                    "properties": {
                                        "levelrewards": {
                                            "type": "object",
                                            "properties": {
                                                "level": {"type": "integer"},
                                                "types": {"type": "array", "items": {}},
                                            },
                                        },
                                        "levelrewards_milestones": {
                                            "type": "array", "items": {}
                                        },
                                    },
                                },
                            },
                        }
                    }
                },
            }
        },
    }
}
# Document the login-user field that drives the home LVL / level locks.
login = paths.get("/auth/login", {}).get("post", {})
if login:
    login["description"] = (
        "Login response. The `user.levelrewards` object is read by "
        "LevelRewardsManager.Connect (0x12733A0); `level` drives the home LVL "
        "text and LevelLockManager (STORE level lock)."
    )
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("added /levelrewards/fetch; paths", len(paths))
