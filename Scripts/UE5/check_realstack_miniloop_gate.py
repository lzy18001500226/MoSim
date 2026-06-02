#!/usr/bin/env python3
"""Gate the MoSim UE/ROS2/MWORKS UAV stack before opening RViz/UE review.

This is intentionally a headless gate. It blocks the old keyboard/grid or
display-only route and records exactly which runtime condition is still missing
before a human is asked to review RViz2/UE windows.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE_DIR = ROOT / "Results" / "unreal_scene_mapping" / "factoryenvironmentcollect"
DEFAULT_MWORKS_RAW = (
    DEFAULT_SCENE_DIR
    / "mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv"
)
DEFAULT_LIVOX_FRAMES = DEFAULT_SCENE_DIR / "livox_like_lidar_frames_mworks_body.jsonl"
DEFAULT_FASTLIO_CONTRACT = DEFAULT_SCENE_DIR / "fastlio_input_contract.json"
DEFAULT_RUNTIME_RECORDING = (
    DEFAULT_SCENE_DIR
    / "fastlio_runtime_factory_mworks_body_formal_20260602_122033/FASTLIO_RUNTIME_RECORDING.json"
)
DEFAULT_RUNTIME_EVALUATION = (
    DEFAULT_SCENE_DIR
    / "fastlio_runtime_factory_mworks_body_formal_20260602_122033/FASTLIO_RUNTIME_EVALUATION.json"
)
DEFAULT_RVIZ_POINTCLOUD = ROOT / "Config" / "rviz2" / "mosim_uav_fastlio_pointcloud.rviz"
DEFAULT_RVIZ_MAP = ROOT / "Config" / "rviz2" / "mosim_uav_fastlio_pointcloud.rviz"


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
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return payload


def read_csv_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            {key: float(value) for key, value in row.items() if value not in ("", None)}
            for row in csv.DictReader(handle)
        ]
    if len(rows) < 2:
        raise ValueError(f"need at least two MWORKS rows: {path}")
    required = {"time", "x", "y", "z", "roll", "pitch", "yaw"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"MWORKS rows missing columns {sorted(missing)}: {path}")
    return rows


def read_jsonl_sample(path: Path, sample_frames: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"JSONL row must be object at {path}:{line_number}")
            rows.append(payload)
            if len(rows) >= sample_frames:
                break
    if not rows:
        raise ValueError(f"empty JSONL sample: {path}")
    return rows


def add_finding(findings: list[dict[str, str]], severity: str, surface: str, detail: str, action: str) -> None:
    findings.append({"severity": severity, "surface": surface, "detail": detail, "action": action})


def summarize_mworks(rows: list[dict[str, float]], sample_frames: int) -> dict[str, Any]:
    selected = rows[: min(sample_frames, len(rows))]
    times = [row["time"] for row in selected]
    deltas = [right - left for left, right in zip(times, times[1:])]
    positive = [delta for delta in deltas if delta > 0.0]
    steps = [
        math.sqrt(
            (right["x"] - left["x"]) ** 2
            + (right["y"] - left["y"]) ** 2
            + (right["z"] - left["z"]) ** 2
        )
        for left, right in zip(selected, selected[1:])
    ]
    return {
        "sample_count": len(selected),
        "monotonic_time": len(positive) == len(deltas),
        "nominal_hz": round(1.0 / (sum(positive) / len(positive)), 6) if positive else 0.0,
        "min_dt_s": round(min(deltas), 9) if deltas else 0.0,
        "max_dt_s": round(max(deltas), 9) if deltas else 0.0,
        "max_step_m": round(max(steps), 6) if steps else 0.0,
        "mean_step_m": round(sum(steps) / len(steps), 6) if steps else 0.0,
    }


def summarize_lidar(frames: list[dict[str, Any]]) -> dict[str, Any]:
    counts = [len(frame.get("points_m", [])) for frame in frames]
    times = [float(frame.get("time", frame.get("time_s", 0.0))) for frame in frames]
    attrs = [frame.get("point_attributes", []) for frame in frames]
    attr_keys: set[str] = set()
    lines: set[int] = set()
    attr_count_matches = []
    for frame, attr_list in zip(frames, attrs):
        attr_count_matches.append(isinstance(attr_list, list) and len(attr_list) == len(frame.get("points_m", [])))
        if not isinstance(attr_list, list):
            continue
        for attr in attr_list[:2000]:
            if not isinstance(attr, dict):
                continue
            attr_keys.update(str(key) for key in attr.keys())
            if "line" in attr:
                lines.add(int(attr["line"]))
    deltas = [right - left for left, right in zip(times, times[1:])]
    return {
        "sample_count": len(frames),
        "schema": frames[0].get("schema"),
        "points_per_frame_min": min(counts) if counts else 0,
        "points_per_frame_avg": round(sum(counts) / len(counts), 3) if counts else 0.0,
        "points_per_frame_max": max(counts) if counts else 0,
        "observed_lines": sorted(lines),
        "attribute_keys": sorted(attr_keys),
        "attribute_count_matches_points": all(attr_count_matches) if attr_count_matches else False,
        "nonmonotonic_time_pairs": sum(1 for delta in deltas if delta < 0.0),
    }


def rviz_text_summary(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return {
        "path": rel(path),
        "exists": path.exists(),
        "uses_orbit_view": "Class: rviz_default_plugins/Orbit" in text,
        "uses_mosim_lidar_points": "Value: /mosim/lidar_points" in text,
        "uses_lowercase_odometry": "Value: /odometry" in text,
        "uses_fastlio_odometry": "Value: /Odometry" in text or "Value: /odometry" in text,
        "uses_registered_cloud": "Value: /cloud_registered" in text,
        "uses_3d_local_voxels": "Value: /mosim/local_occupancy_voxels" in text,
        "has_enabled_2d_occupancy_grid": (
            "Value: /mosim/local_occupancy_grid" in text
            and "Name: Local 2D occupancy grid reference" in text
            and "Enabled: true" in text
        ),
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    mworks_raw = project_path(args.mworks_raw_csv)
    livox_frames_path = project_path(args.livox_frames)
    fastlio_contract_path = project_path(args.fastlio_contract)
    runtime_recording_path = project_path(args.runtime_recording)
    runtime_evaluation_path = project_path(args.runtime_evaluation)
    rviz_pointcloud_path = project_path(args.rviz_pointcloud)
    rviz_map_path = project_path(args.rviz_map)

    findings: list[dict[str, str]] = []
    mworks_summary = summarize_mworks(read_csv_rows(mworks_raw), args.sample_frames)
    lidar_summary = summarize_lidar(read_jsonl_sample(livox_frames_path, args.sample_frames))
    fastlio_contract = read_json(fastlio_contract_path)
    runtime_recording = read_json(runtime_recording_path)
    runtime_evaluation = read_json(runtime_evaluation_path)
    rviz_pointcloud = rviz_text_summary(rviz_pointcloud_path)
    rviz_map = rviz_text_summary(rviz_map_path)

    if not mworks_summary["monotonic_time"]:
        add_finding(findings, "error", "MWORKS state", "MWORKS source timestamps are not monotonic.", "Fix state export before ROS2 replay.")
    if abs(float(mworks_summary["nominal_hz"]) - args.truth_rate_hz) > args.rate_tolerance_hz:
        add_finding(
            findings,
            "error",
            "MWORKS state",
            f"truth/source rate is {mworks_summary['nominal_hz']}Hz, expected {args.truth_rate_hz}Hz.",
            "Use a continuous MWORKS state stream at the controller/setpoint contract rate.",
        )
    if float(mworks_summary["max_step_m"]) >= args.max_continuous_step_m:
        add_finding(
            findings,
            "error",
            "motion continuity",
            f"max pose step is {mworks_summary['max_step_m']}m, threshold {args.max_continuous_step_m}m.",
            "Do not use grid-cell pose jumps for controller or mapping evidence.",
        )
    if lidar_summary["schema"] != "mosim.livox_like_lidar_frame.v1":
        add_finding(findings, "error", "LiDAR schema", f"schema is {lidar_summary['schema']}.", "Use Livox-like Mid360 frames for this gate.")
    if float(lidar_summary["points_per_frame_min"]) < args.min_lidar_points_per_frame:
        add_finding(
            findings,
            "error",
            "LiDAR density",
            f"min points/frame is {lidar_summary['points_per_frame_min']}, threshold {args.min_lidar_points_per_frame}.",
            "Regenerate dense Mid360 scans or lower density only under an explicit degraded-mode task.",
        )
    required_attrs = {"offset_time_ns", "line", "reflectivity", "tag"}
    missing_attrs = sorted(required_attrs - set(lidar_summary["attribute_keys"]))
    if missing_attrs:
        add_finding(findings, "error", "LiDAR attributes", "missing " + ", ".join(missing_attrs), "Preserve Livox per-point timing and line attributes.")
    if lidar_summary["observed_lines"] != [0, 1, 2, 3]:
        add_finding(findings, "error", "LiDAR scan lines", f"observed lines={lidar_summary['observed_lines']}.", "Use the Mid360 four-line route in current config.")
    if lidar_summary["nonmonotonic_time_pairs"] > 0:
        add_finding(findings, "error", "LiDAR time", "LiDAR frame timestamps are not monotonic.", "Fix sensor clocking before FAST-LIO.")

    if fastlio_contract.get("status") not in {"claimable_input_ready"}:
        add_finding(
            findings,
            "error",
            "FAST-LIO input contract",
            f"input contract status is {fastlio_contract.get('status')}.",
            "Patch/replace the FAST-LIO Livox CustomMsg runtime before RViz/UE review.",
        )
    counts = runtime_recording.get("counts", {}) if isinstance(runtime_recording, dict) else {}
    for key, topic in (("odometry", "/odometry"), ("path", "/path"), ("registered_cloud", "/cloud_registered")):
        if int(counts.get(key, 0) or 0) <= 0:
            add_finding(
                findings,
                "error",
                "FAST-LIO runtime output",
                f"{topic} recorded zero samples.",
                "Do not open RViz as evidence until FAST-LIO publishes nonzero runtime outputs.",
            )
    if not runtime_evaluation:
        add_finding(
            findings,
            "error",
            "FAST-LIO truth evaluation",
            "FAST-LIO runtime evaluation is missing.",
            "Evaluate runtime odometry against MWORKS/UE truth before manual RViz/UE review.",
        )
    elif runtime_evaluation.get("status") not in {"passed", "pass", "ok"}:
        metrics = runtime_evaluation.get("metrics", {}) if isinstance(runtime_evaluation, dict) else {}
        add_finding(
            findings,
            "error",
            "FAST-LIO truth evaluation",
            f"evaluation status is {runtime_evaluation.get('status')}; RMSE={metrics.get('position_rmse_m')}m, max={metrics.get('max_position_error_m')}m.",
            "Diagnose extrinsics, timestamp policy, scan pattern, initialization, and frame alignment before opening review windows.",
        )

    if not rviz_pointcloud["uses_mosim_lidar_points"]:
        add_finding(findings, "warning", "RViz2 pointcloud config", "pointcloud window is not subscribed to /mosim/lidar_points.", "Align RViz2 config with MoSim LiDAR topic.")
    if not rviz_pointcloud["uses_fastlio_odometry"]:
        add_finding(findings, "warning", "RViz2 pointcloud config", "pointcloud window is not subscribed to a FAST-LIO odometry topic.", "Align RViz2 config with recorder/FAST-LIO topic.")
    if not rviz_pointcloud["uses_registered_cloud"]:
        add_finding(findings, "warning", "RViz2 pointcloud config", "registered cloud display is missing.", "Show /cloud_registered in the point-cloud window.")
    if not rviz_map["uses_orbit_view"]:
        add_finding(findings, "warning", "RViz2 map config", "RViz view is not explicitly rotatable.", "Use Orbit view for manual inspection.")

    error_count = sum(1 for finding in findings if finding["severity"] == "error")
    warning_count = sum(1 for finding in findings if finding["severity"] == "warning")
    status = "ready_for_manual_rviz_ue_review" if error_count == 0 else "blocked_before_manual_review"
    return {
        "schema": "mosim.realstack_miniloop_gate.v1",
        "status": status,
        "error_count": error_count,
        "warning_count": warning_count,
        "rates_hz": {
            "truth": args.truth_rate_hz,
            "imu_required": args.imu_rate_hz,
            "lidar_required": args.lidar_rate_hz,
            "controller_setpoint": args.controller_rate_hz,
        },
        "paths": {
            "mworks_raw_csv": rel(mworks_raw),
            "livox_frames": rel(livox_frames_path),
            "fastlio_contract": rel(fastlio_contract_path),
            "runtime_recording": rel(runtime_recording_path),
            "runtime_evaluation": rel(runtime_evaluation_path),
            "rviz_pointcloud": rel(rviz_pointcloud_path),
            "rviz_map": rel(rviz_map_path),
        },
        "mworks_state": mworks_summary,
        "lidar": lidar_summary,
        "fastlio_input_contract_status": fastlio_contract.get("status"),
        "fastlio_runtime_counts": counts,
        "fastlio_runtime_evaluation": {
            "status": runtime_evaluation.get("status") if runtime_evaluation else None,
            "metrics": runtime_evaluation.get("metrics", {}) if runtime_evaluation else {},
        },
        "rviz2": {
            "pointcloud": rviz_pointcloud,
            "map": rviz_map,
        },
        "findings": findings,
        "claim_boundary": [
            "This gate allows opening RViz2/UE for human review only after headless runtime topics are credible.",
            "It does not claim final controller integration or planner performance.",
            "Global UE truth remains a validation oracle, not planner input.",
            "Keyboard/mouse controls are view controls only and must not drive UAV pose.",
            "3D local map/planner review is a later phase; this gate covers Factory UAV state, LiDAR, IMU, and FAST-LIO output.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Real UAV Stack Minimum Loop Gate",
        "",
        f"- status: `{report['status']}`",
        f"- errors: `{report['error_count']}`",
        f"- warnings: `{report['warning_count']}`",
        f"- FAST-LIO input contract: `{report['fastlio_input_contract_status']}`",
        f"- FAST-LIO runtime counts: `{report['fastlio_runtime_counts']}`",
        f"- FAST-LIO evaluation: `{report['fastlio_runtime_evaluation']}`",
        "",
        "## Required Rates",
        "",
        f"- truth/controller: `{report['rates_hz']['truth']}` / `{report['rates_hz']['controller_setpoint']}` Hz",
        f"- IMU: `{report['rates_hz']['imu_required']}` Hz",
        f"- LiDAR: `{report['rates_hz']['lidar_required']}` Hz baseline",
        "",
        "## Findings",
        "",
    ]
    if not report["findings"]:
        lines.append("No blocking findings.")
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['severity'].upper()} - {finding['surface']}",
                "",
                finding["detail"],
                "",
                f"Action: {finding['action']}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mworks-raw-csv", default=str(DEFAULT_MWORKS_RAW))
    parser.add_argument("--livox-frames", default=str(DEFAULT_LIVOX_FRAMES))
    parser.add_argument("--fastlio-contract", default=str(DEFAULT_FASTLIO_CONTRACT))
    parser.add_argument("--runtime-recording", default=str(DEFAULT_RUNTIME_RECORDING))
    parser.add_argument("--runtime-evaluation", default=str(DEFAULT_RUNTIME_EVALUATION))
    parser.add_argument("--rviz-pointcloud", default=str(DEFAULT_RVIZ_POINTCLOUD))
    parser.add_argument("--rviz-map", default=str(DEFAULT_RVIZ_MAP))
    parser.add_argument("--sample-frames", type=int, default=8)
    parser.add_argument("--truth-rate-hz", type=float, default=20.0)
    parser.add_argument("--imu-rate-hz", type=float, default=200.0)
    parser.add_argument("--lidar-rate-hz", type=float, default=10.0)
    parser.add_argument("--controller-rate-hz", type=float, default=20.0)
    parser.add_argument("--rate-tolerance-hz", type=float, default=0.1)
    parser.add_argument("--max-continuous-step-m", type=float, default=0.25)
    parser.add_argument("--min-lidar-points-per-frame", type=int, default=15000)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--strict", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = evaluate(args)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        output_json = project_path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if args.output_md:
        write_markdown(project_path(args.output_md), report)
    if args.strict and report["status"] != "ready_for_manual_rviz_ue_review":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
