from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_mpc_attitude_thrust_mworks_models.py"


def test_builds_seven_fixed_size_mil_fixtures(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(BUILDER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    manifest = json.loads((tmp_path / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    assert len(manifest["fixtures"]) == 7
    assert manifest["deferred"] == ["learning_mpc", "distributed_mpc"]
    bridge = Path(manifest["bridge_path"]).read_text(encoding="utf-8")
    assert "MosimMpcStepScalar" in bridge
    assert "static MosimMpcState states[8]" in bridge
    assert "static unsigned char initialized[8]" in bridge
    assert "mosim_mpc_reset(&states[id])" in bridge
    assert "mosim_mpc_step" in bridge
    for output in manifest["outputs"]:
        assert f" {output}_out" in bridge
    for fixture_name in manifest["fixtures"].values():
        fixture = (tmp_path / "models" / f"{fixture_name}.mo").read_text(encoding="utf-8")
        assert "StopTime=0.2" in fixture
