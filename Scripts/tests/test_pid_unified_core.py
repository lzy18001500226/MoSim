from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "control_platform" / "run_pid_unified_gate.py"


def test_pid_unified_core_golden_vector() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, capture_output=True, text=True
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["status"] in {"passed", "toolchain_blocked"}
    assert report["runtime_claim"] == "none"
    if report["status"] == "toolchain_blocked":
        assert report["source_contract"] == "present"
        assert report["next_gate"].startswith("compile_and_execute")


def test_pid_unified_core_declares_required_lifecycle_surface() -> None:
    header = (ROOT / "Scripts" / "control_platform" / "pid_unified_core.h").read_text(encoding="utf-8")
    source = (ROOT / "Scripts" / "control_platform" / "pid_unified_core.c").read_text(encoding="utf-8")
    for token in ("reset", "enable", "dt", "anti_windup_gain", "feedforward_gain",
                  "schedule_gain", "fuzzy_gain", "neural_residual_limit"):
        assert token in header
    for token in ("isfinite", "mosim_pid_reset", "clamp_value", "tanh"):
        assert token in source
    assert "mosim_pid_reset(&state->outer)" in source
    assert "mosim_pid_reset(&state->inner)" in source
