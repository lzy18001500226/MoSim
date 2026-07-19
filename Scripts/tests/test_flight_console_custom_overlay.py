from __future__ import annotations

import argparse
import json
from pathlib import Path

from Scripts.ui import orchestrator_client
from Scripts.ui.check_qgc_windows_toolchain import QT_KIT, QT_MODULES, QT_VERSION, inspect
from Scripts.ui.materialize_qgc_custom_overlay import materialize
from Scripts.ui.generate_qgc_vendor_manifest import MOSIM_MAIN_WINDOW_PATCH, render


ROOT = Path(__file__).resolve().parents[2]
CUSTOM = ROOT / "apps" / "flight_console" / "mosim" / "custom"


def test_vendor_manifest_ignores_generated_gradle_cache(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "tracked.cc").write_text("source", encoding="utf-8")
    (tmp_path / "android" / ".gradle").mkdir(parents=True)
    (tmp_path / "android" / ".gradle" / "cache.bin").write_bytes(b"generated")
    rendered = render(tmp_path)
    assert "src/tracked.cc" in rendered
    assert ".gradle" not in rendered


def test_custom_overlay_uses_supported_qgc_extension_points() -> None:
    cmake = (CUSTOM / "CMakeLists.txt").read_text(encoding="utf-8")
    resources = (CUSTOM / "custom.qrc").read_text(encoding="utf-8")
    plugin = (CUSTOM / "src" / "CustomPlugin.cc").read_text(encoding="utf-8")
    qml = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    plan_qml = (CUSTOM / "src" / "PlanView.qml").read_text(encoding="utf-8")
    bridge_header = (CUSTOM / "src" / "MoSimOrchestratorBridge.h").read_text(encoding="utf-8")
    bridge_source = (CUSTOM / "src" / "MoSimOrchestratorBridge.cc").read_text(encoding="utf-8")
    assert "QGC_CUSTOM_BUILD" in cmake
    assert "CUSTOMCLASS=CustomPlugin" in cmake
    assert "QGroundControl/FlightDisplay/FlyViewCustomLayer.qml" in resources
    assert "QGroundControl/Controls/PlanView.qml" in resources
    assert "QGroundControl/Controls/FactoryPlanMapOverlay.qml" in resources
    assert 'setContextProperty(QStringLiteral("mosimOrchestrator")' in plugin
    assert "4（规模验收未完成）" in qml and "9（规模验收未完成）" in qml
    assert "RViz点云地图" in qml and "UE三维视图" in qml
    assert "应用风扰" in qml and "应用电机故障" in qml
    assert "cascade_pid_figure8_generated_c_v1.json" in qml
    assert "model: mosimOrchestrator.controllers" in qml
    assert "disabled_reason" in qml
    assert "启动仿真并连接飞机" in qml
    assert "启动并执行自动任务" in qml
    assert "无需手动解锁" in qml
    assert 'readonly property bool flightConfigurationEditable' in qml
    assert 'mosimOrchestrator.lifecycleState !== "starting"' in qml
    assert 'mosimOrchestrator.lifecycleState !== "running"' in qml
    assert "px4ctrl_ground_standby_v1.json" in qml
    assert "Take off (W/A/S/D)" not in qml
    assert "启动进度" in qml
    assert "一键关闭全部RViz" in qml
    assert "录制UE画面" in qml and "停止UE录制" in qml
    assert "readonly property var controllers" not in qml
    assert "mosimOrchestrator.attachDisplays()" in qml
    assert "mosimOrchestrator.detachDisplays()" in qml
    assert "WindowContainer" in qml
    assert "window: mosimOrchestrator.unrealWindow" in qml
    assert "anchors.fill: parent" in qml
    assert "setUnrealOverlayHole" in qml
    assert "factoryMapPreview.x" in qml and "factoryMapPreview.y" in qml
    assert "factoryMapPreview.width + 24" not in qml
    assert "!factoryMapExpanded" in qml
    assert "onMosimNativeOverlayVisibleChanged" in qml
    assert "setUnrealPresentationSuppressed" in qml
    assert "FlyViewBottomRightRowLayout" in qml
    assert "visible: activeVehicle !== null && !factoryMapExpanded" in qml
    main_window = (ROOT / "apps" / "flight_console" / "vendor" / "qgroundcontrol" / "src" / "UI" / "MainWindow.qml").read_text(encoding="utf-8")
    assert "mosimNativeOverlayVisible" in main_window
    assert "toolDrawer.visible" in main_window and "indicatorDrawer.visible" in main_window
    assert "重试UE嵌入" in qml
    assert "Q_PROPERTY(QWindow *unrealWindow" in bridge_header
    assert "DISPLAY_PROCESSES.json" in bridge_source
    assert "model_studio_active_run.json" in bridge_source
    assert "recoverRunIdentity();" in bridge_source
    assert "_startupRunRecoveryPending = !_runId.isEmpty()" in bridge_source
    assert 'completedAction == QStringLiteral("get_run_state")' in bridge_source
    assert 'invoke({QStringLiteral("get_run_state"), QStringLiteral("--run-id"), _runId})' in bridge_source
    assert "QWindow::fromWinId" in bridge_source
    assert "findLargestVisibleWindow" in bridge_source
    assert "EnumChildWindows(GetDesktopWindow()" in bridge_source
    assert "ShowWindow(search.bestWindow, SW_HIDE)" in bridge_source
    assert "confirmUnrealContainerReady" in bridge_header
    assert "GetParent(window)" in bridge_source
    assert "ShowWindow(window, SW_SHOWNA)" in bridge_source
    assert "window_discovered_hidden" in bridge_source
    assert "_unrealDiscoveryAttempt >= 360" in bridge_source
    assert "managed_external" not in bridge_source
    assert "cycleUnrealView" in qml and "zoomUnrealIn" in qml and "zoomUnrealOut" in qml
    assert "PostMessage(window, WM_KEYDOWN" in bridge_source
    assert "SetWindowRgn(window, visibleRegion, TRUE)" in bridge_source
    assert "CombineRgn(visibleRegion, visibleRegion, overlayHole, RGN_DIFF)" in bridge_source
    assert "resetUnrealWindowRegion();" in bridge_source
    assert "operator_map_catalog.json" in bridge_source
    ue_launcher = (ROOT / "Scripts" / "ui" / "attach_orchestrated_displays.ps1").read_text(encoding="utf-8")
    ue_camera = (ROOT / "UE5" / "MoSimSceneLibrary" / "Source" / "MoSimSceneLibrary" / "MworksReviewCameraPawn.cpp").read_text(encoding="utf-8")
    ue_input = (ROOT / "UE5" / "MoSimSceneLibrary" / "Config" / "DefaultInput.ini").read_text(encoding="utf-8")
    assert "-MoSimEmbeddedViewport" in ue_launcher
    assert "hidden_until_qgc_embed" in ue_launcher
    assert "Save-ProcessRecords" in ue_launcher
    assert "bShowMouseCursor = bEmbeddedViewport" in ue_camera
    assert "EMouseLockMode::DoNotLock" in ue_camera
    assert "MworksReviewZoom" in ue_input
    assert 'Key=N' in ue_input and 'Key=M' in ue_input
    assert "GetInputMouseDelta(MouseDeltaX, MouseDeltaY)" in ue_camera
    assert "FollowMouseOrbitSensitivityDeg" in ue_camera
    assert "MworksReviewOrbitLeft" in ue_input and "Key=F16" in ue_input
    assert "IsEmbeddedReviewInputActive()" in ue_camera
    assert "GetAsyncKeyState" in ue_camera
    assert "AsyncReviewAxis(VK_RIGHT, VK_LEFT)" in ue_camera
    assert "AsyncReviewAxis(VK_UP, VK_DOWN)" in ue_camera
    assert "AsyncReviewAxis('D'" not in ue_camera
    assert "AsyncReviewAxis('W'" not in ue_camera
    assert "PtInRegion" in ue_camera
    assert "orbitUnreal" in qml and "PixelsPerNudge" in bridge_source
    assert "PixelsPerNudge = 1.0" in bridge_source
    assert 'sequence: "N"' in qml and 'sequence: "M"' in qml
    assert 'sequence: "W"' not in qml
    assert 'sequence: "A"' not in qml
    assert 'sequence: "S"' not in qml
    assert 'sequence: "D"' not in qml
    assert 'sequence: "Left"' in qml and 'sequence: "Right"' in qml
    assert 'sequence: "Up"' in qml and 'sequence: "Down"' in qml
    assert qml.count("context: Qt.ApplicationShortcut") >= 4
    assert qml.count("autoRepeat: true") >= 4
    assert "z: 0" in qml and "z: 100" in qml
    assert "factoryActualTrackPreview" in qml
    assert "factoryActualTrackExpanded" in qml
    assert "factoryTaskPathPreview" in qml
    assert "factoryTaskPathExpanded" in qml
    assert 'var kinds = ["expected", "future"]' in qml
    assert 'kind === "future"' in qml
    assert 'Number(path.updated_at || 0) > 5.0' in qml
    assert "runtimeVehicles()" in qml
    assert "vehicleYawDegrees" in qml
    assert "actualTracksByVehicle" in qml
    assert "Q_PROPERTY(QVariantMap runtimeTelemetry" in bridge_header
    assert 'completedAction == QStringLiteral("get_telemetry")' in bridge_source
    assert "telemetryRunId == _runId" in bridge_source
    assert 'text: "切换UE视角"' in qml
    assert "injectionVehicle.currentIndex = 0" in qml
    assert "Factory image is the only operator map surface" in plan_qml
    assert 'color: "#d9dde0"' in plan_qml
    assert "MapScale" not in plan_qml
    assert "factoryPlanMap.mapCenter" in plan_qml
    assert "id: factoryPlanMap" in plan_qml
    assert "resource_url" in plan_qml
    assert "PlanMasterController" in plan_qml
    assert "MissionItemMapVisual" in plan_qml
    assert "VehicleMapItem" in plan_qml
    overrides = (CUSTOM / "cmake" / "CustomOverrides.cmake").read_text(encoding="utf-8")
    assert 'QGC_APP_NAME "MoSimFlightConsole"' in overrides
    assert "CPM_px4-gpsdrivers_SOURCE" in overrides
    assert "8fdef3bc0cb7820119abdb7320ad3992af2e440f" in overrides


