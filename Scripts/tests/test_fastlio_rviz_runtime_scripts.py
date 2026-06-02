#!/usr/bin/env python3
"""Regression checks for current FAST-LIO/RViz runtime entry points."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.setdefault("ROS_LOG_DIR", str(ROOT / "Results" / "tmp" / "ros_logs"))
    if env:
        merged_env.update(env)
    return subprocess.run(
        command,
        cwd=ROOT,
        env=merged_env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )


def test_factory_fastlio_mid360_headless_dry_run() -> None:
    result = run(["bash", "Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh"], env={"DRY_RUN": "1"})
    payload = json.loads(result.stdout)
    if payload.get("schema") != "mosim.factory_fastlio_mid360_headless_dryrun.v1":
        raise AssertionError(payload)
    if payload.get("scene_id") != "factoryenvironmentcollect":
        raise AssertionError(payload)
    for phase in ("dense_lidar_cpp", "mworks_imu_truth", "fast_lio", "runtime_record", "truth_evaluation"):
        if phase not in payload.get("phases", []):
            raise AssertionError(payload)


def test_fastlio_ros2_topic_checker_contract() -> None:
    result = run(["bash", "Scripts/UE5/check_fastlio_ros2_topics.sh"], env={"DRY_RUN": "1"})
    payload = json.loads(result.stdout)
    if payload.get("schema") != "mosim.fastlio_ros2_topic_check_dryrun.v1":
        raise AssertionError(payload)
    required = set(payload["required_topics"])
    for topic in ("/velodyne_points", "/imu/data", "/tf", "/cloud_registered", "/odometry", "/path"):
        if topic not in required:
            raise AssertionError(payload)
    for removed_topic in ("/mosim/local_occupancy_grid", "/mosim/local_plan", "/mosim/replay_odometry"):
        if removed_topic in required:
            raise AssertionError(payload)

    inputs_only = run(
        ["bash", "Scripts/UE5/check_fastlio_ros2_topics.sh"],
        env={
            "DRY_RUN": "1",
            "REQUIRE_FASTLIO_OUTPUTS": "0",
            "FASTLIO_LIDAR_TOPIC": "/mosim/livox/lidar",
            "FASTLIO_IMU_TOPIC": "/mosim/forward/imu",
        },
    )
    input_payload = json.loads(inputs_only.stdout)
    input_required = set(input_payload["required_topics"])
    if "/cloud_registered" in input_required or "/odometry" in input_required:
        raise AssertionError(input_payload)
    for topic in ("/mosim/livox/lidar", "/mosim/forward/imu", "/tf"):
        if topic not in input_required:
            raise AssertionError(input_payload)


def test_ros2_launch_workflow_dry_run_contract() -> None:
    result = run(
        ["bash", "Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh", "factoryenvironmentcollect"],
        env={"DRY_RUN": "1", "MAX_FRAMES": "2", "LOOP": "0", "START_RVIZ": "0"},
    )
    if "mosim.ros2_launch_workflow_dryrun.v1" not in result.stdout:
        raise AssertionError(result.stdout)
    if "mosim_scene_replay.launch.py" not in result.stdout:
        raise AssertionError(result.stdout)
    for phrase in (
        'fastlio_lidar_topic": "/mosim/livox/lidar"',
        'fastlio_pointcloud_topic": "/mosim/lidar_points"',
        'fastlio_imu_topic": "/mosim/forward/imu"',
    ):
        if phrase not in result.stdout:
            raise AssertionError(result.stdout)
    if "mapping_lidar_topic" in result.stdout:
        raise AssertionError(result.stdout)


def test_ros2_launch_file_show_args_contract() -> None:
    result = run(
        [
            "bash",
            "-lc",
            "source /opt/ros/humble/setup.bash && ros2 launch Scripts/ros/mosim_scene_replay/launch/mosim_scene_replay.launch.py --show-args",
        ]
    )
    for argument in (
        "scene",
        "rviz_profile",
        "start_rviz",
        "start_fastlio",
        "scan_duration_s",
        "fastlio_launch_cmd",
        "fastlio_lidar_topic",
        "fastlio_imu_topic",
    ):
        if argument not in result.stdout:
            raise AssertionError(result.stdout)
    if "mapping_lidar_topic" in result.stdout or "planning_grid" in result.stdout:
        raise AssertionError(result.stdout)


def test_fastlio_rviz_config_is_point_style() -> None:
    text = (ROOT / "Config/rviz2/mosim_uav_fastlio_pointcloud.rviz").read_text(encoding="utf-8")
    for phrase in (
        "Value: /mosim/lidar_points",
        "Value: /cloud_registered",
        "Value: /Odometry",
        "Fixed Frame: camera_init",
        "Style: Points",
        "Size (Pixels): 1",
    ):
        if phrase not in text:
            raise AssertionError(phrase)


def main() -> int:
    test_factory_fastlio_mid360_headless_dry_run()
    test_fastlio_ros2_topic_checker_contract()
    test_ros2_launch_workflow_dry_run_contract()
    test_ros2_launch_file_show_args_contract()
    test_fastlio_rviz_config_is_point_style()
    print("[OK] FAST-LIO/RViz runtime script regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
