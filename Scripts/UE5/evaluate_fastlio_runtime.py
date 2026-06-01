#!/usr/bin/env python3
"""Compare recorded FAST-LIO odometry against MoSim replay truth."""

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
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def load_truth(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    if not rows:
        raise ValueError(f"empty truth dataset: {path}")
    for row in rows:
        if row.get("schema") != "mosim.fastlio_replay_frame.v1":
            raise ValueError(f"unsupported truth schema in {path}: {row.get('schema')}")
    return rows


def load_odometry(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    if not rows:
        raise ValueError(f"empty odometry recording: {path}")
    for row in rows:
        if row.get("schema") != "mosim.fastlio_odometry_sample.v1":
            raise ValueError(f"unsupported odometry schema in {path}: {row.get('schema')}")
    return rows


def nearest_truth(truth: list[dict[str, Any]], times: list[float], time_value: float) -> dict[str, Any]:
    index = bisect_left(times, time_value)
    candidates = []
    if index < len(truth):
        candidates.append(truth[index])
    if index > 0:
        candidates.append(truth[index - 1])
    return min(candidates, key=lambda row: abs(float(row["time"]) - time_value))


def angle_error(a: float, b: float) -> float:
    value = a - b
    while value > math.pi:
        value -= 2.0 * math.pi
    while value < -math.pi:
        value += 2.0 * math.pi
    return value


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    truth_path = project_path(args.truth_dataset)
    odom_path = project_path(args.odometry_jsonl)
    truth = load_truth(truth_path)
    odom = load_odometry(odom_path)
    truth_times = [float(row["time"]) for row in truth]
    odom_times_raw = [float(row["time"]) for row in odom]
    time_offset = odom_times_raw[0] - truth_times[0] if args.align_start_time else 0.0
    samples: list[dict[str, Any]] = []
    for index, row in enumerate(odom):
        odom_time = float(row["time"])
        truth_time = odom_time - time_offset
        match = nearest_truth(truth, truth_times, truth_time)
        match_time = float(match["time"])
        time_delta = abs(match_time - truth_time)
        if time_delta > args.max_time_delta:
            continue
        odom_position = [float(value) for value in row["position_m"]]
        truth_position = [float(value) for value in match["pose_world_m"]]
        error_xyz = [odom_position[axis] - truth_position[axis] for axis in range(3)]
        position_error = math.sqrt(sum(value * value for value in error_xyz))
        yaw_error = angle_error(float(row.get("yaw_rad", 0.0)), float(match.get("rpy_rad", [0.0, 0.0, 0.0])[2]))
        samples.append(
            {
                "odom_seq": row.get("seq", index),
                "odom_time": round(odom_time, 6),
                "truth_time": round(match_time, 6),
                "time_delta_s": round(time_delta, 6),
                "position_error_m": round(position_error, 6),
                "yaw_error_rad": round(yaw_error, 6),
            }
        )

    if not samples:
        status = "failed_no_aligned_samples"
        rmse = None
        max_error = None
        yaw_rmse = None
    else:
        rmse = math.sqrt(sum(sample["position_error_m"] ** 2 for sample in samples) / len(samples))
        max_error = max(sample["position_error_m"] for sample in samples)
        yaw_rmse = math.sqrt(sum(sample["yaw_error_rad"] ** 2 for sample in samples) / len(samples))
        status = "pass" if rmse <= args.max_position_rmse and max_error <= args.max_position_error else "failed_error_threshold"

    return {
        "schema": "mosim.fastlio_runtime_evaluation.v1",
        "scene_id": args.scene_id,
        "status": status,
        "truth_dataset": rel(truth_path),
        "odometry_jsonl": rel(odom_path),
        "align_start_time": args.align_start_time,
        "time_offset_s": round(time_offset, 6),
        "thresholds": {
            "max_time_delta_s": args.max_time_delta,
            "max_position_rmse_m": args.max_position_rmse,
            "max_position_error_m": args.max_position_error,
        },
        "metrics": {
            "truth_frames": len(truth),
            "odometry_samples": len(odom),
            "aligned_samples": len(samples),
            "position_rmse_m": round(rmse, 6) if rmse is not None else None,
            "max_position_error_m": round(max_error, 6) if max_error is not None else None,
            "yaw_rmse_rad": round(yaw_rmse, 6) if yaw_rmse is not None else None,
        },
        "sample_errors": samples[: args.max_samples_reported],
        "claim_boundary": [
            "This evaluates recorded FAST-LIO ROS runtime odometry against replay truth.",
            "A pass requires separately recorded runtime topics; synthetic replay files alone are insufficient.",
            "The global occupancy truth remains a validation oracle and is not a planner input.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# FAST-LIO Runtime Evaluation",
        "",
        f"- scene_id: `{report['scene_id']}`",
        f"- status: `{report['status']}`",
        f"- truth_dataset: `{report['truth_dataset']}`",
        f"- odometry_jsonl: `{report['odometry_jsonl']}`",
        f"- aligned_samples: `{report['metrics']['aligned_samples']}`",
        f"- position_rmse_m: `{report['metrics']['position_rmse_m']}`",
        f"- max_position_error_m: `{report['metrics']['max_position_error_m']}`",
        f"- yaw_rmse_rad: `{report['metrics']['yaw_rmse_rad']}`",
        "",
        "Claim boundary: this is only valid for a real ROS runtime recording.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-id", default="factoryenvironmentcollect")
    parser.add_argument("--truth-dataset", type=Path, required=True)
    parser.add_argument("--odometry-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--align-start-time", action="store_true", default=True)
    parser.add_argument("--no-align-start-time", dest="align_start_time", action="store_false")
    parser.add_argument("--max-time-delta", type=float, default=0.2)
    parser.add_argument("--max-position-rmse", type=float, default=1.0)
    parser.add_argument("--max-position-error", type=float, default=3.0)
    parser.add_argument("--max-samples-reported", type=int, default=20)
    parser.add_argument("--fail-on-threshold", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_time_delta <= 0:
        raise ValueError("--max-time-delta must be positive")
    report = evaluate(args)
    if args.output_json:
        output_json = project_path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        output_md = project_path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(output_md, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_threshold and report["status"] != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
