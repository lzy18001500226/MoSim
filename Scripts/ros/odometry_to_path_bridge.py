#!/usr/bin/env python3
"""Publish review-only nav_msgs/Path from odometry or PX4 local position."""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROS_LOG_DIR = ROOT / "Results" / "tmp" / "ros_logs"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def ensure_ros_log_dir() -> None:
    log_dir = Path(os.environ.get("ROS_LOG_DIR", str(DEFAULT_ROS_LOG_DIR)))
    resolved = project_path(log_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    os.environ["ROS_LOG_DIR"] = str(resolved)


def yaw_to_quat(yaw: float) -> tuple[float, float, float, float]:
    half = 0.5 * yaw
    return (0.0, 0.0, math.sin(half), math.cos(half))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["nav_odom", "px4_local_position"], required=True)
    parser.add_argument("--input-topic", required=True)
    parser.add_argument("--path-topic", required=True)
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--max-poses", type=int, default=4000)
    parser.add_argument("--publish-rate-hz", type=float, default=10.0)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--duration-s", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_ros_log_dir()
    output_json = project_path(args.output_json)
    if args.max_poses <= 0:
        raise SystemExit("--max-poses must be positive")
    if args.publish_rate_hz <= 0.0:
        raise SystemExit("--publish-rate-hz must be positive")

    import rclpy
    from geometry_msgs.msg import PoseStamped
    from nav_msgs.msg import Odometry, Path as NavPath
    from px4_msgs.msg import VehicleLocalPosition

    rclpy.init()
    node = rclpy.create_node("mosim_odometry_to_path_bridge")
    path_pub = node.create_publisher(NavPath, args.path_topic, 10)
    path_msg = NavPath()
    path_msg.header.frame_id = args.frame_id
    state: dict[str, Any] = {
        "input_count": 0,
        "published_count": 0,
        "invalid_count": 0,
        "first_wall_time_s": None,
        "last_wall_time_s": None,
        "last_position_m": None,
    }

    def append_pose(x: float, y: float, z: float, yaw: float) -> None:
        now_msg = node.get_clock().now().to_msg()
        pose = PoseStamped()
        pose.header.stamp = now_msg
        pose.header.frame_id = args.frame_id
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        qx, qy, qz, qw = yaw_to_quat(yaw)
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw
        path_msg.header.stamp = now_msg
        path_msg.poses.append(pose)
        if len(path_msg.poses) > args.max_poses:
            del path_msg.poses[: len(path_msg.poses) - args.max_poses]
        state["last_position_m"] = [x, y, z]

    def on_nav_odom(msg: Odometry) -> None:
        state["input_count"] += 1
        wall_time_s = time.monotonic()
        if state["first_wall_time_s"] is None:
            state["first_wall_time_s"] = wall_time_s
        state["last_wall_time_s"] = wall_time_s
        append_pose(
            float(msg.pose.pose.position.x),
            float(msg.pose.pose.position.y),
            float(msg.pose.pose.position.z),
            0.0,
        )

    def on_px4_local_position(msg: VehicleLocalPosition) -> None:
        state["input_count"] += 1
        if not (msg.xy_valid and msg.z_valid):
            state["invalid_count"] += 1
            return
        wall_time_s = time.monotonic()
        if state["first_wall_time_s"] is None:
            state["first_wall_time_s"] = wall_time_s
        state["last_wall_time_s"] = wall_time_s
        append_pose(float(msg.y), float(msg.x), -float(msg.z), (math.pi / 2.0) - float(msg.heading))

    qos = rclpy.qos.QoSProfile(depth=100, reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT)
    if args.mode == "nav_odom":
        node.create_subscription(Odometry, args.input_topic, on_nav_odom, qos)
    else:
        node.create_subscription(VehicleLocalPosition, args.input_topic, on_px4_local_position, qos)

    period = 1.0 / args.publish_rate_hz
    next_publish = time.monotonic()
    deadline = time.monotonic() + args.duration_s if args.duration_s > 0.0 else None
    try:
        while rclpy.ok() and (deadline is None or time.monotonic() < deadline):
            rclpy.spin_once(node, timeout_sec=0.02)
            now = time.monotonic()
            if now >= next_publish:
                path_pub.publish(path_msg)
                state["published_count"] += 1
                next_publish = now + period
    finally:
        duration = 0.0
        if state["first_wall_time_s"] is not None and state["last_wall_time_s"] is not None:
            duration = max(0.0, float(state["last_wall_time_s"]) - float(state["first_wall_time_s"]))
        payload = {
            "schema": "mosim.odometry_to_path_bridge.v1",
            "status": "ready" if state["input_count"] > 0 else "blocked_no_input",
            "mode": args.mode,
            "input_topic": args.input_topic,
            "path_topic": args.path_topic,
            "frame_id": args.frame_id,
            "counts": {
                "input": int(state["input_count"]),
                "invalid": int(state["invalid_count"]),
                "path_published": int(state["published_count"]),
                "path_poses": len(path_msg.poses),
            },
            "input_rate_hz": ((int(state["input_count"]) - 1) / duration) if int(state["input_count"]) > 1 and duration > 0.0 else 0.0,
            "last_position_m": state["last_position_m"],
            "claim_boundary": "RViz review path only; this node does not publish control commands.",
        }
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
