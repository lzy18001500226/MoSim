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
    fly_map = (CUSTOM / "src" / "FactoryFlyMap.qml").read_text(encoding="utf-8")
    plan_qml = (CUSTOM / "src" / "PlanView.qml").read_text(encoding="utf-8")
    plan_overlay_qml = (CUSTOM / "src" / "FactoryPlanMapOverlay.qml").read_text(encoding="utf-8")
    bridge_header = (CUSTOM / "src" / "MoSimOrchestratorBridge.h").read_text(encoding="utf-8")
    bridge_source = (CUSTOM / "src" / "MoSimOrchestratorBridge.cc").read_text(encoding="utf-8")

    assert "QGC_CUSTOM_BUILD" in cmake
    assert "CUSTOMCLASS=CustomPlugin" in cmake
    assert "QGroundControl/FlightDisplay/FlyViewCustomLayer.qml" in resources
    assert "QGroundControl/Controls/PlanView.qml" in resources
    assert "QGroundControl/Controls/FactoryPlanMapOverlay.qml" in resources
    assert "QGroundControl/Controls/FactoryFlyMap.qml" in resources
    assert 'setContextProperty(QStringLiteral("mosimOrchestrator")' in plugin
    assert 'QMetaObject::invokeMethod(rootObject, "showPlanView")' not in plugin

    assert "FactoryFlyMap {" in qml
    assert "mapConfig: mosimOrchestrator.operatorMap || ({})" in qml
    assert "runManifest: mosimOrchestrator.runManifest || ({})" in qml
    assert "mapState: (mosimOrchestrator.runtimeTelemetry || ({})).map_state || ({})" in qml
    assert "runId: mosimOrchestrator.runId" in qml
    assert "WindowContainer" not in qml
    assert "mosimOrchestrator.unrealWindow" not in qml
    assert "factoryMapPreview" not in qml
    assert "factoryMapExpanded" not in qml
    assert "切换UE视角" not in qml
    assert "独立UE视图" in qml
    assert "RViz点云地图" in qml and "RViz栅格地图" in qml
    assert "暂存风扰" in qml and "暂存电机故障" in qml
    assert "应用待应用故障" in qml and "恢复正常" in qml
    assert "应用风扰" not in qml and "应用电机故障" not in qml
    assert "mosimOrchestrator.stageWind" in qml
    assert "mosimOrchestrator.stageMotorEffectiveness" in qml
    assert "mosimOrchestrator.applyStagedInjection()" in qml
    assert "mosimOrchestrator.restoreNormal" in qml
    assert "pendingInjectionText()" in qml
    assert "一键关闭全部RViz" in qml
    assert "readonly property var profiles: mosimOrchestrator.operatorProfiles || []" in qml
    assert "model: profiles" in qml
    assert "controllerCatalogSynced" not in qml
    assert "controllerBox" not in qml and "vehicleBox" not in qml and "vehicleCounts" not in qml
    assert "disabled_reason" in qml
    assert "FlyViewBottomRightRowLayout" in qml

    assert "required property var mapConfig" in fly_map
    assert "required property var runManifest" in fly_map
    assert "required property var mapState" in fly_map
    assert "required property string runId" in fly_map
    assert "function zoomAt(viewX, viewY, wheelDelta)" in fly_map
    assert "imageRatioX" in fly_map and "imageRatioY" in fly_map
    assert "Flickable" in fly_map and "onWheel: function(wheel)" in fly_map
    assert "function fitMap()" in fly_map
    assert "niceScaleMeters" in fly_map
    assert "mapState.run_id" in fly_map
    assert "mosim.operator_map_state.v1" in fly_map
    assert "received_at_unix_s" in fly_map
    assert "mapIdentityMatches" in fly_map
    assert "coordinate_contract_status" in fly_map
    assert "rosbag_replay" in fly_map
    assert "validWorldPoint" in fly_map
    assert "task_paths" in fly_map
    assert "actualTracksByVehicle" in fly_map
    assert "formationTarget" in fly_map and "explorationBoundary" in fly_map

    assert "Q_PROPERTY(QVariantMap operatorMap" in bridge_header
    assert "Q_PROPERTY(QVariantMap runtimeTelemetry" in bridge_header
    assert "Q_PROPERTY(QVariantList operatorProfiles" in bridge_header
    assert "Q_PROPERTY(QVariantMap pendingInjection" in bridge_header
    assert "stageWind" in bridge_header and "stageMotorEffectiveness" in bridge_header
    assert "applyStagedInjection" in bridge_header and "restoreNormal" in bridge_header
    assert "operator_map_catalog.json" in bridge_source
    assert "telemetryRunId == _runId" in bridge_source
    assert "_autoAttachUnrealAfterStart" not in bridge_header
    assert "_autoAttachUnrealAfterStart" not in bridge_source
    assert "QTimer::singleShot(0, this, &MoSimOrchestratorBridge::refreshUnrealEmbedding)" not in bridge_source

    assert "Factory image is the only operator map surface" in plan_qml
    assert "FactoryPlanMapOverlay" in plan_qml
    assert "resource_url" in plan_overlay_qml
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
    fly_qml = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    fly_map = (CUSTOM / "src" / "FactoryFlyMap.qml").read_text(encoding="utf-8")

    assert 'prefix="/Custom/maps/factory_l2/v1"' in resource
    assert 'maps/factory_l2/v1/floorplan.png' in resource
    assert "FactoryFlyMap {" in fly_qml
    assert 'source: String(root.mapConfig.resource_url || "")' in fly_map
    assert "mapConfig.enabled === true" in fly_map
    assert "world_bounds_m" in fly_map
    assert "function zoomAt(viewX, viewY, wheelDelta)" in fly_map
    assert "function fitMap()" in fly_map
    assert "onWheel: function(wheel)" in fly_map
    assert "metersPerPixel" in fly_map and "niceScaleMeters" in fly_map
    assert "taskBoundaryCanvas" in fly_map
    assert "taskPathCanvas" in fly_map
    assert "actualTrackCanvas" in fly_map
    assert "property bool showVehicles: true" in fly_map
    assert "property bool showActualTracks: true" in fly_map
    assert "property bool showExpectedPath: true" in fly_map
    assert "property bool showFuturePath: true" in fly_map
    assert "property bool showTaskBoundary: true" in fly_map
    assert "property bool showFormationTarget: true" in fly_map
    assert "showVehicles: root.showMapVehicles" in fly_qml
    assert "showActualTracks: root.showMapActualTracks" in fly_qml
    assert 'text: "二维地图图层"' in fly_qml
    assert "property bool replayTelemetryMonitoring: false" in fly_qml
    assert 'text: root.replayTelemetryMonitoring ? "停止回放监看" : "开始回放监看"' in fly_qml
    assert "runtimeTelemetrySourceText()" in fly_qml
    assert "WindowContainer" not in fly_qml
    assert "setUnrealOverlayHole" not in fly_qml

    catalog = json.loads(
        (ROOT / "Config" / "control_platform" / "operator_map_catalog.json").read_text(encoding="utf-8")
    )
    factory = catalog["maps"][0]
    assert factory["map_id"] == "factory_l2"
    assert factory["map_version"] == "v1"
    assert factory["asset_sha256"]
    assert factory["coordinate_contract_id"] == "factory_l2_mworks_world_v1"
    assert factory["coordinate_contract_status"] == "pending_runtime_validation"
    assert factory["resource_url"] == "qrc:/Custom/maps/factory_l2/v1/floorplan.png"
    assert factory["world_bounds_m"]["max_x_m"] - factory["world_bounds_m"]["min_x_m"] > 1100
    assert factory["indoor_task_overlay_bounds_m"]["max_x_m"] - factory["indoor_task_overlay_bounds_m"]["min_x_m"] > 170
    assert factory["mission_publication"]["status"] == "blocked_until_runtime_round_trip_gate"


