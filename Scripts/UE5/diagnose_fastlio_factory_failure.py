#!/usr/bin/env python3
"""Diagnose why the Factory FAST-LIO runtime is not claimable yet."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE_DIR = ROOT / "Results" / "unreal_scene_mapping" / "factoryenvironmentcollect"
DEFAULT_CONFIG = ROOT / "Config" / "ros2" / "mosim_spark_fast_lio_velodyne.yaml"


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the small FAST-LIO config subset used by this diagnostic."""
    out: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, out)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip() or ":" not in line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, value = line.strip().split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        value = value.strip()
        if not value:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(value)
    return out


def parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        text = value[1:-1].strip()
        if not text:
            return []
        return [parse_scalar(item.strip()) for item in text.split(",")]
    try:
        if any(mark in value.lower() for mark in (".", "e")):
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"')


def time_summary(times: list[float]) -> dict[str, Any]:
    deltas = [right - left for left, right in zip(times, times[1:])]
    positive = [delta for delta in deltas if delta > 0.0]
    mean_dt = sum(positive) / len(positive) if positive else 0.0
    return {
        "count": len(times),
        "first_s": round(times[0], 6) if times else None,
        "last_s": round(times[-1], 6) if times else None,
        "duration_s": round(times[-1] - times[0], 6) if len(times) > 1 else 0.0,
        "nonmonotonic_pairs": sum(1 for delta in deltas if delta < 0.0),
        "duplicate_pairs": sum(1 for delta in deltas if abs(delta) < 1e-12),
        "min_dt_s": round(min(deltas), 9) if deltas else 0.0,
        "max_dt_s": round(max(deltas), 9) if deltas else 0.0,
        "mean_positive_dt_s": round(mean_dt, 9),
        "mean_hz": round(1.0 / mean_dt, 6) if mean_dt > 0.0 else 0.0,
    }


def vector_distance(left: list[float], right: list[float]) -> float:
    return math.sqrt(sum((float(left[i]) - float(right[i])) ** 2 for i in range(3)))


def path_motion_summary(truth: list[dict[str, Any]]) -> dict[str, Any]:
    positions = [[float(value) for value in row["pose_world_m"]] for row in truth]
    yaws = [float(row.get("rpy_rad", [0.0, 0.0, 0.0])[2]) for row in truth]
    step_distances = [vector_distance(left, right) for left, right in zip(positions, positions[1:])]
    total_distance = sum(step_distances)
    yaw_span = max(yaws) - min(yaws) if yaws else 0.0
    yaw_changes = [abs(right - left) for left, right in zip(yaws, yaws[1:])]
    x_span = max(p[0] for p in positions) - min(p[0] for p in positions) if positions else 0.0
    y_span = max(p[1] for p in positions) - min(p[1] for p in positions) if positions else 0.0
    z_span = max(p[2] for p in positions) - min(p[2] for p in positions) if positions else 0.0
    return {
        "frames": len(truth),
        "total_distance_m": round(total_distance, 6),
        "max_step_m": round(max(step_distances), 6) if step_distances else 0.0,
        "mean_step_m": round(total_distance / len(step_distances), 6) if step_distances else 0.0,
        "x_span_m": round(x_span, 6),
        "y_span_m": round(y_span, 6),
        "z_span_m": round(z_span, 6),
        "yaw_span_rad": round(yaw_span, 6),
        "mean_abs_yaw_step_rad": round(sum(yaw_changes) / len(yaw_changes), 9) if yaw_changes else 0.0,
        "fixed_yaw": yaw_span < 1e-5,
    }


