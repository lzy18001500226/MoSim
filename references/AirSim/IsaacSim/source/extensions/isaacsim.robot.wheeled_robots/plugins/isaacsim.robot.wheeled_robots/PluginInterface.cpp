// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#define CARB_EXPORTS

// clang-format off
#include <pch/UsdPCH.h>
// clang-format on

#include <carb/Framework.h>
#include <carb/PluginUtils.h>
#include <carb/settings/ISettings.h>

#include <isaacsim/robot/wheeled_robots/IWheeledRobots.h>
#include <omni/fabric/IToken.h>
#include <omni/graph/core/NodeTypeRegistrar.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ogn/Registration.h>
#include <omni/kit/IMinimal.h>

namespace
{

/**
 * @brief Plugin descriptor for the Wheeled Robots module
 * @details
 * Defines the plugin metadata including name, description, author, and hot reload capability.
 * This descriptor is used by the Carbonite framework to identify and manage the plugin.
 */
const struct carb::PluginImplDesc g_kPluginDesc = { "isaacsim.robot.wheeled_robots",
                                                    "Isaac Sim Wheeled Robot Controllers", "NVIDIA",
                                                    carb::PluginHotReload::eEnabled, "dev" };

} // anonymous namespace

/**
 * @brief Plugin implementation declaration for the Wheeled Robots interface
 * @details
 * Registers the IWheeledRobots interface with the Carbonite plugin framework,
 * making it available to other components in the system.
 */
CARB_PLUGIN_IMPL(g_kPluginDesc, isaacsim::robot::wheeled_robots::IWheeledRobots)

/**
 * @brief Plugin dependency declaration
 * @details
 * Declares that this plugin depends on the graph registry, token system, and settings interfaces.
 * These dependencies must be available before this plugin can be loaded.
 */
CARB_PLUGIN_IMPL_DEPS(omni::graph::core::IGraphRegistry, omni::fabric::IToken, carb::settings::ISettings)

/**
 * @brief OGN node declaration
 * @details
 * Declares that this plugin will register OGN (Omniverse Graph Nodes) with the system.
 */
DECLARE_OGN_NODES()

/**
 * @brief Fills the interface with required functionality
 * @details
 * Initializes the IWheeledRobots interface with the implementation of the required functions.
 * Currently, this implementation is empty as it initializes the interface to its default state.
 *
 * @param[out] iface The interface to be filled with functionality
 */
void fillInterface(isaacsim::robot::wheeled_robots::IWheeledRobots& iface)
{
    iface = {};
}

/**
 * @brief Plugin startup function
 * @details
 * Called by the Carbonite framework when the plugin is loaded.
 * Initializes the OGN nodes provided by this plugin.
 */
CARB_EXPORT void carbOnPluginStartup(){ INITIALIZE_OGN_NODES() }

/**
 * @brief Plugin shutdown function
 * @details
 * Called by the Carbonite framework when the plugin is being unloaded.
 * Releases any resources associated with the OGN nodes provided by this plugin.
 */
CARB_EXPORT void carbOnPluginShutdown()
{
    RELEASE_OGN_NODES()
}
