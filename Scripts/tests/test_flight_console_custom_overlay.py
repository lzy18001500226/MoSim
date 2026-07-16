from __future__ import annotations

import argparse
from pathlib import Path

from Scripts.ui import orchestrator_client
from Scripts.ui.check_qgc_windows_toolchain import QT_KIT, QT_MODULES, QT_VERSION, inspect
from Scripts.ui.materialize_qgc_custom_overlay import materialize
from Scripts.ui.generate_qgc_vendor_manifest import render


ROOT = Path(__file__).resolve().parents[2]
CUSTOM = ROOT / "apps" / "flight_console" / "mosim" / "custom"


def test_custom_overlay_uses_supported_qgc_extension_points() -> None:
    cmake = (CUSTOM / "CMakeLists.txt").read_text(encoding="utf-8")
    resources = (CUSTOM / "custom.qrc").read_text(encoding="utf-8")
    plugin = (CUSTOM / "src" / "CustomPlugin.cc").read_text(encoding="utf-8")
    qml = (CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    assert "QGC_CUSTOM_BUILD" in cmake
    assert "CUSTOMCLASS=CustomPlugin" in cmake
    assert "QGroundControl/FlightDisplay/FlyViewCustomLayer.qml" in resources
    assert 'setContextProperty(QStringLiteral("mosimOrchestrator")' in plugin
    assert "4 (scale gate pending)" in qml and "9 (scale gate pending)" in qml
    assert "RViz point cloud" in qml and "Unreal" in qml
    assert "Apply wind" in qml and "Apply motor" in qml
    assert "cascade_pid_figure8_generated_c_v1.json" in qml
    assert "Cascade PID / MWORKS generated C" in qml
    assert "mosimOrchestrator.attachDisplays()" in qml
    assert "mosimOrchestrator.detachDisplays()" in qml
    assert "injectionVehicle.currentIndex = 0" in qml


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
