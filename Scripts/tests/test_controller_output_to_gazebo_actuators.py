from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Scripts" / "ros" / "controller_output_to_gazebo_actuators.py"
NODE = ROOT / "Scripts" / "ros" / "controller_output_to_gazebo_actuators_node.py"
FIXTURE = ROOT / "Scripts" / "ros" / "publish_controller_output_fixture.py"
MSG = ROOT / "Scripts" / "ros" / "mosim_msgs" / "msg" / "ControllerOutput.msg"
CMAKELISTS = ROOT / "Scripts" / "ros" / "mosim_msgs" / "CMakeLists.txt"


def run_adapter(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ADAPTER), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_script(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_controller_output_msg_is_registered() -> None:
    msg_text = MSG.read_text(encoding="utf-8")
    assert "std_msgs/Header header" in msg_text
    assert "string command_type" in msg_text
    assert "float64[] command" in msg_text
    assert "string backend" in msg_text
    assert '"msg/ControllerOutput.msg"' in CMAKELISTS.read_text(encoding="utf-8")


def test_controller_output_node_dry_run_declares_bounded_handoff() -> None:
    completed = run_script(NODE, "--dry-run")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["status"] == "ready"
    assert report["input_type"] == "mosim_msgs/msg/ControllerOutput"
    assert report["output_type"] == "actuator_msgs/msg/Actuators"
    assert report["input_topic"] == "/mosim/sunray150/controller_output"
    assert report["output_topic"] == "/sunray150/gazebo/command/motor_speed"
    assert report["actuator_order"] == ["rotor_0", "rotor_1", "rotor_2", "rotor_3"]
    assert "closed_loop" in " ".join(report["claim_boundary"])


def test_controller_output_fixture_dry_run_declares_fixture_scope() -> None:
    completed = run_script(FIXTURE, "--dry-run")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["status"] == "dry_run_ready"
    assert report["topic"] == "/mosim/sunray150/controller_output"
    assert report["type"] == "mosim_msgs/msg/ControllerOutput"
    assert report["command_type"] == "normalized_motor_speed"
    assert report["command"] == [0.5, 0.5, 0.5, 0.5]
    assert "bounded fixture" in " ".join(report["claim_boundary"])


def test_normalized_motor_speed_maps_to_gazebo_velocity() -> None:
    completed = run_adapter("--command", "0.5", "0.5", "0.5", "0.5")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["status"] == "actuator_payload_ready"
    assert report["input_contract"] == "mosim_msgs/msg/ControllerOutput"
    assert report["ros_type"] == "actuator_msgs/msg/Actuators"
    assert report["gz_type"] == "gz.msgs.Actuators"
    assert report["velocity"] == [4000.0, 4000.0, 4000.0, 4000.0]
    assert report["ros_message"]["velocity"] == [4000.0, 4000.0, 4000.0, 4000.0]
    assert report["ros_cli_yaml"] == "{position: [], velocity: [4000, 4000, 4000, 4000], normalized: []}"
    assert report["actuator_order"] == ["rotor_0", "rotor_1", "rotor_2", "rotor_3"]
    assert report["mworks_spin_command_sign"] == [1, 1, -1, -1]
    assert report["gazebo_turning_direction"] == ["ccw", "ccw", "cw", "cw"]
    assert any("only builds a ROS2/Gazebo Actuators payload" in item for item in report["claim_boundary"])


def test_adapter_accepts_fresh_metadata_guard(tmp_path: Path) -> None:
    fixture = tmp_path / "fresh_controller_output.json"
    fixture.write_text(
        json.dumps(
            {
                "sequence": 7,
                "vehicle_id": "sunray150",
                "command_type": "normalized_motor_speed",
                "command": [0.5, 0.5, 0.5, 0.5],
                "status": "valid",
                "source_authority": "bounded_fixture_no_flight_authority",
                "issued_at_unix": 100.0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    completed = run_adapter(
        "--input-json",
        str(fixture),
        "--expected-vehicle-id",
        "sunray150",
        "--required-status",
        "valid",
        "--max-command-age-s",
        "2.0",
        "--now-unix",
        "101.0",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["sequence"] == 7
    assert report["command_age_s"] == 1.0
    assert report["metadata_policy"]["age_checked"] is True


def test_adapter_blocks_stale_metadata_guard(tmp_path: Path) -> None:
    fixture = tmp_path / "stale_controller_output.json"
    fixture.write_text(
        json.dumps(
            {
                "vehicle_id": "sunray150",
                "command_type": "normalized_motor_speed",
                "command": [0.5, 0.5, 0.5, 0.5],
                "status": "valid",
                "issued_at_unix": 90.0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    completed = run_adapter(
        "--input-json",
        str(fixture),
        "--expected-vehicle-id",
        "sunray150",
        "--required-status",
        "valid",
        "--max-command-age-s",
        "2.0",
        "--now-unix",
        "100.0",
    )
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["status"] == "blocked"
    assert "exceeds max_command_age_s" in report["error"]


def test_adapter_blocks_wrong_vehicle_and_status(tmp_path: Path) -> None:
    fixture = tmp_path / "wrong_vehicle_controller_output.json"
    fixture.write_text(
        json.dumps(
            {
                "vehicle_id": "uav2",
                "command_type": "normalized_motor_speed",
                "command": [0.5, 0.5, 0.5, 0.5],
                "status": "valid",
                "issued_at_unix": 100.0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    completed = run_adapter("--input-json", str(fixture), "--expected-vehicle-id", "sunray150")
    assert completed.returncode == 1
    assert "does not match expected_vehicle_id" in json.loads(completed.stdout)["error"]

    fixture.write_text(
        json.dumps(
            {
                "vehicle_id": "sunray150",
                "command_type": "normalized_motor_speed",
                "command": [0.5, 0.5, 0.5, 0.5],
                "status": "stale",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    completed = run_adapter("--input-json", str(fixture), "--required-status", "valid")
    assert completed.returncode == 1
    assert "does not match required_status" in json.loads(completed.stdout)["error"]


def test_signed_mworks_visual_motor_speed_maps_to_magnitude(tmp_path: Path) -> None:
    fixture = tmp_path / "controller_output.json"
    fixture.write_text(
        json.dumps(
            {
                "vehicle_id": "sunray150",
                "command_type": "mworks_signed_visual_motor_speed",
                "command": [1200.0, 1200.0, -1200.0, -1200.0],
                "mode": "normal",
                "status": "valid",
                "backend": "mworks_equation",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    completed = run_adapter("--input-json", str(fixture))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["input_command_type"] == "mworks_signed_visual_motor_speed"
    assert report["velocity"] == [1200.0, 1200.0, 1200.0, 1200.0]
    assert report["signed_speed_policy"] == "magnitude_after_spin_sign_validation"


def test_signed_mworks_visual_motor_speed_blocks_wrong_sign(tmp_path: Path) -> None:
    fixture = tmp_path / "controller_output_bad_sign.json"
    fixture.write_text(
        json.dumps(
            {
                "command_type": "mworks_signed_visual_motor_speed",
                "command": [1200.0, -1200.0, -1200.0, -1200.0],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    completed = run_adapter("--input-json", str(fixture))
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["status"] == "blocked"
    assert "sign does not match spin convention" in report["error"]


def test_adapter_blocks_nonfinite_and_wrong_length() -> None:
    completed = run_adapter("--command", "0.5", "nan", "0.5", "0.5")
    assert completed.returncode == 1
    assert "not finite" in json.loads(completed.stdout)["error"]

    completed = run_adapter("--command", "0.5", "0.5", "0.5")
    assert completed.returncode == 1
    assert "does not match actuator_count" in json.loads(completed.stdout)["error"]


def test_adapter_blocks_over_max_motor_speed() -> None:
    completed = run_adapter("--command-type", "motor_speed", "--command", "1", "2", "3", "9000")
    assert completed.returncode == 1
    assert "exceeds max_rot_velocity" in json.loads(completed.stdout)["error"]
