# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test
import omni.usd
from isaacsim.core.utils.stage import create_new_stage, traverse_stage
from omni.kit.mainwindow import get_main_window
from omni.kit.ui_test.menu import *
from omni.kit.ui_test.query import *
from omni.ui.tests.test_base import OmniUiTest


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
# OmniUiTest is derived from omni.kit.test.AsyncTestCase
class TestMenuAssets(OmniUiTest):
    # Before running each test
    async def setUp(self):
        self._timeline = omni.timeline.get_timeline_interface()
        result = create_new_stage()
        # Make sure the stage loaded
        self.assertTrue(result)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        pass

    # After running each test
    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        # In some cases the test will end before the asset is loaded, in this case wait for assets to load
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            await omni.kit.app.get_app().next_update_async()
        await super().tearDown()
        pass


# Find all RTX sensor creation menu items and dynamically add test methods to the TestMenuAssets class
window = get_main_window()
menu_dict = asyncio.run(get_context_menu(window._ui_main_window.main_menu_bar, get_all=False))
sensor_menu_dict = menu_dict["Create"]["Sensors"]["RTX Lidar"]
sensor_root_path = "Create/Sensors/RTX Lidar"


def get_menu_path(d, path, result, root_path):
    for key, value in d.items():
        if key != "_":
            new_path = path + "/" + str(key)
        if isinstance(value, dict):
            get_menu_path(value, new_path, result, root_path)
        elif isinstance(value, str):
            result.append(root_path + path + "/" + str(value))
        elif isinstance(value, list):
            for sensor in value:
                result.append(root_path + path + "/" + str(sensor))
    return result


empty_list = []
skip_list = [
    "Create/Sensors/Asset Browser",
]

empty_path = ""
sensor_menu_list = get_menu_path(sensor_menu_dict, empty_path, empty_list, sensor_root_path)


def _create_test_for_menu_option(test_path):
    """Create a test function for a specific menu option"""

    async def test_function(self):
        delays = [5, 50, 100]
        for delay in delays:
            try:
                await menu_click(test_path, human_delay_speed=delay)
                break
            except AttributeError as e:
                if "NoneType' object has no attribute 'center'" in str(e) and delay != delays[-1]:
                    continue
                raise
        self._timeline.play()
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()
        num_prims = 0
        sensor_passed = False

        # count the number of prims on the stage, should be greater than 1
        # also for each prim, look for the matching type of sensor
        for prim in traverse_stage():
            num_prims += 1
            if prim.IsA("OmniLidar"):
                sensor_passed = True
                break

        self._timeline.stop()
        self.assertGreater(num_prims, 0, f"No prims added to stage.")
        self.assertTrue(sensor_passed, f"{test_path} did not pass, missing prim or wrong prim type")

    # Set proper function name and docstring
    test_name = test_path.replace("/", "_").replace(" ", "_")
    test_function.__name__ = f"test_reference_{test_name}"
    test_function.__doc__ = f"Test adding {test_path} as a reference"

    return test_function


if len(sensor_menu_list) == 0:
    # Add a test that will fail with a useful message
    async def test_no_menu_items_found(self):
        self.fail(f"No menu items found in {sensor_root_path}")

    setattr(TestMenuAssets, "test_no_menu_items_found", test_no_menu_items_found)
else:
    for test_path in sensor_menu_list:
        test_func = _create_test_for_menu_option(test_path)
        setattr(TestMenuAssets, test_func.__name__, test_func)
