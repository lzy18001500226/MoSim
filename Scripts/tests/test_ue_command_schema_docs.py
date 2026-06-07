from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_p0_slice_run_manifest.py"
COMMAND_SCHEMA = ROOT / "Config" / "schemas" / "mosim_ue_command_v1.schema.json"
ECHO_SCHEMA = ROOT / "Config" / "schemas" / "mosim_ue_command_echo_v1.schema.json"


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_ue_command_schema_documents_current_adapter_contract() -> None:
    command_schema = read_json(COMMAND_SCHEMA)
    echo_schema = read_json(ECHO_SCHEMA)
    allowed = set(command_schema["command"]["allowed_kinds"])  # type: ignore[index]
    forbidden = set(command_schema["command"]["forbidden_kinds"])  # type: ignore[index]
    assert {"controller_select", "planner_select", "motor_fault", "wind_profile", "sensor_mode", "scene_switch"} <= allowed
    assert {"teleport", "pose_override", "keyboard_pose"} <= forbidden
    assert command_schema["required_values"]["schema"] == "mosim.ue_command.v1"  # type: ignore[index]
    assert echo_schema["required_values"]["no_pose_overwrite_status"] == "pass"  # type: ignore[index]
    assert {"MWORKS", "ROS2", "MWORKS_ROS2"} == set(echo_schema["ack_authority_values"])  # type: ignore[index]
    assert "offline_adapter_smoke" in "\n".join(echo_schema["evidence_boundary"])  # type: ignore[index]


def test_generated_p0_ue_command_and_echo_rows_match_documented_schema(tmp_path: Path) -> None:
    del tmp_path
    output_dir = ROOT / "Results" / "tmp" / f"p0_schema_docs_{uuid4().hex}"
    completed = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--run-id",
            "test_p0_schema_docs",
            "--output-dir",
            str(output_dir),
            "--validate",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    command_schema = read_json(COMMAND_SCHEMA)
    echo_schema = read_json(ECHO_SCHEMA)
    allowed = set(command_schema["command"]["allowed_kinds"])  # type: ignore[index]
    forbidden = set(command_schema["command"]["forbidden_kinds"])  # type: ignore[index]
    command_rows = [json.loads(line) for line in (output_dir / "ue_command_input_smoke.jsonl").read_text(encoding="utf-8").splitlines()]
    echo_rows = [json.loads(line) for line in (output_dir / "ue_command_echo_smoke.jsonl").read_text(encoding="utf-8").splitlines()]
    sender_contract = read_json(output_dir / "ue_command_sender_source_contract.json")

    assert command_rows
    for row in command_rows:
        assert row["schema"] == command_schema["required_values"]["schema"]  # type: ignore[index]
        assert row["type"] == "command"
        assert row["guard"]["require_mworks_ack"] is True
        kind = row["command"]["kind"]
        assert kind in allowed or kind in forbidden
        if kind == "planner_select":
            assert row["guard"]["require_ros2_ack"] is True

    assert echo_rows
    assert {row["status"] for row in echo_rows} == {"accepted", "rejected"}
    for row in echo_rows:
        assert row["schema"] == echo_schema["schema"]
        assert row["ack_authority"] in echo_schema["ack_authority_values"]
        assert row["no_pose_overwrite_status"] == "pass"
        if row["command"]["kind"] in forbidden:
            assert row["status"] == "rejected"
            assert row["reason"] in echo_schema["valid_rejection_reasons_for_forbidden_kinds"]
    assert sender_contract["ok"] is True
    assert sender_contract["not_runtime_ue_console"] is True
    assert sender_contract["runtime_ack_required_before_acceptance"] is True
