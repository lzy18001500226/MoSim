# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

# from omni.kit.test_suite.helpers import StageEventHandler
import omni.kit.ui_test as ui_test
import omni.timeline
import omni.ui as ui


class TestOccupancyMapUI(omni.kit.test.AsyncTestCase):
    async def setup(self):
        # wait for material to be preloaded so create menu is complete & menus don't rebuild during tests
        await omni.kit.material.library.get_mdl_list_async()
        await ui_test.human_delay()

        # TODO: get omni.kit.test_suite.
        # self._stage_event_handler = StageEventHandler("omni.kit.stage_templates")

    async def tearDown(self):
        pass

    async def testLoading(self):
        await omni.usd.get_context().new_stage_async()
        menu_widget = ui_test.get_menubar()
        await menu_widget.find_menu("Tools").click()
        await menu_widget.find_menu("Robotics").click()
        await menu_widget.find_menu("Occupancy Map").click()
