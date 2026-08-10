#!/usr/bin/env python3
"""Forward a fresh QGC Plan View target into the live ROS1 planner input.

QGC writes one request under the active run directory. This bridge validates
that request against the frozen run, the active-run pointer, and the verified
Factory coordinate evidence before it publishes exactly one standard
``geometry_msgs/PoseStamped`` on the planner's RViz-compatible goal topic.

The bridge never consumes rosbag data and never publishes a PX4, MAVROS, or
motor command. A ``forwarded`` status means the ROS publisher observed a
subscriber and published the planner input. It is not planner, controller, or
flight acceptance.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.ui.factory_map_coordinates import world_for_coordinate
from src.orchestration.operator_map_replay import (
    canonical_json_hash,
    load_coordinate_evidence,
)
from src.orchestration.run_manifest_contract import validate_run_manifest_v2


GOAL_REQUEST_SCHEMA = "mosim.qgc_realtime_goal_request.v1"
GOAL_STATUS_SCHEMA = "mosim.qgc_realtime_goal_status.v1"
ACTIVE_POINTER_SCHEMA = "mosim.qgc_active_run_pointer.v1"
MAP_IDENTITY_FIELDS = (
    "map_id",
    "map_version",
    "asset_sha256",
    "world_frame",
    "coordinate_contract_id",
)
REQUEST_ID_PATTERN = re.compile(r"^qgc-goal-[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")


def _mapping(value: Any, reason_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(reason_code)
    return value


def _required_string(value: Any, reason_code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(reason_code)
    return value


def _finite(value: Any, reason_code: str) -> float:
    if isinstance(value, bool):
        raise ValueError(reason_code)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(reason_code) from exc
    if not math.isfinite(number):
        raise ValueError(reason_code)
    return number


def read_json_object(path: Path, reason_code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(reason_code) from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(reason_code) from exc
    return _mapping(value, reason_code)


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(dict(value), stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)


def validate_active_pointer(active: Any, *, manifest: Mapping[str, Any]) -> dict[str, Any]:
    pointer = _mapping(active, "qgc_realtime_goal_active_pointer_invalid")
    run_id = _required_string(manifest.get("run_id"), "qgc_realtime_goal_manifest_run_id_missing")
    if (
        pointer.get("schema") != ACTIVE_POINTER_SCHEMA
        or pointer.get("state") != "running"
        or pointer.get("run_id") != run_id
        or pointer.get("run_directory") != f"Results/runs/{run_id}"
        or pointer.get("experiment_profile_id") != manifest.get("experiment_profile_id")
        or pointer.get("experiment_profile_hash") != manifest.get("experiment_profile_hash")
        or pointer.get("runtime_profile_id") != manifest.get("runtime_profile_id")
    ):
        raise ValueError("qgc_realtime_goal_active_run_not_running")
    return pointer


def normalize_goal_request(request: Any, *, manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the QGC request without importing ROS.

    This intentionally treats QGC's altitude as an audit value only. The
    outgoing topic is the equivalent of RViz 2D Nav Goal, which carries the
    ground-plane point; the running planner adapter owns its configured flight
    height.
    """

    raw = _mapping(request, "qgc_realtime_goal_request_invalid")
    run_id = _required_string(manifest.get("run_id"), "qgc_realtime_goal_manifest_run_id_missing")
    snapshot = _mapping(
        manifest.get("operator_map_snapshot"),
        "qgc_realtime_goal_manifest_map_snapshot_missing",
    )
    snapshot_hash = _required_string(
        manifest.get("operator_map_snapshot_hash"),
        "qgc_realtime_goal_manifest_map_snapshot_hash_missing",
    )
    if canonical_json_hash(snapshot) != snapshot_hash:
        raise ValueError("qgc_realtime_goal_manifest_map_snapshot_hash_mismatch")
    request_id = _required_string(raw.get("request_id"), "qgc_realtime_goal_request_id_missing")
    if REQUEST_ID_PATTERN.fullmatch(request_id) is None:
        raise ValueError("qgc_realtime_goal_request_id_invalid")
    if (
        raw.get("schema") != GOAL_REQUEST_SCHEMA
        or raw.get("state") != "submitted"
        or raw.get("run_id") != run_id
        or raw.get("experiment_profile_id") != manifest.get("experiment_profile_id")
        or raw.get("experiment_profile_hash") != manifest.get("experiment_profile_hash")
        or raw.get("runtime_profile_id") != manifest.get("runtime_profile_id")
        or raw.get("source") != "qgc_plan_view"
    ):
        raise ValueError("qgc_realtime_goal_request_identity_mismatch")

    request_map = _mapping(raw.get("operator_map"), "qgc_realtime_goal_request_map_missing")
    if request_map.get("operator_map_snapshot_hash") != snapshot_hash:
        raise ValueError("qgc_realtime_goal_request_map_snapshot_mismatch")
    for field in MAP_IDENTITY_FIELDS:
        if request_map.get(field) != snapshot.get(field):
            raise ValueError("qgc_realtime_goal_request_map_identity_mismatch")

    goal = _mapping(raw.get("goal"), "qgc_realtime_goal_request_goal_missing")
    latitude = _finite(goal.get("latitude_deg"), "qgc_realtime_goal_request_latitude_invalid")
    longitude = _finite(goal.get("longitude_deg"), "qgc_realtime_goal_request_longitude_invalid")
    qgc_altitude = _finite(goal.get("qgc_altitude_m"), "qgc_realtime_goal_request_altitude_invalid")
    if not -90.0 <= latitude <= 90.0 or not -180.0 <= longitude <= 180.0:
        raise ValueError("qgc_realtime_goal_request_coordinate_out_of_range")
    submitted_at = _finite(raw.get("submitted_at_unix_s"), "qgc_realtime_goal_request_time_invalid")
    if submitted_at <= 0.0:
        raise ValueError("qgc_realtime_goal_request_time_invalid")
    return {
        "schema": GOAL_REQUEST_SCHEMA,
        "state": "submitted",
        "request_id": request_id,
        "run_id": run_id,
        "experiment_profile_id": manifest["experiment_profile_id"],
        "experiment_profile_hash": manifest["experiment_profile_hash"],
        "runtime_profile_id": manifest["runtime_profile_id"],
        "submitted_at_unix_s": submitted_at,
        "source": "qgc_plan_view",
        "operator_map": dict(request_map),
        "goal": {
            "latitude_deg": latitude,
            "longitude_deg": longitude,
            "qgc_altitude_m": qgc_altitude,
        },
    }


