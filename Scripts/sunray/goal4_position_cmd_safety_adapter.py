#!/usr/bin/env python3
"""Safety/hold adapter for planner PositionCommand streams.

This node is intentionally narrow: it keeps the planner output observable on a
raw topic, then publishes the px4ctrl-facing command with a bounded altitude
envelope and a continuous final hold. It is used for Diff-Planner integration,
whose traj_server stops publishing at trajectory end and can produce low-Z
transients in the current Sunray150 pillar map.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import rospy
import sensor_msgs.point_cloud2 as pc2
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import PositionCommand
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool

from trajectory_dynamics import constrain_kinematic_step, enforce_position_z_bounds


class PositionCmdSafetyAdapter:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/diff_planner/position_cmd_raw")
        self.output_topic = rospy.get_param("~output_topic", "/position_cmd")
        self.rate_hz = float(rospy.get_param("~rate_hz", 100.0))
        self.min_z = float(rospy.get_param("~min_z", 0.85))
        self.max_z = float(rospy.get_param("~max_z", 1.35))
        fixed_z_raw = str(rospy.get_param("~fixed_z", "")).strip()
        self.fixed_z = float(fixed_z_raw) if fixed_z_raw else None
        fixed_yaw_raw = str(rospy.get_param("~fixed_yaw", "")).strip()
        self.fixed_yaw = float(fixed_yaw_raw) if fixed_yaw_raw else None
        self.input_timeout_s = float(rospy.get_param("~input_timeout_s", 0.30))
        self.invalid_z_policy = str(rospy.get_param("~invalid_z_policy", "hold_last_safe"))
        self.jump_guard_enabled = bool(rospy.get_param("~jump_guard_enabled", True))
        self.max_position_jump_m = float(rospy.get_param("~max_position_jump_m", 0.0))
        self.max_position_jump_speed_mps = float(rospy.get_param("~max_position_jump_speed_mps", 3.0))
        self.jump_guard_min_dt_s = float(rospy.get_param("~jump_guard_min_dt_s", 0.05))
        self.smoothing_enabled = bool(rospy.get_param("~smoothing_enabled", False))
        self.smoothing_max_speed_mps = float(rospy.get_param("~smoothing_max_speed_mps", 0.0))
        self.smoothing_max_step_m = float(rospy.get_param("~smoothing_max_step_m", 0.0))
        self.smoothing_max_dt_s = float(rospy.get_param("~smoothing_max_dt_s", 0.05))
        self.smoothing_zero_dynamics = bool(rospy.get_param("~smoothing_zero_dynamics", True))
        self.motion_time_basis = str(rospy.get_param("~motion_time_basis", "wall")).strip().lower()
        if self.motion_time_basis not in ("wall", "ros_sim_time"):
            raise ValueError("~motion_time_basis must be 'wall' or 'ros_sim_time'")
        self.recompute_velocity_from_position = bool(
            rospy.get_param("~recompute_velocity_from_position", False)
        )
        self.max_acceleration_mps2 = float(rospy.get_param("~max_acceleration_mps2", 0.0))
        self.max_velocity_mps = float(rospy.get_param("~max_velocity_mps", 0.0))
        self.max_lateral_acceleration_mps2 = float(
            rospy.get_param("~max_lateral_acceleration_mps2", 0.0)
        )
        self.max_jerk_mps3 = float(rospy.get_param("~max_jerk_mps3", 0.0))
        self.zero_all_dynamics = bool(rospy.get_param("~zero_all_dynamics", False))
        self.odom_target_guard_enabled = bool(rospy.get_param("~odom_target_guard_enabled", False))
        self.odom_topic = rospy.get_param("~odom_topic", "")
        self.odom_timeout_s = float(rospy.get_param("~odom_timeout_s", 0.30))
        self.max_target_distance_from_odom_m = float(rospy.get_param("~max_target_distance_from_odom_m", 0.0))
        self.max_xy_target_distance_from_odom_m = float(
            rospy.get_param("~max_xy_target_distance_from_odom_m", 0.0)
        )
        self.odom_distance_policy = str(rospy.get_param("~odom_distance_policy", "project_toward_raw"))
        self.odom_guard_zero_dynamics = bool(rospy.get_param("~odom_guard_zero_dynamics", True))
        self.seed_from_odom_on_enable = bool(rospy.get_param("~seed_from_odom_on_enable", False))
        self.enable_topic = rospy.get_param("~enable_topic", "/mosim/goal4/position_cmd_adapter_enable")
        self.enabled = bool(rospy.get_param("~initial_enabled", True))
        self.require_fresh_raw_after_enable = bool(rospy.get_param("~require_fresh_raw_after_enable", True))
        self.map_guard_enabled = bool(rospy.get_param("~map_guard_enabled", False))
        self.map_guard_cloud_topic = str(rospy.get_param("~map_guard_cloud_topic", "")).strip()
        self.map_guard_occupancy_topic = str(rospy.get_param("~map_guard_occupancy_topic", "")).strip()
        self.map_guard_timeout_s = max(0.0, float(rospy.get_param("~map_guard_timeout_s", 1.0)))
        self.map_guard_min_cloud_points = max(1, int(rospy.get_param("~map_guard_min_cloud_points", 1)))
        self.map_guard_min_occupancy_points = max(
            1, int(rospy.get_param("~map_guard_min_occupancy_points", 1))
        )
        self.map_collision_guard_enabled = bool(
            rospy.get_param("~map_collision_guard_enabled", False)
        )
        self.map_collision_radius_m = max(
            0.0, float(rospy.get_param("~map_collision_radius_m", 0.30))
        )
        self.map_collision_z_margin_m = max(
            0.0, float(rospy.get_param("~map_collision_z_margin_m", 0.25))
        )
        self.map_collision_sample_step_m = max(
            0.02, float(rospy.get_param("~map_collision_sample_step_m", 0.06))
        )
        self.map_collision_max_points = max(
            1, int(rospy.get_param("~map_collision_max_points", 10000))
        )
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")

        self.last_raw: PositionCommand | None = None
        self.last_raw_wall = 0.0
        self.last_raw_motion: float | None = None
        self.prev_raw_wall: float | None = None
        self.last_publish_wall = 0.0
        self.last_accepted_wall: float | None = None
        self.last_accepted_raw_wall: float | None = None
        self.last_safe_msg: PositionCommand | None = None
        self.raw_count = 0
        self.published_count = 0
        self.clamped_low_count = 0
        self.clamped_high_count = 0
        self.hold_publish_count = 0
        self.invalid_z_rejected_low_count = 0
        self.invalid_z_rejected_high_count = 0
        self.invalid_z_hold_publish_count = 0
        self.invalid_z_clamp_fallback_count = 0
        self.invalid_z_clamp_policy_count = 0
        self.jump_rejected_count = 0
        self.jump_hold_publish_count = 0
        self.max_observed_jump_m = 0.0
        self.max_observed_jump_speed_mps = 0.0
        self.max_published_jump_m = 0.0
        self.max_published_jump_speed_mps = 0.0
        self.large_distance_jump_observed_count = 0
        self.smoothing_applied_count = 0
        self.smoothing_limited_distance_m = 0.0
        self.last_smoothing: dict | None = None
        self.odom_count = 0
        self.last_odom_wall: float | None = None
        self.last_odom_xyz: list[float] | None = None
        self.odom_guard_applied_count = 0
        self.odom_guard_hold_count = 0
        self.odom_guard_skipped_no_odom_count = 0
        self.odom_guard_skipped_stale_count = 0
        self.max_observed_target_distance_from_odom_m = 0.0
        self.max_observed_xy_target_distance_from_odom_m = 0.0
        self.max_published_target_distance_from_odom_m = 0.0
        self.max_published_xy_target_distance_from_odom_m = 0.0
        self.last_odom_guard: dict | None = None
        self.last_rejected_jump: dict | None = None
        self.last_observed_jump: dict | None = None
        self.last_rejected_z: dict | None = None
        self.last_reject_reason: str | None = None
        self.first_raw_wall: float | None = None
        self.last_raw_z: float | None = None
        self.last_raw_xyz: list[float] | None = None
        self.last_published_xyz: list[float] | None = None
        self.last_raw_velocity_xyz: list[float] | None = None
        self.last_raw_acceleration_xyz: list[float] | None = None
        self.last_raw_yaw: float | None = None
        self.last_published_wall: float | None = None
        self.last_published_motion_time: float | None = None
        self.last_accepted_motion_time: float | None = None
        self.last_publish_stale = False
        self.min_raw_z: float | None = None
        self.min_published_z: float | None = None
        self.max_published_z: float | None = None
        self.enable_update_count = 0
        self.disabled_publish_skip_count = 0
        self.last_enable_wall: float | None = None
        self.waiting_fresh_raw_after_enable = False
        self.fresh_raw_after_enable_count = 0
        self.dynamics_limited_count = 0
        self.max_published_acceleration_mps2 = 0.0
        self.max_published_lateral_acceleration_mps2 = 0.0
        self.max_published_jerk_mps3 = 0.0
        self.last_dynamics_limit: dict | None = None
        self.post_dynamics_z_clamp_count = 0
        self.last_map_cloud_wall = 0.0
        self.last_map_cloud_points = 0
        self.last_map_cloud_stamp = 0.0
        self.last_occupancy_cloud_wall = 0.0
        self.last_occupancy_cloud_points = 0
        self.last_occupancy_cloud_stamp = 0.0
        self.map_guard_not_ready_count = 0
        self.map_guard_ready_count = 0
        self.map_guard_hold_count = 0
        self.last_map_guard: dict | None = None
        self.last_occupancy_points: list[tuple[float, float, float]] = []
        self.last_occupancy_frame_id = ""
        self.map_collision_guard_count = 0
        self.map_collision_hold_count = 0
        self.last_map_collision: dict | None = None

        self.pub = rospy.Publisher(self.output_topic, PositionCommand, queue_size=20)
        rospy.Subscriber(self.input_topic, PositionCommand, self.on_raw, queue_size=50)
        rospy.Subscriber(self.enable_topic, Bool, self.on_enable, queue_size=5)
        if self.map_guard_enabled or self.map_collision_guard_enabled:
            if self.map_guard_enabled and not self.map_guard_cloud_topic:
                raise ValueError("~map_guard_cloud_topic is required when ~map_guard_enabled is true")
            if not self.map_guard_occupancy_topic:
                raise ValueError(
                    "~map_guard_occupancy_topic is required when a map guard is enabled"
                )
            if self.map_guard_enabled:
                rospy.Subscriber(
                    self.map_guard_cloud_topic,
                    PointCloud2,
                    self.on_map_cloud,
                    callback_args="planner_cloud",
                    queue_size=5,
                )
            rospy.Subscriber(
                self.map_guard_occupancy_topic,
                PointCloud2,
                self.on_map_cloud,
                callback_args="occupancy_inflate",
                queue_size=5,
            )
        if (self.odom_target_guard_enabled or self.seed_from_odom_on_enable or self.map_guard_enabled) and self.odom_topic:
            rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=50)

    @staticmethod
    def clone_msg(src: PositionCommand) -> PositionCommand:
        msg = PositionCommand()
        msg.header = src.header
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = src.header.frame_id or "world"
        msg.trajectory_flag = src.trajectory_flag
        msg.trajectory_id = src.trajectory_id
        msg.position.x = src.position.x
        msg.position.y = src.position.y
        msg.position.z = src.position.z
        msg.velocity.x = src.velocity.x
        msg.velocity.y = src.velocity.y
        msg.velocity.z = src.velocity.z
        msg.acceleration.x = src.acceleration.x
        msg.acceleration.y = src.acceleration.y
        msg.acceleration.z = src.acceleration.z
        msg.jerk.x = src.jerk.x
        msg.jerk.y = src.jerk.y
        msg.jerk.z = src.jerk.z
        msg.yaw = src.yaw
        msg.yaw_dot = src.yaw_dot
        msg.kx = list(src.kx)
        msg.kv = list(src.kv)
        return msg

    @staticmethod
    def zero_dynamic_terms(msg: PositionCommand) -> None:
        msg.velocity.x = 0.0
        msg.velocity.y = 0.0
        msg.velocity.z = 0.0
        msg.acceleration.x = 0.0
        msg.acceleration.y = 0.0
        msg.acceleration.z = 0.0
        msg.jerk.x = 0.0
        msg.jerk.y = 0.0
        msg.jerk.z = 0.0
        msg.yaw_dot = 0.0

    def motion_time(self, now_wall: float) -> float:
        if self.motion_time_basis == "ros_sim_time":
            now_ros = float(rospy.Time.now().to_sec())
            if now_ros > 0.0:
                return now_ros
        return now_wall

    def seed_msg_from_odom(self) -> PositionCommand | None:
        if self.last_odom_xyz is None:
            return None
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = "world"
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        msg.trajectory_id = 0
        msg.position.x = float(self.last_odom_xyz[0])
        msg.position.y = float(self.last_odom_xyz[1])
        seed_z = float(self.last_odom_xyz[2])
        if self.fixed_z is not None:
            seed_z = float(self.fixed_z)
        msg.position.z = min(max(seed_z, self.min_z), self.max_z)
        self.zero_dynamic_terms(msg)
        msg.yaw = 0.0
        if self.fixed_yaw is not None:
            msg.yaw = float(self.fixed_yaw)
        msg.yaw_dot = 0.0
        return msg

    def on_raw(self, msg: PositionCommand) -> None:
        self.raw_count += 1
        now = time.time()
        self.last_raw_motion = self.motion_time(now)
        if self.first_raw_wall is None:
            self.first_raw_wall = now
        self.prev_raw_wall = self.last_raw_wall if self.last_raw_wall > 0.0 else None
        self.last_raw_wall = now
        self.last_raw = msg
        self.last_raw_z = float(msg.position.z)
        self.last_raw_xyz = [float(msg.position.x), float(msg.position.y), float(msg.position.z)]
        self.last_raw_velocity_xyz = [float(msg.velocity.x), float(msg.velocity.y), float(msg.velocity.z)]
        self.last_raw_acceleration_xyz = [
            float(msg.acceleration.x),
            float(msg.acceleration.y),
            float(msg.acceleration.z),
        ]
        self.last_raw_yaw = float(msg.yaw)
        self.min_raw_z = self.last_raw_z if self.min_raw_z is None else min(self.min_raw_z, self.last_raw_z)
        if self.waiting_fresh_raw_after_enable and self.last_enable_wall is not None and now >= self.last_enable_wall:
            self.waiting_fresh_raw_after_enable = False
            self.fresh_raw_after_enable_count += 1

    def on_odom(self, msg: Odometry) -> None:
        self.odom_count += 1
        self.last_odom_wall = time.time()
        self.last_odom_xyz = [
            float(msg.pose.pose.position.x),
            float(msg.pose.pose.position.y),
            float(msg.pose.pose.position.z),
        ]

    @staticmethod
    def pointcloud_point_count(msg: PointCloud2) -> int:
        return max(0, int(getattr(msg, "width", 0))) * max(1, int(getattr(msg, "height", 1)))

    def on_map_cloud(self, msg: PointCloud2, stream: str) -> None:
        now_wall = time.time()
        point_count = self.pointcloud_point_count(msg)
        stamp = float(msg.header.stamp.to_sec()) if msg.header and msg.header.stamp else 0.0
        if stream == "planner_cloud":
            self.last_map_cloud_wall = now_wall
            self.last_map_cloud_points = point_count
            self.last_map_cloud_stamp = stamp
        elif stream == "occupancy_inflate":
            self.last_occupancy_cloud_wall = now_wall
            self.last_occupancy_cloud_points = point_count
            self.last_occupancy_cloud_stamp = stamp
            self.last_occupancy_frame_id = str(getattr(msg.header, "frame_id", "") or "")
            if self.map_collision_guard_enabled:
                points: list[tuple[float, float, float]] = []
                for point in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
                    x, y, z = float(point[0]), float(point[1]), float(point[2])
                    if math.isfinite(x) and math.isfinite(y) and math.isfinite(z):
                        points.append((x, y, z))
                        if len(points) >= self.map_collision_max_points:
                            break
                self.last_occupancy_points = points

    def map_guard_snapshot(self, now_wall: float) -> dict:
        if not self.map_guard_enabled:
            return {"enabled": False, "ready": True, "reasons": []}

        cloud_age_s = (
            now_wall - self.last_map_cloud_wall if self.last_map_cloud_wall > 0.0 else None
        )
        occupancy_age_s = (
            now_wall - self.last_occupancy_cloud_wall
            if self.last_occupancy_cloud_wall > 0.0
            else None
        )
        reasons: list[str] = []
        if self.last_map_cloud_points < self.map_guard_min_cloud_points:
            reasons.append("planner_cloud_empty")
        if self.last_occupancy_cloud_points < self.map_guard_min_occupancy_points:
            reasons.append("occupancy_inflate_empty")
        if cloud_age_s is None or cloud_age_s > self.map_guard_timeout_s:
            reasons.append("planner_cloud_stale")
        if occupancy_age_s is None or occupancy_age_s > self.map_guard_timeout_s:
            reasons.append("occupancy_inflate_stale")
        return {
            "enabled": True,
            "ready": not reasons,
            "reasons": reasons,
            "timeout_s": self.map_guard_timeout_s,
            "planner_cloud_topic": self.map_guard_cloud_topic,
            "planner_cloud_points": self.last_map_cloud_points,
            "planner_cloud_age_s": cloud_age_s,
            "planner_cloud_stamp": self.last_map_cloud_stamp,
            "occupancy_topic": self.map_guard_occupancy_topic,
            "occupancy_points": self.last_occupancy_cloud_points,
            "occupancy_age_s": occupancy_age_s,
            "occupancy_stamp": self.last_occupancy_cloud_stamp,
        }

    def map_collision_snapshot(self, msg: PositionCommand) -> dict:
        if not self.map_collision_guard_enabled:
            return {"enabled": False, "collision": False, "reason": ""}

        candidate = (
            float(msg.position.x),
            float(msg.position.y),
            float(msg.position.z),
        )
        start = candidate
        if self.last_safe_msg is not None:
            start = (
                float(self.last_safe_msg.position.x),
                float(self.last_safe_msg.position.y),
                float(self.last_safe_msg.position.z),
            )
        if not self.last_occupancy_points:
            return {
                "enabled": True,
                "collision": False,
                "ready": False,
                "reason": "occupancy_inflate_empty",
                "candidate_xyz": list(candidate),
                "start_xyz": list(start),
                "occupancy_points": 0,
                "frame_id": self.last_occupancy_frame_id,
            }

        dx = candidate[0] - start[0]
        dy = candidate[1] - start[1]
        dz = candidate[2] - start[2]
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        sample_count = max(1, int(math.ceil(distance / self.map_collision_sample_step_m)))
        radius_sq = self.map_collision_radius_m * self.map_collision_radius_m
        for index in range(sample_count + 1):
            ratio = index / sample_count
            sample = (
                start[0] + ratio * dx,
                start[1] + ratio * dy,
                start[2] + ratio * dz,
            )
            for obstacle in self.last_occupancy_points:
                if abs(sample[2] - obstacle[2]) > self.map_collision_z_margin_m:
                    continue
                ox = sample[0] - obstacle[0]
                oy = sample[1] - obstacle[1]
                if ox * ox + oy * oy <= radius_sq:
                    return {
                        "enabled": True,
                        "collision": True,
                        "ready": True,
                        "reason": "candidate_intersects_inflated_occupancy",
                        "candidate_xyz": list(candidate),
                        "start_xyz": list(start),
                        "obstacle_xyz": list(obstacle),
                        "sample_xyz": list(sample),
                        "sample_index": index,
                        "sample_count": sample_count,
                        "distance_m": distance,
                        "radius_m": self.map_collision_radius_m,
                        "z_margin_m": self.map_collision_z_margin_m,
                        "occupancy_points": len(self.last_occupancy_points),
                        "frame_id": self.last_occupancy_frame_id,
                    }
        return {
            "enabled": True,
            "collision": False,
            "ready": True,
            "reason": "",
            "candidate_xyz": list(candidate),
            "start_xyz": list(start),
            "distance_m": distance,
            "radius_m": self.map_collision_radius_m,
            "z_margin_m": self.map_collision_z_margin_m,
            "occupancy_points": len(self.last_occupancy_points),
            "frame_id": self.last_occupancy_frame_id,
        }

    def apply_map_collision_guard(
        self, msg: PositionCommand, now_wall: float, now_motion: float
    ) -> PositionCommand | None:
        self.last_map_collision = self.map_collision_snapshot(msg)
        if not self.map_collision_guard_enabled:
            return msg
        if not self.last_map_collision.get("ready", True):
            self.last_reject_reason = self.last_map_collision["reason"]
            hold = self.hold_last_safe_msg(now_wall, "planner_map_not_ready", now_motion)
            if hold is not None:
                self.map_collision_hold_count += 1
            return hold
        if not self.last_map_collision["collision"]:
            return msg
        self.map_collision_guard_count += 1
        self.last_reject_reason = "planner_map_collision"
        hold = self.hold_last_safe_msg(now_wall, "planner_map_collision", now_motion)
        if hold is not None:
            self.map_collision_hold_count += 1
        return hold

    def on_enable(self, msg: Bool) -> None:
        was_enabled = self.enabled
        self.enabled = bool(msg.data)
        self.enable_update_count += 1
        self.last_enable_wall = time.time()
        if self.enabled and not was_enabled:
            # A new planner takeover can begin far from the previous held command.
            # Reset baselines so stale pre-takeover or mission-tail commands do
            # not poison the next trajectory stream.
            self.last_safe_msg = None
            self.last_accepted_wall = None
            self.last_accepted_raw_wall = None
            self.last_published_wall = None
            self.last_published_motion_time = None
            self.last_accepted_motion_time = None
            self.last_reject_reason = None
            self.last_rejected_jump = None
            self.last_observed_jump = None
            if self.seed_from_odom_on_enable:
                self.last_safe_msg = self.seed_msg_from_odom()
            self.waiting_fresh_raw_after_enable = bool(self.require_fresh_raw_after_enable)
        self.write_diagnostics()

    def hold_last_safe_msg(
        self, now_wall: float, reason: str, now_motion: float | None = None
    ) -> PositionCommand | None:
        if self.last_safe_msg is None and self.seed_from_odom_on_enable:
            self.last_safe_msg = self.seed_msg_from_odom()
        if self.last_safe_msg is None:
            return None
        msg = self.clone_msg(self.last_safe_msg)
        self.zero_dynamic_terms(msg)
        self.last_publish_stale = reason == "stale"
        self.last_published_xyz = [float(msg.position.x), float(msg.position.y), float(msg.position.z)]
        self.last_published_wall = now_wall
        self.last_published_motion_time = (
            self.motion_time(now_wall) if now_motion is None else now_motion
        )
        self.min_published_z = msg.position.z if self.min_published_z is None else min(self.min_published_z, msg.position.z)
        self.max_published_z = msg.position.z if self.max_published_z is None else max(self.max_published_z, msg.position.z)
        self.jump_hold_publish_count += 1 if reason == "jump" else 0
        self.invalid_z_hold_publish_count += 1 if reason == "invalid_z" else 0
        self.hold_publish_count += 1 if reason == "stale" else 0
        self.last_accepted_wall = now_wall
        return msg

    def should_reject_invalid_z(self, msg: PositionCommand, now_wall: float) -> bool:
        if msg.position.z >= self.min_z and msg.position.z <= self.max_z:
            return False

        low = msg.position.z < self.min_z
        reason = "raw_z_below_min" if low else "raw_z_above_max"
        if low:
            self.invalid_z_rejected_low_count += 1
        else:
            self.invalid_z_rejected_high_count += 1
        self.last_reject_reason = reason
        self.last_rejected_z = {
            "reason": reason,
            "raw_xyz": [float(msg.position.x), float(msg.position.y), float(msg.position.z)],
            "raw_velocity_xyz": [float(msg.velocity.x), float(msg.velocity.y), float(msg.velocity.z)],
            "raw_acceleration_xyz": [
                float(msg.acceleration.x),
                float(msg.acceleration.y),
                float(msg.acceleration.z),
            ],
            "min_z": self.min_z,
            "max_z": self.max_z,
            "wall_time": now_wall,
            "policy": self.invalid_z_policy,
        }
        return self.invalid_z_policy == "hold_last_safe"

    def should_reject_jump(
        self, msg: PositionCommand, now_wall: float, now_motion: float
    ) -> bool:
        if not self.jump_guard_enabled or self.last_safe_msg is None:
            return False
        prev = self.last_safe_msg.position
        curr = msg.position
        jump_m = math.dist(
            (float(prev.x), float(prev.y), float(prev.z)),
            (float(curr.x), float(curr.y), float(curr.z)),
        )
        dt = 0.0
        if self.last_accepted_motion_time is not None:
            dt = max(0.0, now_motion - self.last_accepted_motion_time)
        jump_speed_mps = jump_m / dt if dt > 1e-4 else 0.0
        self.max_observed_jump_m = max(self.max_observed_jump_m, jump_m)
        self.max_observed_jump_speed_mps = max(self.max_observed_jump_speed_mps, jump_speed_mps)
        self.last_observed_jump = {
            "jump_m": jump_m,
            "dt_s": dt,
            "jump_speed_mps": jump_speed_mps,
            "previous_xyz": [float(prev.x), float(prev.y), float(prev.z)],
            "candidate_xyz": [float(curr.x), float(curr.y), float(curr.z)],
            "wall_time": now_wall,
        }
        if self.max_position_jump_m > 0.0 and jump_m > self.max_position_jump_m:
            self.large_distance_jump_observed_count += 1
        reject_by_distance = (
            self.max_position_jump_m > 0.0
            and dt <= self.jump_guard_min_dt_s
            and jump_m > self.max_position_jump_m
        )
        reject_by_speed = (
            self.max_position_jump_speed_mps > 0.0
            and dt > self.jump_guard_min_dt_s
            and jump_speed_mps > self.max_position_jump_speed_mps
        )
        if not (reject_by_distance or reject_by_speed):
            return False
        reason = "position_jump" if reject_by_distance else "position_jump_speed"
        self.jump_rejected_count += 1
        self.last_reject_reason = reason
        self.last_rejected_jump = {
            "reason": reason,
            "jump_m": jump_m,
            "dt_s": dt,
            "jump_speed_mps": jump_speed_mps,
            "previous_xyz": [float(prev.x), float(prev.y), float(prev.z)],
            "candidate_xyz": [float(curr.x), float(curr.y), float(curr.z)],
            "wall_time": now_wall,
        }
        return True

    def apply_smoothing(
        self, msg: PositionCommand, now_wall: float, now_motion: float
    ) -> PositionCommand:
        if (
            not self.smoothing_enabled
            or self.last_safe_msg is None
            or (self.smoothing_max_speed_mps <= 0.0 and self.smoothing_max_step_m <= 0.0)
        ):
            return msg

        prev = self.last_safe_msg.position
        curr = msg.position
        dx = float(curr.x) - float(prev.x)
        dy = float(curr.y) - float(prev.y)
        dz = float(curr.z) - float(prev.z)
        distance_m = math.sqrt(dx * dx + dy * dy + dz * dz)
        if distance_m <= 1e-9:
            return msg

        dt = 0.0
        if self.last_published_motion_time is not None:
            dt = max(0.0, now_motion - self.last_published_motion_time)
        if dt <= 1e-4 and self.rate_hz > 0.0:
            dt = 1.0 / self.rate_hz
        if self.smoothing_max_dt_s > 0.0:
            dt = min(dt, self.smoothing_max_dt_s)

        allowed_step_m = float("inf")
        if self.smoothing_max_speed_mps > 0.0:
            allowed_step_m = min(allowed_step_m, self.smoothing_max_speed_mps * dt)
        if self.smoothing_max_step_m > 0.0:
            allowed_step_m = min(allowed_step_m, self.smoothing_max_step_m)
        if not math.isfinite(allowed_step_m) or distance_m <= allowed_step_m:
            return msg

        scale = max(0.0, allowed_step_m / distance_m)
        smoothed = self.clone_msg(msg)
        smoothed.position.x = float(prev.x) + dx * scale
        smoothed.position.y = float(prev.y) + dy * scale
        smoothed.position.z = float(prev.z) + dz * scale
        if self.smoothing_zero_dynamics:
            self.zero_dynamic_terms(smoothed)
        self.smoothing_applied_count += 1
        self.smoothing_limited_distance_m += distance_m - allowed_step_m
        self.last_smoothing = {
            "reason": "max_step",
            "raw_distance_m": distance_m,
            "allowed_step_m": allowed_step_m,
            "dt_s": dt,
            "time_basis": self.motion_time_basis,
            "scale": scale,
            "previous_xyz": [float(prev.x), float(prev.y), float(prev.z)],
            "raw_candidate_xyz": [float(curr.x), float(curr.y), float(curr.z)],
            "published_xyz": [
                float(smoothed.position.x),
                float(smoothed.position.y),
                float(smoothed.position.z),
            ],
            "wall_time": now_wall,
        }
        return smoothed

    def make_dynamics_consistent_with_position(
        self, msg: PositionCommand, now_motion: float
    ) -> PositionCommand:
        if not self.recompute_velocity_from_position or self.last_safe_msg is None:
            return msg
        dt = 1.0 / self.rate_hz if self.rate_hz > 0.0 else 0.01
        if self.last_published_motion_time is not None:
            measured_dt = max(0.0, now_motion - self.last_published_motion_time)
            if measured_dt > 1e-4:
                dt = measured_dt
        if self.smoothing_max_dt_s > 0.0:
            dt = min(dt, self.smoothing_max_dt_s)
        dt = max(dt, 1e-4)
        previous = self.last_safe_msg
        constrained = constrain_kinematic_step(
            (previous.position.x, previous.position.y, previous.position.z),
            (previous.velocity.x, previous.velocity.y, previous.velocity.z),
            (previous.acceleration.x, previous.acceleration.y, previous.acceleration.z),
            (msg.position.x, msg.position.y, msg.position.z),
            dt,
            self.max_velocity_mps,
            self.max_acceleration_mps2,
            self.max_lateral_acceleration_mps2,
            self.max_jerk_mps3,
        )
        for field, values in (
            (msg.position, constrained["position"]),
            (msg.velocity, constrained["velocity"]),
            (msg.acceleration, constrained["acceleration"]),
            (msg.jerk, constrained["jerk"]),
        ):
            field.x, field.y, field.z = values
        acceleration = constrained["acceleration"]
        jerk = constrained["jerk"]
        acceleration_norm = math.sqrt(sum(value * value for value in acceleration))
        lateral_acceleration = math.hypot(acceleration[0], acceleration[1])
        jerk_norm = math.sqrt(sum(value * value for value in jerk))
        self.max_published_acceleration_mps2 = max(
            self.max_published_acceleration_mps2, acceleration_norm
        )
        self.max_published_lateral_acceleration_mps2 = max(
            self.max_published_lateral_acceleration_mps2, lateral_acceleration
        )
        self.max_published_jerk_mps3 = max(self.max_published_jerk_mps3, jerk_norm)
        if constrained["limited"]:
            self.dynamics_limited_count += 1
            self.last_dynamics_limit = {
                "dt_s": dt,
                "position": list(constrained["position"]),
                "velocity": list(constrained["velocity"]),
                "acceleration": list(acceleration),
                "jerk": list(jerk),
            }
        return msg

    def apply_odom_target_guard(self, msg: PositionCommand, now_wall: float) -> PositionCommand | None:
        if not self.odom_target_guard_enabled:
            return msg
        if self.max_target_distance_from_odom_m <= 0.0 and self.max_xy_target_distance_from_odom_m <= 0.0:
            return msg
        if self.last_odom_xyz is None or self.last_odom_wall is None:
            self.odom_guard_skipped_no_odom_count += 1
            return msg

        odom_age_s = now_wall - self.last_odom_wall
        if odom_age_s > self.odom_timeout_s:
            self.odom_guard_skipped_stale_count += 1
            self.last_odom_guard = {
                "reason": "stale_odom",
                "odom_age_s": odom_age_s,
                "odom_timeout_s": self.odom_timeout_s,
                "wall_time": now_wall,
            }
            return msg

        ox, oy, oz = self.last_odom_xyz
        raw_x = float(msg.position.x)
        raw_y = float(msg.position.y)
        raw_z = float(msg.position.z)
        dx = raw_x - ox
        dy = raw_y - oy
        dz = raw_z - oz
        raw_xy_distance_m = math.sqrt(dx * dx + dy * dy)
        raw_distance_m = math.sqrt(dx * dx + dy * dy + dz * dz)
        self.max_observed_target_distance_from_odom_m = max(
            self.max_observed_target_distance_from_odom_m, raw_distance_m
        )
        self.max_observed_xy_target_distance_from_odom_m = max(
            self.max_observed_xy_target_distance_from_odom_m, raw_xy_distance_m
        )

        if (
            (self.max_target_distance_from_odom_m <= 0.0 or raw_distance_m <= self.max_target_distance_from_odom_m)
            and (
                self.max_xy_target_distance_from_odom_m <= 0.0
                or raw_xy_distance_m <= self.max_xy_target_distance_from_odom_m
            )
        ):
            self.max_published_target_distance_from_odom_m = max(
                self.max_published_target_distance_from_odom_m, raw_distance_m
            )
            self.max_published_xy_target_distance_from_odom_m = max(
                self.max_published_xy_target_distance_from_odom_m, raw_xy_distance_m
            )
            return msg

        if self.odom_distance_policy == "hold_last_safe":
            hold = self.hold_last_safe_msg(now_wall, "odom_target_distance")
            if hold is not None:
                self.odom_guard_hold_count += 1
                self.last_odom_guard = {
                    "reason": "hold_last_safe",
                    "odom_xyz": self.last_odom_xyz,
                    "candidate_xyz": [raw_x, raw_y, raw_z],
                    "raw_distance_m": raw_distance_m,
                    "raw_xy_distance_m": raw_xy_distance_m,
                    "max_target_distance_from_odom_m": self.max_target_distance_from_odom_m,
                    "max_xy_target_distance_from_odom_m": self.max_xy_target_distance_from_odom_m,
                    "odom_age_s": odom_age_s,
                    "wall_time": now_wall,
                }
                return hold

        limited = self.clone_msg(msg)
        limited_x = raw_x
        limited_y = raw_y
        limited_z = raw_z
        xy_scale = 1.0
        xyz_scale = 1.0

        if self.max_xy_target_distance_from_odom_m > 0.0 and raw_xy_distance_m > self.max_xy_target_distance_from_odom_m:
            xy_scale = self.max_xy_target_distance_from_odom_m / max(raw_xy_distance_m, 1e-9)
            limited_x = ox + dx * xy_scale
            limited_y = oy + dy * xy_scale

        ldx = limited_x - ox
        ldy = limited_y - oy
        ldz = limited_z - oz
        limited_distance_m = math.sqrt(ldx * ldx + ldy * ldy + ldz * ldz)
        if self.max_target_distance_from_odom_m > 0.0 and limited_distance_m > self.max_target_distance_from_odom_m:
            xyz_scale = self.max_target_distance_from_odom_m / max(limited_distance_m, 1e-9)
            limited_x = ox + ldx * xyz_scale
            limited_y = oy + ldy * xyz_scale
            limited_z = oz + ldz * xyz_scale

        limited.position.x = limited_x
        limited.position.y = limited_y
        limited.position.z = min(max(limited_z, self.min_z), self.max_z)
        if self.odom_guard_zero_dynamics:
            self.zero_dynamic_terms(limited)

        published_dx = float(limited.position.x) - ox
        published_dy = float(limited.position.y) - oy
        published_dz = float(limited.position.z) - oz
        published_xy_distance_m = math.sqrt(published_dx * published_dx + published_dy * published_dy)
        published_distance_m = math.sqrt(
            published_dx * published_dx + published_dy * published_dy + published_dz * published_dz
        )
        self.max_published_target_distance_from_odom_m = max(
            self.max_published_target_distance_from_odom_m, published_distance_m
        )
        self.max_published_xy_target_distance_from_odom_m = max(
            self.max_published_xy_target_distance_from_odom_m, published_xy_distance_m
        )
        self.odom_guard_applied_count += 1
        self.last_odom_guard = {
            "reason": "project_toward_raw",
            "odom_xyz": self.last_odom_xyz,
            "candidate_xyz": [raw_x, raw_y, raw_z],
            "published_xyz": [
                float(limited.position.x),
                float(limited.position.y),
                float(limited.position.z),
            ],
            "raw_distance_m": raw_distance_m,
            "raw_xy_distance_m": raw_xy_distance_m,
            "published_distance_m": published_distance_m,
            "published_xy_distance_m": published_xy_distance_m,
            "xy_scale": xy_scale,
            "xyz_scale": xyz_scale,
            "max_target_distance_from_odom_m": self.max_target_distance_from_odom_m,
            "max_xy_target_distance_from_odom_m": self.max_xy_target_distance_from_odom_m,
            "odom_age_s": odom_age_s,
            "wall_time": now_wall,
        }
        return limited

    def update_published_jump_stats(self, msg: PositionCommand, now_motion: float) -> None:
        if self.last_safe_msg is None:
            return
        prev = self.last_safe_msg.position
        curr = msg.position
        jump_m = math.dist(
            (float(prev.x), float(prev.y), float(prev.z)),
            (float(curr.x), float(curr.y), float(curr.z)),
        )
        dt = 0.0
        if self.last_published_motion_time is not None:
            dt = max(0.0, now_motion - self.last_published_motion_time)
        jump_speed_mps = jump_m / dt if dt > 1e-4 else 0.0
        self.max_published_jump_m = max(self.max_published_jump_m, jump_m)
        self.max_published_jump_speed_mps = max(self.max_published_jump_speed_mps, jump_speed_mps)

    def adapted_msg(self, now_wall: float, now_motion: float) -> PositionCommand | None:
        if self.last_raw is None:
            return None
        if self.waiting_fresh_raw_after_enable:
            return None

        if self.map_guard_enabled:
            self.last_map_guard = self.map_guard_snapshot(now_wall)
            if not self.last_map_guard["ready"]:
                self.map_guard_not_ready_count += 1
                self.last_reject_reason = "planner_map_not_ready"
                hold = self.hold_last_safe_msg(now_wall, "planner_map_not_ready", now_motion)
                if hold is not None:
                    self.map_guard_hold_count += 1
                return hold
            self.map_guard_ready_count += 1

        msg = self.clone_msg(self.last_raw)

        raw_age_s = (
            now_motion - self.last_raw_motion
            if self.last_raw_motion is not None
            else now_wall - self.last_raw_wall
        )
        stale = raw_age_s > self.input_timeout_s
        self.last_publish_stale = stale
        if stale:
            hold = self.hold_last_safe_msg(now_wall, "stale", now_motion)
            if hold is not None:
                return hold
            self.zero_dynamic_terms(msg)
            self.hold_publish_count += 1

        invalid_z_seen = msg.position.z < self.min_z or msg.position.z > self.max_z
        if self.should_reject_invalid_z(msg, now_wall):
            hold = self.hold_last_safe_msg(now_wall, "invalid_z", now_motion)
            if hold is not None:
                return hold
            self.invalid_z_clamp_fallback_count += 1
            self.zero_dynamic_terms(msg)
        elif invalid_z_seen:
            self.invalid_z_clamp_policy_count += 1

        if msg.position.z < self.min_z:
            msg.position.z = self.min_z
            msg.velocity.z = max(0.0, msg.velocity.z)
            msg.acceleration.z = max(0.0, msg.acceleration.z)
            msg.jerk.z = max(0.0, msg.jerk.z)
            self.clamped_low_count += 1
        elif msg.position.z > self.max_z:
            msg.position.z = self.max_z
            msg.velocity.z = min(0.0, msg.velocity.z)
            msg.acceleration.z = min(0.0, msg.acceleration.z)
            msg.jerk.z = min(0.0, msg.jerk.z)
            self.clamped_high_count += 1

        if self.fixed_z is not None:
            msg.position.z = min(max(self.fixed_z, self.min_z), self.max_z)
            msg.velocity.z = 0.0
            msg.acceleration.z = 0.0
            msg.jerk.z = 0.0
        if self.fixed_yaw is not None:
            msg.yaw = float(self.fixed_yaw)
            msg.yaw_dot = 0.0

        msg = self.apply_odom_target_guard(msg, now_wall)
        if msg is None:
            return None
        # The odom disk is convex. When the previous command and guarded
        # candidate are both inside it, smoothing along their segment remains
        # inside it. A second projection can jump to the opposite side of the
        # disk after a planner direction change and must not run here.
        msg = self.apply_smoothing(msg, now_wall, now_motion)
        collision_guard_msg = self.apply_map_collision_guard(msg, now_wall, now_motion)
        if collision_guard_msg is None:
            return None
        if self.last_map_collision and (
            self.last_map_collision.get("collision")
            or not self.last_map_collision.get("ready", True)
        ):
            return collision_guard_msg
        msg = collision_guard_msg
        # Judge discontinuities on the command that will actually reach the
        # controller. Raw planner references may legitimately run far ahead;
        # the odom guard and smoothing above are what make them executable.
        if self.should_reject_jump(msg, now_wall, now_motion):
            return self.hold_last_safe_msg(now_wall, "jump", now_motion)
        msg = self.make_dynamics_consistent_with_position(msg, now_motion)
        bounded = enforce_position_z_bounds(
            (msg.position.x, msg.position.y, msg.position.z),
            (msg.velocity.x, msg.velocity.y, msg.velocity.z),
            (msg.acceleration.x, msg.acceleration.y, msg.acceleration.z),
            (msg.jerk.x, msg.jerk.y, msg.jerk.z),
            self.min_z,
            self.max_z,
        )
        for field, values in (
            (msg.position, bounded["position"]),
            (msg.velocity, bounded["velocity"]),
            (msg.acceleration, bounded["acceleration"]),
            (msg.jerk, bounded["jerk"]),
        ):
            field.x, field.y, field.z = values
        if bounded["corrected"]:
            self.post_dynamics_z_clamp_count += 1
        if self.zero_all_dynamics:
            self.zero_dynamic_terms(msg)
        self.update_published_jump_stats(msg, now_motion)
        self.min_published_z = msg.position.z if self.min_published_z is None else min(self.min_published_z, msg.position.z)
        self.max_published_z = msg.position.z if self.max_published_z is None else max(self.max_published_z, msg.position.z)
        self.last_published_xyz = [float(msg.position.x), float(msg.position.y), float(msg.position.z)]
        self.last_safe_msg = self.clone_msg(msg)
        self.last_accepted_wall = now_wall
        self.last_accepted_raw_wall = self.last_raw_wall
        self.last_published_wall = now_wall
        self.last_published_motion_time = now_motion
        self.last_accepted_motion_time = now_motion
        return msg

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.sunray_ros1.position_cmd_safety_adapter.v1",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "enable_topic": self.enable_topic,
            "enabled": self.enabled,
            "require_fresh_raw_after_enable": self.require_fresh_raw_after_enable,
            "rate_hz": self.rate_hz,
            "min_z": self.min_z,
            "max_z": self.max_z,
            "fixed_z": self.fixed_z,
            "fixed_yaw": self.fixed_yaw,
            "input_timeout_s": self.input_timeout_s,
            "map_guard_enabled": self.map_guard_enabled,
            "map_guard_cloud_topic": self.map_guard_cloud_topic,
            "map_guard_occupancy_topic": self.map_guard_occupancy_topic,
            "map_guard_timeout_s": self.map_guard_timeout_s,
            "map_guard_min_cloud_points": self.map_guard_min_cloud_points,
            "map_guard_min_occupancy_points": self.map_guard_min_occupancy_points,
            "map_guard_not_ready_count": self.map_guard_not_ready_count,
            "map_guard_ready_count": self.map_guard_ready_count,
            "map_guard_hold_count": self.map_guard_hold_count,
            "last_map_guard": self.last_map_guard,
            "map_collision_guard_enabled": self.map_collision_guard_enabled,
            "map_collision_radius_m": self.map_collision_radius_m,
            "map_collision_z_margin_m": self.map_collision_z_margin_m,
            "map_collision_sample_step_m": self.map_collision_sample_step_m,
            "map_collision_max_points": self.map_collision_max_points,
            "map_collision_guard_count": self.map_collision_guard_count,
            "map_collision_hold_count": self.map_collision_hold_count,
            "last_map_collision": self.last_map_collision,
            "last_occupancy_frame_id": self.last_occupancy_frame_id,
            "last_occupancy_collision_points": len(self.last_occupancy_points),
            "last_map_cloud_wall": self.last_map_cloud_wall,
            "last_map_cloud_points": self.last_map_cloud_points,
            "last_map_cloud_stamp": self.last_map_cloud_stamp,
            "last_occupancy_cloud_wall": self.last_occupancy_cloud_wall,
            "last_occupancy_cloud_points": self.last_occupancy_cloud_points,
            "last_occupancy_cloud_stamp": self.last_occupancy_cloud_stamp,
            "invalid_z_policy": self.invalid_z_policy,
            "jump_guard_enabled": self.jump_guard_enabled,
            "max_position_jump_m": self.max_position_jump_m,
            "max_position_jump_speed_mps": self.max_position_jump_speed_mps,
            "jump_guard_min_dt_s": self.jump_guard_min_dt_s,
            "smoothing_enabled": self.smoothing_enabled,
            "smoothing_max_speed_mps": self.smoothing_max_speed_mps,
            "smoothing_max_step_m": self.smoothing_max_step_m,
            "smoothing_max_dt_s": self.smoothing_max_dt_s,
            "smoothing_zero_dynamics": self.smoothing_zero_dynamics,
            "motion_time_basis": self.motion_time_basis,
            "recompute_velocity_from_position": self.recompute_velocity_from_position,
            "max_acceleration_mps2": self.max_acceleration_mps2,
            "max_velocity_mps": self.max_velocity_mps,
            "max_lateral_acceleration_mps2": self.max_lateral_acceleration_mps2,
            "max_jerk_mps3": self.max_jerk_mps3,
            "dynamics_limited_count": self.dynamics_limited_count,
            "max_published_acceleration_mps2": self.max_published_acceleration_mps2,
            "max_published_lateral_acceleration_mps2": self.max_published_lateral_acceleration_mps2,
            "max_published_jerk_mps3": self.max_published_jerk_mps3,
            "last_dynamics_limit": self.last_dynamics_limit,
            "post_dynamics_z_clamp_count": self.post_dynamics_z_clamp_count,
            "zero_all_dynamics": self.zero_all_dynamics,
            "odom_target_guard_enabled": self.odom_target_guard_enabled,
            "odom_topic": self.odom_topic,
            "odom_timeout_s": self.odom_timeout_s,
            "max_target_distance_from_odom_m": self.max_target_distance_from_odom_m,
            "max_xy_target_distance_from_odom_m": self.max_xy_target_distance_from_odom_m,
            "odom_distance_policy": self.odom_distance_policy,
            "odom_guard_zero_dynamics": self.odom_guard_zero_dynamics,
            "seed_from_odom_on_enable": self.seed_from_odom_on_enable,
            "raw_count": self.raw_count,
            "published_count": self.published_count,
            "clamped_low_count": self.clamped_low_count,
            "clamped_high_count": self.clamped_high_count,
            "hold_publish_count": self.hold_publish_count,
            "invalid_z_rejected_low_count": self.invalid_z_rejected_low_count,
            "invalid_z_rejected_high_count": self.invalid_z_rejected_high_count,
            "invalid_z_hold_publish_count": self.invalid_z_hold_publish_count,
            "invalid_z_clamp_fallback_count": self.invalid_z_clamp_fallback_count,
            "invalid_z_clamp_policy_count": self.invalid_z_clamp_policy_count,
            "jump_rejected_count": self.jump_rejected_count,
            "jump_hold_publish_count": self.jump_hold_publish_count,
            "max_observed_jump_m": self.max_observed_jump_m,
            "max_observed_jump_speed_mps": self.max_observed_jump_speed_mps,
            "max_published_jump_m": self.max_published_jump_m,
            "max_published_jump_speed_mps": self.max_published_jump_speed_mps,
            "large_distance_jump_observed_count": self.large_distance_jump_observed_count,
            "smoothing_applied_count": self.smoothing_applied_count,
            "smoothing_limited_distance_m": self.smoothing_limited_distance_m,
            "last_smoothing": self.last_smoothing,
            "odom_count": self.odom_count,
            "last_odom_wall": self.last_odom_wall,
            "last_odom_xyz": self.last_odom_xyz,
            "odom_guard_applied_count": self.odom_guard_applied_count,
            "odom_guard_hold_count": self.odom_guard_hold_count,
            "odom_guard_skipped_no_odom_count": self.odom_guard_skipped_no_odom_count,
            "odom_guard_skipped_stale_count": self.odom_guard_skipped_stale_count,
            "max_observed_target_distance_from_odom_m": self.max_observed_target_distance_from_odom_m,
            "max_observed_xy_target_distance_from_odom_m": self.max_observed_xy_target_distance_from_odom_m,
            "max_published_target_distance_from_odom_m": self.max_published_target_distance_from_odom_m,
            "max_published_xy_target_distance_from_odom_m": self.max_published_xy_target_distance_from_odom_m,
            "last_odom_guard": self.last_odom_guard,
            "last_reject_reason": self.last_reject_reason,
            "last_observed_jump": self.last_observed_jump,
            "last_rejected_jump": self.last_rejected_jump,
            "last_rejected_z": self.last_rejected_z,
            "enable_update_count": self.enable_update_count,
            "disabled_publish_skip_count": self.disabled_publish_skip_count,
            "last_enable_wall": self.last_enable_wall,
            "waiting_fresh_raw_after_enable": self.waiting_fresh_raw_after_enable,
            "fresh_raw_after_enable_count": self.fresh_raw_after_enable_count,
            "last_accepted_wall": self.last_accepted_wall,
            "last_accepted_raw_wall": self.last_accepted_raw_wall,
            "first_raw_wall": self.first_raw_wall,
            "prev_raw_wall": self.prev_raw_wall,
            "last_raw_z": self.last_raw_z,
            "last_raw_xyz": self.last_raw_xyz,
            "last_published_xyz": self.last_published_xyz,
            "last_raw_velocity_xyz": self.last_raw_velocity_xyz,
            "last_raw_acceleration_xyz": self.last_raw_acceleration_xyz,
            "last_raw_yaw": self.last_raw_yaw,
            "last_published_wall": self.last_published_wall,
            "last_published_motion_time": self.last_published_motion_time,
            "last_accepted_motion_time": self.last_accepted_motion_time,
            "last_raw_motion_time": self.last_raw_motion,
            "last_publish_stale": self.last_publish_stale,
            "min_raw_z": self.min_raw_z,
            "min_published_z": self.min_published_z,
            "max_published_z": self.max_published_z,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(self.rate_hz)
        while not rospy.is_shutdown():
            now = time.time()
            now_motion = self.motion_time(now)
            if self.enabled:
                msg = self.adapted_msg(now, now_motion)
                if msg is not None:
                    self.pub.publish(msg)
                    self.published_count += 1
            else:
                self.disabled_publish_skip_count += 1
            if self.diagnostics_path and now - self.last_publish_wall > 1.0:
                self.write_diagnostics()
                self.last_publish_wall = now
            rate.sleep()
        self.write_diagnostics()


def main() -> None:
    rospy.init_node("mosim_goal4_position_cmd_safety_adapter")
    PositionCmdSafetyAdapter().spin()


if __name__ == "__main__":
    main()
