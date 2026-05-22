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

#include "DynamicControlTypes.h"

namespace omni
{
namespace isaac
{
namespace dynamic_control
{

/**
 * @struct DynamicControl
 * @brief Interface for controlling physics objects in Isaac Sim
 * @details
 * The Dynamic Control extension provides a set of utilities to control physics objects.
 * It provides opaque handles for different physics objects that remain valid between
 * PhysX scene resets, which occur whenever play or stop is pressed.
 */
struct DynamicControl
{
    CARB_PLUGIN_INTERFACE("omni::isaac::dynamic_control::DynamicControl", 0, 1);


    // DcContext*(CARB_ABI* createContext)(const char* scenePath);
    // void(CARB_ABI* destroyContext)(DcContext* ctx);

    // call at end of frame
    // void(CARB_ABI* updateContext)(DcContext* ctx);

    /**
     * @brief Checks if the physics simulation is currently running
     * @return True if simulation is running, false otherwise
     */
    bool(CARB_ABI* isSimulating)();

    //===== Actors =====//

    /**
     * @brief Gets a handle to a rigid body at the specified USD path
     * @param[in] usdPath Path to the rigid body in the USD stage
     * @return Handle to the rigid body, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* getRigidBody)(const char* usdPath);

    /**
     * @brief Gets a handle to a joint at the specified USD path
     * @param[in] usdPath Path to the joint in the USD stage
     * @return Handle to the joint, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* getJoint)(const char* usdPath);

    /**
     * @brief Gets a handle to a degree of freedom at the specified USD path
     * @param[in] usdPath Path to the degree of freedom in the USD stage
     * @return Handle to the degree of freedom, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* getDof)(const char* usdPath);

    /**
     * @brief Gets a handle to an articulation at the specified USD path
     * @param[in] usdPath Path to the articulation in the USD stage
     * @return Handle to the articulation, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* getArticulation)(const char* usdPath);

    /**
     * @brief Gets a handle to a D6 joint at the specified USD path
     * @param[in] usdPath Path to the D6 joint in the USD stage
     * @return Handle to the D6 joint, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* getD6Joint)(const char* usdPath);

    // generic objects and types
    /**
     * @brief Gets a handle to a physics object at the specified USD path
     * @param[in] usdPath Path to the physics object in the USD stage
     * @return Handle to the physics object, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* getObject)(const char* usdPath);

    /**
     * @brief Checks the type of a physics object at the specified USD path without creating a handle
     * @param[in] usdPath Path to the physics object in the USD stage
     * @return Type of the physics object
     */
    DcObjectType(CARB_ABI* peekObjectType)(const char* usdPath);

    /**
     * @brief Gets the type of a physics object from its handle
     * @param[in] handle Handle to the physics object
     * @return Type of the physics object
     */
    DcObjectType(CARB_ABI* getObjectType)(DcHandle handle);

    /**
     * @brief Gets the type name of a physics object from its handle
     * @param[in] handle Handle to the physics object
     * @return Type name of the physics object as a string
     */
    const char*(CARB_ABI* getObjectTypeName)(DcHandle handle);

    // int(CARB_ABI* getArticulationCount)(const DcContext* ctx);
    // int(CARB_ABI* getArticulations)(DcContext* ctx, DcArticulation** userBuffer, int bufferSize);

    /**
     * @brief Wakes up a rigid body for simulation
     * @param[in] bodyHandle Handle to the rigid body
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* wakeUpRigidBody)(DcHandle bodyHandle);

    /**
     * @brief Wakes up an articulation for simulation
     * @param[in] artHandle Handle to the articulation
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* wakeUpArticulation)(DcHandle artHandle);

    /**
     * @brief Puts a rigid body to sleep
     * @param[in] bodyHandle Handle to the rigid body
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* sleepRigidBody)(DcHandle bodyHandle);

    /**
     * @brief Puts an articulation to sleep
     * @param[in] artHandle Handle to the articulation
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* sleepArticulation)(DcHandle artHandle);

    //===== Articulations =====//

    /**
     * @brief Gets the name of an articulation
     * @param[in] artHandle Handle to the articulation
     * @return Name of the articulation
     */
    const char*(CARB_ABI* getArticulationName)(DcHandle artHandle);

