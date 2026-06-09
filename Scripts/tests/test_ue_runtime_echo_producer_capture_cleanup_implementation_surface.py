from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_echo_producer_capture_cleanup_implementation_surface.py"

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
    output_json = tmp_path / "runtime_echo_producer_capture_cleanup_implementation_surface.json"
    output_md = tmp_path / "runtime_echo_producer_capture_cleanup_implementation_surface.md"
    output_matrix = tmp_path / "runtime_echo_producer_capture_cleanup_implementation_surface_matrix.json"
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


def test_implementation_surface_is_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static producer/capture/cleanup implementation surface"
    assert report["source_static_implementation_surface_ready"] is True
    assert report["runtime_route_ready_now"] is False
    assert report["live_attempt_consumed"] is False
    assert report["runtime_probe_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_036"] is False
    assert report["socket_listener_timer_thread_or_background_loop_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert report["live_transport_evidence_rows"] == 0
    assert report["runtime_ack_leaks_now"] == 0


def test_surface_rows_cover_exactly_seven_artifacts(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["implementation_surface_rows"]
    assert {row["artifact"] for row in rows} == EXPECTED_ARTIFACTS
    assert report["matrix_summary"]["implementation_surface_rows"] == 7
    assert report["matrix_summary"]["implemented_artifact_rows"] == 7
    assert all(row["method_declared_in_header"] is True for row in rows)
    assert all(row["method_defined_in_source"] is True for row in rows)
    assert all(row["artifact_literal_present"] is True for row in rows)
    assert all(row["schema_literal_present"] is True for row in rows)
    assert all(row["accepted_as_runtime_ack_now"] is False for row in rows)
    assert all(row["current_runtime_ready"] is False for row in rows)


def test_pending_and_echo_capture_surfaces_are_separated(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    surface = report["producer_capture_cleanup_surface"]
    assert surface["pending_request_capture_surface"]["method"] == "BuildPendingRequestCaptureJson"
    assert surface["pending_request_capture_surface"]["artifact"] == "pending_request_capture.json"
    assert surface["pending_request_capture_surface"]["must_exist_before_echo"] is True
    assert surface["pending_request_capture_surface"]["accepted_as_runtime_ack_now"] is False
    assert surface["authoritative_echo_capture_surface"]["method"] == "BuildAuthoritativeEchoCaptureJson"
    assert surface["authoritative_echo_capture_surface"]["artifact"] == "authoritative_echo_capture.json"
    assert surface["authoritative_echo_capture_surface"]["direct_receiver_input"] is True
    assert surface["authoritative_echo_capture_surface"]["accepted_as_runtime_ack_now"] is False


def test_authoritative_pairs_are_preserved(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["producer_capture_cleanup_surface"]["authoritative_source_authority_pairs"] == {
        "MWORKS_live_downlink": "MWORKS",
        "ROS2_runtime_echo": "ROS2",
        "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
    }


def test_timeout_cleanup_contract_is_bounded(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    cleanup = report["producer_capture_cleanup_surface"]["timeout_cleanup_surface"]
    assert cleanup["method"] == "BuildTimeoutCleanupManifestJson"
    assert cleanup["timeout_seconds_inclusive_max"] == 60
    assert cleanup["probe_attempt_count"] == 1
    assert cleanup["retry_count"] == 0
    assert cleanup["accepted_as_runtime_ack_now"] is False


def test_034_035_boundaries_are_consumed_without_live_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_evidence_consumed"]
    assert prior["ue_034_status"] == "blocked"
    assert prior["ue_034_live_attempt_consumed"] is False
    assert prior["ue_034_runtime_probe_executed"] is False
    assert prior["ue_035_ok"] is True
    assert prior["ue_035_source_static_route_contract_ready"] is True
    assert prior["ue_035_runtime_route_ready_now"] is False
    assert prior["ue_035_runtime_ack_leaks_now"] == 0


def test_false_ack_sources_are_rejected(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = report["false_ack_rejection_boundary"]
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
        assert source in boundary["checked_sources"]
    assert boundary["accepted_runtime_ack_from_false_sources"] is False
    assert boundary["actual_runtime_ack_claimed_from_static_sources"] is False


def test_no_pose_overwrite_markers_are_guarded(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = report["no_pose_overwrite_boundary"]
    for marker in [
        "pose_override",
        "set_uav_pose",
        "actor_transform",
        "keyboard_pose",
        "direct_actor_transform",
        "actor_teleport",
        "SetActorLocation",
        "SetActorTransform",
        "TeleportTo",
        "UE_truth_shortcut",
    ]:
        assert marker in boundary["checked_markers"]
    assert boundary["forbidden_pose_command_seen"] is False
    assert boundary["direct_actor_transform_seen"] is False
    assert boundary["keyboard_pose_control_seen"] is False
    assert boundary["pose_override_seen"] is False
    assert boundary["set_uav_pose_seen"] is False
    assert boundary["actor_teleport_seen"] is False
    assert boundary["ue_truth_shortcut_seen"] is False


def test_claim_boundary_forbids_runtime_success_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    for phrase in [
        "source/static implementation-surface",
        "does not open Unreal Editor",
        "does not run Unreal build",
        "does not edit Blueprint",
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


def test_future_live_preconditions_require_real_routes(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    preconditions = "\n".join(report["future_live_probe_preconditions"])
    for phrase in [
        "PMO explicitly authorizes",
        "producer instance supplies",
        "captures a mosim.ue_command.v1 pending request",
        "captures a mosim.ue_command_echo.v1 row",
        "matching run_id/request_id/seq/time_s/command kind/status",
        "reject pose shortcuts",
        "timeout <= 60 seconds",
    ]:
        assert phrase in preconditions
