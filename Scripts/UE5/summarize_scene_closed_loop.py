#!/usr/bin/env python3
"""Summarize accepted UE scene closed-loop readiness.

This is a status aggregator only. It does not run UE, ROS, FAST-LIO, or
MWORKS. Use it after regenerating scene-truth, FAST-LIO handoff, navigation
handoff, MWORKS smoke, and collision-check artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


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


def count_csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def count_jsonl_rows(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def check_file(path: Path, issues: list[str], label: str) -> bool:
    if path.exists() and path.stat().st_size > 0:
        return True
    issues.append(f"missing_or_empty:{label}:{rel(path)}")
    return False


def summarize_scene(scene_dir: Path) -> dict[str, Any]:
    scene_id = scene_dir.name
    issues: list[str] = []
    warnings: list[str] = []

    planner_path = scene_dir / "planner_summary.json"
    handoff_path = scene_dir / "navigation_control_handoff.json"
    fastlio_path = scene_dir / "fastlio_adapter_manifest.json"
    params_path = scene_dir / "planned_quintic_reference_params.json"
    collision_path = scene_dir / "mworks_smoke" / "collision" / "mworks_scene_truth_collision.json"
    metrics_path = scene_dir / "mworks_smoke" / "metrics" / f"sunray150_ue_{scene_id}_linear_mpc_smoke.json"
    raw_path = scene_dir / "mworks_smoke" / "raw" / f"sunray150_ue_{scene_id}_linear_mpc_smoke.csv"

    required_files = {
        "occupancy_grid": scene_dir / "occupancy_grid.json",
        "trajectory_csv": scene_dir / "trajectory.csv",
        "render_replay_csv": scene_dir / "render_replay.csv",
        "local_known_map_frames": scene_dir / "local_known_map_frames.jsonl",
        "local_plan_frames": scene_dir / "local_plan_frames.jsonl",
        "lidar_point_frames": scene_dir / "lidar_point_frames.jsonl",
        "pointcloud_merged": scene_dir / "pointcloud_merged.ply",
        "fastlio_replay_dataset": scene_dir / "fastlio_replay_dataset.jsonl",
        "navigation_handoff": handoff_path,
        "control_reference": scene_dir / "control_reference.csv",
        "planned_quintic_params": params_path,
        "mworks_metrics": metrics_path,
        "mworks_raw": raw_path,
        "mworks_collision": collision_path,
    }
    existing = {label: check_file(path, issues, label) for label, path in required_files.items()}

    planner: dict[str, Any] = read_json(planner_path) if check_file(planner_path, issues, "planner_summary") else {}
    handoff: dict[str, Any] = read_json(handoff_path) if existing["navigation_handoff"] else {}
    fastlio: dict[str, Any] = read_json(fastlio_path) if check_file(fastlio_path, issues, "fastlio_manifest") else {}
    params: dict[str, Any] = read_json(params_path) if existing["planned_quintic_params"] else {}
    metrics: dict[str, Any] = read_json(metrics_path) if existing["mworks_metrics"] else {}
    collision: dict[str, Any] = read_json(collision_path) if existing["mworks_collision"] else {}

    planner_truth = handoff.get("truth_policy", {})
    if planner.get("global_truth_available_to_planner") is not False:
        issues.append("planner_global_truth_policy_not_false")
    if planner_truth.get("global_truth_available_to_planner") is not False:
        issues.append("handoff_global_truth_policy_not_false")
    if planner.get("collision_free_against_truth") is not True:
        issues.append("planner_reference_not_collision_free")
    if planner.get("buffered_collision_free_against_truth") is not True:
        issues.append("planner_buffered_reference_not_collision_free")
    if planner_truth.get("buffered_collision_free_against_truth") is not True:
        issues.append("handoff_buffered_reference_not_collision_free")

    ros_ready = bool(fastlio.get("ros_environment", {}).get("ros1_ready"))
    fastlio_status = str(fastlio.get("status", "missing"))
    if not ros_ready:
        warnings.append("fastlio_blocked_missing_ros1_runtime")
    elif fastlio_status != "ready_for_ros1_replay":
        warnings.append(f"fastlio_status:{fastlio_status}")

    quality_status = str(metrics.get("quality_status", "missing"))
    if quality_status != "smoke_only":
        issues.append(f"unexpected_mworks_smoke_quality:{quality_status}")
    if metrics.get("valid") is False:
        issues.append("mworks_metrics_marked_invalid")
    if existing["mworks_raw"] and count_csv_rows(raw_path) < 10:
        issues.append("mworks_raw_too_short")

    if collision.get("pass") is not True:
        issues.append("mworks_trajectory_collides_with_ue_truth")
    actual = collision.get("actual", {})
    reference = collision.get("reference", {})
    if actual.get("occupied_sample_count", 1) != 0:
        issues.append(f"mworks_actual_occupied_samples:{actual.get('occupied_sample_count')}")
    if reference.get("occupied_sample_count", 1) != 0:
        issues.append(f"mworks_reference_occupied_samples:{reference.get('occupied_sample_count')}")

    counts = {
        "trajectory_rows": count_csv_rows(scene_dir / "trajectory.csv") if existing["trajectory_csv"] else 0,
        "render_replay_rows": count_csv_rows(scene_dir / "render_replay.csv") if existing["render_replay_csv"] else 0,
        "local_known_map_frames": count_jsonl_rows(scene_dir / "local_known_map_frames.jsonl") if existing["local_known_map_frames"] else 0,
        "local_plan_frames": count_jsonl_rows(scene_dir / "local_plan_frames.jsonl") if existing["local_plan_frames"] else 0,
        "lidar_point_frames": count_jsonl_rows(scene_dir / "lidar_point_frames.jsonl") if existing["lidar_point_frames"] else 0,
        "fastlio_replay_frames": count_jsonl_rows(scene_dir / "fastlio_replay_dataset.jsonl") if existing["fastlio_replay_dataset"] else 0,
        "mworks_rows": count_csv_rows(raw_path) if existing["mworks_raw"] else 0,
    }

    return {
        "scene_id": scene_id,
        "status": "ready_smoke_validated" if not issues else "needs_attention",
        "issues": issues,
        "warnings": warnings,
        "artifacts": {label: rel(path) for label, path in required_files.items()},
        "mapping": {
            "path_cells": planner.get("path_cells"),
            "replan_count": planner.get("replan_count"),
            "lidar_points": planner.get("merged_lidar_point_count"),
            "control_tracking_buffer_cells": planner.get("control_tracking_buffer_cells"),
            "global_truth_available_to_planner": planner.get("global_truth_available_to_planner"),
            "collision_free_against_truth": planner.get("collision_free_against_truth"),
            "buffered_collision_free_against_truth": planner.get("buffered_collision_free_against_truth"),
        },
        "fastlio": {
            "status": fastlio_status,
            "ros1_ready": ros_ready,
            "dataset": rel(scene_dir / "fastlio_replay_dataset.jsonl"),
        },
        "control_reference": {
            "n_segments": params.get("n_segments"),
            "stop_time_s": params.get("stop_time_s"),
            "reference_velocity_m_s": params.get("reference_velocity_m_s"),
            "min_segment_duration_s": params.get("min_segment_duration_s"),
        },
        "mworks_smoke": {
            "quality_status": quality_status,
            "duration_s": metrics.get("duration_s"),
            "row_count": metrics.get("row_count", counts["mworks_rows"]),
            "collision_pass": collision.get("pass"),
            "actual_occupied_sample_count": actual.get("occupied_sample_count"),
            "reference_occupied_sample_count": reference.get("occupied_sample_count"),
            "min_actual_clearance_m": actual.get("min_approx_clearance_m"),
        },
        "counts": counts,
    }


def write_markdown(path: Path, reports: list[dict[str, Any]]) -> None:
    lines = [
        "# UE Scene Closed Loop Status",
        "",
        "This aggregates the accepted scene truth, mapping, FAST-LIO handoff, MWORKS smoke, and UE-truth collision gates.",
        "FAST-LIO replay handoff files are not localization results until ROS1/FAST-LIO produces runtime output.",
        "",
        "| Scene | Status | Path Cells | LiDAR Points | MWORKS Quality | Collision | FAST-LIO | Blockers |",
        "|---|---|---:|---:|---|---|---|---|",
    ]
    for report in reports:
        blockers = report["issues"] + report["warnings"]
        blockers_text = "<br>".join(f"`{item}`" for item in blockers) if blockers else ""
        lines.append(
            f"| `{report['scene_id']}` | `{report['status']}` | "
            f"{report['mapping'].get('path_cells')} | {report['mapping'].get('lidar_points')} | "
            f"`{report['mworks_smoke'].get('quality_status')}` | "
            f"`{str(report['mworks_smoke'].get('collision_pass')).lower()}` | "
            f"`{report['fastlio'].get('status')}` | {blockers_text} |"
        )
    lines.extend([
        "",
        "Acceptance boundary:",
        "- `ready_smoke_validated` means the scene has file-level truth/mapping artifacts, controller-interface MWORKS smoke evidence, and post-simulation UE-truth collision validation.",
        "- `smoke_only` is not a final controller-performance claim.",
        "- `blocked_missing_ros1_runtime` means ROS1/Catkin/FAST-LIO runtime must be installed or sourced before localization can be claimed.",
        "- Global UE occupancy truth is used as a validation oracle only, not as planner input.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--fail-on-issue", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = project_path(args.output_root)
    scene_ids = args.scene or list(DEFAULT_SCENES)
    reports = [summarize_scene(output_root / scene_id) for scene_id in scene_ids]
    payload = {
        "schema": "mosim.ue_scene_closed_loop_status.v1",
        "claim_boundary": [
            "This is an aggregate status, not a new simulation result.",
            "FAST-LIO handoff files are not localization results.",
            "MWORKS smoke evidence validates the control-interface chain only.",
        ],
        "scenes": reports,
        "overall_status": "ready_smoke_validated_with_blockers" if all(not item["issues"] for item in reports) else "needs_attention",
    }
    json_path = output_root / "UE_SCENE_CLOSED_LOOP_STATUS.json"
    md_path = output_root / "UE_SCENE_CLOSED_LOOP_STATUS.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(md_path, reports)
    for report in reports:
        print(
            f"{report['scene_id']}: status={report['status']} "
            f"quality={report['mworks_smoke']['quality_status']} "
            f"collision={report['mworks_smoke']['collision_pass']} "
            f"fastlio={report['fastlio']['status']}"
        )
    if args.fail_on_issue and any(item["issues"] for item in reports):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
