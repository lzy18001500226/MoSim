from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_live_echo_receiver_boundary.py"
STATE_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
FRAME_RECEIVER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "boundary.json"
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


def test_boundary_checker_reflects_024_025_without_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["schema"] == "mosim.ue_runtime_echo_boundary_checker_refresh_static_gate.v1"
    assert report["scope_classification"] == "source-static checker/test/evidence refresh"
    assert report["source_static_authoritative_downlink_handoff_present"] is True
    assert report["compile_only_evidence_present"] is True
    assert report["runtime_probe_executed"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_editor_opened"] is False
    assert report["unreal_build_executed_in_026"] is False
    assert report["live_transport_bound_or_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False


def test_prior_gate_inputs_record_024_handoff_and_025_compile_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_gate_inputs"]
    assert prior["ue_024_status"] == "completed"
    assert prior["ue_024_quality_status"] == "runtime_echo_producer_downlink_source_static_build_prep_passed"
    assert prior["ue_025_status"] == "completed"
    assert prior["ue_025_quality_status"] == "runtime_echo_downlink_compile_gate_passed"
    assert prior["ue_025_compile_classification"] == "compile_pass_warning_only"
    assert prior["ue_025_compile_exit_code"] == 0


def test_receiver_shell_exists_but_is_not_a_runtime_transport_receiver(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    decision = report["receiver_boundary_decision"]
    shell = report["source_anchor_summary"]["command_echo_receiver_shell"]
    assert decision["source_static_echo_receiver_shell_present"] is True
    assert decision["runtime_transport_receiver_present"] is False
    assert decision["current_live_echo_receiver_present"] is False
    assert shell["has_authoritative_validate_method"] is True
    assert shell["has_authoritative_apply_method"] is True
    assert shell["has_source_static_apply_method"] is True
    assert shell["calls_state_sink"] is True
    assert shell["runtime_transport_patterns_present"] == []
    assert shell["forbidden_pose_patterns_present"] == []
    assert shell["records_pending_requests"] is False
    assert shell["parses_command_request_schema"] is False
    assert shell["parses_quadrotor_unreal_state"] is False


def test_existing_frame_receiver_and_sender_are_not_ack_consumers(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    anchors = report["source_anchor_summary"]
    frame = anchors["frame_status_receiver"]
    sender = anchors["command_sender"]
    assert frame["role"] == "quadrotor.unreal_state frame/status receiver only"
    assert frame["parses_command_echo_schema"] is False
    assert frame["calls_echo_sink"] is False
    assert sender["role"] == "mosim.ue_command.v1 sender only"
    assert sender["parses_command_echo_schema"] is False
    assert sender["calls_echo_sink"] is False
    assert sender["send_success_is_ack"] is False


def test_current_state_component_downgrades_known_preflight_labels() -> None:
    source = STATE_SOURCE.read_text(encoding="utf-8")
    smoke_source_start = source.index("bool IsSmokeSource")
    smoke_source_end = source.index("}\n}", smoke_source_start)
    smoke_source_body = source[smoke_source_start:smoke_source_end]
    for label in [
        "offline_adapter_smoke",
        "source_level_smoke",
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
    ]:
        assert f'TEXT("{label}")' in smoke_source_body


def test_source_labels_keep_smoke_only_and_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    labels = report["source_labels"]
    assert labels["non_live_sources_missing_from_state_component"] == []
    assert labels["non_live_sources_covered_by_state_component"] == [
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
        "offline_adapter_smoke",
        "source_level_smoke",
    ]
    assert labels["non_live_source_quality_status"] == "smoke_only"
    assert labels["non_live_accepted_as_runtime_ack"] is False


def test_authoritative_future_rows_are_handoff_eligible_not_current_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["boundary_fixture_matrix"]
    eligible = [row for row in rows if row["source_static_handoff_eligible_for_future_live_probe"]]
    assert {row["row_name"] for row in eligible} == {
        "future_authoritative_accepted_MWORKS_live_downlink",
        "future_authoritative_accepted_ROS2_runtime_echo",
        "future_authoritative_accepted_MWORKS_ROS2_live_downlink",
        "future_authoritative_rejected_MWORKS_live_downlink",
        "future_authoritative_rejected_ROS2_runtime_echo",
        "future_authoritative_rejected_MWORKS_ROS2_live_downlink",
    }
    assert {row["accepted_as_runtime_ack_now"] for row in rows} == {False}
    assert {row["actual_runtime_transport_evidence"] for row in rows} == {False}
    accepted_if_live = [row for row in rows if row["would_be_runtime_ack_if_live_transport_verified"]]
    assert {row["row_name"] for row in accepted_if_live} == {
        "future_authoritative_accepted_MWORKS_live_downlink",
        "future_authoritative_accepted_ROS2_runtime_echo",
        "future_authoritative_accepted_MWORKS_ROS2_live_downlink",
    }


def test_false_ack_and_non_live_sources_reject_before_state_sink(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    false_ack_sources = set(report["source_labels"]["false_ack_sources_rejected_now"])
    assert {
        "024_source_static_handoff",
        "025_compile_pass",
        "UnrealBuildTool_success",
        "build_success",
        "checker_success",
        "pytest_success",
        "udp_send_success",
        "sender_result_bSent",
        "quadrotor.unreal_state.v1",
        "quadrotor.unreal_state.frame",
        "fixture_only_echo",
        "static_catalog_row",
        "operator_intent",
    } <= false_ack_sources
    rows = [
        row
        for row in report["boundary_fixture_matrix"]
        if row["source"] in false_ack_sources or row["source"] in report["source_labels"]["non_live_sources_expected"]
    ]
    assert rows
    assert {row["downlink_policy"] for row in rows} == {"reject_before_state_sink"}
    assert {row["source_static_handoff_eligible_for_future_live_probe"] for row in rows} == {False}
    assert {row["accepted_as_runtime_ack_now"] for row in rows} == {False}


def test_malformed_identity_authority_and_pose_rows_reject_before_state_sink(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    malformed = {
        "missing_run_id",
        "missing_request_id",
        "missing_seq",
        "missing_time_s",
        "missing_command_kind",
        "wrong_authority_for_source",
        "no_pose_overwrite_failure",
        "forbidden_pose_command",
        "frame_schema_not_echo",
    }
    rows = [row for row in report["boundary_fixture_matrix"] if row["row_name"] in malformed]
    assert len(rows) == len(malformed)
    assert {row["downlink_policy"] for row in rows} == {"reject_before_state_sink"}
    assert {row["source_static_handoff_eligible_for_future_live_probe"] for row in rows} == {False}
    assert {row["accepted_as_runtime_ack_now"] for row in rows} == {False}


def test_matrix_summary_has_no_current_runtime_ack_leaks(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    summary = report["matrix_summary"]
    assert summary["future_authoritative_handoff_eligible_rows"] == 6
    assert summary["future_authoritative_accepted_rows"] == 3
    assert summary["future_authoritative_rejected_rows"] == 3
    assert summary["non_live_rows"] == 4
    assert summary["false_ack_rows"] == 16
    assert summary["invalid_rows"] == 9
    assert summary["runtime_ack_leaks_now"] == 0
    assert summary["actual_runtime_claim_rows"] == 0


def test_existing_udp_receiver_is_frame_only_not_command_echo_receiver() -> None:
    source = FRAME_RECEIVER_SOURCE.read_text(encoding="utf-8")
    assert "quadrotor.unreal_state." in source
    assert "mosim.ue_command_echo.v1" not in source
    assert "ApplyCommandEchoJson" not in source


def test_claim_boundary_forbids_live_ack_and_planner_controller_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = report["claim_boundary"]
    assert boundary["not_live_ue_runtime_ack"] is True
    assert boundary["not_live_mworks_downlink"] is True
    assert boundary["not_ros2_runtime_ack"] is True
    assert boundary["not_final_ui_acceptance"] is True
    assert boundary["planner_ready"] is False
    assert boundary["closed_loop_ready"] is False
    assert boundary["controller_performance"] is False
    assert boundary["fast_lio_success"] is False
    assert boundary["mission_success"] is False
    assert all(value is False for value in report["forbidden_runtime_claims"].values())
