#!/usr/bin/env python3
"""Regression checks for accepted UE scene closed-loop status aggregation."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "summarize_scene_closed_loop.py"
    spec = importlib.util.spec_from_file_location("summarize_scene_closed_loop", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["summarize_scene_closed_loop"] = module
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def write_fixture_scene(root: Path) -> Path:
    scene_dir = root / "fixture"
    for name in ["occupancy_grid.json", "pointcloud_merged.ply", "pointcloud_viewer.html"]:
        (scene_dir / name).parent.mkdir(parents=True, exist_ok=True)
        (scene_dir / name).write_text("fixture\n", encoding="utf-8")
    write_csv(scene_dir / "trajectory.csv", ["time", "x", "y", "z"], [{"time": "0", "x": "0", "y": "0", "z": "1"}])
    write_csv(scene_dir / "render_replay.csv", ["time", "x", "y", "z"], [{"time": "0", "x": "0", "y": "0", "z": "1"}])
    write_csv(scene_dir / "control_reference.csv", ["time", "x_ref", "y_ref", "z_ref"], [{"time": "0", "x_ref": "0", "y_ref": "0", "z_ref": "1"}])
    for name in ["local_known_map_frames.jsonl", "local_plan_frames.jsonl", "lidar_point_frames.jsonl", "fastlio_replay_dataset.jsonl"]:
        write_jsonl(scene_dir / name, [{"time": 0.0}])
    write_json(
        scene_dir / "planner_summary.json",
        {
            "path_cells": 2,
            "replan_count": 1,
            "merged_lidar_point_count": 3,
            "control_tracking_buffer_cells": 1,
            "global_truth_available_to_planner": False,
            "collision_free_against_truth": True,
            "buffered_collision_free_against_truth": True,
        },
    )
    write_json(
        scene_dir / "navigation_control_handoff.json",
        {
            "truth_policy": {
                "global_truth_available_to_planner": False,
                "collision_free_against_truth": True,
                "buffered_collision_free_against_truth": True,
                "control_tracking_buffer_cells": 1,
            }
        },
    )
    write_json(
        scene_dir / "fastlio_adapter_manifest.json",
        {
            "status": "blocked_missing_ros1_runtime",
            "ros_environment": {"ros1_ready": False},
        },
    )
    write_json(
        scene_dir / "planned_quintic_reference_params.json",
        {
            "n_segments": 1,
            "stop_time_s": 1.0,
            "reference_velocity_m_s": 0.8,
            "min_segment_duration_s": 0.9,
        },
    )
    write_csv(
        scene_dir / "mworks_smoke" / "raw" / "sunray150_ue_fixture_linear_mpc_smoke.csv",
        ["time", "x", "y", "x_ref", "y_ref"],
        [{"time": str(index), "x": "0", "y": "0", "x_ref": "0", "y_ref": "0"} for index in range(12)],
    )
    write_json(
        scene_dir / "mworks_smoke" / "metrics" / "sunray150_ue_fixture_linear_mpc_smoke.json",
        {"quality_status": "smoke_only", "valid": True, "duration_s": 1.0, "row_count": 12},
    )
    write_json(
        scene_dir / "mworks_smoke" / "collision" / "mworks_scene_truth_collision.json",
        {
            "pass": True,
            "actual": {"occupied_sample_count": 0, "min_approx_clearance_m": 0.5},
            "reference": {"occupied_sample_count": 0},
        },
    )
    return scene_dir


def test_closed_loop_summary_keeps_fastlio_as_blocker_not_failure() -> None:
    module = load_module()
    temp_root = ROOT / "Results" / "tmp" / "scene_closed_loop_summary_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        scene_dir = write_fixture_scene(temp_root)
        report = module.summarize_scene(scene_dir)
        if report["status"] != "ready_smoke_validated":
            raise AssertionError(report)
        if report["issues"]:
            raise AssertionError(report)
        if "fastlio_blocked_missing_ros1_runtime" not in report["warnings"]:
            raise AssertionError(report)
        if report["mworks_smoke"]["quality_status"] != "smoke_only":
            raise AssertionError(report)
        module.write_markdown(temp_root / "UE_SCENE_CLOSED_LOOP_STATUS.md", [report])
        status = (temp_root / "UE_SCENE_CLOSED_LOOP_STATUS.md").read_text(encoding="utf-8")
        if "blocked_missing_ros1_runtime" not in status:
            raise AssertionError(status)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_closed_loop_summary_keeps_fastlio_as_blocker_not_failure()
    print("[OK] UE scene closed-loop summary regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