    /**
     * @brief Gets the USD path of an articulation
     * @param[in] artHandle Handle to the articulation
     * @return USD path of the articulation
     */
    const char*(CARB_ABI* getArticulationPath)(DcHandle artHandle);

    /**
     * @brief Gets the number of rigid bodies in an articulation
     * @param[in] artHandle Handle to the articulation
     * @return Number of rigid bodies in the articulation
     */
    size_t(CARB_ABI* getArticulationBodyCount)(DcHandle artHandle);

    /**
     * @brief Gets a rigid body in an articulation by its index
     * @param[in] artHandle Handle to the articulation
     * @param[in] bodyIdx Index of the rigid body
     * @return Handle to the rigid body
     */
    DcHandle(CARB_ABI* getArticulationBody)(DcHandle artHandle, size_t bodyIdx);

    /**
     * @brief Finds a rigid body in an articulation by its name
     * @param[in] artHandle Handle to the articulation
     * @param[in] bodyName Name of the rigid body
     * @return Handle to the rigid body, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* findArticulationBody)(DcHandle artHandle, const char* bodyName);

    /**
     * @brief Finds the index of a rigid body in an articulation by its name
     * @param[in] artHandle Handle to the articulation
     * @param[in] bodyName Name of the rigid body
     * @return Index of the rigid body, or -1 if not found
     */
    int(CARB_ABI* findArticulationBodyIndex)(DcHandle artHandle, const char* bodyName);

    /**
     * @brief Gets the root rigid body of an articulation
     * @param[in] artHandle Handle to the articulation
     * @return Handle to the root rigid body
     */
    DcHandle(CARB_ABI* getArticulationRootBody)(DcHandle artHandle);

    /**
     * @brief Gets the states of all rigid bodies in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] flags Flags indicating which states to get (position, velocity, etc.)
     * @return Array of rigid body states
     */
    DcRigidBodyState*(CARB_ABI* getArticulationBodyStates)(DcHandle artHandle, const DcStateFlags& flags);

    // //! Sets states for an actor's rigid bodies.
    // /*!
    //  *  \param actor the actor.
    //  *  \param states the states to set.
    //  *  \param flags flags for the state to obtain (kDcStatePos, kDcStateVel, or kDcStateAll)
    //  */
    // bool(CARB_ABI* setArticulationBodyStates)(DcHandle artHandle, const DcRigidBodyState* states, DcStateFlags
    // flags);

    /**
     * @brief Gets the properties of an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[out] properties Articulation properties to be filled
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getArticulationProperties)(DcHandle artHandle, DcArticulationProperties* properties);

    /**
     * @brief Sets the properties of an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] properties Articulation properties to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setArticulationProperties)(DcHandle artHandle, const DcArticulationProperties& properties);

    //===== Articulation joints =====//

    /**
     * @brief Gets the number of joints in an articulation
     * @param[in] artHandle Handle to the articulation
     * @return Number of joints in the articulation
     */
    size_t(CARB_ABI* getArticulationJointCount)(DcHandle artHandle);

    /**
     * @brief Gets a joint in an articulation by its index
     * @param[in] artHandle Handle to the articulation
     * @param[in] jointIdx Index of the joint
     * @return Handle to the joint
     */
    DcHandle(CARB_ABI* getArticulationJoint)(DcHandle artHandle, size_t jointIdx);

    /**
     * @brief Finds a joint in an articulation by its name
     * @param[in] artHandle Handle to the articulation
     * @param[in] jointName Name of the joint
     * @return Handle to the joint, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* findArticulationJoint)(DcHandle artHandle, const char* jointName);

    //===== Articulation DOFs (degrees of freedom) =====//

    /**
     * @brief Gets the number of degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @return Number of degrees of freedom in the articulation
     */
    size_t(CARB_ABI* getArticulationDofCount)(DcHandle artHandle);

