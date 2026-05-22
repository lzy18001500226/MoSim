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
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import open_stage_async
from isaacsim.core.utils.viewports import destroy_all_viewports, get_viewport_names
from isaacsim.storage.native import get_assets_root_path_async


class TestCreateViewport(ogts.OmniGraphTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._timeline = omni.timeline.get_timeline_interface()
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
        # cleanup extra viewports created in test
        destroy_all_viewports(destroy_main_viewport=False)
        await omni.kit.app.get_app().next_update_async()
        # Clean up test
        await omni.kit.stage_templates.new_stage_async()

    # ----------------------------------------------------------------------
    async def test_create_viewport(self):
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnTick", "omni.graph.action.OnTick"),
                    ("createViewport1", "isaacsim.core.nodes.IsaacCreateViewport"),
                    ("createViewport2", "isaacsim.core.nodes.IsaacCreateViewport"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnTick.outputs:tick", "createViewport1.inputs:execIn"),
                    ("OnTick.outputs:tick", "createViewport2.inputs:execIn"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("createViewport1.inputs:viewportId", 0),
                    ("createViewport2.inputs:name", "test name"),
                ],
            },
        )

        # await og.Controller.evaluate(test_graph)
        self.assertEquals(len(get_viewport_names()), 1)
        # check where the joints are after evaluate
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertEquals(len(get_viewport_names()), 2)
