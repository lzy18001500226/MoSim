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

#include <isaacsim/asset/importer/mjcf/Mesh.h>
#include <isaacsim/core/includes/math/core/Maths.h>

#include <set>
#include <vector>

namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace mjcf
{

typedef unsigned int TriangleMeshHandle;
typedef int64_t GymMeshHandle;

/**
 * @brief Information about a mesh used in the MJCF model.
 * @details
 * Contains pointers and handles to mesh data structures used for
 * collision detection and rendering in the physics simulation.
 */
struct MeshInfo
{
    /**
     * @brief Pointer to the mesh data structure.
     */
    Mesh* mesh = nullptr;

    /**
     * @brief Handle to the triangle mesh for collision detection.
     */
    TriangleMeshHandle meshId = -1;

    /**
     * @brief Handle to the mesh in the physics simulation.
     */
    GymMeshHandle meshHandle = -1;
};

/**
 * @brief A node in the contact graph representing collision relationships.
 * @details
 * Represents a body or geometry in the contact filtering graph, storing
 * its name and connections to adjacent nodes for collision filtering purposes.
 */
struct ContactNode
{
    /**
     * @brief Name of the contact node (typically body or geometry name).
     */
    std::string name;

    /**
     * @brief Set of indices of adjacent nodes in the contact graph.
     */
    std::set<int> adjacentNodes;
};

/**
 * @brief Equality constraint that connects two bodies at a fixed relative position.
 * @details
 * Represents an equality constraint in MJCF that constrains two bodies to maintain
 * a fixed relative position and orientation. This is used to create rigid connections
 * between bodies in the simulation.
 */
struct MJCFEqualityConnect
{
public:
    /**
     * @brief Name of the first body in the constraint.
     */
    std::string body1;

    /**
     * @brief Name of the second body in the constraint.
     */
    std::string body2;

    /**
     * @brief Anchor point for the constraint connection.
     */
    Vec3 anchor;
};

/**
 * @brief Represents a joint in the MJCF (MuJoCo XML Format) model.
 * @details
 * Defines a kinematic joint that connects two bodies with specified degrees of freedom.
 * Supports various joint types including hinge (revolute), slide (prismatic), ball (spherical),
 * and free joints with configurable limits, dynamics, and control parameters.
 */
class MJCFJoint
{
public:
    /**
     * @brief Enumeration of joint types supported in MJCF.
     */
    enum Type
    {
        /**
         * @brief Revolute joint with rotation about a single axis.
         */
        HINGE,

        /**
         * @brief Prismatic joint with translation along a single axis.
         */
        SLIDE,

        /**
         * @brief Ball joint with rotation about all three axes.
         */
        BALL,

        /**
         * @brief Free joint with translation and rotation in all directions.
         */
        FREE,
    };

    /**
     * @brief Name identifier for the joint.
     */
    std::string name;

    /**
     * @brief Type of the joint (hinge, slide, ball, or free).
     */
    Type type = HINGE;

    /**
     * @brief Whether the joint has motion limits.
     */
    bool limited;

    /**
     * @brief Armature inertia for numerical stability.
     */
    float armature;
    // dynamics
    /**
     * @brief Stiffness coefficient for joint springs.
     */
    float stiffness;

    /**
     * @brief Damping coefficient for joint friction.
     */
    float damping;

    /**
     * @brief Dry friction force magnitude.
     */
    float friction;

    // axis
    /**
     * @brief Axis of rotation or translation for the joint.
     */
    Vec3 axis;

    /**
     * @brief Reference angle or position for the joint.
     */
    float ref;

    /**
     * @brief Position offset for the joint in the parent body frame.
     */
    Vec3 pos; // aka origin's position: origin is {position, quat}
    // limits
    /**
     * @brief Joint motion limits [lower, upper].
     */
    Vec2 range; // lower to upper joint limit

    /**
     * @brief Force limits [lower, upper] for the joint.
     */
    Vec2 forcerange = { 0.0f, 0.0f };

    /**
     * @brief Velocity limits for each degree of freedom.
     */
    float velocityLimits[6];

    /**
     * @brief Initial value for the joint position or angle.
     */
    float initVal;

    MJCFJoint()
    {
        armature = 0.0f;
        damping = 0.0f;
        limited = false;
        axis = Vec3(1.0f, 0.0f, 0.0f);
        name = "";

        pos = Vec3(0.0f, 0.0f, 0.0f);
        range = Vec2(0.0f, 0.0f);
        stiffness = 0.0f;
        friction = 0.0f;
        type = HINGE;

        ref = 0.0f;
        initVal = 0.0f;
    }
};

/**
 * @brief Base class for visual elements in MJCF models.
 * @details
 * Represents a geometric shape that can be rendered visually in the simulation.
 * Contains basic properties like name, material, color, size, and shape type
 * that are common to all visual geometry elements.
 */
class MJCFVisualElement
{
public:
    /**
     * @brief Enumeration of geometric shape types for visual elements.
     */
    enum Type
    {
        /**
         * @brief Capsule shape (cylinder with hemispherical caps).
         */
        CAPSULE,

        /**
         * @brief Sphere shape.
         */
        SPHERE,

        /**
         * @brief Ellipsoid shape.
         */
        ELLIPSOID,

        /**
         * @brief Cylinder shape.
         */
        CYLINDER,

        /**
         * @brief Box (rectangular cuboid) shape.
         */
        BOX,

        /**
         * @brief Mesh shape loaded from file.
         */
        MESH,

        /**
         * @brief Infinite plane shape.
         */
        PLANE,

        /**
         * @brief Other or unspecified shape type.
         */
        OTHER
    };

    /**
     * @brief Name identifier for the visual element.
     */
    std::string name;

    /**
     * @brief Name of the material applied to this element.
     */
    std::string material;

    /**
     * @brief RGBA color values [red, green, blue, alpha].
     */
    Vec4 rgba;

    /**
     * @brief Size dimensions of the geometric shape.
     */
    Vec3 size;

    /**
     * @brief Type of geometric shape for this visual element.
     */
    Type type;
};

/**
 * @brief Geometry element for collision detection and physics simulation.
 * @details
 * Extends MJCFVisualElement with physical properties needed for collision detection
 * and contact dynamics. Contains material properties, contact parameters, friction
 * coefficients, and spatial positioning information.
 */
class MJCFGeom : public MJCFVisualElement
{
public:
    /**
     * @brief Mass density of the geometry material.
     */
    float density;

    /**
     * @brief Contact affinity bitmask for collision filtering.
     */
    int conaffinity;

    /**
     * @brief Number of contact dimensions (1-6).
     */
    int condim;

    /**
     * @brief Contact type bitmask for collision filtering.
     */
    int contype;

    /**
     * @brief Contact margin for collision detection.
     */
    float margin;

    /**
     * @brief Friction coefficients [sliding, torsional, rolling].
     */
    Vec3 friction;

    /**
     * @brief Constraint solver impedance parameters.
     */
    Vec3 solimp;

    /**
     * @brief Constraint solver reference parameters.
     */
    Vec2 solref;

    /**
     * @brief Start point for geometry shapes defined by two points.
     */
    Vec3 from;

    /**
     * @brief End point for geometry shapes defined by two points.
     */
    Vec3 to;

    /**
     * @brief Position offset in the parent body frame.
     */
    Vec3 pos;

    /**
     * @brief Quaternion orientation relative to parent body.
     */
    Quat quat;

    /**
     * @brief Axis-angle representation of orientation.
     */
    Vec4 axisangle;

    /**
     * @brief Z-axis direction for orientation specification.
     */
    Vec3 zaxis;

    /**
     * @brief Name of the mesh file for mesh geometry types.
     */
    std::string mesh;

    /**
     * @brief Whether the geometry is defined by from-to points.
     */
    bool hasFromTo;

    MJCFGeom()
    {
        conaffinity = 1;
        condim = 3;
        contype = 1;
        margin = 0.0f;
        friction = Vec3(1.0f, 0.005f, 0.0001f);

        material = "";
        rgba = Vec4(0.5f, 0.5f, 0.5f, 1.0f);

        solimp = Vec3(0.9f, 0.95f, 0.001f);
        solref = Vec2(0.02f, 1.0f);

        from = Vec3(0.0f, 0.0f, 0.0f);
        to = Vec3(0.0f, 0.0f, 0.0f);
        size = Vec3(1.0f, 1.0f, 1.0f);

        name = "";

        pos = Vec3(0.0f, 0.0f, 0.0f);
        type = MJCFVisualElement::SPHERE;
        density = 1000.0f;

        quat = Quat();
        hasFromTo = false;
    }
};

/**
 * @brief Site element for marking specific locations and orientations in the model.
 * @details
 * Sites are special objects that mark locations and orientations but do not participate
 * in collisions or dynamics. They are commonly used for sensors, cameras, or as
 * attachment points for other elements.
 */
class MJCFSite : public MJCFVisualElement
{
public:
    /**
     * @brief Enumeration of geometric shape types for site visualization.
     */
    enum Type
    {
        /**
         * @brief Capsule shape (cylinder with hemispherical caps).
         */
        CAPSULE,

        /**
         * @brief Sphere shape.
         */
        SPHERE,

        /**
         * @brief Ellipsoid shape.
         */
        ELLIPSOID,

        /**
         * @brief Cylinder shape.
         */
        CYLINDER,

        /**
         * @brief Box (rectangular cuboid) shape.
         */
        BOX
    };

    /**
     * @brief Group identifier for site organization.
     */
    int group;

    /**
     * @brief Friction coefficients for the site.
     */
    Vec3 friction;

    /**
     * @brief Start point for sites defined by two points.
     */
    Vec3 from;

    /**
     * @brief End point for sites defined by two points.
     */
    Vec3 to;

    /**
     * @brief Whether the site is defined by from-to points.
     */
    bool hasFromTo;

    /**
     * @brief Position offset in the parent body frame.
     */
    Vec3 pos;

    /**
     * @brief Quaternion orientation relative to parent body.
     */
    Quat quat;

    /**
     * @brief Z-axis direction for orientation specification.
     */
    Vec3 zaxis;

    /**
     * @brief Whether the site has associated geometry for visualization.
     */
    bool hasGeom;

    MJCFSite()
    {
        group = 0;

        material = "";
        rgba = Vec4(0.5f, 0.5f, 0.5f, 1.0f);

        from = Vec3(0.0f, 0.0f, 0.0f);
        to = Vec3(0.0f, 0.0f, 0.0f);
        size = Vec3(0.005f, 0.005f, 0.005f);
        hasFromTo = false;

        name = "";

        pos = Vec3(0.0f, 0.0f, 0.0f);
        type = MJCFVisualElement::SPHERE;
        quat = Quat();
        hasGeom = true;
    }
};

/**
 * @brief Inertial properties of a body in the MJCF model.
 * @details
 * Defines the mass distribution and inertial properties of a rigid body.
 * Contains mass, center of mass position, and moment of inertia tensor
 * information needed for dynamics computation.
 */
class MJCFInertial
{
public:
    /**
     * @brief Total mass of the body.
     */
    float mass;

    /**
     * @brief Position of the center of mass relative to the body frame.
     */
    Vec3 pos;

    /**
     * @brief Diagonal elements of the inertia tensor.
     */
    Vec3 diaginertia;

    /**
     * @brief Principal axes orientation as a quaternion.
     */
    Quat principalAxes;

    /**
     * @brief Whether the full inertia tensor is specified.
     */
    bool hasFullInertia;

    MJCFInertial()
    {
        mass = -1.0f;
        pos = Vec3(0.0f, 0.0f, 0.0f);
        diaginertia = Vec3(0.0f, 0.0f, 0.0f);
        principalAxes = Quat();
        hasFullInertia = false;
    }
};

enum JointAxis
{
    eJointAxisX, //!< Corresponds to translation around the body0 x-axis
    eJointAxisY, //!< Corresponds to translation around the body0 y-axis
    eJointAxisZ, //!< Corresponds to translation around the body0 z-axis
    eJointAxisTwist, //!< Corresponds to rotation around the body0 x-axis
    eJointAxisSwing1, //!< Corresponds to rotation around the body0 y-axis
    eJointAxisSwing2, //!< Corresponds to rotation around the body0 z-axis
};

/**
 * @brief Represents a rigid body in the MJCF model hierarchy.
 * @details
 * A body is the fundamental element in the kinematic tree that can contain
 * geometry for collision/visualization, joints for articulation, sites for
 * sensors, and child bodies for hierarchical structure. Bodies have inertial
 * properties and spatial positioning within their parent's coordinate frame.
 */
class MJCFBody
{
public:
    /**
     * @brief Name identifier for the body.
     */
    std::string name;

    /**
     * @brief Position offset relative to the parent body frame.
     */
    Vec3 pos;

    /**
     * @brief Quaternion orientation relative to the parent body frame.
     */
    Quat quat;

    /**
     * @brief Z-axis direction for orientation specification.
     */
    Vec3 zaxis;

    /**
     * @brief Pointer to inertial properties of this body.
     */
    MJCFInertial* inertial;

    /**
     * @brief Collection of geometry elements attached to this body.
     */
    std::vector<MJCFGeom*> geoms;

    /**
     * @brief Collection of joints that connect this body to its children.
     */
    std::vector<MJCFJoint*> joints;

    /**
     * @brief Collection of child bodies in the kinematic hierarchy.
     */
    std::vector<MJCFBody*> bodies;

    /**
     * @brief Collection of sites (reference points) attached to this body.
     */
    std::vector<MJCFSite*> sites;

    /**
     * @brief Whether this body has visual elements for rendering.
     */
    bool hasVisual;

    MJCFBody()
    {
        name = "";
        pos = Vec3(0.0f, 0.0f, 0.0f);
        quat = Quat();
        inertial = nullptr;
        geoms.clear();
        joints.clear();
        bodies.clear();
        hasVisual = false;
    }

    ~MJCFBody()
    {
        if (inertial)
        {
            delete inertial;
        }

        for (int i = 0; i < (int)geoms.size(); i++)
        {
            delete geoms[i];
        }

        for (int i = 0; i < (int)joints.size(); i++)
        {
            delete joints[i];
        }

        for (int i = 0; i < (int)bodies.size(); i++)
        {
            delete bodies[i];
        }

        for (int i = 0; i < (int)sites.size(); i++)
        {
            delete sites[i];
        }
    }
};

/**
 * @brief Compiler settings that affect how the MJCF model is processed.
 * @details
 * Contains flags and settings that control various aspects of model compilation
 * including angle units, coordinate systems, automatic limit generation, and
 * file path specifications for assets.
 */
class MJCFCompiler
{
public:
    /**
     * @brief Whether angles are specified in radians (true) or degrees (false).
     */
    bool angleInRad;

    /**
     * @brief Whether to automatically compute inertia from geometry.
     */
    bool inertiafromgeom;

    /**
     * @brief Whether coordinates are in local frame (true) or global frame (false).
     */
    bool coordinateInLocal;

    /**
     * @brief Whether to automatically generate joint limits.
     */
    bool autolimits;

    /**
     * @brief Euler angle sequence for rotations (e.g., "xyz", "zyx").
     */
    std::string eulerseq;

    /**
     * @brief Directory path for mesh files.
     */
    std::string meshDir;

    /**
     * @brief Directory path for texture files.
     */
    std::string textureDir;

    MJCFCompiler()
    {
        eulerseq = "xyz";
        angleInRad = false;
        inertiafromgeom = true;
        coordinateInLocal = true;
        autolimits = true;
    }
};

/**
 * @brief Contact definition for collision filtering and contact parameters.
 * @details
 * Defines contact behavior between pairs of geometries or bodies, including
 * collision inclusion/exclusion rules and contact constraint parameters.
 * Used to customize collision detection and contact dynamics.
 */
class MJCFContact
{
public:
    /**
     * @brief Enumeration of contact types for collision filtering.
     */
    enum Type
    {
        /**
         * @brief Include contact between specified geometries/bodies.
         */
        PAIR,

        /**
         * @brief Exclude contact between specified geometries/bodies.
         */
        EXCLUDE,

        /**
         * @brief Default contact behavior when not explicitly specified.
         */
        DEFAULT
    };

    /**
     * @brief Type of contact definition (pair, exclude, or default).
     */
    Type type;

    /**
     * @brief Name identifier for the contact definition.
     */
    std::string name;

    /**
     * @brief Name of the first geometry in the contact pair.
     */
    std::string geom1;

    /**
     * @brief Name of the second geometry in the contact pair.
     */
    std::string geom2;

    /**
     * @brief Number of contact constraint dimensions.
     */
    int condim;

    /**
     * @brief Name of the first body in the contact pair.
     */
    std::string body1;

    /**
     * @brief Name of the second body in the contact pair.
     */
    std::string body2;

    MJCFContact()
    {
        type = DEFAULT;

        name = "";
        geom1 = "";
        geom2 = "";
        body1 = "";
        body2 = "";
    }
};

/**
 * @brief Actuator component for applying forces/torques to joints.
 * @details
 * Represents an actuator that can control joint motion through various control
 * modes including position, velocity, torque, and general control. Contains
 * control limits, force limits, and gain parameters for different control strategies.
 */
class MJCFActuator
{
public:
    /**
     * @brief Enumeration of actuator control types.
     */
    enum Type
    {
        /**
         * @brief Motor actuator that applies force/torque directly.
         */
        MOTOR,

        /**
         * @brief Position controller actuator.
         */
        POSITION,

        /**
         * @brief Velocity controller actuator.
         */
        VELOCITY,

        /**
         * @brief General purpose actuator with custom control.
         */
        GENERAL,

        /**
         * @brief Default actuator type when not specified.
         */
        DEFAULT
    };

    /**
     * @brief Type of actuator control.
     */
    Type type;

    /**
     * @brief Whether control input is limited to a range.
     */
    bool ctrllimited;

    /**
     * @brief Whether force output is limited to a range.
     */
    bool forcelimited;

    /**
     * @brief Control input range [min, max].
     */
    Vec2 ctrlrange;

    /**
     * @brief Force output range [min, max].
     */
    Vec2 forcerange = Vec2(-FLT_MAX, FLT_MAX);
    ;

    /**
     * @brief Gear ratio for force/torque transmission.
     */
    float gear;

    /**
     * @brief Name of the joint this actuator controls.
     */
    std::string joint;

    /**
     * @brief Name identifier for the actuator.
     */
    std::string name;

    /**
     * @brief Proportional gain for position control.
     */
    float kp;

    /**
     * @brief Derivative gain for velocity control.
     */
    float kv;

    MJCFActuator()
    {
        type = DEFAULT;

        ctrllimited = false;
        forcelimited = false;

        ctrlrange = Vec2(-1.0f, 1.0f);
        forcerange = Vec2(-FLT_MAX, FLT_MAX);

        gear = 0.0f;
        name = "";
        joint = "";

        kp = 0.f;
        kv = 0.f;
    }
};

/**
 * @brief Tendon element for creating cable-like constraints between bodies.
 * @details
 * Tendons are flexible constraints that can span multiple bodies and joints,
 * creating cable-like connections. They can be either fixed (connecting specific
 * joints) or spatial (following geometric paths through attachments and pulleys).
 */
class MJCFTendon
{
public:
    /**
     * @brief Enumeration of tendon types.
     */
    enum Type
    {
        /**
         * @brief Spatial tendon that follows geometric paths.
         */
        SPATIAL = 0,

        /**
         * @brief Fixed tendon that connects specific joints.
         */
        FIXED,

        /**
         * @brief Default tendon type when not specified.
         */
        DEFAULT // flag for default tendon
    };

    /**
     * @brief Fixed joint connection for fixed tendons.
     */
    struct FixedJoint
    {
        /**
         * @brief Name of the joint connected to the tendon.
         */
        std::string joint;

        /**
         * @brief Coupling coefficient for the joint connection.
         */
        float coef;
    };

    /**
     * @brief Spatial attachment point for spatial tendons.
     */
    struct SpatialAttachment
    {
        /**
         * @brief Type of attachment point.
         */
        enum Type
        {
            /**
             * @brief Attachment to a geometry element.
             */
            GEOM,

            /**
             * @brief Attachment to a site element.
             */
            SITE
        };

        /**
         * @brief Name of the geometry for geom-type attachments.
         */
        std::string geom;

        /**
         * @brief Name of the side site for spatial routing.
         */
        std::string sidesite = "";

        /**
         * @brief Name of the site for site-type attachments.
         */
        std::string site;

        /**
         * @brief Type of this attachment (geom or site).
         */
        Type type;

        /**
         * @brief Branch identifier for multi-branch tendons.
         */
        int branch;
    };

    /**
     * @brief Pulley mechanism for spatial tendons.
     */
    struct SpatialPulley
    {
        /**
         * @brief Pulley gear ratio divisor.
         */
        float divisor = 0.0;

        /**
         * @brief Branch identifier for the pulley.
         */
        int branch;
    };

    /**
     * @brief Type of tendon (spatial, fixed, or default).
     */
    Type type;

    /**
     * @brief Name identifier for the tendon.
     */
    std::string name;

    /**
     * @brief Whether the tendon has length limits.
     */
    bool limited;

    /**
     * @brief Length limits [min, max] for the tendon.
     */
    Vec2 range;

    // limit and friction solver params:
    /**
     * @brief Constraint solver impedance parameters for limits.
     */
    Vec3 solimplimit;

    /**
     * @brief Constraint solver reference parameters for limits.
     */
    Vec2 solreflimit;

    /**
     * @brief Constraint solver impedance parameters for friction.
     */
    Vec3 solimpfriction;

    /**
     * @brief Constraint solver reference parameters for friction.
     */
    Vec2 solreffriction;

    /**
     * @brief Contact margin for tendon interactions.
     */
    float margin;

    /**
     * @brief Friction loss coefficient.
     */
    float frictionloss;

    /**
     * @brief Visual width of the tendon for rendering.
     */
    float width;

    /**
     * @brief Name of the material for tendon visualization.
     */
    std::string material;

    /**
     * @brief RGBA color for tendon visualization.
     */
    Vec4 rgba;

    /**
     * @brief Natural length of the tendon spring.
     */
    float springlength;

    /**
     * @brief Spring stiffness coefficient.
     */
    float stiffness;

    /**
     * @brief Damping coefficient for the tendon.
     */
    float damping;

    // fixed
    /**
     * @brief Collection of fixed joint connections for fixed tendons.
     */
    std::vector<FixedJoint*> fixedJoints;

    // spatial
    /**
     * @brief Collection of spatial attachment points for spatial tendons.
     */
    std::vector<SpatialAttachment*> spatialAttachments;

    /**
     * @brief Collection of spatial pulleys for spatial tendons.
     */
    std::vector<SpatialPulley*> spatialPulleys;

    /**
     * @brief Spatial attachments organized by branch identifier.
     */
    std::map<int, std::vector<SpatialAttachment*>> spatialBranches;

    MJCFTendon()
    {
        type = FIXED;
        limited = false;
        range = Vec2(0.0f, 0.0f);

        solimplimit = Vec3(0.9f, 0.95f, 0.001f);
        solreflimit = Vec2(0.02f, 1.0f);
        solimpfriction = Vec3(0.9f, 0.95f, 0.001f);
        solreffriction = Vec2(0.02f, 1.0f);

        margin = 0.0f;
        frictionloss = 0.0f;

        width = 0.003f;
        material = "";
        rgba = Vec4(0.5f, 0.5f, 0.5f, 1.0f);
    }

    ~MJCFTendon()
    {

        for (int i = 0; i < (int)fixedJoints.size(); i++)
        {
            delete fixedJoints[i];
        }

        for (int i = 0; i < (int)spatialAttachments.size(); i++)
        {
            delete spatialAttachments[i];
        }

        for (int i = 0; i < (int)spatialPulleys.size(); i++)
        {
            delete spatialPulleys[i];
        }
    }
};

/**
 * @brief Mesh asset definition for 3D geometry.
 * @details
 * Defines a mesh asset that can be loaded from external files and used
 * for collision detection or visualization. Contains the file path and
 * scaling information for the mesh.
 */
class MJCFMesh
{
public:
    /**
     * @brief Name identifier for the mesh.
     */
    std::string name;

    /**
     * @brief File path to the mesh asset.
     */
    std::string filename;

    /**
     * @brief Scale factors [x, y, z] to apply to the mesh.
     */
    Vec3 scale;

    MJCFMesh()
    {
        name = "";
        filename = "";
        scale = Vec3(1.0f);
    }
};

/**
 * @brief Texture asset definition for materials.
 * @details
 * Defines a texture that can be applied to materials for visual rendering.
 * Supports various texture types including file-based textures and
 * procedurally generated grid patterns.
 */
class MJCFTexture
{
public:
    /**
     * @brief Name identifier for the texture.
     */
    std::string name;

    /**
     * @brief File path to the texture image.
     */
    std::string filename;

    /**
     * @brief Grid size specification for procedural textures.
     */
    std::string gridsize;

    /**
     * @brief Grid layout pattern for procedural textures.
     */
    std::string gridlayout;

    /**
     * @brief Type of texture (e.g., "cube", "sphere", "cylinder").
     */
    std::string type;

    MJCFTexture()
    {
        name = "";
        filename = "";
        gridsize = "";
        gridlayout = "";
        type = "cube";
    }
};

/**
 * @brief Material definition for visual appearance.
 * @details
 * Defines the visual appearance properties of surfaces including color,
 * texture mapping, and lighting response characteristics. Materials can
 * reference textures and define reflection and roughness properties.
 */
class MJCFMaterial
{
public:
    /**
     * @brief Name identifier for the material.
     */
    std::string name;

    /**
     * @brief Name of the texture applied to this material.
     */
    std::string texture;

    /**
     * @brief Specular reflection coefficient (0.0 to 1.0).
     */
    float specular;

    /**
     * @brief Surface roughness coefficient (0.0 to 1.0).
     */
    float roughness;

    /**
     * @brief Shininess/metallic property (0.0 to 1.0).
     */
    float shininess;

    /**
     * @brief RGBA color values [red, green, blue, alpha].
     */
    Vec4 rgba;

    /**
     * @brief Whether to project UVW coordinates for texture mapping.
     */
    bool project_uvw;

    MJCFMaterial()
    {
        name = "";
        texture = "";
        specular = 0.5f;
        roughness = 0.5f;
        shininess = 0.0f; // metallic
        rgba = Vec4(0.2f, 0.2f, 0.2f, 1.0f);
        project_uvw = true;
    }
};

/**
 * @brief Class definition for setting default values for MJCF elements.
 * @details
 * Defines a class that provides default values for various MJCF elements
 * including joints, geometries, actuators, tendons, meshes, materials, and sites.
 * Classes enable reusable configurations and inheritance of properties.
 */
class MJCFClass
{
public:
    // a class that defines default values for the following entities
    /**
     * @brief Default joint configuration.
     */
    MJCFJoint djoint;

    /**
     * @brief Default geometry configuration.
     */
    MJCFGeom dgeom;

    /**
     * @brief Default actuator configuration.
     */
    MJCFActuator dactuator;

    /**
     * @brief Default tendon configuration.
     */
    MJCFTendon dtendon;

    /**
     * @brief Default mesh configuration.
     */
    MJCFMesh dmesh;

    /**
     * @brief Default material configuration.
     */
    MJCFMaterial dmaterial;

    /**
     * @brief Default site configuration.
     */
    MJCFSite dsite;

    /**
     * @brief Name identifier for the class.
     */
    std::string name;
};

} // namespace mjcf
} // namespace importer
} // namespace asset
} // namespace isaacsim
