#!/usr/bin/env python3
"""Convert PX4 VehicleLocalPosition to map-frame Odometry for planner input.

This bridge is intentionally narrow: it exposes PX4's fused local position to
the planner stack and does not publish setpoints, controller outputs, or Gazebo
actuator commands.
"""

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


def yaw_to_quaternion(yaw_rad: float) -> tuple[float, float, float, float]:
    half = 0.5 * yaw_rad
    return (0.0, 0.0, math.sin(half), math.cos(half))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic", required=True)
    parser.add_argument("--odom-topic", default="/mosim/planner/odom")
    parser.add_argument("--mirror-odom-topic", default="/grid_map/odom")
    parser.add_argument("--map-frame", default="map")
    parser.add_argument("--child-frame", default="px4/base_link")
    parser.add_argument("--sensor-frame", default="")
    parser.add_argument("--sensor-offset-xyz", default="0,0,0")
    parser.add_argument("--publish-tf", action="store_true")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--trace-jsonl", default="")
    parser.add_argument("--duration-s", type=float, default=0.0)
    return parser.parse_args()


def parse_xyz(value: str) -> tuple[float, float, float]:
    parts = [item.strip() for item in value.split(",")]
    if len(parts) != 3:
        raise SystemExit("--sensor-offset-xyz must contain x,y,z")
    try:
        return (float(parts[0]), float(parts[1]), float(parts[2]))
    except ValueError as exc:
        raise SystemExit(f"invalid --sensor-offset-xyz: {value}") from exc


def main() -> int:
    args = parse_args()
    ensure_ros_log_dir()
    output_json = project_path(args.output_json)
    trace_path = project_path(args.trace_jsonl) if args.trace_jsonl else None
    if args.duration_s < 0.0:
        raise SystemExit("--duration-s must be non-negative")

    import rclpy
    from nav_msgs.msg import Odometry
    from px4_msgs.msg import VehicleLocalPosition
    from geometry_msgs.msg import TransformStamped
    from tf2_ros import TransformBroadcaster

    rclpy.init()
    node = rclpy.create_node("mosim_px4_local_position_to_planner_odom")
    qos = rclpy.qos.QoSProfile(depth=100, reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT)
    odom_pub = node.create_publisher(Odometry, args.odom_topic, 10)
    mirror_pub = node.create_publisher(Odometry, args.mirror_odom_topic, 10) if args.mirror_odom_topic else None
    tf_broadcaster = TransformBroadcaster(node) if args.publish_tf else None
    sensor_offset = parse_xyz(args.sensor_offset_xyz)
    trace_handle = trace_path.open("w", encoding="utf-8") if trace_path else None

    state: dict[str, Any] = {
        "input_count": 0,
        "published_count": 0,
        "invalid_count": 0,
        "first_wall_time_s": None,
        "last_wall_time_s": None,
        "last_position_m": None,
    }

    def write_trace(payload: dict[str, Any]) -> None:
        if trace_handle is None:
            return
        trace_handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        trace_handle.flush()

    def on_position(msg: VehicleLocalPosition) -> None:
        state["input_count"] += 1
        if not (msg.xy_valid and msg.z_valid):
            state["invalid_count"] += 1
            return
        now = node.get_clock().now().to_msg()
        wall_time_s = time.monotonic()
        if state["first_wall_time_s"] is None:
            state["first_wall_time_s"] = wall_time_s
        state["last_wall_time_s"] = wall_time_s

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = args.map_frame
        odom.child_frame_id = args.child_frame
        # PX4 VehicleLocalPosition is NED: x north, y east, z down.
        # Planner stack expects ENU/map: x east, y north, z up.
        odom.pose.pose.position.x = float(msg.y)
        odom.pose.pose.position.y = float(msg.x)
        odom.pose.pose.position.z = -float(msg.z)
        yaw_enu = (math.pi / 2.0) - float(msg.heading)
        qx, qy, qz, qw = yaw_to_quaternion(yaw_enu)
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = float(msg.vy) if msg.v_xy_valid else 0.0
        odom.twist.twist.linear.y = float(msg.vx) if msg.v_xy_valid else 0.0
        odom.twist.twist.linear.z = -float(msg.vz) if msg.v_z_valid else 0.0
        odom_pub.publish(odom)
        if mirror_pub is not None:
            mirror_pub.publish(odom)
        if tf_broadcaster is not None:
            base_tf = TransformStamped()
            base_tf.header.stamp = now
            base_tf.header.frame_id = args.map_frame
            base_tf.child_frame_id = args.child_frame
            base_tf.transform.translation.x = odom.pose.pose.position.x
            base_tf.transform.translation.y = odom.pose.pose.position.y
            base_tf.transform.translation.z = odom.pose.pose.position.z
            base_tf.transform.rotation = odom.pose.pose.orientation
            tf_broadcaster.sendTransform(base_tf)
            if args.sensor_frame:
                sx, sy, sz = sensor_offset
                sensor_tf = TransformStamped()
                sensor_tf.header.stamp = now
                sensor_tf.header.frame_id = args.child_frame
                sensor_tf.child_frame_id = args.sensor_frame
                sensor_tf.transform.translation.x = sx
                sensor_tf.transform.translation.y = sy
                sensor_tf.transform.translation.z = sz
                sensor_tf.transform.rotation.w = 1.0
                tf_broadcaster.sendTransform(sensor_tf)
        state["published_count"] += 1
        state["last_position_m"] = [
            odom.pose.pose.position.x,
            odom.pose.pose.position.y,
            odom.pose.pose.position.z,
        ]
        write_trace(
            {
                "schema": "mosim.px4_planner_odom_sample.v1",
                "sequence": int(state["published_count"]),
                "frame_id": args.map_frame,
                "child_frame_id": args.child_frame,
                "position_m": state["last_position_m"],
                "velocity_mps": [
                    odom.twist.twist.linear.x,
                    odom.twist.twist.linear.y,
                    odom.twist.twist.linear.z,
                ],
            }
        )

    node.create_subscription(VehicleLocalPosition, args.input_topic, on_position, qos)
    deadline = time.monotonic() + args.duration_s if args.duration_s > 0.0 else None
    try:
        while rclpy.ok() and (deadline is None or time.monotonic() < deadline):
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        if trace_handle is not None:
            trace_handle.close()
        duration = 0.0
        if state["first_wall_time_s"] is not None and state["last_wall_time_s"] is not None:
            duration = max(0.0, float(state["last_wall_time_s"]) - float(state["first_wall_time_s"]))
        rate_hz = (
            (int(state["published_count"]) - 1) / duration
            if int(state["published_count"]) > 1 and duration > 0.0
            else 0.0
        )
        payload = {
            "schema": "mosim.px4_local_position_to_planner_odom.v1",
            "status": "ready" if int(state["published_count"]) > 0 else "blocked_no_valid_px4_local_position",
            "input_topic": args.input_topic,
            "odom_topic": args.odom_topic,
            "mirror_odom_topic": args.mirror_odom_topic,
            "map_frame": args.map_frame,
            "child_frame": args.child_frame,
            "publish_tf": bool(args.publish_tf),
            "sensor_frame": args.sensor_frame,
            "sensor_offset_xyz": list(sensor_offset),
            "counts": {
                "input": int(state["input_count"]),
                "published": int(state["published_count"]),
                "invalid": int(state["invalid_count"]),
            },
            "published_rate_hz": rate_hz,
            "last_position_m": state["last_position_m"],
            "claim_boundary": "PX4 localization-to-planner odometry bridge only; no setpoint or actuator publication.",
        }
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
