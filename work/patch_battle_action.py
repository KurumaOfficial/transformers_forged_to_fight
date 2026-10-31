from pathlib import Path
p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''            qd = load_data_json("quest_detail.json")
            try:
                tile = qd["map"]["grid"][new["y"]][new["x"]]
            except Exception:
                tile = {"position": new, "walkable": True}
            self.send_sparx({
                "progression": {
                    "version": 2,
                    "currentPos": new,
                    "cleared": [{"x": 0, "y": 0}, new],
                    "previouslyCleared": [],
                    "revealed": [],
                    "currentPosition": new,
                    "playerPosition": new,
                    "currentTile": new,
                    "clearedTiles": [{"x": 0, "y": 0}, new],
                    "percentComplete": 22,
                    "currentFightId": "fight1",
                    "currentBattleId": "battle1",
                    "currentBattleBossId": "enemy1",
                    "currentBattlePos": new,
                    "currentBattleEnemyHealth": 1000,
                    "localPlayer": {
                        "uid": "local",
                        "name": "Local",
                        "tag": "LOCAL",
                        "strongestHero": "bumblebee_cin_dotm",
                        "currentPos": {"x": 0, "y": 0},
                        "currentBattleId": "battle1",
                        "currentBattleState": 2,
                        "currentBattlePos": new,
                        "usedConsumableCount": 0,
                        "battleLockExpiry": 0,
                        "state": 1,
                        "team": [{
                            "id": "bumblebee_cin_dotm",
                            "bid": "bumblebee_cin_dotm",
                            "hero": "bumblebee_cin_dotm",
                            "level": 1,
                            "rank": 1,
                            "sig_lvl": 0,
                            "flvl": 0
                        }]
                    }
                },
                "currentPosition": new,
                "playerPosition": new,
                "currentTile": new,
                "results": [{
                    "action": "moveto",
                    "moveto": {"x": new["x"], "y": new["y"]},
                    "cleared": [{"x": 0, "y": 0}, new],
                    "visibleClearedCount": 2,
                    "walkableCount": 9,
                    "visibleWalkableCount": 9
                }],
                "teamData": wrapper
            }, assumed_label="[CLIENT: /quests/quest-movedir/ progression+results+teamData]")'''
new = '''            qd = load_data_json("quest_detail.json")
            try:
                tile = qd["map"]["grid"][new["y"]][new["x"]]
            except Exception:
                tile = {"position": new, "walkable": True}
            qb = load_data_json("quest_begin_response.json")
            boss = json.loads(json.dumps(
                (qb.get("scaledBossTable") or {}).get("enemy1") or {}
            ))
            boss["id"] = "enemy1"
            local_uid = "10001"
            local_user = {
                "uid": local_uid,
                "name": "Commander",
                "tag": "LOCAL",
                "strongestHero": "bumblebee_cin_dotm_2",
                "currentPos": {"x": 0, "y": 0},
                "currentBattleId": "battle1",
                "currentBattleState": 2,
                "currentBattlePos": new,
                "usedConsumableCount": 0,
                "battleLockExpiry": 0,
                "state": 1,
                "team": [{
                    "id": "bumblebee_cin_dotm_2",
                    "bid": "bumblebee_cin_dotm_2",
                    "hero": "bumblebee_cin_dotm_2",
                    "level": 1,
                    "rank": 1,
                    "sig_lvl": 0,
                    "flvl": 0
                }]
            }
            self.send_sparx({
                "progression": {
                    "version": 3,
                    "currentPos": new,
                    "cleared": [{"x": 0, "y": 0}, new],
                    "previouslyCleared": [],
                    "revealed": [],
                    "currentFightId": "fight1",
                    "currentBattleId": "battle1",
                    "currentBattleBossId": "enemy1",
                    "currentBattlePos": new,
                    "currentBattleEnemyHealth": 1000,
                    "currentBattleEnemy": boss,
                    "users": {local_uid: local_user},
                    "currentPosition": new,
                    "playerPosition": new,
                    "currentTile": new,
                    "clearedTiles": [{"x": 0, "y": 0}, new],
                    "percentComplete": 22
                },
                "currentPosition": new,
                "playerPosition": new,
                "currentTile": new,
                "results": [
                    {"action": {"moveto": {"x": new["x"], "y": new["y"]}}},
                    {"action": {"battle": {
                        "x": new["x"], "y": new["y"],
                        "isFinalBoss": False,
                        "battleEnemy": boss
                    }}}
                ],
                "teamData": wrapper
            }, assumed_label="[CLIENT: /quests/quest-movedir/ battle action + progression]")'''
if old not in s:
    raise SystemExit("old block not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("patched")
