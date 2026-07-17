from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_enhancement_attitude_thrust_mworks_models.py"


def test_builds_bridge_and_six_mil_fixtures(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(BUILDER), "--result-dir", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    manifest = json.loads((tmp_path / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    assert len(manifest["fixtures"]) == 6
    assert manifest["fixed_size_state"] == {"ilc_phase_bins": 64, "axes": 3}
    bridge = (tmp_path / "models/MoSim_P5_Enhancement_CFunction_Sysblock.mo").read_text(encoding="utf-8")
    assert "MosimEnhancementStepScalar" in bridge
    assert "measured_acceleration_x_in" in bridge
    assert "trajectory_phase_bin_in" in bridge
    assert "repeat_complete_in" in bridge
    assert "compensation_x_out" in bridge
    for fixture in manifest["fixtures"].values():
        text = (tmp_path / "models" / f"{fixture}.mo").read_text(encoding="utf-8")
        assert "connect(" in text
        assert "SysplorerEmbeddedCoder.Sources.Constant" in text
