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

import omni.kit.test


class TestImports(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_imports_for_omni_isaac_menu_extension(self):
        # Testing all imports from original extension tests
        from pathlib import Path

        import carb
        import carb.settings
        import carb.tokens
        import omni.kit.commands
        import omni.usd
        from omni.isaac.core.objects import DynamicCuboid
        from omni.isaac.core.utils.prims import get_prim_path
        from omni.isaac.core.utils.stage import clear_stage, create_new_stage, traverse_stage
        from omni.isaac.core.utils.viewports import set_camera_view
        from omni.isaac.range_sensor import _range_sensor
        from omni.isaac.sensor import _sensor
        from omni.kit.mainwindow import get_main_window
        from pxr import UsdGeom, UsdPhysics

        print("All imports successful for extension: omni.isaac.menu")
