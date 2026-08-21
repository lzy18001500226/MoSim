#!/usr/bin/env python3
"""Goal4 EGO single-UAV mission gate for original px4ctrl + Gazebo."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

from mission_status_channel import MissionStatusChannel
from safe_stop_channel import SafeStopChannel

import rospy
import sensor_msgs.point_cloud2 as pc2
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Point, PoseStamped
from mavros_msgs.msg import AttitudeTarget, State
from nav_msgs.msg import Odometry, Path as RosPath
from quadrotor_msgs.msg import GoalSet, PositionCommand, Px4ctrlDebug, TakeoffLand
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool, Header
from visualization_msgs.msg import Marker, MarkerArray
try:
    from traj_utils.msg import Bspline as TrajUtilsBspline
except ImportError:  # EGO v2 overlays may not define Bspline.
    TrajUtilsBspline = None

try:
    from bspline.msg import Bspline as FuelBspline
except ImportError:  # FUEL overlays may not be sourced for EGO/Diff runs.
    FuelBspline = None

try:
    from trajectory.msg import Bspline as FalconBspline
except ImportError:  # FALCON overlays may not be sourced for non-FALCON runs.
    FalconBspline = None

try:
    from traj_utils.msg import PolyTraj
except ImportError:  # EGO v1 overlays may not define PolyTraj.
    PolyTraj = None


class EgoSingleMission:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.start_wall = time.time()
        self.phase = "init"
        self.mission_status = MissionStatusChannel("goal4_single_planner_mission", ["uav1"])
        self.home: tuple[float, float, float] | None = None
        self.mission_home_xy: tuple[float, float] | None = None
        self.truth_home: tuple[float, float, float] | None = None
        self.last_truth: dict | None = None
        self.last_sunray_truth: dict | None = None
        self.last_odom: dict | None = None
        self.last_path_odom: Odometry | None = None
        self.last_path_odom_row: dict | None = None
        self.last_state: State | None = None
        self.last_position_cmd: dict | None = None
        self.home_odom_z: float | None = None
        self.last_position_cmd_xyz: tuple[float, float, float] | None = None
        self.cmd_adapter_enabled = True
        self.hover_cmd_publisher_released = False
        self.interactive_hover_yaw: float | None = None
        self.last_forwarded_goal: dict | None = None
        self.forwarded_goal_seq = 0
        self.last_pre_diff_gate: dict | None = None
        self.pre_diff_gate_history: list[dict] = []
        self.pre_diff_trigger_snapshot: dict | None = None
        self.flight_safety_violation: dict | None = None
        self.target_hold_metrics: dict | None = None
        self.exploration_metrics: dict | None = None
        self.land_metrics: dict | None = None
        self.interactive_goal_metrics: dict[str, dict] = {}
        self.interactive_goal_handoff_metrics: list[dict] = []
        self.last_interactive_goal_frame_issue: dict | None = None
        self.interactive_final_hover_metrics: dict | None = None
        self.interactive_yaw_scan_events: list[dict] = []
        self.first_bspline_t: float | None = None
        self.first_polytraj_t: float | None = None
        self.first_planner_position_cmd_t: float | None = None
        self.bspline_count = 0
        self.polytraj_count = 0
        self.position_cmd_count = 0
        self.planner_position_cmd_count = 0
        self.hover_cmd_publish_count = 0
        self.takeoff_cmd_publish_count = 0
        self.land_cmd_publish_count = 0
        self.lidar_count = 0
        self.lidar_last_points = 0
        self.world_cloud_count = 0
        self.world_cloud_last_points = 0
        self.occupancy_count = 0
        self.occupancy_last_points = 0
        self.occupancy_max_points = 0
        self.frontier_count = 0
        self.frontier_marker_count = 0
        self.trajectory_vis_count = 0
        self.trajectory_vis_marker_count = 0
        self.att_target_count = 0
        self.debug_count = 0
        self.safe_stop = SafeStopChannel()

        self.truth_rows: list[dict] = []
        self.sunray_truth_rows: list[dict] = []
        self.odom_rows: list[dict] = []
        self.state_rows: list[dict] = []
        self.position_cmd_rows: list[dict] = []
        self.planner_position_cmd_rows: list[dict] = []
        self.forwarded_goal_rows: list[dict] = []
        self.bspline_rows: list[dict] = []
        self.att_target_rows: list[dict] = []
        self.debug_rows: list[dict] = []
        self.last_record_t = {
            "truth": -1e9,
            "sunray_truth": -1e9,
            "odom": -1e9,
            "cmd": -1e9,
            "planner_cmd": -1e9,
            "att": -1e9,
            "debug": -1e9,
            "path_publish": -1e9,
        }

        self.takeoff_land_pub = rospy.Publisher("/px4ctrl/takeoff_land", TakeoffLand, queue_size=3, latch=True)
        self.hover_cmd_pub = rospy.Publisher("/position_cmd", PositionCommand, queue_size=10)
        self.cmd_adapter_enable_pub = rospy.Publisher(args.cmd_adapter_enable_topic, Bool, queue_size=3, latch=True)
        self.interactive_goal_ready_pub = rospy.Publisher(args.interactive_goal_ready_topic, Bool, queue_size=3, latch=True)
        self.trigger_pub = rospy.Publisher("/traj_start_trigger", PoseStamped, queue_size=3, latch=True)
        self.goalset_pub = rospy.Publisher(args.goalset_topic, GoalSet, queue_size=3, latch=True) if args.goalset_topic else None
        self.goal_pose_pub = rospy.Publisher(args.goal_pose_topic, PoseStamped, queue_size=3, latch=True) if args.goal_pose_topic else None
        self.truth_path_pub = rospy.Publisher("/mosim/goal4/truth_path", RosPath, queue_size=1, latch=True)
        self.cmd_path_pub = rospy.Publisher("/mosim/goal4/position_cmd_path", RosPath, queue_size=1, latch=True)
        self.target_path_pub = rospy.Publisher("/mosim/goal4/target_path", RosPath, queue_size=1, latch=True)
        # Keep the last vehicle pose visible when RViz starts after the mission node.
        self.body_axes_pub = rospy.Publisher(args.body_axes_topic, MarkerArray, queue_size=1, latch=True)
        self.truth_path = RosPath(header=Header(frame_id=args.path_frame))
        self.cmd_path = RosPath(header=Header(frame_id=args.path_frame))

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=30)
        rospy.Subscriber(args.sunray_truth_topic, Odometry, self.on_sunray_truth, queue_size=100)
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=100)
        if args.path_odom_topic:
            rospy.Subscriber(args.path_odom_topic, Odometry, self.on_path_odom, queue_size=100)
        rospy.Subscriber("/uav1/mavros/state", State, self.on_state, queue_size=20)
        rospy.Subscriber(args.interactive_forwarded_goal_topic, PoseStamped, self.on_forwarded_goal, queue_size=30)
        rospy.Subscriber("/position_cmd", PositionCommand, self.on_position_cmd, queue_size=200)
        if args.planner_position_cmd_topic:
            rospy.Subscriber(args.planner_position_cmd_topic, PositionCommand, self.on_planner_position_cmd, queue_size=200)
        bspline_msg_cls = self.select_bspline_msg_class()
        if bspline_msg_cls is not None and args.bspline_topic:
            rospy.Subscriber(args.bspline_topic, bspline_msg_cls, self.on_bspline, queue_size=20)
        if PolyTraj is not None and args.polytraj_topic:
            rospy.Subscriber(args.polytraj_topic, PolyTraj, self.on_polytraj, queue_size=20)
        rospy.Subscriber(args.raw_lidar_topic, PointCloud2, self.on_raw_lidar, queue_size=20)
        rospy.Subscriber(args.world_cloud_topic, PointCloud2, self.on_world_cloud, queue_size=20)
        if args.occupancy_msg_type == "markerarray":
            rospy.Subscriber(args.occupancy_topic, MarkerArray, self.on_occupancy_markers, queue_size=20)
        else:
            rospy.Subscriber(args.occupancy_topic, PointCloud2, self.on_occupancy, queue_size=20)
        if args.frontier_topic:
            if args.frontier_msg_type == "pointcloud2":
                rospy.Subscriber(args.frontier_topic, PointCloud2, self.on_frontier_cloud, queue_size=20)
            elif args.frontier_msg_type == "markerarray":
                rospy.Subscriber(args.frontier_topic, MarkerArray, self.on_frontier_marker_array, queue_size=20)
            else:
                rospy.Subscriber(args.frontier_topic, Marker, self.on_frontier, queue_size=20)
        if args.trajectory_vis_topic:
            if args.trajectory_vis_msg_type == "markerarray":
                rospy.Subscriber(args.trajectory_vis_topic, MarkerArray, self.on_trajectory_vis_marker_array, queue_size=20)
            else:
                rospy.Subscriber(args.trajectory_vis_topic, Marker, self.on_trajectory_vis, queue_size=20)
        rospy.Subscriber("/uav1/mavros/setpoint_raw/target_attitude", AttitudeTarget, self.on_att_target, queue_size=100)
        rospy.Subscriber("/debugPx4ctrl", Px4ctrlDebug, self.on_debug, queue_size=100)

    def select_bspline_msg_class(self):
        if self.args.bspline_msg_package == "traj_utils":
            return TrajUtilsBspline
        if self.args.bspline_msg_package == "bspline":
            return FuelBspline
        if self.args.bspline_msg_package == "trajectory":
            return FalconBspline
        if self.args.bspline_topic == "/planning/bspline" and FuelBspline is not None:
            return FuelBspline
        return TrajUtilsBspline or FuelBspline or FalconBspline

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        return float(stamp) if stamp > 0 else time.time() - self.start_wall

    def wall_elapsed(self) -> float:
        return time.time() - self.start_wall

    @property
    def phase(self) -> str:
        return self._phase

    @phase.setter
    def phase(self, value: str) -> None:
        self._phase = str(value)
        channel = getattr(self, "mission_status", None)
        if channel is not None:
            channel.update_phase(self._phase)

    def should_record(self, key: str, t: float, hz: float) -> bool:
        if hz <= 0:
            return True
        if t - self.last_record_t[key] < 1.0 / hz:
            return False
        self.last_record_t[key] = t
        return True

    @staticmethod
    def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    @classmethod
    def rpy_from_quat(cls, x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        yaw = cls.yaw_from_quat(x, y, z, w)
        return roll, pitch, yaw

    def on_state(self, msg: State) -> None:
        self.last_state = msg
        self.mission_status.update_vehicle(
            "uav1", connected=msg.connected, armed=msg.armed, mode=msg.mode
        )
        self.state_rows.append(
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
        if len(self.state_rows) > 5000:
            self.state_rows = self.state_rows[-5000:]

    def on_forwarded_goal(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        self.forwarded_goal_seq += 1
        row = {
            "t": self.now(),
            "phase": self.phase,
            "seq": self.forwarded_goal_seq,
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "frame_id": msg.header.frame_id or self.args.path_frame,
        }
        self.last_forwarded_goal = row
        self.forwarded_goal_rows.append(row)

    def on_model_states(self, msg: ModelStates) -> None:
        try:
            idx = list(msg.name).index(self.args.truth_model_name)
        except ValueError:
            return
        pose = msg.pose[idx]
        twist = msg.twist[idx]
        q = pose.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        t = self.now()
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
        self.last_truth = row
        if self.home is None and len(self.truth_rows) > 5:
            self.home = (row["x"], row["y"], row["z"])
        if self.truth_home is None and len(self.truth_rows) > 5:
            self.truth_home = (row["x"], row["y"], row["z"])
        if self.should_record("truth", t, self.args.record_hz):
            self.truth_rows.append(row)
            self.append_path(self.truth_path, row["x"], row["y"], row["z"], t, max_points=self.args.max_path_points)

    def on_sunray_truth(self, msg: Odometry) -> None:
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
        self.last_sunray_truth = row
        if self.should_record("sunray_truth", t, self.args.record_hz):
            self.sunray_truth_rows.append(row)

    def odom_row(self, msg: Odometry) -> dict:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        return {
            "t": self.now(),
            "phase": self.phase,
            "frame_id": str(msg.header.frame_id or ""),
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

    def on_odom(self, msg: Odometry) -> None:
        row = self.odom_row(msg)
        t = float(row["t"])
        self.last_odom = row
        if self.should_record("odom", t, self.args.record_hz):
            self.odom_rows.append(row)

    def on_path_odom(self, msg: Odometry) -> None:
        self.last_path_odom = msg
        self.last_path_odom_row = self.odom_row(msg)

    def position_cmd_row(self, msg: PositionCommand, receive_t: float | None = None) -> dict:
        t = self.now() if receive_t is None else receive_t
        return {
            "t": t,
            "header_t": float(msg.header.stamp.to_sec()),
            "wall_elapsed_s": self.wall_elapsed(),
            "phase": self.phase,
            "trajectory_id": int(msg.trajectory_id),
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

    def on_position_cmd(self, msg: PositionCommand) -> None:
        t = self.now()
        row = self.position_cmd_row(msg, t)
        current_xyz = (row["x"], row["y"], row["z"])
        if self.args.cmd_path_segment_jump_m > 0.0 and self.last_position_cmd_xyz is not None:
            jump = math.dist(self.last_position_cmd_xyz, current_xyz)
            if jump > self.args.cmd_path_segment_jump_m:
                self.cmd_path = RosPath(header=Header(frame_id=self.args.path_frame))
        self.last_position_cmd = row
        self.last_position_cmd_xyz = current_xyz
        self.position_cmd_count += 1
        if self.should_record("cmd", t, self.args.record_cmd_hz):
            self.position_cmd_rows.append(row)
            # /position_cmd is PX4-local after the common-world inverse bridge,
            # while the review path is explicitly published in the world frame.
            self.append_path(
                self.cmd_path,
                row["x"] + self.args.path_command_offset_x,
                row["y"] + self.args.path_command_offset_y,
                row["z"] + self.args.path_command_offset_z,
                t,
                max_points=self.args.max_path_points,
            )

    def on_planner_position_cmd(self, msg: PositionCommand) -> None:
        t = self.now()
        if self.first_planner_position_cmd_t is None:
            self.first_planner_position_cmd_t = t
        self.planner_position_cmd_count += 1
        if self.should_record("planner_cmd", t, self.args.record_cmd_hz):
            self.planner_position_cmd_rows.append(self.position_cmd_row(msg, t))

    def on_bspline(self, msg: Bspline) -> None:
        t = self.now()
        self.bspline_count += 1
        if self.first_bspline_t is None:
            self.first_bspline_t = t
        self.bspline_rows.append(
            {
                "t": t,
                "traj_id": int(msg.traj_id),
                "order": int(msg.order),
                "pos_pts": len(msg.pos_pts),
                "knots": len(msg.knots),
                "start_time": msg.start_time.to_sec(),
            }
        )

    def exploration_trajectory_freshness_summary(self) -> dict | None:
        if self.args.mission_mode != "exploration_stream" or not self.exploration_metrics:
            return None
        start_t = self.exploration_metrics.get("started_t")
        end_t = self.exploration_metrics.get("ended_t")
        if start_t is None or end_t is None:
            return None
        publish_times = sorted(
            float(row["t"])
            for row in self.bspline_rows
            if start_t <= float(row["t"]) <= end_t
        )
        boundaries = [float(start_t), *publish_times, float(end_t)]
        gaps = [boundaries[i + 1] - boundaries[i] for i in range(len(boundaries) - 1)]
        max_gap = max(gaps) if gaps else float(end_t) - float(start_t)
        return {
            "threshold_s": self.args.exploration_max_trajectory_stale_s,
            "publish_count": len(publish_times),
            "first_publish_t": publish_times[0] if publish_times else None,
            "last_publish_t": publish_times[-1] if publish_times else None,
            "max_gap_s": max_gap,
            "terminal_stale_s": float(end_t) - publish_times[-1] if publish_times else float(end_t) - float(start_t),
            "passed": (
                self.args.exploration_max_trajectory_stale_s <= 0.0
                or (publish_times and max_gap <= self.args.exploration_max_trajectory_stale_s)
            ),
        }

    def on_polytraj(self, msg) -> None:
        t = self.now()
        self.polytraj_count += 1
        if self.first_polytraj_t is None:
            self.first_polytraj_t = t
        self.bspline_rows.append(
            {
                "t": t,
                "traj_id": int(msg.traj_id),
                "order": int(msg.order),
                "pos_pts": 0,
                "knots": len(msg.duration),
                "start_time": msg.start_time.to_sec(),
                "planner_msg": "PolyTraj",
            }
        )

    def on_raw_lidar(self, msg: PointCloud2) -> None:
        self.lidar_count += 1
        self.lidar_last_points = int(msg.width * msg.height)

    def on_world_cloud(self, msg: PointCloud2) -> None:
        self.world_cloud_count += 1
        self.world_cloud_last_points = int(msg.width * msg.height)

    def on_occupancy(self, msg: PointCloud2) -> None:
        self.occupancy_count += 1
        self.occupancy_last_points = int(msg.width * msg.height)
        self.occupancy_max_points = max(self.occupancy_max_points, self.occupancy_last_points)

    def on_occupancy_markers(self, msg: MarkerArray) -> None:
        self.occupancy_count += 1
        self.occupancy_last_points = len(msg.markers)
        self.occupancy_max_points = max(self.occupancy_max_points, self.occupancy_last_points)

    def on_frontier(self, msg: Marker) -> None:
        self.frontier_count += 1
        self.frontier_marker_count += 1

    def on_frontier_cloud(self, msg: PointCloud2) -> None:
        self.frontier_count += 1
        self.frontier_marker_count += int(msg.width * msg.height)

    def on_frontier_marker_array(self, msg: MarkerArray) -> None:
        self.frontier_count += 1
        self.frontier_marker_count += len(msg.markers)

    def on_trajectory_vis(self, msg: Marker) -> None:
        self.trajectory_vis_count += 1
        self.trajectory_vis_marker_count += 1

    def on_trajectory_vis_marker_array(self, msg: MarkerArray) -> None:
        self.trajectory_vis_count += 1
        self.trajectory_vis_marker_count += len(msg.markers)

    def on_att_target(self, msg: AttitudeTarget) -> None:
        self.att_target_count += 1
        t = self.now()
        if not self.should_record("att", t, self.args.record_cmd_hz):
            return
        q = msg.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        self.att_target_rows.append(
            {
                "t": t,
                "phase": self.phase,
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw,
                "thrust": float(msg.thrust),
            }
        )

    def on_debug(self, msg: Px4ctrlDebug) -> None:
        self.debug_count += 1
        t = self.now()
        if not self.should_record("debug", t, self.args.record_cmd_hz):
            return
        self.debug_rows.append(
            {
                "t": t,
                "phase": self.phase,
                "des_thr": float(msg.des_thr),
                "des_a_x": float(msg.des_a_x),
                "des_a_y": float(msg.des_a_y),
                "des_a_z": float(msg.des_a_z),
            }
        )

    def append_path(self, path: RosPath, x: float, y: float, z: float, t: float, max_points: int) -> None:
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
        if max_points > 0 and len(path.poses) > max_points:
            path.poses = path.poses[-max_points:]

    @staticmethod
    def quat_rotate(q: tuple[float, float, float, float], v: tuple[float, float, float]) -> tuple[float, float, float]:
        x, y, z, w = q
        vx, vy, vz = v
        tx = 2.0 * (y * vz - z * vy)
        ty = 2.0 * (z * vx - x * vz)
        tz = 2.0 * (x * vy - y * vx)
        return (
            vx + w * tx + (y * tz - z * ty),
            vy + w * ty + (z * tx - x * tz),
            vz + w * tz + (x * ty - y * tx),
        )

    def publish_body_axes(self) -> None:
        if self.last_truth is None:
            return
        pos = (self.last_truth["x"], self.last_truth["y"], self.last_truth["z"])
        q = self.last_truth.get("quat")
        if q is None:
            roll = self.last_truth["roll"]
            pitch = self.last_truth["pitch"]
            yaw = self.last_truth["yaw"]
            cy = math.cos(yaw * 0.5)
            sy = math.sin(yaw * 0.5)
            cp = math.cos(pitch * 0.5)
            sp = math.sin(pitch * 0.5)
            cr = math.cos(roll * 0.5)
            sr = math.sin(roll * 0.5)
            q = (
                sr * cp * cy - cr * sp * sy,
                cr * sp * cy + sr * cp * sy,
                cr * cp * sy - sr * sp * cy,
                cr * cp * cy + sr * sp * sy,
            )
        markers = MarkerArray()
        stamp = rospy.Time.now()
        marker_lifetime = rospy.Duration(0)
        axes = (
            (0, "body_x_forward", (1.0, 0.0, 0.0), (1.0, 0.05, 0.05, 1.0)),
            (1, "body_y_left", (0.0, 1.0, 0.0), (0.05, 1.0, 0.05, 1.0)),
            (2, "body_z_up", (0.0, 0.0, 1.0), (0.1, 0.35, 1.0, 1.0)),
        )
        for marker_id, name, axis, color in axes:
            direction = self.quat_rotate(q, axis)
            marker = Marker()
            marker.header.stamp = stamp
            marker.header.frame_id = self.args.path_frame
            marker.ns = name
            marker.id = marker_id
            marker.type = Marker.ARROW
            marker.action = Marker.ADD
            marker.points = [
                Point(x=pos[0], y=pos[1], z=pos[2]),
                Point(
                    x=pos[0] + direction[0] * self.args.body_axis_length_m,
                    y=pos[1] + direction[1] * self.args.body_axis_length_m,
                    z=pos[2] + direction[2] * self.args.body_axis_length_m,
                ),
            ]
            marker.scale.x = self.args.body_axis_shaft_m
            marker.scale.y = self.args.body_axis_head_diameter_m
            marker.scale.z = self.args.body_axis_head_length_m
            marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
            marker.lifetime = marker_lifetime
            markers.markers.append(marker)

        # Remove any airframe markers left by older mission-node instances.
        # The body-axis display remains available for pose/orientation review.
        for marker_id in range(10, 16):
            marker = Marker()
            marker.header.stamp = stamp
            marker.header.frame_id = self.args.path_frame
            marker.ns = "uav_airframe"
            marker.id = marker_id
            marker.action = Marker.DELETE
            markers.markers.append(marker)
        self.body_axes_pub.publish(markers)

    def publish_paths(self, publish_static_target: bool = True) -> None:
        now_t = self.now()
        min_period = 1.0 / max(1e-6, self.args.path_publish_hz)
        if now_t - self.last_record_t["path_publish"] < min_period:
            return
        self.last_record_t["path_publish"] = now_t
        stamp = rospy.Time.now()
        self.truth_path.header.stamp = stamp
        self.cmd_path.header.stamp = stamp
        self.truth_path_pub.publish(self.truth_path)
        self.cmd_path_pub.publish(self.cmd_path)
        self.publish_body_axes()
        # Interactive Goal4 target_path is owned by the clicked-goal adapter.
        # A second latched publisher would race the live aircraft-to-target
        # segment and could restore the line after the adapter clears it.
        if not publish_static_target or self.args.interactive_goal_review:
            return
        target_path = RosPath(header=Header(stamp=stamp, frame_id=self.args.path_frame))
        start_x, start_y, start_z = self.display_path_start()
        target_x, target_y, target_z = self.display_path_target()
        for x, y, z in [
            (start_x, start_y, start_z),
            (target_x, target_y, target_z),
        ]:
            ps = PoseStamped()
            ps.header = target_path.header
            ps.pose.position.x = x
            ps.pose.position.y = y
            ps.pose.position.z = z
            ps.pose.orientation.w = 1.0
            target_path.poses.append(ps)
        self.target_path_pub.publish(target_path)

    def display_path_start(self) -> tuple[float, float, float]:
        if self.last_path_odom is not None:
            position = self.last_path_odom.pose.pose.position
            return float(position.x), float(position.y), float(position.z)
        home_x, home_y = self.mission_home_xy if self.mission_home_xy else (0.0, 0.0)
        return home_x, home_y, self.takeoff_target_z_m()

    def display_path_target(self) -> tuple[float, float, float]:
        if self.last_forwarded_goal is not None:
            return (
                float(self.last_forwarded_goal["x"]),
                float(self.last_forwarded_goal["y"]),
                float(self.last_forwarded_goal["z"]),
            )
        return self.args.target_x, self.args.target_y, self.args.target_z

    @staticmethod
    def normalize_angle(angle: float) -> float:
        return math.atan2(math.sin(angle), math.cos(angle))

    def make_hover_cmd(
        self,
        x: float,
        y: float,
        z: float,
        yaw: float | None = None,
        yaw_dot: float = 0.0,
    ) -> PositionCommand:
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.control_frame_id()
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        msg.trajectory_id = 0
        msg.position.x = x
        msg.position.y = y
        msg.position.z = z
        msg.yaw = self.args.yaw if yaw is None else yaw
        msg.yaw_dot = yaw_dot
        return msg

    def publish_hover_cmd(self, x: float, y: float, z: float, yaw: float | None = None) -> None:
        self.hover_cmd_pub.publish(self.make_hover_cmd(x, y, z, yaw))
        self.hover_cmd_publish_count += 1

    def control_frame_id(self) -> str:
        if self.last_odom is not None:
            frame_id = str(self.last_odom.get("frame_id") or "")
            if frame_id:
                return frame_id
        return self.args.control_frame

    def takeoff_target_z_m(self) -> float:
        """Return the absolute odom z targeted by px4ctrl auto-takeoff."""
        if self.home_odom_z is None:
            return float(self.args.takeoff_height)
        return float(self.home_odom_z) + float(self.args.takeoff_height)

    def can_publish_takeoff_hover(self) -> bool:
        if not self.last_state:
            return False
        return bool(self.last_state.armed) or str(self.last_state.mode).upper() == "OFFBOARD"

    def publish_scan_hover_cmd(self, x: float, y: float, z: float, yaw: float, yaw_dot: float) -> None:
        self.hover_cmd_pub.publish(self.make_hover_cmd(x, y, z, yaw, yaw_dot))
        self.hover_cmd_publish_count += 1

    def run_interactive_yaw_scan(self, reason: str) -> dict:
        event = {
            "reason": reason,
            "enabled": bool(self.args.interactive_yaw_scan_enable),
            "start_t": self.now(),
            "end_t": None,
            "ok": True,
            "blockers": [],
            "command_count": 0,
            "settle_count": 0,
            "delta_rad": self.args.interactive_yaw_scan_delta_rad,
            "duration_s": self.args.interactive_yaw_scan_duration_s,
            "settle_s": self.args.interactive_yaw_scan_settle_s,
            "disable_cmd_adapter": self.args.interactive_yaw_scan_disable_cmd_adapter,
            "reenable_cmd_adapter": self.args.interactive_yaw_scan_reenable_cmd_adapter,
        }
        if not self.args.interactive_yaw_scan_enable:
            event["end_t"] = self.now()
            self.interactive_yaw_scan_events.append(event)
            return event
        if self.last_odom is None:
            event["ok"] = False
            event["blockers"] = ["interactive_yaw_scan_odom_missing"]
            event["end_t"] = self.now()
            self.interactive_yaw_scan_events.append(event)
            return event

        row = self.last_odom
        hold_x = float(row["x"])
        hold_y = float(row["y"])
        hold_z = float(row["z"])
        start_yaw = float(row["yaw"])
        duration_s = max(0.1, float(self.args.interactive_yaw_scan_duration_s))
        settle_s = max(0.0, float(self.args.interactive_yaw_scan_settle_s))
        delta_rad = float(self.args.interactive_yaw_scan_delta_rad)
        yaw_rate = delta_rad / duration_s
        final_yaw = self.normalize_angle(start_yaw + delta_rad)
        event.update(
            {
                "hold_xyz": [hold_x, hold_y, hold_z],
                "start_yaw": start_yaw,
                "final_yaw": final_yaw,
                "yaw_rate_radps": yaw_rate,
            }
        )

        self.set_interactive_goal_ready(False, repeats=2)
        if self.args.interactive_yaw_scan_disable_cmd_adapter:
            self.set_cmd_adapter_enabled(False)

        previous_phase = self.phase
        self.phase = "interactive_yaw_scan"
        rate = rospy.Rate(max(1.0, self.args.hover_publish_hz))
        scan_start = time.time()
        while not rospy.is_shutdown() and time.time() - scan_start < duration_s:
            alpha = max(0.0, min(1.0, (time.time() - scan_start) / duration_s))
            yaw = self.normalize_angle(start_yaw + delta_rad * alpha)
            self.publish_scan_hover_cmd(hold_x, hold_y, hold_z, yaw, yaw_rate)
            event["command_count"] += 1
            self.publish_paths(publish_static_target=False)
            safety_blockers = self.flight_safety_blockers("interactive_yaw_scan")
            if safety_blockers:
                event["ok"] = False
                event["blockers"] = safety_blockers
                break
            rate.sleep()

        if event["ok"]:
            settle_start = time.time()
            while not rospy.is_shutdown() and time.time() - settle_start < settle_s:
                self.publish_scan_hover_cmd(hold_x, hold_y, hold_z, final_yaw, 0.0)
                event["settle_count"] += 1
                self.publish_paths(publish_static_target=False)
                safety_blockers = self.flight_safety_blockers("interactive_yaw_scan")
                if safety_blockers:
                    event["ok"] = False
                    event["blockers"] = safety_blockers
                    break
                rate.sleep()

        if event["ok"]:
            self.interactive_hover_yaw = final_yaw
        if (
            self.args.interactive_yaw_scan_disable_cmd_adapter
            and self.args.interactive_yaw_scan_reenable_cmd_adapter
        ):
            self.set_cmd_adapter_enabled(True)
        self.phase = previous_phase
        event["end_t"] = self.now()
        self.interactive_yaw_scan_events.append(event)
        return event

    def publish_takeoff_land(self, cmd: int, repeats: int = 8) -> None:
        msg = TakeoffLand()
        msg.takeoff_land_cmd = cmd
        for _ in range(repeats):
            if rospy.is_shutdown():
                break
            self.takeoff_land_pub.publish(msg)
            if cmd == TakeoffLand.TAKEOFF:
                self.takeoff_cmd_publish_count += 1
            elif cmd == TakeoffLand.LAND:
                self.land_cmd_publish_count += 1
            try:
                rospy.sleep(0.1)
            except rospy.exceptions.ROSInterruptException:
                break

    def has_armed_or_started_rising(self) -> bool:
        if self.last_state is not None and self.last_state.armed:
            return True
        if self.last_odom is None or self.home_odom_z is None:
            return False
        return float(self.last_odom["z"]) - self.home_odom_z >= self.args.takeoff_rise_detect_m

    def maybe_retry_takeoff_command(self, last_retry_wall: float, retry_count: int) -> tuple[float, int]:
        if self.args.takeoff_retry_interval_s <= 0.0 or self.args.takeoff_retry_max <= 0:
            return last_retry_wall, retry_count
        if self.has_armed_or_started_rising():
            return last_retry_wall, retry_count
        if retry_count >= self.args.takeoff_retry_max:
            return last_retry_wall, retry_count
        now_wall = time.time()
        if now_wall - last_retry_wall < self.args.takeoff_retry_interval_s:
            return last_retry_wall, retry_count
        self.publish_takeoff_land(TakeoffLand.TAKEOFF, repeats=self.args.takeoff_retry_repeats)
        return now_wall, retry_count + 1

    def set_cmd_adapter_enabled(self, enabled: bool, repeats: int = 3) -> None:
        self.cmd_adapter_enabled = enabled
        msg = Bool(data=enabled)
        for _ in range(repeats):
            if rospy.is_shutdown():
                break
            self.cmd_adapter_enable_pub.publish(msg)
            try:
                rospy.sleep(0.05)
            except rospy.exceptions.ROSInterruptException:
                break

    def set_interactive_goal_ready(self, ready: bool, repeats: int = 3) -> None:
        msg = Bool(data=ready)
        for _ in range(repeats):
            if rospy.is_shutdown():
                break
            self.interactive_goal_ready_pub.publish(msg)
            try:
                rospy.sleep(0.05)
            except rospy.exceptions.ROSInterruptException:
                break

    @staticmethod
    def row_speed(row: dict) -> float:
        return math.sqrt(row["vx"] * row["vx"] + row["vy"] * row["vy"] + row["vz"] * row["vz"])

    @staticmethod
    def xy_distance(row: dict, xy: tuple[float, float]) -> float:
        return math.hypot(row["x"] - xy[0], row["y"] - xy[1])

    @staticmethod
    def z_error(row: dict, z_ref: float) -> float:
        return row["z"] - z_ref

    def target_state_snapshot(self, row: dict | None = None) -> dict | None:
        row = row or self.last_odom
        if row is None:
            return None
        target = (self.args.target_x, self.args.target_y, self.args.target_z)
        return self.state_snapshot_to_target(row, target)

    def state_snapshot_to_target(self, row: dict, target: tuple[float, float, float]) -> dict:
        error_xy = math.dist((row["x"], row["y"]), target[:2])
        error_z = row["z"] - target[2]
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
            "error_xyz_m": math.dist((row["x"], row["y"], row["z"]), target),
            "error_xy_m": error_xy,
            "error_z_m": error_z,
            "speed_mps": self.row_speed(row),
            "abs_vz_mps": abs(row["vz"]),
            "abs_roll_pitch_deg": math.degrees(max(abs(row["roll"]), abs(row["pitch"]))),
        }

    def interactive_goal_state_row(self, goal_frame_id: str, preferred_row: dict | None = None) -> dict | None:
        candidates = (self.last_path_odom_row, preferred_row, self.last_odom)
        for candidate in candidates:
            if candidate is not None and str(candidate.get("frame_id") or "") == goal_frame_id:
                self.last_interactive_goal_frame_issue = None
                return candidate
        self.last_interactive_goal_frame_issue = {
            "reason_code": "interactive_goal_state_frame_mismatch",
            "goal_frame_id": goal_frame_id,
            "available_state_frames": [
                str(candidate.get("frame_id") or "")
                for candidate in candidates
                if candidate is not None
            ],
        }
        return None

    def interactive_goal_snapshot(self, row: dict | None = None) -> dict | None:
        if self.last_forwarded_goal is None:
            return None
        goal = self.last_forwarded_goal
        goal_frame_id = str(goal.get("frame_id") or self.args.path_frame)
        state_row = self.interactive_goal_state_row(goal_frame_id, preferred_row=row)
        if state_row is None:
            return None
        snapshot = self.state_snapshot_to_target(
            state_row,
            (float(goal["x"]), float(goal["y"]), float(goal["z"])),
        )
        snapshot["state_frame_id"] = str(state_row.get("frame_id") or "")
        snapshot["goal_frame_id"] = goal_frame_id
        return snapshot

    def interactive_goal_reached(self) -> bool:
        snapshot = self.interactive_goal_snapshot()
        if snapshot is None:
            return False
        return bool(
            snapshot["error_xy_m"] <= self.args.interactive_target_reached_xy_m
            and abs(snapshot["error_z_m"]) <= self.args.interactive_target_reached_z_m
            and snapshot["speed_mps"] <= self.args.interactive_target_hold_max_speed_mps
            and snapshot["abs_vz_mps"] <= self.args.interactive_target_hold_max_vz_mps
            and snapshot["abs_roll_pitch_deg"] <= self.args.interactive_target_hold_max_roll_pitch_deg
        )

    def publish_interactive_hover_handoff(self, snapshot: dict, goal_seq: int) -> dict:
        control_snapshot = self.last_odom
        if control_snapshot is None:
            return {
                "goal_seq": goal_seq,
                "handoff_t": self.now(),
                "status": "blocked",
                "reason_code": "interactive_handoff_local_odom_missing",
            }
        hold_x = float(control_snapshot["x"])
        hold_y = float(control_snapshot["y"])
        hold_z = float(control_snapshot["z"])
        hold_yaw = float(control_snapshot.get("yaw", self.args.yaw))
        adapter_hold = self.args.interactive_handoff_mode == "adapter_hold"
        if adapter_hold:
            rospy.sleep(self.args.interactive_post_adapter_disable_wait_s)
        else:
            self.set_cmd_adapter_enabled(False)
            # direct_hover is an explicit handoff back to this mission node.
            self.hover_cmd_publisher_released = False
            rospy.sleep(self.args.interactive_post_adapter_disable_wait_s)
            for _ in range(max(1, self.args.interactive_handoff_hover_repeats)):
                self.publish_hover_cmd(hold_x, hold_y, hold_z, hold_yaw)
                rospy.sleep(1.0 / max(1.0, self.args.hover_publish_hz))
        metric = {
            "goal_seq": goal_seq,
            "handoff_t": self.now(),
            "hold_xyz": [hold_x, hold_y, hold_z],
            "hold_yaw": hold_yaw,
            "snapshot": snapshot,
            "control_frame_id": self.control_frame_id(),
            "adapter_disabled": not adapter_hold,
            "mode": self.args.interactive_handoff_mode,
        }
        metric["hold_time_basis"] = "ros_sim_time"
        self.interactive_goal_handoff_metrics.append(metric)
        return metric

    def pre_diff_stability_snapshot(self, home_x: float, home_y: float) -> dict:
        now_t = self.now()
        reasons: list[str] = []
        snapshot: dict = {
            "t": now_t,
            "phase": self.phase,
            "required_stable_s": max(self.args.pre_ego_hover_s, self.args.pre_diff_stable_s),
            "thresholds": {
                "odom_timeout_s": self.args.pre_diff_odom_timeout_s,
                "max_xy_error_m": self.args.pre_diff_max_xy_error_m,
                "max_z_error_m": self.args.pre_diff_max_z_error_m,
                "max_speed_mps": self.args.pre_diff_max_speed_mps,
                "max_vz_mps": self.args.pre_diff_max_vz_mps,
                "max_roll_pitch_deg": self.args.pre_diff_max_roll_pitch_deg,
                "truth_max_xy_error_m": self.args.pre_diff_truth_max_xy_error_m,
                "truth_max_z_error_m": self.args.pre_diff_truth_max_z_error_m,
                "truth_max_speed_mps": self.args.pre_diff_truth_max_speed_mps,
                "truth_max_vz_mps": self.args.pre_diff_truth_max_vz_mps,
                "truth_max_roll_pitch_deg": self.args.pre_diff_truth_max_roll_pitch_deg,
            },
        }

        if self.last_odom is None:
            reasons.append("odom_missing")
        else:
            odom_age = now_t - self.last_odom["t"]
            odom_xy_error = self.xy_distance(self.last_odom, (home_x, home_y))
            odom_z_error = self.z_error(self.last_odom, self.takeoff_target_z_m())
            odom_speed = self.row_speed(self.last_odom)
            odom_abs_vz = abs(self.last_odom["vz"])
            odom_abs_roll_pitch_deg = math.degrees(max(abs(self.last_odom["roll"]), abs(self.last_odom["pitch"])))
            snapshot["odom"] = {
                "age_s": odom_age,
                "x": self.last_odom["x"],
                "y": self.last_odom["y"],
                "z": self.last_odom["z"],
                "xy_error_m": odom_xy_error,
                "z_error_m": odom_z_error,
                "speed_mps": odom_speed,
                "abs_vz_mps": odom_abs_vz,
                "abs_roll_pitch_deg": odom_abs_roll_pitch_deg,
            }
            if odom_age > self.args.pre_diff_odom_timeout_s:
                reasons.append(f"odom_stale:{odom_age:.3f}")
            if odom_xy_error > self.args.pre_diff_max_xy_error_m:
                reasons.append(f"odom_xy_error:{odom_xy_error:.3f}")
            if abs(odom_z_error) > self.args.pre_diff_max_z_error_m:
                reasons.append(f"odom_z_error:{odom_z_error:.3f}")
            if odom_speed > self.args.pre_diff_max_speed_mps:
                reasons.append(f"odom_speed:{odom_speed:.3f}")
            if odom_abs_vz > self.args.pre_diff_max_vz_mps:
                reasons.append(f"odom_vz:{odom_abs_vz:.3f}")
            if odom_abs_roll_pitch_deg > self.args.pre_diff_max_roll_pitch_deg:
                reasons.append(f"odom_roll_pitch:{odom_abs_roll_pitch_deg:.3f}")

        if self.args.pre_diff_require_truth_gate:
            truth_ref = self.last_sunray_truth or self.last_truth
            if truth_ref is None:
                reasons.append("truth_missing")
            else:
                truth_home = self.truth_home or self.home
                truth_xy_error = None
                truth_z_error = None
                if truth_home is not None:
                    truth_xy_error = self.xy_distance(truth_ref, (truth_home[0], truth_home[1]))
                    truth_z_error = self.z_error(truth_ref, truth_home[2] + self.args.takeoff_height)
                truth_speed = self.row_speed(truth_ref)
                truth_abs_vz = abs(truth_ref["vz"])
                truth_abs_roll_pitch_deg = math.degrees(max(abs(truth_ref["roll"]), abs(truth_ref["pitch"])))
                snapshot["truth"] = {
                    "source": "sunray_truth" if self.last_sunray_truth is not None else "gazebo_model_states",
                    "x": truth_ref["x"],
                    "y": truth_ref["y"],
                    "z": truth_ref["z"],
                    "xy_error_m": truth_xy_error,
                    "z_error_m": truth_z_error,
                    "speed_mps": truth_speed,
                    "abs_vz_mps": truth_abs_vz,
                    "abs_roll_pitch_deg": truth_abs_roll_pitch_deg,
                }
                if truth_xy_error is not None and truth_xy_error > self.args.pre_diff_truth_max_xy_error_m:
                    reasons.append(f"truth_xy_error:{truth_xy_error:.3f}")
                if truth_z_error is not None and abs(truth_z_error) > self.args.pre_diff_truth_max_z_error_m:
                    reasons.append(f"truth_z_error:{truth_z_error:.3f}")
                if truth_speed > self.args.pre_diff_truth_max_speed_mps:
                    reasons.append(f"truth_speed:{truth_speed:.3f}")
                if truth_abs_vz > self.args.pre_diff_truth_max_vz_mps:
                    reasons.append(f"truth_vz:{truth_abs_vz:.3f}")
                if truth_abs_roll_pitch_deg > self.args.pre_diff_truth_max_roll_pitch_deg:
                    reasons.append(f"truth_roll_pitch:{truth_abs_roll_pitch_deg:.3f}")

        snapshot["ok"] = not reasons
        snapshot["reasons"] = reasons
        self.last_pre_diff_gate = snapshot
        self.pre_diff_gate_history.append(snapshot)
        if len(self.pre_diff_gate_history) > self.args.pre_diff_history_limit:
            self.pre_diff_gate_history = self.pre_diff_gate_history[-self.args.pre_diff_history_limit :]
        return snapshot

    def truth_odom_relative_z_state(self) -> dict | None:
        if (
            self.last_truth is None
            or self.last_odom is None
            or self.truth_home is None
            or self.home_odom_z is None
        ):
            return None
        truth_z_rel_m = float(self.last_truth["z"] - self.truth_home[2])
        odom_z_rel_m = float(self.last_odom["z"] - self.home_odom_z)
        return {
            "truth_z_rel_m": truth_z_rel_m,
            "odom_z_rel_m": odom_z_rel_m,
            "error_m": truth_z_rel_m - odom_z_rel_m,
        }

    def flight_safety_blockers(self, prefix: str) -> list[str]:
        blockers: list[str] = []
        snapshot: dict = {
            "t": self.now(),
            "phase": self.phase,
            "prefix": prefix,
            "thresholds": {
                "min_truth_z_m": self.args.execute_min_truth_z_m,
                "min_odom_z_m": self.args.execute_min_odom_z_m,
                "max_roll_pitch_deg": self.args.execute_max_roll_pitch_deg,
                "max_truth_odom_z_error_m": self.args.execute_max_truth_odom_z_error_m,
            },
        }

        checks = (
            ("truth", self.last_truth, self.args.execute_min_truth_z_m),
            ("odom", self.last_odom, self.args.execute_min_odom_z_m),
        )
        for source, row, min_z in checks:
            if row is None:
                blockers.append(f"{prefix}_{source}_missing")
                snapshot[source] = {"missing": True}
                continue
            abs_roll_pitch_deg = math.degrees(max(abs(row["roll"]), abs(row["pitch"])))
            item = {
                "t": row["t"],
                "x": row["x"],
                "y": row["y"],
                "z": row["z"],
                "vx": row["vx"],
                "vy": row["vy"],
                "vz": row["vz"],
                "roll": row["roll"],
                "pitch": row["pitch"],
                "yaw": row["yaw"],
                "speed_mps": self.row_speed(row),
                "abs_vz_mps": abs(row["vz"]),
                "abs_roll_pitch_deg": abs_roll_pitch_deg,
            }
            snapshot[source] = item
            if min_z > 0.0 and row["z"] < min_z:
                blockers.append(f"{prefix}_{source}_z_below_gate")
            if self.args.execute_max_roll_pitch_deg > 0.0 and abs_roll_pitch_deg > self.args.execute_max_roll_pitch_deg:
                blockers.append(f"{prefix}_{source}_roll_pitch_above_gate")

        relative_z_state = self.truth_odom_relative_z_state()
        snapshot["truth_odom_relative_z"] = relative_z_state
        if (
            relative_z_state is not None
            and self.args.execute_max_truth_odom_z_error_m > 0.0
            and abs(relative_z_state["error_m"]) > self.args.execute_max_truth_odom_z_error_m
        ):
            blockers.append(f"{prefix}_truth_odom_z_divergence_above_gate")

        if blockers:
            snapshot["blockers"] = blockers
            self.flight_safety_violation = snapshot
        return blockers

    def publish_trigger(self) -> None:
        home_x, home_y = self.mission_home_xy if self.mission_home_xy else (0.0, 0.0)
        self.pre_diff_trigger_snapshot = self.pre_diff_stability_snapshot(home_x, home_y)
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.pose.position.x = self.args.target_x
        msg.pose.position.y = self.args.target_y
        msg.pose.position.z = self.args.target_z
        msg.pose.orientation.w = 1.0
        for _ in range(self.args.goal_trigger_repeats):
            self.trigger_pub.publish(msg)
            if self.goal_pose_pub is not None:
                self.goal_pose_pub.publish(msg)
            rospy.sleep(0.1)
        if self.goalset_pub is not None:
            goal = GoalSet()
            goal.drone_id = self.args.drone_id
            goal.goal[0] = self.args.target_x
            goal.goal[1] = self.args.target_y
            goal.goal[2] = self.args.target_z
            for _ in range(self.args.goal_trigger_repeats):
                self.goalset_pub.publish(goal)
                rospy.sleep(0.1)

    def first_planner_trajectory_time(self) -> float | None:
        times = [t for t in (self.first_bspline_t, self.first_polytraj_t) if t is not None]
        return min(times) if times else None

    def first_planner_takeover_time(self) -> float | None:
        times = [
            t
            for t in (self.first_bspline_t, self.first_polytraj_t, self.first_planner_position_cmd_t)
            if t is not None
        ]
        return min(times) if times else None

    def wait_for_ready(self) -> bool:
        deadline = time.time() + self.args.ready_timeout_s
        rate = rospy.Rate(20)
        while not rospy.is_shutdown() and time.time() < deadline:
            if self.safe_stop.requested():
                return False
            self.publish_paths()
            if (
                self.last_state
                and self.last_state.connected
                and self.last_odom
                and self.last_truth
                and self.takeoff_land_pub.get_num_connections() > 0
            ):
                return True
            rate.sleep()
        return False

    def wall_sleep_once(self) -> None:
        interval_s = 1.0 / max(1.0, float(self.args.hover_publish_hz))
        time.sleep(max(0.005, min(0.1, interval_s)))

    def exploration_elapsed_s(self, start_ros: float, start_wall: float) -> float:
        if self.args.exploration_time_basis == "wall":
            return time.time() - start_wall
        return self.now() - start_ros

    def truth_home_z_m(self) -> float | None:
        if self.truth_home is not None:
            return float(self.truth_home[2])
        if self.home is not None:
            return float(self.home[2])
        return None

    def truth_z_rel_m(self) -> float | None:
        if self.last_truth is None:
            return None
        home_z = self.truth_home_z_m()
        if home_z is None:
            return None
        return float(self.last_truth["z"] - home_z)

    def land_and_finish(self, rate: rospy.Rate) -> int:
        self.phase = "land"
        if self.args.disable_cmd_adapter_before_land:
            self.set_cmd_adapter_enabled(False)
            try:
                rospy.sleep(self.args.post_adapter_disable_wait_s)
            except rospy.exceptions.ROSInterruptException:
                pass
        self.publish_takeoff_land(TakeoffLand.LAND, repeats=self.args.land_cmd_repeats)
        land_start_wall = time.time()
        land_start_ros = self.now()
        landed_by_truth = False
        landed_truth_z_rel_m = None
        landed_stable_since: float | None = None
        while not rospy.is_shutdown() and self.now() - land_start_ros < self.args.land_timeout_s:
            self.publish_paths()
            landed_truth_z_rel_m = self.truth_z_rel_m()
            landed_snapshot = self.target_state_snapshot(self.last_truth) if self.last_truth else None
            height_ok = (
                landed_truth_z_rel_m is not None
                and landed_truth_z_rel_m <= self.args.landed_z_max
            )
            speed_ok = (
                landed_snapshot is not None
                and landed_snapshot["speed_mps"] <= self.args.landed_max_speed_mps
                and landed_snapshot["abs_vz_mps"] <= self.args.landed_max_vz_mps
            )
            attitude_ok = (
                landed_snapshot is not None
                and landed_snapshot["abs_roll_pitch_deg"]
                <= self.args.landed_max_roll_pitch_deg
            )
            disarmed_ok = bool(self.last_state and not self.last_state.armed)
            if height_ok and speed_ok and attitude_ok and disarmed_ok:
                if landed_stable_since is None:
                    landed_stable_since = self.now()
                if self.now() - landed_stable_since >= self.args.landed_stable_s:
                    landed_by_truth = True
                    break
            else:
                landed_stable_since = None
            self.wall_sleep_once()
        self.land_metrics = {
            "landed_by_truth": landed_by_truth,
            "landed_check": "gazebo_truth_relative_to_home_z",
            "landed_z_max_m": self.args.landed_z_max,
            "landed_max_speed_mps": self.args.landed_max_speed_mps,
            "landed_max_vz_mps": self.args.landed_max_vz_mps,
            "landed_max_roll_pitch_deg": self.args.landed_max_roll_pitch_deg,
            "landed_stable_s": self.args.landed_stable_s,
            "disarmed": bool(self.last_state and not self.last_state.armed),
            "truth_home_z_m": self.truth_home_z_m(),
            "truth_z_rel_m": landed_truth_z_rel_m,
            "duration_s": self.now() - land_start_ros,
            "wall_duration_s": time.time() - land_start_wall,
            "truth_snapshot": self.target_state_snapshot(self.last_truth) if self.last_truth else None,
            "odom_snapshot": self.target_state_snapshot(self.last_odom) if self.last_odom else None,
        }

        self.phase = "done"
        acceptance_blockers = self.acceptance_blockers()
        if acceptance_blockers:
            self.write_outputs(status="blocked", blockers=acceptance_blockers)
            return 14
        self.write_outputs(status="passed", blockers=[])
        return 0

    def abort_for_flight_safety(self, rate: rospy.Rate, blockers: list[str]) -> int:
        self.set_interactive_goal_ready(False)
        return self.perform_safe_stop(rate, safety_blockers=list(blockers))

    def perform_safe_stop(self, rate: rospy.Rate, safety_blockers: list[str] | None = None) -> int:
        self.safe_stop.acknowledge("quiescing", 20)
        self.set_cmd_adapter_enabled(False)
        self.phase = "safe_stop_hover"
        self.safe_stop.acknowledge("hovering", 40)
        hover_deadline = time.time() + 1.0
        while not rospy.is_shutdown() and time.time() < hover_deadline:
            if self.last_odom:
                self.publish_hover_cmd(
                    self.last_odom["x"], self.last_odom["y"], self.last_odom["z"], self.last_odom["yaw"]
                )
            self.publish_paths(publish_static_target=False)
            self.wall_sleep_once()
        self.safe_stop.acknowledge("landing", 65)
        self.land_and_finish(rate)
        disarmed = bool(self.land_metrics and self.land_metrics.get("disarmed"))
        if disarmed:
            self.safe_stop.acknowledge("disarmed", 90)
        self.safe_stop.acknowledge(
            "completed" if disarmed else "failed",
            100,
            terminal=True,
            accepted=disarmed,
            reason_code="safe_stop_completed" if disarmed else "safe_stop_disarm_not_confirmed",
            detail={"landing": self.land_metrics or {}},
        )
        final_blockers = list(safety_blockers or [])
        if not disarmed:
            final_blockers.append("safe_stop_disarm_not_confirmed")
        self.write_outputs(
            status="blocked" if final_blockers else "safe_stopped",
            blockers=final_blockers,
        )
        if safety_blockers:
            return 15 if disarmed else 16
        return 0 if disarmed else 16

    def takeoff_status_summary(self) -> dict:
        state_rows = self.rows_in_phases(self.state_rows, {"takeoff"})
        odom_rows = self.rows_in_phases(self.odom_rows, {"takeoff"})
        truth_rows = self.rows_in_phases(self.truth_rows, {"takeoff"})
        target_z = self.takeoff_target_z_m()
        max_odom_z = max((float(row["z"]) for row in odom_rows), default=None)
        max_truth_z = max((float(row["z"]) for row in truth_rows), default=None)
        return {
            "target_z_m": target_z,
            "target_z_semantics": "px4ctrl auto-takeoff uses home_odom_z + --takeoff-height in MAVROS local odom.",
            "takeoff_cmd_publish_count": self.takeoff_cmd_publish_count,
            "land_cmd_publish_count": self.land_cmd_publish_count,
            "state_samples": len(state_rows),
            "armed_observed": any(bool(row["armed"]) for row in state_rows)
            or bool(self.last_state and self.last_state.armed),
            "offboard_observed": any("OFFBOARD" in str(row["mode"]).upper() for row in state_rows),
            "mode_values": sorted({str(row["mode"]) for row in state_rows if row.get("mode")}),
            "last_state": None if not self.state_rows else self.state_rows[-1],
            "home_odom_z_m": self.home_odom_z,
            "max_odom_z_m": max_odom_z,
            "max_truth_z_m": max_truth_z,
            "odom_height_error_to_target_m": None if max_odom_z is None else target_z - max_odom_z,
            "truth_height_error_to_target_m": None if max_truth_z is None else target_z - max_truth_z,
        }

    def takeoff_blockers(self) -> list[str]:
        blockers: list[str] = []
        status = self.takeoff_status_summary()
        if not status["offboard_observed"]:
            blockers.append("offboard_not_observed")
        if not status["armed_observed"]:
            blockers.append("arm_rejected_or_not_armed")
        max_odom_z = status["max_odom_z_m"]
        if max_odom_z is None or abs(max_odom_z - status["target_z_m"]) >= self.args.takeoff_z_tol:
            blockers.append("takeoff_height_not_reached")
        return blockers or ["takeoff_height_not_reached"]

    def run(self) -> int:
        rate = rospy.Rate(self.args.hover_publish_hz)
        self.set_interactive_goal_ready(False, repeats=1)
        if not self.wait_for_ready():
            if self.safe_stop.requested():
                return self.perform_safe_stop(rate)
            self.write_outputs(status="blocked", blockers=["ready_timeout"])
            return 10
        if not self.last_odom:
            self.write_outputs(status="blocked", blockers=["home_odom_missing"])
            return 10

        home_x = float(self.last_odom["x"])
        home_y = float(self.last_odom["y"])
        self.home_odom_z = float(self.last_odom["z"])
        self.mission_home_xy = (home_x, home_y)
        if self.truth_home is None and self.last_truth is not None:
            self.truth_home = (float(self.last_truth["x"]), float(self.last_truth["y"]), float(self.last_truth["z"]))
        if self.home is None and self.last_truth is not None:
            self.home = (float(self.last_truth["x"]), float(self.last_truth["y"]), float(self.last_truth["z"]))

        self.phase = "takeoff"
        self.publish_takeoff_land(TakeoffLand.TAKEOFF, repeats=self.args.takeoff_cmd_repeats)
        hover_start = time.time()
        last_retry_wall = hover_start
        retry_count = 0
        hover_reached_time: float | None = None
        stable_reached_motion_time: float | None = None
        hover_height_satisfied = False
        stable_satisfied = False
        required_stable_s = max(self.args.pre_ego_hover_s, self.args.pre_diff_stable_s)
        while not rospy.is_shutdown() and time.time() - hover_start < self.args.takeoff_timeout_s:
            if self.safe_stop.requested():
                return self.perform_safe_stop(rate)
            last_retry_wall, retry_count = self.maybe_retry_takeoff_command(last_retry_wall, retry_count)
            if (
                self.args.publish_hover_during_takeoff
                and time.time() - hover_start >= self.args.publish_hover_during_takeoff_delay_s
                and self.can_publish_takeoff_hover()
            ):
                self.publish_hover_cmd(home_x, home_y, self.takeoff_target_z_m())
            self.publish_paths()
            stable_snapshot = self.pre_diff_stability_snapshot(home_x, home_y)
            if self.last_odom and abs(self.last_odom["z"] - self.takeoff_target_z_m()) < self.args.takeoff_z_tol:
                if hover_reached_time is None:
                    hover_reached_time = time.time()
                hover_height_satisfied = True
            else:
                hover_reached_time = None
                hover_height_satisfied = False
            if stable_snapshot["ok"]:
                # Stability thresholds are sampled in ROS simulation time.
                # Measuring the dwell with wall time shortens it whenever
                # Gazebo runs below real time and can hand control to the
                # planner while the vehicle is still climbing.
                now_motion = self.now()
                if stable_reached_motion_time is None:
                    stable_reached_motion_time = now_motion
                if now_motion - stable_reached_motion_time >= required_stable_s:
                    stable_satisfied = True
                    break
            else:
                stable_reached_motion_time = None
                stable_satisfied = False
            rate.sleep()

        if not hover_height_satisfied:
            self.write_outputs(status="blocked", blockers=self.takeoff_blockers())
            return 11
        if not stable_satisfied:
            self.write_outputs(status="blocked", blockers=["pre_diff_hover_not_stable"])
            return 11

        if self.args.interactive_goal_review:
            self.phase = "interactive_goal_review"
            initial_scan = self.run_interactive_yaw_scan("initial_ready")
            if not initial_scan.get("ok", False):
                return self.abort_for_flight_safety(rate, list(initial_scan.get("blockers", [])))
            self.set_interactive_goal_ready(True)
            if self.args.publish_goal_in_interactive_review:
                self.publish_trigger()
            review_start = time.time()
            review_has_deadline = self.args.interactive_review_hold_s > 0.0
            active_goal_seq = self.forwarded_goal_seq
            reached_since: float | None = None
            handoff_goal_seq: int | None = None
            handoff_hover_cmd: tuple[float, float, float, float] | None = None
            final_stable_since: float | None = None
            while (
                not rospy.is_shutdown()
                and (not review_has_deadline or time.time() - review_start < self.args.interactive_review_hold_s)
            ):
                if self.safe_stop.requested():
                    self.set_interactive_goal_ready(False)
                    return self.perform_safe_stop(rate)
                mission_owns_position_command = not self.hover_cmd_publisher_released
                if self.forwarded_goal_seq > active_goal_seq:
                    active_goal_seq = self.forwarded_goal_seq
                    reached_since = None
                    handoff_goal_seq = None
                    handoff_hover_cmd = None
                    final_stable_since = None
                    self.interactive_final_hover_metrics = None
                    self.set_cmd_adapter_enabled(True)
                    self.interactive_goal_metrics[str(active_goal_seq)] = {
                        "goal_seq": active_goal_seq,
                        "goal": self.last_forwarded_goal,
                        "started_t": self.now(),
                        "handoff": None,
                        "hold_time_basis": "ros_sim_time",
                        "last_snapshot": None,
                    }
                if self.last_forwarded_goal is None or handoff_goal_seq == active_goal_seq:
                    if mission_owns_position_command:
                        if handoff_hover_cmd is not None and self.args.interactive_handoff_mode != "adapter_hold":
                            self.publish_hover_cmd(*handoff_hover_cmd)
                        elif handoff_hover_cmd is None:
                            self.publish_hover_cmd(
                                home_x, home_y, self.takeoff_target_z_m(), self.interactive_hover_yaw
                            )
                elif self.first_planner_takeover_time() is None:
                    if mission_owns_position_command:
                        self.publish_hover_cmd(
                            home_x, home_y, self.takeoff_target_z_m(), self.interactive_hover_yaw
                        )
                else:
                    # The planner adapter is now the sole /position_cmd owner.
                    # Keep this release sticky across subsequent interactive goals.
                    self.hover_cmd_publisher_released = True
                    snapshot = self.interactive_goal_snapshot()
                    if snapshot is not None:
                        metric = self.interactive_goal_metrics.setdefault(
                            str(active_goal_seq),
                            {
                                "goal_seq": active_goal_seq,
                                "goal": self.last_forwarded_goal,
                                "started_t": self.now(),
                                "handoff": None,
                                "hold_time_basis": "ros_sim_time",
                                "last_snapshot": None,
                            },
                        )
                        metric["last_snapshot"] = snapshot
                        if self.interactive_goal_reached():
                            if reached_since is None:
                                reached_since = self.now()
                                metric["hold_start_t"] = snapshot["t"]
                            metric["hold_duration_s"] = self.now() - reached_since
                            if metric["hold_duration_s"] >= self.args.interactive_target_hold_s:
                                handoff = self.publish_interactive_hover_handoff(snapshot, active_goal_seq)
                                if handoff.get("status") == "blocked":
                                    return self.abort_for_flight_safety(
                                        rate,
                                        [str(handoff["reason_code"])],
                                    )
                                metric["handoff"] = handoff
                                handoff_goal_seq = active_goal_seq
                                handoff_hover_cmd = tuple(handoff["hold_xyz"]) + (float(handoff["hold_yaw"]),)
                                final_stable_since = None
                                self.interactive_final_hover_metrics = {
                                    "goal_seq": active_goal_seq,
                                    "target": self.last_forwarded_goal,
                                    "required_s": self.args.interactive_final_hover_hold_s,
                                    "time_basis": "ros_sim_time",
                                    "reached": False,
                                    "handoff_t": handoff.get("handoff_t"),
                                    "hold_start_t": None,
                                    "hold_end_t": None,
                                    "duration_s": 0.0,
                                    "first_snapshot": None,
                                    "last_snapshot": None,
                                    "end_snapshot": None,
                                    "max_error_xyz_m": 0.0,
                                    "max_error_xy_m": 0.0,
                                    "max_abs_z_error_m": 0.0,
                                    "max_speed_mps": 0.0,
                                    "max_abs_vz_mps": 0.0,
                                    "max_abs_roll_pitch_deg": 0.0,
                                    "stability_reset_count": 0,
                                }
                                final_metric["time_basis"] = "ros_sim_time"
                                self.set_interactive_goal_ready(False)
                                if self.args.interactive_yaw_scan_after_goal:
                                    scan = self.run_interactive_yaw_scan(f"after_goal_{active_goal_seq}")
                                    metric["post_goal_yaw_scan"] = scan
                                    if not scan.get("ok", False):
                                        return self.abort_for_flight_safety(rate, list(scan.get("blockers", [])))
                                self.set_interactive_goal_ready(True)
                        else:
                            reached_since = None
                            metric["hold_duration_s"] = 0.0
                            metric["hold_start_t"] = None
                if handoff_goal_seq is not None and self.interactive_final_hover_metrics is not None:
                    final_snapshot = self.interactive_goal_snapshot()
                    final_metric = self.interactive_final_hover_metrics
                    if final_snapshot is not None:
                        if final_metric["first_snapshot"] is None:
                            final_metric["first_snapshot"] = final_snapshot
                        final_metric["last_snapshot"] = final_snapshot
                        final_metric["max_error_xyz_m"] = max(
                            final_metric["max_error_xyz_m"], final_snapshot["error_xyz_m"]
                        )
                        final_metric["max_error_xy_m"] = max(
                            final_metric["max_error_xy_m"], final_snapshot["error_xy_m"]
                        )
                        final_metric["max_abs_z_error_m"] = max(
                            final_metric["max_abs_z_error_m"], abs(final_snapshot["error_z_m"])
                        )
                        final_metric["max_speed_mps"] = max(
                            final_metric["max_speed_mps"], final_snapshot["speed_mps"]
                        )
                        final_metric["max_abs_vz_mps"] = max(
                            final_metric["max_abs_vz_mps"], final_snapshot["abs_vz_mps"]
                        )
                        final_metric["max_abs_roll_pitch_deg"] = max(
                            final_metric["max_abs_roll_pitch_deg"], final_snapshot["abs_roll_pitch_deg"]
                        )
                        if self.interactive_goal_reached():
                            if final_stable_since is None:
                                final_stable_since = self.now()
                                final_metric["hold_start_t"] = final_snapshot["t"]
                            final_metric["duration_s"] = self.now() - final_stable_since
                            if final_metric["duration_s"] >= final_metric["required_s"]:
                                final_metric["reached"] = True
                                final_metric["hold_end_t"] = final_snapshot["t"]
                                final_metric["end_snapshot"] = final_snapshot
                        else:
                            if final_stable_since is not None:
                                final_metric["stability_reset_count"] += 1
                            final_stable_since = None
                            final_metric["hold_start_t"] = None
                            final_metric["duration_s"] = 0.0
                self.publish_paths(publish_static_target=False)
                safety_blockers = self.flight_safety_blockers("interactive")
                if safety_blockers:
                    return self.abort_for_flight_safety(rate, safety_blockers)
                if (
                    self.args.interactive_auto_pass_goal_count > 0
                    and handoff_goal_seq is not None
                    and handoff_goal_seq >= self.args.interactive_auto_pass_goal_count
                    and final_stable_since is not None
                    and self.interactive_final_hover_metrics is not None
                    and self.interactive_final_hover_metrics.get("reached") is True
                ):
                    self.set_interactive_goal_ready(False)
                    self.write_outputs(status="interactive_passed", blockers=[])
                    return 0
                rate.sleep()
            self.set_interactive_goal_ready(False)
            status = "review_hold" if review_has_deadline else "review_shutdown"
            self.write_outputs(status=status, blockers=[])
            return 0

        self.phase = "ego_triggered"
        if self.safe_stop.requested():
            return self.perform_safe_stop(rate)
        self.publish_trigger()
        takeover_deadline = time.time() + self.args.ego_takeover_timeout_s
        while not rospy.is_shutdown() and time.time() < takeover_deadline and self.first_planner_takeover_time() is None:
            if self.safe_stop.requested():
                return self.perform_safe_stop(rate)
            self.publish_hover_cmd(home_x, home_y, self.takeoff_target_z_m())
            self.publish_paths()
            rate.sleep()

        if self.first_planner_takeover_time() is None:
            self.write_outputs(status="blocked", blockers=["ego_planner_trajectory_timeout"])
            return 12

        self.set_cmd_adapter_enabled(True)

        if self.args.mission_mode == "exploration_stream":
            self.phase = "exploration_execute"
            execute_start_wall = time.time()
            execute_start_ros = self.now()
            execute_duration_s = (
                self.args.exploration_execute_s
                if self.args.exploration_execute_s > 0.0
                else self.args.execute_timeout_s
            )
            self.exploration_metrics = {
                "execute_duration_target_s": execute_duration_s,
                "time_basis": self.args.exploration_time_basis,
                "started_t": execute_start_ros,
                "started_wall_elapsed_s": self.wall_elapsed(),
                "start_snapshot": self.target_state_snapshot(self.last_odom) if self.last_odom else None,
                "last_snapshot": None,
            }
            while not rospy.is_shutdown() and self.exploration_elapsed_s(execute_start_ros, execute_start_wall) < execute_duration_s:
                if self.safe_stop.requested():
                    return self.perform_safe_stop(rate)
                self.publish_paths(publish_static_target=False)
                safety_blockers = self.flight_safety_blockers("exploration")
                if safety_blockers:
                    return self.abort_for_flight_safety(rate, safety_blockers)
                if self.last_odom:
                    self.exploration_metrics["last_snapshot"] = self.target_state_snapshot(self.last_odom)
                self.wall_sleep_once()
            self.exploration_metrics["duration_s"] = self.now() - execute_start_ros
            self.exploration_metrics["wall_duration_s"] = time.time() - execute_start_wall
            self.exploration_metrics["ended_t"] = self.now()
            self.exploration_metrics["ended_wall_elapsed_s"] = self.wall_elapsed()
            self.exploration_metrics["end_snapshot"] = (
                self.target_state_snapshot(self.last_odom) if self.last_odom else None
            )
            self.write_outputs(status="exploration_completed", blockers=[])
            if self.args.skip_land_after_exploration:
                self.phase = "done"
                return 0
            return self.land_and_finish(rate)

        self.phase = "ego_execute"
        execute_start = time.time()
        target_hold_start: float | None = None
        target_hold_reached = False
        self.target_hold_metrics = {
            "reached": False,
            "required_s": self.args.target_hold_s,
            "time_basis": "ros_sim_time",
            "radius_m": self.args.target_reached_radius,
            "max_speed_mps": self.args.target_hold_max_speed_mps,
            "max_vz_mps": self.args.target_hold_max_vz_mps,
            "hold_start_t": None,
            "hold_end_t": None,
            "duration_s": 0.0,
            "best_error_m": None,
            "best_snapshot": None,
            "first_reached_snapshot": None,
            "last_execute_snapshot": None,
            "end_snapshot": None,
        }
        while not rospy.is_shutdown() and time.time() - execute_start < self.args.execute_timeout_s:
            if self.safe_stop.requested():
                return self.perform_safe_stop(rate)
            self.publish_paths()
            safety_blockers = self.flight_safety_blockers("execute")
            if safety_blockers:
                return self.abort_for_flight_safety(rate, safety_blockers)
            if self.last_odom:
                snapshot = self.target_state_snapshot(self.last_odom)
                if snapshot is None:
                    rate.sleep()
                    continue
                self.target_hold_metrics["last_execute_snapshot"] = snapshot
                best_error = self.target_hold_metrics["best_error_m"]
                if best_error is None or snapshot["error_xyz_m"] < best_error:
                    self.target_hold_metrics["best_error_m"] = snapshot["error_xyz_m"]
                    self.target_hold_metrics["best_snapshot"] = snapshot
                speed_ok = (
                    self.args.target_hold_max_speed_mps <= 0.0
                    or snapshot["speed_mps"] <= self.args.target_hold_max_speed_mps
                )
                vz_ok = (
                    self.args.target_hold_max_vz_mps <= 0.0
                    or snapshot["abs_vz_mps"] <= self.args.target_hold_max_vz_mps
                )
                if snapshot["error_xyz_m"] <= self.args.target_reached_radius and speed_ok and vz_ok:
                    if target_hold_start is None:
                        target_hold_start = self.now()
                        self.target_hold_metrics["hold_start_t"] = snapshot["t"]
                        if self.target_hold_metrics["first_reached_snapshot"] is None:
                            self.target_hold_metrics["first_reached_snapshot"] = snapshot
                    hold_duration = self.now() - target_hold_start
                    self.target_hold_metrics["duration_s"] = hold_duration
                    if hold_duration >= self.args.target_hold_s:
                        target_hold_reached = True
                        self.target_hold_metrics["reached"] = True
                        self.target_hold_metrics["hold_end_t"] = snapshot["t"]
                        self.target_hold_metrics["end_snapshot"] = snapshot
                        break
                else:
                    target_hold_start = None
                    self.target_hold_metrics["hold_start_t"] = None
                    self.target_hold_metrics["duration_s"] = 0.0
            rate.sleep()

        if not target_hold_reached:
            self.write_outputs(status="blocked", blockers=["target_not_reached"])
            return 13

        return self.land_and_finish(rate)

    def acceptance_blockers(self) -> list[str]:
        blockers: list[str] = []
        if self.lidar_count < self.args.min_raw_lidar_count:
            blockers.append("raw_lidar_count_below_gate")
        if self.lidar_last_points < self.args.min_raw_lidar_points:
            blockers.append("raw_lidar_points_below_gate")
        if self.world_cloud_count < self.args.min_world_cloud_count:
            blockers.append("world_cloud_count_below_gate")
        if self.world_cloud_last_points < self.args.min_world_cloud_points:
            blockers.append("world_cloud_points_below_gate")
        if self.occupancy_count < self.args.min_occupancy_count:
            blockers.append("occupancy_count_below_gate")
        if (not self.args.allow_empty_final_occupancy) and self.occupancy_max_points < self.args.min_occupancy_points:
            blockers.append("occupancy_points_below_gate")
        if self.frontier_count < self.args.min_frontier_count:
            blockers.append("frontier_count_below_gate")
        if self.trajectory_vis_count < self.args.min_trajectory_vis_count:
            blockers.append("trajectory_vis_count_below_gate")
        if self.bspline_count < self.args.min_bspline_count:
            blockers.append("bspline_count_below_gate")
        if self.bspline_count + self.polytraj_count < self.args.min_planner_traj_count:
            blockers.append("planner_trajectory_count_below_gate")
        if self.planner_position_cmd_count < self.args.min_planner_command_count:
            blockers.append("planner_position_cmd_count_below_gate")
        if self.position_cmd_count < self.args.min_position_cmd_count:
            blockers.append("position_cmd_count_below_gate")
        if self.att_target_count < self.args.min_target_attitude_count:
            blockers.append("target_attitude_count_below_gate")
        if self.land_metrics and self.land_metrics.get("landed_by_truth") is not True:
            blockers.append("landed_by_truth_false")
        raw_jump_gate_m = (
            self.args.max_position_cmd_jump_m
            if self.args.max_raw_planner_position_cmd_jump_m < 0.0
            else self.args.max_raw_planner_position_cmd_jump_m
        )
        raw_speed_gate_mps = (
            self.args.max_position_cmd_speed_mps
            if self.args.max_raw_planner_position_cmd_speed_mps < 0.0
            else self.args.max_raw_planner_position_cmd_speed_mps
        )
        planner_continuity = self.command_continuity_gate_summary(
            self.planner_position_cmd_rows,
            max_position_cmd_jump_m=raw_jump_gate_m,
            max_position_cmd_speed_mps=raw_speed_gate_mps,
        )
        if (
            planner_continuity
            and planner_continuity.get("violates_jump_gate")
            and not self.args.allow_discontinuous_raw_planner_position_cmd
        ):
            blockers.append("raw_planner_position_cmd_discontinuous")
        cmd_continuity = self.command_continuity_gate_summary(self.position_cmd_rows)
        if cmd_continuity and cmd_continuity.get("violates_jump_gate"):
            blockers.append("position_cmd_discontinuous")
        return blockers

    @staticmethod
    def write_csv(path: Path, rows: list[dict]) -> None:
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def target_error_summary(self) -> dict:
        target = (self.args.target_x, self.args.target_y, self.args.target_z)

        def summarize(rows: list[dict]) -> dict | None:
            if not rows:
                return None
            xyz_err = [math.dist((r["x"], r["y"], r["z"]), target) for r in rows]
            xy_err = [math.dist((r["x"], r["y"]), target[:2]) for r in rows]
            return {
                "samples": len(rows),
                "min_xyz_m": min(xyz_err),
                "end_xyz_m": xyz_err[-1],
                "rmse_xyz_m": math.sqrt(sum(e * e for e in xyz_err) / len(xyz_err)),
                "min_xy_m": min(xy_err),
                "end_xy_m": xy_err[-1],
            }

        return {
            "ego_execute": summarize([r for r in self.odom_rows if r.get("phase") == "ego_execute"]),
            "land": summarize([r for r in self.odom_rows if r.get("phase") == "land"]),
        }

    @staticmethod
    def command_motion_summary(rows: list[dict]) -> dict | None:
        if not rows:
            return None
        xs = [float(r["x"]) for r in rows]
        ys = [float(r["y"]) for r in rows]
        zs = [float(r["z"]) for r in rows]
        return {
            "samples": len(rows),
            "x_range_m": max(xs) - min(xs),
            "y_range_m": max(ys) - min(ys),
            "z_range_m": max(zs) - min(zs),
            "start_xyz": [xs[0], ys[0], zs[0]],
            "end_xyz": [xs[-1], ys[-1], zs[-1]],
            "start_to_end_xyz_m": math.dist((xs[0], ys[0], zs[0]), (xs[-1], ys[-1], zs[-1])),
        }

    def command_continuity_summary(
        self,
        rows: list[dict],
        max_position_cmd_jump_m: float | None = None,
        max_position_cmd_speed_mps: float | None = None,
        time_field: str = "t",
        min_dt_for_speed_gate_s: float | None = None,
    ) -> dict | None:
        if len(rows) < 2:
            return None
        jump_gate = self.args.max_position_cmd_jump_m if max_position_cmd_jump_m is None else max_position_cmd_jump_m
        speed_gate = (
            self.args.max_position_cmd_speed_mps
            if max_position_cmd_speed_mps is None
            else max_position_cmd_speed_mps
        )
        min_speed_dt = (
            self.args.min_position_cmd_speed_gate_dt_s
            if min_dt_for_speed_gate_s is None
            else min_dt_for_speed_gate_s
        )
        max_jump = 0.0
        max_xy_jump = 0.0
        max_z_jump = 0.0
        max_jump_speed = 0.0
        max_jump_pair: dict | None = None
        max_speed_pair: dict | None = None
        violations = 0
        short_dt_speed_gate_skips = 0
        for prev, curr in zip(rows, rows[1:]):
            if time_field not in prev or time_field not in curr:
                return None
            dt = float(curr[time_field]) - float(prev[time_field])
            if dt <= 1e-6:
                continue
            dx = float(curr["x"]) - float(prev["x"])
            dy = float(curr["y"]) - float(prev["y"])
            dz = float(curr["z"]) - float(prev["z"])
            jump = math.sqrt(dx * dx + dy * dy + dz * dz)
            xy_jump = math.hypot(dx, dy)
            z_jump = abs(dz)
            jump_speed = jump / dt
            pair = {
                "t_prev": float(prev["t"]),
                "t_curr": float(curr["t"]),
                "wall_elapsed_prev_s": float(prev.get("wall_elapsed_s", 0.0) or 0.0),
                "wall_elapsed_curr_s": float(curr.get("wall_elapsed_s", 0.0) or 0.0),
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
            if jump > max_jump:
                max_jump = jump
                max_jump_pair = pair
            max_xy_jump = max(max_xy_jump, xy_jump)
            max_z_jump = max(max_z_jump, z_jump)
            if jump_speed > max_jump_speed:
                max_jump_speed = jump_speed
                max_speed_pair = pair
            jump_violation = jump_gate > 0.0 and jump > jump_gate
            speed_violation = False
            if speed_gate > 0.0 and jump_speed > speed_gate:
                if min_speed_dt > 0.0 and dt < min_speed_dt:
                    short_dt_speed_gate_skips += 1
                else:
                    speed_violation = True
            if jump_violation or speed_violation:
                violations += 1
        return {
            "samples": len(rows),
            "time_field": time_field,
            "thresholds": {
                "max_position_cmd_jump_m": jump_gate,
                "max_position_cmd_speed_mps": speed_gate,
                "min_position_cmd_speed_gate_dt_s": min_speed_dt,
            },
            "max_jump_m": max_jump,
            "max_xy_jump_m": max_xy_jump,
            "max_z_jump_m": max_z_jump,
            "max_jump_speed_mps": max_jump_speed,
            "max_jump_pair": max_jump_pair,
            "max_speed_pair": max_speed_pair,
            "short_dt_speed_gate_skip_count": short_dt_speed_gate_skips,
            "violation_count": violations,
            "violates_jump_gate": violations > 0,
        }

    def command_continuity_gate_summary(
        self,
        rows: list[dict],
        max_position_cmd_jump_m: float | None = None,
        max_position_cmd_speed_mps: float | None = None,
    ) -> dict | None:
        wall_summary = self.command_continuity_summary(
            rows,
            max_position_cmd_jump_m=max_position_cmd_jump_m,
            max_position_cmd_speed_mps=max_position_cmd_speed_mps,
            time_field="wall_elapsed_s",
            min_dt_for_speed_gate_s=self.args.min_position_cmd_speed_gate_dt_s,
        )
        if wall_summary is not None:
            sim_summary = self.command_continuity_summary(
                rows,
                max_position_cmd_jump_m=max_position_cmd_jump_m,
                max_position_cmd_speed_mps=max_position_cmd_speed_mps,
                time_field="t",
                min_dt_for_speed_gate_s=self.args.min_position_cmd_speed_gate_dt_s,
            )
            if sim_summary is not None:
                wall_summary["sim_time_diagnostic"] = sim_summary
            return wall_summary
        return self.command_continuity_summary(
            rows,
            max_position_cmd_jump_m=max_position_cmd_jump_m,
            max_position_cmd_speed_mps=max_position_cmd_speed_mps,
            time_field="t",
            min_dt_for_speed_gate_s=self.args.min_position_cmd_speed_gate_dt_s,
        )

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
        for item in summary.values():
            if item["samples"] == 0:
                item["min_z_m"] = None
                item["max_z_m"] = None
        return summary

    @staticmethod
    def rows_in_phases(rows: list[dict], phases: set[str]) -> list[dict]:
        return [row for row in rows if str(row.get("phase")) in phases]

    def adapter_diagnostics(self) -> dict | None:
        path = self.result_dir / "position_cmd_safety_adapter.json"
        if not path.exists() or path.stat().st_size == 0:
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"decode_error": True, "path": str(path)}

    def write_outputs(self, status: str, blockers: list[str]) -> None:
        self.write_csv(self.result_dir / "truth.csv", self.truth_rows)
        self.write_csv(self.result_dir / "sunray_truth.csv", self.sunray_truth_rows)
        self.write_csv(self.result_dir / "odom.csv", self.odom_rows)
        self.write_csv(self.result_dir / "mavros_state.csv", self.state_rows)
        self.write_csv(self.result_dir / "position_cmd.csv", self.position_cmd_rows)
        self.write_csv(self.result_dir / "planner_position_cmd_raw.csv", self.planner_position_cmd_rows)
        self.write_csv(self.result_dir / "forwarded_goals.csv", self.forwarded_goal_rows)
        self.write_csv(self.result_dir / "bspline_summary.csv", self.bspline_rows)
        self.write_csv(self.result_dir / "target_attitude.csv", self.att_target_rows)
        self.write_csv(self.result_dir / "debug_px4ctrl.csv", self.debug_rows)
        final_err = None
        if self.last_odom:
            final_err = math.dist(
                (self.last_odom["x"], self.last_odom["y"], self.last_odom["z"]),
                (self.args.target_x, self.args.target_y, self.args.target_z),
            )
        target_hold_end_error = None
        if self.target_hold_metrics and isinstance(self.target_hold_metrics.get("end_snapshot"), dict):
            target_hold_end_error = self.target_hold_metrics["end_snapshot"].get("error_xyz_m")
        final_blockers = list(blockers)
        phase_peak_summary = {
            "truth": self.state_phase_summary(self.truth_rows),
            "odom": self.state_phase_summary(self.odom_rows),
        }
        peak_safety_violation = None
        execute_phases = {"ego_execute", "exploration_execute"}
        attitude_phases = execute_phases | {"land", "done"}
        for source, source_summary in phase_peak_summary.items():
            if not isinstance(source_summary, dict):
                continue
            min_z = self.args.execute_min_truth_z_m if source == "truth" else self.args.execute_min_odom_z_m
            for phase, item in source_summary.items():
                if phase not in attitude_phases or not isinstance(item, dict) or item.get("samples", 0) <= 0:
                    continue
                if (
                    phase in execute_phases
                    and min_z > 0.0
                    and item.get("min_z_m") is not None
                    and item["min_z_m"] < min_z
                ):
                    final_blockers.append(f"phase_peak_{source}_{phase}_z_below_gate")
                if (
                    self.args.execute_max_roll_pitch_deg > 0.0
                    and item.get("max_abs_roll_pitch_deg") is not None
                    and item["max_abs_roll_pitch_deg"] > self.args.execute_max_roll_pitch_deg
                ):
                    final_blockers.append(f"phase_peak_{source}_{phase}_roll_pitch_above_gate")
        if final_blockers and not self.flight_safety_violation:
            peak_safety_violation = {
                "source": "phase_peak_summary",
                "blockers": final_blockers,
                "thresholds": {
                    "min_truth_z_m": self.args.execute_min_truth_z_m,
                    "min_odom_z_m": self.args.execute_min_odom_z_m,
                    "max_roll_pitch_deg": self.args.execute_max_roll_pitch_deg,
                },
            }
            self.flight_safety_violation = peak_safety_violation
        trajectory_freshness = self.exploration_trajectory_freshness_summary()
        if trajectory_freshness and not trajectory_freshness["passed"]:
            final_blockers.append("planner_trajectory_stale")
        final_blockers = list(dict.fromkeys(final_blockers))
        run_status_ok = status == "passed" or (
            self.args.mission_mode == "exploration_stream"
            and status == "exploration_completed"
        ) or (
            self.args.interactive_goal_review
            and status in {"interactive_passed", "review_hold"}
        )
        final_status = "passed" if run_status_ok and not final_blockers else "blocked"
        summary = {
            "schema": "mosim.sunray_ros1.goal4_ego_single_metrics.v1",
            "status": final_status,
            "blockers": final_blockers,
            "run_terminal_status": status,
            "mission_mode": self.args.mission_mode,
            "target": {"x": self.args.target_x, "y": self.args.target_y, "z": self.args.target_z},
            "counts": {
                "truth_rows": len(self.truth_rows),
                "sunray_truth_rows": len(self.sunray_truth_rows),
                "odom_rows": len(self.odom_rows),
                "mavros_state_rows": len(self.state_rows),
                "position_cmd": self.position_cmd_count,
                "planner_position_cmd": self.planner_position_cmd_count,
                "bspline": self.bspline_count,
                "polytraj": self.polytraj_count,
                "raw_lidar": self.lidar_count,
                "world_cloud": self.world_cloud_count,
                "occupancy_inflate": self.occupancy_count,
                "frontier": self.frontier_count,
                "trajectory_vis": self.trajectory_vis_count,
                "target_attitude": self.att_target_count,
                "debug_px4ctrl": self.debug_count,
            },
            "last_point_counts": {
                "raw_lidar": self.lidar_last_points,
                "world_cloud": self.world_cloud_last_points,
                "occupancy_inflate": self.occupancy_last_points,
                "frontier_markers_total": self.frontier_marker_count,
                "trajectory_vis_markers_total": self.trajectory_vis_marker_count,
            },
            "max_point_counts": {
                "occupancy_inflate": self.occupancy_max_points,
            },
            "first_bspline_t": self.first_bspline_t,
            "first_polytraj_t": self.first_polytraj_t,
            "first_planner_position_cmd_t": self.first_planner_position_cmd_t,
            "first_planner_trajectory_t": self.first_planner_trajectory_time(),
            "first_planner_takeover_t": self.first_planner_takeover_time(),
            "hover_cmd_publish_count": self.hover_cmd_publish_count,
            "takeoff_cmd_publish_count": self.takeoff_cmd_publish_count,
            "land_cmd_publish_count": self.land_cmd_publish_count,
            "takeoff_status": self.takeoff_status_summary(),
            "occupancy_last_points": self.occupancy_last_points,
            "execute_target_error_m": target_hold_end_error,
            "target_hold": self.target_hold_metrics,
            "exploration": self.exploration_metrics,
            "exploration_trajectory_freshness": trajectory_freshness,
            "interactive_goals": self.interactive_goal_metrics,
            "interactive_goal_handoffs": self.interactive_goal_handoff_metrics,
            "interactive_goal_frame_issue": self.last_interactive_goal_frame_issue,
            "interactive_final_hover": self.interactive_final_hover_metrics,
            "interactive_yaw_scan_events": self.interactive_yaw_scan_events,
            "forwarded_goal_count": self.forwarded_goal_seq,
            "land": self.land_metrics,
            "final_target_error_m": final_err,
            "post_land_final_target_error_m": final_err,
            "final_target_error_semantics": (
                "Last odom sample at write_outputs time. For a successful run this is usually "
                "post-land and must not be used as execute target tracking acceptance."
            ),
            "target_error_summary": self.target_error_summary(),
            "position_cmd_motion": self.command_motion_summary(self.position_cmd_rows),
            "planner_position_cmd_motion": self.command_motion_summary(self.planner_position_cmd_rows),
            "position_cmd_continuity": self.command_continuity_gate_summary(self.position_cmd_rows),
            "planner_position_cmd_continuity": self.command_continuity_gate_summary(
                self.planner_position_cmd_rows,
                max_position_cmd_jump_m=(
                    self.args.max_position_cmd_jump_m
                    if self.args.max_raw_planner_position_cmd_jump_m < 0.0
                    else self.args.max_raw_planner_position_cmd_jump_m
                ),
                max_position_cmd_speed_mps=(
                    self.args.max_position_cmd_speed_mps
                    if self.args.max_raw_planner_position_cmd_speed_mps < 0.0
                    else self.args.max_raw_planner_position_cmd_speed_mps
                ),
            ),
            "phase_peak_summary": phase_peak_summary,
            "position_cmd_safety_adapter": self.adapter_diagnostics(),
            "pre_diff_gate": {
                "last_snapshot": self.last_pre_diff_gate,
                "trigger_snapshot": self.pre_diff_trigger_snapshot,
                "history_tail": self.pre_diff_gate_history[-20:],
            },
            "flight_safety_violation": self.flight_safety_violation,
            "claim_boundary": (
                "Goal4 planner/traj_server to px4ctrl through MAVROS/PX4/Gazebo; "
                "mission_mode=fixed_goal requires target hold, while "
                "mission_mode=exploration_stream only proves bounded planner command "
                "stream execution before landing. State source is MAVROS local odom, "
                "Gazebo truth is evaluation only."
            ),
        }
        (self.result_dir / "EGO_SINGLE_METRICS.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        self.mission_status.finish(
            result_status=final_status,
            accepted=final_status == "passed",
            blockers=final_blockers,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--path-odom-topic", default="")
    parser.add_argument("--control-frame", default="map")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--sunray-truth-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--raw-lidar-topic", default="/uav1/livox/lidar")
    parser.add_argument("--world-cloud-topic", default="/uav1/livox_world")
    parser.add_argument("--occupancy-topic", default="/drone_0_ego_planner_node/grid_map/occupancy_inflate")
    parser.add_argument("--occupancy-msg-type", choices=["pointcloud2", "markerarray"], default="pointcloud2")
    parser.add_argument("--frontier-topic", default="")
    parser.add_argument("--frontier-msg-type", choices=["marker", "markerarray", "pointcloud2"], default="marker")
    parser.add_argument("--trajectory-vis-topic", default="")
    parser.add_argument("--trajectory-vis-msg-type", choices=["marker", "markerarray"], default="marker")
    parser.add_argument("--bspline-topic", default="/drone_0_planning/bspline")
    parser.add_argument("--bspline-msg-package", choices=["traj_utils", "bspline", "trajectory", "auto"], default="traj_utils")
    parser.add_argument("--polytraj-topic", default="")
    parser.add_argument("--planner-position-cmd-topic", default="")
    parser.add_argument("--goalset-topic", default="")
    parser.add_argument("--goal-pose-topic", default="")
    parser.add_argument("--mission-mode", choices=["fixed_goal", "exploration_stream"], default="fixed_goal")
    parser.add_argument("--path-frame", default="world")
    parser.add_argument("--path-command-offset-x", type=float, default=0.0)
    parser.add_argument("--path-command-offset-y", type=float, default=0.0)
    parser.add_argument("--path-command-offset-z", type=float, default=0.0)
    parser.add_argument("--drone-id", type=int, default=0)
    parser.add_argument("--target-x", type=float, default=4.0)
    parser.add_argument("--target-y", type=float, default=0.0)
    parser.add_argument("--target-z", type=float, default=1.0)
    parser.add_argument("--takeoff-height", type=float, default=1.0)
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--ready-timeout-s", type=float, default=30.0)
    parser.add_argument("--takeoff-timeout-s", type=float, default=35.0)
    parser.add_argument("--ego-takeover-timeout-s", type=float, default=30.0)
    parser.add_argument("--execute-timeout-s", type=float, default=80.0)
    parser.add_argument("--exploration-execute-s", type=float, default=20.0)
    parser.add_argument("--exploration-time-basis", choices=["ros_sim_time", "wall"], default="ros_sim_time")
    parser.add_argument("--exploration-max-trajectory-stale-s", type=float, default=10.0)
    parser.add_argument("--skip-land-after-exploration", action="store_true")
    parser.add_argument("--execute-min-truth-z-m", type=float, default=0.50)
    parser.add_argument("--execute-min-odom-z-m", type=float, default=0.50)
    parser.add_argument("--execute-max-roll-pitch-deg", type=float, default=45.0)
    parser.add_argument("--execute-max-truth-odom-z-error-m", type=float, default=0.0)
    parser.add_argument("--land-timeout-s", type=float, default=25.0)
    parser.add_argument("--pre-ego-hover-s", type=float, default=2.0)
    parser.add_argument("--pre-diff-stable-s", type=float, default=3.0)
    parser.add_argument("--pre-diff-odom-timeout-s", type=float, default=0.25)
    parser.add_argument("--pre-diff-max-xy-error-m", type=float, default=0.20)
    parser.add_argument("--pre-diff-max-z-error-m", type=float, default=0.10)
    parser.add_argument("--pre-diff-max-speed-mps", type=float, default=0.25)
    parser.add_argument("--pre-diff-max-vz-mps", type=float, default=0.18)
    parser.add_argument("--pre-diff-max-roll-pitch-deg", type=float, default=12.0)
    parser.add_argument("--pre-diff-require-truth-gate", action="store_true")
    parser.add_argument("--pre-diff-truth-max-xy-error-m", type=float, default=0.25)
    parser.add_argument("--pre-diff-truth-max-z-error-m", type=float, default=0.15)
    parser.add_argument("--pre-diff-truth-max-speed-mps", type=float, default=0.30)
    parser.add_argument("--pre-diff-truth-max-vz-mps", type=float, default=0.20)
    parser.add_argument("--pre-diff-truth-max-roll-pitch-deg", type=float, default=15.0)
    parser.add_argument("--pre-diff-history-limit", type=int, default=200)
    parser.add_argument("--publish-hover-during-takeoff", action="store_true")
    parser.add_argument("--publish-hover-during-takeoff-delay-s", type=float, default=0.0)
    parser.add_argument("--target-hold-s", type=float, default=2.0)
    parser.add_argument("--target-hold-max-speed-mps", type=float, default=0.35)
    parser.add_argument("--target-hold-max-vz-mps", type=float, default=0.20)
    parser.add_argument("--takeoff-z-tol", type=float, default=0.12)
    parser.add_argument("--target-reached-radius", type=float, default=0.35)
    parser.add_argument("--landed-z-max", type=float, default=0.18)
    parser.add_argument("--landed-max-speed-mps", type=float, default=0.30)
    parser.add_argument("--landed-max-vz-mps", type=float, default=0.25)
    parser.add_argument("--landed-max-roll-pitch-deg", type=float, default=20.0)
    parser.add_argument("--landed-stable-s", type=float, default=0.50)
    parser.add_argument("--min-raw-lidar-count", type=int, default=5)
    parser.add_argument("--min-raw-lidar-points", type=int, default=1)
    parser.add_argument("--min-world-cloud-count", type=int, default=5)
    parser.add_argument("--min-world-cloud-points", type=int, default=1)
    parser.add_argument("--min-occupancy-count", type=int, default=3)
    parser.add_argument("--min-occupancy-points", type=int, default=1)
    parser.add_argument("--min-frontier-count", type=int, default=0)
    parser.add_argument("--min-trajectory-vis-count", type=int, default=0)
    parser.add_argument(
        "--allow-empty-final-occupancy",
        action="store_true",
        help=(
            "Do not block the mission only because the final occupancy frame is empty. "
            "Use this for fixed-goal regression when live lidar/world cloud and "
            "planner command evidence are nonempty; keep the default hard gate for "
            "exploration/map-quality runs."
        ),
    )
    parser.add_argument("--min-bspline-count", type=int, default=0)
    parser.add_argument("--min-planner-traj-count", type=int, default=1)
    parser.add_argument("--min-planner-command-count", type=int, default=0)
    parser.add_argument("--min-position-cmd-count", type=int, default=10)
    parser.add_argument("--min-target-attitude-count", type=int, default=10)
    parser.add_argument("--hover-publish-hz", type=float, default=50.0)
    parser.add_argument("--record-hz", type=float, default=30.0)
    parser.add_argument("--record-cmd-hz", type=float, default=50.0)
    parser.add_argument("--max-path-points", type=int, default=5000)
    parser.add_argument("--path-publish-hz", type=float, default=20.0)
    parser.add_argument("--body-axes-topic", default="/mosim/goal4/body_axes")
    parser.add_argument("--body-axis-length-m", type=float, default=0.25)
    parser.add_argument("--body-axis-shaft-m", type=float, default=0.012)
    parser.add_argument("--body-axis-head-diameter-m", type=float, default=0.035)
    parser.add_argument("--body-axis-head-length-m", type=float, default=0.055)
    parser.add_argument("--body-axis-lifetime-s", type=float, default=1.5)
    parser.add_argument("--cmd-path-segment-jump-m", type=float, default=0.0)
    parser.add_argument("--max-position-cmd-jump-m", type=float, default=0.50)
    parser.add_argument("--max-position-cmd-speed-mps", type=float, default=3.0)
    parser.add_argument(
        "--min-position-cmd-speed-gate-dt-s",
        type=float,
        default=0.05,
        help=(
            "Minimum sample interval for enforcing the offline position-command "
            "speed continuity gate. Shorter intervals are still recorded in "
            "max_speed_pair but are skipped for the speed gate to match the "
            "runtime safety adapter's jump_guard_min_dt_s semantics."
        ),
    )
    parser.add_argument(
        "--max-raw-planner-position-cmd-jump-m",
        type=float,
        default=-1.0,
        help="Raw planner command jump gate. Negative inherits --max-position-cmd-jump-m; 0 disables raw jump gate.",
    )
    parser.add_argument(
        "--max-raw-planner-position-cmd-speed-mps",
        type=float,
        default=-1.0,
        help="Raw planner command speed gate. Negative inherits --max-position-cmd-speed-mps; 0 disables raw speed gate.",
    )
    parser.add_argument(
        "--allow-discontinuous-raw-planner-position-cmd",
        action="store_true",
        help="Keep raw planner command continuity as diagnostics only; hard gate remains on /position_cmd.",
    )
    parser.add_argument("--takeoff-cmd-repeats", type=int, default=8)
    parser.add_argument("--takeoff-retry-interval-s", type=float, default=0.0)
    parser.add_argument("--takeoff-retry-repeats", type=int, default=3)
    parser.add_argument("--takeoff-retry-max", type=int, default=0)
    parser.add_argument("--takeoff-rise-detect-m", type=float, default=0.08)
    parser.add_argument("--land-cmd-repeats", type=int, default=8)
    parser.add_argument("--goal-trigger-repeats", type=int, default=5)
    parser.add_argument("--cmd-adapter-enable-topic", default="/mosim/goal4/position_cmd_adapter_enable")
    parser.add_argument("--disable-cmd-adapter-before-land", action="store_true")
    parser.add_argument("--post-adapter-disable-wait-s", type=float, default=0.8)
    parser.add_argument("--interactive-goal-review", action="store_true")
    parser.add_argument("--interactive-goal-ready-topic", default="/mosim/goal4/interactive_goal_ready")
    parser.add_argument("--interactive-forwarded-goal-topic", default="/goal_with_id")
    parser.add_argument("--publish-goal-in-interactive-review", action="store_true")
    parser.add_argument("--interactive-review-hold-s", type=float, default=180.0)
    parser.add_argument("--interactive-target-reached-xy-m", type=float, default=0.35)
    parser.add_argument("--interactive-target-reached-z-m", type=float, default=0.12)
    parser.add_argument("--interactive-target-hold-s", type=float, default=1.5)
    parser.add_argument("--interactive-target-hold-max-speed-mps", type=float, default=0.35)
    parser.add_argument("--interactive-target-hold-max-vz-mps", type=float, default=0.20)
    parser.add_argument("--interactive-target-hold-max-roll-pitch-deg", type=float, default=15.0)
    parser.add_argument("--interactive-post-adapter-disable-wait-s", type=float, default=0.25)
    parser.add_argument("--interactive-handoff-hover-repeats", type=int, default=10)
    parser.add_argument("--interactive-handoff-mode", choices=["adapter_hold", "direct_hover"], default="adapter_hold")
    parser.add_argument("--interactive-auto-pass-goal-count", type=int, default=0)
    parser.add_argument("--interactive-final-hover-hold-s", type=float, default=5.0)
    parser.add_argument("--interactive-yaw-scan-enable", action="store_true")
    parser.add_argument("--interactive-yaw-scan-after-goal", action="store_true")
    parser.add_argument("--interactive-yaw-scan-delta-rad", type=float, default=math.pi)
    parser.add_argument("--interactive-yaw-scan-duration-s", type=float, default=6.0)
    parser.add_argument("--interactive-yaw-scan-settle-s", type=float, default=1.0)
    parser.add_argument("--interactive-yaw-scan-disable-cmd-adapter", action="store_true")
    parser.add_argument("--interactive-yaw-scan-reenable-cmd-adapter", action="store_true")
    return parser.parse_args()


def main() -> None:
    rospy.init_node("mosim_px4ctrl_ego_single_mission")
    mission = EgoSingleMission(parse_args())
    raise SystemExit(mission.run())


if __name__ == "__main__":
    main()
