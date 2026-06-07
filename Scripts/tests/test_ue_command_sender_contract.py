from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_command_sender_contract.py"
LOOPBACK = ROOT / "Scripts" / "UE5" / "smoke_ue_command_sender_loopback.py"


def test_ue_command_sender_source_contract() -> None:
    completed = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["source"] == "source_level_static_check"
    assert report["not_runtime_ue_console"] is True
    assert report["runtime_ack_required_before_acceptance"] is True
    assert report["no_pose_overwrite_status"] == "pass"
    assert "teleport" in report["forbidden_kinds"]
    assert "controller_select" in report["allowed_kinds"]


def test_ue_command_sender_udp_loopback_smoke(tmp_path: Path) -> None:
    summary = tmp_path / "summary.json"
    received = tmp_path / "received.jsonl"
    completed = subprocess.run(
        [
            sys.executable,
            str(LOOPBACK),
            "--summary-output",
            str(summary),
            "--received-output",
            str(received),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["source"] == "udp_loopback_smoke"
    assert payload["sent_packets"] == 4
    assert payload["received_packets"] == 4
    assert payload["no_pose_overwrite_status"] == "pass"
    assert payload["not_runtime_ue_console"] is True
    assert payload["not_mworks_or_ros2_ack"] is True
    rows = [json.loads(line) for line in received.read_text(encoding="utf-8").splitlines()]
    assert {row["command"]["kind"] for row in rows} == {
        "controller_select",
        "planner_select",
        "motor_fault",
        "scene_switch",
    }
    assert all(row["guard"]["require_mworks_ack"] is True for row in rows)
