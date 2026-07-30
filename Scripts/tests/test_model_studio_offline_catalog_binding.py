#!/usr/bin/env python3
"""Source-contract checks for the current MoSim Studio workspaces."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
APP_SOURCE = ROOT / "apps" / "model_studio" / "src" / "app.jl"
OPEN_MODEL_SCRIPT = ROOT / "Scripts" / "ui" / "open_model_studio_model.py"
CURRENT_MODEL_ENTRY_MAP = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"


def section(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_model_studio_has_four_workspaces_and_compact_header() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    for title in ("在线建模验证", "实时联合仿真", "代码生成", "MoSim 助手"):
        assert title in source
    assert "function configure_model_workspace(app)" in source
    assert "function configure_live_workspace(app)" in source
    assert "function configure_deploy_workspace(app)" in source
    assert 'app.TitleLabel.HorizontalAlignment = "left"' in source
    assert "控制器配置、模型验证与QGC运行交接" not in source


def test_model_workspace_uses_eight_explicit_single_uav_tasks() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    for task_id in (
        "climb_path_50s",
        "hover",
        "step_response",
        "figure8",
        "spiral",
        "wind_disturbance",
        "parameter_mismatch",
        "motor_efficiency_fault",
    ):
        assert f'id="{task_id}"' in source

    model = section(source, "function configure_model_workspace(app)", "function configure_live_workspace(app)")
    assert '"验证任务与控制器"' in model
    assert '"场景参数"' in model
    assert "app.configure_model_task_controls()" in model
    assert "app.TaskDropDown" in model
    assert "app.ParameterMismatchSlider" in model
    assert "电机 1 效率（15 s 后）" in model
    assert "app.ApplyInjectionButton.Text = \"写入配置\"" in model
    assert "app.RestoreInjectionButton.Text = \"重置\"" in model
    assert "app.OpenModelButton.Text = \"打开仿真模型\"" in model
    assert "app.set_visible((app.OpenModelButton,), true)" in model
    assert "ValidateButton" not in model


def test_model_workspace_removes_legacy_preset_and_formation_fields() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    model = section(source, "function configure_model_workspace(app)", "function configure_live_workspace(app)")
    for removed in (
        "ProfileDropDown",
        "VehicleCountDropDown",
        "MapDropDown",
        "MissionDropDown",
        "FormationDropDown",
        "TargetUavDropDown",
    ):
        assert removed not in model
    assert "app.configure_composition_controls()" not in model


def test_model_dropdowns_use_native_labels_without_overlay_fields() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    model_controls = section(source, "function configure_model_task_controls(app)", "function is_three_uav_mission(app, mission)")
    labels = {
        "TaskDropDown": "验证任务",
        "ControllerFamilyDropDown": "控制器家族",
        "PositionDropDown": "控制器实例",
        "AttitudeDropDown": "姿态内环",
        "AugmentationDropDown": "增强层",
        "SafetyDropDown": "安全层",
        "FaultDropDown": "故障容错层",
        "OutputDropDown": "输出边界",
    }
    for control, label in labels.items():
        assert f'app.{control}.Label = "{label}"' in model_controls or f'(app.{control}, "{label}"' in model_controls
    assert 'Label = ""' not in model_controls
    assert "configure_model_field_label" not in source
    assert "TaskLabel::Any" not in source


def test_hidden_workspace_controls_are_parked_outside_the_active_layout() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    visibility_helper = section(source, "function set_visible(app, controls, visible)", "function configure_console_workspace(app;")
    assert "const HIDDEN_CONTROL_POSITION = [-2048, -2048, 1, 1]" in source
    assert "control.Visible = false" in visibility_helper
    assert "control.Position = HIDDEN_CONTROL_POSITION" in visibility_helper


def test_model_workspace_hides_status_summary_blocks() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    model = section(source, "function configure_model_workspace(app)", "function configure_live_workspace(app)")
    model_summary = section(source, 'elseif app.CurrentMode == "model"', 'elseif app.CurrentMode == "deploy"')
    assert "ProfileSummaryLabel" not in model
    assert "InjectionValuesLabel" not in model
    assert "ProfileSummaryLabel" not in model_summary
    assert "InjectionValuesLabel" not in model_summary
    assert "app.ApplyInjectionButton.Position = [494, 536, 160, 36]" in model
    assert "app.OpenModelButton.Position = [664, 536, 200, 36]" in model
    assert "app.RestoreInjectionButton.Position = [874, 536, 60, 36]" in model


def test_model_tasks_are_frozen_before_opening_mworks() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert 'const MODEL_TASK_CONFIG_WRITER = joinpath(PROJECT_ROOT, "Scripts", "ui", "model_studio_task_config.py")' in source
    assert '"--task-id", task.id' in source
    assert '"--controller-id", controller.id' in source
    assert '"--gust-force-x-n", string(app.WindSlider.Value)' in source
    assert '"--mass-inertia-scale", string(app.ParameterMismatchSlider.Value)' in source
    assert "app.TaskConfigDirty = false" in source
    assert '"--task-config", app.TaskConfigPath' in source
    assert "请先写入配置，再打开对应的 MWORKS 仿真模型" in source
    assert "请在 MWORKS 中自行点击仿真" in source
    assert "在线建模验证不从 Studio 启动仿真" in source


def test_model_task_scope_is_explicitly_limited_to_registered_formal_runners() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert 'const MODEL_FORMAL_CONTROLLER_IDS = Set(["official_pid", "px4ctrl"])' in source
    assert "app.model_task_controller_supported()" in source
    assert "当前验证任务只登记 official_pid 与 px4ctrl" in source
    assert "ROTOR_COMMAND / OfficialPidFormalRunner" in source
    assert "ATTITUDE_THRUST / Px4CtrlFormalRunner" in source


def test_live_workspace_retains_its_separate_runtime_controls() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    live = section(source, "function configure_live_workspace(app)", "function configure_deploy_workspace(app)")
    for expected in (
        "TargetHostField",
        "Rt1PortField",
        "RosMasterField",
        "LocalIpField",
        "TargetUavDropDown",
        "WindSlider",
        "Motor1Slider",
        "ApplyInjectionButton",
        "RestoreInjectionButton",
        'app.ApplyInjectionButton.Text = "应用故障"',
        'app.OpenModelButton.Text = "打开联合仿真模型"',
    ):
        assert expected in live


def test_deploy_workspace_remains_manual_mworks_codegen_only() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    deploy = section(source, "function configure_deploy_workspace(app)", "function set_mode(app, mode)")
    assert 'app.CodegenButton.Text = "打开 MWORKS 代码生成模型"' in deploy
    assert "WindSlider" not in deploy
    assert "ApplyInjectionButton" not in deploy
    assert 'app.open_mworks_model("codegen")' in source
    assert "GenerateModelCode" not in source


def test_open_model_entry_loads_frozen_harness_without_simulation() -> None:
    script = OPEN_MODEL_SCRIPT.read_text(encoding="utf-8")
    worker = (ROOT / "Scripts" / "ui" / "open_model_studio_model_worker.py").read_text(encoding="utf-8")
    assert 'TASK_CONFIG_SCHEMA = "mosim.model_studio.task_config.v1"' in script
    assert "def resolve_task_config" in script
    assert 'parser.add_argument("--task-config", type=Path)' in script
    assert "task_config_harness_hash_mismatch" in script
    assert "model_load_files(args.mode, model_file)" in script
    assert 'command.append("--check-model")' in script
    assert "GenerateModelCode" not in script
    assert "SimulateModel" not in script
    assert "ModelingPy.StartSysplorer" in worker
    assert "ModelingPy.CheckModel" in worker
    assert "SimulateModel" not in worker


def test_codegen_model_resolver_uses_current_graphical_model_map() -> None:
    module = load_module(OPEN_MODEL_SCRIPT, "open_model_studio_model_test")
    model_map = json.loads(CURRENT_MODEL_ENTRY_MAP.read_text(encoding="utf-8-sig"))
    rows = {row["scheme_id"]: row for row in model_map["schemes"]}
    resolved_ids = [
        scheme_id
        for scheme_id, row in rows.items()
        if row.get("mapping_state") == "resolved_current_model"
    ]
    assert len(resolved_ids) == 46
    for scheme_id in resolved_ids:
        model_file, model_class = module.resolve_controller_model(scheme_id)
        assert model_file == ROOT / rows[scheme_id]["current_model_file"]
        assert model_file.is_file()
        assert model_class == rows[scheme_id]["current_model_class"]

    model_file, model_class = module.resolve_controller_model("px4ctrl")
    assert model_file == module.PX4CTRL_CODEGEN_MODEL_FILE
    assert model_file.is_file()
    assert model_class == module.PX4CTRL_CODEGEN_MODEL_NAME
    with pytest.raises(ValueError, match="controller_not_openable"):
        module.resolve_controller_model("pid_awff_linear_eso")


def test_catalog_selector_still_contains_all_current_controller_entries() -> None:
    catalog = json.loads(
        (ROOT / "Config" / "control_platform" / "control_scheme_catalog.json").read_text(encoding="utf-8-sig")
    )
    source = APP_SOURCE.read_text(encoding="utf-8")
    selector = section(source, "const CONTROLLER_CATALOG = [", "]\nconst LEGACY_PROFILE_CONTROLLERS")
    active_ids = [scheme["scheme_id"] for scheme in catalog["schemes"]]
    assert len(active_ids) == 48
    assert len(re.findall(r'\(id="([^"]+)"', selector)) == 48
    assert all(f'id="{scheme_id}"' in selector for scheme_id in active_ids)
