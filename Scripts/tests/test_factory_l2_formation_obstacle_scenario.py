from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/sunray/build_factory_l2_formation_obstacle_scenario.py"
SCENARIO = ROOT / "Config/scenarios/formation/factory_l2_three_uav_obstacle_crossing.json"
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
DYN_A_STAR_HEADER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/path_searching/include/path_searching/dyn_a_star.h"
)
SWARM_MISSION = ROOT / "Scripts/sunray/px4ctrl_ego_swarm_mission_node.py"
COLLISION_REPLAN_PATCH = ROOT / "Scripts/sunray/patch_swarm_formation_collision_replan.py"
MAP_ORIGIN_PATCH = ROOT / "Scripts/sunray/patch_swarm_formation_map_origin.py"
GRID_MAP = ROOT / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/plan_env/src/grid_map.cpp"
SWARM_RUNNER = ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
FACTORY_GATE = ROOT / "Scripts/sunray/run_factory_l2_swarm_formation_obstacle_gate.ps1"
FACTORY_REVIEW = ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_review.ps1"
OBSTACLE_CLEARANCE_ANALYZER = ROOT / "Scripts/sunray/analyze_swarm_formation_obstacle_clearance.py"


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


def test_rotated_layout_uses_one_shared_relative_position_contract() -> None:
    module = load_module()
    scale = module.DEFAULT_SCALE
    relative = module.formation_relative_positions(-4.0)
    positions = module.formation_positions((3.0, -4.0), scale, -4.0)

    assert positions["1"] == [3.0, -4.0]
    assert positions["2"] == [
        3.0 + scale * relative["2"][0],
        -4.0 + scale * relative["2"][1],
    ]
    distances = [
        math.dist(positions[first], positions[second])
        for first, second in (("1", "2"), ("1", "3"), ("2", "3"))
    ]
    assert math.isclose(min(distances), 1.40, abs_tol=1e-9)


def test_compact_layout_is_translated_from_the_last_stable_gazebo_uav2_spawn() -> None:
    module = load_module()
    center = module.center_for_uav2_start(
        module.R46_STABLE_UAV2_REQUESTED_START,
        module.DEFAULT_SCALE,
        module.DEFAULT_ROTATION_DEG,
    )
    positions = module.formation_positions(center, module.DEFAULT_SCALE, module.DEFAULT_ROTATION_DEG)

    assert positions["2"] == list(module.R46_STABLE_UAV2_REQUESTED_START)
    assert center != (-12.575025, -19.36313)


def test_scenario_selection_audits_each_member_corridor() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"member_hits": member_hits' in source
    assert "allow_multiple_member_hits" in source
    assert 'item["maximum_hit_planar_span_m"]' in source
    assert "selected_replay_compatible_leader_route" in source
    assert "relative_positions_unit" in source
    assert "r46_uav2_gazebo_spawn_anchor" in source
    assert "gazebo_spawn_anchor" in source
    assert "static_astar_member_audit" in source
    assert "rigid_center_fixed_path_audit" in source
    assert "explicit_catalog_fixed_path" in source
    assert "selected_static_astar_ready" in source
    assert "DEFAULT_PREFERRED_TARGET_CENTER" in source


def test_default_preferred_target_has_a_static_detour_for_all_members() -> None:
    module = load_module()
    import generate_factory_l2_clearance_route_waypoints as clearance

    boundary = clearance.load_boundary(clearance.DEFAULT_ENVELOPE)
    truth = clearance.read_json(clearance.DEFAULT_TRUTH)
    proxies = [
        proxy
        for raw in truth.get("collision_proxies", [])
        if isinstance(raw, dict) and (proxy := clearance.proxy_from_raw(raw)) is not None
    ]
    obstacle_args = type(
        "ObstacleArgs",
        (),
        {
            "flight_obstacle_min_z_m": 0.70,
            "flight_obstacle_max_z_m": 1.70,
            "obstacle_z_inflation_m": 0.0,
            "overhead_obstacle_max_min_z_m": 0.0,
        },
    )()
    obstacles = clearance.flight_obstacle_proxies(proxies, obstacle_args)
    start_center = module.center_for_uav2_start(
        module.R46_STABLE_UAV2_REQUESTED_START,
        module.DEFAULT_SCALE,
        module.DEFAULT_ROTATION_DEG,
    )
    audit = module.static_astar_member_audit(
        boundary=boundary,
        start_positions=module.formation_positions(
            start_center, module.DEFAULT_SCALE, module.DEFAULT_ROTATION_DEG
        ),
        target_positions=module.formation_positions(
            module.DEFAULT_PREFERRED_TARGET_CENTER,
            module.DEFAULT_SCALE,
            module.DEFAULT_ROTATION_DEG,
        ),
        obstacles=obstacles,
        clearance_margin_m=module.STATIC_ASTAR_CLEARANCE_MARGIN_M,
        grid_step_m=module.STATIC_ASTAR_GRID_STEP_M,
        search_padding_m=module.STATIC_ASTAR_SEARCH_PADDING_M,
    )

    assert audit["status"] == "passed"
    assert all(item["path_found"] for item in audit["per_uav"].values())
    assert all(item["detour_excess_m"] > 0.0 for item in audit["per_uav"].values())


