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

import itertools
import os
from os import walk
from pathlib import Path

import carb
import omni.kit.app
from omni.kit import ui_test
from omni.kit.quicklayout import QuickLayout
from omni.kit.test import AsyncTestCase
from omni.ui.workspace_utils import CompareDelegate

EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))


class TestLayoutsExtensions(AsyncTestCase):
    async def setUp(self):
        omni.usd.get_context().new_stage()
        # Make sure the stage loaded
        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        super().tearDown()
        await omni.kit.app.get_app().next_update_async()

    async def test_isaacsim_layouts(self):
        layout_files = []
        ext_path = EXTENSION_FOLDER_PATH
        for dirpath, dirnames, filenames in walk(f"{ext_path}/layouts/"):
            for file in filenames:
                layout_files.append(f"{dirpath}/{file}")

        compare_delegate = CompareDelegate()

        #### test logic:
        # for all the layouts inside the layouts folder, open one after another in all possible combinations
        # compare the layout (opened last) with the json file that the layout is loaded from
        # if they are not the same, print the error
        #####

        for a, b in itertools.combinations(layout_files, 2):
            # for layout in layout_files:
            async def test_layout(layout: str):
                # load layout twice as some don't load fully 1st time
                QuickLayout.load_file(layout, keep_windows_open=False)
                await ui_test.human_delay(50)
                QuickLayout.load_file(layout, keep_windows_open=False)
                await ui_test.human_delay(500)

                compare_errors = QuickLayout.compare_file(layout, compare_delegate)
                if compare_errors:
                    for ce in compare_errors:
                        carb.log_error(f"{os.path.basename(layout)} compare_errors:{ce}")

            await test_layout(a)
            await test_layout(b)
