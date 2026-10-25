import sqlite3
import tempfile
import unittest
from pathlib import Path

from server import persistence


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "state.db"
        persistence.init_db(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_schema_version(self):
        with persistence.connect(self.db) as con:
            row = con.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
            self.assertEqual(row["value"], str(persistence.SCHEMA_VERSION))

    def test_account_roundtrip(self):
        persistence.upsert_account("10001", "Commander", 5, 42, "token", path=self.db)
        a = persistence.get_account("10001", path=self.db)
        self.assertEqual(a["name"], "Commander")
        self.assertEqual(a["level"], 5)
        persistence.upsert_account("10001", "Renamed", 6, 50, "token2", path=self.db)
        a = persistence.get_account("10001", path=self.db)
        self.assertEqual(a["name"], "Renamed")
        self.assertEqual(a["xp"], 50)

    def test_roster_upsert(self):
        persistence.upsert_roster("10001", "windblade_gs", 1, 1, pvpb={"a": 1}, path=self.db)
        persistence.upsert_roster("10001", "windblade_gs", 2, 10, pvpb={"a": 2}, path=self.db)
        rows = persistence.get_roster("10001", path=self.db)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["rank"], 2)
        self.assertEqual(rows[0]["level"], 10)
        self.assertIn('"a":2', rows[0]["pvpb"])

    def test_quest_run_roundtrip(self):
        persistence.save_quest_run("10001", "story_act1_ch1_m1", "run1", "story", "active",
                                   team={"heroes": ["bumblebee"]}, state={"x": 1}, path=self.db)
        run = persistence.get_quest_run("10001", "story_act1_ch1_m1", "run1", path=self.db)
        self.assertEqual(run["mode"], "story")
        self.assertEqual(run["team"]["heroes"], ["bumblebee"])
        self.assertEqual(run["state"]["x"], 1)

    def test_reward_ledger(self):
        rid = persistence.add_reward("10001", "quest", "story_act1_ch1_m1",
                                     {"gold": 100}, path=self.db)
        self.assertGreater(rid, 0)
        with persistence.connect(self.db) as con:
            row = con.execute("SELECT COUNT(*) AS n FROM reward_ledger").fetchone()
            self.assertEqual(row["n"], 1)


if __name__ == "__main__":
    unittest.main()
