from __future__ import annotations

import json
from pathlib import Path

from Scripts.ui.check_qgc_windows_toolchain import QT_KIT, QT_MODULES, QT_VERSION, inspect
from Scripts.ui.generate_qgc_vendor_manifest import MOSIM_MAIN_WINDOW_PATCH, render
from Scripts.ui.materialize_qgc_custom_overlay import materialize


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


def test_custom_overlay_uses_read_only_operator_bridge_and_native_qgc_layers() -> None:
    cmake = (CUSTOM / "CMakeLists.txt").read_text(encoding="utf-8")
    resources = (CUSTOM / "custom.qrc").read_text(encoding="utf-8")
    plugin = (CUSTOM / "src" / "CustomPlugin.cc").read_text(encoding="utf-8")
    bridge_header = (CUSTOM / "src" / "MoSimOperatorBridge.h").read_text(encoding="utf-8")
    bridge_source = (CUSTOM / "src" / "MoSimOperatorBridge.cc").read_text(encoding="utf-8")
    fly_view = (CUSTOM / "src" / "FlyView.qml").read_text(encoding="utf-8")
    fly_layer = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")

    assert "QGC_CUSTOM_BUILD" in cmake
    assert "CUSTOMCLASS=CustomPlugin" in cmake
    assert "MoSimOperatorBridge.cc" in cmake
    assert "MoSimOrchestratorBridge.cc" not in cmake
    assert "QGroundControl/FlightDisplay/FlyView.qml" in resources
    assert "QGroundControl/FlightDisplay/FlyViewCustomLayer.qml" in resources
    assert "QGroundControl/FlightDisplay/FactoryFlyMap.qml" in resources
    assert "QGroundControl/Controls/PlanView.qml" in resources

    assert 'setContextProperty(QStringLiteral("mosimOperator")' in plugin
    assert "mosimOrchestrator" not in plugin
    assert "QMetaObject::invokeMethod(rootObject, \"showPlanView\")" not in plugin

    assert "operatorProfiles" in bridge_header
    assert "controllerFamilies" in bridge_header
    assert "controllerSchemes" in bridge_header
    assert "operatorMaps" in bridge_header
    assert "operatorMap" in bridge_header
    assert "runManifest" in bridge_header
    assert "runtimeTelemetry" in bridge_header
    assert "faultAcks" in bridge_header
    assert "pendingFault" in bridge_header
    assert "profileSelectionLocked" in bridge_header
    assert "selectedControllerSchemeId" in bridge_header
    assert "selectedMapId" in bridge_header
    assert "selectControllerScheme" in bridge_header
    assert "selectOperatorMap" in bridge_header
    assert "copySelectedLaunchCommand" in bridge_header
    assert "copyClearActiveRunCommand" in bridge_header
    assert "copyStagedFaultCommand" in bridge_header
    assert "copyRestoreNormalCommand" in bridge_header
    assert "copyRosbagReplayCommand" in bridge_header
    assert "QProcess" not in bridge_source
    assert "orchestrator_client" not in bridge_source
    assert "operator_profiles.json" in bridge_source
    assert "control_scheme_catalog.json" in bridge_source
    assert "controller_scheme_id" in bridge_source
    assert "runtime_backend_catalog.json" in bridge_source
    assert "operator_invocation" in bridge_source
    assert "prepare_operator_run.py" in bridge_source
    assert "qgc_active_run.json" in bridge_source
    assert "MOSIM_OPERATOR_PROFILE_ID" in bridge_source
    assert "MOSIM_CONTROLLER_PROFILE" in bridge_source
    assert "MOSIM_VEHICLE_COUNT" in bridge_source
    assert "profile_locked_by_run_manifest" in bridge_source
    assert "run_manifest_already_active" in bridge_source
    assert "operator_map_catalog.json" in bridge_source
    assert "RUN_MANIFEST.json" in bridge_source
    assert "telemetry.json" in bridge_source
    assert "injection_acks" in bridge_source
    assert "loadFaultAcks" in bridge_source
    assert "profile_disabled" in bridge_source
    assert "QClipboard" in bridge_source

    # Factory map is below native QGC controls. It replaces online tiles but
    # cannot obscure the normal widget layer used for arm, takeoff and land.
    assert "FlyViewCustomLayer {" in fly_view
    assert "z:                  _fullItemZorder + 1" in fly_view
    assert "FlyViewWidgetLayer {" in fly_view
    assert "z:                      _fullItemZorder + 2" in fly_view
    assert "parentToolInsets:   widgetLayer.totalToolInsets" in fly_view
    assert "WindowContainer" not in fly_view
    assert "UE" not in fly_view

    assert "FactoryFlyMap {" in fly_layer
    assert 'import "qrc:/Custom/qml/QGroundControl/FlightDisplay" as MoSimFlightDisplay' in fly_layer
    assert "MoSimFlightDisplay.FactoryFlyMap {" in fly_layer
    assert "mapConfig: mosimOperator.operatorMap || ({})" in fly_layer
    assert "runManifest: mosimOperator.runManifest || ({})" in fly_layer
    assert "mapState: root.runtimeTelemetry.map_state || ({})" in fly_layer
    assert "runId: mosimOperator.runId" in fly_layer
    assert "copySelectedLaunchCommand" in fly_layer
    assert "copyClearActiveRunCommand" in fly_layer
    assert "copyStagedFaultCommand" in fly_layer
    assert "copyRestoreNormalCommand" in fly_layer
    assert "faultStateText" in fly_layer
    assert "faultAckText" in fly_layer
    assert "生效状态" in fly_layer
    assert "copyRosbagReplayCommand" in fly_layer
    assert "function mapTransportStatusText()" in fly_layer
    assert "ROS1 实时数据" in fly_layer
    assert "rosbag 回放中" in fly_layer
    assert "rosbag 回放已完成" in fly_layer
    assert "function mapTransportDetailText()" in fly_layer
    assert "controllerFamilyBox" in fly_layer
    assert "controllerBox" in fly_layer
    assert "controllerOptionsForFamily" in fly_layer
    assert "profilesForController" in fly_layer
    assert "model: root.compatibleProfiles" in fly_layer
    assert "mosimOperator.selectControllerScheme" in fly_layer
    assert "（未发布）" in fly_layer
    assert "profileSelectionLocked" in fly_layer
    assert "operatorMapBox" in fly_layer
    assert "root.operatorMaps" in fly_layer
    assert "mosimOperator.selectOperatorMap" in fly_layer
    assert "mosimOrchestrator" not in fly_layer
    assert "WindowContainer" not in fly_layer


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
    assert '$CustomResource = Join-Path $VendorRoot "custom/custom.qrc"' in script
    assert "-E touch $CustomResource" in script
    assert "Ninja Multi-Config" in script
    assert "[switch]$Incremental" in script
    assert 'if ($Incremental) { "" } else { "--fresh " }' in script
    tick = chr(96)
    assert script.index(f'set {tick}"PATH=') < script.index(f'call {tick}"$VsDevCmd')


