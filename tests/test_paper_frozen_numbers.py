import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PaperFrozenNumbersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads((ROOT / "paper/frozen_numbers.json").read_text(encoding="utf-8"))
        cls.q1 = json.loads((ROOT / "results/Q1/experiments/round1/metrics/metrics.json").read_text(encoding="utf-8"))
        cls.q2 = json.loads((ROOT / "results/Q2/experiments/round1/metrics/metrics.json").read_text(encoding="utf-8"))
        cls.q3 = json.loads((ROOT / "results/Q3/experiments/round2/metrics/metrics.json").read_text(encoding="utf-8"))
        cls.q4 = json.loads((ROOT / "results/Q4/experiments/round2/metrics/metrics.json").read_text(encoding="utf-8"))

    def test_q1_headline_values(self):
        self.assertAlmostEqual(self.frozen["Q1"]["lp_cost_yuan"], self.q1["lp_cost_yuan"], places=2)
        self.assertAlmostEqual(self.frozen["Q1"]["savings_pct"], self.q1["savings_pct"], places=2)

    def test_q2_headline_values(self):
        method = self.q2["methods"]["m3"]
        self.assertAlmostEqual(self.frozen["Q2"]["rmse_kw"], method["rmse_kw"], places=2)
        self.assertAlmostEqual(self.frozen["Q2"]["annual_total_cost_yuan"], method["annual_total_cost_yuan"], places=2)

    def test_q3_headline_values(self):
        method = self.q3["methods"]["m3"]
        self.assertEqual(self.frozen["Q3"]["reserve_alpha"], self.q3["reserve_alpha"])
        self.assertAlmostEqual(self.frozen["Q3"]["annual_emergency_kwh"], method["annual_emergency_kwh"], places=2)

    def test_q4_headline_values(self):
        method = self.q4["q4_3"]["m3"]
        self.assertAlmostEqual(self.frozen["Q4"]["Q4_3_total_cost_yuan"], method["annual_total_cost_yuan"], places=2)
        self.assertEqual(self.frozen["Q4"]["future_price_leakage_count"], method["future_price_leakage_count"])

    def test_bootstrap_intervals_have_expected_direction(self):
        self.assertGreater(self.frozen["Q2"]["daily_cost_saving_block_bootstrap_95ci_yuan"][0], 0)
        self.assertGreater(self.frozen["Q3"]["daily_added_cost_block_bootstrap_95ci_yuan"][0], 0)
        self.assertGreater(self.frozen["Q3"]["daily_emergency_reduction_block_bootstrap_95ci_kwh"][0], 0)


if __name__ == "__main__":
    unittest.main()
