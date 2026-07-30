from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
APP_SOURCE = ROOT / "apps" / "model_studio" / "src" / "app.jl"
CURRENT_MODEL_ENTRY_MAP = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
OPEN_MODEL_SCRIPT = ROOT / "Scripts" / "ui" / "open_model_studio_model.py"


def test_model_studio_contains_every_offline_profile_authority() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    source = APP_SOURCE.read_text(encoding="utf-8")
    expected = [profile["profile_id"] for profile in catalog["certified_profiles"]]
    expected.extend(proof["profile_id"] for proof in catalog["custom_profile_proofs"])
    expected.extend(profile["profile_id"] for profile in catalog["disabled_profiles"])
    missing = [profile_id for profile_id in expected if profile_id not in source]
    assert missing == []


def test_custom_profiles_are_rerunnable_and_bind_current_evidence() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    source = APP_SOURCE.read_text(encoding="utf-8")
    for proof in catalog["custom_profile_proofs"]:
        assert proof["execution_kind"] == "custom_request"
        assert proof["vehicle_count"] == 1
        assert proof["status"] == "accepted"
        request = ROOT / proof["request_json"]
        certification = ROOT / proof["certification_record"]
        assert request.is_file()
        assert certification.is_file()
        evidence_dir = str(Path(proof["certification_record"]).parent).replace("\\", "/")
        assert evidence_dir in source


def test_model_studio_fail_closes_disabled_safety_profile() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert '"QP/NMPC Safety [当前禁用]"' in source
    assert "available=false" in source
    assert "executable = certified && !unavailable && !incompatible" in source
    assert "app.MilButton.Enable = executable" in source
    assert 'state = incompatible ? "结构不兼容"' in source


def test_model_studio_has_three_distinct_review_workspaces() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert '"在线建模验证"' in source
    assert '"实时联合仿真"' in source
    assert '"代码生成"' in source
    assert "function configure_model_workspace(app)" in source
    assert "function configure_live_workspace(app)" in source
    assert "function configure_deploy_workspace(app)" in source


def test_model_studio_safe_button_callbacks_are_bound() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    expected_callbacks = {
        '"在线建模验证"': '"OfflineModePressed"',
        '"实时联合仿真"': '"LiveModePressed"',
        '"代码生成"': '"DeployModePressed"',
        '"清空"': '"ClearConsolePressed"',
        '"应用故障"': '"ApplyInjectionPressed"',
        '"恢复正常"': '"RestoreInjectionPressed"',
    }
    for text, callback in expected_callbacks.items():
        assert f"app.configure_action(app." in source
        assert text in source
        assert callback in source

    assert 'app.set_mode("model")' in source
    assert 'app.set_mode("live")' in source
    assert 'app.set_mode("deploy")' in source
    assert 'empty!(app.ConsoleLines)' in source
    assert 'app.StatusLabel.Text = ""' in source
    assert '"运行日志已清空"' in source
    assert 'app.WindSlider.Value = 0.0' in source
    for motor in range(1, 5):
        assert f"app.Motor{motor}Slider.Value = 1.0" in source


def test_model_studio_external_action_buttons_fail_closed() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert 'app.ReviewAction("进入 QGC")' in source
    assert 'app.ReviewAction("生成 C 代码")' not in source
    assert 'app.open_mworks_model("codegen")' in source
    assert '"--controller-id", controller.id' in source
    assert "OFFLINE_ANIMATION_RESUMER" in source
    assert '"--keep-session-open"' in source
    assert '"请先完成一次仿真，再打开当前结果"' in source
    assert '"：界面事件已触发，运行后端未连接"' in source
    assert '"故障应用请求未发送；等待实时后端接入"' in source
    assert '"Profile 与当前 UAV 数量、任务或控制链不一致；未启动仿真"' in source


def test_model_workspace_exposes_each_algorithm_layer() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    for component in (
        "MissionDropDown",
        "ControllerFamilyDropDown",
        "PositionDropDown",
        "AttitudeDropDown",
        "AugmentationDropDown",
        "SafetyDropDown",
        "FaultDropDown",
        "FormationDropDown",
        "OutputDropDown",
    ):
        assert f"app.{component}" in source
    assert '"自定义组合"' in source
    assert '"接口待接入"' in source
    assert '"结构不兼容"' in source


