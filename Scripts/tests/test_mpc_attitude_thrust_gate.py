from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/control_platform/run_mpc_attitude_thrust_gate.py"


def test_mpc_source_gate(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    report = json.loads((tmp_path / "P4_MPC_SOURCE_GATE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["case_count"] == 7
    assert report["lifecycle_case_count"] == 6
    assert report["failure_count"] == 0
    assert report["fixed_budget"] == {"ilqr_iterations": 5, "mppi_samples": 7}
    assert report["external_gate_decisions"]["learning_mpc"]["selectable"] is False
    assert report["external_gate_decisions"]["distributed_mpc"]["selectable"] is False


def test_core_has_fixed_budget_and_fail_closed_paths() -> None:
    core = (ROOT / "Scripts/control_platform/mpc_attitude_thrust_core.c").read_text(encoding="utf-8")
    assert "for (iteration = 0; iteration < 5; ++iteration)" in core
    assert "static const double samples[7]" in core
    assert "MOSIM_MPC_TUBE" in core
    assert "MOSIM_MPC_EXPLICIT_GAIN_SCHEDULED" in core
    assert "output->status_code = -3" in core
    assert "params_valid" in core
