from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_operator_command_catalog.py"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "operator_command_catalog.json"
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


def entries_by_kind(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["command_kind"]: entry for entry in report["catalog_entries"]}


def test_operator_command_catalog_checker_passes_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static"
    assert report["checker_only_contract"] is True
    assert report["not_live_runtime_evidence"] is True
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["runtime_transport_implemented"] is False
    assert report["umg_blueprint_slate_or_web_ui_implemented"] is False


def test_minimum_operator_command_entries_are_present(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert set(entries_by_kind(report)) == {
        "motor_fault.inject_or_clear",
        "disturbance.wind.set_or_clear",
        "controller.switch",
        "planner.switch",
        "scene_map.switch",
        "experiment.run_control",
        "manual_review.request",
    }
    assert report["catalog_summary"]["total_entries"] == 7
    assert report["catalog_summary"]["domain_owner_counts"] == {
        "MWORKS": 3,
        "PMO": 2,
        "ROS2": 1,
        "UE": 1,
    }


def test_each_entry_has_required_contract_fields_and_disabled_state(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    required_fields = {
        "command_kind",
        "domain_owner",
        "payload_contract",
        "required_ack_evidence_fields",
        "forbidden_shortcut",
        "accepted_state_precondition",
        "claim_boundary",
        "requires_mworks_ack",
        "requires_ros2_ack",
    }
    for command_kind, entry in entries_by_kind(report).items():
        assert required_fields <= set(entry), command_kind
        assert entry["payload_contract"], command_kind
        assert entry["required_ack_evidence_fields"], command_kind
        assert entry["forbidden_shortcut"], command_kind
        assert entry["accepted_state_allowed_now"] is False
        assert entry["ui_control_enabled_now"] is False
        assert entry["source_static_catalog_only"] is True
        assert entry["not_live_runtime_ack"] is True
        assert "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017" in entry[
            "accepted_state_precondition"
        ]
        assert "mosim.ue_command_echo.v1" in entry["accepted_state_precondition"]
        assert "RecordPendingCommandFromPacketJson" in entry["accepted_state_precondition"]


def test_payload_contracts_match_pmo_minimums(tmp_path: Path) -> None:
    entries = entries_by_kind(run_checker(tmp_path))
    assert set(entries["motor_fault.inject_or_clear"]["payload_contract"]) == {
        "motor_id or rotor_index",
        "fault_mode",
        "severity",
        "start_time_s",
        "duration_s or clear flag",
    }
    assert set(entries["disturbance.wind.set_or_clear"]["payload_contract"]) == {
        "wind_vector or profile_id",
        "frame",
        "start_time_s",
        "duration_s",
    }
    assert set(entries["controller.switch"]["payload_contract"]) == {
        "controller_id",
        "switch_time_s",
        "safe_transition_policy",
    }
    assert set(entries["planner.switch"]["payload_contract"]) == {
        "planner_id",
        "switch_time_s",
        "review_mode",
    }
    assert set(entries["scene_map.switch"]["payload_contract"]) == {
        "scene_id or map_id",
        "loading_policy",
        "review_gate",
    }
    assert set(entries["experiment.run_control"]["payload_contract"]) == {
        "run_id",
        "action",
        "target_domain",
        "evidence_policy",
    }
    assert set(entries["manual_review.request"]["payload_contract"]) == {
        "review_target",
        "artifact_type",
        "blocking_policy",
    }


def test_domain_owner_ack_requirements_are_explicit(tmp_path: Path) -> None:
    entries = entries_by_kind(run_checker(tmp_path))
    for command_kind in [
        "motor_fault.inject_or_clear",
        "disturbance.wind.set_or_clear",
        "controller.switch",
    ]:
        entry = entries[command_kind]
        assert entry["domain_owner"] == "MWORKS"
        assert entry["requires_mworks_ack"] is True
        assert entry["requires_ros2_ack"] is False
        assert entry["required_ack_authority_values"] == ["MWORKS"]
        assert entry["required_live_source_options"] == ["MWORKS_live_downlink"]
    planner = entries["planner.switch"]
    assert planner["domain_owner"] == "ROS2"
    assert planner["requires_mworks_ack"] is True
    assert planner["requires_ros2_ack"] is True
    assert planner["required_ack_authority_values"] == ["ROS2"]
    assert planner["required_live_source_options"] == ["ROS2_runtime_echo"]
    scene = entries["scene_map.switch"]
    assert scene["domain_owner"] == "UE"
    assert scene["requires_mworks_ack"] is True
    assert scene["requires_ros2_ack"] is True
    assert scene["required_ack_authority_values"] == ["MWORKS_ROS2"]
    assert scene["required_live_source_options"] == ["MWORKS_ROS2_live_downlink"]
    for command_kind in ["experiment.run_control", "manual_review.request"]:
        entry = entries[command_kind]
        assert entry["domain_owner"] == "PMO"
        assert entry["requires_mworks_ack"] is True
        assert entry["requires_ros2_ack"] is True


def test_ack_evidence_inherits_017_identity_timestamp_status_no_pose_gate(tmp_path: Path) -> None:
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
    }
    for command_kind, entry in entries_by_kind(report).items():
        assert required <= set(entry["required_ack_evidence_fields"]), command_kind
    gate = report["operator_catalog_gate"]
    assert gate["prior_live_echo_gate"] == "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017"
    assert gate["consumer_sink"] == "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
    assert "ApplyCommandEchoJsonToState" in gate["receiver_shell_entry"]


def test_forbidden_shortcuts_cover_pose_fake_map_and_false_ack_sources(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    required_shortcuts = {
        "keyboard_pose",
        "mouse_pose",
        "actor_transform",
        "SetActorLocation",
        "SetActorTransform",
        "TeleportTo",
        "set_uav_pose",
        "pose_override",
        "fake_point_cloud",
        "fake_grid_map",
        "browser_point_cloud_review",
        "UE_truth_map_to_planner",
        "build_success",
        "UnrealBuildTool_success",
        "pytest_success",
        "checker_success",
        "udp_send_success",
        "sender_result_bSent",
        "quadrotor.unreal_state.frame",
        "fixture_only_echo",
        "offline_source_preflight_smoke_row",
    }
    assert required_shortcuts <= set(report["forbidden_shortcuts_global"])
    for command_kind, entry in entries_by_kind(report).items():
        assert required_shortcuts <= set(entry["forbidden_shortcut"]), command_kind


def test_scene_planner_and_manual_review_claim_boundaries_are_safe(tmp_path: Path) -> None:
    entries = entries_by_kind(run_checker(tmp_path))
    planner = json.dumps(entries["planner.switch"], ensure_ascii=False)
    assert "No planner_ready claim from UE" in planner
    assert "browser local-map review as RViz2 replacement" in planner
    scene = json.dumps(entries["scene_map.switch"], ensure_ascii=False)
    assert "sensor-oracle context" in scene
    assert "UE global truth map to planner" in scene
    assert "visual-only level dropdown" in scene
    run_control = json.dumps(entries["experiment.run_control"], ensure_ascii=False)
    assert "does not prove controller/planner success" in run_control
    manual_review = json.dumps(entries["manual_review.request"], ensure_ascii=False)
    assert "not automated acceptance" in manual_review
    assert "screenshot path alone as visual acceptance" in manual_review


def test_dotted_catalog_labels_do_not_pretend_to_be_current_wire_kinds(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    allowed_wire = set(report["schema_anchor_summary"]["current_allowed_wire_kinds"])
    forbidden_wire = set(report["schema_anchor_summary"]["forbidden_wire_kinds"])
    assert allowed_wire == {
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
    assert {"pose_override", "teleport", "set_uav_pose", "actor_transform", "keyboard_pose"} <= forbidden_wire
    for command_kind, entry in entries_by_kind(report).items():
        wire_kinds = [entry["current_wire_kind"]] if "current_wire_kind" in entry else entry["current_wire_kind_options"]
        assert set(wire_kinds) <= allowed_wire, command_kind
        assert command_kind not in allowed_wire, command_kind
        assert entry["command_kind_status"] == "source_static_operator_catalog_label"
    assert sorted(report["catalog_summary"]["current_wire_kind_options_only"]) == ["experiment.run_control"]
    assert set(report["catalog_summary"]["catalog_only_operator_labels"]) == set(entries_by_kind(report))


def test_source_anchors_keep_sender_state_sink_and_receiver_shell_separate(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    anchors = report["source_anchor_summary"]
    sender = anchors["command_sender"]
    state = anchors["state_component"]
    receiver = anchors["command_echo_receiver_shell"]
    assert sender["role"] == "current mosim.ue_command.v1 sender only"
    assert sender["has_component"] is True
    assert "controller_select" in sender["supported_wire_kinds_present"]
    assert "scene_switch" in sender["supported_wire_kinds_present"]
    assert sender["send_success_is_runtime_ack"] is False
    assert state["has_pending_method"] is True
    assert state["has_echo_sink"] is True
    assert state["has_echo_schema_guard"] is True
    assert receiver["role"] == "source-static echo shell only; no runtime listener"
    assert receiver["has_receiver_shell_entry"] is True
    assert receiver["has_echo_schema_guard"] is True


def test_no_forbidden_runtime_claims_or_ui_acceptance(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert all(value is False for value in report["forbidden_runtime_claims"].values())
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["runtime_transport_implemented"] is False
    assert report["umg_blueprint_slate_or_web_ui_implemented"] is False
    assert report["catalog_summary"]["all_entries_disable_accepted_state_now"] is True
    assert report["catalog_summary"]["all_entries_require_017_gate"] is True
    assert report["catalog_summary"]["all_entries_reject_global_shortcuts"] is True


def test_future_live_ui_task_recommendation_stays_gated_by_authoritative_echo(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    recommendation = report["future_live_ui_task_recommendation"]
    acceptance_gate = set(recommendation["minimum_future_live_acceptance_gate"])
    assert "operator action emits mosim.ue_command.v1 with a catalog entry mapped to an allowed base wire kind" in acceptance_gate
    assert "state component records matching pending request by run_id/request_id/seq" in acceptance_gate
    assert "authorized MWORKS/ROS2/MWORKS_ROS2 producer emits mosim.ue_command_echo.v1" in acceptance_gate
    assert "source matches ack_authority and domain owner" in acceptance_gate
    assert "time_s and command identity are present" in acceptance_gate
    assert "status is accepted or rejected" in acceptance_gate
    assert "no_pose_overwrite_status=pass" in acceptance_gate
    blockers = "\n".join(recommendation["blocker_conditions"])
    assert "enable accepted-state UI before authoritative echo evidence" in blockers
    assert "sender success" in blockers
    assert "quadrotor.unreal_state frames as ack" in blockers
    assert "keyboard/mouse/direct Actor transform" in blockers
