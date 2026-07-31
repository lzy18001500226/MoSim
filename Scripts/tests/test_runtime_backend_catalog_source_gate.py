from __future__ import annotations

import json
from pathlib import Path

from Scripts.ui.check_runtime_backend_catalog import check


CATALOG = Path("Config/control_platform/runtime_backend_catalog.json")
OPERATOR_PROFILES = Path("Config/profiles/operator_profiles.json")


def write_catalog(tmp_path: Path, catalog: dict) -> Path:
    path = tmp_path / "runtime_backend_catalog.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    return path


def write_operator_profiles(tmp_path: Path, catalog: dict) -> Path:
    path = tmp_path / "operator_profiles.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    return path


def test_current_qgc_copy_only_runtime_contract_is_source_closed() -> None:
    result = check(CATALOG)

    assert result["status"] == "passed", result["errors"]
    assert result["runtime_profile_count"] == 9
    assert result["operator_profile_count"] == 9
    assert result["enabled_operator_profile_count"] == 7
    assert result["enabled_operator_invocation_count"] == 7
    assert result["controller_scheme_count"] == 48
    assert result["published_controller_scheme_count"] == 3
    assert result["enabled_controller_scheme_count"] == 2


def test_gate_rejects_operator_profile_without_a_registered_controller_scheme(tmp_path: Path) -> None:
    profiles = json.loads(OPERATOR_PROFILES.read_text(encoding="utf-8"))
    profiles["profiles"][0]["controller_scheme_id"] = "missing_controller"

    result = check(CATALOG, operator_profiles_path=write_operator_profiles(tmp_path, profiles))

    assert result["status"] == "failed"
    assert "operator_profile_controller_scheme_unknown:px4ctrl_ground_standby_v1:missing_controller" in result["errors"]


def test_gate_rejects_operator_profile_without_a_task_key(tmp_path: Path) -> None:
    profiles = json.loads(OPERATOR_PROFILES.read_text(encoding="utf-8"))
    profiles["profiles"][0].pop("task_key")

    result = check(CATALOG, operator_profiles_path=write_operator_profiles(tmp_path, profiles))

    assert result["status"] == "failed"
    assert "operator_profile_task_key_invalid:px4ctrl_ground_standby_v1:" in result["errors"]


def test_gate_rejects_enabled_operator_profile_without_runtime_entry(tmp_path: Path) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    catalog["runtime_profiles"] = catalog["runtime_profiles"][:-1]

    result = check(write_catalog(tmp_path, catalog))

    assert result["status"] == "failed"
    assert "operator_profile_runtime_missing:factory_l2_three_uav_swarm_formation_v1" in result["errors"]


def test_gate_rejects_enabled_profile_without_copyable_invocation(tmp_path: Path) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    fuel = next(
        entry
        for entry in catalog["runtime_profiles"]
        if entry["operation_id"] == "factory_l2_fuel_fixed64_exploration"
    )
    fuel.pop("operator_invocation")

    result = check(write_catalog(tmp_path, catalog))

    assert result["status"] == "failed"
    assert "operator_invocation_missing:sunray_ros1_factory_l2_fuel_fixed64_exploration_v1" in result["errors"]


def test_gate_rejects_shell_unsafe_operator_argument(tmp_path: Path) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    fuel = next(
        entry
        for entry in catalog["runtime_profiles"]
        if entry["operation_id"] == "factory_l2_fuel_fixed64_exploration"
    )
    fuel["operator_invocation"]["arguments"].append("$(unsafe)")

    result = check(write_catalog(tmp_path, catalog))

    assert result["status"] == "failed"
    assert any(
        error.startswith("operator_invocation_argument_invalid:sunray_ros1_factory_l2_fuel_fixed64_exploration_v1:")
        for error in result["errors"]
    )


def test_gate_rejects_enabled_automatic_task_without_matching_authority(tmp_path: Path) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    fuel = next(
        entry
        for entry in catalog["runtime_profiles"]
        if entry["operation_id"] == "factory_l2_fuel_fixed64_exploration"
    )
    fuel["operator_contract"] = {
        "flight_authority": "qgc_native_manual",
        "takeoff_owner": "qgc_native",
        "mission_adapter_source": None,
        "terminal_ack": "qgc_vehicle_disarm",
        "safe_stop": "qgc_native_land",
    }

    result = check(write_catalog(tmp_path, catalog))

    assert result["status"] == "failed"
    assert "operator_profile_authority_mismatch:factory_l2_fuel_fixed64_exploration_v1:mission_adapter" in result["errors"]


def test_gate_rejects_external_mission_adapter_source(tmp_path: Path) -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    figure8 = next(entry for entry in catalog["runtime_profiles"] if entry["operation_id"] == "px4ctrl_figure8_single")
    figure8["operator_contract"]["mission_adapter_source"] = str(tmp_path / "external_adapter.py")

    result = check(write_catalog(tmp_path, catalog))

    assert result["status"] == "failed"
    assert "mission_adapter_source_missing_or_external:sunray_ros1_px4ctrl_figure8_single_v1" in result["errors"]
