from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_capture_summary_requires_passive_gps_state_contract() -> None:
    collector = load_module("gps_state_chain_collector", "Scripts/sunray/collect_sunray_gps_state_chain.py")
    capture = {
        "counts": {
            "global_position": 8,
            "home_position": 1,
            "local_pose": 20,
            "local_odom": 20,
            "gazebo_pose": 20,
            "mavros_state": 8,
        },
        "global_samples": [
            {"latitude": 47.397742, "longitude": 8.545594, "altitude": 488.0, "status": 0}
            for _ in range(8)
        ],
        "home_samples": [{"latitude": 47.397742, "longitude": 8.545594, "altitude": 488.0}],
        "state_samples": [{"connected": True, "armed": False, "mode": "POSCTL"} for _ in range(8)],
        "local_truth_distances_m": [0.02] * 20,
        "home_global_distances_m": [0.01] * 8,
        "ekf2_gps_ctrl": {"success": True, "integer": 7, "real": 0.0},
    }

    result = collector.summarize_capture(
        capture,
        7,
        5,
        10,
        0.5,
        25.0,
        requested_duration_s=90.0,
        observed_duration_s=90.001,
        termination_reason="duration_elapsed",
        post_connect_settle_ready=True,
    )

    assert result["status"] == "passed"
    assert result["blockers"] == []
    assert result["capture_duration"]["complete"] is True


def test_capture_summary_rejects_armed_or_wrong_gps_parameter() -> None:
    collector = load_module("gps_state_chain_collector_fail", "Scripts/sunray/collect_sunray_gps_state_chain.py")
    capture = {
        "counts": {topic: 10 for topic in collector.REQUIRED_TOPICS},
        "global_samples": [
            {"latitude": 47.397742, "longitude": 8.545594, "altitude": 488.0, "status": 0}
            for _ in range(10)
        ],
        "home_samples": [{"latitude": 47.397742, "longitude": 8.545594, "altitude": 488.0}],
        "state_samples": [{"connected": True, "armed": True}],
        "local_truth_distances_m": [0.02] * 10,
        "home_global_distances_m": [0.01],
        "ekf2_gps_ctrl": {"success": True, "integer": 0, "real": 0.0},
    }

    result = collector.summarize_capture(
        capture,
        7,
        5,
        10,
        0.5,
        25.0,
        requested_duration_s=90.0,
        observed_duration_s=45.8,
        termination_reason="ros_shutdown",
        post_connect_settle_ready=True,
    )

    assert result["status"] == "blocked"
    assert "no_flight_contract_violated_armed" in result["blockers"]
    assert "ekf2_gps_ctrl_value_mismatch" in result["blockers"]
    assert "capture_duration_incomplete" in result["blockers"]
    assert result["capture_duration"]["complete"] is False


def test_ulog_summary_accepts_global_home_and_failsafe_contract() -> None:
    analyzer = load_module("gps_state_chain_ulog", "Scripts/sunray/analyze_px4_gps_state_chain_ulog.py")
    datasets = {
        ("vehicle_global_position", 0): {
            "timestamp": [1000, 2000],
            "lat": [473977420, 473977420],
            "lon": [85455940, 85455940],
            "alt": [488.0, 488.0],
            "lat_lon_valid": [1, 1],
            "alt_valid": [1, 1],
        },
        ("home_position", 0): {
            "timestamp": [1000],
            "lat": [473977420],
            "lon": [85455940],
            "alt": [488.0],
            "valid_hpos": [1],
            "valid_alt": [1],
        },
        ("vehicle_status", 0): {"timestamp": [1000], "pre_flight_checks_pass": [1]},
        ("failsafe_flags", 0): {
            "timestamp": [1000],
            "global_position_invalid": [0],
            "home_position_invalid": [0],
        },
    }

    result = analyzer.summarize_datasets(datasets)

    assert result["status"] == "passed"
    assert result["global_home_last_delta"]["horizontal_m"] < 0.01


def test_ulog_summary_serializes_scalar_objects_with_item() -> None:
    analyzer = load_module("gps_state_chain_ulog_scalar", "Scripts/sunray/analyze_px4_gps_state_chain_ulog.py")

    class Int8Like:
        def item(self):
            return 7

    assert json.loads(json.dumps({"value": Int8Like()}, default=analyzer.json_default)) == {"value": 7}


def test_boot_gate_freezes_nested_gps_without_flight() -> None:
    source = (ROOT / "Scripts/sunray/run_sunray_gps_state_chain_gate.sh").read_text(encoding="utf-8")
    basic_gate = (ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")

    assert "SUNRAY_GPS_SENSOR_MODE=nested" in source
    assert "PX4CTRL_BOOT_PARAM_OVERRIDES=\"EKF2_GPS_CTRL=7,EKF2_HGT_REF=1,EKF2_EV_CTRL=0\"" in source
    assert "PX4CTRL_START_CONTROLLER=false" in source
    assert "PX4CTRL_START_EXTERNAL_FUSION=false" in source
    assert "PX4CTRL_SKIP_MISSION=true" in source
    assert "rosbag record --lz4" in source
    assert "set +u\n  source /opt/ros/noetic/setup.bash" in source
    assert "PX4_ULOG_SEARCH_ROOT" in source
    assert "MOSIM_RUNTIME_ROS_HOME" in source
    assert "capture_mavros_effective_state" in source
    assert "mavros_effective_state.txt" in source
    assert "capture_mavros_runtime_config_resolution" in basic_gate
    assert "mavros_runtime_config_resolution.json" in basic_gate
    assert "rospack find sunray_simulator" in basic_gate
    assert "apply_project_mavros_plugin_profile_before_node" in basic_gate
    assert "rosparam load \"${profile_path}\" /uav1/mavros" in basic_gate
    assert "mavros_plugin_profile_apply.txt" in basic_gate
    assert "capture_mavros_plugin_params_before_node" in basic_gate
    assert 'rospy.signal_shutdown("connected")' not in basic_gate
    assert "mavros_plugin_params_before_node.txt" in basic_gate
    assert 'MOSIM_RUNTIME_ROS_HOME="${MOSIM_RUNTIME_ROS_HOME:-${RESULT_DIR}/ros_home}"' in basic_gate
    assert 'export ROS_HOME="${MOSIM_RUNTIME_ROS_HOME}"' in basic_gate