def validate_request_freshness(
    request: Mapping[str, Any],
    *,
    now_unix_s: float,
    max_request_age_s: float,
    max_future_skew_s: float,
) -> float:
    submitted_at = _finite(request.get("submitted_at_unix_s"), "qgc_realtime_goal_request_time_invalid")
    now = _finite(now_unix_s, "qgc_realtime_goal_clock_invalid")
    if max_request_age_s <= 0.0 or max_future_skew_s < 0.0:
        raise ValueError("qgc_realtime_goal_request_age_policy_invalid")
    age_s = now - submitted_at
    if age_s > max_request_age_s:
        raise ValueError("qgc_realtime_goal_request_stale")
    if age_s < -max_future_skew_s:
        raise ValueError("qgc_realtime_goal_request_from_future")
    return max(0.0, age_s)


def _target_to_source(
    position: Mapping[str, float],
    *,
    matrix: list[list[float]],
) -> dict[str, float]:
    """Invert a validated rigid target-from-source transform."""

    shifted = [
        float(position["x"]) - matrix[0][3],
        float(position["y"]) - matrix[1][3],
        float(position["z"]) - matrix[2][3],
    ]
    return {
        axis: sum(matrix[column][row] * shifted[column] for column in range(3))
        for row, axis in enumerate(("x", "y", "z"))
    }


