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
import os
from pathlib import Path
import socket
import sys
import threading
import time
from collections import deque
from typing import Any


IPV4_UDP_HEADER_BYTES = 28
TIMING_CLOCK = "unix_epoch_ns"


def latency_summary_ms(samples: list[float]) -> dict[str, float | int]:
    """Return bounded-window latency percentiles without retaining raw samples."""

    if not samples:
        return {"sample_count": 0, "p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "max_ms": 0.0}
    ordered = sorted(float(value) for value in samples)

    def percentile(percent: float) -> float:
        index = (len(ordered) - 1) * percent / 100.0
        lower = int(math.floor(index))
        upper = int(math.ceil(index))
        if lower == upper:
            return ordered[lower]
        return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)

    return {
        "sample_count": len(ordered),
        "p50_ms": percentile(50.0),
        "p95_ms": percentile(95.0),
        "p99_ms": percentile(99.0),
        "max_ms": ordered[-1],
    }


def source_sample_is_fresh(
    received_monotonic: float,
    timeout_s: float,
    *,
    now_monotonic: float | None = None,
) -> bool:
    """Reject callbacks that waited in-process long enough to be stale."""

    if timeout_s <= 0.0:
        return False
    now = time.monotonic() if now_monotonic is None else now_monotonic
    age_s = now - received_monotonic
    return 0.0 <= age_s <= timeout_s


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def transport_metrics(
    *,
    run_id: str,
    stream_id: str,
    host: str,
    port: int,
    elapsed_s: float,
    sent_frames: int,
    sent_payload_bytes: int,
    send_error_count: int,
    source_updates: int,
    source_age_ms: float,
    source_timeout_s: float,
    source_to_udp_send_samples_ms: list[float],
    stale_odom_callback_drops: int,
    source_to_receiver_clock_offset_ns: int | None,
) -> dict[str, Any]:
    elapsed_s = max(elapsed_s, 1e-9)
    wire_bytes = sent_payload_bytes + sent_frames * IPV4_UDP_HEADER_BYTES
    return {
        "schema": "mosim.gazebo_ue_sender_metrics.v1",
        "run_id": run_id,
        "stream_id": stream_id,
        "link_id": "gazebo_ue_display",
        "destination": f"{host}:{port}",
        "measurement_point": "ros1_udp_sender",
        "window_s": elapsed_s,
        "source_update_rate_hz": source_updates / elapsed_s,
        "send_rate_hz": sent_frames / elapsed_s,
        "sent_frames": sent_frames,
        "send_error_count": send_error_count,
        "avg_payload_bytes": sent_payload_bytes / max(1, sent_frames),
        "payload_bytes_per_s": sent_payload_bytes / elapsed_s,
        "estimated_ipv4_udp_wire_bytes_per_s": wire_bytes / elapsed_s,
        "source_pose_age_ms": source_age_ms,
        "source_freshness": {
            "timeout_s": source_timeout_s,
            "stale_callback_drop_count": stale_odom_callback_drops,
            "policy": "queued ROS callbacks older than source_timeout_s are dropped before display",
        },
        "source_to_udp_send_latency_ms": latency_summary_ms(source_to_udp_send_samples_ms),
        "timing_clock": TIMING_CLOCK,
        "source_to_receiver_clock_offset_ns": source_to_receiver_clock_offset_ns,
        "cross_host_clock_calibration": (
            "wsl_windows_stdout_bracket_midpoint_v2" if source_to_receiver_clock_offset_ns is not None else "unavailable"
        ),
        "receiver_metrics_available": False,
        "unavailable_metrics": ["receive_rate_hz", "receiver_drop_rate", "rtt_ms", "ue_fps"],
        "claim_boundary": "Sender-side measurement only. Source-to-UDP-send latency ends before socket delivery; one-way UDP cannot prove UE receive rate, receiver loss, RTT, actor application, or render FPS.",
        "updated_at_unix": time.time(),
    }


