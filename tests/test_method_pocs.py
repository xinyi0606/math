import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MethodPoCTest(unittest.TestCase):
    CASES = {
        "Q1/q1_m1_no_storage_poc.py": ("Q1-M1", "cost_yuan"),
        "Q1/q1_m2_linear_program_poc.py": ("Q1-M2", "cost_yuan"),
        "Q1/q1_m3_dynamic_program_poc.py": ("Q1-M3", "cost_yuan"),
        "Q2/q2_m1_persistence_poc.py": ("Q2-M1", "rmse_kw"),
        "Q2/q2_m2_rolling_mean_poc.py": ("Q2-M2", "rmse_kw"),
        "Q2/q2_m3_gradient_boosting_poc.py": ("Q2-M3", "rmse_kw"),
        "Q3/q3_m1_midnight_only_poc.py": ("Q3-M1", "emergency_proxy_kwh"),
        "Q3/q3_m2_latest_update_poc.py": ("Q3-M2", "emergency_proxy_kwh"),
        "Q3/q3_m3_quantile_reserve_poc.py": ("Q3-M3", "emergency_proxy_kwh"),
        "Q4/q4_m1_no_storage_poc.py": ("Q4-M1", "cost_yuan"),
        "Q4/q4_m2_price_aware_lp_poc.py": ("Q4-M2", "cost_yuan"),
        "Q4/q4_m3_scenario_robust_poc.py": ("Q4-M3", "worst_cost_yuan"),
    }

    def run_poc(self, relative_path):
        path = ROOT / "methods" / relative_path.split("/")[0] / "poc" / relative_path.split("/")[1]
        completed = subprocess.run(
            [sys.executable, str(path)], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_all_candidates_run_on_real_data_and_emit_finite_metrics(self):
        for path, (candidate, primary_metric) in self.CASES.items():
            with self.subTest(candidate=candidate):
                result = self.run_poc(path)
                self.assertEqual(result["candidate"], candidate)
                self.assertTrue(math.isfinite(result[primary_metric]))
                self.assertGreaterEqual(result[primary_metric], 0)
                self.assertGreaterEqual(result["runtime_s"], 0)

    def test_optimization_pocs_respect_terminal_and_balance_tolerances(self):
        for path in (
            "Q1/q1_m1_no_storage_poc.py",
            "Q1/q1_m2_linear_program_poc.py",
            "Q1/q1_m3_dynamic_program_poc.py",
            "Q4/q4_m1_no_storage_poc.py",
            "Q4/q4_m2_price_aware_lp_poc.py",
            "Q4/q4_m3_scenario_robust_poc.py",
        ):
            with self.subTest(path=path):
                result = self.run_poc(path)
                self.assertLessEqual(result["terminal_error_kwh"], 1e-5)
                self.assertLessEqual(result["balance_violation_kwh"], 1e-5)

    def test_quantile_reserve_reports_valid_coverage(self):
        result = self.run_poc("Q3/q3_m3_quantile_reserve_poc.py")
        self.assertGreaterEqual(result["coverage"], 0)
        self.assertLessEqual(result["coverage"], 1)

    def test_forecast_candidates_use_common_out_of_time_windows(self):
        q2 = [self.run_poc(path) for path in (
            "Q2/q2_m1_persistence_poc.py", "Q2/q2_m2_rolling_mean_poc.py",
            "Q2/q2_m3_gradient_boosting_poc.py")]
        q3 = [self.run_poc(path) for path in (
            "Q3/q3_m1_midnight_only_poc.py", "Q3/q3_m2_latest_update_poc.py",
            "Q3/q3_m3_quantile_reserve_poc.py")]
        self.assertEqual({x.get("evaluation_window") for x in q2}, {"2025-01-22..2025-01-28"})
        self.assertEqual({x.get("evaluation_window") for x in q3}, {"2025-01-22..2025-02-04"})

    def test_q2_emergency_risk_evidence_is_reproducible(self):
        paths = (
            "Q2/q2_m1_persistence_poc.py", "Q2/q2_m2_rolling_mean_poc.py",
            "Q2/q2_m3_gradient_boosting_poc.py",
        )
        results = [self.run_poc(path) for path in paths]
        expected = ((64866.84, 261011.20), (66907.21, 273087.94), (15258.78, 54992.61))
        for result, (energy, cost) in zip(results, expected):
            self.assertAlmostEqual(result["underprediction_kwh"], energy, places=2)
            self.assertAlmostEqual(result["emergency_cost_proxy_yuan"], cost, places=2)
        self.assertLess(results[2]["underprediction_p95_kw"], results[0]["underprediction_p95_kw"])
        self.assertLess(results[2]["underprediction_p95_kw"], results[1]["underprediction_p95_kw"])


if __name__ == "__main__":
    unittest.main()
