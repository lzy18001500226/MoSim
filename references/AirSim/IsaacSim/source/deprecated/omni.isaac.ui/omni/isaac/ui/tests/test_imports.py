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

    async def test_imports_for_omni_isaac_ui_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import os

        import carb
        import numpy as np
        import omni.timeline
        import omni.ui as ui
        import pyperclip
        from omni.isaac.core.articulations import Articulation
        from omni.isaac.core.objects.cuboid import FixedCuboid, VisualCuboid
        from omni.isaac.core.utils.prims import delete_prim
        from omni.isaac.core.utils.stage import add_reference_to_stage, create_new_stage, update_stage_async
        from omni.isaac.core.world import World
        from omni.isaac.nucleus import get_assets_root_path
        from omni.isaac.ui import ScreenPrinter
        from omni.isaac.ui.element_wrappers.core_connectors import LoadButton, ResetButton

        print("All imports successful for extension: omni.isaac.ui")
