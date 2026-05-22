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
import omni.ui as ui
import omni.usd
from isaacsim.core.experimental.utils.stage import create_new_stage_async
from isaacsim.examples.interactive.pick_place.pick_place_example import FrankaPickPlaceInteractive
from isaacsim.examples.interactive.pick_place.pick_place_example_extension import FrankaPickPlaceUI
from omni.kit.app import get_app


class TestPickPlace(omni.kit.test.AsyncTestCase):
    """Test suite for the Franka Pick-and-Place interactive example.

    This test suite verifies:
    1. UI button interactions (Load, Reset, Start Pick Place)
    2. Simulation execution for specified number of frames
    """

    async def setUp(self):
        """Set up test environment before each test."""
        await create_new_stage_async()

        await get_app().next_update_async()

        # Initialize timeline
        self._timeline = omni.timeline.get_timeline_interface()

        self.sample = FrankaPickPlaceInteractive()
        await self.sample.load_world_async()

        # Initialize UI template
        self.ui_template = FrankaPickPlaceUI(
            ext_id="test_ext",
            file_path="test_path",
            title="Test Pick Place",
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
        if "Start Pick Place" in self.task_ui_elements:
            self.task_ui_elements["Start Pick Place"].enabled = False
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
        self.assertTrue(self.sample.controller.cube is not None, "Cube should be initialized after load")

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

        # Verify UI state after load
        self.assertTrue(
            self.task_ui_elements["Start Pick Place"].enabled, "Start Pick Place button should be enabled after load"
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

        # Get initial robot and cube positions
        initial_robot_pos = self.sample.controller.robot.get_dof_positions().numpy()
        initial_cube_pos = self.sample.controller.cube.get_world_poses()[0].numpy()
        # Move robot and cube to different positions
        self.sample.controller.robot.set_dof_positions(np.array([[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0, 0.0]]))
        self.sample.controller.cube.set_world_poses(
            positions=np.array([[0.6, 0.1, 0.1]]), orientations=np.array([[1.0, 0.0, 0.0, 0.0]])
        )

        self.ui_template._on_reset()

        sim_context.play()
        await asyncio.sleep(0.5)

        current_robot_pos = self.sample.controller.robot.get_dof_positions().numpy()
        current_cube_pos = self.sample.controller.cube.get_world_poses()[0].numpy()

        np.testing.assert_array_almost_equal(current_robot_pos, initial_robot_pos, decimal=2)
        np.testing.assert_array_almost_equal(current_cube_pos, initial_cube_pos, decimal=2)

        # Verify prims still exist in stage after reset
        stage = omni.usd.get_context().get_stage()

        # Verify robot prim still exists and is valid
        robot_prim = stage.GetPrimAtPath("/World/robot")
        self.assertIsNotNone(robot_prim, "Robot prim should still exist in stage after reset")
        self.assertTrue(robot_prim.IsValid(), "Robot prim should still be valid after reset")

        # Verify cube prim still exists and is valid
        cube_prim = stage.GetPrimAtPath("/World/Cube")
        self.assertIsNotNone(cube_prim, "Cube prim should still exist in stage after reset")
        self.assertTrue(cube_prim.IsValid(), "Cube prim should still be valid after reset")

        # Verify UI state after reset
        self.assertTrue(
            self.task_ui_elements["Start Pick Place"].enabled, "Start Pick Place button should be enabled after reset"
        )
        self.assertEqual(self.task_ui_elements["Status"].text, "Ready")

    async def test_start_pick_place_button_click(self):
        """Test that the Start Pick Place button initiates the pick-and-place sequence."""
        # First load the scene
        await self.test_load_button_click()

        # Verify initial state
        self.assertFalse(self.sample.is_executing(), "Should not be executing initially")
        self.assertTrue(self.task_ui_elements["Start Pick Place"].enabled, "Button should be enabled")

        # Call the Start Pick Place button's click handler
        self.ui_template._on_pick_place_button_event()
        await get_app().next_update_async()

        # Verify execution started
        self.assertTrue(self.sample.is_executing(), "Should be executing after function call")
        self.assertFalse(
            self.task_ui_elements["Start Pick Place"].enabled, "Button should be disabled during execution"
        )

        # Verify timeline is playing
        self.assertTrue(self._timeline.is_playing(), "Timeline should be playing during execution")

    async def test_simulation_execution_50_frames(self):
        """Test running the simulation for 50 frames and verify state."""
        # Load scene and start pick-and-place
        await self.test_load_button_click()
        await self.test_start_pick_place_button_click()

        # Run simulation for 50 frames
        for frame in range(50):
            await get_app().next_update_async()

            # Verify simulation is still running
            if frame < 40:  # Allow some time for completion
                self.assertTrue(
                    self.sample.is_executing() or self._timeline.is_playing(),
                    f"Simulation should still be running at frame {frame}",
                )

        # Verify final state
        self.assertIsNotNone(self.sample.controller, "Controller should still exist")
        self.assertIsNotNone(self.sample.controller.robot, "Robot should still exist")
        self.assertIsNotNone(self.sample.controller.cube, "Cube should still exist")

    async def test_pick_place_completion_verification(self):
        """Test that the pick-and-place operation completes successfully and cube reaches target position."""
        # Load scene and start pick-and-place
        await self.test_load_button_click()
        await self.test_start_pick_place_button_click()

        # Get the target position from the controller
        target_position = self.sample.controller.target_position
        self.assertIsNotNone(target_position, "Target position should be set in controller")

        # Run simulation until completion or timeout
        max_frames = 500  # Increased timeout for full pick-and-place operation
        for frame in range(max_frames):
            await get_app().next_update_async()

            # Check if execution is complete
            if not self.sample.is_executing():
                print(f"Pick-and-place completed at frame {frame}")
                break

            # Print progress every 50 frames
            if frame % 50 == 0:
                print(f"Frame {frame}: Still executing...")

            # Verify simulation is still running
            if frame < 400:  # Allow more time for completion
                self.assertTrue(
                    self.sample.is_executing() or self._timeline.is_playing(),
                    f"Simulation should still be running at frame {frame}",
                )

        # Verify pick-and-place operation completed
        if self.sample.is_executing():
            self.fail(
                f"Pick-and-place operation did not complete within {max_frames} frames. Operation may be stuck or taking longer than expected."
            )

        self.assertFalse(self.sample.is_executing(), "Pick-and-place operation should be complete")

        # Get final cube position
        final_cube_position = self.sample.controller.cube.get_world_poses()[0].numpy()

        # Check if cube position matches target position in X,Y plane only (ignore Z height)
        xy_tolerance = 0.05  # 5cm tolerance for X,Y position matching
        xy_difference = np.linalg.norm(final_cube_position[0, :2] - target_position[:2])

        self.assertLess(
            xy_difference,
            xy_tolerance,
            f"Cube should be at target X,Y position. Current: [{final_cube_position[0,0]:.4f}, {final_cube_position[0,1]:.4f}], Target: [{target_position[0]:.4f}, {target_position[1]:.4f}], X,Y Difference: {xy_difference:.4f}",
        )
