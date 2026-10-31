import http.server
import socketserver
import json
import wiki_stats
import time
import os
import sys
import urllib.parse
from datetime import datetime
from routes.quests import build_detail as build_quest_detail, build_begin as build_quest_begin, find_quest
from routes import auth as auth_routes
from routes import bcg as bcg_routes
from routes import matches as match_routes
from routes import odr as odr_routes

PORT = 8080
LOG_FILE = os.path.join(os.path.dirname(__file__), "requests.jsonl")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ACTIVE_POS = {}
# Runtime experiment switches, for black-box protocol probes only.
# GET /__control?movedir_actions=moveto|battle|both
EXPERIMENT = {"movedir_actions": "both", "tutorial_mode": "completed"}
DB_ENABLED = bool(os.environ.get("TFTF_DB"))
# Test-only switch: when work/weak_enemy.flag exists, server-generated enemy
# details get 1 HP / 1 attack. Used only to capture the win/post-battle path.
WEAK_ENEMY = os.path.exists(os.path.join(os.path.dirname(__file__), "..", "work", "weak_enemy.flag"))


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

def write_data_json(filename, data):
    """Persist a small JSON state file under server/data."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

def apply_win_progress(qid, pos, cleared, quest):
    """Update the runtime quest progress/active files after a win."""
    try:
        prog = load_data_json("quest_progression.json")
        bucket = prog.setdefault("Story", {})
        entry = bucket.setdefault(qid, {})
        entry.update({
            "unlocked": True,
            "completed": False,
            "mastered": bool(entry.get("mastered", False)),
            "cleared": cleared,
            "visibleClearedCount": len(cleared),
            "currentPos": pos,
            "percentComplete": 100 if (quest or {}).get("isFinalBoss") else 33,
        })
        prog["Story"] = bucket
        write_data_json("quest_progression.json", prog)
        active = load_data_json("quest_begin_response.json")
        active.update({
            "uniqueId": f"active_quest_{qid}",
            "qid": qid,
            "currentPosition": pos,
            "playerPosition": pos,
            "isFinished": False,
        })
        if quest:
            active["data"] = {**active.get("data", {}), **quest}
        write_data_json("quest_active.json", {"activeQuests": [active], "instances": []})
    except Exception as e:
        print(f"[!] apply_win_progress failed: {e}", file=sys.stderr)


def level_rewards_payload():
    """Minimal /levelrewards/fetch result from account level data."""
    level = 5
    try:
        account = load_data_json("account_data.json")
        level = int((account.get("user") or {}).get("level", level))
    except Exception:
        pass
    status = {
        "last_awarded_level": level,
        "lastAwardedLevel": level,
        "level": level,
        "Level": level,
        "isEnabled": True,
        "nextLevelXp": 1000,
        "types": [
            {"name": "commander", "level": level,
             "nextResourceThreshold": 1000, "previousResourceThreshold": 0}
        ],
    }
    return {
        "status": status,
        "levelrewards": status,
        "levelrewards_milestones": [],
        "nextLevelXp": 1000,
    }


def level_sync_async():
    """Ask LevelRewardsManager to fetch its status; component names are probed."""
    return [
        {"component": name, "message": "sync", "payload": {}}
        for name in ("levelrewards", "LevelRewardsManager",
                     "levelrewardsmanager", "levelRewards")
    ]

def make_sparx_response(result=None, sync=None, async_list=None, error=None, fatal=False, retry=False, extra=None):
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
    if extra:
        resp.update(extra)
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

    def send_sparx(self, result=None, sync=None, status_code=200, assumed_label="[ASSUMED]", async_list=None, extra=None):
        payload = make_sparx_response(result=result, sync=sync, async_list=async_list, extra=extra)
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
            self.send_sparx(auth_routes.init(), assumed_label="[RUN: /auth/init]")
            return

        # 2. Auth Enumerate [STATIC: return [] for fresh account flow to invoke PreLoginFlow]
        if path == "/auth/enumerate":
            self.send_sparx(auth_routes.enumerate_accounts(),
                            assumed_label="[STATIC: /auth/enumerate empty accounts array]")
            return

        # 3. Prelogin [STATIC: salt="" causes SyncGenerateHMACSignatureFromAPK to skip APK_Check_Start_Salt in libapkprotect.so]
        if path == "/auth/prelogin":
            self.send_sparx(auth_routes.prelogin(),
                            assumed_label="[STATIC: /auth/prelogin bypass libapkprotect with empty salt]")
            return

        # 4. Login [STATIC: loaded from server/data/login_response.json]
        if path == "/auth/login":
            self.send_sparx(auth_routes.login(load_data_json),
                            assumed_label="[STATIC: /auth/login loaded from data/login_response.json]")
            return

        # 5. Account Data [STATIC: loaded from server/data/account_data.json]
        if path == "/account/data":
            self.send_sparx(auth_routes.account_data(load_data_json),
                            assumed_label="[STATIC: /account/data loaded from data/account_data.json]")
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

        # 7b. Level rewards status [CLIENT: LevelRewardsAPI.FetchStatus 0x1271694]
        if path == "/levelrewards/fetch":
            data = level_rewards_payload()
            self.send_sparx(data, assumed_label="[CLIENT: /levelrewards/fetch status]",
                            extra=data)
            return

        # 8. BCG getLoginData [STATIC: loaded from server/data/bcg_login_data.json]
        if path == "/bcg/getLoginData":
            data = bcg_routes.login_data(load_data_json)
            self.send_sparx(data, assumed_label="[STATIC: /bcg/getLoginData loaded from data/bcg_login_data.json]",
                            async_list=level_sync_async())
            return

        # 8b. BCG hero XP curve [CLIENT: BCGHeroBaseCommon.SetXPCurve 0xC2356C]
        if path == "/bcg/getHeroXPCurve":
            self.send_sparx(bcg_routes.hero_xp_curve(body, load_data_json),
                            assumed_label="[CLIENT: /bcg/getHeroXPCurve array]")
            return

        # 9. BCG base hero data [STATIC: BCGAPI request body {heroes:[{bid,rank,level,sig_lvl,flvl}],api,nonce}]
        # Response is a JSON array of BCGHeroDetails. Attribute values below are [ASSUMED]
        # placeholders (the original Kabam server computed them); schema is [CLIENT].
        if path == "/bcg/getBaseHeroData":
            details = bcg_routes.base_hero_data(body, load_data_json, WEAK_ENEMY)
            self.send_sparx(details, assumed_label="[ASSUMED: /bcg/getBaseHeroData computed details]")
            return

        # 10. BCG user data (roster) [STATIC: loaded from data/bcg_user_data.json]
        if path == "/bcg/getUserData":
            data = bcg_routes.user_data(load_data_json)
            self.send_sparx(data, assumed_label="[STATIC: /bcg/getUserData loaded from data/bcg_user_data.json]")
            return

        # 10b. BCG set saved team [CLIENT: POST /bcg/setSavedTeam {teamID, heroes:[bid]}]
        # The client expects a userData-like payload back. Attributes are [ASSUMED].
        if path == "/bcg/setSavedTeam":
            payload = bcg_routes.set_saved_team(body, load_data_json)
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

        # 12c. Quests: Quest Details [dynamic from quest_list.json]
        if path.startswith("/quests/quest-detail/") or path == "/quests/quest-details":
            qid = path.rstrip("/").rsplit("/", 1)[-1] if path.startswith("/quests/quest-detail/") else ""
            data = build_quest_detail(qid) if qid else load_data_json("quest_detail.json")
            self.send_sparx(data, assumed_label="[CLIENT: /quests/quest-detail/ from quest_list.json]")
            return

        # 12d. Quests: Begin Quest [CLIENT: QuestsManager callback reads
        # result.activeQuests[qid].teamData and passes it to UpdateUserData]
        if path.startswith("/quests/quest-begin/") or path == "/quests/begin-quest":
            qid = path.rstrip("/").rsplit("/", 1)[-1] if "/" in path else ""
            quest = build_quest_begin(qid) if qid and qid != "begin-quest" else load_data_json("quest_begin_response.json")
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
                base_cat = load_data_json("bcg_login_data.json")
                bps = base_cat.get("blueprints", {})
                ud_heroes = {h.get("bid"): h for h in base_cat.get("userData", {}).get("heroes", [])
                             if isinstance(h, dict)}
                team_data = {}
                for bid in team:
                    bp = bps.get(bid, {})
                    uh = ud_heroes.get(bid, {})
                    rank = int(uh.get("rank", 1) or 1)
                    level = int(uh.get("level", 1) or 1)
                    s = wiki_stats.stats_for(bid, rank, level)
                    team_data[bid] = {
                        "hp": float(s["hp"]),
                        "max_hp": float(s["hp"]),
                        "attack": s["attack"],
                        "pi": s["rating"],
                        "rating": s["rating"],
                        "rank": rank,
                        "level": level,
                        "sig_lvl": int(uh.get("sig_lvl", 0) or 0),
                        "blueprint": bid,
                        "tags": list(bp.get("tags") or bp.get("t") or []),
                        "t": list(bp.get("t") or bp.get("tags") or []),
                        "armor": 50.0,
                        "crit_chance": 0.1,
                        "crit_damage": 1.5,
                        "perfect_block_chance": 0.0,
                        "block_proficiency": 0.5,
                        "mana_gain": 1.0,
                        "mana_start": 0.0,
                        "class_power": 1.0,
                        "resist_magic": 0.0,
                        "resist_physical": 0.0,
                        "stun_time": 0.0,
                        "stun_chance": 0.0,
                        "special_attacks": 3,
                        "stat_mods": [],
                        "sig_mods": [],
                        "buff_mods": [],
                        "synergyBonuses": [],
                    }
                quest["team"] = team_data
            base = load_data_json("bcg_login_data.json")
            ud = json.loads(json.dumps(base.get("userData", {})))
            hero_details = []
            for bid in team:
                hero = next((h for h in ud.get("heroes", []) if h.get("bid") == bid), None)
                rank = int(hero.get("rank", 1)) if hero else 1
                level = int(hero.get("level", 1)) if hero else 1
                s = wiki_stats.stats_for(bid, rank, level)
                hero_details.append({
                    "bid": bid, "rank": rank, "level": level, "sig_lvl": 0,
                    "max_hp": s["hp"],
                    "attack": s["attack"],
                    "rating": s["rating"], "rating_hp": s["rating_hp"],
                    "rating_attack": s["rating_attack"],
                    "rating_hp_base": s["rating_hp_base"],
                    "rating_attack_base": s["rating_attack_base"],
                    "armor": 50.0, "crit_chance": 0.1, "crit_damage": 1.5,
                    "perfect_block_chance": 0.0, "block_proficiency": 0.5,
                    "mana_gain": 1.0, "mana_start": 0.0,
                    "class_power": 1.0,
                    "resist_magic": 0.0, "resist_physical": 0.0,
                    "stun_time": 0.0, "stun_chance": 0.0,
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
            qd = build_quest_detail(qid)
            try:
                tile = qd["map"]["grid"][new["y"]][new["x"]]
            except Exception:
                tile = {"position": new, "walkable": True}
            qb = build_quest_begin(qid)
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

        # 12e2. ODR manifest [ASSUMED: client did not request it in the verified run]
        if path == "/odr/get-manifest":
            self.send_sparx(odr_routes.manifest(load_data_json),
                            assumed_label="[ASSUMED: /odr/get-manifest]")
            return
        if path == "/odr/get-published-manifests":
            self.send_sparx(odr_routes.published_manifests(),
                            assumed_label="[ASSUMED: /odr/get-published-manifests empty list]")
            return

        # 12f. Matches: Activate Match [STATIC: loaded from server/data/match_activate_response.json]
        if path.startswith("/matches/activate-match/"):
            self.send_sparx(match_routes.activate(load_data_json),
                            assumed_label="[STATIC: /matches/activate-match/ loaded from data/match_activate_response.json]")
            return

        # 12g. Matches: Match Loaded [STATIC: MatchAPI SignalMatchLoaded]
        if path.startswith("/matches/match-loaded/"):
            self.send_sparx(match_routes.match_loaded(),
                            assumed_label="[STATIC: /matches/match-loaded/]")
            return

        # 12h. Matches: Resolve Match [STATIC: loaded from server/data/match_resolve_response.json]
        if path.startswith("/matches/resolve-match/"):
            data = match_routes.resolve(load_data_json)
            try:
                won = ((body or {}).get("results") or {}).get("result") == "WON"
            except Exception:
                won = False
            qid = (body or {}).get("qid") or ""
            if won and qid:
                pos = ACTIVE_POS.get(qid, {"x": 1, "y": 0})
                cleared = [{"x": 0, "y": 0}]
                if pos not in cleared:
                    cleared.append(pos)
                base_cat = load_data_json("bcg_login_data.json")
                ud = json.loads(json.dumps(base_cat.get("userData", {})))
                wrapper = {
                    "userData": {
                        "blueprintsMax": ud.get("blueprintsMax", 50),
                        "teamSizeMax": ud.get("teamSizeMax", 3),
                        "teamCountMax": ud.get("teamCountMax", 3),
                    },
                    "updates": {
                        "heroes": ud.get("heroes", []),
                        "savedTeams": ud.get("savedTeams", []),
                        "activeTeams": ud.get("activeTeams", []),
                        "inventory": ud.get("inventory", {"f": {}, "bp": {}, "max": {}}),
                    },
                    "deletes": {},
                }
                _qset, quest = find_quest(qid)
                rewards = (quest or {}).get("firstCompletionRewards") or []
                redeems = [
                    {"type": str(r.get("type", "currency")),
                     "data": str(r.get("id", "")),
                     "quantity": int(r.get("amount", 0))}
                    for r in rewards if isinstance(r, dict)
                ]
                first_gold = sum(int(r.get("amount", 0)) for r in rewards
                                 if isinstance(r, dict) and r.get("id") == "gold")
                first_items = [r for r in redeems if r.get("data") != "gold"]
                completion_rewards = {
                    "firstGold": first_gold,
                    "firstItems": first_items,
                    "firstXP": int((quest or {}).get("minXpPerTile", 20) or 20),
                    "masteryGold": 0,
                    "masteryItems": [],
                    "masteryXP": 0,
                    "potentialItems": [],
                }
                completed = (quest or {}).get("isFinalBoss") or False
                if os.path.exists("work/persist_progress.flag"):
                    apply_win_progress(qid, pos, cleared, quest)
                battlecomplete = {
                    "x": pos["x"], "y": pos["y"],
                    "cleared": cleared,
                    "visibleClearedCount": len(cleared),
                    "walkableCount": 6,
                    "visibleWalkableCount": 6,
                    "percentHealthGained": 0,
                    "eventPoints": 0,
                    "isFinalBoss": bool(completed),
                    "redeems": redeems,
                    "spends": [],
                    "withHeldItemRedeems": [],
                    "firstCompletionRewards": redeems,
                    "replayCompletionRewards": [],
                    "masteryCompletionRewards": [],
                    "completionRewards": completion_rewards,
                }
                actions = [
                    {"action": {
                        "battlecomplete": battlecomplete,
                        "cleared": cleared,
                        "visibleClearedCount": len(cleared),
                        "walkableCount": 6,
                        "visibleWalkableCount": 6,
                        "percentComplete": 100,
                        "redeems": redeems,
                        "firstCompletionRewards": redeems,
                        "replayCompletionRewards": [],
                        "masteryCompletionRewards": [],
                        "completionRewards": completion_rewards,
                    }},
                ]
                if completed:
                    actions.append({"action": {"questcomplete": {
                        "x": pos["x"], "y": pos["y"], "cleared": cleared,
                    }}})
                data.update({
                    "qid": qid,
                    "battleId": "battle1",
                    "version": 3,
                    "victory": True,
                    "enemyHealth": 0,
                    "rewards": redeems,
                    "redeems": redeems,
                    "firstCompletionRewards": redeems,
                    "completionRewards": completion_rewards,
                    "results": actions,
                    "matchResults": {"battleId": "battle1", "result": 1},
                    "progression": {
                        "version": 3,
                        "currentPos": pos,
                        "cleared": cleared,
                        "previouslyCleared": [],
                        "revealed": [],
                        "currentFightId": "",
                        "currentBattleId": "",
                        "currentBattleBossId": "",
                        "currentBattlePos": pos,
                        "currentBattleEnemyHealth": 0,
                        "users": {},
                        "currentPosition": pos,
                        "playerPosition": pos,
                        "currentTile": pos,
                        "clearedTiles": cleared,
                        "percentComplete": 22,
                    },
                    "teamData": wrapper,
                })
            self.send_sparx(data,
                            assumed_label="[CLIENT: /matches/resolve-match/ win progression + rewards]",
                            async_list=([{"component": "quests", "message": "match-resolved",
                                          "payload": data},
                                         {"component": "quests", "message": "battlecomplete",
                                          "payload": {"matchId": "match_pve_1001", "isWin": True,
                                                      "remainingHP": [0.0, 0.0], "rewards": data.get("rewards", []),
                                                      "withheldRewards": []}},
                                         {"component": "quests", "message": "questcomplete",
                                          "payload": {"qid": qid, "completion": 1.0,
                                                      "rewards": data.get("rewards", []), "nextQid": ""}}]
                                        if won and qid else None))
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
