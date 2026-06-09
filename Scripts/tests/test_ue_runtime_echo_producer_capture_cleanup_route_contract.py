from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_echo_producer_capture_cleanup_route_contract.py"

EXPECTED_ARTIFACTS = {
    "runtime_probe_manifest.json",
    "pending_request_capture.json",
    "authoritative_echo_capture.json",
    "request_echo_match_report.json",
    "no_pose_overwrite_report.json",
    "false_ack_negative_report.json",
    "timeout_cleanup_manifest.json",
}


def run_checker(tmp_path: Path) -> dict:
    output_json = tmp_path / "runtime_echo_producer_capture_cleanup_route_contract.json"
    output_md = tmp_path / "runtime_echo_producer_capture_cleanup_route_contract.md"
    output_matrix = tmp_path / "runtime_echo_producer_capture_cleanup_route_contract_matrix.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--output-matrix",
            str(output_matrix),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert output_json.exists()
    assert output_md.exists()
    assert output_matrix.exists()
    return json.loads(output_json.read_text(encoding="utf-8"))


def test_route_contract_is_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static producer/capture/cleanup route contract"
    assert report["source_static_route_contract_ready"] is True
    assert report["runtime_route_ready_now"] is False
    assert report["live_attempt_consumed"] is False
    assert report["runtime_probe_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_035"] is False
    assert report["socket_listener_timer_thread_or_background_loop_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert report["live_transport_evidence_rows"] == 0
    assert report["runtime_ack_leaks_now"] == 0


def test_034_blocker_budget_is_preserved(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    consumed = report["prior_evidence_consumed"]
    assert consumed["ue_034_status"] == "blocked"
    assert consumed["ue_034_live_attempt_consumed"] is False
    assert consumed["ue_034_runtime_probe_executed"] is False
    assert consumed["ue_032_source_static_wiring_ready"] is True
    assert consumed["ue_033_source_static_plan_ready"] is True


def test_authoritative_producer_contract_names_allowed_pairs(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    producer = report["producer_capture_cleanup_route_contract"]["authoritative_producer_identity"]
    pairs = report["producer_capture_cleanup_route_contract"]["authoritative_source_authority_pairs"]
    assert producer["status_now"] == "contract_defined_missing_live_producer_instance"
    assert pairs == {
        "MWORKS_live_downlink": "MWORKS",
        "ROS2_runtime_echo": "ROS2",
        "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
    }
    for field in [
        "producer_surface",
        "producer_instance_id",
        "source",
        "ack_authority",
        "capture_session_id",
        "transport_capture_id",
    ]:
        assert field in producer["required_fields"]


def test_field_level_contract_covers_exactly_seven_artifacts(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["field_level_capture_contract"]
    assert {row["artifact"] for row in rows} == EXPECTED_ARTIFACTS
    assert report["matrix_summary"]["field_level_capture_contract_rows"] == 7
    assert report["producer_capture_cleanup_route_contract"]["seven_artifact_generation"]["artifacts"] == list(EXPECTED_ARTIFACTS) or set(report["producer_capture_cleanup_route_contract"]["seven_artifact_generation"]["artifacts"]) == EXPECTED_ARTIFACTS
    assert all(row["current_runtime_ready"] is False for row in rows)
    assert all(row["accepted_as_runtime_ack_now"] is False for row in rows)


def test_authoritative_echo_is_only_direct_receiver_input(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["field_level_capture_contract"]
    direct_rows = [row for row in rows if row["direct_receiver_input"]]
    assert len(direct_rows) == 1
    assert direct_rows[0]["artifact"] == "authoritative_echo_capture.json"
    echo = report["producer_capture_cleanup_route_contract"]["authoritative_echo_capture"]
    assert echo["schema"] == "mosim.ue_command_echo.v1"
    assert echo["direct_receiver_input"] is True
    assert echo["receiver_surface_validate_method"] == "ValidateAuthoritativeRuntimeCommandEchoDownlinkJson"
    assert echo["receiver_surface_ingest_method"] == "IngestAuthoritativeRuntimeCommandEchoDownlinkJson"


def test_pending_request_and_cleanup_contracts_are_not_runtime_ready(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    pending = report["producer_capture_cleanup_route_contract"]["pending_request_capture"]
    cleanup = report["producer_capture_cleanup_route_contract"]["timeout_cleanup"]
    assert pending["schema"] == "mosim.ue_command.v1"
    assert pending["must_exist_before_echo"] is True
    assert pending["receiver_surface_must_not_synthesize_pending"] is True
    assert pending["status_now"] == "contract_defined_missing_live_capture_route"
    assert cleanup["timeout_seconds_inclusive_max"] <= 60
    assert cleanup["probe_attempt_count"] == 1
    assert cleanup["retry_count"] == 0
    assert cleanup["status_now"] == "contract_defined_missing_live_cleanup_route"


def test_route_readiness_matrix_materializes_034_missing_routes(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    routes = {row["route"]: row for row in report["route_readiness_matrix"]}
    for route in [
        "authoritative_producer_identity",
        "pending_request_capture",
        "authoritative_echo_capture",
        "request_echo_identity_match",
        "no_pose_overwrite_proof",
        "false_ack_negative_proof",
        "timeout_cleanup_proof",
    ]:
        assert route in routes
        assert routes[route]["contract_defined_now"] is True
        assert routes[route]["source_static_evidence_now"] is True
        assert routes[route]["current_runtime_ready"] is False
        assert routes[route]["blocks_live_probe_until_implemented"] is True
        assert routes[route]["accepted_as_runtime_ack_now"] is False
    assert report["matrix_summary"]["current_runtime_ready_rows"] == 0


def test_false_ack_rules_reject_static_build_sender_fixture_and_frame_sources(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    sources = {row["source"] for row in report["false_ack_rejection_rules"]}
    for source in [
        "034_no_side_effect_preflight_blocker",
        "033_single_bounded_probe_plan_checker",
        "032_capture_bundle_wiring_checker",
        "031_compile_pass",
        "build_success",
        "checker_success",
        "sender_result_bSent",
        "udp_send_success",
        "fixture_only_echo",
        "operator_intent",
        "quadrotor.unreal_state.frame",
        "quadrotor.unreal_state.v1",
        "MWORKS_MCP_runtime_adapter_preflight",
    ]:
        assert source in sources
    assert all(row["expected_result"] == "reject_as_live_runtime_ack" for row in report["false_ack_rejection_rules"])
    assert all(row["accepted_as_runtime_ack_now"] is False for row in report["false_ack_rejection_rules"])


def test_no_pose_rules_and_receiver_surface_boundary(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    checks = {row["check"] for row in report["no_pose_overwrite_rules"]}
    for check in [
        "keyboard_pose",
        "direct_actor_transform",
        "actor_teleport",
        "pose_override",
        "set_uav_pose",
        "SetActorLocation",
        "SetActorTransform",
        "TeleportTo",
        "UE_truth_shortcut",
    ]:
        assert check in checks
    boundary = report["source_static_receiver_boundary"]
    assert boundary["validate_method_present"] is True
    assert boundary["ingest_method_present"] is True
    assert boundary["boundary_method_present"] is True
    assert boundary["runtime_transport_patterns_present"] == []
    assert boundary["forbidden_pose_patterns_present"] == []
    assert boundary["parses_pending_command_request_schema"] is False


def test_claim_boundary_forbids_live_success_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    for phrase in [
        "source/static producer/capture/cleanup route contract",
        "does not open Unreal Editor",
        "does not run Unreal build",
        "does not edit UE C++ source",
        "not live runtime ack",
        "live_attempt_consumed=false",
        "does not prove live UE runtime ack",
        "MWORKS downlink",
        "ROS2 runtime echo",
        "final UI acceptance",
        "planner_ready",
        "controller performance",
        "mission success",
        "closed_loop",
    ]:
        assert phrase in boundary
