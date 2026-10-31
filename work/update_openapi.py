import json
p = r'.\spec\openapi.json'
s = json.load(open(p, encoding='utf-8'))
s['info']['version'] = '0.2.0-partial'
s['info']['description'] += (' Partial: only endpoints observed in the live 2026-10-21 run and/or '
                             'verified in dump.cs. Quest wire keys are documented in spec/quest_protocol.md.')

def sparx(result_schema):
    return {
        "200": {
            "description": "Sparx envelope",
            "content": {"application/json": {"schema": {
                "type": "object",
                "required": ["ts", "result"],
                "properties": {
                    "ts": {"type": "integer"},
                    "result": result_schema,
                    "sync": {"type": "object"},
                    "async": {"type": "array"},
                    "error": {"type": ["string", "null"]},
                    "fatal": {"type": "boolean"},
                    "retry": {"type": "boolean"}
                }
            }}}
        }
    }

s['paths']['/quests/quest-detail/{qid}'] = {
    "post": {
        "summary": "Quest details",
        "x-verified": "RUN 2026-10-21",
        "parameters": [{"name": "qid", "in": "path", "required": True, "schema": {"type": "string"}}],
        "requestBody": {"required": True, "content": {"application/json": {"schema": {
            "type": "object",
            "required": ["hash", "setId"],
            "properties": {
                "hash": {"type": "string"},
                "setId": {"type": "string"},
                "api": {"type": "integer"},
                "nonce": {"type": "string"}
            }
        }}}},
        "responses": sparx({"type": "object", "required": ["summary", "map"], "properties": {
            "summary": {"type": "object"},
            "map": {"type": "object"}
        }})
    }
}
s['paths']['/quests/quest-begin/{qid}'] = {
    "post": {
        "summary": "Begin quest (NOT OBSERVED)",
        "x-verified": "NOT OBSERVED",
        "parameters": [{"name": "qid", "in": "path", "required": True, "schema": {"type": "string"}}],
        "responses": sparx({"type": "object"})
    }
}
s['paths']['/quests/quest-moveto/{qid}'] = {
    "post": {
        "summary": "Move on quest board (NOT OBSERVED)",
        "x-verified": "NOT OBSERVED",
        "parameters": [{"name": "qid", "in": "path", "required": True, "schema": {"type": "string"}}],
        "responses": sparx({"type": "object"})
    }
}
s['paths']['/matches/match-loaded/{matchType}/{id}'] = {
    "post": {
        "summary": "Signal match loaded (NOT OBSERVED)",
        "x-verified": "NOT OBSERVED",
        "responses": sparx({"type": "object"})
    }
}
s['paths']['/bcg/getUserData'] = {
    "get": {
        "summary": "User roster (NOT OBSERVED; schema experimental)",
        "x-verified": "NOT OBSERVED",
        "responses": sparx({"type": "object"})
    }
}
json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('paths', len(s['paths']))
