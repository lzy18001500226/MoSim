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


// clang-format off
#include <pch/UsdPCH.h>
// clang-format on

#include "IUrdf.h"
#include "KinematicChain.h"
#include "MeshImporter.h"
#include "UrdfParser.h"
#include "UrdfTypes.h"

#include <carb/logging/Log.h>

#include <isaacsim/core/includes/math/core/Maths.h>
#include <pxr/usd/usdPhysics/articulationRootAPI.h>
#include <pxr/usd/usdPhysics/collisionAPI.h>
#include <pxr/usd/usdPhysics/driveAPI.h>
#include <pxr/usd/usdPhysics/fixedJoint.h>
#include <pxr/usd/usdPhysics/joint.h>
#include <pxr/usd/usdPhysics/limitAPI.h>
#include <pxr/usd/usdPhysics/massAPI.h>
#include <pxr/usd/usdPhysics/prismaticJoint.h>
#include <pxr/usd/usdPhysics/revoluteJoint.h>
#include <pxr/usd/usdPhysics/scene.h>
#include <pxr/usd/usdPhysics/sphericalJoint.h>

namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace urdf
{
/**
 * @class UrdfImporter
 * @brief URDF (Unified Robot Description Format) importer for converting robot descriptions to USD format.
 * @details
 * This class handles the import and conversion of URDF robot descriptions into USD (Universal Scene Description)
 * format for use in Isaac Sim. It processes URDF files containing robot geometry, kinematics, dynamics, and
 * material properties, creating equivalent USD representations suitable for physics simulation.
 *
 * The importer supports:
 * - Link geometry conversion from meshes and primitives
 * - Joint definitions with proper kinematic constraints
 * - Material properties and textures
 * - Physics properties including mass, inertia, and collision shapes
 * - Loop closures for closed kinematic chains
 *
 * @note The importer requires a valid URDF file and asset root directory containing referenced mesh files.
 */
class UrdfImporter
{
private:
    std::string assetRoot_;
    std::string urdfPath_;
    const ImportConfig config;
    std::map<std::string, std::string> matPrimPaths;
    std::map<pxr::TfToken, pxr::SdfPath> meshPaths;
    std::map<pxr::TfToken, pxr::SdfPath> materialPaths;

public:
    /**
     * @brief Constructs a UrdfImporter with the specified configuration.
     * @details
     * Initializes the URDF importer with paths to the robot description and import settings.
     * The asset root should contain all mesh and texture files referenced by the URDF.
     *
     * @param[in] assetRoot Root directory path containing robot assets (meshes, textures)
     * @param[in] urdfPath Full path to the URDF file to import
     * @param[in] options Import configuration settings controlling conversion behavior
     *
     * @pre assetRoot must be a valid directory path accessible for reading
     * @pre urdfPath must be a valid URDF file path
     */
    UrdfImporter(const std::string& assetRoot, const std::string& urdfPath, const ImportConfig& options)
        : assetRoot_(assetRoot), urdfPath_(urdfPath), config(options)
    {
    }

    /**
     * @brief Creates and populates a robot asset from the URDF description.
     * @details
     * Parses the URDF file and converts it into a UrdfRobot data structure containing
     * all robot components including links, joints, materials, and kinematic chains.
     * This method performs the core conversion logic from URDF to internal representation.
     *
     * @return UrdfRobot Complete robot data structure with parsed URDF content
     *
     * @throws std::runtime_error If URDF file cannot be parsed or contains invalid data
     * @throws std::invalid_argument If required mesh files are not found in asset root
     *
     * @pre URDF file must be accessible and contain valid robot description
     * @post Returns fully populated robot structure ready for USD stage creation
     */
    UrdfRobot createAsset();

    /**
     * @brief Adds the robot to USD stages for simulation.
     * @param[in,out] stageMap Map of stage names to USD stage references
     * @param[in] robot Robot data structure to add to stages
     * @param[in] getArticulationRoot Whether to get the articulation root
     * @return Path to the created robot in the USD stage
     */
    std::string addToStage(std::unordered_map<std::string, pxr::UsdStageRefPtr> stageMap,
                           const UrdfRobot& robot,
                           const bool getArticulationRoot);


private:
    /**
     * @brief Adds a rigid body link to the USD stage.
     * @param[in,out] stageMap Map of stage names to USD stage references
     * @param[in] link URDF link definition to convert
     * @param[in] poseBodyToWorld Transform from body frame to world frame
     * @param[in] robotPrim USD prim representing the robot root
     * @param[in] robot Complete robot definition for context
     */
    void addRigidBody(std::unordered_map<std::string, pxr::UsdStageRefPtr> stageMap,
                      const UrdfLink& link,
                      const Transform& poseBodyToWorld,
                      pxr::UsdGeomXform robotPrim,
                      const UrdfRobot& robot);
    /**
     * @brief Adds a joint connection between links to the USD stage.
     * @param[in,out] stageMap Map of stage names to USD stage references
     * @param[in] robotPrim USD prim representing the robot root
     * @param[in] joint URDF joint definition to convert
     * @param[in] poseJointToParentBody Transform from joint frame to parent body frame
     */
    void addJoint(std::unordered_map<std::string, pxr::UsdStageRefPtr> stageMap,
                  pxr::UsdGeomXform robotPrim,
                  const UrdfJoint& joint,
                  const Transform& poseJointToParentBody);
    /**
     * @brief Adds loop closure joints for closed kinematic chains.
     * @param[in,out] stages Map of stage names to USD stage references
     * @param[in] robotPrim USD prim representing the robot root
     * @param[in] robot Complete robot definition containing loop joints
     * @param[in] config Import configuration settings
     */
    void addLoopJoints(std::unordered_map<std::string, pxr::UsdStageRefPtr> stages,
                       pxr::UsdGeomXform robotPrim,
                       const UrdfRobot& robot,
                       const ImportConfig& config);
    /**
     * @brief Recursively adds links and joints to the USD stage following kinematic tree.
     * @param[in,out] stageMap Map of stage names to USD stage references
     * @param[in] poseParentToWorld Transform from parent frame to world frame
     * @param[in] parentNode Current node in the kinematic chain
     * @param[in] robot Complete robot definition for context
     * @param[in] robotPrim USD prim representing the robot root
     */
    void addLinksAndJoints(std::unordered_map<std::string, pxr::UsdStageRefPtr> stageMap,
                           const Transform& poseParentToWorld,
                           const KinematicChain::Node* parentNode,
                           const UrdfRobot& robot,
                           pxr::UsdGeomXform robotPrim);
    /**
     * @brief Adds merged child links to a parent prim in the USD stage.
     * @details
     * Processes child links that should be merged into their parent during import,
     * creating unified geometry representations. This is typically used for optimization
     * where multiple URDF links can be combined into a single USD prim to reduce
     * scene complexity while maintaining visual and collision fidelity.
     *
     * @param[in,out] stages Map of stage names to USD stage references for multi-stage import
     * @param[in] link Parent URDF link containing child links to be merged
     * @param[in] parentPrim USD prim that will contain the merged child geometry
     * @param[in] robot Complete robot definition providing context for link relationships
     *
     * @pre parentPrim must be a valid USD prim capable of containing child geometry
     * @pre link must have valid child links defined in the robot structure
     *
     * @note Merged children lose their individual transformation hierarchy but retain geometry
     */
    void addMergedChildren(std::unordered_map<std::string, pxr::UsdStageRefPtr> stages,
                           const UrdfLink& link,
                           const pxr::UsdPrim& parentPrim,
                           const UrdfRobot& robot);
    /**
     * @brief Adds all material definitions from the robot to the USD stage.
     * @details
     * Creates USD material prims for all materials defined in the URDF robot description.
     * This includes setting up material properties like diffuse color, specular values,
     * transparency, and texture references. Materials are created under the specified
     * prefix path to maintain organization in the USD scene hierarchy.
     *
     * @param[in,out] stage USD stage where materials will be created
     * @param[in] robot Robot definition containing all material specifications
     * @param[in] prefixPath USD path prefix where material prims will be created
     *
     * @pre stage must be a valid and writable USD stage
     * @pre prefixPath must be a valid USD path that can contain material prims
     *
     * @post All robot materials are created as USD material prims under prefixPath
     * @see addMaterial for individual material creation details
     */
    void addMaterials(pxr::UsdStageWeakPtr stage, const UrdfRobot& robot, const pxr::SdfPath& prefixPath);
    /**
     * @brief Creates a single USD material from a URDF material definition.
     * @details
     * Converts an individual URDF material specification into a USD Shade material prim
     * with proper surface shader connections. Handles material properties including:
     * - Diffuse color and texture mapping
     * - Specular reflection properties
     * - Transparency and opacity settings
     * - Normal and roughness maps when available
     *
     * @param[in,out] stage USD stage where the material will be created
     * @param[in] mat Key-value pair containing material name and URDF material definition
     * @param[in] prefixPath USD path prefix where the material prim will be created
     * @return UsdShadeMaterial Created USD material prim with configured properties
     *
     * @pre stage must be a valid and writable USD stage
     * @pre mat.second must contain valid URDF material properties
     * @pre prefixPath must be a valid USD path for material creation
     *
     * @post Returns configured USD material ready for assignment to geometry
     * @throws std::runtime_error If material creation fails or required textures are missing
     */
    pxr::UsdShadeMaterial addMaterial(pxr::UsdStageWeakPtr stage,
                                      const std::pair<std::string, UrdfMaterial>& mat,
                                      const pxr::SdfPath& prefixPath);
};
}
}
}
}
