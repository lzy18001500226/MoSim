#!/usr/bin/env python3
"""Publish RViz review paths for Gazebo truth and reference commands.

This node is visual-review support only. It subscribes to the Gazebo dynamic
pose topic and optional PositionCommand references, then publishes
``nav_msgs/Path`` topics for RViz. It never publishes setpoints, controller
outputs, or actuator commands.
"""

from __future__ import annotations

import argparse
import json
import math
import queue
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path as NavPath
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


ROOT = Path(__file__).resolve().parents[2]
for helper_dir in (ROOT / "Scripts" / "gazebo", ROOT / "Scripts" / "ros"):
    if str(helper_dir) not in sys.path:
        sys.path.insert(0, str(helper_dir))

from gazebo_truth_planner_setpoint_tracker import (  # noqa: E402
    iter_stdin_message_chunks,
    parse_truth_samples,
)


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


def finite_pose(pose: Any) -> bool:
    values = (
        float(pose.position.x),
        float(pose.position.y),
        float(pose.position.z),
        float(pose.orientation.x),
        float(pose.orientation.y),
        float(pose.orientation.z),
        float(pose.orientation.w),
    )
    return all(math.isfinite(value) for value in values)


def make_path(frame_id: str) -> NavPath:
    path = NavPath()
    path.header.frame_id = frame_id
    return path