def test_cataloged_leader_blocked_route_has_a_common_rigid_detour() -> None:
    module = load_module()
    import generate_factory_l2_clearance_route_waypoints as clearance

    catalog = module.STATIC_RIGID_ROUTE_CATALOG[0]
    boundary = clearance.load_boundary(clearance.DEFAULT_ENVELOPE)
    truth = clearance.read_json(clearance.DEFAULT_TRUTH)
    proxies = [
        proxy
        for raw in truth.get("collision_proxies", [])
        if isinstance(raw, dict) and (proxy := clearance.proxy_from_raw(raw)) is not None
    ]
    floors = [proxy for proxy in proxies if clearance.is_low_floor(proxy)]
    obstacle_args = type(
        "ObstacleArgs",
        (),
        {
            "flight_obstacle_min_z_m": 0.70,
            "flight_obstacle_max_z_m": 1.70,
            "obstacle_z_inflation_m": 0.0,
            "overhead_obstacle_max_min_z_m": 0.0,
        },
    )()
    obstacles = clearance.flight_obstacle_proxies(proxies, obstacle_args)
    start = tuple(catalog["start_center_xy_m"])
    target = tuple(catalog["target_center_xy_m"])

    audit = module.rigid_center_fixed_path_audit(
        center_waypoints=tuple(tuple(point) for point in catalog["center_waypoints_xy_m"]),
        start_center=start,
        target_center=target,
        scale=module.DEFAULT_SCALE,
        rotation_deg=module.DEFAULT_ROTATION_DEG,
        floors=floors,
        obstacles=obstacles,
        clearance_margin_m=module.STATIC_ASTAR_CLEARANCE_MARGIN_M,
        segment_sample_step_m=module.RIGID_CENTER_FIXED_PATH_SAMPLE_STEP_M,
    )

    assert audit["status"] == "passed"
    assert audit["route_selection"] == "explicit_catalog_fixed_path"
    assert audit["segment_sample_step_m"] == 0.05
    assert audit["detour_excess_m"] > 0.1
    assert all(item["status"] == "passed" for item in audit["waypoint_checks"])
    assert all(item["status"] == "passed" for item in audit["segment_checks"])

    candidate = module.route_candidate(
        start_center=start,
        target_center=target,
        start_positions=module.formation_positions(
            start, module.DEFAULT_SCALE, module.DEFAULT_ROTATION_DEG
        ),
        target_positions=module.formation_positions(
            target, module.DEFAULT_SCALE, module.DEFAULT_ROTATION_DEG
        ),
        obstacles=obstacles,
        margin=module.STATIC_ASTAR_CLEARANCE_MARGIN_M,
        start_shift_m=0.0,
        source=str(catalog["source"]),
        allow_multiple_member_hits=True,
    )
    assert candidate is not None
    assert candidate["obstacle_intersection_clearance_margin_m"] == 1.70
    assert "SM_Container01_100" in [item.actor for item in candidate["member_hits"]["1"]]


