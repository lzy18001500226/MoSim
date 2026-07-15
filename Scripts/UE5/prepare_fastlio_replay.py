#!/usr/bin/env python3
"""Prepare deterministic FAST-LIO replay inputs from UE scene-mapping outputs.

This does not run FAST-LIO. It validates the scene-truth pipeline handoff,
converts world-frame simulated LiDAR hits into a body/LiDAR replay frame, and
writes a manifest that says whether the local ROS2/RViz2 replay runtime is
ready. The local FAST_LIO reference is ROS1/Catkin and remains a degraded
compatibility path on Ubuntu 22.04.
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
DEFAULT_FASTLIO_REPLAY_STEP_SECONDS = 0.1
DEFAULT_LIDAR_POINTS_MAX = 512
DEFAULT_LIDAR_VERTICAL_ANGLES_DEG = (-15.0, -10.0, -5.0, 0.0, 5.0, 10.0)
DEFAULT_SCENE_LIDAR_CONFIG = {
    "factoryenvironmentcollect": {"radius_m": 14.0, "beams": 120},
    "derelictcorridormegascans": {"radius_m": 10.0, "beams": 120},
}


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


class ReplayOccupancyGrid:
    def __init__(
        self,
        *,
        x_min: float,
        y_min: float,
        resolution: float,
        width: int,
        height: int,
        occupied: set[tuple[int, int]],
        z_intervals: dict[tuple[int, int], list[tuple[float, float]]] | None = None,
    ) -> None:
        self.x_min = x_min
        self.y_min = y_min
        self.resolution = resolution
        self.width = width
        self.height = height
        self.occupied = occupied
        self.z_intervals = z_intervals or {}

    def in_bounds(self, cell: tuple[int, int]) -> bool:
        return 0 <= cell[0] < self.width and 0 <= cell[1] < self.height

    def world_to_cell(self, x: float, y: float) -> tuple[int, int]:
        return (
            int(round((x - self.x_min) / self.resolution)),
            int(round((y - self.y_min) / self.resolution)),
        )

    def cell_to_world(self, cell: tuple[int, int], z: float) -> list[float]:
        return [
            self.x_min + cell[0] * self.resolution,
            self.y_min + cell[1] * self.resolution,
            z,
        ]

    def is_occupied(self, cell: tuple[int, int]) -> bool:
        if not self.in_bounds(cell):
            return True
        return cell in self.occupied

    def is_occupied_at_z(self, cell: tuple[int, int], z_m: float) -> bool:
        if not self.in_bounds(cell):
            return True
        intervals = self.z_intervals.get(cell)
        if not intervals:
            return self.is_occupied(cell)
        return any(low <= z_m <= high for low, high in intervals)


def read_occupancy_grid(path: Path) -> ReplayOccupancyGrid:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "mosim.ue_scene_occupancy.v1":
        raise ValueError(f"unsupported occupancy schema in {path}: {payload.get('schema')}")
    grid = payload["grid"]
    origin = grid["origin_xy_m"]
    size = grid["size"]
    occupied = {
        (int(cell[0]), int(cell[1]))
        for cell in grid.get("occupied_cells_xy", [])
    }
    return ReplayOccupancyGrid(
        x_min=float(origin[0]),
        y_min=float(origin[1]),
        resolution=float(grid["resolution_m"]),
        width=int(size[0]),
        height=int(size[1]),
        occupied=occupied,
    )


def merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0]]
    for low, high in intervals[1:]:
        prev_low, prev_high = merged[-1]
        if low <= prev_high + 1e-6:
            merged[-1] = (prev_low, max(prev_high, high))
        else:
            merged.append((low, high))
    return merged


def attach_collision_height_index(
    grid: ReplayOccupancyGrid,
    path: Path,
    *,
    flight_z_m: float,
    radius_padding_m: float,
) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "mosim.unreal_scene_truth.v1":
        raise ValueError(f"unsupported truth schema in {path}: {payload.get('schema')}")
    raw_intervals: dict[tuple[int, int], list[tuple[float, float]]] = {}
    used_boxes = 0
    for proxy in payload.get("collision_proxies", []):
        semantic_type = str(proxy.get("semantic_type", "obstacle"))
        if semantic_type == "sensor":
            continue
        min_m = [float(value) for value in proxy["min_m"]]
        max_m = [float(value) for value in proxy["max_m"]]
        z_min = min(min_m[2], max_m[2])
        z_max = max(min_m[2], max_m[2])
        if semantic_type == "terrain" and z_max < flight_z_m - 0.25:
            continue
        if z_max < flight_z_m - radius_padding_m:
            continue
        if z_min > flight_z_m + radius_padding_m:
            continue
        x0 = max(0, int(math.floor((min(min_m[0], max_m[0]) - grid.x_min) / grid.resolution)))
        x1 = min(grid.width - 1, int(math.ceil((max(min_m[0], max_m[0]) - grid.x_min) / grid.resolution)))
        y0 = max(0, int(math.floor((min(min_m[1], max_m[1]) - grid.y_min) / grid.resolution)))
        y1 = min(grid.height - 1, int(math.ceil((max(min_m[1], max_m[1]) - grid.y_min) / grid.resolution)))
        if x0 > x1 or y0 > y1:
            continue
        used_boxes += 1
        interval = (z_min, z_max)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                raw_intervals.setdefault((x, y), []).append(interval)
    grid.z_intervals = {
        cell: merge_intervals(intervals)
        for cell, intervals in raw_intervals.items()
    }
    return used_boxes


def cast_lidar_points_for_pose(
    grid: ReplayOccupancyGrid,
    position: list[float],
    *,
    beams: int,
    radius_m: float,
    max_points: int = DEFAULT_LIDAR_POINTS_MAX,
) -> list[list[float]]:
    points: list[list[float]] = []
    step_m = max(grid.resolution * 0.5, 0.12)
    max_steps = int(math.ceil(radius_m / step_m))
    for ring, vertical_deg in enumerate(DEFAULT_LIDAR_VERTICAL_ANGLES_DEG):
        vertical = math.radians(vertical_deg)
        horizontal_scale = math.cos(vertical)
        dz = math.sin(vertical)
        for beam in range(beams):
            angle = 2.0 * math.pi * beam / beams
            direction = [math.cos(angle) * horizontal_scale, math.sin(angle) * horizontal_scale, dz]
            hit_distance: float | None = None
            for step in range(1, max_steps + 1):
                distance = step * step_m
                x = position[0] + direction[0] * distance
                y = position[1] + direction[1] * distance
                z = position[2] + direction[2] * distance
                cell = grid.world_to_cell(x, y)
                if not grid.in_bounds(cell):
                    break
                if grid.is_occupied_at_z(cell, z):
                    hit_distance = distance
                    break
            if hit_distance is None:
                continue
            hit = [
                position[0] + direction[0] * hit_distance,
                position[1] + direction[1] * hit_distance,
                position[2] + direction[2] * hit_distance,
            ]
            points.append([round(hit[0], 5), round(hit[1], 5), round(hit[2], 5)])
            if max_points > 0 and len(points) >= max_points:
                return points
    return points


def sample_rows_by_time(rows: list[dict[str, float]], step_seconds: float) -> list[dict[str, float]]:
    if step_seconds <= 0:
        return rows
    selected: list[dict[str, float]] = []
    next_time = rows[0].get("time", 0.0)
    cursor = 0
    while cursor < len(rows):
        best_index = cursor
        best_distance = abs(rows[cursor].get("time", 0.0) - next_time)
        while cursor + 1 < len(rows):
            candidate_distance = abs(rows[cursor + 1].get("time", 0.0) - next_time)
            if candidate_distance > best_distance:
                break
            cursor += 1
            best_index = cursor
            best_distance = candidate_distance
        row = rows[best_index]
        if not selected or row.get("time", 0.0) > selected[-1].get("time", 0.0) + 1e-9:
            selected.append(row)
        next_time += step_seconds
        while cursor < len(rows) and rows[cursor].get("time", 0.0) < next_time - step_seconds * 0.5:
            cursor += 1
    return selected


def control_reference_rows(path: Path) -> list[dict[str, float]]:
    rows = read_csv(path)
    converted: list[dict[str, float]] = []
    for row in rows:
        converted.append(
            {
                "time": row.get("time", 0.0),
                "x": row["x_ref"],
                "y": row["y_ref"],
                "z": row["z_ref"],
                "vx": row.get("vx_ref", 0.0),
                "vy": row.get("vy_ref", 0.0),
                "vz": row.get("vz_ref", 0.0),
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": row.get("yaw_ref", 0.0),
            }
        )
    return sample_rows_by_time(converted, DEFAULT_FASTLIO_REPLAY_STEP_SECONDS)


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


def imu_specific_force_m_s2(linear_acceleration_world: list[float]) -> list[float]:
    """Return synthetic IMU acceleration with gravity included.

    FAST-LIO-family initializers estimate gravity from the IMU acceleration
    norm. A zero vector makes that initialization ill-conditioned, so replay
    data must include a physically plausible static gravity component even
    when the scene-truth trajectory has no measured IMU.
    """
    return [
        linear_acceleration_world[0],
        linear_acceleration_world[1],
        linear_acceleration_world[2] + 9.81,
    ]


def rotate_world_vector_to_body(vector: list[float], yaw: float) -> list[float]:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return [
        c * vector[0] + s * vector[1],
        -s * vector[0] + c * vector[1],
        vector[2],
    ]


def write_fastlio_dataset(
    *,
    dataset_path: Path,
    scene_id: str,
    pose_rows: list[dict[str, float]],
    lidar_points_world: list[list[list[float]]],
    pose_source: str,
    lidar_source: str,
    fixed_yaw: bool,
) -> None:
    if len(pose_rows) != len(lidar_points_world):
        raise ValueError(f"frame count mismatch for {scene_id}: pose={len(pose_rows)} lidar={len(lidar_points_world)}")
    previous_velocity = [pose_rows[0].get("vx", 0.0), pose_rows[0].get("vy", 0.0), pose_rows[0].get("vz", 0.0)]
    previous_yaw = pose_rows[0].get("yaw", 0.0)
    previous_time = pose_rows[0].get("time", 0.0)
    previous_position = [
        pose_rows[0].get("x", 0.0),
        pose_rows[0].get("y", 0.0),
        pose_rows[0].get("z", 0.0),
    ]
    initial_yaw = previous_yaw

    with dataset_path.open("w", encoding="utf-8", newline="\n") as handle:
        for index, (row, frame_points_world) in enumerate(zip(pose_rows, lidar_points_world)):
            t = row.get("time", index * DEFAULT_FASTLIO_REPLAY_STEP_SECONDS)
            dt = max(0.0, t - previous_time)
            position = [row.get("x", 0.0), row.get("y", 0.0), row.get("z", 0.0)]
            yaw = initial_yaw if fixed_yaw else row.get("yaw", 0.0)
            rpy = [row.get("roll", 0.0), row.get("pitch", 0.0), yaw]
            if all(key in row for key in ("vx", "vy", "vz")):
                velocity = [row.get("vx", 0.0), row.get("vy", 0.0), row.get("vz", 0.0)]
            else:
                velocity = [
                    derivative(position[axis], previous_position[axis], dt)
                    for axis in range(3)
                ]
            acceleration = [
                derivative(velocity[axis], previous_velocity[axis], dt)
                for axis in range(3)
            ]
            synthetic_specific_force_world = imu_specific_force_m_s2(acceleration)
            synthetic_specific_force = rotate_world_vector_to_body(synthetic_specific_force_world, rpy[2])
            angular_velocity = [0.0, 0.0, derivative(rpy[2], previous_yaw, dt)]
            points_lidar = [
                rotate_world_to_body(
                    float(point[0]) - position[0],
                    float(point[1]) - position[1],
                    float(point[2]) - position[2],
                    rpy[2],
                )
                for point in frame_points_world
            ]
            payload = {
                "schema": "mosim.fastlio_replay_frame.v1",
                "scene_id": scene_id,
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
                    "linear_acceleration_m_s2": [round(value, 6) for value in synthetic_specific_force],
                    "finite_difference_linear_acceleration_m_s2": [
                        round(value, 6) for value in acceleration
                    ],
                    "linear_acceleration_coordinate_frame": "body_yaw_aligned",
                    "gravity_component_m_s2": [0.0, 0.0, 9.81],
                    "source": "finite_difference_from_scene_truth_replay",
                    "is_measured_imu": False,
                },
                "input_trace": {
                    "pose_source": pose_source,
                    "lidar_source": lidar_source,
                    "fixed_yaw_for_fastlio_input": fixed_yaw,
                },
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
            previous_position = position
            previous_velocity = velocity
            previous_yaw = rpy[2]
            previous_time = t


def ros_environment() -> dict[str, Any]:
    ros2_bin = Path("/opt/ros/humble/bin")

    def which_or_ros2_bin(name: str) -> str | None:
        found = shutil.which(name)
        if found:
            return found
        candidate = ros2_bin / name
        if candidate.exists():
            return str(candidate)
        return None

    commands = {
        "ros2": which_or_ros2_bin("ros2"),
        "rviz2": which_or_ros2_bin("rviz2"),
        "colcon": shutil.which("colcon"),
        "roscore": shutil.which("roscore"),
        "roslaunch": shutil.which("roslaunch"),
        "catkin_make": shutil.which("catkin_make"),
        "rostopic": shutil.which("rostopic"),
        "rviz": shutil.which("rviz"),
    }
    ros2_ready = all(commands[name] for name in ("ros2", "rviz2", "colcon"))
    ros1_ready = all(commands[name] for name in ("roscore", "roslaunch", "catkin_make"))
    return {
        "schema": "mosim.ros_environment.v1",
        "commands": commands,
        "ros2_replay_ready": ros2_ready,
        "ros1_ready": ros1_ready,
        "primary_runtime": "ros2_humble",
    }


def prepare_scene(scene_dir: Path) -> dict[str, Any]:
    handoff_path = scene_dir / "fastlio_handoff.json"
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    generated = handoff.get("generated_inputs", {})
    replay_csv = project_path(generated["render_replay_csv"])
    lidar_jsonl = project_path(generated["lidar_point_frames_jsonl"])
    occupancy_json = project_path(generated["occupancy_json"])
    local_known_jsonl = project_path(generated["local_known_map_jsonl"])
    local_plan_jsonl = project_path(generated["local_plan_jsonl"])
    merged_ply = project_path(generated["merged_pointcloud_ply"])

    read_jsonl(local_known_jsonl, "mosim.local_known_map_frame.v1")
    read_jsonl(local_plan_jsonl, "mosim.local_plan_frame.v1")
    if not merged_ply.exists() or merged_ply.stat().st_size <= 128:
        raise ValueError(f"missing/empty merged point cloud: {merged_ply}")

    dataset_path = scene_dir / "fastlio_replay_dataset.jsonl"
    control_reference_csv = scene_dir / "control_reference.csv"
    replay_input_mode = "render_replay_discrete_fallback"
    replay_fps = 1.0 / DEFAULT_FASTLIO_REPLAY_STEP_SECONDS
    fixed_yaw_for_fastlio_input = False
    truth_source_path = project_path(handoff["truth_source"]) if handoff.get("truth_source") else None
    if control_reference_csv.exists():
        rows = control_reference_rows(control_reference_csv)
        grid = read_occupancy_grid(occupancy_json)
        lidar_config = DEFAULT_SCENE_LIDAR_CONFIG.get(handoff["scene_id"], {"radius_m": 10.0, "beams": 180})
        height_index_source_count = (
            attach_collision_height_index(
                grid,
                truth_source_path,
                flight_z_m=rows[0]["z"],
                radius_padding_m=float(lidar_config["radius_m"]),
            )
            if truth_source_path is not None
            else 0
        )
        lidar_points = [
            cast_lidar_points_for_pose(
                grid,
                [row["x"], row["y"], row["z"]],
                beams=int(lidar_config["beams"]),
                radius_m=float(lidar_config["radius_m"]),
            )
            for row in rows
        ]
        fixed_yaw_for_fastlio_input = True
        replay_input_mode = "control_reference_smooth_3d_raycast"
        write_fastlio_dataset(
            dataset_path=dataset_path,
            scene_id=handoff["scene_id"],
            pose_rows=rows,
            lidar_points_world=lidar_points,
            pose_source=rel(control_reference_csv),
            lidar_source=rel(occupancy_json),
            fixed_yaw=fixed_yaw_for_fastlio_input,
        )
    else:
        rows = read_csv(replay_csv)
        lidar_frames = read_jsonl(lidar_jsonl, "mosim.lidar_point_frame.v1")
        if len(rows) != len(lidar_frames):
            raise ValueError(f"frame count mismatch for {scene_dir.name}: replay={len(rows)} lidar={len(lidar_frames)}")
        lidar_points = [frame.get("points_m", []) for frame in lidar_frames]
        replay_fps = 1.0 / max(1e-9, rows[1].get("time", 0.25) - rows[0].get("time", 0.0)) if len(rows) > 1 else 4.0
        write_fastlio_dataset(
            dataset_path=dataset_path,
            scene_id=handoff["scene_id"],
            pose_rows=rows,
            lidar_points_world=lidar_points,
            pose_source=rel(replay_csv),
            lidar_source=rel(lidar_jsonl),
            fixed_yaw=fixed_yaw_for_fastlio_input,
        )

    env = ros_environment()
    status = "ready_for_ros2_replay" if env["ros2_replay_ready"] else "blocked_missing_ros2_runtime"
    manifest_path = scene_dir / "fastlio_adapter_manifest.json"
    manifest = {
        "schema": "mosim.fastlio_adapter_manifest.v1",
        "scene_id": handoff["scene_id"],
        "status": status,
        "fast_lio_reference_repo": "References/Lab/localization_slam/FAST_LIO",
        "fast_lio_repo_exists": (ROOT / "References/Lab/localization_slam/FAST_LIO/package.xml").exists(),
        "ros_environment": env,
        "generated_outputs": {
            "fastlio_replay_dataset_jsonl": rel(dataset_path),
            "fastlio_adapter_manifest_json": rel(manifest_path),
        },
        "replay_generation": {
            "mode": replay_input_mode,
            "fps": replay_fps,
            "fixed_yaw_for_fastlio_input": fixed_yaw_for_fastlio_input,
            "preferred_pose_source": rel(control_reference_csv) if control_reference_csv.exists() else None,
            "fallback_pose_source": rel(replay_csv),
            "lidar_source": rel(truth_source_path) if replay_input_mode == "control_reference_smooth_3d_raycast" and truth_source_path else rel(lidar_jsonl),
            "truth_source_for_3d_lidar": rel(truth_source_path) if truth_source_path else None,
            "height_index_source_proxy_count": height_index_source_count if replay_input_mode == "control_reference_smooth_3d_raycast" else 0,
            "lidar_vertical_angles_deg": list(DEFAULT_LIDAR_VERTICAL_ANGLES_DEG),
            "lidar_max_points_per_frame": DEFAULT_LIDAR_POINTS_MAX,
            "synthetic_imu_is_measured": False,
        },
        "input_evidence": {
            "handoff": rel(handoff_path),
            "render_replay_csv": rel(replay_csv),
            "control_reference_csv": rel(control_reference_csv) if control_reference_csv.exists() else None,
            "occupancy_json": rel(occupancy_json),
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
        "ros2_topics": {
            "pointcloud2": "/mosim/lidar_points",
            "imu": "/mosim/forward/imu",
            "lidar_frame_id": "base/mid360_link",
            "imu_frame_id": "base/forward_imu_optical_frame",
            "local_occupancy_grid": "/mosim/local_occupancy_grid",
            "local_plan": "/mosim/local_plan",
            "uav_path": "/mosim/uav_path",
            "fastlio_outputs_required_for_localization_claim": ["/cloud_registered", "/odometry", "/path"],
        },
        "run_commands_after_ros_setup": [
            "set +u; source /opt/ros/humble/setup.bash; set -u",
            f"python3 Scripts/UE5/publish_fastlio_replay_ros2.py --dataset {rel(dataset_path)} --dry-run",
            f"python3 Scripts/UE5/publish_fastlio_replay_ros2.py --dataset {rel(dataset_path)} --fps {replay_fps:g}",
            "rviz2 -d Config/rviz2/mosim_uav_fastlio_pointcloud.rviz",
            "DRY_RUN=1 Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh",
            (
                "FASTLIO_ROS2_LAUNCH_CMD='set +u; source /opt/ros/humble/setup.bash; "
                "source Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash; "
                "ros2 launch spark_fast_lio mapping_mit_campus.launch.yaml "
                "start_rviz:=false scene_id:=mosim robot_name:=base base_frame:=base map_frame:=ue_world "
                "config_path:=/mnt/c/Users/HP/Desktop/MoSim/Config/ros2/mosim_spark_fast_lio_mid360.yaml' "
                f"START_FASTLIO=1 START_RVIZ=0 FPS={replay_fps:g} MAX_FRAMES=0 LOOP=1 "
                "FASTLIO_LIDAR_TOPIC=/mosim/lidar_points "
                "FASTLIO_IMU_TOPIC=/mosim/forward/imu "
                "FASTLIO_LIDAR_FRAME=base/mid360_link "
                "FASTLIO_IMU_FRAME=base/forward_imu_optical_frame "
                f"Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh {handoff['scene_id']}"
            ),
            "Scripts/UE5/check_fastlio_ros2_topics.sh",
            (
                "python3 Scripts/UE5/record_fastlio_ros2_runtime.py "
                f"--scene-id {handoff['scene_id']} "
                f"--output-dir Results/unreal_scene_mapping/{handoff['scene_id']}/fastlio_runtime "
                "--duration-seconds 20 "
                "--odom-topic /odometry "
                "--path-topic /path "
                "--cloud-topic /cloud_registered"
            ),
            (
                "python3 Scripts/UE5/evaluate_fastlio_runtime.py "
                f"--scene-id {handoff['scene_id']} "
                f"--truth-dataset {rel(dataset_path)} "
                f"--odometry-jsonl Results/unreal_scene_mapping/{handoff['scene_id']}/fastlio_runtime/fastlio_odometry.jsonl "
                f"--output-json Results/unreal_scene_mapping/{handoff['scene_id']}/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.json "
                f"--output-md Results/unreal_scene_mapping/{handoff['scene_id']}/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.md "
                "--fail-on-threshold"
            ),
            "Optional ROS1 compatibility route for local References/Lab/localization_slam/FAST_LIO:",
            "catkin_make  # from a ROS1 workspace containing References/Lab/localization_slam/FAST_LIO as package fast_lio",
            "source devel/setup.bash",
            "roslaunch fast_lio mapping_velodyne.launch rviz:=false",
            f"python3 Scripts/UE5/publish_fastlio_replay_ros1.py --dataset {rel(dataset_path)} --dry-run",
            f"python3 Scripts/UE5/publish_fastlio_replay_ros1.py --dataset {rel(dataset_path)}",
            f"DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh {handoff['scene_id']}",
            f"Scripts/UE5/open_mapping_rviz_ros1.sh {handoff['scene_id']}",
            f"DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/run_fastlio_rviz_replay_ros1.sh {handoff['scene_id']}",
            f"Scripts/UE5/run_fastlio_rviz_replay_ros1.sh {handoff['scene_id']}",
            "Scripts/UE5/check_fastlio_ros1_topics.sh",
        ],
        "claim_boundary": [
            "This manifest is a FAST-LIO input adapter, not a completed FAST-LIO localization result.",
            "The IMU channel is synthetic finite-difference data derived from the replay path, not measured flight IMU.",
            "When available, FAST-LIO replay uses the smooth control reference and ray-casts multi-line 3D LiDAR from collision truth; this truth is used only to generate validation sensor input, not as planner global-map input.",
            "Yaw is fixed for FAST-LIO replay input when smooth control reference is used, to avoid nonphysical yaw-rate spikes from grid-path heading discontinuities.",
            "A completed FAST-LIO claim requires ROS runtime output, pose/map topics, logs, and comparison against replay truth.",
            "On Ubuntu 22.04, ROS2/RViz2 is the primary live point-cloud/map review path.",
            "Use record/evaluate tooling only after a real FAST-LIO-family runtime publishes odometry and registered-cloud output.",
            "Active point-cloud/map review must use RViz/RViz2 or an equivalent native robotics window, not browser HTML.",
            "Global scene truth remains hidden from the planner and is used only as validation oracle evidence.",
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
        "| Scene | Status | Dataset | ROS2 Replay Ready | ROS1 Compat Ready |",
        "|---|---|---|---:|",
    ]
    for manifest in manifests:
        lines.append(
            f"| `{manifest['scene_id']}` | `{manifest['status']}` | "
            f"`{manifest['generated_outputs']['fastlio_replay_dataset_jsonl']}` | "
            f"{manifest['ros_environment']['ros2_replay_ready']} | "
            f"{manifest['ros_environment']['ros1_ready']} |"
        )
    lines.extend([
        "",
        "Current primary runtime blocker if status is `blocked_missing_ros2_runtime`: source/install ROS2 Humble with RViz2 and colcon before running the publisher.",
        "The local `References/Lab/localization_slam/FAST_LIO` package is ROS1/Catkin-oriented. Treat ROS1 blockers as compatibility blockers unless an approved ROS1 bridge route is being used.",
        "Do not feed the planner global occupancy truth; FAST-LIO replay inputs come from per-frame LiDAR observations and synthetic IMU derived from the replay trajectory.",
        "Do not use browser HTML as the active point-cloud/map window; use RViz/RViz2 or an equivalent native robotics viewer.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[], help="Scene id. Default: accepted Factory and Derelict scenes.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--require-ros", action="store_true", help="Return nonzero if ROS2 replay runtime commands are missing.")
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
    if args.require_ros and any(not manifest["ros_environment"]["ros2_replay_ready"] for manifest in manifests):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
