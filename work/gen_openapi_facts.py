import json

RUN = "[RUN] observed 2026-10-21 21:23-21:24 UTC"
STATIC = "[STATIC] dump.cs / stringliterals"
ASSUMED = "[ASSUMED] stub value, not original"

def envelope(result_schema, evidence, client_behavior, result_desc):
    return {
        "post" if False else "get": {
            "summary": "",
            "x-evidence": evidence,
            "x-client-behavior": client_behavior,
            "responses": {
                "200": {
                    "description": "Sparx envelope. " + evidence,
                    "content": {"application/json": {"schema": {
                        "type": "object",
                        "required": ["ts", "result"],
                        "properties": {
                            "ts": {"type": "integer", "description": "server epoch seconds " + RUN},
                            "result": dict(result_schema, description=result_desc),
                            "sync": {"type": "object", "nullable": True,
                                     "description": "[ASSUMED] not used by the verified client flow; Response has no sync field " + STATIC},
                            "async": {"type": "array", "items": {}, "nullable": True,
                                      "description": "[STATIC] EB.Sparx.Response.async"},
                            "error": {"type": "string", "nullable": True,
                                      "description": "[STATIC] error string or null"},
                            "fatal": {"type": "boolean", "description": "[STATIC] fatal flag"},
                            "retry": {"type": "boolean", "description": "[STATIC] retry flag"}
                        }
                    }}}
                }
            }
        }
    }

def get(path, summary, result_schema, evidence, behavior, result_desc):
    op = envelope(result_schema, evidence, behavior, result_desc)["get"]
    op["summary"] = summary
    return {path: {"get": op}}

def post(path, summary, result_schema, evidence, behavior, result_desc, request_schema=None):
    op = envelope(result_schema, evidence, behavior, result_desc)["get"]
    op["summary"] = summary
    if request_schema:
        op["requestBody"] = {"required": False, "content": {"application/json": {"schema": request_schema}}}
    return {path: {"post": op}}

empty = {"type": "object", "properties": {}}
arr = {"type": "array", "items": {}}

paths = {}
paths.update(get("/auth/init", "Initialize anonymous session", empty, RUN,
                 "session must be non-empty; client proceeds to enumerate",
                 "status/session object; fields [ASSUMED]"))
paths.update(post("/auth/init", "Initialize anonymous session (observed POST too)", empty, RUN,
                  "same as GET; POST observed in later run", "status/session object; [ASSUMED]"))
paths.update(post("/auth/enumerate", "Enumerate device accounts", arr, RUN + "; " + STATIC,
                  "empty array is accepted; client falls through to prelogin/login",
                  "array; empty [] confirmed"))
paths.update(post("/auth/prelogin", "Pre-login salt/challenge", {
    "type": "object", "properties": {
        "salt": {"type": "string", "description": "empty salt skips APK_Check_Start_Salt " + RUN},
        "status": {"type": "string", "description": ASSUMED}
    }}, RUN, "empty salt -> no apkprotect HMAC path", "salt/status"))
paths.update(post("/auth/login", "Login with device authenticator", {
    "type": "object", "properties": {
        "token": {"type": "string", "description": ASSUMED},
        "stoken": {"type": "string", "description": RUN + " session token used by later calls"},
        "auth": {"type": "object", "description": "must contain device:true " + RUN,
                 "properties": {"device": {"type": "boolean"}}},
        "endpoints": {"type": "object", "description": RUN + " service endpoint map"},
        "user": {"type": "object", "description": ASSUMED},
        "modeData": {"type": "object", "description": ASSUMED}
    }}, RUN, "missing auth.device or stoken -> login failure", "login payload; most values [ASSUMED]"))
paths.update(get("/account/data", "Commander profile", {
    "type": "object", "properties": {
        "user": {"type": "object", "description": "uid/name/level/xp; values " + ASSUMED},
        "privacySettings": {"type": "object", "description": "[RUN] required by InvitesManager",
                            "properties": {"friendsinvite": {"type": "boolean"}}},
        "invitesDB": {"type": "object", "description": "[RUN] required"},
        "maxHelpsPerRequest": {"type": "integer", "description": "[RUN] required"},
        "xlate2Resources": {"type": "object", "description": ASSUMED}
    }}, RUN, "missing privacySettings/invitesDB -> NullReferenceException", "profile object; values [ASSUMED]"))
