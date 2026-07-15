#!/usr/bin/env python3
"""Check current Sunray ROS1 RViz review display boundaries.

The check is intentionally narrow: it protects the current review configs from
drifting back to mixed point-cloud/grid views or tiny point sizes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RVIZ_DIR = ROOT / "Config" / "rviz"

POINT_SIZE_REQUIRED = "0.02"
GOAL4_DIFF_POINT_SIZE_REQUIRED = "0.08"
FACTORY_FUEL_POINT_SIZE_REQUIRED = "0.08"
FACTORY_FUEL_POINTCLOUD_CONFIGS = {
    "sunray_ros1_factory_fuel_pointcloud_review.rviz",
}
FACTORY_FUEL_POINTCLOUD_CONFIG = "sunray_ros1_factory_fuel_pointcloud_review.rviz"
FACTORY_FUEL_GRID_CONFIG = "sunray_ros1_factory_fuel_grid3d_review.rviz"
FUEL_DYNAMIC_TRAJECTORY_TOPIC = "/mosim/fuel/planning_vis/trajectory_world"
FUEL_DIAGNOSTIC_TOPICS = {
    "/mosim/fuel/planning_vis/frontier_world",
    "/mosim/fuel/planning_vis/viewpoints_world",
    "/mosim/fuel/coverage_overlay",
}
FACTORY_FUEL_PATH_WIDTHS = {
    "/mosim/goal4/truth_path": "0.12",
    "/mosim/goal4/position_cmd_path": "0.09",
}
POINT_TOPIC_RE = re.compile(
    r"^\s*Topic:\s+(/(?:uav1/livox/lidar|uav1/livox_world|Laser_map|cloud_registered|mosim/fastlio/laser_map_obstacles|mosim/goal4/livox_world_accumulated|mosim/sunray/lidar_points_map_accumulated|velodyne_points|mosim/local_known_map_cloud))\s*$"
)
OCCUPANCY_TOPIC_RE = re.compile(r"^\s*Topic:\s+/.*/grid_map/occupancy(?:_inflate)?\s*$")

GRID_CONFIGS = {
    "sunray_ros1_goal4_diff_grid3d_review.rviz": {
        "/uav1/livox_world",
        "/Laser_map",
        "/cloud_registered",
        "/mosim/fastlio/laser_map_obstacles",
    },
    "sunray_ros1_ego_grid_trajectory_review.rviz": {
        "/uav1/livox_world",
        "/Laser_map",
        "/cloud_registered",
        "/mosim/fastlio/laser_map_obstacles",
    }
}


def iter_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("    - ") and current:
            blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
        elif line.startswith("    - "):
            current = [line]
    if current:
        blocks.append(current)
    return blocks


def check_point_sizes(path: Path, text: str, errors: list[str]) -> None:
    expected_size = (
        GOAL4_DIFF_POINT_SIZE_REQUIRED
        if path.name == "sunray_ros1_goal4_diff_pointcloud_review.rviz"
        else FACTORY_FUEL_POINT_SIZE_REQUIRED
        if path.name in FACTORY_FUEL_POINTCLOUD_CONFIGS
        else POINT_SIZE_REQUIRED
    )
    for block in iter_blocks(text):
        joined = "\n".join(block)
        if "Class: rviz/PointCloud2" not in joined:
            continue
        if OCCUPANCY_TOPIC_RE.search(joined):
            continue
        topic_match = POINT_TOPIC_RE.search(joined)
        if not topic_match:
            continue
        size_match = re.search(r"^\s*Size \(m\):\s+([0-9.]+)\s*$", joined, re.MULTILINE)
        size = size_match.group(1) if size_match else "<missing>"
        if size != expected_size:
            errors.append(
                f"{path.relative_to(ROOT)} topic {topic_match.group(1)} has Size (m)={size}, expected {expected_size}"
            )


def check_grid_boundaries(path: Path, text: str, errors: list[str]) -> None:
    forbidden = GRID_CONFIGS.get(path.name)
    if not forbidden:
        return
    for topic in sorted(forbidden):
        if f"Topic: {topic}" in text:
            errors.append(
                f"{path.relative_to(ROOT)} must not include point-cloud topic {topic} in the grid review window"
            )
    if "Style: Boxes" not in text or "/grid_map/occupancy_inflate" not in text:
        errors.append(
            f"{path.relative_to(ROOT)} must render occupancy_inflate as voxel boxes"
        )
    if path.name == "sunray_ros1_goal4_diff_grid3d_review.rviz":
        if "Topic: /drone_0_ego_planner_node/grid_map/occupancy" not in text:
            errors.append(f"{path.relative_to(ROOT)} must include raw local occupancy as a diagnostic layer")
        if "Topic: /mosim/goal4/occupancy_accumulated" not in text:
            errors.append(f"{path.relative_to(ROOT)} must include accumulated raw occupancy for default grid review")
        raw_local_disabled = False
        accumulated_enabled = False
        for block in iter_blocks(text):
            joined = "\n".join(block)
            if (
                "Topic: /drone_0_ego_planner_node/grid_map/occupancy" in joined
                and "Enabled: false" in joined
                and "Style: Boxes" in joined
            ):
                raw_local_disabled = True
            if (
                "Topic: /mosim/goal4/occupancy_accumulated" in joined
                and "Enabled: true" in joined
                and "Value: true" in joined
                and "Style: Boxes" in joined
            ):
                accumulated_enabled = True
        if not raw_local_disabled:
            errors.append(
                f"{path.relative_to(ROOT)} must keep raw local occupancy as a disabled diagnostic layer"
            )
        if not accumulated_enabled:
            errors.append(
                f"{path.relative_to(ROOT)} must enable accumulated raw occupancy boxes by default"
            )


def check_diff_pointcloud_review(path: Path, text: str, errors: list[str]) -> None:
    if path.name != "sunray_ros1_goal4_diff_pointcloud_review.rviz":
        return
    required = "/mosim/goal4/livox_world_accumulated"
    if f"Topic: {required}" not in text:
        errors.append(f"{path.relative_to(ROOT)} must default to {required}")
    required_block_ok = False
    for block in iter_blocks(text):
        joined = "\n".join(block)
        if f"Topic: {required}" not in joined:
            continue
        required_block_ok = (
            "Enabled: true" in joined
            and "Style: Points" in joined
            and f"Size (m): {GOAL4_DIFF_POINT_SIZE_REQUIRED}" in joined
        )
    if not required_block_ok:
        errors.append(
            f"{path.relative_to(ROOT)} must enable {required} with Style: Points and Size (m): {GOAL4_DIFF_POINT_SIZE_REQUIRED}"
        )


def check_factory_fuel_review(path: Path, text: str, errors: list[str]) -> None:
    if path.name not in {FACTORY_FUEL_POINTCLOUD_CONFIG, FACTORY_FUEL_GRID_CONFIG}:
        return

    for topic, expected_width in FACTORY_FUEL_PATH_WIDTHS.items():
        matching_blocks = [
            "\n".join(block) for block in iter_blocks(text) if f"Topic: {topic}" in "\n".join(block)
        ]
        if not matching_blocks:
            errors.append(f"{path.relative_to(ROOT)} must include {topic}")
            continue
        block = matching_blocks[0]
        if "Enabled: true" not in block or "Line Style: Billboards" not in block:
            errors.append(
                f"{path.relative_to(ROOT)} must enable {topic} with billboard rendering"
            )
        if f"Line Width: {expected_width}" not in block:
            errors.append(
                f"{path.relative_to(ROOT)} topic {topic} must use Line Width: {expected_width}"
            )

    if path.name == FACTORY_FUEL_POINTCLOUD_CONFIG:
        if FUEL_DYNAMIC_TRAJECTORY_TOPIC in text:
            errors.append(
                f"{path.relative_to(ROOT)} must keep the local FUEL B-spline out of the point-cloud review"
            )
        return

    required_topics = {
        "/mosim/goal4/occupancy_accumulated",
        "/mosim/goal4/truth_path",
        "/mosim/goal4/position_cmd_path",
        FUEL_DYNAMIC_TRAJECTORY_TOPIC,
        "/mosim/goal4/body_axes",
    }
    for topic in sorted(required_topics):
        if topic not in text:
            errors.append(f"{path.relative_to(ROOT)} must include {topic}")
    for topic in sorted(FUEL_DIAGNOSTIC_TOPICS):
        if topic in text:
            errors.append(
                f"{path.relative_to(ROOT)} must keep diagnostic topic {topic} out of the default grid review"
            )
    if "/mosim/goal4/livox_world_accumulated" in text:
        errors.append(
            f"{path.relative_to(ROOT)} must keep the accumulated point cloud in the point-cloud window"
        )


def main() -> int:
    errors: list[str] = []
    for path in RVIZ_DIR.glob("*.rviz"):
        text = path.read_text(encoding="utf-8")
        check_point_sizes(path, text, errors)
        check_grid_boundaries(path, text, errors)
        check_diff_pointcloud_review(path, text, errors)
        check_factory_fuel_review(path, text, errors)
    if errors:
        print("Sunray RViz review config check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Sunray RViz review config check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
