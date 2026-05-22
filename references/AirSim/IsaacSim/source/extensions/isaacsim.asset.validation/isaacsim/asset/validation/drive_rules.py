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
import math

import omni.asset_validator.core as av_core
from omni.asset_validator.core import registerRule
from pxr import PhysxSchema, Usd, UsdPhysics


def GetJointDrivesAndJointStates(joint):
    """Get the drive APIs and joint state APIs for a joint.

    Args:
        joint: The joint to get drive and state APIs for.

    Returns:
        A tuple of (drive_apis, joint_state_apis) for the joint.
    """
    driveAPIs = []
    joint_states = []
    if joint.IsA(UsdPhysics.RevoluteJoint):
        driveAPIs.append(UsdPhysics.DriveAPI(joint, "angular"))
        joint_states.append(PhysxSchema.JointStateAPI(joint, "angular"))
    elif joint.IsA(UsdPhysics.PrismaticJoint):
        driveAPIs.append(UsdPhysics.DriveAPI(joint, "linear"))
        joint_states.append(PhysxSchema.JointStateAPI(joint, "linear"))
    else:
        axis = [f"{prefix}{i}" for prefix in ["rot", "trans"] for i in ["X", "Y", "Z"]]
        for axis in axis:
            driveAPI = UsdPhysics.DriveAPI(joint, axis)
            joint_state = PhysxSchema.JointStateAPI(joint, axis)
            if driveAPI:
                driveAPIs.append(driveAPI)
                joint_states.append(joint_state)
    return driveAPIs, joint_states


@registerRule("IsaacSim.PhysicsRules")
class PhysicsJointHasDriveOrMimicAPI(av_core.BaseRuleChecker):
    """Validates that joints have a drive or mimic API.

    This rule ensures that all joints (except fixed joints) have either a drive API
    or a mimic API configured. Joints with both APIs are checked to ensure proper
    configuration where drive stiffness and damping are set to 0.0 when mimic is used.
    """

    def CheckPrim(self, prim: Usd.Prim) -> None:
        """Check if a prim has proper drive or mimic API configuration.

        Args:
            prim: The USD prim to validate.
        """
        if not UsdPhysics.Joint(prim) or UsdPhysics.FixedJoint(prim):
            return
        drives, joint_states = GetJointDrivesAndJointStates(prim)
        has_mimic = prim.HasAPI(PhysxSchema.PhysxMimicJointAPI)
        exclude_from_articulation = UsdPhysics.Joint(prim).GetExcludeFromArticulationAttr().Get()
        if not drives and not has_mimic and not exclude_from_articulation:
            self._AddError(message=f"Joint {prim.GetPath()} has no drive or mimic API", at=prim)
        if drives and has_mimic:
            # Check if stiffness and damping are set to 0.0
            for drive in drives:
                stiffness = drive.GetStiffnessAttr().Get()
                damping = drive.GetDampingAttr().Get()
                if (stiffness and stiffness.Get() != 0.0) or (damping and damping.Get() != 0.0):
                    self._AddError(message=f"Joint {prim.GetPath()} has both drive and mimic API", at=prim)


@registerRule("IsaacSim.PhysicsRules")
class PhysicsJointMaxVelocity(av_core.BaseRuleChecker):
    """Validates that joints have a positive max velocity set.

    This rule checks that joints with the PhysxJointAPI have a defined and positive
    max joint velocity, which is required for proper joint simulation.
    """

    def CheckPrim(self, prim: Usd.Prim) -> None:
        """Check if a prim has proper max joint velocity configuration.

        Args:
            prim: The USD prim to validate.
        """
        if prim.HasAPI(PhysxSchema.PhysxJointAPI):
            joint = PhysxSchema.PhysxJointAPI(prim)
            attr = joint.GetMaxJointVelocityAttr()
            if not attr.IsDefined():
                self._AddError(
                    message=f"Max joint velocity is not set on <{prim.GetPath()}>",
                    at=prim,
                )
            else:
                max_joint_velocity = attr.Get()
                if max_joint_velocity <= 0:
                    self._AddError(
                        message=f"Max joint velocity is zero <{attr.GetPath()}>",
                        at=attr,
                    )


