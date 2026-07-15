import math
import sys
import unittest
from pathlib import Path


SUNRAY_DIR = Path(__file__).resolve().parents[1] / "sunray"
sys.path.insert(0, str(SUNRAY_DIR))

from trajectory_dynamics import constrain_kinematic_step


class TrajectoryDynamicsTests(unittest.TestCase):
    def step(self, position, velocity, acceleration, target, dt=0.1):
        return constrain_kinematic_step(position, velocity, acceleration, target, dt, 0.6, 0.8, 0.6, 2.0)

    def test_straight_acceleration_ramp_is_bounded_and_consistent(self):
        result = self.step((0, 0, 1.2), (0, 0, 0), (0, 0, 0), (10, 0, 1.2))
        self.assertLessEqual(math.dist(result["acceleration"], (0, 0, 0)), 0.8 + 1e-9)
        self.assertLessEqual(math.dist(result["jerk"], (0, 0, 0)), 2.0 + 1e-9)
        self.assertAlmostEqual(result["position"][0], result["velocity"][0] * 0.1)

    def test_direction_reversal_cannot_flip_velocity_in_one_step(self):
        result = self.step((0, 0, 1.2), (0.6, 0, 0), (0, 0, 0), (-10, 0, 1.2))
        self.assertGreater(result["velocity"][0], 0.0)
        self.assertLessEqual(abs(result["acceleration"][0]), 0.6 + 1e-9)

    def test_velocity_stays_bounded_during_continuous_acceleration(self):
        position = (0.0, 0.0, 1.2)
        velocity = (0.0, 0.0, 0.0)
        acceleration = (0.0, 0.0, 0.0)
        for _ in range(200):
            result = self.step(position, velocity, acceleration, (100, 0, 1.2))
            position = result["position"]
            velocity = result["velocity"]
            acceleration = result["acceleration"]
            self.assertLessEqual(math.dist(velocity, (0, 0, 0)), 0.6 + 1e-8)

    def test_ninety_degree_turn_has_bounded_lateral_acceleration(self):
        result = self.step((0, 0, 1.2), (0.6, 0, 0), (0, 0, 0), (0, 10, 1.2))
        lateral = math.hypot(*result["acceleration"][:2])
        self.assertLessEqual(lateral, 0.6 + 1e-9)

    def test_position_jump_is_integrated_not_published_directly(self):
        result = self.step((0, 0, 1.2), (0, 0, 0), (0, 0, 0), (100, 100, 1.2))
        self.assertLess(math.hypot(*result["position"][:2]), 0.1)

    def test_fixed_z_remains_fixed(self):
        result = self.step((0, 0, 1.2), (0, 0, 0), (0, 0, 0), (1, 0, 1.2))
        self.assertAlmostEqual(result["position"][2], 1.2)
        self.assertAlmostEqual(result["velocity"][2], 0.0)

    def test_non_finite_input_is_rejected(self):
        with self.assertRaises(ValueError):
            self.step((0, 0, 1.2), (0, 0, 0), (0, 0, 0), (float("nan"), 0, 1.2))


if __name__ == "__main__":
    unittest.main()
