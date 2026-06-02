#!/usr/bin/env python3
"""Probe ROS2 Livox CustomMsg and IMU input before FAST-LIO consumes them."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROS_LOG_DIR = ROOT / "Results" / "tmp" / "ros_logs"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def ensure_ros_log_dir() -> None:
    log_dir = Path(os.environ.get("ROS_LOG_DIR", str(DEFAULT_ROS_LOG_DIR)))
    resolved = project_path(log_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    os.environ["ROS_LOG_DIR"] = str(resolved)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def stamp_to_sec(stamp: Any) -> float:
    return float(getattr(stamp, "sec", 0)) + float(getattr(stamp, "nanosec", 0)) * 1e-9


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "mean": 0.0, "max": 0.0}
    return {
        "min": round(min(values), 9),
        "mean": round(sum(values) / len(values), 9),
        "max": round(max(values), 9),
    }


def rate_from_times(times: list[float]) -> float:
    deltas = [right - left for left, right in zip(times, times[1:]) if right > left]
    if not deltas:
        return 0.0
    return round(1.0 / (sum(deltas) / len(deltas)), 6)


def dry_run(args: argparse.Namespace) -> int:
    payload = {
        "schema": "mosim.livox_custommsg_probe_dryrun.v1",
        "duration_seconds": args.duration_seconds,
        "topics": {"livox": args.livox_topic, "imu": args.imu_topic},
        "output_json": rel(project_path(args.output_json)),
        "claim": "dry-run only; no ROS2 topics were subscribed",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def probe(args: argparse.Namespace) -> int:
    ensure_ros_log_dir()
    try:
        import rclpy  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from sensor_msgs.msg import Imu  # type: ignore
        from livox_ros_driver2.msg import CustomMsg  # type: ignore
    except ImportError as exc:
        print("ROS2 Python modules are unavailable. Source ROS2 and project workspaces first.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    output_json = project_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    counters = {"livox": 0, "imu": 0}
    livox_times: list[float] = []
    imu_times: list[float] = []
    point_counts: list[int] = []
    offset_min_us: list[float] = []
    offset_max_us: list[float] = []
    line_sets: list[list[int]] = []
    tag_sets: list[list[int]] = []
    bad_livox_frames = 0

    reliability = ReliabilityPolicy.BEST_EFFORT if args.reliability == "best_effort" else ReliabilityPolicy.RELIABLE
    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=64,
        reliability=reliability,
        durability=DurabilityPolicy.VOLATILE,
    )
    rclpy.init()
    node = rclpy.create_node("mosim_livox_custommsg_probe")

    def on_livox(msg: CustomMsg) -> None:
        nonlocal bad_livox_frames
        counters["livox"] += 1
        stamp_s = stamp_to_sec(msg.header.stamp)
        livox_times.append(stamp_s)
        point_num = int(msg.point_num)
        point_counts.append(point_num)
        if point_num != len(msg.points):
            bad_livox_frames += 1
        if msg.points:
            sampled_points = msg.points[: min(len(msg.points), args.max_point_sample)]
            offsets = [float(point.offset_time) for point in sampled_points]
            offset_min_us.append(min(offsets))
            offset_max_us.append(float(msg.points[-1].offset_time))
            line_sets.append(sorted({int(point.line) for point in sampled_points}))
            tag_sets.append(sorted({int(point.tag) for point in sampled_points}))

    def on_imu(msg: Imu) -> None:
        counters["imu"] += 1
        imu_times.append(stamp_to_sec(msg.header.stamp))

    if args.probe_mode in ("both", "livox"):
        node.create_subscription(CustomMsg, args.livox_topic, on_livox, qos)
    if args.probe_mode in ("both", "imu"):
        node.create_subscription(Imu, args.imu_topic, on_imu, qos)

    deadline = time.monotonic() + args.duration_seconds
    try:
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()

    latest_livox = livox_times[-1] if livox_times else 0.0
    latest_imu = imu_times[-1] if imu_times else 0.0
    report = {
        "schema": "mosim.livox_custommsg_probe.v1",
        "probe_mode": args.probe_mode,
        "duration_seconds": args.duration_seconds,
        "topics": {"livox": args.livox_topic, "imu": args.imu_topic},
        "counts": counters,
        "rates_hz": {
            "livox": rate_from_times(livox_times),
            "imu": rate_from_times(imu_times),
        },
        "time_quality": {
            "livox_nonmonotonic_pairs": sum(1 for left, right in zip(livox_times, livox_times[1:]) if right < left),
            "imu_nonmonotonic_pairs": sum(1 for left, right in zip(imu_times, imu_times[1:]) if right < left),
            "latest_livox_minus_imu_s": round(latest_livox - latest_imu, 9) if latest_livox and latest_imu else None,
        },
        "livox": {
            "point_num": summarize([float(value) for value in point_counts]),
            "bad_point_num_frames": bad_livox_frames,
            "offset_min_us": summarize(offset_min_us),
            "offset_max_us": summarize(offset_max_us),
            "observed_lines": sorted({line for lines in line_sets for line in lines}),
            "observed_tags": sorted({tag for tags in tag_sets for tag in tags}),
        },
        "acceptance": {
            "livox_nonzero": (
                args.probe_mode == "imu" or counters["livox"] > 0 and min(point_counts or [0]) >= args.min_points
            ),
            "imu_nonzero": args.probe_mode == "livox" or counters["imu"] > 0,
            "livox_rate_ok": args.probe_mode == "imu" or rate_from_times(livox_times) >= args.min_livox_rate_hz,
            "imu_rate_ok": args.probe_mode == "livox" or rate_from_times(imu_times) >= args.min_imu_rate_hz,
            "time_delta_ok": (
                args.probe_mode != "both"
                or
                latest_livox != 0.0
                and latest_imu != 0.0
                and abs(latest_livox - latest_imu) <= args.max_latest_time_delta_s
            ),
        },
        "claim_boundary": [
            "This probes FAST-LIO input streams only; it is not FAST-LIO localization evidence.",
            "FAST-LIO evidence still requires runtime /cloud_registered, odometry, path, and truth evaluation.",
        ],
    }
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not all(report["acceptance"].values()):
        return 3
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--livox-topic", default="/mosim/livox/lidar")
    parser.add_argument("--imu-topic", default="/mosim/forward/imu")
    parser.add_argument("--duration-seconds", type=float, default=5.0)
    parser.add_argument("--output-json", type=Path, default=ROOT / "Results/tmp/livox_custommsg_probe.json")
    parser.add_argument("--min-points", type=int, default=15000)
    parser.add_argument("--min-livox-rate-hz", type=float, default=8.0)
    parser.add_argument("--min-imu-rate-hz", type=float, default=150.0)
    parser.add_argument("--max-latest-time-delta-s", type=float, default=0.2)
    parser.add_argument("--max-point-sample", type=int, default=5000)
    parser.add_argument("--probe-mode", choices=("both", "livox", "imu"), default="both")
    parser.add_argument("--reliability", choices=("reliable", "best_effort"), default="reliable")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.duration_seconds <= 0:
        raise ValueError("--duration-seconds must be positive")
    if args.dry_run:
        return dry_run(args)
    return probe(args)


if __name__ == "__main__":
    raise SystemExit(main())