def test_live_workspace_surfaces_runtime_observability() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    live = source.split("function configure_live_workspace(app)", 1)[1].split(
        "function configure_deploy_workspace(app)", 1
    )[0]
    for expected in (
        "TargetHostField",
        "Rt1PortField",
        "RosMasterField",
        "LocalIpField",
        "控制频率",
        "Deadline miss",
        "RTT P95",
        "延迟 P99",
        "抖动",
        "丢包率",
        "带宽",
        "运行状态",
    ):
        assert expected in live


def test_deploy_workspace_has_no_fault_injection_controls() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    deploy = source.split("function configure_deploy_workspace(app)", 1)[1].split(
        "function set_mode(app, mode)", 1
    )[0]
    for forbidden in (
        "WindSlider",
        "Motor1Slider",
        "FaultDropDown",
        "ApplyInjectionButton",
        "RestoreInjectionButton",
    ):
        assert forbidden not in deploy


def test_model_studio_uses_compact_status_and_rolling_console() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert "function append_console(app, message; level=\"信息\")" in source
    assert "ConsoleToggleButton" in source
    assert "ConsoleClearButton" in source
    assert "length(app.ConsoleLines) > 40" in source
    assert "CONSOLE_COLOR" in source
    assert 'app.StatusLabel.BackgroundColor = CONSOLE_COLOR' in source
    assert "function configure_console_workspace(app; left=964, width=452)" in source
    assert "app.StatusLabel.Position = [left, 192, width, 456]" in source
    assert "app.ConsoleToggleButton.Visible = false" in source
    assert "app.ConsoleClearButton.Position = [left + width - 84, 200, 76, 28]" in source
    assert "function set_dropdown_position(app, control, position)" in source
    assert "control.Position = position" in source
    for component in (
        "ProfileDropDown",
        "VehicleCountDropDown",
        "MapDropDown",
        "MissionDropDown",
        "PositionDropDown",
        "AttitudeDropDown",
        "AugmentationDropDown",
        "SafetyDropDown",
        "FaultDropDown",
        "FormationDropDown",
        "OutputDropDown",
        "TargetRateDropDown",
        "DeployTargetDropDown",
        "BuildModeDropDown",
        "TargetUavDropDown",
    ):
        assert f"app.{component}.Position =" not in source


def test_model_studio_places_console_in_right_column_and_hides_static_panels() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert "function configure_console_workspace(app; left=964, width=452)" in source
    assert "app.StatusLabel.Position = [left, 192, width, 456]" in source
    assert 'app.configure_section(app.ChainSectionLabel, "风扰与故障"' in source
    assert 'app.configure_section(app.ChainSectionLabel, "连接与实时故障"' in source
    assert "app.configure_console_workspace(left=614, width=802)" in source
    assert "app.ProfileSummaryLabel" not in source.split(
        "function configure_model_workspace(app)", 1
    )[1].split("function configure_live_workspace(app)", 1)[0]


def test_model_studio_shares_layered_composition_and_scenario_controls() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert "const VEHICLE_COUNT_OPTIONS = string.(1:9)" in source
    assert 'const MAP_OPTIONS = ["空白地图", "Factory 避障地图"]' in source
    assert "function configure_composition_controls(app; live=false)" in source
    model = source.split("function configure_model_workspace(app)", 1)[1].split(
        "function configure_live_workspace(app)", 1
    )[0]
    live = source.split("function configure_live_workspace(app)", 1)[1].split(
        "function configure_deploy_workspace(app)", 1
    )[0]
    assert "app.configure_composition_controls()" in model
    assert "app.configure_composition_controls(live=true)" in live
    for control in ("VehicleCountDropDown", "MapDropDown", "TargetUavDropDown"):
        assert f"app.{control}" in model
        assert f"app.{control}" in live


