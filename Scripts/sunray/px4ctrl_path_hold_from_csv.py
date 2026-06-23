#!/usr/bin/env python3
"""Keep px4ctrl review trajectories visible in RViz after the mission exits."""

import argparse
import csv
import math
from pathlib import Path

import rospy
from geometry_msgs.msg import Point, PoseStamped
from nav_msgs.msg import Path as RosPath
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray


def read_path(csv_path: Path, frame_id: str, max_points: int) -> RosPath:
    path = RosPath(header=Header(frame_id=frame_id))
    if not csv_path.exists():
        return path
    rows = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append((float(row["x"]), float(row["y"]), float(row["z"])))
            except (KeyError, TypeError, ValueError):
                continue
    if max_points > 0 and len(rows) > max_points:
        stride = max(1, len(rows) // max_points)
        rows = rows[::stride][:max_points]
    stamp = rospy.Time.now()
    for x, y, z in rows:
        pose = PoseStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = frame_id
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = 1.0
        path.poses.append(pose)
    path.header.stamp = stamp
    return path


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
        marker.lifetime = rospy.Duration(args.body_axis_lifetime_s)
        markers.markers.append(marker)
    return markers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--frame-id", default="camera_init")
    parser.add_argument("--truth-topic", default="/mosim/px4ctrl/truth_path")
    parser.add_argument("--reference-topic", default="/mosim/px4ctrl/reference_path")
    parser.add_argument("--body-axes-topic", default="/mosim/px4ctrl/body_axes")
    parser.add_argument("--publish-hz", type=float, default=2.0)
    parser.add_argument("--max-points", type=int, default=5000)
    parser.add_argument("--body-axis-length-m", type=float, default=0.09)
    parser.add_argument("--body-axis-shaft-m", type=float, default=0.007)
    parser.add_argument("--body-axis-head-diameter-m", type=float, default=0.018)
    parser.add_argument("--body-axis-head-length-m", type=float, default=0.024)
    parser.add_argument("--body-axis-lifetime-s", type=float, default=0.75)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("mosim_px4ctrl_path_hold_from_csv", anonymous=False)
    result_dir = Path(args.result_dir)
    truth_pub = rospy.Publisher(args.truth_topic, RosPath, queue_size=1, latch=True)
    ref_pub = rospy.Publisher(args.reference_topic, RosPath, queue_size=1, latch=True)
    axes_pub = rospy.Publisher(args.body_axes_topic, MarkerArray, queue_size=1)
    rate = rospy.Rate(args.publish_hz)
    while not rospy.is_shutdown():
        truth_csv = result_dir / "truth.csv"
        truth_path = read_path(truth_csv, args.frame_id, args.max_points)
        reference_path = read_path(result_dir / "reference.csv", args.frame_id, args.max_points)
        if truth_path.poses:
            truth_pub.publish(truth_path)
        if reference_path.poses:
            ref_pub.publish(reference_path)
        last_pose = read_last_pose(truth_csv)
        if last_pose is not None:
            axes_pub.publish(make_body_axes(last_pose, args.frame_id, args))
        rate.sleep()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
