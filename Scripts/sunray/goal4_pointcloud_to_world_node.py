#!/usr/bin/env python3
"""Transform Sunray local MID360 PointCloud2 into a world-frame cloud for EGO."""

from __future__ import annotations

import json
import math
import threading
import time
from collections import deque

import rospy
import sensor_msgs.point_cloud2 as pc2
from nav_msgs.msg import Odometry
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
from tf.transformations import euler_from_quaternion, euler_matrix, quaternion_matrix

from peer_airframe_filter import (
    PeerOdomSample,
    match_peer_airframe,
    select_fresh_peer_filter_centers,
)


class PointCloudToWorld:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_point_topic", "/uav1/livox/lidar")
        self.output_topic = rospy.get_param("~output_point_topic", "/uav1/livox_world")
        self.odom_topic = rospy.get_param("~odom_topic", "/uav1/sunray/gazebo_pose")
        self.frame_id = rospy.get_param("~frame_id", "world")
        self.max_points = int(rospy.get_param("~max_points", 30000))
        self.stride = max(1, int(rospy.get_param("~stride", 1)))
        self.mount_mode = str(rospy.get_param("~mount_mode", "sensor_to_body"))
        self.rotation_mode = str(rospy.get_param("~rotation_mode", "full"))
        self.mount_xyz = self._get_float_list("~mount_xyz", [-0.000005, 0.032295, 0.050167], 3)
        self.mount_rpy = self._get_float_list("~mount_rpy", [0.0, 0.0, 4.712389], 3)
        self.min_sensor_range_m = float(rospy.get_param("~min_sensor_range_m", 0.25))
        self.max_sensor_range_m = float(rospy.get_param("~max_sensor_range_m", 8.0))
        self.self_filter_radius_m = float(rospy.get_param("~self_filter_radius_m", 0.35))
        self.peer_odom_topics = self._get_string_list("~peer_odom_topics", [])
        self.peer_filter_radius_xy_m = float(rospy.get_param("~peer_filter_radius_xy_m", 0.0))
        self.peer_filter_z_min_m = float(rospy.get_param("~peer_filter_z_min_m", -0.30))
        self.peer_filter_z_max_m = float(rospy.get_param("~peer_filter_z_max_m", 0.30))
        self.peer_odom_max_age_s = float(rospy.get_param("~peer_odom_max_age_s", 0.50))
        self.min_world_z_m = float(rospy.get_param("~min_world_z_m", 0.50))
        self.max_world_z_m = float(rospy.get_param("~max_world_z_m", 2.20))
        self.min_publish_points = int(rospy.get_param("~min_publish_points", 10))
        self.max_odom_cloud_dt_s = float(rospy.get_param("~max_odom_cloud_dt_s", 0.20))
        self.odom_sync_mode = str(rospy.get_param("~odom_sync_mode", "nearest_stamp")).strip().lower()
        self.output_stamp_mode = str(rospy.get_param("~output_stamp_mode", "input")).strip().lower()
        self.mixed_time_threshold_s = float(rospy.get_param("~mixed_time_threshold_s", 1000000.0))
        self.max_abs_odom_xy_m = float(rospy.get_param("~max_abs_odom_xy_m", 50.0))
        self.min_odom_z_m = float(rospy.get_param("~min_odom_z_m", 0.35))
        self.max_odom_z_m = float(rospy.get_param("~max_odom_z_m", 5.0))
        self.max_abs_roll_pitch_deg = float(rospy.get_param("~max_abs_roll_pitch_deg", 45.0))
        self.log_period_s = float(rospy.get_param("~log_period_s", 5.0))
        self.diagnostics_path = str(rospy.get_param("~diagnostics_path", ""))
        self.history_path = str(rospy.get_param("~history_path", ""))
        self.history_first_n = int(rospy.get_param("~history_first_n", 120))
        self.history_period_clouds = max(1, int(rospy.get_param("~history_period_clouds", 20)))
        self.odom_buffer_size = max(2, int(rospy.get_param("~odom_buffer_size", 300)))
        self.mount_mat = euler_matrix(self.mount_rpy[0], self.mount_rpy[1], self.mount_rpy[2])
        self.lock = threading.Lock()
        self.latest_odom: Odometry | None = None
        self.odom_buffer: deque[Odometry] = deque(maxlen=self.odom_buffer_size)
        self.peer_odom_by_topic: dict[str, Odometry] = {}
        self.received = 0
        self.published = 0
        self.rejected_no_odom = 0
        self.rejected_stale_odom = 0
        self.rejected_absurd_odom = 0
        self.warning_odom_gate = 0
        self.warning_attitude_gate = 0
        self.rejected_sparse_output = 0
        self.peer_filtered_total = 0
        self.peer_stale_samples_total = 0
        self.peer_filtered_by_topic = {topic: 0 for topic in self.peer_odom_topics}
        self.last_stats = {}
        self.last_log_wall = 0.0
        self.pub = rospy.Publisher(self.output_topic, PointCloud2, queue_size=2)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=20)
        for topic in self.peer_odom_topics:
            rospy.Subscriber(topic, Odometry, self.on_peer_odom, callback_args=topic, queue_size=20)
        rospy.Subscriber(self.input_topic, PointCloud2, self.on_cloud, queue_size=2)

    @staticmethod
    def _get_float_list(name: str, default: list[float], length: int) -> list[float]:
        value = rospy.get_param(name, default)
        if isinstance(value, str):
            value = [part for part in value.replace(",", " ").split() if part]
        out = [float(v) for v in value]
        if len(out) != length:
            raise ValueError(f"{name} must have {length} values, got {value!r}")
        return out

    @staticmethod
    def _get_string_list(name: str, default: list[str]) -> list[str]:
        value = rospy.get_param(name, default)
        if isinstance(value, str):
            value = [part.strip() for part in value.replace(";", ",").split(",")]
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"{name} must be a comma-separated string or list, got {value!r}")
        return list(dict.fromkeys(str(part).strip() for part in value if str(part).strip()))

    def on_odom(self, msg: Odometry) -> None:
        with self.lock:
            self.latest_odom = msg
            self.odom_buffer.append(msg)

    def on_peer_odom(self, msg: Odometry, topic: str) -> None:
        with self.lock:
            self.peer_odom_by_topic[topic] = msg

    def on_cloud(self, msg: PointCloud2) -> None:
        with self.lock:
            odom, odom_selection = self._select_odom_locked(msg.header.stamp.to_sec())
            peer_samples = {
                topic: PeerOdomSample(
                    topic=topic,
                    center_xyz=(
                        float(peer.pose.pose.position.x),
                        float(peer.pose.pose.position.y),
                        float(peer.pose.pose.position.z),
                    ),
                    stamp_s=peer.header.stamp.to_sec(),
                )
                for topic, peer in self.peer_odom_by_topic.items()
            }
        self.received += 1
        stats = {
            "wall_time": time.time(),
            "ros_time": rospy.Time.now().to_sec(),
            "received_clouds": self.received,
            "published_clouds": self.published,
            "input_points": 0,
            "stride_skipped": 0,
            "invalid": 0,
            "near_sensor": 0,
            "far_sensor": 0,
            "self_filtered": 0,
            "peer_filtered": 0,
            "peer_filtered_by_topic": {topic: 0 for topic in self.peer_odom_topics},
            "peer_filter_centers": [],
            "peer_filter_stale_topics": [],
            "peer_filter_radius_xy_m": self.peer_filter_radius_xy_m,
            "peer_filter_z_range_m": [self.peer_filter_z_min_m, self.peer_filter_z_max_m],
            "peer_odom_max_age_s": self.peer_odom_max_age_s,
            "z_filtered": 0,
            "world_z_low_filtered": 0,
            "world_z_high_filtered": 0,
            "published_points": 0,
            "min_world_z_m": self.min_world_z_m,
            "max_world_z_m": self.max_world_z_m,
            "requested_mount_mode": self.mount_mode,
            "requested_rotation_mode": self.rotation_mode,
            "cloud_frame": msg.header.frame_id,
            "cloud_stamp": msg.header.stamp.to_sec(),
            "odom_selection": odom_selection,
            "reject_reason": "",
            "warning_reasons": [],
            "rejected_no_odom": self.rejected_no_odom,
            "rejected_stale_odom": self.rejected_stale_odom,
            "rejected_absurd_odom": self.rejected_absurd_odom,
            "warning_odom_gate": self.warning_odom_gate,
            "warning_attitude_gate": self.warning_attitude_gate,
            "rejected_sparse_output": self.rejected_sparse_output,
        }
        if odom is None:
            self.rejected_no_odom += 1
            stats["reject_reason"] = "no_odom"
            stats["rejected_no_odom"] = self.rejected_no_odom
            self.last_stats = stats
            self._write_history(stats, force=True)
            return

        p = odom.pose.pose.position
        q = odom.pose.pose.orientation
        quat = [q.x, q.y, q.z, q.w]
        odom_rpy = euler_from_quaternion(quat)
        effective_mount_mode = self._resolve_mount_mode(msg.header.frame_id)
        effective_rotation_mode, mat = self._rotation_matrix(odom_rpy, quat)
        tx, ty, tz = float(p.x), float(p.y), float(p.z)
        cloud_stamp = msg.header.stamp.to_sec()
        peer_filter_centers, stale_peer_topics = select_fresh_peer_filter_centers(
            peer_samples,
            self.peer_odom_topics,
            cloud_stamp,
            self.peer_odom_max_age_s,
        )
        stats["peer_filter_centers"] = [
            {
                "topic": center.topic,
                "center_xyz": list(center.center_xyz),
                "stamp_delta_s": center.stamp_delta_s,
            }
            for center in peer_filter_centers
        ]
        stats["peer_filter_stale_topics"] = stale_peer_topics
        odom_stamp = odom.header.stamp.to_sec()
        cloud_odom_dt_s = None
        skip_stale_gate = bool(odom_selection.get("skip_stale_gate", False))
        if cloud_stamp > 0.0 and odom_stamp > 0.0:
            cloud_odom_dt_s = cloud_stamp - odom_stamp
            if not skip_stale_gate and abs(cloud_odom_dt_s) > self.max_odom_cloud_dt_s:
                self.rejected_stale_odom += 1
                stats.update(
                    {
                        "reject_reason": "stale_odom",
                        "odom_frame": odom.header.frame_id,
                        "odom_child_frame": odom.child_frame_id,
                        "odom_stamp": odom_stamp,
                        "cloud_odom_dt_s": cloud_odom_dt_s,
                        "odom_selection": odom_selection,
                        "odom_position": [tx, ty, tz],
                        "rejected_stale_odom": self.rejected_stale_odom,
                    }
                )
                self.last_stats = stats
                self._maybe_write_diagnostics(stats)
                self._write_history(stats, force=True)
                return

        if abs(tx) > self.max_abs_odom_xy_m or abs(ty) > self.max_abs_odom_xy_m:
            self.rejected_absurd_odom += 1
            stats.update(
                {
                    "reject_reason": "absurd_odom",
                    "odom_frame": odom.header.frame_id,
                    "odom_child_frame": odom.child_frame_id,
                    "odom_stamp": odom_stamp,
                    "cloud_odom_dt_s": cloud_odom_dt_s,
                    "odom_selection": odom_selection,
                    "odom_position": [tx, ty, tz],
                    "rejected_absurd_odom": self.rejected_absurd_odom,
                }
            )
            self.last_stats = stats
            self._maybe_write_diagnostics(stats)
            self._write_history(stats, force=True)
            return

        roll_deg = abs(math.degrees(odom_rpy[0]))
        pitch_deg = abs(math.degrees(odom_rpy[1]))
        warning_reasons: list[str] = []
        if tz < self.min_odom_z_m or tz > self.max_odom_z_m:
            self.warning_odom_gate += 1
            warning_reasons.append("odom_z_out_of_gate")
        if roll_deg > self.max_abs_roll_pitch_deg or pitch_deg > self.max_abs_roll_pitch_deg:
            self.warning_attitude_gate += 1
            warning_reasons.append("attitude_out_of_gate")

        points: list[tuple[float, float, float]] = []
        raw_bounds = self._empty_bounds()
        body_bounds = self._empty_bounds()
        stats.update(
            {
                "odom_frame": odom.header.frame_id,
                "odom_child_frame": odom.child_frame_id,
                "odom_stamp": odom_stamp,
                "cloud_odom_dt_s": cloud_odom_dt_s,
                "odom_selection": odom_selection,
                "odom_position": [tx, ty, tz],
                "odom_orientation_xyzw": quat,
                "odom_rpy_deg": [math.degrees(v) for v in odom_rpy],
                "effective_mount_mode": effective_mount_mode,
                "effective_rotation_mode": effective_rotation_mode,
                "warning_reasons": warning_reasons,
                "warning_odom_gate": self.warning_odom_gate,
                "warning_attitude_gate": self.warning_attitude_gate,
                "min_odom_z_m": self.min_odom_z_m,
                "max_odom_z_m": self.max_odom_z_m,
                "max_abs_roll_pitch_deg": self.max_abs_roll_pitch_deg,
            }
        )
        for i, pt in enumerate(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)):
            stats["input_points"] += 1
            if i % self.stride:
                stats["stride_skipped"] += 1
                continue
            sx, sy, sz = float(pt[0]), float(pt[1]), float(pt[2])
            if not (math.isfinite(sx) and math.isfinite(sy) and math.isfinite(sz)):
                stats["invalid"] += 1
                continue
            self._update_bounds(raw_bounds, sx, sy, sz)
            sensor_range = math.sqrt(sx * sx + sy * sy + sz * sz)
            if sensor_range < self.min_sensor_range_m:
                stats["near_sensor"] += 1
                continue
            if self.max_sensor_range_m > 0.0 and sensor_range > self.max_sensor_range_m:
                stats["far_sensor"] += 1
                continue

            bx, by, bz = self._sensor_to_body(sx, sy, sz, effective_mount_mode)
            self._update_bounds(body_bounds, bx, by, bz)
            body_range = math.sqrt(bx * bx + by * by + bz * bz)
            if body_range < self.self_filter_radius_m:
                stats["self_filtered"] += 1
                continue

            wx = mat[0, 0] * bx + mat[0, 1] * by + mat[0, 2] * bz + tx
            wy = mat[1, 0] * bx + mat[1, 1] * by + mat[1, 2] * bz + ty
            wz = mat[2, 0] * bx + mat[2, 1] * by + mat[2, 2] * bz + tz
            if wz < self.min_world_z_m:
                stats["z_filtered"] += 1
                stats["world_z_low_filtered"] += 1
                continue
            if wz > self.max_world_z_m:
                stats["z_filtered"] += 1
                stats["world_z_high_filtered"] += 1
                continue
            peer_topic = match_peer_airframe(
                (wx, wy, wz),
                peer_filter_centers,
                self.peer_filter_radius_xy_m,
                self.peer_filter_z_min_m,
                self.peer_filter_z_max_m,
            )
            if peer_topic is not None:
                stats["peer_filtered"] += 1
                stats["peer_filtered_by_topic"][peer_topic] += 1
                continue
            points.append((wx, wy, wz))
            if 0 < self.max_points <= len(points):
                break

        self.peer_filtered_total += int(stats["peer_filtered"])
        self.peer_stale_samples_total += len(stale_peer_topics)
        for topic, count in stats["peer_filtered_by_topic"].items():
            self.peer_filtered_by_topic[topic] += int(count)
        stats["peer_filtered_total"] = self.peer_filtered_total
        stats["peer_stale_samples_total"] = self.peer_stale_samples_total
        stats["peer_filtered_by_topic_total"] = dict(self.peer_filtered_by_topic)

        if len(points) < self.min_publish_points:
            self.rejected_sparse_output += 1
            stats["reject_reason"] = "sparse_output"
            stats["published_points"] = len(points)
            stats["rejected_sparse_output"] = self.rejected_sparse_output
            stats["raw_bounds"] = self._final_bounds(raw_bounds)
            stats["body_bounds"] = self._final_bounds(body_bounds)
            self.last_stats = stats
            self._maybe_write_diagnostics(stats)
            self._write_history(stats, force=True)
            return

        out_stamp = msg.header.stamp
        if self.output_stamp_mode in {"now", "ros_now", "wall_now"}:
            out_stamp = rospy.Time.now()
        elif self.output_stamp_mode not in {"input", "source", ""}:
            rospy.logwarn_throttle(10.0, "Unknown output_stamp_mode=%s, using input cloud stamp", self.output_stamp_mode)
        out = pc2.create_cloud_xyz32(Header(stamp=out_stamp, frame_id=self.frame_id), points)
        self.pub.publish(out)
        self.published += 1
        stats["published_clouds"] = self.published
        stats["published_points"] = len(points)
        stats["raw_bounds"] = self._final_bounds(raw_bounds)
        stats["body_bounds"] = self._final_bounds(body_bounds)
        if points:
            xs, ys, zs = zip(*points)
            stats["world_bounds"] = {
                "min": [min(xs), min(ys), min(zs)],
                "max": [max(xs), max(ys), max(zs)],
            }
        self.last_stats = stats
        self._maybe_write_diagnostics(stats)
        self._write_history(stats)

    def _select_odom_locked(self, cloud_stamp: float) -> tuple[Odometry | None, dict]:
        stats = {
            "mode": "nearest_stamp",
            "buffer_size": len(self.odom_buffer),
            "buffer_capacity": self.odom_buffer_size,
            "fallback": "",
        }
        if not self.odom_buffer:
            stats["mode"] = "none"
            stats["fallback"] = "empty_buffer"
            return None, stats
        if cloud_stamp <= 0.0:
            stats["mode"] = "latest"
            stats["fallback"] = "cloud_stamp_zero"
            odom = self.latest_odom or self.odom_buffer[-1]
            stats["selected_stamp"] = odom.header.stamp.to_sec()
            return odom, stats
        if self.odom_sync_mode in {"latest", "latest_odom"}:
            stats["mode"] = "latest"
            stats["fallback"] = "configured_latest_odom"
            stats["skip_stale_gate"] = True
            odom = self.latest_odom or self.odom_buffer[-1]
            stats["selected_stamp"] = odom.header.stamp.to_sec()
            stats["cloud_to_selected_dt_s"] = cloud_stamp - stats["selected_stamp"]
            return odom, stats
        if self.odom_sync_mode in {"auto_mixed_time", "mixed_time_latest"}:
            latest = self.latest_odom or self.odom_buffer[-1]
            latest_stamp = latest.header.stamp.to_sec()
            if self._looks_like_mixed_time(cloud_stamp, latest_stamp):
                stats["mode"] = "latest"
                stats["fallback"] = "mixed_time_domain_latest_odom"
                stats["skip_stale_gate"] = True
                stats["selected_stamp"] = latest_stamp
                stats["cloud_to_selected_dt_s"] = cloud_stamp - latest_stamp
                stats["oldest_stamp"] = self.odom_buffer[0].header.stamp.to_sec()
                stats["newest_stamp"] = self.odom_buffer[-1].header.stamp.to_sec()
                return latest, stats
        best = min(self.odom_buffer, key=lambda candidate: abs(cloud_stamp - candidate.header.stamp.to_sec()))
        selected_stamp = best.header.stamp.to_sec()
        stats["selected_stamp"] = selected_stamp
        stats["cloud_to_selected_dt_s"] = cloud_stamp - selected_stamp
        stats["oldest_stamp"] = self.odom_buffer[0].header.stamp.to_sec()
        stats["newest_stamp"] = self.odom_buffer[-1].header.stamp.to_sec()
        if selected_stamp <= 0.0:
            stats["fallback"] = "selected_stamp_zero"
        elif cloud_stamp < stats["oldest_stamp"]:
            stats["fallback"] = "cloud_older_than_buffer"
        elif cloud_stamp > stats["newest_stamp"]:
            stats["fallback"] = "cloud_newer_than_buffer"
        return best, stats

    def _looks_like_mixed_time(self, cloud_stamp: float, odom_stamp: float) -> bool:
        if cloud_stamp <= 0.0 or odom_stamp <= 0.0:
            return False
        if abs(cloud_stamp - odom_stamp) < self.mixed_time_threshold_s:
            return False
        cloud_epoch_like = cloud_stamp > self.mixed_time_threshold_s
        odom_epoch_like = odom_stamp > self.mixed_time_threshold_s
        return cloud_epoch_like != odom_epoch_like

    def _resolve_mount_mode(self, frame_id: str) -> str:
        mode = self.mount_mode.strip().lower()
        if mode not in {"auto", "sunray_auto"}:
            return mode
        # Sunray's Livox plugin publishes sensor-local points but labels the
        # ROS frame as base_link. Treat auto as the accepted MID360 mount
        # transform instead of trusting the header name.
        return "sensor_to_body"

    def _rotation_matrix(self, odom_rpy: tuple[float, float, float], quat: list[float]) -> tuple[str, object]:
        mode = self.rotation_mode.strip().lower()
        if mode in {"full", "full_quat", "full_quaternion"}:
            return "full", quaternion_matrix(quat)
        if mode in {"none", "translation_only"}:
            return "translation_only", euler_matrix(0.0, 0.0, 0.0)
        if mode not in {"yaw_only", "yaw"}:
            rospy.logwarn_throttle(10.0, "Unknown rotation_mode=%s, using full quaternion pose", self.rotation_mode)
            return "full", quaternion_matrix(quat)
        return "yaw_only", euler_matrix(0.0, 0.0, odom_rpy[2])

    def _sensor_to_body(self, x: float, y: float, z: float, mode: str) -> tuple[float, float, float]:
        if mode == "none":
            return x, y, z
        if mode == "yaw_only":
            cy = math.cos(self.mount_rpy[2])
            sy = math.sin(self.mount_rpy[2])
            return cy * x - sy * y, sy * x + cy * y, z
        if mode != "sensor_to_body":
            rospy.logwarn_throttle(10.0, "Unknown effective mount_mode=%s, using none", mode)
            return x, y, z
        bx = self.mount_mat[0, 0] * x + self.mount_mat[0, 1] * y + self.mount_mat[0, 2] * z + self.mount_xyz[0]
        by = self.mount_mat[1, 0] * x + self.mount_mat[1, 1] * y + self.mount_mat[1, 2] * z + self.mount_xyz[1]
        bz = self.mount_mat[2, 0] * x + self.mount_mat[2, 1] * y + self.mount_mat[2, 2] * z + self.mount_xyz[2]
        return bx, by, bz

    @staticmethod
    def _empty_bounds() -> dict[str, list[float] | int]:
        return {"count": 0, "min": [math.inf, math.inf, math.inf], "max": [-math.inf, -math.inf, -math.inf]}

    @staticmethod
    def _update_bounds(bounds: dict[str, list[float] | int], x: float, y: float, z: float) -> None:
        bounds["count"] = int(bounds["count"]) + 1
        mins = bounds["min"]
        maxs = bounds["max"]
        assert isinstance(mins, list) and isinstance(maxs, list)
        mins[0] = min(mins[0], x)
        mins[1] = min(mins[1], y)
        mins[2] = min(mins[2], z)
        maxs[0] = max(maxs[0], x)
        maxs[1] = max(maxs[1], y)
        maxs[2] = max(maxs[2], z)

    @staticmethod
    def _final_bounds(bounds: dict[str, list[float] | int]) -> dict | None:
        if int(bounds["count"]) <= 0:
            return None
        return bounds

    def _maybe_write_diagnostics(self, stats: dict) -> None:
        now = time.time()
        if now - self.last_log_wall < self.log_period_s:
            return
        self.last_log_wall = now
        rospy.loginfo(
            "Goal4 pointcloud stats: input=%d near=%d far=%d self=%d peer=%d stale_peer=%d z=%d published=%d mount=%s/%s rotation=%s/%s reject=%s",
            stats.get("input_points", 0),
            stats.get("near_sensor", 0),
            stats.get("far_sensor", 0),
            stats.get("self_filtered", 0),
            stats.get("peer_filtered", 0),
            len(stats.get("peer_filter_stale_topics", [])),
            stats.get("z_filtered", 0),
            stats.get("published_points", 0),
            self.mount_mode,
            stats.get("effective_mount_mode", ""),
            self.rotation_mode,
            stats.get("effective_rotation_mode", ""),
            stats.get("reject_reason", ""),
        )
        if self.diagnostics_path:
            try:
                with open(self.diagnostics_path, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2, sort_keys=True)
            except OSError as exc:
                rospy.logwarn_throttle(10.0, "Failed to write diagnostics %s: %s", self.diagnostics_path, exc)

    def _write_history(self, stats: dict, force: bool = False) -> None:
        if not self.history_path:
            return
        if (
            not force
            and self.received > self.history_first_n
            and self.received % self.history_period_clouds != 0
        ):
            return
        try:
            with open(self.history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(stats, sort_keys=True) + "\n")
        except OSError as exc:
            rospy.logwarn_throttle(10.0, "Failed to write history %s: %s", self.history_path, exc)