    /**
     * @brief Gets a degree of freedom in an articulation by its index
     * @param[in] artHandle Handle to the articulation
     * @param[in] dofIdx Index of the degree of freedom
     * @return Handle to the degree of freedom
     */
    DcHandle(CARB_ABI* getArticulationDof)(DcHandle artHandle, size_t dofIdx);

    /**
     * @brief Finds a degree of freedom in an articulation by its name
     * @param[in] artHandle Handle to the articulation
     * @param[in] dofName Name of the degree of freedom
     * @return Handle to the degree of freedom, or an invalid handle if not found
     */
    DcHandle(CARB_ABI* findArticulationDof)(DcHandle artHandle, const char* dofName);

    /**
     * @brief Finds the index of a degree of freedom in an articulation by its name
     * @param[in] artHandle Handle to the articulation
     * @param[in] dofName Name of the degree of freedom
     * @return Index of the degree of freedom, or -1 if not found
     */
    int(CARB_ABI* findArticulationDofIndex)(DcHandle artHandle, const char* dofName);

    /**
     * @brief Gets the properties of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[out] props Array of degree of freedom properties to be filled
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getArticulationDofProperties)(DcHandle artHandle, DcDofProperties* props);

    /**
     * @brief Sets the properties of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] props Array of degree of freedom properties to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setArticulationDofProperties)(DcHandle artHandle, const DcDofProperties* props);

    /**
     * @brief Gets the states of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] flags Flags indicating which states to get (position, velocity, etc.)
     * @return Array of degree of freedom states
     */
    DcDofState*(CARB_ABI* getArticulationDofStates)(DcHandle artHandle, const DcStateFlags& flags);

    /**
     * @brief Gets the state derivatives of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] states States at which derivatives are evaluated
     * @param[in] efforts Efforts at which derivatives are evaluated
     * @return Array of degree of freedom state derivatives
     *
     * @note Sets the articulation DoFs and efforts to the values provided
     */
    DcDofState*(CARB_ABI* getArticulationDofStateDerivatives)(DcHandle artHandle,
                                                              const DcDofState* states,
                                                              const float* efforts);

    /**
     * @brief Sets the states of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] states Array of degree of freedom states to set
     * @param[in] flags Flags indicating which states to set (position, velocity, etc.)
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setArticulationDofStates)(DcHandle artHandle, const DcDofState* states, const DcStateFlags& flags);

    /**
     * @brief Sets the position targets of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] targets Array of position targets to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setArticulationDofPositionTargets)(DcHandle artHandle, const float* targets);

    /**
     * @brief Gets the position targets of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[out] targets Array to be filled with position targets
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getArticulationDofPositionTargets)(DcHandle artHandle, float* targets);

    /**
     * @brief Sets the velocity targets of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] targets Array of velocity targets to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setArticulationDofVelocityTargets)(DcHandle artHandle, const float* targets);

    /**
     * @brief Gets the velocity targets of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[out] targets Array to be filled with velocity targets
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getArticulationDofVelocityTargets)(DcHandle artHandle, float* targets);

    /**
     * @brief Sets the efforts of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[in] efforts Array of efforts to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setArticulationDofEfforts)(DcHandle artHandle, const float* efforts);

    /**
     * @brief Gets the efforts of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[out] efforts Array to be filled with efforts
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getArticulationDofEfforts)(DcHandle artHandle, float* efforts);

    /**
     * @brief Gets the effective masses of all degrees of freedom in an articulation
     * @param[in] artHandle Handle to the articulation
     * @param[out] masses Array to be filled with effective masses
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getArticulationDofMasses)(DcHandle artHandle, float* masses);


    // rigid bodies

    /**
     * @brief Gets the name of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @return Name of the rigid body
     */
    const char*(CARB_ABI* getRigidBodyName)(DcHandle bodyHandle);

    /**
     * @brief Gets the USD path of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @return USD path of the rigid body
     */
    const char*(CARB_ABI* getRigidBodyPath)(DcHandle bodyHandle);

    /**
     * @brief Gets the parent joint of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @return Handle to the parent joint, or an invalid handle if none
     */
    DcHandle(CARB_ABI* getRigidBodyParentJoint)(DcHandle bodyHandle);

