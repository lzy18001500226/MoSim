#!/usr/bin/env python3
"""Judge PX4 GPS/EKF state evidence from the ULog of a passive boot gate."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def degrees(value: object) -> float | None:
    if not finite(value):
        return None
    number = float(value)
    return number / 1.0e7 if abs(number) > 360.0 else number


def haversine_m(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
    radius_m = 6371000.0
    phi_a = math.radians(latitude_a)
    phi_b = math.radians(latitude_b)
    d_phi = math.radians(latitude_b - latitude_a)
    d_lambda = math.radians(longitude_b - longitude_a)
    value = math.sin(d_phi / 2.0) ** 2 + math.cos(phi_a) * math.cos(phi_b) * math.sin(d_lambda / 2.0) ** 2
    return 2.0 * radius_m * math.asin(min(1.0, math.sqrt(value)))


def first_dataset(datasets: dict[tuple[str, int], Any], name: str) -> dict[str, Any] | None:
    direct = datasets.get((name, 0))
    if direct is not None:
        return direct
    for (candidate_name, _multi_id), data in datasets.items():
        if candidate_name == name:
            return data
    return None


def data_length(data: dict[str, Any]) -> int:
    for values in data.values():
        try:
            return len(values)
        except TypeError:
            continue
    return 0


def field_values(data: dict[str, Any], name: str) -> list[Any] | None:
    values = data.get(name)
    if values is None:
        return None
    return list(values)


def last_value(data: dict[str, Any], name: str) -> Any | None:
    values = field_values(data, name)
    return values[-1] if values else None


def json_default(value: Any) -> Any:
    """Convert NumPy scalar values returned by pyulog into JSON scalars."""
    item = getattr(value, "item", None)
    if callable(item):
        scalar = item()
        if scalar is not value:
            return scalar
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def finite_geo_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    latitudes = field_values(data, "lat")
    longitudes = field_values(data, "lon")
    altitudes = field_values(data, "alt")
    timestamps = field_values(data, "timestamp")
    if latitudes is None or longitudes is None or altitudes is None:
        return []
    rows = []
    for index, (latitude_raw, longitude_raw, altitude_raw) in enumerate(zip(latitudes, longitudes, altitudes)):
        latitude = degrees(latitude_raw)
        longitude = degrees(longitude_raw)
        if latitude is None or longitude is None or not finite(altitude_raw):
            continue
        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            continue
        if abs(latitude) <= 1.0e-6 and abs(longitude) <= 1.0e-6:
            continue
        rows.append(
            {
                "timestamp_us": int(timestamps[index]) if timestamps and index < len(timestamps) else None,
                "latitude_deg": latitude,
                "longitude_deg": longitude,
                "altitude_m": float(altitude_raw),
            }
        )
    return rows


def summarize_datasets(datasets: dict[tuple[str, int], dict[str, Any]]) -> dict[str, Any]:
    """Return a version-tolerant GPS state-chain verdict for synthetic or ULog data."""
    blockers: list[str] = []
    result: dict[str, Any] = {
        "schema": "mosim.sunray_ros1.px4_gps_state_chain_ulog.v1",
        "status": "blocked",
        "blockers": blockers,
    }

    global_position = first_dataset(datasets, "vehicle_global_position")
    home_position = first_dataset(datasets, "home_position")
    vehicle_status = first_dataset(datasets, "vehicle_status")
    failsafe_flags = first_dataset(datasets, "failsafe_flags")

    if global_position is None:
        blockers.append("missing_vehicle_global_position")
        global_rows: list[dict[str, Any]] = []
    else:
        global_rows = finite_geo_rows(global_position)
        if not global_rows:
            blockers.append("vehicle_global_position_has_no_valid_geodetic_sample")
        result["vehicle_global_position"] = {
            "samples": data_length(global_position),
            "valid_geodetic_samples": len(global_rows),
            "first": global_rows[0] if global_rows else None,
            "last": global_rows[-1] if global_rows else None,
            "lat_lon_valid_last": last_value(global_position, "lat_lon_valid"),
            "alt_valid_last": last_value(global_position, "alt_valid"),
        }
        for field in ("lat_lon_valid", "alt_valid"):
            values = field_values(global_position, field)
            if values is not None and not any(bool(value) for value in values):
                blockers.append(f"vehicle_global_position_{field}_never_true")

    if home_position is None:
        blockers.append("missing_home_position")
        home_rows: list[dict[str, Any]] = []
    else:
        home_rows = finite_geo_rows(home_position)
        if not home_rows:
            blockers.append("home_position_has_no_valid_geodetic_sample")
        result["home_position"] = {
            "samples": data_length(home_position),
            "valid_geodetic_samples": len(home_rows),
            "first": home_rows[0] if home_rows else None,
            "last": home_rows[-1] if home_rows else None,
            "valid_hpos_last": last_value(home_position, "valid_hpos"),
            "valid_alt_last": last_value(home_position, "valid_alt"),
        }
        for field in ("valid_hpos", "valid_alt"):
            values = field_values(home_position, field)
            if values is not None and not any(bool(value) for value in values):
                blockers.append(f"home_position_{field}_never_true")

    if global_rows and home_rows:
        global_last = global_rows[-1]
        home_last = home_rows[-1]
        horizontal_distance_m = haversine_m(
            global_last["latitude_deg"],
            global_last["longitude_deg"],
            home_last["latitude_deg"],
            home_last["longitude_deg"],
        )
        altitude_delta_m = abs(global_last["altitude_m"] - home_last["altitude_m"])
        result["global_home_last_delta"] = {
            "horizontal_m": horizontal_distance_m,
            "altitude_m": altitude_delta_m,
        }
        if horizontal_distance_m > 100.0 or altitude_delta_m > 100.0:
            blockers.append("global_home_last_delta_exceeds_sanity_limit")

    if vehicle_status is None:
        blockers.append("missing_vehicle_status")
    else:
        preflight_values = field_values(vehicle_status, "pre_flight_checks_pass")
        result["vehicle_status"] = {
            "samples": data_length(vehicle_status),
            "pre_flight_checks_pass_last": preflight_values[-1] if preflight_values else None,
        }
        if preflight_values is None:
            blockers.append("missing_vehicle_status_pre_flight_checks_pass")
        elif not any(bool(value) for value in preflight_values):
            blockers.append("pre_flight_checks_never_passed")

    if failsafe_flags is None:
        blockers.append("missing_failsafe_flags")
    else:
        failsafe_summary: dict[str, Any] = {"samples": data_length(failsafe_flags)}
        for field in ("global_position_invalid", "home_position_invalid"):
            values = field_values(failsafe_flags, field)
            failsafe_summary[field + "_last"] = values[-1] if values else None
            if values is None:
                blockers.append("missing_failsafe_" + field)
            elif not any(not bool(value) for value in values):
                blockers.append("failsafe_" + field + "_never_false")
        result["failsafe_flags"] = failsafe_summary

    result["status"] = "passed" if not blockers else "blocked"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ulog", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parents[2]))
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ulog_path = Path(args.ulog)
    if not ulog_path.is_file() or ulog_path.stat().st_size == 0:
        result = {
            "schema": "mosim.sunray_ros1.px4_gps_state_chain_ulog.v1",
            "status": "blocked",
            "blockers": ["missing_px4_ulog"],
            "ulog": str(ulog_path),
        }
        output.write_text(
            json.dumps(result, ensure_ascii=True, indent=2, default=json_default) + "\n",
            encoding="utf-8",
        )
        return 18

    project_root = Path(args.project_root)
    sys.path.insert(0, str(project_root / "References" / "Log" / "pyulog"))
    try:
        from pyulog import ULog

        ulog = ULog(str(ulog_path))
    except Exception as exc:
        result = {
            "schema": "mosim.sunray_ros1.px4_gps_state_chain_ulog.v1",
            "status": "blocked",
            "blockers": ["px4_ulog_parse_failed"],
            "ulog": str(ulog_path),
            "error": repr(exc),
        }
        output.write_text(
            json.dumps(result, ensure_ascii=True, indent=2, default=json_default) + "\n",
            encoding="utf-8",
        )
        return 18

    datasets = {(dataset.name, dataset.multi_id): dataset.data for dataset in ulog.data_list}
    result = summarize_datasets(datasets)
    result["ulog"] = str(ulog_path)
    output.write_text(
        json.dumps(result, ensure_ascii=True, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    return 0 if result["status"] == "passed" else 18


if __name__ == "__main__":
    raise SystemExit(main())