def build_live_goal(
    request: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    coordinate_evidence: Mapping[str, Any],
    goal_frame: str,
    ground_z_m: float,
) -> dict[str, Any]:
    """Convert the QGC geographic point into the standard ROS planner goal."""

    snapshot = _mapping(
        manifest.get("operator_map_snapshot"),
        "qgc_realtime_goal_manifest_map_snapshot_missing",
    )
    anchor = _mapping(
        snapshot.get("simulation_geodetic_anchor"),
        "qgc_realtime_goal_geodetic_anchor_missing",
    )
    normalized = normalize_goal_request(request, manifest=manifest)
    world = world_for_coordinate(
        anchor,
        normalized["goal"]["latitude_deg"],
        normalized["goal"]["longitude_deg"],
    )
    target_frame = _required_string(
        coordinate_evidence.get("target_frame_id"),
        "qgc_realtime_goal_coordinate_target_frame_missing",
    )
    source_frame = _required_string(
        coordinate_evidence.get("source_frame_id"),
        "qgc_realtime_goal_coordinate_source_frame_missing",
    )
    if target_frame != snapshot.get("world_frame"):
        raise ValueError("qgc_realtime_goal_coordinate_target_frame_mismatch")
    requested_goal_frame = _required_string(goal_frame, "qgc_realtime_goal_output_frame_missing")
    target_position = {
        "x": _finite(world.get("x_m"), "qgc_realtime_goal_world_coordinate_invalid"),
        "y": _finite(world.get("y_m"), "qgc_realtime_goal_world_coordinate_invalid"),
        "z": _finite(ground_z_m, "qgc_realtime_goal_ground_z_invalid"),
    }
    if requested_goal_frame == target_frame:
        output_position = target_position
    elif requested_goal_frame == source_frame:
        matrix = coordinate_evidence.get("transform_target_from_source_4x4")
        if not isinstance(matrix, list) or len(matrix) != 4:
            raise ValueError("qgc_realtime_goal_coordinate_matrix_invalid")
        output_position = _target_to_source(target_position, matrix=matrix)
    else:
        raise ValueError("qgc_realtime_goal_output_frame_not_evidence_bound")
    return {
        "request_id": normalized["request_id"],
        "run_id": normalized["run_id"],
        "frame_id": requested_goal_frame,
        "position": output_position,
        "qgc_goal": normalized["goal"],
        "map_world_position": target_position,
    }


def build_goal_status(
    *,
    manifest: Mapping[str, Any],
    state: str,
    reason_code: str,
    request_id: str = "",
    details: Mapping[str, Any] | None = None,
    now_unix_s: float | None = None,
) -> dict[str, Any]:
    run_id = _required_string(manifest.get("run_id"), "qgc_realtime_goal_manifest_run_id_missing")
    if state not in {"ready", "awaiting_subscriber", "forwarded", "rejected"}:
        raise ValueError("qgc_realtime_goal_status_state_invalid")
    result: dict[str, Any] = {
        "schema": GOAL_STATUS_SCHEMA,
        "run_id": run_id,
        "request_id": request_id,
        "state": state,
        "reason_code": reason_code,
        "updated_at_unix_s": time.time() if now_unix_s is None else float(now_unix_s),
        "claim_boundary": (
            "Live ROS1 planner-input transport only. This does not prove planner acceptance, "
            "trajectory freshness, controller tracking, PX4/MAVROS output, or flight success."
        ),
    }
    if details:
        result["details"] = dict(details)
    return result


def load_runtime_context(
    *,
    run_dir: Path,
    coordinate_evidence_path: Path,
    active_pointer_path: Path,
) -> dict[str, Any]:
    manifest = read_json_object(run_dir / "RUN_MANIFEST.json", "qgc_realtime_goal_manifest_unreadable")
    validate_run_manifest_v2(manifest)
    validate_active_pointer(
        read_json_object(active_pointer_path, "qgc_realtime_goal_active_pointer_unreadable"),
        manifest=manifest,
    )
    snapshot = _mapping(
        manifest.get("operator_map_snapshot"),
        "qgc_realtime_goal_manifest_map_snapshot_missing",
    )
    snapshot_hash = _required_string(
        manifest.get("operator_map_snapshot_hash"),
        "qgc_realtime_goal_manifest_map_snapshot_hash_missing",
    )
    evidence, evidence_sha256 = load_coordinate_evidence(
        coordinate_evidence_path,
        map_snapshot=snapshot,
        snapshot_hash=snapshot_hash,
    )
    return {
        "manifest": manifest,
        "coordinate_evidence": evidence,
        "coordinate_evidence_sha256": evidence_sha256,
    }


