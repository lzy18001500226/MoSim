#!/usr/bin/env python3
"""Synthetic MoSim-like ROS1 stimulus for the FUEL-D2 adapter dry-run.

This is an interface dry-run helper only. It publishes world-frame point clouds
that match FUEL map_ros cloud semantics and records whether FUEL produces a
B-spline and observed PositionCommand. It must not be used as Gazebo or sensor
success evidence.
"""

import argparse
import json
import math
import os
import sys
from typing import List, Tuple

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2

try:
    from bspline.msg import Bspline
    from quadrotor_msgs.msg import PositionCommand
except ImportError as exc:  # pragma: no cover - exercised only in ROS env
    sys.stderr.write("missing_fuel_messages: %s\n" % exc)
    raise


Point = Tuple[float, float, float]


class FuelD2Stimulus:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.start_time = rospy.Time.now()
        self.trigger_sent = False
        self.bspline_count = 0
        self.position_cmd_count = 0
        self.position_cmd_after_bspline = 0
        self.occupancy_local_count = 0
        self.occupancy_all_count = 0
        self.first_bspline_time_s = None
        self.first_position_cmd_time_s = None
        self.first_position_cmd_after_bspline_time_s = None
        self.first_bspline = {}
        self.last_position_cmd = {}

        self.odom_pub = rospy.Publisher(args.odom_topic, Odometry, queue_size=10)
        self.pose_pub = rospy.Publisher(args.sensor_pose_topic, PoseStamped, queue_size=10)
        self.cloud_pub = rospy.Publisher(args.cloud_topic, PointCloud2, queue_size=10)
        self.path_pub = rospy.Publisher(args.waypoint_topic, Path, queue_size=1, latch=True)

        rospy.Subscriber(args.bspline_topic, Bspline, self._bspline_cb, queue_size=10)
        rospy.Subscriber(args.position_cmd_topic, PositionCommand, self._position_cmd_cb, queue_size=50)
        rospy.Subscriber("/sdf_map/occupancy_local", PointCloud2, self._occupancy_local_cb, queue_size=10)
        rospy.Subscriber("/sdf_map/occupancy_all", PointCloud2, self._occupancy_all_cb, queue_size=10)

        self.cloud_points = self._build_cloud_points()

    def _elapsed_s(self) -> float:
        return max(0.0, (rospy.Time.now() - self.start_time).to_sec())

    def _build_cloud_points(self) -> List[Point]:
        points: List[Point] = []
        sensor_z = self.args.z

        # Dense max-range shell. FUEL treats over-range endpoints as freespace
        # rays up to sdf_map/max_ray_length, which creates free/unknown
        # frontiers without injecting a hidden global map.
        for yaw_deg in range(0, 360, self.args.shell_yaw_step_deg):
            yaw = math.radians(yaw_deg)
            for pitch_deg in range(-12, 13, self.args.shell_pitch_step_deg):
                pitch = math.radians(pitch_deg)
                r = self.args.free_shell_radius_m
                x = self.args.x + r * math.cos(pitch) * math.cos(yaw)
                y = self.args.y + r * math.cos(pitch) * math.sin(yaw)
                z = sensor_z + r * math.sin(pitch)
                if self.args.min_z <= z <= self.args.max_z:
                    points.append((x, y, z))

        # A small visible pillar-like obstacle near the robot makes the dry-run
        # map nonempty while keeping the main D2 assertion focused on interfaces.
        cyl_x = self.args.obstacle_x
        cyl_y = self.args.obstacle_y
        radius = self.args.obstacle_radius_m
        for z_i in range(int(self.args.min_z * 20), int(self.args.max_z * 20) + 1):
            z = z_i / 20.0
            for a_deg in range(0, 360, 12):
                a = math.radians(a_deg)
                points.append((cyl_x + radius * math.cos(a), cyl_y + radius * math.sin(a), z))

        return points

    def _odom_msg(self, stamp: rospy.Time) -> Odometry:
        msg = Odometry()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.child_frame_id = "base_link"
        msg.pose.pose.position.x = self.args.x
        msg.pose.pose.position.y = self.args.y
        msg.pose.pose.position.z = self.args.z
        msg.pose.pose.orientation.w = 1.0
        return msg

    def _pose_msg(self, stamp: rospy.Time) -> PoseStamped:
        msg = PoseStamped()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.pose.position.x = self.args.x
        msg.pose.position.y = self.args.y
        msg.pose.position.z = self.args.z
        msg.pose.orientation.w = 1.0
        return msg

    def _cloud_msg(self, stamp: rospy.Time) -> PointCloud2:
        header = self._pose_msg(stamp).header
        return point_cloud2.create_cloud_xyz32(header, self.cloud_points)

    def _trigger_msg(self, stamp: rospy.Time) -> Path:
        msg = Path()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose.position.x = self.args.trigger_x
        pose.pose.position.y = self.args.trigger_y
        pose.pose.position.z = self.args.trigger_z
        pose.pose.orientation.w = 1.0
        msg.poses.append(pose)
        return msg

    def _bspline_cb(self, msg: Bspline) -> None:
        self.bspline_count += 1
        if self.first_bspline_time_s is None:
            self.first_bspline_time_s = self._elapsed_s()
            self.first_bspline = {
                "traj_id": int(msg.traj_id),
                "order": int(msg.order),
                "pos_pts": len(msg.pos_pts),
                "knots": len(msg.knots),
                "yaw_pts": len(msg.yaw_pts),
            }

    def _position_cmd_cb(self, msg: PositionCommand) -> None:
        self.position_cmd_count += 1
        if self.first_position_cmd_time_s is None:
            self.first_position_cmd_time_s = self._elapsed_s()
        if self.bspline_count > 0:
            self.position_cmd_after_bspline += 1
            if self.first_position_cmd_after_bspline_time_s is None:
                self.first_position_cmd_after_bspline_time_s = self._elapsed_s()
        self.last_position_cmd = {
            "x": msg.position.x,
            "y": msg.position.y,
            "z": msg.position.z,
            "yaw": msg.yaw,
            "trajectory_id": int(msg.trajectory_id),
        }

    def _occupancy_local_cb(self, _msg: PointCloud2) -> None:
        self.occupancy_local_count += 1

    def _occupancy_all_cb(self, _msg: PointCloud2) -> None:
        self.occupancy_all_count += 1

    def run(self) -> int:
        rate = rospy.Rate(self.args.publish_hz)
        deadline = rospy.Time.now() + rospy.Duration(self.args.duration_s)
        while not rospy.is_shutdown() and rospy.Time.now() < deadline:
            stamp = rospy.Time.now()
            self.odom_pub.publish(self._odom_msg(stamp))
            self.pose_pub.publish(self._pose_msg(stamp))
            self.cloud_pub.publish(self._cloud_msg(stamp))

            if not self.trigger_sent and self._elapsed_s() >= self.args.trigger_after_s:
                self.path_pub.publish(self._trigger_msg(stamp))
                self.trigger_sent = True
                rospy.logwarn("FUEL_D2_TRIGGER_SENT")

            if self.bspline_count > 0 and self.position_cmd_after_bspline > 5:
                break
            rate.sleep()

        return self._write_summary()

    def _write_summary(self) -> int:
        success = self.bspline_count > 0 and self.position_cmd_after_bspline > 0
        summary = {
            "status": "passed" if success else "failed",
            "claim": "FUEL_D2 adapter dry-run only; no Gazebo/PX4/MAVROS control claim",
            "odom_topic": self.args.odom_topic,
            "sensor_pose_topic": self.args.sensor_pose_topic,
            "cloud_topic": self.args.cloud_topic,
            "waypoint_topic": self.args.waypoint_topic,
            "bspline_topic": self.args.bspline_topic,
            "position_cmd_topic": self.args.position_cmd_topic,
            "cloud_points_per_frame": len(self.cloud_points),
            "trigger_sent": self.trigger_sent,
            "bspline_count": self.bspline_count,
            "position_cmd_count": self.position_cmd_count,
            "position_cmd_after_bspline": self.position_cmd_after_bspline,
            "occupancy_local_count": self.occupancy_local_count,
            "occupancy_all_count": self.occupancy_all_count,
            "first_bspline_time_s": self.first_bspline_time_s,
            "first_position_cmd_time_s": self.first_position_cmd_time_s,
            "first_position_cmd_after_bspline_time_s": self.first_position_cmd_after_bspline_time_s,
            "first_bspline": self.first_bspline,
            "last_position_cmd": self.last_position_cmd,
        }
        os.makedirs(os.path.dirname(os.path.abspath(self.args.summary_file)), exist_ok=True)
        with open(self.args.summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
            f.write("\n")
        print("FUEL_D2_STIMULUS_SUMMARY=%s" % self.args.summary_file)
        print("FUEL_D2_STIMULUS_STATUS=%s" % summary["status"])
        return 0 if success else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=45.0)
    parser.add_argument("--trigger-after-s", type=float, default=8.0)
    parser.add_argument("--publish-hz", type=float, default=15.0)
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--odom-topic", default="/mosim/fuel_d2/odom")
    parser.add_argument("--sensor-pose-topic", default="/mosim/fuel_d2/sensor_pose")
    parser.add_argument("--cloud-topic", default="/mosim/fuel_d2/cloud")
    parser.add_argument("--waypoint-topic", default="/waypoint_generator/waypoints")
    parser.add_argument("--bspline-topic", default="/planning/bspline")
    parser.add_argument("--position-cmd-topic", default="/mosim/fuel_d2/position_cmd_observed")
    parser.add_argument("--x", type=float, default=0.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--z", type=float, default=1.0)
    parser.add_argument("--trigger-x", type=float, default=2.0)
    parser.add_argument("--trigger-y", type=float, default=0.0)
    parser.add_argument("--trigger-z", type=float, default=1.0)
    parser.add_argument("--min-z", type=float, default=0.45)
    parser.add_argument("--max-z", type=float, default=1.85)
    parser.add_argument("--free-shell-radius-m", type=float, default=5.2)
    parser.add_argument("--shell-yaw-step-deg", type=int, default=2)
    parser.add_argument("--shell-pitch-step-deg", type=int, default=4)
    parser.add_argument("--obstacle-x", type=float, default=2.0)
    parser.add_argument("--obstacle-y", type=float, default=0.0)
    parser.add_argument("--obstacle-radius-m", type=float, default=0.25)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("fuel_d2_synthetic_stimulus", anonymous=False)
    return FuelD2Stimulus(args).run()


if __name__ == "__main__":
    sys.exit(main())
