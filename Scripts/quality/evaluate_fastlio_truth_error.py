#!/usr/bin/env python3
"""Evaluate Spark FAST-LIO odometry against same-run Gazebo pose truth.

Default project output: FASTLIO_TRUTH_ERROR_EVAL.json.
"""

from __future__ import annotations

import argparse
import json
import math
from bisect import bisect_left
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if isinstance(data, dict):
            rows.append(data)
    return rows


def position(row: dict[str, Any]) -> list[float] | None:
    value = row.get("position_m")
    if not isinstance(value, list) or len(value) != 3:
        return None
    try:
        return [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        return None


def time_s(row: dict[str, Any]) -> float | None:
    try:
        return float(row.get("time"))
    except (TypeError, ValueError):
        return None


def valid_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples = []
    for row in rows:
        t = time_s(row)
        p = position(row)
        if t is None or p is None:
            continue
        item = dict(row)
        item["_time"] = t
        item["_position"] = p
        samples.append(item)
    samples.sort(key=lambda item: float(item["_time"]))
    return samples


def relative_time_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not samples:
        return []
    first_time = float(samples[0]["_time"])
    shifted: list[dict[str, Any]] = []
    for sample in samples:
        item = dict(sample)
        item["_absolute_time"] = float(sample["_time"])
        item["_time"] = float(sample["_time"]) - first_time
        shifted.append(item)
    return shifted


def time_range(samples: list[dict[str, Any]]) -> dict[str, float | None]:
    if not samples:
        return {"start_s": None, "end_s": None, "duration_s": None}
    start = float(samples[0]["_time"])
    end = float(samples[-1]["_time"])
    return {
        "start_s": round(start, 6),
        "end_s": round(end, 6),
        "duration_s": round(end - start, 6),
    }


def distance(left: list[float], right: list[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def metrics(errors: list[float]) -> dict[str, float | None]:
    if not errors:
        return {
            "rmse_3d_m": None,
            "mean_3d_m": None,
            "p95_3d_m": None,
            "max_3d_m": None,
            "final_3d_m": None,
        }
    return {
        "rmse_3d_m": round(math.sqrt(sum(error * error for error in errors) / len(errors)), 6),
        "mean_3d_m": round(sum(errors) / len(errors), 6),
        "p95_3d_m": round(float(percentile(errors, 0.95)), 6),
        "max_3d_m": round(max(errors), 6),
        "final_3d_m": round(errors[-1], 6),
    }


def align(
    estimate_samples: list[dict[str, Any]],
    truth_samples: list[dict[str, Any]],
    max_time_delta_s: float,
) -> list[dict[str, Any]]:
    truth_times = [float(item["_time"]) for item in truth_samples]
    matched: list[dict[str, Any]] = []
    for estimate in estimate_samples:
        t = float(estimate["_time"])
        index = bisect_left(truth_times, t)
        candidates = []
        if index < len(truth_samples):
            candidates.append(truth_samples[index])
        if index > 0:
            candidates.append(truth_samples[index - 1])
        if not candidates:
            continue
        truth = min(candidates, key=lambda item: abs(float(item["_time"]) - t))
        delta = abs(float(truth["_time"]) - t)
        if delta <= max_time_delta_s:
            matched.append(
                {
                    "estimate_time": round(t, 6),
                    "truth_time": round(float(truth["_time"]), 6),
                    "time_delta_s": round(delta, 6),
                    "estimate_position_m": estimate["_position"],
                    "truth_position_m": truth["_position"],
                }
            )
    return matched


def add_error_metrics(matches: list[dict[str, Any]]) -> dict[str, Any]:
    direct_errors = [
        distance(match["estimate_position_m"], match["truth_position_m"])
        for match in matches
    ]
    if not matches:
        return {
            "direct": metrics([]),
            "origin_aligned": metrics([]),
            "first_direct_offset_m": None,
        }
    first = matches[0]
    direct_offset = [
        float(first["estimate_position_m"][idx]) - float(first["truth_position_m"][idx])
        for idx in range(3)
    ]
    aligned_errors = []
    for match in matches:
        shifted_estimate = [
            float(match["estimate_position_m"][idx]) - direct_offset[idx]
            for idx in range(3)
        ]
        aligned_errors.append(distance(shifted_estimate, match["truth_position_m"]))
    return {
        "direct": metrics(direct_errors),
        "origin_aligned": metrics(aligned_errors),
        "first_direct_offset_m": [round(item, 6) for item in direct_offset],
    }


def build_alignment_report(
    estimate_samples: list[dict[str, Any]],
    truth_samples: list[dict[str, Any]],
    max_time_delta_s: float,
    method: str,
) -> dict[str, Any]:
    matches = align(estimate_samples, truth_samples, max_time_delta_s)
    return {
        "method": method,
        "max_time_delta_s": max_time_delta_s,
        "estimate_time_range": time_range(estimate_samples),
        "truth_time_range": time_range(truth_samples),
        "matched_count": len(matches),
        "first_matches": matches[:5],
        "metrics": add_error_metrics(matches),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spark-odometry-jsonl", required=True, type=Path)
    parser.add_argument("--truth-pose-jsonl", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--source-topic", default="/world/mosim_factory_minimal/dynamic_pose/info")
    parser.add_argument("--truth-source-kind", default="gazebo_transport_dynamic_pose_info")
    parser.add_argument("--max-time-delta-s", type=float, default=0.05)
    parser.add_argument("--min-matched-samples", type=int, default=30)
    parser.add_argument(
        "--time-alignment",
        choices=["absolute", "relative_start"],
        default="relative_start",
    )
    parser.add_argument("--rmse-warn-m", type=float, default=0.5)
    parser.add_argument("--rmse-block-m", type=float, default=1.0)
    parser.add_argument("--p95-block-m", type=float, default=1.5)
    args = parser.parse_args()

    spark_path = project_path(args.spark_odometry_jsonl)
    truth_path = project_path(args.truth_pose_jsonl)
    output = project_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)

    estimate_samples = valid_samples(read_jsonl(spark_path))
    truth_samples = valid_samples(read_jsonl(truth_path))
    absolute_alignment = build_alignment_report(
        estimate_samples,
        truth_samples,
        args.max_time_delta_s,
        "absolute_nearest_neighbor_by_time",
    )
    if args.time_alignment == "relative_start":
        gate_estimate_samples = relative_time_samples(estimate_samples)
        gate_truth_samples = relative_time_samples(truth_samples)
        gate_alignment = build_alignment_report(
            gate_estimate_samples,
            gate_truth_samples,
            args.max_time_delta_s,
            "relative_start_nearest_neighbor_by_time",
        )
    else:
        gate_alignment = absolute_alignment
    error_metrics = gate_alignment["metrics"]

    blockers: list[str] = []
    warnings: list[str] = []
    if not estimate_samples:
        blockers.append("missing_spark_odometry_samples")
    if not truth_samples:
        blockers.append("missing_gazebo_truth_pose_samples")
    if args.time_alignment == "relative_start" and int(absolute_alignment["matched_count"]) == 0:
        warnings.append("absolute_timestamp_overlap_missing")
    if int(gate_alignment["matched_count"]) < args.min_matched_samples:
        blockers.append(f"matched_samples_below_min:{gate_alignment['matched_count']}<{args.min_matched_samples}")

    origin_rmse = error_metrics["origin_aligned"]["rmse_3d_m"]
    origin_p95 = error_metrics["origin_aligned"]["p95_3d_m"]
    if origin_rmse is not None and origin_rmse > args.rmse_block_m:
        blockers.append(f"origin_aligned_rmse_above_block:{origin_rmse}>{args.rmse_block_m}")
    elif origin_rmse is not None and origin_rmse > args.rmse_warn_m:
        warnings.append(f"origin_aligned_rmse_above_warn:{origin_rmse}>{args.rmse_warn_m}")
    if origin_p95 is not None and origin_p95 > args.p95_block_m:
        blockers.append(f"origin_aligned_p95_above_block:{origin_p95}>{args.p95_block_m}")

    status = "truth_error_passed" if not blockers else "truth_error_blocked"
    report = {
        "schema": "mosim.fastlio_truth_error_eval.v1",
        "status": status,
        "gate_passed": not blockers,
        "claim": "truth_error_evaluation_only_no_planner_no_setpoint_no_closed_loop",
        "spark_odometry": {
            "path": rel(spark_path),
            "time_field": "time",
            "position_field": "position_m",
            "count": len(estimate_samples),
            "frame_id": estimate_samples[0].get("frame_id") if estimate_samples else None,
            "time_range": time_range(estimate_samples),
        },
        "truth_pose": {
            "path": rel(truth_path),
            "source_topic": args.source_topic,
            "source_kind": args.truth_source_kind,
            "time_field": "time",
            "position_field": "position_m",
            "count": len(truth_samples),
            "frame_id": truth_samples[0].get("frame_id") if truth_samples else None,
            "time_range": time_range(truth_samples),
        },
        "time_base": {
            "gate_alignment": args.time_alignment,
            "absolute_alignment_retained_for_diagnosis": True,
            "note": "Gazebo transport pose and Spark FAST-LIO output may use different header time bases in this bounded smoke.",
        },
        "alignment": {
            "gate": {
                "method": gate_alignment["method"],
                "max_time_delta_s": args.max_time_delta_s,
                "estimate_time_range": gate_alignment["estimate_time_range"],
                "truth_time_range": gate_alignment["truth_time_range"],
                "matched_count": gate_alignment["matched_count"],
                "first_matches": gate_alignment["first_matches"],
            },
            "absolute_diagnostic": {
                "method": absolute_alignment["method"],
                "max_time_delta_s": args.max_time_delta_s,
                "estimate_time_range": absolute_alignment["estimate_time_range"],
                "truth_time_range": absolute_alignment["truth_time_range"],
                "matched_count": absolute_alignment["matched_count"],
                "first_matches": absolute_alignment["first_matches"],
            },
            "matched_count": gate_alignment["matched_count"],
            "first_matches": gate_alignment["first_matches"],
        },
        "metrics": error_metrics,
        "thresholds": {
            "max_time_delta_s": args.max_time_delta_s,
            "min_matched_samples": args.min_matched_samples,
            "time_alignment": args.time_alignment,
            "rmse_3d_m_warn": args.rmse_warn_m,
            "rmse_3d_m_block": args.rmse_block_m,
            "p95_3d_m_block": args.p95_block_m,
        },
        "blockers": blockers,
        "warnings": warnings,
        "claim_boundary": [
            "This gate evaluates estimator odometry against same-run Gazebo pose truth.",
            "The default gate uses relative-start time alignment because Gazebo transport pose and Spark output can carry different header time bases in this smoke runner.",
            "Direct error is reported, but origin-aligned error is the first pass/fail metric for this bounded stationary smoke because Spark may choose its own initial map origin.",
            "A pass here does not prove planner_ready, setpoint publication, command acknowledgement, closed_loop behavior, controller performance, or multi-UAV readiness.",
        ],
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
