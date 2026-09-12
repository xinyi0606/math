from __future__ import annotations

import json
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.Q3.run_q3 import _assembled_dispatch, _precompute_pv
from src.common.config import (
    DT_HOURS,
    EMERGENCY_MULTIPLIER,
    OUTPUT_START_INDEX,
    PRICE_SCENARIO_COUNT,
    RELEASE_START_SLOTS,
    RESERVE_ALPHA,
    RESULTS,
    SOC_INITIAL,
)
from src.common.data import load_project_data, six_hour_forecast_blocks
from src.common.forecasting import cached_net_load_forecasts, historical_price_scenarios, quantile_reserve
from src.common.optimization import (
    Dispatch,
    adjustment_components,
    adjustment_contract_cost,
    audit_dispatch,
    solve_dispatch_lp,
)
from src.common.reporting import (
    copy_official_result,
    round_directories,
    write_json,
    write_q2_workbook,
    write_q3_workbook,
)


PRICE_METHODS = ("m1", "m2", "m3")
METHOD_LABELS = {"m1": "Q4-M1 no storage", "m2": "Q4-M2 perfect-price oracle", "m3": "Q4-M3 historical scenarios"}


def _january_prediction(data, day):
    actual_net = data.load_kw - data.pv_actual_kw
    if day == 0:
        return data.q1_load_kw - data.q1_pv_forecast_kw
    return actual_net[max(0, day - 7) : day].mean(axis=0)


def _warmup_states(data):
    states = {"m1": SOC_INITIAL, "m2": SOC_INITIAL, "m3": SOC_INITIAL}
    for day in range(OUTPUT_START_INDEX):
        predicted = _january_prediction(data, day) * DT_HOURS
        oracle = solve_dispatch_lp(predicted, data.variable_price[day], initial_soc=states["m2"])
        if not oracle.success:
            raise RuntimeError(f"Q4 oracle warmup day {day} failed")
        states["m2"] = float(oracle.soc[-1])
        if day > 0:
            scenarios, _ = historical_price_scenarios(
                data.variable_price, day, 0, PRICE_SCENARIO_COUNT
            )
            robust = solve_dispatch_lp(predicted, price_scenarios=scenarios, initial_soc=states["m3"])
            if not robust.success:
                raise RuntimeError(f"Q4 robust warmup day {day} failed")
            states["m3"] = float(robust.soc[-1])
    return states


def _empty_result(dates):
    count = dates.size
    result = {name: np.zeros((count, 144)) for name in
              ("plan", "adjusted", "charge", "discharge", "emergency", "executed_pv_forecast")}
    result["soc"] = np.zeros((count, 145))
    result["dates"] = dates
    result["costs"] = {name: np.zeros(count) for name in
                       ("plan", "contract", "down_refund", "up_purchase", "emergency", "total")}
    result["audits"] = []
    result["scenario_max_index"] = []
    return result


def _solve_price_policy(net, data, day, start_soc, terminal, method, start_slot=0, reference=None):
    if method == "m2":
        return solve_dispatch_lp(
            net, data.variable_price[day, start_slot:], initial_soc=start_soc,
            terminal_soc=terminal, reference_grid=reference
        ), day
    scenarios, indices = historical_price_scenarios(
        data.variable_price, day, start_slot, PRICE_SCENARIO_COUNT
    )
    return solve_dispatch_lp(
        net, price_scenarios=scenarios, initial_soc=start_soc,
        terminal_soc=terminal, reference_grid=reference
    ), int(indices.max())