@registerRule("IsaacSim.PhysicsRules")
class PhysicsDriveAndJointState(av_core.BaseRuleChecker):
    """Validates that joint drives have proper force limits and matching state values.

    This rule checks that joint drives have defined and reasonable max force values,
    and that drive target positions/velocities match joint state positions/velocities.
    """

    def CheckPrim(self, prim: Usd.Prim) -> None:
        """Check if a prim has proper drive and joint state configuration.

        Args:
            prim: The USD prim to validate.
        """
        drives, joint_states = GetJointDrivesAndJointStates(prim)
        if not drives:
            return
        is_mimic = prim.HasAPI(PhysxSchema.PhysxMimicJointAPI)
        stop = True
        if is_mimic:
            for drive, joint_state in zip(drives, joint_states):
                stiffness = drive.GetStiffnessAttr().Get()
                damping = drive.GetDampingAttr().Get()
                if (stiffness and stiffness.Get() != 0.0) or (damping and damping.Get() != 0.0):
                    stop = False
                    break
        if stop:
            return

        for drive, joint_state in zip(drives, joint_states):
            force_attr = drive.GetMaxForceAttr()
            if not force_attr.IsDefined():
                self._AddError(
                    message=f"Drive Max Force is not set on <{prim.GetPath()}>",
                    at=force_attr,
                )
            else:
                max_force = force_attr.Get()
                if max_force <= 0:
                    self._AddError(
                        message=f"Drive Max Force is zero <{force_attr.GetPath()}>",
                        at=force_attr,
                    )
                if max_force >= float("inf"):
                    self._AddError(
                        message=f"Drive Max Force is infinite <{force_attr.GetPath()}>",
                        at=force_attr,
                    )

                drive_target_position = drive.GetTargetPositionAttr()
                drive_target_velocity = drive.GetTargetVelocityAttr()

                joint_state_position = joint_state.GetPositionAttr()
                joint_state_velocity = joint_state.GetVelocityAttr()

                tolerance = 1e-2
                if drive_target_position and joint_state_position:
                    pos_diff = abs(drive_target_position.Get() - joint_state_position.Get())
                    if pos_diff > tolerance:
                        self._AddWarning(
                            message=f"Joint state position is very different from drive target position <{drive_target_position.GetPath()}>: difference is {pos_diff}",
                            at=drive_target_position,
                        )

                if drive_target_velocity and joint_state_velocity:
                    vel_diff = abs(drive_target_velocity.Get() - joint_state_velocity.Get())
                    if vel_diff > tolerance:
                        self._AddWarning(
                            message=f"Joint state velocity is very different from drive target velocity <{drive_target_velocity.GetPath()}>: difference is {vel_diff}",
                            at=drive_target_velocity,
                        )


@registerRule("IsaacSim.PhysicsRules")
class DriveJointValueReasonable(av_core.BaseRuleChecker):
    """Validates that joint drive stiffness values are within reasonable ranges.

    This rule checks that joint drive stiffness values are within defined minimum and
    maximum limits to ensure stable simulation behavior.
    """

    DRIVE_STIFFNESS_MIN = 0.0
    DRIVE_STIFFNESS_MAX = 1000000.0  # 1e6 stiffness
    NATURAL_FREQUENCY_MIN = 0.0
    NATURAL_FREQUENCY_MAX = 500.0  # 500 Hz - warning threshold.

    def CheckPrim(self, prim: Usd.Prim) -> None:
        """Check if a prim has reasonable drive stiffness values.

        Args:
            prim: The USD prim to validate.
        """
        drives, joint_states = GetJointDrivesAndJointStates(prim)
        is_mimic = prim.HasAPI(PhysxSchema.PhysxMimicJointAPI)
        for drive in drives:
            stiffness = drive.GetStiffnessAttr().Get()
            if not stiffness and not is_mimic:
                self._AddError(
                    message=f"Drive stiffness is not set on <{drive.GetPath()}>", at=drive.GetStiffnessAttr()
                )
                continue
            elif is_mimic:
                damping = drive.GetDampingAttr().Get()
                if damping:
                    if damping.Get() != 0.0:
                        self._AddError(
                            message=f"joint is mimic but has damping set <{drive.GetPath()}>", at=drive.GetDampingAttr()
                        )
                if stiffness:
                    if stiffness.Get() != 0.0:
                        self._AddError(
                            message=f"joint is mimic but has stiffness set <{drive.GetPath()}>",
                            at=drive.GetStiffnessAttr(),
                        )
            elif stiffness < self.DRIVE_STIFFNESS_MIN or stiffness > self.DRIVE_STIFFNESS_MAX:
                self._AddError(
                    message=f"Drive stiffness is out of range <{drive.GetPath()}>: {stiffness}",
                    at=prim,
                )
            continue
            # TODO: Work in progress for natural frequency
