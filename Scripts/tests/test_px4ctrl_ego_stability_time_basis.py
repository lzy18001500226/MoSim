import unittest
from pathlib import Path


class Px4ctrlEgoStabilityTimeBasisTests(unittest.TestCase):
    def test_pre_planner_stability_dwell_uses_simulation_time(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "px4ctrl_ego_single_mission_node.py"
        ).read_text(encoding="utf-8")
        self.assertIn("now_motion - stable_reached_motion_time >= required_stable_s", source)
        self.assertNotIn("time.time() - stable_reached_time >= required_stable_s", source)

    def test_takeoff_gate_uses_home_relative_absolute_target(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "px4ctrl_ego_single_mission_node.py"
        ).read_text(encoding="utf-8")
        self.assertIn("def takeoff_target_z_m(self)", source)
        self.assertIn("return float(self.home_odom_z) + float(self.args.takeoff_height)", source)
        self.assertIn("home_odom_z + --takeoff-height", source)
        self.assertNotIn(
            'odom_z_error = self.z_error(self.last_odom, self.args.takeoff_height)',
            source,
        )
        self.assertNotIn(
            'abs(self.last_odom["z"] - self.args.takeoff_height) < self.args.takeoff_z_tol',
            source,
        )

    def test_truth_odom_divergence_aborts_through_controlled_landing(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "px4ctrl_ego_single_mission_node.py"
        ).read_text(encoding="utf-8")
        self.assertIn("def truth_odom_relative_z_state(self)", source)
        self.assertIn('f"{prefix}_truth_odom_z_divergence_above_gate"', source)
        self.assertIn("--execute-max-truth-odom-z-error-m", source)
        self.assertIn("def abort_for_flight_safety", source)
        self.assertIn("return self.perform_safe_stop(rate, safety_blockers=list(blockers))", source)
        self.assertIn("status=\"blocked\" if final_blockers else \"safe_stopped\"", source)

    def test_factory_fuel_wrapper_enables_absolute_hover_takeoff_handoff(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "start_factory_fuel_single_exploration_review.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("[bool]$PublishHoverDuringTakeoff = $true", source)
        self.assertIn("DIFF_PUBLISH_HOVER_DURING_TAKEOFF=", source)

    def test_diff_gate_enables_absolute_hover_takeoff_handoff(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "run_diff_single_auto123_gate.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'DIFF_PUBLISH_HOVER_DURING_TAKEOFF="${DIFF_PUBLISH_HOVER_DURING_TAKEOFF:-true}"',
            source,
        )
        self.assertIn(
            'DIFF_PUBLISH_HOVER_DURING_TAKEOFF="${DIFF_PUBLISH_HOVER_DURING_TAKEOFF}"',
            source,
        )
        self.assertIn("DIFF_PUBLISH_HOVER_DURING_TAKEOFF=${DIFF_PUBLISH_HOVER_DURING_TAKEOFF}", source)

    def test_factory_diff_gate_pins_factory_scene_and_calibration(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "run_factory_l2_diff_single_c99_gate.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("FACTORY_WORLD_MODE=clean", source)
        self.assertIn("factoryenvironmentcollect_l2_static_review_clean.sdf", source)
        self.assertIn("SUNRAY_UAV_INIT_Y=120.0", source)
        self.assertIn("GOALS=-4.0,118.0,1.0", source)
        self.assertIn("DIFF_INTERACTIVE_TARGET_HOLD_S=5.0", source)
        self.assertIn("DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S=5.0", source)
        self.assertIn('PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.294}"', source)

    def test_factory_diff_gate_has_nonexecuting_help(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "run_factory_l2_diff_single_c99_gate.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('case "${1:-}" in', source)
        self.assertIn("-h|--help)", source)
        self.assertIn("Usage: bash Scripts/sunray/run_factory_l2_diff_single_c99_gate.sh", source)

    def test_diff_gate_records_nonempty_raw_lidar_readiness(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "run_px4ctrl_ego_single_gate.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("wait_for_nonempty_pointcloud2.py", source)
        self.assertIn("RAW_LIDAR_READY_TIMEOUT_S", source)
        self.assertIn("raw_lidar_readiness_", source)
        waiter = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "wait_for_nonempty_pointcloud2.py"
        ).read_text(encoding="utf-8")
        self.assertIn('state.get("status") != "passed"', waiter)
        self.assertNotIn("rospy.signal_shutdown", waiter)

    def test_factory_formation_wrapper_keeps_early_hover_handoff_opt_in(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "run_factory_l2_swarm_formation_obstacle_gate.ps1"
        ).read_text(encoding="utf-8")
        mission = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "px4ctrl_ego_swarm_mission_node.py"
        ).read_text(encoding="utf-8")

        self.assertIn("[switch]$PublishHoverDuringTakeoff", source)
        self.assertIn(
            '"EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF=$($PublishHoverDuringTakeoff.ToString().ToLowerInvariant())",',
            source,
        )
        self.assertNotIn('"EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF=true"', source)
        self.assertIn('"takeoff_hover_height_not_held"', mission)

    def test_factory_fuel_ue_review_is_resource_bounded(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "start_factory_fuel_single_exploration_review.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("[int]$UnrealMaxFps = 30", source)
        self.assertIn('"-ExecCmds=`"t.MaxFPS $UnrealMaxFps`""', source)
        self.assertIn('$ueProcess.PriorityClass = "BelowNormal"', source)
        self.assertIn("max_render_fps = $UnrealMaxFps", source)
        self.assertIn('process_priority = "BelowNormal"', source)


if __name__ == "__main__":
    unittest.main()