def _simulate_q42(data, net_forecast_kw, method, initial_soc):
    dates = data.dates[OUTPUT_START_INDEX:]
    result = _empty_result(dates)
    current_soc = initial_soc
    actual_net = (data.load_kw - data.pv_actual_kw) * DT_HOURS
    for out_index, day in enumerate(range(OUTPUT_START_INDEX, 365)):
        predicted = net_forecast_kw[day] * DT_HOURS
        terminal = SOC_INITIAL if day == 364 else None
        if method == "m1":
            grid = np.maximum(predicted, 0.0)
            charge = np.zeros(144)
            discharge = np.zeros(144)
            soc = np.full(145, current_soc)
            dispatch = _assembled_dispatch(grid, charge, discharge, soc)
            max_history = -1
        else:
            dispatch, max_history = _solve_price_policy(
                predicted, data, day, current_soc, terminal, method
            )
            if not dispatch.success:
                raise RuntimeError(f"Q4-2 {method} day {day} failed: {dispatch.message}")
        audit = audit_dispatch(dispatch, predicted, current_soc, terminal)
        if audit["simultaneous_charge_discharge_count"]:
            raise RuntimeError(f"Q4-2 {method} day {day} has simultaneous charge/discharge")
        emergency = np.maximum(actual_net[day] + dispatch.charge - dispatch.discharge - dispatch.grid, 0.0)
        price = data.variable_price[day]
        plan_cost = float(price @ dispatch.grid)
        emergency_cost = float(EMERGENCY_MULTIPLIER * price @ emergency)
        for key, values in (("plan", dispatch.grid), ("adjusted", dispatch.grid),
                            ("charge", dispatch.charge), ("discharge", dispatch.discharge),
                            ("emergency", emergency)):
            result[key][out_index] = values
        result["soc"][out_index] = dispatch.soc
        result["costs"]["plan"][out_index] = plan_cost
        result["costs"]["contract"][out_index] = plan_cost
        result["costs"]["emergency"][out_index] = emergency_cost
        result["costs"]["total"][out_index] = plan_cost + emergency_cost
        result["audits"].append(audit)
        result["scenario_max_index"].append(max_history)
        current_soc = float(dispatch.soc[-1])
    return result


def _simulate_q43(data, net_forecast_kw, pv_10min, forecast_blocks, actual_blocks, method, initial_soc):
    dates = data.dates[OUTPUT_START_INDEX:]
    result = _empty_result(dates)
    current_soc = initial_soc
    actual_net = (data.load_kw - data.pv_actual_kw) * DT_HOURS
    reserves = np.zeros((dates.size, 4))
    for out_index, day in enumerate(range(OUTPUT_START_INDEX, 365)):
        price = data.variable_price[day]
        pv_midnight = pv_10min[day, 0]
        load_forecast = np.maximum(net_forecast_kw[day] + pv_midnight, 0.0)
        reserves[out_index, 0] = quantile_reserve(forecast_blocks, actual_blocks, day, 0, RESERVE_ALPHA)
        safe = np.maximum(pv_midnight - reserves[out_index, 0], 0.0)
        plan_net = (load_forecast - safe) * DT_HOURS
        terminal = SOC_INITIAL if day == 364 else None
        if method == "m1":
            plan_grid = np.maximum(plan_net, 0.0)
            charge = np.zeros(144)
            discharge = np.zeros(144)
            soc = np.full(145, current_soc)
            max_history = -1
        else:
            plan_dispatch, max_history = _solve_price_policy(
                plan_net, data, day, current_soc, terminal, method
            )
            if not plan_dispatch.success:
                raise RuntimeError(f"Q4-3 {method} day {day} plan failed")
            plan_grid = plan_dispatch.grid.copy()
            charge = plan_dispatch.charge.copy()
            discharge = plan_dispatch.discharge.copy()
            soc = plan_dispatch.soc.copy()
        grid = plan_grid.copy()
        executed_prediction = safe.copy()

        for release in range(1, 4):
            start = RELEASE_START_SLOTS[release]
            reserves[out_index, release] = quantile_reserve(
                forecast_blocks, actual_blocks, day, release, RESERVE_ALPHA
            )
            latest = np.maximum(pv_10min[day, release] - reserves[out_index, release], 0.0)
            remaining_net = (load_forecast[start:] - latest[start:]) * DT_HOURS
            if method == "m1":
                grid[start:] = np.maximum(remaining_net, 0.0)
            else:
                update, history_index = _solve_price_policy(
                    remaining_net, data, day, float(soc[start]), terminal, method,
                    start_slot=start, reference=plan_grid[start:]
                )
                max_history = max(max_history, history_index)
                if not update.success:
                    raise RuntimeError(f"Q4-3 {method} day {day} release {release} failed")
                grid[start:] = update.grid
                charge[start:] = update.charge
                discharge[start:] = update.discharge
                soc[start:] = update.soc
            executed_prediction[start:] = latest[start:]

        execution_net = (load_forecast - executed_prediction) * DT_HOURS
        dispatch = _assembled_dispatch(grid, charge, discharge, soc)
        audit = audit_dispatch(dispatch, execution_net, current_soc, terminal)
        if audit["simultaneous_charge_discharge_count"]:
            raise RuntimeError(f"Q4-3 {method} day {day} has simultaneous charge/discharge")
        emergency = np.maximum(actual_net[day] + charge - discharge - grid, 0.0)
        components = adjustment_components(price, plan_grid, grid)
        contract = adjustment_contract_cost(price, plan_grid, grid)
        emergency_cost = float(EMERGENCY_MULTIPLIER * price @ emergency)
        for key, values in (("plan", plan_grid), ("adjusted", grid), ("charge", charge),
                            ("discharge", discharge), ("emergency", emergency),
                            ("executed_pv_forecast", executed_prediction)):
            result[key][out_index] = values
        result["soc"][out_index] = soc
        result["costs"]["plan"][out_index] = components["plan_cost_yuan"]
        result["costs"]["contract"][out_index] = contract
        result["costs"]["down_refund"][out_index] = components["down_refund_yuan"]
        result["costs"]["up_purchase"][out_index] = components["up_purchase_cost_yuan"]
        result["costs"]["emergency"][out_index] = emergency_cost
        result["costs"]["total"][out_index] = contract + emergency_cost
        result["audits"].append(audit)
        result["scenario_max_index"].append(max_history)
        current_soc = float(soc[-1])
    result["reserves"] = reserves
    return result


