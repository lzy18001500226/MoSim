import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COORDINATE_CONTRACT = ROOT / "Scripts" / "sunray" / "write_c99_diff_target_coordinate_contract.py"
MULTIUAV_RUNNER = ROOT / "Scripts" / "sunray" / "run_c99_multiuav_planner_gate.sh"
SINGLE_RUNNER = ROOT / "Scripts" / "sunray" / "run_diff_single_auto123_gate.sh"
SINGLE_GATE = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_single_gate.sh"
DIFF_LAUNCH = ROOT / "Scripts" / "sunray" / "diff_planner_single_px4ctrl_goal4.launch"
FORMATION_GATE = ROOT / "Scripts" / "sunray" / "run_factory_l2_swarm_formation_obstacle_gate.ps1"
GRID_MAP = ROOT / "src" / "planning" / "fixed_formation" / "src" / "planner" / "plan_env" / "src" / "grid_map.cpp"


def test_diff_swarm_world_targets_are_split_between_mission_and_planner_frames(tmp_path: Path) -> None:
    output = tmp_path / "coordinate_contract.json"
    result = subprocess.run(
        [
            sys.executable,
            str(COORDINATE_CONTRACT),
            "--source-frame",
            "world",
            "--mavros-frame",
            "local",
            "--output",
            str(output),
            "--starts",
            "0",
            "-1",
            "0",
            "-1",
            "-1.5",
            "0",
            "--targets",
            "1",
            "-1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "0",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    contract = json.loads(output.read_text(encoding="utf-8"))

    assert result.stdout.strip() == "1 0 1 1 2 1 2.5 0 1"
    assert contract["source_frame"] == "world"
    assert contract["mavros_frame"] == "local"
    assert contract["mission_frame"] == "mavros_local"
    assert contract["planner_frame"] == "common_world"
    assert contract["source_targets"]["2"] == [1.0, 1.0, 1.0]
    assert contract["mission_targets"] == {
        "1": [1.0, 0.0, 1.0],
        "2": [1.0, 2.0, 1.0],
        "3": [2.5, 0.0, 1.0],
    }
    assert contract["planner_targets"] == {
        "1": [1.0, -1.0, 1.0],
        "2": [1.0, 1.0, 1.0],
        "3": [1.0, 0.0, 1.0],
    }
    assert contract["runtime_bridge"]["planner_position_cmd"] == "common_world_to_mavros_local"


def test_diff_swarm_common_world_mavros_keeps_fixed_targets_identical(tmp_path: Path) -> None:
    output = tmp_path / "coordinate_contract.json"
    result = subprocess.run(
        [
            sys.executable,
            str(COORDINATE_CONTRACT),
            "--source-frame",
            "world",
            "--mavros-frame",
            "common_world",
            "--output",
            str(output),
            "--starts",
            "0",
            "120",
            "0",
            "124",
            "0",
            "116",
            "--targets",
            "-4",
            "118",
            "1",
            "-4",
            "122",
            "1",
            "-4",
            "114",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    contract = json.loads(output.read_text(encoding="utf-8"))

    assert result.stdout.strip() == "-4 118 1 -4 122 1 -4 114 1"
    assert contract["mavros_frame"] == "common_world"
    assert contract["mission_frame"] == "common_world"
    assert contract["mission_targets"] == contract["planner_targets"]
    assert contract["mission_targets"]["1"] == [-4.0, 118.0, 1.0]
    assert contract["runtime_bridge"] == {
        "planner_odom": "identity_common_world",
        "planner_goal": "identity_common_world",
        "planner_position_cmd": "identity_common_world",
    }


def test_c99_planner_entrypoints_disable_qgc_and_ue_without_sensor_parameter_tuning() -> None:
    single = SINGLE_RUNNER.read_text(encoding="utf-8")
    multi = MULTIUAV_RUNNER.read_text(encoding="utf-8")
    coordinate_contract = COORDINATE_CONTRACT.read_text(encoding="utf-8")

    assert "PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false" in single
    assert "DIFF_AUTO_GOAL_IN_INTERACTIVE_REVIEW=true" in single
    assert "write_c99_diff_target_coordinate_contract.py" in multi
    assert 'C99_DIFF_MAVROS_ODOM_FRAME="${C99_DIFF_MAVROS_ODOM_FRAME:-common_world}"' in multi
    assert "C99_DIFF_EXPECTED_COMMON_WORLD_BRIDGE=false" in multi
    assert "QGC=disabled" in multi
    assert "export UE_LIVE_MIRROR_ENABLE=false" in multi
    assert "FAST-LIO, MID360, point-cloud and grid-map parameters are unchanged." in coordinate_contract


def test_diff_single_entry_connects_planner_commands_to_px4ctrl() -> None:
    wrapper = SINGLE_RUNNER.read_text(encoding="utf-8")
    gate = SINGLE_GATE.read_text(encoding="utf-8")
    launch = DIFF_LAUNCH.read_text(encoding="utf-8")

    assert "PLANNER_VARIANT=diff_planner" in wrapper
    assert 'bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh' in wrapper
    assert 'PLANNER_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/diff_planner_single_px4ctrl_goal4.launch"' in gate
    assert 'PLANNER_RAW_POSITION_CMD_TOPIC="${DIFF_RAW_POSITION_CMD_TOPIC}"' in gate
    assert 'PLANNER_ENABLE_CMD_SAFETY_ADAPTER="${DIFF_ENABLE_CMD_SAFETY_ADAPTER}"' in gate
    assert 'goal4_position_cmd_safety_adapter.py' in gate
    assert '_input_topic:="${PLANNER_RAW_POSITION_CMD_TOPIC}"' in gate
    assert '_output_topic:=/position_cmd' in gate
    assert '<remap from="position_cmd" to="$(arg position_cmd_topic)"/>' in launch
    assert '<arg name="odom_topic" default="/uav1/mavros/local_position/odom"/>' in launch


def test_formation_gate_uses_the_c99_wrapper_and_only_adds_an_optional_map_origin() -> None:
    gate = FORMATION_GATE.read_text(encoding="utf-8")
    grid_map = GRID_MAP.read_text(encoding="utf-8")

    assert "PX4CTRL_CORE_PROFILE=graphical_c99" in gate
    assert "PRELOAD_GAZEBO_MODELS=true" in gate
    assert "STAGGERED_SPAWN=false" in gate
    assert "bash Scripts/sunray/run_c99_multiuav_planner_gate.sh" in gate
    assert "SWARM_FORMATION_D3_GRID_RESOLUTION=0.20" in gate
    assert 'node_.param("grid_map/use_map_origin_override", use_map_origin_override, false);' in grid_map
    assert "mp_.map_origin_ = Eigen::Vector3d(-x_size / 2.0, -y_size / 2.0, mp_.ground_height_);" in grid_map
