from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_disabled_state_contract.py"


def run_checker(tmp_path: Path) -> dict[str, object]:
    output = tmp_path / "disabled_state_contract.json"
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


def test_disabled_state_checker_passes(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["ui_asset_binding_implemented"] is False
    assert report["runtime_receiver_implemented"] is False
    assert report["not_runtime_ue_console"] is True
    assert report["disabled_state_contract"]["runtime_ack_required_before_enablement"] is True  # type: ignore[index]


def test_required_control_categories_are_covered(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    categories = {row["category"]: row["command_kind"] for row in report["required_control_categories"]}  # type: ignore[index]
    assert categories == {
        "controller": "controller_select",
        "planner": "planner_select",
        "wind": "wind_profile",
        "fault": "motor_fault",
        "map_scene": "scene_switch",
    }


def test_pending_rows_remain_disabled(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    pending_rows = [row for row in report["fixture_matrix"] if row["ui_state"] == "pending"]  # type: ignore[index]
    assert len(pending_rows) == 5
    assert {row["control_display_state"] for row in pending_rows} == {"disabled_pending_echo"}
    assert {row["accepted_as_runtime_ack"] for row in pending_rows} == {False}


def test_non_live_sources_never_enable_runtime_controls(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    non_live_labels = set(report["non_live_source_labels"])  # type: ignore[arg-type]
    rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["echo_source"] in non_live_labels
    ]
    assert len(rows) == 20
    assert {row["quality_status"] for row in rows} == {"smoke_only"}
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}
    assert {row["control_display_state"] for row in rows} == {"disabled_smoke_or_preflight"}
    assert {row["must_remain_disabled"] for row in rows} == {True}


def test_rejected_rows_remain_disabled_even_with_future_live_source(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rejected_rows = [row for row in report["fixture_matrix"] if row["ui_state"] == "rejected"]  # type: ignore[index]
    assert len(rejected_rows) == 5
    assert {row["control_display_state"] for row in rejected_rows} == {"disabled_rejected"}
    assert {row["accepted_as_runtime_ack"] for row in rejected_rows} == {False}


def test_future_live_fixture_only_enables_after_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    live_source = report["future_live_source_fixture"]
    live_accepted_rows = [
        row
        for row in report["fixture_matrix"]  # type: ignore[index]
        if row["echo_source"] == live_source and row["ui_state"] == "accepted"
    ]
    assert len(live_accepted_rows) == 5
    assert {row["quality_status"] for row in live_accepted_rows} == {"runtime_echo_fixture"}
    assert {row["accepted_as_runtime_ack"] for row in live_accepted_rows} == {True}
    assert {row["control_display_state"] for row in live_accepted_rows} == {"enabled_after_runtime_echo"}


def test_no_forbidden_runtime_claims(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    forbidden_claims = report["forbidden_runtime_claims"]
    assert all(value is False for value in forbidden_claims.values())  # type: ignore[union-attr]
    assert report["matrix_summary"]["non_live_runtime_leaks"] == 0  # type: ignore[index]