class RealtimeGoalBridge:
    """ROS-dependent delivery loop, deliberately separated from pure checks."""

    def __init__(self, *, args: argparse.Namespace, rospy: Any, pose_stamped_type: Any) -> None:
        self.args = args
        self.rospy = rospy
        self.pose_stamped_type = pose_stamped_type
        self.run_dir = args.run_dir.resolve()
        self.request_path = self.run_dir / "operator_goal" / "REQUEST.json"
        self.status_path = self.run_dir / "operator_goal" / "STATUS.json"
        self.publisher = rospy.Publisher(args.goal_topic, pose_stamped_type, queue_size=1, latch=False)
        self.context = load_runtime_context(
            run_dir=self.run_dir,
            coordinate_evidence_path=args.coordinate_evidence.resolve(),
            active_pointer_path=args.active_pointer.resolve(),
        )
        self._seen_request_id = self._current_request_id()
        self._pending: tuple[dict[str, Any], dict[str, Any]] | None = None
        self._bridge_ready = False
        self._waiting_for_subscriber_reported = False
        self._refresh_idle_readiness()

    def _current_request_id(self) -> str:
        try:
            value = read_json_object(self.request_path, "qgc_realtime_goal_request_unreadable")
        except ValueError:
            return ""
        request_id = value.get("request_id")
        return request_id if isinstance(request_id, str) else ""

    def _write_status(
        self,
        state: str,
        reason_code: str,
        *,
        request_id: str = "",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        atomic_write_json(
            self.status_path,
            build_goal_status(
                manifest=self.context["manifest"],
                state=state,
                reason_code=reason_code,
                request_id=request_id,
                details=details,
            ),
        )

    def _refresh_idle_readiness(self) -> None:
        """Expose Plan Goal only after the live planner subscribes."""

        if self._bridge_ready:
            return
        subscriber_count = int(self.publisher.get_num_connections())
        if subscriber_count >= 1:
            self._bridge_ready = True
            self._write_status(
                "ready",
                "waiting_for_new_qgc_goal",
                details={
                    "goal_topic": self.args.goal_topic,
                    "subscriber_count": subscriber_count,
                },
            )
        elif not self._waiting_for_subscriber_reported:
            self._waiting_for_subscriber_reported = True
            self._write_status(
                "awaiting_subscriber",
                "qgc_realtime_goal_planner_subscriber_missing",
                details={
                    "goal_topic": self.args.goal_topic,
                    "subscriber_count": subscriber_count,
                },
            )

    def _load_validated_request_context(
        self,
        request: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Bind a request to the runtime context immediately before use."""

        context = load_runtime_context(
            run_dir=self.run_dir,
            coordinate_evidence_path=self.args.coordinate_evidence.resolve(),
            active_pointer_path=self.args.active_pointer.resolve(),
        )
        return normalize_goal_request(request, manifest=context["manifest"]), context

    def _read_new_request(self) -> None:
        try:
            raw = read_json_object(self.request_path, "qgc_realtime_goal_request_unreadable")
        except ValueError:
            return
        request_id = raw.get("request_id")
        if not isinstance(request_id, str) or request_id == self._seen_request_id:
            return
        self._seen_request_id = request_id
        try:
            request, context = self._load_validated_request_context(raw)
            self.context = context
        except ValueError as exc:
            self._write_status("rejected", str(exc), request_id=request_id)
            return
        self._pending = (request, context)

    def _forward_pending_request(self) -> None:
        if self._pending is None:
            return
        request, context = self._pending
        request_id = request["request_id"]
        try:
            # A goal may wait for a planner subscription. Do not release it if
            # the active run or coordinate evidence changed during that wait.
            request, context = self._load_validated_request_context(request)
            self._pending = (request, context)
        except ValueError as exc:
            self.context = context
            self._write_status("rejected", str(exc), request_id=request_id)
            self._pending = None
            return
        try:
            age_s = validate_request_freshness(
                request,
                now_unix_s=time.time(),
                max_request_age_s=self.args.max_request_age_s,
                max_future_skew_s=self.args.max_future_skew_s,
            )
        except ValueError as exc:
            self.context = context
            self._write_status("rejected", str(exc), request_id=request_id)
            self._pending = None
            return
        subscriber_count = int(self.publisher.get_num_connections())
        if subscriber_count < 1:
            self.context = context
            self._write_status(
                "awaiting_subscriber",
                "qgc_realtime_goal_planner_subscriber_missing",
                request_id=request_id,
                details={
                    "goal_topic": self.args.goal_topic,
                    "subscriber_count": subscriber_count,
                    "request_age_s": age_s,
                },
            )
            return
        try:
            outgoing = build_live_goal(
                request,
                manifest=context["manifest"],
                coordinate_evidence=context["coordinate_evidence"],
                goal_frame=self.args.goal_frame,
                ground_z_m=self.args.ground_z_m,
            )
        except ValueError as exc:
            self.context = context
            self._write_status("rejected", str(exc), request_id=request_id)
            self._pending = None
            return
        message = self.pose_stamped_type()
        message.header.stamp = self.rospy.Time.now()
        message.header.frame_id = outgoing["frame_id"]
        message.pose.position.x = outgoing["position"]["x"]
        message.pose.position.y = outgoing["position"]["y"]
        message.pose.position.z = outgoing["position"]["z"]
        message.pose.orientation.w = 1.0
        self.publisher.publish(message)
        self.context = context
        self._write_status(
            "forwarded",
            "qgc_realtime_goal_ros_published",
            request_id=request_id,
            details={
                "transport": "live_ros1",
                "goal_topic": self.args.goal_topic,
                "subscriber_count": subscriber_count,
                "request_age_s": age_s,
                "coordinate_evidence_sha256": context["coordinate_evidence_sha256"],
                "goal": outgoing,
            },
        )
        self._pending = None

    def spin(self) -> None:
        rate = self.rospy.Rate(self.args.poll_hz)
        while not self.rospy.is_shutdown():
            self._refresh_idle_readiness()
            self._read_new_request()
            self._forward_pending_request()
            rate.sleep()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--coordinate-evidence", type=Path, required=True)
    parser.add_argument(
        "--active-pointer",
        type=Path,
        default=ROOT / "Results" / "ui_platform" / "qgc_active_run.json",
    )
    parser.add_argument("--goal-topic", default="/move_base_simple/goal")
    parser.add_argument("--goal-frame", default="world")
    parser.add_argument(
        "--ground-z-m",
        type=float,
        default=0.0,
        help="Ground-plane Z for the RViz-compatible input; planner adapters own flight height.",
    )
    parser.add_argument("--poll-hz", type=float, default=10.0)
    parser.add_argument("--max-request-age-s", type=float, default=5.0)
    parser.add_argument("--max-future-skew-s", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if (
        not args.goal_topic
        or not args.goal_frame
        or not math.isfinite(args.ground_z_m)
        or not math.isfinite(args.poll_hz)
        or args.poll_hz <= 0.0
        or not math.isfinite(args.max_request_age_s)
        or args.max_request_age_s <= 0.0
        or not math.isfinite(args.max_future_skew_s)
        or args.max_future_skew_s < 0.0
    ):
        print(json.dumps({"status": "blocked", "reason_code": "qgc_realtime_goal_arguments_invalid"}))
        return 2
    try:
        import rospy
        from geometry_msgs.msg import PoseStamped
    except ImportError:
        print(json.dumps({"status": "blocked", "reason_code": "qgc_realtime_goal_ros1_unavailable"}))
        return 2
    try:
        rospy.init_node("mosim_qgc_realtime_goal_bridge", anonymous=False)
        RealtimeGoalBridge(args=args, rospy=rospy, pose_stamped_type=PoseStamped).spin()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason_code": str(exc)}, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
