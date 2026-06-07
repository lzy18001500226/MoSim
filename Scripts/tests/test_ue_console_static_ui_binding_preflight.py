from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_static_ui_binding_preflight.py"


def run_checker(tmp_path: Path) -> dict[str, object]:
    output = tmp_path / "static_ui_binding_preflight.json"
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


def test_static_ui_binding_preflight_checker_passes(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["ui_binding_implemented"] is False
    assert report["accepted_state_controls_enabled"] is False
    assert report["runtime_receiver_implemented"] is False
    assert report["not_runtime_ue_console"] is True


def test_control_categories_include_required_ui_groups(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    categories = {row["category"]: row["command_kind"] for row in report["control_categories"]}  # type: ignore[index]
    assert categories == {
        "controller": "controller_select",
        "planner": "planner_select",
        "wind": "wind_profile",
        "fault": "motor_fault",
        "map_scene": "scene_switch",
        "reset": "scenario_reset",
        "recording": "recording",
    }


def test_pending_rows_remain_pending_disabled(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [row for row in report["fixture_matrix"] if row["row_name"] == "pending_request"]  # type: ignore[index]
    assert len(rows) == 7
    assert {row["ui_binding_preflight_state"] for row in rows} == {"pending_disabled"}
    assert {row["must_remain_pending_or_disabled"] for row in rows} == {True}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}


def test_smoke_source_rows_cannot_enable_ui(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    non_live = set(report["non_live_source_labels"])  # type: ignore[arg-type]
    rows = [row for row in report["fixture_matrix"] if row["source"] in non_live]  # type: ignore[index]
    assert len(rows) == 28
    assert {row["ui_binding_preflight_state"] for row in rows} == {"disabled_non_authoritative_or_invalid"}
    assert {row["must_remain_pending_or_disabled"] for row in rows} == {True}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}
    assert {row["actual_accepted_state_control_enabled"] for row in rows} == {False}


def test_sender_frames_fixtures_and_pose_failures_cannot_enable_ui(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    forbidden = set(report["forbidden_ack_sources"])  # type: ignore[arg-type]
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["source"] in forbidden or row["row_name"] == "no_pose_overwrite_failure"
    ]
    assert len(rows) == 56
    assert {row["ui_binding_preflight_state"] for row in rows} == {"disabled_non_authoritative_or_invalid"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}
    assert {row["must_remain_pending_or_disabled"] for row in rows} == {True}


def test_missing_runtime_identity_or_pending_match_cannot_enable_ui(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["row_name"] in {"missing_timestamp", "command_id_mismatch", "no_matching_pending"}
    ]
    assert len(rows) == 21
    assert {row["ui_binding_preflight_state"] for row in rows} == {"disabled_non_authoritative_or_invalid"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}


def test_rejected_authoritative_rows_stay_disabled(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [row for row in report["fixture_matrix"] if row["row_name"] == "authoritative_rejected"]  # type: ignore[index]
    assert len(rows) == 7
    assert {row["ui_binding_preflight_state"] for row in rows} == {"rejected_disabled"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}
    assert {row["must_remain_pending_or_disabled"] for row in rows} == {True}


def test_future_authoritative_rows_are_eligible_but_not_enabled(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["row_name"] == "valid_future_authoritative_live_echo"
    ]
    assert len(rows) == 7
    assert {row["ui_binding_preflight_state"] for row in rows} == {"eligible_after_future_live_echo"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {True}
    assert {row["actual_ui_binding_implemented"] for row in rows} == {False}
    assert {row["actual_accepted_state_control_enabled"] for row in rows} == {False}


def test_no_runtime_or_ui_enablement_leaks(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    summary = report["matrix_summary"]  # type: ignore[index]
    assert summary["actual_enabled_rows"] == 0
    assert summary["disabled_leaks"] == 0
    assert summary["runtime_ack_leaks"] == 0
    forbidden_claims = report["forbidden_runtime_claims"]
    assert all(value is False for value in forbidden_claims.values())  # type: ignore[union-attr]
