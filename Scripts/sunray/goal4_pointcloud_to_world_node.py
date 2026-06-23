#!/usr/bin/env python3
"""Transform Sunray local MID360 PointCloud2 into a world-frame cloud for EGO."""

from __future__ import annotations

import json
import math
import threading
import time

import rospy
import sensor_msgs.point_cloud2 as pc2
from nav_msgs.msg import Odometry
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
from tf.transformations import euler_matrix, quaternion_matrix


class PointCloudToWorld:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_point_topic", "/uav1/livox/lidar")
        self.output_topic = rospy.get_param("~output_point_topic", "/uav1/livox_world")
        self.odom_topic = rospy.get_param("~odom_topic", "/uav1/mavros/local_position/odom")
        self.frame_id = rospy.get_param("~frame_id", "world")
        self.max_points = int(rospy.get_param("~max_points", 30000))
        self.stride = max(1, int(rospy.get_param("~stride", 1)))
        self.mount_mode = str(rospy.get_param("~mount_mode", "sensor_to_body"))
        self.mount_xyz = self._get_float_list("~mount_xyz", [-0.000005, 0.032295, 0.050167], 3)
        self.mount_rpy = self._get_float_list("~mount_rpy", [0.0, 0.0, 4.712389], 3)
        self.min_sensor_range_m = float(rospy.get_param("~min_sensor_range_m", 0.25))
        self.self_filter_radius_m = float(rospy.get_param("~self_filter_radius_m", 0.35))
        self.min_world_z_m = float(rospy.get_param("~min_world_z_m", 0.08))
        self.max_world_z_m = float(rospy.get_param("~max_world_z_m", 2.20))
        self.log_period_s = float(rospy.get_param("~log_period_s", 5.0))
        self.diagnostics_path = str(rospy.get_param("~diagnostics_path", ""))
        self.mount_mat = euler_matrix(self.mount_rpy[0], self.mount_rpy[1], self.mount_rpy[2])
        self.lock = threading.Lock()
        self.latest_odom: Odometry | None = None
        self.received = 0
        self.published = 0
        self.last_stats = {}
        self.last_log_wall = 0.0
        self.pub = rospy.Publisher(self.output_topic, PointCloud2, queue_size=2)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=20)
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

    def on_odom(self, msg: Odometry) -> None:
        with self.lock:
            self.latest_odom = msg

    def on_cloud(self, msg: PointCloud2) -> None:
        with self.lock:
            odom = self.latest_odom
        self.received += 1
        if odom is None:
            return

        p = odom.pose.pose.position
        q = odom.pose.pose.orientation
        mat = quaternion_matrix([q.x, q.y, q.z, q.w])
        tx, ty, tz = float(p.x), float(p.y), float(p.z)

        points: list[tuple[float, float, float]] = []
        stats = {
            "received_clouds": self.received,
            "input_points": 0,
            "stride_skipped": 0,
            "invalid": 0,
            "near_sensor": 0,
            "self_filtered": 0,
            "z_filtered": 0,
            "published_points": 0,
            "mount_mode": self.mount_mode,
        }
        for i, pt in enumerate(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)):
            stats["input_points"] += 1
            if i % self.stride:
                stats["stride_skipped"] += 1
                continue
            sx, sy, sz = float(pt[0]), float(pt[1]), float(pt[2])
            if not (math.isfinite(sx) and math.isfinite(sy) and math.isfinite(sz)):
                stats["invalid"] += 1
                continue
            sensor_range = math.sqrt(sx * sx + sy * sy + sz * sz)
            if sensor_range < self.min_sensor_range_m:
                stats["near_sensor"] += 1
                continue

            bx, by, bz = self._sensor_to_body(sx, sy, sz)
            body_range = math.sqrt(bx * bx + by * by + bz * bz)
            if body_range < self.self_filter_radius_m:
                stats["self_filtered"] += 1
                continue

            wx = mat[0, 0] * bx + mat[0, 1] * by + mat[0, 2] * bz + tx
            wy = mat[1, 0] * bx + mat[1, 1] * by + mat[1, 2] * bz + ty
            wz = mat[2, 0] * bx + mat[2, 1] * by + mat[2, 2] * bz + tz
            if wz < self.min_world_z_m or wz > self.max_world_z_m:
                stats["z_filtered"] += 1
                continue
            points.append((wx, wy, wz))
            if 0 < self.max_points <= len(points):
                break

        out = pc2.create_cloud_xyz32(Header(stamp=msg.header.stamp, frame_id=self.frame_id), points)
        self.pub.publish(out)
        self.published += 1
        stats["published_clouds"] = self.published
        stats["published_points"] = len(points)
        if points:
            xs, ys, zs = zip(*points)
            stats["world_bounds"] = {
                "min": [min(xs), min(ys), min(zs)],
                "max": [max(xs), max(ys), max(zs)],
            }
        self.last_stats = stats
        self._maybe_write_diagnostics(stats)

    def _sensor_to_body(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        if self.mount_mode == "none":
            return x, y, z
        if self.mount_mode == "yaw_only":
            cy = math.cos(self.mount_rpy[2])
            sy = math.sin(self.mount_rpy[2])
            return cy * x - sy * y, sy * x + cy * y, z
        if self.mount_mode != "sensor_to_body":
            rospy.logwarn_throttle(10.0, "Unknown mount_mode=%s, using none", self.mount_mode)
            return x, y, z
        bx = self.mount_mat[0, 0] * x + self.mount_mat[0, 1] * y + self.mount_mat[0, 2] * z + self.mount_xyz[0]
        by = self.mount_mat[1, 0] * x + self.mount_mat[1, 1] * y + self.mount_mat[1, 2] * z + self.mount_xyz[1]
        bz = self.mount_mat[2, 0] * x + self.mount_mat[2, 1] * y + self.mount_mat[2, 2] * z + self.mount_xyz[2]
        return bx, by, bz

    def _maybe_write_diagnostics(self, stats: dict) -> None:
        now = time.time()
        if now - self.last_log_wall < self.log_period_s:
            return
        self.last_log_wall = now
        rospy.loginfo(
            "Goal4 pointcloud stats: input=%d near=%d self=%d z=%d published=%d mode=%s",
            stats.get("input_points", 0),
            stats.get("near_sensor", 0),
            stats.get("self_filtered", 0),
            stats.get("z_filtered", 0),
            stats.get("published_points", 0),
            self.mount_mode,
        )
        if self.diagnostics_path:
            try:
                with open(self.diagnostics_path, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2, sort_keys=True)
            except OSError as exc:
                rospy.logwarn_throttle(10.0, "Failed to write diagnostics %s: %s", self.diagnostics_path, exc)


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
        "Goal4 pointcloud filters: mount_mode=%s mount_xyz=%s mount_rpy=%s min_range=%.3f self_radius=%.3f z=[%.3f, %.3f]",
        node.mount_mode,
        node.mount_xyz,
        node.mount_rpy,
        node.min_sensor_range_m,
        node.self_filter_radius_m,
        node.min_world_z_m,
        node.max_world_z_m,
    )
    rospy.spin()


if __name__ == "__main__":
    main()
