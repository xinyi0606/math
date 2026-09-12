import unittest

import numpy as np

from src.common.forecasting import historical_price_scenarios, quantile_reserve
from src.common.optimization import (
    adjustment_contract_cost,
    audit_dispatch,
    solve_dispatch_lp,
)


class FormalModelUnitTest(unittest.TestCase):
    def test_dispatch_lp_respects_balance_soc_and_terminal(self):
        net = np.array([2.0, -3.0, 4.0, 1.0])
        price = np.array([1.0, 0.2, 1.2, 0.8])
        dispatch = solve_dispatch_lp(net, price, initial_soc=6000.0, terminal_soc=6000.0)
        audit = audit_dispatch(dispatch, net, 6000.0, 6000.0)
        self.assertTrue(dispatch.success)
        self.assertLessEqual(audit["balance_violation_kwh"], 1e-7)
        self.assertLessEqual(audit["terminal_error_kwh"], 1e-7)
        self.assertEqual(audit["simultaneous_charge_discharge_count"], 0)

    def test_adjustment_contract_cost_matches_frozen_piecewise_formula(self):
        price = np.array([1.0, 2.0])
        plan = np.array([10.0, 10.0])
        adjusted = np.array([6.0, 13.0])
        expected = 30.0 - 0.5 * 1.0 * 4.0 + 1.5 * 2.0 * 3.0
        self.assertAlmostEqual(adjustment_contract_cost(price, plan, adjusted), expected)

    def test_adjustment_lp_objective_equals_executed_piecewise_cost(self):
        net = np.array([5.0, 1.0, 4.0])
        price = np.array([0.5, 1.5, 1.0])
        reference = np.array([4.0, 4.0, 4.0])
        dispatch = solve_dispatch_lp(net, price, initial_soc=6000.0, reference_grid=reference)
        self.assertTrue(dispatch.success)
        self.assertAlmostEqual(dispatch.objective, adjustment_contract_cost(price, reference, dispatch.grid), places=7)

    def test_historical_price_scenarios_never_use_target_or_future_day(self):
        prices = np.arange(12 * 8, dtype=float).reshape(12, 8)
        scenarios, indices = historical_price_scenarios(prices, day_index=8, start_slot=4, count=3)
        self.assertEqual(scenarios.shape, (3, 4))
        self.assertTrue(np.all(indices < 8))
        np.testing.assert_array_equal(scenarios, prices[indices, 4:])

    def test_robust_adjustment_objective_is_worst_scenario_cost(self):
        net = np.array([5.0, 1.0])
        scenarios = np.array([[1.0, 2.0], [2.0, 1.0]])
        reference = np.array([4.0, 4.0])
        dispatch = solve_dispatch_lp(
            net, price_scenarios=scenarios, initial_soc=6000.0, reference_grid=reference
        )
        self.assertTrue(dispatch.success)
        worst = max(adjustment_contract_cost(price, reference, dispatch.grid) for price in scenarios)
        self.assertAlmostEqual(dispatch.objective, worst, places=7)

    def test_quantile_reserve_uses_only_prior_days(self):
        forecast = np.zeros((10, 4, 6), dtype=float)
        actual = np.zeros((10, 4, 6), dtype=float)
        forecast[:5] = 10.0
        reserve = quantile_reserve(forecast, actual, day_index=5, release_index=2, alpha=0.9)
        self.assertAlmostEqual(reserve, 10.0)
        forecast[5:] = 10_000.0
        unchanged = quantile_reserve(forecast, actual, day_index=5, release_index=2, alpha=0.9)
        self.assertAlmostEqual(unchanged, reserve)


if __name__ == "__main__":
    unittest.main()
