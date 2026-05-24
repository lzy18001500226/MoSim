// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


#pragma once

#include "DcCommon.h"
#if defined(_WIN32)
#    include <extensions/PxD6Joint.h>
#else
#    pragma GCC diagnostic push
#    pragma GCC diagnostic ignored "-Wpragmas"
#    include <extensions/PxD6Joint.h>
#    pragma GCC diagnostic pop
#endif

#include <omni/isaac/dynamic_control/DynamicControlTypes.h>
#include <pxr/usd/sdf/path.h>

#include <PxActor.h>
#include <PxArticulationJointReducedCoordinate.h>
#include <PxArticulationLink.h>
#include <PxArticulationReducedCoordinate.h>
#include <PxRigidDynamic.h>
#include <PxScene.h>
#include <string>
#include <vector>

namespace omni
{
namespace isaac
{
namespace dynamic_control
{
// Forward declarations
struct DcRigidBody;
struct DcJoint;
struct DcDof;
struct DcArticulation;
struct DcAttractor;
class DcContext;

/**
 * @struct DcRigidBody
 * @brief Represents a rigid body in the physics simulation
 * @details
 * Contains all the information needed to represent and manipulate a rigid body,
 * including its PhysX representation, name, path, and relationships to other objects.
 */
struct DcRigidBody
{
    /**
     * @brief Handle to this rigid body
     */
    DcHandle handle = kDcInvalidHandle;

    /**
     * @brief Pointer to the context this rigid body belongs to
     */
    DcContext* ctx = nullptr;

    /**
     * @brief Pointer to the articulation this rigid body belongs to, if any
     * @details Will only be set if body is an articulation link
     */
    DcArticulation* art = nullptr;

    /**
     * @brief Name of the rigid body
     */
    std::string name;

    /**
     * @brief USD path of the rigid body
     */
    pxr::SdfPath path;

    /**
     * @brief Pointer to the PhysX rigid body
     */
    ::physx::PxRigidBody* pxRigidBody = nullptr;

    /**
     * @brief Handle to the parent joint of this rigid body
     */
    DcHandle parentJoint = kDcInvalidHandle;
    // std::vector<DcHandle> parentJoints;
    /**
     * @brief Handles to the child joints of this rigid body
     * @details Contains a list of joints for which this rigid body is the parent
     */
    std::vector<DcHandle> childJoints;

    /**
     * @brief Origin offset for the rigid body
     * @details Location with respect to which the body poses are set/get
     */
    carb::Float3 origin{ 0.0f, 0.0f, 0.0f };
};

/**
 * @struct DcJoint
 * @brief Represents a joint in the physics simulation
 * @details
 * Contains all the information needed to represent and manipulate a joint,
 * including its PhysX representation, name, path, and relationships to other objects.
 */
struct DcJoint
{
    /**
     * @brief Handle to this joint
     */
    DcHandle handle = kDcInvalidHandle;

    /**
     * @brief Pointer to the context this joint belongs to
     */
    DcContext* ctx = nullptr;

    /**
     * @brief Type of the joint
     */
    DcJointType type = DcJointType::eNone;

    /**
     * @brief Pointer to the articulation this joint belongs to, if any
     * @details Will only be set if joint is an articulation joint
     */
    DcArticulation* art = nullptr;

    /**
     * @brief Name of the joint
     */
    std::string name;

    /**
     * @brief USD path of the joint
     */
    pxr::SdfPath path;

    /**
     * @brief Pointer to the PhysX articulation joint
     * @details Only reduced coordinate articulation joints are supported for now
     */
    ::physx::PxArticulationJointReducedCoordinate* pxArticulationJoint = nullptr;

    /**
     * @brief Handle to the parent body of this joint
     */
    DcHandle parentBody = kDcInvalidHandle;

    /**
     * @brief Handle to the child body of this joint
     */
    DcHandle childBody = kDcInvalidHandle;

    /**
     * @brief Handles to the degrees of freedom of this joint
     */
    std::vector<DcHandle> dofs;
};

/**
 * @struct DcDof
 * @brief Represents a degree of freedom in the physics simulation
 * @details
 * Contains all the information needed to represent and manipulate a degree of freedom,
 * including its PhysX representation, name, path, and relationships to other objects.
 */
struct DcDof
{
    /**
     * @brief Handle to this degree of freedom
     */
    DcHandle handle = kDcInvalidHandle;

    /**
     * @brief Pointer to the context this degree of freedom belongs to
     */
    DcContext* ctx = nullptr;

    /**
     * @brief Type of the degree of freedom
     */
    DcDofType type = DcDofType::eNone;

    /**
     * @brief Pointer to the articulation this degree of freedom belongs to
     */
    DcArticulation* art = nullptr;

    /**
     * @brief Name of the degree of freedom
     */
    std::string name;

    /**
     * @brief USD path of the degree of freedom
     */
    pxr::SdfPath path;

    /**
     * @brief Pointer to the PhysX articulation joint this degree of freedom belongs to
     */
    ::physx::PxArticulationJointReducedCoordinate* pxArticulationJoint = nullptr;

    /**
     * @brief PhysX axis of this degree of freedom
     */
    ::physx::PxArticulationAxis::Enum pxAxis = ::physx::PxArticulationAxis::eTWIST;

