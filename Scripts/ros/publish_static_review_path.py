#!/usr/bin/env python3
"""Publish a static RViz review path.

This node is visual-review support only. It publishes a ``nav_msgs/Path`` for
operator review and never publishes setpoints, controller outputs, or actuator
commands.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path as NavPath
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def finite(values: list[float]) -> bool:
    return all(math.isfinite(value) for value in values)


class StaticReviewPathPublisher(Node):
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__("mosim_static_review_path_publisher")
        self.args = args
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.path_pub = self.create_publisher(NavPath, args.path_topic, qos)
        self.path = NavPath()
        self.path.header.frame_id = args.frame_id
        for x, y, z in (
            (args.start_x, args.start_y, args.start_z),
            (args.goal_x, args.goal_y, args.goal_z),
        ):
            if not finite([x, y, z]):
                raise SystemExit("path points must be finite")
            stamped = PoseStamped()
            stamped.header.frame_id = args.frame_id
            stamped.pose.position.x = float(x)
            stamped.pose.position.y = float(y)
            stamped.pose.position.z = float(z)
            stamped.pose.orientation.w = 1.0
            self.path.poses.append(stamped)
        self.started = self.get_clock().now()
        self.last_summary = self.started
        self.publish_count = 0
        self.should_stop = False
        self.timer = self.create_timer(max(0.05, float(args.publish_period_s)), self.on_timer)

    def on_timer(self) -> None:
        now = self.get_clock().now()
        self.path.header.stamp = now.to_msg()
        for pose in self.path.poses:
            pose.header.stamp = self.path.header.stamp
        self.path_pub.publish(self.path)
        self.publish_count += 1
        if (now - self.last_summary) >= Duration(seconds=float(self.args.summary_period_s)):
            self.write_summary(status="running")
            self.last_summary = now
        if float(self.args.duration_s) > 0.0 and (now - self.started) >= Duration(seconds=float(self.args.duration_s)):
            self.write_summary(status="completed")
            self.should_stop = True

    def write_summary(self, *, status: str) -> None:
        if not self.args.summary_json:
            return
        summary_json = project_path(self.args.summary_json)
        payload = {
            "schema": "mosim.static_rviz_review_path.v1",
            "status": status,
            "path_topic": self.args.path_topic,
            "frame_id": self.args.frame_id,
            "point_count": len(self.path.poses),
            "publish_count": self.publish_count,
            "start_m": [self.args.start_x, self.args.start_y, self.args.start_z],
            "goal_m": [self.args.goal_x, self.args.goal_y, self.args.goal_z],
            "outputs": {
                "summary_json": rel(summary_json),
            },
            "claim_boundary": [
                "RViz visual-review reference path only.",
                "This node does not publish setpoints, controller outputs, or actuator commands.",
            ],
        }
        summary_json.parent.mkdir(parents=True, exist_ok=True)
        summary_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path-topic", default="/mosim/review/reference_path")
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--start-x", type=float, required=True)
    parser.add_argument("--start-y", type=float, required=True)
    parser.add_argument("--start-z", type=float, required=True)
    parser.add_argument("--goal-x", type=float, required=True)
    parser.add_argument("--goal-y", type=float, required=True)
    parser.add_argument("--goal-z", type=float, required=True)
    parser.add_argument("--publish-period-s", type=float, default=0.2)
    parser.add_argument("--summary-period-s", type=float, default=2.0)
    parser.add_argument("--duration-s", type=float, default=0.0)
    parser.add_argument("--summary-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rclpy.init()
    node = StaticReviewPathPublisher(args)
    try:
        while rclpy.ok() and not node.should_stop:
            rclpy.spin_once(node, timeout_sec=0.1)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.write_summary(status="completed")
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
