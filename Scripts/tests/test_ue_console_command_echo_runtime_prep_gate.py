from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_command_echo_runtime_prep_gate.py"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "command_echo_runtime_prep_gate.json"
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
    for row in report["runtime_prep_matrix"]:
        rows.setdefault(row["control_descriptor_id"], []).append(row)
    return rows


def test_runtime_prep_checker_is_source_static_build_prep_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["schema"] == "mosim.ue_console_command_echo_runtime_prep_gate.v1"
    assert report["scope_classification"] == "source-static/build-prep"
    assert report["source_static_runtime_prep"] is True
    assert report["build_prep_only"] is True
    assert report["unreal_build_executed"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_editor_opened"] is False
    assert report["socket_or_listener_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["not_live_runtime_evidence"] is True
    assert all(value is False for value in report["forbidden_runtime_claims"].values())


def test_prior_gates_are_consumed_as_inputs(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_gate_inputs"]
    assert prior["017_status"] == "completed"
    assert prior["018_status"] == "completed"
    assert prior["020_status"] == "completed"
    assert prior["020_checker_ok"] is True
    assert prior["017_return"].endswith("20260607-017.json")
    assert prior["018_return"].endswith("20260607-018.json")
    assert prior["020_reducer_evidence"].endswith("control_state_reducer_fixture_source_static.json")


def test_state_component_has_runtime_prep_source_guards(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    anchors = report["source_anchor_summary"]
    assert anchors["has_pending_method"] is True
    assert anchors["has_echo_sink"] is True
    assert anchors["has_timestamp_guard"] is True
    assert anchors["has_source_authority_guard"] is True
    assert anchors["accepted_runtime_ack_requires_accepted_status"] is True
    assert anchors["legacy_ack_anchor_preserved"] is True
    assert anchors["receiver_shell_calls_state_sink"] is True
    assert anchors["receiver_shell_runtime_patterns_present"] == []
    assert anchors["forbidden_pose_patterns_present"] == []
    assert anchors["frame_receiver_parses_echo"] is False
    assert anchors["sender_parses_echo"] is False
    assert anchors["has_authoritative_live_sources"] == {
        "MWORKS_live_downlink": True,
        "ROS2_runtime_echo": True,
        "MWORKS_ROS2_live_downlink": True,
    }
    assert set(anchors["has_non_live_source_downgrade"].values()) == {True}


def test_source_patch_summary_lists_narrow_changed_methods(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    patch = report["source_patch_summary"]
    assert patch["changed_methods"] == ["ApplyCommandEchoJson", "anonymous namespace helper functions"]
    joined = "\n".join(patch["added_source_guards"])
    assert "time_s" in joined
    assert "IsAuthoritativeLiveEchoSource" in joined
    assert "status=accepted" in joined
    assert "status=rejected" in joined
    assert "smoke_only" in joined
    assert patch["no_pose_overwrite_guard"] == "no_pose_overwrite_not_pass"
    assert patch["pending_precondition"] == "RecordPendingCommandFromPacketJson"
    assert patch["echo_sink"] == "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"


def test_runtime_prep_matrix_covers_seven_controls_and_valid_future_rows(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    summary = report["matrix_summary"]
    assert summary["control_descriptor_count"] == 7
    assert summary["valid_future_authoritative_accepted_echo_rows"] == 7
    assert summary["authoritative_rejected_rows"] == 7
    assert summary["missing_timestamp_rows"] == 7
    assert summary["wrong_authority_rows"] == 7
    assert summary["no_matching_pending_rows"] == 7
    assert summary["command_identity_mismatch_rows"] == 7
    assert summary["no_pose_failure_rows"] == 7
    assert summary["runtime_prep_leaks"] == 0
    assert summary["actual_runtime_or_ui_leaks"] == 0
    assert set(rows_by_descriptor(report)) == {
        "fault_motor_control",
        "wind_disturbance_control",
        "controller_switch_control",
        "planner_switch_control",
        "scene_map_switch_control",
        "experiment_run_control",
        "manual_review_request_control",
    }


def test_only_valid_future_authoritative_accepted_rows_are_runtime_prep_eligible(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    for descriptor_id, rows in rows_by_descriptor(report).items():
        eligible = [row for row in rows if row["accepted_as_runtime_ack_by_source_prep"]]
        assert len(eligible) == 1, descriptor_id
        row = eligible[0]
        assert row["row_kind"] == "valid_future_authoritative_accepted_echo"
        assert row["schema"] == "mosim.ue_command_echo.v1"
        assert row["status"] == "accepted"
        assert row["source_authority_matches"] is True
        assert row["has_matching_pending"] is True
        assert row["has_timestamp"] is True
        assert row["command_identity_matches"] is True
        assert row["no_pose_overwrite_status"] == "pass"
        assert row["actual_live_runtime_ack_now"] is False
        assert row["accepted_state_ui_controls_enabled_now"] is False


def test_rejected_missing_timestamp_wrong_authority_and_identity_rows_do_not_accept(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    blocked_kinds = {
        "authoritative_rejected_echo_not_runtime_accepted",
        "missing_timestamp_rejected",
        "wrong_authority_rejected",
        "no_matching_pending_rejected",
        "command_identity_mismatch_rejected",
        "no_pose_overwrite_failure_rejected",
    }
    for row in report["runtime_prep_matrix"]:
        if row["row_kind"] in blocked_kinds:
            assert row["accepted_as_runtime_ack_by_source_prep"] is False, row
            assert row["future_sink_eligible_after_live_transport"] is False, row
            assert row["state_transition_contract"] == "blocked_or_rejected", row


def test_non_live_and_false_ack_rows_are_rejected(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    non_live = {
        "offline_adapter_smoke",
        "source_level_smoke",
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
    }
    false_ack = {
        "build_success",
        "UnrealBuildTool_success",
        "pytest_success",
        "checker_success",
        "cli_build_success",
        "udp_send_success",
        "sender_result_bSent",
        "quadrotor.unreal_state.frame",
        "quadrotor.unreal_state.v1",
        "fixture_only_echo",
        "static_catalog_row",
        "operator_click_intent",
    }
    rows = [
        row
        for row in report["runtime_prep_matrix"]
        if row["source"] in non_live or row["source"] in false_ack
    ]
    assert rows
    assert {row["accepted_as_runtime_ack_by_source_prep"] for row in rows} == {False}
    assert {row["future_sink_eligible_after_live_transport"] for row in rows} == {False}
    assert {row["actual_live_runtime_ack_now"] for row in rows} == {False}
    assert {row["accepted_state_ui_controls_enabled_now"] for row in rows} == {False}
    assert report["matrix_summary"]["non_live_rows"] == 28
    assert report["matrix_summary"]["false_ack_rows"] == 84


def test_build_prep_surface_is_defined_but_not_executed(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    surface = report["build_prep_surface"]
    assert surface["build_not_run_in_021"] is True
    assert surface["uproject"] == "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
    assert surface["engine_association"] == "5.5"
    assert surface["plugin"] == "UE5/Bridge/QuadrotorMworksBridge.uplugin"
    assert surface["module"] == "QuadrotorMworksBridge"
    assert surface["future_build_command"] == "Scripts/UE5/build_unreal_renderer.sh"
    gates = "\n".join(surface["future_build_acceptance_gates"])
    assert "No UE Editor/PIE/runtime starts" in gates
    assert "Build success is recorded only as compile evidence" in gates


def test_future_live_probe_recommendation_keeps_claim_boundary(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    recommendation = report["future_live_probe_recommendation"]
    evidence = "\n".join(recommendation["minimum_live_probe_evidence"])
    assert "pending mosim.ue_command.v1 request" in evidence
    assert "live mosim.ue_command_echo.v1 row" in evidence
    assert "time_s present" in evidence
    assert "no_pose_overwrite_status=pass" in evidence
    assert "build/checker/sender/fixture/static/frame/non-live sources" in evidence
    must_not_claim = set(recommendation["must_not_claim"])
    assert {
        "controller performance",
        "planner_ready",
        "FAST-LIO success",
        "mission success",
        "closed_loop",
        "final UI acceptance",
    } <= must_not_claim
