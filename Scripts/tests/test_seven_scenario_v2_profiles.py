#!/usr/bin/env python3
"""Static contract checks for the versioned Figure8/Spiral seven-scenario v2 set."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "Config" / "control_platform" / "seven_scenario_injection_contract_v2.json"
PROFILES = ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_v2.json"
DRIVER = ROOT / "Scripts" / "mworks" / "run_seven_scenario_ab.py"

SCENARIOS = [
    "hover",
    "step_response",
    "figure8",
    "spiral",
    "wind_disturbance",
    "parameter_mismatch",
    "motor_efficiency_fault",
]
RUNNER_PARAMETER_KEYS = [
    "gust_force",
    "gust_start_s",
    "gust_duration_s",
    "mass_scale",
    "inertia_scale",
    "rotor_effectiveness",
    "fault_start_s",
    "fault_rotor_index",
    "fault_rotor_effectiveness",
]


def load_driver():
    spec = importlib.util.spec_from_file_location("run_seven_scenario_ab", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {DRIVER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_v2_profile_and_contract_match() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))

    assert contract["schema"] == "mosim.seven_scenario_injection_contract.v2"
    assert profiles["schema"] == "mosim.seven_scenario_experiment_profiles.v2"
    assert [row["scenario_id"] for row in contract["scenarios"]] == SCENARIOS
    assert [row["scenario_id"] for row in profiles["profiles"]] == SCENARIOS
    assert profiles["authority"]["injection_contract"] == "Config/control_platform/seven_scenario_injection_contract_v2.json"
    assert profiles["authority"]["result_root_template"].startswith("Results/control_platform/seven_scenario_ab_v2/")
    expected_runner_classes = {
        row["runner_class"] for row in driver_routes()
    }
    assert set(profiles["formal_runner_binding"]["allowed_runner_classes"]) == expected_runner_classes
    assert set(contract["runner_binding_policy"]["authorized_runner_classes"]) == expected_runner_classes

    by_id = {row["scenario_id"]: row for row in profiles["profiles"]}
    assert by_id["wind_disturbance"]["trajectory_class"].endswith(".Figure8")
    assert by_id["parameter_mismatch"]["trajectory_class"].endswith(".SpiralAscent")
    assert by_id["motor_efficiency_fault"]["trajectory_class"].endswith(".Figure8")
    assert by_id["wind_disturbance"]["runner_parameter_overrides"]["gust_force"] == [0.25, 0.0, 0.0]
    assert by_id["wind_disturbance"]["runner_parameter_overrides"]["gust_start_s"] == 15.0
    assert by_id["wind_disturbance"]["runner_parameter_overrides"]["gust_duration_s"] == 35.0
    assert by_id["parameter_mismatch"]["runner_parameter_overrides"]["mass_scale"] == 1.2
    assert by_id["parameter_mismatch"]["runner_parameter_overrides"]["inertia_scale"] == [1.2, 1.2, 1.2]
    assert by_id["motor_efficiency_fault"]["runner_parameter_overrides"]["fault_start_s"] == 15.0
    assert by_id["motor_efficiency_fault"]["runner_parameter_overrides"]["fault_rotor_index"] == 1
    assert by_id["motor_efficiency_fault"]["runner_parameter_overrides"]["fault_rotor_effectiveness"] == 0.5
    for profile in profiles["profiles"]:
        assert list(profile["runner_parameter_overrides"]) == RUNNER_PARAMETER_KEYS


def driver_routes() -> list[dict[str, str]]:
    driver = load_driver()
    return list(driver.CONTROLLERS.values())


def test_v2_driver_stages_all_48_controllers_across_seven_scenarios() -> None:
    driver = load_driver()
    document, _ = driver.read_profiles(PROFILES)
    contract, _ = driver.read_contract(CONTRACT)
    driver.validate_profile_contract_alignment(document, contract)
    with tempfile.TemporaryDirectory() as tmp:
        cases = driver.selected_cases(
            document,
            sorted(driver.CONTROLLERS),
            None,
            Path(tmp),
        )
    assert len(driver.CONTROLLERS) == 48
    assert len(cases) == 48 * 7
    by_scenario = {case.scenario_id: case for case in cases if case.controller_id == "pid_awff_linear_eso"}
    wind_harness = driver.render_harness(by_scenario["wind_disturbance"])
    mismatch_harness = driver.render_harness(by_scenario["parameter_mismatch"])
    fault_harness = driver.render_harness(by_scenario["motor_efficiency_fault"])
    assert "scenario_mode = 3" in wind_harness
    assert "reference(" in wind_harness
    assert "gust_start_s = 15" in wind_harness
    assert "scenario_mode = 4" in mismatch_harness
    assert "reference(" in mismatch_harness
    assert "mass_scale = 1.2" in mismatch_harness
    assert "injection_plant_inertia_diagonal_kg_m2" in mismatch_harness
    assert "scenario_mode = 3" in fault_harness
    assert "reference(" in fault_harness
    assert "fault_rotor_effectiveness = 0.5" in fault_harness
    assert "PidAwffLinearEsoGraphicalRunner" in fault_harness


def main() -> int:
    test_v2_profile_and_contract_match()
    test_v2_driver_stages_all_48_controllers_across_seven_scenarios()
    print("[OK] seven-scenario v2 profile contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
