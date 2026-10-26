"""R2.1: direct transcription of GameUtil.CalculateModifiedHeroRating."""
import math
import unittest


def calculate_modified_hero_rating(hp, atk, atk_base, class_power,
                                   class_weight, hp_weight=0.2,
                                   attack_weight=1.0, modifier=0.0,
                                   precision=1.0, ideal=True):
    # 0xA4826C..0xA48608
    extra = atk_base * class_weight * class_power
    extra *= attack_weight if ideal else precision
    hp_part = hp * (1.0 - modifier * hp_weight)
    # 0xA48728..0xA48744
    return math.ceil(hp_part + atk + extra)


class TestRatingFormula(unittest.TestCase):
    def test_plain_sum(self):
        self.assertEqual(calculate_modified_hero_rating(1000, 120, 0, 1.0, 0.05), 1120)

    def test_hp_weight_modifier(self):
        self.assertEqual(
            calculate_modified_hero_rating(1000, 120, 0, 1.0, 0.05, modifier=1.0),
            920,
        )

    def test_ideal_branch_uses_attack_bonus(self):
        self.assertEqual(
            calculate_modified_hero_rating(1000, 100, 50, 1.2, 0.10, ideal=True),
            1106,
        )

    def test_non_ideal_branch_uses_penalty_and_precision(self):
        self.assertEqual(
            calculate_modified_hero_rating(1000, 100, 50, 1.2, 0.10,
                                           ideal=False, precision=1.0),
            1106,
        )

    def test_ceil_not_round(self):
        # 10 + 0.1 -> 10.1 -> 11, not 10.
        self.assertEqual(
            calculate_modified_hero_rating(10, 0, 1, 0.1, 1.0, ideal=True),
            11,
        )

    def test_attack_weight_changes_extra(self):
        base = calculate_modified_hero_rating(1000, 100, 50, 1.0, 0.1,
                                              attack_weight=1.0)
        half = calculate_modified_hero_rating(1000, 100, 50, 1.0, 0.1,
                                              attack_weight=0.5)
        self.assertEqual(base, 1105)
        self.assertEqual(half, 1103)


if __name__ == "__main__":
    unittest.main()
