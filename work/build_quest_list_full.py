"""Q1/Q2/Q3: build a full quest list (66 Story + 24 Awaken) with deterministic maps.

Source: data/quests_real.json (latest). Rewards and map layouts are [ASSUMED];
names and boss ids are [WIKI]/[CLIENT].
"""
import json
import re
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
REAL = ROOT / "data" / "quests_real.json"
BASE = ROOT / "server" / "data" / "quest_list.json"
OUT = ROOT / "server" / "data" / "quest_list.json"


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s or "mission"


def make_map(qid, act, chapter, mission, boss_id):
    """Deterministic 3x3 serpentine map. Layout is [ASSUMED]."""
    path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]
    grid = []
    for y in range(3):
        row = []
        for x in range(3):
            links = []
            if (x, y) in path:
                i = path.index((x, y))
                if i + 1 < len(path):
                    links.append({"x": path[i + 1][0], "y": path[i + 1][1]})
            tile = {
                "position": {"x": x, "y": y},
                "start": (x, y) == path[0],
                "final": (x, y) == path[-1],
                "walkable": (x, y) in path,
                "links": links,
                "visibleLinks": links,
                "sockets": {},
            }
            if (x, y) == path[-1]:
                tile["bt"] = [boss_id] if boss_id else []
                tile["entities"] = ([{
                    "id": boss_id,
                    "hero": boss_id,
                    "level": 1,
                    "rank": 1,
                    "team": "enemy",
                    "ai": "default",
                }] if boss_id else [])
            row.append(tile)
        grid.append(row)
    return {
        "mapHash": f"{qid}_map",
        "gridDimension": 3,
        "walkableCount": len(path),
        "visibleWalkableCount": len(path),
        "grid": grid,
        "pathData": [{"path": [{"x": x, "y": y} for x, y in path],
                      "tiles": [{"x": x, "y": y} for x, y in path]}],
        "paths": [{"path": [{"x": x, "y": y} for x, y in path],
                   "tiles": [{"x": x, "y": y} for x, y in path]}],
    }


def quest_obj(qid, category, act, chapter, mission, title, boss_name, boss_id):
    return {
        "id": qid,
        "category": category,
        "isDetailed": False,
        "actIndex": act,
        "chapterIndex": chapter,
        "missionIndex": mission,
        "unlocked": True,
        "alwaysLocked": False,
        "minLevel": 0,
        "minCL": 0,
        "completed": False,
        "mastered": False,
        "friendlyName": f"{act}.{chapter} {title}" if category == "Story" else f"{chapter}.{mission} {title}",
        "description": f"Face {boss_name}." if boss_name else "Continue the mission.",
        "theme": "primordial",
        "todIndex": 0,
        "energyPerTile": 1,
        "minXpPerTile": 20,
        "maxXpPerTile": 50,
        "minHealthPerTile": 0,
        "maxHealthPerTile": 0,
        "sid": qid,
        "mapHash": f"{qid}_map",
        "finalBoss": ({"id": boss_id, "level": 1, "rank": 1} if boss_id else None),
        "teamSizeMin": 1,
        "teamSizeMax": 1,
        "difficulty": "normal",
        "recommendedPartyPI": 100,
        "recommendedMasteryPI": 200,
        "multiplier": 1.0,
        "firstCompletionRewards": [{"id": "gold", "type": "currency", "amount": 2000},
                                   {"id": "shards", "type": "currency", "amount": 100}],
        "firstCompletionRewardsMin": [{"id": "gold", "type": "currency", "amount": 2000}],
        "firstCompletionRewardsMax": [{"id": "gold", "type": "currency", "amount": 2000}],
        "masteryCompletionRewards": [],
        "potentialCompletionRewards": [],
        "act": act,
        "chapter": chapter,
        "mission": mission,
    }


def roman_int(v, default=1):
    s = str(v).strip().upper()
    table = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}
    if s in table:
        return table[s]
    try:
        return int(s)
    except Exception:
        return default


