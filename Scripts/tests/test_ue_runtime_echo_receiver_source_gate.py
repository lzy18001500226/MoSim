from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_echo_receiver_source_gate.py"


def run_checker(tmp_path: Path) -> dict:
    output_json = tmp_path / "runtime_echo_receiver_source_gate.json"
    output_md = tmp_path / "runtime_echo_receiver_source_gate.md"
    output_matrix = tmp_path / "runtime_echo_receiver_source_gate_fixture_matrix.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--output-fixture-matrix",
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
    assert output_md.exists()
    assert output_matrix.exists()
    return json.loads(output_json.read_text(encoding="utf-8"))


def test_receiver_surface_is_source_static_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static receiver surface gate"
    assert report["source_static_receiver_surface_present"] is True
    assert report["runtime_probe_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_030"] is False
    assert report["socket_listener_timer_or_background_loop_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert all(value is False for value in report["forbidden_runtime_claims"].values())


def test_receiver_surface_has_no_live_transport_or_pose_shortcuts(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    surface = report["source_anchor_summary"]["receiver_surface"]
    assert surface["calls_authoritative_validate"] is True
    assert surface["calls_authoritative_apply"] is True
    assert surface["tick_disabled"] is True
    assert surface["runtime_transport_patterns_present"] == []
    assert surface["forbidden_pose_patterns_present"] == []
    assert surface["parses_command_request_schema"] is False
    assert surface["parses_quadrotor_unreal_state"] is False
    contract = report["receiver_surface_contract"]
    assert contract["does_not_start_transport"] is True
    assert contract["does_not_bind_socket"] is True
    assert contract["does_not_start_listener_timer_thread_or_background_loop"] is True
    assert contract["does_not_create_pose_control"] is True


def test_handoff_chain_uses_existing_authoritative_echo_receiver_and_state_sink(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    contract = report["receiver_surface_contract"]
    assert contract["input_schema"] == "mosim.ue_command_echo.v1"
    assert "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.IsAuthoritativeRuntimeCommandEchoPacketJson" in contract["validation_chain"]
    assert "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState" in contract["handoff_chain"]
    assert "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson" in contract["handoff_chain"]
    assert "mosim.ue_command.v1" in contract["pending_precondition"]


def test_future_authoritative_sources_are_candidates_but_not_ack_now(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    candidates = [
        row for row in report["fixture_matrix"]
        if row["source_surface_eligible_for_future_runtime_probe"]
    ]
    assert len(candidates) == 6
    assert {row["source"] for row in candidates} == {
        "MWORKS_live_downlink",
        "ROS2_runtime_echo",
        "MWORKS_ROS2_live_downlink",
    }
    assert {row["status"] for row in candidates} == {"accepted", "rejected"}
    assert all(row["accepted_as_runtime_ack_now"] is False for row in candidates)
    assert all(row["live_transport_evidence"] is False for row in candidates)


def test_false_ack_non_live_sender_frame_and_static_rows_are_rejected(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rejected_sources = set(report["receiver_surface_contract"]["rejected_as_ack_sources"])
    for source in [
        "030_source_static_receiver_surface",
        "029_capture_bundle_validator",
        "build_success",
        "checker_success",
        "pytest_success",
        "sender_result_bSent",
        "udp_send_success",
        "fixture_only_echo",
        "operator_intent",
        "quadrotor.unreal_state.frame",
        "quadrotor.unreal_state.v1",
        "offline_adapter_smoke",
        "source_level_smoke",
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
    ]:
        assert source in rejected_sources
    false_rows = [
        row for row in report["fixture_matrix"]
        if row["source"] in rejected_sources
    ]
    assert false_rows
    assert all(row["source_surface_eligible_for_future_runtime_probe"] is False for row in false_rows)
    assert all(row["accepted_as_runtime_ack_now"] is False for row in false_rows)


def test_prior_gates_are_inherited_without_turning_into_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_gate_status"]
    assert prior["ue_024_completed"] is True
    assert prior["ue_025_completed"] is True
    assert prior["ue_025_compile_exit_code"] == 0
    assert prior["ue_026_runtime_ack_leaks_now"] == 0
    assert prior["ue_027_runtime_ready_now"] is False
    assert prior["ue_028_runtime_probe_executed"] is False
    assert prior["ue_029_source_static_validator_ready"] is True
    assert report["matrix_summary"]["runtime_ack_leaks_now"] == 0
    assert report["matrix_summary"]["live_transport_evidence_rows"] == 0


def test_claim_boundary_forbids_runtime_planner_controller_and_ui_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    for phrase in [
        "does not open Unreal Editor",
        "does not run Unreal build",
        "not live runtime ack",
        "does not prove live UE runtime ack",
        "planner_ready",
        "controller performance",
        "mission success",
        "closed_loop",
    ]:
        assert phrase in boundary
