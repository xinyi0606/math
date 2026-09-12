from __future__ import annotations

import json
import time
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.Q2.run_q2 import _warmup_soc
from src.common.config import (
    DT_HOURS,
    EMERGENCY_MULTIPLIER,
    OUTPUT_START_INDEX,
    RELEASE_START_SLOTS,
    RESERVE_ALPHA,
    RESULTS,
    SOC_INITIAL,
)
from src.common.data import interpolate_pv_forecast, load_project_data, six_hour_forecast_blocks
from src.common.forecasting import cached_net_load_forecasts, quantile_reserve
from src.common.optimization import (
    Dispatch,
    adjustment_components,
    adjustment_contract_cost,
    audit_dispatch,
    solve_dispatch_lp,
)
from src.common.reporting import copy_official_result, round_directories, write_json, write_q3_workbook


METHOD_LABELS = {"m1": "Q3-M1 midnight only", "m2": "Q3-M2 rolling point", "m3": "Q3-M3 rolling quantile"}


def _assembled_dispatch(grid, charge, discharge, soc):
    return Dispatch(True, 0, "assembled rolling dispatch", grid, charge, discharge, soc, float("nan"))


def _precompute_pv(data):
    forecasts = np.zeros((365, 4, 144))
    for day in range(365):
        for release in range(4):
            forecasts[day, release] = interpolate_pv_forecast(data, day, release)
    return forecasts


def _simulate_method(
    data, net_forecast_kw, pv_10min, forecast_blocks, actual_blocks, method, start_soc,
    reserve_alpha=RESERVE_ALPHA,
):
    dates = data.dates[OUTPUT_START_INDEX:]
    count = dates.size
    arrays = {name: np.zeros((count, 144)) for name in
              ("plan", "adjusted", "charge", "discharge", "emergency", "executed_pv_forecast")}
    arrays["soc"] = np.zeros((count, 145))
    costs = {name: np.zeros(count) for name in
             ("plan", "contract", "down_refund", "up_purchase", "emergency", "total")}
    reserves = np.zeros((count, 4))
    audits = []
    current_soc = start_soc
    actual_net_energy = (data.load_kw - data.pv_actual_kw) * DT_HOURS

    for out_index, day in enumerate(range(OUTPUT_START_INDEX, 365)):
        pv_midnight = pv_10min[day, 0]
        load_forecast = np.maximum(net_forecast_kw[day] + pv_midnight, 0.0)
        if method == "m3":
            reserves[out_index, 0] = quantile_reserve(forecast_blocks, actual_blocks, day, 0, reserve_alpha)
        pv_safe = np.maximum(pv_midnight - reserves[out_index, 0], 0.0)
        plan_net = (load_forecast - pv_safe) * DT_HOURS
        terminal = SOC_INITIAL if day == 364 else None
        plan_dispatch = solve_dispatch_lp(plan_net, data.fixed_price, initial_soc=current_soc, terminal_soc=terminal)
        if not plan_dispatch.success:
            raise RuntimeError(f"Q3 {method} day {day} plan failed: {plan_dispatch.message}")

        grid = plan_dispatch.grid.copy()
        charge = plan_dispatch.charge.copy()
        discharge = plan_dispatch.discharge.copy()
        soc = plan_dispatch.soc.copy()
        executed_prediction = pv_safe.copy()
        plan_grid = plan_dispatch.grid.copy()

        if method in ("m2", "m3"):
            for release in range(1, 4):
                start = RELEASE_START_SLOTS[release]
                if method == "m3":
                    reserves[out_index, release] = quantile_reserve(
                        forecast_blocks, actual_blocks, day, release, reserve_alpha
                    )
                latest_pv = np.maximum(pv_10min[day, release] - reserves[out_index, release], 0.0)
                remaining_net = (load_forecast[start:] - latest_pv[start:]) * DT_HOURS
                update = solve_dispatch_lp(
                    remaining_net,
                    data.fixed_price[start:],
                    initial_soc=float(soc[start]),
                    terminal_soc=terminal,
                    reference_grid=plan_grid[start:],
                )
                if not update.success:
                    raise RuntimeError(f"Q3 {method} day {day} release {release} failed: {update.message}")
                grid[start:] = update.grid
                charge[start:] = update.charge
                discharge[start:] = update.discharge
                soc[start:] = update.soc
                executed_prediction[start:] = latest_pv[start:]

        execution_net = (load_forecast - executed_prediction) * DT_HOURS
        dispatch = _assembled_dispatch(grid, charge, discharge, soc)
        audit = audit_dispatch(dispatch, execution_net, current_soc, terminal)
        if audit["simultaneous_charge_discharge_count"]:
            raise RuntimeError(f"Q3 {method} day {day} has simultaneous charge/discharge")
        emergency = np.maximum(actual_net_energy[day] + charge - discharge - grid, 0.0)
        components = adjustment_components(data.fixed_price, plan_grid, grid)
        contract = adjustment_contract_cost(data.fixed_price, plan_grid, grid)

        arrays["plan"][out_index] = plan_grid
        arrays["adjusted"][out_index] = grid
        arrays["charge"][out_index] = charge
        arrays["discharge"][out_index] = discharge
        arrays["soc"][out_index] = soc
        arrays["emergency"][out_index] = emergency
        arrays["executed_pv_forecast"][out_index] = executed_prediction
        costs["plan"][out_index] = components["plan_cost_yuan"]
        costs["contract"][out_index] = contract
        costs["down_refund"][out_index] = components["down_refund_yuan"]
        costs["up_purchase"][out_index] = components["up_purchase_cost_yuan"]
        costs["emergency"][out_index] = EMERGENCY_MULTIPLIER * data.fixed_price @ emergency
        costs["total"][out_index] = contract + costs["emergency"][out_index]
        audits.append(audit)
        current_soc = float(soc[-1])
    return {"dates": dates, **arrays, "costs": costs, "reserves": reserves, "audits": audits}


