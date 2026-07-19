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
    evaluate_readiness_status,
    load_contract,
    resolve_gazebo_body_name,
    validate_command,
)


def _vector(value: Any) -> dict[str, float]:
    return {axis: float(getattr(value, axis)) for axis in ("x", "y", "z")}


def _quaternion(value: Any) -> dict[str, float]:
    return {axis: float(getattr(value, axis)) for axis in ("w", "x", "y", "z")}


def _sample(message: Any = None) -> tuple[Any, float] | None:
    return None if message is None else (message, time.time())


def load_mission_status(
    path: Path,
    *,
    expected_run_id: str,
    expected_vehicle_ids: list[str],
    now: float,
    max_age_s: float,
) -> dict[str, Any]:
    unavailable = {
        "transport_state": "unavailable",
        "fresh": False,
        "terminal": False,
        "reason_code": "mission_status_missing",
    }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return unavailable
    except (OSError, json.JSONDecodeError):
        return {**unavailable, "reason_code": "mission_status_unreadable"}

    vehicles = payload.get("vehicles")
    vehicle_ids = (
        [str(item.get("vehicle_id", "")) for item in vehicles if isinstance(item, dict)]
        if isinstance(vehicles, list)
        else []
    )
    valid = (
        payload.get("schema") == "mosim.mission_status.v1"
        and payload.get("run_id") == expected_run_id
        and isinstance(payload.get("adapter_id"), str)
        and isinstance(payload.get("phase"), str)
        and isinstance(payload.get("state"), str)
        and isinstance(payload.get("terminal"), bool)
        and (payload.get("accepted") is None or isinstance(payload.get("accepted"), bool))
        and sorted(vehicle_ids) == sorted(expected_vehicle_ids)
        and isinstance(payload.get("updated_at"), (int, float))
    )
    if not valid:
        return {**unavailable, "reason_code": "mission_status_contract_invalid"}

    age_s = now - float(payload["updated_at"])
    if age_s < -1.0:
        return {**unavailable, "reason_code": "mission_status_clock_invalid"}
    terminal = bool(payload["terminal"])
    fresh = age_s <= max_age_s
    return {
        **payload,
        "transport_state": "terminal" if terminal else ("fresh" if fresh else "stale"),
        "fresh": fresh,
        "source_age_s": max(0.0, age_s),
    }


