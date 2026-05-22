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

#include <carb/logging/Log.h>

#include <isaacsim/asset/importer/mjcf/IMjcf.h>
#include <isaacsim/asset/importer/mjcf/Mesh.h>
#include <isaacsim/asset/importer/mjcf/MjcfParser.h>
#include <isaacsim/asset/importer/mjcf/MjcfTypes.h>
#include <isaacsim/asset/importer/mjcf/MjcfUsd.h>
#include <isaacsim/asset/importer/mjcf/MjcfUtils.h>
#include <isaacsim/core/includes/math/core/Maths.h>
#include <isaacsim/core/includes/utils/Usd.h>
#include <pxr/usd/usdGeom/imageable.h>

#include <iostream>
#include <iterator>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <tinyxml2.h>
#include <vector>

namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace mjcf
{

/**
 * @brief Main importer class for loading and converting MJCF models to USD format.
 * @details
 * This class handles the complete import pipeline for MJCF (MuJoCo XML Format) models,
 * including parsing, validation, and conversion to USD format with physics properties.
 * It manages all model components including bodies, joints, geometries, actuators,
 * tendons, materials, and contact definitions.
 */
class MJCFImporter
{
public:
    /**
     * @brief Base directory path for resolving relative file paths.
     */
    std::string baseDirPath;

    /**
     * @brief Name of the default class for element configurations.
     */
    std::string defaultClassName;

    /**
     * @brief Map of class definitions by name.
     */
    std::map<std::string, MJCFClass> classes;

    /**
     * @brief Compiler settings for model processing.
     */
    MJCFCompiler compiler;

    /**
     * @brief Collection of all bodies in the model.
     */
    std::vector<MJCFBody*> bodies;

    /**
     * @brief Collection of collision geometry elements.
     */
    std::vector<MJCFGeom*> collisionGeoms;

    /**
     * @brief Collection of actuators in the model.
     */
    std::vector<MJCFActuator*> actuators;

    /**
     * @brief Collection of tendons in the model.
     */
    std::vector<MJCFTendon*> tendons;

    /**
     * @brief Collection of contact definitions.
     */
    std::vector<MJCFContact*> contacts;

    /**
     * @brief Collection of equality constraints.
     */
    std::vector<MJCFEqualityConnect*> equalityConnects;

    /**
     * @brief World body containing global elements.
     */
    MJCFBody worldBody;

    /**
     * @brief Map of USD revolute joints by name.
     */
    std::map<std::string, pxr::UsdPhysicsRevoluteJoint> revoluteJointsMap;

    /**
     * @brief Map of USD prismatic joints by name.
     */
    std::map<std::string, pxr::UsdPhysicsPrismaticJoint> prismaticJointsMap;

    /**
     * @brief Map of USD D6 (6-DOF) joints by name.
     */
    std::map<std::string, pxr::UsdPhysicsJoint> d6JointsMap;

    /**
     * @brief Map of USD geometry primitives by name.
     */
    std::map<std::string, pxr::UsdPrim> geomPrimMap;

    /**
     * @brief Map of USD site primitives by name.
     */
    std::map<std::string, pxr::UsdPrim> sitePrimMap;

    /**
     * @brief Map from site names to their parent body primitives.
     */
    std::map<std::string, pxr::UsdPrim> siteToBodyPrim;

    /**
     * @brief Map from geometry names to their parent body primitives.
     */
    std::map<std::string, pxr::UsdPrim> geomToBodyPrim;

    /**
     * @brief Map from body names to their USD primitives.
     */
    std::map<std::string, pxr::UsdPrim> bodyNameToPrim;

    /**
     * @brief Queue for processing bodies during import.
     */
    std::queue<MJCFBody*> bodyQueue;

    /**
     * @brief Map from joint names to kinematic hierarchy indices.
     */
    std::map<std::string, int> jointToKinematicHierarchy;

    /**
     * @brief Map from joint names to actuator indices.
     */
    std::map<std::string, int> jointToActuatorIdx;

    /**
     * @brief Cache of mesh information for simulation.
     */
    std::map<std::string, MeshInfo> simulationMeshCache;

    /**
     * @brief Map of mesh definitions by name.
     */
    std::map<std::string, MJCFMesh> meshes;

    /**
     * @brief Map of material definitions by name.
     */
    std::map<std::string, MJCFMaterial> materials;

    /**
     * @brief Map from material tokens to USD paths.
     */
    std::map<pxr::TfToken, pxr::SdfPath> materialPaths;

    /**
     * @brief Map of converted mesh USD paths.
     */
    std::map<std::string, pxr::SdfPath> convertedMeshes;

    /**
     * @brief Map of texture definitions by name.
     */
    std::map<std::string, MJCFTexture> textures;

    /**
     * @brief Contact graph for collision filtering.
     */
    std::vector<ContactNode*> contactGraph;

    /**
     * @brief Map from body names to body objects.
     */
    std::map<std::string, MJCFBody*> nameToBody;

    /**
     * @brief Map from geometry names to indices.
     */
    std::map<std::string, int> geomNameToIdx;

    /**
     * @brief Map from names to USD collision primitive paths.
     */
    std::map<std::string, std::string> nameToUsdCollisionPrim;

    /**
     * @brief Whether to create separate bodies for fixed joints.
     */
    bool createBodyForFixedJoint;

    /**
     * @brief Whether the model has been successfully loaded.
     */
    bool isLoaded = false;

    /**
     * @brief Constructor that loads and parses an MJCF file.
     * @param[in] fullPath Full path to the MJCF file
     * @param[in] config Import configuration settings
     */
    MJCFImporter(const std::string fullPath, ImportConfig& config);

    /**
     * @brief Destructor that cleans up allocated resources.
     */
    ~MJCFImporter();

    /**
     * @brief Populates the body lookup maps for fast access.
     * @param[in] body Body to add to lookup maps
     */
    void populateBodyLookup(MJCFBody* body);

    /**
     * @brief Adds physics entities to the USD stages.
     * @param[in] stages Map of USD stages by name
     * @param[in] trans Root transformation
     * @param[in] rootPrimPath Root primitive path in USD
     * @param[in] config Import configuration settings
     * @return True if successful, false otherwise
     */
    bool AddPhysicsEntities(std::unordered_map<std::string, pxr::UsdStageRefPtr> stages,
                            const Transform trans,
                            const std::string& rootPrimPath,
                            const ImportConfig& config);

    /**
     * @brief Creates physics body and joint USD primitives.
     * @param[in] stages Map of USD stages by name
     * @param[in] body MJCF body to convert
     * @param[in] rootPath Root path for USD primitives
     * @param[in] rootPrimPath Root primitive path
     * @param[in] trans Transformation to apply
     * @param[in] isRoot Whether this is the root body
     * @param[in] parentBodyPath Path to parent body
     * @param[in] config Import configuration settings
     * @param[in] instanceableUsdPath Path for instanceable USD assets
     * @param[in,out] robotPrim Robot primitive in USD
     */
    void CreatePhysicsBodyAndJoint(std::unordered_map<std::string, pxr::UsdStageRefPtr> stages,
                                   MJCFBody* body,
                                   const std::string& rootPath,
                                   const std::string& rootPrimPath,
                                   const Transform& trans,
                                   const bool isRoot,
                                   const std::string& parentBodyPath,
                                   const ImportConfig& config,
                                   const std::string& instanceableUsdPath,
                                   pxr::UsdPrim& robotPrim);

    /**
     * @brief Adds joint USD primitives for a body.
     * @param[in] stages Map of USD stages by name
     * @param[in] rootPath Root path for USD primitives
     * @param[in] parentBodyPath Path to parent body
     * @param[in] bodyPath Path to current body
     * @param[in] body MJCF body containing joints
     * @param[in] config Import configuration settings
     * @param[in] trans0 Parent body transformation
     * @param[in] trans1 Current body transformation
     * @param[in] isRoot Whether this is the root body
     * @param[in] numJoints Number of joints to process
     * @param[in,out] robotPrim Robot primitive in USD
     */
    void addJoints(std::unordered_map<std::string, pxr::UsdStageRefPtr> stages,
                   const std::string& rootPath,
                   const std::string& parentBodyPath,
                   const std::string& bodyPath,
                   MJCFBody* body,
                   const ImportConfig& config,
                   const Transform& trans0,
                   const Transform& trans1,
                   const bool isRoot,
                   const int numJoints,
                   pxr::UsdPrim& robotPrim);

    /**
     * @brief Computes joint frame transformations.
     * @param[out] origin Computed joint origin transformation
     * @param[out] axisMap Axis mapping for joint
     * @param[in] body Body containing the joint
     */
    void computeJointFrame(Transform& origin, int* axisMap, const MJCFBody* body);

    /**
     * @brief Checks if contact should be excluded between two bodies.
     * @param[in] body1 First body to check
     * @param[in] body2 Second body to check
     * @return True if contact should be excluded, false otherwise
     */
    bool contactBodyExclusion(MJCFBody* body1, MJCFBody* body2);

    /**
     * @brief Creates the contact graph for collision filtering.
     * @return True if successful, false otherwise
     */
    bool createContactGraph();

    /**
     * @brief Computes the kinematic hierarchy for the model.
     */
    void computeKinematicHierarchy();

    /**
     * @brief Adds world-level geometries and sites to USD.
     * @param[in] stages Map of USD stages by name
     * @param[in] rootPath Root path for USD primitives
     * @param[in] config Import configuration settings
     * @param[in] instanceableUsdPath Path for instanceable USD assets
     */
    void addWorldGeomsAndSites(std::unordered_map<std::string, pxr::UsdStageRefPtr> stages,
                               std::string rootPath,
                               const ImportConfig& config,
                               const std::string instanceableUsdPath);

    /**
     * @brief Adds visual geometry primitives to USD.
     * @param[in] stage USD stage to add to
     * @param[in] bodyPrim Parent body primitive
     * @param[in] body MJCF body containing geometry
     * @param[in] bodyPath Path to the body
     * @param[in] config Import configuration settings
     * @param[in] createGeoms Whether to create geometry primitives
     * @param[in] rootPrimPath Root primitive path
     * @return True if successful, false otherwise
     */
    bool addVisualGeom(pxr::UsdStageWeakPtr stage,
                       pxr::UsdPrim bodyPrim,
                       MJCFBody* body,
                       std::string bodyPath,
                       const ImportConfig& config,
                       bool createGeoms,
                       const std::string rootPrimPath);

    /**
     * @brief Adds site primitives to USD.
     * @param[in] stage USD stage to add to
     * @param[in] bodyPrim Parent body primitive
     * @param[in] body MJCF body containing sites
     * @param[in] bodyPath Path to the body
     * @param[in] config Import configuration settings
     */
    void addVisualSites(pxr::UsdStageWeakPtr stage,
                        pxr::UsdPrim bodyPrim,
                        MJCFBody* body,
                        std::string bodyPath,
                        const ImportConfig& config);

    /**
     * @brief Adds contact filter primitives to USD.
     * @param[in] stage USD stage to add to
     */
    void AddContactFilters(pxr::UsdStageWeakPtr stage);

    /**
     * @brief Adds tendon primitives to USD.
     * @param[in] stage USD stage to add to
     * @param[in] rootPath Root path for USD primitives
     */
    void AddTendons(pxr::UsdStageWeakPtr stage, std::string rootPath);

    /**
     * @brief Gets local position for a spatial attachment.
     * @param[in] attachment Spatial attachment to compute position for
     * @return Local position as 3D vector
     */
    pxr::GfVec3f GetLocalPos(MJCFTendon::SpatialAttachment attachment);

    /**
     * @brief Applies material properties to a USD primitive.
     * @param[in] stage USD stage containing the primitive
     * @param[in,out] prim USD primitive to apply material to
     * @param[in] element Visual element containing material information
     */
    void applyMaterial(pxr::UsdStageWeakPtr stage, pxr::UsdPrim& prim, MJCFVisualElement* element);
};

} // namespace mjcf
} // namespace importer
} // namespace asset
} // namespace isaacsim
