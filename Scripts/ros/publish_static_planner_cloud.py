#!/usr/bin/env python3
"""Publish a small deterministic PointCloud2 for planner smoke gates.

This is only for PX4/EGO transport gates where the purpose is to prove the
planner-to-PX4 runtime chain. Full MID360 point-cloud evidence must come from
Gazebo/FAST-LIO gates, not from this fixture.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
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


def parse_obstacle(value: str) -> tuple[float, float, float, float, float]:
    parts = [float(item.strip()) for item in value.split(",")]
    if len(parts) == 3:
        return (parts[0], parts[1], parts[2], 0.25, 2.0)
    if len(parts) == 5:
        return (parts[0], parts[1], parts[2], parts[3], parts[4])
    raise argparse.ArgumentTypeError("obstacle must be x,y,z or x,y,z,radius,height")


def make_points(obstacles: list[tuple[float, float, float, float, float]], ground_z: float) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for x, y, z, radius, height in obstacles:
        for layer in range(8):
            pz = z + height * layer / 7.0
            for i in range(36):
                theta = 2.0 * math.pi * i / 36.0
                points.append((x + radius * math.cos(theta), y + radius * math.sin(theta), pz))
    for ix in range(-8, 9):
        for iy in range(-4, 5):
            points.append((float(ix), float(iy), ground_z))
    return points


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="/mosim/planner/global_points")
    parser.add_argument("--mirror-topic", default="/uav1/global_points")
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--rate-hz", type=float, default=5.0)
    parser.add_argument("--duration-s", type=float, default=0.0)
    parser.add_argument("--ground-z", type=float, default=-0.05)
    parser.add_argument("--obstacle", action="append", type=parse_obstacle, default=[])
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()
    ensure_ros_log_dir()
    output_json = project_path(args.output_json)
    if args.rate_hz <= 0.0:
        raise SystemExit("--rate-hz must be positive")
    if args.duration_s < 0.0:
        raise SystemExit("--duration-s must be non-negative")

    import rclpy
    from sensor_msgs.msg import PointCloud2, PointField

    obstacles = args.obstacle or [(4.0, 0.0, 0.0, 0.25, 2.0)]
    points = make_points(obstacles, args.ground_z)
    point_step = 16
    data = bytearray(len(points) * point_step)
    for index, (x, y, z) in enumerate(points):
        base = index * point_step
        struct.pack_into("<ffff", data, base, float(x), float(y), float(z), 1.0)

    rclpy.init()
    node = rclpy.create_node("mosim_static_planner_cloud_publisher")
    pub = node.create_publisher(PointCloud2, args.topic, 10)
    mirror_pub = node.create_publisher(PointCloud2, args.mirror_topic, 10) if args.mirror_topic else None
    state: dict[str, Any] = {"published": 0, "first_wall_time_s": None, "last_wall_time_s": None}

    def make_message() -> PointCloud2:
        msg = PointCloud2()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.header.frame_id = args.frame_id
        msg.height = 1
        msg.width = len(points)
        msg.fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = point_step
        msg.row_step = point_step * len(points)
        msg.data = bytes(data)
        msg.is_dense = True
        return msg

    period_s = 1.0 / args.rate_hz
    deadline = time.monotonic() + args.duration_s if args.duration_s > 0.0 else None
    next_publish = time.monotonic()
    try:
        while rclpy.ok() and (deadline is None or time.monotonic() < deadline):
            now = time.monotonic()
            if now >= next_publish:
                next_publish += period_s
                msg = make_message()
                pub.publish(msg)
                if mirror_pub is not None:
                    mirror_pub.publish(msg)
                state["published"] += 1
                if state["first_wall_time_s"] is None:
                    state["first_wall_time_s"] = now
                state["last_wall_time_s"] = now
            rclpy.spin_once(node, timeout_sec=0.02)
    finally:
        duration = 0.0
        if state["first_wall_time_s"] is not None and state["last_wall_time_s"] is not None:
            duration = max(0.0, float(state["last_wall_time_s"]) - float(state["first_wall_time_s"]))
        rate_hz = (
            (int(state["published"]) - 1) / duration
            if int(state["published"]) > 1 and duration > 0.0
            else 0.0
        )
        payload = {
            "schema": "mosim.static_planner_cloud_publisher.v1",
            "status": "ready" if int(state["published"]) > 0 else "blocked_no_publish",
            "topic": args.topic,
            "mirror_topic": args.mirror_topic,
            "frame_id": args.frame_id,
            "point_count": len(points),
            "obstacles": [list(item) for item in obstacles],
            "published_count": int(state["published"]),
            "published_rate_hz": rate_hz,
            "claim_boundary": "Planner input fixture only; not MID360, FAST-LIO, or final point-cloud evidence.",
        }
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
