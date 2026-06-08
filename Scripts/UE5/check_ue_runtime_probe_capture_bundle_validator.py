#!/usr/bin/env python3
"""Validate the future UE command-echo runtime-probe capture bundle.

This is a source-static checker for UE 029. It does not open Unreal Editor,
run UE runtime/build, bind sockets, start listeners/timers/background loops, or
claim live command acknowledgement. It defines and tests the capture-bundle
contract that a later PMO-authorized single bounded runtime probe must satisfy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-PROBE-CAPTURE-BUNDLE-VALIDATOR-20260608-029"

COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
MANIFEST_SCHEMA_ID = "mosim.ue_runtime_probe_capture_bundle_manifest.v1"
MATCH_REPORT_SCHEMA_ID = "mosim.ue_command_echo_match_report.v1"
NO_POSE_REPORT_SCHEMA_ID = "mosim.ue_no_pose_overwrite_report.v1"
FALSE_ACK_REPORT_SCHEMA_ID = "mosim.ue_false_ack_negative_report.v1"
CLEANUP_MANIFEST_SCHEMA_ID = "mosim.ue_runtime_probe_timeout_cleanup_manifest.v1"

EXPECTED_ARTIFACTS = [
    "runtime_probe_manifest.json",
    "pending_request_capture.json",
    "authoritative_echo_capture.json",
    "request_echo_match_report.json",
    "no_pose_overwrite_report.json",
    "false_ack_negative_report.json",
    "timeout_cleanup_manifest.json",
]

AUTHORITATIVE_LIVE_SOURCES = {
    "MWORKS_live_downlink": "MWORKS",
    "ROS2_runtime_echo": "ROS2",
    "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
}
NON_LIVE_SOURCES = {
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
}
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
}
FORBIDDEN_COMMAND_KINDS = {
    "pose_override",
    "teleport",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
}
ALLOWED_COMMAND_KINDS = {
    "controller_select",
    "planner_select",
    "wind_profile",
    "motor_fault",
    "sensor_mode",
    "scenario_reset",
    "start_goal_update",
    "recording",
    "scene_switch",
}


def repo(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"missing artifact: {path.name}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"invalid json in {path.name}: {exc.msg}"]
    if not isinstance(data, dict):
        return {}, [f"artifact must be a JSON object: {path.name}"]
    return data, []


def has_value(value: Any) -> bool:
    return value is not None and value != ""


def dotted(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def command_kind(data: dict[str, Any]) -> Any:
    return data.get("command_kind") or dotted(data, "command.kind")


def require_fields(data: dict[str, Any], fields: list[str], issues: list[str], prefix: str) -> None:
    for field in fields:
        if not has_value(dotted(data, field)):
            issues.append(f"{prefix} missing required field: {field}")


def validate_manifest(manifest: dict[str, Any], artifact_names: set[str]) -> list[str]:
    issues: list[str] = []
    require_fields(
        manifest,
        [
            "schema",
            "probe_id",
            "run_id",
            "request_id",
            "capture_session_id",
            "transport_capture_id",
            "producer_identity.producer_surface",
            "producer_identity.producer_instance_id",
            "producer_identity.source",
            "producer_identity.ack_authority",
            "producer_identity.capture_session_id",
            "producer_identity.transport_capture_id",
        ],
        issues,
        "runtime_probe_manifest",
    )
    if manifest.get("schema") != MANIFEST_SCHEMA_ID:
        issues.append("runtime_probe_manifest schema must be mosim.ue_runtime_probe_capture_bundle_manifest.v1")
    producer = manifest.get("producer_identity", {})
    source = producer.get("source")
    authority = producer.get("ack_authority")
    if source not in AUTHORITATIVE_LIVE_SOURCES:
        issues.append(f"runtime_probe_manifest producer source is not authoritative live source: {source!r}")
    if AUTHORITATIVE_LIVE_SOURCES.get(source) != authority:
        issues.append(f"runtime_probe_manifest source/ack_authority mismatch: {source!r}/{authority!r}")
    if source in NON_LIVE_SOURCES or source in FALSE_ACK_SOURCES or str(source).startswith("quadrotor.unreal_state"):
        issues.append(f"runtime_probe_manifest producer source is forbidden false-ack source: {source!r}")
    if producer.get("capture_session_id") != manifest.get("capture_session_id"):
        issues.append("runtime_probe_manifest producer capture_session_id must match manifest")
    if producer.get("transport_capture_id") != manifest.get("transport_capture_id"):
        issues.append("runtime_probe_manifest producer transport_capture_id must match manifest")
    if manifest.get("bounded_probe") is not True:
        issues.append("runtime_probe_manifest bounded_probe must be true")
    if manifest.get("probe_attempt_count") != 1:
        issues.append("runtime_probe_manifest probe_attempt_count must be 1")
    if manifest.get("runtime_probe_executed") is not True:
        issues.append("runtime_probe_manifest runtime_probe_executed must be true for a future capture bundle")
    if manifest.get("accepted_ui_controls_enabled") is not False:
        issues.append("runtime_probe_manifest accepted_ui_controls_enabled must be false")
    if manifest.get("keyboard_pose_control_enabled") is not False:
        issues.append("runtime_probe_manifest keyboard_pose_control_enabled must be false")
    if manifest.get("direct_actor_transform_enabled") is not False:
        issues.append("runtime_probe_manifest direct_actor_transform_enabled must be false")
    if manifest.get("cleanup_required") is not True:
        issues.append("runtime_probe_manifest cleanup_required must be true")
    expected = set(manifest.get("expected_artifacts", []))
    if set(EXPECTED_ARTIFACTS) - expected:
        missing = sorted(set(EXPECTED_ARTIFACTS) - expected)
        issues.append("runtime_probe_manifest expected_artifacts missing: " + ", ".join(missing))
    if set(EXPECTED_ARTIFACTS) - artifact_names:
        missing = sorted(set(EXPECTED_ARTIFACTS) - artifact_names)
        issues.append("capture bundle directory missing artifact(s): " + ", ".join(missing))
    return issues


def validate_pending_request(pending: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    require_fields(
        pending,
        [
            "schema",
            "type",
            "run_id",
            "request_id",
            "seq",
            "time_s",
            "requested_by",
            "command.kind",
            "command.payload",
            "guard.require_mworks_ack",
            "guard.require_ros2_ack",
            "guard.reject_if_gate_open",
        ],
        issues,
        "pending_request_capture",
    )
    if pending.get("schema") != COMMAND_SCHEMA_ID:
        issues.append("pending_request_capture schema must be mosim.ue_command.v1")
    if pending.get("type") != "command":
        issues.append("pending_request_capture type must be command")
    if pending.get("requested_by") != "ue_experiment_console":
        issues.append("pending_request_capture requested_by must be ue_experiment_console")
    kind = command_kind(pending)
    if kind not in ALLOWED_COMMAND_KINDS:
        issues.append(f"pending_request_capture command.kind is not allowed: {kind!r}")
    if kind in FORBIDDEN_COMMAND_KINDS:
        issues.append(f"pending_request_capture forbidden pose command kind: {kind!r}")
    guard = pending.get("guard", {})
    if guard.get("require_mworks_ack") is not True:
        issues.append("pending_request_capture guard.require_mworks_ack must be true")
    if not isinstance(guard.get("require_ros2_ack"), bool):
        issues.append("pending_request_capture guard.require_ros2_ack must be boolean")
    if not isinstance(guard.get("reject_if_gate_open"), list):
        issues.append("pending_request_capture guard.reject_if_gate_open must be a list")
    return issues


def validate_echo(echo: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    require_fields(
        echo,
        [
            "schema",
            "source",
            "ack_authority",
            "run_id",
            "request_id",
            "seq",
            "time_s",
            "status",
            "no_pose_overwrite_status",
        ],
        issues,
        "authoritative_echo_capture",
    )
    if not has_value(command_kind(echo)):
        issues.append("authoritative_echo_capture missing required field: command.kind or command_kind")
    source = echo.get("source")
    authority = echo.get("ack_authority")
    if echo.get("schema") != ECHO_SCHEMA_ID:
        issues.append("authoritative_echo_capture schema must be mosim.ue_command_echo.v1")
    if source not in AUTHORITATIVE_LIVE_SOURCES:
        issues.append(f"authoritative_echo_capture source is not authoritative live source: {source!r}")
    if AUTHORITATIVE_LIVE_SOURCES.get(source) != authority:
        issues.append(f"authoritative_echo_capture source/ack_authority mismatch: {source!r}/{authority!r}")
    if source in NON_LIVE_SOURCES or source in FALSE_ACK_SOURCES or str(source).startswith("quadrotor.unreal_state"):
        issues.append(f"authoritative_echo_capture source is forbidden false-ack source: {source!r}")
    if echo.get("status") not in {"accepted", "rejected"}:
        issues.append("authoritative_echo_capture status must be accepted or rejected")
    if echo.get("no_pose_overwrite_status") != "pass":
        issues.append("authoritative_echo_capture no_pose_overwrite_status must be pass")
    if command_kind(echo) in FORBIDDEN_COMMAND_KINDS:
        issues.append(f"authoritative_echo_capture forbidden pose command kind: {command_kind(echo)!r}")
    return issues


def validate_match_report(
    match: dict[str, Any],
    pending: dict[str, Any],
    echo: dict[str, Any],
) -> list[str]:
    issues: list[str] = []
    require_fields(
        match,
        [
            "schema",
            "match_status",
            "run_id_match",
            "request_id_match",
            "seq_match",
            "time_s_match",
            "command_kind_match",
            "status_match",
        ],
        issues,
        "request_echo_match_report",
    )
    if match.get("schema") != MATCH_REPORT_SCHEMA_ID:
        issues.append("request_echo_match_report schema must be mosim.ue_command_echo_match_report.v1")
    if match.get("match_status") != "pass":
        issues.append("request_echo_match_report match_status must be pass")
    for field in [
        "run_id_match",
        "request_id_match",
        "seq_match",
        "time_s_match",
        "command_kind_match",
        "status_match",
    ]:
        if match.get(field) is not True:
            issues.append(f"request_echo_match_report {field} must be true")
    comparisons = [
        ("run_id", pending.get("run_id"), echo.get("run_id")),
        ("request_id", pending.get("request_id"), echo.get("request_id")),
        ("seq", pending.get("seq"), echo.get("seq")),
        ("time_s", pending.get("time_s"), echo.get("time_s")),
        ("command_kind", command_kind(pending), command_kind(echo)),
    ]
    for name, left, right in comparisons:
        if left != right:
            issues.append(f"request_echo_match_report identity mismatch: {name} pending={left!r} echo={right!r}")
    if match.get("echo_status") not in {"accepted", "rejected", echo.get("status")}:
        issues.append("request_echo_match_report echo_status must be accepted or rejected when present")
    if has_value(match.get("echo_status")) and match.get("echo_status") != echo.get("status"):
        issues.append("request_echo_match_report echo_status must match authoritative echo status")
    return issues


def validate_no_pose_report(report: dict[str, Any], pending: dict[str, Any], echo: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    require_fields(report, ["schema", "no_pose_overwrite_status"], issues, "no_pose_overwrite_report")
    if report.get("schema") != NO_POSE_REPORT_SCHEMA_ID:
        issues.append("no_pose_overwrite_report schema must be mosim.ue_no_pose_overwrite_report.v1")
    if report.get("no_pose_overwrite_status") != "pass":
        issues.append("no_pose_overwrite_report no_pose_overwrite_status must be pass")
    for field in [
        "forbidden_pose_command_seen",
        "direct_actor_transform_seen",
        "keyboard_pose_control_seen",
        "pose_override_seen",
        "set_uav_pose_seen",
        "actor_teleport_seen",
    ]:
        if report.get(field) is not False:
            issues.append(f"no_pose_overwrite_report {field} must be false")
    if report.get("command_kind_allowed") is not True:
        issues.append("no_pose_overwrite_report command_kind_allowed must be true")
    if command_kind(pending) in FORBIDDEN_COMMAND_KINDS or command_kind(echo) in FORBIDDEN_COMMAND_KINDS:
        issues.append("no_pose_overwrite_report cannot pass for forbidden pose command kind")
    if echo.get("no_pose_overwrite_status") != "pass":
        issues.append("no_pose_overwrite_report cannot pass when echo no_pose_overwrite_status is not pass")
    forbidden_shortcuts = report.get("forbidden_shortcuts", [])
    if not isinstance(forbidden_shortcuts, list) or forbidden_shortcuts:
        issues.append("no_pose_overwrite_report forbidden_shortcuts must be an empty list")
    return issues


def validate_false_ack_report(report: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    require_fields(report, ["schema", "false_ack_negative_status"], issues, "false_ack_negative_report")
    if report.get("schema") != FALSE_ACK_REPORT_SCHEMA_ID:
        issues.append("false_ack_negative_report schema must be mosim.ue_false_ack_negative_report.v1")
    if report.get("false_ack_negative_status") != "pass":
        issues.append("false_ack_negative_report false_ack_negative_status must be pass")
    checked = set(report.get("checked_sources", []))
    required = FALSE_ACK_SOURCES | NON_LIVE_SOURCES
    if required - checked:
        issues.append("false_ack_negative_report checked_sources missing: " + ", ".join(sorted(required - checked)))
    boolean_guards = [
        "build_success_rejected",
        "checker_success_rejected",
        "pytest_success_rejected",
        "sender_success_rejected",
        "fixture_only_echo_rejected",
        "operator_intent_rejected",
        "frame_only_rejected",
        "static_rows_rejected",
    ]
    for field in boolean_guards:
        if report.get(field) is not True:
            issues.append(f"false_ack_negative_report {field} must be true")
    if report.get("false_ack_rows_accepted_as_runtime_ack") != 0:
        issues.append("false_ack_negative_report false_ack_rows_accepted_as_runtime_ack must be 0")
    if report.get("accepted_runtime_ack_from_false_sources") is not False:
        issues.append("false_ack_negative_report accepted_runtime_ack_from_false_sources must be false")
    if report.get("actual_runtime_ack_claimed_from_static_sources") is not False:
        issues.append("false_ack_negative_report actual_runtime_ack_claimed_from_static_sources must be false")
    return issues


def validate_cleanup_manifest(cleanup: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    require_fields(cleanup, ["schema", "timeout_seconds", "probe_attempt_count", "cleanup_status"], issues, "timeout_cleanup_manifest")
    if cleanup.get("schema") != CLEANUP_MANIFEST_SCHEMA_ID:
        issues.append("timeout_cleanup_manifest schema must be mosim.ue_runtime_probe_timeout_cleanup_manifest.v1")
    timeout = cleanup.get("timeout_seconds")
    if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 60:
        issues.append("timeout_cleanup_manifest timeout_seconds must be in (0, 60]")
    if cleanup.get("probe_attempt_count") != 1:
        issues.append("timeout_cleanup_manifest probe_attempt_count must be 1")
    if cleanup.get("cleanup_status") != "pass":
        issues.append("timeout_cleanup_manifest cleanup_status must be pass")
    for field in [
        "cleanup_completed",
        "runtime_windows_state_recorded",
    ]:
        if cleanup.get(field) is not True:
            issues.append(f"timeout_cleanup_manifest {field} must be true")
    for field in [
        "listener_left_running",
        "timer_left_running",
        "background_loop_left_running",
        "socket_left_bound",
        "accepted_ui_controls_enabled",
    ]:
        if cleanup.get(field) is not False:
            issues.append(f"timeout_cleanup_manifest {field} must be false")
    return issues


def validate_cross_artifact_identity(
    manifest: dict[str, Any],
    pending: dict[str, Any],
    echo: dict[str, Any],
    cleanup: dict[str, Any],
) -> list[str]:
    issues: list[str] = []
    common_fields = ["run_id", "request_id"]
    for field in common_fields:
        values = {
            "manifest": manifest.get(field),
            "pending": pending.get(field),
            "echo": echo.get(field),
        }
        if len(set(values.values())) != 1:
            issues.append(f"cross-artifact identity mismatch for {field}: {values}")
    capture_session_id = manifest.get("capture_session_id")
    transport_capture_id = manifest.get("transport_capture_id")
    for name, data in [("pending_request_capture", pending), ("authoritative_echo_capture", echo), ("timeout_cleanup_manifest", cleanup)]:
        if has_value(data.get("capture_session_id")) and data.get("capture_session_id") != capture_session_id:
            issues.append(f"{name} capture_session_id must match runtime_probe_manifest")
        if has_value(data.get("transport_capture_id")) and data.get("transport_capture_id") != transport_capture_id:
            issues.append(f"{name} transport_capture_id must match runtime_probe_manifest")
    return issues


def validate_bundle(bundle_dir: Path) -> dict[str, Any]:
    artifact_status: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, dict[str, Any]] = {}
    bundle_issues: list[str] = []
    artifact_names = {path.name for path in bundle_dir.glob("*.json")} if bundle_dir.exists() else set()
    if not bundle_dir.exists():
        bundle_issues.append(f"bundle_dir does not exist: {bundle_dir}")
    if not bundle_dir.is_dir():
        bundle_issues.append(f"bundle_dir is not a directory: {bundle_dir}")

    for name in EXPECTED_ARTIFACTS:
        data, issues = load_json(bundle_dir / name)
        artifacts[name] = data
        artifact_status[name] = {
            "present": (bundle_dir / name).exists(),
            "valid_json_object": not issues,
            "issues": issues,
        }
        bundle_issues.extend(issues)

    manifest = artifacts["runtime_probe_manifest.json"]
    pending = artifacts["pending_request_capture.json"]
    echo = artifacts["authoritative_echo_capture.json"]
    match = artifacts["request_echo_match_report.json"]
    no_pose = artifacts["no_pose_overwrite_report.json"]
    false_ack = artifacts["false_ack_negative_report.json"]
    cleanup = artifacts["timeout_cleanup_manifest.json"]

    artifact_validators = {
        "runtime_probe_manifest.json": validate_manifest(manifest, artifact_names),
        "pending_request_capture.json": validate_pending_request(pending),
        "authoritative_echo_capture.json": validate_echo(echo),
        "request_echo_match_report.json": validate_match_report(match, pending, echo),
        "no_pose_overwrite_report.json": validate_no_pose_report(no_pose, pending, echo),
        "false_ack_negative_report.json": validate_false_ack_report(false_ack),
        "timeout_cleanup_manifest.json": validate_cleanup_manifest(cleanup),
    }
    for name, issues in artifact_validators.items():
        artifact_status[name]["issues"].extend(issues)
        bundle_issues.extend(f"{name}: {issue}" for issue in issues)

    cross_issues = validate_cross_artifact_identity(manifest, pending, echo, cleanup)
    bundle_issues.extend(cross_issues)
    echo_status = echo.get("status")
    ok = not bundle_issues
    return {
        "bundle_dir": repo(bundle_dir),
        "ok": ok,
        "status": "valid_future_live_capture_contract_bundle" if ok else "invalid_capture_bundle",
        "artifact_status": artifact_status,
        "cross_artifact_issues": cross_issues,
        "identity_summary": {
            "run_id": manifest.get("run_id") or pending.get("run_id") or echo.get("run_id"),
            "request_id": manifest.get("request_id") or pending.get("request_id") or echo.get("request_id"),
            "seq": pending.get("seq") or echo.get("seq"),
            "time_s": pending.get("time_s") or echo.get("time_s"),
            "command_kind": command_kind(pending) or command_kind(echo),
            "echo_status": echo_status,
        },
        "capture_claims": {
            "bundle_can_support_future_live_probe_acceptance": ok,
            "future_live_accepted_state_if_authorized_and_actual_runtime": ok and echo_status == "accepted",
            "future_live_rejected_state_if_authorized_and_actual_runtime": ok and echo_status == "rejected",
            "accepted_as_runtime_ack_now": False,
            "authoritative_runtime_ack_claimable_now": False,
            "runtime_probe_executed_by_029": False,
        },
        "issues": bundle_issues,
    }


def fixture_matrix_row(row_id: str, expected_valid_bundle: bool, reason: str) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "expected_valid_bundle": expected_valid_bundle,
        "reason": reason,
        "accepted_as_runtime_ack_now": False,
        "authoritative_runtime_ack_claimable_now": False,
    }


def build_fixture_matrix() -> list[dict[str, Any]]:
    rows = [
        fixture_matrix_row("valid_future_accepted_MWORKS_live_downlink", True, "authoritative source, matching identity, no-pose pass, negative report pass, cleanup pass"),
        fixture_matrix_row("valid_future_rejected_MWORKS_live_downlink", True, "authoritative rejected echo is valid echo evidence but not accepted-state evidence"),
        fixture_matrix_row("valid_future_accepted_ROS2_runtime_echo", True, "ROS2 authoritative echo source/authority pair"),
        fixture_matrix_row("valid_future_accepted_MWORKS_ROS2_live_downlink", True, "shared MWORKS_ROS2 authoritative echo source/authority pair"),
        fixture_matrix_row("missing_runtime_probe_manifest", False, "all seven expected JSON artifacts are mandatory"),
        fixture_matrix_row("missing_pending_request_capture", False, "pending can come only from mosim.ue_command.v1 request"),
        fixture_matrix_row("missing_authoritative_echo_capture", False, "accepted/rejected can come only from authoritative mosim.ue_command_echo.v1"),
        fixture_matrix_row("missing_request_echo_match_report", False, "run_id/request_id/seq/time_s/command kind/status match must be reported"),
        fixture_matrix_row("missing_no_pose_overwrite_report", False, "no-pose-overwrite proof is mandatory"),
        fixture_matrix_row("missing_false_ack_negative_report", False, "false-ack negative proof is mandatory"),
        fixture_matrix_row("missing_timeout_cleanup_manifest", False, "bounded timeout and cleanup manifest is mandatory"),
        fixture_matrix_row("missing_producer_identity", False, "producer identity requires source, authority, surface, instance, session, and transport ids"),
        fixture_matrix_row("identity_mismatch_request_id", False, "pending and echo identity must match"),
        fixture_matrix_row("identity_mismatch_seq", False, "pending and echo sequence must match"),
        fixture_matrix_row("identity_mismatch_time_s", False, "pending and echo command timestamp must match"),
        fixture_matrix_row("identity_mismatch_command_kind", False, "pending and echo command kind must match"),
        fixture_matrix_row("wrong_source_authority_pair", False, "source must match the expected authoritative ack authority"),
        fixture_matrix_row("no_pose_overwrite_failure", False, "no_pose_overwrite_status must be pass"),
        fixture_matrix_row("forbidden_pose_command", False, "pose override, teleport, set_uav_pose, actor_transform, and keyboard_pose are forbidden"),
        fixture_matrix_row("false_ack_build_success", False, "build success cannot be runtime command ack"),
        fixture_matrix_row("false_ack_sender_success", False, "sender success cannot be runtime command ack"),
        fixture_matrix_row("false_ack_fixture_only_echo", False, "fixture-only echo cannot be runtime command ack"),
        fixture_matrix_row("false_ack_operator_intent", False, "operator intent cannot be runtime command ack"),
        fixture_matrix_row("false_ack_quadrotor_unreal_state", False, "quadrotor.unreal_state frames are status frames, not command echo"),
        fixture_matrix_row("cleanup_failure_socket_left_bound", False, "cleanup must prove no socket/listener/timer/background loop remains"),
    ]
    return rows


def build_validator_contract() -> dict[str, Any]:
    return {
        "expected_artifacts": EXPECTED_ARTIFACTS,
        "runtime_probe_manifest": {
            "schema": MANIFEST_SCHEMA_ID,
            "required_fields": [
                "probe_id",
                "run_id",
                "request_id",
                "capture_session_id",
                "transport_capture_id",
                "producer_identity.producer_surface",
                "producer_identity.producer_instance_id",
                "producer_identity.source",
                "producer_identity.ack_authority",
                "producer_identity.capture_session_id",
                "producer_identity.transport_capture_id",
                "bounded_probe=true",
                "probe_attempt_count=1",
                "runtime_probe_executed=true",
                "accepted_ui_controls_enabled=false",
                "keyboard_pose_control_enabled=false",
                "direct_actor_transform_enabled=false",
                "cleanup_required=true",
            ],
        },
        "pending_request_capture": {
            "schema": COMMAND_SCHEMA_ID,
            "required_fields": [
                "schema",
                "type",
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "requested_by",
                "command.kind",
                "command.payload",
                "guard.require_mworks_ack",
                "guard.require_ros2_ack",
                "guard.reject_if_gate_open",
            ],
            "source_boundary": "pending can only originate from a mosim.ue_command.v1 UE command request path",
        },
        "authoritative_echo_capture": {
            "schema": ECHO_SCHEMA_ID,
            "authoritative_source_authority_pairs": AUTHORITATIVE_LIVE_SOURCES,
            "required_fields": [
                "schema",
                "source",
                "ack_authority",
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "status",
                "command.kind or command_kind",
                "no_pose_overwrite_status=pass",
            ],
            "status_values": ["accepted", "rejected"],
        },
        "request_echo_match_report": {
            "schema": MATCH_REPORT_SCHEMA_ID,
            "required_pass_fields": [
                "match_status=pass",
                "run_id_match=true",
                "request_id_match=true",
                "seq_match=true",
                "time_s_match=true",
                "command_kind_match=true",
                "status_match=true",
            ],
        },
        "no_pose_overwrite_report": {
            "schema": NO_POSE_REPORT_SCHEMA_ID,
            "required_pass_fields": [
                "no_pose_overwrite_status=pass",
                "forbidden_pose_command_seen=false",
                "direct_actor_transform_seen=false",
                "keyboard_pose_control_seen=false",
                "pose_override_seen=false",
                "set_uav_pose_seen=false",
                "actor_teleport_seen=false",
                "command_kind_allowed=true",
            ],
            "forbidden_command_kinds": sorted(FORBIDDEN_COMMAND_KINDS),
        },
        "false_ack_negative_report": {
            "schema": FALSE_ACK_REPORT_SCHEMA_ID,
            "must_reject_sources": sorted(FALSE_ACK_SOURCES | NON_LIVE_SOURCES),
            "must_reject_surfaces": [
                "build_success",
                "checker_success",
                "pytest_success",
                "sender_success",
                "fixture_only_echo",
                "operator_intent",
                "quadrotor.unreal_state frame/status",
                "static/source/preflight rows",
            ],
        },
        "timeout_cleanup_manifest": {
            "schema": CLEANUP_MANIFEST_SCHEMA_ID,
            "required_pass_fields": [
                "timeout_seconds in (0, 60]",
                "probe_attempt_count=1",
                "cleanup_status=pass",
                "cleanup_completed=true",
                "runtime_windows_state_recorded=true",
                "listener_left_running=false",
                "timer_left_running=false",
                "background_loop_left_running=false",
                "socket_left_bound=false",
                "accepted_ui_controls_enabled=false",
            ],
        },
    }


def build_report(bundle_dir: Path | None = None) -> dict[str, Any]:
    fixture_matrix = build_fixture_matrix()
    bundle_validation = validate_bundle(bundle_dir) if bundle_dir else None
    matrix_summary = {
        "fixture_rows": len(fixture_matrix),
        "expected_valid_rows": sum(1 for row in fixture_matrix if row["expected_valid_bundle"]),
        "expected_reject_rows": sum(1 for row in fixture_matrix if not row["expected_valid_bundle"]),
        "runtime_ack_claims_now": sum(1 for row in fixture_matrix if row["accepted_as_runtime_ack_now"]),
        "authoritative_runtime_ack_claimable_now": False,
    }
    issues: list[str] = []
    if bundle_validation and not bundle_validation["ok"]:
        issues.extend(bundle_validation["issues"])
    return {
        "schema": "mosim.ue_runtime_probe_capture_bundle_validator.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static/capture-bundle-validator",
        "bundle_validation_performed": bundle_validation is not None,
        "source_static_validator_ready": True,
        "runtime_probe_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_029": False,
        "socket_listener_timer_or_background_loop_started": False,
        "accepted_state_ui_controls_enabled": False,
        "authoritative_runtime_ack_claimable_now": False,
        "validator_contract": build_validator_contract(),
        "fixture_matrix": fixture_matrix,
        "matrix_summary": matrix_summary,
        "bundle_validation": bundle_validation,
        "quality_boundary": {
            "accepted_as_runtime_ack_now": False,
            "future_live_bundle_can_be_validated": True,
            "static_build_sender_fixture_operator_or_frame_rows_are_ack": False,
            "json_packet_alone_is_runtime_ack": False,
        },
        "next_safe_runtime_gate": {
            "recommendation": "Use this validator in the next separately authorized single bounded live UE command-echo probe after an authoritative producer/capture surface exists.",
            "minimum_capture_artifacts": EXPECTED_ARTIFACTS,
            "blocked_now_reason": "029 is source-static only and does not authorize UE runtime/editor launch, live transport, sockets/listeners/timers/background loops, Unreal build, MWORKS/ROS2 execution, or runtime capture.",
        },
        "claim_boundary": [
            "029 proves only a source-static capture-bundle validator, focused tests, and fixture matrix for a future bounded live probe.",
            "029 does not open Unreal Editor, PIE, standalone runtime, or UE runtime.",
            "029 does not run Unreal build, bind sockets, start listeners/timers/background loops, or execute live transport.",
            "029 does not edit UE C++ source, Blueprint, UMG, Slate, web UI, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, or Git.",
            "029 checker/test/fixture rows and any source-static bundle validation are not live runtime ack.",
            "Build success, checker success, sender success, fixture-only echo, operator intent, source/static/preflight rows, and quadrotor.unreal_state frames cannot satisfy runtime command acknowledgement.",
            "029 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.",
        ],
        "forbidden_runtime_claims": {
            "authoritative_runtime_ack": False,
            "live_ue_runtime_ack": False,
            "live_mworks_downlink": False,
            "ros2_runtime_ack": False,
            "final_ui_acceptance": False,
            "planner_ready": False,
            "closed_loop": False,
            "controller_performance": False,
            "fast_lio_success": False,
            "mission_success": False,
        },
        "issues": issues,
    }


def write_summary(report: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# UE 029 Runtime Probe Capture Bundle Validator",
        "",
        f"- ok: {report['ok']}",
        f"- scope: {report['scope_classification']}",
        f"- bundle_validation_performed: {report['bundle_validation_performed']}",
        f"- runtime_probe_executed: {report['runtime_probe_executed']}",
        f"- authoritative_runtime_ack_claimable_now: {report['authoritative_runtime_ack_claimable_now']}",
        "",
        "## Required Artifacts",
        "",
    ]
    for artifact in EXPECTED_ARTIFACTS:
        lines.append(f"- {artifact}")
    lines.extend(["", "## Fixture Matrix Summary", ""])
    summary = report["matrix_summary"]
    lines.append(f"- fixture_rows: {summary['fixture_rows']}")
    lines.append(f"- expected_valid_rows: {summary['expected_valid_rows']}")
    lines.append(f"- expected_reject_rows: {summary['expected_reject_rows']}")
    lines.append(f"- runtime_ack_claims_now: {summary['runtime_ack_claims_now']}")
    if report.get("bundle_validation"):
        validation = report["bundle_validation"]
        lines.extend(["", "## Bundle Validation", ""])
        lines.append(f"- bundle_dir: {validation['bundle_dir']}")
        lines.append(f"- ok: {validation['ok']}")
        lines.append(f"- status: {validation['status']}")
    lines.extend(["", "## Claim Boundary", ""])
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", default="", help="Optional future capture-bundle directory to validate.")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--output-fixture-matrix", default="")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir) if args.bundle_dir else None
    if bundle_dir and not bundle_dir.is_absolute():
        bundle_dir = ROOT / bundle_dir

    report = build_report(bundle_dir)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        output_json = Path(args.output_json)
        if not output_json.is_absolute():
            output_json = ROOT / output_json
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text + "\n", encoding="utf-8")
    if args.output_fixture_matrix:
        output_matrix = Path(args.output_fixture_matrix)
        if not output_matrix.is_absolute():
            output_matrix = ROOT / output_matrix
        output_matrix.parent.mkdir(parents=True, exist_ok=True)
        output_matrix.write_text(json.dumps(report["fixture_matrix"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        if not output_md.is_absolute():
            output_md = ROOT / output_md
        write_summary(report, output_md)
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
