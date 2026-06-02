#!/usr/bin/env python3
"""Regression checks for the MWORKS UAV state ROS2 replay bridge."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_bridge():
    path = ROOT / "Scripts" / "ros" / "publish_mworks_uav_state_ros2.py"
    spec = importlib.util.spec_from_file_location("publish_mworks_uav_state_ros2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load publish_mworks_uav_state_ros2.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["publish_mworks_uav_state_ros2"] = module
    spec.loader.exec_module(module)
    return module


def run_dryrun(max_frames: int = 3) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "ros" / "publish_mworks_uav_state_ros2.py"),
            "--mworks-raw-csv",
            "Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/"
            "sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv",
            "--lidar-point-frames-jsonl",
            "Results/unreal_scene_mapping/factoryenvironmentcollect/lidar_point_frames.jsonl",
            "--dry-run",
            "--max-frames",
            str(max_frames),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_mworks_uav_state_dryrun_contract() -> None:
    payload = run_dryrun()
    if payload["schema"] != "mosim.mworks_uav_state_ros2_dryrun.v1":
        raise AssertionError(payload)
    if payload["source"] != "MWORKS_MCP_raw_replay":
        raise AssertionError(payload)
    if payload["frames"] != 3:
        raise AssertionError(payload)
    if payload["target_rates_hz"]["truth_odometry"] != 20.0:
        raise AssertionError(payload)
    if payload["target_rates_hz"]["imu"] != 200.0:
        raise AssertionError(payload)
    if payload["target_rates_hz"]["controller_setpoint_contract"] != 20.0:
        raise AssertionError(payload)
    for topic_key in ("truth_odometry", "imu", "lidar", "tf"):
        if topic_key not in payload["topics"]:
            raise AssertionError(payload)
    if payload["pointcloud2_fields"] != ["x", "y", "z", "intensity", "time", "ring"]:
        raise AssertionError(payload)
    if "/cloud_registered" not in payload["not_published"]:
        raise AssertionError(payload)
    if "closed-loop co-simulation" not in payload["claim"]:
        raise AssertionError(payload)


def test_mworks_uav_state_path_guard_and_math() -> None:
    bridge = load_bridge()
    rows = [
        {"time": 0.0, "x": 0.0, "y": 0.0, "z": 1.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0},
        {"time": 0.05, "x": 0.1, "y": 0.0, "z": 1.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.1},
        {"time": 0.10, "x": 0.2, "y": 0.0, "z": 1.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.2},
    ]
    vx, vy, vz = bridge.velocity(rows, 1)
    if abs(vx - 2.0) > 1e-9 or abs(vy) > 1e-9 or abs(vz) > 1e-9:
        raise AssertionError((vx, vy, vz))
    midpoint = bridge.interpolate_rows(rows, 0, 0.5)
    if abs(midpoint["x"] - 0.05) > 1e-9 or abs(midpoint["yaw"] - 0.05) > 1e-9:
        raise AssertionError(midpoint)
    qx, qy, qz, qw = bridge.quaternion_from_rpy(0.0, 0.0, 0.0)
    if (qx, qy, qz, qw) != (0.0, 0.0, 0.0, 1.0):
        raise AssertionError((qx, qy, qz, qw))
    cloud = bridge.pack_livox_like_cloud([[0, 0, 0], [1, 2, 3]], 0.1, 4, 50.0)
    if len(cloud) != 48:
        raise AssertionError(len(cloud))
    try:
        bridge.project_path("/mnt/c/Users/HP/Desktop/not_mosim/file.txt")
    except SystemExit:
        return
    raise AssertionError("project_path accepted a path outside MoSim")


def test_mworks_uav_state_accepts_livox_like_schema() -> None:
    temp_root = ROOT / "Results" / "tmp" / "mworks_uav_state_livox_schema_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    temp_root.mkdir(parents=True)
    lidar_path = temp_root / "livox_like.jsonl"
    try:
        lidar_path.write_text(
            json.dumps(
                {
                    "schema": "mosim.livox_like_lidar_frame.v1",
                    "scene_id": "fixture",
                    "seq": 0,
                    "time": 0.0,
                    "points_m": [[1.0, 2.0, 3.0]],
                    "point_attributes": [{"offset_time_ns": 0, "line": 0, "reflectivity": 100, "tag": 16}],
                },
                separators=(",", ":"),
            )
            + "\n"
            + json.dumps(
                {
                    "schema": "mosim.livox_like_lidar_frame.v1",
                    "scene_id": "fixture",
                    "seq": 1,
                    "time": 0.05,
                    "points_m": [[2.0, 3.0, 4.0]],
                    "point_attributes": [{"offset_time_ns": 0, "line": 1, "reflectivity": 100, "tag": 16}],
                },
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "Scripts" / "ros" / "publish_mworks_uav_state_ros2.py"),
                "--mworks-raw-csv",
                "Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/"
                "sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv",
                "--lidar-point-frames-jsonl",
                str(lidar_path),
                "--dry-run",
                "--max-frames",
                "2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(result.stdout)
        if payload["frames"] != 2:
            raise AssertionError(payload)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_mworks_uav_state_dryrun_contract()
    test_mworks_uav_state_path_guard_and_math()
    test_mworks_uav_state_accepts_livox_like_schema()
    print("[OK] MWORKS UAV state ROS2 bridge regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