    /**
     * @brief Gets the number of child joints of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @return Number of child joints
     */
    size_t(CARB_ABI* getRigidBodyChildJointCount)(DcHandle bodyHandle);

    /**
     * @brief Gets a child joint of a rigid body by its index
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] jointIdx Index of the child joint
     * @return Handle to the child joint
     */
    DcHandle(CARB_ABI* getRigidBodyChildJoint)(DcHandle bodyHandle, size_t jointIdx);

    /**
     * @brief Gets the pose of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @return Pose of the rigid body
     */
    DcTransform(CARB_ABI* getRigidBodyPose)(DcHandle bodyHandle);

    /**
     * @brief Gets the linear velocity of a rigid body in world coordinates
     * @param[in] bodyHandle Handle to the rigid body
     * @return Linear velocity of the rigid body
     */
    carb::Float3(CARB_ABI* getRigidBodyLinearVelocity)(DcHandle bodyHandle);

    /**
     * @brief Gets the linear velocity of a rigid body in local coordinates
     * @param[in] bodyHandle Handle to the rigid body
     * @return Linear velocity of the rigid body in local coordinates
     */
    carb::Float3(CARB_ABI* getRigidBodyLocalLinearVelocity)(DcHandle bodyHandle);

    /**
     * @brief Gets the angular velocity of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @return Angular velocity of the rigid body
     */
    carb::Float3(CARB_ABI* getRigidBodyAngularVelocity)(DcHandle bodyHandle);

    /**
     * @brief Enables or disables gravity for a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] disableGravity True to disable gravity, false to enable
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setRigidBodyDisableGravity)(DcHandle bodyHandle, const bool disableGravity);

    /**
     * @brief Enables or disables simulation for a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] disableSimulation True to disable simulation, false to enable
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setRigidBodyDisableSimulation)(DcHandle bodyHandle, const bool disableSimulation);

    /**
     * @brief Sets the pose of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] pose Pose to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setRigidBodyPose)(DcHandle bodyHandle, const DcTransform& pose);

    /**
     * @brief Sets the linear velocity of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] linvel Linear velocity to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setRigidBodyLinearVelocity)(DcHandle bodyHandle, const carb::Float3& linvel);

    /**
     * @brief Sets the angular velocity of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] angvel Angular velocity to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setRigidBodyAngularVelocity)(DcHandle bodyHandle, const carb::Float3& angvel);

    /**
     * @brief Applies a force to a rigid body at a specific position
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] force Force to apply
     * @param[in] pos Position at which to apply the force
     * @param[in] globalCoordinates True if force and position are in global coordinates, false if in local coordinates
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* applyBodyForce)(DcHandle bodyHandle,
                                   const carb::Float3& force,
                                   const carb::Float3& pos,
                                   const bool globalCoordinates);

    /**
     * @brief Applies a torque to a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] torque Torque to apply
     * @param[in] globalCoordinates True if torque is in global coordinates, false if in local coordinates
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* applyBodyTorque)(DcHandle bodyHandle, const carb::Float3& torque, const bool globalCoordinates);

    /**
     * @brief Gets the poses of multiple rigid bodies relative to a parent body
     * @param[in] parentHandle Handle to the parent rigid body
     * @param[in] numBodies Number of rigid bodies
     * @param[in] bodyHandles Array of handles to the rigid bodies
     * @param[out] bodyTransforms Array to be filled with relative poses
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getRelativeBodyPoses)(DcHandle parentHandle,
                                         size_t numBodies,
                                         const DcHandle* bodyHandles,
                                         DcTransform* bodyTransforms);

    /**
     * @brief Gets the properties of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[out] props Rigid body properties to be filled
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getRigidBodyProperties)(DcHandle bodyHandle, DcRigidBodyProperties* props);

    /**
     * @brief Sets the properties of a rigid body
     * @param[in] bodyHandle Handle to the rigid body
     * @param[in] properties Rigid body properties to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setRigidBodyProperties)(DcHandle bodyHandle, const DcRigidBodyProperties& properties);

    // joints

    /**
     * @brief Gets the name of a joint
     * @param[in] jointHandle Handle to the joint
     * @return Name of the joint
     */
    const char*(CARB_ABI* getJointName)(DcHandle jointHandle);

