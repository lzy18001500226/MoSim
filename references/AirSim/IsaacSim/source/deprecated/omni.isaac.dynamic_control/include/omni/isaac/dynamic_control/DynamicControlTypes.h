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

#include <carb/Defines.h>
#include <carb/Types.h>

#include <limits>

namespace omni
{
namespace isaac
{
namespace dynamic_control
{
/**
 * @brief Handle type for dynamic control objects
 * @details Used to reference physics objects such as rigid bodies, joints, DOFs, articulations, etc.
 */
using DcHandle = uint64_t;

/**
 * @brief Invalid handle constant
 * @details Used to indicate an invalid or uninitialized handle
 */
constexpr DcHandle kDcInvalidHandle = DcHandle(0);

/**
 * @enum DcObjectType
 * @brief Types of objects that can be controlled via dynamic control
 */
enum DcObjectType : uint32_t
{
    eDcObjectNone, //!< No object/invalid object type
    eDcObjectRigidBody, //!< Rigid body object
    eDcObjectJoint, //!< Joint object
    eDcObjectDof, //!< Degree of freedom object
    eDcObjectArticulation, //!< Articulation object
    eDcObjectAttractor, //!< Attractor object
    eDcObjectD6Joint, //!< D6 joint object

    kDcObjectTypeCount //!< Total number of object types
};

/// Transform
/**
 * @brief Represents a pose (e.g. of a rigid body)
 * @details Contains position and rotation information for an object in 3D space
 */
struct DcTransform
{
    carb::Float3 p{ 0.0f, 0.0f, 0.0f }; //!< Position, in meters
    carb::Float4 r{ 0.0f, 0.0f, 0.0f, 1.0f }; //!< Rotation Quaternion, represented in the format x*i + y*j +
                                              //!< z*k + w
};

/// Velocity
/**
 * @brief Holds linear and angular velocities, in $m/s$ and $radians/s$
 * @details Used to represent the complete velocity state of a rigid body
 */
struct DcVelocity
{
    carb::Float3 linear{ 0.0f, 0.0f, 0.0f }; //!< Linear velocity component
    carb::Float3 angular{ 0.0f, 0.0f, 0.0f }; //!< angular velocity component
};

// useful constants

/**
 * @brief Zero vector constant
 * @details Represents a 3D vector with all components set to zero
 */
constexpr carb::Float3 kFloat3Zero = { 0.0f, 0.0f, 0.0f };

/**
 * @brief Identity quaternion constant
 * @details Represents a quaternion with no rotation (identity)
 */
constexpr carb::Float4 kQuatIdentity = { 0.0f, 0.0f, 0.0f, 1.0f };

/**
 * @brief Zero quaternion constant
 * @details Represents a quaternion with all components set to zero (not a valid rotation)
 */
constexpr carb::Float4 kQuatZero = { 0.0f, 0.0f, 0.0f, 0.0f };

/**
 * @brief Identity transform constant
 * @details Represents a transform with no translation and no rotation
 */
constexpr DcTransform kTransformIdentity = { kFloat3Zero, kQuatIdentity };

/**
 * @brief Zero transform constant
 * @details Represents a transform with no translation and identity rotation
 */
constexpr DcTransform kTransformZero = { kFloat3Zero, kQuatIdentity };

/**
 * @brief Zero velocity constant
 * @details Represents a velocity with no linear or angular components
 */
constexpr DcVelocity kVelocityZero{ kFloat3Zero, kFloat3Zero };

/** @defgroup DcStateFlags Dynamic Control State Flags
 * States that can be get/set from Degrees of Freedom and Rigid Bodies
 * @{
 */
/**
 * @brief Type for state flags
 * @details Used to specify which state components to get or set
 */
using DcStateFlags = int;
constexpr DcStateFlags kDcStateNone = 0; //!< No state selected
constexpr DcStateFlags kDcStatePos = 1 << 0; //!< Position states
constexpr DcStateFlags kDcStateVel = 1 << 1; //!< Velocity states
constexpr DcStateFlags kDcStateEffort = 1 << 2; //!< Forces/Torques states
constexpr DcStateFlags kDcStateAll = (kDcStatePos | kDcStateVel | kDcStateEffort); //!< All states
/** @} */ // end of DcStateFlags group

/// Drive modes for degrees-of-freedom.
/**
 * @brief Drive modes for degrees-of-freedom
 * @details A DoF that is set on a specific drive mode will ignore drive target
 * commands sent for a different mode.
 * Joint limits, if they exist, will still be enforced.
 */
enum class DcDriveMode : int32_t
{
    eForce, //!< The output of the implicit spring drive controller is a force/torque.
    eAcceleration, //!< The output of the implicit spring drive controller is a joint acceleration (use this to get
                   //!< (spatial)-inertia-invariant behavior of the drive).
};

/**
 * @brief Result of a Raycast
 * @details Contains information about a raycast hit, including the hit object and distance
 */
struct DcRayCastResult
{
    bool hit; //!< an object was hit
    DcHandle rigidBody; //!< which object was hit
    float distance; //!< distance to object surface from raycast source
};

/**
 * @brief State of a rigid body
 * @details Contains the pose and velocity of a rigid body
 */
struct DcRigidBodyState
{
    DcTransform pose; //!< Transform with position and orientation of rigid body
    DcVelocity vel; //!< Set of angular and linear velocities of rigid body
};

/**
 * @brief State of a degree of freedom
 * @details Contains the position, velocity, and effort of a degree of freedom
 */
struct DcDofState
{
    float pos; //!< DOF position, in radians if it's a revolute DOF, or meters, if it's a prismatic DOF
    float vel; //!< DOF velocity, in radians/s if it's a revolute DOF, or m/s, if it's a prismatic DOF
    float effort; //!< DOF effort, torque if it's a revolute DOF, or force if it's a prismatic DOF
};

/// Types of joint
/**
 * @brief Types of joint
 * @details Defines the different types of joints that can be created
 */
enum class DcJointType : int32_t
{
    eNone, //!< invalid/unknown/uninitialized joint type
    eFixed, //!< Fixed joint with no degrees of freedom
    eRevolute, //!< Revolute joint with one rotational degree of freedom
    ePrismatic, //!< Prismatic joint with one translational degree of freedom
    eSpherical, //!< Spherical joint with three rotational degrees of freedom
};

/// Types of degree of freedom
/**
 * @brief Types of degree of freedom
 * @details Defines the different types of degrees of freedom
 */
enum class DcDofType : int32_t
{
    eNone, //!< invalid/unknown/uninitialized DOF type
    eRotation, //!< The degrees of freedom correspond to a rotation between bodies
    eTranslation, //!< The degrees of freedom correspond to a translation between bodies.
};

/**
 * @brief Properties of an articulation
 * @details Contains settings that control the behavior of an articulation
 */
struct DcArticulationProperties
{

