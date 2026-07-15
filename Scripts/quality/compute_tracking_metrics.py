"""Compute MoSim tracking metrics from a standard tracking.csv file.

This script is static/offline. It reads a recorded tracking log and writes a
metrics.json packet. It does not start ROS, Gazebo, PX4, MAVROS, RViz, or
MWORKS.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRICS_SCHEMA = ROOT / "Config" / "profiles" / "metrics_schema.json"
REQUIRED_TRACKING_COLUMNS = [
    "time_s",
    "ref_x_m",
    "ref_y_m",
    "ref_z_m",
    "truth_x_m",
    "truth_y_m",
    "truth_z_m",
]
REQUIRED_LOCALIZATION_COLUMNS = [
    "stamp",
    "seq",
    "estimate_x",
    "estimate_y",
    "estimate_z",
    "truth_x",
    "truth_y",
    "truth_z",
    "estimate_vx",
    "estimate_vy",
    "estimate_vz",
    "truth_vx",
    "truth_vy",
    "truth_vz",
    "estimate_yaw_rad",
    "truth_yaw_rad",
    "delay_s",
]
LOCALIZATION_METRICS = {
    "ate",
    "rpe",
    "pose_error",
    "velocity_error",
    "delay",
    "drop_rate",
    "map_completeness",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def read_tracking(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = [name for name in REQUIRED_TRACKING_COLUMNS if name not in columns]
        if missing:
            raise ValueError(f"{path}: missing tracking columns: {', '.join(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: tracking log has no rows")
    return rows


def read_csv_with_columns(path: Path, required_columns: list[str], label: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = [name for name in required_columns if name not in columns]
        if missing:
            raise ValueError(f"{path}: missing {label} columns: {', '.join(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: {label} log has no rows")
    return rows


def as_float(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"tracking row has invalid numeric value for {key}: {row.get(key)!r}") from exc


def as_int(row: dict[str, str], key: str) -> int:
    try:
        return int(float(row[key]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"localization row has invalid integer value for {key}: {row.get(key)!r}") from exc


def errors_for(rows: list[dict[str, str]]) -> list[dict[str, float]]:
    errors = []
    for row in rows:
        ex = as_float(row, "truth_x_m") - as_float(row, "ref_x_m")
        ey = as_float(row, "truth_y_m") - as_float(row, "ref_y_m")
        ez = as_float(row, "truth_z_m") - as_float(row, "ref_z_m")
        errors.append(
            {
                "time_s": as_float(row, "time_s"),
                "x": ex,
                "y": ey,
                "z": ez,
                "xy": math.hypot(ex, ey),
                "norm": math.sqrt(ex * ex + ey * ey + ez * ez),
                "saturated": float(row.get("saturated", "0") or 0),
                "phase": row.get("phase", ""),
            }
        )
    return errors


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def settling_time(errors: list[dict[str, float]], tolerance_m: float) -> float | None:
    for index, item in enumerate(errors):
        if all(later["norm"] <= tolerance_m for later in errors[index:]):
            return item["time_s"]
    return None


def steady_rows(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    selected = [row for row in rows if "hover" in str(row.get("phase", "")).lower() or "hold" in str(row.get("phase", "")).lower()]
    if selected:
        return selected
    start = max(0, int(len(rows) * 0.8))
    return rows[start:]


def metric(value: float | None, unit: str, source: str) -> dict[str, Any]:
    return {"value": value, "unit": unit, "source": source}


def wrap_angle_rad(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


def vector_error(row: dict[str, str], estimate_prefix: str, truth_prefix: str) -> tuple[float, float, float]:
    return (
        as_float(row, f"{estimate_prefix}_x") - as_float(row, f"{truth_prefix}_x"),
        as_float(row, f"{estimate_prefix}_y") - as_float(row, f"{truth_prefix}_y"),
        as_float(row, f"{estimate_prefix}_z") - as_float(row, f"{truth_prefix}_z"),
    )


def velocity_error(row: dict[str, str]) -> tuple[float, float, float]:
    return (
        as_float(row, "estimate_vx") - as_float(row, "truth_vx"),
        as_float(row, "estimate_vy") - as_float(row, "truth_vy"),
        as_float(row, "estimate_vz") - as_float(row, "truth_vz"),
    )


def norm3(values: tuple[float, float, float]) -> float:
    x, y, z = values
    return math.sqrt(x * x + y * y + z * z)


def map_completeness_from_summary(path: Path | None) -> float:
    if path is None:
        raise ValueError("FAST-LIO localization metrics require --map-summary-json")
    packet = load_json(path)
    for key in ("map_completeness", "coverage_ratio", "observed_ratio"):
        value = packet.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    coverage = packet.get("coverage")
    if isinstance(coverage, dict):
        for key in ("map_completeness", "ratio", "observed_ratio"):
            value = coverage.get(key)
            if isinstance(value, (int, float)):
                return float(value)
    raise ValueError(f"{path}: map summary must contain map_completeness, coverage_ratio, observed_ratio, or coverage.ratio")


def drop_rate_from_seq(rows: list[dict[str, str]]) -> float:
    seqs = [as_int(row, "seq") for row in rows]
    expected = max(seqs) - min(seqs) + 1
    if expected <= 0:
        raise ValueError("localization seq range is invalid")
    received = len(set(seqs))
    missing = max(0, expected - received)
    return missing / expected


def compute_localization(rows: list[dict[str, str]], map_summary_path: Path | None) -> dict[str, dict[str, Any]]:
    position_errors = []
    pose_errors = []
    velocity_errors = []
    delays = []
    sorted_rows = sorted(rows, key=lambda row: as_float(row, "stamp"))
    for row in sorted_rows:
        position_error = norm3(vector_error(row, "estimate", "truth"))
        linear_velocity_error = norm3(velocity_error(row))
        yaw_error = abs(wrap_angle_rad(as_float(row, "estimate_yaw_rad") - as_float(row, "truth_yaw_rad")))
        position_errors.append(position_error)
        pose_errors.append(math.sqrt(position_error * position_error + yaw_error * yaw_error))
        velocity_errors.append(linear_velocity_error)
        delays.append(as_float(row, "delay_s"))

    rpe_values = []
    for previous, current in zip(sorted_rows, sorted_rows[1:]):
        estimate_delta = (
            as_float(current, "estimate_x") - as_float(previous, "estimate_x"),
            as_float(current, "estimate_y") - as_float(previous, "estimate_y"),
            as_float(current, "estimate_z") - as_float(previous, "estimate_z"),
        )
        truth_delta = (
            as_float(current, "truth_x") - as_float(previous, "truth_x"),
            as_float(current, "truth_y") - as_float(previous, "truth_y"),
            as_float(current, "truth_z") - as_float(previous, "truth_z"),
        )
        delta_error = norm3(
            (
                estimate_delta[0] - truth_delta[0],
                estimate_delta[1] - truth_delta[1],
                estimate_delta[2] - truth_delta[2],
            )
        )
        estimate_yaw_delta = wrap_angle_rad(
            as_float(current, "estimate_yaw_rad") - as_float(previous, "estimate_yaw_rad")
        )
        truth_yaw_delta = wrap_angle_rad(as_float(current, "truth_yaw_rad") - as_float(previous, "truth_yaw_rad"))
        yaw_delta_error = abs(wrap_angle_rad(estimate_yaw_delta - truth_yaw_delta))
        rpe_values.append(math.sqrt(delta_error * delta_error + yaw_delta_error * yaw_delta_error))

    return {
        "ate": metric(rms(position_errors), "m", "localization.csv estimate vs truth"),
        "rpe": metric(rms(rpe_values) if rpe_values else 0.0, "m/rad", "localization.csv relative pose increments"),
        "pose_error": metric(rms(pose_errors), "m/rad", "localization.csv position+yaw estimate vs truth"),
        "velocity_error": metric(rms(velocity_errors), "m/s", "localization.csv velocity estimate vs truth"),
        "delay": metric(max(delays), "s", "localization.csv delay_s max"),
        "drop_rate": metric(drop_rate_from_seq(sorted_rows), "ratio", "localization.csv seq gaps"),
        "map_completeness": metric(
            map_completeness_from_summary(map_summary_path),
            "ratio",
            "map_summary.json",
        ),
    }


def compute(rows: list[dict[str, str]], tolerance_m: float) -> dict[str, dict[str, Any]]:
    errors = errors_for(rows)
    steady = steady_rows(errors)
    ref_z_values = [as_float(row, "ref_z_m") for row in rows]
    truth_z_values = [as_float(row, "truth_z_m") for row in rows]
    max_ref_z = max(ref_z_values)
    max_truth_z = max(truth_z_values)
    saturation_samples = [row["saturated"] for row in errors]
    saturated_count = sum(1 for value in saturation_samples if value > 0.5)

    return {
        "rmse": metric(rms([row["norm"] for row in errors]), "m", "tracking.csv"),
        "max_error": metric(max(row["norm"] for row in errors), "m", "tracking.csv"),
        "steady_state_error": metric(rms([row["norm"] for row in steady]), "m", "tracking.csv steady window"),
        "overshoot": metric(max(0.0, max_truth_z - max_ref_z), "m", "tracking.csv z axis"),
        "settling_time": metric(settling_time(errors, tolerance_m), "s", "tracking.csv"),
        "saturation_ratio": metric(saturated_count / len(errors), "ratio", "tracking.csv saturated column"),
        "xy_error": metric(rms([row["xy"] for row in errors]), "m", "tracking.csv"),
        "z_error": metric(rms([row["z"] for row in errors]), "m", "tracking.csv"),
    }


def filter_metrics(metrics: dict[str, dict[str, Any]], required: list[str] | None) -> dict[str, dict[str, Any]]:
    if not required:
        return metrics
    return {name: metrics[name] for name in required if name in metrics}


def build_packet(
    tracking_path: Path,
    metrics: dict[str, dict[str, Any]],
    metrics_schema_path: Path,
    manifest: dict[str, Any] | None,
    localization_path: Path | None = None,
    map_summary_path: Path | None = None,
) -> dict[str, Any]:
    run_manifest = manifest.get("run_manifest", {}) if manifest else {}
    return {
        "schema_version": 1,
        "generator": "Scripts/quality/compute_tracking_metrics.py",
        "run_id": run_manifest.get("run_id"),
        "experiment_profile_id": run_manifest.get("experiment_profile_id"),
        "launch_plan_hash": run_manifest.get("launch_plan_hash"),
        "metrics_schema": str(metrics_schema_path),
        "tracking_log": str(tracking_path) if tracking_path else None,
        "localization_log": None if localization_path is None else str(localization_path),
        "map_summary": None if map_summary_path is None else str(map_summary_path),
        "metrics": metrics,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tracking_csv", nargs="?", help="Path to tracking.csv")
    parser.add_argument("--manifest", help="Optional RUN_MANIFEST.json path")
    parser.add_argument("--metrics-schema", default=str(DEFAULT_METRICS_SCHEMA), help="Metric schema JSON path")
    parser.add_argument("--localization-csv", help="Optional FAST-LIO estimate-vs-truth localization.csv path")
    parser.add_argument("--map-summary-json", help="Optional FAST-LIO map summary JSON path")
    parser.add_argument("--out", help="Optional metrics.json output path")
    parser.add_argument("--settling-tolerance-m", type=float, default=0.05, help="Settling tolerance in meters")
    args = parser.parse_args(argv)

    try:
        metrics_schema_path = Path(args.metrics_schema)
        load_json(metrics_schema_path)
        manifest = load_json(Path(args.manifest)) if args.manifest else None
        required = None
        if manifest:
            required = manifest.get("run_manifest", {}).get("evaluation", {}).get("required_metrics")
        if args.localization_csv:
            localization_path = Path(args.localization_csv)
            localization_rows = read_csv_with_columns(localization_path, REQUIRED_LOCALIZATION_COLUMNS, "localization")
            map_summary_path = Path(args.map_summary_json) if args.map_summary_json else None
            metrics = filter_metrics(compute_localization(localization_rows, map_summary_path), required)
            tracking_path = Path(args.tracking_csv) if args.tracking_csv else None
            packet = build_packet(tracking_path, metrics, metrics_schema_path, manifest, localization_path, map_summary_path)
        else:
            if not args.tracking_csv:
                raise ValueError("tracking_csv is required unless --localization-csv is provided")
            tracking_path = Path(args.tracking_csv)
            rows = read_tracking(tracking_path)
            metrics = filter_metrics(compute(rows, args.settling_tolerance_m), required)
            packet = build_packet(tracking_path, metrics, metrics_schema_path, manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = json.dumps(packet, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
