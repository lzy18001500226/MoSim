from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_classic_controller_source_gate(tmp_path: Path) -> None:
    process = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts/control_platform/run_classic_controller_gate.py"),
            "--result-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    report = json.loads((tmp_path / "CLASSIC_CONTROLLER_SOURCE_GATE.json").read_text())
    assert report["status"] == "passed"
    assert report["controller_count"] == 5
    assert all(report["algorithm_identity_checks"].values())
