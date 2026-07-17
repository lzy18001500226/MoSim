import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
ENSURE = ROOT / "Scripts/sunray/ensure_p9_learning_px4ctrl_backend.sh"
CHECKER = ROOT / "Scripts/sunray/check_learning_generated_runtime_provenance.py"
REGISTRY = ROOT / "Config/control_platform/control_module_registry.json"
CATALOG = ROOT / "Config/profiles/catalog.json"


def test_cmake_declares_learning_generated_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "learning_attitude_thrust"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST" in text
    assert "generated_c/MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock" in text


def test_adapter_maps_both_frozen_routes_and_fails_closed() -> None:
    controller = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    for profile in ("trained_neural_residual", "rl_gain_scheduler"):
        assert f'"{profile}"' in controller
        assert profile in BASIC_GATE.read_text(encoding="utf-8")
    for token in (
        "learning_enable_in = 1.0",
        "mass_kg_in = param_.mass",
        "hover_percentage_in = effective_hover_percentage",
        "normalized_thrust_out",
        "fallback_active_out == 0.0",
        "Learning ATTITUDE_THRUST generated backend returned invalid output",
        "learning_artifact_sha256=4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45",
        "u.thrust = 0.0",
    ):
        assert token in controller
    assert "learning_attitude_thrust" in ENSURE.read_text(encoding="utf-8")
    assert "ARTIFACT_SHA256" in CHECKER.read_text(encoding="utf-8")


def test_trained_routes_are_separate_from_legacy_zero_neural_pid() -> None:
    registry = REGISTRY.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    for route in ("trained_neural_residual", "rl_gain_scheduler"):
        assert f'"module_id": "{route}"' in registry
        assert f'"{route}_attitude_thrust_v1"' in catalog
    assert "zero_untrained_bounded_residual" in registry
    assert "P9_LEARNING_RUNTIME_CLOSEOUT.json" in registry
    assert "strict_performance_acceptance_blocked" in registry
    profiles = json.loads(catalog)["controller_profiles"]
    for route in ("trained_neural_residual", "rl_gain_scheduler"):
        profile = profiles[f"{route}_attitude_thrust_v1"]
        assert profile["selectable"] is False
        assert "strict_performance_acceptance_blocked" in profile["claim_ceiling"]
