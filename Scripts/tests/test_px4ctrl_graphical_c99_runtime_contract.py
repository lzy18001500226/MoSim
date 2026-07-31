from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "src" / "control" / "runtime_adapters" / "px4ctrl"
CODEGEN = ROOT / "src" / "control" / "codegen" / "px4ctrl"
PREPARE = ROOT / "Scripts" / "sunray" / "prepare_local_ros1_workspace.sh"
GATE = ROOT / "Scripts" / "sunray" / "run_px4ctrl_basic_gate.sh"
FASTLIO_GATE = ROOT / "Scripts" / "sunray" / "run_px4ctrl_fastlio_hover_gate.sh"


def test_graphical_c99_backend_has_a_project_local_build_path() -> None:
    cmake = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")

    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "graphical_px4ctrl_c99"' in cmake
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_GRAPHICAL_PX4CTRL_C99" in cmake
    assert "px4ctrl_graphical_generated_shared.c" in cmake
    assert "MOSIM_PX4CTRL_CONTROL_SOURCE_DIR" in cmake
    assert "Results/" not in cmake


def test_graphical_wrapper_uses_private_init_step_symbols() -> None:
    wrapper = (CODEGEN / "px4ctrl_graphical_generated_shared.c").read_text(
        encoding="utf-8"
    )

    assert "#define Init MosimPx4ctrlGraphicalGeneratedInit" in wrapper
    assert "#define Step MosimPx4ctrlGraphicalGeneratedStep" in wrapper
    assert "MosimPx4ctrlGeneratedGraphStepScalar" in wrapper


def test_ros_adapter_uses_physical_acceleration_for_runtime_thrust_mapping() -> None:
    controller = (PX4CTRL / "src" / "controller.cpp").read_text(encoding="utf-8")
    start = controller.index("LinearControl::calculateGraphicalC99Control")
    end = controller.index("LinearControl::usingGeneratedCore", start)
    graphical = controller[start:end]

    assert "MosimPx4ctrlGeneratedGraphStepScalar" in graphical
    assert "computeDesiredCollectiveThrustSignal(generated_des_acc)" in graphical
    assert "u.thrust = generated_normalized_thrust" not in graphical
    assert "bodyrateAttitudeFeedback" in graphical


def test_source_local_entry_requires_a_matching_graphical_build() -> None:
    prepare = PREPARE.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    fastlio = FASTLIO_GATE.read_text(encoding="utf-8")

    assert "--px4ctrl-backend" in prepare
    assert "graphical_px4ctrl_c99" in prepare
    assert "graphical_c99" in gate
    assert "capture_px4ctrl_build_backend" in gate
    assert "PX4CTRL_EXPECTED_BUILD_BACKEND" in gate
    assert "PX4CTRL_BUILD_BACKEND=graphical_px4ctrl_c99" not in gate
    assert "PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99" in fastlio
