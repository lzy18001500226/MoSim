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

    def test_factory_fuel_wrapper_enables_absolute_hover_takeoff_handoff(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "sunray"
            / "start_factory_fuel_single_exploration_review.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("[bool]$PublishHoverDuringTakeoff = $true", source)
        self.assertIn("DIFF_PUBLISH_HOVER_DURING_TAKEOFF=", source)


if __name__ == "__main__":
    unittest.main()