def main() -> None:
    rospy.init_node("mosim_goal4_pointcloud_to_world", anonymous=True)
    node = PointCloudToWorld()
    rospy.loginfo(
        "Goal4 pointcloud transform: %s -> %s using %s",
        node.input_topic,
        node.output_topic,
        node.odom_topic,
    )
    rospy.loginfo(
        "Goal4 pointcloud filters: mount_mode=%s rotation_mode=%s odom_sync=%s output_stamp=%s mount_xyz=%s mount_rpy=%s range=[%.3f, %.3f] self_radius=%.3f peer_topics=%s peer_radius_xy=%.3f peer_z=[%.3f, %.3f] peer_max_age=%.3f z=[%.3f, %.3f] odom_z=[%.3f, %.3f] max_abs_roll_pitch=%.1f min_publish=%d",
        node.mount_mode,
        node.rotation_mode,
        node.odom_sync_mode,
        node.output_stamp_mode,
        node.mount_xyz,
        node.mount_rpy,
        node.min_sensor_range_m,
        node.max_sensor_range_m,
        node.self_filter_radius_m,
        node.peer_odom_topics,
        node.peer_filter_radius_xy_m,
        node.peer_filter_z_min_m,
        node.peer_filter_z_max_m,
        node.peer_odom_max_age_s,
        node.min_world_z_m,
        node.max_world_z_m,
        node.min_odom_z_m,
        node.max_odom_z_m,
        node.max_abs_roll_pitch_deg,
        node.min_publish_points,
    )
    rospy.spin()


if __name__ == "__main__":
    main()
