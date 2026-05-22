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

    async def test_imports_for_omni_isaac_surface_gripper_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import os

        import carb
        import carb.tokens
        import numpy as np
        import omni.kit.commands
        import omni.kit.usd
        import omni.physics.tensors
        from omni.isaac.core.prims.rigid_prim import RigidPrim
        from omni.isaac.core.utils.physics import simulate_async
        from omni.isaac.surface_gripper import _surface_gripper
        from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdLux, UsdPhysics

        print("All imports successful for extension: omni.isaac.surface_gripper")