    /**
     * @brief Gets the USD path of a joint
     * @param[in] jointHandle Handle to the joint
     * @return USD path of the joint
     */
    const char*(CARB_ABI* getJointPath)(DcHandle jointHandle);

    /**
     * @brief Gets the type of a joint
     * @param[in] jointHandle Handle to the joint
     * @return Type of the joint
     */
    DcJointType(CARB_ABI* getJointType)(DcHandle jointHandle);

    /**
     * @brief Gets the number of degrees of freedom in a joint
     * @param[in] jointHandle Handle to the joint
     * @return Number of degrees of freedom in the joint
     */
    size_t(CARB_ABI* getJointDofCount)(DcHandle jointHandle);

    /**
     * @brief Gets a degree of freedom in a joint by its index
     * @param[in] jointHandle Handle to the joint
     * @param[in] dofIdx Index of the degree of freedom
     * @return Handle to the degree of freedom
     */
    DcHandle(CARB_ABI* getJointDof)(DcHandle jointHandle, size_t dofIdx);

    /**
     * @brief Gets the parent rigid body of a joint
     * @param[in] jointHandle Handle to the joint
     * @return Handle to the parent rigid body
     */
    DcHandle(CARB_ABI* getJointParentBody)(DcHandle jointHandle);

    /**
     * @brief Gets the child rigid body of a joint
     * @param[in] jointHandle Handle to the joint
     * @return Handle to the child rigid body
     */
    DcHandle(CARB_ABI* getJointChildBody)(DcHandle jointHandle);

    // dofs

    /**
     * @brief Gets the name of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Name of the degree of freedom
     */
    const char*(CARB_ABI* getDofName)(DcHandle dofHandle);

    /**
     * @brief Gets the USD path of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return USD path of the degree of freedom
     */
    const char*(CARB_ABI* getDofPath)(DcHandle dofHandle);

    /**
     * @brief Gets the type of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Type of the degree of freedom
     */
    DcDofType(CARB_ABI* getDofType)(DcHandle dofHandle);

    /**
     * @brief Gets the joint that a degree of freedom belongs to
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Handle to the joint
     */
    DcHandle(CARB_ABI* getDofJoint)(DcHandle dofHandle);

    /**
     * @brief Gets the parent rigid body of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Handle to the parent rigid body
     */
    DcHandle(CARB_ABI* getDofParentBody)(DcHandle dofHandle);

    /**
     * @brief Gets the child rigid body of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Handle to the child rigid body
     */
    DcHandle(CARB_ABI* getDofChildBody)(DcHandle dofHandle);

    /**
     * @brief Gets the state of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] flags Flags indicating which states to get (position, velocity, etc.)
     * @return State of the degree of freedom
     */
    DcDofState(CARB_ABI* getDofState)(DcHandle dofHandle, const DcStateFlags& flags);

    /**
     * @brief Sets the state of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] state State to set
     * @param[in] flags Flags indicating which states to set (position, velocity, etc.)
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setDofState)(DcHandle dofHandle, const DcDofState* state, const DcStateFlags& flags);

    /**
     * @brief Gets the position of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Position of the degree of freedom
     */
    float(CARB_ABI* getDofPosition)(DcHandle dofHandle);

    /**
     * @brief Sets the position of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] pos Position to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setDofPosition)(DcHandle dofHandle, float pos);

    /**
     * @brief Gets the velocity of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Velocity of the degree of freedom
     */
    float(CARB_ABI* getDofVelocity)(DcHandle dofHandle);

    /**
     * @brief Sets the velocity of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] vel Velocity to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setDofVelocity)(DcHandle dofHandle, float vel);

    /**
     * @brief Gets the properties of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[out] props Degree of freedom properties to be filled
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getDofProperties)(DcHandle dofHandle, DcDofProperties* props);

    /**
     * @brief Sets the properties of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] props Degree of freedom properties to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setDofProperties)(DcHandle dofHandle, const DcDofProperties* props);

    /**
     * @brief Sets the position target of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] target Position target to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setDofPositionTarget)(DcHandle dofHandle, float target);

    /**
     * @brief Sets the velocity target of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] target Velocity target to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setDofVelocityTarget)(DcHandle dofHandle, float target);

    /**
     * @brief Gets the position target of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Position target of the degree of freedom
     */
    float(CARB_ABI* getDofPositionTarget)(DcHandle dofHandle);

