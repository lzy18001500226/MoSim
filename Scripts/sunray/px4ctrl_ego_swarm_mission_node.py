#!/usr/bin/env python3
"""Goal5 EGO-Swarm gate for per-UAV EGO -> original px4ctrl -> PX4/Gazebo."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path

import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import AttitudeTarget, State
from nav_msgs.msg import Odometry, Path as RosPath
from quadrotor_msgs.msg import PositionCommand, Px4ctrlDebug, TakeoffLand
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
from traj_utils.msg import Bspline


@dataclass
class UavRuntime:
    uid: int
    drone_id: int
    target: tuple[float, float, float]
    start_xy: tuple[float, float]
    takeoff_land_pub: rospy.Publisher
    hover_cmd_pub: rospy.Publisher
    truth_path_pub: rospy.Publisher
    cmd_path_pub: rospy.Publisher
    state: State | None = None
    truth: dict | None = None
    odom: dict | None = None
    position_cmd: dict | None = None
    bspline_count: int = 0
    raw_lidar_count: int = 0
    raw_lidar_points: int = 0
    world_cloud_count: int = 0
    world_cloud_points: int = 0
    occupancy_count: int = 0
    occupancy_points: int = 0
    target_attitude_count: int = 0
    debug_count: int = 0
    first_bspline_t: float | None = None
    reached_t: float | None = None
    truth_rows: list[dict] = field(default_factory=list)
    odom_rows: list[dict] = field(default_factory=list)
    cmd_rows: list[dict] = field(default_factory=list)
    bspline_rows: list[dict] = field(default_factory=list)
    att_rows: list[dict] = field(default_factory=list)
    debug_rows: list[dict] = field(default_factory=list)
    truth_path: RosPath = field(default_factory=lambda: RosPath(header=Header(frame_id="world")))
    cmd_path: RosPath = field(default_factory=lambda: RosPath(header=Header(frame_id="world")))
    last_record_t: dict[str, float] = field(default_factory=lambda: {"truth": -1e9, "odom": -1e9, "cmd": -1e9, "att": -1e9, "debug": -1e9})


class EgoSwarmMission:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.start_wall = time.time()
        self.phase = "init"
        self.uavs: dict[int, UavRuntime] = {}
        self.min_inter_uav_distance = float("inf")
        self.min_inter_uav_pair: tuple[int, int] | None = None
        self.separation_rows: list[dict] = []
        self.last_sep_record_t = -1e9
        self.trigger_pub = rospy.Publisher("/traj_start_trigger", PoseStamped, queue_size=3, latch=True)
        self.target_path_pub = rospy.Publisher("/mosim/goal5/target_path", RosPath, queue_size=1, latch=True)

        for uid in range(1, args.uav_num + 1):
            target = self.target_for(uid)
            start_xy = self.start_xy_for(uid)
            uav = UavRuntime(
                uid=uid,
                drone_id=uid - 1,
                target=target,
                start_xy=start_xy,
                takeoff_land_pub=rospy.Publisher(f"/uav{uid}/px4ctrl/takeoff_land", TakeoffLand, queue_size=3, latch=True),
                hover_cmd_pub=rospy.Publisher(f"/uav{uid}/position_cmd", PositionCommand, queue_size=10),
                truth_path_pub=rospy.Publisher(f"/mosim/goal5/uav{uid}/truth_path", RosPath, queue_size=1, latch=True),
                cmd_path_pub=rospy.Publisher(f"/mosim/goal5/uav{uid}/position_cmd_path", RosPath, queue_size=1, latch=True),
            )
            uav.truth_path.header.frame_id = args.path_frame
            uav.cmd_path.header.frame_id = args.path_frame
            self.uavs[uid] = uav

            rospy.Subscriber(f"/uav{uid}/mavros/state", State, lambda msg, uid=uid: self.on_state(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/mavros/local_position/odom", Odometry, lambda msg, uid=uid: self.on_odom(uid, msg), queue_size=100)
            rospy.Subscriber(f"/uav{uid}/position_cmd", PositionCommand, lambda msg, uid=uid: self.on_position_cmd(uid, msg), queue_size=200)
            rospy.Subscriber(f"/drone_{uid - 1}_planning/bspline", Bspline, lambda msg, uid=uid: self.on_bspline(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/livox/lidar", PointCloud2, lambda msg, uid=uid: self.on_raw_lidar(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/livox_world", PointCloud2, lambda msg, uid=uid: self.on_world_cloud(uid, msg), queue_size=20)
            rospy.Subscriber(f"/drone_{uid - 1}_ego_planner_node/grid_map/occupancy_inflate", PointCloud2, lambda msg, uid=uid: self.on_occupancy(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/mavros/setpoint_raw/target_attitude", AttitudeTarget, lambda msg, uid=uid: self.on_att_target(uid, msg), queue_size=100)
            rospy.Subscriber(f"/uav{uid}/debugPx4ctrl", Px4ctrlDebug, lambda msg, uid=uid: self.on_debug(uid, msg), queue_size=100)

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=30)

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

    @staticmethod
    def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    @classmethod
    def rpy_from_quat(cls, x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        return roll, pitch, cls.yaw_from_quat(x, y, z, w)

    def on_state(self, uid: int, msg: State) -> None:
        self.uavs[uid].state = msg

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

    def on_position_cmd(self, uid: int, msg: PositionCommand) -> None:
        uav = self.uavs[uid]
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
        uav.position_cmd = row
        if self.should_record(uav, "cmd", t, self.args.record_cmd_hz):
            uav.cmd_rows.append(row)
            self.append_path(uav.cmd_path, row["x"], row["y"], row["z"], t)

    def on_bspline(self, uid: int, msg: Bspline) -> None:
        uav = self.uavs[uid]
        t = self.now()
        uav.bspline_count += 1
        if uav.first_bspline_t is None:
            uav.first_bspline_t = t
        uav.bspline_rows.append({"t": t, "traj_id": int(msg.traj_id), "order": int(msg.order), "pos_pts": len(msg.pos_pts), "knots": len(msg.knots)})

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

    def make_hover_cmd(self, uav: UavRuntime) -> PositionCommand:
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        msg.trajectory_id = 0
        msg.position.x = uav.start_xy[0]
        msg.position.y = uav.start_xy[1]
        msg.position.z = self.args.takeoff_height
        msg.yaw = self.args.yaw
        return msg

    def publish_takeoff_land(self, cmd: int, repeats: int) -> None:
        msg = TakeoffLand()
        msg.takeoff_land_cmd = cmd
        for _ in range(repeats):
            for uav in self.uavs.values():
                uav.takeoff_land_pub.publish(msg)
            rospy.sleep(0.1)

    def publish_hover_cmds(self) -> None:
        for uav in self.uavs.values():
            uav.hover_cmd_pub.publish(self.make_hover_cmd(uav))

    def publish_trigger(self) -> None:
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.pose.orientation.w = 1.0
        for _ in range(5):
            self.trigger_pub.publish(msg)
            rospy.sleep(0.1)

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

    def run(self) -> int:
        rate = rospy.Rate(self.args.hover_publish_hz)
        deadline = time.time() + self.args.ready_timeout_s
        while not rospy.is_shutdown() and time.time() < deadline:
            self.publish_paths()
            if self.all_ready():
                break
            rate.sleep()
        if not self.all_ready():
            self.write_outputs("blocked", ["ready_timeout"])
            return 10

        self.phase = "takeoff"
        self.publish_takeoff_land(TakeoffLand.TAKEOFF, self.args.takeoff_cmd_repeats)
        takeoff_start = time.time()
        hover_reached_time: float | None = None
        while not rospy.is_shutdown() and time.time() - takeoff_start < self.args.takeoff_timeout_s:
            self.publish_hover_cmds()
            self.publish_paths()
            if all(uav.odom and abs(uav.odom["z"] - self.args.takeoff_height) < self.args.takeoff_z_tol for uav in self.uavs.values()):
                if hover_reached_time is None:
                    hover_reached_time = time.time()
                if time.time() - hover_reached_time >= self.args.pre_ego_hover_s:
                    break
            else:
                hover_reached_time = None
            rate.sleep()
        if hover_reached_time is None:
            self.write_outputs("blocked", ["takeoff_height_not_reached"])
            return 11

        self.phase = "ego_triggered"
        self.publish_trigger()
        deadline = time.time() + self.args.ego_takeover_timeout_s
        while not rospy.is_shutdown() and time.time() < deadline:
            self.publish_hover_cmds()
            self.publish_paths()
            if all(uav.first_bspline_t is not None for uav in self.uavs.values()):
                break
            rate.sleep()
        if not all(uav.first_bspline_t is not None for uav in self.uavs.values()):
            self.write_outputs("blocked", ["ego_bspline_timeout"])
            return 12

        self.phase = "ego_execute"
        execute_start = time.time()
        while not rospy.is_shutdown() and time.time() - execute_start < self.args.execute_timeout_s:
            self.publish_paths()
            all_reached = True
            for uav in self.uavs.values():
                if not uav.odom:
                    all_reached = False
                    continue
                err = math.dist((uav.odom["x"], uav.odom["y"], uav.odom["z"]), uav.target)
                if err <= self.args.target_reached_radius:
                    if uav.reached_t is None:
                        uav.reached_t = time.time()
                else:
                    uav.reached_t = None
                if uav.reached_t is None or time.time() - uav.reached_t < self.args.target_hold_s:
                    all_reached = False
            if all_reached:
                break
            rate.sleep()
        if not all(uav.reached_t is not None for uav in self.uavs.values()):
            self.write_outputs("blocked", ["target_not_reached"])
            return 13

        self.phase = "land"
        self.publish_takeoff_land(TakeoffLand.LAND, self.args.land_cmd_repeats)
        land_start = time.time()
        while not rospy.is_shutdown() and time.time() - land_start < self.args.land_timeout_s:
            self.publish_paths()
            if all(uav.truth and uav.truth["z"] < self.args.landed_z_max for uav in self.uavs.values()):
                break
            rate.sleep()

        self.phase = "done"
        blockers = self.acceptance_blockers()
        if blockers:
            self.write_outputs("blocked", blockers)
            return 14
        self.write_outputs("passed", [])
        return 0

    def acceptance_blockers(self) -> list[str]:
        blockers: list[str] = []
        if self.min_inter_uav_distance < self.args.min_inter_uav_distance:
            blockers.append("inter_uav_distance_below_gate")
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
            if uav.bspline_count < self.args.min_bspline_count:
                blockers.append(prefix + "bspline_count_below_gate")
            if len(uav.cmd_rows) < self.args.min_position_cmd_count:
                blockers.append(prefix + "position_cmd_count_below_gate")
            if uav.target_attitude_count < self.args.min_target_attitude_count:
                blockers.append(prefix + "target_attitude_count_below_gate")
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

    def write_outputs(self, status: str, blockers: list[str]) -> None:
        per_uav = {}
        for uid, uav in self.uavs.items():
            prefix = f"uav{uid}_"
            self.write_csv(self.result_dir / f"{prefix}truth.csv", uav.truth_rows)
            self.write_csv(self.result_dir / f"{prefix}odom.csv", uav.odom_rows)
            self.write_csv(self.result_dir / f"{prefix}position_cmd.csv", uav.cmd_rows)
            self.write_csv(self.result_dir / f"{prefix}bspline_summary.csv", uav.bspline_rows)
            self.write_csv(self.result_dir / f"{prefix}target_attitude.csv", uav.att_rows)
            self.write_csv(self.result_dir / f"{prefix}debug_px4ctrl.csv", uav.debug_rows)
            final_err = None
            if uav.odom:
                final_err = math.dist((uav.odom["x"], uav.odom["y"], uav.odom["z"]), uav.target)
            per_uav[str(uid)] = {
                "target": {"x": uav.target[0], "y": uav.target[1], "z": uav.target[2]},
                "final_target_error_m": final_err,
                "first_bspline_t": uav.first_bspline_t,
                "counts": {
                    "truth_rows": len(uav.truth_rows),
                    "odom_rows": len(uav.odom_rows),
                    "position_cmd_rows": len(uav.cmd_rows),
                    "bspline": uav.bspline_count,
                    "raw_lidar": uav.raw_lidar_count,
                    "world_cloud": uav.world_cloud_count,
                    "occupancy_inflate": uav.occupancy_count,
                    "target_attitude": uav.target_attitude_count,
                    "debug_px4ctrl": uav.debug_count,
                },
                "last_point_counts": {
                    "raw_lidar": uav.raw_lidar_points,
                    "world_cloud": uav.world_cloud_points,
                    "occupancy_inflate": uav.occupancy_points,
                },
            }
        self.write_csv(self.result_dir / "inter_uav_separation.csv", self.separation_rows)
        summary = {
            "schema": "mosim.sunray_ros1.goal5_ego_swarm_metrics.v1",
            "status": status,
            "blockers": blockers,
            "uav_num": self.args.uav_num,
            "per_uav": per_uav,
            "min_inter_uav_distance_m": None if math.isinf(self.min_inter_uav_distance) else self.min_inter_uav_distance,
            "min_inter_uav_pair": self.min_inter_uav_pair,
            "claim_boundary": "EGO-Swarm planning/traj_server per UAV to original px4ctrl through MAVROS/PX4/Gazebo; no fake_drone, no Sunray native controller success claim, and Gazebo truth is evaluation only.",
        }
        (self.result_dir / "EGO_SWARM_METRICS.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--uav-num", type=int, choices=[2, 3], default=2)
    for uid, defaults in {
        1: (4.0, -1.0, 1.0, 0.0, -1.0),
        2: (4.0, 1.0, 1.0, 0.0, 1.0),
        3: (4.0, 0.0, 1.25, -1.5, 0.0),
    }.items():
        tx, ty, tz, sx, sy = defaults
        parser.add_argument(f"--target{uid}-x", dest=f"target{uid}_x", type=float, default=tx)
        parser.add_argument(f"--target{uid}-y", dest=f"target{uid}_y", type=float, default=ty)
        parser.add_argument(f"--target{uid}-z", dest=f"target{uid}_z", type=float, default=tz)
        parser.add_argument(f"--start{uid}-x", dest=f"start{uid}_x", type=float, default=sx)
        parser.add_argument(f"--start{uid}-y", dest=f"start{uid}_y", type=float, default=sy)
    parser.add_argument("--path-frame", default="world")
    parser.add_argument("--takeoff-height", type=float, default=1.0)
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--ready-timeout-s", type=float, default=60.0)
    parser.add_argument("--takeoff-timeout-s", type=float, default=45.0)
    parser.add_argument("--ego-takeover-timeout-s", type=float, default=45.0)
    parser.add_argument("--execute-timeout-s", type=float, default=100.0)
    parser.add_argument("--land-timeout-s", type=float, default=30.0)
    parser.add_argument("--pre-ego-hover-s", type=float, default=2.0)
    parser.add_argument("--target-hold-s", type=float, default=2.0)
    parser.add_argument("--takeoff-z-tol", type=float, default=0.15)
    parser.add_argument("--target-reached-radius", type=float, default=0.45)
    parser.add_argument("--landed-z-max", type=float, default=0.20)
    parser.add_argument("--min-inter-uav-distance", type=float, default=0.45)
    parser.add_argument("--min-raw-lidar-count", type=int, default=5)
    parser.add_argument("--min-raw-lidar-points", type=int, default=1)
    parser.add_argument("--min-world-cloud-count", type=int, default=5)
    parser.add_argument("--min-world-cloud-points", type=int, default=1)
    parser.add_argument("--min-occupancy-count", type=int, default=2)
    parser.add_argument("--min-occupancy-points", type=int, default=1)
    parser.add_argument("--min-bspline-count", type=int, default=1)
    parser.add_argument("--min-position-cmd-count", type=int, default=10)
    parser.add_argument("--min-target-attitude-count", type=int, default=10)
    parser.add_argument("--hover-publish-hz", type=float, default=50.0)
    parser.add_argument("--record-hz", type=float, default=30.0)
    parser.add_argument("--record-cmd-hz", type=float, default=50.0)
    parser.add_argument("--max-path-points", type=int, default=8000)
    parser.add_argument("--takeoff-cmd-repeats", type=int, default=8)
    parser.add_argument("--land-cmd-repeats", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    rospy.init_node("mosim_px4ctrl_ego_swarm_mission")
    raise SystemExit(EgoSwarmMission(parse_args()).run())


if __name__ == "__main__":
    main()
