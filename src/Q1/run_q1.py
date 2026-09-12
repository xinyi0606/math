from __future__ import annotations

import json
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.common.config import DT_HOURS, ENERGY_MAX_KWH, ETA_C, ETA_D, SOC_INITIAL
from src.common.data import load_project_data
from src.common.optimization import audit_dispatch, solve_dispatch_lp
from src.common.reporting import copy_official_result, round_directories, write_json, write_q1_workbook


def dynamic_program_cost(net: np.ndarray, price: np.ndarray, grid_step: float) -> float:
    states = np.arange(1200.0, 10800.0 + grid_step / 2.0, grid_step)
    if not np.any(np.isclose(states, SOC_INITIAL)):
        raise ValueError(f"SOC grid {grid_step} does not contain initial state")
    state_count = states.size
    previous = np.full(state_count, np.inf)
    previous[int(np.argmin(abs(states - SOC_INITIAL)))] = 0.0
    delta = states[None, :] - states[:, None]
    charge = np.maximum(delta, 0.0) / ETA_C
    discharge = np.maximum(-delta, 0.0) * ETA_D
    feasible = (charge <= ENERGY_MAX_KWH + 1e-9) & (discharge <= ENERGY_MAX_KWH + 1e-9)
    for slot in range(net.size):
        grid = np.maximum(net[slot] + charge - discharge, 0.0)
        transition = previous[:, None] + price[slot] * grid
        transition[~feasible] = np.inf
        previous = transition.min(axis=0)
    return float(previous[int(np.argmin(abs(states - SOC_INITIAL)))])


def run() -> dict:
    started = time.perf_counter()
    paths = round_directories("Q1")
    data = load_project_data()
    net = (data.q1_load_kw - data.q1_pv_forecast_kw) * DT_HOURS

    baseline_grid = np.maximum(net, 0.0)
    baseline_cost = float(data.fixed_price @ baseline_grid)
    dispatch = solve_dispatch_lp(net, data.fixed_price, initial_soc=SOC_INITIAL, terminal_soc=SOC_INITIAL)
    if not dispatch.success:
        raise RuntimeError(dispatch.message)
    audit = audit_dispatch(dispatch, net, SOC_INITIAL, SOC_INITIAL)
    if audit["simultaneous_charge_discharge_count"]:
        raise RuntimeError("Q1 LP produced simultaneous charge/discharge; MILP upgrade is required")

    convergence = []
    for step in (400.0, 200.0, 100.0, 50.0):
        cost = dynamic_program_cost(net, data.fixed_price, step)
        convergence.append({"soc_grid_kwh": step, "cost_yuan": cost,
                            "gap_to_lp_pct": 100.0 * (cost - dispatch.objective) / dispatch.objective})

    schedule = pd.DataFrame({
        "slot": np.arange(1, 145),
        "time_header": data.time_headers,
        "price_yuan_per_kwh": data.fixed_price,
        "load_kw": data.q1_load_kw,
        "pv_forecast_kw": data.q1_pv_forecast_kw,
        "plan_grid_kwh": dispatch.grid,
        "charge_kwh": dispatch.charge,
        "discharge_kwh": dispatch.discharge,
        "soc_start_kwh": dispatch.soc[:-1],
        "soc_end_kwh": dispatch.soc[1:],
    })
    schedule.to_csv(paths["tables"] / "q1_schedule.csv", index=False)
    pd.DataFrame(convergence).to_csv(paths["tables"] / "q1_dp_grid_convergence.csv", index=False)

    workbook = paths["tables"] / "result1.xlsx"
    write_q1_workbook(workbook, dispatch.grid, dispatch.charge, dispatch.discharge, dispatch.soc)
    official = copy_official_result(workbook, "result1.xlsx")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(data.q1_load_kw, label="Load", linewidth=1.1)
    axes[0].plot(data.q1_pv_forecast_kw, label="PV forecast", linewidth=1.1)
    axes[0].plot(dispatch.grid / DT_HOURS, label="Grid plan", linewidth=1.1)
    axes[0].set_ylabel("Power (kW)")
    axes[0].legend(ncol=3)
    axes[1].plot(dispatch.soc[:-1], color="tab:purple", label="SOC")
    axes[1].set_ylabel("Energy (kWh)")
    axes[1].set_xlabel("10-minute slot")
    axes[1].legend()
    fig.tight_layout()
    figure_path = paths["figures"] / "q1_dispatch.png"
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)

    metrics = {
        "question": "Q1",
        "selected_method": "Q1-M2",
        "baseline_method": "Q1-M1",
        "cross_check_method": "Q1-M3",
        "lp_cost_yuan": dispatch.objective,
        "baseline_cost_yuan": baseline_cost,
        "savings_yuan": baseline_cost - dispatch.objective,
        "savings_pct": 100.0 * (baseline_cost - dispatch.objective) / baseline_cost,
        "total_grid_kwh": float(dispatch.grid.sum()),
        "total_charge_kwh": float(dispatch.charge.sum()),
        "total_discharge_kwh": float(dispatch.discharge.sum()),
        "soc_min_kwh": float(dispatch.soc.min()),
        "soc_max_kwh": float(dispatch.soc.max()),
        "audit": audit,
        "dp_grid_convergence": convergence,
    }
    write_json(paths["metrics"] / "metrics.json", metrics)
    runtime = time.perf_counter() - started
    summary = {
        "status": "PASS",
        "question": "Q1",
        "method": "Q1-M2 continuous linear programming",
        "runtime_seconds": runtime,
        "seed": 2026,
        "input": "data/raw/附件1.xlsx (read-only)",
        "outputs": [str(workbook), str(official), str(figure_path)],
        "audit": audit,
    }
    write_json(paths["root"] / "run_summary.json", summary)
    (paths["logs"] / "run.log").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metrics


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
