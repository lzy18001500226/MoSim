#!/usr/bin/env python3
"""Synthetic MoSim-like ROS1 stimulus for Swarm-Formation SF-D2.

This helper publishes per-drone odometry and point-cloud inputs for the local
Swarm-Formation adapter dry-run, sends a central formation goal, relays
planner-broadcast trajectories without the UDP bridge, and records planner
outputs. It is not a Gazebo/PX4/MAVROS/RViz proof.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rospy.msg import AnyMsg
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool

try:
    from quadrotor_msgs.msg import PositionCommand
    from traj_utils.msg import PolyTraj
except ImportError as exc:  # pragma: no cover - only exercised inside ROS env
    sys.stderr.write("missing_swarm_formation_messages: %s\n" % exc)
    raise


Point = Tuple[float, float, float]


@dataclass(frozen=True)
class DroneConfig:
    uav_name: str
    drone_name: str
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


class SwarmFormationD2Stimulus:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.start_wall = time.time()
        self.start_ros = rospy.Time.now()
        self.goal_sent = False
        self.goal_publish_count = 0
        self.last_goal_elapsed_s = -1.0
        self.broadcast_relay_count = 0
        self.broadcast_relay_time_adjust_count = 0
        self.broadcast_cache: Dict[int, PolyTraj] = {}

        # MoSim user-facing names are uav1/uav2/uav3. Upstream Swarm-Formation
        # formation offsets are zero-based, so SF-D2 keeps drone_0/1/2.
        self.drones = [
            DroneConfig("uav1", "drone_0", 0, -1.2, 0.0, 1.0),
            DroneConfig("uav2", "drone_1", 1, -1.2, -0.8, 1.0),
            DroneConfig("uav3", "drone_2", 2, -1.2, -1.6, 1.0),
        ]

        self.odom_pubs = {}
        self.cloud_pubs = {}
        self.cloud_points = {}
        self.input_counts = {d.drone_name: {"odom": 0, "cloud": 0} for d in self.drones}
        for drone in self.drones:
            self.odom_pubs[drone.drone_name] = rospy.Publisher(
                f"/{drone.drone_name}_visual_slam/odom", Odometry, queue_size=10
            )
            self.cloud_pubs[drone.drone_name] = rospy.Publisher(
                f"/{drone.drone_name}_pcl_render_node/cloud", PointCloud2, queue_size=10
            )
            self.cloud_points[drone.drone_name] = self._build_cloud_points(drone)

        self.goal_pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=1, latch=True)
        self.broadcast_relay_pub = rospy.Publisher("/broadcast_traj_to_planner", PolyTraj, queue_size=100)

        self.trajectory_counts: Dict[str, Counter] = {}
        self.pos_cmd_counts: Dict[str, Counter] = {}
        self.start_counts: Dict[str, Counter] = {}
        self.finish_counts: Dict[str, Counter] = {}
        self.map_counts: Dict[str, Dict[str, Counter]] = {}
        for drone in self.drones:
            traj_topic = f"/{drone.drone_name}_planning/trajectory"
            pos_topic = f"/{drone.drone_name}_planning/pos_cmd"
            start_topic = f"/{drone.drone_name}_planning/start"
            finish_topic = f"/{drone.drone_name}_planning/finish"
            self.trajectory_counts[drone.drone_name] = Counter(traj_topic)
            self.pos_cmd_counts[drone.drone_name] = Counter(pos_topic)
            self.start_counts[drone.drone_name] = Counter(start_topic)
            self.finish_counts[drone.drone_name] = Counter(finish_topic)
            rospy.Subscriber(traj_topic, PolyTraj, self._make_poly_traj_cb(drone.drone_name), queue_size=50)
            rospy.Subscriber(pos_topic, PositionCommand, self._make_pos_cmd_cb(drone.drone_name), queue_size=100)
            rospy.Subscriber(start_topic, Bool, self._make_bool_counter_cb(self.start_counts[drone.drone_name]), queue_size=10)
            rospy.Subscriber(
                finish_topic, Bool, self._make_bool_counter_cb(self.finish_counts[drone.drone_name]), queue_size=10
            )

            self.map_counts[drone.drone_name] = {}
            for suffix in ("grid_map/occupancy", "grid_map/occupancy_inflate", "grid_map/unknown"):
                topic = f"/{drone.drone_name}_ego_planner_node/{suffix}"
                counter = Counter(topic)
                self.map_counts[drone.drone_name][suffix] = counter
                rospy.Subscriber(topic, PointCloud2, self._make_cloud_counter_cb(counter), queue_size=10)

        self.broadcast_from_counter = Counter("/broadcast_traj_from_planner")
        self.broadcast_to_counter = Counter("/broadcast_traj_to_planner")
        rospy.Subscriber("/broadcast_traj_from_planner", PolyTraj, self._broadcast_from_cb, queue_size=100)
        rospy.Subscriber(
            "/broadcast_traj_to_planner",
            PolyTraj,
            self._make_poly_counter_cb(self.broadcast_to_counter),
            queue_size=100,
        )

        self.extra_topic_counts: Dict[str, Counter] = {}
        for topic in ("/move_base_simple/goal",):
            counter = Counter(topic)
            self.extra_topic_counts[topic] = counter
            rospy.Subscriber(topic, AnyMsg, self._make_any_counter_cb(counter), queue_size=10)

    def _elapsed_s(self) -> float:
        return max(0.0, (rospy.Time.now() - self.start_ros).to_sec())

    def _build_cloud_points(self, drone: DroneConfig) -> List[Point]:
        points: List[Point] = []

        # Sparse non-blocking columns. Do not publish a 360-degree max-range
        # shell here: the upstream grid map treats cloud endpoints as occupied,
        # so a synthetic shell becomes a closed obstacle wall around the UAV.
        for ox, oy in ((0.8, 1.9), (1.9, -2.9), (3.0, 1.7)):
            z_steps = range(int(self.args.min_z * 20), int(self.args.max_z * 20) + 1)
            for z_i in z_steps:
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

    def _odom_msg(self, drone: DroneConfig, stamp: rospy.Time) -> Odometry:
        msg = Odometry()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.child_frame_id = f"{drone.drone_name}/base_link"
        msg.pose.pose.position.x = drone.x
        msg.pose.pose.position.y = drone.y
        msg.pose.pose.position.z = drone.z
        msg.pose.pose.orientation.w = 1.0
        return msg

    def _cloud_msg(self, drone: DroneConfig, stamp: rospy.Time) -> PointCloud2:
        header = self._odom_msg(drone, stamp).header
        return point_cloud2.create_cloud_xyz32(header, self.cloud_points[drone.drone_name])

    def _goal_msg(self, stamp: rospy.Time) -> PoseStamped:
        msg = PoseStamped()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.pose.position.x = self.args.goal_x
        msg.pose.position.y = self.args.goal_y
        msg.pose.position.z = self.args.goal_z
        msg.pose.orientation.w = 1.0
        return msg

    def _broadcast_from_cb(self, msg: PolyTraj) -> None:
        self.broadcast_from_counter.observe(self._poly_traj_summary(msg))
        self.broadcast_cache[int(msg.drone_id)] = self._clone_poly_traj(msg)
        self._relay_poly_traj(msg)

    def _clone_poly_traj(self, msg: PolyTraj) -> PolyTraj:
        relayed = PolyTraj()
        relayed.drone_id = msg.drone_id
        relayed.traj_id = msg.traj_id
        relayed.start_time = msg.start_time
        relayed.order = msg.order
        relayed.coef_x = list(msg.coef_x)
        relayed.coef_y = list(msg.coef_y)
        relayed.coef_z = list(msg.coef_z)
        relayed.duration = list(msg.duration)
        return relayed

    def _relay_poly_traj(self, msg: PolyTraj) -> None:
        relayed = self._clone_poly_traj(msg)
        if self.args.relay_retime:
            relayed.start_time = rospy.Time.now() + rospy.Duration(self.args.relay_retime_future_s)
            self.broadcast_relay_time_adjust_count += 1
        self.broadcast_relay_pub.publish(relayed)
        self.broadcast_relay_count += 1

    def _relay_cached_broadcasts(self) -> None:
        if not self.args.relay_cached_broadcasts:
            return
        for msg in list(self.broadcast_cache.values()):
            self._relay_poly_traj(msg)

    def _make_poly_traj_cb(self, drone_name: str):
        def cb(msg: PolyTraj) -> None:
            self.trajectory_counts[drone_name].observe(self._poly_traj_summary(msg))

        return cb

    def _make_poly_counter_cb(self, counter: Counter):
        def cb(msg: PolyTraj) -> None:
            counter.observe(self._poly_traj_summary(msg))

        return cb

    def _make_pos_cmd_cb(self, drone_name: str):
        def cb(msg: PositionCommand) -> None:
            self.pos_cmd_counts[drone_name].observe(
                {
                    "trajectory_id": int(msg.trajectory_id),
                    "trajectory_flag": int(msg.trajectory_flag),
                    "position": [msg.position.x, msg.position.y, msg.position.z],
                    "velocity": [msg.velocity.x, msg.velocity.y, msg.velocity.z],
                    "acceleration": [msg.acceleration.x, msg.acceleration.y, msg.acceleration.z],
                    "yaw": msg.yaw,
                }
            )

        return cb

    def _make_bool_counter_cb(self, counter: Counter):
        def cb(msg: Bool) -> None:
            counter.observe({"data": bool(msg.data)})

        return cb

    def _make_cloud_counter_cb(self, counter: Counter):
        def cb(msg: PointCloud2) -> None:
            counter.observe({"width": int(msg.width), "height": int(msg.height), "frame_id": msg.header.frame_id})

        return cb

    def _make_any_counter_cb(self, counter: Counter):
        def cb(_msg: AnyMsg) -> None:
            counter.observe()

        return cb

    def _poly_traj_summary(self, msg: PolyTraj) -> dict:
        return {
            "drone_id": int(msg.drone_id),
            "traj_id": int(msg.traj_id),
            "order": int(msg.order),
            "duration_count": len(msg.duration),
            "duration_sum_s": float(sum(msg.duration)) if msg.duration else 0.0,
            "coef_x_count": len(msg.coef_x),
            "coef_y_count": len(msg.coef_y),
            "coef_z_count": len(msg.coef_z),
            "start_time_s": msg.start_time.to_sec(),
        }

    def _published_topic_names(self) -> List[str]:
        try:
            return sorted(name for name, _type in rospy.get_published_topics(namespace="/"))
        except Exception:
            return []

    def _publish_inputs(self, stamp: rospy.Time) -> None:
        for drone in self.drones:
            self.odom_pubs[drone.drone_name].publish(self._odom_msg(drone, stamp))
            self.cloud_pubs[drone.drone_name].publish(self._cloud_msg(drone, stamp))
            self.input_counts[drone.drone_name]["odom"] += 1
            self.input_counts[drone.drone_name]["cloud"] += 1

    def _outputs_ready(self) -> bool:
        return all(
            self.trajectory_counts[d.drone_name].count > 0 or self.pos_cmd_counts[d.drone_name].count > 0
            for d in self.drones
        )

    def run(self) -> int:
        rate = rospy.Rate(self.args.publish_hz)
        deadline = rospy.Time.now() + rospy.Duration(self.args.duration_s)
        while not rospy.is_shutdown() and rospy.Time.now() < deadline:
            stamp = rospy.Time.now()
            self._publish_inputs(stamp)
            self._relay_cached_broadcasts()

            elapsed_s = self._elapsed_s()
            if (
                elapsed_s >= self.args.goal_after_s
                and not self._outputs_ready()
                and self.goal_publish_count < self.args.max_goal_publishes
                and (
                    not self.goal_sent
                    or elapsed_s - self.last_goal_elapsed_s >= self.args.goal_repeat_interval_s
                )
            ):
                self.goal_pub.publish(self._goal_msg(stamp))
                self.goal_sent = True
                self.goal_publish_count += 1
                self.last_goal_elapsed_s = elapsed_s
                rospy.logwarn("SWARM_FORMATION_D2_GOAL_SENT count=%d", self.goal_publish_count)

            if self.goal_sent and self._outputs_ready():
                break
            rate.sleep()

        return self._write_summary()

    def _write_summary(self) -> int:
        per_drone = {}
        for drone in self.drones:
            drone_key = drone.drone_name
            per_drone[drone_key] = {
                "uav_name": drone.uav_name,
                "drone_id": drone.drone_id,
                "mapping": f"{drone.uav_name}->{drone.drone_name}",
                "input_topics": {
                    "odom": f"/{drone.drone_name}_visual_slam/odom",
                    "cloud": f"/{drone.drone_name}_pcl_render_node/cloud",
                },
                "input_publish_counts": self.input_counts[drone_key],
                "cloud_points_per_frame": len(self.cloud_points[drone_key]),
                "trajectory": vars(self.trajectory_counts[drone_key]),
                "pos_cmd": vars(self.pos_cmd_counts[drone_key]),
                "start": vars(self.start_counts[drone_key]),
                "finish": vars(self.finish_counts[drone_key]),
                "map_topics": {key: vars(counter) for key, counter in self.map_counts[drone_key].items()},
            }

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

        input_ok = {d.drone_name: all(v > 0 for v in self.input_counts[d.drone_name].values()) for d in self.drones}
        per_drone_outputs_ok = {
            d.drone_name: (
                self.trajectory_counts[d.drone_name].count > 0
                or self.pos_cmd_counts[d.drone_name].count > 0
            )
            for d in self.drones
        }
        broadcast_ok = self.broadcast_from_counter.count > 0 and self.broadcast_relay_count > 0
        success = (
            all(input_ok.values())
            and self.goal_sent
            and all(per_drone_outputs_ok.values())
            and broadcast_ok
            and not forbidden_topics
        )

        summary = {
            "schema": "mosim.sunray_ros1.swarm_formation_d2_adapter_dry_run.v1",
            "status": "passed" if success else "failed",
            "claim": "Swarm-Formation SF-D2 adapter dry-run only; no Gazebo/PX4/MAVROS/RViz formation-flight claim",
            "duration_s_requested": self.args.duration_s,
            "duration_s_wall": time.time() - self.start_wall,
            "uav_to_upstream_mapping": {d.uav_name: d.drone_name for d in self.drones},
            "upstream_drone_ids": {d.drone_name: d.drone_id for d in self.drones},
            "goal_sent": self.goal_sent,
            "goal_publish_count": self.goal_publish_count,
            "goal": {"x": self.args.goal_x, "y": self.args.goal_y, "z": self.args.goal_z},
            "input_ok": input_ok,
            "per_drone_outputs_ok": per_drone_outputs_ok,
            "broadcast_ok": broadcast_ok,
            "broadcast": {
                "from_planner": vars(self.broadcast_from_counter),
                "to_planner": vars(self.broadcast_to_counter),
                "relay_count": self.broadcast_relay_count,
                "relay_time_adjust_count": self.broadcast_relay_time_adjust_count,
                "relay_retime": self.args.relay_retime,
                "relay_retime_future_s": self.args.relay_retime_future_s,
                "relay_cached_broadcasts": self.args.relay_cached_broadcasts,
                "relay_cache_size": len(self.broadcast_cache),
            },
            "forbidden_topics": forbidden_topics,
            "per_drone": per_drone,
            "extra_topic_counts": {topic: vars(counter) for topic, counter in self.extra_topic_counts.items()},
            "published_topic_sample": published_topics[:350],
        }

        os.makedirs(os.path.dirname(os.path.abspath(self.args.summary_file)), exist_ok=True)
        with open(self.args.summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
            f.write("\n")
        print("SWARM_FORMATION_D2_STIMULUS_SUMMARY=%s" % self.args.summary_file)
        print("SWARM_FORMATION_D2_STIMULUS_STATUS=%s" % summary["status"])
        return 0 if success else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=90.0)
    parser.add_argument("--goal-after-s", type=float, default=3.0)
    parser.add_argument("--goal-repeat-interval-s", type=float, default=0.75)
    parser.add_argument("--max-goal-publishes", type=int, default=1)
    parser.add_argument("--publish-hz", type=float, default=10.0)
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--goal-x", type=float, default=2.2)
    parser.add_argument("--goal-y", type=float, default=0.0)
    parser.add_argument("--goal-z", type=float, default=1.0)
    parser.add_argument("--min-z", type=float, default=0.25)
    parser.add_argument("--max-z", type=float, default=1.8)
    parser.add_argument("--obstacle-radius-m", type=float, default=0.20)
    parser.add_argument("--relay-retime", dest="relay_retime", action="store_true", default=True)
    parser.add_argument("--no-relay-retime", dest="relay_retime", action="store_false")
    parser.add_argument("--relay-retime-future-s", type=float, default=0.05)
    parser.add_argument("--relay-cached-broadcasts", dest="relay_cached_broadcasts", action="store_true", default=True)
    parser.add_argument("--no-relay-cached-broadcasts", dest="relay_cached_broadcasts", action="store_false")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("swarm_formation_d2_synthetic_stimulus", anonymous=False)
    return SwarmFormationD2Stimulus(args).run()


if __name__ == "__main__":
    sys.exit(main())
