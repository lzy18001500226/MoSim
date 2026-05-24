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
from enum import Enum

import pxr


class Classes(Enum):

    ROBOT_API = "IsaacRobotAPI"
    LINK_API = "IsaacLinkAPI"
    REFERENCE_POINT_API = "IsaacReferencePointAPI"
    JOINT_API = "IsaacJointAPI"
    SURFACE_GRIPPER = "IsaacSurfaceGripper"
    ATTACHMENT_POINT_API = "IsaacAttachmentPointAPI"


_attr_prefix = "isaac"


class Attributes(Enum):
    DESCRIPTION = (f"{_attr_prefix}:description", "Description", pxr.Sdf.ValueTypeNames.String)
    NAMESPACE = (f"{_attr_prefix}:namespace", "Namespace", pxr.Sdf.ValueTypeNames.String)
    ROBOT_TYPE = (f"{_attr_prefix}:robotType", "Robot Type", pxr.Sdf.ValueTypeNames.Token)
    LICENSE = (f"{_attr_prefix}:license", "License", pxr.Sdf.ValueTypeNames.Token)
    VERSION = (f"{_attr_prefix}:version", "Version", pxr.Sdf.ValueTypeNames.String)
    SOURCE = (f"{_attr_prefix}:source", "Source", pxr.Sdf.ValueTypeNames.String)
    CHANGELOG = (f"{_attr_prefix}:changelog", "Changelog", pxr.Sdf.ValueTypeNames.StringArray)
    INDEX = (f"{_attr_prefix}:physics:index", "Index", pxr.Sdf.ValueTypeNames.Int)
    NAME_OVERRIDE = (f"{_attr_prefix}:nameOverride", "Name Override", pxr.Sdf.ValueTypeNames.String)
    FORWARD_AXIS = (f"{_attr_prefix}:forwardAxis", "Forward Axis", pxr.Sdf.ValueTypeNames.Token)
    JOINT_INDEX = (f"{_attr_prefix}:physics:index", "Joint Index", pxr.Sdf.ValueTypeNames.Int)
    ROT_X_OFFSET = (f"{_attr_prefix}:physics:Rot_X:DofOffset", "Rot X Offset", pxr.Sdf.ValueTypeNames.Int)
    ROT_Y_OFFSET = (f"{_attr_prefix}:physics:Rot_Y:DofOffset", "Rot Y Offset", pxr.Sdf.ValueTypeNames.Int)
    ROT_Z_OFFSET = (f"{_attr_prefix}:physics:Rot_Z:DofOffset", "Rot Z Offset", pxr.Sdf.ValueTypeNames.Int)
    TR_X_OFFSET = (f"{_attr_prefix}:physics:Tr_X:DofOffset", "Tr X Offset", pxr.Sdf.ValueTypeNames.Int)
    TR_Y_OFFSET = (f"{_attr_prefix}:physics:Tr_Y:DofOffset", "Tr Y Offset", pxr.Sdf.ValueTypeNames.Int)
    TR_Z_OFFSET = (f"{_attr_prefix}:physics:Tr_Z:DofOffset", "Tr Z Offset", pxr.Sdf.ValueTypeNames.Int)
    RETRY_INTERVAL = (f"{_attr_prefix}:retryInterval", "Retry Interval", pxr.Sdf.ValueTypeNames.Float)
    ACCELERATION_LIMIT = (
        f"{_attr_prefix}:physics:AccelerationLimit",
        "Acceleration Limit",
        pxr.Sdf.ValueTypeNames.FloatArray,
    )
    JERK_LIMIT = (f"{_attr_prefix}:physics:JerkLimit", "Jerk Limit", pxr.Sdf.ValueTypeNames.FloatArray)
    ACTUATOR = (f"{_attr_prefix}:physics:Actuator", "Actuator", pxr.Sdf.ValueTypeNames.BoolArray)
    STATUS = (f"{_attr_prefix}:status", "Status", pxr.Sdf.ValueTypeNames.Token)
    SHEAR_FORCE_LIMIT = (f"{_attr_prefix}:shearForceLimit", "Shear Force Limit", pxr.Sdf.ValueTypeNames.Float)
    COAXIAL_FORCE_LIMIT = (f"{_attr_prefix}:coaxialForceLimit", "Coaxial Force Limit", pxr.Sdf.ValueTypeNames.Float)
    MAX_GRIP_DISTANCE = (f"{_attr_prefix}:maxGripDistance", "Max Grip Distance", pxr.Sdf.ValueTypeNames.Float)
    CLEARANCE_OFFSET = (f"{_attr_prefix}:clearanceOffset", "Clearance Offset", pxr.Sdf.ValueTypeNames.Float)

    # Custom properties for name and type
    @property
    def name(self):
        return self.value[0]

    @property
    def display_name(self):
        return self.value[1]

    @property
    def type(self):
        return self.value[2]


