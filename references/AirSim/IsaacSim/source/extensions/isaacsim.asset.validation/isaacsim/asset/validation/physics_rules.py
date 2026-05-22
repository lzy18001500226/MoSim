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
import typing

import carb
import omni.asset_validator.core as av_core
import usdrt
from omni.asset_validator.core import registerRule
from omni.physx import get_physx_simulation_interface
from omni.physx.bindings._physx import SETTING_UPDATE_TO_USD, ContactEventType, SimulationEvent
from pxr import Gf, PhysicsSchemaTools, PhysxSchema, Sdf, Usd, UsdGeom, UsdPhysics, UsdUtils

# from omni.physx.scripts.physicsUtils import get_initial_collider_pairs # ideally, import Ales's code here, blocked atm


@registerRule("IsaacSim.PhysicsRules")
class RigidBodyHasMassAPI(av_core.BaseRuleChecker):
    """Validates that rigid bodies have properly configured mass properties.

    This rule checks that prims with the RigidBodyAPI also have the MassAPI applied
    with properly defined mass, diagonal inertia, and principal axes attributes.
    """

    def check_rigid_body_prim(self, prim: Usd.Prim) -> None:
        """Check if a rigid body prim has proper mass configuration.

        Args:
            prim: The rigid body prim to validate.
        """
        # Has Rigid body API, now check if it has MassAPI
        if not prim.HasAPI(UsdPhysics.MassAPI):
            self._AddError(message=f"Rigid body {prim.GetPath()} has rigid body api but no mass api", at=prim)

        # check if mass attr is authored
        if not prim.HasAttribute("physics:mass"):
            self._AddError(message=f"Rigid body {prim.GetPath()} has mass api but no mass attr", at=prim)

        # check if mass attr is not 0
        if prim.GetAttribute("physics:mass").Get() == 0:
            self._AddInfo(message=f"Rigid body {prim.GetPath()} has mass of 0", at=prim)

        # check if diagonal inertia is authored
        if not prim.HasAttribute("physics:diagonalInertia"):
            self._AddError(message=f"Rigid body {prim.GetPath()} has mass api but no diagonal inertia attr", at=prim)

        # check if diagonal inertia is non-zero
        diagonal_inertia = prim.GetAttribute("physics:diagonalInertia").Get()
        if diagonal_inertia == Gf.Vec3f(0, 0, 0):
            self._AddInfo(message=f"Rigid body {prim.GetPath()} has diagonal inertia of [0, 0, 0]", at=prim)
        else:
            # check triangle inequality: I1 + I2 >= I3, I1 + I3 >= I2, I2 + I3 >= I1
            i1, i2, i3 = diagonal_inertia[0], diagonal_inertia[1], diagonal_inertia[2]
            if i1 + i2 < i3:
                self._AddError(
                    message=f"Rigid body {prim.GetPath()} violates inertia triangle inequality: I1 + I2 ({i1 + i2}) < I3 ({i3})",
                    at=prim,
                )
            if i1 + i3 < i2:
                self._AddError(
                    message=f"Rigid body {prim.GetPath()} violates inertia triangle inequality: I1 + I3 ({i1 + i3}) < I2 ({i2})",
                    at=prim,
                )
            if i2 + i3 < i1:
                self._AddError(
                    message=f"Rigid body {prim.GetPath()} violates inertia triangle inequality: I2 + I3 ({i2 + i3}) < I1 ({i1})",
                    at=prim,
                )

        # check if principal axes is authored
        if not prim.HasAttribute("physics:principalAxes"):
            self._AddError(message=f"Rigid body {prim.GetPath()} has mass api but no principal axes attr", at=prim)

        # check if principal axes == quatf(1, 0, 0, 0)
        if abs(prim.GetAttribute("physics:principalAxes").Get().GetLength() - 1.0) > 1e-4:
            self._AddError(
                message=f"Rigid body {prim.GetPath()}'s principal axes is not normalized, but: {prim.GetAttribute('physics:principalAxes').Get().GetLength()}",
                at=prim,
            )

    def CheckStage(self, stage: Usd.Stage) -> None:
        """Check all rigid bodies in the stage for proper mass configuration.

        Args:
            stage: The USD stage to validate.
        """
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                self.check_rigid_body_prim(prim)


