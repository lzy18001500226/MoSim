from __future__ import annotations

import argparse
from pathlib import Path

from Scripts.ui import orchestrator_client
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
        ramp_s=0.2,
        duration_s=3.0,
        display=[],
    )
    payload = orchestrator_client.build_payload(args)
    assert payload["run_id"] == "run-test"
    assert payload["command"]["target"] == "motor_effectiveness"
    assert payload["command"]["rotor_index"] == 2
    assert payload["command"]["source"] == "flight_console"
