# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import omni.usd
from isaacsim.core.experimental.utils.stage import create_new_stage_async
from isaacsim.examples.interactive.ur_follow_target.follow_target_experimental import UR10FollowTargetInteractive
from isaacsim.examples.interactive.ur_follow_target.follow_target_extension_experimental import UR10FollowTargetUI
from omni.kit.app import get_app


class TestURFollowTarget(omni.kit.test.AsyncTestCase):
    """Test suite for the UR10 Follow Target interactive example.

    This test suite verifies:
    1. UI button interactions (Load, Reset, Start/Stop Follow Target)
    2. IK method selection functionality
    3. Simulation execution and robot following behavior
    4. Status display and updates
    """

    async def setUp(self):
        """Set up test environment before each test."""
        await create_new_stage_async()

        await get_app().next_update_async()

        # Initialize timeline
        self._timeline = omni.timeline.get_timeline_interface()

        self.sample = UR10FollowTargetInteractive()
        await self.sample.load_world_async()

        # Initialize UI template
        self.ui_template = UR10FollowTargetUI(
            ext_id="test_ext",
            file_path="test_path",
            title="Test UR Follow Target",
            overview="Test overview",
            sample=self.sample,
        )

        self.ui_template.build_ui()
        self.task_ui_elements = self.ui_template.task_ui_elements

        await get_app().next_update_async()

        # Reset UI state to ensure consistent starting conditions
        self._reset_ui_state()

    def _reset_ui_state(self):
        """Reset UI state to initial conditions."""
        if "Follow Target" in self.task_ui_elements:
            self.task_ui_elements["Follow Target"].enabled = False
        if "Status" in self.task_ui_elements:
            self.task_ui_elements["Status"].text = "Ready"

    async def tearDown(self):
        """Clean up after each test."""
        # Stop timeline if running
        if self._timeline.is_playing():
            self._timeline.stop()

        if hasattr(self, "sample") and self.sample:
            self.sample.simulation_context_cleanup()

        await get_app().next_update_async()

    async def test_load_button_click(self):
        """Test that the Load button properly sets up the scene."""
        self.ui_template._on_load_world()

        await get_app().next_update_async()
        await asyncio.sleep(0.5)

        self.ui_template.post_load_button_event()

        for _ in range(30):
            await get_app().next_update_async()

        sim_context = self.sample.get_simulation_context()
        self.assertIsNotNone(sim_context, "Simulation context should exist after load")
        sim_context.play()
        await asyncio.sleep(0.5)
        sim_context.pause()

        # Verify scene was loaded
        self.assertTrue(self.sample.controller is not None, "Controller should be initialized after load")
        self.assertTrue(self.sample.controller.robot is not None, "Robot should be initialized after load")
        self.assertTrue(self.sample.controller.target_cube is not None, "Target cube should be initialized after load")

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

        # Verify UI state after load
        self.assertTrue(
            self.task_ui_elements["Follow Target"].enabled, "Follow Target button should be enabled after load"
        )
        self.assertEqual(self.task_ui_elements["Status"].text, "Scene loaded - ready to start")

    async def test_reset_button_click(self):
        """Test that the Reset button properly resets the scene."""
        await self.test_load_button_click()
        self.ui_template._on_reset()

        await get_app().next_update_async()
        await asyncio.sleep(0.5)

        sim_context = self.sample.get_simulation_context()
        self.assertIsNotNone(sim_context, "Simulation context should exist after load")

        sim_context.play()
        await asyncio.sleep(0.5)  # Let physics initialize and settle

        # Get initial robot and target cube positions
        initial_robot_pos = self.sample.controller.robot.get_dof_positions().numpy()
        initial_cube_pos = self.sample.controller.get_target_position()

        # Move robot to different position
        self.sample.controller.robot.set_dof_positions(np.array([[0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]))

        # Reset the scene
        self.ui_template._on_reset()

        sim_context.play()
        await asyncio.sleep(0.5)

        current_robot_pos = self.sample.controller.robot.get_dof_positions().numpy()
        current_cube_pos = self.sample.controller.get_target_position()

        # Verify robot returned to initial position
        np.testing.assert_array_almost_equal(current_robot_pos, initial_robot_pos, decimal=2)
        np.testing.assert_array_almost_equal(current_cube_pos, initial_cube_pos, decimal=2)

        # Verify prims still exist in stage after reset
        stage = omni.usd.get_context().get_stage()

        # Verify robot prim still exists and is valid
        robot_prim = stage.GetPrimAtPath("/World/ur10_robot")
        self.assertIsNotNone(robot_prim, "Robot prim should still exist in stage after reset")
        self.assertTrue(robot_prim.IsValid(), "Robot prim should still be valid after reset")

        # Verify target cube prim still exists and is valid
        cube_prim = stage.GetPrimAtPath("/World/TargetCube")
        self.assertIsNotNone(cube_prim, "Target cube prim should still exist in stage after reset")
        self.assertTrue(cube_prim.IsValid(), "Target cube prim should still be valid after reset")

        # Verify UI state after reset
        self.assertTrue(
            self.task_ui_elements["Follow Target"].enabled, "Follow Target button should be enabled after reset"
        )
        self.assertEqual(self.task_ui_elements["Status"].text, "Ready")

    async def test_start_stop_follow_target_button_click(self):
        """Test that the Start/Stop Follow Target button initiates and stops the following behavior."""
        # First load the scene
        await self.test_load_button_click()

        # Verify initial state
        self.assertFalse(self.sample.is_following(), "Should not be following initially")
        self.assertTrue(self.task_ui_elements["Follow Target"].enabled, "Button should be enabled")

        # Call the Start Follow Target button's click handler
        self.ui_template._on_follow_target_button_event(True)  # True = START
        await get_app().next_update_async()

        # Verify execution started
        self.assertTrue(self.sample.is_following(), "Should be following after function call")
        self.assertTrue(self.task_ui_elements["Follow Target"].enabled, "Button should remain enabled during execution")

        # Verify timeline is playing
        self.assertTrue(self._timeline.is_playing(), "Timeline should be playing during execution")

        # Now test stopping
        self.ui_template._on_follow_target_button_event(False)  # False = STOP
        await get_app().next_update_async()

        # Verify execution stopped
        self.assertFalse(self.sample.is_following(), "Should not be following after stop")
        self.assertTrue(self.task_ui_elements["Follow Target"].enabled, "Button should remain enabled after stop")

    async def test_ik_method_selection(self):
        """Test that IK method selection works correctly."""
        await self.test_load_button_click()

        # Test different IK methods
        test_methods = ["damped-least-squares", "pseudoinverse", "transpose", "singular-value-decomposition"]

        for method in test_methods:
            # Simulate dropdown selection
            self.ui_template._on_ik_method_change(method)

            # Verify the method was set in the sample
            self.assertEqual(self.sample._ik_method, method, f"IK method should be set to {method}")

    async def test_status_display_and_updates(self):
        """Test that status display works correctly and updates properly."""
        await self.test_load_button_click()

        # Test initial status
        initial_status = self.sample.get_controller_status()
        self.assertIsNotNone(initial_status, "Controller status should be available")
        self.assertIn("target_position", initial_status, "Status should contain target position")
        self.assertIn("end_effector_position", initial_status, "Status should contain end effector position")
        self.assertIn("distance_to_target", initial_status, "Status should contain distance")
        self.assertIn("target_reached", initial_status, "Status should contain target reached status")
        self.assertIn("is_following", initial_status, "Status should contain following status")
        self.assertIn("ik_method", initial_status, "Status should contain IK method")

        # Test status update button
        self.ui_template._on_update_status()

        # Verify status elements exist and are updated
        self.assertIn("Target Position", self.task_ui_elements, "Target Position display should exist")
        self.assertIn("EE Position", self.task_ui_elements, "End Effector Position display should exist")
        self.assertIn("Distance", self.task_ui_elements, "Distance display should exist")
        self.assertIn("Target Reached", self.task_ui_elements, "Target Reached display should exist")

    async def test_follow_target_completion_verification(self):
        """Test that the follow target behavior works correctly and robot responds to target movement."""
        # Load scene and start following
        await self.test_load_button_click()
        # Call the Start Follow Target button's click handler
        self.ui_template._on_follow_target_button_event(True)

        # Get initial positions
        initial_ee_pos = self.sample.controller.get_robot_end_effector_position()
        initial_target_pos = self.sample.controller.get_target_position()
        initial_distance = np.linalg.norm(initial_ee_pos - initial_target_pos)

        print(f"Initial end effector position: {initial_ee_pos}")
        print(f"Initial target position: {initial_target_pos}")
        print(f"Initial distance: {initial_distance:.4f}m")

        # Run simulation for a reasonable number of frames to see if robot moves
        max_frames = 200
        for frame in range(max_frames):
            await get_app().next_update_async()

            # Check if execution is still running
            if not self.sample.is_following():
                print(f"Follow target stopped at frame {frame}")
                break

            # Print progress every 50 frames
            if frame % 50 == 0:
                current_ee_pos = self.sample.controller.get_robot_end_effector_position()
                current_distance = np.linalg.norm(current_ee_pos - initial_target_pos)
                print(f"Frame {frame}: EE pos: {current_ee_pos}, Distance: {current_distance:.4f}m")

            # Verify simulation is still running
            if frame < 150:  # Allow more time for completion
                self.assertTrue(
                    self.sample.is_following() or self._timeline.is_playing(),
                    f"Simulation should still be running at frame {frame}",
                )

        # Verify follow target operation behavior
        if self.sample.is_following():
            print("Follow target is still running - this is expected for continuous following")
        else:
            print("Follow target completed or was stopped")

        # Get final positions
        final_ee_pos = self.sample.controller.get_robot_end_effector_position()
        final_target_pos = self.sample.controller.get_target_position()
        final_distance = np.linalg.norm(final_ee_pos - final_target_pos)

        print(f"Final end effector position: {final_ee_pos}")
        print(f"Final target position: {final_target_pos}")
        print(f"Final distance: {final_distance:.4f}m")

        # Verify that robot and target still exist
        self.assertIsNotNone(self.sample.controller.robot, "Robot should still exist")
        self.assertIsNotNone(self.sample.controller.target_cube, "Target cube should still exist")

        # Verify that positions are valid (not NaN or infinite)
        self.assertTrue(np.all(np.isfinite(final_ee_pos)), "Final end effector position should be finite")
        self.assertTrue(np.all(np.isfinite(final_target_pos)), "Final target position should be finite")
        self.assertTrue(np.isfinite(final_distance), "Final distance should be finite")

        # Verify that robot made some movement (basic sanity check)
        movement_distance = np.linalg.norm(final_ee_pos - initial_ee_pos)
        print(f"Robot movement distance: {movement_distance:.4f}m")

        # Robot should have moved some distance (even if small due to IK constraints)
        self.assertGreater(
            movement_distance,
            0.001,  # At least 1mm of movement
            f"Robot should have moved some distance. Movement: {movement_distance:.6f}m",
        )
