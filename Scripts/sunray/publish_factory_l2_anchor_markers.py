#!/usr/bin/env python3
"""Publish Factory L2 coordinate-review anchors as RViz MarkerArray.

This node is visual-review support only. It never publishes setpoints,
controller outputs, estimator state, actuator commands, or planner inputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


COLORS = {
    "origin": (1.0, 1.0, 1.0, 1.0),
    "scene_profile_spawn": (0.1, 0.45, 1.0, 1.0),
    "truth_aabb": (1.0, 0.85, 0.05, 1.0),
    "ue_landmark_gate": (1.0, 0.2, 0.1, 1.0),
    "ue_landmark_obstacle": (0.2, 1.0, 0.2, 1.0),
    "ue_landmark_terrain": (0.1, 0.8, 1.0, 1.0),
    "ue_landmark_building": (1.0, 0.45, 1.0, 1.0),
    "ue_landmark_sensor": (1.0, 0.55, 0.05, 1.0),
    "ue_landmark_wall": (0.8, 0.8, 0.8, 1.0),
}


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
        return str(path)


def color_for(anchor_type: str) -> tuple[float, float, float, float]:
    return COLORS.get(anchor_type, (1.0, 1.0, 1.0, 1.0))


def load_anchors(path: Path) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                x = float(row["mworks_x_m"])
                y = float(row["mworks_y_m"])
                z = float(row["mworks_z_m"])
            except (KeyError, TypeError, ValueError):
                continue
            if not all(math.isfinite(value) for value in (x, y, z)):
                continue
            anchors.append({**row, "xyz_m": [x, y, z]})
    return anchors


def write_summary(path: Path, *, status: str, args: argparse.Namespace, anchors: list[dict[str, Any]], publish_count: int = 0) -> None:
    payload = {
        "schema": "mosim.factory_l2_anchor_marker_publisher.v1",
        "status": status,
        "anchor_csv": rel(project_path(args.anchor_csv)),
        "marker_topic": args.marker_topic,
        "frame_id": args.frame_id,
        "anchor_count": len(anchors),
        "publish_count": publish_count,
        "claim_boundary": [
            "RViz visual-review anchors only.",
            "This node does not publish setpoints, controller outputs, estimator state, actuator commands, or planner inputs.",
        ],
    }
    if path:
        project_path(path).parent.mkdir(parents=True, exist_ok=True)
        project_path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anchor-csv", type=Path, required=True)
    parser.add_argument("--marker-topic", default="/mosim/factory_l2/anchor_markers")
    parser.add_argument("--frame-id", default="camera_init")
    parser.add_argument("--publish-hz", type=float, default=2.0)
    parser.add_argument("--sphere-radius-m", type=float, default=1.2)
    parser.add_argument("--text-height-m", type=float, default=2.4)
    parser.add_argument("--text-z-offset-m", type=float, default=3.0)
    parser.add_argument("--line-width-m", type=float, default=0.12)
    parser.add_argument("--summary-json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    anchor_csv = project_path(args.anchor_csv)
    anchors = load_anchors(anchor_csv)
    if args.dry_run:
        if args.summary_json:
            write_summary(project_path(args.summary_json), status="dry_run_passed", args=args, anchors=anchors)
        print(json.dumps({"status": "dry_run_passed", "anchor_count": len(anchors), "anchor_csv": rel(anchor_csv)}, ensure_ascii=False, indent=2))
        return 0 if anchors else 2

    import rospy
    from geometry_msgs.msg import Point
    from visualization_msgs.msg import Marker, MarkerArray

    rospy.init_node("mosim_factory_l2_anchor_markers", anonymous=False)
    publisher = rospy.Publisher(args.marker_topic, MarkerArray, queue_size=1, latch=True)
    rate = rospy.Rate(max(0.1, float(args.publish_hz)))
    publish_count = 0
    while not rospy.is_shutdown():
        stamp = rospy.Time.now()
        marker_array = MarkerArray()
        marker_id = 0
        for anchor in anchors:
            x, y, z = anchor["xyz_m"]
            r, g, b, a = color_for(str(anchor.get("type", "")))

            sphere = Marker()
            sphere.header.frame_id = args.frame_id
            sphere.header.stamp = stamp
            sphere.ns = "factory_l2_anchor_spheres"
            sphere.id = marker_id
            marker_id += 1
            sphere.type = Marker.SPHERE
            sphere.action = Marker.ADD
            sphere.pose.position.x = x
            sphere.pose.position.y = y
            sphere.pose.position.z = z
            sphere.pose.orientation.w = 1.0
            sphere.scale.x = sphere.scale.y = sphere.scale.z = args.sphere_radius_m * 2.0
            sphere.color.r, sphere.color.g, sphere.color.b, sphere.color.a = r, g, b, a
            marker_array.markers.append(sphere)

            line = Marker()
            line.header.frame_id = args.frame_id
            line.header.stamp = stamp
            line.ns = "factory_l2_anchor_label_stems"
            line.id = marker_id
            marker_id += 1
            line.type = Marker.LINE_LIST
            line.action = Marker.ADD
            line.points = [Point(x=x, y=y, z=z), Point(x=x, y=y, z=z + args.text_z_offset_m)]
            line.scale.x = args.line_width_m
            line.color.r, line.color.g, line.color.b, line.color.a = r, g, b, a
            marker_array.markers.append(line)

            text = Marker()
            text.header.frame_id = args.frame_id
            text.header.stamp = stamp
            text.ns = "factory_l2_anchor_labels"
            text.id = marker_id
            marker_id += 1
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD
            text.pose.position.x = x
            text.pose.position.y = y
            text.pose.position.z = z + args.text_z_offset_m
            text.pose.orientation.w = 1.0
            text.scale.z = args.text_height_m
            text.color.r, text.color.g, text.color.b, text.color.a = r, g, b, a
            text.text = f"{anchor.get('id', '')}\\n{anchor.get('label', '')}"
            marker_array.markers.append(text)

        publisher.publish(marker_array)
        publish_count += 1
        if args.summary_json and publish_count == 1:
            write_summary(project_path(args.summary_json), status="running", args=args, anchors=anchors, publish_count=publish_count)
        rate.sleep()

    if args.summary_json:
        write_summary(project_path(args.summary_json), status="completed", args=args, anchors=anchors, publish_count=publish_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