    // float stabilizationThreshold = 10.0;
    // float sleepThreshold = 50.0;
    uint32_t solverPositionIterationCount = 32; //!< Number of position iterations for the solver
    uint32_t solverVelocityIterationCount = 1; //!< Number of velocity iterations for the solver
    bool enableSelfCollisions = false; //!< Whether to enable self-collisions within the articulation
};

/**
 * @brief Properties of a rigid body
 * @details Contains settings that control the behavior of a rigid body
 */
struct DcRigidBodyProperties
{
    float mass; //!< Mass of the rigid body
    carb::Float3 moment; //!< Moment of inertia of the rigid body
    carb::Float3 cMassLocalPose; //!< Local pose of the center of mass
    float maxDepenetrationVelocity = std::numeric_limits<float>::max(); //!< Maximum velocity used for depenetration
    float maxContactImpulse = std::numeric_limits<float>::max(); //!< Maximum impulse that can be applied at a contact
    uint32_t solverPositionIterationCount = 16; //!< Number of position iterations for the solver
    uint32_t solverVelocityIterationCount = 1; //!< Number of velocity iterations for the solver
    // float stabilizationThreshold = 10.0;
    // bool enableSpeculativeCCD = false;
    // bool enableGyroscopicForces = true;
    // bool retainAccelerations = false;
};
/**
 * @brief Properties of a degree-of-freedom
 * @details Contains settings that control the behavior of a degree of freedom
 */
struct DcDofProperties
{
    DcDofType type = DcDofType::eNone; //!< Type of dof (read-only property)

    bool hasLimits = false; //!< Flags whether the DOF has limits. (read-only property)
    float lower = 0.0f; //!< lower limit of DOF. In radians or meters (read-only property)
    float upper = 0.0f; //!< upper limit of DOF. In radians or meters (read-only property)

