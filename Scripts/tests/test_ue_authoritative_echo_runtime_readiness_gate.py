from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_authoritative_echo_runtime_readiness_gate.py"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "authoritative_echo_runtime_readiness.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), "--output-json", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(output.read_text(encoding="utf-8"))


def test_027_checker_is_source_static_runtime_readiness_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["schema"] == "mosim.ue_authoritative_echo_runtime_readiness_gate.v1"
    assert report["scope_classification"] == "source-static/build-prep/runtime-readiness"
    assert report["source_static_readiness_ok"] is True
    assert report["runtime_ready_now"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_027"] is False
    assert report["live_socket_listener_or_transport_started"] is False
    assert report["ue_cpp_source_edited_by_027"] is False
    assert report["accepted_state_ui_controls_enabled"] is False


def test_prior_gate_inputs_record_024_025_026_evidence(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_gate_inputs"]
    assert prior["ue_024_status"] == "completed"
    assert prior["ue_024_quality_status"] == "runtime_echo_producer_downlink_source_static_build_prep_passed"
    assert prior["ue_025_status"] == "completed"
    assert prior["ue_025_quality_status"] == "runtime_echo_downlink_compile_gate_passed"
    assert prior["ue_025_compile_exit_code"] == 0
    assert prior["ue_025_compile_classification"] == "compile_pass_warning_only"
    assert prior["ue_026_status"] == "completed"
    assert prior["ue_026_quality_status"] == "runtime_echo_boundary_checker_refresh_source_static_passed"
    assert prior["ue_026_runtime_ack_leaks_now"] == 0
    assert prior["ue_026_actual_runtime_claim_rows"] == 0


def test_receiver_state_sender_and_frame_anchors_keep_boundaries(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    anchors = report["source_anchor_summary"]
    receiver = anchors["command_echo_receiver_shell"]
    state = anchors["state_component"]
    frame = anchors["frame_status_receiver"]
    sender = anchors["command_sender"]

    assert receiver["has_authoritative_validate_method"] is True
    assert receiver["has_authoritative_apply_method"] is True
    assert receiver["calls_state_sink"] is True
    assert receiver["runtime_transport_patterns_present"] == []
    assert receiver["forbidden_pose_patterns_present"] == []
    assert receiver["records_pending_requests"] is False
    assert receiver["parses_command_request_schema"] is False
    assert receiver["parses_quadrotor_unreal_state"] is False

    assert state["pending_source"] == "RecordPendingCommandFromPacketJson"
    assert state["echo_sink"] == "ApplyCommandEchoJson"
    assert set(state["non_live_labels_downgraded"]) == {
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
        "offline_adapter_smoke",
        "source_level_smoke",
    }
    assert state["non_live_source_quality_status"] == "smoke_only"
    assert state["non_live_accepted_as_runtime_ack"] is False

    assert frame["role"] == "quadrotor.unreal_state frame/status receiver only"
    assert frame["parses_command_echo_schema"] is False
    assert frame["calls_echo_sink"] is False
    assert sender["role"] == "mosim.ue_command.v1 sender only"
    assert sender["parses_command_echo_schema"] is False
    assert sender["calls_echo_sink"] is False
    assert sender["send_success_is_ack"] is False


def test_readiness_matrix_marks_static_parts_present_and_runtime_parts_missing(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = {row["row_id"]: row for row in report["source_static_readiness_matrix"]}
    for row_id in [
        "source_static_authoritative_downlink_handoff",
        "compile_only_evidence_for_handoff",
        "boundary_checker_false_ack_rejection",
        "pending_command_request_reducer",
        "command_echo_state_sink",
    ]:
        assert rows[row_id]["available_now"] is True
        assert rows[row_id]["required_for_live_ack"] is True
        assert rows[row_id]["accepted_as_runtime_ack_now"] is False

    for row_id in [
        "live_authoritative_echo_producer",
        "live_transport_capture_surface",
        "bounded_ue_runtime_probe_authorization",
        "matching_pending_request_and_echo_capture",
        "runtime_no_pose_overwrite_proof",
        "runtime_negative_false_ack_proof",
    ]:
        assert rows[row_id]["available_now"] is False
        assert rows[row_id]["required_for_live_ack"] is True
        assert rows[row_id]["accepted_as_runtime_ack_now"] is False
        assert rows[row_id]["missing_reason"]

    assert rows["final_operator_ui_acceptance"]["available_now"] is False
    assert rows["final_operator_ui_acceptance"]["required_for_live_ack"] is False


def test_false_ack_rejection_matrix_has_no_runtime_leaks(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["false_ack_rejection_matrix"]
    sources = {row["source"] for row in rows}
    assert {
        "024_source_static_handoff",
        "025_compile_pass",
        "026_checker_success",
        "UnrealBuildTool_success",
        "build_success",
        "checker_success",
        "pytest_success",
        "udp_send_success",
        "sender_result_bSent",
        "quadrotor.unreal_state.v1",
        "quadrotor.unreal_state.frame",
        "fixture_only_echo",
        "operator_intent",
        "static_fixture_row",
        "offline_adapter_smoke",
        "source_level_smoke",
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
    } <= sources
    assert {row["accepted_as_runtime_ack_now"] for row in rows} == {False}
    assert {row["runtime_transport_evidence"] for row in rows} == {False}
    assert {row["policy"] for row in rows} == {"reject_as_false_ack"}


def test_matrix_summary_shows_not_runtime_ready(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    summary = report["matrix_summary"]
    assert summary["total_readiness_rows"] == 12
    assert summary["required_rows_available_now"] == 5
    assert summary["required_rows_missing_now"] == 6
    assert summary["false_ack_rows"] >= 18
    assert summary["false_ack_runtime_leaks_now"] == 0
    assert summary["runtime_ready_now"] is False
    assert summary["authoritative_runtime_ack_claimable_now"] is False


def test_acceptance_contract_requires_pending_echo_identity_and_no_pose(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    contract = report["authoritative_echo_acceptance_contract"]
    assert "mosim.ue_command.v1" in contract["pending_precondition"]
    assert contract["echo_schema"] == "mosim.ue_command_echo.v1"
    assert contract["consumer_handoff"].endswith("ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState")
    assert contract["consumer_sink"] == "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
    assert contract["authoritative_source_authority_pairs"] == {
        "MWORKS_live_downlink": "MWORKS",
        "ROS2_runtime_echo": "ROS2",
        "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
    }
    assert {
        "schema",
        "source",
        "ack_authority",
        "run_id",
        "request_id",
        "seq",
        "time_s",
        "status",
        "command.kind or command_kind",
        "no_pose_overwrite_status",
    } <= set(contract["required_echo_fields"])
    assert {
        "live producer identity",
        "transport capture/log",
        "pending request capture",
        "matching request/echo identity",
        "no_pose_overwrite_status=pass",
        "negative false-ack rejection evidence",
    } <= set(contract["required_runtime_evidence"])


def test_next_runtime_gate_is_a_future_authorized_probe_not_027_runtime(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    next_gate = report["next_safe_runtime_gate"]
    assert "Do not run a live UE runtime probe from 027" in next_gate["recommendation"]
    assert "No live authoritative producer/downlink transport" in next_gate["blocked_now_reason"]
    assert {
        "explicit runtime/editor probe authorization",
        "single bounded probe budget and cleanup plan",
        "live authoritative producer for mosim.ue_command_echo.v1",
        "transport capture route from producer to UE command echo receiver",
        "pending mosim.ue_command.v1 request capture",
        "matching run_id/request_id/seq/time_s/command kind/status",
        "no_pose_overwrite_status=pass",
    } <= set(next_gate["minimum_preconditions"])


def test_claim_boundary_forbids_live_ack_and_success_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    assert "source-static/build-prep/runtime-readiness" in boundary
    assert "does not run Unreal Editor" in boundary
    assert "does not edit UE C++ source" in boundary
    assert "are not live runtime ack" in boundary
    assert "does not prove authoritative runtime ack" in boundary
    assert "planner_ready" in boundary
    assert "controller performance" in boundary
    assert "mission success" in boundary
    assert "closed_loop" in boundary
    assert all(value is False for value in report["forbidden_runtime_claims"].values())