def test_model_studio_filters_three_uav_mission_by_vehicle_count() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert "const SINGLE_UAV_MISSION_OPTIONS" in source
    assert 'const THREE_UAV_MISSION_OPTIONS = ["三机三角编队 8 字"]' in source
    assert "function is_three_uav_mission(app, mission)" in source
    assert "function mission_vehicle_count(app, mission)" in source
    assert "function mission_options_for_vehicle_count(app, vehicle_count)" in source

    sync = source.split("function sync_vehicle_controls(app)", 1)[1].split(
        "function configure_composition_controls(app; live=false)", 1
    )[0]
    assert "app.MissionDropDown.Items = mission_items" in sync
    assert "current_mission in mission_items ?" in sync
    assert "current_mission : mission_items[1]" in sync
    assert 'app.FormationDropDown.Value = "无"' in sync

    assert 'app.VehicleCountDropDown.Value = string(app.mission_vehicle_count(item.mission))' in source
    assert 'occursin("三机", item.mission)' not in source
    assert 'occursin("三机", app.MissionDropDown.Value)' not in source


def test_model_studio_header_is_compact_and_left_aligned() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert 'app.TitleLabel.HorizontalAlignment = "left"' in source
    assert "SubtitleLabel" not in source
    assert "控制器配置、模型验证与QGC运行交接" not in source
    assert "控制器配置、模型验证与 QGC 运行交接" not in source


def test_model_studio_controller_selector_matches_active_catalog() -> None:
    catalog = json.loads(
        (ROOT / "Config" / "control_platform" / "control_scheme_catalog.json").read_text(
            encoding="utf-8-sig"
        )
    )
    source = APP_SOURCE.read_text(encoding="utf-8")
    selector = source.split("const CONTROLLER_CATALOG = [", 1)[1].split(
        "]\nconst LEGACY_PROFILE_CONTROLLERS", 1
    )[0]
    active_ids = [scheme["scheme_id"] for scheme in catalog["schemes"]]
    assert len(active_ids) == 48
    assert len(re.findall(r'\(id="([^"]+)"', selector)) == 48
    assert all(f'id="{scheme_id}"' in selector for scheme_id in active_ids)
    assert "mu_synthesis" not in selector
    assert "neural_smc" not in selector
    assert "FamilyChanged" in source
    assert "IMPLEMENTED_COLOR" in source
    assert "app.controller_options_for_family(family)" in source


def test_model_studio_starts_offline_batch_with_base_process_api() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert "function run_process_in_directory(command_args, directory)" in source
    assert "command = Cmd(Cmd(command_args); dir=directory)" in source
    assert "process = run(command; wait=false)" in source
    assert "wait(process)" in source
    batch_runner = source.split("function run_offline_batch(app, profile_id)", 1)[1].split(
        "function request_offline_cancel", 1
    )[0]
    assert "Base.@async begin" in batch_runner
    assert "run_process_in_directory(command_args, PROJECT_ROOT)" in batch_runner
    assert 'app.append_console("批次阻断：" * sprint(showerror, error); level="错误")' in batch_runner


def test_model_studio_mil_callback_requires_matching_profile() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    mil_callback = source.split("function MilPressed(app, event)", 1)[1].split(
        "function CodegenPressed", 1
    )[0]
    assert "item.available && app.preset_matches_selection(item)" in mil_callback
    assert "Profile 与当前 UAV 数量、任务或控制链不一致；未启动仿真" in mil_callback


def test_live_workspace_groups_five_runtime_actions_in_middle_column() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    live = source.split("function configure_live_workspace(app)", 1)[1].split(
        "function configure_deploy_workspace(app)", 1
    )[0]
    assert "app.ApplyInjectionButton.Position = [494, 628, 210, 32]" in live
    assert "app.RestoreInjectionButton.Position = [724, 628, 210, 32]" in live
    assert "app.set_visible((app.ValidateButton, app.OpenModelButton), true)" in live
    assert 'app.ValidateButton.Text = "应用配置"' in live
    assert 'app.OpenModelButton.Text = "打开联合仿真模型"' in live
    assert 'app.PublishButton.Text = "发布并准备"' not in live


