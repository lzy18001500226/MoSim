#!/usr/bin/env python3
"""Static checks for the 075 camera_init-to-map/world grounding contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_camera_init_map_world_grounding_static_gate_20260609_075"
)
CONTRACT = EVIDENCE / "camera_init_map_world_grounding_static_contract.json"
MATRIX = EVIDENCE / "camera_init_map_world_grounding_matrix.json"
REJECTION_RULES = EVIDENCE / "camera_init_map_world_fake_transform_rejection_rules.json"
FUTURE_CHECKLIST = EVIDENCE / "camera_init_map_world_future_same_run_evidence_checklist.json"
CHECK_SUMMARY = EVIDENCE / "camera_init_map_world_static_check_summary.json"
REPORT = EVIDENCE / "camera_init_map_world_grounding_report.md"


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def matrix_by_route() -> dict[str, dict]:
    return {row["route_id"]: row for row in load_json(MATRIX)}


def test_075_static_only_and_preserves_074_blocker_boundary() -> None:
    contract = load_json(CONTRACT)

    assert contract["mode"] == "source_static_contract_only"
    assert all(value is False for value in contract["live_actions"].values())
    assert contract["upstream_evidence"]["074"]["validator_ok"] is True
    assert (
        contract["upstream_evidence"]["074"]["tf"]["camera_init_map_world_grounding"]["status"]
        == "blocked_absent"
    )
    assert contract["upstream_evidence"]["074"]["controller_handoff"]["status"] == "blocked_no_map_world_grounding"
    assert contract["decision"]["camera_init_to_map_world_current_status"] == "blocked_absent"
    assert contract["decision"]["controller_handoff_status"] == "blocked_no_map_world_grounding"

    boundary = "\n".join(contract["claim_boundary"])
    assert "source/static camera_init-to-map/world grounding contract" in boundary
    assert "does not prove live ROS2/RViz/FAST-LIO success" in boundary
    assert "does not authorize controller handoff" in boundary
    assert "rejects arbitrary/fake camera_init-to-map/world transforms" in boundary


def test_075_grounding_matrix_classifies_current_future_and_rejected_routes() -> None:
    matrix = matrix_by_route()

    assert matrix["current_074_camera_init_output_only"]["classification"] == "reference_only"
    assert matrix["current_074_camera_init_output_only"]["frames"]["fastlio_output_frame"] == "camera_init"
    assert matrix["current_074_camera_init_output_only"]["frames"]["dynamic_edges"] == ["camera_init->body"]
    assert matrix["current_074_camera_init_output_only"]["frames"]["static_edges"] == []
    assert matrix["current_074_camera_init_output_only"]["frames"]["map_world_grounding"]["status"] == "blocked_absent"

    assert matrix["real_same_run_tf_grounding"]["classification"] == "adopt"
    required = "\n".join(matrix["real_same_run_tf_grounding"]["required_future_evidence"])
    assert "/tf or /tf_static" in required
    assert "evidence_path" in required
    assert "same probe" in required
    assert "fake/arbitrary/header-rename" in required

    assert matrix["real_same_run_external_grounding_measurement"]["classification"] == "adapt"
    assert matrix["controller_map_world_policy"]["classification"] == "reference_only"
    assert matrix["controller_map_world_policy"]["facts"]["canonical_controller_frame"] == "map"
    assert matrix["controller_map_world_policy"]["facts"]["position_command_alias"] == "world"
    assert "World alias is not camera_init-to-world grounding" in matrix["controller_map_world_policy"]["forbidden_claim"]

    assert matrix["arbitrary_static_transform_or_header_rename"]["classification"] == "reject"
    rejected = "\n".join(matrix["arbitrary_static_transform_or_header_rename"]["rejected_shortcuts"])
    assert "publish arbitrary camera_init->map/world static TF" in rejected
    assert "rename header.frame_id from camera_init to map/world" in rejected
    assert "fake point cloud, map, odom, or TF" in rejected


def test_075_rejects_fake_transform_routes_and_requires_same_run_evidence() -> None:
    rejection_rules = load_json(REJECTION_RULES)
    future = load_json(FUTURE_CHECKLIST)

    rule_ids = {rule["rule_id"] for rule in rejection_rules["rules"]}
    assert "reject_arbitrary_camera_init_map_world_static_tf" in rule_ids
    assert "reject_header_frame_rename" in rule_ids
    assert "reject_fake_map_world_odom_republisher" in rule_ids
    assert "reject_world_alias_as_grounding" in rule_ids
    assert all(rule["classification"] == "reject" for rule in rejection_rules["rules"])

    checklist_text = "\n".join(future["required_before_any_handoff_claim"])
    assert "same-run /tf dynamic_edges list and /tf_static static_edges list" in checklist_text
    assert "real_same_run_evidence" in checklist_text
    assert "evidence_path" in checklist_text
    assert "forbidden-topic absence" in checklist_text
    assert "cleanup summary" in checklist_text
    assert future["allowed_grounding_status_values"] == ["blocked_absent", "real_same_run_evidence"]
    blocked_text = "\n".join(future["handoff_stays_blocked_when"])
    assert "grounding basis is fake" in blocked_text
    assert "evidence_path is absent" in blocked_text


def test_075_source_static_checks_and_summary_are_complete() -> None:
    contract = load_json(CONTRACT)
    summary = load_json(CHECK_SUMMARY)

    for checks in contract["source_static_checks"].values():
        assert all(checks.values())

    assert summary["ok"] is True
    assert summary["failures"] == []
    assert all(summary["gates"].values())
    assert summary["gates"]["source_static_checks_present"] is True
    assert summary["gates"]["live_actions_all_false"] is True


def test_075_report_does_not_upgrade_claims() -> None:
    report = REPORT.read_text(encoding="utf-8")

    assert "Controller handoff remains blocked" in report
    assert "Current accepted evidence keeps `camera_init` as FAST-LIO output-only" in report
    assert "`real_same_run_tf_grounding`: `adopt`" in report
    assert "`arbitrary_static_transform_or_header_rename`: `reject`" in report
    assert "does not prove live ROS2/RViz/FAST-LIO success" in report
    assert "does not authorize controller handoff" in report
    forbidden_claims = [
        "planner_ready: true",
        "closed_loop: true",
        "TF/RViz readiness is proven",
        "controller handoff is authorized",
        "mission success is proven",
    ]
    for phrase in forbidden_claims:
        assert phrase not in report


def main() -> int:
    test_075_static_only_and_preserves_074_blocker_boundary()
    test_075_grounding_matrix_classifies_current_future_and_rejected_routes()
    test_075_rejects_fake_transform_routes_and_requires_same_run_evidence()
    test_075_source_static_checks_and_summary_are_complete()
    test_075_report_does_not_upgrade_claims()
    print("[OK] 075 camera_init map/world grounding static gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
