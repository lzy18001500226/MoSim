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
    if report.get("local_window_radius_m") != 2.5:
        raise AssertionError(report)
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
