#!/usr/bin/env python3
"""Measure the effective FUEL cloud/pose synchronization contract."""

from __future__ import annotations

import json
import math
import os
import threading
import time

import message_filters
import rospy
import sensor_msgs.point_cloud2 as pc2
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import PointCloud2


class FrontendDiagnostic:
    def __init__(self) -> None:
        self.cloud_topic = rospy.get_param("~cloud_topic", "/uav1/livox_world")
        self.pose_topic = rospy.get_param("~pose_topic", "/uav1/mavros/local_position/pose")
        self.output_path = rospy.get_param("~output_path", "")
        self.queue_size = int(rospy.get_param("~queue_size", 100))
        self.slop_s = float(rospy.get_param("~slop_s", 0.1))
        self.write_period_s = float(rospy.get_param("~write_period_s", 2.0))
        self.lock = threading.Lock()
        self.start_wall = time.time()
        self.cloud_count = 0
        self.pose_count = 0
        self.sync_count = 0
        self.dt_abs_sum = 0.0
        self.dt_abs_max = 0.0
        self.last_sync = {}

        rospy.Subscriber(self.cloud_topic, PointCloud2, self.on_cloud, queue_size=20)
        rospy.Subscriber(self.pose_topic, PoseStamped, self.on_pose, queue_size=50)
        cloud_sub = message_filters.Subscriber(self.cloud_topic, PointCloud2, queue_size=20)
        pose_sub = message_filters.Subscriber(self.pose_topic, PoseStamped, queue_size=50)
        sync = message_filters.ApproximateTimeSynchronizer(
            [cloud_sub, pose_sub], self.queue_size, self.slop_s, allow_headerless=False
        )
        sync.registerCallback(self.on_sync)
        self.cloud_sub = cloud_sub
        self.pose_sub = pose_sub
        self.sync = sync
        self.timer = rospy.Timer(rospy.Duration(self.write_period_s), self.on_timer)

    def on_cloud(self, _msg: PointCloud2) -> None:
        with self.lock:
            self.cloud_count += 1

    def on_pose(self, _msg: PoseStamped) -> None:
        with self.lock:
            self.pose_count += 1

    def on_sync(self, cloud: PointCloud2, pose: PoseStamped) -> None:
        cloud_stamp = cloud.header.stamp.to_sec()
        pose_stamp = pose.header.stamp.to_sec()
        dt = abs(cloud_stamp - pose_stamp)
        point_count = int(cloud.width) * int(cloud.height)
        bounds = None
        min_xyz = [math.inf, math.inf, math.inf]
        max_xyz = [-math.inf, -math.inf, -math.inf]
        sampled = 0
        for index, point in enumerate(pc2.read_points(cloud, field_names=("x", "y", "z"), skip_nans=True)):
            if index % 20:
                continue
            xyz = [float(point[0]), float(point[1]), float(point[2])]
            for axis in range(3):
                min_xyz[axis] = min(min_xyz[axis], xyz[axis])
                max_xyz[axis] = max(max_xyz[axis], xyz[axis])
            sampled += 1
        if sampled:
            bounds = {"sampled_points": sampled, "min": min_xyz, "max": max_xyz}
        with self.lock:
            self.sync_count += 1
            self.dt_abs_sum += dt
            self.dt_abs_max = max(self.dt_abs_max, dt)
            self.last_sync = {
                "cloud_stamp": cloud_stamp,
                "pose_stamp": pose_stamp,
                "abs_stamp_delta_s": dt,
                "cloud_frame": cloud.header.frame_id,
                "pose_frame": pose.header.frame_id,
                "cloud_point_count": point_count,
                "sampled_cloud_bounds": bounds,
                "camera_position": [pose.pose.position.x, pose.pose.position.y, pose.pose.position.z],
            }

    def snapshot(self) -> dict:
        with self.lock:
            elapsed = max(1e-6, time.time() - self.start_wall)
            sync_ratio = self.sync_count / self.cloud_count if self.cloud_count else 0.0
            return {
                "schema": "mosim.fuel_cloud_pose_frontend_diagnostic.v1",
                "cloud_topic": self.cloud_topic,
                "pose_topic": self.pose_topic,
                "queue_size": self.queue_size,
                "slop_s": self.slop_s,
                "elapsed_wall_s": elapsed,
                "cloud_received": self.cloud_count,
                "pose_received": self.pose_count,
                "synchronized_callbacks": self.sync_count,
                "cloud_hz_wall": self.cloud_count / elapsed,
                "pose_hz_wall": self.pose_count / elapsed,
                "sync_hz_wall": self.sync_count / elapsed,
                "sync_to_cloud_ratio": sync_ratio,
                "mean_abs_stamp_delta_s": self.dt_abs_sum / self.sync_count if self.sync_count else None,
                "max_abs_stamp_delta_s": self.dt_abs_max if self.sync_count else None,
                "last_sync": self.last_sync,
            }

    def on_timer(self, _event) -> None:
        data = self.snapshot()
        if self.output_path:
            directory = os.path.dirname(self.output_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            tmp = self.output_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
                handle.write("\n")
            os.replace(tmp, self.output_path)
        rospy.loginfo_throttle(
            10.0,
            "FUEL frontend: cloud=%d pose=%d sync=%d ratio=%.3f mean_dt=%s",
            data["cloud_received"],
            data["pose_received"],
            data["synchronized_callbacks"],
            data["sync_to_cloud_ratio"],
            data["mean_abs_stamp_delta_s"],
        )


def main() -> None:
    rospy.init_node("mosim_fuel_cloud_pose_frontend_diagnostic", anonymous=False)
    FrontendDiagnostic()
    rospy.spin()


if __name__ == "__main__":
    main()
