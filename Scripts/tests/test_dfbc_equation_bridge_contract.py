from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRAPHICAL = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "GeometricFlatness" / "MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo"
BRIDGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Bridges" / "DfbcHighOrderEquationBridge.mo"
ADAPTER = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / "DfbcHighOrderAttitudeThrustAdapter.mo"
BINDING = ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "dfbc_high_order_attitude.json"


def test_dfbc_equation_bridge_preserves_selected_graphical_law_constants() -> None:
    graphical = GRAPHICAL.read_text(encoding="utf-8")
    bridge = BRIDGE.read_text(encoding="utf-8")

    for graphical_declaration, bridge_parameter in (
        ("position_feedback_x(k=1.7)", "parameter Real position_gain_x = 1.7;"),
        ("position_feedback_y(k=1.7)", "parameter Real position_gain_y = 1.7;"),
        ("position_feedback_z(k=2.1)", "parameter Real position_gain_z = 2.1;"),
        ("velocity_feedback_x(k=1.2)", "parameter Real velocity_gain_x = 1.2;"),
        ("velocity_feedback_y(k=1.2)", "parameter Real velocity_gain_y = 1.2;"),
        ("velocity_feedback_z(k=1.55)", "parameter Real velocity_gain_z = 1.55;"),
        ("surface_rate_x(k=100.0)", "parameter Real surface_rate_gain = 100.0;"),
        ("high_order_rate_feedback_x(k=0.045)", "parameter Real high_order_rate_gain_x = 0.045;"),
        ("high_order_rate_feedback_y(k=0.045)", "parameter Real high_order_rate_gain_y = 0.045;"),
        ("high_order_rate_feedback_z(k=0.06)", "parameter Real high_order_rate_gain_z = 0.06;"),
        ("gravity_compensation(k=9.80665)", "parameter Real gravity_mps2 = 9.80665;"),
        ("normalized_thrust_scaling(k=0.03772949988018335)", "parameter Real normalized_thrust_scale = 0.03772949988018335;"),
    ):
        assert graphical_declaration in graphical
        assert bridge_parameter in bridge

    assert "Modelica.Blocks.Discrete.UnitDelay previous_surface_x" in bridge
    assert "samplePeriod = sample_time_s" in bridge
    assert "enabled = enable >= 0.5;" in bridge
    assert "if enabled then normalized_thrust else 0" in bridge


def test_dfbc_formal_binding_freezes_graphical_and_equation_bridge_sources() -> None:
    adapter = ADAPTER.read_text(encoding="utf-8")
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    roles = {item["role"] for item in binding["source_bindings"]}

    assert "DfbcHighOrderEquationBridge core" in adapter
    assert "graphical_controller_core" in roles
    assert "equation_bridge" in roles
    implementation = binding["formal_adapter"]["implementation"]
    assert implementation["kind"] == "equation_bridge"
    assert implementation["bridge_class"].endswith("DfbcHighOrderEquationBridge")
