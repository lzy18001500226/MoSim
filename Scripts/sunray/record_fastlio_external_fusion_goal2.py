#!/usr/bin/env python3
"""Record Goal 2 FAST-LIO -> Sunray external_fusion evidence.

This recorder is intentionally no-flight. It subscribes only; it does not arm,
publish setpoints, or start a controller mission.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any, Callable

import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import AttitudeTarget, PositionTarget, State
from nav_msgs.msg import Odometry
from sunray_msgs.msg import PX4State, UAVState


def stamp_to_sec(stamp: Any) -> float | None:
    try:
        return float(stamp.secs) + float(stamp.nsecs) * 1e-9
    except Exception:
        return None


def yaw_from_quat(q: Any) -> float:
    x, y, z, w = float(q.x), float(q.y), float(q.z), float(q.w)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def quat_angle_error(a: Any, b: Any) -> float:
    dot = float(a.x) * float(b.x) + float(a.y) * float(b.y) + float(a.z) * float(b.z) + float(a.w) * float(b.w)
    dot = min(1.0, max(-1.0, abs(dot)))
    return 2.0 * math.acos(dot)


def angle_diff(a: float, b: float) -> float:
    return math.atan2(math.sin(a - b), math.cos(a - b))


def pos_tuple(p: Any) -> tuple[float, float, float]:
    return float(p.x), float(p.y), float(p.z)


def dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def gap_stats(values: list[float]) -> dict[str, Any]:
    if len(values) < 2:
        return {"count": len(values)}
    gaps = [b - a for a, b in zip(values, values[1:])]
    elapsed = values[-1] - values[0]
    return {
        "count": len(values),
        "avg_hz": (len(values) - 1) / elapsed if elapsed > 0 else None,
        "min_gap_s": min(gaps),
        "max_gap_s": max(gaps),
        "negative_gap_count": sum(1 for gap in gaps if gap < -1e-6),
        "first": values[0],
        "last": values[-1],
    }


def scalar_stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def odom_sample(msg: Odometry) -> dict[str, Any]:
    p = msg.pose.pose.position
    q = msg.pose.pose.orientation
    return {
        "frame_id": msg.header.frame_id,
        "child_frame_id": msg.child_frame_id,
        "stamp": stamp_to_sec(msg.header.stamp),
        "position": {"x": float(p.x), "y": float(p.y), "z": float(p.z)},
        "quaternion": {"x": float(q.x), "y": float(q.y), "z": float(q.z), "w": float(q.w)},
        "yaw_rad": yaw_from_quat(q),
    }


def pose_sample(msg: PoseStamped) -> dict[str, Any]:
    p = msg.pose.position
    q = msg.pose.orientation
    return {
        "frame_id": msg.header.frame_id,
        "stamp": stamp_to_sec(msg.header.stamp),
        "position": {"x": float(p.x), "y": float(p.y), "z": float(p.z)},
        "quaternion": {"x": float(q.x), "y": float(q.y), "z": float(q.z), "w": float(q.w)},
        "yaw_rad": yaw_from_quat(q),
    }


class TopicRecord:
    def __init__(self) -> None:
        self.wall: list[float] = []
        self.header: list[float] = []
        self.frame_ids: list[str] = []
        self.child_frame_ids: list[str] = []
        self.first: Any = None
        self.last: Any = None

    def add(self, sample: dict[str, Any]) -> None:
        self.wall.append(time.time())
        stamp = sample.get("stamp")
        if stamp is not None:
            self.header.append(float(stamp))
        frame_id = sample.get("frame_id")
        if frame_id:
            self.frame_ids.append(str(frame_id))
        child = sample.get("child_frame_id")
        if child:
            self.child_frame_ids.append(str(child))
        if self.first is None:
            self.first = sample
        self.last = sample

    def summary(self) -> dict[str, Any]:
        return {
            "wall_stats": gap_stats(self.wall),
            "header_stats": gap_stats(self.header),
            "unique_frame_ids": sorted(set(self.frame_ids)),
            "unique_child_frame_ids": sorted(set(self.child_frame_ids)),
            "first": self.first,
            "last": self.last,
        }


class Goal2Recorder:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.records: dict[str, TopicRecord] = {}
        self.latest_aligned: Odometry | None = None
        self.latest_local: Odometry | None = None
        self.latest_mavros_state: State | None = None
        self.mavros_armed_true_count = 0
        self.vision_vs_aligned_pos: list[float] = []
        self.vision_vs_aligned_yaw: list[float] = []
        self.vision_vs_aligned_quat: list[float] = []
        self.external_vs_aligned_pos: list[float] = []
        self.external_vs_aligned_yaw: list[float] = []
        self.local_vs_aligned_pos: list[float] = []
        self.local_vs_aligned_yaw: list[float] = []
        self.external_source_values: list[int] = []
        self.odom_valid_values: list[bool] = []
        self.fusion_success_values: list[bool] = []
        self.setpoint_counts = {"attitude": 0, "local": 0}

    def rec(self, name: str) -> TopicRecord:
        return self.records.setdefault(name, TopicRecord())

    def add_odom(self, name: str, msg: Odometry) -> None:
        self.rec(name).add(odom_sample(msg))

    def add_pose(self, name: str, msg: PoseStamped) -> None:
        self.rec(name).add(pose_sample(msg))

    def on_aligned(self, msg: Odometry) -> None:
        self.latest_aligned = msg
        self.add_odom("fastlio_aligned_odom", msg)
        if self.latest_local is not None:
            self.compare_local_to_aligned(self.latest_local, msg)

    def on_local(self, msg: Odometry) -> None:
        self.latest_local = msg
        self.add_odom("mavros_local_odom", msg)
        if self.latest_aligned is not None:
            self.compare_local_to_aligned(msg, self.latest_aligned)

    def on_vision_pose(self, msg: PoseStamped) -> None:
        self.add_pose("mavros_vision_pose", msg)
        aligned = self.latest_aligned
        if aligned is None:
            return
        self.vision_vs_aligned_pos.append(dist(pos_tuple(msg.pose.position), pos_tuple(aligned.pose.pose.position)))
        self.vision_vs_aligned_yaw.append(abs(angle_diff(yaw_from_quat(msg.pose.orientation), yaw_from_quat(aligned.pose.pose.orientation))))
        self.vision_vs_aligned_quat.append(quat_angle_error(msg.pose.orientation, aligned.pose.pose.orientation))

    def on_px4_state(self, msg: PX4State) -> None:
        sample = {
            "stamp": stamp_to_sec(msg.header.stamp),
            "connected": bool(msg.connected),
            "armed": bool(msg.armed),
            "mode": msg.mode,
            "external_odom": {
                "external_source": int(msg.external_odom.external_source),
                "odom_valid": bool(msg.external_odom.odom_valid),
                "fusion_success": bool(msg.external_odom.fusion_success),
                "position": [float(v) for v in msg.external_odom.position],
                "velocity": [float(v) for v in msg.external_odom.velocity],
                "attitude": [float(v) for v in msg.external_odom.attitude],
                "attitude_q": {
                    "x": float(msg.external_odom.attitude_q.x),
                    "y": float(msg.external_odom.attitude_q.y),
                    "z": float(msg.external_odom.attitude_q.z),
                    "w": float(msg.external_odom.attitude_q.w),
                },
            },
            "local_position": [float(v) for v in msg.position],
            "local_velocity": [float(v) for v in msg.velocity],
        }
        self.rec("sunray_px4_state").add(sample)
        self.external_source_values.append(int(msg.external_odom.external_source))
        self.odom_valid_values.append(bool(msg.external_odom.odom_valid))
        self.fusion_success_values.append(bool(msg.external_odom.fusion_success))
        if msg.armed:
            self.mavros_armed_true_count += 1
        aligned = self.latest_aligned
        if aligned is None:
            return
        ext_pos = tuple(float(v) for v in msg.external_odom.position)
        self.external_vs_aligned_pos.append(dist(ext_pos, pos_tuple(aligned.pose.pose.position)))
        ext_yaw = float(msg.external_odom.attitude[2])
        self.external_vs_aligned_yaw.append(abs(angle_diff(ext_yaw, yaw_from_quat(aligned.pose.pose.orientation))))

    def on_uav_state(self, msg: UAVState) -> None:
        sample = {
            "stamp": stamp_to_sec(msg.header.stamp),
            "connected": bool(msg.connected),
            "armed": bool(msg.armed),
            "mode": msg.mode,
            "position": [float(v) for v in msg.position],
            "velocity": [float(v) for v in msg.velocity],
            "attitude": [float(v) for v in msg.attitude],
        }
        self.rec("sunray_uav_state").add(sample)
        if msg.armed:
            self.mavros_armed_true_count += 1

    def on_mavros_state(self, msg: State) -> None:
        self.latest_mavros_state = msg
        sample = {
            "stamp": None,
            "connected": bool(msg.connected),
            "armed": bool(msg.armed),
            "guided": bool(msg.guided),
            "mode": msg.mode,
        }
        self.rec("mavros_state").add(sample)
        if msg.armed:
            self.mavros_armed_true_count += 1

    def compare_local_to_aligned(self, local: Odometry, aligned: Odometry) -> None:
        self.local_vs_aligned_pos.append(dist(pos_tuple(local.pose.pose.position), pos_tuple(aligned.pose.pose.position)))
        self.local_vs_aligned_yaw.append(abs(angle_diff(yaw_from_quat(local.pose.pose.orientation), yaw_from_quat(aligned.pose.pose.orientation))))

    def on_setpoint(self, name: str) -> Callable[[Any], None]:
        def cb(_: Any) -> None:
            self.setpoint_counts[name] += 1

        return cb

    def run(self) -> dict[str, Any]:
        rospy.init_node("mosim_fastlio_external_fusion_goal2_recorder", anonymous=True, disable_signals=True)
        subscribers = [
            rospy.Subscriber(self.args.aligned_odom_topic, Odometry, self.on_aligned, queue_size=100),
            rospy.Subscriber(self.args.local_odom_topic, Odometry, self.on_local, queue_size=100),
            rospy.Subscriber(self.args.vision_pose_topic, PoseStamped, self.on_vision_pose, queue_size=100),
            rospy.Subscriber(self.args.px4_state_topic, PX4State, self.on_px4_state, queue_size=100),
            rospy.Subscriber(self.args.uav_state_topic, UAVState, self.on_uav_state, queue_size=50),
            rospy.Subscriber(self.args.mavros_state_topic, State, self.on_mavros_state, queue_size=50),
            rospy.Subscriber(self.args.setpoint_attitude_topic, AttitudeTarget, self.on_setpoint("attitude"), queue_size=10),
            rospy.Subscriber(self.args.setpoint_local_topic, PositionTarget, self.on_setpoint("local"), queue_size=10),
        ]
        start = time.time()
        while not rospy.is_shutdown() and time.time() - start < self.args.duration_s:
            time.sleep(0.05)
        for subscriber in subscribers:
            subscriber.unregister()
        return self.summary(time.time() - start)

    def summary(self, duration_wall_s: float) -> dict[str, Any]:
        topics = {name: rec.summary() for name, rec in self.records.items()}
        negative_header_gaps = {
            name: data.get("header_stats", {}).get("negative_gap_count", 0)
            for name, data in topics.items()
        }
        comparison = {
            "vision_pose_vs_aligned_position_m": scalar_stats(self.vision_vs_aligned_pos),
            "vision_pose_vs_aligned_yaw_rad": scalar_stats(self.vision_vs_aligned_yaw),
            "vision_pose_vs_aligned_quat_angle_rad": scalar_stats(self.vision_vs_aligned_quat),
            "px4_state_external_odom_vs_aligned_position_m": scalar_stats(self.external_vs_aligned_pos),
            "px4_state_external_odom_vs_aligned_yaw_rad": scalar_stats(self.external_vs_aligned_yaw),
            "mavros_local_odom_vs_aligned_position_m": scalar_stats(self.local_vs_aligned_pos),
            "mavros_local_odom_vs_aligned_yaw_rad": scalar_stats(self.local_vs_aligned_yaw),
        }
        checks = {
            "aligned_odom_present": topics.get("fastlio_aligned_odom", {}).get("wall_stats", {}).get("count", 0) > 0,
            "vision_pose_present": topics.get("mavros_vision_pose", {}).get("wall_stats", {}).get("count", 0) > 0,
            "px4_state_present": topics.get("sunray_px4_state", {}).get("wall_stats", {}).get("count", 0) > 0,
            "local_odom_present": topics.get("mavros_local_odom", {}).get("wall_stats", {}).get("count", 0) > 0,
            "mavros_state_present": topics.get("mavros_state", {}).get("wall_stats", {}).get("count", 0) > 0,
            "aligned_frame_world": "world" in topics.get("fastlio_aligned_odom", {}).get("unique_frame_ids", []),
            "aligned_child_base_link": "base_link" in topics.get("fastlio_aligned_odom", {}).get("unique_child_frame_ids", []),
            "external_source_all_odom": bool(self.external_source_values) and all(v == 0 for v in self.external_source_values),
            "external_odom_valid_seen": any(self.odom_valid_values),
            "external_odom_valid_last": self.odom_valid_values[-1] if self.odom_valid_values else False,
            "fusion_success_seen": any(self.fusion_success_values),
            "fusion_success_last": self.fusion_success_values[-1] if self.fusion_success_values else False,
            "mavros_or_sunray_armed_true_count": self.mavros_armed_true_count,
            "setpoint_attitude_count": self.setpoint_counts["attitude"],
            "setpoint_local_count": self.setpoint_counts["local"],
            "negative_header_gaps": negative_header_gaps,
        }
        pass_through_ok = (
            comparison["vision_pose_vs_aligned_position_m"].get("max", float("inf")) <= self.args.pass_through_position_tolerance_m
            and comparison["px4_state_external_odom_vs_aligned_position_m"].get("max", float("inf")) <= self.args.pass_through_position_tolerance_m
            and comparison["vision_pose_vs_aligned_quat_angle_rad"].get("max", float("inf")) <= self.args.pass_through_attitude_tolerance_rad
        )
        local_comparable_ok = comparison["mavros_local_odom_vs_aligned_position_m"].get("max", float("inf")) <= self.args.local_comparable_position_tolerance_m
        gate_pass = (
            checks["aligned_odom_present"]
            and checks["vision_pose_present"]
            and checks["px4_state_present"]
            and checks["local_odom_present"]
            and checks["mavros_state_present"]
            and checks["aligned_frame_world"]
            and checks["aligned_child_base_link"]
            and checks["external_source_all_odom"]
            and checks["external_odom_valid_seen"]
            and checks["external_odom_valid_last"]
            and checks["mavros_or_sunray_armed_true_count"] == 0
            and checks["setpoint_attitude_count"] == 0
            and checks["setpoint_local_count"] == 0
            and all(count == 0 for count in negative_header_gaps.values())
            and pass_through_ok
            and local_comparable_ok
        )
        return {
            "schema": "mosim.sunray_ros1.fastlio_external_fusion_goal2.v1",
            "duration_requested_s": self.args.duration_s,
            "duration_wall_s": duration_wall_s,
            "claim_boundary": {
                "no_arming": True,
                "no_setpoint_publication": True,
                "no_px4ctrl_mission": True,
                "external_source": "ODOM",
                "use_vision_pose": True,
                "position_topic": self.args.aligned_odom_topic,
                "fusion_success_is_recorded_not_required_for_goal2": True,
            },
            "topics": topics,
            "comparison": comparison,
            "checks": checks,
            "thresholds": {
                "pass_through_position_tolerance_m": self.args.pass_through_position_tolerance_m,
                "pass_through_attitude_tolerance_rad": self.args.pass_through_attitude_tolerance_rad,
                "local_comparable_position_tolerance_m": self.args.local_comparable_position_tolerance_m,
            },
            "gate_pass": gate_pass,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=25.0)
    parser.add_argument("--out", required=True)
    parser.add_argument("--aligned-odom-topic", default="/mosim/fastlio/odom_aligned")
    parser.add_argument("--local-odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--vision-pose-topic", default="/uav1/mavros/vision_pose/pose")
    parser.add_argument("--px4-state-topic", default="/uav1/sunray/px4_state")
    parser.add_argument("--uav-state-topic", default="/uav1/sunray/uav_state")
    parser.add_argument("--mavros-state-topic", default="/uav1/mavros/state")
    parser.add_argument("--setpoint-attitude-topic", default="/uav1/mavros/setpoint_raw/attitude")
    parser.add_argument("--setpoint-local-topic", default="/uav1/mavros/setpoint_raw/local")
    parser.add_argument("--pass-through-position-tolerance-m", type=float, default=0.02)
    parser.add_argument("--pass-through-attitude-tolerance-rad", type=float, default=0.02)
    parser.add_argument("--local-comparable-position-tolerance-m", type=float, default=0.10)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = Goal2Recorder(args).run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["gate_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
