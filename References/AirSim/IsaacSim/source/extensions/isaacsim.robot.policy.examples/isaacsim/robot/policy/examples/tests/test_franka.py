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
import isaacsim.core.utils.stage as stage_utils
import numpy as np
import omni.kit.commands

# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test
from isaacsim.core.api import World
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.prims import get_prim_at_path
from isaacsim.core.utils.stage import create_new_stage_async
from isaacsim.robot.policy.examples.robots.franka import FrankaOpenDrawerPolicy
from isaacsim.storage.native import get_assets_root_path
from pxr import UsdPhysics


class TestFrankaExampleExtension(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        World.clear_instance()
        await create_new_stage_async()
        # This needs to be set so that kit updates match physics updates
        self._physics_rate = 400
        carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", True)
        carb.settings.get_settings().set_int("/app/runLoops/main/rateLimitFrequency", int(self._physics_rate))
        carb.settings.get_settings().set_int("/persistent/simulation/minFrameRate", int(self._physics_rate))

        self._physics_dt = 1 / self._physics_rate
        self._world = World(stage_units_in_meters=1.0, physics_dt=self._physics_dt, rendering_dt=10 * self._physics_dt)
        await self._world.initialize_simulation_context_async()

        ground_prim = get_prim_at_path("/World/defaultGroundPlane")
        # Create the physics ground plane if it hasn't been created
        if not ground_prim.IsValid() or not ground_prim.IsActive():
            self._world.scene.add_default_ground_plane()

        cabinet_prim_path = "/World/cabinet"
        cabinet_usd_path = get_assets_root_path() + "/Isaac/Props/Sektion_Cabinet/sektion_cabinet_instanceable.usd"

        cabinet_name = "cabinet"
        cabinet_position = np.array([0.8, 0.0, 0.4])
        cabinet_orientation = np.array([0.0, 0.0, 0.0, 1.0])

        stage_utils.add_reference_to_stage(cabinet_usd_path, cabinet_prim_path)

        self.cabinet = SingleArticulation(
            prim_path=cabinet_prim_path, name=cabinet_name, position=cabinet_position, orientation=cabinet_orientation
        )

        self._timeline = omni.timeline.get_timeline_interface()
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        self._timeline.stop()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await omni.kit.app.get_app().next_update_async()

    async def test_franka_add(self):
        await self.spawn_franka()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._franka.robot.num_dof, 9)
        self.assertTrue(get_prim_at_path("/World/franka").IsValid(), True)
        self.assertTrue(get_prim_at_path("/World/cabinet").IsValid(), True)
        self.assertTrue(get_prim_at_path("/World/franka").HasAPI(UsdPhysics.ArticulationRootAPI))
        print("robot articulation passed")

    async def test_franka_open_drawer(self):
        await self.spawn_franka()
        await omni.kit.app.get_app().next_update_async()
        max_drawer_opening = 0
        drawer_link_idx = self.cabinet.get_dof_index("drawer_top_joint")
        for i in range(100):
            # Step the simulation
            await omni.kit.app.get_app().next_update_async()
            drawer_joint_position = self._franka.cabinet.get_joint_positions()[drawer_link_idx]
            if drawer_joint_position > max_drawer_opening:
                max_drawer_opening = drawer_joint_position

        # drawer is closed at 0.0 and open at 0.4, the robot should be able to open the drawer
        # to at least 0.3
        self.assertGreater(max_drawer_opening, 0.3)
        print("robot drawer opening passed, drawer position:", max_drawer_opening)

    async def spawn_franka(self, name="franka"):
        self._prim_path = "/World/" + name

        self._franka = FrankaOpenDrawerPolicy(
            prim_path=self._prim_path, name=name, position=np.array([0, 0, 0]), cabinet=self.cabinet
        )
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self._franka.initialize()
        self._franka.post_reset()
        self._franka.robot.set_joints_default_state(self._franka.default_pos)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        self._world.add_physics_callback("physics_step", callback_fn=self.on_physics_step)
        await omni.kit.app.get_app().next_update_async()

    def on_physics_step(self, step_size):
        if self._franka:
            self._franka.forward(step_size)
