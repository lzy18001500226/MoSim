#!/usr/bin/env python3
"""Static checks for the 072 frame-policy/controller-handoff contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_frame_policy_controller_handoff_static_gate_20260608_072"
)
CONTRACT = EVIDENCE / "frame_policy_controller_handoff_contract.json"
MATRIX = EVIDENCE / "frame_policy_matrix.json"
REJECTION_RULES = EVIDENCE / "fake_transform_rejection_rules.json"
FUTURE_CHECKLIST = EVIDENCE / "future_live_evidence_checklist.json"
CHECK_SUMMARY = EVIDENCE / "static_frame_policy_check_summary.json"


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def test_072_static_only_and_claim_boundary() -> None:
    contract = load_json(CONTRACT)

    assert contract["mode"] == "source_static_contract_only"
    assert all(value is False for value in contract["live_actions"].values())
    boundary = "\n".join(contract["claim_boundary"])
    assert "static frame-policy/controller-handoff contract" in boundary
    assert "does not run ROS2" in boundary
    assert "does not publish planner goals" in boundary
    assert "does not prove true sensor capture" in boundary
    assert "TF/RViz readiness" in boundary
    assert "closed_loop" in boundary


def test_072_camera_init_is_output_review_not_controller_acceptance() -> None:
    contract = load_json(CONTRACT)
    matrix = {item["frame"]: item for item in load_json(MATRIX)}
    policy = contract["controller_handoff_policy"]

    assert matrix["camera_init"]["controller_handoff_role"] == "reference_only_output_review_frame"
    assert "not accepted as map/world" in matrix["camera_init"]["policy"]
    assert matrix["camera_init"]["current_evidence"]["/Odometry_frame"] == "camera_init"
    assert matrix["camera_init"]["current_evidence"]["/cloud_registered_frame"] == "camera_init"
    assert matrix["camera_init"]["current_evidence"]["dynamic_tf_edges"] == ["camera_init->body"]
    assert matrix["camera_init"]["current_evidence"]["tf_static_edges"] == []

    assert policy["current_fastlio_output"]["fixed_frame"] == "camera_init"
    assert policy["current_fastlio_output"]["classification"] == "reference_only_output_review_frame"
    assert "does not prove camera_init equals" in policy["gap"]
    assert "blocked_pending_real_frame_policy_evidence" in policy["status"]


def test_072_map_world_controller_contract_and_alias_boundary() -> None:
    matrix = {item["frame"]: item for item in load_json(MATRIX)}
    contract = load_json(CONTRACT)
    acceptance = contract["controller_handoff_policy"]["current_controller_acceptance"]

    assert matrix["map"]["controller_handoff_role"] == "canonical_acceptance_frame_static_only"
    assert matrix["map"]["current_evidence"]["adapter_input_topic"] == "/mosim/planner/position_cmd"
    assert matrix["map"]["current_evidence"]["adapter_output_topic"] == "/mosim/planner/setpoint"
    assert matrix["map"]["current_evidence"]["rate_hz"] == 20.0
    assert matrix["map"]["current_evidence"]["stale_timeout_s"] == 0.15

    assert matrix["world"]["controller_handoff_role"] == "alias_only_for_PositionCommand_input"
    assert matrix["world"]["current_evidence"]["input_topic"] == "/position_cmd"
    assert matrix["world"]["current_evidence"]["normalizes_output_to"] == "map"
    assert "not evidence that camera_init equals world" in "\n".join(matrix["world"]["forbidden_use"])

    assert acceptance["canonical_frame"] == "map"
    assert acceptance["source_alias"] == "world"
    assert acceptance["monotonic_stamp_required"] is True


def test_072_rejects_fake_transform_routes_and_preserves_future_gate() -> None:
    rejection_rules = load_json(REJECTION_RULES)
    future = load_json(FUTURE_CHECKLIST)
    summary = load_json(CHECK_SUMMARY)

    rule_ids = {rule["rule_id"] for rule in rejection_rules["rules"]}
    assert "reject_arbitrary_camera_init_to_map_static_tf" in rule_ids
    assert "reject_frame_rename" in rule_ids
    assert "reject_fake_odom_map_republisher" in rule_ids
    assert "reject_world_alias_as_transform" in rule_ids
    assert all(rule["classification"] == "reject" for rule in rejection_rules["rules"])

    checklist_text = "\n".join(future["required_same_run_evidence_before_controller_handoff"])
    assert "real camera_init<->map/world grounding" in checklist_text
    assert "controller handoff remains blocked" in checklist_text
    assert "Forbidden-topic absence" in checklist_text
    assert "No current accepted evidence grounds camera_init to map/world." in future["blocked_until"]

    assert summary["ok"] is True
    assert summary["gates"]["tf_static_gap_visible"] is True
    assert summary["gates"]["fake_transform_routes_rejected"] is True
    assert all(summary["gates"].values())


def test_072_source_static_checks_cover_adapter_and_wrapper_contracts() -> None:
    contract = load_json(CONTRACT)
    for checks in contract["source_static_checks"].values():
        assert all(checks.values())


def main() -> int:
    test_072_static_only_and_claim_boundary()
    test_072_camera_init_is_output_review_not_controller_acceptance()
    test_072_map_world_controller_contract_and_alias_boundary()
    test_072_rejects_fake_transform_routes_and_preserves_future_gate()
    test_072_source_static_checks_cover_adapter_and_wrapper_contracts()
    print("[OK] 072 frame-policy/controller-handoff static gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
