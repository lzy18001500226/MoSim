from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = ROOT / "Scripts" / "quality" / "evaluate_gazebo_hover_bracket.py"
RUNNER = ROOT / "Scripts" / "gazebo" / "run_sunray150_hover_command_bracket.sh"
SCENARIO = ROOT / "Config" / "scenarios" / "system" / "sunray150_gazebo_ros2_smoke.yaml"


def project_tmp_root(name: str) -> Path:
    root = ROOT / "Results" / "tmp" / "test_gazebo_hover_bracket" / f"{name}_{uuid.uuid4().hex}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_sample(root: Path, command: float, *, z_delta: float, max_z: float, max_3d: float, plant_passed: bool) -> None:
    sample_dir = root / f"cmd_{command:.6f}".replace(".", "p")
    sample_dir.mkdir(parents=True, exist_ok=True)
    command_values = [command, command, command, command]
    velocity = [command * 8000.0] * 4
    (sample_dir / "controller_output_fixture.json").write_text(
        json.dumps({"status": "published", "command": command_values}, ensure_ascii=False),
        encoding="utf-8",
    )
    (sample_dir / "controller_output_adapter_node.json").write_text(
        json.dumps({"status": "published", "velocity": velocity}, ensure_ascii=False),
        encoding="utf-8",
    )
    (sample_dir / "GAZEBO_PLANT_RESPONSE_EVAL.json").write_text(
        json.dumps(
            {
                "status": "passed" if plant_passed else "blocked",
                "gate_passed": plant_passed,
                "blockers": [] if plant_passed else ["plant_z_response_below_min"],
                "truth_recording": {
                    "valid_sample_count": 100,
                    "duration_s": 4.0,
                },
                "plant_response": {
                    "z_delta_m": z_delta,
                    "max_z_delta_m": max_z,
                    "max_3d_delta_m": max_3d,
                    "xy_delta_m": 0.0,
                    "early_z_range_m": 0.001,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (sample_dir / "RUNTIME_STATUS.json").write_text(
        json.dumps(
            {
                "status": "runtime_smoke_passed" if plant_passed else "runtime_smoke_blocked",
                "gate_passed": plant_passed,
                "blockers": [] if plant_passed else ["plant_response_gate_not_passed"],
                "plant_response_pre_acceptance": {
                    "truth_recording_recorded": True,
                    "eval_recorded": True,
                },
                "actuator_command": {
                    "ros_velocity_matches_expected": True,
                    "gz_velocity_matches_expected": True,
                    "ros_echo": {"sample_recorded": True},
                    "gz_echo": {"sample_recorded": True},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_hover_bracket_accepts_under_near_and_over_samples() -> None:
    result_root = project_tmp_root("accepts")
    write_sample(result_root, 0.04, z_delta=0.01, max_z=0.02, max_3d=0.02, plant_passed=False)
    write_sample(result_root, 0.055, z_delta=0.08, max_z=0.12, max_3d=0.2, plant_passed=True)
    write_sample(result_root, 0.065, z_delta=2.5, max_z=2.8, max_3d=3.0, plant_passed=True)
    output = result_root / "GAZEBO_HOVER_COMMAND_BRACKET_EVAL.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--scenario",
            str(SCENARIO),
            "--result-root",
            str(result_root),
            "--output-json",
            str(output),
            "--commands",
            "0.04",
            "0.055",
            "0.065",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["class_counts"]["under_thrust"] == 1
    assert report["class_counts"]["near_hover_candidate"] == 1
    assert report["class_counts"]["over_climb"] == 1
    assert report["selected_near_hover_candidate"]["command"] == 0.055
    assert "closed_loop" in " ".join(report["claim_boundary"])


def test_hover_bracket_blocks_missing_evidence() -> None:
    result_root = project_tmp_root("blocks")
    write_sample(result_root, 0.055, z_delta=0.08, max_z=0.12, max_3d=0.2, plant_passed=True)
    (result_root / "cmd_0p055000" / "controller_output_adapter_node.json").write_text(
        json.dumps({"status": "blocked"}, ensure_ascii=False),
        encoding="utf-8",
    )
    output = result_root / "GAZEBO_HOVER_COMMAND_BRACKET_EVAL.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--scenario",
            str(SCENARIO),
            "--result-root",
            str(result_root),
            "--output-json",
            str(output),
            "--commands",
            "0.055",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert "invalid_sample_evidence:0.055" in report["blockers"]


def test_hover_bracket_runner_uses_paused_free_flight_gate() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "RUNTIME_GATE_PROFILE=single_uav_hover_command_bracket" in text
    assert 'START_GAZEBO_PAUSED="${START_GAZEBO_PAUSED:-1}"' in text
    assert 'UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND="${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND:-1}"' in text
