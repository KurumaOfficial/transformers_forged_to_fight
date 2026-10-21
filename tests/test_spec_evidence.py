import json
import os
import unittest

SPEC = os.path.join(os.path.dirname(__file__), "..", "spec", "openapi.json")


class TestSpecEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SPEC, "r", encoding="utf-8") as f:
            cls.spec = json.load(f)

    def test_openapi_version(self):
        self.assertEqual(self.spec["openapi"], "3.0.3")

    def test_every_path_has_evidence(self):
        for path, item in self.spec["paths"].items():
            for method, op in item.items():
                if method not in ("get", "post", "put", "delete", "patch"):
                    continue
                self.assertIn("x-evidence", op, f"{method.upper()} {path} missing x-evidence")
                self.assertIn("x-client-behavior", op, f"{method.upper()} {path} missing x-client-behavior")
                self.assertTrue(op["x-evidence"], f"{method.upper()} {path} empty x-evidence")

    def test_nullable_is_30x_syntax(self):
        """3.0.3 uses nullable: true, not type: [..., null]."""
        raw = json.dumps(self.spec)
        self.assertNotIn('"type": ["', raw, "3.1-style union type found")
        self.assertIn("nullable", raw)

    def test_info_explains_test_scope(self):
        desc = self.spec["info"]["description"]
        self.assertIn("internal consistency", desc)
        self.assertIn("DO NOT prove client compatibility", desc)

    def test_observed_paths_present(self):
        observed = [
            "/auth/init", "/auth/enumerate", "/auth/prelogin", "/auth/login",
            "/account/data", "/bcg/getLoginData", "/tuning", "/base/active",
            "/quests/quest-list", "/quests/quest-active", "/quests/quest-progression",
            "/quests/quest-detail/{qid}", "/inventory", "/chat/data",
            "/autorefresh/grouprefresh", "/userprofile/", "/telemetry",
        ]
        for p in observed:
            self.assertIn(p, self.spec["paths"], f"observed path missing from spec: {p}")


if __name__ == "__main__":
    unittest.main()
