from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_probe_capture_bundle_validator.py"

EXPECTED_ARTIFACTS = [
    "runtime_probe_manifest.json",
    "pending_request_capture.json",
    "authoritative_echo_capture.json",
    "request_echo_match_report.json",
    "no_pose_overwrite_report.json",
    "false_ack_negative_report.json",
    "timeout_cleanup_manifest.json",
]

FALSE_ACK_SOURCES = {
    "024_source_static_handoff",
    "025_compile_pass",
    "026_checker_success",
    "027_runtime_readiness_checker",
    "028_harness_prep_checker",
    "029_capture_bundle_validator",
    "UnrealBuildTool_success",
    "build_success",
    "checker_success",
    "cli_build_success",
    "compile_pass_warning_only",
    "fixture_only_echo",
    "operator_intent",
    "pytest_success",
    "quadrotor.unreal_state.frame",
    "quadrotor.unreal_state.v1",
    "sender_result_bSent",
    "static_fixture_row",
    "udp_send_success",
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
}


def valid_bundle() -> dict[str, dict[str, Any]]:
    run_id = "ue029_run"
    request_id = "ue029_req_001"
    seq = 29
    time_s = 12.5
    capture_session_id = "ue029_capture_session"
    transport_capture_id = "ue029_transport_capture"
    command_kind = "controller_select"
    return {
        "runtime_probe_manifest.json": {
            "schema": "mosim.ue_runtime_probe_capture_bundle_manifest.v1",
            "probe_id": "ue029_future_probe",
            "run_id": run_id,
            "request_id": request_id,
            "capture_session_id": capture_session_id,
            "transport_capture_id": transport_capture_id,
            "producer_identity": {
                "producer_surface": "future_single_bounded_live_probe",
                "producer_instance_id": "mworks_live_downlink_instance",
                "source": "MWORKS_live_downlink",
                "ack_authority": "MWORKS",
                "capture_session_id": capture_session_id,
                "transport_capture_id": transport_capture_id,
            },
            "bounded_probe": True,
            "probe_attempt_count": 1,
            "runtime_probe_executed": True,
            "accepted_ui_controls_enabled": False,
            "keyboard_pose_control_enabled": False,
            "direct_actor_transform_enabled": False,
            "cleanup_required": True,
            "expected_artifacts": EXPECTED_ARTIFACTS,
        },
        "pending_request_capture.json": {
            "schema": "mosim.ue_command.v1",
            "type": "command",
            "run_id": run_id,
            "request_id": request_id,
            "seq": seq,
            "time_s": time_s,
            "requested_by": "ue_experiment_console",
            "capture_session_id": capture_session_id,
            "transport_capture_id": transport_capture_id,
            "command": {
                "kind": command_kind,
                "payload": {"controller_id": "pid"},
            },
            "guard": {
                "require_mworks_ack": True,
                "require_ros2_ack": False,
                "reject_if_gate_open": [],
            },
        },
        "authoritative_echo_capture.json": {
            "schema": "mosim.ue_command_echo.v1",
            "source": "MWORKS_live_downlink",
            "ack_authority": "MWORKS",
            "run_id": run_id,
            "request_id": request_id,
            "seq": seq,
            "time_s": time_s,
            "status": "accepted",
            "capture_session_id": capture_session_id,
            "transport_capture_id": transport_capture_id,
            "command": {"kind": command_kind},
            "no_pose_overwrite_status": "pass",
        },
        "request_echo_match_report.json": {
            "schema": "mosim.ue_command_echo_match_report.v1",
            "match_status": "pass",
            "run_id_match": True,
            "request_id_match": True,
            "seq_match": True,
            "time_s_match": True,
            "command_kind_match": True,
            "status_match": True,
            "echo_status": "accepted",
        },
        "no_pose_overwrite_report.json": {
            "schema": "mosim.ue_no_pose_overwrite_report.v1",
            "no_pose_overwrite_status": "pass",
            "forbidden_pose_command_seen": False,
            "direct_actor_transform_seen": False,
            "keyboard_pose_control_seen": False,
            "pose_override_seen": False,
            "set_uav_pose_seen": False,
            "actor_teleport_seen": False,
            "command_kind_allowed": True,
            "forbidden_shortcuts": [],
        },
        "false_ack_negative_report.json": {
            "schema": "mosim.ue_false_ack_negative_report.v1",
            "false_ack_negative_status": "pass",
            "checked_sources": sorted(FALSE_ACK_SOURCES),
            "build_success_rejected": True,
            "checker_success_rejected": True,
            "pytest_success_rejected": True,
            "sender_success_rejected": True,
            "fixture_only_echo_rejected": True,
            "operator_intent_rejected": True,
            "frame_only_rejected": True,
            "static_rows_rejected": True,
            "false_ack_rows_accepted_as_runtime_ack": 0,
            "accepted_runtime_ack_from_false_sources": False,
            "actual_runtime_ack_claimed_from_static_sources": False,
        },
        "timeout_cleanup_manifest.json": {
            "schema": "mosim.ue_runtime_probe_timeout_cleanup_manifest.v1",
            "timeout_seconds": 60,
            "probe_attempt_count": 1,
            "cleanup_status": "pass",
            "cleanup_completed": True,
            "runtime_windows_state_recorded": True,
            "listener_left_running": False,
            "timer_left_running": False,
            "background_loop_left_running": False,
            "socket_left_bound": False,
            "accepted_ui_controls_enabled": False,
            "capture_session_id": capture_session_id,
            "transport_capture_id": transport_capture_id,
        },
    }


