from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORMAL_RUNNER = ROOT / "Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
MISSION_NODE = ROOT / "Scripts/sunray/px4ctrl_basic_mission_node.py"


def test_formal_fastlio_hover_runner_freezes_source_local_state_contract() -> None:
    source = FORMAL_RUNNER.read_text(encoding="utf-8")

    assert "SUNRAY_GPS_SENSOR_MODE=removed" in source
    assert "PX4CTRL_HOVER_PERCENTAGE=0.456" in source
    assert "PX4CTRL_SUNRAY150_IMU_CALIBRATION_ENABLED=false" in source
    assert "--pre-takeoff-max-abs-roll-pitch-deg 2.0" in source
    assert "PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true" in source
    assert "PX4CTRL_START_EXTERNAL_FUSION=true" in source
    assert "PX4CTRL_ODOM_SOURCE=mavros_local" in source
    assert "FASTLIO_ALIGNMENT_Z_SOURCE=truth" in source
    assert "run_px4ctrl_basic_gate.sh" in source


def test_hybrid_z_adapter_never_becomes_a_direct_px4ctrl_truth_input() -> None:
    source = BASIC_GATE.read_text(encoding="utf-8")

    assert "truth|truth_delta)" in source
    assert "px4ctrl still consumes MAVROS/PX4 local odometry." in source
    assert '"gazebo_truth_direct_px4ctrl_input_allowed": false' in source


def test_goal1_alignment_uses_the_same_steady_hover_window_as_hover_metrics() -> None:
    source = MISSION_NODE.read_text(encoding="utf-8")
    goal1_start = source.index("    def goal1_gate(")
    goal2_start = source.index("    def goal2_gate(", goal1_start)
    goal1 = source[goal1_start:goal2_start]

    assert 'gate_truth_rows = [r for r in self.sunray_truth_rows if r.get("phase") == "hover_before"]' in goal1
    assert 'gate_local_rows = [r for r in self.local_rows if r.get("phase") == "hover_before"]' in goal1
    assert "full_delta_error_preview_diagnostic_only" in goal1
