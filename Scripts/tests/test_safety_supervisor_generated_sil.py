from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/control_platform/run_safety_supervisor_generated_sil.py"


def test_p6_generated_code_matches_source(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(RUNNER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    report = json.loads((tmp_path / "P6_GENERATED_SIL_EQUIVALENCE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["mode_count"] == 7
    assert report["compared_columns_per_mode"] == 13
    assert report["max_abs_difference"] <= report["tolerance"]
