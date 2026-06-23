#!/usr/bin/env python3
"""Record ROS1 topic continuity for Sunray MID360/FAST-LIO review.

This diagnostic separates raw sensor drops from FAST-LIO output drops and
RViz/TF display artifacts. It intentionally records both wall-time gaps and
header-time gaps because the current Sunray/Gazebo chain mixes wall-time and
simulation-time stamped topics.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import rospy
from nav_msgs.msg import Odometry, Path as RosPath
from sensor_msgs.msg import PointCloud2

try:
    from livox_ros_driver.msg import CustomMsg
except Exception:  # pragma: no cover - depends on sourced catkin workspace.
    CustomMsg = None


def stamp_to_sec(stamp: Any) -> float | None:
    try:
        return float(stamp.secs) + float(stamp.nsecs) * 1e-9
    except Exception:
        return None


def gap_stats(values: list[float]) -> dict[str, Any]:
    if len(values) < 2:
        return {"count": len(values)}
    gaps = [b - a for a, b in zip(values, values[1:])]
    sorted_gaps = sorted(gaps)
    elapsed = values[-1] - values[0]
    return {
        "count": len(values),
        "avg_hz": (len(values) - 1) / elapsed if elapsed > 0 else None,
        "max_gap_s": max(gaps),
        "p95_gap_s": sorted_gaps[int(0.95 * (len(sorted_gaps) - 1))],
        "gaps_gt_0p5s": sum(1 for gap in gaps if gap > 0.5),
        "gaps_gt_1s": sum(1 for gap in gaps if gap > 1.0),
        "first": values[0],
        "last": values[-1],
    }


class ContinuityRecorder:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.records: dict[str, dict[str, list[Any]]] = {}
        self.subscribers = []
        self.topic_types: list[tuple[str, Any]] = [
            ("/uav1/livox/lidar", PointCloud2),
            ("/cloud_registered", PointCloud2),
            ("/Odometry", Odometry),
            ("/path", RosPath),
            ("/mosim/sunray/lidar_points_map_accumulated", PointCloud2),
        ]
        if CustomMsg is not None:
            self.topic_types.insert(1, ("/mosim/fastlio/livox/lidar", CustomMsg))

    def callback_for(self, topic: str):
        def callback(msg: Any) -> None:
            wall = time.time()
            header = getattr(msg, "header", None)
            rec = self.records.setdefault(
                topic,
                {"wall": [], "header": [], "frame_id": [], "width": [], "height": [], "point_num": []},
            )
            rec["wall"].append(wall)
            rec["header"].append(stamp_to_sec(header.stamp) if header is not None else None)
            rec["frame_id"].append(getattr(header, "frame_id", "") if header is not None else "")
            if hasattr(msg, "width"):
                rec["width"].append(int(msg.width))
                rec["height"].append(int(msg.height))
            if hasattr(msg, "point_num"):
                rec["point_num"].append(int(msg.point_num))

        return callback

    def run(self) -> dict[str, Any]:
        rospy.init_node("mosim_sunray_topic_continuity_recorder", anonymous=True, disable_signals=True)
        for topic, msg_type in self.topic_types:
            self.subscribers.append(rospy.Subscriber(topic, msg_type, self.callback_for(topic), queue_size=200))

        start = time.time()
        while not rospy.is_shutdown() and time.time() - start < self.args.duration_s:
            time.sleep(0.05)

        summary: dict[str, Any] = {
            "schema": "mosim.sunray_ros1_topic_continuity.v1",
            "duration_requested_s": self.args.duration_s,
            "duration_wall_s": time.time() - start,
            "topics": {},
        }
        for topic, _ in self.topic_types:
            rec = self.records.get(
                topic,
                {"wall": [], "header": [], "frame_id": [], "width": [], "height": [], "point_num": []},
            )
            headers = [value for value in rec["header"] if value is not None]
            topic_summary: dict[str, Any] = {
                "wall_stats": gap_stats(rec["wall"]),
                "header_stats": gap_stats(headers),
                "unique_frames": sorted(set(rec["frame_id"]))[:10],
            }
            if rec["width"]:
                topic_summary["width_minmax_last"] = [min(rec["width"]), max(rec["width"]), rec["width"][-1]]
                topic_summary["height_minmax_last"] = [min(rec["height"]), max(rec["height"]), rec["height"][-1]]
            if rec["point_num"]:
                topic_summary["point_num_minmax_last"] = [
                    min(rec["point_num"]),
                    max(rec["point_num"]),
                    rec["point_num"][-1],
                ]
            summary["topics"][topic] = topic_summary
        return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=120.0)
    parser.add_argument("--out", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = ContinuityRecorder(args).run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
