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

    async def test_imports_for_omni_isaac_tests_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import itertools
        import math
        import os
        import random
        import time
        from itertools import chain

        import carb
        import carb.tokens
        import numpy as np
        import omni
        import omni.graph.core as og
        import omni.isaac.core.objects as objects
        import omni.kit.app
        import omni.kit.asset_converter
        import omni.kit.commands
        import omni.physx
        import omni.replicator.core as rep
        import omni.usd

        # import rclpy
        import usdrt.Sdf

        # from ackermann_msgs.msg import AckermannDriveStamped
        from omni.isaac.core import World
        from omni.isaac.core.articulations.articulation import Articulation
        from omni.isaac.core.objects import DynamicCuboid
        from omni.isaac.core.prims import RigidPrim
        from omni.isaac.core.robots.robot import Robot
        from omni.isaac.core.utils.bounds import compute_aabb, compute_obb, create_bbox_cache
        from omni.isaac.core.utils.extensions import get_extension_path_from_name
        from omni.isaac.core.utils.nucleus import get_assets_root_path
        from omni.isaac.core.utils.physics import simulate_async
        from omni.isaac.core.utils.prims import delete_prim, get_prim_at_path
        from omni.isaac.core.utils.rotations import quat_to_euler_angles
        from omni.isaac.core.utils.semantics import add_update_semantics, get_semantics
        from omni.isaac.core.utils.stage import (
            add_reference_to_stage,
            create_new_stage_async,
            open_stage_async,
            update_stage_async,
        )
        from omni.isaac.core.utils.xforms import get_world_pose
        from omni.isaac.core.world import World
        from omni.isaac.nucleus import get_assets_root_path, get_assets_root_path_async
        from omni.physx import get_physx_simulation_interface
        from omni.physx.scripts import utils
        from omni.physx.scripts.physicsUtils import add_ground_plane
        from omni.syntheticdata import helpers
        from omni.usd.commands import DeletePrimsCommand
        from pxr import Gf, PhysicsSchemaTools, PhysxSchema, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics, UsdShade, UsdUtils

        # from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
        # from sensor_msgs.msg import Image
        from .robot_helpers import init_robot_sim, set_physics_frequency, setup_robot_og

        print("All imports successful for extension: omni.isaac.tests")
