import http.server
import socketserver
import json
import time
import os
import sys
import urllib.parse
from datetime import datetime

PORT = 8080
LOG_FILE = os.path.join(os.path.dirname(__file__), "requests.jsonl")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ACTIVE_POS = {}
# Runtime experiment switches, for black-box protocol probes only.
# GET /__control?movedir_actions=moveto|battle|both
EXPERIMENT = {"movedir_actions": "both", "tutorial_mode": "completed"}
DB_ENABLED = bool(os.environ.get("TFTF_DB"))


def persist_quest_run(qid, team=None, state=None):
    if not DB_ENABLED:
        return
    try:
        from persistence import save_quest_run
        save_quest_run("10001", qid, "local", team=team or {}, state=state or {})
    except Exception as exc:
        print(f"[persistence] {exc}")


def tutorial_payload(data):
    """Return the stub tutorial payload, optionally reset to the original flow."""
    if EXPERIMENT.get("tutorial_mode") != "original":
        return data
    out = json.loads(json.dumps(data))
    for key, value in list(out.items()):
        if not isinstance(value, dict):
            continue
        value["s"] = "not_started"
        value["state"] = "not_started"
        value["current_bid"] = "fte"
        value["currentBranchID"] = "fte"
        branches = value.get("branches")
        if isinstance(branches, dict):
            for branch in branches.values():
                if isinstance(branch, dict):
                    branch["s"] = "not_started"
                    branch["state"] = "not_started"
    return out

def load_data_json(filename, default=None):
    """Load JSON data payload from server/data/<filename>."""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading {filepath}: {e}", file=sys.stderr)
    return default if default is not None else {}

def make_sparx_response(result=None, sync=None, async_list=None, error=None, fatal=False, retry=False):
    # Sparx canonical envelope [STATIC: parsed from EB.Sparx.Response and EB.Sparx.EndPoint]
    resp = {
        "ts": int(time.time()),
        "result": result if result is not None else {},
    }
    if sync:
        resp["sync"] = sync
    if async_list:
        resp["async"] = async_list
    if error:
        resp["error"] = error
        resp["fatal"] = fatal
        resp["retry"] = retry
    return json.dumps(resp, ensure_ascii=False)

class SparxStubHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_request_details(self, method, body_bytes=b""):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        headers_dict = dict(self.headers)

        body_str = ""
        body_json = None
        if body_bytes:
            try:
                body_str = body_bytes.decode('utf-8')
                body_json = json.loads(body_str)
            except Exception:
                body_str = body_bytes.decode('utf-8', errors='replace')

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "client_ip": self.client_address[0],
            "client_port": self.client_address[1],
            "method": method,
            "path": path,
            "query": query,
            "headers": headers_dict,
            "body": body_json if body_json is not None else body_str
        }

        # Write to JSONL file with explicit flush
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                f.flush()
        except Exception as e:
            print(f"[!] Error writing log: {e}", file=sys.stderr)

        print(f"\n[CLIENT REQUEST] {method} {path}")
        print(f"       Client: {self.client_address[0]}:{self.client_address[1]}")
        print(f"       Headers: stoken={headers_dict.get('stoken') or query.get('stoken', [None])[0]}")
        if body_json:
            print(f"       Body JSON: {json.dumps(body_json, ensure_ascii=False)}")
        elif body_str:
            print(f"       Body Raw: {body_str[:120]}")

        return path, query, headers_dict, body_json

    def send_sparx(self, result=None, sync=None, status_code=200, assumed_label="[ASSUMED]"):
        payload = make_sparx_response(result=result, sync=sync)
        body = payload.encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        self.wfile.write(body)
        print(f"[SPARX RESPONSE 200] {assumed_label} Sent {len(body)} bytes")

    def do_GET(self):
        # Support WebSocket upgrade handshake if client requests ws
        if self.headers.get("Upgrade", "").lower() == "websocket" or self.path == "/ws":
            self.send_response(400)
            self.end_headers()
            return

        path, query, headers, body_json = self.log_request_details("GET")
        self.dispatch(path, query, headers, body_json)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
        path, query, headers, body_json = self.log_request_details("POST", body_bytes)
        self.dispatch(path, query, headers, body_json)

    def dispatch(self, path, query, headers, body):
        now = int(time.time())

        # Experiment control (black-box probes; not part of the game protocol).
        if path == "/__control":
            if "movedir_actions" in query:
                val = query["movedir_actions"][0]
                if val in ("moveto", "battle", "both"):
                    EXPERIMENT["movedir_actions"] = val
            if "tutorial_mode" in query:
                val = query["tutorial_mode"][0]
                if val in ("completed", "original"):
                    EXPERIMENT["tutorial_mode"] = val
            if "reset" in query:
                EXPERIMENT["movedir_actions"] = "both"
                EXPERIMENT["tutorial_mode"] = "completed"
            self.send_sparx(dict(EXPERIMENT), assumed_label="[RUN: __control]")
            return

        # 1. Auth Init [RUN: confirmed in device test]
        if path == "/auth/init":
            self.send_sparx({
                "status": "ok",
                "session": "sess_tf_stub_token_12345"
            }, assumed_label="[RUN: /auth/init]")
            return

        # 2. Auth Enumerate [STATIC: return [] for fresh account flow to invoke PreLoginFlow]
        if path == "/auth/enumerate":
            self.send_sparx([], assumed_label="[STATIC: /auth/enumerate empty accounts array]")
            return

        # 3. Prelogin [STATIC: salt="" causes SyncGenerateHMACSignatureFromAPK to skip APK_Check_Start_Salt in libapkprotect.so]
        if path == "/auth/prelogin":
            self.send_sparx({
                "salt": "",
                "status": "ok"
            }, assumed_label="[STATIC: /auth/prelogin bypass libapkprotect with empty salt]")
            return

        # 4. Login [STATIC: loaded from server/data/login_response.json]
        if path == "/auth/login":
            data = load_data_json("login_response.json")
            if not data:
                data = {
                    "token": "sess_tf_stub_token_12345",
                    "stoken": "sess_tf_stub_token_12345",
                    "auth": {"device": True},
                    "endpoints": {"device": "http://127.0.0.1:8080"}
                }
            self.send_sparx(data, assumed_label="[STATIC: /auth/login loaded from data/login_response.json]")
            return

        # 5. Account Data [STATIC: loaded from server/data/account_data.json]
        if path == "/account/data":
            data = load_data_json("account_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /account/data loaded from data/account_data.json]")
            return

        # 6. Krash / Error reporting [RUN: captured in live run]
        if path == "/krash" or path.startswith("/krash/"):
            print("[KRASH REPORT RECEIVED]")
            self.send_sparx({"status": "received", "id": "krash_1001"}, assumed_label="[RUN: /krash]")
            return

        # 7. Tuning [STATIC: loaded from server/data/tuning_data.json]
        if path == "/tuning":
            data = load_data_json("tuning_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /tuning loaded from data/tuning_data.json]")
            return

        # 8. BCG getLoginData [STATIC: loaded from server/data/bcg_login_data.json]
        if path == "/bcg/getLoginData":
            data = load_data_json("bcg_login_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /bcg/getLoginData loaded from data/bcg_login_data.json]")
            return

        # 9. BCG base hero data [STATIC: BCGAPI request body {heroes:[{bid,rank,level,sig_lvl,flvl}],api,nonce}]
        # Response is a JSON array of BCGHeroDetails. Attribute values below are [ASSUMED]
        # placeholders (the original Kabam server computed them); schema is [CLIENT].
        if path == "/bcg/getBaseHeroData":
            heroes_req = []
            if isinstance(body, dict):
                heroes_req = body.get("heroes") or []
            details = []
            for h in heroes_req:
                if not isinstance(h, dict):
                    continue
                bid = h.get("bid", "")
                rank = int(h.get("rank", 1) or 1)
                level = int(h.get("level", 1) or 1)
                sig = int(h.get("sig_lvl", 0) or 0)
                hp = 800 + rank * 200 + level * 50
                atk = 80 + rank * 30 + level * 5
                rating_hp = int(hp * 0.1)
                rating_attack = int(atk * 0.5)
                details.append({
                    "bid": bid,
                    "rank": rank,
                    "level": level,
                    "sig_lvl": sig,
                    "max_hp": hp,
                    "attack": atk,
                    "rating": rating_hp + rating_attack,
                    "rating_hp": rating_hp,
                    "rating_attack": rating_attack,
                    "rating_hp_base": rating_hp,
                    "rating_attack_base": rating_attack,
                    "special_attacks": 3,
                    "pvpb": {},
                    "synergyBonuses": [],
                    "user_owned": True
                })
            self.send_sparx(details, assumed_label="[ASSUMED: /bcg/getBaseHeroData computed details]")
            return

        # 10. BCG user data (roster) [STATIC: loaded from data/bcg_user_data.json]
        if path == "/bcg/getUserData":
            data = load_data_json("bcg_user_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /bcg/getUserData loaded from data/bcg_user_data.json]")
            return

        # 10b. BCG set saved team [CLIENT: POST /bcg/setSavedTeam {teamID, heroes:[bid]}]
        # The client expects a userData-like payload back. Attributes are [ASSUMED].
        if path == "/bcg/setSavedTeam":
            base = load_data_json("bcg_login_data.json")
            ud = json.loads(json.dumps(base.get("userData", {})))
            team_id = "0"
            hero_ids = []
            if isinstance(body, dict):
                team_id = str(body.get("teamID", "0"))
                hero_ids = body.get("heroes") or []
            details = []
            for bid in hero_ids:
                hero = next((h for h in ud.get("heroes", []) if h.get("bid") == bid), None)
                rank = int(hero.get("rank", 1)) if hero else 1
                level = int(hero.get("level", 1)) if hero else 1
                hp = 800 + rank * 200 + level * 50
                atk = 80 + rank * 30 + level * 5
                details.append({
                    "bid": bid, "rank": rank, "level": level, "sig_lvl": 0,
                    "max_hp": hp, "attack": atk,
                    "rating": int(hp * 0.1) + int(atk * 0.5),
                    "rating_hp": int(hp * 0.1), "rating_attack": int(atk * 0.5),
                    "rating_hp_base": int(hp * 0.1), "rating_attack_base": int(atk * 0.5),
                    "special_attacks": 3, "pvpb": {},
                    "synergyBonuses": [], "user_owned": True
                })
            saved = ud.get("savedTeams")
            if not isinstance(saved, list):
                saved = []
            saved = [t for t in saved if not (isinstance(t, dict) and str(t.get("sid")) == team_id)]
            saved.append({"sid": team_id, "heroes": details})
            ud["savedTeams"] = saved
            # Same envelope shape as /bcg/getLoginData.result.userData (verified to parse):
            # { userData:{...}, updates:{heroes,...}, deletes:{} }
            wrapper = {
                "userData": {
                    "blueprintsMax": ud.get("blueprintsMax", 50),
                    "teamSizeMax": ud.get("teamSizeMax", 3),
                    "teamCountMax": ud.get("teamCountMax", 3)
                },
                "updates": {
                    "heroes": ud.get("heroes", []),
                    "savedTeams": ud.get("savedTeams", []),
                    "activeTeams": ud.get("activeTeams", []),
                    "inventory": ud.get("inventory", {"f": {}, "bp": {}, "max": {}}),
                    "heroesScreenList": [],
                    "heroes_cta": {}
                },
                "deletes": {}
            }
            payload = json.loads(json.dumps(base))
            payload["userData"] = wrapper
            self.send_sparx(payload, assumed_label="[ASSUMED: /bcg/setSavedTeam full BCG payload + userData wrapper]")
            return

        # 11. AutoRefresh endpoints [STATIC: loaded from server/data/missions_config.json or generic envelope]
        if path.startswith("/autorefresh/missionsconfig/"):
            data = load_data_json("missions_config.json")
            self.send_sparx(data, assumed_label="[STATIC: /autorefresh/missionsconfig/ loaded from data/missions_config.json]")
            return

        if path.startswith("/autorefresh/"):
            sub_name = path.split("/")[2] if len(path.split("/")) > 2 else "data"
            meta = load_data_json("autorefresh_metadata.json")
            self.send_sparx({
                "check": meta.get("check", "check_hash_12345"),
                "refresh": meta.get("refresh", 3600),
                "cache": meta.get("cache", False),
                sub_name: {}
            }, assumed_label=f"[STATIC: /autorefresh/{sub_name}]")
            return

        # 12. Quests: Available quests [STATIC: loaded from server/data/quest_list.json]
        if path == "/quests/quest-list":
            data = load_data_json("quest_list.json", default=[])
            self.send_sparx(data, assumed_label="[STATIC: /quests/quest-list loaded from data/quest_list.json]")
            return

        # 12b. Quests: Progression [STATIC: QuestsAPI]
        if path == "/quests/quest-progression":
            data = load_data_json("quest_progression.json")
            self.send_sparx(data, assumed_label="[STATIC: /quests/quest-progression loaded from data/quest_progression.json]")
            return

        # 12c. Quests: Quest Details [STATIC: loaded from server/data/quest_detail.json]
        if path.startswith("/quests/quest-detail/") or path == "/quests/quest-details":
            data = load_data_json("quest_detail.json")
            self.send_sparx(data, assumed_label="[STATIC: /quests/quest-detail/ loaded from data/quest_detail.json]")
            return

        # 12d. Quests: Begin Quest [CLIENT: QuestsManager callback reads
        # result.activeQuests[qid].teamData and passes it to UpdateUserData]
        if path.startswith("/quests/quest-begin/") or path == "/quests/begin-quest":
            quest = load_data_json("quest_begin_response.json")
            qid = path.rstrip("/").rsplit("/", 1)[-1] if "/" in path else quest.get("qid", "")
            if qid and qid != "begin-quest":
                quest["qid"] = qid
                if isinstance(quest.get("data"), dict):
                    quest["data"]["id"] = qid
            team = []
            if isinstance(body, dict):
                for key in ("tm0", "tm1", "tm2", "tm3"):
                    if body.get(key):
                        team.append(body[key])
            if team:
                quest["team"] = {
                    bid: {"hp": 1000.0, "pi": 100, "sig_lvl": 0, "stat_mods": [], "sig_mods": []}
                    for bid in team
                }
            base = load_data_json("bcg_login_data.json")
            ud = json.loads(json.dumps(base.get("userData", {})))
            hero_details = []
            for bid in team:
                hero = next((h for h in ud.get("heroes", []) if h.get("bid") == bid), None)
                rank = int(hero.get("rank", 1)) if hero else 1
                level = int(hero.get("level", 1)) if hero else 1
                hero_details.append({
                    "bid": bid, "rank": rank, "level": level, "sig_lvl": 0,
                    "max_hp": 800 + rank * 200 + level * 50,
                    "attack": 80 + rank * 30 + level * 5,
                    "rating": 100, "rating_hp": 50, "rating_attack": 50,
                    "rating_hp_base": 50, "rating_attack_base": 50,
                    "special_attacks": 3, "pvpb": {},
                    "synergyBonuses": [], "user_owned": True
                })
            active_teams = [t for t in (ud.get("activeTeams") or []) if isinstance(t, dict) and t.get("aid") != qid]
            team_obj = {
                "aid": qid, "type": "story", "modes": ["Story"], "expire": 0,
                "heroes": {d["bid"]: d for d in hero_details}
            }
            active_teams.append(team_obj)
            mode_team = json.loads(json.dumps(team_obj))
            mode_team["aid"] = "story"
            mode_team["activityID"] = "story"
            active_teams.append(mode_team)
            set_id = body.get("setId") if isinstance(body, dict) else None
            if set_id:
                set_team = json.loads(json.dumps(team_obj))
                set_team["aid"] = str(set_id)
                set_team["activityID"] = str(set_id)
                active_teams.append(set_team)
            quest["teamData"] = {
                "userData": {
                    "blueprintsMax": ud.get("blueprintsMax", 50),
                    "teamSizeMax": ud.get("teamSizeMax", 3),
                    "teamCountMax": ud.get("teamCountMax", 3)
                },
                "updates": {
                    "heroes": ud.get("heroes", []),
                    "savedTeams": ud.get("savedTeams", []),
                    "activeTeams": active_teams,
                    "inventory": ud.get("inventory", {"f": {}, "bp": {}, "max": {}})
                },
                "deletes": {}
            }
            persist_quest_run(qid, team=quest.get("team"), state={"phase": "begin"})
            self.send_sparx({"activeQuests": {qid: quest}},
                            assumed_label="[CLIENT: /quests/quest-begin/ activeQuests wrapper + teamData]")
            ACTIVE_POS[qid] = {"x": 0, "y": 0}
            return

        # 12e. Quests: Move To [STATIC: loaded from server/data/quest_begin_response.json]
        if path.startswith("/quests/quest-moveto/"):
            data = load_data_json("quest_begin_response.json")
            if isinstance(body, dict) and "x" in body and "y" in body:
                data["currentPosition"] = {"x": body["x"], "y": body["y"]}
                data["playerPosition"] = {"x": body["x"], "y": body["y"]}
            self.send_sparx(data, assumed_label="[STATIC: /quests/quest-moveto/]")
            return

        # 12e. Quests: Move direction (battle action is experimental; prefight opens) [CLIENT: /quests/quest-movedir/{qid}/{dx}/{dy}]
        if path.startswith("/quests/quest-movedir/"):
            parts = path.rstrip("/").split("/")
            qid = parts[3] if len(parts) > 3 else ""
            try:
                dx = int(parts[4]); dy = int(parts[5])
            except Exception:
                dx = dy = 0
            cur = ACTIVE_POS.get(qid, {"x": 0, "y": 0})
            new = {"x": cur["x"] + dx, "y": cur["y"] + dy}
            ACTIVE_POS[qid] = new
            base = load_data_json("bcg_login_data.json")
            ud = json.loads(json.dumps(base.get("userData", {})))
            team = next((t for t in (ud.get("activeTeams") or []) if isinstance(t, dict) and t.get("aid") == qid), None)
            wrapper = {
                "userData": {
                    "blueprintsMax": ud.get("blueprintsMax", 50),
                    "teamSizeMax": ud.get("teamSizeMax", 3),
                    "teamCountMax": ud.get("teamCountMax", 3)
                },
                "updates": {
                    "heroes": ud.get("heroes", []),
                    "savedTeams": ud.get("savedTeams", []),
                    "activeTeams": ud.get("activeTeams", []),
                    "inventory": ud.get("inventory", {"f": {}, "bp": {}, "max": {}})
                },
                "deletes": {}
            }
            # The prefight asset database is keyed by the base blueprint id.
            # The roster uses a synthetic _2 id; rebase only the battle teamData.
            base_bp = "bumblebee_cin_dotm"
            def rebase(obj):
                if isinstance(obj, dict):
                    return {(base_bp if k == "bumblebee_cin_dotm_2" else k): rebase(v)
                            for k, v in obj.items()}
                if isinstance(obj, list):
                    return [rebase(v) for v in obj]
                if obj == "bumblebee_cin_dotm_2":
                    return base_bp
                return obj
            wrapper = rebase(wrapper)
            def fill_hp(h):
                if isinstance(h, dict):
                    h["hp"] = 1000.0
                    h["max_hp"] = 1000.0
                    h["pi"] = 100
                    h.setdefault("sig_lvl", 0)
                    h.setdefault("stat_mods", [])
                    h.setdefault("sig_mods", [])
                    h.setdefault("blueprint", h.get("bid") or h.get("id") or h.get("hero") or "")
                    h.setdefault("rank", 1)
                    h.setdefault("level", 1)
            for h in wrapper["updates"].get("heroes", []):
                fill_hp(h)
            ats = wrapper["updates"].get("activeTeams", [])
            if isinstance(ats, list):
                fixed = {}
                for t in ats:
                    hv = t.get("heroes", {})
                    if isinstance(hv, dict):
                        for h in hv.values():
                            fill_hp(h)
                    elif isinstance(hv, list):
                        for h in hv:
                            fill_hp(h)
                    aid = t.get("aid") or t.get("activityID") or qid
                    t["activityID"] = aid
                    t["estimatedExpire"] = t.get("expire", t.get("estimatedExpire", 0))
                    fixed[aid] = t
                    qbegin = load_data_json("quest_begin_response.json")
                    uid = qbegin.get("uniqueId")
                    if uid:
                        fixed[uid] = t
                    mode_key = qbegin.get("mode")
                    if mode_key:
                        fixed[mode_key] = t
                        fixed[str(mode_key).capitalize()] = t
                    story_team = json.loads(json.dumps(t))
                    story_team["aid"] = "story"
                    story_team["activityID"] = "story"
                    fixed["story"] = story_team
                    story_upper = json.loads(json.dumps(story_team))
                    story_upper["aid"] = "Story"
                    story_upper["activityID"] = "Story"
                    fixed["Story"] = story_upper
                wrapper["updates"]["activeTeams"] = fixed
            elif isinstance(ats, dict):
                for t in ats.values():
                    hv = t.get("heroes", {})
                    if isinstance(hv, dict):
                        for h in hv.values():
                            fill_hp(h)
                    elif isinstance(hv, list):
                        for h in hv:
                            fill_hp(h)
            qd = load_data_json("quest_detail.json")
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
                "strongestHero": base_bp,
                "currentPos": {"x": 0, "y": 0},
                "currentBattleId": "battle1",
                "currentBattleState": 2,
                "currentBattlePos": new,
                "usedConsumableCount": 0,
                "battleLockExpiry": 0,
                "state": 1,
                "team": {
                    base_bp: {
                        "hp": 1000.0,
                        "pi": 100,
                        "sig_lvl": 0,
                        "stat_mods": [],
                        "sig_mods": []
                    }
                }
            }
            results = [
                {"action": {"moveto": {"x": new["x"], "y": new["y"]}}},
                {"action": {"battle": {
                    "x": new["x"], "y": new["y"],
                    "isFinalBoss": False,
                    "battleEnemy": boss
                }}},
            ]
            mode = EXPERIMENT.get("movedir_actions", "both")
            if mode == "moveto":
                results = results[:1]
            elif mode == "battle":
                results = results[1:]
            persist_quest_run(qid, state={"position": new})
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
                "results": results,
                "teamData": wrapper
            }, assumed_label="[CLIENT: /quests/quest-movedir/ battle action + progression]")
            return

        # 12f. Matches: Activate Match [STATIC: loaded from server/data/match_activate_response.json]
        if path.startswith("/matches/activate-match/"):
            data = load_data_json("match_activate_response.json")
            self.send_sparx(data, assumed_label="[STATIC: /matches/activate-match/ loaded from data/match_activate_response.json]")
            return

        # 12g. Matches: Match Loaded [STATIC: MatchAPI SignalMatchLoaded]
        if path.startswith("/matches/match-loaded/"):
            self.send_sparx({"status": "ok"}, assumed_label="[STATIC: /matches/match-loaded/]")
            return

        # 12h. Matches: Resolve Match [STATIC: loaded from server/data/match_resolve_response.json]
        if path.startswith("/matches/resolve-match/"):
            data = load_data_json("match_resolve_response.json")
            self.send_sparx(data, assumed_label="[STATIC: /matches/resolve-match/ loaded from data/match_resolve_response.json]")
            return

        # 13. Quests: Active quest [STATIC: loaded from server/data/quest_active.json]
        if path == "/quests/quest-active":
            data = load_data_json("quest_active.json")
            self.send_sparx(data, assumed_label="[STATIC: /quests/quest-active loaded from data/quest_active.json]")
            return

        # 14. PVP Login Data [STATIC: loaded from server/data/pvp_login_data.json]
        if path == "/pvp/get-login-data":
            data = load_data_json("pvp_login_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /pvp/get-login-data loaded from data/pvp_login_data.json]")
            return

        # 15. Base Active [STATIC: loaded from server/data/base_active.json]
        if path == "/base/active":
            data = load_data_json("base_active.json")
            self.send_sparx(data, assumed_label="[STATIC: /base/active loaded from data/base_active.json]")
            return

        # 16. Payments Payouts [STATIC: loaded from server/data/payments_payouts.json]
        if path == "/payments/payouts":
            data = load_data_json("payments_payouts.json")
            self.send_sparx(data, assumed_label="[STATIC: /payments/payouts loaded from data/payments_payouts.json]")
            return

        # 17. Offers Data [STATIC: loaded from server/data/offers_data.json]
        if path == "/offers/getLoginData":
            data = load_data_json("offers_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /offers/getLoginData loaded from data/offers_data.json]")
            return

        # 18. Redeemer Refresh [STATIC: loaded from server/data/redeemer_data.json]
        if path == "/redeemer/refresh":
            data = load_data_json("redeemer_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /redeemer/refresh loaded from data/redeemer_data.json]")
            return

        # 19. Events Refresh [STATIC: loaded from server/data/events_data.json]
        if path == "/events/refresh":
            data = load_data_json("events_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /events/refresh loaded from data/events_data.json]")
            return

        # 20. GameStats [STATIC: loaded from server/data/gamestats_data.json]
        if path == "/gamestats/get-login-data":
            data = load_data_json("gamestats_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /gamestats/get-login-data loaded from data/gamestats_data.json]")
            return

        # 21. GameStats Achievements Check [STATIC]
        if path == "/gamestats/check-login-achievements":
            self.send_sparx([], assumed_label="[STATIC: /gamestats/check-login-achievements]")
            return

        # 22. Performance Profile [STATIC: loaded from server/data/performance_profile.json]
        if path == "/performance/profile":
            data = load_data_json("performance_profile.json")
            self.send_sparx(data, assumed_label="[STATIC: /performance/profile loaded from data/performance_profile.json]")
            return

        # 23. Tutorial login data [STATIC: loaded from server/data/tutorial_data.json]
        if path == "/tutorial/get-login-data":
            data = tutorial_payload(load_data_json("tutorial_data.json"))
            self.send_sparx(data, assumed_label="[STATIC: /tutorial/get-login-data loaded from data/tutorial_data.json]")
            return

        # 23b. Tutorial Actions [STATIC: TutorialAPI StartTutorial, StartBranch, CompleteTutorial]
        if path.startswith("/tutorial/"):
            tid = "FTE"
            bid = "close"
            if isinstance(body, dict):
                tid = body.get("tid", "FTE")
                bid = body.get("bid", "close")

            branch_data = {
                "s": "completed",
                "branchID": bid,
                "state": "completed"
            }
            res_data = {
                "s": "completed",
                "state": "completed",
                "current_bid": bid,
                "currentBranchID": bid,
                "branches": {
                    bid: branch_data,
                    "close": branch_data,
                    "FTE": branch_data
                }
            }
            self.send_sparx({
                tid: res_data,
                "FTE": res_data
            }, assumed_label="[STATIC: /tutorial/* action]")
            return

        # 24. Push token [STATIC: PushAPI]
        if path == "/push/token":
            self.send_sparx({
                "status": "ok",
                "websocket": "ws://127.0.0.1:8080/ws"
            }, assumed_label="[STATIC: /push/token]")
            return

        # 25. Inventory [STATIC: InventoryAPI]
        if path.startswith("/inventory"):
            self.send_sparx({
                "items": []
            }, assumed_label="[STATIC: /inventory]")
            return

        # 26. Wallet [STATIC: loaded from server/data/wallet_data.json]
        if path.startswith("/wallet"):
            data = load_data_json("wallet_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /wallet loaded from data/wallet_data.json]")
            return

        # 27. DataSync [STATIC: loaded from server/data/datasync_profile.json]
        if path.startswith("/ds/"):
            data = load_data_json("datasync_profile.json")
            self.send_sparx(data, assumed_label="[STATIC: /ds/ loaded from data/datasync_profile.json]")
            return

        # Default safe empty response for any unknown path [ASSUMED]
        print(f"[!] Warning: Handled UNKNOWN endpoint {path} with safe empty envelope")
        self.send_sparx({}, assumed_label="[ASSUMED: unknown fallback]")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run(port=PORT):
    if DB_ENABLED:
        from persistence import init_db
        init_db()
        print(f"  SQLite persistence: {os.environ.get('TFTF_DB')}")
    server_address = ('0.0.0.0', port)
    httpd = ThreadedHTTPServer(server_address, SparxStubHandler)
    print(f"==================================================")
    print(f"  Transformers: Forged to Fight - Mock Stub Server")
    print(f"  Listening on: http://0.0.0.0:{port}")
    print(f"  Logging all requests to: {LOG_FILE}")
    print(f"  Data Directory: {DATA_DIR}")
    print(f"  Status: Ready for client connection [STATIC/RUN schemas]")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(p)
