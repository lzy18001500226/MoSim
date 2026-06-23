#!/usr/bin/env python3
"""Publish a bounded EGO-style planner output from live Gazebo/ROS2 inputs.

This node is a runtime gate for the planner output surface. It consumes the
same-run planner odometry and map-frame point cloud produced by the Gazebo /
FAST-LIO input adapter, then publishes PositionCommand references. It is not a
flight controller and must not publish ControllerOutput or actuator commands.
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


def stamp_s(stamp: Any) -> float:
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


def pointcloud_bounds(message: Any, max_points: int) -> dict[str, Any]:
    offsets = {field.name: int(field.offset) for field in message.fields}
    if not {"x", "y", "z"}.issubset(offsets):
        return {"point_count": 0, "error": "missing_xyz_fields"}
    endian = ">" if message.is_bigendian else "<"
    data = bytes(message.data)
    point_step = int(message.point_step)
    total_points = min(int(message.width) * int(message.height), int(max_points))
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for index in range(total_points):
        base = index * point_step
        if base + point_step > len(data):
            break
        try:
            x = struct.unpack_from(endian + "f", data, base + offsets["x"])[0]
            y = struct.unpack_from(endian + "f", data, base + offsets["y"])[0]
            z = struct.unpack_from(endian + "f", data, base + offsets["z"])[0]
        except struct.error:
            break
        if math.isfinite(x) and math.isfinite(y) and math.isfinite(z):
            xs.append(float(x))
            ys.append(float(y))
            zs.append(float(z))
    if not xs:
        return {"point_count": 0, "error": "no_finite_xyz_points"}
    return {
        "point_count": len(xs),
        "min_xyz": [min(xs), min(ys), min(zs)],
        "max_xyz": [max(xs), max(ys), max(zs)],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--odom-topic", default="/mosim/planner/odom")
    parser.add_argument("--global-points-topic", default="/mosim/planner/global_points")
    parser.add_argument("--position-command-topic", default="/position_cmd")
    parser.add_argument("--mosim-position-command-topic", default="/mosim/planner/position_cmd")
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--trace-jsonl", required=True)
    parser.add_argument("--map-frame", default="map")
    parser.add_argument("--source-frame-alias", default="world")
    parser.add_argument("--planner-id", default="mosim_ego_style_local_goal")
    parser.add_argument("--rate-hz", type=float, default=5.0)
    parser.add_argument("--duration-s", type=float, default=8.0)
    parser.add_argument("--input-wait-s", type=float, default=45.0)
    parser.add_argument("--target-forward-m", type=float, default=2.0)
    parser.add_argument("--target-left-m", type=float, default=0.0)
    parser.add_argument("--target-altitude-m", type=float, default=1.2)
    parser.add_argument("--max-points-per-cloud", type=int, default=20000)
    parser.add_argument("--min-odom-samples", type=int, default=5)
    parser.add_argument("--min-cloud-samples", type=int, default=2)
    parser.add_argument("--min-published-commands", type=int, default=10)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_ros_log_dir()
    report_path = project_path(args.report_json)
    trace_path = project_path(args.trace_jsonl)
    if args.rate_hz <= 0.0:
        raise SystemExit("rate-hz must be positive")
    if args.duration_s <= 0.0:
        raise SystemExit("duration-s must be positive")
    if args.input_wait_s <= 0.0:
        raise SystemExit("input-wait-s must be positive")

    import rclpy
    from geometry_msgs.msg import Point, Vector3
    from mosim_msgs.msg import PositionCommand
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import PointCloud2

    rclpy.init()
    node = rclpy.create_node("mosim_ego_style_planner_output_node")
    state: dict[str, Any] = {
        "odom_count": 0,
        "cloud_count": 0,
        "published_position_cmd": 0,
        "published_mosim_position_cmd": 0,
        "last_odom": None,
        "last_cloud": None,
        "cloud_bounds": None,
        "start_monotonic_s": time.monotonic(),
        "first_publish_monotonic_s": None,
        "last_publish_monotonic_s": None,
    }

    qos = 10
    position_pub = node.create_publisher(PositionCommand, args.position_command_topic, qos)
    mosim_position_pub = node.create_publisher(PositionCommand, args.mosim_position_command_topic, qos)

    def on_odom(message: Odometry) -> None:
        state["odom_count"] += 1
        pose = message.pose.pose
        state["last_odom"] = {
            "stamp_s": stamp_s(message.header.stamp),
            "frame_id": message.header.frame_id,
            "child_frame_id": message.child_frame_id,
            "position_m": [float(pose.position.x), float(pose.position.y), float(pose.position.z)],
            "orientation_xyzw": [
                float(pose.orientation.x),
                float(pose.orientation.y),
                float(pose.orientation.z),
                float(pose.orientation.w),
            ],
        }

    def on_cloud(message: PointCloud2) -> None:
        state["cloud_count"] += 1
        bounds = pointcloud_bounds(message, args.max_points_per_cloud)
        state["last_cloud"] = {
            "stamp_s": stamp_s(message.header.stamp),
            "frame_id": message.header.frame_id,
            "width": int(message.width),
            "height": int(message.height),
        }
        state["cloud_bounds"] = bounds

    node.create_subscription(Odometry, args.odom_topic, on_odom, qos)
    node.create_subscription(PointCloud2, args.global_points_topic, on_cloud, qos)

    sequence = 0
    period_s = 1.0 / float(args.rate_hz)
    input_deadline = time.monotonic() + float(args.input_wait_s)
    publish_deadline: float | None = None
    next_publish = time.monotonic() + period_s

    try:
        while True:
            rclpy.spin_once(node, timeout_sec=0.05)
            now = time.monotonic()
            odom = state.get("last_odom")
            cloud = state.get("last_cloud")
            if publish_deadline is None:
                if isinstance(odom, dict) and isinstance(cloud, dict):
                    publish_deadline = now + float(args.duration_s)
                    next_publish = now
                elif now >= input_deadline:
                    break
                else:
                    continue
            if now >= publish_deadline:
                break
            if now < next_publish:
                continue
            next_publish += period_s
            if not isinstance(odom, dict) or not isinstance(cloud, dict):
                continue
            sequence += 1
            position = odom["position_m"]
            command = PositionCommand()
            command.header.stamp = node.get_clock().now().to_msg()
            command.header.frame_id = args.map_frame
            command.position = Point(
                x=float(position[0]) + float(args.target_forward_m),
                y=float(position[1]) + float(args.target_left_m),
                z=float(args.target_altitude_m),
            )
            command.velocity = Vector3(x=0.0, y=0.0, z=0.0)
            command.acceleration = Vector3(x=0.0, y=0.0, z=0.0)
            command.yaw = 0.0
            command.yaw_dot = 0.0
            command.kx = [1.0, 1.0, 1.0]
            command.kv = [0.2, 0.2, 0.2]
            command.trajectory_id = sequence
            command.trajectory_flag = 1
            position_pub.publish(command)
            mosim_position_pub.publish(command)
            publish_time = time.monotonic()
            if state["first_publish_monotonic_s"] is None:
                state["first_publish_monotonic_s"] = publish_time
            state["last_publish_monotonic_s"] = publish_time
            state["published_position_cmd"] += 1
            state["published_mosim_position_cmd"] += 1
            append_jsonl(
                trace_path,
                {
                    "schema": "mosim.ego_style_planner_output_sample.v1",
                    "sequence": sequence,
                    "stamp_s": stamp_s(command.header.stamp),
                    "frame_id": command.header.frame_id,
                    "position_m": [command.position.x, command.position.y, command.position.z],
                    "source_odom_position_m": position,
                    "source_cloud_frame": cloud.get("frame_id"),
                    "planner_id": args.planner_id,
                },
            )
    finally:
        duration = max(0.0, time.monotonic() - float(state["start_monotonic_s"]))
        publish_duration = 0.0
        if state["first_publish_monotonic_s"] is not None and state["last_publish_monotonic_s"] is not None:
            publish_duration = max(0.0, state["last_publish_monotonic_s"] - state["first_publish_monotonic_s"])
        output_rate = 0.0
        if state["published_position_cmd"] > 1 and publish_duration > 0.0:
            output_rate = (int(state["published_position_cmd"]) - 1) / publish_duration
        gate_passed = (
            int(state["odom_count"]) >= int(args.min_odom_samples)
            and int(state["cloud_count"]) >= int(args.min_cloud_samples)
            and int(state["published_position_cmd"]) >= int(args.min_published_commands)
            and int(state["published_mosim_position_cmd"]) >= int(args.min_published_commands)
        )
        blockers: list[str] = []
        if int(state["odom_count"]) < int(args.min_odom_samples):
            blockers.append("insufficient_planner_odom_samples")
        if int(state["cloud_count"]) < int(args.min_cloud_samples):
            blockers.append("insufficient_global_points_samples")
        if int(state["published_position_cmd"]) < int(args.min_published_commands):
            blockers.append("insufficient_position_cmd_publications")
        if int(state["published_mosim_position_cmd"]) < int(args.min_published_commands):
            blockers.append("insufficient_mosim_position_cmd_publications")
        report = {
            "schema": "mosim.ego_style_planner_output_gate.v1",
            "status": "planner_output_surface_passed" if gate_passed else "planner_output_surface_blocked",
            "gate_passed": gate_passed,
            "topics": {
                "input_odom": args.odom_topic,
                "input_global_points": args.global_points_topic,
                "position_command": args.position_command_topic,
                "mosim_position_command": args.mosim_position_command_topic,
            },
            "counts": {
                "odom": int(state["odom_count"]),
                "global_points": int(state["cloud_count"]),
                "position_cmd": int(state["published_position_cmd"]),
                "mosim_position_cmd": int(state["published_mosim_position_cmd"]),
            },
            "duration_s": duration,
            "measured_position_cmd_rate_hz": output_rate,
            "last_odom": state["last_odom"],
            "last_cloud": state["last_cloud"],
            "cloud_bounds": state["cloud_bounds"],
            "trace_jsonl": str(trace_path.relative_to(ROOT).as_posix()),
            "blockers": blockers,
            "claim_boundary": [
                "EGO-style planner output surface only.",
                "Inputs must come from same-run Gazebo/ROS2 planner odom and global point cloud topics.",
                "This node publishes PositionCommand references only.",
                "No ControllerOutput, actuator command, trajectory tracking, planner_ready, or closed_loop success is claimed.",
            ],
        }
        write_json(report_path, report)
        node.destroy_node()
        rclpy.shutdown()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if gate_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
