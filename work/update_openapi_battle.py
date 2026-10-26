import json
from pathlib import Path

p = Path("spec/openapi.json")
d = json.loads(p.read_text(encoding="utf-8"))
paths = d["paths"]

act = paths["/matches/activate-match/{matchType}"]["post"]
act["summary"] = "Activate match (quest fight)"
act["x-evidence"] = "[RUN]"
act["x-client-behavior"] = (
    "POST /matches/activate-match/quests_fight after FIGHT; body "
    "{hero,qid,battleId}. The client then loads the battle scene."
)
act["requestBody"] = {
    "required": True,
    "content": {"application/json": {"schema": {
        "type": "object",
        "properties": {
            "hero": {"type": "string", "example": "bumblebee_cin_dotm_2"},
            "qid": {"type": "string", "example": "story_act1_ch4_m2"},
            "battleId": {"type": "string", "example": "battle1"},
            "api": {"type": "integer", "example": 3},
            "nonce": {"type": "string"},
        },
    }}},
}
act["responses"]["200"]["description"] = (
    "Sparx envelope. [RUN] request captured; result body is [ASSUMED] "
    "match_activate_response.json (matchId/matchType/seed/fighterData)."
)

ml = paths["/matches/match-loaded/{matchType}/{id}"]["post"]
ml["summary"] = "Match loaded (not sent for quests_fight)"
ml["x-evidence"] = "[RUN: not observed]"
ml["x-client-behavior"] = (
    "Not sent in the verified quest fight. Whether it is PvP-only is open; "
    "the smoke battle_checks keep it as an open xfail."
)

rm = paths["/matches/resolve-match/{matchType}"]["post"]
rm["summary"] = "Resolve match (blocked by ODR/loading)"
rm["x-evidence"] = "[BLOCKED]"
rm["x-client-behavior"] = (
    "Not reached: FuseLoadingScreen/FuseODRBlocker remains above HudScreen "
    "because Play Asset Delivery is unavailable on the emulator."
)

p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("updated paths")
