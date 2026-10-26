import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = json.loads((ROOT / "data" / "rating_table.json").read_text(encoding="utf-8"))["rows"]


class TestRatingInverse(unittest.TestCase):
    def test_equivalent_split_reproduces_every_rating(self):
        for r in ROWS:
            value = r["hero_rating_hp"] + r["hero_rating_attack"]
            self.assertEqual(math.ceil(value), r["rating"],
                             msg=f"{r['bot']} rank={r['rank']} level={r['level']}")

    def test_split_parts_are_non_negative(self):
        for r in ROWS:
            self.assertGreaterEqual(r["hero_rating_hp"], 0)
            self.assertGreaterEqual(r["hero_rating_attack"], 0)

    def test_decomposition_is_labelled_derived(self):
        self.assertEqual(ROWS[0]["decomposition"].startswith("proportional"), True)
        self.assertIn("[DERIVED]", ROWS[0]["decomposition"])

    def test_row_count(self):
        self.assertEqual(len(ROWS), 363)


if __name__ == "__main__":
    unittest.main()
