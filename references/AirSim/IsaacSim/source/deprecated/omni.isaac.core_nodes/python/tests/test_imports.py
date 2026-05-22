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

    async def test_imports_for_omni_isaac_core_nodes_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        from re import I

        import carb
        import numpy as np
        import omni.graph.core as og
        import omni.graph.core.tests as ogts
        import omni.replicator.core as rep
        import omni.syntheticdata._syntheticdata as sd
        from omni.isaac.core.objects.ground_plane import GroundPlane
        from omni.isaac.core.robots import Robot
        from omni.isaac.core.utils.physics import simulate_async
        from omni.isaac.core.utils.stage import get_current_stage, open_stage_async
        from omni.isaac.core.utils.viewports import get_viewport_names, set_camera_view
        from omni.isaac.core_nodes import BaseResetNode, BaseWriterNode
        from omni.isaac.nucleus import get_assets_root_path, get_assets_root_path_async
        from omni.kit.viewport.utility import get_active_viewport
        from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics, UsdRender

        print("All imports successful for extension: omni.isaac.core_nodes")
