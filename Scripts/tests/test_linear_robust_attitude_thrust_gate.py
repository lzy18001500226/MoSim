from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/control_platform/run_linear_robust_attitude_thrust_gate.py"


def test_linear_robust_source_gate(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    report = json.loads((tmp_path / "P2_LINEAR_ROBUST_SOURCE_GATE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["case_count"] == 4
    assert report["lifecycle_case_count"] == 7
    assert all(item["passed"] for item in report["lifecycle_checks"].values())
    assert report["failure_count"] == 0
    assert report["command_contract"] == "ATTITUDE_THRUST"


def test_core_has_explicit_estimator_adaptation_and_fail_closed_paths() -> None:
    core = (ROOT / "Scripts/control_platform/linear_robust_attitude_thrust_core.c").read_text(encoding="utf-8")
    assert "observer_initialized" in core
    assert "adaptive_disturbance" in core
    assert "storage_function" in core
    assert "output->status_code = -3" in core
    assert "quaternion_from_rotation" in core
    assert "params_valid" in core
    assert "tan(params->max_tilt_rad)" in core
