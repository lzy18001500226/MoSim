from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
CHECKER = ROOT / "Scripts/sunray/check_mpc_generated_runtime_provenance.py"
PROFILES = (
    "linear_mpc", "robust_mpc", "adaptive_mpc", "tube_mpc",
    "explicit_gain_scheduled_mpc", "ilqr", "mppi",
)


def test_cmake_declares_mpc_generated_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'get_filename_component(MOSIM_PX4CTRL_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" REALPATH)' in text
    assert '"${MOSIM_PX4CTRL_SOURCE_DIR}/../../../../../../.." ABSOLUTE' in text
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "mpc_attitude_thrust"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST" in text
    assert "generated_c_lifecycle_fixed/MoSim_P4_Mpc_CFunction_Sysblock" in text


def test_adapter_maps_all_profiles_and_fails_closed() -> None:
    controller = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    runner = BASIC_GATE.read_text(encoding="utf-8")
    checker = CHECKER.read_text(encoding="utf-8")
    for profile in PROFILES:
        assert f'"{profile}"' in controller
        assert profile in runner
        assert profile in checker
    for token in (
        "mass_kg_in = param_.mass",
        "gravity_mps2_in = param_.gra",
        "hover_percentage_in = effective_hover_percentage",
        "max_tilt_rad_in",
        "min_collective_thrust_n_in = 0.0",
        "max_collective_thrust_n_in = full_collective_thrust_n",
        "status_code_out == 0.0",
        "MPC ATTITUDE_THRUST generated backend returned invalid output",
        "u.thrust = 0.0",
    ):
        assert token in controller
