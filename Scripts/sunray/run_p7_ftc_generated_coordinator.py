#!/usr/bin/env python3
"""Run the official P7 generated FTC core against same-run Gazebo actuator data."""

from __future__ import annotations

import argparse
import csv
import ctypes
import json
import time
from pathlib import Path

import rospy
from mavros_msgs.msg import ExtendedState, State
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import TakeoffLand
from std_msgs.msg import Float64MultiArray

from p7_ftc_runtime_math import wrench_from_motors


class GeneratedInputs(ctypes.Structure):
    _fields_ = [(name, ctypes.c_double) for name in (
        "mode_id", "dt", "desired_thrust", "desired_roll", "desired_pitch",
        "desired_yaw", "response_1", "response_2", "response_3", "response_4",
        "airborne", "altitude", "enable", "reset")]


class GeneratedOutputs(ctypes.Structure):
    _fields_ = [(name, ctypes.c_double) for name in (
        "motor_1", "motor_2", "motor_3", "motor_4", "eta_1", "eta_2",
        "eta_3", "eta_4", "achieved_thrust", "achieved_roll",
        "achieved_pitch", "achieved_yaw", "residual_norm", "isolated_mask",
        "fault_count", "action", "allocation_saturated", "status_code")]


class Coordinator:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.telemetry = None
        self.odom = None
        self.extended = None
        self.state = None
        self.command_pub = rospy.Publisher(args.command_topic, Float64MultiArray, queue_size=5)
        self.takeoff_land_pub = rospy.Publisher(args.takeoff_land_topic, TakeoffLand, queue_size=5)
        rospy.Subscriber(args.telemetry_topic, Float64MultiArray, self._telemetry_cb, queue_size=20)
        rospy.Subscriber(args.odom_topic, Odometry, self._odom_cb, queue_size=10)
        rospy.Subscriber(args.extended_state_topic, ExtendedState, self._extended_cb, queue_size=10)
        rospy.Subscriber(args.state_topic, State, self._state_cb, queue_size=10)

        self.lib = ctypes.CDLL(str(args.generated_library))
        self.inputs = GeneratedInputs.in_dll(self.lib, "ol_cfunction_sysblockGbIn")
        self.outputs = GeneratedOutputs.in_dll(self.lib, "rol_cfunction_sysblockGbOut")
        self.lib.Init()

    def _telemetry_cb(self, msg): self.telemetry = list(msg.data)
    def _odom_cb(self, msg): self.odom = msg
    def _extended_cb(self, msg): self.extended = msg
    def _state_cb(self, msg): self.state = msg

    def publish_command(self, eta: list[float], override: list[float] | None = None) -> None:
        msg = Float64MultiArray()
        msg.data = [1.0 if override is not None else 0.0, *eta,
                    *(override if override is not None else [0.0] * 4)]
        self.command_pub.publish(msg)

    def publish_takeoff_land(self, command: int) -> None:
        msg = TakeoffLand()
        msg.takeoff_land_cmd = command
        self.takeoff_land_pub.publish(msg)

    def wait_ready(self) -> None:
        deadline = time.monotonic() + self.args.ready_timeout_s
        rate = rospy.Rate(20)
        while not rospy.is_shutdown() and time.monotonic() < deadline:
            if (self.telemetry and len(self.telemetry) == 18 and self.odom and
                    self.extended and self.state and self.state.connected and
                    self.command_pub.get_num_connections() > 0 and
                    self.takeoff_land_pub.get_num_connections() > 0):
                return
            rate.sleep()
        raise RuntimeError(
            "FTC telemetry/MAVROS/plugin/px4ctrl publisher readiness timeout")

    def request_takeoff(self) -> None:
        deadline = time.monotonic() + self.args.takeoff_timeout_s
        rate = rospy.Rate(10)
        while not rospy.is_shutdown() and time.monotonic() < deadline:
            self.publish_takeoff_land(TakeoffLand.TAKEOFF)
            if (self.state.armed or self.extended.landed_state in (
                    ExtendedState.LANDED_STATE_TAKEOFF,
                    ExtendedState.LANDED_STATE_IN_AIR)):
                return
            rate.sleep()
        raise RuntimeError(
            "px4ctrl takeoff was not accepted before takeoff timeout")

    def run(self) -> dict:
        self.wait_ready()
        nominal_eta = [1.0] * 4
        self.publish_command(nominal_eta)
        self.request_takeoff()

        rows = []
        fault_applied = False
        takeover_applied = False
        detection_time = None
        start = time.monotonic()
        last = start
        rate = rospy.Rate(self.args.rate_hz)
        while not rospy.is_shutdown() and time.monotonic() - start < self.args.timeout_s:
            now = time.monotonic()
            altitude = self.odom.pose.pose.position.z
            airborne = self.extended.landed_state in (
                ExtendedState.LANDED_STATE_IN_AIR, ExtendedState.LANDED_STATE_LANDING)
            raw = [max(0.0, min(1.0, value)) for value in self.telemetry[1:5]]
            response = [max(0.0, min(1.0, value)) for value in self.telemetry[9:13]]
            if (not fault_applied and airborne and altitude >= self.args.inject_altitude_m and
                    now - start >= self.args.minimum_inject_delay_s):
                fault_applied = True
                fault_time = now
            eta = nominal_eta.copy()
            if fault_applied:
                eta[self.args.rotor_index - 1] = self.args.effectiveness

            thrust, roll, pitch, yaw = wrench_from_motors(raw)
            values = [self.args.mode_id, max(0.001, min(0.05, now - last)), thrust,
                      roll, pitch, yaw, *response, float(airborne), altitude, 1.0,
                      1.0 if not rows else 0.0]
            for name, value in zip((name for name, _ in self.inputs._fields_), values):
                setattr(self.inputs, name, value)
            self.lib.Step()
            generated_motor = [self.outputs.motor_1, self.outputs.motor_2,
                               self.outputs.motor_3, self.outputs.motor_4]
            if fault_applied and int(round(self.outputs.action)) == 2:
                takeover_applied = True
                detection_time = detection_time or now
            self.publish_command(eta, generated_motor if takeover_applied else None)
            rows.append({
                "wall_s": now - start, "sim_s": self.telemetry[0], "altitude_m": altitude,
                "armed": int(self.state.armed), "landed_state": self.extended.landed_state,
                "fault_applied": int(fault_applied), "takeover": int(takeover_applied),
                "isolated_mask": int(round(self.outputs.isolated_mask)),
                "fault_count": int(round(self.outputs.fault_count)),
                "action": int(round(self.outputs.action)),
                "raw_motor": raw, "response": response, "eta_hat": [self.outputs.eta_1,
                    self.outputs.eta_2, self.outputs.eta_3, self.outputs.eta_4],
                "generated_motor": generated_motor,
            })
            if takeover_applied and now - detection_time >= self.args.recovery_hold_s:
                self.publish_takeoff_land(TakeoffLand.LAND)
            if (takeover_applied and not self.state.armed and
                    self.extended.landed_state == ExtendedState.LANDED_STATE_ON_GROUND):
                break
            last = now
            rate.sleep()

        self.publish_command(nominal_eta)
        self.publish_takeoff_land(TakeoffLand.LAND)
        isolated_bit = 1 << (self.args.rotor_index - 1)
        max_altitude = max((row["altitude_m"] for row in rows), default=0.0)
        final = rows[-1] if rows else {}
        status = "passed" if (
            fault_applied and takeover_applied and
            any(row["isolated_mask"] & isolated_bit for row in rows) and
            max_altitude >= self.args.inject_altitude_m and
            final.get("landed_state") == ExtendedState.LANDED_STATE_ON_GROUND and
            final.get("armed") == 0
        ) else "failed"
        return {
            "schema": "mosim.p7.ftc_generated_gazebo_gate.v1", "status": status,
            "mode_id": self.args.mode_id, "rotor_index": self.args.rotor_index,
            "effectiveness": self.args.effectiveness, "fault_applied": fault_applied,
            "generated_takeover_applied": takeover_applied,
            "isolated_mask_observed": max((row["isolated_mask"] for row in rows), default=0),
            "max_altitude_m": max_altitude, "final_landed_state": final.get("landed_state"),
            "final_armed": final.get("armed"), "sample_count": len(rows),
            "claim_boundary": "Same-run Gazebo physical motor-effectiveness injection, official MWORKS-generated FTC detection/isolation and L3 actuator takeover through a bounded companion plugin.",
            "rows": rows,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--mode-id", type=int, default=4)
    parser.add_argument("--rotor-index", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--effectiveness", type=float, default=0.65)
    parser.add_argument("--rate-hz", type=float, default=100.0)
    parser.add_argument("--ready-timeout-s", type=float, default=90.0)
    parser.add_argument("--takeoff-timeout-s", type=float, default=30.0)
    parser.add_argument("--timeout-s", type=float, default=100.0)
    parser.add_argument("--inject-altitude-m", type=float, default=0.75)
    parser.add_argument("--minimum-inject-delay-s", type=float, default=8.0)
    parser.add_argument("--recovery-hold-s", type=float, default=5.0)
    parser.add_argument("--command-topic", default="/uav1/mosim/ftc_actuator_command")
    parser.add_argument("--telemetry-topic", default="/uav1/mosim/ftc_actuator_telemetry")
    parser.add_argument("--takeoff-land-topic", default="/px4ctrl/takeoff_land")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--extended-state-topic", default="/uav1/mavros/extended_state")
    parser.add_argument("--state-topic", default="/uav1/mavros/state")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("mosim_p7_ftc_generated_coordinator", anonymous=False)
    result = Coordinator(args).run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    rows = result.pop("rows")
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["wall_s", "sim_s", "altitude_m", "armed", "landed_state",
                         "fault_applied", "takeover", "isolated_mask", "fault_count",
                         "action", *[f"raw_{i}" for i in range(1, 5)],
                         *[f"response_{i}" for i in range(1, 5)],
                         *[f"eta_hat_{i}" for i in range(1, 5)],
                         *[f"generated_{i}" for i in range(1, 5)]])
        for row in rows:
            writer.writerow([row[k] for k in ("wall_s", "sim_s", "altitude_m", "armed",
                "landed_state", "fault_applied", "takeover", "isolated_mask",
                "fault_count", "action")] + row["raw_motor"] + row["response"] +
                row["eta_hat"] + row["generated_motor"])
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
