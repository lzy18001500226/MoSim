// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <usdrt/gf/matrix.h>

#include <string>
#include <vector>

namespace isaacsim
{
namespace robot
{
namespace surface_gripper
{

/**
 * @struct SurfaceGripperInterface
 * @brief Interface for controlling surface gripper functionality.
 * @details
 * Provides function pointers for controlling surface grippers in the simulation.
 * Surface grippers can attach to and manipulate objects through surface contact
 * rather than traditional mechanical gripping.
 *
 * All functions operate on grippers identified by their USD prim path.
 */
struct SurfaceGripperInterface
{
    CARB_PLUGIN_INTERFACE("isaacsim::robot::surface_gripper::ISurfaceGripper", 0, 1);

    /** @brief Function pointer to get the current status of a surface gripper */
    int(CARB_ABI* getGripperStatus)(const char* primPath);

    /** @brief Function pointer to open/release a surface gripper */
    bool(CARB_ABI* openGripper)(const char* primPath);

    /** @brief Function pointer to close/activate a surface gripper */
    bool(CARB_ABI* closeGripper)(const char* primPath);

    /** @brief Function pointer to set a specific gripper action value */
    bool(CARB_ABI* setGripperAction)(const char* primPath, const float action);

    /** @brief Function pointer to get the list of objects currently gripped */
    std::vector<std::string>(CARB_ABI* getGrippedObjects)(const char* primPath);

    /** @brief Function pointer to set whether to write to USD */
    bool(CARB_ABI* setWriteToUsd)(const bool writeToUsd);

    /** @brief Function pointer to get statuses for multiple surface grippers */
    std::vector<int>(CARB_ABI* getGripperStatusBatch)(const char* const* primPaths, size_t count);

    /** @brief Function pointer to open multiple surface grippers */
    std::vector<bool>(CARB_ABI* openGripperBatch)(const char* const* primPaths, size_t count);

    /** @brief Function pointer to close multiple surface grippers */
    std::vector<bool>(CARB_ABI* closeGripperBatch)(const char* const* primPaths, size_t count);

    /** @brief Function pointer to set actions for multiple surface grippers */
    std::vector<bool>(CARB_ABI* setGripperActionBatch)(const char* const* primPaths, const float* actions, size_t count);

    /** @brief Function pointer to get gripped objects for multiple surface grippers */
    std::vector<std::vector<std::string>>(CARB_ABI* getGrippedObjectsBatch)(const char* const* primPaths, size_t count);
};

} // namespace surface_gripper
} // namespace robot
} // namespace isaacsim
