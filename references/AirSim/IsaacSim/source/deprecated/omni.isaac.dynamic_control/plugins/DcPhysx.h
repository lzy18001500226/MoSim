// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#include "DcTypes.h"


namespace omni
{
namespace physx
{
struct IPhysx;
struct IPhysxSceneQuery;

}
}

namespace omni
{
namespace isaac
{
namespace dynamic_control
{

/**
 * @class DcContext
 * @brief Context for managing dynamic control objects in a physics scene
 * @details
 * Provides functionality for creating, retrieving, and managing physics objects
 * such as rigid bodies, joints, articulations, and attractors. Maintains the mapping
 * between USD paths and physics objects.
 */
class DcContext
{
public:
    /**
     * @brief Constructs a DcContext with the given context ID
     * @param[in] ctxId The unique identifier for this context
     */
    explicit DcContext(uint32_t ctxId);

    /**
     * @brief Gets the ID of this context
     * @return The context ID
     */
    uint32_t getId() const;

    /**
     * @brief Registers a rigid body at the specified USD path
     * @param[in] usdPath The USD path to register
     * @return Handle to the registered rigid body
     */
    DcHandle registerRigidBody(const pxr::SdfPath& usdPath);

    /**
     * @brief Registers a joint at the specified USD path
     * @param[in] usdPath The USD path to register
     * @return Handle to the registered joint
     */
    static DcHandle registerJoint(const pxr::SdfPath& usdPath);

    /**
     * @brief Registers a degree of freedom at the specified USD path
     * @param[in] usdPath The USD path to register
     * @return Handle to the registered degree of freedom
     */
    static DcHandle registerDof(const pxr::SdfPath& usdPath);

    /**
     * @brief Registers an articulation at the specified USD path
     * @param[in] usdPath The USD path to register
     * @return Handle to the registered articulation
     */
    DcHandle registerArticulation(const pxr::SdfPath& usdPath);

    /**
     * @brief Registers a D6 joint at the specified USD path
     * @param[in] usdPath The USD path to register
     * @return Handle to the registered D6 joint
     */
    DcHandle registerD6Joint(const pxr::SdfPath& usdPath);

    /**
     * @brief Adds a rigid body to the context
     * @param[in] rb The rigid body to add
     * @param[in] usdPath The USD path to associate with the rigid body
     * @return Handle to the added rigid body
     */
    DcHandle addRigidBody(std::unique_ptr<DcRigidBody>&& rb, const pxr::SdfPath& usdPath);

    /**
     * @brief Adds a joint to the context
     * @param[in] joint The joint to add
     * @param[in] usdPath The USD path to associate with the joint
     * @return Handle to the added joint
     */
    DcHandle addJoint(std::unique_ptr<DcJoint>&& joint, const pxr::SdfPath& usdPath);

    /**
     * @brief Adds a degree of freedom to the context
     * @param[in] dof The degree of freedom to add
     * @param[in] usdPath The USD path to associate with the degree of freedom
     * @return Handle to the added degree of freedom
     */
    DcHandle addDof(std::unique_ptr<DcDof>&& dof, const pxr::SdfPath& usdPath);

    /**
     * @brief Adds an articulation to the context
     * @param[in] art The articulation to add
     * @param[in] usdPath The USD path to associate with the articulation
     * @return Handle to the added articulation
     */
    DcHandle addArticulation(std::unique_ptr<DcArticulation>&& art, const pxr::SdfPath& usdPath);

    /**
     * @brief Adds an attractor to the context
     * @param[in] attractor The attractor to add
     * @param[in] usdPath The USD path to associate with the attractor
     * @return Handle to the added attractor
     */
    DcHandle addAttractor(std::unique_ptr<DcAttractor>&& attractor, const pxr::SdfPath& usdPath);

    /**
     * @brief Adds a D6 joint to the context
     * @param[in] dc_joint The D6 joint to add
     * @param[in] usdPath The USD path to associate with the D6 joint
     * @return Handle to the added D6 joint
     */
    DcHandle addD6Joint(std::unique_ptr<DcD6Joint>&& dc_joint, const pxr::SdfPath& usdPath);


    /**
     * @brief Gets the handle of a rigid body at the specified USD path
     * @param[in] usdPath The USD path of the rigid body
     * @return Handle to the rigid body, or an invalid handle if not found
     */
    DcHandle getRigidBodyHandle(const pxr::SdfPath& usdPath) const;

    /**
     * @brief Gets the handle of a joint at the specified USD path
     * @param[in] usdPath The USD path of the joint
     * @return Handle to the joint, or an invalid handle if not found
     */
    DcHandle getJointHandle(const pxr::SdfPath& usdPath) const;

    // HMMM, there could be multiple DOFs at a single USD path (e.g. spherical joint)
    /**
     * @brief Gets the handle of a degree of freedom at the specified USD path
     * @param[in] usdPath The USD path of the degree of freedom
     * @return Handle to the degree of freedom, or an invalid handle if not found
     */
    DcHandle getDofHandle(const pxr::SdfPath& usdPath) const;

    /**
     * @brief Gets the handle of an articulation at the specified USD path
     * @param[in] usdPath The USD path of the articulation
     * @return Handle to the articulation, or an invalid handle if not found
     */
    DcHandle getArticulationHandle(const pxr::SdfPath& usdPath) const;

    /**
     * @brief Gets the handle of an attractor at the specified USD path
     * @param[in] usdPath The USD path of the attractor
     * @return Handle to the attractor, or an invalid handle if not found
     */
    DcHandle getAttractorHandle(const pxr::SdfPath& usdPath) const;

