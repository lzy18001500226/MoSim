#!/usr/bin/env python3
"""Regression checks for the ROS/RViz mapping replay publisher contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_scene_pipeline():
    path = ROOT / "Scripts" / "UE5" / "scene_truth_pipeline.py"
    spec = importlib.util.spec_from_file_location("scene_truth_pipeline", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load scene_truth_pipeline.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["scene_truth_pipeline"] = module
    spec.loader.exec_module(module)
    return module


def run_mapping_publisher_dryrun(script_name: str) -> dict:
    scene_pipeline = load_scene_pipeline()
    temp_root = ROOT / "Results" / "tmp" / f"ros_mapping_replay_publisher_test_{script_name}"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    output_root = temp_root / "scene_mapping"
    try:
        scene_id = "factoryenvironmentcollect"
        truth_path = scene_pipeline.scene_truth_path(scene_id)
        truth = scene_pipeline.load_truth(truth_path)
        profile = scene_pipeline.default_profile(str(truth["scene_id"]), truth_path)
        scene_pipeline.run_scene(profile, output_root)
        scene_dir = output_root / scene_id

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "Scripts" / "ros" / script_name),
                "--render-replay-csv",
                str(scene_dir / "render_replay.csv"),
                "--local-known-map-jsonl",
                str(scene_dir / "local_known_map_frames.jsonl"),
                "--local-plan-jsonl",
                str(scene_dir / "local_plan_frames.jsonl"),
                "--lidar-point-frames-jsonl",
                str(scene_dir / "lidar_point_frames.jsonl"),
                "--dry-run",
                "--max-frames",
                "2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        return json.loads(result.stdout)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def assert_mapping_payload(
    payload: dict,
    expected_schema: str,
    expected_claim: str,
    extra_topics: set[str] | None = None,
) -> None:
    if payload["schema"] != expected_schema:
        raise AssertionError(payload)
    if payload["claim"] != expected_claim:
        raise AssertionError(payload)
    if payload["frames"] != 2:
        raise AssertionError(payload)
    if payload["lidar_points"] <= 0:
        raise AssertionError(payload)
    expected_topics = {
        "lidar",
        "local_known_map_cloud",
        "local_occupancy_grid",
        "local_plan",
        "uav_path",
    }
    if extra_topics:
        expected_topics.update(extra_topics)
    if not expected_topics.issubset(set(payload["topics"])):
        raise AssertionError(payload)


def test_ros_mapping_replay_dryrun_contract() -> None:
    payload = run_mapping_publisher_dryrun("publish_mosim_mapping_replay_ros1.py")
    assert_mapping_payload(
        payload,
        "mosim.ros1_mapping_replay_dryrun.v1",
        "dry-run only; no ROS messages were published",
    )


def test_ros2_mapping_replay_dryrun_contract() -> None:
    payload = run_mapping_publisher_dryrun("publish_mosim_mapping_replay_ros2.py")
    assert_mapping_payload(
        payload,
        "mosim.ros2_mapping_replay_dryrun.v1",
        "dry-run only; no ROS2 messages were published",
        extra_topics={"replay_odometry"},
    )
    if payload["topics"].get("tf") != "/tf":
        raise AssertionError(payload)


def main() -> int:
    test_ros_mapping_replay_dryrun_contract()
    test_ros2_mapping_replay_dryrun_contract()
    print("[OK] ROS/RViz mapping replay publisher regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
