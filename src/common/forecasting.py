from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

from .config import FORECAST_TRAINING_DAYS, SEED


def day_features(net_kw: np.ndarray, day_index: int) -> np.ndarray:
    slots = net_kw.shape[1]
    slot = np.arange(slots, dtype=float)
    return np.column_stack(
        (
            net_kw[day_index - 1],
            net_kw[day_index - 7 : day_index].mean(axis=0),
            np.sin(2.0 * np.pi * slot / slots),
            np.cos(2.0 * np.pi * slot / slots),
            np.full(slots, day_index % 7, dtype=float),
        )
    )


def forecast_net_loads(net_kw: np.ndarray, start_day: int = 31) -> dict[str, np.ndarray]:
    """Generate strict day-ahead forecasts; row d never reads net_kw[d:] while fitting."""
    days, slots = net_kw.shape
    forecasts = {name: np.full((days, slots), np.nan) for name in ("m1", "m2", "m3")}
    for day in range(start_day, days):
        forecasts["m1"][day] = net_kw[day - 1]
        forecasts["m2"][day] = net_kw[day - 7 : day].mean(axis=0)
        first_train = max(7, day - FORECAST_TRAINING_DAYS)
        train_days = range(first_train, day)
        x_train = np.vstack([day_features(net_kw, train_day) for train_day in train_days])
        y_train = np.hstack([net_kw[train_day] for train_day in train_days])
        model = HistGradientBoostingRegressor(
            max_iter=30,
            max_depth=4,
            learning_rate=0.1,
            l2_regularization=1e-4,
            random_state=SEED,
        )
        model.fit(x_train, y_train)
        forecasts["m3"][day] = model.predict(day_features(net_kw, day))
    return forecasts


def cached_net_load_forecasts(net_kw: np.ndarray, cache_path: Path, start_day: int = 31):
    fingerprint = hashlib.sha256(np.ascontiguousarray(net_kw).view(np.uint8)).hexdigest()
    metadata_path = cache_path.with_suffix(".json")
    expected = {
        "input_sha256": fingerprint,
        "start_day": start_day,
        "training_days": FORECAST_TRAINING_DAYS,
        "max_iter": 30,
        "max_depth": 4,
        "seed": SEED,
    }
    if cache_path.exists() and metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata == expected:
            loaded = np.load(cache_path)
            return {name: loaded[name] for name in ("m1", "m2", "m3")}, True
    forecasts = forecast_net_loads(net_kw, start_day=start_day)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_path, **forecasts)
    metadata_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return forecasts, False


def quantile_reserve(
    forecast_blocks: np.ndarray,
    actual_blocks: np.ndarray,
    day_index: int,
    release_index: int,
    alpha: float = 0.9,
) -> float:
    if day_index <= 0:
        return 0.0
    errors = forecast_blocks[:day_index, release_index] - actual_blocks[:day_index, release_index]
    return max(float(np.quantile(errors.ravel(), alpha)), 0.0)


def historical_price_scenarios(
    prices: np.ndarray,
    day_index: int,
    start_slot: int,
    count: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return only earlier-day price suffixes, conditioned on today's known prefix when available."""
    if day_index <= 0:
        raise ValueError("No historical price day is available")
    candidates = np.arange(day_index, dtype=int)
    count = min(count, candidates.size)
    if start_slot == 0:
        selected = candidates[-count:]
    else:
        known = prices[day_index, :start_slot]
        distances = np.sqrt(np.mean((prices[candidates, :start_slot] - known) ** 2, axis=1))
        order = np.lexsort((-candidates, distances))
        selected = candidates[order[:count]]
    return prices[selected, start_slot:].copy(), selected
