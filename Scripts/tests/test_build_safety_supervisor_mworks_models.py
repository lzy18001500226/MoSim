from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_safety_supervisor_mworks_models.py"


def test_builds_safety_bridge_and_seven_fixtures(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(BUILDER), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    manifest = json.loads((tmp_path / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    assert len(manifest["fixtures"]) == 7
    assert manifest["expected_actions"] == {
        "safety_filter": 1,
        "cbf": 1,
        "reference_governor": 1,
        "geofence": 1,
        "emergency_stop": 5,
        "return_and_land": 3,
        "failsafe_state_machine": 2,
    }
    bridge = (tmp_path / "models/MoSim_P6_SafetySupervisor_CFunction_Sysblock.mo").read_text(encoding="utf-8")
    for token in (
        "MosimSafetySupervisorStepScalar", "candidate_acceleration_x_in",
        "emergency_request_in", "active_constraints_out", "status_code_out",
    ):
        assert token in bridge
    for fixture in manifest["fixtures"].values():
        text = (tmp_path / "models" / f"{fixture}.mo").read_text(encoding="utf-8")
        assert "connect(" in text
        assert "SysplorerEmbeddedCoder.Sources.Constant" in text

    failsafe = (tmp_path / "models/MoSim_P6_FAILSAFE_STATE_MACHINE_MIL.mo").read_text(encoding="utf-8")
    assert "command_age_s_source(k=1.0)" in failsafe
    assert "emergency_request_source(k=0.0)" in failsafe
    assert "return_request_source(k=0.0)" in failsafe

    emergency = (tmp_path / "models/MoSim_P6_EMERGENCY_STOP_MIL.mo").read_text(encoding="utf-8")
    assert "emergency_request_source(k=1.0)" in emergency
    assert "command_age_s_source(k=0.0)" in emergency

    return_and_land = (tmp_path / "models/MoSim_P6_RETURN_AND_LAND_MIL.mo").read_text(encoding="utf-8")
    assert "return_request_source(k=1.0)" in return_and_land
    assert "emergency_request_source(k=0.0)" in return_and_land
