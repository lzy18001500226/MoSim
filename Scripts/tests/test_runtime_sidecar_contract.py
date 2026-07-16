from __future__ import annotations

from pathlib import Path

import pytest

from src.orchestration.runtime_sidecar_contract import load_contract, resolve_gazebo_body_name, validate_command


CONTRACT = Path("Config/control_platform/factory_injection_contract.json")


def command(**overrides):
    value = {
        "command_id": "inj-contract-test",
        "run_id": "run-test",
        "profile_hash": "hash-test",
        "target": "motor_effectiveness",
        "requested_at": 1.0,
        "apply_mode": "set",
        "value": 0.6,
        "ramp_s": 0.0,
        "duration_s": 0.0,
        "restore_policy": "manual",
        "source": "test",
        "rotor_index": 2,
    }
    value.update(overrides)
    return value


def test_contract_normalizes_restore_to_physical_nominal() -> None:
    normalized = validate_command(
        command(apply_mode="restore", value=0.0),
        manifest={"run_id": "run-test", "experiment_profile_hash": "hash-test"},
        contract=load_contract(CONTRACT),
    )
    assert normalized["value"] == 1.0


@pytest.mark.parametrize(
    ("override", "reason"),
    [
        ({"value": 1.2}, "injection_value_out_of_range"),
        ({"rotor_index": 5}, "injection_rotor_index_invalid"),
        ({"run_id": "run-other"}, "injection_run_id_mismatch"),
    ],
)
def test_contract_rejects_invalid_commands(override, reason) -> None:
    with pytest.raises(ValueError, match=reason):
        validate_command(
            command(**override),
            manifest={"run_id": "run-test", "experiment_profile_hash": "hash-test"},
            contract=load_contract(CONTRACT),
        )


def test_runtime_wrapper_starts_sidecar_and_reuses_ftc_plugin() -> None:
    wrapper = Path("Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    assert "runtime_sidecar.py" in wrapper
    assert "build_p7_ftc_actuator_plugin.sh" in wrapper
    assert 'MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN="true"' in wrapper
    assert "factoryenvironmentcollect_l2_static_review_clean.sdf" in wrapper
    assert '--body-name "uav1::base_link"' in wrapper


def test_gazebo_body_resolution_prefers_explicit_factory_vehicle() -> None:
    assert resolve_gazebo_body_name("uav1::base_link", ["sunray150_with_mid360"]) == "uav1::base_link"


def test_gazebo_body_resolution_prefers_runtime_uav_name() -> None:
    assert resolve_gazebo_body_name("", ["ground_plane", "sunray150_template", "uav1"]) == "uav1::base_link"


def test_gazebo_body_resolution_keeps_sunray_fallback() -> None:
    assert resolve_gazebo_body_name("", ["ground_plane", "sunray150_with_mid360"]) == (
        "sunray150_with_mid360::base_link"
    )
