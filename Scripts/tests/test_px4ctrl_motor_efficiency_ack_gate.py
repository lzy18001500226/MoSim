from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "Scripts/sunray/run_px4ctrl_motor_efficiency_ack_gate.sh"


def test_motor_efficiency_ack_gate_keeps_px4ctrl_in_control() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "build_p7_ftc_actuator_plugin.sh" in source
    assert "MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN=true" in source
    assert "apply_motor_efficiency_fault.py" in source
    assert "PX4CTRL_START_EXTERNAL_FUSION=false" in source
    assert "PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false" in source
    assert "controller_authority=px4ctrl_only" in source
    assert "controller_override_observed" in source
    assert "reset_to_nominal_commanded" in source
    assert '"$(<"${RUNTIME_LOCK_DIR}/run_id")" == "${RUN_ID}"' in source


def test_motor_efficiency_ack_gate_separates_ack_from_mission_quality() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "fault_ack_status" in source
    assert "basic_mission_status" in source
    assert "Mission-quality acceptance remains governed separately" in source
