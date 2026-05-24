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

    async def test_imports_for_omni_isaac_core_extension(self):
        # Testing all imports from original extension tests
        import asyncio
        import unittest

        import carb
        import numpy as np
        import omni
        import omni.isaac.core.utils.deformable_mesh_utils as DeformableMeshUtils
        import omni.isaac.core.utils.numpy.rotations as rotation_conversions
        import omni.kit.commands
        import omni.physx as _physx
        import omni.replicator.core as rep
        import torch
        import warp as wp
        from omni.isaac.cloner import GridCloner
        from omni.isaac.core import SimulationContext, World
        from omni.isaac.core.articulations import Articulation, ArticulationView
        from omni.isaac.core.materials.deformable_material import DeformableMaterial
        from omni.isaac.core.materials.deformable_material_view import DeformableMaterialView
        from omni.isaac.core.materials.particle_material import ParticleMaterial
        from omni.isaac.core.materials.particle_material_view import ParticleMaterialView
        from omni.isaac.core.materials.physics_material import PhysicsMaterial
        from omni.isaac.core.objects import DynamicCuboid, VisualCuboid
        from omni.isaac.core.prims.geometry_prim import GeometryPrim
        from omni.isaac.core.prims.geometry_prim_view import GeometryPrimView
        from omni.isaac.core.prims.rigid_prim import RigidPrim
        from omni.isaac.core.prims.rigid_prim_view import RigidPrimView
        from omni.isaac.core.prims.sdf_shape_view import SdfShapeView
        from omni.isaac.core.prims.soft.cloth_prim import ClothPrim
        from omni.isaac.core.prims.soft.cloth_prim_view import ClothPrimView
        from omni.isaac.core.prims.soft.deformable_prim import DeformablePrim
        from omni.isaac.core.prims.soft.deformable_prim_view import DeformablePrimView
        from omni.isaac.core.prims.soft.particle_system import ParticleSystem
        from omni.isaac.core.prims.soft.particle_system_view import ParticleSystemView
        from omni.isaac.core.prims.xform_prim import XFormPrim
        from omni.isaac.core.prims.xform_prim_view import XFormPrimView
        from omni.isaac.core.robots import Robot
        from omni.isaac.core.utils.distance_metrics import (
            rotational_distance_angle,
            rotational_distance_identity_matrix_deviation,
            rotational_distance_single_axis,
            weighted_translational_distance,
        )
        from omni.isaac.core.utils.numpy.rotations import euler_angles_to_quats
        from omni.isaac.core.utils.physics import get_rigid_body_enabled, set_rigid_body_enabled
        from omni.isaac.core.utils.prims import (
            create_prim,
            define_prim,
            find_matching_prim_paths,
            get_all_matching_child_prims,
            get_articulation_root_api_prim_path,
            get_prim_at_path,
            get_prim_object_type,
            get_prim_path,
            is_prim_non_root_articulation_link,
            is_prim_path_valid,
        )
        from omni.isaac.core.utils.render_product import (
            add_aov,
            create_hydra_texture,
            get_camera_prim_path,
            get_resolution,
            set_camera_prim_path,
            set_resolution,
        )
        from omni.isaac.core.utils.rotations import euler_angles_to_quat
        from omni.isaac.core.utils.stage import (
            add_reference_to_stage,
            clear_stage,
            create_new_stage_async,
            get_current_stage,
            get_stage_units,
            open_stage_async,
            set_stage_units,
            update_stage_async,
        )
        from omni.isaac.core.utils.torch.rotations import euler_angles_to_quats
        from omni.isaac.core.utils.types import ArticulationAction, DynamicsViewState
        from omni.isaac.nucleus import get_assets_root_path_async
        from omni.isaac.sensor import Camera
        from omni.kit.viewport.utility import create_viewport_window
        from omni.physx.scripts import deformableUtils, physicsUtils
        from pxr import Gf, PhysxSchema, Sdf, Usd, UsdGeom, UsdPhysics
        from scipy.spatial.transform import Rotation

        print("All imports successful for extension: omni.isaac.core")
