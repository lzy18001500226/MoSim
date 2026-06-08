from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_echo_receiver_single_bounded_probe_plan.py"

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
    output_json = tmp_path / "runtime_echo_receiver_single_bounded_probe_plan.json"
    output_md = tmp_path / "runtime_echo_receiver_single_bounded_probe_plan.md"
    output_matrix = tmp_path / "runtime_echo_receiver_single_bounded_probe_plan_matrix.json"
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


def test_probe_plan_is_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static single-bounded-probe plan/readiness"
    assert report["source_static_plan_ready"] is True
    assert report["runtime_probe_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_033"] is False
    assert report["socket_listener_timer_thread_or_background_loop_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert report["runtime_ack_leaks_now"] == 0
    assert report["live_transport_evidence_rows"] == 0


def test_future_probe_is_single_attempt_with_bounded_timeout(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    plan = report["single_bounded_probe_plan"]
    assert plan["future_pmo_runtime_authorization_required"] is True
    assert plan["future_probe_attempt_count"] == 1
    assert plan["future_probe_retry_budget"] == 0
    assert plan["future_probe_must_stop_after_first_attempt"] is True
    timeout = plan["timeout_seconds_range"]
    assert timeout["exclusive_min"] == 0
    assert timeout["inclusive_max"] <= 60
    assert timeout["recommended_default"] <= 60
    assert plan["timeout_cleanup_required"] is True


def test_all_seven_capture_artifacts_are_preconditions(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["capture_bundle_precondition_matrix"]
    artifacts = {row["artifact"] for row in rows}
    assert artifacts == EXPECTED_ARTIFACTS
    assert report["matrix_summary"]["capture_bundle_precondition_rows"] == 7
    assert all(row["current_runtime_evidence"] is False for row in rows)
    assert all(row["accepted_as_runtime_ack_now"] is False for row in rows)
    assert set(report["single_bounded_probe_plan"]["seven_capture_bundle_artifacts"]) == EXPECTED_ARTIFACTS


def test_authoritative_echo_is_only_direct_receiver_input(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["capture_bundle_precondition_matrix"]
    direct_rows = [row for row in rows if row["direct_receiver_input"]]
    assert len(direct_rows) == 1
    assert direct_rows[0]["artifact"] == "authoritative_echo_capture.json"
    plan = report["single_bounded_probe_plan"]["authoritative_echo_capture"]
    assert plan["schema"] == "mosim.ue_command_echo.v1"
    assert plan["direct_receiver_input"] == "authoritative_echo_capture.json"
    assert "ValidateAuthoritativeRuntimeCommandEchoDownlinkJson" in plan["receiver_surface_validate_method"]
    assert "IngestAuthoritativeRuntimeCommandEchoDownlinkJson" in plan["receiver_surface_ingest_method"]


def test_pending_request_is_precondition_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    plan = report["single_bounded_probe_plan"]["pending_request_capture"]
    assert plan["schema"] == "mosim.ue_command.v1"
    assert plan["source"] == "UE command request path only"
    assert plan["must_exist_before_echo"] is True
    assert plan["receiver_surface_must_not_synthesize_pending"] is True
    surface = report["receiver_surface_source_scan"]
    assert surface["parses_pending_command_request_schema"] is False


def test_false_ack_rules_reject_static_build_sender_fixture_and_frame_sources(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    sources = {row["source"] for row in report["false_ack_negative_rules"]}
    for source in [
        "031_compile_pass",
        "032_capture_bundle_wiring_checker",
        "033_single_bounded_probe_plan_checker",
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
        assert source in sources
    assert all(row["future_probe_expected_result"] == "reject_as_runtime_ack" for row in report["false_ack_negative_rules"])
    assert all(row["accepted_as_runtime_ack_now"] is False for row in report["false_ack_negative_rules"])


def test_no_pose_overwrite_checks_cover_direct_actor_and_keyboard_shortcuts(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    checks = {row["check"] for row in report["no_pose_overwrite_checks"]}
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
    assert all(row["required_result"] == "absent_or_false" for row in report["no_pose_overwrite_checks"])
    surface = report["receiver_surface_source_scan"]
    assert surface["runtime_transport_patterns_present"] == []
    assert surface["forbidden_pose_patterns_present"] == []


def test_prior_032_wiring_is_consumed_without_ack_claim(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    consumed = report["source_static_evidence_consumed"]
    assert consumed["ue_029_return_status"] == "completed"
    assert consumed["ue_030_return_status"] == "completed"
    assert consumed["ue_031_return_status"] == "completed"
    assert consumed["ue_031_compile_exit_code"] == 0
    assert consumed["ue_032_return_status"] == "completed"
    assert consumed["ue_032_source_static_wiring_ready"] is True
    assert consumed["ue_032_runtime_ack_leaks_now"] == 0
    assert consumed["ue_032_live_transport_evidence_rows"] == 0
    assert report["authoritative_runtime_ack_claimable_now"] is False


def test_claim_boundary_requires_future_runtime_authorization_and_forbids_success_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    for phrase in [
        "source-static plan/readiness contract",
        "does not open Unreal Editor",
        "does not run Unreal build",
        "not live runtime ack",
        "separate PMO task packet",
        "does not prove live UE runtime ack",
        "final UI acceptance",
        "planner_ready",
        "controller performance",
        "mission success",
        "closed_loop",
    ]:
        assert phrase in boundary
