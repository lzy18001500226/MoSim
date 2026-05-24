# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import omni.kit.test
from isaacsim.core.api.robots.robot import Robot
from isaacsim.core.api.world import World
from isaacsim.core.utils.stage import add_reference_to_stage, create_new_stage_async, update_stage_async
from isaacsim.storage.native import get_assets_root_path_async


# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of module will
# make it auto-discoverable by omni.kit.test
class TestSimulationContextCrash(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._physics_dt = 1 / 60  # duration of physics frame in seconds

        self._timeline = omni.timeline.get_timeline_interface()

        await create_new_stage_async()
        await update_stage_async()

        pass

    # After running each test
    async def tearDown(self):
        self._timeline.stop()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await update_stage_async()
        World.clear_instance()
        pass

    async def test_simulation_context_crash(self):
        usd_path = await get_assets_root_path_async()
        usd_path += "/Isaac/Robots/Denso/CobottaPro900/cobotta_pro_900.usd"
        robot_prim_path = "/cobotta_pro_900"

        add_reference_to_stage(usd_path, robot_prim_path)

        self._timeline = omni.timeline.get_timeline_interface()

        # Start Simulation and wait
        self._timeline.play()
        await update_stage_async()
        self._robot = Robot(robot_prim_path)
        self._robot.initialize()
        # Initializing World after creating a robot will cause undefined behavior if timeline is playing
        world = World()
        # initializing causes timeline to stop if playing
        await world.initialize_simulation_context_async()
        await update_stage_async()
        self.assertEquals(world.is_playing(), False)
        # Make sure this call doesn't crash due to invalid physx handles
        self._robot.disable_gravity()
