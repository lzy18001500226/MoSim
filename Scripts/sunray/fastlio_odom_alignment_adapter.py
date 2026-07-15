#!/usr/bin/env python3
"""Align FAST-LIO Livox-body odometry to the PX4/MAVROS UAV-base frame."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import time
from collections import deque
from pathlib import Path
import sys
from threading import Lock
from typing import Dict, Optional, Tuple

import rospy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry, Path as RosPath
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float64
from sensor_msgs.msg import PointCloud2
from sensor_msgs import point_cloud2
import tf2_ros

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fastlio_frame_transform import (  # noqa: E402
    Pose3,
    livox_pose_to_base_pose,
    make_alignment,
    pose_mul,
    quat_from_rpy,
    rotate,
    transform_velocity,
    yaw_from_quat,
)


class FastlioOdomAlignmentAdapter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.fastlio_odom: Optional[Odometry] = None
        self.local_odom: Optional[Odometry] = None
        self.local_odom_history = deque(maxlen=500)
        self.local_odom_history_lock = Lock()
        self.fastlio_base0: Optional[Pose3] = None
        self.local_base0: Optional[Pose3] = None
        self.truth_odom: Optional[Odometry] = None
        self.truth_base0_z: Optional[float] = None
        self.config_base0 = Pose3(args.alignment_origin_xyz, quat_from_rpy(*args.alignment_origin_rpy))
        self.local_from_fast: Optional[Pose3] = None
        self.last_aligned_pos: Optional[Tuple[float, float, float]] = None
        self.last_aligned_time: Optional[float] = None
        self.last_published_fastlio_key: Optional[Tuple[int, int, int]] = None
        self.cloud_received = 0
        self.cloud_published = 0
        self.cloud_dropped_before_alignment = 0
        self.cloud_finite_input_total = 0
        self.cloud_self_filtered_total = 0
        self.cloud_peer_filtered_total = 0
        self.cloud_peer_stale_samples_total = 0
        self.cloud_finite_output_total = 0
        self.last_cloud_input_point_count = 0
        self.last_cloud_finite_input_count = 0
        self.last_cloud_self_filtered_count = 0
        self.last_cloud_peer_filtered_count = 0
        self.last_cloud_finite_output_count = 0
        self.last_cloud_self_filter_center_xyz: Optional[Tuple[float, float, float]] = None
        self.last_cloud_peer_filter_centers = []
        self.cloud_peer_filtered_by_topic: Dict[str, int] = {
            topic: 0 for topic in args.cloud_peer_odom_topic
        }
        self.peer_odom_by_topic: Dict[str, Odometry] = {}
        self.peer_odom_lock = Lock()
        self.last_cloud_z_correction_m = 0.0
        self.last_cloud_diagnostics_wall = 0.0
        self.aligned_path = RosPath()
        self.aligned_path.header.frame_id = args.output_frame
        self.mount_pose = Pose3(args.mount_xyz, quat_from_rpy(*args.mount_rpy))
        self.dynamic_csv_file = None
        self.dynamic_csv = None
        self.dynamic_rows = 0
        self.dynamic_xy_residual_sum = 0.0
        self.dynamic_xy_residual_max = 0.0
        self.dynamic_jump_max = 0.0
        self.dynamic_prev_aligned: Optional[Tuple[float, float, float]] = None
        self.dynamic_prev_local: Optional[Tuple[float, float, float]] = None
        if args.dynamic_diagnostics_csv:
            csv_path = Path(args.dynamic_diagnostics_csv)
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            self.dynamic_csv_file = csv_path.open("w", newline="", encoding="utf-8")
            self.dynamic_csv = csv.writer(self.dynamic_csv_file)
            self.dynamic_csv.writerow(
                [
                    "fast_stamp", "local_stamp", "stamp_delta_s",
                    "fast_x", "fast_y", "fast_z",
                    "aligned_x", "aligned_y", "aligned_z",
                    "local_x", "local_y", "local_z",
                    "truth_x", "truth_y", "truth_z",
                    "xy_residual_m", "aligned_step_m", "local_step_m",
                    "delta_motion_ratio", "aligned_jump_m",
                ]
            )

        self.pub = rospy.Publisher(args.output_topic, Odometry, queue_size=20)
        self.path_pub = rospy.Publisher(args.path_topic, RosPath, queue_size=1, latch=True)
        self.delay_pub = rospy.Publisher(args.delay_topic, Float64, queue_size=20)
        self.cloud_pub = (
            rospy.Publisher(args.cloud_output_topic, PointCloud2, queue_size=2)
            if args.cloud_input_topic and args.cloud_output_topic
            else None
        )
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()

        rospy.Subscriber(args.fastlio_topic, Odometry, self.on_fastlio_odom, queue_size=20)
        rospy.Subscriber(args.local_topic, Odometry, self.on_local_odom, queue_size=20)
        for topic in args.cloud_peer_odom_topic:
            rospy.Subscriber(topic, Odometry, self.on_peer_odom, callback_args=topic, queue_size=20)
        if self.cloud_pub is not None:
            rospy.Subscriber(args.cloud_input_topic, PointCloud2, self.on_cloud, queue_size=2)
        if (
            args.z_source in ("truth", "truth_delta")
            or args.alignment_reference == "truth"
            or args.dynamic_diagnostics_csv
        ):
            rospy.Subscriber(args.truth_topic, Odometry, self.on_truth_odom, queue_size=20)

    @staticmethod
    def pose(msg: Odometry) -> Pose3:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        return Pose3(
            (float(p.x), float(p.y), float(p.z)),
            (float(q.x), float(q.y), float(q.z), float(q.w)),
        )

    @staticmethod
    def pos(msg: Odometry) -> Tuple[float, float, float]:
        return FastlioOdomAlignmentAdapter.pose(msg).p

    @staticmethod
    def set_pose(msg: Odometry, pose: Pose3) -> None:
        msg.pose.pose.position.x = pose.p[0]
        msg.pose.pose.position.y = pose.p[1]
        msg.pose.pose.position.z = pose.p[2]
        msg.pose.pose.orientation.x = pose.q[0]
        msg.pose.pose.orientation.y = pose.q[1]
        msg.pose.pose.orientation.z = pose.q[2]
        msg.pose.pose.orientation.w = pose.q[3]

    @staticmethod
    def vec(msg: Odometry) -> Tuple[float, float, float]:
        v = msg.twist.twist.linear
        return float(v.x), float(v.y), float(v.z)

    def on_fastlio_odom(self, msg: Odometry) -> None:
        self.fastlio_odom = msg
        if self.fastlio_base0 is None:
            self.fastlio_base0 = self.fastlio_base_pose(msg)
            self.try_make_alignment()

    def on_local_odom(self, msg: Odometry) -> None:
        with self.local_odom_history_lock:
            self.local_odom = msg
            self.local_odom_history.append(msg)
        if self.local_base0 is None:
            self.local_base0 = self.pose(msg)
            self.try_make_alignment()

    def local_odom_snapshot(self) -> Tuple[Optional[Odometry], Tuple[Odometry, ...]]:
        with self.local_odom_history_lock:
            return self.local_odom, tuple(self.local_odom_history)

    def on_peer_odom(self, msg: Odometry, topic: str) -> None:
        with self.peer_odom_lock:
            self.peer_odom_by_topic[topic] = msg

    def peer_filter_centers(self, cloud_stamp_s: float):
        if self.args.cloud_peer_filter_radius_xy_m <= 0.0:
            return [], len(self.args.cloud_peer_odom_topic)
        with self.peer_odom_lock:
            peers = dict(self.peer_odom_by_topic)
        centers = []
        stale = 0
        for topic in self.args.cloud_peer_odom_topic:
            msg = peers.get(topic)
            if msg is None:
                stale += 1
                continue
            peer_stamp_s = msg.header.stamp.to_sec()
            age_s = abs(cloud_stamp_s - peer_stamp_s)
            if cloud_stamp_s <= 0.0 or peer_stamp_s <= 0.0 or age_s > self.args.cloud_peer_odom_max_age_s:
                stale += 1
                continue
            centers.append((topic, self.pos(msg), age_s))
        return centers, stale

    def on_truth_odom(self, msg: Odometry) -> None:
        self.truth_odom = msg
        if self.truth_base0_z is None:
            self.truth_base0_z = float(msg.pose.pose.position.z)
        self.try_make_alignment()

    def on_cloud(self, msg: PointCloud2) -> None:
        self.cloud_received += 1
        z_correction = self.current_cloud_z_correction()
        if self.local_from_fast is None or self.cloud_pub is None or z_correction is None:
            self.cloud_dropped_before_alignment += 1
            return

        field_names = [field.name for field in msg.fields]
        try:
            ix = field_names.index("x")
            iy = field_names.index("y")
            iz = field_names.index("z")
        except ValueError:
            rospy.logerr_throttle(5.0, "FAST-LIO cloud has no x/y/z fields")
            return

        tx, ty, tz = self.local_from_fast.p
        aligned_base = self.aligned_pose(self.fastlio_odom)
        self_filter_center = (
            aligned_base.p[0],
            aligned_base.p[1],
            self.output_z(aligned_base.p[2]),
        )
        peer_filter_centers, stale_peer_samples = self.peer_filter_centers(msg.header.stamp.to_sec())
        transformed = []
        finite_input = 0
        self_filtered = 0
        peer_filtered = 0
        peer_filtered_by_topic = {topic: 0 for topic in self.args.cloud_peer_odom_topic}
        finite_output = 0
        for source in point_cloud2.read_points(msg, field_names=field_names, skip_nans=False):
            row = list(source)
            keep_row = True
            x, y, z = float(row[ix]), float(row[iy]), float(row[iz])
            if math.isfinite(x) and math.isfinite(y) and math.isfinite(z):
                finite_input += 1
                rx, ry, rz = rotate(self.local_from_fast.q, (x, y, z))
                world_point = (rx + tx, ry + ty, rz + tz + z_correction)
                if self.point_is_inside_self_filter(world_point, self_filter_center):
                    keep_row = False
                    self_filtered += 1
                else:
                    filtered_peer_topic = self.peer_filter_match(world_point, peer_filter_centers)
                    if filtered_peer_topic is not None:
                        keep_row = False
                        peer_filtered += 1
                        peer_filtered_by_topic[filtered_peer_topic] += 1
                    else:
                        row[ix], row[iy], row[iz] = world_point
                        finite_output += 1
            if keep_row:
                transformed.append(row)

        header = copy.deepcopy(msg.header)
        header.frame_id = self.args.output_frame
        out = point_cloud2.create_cloud(header, msg.fields, transformed)
        self.cloud_pub.publish(out)
        self.cloud_published += 1
        self.cloud_finite_input_total += finite_input
        self.cloud_self_filtered_total += self_filtered
        self.cloud_peer_filtered_total += peer_filtered
        self.cloud_peer_stale_samples_total += stale_peer_samples
        for topic, count in peer_filtered_by_topic.items():
            self.cloud_peer_filtered_by_topic[topic] += count
        self.cloud_finite_output_total += finite_output
        self.last_cloud_input_point_count = int(msg.width * msg.height)
        self.last_cloud_finite_input_count = finite_input
        self.last_cloud_self_filtered_count = self_filtered
        self.last_cloud_peer_filtered_count = peer_filtered
        self.last_cloud_finite_output_count = finite_output
        self.last_cloud_self_filter_center_xyz = self_filter_center
        self.last_cloud_peer_filter_centers = [
            {"topic": topic, "center_xyz": list(center), "stamp_delta_s": age_s}
            for topic, center, age_s in peer_filter_centers
        ]
        self.last_cloud_z_correction_m = z_correction
        self.write_cloud_diagnostics()

    def point_is_inside_self_filter(
        self,
        point_xyz: Tuple[float, float, float],
        center_xyz: Tuple[float, float, float],
    ) -> bool:
        radius = self.args.cloud_self_filter_radius_xy_m
        if radius <= 0.0:
            return False
        dx = point_xyz[0] - center_xyz[0]
        dy = point_xyz[1] - center_xyz[1]
        dz = point_xyz[2] - center_xyz[2]
        return (
            dx * dx + dy * dy <= radius * radius
            and self.args.cloud_self_filter_z_min_m <= dz <= self.args.cloud_self_filter_z_max_m
        )

    def peer_filter_match(self, point_xyz, peer_filter_centers) -> Optional[str]:
        radius = self.args.cloud_peer_filter_radius_xy_m
        if radius <= 0.0:
            return None
        for topic, center_xyz, _age_s in peer_filter_centers:
            dx = point_xyz[0] - center_xyz[0]
            dy = point_xyz[1] - center_xyz[1]
            dz = point_xyz[2] - center_xyz[2]
            if (
                dx * dx + dy * dy <= radius * radius
                and self.args.cloud_peer_filter_z_min_m
                <= dz
                <= self.args.cloud_peer_filter_z_max_m
            ):
                return topic
        return None

    def output_z(self, rigid_aligned_z: float) -> float:
        if self.args.z_source == "truth":
            return self.truth_z()
        if self.args.z_source == "truth_delta":
            return self.truth_delta_z()
        return rigid_aligned_z

    def current_cloud_z_correction(self) -> Optional[float]:
        if self.local_from_fast is None:
            return None
        if self.args.z_source in ("truth", "truth_delta") and (
            self.truth_odom is None or self.truth_base0_z is None
        ):
            return None
        if self.args.z_source == "truth_delta" and self.local_base0 is None:
            return None
        if self.fastlio_odom is None:
            return None
        rigid_aligned_z = self.aligned_pose(self.fastlio_odom).p[2]
        return self.output_z(rigid_aligned_z) - rigid_aligned_z

    def write_cloud_diagnostics(self, force: bool = False) -> None:
        if not self.args.cloud_diagnostics_path:
            return
        now = time.time()
        if not force and now - self.last_cloud_diagnostics_wall < 1.0:
            return
        self.last_cloud_diagnostics_wall = now
        transform = None
        if self.local_from_fast is not None:
            transform = {
                "translation_xyz": list(self.local_from_fast.p),
                "quaternion_xyzw": list(self.local_from_fast.q),
                "yaw_rad": yaw_from_quat(self.local_from_fast.q),
            }
        data = {
            "schema": "mosim.fastlio_cloud_odom_alignment.v1",
            "fastlio_odom_topic": self.args.fastlio_topic,
            "local_reference_topic": self.args.local_topic,
            "aligned_odom_topic": self.args.output_topic,
            "cloud_input_topic": self.args.cloud_input_topic,
            "cloud_output_topic": self.args.cloud_output_topic,
            "output_frame": self.args.output_frame,
            "cloud_received": self.cloud_received,
            "cloud_published": self.cloud_published,
            "cloud_dropped_before_alignment": self.cloud_dropped_before_alignment,
            "cloud_finite_input_total": self.cloud_finite_input_total,
            "cloud_self_filtered_total": self.cloud_self_filtered_total,
            "cloud_peer_filtered_total": self.cloud_peer_filtered_total,
            "cloud_peer_stale_samples_total": self.cloud_peer_stale_samples_total,
            "cloud_finite_output_total": self.cloud_finite_output_total,
            "last_cloud_input_point_count": self.last_cloud_input_point_count,
            "last_cloud_finite_input_count": self.last_cloud_finite_input_count,
            "last_cloud_self_filtered_count": self.last_cloud_self_filtered_count,
            "last_cloud_peer_filtered_count": self.last_cloud_peer_filtered_count,
            "last_cloud_finite_output_count": self.last_cloud_finite_output_count,
            "cloud_self_filter": {
                "radius_xy_m": self.args.cloud_self_filter_radius_xy_m,
                "z_min_m": self.args.cloud_self_filter_z_min_m,
                "z_max_m": self.args.cloud_self_filter_z_max_m,
                "last_center_xyz": list(self.last_cloud_self_filter_center_xyz)
                if self.last_cloud_self_filter_center_xyz is not None
                else None,
            },
            "cloud_peer_filter": {
                "odom_topics": self.args.cloud_peer_odom_topic,
                "radius_xy_m": self.args.cloud_peer_filter_radius_xy_m,
                "z_min_m": self.args.cloud_peer_filter_z_min_m,
                "z_max_m": self.args.cloud_peer_filter_z_max_m,
                "max_age_s": self.args.cloud_peer_odom_max_age_s,
                "filtered_total_by_topic": self.cloud_peer_filtered_by_topic,
                "last_centers": self.last_cloud_peer_filter_centers,
            },
            "z_source": self.args.z_source,
            "last_cloud_z_correction_m": self.last_cloud_z_correction_m,
            "local_from_fast": transform,
        }
        path = Path(self.args.cloud_diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def try_make_alignment(self) -> None:
        if self.local_from_fast is not None or self.fastlio_base0 is None:
            return
        if self.args.alignment_reference == "truth":
            if self.truth_odom is not None:
                self.local_from_fast = make_alignment(self.pose(self.truth_odom), self.fastlio_base0)
            return
        if self.args.alignment_reference == "config":
            self.local_from_fast = make_alignment(self.config_base0, self.fastlio_base0)
            return
        if self.local_base0 is not None:
            self.local_from_fast = make_alignment(self.local_base0, self.fastlio_base0)

    def ready(self) -> bool:
        return (
            self.fastlio_odom is not None
            and self.local_odom is not None
            and self.fastlio_base0 is not None
            and self.local_base0 is not None
            and self.local_from_fast is not None
            and (
                self.args.z_source not in ("truth", "truth_delta")
                or (self.truth_odom is not None and self.truth_base0_z is not None)
            )
            and (
                self.args.alignment_reference != "truth"
                or self.truth_odom is not None
            )
        )

    def fastlio_base_pose(self, msg: Odometry) -> Pose3:
        pose = self.pose(msg)
        if self.args.input_pose_frame == "livox":
            return livox_pose_to_base_pose(pose, self.mount_pose)
        return pose

    def aligned_pose(self, msg: Odometry) -> Pose3:
        if self.local_from_fast is None:
            raise RuntimeError("alignment transform not initialized")
        return pose_mul(self.local_from_fast, self.fastlio_base_pose(msg))

    def fastlio_key(self, msg: Odometry) -> Tuple[int, int, int]:
        return int(msg.header.seq), int(msg.header.stamp.secs), int(msg.header.stamp.nsecs)

    def output_stamp(self, msg: Odometry, now: rospy.Time) -> rospy.Time:
        if self.args.stamp_source == "now":
            return now
        if msg.header.stamp.to_sec() > 0:
            return msg.header.stamp
        rospy.logwarn_throttle(5.0, "FAST-LIO odom stamp is zero; falling back to rospy.Time.now()")
        return now

    def publish_once(self) -> None:
        if not self.ready() or self.fastlio_odom is None:
            return

        now = rospy.Time.now()
        fastlio_key = self.fastlio_key(self.fastlio_odom)
        if not self.args.republish_latest and fastlio_key == self.last_published_fastlio_key:
            return

        out = copy.deepcopy(self.fastlio_odom)
        out.header.stamp = self.output_stamp(self.fastlio_odom, now)
        out.header.frame_id = self.args.output_frame
        out.child_frame_id = self.args.child_frame

        aligned = self.aligned_pose(self.fastlio_odom)
        self.set_pose(out, aligned)
        x, y, z = aligned.p
        z = self.output_z(z)
        out.pose.pose.position.z = z

        if self.args.use_fastlio_twist and self.local_from_fast is not None:
            vx, vy, vz = transform_velocity(self.local_from_fast.q, self.vec(self.fastlio_odom))
            out.twist.twist.linear.x = vx
            out.twist.twist.linear.y = vy
            out.twist.twist.linear.z = vz
            if self.args.z_source in ("truth", "truth_delta") and self.truth_odom is not None:
                out.twist.twist.linear.z = float(self.truth_odom.twist.twist.linear.z)

        t = out.header.stamp.to_sec()
        if not self.args.use_fastlio_twist and self.last_aligned_pos is not None and self.last_aligned_time is not None:
            dt = max(1e-3, t - self.last_aligned_time)
            px, py, pz = self.last_aligned_pos
            out.twist.twist.linear.x = (x - px) / dt
            out.twist.twist.linear.y = (y - py) / dt
            out.twist.twist.linear.z = (z - pz) / dt

        self.pub.publish(out)
        self.delay_pub.publish(Float64(data=max(0.0, now.to_sec() - out.header.stamp.to_sec())))
        self.publish_path_point(out)
        self.publish_tf(out)
        self.write_dynamic_diagnostics(self.fastlio_odom, out)

        self.last_aligned_pos = (x, y, z)
        self.last_aligned_time = t
        self.last_published_fastlio_key = fastlio_key

    def write_dynamic_diagnostics(self, fast: Odometry, aligned: Odometry) -> None:
        latest_local, local_history = self.local_odom_snapshot()
        if self.dynamic_csv is None or latest_local is None:
            return
        fast_stamp = fast.header.stamp.to_sec()
        local = min(
            local_history,
            key=lambda msg: abs(msg.header.stamp.to_sec() - fast_stamp),
            default=latest_local,
        )
        fast_pos = self.pos(fast)
        aligned_pos = self.pos(aligned)
        local_pos = self.pos(local)
        truth_pos = self.pos(self.truth_odom) if self.truth_odom is not None else (math.nan,) * 3
        residual = math.hypot(aligned_pos[0] - local_pos[0], aligned_pos[1] - local_pos[1])
        aligned_step = (
            math.dist(aligned_pos, self.dynamic_prev_aligned)
            if self.dynamic_prev_aligned is not None
            else 0.0
        )
        local_step = (
            math.dist(local_pos, self.dynamic_prev_local)
            if self.dynamic_prev_local is not None
            else 0.0
        )
        ratio = aligned_step / local_step if local_step > 1e-4 else math.nan
        local_stamp = local.header.stamp.to_sec()
        self.dynamic_csv.writerow(
            [
                fast_stamp, local_stamp, fast_stamp - local_stamp,
                *fast_pos, *aligned_pos, *local_pos, *truth_pos,
                residual, aligned_step, local_step, ratio, aligned_step,
            ]
        )
        self.dynamic_csv_file.flush()
        self.dynamic_rows += 1
        self.dynamic_xy_residual_sum += residual
        self.dynamic_xy_residual_max = max(self.dynamic_xy_residual_max, residual)
        self.dynamic_jump_max = max(self.dynamic_jump_max, aligned_step)
        self.dynamic_prev_aligned = aligned_pos
        self.dynamic_prev_local = local_pos

    def write_dynamic_summary(self) -> None:
        if not self.args.dynamic_diagnostics_json:
            return
        data = {
            "schema": "mosim.fastlio_dynamic_alignment.v1",
            "samples": self.dynamic_rows,
            "mean_xy_residual_m": (
                self.dynamic_xy_residual_sum / self.dynamic_rows if self.dynamic_rows else None
            ),
            "max_xy_residual_m": self.dynamic_xy_residual_max if self.dynamic_rows else None,
            "max_aligned_step_m": self.dynamic_jump_max if self.dynamic_rows else None,
            "csv": self.args.dynamic_diagnostics_csv or None,
        }
        path = Path(self.args.dynamic_diagnostics_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def truth_delta_z(self) -> float:
        if self.local_base0 is None or self.truth_odom is None or self.truth_base0_z is None:
            raise RuntimeError("truth_delta z source is not ready")
        truth_z = float(self.truth_odom.pose.pose.position.z)
        return self.local_base0.p[2] + (truth_z - self.truth_base0_z)

    def truth_z(self) -> float:
        if self.truth_odom is None:
            raise RuntimeError("truth z source is not ready")
        return float(self.truth_odom.pose.pose.position.z)

    def publish_path_point(self, msg: Odometry) -> None:
        if self.aligned_path.poses:
            last = self.aligned_path.poses[-1].pose.position
            p = msg.pose.pose.position
            dist = math.sqrt((p.x - last.x) ** 2 + (p.y - last.y) ** 2 + (p.z - last.z) ** 2)
            if dist < self.args.path_min_step_m:
                return
        if len(self.aligned_path.poses) >= self.args.max_path_points:
            self.aligned_path.poses.pop(0)

        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose
        self.aligned_path.header.stamp = msg.header.stamp
        self.aligned_path.poses.append(pose)
        self.path_pub.publish(self.aligned_path)

    def publish_tf(self, msg: Odometry) -> None:
        tf = TransformStamped()
        tf.header = msg.header
        tf.child_frame_id = self.args.child_frame
        tf.transform.translation.x = msg.pose.pose.position.x
        tf.transform.translation.y = msg.pose.pose.position.y
        tf.transform.translation.z = msg.pose.pose.position.z
        tf.transform.rotation = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(tf)

    def spin(self) -> None:
        deadline = time.time() + self.args.ready_timeout_s
        wait_rate = rospy.Rate(20)
        try:
            while not rospy.is_shutdown() and not self.ready() and time.time() < deadline:
                wait_rate.sleep()
        except rospy.ROSInterruptException:
            return
        if not self.ready():
            rospy.logerr("FAST-LIO alignment adapter did not receive both odom sources before timeout")
            return

        rospy.loginfo(
            "FAST-LIO odom aligned: alignment_reference=%s fastlio_base0=%s local_base0=%s truth_base0=%s local_from_fast_yaw=%.6f output=%s",
            self.args.alignment_reference,
            self.fastlio_base0,
            self.local_base0,
            self.pose(self.truth_odom) if self.truth_odom is not None else None,
            yaw_from_quat(self.local_from_fast.q) if self.local_from_fast else float("nan"),
            self.args.output_topic,
        )
        rate = rospy.Rate(self.args.publish_rate_hz)
        try:
            while not rospy.is_shutdown():
                self.publish_once()
                rate.sleep()
        except rospy.ROSInterruptException:
            pass
        finally:
            self.write_cloud_diagnostics(force=True)
            self.write_dynamic_summary()
            if self.dynamic_csv_file is not None:
                self.dynamic_csv_file.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-name", default="mosim_fastlio_odom_alignment_adapter")
    parser.add_argument("--fastlio-topic", default="/Odometry")
    parser.add_argument("--local-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--output-topic", default="/mosim/fastlio/odom_aligned")
    parser.add_argument("--path-topic", default="/mosim/fastlio/odom_aligned_path")
    parser.add_argument("--delay-topic", default="/mosim/fastlio/odom_aligned_delay")
    parser.add_argument("--cloud-input-topic", default="")
    parser.add_argument("--cloud-output-topic", default="")
    parser.add_argument("--cloud-diagnostics-path", default="")
    parser.add_argument("--cloud-self-filter-radius-xy-m", type=float, default=0.0)
    parser.add_argument("--cloud-self-filter-z-min-m", type=float, default=-0.30)
    parser.add_argument("--cloud-self-filter-z-max-m", type=float, default=0.30)
    parser.add_argument("--cloud-peer-odom-topic", action="append", default=[])
    parser.add_argument("--cloud-peer-odom-max-age-s", type=float, default=0.5)
    parser.add_argument("--cloud-peer-filter-radius-xy-m", type=float, default=0.0)
    parser.add_argument("--cloud-peer-filter-z-min-m", type=float, default=-0.30)
    parser.add_argument("--cloud-peer-filter-z-max-m", type=float, default=0.30)
    parser.add_argument("--dynamic-diagnostics-csv", default="")
    parser.add_argument("--dynamic-diagnostics-json", default="")
    parser.add_argument("--z-source", choices=["fastlio", "truth", "truth_delta"], default="fastlio")
    parser.add_argument("--truth-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument(
        "--alignment-reference",
        choices=["local", "truth", "config"],
        default="local",
        help=(
            "Initial frame used for FAST-LIO alignment. 'local' preserves the runtime PX4/MAVROS frame; "
            "'truth' is simulation-only diagnostics to detect PX4-local yaw initialization bias; "
            "'config' uses --alignment-origin-* as an explicit takeoff pose/yaw authority."
        ),
    )
    parser.add_argument(
        "--alignment-origin-xyz",
        type=parse_vec3,
        default=(0.0, 0.0, 0.035),
        help="Explicit world/map -> base_link alignment origin used when --alignment-reference=config.",
    )
    parser.add_argument(
        "--alignment-origin-rpy",
        type=parse_vec3,
        default=(0.0, 0.0, 0.0),
        help="Explicit world/map -> base_link roll,pitch,yaw origin used when --alignment-reference=config.",
    )
    parser.add_argument("--output-frame", default="world")
    parser.add_argument("--child-frame", default="base_link")
    parser.add_argument(
        "--stamp-source",
        choices=["measurement", "now"],
        default="measurement",
        help="Use FAST-LIO measurement stamps by default; 'now' is only for legacy smoke tests.",
    )
    parser.add_argument(
        "--republish-latest",
        action="store_true",
        help="Republish the latest FAST-LIO frame at publish-rate-hz. Default publishes each measured odom once.",
    )
    parser.add_argument(
        "--input-pose-frame",
        choices=["base", "livox"],
        default="base",
        help="Semantic frame of FAST-LIO /Odometry pose. FAST-LIO publishes camera_init->body, so base is the safe default.",
    )
    parser.add_argument(
        "--mount-xyz",
        type=parse_vec3,
        default=(-0.000005, 0.032295, 0.050167),
        help="Fixed UAV base_link -> MID360/Livox body translation in meters.",
    )
    parser.add_argument(
        "--mount-rpy",
        type=parse_vec3,
        default=(0.0, 0.0, 4.712389),
        help="Fixed UAV base_link -> MID360/Livox body roll,pitch,yaw in radians.",
    )
    parser.add_argument(
        "--use-fastlio-twist",
        action="store_true",
        help="Rotate FAST-LIO twist into the aligned frame instead of differentiating aligned pose.",
    )
    parser.add_argument("--publish-rate-hz", type=float, default=100.0)
    parser.add_argument("--ready-timeout-s", type=float, default=20.0)
    parser.add_argument("--path-min-step-m", type=float, default=0.01)
    parser.add_argument("--max-path-points", type=int, default=20000)
    args = parser.parse_args()
    if args.cloud_self_filter_radius_xy_m < 0.0:
        parser.error("--cloud-self-filter-radius-xy-m must be >= 0")
    if args.cloud_self_filter_z_min_m > args.cloud_self_filter_z_max_m:
        parser.error("--cloud-self-filter-z-min-m must be <= --cloud-self-filter-z-max-m")
    if args.cloud_peer_odom_max_age_s < 0.0:
        parser.error("--cloud-peer-odom-max-age-s must be >= 0")
    if args.cloud_peer_filter_radius_xy_m < 0.0:
        parser.error("--cloud-peer-filter-radius-xy-m must be >= 0")
    if args.cloud_peer_filter_z_min_m > args.cloud_peer_filter_z_max_m:
        parser.error("--cloud-peer-filter-z-min-m must be <= --cloud-peer-filter-z-max-m")

    rospy.init_node(args.node_name, anonymous=False)
    FastlioOdomAlignmentAdapter(args).spin()


def parse_vec3(text: str) -> Tuple[float, float, float]:
    parts = [p for p in text.replace(",", " ").split() if p]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"expected 3 floats, got {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


if __name__ == "__main__":
    main()
