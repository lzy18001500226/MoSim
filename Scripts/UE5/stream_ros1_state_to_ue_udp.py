#!/usr/bin/env python3
"""Stream live ROS1 controller state to the UE display bridge over UDP.

This is a one-way display sidecar. It subscribes to the active Gazebo/PX4/
MAVROS/px4ctrl ROS graph and sends actual pose plus the recent PositionCommand
trail to Unreal. It must not publish ROS setpoints or feed UE state back into
the controller, planner, estimator, or Gazebo.
"""

from __future__ import annotations

import argparse
import json
import math
import socket
import sys
import threading
import time
from collections import deque
from typing import Any


def quat_to_rpy(x: float, y: float, z: float, w: float) -> list[float]:
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)
    else:
        pitch = math.asin(sinp)

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return [roll, pitch, yaw]


def vector3(obj: Any) -> list[float]:
    return [float(obj.x), float(obj.y), float(obj.z)]


def finite_vector(values: list[float]) -> list[float]:
    out: list[float] = []
    for value in values:
        value = float(value)
        out.append(value if math.isfinite(value) else 0.0)
    return out


class Ros1ToUeStreamer:
    def __init__(self, args: argparse.Namespace) -> None:
        import rospy
        from gazebo_msgs.msg import LinkStates
        from mavros_msgs.msg import State
        from nav_msgs.msg import Odometry
        from quadrotor_msgs.msg import PositionCommand

        self.rospy = rospy
        self.args = args
        self.sequence = 0
        self.lock = threading.Lock()
        self.latest_state: dict[str, Any] | None = None
        self.latest_cmd: dict[str, Any] | None = None
        self.latest_motors: list[float] | None = None
        self.latest_motors_monotonic = 0.0
        self.source_updates_since_report = 0
        self.armed: bool | None = None
        self.last_reported_motor_source = ""
        self.actual_trail: deque[list[float]] = deque(maxlen=max(2, args.max_trail_points))
        self.cmd_trail: deque[list[float]] = deque(maxlen=max(2, args.max_cmd_points))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=args.queue_size)
        rospy.Subscriber(args.position_cmd_topic, PositionCommand, self.on_position_cmd, queue_size=args.queue_size)
        rospy.Subscriber(args.link_states_topic, LinkStates, self.on_link_states, queue_size=1)
        rospy.Subscriber(args.mavros_state_topic, State, self.on_mavros_state, queue_size=args.queue_size)
        rospy.loginfo(
            "MoSim UE live streamer subscribed odom=%s position_cmd=%s link_states=%s mavros_state=%s udp=%s:%d rate=%.1fHz",
            args.odom_topic,
            args.position_cmd_topic,
            args.link_states_topic,
            args.mavros_state_topic,
            args.host,
            args.port,
            args.rate_hz,
        )

    def on_odom(self, msg: Any) -> None:
        q = msg.pose.pose.orientation
        position = vector3(msg.pose.pose.position)
        rpy = quat_to_rpy(float(q.x), float(q.y), float(q.z), float(q.w))
        velocity = vector3(msg.twist.twist.linear)
        with self.lock:
            self.latest_state = {
                "position": finite_vector(position),
                "rpy": finite_vector(rpy),
                "velocity": finite_vector(velocity),
                "stamp": msg.header.stamp.to_sec() if msg.header.stamp else self.rospy.Time.now().to_sec(),
            }
            self.source_updates_since_report += 1
            if not self.actual_trail or self.distance(self.actual_trail[-1], position) >= self.args.trail_min_distance_m:
                self.actual_trail.append(finite_vector(position))

    def on_position_cmd(self, msg: Any) -> None:
        position = vector3(msg.position)
        velocity = vector3(msg.velocity) if hasattr(msg, "velocity") else [0.0, 0.0, 0.0]
        yaw = float(getattr(msg, "yaw", 0.0))
        with self.lock:
            self.latest_cmd = {
                "position": finite_vector(position),
                "velocity": finite_vector(velocity),
                "yaw": yaw if math.isfinite(yaw) else 0.0,
                "stamp": msg.header.stamp.to_sec() if getattr(msg, "header", None) else self.rospy.Time.now().to_sec(),
            }
            if not self.cmd_trail or self.distance(self.cmd_trail[-1], position) >= self.args.cmd_min_distance_m:
                self.cmd_trail.append(finite_vector(position))

    def on_mavros_state(self, msg: Any) -> None:
        with self.lock:
            self.armed = bool(msg.armed)

    def on_link_states(self, msg: Any) -> None:
        name_to_index = {name: index for index, name in enumerate(msg.name)}
        rotor_indices: list[int] = []
        rotor_prefix = ""
        for rotor_name in self.args.rotor_link_names:
            suffix = "::" + rotor_name
            matches = [(name, index) for name, index in name_to_index.items() if name == rotor_name or name.endswith(suffix)]
            if len(matches) != 1:
                return
            matched_name, matched_index = matches[0]
            rotor_indices.append(matched_index)
            if not rotor_prefix and matched_name.endswith(suffix):
                rotor_prefix = matched_name[: -len(suffix)]

        base_angular = [0.0, 0.0, 0.0]
        if rotor_prefix:
            base_index = name_to_index.get(rotor_prefix + "::" + self.args.base_link_name)
            if base_index is not None:
                base = msg.twist[base_index].angular
                base_angular = [float(base.x), float(base.y), float(base.z)]

        motors: list[float] = []
        for index in rotor_indices:
            angular = msg.twist[index].angular
            relative = [
                float(angular.x) - base_angular[0],
                float(angular.y) - base_angular[1],
                float(angular.z) - base_angular[2],
            ]
            motors.append(math.sqrt(sum(value * value for value in relative)))
        with self.lock:
            self.latest_motors = finite_vector(motors)
            self.latest_motors_monotonic = time.monotonic()

    def motor_visual_state(self) -> tuple[list[float], str]:
        with self.lock:
            motors = list(self.latest_motors) if self.latest_motors is not None else None
            motor_age = time.monotonic() - self.latest_motors_monotonic
            armed = self.armed
        if motors is not None and motor_age <= self.args.motor_timeout_s:
            return motors, "gazebo_link_states"
        if armed is True:
            return [self.args.armed_visual_motor_command] * 4, "mavros_armed_visual_fallback"
        if armed is False:
            return [0.0] * 4, "mavros_disarmed_visual_fallback"
        return [], "unavailable"

    @staticmethod
    def distance(a: list[float], b: list[float]) -> float:
        return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))

    def make_frame(self) -> dict[str, Any] | None:
        with self.lock:
            if self.latest_state is None:
                return None
            state = dict(self.latest_state)
            cmd = dict(self.latest_cmd) if self.latest_cmd is not None else None
            cmd_trail = list(self.cmd_trail) if self.args.include_local_plan else []

        position = state["position"]
        reference = cmd["position"] if cmd else position
        yaw = state["rpy"][2]
        motor_command, motor_source = self.motor_visual_state()
        frame = {
            "schema": "quadrotor.unreal_state.v1",
            "type": "frame",
            "scene_id": self.args.scene_id,
            "map_id": self.args.map_id,
            "seq": self.sequence,
            "t": state["stamp"],
            "units": {"position": "m", "angle": "rad", "time": "s"},
            "coordinate_policy": self.args.coordinate_policy,
            "uav": {
                "id": self.args.vehicle_id,
                "position_m": position,
                "rpy_rad": state["rpy"],
                "motor_command": motor_command,
            },
            "reference": {"position_m": reference},
            "mission": {
                "start_m": list(self.actual_trail[0]) if self.actual_trail else position,
                "goal_m": reference,
                "current_goal_m": reference,
            },
            "perception": {
                "radar_origin_m": position,
                "yaw_rad": yaw,
                "near_radius_m": 0.0,
                "far_radius_m": 0.0,
                "fov_deg": 0.0,
            },
            "local_known_map": {
                "schema": "quadrotor.local_known_map.v1",
                "origin_m": position,
                "grid_m": 0.5,
                "radius_m": 0.0,
                "cells": [],
                "render_only": True,
                "evidence_backed": False,
            },
            "lidar_points": {
                "schema": "quadrotor.lidar_points.v1",
                "coordinate_frame": self.args.coordinate_policy,
                "points_m": [],
                "render_only": True,
                "evidence_backed": False,
                "source": "disabled_for_live_controller_pose_review",
            },
            "local_plan": {
                "source": self.args.position_cmd_topic if self.args.include_local_plan else "disabled",
                "points_m": cmd_trail,
                "render_only": False,
                "evidence_backed": self.args.include_local_plan,
                "valid": bool(cmd_trail),
            },
            "status": {
                "controller_mode": self.args.controller_profile,
                "planner_state": self.args.planner_profile,
                "safety_state": "live_display_only",
                "evidence_level": "live_ros1_gazebo_px4_mavros_px4ctrl_state_mirror",
                "rotor_visual_source": motor_source,
                "rotor_visual_only": True,
                "notes": "red actual pose trail only; local plan hidden; rotor animation is display only",
            },
            "overlays": {
                "scene_label": self.args.scene_id,
                "map_label": self.args.map_id,
                "quality_flags": [
                    "live_ros1_state",
                    "no_ue_feedback",
                    "not_synthetic_replay",
                    "rotor_visual_" + motor_source,
                ],
            },
        }
        self.sequence += 1
        return frame

    def encode_frame(self, frame: dict[str, Any]) -> tuple[bytes, int, int]:
        points = frame["local_plan"]["points_m"]
        original_count = len(points)
        data = json.dumps(frame, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        while len(data) > self.args.max_datagram_bytes and len(points) > 2:
            reduced = points[::2]
            if reduced[-1] != points[-1]:
                reduced.append(points[-1])
            points = reduced
            frame["local_plan"]["points_m"] = points
            data = json.dumps(frame, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(data) > self.args.max_datagram_bytes:
            frame["local_plan"]["points_m"] = []
            frame["local_plan"]["valid"] = False
            data = json.dumps(frame, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return data, original_count, len(frame["local_plan"]["points_m"])

    def spin(self) -> None:
        period_s = 1.0 / self.args.rate_hz
        next_send_monotonic = time.monotonic()
        wait_logged = False
        report_started = time.monotonic()
        report_frames = 0
        report_bytes = 0
        while not self.rospy.is_shutdown():
            frame = self.make_frame()
            if frame is None:
                if not wait_logged:
                    self.rospy.logwarn("Waiting for first odom sample on %s", self.args.odom_topic)
                    wait_logged = True
                time.sleep(period_s)
                next_send_monotonic = time.monotonic()
                continue
            data, original_plan_points, sent_plan_points = self.encode_frame(frame)
            if sent_plan_points != original_plan_points:
                self.rospy.logwarn_throttle(
                    5.0,
                    "MoSim UE live streamer decimated local plan from %d to %d points to keep UDP payload at %d bytes",
                    original_plan_points,
                    sent_plan_points,
                    len(data),
                )
            try:
                self.sock.sendto(data, (self.args.host, self.args.port))
            except OSError as exc:
                self.rospy.logerr_throttle(5.0, "MoSim UE UDP send failed without stopping streamer: %s", exc)
            report_frames += 1
            report_bytes += len(data)
            motor_source = str(frame["status"]["rotor_visual_source"])
            if motor_source != self.last_reported_motor_source:
                self.rospy.loginfo(
                    "MoSim UE rotor visual source=%s motor_command=%s",
                    motor_source,
                    frame["uav"]["motor_command"],
                )
                self.last_reported_motor_source = motor_source
            report_elapsed = time.monotonic() - report_started
            if report_elapsed >= 5.0:
                with self.lock:
                    source_updates = self.source_updates_since_report
                    self.source_updates_since_report = 0
                self.rospy.loginfo(
                    "MoSim UE live streamer wall_send_rate=%.1fHz target=%.1fHz source_pose_rate=%.1fHz avg_payload_bytes=%.0f rotor_source=%s motor_command=%s",
                    report_frames / report_elapsed,
                    self.args.rate_hz,
                    source_updates / report_elapsed,
                    report_bytes / max(1, report_frames),
                    motor_source,
                    frame["uav"]["motor_command"],
                )
                report_started = time.monotonic()
                report_frames = 0
                report_bytes = 0

            next_send_monotonic += period_s
            remaining_s = next_send_monotonic - time.monotonic()
            if remaining_s > 0.0:
                time.sleep(remaining_s)
            elif remaining_s < -4.0 * period_s:
                next_send_monotonic = time.monotonic()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--odom-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--position-cmd-topic", default="/position_cmd")
    parser.add_argument("--link-states-topic", default="/gazebo/link_states")
    parser.add_argument("--mavros-state-topic", default="/uav1/mavros/state")
    parser.add_argument("--base-link-name", default="base_link")
    parser.add_argument("--rotor-link-names", default="rotor_0,rotor_1,rotor_2,rotor_3")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--rate-hz", type=float, default=100.0)
    parser.add_argument("--max-datagram-bytes", type=int, default=60000)
    parser.add_argument("--motor-timeout-s", type=float, default=0.5)
    parser.add_argument("--armed-visual-motor-command", type=float, default=0.65)
    parser.add_argument("--queue-size", type=int, default=50)
    parser.add_argument("--vehicle-id", default="uav1")
    parser.add_argument("--scene-id", default="factory")
    parser.add_argument("--map-id", default="local_factoryenvironmentcollect")
    parser.add_argument("--controller-profile", default="px4ctrl")
    parser.add_argument("--planner-profile", default="diff_interactive")
    parser.add_argument("--coordinate-policy", default="mworks_world_m_z_up", choices=["mworks_world_m_z_up", "ue_world_m_z_up"])
    parser.add_argument("--max-trail-points", type=int, default=1200)
    parser.add_argument("--max-cmd-points", type=int, default=400)
    parser.add_argument("--trail-min-distance-m", type=float, default=0.02)
    parser.add_argument("--cmd-min-distance-m", type=float, default=0.02)
    parser.add_argument(
        "--include-local-plan",
        action="store_true",
        help="Include the recent PositionCommand trail in UE frames; disabled by default for actual-flight-only review.",
    )
    args = parser.parse_args(argv)
    args.rotor_link_names = [name.strip() for name in args.rotor_link_names.split(",") if name.strip()]
    if len(args.rotor_link_names) != 4:
        parser.error("--rotor-link-names must contain exactly four comma-separated link names")
    if args.rate_hz <= 0.0:
        parser.error("--rate-hz must be positive")
    if args.max_datagram_bytes < 1024 or args.max_datagram_bytes > 65507:
        parser.error("--max-datagram-bytes must be between 1024 and 65507")
    return args


def main(argv: list[str]) -> int:
    try:
        import rospy

        args = parse_args(argv)
        rospy.init_node("mosim_ros1_to_ue_live_streamer", anonymous=True)
        Ros1ToUeStreamer(args).spin()
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
