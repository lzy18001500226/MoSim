# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio

import numpy as np
import omni.kit.test
import omni.timeline
import omni.ui as ui
import omni.usd
from isaacsim.core.experimental.utils.stage import create_new_stage_async
from isaacsim.robot.manipulators.examples.universal_robots.follow_target_experimental import UR10FollowTarget
from isaacsim.robot.manipulators.examples.universal_robots.ur10_experimental import UR10Experimental
from omni.kit.app import get_app


class TestURFollowTarget(omni.kit.test.AsyncTestCase):
    """Test suite for UR10 follow target components.

    This test suite verifies:
    1. UR10Experimental robot controller functionality
    2. UR10FollowTarget follow target controller functionality
    3. Robot kinematics and inverse kinematics
    4. Target following behavior
    5. Scene setup and reset operations
    """

    async def setUp(self):
        """Set up test environment before each test."""
        await create_new_stage_async()
        await get_app().next_update_async()

        self._timeline = omni.timeline.get_timeline_interface()

        # Initialize UR10Experimental robot
        self.robot = UR10Experimental(robot_path="/World/ur10_robot", create_robot=True, attach_gripper=False)

        # Initialize UR10FollowTarget controller
        self.follow_target = UR10FollowTarget()

        await get_app().next_update_async()

    async def tearDown(self):
        """Clean up after each test."""
        if self._timeline.is_playing():
            self._timeline.stop()

        # Clean up simulation context - the framework handles cleanup automatically
        await get_app().next_update_async()

    async def _initialize_physics(self):
        """Initialize physics simulation for robot operations."""
        self._timeline.play()
        await get_app().next_update_async()
        await asyncio.sleep(0.1)  # Allow physics to initialize

    async def test_ur10_experimental_initialization(self):
        """Test UR10Experimental robot initialization and basic properties."""
        # Initialize physics first
        await self._initialize_physics()

        # Verify robot was created
        self.assertIsNotNone(self.robot)
        self.assertIsNotNone(self.robot.end_effector_link)

        # Check default state
        dof_positions, _, _ = self.robot.get_current_state()
        self.assertEqual(dof_positions.shape[1], 6)  # 6 arm joints (no gripper)

        # Verify robot has correct number of DOFs
        actual_dof_count = self.robot.get_actual_dof_count()
        self.assertEqual(actual_dof_count, 6)

    async def test_ur10_follow_target_setup_scene(self):
        """Test UR10FollowTarget scene setup functionality."""
        # Setup scene with custom parameters
        target_position = np.array([0.5, 0.2, 0.3])

        self.follow_target.setup_scene(target_position=target_position)

        # Verify scene components were created
        self.assertIsNotNone(self.follow_target.robot)
        self.assertIsNotNone(self.follow_target.target_cube)
        self.assertIsNotNone(self.follow_target.target_position)

        # Verify prims exist in stage
        stage = omni.usd.get_context().get_stage()

        # Verify robot prim exists
        robot_prim = stage.GetPrimAtPath("/World/ur10_robot")
        self.assertIsNotNone(robot_prim, "Robot prim should exist in stage at /World/ur10_robot")
        self.assertTrue(robot_prim.IsValid(), "Robot prim should be valid")

        # Verify target cube prim exists
        cube_prim = stage.GetPrimAtPath("/World/TargetCube")
        self.assertIsNotNone(cube_prim, "Target cube prim should exist in stage at /World/TargetCube")
        self.assertTrue(cube_prim.IsValid(), "Target cube prim should be valid")

    async def test_ur10_follow_target_ik_methods(self):
        """Test UR10FollowTarget with different IK methods."""
        # Setup scene with a specific target position
        target_position = np.array([0.5, 0.2, 0.3])
        self.follow_target.setup_scene(target_position=target_position)

        # Initialize physics
        await self._initialize_physics()

        # Test different IK methods
        ik_methods = ["damped-least-squares", "pseudoinverse", "transpose", "singular-value-decomposition"]

        for method in ik_methods:
            # Reset to initial state
            self.follow_target.reset_robot()

            # Get initial positions for comparison
            initial_ee_pos = self.follow_target.get_robot_end_effector_position()

            # Wait for robot to move towards target
            max_frames = 500
            frame_count = 0
            position_tolerance = 0.05  # 5cm tolerance

            while frame_count < max_frames:
                # Execute with specific IK method
                self.follow_target.move_to_target(ik_method=method)

                await get_app().next_update_async()
                frame_count += 1

                # Get current positions
                current_ee_pos = self.follow_target.get_robot_end_effector_position()

                # Check if robot end effector is close to target
                distance_to_target = np.linalg.norm(current_ee_pos - target_position)
                if distance_to_target < position_tolerance:
                    break

            # Verify robot is responding and moved towards target
            current_ee_pos = self.follow_target.get_robot_end_effector_position()
            self.assertIsNotNone(current_ee_pos)

            # Verify target cube position hasn't changed (should remain at target)
            final_cube_pos = self.follow_target.get_target_position()
            np.testing.assert_array_almost_equal(
                final_cube_pos,
                target_position,
                decimal=3,
                err_msg=f"Target cube should remain at target position {target_position}",
            )

            # Verify robot end effector moved towards target (should be closer than initial position)
            initial_distance = np.linalg.norm(initial_ee_pos - target_position)
            final_distance = np.linalg.norm(current_ee_pos - target_position)

            # Robot should have moved towards target (distance should not increase significantly)
            self.assertLessEqual(
                final_distance,
                initial_distance + 0.1,  # Allow small increase due to IK constraints
                f"Robot end effector should move towards target. Initial distance: {initial_distance:.4f}, Final distance: {final_distance:.4f}",
            )

            # Verify target cube is at the expected position
            self.assertIsNotNone(self.follow_target.target_cube)
            self.assertIsNotNone(self.follow_target.target_position)
            np.testing.assert_array_almost_equal(
                self.follow_target.target_position,
                target_position,
                decimal=3,
                err_msg=f"Target position should be set to {target_position}",
            )

            # Debug: Print final positions and distances for target reach detection
            final_ee_pos = self.follow_target.get_robot_end_effector_position()
            final_cube_pos = self.follow_target.get_target_position()
            final_distance = np.linalg.norm(final_ee_pos - final_cube_pos)

            # Now test the actual assertion
            self.assertTrue(
                self.follow_target.target_reached(threshold=0.08),
                f"After moving robot towards target, target_reached(0.1) should return True. Final distance: {final_distance:.4f}m",
            )
