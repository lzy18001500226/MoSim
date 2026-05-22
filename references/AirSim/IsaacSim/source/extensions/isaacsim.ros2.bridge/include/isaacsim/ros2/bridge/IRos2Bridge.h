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

/**
 * @file
 * @brief Interface to access the ROS 2 factory and context handler for the sourced ROS 2 distribution.
 * @details
 * This header file defines the main interface for the ROS 2 bridge, providing access to factory
 * and context handling functionality for ROS 2 integration within Isaac Sim.
 */
#pragma once

#include <carb/Defines.h>
#include <carb/Types.h>

#include <string>
#include <vector>

namespace isaacsim
{
namespace ros2
{
namespace bridge
{

class Ros2Factory;

/**
 * @class Ros2Bridge
 * @brief Main interface class for the ROS 2 bridge functionality.
 * @details
 * The Ros2Bridge class provides the core interface for interacting with ROS 2 functionality
 * within Isaac Sim. It manages the lifecycle of ROS 2 context handlers and provides factory
 * access for creating ROS 2 related objects.
 */
struct Ros2Bridge
{
    /**
     * @brief Plugin interface definition for the ROS 2 bridge.
     * @details Defines the plugin interface with version information.
     */
    CARB_PLUGIN_INTERFACE("isaacsim::ros2::bridge::Ros2Bridge", 0, 2);

    /**
     * @brief Retrieves the memory address of the ROS 2 context handler.
     * @details
     * The Ros2ContextHandle object encapsulates a `rcl_context_t` (non-global state of an init/shutdown cycle)
     * instance used in the creation of ROS 2 nodes and other entities.
     *
     * @return Memory address of the context handler as a 64-bit unsigned integer.
     *
     * @note This address points to a shared pointer object of type Ros2ContextHandle.
     * @warning Do not attempt to dereference this address directly without proper casting to the correct type.
     */
    uint64_t const(CARB_ABI* getDefaultContextHandleAddr)();

    /**
     * @brief Retrieves the factory instance for creating ROS 2 objects.
     * @details
     * Returns a factory instance that can create various ROS 2 related functions and objects
     * according to the sourced ROS 2 distribution. The factory provides a centralized way
     * to instantiate ROS 2 components.
     *
     * @return Pointer to the factory instance.
     *
     * @note The returned pointer is owned by the bridge implementation and should not be deleted.
     * @see Ros2Factory for the complete list of available factory methods.
     */
    Ros2Factory* const(CARB_ABI* getFactory)();

    /**
     * @brief Checks the initialization status of the bridge.
     * @details
     * Verifies if both the factory (Ros2Factory) and the handler (Ros2ContextHandle) objects
     * have been properly instantiated. These objects are created when the Ros2Bridge interface
     * is first acquired after the plugin is loaded by the isaacsim.ros2.bridge extension.
     *
     * @return True if both factory and context handler are successfully instantiated,
     *         false otherwise.
     *
     * @note This method should be called before attempting to use any other methods of this interface.
     * @warning Using other methods when this returns false may result in undefined behavior.
     */
    bool const(CARB_ABI* getStartupStatus)();
};

} // namespace bridge
} // namespace ros2
} // namespace isaacsim
