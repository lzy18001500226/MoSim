#!/usr/bin/env python3
"""Static contract checks for the canonical OpenBlocks single-UAV map audit."""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning"
DISPLAY = PLANNING / "PlanningNavigationDisplay.mo"
MAP_TRUTH = PLANNING / "OpenBlocksMapTruthDisplay.mo"
AUDIT = PLANNING / "Sunray150PlanningOpenBlocksSingleUavMapAudit.mo"
PX4_RUNNER = PLANNING / "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop.mo"
THREE_UAV = PLANNING / "ThreeUavOpenBlocksReconfigurableFormationLinearMPC.mo"
PACKAGE = PLANNING / "package.mo"
PACKAGE_ORDER = PLANNING / "package.order"
MAP_CONFIG = ROOT / "Config" / "planners" / "astar_min_snap" / "map_open_blocks.yaml"
STATIC_MANIFEST = (
    ROOT
    / "Results"
    / "planning"
    / "single_obstacle_astar_awff"
    / "figures"
    / "static_map"
    / "map_open_blocks_static_ground_0p2_obstacle_columns_0p2_h2p8_3p5_manifest.json"
)
HELPER_PATH = ROOT / "Scripts" / "planning" / "update_planning_open_blocks_model.py"
PLANNER_PATH = ROOT / "Scripts" / "planning" / "plan_astar_min_snap.py"
THREE_UAV_BUILDER = ROOT / "Scripts" / "planning" / "build_three_uav_open_blocks_model.py"
THREE_UAV_METRICS = ROOT / "Results" / "planning" / "three_uav_open_blocks_mworks_20260720" / "metrics" / "three_uav_planning_metrics.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical_walls() -> dict[str, list[list[float]] | int]:
    planner = load_module("open_blocks_planner_for_map_audit", PLANNER_PATH)
    helper = load_module("open_blocks_helper_for_map_audit", HELPER_PATH)
    config = yaml.safe_load(MAP_CONFIG.read_text(encoding="utf-8"))
    expanded = planner.expand_wall_groups(config)
    walls = helper.build_wall_groups({"truth_obstacles": expanded["map"]["obstacles"]})
    assert walls["wall_group_count"] == 8
    return walls


def extract_matrix(source: str, name: str) -> list[list[float]]:
    marker = f"final {name} = {{"
    start = source.index(marker) + len(f"final {name} = ")
    depth = 0
    end = start
    for end in range(start, len(source)):
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
            if depth == 0:
                break
    rows = re.findall(r"\{([^{}]+)\}", source[start : end + 1])
    return [[float(value.strip()) for value in row.split(",")] for row in rows]


def test_global_wall_truth_is_separate_from_local_sensing_overlay() -> None:
    source = DISPLAY.read_text(encoding="utf-8")
    for token in (
        "parameter Boolean show_global_wall_truth = false",
        "global_wall_arm1[max_wall_groups]",
        "global_wall_arm2[max_wall_groups]",
        "local_wall_overlay_thickness_m",
        "wall_arm1_sensed[i] = highlight_local_costmap",
        "wall_arm2_sensed[i] = highlight_local_costmap",
    ):
        assert token in source


def test_map_truth_display_matches_current_yaml_and_static_mesh_manifest() -> None:
    source = MAP_TRUTH.read_text(encoding="utf-8")
    walls = canonical_walls()
    assert source.count("{") == source.count("}")
    assert source.count("(") == source.count(")")
    assert "extends PlanningNavigationDisplay(" in source
    assert "final show_static_map_layers = true" in source
    assert "final show_global_wall_truth = true" in source
    assert "final wall_group_count = 8" in source
    for source_name, wall_name in (
        ("wall_arm1_min", "arm1_min"),
        ("wall_arm1_max", "arm1_max"),
        ("wall_arm2_min", "arm2_min"),
        ("wall_arm2_max", "arm2_max"),
    ):
        actual = extract_matrix(source, source_name)
        expected = walls[wall_name]
        assert len(actual) == len(expected) == 8
        for actual_row, expected_row in zip(actual, expected):
            assert len(actual_row) == len(expected_row) == 3
            for actual_value, expected_value in zip(actual_row, expected_row):
                assert math.isclose(actual_value, expected_value, abs_tol=1e-12)

    manifest = json.loads(STATIC_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["random_obstacle_column_count"] == 7102
    assert manifest["dynamic_wall_group_count"] == 8
    assert manifest["dynamic_wall_box_count"] == 16
    assert manifest["walls_baked_into_static_mesh"] is False


def test_current_single_and_three_uav_models_reuse_one_map_truth_surface() -> None:
    px4_source = PX4_RUNNER.read_text(encoding="utf-8")
    three_source = THREE_UAV.read_text(encoding="utf-8")
    assert "OpenBlocksMapTruthDisplay navigationDisplay(" in px4_source
    assert "OpenBlocksMapTruthDisplay navigationDisplay(" in three_source
    for source in (px4_source, three_source):
        assert "wall_arm1_min =" not in source
        assert "wall_arm2_max =" not in source

    builder = load_module("open_blocks_three_uav_builder_for_map_audit", THREE_UAV_BUILDER)
    config = builder.read_yaml(MAP_CONFIG)
    metrics = json.loads(THREE_UAV_METRICS.read_text(encoding="utf-8"))
    generated = builder.build_model(config, metrics)
    assert "OpenBlocksMapTruthDisplay navigationDisplay(" in generated
    assert "wall_arm1_min =" not in generated
    assert "wall_arm2_max =" not in generated


def test_single_uav_audit_entry_is_map_only_and_publicly_reachable() -> None:
    source = AUDIT.read_text(encoding="utf-8")
    assert "extends Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop;" in source
    assert "StopTime = 0.2" in source
    assert "avoidance acceptance" in source

    package_source = PACKAGE.read_text(encoding="utf-8")
    package_order = PACKAGE_ORDER.read_text(encoding="utf-8").splitlines()
    assert "model OpenBlocksSingleUavMapAudit" in package_source
    assert "Sunray150PlanningOpenBlocksSingleUavMapAudit" in package_source
    for name in (
        "OpenBlocksMapTruthDisplay",
        "Sunray150PlanningOpenBlocksSingleUavMapAudit",
    ):
        assert name in package_order


def main() -> int:
    test_global_wall_truth_is_separate_from_local_sensing_overlay()
    test_map_truth_display_matches_current_yaml_and_static_mesh_manifest()
    test_current_single_and_three_uav_models_reuse_one_map_truth_surface()
    test_single_uav_audit_entry_is_map_only_and_publicly_reachable()
    print("[OK] OpenBlocks canonical global-map audit surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