    /**
     * @brief Gets a rigid body by its handle
     * @param[in] handle The handle of the rigid body
     * @return Pointer to the rigid body, or nullptr if not found
     */
    DcRigidBody* getRigidBody(DcHandle handle) const;

    /**
     * @brief Gets a joint by its handle
     * @param[in] handle The handle of the joint
     * @return Pointer to the joint, or nullptr if not found
     */
    DcJoint* getJoint(DcHandle handle) const;

    /**
     * @brief Gets a degree of freedom by its handle
     * @param[in] handle The handle of the degree of freedom
     * @return Pointer to the degree of freedom, or nullptr if not found
     */
    DcDof* getDof(DcHandle handle) const;

    /**
     * @brief Gets an articulation by its handle
     * @param[in] handle The handle of the articulation
     * @return Pointer to the articulation, or nullptr if not found
     */
    DcArticulation* getArticulation(DcHandle handle) const;

    /**
     * @brief Gets an attractor by its handle
     * @param[in] handle The handle of the attractor
     * @return Pointer to the attractor, or nullptr if not found
     */
    DcAttractor* getAttractor(DcHandle handle) const;

    /**
     * @brief Gets a D6 joint by its handle
     * @param[in] handle The handle of the D6 joint
     * @return Pointer to the D6 joint, or nullptr if not found
     */
    DcD6Joint* getD6Joint(DcHandle handle) const;

    /**
     * @brief Removes a rigid body from the context
     * @param[in] handle The handle of the rigid body to remove
     */
    void removeRigidBody(DcHandle handle);

    /**
     * @brief Removes a joint from the context
     * @param[in] handle The handle of the joint to remove
     */
    void removeJoint(DcHandle handle);

    /**
     * @brief Removes an articulation from the context
     * @param[in] handle The handle of the articulation to remove
     */
    void removeArticulation(DcHandle handle);

    /**
     * @brief Removes an attractor from the context
     * @param[in] handle The handle of the attractor to remove
     */
    void removeAttractor(DcHandle handle);

    /**
     * @brief Removes a D6 joint from the context
     * @param[in] handle The handle of the D6 joint to remove
     */
    void removeD6Joint(DcHandle handle);

    /**
     * @brief Removes an object from the context based on its handle
     * @param[in] handle The handle of the object to remove
     */
    void remove(DcHandle handle);

    /**
     * @brief Removes all objects associated with the specified USD path
     * @param[in] usdPath The USD path to remove
     */
    void removeUsdPath(const pxr::SdfPath& usdPath);

    /**
     * @brief Gets the number of attractors in the context
     * @return The number of attractors
     */
    int numAttractors() const;

    /**
     * @brief Gets the number of D6 joints in the context
     * @return The number of D6 joints
     */
    int numD6Joints() const;

    /**
     * @brief Pointer to the PhysX interface
     */
    omni::physx::IPhysx* physx = nullptr;

    /**
     * @brief Pointer to the PhysX scene query interface
     */
    omni::physx::IPhysxSceneQuery* physxSceneQuery = nullptr;

    /**
     * @brief Flag indicating whether the simulation is currently running
     */
    bool isSimulating = false;

    /**
     * @brief Weak pointer to the USD stage
     */
    pxr::UsdStageWeakPtr mStage = nullptr;

    /**
     * @brief Flag indicating whether the simulation was paused
     */
    bool wasPaused = false;

    /**
     * @brief Refreshes the physics pointers after a reset
     * @param[in] verbose Whether to print verbose output
     */
    void refreshPhysicsPointers(bool verbose);

private:
    // refresh after a physics reset
    bool refreshPhysicsPointers(DcRigidBody* body, bool verbose);
    bool refreshPhysicsPointers(DcJoint* joint, bool verbose);
    // bool refreshPhysicsPointers(DcDof* dof, bool verbose); // refreshing joint will refresh its dofs
    bool refreshPhysicsPointers(DcArticulation* art, bool verbose);
    bool refreshPhysicsPointers(DcAttractor* att, bool verbose);
    bool refreshPhysicsPointers(DcD6Joint* d6joint, bool verbose);

    uint32_t mId = 0;

    Bucket<DcRigidBody> mRigidBodies;
    Bucket<DcJoint> mJoints;
    Bucket<DcDof> mDofs;
    Bucket<DcArticulation> mArticulations;
    Bucket<DcAttractor> mAttractors;
    Bucket<DcD6Joint> mD6Joints;

    std::unordered_map<pxr::SdfPath, DcHandle, pxr::SdfPath::Hash> mRigidBodyMap;
    std::unordered_map<pxr::SdfPath, DcHandle, pxr::SdfPath::Hash> mJointMap;
    std::unordered_map<pxr::SdfPath, DcHandle, pxr::SdfPath::Hash> mDofMap;
    std::unordered_map<pxr::SdfPath, DcHandle, pxr::SdfPath::Hash> mArticulationMap;
    std::unordered_map<pxr::SdfPath, DcHandle, pxr::SdfPath::Hash> mAttractorMap;
    std::unordered_map<pxr::SdfPath, DcHandle, pxr::SdfPath::Hash> mD6JointMap;

    // Maps USD paths to handles.  There can be more than one handle per path.
    // e.g., articulation at same path as one of its links
    // e.g., dof at the same path as a revolute/prismatic joint
    // e.g., multiple dofs of a spherical joint
    std::unordered_map<pxr::SdfPath, std::set<DcHandle>, pxr::SdfPath::Hash> mHandleMap;
};

}
}
}