class UdpPortLease:
    """Prevent two project bridge processes from sending to one UE UDP port."""

    def __init__(self, lease_dir: str, host: str, port: int, owner_id: str) -> None:
        import fcntl

        safe_host = "".join(ch if ch.isalnum() or ch in ".-_" else "_" for ch in host)
        path = Path(lease_dir) / f"{safe_host}_{port}.lock"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.handle.seek(0)
            current = self.handle.read().strip() or "unknown owner"
            self.handle.close()
            raise RuntimeError(f"UE UDP bridge lease busy for {host}:{port}: {current}") from exc
        self.handle.seek(0)
        self.handle.truncate()
        json.dump({"pid": os.getpid(), "owner_id": owner_id, "host": host, "port": port}, self.handle)
        self.handle.flush()


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
        self.port_lease = UdpPortLease(args.lease_dir, args.host, args.port, args.stream_id)
        self.sequence = 0
        self.lock = threading.Lock()
        self.latest_state: dict[str, Any] | None = None
        self.latest_state_monotonic = 0.0
        self.latest_cmd: dict[str, Any] | None = None
        self.latest_motors: list[float] | None = None
        self.latest_motors_monotonic = 0.0
        self.source_updates_since_report = 0
        self.stale_odom_callback_drops_since_report = 0
        self.armed: bool | None = None
        self.last_reported_motor_source = ""
        self.send_error_count = 0
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
        received_monotonic = time.monotonic()
        received_unix_ns = time.time_ns()
        q = msg.pose.pose.orientation
        position = vector3(msg.pose.pose.position)
        rpy = quat_to_rpy(float(q.x), float(q.y), float(q.z), float(q.w))
        velocity = vector3(msg.twist.twist.linear)
        if not source_sample_is_fresh(received_monotonic, self.args.source_timeout_s):
            with self.lock:
                self.stale_odom_callback_drops_since_report += 1
            self.rospy.logwarn_throttle(
                5.0,
                "Dropping queued stale odom callback before UE display; age exceeded %.3fs",
                self.args.source_timeout_s,
            )
            return
        with self.lock:
            self.latest_state = {
                "position": finite_vector(position),
                "rpy": finite_vector(rpy),
                "velocity": finite_vector(velocity),
                "stamp": msg.header.stamp.to_sec() if msg.header.stamp else self.rospy.Time.now().to_sec(),
                "received_unix_ns": received_unix_ns,
            }
            self.latest_state_monotonic = received_monotonic
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
        if armed is False:
            return [0.0] * 4, "mavros_disarmed"
        if motors is not None and motor_age <= self.args.motor_timeout_s:
            return motors, "gazebo_link_states"
        if armed is True:
            return [self.args.armed_visual_motor_command] * 4, "mavros_armed_visual_fallback"
        return [], "unavailable"

    @staticmethod
    def distance(a: list[float], b: list[float]) -> float:
        return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))

    def make_frame(self) -> dict[str, Any] | None:
        with self.lock:
            if self.latest_state is None:
                return None
            if time.monotonic() - self.latest_state_monotonic > self.args.source_timeout_s:
                return None
            state = dict(self.latest_state)
            cmd = dict(self.latest_cmd) if self.latest_cmd is not None else None
            cmd_trail = list(self.cmd_trail) if self.args.include_local_plan else []

        position = state["position"]
        reference = cmd["position"] if cmd else position
        yaw = state["rpy"][2]
        motor_command, motor_source = self.motor_visual_state()
        timing = {
            "clock": TIMING_CLOCK,
            "source_received_unix_ns": str(state["received_unix_ns"]),
            "udp_sent_unix_ns": "",
        }
        if self.args.source_to_receiver_clock_offset_ns is not None:
            timing["source_to_receiver_clock_offset_ns"] = str(self.args.source_to_receiver_clock_offset_ns)
        frame = {
            "schema": "quadrotor.unreal_state.v1",
            "type": "frame",
            "scene_id": self.args.scene_id,
            "map_id": self.args.map_id,
            "run_id": self.args.run_id,
            "stream_id": self.args.stream_id,
            "seq": self.sequence,
            "t": state["stamp"],
            "units": {"position": "m", "angle": "rad", "time": "s"},
            "timing": timing,
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

        def serialize_for_send() -> bytes:
            frame["timing"]["udp_sent_unix_ns"] = str(time.time_ns())
            return json.dumps(frame, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        data = serialize_for_send()
        while len(data) > self.args.max_datagram_bytes and len(points) > 2:
            reduced = points[::2]
            if reduced[-1] != points[-1]:
                reduced.append(points[-1])
            points = reduced
            frame["local_plan"]["points_m"] = points
            data = serialize_for_send()
        if len(data) > self.args.max_datagram_bytes:
            frame["local_plan"]["points_m"] = []
            frame["local_plan"]["valid"] = False
            data = serialize_for_send()
        return data, original_count, len(frame["local_plan"]["points_m"])

    def spin(self) -> None:
        period_s = 1.0 / self.args.rate_hz
        next_send_monotonic = time.monotonic()
        wait_logged = False
        report_started = time.monotonic()
        report_frames = 0
        report_bytes = 0
        report_send_errors = 0
        report_source_to_udp_send_samples_ms: list[float] = []
        while not self.rospy.is_shutdown():
            frame = self.make_frame()
            if frame is None:
                if not wait_logged:
                    self.rospy.logwarn(
                        "Waiting for a fresh odom sample on %s; UE transmission is paused when source age exceeds %.3fs",
                        self.args.odom_topic,
                        self.args.source_timeout_s,
                    )
                    wait_logged = True
                time.sleep(period_s)
                next_send_monotonic = time.monotonic()
                continue
            wait_logged = False
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
                sent_bytes = self.sock.sendto(data, (self.args.host, self.args.port))
            except OSError as exc:
                self.send_error_count += 1
                report_send_errors += 1
                self.rospy.logerr_throttle(5.0, "MoSim UE UDP send failed without stopping streamer: %s", exc)
            else:
                report_frames += 1
                report_bytes += sent_bytes
                timing = frame.get("timing", {})
                try:
                    source_received_ns = int(timing.get("source_received_unix_ns", "0"))
                    udp_sent_ns = int(timing.get("udp_sent_unix_ns", "0"))
                except (TypeError, ValueError):
                    source_received_ns = 0
                    udp_sent_ns = 0
                if udp_sent_ns >= source_received_ns > 0:
                    source_to_udp_send_ms = (udp_sent_ns - source_received_ns) / 1_000_000.0
                    if source_to_udp_send_ms <= 60_000.0:
                        report_source_to_udp_send_samples_ms.append(source_to_udp_send_ms)
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
                    stale_odom_callback_drops = self.stale_odom_callback_drops_since_report
                    self.stale_odom_callback_drops_since_report = 0
                    source_age_ms = max(0.0, (time.monotonic() - self.latest_state_monotonic) * 1000.0)
                metrics = transport_metrics(
                    run_id=self.args.run_id,
                    stream_id=self.args.stream_id,
                    host=self.args.host,
                    port=self.args.port,
                    elapsed_s=report_elapsed,
                    sent_frames=report_frames,
                    sent_payload_bytes=report_bytes,
                    send_error_count=report_send_errors,
                    source_updates=source_updates,
                    source_age_ms=source_age_ms,
                    source_timeout_s=self.args.source_timeout_s,
                    source_to_udp_send_samples_ms=report_source_to_udp_send_samples_ms,
                    stale_odom_callback_drops=stale_odom_callback_drops,
                    source_to_receiver_clock_offset_ns=self.args.source_to_receiver_clock_offset_ns,
                )
                if self.args.metrics_output:
                    atomic_json(Path(self.args.metrics_output), metrics)
                self.rospy.loginfo(
                    "MoSim UE live streamer wall_send_rate=%.1fHz target=%.1fHz source_pose_rate=%.1fHz avg_payload_bytes=%.0f payload_kBps=%.1f wire_kBps=%.1f rotor_source=%s motor_command=%s",
                    metrics["send_rate_hz"],
                    self.args.rate_hz,
                    metrics["source_update_rate_hz"],
                    metrics["avg_payload_bytes"],
                    metrics["payload_bytes_per_s"] / 1000.0,
                    metrics["estimated_ipv4_udp_wire_bytes_per_s"] / 1000.0,
                    motor_source,
                    frame["uav"]["motor_command"],
                )
                report_started = time.monotonic()
                report_frames = 0
                report_bytes = 0
                report_send_errors = 0
                report_source_to_udp_send_samples_ms = []

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
    parser.add_argument("--source-timeout-s", type=float, default=0.5)
    parser.add_argument("--stream-id", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--metrics-output", default="")
    parser.add_argument(
        "--source-to-receiver-clock-offset-ns",
        type=int,
        default=None,
        help="Windows receiver Unix time minus WSL source Unix time, captured by the launcher before streaming.",
    )
    parser.add_argument("--lease-dir", default="/tmp/mosim_ue_udp_bridge")
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
    if args.source_timeout_s <= 0.0:
        parser.error("--source-timeout-s must be positive")
    if args.max_datagram_bytes < 1024 or args.max_datagram_bytes > 65507:
        parser.error("--max-datagram-bytes must be between 1024 and 65507")
    if args.source_to_receiver_clock_offset_ns is not None and abs(args.source_to_receiver_clock_offset_ns) > 60_000_000_000:
        parser.error("--source-to-receiver-clock-offset-ns must be within +/-60 seconds")
    if not args.stream_id:
        args.stream_id = f"{args.vehicle_id}-{os.getpid()}-{time.time_ns()}"
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
