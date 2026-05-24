# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from pathlib import Path

import carb
import isaacsim.app.about
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest


class TestAboutWindow(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        EXTENSION_FOLDER_PATH = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        )
        TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_about_ui(self):
        class FakePluginImpl:
            def __init__(self, name):
                self.name = name

        class FakePlugin:
            def __init__(self, name):
                self.libPath = "Lib Path " + name
                self.impl = FakePluginImpl("Impl " + name)
                self.interfaces = "Interface " + name

        about = isaacsim.app.about.get_instance()
        about.kit_version = "#Version#"
        about.nucleus_version = "#Nucleus Version#"
        about.client_library_version = "#Client Library Version#"
        about.app_name = "#App Name#"
        about.app_version = "#App Version#"
        about_window = about.menu_show_about(
            [FakePlugin("Test 1"), FakePlugin("Test 2"), FakePlugin("Test 3"), FakePlugin("Test 4")]
        )

        about.get_values()
        try:
            await self.docked_test_window(window=about_window, width=400, height=510)
            await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_about_ui.png")
        except:
            carb.log_warn("Could not run test because carb::windowing is not available")
