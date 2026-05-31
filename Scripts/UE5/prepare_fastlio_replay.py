#!/usr/bin/env python3
"""Prepare deterministic FAST-LIO replay inputs from UE scene-mapping outputs.

This does not run FAST-LIO. It validates the scene-truth pipeline handoff,
converts world-frame simulated LiDAR hits into a body/LiDAR replay frame, and
writes a manifest that says whether the local ROS1/FAST-LIO runtime is ready.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
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


def read_csv(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, float]] = []
        for row in reader:
            rows.append({key: float(value) for key, value in row.items() if value not in (None, "")})
    if not rows:
        raise ValueError(f"empty replay CSV: {path}")
    return rows


def read_jsonl(path: Path, schema: str) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") != schema:
                raise ValueError(f"unsupported schema at {path}:{line_number}: {payload.get('schema')}")
            frames.append(payload)
    if not frames:
        raise ValueError(f"empty JSONL: {path}")
    return frames


def rotate_world_to_body(dx: float, dy: float, dz: float, yaw: float) -> list[float]:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return [
        round(c * dx + s * dy, 5),
        round(-s * dx + c * dy, 5),
        round(dz, 5),
    ]


def derivative(current: float, previous: float, dt: float) -> float:
    if dt <= 1e-9:
        return 0.0
    return (current - previous) / dt


def ros_environment() -> dict[str, Any]:
    commands = {
        "roscore": shutil.which("roscore"),
        "roslaunch": shutil.which("roslaunch"),
        "catkin_make": shutil.which("catkin_make"),
        "rostopic": shutil.which("rostopic"),
        "rviz": shutil.which("rviz"),
    }
    return {
        "schema": "mosim.ros_environment.v1",
        "commands": commands,
        "ros1_ready": all(commands[name] for name in ("roscore", "roslaunch", "catkin_make")),
    }


def prepare_scene(scene_dir: Path) -> dict[str, Any]:
    handoff_path = scene_dir / "fastlio_handoff.json"
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    generated = handoff.get("generated_inputs", {})
    replay_csv = project_path(generated["render_replay_csv"])
    lidar_jsonl = project_path(generated["lidar_point_frames_jsonl"])
    local_known_jsonl = project_path(generated["local_known_map_jsonl"])
    local_plan_jsonl = project_path(generated["local_plan_jsonl"])
    merged_ply = project_path(generated["merged_pointcloud_ply"])

    rows = read_csv(replay_csv)
    lidar_frames = read_jsonl(lidar_jsonl, "mosim.lidar_point_frame.v1")
    read_jsonl(local_known_jsonl, "mosim.local_known_map_frame.v1")
    read_jsonl(local_plan_jsonl, "mosim.local_plan_frame.v1")
    if len(rows) != len(lidar_frames):
        raise ValueError(f"frame count mismatch for {scene_dir.name}: replay={len(rows)} lidar={len(lidar_frames)}")
    if not merged_ply.exists() or merged_ply.stat().st_size <= 128:
        raise ValueError(f"missing/empty merged point cloud: {merged_ply}")

    dataset_path = scene_dir / "fastlio_replay_dataset.jsonl"
    previous_velocity = [0.0, 0.0, 0.0]
    previous_yaw = rows[0].get("yaw", 0.0)
    previous_time = rows[0].get("time", 0.0)
    previous_position = [rows[0].get("x", 0.0), rows[0].get("y", 0.0), rows[0].get("z", 0.0)]

    with dataset_path.open("w", encoding="utf-8", newline="\n") as handle:
        for index, (row, lidar_frame) in enumerate(zip(rows, lidar_frames)):
            t = row.get("time", index * 0.25)
            dt = max(0.0, t - previous_time)
            position = [row.get("x", 0.0), row.get("y", 0.0), row.get("z", 0.0)]
            rpy = [row.get("roll", 0.0), row.get("pitch", 0.0), row.get("yaw", 0.0)]
            velocity = [
                derivative(position[axis], previous_position[axis], dt)
                for axis in range(3)
            ]
            acceleration = [
                derivative(velocity[axis], previous_velocity[axis], dt)
                for axis in range(3)
            ]
            angular_velocity = [0.0, 0.0, derivative(rpy[2], previous_yaw, dt)]
            points_lidar = [
                rotate_world_to_body(
                    float(point[0]) - position[0],
                    float(point[1]) - position[1],
                    float(point[2]) - position[2],
                    rpy[2],
                )
                for point in lidar_frame.get("points_m", [])
            ]
            payload = {
                "schema": "mosim.fastlio_replay_frame.v1",
                "scene_id": handoff["scene_id"],
                "seq": index,
                "time": round(t, 6),
                "world_frame_id": "ue_world",
                "body_frame_id": "base_link",
                "lidar_frame_id": "velodyne",
                "pose_world_m": [round(value, 5) for value in position],
                "rpy_rad": [round(value, 6) for value in rpy],
                "points_lidar_m": points_lidar,
                "synthetic_imu": {
                    "frame_id": "imu",
                    "orientation_rpy_rad": [round(value, 6) for value in rpy],
                    "angular_velocity_rad_s": [round(value, 6) for value in angular_velocity],
                    "linear_acceleration_m_s2": [round(value, 6) for value in acceleration],
                    "source": "finite_difference_from_scene_truth_replay",
                    "is_measured_imu": False,
                },
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
            previous_position = position
            previous_velocity = velocity
            previous_yaw = rpy[2]
            previous_time = t

    env = ros_environment()
    status = "ros1_runtime_ready" if env["ros1_ready"] else "blocked_missing_ros1_runtime"
    manifest_path = scene_dir / "fastlio_adapter_manifest.json"
    manifest = {
        "schema": "mosim.fastlio_adapter_manifest.v1",
        "scene_id": handoff["scene_id"],
        "status": status,
        "fast_lio_reference_repo": "References/Lab/FAST_LIO",
        "fast_lio_repo_exists": (ROOT / "References/Lab/FAST_LIO/package.xml").exists(),
        "ros_environment": env,
        "generated_outputs": {
            "fastlio_replay_dataset_jsonl": rel(dataset_path),
            "fastlio_adapter_manifest_json": rel(manifest_path),
        },
        "input_evidence": {
            "handoff": rel(handoff_path),
            "render_replay_csv": rel(replay_csv),
            "lidar_point_frames_jsonl": rel(lidar_jsonl),
            "local_known_map_jsonl": rel(local_known_jsonl),
            "local_plan_jsonl": rel(local_plan_jsonl),
            "merged_pointcloud_ply": rel(merged_ply),
        },
        "ros1_topics": {
            "pointcloud2": "/velodyne_points",
            "imu": "/imu/data",
            "lidar_frame_id": "velodyne",
            "imu_frame_id": "imu",
        },
        "run_commands_after_ros_setup": [
            "catkin_make  # from a ROS1 workspace containing References/Lab/FAST_LIO as package fast_lio",
            "source devel/setup.bash",
            "roslaunch fast_lio mapping_velodyne.launch rviz:=false",
            f"python3 Scripts/UE5/publish_fastlio_replay_ros1.py --dataset {rel(dataset_path)} --dry-run",
            f"python3 Scripts/UE5/publish_fastlio_replay_ros1.py --dataset {rel(dataset_path)}",
            f"DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh {handoff['scene_id']}",
            f"Scripts/UE5/open_mapping_rviz_ros1.sh {handoff['scene_id']}",
        ],
        "claim_boundary": [
            "This manifest is a FAST-LIO input adapter, not a completed FAST-LIO localization result.",
            "The IMU channel is synthetic finite-difference data derived from the replay path, not measured flight IMU.",
            "A completed FAST-LIO claim requires ROS runtime output, pose/map topics, logs, and comparison against replay truth.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def write_status_markdown(path: Path, manifests: list[dict[str, Any]]) -> None:
    lines = [
        "# FAST-LIO Replay Adapter Status",
        "",
        "This file records the current bridge between UE scene-truth mapping outputs and FAST-LIO.",
        "It is not a FAST-LIO localization result.",
        "",
        "| Scene | Status | Dataset | ROS1 Ready |",
        "|---|---|---|---:|",
    ]
    for manifest in manifests:
        lines.append(
            f"| `{manifest['scene_id']}` | `{manifest['status']}` | "
            f"`{manifest['generated_outputs']['fastlio_replay_dataset_jsonl']}` | "
            f"{manifest['ros_environment']['ros1_ready']} |"
        )
    lines.extend([
        "",
        "Current blocker if status is `blocked_missing_ros1_runtime`: install/source a ROS1 Catkin environment with FAST-LIO dependencies before running the publisher.",
        "Do not feed the planner global occupancy truth; FAST-LIO replay inputs come from per-frame LiDAR observations and synthetic IMU derived from the replay trajectory.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[], help="Scene id. Default: accepted Factory and Derelict scenes.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--require-ros", action="store_true", help="Return nonzero if ROS1 runtime commands are missing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = project_path(args.output_root)
    scene_ids = args.scene or list(DEFAULT_SCENES)
    manifests = []
    for scene_id in scene_ids:
        manifest = prepare_scene(output_root / scene_id.lower())
        manifests.append(manifest)
        print(f"{scene_id}: {manifest['status']} dataset={manifest['generated_outputs']['fastlio_replay_dataset_jsonl']}")
    write_status_markdown(output_root / "FASTLIO_REPLAY_STATUS.md", manifests)
    if args.require_ros and any(not manifest["ros_environment"]["ros1_ready"] for manifest in manifests):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
