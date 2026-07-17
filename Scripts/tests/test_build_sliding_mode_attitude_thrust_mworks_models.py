from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_sliding_mode_attitude_thrust_mworks_models.py"


def test_builds_six_fixed_size_mil_fixtures(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(BUILDER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    manifest = json.loads((tmp_path / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    assert len(manifest["fixtures"]) == 6
    assert set(manifest["feature_output"]) == set(manifest["fixtures"])
    assert manifest["neural_smc"] == {"decision": "deferred", "selectable": False}
    bridge = Path(manifest["bridge_path"]).read_text(encoding="utf-8")
    assert "MosimSlidingModeStepScalar" in bridge
    assert "static MosimSlidingModeState states[7]" in bridge
    assert "mosim_sliding_mode_step" in bridge
    for output in manifest["outputs"]:
        assert f" {output}_out" in bridge
    for algorithm, fixture in manifest["fixtures"].items():
        text = (tmp_path / "models" / f"{fixture}.mo").read_text(encoding="utf-8")
        assert "MoSim_P3_SlidingMode_CFunction_Sysblock controller" in text
        assert f"controller_id_source(k={float(list(manifest['fixtures']).index(algorithm) + 1)})" in text
        assert manifest["feature_output"][algorithm] in text
