from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_probe_harness_prep.py"


def run_checker(tmp_path: Path) -> dict[str, Any]:
    output = tmp_path / "runtime_probe_harness_prep.json"
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


def test_028_checker_is_source_static_harness_prep_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["schema"] == "mosim.ue_runtime_probe_harness_prep.v1"
    assert report["scope_classification"] == "source-static/runtime-probe-harness-prep"
    assert report["source_diff_required_for_028"] is False
    assert report["cxx_edits_performed_by_028"] is False
    assert report["runtime_probe_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["unreal_build_executed_in_028"] is False
    assert report["socket_listener_timer_or_background_loop_started"] is False
    assert report["accepted_state_ui_controls_enabled"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False


def test_027_readiness_input_is_preserved_as_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_gate_inputs"]
    assert prior["ue_027_status"] == "completed"
    assert prior["ue_027_quality_status"] == "authoritative_echo_runtime_readiness_source_static_passed"
    assert prior["ue_027_runtime_ready_now"] is False
    assert prior["ue_027_authoritative_runtime_ack_claimable_now"] is False
    assert prior["ue_027_false_ack_runtime_leaks_now"] == 0


def test_no_diff_harness_plan_uses_existing_source_anchors(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    plan = report["no_diff_harness_plan"]
    assert plan["plan_type"] == "precise_no_diff_harness_plan"
    assert plan["existing_source_anchors_sufficient"] is True
    assert "No UE C++ diff is required" in plan["next_code_surface"]

    anchors = report["source_anchor_summary"]
    receiver = anchors["command_echo_receiver"]
    state = anchors["state_component"]
    frame = anchors["frame_status_receiver"]
    sender = anchors["command_sender"]

    assert receiver["has_authoritative_validate_method"] is True
    assert receiver["has_authoritative_apply_method"] is True
    assert receiver["calls_state_sink"] is True
    assert receiver["runtime_transport_patterns_present"] == []
    assert receiver["forbidden_pose_patterns_present"] == []
    assert receiver["records_pending_requests"] is False
    assert receiver["parses_command_request_schema"] is False
    assert receiver["parses_quadrotor_unreal_state"] is False

    assert state["pending_source"] == "RecordPendingCommandFromPacketJson"
    assert state["echo_sink"] == "ApplyCommandEchoJson"
    assert set(state["non_live_labels_downgraded"]) == {
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
        "offline_adapter_smoke",
        "source_level_smoke",
    }
    assert state["non_live_accepted_as_runtime_ack"] is False

    assert frame["role"] == "quadrotor.unreal_state frame/status receiver only"
    assert frame["parses_command_echo_schema"] is False
    assert frame["calls_echo_sink"] is False
    assert sender["role"] == "mosim.ue_command.v1 sender only"
    assert sender["parses_command_echo_schema"] is False
    assert sender["calls_echo_sink"] is False
    assert sender["send_success_is_ack"] is False


def test_runtime_probe_contract_names_required_capture_fields(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    contract = report["runtime_probe_harness_contract"]
    assert contract["future_probe_scope"] == "single bounded PMO-authorized UE runtime/editor probe only"
    assert {
        "producer_surface",
        "producer_instance_id",
        "source",
        "ack_authority",
        "capture_session_id",
        "transport_capture_id",
    } <= set(contract["producer_identity_required"])
    assert contract["authoritative_source_authority_pairs"] == {
        "MWORKS_live_downlink": "MWORKS",
        "ROS2_runtime_echo": "ROS2",
        "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
    }
    assert contract["pending_request_capture"]["schema"] == "mosim.ue_command.v1"
    assert contract["echo_capture"]["schema"] == "mosim.ue_command_echo.v1"
    assert {
        "run_id",
        "request_id",
        "seq",
        "time_s",
        "command.kind or command_kind",
        "status",
    } <= set(contract["matching_identity_fields"])
    assert contract["no_pose_overwrite_proof"]["required_value"] == "no_pose_overwrite_status=pass"
    assert {
        "pose_override",
        "teleport",
        "set_uav_pose",
        "actor_transform",
        "keyboard_pose",
    } <= set(contract["no_pose_overwrite_proof"]["forbidden_command_kinds"])
    assert "timeout_cleanup_manifest.json" in contract["future_capture_artifacts"]


def test_harness_matrix_keeps_future_runtime_rows_missing_now(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = {row["row_id"]: row for row in report["harness_readiness_matrix"]}
    for row_id in [
        "prior_027_source_static_readiness",
        "command_request_schema_identity",
        "command_echo_schema_boundary",
        "source_static_authoritative_echo_receiver",
        "pending_request_capture_sink",
        "authoritative_echo_state_sink",
        "no_diff_harness_plan",
    ]:
        assert rows[row_id]["available_now"] is True
        assert rows[row_id]["accepted_as_runtime_ack_now"] is False

    for row_id in [
        "future_live_authoritative_echo_producer",
        "future_live_transport_capture",
        "future_runtime_no_pose_overwrite_capture",
        "future_runtime_false_ack_negative_capture",
        "future_cleanup_manifest",
    ]:
        assert rows[row_id]["available_now"] is False
        assert rows[row_id]["accepted_as_runtime_ack_now"] is False
        assert rows[row_id]["missing_reason"]


def test_future_probe_fixture_matrix_accepts_only_future_authoritative_contract_rows(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["future_probe_fixture_matrix"]
    eligible = [row for row in rows if row["source_static_contract_eligible_for_future_probe"]]
    eligible_accepted = [row for row in eligible if row["status"] == "accepted"]
    eligible_rejected = [row for row in eligible if row["status"] == "rejected"]
    assert len(eligible_accepted) == 3
    assert len(eligible_rejected) == 3
    assert {row["source"] for row in eligible} == {
        "MWORKS_live_downlink",
        "ROS2_runtime_echo",
        "MWORKS_ROS2_live_downlink",
    }
    assert {row["actual_runtime_transport_evidence"] for row in rows} == {False}
    assert {row["accepted_as_runtime_ack_now"] for row in rows} == {False}

    negative_rows = [
        row
        for row in rows
        if row["source"] in {
            "024_source_static_handoff",
            "025_compile_pass",
            "026_checker_success",
            "027_runtime_readiness_checker",
            "028_harness_prep_checker",
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
        }
    ]
    assert negative_rows
    assert all(not row["source_static_contract_eligible_for_future_probe"] for row in negative_rows)


def test_next_gate_requires_future_live_authorization_and_cleanup(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    next_gate = report["next_safe_runtime_gate"]
    assert "separate PMO-authorized single bounded live UE runtime" in next_gate["recommendation"]
    assert "028 does not authorize" in next_gate["blocked_now_reason"]
    assert {
        "runtime/editor probe explicitly authorized by PMO",
        "producer identity captured for MWORKS_live_downlink, ROS2_runtime_echo, or MWORKS_ROS2_live_downlink",
        "pending mosim.ue_command.v1 request captured before echo",
        "authoritative mosim.ue_command_echo.v1 echo captured from live transport",
        "run_id/request_id/seq/time_s/command kind/status match policy evaluated",
        "no_pose_overwrite_status=pass captured",
        "false-ack negative report rejects build/checker/sender/fixture/operator/frame rows",
        "timeout and cleanup manifest captured after one bounded attempt",
    } <= set(next_gate["minimum_acceptance_gates"])


def test_claim_boundary_forbids_runtime_ack_and_success_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    assert "source-static/runtime-probe harness preparation" in boundary
    assert "does not open Unreal Editor" in boundary
    assert "does not run Unreal build" in boundary
    assert "are not live runtime ack" in boundary
    assert "does not prove live UE runtime ack" in boundary
    assert "planner_ready" in boundary
    assert "controller performance" in boundary
    assert "mission success" in boundary
    assert "closed_loop" in boundary
    assert all(value is False for value in report["forbidden_runtime_claims"].values())
