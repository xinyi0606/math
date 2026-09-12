from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, diags, hstack, identity, vstack

from .config import (
    DOWN_REFUND_RATE,
    ENERGY_MAX_KWH,
    ETA_C,
    ETA_D,
    SOC_MAX,
    SOC_MIN,
    UP_PURCHASE_RATE,
)


@dataclass(frozen=True)
class Dispatch:
    success: bool
    status: int
    message: str
    grid: np.ndarray
    charge: np.ndarray
    discharge: np.ndarray
    soc: np.ndarray
    objective: float


def _physical_rows(net: np.ndarray, total_vars: int):
    n = net.size
    eye = identity(n, format="csr")
    lower = csr_matrix(np.tril(np.ones((n, n), dtype=float)))
    tail = total_vars - 3 * n
    zeros_tail = csr_matrix((n, tail))
    balance = hstack((-eye, eye, -eye, zeros_tail), format="csr")
    soc_upper = hstack((csr_matrix((n, n)), ETA_C * lower, -lower / ETA_D, zeros_tail), format="csr")
    soc_lower = -soc_upper
    rows = vstack((balance, soc_upper, soc_lower), format="csr")
    return rows, np.r_[-net, np.full(n, SOC_MAX), np.full(n, -SOC_MIN)]


def solve_dispatch_lp(
    net_energy_kwh: np.ndarray,
    price: np.ndarray | None = None,
    *,
    price_scenarios: np.ndarray | None = None,
    initial_soc: float,
    terminal_soc: float | None = None,
    reference_grid: np.ndarray | None = None,
) -> Dispatch:
    net = np.asarray(net_energy_kwh, dtype=float)
    n = net.size
    if price_scenarios is None:
        if price is None:
            raise ValueError("price or price_scenarios is required")
        scenarios = np.asarray(price, dtype=float).reshape(1, n)
        robust = False
    else:
        scenarios = np.asarray(price_scenarios, dtype=float)
        if scenarios.ndim != 2 or scenarios.shape[1] != n:
            raise ValueError("price_scenarios must have shape (S, n)")
        robust = True
    scenario_count = scenarios.shape[0]

    if reference_grid is None:
        extra = 1 if robust else 0
        total_vars = 3 * n + extra
        objective = np.zeros(total_vars)
        if robust:
            objective[-1] = 1.0
        else:
            objective[:n] = scenarios[0]
        rows, rhs = _physical_rows(net, total_vars)
        if robust:
            scenario_rows = []
            for scenario in scenarios:
                scenario_rows.append(
                    hstack((csr_matrix(scenario.reshape(1, -1)), csr_matrix((1, 2 * n)), csr_matrix([[-1.0]])))
                )
            rows = vstack((rows, *scenario_rows), format="csr")
            rhs = np.r_[rhs - np.r_[np.zeros(n), np.full(n, initial_soc), np.full(n, -initial_soc)], np.zeros(scenario_count)]
        else:
            rhs = rhs - np.r_[np.zeros(n), np.full(n, initial_soc), np.full(n, -initial_soc)]
    else:
        reference = np.asarray(reference_grid, dtype=float)
        if reference.shape != (n,):
            raise ValueError("reference_grid must have shape (n,)")
        u_count = scenario_count * n
        total_vars = 3 * n + u_count + (1 if robust else 0)
        objective = np.zeros(total_vars)
        if robust:
            objective[-1] = 1.0
        else:
            objective[3 * n : 4 * n] = 1.0
        rows, rhs = _physical_rows(net, total_vars)
        rhs = rhs - np.r_[np.zeros(n), np.full(n, initial_soc), np.full(n, -initial_soc)]
        piecewise_rows = []
        piecewise_rhs = []
        for scenario_index, scenario in enumerate(scenarios):
            u_block = -identity(n, format="csr")
            first = hstack((diags(DOWN_REFUND_RATE * scenario), csr_matrix((n, 2 * n)),
                            csr_matrix((n, scenario_index * n)), u_block,
                            csr_matrix((n, u_count - (scenario_index + 1) * n)),
                            csr_matrix((n, 1 if robust else 0))), format="csr")
            second = hstack((diags(UP_PURCHASE_RATE * scenario), csr_matrix((n, 2 * n)),
                             csr_matrix((n, scenario_index * n)), u_block,
                             csr_matrix((n, u_count - (scenario_index + 1) * n)),
                             csr_matrix((n, 1 if robust else 0))), format="csr")
            piecewise_rows.extend((first, second))
            piecewise_rhs.extend((-DOWN_REFUND_RATE * scenario * reference,
                                  DOWN_REFUND_RATE * scenario * reference))
        rows = vstack((rows, *piecewise_rows), format="csr")
        rhs = np.r_[rhs, *piecewise_rhs]
        if robust:
            worst_rows = []
            for scenario_index in range(scenario_count):
                u_part = np.zeros(u_count)
                u_part[scenario_index * n : (scenario_index + 1) * n] = 1.0
                worst_rows.append(
                    hstack((csr_matrix((1, 3 * n)), csr_matrix(u_part.reshape(1, -1)), csr_matrix([[-1.0]])))
                )
            rows = vstack((rows, *worst_rows), format="csr")
            rhs = np.r_[rhs, np.zeros(scenario_count)]

    equality = None
    equality_rhs = None
    if terminal_soc is not None:
        equality = csr_matrix((
            np.r_[np.zeros(n), np.full(n, ETA_C), np.full(n, -1.0 / ETA_D),
                  np.zeros(total_vars - 3 * n)]
        ).reshape(1, -1))
        equality_rhs = np.array([terminal_soc - initial_soc], dtype=float)

    bounds = [(0.0, None)] * n + [(0.0, ENERGY_MAX_KWH)] * (2 * n)
    bounds += [(0.0, None)] * (total_vars - 3 * n)
    result = linprog(
        objective,
        A_ub=rows,
        b_ub=rhs,
        A_eq=equality,
        b_eq=equality_rhs,
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        return Dispatch(False, result.status, result.message, *(np.array([]) for _ in range(4)), float("nan"))
    grid = result.x[:n]
    charge = result.x[n : 2 * n]
    discharge = result.x[2 * n : 3 * n]
    soc = np.r_[initial_soc, initial_soc + np.cumsum(ETA_C * charge - discharge / ETA_D)]
    return Dispatch(True, result.status, result.message, grid, charge, discharge, soc, float(result.fun))


def audit_dispatch(
    dispatch: Dispatch,
    net_energy_kwh: np.ndarray,
    initial_soc: float,
    terminal_soc: float | None = None,
    tolerance: float = 1e-7,
) -> dict[str, float | int]:
    if not dispatch.success:
        return {"solver_success": 0, "balance_violation_kwh": float("inf")}
    net = np.asarray(net_energy_kwh, dtype=float)
    supplied = dispatch.grid + dispatch.discharge - dispatch.charge
    simultaneous = (dispatch.charge > tolerance) & (dispatch.discharge > tolerance)
    terminal_error = 0.0 if terminal_soc is None else abs(dispatch.soc[-1] - terminal_soc)
    return {
        "solver_success": 1,
        "balance_violation_kwh": float(np.maximum(net - supplied, 0.0).max(initial=0.0)),
        "soc_violation_kwh": float(max(SOC_MIN - dispatch.soc.min(), dispatch.soc.max() - SOC_MAX, 0.0)),
        "initial_error_kwh": float(abs(dispatch.soc[0] - initial_soc)),
        "terminal_error_kwh": float(terminal_error),
        "power_violation_kwh": float(max(dispatch.charge.max(initial=0.0) - ENERGY_MAX_KWH,
                                          dispatch.discharge.max(initial=0.0) - ENERGY_MAX_KWH, 0.0)),
        "simultaneous_charge_discharge_count": int(simultaneous.sum()),
    }


def emergency_purchase(actual_net_energy: np.ndarray, dispatch: Dispatch) -> np.ndarray:
    required = np.asarray(actual_net_energy, dtype=float) + dispatch.charge - dispatch.discharge
    return np.maximum(required - dispatch.grid, 0.0)


def adjustment_contract_cost(price: np.ndarray, plan: np.ndarray, adjusted: np.ndarray) -> float:
    price = np.asarray(price, dtype=float)
    plan = np.asarray(plan, dtype=float)
    adjusted = np.asarray(adjusted, dtype=float)
    down = np.maximum(plan - adjusted, 0.0)
    up = np.maximum(adjusted - plan, 0.0)
    return float(price @ plan - DOWN_REFUND_RATE * price @ down + UP_PURCHASE_RATE * price @ up)


def adjustment_components(price: np.ndarray, plan: np.ndarray, adjusted: np.ndarray) -> dict[str, float]:
    price = np.asarray(price, dtype=float)
    plan = np.asarray(plan, dtype=float)
    down = np.maximum(np.asarray(plan) - np.asarray(adjusted), 0.0)
    up = np.maximum(np.asarray(adjusted) - np.asarray(plan), 0.0)
    return {
        "plan_cost_yuan": float(price @ plan),
        "down_refund_yuan": float(DOWN_REFUND_RATE * price @ down),
        "up_purchase_cost_yuan": float(UP_PURCHASE_RATE * price @ up),
    }
