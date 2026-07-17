from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/control_platform/run_sliding_mode_attitude_thrust_gate.py"


def test_sliding_mode_source_gate(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    report = json.loads((tmp_path / "P3_SLIDING_MODE_SOURCE_GATE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["case_count"] == 6
    assert report["lifecycle_case_count"] == 6
    assert report["failure_count"] == 0
    assert report["neural_smc"]["decision"] == "deferred"
    assert report["neural_smc"]["selectable"] is False


def test_core_has_distinct_stateful_variants_and_fail_closed_paths() -> None:
    core = (ROOT / "Scripts/control_platform/sliding_mode_attitude_thrust_core.c").read_text(encoding="utf-8")
    assert "position_error_integral" in core
    assert "super_twisting_integral" in core
    assert "adaptive_reaching_gain" in core
    assert "MOSIM_SMC_NONSINGULAR_TERMINAL" in core
    assert "MOSIM_SMC_FUZZY" in core
    assert "output->status_code = -3" in core
    assert "params_valid" in core
