#!/usr/bin/env python3
"""Synthetic MoSim-like ROS1 stimulus for RACER-D2.

This helper publishes per-UAV odometry, sensor pose and point-cloud inputs for
uav1/uav2/uav3 and monitors RACER planner outputs. It is an adapter dry-run
only; it is not Gazebo/PX4/MAVROS/RViz or exploration-success evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rospy.msg import AnyMsg
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2

try:
    from bspline.msg import Bspline
    from quadrotor_msgs.msg import PositionCommand
except ImportError as exc:  # pragma: no cover - only exercised inside ROS env
    sys.stderr.write("missing_racer_messages: %s\n" % exc)
    raise


Point = Tuple[float, float, float]


@dataclass(frozen=True)
class UavConfig:
    name: str
    drone_id: int
    x: float
    y: float
    z: float


class Counter:
    def __init__(self, topic: str) -> None:
        self.topic = topic
        self.count = 0
        self.first_time_s = None
        self.last_time_s = None
        self.last_summary = {}

    def observe(self, summary: dict | None = None) -> None:
        now = rospy.get_time()
        self.count += 1
        if self.first_time_s is None:
            self.first_time_s = now
        self.last_time_s = now
        if summary:
            self.last_summary = summary


class RacerD2Stimulus:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.start_wall = time.time()
        self.start_ros = rospy.Time.now()
        self.trigger_sent = False
        self.trigger_publish_count = 0
        self.last_trigger_elapsed_s = -1.0
        self.uavs = [
            UavConfig("uav1", 1, -1.0, 0.6, 1.0),
            UavConfig("uav2", 2, -1.0, 0.0, 1.0),
            UavConfig("uav3", 3, -1.0, -0.6, 1.0),
        ]

        self.odom_pubs = {}
        self.pose_pubs = {}
        self.cloud_pubs = {}
        self.cloud_points = {}
        self.input_counts = {u.name: {"odom": 0, "sensor_pose": 0, "cloud": 0} for u in self.uavs}
        for uav in self.uavs:
            self.odom_pubs[uav.name] = rospy.Publisher(
                f"/{uav.name}/mosim/racer_d2/odom", Odometry, queue_size=10
            )
            self.pose_pubs[uav.name] = rospy.Publisher(
                f"/{uav.name}/mosim/racer_d2/sensor_pose", PoseStamped, queue_size=10
            )
            self.cloud_pubs[uav.name] = rospy.Publisher(
                f"/{uav.name}/mosim/racer_d2/cloud", PointCloud2, queue_size=10
            )
            self.cloud_points[uav.name] = self._build_cloud_points(uav)

        self.trigger_pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=1, latch=True)

        self.bspline_counts: Dict[str, Counter] = {}
        self.pos_cmd_counts: Dict[str, Counter] = {}
        self.occupancy_counts: Dict[str, Dict[str, Counter]] = {}
        for uav in self.uavs:
            b_topic = f"/planning/bspline_{uav.drone_id}"
            p_topic = f"/{uav.name}/mosim/racer_d2/pos_cmd"
            self.bspline_counts[uav.name] = Counter(b_topic)
            self.pos_cmd_counts[uav.name] = Counter(p_topic)
            rospy.Subscriber(b_topic, Bspline, self._make_bspline_cb(uav.name), queue_size=10)
            rospy.Subscriber(p_topic, PositionCommand, self._make_pos_cmd_cb(uav.name), queue_size=50)

            self.occupancy_counts[uav.name] = {}
            for suffix in ("occupancy_local", "occupancy_all", "occupancy_local_inflate"):
                topic = f"/sdf_map/{suffix}_{uav.drone_id}"
                counter = Counter(topic)
                self.occupancy_counts[uav.name][suffix] = counter
                rospy.Subscriber(topic, PointCloud2, self._make_cloud_counter_cb(counter), queue_size=10)

        self.shared_counts: Dict[str, Counter] = {}
        for topic in (
            "/swarm_expl/drone_state",
            "/swarm_expl/pair_opt",
            "/swarm_expl/pair_opt_res",
            "/swarm_expl/grid_tour",
            "/swarm_expl/hgrid",
            "/multi_map_manager/chunk_stamps",
            "/multi_map_manager/chunk_data",
            "/planning/swarm_traj",
        ):
            counter = Counter(topic)
            self.shared_counts[topic] = counter
            rospy.Subscriber(topic, AnyMsg, self._make_any_counter_cb(counter), queue_size=100)

    def _elapsed_s(self) -> float:
        return max(0.0, (rospy.Time.now() - self.start_ros).to_sec())

    def _build_cloud_points(self, uav: UavConfig) -> List[Point]:
        points: List[Point] = []
        # Free-space rays with max-range endpoints. These create known-free to
        # unknown boundaries for RACER's frontier detector without exposing a
        # full oracle map to the planner.
        for yaw_deg in range(0, 360, self.args.shell_yaw_step_deg):
            yaw = math.radians(yaw_deg)
            for pitch_deg in range(-10, 12, self.args.shell_pitch_step_deg):
                pitch = math.radians(pitch_deg)
                r = self.args.free_shell_radius_m
                x = uav.x + r * math.cos(pitch) * math.cos(yaw)
                y = uav.y + r * math.cos(pitch) * math.sin(yaw)
                z = uav.z + r * math.sin(pitch)
                if self.args.min_z <= z <= self.args.max_z:
                    points.append((x, y, z))

        # Sparse obstacle columns in front of the three vehicles. D2 only
        # checks adapter semantics, so the map is intentionally small.
        obstacle_centers = [(1.6, -0.8), (1.8, 0.8), (3.0, 0.0)]
        for ox, oy in obstacle_centers:
            for z_i in range(int(self.args.min_z * 20), int(self.args.max_z * 20) + 1):
                z = z_i / 20.0
                for a_deg in range(0, 360, 18):
                    a = math.radians(a_deg)
                    points.append(
                        (
                            ox + self.args.obstacle_radius_m * math.cos(a),
                            oy + self.args.obstacle_radius_m * math.sin(a),
                            z,
                        )
                    )
        return points

    def _odom_msg(self, uav: UavConfig, stamp: rospy.Time) -> Odometry:
        msg = Odometry()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.child_frame_id = f"{uav.name}/base_link"
        msg.pose.pose.position.x = uav.x
        msg.pose.pose.position.y = uav.y
        msg.pose.pose.position.z = uav.z
        msg.pose.pose.orientation.w = 1.0
        return msg

    def _pose_msg(self, uav: UavConfig, stamp: rospy.Time) -> PoseStamped:
        msg = PoseStamped()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.pose.position.x = uav.x
        msg.pose.position.y = uav.y
        msg.pose.position.z = uav.z
        msg.pose.orientation.w = 1.0
        return msg

    def _cloud_msg(self, uav: UavConfig, stamp: rospy.Time) -> PointCloud2:
        header = self._pose_msg(uav, stamp).header
        return point_cloud2.create_cloud_xyz32(header, self.cloud_points[uav.name])

    def _trigger_msg(self, stamp: rospy.Time) -> PoseStamped:
        msg = PoseStamped()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.pose.position.x = self.args.trigger_x
        msg.pose.position.y = self.args.trigger_y
        msg.pose.position.z = self.args.trigger_z
        msg.pose.orientation.w = 1.0
        return msg

    def _make_bspline_cb(self, uav_name: str):
        def cb(msg: Bspline) -> None:
            self.bspline_counts[uav_name].observe(
                {
                    "traj_id": int(msg.traj_id),
                    "drone_id": int(getattr(msg, "drone_id", 0)),
                    "order": int(msg.order),
                    "pos_pts": len(msg.pos_pts),
                    "knots": len(msg.knots),
                    "yaw_pts": len(msg.yaw_pts),
                }
            )

        return cb

    def _make_pos_cmd_cb(self, uav_name: str):
        def cb(msg: PositionCommand) -> None:
            self.pos_cmd_counts[uav_name].observe(
                {
                    "trajectory_id": int(msg.trajectory_id),
                    "position": [msg.position.x, msg.position.y, msg.position.z],
                    "velocity": [msg.velocity.x, msg.velocity.y, msg.velocity.z],
                    "yaw": msg.yaw,
                }
            )

        return cb

    def _make_cloud_counter_cb(self, counter: Counter):
        def cb(msg: PointCloud2) -> None:
            counter.observe({"width": int(msg.width), "height": int(msg.height), "frame_id": msg.header.frame_id})

        return cb

    def _make_any_counter_cb(self, counter: Counter):
        def cb(_msg: AnyMsg) -> None:
            counter.observe()

        return cb

    def _published_topic_names(self) -> List[str]:
        try:
            return sorted(name for name, _type in rospy.get_published_topics(namespace="/"))
        except Exception:
            return []

    def run(self) -> int:
        rate = rospy.Rate(self.args.publish_hz)
        deadline = rospy.Time.now() + rospy.Duration(self.args.duration_s)
        while not rospy.is_shutdown() and rospy.Time.now() < deadline:
            stamp = rospy.Time.now()
            for uav in self.uavs:
                self.odom_pubs[uav.name].publish(self._odom_msg(uav, stamp))
                self.pose_pubs[uav.name].publish(self._pose_msg(uav, stamp))
                self.cloud_pubs[uav.name].publish(self._cloud_msg(uav, stamp))
                self.input_counts[uav.name]["odom"] += 1
                self.input_counts[uav.name]["sensor_pose"] += 1
                self.input_counts[uav.name]["cloud"] += 1

            outputs_ready = all(
                self.bspline_counts[u.name].count > 0 or self.pos_cmd_counts[u.name].count > 0
                for u in self.uavs
            )
            elapsed_s = self._elapsed_s()
            should_repeat_trigger = (
                elapsed_s >= self.args.trigger_after_s
                and not outputs_ready
                and (
                    not self.trigger_sent
                    or elapsed_s - self.last_trigger_elapsed_s >= self.args.trigger_repeat_interval_s
                )
            )
            if should_repeat_trigger:
                self.trigger_pub.publish(self._trigger_msg(stamp))
                self.trigger_sent = True
                self.trigger_publish_count += 1
                self.last_trigger_elapsed_s = elapsed_s
                rospy.logwarn("RACER_D2_TRIGGER_SENT count=%d", self.trigger_publish_count)

            if self.trigger_sent and outputs_ready:
                break
            rate.sleep()

        return self._write_summary()

    def _write_summary(self) -> int:
        per_uav = {}
        for uav in self.uavs:
            bspline_counter = self.bspline_counts[uav.name]
            pos_cmd_counter = self.pos_cmd_counts[uav.name]
            per_uav[uav.name] = {
                "drone_id": uav.drone_id,
                "input_topics": {
                    "odom": f"/{uav.name}/mosim/racer_d2/odom",
                    "sensor_pose": f"/{uav.name}/mosim/racer_d2/sensor_pose",
                    "cloud": f"/{uav.name}/mosim/racer_d2/cloud",
                },
                "input_publish_counts": self.input_counts[uav.name],
                "cloud_points_per_frame": len(self.cloud_points[uav.name]),
                "bspline": vars(bspline_counter),
                "pos_cmd": vars(pos_cmd_counter),
                "occupancy": {key: vars(counter) for key, counter in self.occupancy_counts[uav.name].items()},
            }

        shared = {topic: vars(counter) for topic, counter in self.shared_counts.items()}
        published_topics = self._published_topic_names()
        forbidden_topics = [
            topic
            for topic in published_topics
            if topic.startswith("/mavros/")
            or topic == "/mavros"
            or topic.startswith("/fmu/")
            or "setpoint_raw" in topic
            or "setpoint_position" in topic
            or "actuator_control" in topic
        ]
        per_uav_outputs_ok = {
            u.name: (self.bspline_counts[u.name].count > 0 or self.pos_cmd_counts[u.name].count > 0)
            for u in self.uavs
        }
        input_ok = {
            u.name: all(v > 0 for v in self.input_counts[u.name].values())
            for u in self.uavs
        }
        shared_core_ok = (
            self.shared_counts["/swarm_expl/drone_state"].count > 0
            and self.shared_counts["/planning/swarm_traj"].count > 0
            and self.shared_counts["/multi_map_manager/chunk_stamps"].count > 0
        )
        success = (
            all(input_ok.values())
            and self.trigger_sent
            and all(per_uav_outputs_ok.values())
            and shared_core_ok
            and not forbidden_topics
        )
        summary = {
            "schema": "mosim.sunray_ros1.racer_d2_adapter_dry_run.v1",
            "status": "passed" if success else "failed",
            "claim": "RACER-D2 adapter dry-run only; no Gazebo/PX4/MAVROS/RViz or exploration-success claim",
            "duration_s_requested": self.args.duration_s,
            "duration_s_wall": time.time() - self.start_wall,
            "trigger_sent": self.trigger_sent,
            "trigger_publish_count": self.trigger_publish_count,
            "input_ok": input_ok,
            "per_uav_outputs_ok": per_uav_outputs_ok,
            "shared_core_ok": shared_core_ok,
            "forbidden_topics": forbidden_topics,
            "per_uav": per_uav,
            "shared_topics": shared,
            "published_topic_sample": published_topics[:300],
        }
        os.makedirs(os.path.dirname(os.path.abspath(self.args.summary_file)), exist_ok=True)
        with open(self.args.summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
            f.write("\n")
        print("RACER_D2_STIMULUS_SUMMARY=%s" % self.args.summary_file)
        print("RACER_D2_STIMULUS_STATUS=%s" % summary["status"])
        return 0 if success else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=75.0)
    parser.add_argument("--trigger-after-s", type=float, default=3.0)
    parser.add_argument("--trigger-repeat-interval-s", type=float, default=0.5)
    parser.add_argument("--publish-hz", type=float, default=10.0)
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--trigger-x", type=float, default=2.0)
    parser.add_argument("--trigger-y", type=float, default=0.0)
    parser.add_argument("--trigger-z", type=float, default=1.0)
    parser.add_argument("--min-z", type=float, default=0.45)
    parser.add_argument("--max-z", type=float, default=1.55)
    parser.add_argument("--free-shell-radius-m", type=float, default=4.0)
    parser.add_argument("--shell-yaw-step-deg", type=int, default=4)
    parser.add_argument("--shell-pitch-step-deg", type=int, default=5)
    parser.add_argument("--obstacle-radius-m", type=float, default=0.22)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("racer_d2_synthetic_stimulus", anonymous=False)
    return RacerD2Stimulus(args).run()


if __name__ == "__main__":
    sys.exit(main())
