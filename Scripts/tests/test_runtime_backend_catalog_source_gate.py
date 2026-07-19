from __future__ import annotations

import json
from pathlib import Path

from Scripts.ui.check_runtime_backend_catalog import check


def test_current_qgc_runtime_chain_is_source_closed() -> None:
    result = check(Path("Config/control_platform/runtime_backend_catalog.json"))
    assert result["status"] == "passed", result["errors"]
    assert result["runtime_profile_count"] == 7
    assert result["runner_operation_count"] == 7
    assert result["qgc_profile_count"] == 7


def test_gate_rejects_qgc_profile_without_runtime_selection(tmp_path: Path) -> None:
    catalog = json.loads(Path("Config/control_platform/runtime_backend_catalog.json").read_text(encoding="utf-8"))
    catalog["runtime_profiles"] = catalog["runtime_profiles"][:-1]
    catalog_path = tmp_path / "runtime_backend_catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    result = check(catalog_path)

    assert result["status"] == "failed"
    assert "runner_operation_not_catalogued:factory_l2_three_uav_swarm_formation" in result["errors"]
    assert "qgc_runtime_selection_missing:factory_l2_three_uav_swarm_formation_v1:px4ctrl:3" in result["errors"]


def test_gate_rejects_catalog_operation_missing_from_runner(tmp_path: Path) -> None:
    runner = Path("Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    runner = runner.replace("  factory_l2_fuel_fixed64_exploration)\n", "")
    runner_path = tmp_path / "runner.sh"
    runner_path.write_text(runner, encoding="utf-8")

    result = check(Path("Config/control_platform/runtime_backend_catalog.json"), runner_path=runner_path)

    assert result["status"] == "failed"
    assert any(error.endswith(":factory_l2_fuel_fixed64_exploration") for error in result["errors"])


def test_gate_rejects_enabled_automatic_task_without_mission_adapter_contract(tmp_path: Path) -> None:
    catalog = json.loads(Path("Config/control_platform/runtime_backend_catalog.json").read_text(encoding="utf-8"))
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
    catalog_path = tmp_path / "runtime_backend_catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    result = check(catalog_path)

    assert result["status"] == "failed"
    assert "qgc_automatic_authority_mismatch:factory_l2_fuel_fixed64_exploration_v1" in result["errors"]


def test_gate_rejects_external_mission_adapter_source(tmp_path: Path) -> None:
    catalog = json.loads(Path("Config/control_platform/runtime_backend_catalog.json").read_text(encoding="utf-8"))
    figure8 = next(
        entry for entry in catalog["runtime_profiles"] if entry["operation_id"] == "px4ctrl_figure8_single"
    )
    incomplete_adapter = tmp_path / "incomplete_adapter.py"
    incomplete_adapter.write_text("MissionStatusChannel\nSafeStopChannel\n", encoding="utf-8")
    figure8["operator_contract"]["mission_adapter_source"] = str(
        incomplete_adapter.relative_to(Path.cwd())
    ) if incomplete_adapter.is_relative_to(Path.cwd()) else str(incomplete_adapter)
    catalog_path = tmp_path / "runtime_backend_catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    result = check(catalog_path)

    assert result["status"] == "failed"
    assert any(error.startswith("mission_adapter_source_missing_or_external:") for error in result["errors"])
