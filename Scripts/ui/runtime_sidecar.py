#!/usr/bin/env python3
"""Publish same-run ROS readiness, telemetry, and audited physical injections."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.runtime_sidecar_contract import (
    atomic_write_json,
    load_contract,
    resolve_gazebo_body_name,
    validate_command,
)


def _vector(value: Any) -> dict[str, float]:
    return {axis: float(getattr(value, axis)) for axis in ("x", "y", "z")}


def _quaternion(value: Any) -> dict[str, float]:
    return {axis: float(getattr(value, axis)) for axis in ("w", "x", "y", "z")}


class RosRuntimeSidecar:
    def __init__(self, args: argparse.Namespace) -> None:
        import rospy
        from gazebo_msgs.msg import ModelStates
        from gazebo_msgs.srv import ApplyBodyWrench
        from geometry_msgs.msg import Point, Wrench
        from mavros_msgs.msg import AttitudeTarget, State
        from nav_msgs.msg import Odometry
        from quadrotor_msgs.msg import PositionCommand
        from std_msgs.msg import Float64MultiArray

        self.rospy = rospy
        self.ApplyBodyWrench = ApplyBodyWrench
        self.Wrench = Wrench
        self.Point = Point
        self.Float64MultiArray = Float64MultiArray
        self.args = args
        self.run_dir = args.run_dir
        self.manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        self.contract = load_contract(args.contract)
        self.started_at = time.time()
        self.state = None
        self.odom = None
        self.target_attitude = None
        self.position_command = None
        self.actuator = None
        self.model_names: list[str] = []
        self.effectiveness = [1.0] * 4
        self.wind_speed_mps = 0.0
        self.wind_direction_deg = 0.0
        self.active_injections: dict[str, dict[str, Any]] = {}
        self.processed_commands: set[str] = set()

        self.command_pub = rospy.Publisher(args.actuator_command_topic, Float64MultiArray, queue_size=5)
        rospy.Subscriber(args.state_topic, State, self._state_cb, queue_size=20)
        rospy.Subscriber(args.odom_topic, Odometry, self._odom_cb, queue_size=50)
        rospy.Subscriber(args.target_attitude_topic, AttitudeTarget, self._target_attitude_cb, queue_size=50)
        rospy.Subscriber(args.position_command_topic, PositionCommand, self._position_command_cb, queue_size=50)
        rospy.Subscriber(args.actuator_telemetry_topic, Float64MultiArray, self._actuator_cb, queue_size=50)
        rospy.Subscriber(args.model_states_topic, ModelStates, self._models_cb, queue_size=10)
        self.wrench = rospy.ServiceProxy(args.wrench_service, ApplyBodyWrench)

    def _state_cb(self, msg: Any) -> None: self.state = (msg, time.time())
    def _odom_cb(self, msg: Any) -> None: self.odom = (msg, time.time())
    def _target_attitude_cb(self, msg: Any) -> None: self.target_attitude = (msg, time.time())
    def _position_command_cb(self, msg: Any) -> None: self.position_command = (msg, time.time())
    def _actuator_cb(self, msg: Any) -> None: self.actuator = (msg, time.time())
    def _models_cb(self, msg: Any) -> None: self.model_names = list(msg.name)

    def _ready(self, now: float) -> tuple[bool, list[str]]:
        missing = []
        if self.state is None or not self.state[0].connected or now - self.state[1] > 2.0:
            missing.append("mavros_connected")
        if self.odom is None or now - self.odom[1] > 1.0:
            missing.append("mavros_odom_fresh")
        if self.target_attitude is None or now - self.target_attitude[1] > 1.0:
            missing.append("controller_command_fresh")
        if self.actuator is None or now - self.actuator[1] > 1.0:
            missing.append("actuator_plugin_telemetry_fresh")
        return not missing, missing

    def _publish_effectiveness(self) -> None:
        msg = self.Float64MultiArray()
        msg.data = [0.0, *self.effectiveness, 0.0, 0.0, 0.0, 0.0]
        self.command_pub.publish(msg)

    def _body_name(self) -> str | None:
        return resolve_gazebo_body_name(self.args.body_name, self.model_names)

    def _apply_wind_force(self) -> tuple[bool, str]:
        if self.wind_speed_mps <= 0.0:
            return True, "wind_zero"
        body_name = self._body_name()
        if not body_name:
            return False, "gazebo_vehicle_body_not_found"
        angle = math.radians(self.wind_direction_deg)
        force = self.args.wind_force_coefficient * self.wind_speed_mps * self.wind_speed_mps
        wrench = self.Wrench()
        wrench.force.x = force * math.cos(angle)
        wrench.force.y = force * math.sin(angle)
        try:
            response = self.wrench(
                body_name=body_name,
                reference_frame="world",
                reference_point=self.Point(),
                wrench=wrench,
                start_time=self.rospy.Time(0),
                duration=self.rospy.Duration(0.15),
            )
        except Exception as exc:
            return False, f"gazebo_apply_body_wrench_failed:{exc}"
        return bool(response.success), str(response.status_message)

    def _ack(self, command: dict[str, Any], *, accepted: bool, reason: str, applied_value: Any = None) -> None:
        payload = {
            "schema": "mosim.runtime_injection_ack.v1",
            "command_id": command.get("command_id", ""),
            "run_id": self.manifest["run_id"],
            "accepted": accepted,
            "reason_code": reason,
            "requested_value": command.get("value"),
            "applied_value": applied_value,
            "applied_at": time.time(),
        }
        atomic_write_json(self.run_dir / "injection_acks" / f"{command.get('command_id', 'invalid')}.json", payload)

    def _consume_commands(self) -> None:
        command_dir = self.run_dir / "injection_commands"
        command_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(command_dir.glob("inj-*.json")):
            if path.name in self.processed_commands:
                continue
            self.processed_commands.add(path.name)
            raw: dict[str, Any] = {}
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                command = validate_command(raw, manifest=self.manifest, contract=self.contract)
            except (OSError, ValueError, TypeError) as exc:
                self._ack(raw, accepted=False, reason=str(exc))
                continue
            target = command["target"]
            value = float(command["value"])
            if target == "motor_effectiveness":
                self.effectiveness[int(command["rotor_index"]) - 1] = value
                self._publish_effectiveness()
                self.active_injections[target + f":{command['rotor_index']}"] = command
                self._ack(command, accepted=True, reason="motor_effectiveness_published", applied_value=value)
            elif target == "wind_direction_deg":
                self.wind_direction_deg = value
                self.active_injections[target] = command
                self._ack(command, accepted=True, reason="wind_direction_applied", applied_value=value)
            elif target == "wind_speed_mps":
                self.wind_speed_mps = value
                ok, reason = self._apply_wind_force()
                if ok:
                    self.active_injections[target] = command
                self._ack(command, accepted=ok, reason=reason, applied_value=value if ok else None)

    def _write_status_and_telemetry(self) -> None:
        now = time.time()
        ready, missing = self._ready(now)
        timed_out = not ready and now - self.started_at >= self.args.ready_timeout_s
        status = "running" if ready else ("blocked" if timed_out else "starting")
        status_payload = {
            "schema": "mosim.runtime_status.v1",
            "run_id": self.manifest["run_id"],
            "status": status,
            "reason_code": "runtime_ready" if ready else (
                "runtime_readiness_timeout" if timed_out else "runtime_readiness_pending"),
            "missing_readiness": missing,
            "updated_at": now,
        }
        atomic_write_json(self.run_dir / "RUNTIME_STATUS.json", status_payload)
        telemetry: dict[str, Any] = {
            "schema": "mosim.runtime_telemetry.v1",
            "run_id": self.manifest["run_id"],
            "timestamp": now,
            "readiness": status_payload,
            "state": {},
            "reference": None,
            "command": None,
            "injection_state": {
                "wind_speed_mps": self.wind_speed_mps,
                "wind_direction_deg": self.wind_direction_deg,
                "motor_effectiveness": self.effectiveness,
            },
            "rotor_state": None,
            "attitude_error": None,
            "control_output": None,
            "module_diagnostics": {"active_controller_command": self.target_attitude is not None},
            "safety_intervention": False,
        }
        if self.state:
            msg = self.state[0]
            telemetry["state"] = {"connected": bool(msg.connected), "armed": bool(msg.armed), "mode": msg.mode}
        if self.odom:
            msg = self.odom[0]
            telemetry["state"].update({
                "position": _vector(msg.pose.pose.position),
                "orientation": _quaternion(msg.pose.pose.orientation),
                "linear_velocity": _vector(msg.twist.twist.linear),
                "angular_velocity": _vector(msg.twist.twist.angular),
            })
        if self.position_command:
            msg = self.position_command[0]
            telemetry["reference"] = {
                "position": _vector(msg.position),
                "velocity": _vector(msg.velocity),
                "acceleration": _vector(msg.acceleration),
                "yaw": float(msg.yaw),
                "yaw_dot": float(msg.yaw_dot),
            }
        if self.target_attitude:
            msg = self.target_attitude[0]
            telemetry["command"] = {
                "orientation": _quaternion(msg.orientation),
                "body_rate": _vector(msg.body_rate),
                "thrust": float(msg.thrust),
                "type_mask": int(msg.type_mask),
            }
            telemetry["control_output"] = {
                "body_rate": _vector(msg.body_rate),
                "thrust": float(msg.thrust),
            }
        if self.odom and self.target_attitude:
            actual = self.odom[0].pose.pose.orientation
            desired = self.target_attitude[0].orientation
            dot = abs(actual.w * desired.w + actual.x * desired.x + actual.y * desired.y + actual.z * desired.z)
            telemetry["attitude_error"] = 2.0 * math.acos(max(0.0, min(1.0, dot)))
        if self.odom and self.position_command:
            actual = self.odom[0].pose.pose.position
            desired = self.position_command[0].position
            telemetry["position_error_m"] = {
                "x": float(desired.x - actual.x),
                "y": float(desired.y - actual.y),
                "z": float(desired.z - actual.z),
            }
        if self.actuator and len(self.actuator[0].data) == 18:
            values = list(self.actuator[0].data)
            telemetry["rotor_state"] = {
                "sim_time_s": values[0],
                "raw_command": values[1:5],
                "physical_speed_ratio": values[5:9],
                "effective_response": values[9:13],
                "effectiveness": values[13:17],
                "override_enabled": bool(values[17] >= 0.5),
            }
        atomic_write_json(self.run_dir / "telemetry.json", telemetry)

    def run(self) -> None:
        rate = self.rospy.Rate(self.args.rate_hz)
        while not self.rospy.is_shutdown():
            self._consume_commands()
            self._publish_effectiveness()
            if self.wind_speed_mps > 0.0:
                self._apply_wind_force()
            self._write_status_and_telemetry()
            rate.sleep()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--ready-timeout-s", type=float, default=90.0)
    parser.add_argument("--wind-force-coefficient", type=float, default=0.025)
    parser.add_argument("--body-name", default=os.environ.get("MOSIM_GAZEBO_BODY_NAME", ""))
    parser.add_argument("--state-topic", default="/uav1/mavros/state")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--target-attitude-topic", default="/uav1/mavros/setpoint_raw/target_attitude")
    parser.add_argument("--position-command-topic", default="/position_cmd")
    parser.add_argument("--actuator-command-topic", default="/uav1/mosim/ftc_actuator_command")
    parser.add_argument("--actuator-telemetry-topic", default="/uav1/mosim/ftc_actuator_telemetry")
    parser.add_argument("--model-states-topic", default="/gazebo/model_states")
    parser.add_argument("--wrench-service", default="/gazebo/apply_body_wrench")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate_hz <= 0.0 or args.ready_timeout_s <= 0.0:
        raise SystemExit("rate and timeout must be positive")
    args.run_dir.mkdir(parents=True, exist_ok=True)
    import rospy
    rospy.init_node("mosim_orchestrator_runtime_sidecar", anonymous=False)
    RosRuntimeSidecar(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