    /**
     * @brief Gets the velocity target of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Velocity target of the degree of freedom
     */
    float(CARB_ABI* getDofVelocityTarget)(DcHandle dofHandle);

    /**
     * @brief Sets the effort of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @param[in] effort Effort to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setDofEffort)(DcHandle dofHandle, float effort);

    /**
     * @brief Gets the effort of a degree of freedom
     * @param[in] dofHandle Handle to the degree of freedom
     * @return Effort of the degree of freedom
     */
    float(CARB_ABI* getDofEffort)(DcHandle dofHandle);

    // attractors

    /**
     * @brief Creates a rigid body attractor
     * @param[in] props Properties for the attractor
     * @return Handle to the created attractor
     */
    DcHandle(CARB_ABI* createRigidBodyAttractor)(const DcAttractorProperties* props);

    /**
     * @brief Destroys a rigid body attractor
     * @param[in] attHandle Handle to the attractor to destroy
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* destroyRigidBodyAttractor)(DcHandle attHandle);

    /**
     * @brief Gets the properties of an attractor
     * @param[in] attHandle Handle to the attractor
     * @param[out] props Attractor properties to be filled
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getAttractorProperties)(DcHandle attHandle, DcAttractorProperties* props);

    /**
     * @brief Sets the properties of an attractor
     * @param[in] attHandle Handle to the attractor
     * @param[in] props Attractor properties to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setAttractorProperties)(DcHandle attHandle, const DcAttractorProperties* props);

    /**
     * @brief Sets the target pose of an attractor
     * @param[in] attHandle Handle to the attractor
     * @param[in] target Target pose to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setAttractorTarget)(DcHandle attHandle, const DcTransform& target);

    // General D6 Joint

    /**
     * @brief Creates a D6 joint between two rigid bodies
     * @param[in] props Properties for the D6 joint
     * @return Handle to the created D6 joint
     */
    DcHandle(CARB_ABI* createD6Joint)(const DcD6JointProperties* props);

    /**
     * @brief Destroys a D6 joint
     * @param[in] jointHandle Handle to the D6 joint to destroy
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* destroyD6Joint)(DcHandle jointHandle);

    /**
     * @brief Gets the properties of a D6 joint
     * @param[in] jointHandle Handle to the D6 joint
     * @param[out] props D6 joint properties to be filled
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* getD6JointProperties)(DcHandle jointHandle, DcD6JointProperties* props);

    /**
     * @brief Checks if a D6 joint constraint is broken
     * @param[in] jointHandle Handle to the D6 joint
     * @return True if the joint constraint is broken, false otherwise
     */
    bool(CARB_ABI* getD6JointConstraintIsBroken)(DcHandle jointHandle);

    /**
     * @brief Sets the properties of a D6 joint
     * @param[in] jointHandle Handle to the D6 joint
     * @param[in] props D6 joint properties to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setD6JointProperties)(DcHandle jointHandle, const DcD6JointProperties* props);

    /**
     * @brief Sets the origin offset for a physics object
     * @param[in] handle Handle to the physics object
     * @param[in] origin Origin offset to set
     * @return True if successful, false otherwise
     */
    bool(CARB_ABI* setOriginOffset)(DcHandle handle, const carb::Float3& origin);

    /**
     * @brief Performs a raycast in the physics scene
     * @param[in] origin Origin point of the ray
     * @param[in] direction Direction of the ray
     * @param[in] max_distrance Maximum distance for the raycast
     * @return Result of the raycast
     */
    DcRayCastResult(CARB_ABI* rayCast)(const carb::Float3& origin, const carb::Float3& direction, float max_distrance);

#if 0
    DcShape(CARB_ABI* createShape)(int ndims, ...);

    DcTensor* createTensor(const DcShape& shape, DcDtype dtype);
#endif
};

}
}
}