@registerRule("IsaacSim.PhysicsRules")
class RigidBodyHasCollider(av_core.BaseRuleChecker):
    """Validates that enabled rigid bodies have collision geometry.

    This rule checks that prims with an enabled RigidBodyAPI also have the CollisionAPI
    applied, which is required for collision detection in physics simulation.
    """

    def CheckPrim(self, prim: Usd.Prim) -> None:
        """Check if an enabled rigid body has collision geometry.

        Args:
            prim: The USD prim to validate.
        """
        rigid_body_api = UsdPhysics.RigidBodyAPI(prim)
        if not rigid_body_api:
            return
        else:
            # check if the rigid body api is enabled
            if not rigid_body_api.GetRigidBodyEnabledAttr().Get():
                return
            for p in Usd.PrimRange(prim, Usd.TraverseInstanceProxies()):
                if p.HasAPI(UsdPhysics.CollisionAPI):
                    return
            self._AddError(message=f"Rigid body {prim.GetPath()} has rigid body api but no collision api", at=prim)


def ComputeAdjacentMeshDict(stage: Usd.Stage) -> dict:
    """Compute a dictionary mapping body paths to lists of adjacent body paths.

    Args:
        stage: The USD stage to analyze.

    Returns:
        A dictionary mapping body paths to lists of adjacent body paths.
    """
    # Traverse through the joints, log every pair of connected bodies
    defaultPrim = stage.GetDefaultPrim()
    if not defaultPrim or not defaultPrim.IsValid():
        return {}

    adjacent_mesh_matrix = {}

    for prim in stage.Traverse():
        if prim.HasAPI(PhysxSchema.PhysxJointAPI):
            joint = UsdPhysics.Joint(prim)
            body0_targets = joint.GetBody0Rel().GetTargets()
            if not body0_targets:
                continue
            body0 = body0_targets[0]
            body1_targets = joint.GetBody1Rel().GetTargets()
            if not body1_targets:
                continue
            body1 = body1_targets[0]

            # body0 and body1 are adjacent, log into joint dict
            if body0 not in adjacent_mesh_matrix:
                adjacent_mesh_matrix[body0] = []
            if body1 not in adjacent_mesh_matrix:
                adjacent_mesh_matrix[body1] = []
            adjacent_mesh_matrix[body0].append(body1)
            adjacent_mesh_matrix[body1].append(body0)

    return adjacent_mesh_matrix


# Copied from Ales's code
def get_initial_collider_pairs(stage: Usd.Stage) -> typing.Set[typing.Tuple[str, str]]:
    """
    Get all collider pairs that are in contact in the physics simulation.

    This function performs a single physics simulation step and collects all collider pairs
    that are in contact. It temporarily modifies physics settings to ensure accurate contact
    detection and restores them after completion.

    The function:
    1. Creates a temporary session layer for contact reporting
    2. Enables contact reporting for all rigid bodies
    3. Runs a single physics simulation step
    4. Collects all collider pairs that are in contact
    5. Restores original physics settings

    Args:
        stage (Usd.Stage): The USD stage containing the physics scene to analyze.

    Returns:
        typing.Set[typing.Tuple[str, str]]: A set of tuples, where each tuple contains
            the paths of two colliders that are in contact. The paths in each tuple are
            sorted alphabetically to ensure consistent ordering regardless of which collider
            initiated the contact.

    Note:
        This function temporarily modifies physics settings and runs a simulation step.
        The original settings are restored after the function completes.
    """
    unique_collider_pairs = set()  # Use a set to store unique collider pairs
    session_sub_layer = Sdf.Layer.CreateAnonymous()
    stage.GetSessionLayer().subLayerPaths.append(session_sub_layer.identifier)
    old_layer = stage.GetEditTarget().GetLayer()
    stage.SetEditTarget(Usd.EditTarget(session_sub_layer))

    # Added this to avoid stage not in cache error
    stageCache = UsdUtils.StageCache.Get()
    stageCache.Insert(stage)  # Register the stage

    stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
    usdrtStage = usdrt.Usd.Stage.Attach(stage_id)
    prim_paths = usdrtStage.GetPrimsWithAppliedAPIName("PhysicsRigidBodyAPI")

    for prim_path in prim_paths:
        prim = stage.GetPrimAtPath(str(prim_path))
        if prim:
            contact_report_api = PhysxSchema.PhysxContactReportAPI.Apply(prim)
            contact_report_api.CreateThresholdAttr().Set(0)

    settings = carb.settings.get_settings()
    write_usd = settings.get_as_bool(SETTING_UPDATE_TO_USD)
    write_fabric = settings.get_as_bool("/physics/fabricEnabled")

    settings.set(SETTING_UPDATE_TO_USD, False)
    settings.set("/physics/fabricEnabled", False)

    initial_attach = False
    if get_physx_simulation_interface().get_attached_stage() != stage_id:
        get_physx_simulation_interface().attach_stage(stage_id)
        initial_attach = True

    get_physx_simulation_interface().simulate(1.0 / 60.0, 0.0)
    get_physx_simulation_interface().fetch_results()

    contact_headers, contact_data = get_physx_simulation_interface().get_contact_report()
    if len(contact_headers) > 0:
        for contact_header in contact_headers:
            if contact_header.type == ContactEventType.CONTACT_FOUND:
                collider0 = str(PhysicsSchemaTools.intToSdfPath(contact_header.collider0))
                collider1 = str(PhysicsSchemaTools.intToSdfPath(contact_header.collider1))
                # Store as a tuple, ensuring consistent ordering
                pair = tuple(sorted([collider0, collider1]))
                unique_collider_pairs.add(pair)

    if initial_attach:
        get_physx_simulation_interface().detach_stage()

    settings.set(SETTING_UPDATE_TO_USD, write_usd)
    settings.set("/physics/fabricEnabled", write_fabric)

    stage.SetEditTarget(old_layer)

    stage.GetSessionLayer().subLayerPaths.remove(session_sub_layer.identifier)
    session_sub_layer = None

    return unique_collider_pairs


