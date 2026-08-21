#!/usr/bin/env python3
"""Unit tests for the no-solver Model Studio task handoff path."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
WRITER_PATH = ROOT / "Scripts" / "ui" / "model_studio_task_config.py"
OPEN_MODEL_PATH = ROOT / "Scripts" / "ui" / "open_model_studio_model.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_config(writer, tmp_path: Path, **kwargs):
    return writer.write_task_config(output=tmp_path / "latest.json", **kwargs)


def test_standard_wind_task_writes_the_formal_v2_profile(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_wind")
    payload = write_config(
        writer,
        tmp_path,
        task_id="wind_disturbance",
        controller_id="px4ctrl",
        gust_force_x_n=0.25,
        mass_inertia_scale=1.0,
        motor_effectiveness=[1.0, 1.0, 1.0, 1.0],
    )
    saved = json.loads((tmp_path / "latest.json").read_text(encoding="utf-8"))
    assert payload == saved
    assert payload["schema"] == writer.TASK_CONFIG_SCHEMA
    assert payload["configuration_kind"] == "formal_v2_profile"
    assert payload["runner_class"] == "MoSimQuadrotorModel.Experiment.SingleUav.Px4Ctrl.Px4CtrlRunner"
    assert payload["trajectory_binding"] == "scenario_mode"
    assert payload["trajectory_mode"] == 3
    assert payload["profile"]["runner_parameter_overrides"]["gust_force"] == [0.25, 0.0, 0.0]
    assert payload["profile"]["runner_parameter_overrides"]["gust_start_s"] == 15.0
    assert payload["profile"]["runner_parameter_overrides"]["gust_duration_s"] == 35.0
    harness = Path(payload["harness_file"])
    assert harness.is_file()
    assert "gust_force = {0.25, 0, 0}" in harness.read_text(encoding="utf-8")


def test_parameter_mismatch_synchronizes_mass_and_all_inertias(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_mismatch")
    payload = write_config(
        writer,
        tmp_path,
        task_id="parameter_mismatch",
        controller_id="official_pid",
        gust_force_x_n=0.0,
        mass_inertia_scale=1.3,
        motor_effectiveness=[1.0, 1.0, 1.0, 1.0],
    )
    runner = payload["profile"]["runner_parameter_overrides"]
    assert payload["configuration_kind"] == "task_parameter_variant"
    assert runner["mass_scale"] == 1.3
    assert runner["inertia_scale"] == [1.3, 1.3, 1.3]
    harness = Path(payload["harness_file"]).read_text(encoding="utf-8")
    assert "mass_scale = 1.3" in harness
    assert "inertia_scale = {1.3, 1.3, 1.3}" in harness
    assert "extends MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner(" in harness


def test_motor_task_keeps_a_single_delayed_rotor_fault(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_motor")
    payload = write_config(
        writer,
        tmp_path,
        task_id="motor_efficiency_fault",
        controller_id="px4ctrl",
        gust_force_x_n=0.0,
        mass_inertia_scale=1.0,
        motor_effectiveness=[1.0, 1.0, 0.6, 1.0],
    )
    runner = payload["profile"]["runner_parameter_overrides"]
    assert payload["configuration_kind"] == "task_parameter_variant"
    assert runner["fault_start_s"] == 15.0
    assert runner["fault_rotor_index"] == 3
    assert runner["fault_rotor_effectiveness"] == 0.6
    assert runner["rotor_effectiveness"] == [1.0, 1.0, 1.0, 1.0]


def test_standard_motor_fault_is_the_formal_v2_profile(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_motor_formal")
    payload = write_config(
        writer,
        tmp_path,
        task_id="motor_efficiency_fault",
        controller_id="official_pid",
        gust_force_x_n=0.0,
        mass_inertia_scale=1.0,
        motor_effectiveness=[0.5, 1.0, 1.0, 1.0],
    )
    assert payload["configuration_kind"] == "formal_v2_profile"


def test_task_writer_rejects_out_of_contract_parameter_combinations(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_reject")
    with pytest.raises(ValueError, match="motor_fault_requires_exactly_one_impaired_motor"):
        write_config(
            writer,
            tmp_path,
            task_id="motor_efficiency_fault",
            controller_id="px4ctrl",
            gust_force_x_n=0.0,
            mass_inertia_scale=1.0,
            motor_effectiveness=[0.5, 0.7, 1.0, 1.0],
        )
    with pytest.raises(ValueError, match="formal_task_controller_has_no_registered_runner"):
        write_config(
            writer,
            tmp_path,
            task_id="hover",
            controller_id="unregistered_controller",
            gust_force_x_n=0.0,
            mass_inertia_scale=1.0,
            motor_effectiveness=[1.0, 1.0, 1.0, 1.0],
        )


def test_registered_formal_route_writes_a_manual_task_for_any_controller(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_generic_formal")
    payload = write_config(
        writer,
        tmp_path,
        task_id="figure8",
        controller_id="linear_mpc",
        gust_force_x_n=0.25,
        mass_inertia_scale=1.2,
        motor_effectiveness=[1.0, 0.5, 1.0, 1.0],
        fault_start_s=17.0,
    )
    assert payload["configuration_kind"] == "manual_formal_task"
    assert payload["runner_class"] == writer.FORMAL_CONTROLLER_ROUTES["linear_mpc"]["runner_class"]
    assert payload["task_route"]["boundary"] == "ATTITUDE_THRUST"
    assert payload["task_route_source"].endswith("model_studio_task_routes_v1.toml")
    harness = Path(payload["harness_file"]).read_text(encoding="utf-8")
    assert "extends MoSimQuadrotorModel.Experiment.SingleUav.LinearMpc.LinearMpcGraphicalRunner(" in harness
    assert "scenario_mode = 3" in harness
    assert "gust_force = {0.25, 0, 0}" in harness
    assert "fault_rotor_index = 2" in harness


def test_manual_route_catalog_covers_the_controller_catalog_without_evidence_gating() -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_route_catalog")
    assert len(writer.FORMAL_CONTROLLER_ROUTES) == 48
    assert len(writer.FORMAL_CONTROLLER_IDS) == 48
    for controller_id in ("adaptive_backstepping", "fixed_awff_pid", "fixed_linear_mpc_l1_indi", "px4ctrl"):
        assert controller_id in writer.FORMAL_CONTROLLER_IDS
    for controller_id in ("pid_awff_linear_eso", "smc_boundary_layer", "nmpc_outer", "fixed_qp_nmpc_l1_indi_cbf"):
        assert controller_id in writer.FORMAL_CONTROLLER_IDS


def test_every_registered_route_renders_its_current_runner_and_reference_binding(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_all_routes")
    for controller_id, route in sorted(writer.FORMAL_CONTROLLER_ROUTES.items()):
        payload = write_config(
            writer,
            tmp_path / controller_id,
            task_id="figure8",
            controller_id=controller_id,
            gust_force_x_n=0.0,
            mass_inertia_scale=1.0,
            motor_effectiveness=[1.0, 1.0, 1.0, 1.0],
        )
        assert payload["runner_class"] == route["runner_class"]
        assert payload["task_route"]["runner_file"] == route["runner_file"]
        harness = Path(payload["harness_file"]).read_text(encoding="utf-8")
        assert f"extends {route['runner_class']}(" in harness
        assert "scenario_mode = 3" in harness


def test_baseline_is_a_separate_climbpath_handoff(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_baseline")
    payload = write_config(
        writer,
        tmp_path,
        task_id="climb_path_50s",
        controller_id="px4ctrl",
        gust_force_x_n=0.0,
        mass_inertia_scale=1.0,
        motor_effectiveness=[1.0, 1.0, 1.0, 1.0],
    )
    assert payload["configuration_kind"] == "climb_path_baseline"
    assert payload["profile"]["duration_s"] == 50.0
    assert payload["profile"]["trajectory_class"].endswith(".ClimbPath")


def test_formal_task_accepts_composed_wind_mismatch_and_motor_fault(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_composed")
    payload = write_config(
        writer,
        tmp_path,
        task_id="figure8",
        controller_id="px4ctrl",
        gust_force_x_n=0.25,
        mass_inertia_scale=1.2,
        motor_effectiveness=[1.0, 0.5, 1.0, 1.0],
        fault_start_s=17.0,
    )
    runner = payload["profile"]["runner_parameter_overrides"]
    assert payload["configuration_kind"] == "task_parameter_variant"
    assert runner["gust_force"] == [0.25, 0.0, 0.0]
    assert runner["gust_start_s"] == 17.0
    assert runner["gust_duration_s"] == 33.0
    assert runner["mass_scale"] == 1.2
    assert runner["inertia_scale"] == [1.2, 1.2, 1.2]
    assert runner["fault_start_s"] == 17.0
    assert runner["fault_rotor_index"] == 2
    assert runner["fault_rotor_effectiveness"] == 0.5


def test_single_uav_autonomous_avoidance_uses_the_registered_px4ctrl_route(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_single_avoidance")
    payload = write_config(
        writer,
        tmp_path,
        task_id="single_uav_autonomous_avoidance",
        controller_id="px4ctrl",
        gust_force_x_n=0.25,
        mass_inertia_scale=1.1,
        motor_effectiveness=[1.0, 1.0, 0.6, 1.0],
        vehicle_count=1,
        map_id="openblocks",
        fault_target_uav=1,
        fault_start_s=20.0,
    )
    assert payload["configuration_kind"] == "single_uav_planning_route"
    assert payload["runner_class"] == writer.SPECIAL_ROUTES["single_uav_autonomous_avoidance"]["base_model"]
    assert payload["selection"] == {
        "vehicle_count": 1,
        "map_id": "openblocks",
        "fault_target_uav": 1,
    }
    harness = Path(payload["harness_file"]).read_text(encoding="utf-8")
    assert "extends MoSimQuadrotorModel.Guidance.Planning.OpenBlocksPx4Ctrl(" in harness
    assert "gust_start_s = 20" in harness
    gust_duration = re.search(r"gust_duration_s = ([0-9.eE+-]+)", harness)
    assert gust_duration is not None
    assert float(gust_duration.group(1)) == pytest.approx(80.1247340259 - 20.0)
    assert "fault_rotor_index = 3" in harness


def test_three_uav_figure8_targets_the_selected_plant(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_three_figure8")
    payload = write_config(
        writer,
        tmp_path,
        task_id="three_uav_figure8",
        controller_id="px4ctrl",
        gust_force_x_n=0.25,
        mass_inertia_scale=1.2,
        motor_effectiveness=[0.5, 1.0, 1.0, 1.0],
        vehicle_count=3,
        map_id="blank",
        fault_target_uav=2,
        fault_start_s=15.0,
    )
    assert payload["configuration_kind"] == "three_uav_formation_route"
    assert payload["selection"]["fault_target_uav"] == 2
    harness = Path(payload["harness_file"]).read_text(encoding="utf-8")
    assert "extends MoSimQuadrotorModel.Experiment.Formation.Px4Ctrl.ThreeUavPx4CtrlFormationRunner(" in harness
    assert "plant_2(" in harness
    assert "gust_force = {0.25, 0, 0}" in harness
    assert "fault_rotor_effectiveness = 0.5" in harness


def test_multi_uav_route_rejects_wrong_count_and_unsupported_injection(tmp_path: Path) -> None:
    writer = load_module(WRITER_PATH, "model_studio_task_writer_multi_reject")
    with pytest.raises(ValueError, match="task_vehicle_count_not_supported"):
        write_config(
            writer,
            tmp_path,
            task_id="three_uav_figure8",
            controller_id="px4ctrl",
            gust_force_x_n=0.0,
            mass_inertia_scale=1.0,
            motor_effectiveness=[1.0, 1.0, 1.0, 1.0],
            vehicle_count=2,
        )
    with pytest.raises(ValueError, match="task_route_does_not_support_injection"):
        write_config(
            writer,
            tmp_path,
            task_id="three_uav_autonomous_avoidance",
            controller_id="linear_mpc",
            gust_force_x_n=0.25,
            mass_inertia_scale=1.0,
            motor_effectiveness=[1.0, 1.0, 1.0, 1.0],
            vehicle_count=3,
            map_id="openblocks",
        )


def test_open_model_resolves_a_hash_bound_project_harness(tmp_path: Path) -> None:
    opener = load_module(OPEN_MODEL_PATH, "model_studio_open_task_resolver")
    original_root = opener.ROOT
    opener.ROOT = tmp_path
    try:
        harness = tmp_path / "harness.mo"
        harness.write_text("within ;\nmodel FrozenTask\nend FrozenTask;\n", encoding="utf-8")
        config = tmp_path / "latest.json"
        config.write_text(
            json.dumps({
                "schema": opener.TASK_CONFIG_SCHEMA,
                "controller_id": "px4ctrl",
                "model_name": "FrozenTask",
                "harness_file": "harness.mo",
                "harness_sha256": hashlib.sha256(harness.read_bytes()).hexdigest(),
            }),
            encoding="utf-8",
        )
        resolved_harness, model_name, document = opener.resolve_task_config(config)
        assert resolved_harness == harness
        assert model_name == "FrozenTask"
        assert document["controller_id"] == "px4ctrl"

        harness.write_text("within ;\nmodel ChangedTask\nend ChangedTask;\n", encoding="utf-8")
        with pytest.raises(ValueError, match="task_config_harness_hash_mismatch"):
            opener.resolve_task_config(config)
    finally:
        opener.ROOT = original_root
