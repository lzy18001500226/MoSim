// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <pybind11/pybind11.h>

#include <stdint.h>

namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace mjcf
{

/**
 * @struct ImportConfig
 * @brief Configuration settings for importing MJCF files.
 * @details
 * This structure contains various options and parameters that control how MJCF files
 * are imported and converted into USD format. It includes physics settings, visual
 * options, and optimization flags.
 */
struct ImportConfig
{
    /** @brief Whether to merge fixed joints during import. */
    bool mergeFixedJoints = false;

    /** @brief Whether to perform convex decomposition on meshes. */
    bool convexDecomp = false;

    /** @brief Whether to import inertia tensor information. */
    bool importInertiaTensor = false;

    /** @brief Whether to fix the base of the imported model. */
    bool fixBase = true;

    /** @brief Whether to enable self-collision detection. */
    bool selfCollision = false;

    /** @brief Default density used for objects without mass/inertia in kg/m³. */
    float density = 1000; // default density used for objects without mass/inertia
    // UrdfJointTargetType defaultDriveType = UrdfJointTargetType::POSITION;

    /** @brief Default drive strength value for joints. */
    float defaultDriveStrength = 100000;

    /** @brief Scaling factor for distances in the imported model. */
    float distanceScale = 1.0f;
    // UrdfAxis upVector = { 0, 0, 1 };

    /** @brief Whether to create a physics scene during import. */
    bool createPhysicsScene = true;

    /** @brief Whether to make the imported model the default prim. */
    bool makeDefaultPrim = true;

    /** @brief Whether to create bodies for fixed joints. */
    bool createBodyForFixedJoint = true;

    /** @brief Whether to override center of mass calculations. */
    bool overrideCoM = false;

    /** @brief Whether to override inertia calculations. */
    bool overrideInertia = false;

    /** @brief Whether to visualize collision geometries. */
    bool visualizeCollisionGeoms = false;

    /** @brief Whether to import MJCF site elements. */
    bool importSites = true;

    /** @brief Whether to make meshes instanceable for optimization. */
    bool makeInstanceable = false;

    /** @brief USD file path for instanceable meshes. */
    std::string instanceableMeshUsdPath = "./instanceable_meshes.usd";
};

/**
 * @struct Mjcf
 * @brief Interface for MJCF file import functionality.
 * @details
 * This structure defines the plugin interface for importing MJCF (MuJoCo XML) files
 * and converting them to USD format for use in Isaac Sim.
 */
struct Mjcf
{
    CARB_PLUGIN_INTERFACE("isaacsim::asset::importer::mjcf::Mjcf", 0, 1);

    /**
     * @brief Function pointer for creating assets from MJCF files.
     * @details
     * This function loads an MJCF file and creates corresponding USD assets
     * based on the provided configuration settings.
     *
     * @param[in] fileName Path to the MJCF file to import
     * @param[in] primName Name for the created USD primitive
     * @param[in,out] config Configuration settings for the import process
     * @param[in] stage_identifier Identifier for the target USD stage
     */
    void(CARB_ABI* createAssetFromMJCF)(const char* fileName,
                                        const char* primName,
                                        ImportConfig& config,
                                        const std::string& stage_identifier);
};

} // namespace mjcf
} // namespace importer
} // namespace asset
} // namespace isaacsim
