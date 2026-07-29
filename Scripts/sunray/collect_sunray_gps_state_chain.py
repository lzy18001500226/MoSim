#!/usr/bin/env python3
"""Collect passive ROS1 observations for the PX4 GPS/EKF state-chain gate."""

from __future__ import annotations

import argparse
import json
import math
import signal
import time
from pathlib import Path
from typing import Any


REQUIRED_TOPICS = (
    "global_position",
    "home_position",
    "local_pose",
    "local_odom",
    "gazebo_pose",
    "mavros_state",
)


def finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def percentile(values: list[float], fraction: float) -> float | None:
    finite_values = sorted(float(value) for value in values if finite(value))
    if not finite_values:
        return None
    index = int(round((len(finite_values) - 1) * fraction))
    return finite_values[max(0, min(index, len(finite_values) - 1))]


def haversine_m(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
    radius_m = 6371000.0
    phi_a = math.radians(latitude_a)
    phi_b = math.radians(latitude_b)
    d_phi = math.radians(latitude_b - latitude_a)
    d_lambda = math.radians(longitude_b - longitude_a)
    sin_phi = math.sin(d_phi / 2.0)
    sin_lambda = math.sin(d_lambda / 2.0)
    value = sin_phi * sin_phi + math.cos(phi_a) * math.cos(phi_b) * sin_lambda * sin_lambda
    return 2.0 * radius_m * math.asin(min(1.0, math.sqrt(value)))


def summarize_capture(
    capture: dict[str, Any],
    expected_ekf2_gps_ctrl: int,
    min_global_samples: int,
    min_local_truth_pairs: int,
    max_local_truth_p95_m: float,
    max_home_global_distance_m: float,
    *,
    requested_duration_s: float | None = None,
    observed_duration_s: float | None = None,
    termination_reason: str | None = None,
    post_connect_settle_ready: bool | None = None,
) -> dict[str, Any]:
    """Evaluate captured records without importing ROS so unit tests stay local."""
    blockers: list[str] = []
    counts = dict(capture.get("counts", {}))
    global_samples = list(capture.get("global_samples", []))
    home_samples = list(capture.get("home_samples", []))
    state_samples = list(capture.get("state_samples", []))
    local_truth_distances = list(capture.get("local_truth_distances_m", []))
    home_global_distances = list(capture.get("home_global_distances_m", []))

    for topic in REQUIRED_TOPICS:
        if int(counts.get(topic, 0)) <= 0:
            blockers.append(f"missing_{topic}")

    valid_globals = [
        sample
        for sample in global_samples
        if int(sample.get("status", -1)) >= 0
        and all(finite(sample.get(field)) for field in ("latitude", "longitude", "altitude"))
        and (abs(float(sample["latitude"])) > 1.0e-6 or abs(float(sample["longitude"])) > 1.0e-6)
    ]
    if len(valid_globals) < min_global_samples:
        blockers.append("insufficient_valid_global_position_samples")

    valid_homes = [
        sample
        for sample in home_samples
        if all(finite(sample.get(field)) for field in ("latitude", "longitude", "altitude"))
        and (abs(float(sample["latitude"])) > 1.0e-6 or abs(float(sample["longitude"])) > 1.0e-6)
    ]
    if not valid_homes:
        blockers.append("missing_valid_home_position")

    connected_states = [sample for sample in state_samples if bool(sample.get("connected"))]
    if len(connected_states) < min_global_samples:
        blockers.append("mavros_connection_not_stable")
    if any(bool(sample.get("armed")) for sample in state_samples):
        blockers.append("no_flight_contract_violated_armed")

    finite_pair_distances = [float(value) for value in local_truth_distances if finite(value)]
    local_truth_p95_m = percentile(finite_pair_distances, 0.95)
    if len(finite_pair_distances) < min_local_truth_pairs:
        blockers.append("insufficient_local_gazebo_truth_pairs")
    elif local_truth_p95_m is None or local_truth_p95_m > max_local_truth_p95_m:
        blockers.append("local_gazebo_truth_p95_exceeds_limit")

    finite_home_distances = [float(value) for value in home_global_distances if finite(value)]
    home_global_p95_m = percentile(finite_home_distances, 0.95)
    if not finite_home_distances:
        blockers.append("missing_home_global_pair")
    elif home_global_p95_m is None or home_global_p95_m > max_home_global_distance_m:
        blockers.append("home_global_distance_exceeds_limit")

    param = dict(capture.get("ekf2_gps_ctrl", {}))
    param_value = param.get("integer")
    if not param.get("success"):
        blockers.append("ekf2_gps_ctrl_read_failed")
    elif not finite(param_value) or int(round(float(param_value))) != expected_ekf2_gps_ctrl:
        blockers.append("ekf2_gps_ctrl_value_mismatch")

    result = {
        "schema": "mosim.sunray_ros1.gps_state_chain_capture.v1",
        "status": "passed" if not blockers else "blocked",
        "blockers": blockers,
        "expected_ekf2_gps_ctrl": expected_ekf2_gps_ctrl,
        "counts": counts,
        "global_position": {
            "valid_samples": len(valid_globals),
            "first": valid_globals[0] if valid_globals else None,
            "last": valid_globals[-1] if valid_globals else None,
        },
        "home_position": {
            "valid_samples": len(valid_homes),
            "first": valid_homes[0] if valid_homes else None,
            "last": valid_homes[-1] if valid_homes else None,
        },
        "mavros_state": {
            "connected_samples": len(connected_states),
            "armed_samples": sum(1 for sample in state_samples if bool(sample.get("armed"))),
            "last": state_samples[-1] if state_samples else None,
        },
        "local_vs_gazebo_truth": {
            "pair_count": len(finite_pair_distances),
            "p95_m": local_truth_p95_m,
            "max_m": max(finite_pair_distances) if finite_pair_distances else None,
            "limit_p95_m": max_local_truth_p95_m,
        },
        "home_vs_global": {
            "pair_count": len(finite_home_distances),
            "p95_m": home_global_p95_m,
            "max_m": max(finite_home_distances) if finite_home_distances else None,
            "limit_p95_m": max_home_global_distance_m,
        },
        "ekf2_gps_ctrl": param,
    }
    if requested_duration_s is not None:
        requested = max(0.0, float(requested_duration_s))
        observed = float(observed_duration_s) if finite(observed_duration_s) else None
        complete = (
            termination_reason == "duration_elapsed"
            and observed is not None
            and observed >= requested
        )
        result["capture_duration"] = {
            "requested_s": requested,
            "observed_s": observed,
            "termination_reason": termination_reason,
            "complete": complete,
        }
        if not complete:
            blockers.append("capture_duration_incomplete")
    if post_connect_settle_ready is not None:
        result["mavros_state"]["post_connect_settle_ready"] = post_connect_settle_ready
        if not post_connect_settle_ready:
            blockers.append("post_connect_settle_not_observed")

    result["status"] = "passed" if not blockers else "blocked"
    return result


class GpsStateChainCollector:
    def __init__(self, args: argparse.Namespace, rospy: Any) -> None:
        self.args = args
        self.rospy = rospy
        self.out = Path(args.output)
        self.out.parent.mkdir(parents=True, exist_ok=True)
        self.samples_path = self.out.with_suffix(".jsonl")
        self.samples_file = self.samples_path.open("w", encoding="utf-8", buffering=1)
        self.start_wall = time.monotonic()
        self.stop_requested = False
        self.last_global: dict[str, Any] | None = None
        self.last_home: dict[str, Any] | None = None
        self.last_local_pose: dict[str, Any] | None = None
        self.last_local_odom: dict[str, Any] | None = None
        self.last_gazebo_pose: dict[str, Any] | None = None
        self.last_state: dict[str, Any] | None = None
        self.global_samples: list[dict[str, Any]] = []
        self.home_samples: list[dict[str, Any]] = []
        self.state_samples: list[dict[str, Any]] = []
        self.local_truth_distances_m: list[float] = []
        self.home_global_distances_m: list[float] = []
        self.ekf2_gps_ctrl: dict[str, Any] = {
            "success": False,
            "integer": None,
            "real": None,
            "attempt_count": 0,
        }
        self.last_param_attempt_wall = 0.0
        self.first_connected_wall_s: float | None = None
        self.counts = {topic: 0 for topic in REQUIRED_TOPICS}
        self.snapshot_count = 0

        from geometry_msgs.msg import PoseStamped
        from mavros_msgs.msg import HomePosition, State
        from mavros_msgs.srv import ParamGet
        from nav_msgs.msg import Odometry
        from sensor_msgs.msg import NavSatFix

        ns = args.uav_ns.rstrip("/")
        self.param_get = rospy.ServiceProxy(f"{ns}/mavros/param/get", ParamGet, persistent=False)
        rospy.Subscriber(f"{ns}/mavros/global_position/global", NavSatFix, self.on_global, queue_size=100)
        rospy.Subscriber(f"{ns}/mavros/home_position/home", HomePosition, self.on_home, queue_size=20)
        rospy.Subscriber(f"{ns}/mavros/local_position/pose", PoseStamped, self.on_local_pose, queue_size=100)
        rospy.Subscriber(f"{ns}/mavros/local_position/odom", Odometry, self.on_local_odom, queue_size=100)
        rospy.Subscriber(f"{ns}/sunray/gazebo_pose", Odometry, self.on_gazebo_pose, queue_size=100)
        rospy.Subscriber(f"{ns}/mavros/state", State, self.on_state, queue_size=100)

    def elapsed_s(self) -> float:
        return time.monotonic() - self.start_wall

    @staticmethod
    def pose_dict(msg: Any) -> dict[str, Any]:
        pose = msg.pose.pose if hasattr(msg.pose, "pose") else msg.pose
        return {
            "x": float(pose.position.x),
            "y": float(pose.position.y),
            "z": float(pose.position.z),
        }

    def on_global(self, msg: Any) -> None:
        sample = {
            "t_wall_s": self.elapsed_s(),
            "latitude": float(msg.latitude),
            "longitude": float(msg.longitude),
            "altitude": float(msg.altitude),
            "status": int(msg.status.status),
        }
        self.last_global = sample
        self.global_samples.append(sample)
        self.counts["global_position"] += 1

    def on_home(self, msg: Any) -> None:
        sample = {
            "t_wall_s": self.elapsed_s(),
            "latitude": float(msg.geo.latitude),
            "longitude": float(msg.geo.longitude),
            "altitude": float(msg.geo.altitude),
        }
        self.last_home = sample
        self.home_samples.append(sample)
        self.counts["home_position"] += 1

    def on_local_pose(self, msg: Any) -> None:
        sample = self.pose_dict(msg)
        sample["t_wall_s"] = self.elapsed_s()
        self.last_local_pose = sample
        self.counts["local_pose"] += 1

    def on_local_odom(self, msg: Any) -> None:
        sample = self.pose_dict(msg)
        sample["t_wall_s"] = self.elapsed_s()
        self.last_local_odom = sample
        self.counts["local_odom"] += 1

    def on_gazebo_pose(self, msg: Any) -> None:
        sample = self.pose_dict(msg)
        sample["t_wall_s"] = self.elapsed_s()
        self.last_gazebo_pose = sample
        self.counts["gazebo_pose"] += 1

    def on_state(self, msg: Any) -> None:
        sample = {
            "t_wall_s": self.elapsed_s(),
            "connected": bool(msg.connected),
            "armed": bool(msg.armed),
            "mode": str(msg.mode),
            "system_status": int(msg.system_status),
        }
        self.last_state = sample
        self.state_samples.append(sample)
        self.counts["mavros_state"] += 1
        if sample["connected"] and self.first_connected_wall_s is None:
            self.first_connected_wall_s = sample["t_wall_s"]

    def query_ekf2_gps_ctrl(self) -> None:
        if self.ekf2_gps_ctrl.get("success"):
            return
        now = time.monotonic()
        if now - self.last_param_attempt_wall < 1.0:
            return
        self.last_param_attempt_wall = now
        attempt_count = int(self.ekf2_gps_ctrl.get("attempt_count", 0)) + 1
        attempt_t_wall_s = self.elapsed_s()
        try:
            self.rospy.wait_for_service(f"{self.args.uav_ns.rstrip('/')}/mavros/param/get", timeout=0.2)
            response = self.param_get("EKF2_GPS_CTRL")
            self.ekf2_gps_ctrl = {
                "success": bool(response.success),
                "integer": int(response.value.integer),
                "real": float(response.value.real),
                "attempt_count": attempt_count,
                "last_attempt_t_wall_s": attempt_t_wall_s,
                "error": None if response.success else "mavros_param_get_response_success_false",
            }
        except Exception as exc:  # ROS service may appear after Gazebo/PX4 boot.
            self.ekf2_gps_ctrl = {
                "success": False,
                "integer": None,
                "real": None,
                "attempt_count": attempt_count,
                "last_attempt_t_wall_s": attempt_t_wall_s,
                "error": repr(exc),
            }

    def snapshot(self) -> None:
        self.query_ekf2_gps_ctrl()
        row: dict[str, Any] = {
            "t_wall_s": self.elapsed_s(),
            "global_position": self.last_global,
            "home_position": self.last_home,
            "local_pose": self.last_local_pose,
            "local_odom": self.last_local_odom,
            "gazebo_pose": self.last_gazebo_pose,
            "mavros_state": self.last_state,
        }
        if self.last_local_pose and self.last_gazebo_pose:
            distance_m = math.sqrt(
                sum(
                    (float(self.last_local_pose[axis]) - float(self.last_gazebo_pose[axis])) ** 2
                    for axis in ("x", "y", "z")
                )
            )
            row["local_vs_gazebo_truth_m"] = distance_m
            self.local_truth_distances_m.append(distance_m)
        if (
            self.last_global
            and self.last_home
            and int(self.last_global["status"]) >= 0
            and all(
                finite(self.last_global[field]) and finite(self.last_home[field])
                for field in ("latitude", "longitude", "altitude")
            )
            and (
                abs(float(self.last_global["latitude"])) > 1.0e-6
                or abs(float(self.last_global["longitude"])) > 1.0e-6
            )
        ):
            distance_m = haversine_m(
                float(self.last_global["latitude"]),
                float(self.last_global["longitude"]),
                float(self.last_home["latitude"]),
                float(self.last_home["longitude"]),
            )
            row["home_vs_global_m"] = distance_m
            self.home_global_distances_m.append(distance_m)
        self.samples_file.write(json.dumps(row, ensure_ascii=True) + "\n")
        self.snapshot_count += 1

    def ready(self) -> bool:
        if self.first_connected_wall_s is None:
            return False
        if self.elapsed_s() - self.first_connected_wall_s < self.args.post_connect_settle_s:
            return False
        return all(self.counts[topic] > 0 for topic in REQUIRED_TOPICS) and bool(self.ekf2_gps_ctrl.get("success"))

    def request_stop(self, _signum: int, _frame: Any) -> None:
        self.stop_requested = True

    def run(self) -> int:
        signal.signal(signal.SIGTERM, self.request_stop)
        signal.signal(signal.SIGINT, self.request_stop)
        requested_duration_s = max(0.0, float(self.args.duration_s))
        deadline = time.monotonic() + requested_duration_s
        termination_reason = "duration_elapsed"
        post_connect_settle_ready = False
        while True:
            if self.rospy.is_shutdown():
                termination_reason = "ros_shutdown"
                break
            if self.stop_requested:
                termination_reason = "signal"
                break
            if time.monotonic() >= deadline:
                break
            self.snapshot()
            post_connect_settle_ready = post_connect_settle_ready or self.ready()
            remaining_s = max(0.0, deadline - time.monotonic())
            if remaining_s > 0.0:
                time.sleep(min(1.0 / max(self.args.sample_rate_hz, 1.0), remaining_s))

        self.samples_file.flush()
        self.samples_file.close()
        observed_duration_s = self.elapsed_s()
        capture = {
            "counts": self.counts,
            "global_samples": self.global_samples,
            "home_samples": self.home_samples,
            "state_samples": self.state_samples,
            "local_truth_distances_m": self.local_truth_distances_m,
            "home_global_distances_m": self.home_global_distances_m,
            "ekf2_gps_ctrl": self.ekf2_gps_ctrl,
        }
        summary = summarize_capture(
            capture,
            expected_ekf2_gps_ctrl=self.args.expected_ekf2_gps_ctrl,
            min_global_samples=self.args.min_global_samples,
            min_local_truth_pairs=self.args.min_local_truth_pairs,
            max_local_truth_p95_m=self.args.max_local_truth_p95_m,
            max_home_global_distance_m=self.args.max_home_global_distance_m,
            requested_duration_s=requested_duration_s,
            observed_duration_s=observed_duration_s,
            termination_reason=termination_reason,
            post_connect_settle_ready=post_connect_settle_ready,
        )
        summary.update(
            {
                "requested_duration_s": requested_duration_s,
                "observed_duration_s": observed_duration_s,
                "sample_rate_hz": self.args.sample_rate_hz,
                "post_connect_settle_s": self.args.post_connect_settle_s,
                "first_connected_wall_s": self.first_connected_wall_s,
                "snapshot_count": self.snapshot_count,
                "termination_reason": termination_reason,
                "interrupted": termination_reason != "duration_elapsed",
                "samples_jsonl": str(self.samples_path),
            }
        )
        self.out.write_text(json.dumps(summary, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=True, indent=2))
        return 0 if summary["status"] == "passed" else 18


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--duration-s", type=float, default=90.0)
    parser.add_argument("--sample-rate-hz", type=float, default=5.0)
    parser.add_argument("--post-connect-settle-s", type=float, default=10.0)
    parser.add_argument("--uav-ns", default="/uav1")
    parser.add_argument("--expected-ekf2-gps-ctrl", type=int, default=7)
    parser.add_argument("--min-global-samples", type=int, default=5)
    parser.add_argument("--min-local-truth-pairs", type=int, default=10)
    parser.add_argument("--max-local-truth-p95-m", type=float, default=0.5)
    parser.add_argument("--max-home-global-distance-m", type=float, default=25.0)
    args = parser.parse_args()

    import rospy

    rospy.init_node("mosim_sunray_gps_state_chain", anonymous=True, disable_signals=True)
    return GpsStateChainCollector(args, rospy).run()


if __name__ == "__main__":
    raise SystemExit(main())
