// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include <pxr/base/tf/token.h>
#include <pxr/base/vt/array.h>
#include <pxr/pxr.h>
#include <pxr/usd/usd/attribute.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/relationship.h>

#include <unordered_map>

#pragma once

namespace isaacsim
{
namespace robot
{
namespace schema
{

// Enum for classes
enum class Classes
{
    ROBOT_API,
    LINK_API,
    REFERENCE_POINT_API,
    JOINT_API,
    SURFACE_GRIPPER,
    ATTACHMENT_POINT_API
};

// Enum for attributes
enum class Attributes
{
    DESCRIPTION,
    NAMESPACE,
    ROBOT_TYPE,
    LICENSE,
    VERSION,
    SOURCE,
    CHANGELOG,
    INDEX,
    NAME_OVERRIDE,
    FORWARD_AXIS,
    JOINT_INDEX,
    ROT_X_OFFSET,
    ROT_Y_OFFSET,
    ROT_Z_OFFSET,
    TR_X_OFFSET,
    TR_Y_OFFSET,
    TR_Z_OFFSET,
    ACCELERATION_LIMIT,
    JERK_LIMIT,
    ACTUATOR,
    STATUS,
    RETRY_INTERVAL,
    SHEAR_FORCE_LIMIT,
    COAXIAL_FORCE_LIMIT,
    MAX_GRIP_DISTANCE,
    GRIP_DISTANCE,
    CLEARANCE_OFFSET,
};

// Enum for relations
enum class Relations
{
    ROBOT_LINKS,
    ROBOT_JOINTS,
    ATTACHMENT_POINTS,
    GRIPPED_OBJECTS
};

// Common prefix token
const std::string _attrPrefix("isaac");

// Map of class names
const std::string classNames[] = { "IsaacRobotAPI", "IsaacLinkAPI",        "IsaacReferencePointAPI",
                                   "IsaacJointAPI", "IsaacSurfaceGripper", "IsaacAttachmentPointAPI" };

inline const pxr::TfToken className(Classes name)
{
    return pxr::TfToken(classNames[static_cast<int>(name)]);
}

namespace custom
{
/**
 * @struct hash
 * @brief Hash function object for enum types.
 * @details
 * Provides a hash function for enum types by casting them to size_t.
 * This allows enums to be used as keys in unordered containers.
 *
 * @tparam E The enum type to provide hashing for
 */
template <typename E>
struct hash
{
    /**
     * @brief Hash function operator for enum values.
     * @details
     * Converts an enum value to its underlying integer representation
     * and casts it to size_t for use as a hash value.
     *
     * @param[in] e The enum value to hash
     * @return size_t Hash value for the enum
     */
    size_t operator()(const E& e) const
    {
        return static_cast<size_t>(e);
    }
};
}

// Map of attribute names and types
const std::unordered_map<Attributes, std::pair<pxr::TfToken, pxr::SdfValueTypeName>> attributeNames = {
    { Attributes::DESCRIPTION, { pxr::TfToken("description"), pxr::SdfValueTypeNames->String } },
    { Attributes::NAMESPACE, { pxr::TfToken("namespace"), pxr::SdfValueTypeNames->String } },
    { Attributes::ROBOT_TYPE, { pxr::TfToken("robotType"), pxr::SdfValueTypeNames->Token } },
    { Attributes::LICENSE, { pxr::TfToken("license"), pxr::SdfValueTypeNames->Token } },
    { Attributes::VERSION, { pxr::TfToken("version"), pxr::SdfValueTypeNames->String } },
    { Attributes::SOURCE, { pxr::TfToken("source"), pxr::SdfValueTypeNames->String } },
    { Attributes::CHANGELOG, { pxr::TfToken("changelog"), pxr::SdfValueTypeNames->StringArray } },
    { Attributes::INDEX, { pxr::TfToken("physics:index"), pxr::SdfValueTypeNames->Int } },
    { Attributes::NAME_OVERRIDE, { pxr::TfToken("nameOverride"), pxr::SdfValueTypeNames->String } },
    { Attributes::FORWARD_AXIS, { pxr::TfToken("forwardAxis"), pxr::SdfValueTypeNames->Token } },
    { Attributes::JOINT_INDEX, { pxr::TfToken("physics:index"), pxr::SdfValueTypeNames->Int } },
    { Attributes::ROT_X_OFFSET, { pxr::TfToken("physics:Rot_X:DofOffset"), pxr::SdfValueTypeNames->Int } },
    { Attributes::ROT_Y_OFFSET, { pxr::TfToken("physics:Rot_Y:DofOffset"), pxr::SdfValueTypeNames->Int } },
    { Attributes::ROT_Z_OFFSET, { pxr::TfToken("physics:Rot_Z:DofOffset"), pxr::SdfValueTypeNames->Int } },
    { Attributes::TR_X_OFFSET, { pxr::TfToken("physics:Tr_X:DofOffset"), pxr::SdfValueTypeNames->Int } },
    { Attributes::TR_Y_OFFSET, { pxr::TfToken("physics:Tr_Y:DofOffset"), pxr::SdfValueTypeNames->Int } },
    { Attributes::TR_Z_OFFSET, { pxr::TfToken("physics:Tr_Z:DofOffset"), pxr::SdfValueTypeNames->Int } },
    { Attributes::ACCELERATION_LIMIT, { pxr::TfToken("physics:AccelerationLimit"), pxr::SdfValueTypeNames->FloatArray } },
    { Attributes::JERK_LIMIT, { pxr::TfToken("physics:JerkLimit"), pxr::SdfValueTypeNames->FloatArray } },
    { Attributes::ACTUATOR, { pxr::TfToken("physics:Actuator"), pxr::SdfValueTypeNames->BoolArray } },
    { Attributes::STATUS, { pxr::TfToken("status"), pxr::SdfValueTypeNames->Token } },
    { Attributes::RETRY_INTERVAL, { pxr::TfToken("retryInterval"), pxr::SdfValueTypeNames->Float } },
    { Attributes::SHEAR_FORCE_LIMIT, { pxr::TfToken("shearForceLimit"), pxr::SdfValueTypeNames->Float } },
    { Attributes::COAXIAL_FORCE_LIMIT, { pxr::TfToken("coaxialForceLimit"), pxr::SdfValueTypeNames->Float } },
    { Attributes::MAX_GRIP_DISTANCE, { pxr::TfToken("maxGripDistance"), pxr::SdfValueTypeNames->Float } },
    { Attributes::GRIP_DISTANCE, { pxr::TfToken("gripDistance"), pxr::SdfValueTypeNames->Float } },
    { Attributes::CLEARANCE_OFFSET, { pxr::TfToken("clearanceOffset"), pxr::SdfValueTypeNames->Float } }
};
// Map of relation names
const std::unordered_map<Relations, pxr::TfToken> relationNames = {
    { Relations::ROBOT_LINKS, pxr::TfToken(_attrPrefix + ":physics:robotLinks") },
    { Relations::ROBOT_JOINTS, pxr::TfToken(_attrPrefix + ":physics:robotJoints") },
    { Relations::ATTACHMENT_POINTS, pxr::TfToken(_attrPrefix + ":attachmentPoints") },
    { Relations::GRIPPED_OBJECTS, pxr::TfToken(_attrPrefix + ":grippedObjects") }
};

// Function to get attribute name
inline pxr::TfToken getAttributeName(Attributes attr)
{
    return pxr::TfToken(_attrPrefix + ":" + attributeNames.at(attr).first.GetString());
}

// Function to apply RobotAPI
inline void ApplyRobotAPI(pxr::UsdPrim& prim)
{
    prim.AddAppliedSchema(pxr::TfToken(classNames[static_cast<int>(Classes::ROBOT_API)]));
    for (const auto& attr : { Attributes::DESCRIPTION, Attributes::NAMESPACE, Attributes::ROBOT_TYPE,
                              Attributes::LICENSE, Attributes::VERSION, Attributes::SOURCE, Attributes::CHANGELOG })
    {
        prim.CreateAttribute(getAttributeName(attr), attributeNames.at(attr).second, false);
    }
    for (const auto& rel : { Relations::ROBOT_LINKS, Relations::ROBOT_JOINTS })
    {
        prim.CreateRelationship(relationNames.at(rel), false);
    }
}

// Function to apply LinkAPI
inline void ApplyLinkAPI(pxr::UsdPrim& prim)
{
    prim.AddAppliedSchema(pxr::TfToken(classNames[static_cast<int>(Classes::LINK_API)]));
    for (const auto& attr : { Attributes::NAME_OVERRIDE })
    {
        prim.CreateAttribute(getAttributeName(attr), attributeNames.at(attr).second, false);
    }
}

// Function to apply ReferencePointAPI
inline void ApplyReferencePointAPI(pxr::UsdPrim& prim)
{
    prim.AddAppliedSchema(pxr::TfToken(classNames[static_cast<int>(Classes::REFERENCE_POINT_API)]));
    for (const auto& attr : { Attributes::DESCRIPTION, Attributes::FORWARD_AXIS })
    {
        prim.CreateAttribute(getAttributeName(attr), attributeNames.at(attr).second, false);
    }
}

// Function to apply JointAPI
inline void ApplyJointAPI(pxr::UsdPrim& prim)
{
    prim.AddAppliedSchema(pxr::TfToken(classNames[static_cast<int>(Classes::JOINT_API)]));
    for (const auto& attr :
         { Attributes::JOINT_INDEX, Attributes::ROT_X_OFFSET, Attributes::ROT_Y_OFFSET, Attributes::ROT_Z_OFFSET,
           Attributes::TR_X_OFFSET, Attributes::TR_Y_OFFSET, Attributes::TR_Z_OFFSET, Attributes::NAME_OVERRIDE,
           Attributes::ACCELERATION_LIMIT, Attributes::JERK_LIMIT })
    {
        prim.CreateAttribute(getAttributeName(attr), attributeNames.at(attr).second, false);
    }
}

// /**
//  * @brief Creates a Surface Gripper prim with all its attributes and relationships
//  *
//  * @param stage The USD stage to create the prim in
//  * @param primPath The path where to create the prim
//  * @return pxr::UsdPrim The created Surface Gripper prim
//  */
inline pxr::UsdPrim CreateSurfaceGripper(pxr::UsdStagePtr stage, const std::string& primPath)
{
    // Create the prim
    pxr::UsdPrim prim =
        stage->DefinePrim(pxr::SdfPath(primPath), pxr::TfToken(classNames[static_cast<int>(Classes::SURFACE_GRIPPER)]));

    // Create attributes with default values
    for (const auto& attr : { Attributes::STATUS, Attributes::SHEAR_FORCE_LIMIT, Attributes::COAXIAL_FORCE_LIMIT,
                              Attributes::MAX_GRIP_DISTANCE, Attributes::GRIP_DISTANCE, Attributes::RETRY_INTERVAL })
    {
        prim.CreateAttribute(getAttributeName(attr), attributeNames.at(attr).second, false);
    }

    // Create relationships
    for (const auto& rel : { Relations::ATTACHMENT_POINTS, Relations::GRIPPED_OBJECTS })
    {
        prim.CreateRelationship(relationNames.at(rel), false);
    }

    return prim;
}

// Function to apply AttachmentPointAPI
inline void ApplyAttachmentPointAPI(pxr::UsdPrim& prim)
{
    prim.AddAppliedSchema(pxr::TfToken(classNames[static_cast<int>(Classes::ATTACHMENT_POINT_API)]));
    for (const auto& attr : { Attributes::FORWARD_AXIS, Attributes::CLEARANCE_OFFSET })
    {
        prim.CreateAttribute(getAttributeName(attr), attributeNames.at(attr).second, false);
    }
}

}
}
}
