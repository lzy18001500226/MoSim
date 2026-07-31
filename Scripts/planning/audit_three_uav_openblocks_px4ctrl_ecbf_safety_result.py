#!/usr/bin/env python3
"""Audit an exported three-UAV PX4CTRL pairwise-ECBF safety result."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = ROOT / "Results/planning/three_uav_openblocks_px4ctrl_ecbf_safety_20260731"
DEFAULT_RAW = DEFAULT_BUNDLE / "raw/mworks_px4ctrl_ecbf_safety_full_304p84s.csv"
DEFAULT_PLANNING = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720/metrics/three_uav_planning_metrics.json"
DEFAULT_JSON = DEFAULT_BUNDLE / "metrics/mworks_px4ctrl_ecbf_safety_full_304p84s.json"
DEFAULT_CSV = DEFAULT_BUNDLE / "metrics/mworks_px4ctrl_ecbf_safety_full_304p84s.csv"

MIN_PAIR_DISTANCE_M = 1.0
MAX_REFERENCE_OFFSET_M = 0.5
MAX_TRACKING_RMSE_M = 0.20
MAX_TRACKING_ERROR_M = 0.50
MAX_FINAL_TRACKING_ERROR_M = 0.15


def read_numeric_csv(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        data = {name: [] for name in reader.fieldnames}
        for row_index, row in enumerate(reader, start=2):
            for name in reader.fieldnames:
                try:
                    data[name].append(float(row[name]))
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid numeric value at row {row_index}, column {name}") from exc
    return data


def rmse(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def vector_distance(data: dict[str, list[float]], prefix_a: str, prefix_b: str, index: int) -> float:
    return math.sqrt(sum(
        (data[f"{prefix_a}_{axis}_m"][index] - data[f"{prefix_b}_{axis}_m"][index]) ** 2
        for axis in "xyz"
    ))


def min_value_time(values: list[float], times: list[float]) -> tuple[float, float]:
    index = min(range(len(values)), key=values.__getitem__)
    return values[index], times[index]


def audit(raw_path: Path, planning_path: Path) -> dict[str, Any]:
    data = read_numeric_csv(raw_path)
    required = {
        "time_s",
        "minimum_pair_distance_m",
        "formation_distance_error_m",
        "clearance_lower_bound_m",
        "minimum_predicted_pair_distance_m",
        "safety_active_pair_count",
        "safety_maximum_reference_offset_m",
        "safety_maximum_ecbf_residual_m2_s2",
        "safety_correction_saturated",
        "nominal_formation_deviation_m",
    }
    for index in range(1, 4):
        required.add(f"uav{index}_tracking_error_m")
        for axis in "xyz":
            required.add(f"uav{index}_{axis}_m")
            required.add(f"uav{index}_nominal_ref_{axis}_m")
            required.add(f"uav{index}_safe_ref_{axis}_m")
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    times = data["time_s"]
    if len(times) < 11:
        raise ValueError(f"Expected more than 10 samples, got {len(times)}")
    if any(right <= left for left, right in zip(times, times[1:])):
        raise ValueError("time_s must be strictly increasing")

    non_finite_count = sum(
        1 for values in data.values() for value in values if not math.isfinite(value)
    )
    planning = json.loads(planning_path.read_text(encoding="utf-8"))
    metrics: dict[str, Any] = {
        "schema": "mosim.mworks.three_uav_open_blocks_px4ctrl_ecbf_safety.metrics.v1",
        "source": "MWORKS_MCP",
        "model_name": "MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety",
        "raw_result": str(raw_path.resolve()),
        "planning_result": str(planning_path.resolve()),
        "sample_count": len(times),
        "time_start_s": times[0],
        "time_end_s": times[-1],
        "nan_or_inf_count": non_finite_count,
        "thresholds": {
            "minimum_pair_distance_m": MIN_PAIR_DISTANCE_M,
            "maximum_reference_offset_m": MAX_REFERENCE_OFFSET_M,
            "maximum_tracking_rmse_m": MAX_TRACKING_RMSE_M,
            "maximum_tracking_error_m": MAX_TRACKING_ERROR_M,
            "maximum_final_tracking_error_m": MAX_FINAL_TRACKING_ERROR_M,
        },
        "reference_schedule": planning["schedule"],
    }

    tracking_pass = True
    tracking_consistency_pass = True
    for index in range(1, 4):
        reported_errors = data[f"uav{index}_tracking_error_m"]
        safe_errors = [
            vector_distance(data, f"uav{index}", f"uav{index}_safe_ref", sample)
            for sample in range(len(times))
        ]
        nominal_errors = [
            vector_distance(data, f"uav{index}", f"uav{index}_nominal_ref", sample)
            for sample in range(len(times))
        ]
        max_consistency_error = max(
            abs(reported - observed) for reported, observed in zip(reported_errors, safe_errors)
        )
        vehicle = {
            "safe_tracking_rmse_m": rmse(safe_errors),
            "safe_tracking_max_m": max(safe_errors),
            "safe_tracking_final_m": safe_errors[-1],
            "nominal_tracking_rmse_m": rmse(nominal_errors),
            "nominal_tracking_max_m": max(nominal_errors),
            "nominal_tracking_final_m": nominal_errors[-1],
            "reported_tracking_error_consistency_max_m": max_consistency_error,
            "final_position_m": [data[f"uav{index}_{axis}_m"][-1] for axis in "xyz"],
            "final_safe_reference_m": [data[f"uav{index}_safe_ref_{axis}_m"][-1] for axis in "xyz"],
            "final_nominal_reference_m": [data[f"uav{index}_nominal_ref_{axis}_m"][-1] for axis in "xyz"],
        }
        vehicle["tracking_gate_passed"] = (
            vehicle["safe_tracking_rmse_m"] <= MAX_TRACKING_RMSE_M
            and vehicle["safe_tracking_max_m"] <= MAX_TRACKING_ERROR_M
            and vehicle["safe_tracking_final_m"] <= MAX_FINAL_TRACKING_ERROR_M
        )
        vehicle["reported_tracking_error_consistent"] = max_consistency_error <= 1e-7
        tracking_pass = tracking_pass and bool(vehicle["tracking_gate_passed"])
        tracking_consistency_pass = tracking_consistency_pass and bool(vehicle["reported_tracking_error_consistent"])
        metrics[f"uav{index}"] = vehicle

    actual_pair_values = data["minimum_pair_distance_m"]
    predicted_pair_values = data["minimum_predicted_pair_distance_m"]
    safe_reference_pair_values: list[float] = []
    nominal_reference_pair_values: list[float] = []
    for sample in range(len(times)):
        safe_reference_pair_values.append(min(
            vector_distance(data, "uav1_safe_ref", "uav2_safe_ref", sample),
            vector_distance(data, "uav1_safe_ref", "uav3_safe_ref", sample),
            vector_distance(data, "uav2_safe_ref", "uav3_safe_ref", sample),
        ))
        nominal_reference_pair_values.append(min(
            vector_distance(data, "uav1_nominal_ref", "uav2_nominal_ref", sample),
            vector_distance(data, "uav1_nominal_ref", "uav3_nominal_ref", sample),
            vector_distance(data, "uav2_nominal_ref", "uav3_nominal_ref", sample),
        ))

    minimum_actual_pair_distance_m, minimum_actual_pair_distance_time_s = min_value_time(actual_pair_values, times)
    minimum_predicted_pair_distance_m, minimum_predicted_pair_distance_time_s = min_value_time(predicted_pair_values, times)
    minimum_safe_reference_pair_distance_m, minimum_safe_reference_pair_distance_time_s = min_value_time(
        safe_reference_pair_values, times
    )
    minimum_nominal_reference_pair_distance_m, minimum_nominal_reference_pair_distance_time_s = min_value_time(
        nominal_reference_pair_values, times
    )
    maximum_reference_offset_m = max(data["safety_maximum_reference_offset_m"])
    maximum_ecbf_residual_m2_s2 = max(data["safety_maximum_ecbf_residual_m2_s2"])
    intervention_sample_count = sum(1 for value in data["safety_active_pair_count"] if value > 0.5)
    correction_saturated_sample_count = sum(1 for value in data["safety_correction_saturated"] if value > 0.5)
    clearance_proxy_m, clearance_proxy_time_s = min_value_time(data["clearance_lower_bound_m"], times)

    metrics.update({
        "minimum_actual_pair_distance_m": minimum_actual_pair_distance_m,
        "minimum_actual_pair_distance_time_s": minimum_actual_pair_distance_time_s,
        "minimum_predicted_pair_distance_m": minimum_predicted_pair_distance_m,
        "minimum_predicted_pair_distance_time_s": minimum_predicted_pair_distance_time_s,
        "minimum_safe_reference_pair_distance_m": minimum_safe_reference_pair_distance_m,
        "minimum_safe_reference_pair_distance_time_s": minimum_safe_reference_pair_distance_time_s,
        "minimum_nominal_reference_pair_distance_m": minimum_nominal_reference_pair_distance_m,
        "minimum_nominal_reference_pair_distance_time_s": minimum_nominal_reference_pair_distance_time_s,
        "maximum_nominal_formation_deviation_m": max(data["nominal_formation_deviation_m"]),
        "maximum_formation_distance_error_m": max(data["formation_distance_error_m"]),
        "formation_distance_error_rmse_m": rmse(data["formation_distance_error_m"]),
        "maximum_reference_offset_m": maximum_reference_offset_m,
        "maximum_ecbf_residual_m2_s2": maximum_ecbf_residual_m2_s2,
        "maximum_active_pair_count": max(data["safety_active_pair_count"]),
        "intervention_sample_count": intervention_sample_count,
        "correction_saturated_sample_count": correction_saturated_sample_count,
        "minimum_clearance_proxy_m": clearance_proxy_m,
        "minimum_clearance_proxy_time_s": clearance_proxy_time_s,
    })

    pair_separation_pass = minimum_actual_pair_distance_m >= MIN_PAIR_DISTANCE_M
    safety_intervened = intervention_sample_count > 0
    reference_offset_bound_pass = maximum_reference_offset_m <= MAX_REFERENCE_OFFSET_M + 1e-9
    pairwise_safety_evidence_pass = (
        non_finite_count == 0
        and tracking_consistency_pass
        and pair_separation_pass
        and safety_intervened
        and reference_offset_bound_pass
    )
    metrics["gates"] = {
        "finite_values": non_finite_count == 0,
        "reported_safe_tracking_consistency": tracking_consistency_pass,
        "pair_separation": pair_separation_pass,
        "safety_intervened": safety_intervened,
        "reference_offset_bound": reference_offset_bound_pass,
        "tracking_diagnostic": tracking_pass,
        "clearance_proxy_nonnegative_diagnostic": clearance_proxy_m >= 0.0,
        "correction_saturated_diagnostic": correction_saturated_sample_count == 0,
    }
    metrics["accepted"] = pairwise_safety_evidence_pass
    metrics["status"] = (
        "accepted_for_pairwise_safety_comparison"
        if pairwise_safety_evidence_pass and tracking_pass and clearance_proxy_m >= 0.0
        else "accepted_for_pairwise_safety_comparison_with_tracking_or_clearance_warning"
        if pairwise_safety_evidence_pass
        else "blocked"
    )
    metrics["claim_boundary"] = (
        "This is MWORKS whole-aircraft evidence for a frozen OpenBlocks reference route plus a pairwise ECBF "
        "reference governor. It evaluates finite output, intervention, reference-boundedness, and inter-UAV "
        "separation. It is not online replanning, global wall/column CBF coverage, plant-coupled collision-contact "
        "acceptance, or Gazebo/PX4/ROS runtime evidence. The clearance field is a nominal-path tracking proxy only."
    )
    return metrics


def write_outputs(metrics: dict[str, Any], json_path: Path, csv_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("status", metrics["status"]),
        ("accepted", metrics["accepted"]),
        ("sample_count", metrics["sample_count"]),
        ("minimum_actual_pair_distance_m", metrics["minimum_actual_pair_distance_m"]),
        ("minimum_predicted_pair_distance_m", metrics["minimum_predicted_pair_distance_m"]),
        ("minimum_safe_reference_pair_distance_m", metrics["minimum_safe_reference_pair_distance_m"]),
        ("minimum_nominal_reference_pair_distance_m", metrics["minimum_nominal_reference_pair_distance_m"]),
        ("maximum_nominal_formation_deviation_m", metrics["maximum_nominal_formation_deviation_m"]),
        ("maximum_reference_offset_m", metrics["maximum_reference_offset_m"]),
        ("intervention_sample_count", metrics["intervention_sample_count"]),
        ("correction_saturated_sample_count", metrics["correction_saturated_sample_count"]),
        ("minimum_clearance_proxy_m", metrics["minimum_clearance_proxy_m"]),
    ]
    for index in range(1, 4):
        rows.extend([
            (f"uav{index}_safe_tracking_rmse_m", metrics[f"uav{index}"]["safe_tracking_rmse_m"]),
            (f"uav{index}_safe_tracking_max_m", metrics[f"uav{index}"]["safe_tracking_max_m"]),
            (f"uav{index}_safe_tracking_final_m", metrics[f"uav{index}"]["safe_tracking_final_m"]),
            (f"uav{index}_nominal_tracking_rmse_m", metrics[f"uav{index}"]["nominal_tracking_rmse_m"]),
        ])
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--planning", type=Path, default=DEFAULT_PLANNING)
    parser.add_argument("--metrics-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--metrics-csv", type=Path, default=DEFAULT_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics = audit(args.raw.resolve(), args.planning.resolve())
    write_outputs(metrics, args.metrics_json.resolve(), args.metrics_csv.resolve())
    print(json.dumps({
        "status": metrics["status"],
        "accepted": metrics["accepted"],
        "minimum_actual_pair_distance_m": metrics["minimum_actual_pair_distance_m"],
        "intervention_sample_count": metrics["intervention_sample_count"],
    }, indent=2))
    return 0 if metrics["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