def test_materializer_keeps_source_and_target_separate(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    (source / "CMakeLists.txt").write_text("set(TEST ON)\n", encoding="utf-8")
    manifest = materialize(source, target, project_root=tmp_path)
    assert (target / "CMakeLists.txt").read_text(encoding="utf-8") == "set(TEST ON)\n"
    assert manifest["files"]["CMakeLists.txt"]
    assert source != target


def test_vendor_digest_excludes_generated_custom_overlay(tmp_path: Path) -> None:
    (tmp_path / "upstream.txt").write_text("upstream\n", encoding="utf-8")
    custom = tmp_path / "custom"
    custom.mkdir()
    (custom / "generated.txt").write_text("generated\n", encoding="utf-8")
    rendered = render(tmp_path)
    assert "upstream.txt" in rendered
    assert "custom/generated.txt" not in rendered


def test_vendor_digest_normalizes_only_the_reviewed_main_window_patch(tmp_path: Path) -> None:
    main_window = tmp_path / "src" / "UI" / "MainWindow.qml"
    main_window.parent.mkdir(parents=True)
    upstream = "ApplicationWindow {\n    visible: true\n}\n"
    main_window.write_text(upstream, encoding="utf-8", newline="\n")
    baseline = render(tmp_path)
    main_window.write_text(
        upstream.replace("    visible: true\n", "    visible: true\n" + MOSIM_MAIN_WINDOW_PATCH),
        encoding="utf-8",
        newline="\n",
    )
    assert render(tmp_path) == baseline


def test_client_builds_audited_injection_payload(tmp_path: Path, monkeypatch) -> None:
    active = tmp_path / "active.json"
    active.write_text('{"run_id":"run-test","profile_hash":"hash-test"}', encoding="utf-8")
    monkeypatch.setattr(orchestrator_client, "ACTIVE_RUN", active)
    args = argparse.Namespace(
        action="apply_injection",
        run_id=None,
        profile_path=None,
        controller_id=None,
        vehicle_count=None,
        wind_speed_mps=0.0,
        target="motor_effectiveness",
        value=0.6,
        rotor_index=2,
        vehicle_id="uav2",
        ramp_s=0.2,
        duration_s=3.0,
        display=[],
        session_id=None,
    )
    payload = orchestrator_client.build_payload(args)
    assert payload["run_id"] == "run-test"
    assert payload["command"]["target"] == "motor_effectiveness"
    assert payload["command"]["rotor_index"] == 2
    assert payload["command"]["vehicle_id"] == "uav2"
    assert payload["command"]["source"] == "flight_console"


def test_client_builds_display_attach_without_shell_arguments() -> None:
    args = argparse.Namespace(
        action="attach_display", session_id="display-1234567890", run_id=None,
        profile_path=None, controller_id=None, vehicle_count=None, wind_speed_mps=0.0,
        target=None, value=None, rotor_index=None, vehicle_id=None, ramp_s=0.0, duration_s=0.0, display=[],
    )
    assert orchestrator_client.build_payload(args) == {
        "schema": "mosim.orchestrator.request.v1",
        "action": "attach_display",
        "session_id": "display-1234567890",
    }


def test_windows_toolchain_preflight_is_read_only_and_version_pinned(monkeypatch) -> None:
    monkeypatch.setenv("PATH", "")
    report = inspect(qt_dir="Z:/missing-qt")
    assert report["status"] == "blocked"
    assert report["required"]["qt_version"] == QT_VERSION == "6.8.3"
    assert report["required"]["qt_kit"] == QT_KIT == "msvc2022_64"
    assert set(report["missing_qt_modules"]) == set(QT_MODULES)
    assert report["mutated_system"] is False


def test_windows_build_entrypoint_never_installs_dependencies() -> None:
    script = (ROOT / "Scripts" / "ui" / "build_flight_console.ps1").read_text(encoding="utf-8")
    lowered = script.lower()
    assert "winget install" not in lowered
    assert "choco install" not in lowered
    assert "materialize_qgc_custom_overlay.py" in script
    assert "generate_qgc_vendor_manifest.py" in script
    assert 'Ninja Multi-Config' in script
    assert "[switch]$Incremental" in script
    assert 'if ($Incremental) { "" } else { "--fresh " }' in script
    tick = chr(96)
    assert script.index(f'set {tick}"PATH=') < script.index(f'call {tick}"$VsDevCmd')


def test_factory_floorplan_is_packaged_for_the_flight_console() -> None:
    resource = (ROOT / "apps" / "flight_console" / "mosim" / "custom" / "custom.qrc").read_text(
        encoding="utf-8"
    )
    qml = (
        ROOT / "apps" / "flight_console" / "mosim" / "custom" / "src" / "FlyViewCustomLayer.qml"
    ).read_text(encoding="utf-8")
    assert 'prefix="/Custom/maps/factory_l2/v1"' in resource
    assert 'maps/factory_l2/v1/floorplan.png' in resource
    assert 'qrc:/Custom/maps/factory_l2/v1/floorplan.png' in qml
    assert "factoryMapExpanded" in qml
    assert "Flickable" in qml
    assert "factoryMapImage" in qml
    assert "factoryMapFlickable" in qml
    assert "factoryFlightMap" not in qml
    assert "factoryOverlay" not in qml
    assert "MapScale" not in qml
    assert "factoryMapScale" not in qml

    catalog = json.loads(
        (ROOT / "Config" / "control_platform" / "operator_map_catalog.json").read_text(encoding="utf-8")
    )
    assert "mosimOrchestrator.operatorMap" in qml
    assert "factoryMapCanvas.zoomFactor" in qml
    assert "function zoomAt(viewX, viewY, wheelDelta)" in qml
    assert "imageRatioX" in qml and "imageRatioY" in qml
    assert "onWheel: function(wheel)" in qml
    assert "contentX" in qml and "contentY" in qml
    assert "enabled: factoryMapExpanded" in qml
    assert "onClicked: factoryMapExpanded = false" in qml
    assert "visible: window !== null" in qml
    assert "setUnrealPresentationSuppressed(mainWindow.mosimNativeOverlayVisible)" in qml
    assert "mosimOrchestrator.refreshTelemetry()" in qml
    assert "Math.abs(Date.now() / 1000.0 - timestamp) <= 2.5" in qml
    assert "vehicle.state.connected" in qml
    factory = catalog["maps"][0]
    assert factory["map_id"] == "factory_l2"
    assert factory["world_bounds_m"]["max_x_m"] - factory["world_bounds_m"]["min_x_m"] > 1100
    assert factory["mission_publication"]["status"] == "blocked_until_runtime_round_trip_gate"


def test_competition_console_exposes_chinese_tasks_and_native_manual_control() -> None:
    qml = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    bridge_header = (CUSTOM / "src" / "MoSimOrchestratorBridge.h").read_text(encoding="utf-8")
    for label in (
        "单机定点操纵",
        "单机8字飞行",
        "生成代码控制器8字飞行",
        "FUEL单机自主探索",
        "三机固定编队避障",
        "MWORKS实时联合仿真（50 Hz）",
    ):
        assert label in qml
    assert "activeVehicle.virtualTabletJoystickValue(roll, pitch, 0.0, 0.5)" in qml
    assert "readonly property bool manualControlReady" in qml
    assert 'activeVehicle.flightMode === "Position"' in qml
    assert "running: manualKeyboardEnabled && manualControlReady" in qml
    assert "manualModeCheck.checked = false" in qml
    assert "manualTaskSelected)" in qml
    assert "全过程必须在QGC确认阶段、告警和结束状态" in qml
    assert "function flightAuthorityText()" in qml
    assert 'text: "控制权与解锁责任：" + flightAuthorityText()' in qml
    assert "QGC原生控制：你负责解锁、起飞、Position模式操纵和降落" in qml
    assert "编队Mission Adapter独占控制：自动逐机解锁、起飞、编队任务和降落" in qml
    assert "任务Mission Adapter独占控制：自动解锁、起飞、任务执行和降落" in qml
    assert "function qgcConnectedVehicleCount()" in qml
    assert "function qgcArmedVehicleCount()" in qml
    assert "function runtimeVehicleStateText(vehicle)" in qml
    assert "function runtimeVehiclePositionText(vehicle)" in qml
    assert 'text: "逐机运行状态"' in qml
    assert "以下为逐机遥测确认，不代替任务Adapter终态ACK" in qml
    assert "model: root.runtimeVehicles()" in qml
    assert 'String(modelData.vehicle_id || "未知飞机")' in qml
    assert "function missionStatusText()" in qml
    assert 'QGCLabel { text: "任务Adapter确认"; font.bold: true }' in qml
    assert 'text: "Adapter：" + String(missionStatus().adapter_id || "-")' in qml
    assert 'root.missionAdapterVehicleText(modelData)' in qml
    assert "状态不完整：收到 " in qml
    assert 'text: "飞行阶段：" + flightPhaseText()' in qml
    assert 'text: "任务Adapter阶段：" + missionStatusText()' in qml
    assert '"run_starting": "正在启动飞行运行时"' in qml
    assert "operationStageText(mosimOrchestrator.operationStage)" in qml
    assert "interval: 40" in qml
    assert "QGC原生解锁/起飞" in qml
    assert "下一步：" in qml
    assert "selectionMatchesPreparedRun()" in qml
    assert "另一个任务仍在运行" in qml
    assert "experimentProfileId" in bridge_header
    assert "selectedControllerId" in bridge_header
    assert "selectedVehicleCount" in bridge_header
    assert "助手将读取当前Profile" in qml
    assert "任何飞行操作仍需人工确认" in qml
    assert "factory_l2_fuel_fixed64_exploration_v1.json" in qml
    assert 'label: "FUEL单机自主探索"' in qml
    assert 'text: "请求安全停止"' in qml
    assert "mosimOrchestrator.requestSafeStop()" in qml
    assert 'text: "停止当前仿真"' in qml
    assert "function canStopRuntime()" in qml
    assert 'mosimOrchestrator.lifecycleState === "starting"' in qml
    assert "runtime_not_airborne_startup_stop_allowed" not in qml
    assert "qgcConnectedVehicleCount() === expected && qgcArmedVehicleCount() === 0" in qml
    assert 'mosimOrchestrator.operationStage === "Safe stop complete"' in qml
    assert '"runtime_stop_rejected_vehicle_armed"' in qml
    assert "requestSafeStop" in bridge_header


def test_fuel_display_route_uses_accepted_rviz_configs() -> None:
    launcher = (ROOT / "Scripts" / "ui" / "launch_ros1_display.sh").read_text(encoding="utf-8")
    assert 'planner_profile}" == "fuel_single_exploration"' in launcher
    assert "sunray_ros1_factory_fuel_pointcloud_review.rviz" in launcher
    assert "sunray_ros1_factory_fuel_grid3d_review.rviz" in launcher
    assert "/mosim/goal4/livox_world_accumulated" in launcher
    assert "/mosim/goal4/occupancy_object_review" in launcher


def test_windows_run_entrypoint_uses_private_runtime_and_reuses_existing_instance() -> None:
    script = (ROOT / "Scripts" / "ui" / "run_flight_console.ps1").read_text(encoding="utf-8")
    assert "flight_console_windows_toolchain_preflight.json" in script
    assert 'Get-Process -Name "MoSimFlightConsole"' in script
    assert "detected.qt_root" in script
    assert "detected.gstreamer_root" in script
    assert "Start-Process" in script
    assert "build/flight-console-qgc/Release/MoSimFlightConsole.exe" in script


def test_private_toolchain_layout_is_supported(tmp_path: Path, monkeypatch) -> None:
    tool_root = tmp_path / "tools"
    ninja = tool_root / "python" / "Scripts" / "ninja.exe"
    qt = tool_root / "qt" / QT_VERSION / QT_KIT
    gst = tool_root / "gstreamer" / "gstreamer" / "1.0" / "msvc_x86_64"
    for file in (ninja, qt / "bin" / "qtpaths6.exe", gst / "bin" / "gst-launch-1.0.exe"):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(b"")
    for module in QT_MODULES:
        (qt / "lib" / "cmake" / module).mkdir(parents=True)
    monkeypatch.setenv("PATH", "")
    report = inspect(tool_root=tool_root)
    assert report["detected"]["ninja"] == str(ninja.resolve())
    assert report["detected"]["qt_root"] == str(qt.resolve())
    assert report["detected"]["gstreamer_root"] == str(gst.resolve())


def test_private_installer_stays_inside_repository_and_uses_admin_extract() -> None:
    script = (ROOT / "Scripts" / "ui" / "install_flight_console_toolchain.ps1").read_text(encoding="utf-8")
    assert ".tools/flight-console" in script
    assert "ToolRoot must stay inside the MoSim repository" in script
    assert '"aqtinstall==3.3.0"' in script
    assert '"ninja==1.13.0"' in script
    assert "1437DC5D2FE7F3C6F9F24396DBAEB55C79A4F9E0F95D8EF559AD14ADB0237FAF" in script
    assert '"/a ' in script
    assert "-Verb RunAs" not in script
