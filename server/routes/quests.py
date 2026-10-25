"""Quest response builders (T1 routing split, behavior unchanged)."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def _load(name, default=None):
    p = DATA / name
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def find_quest(qid):
    for qset in _load("quest_list.json", []):
        for quest in qset.get("availableQuests", []):
            if quest.get("id") == qid:
                return qset, quest
    return None, None


def scaled_boss(quest):
    boss = (quest or {}).get("finalBoss") or {}
    bid = boss.get("id")
    if not bid:
        return {}
    return {
        "enemy1": {
            "isFinalBoss": True,
            "characters": [bid],
            "rank": int(boss.get("rank", 1)),
            "level": int(boss.get("level", 1)),
            "sig_lvl": 0,
            "flvl": 0,
            "aiType": 1,
            "aiString": "default",
            "aiPer": "aggressive",
            "mapOverride": "",
            "todIndex": 0,
            "uid": "enemy1",
            "key": bid,
            "hi": [],
            "type": "boss",
            "baseType": "boss",
        }
    }


def build_detail(qid):
    qset, quest = find_quest(qid)
    if not quest:
        return _load("quest_detail.json")
    data = json.loads(json.dumps(_load("quest_detail.json")))
    data["summary"] = {
        "id": qid,
        "category": quest.get("category", "Story"),
        "friendlyName": quest.get("friendlyName", qid),
        "description": quest.get("description", ""),
        "isDetailed": True,
        "theme": quest.get("theme", "primordial"),
        "todIndex": quest.get("todIndex", 0),
        "energyPerTile": quest.get("energyPerTile", 1),
        "minXpPerTile": quest.get("minXpPerTile", 20),
        "maxXpPerTile": quest.get("maxXpPerTile", 50),
        "actIndex": quest.get("actIndex", 1),
        "chapterIndex": quest.get("chapterIndex", 1),
        "missionIndex": quest.get("missionIndex", 1),
        "act": quest.get("act", 1),
        "chapter": quest.get("chapter", 1),
        "mission": quest.get("mission", 1),
        "teamSizeMin": quest.get("teamSizeMin", 1),
        "teamSizeMax": quest.get("teamSizeMax", 1),
        "unlocked": True,
    }
    data["map"] = (qset.get("QuestMaps") or {}).get(qid) or data.get("map", {})
    data["scaledBossTable"] = scaled_boss(quest)
    return data


def build_begin(qid):
    qset, quest = find_quest(qid)
    if not quest:
        return _load("quest_begin_response.json")
    data = json.loads(json.dumps(_load("quest_begin_response.json")))
    data["qid"] = qid
    data["uniqueId"] = qid
    data["data"] = {
        "id": qid,
        "category": quest.get("category", "Story"),
        "friendlyName": quest.get("friendlyName", qid),
        "description": quest.get("description", ""),
        "isDetailed": True,
        "theme": quest.get("theme", "primordial"),
        "todIndex": quest.get("todIndex", 0),
        "energyPerTile": quest.get("energyPerTile", 1),
        "minXpPerTile": quest.get("minXpPerTile", 20),
        "maxXpPerTile": quest.get("maxXpPerTile", 50),
        "actIndex": quest.get("actIndex", 1),
        "chapterIndex": quest.get("chapterIndex", 1),
        "missionIndex": quest.get("missionIndex", 1),
        "act": quest.get("act", 1),
        "chapter": quest.get("chapter", 1),
        "mission": quest.get("mission", 1),
        "teamSizeMin": quest.get("teamSizeMin", 1),
        "teamSizeMax": quest.get("teamSizeMax", 1),
        "unlocked": True,
    }
    data["map"] = (qset.get("QuestMaps") or {}).get(qid) or data.get("map", {})
    data["scaledBossTable"] = scaled_boss(quest)
    data["progression"] = {
        "clearedTiles": [{"x": 0, "y": 0}],
        "currentTile": {"x": 0, "y": 0},
        "percentComplete": 0,
    }
    return data
