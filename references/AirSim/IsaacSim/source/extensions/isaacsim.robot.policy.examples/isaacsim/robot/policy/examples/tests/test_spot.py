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

import asyncio

import carb.tokens
import numpy as np
import omni.kit.commands

# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test
from isaacsim.core.api import World
from isaacsim.core.utils.physics import simulate_async
from isaacsim.core.utils.prims import get_prim_at_path
from isaacsim.core.utils.rotations import quat_to_euler_angles
from isaacsim.core.utils.stage import create_new_stage_async
from isaacsim.robot.policy.examples.robots.spot import SpotFlatTerrainPolicy
from pxr import UsdPhysics


class TestSpot(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        World.clear_instance()
        await create_new_stage_async()
        # This needs to be set so that kit updates match physics updates
        self._physics_rate = 500
        carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", True)
        carb.settings.get_settings().set_int("/app/runLoops/main/rateLimitFrequency", int(self._physics_rate))
        carb.settings.get_settings().set_int("/persistent/simulation/minFrameRate", int(self._physics_rate))

        self._physics_dt = 1 / self._physics_rate
        self._world = World(stage_units_in_meters=1.0, physics_dt=self._physics_dt, rendering_dt=1.0 / 60)
        await self._world.initialize_simulation_context_async()

        ground_prim = get_prim_at_path("/World/defaultGroundPlane")
        # Create the physics ground plane if it hasn't been created
        if not ground_prim.IsValid() or not ground_prim.IsActive():
            self._world.scene.add_default_ground_plane()

        self._base_command = [0, 0, 0]
        self._stage = omni.usd.get_context().get_stage()
        self._timeline = omni.timeline.get_timeline_interface()

    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        self._timeline.stop()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await omni.kit.app.get_app().next_update_async()

    async def test_spot_add(self):
        await self.spawn_spot()
        await omni.kit.app.get_app().next_update_async()

        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._spot.robot.num_dof, 12)
        self.assertTrue(get_prim_at_path("/World/spot").IsValid(), True)
        self.assertTrue(get_prim_at_path("/World/spot").HasAPI(UsdPhysics.ArticulationRootAPI))

    async def test_robot_move_forward_command(self):
        await self.spawn_spot()
        await omni.kit.app.get_app().next_update_async()

        self.start_pos = np.array(self._spot.robot.get_world_pose()[0])
        self._base_command = [2, 0, 0]
        await simulate_async(seconds=1.0)

        self.current_pos = np.array(self._spot.robot.get_world_pose()[0])

        print(str(self.current_pos))
        delta = abs(self.current_pos[0] - self.start_pos[0])

        self.assertGreater(delta, 1.0)
        self.assertLess(delta, 2.0)

    async def test_robot_turn_command(self):
        await self.spawn_spot()
        await omni.kit.app.get_app().next_update_async()

        self.start_orientation = np.array(self._spot.robot.get_world_pose()[1])
        self._base_command = [0, 0, 1]
        await simulate_async(seconds=2.0)

        self.current_orientation = np.array(self._spot.robot.get_world_pose()[1])

        print(str(quat_to_euler_angles(self.start_orientation)))
        print(str(quat_to_euler_angles(self.current_orientation)))
        heading_delta = abs(
            quat_to_euler_angles(self.current_orientation)[2] - quat_to_euler_angles(self.start_orientation)[2]
        )

        # should have turned at least 90 deg
        self.assertGreater(heading_delta, 1.5)

    async def spawn_spot(self, name="spot"):
        self._prim_path = "/World/" + name

        self._spot = SpotFlatTerrainPolicy(prim_path=self._prim_path, name=name, position=np.array([0, 0, 0.7]))
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self._spot.initialize()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        self._world.add_physics_callback("physics_step", callback_fn=self.on_physics_step)
        await omni.kit.app.get_app().next_update_async()

    def on_physics_step(self, step_size):
        if self._spot:
            self._spot.forward(step_size, self._base_command)
