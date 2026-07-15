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


if __name__ == "__main__":
    unittest.main()
