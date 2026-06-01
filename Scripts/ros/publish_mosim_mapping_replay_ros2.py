#!/usr/bin/env python3
"""Publish MoSim UE mapping replay artifacts to ROS2/RViz2 topics.

This is the native point-cloud/map visualization path for Ubuntu 22.04.
It opens no browser and does not claim FAST-LIO localization. Use
`--dry-run` to validate the replay contract without a sourced ROS2 runtime.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import struct
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def read_jsonl(path: Path, schema: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") != schema:
                raise ValueError(f"unsupported schema at {path}:{line_number}: {payload.get('schema')}")
            rows.append(payload)
    if not rows:
        raise ValueError(f"empty JSONL: {path}")
    return rows


def read_replay_csv(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            {key: float(value) for key, value in row.items() if value not in ("", None)}
            for row in csv.DictReader(handle)
        ]
    if not rows:
        raise ValueError(f"empty replay CSV: {path}")
    return rows


def pack_xyz_intensity(points: list[list[float]], intensity: float = 0.0) -> bytes:
    data = bytearray()
    for point in points:
        data.extend(struct.pack("<ffff", float(point[0]), float(point[1]), float(point[2]), float(intensity)))
    return bytes(data)


def local_known_points(frame: dict[str, Any]) -> tuple[list[list[float]], list[list[float]]]:
    origin = frame["origin_m"]
    grid = float(frame["grid_m"])
    free_points: list[list[float]] = []
    occupied_points: list[list[float]] = []
    for cell in frame.get("cells", []):
        offset = cell["offset"]
        point = [
            round(float(origin[0]) + float(offset[0]) * grid, 5),
            round(float(origin[1]) + float(offset[1]) * grid, 5),
            round(float(origin[2]) + float(offset[2]) * grid, 5),
        ]
        if cell.get("state") == "observed_occupied":
            occupied_points.append(point)
        else:
            free_points.append(point)
    return free_points, occupied_points


def dry_run(args: argparse.Namespace) -> int:
    replay = read_replay_csv(project_path(args.render_replay_csv))
    lidar = read_jsonl(project_path(args.lidar_point_frames_jsonl), "mosim.lidar_point_frame.v1")
    local_known = read_jsonl(project_path(args.local_known_map_jsonl), "mosim.local_known_map_frame.v1")
    local_plan = read_jsonl(project_path(args.local_plan_jsonl), "mosim.local_plan_frame.v1")
    selected = min(len(replay), len(lidar), len(local_known), len(local_plan), args.max_frames or 10**9)
    occupied = 0
    free = 0
    for frame in local_known[:selected]:
        frame_free, frame_occupied = local_known_points(frame)
        free += len(frame_free)
        occupied += len(frame_occupied)
    print(
        json.dumps(
            {
                "schema": "mosim.ros2_mapping_replay_dryrun.v1",
                "frames": selected,
                "lidar_points": sum(len(frame.get("points_m", [])) for frame in lidar[:selected]),
                "local_known_free_cells": free,
                "local_known_occupied_cells": occupied,
                "topics": {
                    "lidar": args.lidar_topic,
                    "local_known_map_cloud": args.local_known_cloud_topic,
                    "local_occupancy_grid": args.local_occupancy_topic,
                    "local_plan": args.local_plan_topic,
                    "replay_odometry": args.replay_odometry_topic,
                    "uav_path": args.uav_path_topic,
                    "tf": "/tf",
                },
                "claim": "dry-run only; no ROS2 messages were published",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def publish_ros2(args: argparse.Namespace) -> int:
    try:
        import rclpy  # type: ignore
        from builtin_interfaces.msg import Time  # type: ignore
        from geometry_msgs.msg import PoseStamped, TransformStamped  # type: ignore
        from nav_msgs.msg import OccupancyGrid, Odometry, Path as RosPath  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from sensor_msgs.msg import PointCloud2, PointField  # type: ignore
        from std_msgs.msg import Header  # type: ignore
        from tf2_ros import TransformBroadcaster  # type: ignore
    except ImportError as exc:
        print("ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    replay = read_replay_csv(project_path(args.render_replay_csv))
    lidar = read_jsonl(project_path(args.lidar_point_frames_jsonl), "mosim.lidar_point_frame.v1")
    local_known = read_jsonl(project_path(args.local_known_map_jsonl), "mosim.local_known_map_frame.v1")
    local_plan = read_jsonl(project_path(args.local_plan_jsonl), "mosim.local_plan_frame.v1")
    frame_count = min(len(replay), len(lidar), len(local_known), len(local_plan))
    if args.max_frames > 0:
        frame_count = min(frame_count, args.max_frames)

    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    rclpy.init()
    node = rclpy.create_node("mosim_mapping_replay_publisher")
    tf_broadcaster = TransformBroadcaster(node)
    lidar_pub = node.create_publisher(PointCloud2, args.lidar_topic, qos)
    known_pub = node.create_publisher(PointCloud2, args.local_known_cloud_topic, qos)
    occ_pub = node.create_publisher(OccupancyGrid, args.local_occupancy_topic, qos)
    plan_pub = node.create_publisher(RosPath, args.local_plan_topic, qos)
    replay_odom_pub = node.create_publisher(Odometry, args.replay_odometry_topic, qos)
    uav_path_pub = node.create_publisher(RosPath, args.uav_path_topic, qos)
    uav_path = RosPath()
    uav_path.header.frame_id = args.world_frame

    def stamp_from_seconds(seconds: float) -> Any:
        msg = Time()
        whole = math.floor(seconds)
        msg.sec = int(whole)
        msg.nanosec = int(round((seconds - whole) * 1_000_000_000))
        if msg.nanosec >= 1_000_000_000:
            msg.sec += 1
            msg.nanosec -= 1_000_000_000
        return msg

    def current_stamp(row: dict[str, float], index: int) -> Any:
        if args.wall_time:
            return node.get_clock().now().to_msg()
        return stamp_from_seconds(float(row.get("time", index / args.fps)))

    def make_header(stamp: Any, frame_id: str) -> Any:
        return Header(stamp=stamp, frame_id=frame_id)

    def make_cloud(points: list[list[float]], stamp: Any, frame_id: str, intensity: float) -> Any:
        msg = PointCloud2()
        msg.header = make_header(stamp, frame_id)
        msg.height = 1
        msg.width = len(points)
        msg.fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 16
        msg.row_step = msg.point_step * msg.width
        msg.data = pack_xyz_intensity(points, intensity=intensity)
        msg.is_dense = True
        return msg

    def make_pose(row: dict[str, float], stamp: Any) -> Any:
        pose = PoseStamped()
        pose.header = make_header(stamp, args.world_frame)
        pose.pose.position.x = row.get("x", 0.0)
        pose.pose.position.y = row.get("y", 0.0)
        pose.pose.position.z = row.get("z", 0.0)
        yaw = row.get("yaw", 0.0)
        pose.pose.orientation.z = math.sin(yaw * 0.5)
        pose.pose.orientation.w = math.cos(yaw * 0.5)
        return pose

    def make_replay_odometry(row: dict[str, float], stamp: Any) -> Any:
        odom = Odometry()
        odom.header = make_header(stamp, args.world_frame)
        odom.child_frame_id = args.body_frame
        odom.pose.pose = make_pose(row, stamp).pose
        return odom

    def publish_tf(row: dict[str, float], stamp: Any) -> None:
        transform = TransformStamped()
        transform.header = make_header(stamp, args.world_frame)
        transform.child_frame_id = args.body_frame
        transform.transform.translation.x = row.get("x", 0.0)
        transform.transform.translation.y = row.get("y", 0.0)
        transform.transform.translation.z = row.get("z", 0.0)
        yaw = row.get("yaw", 0.0)
        transform.transform.rotation.z = math.sin(yaw * 0.5)
        transform.transform.rotation.w = math.cos(yaw * 0.5)
        tf_broadcaster.sendTransform(transform)

    def make_plan(points: list[list[float]], stamp: Any) -> Any:
        path = RosPath()
        path.header = make_header(stamp, args.world_frame)
        for point in points:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = float(point[0])
            pose.pose.position.y = float(point[1])
            pose.pose.position.z = float(point[2])
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        return path

    def make_occupancy(frame: dict[str, Any], stamp: Any) -> Any:
        cells = frame.get("cells", [])
        if not cells:
            raise ValueError("local-known-map frame has no cells")
        offsets = [cell["offset"] for cell in cells]
        min_x = min(int(offset[0]) for offset in offsets)
        max_x = max(int(offset[0]) for offset in offsets)
        min_y = min(int(offset[1]) for offset in offsets)
        max_y = max(int(offset[1]) for offset in offsets)
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        data = [-1] * (width * height)
        for cell in cells:
            offset = cell["offset"]
            x = int(offset[0]) - min_x
            y = int(offset[1]) - min_y
            data[y * width + x] = 100 if cell.get("state") == "observed_occupied" else 0
        origin = frame["origin_m"]
        resolution = float(frame["grid_m"])
        msg = OccupancyGrid()
        msg.header = make_header(stamp, args.world_frame)
        msg.info.resolution = resolution
        msg.info.width = width
        msg.info.height = height
        msg.info.origin.position.x = float(origin[0]) + min_x * resolution
        msg.info.origin.position.y = float(origin[1]) + min_y * resolution
        msg.info.origin.position.z = 0.0
        msg.info.origin.orientation.w = 1.0
        msg.data = data
        return msg

    period_s = 1.0 / args.fps
    try:
        while rclpy.ok():
            for index in range(frame_count):
                if not rclpy.ok():
                    break
                row = replay[index]
                stamp = current_stamp(row, index)
                publish_tf(row, stamp)
                uav_path.header.stamp = stamp
                uav_path.poses.append(make_pose(row, stamp))
                lidar_pub.publish(make_cloud(lidar[index].get("points_m", []), stamp, args.world_frame, intensity=50.0))
                free_points, occupied_points = local_known_points(local_known[index])
                known_pub.publish(make_cloud(free_points + occupied_points, stamp, args.world_frame, intensity=80.0))
                occ_pub.publish(make_occupancy(local_known[index], stamp))
                plan_pub.publish(make_plan(local_plan[index].get("points_m", []), stamp))
                replay_odom_pub.publish(make_replay_odometry(row, stamp))
                uav_path_pub.publish(uav_path)
                rclpy.spin_once(node, timeout_sec=0.0)
                time.sleep(period_s)
            if not args.loop:
                break
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-replay-csv", type=Path, required=True)
    parser.add_argument("--local-known-map-jsonl", type=Path, required=True)
    parser.add_argument("--local-plan-jsonl", type=Path, required=True)
    parser.add_argument("--lidar-point-frames-jsonl", type=Path, required=True)
    parser.add_argument("--world-frame", default="ue_world")
    parser.add_argument("--body-frame", default="base_link")
    parser.add_argument("--lidar-topic", default="/velodyne_points")
    parser.add_argument("--local-known-cloud-topic", default="/mosim/local_known_map_cloud")
    parser.add_argument("--local-occupancy-topic", default="/mosim/local_occupancy_grid")
    parser.add_argument("--local-plan-topic", default="/mosim/local_plan")
    parser.add_argument("--replay-odometry-topic", default="/mosim/replay_odometry")
    parser.add_argument("--uav-path-topic", default="/mosim/uav_path")
    parser.add_argument("--fps", type=float, default=10.0)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--wall-time", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.fps <= 0:
        raise ValueError("--fps must be positive")
    if args.dry_run:
        return dry_run(args)
    return publish_ros2(args)


if __name__ == "__main__":
    raise SystemExit(main())
