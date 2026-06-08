from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_runtime_echo_producer_downlink_gate.py"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "runtime_echo_producer_downlink_gate.json"
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


def test_024_checker_is_source_static_build_prep_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["schema"] == "mosim.ue_console_runtime_echo_producer_downlink_gate.v1"
    assert report["scope_classification"] == "source-static/build-prep"
    assert report["source_static_build_prep"] is True
    assert report["runtime_probe_executed"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_editor_opened"] is False
    assert report["unreal_build_executed"] is False
    assert report["socket_or_listener_started"] is False
    assert report["runtime_socket_udp_tcp_receiver_implemented"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["not_live_runtime_evidence"] is True
    assert all(value is False for value in report["forbidden_runtime_claims"].values())


def test_prior_gate_inputs_capture_021_022_and_023_blocker(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_gate_inputs"]
    assert prior["021_status"] == "completed"
    assert prior["022_status"] == "completed"
    assert prior["023_status"] == "blocked"
    assert prior["023_blocker_code"] == "blocked_no_authoritative_runtime_echo_probe_surface"
    assert prior["021_return"].endswith("20260608-021.json")
    assert prior["022_return"].endswith("20260608-022.json")
    assert prior["023_blocker"].endswith("20260608-023.json")


def test_receiver_shell_exposes_authoritative_downlink_handoff_without_transport(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    receiver = report["source_anchor_summary"]["receiver_shell"]
    assert receiver["has_authoritative_validate_method"] is True
    assert receiver["has_authoritative_apply_method"] is True
    assert receiver["has_existing_source_static_apply_method"] is True
    assert receiver["calls_state_sink"] is True
    assert receiver["runtime_transport_patterns_present"] == []
    assert receiver["forbidden_pose_patterns_present"] == []
    patch = report["source_patch_summary"]
    assert patch["added_source_static_methods"] == [
        "IsAuthoritativeRuntimeCommandEchoPacketJson",
        "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState",
    ]
    assert patch["does_not_record_pending_request"] is True
    assert patch["does_not_parse_command_request_schema"] is True
    assert patch["does_not_parse_quadrotor_unreal_state"] is True


def test_state_sender_and_frame_receiver_boundaries_stay_separate(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    anchors = report["source_anchor_summary"]
    state = anchors["state_component"]
    frame = anchors["frame_status_receiver"]
    sender = anchors["command_sender"]
    assert state["pending_source"] == "RecordPendingCommandFromPacketJson"
    assert state["echo_sink"] == "ApplyCommandEchoJson"
    assert state["has_timestamp_guard"] is True
    assert state["has_source_authority_guard"] is True
    assert set(state["non_live_labels_downgraded"]) == {
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
        "offline_adapter_smoke",
        "source_level_smoke",
    }
    assert frame["role"] == "quadrotor.unreal_state frame/status receiver only"
    assert frame["parses_command_echo_schema"] is False
    assert frame["calls_echo_sink"] is False
    assert sender["role"] == "mosim.ue_command.v1 sender only"
    assert sender["parses_command_echo_schema"] is False
    assert sender["calls_echo_sink"] is False
    assert sender["send_success_is_ack"] is False


def test_downlink_contract_requires_identity_timestamp_status_and_no_pose(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    contract = report["downlink_contract"]
    assert contract["consumer_handoff"].endswith("ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState")
    assert contract["consumer_sink"] == "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
    assert "mosim.ue_command.v1" in contract["pending_precondition"]
    required = set(contract["required_fields_before_state_sink"])
    assert {
        "schema",
        "source",
        "ack_authority",
        "run_id",
        "request_id",
        "seq",
        "time_s",
        "status",
        "command.kind or command_kind",
        "no_pose_overwrite_status",
    } <= required
    assert contract["authoritative_source_authority_pairs"] == {
        "MWORKS_live_downlink": "MWORKS",
        "ROS2_runtime_echo": "ROS2",
        "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
    }


def test_only_authoritative_rows_are_downlink_handoff_eligible(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["downlink_fixture_matrix"]
    eligible = [row for row in rows if row["downlink_handoff_eligible"]]
    assert {row["row_name"] for row in eligible} == {
        "valid_future_MWORKS_live_downlink",
        "valid_future_ROS2_runtime_echo",
        "valid_future_MWORKS_ROS2_live_downlink",
        "valid_future_rejected_MWORKS_live_downlink",
        "valid_future_rejected_ROS2_runtime_echo",
        "valid_future_rejected_MWORKS_ROS2_live_downlink",
    }
    accepted = [row for row in rows if row["accepted_as_runtime_ack"]]
    assert {row["row_name"] for row in accepted} == {
        "valid_future_MWORKS_live_downlink",
        "valid_future_ROS2_runtime_echo",
        "valid_future_MWORKS_ROS2_live_downlink",
    }
    assert {row["actual_runtime_transport_evidence"] for row in rows} == {False}


def test_false_ack_and_non_live_sources_reject_before_state_sink(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rejected_sources = set(report["downlink_contract"]["negative_sources_rejected_before_state_sink"]["false_ack_sources"])
    rejected_sources |= set(report["downlink_contract"]["negative_sources_rejected_before_state_sink"]["non_live_sources"])
    rows = [row for row in report["downlink_fixture_matrix"] if row["source"] in rejected_sources]
    assert rows
    assert {row["downlink_policy"] for row in rows} == {"reject_before_state_sink"}
    assert {row["downlink_handoff_eligible"] for row in rows} == {False}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}
    assert {
        "022_build_only_compile_pass",
        "UnrealBuildTool_success",
        "build_success",
        "udp_send_success",
        "sender_result_bSent",
        "quadrotor.unreal_state.v1",
        "quadrotor.unreal_state.frame",
    } <= rejected_sources


def test_malformed_identity_authority_and_pose_rows_reject_before_state_sink(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    malformed = {
        "missing_run_id",
        "missing_request_id",
        "missing_seq",
        "missing_time_s",
        "missing_command_kind",
        "wrong_authority_for_source",
        "no_pose_overwrite_failure",
        "forbidden_pose_command",
        "frame_schema_not_echo",
    }
    rows = [row for row in report["downlink_fixture_matrix"] if row["row_name"] in malformed]
    assert len(rows) == len(malformed)
    assert {row["downlink_policy"] for row in rows} == {"reject_before_state_sink"}
    assert {row["downlink_handoff_eligible"] for row in rows} == {False}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}


def test_matrix_summary_has_no_runtime_leaks(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    summary = report["matrix_summary"]
    assert summary["future_authoritative_accepted_rows"] == 3
    assert summary["future_authoritative_rejected_rows"] == 3
    assert summary["non_live_rows"] == 4
    assert summary["false_ack_rows"] == 16
    assert summary["invalid_rows"] == 9
    assert summary["runtime_ack_leaks"] == 0
    assert summary["actual_runtime_claim_rows"] == 0


def test_build_prep_surface_defers_unreal_build_to_later_gate(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    surface = report["build_prep_surface"]
    assert surface["build_not_run_in_024"] is True
    assert surface["future_build_command"] == "Scripts/UE5/build_unreal_renderer.sh"
    assert surface["uproject"] == "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
    assert surface["engine_association"] == "5.5"
    assert surface["plugin"] == "UE5/Bridge/QuadrotorMworksBridge.uplugin"
    assert surface["module"] == "QuadrotorMworksBridge"
    assert surface["prior_compile_evidence"].endswith("20260608-022.json")


def test_claim_boundary_forbids_live_ack_and_planner_controller_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    assert "source-static/build-prep" in boundary
    assert "does not run a live UE runtime/editor command-echo probe" in boundary
    assert "does not implement a socket/UDP/TCP listener" in boundary
    assert "does not prove live UE runtime ack" in boundary
    assert "planner_ready" in boundary
    assert "controller performance" in boundary
    assert "mission success" in boundary
    assert "closed_loop" in boundary