@registerRule("IsaacSim.PhysicsRules")
class NonAdjacentCollisionMeshesDoNotClash(av_core.BaseRuleChecker):
    """Validates that non-adjacent collision meshes don't intersect.

    This rule checks that collision meshes that aren't connected by joints don't
    intersect each other, which can cause unstable physics simulation.
    """

    def CheckStage(self, stage: Usd.Stage) -> None:
        """Check for intersecting non-adjacent collision meshes.

        Args:
            stage: The USD stage to validate.
        """
        self.adjacent_mesh_matrix = ComputeAdjacentMeshDict(stage)  # Sdf Path of all joints
        self.collisions_pairs = get_initial_collider_pairs(
            stage
        )  # Set of tuples of collider pairs in contact (Sdf Paths)

        for collision_pair in self.collisions_pairs:
            body0_prim = stage.GetPrimAtPath(collision_pair[0])
            body1_prim = stage.GetPrimAtPath(collision_pair[1])

            body0_parent_path = body0_prim.GetParent().GetPath()
            body1_parent_path = body1_prim.GetParent().GetPath()

            # check if the two bodies are adjacent
            if body1_parent_path in self.adjacent_mesh_matrix.get(body0_parent_path, []):
                continue
            else:
                self._AddError(
                    message=f"Colliding meshes {body0_prim.GetPath()} and {body1_prim.GetPath()} are not adjacent",
                    at=body0_prim,
                )


@registerRule("IsaacSim.PhysicsRules")
class InvisibleCollisionMeshHasPurposeGuide(av_core.BaseRuleChecker):
    """Validates that invisible collision meshes have purpose set to 'guide'.

    This rule checks that collision meshes with visibility set to 'invisible'
    have their purpose set to 'guide', following USD best practices.
    """

    def CheckPrim(self, prim: Usd.Prim) -> None:
        """Check if invisible collision meshes have proper purpose setting.

        Args:
            prim: The USD prim to validate.
        """
        if not prim.HasAPI(UsdPhysics.CollisionAPI):
            return
        prim_imageable = UsdGeom.Imageable(prim)
        prim_visibility = prim_imageable.ComputeVisibility()

        match prim_visibility:
            case UsdGeom.Tokens.inherited:
                return
            case UsdGeom.Tokens.invisible:
                prim_purpose = prim_imageable.GetPurposeAttr().Get()
                if prim_purpose != UsdGeom.Tokens.guide:
                    self._AddWarning(
                        message=f"Invisible collision mesh {prim.GetPath()} purpose: [{prim_purpose}], not [guide]",
                        at=prim,
                    )
                return
            case _:
                return


@registerRule("IsaacSim.PhysicsRules")
class HasArticulationRoot(av_core.BaseRuleChecker):
    """Validates that at least one prim in the stage has the ArticulationRootAPI.

    This rule checks that the USD stage contains at least one prim with the
    UsdPhysics.ArticulationRootAPI applied. The ArticulationRootAPI is required for
    proper articulation simulation in physics.
    """

    def CheckStage(self, stage: Usd.Stage) -> None:
        """Check if the stage has at least one articulation root.

        Args:
            stage: The USD stage to validate.
        """
        roots = []
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
                roots.append(prim)
        if len(roots) == 0:
            self._AddError(
                message=f"Articulation Root API is not set on any prim in the stage",
                at=stage,
            )
