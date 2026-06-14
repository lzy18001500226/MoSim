#!/usr/bin/env python3
"""Static tests for the 080 camera_init map/world grounding source repair."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "Scripts" / "ros" / "check_camera_init_map_world_grounding_source_repair.py"
EVIDENCE = (
    ROOT
    / "Results"
    / "ros2_runtime"
    / "camera_init_map_world_grounding_source_repair_20260609_080"
)


def load_checker():
    spec = importlib.util.spec_from_file_location("check_camera_init_map_world_grounding_source_repair", CHECKER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_outputs() -> None:
    checker = load_checker()
    summary = checker.run(EVIDENCE)
    assert summary["ok"] is True


def test_080_checker_generates_static_repair_outputs() -> None:
    ensure_outputs()
    expected = [
        "camera_init_map_world_grounding_source_repair_matrix_080.json",
        "camera_init_map_world_grounding_future_single_probe_gate_080.json",
        "camera_init_map_world_grounding_source_manifest_080.json",
        "camera_init_map_world_grounding_source_repair_summary_080.json",
        "camera_init_map_world_grounding_source_repair_report_080.md",
    ]
    for name in expected:
        assert (EVIDENCE / name).is_file()


def test_080_route_matrix_classifies_real_repair_surface_and_rejects_fake_routes() -> None:
    ensure_outputs()
    matrix = {route["route_id"]: route for route in load_json(EVIDENCE / "camera_init_map_world_grounding_source_repair_matrix_080.json")}

    adopt = matrix["future_single_probe_raw_tf_chain_with_source_config_anchor"]
    assert adopt["classification"] == "adopt"
    adopt_text = "\n".join(adopt["route_design"])
    assert "Capture raw /tf and /tf_static events" in adopt_text
    assert "camera_init-to-map/world/ue_world chain" in adopt_text

    assert matrix["079_upstream_fast_lio_mapping_launch"]["classification"] == "reference_only"
    assert matrix["079_upstream_fast_lio_mapping_launch"]["facts"]["079_grounding_status"] == "blocked_absent"

    spark = matrix["project_spark_fast_lio_map_frame_binding"]
    assert spark["classification"] == "adapt"
    assert all(spark["source_static_facts"].values())
    requirement_text = "\n".join(spark["future_single_probe_requirement"])
    assert "selected map_frame/base_frame/lidar_frame/imu_frame" in requirement_text
    assert "raw /tf and /tf_static" in requirement_text
    assert "blocked_absent" in requirement_text

    scene = matrix["scene_replay_external_fastlio_launch_cmd_binding"]
    assert scene["classification"] == "adapt"
    assert scene["source_static_facts"]["has_fastlio_launch_cmd_argument"] is True

    controller = matrix["controller_map_world_policy"]
    assert controller["classification"] == "reference_only"
    assert controller["source_static_facts"]["converter_accepts_world_alias"] is True

    reject = matrix["arbitrary_static_tf_header_rename_or_truth_shortcut"]
    assert reject["classification"] == "reject"
    rejected = "\n".join(reject["rejected_shortcuts"])
    assert "header.frame_id rename" in rejected
    assert "UE truth shortcut" in rejected
    assert "arbitrary camera_init->map/world/ue_world static TF" in rejected


def test_080_future_gate_keeps_live_probe_and_handoff_blocked() -> None:
    ensure_outputs()
    gate = load_json(EVIDENCE / "camera_init_map_world_grounding_future_single_probe_gate_080.json")
    summary = load_json(EVIDENCE / "camera_init_map_world_grounding_source_repair_summary_080.json")

    pre_probe = "\n".join(gate["pre_probe_source_static_requirements"])
    assert "selected_route_id is project_spark_fast_lio_map_frame_binding" in pre_probe
    assert "bare upstream fast_lio mapping.launch.py" in pre_probe
    assert "no arbitrary camera_init->map/world static TF" in pre_probe

    acceptance = "\n".join(gate["acceptance_requires_all"])
    assert "raw /tf event path" in acceptance
    assert "chain connects camera_init to map, world, or ue_world" in acceptance
    assert "non_fake_basis is true" in acceptance
    assert "forbidden planner/controller/setpoint topics are absent" in acceptance

    blocked = "\n".join(gate["remain_blocked_when"])
    assert "dynamic_edges remain camera_init->body only" in blocked
    assert "map_frame exists only as a parameter" in blocked
    assert "fake, arbitrary, header-only" in blocked

    assert summary["ok"] is True
    assert summary["can_claim_current_grounding"] is False
    assert summary["can_authorize_live_probe_from_080"] is False
    assert summary["can_authorize_controller_handoff_from_080"] is False
    assert all(value is False for value in summary["live_actions"].values())


def test_080_report_does_not_upgrade_runtime_claims() -> None:
    ensure_outputs()
    report = (EVIDENCE / "camera_init_map_world_grounding_source_repair_report_080.md").read_text(encoding="utf-8")
    assert "080 is a source/static repair checker" in report
    assert "grounding_status: `blocked_absent`" in report
    assert "`project_spark_fast_lio_map_frame_binding`: `adapt`" in report
    assert "`arbitrary_static_tf_header_rename_or_truth_shortcut`: `reject`" in report
    assert "It does not authorize a live probe" in report

    forbidden_claims = [
        "planner_ready: true",
        "closed_loop: true",
        "controller handoff is authorized",
        "current grounding is proven",
        "runtime success is proven",
    ]
    for phrase in forbidden_claims:
        assert phrase not in report


def main() -> int:
    test_080_checker_generates_static_repair_outputs()
    test_080_route_matrix_classifies_real_repair_surface_and_rejects_fake_routes()
    test_080_future_gate_keeps_live_probe_and_handoff_blocked()
    test_080_report_does_not_upgrade_runtime_claims()
    print("[OK] 080 camera_init map/world grounding source repair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