def test_factory_floorplan_is_packaged_for_the_flight_console() -> None:
    resource = (CUSTOM / "custom.qrc").read_text(encoding="utf-8")
    fly_qml = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    fly_map = (CUSTOM / "src" / "FactoryFlyMap.qml").read_text(encoding="utf-8")

    assert 'prefix="/Custom/maps/factory_l2/v1"' in resource
    assert "maps/factory_l2/v1/floorplan.png" in resource
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
    assert "actualTrackSourceIdentity" in fly_map
    assert "rosbag_replay" in fly_map
    assert "formationTarget" in fly_map and "explorationBoundary" in fly_map

    catalog = json.loads(
        (ROOT / "Config" / "control_platform" / "operator_map_catalog.json").read_text(encoding="utf-8")
    )
    assert catalog["default_map_id"] == "factory_l2"
    factory = catalog["maps"][0]
    assert factory["map_id"] == "factory_l2"
    assert factory["map_version"] == "v1"
    assert factory["asset_sha256"]
    assert factory["coordinate_contract_id"] == "factory_l2_mworks_world_v1"
    assert factory["coordinate_contract_status"] == "pending_runtime_validation"
    assert factory["resource_url"] == "qrc:/Custom/maps/factory_l2/v1/floorplan.png"
    assert factory["world_bounds_m"]["max_x_m"] - factory["world_bounds_m"]["min_x_m"] > 1100
    assert factory["mission_publication"]["status"] == "blocked_until_runtime_round_trip_gate"
    bridge_source = (CUSTOM / "src" / "MoSimOperatorBridge.cc").read_text(encoding="utf-8")
    assert 'mapCatalog.value(QStringLiteral("default_map_id"))' in bridge_source
    assert "requestedDefaultMapId" in bridge_source
    assert "_defaultMapId" in bridge_source


