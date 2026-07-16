import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RacerSwarmExplorationContractTests(unittest.TestCase):
    def test_exploration_duration_uses_ros_simulation_time(self):
        source = (ROOT / "sunray" / "px4ctrl_ego_swarm_mission_node.py").read_text(encoding="utf-8")
        self.assertIn("self.exploration_started_t = self.now()", source)
        self.assertIn("self.now() - self.exploration_started_t < self.args.exploration_duration_s", source)
        self.assertNotIn("time.time() - execute_start < self.args.exploration_duration_s", source)

    def test_swarm_exploration_has_team_trajectory_freshness_gate(self):
        source = (ROOT / "sunray" / "px4ctrl_ego_swarm_mission_node.py").read_text(encoding="utf-8")
        self.assertIn("def exploration_team_trajectory_freshness_summary", source)
        self.assertIn("def exploration_trajectory_freshness_summary", source)
        self.assertIn('blockers.append("swarm_planner_trajectory_stale")', source)
        self.assertNotIn('blockers.append(prefix + "planner_trajectory_stale")', source)
        self.assertIn('"scope": "swarm_team"', source)
        self.assertIn('"time_basis": "ros_simulation_time"', source)

    def test_racer_semantic_window_ends_with_execute_phase(self):
        source = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")
        self.assertIn('str(row.get("phase") or "") != "ego_execute"', source)
        self.assertIn('print(f"{max(done_times):.3f}")', source)

    def test_factory_wrapper_scales_wall_budget_from_expected_rtf(self):
        source = (
            ROOT / "sunray" / "run_factory_l2_indoor_racer_swarm_coverage_gate.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('MIN_EXPECTED_RTF="${MIN_EXPECTED_RTF:-0.08}"', source)
        self.assertIn('WALL_TIMEOUT_S="${WALL_TIMEOUT_S:-$((TOTAL_TIMEOUT_S + 600))}"', source)
        self.assertIn(
            'MIN_WALL_TIMEOUT_S=$((MAVROS_READY_TIMEOUT_S + TOTAL_TIMEOUT_S + 120))',
            source,
        )
        self.assertIn('WALL_TIMEOUT_S="${MIN_WALL_TIMEOUT_S}"', source)
        self.assertIn('"effective_wall_timeout_s": ${WALL_TIMEOUT_S}', source)

    def test_swarm_runner_cleans_up_the_actual_mission_process(self):
        source = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'pkill -f "[p]x4ctrl_ego_swarm_mission_node.py"',
            source,
        )

    def test_ros_master_readiness_does_not_repeat_a_successful_probe(self):
        source = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("local ros_master_ready=false", source)
        self.assertIn("ros_master_ready=true", source)
        self.assertIn('if [[ "${ros_master_ready}" != "true" ]]', source)
        self.assertNotIn(
            'if ! timeout 2s rosparam get /run_id >/dev/null 2>&1; then\n'
            '    echo "ROS master did not expose /run_id before Gazebo start"',
            source,
        )

    def test_racer_acceptance_distance_matches_planner_safe_distance(self):
        source = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'EGO_GATE_MIN_INTER_UAV_DISTANCE="${RACER_D3_SWARM_SAFE_DIST}"',
            source,
        )
        self.assertIn(
            '--min-inter-uav-distance "${EGO_GATE_MIN_INTER_UAV_DISTANCE}"',
            source,
        )
        self.assertIn(
            '"min_inter_uav_distance_gate_m": ${EGO_GATE_MIN_INTER_UAV_DISTANCE}',
            source,
        )

    def test_racer_exploration_has_live_odom_pair_emergency_hold(self):
        mission = (ROOT / "sunray" / "px4ctrl_ego_swarm_mission_node.py").read_text(
            encoding="utf-8"
        )
        runner = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("def inter_uav_emergency_snapshot", mission)
        self.assertIn('"source": "mavros_fastlio_odom"', mission)
        self.assertIn('blockers.append("inter_uav_emergency_hold")', mission)
        self.assertIn("--inter-uav-emergency-hold-enabled", runner)

    def test_landing_uses_sim_time_and_requires_height_and_disarm(self):
        mission = (ROOT / "sunray" / "px4ctrl_ego_swarm_mission_node.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("def run_landing", mission)
        self.assertIn("self.now() - start_sim_t", mission)
        self.assertIn("time.monotonic() - start_wall_t", mission)
        self.assertIn('exit_reason = "simulation_time_timeout"', mission)
        self.assertIn('exit_reason = "wall_time_hard_timeout"', mission)
        self.assertIn('"landed": truth_below_gate and odom_below_gate and disarmed', mission)
        self.assertIn("uav.home_truth_z + self.args.landed_z_tolerance_m", mission)
        self.assertIn("uav.home_odom_z + self.args.landed_z_tolerance_m", mission)
        self.assertIn("uav.home_truth_z = None if uav.truth is None", mission)
        self.assertIn("self.now() - stop_start_sim", mission)
        self.assertIn("time.monotonic() - stop_start_wall", mission)
        self.assertIn('"simulation_quiet_period_completed"', mission)
        self.assertIn('blockers.append("pre_land_command_quiesce_timeout")', mission)
        self.assertIn('blockers.append(prefix + "landing_not_completed")', mission)
        self.assertIn('blockers.append(prefix + "still_armed_after_land")', mission)
        self.assertEqual(mission.count("self.run_landing(rate)"), 3)
        self.assertNotIn("land_start = time.time()", mission)

        runner = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn('EGO_GATE_LAND_WALL_TIMEOUT_S="${EGO_GATE_LAND_WALL_TIMEOUT_S:-300.0}"', runner)
        self.assertIn('--land-wall-timeout-s "${EGO_GATE_LAND_WALL_TIMEOUT_S}"', runner)
        self.assertIn(
            'EGO_GATE_PRE_LAND_NO_CMD_WALL_TIMEOUT_S="${EGO_GATE_PRE_LAND_NO_CMD_WALL_TIMEOUT_S:-30.0}"',
            runner,
        )
        self.assertIn(
            '--pre-land-no-cmd-wall-timeout-s "${EGO_GATE_PRE_LAND_NO_CMD_WALL_TIMEOUT_S}"',
            runner,
        )
        self.assertIn('EGO_GATE_LANDED_Z_TOLERANCE_M="${EGO_GATE_LANDED_Z_TOLERANCE_M:-0.08}"', runner)
        self.assertIn('--landed-z-tolerance-m "${EGO_GATE_LANDED_Z_TOLERANCE_M}"', runner)

    def test_takeoff_uses_sim_time_with_a_wall_hard_limit(self):
        mission = (ROOT / "sunray" / "px4ctrl_ego_swarm_mission_node.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("takeoff_start_sim = self.now()", mission)
        self.assertIn("time.monotonic() - takeoff_start_wall", mission)
        self.assertIn('takeoff_exit_reason = "simulation_time_timeout"', mission)
        self.assertIn('takeoff_exit_reason = "wall_time_hard_timeout"', mission)
        self.assertIn('"time_basis": "ros_simulation_time_with_wall_hard_limit"', mission)
        self.assertIn('parser.add_argument("--takeoff-wall-timeout-s"', mission)
        self.assertNotIn(
            "time.time() - takeoff_start < self.args.takeoff_timeout_s",
            mission,
        )

        runner = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'EGO_GATE_TAKEOFF_WALL_TIMEOUT_S="${EGO_GATE_TAKEOFF_WALL_TIMEOUT_S:-300.0}"',
            runner,
        )
        self.assertIn(
            '--takeoff-wall-timeout-s "${EGO_GATE_TAKEOFF_WALL_TIMEOUT_S}"',
            runner,
        )


if __name__ == "__main__":
    unittest.main()
