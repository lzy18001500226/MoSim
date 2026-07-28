from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "ui" / "write_operator_fault_request.py"


def _module():
    spec = importlib.util.spec_from_file_location("write_operator_fault_request", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest(vehicle_count: int = 3) -> dict[str, object]:
    return {
        "run_id": "run-factory-test",
        "experiment_profile_hash": "profile-hash-test",
        "vehicle_count": vehicle_count,
    }


def _args(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "vehicle_id": "uav1",
        "target": "wind_speed_mps",
        "value": 3.5,
        "rotor_index": None,
        "apply_mode": "set",
        "restore_policy": "manual",
        "ramp_s": 0.0,
        "duration_s": 0.0,
        "restore_normal": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_wind_request_is_bound_to_the_frozen_run_and_profile(tmp_path: Path) -> None:
    module = _module()
    contract = module.load_contract(ROOT / "Config" / "control_platform" / "factory_injection_contract.json")

    commands = module.build_commands(_manifest(), contract, _args(vehicle_id="uav2", value=4.5))
    written = module.write_commands(tmp_path, commands)
    payload = json.loads(written[0].read_text(encoding="utf-8"))

    assert payload["schema"] == "mosim.factory_injection_command.v1"
    assert payload["run_id"] == "run-factory-test"
    assert payload["profile_hash"] == "profile-hash-test"
    assert payload["vehicle_id"] == "uav2"
    assert payload["target"] == "wind_speed_mps"
    assert payload["value"] == 4.5
    assert payload["source"] == "qgc_visible_terminal"
    assert written[0].parent == tmp_path / "injection_commands"


def test_motor_request_requires_a_valid_rotor_and_vehicle() -> None:
    module = _module()
    contract = module.load_contract(ROOT / "Config" / "control_platform" / "factory_injection_contract.json")

    commands = module.build_commands(
        _manifest(),
        contract,
        _args(vehicle_id="uav3", target="motor_effectiveness", value=0.6, rotor_index=4),
    )

    assert commands[0]["target"] == "motor_effectiveness"
    assert commands[0]["rotor_index"] == 4
    assert commands[0]["value"] == 0.6

    with pytest.raises(ValueError, match="injection_vehicle_id_invalid"):
        module.build_commands(_manifest(vehicle_count=1), contract, _args(vehicle_id="uav2"))
    with pytest.raises(ValueError, match="injection_rotor_index_invalid"):
        module.build_commands(
            _manifest(),
            contract,
            _args(target="motor_effectiveness", value=0.6, rotor_index=None),
        )


def test_restore_normal_writes_one_wind_and_four_rotor_recovery_commands(tmp_path: Path) -> None:
    module = _module()
    contract = module.load_contract(ROOT / "Config" / "control_platform" / "factory_injection_contract.json")

    commands = module.build_commands(_manifest(), contract, _args(vehicle_id="uav2", restore_normal=True))
    written = module.write_commands(tmp_path, commands)

    assert len(commands) == 5
    assert len(written) == 5
    assert commands[0]["target"] == "wind_speed_mps"
    assert commands[0]["value"] == 0.0
    assert commands[0]["apply_mode"] == "restore"
    rotor_commands = commands[1:]
    assert [command["rotor_index"] for command in rotor_commands] == [1, 2, 3, 4]
    assert all(command["target"] == "motor_effectiveness" for command in rotor_commands)
    assert all(command["value"] == 1.0 for command in rotor_commands)
    assert all(command["vehicle_id"] == "uav2" for command in commands)
