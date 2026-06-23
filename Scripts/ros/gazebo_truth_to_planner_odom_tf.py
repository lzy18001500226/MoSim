#!/usr/bin/env python3
"""Publish planner odometry and TF from Gazebo transport truth pose.

This bridge is for real EGO closed-loop gates. EGO needs the vehicle state to
move with the Gazebo plant; a static TF is enough for smoke tests but invalid
for closed-loop planning/execution acceptance.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def number_after(label: str, text: str) -> float | None:
    match = re.search(rf"^\s*{re.escape(label)}:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*$", text, re.M)
    return float(match.group(1)) if match else None


def string_after(label: str, text: str) -> str | None:
    match = re.search(rf'^\s*{re.escape(label)}:\s*"([^"]+)"\s*$', text, re.M)
    return match.group(1) if match else None


def first_balanced_block(text: str, label: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(label)}\s*\{{", text)
    if not match:
        return None
    brace = text.find("{", match.start())
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1 : index]
    return None


def parse_header_time(block: str) -> float | None:
    header = first_balanced_block(block, "header")
    if header is None:
        return None
    stamp = first_balanced_block(header, "stamp") or header
    sec = number_after("sec", stamp)
    nsec = number_after("nsec", stamp)
    if nsec is None:
        nsec = number_after("nanosec", stamp)
    if sec is None:
        return None
    return float(sec) + float(nsec or 0.0) * 1e-9


def iter_pose_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    index = 0
    while True:
        start = text.find("pose {", index)
        if start < 0:
            break
        brace = text.find("{", start)
        depth = 0
        end = brace
        while end < len(text):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start : end + 1])
                    index = end + 1
                    break
            end += 1
        else:
            break
    return blocks


def xyz_from_section(block: str, section: str) -> tuple[float, float, float]:
    match = re.search(rf"{re.escape(section)}\s*\{{(?P<body>.*?)^\s*\}}", block, re.S | re.M)
    body = match.group("body") if match else ""
    return (
        float(number_after("x", body) or 0.0),
        float(number_after("y", body) or 0.0),
        float(number_after("z", body) or 0.0),
    )


def xyzw_from_orientation(block: str) -> tuple[float, float, float, float]:
    match = re.search(r"orientation\s*\{(?P<body>.*?)^\s*\}", block, re.S | re.M)
    body = match.group("body") if match else ""
    return (
        float(number_after("x", body) or 0.0),
        float(number_after("y", body) or 0.0),
        float(number_after("z", body) or 0.0),
        float(number_after("w", body) if number_after("w", body) is not None else 1.0),
    )


def iter_message_chunks(text: str) -> list[str]:
    chunks = [chunk for chunk in re.split(r"(?m)^---\s*$", text) if chunk.strip()]
    output: list[str] = []
    for chunk in chunks:
        starts = [match.start() for match in re.finditer(r"(?m)^header\s*\{", chunk)]
        if len(starts) <= 1:
            output.append(chunk)
            continue
        starts.append(len(chunk))
        for index in range(len(starts) - 1):
            message = chunk[starts[index] : starts[index + 1]].strip()
            if message:
                output.append(message)
    return output


def parse_sample(chunk: str, *, model_name: str) -> dict[str, Any] | None:
    time_s = parse_header_time(chunk)
    pose_blocks = iter_pose_blocks(chunk)
    if not pose_blocks and re.search(r"(?m)^position\s*\{", chunk):
        pose_blocks = [chunk]
    for pose_block in pose_blocks:
        actual_name = string_after("name", pose_block)
        if actual_name != model_name and not (actual_name or "").endswith(f"::{model_name}"):
            continue
        return {
            "time_s": time_s,
            "position_m": xyz_from_section(pose_block, "position"),
            "orientation_xyzw": xyzw_from_orientation(pose_block),
            "source_entity_name": actual_name,
        }
    return None


def normalize_quaternion(q: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    x, y, z, w = q
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm <= 0:
        return (0.0, 0.0, 0.0, 1.0)
    return (x / norm, y / norm, z / norm, w / norm)


def rotate_point(
    point: tuple[float, float, float],
    quaternion_xyzw: tuple[float, float, float, float],
) -> tuple[float, float, float]:
    x, y, z, w = normalize_quaternion(quaternion_xyzw)
    px, py, pz = point
    tx = 2.0 * (y * pz - z * py)
    ty = 2.0 * (z * px - x * pz)
    tz = 2.0 * (x * py - y * px)
    return (
        px + w * tx + (y * tz - z * ty),
        py + w * ty + (z * tx - x * tz),
        pz + w * tz + (x * ty - y * tx),
    )


def stamp_from_seconds(time_msg_type: Any, seconds: float) -> Any:
    msg = time_msg_type()
    if not math.isfinite(seconds) or seconds < 0:
        seconds = time.time()
    whole = math.floor(seconds)
    msg.sec = int(whole)
    msg.nanosec = int(round((seconds - whole) * 1_000_000_000))
    if msg.nanosec >= 1_000_000_000:
        msg.sec += 1
        msg.nanosec -= 1_000_000_000
    return msg


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gz-command", default="ign")
    parser.add_argument("--gz-topic", default="/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info")
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--map-frame", default="map")
    parser.add_argument("--body-frame", default="sunray150_assembled/base_link")
    parser.add_argument("--sensor-frame", default="sunray150_assembled/base_link/mid360_lidar")
    parser.add_argument("--planner-odom-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--mosim-planner-odom-topic", default="/mosim/planner/odom")
    parser.add_argument("--sensor-offset", default="0.035,0,0.045")
    parser.add_argument("--poll-sleep-s", type=float, default=0.02)
    parser.add_argument("--poll-timeout-s", type=float, default=0.5)
    parser.add_argument("--stream-idle-report-s", type=float, default=2.0)
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_json = project_path(args.output_json)
    try:
        import rclpy  # type: ignore
        from builtin_interfaces.msg import Time  # type: ignore
        from geometry_msgs.msg import TransformStamped  # type: ignore
        from nav_msgs.msg import Odometry  # type: ignore
        from std_msgs.msg import Header  # type: ignore
        from tf2_ros import TransformBroadcaster  # type: ignore
    except ImportError as exc:
        print("ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    sensor_offset = tuple(float(item) for item in str(args.sensor_offset).split(","))
    if len(sensor_offset) != 3 or not all(math.isfinite(item) for item in sensor_offset):
        raise SystemExit("--sensor-offset must be x,y,z")

    rclpy.init()
    node = rclpy.create_node("mosim_gazebo_truth_to_planner_odom_tf")
    tf_broadcaster = TransformBroadcaster(node)
    planner_odom_pub = node.create_publisher(Odometry, args.planner_odom_topic, 10)
    mosim_odom_pub = node.create_publisher(Odometry, args.mosim_planner_odom_topic, 10)

    counts = {
        "poll_attempts": 0,
        "poll_timeouts": 0,
        "poll_failures": 0,
        "stream_starts": 0,
        "stream_lines_read": 0,
        "stream_messages_completed": 0,
        "stream_restarts": 0,
        "chunks_parsed": 0,
        "samples_matched": 0,
        "odom_published": 0,
        "tf_published": 0,
    }
    last_position: tuple[float, float, float] | None = None
    last_time: float | None = None
    last_wall_time: float | None = None
    last_report = time.monotonic()
    stop_requested = {"value": False}
    stream_process: subprocess.Popen[str] | None = None

    def request_stop(_signum: int, _frame: Any) -> None:
        stop_requested["value"] = True
        if stream_process is not None and stream_process.poll() is None:
            stream_process.terminate()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    def publish(sample: dict[str, Any]) -> None:
        nonlocal last_position, last_time, last_wall_time
        position = tuple(float(item) for item in sample["position_m"])
        orientation = normalize_quaternion(tuple(float(item) for item in sample["orientation_xyzw"]))
        now_s = node.get_clock().now().nanoseconds / 1_000_000_000
        stamp = stamp_from_seconds(Time, now_s)

        velocity = (0.0, 0.0, 0.0)
        source_time = sample.get("time_s")
        if last_position is not None:
            dt = None
            if isinstance(source_time, float) and last_time is not None and source_time > last_time:
                dt = source_time - last_time
            if dt is None or dt <= 0:
                dt = max(time.monotonic() - (last_wall_time or time.monotonic()), 1e-3)
            velocity = (
                (position[0] - last_position[0]) / dt,
                (position[1] - last_position[1]) / dt,
                (position[2] - last_position[2]) / dt,
            )
        last_position = position
        last_time = float(source_time) if isinstance(source_time, float) else last_time
        last_wall_time = time.monotonic()

        header = Header(stamp=stamp, frame_id=args.map_frame)
        odom = Odometry()
        odom.header = header
        odom.child_frame_id = args.body_frame
        odom.pose.pose.position.x = position[0]
        odom.pose.pose.position.y = position[1]
        odom.pose.pose.position.z = position[2]
        odom.pose.pose.orientation.x = orientation[0]
        odom.pose.pose.orientation.y = orientation[1]
        odom.pose.pose.orientation.z = orientation[2]
        odom.pose.pose.orientation.w = orientation[3]
        odom.twist.twist.linear.x = velocity[0]
        odom.twist.twist.linear.y = velocity[1]
        odom.twist.twist.linear.z = velocity[2]
        planner_odom_pub.publish(odom)
        mosim_odom_pub.publish(odom)
        counts["odom_published"] += 1

        body_tf = TransformStamped()
        body_tf.header = header
        body_tf.child_frame_id = args.body_frame
        body_tf.transform.translation.x = position[0]
        body_tf.transform.translation.y = position[1]
        body_tf.transform.translation.z = position[2]
        body_tf.transform.rotation.x = orientation[0]
        body_tf.transform.rotation.y = orientation[1]
        body_tf.transform.rotation.z = orientation[2]
        body_tf.transform.rotation.w = orientation[3]

        sensor_position = rotate_point(sensor_offset, orientation)
        sensor_tf = TransformStamped()
        sensor_tf.header = header
        sensor_tf.child_frame_id = args.sensor_frame
        sensor_tf.transform.translation.x = position[0] + sensor_position[0]
        sensor_tf.transform.translation.y = position[1] + sensor_position[1]
        sensor_tf.transform.translation.z = position[2] + sensor_position[2]
        sensor_tf.transform.rotation.x = orientation[0]
        sensor_tf.transform.rotation.y = orientation[1]
        sensor_tf.transform.rotation.z = orientation[2]
        sensor_tf.transform.rotation.w = orientation[3]
        tf_broadcaster.sendTransform([body_tf, sensor_tf])
        counts["tf_published"] += 2

    def handle_message(raw: str) -> None:
        for chunk in iter_message_chunks(raw):
            counts["chunks_parsed"] += 1
            sample = parse_sample(chunk, model_name=args.model_name)
            if sample is None:
                continue
            counts["samples_matched"] += 1
            publish(sample)
            rclpy.spin_once(node, timeout_sec=0.0)
            break

    try:
        while rclpy.ok() and not stop_requested["value"]:
            counts["stream_starts"] += 1
            stream_process = subprocess.Popen(
                [args.gz_command, "topic", "-e", "-t", args.gz_topic],
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=1,
            )
            buffer: list[str] = []
            try:
                assert stream_process.stdout is not None
                for line in stream_process.stdout:
                    if stop_requested["value"]:
                        break
                    counts["stream_lines_read"] += 1
                    if line.startswith("header {") and buffer:
                        message = "".join(buffer).strip()
                        buffer = [line]
                        if message:
                            counts["stream_messages_completed"] += 1
                            handle_message(message)
                    elif line.strip() == "---":
                        message = "".join(buffer).strip()
                        buffer = []
                        if message:
                            counts["stream_messages_completed"] += 1
                            handle_message(message)
                    else:
                        buffer.append(line)
                    if args.max_samples > 0 and counts["samples_matched"] >= args.max_samples:
                        stop_requested["value"] = True
                        break
                    now = time.monotonic()
                    if now - last_report >= float(args.stream_idle_report_s):
                        write_json(
                            output_json,
                            {
                                "schema": "mosim.gazebo_truth_to_planner_odom_tf.v1",
                                "status": "active" if counts["odom_published"] else "waiting_for_stream_sample",
                                "counts": counts,
                            },
                        )
                        last_report = now
                trailing = "".join(buffer).strip()
                if trailing and not stop_requested["value"]:
                    counts["stream_messages_completed"] += 1
                    handle_message(trailing)
            finally:
                if stream_process.poll() is None:
                    stream_process.terminate()
                    try:
                        stream_process.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        stream_process.kill()
                if not stop_requested["value"]:
                    counts["stream_restarts"] += 1
                    counts["poll_failures"] += 1
                    time.sleep(max(0.0, float(args.poll_sleep_s)))
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    status = "published" if counts["odom_published"] > 0 else "blocked_no_samples"
    report = {
        "schema": "mosim.gazebo_truth_to_planner_odom_tf.v1",
        "status": status,
        "gz_topic": args.gz_topic,
        "model_name": args.model_name,
        "outputs": {
            "planner_odom": args.planner_odom_topic,
            "mosim_planner_odom": args.mosim_planner_odom_topic,
            "tf_edges": [
                f"{args.map_frame}->{args.body_frame}",
                f"{args.map_frame}->{args.sensor_frame}",
            ],
        },
        "counts": counts,
        "claim_boundary": [
            "Publishes dynamic planner odometry and TF from Gazebo truth for closed-loop EGO gate input.",
            "Does not by itself prove planning, control, obstacle avoidance, or final mission success.",
        ],
    }
    write_json(output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "published" else 3


if __name__ == "__main__":
    raise SystemExit(main())
