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

import carb
import omni.kit.test
import omni.usd
from isaacsim.storage.native import get_assets_root_path_async
from omni.isaac.dynamic_control import _dynamic_control
from pxr import Sdf


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestCore(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._dc = _dynamic_control.acquire_dynamic_control_interface()
        self._timeline = omni.timeline.get_timeline_interface()
        await omni.kit.app.get_app().next_update_async()
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        pass

    # After running each test
    async def tearDown(self):
        self._timeline.stop()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await omni.kit.app.get_app().next_update_async()
        pass

    async def test_is_simulating(self):
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(self._dc.is_simulating())
        # Start Simulation and wait
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._dc.is_simulating())
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(self._dc.is_simulating())
        await omni.kit.app.get_app().next_update_async()
        pass

    async def test_print(self):
        t = _dynamic_control.Transform((1, 2, 3), (1, 2, 3, 4))
        v = _dynamic_control.Velocity((1, 2, 3), (4, 5, 6))
        self.assertEqual("(1, 2, 3), (1, 2, 3, 4)", str(t))
        self.assertEqual("(1, 2, 3), (4, 5, 6)", str(v))
        self.assertEqual("(1, 2, 3), (1, 2, 3, 4), (1, 2, 3), (4, 5, 6)", str(_dynamic_control.RigidBodyState(t, v)))
        self.assertEqual("(1, 2, 3)", str(_dynamic_control.DofState(1, 2, 3)))

    async def test_delete(self):

        self._assets_root_path = await get_assets_root_path_async()
        if self._assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
            return

        await omni.kit.app.get_app().next_update_async()
        self._stage = omni.usd.get_context().get_stage()
        await omni.kit.app.get_app().next_update_async()
        prim_a = self._stage.DefinePrim("/World/Franka_1", "Xform")
        prim_a.GetReferences().AddReference(
            self._assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        )
        prim_b = self._stage.DefinePrim("/World/Franka_2", "Xform")
        prim_b.GetReferences().AddReference(
            self._assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        )
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self._handle = self._dc.get_articulation("/World/Franka_1")
        await omni.kit.app.get_app().next_update_async()
        with Sdf.ChangeBlock():
            omni.usd.commands.DeletePrimsCommand(["/World/Franka_1"]).do()
            omni.usd.commands.DeletePrimsCommand(["/World/Franka_2"]).do()
        await omni.kit.app.get_app().next_update_async()
