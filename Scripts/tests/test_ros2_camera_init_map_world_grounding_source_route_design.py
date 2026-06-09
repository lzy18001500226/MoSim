#!/usr/bin/env python3
"""Static checks for the 077 camera_init-to-map/world source route design."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_camera_init_map_world_grounding_source_route_design_20260609_077"
)
CONTRACT = EVIDENCE / "camera_init_map_world_grounding_source_route_design.json"
MATRIX = EVIDENCE / "camera_init_map_world_source_route_matrix.json"
FUTURE_GATE = EVIDENCE / "camera_init_map_world_future_evidence_gate_077.json"
SUMMARY = EVIDENCE / "camera_init_map_world_source_route_design_summary.json"
REPORT = EVIDENCE / "camera_init_map_world_source_route_design_report.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def routes_by_id() -> dict[str, dict]:
    return {route["route_id"]: route for route in load_json(MATRIX)}


def test_077_preserves_076_blocked_absent_boundary() -> None:
    contract = load_json(CONTRACT)
    summary = load_json(SUMMARY)

    assert contract["mode"] == "source_static_route_design_only"
    assert contract["upstream_evidence"]["076_grounding"]["status"] == "blocked_absent"
    assert contract["upstream_evidence"]["076_controller_handoff"]["status"] == "blocked_no_map_world_grounding"
    assert contract["upstream_evidence"]["076_validator"]["ok"] is True

    assert summary["ok"] is True
    assert summary["upstream_status"]["076_grounding_status"] == "blocked_absent"
    assert summary["current_decision"]["controller_handoff_status"] == "blocked_no_map_world_grounding"
    assert summary["current_decision"]["can_authorize_controller_handoff_from_077"] is False
    assert summary["current_decision"]["can_authorize_live_probe_from_077"] is False
    assert all(value is False for value in summary["live_actions"].values())


def test_077_route_matrix_has_required_classifications() -> None:
    routes = routes_by_id()

    assert routes["current_076_camera_init_output_only"]["classification"] == "reference_only"
    assert routes["current_076_camera_init_output_only"]["facts"]["grounding_status"] == "blocked_absent"

    assert routes["future_same_run_tf_chain_camera_init_to_map_or_world"]["classification"] == "adopt"
    adopt_required = "\n".join(routes["future_same_run_tf_chain_camera_init_to_map_or_world"]["next_proof_required"])
    assert "raw TF event file path" in adopt_required
    assert "camera_init connected to map/world" in adopt_required
    assert "fake/arbitrary/header rename" in adopt_required

    assert routes["spark_fast_lio_map_frame_binding"]["classification"] == "adapt"
    assert routes["spark_fast_lio_map_frame_binding"]["source_static_facts"]["launch_declares_map_frame_default_ue_world"] is True
    assert routes["spark_fast_lio_map_frame_binding"]["source_static_facts"]["launch_passes_common_map_frame"] is True

    assert routes["mworks_state_truth_tf_as_external_grounding_measurement"]["classification"] == "adapt"
    assert routes["mworks_state_truth_tf_as_external_grounding_measurement"]["source_static_facts"]["broadcasts_world_to_body_tf"] is True

    assert routes["controller_map_world_policy"]["classification"] == "reference_only"
    assert routes["controller_map_world_policy"]["source_static_facts"]["converter_accepts_world_alias"] is True
    assert routes["controller_map_world_policy"]["source_static_facts"]["converter_normalizes_to_map"] is True

    assert routes["arbitrary_static_transform_or_header_frame_rename"]["classification"] == "reject"
    assert routes["fake_sensor_truth_or_gui_shortcut"]["classification"] == "reject"


def test_077_future_gate_blocks_reference_only_and_fake_routes() -> None:
    gate = load_json(FUTURE_GATE)

    assert gate["allowed_route_classifications_for_next_probe"] == ["adopt", "adapt"]
    assert gate["rejected_route_classifications_for_handoff"] == ["reference_only", "reject"]
    pre_probe_text = "\n".join(gate["pre_probe_static_requirements"])
    assert "selected_route_id" in pre_probe_text
    assert "source/config provenance" in pre_probe_text
    assert "fake/arbitrary/header-only" in pre_probe_text

    must_include = "\n".join(gate["real_grounding_acceptance"]["must_include"])
    assert "evidence_path" in must_include
    assert "non_fake_basis" in must_include
    assert "same_run_source_topics_and_fastlio_outputs" in must_include
    assert "validator_ok_true" in must_include

    blocked_text = "\n".join(gate["handoff_remains_blocked_when"])
    assert "selected route is reference_only" in blocked_text
    assert "selected route is reject" in blocked_text
    assert "map_frame parameter exists but no same-run TF/output evidence links camera_init to map/world" in blocked_text
    assert "grounding basis is fake" in blocked_text
    assert "/position_cmd" in gate["forbidden_before_controller_handoff"]
    assert "/mosim/planner/setpoint" in gate["forbidden_before_controller_handoff"]


def test_077_source_static_checks_are_present() -> None:
    summary = load_json(SUMMARY)
    checks = summary["source_static_checks"]

    for check_group in checks.values():
        assert all(check_group.values())

    assert summary["route_counts"] == {
        "adopt": 1,
        "adapt": 2,
        "reference_only": 2,
        "reject": 2,
    }


def test_077_report_does_not_upgrade_claims() -> None:
    report = REPORT.read_text(encoding="utf-8")

    assert "source/static route design artifact" in report
    assert "076 camera_init-to-map/world grounding: `blocked_absent`" in report
    assert "`future_same_run_tf_chain_camera_init_to_map_or_world`: `adopt`" in report
    assert "`spark_fast_lio_map_frame_binding`: `adapt`" in report
    assert "`arbitrary_static_transform_or_header_frame_rename`: `reject`" in report
    assert "077 does not prove current camera_init-to-map/world grounding" in report
    assert "077 does not authorize planner/controller handoff" in report

    forbidden_claims = [
        "planner_ready: true",
        "closed_loop: true",
        "controller handoff is authorized",
        "runtime success is proven",
        "mission success is proven",
    ]
    for phrase in forbidden_claims:
        assert phrase not in report


def main() -> int:
    test_077_preserves_076_blocked_absent_boundary()
    test_077_route_matrix_has_required_classifications()
    test_077_future_gate_blocks_reference_only_and_fake_routes()
    test_077_source_static_checks_are_present()
    test_077_report_does_not_upgrade_claims()
    print("[OK] 077 camera_init map/world grounding source route design")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
