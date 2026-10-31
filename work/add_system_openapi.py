import json
from pathlib import Path

p = Path("spec/openapi.json")
d = json.loads(p.read_text(encoding="utf-8"))
paths = d["paths"]
paths["/gacha/store"] = {
    "get": {
        "summary": "Gacha store (static endpoint)",
        "description": "Static endpoint found in string literals; no client request observed on the empty CRYSTALS screen.",
        "x-evidence": "[STATIC] string literal /gacha/store",
        "x-implementation": "not implemented",
        "responses": {"200": {"description": "Sparx envelope [ASSUMED]"}},
    }
}
paths["/gacha/pick"] = {
    "post": {
        "summary": "Gacha pick (static endpoint)",
        "description": "GachaAPI.PickFromBox 0xF66AFC; request/response keys not captured.",
        "x-evidence": "[STATIC] string literal /gacha/pick",
        "x-implementation": "not implemented",
        "responses": {"200": {"description": "Sparx envelope [ASSUMED]"}},
    }
}
paths["/gacha/getOdds"] = {
    "get": {
        "summary": "Gacha odds (static endpoint)",
        "description": "GachaAPI.GetGachaOdds 0xF670EC; odds schema not captured.",
        "x-evidence": "[STATIC] string literal /gacha/getOdds",
        "x-implementation": "not implemented",
        "responses": {"200": {"description": "Sparx envelope [ASSUMED]"}},
    }
}
paths["/objectives"] = {
    "get": {
        "summary": "Objectives list (static endpoint)",
        "description": "OBJECTIVES screen opens with [0/0]; server payload empty.",
        "x-evidence": "[RUN] screen, [STATIC] string literal /objectives",
        "x-implementation": "empty",
        "responses": {"200": {"description": "Sparx envelope [ASSUMED]"}},
    }
}
paths["/store/{type}"] = {
    "get": {
        "summary": "Store (static endpoint)",
        "description": "STORE is client level-locked at LEVEL 2; item/price schema not captured.",
        "x-evidence": "[RUN] level lock, [STATIC] string literal /store/:type",
        "x-implementation": "not implemented",
        "parameters": [{"name": "type", "in": "path", "required": True, "schema": {"type": "string"}}],
        "responses": {"200": {"description": "Sparx envelope [ASSUMED]"}},
    }
}
for _path in ("/gacha/store", "/gacha/pick", "/gacha/getOdds", "/objectives", "/store/{type}"):
    _op = paths[_path].get("get") or paths[_path].get("post")
    _op.setdefault("x-client-behavior", "Static endpoint; not observed on the wire in the verified flow.")
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("paths", len(paths))
