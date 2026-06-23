#!/usr/bin/env python3
"""Gazebo-truth position controller for bounded single-UAV pre-acceptance.

This node consumes Gazebo truth pose text from stdin plus live
`/mosim/planner/setpoint`, then publishes `mosim_msgs/msg/ControllerOutput`.
It is a real external-setpoint controller bridge for the current Gazebo plant;
it is still pre-acceptance evidence, not final controller-performance proof.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for helper_path in (Path(__file__).resolve().parent, ROOT / "Scripts" / "gazebo"):
    if str(helper_path) not in sys.path:
        sys.path.insert(0, str(helper_path))

from gazebo_truth_planner_setpoint_tracker import (  # noqa: E402
    PITCH_MIX,
    ROLL_MIX,
    YAW_MIX,
    angle_wrap,
    append_jsonl,
    bounded,
    has_timed_truth,
    iter_stdin_message_chunks,
    parse_truth_samples,
    project_path,
    rel,
    sample_orientation,
    write_json,
)
from capture_gazebo_state_truth_topic import (  # noqa: E402
    parse_samples as parse_state_topic_samples,
    run_sample as run_state_topic_sample,
)
from capture_gazebo_pose_truth_topic import (  # noqa: E402
    parse_samples as parse_pose_topic_samples,
    run_sample as run_pose_topic_sample,
)


def stamp_to_seconds(stamp: Any) -> float:
    return float(getattr(stamp, "sec", 0)) + float(getattr(stamp, "nanosec", 0)) * 1e-9


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic-name", default="/world/sunray150_single_uav_competition_light/dynamic_pose/info")
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--truth-frame-id", default="world")
    parser.add_argument("--setpoint-topic", default="/mosim/planner/setpoint")
    parser.add_argument("--output-topic", default="/mosim/sunray150/controller_output")
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--expected-frame", default="map")
    parser.add_argument("--hover-command", type=float, default=0.05520)
    parser.add_argument("--kp-x", type=float, default=0.0012)
    parser.add_argument("--kd-x", type=float, default=0.0022)
    parser.add_argument("--ka-x", type=float, default=0.0008)
    parser.add_argument("--kp-y", type=float, default=0.0012)
    parser.add_argument("--kd-y", type=float, default=0.0022)
    parser.add_argument("--ka-y", type=float, default=0.0008)
    parser.add_argument("--kp-z", type=float, default=0.0010)
    parser.add_argument("--kd-z", type=float, default=0.0020)
    parser.add_argument("--ki-z", type=float, default=0.00015)
    parser.add_argument("--kp-roll", type=float, default=0.010)
    parser.add_argument("--kd-roll", type=float, default=0.002)
    parser.add_argument("--kp-pitch", type=float, default=0.010)
    parser.add_argument("--kd-pitch", type=float, default=0.002)
    parser.add_argument("--kp-yaw", type=float, default=0.0)
    parser.add_argument("--kd-yaw", type=float, default=0.0)
    parser.add_argument("--attitude-command-limit", type=float, default=0.0035)
    parser.add_argument("--xy-control-sign", type=float, choices=(-1.0, 1.0), default=-1.0)
    parser.add_argument("--roll-control-sign", type=float, choices=(-1.0, 1.0), default=None)
    parser.add_argument("--pitch-control-sign", type=float, choices=(-1.0, 1.0), default=None)
    parser.add_argument("--xy-error-limit-m", type=float, default=2.0)
    parser.add_argument("--xy-velocity-error-limit-mps", type=float, default=1.5)
    parser.add_argument("--xy-track-failsafe-error-m", type=float, default=3.0)
    parser.add_argument("--xy-track-failsafe-land-after-count", type=int, default=20)
    parser.add_argument("--integral-limit-m-s", type=float, default=1.0)
    parser.add_argument("--command-min", type=float, default=0.05350)
    parser.add_argument("--command-max", type=float, default=0.05635)
    parser.add_argument("--ground-motor-command", type=float, default=0.0)
    parser.add_argument("--takeoff-xy-enable-altitude-m", type=float, default=0.9)
    parser.add_argument("--takeoff-stable-z-error-m", type=float, default=0.3)
    parser.add_argument("--takeoff-reference-ready-z-m", type=float, default=0.9)
    parser.add_argument("--takeoff-stable-max-vz-mps", type=float, default=0.35)
    parser.add_argument("--takeoff-stable-s", type=float, default=0.5)
    parser.add_argument("--takeoff-hold-setpoint-until-stable", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--low-altitude-xy-scale-start-m", type=float, default=0.35)
    parser.add_argument("--low-altitude-xy-scale-full-m", type=float, default=0.85)
    parser.add_argument("--recovery-xy-brake-scale", type=float, default=0.35)
    parser.add_argument("--recovery-reset-altitude-m", type=float, default=0.35)
    parser.add_argument("--recovery-exit-altitude-m", type=float, default=0.85)
    parser.add_argument("--recovery-attitude-command-limit", type=float, default=0.004)
    parser.add_argument("--recovery-kp-roll", type=float, default=0.018)
    parser.add_argument("--recovery-kd-roll", type=float, default=0.004)
    parser.add_argument("--recovery-kp-pitch", type=float, default=0.018)
    parser.add_argument("--recovery-kd-pitch", type=float, default=0.004)
    parser.add_argument("--tilt-recovery-threshold-rad", type=float, default=0.55)
    parser.add_argument("--descent-recovery-threshold-mps", type=float, default=0.75)
    parser.add_argument("--ground-xy-disable-altitude-m", type=float, default=0.18)
    parser.add_argument("--ground-target-altitude-m", type=float, default=0.20)
    parser.add_argument("--keep-xy-track-after-first-entry", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--publish-hold-before-setpoint", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--pre-setpoint-hold-z", type=float, default=1.2)
    parser.add_argument("--mission-goal", default="")
    parser.add_argument("--mission-goal-reference-radius-m", type=float, default=0.35)
    parser.add_argument("--mission-goal-capture-radius-m", type=float, default=0.0)
    parser.add_argument("--mission-goal-capture-min-altitude-m", type=float, default=0.45)
    parser.add_argument("--mission-goal-capture-xy-scale", type=float, default=0.45)
    parser.add_argument("--mission-goal-capture-z-error-m", type=float, default=0.35)
    parser.add_argument("--mission-goal-accept-radius-m", type=float, default=0.8)
    parser.add_argument("--mission-land-lock", choices=("current", "goal"), default="current")
    parser.add_argument("--mission-goal-hold-s", type=float, default=1.5)
    parser.add_argument("--mission-land-z-m", type=float, default=0.12)
    parser.add_argument("--mission-land-rate-mps", type=float, default=0.35)
    parser.add_argument("--setpoint-timeout-s", type=float, default=0.35)
    parser.add_argument("--hold-last-setpoint-when-truth-buffered", action="store_true")
    parser.add_argument("--max-publish-hz", type=float, default=20.0)
    parser.add_argument("--duration-s", type=float, default=24.0)
    parser.add_argument("--sync-truth-to-wall-time", action="store_true")
    parser.add_argument("--truth-wall-time-factor", type=float, default=1.0)
    parser.add_argument("--poll-command", default="")
    parser.add_argument("--poll-sleep-s", type=float, default=0.05)
    parser.add_argument("--poll-sample-timeout-s", type=float, default=1.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    for key, value in vars(args).items():
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"{key} must be finite")
    if not (0.0 < args.command_min < args.command_max <= 1.0):
        raise ValueError("command bounds must satisfy 0 < command_min < command_max <= 1")
    if not (0.0 <= args.ground_motor_command <= args.command_min):
        raise ValueError("ground_motor_command must satisfy 0 <= ground_motor_command <= command_min")
    if not (args.command_min <= args.hover_command <= args.command_max):
        raise ValueError("hover_command must be within command bounds")
    if args.setpoint_timeout_s <= 0.0 or args.max_publish_hz <= 0.0 or args.duration_s <= 0.0:
        raise ValueError("timeouts, rates, and duration must be positive")
    if args.truth_wall_time_factor <= 0.0:
        raise ValueError("truth_wall_time_factor must be positive")
    if args.poll_sleep_s < 0.0 or args.poll_sample_timeout_s <= 0.0:
        raise ValueError("poll timing values must be non-negative and positive")
    if args.xy_error_limit_m <= 0.0 or args.xy_velocity_error_limit_mps <= 0.0:
        raise ValueError("XY limits must be positive")
    if args.xy_track_failsafe_error_m <= 0.0:
        raise ValueError("XY track failsafe error must be positive")
    if args.xy_track_failsafe_land_after_count < 0:
        raise ValueError("XY track failsafe land-after-count must be non-negative")
    if args.attitude_command_limit < 0.0 or args.integral_limit_m_s < 0.0:
        raise ValueError("command and integral limits must be non-negative")
    if args.takeoff_stable_max_vz_mps < 0.0:
        raise ValueError("takeoff stable vertical speed must be non-negative")
    if args.takeoff_reference_ready_z_m < 0.0:
        raise ValueError("takeoff reference-ready altitude must be non-negative")
    if args.low_altitude_xy_scale_start_m < 0.0:
        raise ValueError("low-altitude XY scale start must be non-negative")
    if args.low_altitude_xy_scale_full_m <= args.low_altitude_xy_scale_start_m:
        raise ValueError("low-altitude XY scale full threshold must exceed start threshold")
    if not (0.0 <= args.recovery_xy_brake_scale <= 1.0):
        raise ValueError("recovery XY brake scale must be within [0, 1]")
    if args.recovery_reset_altitude_m < 0.0:
        raise ValueError("recovery reset altitude must be non-negative")
    if args.recovery_exit_altitude_m < args.recovery_reset_altitude_m:
        raise ValueError("recovery exit altitude must be >= recovery reset altitude")
    if args.recovery_attitude_command_limit < 0.0:
        raise ValueError("recovery attitude command limit must be non-negative")
    if args.tilt_recovery_threshold_rad < 0.0 or args.descent_recovery_threshold_mps < 0.0:
        raise ValueError("tilt/descent recovery thresholds must be non-negative")
    if args.ground_xy_disable_altitude_m < 0.0 or args.ground_target_altitude_m < 0.0:
        raise ValueError("ground XY disable thresholds must be non-negative")
    if args.pre_setpoint_hold_z < 0.0:
        raise ValueError("pre-setpoint hold altitude must be non-negative")
    if args.mission_goal:
        values = [float(item) for item in str(args.mission_goal).split(",")]
        if len(values) != 3 or not all(math.isfinite(item) for item in values):
            raise ValueError("--mission-goal must be finite x,y,z")
    if (
        args.mission_goal_reference_radius_m < 0.0
        or args.mission_goal_capture_radius_m < 0.0
        or args.mission_goal_accept_radius_m < 0.0
    ):
        raise ValueError("mission goal radii must be non-negative")
    if args.mission_goal_capture_min_altitude_m < 0.0:
        raise ValueError("mission goal capture minimum altitude must be non-negative")
    if not (0.0 <= args.mission_goal_capture_xy_scale <= 1.0):
        raise ValueError("mission goal capture XY scale must be within [0, 1]")
    if args.mission_goal_capture_z_error_m < 0.0:
        raise ValueError("mission goal capture z error must be non-negative")
    if args.mission_goal_hold_s < 0.0 or args.mission_land_z_m < 0.0 or args.mission_land_rate_mps <= 0.0:
        raise ValueError("mission landing parameters must be non-negative, with positive land rate")


def dry_run_report(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": "mosim.gazebo_truth_position_controller.dry_run.v1",
        "status": "ready",
        "input_truth_topic": args.input_topic_name,
        "setpoint_topic": args.setpoint_topic,
        "output_topic": args.output_topic,
        "required_reference_mode": "external_planner_setpoint",
        "gains": {
            "kp_x": args.kp_x,
            "kd_x": args.kd_x,
            "ka_x": args.ka_x,
            "kp_y": args.kp_y,
            "kd_y": args.kd_y,
            "ka_y": args.ka_y,
            "kp_z": args.kp_z,
            "kd_z": args.kd_z,
            "ki_z": args.ki_z,
        },
        "command_bounds": [args.command_min, args.command_max],
        "xy_control_sign": args.xy_control_sign,
        "truth_clock_policy": {
            "sync_truth_to_wall_time": bool(args.sync_truth_to_wall_time),
            "truth_wall_time_factor": args.truth_wall_time_factor,
            "poll_command": args.poll_command,
            "hold_last_setpoint_when_truth_buffered": bool(args.hold_last_setpoint_when_truth_buffered),
        },
        "claim_boundary": [
            "dry-run only; no ROS2 graph or Gazebo stream was touched",
            "external PlannerSetpoint is required; no internal figure-8 reference is generated",
            "no final closed_loop, competition controller performance, planner_ready, or multi-UAV readiness is claimed",
        ],
    }


def iter_truth_chunks(args: argparse.Namespace):
    if not args.poll_command:
        yield from iter_stdin_message_chunks(sys.stdin)
        return
    deadline = time.monotonic() + float(args.duration_s) + float(args.setpoint_timeout_s) + 2.0
    while time.monotonic() < deadline:
        try:
            completed = subprocess.run(
                [args.poll_command, "topic", "-e", "-t", args.input_topic_name, "-n", "1"],
                check=False,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=max(0.1, float(args.poll_sample_timeout_s)),
            )
        except subprocess.TimeoutExpired:
            time.sleep(max(0.0, float(args.poll_sleep_s)))
            continue
        if completed.stdout.strip():
            yield completed.stdout
        time.sleep(max(0.0, float(args.poll_sleep_s)))


def iter_polled_truth_samples(args: argparse.Namespace, diagnostics: dict[str, Any] | None = None):
    deadline = time.monotonic() + float(args.duration_s) + float(args.setpoint_timeout_s) + 2.0
    while time.monotonic() < deadline:
        stdout, stderr, returncode = run_pose_topic_sample(
            args.poll_command,
            args.input_topic_name,
            max(0.1, float(args.poll_sample_timeout_s)),
        )
        if diagnostics is not None:
            diagnostics["attempt_count"] = int(diagnostics.get("attempt_count", 0)) + 1
            diagnostics["stdout_bytes_total"] = int(diagnostics.get("stdout_bytes_total", 0)) + len(
                stdout.encode("utf-8", errors="replace")
            )
            diagnostics["stderr_tail"] = stderr[-500:]
            diagnostics["returncode_tail"] = (diagnostics.get("returncode_tail") or [])[-9:] + [int(returncode)]
        if stdout.strip():
            samples = parse_pose_topic_samples(
                stdout,
                model_name=args.model_name,
                topic=args.input_topic_name,
                frame_id=args.truth_frame_id,
            )
            pose_sample_count = len(samples)
            if not samples:
                samples = parse_state_topic_samples(
                    stdout,
                    topic=args.input_topic_name,
                    model_name=args.model_name,
                    frame_id=args.truth_frame_id,
                )
            state_sample_count = len(samples) if pose_sample_count == 0 else 0
            if diagnostics is not None:
                diagnostics["stdout_nonempty_attempt_count"] = int(
                    diagnostics.get("stdout_nonempty_attempt_count", 0)
                ) + 1
                diagnostics["pose_parsed_samples_total"] = int(
                    diagnostics.get("pose_parsed_samples_total", 0)
                ) + pose_sample_count
                diagnostics["state_parsed_samples_total"] = int(
                    diagnostics.get("state_parsed_samples_total", 0)
                ) + state_sample_count
                diagnostics["parsed_samples_total"] = int(diagnostics.get("parsed_samples_total", 0)) + len(samples)
                diagnostics["attempts_tail"] = (diagnostics.get("attempts_tail") or [])[-9:] + [
                    {
                        "returncode": int(returncode),
                        "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
                        "stderr_tail": stderr[-200:],
                        "pose_parsed_samples": pose_sample_count,
                        "state_parsed_samples": state_sample_count,
                        "parsed_samples": len(samples),
                    }
                ]
            for sample in samples:
                yield sample
        time.sleep(max(0.0, float(args.poll_sleep_s)))


def iter_truth_samples(args: argparse.Namespace, diagnostics: dict[str, Any] | None = None):
    if args.poll_command:
        yield from iter_polled_truth_samples(args, diagnostics=diagnostics)
        return
    for chunk in iter_truth_chunks(args):
        samples = parse_truth_samples(
            chunk,
            model_name=args.model_name,
            topic=args.input_topic_name,
            frame_id=args.truth_frame_id,
        )
        for sample in samples:
            yield sample


def run_controller(args: argparse.Namespace) -> int:
    try:
        import rclpy
        from mosim_msgs.msg import ControllerOutput, PlannerSetpoint
        from rclpy.node import Node
    except Exception as exc:
        report = {
            "schema": "mosim.gazebo_truth_position_controller.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "claim_boundary": ["No ControllerOutput message was published."],
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    class PositionControllerNode(Node):
        def __init__(self) -> None:
            super().__init__("mosim_gazebo_truth_position_controller")
            self.publisher = self.create_publisher(ControllerOutput, args.output_topic, 10)
            self.subscription = self.create_subscription(PlannerSetpoint, args.setpoint_topic, self.on_setpoint, 10)
            self.latest_setpoint: PlannerSetpoint | None = None
            self.latest_setpoint_wall = 0.0
            self.latest_setpoint_stamp_s: float | None = None
            self.accepted_setpoints = 0
            self.rejected_setpoints = 0

        def on_setpoint(self, message: PlannerSetpoint) -> None:
            if message.frame_id != args.expected_frame:
                self.rejected_setpoints += 1
                return
            values = list(message.position_m) + list(message.velocity_mps) + list(message.acceleration_mps2)
            values += [message.yaw_rad, message.yaw_rate_radps]
            if not all(math.isfinite(float(item)) for item in values):
                self.rejected_setpoints += 1
                return
            self.latest_setpoint = message
            self.latest_setpoint_wall = time.time()
            self.latest_setpoint_stamp_s = stamp_to_seconds(message.header.stamp)
            self.accepted_setpoints += 1

    rclpy.init()
    node = PositionControllerNode()
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    published_count = 0
    truth_sample_count = 0
    header_stamp_sample_count = 0
    skipped_no_setpoint = 0
    skipped_stale_setpoint = 0
    skipped_by_rate = 0
    first_header_time: float | None = None
    last_header_time: float | None = None
    last_sample_time: float | None = None
    last_position: list[float] | None = None
    last_roll: float | None = None
    last_pitch: float | None = None
    last_yaw: float | None = None
    last_publish_wall = 0.0
    last_publish_sample_time: float | None = None
    first_truth_wall: float | None = None
    integral_z_error = 0.0
    min_z: float | None = None
    max_z: float | None = None
    max_xy_error = 0.0
    max_z_error = 0.0
    max_command_span = 0.0
    altitude_stable_since: float | None = None
    xy_tracking_enabled = False
    xy_hold_position: list[float] | None = None
    xy_track_enter_count = 0
    xy_track_exit_count = 0
    mission_goal = [float(item) for item in str(args.mission_goal).split(",")] if args.mission_goal else None
    mission_goal_reference_since: float | None = None
    mission_goal_capture_active = False
    mission_goal_capture_since: float | None = None
    mission_goal_arrival_since: float | None = None
    mission_land_start_time: float | None = None
    mission_land_xy_position: list[float] | None = None
    altitude_recovery_active = False
    airborne_seen = False
    ground_lock_latched = False
    altitude_recovery_enter_count = 0
    altitude_recovery_exit_count = 0
    xy_track_failsafe_enter_count = 0
    xy_track_failsafe_active_count = 0
    control_phase_counts: dict[str, int] = {}
    last_trace: dict[str, Any] | None = None
    poll_diagnostics: dict[str, Any] = {
        "enabled": bool(args.poll_command),
        "command": args.poll_command,
        "sample_timeout_s": args.poll_sample_timeout_s,
        "sleep_s": args.poll_sleep_s,
        "attempt_count": 0,
        "stdout_nonempty_attempt_count": 0,
        "stdout_bytes_total": 0,
        "pose_parsed_samples_total": 0,
        "state_parsed_samples_total": 0,
        "parsed_samples_total": 0,
        "returncode_tail": [],
        "stderr_tail": "",
        "attempts_tail": [],
    }

    try:
        time.sleep(0.8)

        for sample in iter_truth_samples(args, diagnostics=poll_diagnostics):
                truth_sample_count += 1
                if not has_timed_truth(sample):
                    continue
                header_stamp_sample_count += 1
                sample_time = float(sample["time"])
                if first_header_time is None:
                    first_header_time = sample_time
                    first_truth_wall = time.monotonic()
                last_header_time = sample_time
                if args.sync_truth_to_wall_time and first_truth_wall is not None and first_header_time is not None:
                    target_wall = first_truth_wall + (sample_time - first_header_time) / args.truth_wall_time_factor
                    sleep_s = target_wall - time.monotonic()
                    if sleep_s > 0.0:
                        time.sleep(min(sleep_s, 0.25))
                position = [float(item) for item in sample["position_m"]]
                if xy_hold_position is None:
                    xy_hold_position = [position[0], position[1]]
                min_z = position[2] if min_z is None else min(min_z, position[2])
                max_z = position[2] if max_z is None else max(max_z, position[2])
                roll, pitch, yaw = sample_orientation(sample)

                dt = 0.0
                velocity = [0.0, 0.0, 0.0]
                roll_rate = 0.0
                pitch_rate = 0.0
                yaw_rate = 0.0
                if last_sample_time is not None and last_position is not None and sample_time > last_sample_time:
                    dt = sample_time - last_sample_time
                    velocity = [(position[i] - last_position[i]) / dt for i in range(3)]
                    if last_roll is not None:
                        roll_rate = angle_wrap(roll - last_roll) / dt
                    if last_pitch is not None:
                        pitch_rate = angle_wrap(pitch - last_pitch) / dt
                    if last_yaw is not None:
                        yaw_rate = angle_wrap(yaw - last_yaw) / dt
                last_sample_time = sample_time
                last_position = position
                last_roll = roll
                last_pitch = pitch
                last_yaw = yaw

                if first_header_time is not None and sample_time - first_header_time >= args.duration_s:
                    raise StopIteration

                setpoint = node.latest_setpoint
                using_pre_setpoint_hold = setpoint is None
                if using_pre_setpoint_hold:
                    skipped_no_setpoint += 1
                    if not args.publish_hold_before_setpoint:
                        continue
                    setpoint_age = 0.0
                    setpoint_age_source = "pre_setpoint_hold"
                    raw_target_position = [
                        xy_hold_position[0] if xy_hold_position is not None else position[0],
                        xy_hold_position[1] if xy_hold_position is not None else position[1],
                        float(args.pre_setpoint_hold_z),
                    ]
                    raw_target_velocity = [0.0, 0.0, 0.0]
                    raw_target_acceleration = [0.0, 0.0, 0.0]
                    target_yaw = 0.0
                    target_yaw_rate = 0.0
                    setpoint_sequence = 0
                else:
                    setpoint_stamp_s = node.latest_setpoint_stamp_s
                    if setpoint_stamp_s is not None and setpoint_stamp_s > 0.0:
                        setpoint_age = max(0.0, sample_time - setpoint_stamp_s)
                        setpoint_age_source = "sim_time_header_stamp"
                    else:
                        setpoint_age = time.time() - node.latest_setpoint_wall
                        setpoint_age_source = "wall_receive_time"
                    if setpoint_age > args.setpoint_timeout_s and not args.hold_last_setpoint_when_truth_buffered:
                        skipped_stale_setpoint += 1
                        continue
                    if setpoint_age > args.setpoint_timeout_s:
                        skipped_stale_setpoint += 1
                    raw_target_position = [float(item) for item in setpoint.position_m]
                    raw_target_velocity = [float(item) for item in setpoint.velocity_mps]
                    raw_target_acceleration = [float(item) for item in setpoint.acceleration_mps2]
                    target_yaw = float(setpoint.yaw_rad)
                    target_yaw_rate = float(setpoint.yaw_rate_radps)
                    setpoint_sequence = int(setpoint.sequence)
                    takeoff_hold_can_override_setpoint = (
                        args.takeoff_hold_setpoint_until_stable
                        and not xy_tracking_enabled
                        and xy_track_enter_count <= 0
                        and raw_target_position[2] > args.ground_target_altitude_m
                    )
                    if takeoff_hold_can_override_setpoint:
                        raw_target_position = [
                            xy_hold_position[0] if xy_hold_position is not None else position[0],
                            xy_hold_position[1] if xy_hold_position is not None else position[1],
                            max(float(args.pre_setpoint_hold_z), raw_target_position[2]),
                        ]
                        raw_target_velocity = [0.0, 0.0, 0.0]
                        raw_target_acceleration = [0.0, 0.0, 0.0]
                    if (
                        position[2] >= args.takeoff_xy_enable_altitude_m
                        and not xy_tracking_enabled
                        and not altitude_recovery_active
                        and not args.takeoff_hold_setpoint_until_stable
                    ):
                        xy_tracking_enabled = True
                        xy_track_enter_count += 1
                now = time.time()
                if (
                    published_count > 0
                    and last_publish_sample_time is not None
                    and sample_time - last_publish_sample_time < 1.0 / args.max_publish_hz
                ):
                    skipped_by_rate += 1
                    continue

                reference_error = [raw_target_position[i] - position[i] for i in range(3)]
                reference_xy_error = math.hypot(reference_error[0], reference_error[1])
                z_error = reference_error[2]
                if dt > 0.0:
                    integral_z_error = bounded(
                        integral_z_error + z_error * dt,
                        -abs(args.integral_limit_m_s),
                        abs(args.integral_limit_m_s),
                    )
                max_xy_error = max(max_xy_error, reference_xy_error)
                max_z_error = max(max_z_error, abs(z_error))

                altitude_is_stable = (
                    position[2] >= args.takeoff_xy_enable_altitude_m
                    and raw_target_position[2] >= args.takeoff_reference_ready_z_m
                    and abs(z_error) <= args.takeoff_stable_z_error_m
                    and abs(velocity[2]) <= args.takeoff_stable_max_vz_mps
                )
                if position[2] >= args.takeoff_xy_enable_altitude_m or xy_track_enter_count > 0:
                    airborne_seen = True
                ground_lock_active = (
                    airborne_seen
                    and
                    raw_target_position[2] <= args.ground_target_altitude_m
                    and position[2] <= args.ground_xy_disable_altitude_m
                )
                if ground_lock_active:
                    ground_lock_latched = True
                elif ground_lock_latched and not using_pre_setpoint_hold:
                    raw_target_position = [
                        position[0],
                        position[1],
                        min(raw_target_position[2], args.ground_target_altitude_m),
                    ]
                    raw_target_velocity = [0.0, 0.0, min(0.0, raw_target_velocity[2])]
                    raw_target_acceleration = [0.0, 0.0, 0.0]
                    reference_error = [raw_target_position[i] - position[i] for i in range(3)]
                    reference_xy_error = math.hypot(reference_error[0], reference_error[1])
                    z_error = reference_error[2]
                    ground_lock_active = position[2] <= args.ground_xy_disable_altitude_m
                if altitude_is_stable:
                    if altitude_stable_since is None:
                        altitude_stable_since = sample_time
                    if not xy_tracking_enabled and sample_time - altitude_stable_since >= args.takeoff_stable_s:
                        xy_tracking_enabled = True
                        xy_track_enter_count += 1
                else:
                    altitude_stable_since = None
                if (
                    not ground_lock_active
                    and raw_target_position[2] > args.ground_target_altitude_m
                    and xy_track_enter_count > 0
                    and (
                        position[2] < args.recovery_reset_altitude_m
                        or math.hypot(roll, pitch) > args.tilt_recovery_threshold_rad
                        or velocity[2] < -args.descent_recovery_threshold_mps
                        or (xy_tracking_enabled and reference_xy_error > args.xy_track_failsafe_error_m)
                    )
                    and not altitude_recovery_active
                ):
                    altitude_recovery_active = True
                    altitude_recovery_enter_count += 1
                    if reference_xy_error > args.xy_track_failsafe_error_m:
                        xy_track_failsafe_enter_count += 1
                        xy_track_failsafe_active_count += 1
                    xy_hold_position = [position[0], position[1]]
                elif altitude_recovery_active and reference_xy_error > args.xy_track_failsafe_error_m:
                    xy_track_failsafe_active_count += 1
                if altitude_recovery_active and (
                    ground_lock_active
                    or (
                        position[2] >= args.recovery_exit_altitude_m
                        and math.hypot(roll, pitch) <= args.tilt_recovery_threshold_rad * 0.5
                        and abs(velocity[2]) <= args.takeoff_stable_max_vz_mps
                    )
                ):
                    altitude_recovery_active = False
                    altitude_recovery_exit_count += 1
                    altitude_stable_since = sample_time
                disable_xy_for_low_altitude = altitude_recovery_active or (
                    position[2] < max(0.1, args.takeoff_xy_enable_altitude_m * 0.5)
                    and (not args.keep_xy_track_after_first_entry or xy_track_enter_count <= 0)
                )
                if disable_xy_for_low_altitude:
                    if xy_tracking_enabled:
                        xy_track_exit_count += 1
                    xy_tracking_enabled = False
                    altitude_stable_since = None
                if (
                    position[2] < args.recovery_reset_altitude_m
                    and xy_hold_position is not None
                    and (ground_lock_active or not args.keep_xy_track_after_first_entry)
                ):
                    xy_hold_position = [position[0], position[1]]
                if ground_lock_active:
                    if xy_tracking_enabled:
                        xy_track_exit_count += 1
                    xy_tracking_enabled = False

                mission_phase = "none"
                if mission_goal is not None and not using_pre_setpoint_hold:
                    ref_goal_dist_xy = math.hypot(raw_target_position[0] - mission_goal[0], raw_target_position[1] - mission_goal[1])
                    vehicle_goal_dist_xy = math.hypot(position[0] - mission_goal[0], position[1] - mission_goal[1])
                    if ref_goal_dist_xy <= args.mission_goal_reference_radius_m:
                        if mission_goal_reference_since is None:
                            mission_goal_reference_since = sample_time
                        if (
                            not mission_goal_capture_active
                            and args.mission_goal_capture_radius_m > 0.0
                            and vehicle_goal_dist_xy <= args.mission_goal_capture_radius_m
                            and position[2] >= args.mission_goal_capture_min_altitude_m
                        ):
                            mission_goal_capture_active = True
                            mission_goal_capture_since = sample_time
                    else:
                        mission_goal_reference_since = None
                        if not mission_goal_capture_active:
                            mission_goal_arrival_since = None
                    if mission_goal_capture_active and mission_land_start_time is None:
                        raw_target_position = [mission_goal[0], mission_goal[1], mission_goal[2]]
                        raw_target_velocity = [0.0, 0.0, 0.0]
                        raw_target_acceleration = [0.0, 0.0, 0.0]
                        target_yaw_rate = 0.0
                        reference_error = [raw_target_position[i] - position[i] for i in range(3)]
                        reference_xy_error = math.hypot(reference_error[0], reference_error[1])
                        z_error = reference_error[2]
                        if position[2] >= args.mission_goal_capture_min_altitude_m:
                            xy_tracking_enabled = True
                    if (
                        mission_goal_reference_since is not None
                        and vehicle_goal_dist_xy <= args.mission_goal_accept_radius_m
                        and (
                            abs(position[2] - mission_goal[2]) <= args.mission_goal_capture_z_error_m
                            or position[2] <= max(
                                args.mission_goal_capture_min_altitude_m,
                                args.mission_land_z_m + 0.25,
                            )
                        )
                    ):
                        if mission_goal_arrival_since is None:
                            mission_goal_arrival_since = sample_time
                    elif mission_land_start_time is None:
                        mission_goal_arrival_since = None
                    if (
                        mission_goal_arrival_since is not None
                        and sample_time - mission_goal_arrival_since >= args.mission_goal_hold_s
                        and mission_land_start_time is None
                    ):
                        mission_land_start_time = sample_time
                        if args.mission_land_lock == "goal":
                            mission_land_xy_position = [mission_goal[0], mission_goal[1]]
                        else:
                            mission_land_xy_position = [position[0], position[1]]
                    if mission_land_start_time is not None:
                        mission_phase = "auto_land"
                        altitude_recovery_active = False
                        descend = args.mission_land_rate_mps * max(0.0, sample_time - mission_land_start_time)
                        land_xy = mission_land_xy_position if mission_land_xy_position is not None else [mission_goal[0], mission_goal[1]]
                        raw_target_position = [
                            land_xy[0],
                            land_xy[1],
                            max(args.mission_land_z_m, mission_goal[2] - descend),
                        ]
                        raw_target_velocity = [0.0, 0.0, -args.mission_land_rate_mps if raw_target_position[2] > args.mission_land_z_m else 0.0]
                        raw_target_acceleration = [0.0, 0.0, 0.0]
                        reference_error = [raw_target_position[i] - position[i] for i in range(3)]
                        reference_xy_error = math.hypot(reference_error[0], reference_error[1])
                        z_error = reference_error[2]
                        ground_lock_active = (
                            airborne_seen
                            and raw_target_position[2] <= args.ground_target_altitude_m
                            and position[2] <= args.ground_xy_disable_altitude_m
                        )
                        if ground_lock_active:
                            ground_lock_latched = True
                    elif mission_goal_arrival_since is not None:
                        mission_phase = "goal_hold"
                    elif mission_goal_capture_active:
                        mission_phase = "goal_capture"
                    elif mission_goal_reference_since is not None:
                        mission_phase = "goal_reference_seen"

                if mission_phase == "auto_land":
                    control_phase = "mission_auto_land"
                elif (
                    args.xy_track_failsafe_land_after_count > 0
                    and xy_track_failsafe_active_count >= args.xy_track_failsafe_land_after_count
                ):
                    control_phase = "failsafe_land"
                elif ground_lock_active:
                    control_phase = "ground_altitude_hold"
                elif altitude_recovery_active:
                    control_phase = "altitude_recovery"
                elif xy_tracking_enabled:
                    control_phase = "xy_track"
                else:
                    control_phase = "takeoff_altitude_hold"
                control_phase_counts[control_phase] = control_phase_counts.get(control_phase, 0) + 1
                stale_truth_interval = dt > max(0.25, 5.0 / args.max_publish_hz)
                if control_phase == "failsafe_land":
                    target_position = [position[0], position[1], args.mission_land_z_m]
                    target_velocity = [0.0, 0.0, -args.mission_land_rate_mps]
                    target_acceleration = [0.0, 0.0, 0.0]
                    xy_scale = 0.0
                elif altitude_recovery_active:
                    if mission_goal_capture_active and mission_goal is not None:
                        target_position = [mission_goal[0], mission_goal[1], raw_target_position[2]]
                        target_velocity = [0.0, 0.0, raw_target_velocity[2]]
                        xy_scale = (
                            args.mission_goal_capture_xy_scale
                            if position[2] >= args.mission_goal_capture_min_altitude_m and not stale_truth_interval
                            else 0.0
                        )
                    else:
                        target_position = [position[0], position[1], raw_target_position[2]]
                        target_velocity = [0.0, 0.0, raw_target_velocity[2]]
                        xy_scale = 0.0
                    target_acceleration = [0.0, 0.0, 0.0]
                elif xy_tracking_enabled:
                    target_position = raw_target_position
                    target_velocity = raw_target_velocity
                    target_acceleration = raw_target_acceleration
                    if mission_goal_capture_active and mission_phase != "auto_land":
                        xy_scale = args.mission_goal_capture_xy_scale if not stale_truth_interval else 0.0
                    else:
                        xy_scale = 1.0 if not stale_truth_interval else 0.0
                else:
                    hold_x = position[0] if xy_hold_position is None else xy_hold_position[0]
                    hold_y = position[1] if xy_hold_position is None else xy_hold_position[1]
                    target_position = [hold_x, hold_y, raw_target_position[2]]
                    target_velocity = [0.0, 0.0, raw_target_velocity[2]]
                    target_acceleration = [0.0, 0.0, raw_target_acceleration[2]]
                    xy_scale = args.recovery_xy_brake_scale if not stale_truth_interval else 0.0
                error = [target_position[i] - position[i] for i in range(3)]
                velocity_error = [target_velocity[i] - velocity[i] for i in range(3)]
                xy_error = math.hypot(error[0], error[1])
                altitude_xy_scale = bounded(
                    (position[2] - args.low_altitude_xy_scale_start_m)
                    / (args.low_altitude_xy_scale_full_m - args.low_altitude_xy_scale_start_m),
                    0.0,
                    1.0,
                )
                xy_scale *= altitude_xy_scale
                ex = bounded(error[0], -args.xy_error_limit_m, args.xy_error_limit_m)
                ey = bounded(error[1], -args.xy_error_limit_m, args.xy_error_limit_m)
                evx = bounded(velocity_error[0], -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps)
                evy = bounded(velocity_error[1], -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps)

                base_command = bounded(
                    args.hover_command
                    + args.kp_z * z_error
                    + args.kd_z * velocity_error[2]
                    + args.ki_z * integral_z_error,
                    args.command_min,
                    args.command_max,
                )
                if ground_lock_active:
                    base_command = args.ground_motor_command
                desired_x = args.kp_x * ex + args.kd_x * evx + args.ka_x * target_acceleration[0]
                desired_y = args.kp_y * ey + args.kd_y * evy + args.ka_y * target_acceleration[1]
                roll_control_sign = args.roll_control_sign if args.roll_control_sign is not None else args.xy_control_sign
                pitch_control_sign = (
                    args.pitch_control_sign if args.pitch_control_sign is not None else args.xy_control_sign
                )
                # In the current motor/mixer path, axis probes showed that the accepted assembled plant reduces positive world-frame X/Y error with negative roll and positive pitch signs. The
                # split-axis form below is equivalent to the previous tuned
                # expressions xy_scale * (-desired_y) for roll and
                # xy_scale * (-desired_x) for pitch in the legacy axis-probe
                # wording; the current split-axis signs preserve the tuned
                # assembled-plant response when roll_control_sign=-1 and
                # pitch_control_sign=+1.
                if altitude_recovery_active:
                    roll_command = bounded(
                        -args.recovery_kp_roll * roll - args.recovery_kd_roll * roll_rate,
                        -args.recovery_attitude_command_limit,
                        args.recovery_attitude_command_limit,
                    )
                    pitch_command = bounded(
                        -args.recovery_kp_pitch * pitch - args.recovery_kd_pitch * pitch_rate,
                        -args.recovery_attitude_command_limit,
                        args.recovery_attitude_command_limit,
                    )
                else:
                    roll_command = bounded(
                        xy_scale * roll_control_sign * desired_y - args.kp_roll * roll - args.kd_roll * roll_rate,
                        -args.attitude_command_limit,
                        args.attitude_command_limit,
                    )
                    pitch_command = bounded(
                        xy_scale * pitch_control_sign * desired_x - args.kp_pitch * pitch - args.kd_pitch * pitch_rate,
                        -args.attitude_command_limit,
                        args.attitude_command_limit,
                    )
                yaw_error = angle_wrap(target_yaw - yaw)
                yaw_command = bounded(
                    args.kp_yaw * yaw_error + args.kd_yaw * (target_yaw_rate - yaw_rate),
                    -args.attitude_command_limit,
                    args.attitude_command_limit,
                )
                if ground_lock_active:
                    commands = [args.ground_motor_command for _ in range(4)]
                else:
                    commands = [
                        bounded(
                            base_command
                            + ROLL_MIX[i] * roll_command
                            + PITCH_MIX[i] * pitch_command
                            + YAW_MIX[i] * yaw_command,
                            args.command_min,
                            args.command_max,
                        )
                        for i in range(4)
                    ]
                max_command_span = max(max_command_span, max(commands) - min(commands))

                message = ControllerOutput()
                message.header.stamp = node.get_clock().now().to_msg()
                message.header.frame_id = "body_motor_order_rotor_0_1_2_3"
                message.sequence = published_count + 1
                message.vehicle_id = args.vehicle_id
                message.command_type = "normalized_motor_speed"
                message.command = [float(command) for command in commands]
                message.command_frame = "body_motor_order_rotor_0_1_2_3"
                message.mode = "planner_setpoint_position_control_pre_acceptance"
                message.status = "valid"
                message.backend = "gazebo_truth_position_controller"
                message.saturation = (
                    False
                    if ground_lock_active
                    else any(command <= args.command_min or command >= args.command_max for command in commands)
                )
                message.source_authority = "bounded_gazebo_truth_position_controller"
                node.publisher.publish(message)
                published_count += 1
                last_publish_wall = now
                last_publish_sample_time = sample_time

                last_trace = {
                    "schema": "mosim.gazebo_truth_position_controller_sample.v1",
                    "sequence": published_count,
                    "truth_time_s": sample_time,
                    "position_m": [round(item, 6) for item in position],
                    "target_position_m": [round(item, 6) for item in target_position],
                    "raw_reference_position_m": [round(item, 6) for item in raw_target_position],
                    "position_error_m": [round(item, 6) for item in error],
                    "reference_error_m": [round(item, 6) for item in reference_error],
                    "velocity_mps": [round(item, 6) for item in velocity],
                    "target_velocity_mps": [round(item, 6) for item in target_velocity],
                    "xy_error_m": round(xy_error, 6),
                    "reference_xy_error_m": round(reference_xy_error, 6),
                    "z_error_m": round(z_error, 6),
                    "setpoint_sequence": setpoint_sequence,
                    "setpoint_age_s": round(setpoint_age, 6),
                    "setpoint_age_source": setpoint_age_source,
                    "command": [round(float(command), 9) for command in commands],
                    "saturation": bool(message.saturation),
                    "base_command": round(base_command, 9),
                    "attitude_command": {
                        "roll": round(roll_command, 9),
                        "pitch": round(pitch_command, 9),
                        "yaw": round(yaw_command, 9),
                    },
                    "control_phase": control_phase,
                    "xy_tracking_enabled": bool(xy_tracking_enabled),
                    "xy_scale": round(xy_scale, 6),
                    "altitude_xy_scale": round(altitude_xy_scale, 6),
                    "xy_hold_position_m": [round(item, 6) for item in xy_hold_position] if xy_hold_position else None,
                    "ground_lock_active": bool(ground_lock_active),
                    "airborne_seen": bool(airborne_seen),
                    "ground_lock_latched": bool(ground_lock_latched),
                    "altitude_recovery_active": bool(altitude_recovery_active),
                    "stale_truth_interval": bool(stale_truth_interval),
                    "using_pre_setpoint_hold": bool(using_pre_setpoint_hold),
                    "mission_phase": mission_phase,
                    "mission_goal_m": [round(item, 6) for item in mission_goal] if mission_goal else None,
                    "mission_goal_capture_active": bool(mission_goal_capture_active),
                }
                append_jsonl(args.trace_jsonl, last_trace)

    except StopIteration:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        spin_thread.join(timeout=1.0)

    duration_s = (
        float(last_header_time - first_header_time)
        if first_header_time is not None and last_header_time is not None
        else 0.0
    )
    blockers: list[str] = []
    if node.accepted_setpoints <= 0:
        blockers.append("no_valid_external_planner_setpoint_received")
    if published_count <= 0:
        blockers.append("no_controller_output_published")
    if header_stamp_sample_count <= 0:
        blockers.append("no_header_stamp_truth_samples")
    status = "completed" if not blockers else "blocked"
    report = {
        "schema": "mosim.gazebo_truth_position_controller.v1",
        "status": status,
        "input_truth_topic": args.input_topic_name,
        "setpoint_topic": args.setpoint_topic,
        "output_topic": args.output_topic,
        "vehicle_id": args.vehicle_id,
        "expected_frame": args.expected_frame,
        "reference_mode": "external_planner_setpoint",
        "truth_clock_policy": {
            "sync_truth_to_wall_time": bool(args.sync_truth_to_wall_time),
            "truth_wall_time_factor": args.truth_wall_time_factor,
            "poll_command": args.poll_command,
            "hold_last_setpoint_when_truth_buffered": bool(args.hold_last_setpoint_when_truth_buffered),
        },
        "counts": {
            "truth_samples": truth_sample_count,
            "header_stamp_samples": header_stamp_sample_count,
            "accepted_setpoints": node.accepted_setpoints,
            "rejected_setpoints": node.rejected_setpoints,
            "published": published_count,
            "skipped_no_setpoint": skipped_no_setpoint,
            "skipped_stale_setpoint": skipped_stale_setpoint,
            "skipped_by_rate": skipped_by_rate,
        },
        "duration_s": round(duration_s, 6),
        "z_range_m": {
            "min": round(min_z, 6) if min_z is not None else None,
            "max": round(max_z, 6) if max_z is not None else None,
        },
        "tracking_errors": {
            "max_xy_error_m": round(max_xy_error, 6),
            "max_abs_z_error_m": round(max_z_error, 6),
        },
        "xy_control_sign": args.xy_control_sign,
        "roll_control_sign": args.roll_control_sign if args.roll_control_sign is not None else args.xy_control_sign,
        "pitch_control_sign": args.pitch_control_sign if args.pitch_control_sign is not None else args.xy_control_sign,
        "keep_xy_track_after_first_entry": bool(args.keep_xy_track_after_first_entry),
        "control_phase_counts": control_phase_counts,
        "control_state_transitions": {
            "xy_track_enter_count": xy_track_enter_count,
            "xy_track_exit_count": xy_track_exit_count,
            "takeoff_reference_ready_z_m": args.takeoff_reference_ready_z_m,
            "takeoff_stable_max_vz_mps": args.takeoff_stable_max_vz_mps,
            "low_altitude_xy_scale_start_m": args.low_altitude_xy_scale_start_m,
            "low_altitude_xy_scale_full_m": args.low_altitude_xy_scale_full_m,
            "recovery_xy_brake_scale": args.recovery_xy_brake_scale,
            "recovery_reset_altitude_m": args.recovery_reset_altitude_m,
            "recovery_exit_altitude_m": args.recovery_exit_altitude_m,
            "altitude_recovery_enter_count": altitude_recovery_enter_count,
            "altitude_recovery_exit_count": altitude_recovery_exit_count,
            "xy_track_failsafe_error_m": args.xy_track_failsafe_error_m,
            "xy_track_failsafe_enter_count": xy_track_failsafe_enter_count,
            "xy_track_failsafe_active_count": xy_track_failsafe_active_count,
            "xy_track_failsafe_land_after_count": args.xy_track_failsafe_land_after_count,
            "ground_xy_disable_altitude_m": args.ground_xy_disable_altitude_m,
            "ground_target_altitude_m": args.ground_target_altitude_m,
            "ground_motor_command": args.ground_motor_command,
            "airborne_seen": bool(airborne_seen),
            "ground_lock_latched": bool(ground_lock_latched),
            "publish_hold_before_setpoint": bool(args.publish_hold_before_setpoint),
            "pre_setpoint_hold_z": args.pre_setpoint_hold_z,
            "takeoff_hold_setpoint_until_stable": bool(args.takeoff_hold_setpoint_until_stable),
            "mission_goal_m": mission_goal,
            "mission_goal_reference_radius_m": args.mission_goal_reference_radius_m,
            "mission_goal_capture_radius_m": args.mission_goal_capture_radius_m,
            "mission_goal_capture_min_altitude_m": args.mission_goal_capture_min_altitude_m,
            "mission_goal_capture_xy_scale": args.mission_goal_capture_xy_scale,
            "mission_goal_capture_z_error_m": args.mission_goal_capture_z_error_m,
            "mission_goal_accept_radius_m": args.mission_goal_accept_radius_m,
            "mission_goal_hold_s": args.mission_goal_hold_s,
            "mission_land_z_m": args.mission_land_z_m,
            "mission_land_rate_mps": args.mission_land_rate_mps,
            "mission_goal_reference_since_s": mission_goal_reference_since,
            "mission_goal_capture_active": mission_goal_capture_active,
            "mission_goal_capture_since_s": mission_goal_capture_since,
            "mission_goal_arrival_since_s": mission_goal_arrival_since,
            "mission_land_start_time_s": mission_land_start_time,
        },
        "max_command_span": round(max_command_span, 9),
        "last_sample": last_trace,
        "poll_diagnostics": poll_diagnostics,
        "blockers": blockers,
        "outputs": {
            "trace_jsonl": rel(project_path(args.trace_jsonl)) if args.trace_jsonl else "",
        },
        "claim_boundary": [
            "bounded single-UAV Gazebo truth-feedback position-control pre-acceptance only",
            "ControllerOutput is published only from valid, fresh external /mosim/planner/setpoint samples",
            "no final closed_loop, competition controller performance, planner_ready, or multi-UAV readiness is claimed",
        ],
    }
    write_json(args.output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 1


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        validate_args(args)
        if args.dry_run:
            report = dry_run_report(args)
            write_json(args.output_json, report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        return run_controller(args)
    except Exception as exc:
        report = {
            "schema": "mosim.gazebo_truth_position_controller.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
        write_json(getattr(args, "output_json", None), report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
