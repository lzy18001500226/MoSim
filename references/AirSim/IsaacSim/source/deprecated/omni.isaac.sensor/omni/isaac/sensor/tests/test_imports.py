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

    async def test_imports_for_omni_isaac_sensor_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import math
        import os
        import sys
        from math import floor
        from typing import List

        import carb
        import carb.tokens
        import numpy as np
        import omni
        import omni.graph.action
        import omni.graph.core as og
        import omni.hydratexture
        import omni.isaac.core.utils.numpy.rotations as rot_utils
        import omni.isaac.core.utils.stage as stage_utils
        import omni.isaac.IsaacSensorSchema as sensorSchema
        import omni.kit
        import omni.kit.commands
        import omni.replicator.core as rep
        import omni.usd
        import torch
        import usdrt.Sdf
        import warp as wp
        from omni.isaac.core import World
        from omni.isaac.core.articulations import Articulation
        from omni.isaac.core.objects import DynamicCuboid, GroundPlane, VisualCuboid
        from omni.isaac.core.objects.ground_plane import GroundPlane
        from omni.isaac.core.prims.rigid_prim import RigidPrim
        from omni.isaac.core.prims.xform_prim import XFormPrim
        from omni.isaac.core.utils.physics import simulate_async
        from omni.isaac.core.utils.prims import add_reference_to_stage, delete_prim, get_prim_at_path
        from omni.isaac.core.utils.rotations import quat_to_euler_angles
        from omni.isaac.core.utils.semantics import add_update_semantics
        from omni.isaac.core.utils.stage import add_reference_to_stage, create_new_stage_async, update_stage_async
        from omni.isaac.nucleus import get_assets_root_path, get_assets_root_path_async
        from omni.isaac.sensor import (
            Camera,
            CameraView,
            ContactSensor,
            IMUSensor,
            LidarRtx,
            RotatingLidarPhysX,
            _sensor,
        )
        from omni.isaac.sensor.scripts.effort_sensor import EffortSensor, EsSensorReading
        from omni.kit.viewport.utility import get_active_viewport
        from omni.physx.scripts import physicsUtils
        from PIL import Image
        from pxr import Gf, PhysicsSchemaTools, PhysxSchema, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics

        print("All imports successful for extension: omni.isaac.sensor")
