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

    async def test_imports_for_omni_isaac_ros2_bridge_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import copy
        import gc
        import json
        import math
        import random
        import sys
        import time
        from collections import deque
        from copy import deepcopy
        from re import A, I

        import builtin_interfaces.msg
        import carb
        import carb.tokens
        import cv2
        import isaac_ros2_messages.srv
        import numpy as np
        import omni
        import omni.graph.core as og
        import omni.graph.core.tests as ogts
        import omni.kit
        import omni.kit.commands
        import omni.kit.usd
        import omni.kit.viewport.utility
        import omni.replicator.core as rep
        import omni.usd
        import rclpy
        import std_msgs.msg

        # import trajectory_msgs.msg
        import usdrt.Sdf

        # from ackermann_msgs.msg import AckermannDriveStamped
        from builtin_interfaces.msg import Time

        # from cv_bridge.boost.cv_bridge_boost import CV_MAT_CNWrap, CV_MAT_DEPTHWrap, getCvType
        # from geometry_msgs.msg import TransformStamped, Twist
        # from nav_msgs.msg import Odometry
        from omni.isaac.benchmark.services.utils import wait_until_stage_is_fully_loaded_async
        from omni.isaac.core.articulations import Articulation
        from omni.isaac.core.objects import DynamicCuboid, VisualCuboid
        from omni.isaac.core.prims.xform_prim import XFormPrim
        from omni.isaac.core.utils.physics import simulate_async
        from omni.isaac.core.utils.semantics import add_update_semantics
        from omni.isaac.core.utils.stage import (
            add_reference_to_stage,
            create_new_stage_async,
            get_current_stage,
            open_stage_async,
        )
        from omni.isaac.core.utils.viewports import add_aov_to_viewport, set_camera_view
        from omni.isaac.core.utils.xforms import get_world_pose
        from omni.isaac.core_nodes.scripts.utils import set_target_prims
        from omni.isaac.nucleus import get_assets_root_path_async
        from omni.isaac.sensor import Camera, _sensor
        from omni.kit.viewport.utility import get_active_viewport
        from omni.syntheticdata import sensors
        from pxr import Gf, PhysicsSchemaTools, PhysxSchema, Sdf, Tf, Usd, UsdGeom, UsdLux, UsdPhysics

        # from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
        # from rosgraph_msgs.msg import Clock
        # from sensor_msgs.msg import CameraInfo, Image, JointState, LaserScan, PointCloud2, PointField
        # from std_msgs.msg import String
        # from tf2_msgs.msg import TFMessage
        # from usd.schema.isaac import ISAAC_NAME_OVERRIDE
        # from vision_msgs.msg import Detection2DArray, Detection3DArray
        from .common import (
            add_carter,
            add_carter_ros,
            add_cube,
            add_franka,
            add_nova_carter_ros,
            fields_to_dtype,
            get_qos_profile,
            set_joint_drive_parameters,
            set_rotate,
            set_translate,
        )

        print("All imports successful for extension: omni.isaac.ros2_bridge")
