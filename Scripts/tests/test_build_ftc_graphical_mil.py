from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_ftc_graphical_mil.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_ftc_graphical_mil", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load P7 graphical builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ftc_fixture_contains_full_detection_and_reconfiguration_chain() -> None:
    source = load_builder().build_model()
    for layer in (
        "nominal_control_allocation",
        "motor_response_residual",
        "residual_to_effectiveness",
        "effectiveness_update",
        "bounded_effectiveness_estimate",
        "persistent_effectiveness_state",
        "fault_isolation_gain",
        "fault_aware_reallocation",
        "reconfigured_motor_command",
        "degraded_action_selection",
    ):
        assert layer in source
    assert source.count("connect(") == 21
    assert "StopTime=0.25" in source


def test_ftc_fixture_has_report_outputs() -> None:
    source = load_builder().build_model()
    for output in ("motor_command_1", "eta_hat_1", "isolated_score", "action"):
        assert f"Outport {output}" in source


def test_generated_manifest_starts_pending_live_check() -> None:
    module = load_builder()
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert '"status": "generated_pending_live_check"' in source
    assert '"live_check": None' in source