def test_runtime_uses_real_three_uav_formation_model() -> None:
    launch = LAUNCH.read_text(encoding="utf-8")
    optimizer = OPTIMIZER.read_text(encoding="utf-8")
    optimizer_header = OPTIMIZER_HEADER.read_text(encoding="utf-8")
    replan_fsm = REPLAN_FSM.read_text(encoding="utf-8")

    assert '<arg name="formation_type" default="2"/>' in launch
    assert launch.count('name="optimization/formation_type"') == 3
    assert '<arg name="relative_pos_1_x" default="1.7321"/>' in launch
    assert launch.count('name="global_goal/relative_pos_0/x"') == 3
    assert launch.count('name="global_goal/relative_pos_1/x"') == 3
    assert launch.count('name="global_goal/relative_pos_2/x"') == 3
    assert "THREE_UAV_TRIANGLE    = 2" in optimizer_header
    assert "formation_ready" in optimizer
    assert "if (formation_ready)" in optimizer
    assert "(pos - start_pos).norm() < obs_clearance_" in optimizer
    assert "planFromLocalTraj(true, false)" not in replan_fsm
    # The normal formation path still compares peer trajectories. In the
    # explicit rigid leader-follower path, follower planner trajectories are
    # deliberately not executed, so the collision-triggered replan keeps map
    # avoidance but omits that stale peer-polynomial comparison.
    assert "planFromLocalTraj(true, !rigid_leader_follower_mode_)" in replan_fsm
    assert replan_fsm.count("planFromLocalTraj(true, true)") >= 1
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
    assert 'SAFETY_ADAPTER_UIDS=(1)' in runner
    assert 'bridge_input_topic="/uav1/position_cmd"' in runner
    assert 'bridge_output_topic="/uav${uid}/position_cmd"' in runner
    assert 'leader_safety_adapter_with_spawn_offset_follower_relay' in runner
    assert '_output_offset_x:="${bridge_offset_x}"' in runner
    assert '_output_offset_y:="${bridge_offset_y}"' in runner
    assert '"leader_follower_commands": ${SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS}' in runner
    assert 'SWARM_FORMATION_D3_RIGID_LEADER_FOLLOWER_MODE="${SWARM_FORMATION_D3_RIGID_LEADER_FOLLOWER_MODE:-false}"' in runner
    assert 'rigid_leader_follower_mode:="${SWARM_FORMATION_D3_RIGID_LEADER_FOLLOWER_MODE}"' in runner
    assert "requires SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS=true" in runner
    assert '"planner_command_producer_uav_ids"' in runner


def test_leader_follower_has_one_final_command_owner_after_planner_takeover() -> None:
    mission = SWARM_MISSION.read_text(encoding="utf-8")
    runner = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "leader-follower-commands" in mission
    assert "def planner_takeover_ready(self) -> bool:" in mission
    assert "def raw_position_cmd_required(self, uid: int) -> bool:" in mission
    assert "def planner_trajectory_required(self, uid: int) -> bool:" in mission
    assert "return not self.args.leader_follower_commands or uid == 1" in mission
    assert "leader_offset_relay_no_independent_planner_trajectory_required" in mission
    assert "self.planner_trajectory_required(uid)" in mission
    assert '"leader_adapter_takeover_missing"' in mission
    assert '"direct_hover_during_leader_adapter_takeover"' in mission
    assert '"raw_position_cmd_required": self.raw_position_cmd_required(uid)' in mission
    assert '"leader_offset_relay_no_independent_raw_command_required"' in mission
    assert "return self.first_planner_trajectory_time(self.uavs[1]) is not None" in mission
    assert "uavs = [self.uavs[1]]" in mission
    assert "if not self.args.leader_follower_commands:" in mission
    assert "self.leader_adapter_takeover_active = False" in mission
    assert "if self.leader_adapter_takeover_active:" in mission
    assert "self.leader_adapter_takeover_suppressed_hover_call_count += 1" in mission
    assert "self.direct_hover_publish_count_during_adapter_takeover = 0" in mission
    assert (
        '"direct_hover_publish_count_during_adapter_takeover": '
        "self.direct_hover_publish_count_during_adapter_takeover"
    ) in mission
    assert "MISSION_TOPOLOGY_ARGS+=(--leader-follower-commands)" in runner


def test_swarm_runtime_passes_one_layout_contract_to_planner_and_followers() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    gate = FACTORY_GATE.read_text(encoding="utf-8")

    assert 'SWARM_FORMATION_D3_RELATIVE_POS_1_X="${SWARM_FORMATION_D3_RELATIVE_POS_1_X:-1.7321}"' in runner
    assert 'relative_pos_1_x:="${SWARM_FORMATION_D3_RELATIVE_POS_1_X}"' in runner
    assert '"relative_positions_unit": {' in runner
    assert "$relative = $formation.relative_positions_unit" in gate
    assert '"SWARM_FORMATION_D3_RELATIVE_POS_1_X=$($relative.\'2\'[0])"' in gate


def test_swarm_replan_never_extrapolates_an_expired_local_trajectory() -> None:
    replan_fsm = REPLAN_FSM.read_text(encoding="utf-8")

    assert "isLocalTrajectorySampleTimeValid" in replan_fsm
    assert "start_pt_ = odom_pos_;" in replan_fsm
    assert "start_vel_ = odom_vel_;" in replan_fsm
    assert "desired_start_time = now;" in replan_fsm
    assert "Formation replan start is outside the local trajectory window" in replan_fsm
    assert "std::min(info->duration, std::max(0.0, t_cur))" in replan_fsm


