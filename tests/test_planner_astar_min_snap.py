#!/usr/bin/env python3
"""Regression checks for A* + trackability reference generation."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


def load_planner_module():
    path = ROOT / "scripts" / "plan_astar_min_snap.py"
    spec = importlib.util.spec_from_file_location("plan_astar_min_snap", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load plan_astar_min_snap.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_wall_bbox_module():
    path = ROOT / "scripts" / "check_wall_group_bboxes.py"
    spec = importlib.util.spec_from_file_location("check_wall_group_bboxes", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_wall_group_bboxes.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    for item in sorted(path.glob("**/*"), key=lambda value: len(value.parts), reverse=True):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            item.rmdir()
    path.rmdir()


def test_open_blocks_planner_outputs_trackable_reference() -> None:
    module = load_planner_module()
    config_path = ROOT / "planners" / "astar_min_snap" / "map_open_blocks.yaml"
    config = module.read_yaml(config_path)
    raw_path, simplified, rows, report = module.plan_trackable(config)

    if len(raw_path) <= len(simplified):
        raise AssertionError("Line-of-sight simplification should reduce the raw grid path")
    if len(simplified) < 3:
        raise AssertionError(f"Simplified path should route around obstacles, got {len(simplified)} points")
    if report["planning_success"] is not True or report["accepted"] is not True:
        raise AssertionError(report)
    if report["min_obstacle_distance_m"] < report["safety_margin_m"]:
        raise AssertionError(report)
    if report["dynamic_violation_count"] != 0:
        raise AssertionError(report)
    if report["trackability_score"] < 0.8:
        raise AssertionError(report)
    if report.get("local_planning_enabled") is not True:
        raise AssertionError("planning_open_blocks must use local-window receding planning")
    if report.get("known_obstacle_count_final", 0) >= report.get("truth_obstacle_count", 0):
        raise AssertionError("Planner appears to know every truth obstacle; local sensing constraint regressed")
    if report.get("local_window_radius_m") != 3.0:
        raise AssertionError(report)
    if report.get("model_segment_limit") != 90:
        raise AssertionError(report)
    truth_obstacles = report.get("truth_obstacles", [])
    fixed_wall_count = sum(1 for obstacle in truth_obstacles if obstacle.get("type") == "box" and "wall_group_id" in obstacle)
    random_cylinder_count = sum(1 for obstacle in truth_obstacles if obstacle.get("type") == "cylinder")
    random_column_count = sum(1 for obstacle in truth_obstacles if obstacle.get("random_cluster"))
    random_cluster_count = len({
        int(obstacle["random_cluster_id"])
        for obstacle in truth_obstacles
        if obstacle.get("random_cluster") and "random_cluster_id" in obstacle
    })
    wall_groups = config["map"].get("wall_groups", {}).get("groups", [])
    if len(wall_groups) != 8:
        raise AssertionError("planning_open_blocks must use eight reusable L/T wall-group templates")
    shape_counts = {shape: sum(1 for group in wall_groups if group.get("shape") == shape) for shape in ["L", "T"]}
    if shape_counts != {"L": 4, "T": 4}:
        raise AssertionError(f"Expected four L wall groups and four T wall groups, got {shape_counts}")
    expected_random_count = int(config["map"].get("random_obstacles", {}).get("count", 0))
    if fixed_wall_count != 16 or random_cluster_count != expected_random_count or random_cylinder_count != 0:
        raise AssertionError(
            f"Expected eight L/T walls expanded as 16 boxes plus {expected_random_count} random column clusters, got wall_boxes={fixed_wall_count}, clusters={random_cluster_count}, columns={random_column_count}, cylinders={random_cylinder_count}"
        )
    if random_column_count < expected_random_count * 4 or random_column_count > expected_random_count * 10:
        raise AssertionError(f"Random cluster column count outside 4-10 per cluster: {random_column_count}")
    required = {
        "time",
        "x_ref",
        "y_ref",
        "z_ref",
        "vx_ref",
        "vy_ref",
        "vz_ref",
        "ax_ref",
        "ay_ref",
        "az_ref",
        "jx_ref",
        "jy_ref",
        "jz_ref",
        "yaw_ref",
    }
    if set(rows[0]) != required:
        raise AssertionError(rows[0].keys())


def test_open_blocks_wall_groups_do_not_overlap_or_leave_map() -> None:
    module = load_planner_module()
    bbox = load_wall_bbox_module()
    config_path = ROOT / "planners" / "astar_min_snap" / "map_open_blocks.yaml"
    config = module.read_yaml(config_path)
    config = module.expand_wall_groups(config)
    map_config = config["map"]
    world = [
        float(map_config["bounds"]["x"][0]),
        float(map_config["bounds"]["y"][0]),
        float(map_config["bounds"]["z"][0]),
        float(map_config["bounds"]["x"][1]),
        float(map_config["bounds"]["y"][1]),
        float(map_config["bounds"]["z"][1]),
    ]
    fixed = [
        obstacle for obstacle in map_config["obstacles"]
        if obstacle.get("type") == "box" and "wall_group_id" in obstacle
    ]
    groups = [
        bbox.merge_boxes([bbox.box_from_obstacle(item) for item in fixed[index:index + 2]])
        for index in range(0, len(fixed), 2)
    ]

    if len(groups) != 8:
        raise AssertionError(groups)
    start = [float(value) for value in map_config["start"]]
    goal = [float(value) for value in map_config["goal"]]
    for group in groups:
        if group[0] < world[0] or group[1] < world[1] or group[2] < world[2] or group[3] > world[3] or group[4] > world[4] or group[5] > world[5]:
            raise AssertionError(f"wall group leaves map bounds: {group}")
        if bbox.point_distance_to_box(start, group) < 5.0:
            raise AssertionError(f"wall group too close to start: {group}")
        if bbox.point_distance_to_box(goal, group) < 5.0:
            raise AssertionError(f"wall group too close to goal: {group}")

    for index in range(0, len(fixed), 2):
        parts = [bbox.box_from_obstacle(item) for item in fixed[index:index + 2]]
        lines = [bbox.wall_centerline(part) for part in parts]
        long_index = 0 if lines[0]["length"] >= lines[1]["length"] else 1
        short_index = 1 - long_index
        shape = bbox.wall_shape_from_parts(parts[long_index], parts[short_index])
        expected_shape = config["map"]["wall_groups"]["groups"][index // 2]["shape"]
        if shape["shape"] != expected_shape:
            raise AssertionError(f"wall group shape mismatch: expected={expected_shape}, actual={shape}")
        if shape["distance"] > 1e-3:
            raise AssertionError(f"wall centerline connection is open: group={index // 2 + 1} {shape}")

    for i, group_a in enumerate(groups):
        for group_b in groups[i + 1:]:
            distance = bbox.bounds_distance(group_a, group_b)
            if distance < 4.0:
                raise AssertionError(f"wall groups too close or overlap: {group_a} {group_b} distance={distance}")


def test_corridor_planner_writes_expected_artifacts() -> None:
    module = load_planner_module()
    temp_dir = ROOT / ".tmp" / f"planner_{uuid4().hex}"
    try:
        config_path = ROOT / "planners" / "astar_min_snap" / "map_corridor_gate.yaml"
        config = module.read_yaml(config_path)
        paths = module.write_outputs(config_path, config, temp_dir)
        for key in ["raw_path", "path", "reference", "summary", "trackability", "preview", "manifest"]:
            if not paths[key].exists():
                raise AssertionError(f"Missing planner artifact {key}: {paths[key]}")
        summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
        if summary["map_id"] != "map_corridor_gate" or summary["accepted"] is not True:
            raise AssertionError(summary)
        with paths["reference"].open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) < 20:
            raise AssertionError("Reference output is unexpectedly short")
        if abs(float(rows[0]["z_ref"]) - 1.0) > 1e-9 or abs(float(rows[-1]["z_ref"]) - 1.0) > 1e-9:
            raise AssertionError("P1 planner should keep fixed altitude for this scenario")
        preview = paths["preview"].read_text(encoding="utf-8")
        if "<svg" not in preview or "safety margin" not in preview:
            raise AssertionError("Preview SVG missing expected content")
    finally:
        remove_tree(temp_dir)
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
