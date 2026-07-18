from Scripts.ui.export_model_studio_catalog import build_catalog, render_tsv
from apps.model_studio.tools.generate_slapp import build_project


def test_catalog_is_registry_and_profile_driven() -> None:
    catalog = build_catalog()
    profiles = {profile["profile_id"]: profile for profile in catalog["profiles"]}
    assert profiles["px4ctrl_figure8_baseline_v1"]["controller_id"] == "px4ctrl"
    assert profiles["px4ctrl_figure8_baseline_v1"]["vehicle_count"] == 1
    assert profiles["factory_l2_three_uav_swarm_formation_v1"]["vehicle_count"] == 3
    assert profiles["factory_l2_three_uav_swarm_formation_v1"]["enabled"] is True
    vehicles = {vehicle["vehicle_count"]: vehicle for vehicle in catalog["vehicles"]}
    assert vehicles[1]["enabled"] is True
    assert vehicles[3]["enabled"] is True
    assert all(not vehicles[count]["enabled"] for count in range(4, 10))
    assert "PROFILE\tpx4ctrl_figure8_baseline_v1\t" in render_tsv(catalog)


def test_generated_app_exposes_three_modes_and_layered_control_chain() -> None:
    project = build_project()
    callbacks = {callback["name"]: callback["code"] for callback in project["callbackFunctions"]}
    children = {child["variableName"]: child for child in project["figure"]["children"]}

    assert {"OfflineModePressed", "LiveModePressed", "DeployModePressed"} <= callbacks.keys()
    assert children["OfflineModeButton"]["text"] == "离线建模验证"
    assert children["LiveModeButton"]["text"] == "实时联合仿真"
    assert children["DeployModeButton"]["text"] == "生成代码部署"
    assert children["PositionDropDown"]["label"] == "位置 / 平动外环"
    assert children["AttitudeDropDown"]["label"] == "姿态 / 角速度内环"
    assert children["AttitudeDropDown"]["enable"] is False
    assert children["AttitudeDropDown"]["value"] == "PX4 内置姿态/角速度环 [锁定]"
    assert children["AugmentationDropDown"]["label"] == "增强与扰动补偿"
    assert children["OutputDropDown"]["value"] == "ATTITUDE_THRUST [锁定]"


def test_generated_app_is_ui_only_and_separates_offline_from_qgc_actions() -> None:
    project = build_project()
    callbacks = {callback["name"]: callback["code"] for callback in project["callbackFunctions"]}
    children = {child["variableName"]: child for child in project["figure"]["children"]}

    assert project["info"]["version"] == "0.5.0"
    assert {
        "ValidatePressed", "PublishPressed", "PreparePressed", "QgcPressed",
        "SafeStopPressed", "OpenModelPressed", "MilPressed", "CodegenPressed",
        "ResultPressed", "ApplyInjectionPressed", "RestoreInjectionPressed",
    } <= callbacks.keys()
    serialized = str(project)
    assert "orchestrator_client.py" not in serialized
    assert "start_run" not in serialized
    assert "stop_run" not in serialized
    assert "UIAxes" not in children
    assert "PreviewButton" not in children
    assert children["PublishButton"]["text"] == "发布 Profile"
    assert children["PrepareButton"]["text"] == "准备运行"
    assert children["QgcButton"]["text"] == "进入 QGC"
    assert children["SafeStopButton"]["text"] == "请求安全停止"
    assert children["OpenModelButton"]["text"] == "打开模型"
    assert children["MilButton"]["text"] == "运行 MWORKS MIL"
    assert children["CodegenButton"]["text"] == "生成 C 代码"


def test_generated_app_has_pending_and_applied_injection_surfaces() -> None:
    project = build_project()
    children = {child["variableName"]: child for child in project["figure"]["children"]}

    sliders = [
        children["WindSlider"],
        children["Motor1Slider"],
        children["Motor2Slider"],
        children["Motor3Slider"],
        children["Motor4Slider"],
    ]
    assert all(control["type"] == "slider" for control in sliders)
    assert children["WindSlider"]["limits"] == [0.0, 20.0]
    assert all(control["limits"] == [0.0, 1.0] for control in sliders[1:])
    assert "待应用值" in children["InjectionValuesLabel"]["text"]
    assert "实际值" in children["InjectionValuesLabel"]["text"]
    assert children["ApplyInjectionButton"]["text"] == "应用"
    assert children["RestoreInjectionButton"]["text"] == "恢复正常"


def test_generated_app_controls_stay_inside_fixed_review_canvas() -> None:
    project = build_project()
    figure = project["figure"]
    _, _, canvas_width, canvas_height = figure["position"]

    assert [canvas_width, canvas_height] == [1440, 900]
    for child in figure["children"]:
        x, y, width, height = child["position"]
        assert x >= 0 and y >= 0, child["variableName"]
        assert width > 0 and height > 0, child["variableName"]
        assert x + width <= canvas_width, child["variableName"]
        assert y + height <= canvas_height, child["variableName"]
