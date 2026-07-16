from __future__ import annotations

import importlib.util
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/sunray/build_factory_l2_formation_obstacle_scenario.py"
LAUNCH = ROOT / "Scripts/sunray/swarm_formation_swarm_px4ctrl_d3.launch"
RUNNER = ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
OPTIMIZER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/traj_opt/src/poly_traj_optimizer.cpp"
)
OPTIMIZER_HEADER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/traj_opt/include/optimizer/poly_traj_optimizer.h"
)
REPLAN_FSM = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/plan_manage/src/ego_replan_fsm.cpp"
)
PLANNER_MANAGER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/plan_manage/src/planner_manager.cpp"
)
POLY_TRAJ_OPTIMIZER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/traj_opt/src/poly_traj_optimizer.cpp"
)
POLY_TRAJ_OPTIMIZER_HEADER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/traj_opt/include/optimizer/poly_traj_optimizer.h"
)
DYN_A_STAR = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/path_searching/src/dyn_a_star.cpp"
)
SWARM_MISSION = ROOT / "Scripts/sunray/px4ctrl_ego_swarm_mission_node.py"
COLLISION_REPLAN_PATCH = ROOT / "Scripts/sunray/patch_swarm_formation_collision_replan.py"
SWARM_RUNNER = ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
FACTORY_GATE = ROOT / "Scripts/sunray/run_factory_l2_swarm_formation_obstacle_gate.ps1"
FACTORY_REVIEW = ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_review.ps1"


