// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <isaacsim/core/includes/math/core/Maths.h>

#include <float.h>
#include <iostream>
#include <map>
#include <string>
#include <vector>

namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace urdf
{
// The default values and data structures are mostly the same as defined in the official URDF documentation
// http://wiki.ros.org/urdf/XML

/**
 * @brief Inertia tensor components for a rigid body.
 * @details
 * Represents the 3x3 inertia tensor in matrix form with the six unique
 * components (since the tensor is symmetric). Used to define the mass
 * distribution properties of a link for dynamics computation.
 */
struct UrdfInertia
{
    /**
     * @brief Moment of inertia about x-axis (Ixx component).
     */
    float ixx = 0.0f;

    /**
     * @brief Product of inertia xy (Ixy component).
     */
    float ixy = 0.0f;

    /**
     * @brief Product of inertia xz (Ixz component).
     */
    float ixz = 0.0f;

    /**
     * @brief Moment of inertia about y-axis (Iyy component).
     */
    float iyy = 0.0f;

    /**
     * @brief Product of inertia yz (Iyz component).
     */
    float iyz = 0.0f;

    /**
     * @brief Moment of inertia about z-axis (Izz component).
     */
    float izz = 0.0f;
};

/**
 * @brief Inertial properties of a URDF link.
 * @details
 * Contains the mass, center of mass location, and inertia tensor for a link.
 * The origin represents the pose of the inertial reference frame relative
 * to the link reference frame, with the origin at the center of gravity.
 */
struct UrdfInertial
{
    /**
     * @brief Pose of the inertial reference frame relative to link frame.
     * @details The origin must be at the center of gravity.
     */
    Transform origin; // This is the pose of the inertial reference frame, relative to the link reference frame. The
                      // origin of the inertial reference frame needs to be at the center of gravity

    /**
     * @brief Mass of the link in kilograms.
     */
    float mass = 0.0f;

    /**
     * @brief Inertia tensor components for the link.
     */
    UrdfInertia inertia;

    /**
     * @brief Whether the origin was explicitly defined in the URDF.
     */
    bool hasOrigin = false;

    /**
     * @brief Whether the mass was explicitly defined in the URDF.
     */
    bool hasMass = false; // Whether the inertial field defined a mass

    /**
     * @brief Whether the inertia was explicitly defined in the URDF.
     */
    bool hasInertia = false; // Whether the inertial field defined an inertia
};

/**
 * @brief Joint axis definition for URDF joints.
 * @details
 * Specifies the axis of rotation for revolute joints or the axis of
 * translation for prismatic joints. The axis is defined in the joint frame.
 */
struct UrdfAxis
{
    /**
     * @brief X component of the joint axis vector.
     */
    float x = 1.0f;

    /**
     * @brief Y component of the joint axis vector.
     */
    float y = 0.0f;

    /**
     * @brief Z component of the joint axis vector.
     */
    float z = 0.0f;
};

/**
 * @brief RGBA color specification for URDF materials.
 * @details
 * Represents color values for visual elements. By default, a UrdfColor
 * struct has invalid color values (negative red component) unless it
 * was explicitly defined in the XML.
 */
// By Default a UrdfColor struct will have an invalid color unless it was found in the xml
struct UrdfColor
{
    /**
     * @brief Red color component (0.0 to 1.0, or -1.0 if undefined).
     */
    float r = -1.0f;

    /**
     * @brief Green color component (0.0 to 1.0, or -1.0 if undefined).
     */
    float g = -1.0f;

    /**
     * @brief Blue color component (0.0 to 1.0, or -1.0 if undefined).
     */
    float b = -1.0f;

    /**
     * @brief Alpha (transparency) component (0.0 to 1.0).
     */
    float a = 1.0f;
};

enum class UrdfJointType
{
    REVOLUTE = 0, // A hinge joint that rotates along the axis and has a limited range specified by the upper and lower
                  // limits
    CONTINUOUS = 1, // A continuous hinge joint that rotates around the axis and has no upper and lower limits
    PRISMATIC = 2, // A sliding joint that slides along the axis, and has a limited range specified by the upper and
                   // lower limits
    FIXED = 3, // this is not really a joint because it cannot move. All degrees of freedom are locked. This type of
               // joint does not require the axis, calibration, dynamics, limits or safety_controller
    FLOATING = 4, // This joint allows motion for all 6 degrees of freedom
    PLANAR = 5, // This joint allows motion in a plane perpendicular to the axis
    SPHERICAL = 6 // This joint allows motion in all 3 rotational dimensions
};

enum class UrdfJointTargetType
{
    NONE = 0,
    POSITION = 1,
    VELOCITY = 2
};


enum class UrdfNormalSubdivisionScheme
{
    CATMULLCLARK = 0,
    LOOP = 1,
    BILINEAR = 2,
    NONE = 3
};

enum class UrdfJointDriveType
{
    ACCELERATION = 0,
    FORCE = 2
};

enum class UrdfSensorType
{
    CAMERA = 0,
    RAY = 1,
    IMU = 2,
    MAGNETOMETER = 3,
    GPS = 4,
    FORCE = 5,
    CONTACT = 6,
    SONAR = 7,
    RFIDTAG = 8,
    RFID = 9,
    UNSUPPORTED = -1,

};

/**
 * @brief Joint dynamics properties for URDF joints.
 * @details
 * Specifies the physical properties that affect joint motion including
 * damping, friction, and stiffness coefficients used in simulation.
 */
struct UrdfDynamics
{
    /**
     * @brief Damping coefficient for joint motion.
     */
    float damping = 0.0f;

    /**
     * @brief Friction coefficient for joint motion.
     */
    float friction = 0.0f;

    /**
     * @brief Stiffness coefficient for joint springs.
     */
    float stiffness = 0.0f;
};

/**
 * @brief Joint drive configuration for actuated joints.
 * @details
 * Defines the control parameters for joint actuation including target values,
 * control gains, and drive characteristics. Used for position and velocity
 * control of joints in simulation.
 */
struct UrdfJointDrive
{
    /**
     * @brief Target value for joint control (position or velocity).
     */
    float target = 0.0;

    /**
     * @brief Control strength/gain for the joint drive.
     */
    float strength = 0.0f;

    /**
     * @brief Damping coefficient for the joint drive.
     */
    float damping = 0.0f;

    /**
     * @brief Type of target control (position or velocity).
     */
    UrdfJointTargetType targetType = UrdfJointTargetType::POSITION;

    /**
     * @brief Type of drive actuation (acceleration or force).
     */
    UrdfJointDriveType driveType = UrdfJointDriveType::ACCELERATION;

    /**
     * @brief Natural frequency for control system tuning.
     * @details Default is 25Hz for stable simulation at 60Hz timestep.
     */
    float naturalFrequency = 25.0f; // Since simulation default is 60Hz, 25 puts it at slightly above 2 sim steps per
                                    // oscillation cycle, so it ensures a stable simulation

    /**
     * @brief Damping ratio for control system tuning.
     * @details Low damping allows oscillation but ensures settling.
     */
    float dampingRatio = 0.005f; // Make the system almost without damping - it may oscillate but will settle
};

/**
 * @brief Joint mimic configuration for coupled joint motion.
 * @details
 * Allows one joint to mimic the motion of another joint with a linear
 * relationship defined by multiplier and offset parameters.
 */
struct UrdfJointMimic
{
    /**
     * @brief Name of the joint to mimic.
     */
    std::string joint = "";

    /**
     * @brief Multiplier for the mimic relationship.
     */
    float multiplier;

    /**
     * @brief Offset for the mimic relationship.
     */
    float offset;
};

/**
 * @brief Joint motion limits for URDF joints.
 * @details
 * Defines the allowable range of motion, maximum effort, and maximum
 * velocity for joints. Used to constrain joint motion in simulation.
 */
struct UrdfLimit
{
    /**
     * @brief Lower joint limit (radians for revolute, meters for prismatic).
     */
    float lower = -FLT_MAX; // An attribute specifying the lower joint limit (radians for revolute joints, meters for
                            // prismatic joints)

    /**
     * @brief Upper joint limit (radians for revolute, meters for prismatic).
     */
    float upper = FLT_MAX; // An attribute specifying the upper joint limit (radians for revolute joints, meters for
                           // prismatic joints)

    /**
     * @brief Maximum joint effort (force or torque).
     */
    float effort = FLT_MAX; // An attribute for enforcing the maximum joint effort

    /**
     * @brief Maximum joint velocity.
     */
    float velocity = FLT_MAX; // An attribute for enforcing the maximum joint velocity
};

enum class UrdfGeometryType
{
    BOX = 0,
    CYLINDER = 1,
    CAPSULE = 2,
    SPHERE = 3,
    MESH = 4
};

/**
 * @brief Geometric shape definition for URDF visual and collision elements.
 * @details
 * Represents various geometric primitives and mesh assets that can be used
 * for visual rendering and collision detection. Supports boxes, cylinders,
 * capsules, spheres, and mesh files with scaling parameters.
 */
struct UrdfGeometry
{
    /**
     * @brief Type of geometric shape.
     */
    UrdfGeometryType type;
    // Box
    /**
     * @brief Box size in x-direction.
     */
    float size_x = 0.0f;

    /**
     * @brief Box size in y-direction.
     */
    float size_y = 0.0f;

    /**
     * @brief Box size in z-direction.
     */
    float size_z = 0.0f;
    // Cylinder and Sphere
    /**
     * @brief Radius for cylindrical and spherical shapes.
     */
    float radius = 0.0f;

    /**
     * @brief Length for cylindrical shapes.
     */
    float length = 0.0f;
    // Mesh
    /**
     * @brief Scale factor in x-direction for mesh geometry.
     */
    float scale_x = 1.0f;

    /**
     * @brief Scale factor in y-direction for mesh geometry.
     */
    float scale_y = 1.0f;

    /**
     * @brief Scale factor in z-direction for mesh geometry.
     */
    float scale_z = 1.0f;

    /**
     * @brief File path to mesh asset.
     */
    std::string meshFilePath;
};

/**
 * @brief Material definition for URDF visual elements.
 * @details
 * Defines the visual appearance properties including color and texture
 * for rendering visual elements in the simulation environment.
 */
struct UrdfMaterial
{
    /**
     * @brief Name identifier for the material.
     */
    std::string name;

    /**
     * @brief Color specification for the material.
     */
    UrdfColor color;

    /**
     * @brief File path to texture image for the material.
     */
    std::string textureFilePath;
};

/**
 * @brief Visual element definition for URDF links.
 * @details
 * Represents a visual component of a link including its geometry,
 * material properties, and spatial positioning for rendering purposes.
 */
struct UrdfVisual
{
    /**
     * @brief Name identifier for the visual element.
     */
    std::string name;

    /**
     * @brief Transform from link frame to visual element frame.
     */
    Transform origin; // The reference frame of the visual element with respect to the reference frame of the link

    /**
     * @brief Geometric shape of the visual element.
     */
    UrdfGeometry geometry;

    /**
     * @brief Material properties for rendering.
     */
    UrdfMaterial material;
};

/**
 * @brief Collision element definition for URDF links.
 * @details
 * Represents a collision component of a link including its geometry
 * and spatial positioning for collision detection purposes.
 */
struct UrdfCollision
{
    /**
     * @brief Name identifier for the collision element.
     */
    std::string name;

    /**
     * @brief Transform from link frame to collision element frame.
     */
    Transform origin; // The reference frame of the collision element, relative to the reference frame of the link

    /**
     * @brief Geometric shape of the collision element.
     */
    UrdfGeometry geometry;
};

/**
 * @brief Noise characteristics for sensor measurements.
 * @details
 * Defines statistical properties of noise that affects sensor readings
 * including mean, standard deviation, bias parameters, and precision.
 */
struct UrdfNoise
{
    /**
     * @brief Mean value of the noise distribution.
     */
    float mean;

    /**
     * @brief Standard deviation of the noise distribution.
     */
    float stddev;

    /**
     * @brief Mean value of the bias component.
     */
    float biasMean;

    /**
     * @brief Standard deviation of the bias component.
     */
    float biasStddev;

    /**
     * @brief Precision of the sensor measurements.
     */
    float precision;
};

/**
 * @brief Base sensor definition for URDF sensors.
 * @details
 * Provides common properties for all sensor types including name,
 * pose, type identification, and update rate configuration.
 */
struct UrdfSensor
{
    /**
     * @brief Name identifier for the sensor.
     */
    std::string name;

    /**
     * @brief Transform from link frame to sensor frame.
     */
    Transform origin;

    /**
     * @brief Type of sensor (camera, lidar, IMU, etc.).
     */
    UrdfSensorType type;

    /**
     * @brief Unique identifier for the sensor.
     */
    std::string id;

    /**
     * @brief Update rate of the sensor in Hz.
     */
    float updateRate;
};

/**
 * @brief Camera sensor configuration extending base sensor.
 * @details
 * Defines camera-specific properties for visual sensors including
 * image dimensions, field of view, and rendering parameters.
 */
struct UrdfCamera : public UrdfSensor
{
    /**
     * @brief Image width in pixels.
     */
    float width;

    /**
     * @brief Image height in pixels.
     */
    float height;

    /**
     * @brief Image format specification.
     */
    std::string format;

    /**
     * @brief Horizontal field of view in radians.
     */
    float hfov;

    /**
     * @brief Near clipping plane distance.
     */
    float clipNear;

    /**
     * @brief Far clipping plane distance.
     */
    float clipFar;
};

/**
 * @brief Ray dimension configuration for lidar sensors.
 * @details
 * Defines the sampling parameters for a single dimension (horizontal or vertical)
 * of a ray-based sensor including sample count, resolution, and angular range.
 */
struct UrdfRayDim
{
    /**
     * @brief Number of ray samples in this dimension.
     */
    size_t samples;

    /**
     * @brief Angular resolution between samples.
     */
    float resolution;

    /**
     * @brief Minimum angle of the scanning range.
     */
    float minAngle;

    /**
     * @brief Maximum angle of the scanning range.
     */
    float maxAngle;
};

/**
 * @brief Ray-based sensor configuration for lidar/laser scanners.
 * @details
 * Defines properties for ray-casting sensors including horizontal and vertical
 * scanning dimensions and Isaac Sim specific configuration parameters.
 */
struct UrdfRay : public UrdfSensor
{
    /**
     * @brief Whether horizontal scanning dimension is configured.
     */
    bool hasHorizontal = false;

    /**
     * @brief Whether vertical scanning dimension is configured.
     */
    bool hasVertical = false;

    /**
     * @brief Horizontal scanning dimension parameters.
     */
    UrdfRayDim horizontal;

    /**
     * @brief Vertical scanning dimension parameters.
     */
    UrdfRayDim vertical;

    /**
     * @brief Isaac Sim specific configuration string.
     */
    std::string isaacSimConfig;
    // float min;
    // float max;
    // float resolution;
};

/**
 * @brief Inertial measurement unit sensor configuration.
 * @details
 * Defines IMU sensor properties including noise characteristics for
 * gyroscope and accelerometer measurements.
 */
struct UrdfImu : public UrdfSensor
{
    /**
     * @brief Noise characteristics for gyroscope measurements.
     */
    UrdfNoise gyroNoise;

    /**
     * @brief Noise characteristics for accelerometer measurements.
     */
    UrdfNoise accelerationNoise;
};

/**
 * @brief Magnetometer sensor configuration.
 * @details
 * Defines magnetometer sensor properties including noise characteristics
 * for magnetic field measurements.
 */
struct UrdfMagnetometer : public UrdfSensor
{
    /**
     * @brief Noise characteristics for magnetometer measurements.
     */
    UrdfNoise noise;
};

/**
 * @brief GPS sensor configuration.
 * @details
 * Defines GPS sensor properties including noise characteristics for
 * position and velocity measurements.
 */
struct UrdfGps : public UrdfSensor
{
    /**
     * @brief Noise characteristics for position measurements.
     */
    UrdfNoise positionNoise;

    /**
     * @brief Noise characteristics for velocity measurements.
     */
    UrdfNoise velocityNoise;
};

/**
 * @brief Force sensor configuration.
 * @details
 * Defines force sensor properties including the reference frame and
 * measurement direction for force/torque sensing.
 */
struct UrdfForce : public UrdfSensor
{
    /**
     * @brief The child element frame to measure force relative to.
     */
    std::string frame; // the child element to measure force

    /**
     * @brief Direction of force measurement (0: parent_to_child, 1: child_to_parent).
     */
    int measureDirection; // 0 is parent_to_child, 1 is child_to_parent
};

/**
 * @brief Contact sensor configuration.
 * @details
 * Defines contact sensor properties including the collision elements
 * that are monitored for contact detection.
 */
struct UrdfContact : public UrdfSensor
{
    /**
     * @brief Collision elements monitored for contact detection.
     */
    std::vector<UrdfCollision> collision;
};

/**
 * @brief Sonar sensor configuration.
 * @details
 * Defines sonar sensor properties including range limits and
 * detection radius for ultrasonic distance sensing.
 */
struct UrdfSonar : public UrdfSensor
{
    /**
     * @brief Minimum detection range.
     */
    float min;

    /**
     * @brief Maximum detection range.
     */
    float max;

    /**
     * @brief Detection radius/beam width.
     */
    float radius;
};

/**
 * @brief RFID tag sensor configuration.
 * @details
 * Defines RFID tag sensor properties for radio frequency identification
 * tag detection and reading.
 */
struct UrdfRfidTag : public UrdfSensor
{
};

/**
 * @brief RFID reader sensor configuration.
 * @details
 * Defines RFID reader sensor properties for radio frequency identification
 * tag detection and communication.
 */
struct UrdfRfid : public UrdfSensor
{
};

/**
 * @brief Link definition in URDF robot model.
 * @details
 * Represents a rigid body in the robot with inertial properties, visual elements,
 * collision geometry, sensors, and hierarchical relationships to other links.
 */
struct UrdfLink
{
    /**
     * @brief Name identifier for the link.
     */
    std::string name;

    /**
     * @brief Inertial properties of the link.
     */
    UrdfInertial inertial;

    /**
     * @brief Visual elements for rendering the link.
     */
    std::vector<UrdfVisual> visuals;

    /**
     * @brief Collision elements for physics simulation.
     */
    std::vector<UrdfCollision> collisions;

    /**
     * @brief Transforms of merged child links (for fixed joint optimization).
     */
    std::map<std::string, Transform> mergedChildren;

    /**
     * @brief Camera sensors attached to this link.
     */
    std::vector<UrdfCamera> cameras;

    /**
     * @brief Lidar sensors attached to this link.
     */
    std::vector<UrdfRay> lidars;

    /**
     * @brief Name of the parent link in the kinematic tree.
     */
    std::string parentLink;

    /**
     * @brief Names of child links in the kinematic tree.
     */
    std::vector<std::string> childrenLinks;

    // std::vector<UrdfMagnetometer> magnetometers;
    // std::vector<UrdfImu> Imus;
    // std::vector<UrdfGps> Gps;
    // std::vector<UrdfForce> forceSensors;
    // std::vector<UrdfContact> contactSensors;
    // std::vector<UrdfSonar> sonars;
    // std::vector<UrdfRfid> rfids;
    // std::vector<UrdfRfidTag> rfdidTags;
};

/**
 * @brief Joint definition connecting two links in URDF robot model.
 * @details
 * Represents a kinematic joint between parent and child links with motion constraints,
 * dynamics properties, control parameters, and hierarchical relationships.
 */
struct UrdfJoint
{
    /**
     * @brief Name identifier for the joint.
     */
    std::string name;

    /**
     * @brief Type of joint (revolute, prismatic, fixed, etc.).
     */
    UrdfJointType type;

    /**
     * @brief Transform from parent link to child link frame.
     * @details The joint is located at the origin of the child link.
     */
    Transform origin; // This is the transform from the parent link to the child link. The joint is located at the
                      // origin of the child link

    /**
     * @brief Name of the parent link.
     */
    std::string parentLinkName;

    /**
     * @brief Name of the child link.
     */
    std::string childLinkName;

    /**
     * @brief Axis of rotation or translation for the joint.
     */
    UrdfAxis axis;

    /**
     * @brief Dynamics properties (damping, friction, stiffness).
     */
    UrdfDynamics dynamics;

    /**
     * @brief Motion limits for the joint.
     */
    UrdfLimit limit;

    /**
     * @brief Drive configuration for joint actuation.
     */
    UrdfJointDrive drive;

    /**
     * @brief Mimic configuration for coupled joint motion.
     */
    UrdfJointMimic mimic;

    /**
     * @brief Map of child joints that mimic this joint with their multipliers.
     */
    std::map<std::string, float> mimicChildren;

    /**
     * @brief Natural stiffness used for auto-configuring position control gains.
     */
    float naturalStiffness; // Used to auto-configure position control gains

    /**
     * @brief Joint inertia used for auto-configuring position control gains.
     */
    float jointInertia; // Used to auto-configure position control gains

    /**
     * @brief Custom attribute to prevent fixed joint merging.
     * @details
     * Prevents the child link from being collapsed into the parent link when
     * fixed joint merging is enabled. Useful for sensor or end-effector frames.
     * This is a custom Isaac Gym extension, not part of standard URDF.
     */
    bool dontCollapse = false; // This is a custom attribute that is used to prevent the child link from being
                               // collapsed into the parent link when a fixed joint is used. It is used when user
                               // enables "merging of fixed joints" but does not want to merge this particular joint.
                               // For example: for sensor or end-effector frames.
                               // Note: The tag is not part of the URDF specification. Rather it is a custom tag
                               //   that was first introduced in Isaac Gym for the purpose of merging fixed joints.

    /**
     * @brief Name of the parent joint in the kinematic tree.
     */
    std::string parentJoint;

    /**
     * @brief Names of child joints in the kinematic tree.
     */
    std::vector<std::string> childrenJoints;
};

/**
 * @brief Loop joint definition for closed kinematic chains.
 * @details
 * Represents a joint that creates a closed loop in the kinematic structure
 * by connecting two links that are already connected through other joints.
 */
struct UrdfLoopJoint
{
    /**
     * @brief Name identifier for the loop joint.
     */
    std::string name;

    /**
     * @brief Type of joint creating the loop closure.
     */
    UrdfJointType type;

    /**
     * @brief Names of the two links connected by the loop joint.
     */
    std::string linkName[2];

    /**
     * @brief Poses of the connection points on each link.
     */
    Transform linkPose[2];
};

/**
 * @brief Complete URDF robot model definition.
 * @details
 * Represents the entire robot model containing all links, joints, materials,
 * and metadata. Serves as the root container for the robot description.
 */
struct UrdfRobot
{
    /**
     * @brief Name identifier for the robot.
     */
    std::string name;

    /**
     * @brief Name of the root link in the kinematic tree.
     */
    std::string rootLink;

    /**
     * @brief File path to the original URDF file.
     */
    std::string urdfPath;

    /**
     * @brief Root directory for resolving relative asset paths.
     */
    std::string assetRoot;

    /**
     * @brief Map of all links in the robot indexed by name.
     */
    std::map<std::string, UrdfLink> links;

    /**
     * @brief Map of all joints in the robot indexed by name.
     */
    std::map<std::string, UrdfJoint> joints;

    /**
     * @brief Map of all loop joints in the robot indexed by name.
     */
    std::map<std::string, UrdfLoopJoint> loopJoints;

    /**
     * @brief Map of all materials in the robot indexed by name.
     */
    std::map<std::string, UrdfMaterial> materials;
};

} // namespace urdf
}
}
}
