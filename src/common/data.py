from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA_RAW, RELEASE_HOURS, RELEASE_START_SLOTS, SLOT_MINUTES, SLOTS_PER_DAY


@dataclass(frozen=True)
class ProjectData:
    dates: np.ndarray
    time_headers: tuple[str, ...]
    fixed_price: np.ndarray
    q1_load_kw: np.ndarray
    q1_pv_forecast_kw: np.ndarray
    load_kw: np.ndarray
    pv_actual_kw: np.ndarray
    variable_price: np.ndarray
    pv_forecast_hourly_kw: np.ndarray


def _numeric_matrix(path: Path, sheet_name: str) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    frame = pd.read_excel(path, sheet_name=sheet_name)
    dates = pd.to_datetime(frame.iloc[:, 0]).to_numpy(dtype="datetime64[D]")
    matrix = frame.iloc[:, 1:].to_numpy(dtype=float)
    headers = tuple(str(x) for x in frame.columns[1:])
    return dates, matrix, headers


def _check_nonnegative_finite(name: str, values: np.ndarray, shape: tuple[int, ...]) -> None:
    if values.shape != shape:
        raise ValueError(f"{name} shape {values.shape} != {shape}")
    if not np.isfinite(values).all():
        raise ValueError(f"{name} contains non-finite values")
    if (values < 0).any():
        raise ValueError(f"{name} contains negative values")


def load_project_data(data_raw: Path = DATA_RAW) -> ProjectData:
    q1 = pd.read_excel(data_raw / "附件1.xlsx")
    if q1.shape != (SLOTS_PER_DAY, 4):
        raise ValueError(f"附件1 shape {q1.shape} is not (144, 4)")
    fixed_price = q1.iloc[:, 1].to_numpy(dtype=float)
    q1_load = q1.iloc[:, 2].to_numpy(dtype=float)
    q1_pv = q1.iloc[:, 3].to_numpy(dtype=float)

    dates_l, load, headers_l = _numeric_matrix(data_raw / "附件2.xlsx", "小区负载")
    dates_pv, pv, headers_pv = _numeric_matrix(data_raw / "附件2.xlsx", "光伏发电实际功率")
    dates_price, variable_price, headers_price = _numeric_matrix(data_raw / "附件4.xlsx", "Sheet1")
    expected = (365, SLOTS_PER_DAY)
    for name, values in (("load", load), ("pv", pv), ("variable_price", variable_price)):
        _check_nonnegative_finite(name, values, expected)
    if not (np.array_equal(dates_l, dates_pv) and np.array_equal(dates_l, dates_price)):
        raise ValueError("附件2与附件4日期顺序不一致")
    if headers_l != headers_pv or headers_l != headers_price:
        raise ValueError("附件2与附件4的144个时点表头不一致")

    forecast_frame = pd.read_excel(data_raw / "附件3.xlsx")
    forecast_frame.iloc[:, 0] = forecast_frame.iloc[:, 0].ffill()
    forecast_dates = pd.to_datetime(forecast_frame.iloc[:, 0]).to_numpy(dtype="datetime64[D]")
    release = forecast_frame.iloc[:, 1].astype(str).to_numpy()
    forecast = forecast_frame.iloc[:, 2:].to_numpy(dtype=float)
    _check_nonnegative_finite("pv_forecast", forecast, (365 * 4, 24))
    forecast = forecast.reshape(365, 4, 24)
    if not np.array_equal(forecast_dates.reshape(365, 4)[:, 0], dates_l):
        raise ValueError("附件3与附件2日期顺序不一致")
    expected_release = np.array([f"{hour}:00" for hour in RELEASE_HOURS])
    if not np.all(release.reshape(365, 4) == expected_release):
        raise ValueError("附件3每日预测发布时间不是00/06/12/18四个时点")

    for name, values, shape in (
        ("fixed_price", fixed_price, (144,)),
        ("q1_load", q1_load, (144,)),
        ("q1_pv", q1_pv, (144,)),
    ):
        _check_nonnegative_finite(name, values, shape)

    return ProjectData(
        dates=dates_l,
        time_headers=headers_l,
        fixed_price=fixed_price,
        q1_load_kw=q1_load,
        q1_pv_forecast_kw=q1_pv,
        load_kw=load,
        pv_actual_kw=pv,
        variable_price=variable_price,
        pv_forecast_hourly_kw=forecast,
    )


def interpolate_pv_forecast(data: ProjectData, day_index: int, release_index: int) -> np.ndarray:
    """Map a release's hourly nodes to the frozen 10-minute slot-start convention."""
    start_slot = RELEASE_START_SLOTS[release_index]
    release_minute = RELEASE_HOURS[release_index] * 60
    hourly = data.pv_forecast_hourly_kw[day_index, release_index]
    if release_index == 0:
        boundary = float(hourly[0])
    else:
        boundary = float(data.pv_actual_kw[day_index, start_slot - 1])
    nodes_x = np.arange(25, dtype=float) * 60.0
    nodes_y = np.r_[boundary, hourly]
    target = np.asarray(SLOT_MINUTES, dtype=float) - release_minute
    result = np.empty(SLOTS_PER_DAY, dtype=float)
    result[:start_slot] = data.pv_actual_kw[day_index, :start_slot]
    result[start_slot:] = np.interp(target[start_slot:], nodes_x, nodes_y)
    return np.maximum(result, 0.0)


def six_hour_forecast_blocks(data: ProjectData) -> tuple[np.ndarray, np.ndarray]:
    forecast = data.pv_forecast_hourly_kw[:, :, :6].copy()
    hourly_actual = data.pv_actual_kw[:, 5::6]
    if hourly_actual.shape != (365, 24):
        raise ValueError("实际光伏的整点抽样不是365×24")
    actual = hourly_actual.reshape(365, 4, 6)
    return forecast, actual