def build_set(set_id, set_name, category, group_tag, act_no, act_name, chapters_src):
    local_act = 1
    chapters = []
    quests = []
    maps = {}
    for ch in chapters_src:
        cno = roman_int(ch.get("chapter", 1))
        cname = ch.get("name") or f"Chapter {cno}"
        ch_quests = []
        for m in ch.get("missions", []):
            mno = int(m.get("index", len(ch_quests) + 1))
            title = m.get("name") or f"Mission {mno}"
            boss_name = m.get("boss") or ""
            boss_id = m.get("boss_client_id")
            qid = (f"story_act{act_no}_ch{cno}_m{mno}" if category == "Story"
                   else f"awaken_ch{cno}_m{mno}")
            q = quest_obj(qid, category, local_act, cno, mno, title, boss_name, boss_id)
            ch_quests.append(q)
            quests.append(q)
            maps[qid] = make_map(qid, act_no, cno, mno, boss_id)
        chapters.append({
            "act": local_act,
            "chapter": cno,
            "friendlyName": cname,
            "description": cname,
            "image": f"chapter_{cno}_banner",
            "unlocked": True,
            "completed": False,
            "mastered": False,
            "alwaysLocked": False,
            "clearedCount": 0,
            "visibleClearedCount": 0,
            "walkableCount": 3,
            "visibleWalkableCount": 3,
            "firstCompletionRewards": [{"id": "gold", "type": "currency", "amount": 1000}],
            "masteryCompletionRewards": [],
            "potentialCompletionRewards": [],
            "Quests": ch_quests,
        })
    act = {
        "act": local_act,
        "friendlyName": act_name,
        "description": act_name,
        "image": f"act_{act_no}_banner",
        "unlocked": True,
        "completed": False,
        "mastered": False,
        "clearedCount": 0,
        "visibleClearedCount": 0,
        "walkableCount": 3,
        "visibleWalkableCount": 3,
        "firstCompletionRewards": [{"id": "gold", "type": "currency", "amount": 2000},
                                   {"id": "shards", "type": "currency", "amount": 100}],
        "masteryCompletionRewards": [],
        "potentialCompletionRewards": [],
        "Chapters": chapters,
    }
    return {
        "category": category,
        "hash": "v1",
        "setName": set_name,
        "setId": set_id,
        "cdn": "",
        "showInUI": True,
        "groupTag": group_tag,
        "difficulty": "normal",
        "difficultyLabel": "Normal",
        "minLevel": 0,
        "recommendedMinLevel": 0,
        "hasProgression": True,
        "actCount": 1,
        "chapterCount": [0, len(chapters)],
        "availableQuests": quests,
        "acts": [act],
        "chapters": chapters,
        "QuestMaps": maps,
        "expiry": 0,
        "showUI": True,
        "group": group_tag,
        "recommendMinLevel": 0,
        "timeLimit": 0,
        "timeLimitGrace": 0,
        "use_ui_color": False,
        "difficulty_label": "Normal",
        "tags": [group_tag],
    }


real = json.loads(REAL.read_text(encoding="utf-8"))["latest"]
sets = []
for a in real["story_acts"]:
    sets.append(build_set(f"story_act_{a['act']}", f"Act {a['act']}: {a['name']}",
                          "Story", "story", int(a["act"]), a["name"], a.get("chapters", [])))
aw = real["other_act_pages"].get("Awaken and Corrupt", {})
sets.append(build_set("awaken_and_corrupt", "Awaken and Corrupt", "Awaken",
                      "awaken", 1, "Awaken and Corrupt", aw.get("chapters", [])))

OUT.write_text(json.dumps(sets, ensure_ascii=False, indent=1), encoding="utf-8")
total = sum(len(s["availableQuests"]) for s in sets)
story = sum(len(s["availableQuests"]) for s in sets if s["category"] == "Story")
awaken = sum(len(s["availableQuests"]) for s in sets if s["category"] == "Awaken")
print("sets", len(sets), "quests", total, "story", story, "awaken", awaken)
for s in sets:
    print(" ", s["setId"], len(s["availableQuests"]), len(s["chapters"]))