def _metrics(result):
    return {
        "annual_plan_cost_yuan": float(result["costs"]["plan"].sum()),
        "annual_contract_cost_yuan": float(result["costs"]["contract"].sum()),
        "annual_emergency_cost_yuan": float(result["costs"]["emergency"].sum()),
        "annual_total_cost_yuan": float(result["costs"]["total"].sum()),
        "annual_emergency_kwh": float(result["emergency"].sum()),
        "worst_day_cost_yuan": float(result["costs"]["total"].max()),
        "terminal_soc_kwh": float(result["soc"][-1, -1]),
        "max_balance_violation_kwh": max(a["balance_violation_kwh"] for a in result["audits"]),
        "max_soc_violation_kwh": max(a["soc_violation_kwh"] for a in result["audits"]),
        "simultaneous_charge_discharge_count": sum(a["simultaneous_charge_discharge_count"] for a in result["audits"]),
        "future_price_leakage_count": int(sum(index >= OUTPUT_START_INDEX + offset
                                                  for offset, index in enumerate(result["scenario_max_index"]) if index >= 0)),
    }


def _write_daily_table(path, family, results):
    rows = []
    for method, result in results.items():
        for index, date in enumerate(result["dates"]):
            rows.append({"family": family, "date": str(date), "method": method,
                         "plan_cost_yuan": result["costs"]["plan"][index],
                         "contract_cost_yuan": result["costs"]["contract"][index],
                         "emergency_cost_yuan": result["costs"]["emergency"][index],
                         "total_cost_yuan": result["costs"]["total"][index],
                         "emergency_kwh": result["emergency"][index].sum(),
                         "soc_start_kwh": result["soc"][index, 0],
                         "soc_end_kwh": result["soc"][index, -1]})
    frame = pd.DataFrame(rows)
    frame.to_csv(path, index=False)
    return frame