def test_model_workspace_removes_manual_timing_and_extra_primary_actions() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    for removed in ("仿真时长", "输出步长", "故障开始", "故障结束", "高级参数"):
        assert removed not in source
    model = source.split("function configure_model_workspace(app)", 1)[1].split(
        "function configure_live_workspace(app)", 1
    )[0]
    assert "app.set_visible((app.ValidateButton, app.OpenModelButton), true)" in model
    assert 'app.ValidateButton.Text = "应用配置"' in model
    assert 'app.OpenModelButton.Text = "打开仿真模型"' in model
    assert 'app.MilButton.Text = "开始仿真"' not in model


def test_model_studio_open_model_is_a_separate_non_simulation_entry() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert 'const OPEN_MODEL_SCRIPT = joinpath(PROJECT_ROOT, "Scripts", "ui", "open_model_studio_model.py")' in source
    assert '"--mode", mode' in source
    assert '"--controller-id", controller.id' in source
    assert '"--output-variant", output_variant' in source
    assert 'success(process) || error(' in source
    assert "请在 MWORKS 中自行点击仿真" in source
    script = ROOT / "Scripts" / "ui" / "open_model_studio_model.py"
    script_text = script.read_text(encoding="utf-8")
    worker = ROOT / "Scripts" / "ui" / "open_model_studio_model_worker.py"
    worker_text = worker.read_text(encoding="utf-8")
    assert "BASE_MODEL_FILES" in script_text
    assert "model_load_files(args.mode, model_file)" in script_text
    assert 'command.append("--check-model")' in script_text
    assert "visible_model_window(model_name)" in script_text
    assert "subprocess.Popen" in script_text
    assert 'result["worker_process_id"] = worker.pid' in script_text
    assert "user32.SetForegroundWindow(hwnd)" in script_text
    assert 'RUNNER_MODELS' in script_text
    assert 'choices=("model", "live", "codegen")' in script_text
    assert 'parser.add_argument("--controller-id", default="")' in script_text
    assert "resolve_controller_model" in script_text
    assert "PX4CTRL_CODEGEN_MODEL_FILE" in script_text
    assert 'args.mode == "codegen"' in script_text
    assert '"controller_id": args.controller_id' in script_text
    assert "GenerateModelCode" not in script_text
    assert "SimulateModel" not in script_text
    assert 'ModelingPy.StartSysplorer(start_mode="-gui", processPath=args.mworks_exe)' in worker_text
    assert "ModelingPy.OpenModelFile" in worker_text
    assert "ModelingPy.OpenModel" in worker_text
    assert "ModelingPy.CheckModel" in worker_text
    assert "while any(psutil.pid_exists(pid) for pid in tracked_pids):" in worker_text
    assert 'result["mworks_process_ids"]' in worker_text
    assert "psutil.pid_exists(pid)" in worker_text
    assert "SimulateModel" not in worker_text


def test_codegen_model_resolver_uses_current_graphical_model_map() -> None:
    spec = importlib.util.spec_from_file_location("open_model_studio_model", OPEN_MODEL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

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


def test_deploy_workspace_uses_two_columns_and_wide_console() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    deploy = source.split("function configure_deploy_workspace(app)", 1)[1].split(
        "function set_mode(app, mode)", 1
    )[0]
    assert "app.configure_console_workspace(left=614, width=802)" in deploy
    assert "app.ChainSectionLabel.Visible = false" in deploy
    assert 'app.configure_section(app.ConfigSectionLabel, "代码生成模型", [24, 144, 560, 34])' in deploy
    assert 'app.configure_section(app.InjectionSectionLabel, "操作日志", [614, 144, 802, 34])' in deploy
    assert 'app.CodegenButton.Text = "打开 MWORKS 代码生成模型"' in deploy
    assert 'app.set_visible((app.CodegenButton,), true)' in deploy


def test_model_studio_window_height_tracks_lowest_controls() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert "app.UIFigure.Position = [30, 30, 1440, 720]" in source
    assert "app.OpenModelButton.Position = [724, 674, 210, 38]" in source


def test_certification_runner_closes_windows_and_session() -> None:
    source = (ROOT / "Scripts" / "mworks" / "run_offline_profile_certification.py").read_text(
        encoding="utf-8"
    )
    assert '"--gui-reset-windows"' in source
    assert '"--shutdown-session"' in source
