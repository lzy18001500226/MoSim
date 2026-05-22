# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import gc
from abc import abstractmethod

import omni.kit.app
from isaacsim.core.api.simulation_context import SimulationContext
from isaacsim.core.experimental.utils.stage import create_new_stage_async
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.core.utils.viewports import set_camera_view


class BaseSample(object):
    def __init__(self) -> None:
        self._simulation_context = None
        self._world_settings = {"physics_dt": 1.0 / 60.0, "stage_units_in_meters": 1.0, "rendering_dt": 1.0 / 60.0}
        self._logging_info = ""
        return

    def get_simulation_context(self):
        return self._simulation_context

    def set_world_settings(self, physics_dt=None, stage_units_in_meters=None, rendering_dt=None):
        if physics_dt is not None:
            self._world_settings["physics_dt"] = physics_dt
        if stage_units_in_meters is not None:
            self._world_settings["stage_units_in_meters"] = stage_units_in_meters
        if rendering_dt is not None:
            self._world_settings["rendering_dt"] = rendering_dt
        return

    async def load_world_async(self):
        """Function called when clicking load buttton"""
        await create_new_stage_async()

        self.setup_scene()

        # Create SimulationContext directly instead of using singleton
        self._simulation_context = SimulationContext(**self._world_settings)
        await self._simulation_context.initialize_simulation_context_async()

        set_camera_view(eye=[1.5, 1.5, 1.5], target=[0.01, 0.01, 0.01], camera_prim_path="/OmniverseKit_Persp")

        await self._simulation_context.reset_async()
        SimulationManager.initialize_physics()

        await self._simulation_context.pause_async()
        await self.setup_post_load()
        return

    async def reset_async(self):
        """Function called when clicking reset buttton"""
        await self._simulation_context.play_async()
        await omni.kit.app.get_app().next_update_async()
        await self.setup_pre_reset()

        # Use the direct SimulationContext instance and SimulationManager
        await self._simulation_context.reset_async()
        SimulationManager.initialize_physics()

        await self._simulation_context.pause_async()
        await self.setup_post_reset()
        return

    @abstractmethod
    def setup_scene(self) -> None:
        """used to setup anything in the world, adding tasks happen here for instance.

        Args:
            scene (Scene): [description]
        """
        return

    @abstractmethod
    async def setup_post_load(self):
        """called after first reset of the world when pressing load,
        intializing provate variables happen here.
        """
        return

    @abstractmethod
    async def setup_pre_reset(self):
        """called in reset button before resetting the world
        to remove a physics callback for instance or a controller reset
        """
        return

    @abstractmethod
    async def setup_post_reset(self):
        """called in reset button after resetting the world which includes one step with rendering"""
        return

    @abstractmethod
    async def setup_post_clear(self):
        """called after clicking clear button
        or after creating a new stage and clearing the instance of the world with its callbacks
        """
        return

    def log_info(self, info):
        self._logging_info += str(info) + "\n"
        return

    def _simulation_context_cleanup(self):
        if self._simulation_context is not None:
            self._simulation_context.stop()
            self._simulation_context.clear_all_callbacks()
        self.simulation_context_cleanup()
        return

    def simulation_context_cleanup(self):
        """Function called when extension shutdowns and starts again, (hot reloading feature)"""
        return

    async def clear_async(self):
        """Function called when clicking clear buttton"""
        await create_new_stage_async()
        if self._simulation_context is not None:
            self._simulation_context_cleanup()
            self._simulation_context.clear_instance()
            self._simulation_context = None
            gc.collect()
        await self.setup_post_clear()
        return