def test_factory_gate_limits_execution_without_degrading_planner_search() -> None:
    gate = FACTORY_GATE.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")

    assert '[ValidateSet("leader_follower", "native_per_uav")]' in gate
    assert '[string]$CommandMode = "leader_follower"' in gate
    assert '$leaderFollowerCommands = $CommandMode -eq "leader_follower"' in gate
    assert '"SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS=$($leaderFollowerCommands.ToString().ToLowerInvariant())"' in gate
    assert '"SWARM_FORMATION_D3_RIGID_LEADER_FOLLOWER_MODE=$($rigidLeaderFollowerMode.ToString().ToLowerInvariant())"' in gate
    assert "$plannerCommandProducerUavIds = [System.Collections.ArrayList]::new()" in gate
    assert "[void]$plannerCommandProducerUavIds.Add(1)" in gate
    assert "planner_command_producer_uav_ids = $plannerCommandProducerUavIds" in gate
    assert 'command_mode = $CommandMode' in gate
    assert "$runtimePlannerObstacleInflationM = [math]::Round($plannerObstacleClearanceM + 0.20, 2)" in gate
    assert '"SWARM_FORMATION_D3_OBSTACLES_INFLATION=$runtimePlannerObstacleInflationM"' in gate
    assert "runtime_planner_obstacle_inflation_m = $runtimePlannerObstacleInflationM" in gate
    assert "$mapSizeX = 64.0" in gate
    assert "$mapSizeY = 64.0" in gate
    assert '"SWARM_FORMATION_D3_MAP_SIZE_X=$mapSizeX"' in gate
    assert '"SWARM_FORMATION_D3_MAP_SIZE_Y=$mapSizeY"' in gate
    assert '"SWARM_FORMATION_D3_MIN_TRAJ_Z=0.90"' in gate
    assert '"SWARM_FORMATION_D3_MAX_TRAJ_Z=1.35"' in gate
    assert '"SWARM_FORMATION_D3_VIRTUAL_CEIL_HEIGHT=1.45"' in gate
    assert '"SWARM_FORMATION_D3_WEIGHT_HEIGHT=50000.0"' in gate
    assert "EGO_MAX_VEL=$($dynamics['ego_max_vel_mps'])" in gate
    assert "EGO_MAX_ACC=$($dynamics['ego_max_acc_mps2'])" in gate
    assert '"EGO_CMD_SAFETY_MOTION_TIME_BASIS=ros_sim_time"' in gate
    assert "EGO_CMD_SAFETY_SMOOTHING_MAX_SPEED_MPS=$($dynamics['command_speed_mps'])" in gate
    assert '"EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION=true"' in gate
    assert "EGO_CMD_SAFETY_MAX_VELOCITY_MPS=$($dynamics['command_speed_mps'])" in gate
    assert '"EGO_CMD_SAFETY_MAX_Z=1.35"' in gate
    assert "EGO_CMD_SAFETY_MAX_ACCELERATION_MPS2=$($dynamics['command_acceleration_mps2'])" in gate
    assert '"EGO_GATE_MIN_INTER_UAV_DISTANCE=1.0"' in gate
    assert '"EGO_GATE_INTER_UAV_EMERGENCY_HOLD_ENABLE=true"' in gate
    assert '"EGO_GATE_INTER_UAV_EMERGENCY_MARGIN_M=0.10"' in gate
    assert 'inter_uav_emergency_prediction_margin_m = 0.10' in gate
    assert "$plannerObstacleClearanceM = [double]$rigidPath.clearance_margin_m" in gate
    assert "planner_obstacle_clearance_m = $plannerObstacleClearanceM" in gate
    assert '"EGO_GATE_TARGET_REACHED_RADIUS_M=$targetReachedRadiusM"' in gate
    assert '"EGO_GATE_TARGET_HOLD_S=$targetHoldS"' in gate
    assert "--planner-clearance-m $plannerObstacleClearanceM" in gate
    assert 'EGO_GATE_TARGET_HOLD_S="${EGO_GATE_TARGET_HOLD_S:-2.0}"' in runner
    assert '--target-hold-s "${EGO_GATE_TARGET_HOLD_S}"' in runner
    assert '--target-reached-radius "${EGO_GATE_TARGET_REACHED_RADIUS_M}"' in runner
    assert "formation_envelope_radius_m = 1.50" in gate
    assert "formation_envelope_obstacle_inflation_m = 1.70" in gate
    assert "analyze_swarm_formation_obstacle_clearance.py" in gate
    assert "$obstacleExit = $LASTEXITCODE" in gate
    # The r8 center-chain run consumed about 847 s before its sixth target;
    # retain the documented 2400 s outer lifecycle watchdog.
    assert '[int]$TotalTimeoutS = 2400' in gate
    assert '"EGO_GATE_EXECUTE_WALL_TIMEOUT_S=900"' in gate
    assert '"TOTAL_TIMEOUT_S=$TotalTimeoutS"' in gate


