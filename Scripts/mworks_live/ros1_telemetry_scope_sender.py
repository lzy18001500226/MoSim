#!/usr/bin/env python3
"""Mirror live ROS1 flight telemetry to the read-only MWORKS Scope channel."""

from __future__ import annotations

import argparse
import json
import math
import socket
import statistics
import threading
import time
from pathlib import Path
from typing import Any

from telemetry_scope_contract import TelemetryScopeAck, TelemetryScopeFrame


class TelemetryScopeSender:
    def __init__(self, args: argparse.Namespace) -> None:
        import rospy
        from mavros_msgs.msg import AttitudeTarget, State
        from nav_msgs.msg import Odometry
        from quadrotor_msgs.msg import PositionCommand

        self.rospy = rospy
        self.args = args
        self.peer = (args.mworks_host, args.mworks_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((args.bind_host, 0))
        self.sock.setblocking(False)
        self.stop_event = threading.Event()
        self.odom: Any = None
        self.reference: Any = None
        self.command: Any = None
        self.state: Any = None
        self.sequence = 0
        self.ack_sequence = -1
        self.sent_ns: dict[int, int] = {}
        self.sent_count = 0
        self.ack_count = 0
        self.invalid_ack_count = 0
        self.sequence_gap_count = 0
        self.rtt_ms = math.nan
        self.rtt_samples_ms: list[float] = []
        self.send_intervals_ms: list[float] = []
        self.last_send_ns: int | None = None
        self.started_ns = time.monotonic_ns()
        self.result_dir = args.result_dir
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.result_dir / "telemetry_scope_trace.jsonl"
        self.summary_path = self.result_dir / "TELEMETRY_SCOPE_SUMMARY.json"
        self.trace = self.trace_path.open("a", encoding="utf-8", buffering=1)

        rospy.Subscriber(args.odom_topic, Odometry, self._store_odom, queue_size=50)
        rospy.Subscriber(args.reference_topic, PositionCommand, self._store_reference, queue_size=50)
        rospy.Subscriber(args.command_topic, AttitudeTarget, self._store_command, queue_size=50)
        rospy.Subscriber(args.state_topic, State, self._store_state, queue_size=20)
        rospy.on_shutdown(self.close)
        self.thread = threading.Thread(target=self._loop, name="mworks-telemetry-scope", daemon=True)
        self.thread.start()

    def _store_odom(self, message: Any) -> None:
        self.odom = message

    def _store_reference(self, message: Any) -> None:
        self.reference = message

    def _store_command(self, message: Any) -> None:
        self.command = message

    def _store_state(self, message: Any) -> None:
        self.state = message

    def _loop(self) -> None:
        period_s = 1.0 / self.args.rate_hz
        next_tick = time.monotonic()
        next_status = next_tick
        while not self.rospy.is_shutdown() and not self.stop_event.is_set():
            self._receive_acks()
            if self.odom is not None:
                self._send_frame()
            now = time.monotonic()
            if now >= next_status:
                self._write_summary()
                next_status = now + 1.0 / self.args.status_rate_hz
            next_tick += period_s
            wait_s = next_tick - time.monotonic()
            if wait_s > 0:
                self.stop_event.wait(wait_s)
            elif wait_s < -4.0 * period_s:
                next_tick = time.monotonic()

    def _send_frame(self) -> None:
        now_ns = time.monotonic_ns()
        odom = self.odom
        position = odom.pose.pose.position
        velocity = odom.twist.twist.linear
        orientation = odom.pose.pose.orientation
        body_rate = odom.twist.twist.angular
        reference = self.reference
        command = self.command

        if reference is None:
            ref_position = (position.x, position.y, position.z)
            ref_velocity = (0.0, 0.0, 0.0)
            ref_acceleration = (0.0, 0.0, 0.0)
            ref_yaw = self._yaw(orientation.x, orientation.y, orientation.z, orientation.w)
        else:
            ref_position = (reference.position.x, reference.position.y, reference.position.z)
            ref_velocity = (reference.velocity.x, reference.velocity.y, reference.velocity.z)
            ref_acceleration = (reference.acceleration.x, reference.acceleration.y, reference.acceleration.z)
            ref_yaw = reference.yaw

        position_error = (
            ref_position[0] - position.x,
            ref_position[1] - position.y,
            ref_position[2] - position.z,
        )
        target_thrust = float(command.thrust) if command is not None else 0.0
        attitude_error = self._attitude_error(command, orientation)
        source_stamp_ns = odom.header.stamp.to_nsec()
        source_age_ms = self._source_age_ms(odom)
        command_age_ms = self._message_age_ms(command)
        values = (
            position.x, position.y, position.z,
            velocity.x, velocity.y, velocity.z,
            orientation.x, orientation.y, orientation.z, orientation.w,
            body_rate.x, body_rate.y, body_rate.z,
            *ref_position, *ref_velocity, *ref_acceleration, ref_yaw,
            target_thrust, *position_error, attitude_error, source_age_ms,
            self.rtt_ms if math.isfinite(self.rtt_ms) else -1.0,
            command_age_ms,
            float(self.sequence_gap_count),
        )
        frame = TelemetryScopeFrame(
            run_id=self.args.run_id,
            sequence=self.sequence,
            source_stamp_ns=max(0, source_stamp_ns),
            produced_monotonic_ns=now_ns,
            valid_until_ns=now_ns + round(self.args.stale_ms * 1e6),
            armed=bool(self.state is not None and self.state.armed),
            state_valid=True,
            reference_valid=reference is not None,
            command_valid=command is not None,
            values=tuple(float(value) for value in values),
        )
        payload = frame.pack()
        self.sock.sendto(payload, self.peer)
        if self.last_send_ns is not None:
            self.send_intervals_ms.append((now_ns - self.last_send_ns) / 1e6)
            self.send_intervals_ms = self.send_intervals_ms[-4096:]
        self.last_send_ns = now_ns
        self.sent_ns[self.sequence] = now_ns
        while len(self.sent_ns) > 4096:
            self.sent_ns.pop(next(iter(self.sent_ns)))
        self.sent_count += 1
        self.sequence += 1

    def _receive_acks(self) -> None:
        while True:
            try:
                payload, _peer = self.sock.recvfrom(256)
            except BlockingIOError:
                return
            now_ns = time.monotonic_ns()
            try:
                ack = TelemetryScopeAck.unpack(payload)
            except ValueError:
                self.invalid_ack_count += 1
                continue
            if ack.run_id != self.args.run_id:
                self.invalid_ack_count += 1
                continue
            if self.ack_sequence >= 0 and ack.related_sequence > self.ack_sequence + 1:
                self.sequence_gap_count += ack.related_sequence - self.ack_sequence - 1
            self.ack_sequence = max(self.ack_sequence, ack.related_sequence)
            sent_ns = self.sent_ns.pop(ack.related_sequence, None)
            if sent_ns is not None:
                self.rtt_ms = (now_ns - sent_ns) / 1e6
                self.rtt_samples_ms.append(self.rtt_ms)
                self.rtt_samples_ms = self.rtt_samples_ms[-4096:]
            self.ack_count += 1

    def _write_summary(self) -> None:
        now_ns = time.monotonic_ns()
        elapsed_s = max((now_ns - self.started_ns) / 1e9, 1e-9)
        intervals = self.send_intervals_ms
        payload = {
            "schema": "mosim.mworks_telemetry_scope_summary.v1",
            "run_id": self.args.run_id,
            "read_only_observer": True,
            "control_authority": False,
            "peer": f"{self.args.mworks_host}:{self.args.mworks_port}",
            "sent_frames": self.sent_count,
            "ack_frames": self.ack_count,
            "invalid_ack_frames": self.invalid_ack_count,
            "ack_sequence_gaps": self.sequence_gap_count,
            "send_rate_hz": self.sent_count / elapsed_s,
            "send_jitter_ms": statistics.pstdev(intervals) if len(intervals) > 1 else 0.0,
            "rtt_ms_latest": self.rtt_ms if math.isfinite(self.rtt_ms) else None,
            "rtt_ms_p95": self._percentile(self.rtt_samples_ms, 0.95),
            "updated_at_unix": time.time(),
        }
        temporary = self.summary_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.summary_path)
        self.trace.write(json.dumps(payload, separators=(",", ":")) + "\n")

    def close(self) -> None:
        self.stop_event.set()
        if hasattr(self, "thread") and self.thread is not threading.current_thread():
            self.thread.join(timeout=1.0)
        self._write_summary()
        if not self.trace.closed:
            self.trace.close()
        self.sock.close()

    def _source_age_ms(self, odom: Any) -> float:
        stamp = odom.header.stamp
        if stamp.to_nsec() <= 0:
            return -1.0
        return max(0.0, (self.rospy.Time.now() - stamp).to_sec() * 1000.0)

    def _message_age_ms(self, message: Any) -> float:
        if message is None or not hasattr(message, "header"):
            return -1.0
        stamp = message.header.stamp
        if stamp.to_nsec() <= 0:
            return -1.0
        return max(0.0, (self.rospy.Time.now() - stamp).to_sec() * 1000.0)

    @staticmethod
    def _yaw(x: float, y: float, z: float, w: float) -> float:
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    @staticmethod
    def _attitude_error(command: Any, orientation: Any) -> float:
        if command is None:
            return -1.0
        target = command.orientation
        dot = abs(
            target.w * orientation.w + target.x * orientation.x
            + target.y * orientation.y + target.z * orientation.z
        )
        return 2.0 * math.acos(max(0.0, min(1.0, dot)))

    @staticmethod
    def _percentile(values: list[float], fraction: float) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        return ordered[round((len(ordered) - 1) * fraction)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--mworks-host", default="127.0.0.1")
    parser.add_argument("--mworks-port", type=int, default=49020)
    parser.add_argument("--bind-host", default="0.0.0.0")
    parser.add_argument("--rate-hz", type=float, default=50.0)
    parser.add_argument("--status-rate-hz", type=float, default=1.0)
    parser.add_argument("--stale-ms", type=float, default=200.0)
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--reference-topic", default="/position_cmd")
    parser.add_argument("--command-topic", default="/uav1/mavros/setpoint_raw/target_attitude")
    parser.add_argument("--state-topic", default="/uav1/mavros/state")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate_hz <= 0 or args.status_rate_hz <= 0 or args.stale_ms <= 0:
        raise SystemExit("rate_hz, status_rate_hz, and stale_ms must be positive")
    import rospy

    rospy.init_node("mosim_mworks_telemetry_scope_sender")
    TelemetryScopeSender(args)
    rospy.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
