import unittest
import urllib.request
import json
import os

SERVER_URL = "http://127.0.0.1:8080"
SPEC_FILE = os.path.join(os.path.dirname(__file__), "..", "spec", "openapi.json")

class TestApiSchemas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(SPEC_FILE, "r", encoding="utf-8") as f:
            cls.spec = json.load(f)

    def request_endpoint(self, path, method="GET", body=None):
        url = SERVER_URL + path
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        if data:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw)

    def test_sparx_envelope_on_all_endpoints(self):
        """Every endpoint must return 200 and a valid Sparx envelope with 'ts' and 'result'."""
        endpoints = [
            ("POST", "/auth/init", {"api": 1}),
            ("POST", "/auth/enumerate", {"api": 1}),
            ("POST", "/auth/prelogin", {"api": 1}),
            ("POST", "/auth/login", {"api": 1}),
            ("GET", "/account/data", None),
            ("GET", "/bcg/getLoginData", None),
            ("GET", "/tuning", None),
            ("GET", "/base/active", None),
            ("POST", "/tutorial/get-login-data", {"api": 1}),
            ("GET", "/quests/quest-list", None),
            ("GET", "/quests/quest-active", None),
            ("GET", "/pvp/get-login-data", None),
        ]
        for method, path, body in endpoints:
            status, data = self.request_endpoint(path, method, body)
            self.assertEqual(status, 200, f"{path} returned HTTP {status}")
            self.assertIn("ts", data, f"{path} missing 'ts' in envelope")
            self.assertIn("result", data, f"{path} missing 'result' in envelope")
            self.assertIsInstance(data["ts"], int, f"{path} 'ts' is not integer")

    def test_auth_enumerate_is_array(self):
        """CRITICAL: /auth/enumerate must return a JSON array, NOT a dict."""
        status, data = self.request_endpoint("/auth/enumerate", "POST", {"api": 1})
        self.assertIsInstance(data["result"], list, "/auth/enumerate result must be a list/array")

    def test_account_data_privacy_settings(self):
        """CRITICAL: /account/data must contain privacySettings, invitesDB, maxHelpsPerRequest."""
        status, data = self.request_endpoint("/account/data", "GET")
        res = data["result"]
        self.assertIn("privacySettings", res, "/account/data missing privacySettings")
        self.assertIn("invitesDB", res, "/account/data missing invitesDB")
        self.assertIn("maxHelpsPerRequest", res, "/account/data missing maxHelpsPerRequest")
        self.assertIn("friendsinvite", res["privacySettings"], "privacySettings missing friendsinvite")

    def test_bcg_login_data_required_collections(self):
        """CRITICAL: /bcg/getLoginData must contain attributeGrowthDefs, heroes, blueprints, evoBlueprints."""
        status, data = self.request_endpoint("/bcg/getLoginData", "GET")
        res = data["result"]
        required = ["attributeGrowthDefs", "heroes", "blueprints", "evoBlueprints", "statMods", "synergyBonuses"]
        for key in required:
            self.assertIn(key, res, f"/bcg/getLoginData missing required collection '{key}'")

    def test_base_active_path_data_schema(self):
        """CRITICAL: /base/active must contain pathData with nested 'path' coordinates list."""
        status, data = self.request_endpoint("/base/active", "GET")
        res = data["result"]
        # Can be in user.Base or userBase
        base_mission = res.get("user", {}).get("Base") or res.get("userBase")
        self.assertIsNotNone(base_mission, "/base/active missing base mission")
        self.assertIn("map", base_mission, "base mission missing 'map'")
        map_data = base_mission["map"]
        self.assertIn("pathData", map_data, "map missing 'pathData' key")
        self.assertIsInstance(map_data["pathData"], list, "pathData must be a list")
        self.assertGreater(len(map_data["pathData"]), 0, "pathData must not be empty")
        first_path = map_data["pathData"][0]
        self.assertIn("path", first_path, "pathData item missing 'path' key")
        self.assertIsInstance(first_path["path"], list, "'path' must be a list of coordinates")
        first_coord = first_path["path"][0]
        self.assertIn("x", first_coord, "coordinate missing 'x'")
        self.assertIn("y", first_coord, "coordinate missing 'y'")

    def test_tutorial_wire_format(self):
        """CRITICAL: Tutorial wire format must use 's' for state and 'current_bid' for branch ID."""
        status, data = self.request_endpoint("/tutorial/get-login-data", "POST", {"api": 1})
        res = data["result"]
        self.assertIn("FTE", res, "Tutorial data missing FTE")
        fte = res["FTE"]
        self.assertIn("s", fte, "FTE missing key 's'")
        self.assertEqual(fte["s"], "completed", "FTE state 's' is not completed")
        self.assertIn("current_bid", fte, "FTE missing key 'current_bid'")

    def test_quest_list_is_array(self):
        """CRITICAL: /quests/quest-list must return a list/array for QuestsAPI.GetAvailableQuests."""
        status, data = self.request_endpoint("/quests/quest-list", "GET")
        self.assertIsInstance(data["result"], list, "/quests/quest-list result must be a list/array")

if __name__ == "__main__":
    unittest.main()
