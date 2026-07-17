from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts" / "control_platform"
RUNNER = SOURCE_DIR / "run_enhancement_attitude_thrust_gate.py"


def test_enhancement_core_compiles_and_passes_gate(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    payload = json.loads((tmp_path / "P5_ENHANCEMENT_SOURCE_GATE.json").read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["controller_count"] == 6
    assert payload["failure_count"] == 0
    assert payload["fixed_size_state"] == {"ilc_phase_bins": 64, "axes": 3}
    assert set(payload["external_gate_decisions"]) == {
        "fuzzy_anfis_compensation",
        "rbf_nn_disturbance_compensation",
        "rl_gain_scheduling_residual_policy",
    }


def test_enhancement_core_uses_fixed_size_codegen_state() -> None:
    header = (SOURCE_DIR / "enhancement_attitude_thrust_core.h").read_text(encoding="utf-8")
    assert "MOSIM_ENHANCEMENT_ILC_BINS = 64" in header
    assert "double ilc_memory[MOSIM_ENHANCEMENT_ILC_BINS][3]" in header
    assert "malloc" not in (SOURCE_DIR / "enhancement_attitude_thrust_core.c").read_text(encoding="utf-8")
