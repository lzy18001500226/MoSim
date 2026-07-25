#!/usr/bin/env python3
"""Bridge ROS1 state/reference to MWORKS Live with shadow-first arbitration."""

from __future__ import annotations

import argparse
from collections import deque
import json
import math
import socket
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts/mworks_live"))
from rt1_contract import (  # noqa: E402
    COMMAND_VALUES,
    HEADER,
    STATE_REFERENCE_VALUES,
    CommandFrame,
    ControlOwnerArbiter,
    ControlState,
    StateReferenceFrame,
)
from sunray150_virtual_px4_classic_profile import load_rt1_controller_defaults  # noqa: E402


DEFAULT_MASS_KG, DEFAULT_GRAVITY_MPS2, DEFAULT_HOVER_PERCENTAGE = load_rt1_controller_defaults()


STATE_FRAME_BYTES = HEADER.size + STATE_REFERENCE_VALUES.size
COMMAND_FRAME_BYTES = HEADER.size + COMMAND_VALUES.size
IPV4_UDP_HEADER_BYTES = 28


def percentile(values: deque[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class Rt1RosAdapter:
    def __init__(self, args: argparse.Namespace) -> None:
        import rospy
        from mavros_msgs.msg import AttitudeTarget, State
        from nav_msgs.msg import Odometry
        from quadrotor_msgs.msg import PositionCommand
        from sensor_msgs.msg import Imu
        from std_msgs.msg import String

        self.rospy = rospy
        self.AttitudeTarget = AttitudeTarget
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.trace_stream = (self.result_dir / "rt1_trace.jsonl").open("a", encoding="utf-8", buffering=1)
        self.status_path = self.result_dir / "RT1_STATUS.json"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((args.bind_host, 0))
        self.sock.setblocking(False)
        self.peer = (args.mworks_host, args.mworks_port)
        self.arbiter = ControlOwnerArbiter(
            args.run_id,
            deadline_ms=args.deadline_ms,
            stale_ms=args.command_stale_ms,
            escalation_ms=args.failsafe_escalation_ms,
            consecutive_misses=args.consecutive_deadline_misses,
        )
        self.arbiter.enable_shadow()
        self.sequence = 0
        self.last_odom = None
        self.last_imu = None
        self.last_state = None
        self.last_reference = None
        self.last_px4_candidate = None
        self.last_command = None
        self.last_command_receive_ns = None
        self.command_count = 0
        self.rejected_count = 0
        self.sent_frame_count = 0
        self.sent_payload_bytes = 0
        self.send_error_count = 0
        self.received_frame_count = 0
        self.received_payload_bytes = 0
        self.missing_command_count = 0
        self.duplicate_command_count = 0
        self.out_of_order_command_count = 0
        self.last_received_command_sequence = -1
        self.state_send_times_ns: dict[int, int] = {}
        self.command_age_samples_ms: deque[float] = deque(maxlen=20000)
        self.rtt_samples_ms: deque[float] = deque(maxlen=20000)
        self.send_intervals_ms: deque[float] = deque(maxlen=20000)
        self.receive_intervals_ms: deque[float] = deque(maxlen=20000)
        self.last_send_ns = None
        self.last_receive_ns = None
        self.first_send_ns = None
        self.first_receive_ns = None
        self.last_accepted_trace_ns = 0
        self.accepted_trace_sample_count = 0
        self.last_status_ns = 0
        self.started_ns = time.monotonic_ns()
        self.stop_event = threading.Event()

        self.final_pub = rospy.Publisher(args.final_topic, AttitudeTarget, queue_size=10)
        self.mworks_candidate_pub = rospy.Publisher(args.mworks_candidate_topic, AttitudeTarget, queue_size=10)
        self.owner_pub = rospy.Publisher(args.owner_state_topic, String, queue_size=2, latch=True)
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=10)
        rospy.Subscriber(args.imu_topic, Imu, self.on_imu, queue_size=20)
        rospy.Subscriber(args.flight_state_topic, State, self.on_state, queue_size=10)
        rospy.Subscriber(args.reference_topic, PositionCommand, self.on_reference, queue_size=10)
        rospy.Subscriber(args.px4_candidate_topic, AttitudeTarget, self.on_px4_candidate, queue_size=20)
        rospy.on_shutdown(self.close)
        self.publish_status("shadow_started", force=True)
        self.tick_thread = threading.Thread(
            target=self.wall_clock_tick_loop,
            name="mworks-live-wall-clock-tick",
            daemon=True,
        )
        self.tick_thread.start()

    def wall_clock_tick_loop(self) -> None:
        period_s = 1.0 / self.args.rate_hz
        next_tick = time.monotonic()
        while not self.rospy.is_shutdown() and not self.stop_event.is_set():
            self.on_tick(None)
            next_tick += period_s
            remaining_s = next_tick - time.monotonic()
            if remaining_s > 0.0:
                self.stop_event.wait(remaining_s)
            elif remaining_s < -4.0 * period_s:
                next_tick = time.monotonic()

    def on_odom(self, message: Any) -> None:
        self.last_odom = message

    def on_imu(self, message: Any) -> None:
        self.last_imu = message

    def on_state(self, message: Any) -> None:
        self.last_state = message

    def on_reference(self, message: Any) -> None:
        self.last_reference = message

    def on_px4_candidate(self, message: Any) -> None:
        self.last_px4_candidate = message

    def ready(self) -> bool:
        base_ready = all(value is not None for value in (self.last_odom, self.last_imu, self.last_state))
        ground_hold_ready = bool(
            self.args.allow_ground_hold_reference
            and self.last_state is not None
            and not self.last_state.armed
        )
        return base_ready and (self.last_reference is not None or ground_hold_ready)

    def frame_values(self) -> tuple[float, ...]:
        odom = self.last_odom
        imu = self.last_imu
        reference = self.last_reference
        assert odom is not None and imu is not None
        position = odom.pose.pose.position
        velocity = odom.twist.twist.linear
        orientation = odom.pose.pose.orientation
        body_rate = imu.angular_velocity
        if reference is None:
            orientation_values = (orientation.x, orientation.y, orientation.z, orientation.w)
            yaw = math.atan2(
                2.0 * (orientation_values[3] * orientation_values[2] + orientation_values[0] * orientation_values[1]),
                1.0 - 2.0 * (orientation_values[1] ** 2 + orientation_values[2] ** 2),
            )
            reference_values = (
                position.x, position.y, position.z,
                0.0, 0.0, 0.0,
                0.0, 0.0, 0.0,
                yaw, 0.0,
            )
        else:
            reference_values = (
                reference.position.x, reference.position.y, reference.position.z,
                reference.velocity.x, reference.velocity.y, reference.velocity.z,
                reference.acceleration.x, reference.acceleration.y, reference.acceleration.z,
                reference.yaw, reference.yaw_dot,
            )
        return (
            position.x, position.y, position.z,
            velocity.x, velocity.y, velocity.z,
            orientation.x, orientation.y, orientation.z, orientation.w,
            body_rate.x, body_rate.y, body_rate.z,
            *reference_values,
        )

    def on_tick(self, _event: Any) -> None:
        now_ns = time.monotonic_ns()
        if self.ready():
            self.send_state_reference(now_ns)
        self.receive_commands(now_ns)
        self.arbiter.observe_timeout(now_ns=now_ns, last_command_receive_ns=self.last_command_receive_ns)
        self.maybe_activate_on_ground()
        state = self.arbiter.tick(now_ns=now_ns)
        if state in {
            ControlState.SHADOW, ControlState.READY, ControlState.FALLBACK_HOVER,
            ControlState.DEGRADED, ControlState.LANDING,
        }:
            self.publish_px4_fallback()
        self.publish_status("tick")

    def send_state_reference(self, now_ns: int) -> None:
        state = self.last_state
        assert state is not None
        source_stamp_ns = now_ns
        odom_stamp = self.last_odom.header.stamp.to_nsec()
        if odom_stamp > 0:
            source_stamp_ns = odom_stamp
        frame = StateReferenceFrame(
            run_id=self.args.run_id,
            sequence=self.sequence,
            source_stamp_ns=source_stamp_ns,
            receive_monotonic_ns=now_ns,
            valid_until_ns=now_ns + round(self.args.command_stale_ms * 1e6),
            armed=bool(state.armed),
            state_valid=True,
            reference_valid=True,
            values=tuple(float(value) for value in self.frame_values()),
        )
        payload = frame.pack()
        try:
            sent_bytes = self.sock.sendto(payload, self.peer)
        except OSError as exc:
            self.send_error_count += 1
            self.log({"event": "state_send_error", "reason_code": str(exc), "sent_ns": now_ns})
            return
        if self.last_send_ns is not None:
            self.send_intervals_ms.append((now_ns - self.last_send_ns) / 1e6)
        if self.first_send_ns is None:
            self.first_send_ns = now_ns
        self.last_send_ns = now_ns
        self.sent_frame_count += 1
        self.sent_payload_bytes += sent_bytes
        self.state_send_times_ns[self.sequence] = now_ns
        while len(self.state_send_times_ns) > 4096:
            self.state_send_times_ns.pop(next(iter(self.state_send_times_ns)))
        self.sequence += 1

    def receive_commands(self, now_ns: int) -> None:
        expected_size = HEADER.size + COMMAND_VALUES.size
        processed = 0
        while processed < self.args.max_receive_batch:
            try:
                payload, _peer = self.sock.recvfrom(expected_size + 64)
            except BlockingIOError:
                break
            processed += 1
            receive_ns = time.monotonic_ns()
            if self.first_receive_ns is None:
                self.first_receive_ns = receive_ns
            self.received_frame_count += 1
            self.received_payload_bytes += len(payload)
            if self.last_receive_ns is not None:
                self.receive_intervals_ms.append((receive_ns - self.last_receive_ns) / 1e6)
            self.last_receive_ns = receive_ns
            try:
                command = CommandFrame.unpack(payload)
            except ValueError as exc:
                self.rejected_count += 1
                self.log({"event": "command_rejected", "reason_code": str(exc), "received_ns": receive_ns})
                continue
            if command.sequence == self.last_received_command_sequence:
                self.duplicate_command_count += 1
            elif command.sequence < self.last_received_command_sequence:
                self.out_of_order_command_count += 1
            elif self.last_received_command_sequence >= 0:
                self.missing_command_count += max(0, command.sequence - self.last_received_command_sequence - 1)
            self.last_received_command_sequence = max(self.last_received_command_sequence, command.sequence)
            state_send_ns = self.state_send_times_ns.pop(command.state_sequence, None)
            if state_send_ns is not None:
                self.rtt_samples_ms.append((receive_ns - state_send_ns) / 1e6)
            decision = self.arbiter.observe(
                command,
                now_ns=receive_ns,
                latest_state_sequence=max(0, self.sequence - 1),
            )
            self.last_command = command
            self.last_command_receive_ns = receive_ns
            if decision.command_age_ms is not None:
                self.command_age_samples_ms.append(decision.command_age_ms)
            if decision.accepted:
                self.command_count += 1
                message = self.command_to_attitude_target(command)
                self.mworks_candidate_pub.publish(message)
                if self.arbiter.state == ControlState.ACTIVE:
                    self.final_pub.publish(message)
            else:
                self.rejected_count += 1
            trace_period_ns = round(1e9 / self.args.trace_sample_rate_hz)
            should_trace = not decision.accepted or receive_ns - self.last_accepted_trace_ns >= trace_period_ns
            if should_trace:
                self.log(
                    {
                        "event": "command_decision",
                        "sequence": command.sequence,
                        "state_sequence": command.state_sequence,
                        "accepted": decision.accepted,
                        "reason_code": decision.reason_code,
                        "control_state": decision.state.value,
                        "command_age_ms": decision.command_age_ms,
                        "mworks_compute_ns": command.produced_monotonic_ns,
                    }
                )
                if decision.accepted:
                    self.last_accepted_trace_ns = receive_ns
                    self.accepted_trace_sample_count += 1

    def command_to_attitude_target(self, command: CommandFrame) -> Any:
        message = self.AttitudeTarget()
        message.header.stamp = self.rospy.Time.now()
        message.header.frame_id = "FCU"
        message.type_mask = (
            self.AttitudeTarget.IGNORE_ROLL_RATE
            | self.AttitudeTarget.IGNORE_PITCH_RATE
            | self.AttitudeTarget.IGNORE_YAW_RATE
        )
        q = command.q_enu_from_flu_des_xyzw
        message.orientation.x, message.orientation.y, message.orientation.z, message.orientation.w = q
        full_thrust_n = self.args.mass_kg * self.args.gravity_mps2 / self.args.hover_percentage
        message.thrust = max(0.0, min(1.0, command.collective_thrust_n / full_thrust_n))
        return message

    def publish_px4_fallback(self) -> None:
        if self.last_px4_candidate is not None:
            self.final_pub.publish(self.last_px4_candidate)

    def request_ready(self) -> None:
        if not self.ready() or self.command_count < self.args.minimum_shadow_commands:
            raise ValueError("shadow_evidence_incomplete")
        self.arbiter.mark_ready()
        self.publish_status("ready", force=True)

    def activate(self) -> None:
        if not self.args.allow_active_takeover:
            raise ValueError("active_takeover_not_enabled")
        airborne = bool(self.last_state and self.last_state.armed)
        self.arbiter.activate(airborne=airborne)
        self.publish_status("active", force=True)

    def maybe_activate_on_ground(self) -> None:
        if not self.args.auto_activate_ground or self.arbiter.state != ControlState.SHADOW:
            return
        if not self.ready() or self.command_count < self.args.minimum_shadow_commands:
            return
        self.request_ready()
        self.activate()

    def safe_stop(self) -> None:
        self.arbiter.safe_stop()
        self.publish_status("safe_stop", force=True)

    def transport_metrics(self, now_ns: int) -> dict[str, Any]:
        process_elapsed_s = max((now_ns - self.started_ns) / 1e9, 1e-9)
        state_window_s = (
            max((now_ns - self.first_send_ns) / 1e9, 1e-9)
            if self.first_send_ns is not None
            else 0.0
        )
        command_window_s = (
            max((now_ns - self.first_receive_ns) / 1e9, 1e-9)
            if self.first_receive_ns is not None
            else 0.0
        )
        command_total = self.received_frame_count + self.missing_command_count
        send_jitter = statistics.pstdev(self.send_intervals_ms) if len(self.send_intervals_ms) > 1 else None
        receive_jitter = statistics.pstdev(self.receive_intervals_ms) if len(self.receive_intervals_ms) > 1 else None
        return {
            "state_frame_bytes": STATE_FRAME_BYTES,
            "command_frame_bytes": COMMAND_FRAME_BYTES,
            "process_window_s": process_elapsed_s,
            "startup_wait_before_first_state_s": (
                None if self.first_send_ns is None else (self.first_send_ns - self.started_ns) / 1e9
            ),
            "state_measurement_window_s": state_window_s,
            "command_measurement_window_s": command_window_s,
            "state_send_rate_hz": self.sent_frame_count / state_window_s if state_window_s else 0.0,
            "command_receive_rate_hz": (
                self.received_frame_count / command_window_s if command_window_s else 0.0
            ),
            "state_payload_bytes_per_s": self.sent_payload_bytes / state_window_s if state_window_s else 0.0,
            "command_payload_bytes_per_s": (
                self.received_payload_bytes / command_window_s if command_window_s else 0.0
            ),
            "bidirectional_payload_bytes_per_s": (
                self.sent_payload_bytes / state_window_s if state_window_s else 0.0
            ) + (
                self.received_payload_bytes / command_window_s if command_window_s else 0.0
            ),
            "estimated_ipv4_udp_wire_bytes_per_s": (
                (self.sent_payload_bytes + self.sent_frame_count * IPV4_UDP_HEADER_BYTES) / state_window_s
                if state_window_s else 0.0
            ) + (
                (self.received_payload_bytes + self.received_frame_count * IPV4_UDP_HEADER_BYTES)
                / command_window_s
                if command_window_s else 0.0
            ),
            "send_error_count": self.send_error_count,
            "missing_command_count": self.missing_command_count,
            "duplicate_command_count": self.duplicate_command_count,
            "out_of_order_command_count": self.out_of_order_command_count,
            "estimated_command_drop_rate": self.missing_command_count / command_total if command_total else 0.0,
            "send_interval_jitter_ms": send_jitter,
            "receive_interval_jitter_ms": receive_jitter,
            "rtt_ms_p50": percentile(self.rtt_samples_ms, 0.50),
            "rtt_ms_p95": percentile(self.rtt_samples_ms, 0.95),
            "rtt_ms_p99": percentile(self.rtt_samples_ms, 0.99),
            "command_age_ms_p50": percentile(self.command_age_samples_ms, 0.50),
            "command_age_ms_p95": percentile(self.command_age_samples_ms, 0.95),
            "command_age_ms_p99": percentile(self.command_age_samples_ms, 0.99),
        }

    def publish_status(self, reason: str, *, force: bool = False) -> None:
        now_ns = time.monotonic_ns()
        status_period_ns = round(1e9 / self.args.status_rate_hz)
        if not force and now_ns - self.last_status_ns < status_period_ns:
            return
        self.last_status_ns = now_ns
        value = {
            "schema": "mosim.mworks_live_rt1_status.v1",
            "run_id": self.args.run_id,
            "state": self.arbiter.state.value,
            "reason": reason,
            "shadow_only": not self.args.allow_active_takeover,
            "state_reference_count": self.sequence,
            "accepted_command_count": self.command_count,
            "rejected_command_count": self.rejected_count,
            "accepted_trace_sample_count": self.accepted_trace_sample_count,
            "last_command_sequence": self.arbiter.last_command_sequence,
            "consecutive_deadline_misses": self.arbiter.consecutive_deadline_misses,
            "command_age_ms": (
                None if self.last_command_receive_ns is None or self.last_command is None
                else (self.last_command_receive_ns - self.last_command.source_stamp_ns) / 1e6
            ),
            "mworks_peer": f"{self.args.mworks_host}:{self.args.mworks_port}",
            "transport": self.transport_metrics(now_ns),
            "updated_at_unix": time.time(),
        }
        atomic_json(self.status_path, value)
        self.owner_pub.publish(json.dumps(value, separators=(",", ":")))

    def log(self, value: dict[str, Any]) -> None:
        self.trace_stream.write(json.dumps(value, separators=(",", ":")) + "\n")

    def close(self) -> None:
        self.stop_event.set()
        if hasattr(self, "tick_thread") and self.tick_thread is not threading.current_thread():
            self.tick_thread.join(timeout=1.0)
        if not self.trace_stream.closed:
            self.trace_stream.close()
        self.sock.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--mworks-host", default="127.0.0.1")
    parser.add_argument("--mworks-port", type=int, default=49020)
    parser.add_argument("--bind-host", default="0.0.0.0")
    parser.add_argument("--rate-hz", type=float, default=50.0)
    parser.add_argument("--status-rate-hz", type=float, default=2.0)
    parser.add_argument("--deadline-ms", type=float, default=10.0)
    parser.add_argument("--command-stale-ms", type=float, default=50.0)
    parser.add_argument("--failsafe-escalation-ms", type=float, default=100.0)
    parser.add_argument("--consecutive-deadline-misses", type=int, default=3)
    parser.add_argument("--minimum-shadow-commands", type=int, default=250)
    parser.add_argument("--max-receive-batch", type=int, default=16)
    parser.add_argument("--trace-sample-rate-hz", type=float, default=10.0)
    parser.add_argument("--allow-active-takeover", action="store_true")
    parser.add_argument("--auto-activate-ground", action="store_true")
    parser.add_argument("--allow-ground-hold-reference", action="store_true")
    parser.add_argument("--mass-kg", type=float, default=DEFAULT_MASS_KG)
    parser.add_argument("--gravity-mps2", type=float, default=DEFAULT_GRAVITY_MPS2)
    parser.add_argument("--hover-percentage", type=float, default=DEFAULT_HOVER_PERCENTAGE)
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--imu-topic", default="/uav1/mavros/imu/data")
    parser.add_argument("--flight-state-topic", default="/uav1/mavros/state")
    parser.add_argument("--reference-topic", default="/position_cmd")
    parser.add_argument("--px4-candidate-topic", default="/mosim/mworks_live/px4ctrl_attitude_candidate")
    parser.add_argument("--mworks-candidate-topic", default="/mosim/mworks_live/mworks_attitude_candidate")
    parser.add_argument("--final-topic", default="/uav1/mavros/setpoint_raw/attitude")
    parser.add_argument("--owner-state-topic", default="/mosim/mworks_live/control_owner_state")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_receive_batch <= 0 or args.trace_sample_rate_hz <= 0.0:
        raise SystemExit("receive batch and trace sample rate must be positive")
    if args.rate_hz <= 0.0 or args.status_rate_hz <= 0.0:
        raise SystemExit("rate_hz and status_rate_hz must be positive")
    if args.allow_active_takeover and args.px4_candidate_topic == args.final_topic:
        raise SystemExit("active takeover requires a distinct px4ctrl candidate topic")
    if args.auto_activate_ground and not args.allow_active_takeover:
        raise SystemExit("auto ground activation requires active takeover")
    import rospy

    rospy.init_node("mosim_mworks_live_rt1_adapter")
    Rt1RosAdapter(args)
    rospy.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
