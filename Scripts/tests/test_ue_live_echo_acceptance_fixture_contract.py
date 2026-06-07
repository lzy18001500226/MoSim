from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_live_echo_acceptance_fixture_contract.py"
DISABLED_CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_console_disabled_state_contract.py"


def run_checker(tmp_path: Path) -> dict[str, object]:
    output = tmp_path / "live_echo_acceptance_fixture_contract.json"
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


def test_live_echo_acceptance_fixture_checker_passes(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["ui_asset_binding_implemented"] is False
    assert report["runtime_receiver_implemented"] is False
    assert report["not_runtime_ue_console"] is True
    assert report["fixture_summary"]["valid_future_live_accepted_rows"] == 5  # type: ignore[index]


def test_accepted_runtime_fixture_requires_authoritative_source_and_fields(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    contract = report["accepted_state_fixture_contract"]  # type: ignore[index]
    assert contract["required_fields_for_runtime_accepted"] == [  # type: ignore[index]
        "schema",
        "source",
        "status",
        "run_id",
        "request_id",
        "seq",
        "time_s",
        "ack_authority",
        "no_pose_overwrite_status",
        "command.kind",
    ]
    assert contract["authoritative_live_sources"] == {  # type: ignore[index]
        "MWORKS_live_downlink": "MWORKS",
        "ROS2_runtime_echo": "ROS2",
        "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
    }
    accepted_rows = [
        row
        for row in report["fixture_rows"]  # type: ignore[index]
        if row["valid_future_live_fixture"] and row["status"] == "accepted"
    ]
    assert len(accepted_rows) == 5
    assert {row["has_authoritative_source"] for row in accepted_rows} == {True}
    assert {row["has_command_id"] for row in accepted_rows} == {True}
    assert {row["has_timestamp"] for row in accepted_rows} == {True}
    assert {row["has_status"] for row in accepted_rows} == {True}
    assert {row["accepted_as_runtime_ack"] for row in accepted_rows} == {True}
    assert {row["control_display_state"] for row in accepted_rows} == {"enabled_after_runtime_echo"}


def test_smoke_preflight_source_rows_cannot_be_runtime_accepted(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    non_live = set(report["non_live_source_labels"])  # type: ignore[arg-type]
    rows = [row for row in report["fixture_rows"] if row["source"] in non_live]  # type: ignore[index]
    assert len(rows) == 4
    assert {row["accepted_as_runtime_ack"] for row in rows} == {False}
    assert {row["quality_status"] for row in rows} == {"smoke_only"}
    assert {row["must_remain_disabled"] for row in rows} == {True}
    assert report["fixture_summary"]["non_live_runtime_leaks"] == 0  # type: ignore[index]


def test_missing_or_mismatched_future_live_fields_do_not_enable_controls(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = {row["name"]: row for row in report["fixture_rows"]}  # type: ignore[index]
    for name in ["authority_mismatch", "missing_timestamp", "missing_command_id", "missing_status"]:
        assert rows[name]["accepted_as_runtime_ack"] is False
        assert rows[name]["control_display_state"] == "disabled_smoke_or_invalid_fixture"
        assert rows[name]["must_remain_disabled"] is True
    assert rows["authority_mismatch"]["has_authoritative_source"] is False
    assert "time_s" in rows["missing_timestamp"]["missing_required_fields"]
    assert "request_id" in rows["missing_command_id"]["missing_required_fields"]
    assert "status" in rows["missing_status"]["missing_required_fields"]


def test_rejected_future_live_fixture_stays_disabled(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = {row["name"]: row for row in report["fixture_rows"]}  # type: ignore[index]
    rejected = rows["rejected_future_live"]
    assert rejected["valid_future_live_fixture"] is True
    assert rejected["accepted_as_runtime_ack"] is False
    assert rejected["control_display_state"] == "disabled_rejected"
    assert rejected["must_remain_disabled"] is True


def test_disabled_state_contract_007_still_holds(tmp_path: Path) -> None:
    output = tmp_path / "disabled_state_contract.json"
    completed = subprocess.run(
        [sys.executable, str(DISABLED_CHECKER), "--output-json", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["matrix_summary"]["non_live_runtime_leaks"] == 0
