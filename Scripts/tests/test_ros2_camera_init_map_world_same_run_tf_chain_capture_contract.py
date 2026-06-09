#!/usr/bin/env python3
"""Static checks for the 078 same-run TF-chain capture contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_camera_init_map_world_same_run_tf_chain_capture_contract_20260609_078"
)

CONTRACT = EVIDENCE / "same_run_tf_chain_capture_contract_078.json"
FIELD_LIST = EVIDENCE / "future_evidence_bundle_field_list_078.json"
ACCEPTANCE = EVIDENCE / "real_same_run_evidence_acceptance_rule_078.json"
REJECTION = EVIDENCE / "tf_chain_rejection_rules_078.json"
CHECKER_CONTRACT = EVIDENCE / "static_checker_contract_078.json"
SUMMARY = EVIDENCE / "same_run_tf_chain_capture_contract_summary_078.json"
REPORT = EVIDENCE / "same_run_tf_chain_capture_contract_report_078.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_078_targets_077_adopt_route_and_preserves_076_boundary() -> None:
    contract = load_json(CONTRACT)
    summary = load_json(SUMMARY)

    assert contract["mode"] == "source_static_capture_contract_only"
    assert contract["target_route"]["route_id"] == "future_same_run_tf_chain_camera_init_to_map_or_world"
    assert contract["target_route"]["classification_from_077"] == "adopt"
    assert contract["upstream_boundaries"]["076_grounding_status"] == "blocked_absent"
    assert contract["upstream_boundaries"]["076_dynamic_edges"] == ["camera_init->body"]
    assert contract["upstream_boundaries"]["076_static_edges"] == []
    assert contract["upstream_boundaries"]["076_controller_handoff"] == "blocked_no_map_world_grounding"

    assert summary["ok"] is True
    assert summary["target_route_classification"] == "adopt"
    assert summary["preserves_076_grounding_status"] == "blocked_absent"
    assert summary["can_authorize_live_probe_from_078"] is False
    assert summary["can_authorize_controller_handoff_from_078"] is False
    assert all(value is False for value in summary["live_actions"].values())


def test_078_future_bundle_fields_require_raw_tf_and_same_run_scope() -> None:
    fields = load_json(FIELD_LIST)
    tf_fields = set(fields["tf_required_fields"])
    same_run_fields = set(fields["same_run_consistency_fields"])

    assert "tf.dynamic_events_path" in tf_fields
    assert "tf.static_events_path" in tf_fields
    assert "tf.dynamic_edges" in tf_fields
    assert "tf.static_edges" in tf_fields
    assert "tf.camera_init_map_world_grounding.evidence_path" in tf_fields
    assert "tf.camera_init_map_world_grounding.non_fake_basis" in tf_fields
    assert "tf.camera_init_map_world_grounding.chain" in tf_fields

    assert "same_run_scope.scope_id" in same_run_fields
    assert "source_topics.lidar.same_run_scope_id" in same_run_fields
    assert "source_topics.imu.same_run_scope_id" in same_run_fields
    assert "fastlio.same_run_scope_id" in same_run_fields
    assert "tf.same_run_scope_id" in same_run_fields
    assert "forbidden_topic_absence.same_run_scope_id" in same_run_fields
    assert "cleanup.same_run_scope_id" in same_run_fields


def test_078_real_same_run_acceptance_rule_is_strict() -> None:
    rule = load_json(ACCEPTANCE)
    must = "\n".join(rule["must_all_be_true"])

    assert rule["status_value"] == "real_same_run_evidence"
    assert "selected_route_id equals future_same_run_tf_chain_camera_init_to_map_or_world" in must
    assert "selected_route_classification equals adopt" in must
    assert "tf_dynamic_events_path and tf_static_events_path are present" in must
    assert "an ordered chain connects camera_init to map, world, or ue_world in the same run" in must
    assert "camera_init_map_world_grounding.evidence_path is present" in must
    assert "camera_init_map_world_grounding.non_fake_basis is true" in must
    assert "source topics and FAST-LIO outputs overlap the TF capture window in the same run" in must
    assert "073 base validator ok=true and 078 route-specific validator ok=true" in must
    assert "still not automatic" in rule["controller_handoff_after_acceptance"]


def test_078_rejects_reference_fake_arbitrary_and_header_only_routes() -> None:
    rules = {item["route"]: item for item in load_json(REJECTION)}

    assert rules["current_076_camera_init_output_only"]["classification"] == "reference_only"
    assert rules["current_076_camera_init_output_only"]["reject_for_real_grounding"] is True
    assert "cannot be promoted" in rules["current_076_camera_init_output_only"]["reason"]

    assert rules["arbitrary_static_transform_or_header_frame_rename"]["classification"] == "reject"
    assert "header.frame_id rename" in rules["arbitrary_static_transform_or_header_frame_rename"]["reason"]

    assert rules["world_alias_as_transform"]["classification"] == "reject"
    assert "world alias" in rules["world_alias_as_transform"]["reason"]

    assert rules["fake_sensor_truth_or_gui_shortcut"]["classification"] == "reject"
    assert "Fake point cloud/map/odom/TF" in rules["fake_sensor_truth_or_gui_shortcut"]["reason"]

    assert rules["raw_tf_files_absent"]["classification"] == "reject"
    assert rules["same_run_scope_mismatch"]["classification"] == "reject"


def test_078_checker_contract_and_report_do_not_upgrade_claims() -> None:
    checker = load_json(CHECKER_CONTRACT)
    report = REPORT.read_text(encoding="utf-8")

    assert checker["checker_mode"] == "source_static_file_only"
    assert checker["no_test_rationale"] is None
    assert "raw /tf and /tf_static event paths" in "\n".join(checker["checks"])

    assert "source/static route-specific capture contract" in report
    assert "076 grounding status remains: `blocked_absent`" in report
    assert "Set `camera_init_map_world_grounding.status=real_same_run_evidence` only when" in report
    assert "`current_076_camera_init_output_only`: `reference_only`" in report
    assert "`arbitrary_static_transform_or_header_frame_rename`: `reject`" in report

    forbidden_claims = [
        "planner_ready: true",
        "closed_loop: true",
        "controller handoff is authorized",
        "runtime success is proven",
        "mission success is proven",
        "TF/RViz readiness is proven",
    ]
    for phrase in forbidden_claims:
        assert phrase not in report


def main() -> int:
    test_078_targets_077_adopt_route_and_preserves_076_boundary()
    test_078_future_bundle_fields_require_raw_tf_and_same_run_scope()
    test_078_real_same_run_acceptance_rule_is_strict()
    test_078_rejects_reference_fake_arbitrary_and_header_only_routes()
    test_078_checker_contract_and_report_do_not_upgrade_claims()
    print("[OK] 078 same-run TF-chain capture contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
