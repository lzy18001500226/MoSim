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

    async def test_imports_for_omni_isaac_motion_generation_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import json
        import os

        import carb
        import lula
        import numpy as np
        import omni.isaac.core.objects as objects
        import omni.isaac.motion_generation.interface_config_loader as interface_config_loader
        from omni.isaac.core.objects import FixedCuboid, VisualCuboid
        from omni.isaac.core.objects.cuboid import VisualCuboid
        from omni.isaac.core.objects.ground_plane import GroundPlane
        from omni.isaac.core.prims import XFormPrim
        from omni.isaac.core.prims.xform_prim import XFormPrim
        from omni.isaac.core.robots import Robot
        from omni.isaac.core.robots.robot import Robot
        from omni.isaac.core.utils import distance_metrics
        from omni.isaac.core.utils.numpy.rotations import (
            euler_angles_to_quats,
            quats_to_rot_matrices,
            rot_matrices_to_quats,
            rotvecs_to_quats,
        )
        from omni.isaac.core.utils.prims import delete_prim, is_prim_path_valid
        from omni.isaac.core.utils.rotations import gf_quat_to_np_array, quat_to_rot_matrix
        from omni.isaac.core.utils.types import ArticulationAction
        from omni.isaac.core.utils.viewports import set_camera_view
        from omni.isaac.core.world import World
        from omni.isaac.motion_generation import ArticulationTrajectory
        from omni.isaac.motion_generation.articulation_kinematics_solver import ArticulationKinematicsSolver
        from omni.isaac.motion_generation.articulation_motion_policy import ArticulationMotionPolicy
        from omni.isaac.motion_generation.articulation_trajectory import ArticulationTrajectory
        from omni.isaac.motion_generation.lula.kinematics import LulaKinematicsSolver
        from omni.isaac.motion_generation.lula.motion_policies import RmpFlow
        from omni.isaac.motion_generation.lula.path_planners import RRT
        from omni.isaac.motion_generation.lula.trajectory_generator import LulaCSpaceTrajectoryGenerator
        from omni.isaac.motion_generation.path_planner_visualizer import PathPlannerVisualizer
        from omni.isaac.nucleus import get_assets_root_path_async
        from pxr import Gf, Sdf, UsdLux

        print("All imports successful for extension: omni.isaac.motion_generation")
