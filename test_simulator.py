import random
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator import Strategy, monte_carlo, simulate_race, summarize


class SimulatorTests(unittest.TestCase):
    def setUp(self):
        self.wear = {"Soft": 0.1, "Hard": 0.05}

    def test_single_stop_resets_tire_age(self):
        strategy = Strategy("test", [2], ["Soft", "Hard"])
        # Lap wear: 0 + .1, then reset to 0; total 3 baseline laps + pit loss.
        actual = simulate_race(3, 90, 20, self.wear, strategy)
        self.assertAlmostEqual(actual, 290.1)

    def test_equal_strategies_have_expected_time(self):
        strategy = Strategy("test", [2], ["Hard", "Hard"])
        self.assertAlmostEqual(simulate_race(4, 90, 20, self.wear, strategy), 380.1)

    def test_seed_makes_monte_carlo_repeatable(self):
        strategy = Strategy("test", [2], ["Soft", "Hard"])
        args = (5, 90, 20, self.wear, strategy)
        self.assertEqual(monte_carlo(*args, trials=20, seed=4),
                         monte_carlo(*args, trials=20, seed=4))

    def test_summary_reports_average_and_percentiles(self):
        result = summarize([1, 2, 3, 4, 5])
        self.assertEqual(result["mean"], 3)
        self.assertEqual(result["median"], 3)
        self.assertEqual(result["p10"], 1)
        self.assertEqual(result["p90"], 4)

    def test_rejects_pit_on_final_lap(self):
        with self.assertRaises(ValueError):
            simulate_race(3, 90, 20, self.wear,
                          Strategy("test", [3], ["Soft", "Hard"]))


if __name__ == "__main__":
    unittest.main()
