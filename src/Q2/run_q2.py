from __future__ import annotations

import json
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.common.config import (
    DT_HOURS,
    EMERGENCY_MULTIPLIER,
    OUTPUT_START_INDEX,
    SOC_INITIAL,
)
from src.common.data import load_project_data
from src.common.forecasting import cached_net_load_forecasts
from src.common.optimization import audit_dispatch, emergency_purchase, solve_dispatch_lp
from src.common.reporting import copy_official_result, round_directories, write_json, write_q2_workbook


METHOD_LABELS = {"m1": "Q2-M1 persistence", "m2": "Q2-M2 7-day mean", "m3": "Q2-M3 gradient boosting"}


def _warmup_soc(data) -> float:
    actual_net = (data.load_kw - data.pv_actual_kw) * DT_HOURS
    initial_typical = (data.q1_load_kw - data.q1_pv_forecast_kw) * DT_HOURS
    soc = SOC_INITIAL
    for day in range(OUTPUT_START_INDEX):
        if day == 0:
            predicted = initial_typical
        else:
            predicted = actual_net[max(0, day - 7) : day].mean(axis=0)
        dispatch = solve_dispatch_lp(predicted, data.fixed_price, initial_soc=soc)
        if not dispatch.success:
            raise RuntimeError(f"January warmup day {day} failed: {dispatch.message}")
        soc = float(dispatch.soc[-1])
    return soc


def _simulate_method(data, prediction_kw: np.ndarray, start_soc: float):
    days = data.dates[OUTPUT_START_INDEX:]
    count = days.size
    plan = np.zeros((count, 144))
    charge = np.zeros_like(plan)
    discharge = np.zeros_like(plan)
    emergency = np.zeros_like(plan)
    soc = np.zeros((count, 145))
    plan_cost = np.zeros(count)
    emergency_cost = np.zeros(count)
    audits = []
    current_soc = start_soc
    actual_net = (data.load_kw - data.pv_actual_kw) * DT_HOURS
    for out_index, day in enumerate(range(OUTPUT_START_INDEX, 365)):
        terminal = SOC_INITIAL if day == 364 else None
        dispatch = solve_dispatch_lp(
            prediction_kw[day] * DT_HOURS,
            data.fixed_price,
            initial_soc=current_soc,
            terminal_soc=terminal,
        )
        if not dispatch.success:
            raise RuntimeError(f"Q2 day {day} failed: {dispatch.message}")
        audit = audit_dispatch(dispatch, prediction_kw[day] * DT_HOURS, current_soc, terminal)
        if audit["simultaneous_charge_discharge_count"]:
            raise RuntimeError(f"Q2 day {day} has simultaneous charge/discharge")
        plan[out_index] = dispatch.grid
        charge[out_index] = dispatch.charge
        discharge[out_index] = dispatch.discharge
        soc[out_index] = dispatch.soc
        emergency[out_index] = emergency_purchase(actual_net[day], dispatch)
        plan_cost[out_index] = data.fixed_price @ dispatch.grid
        emergency_cost[out_index] = EMERGENCY_MULTIPLIER * data.fixed_price @ emergency[out_index]
        audits.append(audit)
        current_soc = float(dispatch.soc[-1])
    return {
        "dates": days,
        "plan": plan,
        "charge": charge,
        "discharge": discharge,
        "soc": soc,
        "emergency": emergency,
        "plan_cost": plan_cost,
        "emergency_cost": emergency_cost,
        "total_cost": plan_cost + emergency_cost,
        "audits": audits,
    }


def _metrics(data, forecast: np.ndarray, result: dict) -> dict:
    actual = data.load_kw[OUTPUT_START_INDEX:] - data.pv_actual_kw[OUTPUT_START_INDEX:]
    predicted = forecast[OUTPUT_START_INDEX:]
    error = actual - predicted
    under = np.maximum(error, 0.0)
    return {
        "rmse_kw": float(np.sqrt(np.mean(error ** 2))),
        "mae_kw": float(np.mean(abs(error))),
        "underprediction_p95_kw": float(np.quantile(under, 0.95)),
        "annual_plan_cost_yuan": float(result["plan_cost"].sum()),
        "annual_emergency_cost_yuan": float(result["emergency_cost"].sum()),
        "annual_total_cost_yuan": float(result["total_cost"].sum()),
        "annual_plan_grid_kwh": float(result["plan"].sum()),
        "annual_emergency_kwh": float(result["emergency"].sum()),
        "emergency_rate": float(result["emergency"].sum() / ((data.load_kw[OUTPUT_START_INDEX:] * DT_HOURS).sum())),
        "worst_day_cost_yuan": float(result["total_cost"].max()),
        "terminal_soc_kwh": float(result["soc"][-1, -1]),
        "max_balance_violation_kwh": max(a["balance_violation_kwh"] for a in result["audits"]),
        "max_soc_violation_kwh": max(a["soc_violation_kwh"] for a in result["audits"]),
        "simultaneous_charge_discharge_count": sum(a["simultaneous_charge_discharge_count"] for a in result["audits"]),
    }


