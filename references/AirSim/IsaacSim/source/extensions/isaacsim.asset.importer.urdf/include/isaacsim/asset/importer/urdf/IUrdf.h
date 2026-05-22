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

#include <carb/Defines.h>

#include <isaacsim/asset/importer/urdf/UrdfTypes.h>
#include <pybind11/pybind11.h>

#include <stdint.h>
namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace urdf
{
/**
 * @struct ImportConfig
 * @brief Configuration parameters for URDF import operations.
 * @details
 * This structure contains various options and settings that control how
 * URDF files are parsed and imported into the simulation environment.
 * It allows customization of joint merging, physics properties, scaling,
 * and other import behaviors.
 */
struct ImportConfig
{
    /**
     * @brief Whether to merge fixed joints during import
     */
    bool mergeFixedJoints = true;

    /**
     * @brief Whether to replace cylinder geometries with capsule geometries
     */
    bool replaceCylindersWithCapsules = false;

    /**
     * @brief Whether to perform convex decomposition on meshes
     */
    bool convexDecomp = false;

    /**
     * @brief Whether to import inertia tensor information
     */
    bool importInertiaTensor = true;

    /**
     * @brief Whether to fix the base of the robot (make it static)
     */
    bool fixBase = true;

    /**
     * @brief Whether to enable self-collision detection
     */
    bool selfCollision = false;

    /**
     * @brief Default density for objects without mass/inertia (0 to auto-compute)
     */
    float density = 0.0f;

    /**
     * @brief Default drive type for joints
     */
    UrdfJointTargetType defaultDriveType = UrdfJointTargetType::POSITION;

    /**
     * @brief Default drive strength for joint actuators
     */
    float defaultDriveStrength = 1e3f;

    /**
     * @brief Default damping for position-driven joints
     */
    float defaultPositionDriveDamping = 1e2f;

    /**
     * @brief Scale factor for all distance measurements
     */
    float distanceScale = 1.0f;

    /**
     * @brief Up vector direction for the coordinate system
     */
    UrdfAxis upVector = { 0.0f, 0.0f, 1.0f };

    /**
     * @brief Whether to create a physics scene during import
     */
    bool createPhysicsScene = false;

    /**
     * @brief Whether to make the imported model the default prim
     */
    bool makeDefaultPrim = false;

    /**
     * @brief Subdivision scheme for normal computation
     */
    UrdfNormalSubdivisionScheme subdivisionScheme = UrdfNormalSubdivisionScheme::BILINEAR;

    /**
     * @brief Whether to create collision geometry from visual geometry when missing
     */
    bool collisionFromVisuals = false;

    /**
     * @brief Whether to parse mimic joint relationships
     */
    bool parseMimic = true;

    /**
     * @brief Whether to override joint dynamics parameters
     */
    bool overrideJointDynamics = false;
};


/**
 * @struct Urdf
 * @brief Interface for URDF parsing and import operations.
 * @details
 * This structure defines the interface for URDF (Unified Robot Description Format)
 * operations including parsing URDF files/strings and importing robots into
 * the simulation environment.
 */
struct Urdf
{
    CARB_PLUGIN_INTERFACE("isaacsim::asset::importer::urdf::Urdf", 0, 1);

    /**
     * @brief Parses a URDF file into a UrdfRobot data structure
     * @param[in] assetRoot Root directory path for assets
     * @param[in] assetName Name of the URDF asset file
     * @param[in,out] importConfig Configuration parameters for import
     * @return UrdfRobot data structure containing parsed robot information
     */
    UrdfRobot(CARB_ABI* parseUrdf)(const std::string& assetRoot, const std::string& assetName, ImportConfig& importConfig);

    /**
     * @brief Parses a URDF data string into a UrdfRobot data structure
     * @param[in] urdf_str URDF content as string
     * @param[in,out] importConfig Configuration parameters for import
     * @return UrdfRobot data structure containing parsed robot information
     */
    UrdfRobot(CARB_ABI* parseUrdfString)(const std::string& urdf_str, ImportConfig& importConfig);

    /**
     * @brief Computes natural stiffness for a joint
     * @param[in] robot Robot data structure
     * @param[in] joint Name of the joint
     * @param[in] naturalFrequency Desired natural frequency in Hz
     * @return Computed natural stiffness value
     */
    float(CARB_ABI* computeJointNaturalStiffess)(const UrdfRobot& robot, std::string joint, float naturalFrequency);

    /**
     * @brief Imports a UrdfRobot into the stage
     * @param[in] assetRoot Root directory path for assets
     * @param[in] assetName Name of the asset
     * @param[in] robot Robot data structure to import
     * @param[in,out] importConfig Configuration parameters for import
     * @param[in] stage Stage identifier where robot will be imported
     * @param[in] getArticulationRoot Whether to get the articulation root
     * @return Path to the imported robot in the stage
     */
    std::string(CARB_ABI* importRobot)(const std::string& assetRoot,
                                       const std::string& assetName,
                                       const UrdfRobot& robot,
                                       ImportConfig& importConfig,
                                       const std::string& stage,
                                       const bool getArticulationRoot);

    /**
     * @brief Gets the kinematic chain of the robot
     * @param[in] robot Robot data structure
     * @return Python dictionary containing kinematic chain information
     */
    pybind11::dict(CARB_ABI* getKinematicChain)(const UrdfRobot& robot);
};
}
}
}
}
