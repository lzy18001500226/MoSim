from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "run_official_pid_sysblock_seven_scenarios.py"
SPEC = importlib.util.spec_from_file_location("native_sysblock_seven_scenarios", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_native_sysblock_harness_uses_golden_runner_not_formal_runner() -> None:
    profiles, _, _ = MODULE.read_profiles(MODULE.PROFILE_PATH)
    case = MODULE.Case(profile=profiles[0], result_root=ROOT / "Results" / "test_native_sysblock")

    harness = MODULE.render_harness(case)

    assert "Golden.OfficialPidSysblockSingleUavRunner" in harness
    assert "Formal.OfficialPidFormalRunner" not in harness
    assert "injection_gust_force_N = plant.gust.force" in harness
    assert "injection_fault_effectiveness" in harness


def test_native_sysblock_runner_keeps_native_result_and_avoids_gui_reset() -> None:
    profiles, _, _ = MODULE.read_profiles(MODULE.PROFILE_PATH)
    case = MODULE.Case(profile=profiles[4], result_root=ROOT / "Results" / "test_native_sysblock")

    arguments = MODULE.runner_arguments(case, timeout_s=240.0)

    assert "--no-gui-open" in arguments
    assert "--no-gui-result-viewer" not in arguments
    assert "--gui-reset-windows" not in arguments
    assert "x=position[1]" in arguments
    assert "plant_gust_force_x_N=injection_gust_force_N[1]" in arguments


def test_dry_run_matrix_is_planned_instead_of_invalid(tmp_path: Path) -> None:
    profiles, profile_hash, profile_document = MODULE.read_profiles(MODULE.PROFILE_PATH)
    contract_hash, _ = MODULE.read_contract(MODULE.CONTRACT_PATH)
    case = MODULE.Case(profile=profiles[0], result_root=tmp_path)
    MODULE.stage_case(
        case,
        profile_path=MODULE.PROFILE_PATH,
        profile_hash=profile_hash,
        contract_path=MODULE.CONTRACT_PATH,
        contract_hash=contract_hash,
        profile_document=profile_document,
    )
    record = MODULE.write_record(case, None, dry_run=True)

    matrix_path = MODULE.write_matrix(
        [record],
        result_root=tmp_path,
        profile_path=MODULE.PROFILE_PATH,
        profile_hash=profile_hash,
        contract_path=MODULE.CONTRACT_PATH,
        contract_hash=contract_hash,
        dry_run=True,
    )
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    assert matrix["status"] == "planned"
