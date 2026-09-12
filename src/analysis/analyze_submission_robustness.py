"""Generate paired temporal-stability evidence for the final paper.

The analysis uses only the already-produced daily result tables.  It does not
rerun or alter any optimization result.  Seven-day moving-block bootstrap
intervals preserve short-range temporal dependence better than an i.i.d.
day bootstrap.
"""

from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "robustness" / "final_submission"
SEED = 20260913
REPS = 5000
BLOCK = 7


CASES = [
    ("Q2", "results/Q2/experiments/round1/tables/q2_daily_metrics.csv", "m1", "m3"),
    ("Q3", "results/Q3/experiments/round2/tables/q3_daily_metrics.csv", "m1", "m3"),
    ("Q4-2_vs_baseline", "results/Q4/experiments/round2/tables/q4_2_daily_metrics.csv", "m1", "m3"),
    ("Q4-2_vs_oracle", "results/Q4/experiments/round2/tables/q4_2_daily_metrics.csv", "m2", "m3"),
    ("Q4-3_vs_baseline", "results/Q4/experiments/round2/tables/q4_3_daily_metrics.csv", "m1", "m3"),
    ("Q4-3_vs_oracle", "results/Q4/experiments/round2/tables/q4_3_daily_metrics.csv", "m2", "m3"),
]


def read_methods(relative: str) -> dict[str, dict[str, dict[str, float]]]:
    by_method: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            by_method[row["method"]][row["date"]] = {
                "total_cost_yuan": float(row["total_cost_yuan"]),
                "emergency_kwh": float(row["emergency_kwh"]),
            }
    return by_method


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def moving_block_ci(values: list[float], rng: random.Random) -> tuple[float, float]:
    n = len(values)
    starts = list(range(n - BLOCK + 1))
    means: list[float] = []
    for _ in range(REPS):
        sample: list[float] = []
        while len(sample) < n:
            start = rng.choice(starts)
            sample.extend(values[start : start + BLOCK])
        means.append(sum(sample[:n]) / n)
    return percentile(means, 0.025), percentile(means, 0.975)


def season(month: int) -> str:
    if month in (3, 4, 5):
        return "春季"
    if month in (6, 7, 8):
        return "夏季"
    if month in (9, 10, 11):
        return "秋季"
    return "冬季"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    paired_rows: list[dict[str, object]] = []
    seasonal_rows: list[dict[str, object]] = []
    summary: dict[str, object] = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "seed": SEED,
        "bootstrap_repetitions": REPS,
        "moving_block_days": BLOCK,
        "cases": {},
    }

    for label, relative, comparator, main_method in CASES:
        methods = read_methods(relative)
        dates = sorted(set(methods[comparator]) & set(methods[main_method]))
        case_summary: dict[str, object] = {"n_days": len(dates), "metrics": {}}

        for metric in ("total_cost_yuan", "emergency_kwh"):
            comparator_values = [methods[comparator][d][metric] for d in dates]
            main_values = [methods[main_method][d][metric] for d in dates]
            improvements = [a - b for a, b in zip(comparator_values, main_values)]
            mean_improvement = sum(improvements) / len(improvements)
            ci_low, ci_high = moving_block_ci(improvements, rng)
            better_days = sum(value > 0 for value in improvements)
            aggregate_change_pct = (
                sum(main_values) / sum(comparator_values) - 1
            ) * 100
            metric_summary = {
                "comparator": comparator,
                "main_method": main_method,
                "aggregate_comparator": sum(comparator_values),
                "aggregate_main": sum(main_values),
                "aggregate_main_vs_comparator_pct": aggregate_change_pct,
                "mean_daily_comparator_minus_main": mean_improvement,
                "moving_block_95ci_low": ci_low,
                "moving_block_95ci_high": ci_high,
                "main_lower_days": better_days,
                "main_lower_days_pct": 100 * better_days / len(dates),
            }
            case_summary["metrics"][metric] = metric_summary
            paired_rows.append({"case": label, "metric": metric, **metric_summary})

        grouped: dict[str, list[str]] = defaultdict(list)
        for date in dates:
            grouped[season(int(date[5:7]))].append(date)
        for season_name in ("春季", "夏季", "秋季", "冬季"):
            group_dates = grouped[season_name]
            row: dict[str, object] = {
                "case": label,
                "season": season_name,
                "n_days": len(group_dates),
            }
            for metric in ("total_cost_yuan", "emergency_kwh"):
                a = sum(methods[comparator][d][metric] for d in group_dates)
                b = sum(methods[main_method][d][metric] for d in group_dates)
                row[f"{metric}_main_vs_comparator_pct"] = (b / a - 1) * 100
                row[f"{metric}_main_lower_days"] = sum(
                    methods[main_method][d][metric] < methods[comparator][d][metric]
                    for d in group_dates
                )
            seasonal_rows.append(row)
        summary["cases"][label] = case_summary

    with (OUT / "paired_validation.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(paired_rows[0]))
        writer.writeheader()
        writer.writerows(paired_rows)
    with (OUT / "seasonal_validation.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(seasonal_rows[0]))
        writer.writeheader()
        writer.writerows(seasonal_rows)
    (OUT / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
