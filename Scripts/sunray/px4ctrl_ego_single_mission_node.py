#!/usr/bin/env python3
"""Goal4 EGO single-UAV mission gate for original px4ctrl + Gazebo."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import rospy
import sensor_msgs.point_cloud2 as pc2
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import AttitudeTarget, State
from nav_msgs.msg import Odometry, Path as RosPath
from quadrotor_msgs.msg import GoalSet, PositionCommand, Px4ctrlDebug, TakeoffLand
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool, Header
try:
    from traj_utils.msg import Bspline
except ImportError:  # EGO v2 overlays may not define Bspline.
    Bspline = None

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
        self.home: tuple[float, float, float] | None = None
        self.mission_home_xy: tuple[float, float] | None = None
        self.last_truth: dict | None = None
        self.last_odom: dict | None = None
        self.last_state: State | None = None
        self.last_position_cmd: dict | None = None
        self.first_bspline_t: float | None = None
        self.first_polytraj_t: float | None = None
        self.bspline_count = 0
        self.polytraj_count = 0
        self.position_cmd_count = 0
        self.lidar_count = 0
        self.lidar_last_points = 0
        self.world_cloud_count = 0
        self.world_cloud_last_points = 0
        self.occupancy_count = 0
        self.occupancy_last_points = 0
        self.att_target_count = 0
        self.debug_count = 0

        self.truth_rows: list[dict] = []
        self.odom_rows: list[dict] = []
        self.position_cmd_rows: list[dict] = []
        self.bspline_rows: list[dict] = []
        self.att_target_rows: list[dict] = []
        self.debug_rows: list[dict] = []
        self.last_record_t = {"truth": -1e9, "odom": -1e9, "cmd": -1e9, "att": -1e9, "debug": -1e9}

        self.takeoff_land_pub = rospy.Publisher("/px4ctrl/takeoff_land", TakeoffLand, queue_size=3, latch=True)
        self.hover_cmd_pub = rospy.Publisher("/position_cmd", PositionCommand, queue_size=10)
        self.cmd_adapter_enable_pub = rospy.Publisher(args.cmd_adapter_enable_topic, Bool, queue_size=3, latch=True)
        self.trigger_pub = rospy.Publisher("/traj_start_trigger", PoseStamped, queue_size=3, latch=True)
        self.goalset_pub = rospy.Publisher(args.goalset_topic, GoalSet, queue_size=3, latch=True) if args.goalset_topic else None
        self.goal_pose_pub = rospy.Publisher(args.goal_pose_topic, PoseStamped, queue_size=3, latch=True) if args.goal_pose_topic else None
        self.truth_path_pub = rospy.Publisher("/mosim/goal4/truth_path", RosPath, queue_size=1, latch=True)
        self.cmd_path_pub = rospy.Publisher("/mosim/goal4/position_cmd_path", RosPath, queue_size=1, latch=True)
        self.target_path_pub = rospy.Publisher("/mosim/goal4/target_path", RosPath, queue_size=1, latch=True)
        self.truth_path = RosPath(header=Header(frame_id=args.path_frame))
        self.cmd_path = RosPath(header=Header(frame_id=args.path_frame))

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=30)
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=100)
        rospy.Subscriber("/uav1/mavros/state", State, self.on_state, queue_size=20)
        rospy.Subscriber("/position_cmd", PositionCommand, self.on_position_cmd, queue_size=200)
        if Bspline is not None and args.bspline_topic:
            rospy.Subscriber(args.bspline_topic, Bspline, self.on_bspline, queue_size=20)
        if PolyTraj is not None and args.polytraj_topic:
            rospy.Subscriber(args.polytraj_topic, PolyTraj, self.on_polytraj, queue_size=20)
        rospy.Subscriber(args.raw_lidar_topic, PointCloud2, self.on_raw_lidar, queue_size=20)
        rospy.Subscriber(args.world_cloud_topic, PointCloud2, self.on_world_cloud, queue_size=20)
        rospy.Subscriber(args.occupancy_topic, PointCloud2, self.on_occupancy, queue_size=20)
        rospy.Subscriber("/uav1/mavros/setpoint_raw/target_attitude", AttitudeTarget, self.on_att_target, queue_size=100)
        rospy.Subscriber("/debugPx4ctrl", Px4ctrlDebug, self.on_debug, queue_size=100)

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        return float(stamp) if stamp > 0 else time.time() - self.start_wall

    def wall_elapsed(self) -> float:
        return time.time() - self.start_wall

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
        if self.should_record("truth", t, self.args.record_hz):
            self.truth_rows.append(row)
            self.append_path(self.truth_path, row["x"], row["y"], row["z"], t, max_points=self.args.max_path_points)

    def on_odom(self, msg: Odometry) -> None:
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
        self.last_odom = row
        if self.should_record("odom", t, self.args.record_hz):
            self.odom_rows.append(row)

    def on_position_cmd(self, msg: PositionCommand) -> None:
        t = self.now()
        row = {
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
        self.last_position_cmd = row
        self.position_cmd_count += 1
        if self.should_record("cmd", t, self.args.record_cmd_hz):
            self.position_cmd_rows.append(row)
            self.append_path(self.cmd_path, row["x"], row["y"], row["z"], t, max_points=self.args.max_path_points)

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

    def publish_paths(self) -> None:
        stamp = rospy.Time.now()
        self.truth_path.header.stamp = stamp
        self.cmd_path.header.stamp = stamp
        self.truth_path_pub.publish(self.truth_path)
        self.cmd_path_pub.publish(self.cmd_path)
        target_path = RosPath(header=Header(stamp=stamp, frame_id=self.args.path_frame))
        home_x, home_y = self.mission_home_xy if self.mission_home_xy else (0.0, 0.0)
        for x, y, z in [(home_x, home_y, self.args.takeoff_height), (self.args.target_x, self.args.target_y, self.args.target_z)]:
            ps = PoseStamped()
            ps.header = target_path.header
            ps.pose.position.x = x
            ps.pose.position.y = y
            ps.pose.position.z = z
            ps.pose.orientation.w = 1.0
            target_path.poses.append(ps)
        self.target_path_pub.publish(target_path)

    def make_hover_cmd(self, x: float, y: float, z: float) -> PositionCommand:
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        msg.trajectory_id = 0
        msg.position.x = x
        msg.position.y = y
        msg.position.z = z
        msg.yaw = self.args.yaw
        return msg

    def publish_takeoff_land(self, cmd: int, repeats: int = 8) -> None:
        msg = TakeoffLand()
        msg.takeoff_land_cmd = cmd
        for _ in range(repeats):
            self.takeoff_land_pub.publish(msg)
            rospy.sleep(0.1)

    def set_cmd_adapter_enabled(self, enabled: bool, repeats: int = 3) -> None:
        msg = Bool(data=enabled)
        for _ in range(repeats):
            self.cmd_adapter_enable_pub.publish(msg)
            rospy.sleep(0.05)

    def publish_trigger(self) -> None:
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.pose.position.x = self.args.target_x
        msg.pose.position.y = self.args.target_y
        msg.pose.position.z = self.args.target_z
        msg.pose.orientation.w = 1.0
        for _ in range(5):
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
            for _ in range(5):
                self.goalset_pub.publish(goal)
                rospy.sleep(0.1)

    def first_planner_trajectory_time(self) -> float | None:
        times = [t for t in (self.first_bspline_t, self.first_polytraj_t) if t is not None]
        return min(times) if times else None

    def wait_for_ready(self) -> bool:
        deadline = time.time() + self.args.ready_timeout_s
        rate = rospy.Rate(20)
        while not rospy.is_shutdown() and time.time() < deadline:
            self.publish_paths()
            if self.last_state and self.last_state.connected and self.last_odom and self.last_truth:
                return True
            rate.sleep()
        return False

    def run(self) -> int:
        if not self.wait_for_ready():
            self.write_outputs(status="blocked", blockers=["ready_timeout"])
            return 10
        if not self.last_odom:
            self.write_outputs(status="blocked", blockers=["home_odom_missing"])
            return 10

        home_x = float(self.last_odom["x"])
        home_y = float(self.last_odom["y"])
        self.mission_home_xy = (home_x, home_y)

        self.phase = "takeoff"
        self.publish_takeoff_land(TakeoffLand.TAKEOFF, repeats=self.args.takeoff_cmd_repeats)
        rate = rospy.Rate(self.args.hover_publish_hz)
        hover_start = time.time()
        hover_reached_time: float | None = None
        while not rospy.is_shutdown() and time.time() - hover_start < self.args.takeoff_timeout_s:
            self.hover_cmd_pub.publish(self.make_hover_cmd(home_x, home_y, self.args.takeoff_height))
            self.publish_paths()
            if self.last_odom and abs(self.last_odom["z"] - self.args.takeoff_height) < self.args.takeoff_z_tol:
                if hover_reached_time is None:
                    hover_reached_time = time.time()
                if time.time() - hover_reached_time >= self.args.pre_ego_hover_s:
                    break
            rate.sleep()

        if hover_reached_time is None:
            self.write_outputs(status="blocked", blockers=["takeoff_height_not_reached"])
            return 11

        self.phase = "ego_triggered"
        self.publish_trigger()
        takeover_deadline = time.time() + self.args.ego_takeover_timeout_s
        while not rospy.is_shutdown() and time.time() < takeover_deadline and self.first_planner_trajectory_time() is None:
            self.hover_cmd_pub.publish(self.make_hover_cmd(home_x, home_y, self.args.takeoff_height))
            self.publish_paths()
            rate.sleep()

        if self.first_planner_trajectory_time() is None:
            self.write_outputs(status="blocked", blockers=["ego_planner_trajectory_timeout"])
            return 12

        self.phase = "ego_execute"
        execute_start = time.time()
        target_hold_start: float | None = None
        while not rospy.is_shutdown() and time.time() - execute_start < self.args.execute_timeout_s:
            self.publish_paths()
            if self.last_odom:
                err = math.dist(
                    (self.last_odom["x"], self.last_odom["y"], self.last_odom["z"]),
                    (self.args.target_x, self.args.target_y, self.args.target_z),
                )
                if err <= self.args.target_reached_radius:
                    if target_hold_start is None:
                        target_hold_start = time.time()
                    if time.time() - target_hold_start >= self.args.target_hold_s:
                        break
                else:
                    target_hold_start = None
            rate.sleep()

        if target_hold_start is None:
            self.write_outputs(status="blocked", blockers=["target_not_reached"])
            return 13

        self.phase = "land"
        if self.args.disable_cmd_adapter_before_land:
            self.set_cmd_adapter_enabled(False)
            rospy.sleep(self.args.post_adapter_disable_wait_s)
        self.publish_takeoff_land(TakeoffLand.LAND, repeats=self.args.land_cmd_repeats)
        land_start = time.time()
        while not rospy.is_shutdown() and time.time() - land_start < self.args.land_timeout_s:
            self.publish_paths()
            if self.last_truth and self.last_truth["z"] < self.args.landed_z_max:
                break
            rate.sleep()

        self.phase = "done"
        acceptance_blockers = self.acceptance_blockers()
        if acceptance_blockers:
            self.write_outputs(status="blocked", blockers=acceptance_blockers)
            return 14
        self.write_outputs(status="passed", blockers=[])
        return 0

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
        if self.occupancy_last_points < self.args.min_occupancy_points:
            blockers.append("occupancy_points_below_gate")
        if self.bspline_count < self.args.min_bspline_count:
            blockers.append("bspline_count_below_gate")
        if self.bspline_count + self.polytraj_count < self.args.min_planner_traj_count:
            blockers.append("planner_trajectory_count_below_gate")
        if self.position_cmd_count < self.args.min_position_cmd_count:
            blockers.append("position_cmd_count_below_gate")
        if self.att_target_count < self.args.min_target_attitude_count:
            blockers.append("target_attitude_count_below_gate")
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

    def write_outputs(self, status: str, blockers: list[str]) -> None:
        self.write_csv(self.result_dir / "truth.csv", self.truth_rows)
        self.write_csv(self.result_dir / "odom.csv", self.odom_rows)
        self.write_csv(self.result_dir / "position_cmd.csv", self.position_cmd_rows)
        self.write_csv(self.result_dir / "bspline_summary.csv", self.bspline_rows)
        self.write_csv(self.result_dir / "target_attitude.csv", self.att_target_rows)
        self.write_csv(self.result_dir / "debug_px4ctrl.csv", self.debug_rows)
        final_err = None
        if self.last_odom:
            final_err = math.dist(
                (self.last_odom["x"], self.last_odom["y"], self.last_odom["z"]),
                (self.args.target_x, self.args.target_y, self.args.target_z),
            )
        summary = {
            "schema": "mosim.sunray_ros1.goal4_ego_single_metrics.v1",
            "status": status,
            "blockers": blockers,
            "target": {"x": self.args.target_x, "y": self.args.target_y, "z": self.args.target_z},
            "counts": {
                "truth_rows": len(self.truth_rows),
                "odom_rows": len(self.odom_rows),
                "position_cmd": self.position_cmd_count,
                "bspline": self.bspline_count,
                "polytraj": self.polytraj_count,
                "raw_lidar": self.lidar_count,
                "world_cloud": self.world_cloud_count,
                "occupancy_inflate": self.occupancy_count,
                "target_attitude": self.att_target_count,
                "debug_px4ctrl": self.debug_count,
            },
            "last_point_counts": {
                "raw_lidar": self.lidar_last_points,
                "world_cloud": self.world_cloud_last_points,
                "occupancy_inflate": self.occupancy_last_points,
            },
            "first_bspline_t": self.first_bspline_t,
            "first_polytraj_t": self.first_polytraj_t,
            "first_planner_trajectory_t": self.first_planner_trajectory_time(),
            "occupancy_last_points": self.occupancy_last_points,
            "final_target_error_m": final_err,
            "target_error_summary": self.target_error_summary(),
            "claim_boundary": "EGO planner/traj_server to original px4ctrl through MAVROS/PX4/Gazebo; state source is MAVROS local odom, Gazebo truth is evaluation only.",
        }
        (self.result_dir / "EGO_SINGLE_METRICS.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--raw-lidar-topic", default="/uav1/livox/lidar")
    parser.add_argument("--world-cloud-topic", default="/uav1/livox_world")
    parser.add_argument("--occupancy-topic", default="/drone_0_ego_planner_node/grid_map/occupancy_inflate")
    parser.add_argument("--bspline-topic", default="/drone_0_planning/bspline")
    parser.add_argument("--polytraj-topic", default="")
    parser.add_argument("--goalset-topic", default="")
    parser.add_argument("--goal-pose-topic", default="")
    parser.add_argument("--path-frame", default="world")
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
    parser.add_argument("--land-timeout-s", type=float, default=25.0)
    parser.add_argument("--pre-ego-hover-s", type=float, default=2.0)
    parser.add_argument("--target-hold-s", type=float, default=2.0)
    parser.add_argument("--takeoff-z-tol", type=float, default=0.12)
    parser.add_argument("--target-reached-radius", type=float, default=0.35)
    parser.add_argument("--landed-z-max", type=float, default=0.18)
    parser.add_argument("--min-raw-lidar-count", type=int, default=5)
    parser.add_argument("--min-raw-lidar-points", type=int, default=1)
    parser.add_argument("--min-world-cloud-count", type=int, default=5)
    parser.add_argument("--min-world-cloud-points", type=int, default=1)
    parser.add_argument("--min-occupancy-count", type=int, default=3)
    parser.add_argument("--min-occupancy-points", type=int, default=1)
    parser.add_argument("--min-bspline-count", type=int, default=0)
    parser.add_argument("--min-planner-traj-count", type=int, default=1)
    parser.add_argument("--min-position-cmd-count", type=int, default=10)
    parser.add_argument("--min-target-attitude-count", type=int, default=10)
    parser.add_argument("--hover-publish-hz", type=float, default=50.0)
    parser.add_argument("--record-hz", type=float, default=30.0)
    parser.add_argument("--record-cmd-hz", type=float, default=50.0)
    parser.add_argument("--max-path-points", type=int, default=5000)
    parser.add_argument("--takeoff-cmd-repeats", type=int, default=8)
    parser.add_argument("--land-cmd-repeats", type=int, default=8)
    parser.add_argument("--cmd-adapter-enable-topic", default="/mosim/goal4/position_cmd_adapter_enable")
    parser.add_argument("--disable-cmd-adapter-before-land", action="store_true")
    parser.add_argument("--post-adapter-disable-wait-s", type=float, default=0.8)
    return parser.parse_args()


def main() -> None:
    rospy.init_node("mosim_px4ctrl_ego_single_mission")
    mission = EgoSingleMission(parse_args())
    raise SystemExit(mission.run())


if __name__ == "__main__":
    main()
