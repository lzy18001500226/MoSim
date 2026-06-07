from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_receiver_shell_static_contract.py"


def run_checker(tmp_path: Path) -> dict[str, object]:
    output = tmp_path / "receiver_shell_static_contract.json"
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


def test_receiver_shell_checker_passes_without_runtime_receiver(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["checker_only_contract"] is True
    assert report["receiver_shell_cpp_implemented"] is False
    assert report["runtime_receiver_implemented"] is False
    assert report["safe_to_implement_runtime_receiver_next"] is False
    assert report["ui_accepted_state_controls_enabled"] is False
    assert report["not_live_runtime_evidence"] is True


def test_future_receiver_boundary_and_sink_are_fixed(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    contract = report["future_receiver_shell_contract"]  # type: ignore[index]
    assert contract["recommended_component_name"] == "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent"
    assert contract["input_schema"] == "mosim.ue_command_echo.v1"
    assert (
        contract["single_state_sink"]
        == "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
    )
    assert "UQuadrotorMworksUdpReceiverComponent" in contract["must_remain_separate_from"]
    assert "UQuadrotorMworksUdpCommandSenderComponent" in contract["must_remain_separate_from"]


def test_state_component_is_the_only_command_echo_sink_anchor(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    anchors = report["source_anchor_summary"]  # type: ignore[index]
    state = anchors["state_component"]
    frame_receiver = anchors["frame_status_receiver"]
    sender = anchors["command_sender"]
    assert state["has_pending_method"] is True
    assert state["has_echo_sink"] is True
    assert state["has_echo_schema_guard"] is True
    assert state["has_command_schema_guard"] is True
    assert state["forbidden_pose_patterns_present"] == []
    assert frame_receiver["has_frame_schema_guard"] is True
    assert frame_receiver["uses_fudp_socket_receiver"] is True
    assert frame_receiver["parses_command_echo_schema"] is False
    assert frame_receiver["calls_echo_sink"] is False
    assert sender["has_command_schema"] is True
    assert sender["has_send_success_anchor"] is True
    assert sender["send_success_is_ack"] is False
    assert sender["parses_command_echo_schema"] is False
    assert sender["calls_echo_sink"] is False


def test_non_live_labels_stay_smoke_only_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    contract = report["future_receiver_shell_contract"]  # type: ignore[index]
    assert contract["non_live_source_labels"] == [
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
        "offline_adapter_smoke",
        "source_level_smoke",
    ]
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["source"] in set(contract["non_live_source_labels"])
    ]
    assert len(rows) == 4
    assert {row["receiver_shell_policy"] for row in rows} == {"do_not_sink_as_live_ack"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}


def test_sender_frames_fixtures_and_no_pose_failures_are_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["source"] in set(report["future_receiver_shell_contract"]["forbidden_ack_sources"])  # type: ignore[index]
        or row["row_name"] in {"quadrotor_unreal_state_frame", "no_pose_overwrite_failure"}
    ]
    assert rows
    assert {row["receiver_shell_policy"] for row in rows} == {"do_not_sink_as_live_ack"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}
    assert {row["actual_runtime_receiver_implemented"] for row in rows} == {False}
    assert {row["actual_sink_called_by_receiver"] for row in rows} == {False}


def test_missing_identity_pending_match_and_wrong_authority_are_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["row_name"]
        in {
            "missing_command_id",
            "missing_timestamp",
            "no_matching_pending",
            "command_id_mismatch",
            "wrong_authority_for_source",
        }
    ]
    assert len(rows) == 5
    assert {row["receiver_shell_policy"] for row in rows} == {"do_not_sink_as_live_ack"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}


def test_rejected_authoritative_echo_does_not_mark_runtime_accepted(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [row for row in report["fixture_matrix"] if row["row_name"] == "authoritative_rejected"]  # type: ignore[index]
    assert len(rows) == 1
    assert rows[0]["receiver_shell_policy"] == "do_not_mark_runtime_accepted_rejected_echo"
    assert rows[0]["accepted_as_runtime_ack"] is False


def test_future_authoritative_rows_are_eligible_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["row_name"].startswith("valid_future_")
    ]
    assert len(rows) == 3
    assert {row["receiver_shell_policy"] for row in rows} == {
        "future_sink_eligible_after_runtime_receiver_exists"
    }
    assert {row["eligible_for_future_receiver_sink"] for row in rows} == {True}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {True}
    assert {row["actual_runtime_receiver_implemented"] for row in rows} == {False}
    assert {row["actual_sink_called_by_receiver"] for row in rows} == {False}


def test_no_forbidden_runtime_claims_or_matrix_leaks(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    summary = report["matrix_summary"]  # type: ignore[index]
    assert summary["future_authoritative_live_eligible_rows"] == 3
    assert summary["runtime_ack_leaks"] == 0
    assert summary["actual_receiver_sink_leaks"] == 0
    forbidden_claims = report["forbidden_runtime_claims"]
    assert all(value is False for value in forbidden_claims.values())  # type: ignore[union-attr]
