import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGIN = json.loads((ROOT / "server" / "data" / "bcg_login_data.json").read_text(encoding="utf-8"))

HIDDEN = ("armor", "crit_chance", "crit_damage", "perfect_block_chance",
          "block_proficiency", "mana_gain", "mana_start", "resist_magic",
          "resist_physical", "stun_time", "stun_chance")


class TestTeamHiddenAttrs(unittest.TestCase):
    """The quest team payload is the player's battle attribute source."""

    def test_every_rank_entry_has_hidden_attrs(self):
        missing = []
        for bid, ranks in LOGIN["heroes"].items():
            for rank, entry in ranks.items():
                for key in HIDDEN:
                    if key not in entry:
                        missing.append(f"{bid}/{rank}:{key}")
        self.assertEqual(missing, [], msg=missing[:10])

    def test_rank_values_are_the_assumed_defaults(self):
        entry = LOGIN["heroes"]["bumblebee_cin_dotm_2"]["1"]
        self.assertEqual(entry["armor"], 50.0)
        self.assertEqual(entry["crit_chance"], 0.1)
        self.assertEqual(entry["crit_damage"], 1.5)
        self.assertEqual(entry["block_proficiency"], 0.5)
        self.assertEqual(entry["mana_gain"], 1.0)

    def test_login_active_team_heroes_have_hidden_attrs(self):
        teams = LOGIN["userData"]["activeTeams"]
        self.assertTrue(teams)
        for team in teams:
            for bid, hero in team["heroes"].items():
                for key in HIDDEN:
                    self.assertIn(key, hero, msg=f"{team.get('aid')}/{bid}:{key}")


if __name__ == "__main__":
    unittest.main()
