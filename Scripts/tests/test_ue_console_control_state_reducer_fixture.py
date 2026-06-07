from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_control_state_reducer_fixture.py"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "control_state_reducer_fixture.json"
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


def rows_by_descriptor(report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = {}
    for row in report["reducer_fixture_matrix"]:
        rows.setdefault(row["control_descriptor_id"], []).append(row)
    return rows


def row_by_kind(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["row_kind"]: row for row in rows}


def test_control_state_reducer_checker_is_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["schema"] == "mosim.ue_console_control_state_reducer_fixture.v1"
    assert report["scope_classification"] == "source-static"
    assert report["checker_only_contract"] is True
    assert report["source_static_reducer_fixture_gate"] is True
    assert report["not_live_runtime_evidence"] is True
    assert report["runtime_transport_implemented"] is False
    assert report["ui_runtime_implemented"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert all(value is False for value in report["forbidden_runtime_claims"].values())


def test_matrix_covers_all_seven_019_control_descriptors(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    summary = report["matrix_summary"]
    assert summary["descriptor_count"] == 7
    assert summary["total_rows"] == 49
    assert set(rows_by_descriptor(report)) == {
        "fault_motor_control",
        "wind_disturbance_control",
        "controller_switch_control",
        "planner_switch_control",
        "scene_map_switch_control",
        "experiment_run_control",
        "manual_review_request_control",
    }
    required = {
        "initial_disabled",
        "pending_from_matching_command",
        "accepted_from_authoritative_echo",
        "rejected_from_authoritative_echo",
        "stale_echo_rejected",
        "mismatched_echo_rejected",
        "false_ack_rejected",
    }
    for descriptor_id, row_kinds in summary["rows_per_descriptor"].items():
        assert set(row_kinds) == required, descriptor_id


def test_pending_only_comes_from_matching_ue_command_request(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    for descriptor_id, rows in rows_by_descriptor(report).items():
        pending = row_by_kind(rows)["pending_from_matching_command"]
        assert pending["input_schema"] == "mosim.ue_command.v1", descriptor_id
        assert pending["requested_by"] == "ue_experiment_console", descriptor_id
        assert pending["pending_source_method"] == "RecordPendingCommandFromPacketJson", descriptor_id
        assert pending["pending_created"] is True, descriptor_id
        assert pending["request_matches_descriptor"] is True, descriptor_id
        assert pending["request_matches_command_identity"] is True, descriptor_id
        assert pending["state_after"] == "pending", descriptor_id
        assert pending["quality_status"] == "pending_no_runtime_echo", descriptor_id
        assert pending["actual_live_runtime_ack"] is False, descriptor_id
        assert pending["accepted_state_ui_controls_enabled_now"] is False, descriptor_id


def test_accepted_and_rejected_only_come_from_authoritative_echo(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    for descriptor_id, rows in rows_by_descriptor(report).items():
        by_kind = row_by_kind(rows)
        accepted = by_kind["accepted_from_authoritative_echo"]
        rejected = by_kind["rejected_from_authoritative_echo"]
        for row in [accepted, rejected]:
            assert row["input_schema"] == "mosim.ue_command_echo.v1", descriptor_id
            assert row["source_authoritative_for_required_ack"] is True, descriptor_id
            assert row["matches_pending_request"] is True, descriptor_id
            assert row["matches_command_identity"] is True, descriptor_id
            assert row["no_pose_overwrite_status"] == "pass", descriptor_id
            assert row["echo_sink"] == "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
            assert row["actual_live_runtime_ack"] is False, descriptor_id
            assert row["accepted_as_live_runtime_ack_now"] is False, descriptor_id
            assert row["accepted_state_ui_controls_enabled_now"] is False, descriptor_id
        assert accepted["status"] == "accepted", descriptor_id
        assert accepted["future_accepted_state_eligible"] is True, descriptor_id
        assert rejected["status"] == "rejected", descriptor_id
        assert rejected["future_accepted_state_eligible"] is False, descriptor_id


def test_stale_and_mismatched_echoes_are_rejected(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    for descriptor_id, rows in rows_by_descriptor(report).items():
        stale = row_by_kind(rows)["stale_echo_rejected"]
        assert stale["input_schema"] == "mosim.ue_command_echo.v1", descriptor_id
        assert stale["transition_applied"] is False, descriptor_id
        assert stale["state_after"] == "pending", descriptor_id
        assert stale["reject_reason"] == "stale_or_seq_mismatch", descriptor_id
        assert stale["echo_seq"] != stale["pending_seq"], descriptor_id
        assert stale["future_accepted_state_eligible"] is False, descriptor_id
        mismatch = row_by_kind(rows)["mismatched_echo_rejected"]
        assert mismatch["input_schema"] == "mosim.ue_command_echo.v1", descriptor_id
        assert mismatch["transition_applied"] is False, descriptor_id
        assert mismatch["state_after"] == "pending", descriptor_id
        assert mismatch["matches_pending_request"] is False, descriptor_id
        assert mismatch["matches_command_identity"] is False, descriptor_id
        assert mismatch["echo_request_id"] != mismatch["pending_request_id"], descriptor_id
        assert mismatch["future_accepted_state_eligible"] is False, descriptor_id


def test_false_ack_sources_never_drive_pending_or_accepted_state(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    expected = {
        "build_success",
        "UnrealBuildTool_success",
        "pytest_success",
        "checker_success",
        "udp_send_success",
        "sender_result_bSent",
        "quadrotor.unreal_state.frame",
        "quadrotor.unreal_state.v1",
        "fixture_only_echo",
        "static_catalog_row",
        "operator_click_intent",
        "offline_adapter_smoke",
        "source_level_smoke",
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
    }
    assert expected <= set(report["gate_summary"]["false_ack_sources_rejected"])
    for descriptor_id, rows in rows_by_descriptor(report).items():
        false_ack = row_by_kind(rows)["false_ack_rejected"]
        assert false_ack["transition_applied"] is False, descriptor_id
        assert false_ack["state_after"] == "disabled_or_pending", descriptor_id
        assert false_ack["future_accepted_state_eligible"] is False, descriptor_id
        by_source = {case["source"]: case for case in false_ack["false_ack_sources"]}
        assert expected <= set(by_source), descriptor_id
        for source_name, case in by_source.items():
            assert case["is_authoritative_echo"] is False, source_name
            assert case["can_create_pending"] is False, source_name
            assert case["can_accept_or_reject"] is False, source_name
            assert case["accepted_as_live_runtime_ack_now"] is False, source_name
            assert case["accepted_state_ui_controls_enabled_now"] is False, source_name


def test_schema_and_state_component_anchors_are_present(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    schema = report["schema_anchor_summary"]
    assert "mosim_ue_command_v1.schema.json" in schema["command_schema"]
    assert "mosim_ue_command_echo_v1.schema.json" in schema["echo_schema"]
    assert {"accepted", "rejected"} <= set(schema["echo_status_values"])
    assert {"MWORKS", "ROS2", "MWORKS_ROS2"} <= set(schema["echo_ack_authority_values"])
    assert {"pose_override", "teleport", "set_uav_pose", "actor_transform", "keyboard_pose"} <= set(
        schema["command_schema_forbidden_wire_kinds"]
    )
    anchors = report["source_anchor_summary"]
    assert anchors["has_pending_method"] is True
    assert anchors["has_echo_sink"] is True
    assert anchors["has_command_schema_guard"] is True
    assert anchors["has_echo_schema_guard"] is True
    assert anchors["has_no_pose_overwrite_guard"] is True
    assert anchors["has_matching_pending_request_guard"] is True
    assert anchors["has_seq_mismatch_guard"] is True
    assert anchors["has_command_kind_mismatch_guard"] is True
    assert anchors["has_smoke_source_downgrade"] is True


def test_future_ui_recommendation_stays_echo_gated(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    gates = "\n".join(report["future_ui_implementation_recommendation"]["minimum_reducer_acceptance_gate"])
    assert "matching mosim.ue_command.v1 request" in gates
    assert "authoritative mosim.ue_command_echo.v1 row" in gates
    assert "run_id, request_id, seq, command wire kind, control_descriptor_id, and time_s" in gates
    assert "stale seq/time echoes remain rejected" in gates
    assert "mismatched request_id, command kind, or control descriptor echoes remain rejected" in gates
    assert "quadrotor.unreal_state never enable accepted controls" in gates
    blockers = "\n".join(report["future_ui_implementation_recommendation"]["blocker_conditions"])
    assert "enables accepted-state controls before authoritative live echo evidence" in blockers
    assert "planner_ready" in blockers
    assert "controller performance" in blockers
    assert "closed_loop" in blockers


def test_no_source_static_row_claims_live_ack_or_ui_acceptance(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["matrix_summary"]["runtime_ack_now_leaks"] == 0
    assert report["matrix_summary"]["all_controls_disabled_now"] is True
    assert report["matrix_summary"]["all_rows_not_live_runtime_evidence"] is True
    for row in report["reducer_fixture_matrix"]:
        assert row["actual_live_runtime_ack"] is False
        assert row["accepted_as_live_runtime_ack_now"] is False
        assert row["accepted_state_ui_controls_enabled_now"] is False
        assert row["not_live_runtime_evidence"] is True
        assert row["control_enabled_now"] is False
