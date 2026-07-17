from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_linear_robust_attitude_thrust_mworks_models.py"


def test_builder_emits_bridge_and_four_fixtures(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(BUILDER), "--result-dir", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    models = tmp_path / "models"
    bridge = (models / "MoSim_P2_LinearRobust_CFunction_Sysblock.mo").read_text(encoding="utf-8")
    assert "MosimLinearRobustStepScalar" in bridge
    assert "max_tilt_rad_in" in bridge
    assert "storage_function_out" in bridge
    for algorithm in ("LQG", "FEEDBACK_LINEARIZATION", "PASSIVITY_BASED_CONTROL", "ADAPTIVE_BACKSTEPPING"):
        fixture = (models / f"MoSim_P2_{algorithm}_MIL.mo").read_text(encoding="utf-8")
        assert "connect(controller.normalized_thrust_out, normalized_thrust);" in fixture
        assert "StopTime=0.2" in fixture
