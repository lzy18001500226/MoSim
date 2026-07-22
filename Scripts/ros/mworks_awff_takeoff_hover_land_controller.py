#!/usr/bin/env python3
"""MWORKS AWFF equation-controller wrapper for Gazebo takeoff-hover-land.

This is a behavior-equivalent Python runtime wrapper for
Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_FullControllerEquation_Sysblock.mo.
It ports the Sysblock equations into the same Gazebo ControllerOutput ABI used
by the runtime plant gate. It is not generated C code and must not be claimed
as final SIL/codegen evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HELPERS = ROOT / "Scripts" / "ros"
if str(HELPERS) not in sys.path:
    sys.path.insert(0, str(HELPERS))

from gazebo_truth_takeoff_hover_land_controller import (  # noqa: E402
    angle_wrap,
    append_jsonl,
    bounded,
    has_timed_truth,
    iter_stdin_message_chunks,
    parse_truth_samples,
    project_path,
    rel,
    sample_orientation,
    target_altitude,
    write_json,
)


MWORKS_SOURCE_MODEL = "Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_FullControllerEquation_Sysblock.mo"
SPIN_SIGN = [1.0, -1.0, 1.0, -1.0]
# MWORKS controller/source order is Dronefixed1..4:
# front-right, front-left, back-left, back-right.
# Gazebo actuator order for sunray150_assembled is rotor_0..3:
# front-right, back-left, front-left, back-right.
MWORKS_TO_GAZEBO_ACTUATOR_ORDER = [0, 2, 1, 3]


@dataclass
class AwffState:
    x_error_filter: float = 0.0
    y_error_filter: float = 0.0
    z_error_filter: float = 0.0
    z_integral: float = 0.0
    roll_error_filter: float = 0.0
    pitch_error_filter: float = 0.0


@dataclass(frozen=True)
class AwffParams:
    kp_x: float = 1.65
    kd_x: float = 1.0
    kp_y: float = 1.65
    kd_y: float = 1.0
    kp_z: float = 8.0
    ki_z: float = 6.0
    kd_z: float = 4.0
    kff_z: float = 0.35
    kp_roll: float = 14.142
    kd_roll: float = 1.70
    kp_pitch: float = 14.142
    kd_pitch: float = 1.70
    kp_yaw: float = 5.0
    roll_pitch_cmd_limit: float = 12.0 / 57.3
    attitude_cmd_limit: float = 6.5
    yaw_cmd_limit: float = 6.5
    output_limit: float = 20.0
    position_derivative_filter_T: float = 0.05
    altitude_derivative_filter_T: float = 0.08
    attitude_derivative_filter_T: float = 0.03


def awff_step(
    state: AwffState,
    params: AwffParams,
    *,
    dt: float,
    x_error: float,
    y_error: float,
    z_error: float,
    z_ref_rate: float,
    roll_mea: float,
    pitch_mea: float,
    yaw_mea: float,
    yaw_ref: float,
) -> dict[str, Any]:
    x_error_rate = (x_error - state.x_error_filter) / params.position_derivative_filter_T
    y_error_rate = (y_error - state.y_error_filter) / params.position_derivative_filter_T
    z_error_rate = (z_error - state.z_error_filter) / params.altitude_derivative_filter_T

    pitch_ref_raw = 0.1 * (params.kp_x * x_error + params.kd_x * x_error_rate)
    roll_ref_raw = 0.1 * (params.kp_y * y_error + params.kd_y * y_error_rate)
    thrust_ref_raw = (
        params.kp_z * z_error
        + params.ki_z * state.z_integral
        + params.kd_z * z_error_rate
        + params.kff_z * z_ref_rate
    )

    pitch_ref = bounded(pitch_ref_raw, -params.roll_pitch_cmd_limit, params.roll_pitch_cmd_limit)
    roll_ref = bounded(roll_ref_raw, -params.roll_pitch_cmd_limit, params.roll_pitch_cmd_limit)
    thrust_ref = bounded(thrust_ref_raw, -params.output_limit, params.output_limit)
    if abs(thrust_ref_raw) < params.output_limit or z_error * thrust_ref_raw < 0.0:
        state.z_integral += z_error * max(0.0, dt)

    roll_error = roll_ref + roll_mea
    pitch_error = pitch_ref - pitch_mea
    yaw_error = angle_wrap(yaw_ref - yaw_mea)
    roll_error_rate = (roll_error - state.roll_error_filter) / params.attitude_derivative_filter_T
    pitch_error_rate = (pitch_error - state.pitch_error_filter) / params.attitude_derivative_filter_T

    roll_cmd_raw = params.kp_roll * roll_error + params.kd_roll * roll_error_rate
    pitch_cmd_raw = params.kp_pitch * pitch_error + params.kd_pitch * pitch_error_rate
    yaw_cmd_raw = params.kp_yaw * yaw_error

    roll_cmd = bounded(roll_cmd_raw, -params.attitude_cmd_limit, params.attitude_cmd_limit)
    pitch_cmd = bounded(pitch_cmd_raw, -params.attitude_cmd_limit, params.attitude_cmd_limit)
    yaw_cmd = bounded(yaw_cmd_raw, -params.yaw_cmd_limit, params.yaw_cmd_limit)

    yaw_mix = 0.707 * yaw_cmd
    pitch_mix = 0.707 * pitch_cmd
    roll_mix = 0.707 * roll_cmd

    u1_raw = thrust_ref + (-yaw_mix - pitch_mix + roll_mix)
    u2_raw = -(thrust_ref + (yaw_mix - pitch_mix - roll_mix))
    u3_raw = thrust_ref + (-yaw_mix + pitch_mix - roll_mix)
    u4_raw = -(thrust_ref + (yaw_mix + pitch_mix + roll_mix))
    outputs = [bounded(item, -params.output_limit, params.output_limit) for item in (u1_raw, u2_raw, u3_raw, u4_raw)]

    if dt > 0.0:
        state.x_error_filter += dt * (x_error - state.x_error_filter) / params.position_derivative_filter_T
        state.y_error_filter += dt * (y_error - state.y_error_filter) / params.position_derivative_filter_T
        state.z_error_filter += dt * (z_error - state.z_error_filter) / params.altitude_derivative_filter_T
        state.roll_error_filter += dt * (roll_error - state.roll_error_filter) / params.attitude_derivative_filter_T
        state.pitch_error_filter += dt * (pitch_error - state.pitch_error_filter) / params.attitude_derivative_filter_T

    return {
        "outputs": outputs,
        "refs": {
            "roll_ref": roll_ref,
            "pitch_ref": pitch_ref,
            "thrust_ref": thrust_ref,
            "roll_ref_raw": roll_ref_raw,
            "pitch_ref_raw": pitch_ref_raw,
            "thrust_ref_raw": thrust_ref_raw,
        },
        "errors": {
            "roll_error": roll_error,
            "pitch_error": pitch_error,
            "yaw_error": yaw_error,
            "x_error_rate": x_error_rate,
            "y_error_rate": y_error_rate,
            "z_error_rate": z_error_rate,
        },
        "commands": {"roll_cmd": roll_cmd, "pitch_cmd": pitch_cmd, "yaw_cmd": yaw_cmd},
    }


def mworks_delta_to_normalized(
    outputs: list[float],
    *,
    hover_command: float,
    legacy_hover_motor_speed_cmd: float,
    gazebo_delta_scale: float,
    command_min: float,
    command_max: float,
) -> list[float]:
    delta_gain = hover_command / legacy_hover_motor_speed_cmd * gazebo_delta_scale
    commands: list[float] = []
    for index, output in enumerate(outputs):
        signed_normalized = SPIN_SIGN[index] * hover_command + output * delta_gain
        commands.append(bounded(abs(signed_normalized), command_min, command_max))
    return [commands[index] for index in MWORKS_TO_GAZEBO_ACTUATOR_ORDER]


def awff_control_to_gazebo_mixer(
    step: dict[str, Any],
    *,
    hover_command: float,
    thrust_scale: float,
    vz_damping_scale: float,
    vz_mps: float,
    vx_mps: float,
    vy_mps: float,
    xy_velocity_damping_scale: float,
    attitude_scale: float,
    yaw_scale: float,
    command_min: float,
    command_max: float,
) -> list[float]:
    """Project AWFF control axes onto the accepted Gazebo motor mixer."""
    thrust = float(step["refs"]["thrust_ref"])
    roll_cmd = float(step["commands"]["roll_cmd"])
    pitch_cmd = float(step["commands"]["pitch_cmd"])
    yaw_cmd = float(step["commands"]["yaw_cmd"])
    base = hover_command + thrust_scale * thrust - vz_damping_scale * vz_mps
    # AWFF roll sign follows the MWORKS motor layout; the accepted Gazebo
    # assembled plant needs the split-axis sign identified by prior probes.
    gazebo_roll = attitude_scale * roll_cmd + xy_velocity_damping_scale * vy_mps
    gazebo_pitch = attitude_scale * pitch_cmd - xy_velocity_damping_scale * vx_mps
    gazebo_yaw = -yaw_scale * yaw_cmd
    roll_mix = [-1.0, 1.0, 1.0, -1.0]
    pitch_mix = [-1.0, 1.0, -1.0, 1.0]
    yaw_mix = [-1.0, -1.0, 1.0, 1.0]
    return [
        bounded(
            base + roll_mix[i] * gazebo_roll + pitch_mix[i] * gazebo_pitch + yaw_mix[i] * gazebo_yaw,
            command_min,
            command_max,
        )
        for i in range(4)
    ]


def awff_ref_to_gazebo_adapter(
    step: dict[str, Any],
    *,
    hover_command: float,
    thrust_scale: float,
    vz_damping_scale: float,
    vz_mps: float,
    roll_mps: float,
    pitch_mps: float,
    roll_mea: float,
    pitch_mea: float,
    yaw_cmd_scale: float,
    attitude_kp: float,
    attitude_kd: float,
    attitude_limit: float,
    roll_ref_sign: float,
    pitch_ref_sign: float,
    command_min: float,
    command_max: float,
) -> list[float]:
    """Use AWFF references through a Gazebo-calibrated attitude adapter.

    The MWORKS AWFF model was designed around the MWORKS plant and motor
    semantics. This adapter keeps the AWFF outer-loop references and thrust
    term, then applies the same small normalized-motor command scale used by
    the accepted Gazebo plant sanity controller.
    """
    thrust = float(step["refs"]["thrust_ref"])
    roll_ref = roll_ref_sign * float(step["refs"]["roll_ref"])
    pitch_ref = pitch_ref_sign * float(step["refs"]["pitch_ref"])
    yaw_cmd = float(step["commands"]["yaw_cmd"])
    base = hover_command + thrust_scale * thrust - vz_damping_scale * vz_mps
    roll_command = bounded(
        attitude_kp * (roll_ref - roll_mea) - attitude_kd * roll_mps,
        -attitude_limit,
        attitude_limit,
    )
    pitch_command = bounded(
        attitude_kp * (pitch_ref - pitch_mea) - attitude_kd * pitch_mps,
        -attitude_limit,
        attitude_limit,
    )
    yaw_command = bounded(yaw_cmd_scale * yaw_cmd, -attitude_limit, attitude_limit)
    roll_mix = [-1.0, 1.0, 1.0, -1.0]
    pitch_mix = [-1.0, 1.0, -1.0, 1.0]
    yaw_mix = [-1.0, -1.0, 1.0, 1.0]
    return [
        bounded(
            base + roll_mix[i] * roll_command + pitch_mix[i] * pitch_command + yaw_mix[i] * yaw_command,
            command_min,
            command_max,
        )
        for i in range(4)
    ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic-name", default="/world/sunray150_takeoff_hover_land_plant_sanity/dynamic_pose/info")
    parser.add_argument("--output-topic", default="/mosim/sunray150/controller_output")
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--hover-altitude-m", type=float, default=0.6)
    parser.add_argument("--landed-altitude-m", type=float, default=0.12)
    parser.add_argument("--takeoff-duration-s", type=float, default=4.0)
    parser.add_argument("--hover-duration-s", type=float, default=4.0)
    parser.add_argument("--land-duration-s", type=float, default=4.0)
    parser.add_argument("--settle-duration-s", type=float, default=1.0)
    parser.add_argument("--hover-command", type=float, default=0.0556)
    parser.add_argument("--command-min", type=float, default=0.0528)
    parser.add_argument("--command-max", type=float, default=0.0585)
    parser.add_argument("--land-command-max", type=float, default=0.0554)
    parser.add_argument("--legacy-hover-motor-speed-cmd", type=float, default=13.985413115099604)
    parser.add_argument("--controller-sample-time-s", type=float, default=0.01)
    parser.add_argument("--mapping-mode", choices=("mworks_motor_delta", "gazebo_axis_mixer", "gazebo_ref_adapter"), default="gazebo_axis_mixer")
    parser.add_argument("--gazebo-delta-scale", type=float, default=0.020)
    parser.add_argument("--gazebo-thrust-scale", type=float, default=0.00010)
    parser.add_argument("--gazebo-vz-damping-scale", type=float, default=0.0022)
    parser.add_argument("--gazebo-attitude-scale", type=float, default=0.00018)
    parser.add_argument("--gazebo-xy-velocity-damping-scale", type=float, default=0.0010)
    parser.add_argument("--gazebo-yaw-scale", type=float, default=0.0)
    parser.add_argument("--gazebo-ref-attitude-kp", type=float, default=0.010)
    parser.add_argument("--gazebo-ref-attitude-kd", type=float, default=0.002)
    parser.add_argument("--gazebo-ref-attitude-limit", type=float, default=0.002)
    parser.add_argument("--gazebo-roll-ref-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--gazebo-pitch-ref-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--ground-lock-altitude-m", type=float, default=0.16)
    parser.add_argument("--ground-lock-command", type=float, default=0.0)
    parser.add_argument("--landing-attitude-disable-altitude-m", type=float, default=0.35)
    parser.add_argument("--landing-xy-disable-altitude-m", type=float, default=0.45)
    parser.add_argument("--x-error-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--y-error-sign", type=float, choices=(-1.0, 1.0), default=-1.0)
    parser.add_argument("--roll-measurement-sign", type=float, choices=(-1.0, 1.0), default=-1.0)
    parser.add_argument("--pitch-measurement-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--yaw-measurement-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--low-altitude-xy-scale-start-m", type=float, default=0.35)
    parser.add_argument("--low-altitude-xy-scale-full-m", type=float, default=0.85)
    parser.add_argument("--enable-xy-hold", action="store_true")
    parser.add_argument("--xy-error-limit-m", type=float, default=0.8)
    parser.add_argument("--max-publish-hz", type=float, default=20.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    return parser.parse_args(argv)


def run_controller(args: argparse.Namespace) -> int:
    try:
        import rclpy
        from mosim_msgs.msg import ControllerOutput
        from rclpy.node import Node
    except Exception as exc:
        report = {"schema": "mosim.mworks_awff_takeoff_hover_land_controller.v1", "status": "blocked", "error": f"{type(exc).__name__}: {exc}"}
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    class Controller(Node):
        def __init__(self) -> None:
            super().__init__("mosim_mworks_awff_takeoff_hover_land_controller")
            self.publisher = self.create_publisher(ControllerOutput, args.output_topic, 10)

    rclpy.init()
    node = Controller()
    awff_state = AwffState()
    awff_params = AwffParams()
    published = 0
    skipped = 0
    chunks = 0
    truth_samples = 0
    header_samples = 0
    first_time: float | None = None
    last_time: float | None = None
    last_sample_time: float | None = None
    start_altitude: float | None = None
    target_xy: list[float] | None = None
    target_yaw: float | None = None
    last_position: list[float] | None = None
    last_roll: float | None = None
    last_pitch: float | None = None
    last_yaw: float | None = None
    last_publish_wall = 0.0
    phase_counts: dict[str, int] = {}
    min_z: float | None = None
    max_z: float | None = None
    max_xy_error = 0.0
    max_tilt = 0.0
    min_command: float | None = None
    max_command: float | None = None
    total_duration = args.takeoff_duration_s + args.hover_duration_s + args.land_duration_s + args.settle_duration_s

    try:
        for chunk in iter_stdin_message_chunks(sys.stdin):
            chunks += 1
            for sample in parse_truth_samples(chunk, model_name=args.model_name, topic=args.input_topic_name, frame_id=args.frame_id):
                truth_samples += 1
                if not has_timed_truth(sample):
                    continue
                header_samples += 1
                sample_time = float(sample["time"])
                position = [float(item) for item in sample["position_m"]]
                roll, pitch, yaw = sample_orientation(sample)
                if first_time is None:
                    first_time = sample_time
                    start_altitude = position[2]
                    target_xy = [position[0], position[1]]
                    target_yaw = yaw
                last_time = sample_time
                dt = 0.0 if last_sample_time is None or sample_time <= last_sample_time else sample_time - last_sample_time
                elapsed = sample_time - first_time
                target_z, phase = target_altitude(
                    elapsed,
                    start_altitude=float(start_altitude),
                    hover_altitude=args.hover_altitude_m,
                    takeoff_s=args.takeoff_duration_s,
                    hover_s=args.hover_duration_s,
                    land_s=args.land_duration_s,
                    landed_altitude=args.landed_altitude_m,
                )
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
                z_ref_rate = 0.0
                if elapsed < args.takeoff_duration_s:
                    z_ref_rate = (args.hover_altitude_m - float(start_altitude)) / args.takeoff_duration_s
                elif elapsed < args.takeoff_duration_s + args.hover_duration_s:
                    z_ref_rate = 0.0
                elif elapsed < args.takeoff_duration_s + args.hover_duration_s + args.land_duration_s:
                    z_ref_rate = (args.landed_altitude_m - args.hover_altitude_m) / args.land_duration_s

                min_z = position[2] if min_z is None else min(min_z, position[2])
                max_z = position[2] if max_z is None else max(max_z, position[2])
                max_tilt = max(max_tilt, math.hypot(roll, pitch))
                vx = vy = vz = 0.0
                roll_rate = pitch_rate = yaw_rate = 0.0
                if last_sample_time is not None and last_position is not None and sample_time > last_sample_time:
                    sample_dt = sample_time - last_sample_time
                    vx = (position[0] - last_position[0]) / sample_dt
                    vy = (position[1] - last_position[1]) / sample_dt
                    vz = (position[2] - last_position[2]) / sample_dt
                    if last_roll is not None and last_pitch is not None and last_yaw is not None:
                        roll_rate = angle_wrap(roll - last_roll) / sample_dt
                        pitch_rate = angle_wrap(pitch - last_pitch) / sample_dt
                        yaw_rate = angle_wrap(yaw - last_yaw) / sample_dt
                x_error_raw = float(target_xy[0]) - position[0]
                y_error_raw = float(target_xy[1]) - position[1]
                z_error = target_z - position[2]
                max_xy_error = max(max_xy_error, math.hypot(x_error_raw, y_error_raw))
                altitude_xy_scale = bounded(
                    (position[2] - args.low_altitude_xy_scale_start_m)
                    / (args.low_altitude_xy_scale_full_m - args.low_altitude_xy_scale_start_m),
                    0.0,
                    1.0,
                ) if args.enable_xy_hold else 0.0
                landing_xy_disabled = phase in {"land", "settle"} and position[2] <= args.landing_xy_disable_altitude_m
                if landing_xy_disabled:
                    altitude_xy_scale = 0.0
                x_error = args.x_error_sign * altitude_xy_scale * bounded(x_error_raw, -args.xy_error_limit_m, args.xy_error_limit_m)
                y_error = args.y_error_sign * altitude_xy_scale * bounded(y_error_raw, -args.xy_error_limit_m, args.xy_error_limit_m)

                if args.controller_sample_time_s <= 0.0:
                    raise ValueError("--controller-sample-time-s must be positive")
                substep_count = max(1, int(math.ceil(dt / args.controller_sample_time_s))) if dt > 0.0 else 1
                substep_dt = dt / substep_count if dt > 0.0 else 0.0
                step: dict[str, Any] | None = None
                for _ in range(substep_count):
                    step = awff_step(
                        awff_state,
                        awff_params,
                        dt=substep_dt,
                        x_error=x_error,
                        y_error=y_error,
                        z_error=z_error,
                        z_ref_rate=z_ref_rate,
                        roll_mea=args.roll_measurement_sign * roll,
                        pitch_mea=args.pitch_measurement_sign * pitch,
                        yaw_mea=args.yaw_measurement_sign * yaw,
                        yaw_ref=float(target_yaw),
                    )
                assert step is not None
                phase_command_max = min(args.command_max, args.land_command_max) if phase in {"land", "settle"} else args.command_max
                if args.mapping_mode == "mworks_motor_delta":
                    attitude_scale = 0.0
                    xy_velocity_damping_scale = 0.0
                    commands = mworks_delta_to_normalized(
                        step["outputs"],
                        hover_command=args.hover_command,
                        legacy_hover_motor_speed_cmd=args.legacy_hover_motor_speed_cmd,
                        gazebo_delta_scale=args.gazebo_delta_scale,
                        command_min=args.command_min,
                        command_max=phase_command_max,
                    )
                elif args.mapping_mode == "gazebo_axis_mixer":
                    attitude_scale = args.gazebo_attitude_scale
                    xy_velocity_damping_scale = args.gazebo_xy_velocity_damping_scale
                    if phase in {"land", "settle"} and position[2] <= args.landing_attitude_disable_altitude_m:
                        attitude_scale = 0.0
                        xy_velocity_damping_scale = 0.0
                    commands = awff_control_to_gazebo_mixer(
                        step,
                        hover_command=args.hover_command,
                        thrust_scale=args.gazebo_thrust_scale,
                        vz_damping_scale=args.gazebo_vz_damping_scale,
                        vz_mps=vz,
                        vx_mps=vx,
                        vy_mps=vy,
                        xy_velocity_damping_scale=xy_velocity_damping_scale,
                        attitude_scale=attitude_scale,
                        yaw_scale=args.gazebo_yaw_scale,
                        command_min=args.command_min,
                        command_max=phase_command_max,
                    )
                else:
                    attitude_scale = args.gazebo_ref_attitude_kp
                    xy_velocity_damping_scale = 0.0
                    if phase in {"land", "settle"} and position[2] <= args.landing_attitude_disable_altitude_m:
                        attitude_scale = 0.0
                    commands = awff_ref_to_gazebo_adapter(
                        step,
                        hover_command=args.hover_command,
                        thrust_scale=args.gazebo_thrust_scale,
                        vz_damping_scale=args.gazebo_vz_damping_scale,
                        vz_mps=vz,
                        roll_mps=roll_rate,
                        pitch_mps=pitch_rate,
                        roll_mea=roll,
                        pitch_mea=pitch,
                        yaw_cmd_scale=args.gazebo_yaw_scale,
                        attitude_kp=attitude_scale,
                        attitude_kd=args.gazebo_ref_attitude_kd,
                        attitude_limit=args.gazebo_ref_attitude_limit,
                        roll_ref_sign=args.gazebo_roll_ref_sign,
                        pitch_ref_sign=args.gazebo_pitch_ref_sign,
                        command_min=args.command_min,
                        command_max=phase_command_max,
                    )
                ground_lock_active = phase in {"land", "settle"} and position[2] <= args.ground_lock_altitude_m
                if ground_lock_active:
                    commands = [args.ground_lock_command] * 4
                last_sample_time = sample_time
                last_position = position
                last_roll = roll
                last_pitch = pitch
                last_yaw = yaw

                now = time.time()
                if published > 0 and now - last_publish_wall < 1.0 / args.max_publish_hz:
                    skipped += 1
                    continue
                message = ControllerOutput()
                message.header.stamp = node.get_clock().now().to_msg()
                message.header.frame_id = "body_motor_order_rotor_0_1_2_3"
                message.sequence = published + 1
                message.vehicle_id = args.vehicle_id
                message.command_type = "normalized_motor_speed"
                message.command = [float(item) for item in commands]
                message.command_frame = "body_motor_order_rotor_0_1_2_3"
                message.mode = f"mworks_awff_takeoff_hover_land_{phase}"
                message.status = "valid"
                message.backend = "mworks_awff_equation_behavior_wrapper"
                message.saturation = any(command <= args.command_min or command >= phase_command_max for command in commands)
                message.source_authority = "MWORKS_AWFF_FullControllerEquation_Sysblock_behavior_equivalent_wrapper"
                node.publisher.publish(message)
                rclpy.spin_once(node, timeout_sec=0.01)
                published += 1
                last_publish_wall = now
                min_command = min(commands) if min_command is None else min(min_command, min(commands))
                max_command = max(commands) if max_command is None else max(max_command, max(commands))
                append_jsonl(
                    args.trace_jsonl,
                    {
                        "schema": "mosim.mworks_awff_takeoff_hover_land_controller_sample.v1",
                        "sequence": published,
                        "truth_time_s": round(sample_time, 6),
                        "elapsed_s": round(elapsed, 6),
                        "phase": phase,
                        "position_m": [round(item, 6) for item in position],
                        "target_position_m": [round(float(target_xy[0]), 6), round(float(target_xy[1]), 6), round(target_z, 6)],
                        "position_error_m": [round(x_error_raw, 6), round(y_error_raw, 6), round(z_error, 6)],
                        "euler_rpy_rad": [round(roll, 6), round(pitch, 6), round(yaw, 6)],
                        "velocity_mps": [round(vx, 6), round(vy, 6), round(vz, 6)],
                        "angular_rate_rpy_radps": [round(roll_rate, 6), round(pitch_rate, 6), round(yaw_rate, 6)],
                        "awff_inputs": {
                            "x_error": round(x_error, 6),
                            "y_error": round(y_error, 6),
                            "z_error": round(z_error, 6),
                            "z_ref_rate": round(z_ref_rate, 6),
                            "roll_mea": round(args.roll_measurement_sign * roll, 6),
                            "pitch_mea": round(args.pitch_measurement_sign * pitch, 6),
                            "yaw_mea": round(args.yaw_measurement_sign * yaw, 6),
                            "yaw_ref": round(float(target_yaw), 6),
                        },
                        "awff_outputs": [round(item, 6) for item in step["outputs"]],
                        "awff_axis_commands": {
                            key: round(float(value), 6)
                            for key, value in step["commands"].items()
                        },
                        "awff_refs": {
                            key: round(float(value), 6)
                            for key, value in step["refs"].items()
                        },
                        "command": [round(item, 9) for item in commands],
                        "mapping_mode": args.mapping_mode,
                        "controller_sample_time_s": args.controller_sample_time_s,
                        "controller_substep_count": substep_count,
                        "gazebo_delta_scale": args.gazebo_delta_scale,
                        "gazebo_thrust_scale": args.gazebo_thrust_scale,
                        "gazebo_vz_damping_scale": args.gazebo_vz_damping_scale,
                        "gazebo_xy_velocity_damping_scale": xy_velocity_damping_scale,
                        "gazebo_attitude_scale": attitude_scale,
                        "landing_attitude_disabled": bool(attitude_scale == 0.0 and phase in {"land", "settle"}),
                        "landing_xy_disabled": bool(landing_xy_disabled),
                        "ground_lock_active": bool(ground_lock_active),
                    },
                )
                if elapsed >= total_duration:
                    raise StopIteration
    except StopIteration:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

    duration = 0.0 if first_time is None or last_time is None else last_time - first_time
    status = "completed" if published > 0 and header_samples > 0 else "blocked"
    report = {
        "schema": "mosim.mworks_awff_takeoff_hover_land_controller.v1",
        "status": status,
        "source_model": MWORKS_SOURCE_MODEL,
        "runtime_kind": "behavior_equivalent_python_wrapper",
        "input_topic_name": args.input_topic_name,
        "output_topic": args.output_topic,
        "model_name": args.model_name,
        "vehicle_id": args.vehicle_id,
        "mapping": {
            "mworks_semantics": "signed hover motor speed plus Sysblock delta output",
            "gazebo_command_type": "normalized_motor_speed",
            "legacy_hover_motor_speed_cmd": args.legacy_hover_motor_speed_cmd,
            "hover_command": args.hover_command,
            "gazebo_delta_scale": args.gazebo_delta_scale,
            "controller_sample_time_s": args.controller_sample_time_s,
            "mapping_mode": args.mapping_mode,
            "gazebo_thrust_scale": args.gazebo_thrust_scale,
            "gazebo_vz_damping_scale": args.gazebo_vz_damping_scale,
            "gazebo_xy_velocity_damping_scale": args.gazebo_xy_velocity_damping_scale,
            "gazebo_attitude_scale": args.gazebo_attitude_scale,
            "gazebo_yaw_scale": args.gazebo_yaw_scale,
            "gazebo_ref_attitude_kp": args.gazebo_ref_attitude_kp,
            "gazebo_ref_attitude_kd": args.gazebo_ref_attitude_kd,
            "gazebo_ref_attitude_limit": args.gazebo_ref_attitude_limit,
            "gazebo_roll_ref_sign": args.gazebo_roll_ref_sign,
            "gazebo_pitch_ref_sign": args.gazebo_pitch_ref_sign,
            "ground_lock_altitude_m": args.ground_lock_altitude_m,
            "ground_lock_command": args.ground_lock_command,
            "landing_xy_disable_altitude_m": args.landing_xy_disable_altitude_m,
            "spin_sign": SPIN_SIGN,
        },
        "profile": {
            "hover_altitude_m": args.hover_altitude_m,
            "landed_altitude_m": args.landed_altitude_m,
            "takeoff_duration_s": args.takeoff_duration_s,
            "hover_duration_s": args.hover_duration_s,
            "land_duration_s": args.land_duration_s,
            "settle_duration_s": args.settle_duration_s,
        },
        "counts": {
            "chunks": chunks,
            "truth_samples": truth_samples,
            "header_stamp_samples": header_samples,
            "published": published,
            "skipped_by_rate": skipped,
            "phase_counts": phase_counts,
        },
        "duration_s": round(duration, 6),
        "z_range_m": {"min": round(min_z, 6) if min_z is not None else None, "max": round(max_z, 6) if max_z is not None else None},
        "max_xy_error_m": round(max_xy_error, 6),
        "max_tilt_rad": round(max_tilt, 6),
        "command_range": {"min": round(min_command, 9) if min_command is not None else None, "max": round(max_command, 9) if max_command is not None else None},
        "outputs": {"trace_jsonl": rel(project_path(args.trace_jsonl)) if args.trace_jsonl else ""},
        "claim_boundary": [
            "ports AWFF_FullControllerEquation_Sysblock equations into a Python ControllerOutput runtime wrapper",
            "uses Gazebo-calibrated hover trim and the accepted Gazebo mixer for the sunray150_assembled plant",
            "not generated C/C++ code and not a completed SIL equivalence gate",
            "does not prove planner_ready, final closed_loop acceptance, final competition controller performance, UE acceptance, or multi-UAV readiness",
        ],
    }
    write_json(args.output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 1


def main(argv: list[str]) -> int:
    return run_controller(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