def write_bundle(bundle_dir: Path, bundle: dict[str, dict[str, Any]]) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for name, data in bundle.items():
        (bundle_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_checker(tmp_path: Path, bundle_dir: Path | None = None, expect_ok: bool = True) -> dict[str, Any]:
    output = tmp_path / "runtime_probe_capture_bundle_validator.json"
    cmd = [sys.executable, str(CHECKER), "--output-json", str(output)]
    if bundle_dir:
        cmd.extend(["--bundle-dir", str(bundle_dir)])
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if expect_ok:
        assert completed.returncode == 0, completed.stdout + completed.stderr
    else:
        assert completed.returncode != 0, completed.stdout + completed.stderr
    return json.loads(output.read_text(encoding="utf-8"))


def test_validator_contract_is_source_static_and_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["schema"] == "mosim.ue_runtime_probe_capture_bundle_validator.v1"
    assert report["scope_classification"] == "source-static/capture-bundle-validator"
    assert report["bundle_validation_performed"] is False
    assert report["runtime_probe_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_029"] is False
    assert report["socket_listener_timer_or_background_loop_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert set(report["validator_contract"]["expected_artifacts"]) == set(EXPECTED_ARTIFACTS)
    assert report["quality_boundary"]["static_build_sender_fixture_operator_or_frame_rows_are_ack"] is False
    assert all(value is False for value in report["forbidden_runtime_claims"].values())


def test_valid_future_capture_bundle_passes_but_is_not_runtime_ack_now(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, valid_bundle())
    report = run_checker(tmp_path, bundle_dir=bundle_dir)
    validation = report["bundle_validation"]
    assert validation["ok"] is True
    assert validation["status"] == "valid_future_live_capture_contract_bundle"
    assert validation["capture_claims"]["bundle_can_support_future_live_probe_acceptance"] is True
    assert validation["capture_claims"]["future_live_accepted_state_if_authorized_and_actual_runtime"] is True
    assert validation["capture_claims"]["accepted_as_runtime_ack_now"] is False
    assert validation["capture_claims"]["authoritative_runtime_ack_claimable_now"] is False
    assert validation["capture_claims"]["runtime_probe_executed_by_029"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False


def test_valid_rejected_echo_bundle_passes_without_accepted_state_claim(tmp_path: Path) -> None:
    bundle = copy.deepcopy(valid_bundle())
    bundle["authoritative_echo_capture.json"]["status"] = "rejected"
    bundle["request_echo_match_report.json"]["echo_status"] = "rejected"
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, bundle)
    report = run_checker(tmp_path, bundle_dir=bundle_dir)
    validation = report["bundle_validation"]
    assert validation["ok"] is True
    assert validation["capture_claims"]["future_live_accepted_state_if_authorized_and_actual_runtime"] is False
    assert validation["capture_claims"]["future_live_rejected_state_if_authorized_and_actual_runtime"] is True
    assert validation["capture_claims"]["accepted_as_runtime_ack_now"] is False


def test_missing_required_artifact_fails(tmp_path: Path) -> None:
    bundle = copy.deepcopy(valid_bundle())
    bundle.pop("timeout_cleanup_manifest.json")
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, bundle)
    report = run_checker(tmp_path, bundle_dir=bundle_dir, expect_ok=False)
    assert report["ok"] is False
    assert "missing artifact: timeout_cleanup_manifest.json" in "\n".join(report["issues"])


def test_identity_mismatch_fails(tmp_path: Path) -> None:
    bundle = copy.deepcopy(valid_bundle())
    bundle["authoritative_echo_capture.json"]["request_id"] = "different_request"
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, bundle)
    report = run_checker(tmp_path, bundle_dir=bundle_dir, expect_ok=False)
    issues = "\n".join(report["issues"])
    assert "identity mismatch" in issues
    assert "request_id" in issues


