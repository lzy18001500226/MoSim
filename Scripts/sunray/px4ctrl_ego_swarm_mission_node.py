#!/usr/bin/env python3
"""Goal5 multi-UAV EGO-style planner -> original px4ctrl -> PX4/Gazebo gate."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path

import rospy
from rospy.msg import AnyMsg
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import AttitudeTarget, State
from nav_msgs.msg import Odometry, Path as RosPath
from quadrotor_msgs.msg import PositionCommand, Px4ctrlDebug, TakeoffLand
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool, Header

from trajectory_dynamics import inter_uav_braking_guard


def wall_sleep(duration_s: float) -> None:
    """Sleep on wall time so mission deadlines are not stretched by /use_sim_time."""
    deadline = time.monotonic() + max(0.0, duration_s)
    while not rospy.is_shutdown():
        remaining = deadline - time.monotonic()
        if remaining <= 0.0:
            return
        time.sleep(min(remaining, 0.05))
    raise rospy.exceptions.ROSInterruptException("ROS shutdown request")


class WallRate:
    def __init__(self, hz: float) -> None:
        self.period_s = 1.0 / max(1.0, float(hz))

    def sleep(self) -> None:
        wall_sleep(self.period_s)


try:
    from traj_utils.msg import Bspline as TrajUtilsBspline
except ImportError:  # Diff-only overlays may not define Bspline.
    TrajUtilsBspline = None

try:
    from bspline.msg import Bspline as RacerBspline
except ImportError:  # RACER/FUEL overlays may not define this in EGO/Diff runs.
    RacerBspline = None

try:
    from traj_utils.msg import PolyTraj
except ImportError:  # EGO v1 overlays may not define PolyTraj.
    PolyTraj = None


@dataclass
class UavRuntime:
    uid: int
    drone_id: int
    target: tuple[float, float, float]
    start_xy: tuple[float, float]
    goal_topic: str
    takeoff_land_pub: rospy.Publisher
    hover_cmd_pub: rospy.Publisher
    goal_pub: rospy.Publisher
    cmd_adapter_enable_pub: rospy.Publisher
    truth_path_pub: rospy.Publisher
    cmd_path_pub: rospy.Publisher
    raw_cmd_topic: str
    adapted_cmd_topic: str
    cmd_safety_diagnostics_path: Path | None
    home_odom_xy: tuple[float, float] | None = None
    home_odom_z: float | None = None
    home_truth_z: float | None = None
    state: State | None = None
    truth: dict | None = None
    odom: dict | None = None
    raw_position_cmd: dict | None = None
    position_cmd: dict | None = None
    bspline_count: int = 0
    polytraj_count: int = 0
    raw_lidar_count: int = 0
    raw_lidar_points: int = 0
    world_cloud_count: int = 0
    world_cloud_points: int = 0
    occupancy_count: int = 0
    occupancy_points: int = 0
    frontier_count: int = 0
    trajectory_vis_count: int = 0
    swarm_traj_count: int = 0
    target_attitude_count: int = 0
    debug_count: int = 0
    first_bspline_t: float | None = None
    first_polytraj_t: float | None = None
    first_planner_position_cmd_t: float | None = None
    reached_t: float | None = None
    hover_cmd_publish_count: int = 0
    goal_publish_count: int = 0
    last_pre_takeoff_gate: dict | None = None
    pre_takeoff_gate_history: list[dict] = field(default_factory=list)
    last_pre_planner_gate: dict | None = None
    pre_planner_trigger_snapshot: dict | None = None
    pre_planner_gate_history: list[dict] = field(default_factory=list)
    target_hold_metrics: dict | None = None
    warnings: list[str] = field(default_factory=list)
    truth_rows: list[dict] = field(default_factory=list)
    odom_rows: list[dict] = field(default_factory=list)
    raw_cmd_rows: list[dict] = field(default_factory=list)
    cmd_rows: list[dict] = field(default_factory=list)
    bspline_rows: list[dict] = field(default_factory=list)
    att_rows: list[dict] = field(default_factory=list)
    debug_rows: list[dict] = field(default_factory=list)
    state_rows: list[dict] = field(default_factory=list)
    truth_path: RosPath = field(default_factory=lambda: RosPath(header=Header(frame_id="world")))
    cmd_path: RosPath = field(default_factory=lambda: RosPath(header=Header(frame_id="world")))
    last_record_t: dict[str, float] = field(default_factory=lambda: {"truth": -1e9, "odom": -1e9, "raw_cmd": -1e9, "cmd": -1e9, "att": -1e9, "debug": -1e9})
    takeoff_cmd_publish_count: int = 0
    land_cmd_publish_count: int = 0


class EgoSwarmMission:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.start_wall = time.time()
        self.exploration_started_t: float | None = None
        self.exploration_ended_t: float | None = None
        self.phase = "init"
        self.uavs: dict[int, UavRuntime] = {}
        self.formation_center_goal_publish_count = 0
        self.min_inter_uav_distance = float("inf")
        self.min_inter_uav_pair: tuple[int, int] | None = None
        self.separation_rows: list[dict] = []
        self.last_sep_record_t = -1e9
        self.inter_uav_emergency_events: list[dict] = []
        self.landing_summary: dict | None = None
        self.command_quiesce_summaries: list[dict] = []
        self.takeoff_timing_summary: dict | None = None
        self.target_chains: dict[int, list[tuple[float, float, float]]] = {}
        self.target_chain_report: dict | None = None
        self.trigger_pub = rospy.Publisher("/traj_start_trigger", PoseStamped, queue_size=3)
        self.target_path_pub = rospy.Publisher("/mosim/goal5/target_path", RosPath, queue_size=1, latch=True)
        self.pre_takeoff_settle_summary: dict | None = None

        for uid in range(1, args.uav_num + 1):
            target = self.target_for(uid)
            start_xy = self.start_xy_for(uid)
            goal_topic = args.goal_topic_template.format(uid=uid, drone_id=uid - 1)
            raw_cmd_topic = args.raw_position_cmd_topic_template.format(uid=uid, drone_id=uid - 1)
            adapted_cmd_topic = args.adapted_position_cmd_topic_template.format(uid=uid, drone_id=uid - 1)
            cmd_safety_diagnostics_path = None
            if args.cmd_safety_diagnostics_template:
                cmd_safety_diagnostics_path = Path(args.cmd_safety_diagnostics_template.format(uid=uid, drone_id=uid - 1))
            uav = UavRuntime(
                uid=uid,
                drone_id=uid - 1,
                target=target,
                start_xy=start_xy,
                goal_topic=goal_topic,
                takeoff_land_pub=rospy.Publisher(f"/uav{uid}/px4ctrl/takeoff_land", TakeoffLand, queue_size=3, latch=True),
                hover_cmd_pub=rospy.Publisher(adapted_cmd_topic, PositionCommand, queue_size=10),
                goal_pub=rospy.Publisher(goal_topic, PoseStamped, queue_size=3, latch=True),
                cmd_adapter_enable_pub=rospy.Publisher(args.cmd_adapter_enable_topic_template.format(uid=uid, drone_id=uid - 1), Bool, queue_size=3, latch=True),
                truth_path_pub=rospy.Publisher(f"/mosim/goal5/uav{uid}/truth_path", RosPath, queue_size=1, latch=True),
                cmd_path_pub=rospy.Publisher(f"/mosim/goal5/uav{uid}/position_cmd_path", RosPath, queue_size=1, latch=True),
                raw_cmd_topic=raw_cmd_topic,
                adapted_cmd_topic=adapted_cmd_topic,
                cmd_safety_diagnostics_path=cmd_safety_diagnostics_path,
            )
            uav.truth_path.header.frame_id = args.path_frame
            uav.cmd_path.header.frame_id = args.path_frame
            self.uavs[uid] = uav

            rospy.Subscriber(f"/uav{uid}/mavros/state", State, lambda msg, uid=uid: self.on_state(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/mavros/local_position/odom", Odometry, lambda msg, uid=uid: self.on_odom(uid, msg), queue_size=100)
            rospy.Subscriber(raw_cmd_topic, PositionCommand, lambda msg, uid=uid: self.on_raw_position_cmd(uid, msg), queue_size=200)
            rospy.Subscriber(adapted_cmd_topic, PositionCommand, lambda msg, uid=uid: self.on_position_cmd(uid, msg), queue_size=200)
            bspline_topic = args.bspline_topic_template.format(uid=uid, drone_id=uid - 1)
            polytraj_topic = args.polytraj_topic_template.format(uid=uid, drone_id=uid - 1)
            bspline_msg_cls = self.select_bspline_msg_class()
            if bspline_msg_cls is not None and bspline_topic:
                rospy.Subscriber(bspline_topic, bspline_msg_cls, lambda msg, uid=uid: self.on_bspline(uid, msg), queue_size=20)
            if PolyTraj is not None and polytraj_topic:
                rospy.Subscriber(polytraj_topic, PolyTraj, lambda msg, uid=uid: self.on_polytraj(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/livox/lidar", PointCloud2, lambda msg, uid=uid: self.on_raw_lidar(uid, msg), queue_size=20)
            world_cloud_topic = args.world_cloud_topic_template.format(uid=uid, drone_id=uid - 1)
            rospy.Subscriber(world_cloud_topic, PointCloud2, lambda msg, uid=uid: self.on_world_cloud(uid, msg), queue_size=20)
            occupancy_topic = args.occupancy_topic_template.format(uid=uid, drone_id=uid - 1)
            if occupancy_topic:
                rospy.Subscriber(occupancy_topic, PointCloud2, lambda msg, uid=uid: self.on_occupancy(uid, msg), queue_size=20)
            frontier_topic = args.frontier_topic_template.format(uid=uid, drone_id=uid - 1)
            if frontier_topic:
                rospy.Subscriber(frontier_topic, AnyMsg, lambda msg, uid=uid: self.on_frontier(uid, msg), queue_size=20)
            trajectory_vis_topic = args.trajectory_vis_topic_template.format(uid=uid, drone_id=uid - 1)
            if trajectory_vis_topic:
                rospy.Subscriber(trajectory_vis_topic, AnyMsg, lambda msg, uid=uid: self.on_trajectory_vis(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/mavros/setpoint_raw/target_attitude", AttitudeTarget, lambda msg, uid=uid: self.on_att_target(uid, msg), queue_size=100)
            rospy.Subscriber(f"/uav{uid}/debugPx4ctrl", Px4ctrlDebug, lambda msg, uid=uid: self.on_debug(uid, msg), queue_size=100)

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=30)
        if args.swarm_traj_topic:
            rospy.Subscriber(args.swarm_traj_topic, AnyMsg, self.on_swarm_traj, queue_size=100)
        self.target_chains = self.load_target_chains()

    def select_bspline_msg_class(self):
        if self.args.bspline_msg_package == "traj_utils":
            return TrajUtilsBspline
        if self.args.bspline_msg_package == "bspline":
            return RacerBspline
        return TrajUtilsBspline or RacerBspline

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        return float(stamp) if stamp > 0 else time.time() - self.start_wall

    def wall_elapsed(self) -> float:
        return time.time() - self.start_wall

    def should_record(self, uav: UavRuntime, key: str, t: float, hz: float) -> bool:
        if hz <= 0:
            return True
        if t - uav.last_record_t[key] < 1.0 / hz:
            return False
        uav.last_record_t[key] = t
        return True

    def target_for(self, uid: int) -> tuple[float, float, float]:
        return tuple(getattr(self.args, f"target{uid}_{axis}") for axis in ("x", "y", "z"))

    def start_xy_for(self, uid: int) -> tuple[float, float]:
        return (getattr(self.args, f"start{uid}_x"), getattr(self.args, f"start{uid}_y"))

    def load_target_chains(self) -> dict[int, list[tuple[float, float, float]]]:
        chains: dict[int, list[tuple[float, float, float]]] = {}
        for uid in range(1, self.args.uav_num + 1):
            path_text = str(getattr(self.args, f"target{uid}_chain_file", "") or "").strip()
            if not path_text:
                continue
            path = Path(path_text)
            packet = json.loads(path.read_text(encoding="utf-8"))
            raw_waypoints = packet.get("waypoints")
            if not isinstance(raw_waypoints, list):
                raise ValueError(f"target chain file has no waypoints list: {path}")
            chain: list[tuple[float, float, float]] = []
            for item in raw_waypoints:
                if not isinstance(item, list) or len(item) < 3:
                    raise ValueError(f"invalid waypoint in target chain file {path}: {item!r}")
                chain.append((float(item[0]), float(item[1]), float(item[2])))
            if self.args.target_chain_max_goals > 0:
                chain = chain[: self.args.target_chain_max_goals]
            if chain:
                chains[uid] = chain
        if chains and len(chains) != self.args.uav_num:
            missing = [uid for uid in range(1, self.args.uav_num + 1) if uid not in chains]
            raise ValueError(f"target-chain mode requires every UAV to have a chain file; missing uav ids: {missing}")
        return chains

    @staticmethod
    def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    @classmethod
    def rpy_from_quat(cls, x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        return roll, pitch, cls.yaw_from_quat(x, y, z, w)

    def on_state(self, uid: int, msg: State) -> None:
        uav = self.uavs[uid]
        uav.state = msg
        uav.state_rows.append(
            {
                "t": self.now(),
                "wall_elapsed_s": self.wall_elapsed(),
                "phase": self.phase,
                "connected": bool(msg.connected),
                "armed": bool(msg.armed),
                "guided": bool(msg.guided),
                "manual_input": bool(msg.manual_input),
                "mode": str(msg.mode),
                "system_status": int(msg.system_status),
            }
        )
        if len(uav.state_rows) > 5000:
            uav.state_rows = uav.state_rows[-5000:]

    def on_model_states(self, msg: ModelStates) -> None:
        names = list(msg.name)
        t = self.now()
        for uid, uav in self.uavs.items():
            model_name = f"uav{uid}"
            try:
                idx = names.index(model_name)
            except ValueError:
                continue
            pose = msg.pose[idx]
            twist = msg.twist[idx]
            q = pose.orientation
            roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
            row = {
                "t": t,
                "phase": self.phase,
                "x": float(pose.position.x),
                "y": float(pose.position.y),
                "z": float(pose.position.z),
                "vx": float(twist.linear.x),
                "vy": float(twist.linear.y),
                "vz": float(twist.linear.z),
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw,
            }
            uav.truth = row
            if self.should_record(uav, "truth", t, self.args.record_hz):
                uav.truth_rows.append(row)
                self.append_path(uav.truth_path, row["x"], row["y"], row["z"], t)
        self.update_separation(t)

    def on_odom(self, uid: int, msg: Odometry) -> None:
        uav = self.uavs[uid]
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        t = self.now()
        row = {
            "t": t,
            "phase": self.phase,
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "vx": float(v.x),
            "vy": float(v.y),
            "vz": float(v.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        uav.odom = row
        if self.should_record(uav, "odom", t, self.args.record_hz):
            uav.odom_rows.append(row)

    def position_cmd_row(self, msg: PositionCommand) -> dict:
        t = self.now()
        return {
            "t": t,
            "phase": self.phase,
            "x": float(msg.position.x),
            "y": float(msg.position.y),
            "z": float(msg.position.z),
            "vx": float(msg.velocity.x),
            "vy": float(msg.velocity.y),
            "vz": float(msg.velocity.z),
            "ax": float(msg.acceleration.x),
            "ay": float(msg.acceleration.y),
            "az": float(msg.acceleration.z),
            "yaw": float(msg.yaw),
        }

    def on_raw_position_cmd(self, uid: int, msg: PositionCommand) -> None:
        uav = self.uavs[uid]
        row = self.position_cmd_row(msg)
        uav.raw_position_cmd = row
        if uav.first_planner_position_cmd_t is None:
            uav.first_planner_position_cmd_t = row["t"]
        if self.should_record(uav, "raw_cmd", row["t"], self.args.record_cmd_hz):
            uav.raw_cmd_rows.append(row)

    def on_position_cmd(self, uid: int, msg: PositionCommand) -> None:
        uav = self.uavs[uid]
        row = self.position_cmd_row(msg)
        uav.position_cmd = row
        if self.should_record(uav, "cmd", row["t"], self.args.record_cmd_hz):
            uav.cmd_rows.append(row)
            self.append_path(uav.cmd_path, row["x"], row["y"], row["z"], row["t"])

    def on_bspline(self, uid: int, msg) -> None:
        uav = self.uavs[uid]
        t = self.now()
        uav.bspline_count += 1
        if uav.first_bspline_t is None:
            uav.first_bspline_t = t
        uav.bspline_rows.append({
            "t": t,
            "planner_msg": "Bspline",
            "traj_id": int(msg.traj_id),
            "order": int(msg.order),
            "pos_pts": len(msg.pos_pts),
            "knots": len(msg.knots),
        })

    def on_polytraj(self, uid: int, msg) -> None:
        uav = self.uavs[uid]
        t = self.now()
        uav.polytraj_count += 1
        if uav.first_polytraj_t is None:
            uav.first_polytraj_t = t
        uav.bspline_rows.append({
            "t": t,
            "planner_msg": "PolyTraj",
            "traj_id": int(msg.traj_id),
            "order": int(msg.order),
            "pos_pts": 0,
            "knots": len(msg.duration),
        })

    def exploration_trajectory_freshness_summary(self, uav: UavRuntime) -> dict | None:
        if self.args.mission_completion_mode != "exploration":
            return None
        if self.exploration_started_t is None or self.exploration_ended_t is None:
            return None
        publish_times = sorted(
            float(row["t"])
            for row in uav.bspline_rows
            if self.exploration_started_t <= float(row["t"]) <= self.exploration_ended_t
        )
        boundaries = [self.exploration_started_t, *publish_times, self.exploration_ended_t]
        gaps = [boundaries[index + 1] - boundaries[index] for index in range(len(boundaries) - 1)]
        max_gap = max(gaps) if gaps else self.exploration_ended_t - self.exploration_started_t
        return {
            "time_basis": "ros_simulation_time",
            "threshold_s": self.args.exploration_max_trajectory_stale_s,
            "publish_count": len(publish_times),
            "first_publish_t": publish_times[0] if publish_times else None,
            "last_publish_t": publish_times[-1] if publish_times else None,
            "max_gap_s": max_gap,
            "terminal_stale_s": (
                self.exploration_ended_t - publish_times[-1]
                if publish_times
                else self.exploration_ended_t - self.exploration_started_t
            ),
            "passed": (
                self.args.exploration_max_trajectory_stale_s <= 0.0
                or bool(publish_times)
                and max_gap <= self.args.exploration_max_trajectory_stale_s
            ),
        }

    def exploration_team_trajectory_freshness_summary(self) -> dict | None:
        if self.args.mission_completion_mode != "exploration":
            return None
        if self.exploration_started_t is None or self.exploration_ended_t is None:
            return None
        publish_events = sorted(
            (float(row["t"]), uid)
            for uid, uav in self.uavs.items()
            for row in uav.bspline_rows
            if self.exploration_started_t <= float(row["t"]) <= self.exploration_ended_t
        )
        publish_times = [event[0] for event in publish_events]
        boundaries = [self.exploration_started_t, *publish_times, self.exploration_ended_t]
        gaps = [boundaries[index + 1] - boundaries[index] for index in range(len(boundaries) - 1)]
        max_gap = max(gaps) if gaps else self.exploration_ended_t - self.exploration_started_t
        return {
            "time_basis": "ros_simulation_time",
            "scope": "swarm_team",
            "threshold_s": self.args.exploration_max_trajectory_stale_s,
            "publish_count": len(publish_events),
            "publish_count_per_uav": {
                str(uid): sum(1 for _, event_uid in publish_events if event_uid == uid)
                for uid in self.uavs
            },
            "first_publish_t": publish_times[0] if publish_times else None,
            "last_publish_t": publish_times[-1] if publish_times else None,
            "max_gap_s": max_gap,
            "terminal_stale_s": (
                self.exploration_ended_t - publish_times[-1]
                if publish_times
                else self.exploration_ended_t - self.exploration_started_t
            ),
            "passed": (
                self.args.exploration_max_trajectory_stale_s <= 0.0
                or bool(publish_times)
                and max_gap <= self.args.exploration_max_trajectory_stale_s
            ),
            "semantics": (
                "RACER may intentionally hold one UAV while another explores. The hard freshness "
                "gate therefore uses the merged team trajectory stream; per-UAV freshness remains diagnostic."
            ),
        }

    def on_raw_lidar(self, uid: int, msg: PointCloud2) -> None:
        uav = self.uavs[uid]
        uav.raw_lidar_count += 1
        uav.raw_lidar_points = int(msg.width * msg.height)

    def on_world_cloud(self, uid: int, msg: PointCloud2) -> None:
        uav = self.uavs[uid]
        uav.world_cloud_count += 1
        uav.world_cloud_points = int(msg.width * msg.height)

    def on_occupancy(self, uid: int, msg: PointCloud2) -> None:
        uav = self.uavs[uid]
        uav.occupancy_count += 1
        uav.occupancy_points = int(msg.width * msg.height)

    def on_frontier(self, uid: int, msg: AnyMsg) -> None:
        self.uavs[uid].frontier_count += 1

    def on_trajectory_vis(self, uid: int, msg: AnyMsg) -> None:
        self.uavs[uid].trajectory_vis_count += 1

    def on_swarm_traj(self, msg: AnyMsg) -> None:
        for uav in self.uavs.values():
            uav.swarm_traj_count += 1

    def on_att_target(self, uid: int, msg: AttitudeTarget) -> None:
        uav = self.uavs[uid]
        uav.target_attitude_count += 1
        t = self.now()
        if not self.should_record(uav, "att", t, self.args.record_cmd_hz):
            return
        q = msg.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        uav.att_rows.append({"t": t, "phase": self.phase, "roll": roll, "pitch": pitch, "yaw": yaw, "thrust": float(msg.thrust)})

    def on_debug(self, uid: int, msg: Px4ctrlDebug) -> None:
        uav = self.uavs[uid]
        uav.debug_count += 1
        t = self.now()
        if not self.should_record(uav, "debug", t, self.args.record_cmd_hz):
            return
        uav.debug_rows.append({"t": t, "phase": self.phase, "des_thr": float(msg.des_thr), "des_a_x": float(msg.des_a_x), "des_a_y": float(msg.des_a_y), "des_a_z": float(msg.des_a_z)})

    def append_path(self, path: RosPath, x: float, y: float, z: float, t: float) -> None:
        ps = PoseStamped()
        ps.header.stamp = rospy.Time.from_sec(t)
        ps.header.frame_id = self.args.path_frame
        ps.pose.position.x = x
        ps.pose.position.y = y
        ps.pose.position.z = z
        ps.pose.orientation.w = 1.0
        path.header.stamp = ps.header.stamp
        path.header.frame_id = self.args.path_frame
        path.poses.append(ps)
        if self.args.max_path_points > 0 and len(path.poses) > self.args.max_path_points:
            path.poses = path.poses[-self.args.max_path_points :]

    def update_separation(self, t: float) -> None:
        ids = sorted(self.uavs)
        current_min = float("inf")
        current_pair = None
        for i, uid_a in enumerate(ids):
            truth_a = self.uavs[uid_a].truth
            if not truth_a:
                continue
            for uid_b in ids[i + 1 :]:
                truth_b = self.uavs[uid_b].truth
                if not truth_b:
                    continue
                dist = math.dist((truth_a["x"], truth_a["y"], truth_a["z"]), (truth_b["x"], truth_b["y"], truth_b["z"]))
                if dist < current_min:
                    current_min = dist
                    current_pair = (uid_a, uid_b)
                if dist < self.min_inter_uav_distance:
                    self.min_inter_uav_distance = dist
                    self.min_inter_uav_pair = (uid_a, uid_b)
        if current_pair and t - self.last_sep_record_t >= 1.0 / self.args.record_hz:
            self.separation_rows.append({"t": t, "phase": self.phase, "uav_a": current_pair[0], "uav_b": current_pair[1], "distance_m": current_min})
            self.last_sep_record_t = t

    @staticmethod
    def row_speed(row: dict) -> float:
        return math.sqrt(row["vx"] * row["vx"] + row["vy"] * row["vy"] + row["vz"] * row["vz"])

    @staticmethod
    def xy_distance(row: dict, xy: tuple[float, float]) -> float:
        return math.hypot(row["x"] - xy[0], row["y"] - xy[1])

    @staticmethod
    def pose_delta(a: dict | None, b: dict | None) -> dict | None:
        if not a or not b:
            return None
        dx = float(a["x"] - b["x"])
        dy = float(a["y"] - b["y"])
        dz = float(a["z"] - b["z"])
        return {
            "dx_m": dx,
            "dy_m": dy,
            "dz_m": dz,
            "dxy_m": math.hypot(dx, dy),
            "dxyz_m": math.sqrt(dx * dx + dy * dy + dz * dz),
        }

    def frame_alignment_summary(self, uav: UavRuntime) -> dict:
        home_delta = None
        if uav.home_odom_xy is not None and uav.truth_rows:
            first_truth = uav.truth_rows[0]
            dx = uav.home_odom_xy[0] - first_truth["x"]
            dy = uav.home_odom_xy[1] - first_truth["y"]
            dz = 0.0 if uav.home_odom_z is None else uav.home_odom_z - first_truth["z"]
            home_delta = {
                "odom_minus_truth_dx_m": dx,
                "odom_minus_truth_dy_m": dy,
                "odom_minus_truth_dz_m": dz,
                "odom_minus_truth_dxy_m": math.hypot(dx, dy),
                "odom_minus_truth_dxyz_m": math.sqrt(dx * dx + dy * dy + dz * dz),
            }
        return {
            "home_odom_xy": None if uav.home_odom_xy is None else {"x": uav.home_odom_xy[0], "y": uav.home_odom_xy[1]},
            "home_odom_z": uav.home_odom_z,
            "takeoff_hover_z": self.takeoff_hover_z(uav),
            "first_truth_xy": None
            if not uav.truth_rows
            else {"x": uav.truth_rows[0]["x"], "y": uav.truth_rows[0]["y"]},
            "first_truth_z": None if not uav.truth_rows else uav.truth_rows[0]["z"],
            "home_odom_minus_first_truth": home_delta,
            "final_odom_minus_truth": self.pose_delta(uav.odom, uav.truth),
            "target_frame_note": (
                "planner goals are world-frame review targets, while px4ctrl "
                "consumes MAVROS/PX4 local odometry. Multi-UAV success requires "
                "either PX4 local frame alignment through external position "
                "fusion or an explicit world-to-local target transform."
            ),
        }

    def target_state_snapshot(self, uav: UavRuntime, row: dict | None = None) -> dict | None:
        row = row or uav.odom
        if row is None:
            return None
        return {
            "t": row["t"],
            "phase": row.get("phase", self.phase),
            "x": row["x"],
            "y": row["y"],
            "z": row["z"],
            "vx": row["vx"],
            "vy": row["vy"],
            "vz": row["vz"],
            "roll": row["roll"],
            "pitch": row["pitch"],
            "yaw": row["yaw"],
            "error_xyz_m": math.dist((row["x"], row["y"], row["z"]), uav.target),
            "error_xy_m": math.dist((row["x"], row["y"]), uav.target[:2]),
            "error_z_m": row["z"] - uav.target[2],
            "speed_mps": self.row_speed(row),
            "abs_vz_mps": abs(row["vz"]),
            "abs_roll_pitch_deg": math.degrees(max(abs(row["roll"]), abs(row["pitch"]))),
        }

    @staticmethod
    def first_planner_trajectory_time(uav: UavRuntime) -> float | None:
        times = [t for t in (uav.first_bspline_t, uav.first_polytraj_t) if t is not None]
        return min(times) if times else None

    @staticmethod
    def first_planner_takeover_time(uav: UavRuntime) -> float | None:
        times = [
            t
            for t in (uav.first_bspline_t, uav.first_polytraj_t, uav.first_planner_position_cmd_t)
            if t is not None
        ]
        return min(times) if times else None

    def takeoff_hover_z(self, uav: UavRuntime) -> float:
        if uav.home_odom_z is None:
            return self.args.takeoff_height
        return uav.home_odom_z + self.args.takeoff_height

    def pre_planner_stability_snapshot(self, uav: UavRuntime) -> dict:
        now_t = self.now()
        home_xy = uav.home_odom_xy or uav.start_xy
        target_z = self.takeoff_hover_z(uav)
        reasons: list[str] = []
        snapshot: dict = {
            "t": now_t,
            "phase": self.phase,
            "required_stable_s": max(self.args.pre_ego_hover_s, self.args.pre_planner_stable_s),
            "thresholds": {
                "odom_timeout_s": self.args.pre_planner_odom_timeout_s,
                "max_xy_error_m": self.args.pre_planner_max_xy_error_m,
                "max_z_error_m": self.args.pre_planner_max_z_error_m,
                "max_speed_mps": self.args.pre_planner_max_speed_mps,
                "max_vz_mps": self.args.pre_planner_max_vz_mps,
                "max_roll_pitch_deg": self.args.pre_planner_max_roll_pitch_deg,
                "target_z_m": target_z,
                "target_z_semantics": "px4ctrl AUTO_TAKEOFF uses home_odom_z + takeoff_height.",
            },
        }
        if uav.odom is None:
            reasons.append("odom_missing")
        else:
            odom_age = now_t - uav.odom["t"]
            odom_xy_error = self.xy_distance(uav.odom, home_xy)
            odom_z_error = uav.odom["z"] - target_z
            odom_speed = self.row_speed(uav.odom)
            odom_abs_vz = abs(uav.odom["vz"])
            odom_abs_roll_pitch_deg = math.degrees(max(abs(uav.odom["roll"]), abs(uav.odom["pitch"])))
            snapshot["odom"] = {
                "age_s": odom_age,
                "x": uav.odom["x"],
                "y": uav.odom["y"],
                "z": uav.odom["z"],
                "xy_error_m": odom_xy_error,
                "target_z_m": target_z,
                "z_error_m": odom_z_error,
                "speed_mps": odom_speed,
                "abs_vz_mps": odom_abs_vz,
                "abs_roll_pitch_deg": odom_abs_roll_pitch_deg,
            }
            if odom_age > self.args.pre_planner_odom_timeout_s:
                reasons.append(f"odom_stale:{odom_age:.3f}")
            if odom_xy_error > self.args.pre_planner_max_xy_error_m:
                reasons.append(f"odom_xy_error:{odom_xy_error:.3f}")
            if abs(odom_z_error) > self.args.pre_planner_max_z_error_m:
                reasons.append(f"odom_z_error:{odom_z_error:.3f}")
            if odom_speed > self.args.pre_planner_max_speed_mps:
                reasons.append(f"odom_speed:{odom_speed:.3f}")
            if odom_abs_vz > self.args.pre_planner_max_vz_mps:
                reasons.append(f"odom_vz:{odom_abs_vz:.3f}")
            if odom_abs_roll_pitch_deg > self.args.pre_planner_max_roll_pitch_deg:
                reasons.append(f"odom_roll_pitch:{odom_abs_roll_pitch_deg:.3f}")
        snapshot["ok"] = not reasons
        snapshot["reasons"] = reasons
        uav.last_pre_planner_gate = snapshot
        uav.pre_planner_gate_history.append(snapshot)
        if len(uav.pre_planner_gate_history) > self.args.pre_planner_history_limit:
            uav.pre_planner_gate_history = uav.pre_planner_gate_history[-self.args.pre_planner_history_limit :]
        return snapshot

    def make_hover_cmd(self, uav: UavRuntime, current_pose: bool = False) -> PositionCommand:
        if current_pose and uav.odom is not None:
            cmd_xy = (float(uav.odom["x"]), float(uav.odom["y"]))
            cmd_z = min(max(float(uav.odom["z"]), self.args.min_adapted_cmd_z_m), self.takeoff_hover_z(uav) + 0.35)
            cmd_yaw = float(uav.odom.get("yaw", self.args.yaw))
        else:
            cmd_xy = uav.home_odom_xy if uav.home_odom_xy is not None else uav.start_xy
            cmd_z = self.takeoff_hover_z(uav)
            cmd_yaw = self.args.yaw
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        msg.trajectory_id = 0
        msg.position.x = cmd_xy[0]
        msg.position.y = cmd_xy[1]
        msg.position.z = cmd_z
        msg.yaw = cmd_yaw
        return msg

    def publish_takeoff_land(self, cmd: int, repeats: int, selected_uavs: list[UavRuntime] | None = None) -> None:
        msg = TakeoffLand()
        msg.takeoff_land_cmd = cmd
        uavs = selected_uavs if selected_uavs is not None else list(self.uavs.values())
        for _ in range(repeats):
            for uav in uavs:
                uav.takeoff_land_pub.publish(msg)
                if cmd == TakeoffLand.TAKEOFF:
                    uav.takeoff_cmd_publish_count += 1
                elif cmd == TakeoffLand.LAND:
                    uav.land_cmd_publish_count += 1
            wall_sleep(0.1)

    def has_armed_or_started_rising(self, uav: UavRuntime) -> bool:
        if uav.state is not None and uav.state.armed:
            return True
        if uav.odom is None or uav.home_odom_z is None:
            return False
        return float(uav.odom["z"]) - uav.home_odom_z >= self.args.takeoff_rise_detect_m

    def publish_takeoff_sequence(self, rate: WallRate) -> None:
        uav_list = list(self.uavs.values())
        for index, uav in enumerate(uav_list):
            self.publish_takeoff_land(TakeoffLand.TAKEOFF, self.args.takeoff_cmd_repeats, [uav])
            if self.args.takeoff_uav_stagger_s <= 0.0 or index == len(uav_list) - 1:
                continue
            stagger_deadline = time.time() + self.args.takeoff_uav_stagger_s
            while not rospy.is_shutdown() and time.time() < stagger_deadline:
                if self.has_armed_or_started_rising(uav):
                    break
                self.publish_paths()
                rate.sleep()

    def maybe_retry_takeoff_commands(self, last_retry_wall: dict[int, float], retry_count: dict[int, int]) -> None:
        if self.args.takeoff_retry_interval_s <= 0.0 or self.args.takeoff_retry_max <= 0:
            return
        now_wall = time.time()
        for uid, uav in self.uavs.items():
            if self.has_armed_or_started_rising(uav):
                continue
            if retry_count.get(uid, 0) >= self.args.takeoff_retry_max:
                continue
            if now_wall - last_retry_wall.get(uid, 0.0) < self.args.takeoff_retry_interval_s:
                continue
            self.publish_takeoff_land(TakeoffLand.TAKEOFF, self.args.takeoff_retry_repeats, [uav])
            last_retry_wall[uid] = now_wall
            retry_count[uid] = retry_count.get(uid, 0) + 1

    def publish_hover_cmds(
        self,
        current_pose: bool = False,
        selected_uavs: list[UavRuntime] | None = None,
    ) -> None:
        uavs = selected_uavs if selected_uavs is not None else list(self.uavs.values())
        for uav in uavs:
            uav.hover_cmd_pub.publish(self.make_hover_cmd(uav, current_pose=current_pose))
            uav.hover_cmd_publish_count += 1

    def set_cmd_adapters_enabled(self, enabled: bool, repeats: int = 3) -> None:
        msg = Bool(data=enabled)
        for _ in range(repeats):
            for uav in self.uavs.values():
                uav.cmd_adapter_enable_pub.publish(msg)
            wall_sleep(0.05)

    def planner_command_quiesce(self, reason: str) -> None:
        self.set_cmd_adapters_enabled(False, repeats=5)
        self.phase = reason
        rate = WallRate(self.args.hover_publish_hz)
        settle_start = time.time()
        while not rospy.is_shutdown() and time.time() - settle_start < self.args.pre_land_hover_s:
            self.publish_hover_cmds(current_pose=True)
            self.publish_paths()
            rate.sleep()
        # px4ctrl's command timeout uses ROS time. Waiting on wall time here can
        # publish LAND too early whenever Gazebo runs below real time.
        stop_start_sim = self.now()
        stop_start_wall = time.monotonic()
        exit_reason = "ros_shutdown"
        while not rospy.is_shutdown():
            sim_elapsed_s = max(0.0, self.now() - stop_start_sim)
            wall_elapsed_s = max(0.0, time.monotonic() - stop_start_wall)
            if sim_elapsed_s >= self.args.pre_land_no_cmd_s:
                exit_reason = "simulation_quiet_period_completed"
                break
            if wall_elapsed_s >= self.args.pre_land_no_cmd_wall_timeout_s:
                exit_reason = "wall_time_hard_timeout"
                break
            self.publish_paths()
            rate.sleep()
        self.command_quiesce_summaries.append(
            {
                "reason": reason,
                "completed": exit_reason == "simulation_quiet_period_completed",
                "exit_reason": exit_reason,
                "time_basis": "ros_simulation_time_with_wall_hard_limit",
                "simulation_target_s": self.args.pre_land_no_cmd_s,
                "wall_hard_timeout_s": self.args.pre_land_no_cmd_wall_timeout_s,
                "simulation_elapsed_s": max(0.0, self.now() - stop_start_sim),
                "wall_elapsed_s": max(0.0, time.monotonic() - stop_start_wall),
            }
        )

    def publish_trigger(self) -> None:
        for uav in self.uavs.values():
            uav.pre_planner_trigger_snapshot = self.pre_planner_stability_snapshot(uav)
            uav.first_bspline_t = None
            uav.first_polytraj_t = None
            uav.first_planner_position_cmd_t = None
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.pose.orientation.w = 1.0
        for _ in range(5):
            self.trigger_pub.publish(msg)
            wall_sleep(0.1)

    def publish_manual_targets(self) -> None:
        if self.args.planner_target_mode == "formation_center":
            self.publish_formation_center_goal()
            return
        self.publish_target_goals(list(self.uavs), reset_planner_markers=True)

    def publish_target_goals(self, uids: list[int], reset_planner_markers: bool = False) -> None:
        messages: list[tuple[UavRuntime, PoseStamped]] = []
        stamp = rospy.Time.now()
        for uid in uids:
            uav = self.uavs[uid]
            if reset_planner_markers:
                uav.pre_planner_trigger_snapshot = self.pre_planner_stability_snapshot(uav)
                uav.first_bspline_t = None
                uav.first_polytraj_t = None
                uav.first_planner_position_cmd_t = None
            msg = PoseStamped()
            msg.header.stamp = stamp
            msg.header.frame_id = self.args.path_frame
            msg.pose.position.x = uav.target[0]
            msg.pose.position.y = uav.target[1]
            msg.pose.position.z = uav.target[2]
            msg.pose.orientation.w = 1.0
            messages.append((uav, msg))
        if self.args.goal_publish_stagger_s <= 0.0 or len(messages) <= 1:
            for _ in range(self.args.goal_publish_repeats):
                for uav, msg in messages:
                    msg.header.stamp = rospy.Time.now()
                    uav.goal_pub.publish(msg)
                    uav.goal_publish_count += 1
                wall_sleep(self.args.goal_publish_period_s)
            return

        # A simultaneous first trigger can make a lower-priority UAV plan
        # against a stationary peer placeholder and miss its first takeover.
        # RACER can opt into a bounded per-UAV startup stagger; the default
        # remains the original simultaneous publication behavior.
        for index, (uav, msg) in enumerate(messages):
            for _ in range(self.args.goal_publish_repeats):
                msg.header.stamp = rospy.Time.now()
                uav.goal_pub.publish(msg)
                uav.goal_publish_count += 1
                wall_sleep(self.args.goal_publish_period_s)
            if index + 1 < len(messages):
                wall_sleep(self.args.goal_publish_stagger_s)

    def publish_formation_center_goal(self) -> None:
        for uav in self.uavs.values():
            uav.pre_planner_trigger_snapshot = self.pre_planner_stability_snapshot(uav)
            uav.first_bspline_t = None
            uav.first_polytraj_t = None
            uav.first_planner_position_cmd_t = None

        msg = PoseStamped()
        msg.header.frame_id = self.args.path_frame
        msg.pose.position.x = self.args.formation_center_x
        msg.pose.position.y = self.args.formation_center_y
        msg.pose.position.z = self.args.formation_center_z
        msg.pose.orientation.w = 1.0

        for _ in range(self.args.goal_publish_repeats):
            msg.header.stamp = rospy.Time.now()
            # Swarm-Formation subscribes to one global formation-center goal.
            next(iter(self.uavs.values())).goal_pub.publish(msg)
            self.formation_center_goal_publish_count += 1
            for uav in self.uavs.values():
                uav.goal_publish_count += 1
            wall_sleep(self.args.goal_publish_period_s)

    def publish_paths(self) -> None:
        stamp = rospy.Time.now()
        target_path = RosPath(header=Header(stamp=stamp, frame_id=self.args.path_frame))
        for uav in self.uavs.values():
            uav.truth_path.header.stamp = stamp
            uav.cmd_path.header.stamp = stamp
            uav.truth_path_pub.publish(uav.truth_path)
            uav.cmd_path_pub.publish(uav.cmd_path)
            for xyz in ((uav.start_xy[0], uav.start_xy[1], self.args.takeoff_height), uav.target):
                ps = PoseStamped()
                ps.header = target_path.header
                ps.pose.position.x = xyz[0]
                ps.pose.position.y = xyz[1]
                ps.pose.position.z = xyz[2]
                ps.pose.orientation.w = 1.0
                target_path.poses.append(ps)
        self.target_path_pub.publish(target_path)

    def all_ready(self) -> bool:
        return all(uav.state and uav.state.connected and uav.odom and uav.truth for uav in self.uavs.values())

    def pre_takeoff_stability_snapshot(self, uav: UavRuntime) -> dict:
        now_t = self.now()
        reasons: list[str] = []
        snapshot: dict = {
            "t": now_t,
            "wall_elapsed_s": self.wall_elapsed(),
            "phase": self.phase,
            "required_stable_s": self.args.pre_takeoff_settle_s,
            "thresholds": {
                "odom_timeout_s": self.args.pre_takeoff_odom_timeout_s,
                "truth_timeout_s": self.args.pre_takeoff_truth_timeout_s,
                "max_speed_mps": self.args.pre_takeoff_max_speed_mps,
                "max_vz_mps": self.args.pre_takeoff_max_vz_mps,
                "max_roll_pitch_deg": self.args.pre_takeoff_max_roll_pitch_deg,
                "min_target_attitude_count": self.args.pre_takeoff_min_target_attitude_count,
                "min_debug_count": self.args.pre_takeoff_min_debug_count,
            },
        }
        if uav.state is None:
            reasons.append("state_missing")
        else:
            snapshot["state"] = {
                "connected": bool(uav.state.connected),
                "armed": bool(uav.state.armed),
                "guided": bool(uav.state.guided),
                "manual_input": bool(uav.state.manual_input),
                "mode": str(uav.state.mode),
                "system_status": int(uav.state.system_status),
            }
            if not uav.state.connected:
                reasons.append("mavros_not_connected")
            if not uav.state.guided:
                reasons.append("mavros_not_guided")
        if uav.odom is None:
            reasons.append("odom_missing")
        else:
            odom_age = now_t - uav.odom["t"]
            odom_speed = self.row_speed(uav.odom)
            odom_abs_vz = abs(uav.odom["vz"])
            odom_abs_roll_pitch_deg = math.degrees(max(abs(uav.odom["roll"]), abs(uav.odom["pitch"])))
            snapshot["odom"] = {
                "age_s": odom_age,
                "x": uav.odom["x"],
                "y": uav.odom["y"],
                "z": uav.odom["z"],
                "speed_mps": odom_speed,
                "abs_vz_mps": odom_abs_vz,
                "abs_roll_pitch_deg": odom_abs_roll_pitch_deg,
            }
            if odom_age > self.args.pre_takeoff_odom_timeout_s:
                reasons.append(f"odom_stale:{odom_age:.3f}")
            if odom_speed > self.args.pre_takeoff_max_speed_mps:
                reasons.append(f"odom_speed:{odom_speed:.3f}")
            if odom_abs_vz > self.args.pre_takeoff_max_vz_mps:
                reasons.append(f"odom_vz:{odom_abs_vz:.3f}")
            if odom_abs_roll_pitch_deg > self.args.pre_takeoff_max_roll_pitch_deg:
                reasons.append(f"odom_roll_pitch:{odom_abs_roll_pitch_deg:.3f}")
        if uav.truth is None:
            reasons.append("truth_missing")
        else:
            truth_age = now_t - uav.truth["t"]
            snapshot["truth"] = {
                "age_s": truth_age,
                "x": uav.truth["x"],
                "y": uav.truth["y"],
                "z": uav.truth["z"],
                "speed_mps": self.row_speed(uav.truth),
                "abs_vz_mps": abs(uav.truth["vz"]),
                "abs_roll_pitch_deg": math.degrees(max(abs(uav.truth["roll"]), abs(uav.truth["pitch"]))),
            }
            if truth_age > self.args.pre_takeoff_truth_timeout_s:
                reasons.append(f"truth_stale:{truth_age:.3f}")
        att_first_t = uav.att_rows[0]["t"] if uav.att_rows else None
        att_last_t = uav.att_rows[-1]["t"] if uav.att_rows else None
        snapshot["controller_stream"] = {
            "target_attitude_count": uav.target_attitude_count,
            "debug_count": uav.debug_count,
            "first_target_attitude_t": att_first_t,
            "last_target_attitude_t": att_last_t,
            "target_attitude_span_s": None if att_first_t is None or att_last_t is None else att_last_t - att_first_t,
        }
        if uav.target_attitude_count < self.args.pre_takeoff_min_target_attitude_count:
            reasons.append(f"target_attitude_count:{uav.target_attitude_count}")
        if uav.debug_count < self.args.pre_takeoff_min_debug_count:
            reasons.append(f"debug_count:{uav.debug_count}")
        snapshot["ok"] = not reasons
        snapshot["reasons"] = reasons
        uav.last_pre_takeoff_gate = snapshot
        uav.pre_takeoff_gate_history.append(snapshot)
        if len(uav.pre_takeoff_gate_history) > self.args.pre_planner_history_limit:
            uav.pre_takeoff_gate_history = uav.pre_takeoff_gate_history[-self.args.pre_planner_history_limit :]
        return snapshot

    def wait_pre_takeoff_settle(self, rate: WallRate) -> bool:
        self.phase = "pre_takeoff_settle"
        start_wall = time.time()
        stable_start_wall: float | None = None
        last_snapshots: list[dict] = []
        while not rospy.is_shutdown() and time.time() - start_wall < self.args.pre_takeoff_settle_timeout_s:
            self.publish_paths()
            last_snapshots = [self.pre_takeoff_stability_snapshot(uav) for uav in self.uavs.values()]
            if all(snapshot["ok"] for snapshot in last_snapshots):
                if stable_start_wall is None:
                    stable_start_wall = time.time()
                stable_elapsed = time.time() - stable_start_wall
                if stable_elapsed >= self.args.pre_takeoff_settle_s:
                    self.pre_takeoff_settle_summary = {
                        "status": "passed",
                        "duration_wall_s": time.time() - start_wall,
                        "stable_wall_s": stable_elapsed,
                        "last_snapshots": last_snapshots,
                    }
                    return True
            else:
                stable_start_wall = None
            rate.sleep()
        self.pre_takeoff_settle_summary = {
            "status": "blocked",
            "duration_wall_s": time.time() - start_wall,
            "required_stable_s": self.args.pre_takeoff_settle_s,
            "timeout_s": self.args.pre_takeoff_settle_timeout_s,
            "last_snapshots": last_snapshots,
        }
        return False

    def takeoff_status_summary(self, uav: UavRuntime) -> dict:
        state_rows = self.rows_in_phases(uav.state_rows, {"takeoff"})
        odom_rows = self.rows_in_phases(uav.odom_rows, {"takeoff"})
        truth_rows = self.rows_in_phases(uav.truth_rows, {"takeoff"})
        target_z = self.takeoff_hover_z(uav)
        max_odom_z = max((float(row["z"]) for row in odom_rows), default=None)
        max_truth_z = max((float(row["z"]) for row in truth_rows), default=None)
        return {
            "target_z_m": target_z,
            "takeoff_cmd_publish_count": uav.takeoff_cmd_publish_count,
            "land_cmd_publish_count": uav.land_cmd_publish_count,
            "state_samples": len(state_rows),
            "armed_observed": any(bool(row["armed"]) for row in state_rows)
            or bool(uav.state and uav.state.armed),
            "offboard_observed": any("OFFBOARD" in str(row["mode"]).upper() for row in state_rows),
            "mode_values": sorted({str(row["mode"]) for row in state_rows if row.get("mode")}),
            "last_state": None if not uav.state_rows else uav.state_rows[-1],
            "max_odom_z_m": max_odom_z,
            "max_truth_z_m": max_truth_z,
            "odom_height_error_to_target_m": None if max_odom_z is None else target_z - max_odom_z,
            "truth_height_error_to_target_m": None if max_truth_z is None else target_z - max_truth_z,
        }

    def takeoff_blockers(self) -> list[str]:
        blockers: list[str] = []
        for uid, uav in self.uavs.items():
            prefix = f"uav{uid}_"
            status = self.takeoff_status_summary(uav)
            if not status["offboard_observed"]:
                blockers.append(prefix + "offboard_not_observed")
            if not status["armed_observed"]:
                blockers.append(prefix + "arm_rejected_or_not_armed")
            max_odom_z = status["max_odom_z_m"]
            if max_odom_z is None or abs(max_odom_z - status["target_z_m"]) >= self.args.takeoff_z_tol:
                blockers.append(prefix + "takeoff_height_not_reached")
        return blockers or ["takeoff_height_reached_but_not_stable"]

    def reset_target_hold_metrics(self, uav: UavRuntime, chain_round_index: int | None = None) -> None:
        uav.reached_t = None
        uav.target_hold_metrics = {
            "reached": False,
            "required_s": self.args.target_hold_s,
            "radius_m": self.args.target_reached_radius,
            "max_speed_mps": self.args.target_hold_max_speed_mps,
            "max_vz_mps": self.args.target_hold_max_vz_mps,
            "stable_skip_enabled": self.args.target_stable_skip_radius_m > 0.0,
            "stable_skip_radius_m": self.args.target_stable_skip_radius_m,
            "stable_skip_required_s": self.args.target_stable_skip_s,
            "stable_skip_max_speed_mps": self.args.target_stable_skip_max_speed_mps,
            "stable_skip_max_vz_mps": self.args.target_stable_skip_max_vz_mps,
            "active_hold_mode": None,
            "reached_by": None,
            "hold_start_t": None,
            "hold_end_t": None,
            "duration_s": 0.0,
            "best_error_m": None,
            "best_snapshot": None,
            "first_reached_snapshot": None,
            "last_execute_snapshot": None,
            "end_snapshot": None,
            "chain_round_index": chain_round_index,
        }

    def execute_safety_blockers(self) -> list[str]:
        blockers: list[str] = []
        if self.min_inter_uav_distance < self.args.min_inter_uav_distance:
            blockers.append("inter_uav_distance_below_gate")
        for uid, uav in self.uavs.items():
            prefix = f"uav{uid}_"
            for source, row in (("truth", uav.truth), ("odom", uav.odom)):
                if row is None:
                    continue
                if float(row["z"]) < (self.args.execute_min_truth_z_m if source == "truth" else self.args.execute_min_odom_z_m):
                    blockers.append(prefix + f"execute_{source}_z_below_gate")
                abs_roll_pitch_deg = math.degrees(max(abs(float(row["roll"])), abs(float(row["pitch"]))))
                if abs_roll_pitch_deg > self.args.execute_max_roll_pitch_deg:
                    blockers.append(prefix + f"execute_{source}_roll_pitch_above_gate")
        return list(dict.fromkeys(blockers))

    def inter_uav_emergency_snapshot(self) -> dict | None:
        if not self.args.inter_uav_emergency_hold_enabled:
            return None
        now_t = self.now()
        candidates: list[dict] = []
        ids = sorted(self.uavs)
        for index, uid_a in enumerate(ids):
            odom_a = self.uavs[uid_a].odom
            if odom_a is None or now_t - float(odom_a["t"]) > self.args.inter_uav_emergency_odom_timeout_s:
                continue
            for uid_b in ids[index + 1 :]:
                odom_b = self.uavs[uid_b].odom
                if odom_b is None or now_t - float(odom_b["t"]) > self.args.inter_uav_emergency_odom_timeout_s:
                    continue
                guard = inter_uav_braking_guard(
                    (odom_a["x"], odom_a["y"], odom_a["z"]),
                    (odom_a["vx"], odom_a["vy"], odom_a["vz"]),
                    (odom_b["x"], odom_b["y"], odom_b["z"]),
                    (odom_b["vx"], odom_b["vy"], odom_b["vz"]),
                    self.args.min_inter_uav_distance,
                    self.args.inter_uav_emergency_deceleration_mps2,
                    self.args.inter_uav_emergency_margin_m,
                )
                if guard["triggered"]:
                    candidates.append(
                        {
                            "t": now_t,
                            "wall_elapsed_s": time.time() - self.start_wall,
                            "phase": self.phase,
                            "source": "mavros_fastlio_odom",
                            "pair": [uid_a, uid_b],
                            **guard,
                        }
                    )
        if not candidates:
            return None
        return min(candidates, key=lambda item: item["distance_m"] - item["trigger_distance_m"])

    def landing_uav_snapshot(self, uav: UavRuntime) -> dict:
        truth_z = None if uav.truth is None else float(uav.truth["z"])
        odom_z = None if uav.odom is None else float(uav.odom["z"])
        armed = None if uav.state is None else bool(uav.state.armed)
        truth_gate_z = (
            self.args.landed_z_max
            if uav.home_truth_z is None
            else uav.home_truth_z + self.args.landed_z_tolerance_m
        )
        odom_gate_z = (
            self.args.landed_z_max
            if uav.home_odom_z is None
            else uav.home_odom_z + self.args.landed_z_tolerance_m
        )
        truth_below_gate = truth_z is not None and truth_z <= truth_gate_z
        odom_below_gate = odom_z is not None and odom_z <= odom_gate_z
        disarmed = armed is False
        return {
            "truth_z_m": truth_z,
            "odom_z_m": odom_z,
            "armed": armed,
            "home_truth_z_m": uav.home_truth_z,
            "home_odom_z_m": uav.home_odom_z,
            "truth_gate_z_m": truth_gate_z,
            "odom_gate_z_m": odom_gate_z,
            "truth_below_gate": truth_below_gate,
            "odom_below_gate": odom_below_gate,
            "disarmed": disarmed,
            "landed": truth_below_gate and odom_below_gate and disarmed,
        }

    def run_landing(self, rate: WallRate) -> dict:
        self.phase = "land"
        self.publish_takeoff_land(TakeoffLand.LAND, self.args.land_cmd_repeats)
        start_sim_t = self.now()
        start_wall_t = time.monotonic()
        exit_reason = "ros_shutdown"
        per_uav: dict[str, dict] = {}
        while not rospy.is_shutdown():
            self.publish_paths()
            per_uav = {
                str(uid): self.landing_uav_snapshot(uav)
                for uid, uav in self.uavs.items()
            }
            if per_uav and all(item["landed"] for item in per_uav.values()):
                exit_reason = "all_uavs_landed_and_disarmed"
                break
            sim_elapsed_s = max(0.0, self.now() - start_sim_t)
            wall_elapsed_s = max(0.0, time.monotonic() - start_wall_t)
            if sim_elapsed_s >= self.args.land_timeout_s:
                exit_reason = "simulation_time_timeout"
                break
            if wall_elapsed_s >= self.args.land_wall_timeout_s:
                exit_reason = "wall_time_hard_timeout"
                break
            rate.sleep()

        per_uav = {
            str(uid): self.landing_uav_snapshot(uav)
            for uid, uav in self.uavs.items()
        }
        self.landing_summary = {
            "completed": bool(per_uav) and all(item["landed"] for item in per_uav.values()),
            "exit_reason": exit_reason,
            "time_basis": "ros_simulation_time_with_wall_hard_limit",
            "simulation_timeout_s": self.args.land_timeout_s,
            "wall_hard_timeout_s": self.args.land_wall_timeout_s,
            "simulation_elapsed_s": max(0.0, self.now() - start_sim_t),
            "wall_elapsed_s": max(0.0, time.monotonic() - start_wall_t),
            "landed_z_absolute_fallback_m": self.args.landed_z_max,
            "landed_z_tolerance_above_home_m": self.args.landed_z_tolerance_m,
            "landed_height_semantics": (
                "Each UAV must return to its own pre-takeoff truth and odom ground height "
                "plus tolerance, then disarm. The absolute threshold is fallback-only."
            ),
            "per_uav": per_uav,
        }
        return self.landing_summary

    def update_target_hold(self, uav: UavRuntime) -> bool:
        if not uav.odom:
            return False
        snapshot = self.target_state_snapshot(uav, uav.odom)
        if snapshot is None:
            return False
        assert uav.target_hold_metrics is not None
        uav.target_hold_metrics["last_execute_snapshot"] = snapshot
        best_error = uav.target_hold_metrics["best_error_m"]
        if best_error is None or snapshot["error_xyz_m"] < best_error:
            uav.target_hold_metrics["best_error_m"] = snapshot["error_xyz_m"]
            uav.target_hold_metrics["best_snapshot"] = snapshot
        speed_ok = self.args.target_hold_max_speed_mps <= 0.0 or snapshot["speed_mps"] <= self.args.target_hold_max_speed_mps
        vz_ok = self.args.target_hold_max_vz_mps <= 0.0 or snapshot["abs_vz_mps"] <= self.args.target_hold_max_vz_mps
        strict_ok = snapshot["error_xyz_m"] <= self.args.target_reached_radius and speed_ok and vz_ok
        skip_speed_ok = (
            self.args.target_stable_skip_max_speed_mps <= 0.0
            or snapshot["speed_mps"] <= self.args.target_stable_skip_max_speed_mps
        )
        skip_vz_ok = (
            self.args.target_stable_skip_max_vz_mps <= 0.0
            or snapshot["abs_vz_mps"] <= self.args.target_stable_skip_max_vz_mps
        )
        skip_ok = (
            self.args.target_stable_skip_radius_m > 0.0
            and snapshot["error_xyz_m"] <= self.args.target_stable_skip_radius_m
            and skip_speed_ok
            and skip_vz_ok
        )
        hold_mode = "strict_radius" if strict_ok else ("stable_skip" if skip_ok else None)
        required_s = self.args.target_hold_s if hold_mode == "strict_radius" else self.args.target_stable_skip_s
        if hold_mode is not None:
            if uav.reached_t is None or uav.target_hold_metrics.get("active_hold_mode") != hold_mode:
                uav.reached_t = time.time()
                uav.target_hold_metrics["active_hold_mode"] = hold_mode
                uav.target_hold_metrics["required_s"] = required_s
                uav.target_hold_metrics["hold_start_t"] = snapshot["t"]
                if uav.target_hold_metrics["first_reached_snapshot"] is None:
                    uav.target_hold_metrics["first_reached_snapshot"] = snapshot
            hold_duration = time.time() - uav.reached_t
            uav.target_hold_metrics["duration_s"] = hold_duration
            if hold_duration >= required_s:
                uav.target_hold_metrics["reached"] = True
                uav.target_hold_metrics["reached_by"] = hold_mode
                uav.target_hold_metrics["hold_end_t"] = snapshot["t"]
                uav.target_hold_metrics["end_snapshot"] = snapshot
        else:
            uav.reached_t = None
            uav.target_hold_metrics["active_hold_mode"] = None
            uav.target_hold_metrics["hold_start_t"] = None
            uav.target_hold_metrics["duration_s"] = 0.0
        return bool(uav.target_hold_metrics["reached"])

    def run_target_chains(self, rate: WallRate) -> tuple[bool, list[str]]:
        round_count = max((len(chain) for chain in self.target_chains.values()), default=0)
        report: dict = {
            "schema": "mosim.sunray_ros1.goal5_swarm_target_chain_probe.v1",
            "status": "running",
            "round_count": round_count,
            "chain_lengths": {f"uav{uid}": len(chain) for uid, chain in self.target_chains.items()},
            "rounds": [],
            "claim_boundary": (
                "Known-scene multi-UAV target-chain map-building support route. "
                "This is not pure unknown autonomous exploration or task allocation."
            ),
        }
        self.target_chain_report = report
        output_path = self.result_dir / "SWARM_TARGET_CHAIN_PROBE.json"

        for round_index in range(round_count):
            active_uids: list[int] = []
            for uid, uav in self.uavs.items():
                chain = self.target_chains.get(uid, [])
                if round_index < len(chain):
                    uav.target = chain[round_index]
                    active_uids.append(uid)
                    self.reset_target_hold_metrics(uav, chain_round_index=round_index + 1)
            if not active_uids:
                continue

            self.publish_target_goals(active_uids, reset_planner_markers=True)
            start_wall = time.time()
            last_goal_republish_wall = start_wall
            goal_republish_count = 0
            round_item: dict = {
                "round_index": round_index + 1,
                "active_uavs": active_uids,
                "targets": {f"uav{uid}": list(self.uavs[uid].target) for uid in active_uids},
                "status": "running",
                "blockers": [],
                "goal_republish_period_s": self.args.target_chain_goal_republish_period_s,
            }
            report["rounds"].append(round_item)
            output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

            while not rospy.is_shutdown() and time.time() - start_wall < self.args.target_chain_goal_timeout_s:
                if (
                    self.args.target_chain_goal_republish_period_s > 0.0
                    and time.time() - last_goal_republish_wall >= self.args.target_chain_goal_republish_period_s
                ):
                    self.publish_target_goals(active_uids, reset_planner_markers=False)
                    last_goal_republish_wall = time.time()
                    goal_republish_count += 1
                    round_item["goal_republish_count"] = goal_republish_count
                self.publish_paths()
                safety_blockers = self.execute_safety_blockers()
                if safety_blockers:
                    round_item["status"] = "blocked"
                    round_item["blockers"] = safety_blockers
                    report["status"] = "blocked"
                    report["blockers"] = safety_blockers
                    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                    return False, safety_blockers
                reached = [self.update_target_hold(self.uavs[uid]) for uid in active_uids]
                if all(reached):
                    round_item["status"] = "passed"
                    round_item["duration_wall_s"] = time.time() - start_wall
                    round_item["end_snapshots"] = {
                        f"uav{uid}": self.uavs[uid].target_hold_metrics.get("end_snapshot")
                        if self.uavs[uid].target_hold_metrics
                        else None
                        for uid in active_uids
                    }
                    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                    self.write_partial_outputs(
                        "running_partial",
                        [f"target_chain_round_{round_index + 1}_passed_pending_landing"],
                    )
                    break
                rate.sleep()
            else:
                blockers = [f"target_chain_round_{round_index + 1}_timeout"]
                round_item["status"] = "blocked"
                round_item["duration_wall_s"] = time.time() - start_wall
                round_item["blockers"] = blockers
                round_item["last_snapshots"] = {
                    f"uav{uid}": self.uavs[uid].target_hold_metrics.get("last_execute_snapshot")
                    if self.uavs[uid].target_hold_metrics
                    else None
                    for uid in active_uids
                }
                report["status"] = "blocked"
                report["blockers"] = blockers
                output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                self.write_partial_outputs("blocked_partial", blockers)
                return False, blockers

        report["status"] = "passed"
        report["blockers"] = []
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        self.write_partial_outputs("target_chain_passed_pending_landing", [])
        return True, []

    def run(self) -> int:
        rate = WallRate(self.args.hover_publish_hz)
        deadline = time.time() + self.args.ready_timeout_s
        while not rospy.is_shutdown() and time.time() < deadline:
            self.publish_paths()
            if self.all_ready():
                break
            rate.sleep()
        if not self.all_ready():
            self.write_outputs("blocked", ["ready_timeout"])
            return 10
        self.set_cmd_adapters_enabled(False)
        if not self.wait_pre_takeoff_settle(rate):
            self.write_outputs("blocked", ["pre_takeoff_settle_timeout"])
            return 10
        # Latch home only after the odometry stream has settled. With staggered
        # three-UAV startup, the first ready sample can contain a transient Z.
        for uav in self.uavs.values():
            if uav.odom:
                uav.home_odom_xy = (float(uav.odom["x"]), float(uav.odom["y"]))
                uav.home_odom_z = float(uav.odom["z"])
                uav.home_truth_z = None if uav.truth is None else float(uav.truth["z"])

        self.phase = "takeoff"
        self.publish_takeoff_sequence(rate)
        takeoff_start_sim = self.now()
        takeoff_start_wall = time.monotonic()
        last_retry_wall = {uid: time.time() for uid in self.uavs}
        retry_count = {uid: 0 for uid in self.uavs}
        hover_reached_time: float | None = None
        stable_reached_time: float | None = None
        hover_height_satisfied = False
        stable_satisfied = False
        required_stable_s = max(self.args.pre_ego_hover_s, self.args.pre_planner_stable_s)
        takeoff_exit_reason = "ros_shutdown"
        while not rospy.is_shutdown():
            takeoff_sim_elapsed_s = max(0.0, self.now() - takeoff_start_sim)
            takeoff_wall_elapsed_s = max(0.0, time.monotonic() - takeoff_start_wall)
            if takeoff_sim_elapsed_s >= self.args.takeoff_timeout_s:
                takeoff_exit_reason = "simulation_time_timeout"
                break
            if takeoff_wall_elapsed_s >= self.args.takeoff_wall_timeout_s:
                takeoff_exit_reason = "wall_time_hard_timeout"
                break
            self.maybe_retry_takeoff_commands(last_retry_wall, retry_count)
            if self.args.publish_hover_during_takeoff:
                airborne_uavs = [
                    uav for uav in self.uavs.values() if self.has_armed_or_started_rising(uav)
                ]
                self.publish_hover_cmds(selected_uavs=airborne_uavs)
            self.publish_paths()
            if all(
                uav.odom and abs(uav.odom["z"] - self.takeoff_hover_z(uav)) < self.args.takeoff_z_tol
                for uav in self.uavs.values()
            ):
                if hover_reached_time is None:
                    hover_reached_time = time.time()
                hover_height_satisfied = True
            else:
                hover_reached_time = None
                hover_height_satisfied = False
            gate_snapshots = [self.pre_planner_stability_snapshot(uav) for uav in self.uavs.values()]
            if all(snapshot["ok"] for snapshot in gate_snapshots):
                if stable_reached_time is None:
                    stable_reached_time = self.now()
                if self.now() - stable_reached_time >= required_stable_s:
                    stable_satisfied = True
                    takeoff_exit_reason = "height_and_stability_reached"
                    break
            else:
                stable_reached_time = None
                stable_satisfied = False
            rate.sleep()
        self.takeoff_timing_summary = {
            "completed": hover_height_satisfied and stable_satisfied,
            "exit_reason": takeoff_exit_reason,
            "time_basis": "ros_simulation_time_with_wall_hard_limit",
            "simulation_timeout_s": self.args.takeoff_timeout_s,
            "wall_hard_timeout_s": self.args.takeoff_wall_timeout_s,
            "simulation_elapsed_s": max(0.0, self.now() - takeoff_start_sim),
            "wall_elapsed_s": max(0.0, time.monotonic() - takeoff_start_wall),
        }
        if not hover_height_satisfied:
            self.write_outputs("blocked", self.takeoff_blockers())
            return 11
        if not stable_satisfied:
            self.write_outputs("blocked", ["pre_planner_hover_not_stable"])
            return 11

        self.phase = "ego_triggered"
        if self.args.planner_target_mode == "trigger":
            self.publish_trigger()
        else:
            self.publish_manual_targets()
        self.set_cmd_adapters_enabled(True)
        deadline = time.time() + self.args.ego_takeover_timeout_s
        while not rospy.is_shutdown() and time.time() < deadline:
            self.publish_hover_cmds()
            self.publish_paths()
            if all(self.first_planner_takeover_time(uav) is not None for uav in self.uavs.values()):
                break
            rate.sleep()
        if not all(self.first_planner_takeover_time(uav) is not None for uav in self.uavs.values()):
            self.write_outputs("blocked", ["planner_takeover_timeout"])
            return 12

        self.phase = "ego_execute"
        for uav in self.uavs.values():
            self.reset_target_hold_metrics(uav)
        execute_start = time.time()
        if self.args.mission_completion_mode == "exploration":
            self.exploration_started_t = self.now()
            emergency_event = None
            while (
                not rospy.is_shutdown()
                and self.now() - self.exploration_started_t < self.args.exploration_duration_s
            ):
                self.publish_paths()
                emergency_event = self.inter_uav_emergency_snapshot()
                if emergency_event is not None:
                    self.inter_uav_emergency_events.append(emergency_event)
                    break
                rate.sleep()
            self.exploration_ended_t = self.now()
            self.planner_command_quiesce(
                "inter_uav_emergency_hold" if emergency_event is not None else "pre_land_hover"
            )
            self.run_landing(rate)

            self.phase = "done"
            blockers = self.acceptance_blockers()
            if emergency_event is not None and "inter_uav_emergency_hold" not in blockers:
                blockers.insert(0, "inter_uav_emergency_hold")
            if blockers:
                self.write_outputs("blocked", blockers)
                return 14
            self.write_outputs("passed", [])
            return 0

        if self.target_chains:
            passed, chain_blockers = self.run_target_chains(rate)
            if not passed:
                blockers = list(chain_blockers)
                blockers.extend(b for b in self.acceptance_blockers() if b not in blockers)
                self.write_outputs("blocked", blockers)
                return 13

            self.planner_command_quiesce("pre_land_hover")
            self.run_landing(rate)

            self.phase = "done"
            blockers = self.acceptance_blockers()
            if blockers:
                self.write_outputs("blocked", blockers)
                return 14
            self.write_outputs("passed", [])
            return 0

        while not rospy.is_shutdown() and time.time() - execute_start < self.args.execute_timeout_s:
            self.publish_paths()
            all_reached = True
            for uav in self.uavs.values():
                if not self.update_target_hold(uav):
                    all_reached = False
            if all_reached:
                break
            rate.sleep()
        if not all(uav.target_hold_metrics and uav.target_hold_metrics.get("reached") for uav in self.uavs.values()):
            blockers = ["target_not_reached"]
            blockers.extend(b for b in self.acceptance_blockers() if b not in blockers)
            self.write_outputs("blocked", blockers)
            return 13

        self.planner_command_quiesce("pre_land_hover")
        self.run_landing(rate)

        self.phase = "done"
        blockers = self.acceptance_blockers()
        if blockers:
            self.write_outputs("blocked", blockers)
            return 14
        self.write_outputs("passed", [])
        return 0

    def acceptance_blockers(self) -> list[str]:
        blockers: list[str] = []
        if self.inter_uav_emergency_events:
            blockers.append("inter_uav_emergency_hold")
        if self.min_inter_uav_distance < self.args.min_inter_uav_distance:
            blockers.append("inter_uav_distance_below_gate")
        team_trajectory_freshness = self.exploration_team_trajectory_freshness_summary()
        if team_trajectory_freshness and not team_trajectory_freshness["passed"]:
            blockers.append("swarm_planner_trajectory_stale")
        if self.landing_summary is not None:
            for uid_text, landing in self.landing_summary["per_uav"].items():
                prefix = f"uav{uid_text}_"
                if not landing["truth_below_gate"] or not landing["odom_below_gate"]:
                    blockers.append(prefix + "landing_not_completed")
                if not landing["disarmed"]:
                    blockers.append(prefix + "still_armed_after_land")
        if self.command_quiesce_summaries and not self.command_quiesce_summaries[-1]["completed"]:
            blockers.append("pre_land_command_quiesce_timeout")
        for uid, uav in self.uavs.items():
            prefix = f"uav{uid}_"
            if uav.raw_lidar_count < self.args.min_raw_lidar_count:
                blockers.append(prefix + "raw_lidar_count_below_gate")
            if uav.raw_lidar_points < self.args.min_raw_lidar_points:
                blockers.append(prefix + "raw_lidar_points_below_gate")
            if uav.world_cloud_count < self.args.min_world_cloud_count:
                blockers.append(prefix + "world_cloud_count_below_gate")
            if uav.world_cloud_points < self.args.min_world_cloud_points:
                blockers.append(prefix + "world_cloud_points_below_gate")
            if uav.occupancy_count < self.args.min_occupancy_count:
                blockers.append(prefix + "occupancy_count_below_gate")
            if uav.occupancy_points < self.args.min_occupancy_points:
                blockers.append(prefix + "occupancy_points_below_gate")
            if uav.frontier_count < self.args.min_frontier_count:
                blockers.append(prefix + "frontier_count_below_gate")
            if uav.trajectory_vis_count < self.args.min_trajectory_vis_count:
                blockers.append(prefix + "trajectory_vis_count_below_gate")
            if uav.swarm_traj_count < self.args.min_swarm_traj_count:
                blockers.append(prefix + "swarm_traj_count_below_gate")
            if uav.bspline_count + uav.polytraj_count < self.args.min_planner_traj_count:
                blockers.append(prefix + "planner_trajectory_count_below_gate")
            if len(uav.raw_cmd_rows) < self.args.min_raw_position_cmd_count:
                blockers.append(prefix + "raw_position_cmd_count_below_gate")
            if len(uav.cmd_rows) < self.args.min_position_cmd_count:
                blockers.append(prefix + "position_cmd_count_below_gate")
            raw_execute_rows = self.rows_in_phases(uav.raw_cmd_rows, {"ego_execute"})
            cmd_execute_rows = self.rows_in_phases(uav.cmd_rows, {"ego_execute"})
            raw_z = self.z_range(raw_execute_rows)
            if raw_z and raw_z["min_m"] < self.args.min_raw_planner_z_warn_m:
                self.add_warning_once(uav, prefix + "raw_planner_position_cmd_z_below_gate")
                if self.args.block_on_raw_planner_z_below_gate:
                    blockers.append(prefix + "raw_planner_position_cmd_z_below_gate")
            adapted_z = self.z_range(cmd_execute_rows)
            if adapted_z and adapted_z["min_m"] < self.args.min_adapted_cmd_z_m:
                blockers.append(prefix + "adapted_position_cmd_z_below_gate")
            raw_continuity = self.command_continuity_summary(raw_execute_rows)
            if raw_continuity and raw_continuity.get("violates_jump_gate"):
                self.add_warning_once(uav, prefix + "raw_position_cmd_discontinuous")
                if self.args.block_on_raw_position_cmd_discontinuity:
                    blockers.append(prefix + "raw_position_cmd_discontinuous")
            adapted_continuity = self.command_continuity_summary(cmd_execute_rows)
            if adapted_continuity and adapted_continuity.get("violates_jump_gate"):
                blockers.append(prefix + "position_cmd_discontinuous")
            if uav.target_attitude_count < self.args.min_target_attitude_count:
                blockers.append(prefix + "target_attitude_count_below_gate")
            truth_execute = self.state_phase_summary(uav.truth_rows).get("ego_execute")
            if truth_execute:
                if truth_execute["min_z_m"] < self.args.execute_min_truth_z_m:
                    blockers.append(prefix + "execute_truth_z_below_gate")
                if truth_execute["max_abs_roll_pitch_deg"] > self.args.execute_max_roll_pitch_deg:
                    blockers.append(prefix + "execute_truth_roll_pitch_above_gate")
            odom_execute = self.state_phase_summary(uav.odom_rows).get("ego_execute")
            if odom_execute:
                if odom_execute["min_z_m"] < self.args.execute_min_odom_z_m:
                    blockers.append(prefix + "execute_odom_z_below_gate")
                if odom_execute["max_abs_roll_pitch_deg"] > self.args.execute_max_roll_pitch_deg:
                    blockers.append(prefix + "execute_odom_roll_pitch_above_gate")
        return blockers

    @staticmethod
    def add_warning_once(uav: UavRuntime, warning: str) -> None:
        if warning not in uav.warnings:
            uav.warnings.append(warning)

    @staticmethod
    def rows_in_phases(rows: list[dict], phases: set[str]) -> list[dict]:
        return [row for row in rows if str(row.get("phase") or "") in phases]

    @staticmethod
    def z_range(rows: list[dict]) -> dict | None:
        if not rows:
            return None
        values = [float(row["z"]) for row in rows]
        return {"min_m": min(values), "max_m": max(values), "mean_m": sum(values) / len(values)}

    @staticmethod
    def xyz_range(rows: list[dict]) -> dict | None:
        if not rows:
            return None
        return {
            axis: {
                "min_m": min(float(row[axis]) for row in rows),
                "max_m": max(float(row[axis]) for row in rows),
                "mean_m": sum(float(row[axis]) for row in rows) / len(rows),
            }
            for axis in ("x", "y", "z")
        }

    def read_cmd_safety_diagnostics(self, uav: UavRuntime) -> dict | None:
        if not uav.cmd_safety_diagnostics_path:
            return None
        try:
            return json.loads(uav.cmd_safety_diagnostics_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"missing": True, "path": str(uav.cmd_safety_diagnostics_path)}
        except json.JSONDecodeError as exc:
            return {"invalid_json": True, "path": str(uav.cmd_safety_diagnostics_path), "error": str(exc)}

    def command_continuity_summary(self, rows: list[dict]) -> dict | None:
        if len(rows) < 2:
            return None
        max_jump = 0.0
        max_xy_jump = 0.0
        max_z_jump = 0.0
        max_jump_speed = 0.0
        max_pair: dict | None = None
        violations = 0
        for prev, curr in zip(rows, rows[1:]):
            dt = float(curr["t"]) - float(prev["t"])
            if dt <= 1e-6:
                continue
            dx = float(curr["x"]) - float(prev["x"])
            dy = float(curr["y"]) - float(prev["y"])
            dz = float(curr["z"]) - float(prev["z"])
            jump = math.sqrt(dx * dx + dy * dy + dz * dz)
            xy_jump = math.hypot(dx, dy)
            z_jump = abs(dz)
            jump_speed = jump / dt
            if jump > max_jump:
                max_jump = jump
                max_pair = {
                    "t_prev": float(prev["t"]),
                    "t_curr": float(curr["t"]),
                    "dt_s": dt,
                    "jump_m": jump,
                    "xy_jump_m": xy_jump,
                    "z_jump_m": z_jump,
                    "jump_speed_mps": jump_speed,
                    "previous_xyz": [float(prev["x"]), float(prev["y"]), float(prev["z"])],
                    "current_xyz": [float(curr["x"]), float(curr["y"]), float(curr["z"])],
                    "previous_phase": prev.get("phase"),
                    "current_phase": curr.get("phase"),
                }
            max_xy_jump = max(max_xy_jump, xy_jump)
            max_z_jump = max(max_z_jump, z_jump)
            max_jump_speed = max(max_jump_speed, jump_speed)
            if (
                self.args.max_position_cmd_jump_m > 0.0
                and jump > self.args.max_position_cmd_jump_m
            ) or (
                self.args.max_position_cmd_speed_mps > 0.0
                and jump_speed > self.args.max_position_cmd_speed_mps
            ):
                violations += 1
        return {
            "samples": len(rows),
            "thresholds": {
                "max_position_cmd_jump_m": self.args.max_position_cmd_jump_m,
                "max_position_cmd_speed_mps": self.args.max_position_cmd_speed_mps,
            },
            "max_jump_m": max_jump,
            "max_xy_jump_m": max_xy_jump,
            "max_z_jump_m": max_z_jump,
            "max_jump_speed_mps": max_jump_speed,
            "max_jump_pair": max_pair,
            "violation_count": violations,
            "violates_jump_gate": violations > 0,
        }

    @staticmethod
    def state_phase_summary(rows: list[dict]) -> dict:
        summary: dict[str, dict] = {}
        for row in rows:
            phase = str(row.get("phase") or "unknown")
            item = summary.setdefault(
                phase,
                {
                    "samples": 0,
                    "min_z_m": float("inf"),
                    "max_z_m": float("-inf"),
                    "max_speed_mps": 0.0,
                    "max_abs_vz_mps": 0.0,
                    "max_abs_roll_pitch_deg": 0.0,
                },
            )
            item["samples"] += 1
            z = float(row["z"])
            speed = math.sqrt(float(row["vx"]) ** 2 + float(row["vy"]) ** 2 + float(row["vz"]) ** 2)
            abs_vz = abs(float(row["vz"]))
            abs_roll_pitch_deg = math.degrees(max(abs(float(row["roll"])), abs(float(row["pitch"]))))
            item["min_z_m"] = min(item["min_z_m"], z)
            item["max_z_m"] = max(item["max_z_m"], z)
            item["max_speed_mps"] = max(item["max_speed_mps"], speed)
            item["max_abs_vz_mps"] = max(item["max_abs_vz_mps"], abs_vz)
            item["max_abs_roll_pitch_deg"] = max(item["max_abs_roll_pitch_deg"], abs_roll_pitch_deg)
        return summary

    @staticmethod
    def write_csv(path: Path, rows: list[dict]) -> None:
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def write_outputs(self, status: str, blockers: list[str], metrics_filename: str = "EGO_SWARM_METRICS.json") -> None:
        per_uav = {}
        for uid, uav in self.uavs.items():
            prefix = f"uav{uid}_"
            self.write_csv(self.result_dir / f"{prefix}truth.csv", uav.truth_rows)
            self.write_csv(self.result_dir / f"{prefix}odom.csv", uav.odom_rows)
            self.write_csv(self.result_dir / f"{prefix}raw_position_cmd.csv", uav.raw_cmd_rows)
            self.write_csv(self.result_dir / f"{prefix}position_cmd.csv", uav.cmd_rows)
            self.write_csv(self.result_dir / f"{prefix}bspline_summary.csv", uav.bspline_rows)
            self.write_csv(self.result_dir / f"{prefix}target_attitude.csv", uav.att_rows)
            self.write_csv(self.result_dir / f"{prefix}debug_px4ctrl.csv", uav.debug_rows)
            self.write_csv(self.result_dir / f"{prefix}mavros_state.csv", uav.state_rows)
            post_land_final_err = None
            if uav.odom:
                post_land_final_err = math.dist((uav.odom["x"], uav.odom["y"], uav.odom["z"]), uav.target)
            target_hold_end_error = None
            if uav.target_hold_metrics and isinstance(uav.target_hold_metrics.get("end_snapshot"), dict):
                target_hold_end_error = uav.target_hold_metrics["end_snapshot"].get("error_xyz_m")
            per_uav[str(uid)] = {
                "target": {"x": uav.target[0], "y": uav.target[1], "z": uav.target[2]},
                "warnings": uav.warnings,
                "goal_topic": uav.goal_topic,
                "raw_position_cmd_topic": uav.raw_cmd_topic,
                "adapted_position_cmd_topic": uav.adapted_cmd_topic,
                "execute_target_error_m": target_hold_end_error,
                "post_land_final_target_error_m": post_land_final_err,
                "final_target_error_semantics": (
                    "post_land_final_target_error_m is measured after LAND and must not be used "
                    "as execute target tracking acceptance."
                ),
                "target_hold": uav.target_hold_metrics,
                "home_odom_xy": None if uav.home_odom_xy is None else {"x": uav.home_odom_xy[0], "y": uav.home_odom_xy[1]},
                "home_odom_z": uav.home_odom_z,
                "home_truth_z": uav.home_truth_z,
                "takeoff_hover_z": self.takeoff_hover_z(uav),
                "frame_alignment": self.frame_alignment_summary(uav),
                "planner_command_audit": {
                    "raw_xyz_range": self.xyz_range(uav.raw_cmd_rows),
                    "adapted_xyz_range": self.xyz_range(uav.cmd_rows),
                    "raw_continuity": self.command_continuity_summary(uav.raw_cmd_rows),
                    "adapted_continuity": self.command_continuity_summary(uav.cmd_rows),
                    "raw_execute_continuity": self.command_continuity_summary(
                        self.rows_in_phases(uav.raw_cmd_rows, {"ego_execute"})
                    ),
                    "adapted_execute_continuity": self.command_continuity_summary(
                        self.rows_in_phases(uav.cmd_rows, {"ego_execute"})
                    ),
                    "min_raw_planner_z_warn_m": self.args.min_raw_planner_z_warn_m,
                    "min_adapted_cmd_z_m": self.args.min_adapted_cmd_z_m,
                    "block_on_raw_planner_z_below_gate": self.args.block_on_raw_planner_z_below_gate,
                    "block_on_raw_position_cmd_discontinuity": self.args.block_on_raw_position_cmd_discontinuity,
                    "raw_position_cmd_discontinuity_gate_scope": "ego_execute",
                    "raw_z_below_gate": (
                        None
                        if not uav.raw_cmd_rows
                        else self.z_range(uav.raw_cmd_rows)["min_m"] < self.args.min_raw_planner_z_warn_m
                    ),
                    "adapted_z_below_gate": (
                        None
                        if not uav.cmd_rows
                        else self.z_range(uav.cmd_rows)["min_m"] < self.args.min_adapted_cmd_z_m
                    ),
                    "cmd_safety_adapter": self.read_cmd_safety_diagnostics(uav),
                },
                "phase_peak_summary": {
                    "truth": self.state_phase_summary(uav.truth_rows),
                    "odom": self.state_phase_summary(uav.odom_rows),
                },
                "first_bspline_t": uav.first_bspline_t,
                "first_polytraj_t": uav.first_polytraj_t,
                "first_planner_position_cmd_t": uav.first_planner_position_cmd_t,
                "first_planner_trajectory_t": self.first_planner_trajectory_time(uav),
                "first_planner_takeover_t": self.first_planner_takeover_time(uav),
                "exploration_stream": {
                    "enabled": self.args.mission_completion_mode == "exploration",
                    "duration_target_s": self.args.exploration_duration_s,
                    "time_basis": "ros_simulation_time",
                    "started_t": self.exploration_started_t,
                    "ended_t": self.exploration_ended_t,
                    "elapsed_s": (
                        None
                        if self.exploration_started_t is None or self.exploration_ended_t is None
                        else self.exploration_ended_t - self.exploration_started_t
                    ),
                    "trajectory_freshness": self.exploration_trajectory_freshness_summary(uav),
                },
                "hover_cmd_publish_count": uav.hover_cmd_publish_count,
                "goal_publish_count": uav.goal_publish_count,
                "takeoff_cmd_publish_count": uav.takeoff_cmd_publish_count,
                "land_cmd_publish_count": uav.land_cmd_publish_count,
                "takeoff_status": self.takeoff_status_summary(uav),
                "pre_takeoff_gate": {
                    "last_snapshot": uav.last_pre_takeoff_gate,
                    "history_tail": uav.pre_takeoff_gate_history[-20:],
                },
                "pre_planner_gate": {
                    "last_snapshot": uav.last_pre_planner_gate,
                    "trigger_snapshot": uav.pre_planner_trigger_snapshot,
                    "history_tail": uav.pre_planner_gate_history[-20:],
                },
                "counts": {
                    "truth_rows": len(uav.truth_rows),
                    "odom_rows": len(uav.odom_rows),
                    "mavros_state_rows": len(uav.state_rows),
                    "raw_position_cmd_rows": len(uav.raw_cmd_rows),
                    "position_cmd_rows": len(uav.cmd_rows),
                    "bspline": uav.bspline_count,
                    "polytraj": uav.polytraj_count,
                    "raw_lidar": uav.raw_lidar_count,
                    "world_cloud": uav.world_cloud_count,
                    "occupancy": uav.occupancy_count,
                    "frontier": uav.frontier_count,
                    "trajectory_vis": uav.trajectory_vis_count,
                    "swarm_traj": uav.swarm_traj_count,
                    "target_attitude": uav.target_attitude_count,
                    "debug_px4ctrl": uav.debug_count,
                },
                "last_point_counts": {
                    "raw_lidar": uav.raw_lidar_points,
                    "world_cloud": uav.world_cloud_points,
                    "occupancy": uav.occupancy_points,
                },
            }
        self.write_csv(self.result_dir / "inter_uav_separation.csv", self.separation_rows)
        summary = {
            "schema": "mosim.sunray_ros1.goal5_ego_swarm_metrics.v1",
            "status": status,
            "blockers": blockers,
            "uav_num": self.args.uav_num,
            "planner_target_mode": self.args.planner_target_mode,
            "formation_center_goal": {
                "enabled": self.args.planner_target_mode == "formation_center",
                "topic": next(iter(self.uavs.values())).goal_topic if self.uavs else "",
                "x": self.args.formation_center_x,
                "y": self.args.formation_center_y,
                "z": self.args.formation_center_z,
                "publish_count": self.formation_center_goal_publish_count,
                "semantics": (
                    "Swarm-Formation consumes one center goal and expands it "
                    "with global_goal/swarm_scale and relative_pos_i; per-UAV "
                    "targets in this metrics file are the expanded acceptance points."
                ),
            },
            "mission_completion_mode": self.args.mission_completion_mode,
            "swarm_exploration_stream": {
                "enabled": self.args.mission_completion_mode == "exploration",
                "duration_target_s": self.args.exploration_duration_s,
                "time_basis": "ros_simulation_time",
                "started_t": self.exploration_started_t,
                "ended_t": self.exploration_ended_t,
                "trajectory_freshness": self.exploration_team_trajectory_freshness_summary(),
            },
            "warnings": [warning for uav in self.uavs.values() for warning in uav.warnings],
            "per_uav": per_uav,
            "target_chain": self.target_chain_report,
            "pre_takeoff_settle": self.pre_takeoff_settle_summary,
            "takeoff_timing": self.takeoff_timing_summary,
            "min_inter_uav_distance_m": None if math.isinf(self.min_inter_uav_distance) else self.min_inter_uav_distance,
            "min_inter_uav_pair": self.min_inter_uav_pair,
            "inter_uav_emergency_hold": {
                "enabled": self.args.inter_uav_emergency_hold_enabled,
                "source": "mavros_fastlio_odom",
                "min_distance_m": self.args.min_inter_uav_distance,
                "deceleration_mps2": self.args.inter_uav_emergency_deceleration_mps2,
                "margin_m": self.args.inter_uav_emergency_margin_m,
                "odom_timeout_s": self.args.inter_uav_emergency_odom_timeout_s,
                "trigger_count": len(self.inter_uav_emergency_events),
                "events": self.inter_uav_emergency_events,
            },
            "pre_land_command_quiesce": self.command_quiesce_summaries,
            "landing": self.landing_summary,
            "claim_boundary": (
                "Goal5 multi-UAV planner engineering gate through px4ctrl/MAVROS/PX4/Gazebo. "
                "mission_completion_mode=target requires scripted target hold. "
                "mission_completion_mode=exploration proves bounded autonomous-exploration "
                "streaming, planner command output, map/frontier/trajectory evidence, "
                "landing, and inter-UAV safety only; it does not claim full-map completion. "
                "No fake_drone, no ROS2/x500, and Gazebo truth is evaluation only."
            ),
        }
        (self.result_dir / metrics_filename).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    def write_partial_outputs(self, status: str, blockers: list[str]) -> None:
        self.write_outputs(status, blockers, "EGO_SWARM_METRICS_PARTIAL.json")
        marker = {
            "schema": "mosim.sunray_ros1.goal5_partial_output_flush.v1",
            "status": status,
            "blockers": blockers,
            "phase": self.phase,
            "wall_elapsed_s": self.wall_elapsed(),
            "claim_boundary": (
                "Partial flush for diagnostics and timeout recovery only. "
                "It is not accepted by merged coverage gates unless a normal "
                "EGO_SWARM_METRICS.json with status=passed is produced."
            ),
        }
        (self.result_dir / "PARTIAL_OUTPUT_FLUSH.json").write_text(json.dumps(marker, indent=2), encoding="utf-8")

    def shutdown_blockers(self) -> list[str]:
        blockers = [f"{self.phase}_interrupted_by_ros_shutdown", "ros_shutdown"]
        if self.phase == "ego_execute" and self.args.mission_completion_mode == "target":
            if not all(uav.target_hold_metrics and uav.target_hold_metrics.get("reached") for uav in self.uavs.values()):
                blockers.insert(0, "target_not_reached")
        return list(dict.fromkeys(blockers))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--uav-num", type=int, choices=[2, 3], default=2)
    for uid, defaults in {
        1: (1.0, -1.0, 1.0, 0.0, -1.0),
        2: (1.0, 1.0, 1.0, 0.0, 1.0),
        3: (1.0, 0.0, 1.0, -1.5, 0.0),
    }.items():
        tx, ty, tz, sx, sy = defaults
        parser.add_argument(f"--target{uid}-x", dest=f"target{uid}_x", type=float, default=tx)
        parser.add_argument(f"--target{uid}-y", dest=f"target{uid}_y", type=float, default=ty)
        parser.add_argument(f"--target{uid}-z", dest=f"target{uid}_z", type=float, default=tz)
        parser.add_argument(f"--target{uid}-chain-file", dest=f"target{uid}_chain_file", default="")
        parser.add_argument(f"--start{uid}-x", dest=f"start{uid}_x", type=float, default=sx)
        parser.add_argument(f"--start{uid}-y", dest=f"start{uid}_y", type=float, default=sy)
    parser.add_argument("--path-frame", default="world")
    parser.add_argument("--planner-target-mode", choices=["goal", "trigger", "formation_center"], default="goal")
    parser.add_argument("--goal-topic-template", default="/uav{uid}/move_base_simple/goal")
    parser.add_argument("--formation-center-x", type=float, default=2.0)
    parser.add_argument("--formation-center-y", type=float, default=0.0)
    parser.add_argument("--formation-center-z", type=float, default=1.0)
    parser.add_argument("--raw-position-cmd-topic-template", default="/uav{uid}/planner_position_cmd_raw")
    parser.add_argument("--adapted-position-cmd-topic-template", default="/uav{uid}/position_cmd")
    parser.add_argument("--cmd-adapter-enable-topic-template", default="/uav{uid}/mosim/position_cmd_adapter_enable")
    parser.add_argument("--bspline-topic-template", default="/drone_{drone_id}_planning/bspline")
    parser.add_argument("--bspline-msg-package", choices=["traj_utils", "bspline", "auto"], default="traj_utils")
    parser.add_argument("--polytraj-topic-template", default="")
    parser.add_argument("--occupancy-topic-template", default="/drone_{drone_id}_ego_planner_node/grid_map/occupancy_inflate")
    parser.add_argument("--frontier-topic-template", default="")
    parser.add_argument("--trajectory-vis-topic-template", default="")
    parser.add_argument("--swarm-traj-topic", default="")
    parser.add_argument("--cmd-safety-diagnostics-template", default="")
    parser.add_argument("--min-raw-planner-z-warn-m", type=float, default=0.85)
    parser.add_argument("--min-adapted-cmd-z-m", type=float, default=0.85)
    parser.add_argument("--block-on-raw-planner-z-below-gate", action="store_true")
    parser.add_argument("--block-on-raw-position-cmd-discontinuity", action="store_true", default=None)
    parser.add_argument("--max-position-cmd-jump-m", type=float, default=0.50)
    parser.add_argument("--max-position-cmd-speed-mps", type=float, default=3.0)
    parser.add_argument("--goal-publish-repeats", type=int, default=5)
    parser.add_argument("--goal-publish-period-s", type=float, default=0.1)
    parser.add_argument("--goal-publish-stagger-s", type=float, default=0.0)
    parser.add_argument("--takeoff-height", type=float, default=1.0)
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--ready-timeout-s", type=float, default=60.0)
    parser.add_argument("--takeoff-timeout-s", type=float, default=45.0)
    parser.add_argument("--takeoff-wall-timeout-s", type=float, default=300.0)
    parser.add_argument("--ego-takeover-timeout-s", type=float, default=45.0)
    parser.add_argument("--execute-timeout-s", type=float, default=100.0)
    parser.add_argument("--land-timeout-s", type=float, default=30.0)
    parser.add_argument("--pre-land-hover-s", type=float, default=1.0)
    parser.add_argument("--pre-land-no-cmd-s", type=float, default=0.8)
    parser.add_argument("--pre-land-no-cmd-wall-timeout-s", type=float, default=30.0)
    parser.add_argument("--mission-completion-mode", choices=["target", "exploration"], default="target")
    parser.add_argument("--exploration-duration-s", type=float, default=30.0)
    parser.add_argument("--exploration-max-trajectory-stale-s", type=float, default=10.0)
    parser.add_argument("--pre-takeoff-settle-s", type=float, default=2.0)
    parser.add_argument("--pre-takeoff-settle-timeout-s", type=float, default=40.0)
    parser.add_argument("--pre-takeoff-odom-timeout-s", type=float, default=0.35)
    parser.add_argument("--pre-takeoff-truth-timeout-s", type=float, default=0.35)
    parser.add_argument("--pre-takeoff-max-speed-mps", type=float, default=0.10)
    parser.add_argument("--pre-takeoff-max-vz-mps", type=float, default=0.08)
    parser.add_argument("--pre-takeoff-max-roll-pitch-deg", type=float, default=8.0)
    parser.add_argument("--pre-takeoff-min-target-attitude-count", type=int, default=10)
    parser.add_argument("--pre-takeoff-min-debug-count", type=int, default=0)
    parser.add_argument("--pre-ego-hover-s", type=float, default=2.0)
    parser.add_argument("--pre-planner-stable-s", type=float, default=3.0)
    parser.add_argument("--pre-planner-odom-timeout-s", type=float, default=0.25)
    parser.add_argument("--pre-planner-max-xy-error-m", type=float, default=0.20)
    parser.add_argument("--pre-planner-max-z-error-m", type=float, default=0.10)
    parser.add_argument("--pre-planner-max-speed-mps", type=float, default=0.25)
    parser.add_argument("--pre-planner-max-vz-mps", type=float, default=0.18)
    parser.add_argument("--pre-planner-max-roll-pitch-deg", type=float, default=12.0)
    parser.add_argument("--pre-planner-history-limit", type=int, default=200)
    parser.add_argument("--publish-hover-during-takeoff", action="store_true")
    parser.add_argument("--target-hold-s", type=float, default=2.0)
    parser.add_argument("--target-hold-max-speed-mps", type=float, default=0.35)
    parser.add_argument("--target-hold-max-vz-mps", type=float, default=0.20)
    parser.add_argument("--target-stable-skip-radius-m", type=float, default=0.0)
    parser.add_argument("--target-stable-skip-s", type=float, default=2.0)
    parser.add_argument("--target-stable-skip-max-speed-mps", type=float, default=0.08)
    parser.add_argument("--target-stable-skip-max-vz-mps", type=float, default=0.08)
    parser.add_argument("--target-chain-max-goals", type=int, default=0)
    parser.add_argument("--target-chain-goal-timeout-s", type=float, default=90.0)
    parser.add_argument("--target-chain-goal-republish-period-s", type=float, default=3.0)
    parser.add_argument("--execute-min-truth-z-m", type=float, default=0.50)
    parser.add_argument("--execute-min-odom-z-m", type=float, default=0.50)
    parser.add_argument("--execute-max-roll-pitch-deg", type=float, default=45.0)
    parser.add_argument("--takeoff-z-tol", type=float, default=0.15)
    parser.add_argument("--target-reached-radius", type=float, default=0.45)
    parser.add_argument("--landed-z-max", type=float, default=0.20)
    parser.add_argument("--landed-z-tolerance-m", type=float, default=0.08)
    parser.add_argument("--land-wall-timeout-s", type=float, default=300.0)
    parser.add_argument("--min-inter-uav-distance", type=float, default=0.45)
    parser.add_argument("--inter-uav-emergency-hold-enabled", action="store_true")
    parser.add_argument("--inter-uav-emergency-deceleration-mps2", type=float, default=1.2)
    parser.add_argument("--inter-uav-emergency-margin-m", type=float, default=0.2)
    parser.add_argument("--inter-uav-emergency-odom-timeout-s", type=float, default=0.3)
    parser.add_argument("--min-raw-lidar-count", type=int, default=5)
    parser.add_argument("--min-raw-lidar-points", type=int, default=1)
    parser.add_argument("--world-cloud-topic-template", default="/uav{uid}/livox_world")
    parser.add_argument("--min-world-cloud-count", type=int, default=5)
    parser.add_argument("--min-world-cloud-points", type=int, default=1)
    parser.add_argument("--min-occupancy-count", type=int, default=2)
    parser.add_argument("--min-occupancy-points", type=int, default=1)
    parser.add_argument("--min-frontier-count", type=int, default=0)
    parser.add_argument("--min-trajectory-vis-count", type=int, default=0)
    parser.add_argument("--min-swarm-traj-count", type=int, default=0)
    parser.add_argument("--min-bspline-count", type=int, default=0)
    parser.add_argument("--min-planner-traj-count", type=int, default=1)
    parser.add_argument("--min-raw-position-cmd-count", type=int, default=10)
    parser.add_argument("--min-position-cmd-count", type=int, default=10)
    parser.add_argument("--min-target-attitude-count", type=int, default=10)
    parser.add_argument("--hover-publish-hz", type=float, default=50.0)
    parser.add_argument("--record-hz", type=float, default=30.0)
    parser.add_argument("--record-cmd-hz", type=float, default=50.0)
    parser.add_argument("--max-path-points", type=int, default=8000)
    parser.add_argument("--takeoff-cmd-repeats", type=int, default=8)
    parser.add_argument("--takeoff-uav-stagger-s", type=float, default=0.0)
    parser.add_argument("--takeoff-retry-interval-s", type=float, default=0.0)
    parser.add_argument("--takeoff-retry-repeats", type=int, default=3)
    parser.add_argument("--takeoff-retry-max", type=int, default=0)
    parser.add_argument("--takeoff-rise-detect-m", type=float, default=0.08)
    parser.add_argument("--land-cmd-repeats", type=int, default=8)
    args = parser.parse_args()
    if args.block_on_raw_position_cmd_discontinuity is None:
        args.block_on_raw_position_cmd_discontinuity = args.mission_completion_mode != "exploration"
    return args


def main() -> None:
    rospy.init_node("mosim_px4ctrl_ego_swarm_mission")
    mission = EgoSwarmMission(parse_args())
    try:
        raise SystemExit(mission.run())
    except rospy.exceptions.ROSInterruptException:
        mission.write_outputs("blocked", mission.shutdown_blockers())
        raise SystemExit(16)


if __name__ == "__main__":
    main()