class GazeboReviewPathPublisher(Node):
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__("mosim_gazebo_review_path_publisher")
        self.args = args
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=max(1, int(args.qos_depth)),
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        latched_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.truth_path = make_path(args.frame_id)
        self.reference_path = make_path(args.frame_id)
        self.truth_pub = self.create_publisher(NavPath, args.truth_path_topic, latched_qos)
        self.reference_pub = self.create_publisher(NavPath, args.reference_path_topic, latched_qos)
        self.reference_sub = None
        self.truth_process: subprocess.Popen[str] | None = None
        self.truth_thread: threading.Thread | None = None
        self.truth_stderr_thread: threading.Thread | None = None
        self.truth_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self.truth_stderr_tail: list[str] = []
        self.started = self.get_clock().now()
        self.last_truth = None
        self.last_reference = None
        self.last_summary = self.started
        self.truth_messages = 0
        self.truth_points = 0
        self.reference_messages = 0
        self.reference_points = 0
        self.dropped_truth_points = 0
        self.dropped_reference_points = 0
        self.should_stop = False

        if args.reference_topic:
            try:
                from mosim_msgs.msg import PositionCommand  # type: ignore

                self.reference_sub = self.create_subscription(
                    PositionCommand,
                    args.reference_topic,
                    self.on_reference_command,
                    qos,
                )
            except Exception as exc:  # pragma: no cover - runtime dependency
                self.get_logger().error(f"PositionCommand subscription unavailable: {exc}")
                self.reference_sub = None

        self.start_truth_stream()
        self.timer = self.create_timer(max(0.05, float(args.publish_period_s)), self.on_timer)

    def start_truth_stream(self) -> None:
        self.truth_process = subprocess.Popen(
            [self.args.gz_command, "topic", "-e", "-t", self.args.gz_truth_topic],
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.truth_thread = threading.Thread(target=self.read_truth_stdout, daemon=True)
        self.truth_stderr_thread = threading.Thread(target=self.read_truth_stderr, daemon=True)
        self.truth_thread.start()
        self.truth_stderr_thread.start()

    def read_truth_stdout(self) -> None:
        assert self.truth_process is not None
        assert self.truth_process.stdout is not None
        for chunk in iter_stdin_message_chunks(self.truth_process.stdout):
            samples = parse_truth_samples(
                chunk,
                model_name=self.args.model_name,
                topic=self.args.gz_truth_topic,
                frame_id=self.args.frame_id,
            )
            for sample in samples:
                self.truth_queue.put(sample)

    def read_truth_stderr(self) -> None:
        assert self.truth_process is not None
        assert self.truth_process.stderr is not None
        for line in self.truth_process.stderr:
            self.truth_stderr_tail.append(line.rstrip())
            del self.truth_stderr_tail[:-20]

    def destroy_node(self) -> bool:
        if self.truth_process is not None and self.truth_process.poll() is None:
            self.truth_process.terminate()
            try:
                self.truth_process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.truth_process.kill()
                self.truth_process.wait(timeout=2.0)
        return super().destroy_node()

    def append_pose(self, path: NavPath, pose_stamped: PoseStamped, *, truth: bool) -> None:
        if len(path.poses) >= int(self.args.max_points):
            path.poses.pop(0)
        path.poses.append(pose_stamped)
        if truth:
            self.truth_points = len(path.poses)
        else:
            self.reference_points = len(path.poses)

    def on_truth_sample(self, sample: dict[str, Any]) -> None:
        position = sample.get("position_m")
        orientation = sample.get("orientation_xyzw")
        if not isinstance(position, list) or len(position) != 3:
            self.dropped_truth_points += 1
            return
        if not isinstance(orientation, list) or len(orientation) != 4:
            self.dropped_truth_points += 1
            return
        stamped = PoseStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = self.args.frame_id
        stamped.pose.position.x = float(position[0])
        stamped.pose.position.y = float(position[1])
        stamped.pose.position.z = float(position[2])
        stamped.pose.orientation.x = float(orientation[0])
        stamped.pose.orientation.y = float(orientation[1])
        stamped.pose.orientation.z = float(orientation[2])
        stamped.pose.orientation.w = float(orientation[3])
        if not finite_pose(stamped.pose):
            self.dropped_truth_points += 1
            return
        self.truth_path.header.stamp = stamped.header.stamp
        self.append_pose(self.truth_path, stamped, truth=True)
        self.last_truth = self.get_clock().now()

    def on_reference_command(self, msg: Any) -> None:
        self.reference_messages += 1
        stamped = PoseStamped()
        stamped.header.stamp = msg.header.stamp if msg.header.stamp.sec or msg.header.stamp.nanosec else self.get_clock().now().to_msg()
        stamped.header.frame_id = self.args.frame_id
        stamped.pose.position.x = float(msg.position.x)
        stamped.pose.position.y = float(msg.position.y)
        stamped.pose.position.z = float(msg.position.z)
        stamped.pose.orientation.w = 1.0
        if not finite_pose(stamped.pose):
            self.dropped_reference_points += 1
            return
        self.reference_path.header.stamp = stamped.header.stamp
        self.append_pose(self.reference_path, stamped, truth=False)
        self.last_reference = self.get_clock().now()

    def on_timer(self) -> None:
        now = self.get_clock().now()
        while True:
            try:
                sample = self.truth_queue.get_nowait()
            except queue.Empty:
                break
            self.truth_messages += 1
            self.on_truth_sample(sample)
        self.truth_path.header.stamp = now.to_msg()
        self.reference_path.header.stamp = now.to_msg()
        if self.truth_path.poses:
            self.truth_pub.publish(self.truth_path)
        if self.reference_path.poses:
            self.reference_pub.publish(self.reference_path)
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
        payload: dict[str, Any] = {
            "schema": "mosim.gazebo_rviz_review_paths.v1",
            "status": status,
            "gz_truth_topic": self.args.gz_truth_topic,
            "gz_command": self.args.gz_command,
            "model_name": self.args.model_name,
            "reference_topic": self.args.reference_topic,
            "truth_path_topic": self.args.truth_path_topic,
            "reference_path_topic": self.args.reference_path_topic,
            "frame_id": self.args.frame_id,
            "truth_messages": self.truth_messages,
            "truth_points": self.truth_points,
            "reference_messages": self.reference_messages,
            "reference_points": self.reference_points,
            "dropped_truth_points": self.dropped_truth_points,
            "dropped_reference_points": self.dropped_reference_points,
            "max_points": int(self.args.max_points),
            "truth_stream_returncode": self.truth_process.poll() if self.truth_process else None,
            "truth_stream_stderr_tail": self.truth_stderr_tail[-5:],
            "outputs": {
                "summary_json": rel(summary_json),
            },
            "claim_boundary": [
                "RViz visual-review paths only.",
                "Actual path is filtered by Gazebo entity name; it is not PoseArray index 0.",
                "This node does not publish setpoints, controller outputs, or actuator commands.",
                "Gazebo remains the vehicle/world animation surface; RViz is the path, point-cloud, and occupancy review surface.",
            ],
        }
        summary_json.parent.mkdir(parents=True, exist_ok=True)
        summary_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gz-truth-topic", default="/world/sunray150_single_uav_competition_light/dynamic_pose/info")
    parser.add_argument("--gz-command", default="ign")
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--reference-topic", default="/position_cmd")
    parser.add_argument("--truth-path-topic", default="/mosim/review/actual_path")
    parser.add_argument("--reference-path-topic", default="/mosim/review/reference_path")
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--max-points", type=int, default=5000)
    parser.add_argument("--qos-depth", type=int, default=50)
    parser.add_argument("--publish-period-s", type=float, default=0.05)
    parser.add_argument("--summary-period-s", type=float, default=2.0)
    parser.add_argument("--duration-s", type=float, default=0.0)
    parser.add_argument("--summary-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_points < 2:
        raise SystemExit("max-points must be at least 2")
    rclpy.init()
    node = GazeboReviewPathPublisher(args)
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
