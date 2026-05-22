# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from typing import List

import carb
import numpy as np
import omni
from isaacsim.core.utils.numpy.rotations import quats_to_rot_matrices, rot_matrices_to_quats
from isaacsim.core.utils.prims import get_prim_at_path
from isaacsim.core.utils.xforms import get_world_pose
from pxr import PhysxSchema, Sdf, Usd, UsdPhysics


def move_rb_subframe_to_position(rb_xform_view, rb_subframe, desired_translation, desired_orientation):
    # Get position of rb_xform as `a`
    a_trans, a_orient = rb_xform_view.get_world_poses()
    a_trans = a_trans[0]
    a_orient = a_orient[0]

    # Get the subframe position as `b`
    b_trans, b_orient = get_world_pose(rb_subframe)

    # The goal is to move `a` such that `rb_subframe` ends up at `desired_translation`, `desired_orientation`
    c_trans, c_orient = desired_translation, desired_orientation

    a_rot, b_rot, c_rot = quats_to_rot_matrices(np.vstack([a_orient, b_orient, c_orient]))

    a_rot_cmd = c_rot @ b_rot.T @ a_rot
    a_trans_cmd = c_trans + c_rot @ b_rot.T @ (a_trans - b_trans)

    a_orient_cmd = rot_matrices_to_quats(a_rot_cmd)

    rb_xform_view.set_world_poses(a_trans_cmd[np.newaxis, :], a_orient_cmd[np.newaxis, :])


def show_physics_colliders(show: bool):
    settings = carb.settings.get_settings()
    num = 2 if show else 0
    settings.set_int("/persistent/physics/visualizationDisplayColliders", num)


def unmask_collisions(collision_mask):
    [collision_mask.RemoveTarget(target) for target in collision_mask.GetTargets()]


def mask_collisions(prim_path_a: str, prim_path_b: str) -> Usd.Relationship:
    """Mask collisions between two prims.  All nested prims will also be included.

    Args:
        prim_path_a (str): Path to a prim
        prim_path_b (str): Path to a prim

    Returns:
        Usd.Relationship: A relationship filtering collisions between prim_path_a and prim_path_b
    """
    filteringPairsAPI = UsdPhysics.FilteredPairsAPI.Apply(get_prim_at_path(prim_path_a))
    rel = filteringPairsAPI.CreateFilteredPairsRel()
    rel.AddTarget(Sdf.Path(prim_path_b))
    return rel


def convert_prim_to_collidable_rigid_body(prim_path: str, articulation_paths: List[str]) -> None:
    """Convert a prim to a rigid body by applying the UsdPhysics.RigidBodyAPI
    Also sets physics:kinematicEnabled property to true to prevent falling from gravity without needing a fixed joint.

    Args:
        prim_path (str): Path to prim to convert.
    """
    prim_to_convert = get_prim_at_path(prim_path)
    for art_path in articulation_paths:
        if prim_path[: len(art_path)] == art_path:
            return "Cannot convert a part of an Articulation to Rigid Body"
    if not prim_to_convert.IsValid():
        return f"No prim can be found at path {prim_path}"

    # If the prim path has one or more rigid bodies nested within it, display an error
    for prim in Usd.PrimRange(prim_to_convert):
        path = str(prim.GetPath())
        if path == prim_path:
            continue
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            return (
                "One or more prims nested under the selected path are already Rigid Bodies.  This will cause undefined behavior.  "
                + "Select one of these nested rigid body prims instead."
            )

    # if not prim_to_convert.HasAPI(UsdPhysics.RigidBodyAPI):

    collision_api = UsdPhysics.MeshCollisionAPI.Apply(prim_to_convert)
    collision_api.GetApproximationAttr().Set("convexDecomposition")

    rb_api = PhysxSchema.PhysxRigidBodyAPI.Apply(prim_to_convert)
    rb_api.GetDisableGravityAttr().Set(True)

    UsdPhysics.CollisionAPI.Apply(prim_to_convert)
    UsdPhysics.RigidBodyAPI.Apply(prim_to_convert)


def find_all_articulations():
    art_root_paths = []
    articulation_candidates = set()

    stage = omni.usd.get_context().get_stage()

    if not stage:
        return art_root_paths

    # Find all articulation root paths
    # Find all paths that are the maximal subpath of all prims connected by a fixed joint
    # I.e. a fixed joint connecting /ur10/link1 to /ur10/link0 would result in the path
    # /ur10.  The path /ur10 becomes a candidate Articulation.
    for prim in Usd.PrimRange(stage.GetPrimAtPath("/")):
        if (
            prim.HasAPI(UsdPhysics.ArticulationRootAPI)
            and prim.GetProperty("physxArticulation:articulationEnabled").IsValid()
            and prim.GetProperty("physxArticulation:articulationEnabled").Get()
        ):
            art_root_paths.append(tuple(str(prim.GetPath()).split("/")[1:]))
        elif UsdPhysics.Joint(prim):
            bodies = prim.GetProperty("physics:body0").GetTargets()
            bodies.extend(prim.GetProperty("physics:body1").GetTargets())
            if len(bodies) == 1:
                continue
            base_path_split = str(bodies[0]).split("/")[1:]
            for body in bodies[1:]:
                body_path_split = str(body).split("/")[1:]
                for i in range(len(base_path_split)):
                    if len(body_path_split) < i or base_path_split[i] != body_path_split[i]:
                        base_path_split = base_path_split[:i]
                        break
            articulation_candidates.add(tuple(base_path_split))

    # Only keep candidates whose path is not a subset of another candidate's path
    unique_candidates = []
    for c1 in articulation_candidates:
        is_unique = True
        for c2 in articulation_candidates:
            if c1 == c2:
                continue
            elif c2[: len(c1)] == c1:
                is_unique = False
                break
        if is_unique:
            unique_candidates.append(c1)

    # Only keep candidates that are a subset of exactly one articulation root
    art_base_paths = []
    for c in unique_candidates:
        subset_count = 0
        for root in art_root_paths:
            if root[: len(c)] == c:
                subset_count += 1
        if subset_count == 1:
            art_path = ""
            for s in c:
                art_path += "/" + s
            art_base_paths.append(art_path)

    return art_base_paths


def adjust_text_block_num_lines(text_block):
    characters_per_line = 80.0  # In a TextBlock of default size
    text_block.set_num_lines(int(max(np.ceil(len(text_block.get_text()) / characters_per_line), 1.0)))