def truth_lidar_summary(truth: list[dict[str, Any]]) -> dict[str, Any]:
    point_counts = [len(row.get("points_lidar_m", [])) for row in truth]
    measured_imu = [bool(row.get("synthetic_imu", {}).get("is_measured_imu")) for row in truth]
    imu_sources = sorted({str(row.get("synthetic_imu", {}).get("source", "unknown")) for row in truth})
    z_values: list[float] = []
    line_values = set()
    has_attrs = False
    for row in truth[: min(20, len(truth))]:
        for point in row.get("points_lidar_m", [])[:2000]:
            if len(point) >= 3:
                z_values.append(float(point[2]))
        for attr in row.get("point_attributes", []):
            has_attrs = True
            if "line" in attr:
                line_values.add(int(attr["line"]))
    return {
        "frame_count": len(truth),
        "points_per_frame_min": min(point_counts) if point_counts else 0,
        "points_per_frame_max": max(point_counts) if point_counts else 0,
        "points_per_frame_avg": round(sum(point_counts) / len(point_counts), 3) if point_counts else 0.0,
        "measured_imu_frames": sum(1 for item in measured_imu if item),
        "synthetic_imu_frames": sum(1 for item in measured_imu if not item),
        "imu_sources": imu_sources,
        "point_attributes_present": has_attrs,
        "observed_lines_in_first_frames": sorted(line_values),
        "z_min_m_first_frames": round(min(z_values), 6) if z_values else None,
        "z_max_m_first_frames": round(max(z_values), 6) if z_values else None,
    }


def load_runtime(scene_dir: Path, name: str) -> dict[str, Any]:
    runtime_dir = scene_dir / name
    return {
        "name": name,
        "evaluation_path": rel(runtime_dir / "FASTLIO_RUNTIME_EVALUATION.json"),
        "recording_path": rel(runtime_dir / "FASTLIO_RUNTIME_RECORDING.json"),
        "odometry_path": rel(runtime_dir / "fastlio_odometry.jsonl"),
        "cloud_summary_path": rel(runtime_dir / "fastlio_registered_cloud_summary.jsonl"),
        "evaluation": read_json(runtime_dir / "FASTLIO_RUNTIME_EVALUATION.json"),
        "recording": read_json(runtime_dir / "FASTLIO_RUNTIME_RECORDING.json"),
        "odometry": read_jsonl(runtime_dir / "fastlio_odometry.jsonl"),
        "cloud_summary": read_jsonl(runtime_dir / "fastlio_registered_cloud_summary.jsonl"),
    }


def runtime_summary(runtime: dict[str, Any], truth_duration_s: float) -> dict[str, Any]:
    evaluation = runtime["evaluation"]
    recording = runtime["recording"]
    odom = runtime["odometry"]
    clouds = runtime["cloud_summary"]
    odom_times = [float(row["time"]) for row in odom]
    cloud_counts = [int(row.get("point_count", 0)) for row in clouds]
    sample_errors = evaluation.get("sample_errors", [])
    error_growth = {}
    if sample_errors:
        error_growth = {
            "first_reported_error_m": sample_errors[0].get("position_error_m"),
            "last_reported_error_m": sample_errors[-1].get("position_error_m"),
            "first_reported_truth_time_s": sample_errors[0].get("truth_time"),
            "last_reported_truth_time_s": sample_errors[-1].get("truth_time"),
        }
    return {
        "name": runtime["name"],
        "status": evaluation.get("status"),
        "metrics": evaluation.get("metrics", {}),
        "odometry_time_quality": evaluation.get("odometry_time_quality", {}),
        "recording_counts": recording.get("counts", {}),
        "recording_duration_s": recording.get("duration_seconds"),
        "odometry_observed": time_summary(odom_times),
        "truth_duration_s": round(truth_duration_s, 6),
        "registered_cloud_frames": len(clouds),
        "registered_cloud_points_min": min(cloud_counts) if cloud_counts else 0,
        "registered_cloud_points_max": max(cloud_counts) if cloud_counts else 0,
        "registered_cloud_points_avg": round(sum(cloud_counts) / len(cloud_counts), 3) if cloud_counts else 0.0,
        "first_error_growth_window": error_growth,
        "paths": {
            "evaluation": runtime["evaluation_path"],
            "recording": runtime["recording_path"],
            "odometry": runtime["odometry_path"],
            "registered_cloud_summary": runtime["cloud_summary_path"],
        },
    }


