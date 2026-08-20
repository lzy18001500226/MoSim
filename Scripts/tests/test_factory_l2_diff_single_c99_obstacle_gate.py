import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_BUILDER = ROOT / "Scripts" / "sunray" / "build_factory_l2_formation_obstacle_scenario.py"
RUNNER = ROOT / "Scripts" / "sunray" / "run_factory_l2_diff_single_c99_obstacle_gate.sh"


def test_obstacle_gate_uses_the_audited_center_route_as_sequential_goals() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT / "Results") as temp_dir:
        scenario_path = Path(temp_dir) / "scenario.json"
        subprocess.run(
            [
                sys.executable,
                str(SCENARIO_BUILDER),
                "--output",
                str(scenario_path),
            ],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    route = scenario["rigid_center_path_contract"]["center_waypoints_xy_m"]
    assert len(route) >= 3
    assert route[0] == scenario["formation"]["start_center_xy_m"]
    assert route[-1] == scenario["formation"]["target_center_xy_m"]

    source = RUNNER.read_text(encoding="utf-8")
    assert 'rigid_center_path_contract' in source
    assert 'route[1:]' in source
    assert 'GOALS="${GOALS}"' in source
    assert 'GOALS="${TARGET_X},${TARGET_Y},${TARGET_Z}"' not in source
    assert 'GOAL_COUNT="$(awk -F\';\'' in source
    assert 'DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT="${GOAL_COUNT}"' in source


def test_obstacle_gate_keeps_c99_profile_and_live_planner_boundary() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "PX4CTRL_CORE_PROFILE=graphical_c99" in source
    assert "PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99" in source
    assert "live planner still receives only MID360-derived world cloud" in source
    assert "Static collision truth selects the end points" in source
    assert 'RUNTIME_INFLATION_M="${RUNTIME_INFLATION_M:-0.20}"' in source
    assert 'RUNTIME_INFLATION_M="${route_values[6]}"' not in source
    assert 'DIFF_FASTLIO_EKF_FUSION="${DIFF_FASTLIO_EKF_FUSION:-false}"' in source
    assert 'DIFF_FASTLIO_ALIGNMENT_Z_SOURCE="${DIFF_FASTLIO_ALIGNMENT_Z_SOURCE:-truth}"' in source
    assert 'DIFF_FASTLIO_EKF_FUSION="${DIFF_FASTLIO_EKF_FUSION}"' in source
    assert '"px4ctrl_odom_source": "/uav1/mavros/local_position/odom"' in source
    assert '"gazebo_truth_direct_px4ctrl_input_allowed": False' in source
    assert 'TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-1200}"' in source


def test_interactive_route_uses_sim_time_holds_and_wall_time_stage_budget() -> None:
    mission = (ROOT / "Scripts" / "sunray" / "px4ctrl_ego_single_mission_node.py").read_text(
        encoding="utf-8"
    )
    probe = (ROOT / "Scripts" / "sunray" / "probe_diff_interactive_goal_switch_chain.py").read_text(
        encoding="utf-8"
    )
    runner = (ROOT / "Scripts" / "sunray" / "run_diff_single_auto123_gate.sh").read_text(
        encoding="utf-8"
    )

    assert 'metric["hold_time_basis"] = "ros_sim_time"' in mission
    assert 'final_metric["time_basis"] = "ros_sim_time"' in mission
    assert 'stable_since_sim = None' in probe
    assert '"time_basis": "ros_sim_time"' in probe
    assert 'DIFF_INTERACTIVE_GOAL_TIMEOUT_S="${DIFF_INTERACTIVE_GOAL_TIMEOUT_S:-120}"' in runner
    assert 'DIFF_INTERACTIVE_REVIEW_HOLD_S="${DIFF_INTERACTIVE_REVIEW_HOLD_S:-$((GOAL_COUNT * DIFF_INTERACTIVE_GOAL_TIMEOUT_S + 180))}"' in runner
    assert '--goal-timeout-s "${DIFF_INTERACTIVE_GOAL_TIMEOUT_S}"' in runner


def test_full_factory_world_gets_a_bounded_model_ready_budget() -> None:
    gate = (ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_single_gate.sh").read_text(
        encoding="utf-8"
    )

    assert 'if [[ "${SUNRAY_FACTORY_WORLD_RUNTIME_OVERLAY}" == "true" ]]; then' in gate
    assert "GAZEBO_MODEL_READY_TIMEOUT_S=360" in gate
    assert 'GAZEBO_MODEL_READY_TIMEOUT_S="${GAZEBO_MODEL_READY_TIMEOUT_S:-180}"' not in gate
