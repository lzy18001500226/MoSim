from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/collect_classic_controller_mworks_evidence.py"


def test_collector_uses_only_live_mworks_result_api() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "ModelingPy.CheckModel",
        "ModelingPy.SimulateModel",
        "ModelingPy.GetVarTimes",
        "ModelingPy.GetVarsValues(builder.OUTPUTS)",
        '"source": "MWORKS_MCP_LIVE"',
    ):
        assert token in text
    assert "offline" not in text.lower()


def test_collector_enforces_stateful_family_behavior() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "observer_position_x_evolves",
        "adaptive_position_delta_x_evolves",
        "fractional_integral_x_evolves",
        "fractional_derivative_x_evolves",
        "status_code_zero",
        "finite_thrust",
        "lengths != {4}",
    ):
        assert token in text
