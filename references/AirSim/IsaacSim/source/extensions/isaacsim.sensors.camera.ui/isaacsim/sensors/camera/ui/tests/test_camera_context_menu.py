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
"""
Test file for Camera and Depth sensors added via context menus.
This test file simulates context menu clicks (instead of using main menu clicks)
to create Camera sensors and then verifies that a sensor prim is created on stage.
"""

import asyncio

import carb
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.timeline
import omni.usd
from isaacsim.core.utils.stage import clear_stage, create_new_stage
from omni.ui.tests.test_base import OmniUiTest


class TestCameraContextMenu(OmniUiTest):
    async def setUp(self):
        # Create a new stage for testing.
        result = create_new_stage()
        self.assertTrue(result)
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        # Wait until stage loading finishes if necessary.
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            await omni.kit.app.get_app().next_update_async()
        await super().tearDown()

    async def test_camera_context_menu_count(self):
        """
        Test that all the Camera and Depth Sensor menu items are added correctly.
        Expected items based on extension definition:
            Intel: 1
            Orbbec: 4
            Leopard Imaging: 2
            Sensing: 7
            SICK: 1
            Stereolabs: 1
        Total expected = 16.
        """
        # Open the Stage window context menu with retry mechanism
        max_attempts = 5
        retry_delay = 0.5
        viewport_context_menu = None

        for attempt in range(max_attempts):
            try:
                viewport_window = ui_test.find("Viewport")
                await viewport_window.right_click()
                viewport_context_menu = await ui_test.get_context_menu()
                break  # Success, exit the loop
            except Exception as e:
                if attempt < max_attempts - 1:  # Don't sleep on the last attempt
                    carb.log_warn(f"Attempt {attempt+1} failed to get context menu: {str(e)}. Retrying...")
                    await omni.kit.app.get_app().next_update_async()
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                else:
                    carb.log_error(f"Failed to get context menu after {max_attempts} attempts: {str(e)}")
                    raise  # Re-raise the last exception if all attempts failed

        self.assertIsNotNone(viewport_context_menu, "Failed to get viewport context menu")
        camera_menu_dict = viewport_context_menu["Create"]["Isaac"]["Sensors"]["Camera and Depth Sensors"]

        def count_menu_items(menu_dict):
            count = 0
            for key, item in menu_dict.items():
                if isinstance(item, dict):
                    count += count_menu_items(item)
                else:
                    count += len(item)
            return count

        n_items = count_menu_items(camera_menu_dict)
        expected_items = 1 + 4 + 2 + 7 + 1 + 1  # equal to 16 based on extension definition.
        self.assertEqual(
            n_items,
            expected_items,
            f"The number of items in the Camera and Depth Sensors menu ({n_items}) does not match the expected ({expected_items})",
        )

    async def test_camera_sensors_context_menu_click(self):
        """
        Test the Camera and Depth Sensors are added to stage context menus correctly.
        """

        # find the path to the last layer of the menu by randomly traversing
        def get_all_menu_paths(menu_dict):
            leaf_nodes = []
            stack = [(menu_dict, "")]  # (current_dict, current_path)

            while stack:
                current_dict, current_path = stack.pop()

                for key, value in current_dict.items():
                    if key != "_":
                        new_path = current_path + "/" + key
                    else:
                        new_path = current_path
                    if isinstance(value, dict):
                        stack.append((value, new_path))
                    elif isinstance(value, list):
                        for item in value:
                            leaf_nodes.append(new_path + "/" + item)
            return leaf_nodes

        # Attempt to get the context menu once, to populate the list of menu paths
        max_attempts = 5
        retry_delay = 0.5
        viewport_context_menu = None

        for attempt in range(max_attempts):
            try:
                viewport_window = ui_test.find("Viewport")
                await viewport_window.right_click()
                viewport_context_menu = await ui_test.get_context_menu()
                break  # Success, exit the loop
            except Exception as e:
                if attempt < max_attempts - 1:  # Don't sleep on the last attempt
                    carb.log_warn(f"Attempt {attempt+1} failed to get context menu: {str(e)}. Retrying...")
                    await omni.kit.app.get_app().next_update_async()
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                else:
                    carb.log_error(f"Failed to get context menu after {max_attempts} attempts: {str(e)}")
                    raise  # Re-raise the last exception if all attempts failed

        self.assertIsNotNone(viewport_context_menu, "Failed to get viewport context menu")
        camera_viewport_menu_dict = viewport_context_menu["Create"]["Isaac"]["Sensors"]["Camera and Depth Sensors"]

        # Iterate over all menu paths and test each one
        for test_path in get_all_menu_paths(camera_viewport_menu_dict):
            full_test_path = "Create/Isaac/Sensors/Camera and Depth Sensors" + test_path

            # Attempt to get the context menu again, this time to select the appropriate menu item
            max_attempts = 5
            retry_delay = 0.5
            viewport_context_menu = None

            for attempt in range(max_attempts):
                try:
                    viewport_window = ui_test.find("Viewport")
                    await viewport_window.right_click()
                    viewport_context_menu = await ui_test.get_context_menu()
                    break  # Success, exit the loop
                except Exception as e:
                    if attempt < max_attempts - 1:  # Don't sleep on the last attempt
                        carb.log_warn(f"Attempt {attempt+1} failed to get context menu: {str(e)}. Retrying...")
                        await omni.kit.app.get_app().next_update_async()
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 1.5  # Exponential backoff
                    else:
                        carb.log_error(f"Failed to get context menu after {max_attempts} attempts: {str(e)}")
                        raise  # Re-raise the last exception if all attempts failed

            clear_stage()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            await ui_test.select_context_menu(full_test_path)

            # Wait until stage loading finishes
            while omni.usd.get_context().get_stage_loading_status()[2] > 0:
                await omni.kit.app.get_app().next_update_async()

            # Give one more frame to ensure everything is settled
            for _ in range(50):
                await omni.kit.app.get_app().next_update_async()

            # check if there is more than one Camera prim on stage
            stage = omni.usd.get_context().get_stage()
            prims = stage.TraverseAll()
            n_cameras = 0
            for prim in prims:
                if prim.GetTypeName() == "Camera":
                    n_cameras += 1

            self.assertGreater(
                n_cameras, 1, f"There are {n_cameras} Camera prims on stage for {full_test_path}, expected at least 1."
            )