def test_factory_gate_fails_closed_when_rigid_scenario_generation_fails() -> None:
    gate = FACTORY_GATE.read_text(encoding="utf-8")

    assert 'if ($LASTEXITCODE -ne 0)' in gate
    assert "The previous scenario file will not be reused." in gate
    assert "$rigidPath = $scenario.rigid_center_path_contract" in gate
    assert '$rigidPath.status -ne "passed"' in gate


def test_factory_review_requires_accepted_runtime_evidence() -> None:
    review = FACTORY_REVIEW.read_text(encoding="utf-8")

    assert 'factory_l2_swarm_formation_maporigin_r54_runtime_20260722' in review
    assert '"EGO_SWARM_METRICS.json"' in review
    assert '"SWARM_FORMATION_TRACKING_GATE.json"' in review
    assert '"SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json"' in review
    assert '$gatePacket.status -ne "passed"' in review
    assert '@($gatePacket.blockers).Count -ne 0' in review
    assert 'source /opt/ros/noetic/setup.bash && rostopic list' in review
    assert 'source /opt/ros/noetic/setup.bash' in review
    assert 'rviz -d' in review
    assert '[int]$ReviewTotalTimeoutS = 1200' in review
    assert '"-TotalTimeoutS", $ReviewTotalTimeoutS' in review


def test_obstacle_clearance_analyzer_is_postflight_only() -> None:
    source = OBSTACLE_CLEARANCE_ANALYZER.read_text(encoding="utf-8")
    assert "SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json" in source
    assert "uav{uid}_truth.csv" in source
    assert "Static collision truth is used only as a post-flight clearance oracle" in source
    assert "MID360 world-cloud and grid-map publication" in source


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
    assert 'virtual_ceil_height:="${SWARM_FORMATION_D3_VIRTUAL_CEIL_HEIGHT}"' in swarm_branch
    assert 'weight_height:="${SWARM_FORMATION_D3_WEIGHT_HEIGHT}"' in swarm_branch
    assert 'astar_search_timeout_s:="${SWARM_FORMATION_D3_ASTAR_SEARCH_TIMEOUT_S}"' in swarm_branch
    assert 'astar_planar_search:="${SWARM_FORMATION_D3_ASTAR_PLANAR_SEARCH}"' in swarm_branch
    assert '"swarm_clearance_m": ${SWARM_FORMATION_D3_SWARM_CLEARANCE}' in runner
    assert '"obstacles_inflation_m": ${SWARM_FORMATION_D3_OBSTACLES_INFLATION}' in runner
    assert '"astar_search_timeout_s": ${SWARM_FORMATION_D3_ASTAR_SEARCH_TIMEOUT_S}' in runner
    assert '"astar_planar_search": ${SWARM_FORMATION_D3_ASTAR_PLANAR_SEARCH}' in runner
    assert '"virtual_ceil_height_m": ${SWARM_FORMATION_D3_VIRTUAL_CEIL_HEIGHT}' in runner
    assert '"map_size_m": [${SWARM_FORMATION_D3_MAP_SIZE_X}, ${SWARM_FORMATION_D3_MAP_SIZE_Y}, ${SWARM_FORMATION_D3_MAP_SIZE_Z}]' in runner


def test_factory_gate_expands_obstacles_for_the_rigid_formation_footprint() -> None:
    gate = FACTORY_GATE.read_text(encoding="utf-8")
    runner = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "$runtimePlannerObstacleInflationM = [math]::Round($plannerObstacleClearanceM + 0.20, 2)" in gate
    assert '"SWARM_FORMATION_D3_OBSTACLES_INFLATION=$runtimePlannerObstacleInflationM"' in gate
    assert '"SWARM_FORMATION_D3_ASTAR_SEARCH_TIMEOUT_S=1.00"' in gate
    assert '"SWARM_FORMATION_D3_ASTAR_PLANAR_SEARCH=true"' in gate
    assert '"SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS=$($leaderFollowerCommands.ToString().ToLowerInvariant())"' in gate
    assert 'bridge_input_topic="/uav1/planner_position_cmd_swarm_raw"' in runner
    assert '"leader_follower_commands": ${SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS}' in runner


def test_astar_uses_wall_time_and_clears_stale_path_per_attempt() -> None:
    source = DYN_A_STAR.read_text(encoding="utf-8")
    search_body = source.split("bool AStar::AstarSearch", 1)[1].split(
        "vector<Vector3d> AStar::getPath", 1
    )[0]

    assert "const ros::WallTime time_1 = ros::WallTime::now();" in search_body
    assert search_body.count("ros::WallTime::now()") >= 4
    assert "ros::Time::now()" not in search_body
    assert search_body.index("gridPath_.clear();") < search_body.index("++rounds_;")
    assert "if ((time_2 - time_1).toSec() > search_timeout_s_)" in search_body
    assert "setSearchTimeout" in source