    /**
     * @brief Drive mode of this degree of freedom
     */
    DcDriveMode driveMode = DcDriveMode::eAcceleration;

    /**
     * @brief Index in the PhysX articulation cache
     * @details Used to access this DOF's data in the articulation cache
     */
    size_t cacheIdx = 0;

    /**
     * @brief Handle to the joint this degree of freedom belongs to
     */
    DcHandle joint = kDcInvalidHandle;

    // can get these from joint
    // DcHandle parentBody;
    // DcHandle childBody;
};

/**
 * @struct DcArticulation
 * @brief Represents an articulation in the physics simulation
 * @details
 * Contains all the information needed to represent and manipulate an articulation,
 * including its PhysX representation, name, path, and relationships to other objects.
 * An articulation is a collection of rigid bodies connected by joints.
 */
struct DcArticulation
{
    /**
     * @brief Gets the number of rigid bodies in this articulation
     * @return The number of rigid bodies
     */
    size_t numRigidBodies() const
    {
        return rigidBodies.size();
    }

    /**
     * @brief Gets the number of joints in this articulation
     * @return The number of joints
     */
    size_t numJoints() const
    {
        return joints.size();
    }

    /**
     * @brief Gets the number of degrees of freedom in this articulation
     * @return The number of degrees of freedom
     */
    size_t numDofs() const
    {
        return dofs.size();
    }

    /**
     * @brief Refreshes the PhysX articulation cache
     * @param[in] flags Flags indicating which parts of the cache to refresh
     * @return True if successful, false otherwise
     */
    bool refreshCache(const ::physx::PxArticulationCacheFlags& flags = ::physx::PxArticulationCacheFlag::eALL) const;

    /**
     * @brief Handle to this articulation
     */
    DcHandle handle = kDcInvalidHandle;

    /**
     * @brief Pointer to the context this articulation belongs to
     */
    DcContext* ctx = nullptr;

    /**
     * @brief Pointer to the PhysX articulation
     */
    ::physx::PxArticulationReducedCoordinate* pxArticulation = nullptr;

    /**
     * @brief Name of the articulation
     */
    std::string name;

    /**
     * @brief USD path of the articulation
     */
    pxr::SdfPath path;

    /**
     * @brief USD paths of the components of this articulation
     */
    std::set<pxr::SdfPath> componentPaths;

    /**
     * @brief Handles to the rigid bodies in this articulation
     */
    std::vector<DcRigidBody*> rigidBodies;

    /**
     * @brief Handles to the joints in this articulation
     */
    std::vector<DcJoint*> joints;

    /**
     * @brief Handles to the degrees of freedom in this articulation
     */
    std::vector<DcDof*> dofs;

    /**
     * @brief Map from rigid body names to handles
     */
    std::map<std::string, DcRigidBody*> rigidBodyMap;

    /**
     * @brief Map from joint names to handles
     */
    std::map<std::string, DcJoint*> jointMap;

    /**
     * @brief Map from degree of freedom names to handles
     */
    std::map<std::string, DcDof*> dofMap;

    /**
     * @brief Pointer to the PhysX articulation cache
     */
    mutable ::physx::PxArticulationCache* pxArticulationCache = nullptr;

    /**
     * @brief Age of the cache, used to determine when to refresh
     */
    mutable int64_t cacheAge = -1;

    /**
     * @brief Cache of rigid body states
     */
    mutable std::vector<DcRigidBodyState> rigidBodyStateCache;

    /**
     * @brief Cache of degree of freedom states
     */
    mutable std::vector<DcDofState> dofStateCache;
};

/**
 * @struct DcAttractor
 * @brief Represents an attractor in the physics simulation
 * @details
 * Contains all the information needed to represent and manipulate an attractor,
 * which is used to apply forces to rigid bodies to attract them to a target pose.
 */
struct DcAttractor
{
    /**
     * @brief Handle to this attractor
     */
    DcHandle handle = kDcInvalidHandle;

    /**
     * @brief Pointer to the context this attractor belongs to
     */
    DcContext* ctx = nullptr;

    /**
     * @brief Pointer to the PhysX D6 joint used to implement the attractor
     */
    ::physx::PxD6Joint* pxJoint = nullptr;

    /**
     * @brief Properties of the attractor
     */
    DcAttractorProperties props{};

    /**
     * @brief USD path of the attractor
     */
    pxr::SdfPath path;
};

/**
 * @struct DcD6Joint
 * @brief Represents a D6 joint in the physics simulation
 * @details
 * Contains all the information needed to represent and manipulate a D6 joint,
 * which is a general-purpose joint that can have up to 6 degrees of freedom.
 * D6 joints can be configured to represent various joint types by constraining
 * specific degrees of freedom.
 */
struct DcD6Joint
{
    /**
     * @brief Handle to this D6 joint
     */
    DcHandle handle = kDcInvalidHandle;

    /**
     * @brief Pointer to the context this D6 joint belongs to
     */
    DcContext* ctx = nullptr;

    /**
     * @brief Pointer to the PhysX D6 joint
     */
    ::physx::PxD6Joint* pxJoint = nullptr;

    /**
     * @brief Properties of the D6 joint
     */
    DcD6JointProperties props{};

    /**
     * @brief USD path of the D6 joint
     */
    pxr::SdfPath path;
};

}
}
}
