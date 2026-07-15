from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "control_platform" / "run_wave_b_hinf_gate.py"


def test_wave_b_hinf_matches_frozen_gain_oracle(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads((tmp_path / "G5_WAVE_B_HINF_GATE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["failure_count"] == 0
    assert report["selectable"] is False
    assert report["max_closed_loop_real_eigenvalue"] < 0.0
