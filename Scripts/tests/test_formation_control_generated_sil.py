import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_official_generated_formation_c_matches_source(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "Scripts/control_platform/run_formation_control_generated_sil.py"), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((tmp_path / "P8_GENERATED_SIL_EQUIVALENCE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["mode_count"] == 9
    assert report["compared_columns_per_mode"] == 25
    assert report["max_abs_difference"] <= report["tolerance"]