class RosRuntimeSidecar:
    def __init__(self, args: argparse.Namespace) -> None:
        import rospy
        from gazebo_msgs.msg import ModelStates
        from gazebo_msgs.srv import ApplyBodyWrench
        from geometry_msgs.msg import Point, Wrench
        from mavros_msgs.msg import AttitudeTarget, State
        from nav_msgs.msg import Odometry, Path as RosPath
        from quadrotor_msgs.msg import PositionCommand
        from std_msgs.msg import Float64MultiArray
        from visualization_msgs.msg import Marker

        self.rospy = rospy
        self.ApplyBodyWrench = ApplyBodyWrench
        self.Wrench = Wrench
        self.Point = Point
        self.Float64MultiArray = Float64MultiArray
        self.args = args
        self.run_dir = args.run_dir
        self.manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        self.profile_id = str(self.manifest.get("experiment_profile_id", ""))
        self.contract = load_contract(args.contract)
        manifest_count = self.manifest.get("vehicle_count", args.vehicle_count)
        if manifest_count != args.vehicle_count:
            raise ValueError("sidecar_vehicle_count_manifest_mismatch")
        self.vehicle_ids = [f"uav{index}" for index in range(1, args.vehicle_count + 1)]
        self.started_at = time.time()
        self.ever_ready = False
        self.model_names: list[str] = []
        self.active_injections: dict[str, dict[str, Any]] = {}
        self.processed_commands: set[str] = set()
        self.task_paths: dict[str, dict[str, Any]] = {}
        self.vehicles: dict[str, dict[str, Any]] = {
            vehicle_id: {
                "state": None,
                "odom": None,
                "target_attitude": None,
                "position_command": None,
                "actuator": None,
                "effectiveness": [1.0] * 4,
                "wind_speed_mps": 0.0,
                "wind_direction_deg": 0.0,
            }
            for vehicle_id in self.vehicle_ids
        }
        self.command_pubs: dict[str, Any] = {}

        for vehicle_id in self.vehicle_ids:
            topics = self._topics(vehicle_id)
            self.command_pubs[vehicle_id] = rospy.Publisher(
                topics["actuator_command"], Float64MultiArray, queue_size=5
            )
            rospy.Subscriber(topics["state"], State, self._store, (vehicle_id, "state"), queue_size=20)
            rospy.Subscriber(topics["odom"], Odometry, self._store, (vehicle_id, "odom"), queue_size=50)
            rospy.Subscriber(
                topics["target_attitude"], AttitudeTarget, self._store,
                (vehicle_id, "target_attitude"), queue_size=50,
            )
            rospy.Subscriber(
                topics["position_command"], PositionCommand, self._store,
                (vehicle_id, "position_command"), queue_size=50,
            )
            rospy.Subscriber(
                topics["actuator_telemetry"], Float64MultiArray, self._store,
                (vehicle_id, "actuator"), queue_size=50,
            )
        rospy.Subscriber(args.model_states_topic, ModelStates, self._models_cb, queue_size=10)
        if args.expected_path_topic:
            rospy.Subscriber(
                args.expected_path_topic, RosPath, self._expected_path_cb,
                callback_args=args.expected_path_topic, queue_size=2,
            )
        if args.future_marker_topic:
            rospy.Subscriber(
                args.future_marker_topic, Marker, self._future_marker_cb,
                callback_args=args.future_marker_topic, queue_size=10,
            )
        self.wrench = rospy.ServiceProxy(args.wrench_service, ApplyBodyWrench)

    @staticmethod
    def _bounded_points(points: list[Any], max_points: int = 1200) -> list[dict[str, float]]:
        if not points:
            return []
        stride = max(1, math.ceil(len(points) / max_points))
        return [_vector(point) for point in points[::stride]][:max_points]

    def _expected_path_cb(self, msg: Any, source_topic: str) -> None:
        if self.profile_id == "factory_l2_three_uav_swarm_formation_v1":
            semantics = "formation_center_reference"
            vehicle_scope = "formation_center"
        elif self.profile_id == "factory_l2_fuel_fixed64_exploration_v1":
            semantics = "exploration_target_sequence"
            vehicle_scope = "uav1"
        else:
            semantics = "mission_reference"
            vehicle_scope = "uav1" if len(self.vehicle_ids) == 1 else "all_vehicles"
        self.task_paths["expected"] = {
            "status": "available",
            "semantics": semantics,
            "vehicle_scope": vehicle_scope,
            "source_topic": source_topic,
            "frame_id": str(msg.header.frame_id),
            "updated_at": time.time(),
            "points": self._bounded_points([pose.pose.position for pose in msg.poses]),
        }

    def _future_marker_cb(self, msg: Any, source_topic: str) -> None:
        if msg.action != msg.ADD or msg.ns != "B-Spline" or msg.id >= 50 or not msg.points:
            return
        self.task_paths["future"] = {
            "status": "available",
            "semantics": "planner_sampled_future_trajectory",
            "vehicle_scope": "uav1" if len(self.vehicle_ids) == 1 else "planner_default",
            "source_topic": source_topic,
            "frame_id": str(msg.header.frame_id),
            "updated_at": time.time(),
            "points": self._bounded_points(list(msg.points)),
        }

    def _topics(self, vehicle_id: str) -> dict[str, str]:
        if self.args.vehicle_count == 1:
            return {
                "state": self.args.state_topic,
                "odom": self.args.odom_topic,
                "target_attitude": self.args.target_attitude_topic,
                "position_command": self.args.position_command_topic,
                "actuator_command": self.args.actuator_command_topic,
                "actuator_telemetry": self.args.actuator_telemetry_topic,
            }
        return {
            "state": f"/{vehicle_id}/mavros/state",
            "odom": f"/{vehicle_id}/mavros/local_position/odom",
            "target_attitude": f"/{vehicle_id}/mavros/setpoint_raw/target_attitude",
            "position_command": f"/{vehicle_id}/position_cmd",
            "actuator_command": f"/{vehicle_id}/mosim/ftc_actuator_command",
            "actuator_telemetry": f"/{vehicle_id}/mosim/ftc_actuator_telemetry",
        }

    def _store(self, msg: Any, target: tuple[str, str]) -> None:
        vehicle_id, field = target
        self.vehicles[vehicle_id][field] = _sample(msg)

    def _models_cb(self, msg: Any) -> None:
        self.model_names = list(msg.name)

    def _vehicle_missing(self, vehicle_id: str, now: float) -> list[str]:
        vehicle = self.vehicles[vehicle_id]
        missing = []
        state = vehicle["state"]
        if state is None or not state[0].connected or now - state[1] > 2.0:
            missing.append("mavros_connected")
        required_samples = [
            ("odom", "mavros_odom_fresh"),
        ]
        if not self.args.skip_controller_command_readiness:
            required_samples.append(("target_attitude", "controller_command_fresh"))
        if not self.args.skip_actuator_telemetry_readiness:
            required_samples.append(("actuator", "actuator_plugin_telemetry_fresh"))
        for field, reason in required_samples:
            sample = vehicle[field]
            if sample is None or now - sample[1] > 1.0:
                missing.append(reason)
        return [f"{vehicle_id}:{reason}" for reason in missing]

    def _ready(self, now: float) -> tuple[bool, list[str]]:
        missing = [reason for vehicle_id in self.vehicle_ids for reason in self._vehicle_missing(vehicle_id, now)]
        return not missing, missing

    def _publish_effectiveness(self, vehicle_id: str) -> None:
        msg = self.Float64MultiArray()
        msg.data = [0.0, *self.vehicles[vehicle_id]["effectiveness"], 0.0, 0.0, 0.0, 0.0]
        self.command_pubs[vehicle_id].publish(msg)

    def _body_name(self, vehicle_id: str) -> str | None:
        configured = self.args.body_name if self.args.vehicle_count == 1 else ""
        return resolve_gazebo_body_name(configured, self.model_names, vehicle_id)

    def _apply_wind_force(self, vehicle_id: str) -> tuple[bool, str]:
        vehicle = self.vehicles[vehicle_id]
        if vehicle["wind_speed_mps"] <= 0.0:
            return True, "wind_zero"
        body_name = self._body_name(vehicle_id)
        if not body_name:
            return False, "gazebo_vehicle_body_not_found"
        angle = math.radians(vehicle["wind_direction_deg"])
        force = self.args.wind_force_coefficient * vehicle["wind_speed_mps"] ** 2
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
        reason = str(response.status_message).strip()
        if response.success and not reason:
            reason = "wind_wrench_applied"
        return bool(response.success), reason

    def _ack(self, command: dict[str, Any], *, accepted: bool, reason: str, applied_value: Any = None) -> None:
        payload = {
            "schema": "mosim.runtime_injection_ack.v1",
            "command_id": command.get("command_id", ""),
            "run_id": self.manifest["run_id"],
            "vehicle_id": command.get("vehicle_id"),
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
            vehicle_id = command["vehicle_id"]
            vehicle = self.vehicles[vehicle_id]
            target = command["target"]
            value = float(command["value"])
            if target == "motor_effectiveness":
                vehicle["effectiveness"][int(command["rotor_index"]) - 1] = value
                self._publish_effectiveness(vehicle_id)
                self.active_injections[f"{vehicle_id}:{target}:{command['rotor_index']}"] = command
                self._ack(command, accepted=True, reason="motor_effectiveness_published", applied_value=value)
            elif target == "wind_direction_deg":
                vehicle["wind_direction_deg"] = value
                self.active_injections[f"{vehicle_id}:{target}"] = command
                self._ack(command, accepted=True, reason="wind_direction_applied", applied_value=value)
            elif target == "wind_speed_mps":
                vehicle["wind_speed_mps"] = value
                ok, reason = self._apply_wind_force(vehicle_id)
                if ok:
                    self.active_injections[f"{vehicle_id}:{target}"] = command
                self._ack(command, accepted=ok, reason=reason, applied_value=value if ok else None)

    def _vehicle_telemetry(self, vehicle_id: str) -> dict[str, Any]:
        vehicle = self.vehicles[vehicle_id]
        telemetry: dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "state": {},
            "reference": None,
            "command": None,
            "injection_state": {
                "wind_speed_mps": vehicle["wind_speed_mps"],
                "wind_direction_deg": vehicle["wind_direction_deg"],
                "motor_effectiveness": vehicle["effectiveness"],
            },
            "rotor_state": None,
            "attitude_error": None,
            "control_output": None,
            "module_diagnostics": {"active_controller_command": vehicle["target_attitude"] is not None},
            "safety_intervention": False,
        }
        if vehicle["state"]:
            msg = vehicle["state"][0]
            telemetry["state"] = {"connected": bool(msg.connected), "armed": bool(msg.armed), "mode": msg.mode}
        if vehicle["odom"]:
            msg = vehicle["odom"][0]
            telemetry["state"].update({
                "position": _vector(msg.pose.pose.position),
                "orientation": _quaternion(msg.pose.pose.orientation),
                "linear_velocity": _vector(msg.twist.twist.linear),
                "angular_velocity": _vector(msg.twist.twist.angular),
            })
        if vehicle["position_command"]:
            msg = vehicle["position_command"][0]
            telemetry["reference"] = {
                "position": _vector(msg.position), "velocity": _vector(msg.velocity),
                "acceleration": _vector(msg.acceleration), "yaw": float(msg.yaw), "yaw_dot": float(msg.yaw_dot),
            }
        if vehicle["target_attitude"]:
            msg = vehicle["target_attitude"][0]
            telemetry["command"] = {
                "orientation": _quaternion(msg.orientation), "body_rate": _vector(msg.body_rate),
                "thrust": float(msg.thrust), "type_mask": int(msg.type_mask),
            }
            telemetry["control_output"] = {"body_rate": _vector(msg.body_rate), "thrust": float(msg.thrust)}
        if vehicle["odom"] and vehicle["target_attitude"]:
            actual = vehicle["odom"][0].pose.pose.orientation
            desired = vehicle["target_attitude"][0].orientation
            dot = abs(actual.w * desired.w + actual.x * desired.x + actual.y * desired.y + actual.z * desired.z)
            telemetry["attitude_error"] = 2.0 * math.acos(max(0.0, min(1.0, dot)))
        if vehicle["odom"] and vehicle["position_command"]:
            actual = vehicle["odom"][0].pose.pose.position
            desired = vehicle["position_command"][0].position
            telemetry["position_error_m"] = {
                "x": float(desired.x - actual.x), "y": float(desired.y - actual.y), "z": float(desired.z - actual.z),
            }
        if vehicle["actuator"] and len(vehicle["actuator"][0].data) == 18:
            values = list(vehicle["actuator"][0].data)
            telemetry["rotor_state"] = {
                "sim_time_s": values[0], "raw_command": values[1:5], "physical_speed_ratio": values[5:9],
                "effective_response": values[9:13], "effectiveness": values[13:17],
                "override_enabled": bool(values[17] >= 0.5),
            }
        return telemetry

    def _write_status_and_telemetry(self) -> None:
        now = time.time()
        ready, missing = self._ready(now)
        status, reason_code, self.ever_ready = evaluate_readiness_status(
            ready=ready,
            ever_ready=self.ever_ready,
            elapsed_s=now - self.started_at,
            timeout_s=self.args.ready_timeout_s,
        )
        status_payload = {
            "schema": "mosim.runtime_status.v1", "run_id": self.manifest["run_id"], "status": status,
            "reason_code": reason_code,
            "vehicle_count": len(self.vehicle_ids), "missing_readiness": missing, "updated_at": now,
        }
        atomic_write_json(self.run_dir / "RUNTIME_STATUS.json", status_payload)
        vehicles = [self._vehicle_telemetry(vehicle_id) for vehicle_id in self.vehicle_ids]
        telemetry: dict[str, Any] = {
            "schema": "mosim.runtime_telemetry.v2", "run_id": self.manifest["run_id"], "timestamp": now,
            "vehicle_count": len(vehicles), "readiness": status_payload, "vehicles": vehicles,
            "task_paths": self.task_paths,
            "mission_status": load_mission_status(
                self.run_dir / "mission_status.json",
                expected_run_id=self.manifest["run_id"],
                expected_vehicle_ids=self.vehicle_ids,
                now=now,
                max_age_s=self.args.mission_status_max_age_s,
            ),
        }
        if len(vehicles) == 1:
            telemetry.update({key: value for key, value in vehicles[0].items() if key != "vehicle_id"})
        atomic_write_json(self.run_dir / "telemetry.json", telemetry)

    def run(self) -> None:
        rate = self.rospy.Rate(self.args.rate_hz)
        while not self.rospy.is_shutdown():
            self._consume_commands()
            for vehicle_id in self.vehicle_ids:
                self._publish_effectiveness(vehicle_id)
                if self.vehicles[vehicle_id]["wind_speed_mps"] > 0.0:
                    self._apply_wind_force(vehicle_id)
            self._write_status_and_telemetry()
            rate.sleep()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--vehicle-count", type=int, choices=range(1, 10), default=1)
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--ready-timeout-s", type=float, default=90.0)
    parser.add_argument("--mission-status-max-age-s", type=float, default=2.5)
    parser.add_argument("--wind-force-coefficient", type=float, default=0.025)
    parser.add_argument("--body-name", default=os.environ.get("MOSIM_GAZEBO_BODY_NAME", ""))
    parser.add_argument("--state-topic", default="/uav1/mavros/state")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--target-attitude-topic", default="/uav1/mavros/setpoint_raw/target_attitude")
    parser.add_argument("--position-command-topic", default="/position_cmd")
    parser.add_argument("--actuator-command-topic", default="/uav1/mosim/ftc_actuator_command")
    parser.add_argument("--actuator-telemetry-topic", default="/uav1/mosim/ftc_actuator_telemetry")
    parser.add_argument("--expected-path-topic", default="")
    parser.add_argument("--future-marker-topic", default="")
    parser.add_argument(
        "--skip-controller-command-readiness",
        action="store_true",
        help="Do not require a controller setpoint for operator ground-standby profiles.",
    )
    parser.add_argument(
        "--skip-actuator-telemetry-readiness",
        action="store_true",
        help="Do not require FTC plugin telemetry for profiles that do not enable actuator faults.",
    )
    parser.add_argument("--model-states-topic", default="/gazebo/model_states")
    parser.add_argument("--wrench-service", default="/gazebo/apply_body_wrench")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate_hz <= 0.0 or args.ready_timeout_s <= 0.0 or args.mission_status_max_age_s <= 0.0:
        raise SystemExit("rate and timeout must be positive")
    args.run_dir.mkdir(parents=True, exist_ok=True)
    import rospy
    rospy.init_node("mosim_orchestrator_runtime_sidecar", anonymous=False)
    RosRuntimeSidecar(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