    DcDriveMode driveMode = DcDriveMode::eAcceleration; //!< Drive mode for the DOF. See DcDriveMode.
    float maxVelocity = std::numeric_limits<float>::max(); //!< Maximum velocity of DOF. In Radians/s, or m/s
    float maxEffort = std::numeric_limits<float>::max(); //!< Maximum effort of DOF. in N or Nm.
    float stiffness = 0.0f; //!< Stiffness of DOF.
    float damping = 0.0f; //!< Damping of DOF.
};

/** @defgroup DcAxisFlags transform axis flags
 * Flags for Axes used in Attractor setup
 * @{
 */
/**
 * @brief Type for axis flags
 * @details Used to specify which axes to affect in attractors and joints
 */
using DcAxisFlags = int;
constexpr DcAxisFlags kDcAxisNone = 0; //!< No axis selected
constexpr DcAxisFlags kDcAxisX = (1 << 0); //!< Corresponds to translation around the body x-axis
constexpr DcAxisFlags kDcAxisY = (1 << 1); //!< Corresponds to translation around the body y-axis
constexpr DcAxisFlags kDcAxisZ = (1 << 2); //!< Corresponds to translation around the body z-axis
constexpr DcAxisFlags kDcAxisTwist = (1 << 3); //!< Corresponds to rotation around the body x-axis
constexpr DcAxisFlags kDcAxisSwing1 = (1 << 4); //!< Corresponds to rotation around the body y-axis
constexpr DcAxisFlags kDcAxisSwing2 = (1 << 5); //!< Corresponds to rotation around the body z-axis
constexpr DcAxisFlags kDcAxisAllTranslation = kDcAxisX | kDcAxisY | kDcAxisZ; //!< Corresponds to all Translation axes
constexpr DcAxisFlags kDcAxisAllRotation = kDcAxisTwist | kDcAxisSwing1 | kDcAxisSwing2; //!< Corresponds to all
                                                                                         //!< Rotation axes
constexpr DcAxisFlags kDcAxisAll = kDcAxisAllTranslation | kDcAxisAllRotation; //!< Corresponds to all axes
/** @} */ // end of group DcAxisFlags

/// Properties to set up a pose attractor
/**
 * @brief Properties to set up a pose attractor
 * @details The Attractor is used to pull a rigid body towards a pose. Each pose axis can be individually selected.
 */
struct DcAttractorProperties
{
    DcHandle rigidBody = kDcInvalidHandle; //!< Rigid body to set the attractor to
    DcAxisFlags axes = 0; //!< Axes to set the attractor, using DcTransformAxesFlags. Multiple axes can be selected
                          //!< using bitwise combination of each axis flag. if axis flag is set to zero, the attractor
                          //!< will be disabled and won't impact in solver computational complexity.
    DcTransform target{ kTransformIdentity }; //!< Target pose to attract to.
    DcTransform offset{ kTransformIdentity }; //!< Offset from rigid body origin to set the attractor pose.
    float stiffness = 1e5f; //!< Stiffness to be used on attraction for solver. Stiffness value should be larger than
                            //!< the largest agent kinematic chain stifness
    float damping = 1e3f; //!< Damping to be used on attraction solver.
    float forceLimit = std::numeric_limits<float>::max(); //!< Maximum force to be applied by drive
};

/// Properties to set up a D6 Joint
/**
 * @brief Properties to set up a D6 Joint
 * @details The Joint is used to connect two rigid bodies.
 */
struct DcD6JointProperties
{
    char* name{ nullptr }; //!< Name of the joint
    DcHandle body0 = kDcInvalidHandle; //!< Rigid body to set the joint to
    DcHandle body1 = kDcInvalidHandle; //!< Rigid body to set the joint to
    DcAxisFlags axes = kDcAxisNone; //!< Joint Axes, using DcTransformAxesFlags. Multiple axes can be selected
                                    //!< using bitwise combination of each axis flag. if axis flag is set to zero, the
                                    //!< joint will be disabled and won't impact in solver computational complexity.
    DcTransform pose0{ kTransformIdentity }; //!< Offset from Rigid Body 0 to Joint.
    DcTransform pose1{ kTransformIdentity }; //!< Offset from Rigid Body 1 to Joint.
    DcJointType jointType; //!< Joint type being defined
    bool hasLimits[6]; //!< Flag for determining if joint has limits or is locked
    bool softLimit{ true }; //!< Whether joint limits are progressively harder (soft limits) or rigid
    float lowerLimit; //!< lower joint limit, same for all axes
    float upperLimit; //!< upper joint limit, same for all axes
    float limitStiffness{ 1e5f }; //!< Joint Stiffness
    float limitDamping = { 1e3f }; //!< Joint Damping
    float stiffness = { 1e5f }; //!< Joint Stiffness
    float damping = { 1e3f }; //!< Joint Damping
    float forceLimit = std::numeric_limits<float>::max(); //!< Joint Breaking Force
    float torqueLimit = std::numeric_limits<float>::max(); //!< Joint Breaking torque
};

/////////////////////////////

/**
 * @brief Maximum number of dimensions for a shape
 */
constexpr int kMaxDims = 8;

/**
 * @brief Shape descriptor for tensors
 * @details Describes the dimensions of a tensor
 */
struct DcShape
{
    int ndims = 0; //!< Number of dimensions
    int dims[kMaxDims] = { 0 }; //!< Size of each dimension
};

/**
 * @brief Data types for tensors
 */
enum class DcDtype
{
    kVoid, //!< Void data type
    kFloat32, //!< 32-bit floating point data type
};

/**
 * @brief Forward declaration of tensor structure
 */
struct DcTensor;

/**
 * @brief Forward declaration of actuator structure
 */
struct DcActuator;

/**
 * @brief Forward declaration of actuator group structure
 */
struct DcActuatorGroup;

}
}
}