def test_plan_view_uses_georeferenced_factory_overlay_without_orchestrator() -> None:
    plan_view = (CUSTOM / "src" / "PlanView.qml").read_text(encoding="utf-8")
    overlay = (CUSTOM / "src" / "FactoryPlanMapOverlay.qml").read_text(encoding="utf-8")

    assert "FactoryPlanMapOverlay {" in plan_view
    assert 'import "qrc:/Custom/qml/QGroundControl/Controls" as MoSimControls' in plan_view
    assert "MoSimControls.FactoryPlanMapOverlay {" in plan_view
    assert "map: editorMap" in plan_view
    assert "mapConfig: mosimOperator.operatorMap || ({})" in plan_view
    assert "runManifest: mosimOperator.runManifest || ({})" in plan_view
    assert "target: mosimOperator" in plan_view
    assert "function onStateChanged()" in plan_view
    assert "mosimOrchestrator" not in plan_view
    assert "editorMap.center = factoryPlanMap.mapCenter" in plan_view
    assert "factoryMissionPublicationAllowed" in plan_view

    assert "map.fromCoordinate(northWest, false)" in overlay
    assert "map.fromCoordinate(southEast, false)" in overlay
    assert "function coordinateForWorld(worldX, worldY)" in overlay
    assert "mapCenter.atDistanceAndAzimuth" in overlay
    assert "explorationBoundaryValid" in overlay
    assert "scenarioBoundaryValid ? scenarioBoundary : configuredBoundary" in overlay


def test_operator_console_exposes_profiles_fault_staging_and_visible_commands() -> None:
    qml = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    header = (CUSTOM / "src" / "MoSimOperatorBridge.h").read_text(encoding="utf-8")

    assert "operatorProfiles" in header
    assert "controllerFamilies" in header
    assert "controllerSchemes" in header
    assert "selectedProfile" in header
    assert "selectedControllerSchemeId" in header
    assert "pendingFault" in header
    assert "readonly property var profiles: mosimOperator.operatorProfiles || []" in qml
    assert "readonly property var controllerFamilies: mosimOperator.controllerFamilies || []" in qml
    assert "readonly property var controllerSchemes: mosimOperator.controllerSchemes || []" in qml
    assert "model: root.compatibleProfiles" in qml
    assert "controller_profile" in qml and "vehicle_count" in qml
    assert "控制：" in qml
    assert "controllerFamilyBox" in qml and "controllerBox" in qml
    assert "controllerOptionsForFamily" in qml
    assert "profilesForController" in qml
    assert "model: root.compatibleProfiles" in qml
    assert "mosimOperator.selectControllerScheme" in qml
    assert "stageWind" in qml and "stageMotorEffectiveness" in qml
    assert "copyStagedFaultCommand" in qml
    assert "copyRestoreNormalCommand" in qml
    assert "copySelectedLaunchCommand" in qml
    assert "copyClearActiveRunCommand" in qml
    assert "copyRosbagReplayCommand" in qml
    assert "TextArea" in qml and "mosimOperator.lastCommand" in qml
    assert "agentSuggest" in qml
    assert "mosimOrchestrator" not in qml


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
    assert "[int]$StartupTimeoutSeconds = 15" in script
    assert "MainWindowHandle" in script
    assert "exited during startup" in script
    assert "did not create a main window" in script


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