def run() -> dict:
    started = time.perf_counter()
    paths = round_directories("Q4")
    data = load_project_data()
    q2_cache = RESULTS / "Q2" / "experiments" / "round1" / "tables" / "net_load_forecasts.npz"
    net_forecasts, cache_hit = cached_net_load_forecasts(data.load_kw - data.pv_actual_kw, q2_cache)
    pv_10min = _precompute_pv(data)
    forecast_blocks, actual_blocks = six_hour_forecast_blocks(data)
    warmup = _warmup_states(data)

    q42 = {method: _simulate_q42(data, net_forecasts["m3"], method, warmup[method]) for method in PRICE_METHODS}
    q43 = {method: _simulate_q43(data, net_forecasts["m3"], pv_10min, forecast_blocks, actual_blocks,
                                 method, warmup[method]) for method in PRICE_METHODS}
    metrics42 = {method: _metrics(result) for method, result in q42.items()}
    metrics43 = {method: _metrics(result) for method, result in q43.items()}

    chosen42 = q42["m3"]
    workbook42 = paths["tables"] / "result4-2.xlsx"
    write_q2_workbook(workbook42, chosen42["dates"], chosen42["plan"], chosen42["costs"]["plan"],
                      chosen42["charge"], chosen42["discharge"], chosen42["soc"], chosen42["emergency"],
                      template_name="result4-2.xlsx")
    official42 = copy_official_result(workbook42, "result4-2.xlsx")

    chosen43 = q43["m3"]
    workbook43 = paths["tables"] / "result4-3.xlsx"
    write_q3_workbook(workbook43, chosen43["dates"], chosen43["plan"], chosen43["costs"]["plan"],
                      chosen43["adjusted"], chosen43["costs"]["contract"], chosen43["charge"],
                      chosen43["discharge"], chosen43["soc"], chosen43["emergency"],
                      template_name="result4-3.xlsx")
    official43 = copy_official_result(workbook43, "result4-3.xlsx")

    daily42 = _write_daily_table(paths["tables"] / "q4_2_daily_metrics.csv", "Q4-2", q42)
    daily43 = _write_daily_table(paths["tables"] / "q4_3_daily_metrics.csv", "Q4-3", q43)
    for family, chosen in (("q4_2", chosen42), ("q4_3", chosen43)):
        detail = []
        for day_index, date in enumerate(chosen["dates"]):
            for slot in range(144):
                detail.append((str(date), slot + 1, chosen["plan"][day_index, slot],
                               chosen["adjusted"][day_index, slot], chosen["charge"][day_index, slot],
                               chosen["discharge"][day_index, slot], chosen["emergency"][day_index, slot],
                               chosen["soc"][day_index, slot], chosen["soc"][day_index, slot + 1]))
        pd.DataFrame(detail, columns=["date", "slot", "plan_grid_kwh", "adjusted_grid_kwh", "charge_kwh",
                                             "discharge_kwh", "emergency_kwh", "soc_start_kwh", "soc_end_kwh"]).to_csv(
            paths["tables"] / f"{family}_m3_full_schedule.csv.gz", index=False, compression="gzip")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for method in PRICE_METHODS:
        subset = daily42[daily42.method == method]
        axes[0].plot(pd.to_datetime(subset.date), subset.total_cost_yuan.rolling(14, min_periods=1).mean(),
                     label=METHOD_LABELS[method], linewidth=1)
        subset43 = daily43[daily43.method == method]
        axes[1].plot(pd.to_datetime(subset43.date), subset43.total_cost_yuan.rolling(14, min_periods=1).mean(),
                     label=METHOD_LABELS[method], linewidth=1)
    axes[0].set_ylabel("Q4-2 cost (yuan)")
    axes[1].set_ylabel("Q4-3 cost (yuan)")
    axes[1].set_xlabel("Date")
    axes[0].legend(ncol=3, fontsize=8)
    fig.tight_layout()
    figure_path = paths["figures"] / "q4_price_policy_comparison.png"
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)

    payload = {"question": "Q4", "selected_method": "Q4-M3", "q2_forecast_cache_hit": cache_hit,
               "warmup_soc_2025_02_01_kwh": warmup, "q4_2": metrics42, "q4_3": metrics43}
    write_json(paths["metrics"] / "metrics.json", payload)
    summary = {"status": "PASS", "question": "Q4", "method": "Q4-M3 historical-price scenario robust LP",
               "runtime_seconds": time.perf_counter() - started, "seed": 2026,
               "information_boundary": "M3 uses only historical days; M2 is explicitly an oracle",
               "outputs": [str(workbook42), str(workbook43), str(official42), str(official43), str(figure_path)],
               "chosen_metrics": {"q4_2": metrics42["m3"], "q4_3": metrics43["m3"]}}
    write_json(paths["root"] / "run_summary.json", summary)
    (paths["logs"] / "run.log").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
