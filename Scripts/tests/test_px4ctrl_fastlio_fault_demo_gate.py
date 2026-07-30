from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "Scripts/sunray/run_px4ctrl_fastlio_fault_demo_gate.sh"


def test_fastlio_fault_demo_reuses_the_frozen_source_local_baseline() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "Usage: $0 [--factory-l2-fault-demo]" in source
    assert "operation_selector=factory_l2_fault_demo" in source
    assert "run_px4ctrl_fastlio_hover_gate.sh" in source
    assert "resolve_local_ros1_runtime.sh" in source
    assert 'source "${LOCAL_ROS1_WS}/devel/setup.bash"' in source
    assert "MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN=true" in source
    assert "MOTOR_EFFICIENCY_EFFECTIVENESS:-0.85" in source
    assert "apply_motor_efficiency_fault.py" in source
    assert "controller_authority=px4ctrl_only" in source
    assert "controller_override_observed" in source
    assert "reset_to_nominal_commanded" in source
    assert "px4ctrl_basic_mission.log" in source
    assert "mission_node_not_started_before_fault_injection" in source


def test_fastlio_fault_demo_records_only_lightweight_replay_topics() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "rosbag record --lz4" in source
    assert "/uav1/mavros/local_position/odom" in source
    assert "/uav1/sunray/gazebo_pose" in source
    assert "/mosim/px4ctrl/reference_path" in source
    assert "/mosim/px4ctrl/truth_path" in source
    assert "/uav1/mosim/ftc_actuator_telemetry" in source
    assert "PointCloud2" not in source


def test_fastlio_fault_demo_separates_functional_evidence_from_quality_observation() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "functional_lifecycle" in source
    assert "physical_motor_fault" in source
    assert "quality_observation" in source
    assert "PX4CTRL_BASIC_MISSION_METRICS.json" in source
    assert "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json" in source
    assert "does not override the functional lifecycle" in source


def test_fastlio_fault_demo_uses_a_read_only_qgc_display_bridge() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "MOSIM_OPERATOR_RUN_ID" in source
    assert "prepare_factory_live_operator_map.py" in source
    assert "OPERATOR_MAP_COORDINATE_EVIDENCE.json" in source
    assert "runtime_sidecar.py" in source
    assert "--read-only" in source
    assert "QGC read-only telemetry sidecar exited during startup" in source
    assert "ps -o stat=" in source
    assert "terminal_fastlio_fault_demo_gate" in source


def test_fastlio_fault_demo_freezes_factory_map_and_ue_display_contract() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert 'FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF:-0.5}"' in source
    assert 'FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP:-0.5}"' in source
    assert 'REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE:-true}"' in source
    assert 'MOSIM_UE_STATE_STREAM="${MOSIM_UE_STATE_STREAM:-true}"' in source
    assert "stream_ros1_state_to_ue_udp.py" in source
    assert "ue_sender_metrics.json" in source
    assert "stop_ue_stream" in source