paths.update(get("/bcg/getLoginData", "BCG catalog + optional userData", {
    "type": "object", "properties": {
        "heroes": {"type": "object", "description": "[RUN] catalog accepted; values " + ASSUMED},
        "blueprints": {"type": "object", "description": "[RUN] catalog accepted; values " + ASSUMED},
        "characters": {"type": "object", "description": "[RUN] catalog accepted; values " + ASSUMED},
        "evoBlueprints": {"type": "object", "description": "[RUN] required"},
        "attributeGrowthDefs": {"type": "object", "description": "[RUN] required"},
        "statMods": {"type": "object", "description": "[RUN] required"},
        "statModAppears": {"type": "object", "description": "[RUN] required"},
        "synergyBonuses": {"type": "object", "description": "[RUN] required"},
        "attackValues": {"type": "object", "description": "[RUN] required"},
        "blueprintBonuses": {"type": "object", "description": "[RUN] required"},
        "heroClasses": {"type": "object", "description": "[RUN] required"},
        "curves": {"type": "object", "description": "[RUN] required"},
        "evoCosts": {"type": "object", "description": "[RUN] required"},
        "rarityProperties": {"type": "object", "description": "[RUN] required"},
        "staminaRegen": {"type": "object", "description": "[RUN] required"},
        "userData": {"type": "object", "description": "[STATIC] top-level key read by OnBCGData; exact shape not yet accepted. [ASSUMED]"},
        "cdn": {"type": "string", "description": ASSUMED}
    }}, RUN + "; " + STATIC, "missing required collections -> alerts/NullRef; userData roster still empty [RUN]",
    "catalog + userData; only key names verified, values [ASSUMED]"))
paths.update(get("/tuning", "Combat tuning", {"type": "object", "description": ASSUMED}, RUN,
                 "client falls back to built-in defaults if empty", "tuning dict; values [ASSUMED]"))
paths.update(get("/payments/payouts", "Payment payouts", empty, RUN, "shop hides paid offers", "empty object [ASSUMED]"))
paths.update(get("/performance/profile", "Graphics profile", {"type": "object", "description": ASSUMED}, RUN,
                 "client selects a default profile", "profile dict; [ASSUMED]"))
paths.update(get("/redeemer/refresh", "Redeemer gifts", empty, RUN, "promo section empty", "empty [ASSUMED]"))
paths.update(get("/events/refresh", "Events", empty, RUN, "events tab empty", "empty [ASSUMED]"))
paths.update(get("/offers/getLoginData", "Offers", empty, RUN, "offer showcase empty", "empty [ASSUMED]"))
paths.update(get("/gamestats/get-login-data", "Game stats", {"type": "object", "properties": {
    "stats": {"type": "object", "description": ASSUMED},
    "achievements": {"type": "object", "description": ASSUMED}
}}, RUN, "stats/achievements empty", "stats object; [ASSUMED]"))
paths.update(get("/gamestats/check-login-achievements", "Achievement check", arr, RUN,
                 "empty array accepted", "array [ASSUMED]"))
paths.update(get("/push/token", "Push token", {"type": "object", "properties": {
    "status": {"type": "string", "description": ASSUMED},
    "websocket": {"type": "string", "description": ASSUMED}
}}, RUN, "push disabled if empty", "status/websocket; [ASSUMED]"))
paths.update(get("/inventory", "Inventory", {"type": "object", "properties": {
    "items": {"type": "array", "items": {}, "description": ASSUMED}
}}, RUN, "empty inventory accepted", "items array; [ASSUMED]"))
paths.update(get("/chat/data", "Chat channels", empty, RUN, "chat disabled/empty", "empty [ASSUMED]"))
paths.update(get("/base/active", "Player base", {
    "type": "object", "properties": {
        "user": {"type": "object", "description": "[RUN] wrapper observed; Base/map required",
                 "properties": {"Base": {"type": "object", "description": "[RUN] required by BaseManager"}}},
        "userBase": {"type": "object", "description": "[RUN] alternative wrapper"},
        "map": {"type": "object", "description": "[RUN] pathData required",
                "properties": {"pathData": {"type": "array", "description": "[RUN] must be non-empty",
                                            "items": {"type": "object", "properties": {
                                                "path": {"type": "array", "items": {"type": "object", "properties": {
                                                    "x": {"type": "integer"}, "y": {"type": "integer"}}}}}}}}}
    }}, RUN + "; " + STATIC, "missing pathData -> NullReferenceException in PathAnalyzer", "base mission; values [ASSUMED]"))
paths.update(get("/pvp/get-login-data", "PvP season", empty, RUN, "arena unavailable", "empty [ASSUMED]"))
paths.update(get("/autorefresh/grouprefresh", "Background refresh", empty, RUN,
                 "polled every ~20s; empty accepted", "empty [ASSUMED]"))
for sub in ["gacha", "gamestore", "objectives", "prizes", "message", "kabamsignup",
            "missionsconfig", "ads", "quests", "ave", "raid", "ai"]:
    paths.update(get(f"/autorefresh/{sub}/refresh", f"AutoRefresh {sub}", {
        "type": "object", "properties": {
            "check": {"type": "string", "description": ASSUMED},
            "refresh": {"type": "integer", "description": ASSUMED},
            "cache": {"type": "boolean", "description": ASSUMED}
        }}, RUN, "client re-polls; empty accepted", "refresh object; [ASSUMED]"))
paths.update(get("/ds/{uid}/", "DataSync profile", {"type": "object", "description": ASSUMED}, RUN,
                 "client sends profile on exit; empty accepted", "profile dict; [ASSUMED]"))
paths.update(post("/ds/{uid}", "DataSync profile (POST observed)", {"type": "object", "description": ASSUMED}, RUN,
                  "client sends profile JSON; empty accepted", "profile dict; [ASSUMED]"))