def test_fixed_height_formation_can_limit_only_its_astar_initialization_to_xy() -> None:
    astar = DYN_A_STAR.read_text(encoding="utf-8")
    astar_header = DYN_A_STAR_HEADER.read_text(encoding="utf-8")
    optimizer = POLY_TRAJ_OPTIMIZER.read_text(encoding="utf-8")

    assert "bool planar_search_{false};" in astar_header
    assert "void setPlanarSearch(const bool planar_search);" in astar_header
    assert "end_idx(2) = start_idx(2);" in astar
    assert "for (int dz = planar_search_ ? 0 : -1; dz <= (planar_search_ ? 0 : 1); dz++)" in astar
    assert 'nh.param("optimization/astar_planar_search", astar_planar_search_, false);' in optimizer
    assert "a_star_->setPlanarSearch(astar_planar_search_);" in optimizer


def test_fixed_height_formation_keeps_continuous_obstacle_avoidance_lateral() -> None:
    optimizer = POLY_TRAJ_OPTIMIZER.read_text(encoding="utf-8")
    obstacle_body = optimizer.split("bool PolyTrajOptimizer::obstacleGradCostP", 1)[1].split(
        "bool PolyTrajOptimizer::heightGradCostP", 1
    )[0]
    height_body = optimizer.split("bool PolyTrajOptimizer::heightGradCostP", 1)[1].split(
        "bool PolyTrajOptimizer::swarmGradCostP", 1
    )[0]

    assert "if (astar_planar_search_)" in obstacle_body
    assert "dist_grad.z() = 0.0;" in obstacle_body
    assert "costp = wei_height_ * violation * violation;" in height_body
    assert "2.0 * wei_height_ * violation" in height_body


def test_astar_path_simplification_is_bounded_and_uses_search_collision_policy() -> None:
    source = DYN_A_STAR.read_text(encoding="utf-8")
    simplify_body = source.split("vector<Vector3d> AStar::astarSearchAndGetSimplePath", 1)[1]

    assert "bool use_esdf_path = true;" in simplify_body
    assert "use_esdf_path = false;" in simplify_body
    assert "use_esdf_path ? checkOccupancy_esdf(check_safe_pt)" in simplify_body
    assert ": checkOccupancy(check_safe_pt);" in simplify_body
    assert "const double collision_sample_spacing = collisionSampleSpacing(step_size_);" in simplify_body
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
    assert "collisionSampleSpacing(step_size_)" in source
    assert source.count("collisionSampleSpacing(step_size_)") >= 2
    assert "use_esdf_check ? checkOccupancy_esdf(edge_pt)" in search_body
    assert ": checkOccupancy(edge_pt);" in search_body
    assert "if (edge_blocked)" in search_body


def test_swarm_runner_rebuilds_when_any_audited_planner_source_changes() -> None:
    runner = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "local rebuild_required=0" in runner
    assert "planner/path_searching/include/path_searching/dyn_a_star.h" in runner
    assert 'runtime_sources+=("${runtime_source}")' in runner
    assert "rebuild_required=1" in runner
    assert runner.count('for runtime_source in "${runtime_sources[@]}"; do') >= 2
    assert 'if [[ ! -x "${executable}" ]]; then' in runner
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