def test_false_ack_source_fails(tmp_path: Path) -> None:
    bundle = copy.deepcopy(valid_bundle())
    bundle["runtime_probe_manifest.json"]["producer_identity"]["source"] = "build_success"
    bundle["runtime_probe_manifest.json"]["producer_identity"]["ack_authority"] = "MWORKS"
    bundle["authoritative_echo_capture.json"]["source"] = "build_success"
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, bundle)
    report = run_checker(tmp_path, bundle_dir=bundle_dir, expect_ok=False)
    issues = "\n".join(report["issues"])
    assert "forbidden false-ack source" in issues
    assert "not authoritative live source" in issues


def test_no_pose_overwrite_failure_fails(tmp_path: Path) -> None:
    bundle = copy.deepcopy(valid_bundle())
    bundle["authoritative_echo_capture.json"]["no_pose_overwrite_status"] = "fail"
    bundle["no_pose_overwrite_report.json"]["no_pose_overwrite_status"] = "fail"
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, bundle)
    report = run_checker(tmp_path, bundle_dir=bundle_dir, expect_ok=False)
    issues = "\n".join(report["issues"])
    assert "no_pose_overwrite_status must be pass" in issues


def test_cleanup_failure_fails(tmp_path: Path) -> None:
    bundle = copy.deepcopy(valid_bundle())
    bundle["timeout_cleanup_manifest.json"]["socket_left_bound"] = True
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, bundle)
    report = run_checker(tmp_path, bundle_dir=bundle_dir, expect_ok=False)
    assert "socket_left_bound must be false" in "\n".join(report["issues"])


def test_false_ack_negative_report_must_cover_static_build_sender_frame_rows(tmp_path: Path) -> None:
    bundle = copy.deepcopy(valid_bundle())
    bundle["false_ack_negative_report.json"]["checked_sources"] = ["build_success"]
    bundle_dir = tmp_path / "bundle"
    write_bundle(bundle_dir, bundle)
    report = run_checker(tmp_path, bundle_dir=bundle_dir, expect_ok=False)
    issues = "\n".join(report["issues"])
    assert "checked_sources missing" in issues
    assert "quadrotor.unreal_state.v1" in issues
    assert "sender_result_bSent" in issues