def config_summary(config: dict[str, Any]) -> dict[str, Any]:
    root = config.get("/**", config.get("**", {}))
    params = root.get("ros__parameters", {})
    preprocess = params.get("preprocess", {})
    mapping = params.get("mapping", {})
    return {
        "lidar_type": preprocess.get("lidar_type"),
        "scan_line": preprocess.get("scan_line"),
        "scan_rate": preprocess.get("scan_rate"),
        "timestamp_unit": preprocess.get("timestamp_unit"),
        "blind": preprocess.get("blind"),
        "extrinsic_est_en": mapping.get("extrinsic_est_en"),
        "extrinsic_T": mapping.get("extrinsic_T"),
        "extrinsic_R": mapping.get("extrinsic_R"),
        "filter_size_map": params.get("filter_size_map"),
        "point_filter_num_for_preprocessing": params.get("point_filter_num_for_preprocessing"),
        "point_filter_num": params.get("point_filter_num"),
    }


def finding(severity: str, surface: str, evidence: str, recommendation: str) -> dict[str, str]:
    return {
        "severity": severity,
        "surface": surface,
        "evidence": evidence,
        "recommendation": recommendation,
    }


def build_findings(
    *,
    adapter: dict[str, Any],
    livox_manifest: dict[str, Any],
    cfg: dict[str, Any],
    motion: dict[str, Any],
    lidar: dict[str, Any],
    runtimes: list[dict[str, Any]],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    replay_generation = adapter.get("replay_generation", {})
    cfg_scan_line = cfg.get("scan_line")
    cfg_lidar_type = cfg.get("lidar_type")
    if cfg_lidar_type != 1:
        findings.append(
            finding(
                "critical",
                "FAST-LIO sensor model",
                f"config lidar_type={cfg_lidar_type}, while target Mid360/Livox-style data should use Livox serial semantics.",
                "Create a Livox/Mid360 FAST-LIO config path (`lidar_type=1`, `scan_line=4`) or route through a FAST-LIO variant confirmed to accept current PointCloud2 fields.",
            )
        )
    if cfg_scan_line != 4:
        findings.append(
            finding(
                "high",
                "FAST-LIO scan lines",
                f"config scan_line={cfg_scan_line}; Sunray/Mid360 references use 4 lines, and the dense replay path emits line values 0-3.",
                "Align scan_line with the actual Mid360/Livox replay contract before retesting localization.",
            )
        )
    if cfg.get("extrinsic_est_en") is False and cfg.get("extrinsic_T") == [0.0, 0.0, 0.0]:
        findings.append(
            finding(
                "medium",
                "LiDAR/IMU extrinsics",
                "extrinsic_est_en=false and extrinsic_T is identity/zero.",
                "Keep identity only for a controlled synthetic frame; otherwise define the Sunray150 LiDAR-to-IMU mount or enable a validated calibration route.",
            )
        )
    if lidar["synthetic_imu_frames"] > 0:
        findings.append(
            finding(
                "critical",
                "IMU source",
                f"{lidar['synthetic_imu_frames']} replay frames use synthetic IMU; sources={lidar['imu_sources']}.",
                "Generate/export measured high-rate MWORKS IMU at about 200Hz or a physically consistent simulated IMU before claiming FAST-LIO quality.",
            )
        )
    if float(lidar["points_per_frame_avg"]) < 5000:
        findings.append(
            finding(
                "critical",
                "LiDAR density",
                f"FAST-LIO truth replay averages {lidar['points_per_frame_avg']} points/frame; adapter max is {replay_generation.get('lidar_max_points_per_frame')}.",
                "Replace the low-density legacy replay with the dense Livox-like C++ transport or a UE C++ raycast sensor before localization tuning.",
            )
        )
    if not lidar["point_attributes_present"]:
        findings.append(
            finding(
                "high",
                "Per-point timing",
                "fastlio_replay_dataset.jsonl has no point_attributes in sampled frames, so per-point offset_time/line/tag are absent from the evaluated dataset.",
                "Use the Livox-like replay frames with offset_time/tag/line, or generate a FAST-LIO dataset that preserves those attributes.",
            )
        )
    if motion["fixed_yaw"]:
        findings.append(
            finding(
                "medium",
                "Motion excitation",
                f"truth yaw span is {motion['yaw_span_rad']} rad and adapter fixed_yaw_for_fastlio_input={replay_generation.get('fixed_yaw_for_fastlio_input')}.",
                "Add realistic yaw and acceleration excitation after the sensor contract is fixed, then evaluate whether observability improves.",
            )
        )
    for runtime in runtimes:
        metrics = runtime["metrics"]
        if runtime["status"] != "pass":
            findings.append(
                finding(
                    "critical",
                    f"Runtime quality: {runtime['name']}",
                    f"status={runtime['status']}, RMSE={metrics.get('position_rmse_m')}m, max_error={metrics.get('max_position_error_m')}m.",
                    "Do not use this Factory run as localization evidence; rerun only after sensor/config/time fixes.",
                )
            )
        time_quality = runtime.get("odometry_time_quality", {})
        if int(time_quality.get("nonmonotonic_pairs", 0)) > 0:
            findings.append(
                finding(
                    "high",
                    f"Odometry timestamps: {runtime['name']}",
                    f"nonmonotonic_pairs={time_quality.get('nonmonotonic_pairs')}, raw_samples={time_quality.get('raw_samples')}, unique_timestamps={time_quality.get('unique_timestamps')}.",
                    "Fix replay/runtime timestamp monotonicity before evaluating controller or mapper quality.",
                )
            )
    if livox_manifest.get("points_per_frame_avg", 0) >= 10000:
        findings.append(
            finding(
                "info",
                "Dense transport status",
                f"Livox-like manifest averages {livox_manifest.get('points_per_frame_avg')} points/frame at {livox_manifest.get('lidar_rate_hz')}Hz, but this is not the evaluated FAST-LIO dataset.",
                "Promote the dense Livox-like dataset into the FAST-LIO runtime path after config and IMU synchronization are corrected.",
            )
        )
    return findings


def diagnose(args: argparse.Namespace) -> dict[str, Any]:
    scene_dir = project_path(args.scene_dir)
    config_path = project_path(args.config)
    truth_path = scene_dir / "fastlio_replay_dataset.jsonl"
    adapter_path = scene_dir / "fastlio_adapter_manifest.json"
    livox_manifest_path = scene_dir / "livox_like_lidar_manifest.json"
    truth = read_jsonl(truth_path)
    adapter = read_json(adapter_path)
    livox_manifest = read_json(livox_manifest_path)
    config = config_summary(parse_simple_yaml(config_path))
    truth_times = [float(row["time"]) for row in truth]
    truth_time = time_summary(truth_times)
    motion = path_motion_summary(truth)
    lidar = truth_lidar_summary(truth)
    runtime_names = args.runtime_dirs or ["fastlio_runtime", "fastlio_runtime_scan099"]
    runtimes = [runtime_summary(load_runtime(scene_dir, name), truth_time["duration_s"]) for name in runtime_names]
    findings = build_findings(
        adapter=adapter,
        livox_manifest=livox_manifest,
        cfg=config,
        motion=motion,
        lidar=lidar,
        runtimes=runtimes,
    )
    return {
        "schema": "mosim.fastlio_factory_failure_diagnosis.v1",
        "scene_id": scene_dir.name,
        "status": "not_claimable",
        "claim_boundary": [
            "This report diagnoses existing Factory FAST-LIO runtime evidence; it is not a new localization run.",
            "Factory FAST-LIO topics exist, but current accuracy fails and must not be used as product evidence.",
            "UE collision truth is a validation/sensor oracle and must not be fed to the planner as a known global map.",
        ],
        "inputs": {
            "scene_dir": rel(scene_dir),
            "truth_dataset": rel(truth_path),
            "fastlio_adapter_manifest": rel(adapter_path),
            "livox_like_lidar_manifest": rel(livox_manifest_path),
            "fastlio_config": rel(config_path),
        },
        "fastlio_config": config,
        "adapter_replay_generation": adapter.get("replay_generation", {}),
        "truth_time": truth_time,
        "truth_motion": motion,
        "truth_lidar_and_imu": lidar,
        "livox_like_dense_manifest": {
            key: livox_manifest.get(key)
            for key in (
                "frame_count",
                "points_per_frame_requested",
                "points_per_frame_min",
                "points_per_frame_max",
                "points_per_frame_avg",
                "lidar_rate_hz",
                "point_rate_hz",
                "scan_mode_csv",
                "claim",
            )
        },
        "runtime_summaries": runtimes,
        "findings": findings,
        "next_actions_ordered": [
            "Stop treating Factory FAST-LIO as claimable evidence until RMSE/max-error pass the runtime gate.",
            "Move Factory runtime input from low-density legacy replay to dense Livox/Mid360-shaped data with per-point timing fields.",
            "Create a Mid360/Livox FAST-LIO config path and test lidar_type/scan_line/timestamp_unit against the selected ROS2 FAST-LIO implementation.",
            "Replace synthetic finite-difference IMU with high-rate MWORKS IMU or a physically consistent simulated IMU synchronized to LiDAR.",
            "Fix nonmonotonic odometry/replay timestamp behavior and rerun runtime evaluation.",
            "Only after localization passes, reconnect local 3D map and planner review windows.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Factory FAST-LIO Failure Diagnosis",
        "",
        f"- scene_id: `{report['scene_id']}`",
        f"- status: `{report['status']}`",
        f"- truth_dataset: `{report['inputs']['truth_dataset']}`",
        f"- fastlio_config: `{report['inputs']['fastlio_config']}`",
        "",
        "## Summary",
        "",
        "Factory FAST-LIO is not blocked by topic plumbing: existing recordings contain",
        "odometry, path, and registered-cloud summaries. It is blocked by localization",
        "quality and input-contract mismatches.",
        "",
        "## Runtime Results",
        "",
    ]
    for runtime in report["runtime_summaries"]:
        metrics = runtime["metrics"]
        time_quality = runtime["odometry_time_quality"]
        lines.extend(
            [
                f"### {runtime['name']}",
                "",
                f"- status: `{runtime['status']}`",
                f"- position_rmse_m: `{metrics.get('position_rmse_m')}`",
                f"- max_position_error_m: `{metrics.get('max_position_error_m')}`",
                f"- yaw_rmse_rad: `{metrics.get('yaw_rmse_rad')}`",
                f"- odometry nonmonotonic_pairs: `{time_quality.get('nonmonotonic_pairs')}`",
                f"- registered_cloud_points_avg: `{runtime['registered_cloud_points_avg']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Key Input Contract",
            "",
            f"- config lidar_type: `{report['fastlio_config'].get('lidar_type')}`",
            f"- config scan_line: `{report['fastlio_config'].get('scan_line')}`",
            f"- config scan_rate: `{report['fastlio_config'].get('scan_rate')}`",
            f"- config extrinsic_est_en: `{report['fastlio_config'].get('extrinsic_est_en')}`",
            f"- truth points/frame avg: `{report['truth_lidar_and_imu']['points_per_frame_avg']}`",
            f"- truth synthetic IMU frames: `{report['truth_lidar_and_imu']['synthetic_imu_frames']}`",
            f"- truth fixed_yaw: `{report['truth_motion']['fixed_yaw']}`",
            "",
            "## Findings",
            "",
        ]
    )
    for item in report["findings"]:
        lines.extend(
            [
                f"- `{item['severity']}` {item['surface']}: {item['evidence']}",
                f"  Recommendation: {item['recommendation']}",
            ]
        )
    lines.extend(["", "## Next Actions", ""])
    for index, action in enumerate(report["next_actions_ordered"], start=1):
        lines.append(f"{index}. {action}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-dir", type=Path, default=DEFAULT_SCENE_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--runtime-dir", action="append", dest="runtime_dirs")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = diagnose(args)
    output_json = project_path(args.output_json) if args.output_json else project_path(args.scene_dir) / "fastlio_failure_diagnosis.json"
    output_md = project_path(args.output_md) if args.output_md else project_path(args.scene_dir) / "FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md"
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(output_md, report)
    print(json.dumps({"status": report["status"], "output_json": rel(output_json), "output_md": rel(output_md)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
