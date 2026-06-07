from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_ui_binding_preflight.py"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "ui_binding_preflight.json"
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


def descriptors_by_kind(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {descriptor["command_kind"]: descriptor for descriptor in report["control_descriptors"]}


def test_ui_binding_preflight_checker_passes_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static"
    assert report["checker_only_contract"] is True
    assert report["source_static_ui_binding_preflight"] is True
    assert report["not_live_runtime_evidence"] is True
    assert report["runtime_transport_implemented"] is False
    assert report["ui_runtime_implemented"] is False
    assert report["accepted_state_ui_controls_enabled"] is False


def test_all_seven_018_catalog_entries_have_control_descriptors(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert set(descriptors_by_kind(report)) == {
        "motor_fault.inject_or_clear",
        "disturbance.wind.set_or_clear",
        "controller.switch",
        "planner.switch",
        "scene_map.switch",
        "experiment.run_control",
        "manual_review.request",
    }
    assert report["descriptor_summary"]["total_descriptors"] == 7
    assert report["descriptor_summary"]["control_descriptor_ids"] == [
        "controller_switch_control",
        "experiment_run_control",
        "fault_motor_control",
        "manual_review_request_control",
        "planner_switch_control",
        "scene_map_switch_control",
        "wind_disturbance_control",
    ]


def test_control_descriptors_default_disabled_and_source_static(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    for command_kind, descriptor in descriptors_by_kind(report).items():
        assert descriptor["default_state"] == "disabled_pending_authoritative_echo", command_kind
        assert descriptor["control_enabled_now"] is False, command_kind
        assert descriptor["accepted_state_allowed_now"] is False, command_kind
        assert descriptor["source_static_descriptor_only"] is True, command_kind
        assert descriptor["not_live_runtime_evidence"] is True, command_kind
        assert descriptor["runtime_binding_implemented"] is False, command_kind
        assert descriptor["ui_runtime_implemented"] is False, command_kind
        assert descriptor["accepted_state_ui_controls_enabled"] is False, command_kind
    summary = report["descriptor_summary"]
    assert summary["all_default_disabled_pending_authoritative_echo"] is True
    assert summary["all_controls_disabled_now"] is True
    assert summary["all_accepted_state_disallowed_now"] is True
    assert summary["all_descriptors_source_static_only"] is True


def test_control_descriptor_groups_and_wire_mappings_are_explicit(tmp_path: Path) -> None:
    descriptors = descriptors_by_kind(run_checker(tmp_path))
    assert descriptors["motor_fault.inject_or_clear"]["control_group"] == "Fault"
    assert descriptors["motor_fault.inject_or_clear"]["current_wire_kind"] == "motor_fault"
    assert descriptors["disturbance.wind.set_or_clear"]["control_group"] == "Disturbance"
    assert descriptors["disturbance.wind.set_or_clear"]["current_wire_kind"] == "wind_profile"
    assert descriptors["controller.switch"]["control_group"] == "Controller"
    assert descriptors["controller.switch"]["current_wire_kind"] == "controller_select"
    assert descriptors["planner.switch"]["control_group"] == "Planner"
    assert descriptors["planner.switch"]["current_wire_kind"] == "planner_select"
    assert descriptors["scene_map.switch"]["control_group"] == "Scenario"
    assert descriptors["scene_map.switch"]["current_wire_kind"] == "scene_switch"
    assert descriptors["experiment.run_control"]["control_group"] == "Run"
    assert descriptors["experiment.run_control"]["current_wire_kind_options"] == [
        "scenario_reset",
        "start_goal_update",
        "recording",
    ]
    assert descriptors["manual_review.request"]["control_group"] == "Evidence/Review"
    assert descriptors["manual_review.request"]["current_wire_kind"] == "recording"


def test_pending_source_and_authoritative_echo_precondition_are_required(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    for command_kind, descriptor in descriptors_by_kind(report).items():
        assert "RecordPendingCommandFromPacketJson" in descriptor["pending_source"], command_kind
        assert "mosim.ue_command.v1" in descriptor["pending_source"], command_kind
        precondition = descriptor["accepted_state_precondition"]
        assert "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017" in precondition
        assert "mosim.ue_command_echo.v1" in precondition
        assert "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson" in precondition
        assert "run_id/request_id/seq/command identity" in precondition
        assert "time_s" in precondition
        assert "status=accepted|rejected" in precondition
        assert "no_pose_overwrite_status=pass" in precondition
    gate = report["catalog_to_control_gate"]
    assert gate["source_catalog_gate"] == "RFLY-MOSIM-UE-CONSOLE-OPERATOR-COMMAND-CATALOG-SOURCE-STATIC-GATE-20260607-018"
    assert gate["future_live_echo_gate"] == "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017"
    assert gate["consumer_sink"] == "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"


def test_required_echo_fields_match_017_authoritative_ack_contract(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    required = {
        "schema=mosim.ue_command_echo.v1",
        "source",
        "ack_authority",
        "run_id",
        "request_id",
        "seq",
        "time_s",
        "status=accepted|rejected",
        "command.kind or command_kind",
        "matching pending request recorded from mosim.ue_command.v1",
        "no_pose_overwrite_status=pass",
        "source/ack_authority matches domain owner",
        "control_descriptor_id matches pending UI command descriptor",
    }
    for command_kind, descriptor in descriptors_by_kind(report).items():
        assert required <= set(descriptor["required_echo_fields"]), command_kind


def test_false_ack_sources_and_operator_clicks_are_rejected(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    required_false_ack_sources = {
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
    assert required_false_ack_sources <= set(report["false_ack_sources_rejected"])
    for command_kind, descriptor in descriptors_by_kind(report).items():
        assert required_false_ack_sources <= set(descriptor["forbidden_shortcut"]), command_kind
        assert descriptor["operator_click_is_success"] is False
        assert descriptor["sender_success_is_success"] is False
        assert descriptor["build_success_is_success"] is False
        assert descriptor["fixture_or_static_row_is_success"] is False
    assert report["descriptor_summary"]["all_reject_operator_click_sender_build_fixture_success"] is True


def test_schema_and_source_anchors_keep_sender_state_and_receiver_roles_separate(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    schema = report["schema_anchor_summary"]
    assert set(schema["current_allowed_wire_kinds"]) == {
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
    assert {"pose_override", "teleport", "set_uav_pose", "actor_transform", "keyboard_pose"} <= set(
        schema["forbidden_wire_kinds"]
    )
    anchors = report["source_anchor_summary"]
    sender = anchors["command_sender"]
    state = anchors["state_component"]
    receiver = anchors["command_echo_receiver_shell"]
    assert sender["role"] == "mosim.ue_command.v1 sender only"
    assert sender["has_command_schema"] is True
    assert sender["has_send_success_anchor"] is True
    assert sender["send_success_is_runtime_ack"] is False
    assert state["role"] == "pending command and command echo state reducer"
    assert state["has_pending_method"] is True
    assert state["has_echo_sink"] is True
    assert state["has_echo_schema_guard"] is True
    assert receiver["role"] == "source-static echo shell only; no runtime listener"
    assert receiver["has_receiver_shell_entry"] is True
    assert receiver["has_echo_schema_guard"] is True
    assert receiver["runtime_udp_receiver_pattern_present"] is False


def test_planner_scene_run_and_manual_review_claim_boundaries_are_safe(tmp_path: Path) -> None:
    descriptors = descriptors_by_kind(run_checker(tmp_path))
    planner = json.dumps(descriptors["planner.switch"], ensure_ascii=False)
    assert "planner_ready" in planner
    assert "browser local-map review as RViz2 replacement" in planner
    scene = json.dumps(descriptors["scene_map.switch"], ensure_ascii=False)
    assert "UE global truth map to planner" in scene
    assert "visual-only level dropdown" in scene
    run_control = json.dumps(descriptors["experiment.run_control"], ensure_ascii=False)
    assert "does not prove controller/planner success" in run_control
    assert "closed_loop" in run_control
    manual_review = json.dumps(descriptors["manual_review.request"], ensure_ascii=False)
    assert "not automated acceptance" in manual_review
    assert "final" in manual_review or "acceptance" in manual_review


def test_no_forbidden_runtime_claims_or_ui_acceptance(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert all(value is False for value in report["forbidden_runtime_claims"].values())
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["runtime_transport_implemented"] is False
    assert report["ui_runtime_implemented"] is False


def test_future_live_ui_task_recommendation_stays_authoritative_echo_gated(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    recommendation = report["future_live_ui_task_recommendation"]
    gate = set(recommendation["minimum_acceptance_gate"])
    assert "operator control emits mosim.ue_command.v1 for an allowed current wire kind" in gate
    assert "state component records matching pending request by run_id/request_id/seq" in gate
    assert "authoritative MWORKS/ROS2/MWORKS_ROS2 producer emits mosim.ue_command_echo.v1" in gate
    assert "source and ack_authority match domain owner" in gate
    assert "time_s and command identity are present" in gate
    assert "status is accepted or rejected" in gate
    assert "no_pose_overwrite_status=pass" in gate
    blockers = "\n".join(recommendation["blocker_conditions"])
    assert "enable accepted-state UI before authoritative echo evidence" in blockers
    assert "sender/build/pytest/checker/fixture/static/operator-click/frame rows as ack" in blockers
    assert "keyboard/mouse/direct Actor transform" in blockers
    assert "UE global truth map to planner" in blockers
