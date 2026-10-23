import json
from pathlib import Path
p = Path(r"C:\Users\gameg\Desktop\TFTF\spec\openapi.json")
d = json.loads(p.read_text(encoding="utf-8"))

def envelope(result, desc):
    return {
        "type": "object", "required": ["ts", "result"],
        "properties": {
            "ts": {"type": "integer", "description": "server epoch seconds [RUN] 2026-10-23"},
            "result": dict(result, description=desc),
            "sync": {"type": "object", "nullable": True, "description": "[ASSUMED] unused by verified flow"},
            "async": {"type": "array", "items": {}, "nullable": True, "description": "[STATIC] EB.Sparx.Response.async"},
            "error": {"type": "string", "nullable": True},
            "fatal": {"type": "boolean"},
            "retry": {"type": "boolean"},
        },
    }

begin_result = {
    "type": "object",
    "properties": {
        "uniqueId": {"type": "string", "description": "[RUN] active_quest_1001"},
        "qid": {"type": "string", "description": "[RUN] story_act1_ch1_m1"},
        "category": {"type": "string"}, "mode": {"type": "string", "description": "[RUN] story"},
        "phase": {"type": "integer"}, "isFinished": {"type": "boolean"},
        "startTime": {"type": "integer"}, "expiryTime": {"type": "integer"},
        "team": {"type": "object", "description": "[RUN] blueprint -> {hp,pi,sig_lvl,stat_mods,sig_mods}"},
        "currentPosition": {"type": "object"}, "playerPosition": {"type": "object"},
        "data": {"type": "object"}, "map": {"type": "object"},
        "progression": {"type": "object"}, "scaledBossTable": {"type": "object"},
    },
}
move_result = {
    "type": "object",
    "properties": {
        "progression": {"type": "object", "description": "[RUN] currentPos/cleared/currentBattleId/localPlayer"},
        "currentPosition": {"type": "object"}, "playerPosition": {"type": "object"},
        "currentTile": {"type": "object"},
        "results": {"type": "array", "items": {"type": "object"}, "description": "[RUN] QuestActionResult list; battle opens prefight"},
        "teamData": {"type": "object", "description": "[RUN] BCG userData wrapper; activeTeams dict"},
    },
}
d["paths"]["/quests/quest-begin/{qid}"] = {
    "post": {
        "summary": "Begin/resume quest",
        "x-evidence": "[RUN] 2026-10-23",
        "x-client-behavior": "body tm0..tm3; result activeQuests[qid].teamData updates BCG userData",
        "requestBody": {"required": False, "content": {"application/json": {"schema": {"type": "object", "properties": {
            "tm0": {"type": "string"}, "tm1": {"type": "string"}, "tm2": {"type": "string"}, "tm3": {"type": "string"},
            "api": {"type": "string"}, "nonce": {"type": "string"}}}}}},
        "responses": {"200": {"description": "Sparx envelope [RUN]", "content": {"application/json": {"schema": envelope(begin_result, "quest-begin result; values from stub [RUN]")}}}},
    }
}
d["paths"]["/quests/quest-movedir/{qid}/{x}/{y}"] = {
    "post": {
        "summary": "Move on quest map",
        "x-evidence": "[RUN] 2026-10-23",
        "x-client-behavior": "client sends {}; result.results[] drives movement/battle; progression.localPlayer read by map/prefight",
        "parameters": [
            {"name": "qid", "in": "path", "required": True, "schema": {"type": "string"}},
            {"name": "x", "in": "path", "required": True, "schema": {"type": "integer"}},
            {"name": "y", "in": "path", "required": True, "schema": {"type": "integer"}},
        ],
        "responses": {"200": {"description": "Sparx envelope [RUN]", "content": {"application/json": {"schema": envelope(move_result, "movedir result; values from stub [RUN]")}}}},
    }
}
# Mark the existing detail operation observed.
det = d["paths"].get("/quests/quest-detail/{qid}", {})
if "post" in det:
    det["post"]["x-evidence"] = "[RUN] 2026-10-23"
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("openapi paths", len(d["paths"]))
