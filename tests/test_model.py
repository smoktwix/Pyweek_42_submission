"""Check rules against concrete examples from the game design."""

import unittest
from dataclasses import replace
from unittest.mock import patch

from cat_clicker import config
from cat_clicker.model import GameState


class GameStateTests(unittest.TestCase):
    def test_new_round(self):
        state = GameState()
        self.assertEqual((state.points, state.remaining, state.points_per_second), (0, 240, 0))
        self.assertTrue(state.active)
        self.assertTrue(all(count == 0 for count in state.owned.values()))

    def test_only_actual_clicks_generate_manual_points(self):
        state = GameState()
        for _ in range(7):
            self.assertTrue(state.click())
        state.advance(10)
        self.assertEqual(state.points, 7)
        self.assertEqual(state.remaining, 230)

    def test_purchase_charges_current_price_and_increases_next_price(self):
        state = GameState(points=30)
        self.assertTrue(state.buy("cat_petter"))
        self.assertEqual(state.points, 20)
        self.assertEqual(state.price("cat_petter"), 20)
        self.assertTrue(state.buy("cat_petter"))
        self.assertEqual(state.points, 0)
        self.assertEqual(state.price("cat_petter"), 30)
        self.assertEqual(state.points_per_second, 2)

    def test_unaffordable_purchase_changes_nothing(self):
        state = GameState(points=9)
        before = state.owned.copy()
        self.assertFalse(state.buy("cat_petter"))
        self.assertEqual(state.points, 9)
        self.assertEqual(state.owned, before)

    def test_exact_price_is_affordable(self):
        for name, spec in config.UPGRADES.items():
            with self.subTest(upgrade=name):
                state = GameState(points=spec.base_cost)
                self.assertTrue(state.buy(name))
                self.assertEqual(state.points, 0)

    def test_each_limit_and_total_price(self):
        expected = {
            "cat_petter": (10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150),
            "litter_box": (30, 60, 120, 240, 480),
            "yarn_ball": (80, 160, 320, 640, 1280, 2560),
            "cat_house": (5999,),
            "golden_kitty": (50500,),
        }
        for name, prices in expected.items():
            with self.subTest(upgrade=name):
                state = GameState(points=100000)
                for price in prices:
                    self.assertEqual(state.price(name), price)
                    before = state.points
                    self.assertTrue(state.buy(name))
                    self.assertEqual(state.points, before - price)
                self.assertEqual(state.points, 100000 - sum(prices))
                self.assertEqual(state.owned[name], len(prices))
                self.assertTrue(state.at_limit(name))
                self.assertFalse(state.buy(name))
                self.assertEqual(state.points, 100000 - sum(prices))

    def test_five_litter_boxes_compound_speed(self):
        state = GameState(points=1000)
        state.buy("cat_petter")
        for _ in range(5):
            state.buy("litter_box")
        self.assertAlmostEqual(state.points_per_second, 2.48832)

    def test_six_yarn_balls_double_output_each_time(self):
        state = GameState(points=10000)
        state.buy("cat_petter")
        for _ in range(6):
            state.buy("yarn_ball")
        self.assertEqual(state.points_per_second, 64)

    def test_combined_boosts_do_not_affect_house_or_manual_clicks(self):
        state = GameState(points=10000)
        for name in ("cat_petter", "cat_petter", "litter_box", "litter_box", "yarn_ball", "cat_house"):
            state.buy(name)
        self.assertAlmostEqual(state.points_per_second, 105.76)
        before = state.points
        state.click()
        self.assertEqual(state.points - before, 1)

    def test_upgrades_bought_before_petters_apply_to_future_petters(self):
        state = GameState(points=1000)
        state.buy("litter_box")
        state.buy("yarn_ball")
        self.assertEqual(state.points_per_second, 0)
        state.buy("cat_petter")
        self.assertAlmostEqual(state.points_per_second, 2.4)

    def test_fractional_income_is_kept(self):
        state = GameState(points=40)
        state.buy("cat_petter")
        state.buy("litter_box")
        state.advance(0.25)
        self.assertAlmostEqual(state.points, 0.3)
        state.advance(0.75)
        self.assertAlmostEqual(state.points, 1.2)

    def test_income_is_independent_of_frame_rate(self):
        states = [GameState(points=110) for _ in range(2)]
        for state in states:
            state.buy("cat_petter")
            state.buy("cat_petter")
            state.buy("litter_box")
        states[0].advance(10)
        for _ in range(600):
            states[1].advance(1 / 60)
        self.assertAlmostEqual(states[0].points, states[1].points)
        self.assertAlmostEqual(states[0].remaining, states[1].remaining)

    def test_fractional_accumulation_can_pay_exact_price(self):
        state = GameState(points=10)
        state.buy("cat_petter")
        for _ in range(200):
            state.advance(0.1)
        self.assertTrue(state.buy("cat_petter"))
        self.assertAlmostEqual(state.points, 0)

    def test_pause_blocks_income_clock_clicks_and_purchases(self):
        state = GameState(points=100)
        state.buy("cat_petter")
        state.paused = True
        state.advance(1000)
        self.assertEqual((state.points, state.remaining), (90, 240))
        self.assertFalse(state.click())
        self.assertFalse(state.buy("cat_petter"))
        state.paused = False
        state.advance(2)
        self.assertEqual((state.points, state.remaining), (92, 238))

    def test_a_long_frame_only_earns_income_until_deadline(self):
        state = GameState(points=10, duration=2)
        state.buy("cat_petter")
        state.advance(100)
        self.assertEqual((state.points, state.remaining, state.outcome), (2, 0, "lose"))

    def test_full_four_minute_countdown_at_60_fps(self):
        state = GameState()
        for _ in range(14400):
            state.advance(1 / 60)
        self.assertEqual((state.remaining, state.outcome), (0, "lose"))

    def test_having_enough_points_does_not_automatically_win(self):
        state = GameState(points=50500)
        state.advance(240)
        self.assertEqual(state.outcome, "lose")
        self.assertFalse(state.buy("golden_kitty"))

    def test_buying_before_deadline_wins_and_freezes_state(self):
        state = GameState(points=50500)
        state.advance(239.999)
        self.assertTrue(state.buy("golden_kitty"))
        remaining = state.remaining
        state.advance(100)
        self.assertEqual(state.outcome, "win")
        self.assertEqual(state.remaining, remaining)
        self.assertEqual(state.points, 0)
        self.assertFalse(state.click())

    def test_game_settings_are_used_by_new_rounds(self):
        with patch.object(config, "GAME_DURATION", 30), patch.object(config, "STARTING_POINTS", 20), \
                patch.object(config, "POINTS_PER_CLICK", 3):
            state = GameState()
            state.click()
            self.assertEqual((state.remaining, state.points), (30, 23))
        changed = replace(config.UPGRADES["litter_box"], speed_multiplier=1.5)
        with patch.dict(config.UPGRADES, litter_box=changed):
            state = GameState(points=40)
            state.buy("cat_petter")
            state.buy("litter_box")
            self.assertEqual(state.points_per_second, 1.5)

    def test_rounds_do_not_share_purchases(self):
        first = GameState(points=10)
        first.buy("cat_petter")
        second = GameState()
        self.assertEqual(second.owned["cat_petter"], 0)

    def test_invalid_time_is_rejected(self):
        for invalid in (-1, float("inf"), float("nan")):
            with self.subTest(seconds=invalid):
                with self.assertRaises(ValueError):
                    GameState().advance(invalid)
                with self.assertRaises(ValueError):
                    GameState(duration=invalid)
        with self.assertRaises(ValueError):
            GameState(duration=0)


if __name__ == "__main__":
    unittest.main()