def _method_metrics(data, result):
    actual_pv = data.pv_actual_kw[OUTPUT_START_INDEX:]
    pv_error = actual_pv - result["executed_pv_forecast"]
    return {
        "pv_rmse_kw": float(np.sqrt(np.mean(pv_error ** 2))),
        "pv_mae_kw": float(np.mean(abs(pv_error))),
        "safe_pv_coverage": float(np.mean(actual_pv >= result["executed_pv_forecast"])),
        "annual_plan_cost_yuan": float(result["costs"]["plan"].sum()),
        "annual_contract_cost_yuan": float(result["costs"]["contract"].sum()),
        "annual_down_refund_yuan": float(result["costs"]["down_refund"].sum()),
        "annual_up_purchase_cost_yuan": float(result["costs"]["up_purchase"].sum()),
        "annual_emergency_cost_yuan": float(result["costs"]["emergency"].sum()),
        "annual_total_cost_yuan": float(result["costs"]["total"].sum()),
        "annual_emergency_kwh": float(result["emergency"].sum()),
        "worst_day_cost_yuan": float(result["costs"]["total"].max()),
        "mean_reserve_kw": float(result["reserves"].mean()),
        "terminal_soc_kwh": float(result["soc"][-1, -1]),
        "max_balance_violation_kwh": max(a["balance_violation_kwh"] for a in result["audits"]),
        "max_soc_violation_kwh": max(a["soc_violation_kwh"] for a in result["audits"]),
        "simultaneous_charge_discharge_count": sum(a["simultaneous_charge_discharge_count"] for a in result["audits"]),
    }


