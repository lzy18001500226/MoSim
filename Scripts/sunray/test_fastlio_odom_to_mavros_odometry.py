#!/usr/bin/env python3

import math
import unittest

from fastlio_odom_to_mavros_odometry import (
    covariance_with_floors,
    rotate_covariance_world_to_body,
    world_to_body_vector,
)


class FastlioMavrosOdometryFrameTest(unittest.TestCase):
    def test_identity_keeps_world_velocity(self):
        actual = world_to_body_vector((0.0, 0.0, 0.0, 1.0), (1.0, -2.0, 3.0))
        self.assertSequenceAlmostEqual(actual, (1.0, -2.0, 3.0))

    def test_yaw_ninety_maps_world_y_to_body_x(self):
        half = math.sqrt(0.5)
        actual = world_to_body_vector((0.0, 0.0, half, half), (0.0, 2.0, 0.0))
        self.assertSequenceAlmostEqual(actual, (2.0, 0.0, 0.0))

    def test_covariance_rotates_with_velocity(self):
        half = math.sqrt(0.5)
        covariance = [[4.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 9.0]]
        actual = rotate_covariance_world_to_body((0.0, 0.0, half, half), covariance)
        self.assertSequenceAlmostEqual(
            (actual[0][0], actual[1][1], actual[2][2]),
            (1.0, 4.0, 9.0),
        )

    def test_covariance_floor_prevents_zero_confidence(self):
        actual = covariance_with_floors([0.0] * 36, 0.2, 0.5)
        self.assertSequenceAlmostEqual(
            (actual[0], actual[7], actual[14], actual[21], actual[28], actual[35]),
            (0.04, 0.04, 0.04, 0.25, 0.25, 0.25),
        )

    def assertSequenceAlmostEqual(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for actual_value, expected_value in zip(actual, expected):
            self.assertAlmostEqual(actual_value, expected_value, places=7)


if __name__ == "__main__":
    unittest.main()
