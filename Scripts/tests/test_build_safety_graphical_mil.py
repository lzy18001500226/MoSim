from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_safety_graphical_mil.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_safety_graphical_mil", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load P6 graphical builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_safety_family_fixture_contains_readable_layers_and_wiring() -> None:
    source = load_builder().build_model()
    for layer in (
        "candidate_command_limit",
        "cbf_barrier_correction",
        "geofence_projection",
        "reference_governor",
        "health_watchdog",
        "emergency_stop_request",
        "failsafe_action_arbiter",
    ):
        assert layer in source
    assert source.count("connect(") == 15
    assert "StopTime=0.2" in source


def test_safety_family_fixture_has_three_report_outputs() -> None:
    source = load_builder().build_model()
    for output in ("safe_acceleration_x", "safe_reference_x", "action"):
        assert f"Outport {output}" in source
