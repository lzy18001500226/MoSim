#!/usr/bin/env python3
"""Regression checks for native FAST-LIO/RViz runtime wrappers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = None
    if env:
        import os

        merged_env = os.environ.copy()
        merged_env.update(env)
    return subprocess.run(
        command,
        cwd=ROOT,
        env=merged_env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_fastlio_rviz_replay_wrapper_dry_run() -> None:
    for scene_id in ("factoryenvironmentcollect", "derelictcorridormegascans"):
        result = run(
            [
                "bash",
                "Scripts/UE5/run_fastlio_rviz_replay_ros1.sh",
                scene_id,
            ],
            env={"DRY_RUN": "1", "MAX_FRAMES": "2", "LOOP": "0", "START_RVIZ": "0"},
        )
        if "mosim.fastlio_ros1_publish_dryrun.v1" not in result.stdout:
            raise AssertionError(result.stdout)
        if "mosim.ros1_mapping_replay_dryrun.v1" not in result.stdout:
            raise AssertionError(result.stdout)
        if "browser" in result.stdout.lower() or "html" in result.stdout.lower():
            raise AssertionError(result.stdout)
        if "RVIZ_PROFILE=fastlio_pointcloud" not in result.stdout:
            raise AssertionError(result.stdout)


def test_fastlio_rviz2_replay_wrapper_dry_run() -> None:
    for scene_id in ("factoryenvironmentcollect", "derelictcorridormegascans"):
        result = run(
            [
                "bash",
                "Scripts/UE5/run_fastlio_rviz_replay_ros2.sh",
                scene_id,
            ],
            env={"DRY_RUN": "1", "MAX_FRAMES": "2", "LOOP": "0", "START_RVIZ": "0"},
        )
        if "mosim.fastlio_ros2_publish_dryrun.v1" not in result.stdout:
            raise AssertionError(result.stdout)
        if "mosim.ros2_mapping_replay_dryrun.v1" not in result.stdout:
            raise AssertionError(result.stdout)
        if "browser" in result.stdout.lower() or "html" in result.stdout.lower():
            raise AssertionError(result.stdout)
        if "RVIZ_PROFILE=fastlio_pointcloud" not in result.stdout:
            raise AssertionError(result.stdout)
        if '"/cloud_registered"' not in result.stdout or '"/Odometry"' not in result.stdout:
            raise AssertionError(result.stdout)


def test_mapping_rviz_split_window_dry_run() -> None:
    result = run(
        [
            "bash",
            "Scripts/UE5/open_mapping_rviz_ros1.sh",
            "factoryenvironmentcollect",
        ],
        env={"DRY_RUN": "1", "MAX_FRAMES": "2", "LOOP": "0", "RVIZ_PROFILE": "split"},
    )
    if "mosim.rviz_window_contract_dryrun.v1" not in result.stdout:
        raise AssertionError(result.stdout)
    if "mosim_uav_planning_grid.rviz" not in result.stdout:
        raise AssertionError(result.stdout)
    if "mosim_uav_fastlio_pointcloud.rviz" not in result.stdout:
        raise AssertionError(result.stdout)
    if "mosim.ros1_mapping_replay_dryrun.v1" not in result.stdout:
        raise AssertionError(result.stdout)


def test_mapping_rviz2_split_window_dry_run() -> None:
    result = run(
        [
            "bash",
            "Scripts/UE5/open_mapping_rviz_ros2.sh",
            "factoryenvironmentcollect",
        ],
        env={"DRY_RUN": "1", "MAX_FRAMES": "2", "LOOP": "0", "RVIZ_PROFILE": "split"},
    )
    if "mosim.rviz2_window_contract_dryrun.v1" not in result.stdout:
        raise AssertionError(result.stdout)
    if "Config/rviz2/mosim_uav_planning_grid.rviz" not in result.stdout:
        raise AssertionError(result.stdout)
    if "Config/rviz2/mosim_uav_fastlio_pointcloud.rviz" not in result.stdout:
        raise AssertionError(result.stdout)
    if "mosim.ros2_mapping_replay_dryrun.v1" not in result.stdout:
        raise AssertionError(result.stdout)


def test_fastlio_topic_checker_dry_run_contract() -> None:
    result = run(
        ["bash", "Scripts/UE5/check_fastlio_ros1_topics.sh"],
        env={"DRY_RUN": "1"},
    )
    payload = json.loads(result.stdout)
    required = set(payload["required_topics"])
    for topic in ("/velodyne_points", "/imu/data", "/cloud_registered", "/Odometry"):
        if topic not in required:
            raise AssertionError(payload)


def test_fastlio_ros2_topic_checker_dry_run_contract() -> None:
    result = run(
        ["bash", "Scripts/UE5/check_fastlio_ros2_topics.sh"],
        env={"DRY_RUN": "1"},
    )
    payload = json.loads(result.stdout)
    if payload.get("schema") != "mosim.fastlio_ros2_topic_check_dryrun.v1":
        raise AssertionError(payload)
    required = set(payload["required_topics"])
    for topic in ("/velodyne_points", "/imu/data", "/cloud_registered", "/Odometry"):
        if topic not in required:
            raise AssertionError(payload)
    result_inputs_only = run(
        ["bash", "Scripts/UE5/check_fastlio_ros2_topics.sh"],
        env={"DRY_RUN": "1", "REQUIRE_FASTLIO_OUTPUTS": "0"},
    )
    payload_inputs_only = json.loads(result_inputs_only.stdout)
    if "/cloud_registered" in set(payload_inputs_only["required_topics"]):
        raise AssertionError(payload_inputs_only)
    result_spark = run(
        ["bash", "Scripts/UE5/check_fastlio_ros2_topics.sh"],
        env={"DRY_RUN": "1", "FASTLIO_ODOMETRY_TOPIC": "/odometry"},
    )
    payload_spark = json.loads(result_spark.stdout)
    required_spark = set(payload_spark["required_topics"])
    if "/odometry" not in required_spark or "/Odometry" in required_spark:
        raise AssertionError(payload_spark)


def test_ros2_launch_workflow_dry_run_contract() -> None:
    result = run(
        ["bash", "Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh", "factoryenvironmentcollect"],
        env={"DRY_RUN": "1", "MAX_FRAMES": "2", "LOOP": "0", "START_RVIZ": "0"},
    )
    if "mosim.ros2_launch_workflow_dryrun.v1" not in result.stdout:
        raise AssertionError(result.stdout)
    if "mosim_scene_replay.launch.py" not in result.stdout:
        raise AssertionError(result.stdout)
    if "mosim_scene_replay_ros2_ws_factoryenvironmentcollect" not in result.stdout:
        raise AssertionError(result.stdout)
    if "scene" not in result.stdout or "rviz_profile" not in result.stdout:
        raise AssertionError(result.stdout)
    if "browser" in result.stdout.lower() or "html" in result.stdout.lower():
        raise AssertionError(result.stdout)


def test_ros2_launch_file_show_args_contract() -> None:
    result = run(
        [
            "bash",
            "-lc",
            "source /opt/ros/humble/setup.bash && ros2 launch Scripts/ros/mosim_scene_replay/launch/mosim_scene_replay.launch.py --show-args",
        ]
    )
    for argument in ("scene", "rviz_profile", "start_rviz", "start_fastlio", "fastlio_launch_cmd"):
        if argument not in result.stdout:
            raise AssertionError(result.stdout)


def test_spark_fastlio_ros2_candidate_preflight_contract() -> None:
    temp_root = ROOT / "Results" / "tmp" / "spark_fastlio_candidate_test"
    temp_root.mkdir(parents=True, exist_ok=True)
    result = run(
        ["bash", "Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh"],
        env={
            "DRY_RUN": "1",
            "STATUS_JSON": str(temp_root / "status.json"),
            "STATUS_MD": str(temp_root / "status.md"),
        },
    )
    payload = json.loads(result.stdout)
    if payload.get("schema") != "mosim.spark_fastlio_ros2_candidate.v1":
        raise AssertionError(payload)
    if payload.get("repo_url") != "https://github.com/MIT-SPARK/spark-fast-lio.git":
        raise AssertionError(payload)
    if "spark_fast_lio_ros2_ws" not in payload.get("workspace", ""):
        raise AssertionError(payload)
    if "ros2_overlay_pcl_ros" not in payload.get("apt_overlay_dir", ""):
        raise AssertionError(payload)
    if payload.get("runtime_claimable"):
        raise AssertionError(payload)
    for command_name in ("build", "clean_build", "source_overlay_after_download"):
        if command_name not in payload.get("commands", {}):
            raise AssertionError(payload)
    if not payload.get("auto_apt_overlay"):
        raise AssertionError(payload)


def test_fastlio_workspace_bootstrap_dry_run_contract() -> None:
    result = run(
        ["bash", "Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh"],
        env={"DRY_RUN": "1", "BUILD": "0"},
    )
    payload = json.loads(result.stdout)
    if payload.get("schema") != "mosim.fastlio_ros1_workspace_bootstrap_dryrun.v1":
        raise AssertionError(payload)
    if "Results/tmp/fastlio_ros1_ws" not in payload.get("catkin_ws", ""):
        raise AssertionError(payload)
    if "no workspace files were created" not in payload.get("claim", ""):
        raise AssertionError(payload)


def main() -> int:
    test_fastlio_rviz_replay_wrapper_dry_run()
    test_fastlio_rviz2_replay_wrapper_dry_run()
    test_mapping_rviz_split_window_dry_run()
    test_mapping_rviz2_split_window_dry_run()
    test_fastlio_topic_checker_dry_run_contract()
    test_fastlio_ros2_topic_checker_dry_run_contract()
    test_ros2_launch_workflow_dry_run_contract()
    test_ros2_launch_file_show_args_contract()
    test_spark_fastlio_ros2_candidate_preflight_contract()
    test_fastlio_workspace_bootstrap_dry_run_contract()
    print("[OK] FAST-LIO/RViz runtime script regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
