from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_echo_receiver_capture_bundle_wiring.py"

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
    output_json = tmp_path / "runtime_echo_receiver_capture_bundle_wiring.json"
    output_md = tmp_path / "runtime_echo_receiver_capture_bundle_wiring.md"
    output_matrix = tmp_path / "runtime_echo_receiver_capture_bundle_wiring_matrix.json"
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


def test_wiring_checker_is_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static wiring/checker"
    assert report["source_static_wiring_ready"] is True
    assert report["runtime_probe_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_032"] is False
    assert report["socket_listener_timer_or_background_loop_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert report["runtime_ack_leaks_now"] == 0
    assert report["live_transport_evidence_rows"] == 0


def test_all_seven_capture_artifacts_have_wiring_rows(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    artifacts = {row["artifact"] for row in report["wiring_matrix"]}
    assert artifacts == EXPECTED_ARTIFACTS
    assert report["matrix_summary"]["capture_artifact_rows"] == 7
    assert all(row["required_for_future_bundle"] is True for row in report["wiring_matrix"])
    assert all(row["accepted_as_runtime_ack_now"] is False for row in report["wiring_matrix"])


def test_authoritative_echo_capture_is_the_only_direct_receiver_input(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    direct_rows = [row for row in report["wiring_matrix"] if row["direct_receiver_input"]]
    assert len(direct_rows) == 1
    assert direct_rows[0]["artifact"] == "authoritative_echo_capture.json"
    assert "Validate/Ingest receiver methods" in direct_rows[0]["receiver_surface_role"]
    chain = report["source_static_handoff_chain"]
    assert "UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.ValidateAuthoritativeRuntimeCommandEchoDownlinkJson" in chain
    assert "UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.IngestAuthoritativeRuntimeCommandEchoDownlinkJson" in chain
    assert "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson" in chain


def test_pending_request_is_precondition_not_receiver_input(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    pending_row = next(row for row in report["wiring_matrix"] if row["artifact"] == "pending_request_capture.json")
    assert pending_row["direct_receiver_input"] is False
    assert "precondition only" in pending_row["receiver_surface_role"]
    pending = report["pending_request_precondition"]
    assert pending["schema"] == "mosim.ue_command.v1"
    assert pending["receiver_surface_must_not_synthesize_pending"] is True
    assert "RecordPendingCommandFromPacketJson" in pending["state_anchor"]
    surface = report["receiver_surface_anchor"]
    assert surface["parses_pending_command_request_schema"] is False


def test_receiver_surface_has_no_runtime_transport_or_pose_shortcuts(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    surface = report["receiver_surface_anchor"]
    assert surface["calls_authoritative_validate"] is True
    assert surface["calls_authoritative_apply"] is True
    assert surface["tick_disabled"] is True
    assert surface["runtime_transport_patterns_present"] == []
    assert surface["forbidden_pose_patterns_present"] == []
    assert surface["parses_quadrotor_unreal_state"] is False


def test_false_ack_matrix_rejects_static_build_sender_and_frame_rows(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    false_sources = {row["source"] for row in report["false_ack_negative_matrix"]}
    for source in [
        "031_compile_pass",
        "032_capture_bundle_wiring_checker",
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
        assert source in false_sources
    assert all(row["accepted_as_runtime_ack_now"] is False for row in report["false_ack_negative_matrix"])
    assert all(row["eligible_for_future_authoritative_echo"] is False for row in report["false_ack_negative_matrix"])


def test_prior_029_030_031_evidence_is_consumed_without_ack_claim(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_evidence_consumed"]
    assert prior["ue_029_status"] == "completed"
    assert prior["ue_029_source_static_validator_ready"] is True
    assert prior["ue_030_status"] == "completed"
    assert prior["ue_030_receiver_does_not_start_transport"] is True
    assert prior["ue_031_status"] == "completed"
    assert prior["ue_031_compile_exit_code"] == 0
    assert prior["ue_031_compiled_receiver_surface_cpp"] is True
    assert report["authoritative_runtime_ack_claimable_now"] is False


def test_claim_boundary_forbids_runtime_ui_planner_controller_and_closed_loop_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    for phrase in [
        "does not open Unreal Editor",
        "does not run Unreal build",
        "not live runtime ack",
        "does not prove live UE runtime ack",
        "final UI acceptance",
        "planner_ready",
        "controller performance",
        "mission success",
        "closed_loop",
    ]:
        assert phrase in boundary