def run(round_number: int = 2, reserve_alpha: float = RESERVE_ALPHA) -> dict:
    started = time.perf_counter()
    paths = round_directories("Q3", round_number)
    data = load_project_data()
    q2_cache = RESULTS / "Q2" / "experiments" / "round1" / "tables" / "net_load_forecasts.npz"
    net_forecasts, cache_hit = cached_net_load_forecasts(data.load_kw - data.pv_actual_kw, q2_cache)
    pv_10min = _precompute_pv(data)
    forecast_blocks, actual_blocks = six_hour_forecast_blocks(data)
    start_soc = _warmup_soc(data)

    results = {}
    metrics = {}
    for method in ("m1", "m2", "m3"):
        results[method] = _simulate_method(
            data, net_forecasts["m3"], pv_10min, forecast_blocks, actual_blocks, method, start_soc,
            reserve_alpha=reserve_alpha,
        )
        metrics[method] = _method_metrics(data, results[method])

    sensitivity = []
    for alpha in (0.80, 0.90, 0.95, 0.975, 0.99):
        if np.isclose(alpha, reserve_alpha):
            sensitivity_result = results["m3"]
        else:
            sensitivity_result = _simulate_method(
                data, net_forecasts["m3"], pv_10min, forecast_blocks, actual_blocks,
                "m3", start_soc, reserve_alpha=alpha,
            )
        sensitivity_metrics = _method_metrics(data, sensitivity_result)
        sensitivity.append({"alpha": alpha, **sensitivity_metrics})
    pd.DataFrame(sensitivity).to_csv(paths["tables"] / "q3_reserve_sensitivity.csv", index=False)

    chosen = results["m3"]
    workbook = paths["tables"] / "result3.xlsx"
    write_q3_workbook(
        workbook,
        chosen["dates"],
        chosen["plan"],
        chosen["costs"]["plan"],
        chosen["adjusted"],
        chosen["costs"]["contract"],
        chosen["charge"],
        chosen["discharge"],
        chosen["soc"],
        chosen["emergency"],
    )
    official = copy_official_result(workbook, "result3.xlsx")

    daily_rows = []
    for method, result in results.items():
        for index, date in enumerate(result["dates"]):
            daily_rows.append({
                "date": str(date), "method": method,
                "plan_cost_yuan": result["costs"]["plan"][index],
                "contract_cost_yuan": result["costs"]["contract"][index],
                "emergency_cost_yuan": result["costs"]["emergency"][index],
                "total_cost_yuan": result["costs"]["total"][index],
                "emergency_kwh": result["emergency"][index].sum(),
                "mean_reserve_kw": result["reserves"][index].mean(),
                "soc_start_kwh": result["soc"][index, 0],
                "soc_end_kwh": result["soc"][index, -1],
            })
    daily = pd.DataFrame(daily_rows)
    daily.to_csv(paths["tables"] / "q3_daily_metrics.csv", index=False)

    detail = []
    for day_index, date in enumerate(chosen["dates"]):
        for slot in range(144):
            detail.append((str(date), slot + 1, chosen["plan"][day_index, slot], chosen["adjusted"][day_index, slot],
                           chosen["charge"][day_index, slot], chosen["discharge"][day_index, slot],
                           chosen["emergency"][day_index, slot], chosen["executed_pv_forecast"][day_index, slot],
                           chosen["soc"][day_index, slot], chosen["soc"][day_index, slot + 1]))
    pd.DataFrame(detail, columns=["date", "slot", "plan_grid_kwh", "adjusted_grid_kwh", "charge_kwh",
                                         "discharge_kwh", "emergency_kwh", "executed_pv_forecast_kw",
                                         "soc_start_kwh", "soc_end_kwh"]).to_csv(
        paths["tables"] / "q3_m3_full_schedule.csv.gz", index=False, compression="gzip")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for method in ("m1", "m2", "m3"):
        subset = daily[daily.method == method]
        axes[0].plot(pd.to_datetime(subset.date), subset.total_cost_yuan.rolling(14, min_periods=1).mean(),
                     label=METHOD_LABELS[method], linewidth=1)
        axes[1].plot(pd.to_datetime(subset.date), subset.emergency_kwh.cumsum(),
                     label=METHOD_LABELS[method], linewidth=1)
    axes[0].set_ylabel("14-day mean cost (yuan)")
    axes[1].set_ylabel("Cumulative emergency (kWh)")
    axes[1].set_xlabel("Date")
    axes[0].legend(ncol=3, fontsize=8)
    fig.tight_layout()
    figure_path = paths["figures"] / "q3_method_comparison.png"
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)

    payload = {
        "question": "Q3", "round": round_number, "selected_method": "Q3-M3",
        "reserve_alpha": reserve_alpha, "q2_forecast_cache_hit": cache_hit,
        "common_warmup_soc_2025_02_01_kwh": start_soc, "methods": metrics,
        "reserve_sensitivity": sensitivity,
    }
    write_json(paths["metrics"] / "metrics.json", payload)
    summary = {
        "status": "PASS", "question": "Q3", "round": round_number,
        "method": "Q3-M3 rolling quantile-reserve LP",
        "reserve_alpha": reserve_alpha,
        "runtime_seconds": time.perf_counter() - started, "seed": 2026,
        "information_boundary": "Each release freezes executed slots and uses only historical reserve errors",
        "outputs": [str(workbook), str(official), str(figure_path)], "chosen_metrics": metrics["m3"],
    }
    write_json(paths["root"] / "run_summary.json", summary)
    (paths["logs"] / "run.log").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Q3 rolling optimization experiment.")
    parser.add_argument("--round-number", type=int, default=2)
    parser.add_argument("--reserve-alpha", type=float, default=RESERVE_ALPHA)
    args = parser.parse_args()
    print(json.dumps(run(args.round_number, args.reserve_alpha), ensure_ascii=False, indent=2))
