#!/usr/bin/env python3
"""Keep Goal4 planner review paths visible in RViz after the mission exits."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Point, PoseStamped
from nav_msgs.msg import Path as RosPath
from quadrotor_msgs.msg import PositionCommand
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray


def read_pose_rows(csv_path: Path, max_points: int) -> list[dict]:
    if not csv_path.exists():
        return []
    rows = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append(
                    {
                        "x": float(row["x"]),
                        "y": float(row["y"]),
                        "z": float(row["z"]),
                        "roll": float(row.get("roll", 0.0) or 0.0),
                        "pitch": float(row.get("pitch", 0.0) or 0.0),
                        "yaw": float(row.get("yaw", 0.0) or 0.0),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue
    if max_points > 0 and len(rows) > max_points:
        stride = max(1, len(rows) // max_points)
        rows = rows[::stride][:max_points]
    return rows


def read_path(csv_path: Path, frame_id: str, max_points: int) -> RosPath:
    path = RosPath(header=Header(frame_id=frame_id))
    rows = read_pose_rows(csv_path, max_points)
    stamp = rospy.Time.now()
    for row in rows:
        pose = PoseStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = frame_id
        pose.pose.position.x = row["x"]
        pose.pose.position.y = row["y"]
        pose.pose.position.z = row["z"]
        pose.pose.orientation.w = 1.0
        path.poses.append(pose)
    path.header.stamp = stamp
    return path


def read_last_pose(csv_path: Path) -> dict | None:
    if not csv_path.exists():
        return None
    last = None
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                last = {
                    "x": float(row["x"]),
                    "y": float(row["y"]),
                    "z": float(row["z"]),
                    "roll": float(row.get("roll", 0.0)),
                    "pitch": float(row.get("pitch", 0.0)),
                    "yaw": float(row.get("yaw", 0.0)),
                }
            except (KeyError, TypeError, ValueError):
                continue
    return last


def quat_from_rpy(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def rpy_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return roll, pitch, yaw


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


def make_body_axes(row: dict, frame_id: str, args: argparse.Namespace) -> MarkerArray:
    pos = (row["x"], row["y"], row["z"])
    q = quat_from_rpy(row["roll"], row["pitch"], row["yaw"])
    axes = (
        (0, "body_x_forward", (1.0, 0.0, 0.0), (1.0, 0.05, 0.05, 1.0)),
        (1, "body_y_left", (0.0, 1.0, 0.0), (0.05, 1.0, 0.05, 1.0)),
        (2, "body_z_up", (0.0, 0.0, 1.0), (0.1, 0.35, 1.0, 1.0)),
    )
    markers = MarkerArray()
    stamp = rospy.Time.now()
    for marker_id, name, axis, color in axes:
        direction = quat_rotate(q, axis)
        marker = Marker()
        marker.header.stamp = stamp
        marker.header.frame_id = frame_id
        marker.ns = name
        marker.id = marker_id
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.points = [
            Point(x=pos[0], y=pos[1], z=pos[2]),
            Point(
                x=pos[0] + direction[0] * args.body_axis_length_m,
                y=pos[1] + direction[1] * args.body_axis_length_m,
                z=pos[2] + direction[2] * args.body_axis_length_m,
            ),
        ]
        marker.scale.x = args.body_axis_shaft_m
        marker.scale.y = args.body_axis_head_diameter_m
        marker.scale.z = args.body_axis_head_length_m
        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = color[3]
        # The keep-alive process is the owner after the mission exits.  A
        # finite lifetime makes the last pose disappear during any publish
        # gap, so keep the latched review marker persistent.
        marker.lifetime = rospy.Duration(0)
        markers.markers.append(marker)
    return markers


def append_pose(path: RosPath, frame_id: str, x: float, y: float, z: float, max_points: int) -> None:
    pose = PoseStamped()
    pose.header.stamp = rospy.Time.now()
    pose.header.frame_id = frame_id
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = z
    pose.pose.orientation.w = 1.0
    path.header.stamp = pose.header.stamp
    path.header.frame_id = frame_id
    path.poses.append(pose)
    if max_points > 0 and len(path.poses) > max_points:
        path.poses = path.poses[-max_points:]


def moved_enough(last: tuple[float, float, float] | None, current: tuple[float, float, float], min_step: float) -> bool:
    if last is None:
        return True
    return math.dist(last, current) >= min_step


def target_path(args: argparse.Namespace) -> RosPath:
    path = RosPath(header=Header(stamp=rospy.Time.now(), frame_id=args.frame_id))
    for x, y, z in ((0.0, 0.0, args.target_z), (args.target_x, args.target_y, args.target_z)):
        pose = PoseStamped()
        pose.header = path.header
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = 1.0
        path.poses.append(pose)
    return path


class LiveReviewState:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.truth_path = RosPath(header=Header(frame_id=args.frame_id))
        self.cmd_path = RosPath(header=Header(frame_id=args.frame_id))
        self.last_truth_row: dict | None = None
        self.last_truth_point: tuple[float, float, float] | None = None
        self.last_cmd_point: tuple[float, float, float] | None = None
        self.last_truth_wall = 0.0
        self.last_cmd_wall = 0.0
        if not args.disable_live:
            rospy.Subscriber(args.live_truth_topic, ModelStates, self.on_model_states, queue_size=30)
            rospy.Subscriber(args.live_cmd_topic, PositionCommand, self.on_position_cmd, queue_size=100)

    def on_model_states(self, msg: ModelStates) -> None:
        try:
            idx = list(msg.name).index(self.args.truth_model_name)
        except ValueError:
            return
        pose = msg.pose[idx]
        q = pose.orientation
        roll, pitch, yaw = rpy_from_quat(q.x, q.y, q.z, q.w)
        point = (float(pose.position.x), float(pose.position.y), float(pose.position.z))
        self.last_truth_row = {
            "x": point[0],
            "y": point[1],
            "z": point[2],
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        self.last_truth_wall = rospy.get_time()
        if moved_enough(self.last_truth_point, point, self.args.min_path_step_m):
            append_pose(self.truth_path, self.args.frame_id, point[0], point[1], point[2], self.args.max_points)
            self.last_truth_point = point

    def on_position_cmd(self, msg: PositionCommand) -> None:
        point = (float(msg.position.x), float(msg.position.y), float(msg.position.z))
        self.last_cmd_wall = rospy.get_time()
        if moved_enough(self.last_cmd_point, point, self.args.min_path_step_m):
            append_pose(self.cmd_path, self.args.frame_id, point[0], point[1], point[2], self.args.max_points)
            self.last_cmd_point = point

    def live_truth_available(self) -> bool:
        return bool(self.truth_path.poses) and rospy.get_time() - self.last_truth_wall <= self.args.live_timeout_s

    def live_cmd_available(self) -> bool:
        return bool(self.cmd_path.poses) and rospy.get_time() - self.last_cmd_wall <= self.args.live_timeout_s


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--target-x", type=float, default=4.0)
    parser.add_argument("--target-y", type=float, default=1.0)
    parser.add_argument("--target-z", type=float, default=1.0)
    parser.add_argument("--truth-topic", default="/mosim/goal4/truth_path")
    parser.add_argument("--cmd-topic", default="/mosim/goal4/position_cmd_path")
    parser.add_argument("--planner-cmd-topic", default="/mosim/goal4/planner_position_cmd_raw_path")
    parser.add_argument("--target-topic", default="/mosim/goal4/target_path")
    parser.add_argument("--body-axes-topic", default="/mosim/goal4/body_axes")
    parser.add_argument("--live-truth-topic", default="/gazebo/model_states")
    parser.add_argument("--live-cmd-topic", default="/position_cmd")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--publish-hz", type=float, default=2.0)
    parser.add_argument("--max-points", type=int, default=5000)
    parser.add_argument("--min-path-step-m", type=float, default=0.01)
    parser.add_argument("--live-timeout-s", type=float, default=2.0)
    parser.add_argument("--disable-live", action="store_true")
    parser.add_argument("--disable-static-target", action="store_true")
    parser.add_argument("--body-axis-length-m", type=float, default=0.25)
    parser.add_argument("--body-axis-shaft-m", type=float, default=0.012)
    parser.add_argument("--body-axis-head-diameter-m", type=float, default=0.035)
    parser.add_argument("--body-axis-head-length-m", type=float, default=0.055)
    parser.add_argument("--body-axis-lifetime-s", type=float, default=1.5)
    parser.add_argument(
        "--body-axes-source",
        choices=("truth", "cmd", "planner_cmd"),
        default="truth",
        help="CSV source used for review body axes when live truth is unavailable.",
    )
    parser.add_argument(
        "--body-axes-replay",
        action="store_true",
        help="Cycle the review body axes through the selected CSV path instead of pinning it to the last sample.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("mosim_goal4_path_hold_from_csv", anonymous=False)
    result_dir = Path(args.result_dir)
    truth_pub = rospy.Publisher(args.truth_topic, RosPath, queue_size=1, latch=True)
    cmd_pub = rospy.Publisher(args.cmd_topic, RosPath, queue_size=1, latch=True)
    planner_cmd_pub = rospy.Publisher(args.planner_cmd_topic, RosPath, queue_size=1, latch=True)
    target_pub = rospy.Publisher(args.target_topic, RosPath, queue_size=1, latch=True)
    # Keep the last review pose available to RViz subscribers that start late.
    axes_pub = rospy.Publisher(args.body_axes_topic, MarkerArray, queue_size=1, latch=True)
    live = LiveReviewState(args)
    rate = rospy.Rate(args.publish_hz)
    axes_replay_index = 0
    last_truth_path: RosPath | None = None
    last_cmd_path: RosPath | None = None
    last_planner_cmd_path: RosPath | None = None
    while not rospy.is_shutdown():
        truth = live.truth_path if live.live_truth_available() else read_path(result_dir / "truth.csv", args.frame_id, args.max_points)
        cmd = live.cmd_path if live.live_cmd_available() else read_path(result_dir / "position_cmd.csv", args.frame_id, args.max_points)
        planner_cmd = read_path(result_dir / "planner_position_cmd_raw.csv", args.frame_id, args.max_points)

        # Do not replace a real path with an empty fallback while the mission
        # is still writing its CSVs or a live topic is momentarily quiet.
        if truth.poses:
            last_truth_path = truth
        if cmd.poses:
            last_cmd_path = cmd
        if planner_cmd.poses:
            last_planner_cmd_path = planner_cmd
        if last_truth_path is not None:
            last_truth_path.header.stamp = rospy.Time.now()
            truth_pub.publish(last_truth_path)
        if last_cmd_path is not None:
            last_cmd_path.header.stamp = rospy.Time.now()
            cmd_pub.publish(last_cmd_path)
        if last_planner_cmd_path is not None:
            last_planner_cmd_path.header.stamp = rospy.Time.now()
            planner_cmd_pub.publish(last_planner_cmd_path)
        if not args.disable_static_target:
            target_pub.publish(target_path(args))
        axes_pose = None
        if live.live_truth_available() and args.body_axes_source == "truth" and not args.body_axes_replay:
            axes_pose = live.last_truth_row
        else:
            csv_name = {
                "truth": "truth.csv",
                "cmd": "position_cmd.csv",
                "planner_cmd": "planner_position_cmd_raw.csv",
            }[args.body_axes_source]
            if args.body_axes_replay:
                axes_rows = read_pose_rows(result_dir / csv_name, args.max_points)
                if axes_rows:
                    axes_pose = axes_rows[axes_replay_index % len(axes_rows)]
                    axes_replay_index += 1
            else:
                axes_pose = read_last_pose(result_dir / csv_name)
        if axes_pose is not None:
            axes_pub.publish(make_body_axes(axes_pose, args.frame_id, args))
        rate.sleep()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
