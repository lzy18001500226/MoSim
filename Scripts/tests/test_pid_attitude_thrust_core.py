from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
RUNNER = SOURCE_DIR / "run_pid_attitude_thrust_gate.py"


def test_attitude_thrust_gate_passes(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["status"] == "passed"
    assert report["case_count"] == 12
    assert report["lifecycle_fail_closed"] is True
    assert report["frame_contract"] == {
        "world": "ENU", "body": "FLU", "quaternion_order": "wxyz", "thrust_unit": "N"
    }
    assert report["runtime_started"] is False


def test_attitude_thrust_core_keeps_backend_mapping_outside_algorithm() -> None:
    header = (SOURCE_DIR / "pid_attitude_thrust_core.h").read_text(encoding="utf-8")
    source = (SOURCE_DIR / "pid_attitude_thrust_core.c").read_text(encoding="utf-8")
    for token in (
        "desired_attitude_enu_flu_wxyz",
        "desired_collective_thrust_n",
        "int algorithm_id",
        "reference_acceleration_enu_mps2",
        "MOSIM_PID_GAIN_SCHEDULED",
        "MOSIM_PID_FUZZY",
        "MOSIM_PID_NEURAL",
        "MOSIM_PID_ANTI_WINDUP",
        "MOSIM_PID_FEEDFORWARD_PROFILE",
    ):
        assert token in header
    for token in ("isfinite", "input->reset", "input->enable", "quat_from_columns", "tan(params->max_tilt_rad)"):
        assert token in source
    for forbidden in ("mavros", "ros::", "uORB", "normalized_thrust"):
        assert forbidden not in header
        assert forbidden not in source
