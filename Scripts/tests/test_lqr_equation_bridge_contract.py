from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRAPHICAL = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "ClassicRobust" / "MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.mo"
BRIDGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Bridges" / "LqrBaselineEquationBridge.mo"
ADAPTER = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / "LqrBaselineAttitudeThrustAdapter.mo"
BINDING = ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "lqr_baseline.json"


def test_lqr_equation_bridge_preserves_the_selected_graphical_law_constants() -> None:
    graphical = GRAPHICAL.read_text(encoding="utf-8")
    bridge = BRIDGE.read_text(encoding="utf-8")

    for graphical_declaration, bridge_parameter in (
        ("position_gain_x(k=1.6)", "parameter Real position_gain_x = 1.6;"),
        ("position_gain_y(k=1.6)", "parameter Real position_gain_y = 1.6;"),
        ("position_gain_z(k=2.2)", "parameter Real position_gain_z = 2.2;"),
        ("velocity_gain_x(k=1.8)", "parameter Real velocity_gain_x = 1.8;"),
        ("velocity_gain_y(k=1.8)", "parameter Real velocity_gain_y = 1.8;"),
        ("velocity_gain_z(k=2.0)", "parameter Real velocity_gain_z = 2.0;"),
        ("gravity_compensation(k=9.80665)", "parameter Real gravity_mps2 = 9.80665;"),
        ("roll_from_lateral_acceleration(k=-0.10197162129779283)", "parameter Real roll_from_lateral_acceleration = -0.10197162129779283;"),
        ("pitch_from_lateral_acceleration(k=0.10197162129779283)", "parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;"),
        ("normalized_thrust_pre_limit(k=0.03772949988018335)", "parameter Real normalized_thrust_scale = 0.03772949988018335;"),
        ("collective_thrust_from_normalized(k=17.745945945945948)", "parameter Real collective_thrust_from_normalized = 17.745945945945948;"),
    ):
        assert graphical_declaration in graphical
        assert bridge_parameter in bridge

    assert "input Real dt" in bridge
    assert "enabled = enable >= 0.5;" in bridge
    assert "if enabled then collective_thrust_n else 0" in bridge


def test_lqr_formal_binding_freezes_graphical_and_equation_bridge_sources() -> None:
    adapter = ADAPTER.read_text(encoding="utf-8")
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    roles = {item["role"] for item in binding["source_bindings"]}

    assert "LqrBaselineEquationBridge core;" in adapter
    assert "graphical_controller_core" in roles
    assert "equation_bridge" in roles
    implementation = binding["formal_adapter"]["implementation"]
    assert implementation["kind"] == "equation_bridge"
    assert implementation["bridge_class"].endswith("LqrBaselineEquationBridge")
