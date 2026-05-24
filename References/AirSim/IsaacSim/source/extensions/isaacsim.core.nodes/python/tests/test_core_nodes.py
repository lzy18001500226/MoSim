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


import carb
import omni.kit.test
from isaacsim.core.nodes.bindings import _isaacsim_core_nodes
from isaacsim.core.utils.stage import open_stage_async
from isaacsim.storage.native import get_assets_root_path_async


class TestCoreNodes(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        self._timeline = omni.timeline.get_timeline_interface()
        self._core_nodes = _isaacsim_core_nodes.acquire_interface()
        # add franka robot for test
        assets_root_path = await get_assets_root_path_async()
        if assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
            return
        (result, error) = await open_stage_async(
            assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        )

    # ----------------------------------------------------------------------
    async def tearDown(self):
        """Get rid of temporary data used by the test"""
        await omni.kit.stage_templates.new_stage_async()

    # ----------------------------------------------------------------------
    async def test_simulation_time(self):
        await omni.kit.app.get_app().next_update_async()
        a = self._core_nodes.get_sim_time()
        b = self._core_nodes.get_sim_time_monotonic()
        c = self._core_nodes.get_system_time()
        await omni.kit.app.get_app().next_update_async()
        a = self._core_nodes.get_sim_time_at_time((0, 1))
        b = self._core_nodes.get_sim_time_monotonic_at_time((0, 1))
        c = self._core_nodes.get_system_time_at_time((0, 1))
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        a = self._core_nodes.get_sim_time()
        b = self._core_nodes.get_sim_time_monotonic()
        c = self._core_nodes.get_system_time()
        a = self._core_nodes.get_sim_time_at_time((0, 0))
        b = self._core_nodes.get_sim_time_monotonic_at_time((0, 0))
        c = self._core_nodes.get_system_time_at_time((0, 0))

    # ----------------------------------------------------------------------
    async def test_physics_num_steps(self):
        carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", True)
        carb.settings.get_settings().set_int("/app/runLoops/main/rateLimitFrequency", 60)
        carb.settings.get_settings().set_int("/persistent/simulation/minFrameRate", 60)
        omni.timeline.get_timeline_interface().set_target_framerate(60)
        omni.timeline.get_timeline_interface().set_time_codes_per_second(60)

        steps = self._core_nodes.get_physics_num_steps()
        self.assertEqual(steps, 0)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        steps = self._core_nodes.get_physics_num_steps()
        self.assertEqual(steps, 3)
        await omni.kit.app.get_app().next_update_async()
        steps = self._core_nodes.get_physics_num_steps()
        self.assertEqual(steps, 4)
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        steps = self._core_nodes.get_physics_num_steps()
        self.assertEqual(steps, 0)
