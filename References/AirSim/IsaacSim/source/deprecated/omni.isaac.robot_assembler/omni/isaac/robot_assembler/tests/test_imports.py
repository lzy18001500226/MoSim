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

    async def test_imports_for_omni_isaac_robot_assembler_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import os
        from typing import List

        import carb
        import numpy as np
        from omni.isaac.core.articulations import Articulation
        from omni.isaac.core.prims.xform_prim import XFormPrim
        from omni.isaac.core.utils.prims import get_prim_at_path
        from omni.isaac.core.utils.types import ArticulationAction
        from omni.isaac.core.world import World
        from omni.isaac.nucleus import get_assets_root_path_async
        from omni.isaac.robot_assembler import AssembledRobot, RobotAssembler
        from pxr import PhysxSchema, Sdf, UsdLux, UsdPhysics

        print("All imports successful for extension: omni.isaac.robot_assembler")
