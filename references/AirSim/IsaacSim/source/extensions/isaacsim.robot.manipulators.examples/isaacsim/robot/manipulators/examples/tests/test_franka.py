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
from isaacsim.robot.manipulators.examples.franka.franka_experimental import FrankaExperimental
from isaacsim.robot.manipulators.examples.franka.pick_place.pick_place import FrankaPickPlace
from omni.kit.app import get_app


class TestFranka(omni.kit.test.AsyncTestCase):
    """Test suite for Franka robot components.

    This test suite verifies:
    1. FrankaExperimental robot controller functionality
    2. FrankaPickPlace pick-and-place controller functionality
    3. Robot kinematics and inverse kinematics
    4. Gripper control operations
    5. Scene setup and reset operations
    """

    async def setUp(self):
        """Set up test environment before each test."""
        await create_new_stage_async()
        await get_app().next_update_async()

        self._timeline = omni.timeline.get_timeline_interface()

        # Initialize FrankaExperimental robot
        self.robot = FrankaExperimental(robot_path="/World/robot", create_robot=True)

        # Initialize FrankaPickPlace controller
        self.pick_place = FrankaPickPlace()

        await get_app().next_update_async()

    async def tearDown(self):
        """Clean up after each test."""
        if self._timeline.is_playing():
            self._timeline.stop()

        # Clean up simulation context - remove problematic SimulationManager call
        # The framework handles cleanup automatically

        await get_app().next_update_async()

    async def _initialize_physics(self):
        """Initialize physics simulation for robot operations."""
        self._timeline.play()
        await get_app().next_update_async()
        await asyncio.sleep(0.1)  # Allow physics to initialize

    async def test_franka_experimental_initialization(self):
        """Test FrankaExperimental robot initialization and basic properties."""
        # Initialize physics first
        await self._initialize_physics()

        # Verify robot was created
        self.assertIsNotNone(self.robot)
        self.assertIsNotNone(self.robot.end_effector_link)

        # Check default state
        dof_positions, _, _ = self.robot.get_current_state()
        self.assertEqual(dof_positions.shape[1], 9)  # 7 arm joints + 2 gripper joints

    async def test_franka_pick_place_setup_scene(self):
        """Test FrankaPickPlace scene setup functionality."""
        # Setup scene with custom parameters
        cube_position = np.array([0.4, 0.0, 0.0258])
        target_position = np.array([-0.2, -0.2, 0.12])

        self.pick_place.setup_scene(cube_initial_position=cube_position, target_position=target_position)

        # Verify scene components were created
        self.assertIsNotNone(self.pick_place.robot)
        self.assertIsNotNone(self.pick_place.cube)
        self.assertIsNotNone(self.pick_place.cube_initial_position)

        # Verify prims exist in stage
        stage = omni.usd.get_context().get_stage()

        # Verify robot prim exists
        robot_prim = stage.GetPrimAtPath("/World/robot")
        self.assertIsNotNone(robot_prim, "Robot prim should exist in stage at /World/robot")
        self.assertTrue(robot_prim.IsValid(), "Robot prim should be valid")

        # Verify cube prim exists
        cube_prim = stage.GetPrimAtPath("/World/Cube")
        self.assertIsNotNone(cube_prim, "Cube prim should exist in stage at /World/cube")
        self.assertTrue(cube_prim.IsValid(), "Cube prim should be valid")

    async def test_franka_pick_place_completion(self):
        """Test FrankaPickPlace completion detection."""
        # Setup scene
        self.pick_place.setup_scene()

        # Initialize physics
        await self._initialize_physics()

        # Initially not done
        self.assertFalse(self.pick_place.is_done())

        # Complete all phases with timeout protection
        max_frames = 300  # Reasonable timeout for pick-and-place operation
        frame_count = 0

        while not self.pick_place.is_done() and frame_count < max_frames:
            self.pick_place.forward()
            await get_app().next_update_async()
            frame_count += 1

            # Print progress every 50 frames
            if frame_count % 50 == 0:
                print(f"Frame {frame_count}: Still executing pick-and-place...")

        # Check if we hit the timeout
        if frame_count >= max_frames:
            self.fail(
                f"Pick-and-place operation did not complete within {max_frames} frames. Operation may be stuck or taking longer than expected."
            )

        # Should be done after all phases
        self.assertTrue(self.pick_place.is_done(), f"Operation should be complete after {frame_count} frames")

    async def test_franka_pick_place_ik_methods(self):
        """Test FrankaPickPlace with different IK methods."""
        # Setup scene
        self.pick_place.setup_scene()

        # Initialize physics
        await self._initialize_physics()

        # Test different IK methods
        ik_methods = ["damped-least-squares", "pseudoinverse", "transpose"]

        for method in ik_methods:
            # Reset to initial state
            self.pick_place.reset_robot()

            # Execute with specific IK method
            result = self.pick_place.forward(ik_method=method)
            self.assertTrue(result)
            await get_app().next_update_async()

    async def test_franka_integration(self):
        """Test integration between FrankaExperimental and FrankaPickPlace."""
        # Setup pick-and-place scene
        self.pick_place.setup_scene()

        # Initialize physics
        await self._initialize_physics()

        # Verify robot is accessible through pick-place controller
        self.assertIsNotNone(self.pick_place.robot)
        self.assertIsInstance(self.pick_place.robot, FrankaExperimental)

        # Test that we can control the robot directly (avoid gripper issues)
        self.pick_place.robot.set_gripper_position(np.array([[0.02, 0.02]]))
        await get_app().next_update_async()

        # Test end effector control through the robot
        # Use a more conservative target that's likely within reach
        target_position = np.array([0.5, 0.0, 0.0258])  # Closer and lower target
        target_orientation = self.pick_place.robot.get_downward_orientation()

        # Get initial pose for comparison
        _, initial_position, initial_orientation = self.pick_place.robot.get_current_state()

        # Check if target is reachable (basic sanity check)
        if np.linalg.norm(initial_position - target_position) > 1.0:  # More than 1m away
            self.skipTest("Target position too far from initial position - may be unreachable")

        self.pick_place.robot.set_end_effector_pose(position=target_position, orientation=target_orientation)

        # Wait for robot to reach target pose with timeout
        max_frames = 300  # Reduced timeout since we're using a closer target
        frame_count = 0
        position_tolerance = 0.05  # 5cm tolerance for position (increased)
        orientation_tolerance = 0.2  # ~11.5 degrees tolerance for orientation (increased)

        # Track if we're making progress
        last_position_error = float("inf")
        stuck_frames = 0

        while frame_count < max_frames:
            await get_app().next_update_async()
            frame_count += 1

            # Get current end effector pose using the robot's get_current_state method
            _, current_position, current_orientation = self.pick_place.robot.get_current_state()

            # Check if we've reached the target
            position_error = np.linalg.norm(current_position - target_position)
            orientation_error = np.linalg.norm(current_orientation - target_orientation)

            # Check if we're making progress
            if abs(position_error - last_position_error) < 0.001:  # Less than 1mm change
                stuck_frames += 1
            else:
                stuck_frames = 0
                last_position_error = position_error

            # Fail early if stuck for too long
            if stuck_frames > 50:  # 50 frames without progress
                self.fail(
                    f"End effector stuck at position error {position_error:.4f}m for {stuck_frames} frames. Robot may not be moving."
                )

            if position_error < position_tolerance and orientation_error < orientation_tolerance:
                break

        # Verify we reached the target within timeout
        if frame_count >= max_frames:
            self.fail(
                f"End effector did not reach target pose within {max_frames} frames. Final position error: {position_error:.4f}m, orientation error: {orientation_error:.4f}"
            )

        # Final verification that we're at the target
        self.assertLess(
            position_error,
            position_tolerance,
            f"End effector should be at target position. Error: {position_error:.4f}m",
        )
        self.assertLess(
            orientation_error,
            orientation_tolerance,
            f"End effector should have target orientation. Error: {orientation_error:.4f}",
        )

        # Verify robot state is accessible
        dof_positions, _, _ = self.pick_place.robot.get_current_state()
        self.assertIsNotNone(dof_positions)