def test_collision_replan_patch_accepts_rigid_leader_follower_guard(tmp_path: Path) -> None:
    source = tmp_path / "ego_replan_fsm.cpp"
    source.write_text(
        "success = planFromLocalTraj(true, true);\n"
        "if (planFromLocalTraj(true, !rigid_leader_follower_mode_)) {}\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(COLLISION_REPLAN_PATCH), str(source)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "already_patched"
    assert payload["formation_preserving_calls"] == 2
    assert payload["peer_trajectory_preserving_calls"] == 1
    assert payload["rigid_leader_follower_collision_replans"] == 1


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


def test_swarm_formation_target_timeout_uses_sim_time_with_explicit_wall_guard() -> None:
    mission = SWARM_MISSION.read_text(encoding="utf-8")
    runner = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "execute_start_sim = self.now()" in mission
    assert "execute_start_wall = time.monotonic()" in mission
    assert "self.now() - execute_start_sim" in mission
    assert "self.args.execute_wall_timeout_s" in mission
    assert '"time_basis": "ros_simulation_time_with_wall_hard_limit"' in mission
    assert 'parser.add_argument("--execute-wall-timeout-s"' in mission
    assert 'EGO_GATE_EXECUTE_WALL_TIMEOUT_S="${EGO_GATE_EXECUTE_WALL_TIMEOUT_S:-300.0}"' in runner
    assert '--execute-wall-timeout-s "${EGO_GATE_EXECUTE_WALL_TIMEOUT_S}"' in runner

    target_chain = mission[mission.index("def run_target_chains"):mission.index("def run(self)")]
    assert "round_start_sim = self.now()" in target_chain
    assert "round_start_wall = time.monotonic()" in target_chain
    assert "self.args.target_chain_goal_wall_timeout_s" in target_chain
    assert '"goal_republish_time_basis": "ros_simulation_time"' in target_chain
    assert 'parser.add_argument("--target-chain-goal-wall-timeout-s"' in mission
    assert 'TARGET_CHAIN_GOAL_WALL_TIMEOUT_S="${TARGET_CHAIN_GOAL_WALL_TIMEOUT_S:-300.0}"' in runner
    assert '--target-chain-goal-wall-timeout-s "${TARGET_CHAIN_GOAL_WALL_TIMEOUT_S}"' in runner


def test_swarm_formation_can_explicitly_warn_without_blocking_raw_planner_jumps() -> None:
    mission = SWARM_MISSION.read_text(encoding="utf-8")
    runner = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "--warn-on-raw-position-cmd-discontinuity" in mission
    assert 'else echo "--warn-on-raw-position-cmd-discontinuity"' in runner


def test_target_chain_executes_live_inter_uav_emergency_guard() -> None:
    mission = SWARM_MISSION.read_text(encoding="utf-8")
    target_chain = mission[mission.index("def run_target_chains"):mission.index("def run(self)")]
    assert "emergency_event = self.inter_uav_emergency_snapshot()" in target_chain
    assert 'blockers = ["inter_uav_emergency_hold"]' in target_chain
    assert 'round_item["emergency_event"] = emergency_event' in target_chain


def test_swarm_emergency_guard_freezes_a_low_speed_noise_floor() -> None:
    mission = SWARM_MISSION.read_text(encoding="utf-8")
    runner = SWARM_RUNNER.read_text(encoding="utf-8")
    launcher = (ROOT / "Scripts/sunray/run_factory_l2_swarm_formation_obstacle_gate.ps1").read_text(
        encoding="utf-8"
    )

    assert 'parser.add_argument("--inter-uav-emergency-min-closing-speed-mps", type=float, default=0.05)' in mission
    assert "EGO_GATE_INTER_UAV_EMERGENCY_MIN_CLOSING_SPEED_MPS" in runner
    assert '--inter-uav-emergency-min-closing-speed-mps "${EGO_GATE_INTER_UAV_EMERGENCY_MIN_CLOSING_SPEED_MPS}"' in runner
    assert '"EGO_GATE_INTER_UAV_EMERGENCY_MIN_CLOSING_SPEED_MPS=0.05"' in launcher


def test_two_point_astar_path_uses_the_existing_midpoint_initialization() -> None:
    astar = DYN_A_STAR.read_text(encoding="utf-8")
    optimizer = POLY_TRAJ_OPTIMIZER.read_text(encoding="utf-8")
    manager = PLANNER_MANAGER.read_text(encoding="utf-8")
    assert "if (!search_success || path.empty())" in astar
    assert "if (simple_path.size() < 2)" in optimizer
    assert "return false;" in optimizer[optimizer.index("if (simple_path.size() < 2)"):]
    assert "if (simple_path.size() == 2)" in optimizer
    assert "inserting a midpoint for minimum-jerk initialization" in optimizer
    assert "innerPts.col(0) = (simple_path[0] + simple_path[1]) / 2;" in optimizer
    assert "simple_path.insert(simple_path.begin() + 1, innerPts.col(0));" in optimizer
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


def test_map_origin_patch_is_opt_in_idempotent_and_never_targets_references(tmp_path: Path) -> None:
    source = tmp_path / "grid_map.cpp"
    source.write_text(GRID_MAP.read_text(encoding="utf-8"), encoding="utf-8")

    first = subprocess.run(
        [sys.executable, str(MAP_ORIGIN_PATCH), str(source)],
        check=True,
        capture_output=True,
        text=True,
    )
    second = subprocess.run(
        [sys.executable, str(MAP_ORIGIN_PATCH), str(source)],
        check=True,
        capture_output=True,
        text=True,
    )
    patched = source.read_text(encoding="utf-8")

    assert '"status": "patched"' in first.stdout
    assert '"status": "already_patched"' in second.stdout
    assert 'node_.param("grid_map/use_map_origin_override", use_map_origin_override, false);' in patched
    assert 'node_.param("grid_map/map_origin_x", map_origin_x, -x_size / 2.0);' in patched
    assert 'node_.param("grid_map/map_origin_y", map_origin_y, -y_size / 2.0);' in patched
    assert "if (use_map_origin_override)" in patched
    assert patched.count("if (use_map_origin_override)") == 1
    assert "else\n  {\n    mp_.map_origin_ = Eigen::Vector3d(-x_size / 2.0, -y_size / 2.0, mp_.ground_height_);" in patched

    rejected = subprocess.run(
        [sys.executable, str(MAP_ORIGIN_PATCH), str(GRID_MAP)],
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert "refusing to patch authoritative reference source" in rejected.stderr


def test_swarm_origin_override_is_plumbed_to_all_three_runtime_planners() -> None:
    launch = LAUNCH.read_text(encoding="utf-8")
    runner = SWARM_RUNNER.read_text(encoding="utf-8")

    assert '<arg name="use_map_origin_override" default="false"/>' in launch
    assert launch.count('name="grid_map/use_map_origin_override"') == 3
    assert launch.count('name="grid_map/map_origin_x"') == 3
    assert launch.count('name="grid_map/map_origin_y"') == 3
    assert "planner/plan_env/src/grid_map.cpp" in runner
    assert "patch_swarm_formation_map_origin.py" in runner
    assert 'use_map_origin_override:="${SWARM_FORMATION_D3_USE_MAP_ORIGIN_OVERRIDE}"' in runner
    assert 'map_origin_x:="${SWARM_FORMATION_D3_MAP_ORIGIN_X}"' in runner
    assert 'map_origin_y:="${SWARM_FORMATION_D3_MAP_ORIGIN_Y}"' in runner


def test_factory_gate_centers_the_local_map_on_the_formation_target() -> None:
    factory_gate = FACTORY_GATE.read_text(encoding="utf-8")
    assert '$mapOriginX = [double]$center[0] - ($mapSizeX / 2.0)' in factory_gate
    assert '$mapOriginY = [double]$center[1] - ($mapSizeY / 2.0)' in factory_gate
    assert '"SWARM_FORMATION_D3_USE_MAP_ORIGIN_OVERRIDE=true"' in factory_gate
    assert '"SWARM_FORMATION_D3_MAP_ORIGIN_X=$mapOriginX"' in factory_gate
    assert '"SWARM_FORMATION_D3_MAP_ORIGIN_Y=$mapOriginY"' in factory_gate

def test_factory_gate_exposes_a_safe_default_dynamics_profile_without_relaxing_separation() -> None:
    gate = FACTORY_GATE.read_text(encoding="utf-8")

    assert '[ValidateSet("r6_baseline_v1", "conservative_v1")]' in gate
    assert '[string]$DynamicsProfile = "conservative_v1"' in gate
    assert '"conservative_v1" = [ordered]@{' in gate
    assert 'ego_max_vel_mps = 0.45' in gate
    assert 'ego_max_acc_mps2 = 0.35' in gate
    assert 'command_speed_mps = 0.35' in gate
    assert 'command_acceleration_mps2 = 0.25' in gate
    assert 'command_lateral_acceleration_mps2 = 0.25' in gate
    assert 'command_jerk_mps3 = 0.75' in gate
    assert 'predictive_braking_deceleration_mps2 = 0.25' in gate
    assert "EGO_GATE_INTER_UAV_EMERGENCY_DECELERATION_MPS2=" in gate
    assert 'minimum_inter_uav_distance_m = 1.0' in gate
    assert 'predictive_margin_m = 0.10' in gate


def test_factory_l2_receiver_window_is_generated_and_bound_to_the_gate() -> None:
    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    contract = scenario["runtime_contract"]
    gate = FACTORY_GATE.read_text(encoding="utf-8")

    assert math.isclose(contract["swarm_trajectory_receiver_time_tolerance_s"], 2.0)
    assert math.isclose(contract["r52_observed_max_receive_age_s"], 1.676)
    assert contract["receiver_age_safety_margin_s"] > 0.0
    assert math.isclose(contract["receiver_age_safety_margin_s"], 0.324)
    assert "preserves the received trajectory start_time and phase" in contract["semantics"]
    assert "$runtimeContract = $scenario.runtime_contract" in gate
    assert '"SWARM_FORMATION_D3_SWARM_TRAJ_TIME_TOLERANCE_S=$swarmTrajectoryReceiverTimeToleranceS"' in gate
    assert "receiver_age_safety_margin_s = $receiverAgeSafetyMarginS" in gate