class Relations(Enum):
    ROBOT_LINKS = (f"{_attr_prefix}:physics:robotLinks", "Robot Links")
    ROBOT_JOINTS = (f"{_attr_prefix}:physics:robotJoints", "Robot Joints")
    ATTACHMENT_POINTS = (f"{_attr_prefix}:attachmentPoints", "Attachment Points")
    GRIPPED_OBJECTS = (f"{_attr_prefix}:grippedObjects", "Gripped Objects")

    @property
    def name(self):
        return self.value[0]

    @property
    def display_name(self):
        return self.value[1]


def ApplyRobotAPI(prim: pxr.Usd.Prim):
    prim.AddAppliedSchema(Classes.ROBOT_API.value)
    for attr in [
        Attributes.DESCRIPTION,
        Attributes.NAMESPACE,
        Attributes.ROBOT_TYPE,
        Attributes.LICENSE,
        Attributes.VERSION,
        Attributes.SOURCE,
        Attributes.CHANGELOG,
    ]:
        prim.CreateAttribute(attr.name, attr.type, True)

    for rel in [Relations.ROBOT_LINKS, Relations.ROBOT_JOINTS]:
        prim.CreateRelationship(rel.name, custom=True)


def ApplyLinkAPI(prim: pxr.Usd.Prim):
    prim.AddAppliedSchema(Classes.LINK_API.value)
    for attr in [Attributes.NAME_OVERRIDE]:
        prim.CreateAttribute(attr.name, attr.type, True)


def ApplyReferencePointAPI(prim: pxr.Usd.Prim):
    prim.AddAppliedSchema(Classes.REFERENCE_POINT_API.value)
    for attr in [Attributes.DESCRIPTION, Attributes.FORWARD_AXIS]:
        prim.CreateAttribute(attr.name, attr.type, True)


def ApplyJointAPI(prim: pxr.Usd.Prim):
    prim.AddAppliedSchema(Classes.JOINT_API.value)
    for attr in [
        Attributes.ROT_X_OFFSET,
        Attributes.ROT_Y_OFFSET,
        Attributes.ROT_Z_OFFSET,
        Attributes.TR_X_OFFSET,
        Attributes.TR_Y_OFFSET,
        Attributes.TR_Z_OFFSET,
        Attributes.NAME_OVERRIDE,
        Attributes.ACCELERATION_LIMIT,
        Attributes.JERK_LIMIT,
    ]:
        prim.CreateAttribute(attr.name, attr.type, True)


def CreateSurfaceGripper(stage: pxr.Usd.Stage, prim_path: str) -> pxr.Usd.Prim:
    """Creates a Surface Gripper prim with all its attributes and relationships.

    Args:
        stage: The USD stage to create the prim in
        prim_path: The path where to create the prim

    Returns:
        The created Surface Gripper prim
    """
    # Create the prim
    prim = stage.DefinePrim(prim_path, Classes.SURFACE_GRIPPER.value)

    # Create attributes with default values
    for attr in [
        Attributes.STATUS,
        Attributes.SHEAR_FORCE_LIMIT,
        Attributes.COAXIAL_FORCE_LIMIT,
        Attributes.MAX_GRIP_DISTANCE,
        Attributes.RETRY_INTERVAL,
    ]:
        prim.CreateAttribute(attr.name, attr.type, False)

    # Create relationships
    prim.CreateRelationship(Relations.ATTACHMENT_POINTS.name, False)
    prim.CreateRelationship(Relations.GRIPPED_OBJECTS.name, False)

    return prim


def ApplyAttachmentPointAPI(prim: pxr.Usd.Prim):
    prim.AddAppliedSchema(Classes.ATTACHMENT_POINT_API.name)
    for attr in [Attributes.FORWARD_AXIS, Attributes.CLEARANCE_OFFSET]:
        prim.CreateAttribute(attr.name, attr.type, False)
