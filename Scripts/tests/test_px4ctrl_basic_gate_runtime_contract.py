from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
G9_RUNNER = ROOT / "Scripts/sunray/run_g9_controller_final_acceptance.sh"


def test_px4_work_directory_is_per_run_and_exported_before_roslaunch() -> None:
    source = G9_RUNNER.read_text(encoding="utf-8")

    default = 'MOSIM_PX4_WORK_DIR="${MOSIM_PX4_WORK_DIR:-${RESULT_DIR}/px4_work}"'
    create = 'mkdir -p "${RESULT_DIR}" "${MOSIM_PX4_WORK_DIR}"'
    export = "export MOSIM_PX4_WORK_DIR"
    gate = 'bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh"'

    assert default in source
    assert source.index(create) < source.index(export) < source.index(gate)


def test_g9_final_runner_freezes_backend_and_calibration_contract() -> None:
    source = G9_RUNNER.read_text(encoding="utf-8")

    assert "g9_single_uav_isolated_px4.launch" in source
    assert "check_g9_generated_runtime_provenance.py" in source
    assert "--require-runtime-ack" in source
    assert source.count("CAL_GYRO0_") == 3
    assert source.count("CAL_ACC0_") == 3
    assert "takeoff_hover_land|figure8" in source
