from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/control_platform/run_learning_generated_sil.py"


def test_learning_generated_sil(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads((tmp_path / "P9_GENERATED_SIL_EQUIVALENCE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["route_count"] == 2
    assert report["max_abs_difference"] <= 1.0e-12
    assert report["official_codegen"] == "MWORKS GenerateModelCode"
