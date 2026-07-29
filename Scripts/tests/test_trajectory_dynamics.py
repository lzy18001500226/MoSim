import math
import sys
import unittest
from pathlib import Path


SUNRAY_DIR = Path(__file__).resolve().parents[1] / "sunray"
sys.path.insert(0, str(SUNRAY_DIR))

from trajectory_dynamics import (
    body_to_world_vector,
    constrain_kinematic_step,
    enforce_position_z_bounds,
    inter_uav_braking_guard,
)


class TrajectoryDynamicsTests(unittest.TestCase):
    def step(self, position, velocity, acceleration, target, dt=0.1):
        return constrain_kinematic_step(position, velocity, acceleration, target, dt, 0.6, 0.8, 0.6, 2.0)

    def test_straight_acceleration_ramp_is_bounded_and_consistent(self):
        result = self.step((0, 0, 1.2), (0, 0, 0), (0, 0, 0), (10, 0, 1.2))
        self.assertLessEqual(math.dist(result["acceleration"], (0, 0, 0)), 0.8 + 1e-9)
        self.assertLessEqual(math.dist(result["jerk"], (0, 0, 0)), 2.0 + 1e-9)
        self.assertAlmostEqual(result["position"][0], result["velocity"][0] * 0.1)

    def test_pair_guard_triggers_before_a_fast_closing_pair_reaches_minimum(self):
        result = inter_uav_braking_guard(
            (0, 0, 1),
            (1, 0, 0),
            (3, 0, 1),
            (-1, 0, 0),
            min_distance_m=1.5,
            deceleration_mps2=1.2,
            margin_m=0.2,
        )
        self.assertTrue(result["triggered"])
        self.assertAlmostEqual(result["closing_speed_mps"], 2.0)
        self.assertGreater(result["trigger_distance_m"], 3.0)

    def test_body_to_world_vector_rotates_a_yaw_ninety_velocity(self):
        half = math.sqrt(0.5)
        actual = body_to_world_vector((0.0, 0.0, half, half), (1.0, 0.0, 0.0))
        self.assertAlmostEqual(actual[0], 0.0, places=9)
        self.assertAlmostEqual(actual[1], 1.0, places=9)
        self.assertAlmostEqual(actual[2], 0.0, places=9)

    def test_pair_guard_does_not_trigger_for_separating_pair(self):
        result = inter_uav_braking_guard(
            (0, 0, 1),
            (-1, 0, 0),
            (3, 0, 1),
            (1, 0, 0),
            min_distance_m=1.5,
            deceleration_mps2=1.2,
            margin_m=0.2,
        )
        self.assertFalse(result["triggered"])
        self.assertEqual(result["closing_speed_mps"], 0.0)

    def test_pair_guard_does_not_trigger_for_stationary_pair_inside_predictive_margin(self):
        result = inter_uav_braking_guard(
            (0, 0, 1),
            (0, 0, 0),
            (1.18, 0, 1),
            (0, 0, 0),
            min_distance_m=1.0,
            deceleration_mps2=1.2,
            margin_m=0.2,
        )
        self.assertFalse(result["triggered"])
        self.assertFalse(result["hard_distance_violation"])
        self.assertFalse(result["predicted_braking_violation"])
        self.assertEqual(result["closing_speed_mps"], 0.0)

    def test_pair_guard_ignores_low_speed_odom_noise_inside_predictive_margin(self):
        result = inter_uav_braking_guard(
            (0, 0, 1),
            (0.0065, 0, 0),
            (1.18, 0, 1),
            (0, 0, 0),
            min_distance_m=1.0,
            deceleration_mps2=1.2,
            margin_m=0.2,
            min_predictive_closing_speed_mps=0.05,
        )
        self.assertFalse(result["triggered"])
        self.assertFalse(result["hard_distance_violation"])
        self.assertFalse(result["predicted_braking_violation"])
        self.assertAlmostEqual(result["closing_speed_mps"], 0.0065)

    def test_pair_guard_triggers_for_meaningful_closing_speed_inside_predictive_margin(self):
        result = inter_uav_braking_guard(
            (0, 0, 1),
            (0.10, 0, 0),
            (1.18, 0, 1),
            (0, 0, 0),
            min_distance_m=1.0,
            deceleration_mps2=1.2,
            margin_m=0.2,
            min_predictive_closing_speed_mps=0.05,
        )
        self.assertTrue(result["triggered"])
        self.assertTrue(result["predicted_braking_violation"])

    def test_pair_guard_triggers_inside_hard_distance_even_when_separating(self):
        result = inter_uav_braking_guard(
            (0, 0, 1),
            (-1, 0, 0),
            (0.8, 0, 1),
            (1, 0, 0),
            min_distance_m=1.0,
            deceleration_mps2=1.2,
            margin_m=0.0,
        )
        self.assertTrue(result["triggered"])
        self.assertAlmostEqual(result["distance_m"], 0.8)
        self.assertEqual(result["closing_speed_mps"], 0.0)

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

    def test_speed_braking_margin_preserves_jerk_limit(self):
        position = (0.0, 0.0, 1.2)
        velocity = (0.0, 0.0, 0.0)
        acceleration = (0.0, 0.0, 0.0)
        for _ in range(500):
            result = constrain_kinematic_step(
                position,
                velocity,
                acceleration,
                (100.0, 0.0, 1.2),
                0.02,
                2.0,
                1.2,
                1.2,
                6.0,
            )
            position = result["position"]
            velocity = result["velocity"]
            acceleration = result["acceleration"]
            self.assertLessEqual(norm := math.dist(velocity, (0, 0, 0)), 2.0 + 1e-8)
            self.assertGreaterEqual(norm, 0.0)
            self.assertLessEqual(math.dist(result["jerk"], (0, 0, 0)), 6.0 + 1e-8)

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

    def test_final_altitude_gate_corrects_integrated_overshoot(self):
        result = enforce_position_z_bounds(
            (1.0, 2.0, 1.42),
            (0.2, 0.3, 0.7),
            (0.1, 0.2, 1.1),
            (0.0, 0.0, 3.0),
            0.9,
            1.35,
        )
        self.assertTrue(result["corrected"])
        self.assertEqual(result["position"], (1.0, 2.0, 1.35))
        self.assertEqual(result["velocity"][2], 0.0)
        self.assertEqual(result["acceleration"][2], 0.0)
        self.assertEqual(result["jerk"][2], 0.0)


if __name__ == "__main__":
    unittest.main()