def test_plan_view_uses_georeferenced_factory_overlay() -> None:
    plan_view = (CUSTOM / "src" / "PlanView.qml").read_text(encoding="utf-8")
    overlay = (CUSTOM / "src" / "FactoryPlanMapOverlay.qml").read_text(encoding="utf-8")

    assert "FactoryPlanMapOverlay {" in plan_view
    assert "map: editorMap" in plan_view
    assert "mapConfig: mosimOrchestrator.operatorMap" in plan_view
    assert "runManifest: mosimOrchestrator.runManifest" in plan_view
    assert "id: factoryPlanMap" in plan_view
    assert "editorMap.center = factoryPlanMap.mapCenter" in plan_view
    assert "anchors.fill: parent\n                    source:" not in plan_view

    assert "map.fromCoordinate(northWest, false)" in overlay
    assert "map.fromCoordinate(southEast, false)" in overlay
    assert "function coordinateForWorld(worldX, worldY)" in overlay
    assert "mapCenter.atDistanceAndAzimuth" in overlay
    assert "explorationBoundaryValid" in overlay
    assert "configuredBoundary" in overlay
    assert "scenarioBoundaryValid ? scenarioBoundary : configuredBoundary" in overlay
    assert 'border.color: "#20c7b7"' in overlay


def test_competition_console_exposes_chinese_tasks_and_native_manual_control() -> None:
    qml = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    fly_map = (CUSTOM / "src" / "FactoryFlyMap.qml").read_text(encoding="utf-8")
    bridge_header = (CUSTOM / "src" / "MoSimOrchestratorBridge.h").read_text(encoding="utf-8")
    assert "operatorProfiles" in bridge_header
    assert "readonly property var profiles: mosimOrchestrator.operatorProfiles || []" in qml
    assert "controller_label" in qml and "vehicle_count" in qml
    assert "model: profiles" in qml
    assert "activeVehicle.virtualTabletJoystickValue(roll, pitch, 0.0, 0.5)" in qml
    assert "readonly property bool manualControlReady" in qml
    assert 'activeVehicle.flightMode === "Position"' in qml
    assert "running: manualKeyboardEnabled && manualControlReady" in qml
    assert "manualModeCheck.checked = false" in qml
    assert "manualTaskSelected)" in qml
    assert "function flightAuthorityText()" in qml
    assert 'text: "控制权与解锁责任：" + flightAuthorityText()' not in qml
    assert "QGC原生控制：你负责解锁、起飞、Position模式操纵和降落" in qml
    assert "编队Mission Adapter独占控制：自动逐机解锁、起飞、编队任务和降落" in qml
    assert "任务Mission Adapter独占控制：自动解锁、起飞、任务执行和降落" in qml
    assert "function qgcConnectedVehicleCount()" in qml
    assert "function qgcArmedVehicleCount()" in qml
    assert "function runtimeVehicleStateText(vehicle)" in qml
    assert "function runtimeVehiclePositionText(vehicle)" in qml
    assert 'text: "逐机运行状态"' in qml
    assert "以下为逐机遥测确认，不代替任务Adapter终态ACK" not in qml
    assert "model: root.runtimeVehicles()" in qml
    assert 'String(modelData.vehicle_id || "未知飞机")' in qml
    assert "function missionStatusText()" in qml
    assert "FactoryFlyMap {" in qml
    assert 'text: "地图轨迹：" + factoryFlyMap.taskPathStatusText()' in qml
    assert "function explorationBoundary()" in fly_map
    assert "function paintTaskBoundary" in fly_map
    assert "taskBoundaryCanvas" in fly_map
    assert "function formationTarget()" in fly_map
    assert "function paintFormationTarget" in fly_map
    assert "formationTargetCanvas" in fly_map
    assert "function taskPathLabel(kind)" in fly_map
    assert "function taskPathStatusText()" in fly_map
    assert 'return "编队中心预期"' in fly_map
    assert 'return "探索目标序列"' in fly_map
    assert 'return "规划器未来轨迹"' in fly_map
    assert "formation.target_center_xy_m" in fly_map
    assert 'context.strokeStyle = "#f05d9b"' in fly_map
    assert '{ label: "编队目标", color: "#f05d9b", visible: root.showFormationTarget && root.formationTarget() !== null }' in fly_map
    assert "property bool showMapVehicles: true" in qml
    assert "property bool showMapActualTracks: true" in qml
    assert "property bool showMapExpectedPath: true" in qml
    assert "property bool showMapFuturePath: true" in qml
    assert "property bool showMapTaskBoundary: true" in qml
    assert "property bool showMapFormationTarget: true" in qml
    assert 'text: "飞机位置与航向"' in qml
    assert 'text: "实际飞行轨迹"' in qml
    assert 'text: "规划器未来轨迹"' in qml
    assert "actualTrackSourceIdentity" in fly_map
    assert "actualTrackLastSequence" in fly_map
    assert 'text: "场景哈希："' not in qml
    assert 'QGCLabel { text: "任务Adapter确认"; font.bold: true }' in qml
    assert 'text: "Adapter：" + String(missionStatus().adapter_id || "-")' in qml
    assert 'root.missionAdapterVehicleText(modelData)' in qml
    assert "状态不完整：收到 " in qml
    assert 'text: "飞行阶段：" + flightPhaseText()' not in qml
    assert 'text: "任务Adapter阶段：" + missionStatusText()' in qml
    assert '"run_starting": "正在启动飞行运行时"' in qml
    assert "operationStageText(mosimOrchestrator.operationStage)" in qml
    assert "interval: 40" in qml
    assert "QGC原生解锁/起飞" in qml
    assert 'text: "下一步：" + nextOperatorStepText()' not in qml
    assert "function operatorChecklist()" in qml
    assert 'text: "操作进度"' not in qml
    assert "QGC原生飞行操作栏执行解锁和起飞" in qml
    assert "activeVehicle.initialConnectComplete" in qml
    assert "activeVehicle.flying" in qml
    assert "activeVehicle.landing" in qml
    assert 'if (state === "失败")' in qml
    assert 'label: "5. 降落、锁定与结束"' in qml
    assert "selectionMatchesPreparedRun()" in qml
    assert "controllerBox" not in qml and "vehicleBox" not in qml
    assert "控制器（已绑定）" in qml and "无人机（已绑定）" in qml
    assert "另一个任务仍在运行" in qml
    assert "experimentProfileId" in bridge_header
    assert "selectedControllerId" in bridge_header
    assert "selectedVehicleCount" in bridge_header
    assert "受控任务助手把自然语言转换为已登记的任务Profile" not in qml
    assert "function agentProposalReady()" in qml
    assert "function confirmAgentProposal()" in qml
    assert 'text: "生成受控任务建议"' in qml
    assert 'text: "采用建议并验证配置"' in qml
    assert "mosimOrchestrator.proposeOperatorTask(agentPrompt.text)" in qml
    assert "proposal.may_start_flight === false" in qml
    assert "Codex诊断能力尚未接入" not in qml
    assert "FUEL单机自主探索" in qml
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
    assert "build/flight-console-qgc-candidate/Release/MoSimFlightConsole.exe" in script
    assert "$candidateItem.LastWriteTimeUtc -gt $formalItem.LastWriteTimeUtc" in script
    assert "Using newer Flight Console candidate build" in script
    assert "Flight Console executable:" in script
    assert "[switch]$ResolveOnly" in script
    assert "if ($ResolveOnly)" in script


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