def load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("formation_scenario", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_formation_positions_preserve_two_meter_minimum_spacing() -> None:
    module = load_module()
    positions = module.formation_positions((3.0, -4.0), 1.0)
    distances = [
        math.dist(positions[first], positions[second])
        for first, second in (("1", "2"), ("1", "3"), ("2", "3"))
    ]
    assert min(distances) == 2.0


def test_scenario_selection_audits_each_member_corridor() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"member_hits": member_hits' in source
    assert "any(len(path_hits) > 1" in source
    assert 'item["maximum_hit_planar_span_m"]' in source


def test_runtime_uses_real_three_uav_formation_model() -> None:
    launch = LAUNCH.read_text(encoding="utf-8")
    optimizer = OPTIMIZER.read_text(encoding="utf-8")
    optimizer_header = OPTIMIZER_HEADER.read_text(encoding="utf-8")
    replan_fsm = REPLAN_FSM.read_text(encoding="utf-8")

    assert '<arg name="formation_type" default="2"/>' in launch
    assert launch.count('name="optimization/formation_type"') == 3
    assert "THREE_UAV_TRIANGLE    = 2" in optimizer_header
    assert "formation_ready" in optimizer
    assert "if (formation_ready)" in optimizer
    assert "(pos - start_pos).norm() < obs_clearance_" in optimizer
    assert "planFromLocalTraj(true, false)" not in replan_fsm
    assert replan_fsm.count("planFromLocalTraj(true, true)") >= 2
    assert '<arg name="swarm_clearance" default="1.0"/>' in launch
    assert launch.count('name="optimization/swarm_clearance"') == 3
    assert '<arg name="planar_formation" default="true"/>' in launch
    assert launch.count('name="optimization/planar_formation"') == 3
    assert 'nh.param("optimization/planar_formation", planar_formation_, false);' in optimizer
    assert "swarm_graph_pos[id].z() = 0.0;" in optimizer
    assert "swarm_graph_vel[id].z() = 0.0;" in optimizer
    assert "heightGradCostP(pos, gradp, costp)" in optimizer
    assert "costs(3) += omg * step * costp;" in optimizer
    assert 'nh.param("optimization/min_traj_z"' in optimizer
    assert 'nh.param("optimization/max_traj_z"' in optimizer


def test_swarm_runtime_supports_explicit_leader_follower_commands() -> None:
    runner = RUNNER.read_text(encoding="utf-8")

    assert (
        'SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS="${SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS:-false}"'
        in runner
    )
    assert 'bridge_input_topic="/uav1/planner_position_cmd_swarm_raw"' in runner
    assert '_output_offset_x:="${bridge_offset_x}"' in runner
    assert '_output_offset_y:="${bridge_offset_y}"' in runner
    assert '"leader_follower_commands": ${SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS}' in runner


def test_factory_gate_limits_execution_without_degrading_planner_search() -> None:
    gate = FACTORY_GATE.read_text(encoding="utf-8")

    assert '"SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS=true"' in gate
    assert '"SWARM_FORMATION_D3_MIN_TRAJ_Z=0.90"' in gate
    assert '"SWARM_FORMATION_D3_MAX_TRAJ_Z=1.60"' in gate
    assert '"SWARM_FORMATION_D3_WEIGHT_HEIGHT=50000.0"' in gate
    assert '"EGO_MAX_VEL=0.8"' in gate
    assert '"EGO_MAX_ACC=0.8"' in gate
    assert '"EGO_CMD_SAFETY_MOTION_TIME_BASIS=ros_sim_time"' in gate
    assert '"EGO_CMD_SAFETY_SMOOTHING_MAX_SPEED_MPS=0.6"' in gate
    assert '"EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION=true"' in gate
    assert '"EGO_CMD_SAFETY_MAX_VELOCITY_MPS=0.6"' in gate
    assert '"EGO_CMD_SAFETY_MAX_ACCELERATION_MPS2=0.4"' in gate
    assert '"EGO_GATE_MIN_INTER_UAV_DISTANCE=1.0"' in gate
    assert '[int]$TotalTimeoutS = 600' in gate
    assert '"TOTAL_TIMEOUT_S=$TotalTimeoutS"' in gate


def test_factory_review_requires_accepted_runtime_evidence() -> None:
    review = FACTORY_REVIEW.read_text(encoding="utf-8")

    assert 'factory_l2_swarm_formation_obstacle_runtime_r34_20260716' in review
    assert '"EGO_SWARM_METRICS.json"' in review
    assert '"SWARM_FORMATION_TRACKING_GATE.json"' in review
    assert '$gatePacket.status -ne "passed"' in review
    assert '@($gatePacket.blockers).Count -ne 0' in review
    assert 'source /opt/ros/noetic/setup.bash && rostopic list' in review
    assert 'source /opt/ros/noetic/setup.bash' in review
    assert 'rviz -d' in review
    assert '[int]$ReviewTotalTimeoutS = 1200' in review
    assert '"-TotalTimeoutS", $ReviewTotalTimeoutS' in review


def test_optimized_trajectory_rejects_map_boundary_escape() -> None:
    optimizer = OPTIMIZER.read_text(encoding="utf-8")
    collision_body = optimizer.split("bool PolyTrajOptimizer::checkCollision", 1)[1].split(
        "/* callbacks by the L-BFGS optimizer */", 1
    )[0]

    assert "if (!grid_map_->isInMap(pos))" in collision_body
    assert 'ROS_WARN("optimized trajectory left map:' in collision_body
    assert collision_body.index("if (!grid_map_->isInMap(pos))") < collision_body.index(
        "(pos - start_pos).norm() < obs_clearance_"
    )


def test_astar_pool_is_map_derived_and_rejects_invalid_endpoints() -> None:
    astar = DYN_A_STAR.read_text(encoding="utf-8")
    optimizer = POLY_TRAJ_OPTIMIZER.read_text(encoding="utf-8")

    assert "start_pt.allFinite()" in astar
    assert "end_pt.allFinite()" in astar
    assert "grid_map_->isInMap(start_pt)" in astar
    assert "grid_map_->isInMap(end_pt)" in astar
    assert "grid_map_->getRegion(map_origin, map_size);" in optimizer
    assert "grid_map_->getResolution();" in optimizer
    assert "Eigen::Vector3i(800, 200, 40)" not in optimizer
    assert "Eigen::Vector3i::Constant(4)" in optimizer


def test_swarm_runner_aligns_planner_clearance_with_physical_gate() -> None:
    runner = SWARM_RUNNER.read_text(encoding="utf-8")
    assert 'SWARM_FORMATION_D3_SWARM_CLEARANCE="${SWARM_FORMATION_D3_SWARM_CLEARANCE:-1.0}"' in runner
    assert 'swarm_clearance:="${SWARM_FORMATION_D3_SWARM_CLEARANCE}"' in runner
    swarm_branch = runner.split('elif [[ "${PLANNER_VARIANT}" == "swarm_formation" ]]', 1)[1].split(
        "else", 1
    )[0]
    assert 'min_traj_z:="${SWARM_FORMATION_D3_MIN_TRAJ_Z}"' in swarm_branch
    assert 'max_traj_z:="${SWARM_FORMATION_D3_MAX_TRAJ_Z}"' in swarm_branch
    assert 'weight_height:="${SWARM_FORMATION_D3_WEIGHT_HEIGHT}"' in swarm_branch
    assert '"swarm_clearance_m": ${SWARM_FORMATION_D3_SWARM_CLEARANCE}' in runner


def test_astar_uses_wall_time_and_clears_stale_path_per_attempt() -> None:
    source = DYN_A_STAR.read_text(encoding="utf-8")
    search_body = source.split("bool AStar::AstarSearch", 1)[1].split(
        "vector<Vector3d> AStar::getPath", 1
    )[0]

    assert "const ros::WallTime time_1 = ros::WallTime::now();" in search_body
    assert search_body.count("ros::WallTime::now()") >= 4
    assert "ros::Time::now()" not in search_body
    assert search_body.index("gridPath_.clear();") < search_body.index("++rounds_;")
    assert "if ((time_2 - time_1).toSec() > 0.2)" in search_body


def test_astar_path_simplification_is_bounded_and_uses_search_collision_policy() -> None:
    source = DYN_A_STAR.read_text(encoding="utf-8")
    simplify_body = source.split("vector<Vector3d> AStar::astarSearchAndGetSimplePath", 1)[1]

    assert "bool use_esdf_path = true;" in simplify_body
    assert "use_esdf_path = false;" in simplify_body
    assert "use_esdf_path ? checkOccupancy_esdf(check_safe_pt)" in simplify_body
    assert ": checkOccupancy(check_safe_pt);" in simplify_body
    assert "const ros::WallTime simplify_start = ros::WallTime::now();" in simplify_body
    assert "if (i == end_idx)" in simplify_body
    assert "if (!finish && !advanced)" in simplify_body
    assert "simplification exceeded 0.2 seconds wall time" in simplify_body


def test_astar_rejects_corner_cutting_with_the_active_collision_policy() -> None:
    source = DYN_A_STAR.read_text(encoding="utf-8")
    search_body = source.split("bool AStar::AstarSearch", 1)[1].split(
        "vector<Vector3d> AStar::getPath", 1
    )[0]

    assert "const int edge_samples = std::max(" in search_body
    assert "(0.5 * step_size_)" in search_body
    assert "use_esdf_check ? checkOccupancy_esdf(edge_pt)" in search_body
    assert ": checkOccupancy(edge_pt);" in search_body
    assert "if (edge_blocked)" in search_body


def test_swarm_runner_rebuilds_when_any_audited_planner_source_changes() -> None:
    runner = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "local rebuild_required=0" in runner
    assert 'runtime_sources+=("${runtime_source}")' in runner
    assert "rebuild_required=1" in runner
    assert 'for runtime_source in "${runtime_sources[@]}"; do' in runner
    assert '"${runtime_source}" -nt "${executable}"' in runner


def test_collision_replan_patch_is_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "ego_replan_fsm.cpp"
    source.write_text(
        "success = planFromLocalTraj(true, false);\n"
        "if (planFromLocalTraj(true, false)) {}\n",
        encoding="utf-8",
    )

    first = subprocess.run(
        [sys.executable, str(COLLISION_REPLAN_PATCH), str(source)],
        check=True,
        capture_output=True,
        text=True,
    )
    second = subprocess.run(
        [sys.executable, str(COLLISION_REPLAN_PATCH), str(source)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert '"status": "patched"' in first.stdout
    assert '"status": "already_patched"' in second.stdout
    assert source.read_text(encoding="utf-8").count("planFromLocalTraj(true, true)") == 2


def test_swarm_runner_patches_and_rebuilds_the_runtime_workspace() -> None:
    runner = SWARM_RUNNER.read_text(encoding="utf-8")
    assert "prepare_swarm_formation_workspace" in runner
    assert "patch_swarm_formation_collision_replan.py" in runner
    assert "--target ego_planner_node" in runner
    assert runner.index("\nprepare_swarm_formation_workspace\n") < runner.index(
        "\n  start_gazebo_world\n"
    )


def test_swarm_formation_runtime_holds_a_continuous_fixed_yaw() -> None:
    runner = SWARM_RUNNER.read_text(encoding="utf-8")
    assert 'EGO_CMD_SAFETY_FIXED_YAW="${EGO_CMD_SAFETY_FIXED_YAW:-$(if [[ "${PLANNER_VARIANT}" == "swarm_formation" ]]; then echo 0.0; else echo \'\'; fi)}"' in runner
    assert '_fixed_yaw:="${EGO_CMD_SAFETY_FIXED_YAW}"' in runner
    assert '"fixed_yaw_rad": $(if [[ -n "${EGO_CMD_SAFETY_FIXED_YAW}" ]]' in runner


def test_swarm_formation_invalid_z_clamps_without_freezing_xy() -> None:
    runner = SWARM_RUNNER.read_text(encoding="utf-8")
    assert (
        '"${PLANNER_VARIANT}" == "racer" || "${PLANNER_VARIANT}" == "swarm_formation"'
        ' ]]; then echo clamp'
    ) in runner


def test_target_chain_executes_live_inter_uav_emergency_guard() -> None:
    mission = SWARM_MISSION.read_text(encoding="utf-8")
    target_chain = mission[mission.index("def run_target_chains"):mission.index("def run(self)")]
    assert "emergency_event = self.inter_uav_emergency_snapshot()" in target_chain
    assert 'blockers = ["inter_uav_emergency_hold"]' in target_chain
    assert 'round_item["emergency_event"] = emergency_event' in target_chain


def test_two_point_astar_path_is_rejected_before_optimization() -> None:
    astar = DYN_A_STAR.read_text(encoding="utf-8")
    optimizer = POLY_TRAJ_OPTIMIZER.read_text(encoding="utf-8")
    manager = PLANNER_MANAGER.read_text(encoding="utf-8")
    assert "if (!search_success || path.empty())" in astar
    assert "if (simple_path.size() <= 2)" in optimizer
    assert "return false;" in optimizer[optimizer.index("if (simple_path.size() <= 2)"):]
    assert "if (!ploy_traj_opt_->astarWithMinTraj" in manager
    assert "return false;" in manager[manager.index("if (!ploy_traj_opt_->astarWithMinTraj"):]


def test_swarm_runner_syncs_all_audited_planner_sources() -> None:
    runner = SWARM_RUNNER.read_text(encoding="utf-8")
    for path in (
        "planner/plan_manage/src/planner_manager.cpp",
        "planner/path_searching/src/dyn_a_star.cpp",
        "planner/traj_opt/src/poly_traj_optimizer.cpp",
        "planner/traj_opt/include/optimizer/poly_traj_optimizer.h",
    ):
        assert path in runner
    assert 'cmp -s "${audited_source}" "${runtime_source}"' in runner
    assert 'cp "${audited_source}" "${runtime_source}"' in runner