paths.update(post("/tutorial/get-login-data", "Tutorial login data", {
    "type": "object", "description": "[RUN] keyed by tutorial id; each has s/current_bid",
    "additionalProperties": {"type": "object", "properties": {
        "s": {"type": "string", "description": "[RUN] 'completed' bypass"},
        "current_bid": {"type": "string", "description": "[RUN] branch id"}
    }}
}, RUN, "all completed -> no tutorial modal; deviation DEV-001", "tutorial map; bypass [RUN]"))
paths.update(post("/tutorial/{action}", "Tutorial action", {"type": "object", "description": ASSUMED}, RUN,
                  "completed branch returned", "tutorial state; [ASSUMED]"))
paths.update(get("/quests/quest-list", "Available quest sets", arr, RUN + "; " + STATIC,
                 "array; set keys and summary act/chapter/mission verified; values invented",
                 "array of sets; schema in spec/quest_protocol.md"))
paths.update(get("/quests/quest-active", "Active quests", {
    "type": "object", "properties": {
        "activeQuests": {"type": "array", "items": {}},
        "instances": {"type": "array", "items": {}}
    }}, RUN, "empty accepted; active quest not verified", "active quests; [ASSUMED]"))
paths.update(get("/quests/quest-progression", "Quest progression", {
    "type": "object", "description": "[STATIC] keyed by category, then quest id; values [ASSUMED]"
}, RUN + "; " + STATIC, "applied to QuestSummary.UpdateProgression", "progression map; [ASSUMED]"))
paths.update(post("/quests/quest-detail/{qid}", "Quest details", {
    "type": "object", "required": ["summary", "map"],
    "properties": {"summary": {"type": "object", "description": RUN},
                   "map": {"type": "object", "description": RUN}}
}, RUN, "client sends {hash,nonce,api,setId}; screen renders; team empty -> START disabled",
   "summary/map; values [ASSUMED]", {
       "type": "object", "required": ["hash", "setId"],
       "properties": {"hash": {"type": "string"}, "setId": {"type": "string"},
                      "api": {"type": "integer"}, "nonce": {"type": "string"}}
   }))
paths.update(post("/quests/quest-begin/{qid}", "Begin quest", {"type": "object"}, "[NOT OBSERVED]",
                  "not called: roster empty", "unknown"))
paths.update(post("/quests/quest-moveto/{qid}", "Move on board", {"type": "object"}, "[NOT OBSERVED]",
                  "not called", "unknown"))
paths.update(post("/matches/activate-match/{matchType}", "Activate match", {"type": "object"}, "[NOT OBSERVED]",
                  "not called", "unknown"))
paths.update(post("/matches/match-loaded/{matchType}/{id}", "Match loaded", {"type": "object"}, "[NOT OBSERVED]",
                  "not called", "unknown"))
paths.update(post("/matches/resolve-match/{matchType}", "Resolve match", {"type": "object"}, "[NOT OBSERVED]",
                  "not called", "unknown"))
paths.update(get("/bcg/getUserData", "User roster", {"type": "object"}, "[NOT OBSERVED]",
                  "not requested on boot or edit squad; BOTS crashes before fetch", "unknown; experimental"))
paths.update(post("/userprofile/", "User profile", empty, RUN, "profile card refresh", "empty [ASSUMED]"))
paths.update(post("/telemetry", "Telemetry", empty, RUN, "client ignores response", "empty [ASSUMED]"))
paths.update(post("/util/ping", "Ping", empty, "[RUN] earlier runs", "keepalive", "empty [ASSUMED]"))
paths.update(post("/krash", "Crash report", {"type": "object", "properties": {
    "status": {"type": "string"}, "id": {"type": "string"}
}}, RUN, "client posts crash JSON; response ignored", "status/id [ASSUMED]"))
paths.update(post("/bugs", "Bug report", empty, RUN, "client posts bug report; ignored", "empty [ASSUMED]"))
paths.update(get("/health", "Health check", empty, "[RUN] debug", "manual test only", "empty"))
paths.update(get("/ws", "WebSocket upgrade", {"type": "string"}, "[RUN] debug; 400",
                  "client retries; not required for hub", "not implemented"))

spec = {
    "openapi": "3.0.3",
    "info": {
        "title": "Transformers: Forged to Fight 9.2.0 — observed Sparx protocol",
        "version": "0.3.0-facts",
        "description": (
            "FACT-ONLY partial specification. Every path has x-evidence; every "
            "non-obvious field carries [RUN]/[STATIC]/[ASSUMED] in its description. "
            "The 9 unittest cases check internal consistency (envelope, array shapes, "
            "required keys) and DO NOT prove client compatibility. Client compatibility "
            "is proven only by a live run with server/requests.jsonl + logcat. "
            "Quest schema: spec/quest_protocol.md. Coverage matrix: docs/protocol_coverage.md."
        )
    },
    "servers": [{"url": "http://127.0.0.1:8080"}],
    "tags": [{"name": "observed"}, {"name": "not-observed"}],
    "paths": paths
}
json.dump(spec, open(r".\spec\openapi.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("paths", len(paths))
