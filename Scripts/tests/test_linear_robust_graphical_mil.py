from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/build_linear_robust_graphical_mil.py"


def test_graphical_mil_exposes_all_four_controller_behaviors() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for algorithm in ("lqg", "feedback_linearization", "passivity_based_control", "adaptive_backstepping"):
        assert f'"{algorithm}"' in text
    for behavior in ("estimated_position_state", "storage_total", "sliding_surface", "adaptive_state"):
        assert behavior in text
    assert '"++-"' not in text
    assert "MWORKS_CFUNCTION_MIL" in text
    assert "all_behavior_equivalent" in text


def test_graphical_mil_keeps_full_contract_claim_separate() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "Full ATTITUDE_THRUST geometry" in text
    assert "Gazebo runtime are separate gates" in text