def run() -> dict:
    started = time.perf_counter()
    paths = round_directories("Q2")
    data = load_project_data()
    net_kw = data.load_kw - data.pv_actual_kw
    cache_path = paths["tables"] / "net_load_forecasts.npz"
    forecasts, cache_hit = cached_net_load_forecasts(net_kw, cache_path)
    warmup_soc = _warmup_soc(data)

    results = {}
    metrics = {}
    for method in ("m1", "m2", "m3"):
        results[method] = _simulate_method(data, forecasts[method], warmup_soc)
        metrics[method] = _metrics(data, forecasts[method], results[method])

    chosen = results["m3"]
    workbook = paths["tables"] / "result2.xlsx"
    write_q2_workbook(
        workbook,
        chosen["dates"],
        chosen["plan"],
        chosen["plan_cost"],
        chosen["charge"],
        chosen["discharge"],
        chosen["soc"],
        chosen["emergency"],
    )
    official = copy_official_result(workbook, "result2.xlsx")

    rows = []
    for method, result in results.items():
        for index, date in enumerate(result["dates"]):
            rows.append({
                "date": str(date.astype("datetime64[D]")),
                "method": method,
                "plan_cost_yuan": result["plan_cost"][index],
                "emergency_cost_yuan": result["emergency_cost"][index],
                "total_cost_yuan": result["total_cost"][index],
                "emergency_kwh": result["emergency"][index].sum(),
                "soc_start_kwh": result["soc"][index, 0],
                "soc_end_kwh": result["soc"][index, -1],
            })
    daily = pd.DataFrame(rows)
    daily.to_csv(paths["tables"] / "q2_daily_metrics.csv", index=False)

    chosen_rows = []
    for day_index, date in enumerate(chosen["dates"]):
        for slot in range(144):
            chosen_rows.append((str(date), slot + 1, forecasts["m3"][OUTPUT_START_INDEX + day_index, slot],
                                chosen["plan"][day_index, slot], chosen["charge"][day_index, slot],
                                chosen["discharge"][day_index, slot], chosen["emergency"][day_index, slot],
                                chosen["soc"][day_index, slot], chosen["soc"][day_index, slot + 1]))
    pd.DataFrame(chosen_rows, columns=["date", "slot", "forecast_net_kw", "plan_grid_kwh", "charge_kwh",
                                               "discharge_kwh", "emergency_kwh", "soc_start_kwh", "soc_end_kwh"]).to_csv(
        paths["tables"] / "q2_m3_full_schedule.csv.gz", index=False, compression="gzip")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for method in ("m1", "m2", "m3"):
        subset = daily[daily.method == method]
        axes[0].plot(pd.to_datetime(subset.date), subset.total_cost_yuan.rolling(14, min_periods=1).mean(),
                     label=METHOD_LABELS[method], linewidth=1)
        axes[1].plot(pd.to_datetime(subset.date), subset.emergency_kwh.cumsum(), label=METHOD_LABELS[method], linewidth=1)
    axes[0].set_ylabel("14-day mean cost (yuan)")
    axes[1].set_ylabel("Cumulative emergency (kWh)")
    axes[1].set_xlabel("Date")
    axes[0].legend(ncol=3, fontsize=8)
    fig.tight_layout()
    figure_path = paths["figures"] / "q2_method_comparison.png"
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)

    payload = {
        "question": "Q2",
        "selected_method": "Q2-M3",
        "forecast_cache_hit": cache_hit,
        "common_warmup_soc_2025_02_01_kwh": warmup_soc,
        "methods": metrics,
    }
    write_json(paths["metrics"] / "metrics.json", payload)
    summary = {
        "status": "PASS",
        "question": "Q2",
        "method": "Q2-M3 gradient boosting plus daily receding-horizon LP",
        "runtime_seconds": time.perf_counter() - started,
        "seed": 2026,
        "information_boundary": "Each day uses only rows strictly before the target day",
        "forecast_cache_hit": cache_hit,
        "outputs": [str(workbook), str(official), str(figure_path)],
        "chosen_metrics": metrics["m3"],
    }
    write_json(paths["root"] / "run_summary.json", summary)
    (paths["logs"] / "run.log").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
