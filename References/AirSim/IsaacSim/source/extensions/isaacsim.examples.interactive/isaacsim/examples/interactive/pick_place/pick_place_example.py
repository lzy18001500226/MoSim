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

"""
Simple Franka Pick-and-Place Interactive Example

This interactive example demonstrates the simplified Franka pick-and-place controller
without complex layers or RL concepts. Users can trigger pick-and-place actions
through the UI.
"""

from isaacsim.examples.interactive.base_sample.base_sample_experimental import BaseSample
from isaacsim.robot.manipulators.examples.franka import FrankaPickPlace


class FrankaPickPlaceInteractive(BaseSample):
    """Interactive sample for simple pick-and-place demonstration."""

    def __init__(self) -> None:
        super().__init__()
        self.controller: FrankaPickPlace = None
        self._is_executing = False

    def get_simulation_context(self):
        """Get the simulation context for physics callbacks."""
        return self._simulation_context

    def setup_scene(self):
        """Set up the scene with robot and cube."""
        # Create controller and setup scene
        self.controller = FrankaPickPlace()
        self.controller.setup_scene()

        print("Scene setup complete with simplified controller")
        return

    async def setup_post_load(self):
        """Called after the scene is loaded."""
        print("Simple pick-place scene loaded successfully")
        return

    async def setup_pre_reset(self):
        """Called before world reset."""
        # Stop any ongoing execution and remove callbacks
        if self._is_executing and self.get_simulation_context():
            self.get_simulation_context().remove_physics_callback("sim_step")

        if self.controller:
            self.controller.reset()
        self._is_executing = False
        return

    async def setup_post_reset(self):
        """Called after world reset."""
        if self.controller:
            # Ensure robot starts in a good position
            self.controller.reset_robot()
        return

    async def setup_post_clear(self):
        """Called after clearing the scene."""
        # Stop any ongoing execution and remove callbacks
        if self._is_executing and self.get_simulation_context():
            self.get_simulation_context().remove_physics_callback("sim_step")

        self.controller = None
        self._is_executing = False
        return

    def simulation_context_cleanup(self):
        """Clean up world resources."""
        # Stop any ongoing execution and remove callbacks
        if self._is_executing and self.get_simulation_context():
            self.get_simulation_context().remove_physics_callback("sim_step")

        self.controller = None
        self._is_executing = False
        return

    def _pick_place_physics_callback(self, dt):
        """Physics callback to execute pick-and-place step by step."""
        if not self._is_executing or self.controller is None:
            return

        if self.controller.is_done():
            print("Pick-and-place completed successfully!")
            self._is_executing = False

            # Remove the physics callback
            if self.get_simulation_context():
                self.get_simulation_context().remove_physics_callback("sim_step")
            return

        # Execute one step of the pick-and-place operation
        try:
            step_executed = self.controller.forward()
            if not step_executed:
                print("Forward step failed!")
                self._is_executing = False
                if self.get_simulation_context():
                    self.get_simulation_context().remove_physics_callback("sim_step")
        except Exception as e:
            print(f"Error during pick-and-place step: {e}")
            self._is_executing = False
            if self.get_simulation_context():
                self.get_simulation_context().remove_physics_callback("sim_step")

    def get_controller_status(self) -> dict:
        """Get current status of the controller."""
        if self.controller:
            return self.controller.get_current_status()
        else:
            return {"error": "Controller not initialized"}

    def is_executing(self) -> bool:
        """Check if pick-and-place is currently executing."""
        return self._is_executing

    # Methods for UI integration
    async def execute_pick_place_async(self):
        """Async wrapper for pick-and-place execution."""
        if self.controller is None:
            print("ERROR: Controller not initialized")
            return False

        if self._is_executing:
            print("Pick-and-place already in progress...")
            return False

        print("Starting pick-and-place execution...")
        self._is_executing = True

        # Reset the robot/controller to ensure clean start
        self.controller.reset()
        print("Robot reset for clean start")

        world = self.get_simulation_context()
        world.add_physics_callback("sim_step", self._pick_place_physics_callback)
        await world.play_async()
        return
