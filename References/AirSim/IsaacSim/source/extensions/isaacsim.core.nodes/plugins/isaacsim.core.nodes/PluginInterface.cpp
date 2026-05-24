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
#include <carb/filesystem/IFileSystem.h>

#include <isaacsim/core/nodes/ICoreNodes.h>
#include <isaacsim/core/simulation_manager/ISimulationManager.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/SimStageWithHistory.h>
#include <omni/graph/core/NodeTypeRegistrar.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ogn/Registration.h>
#include <omni/kit/IMinimal.h>
#include <omni/kit/IStageUpdate.h>
#include <omni/physx/IPhysx.h>


const struct carb::PluginImplDesc g_kPluginDesc = { "isaacsim.core.nodes", "Isaac Sim Core OmniGraph Nodes", "NVIDIA",
                                                    carb::PluginHotReload::eEnabled, "dev" };

CARB_PLUGIN_IMPL(g_kPluginDesc, isaacsim::core::nodes::CoreNodes)

DECLARE_OGN_NODES()

namespace
{
isaacsim::core::simulation_manager::ISimulationManager* g_simulationManager = nullptr;
std::map<uint64_t, void*> g_handleMap;
std::mutex g_handleMutex;
}

double getSimulationTime()
{
    return g_simulationManager->getSimulationTime();
}


double getSimulationTimeMonotonic()
{
    return g_simulationManager->getSimulationTimeMonotonic();
}

double getSystemTime()
{
    return g_simulationManager->getSystemTime();
}

size_t getPhysicsNumSteps()
{
    return g_simulationManager->getNumPhysicsSteps();
}

double getSimulationTimeAtTime(const omni::fabric::RationalTime& rtime)
{
    return g_simulationManager->getSimulationTimeAtTime(rtime);
}


double getSimulationTimeMonotonicAtTime(const omni::fabric::RationalTime& rtime)
{
    return g_simulationManager->getSimulationTimeMonotonicAtTime(rtime);
}

double getSystemTimeAtTime(const omni::fabric::RationalTime& rtime)
{
    return g_simulationManager->getSystemTimeAtTime(rtime);
}

uint64_t addHandle(void* handle)
{
    uint64_t handleId = reinterpret_cast<uint64_t>(handle);
    std::lock_guard<std::mutex> guard(g_handleMutex);
    g_handleMap[handleId] = handle;
    return handleId;
}

void* getHandle(const uint64_t handleId)
{
    std::lock_guard<std::mutex> guard(g_handleMutex);
    auto it = g_handleMap.find(handleId);
    if (it == g_handleMap.end())
    {
        return nullptr;
    }
    else
    {
        return it->second;
    }
}

bool removeHandle(const uint64_t handleId)
{
    std::lock_guard<std::mutex> guard(g_handleMutex);
    return g_handleMap.erase(handleId);
}

CARB_EXPORT void carbOnPluginStartup()
{
    g_simulationManager = carb::getCachedInterface<isaacsim::core::simulation_manager::ISimulationManager>();
    INITIALIZE_OGN_NODES()
}

CARB_EXPORT void carbOnPluginShutdown()
{
    RELEASE_OGN_NODES()
}

// carbonite interface for this plugin (may contain multiple compute nodes)
void fillInterface(isaacsim::core::nodes::CoreNodes& iface)
{

    using namespace isaacsim::core::nodes;

    memset(&iface, 0, sizeof(iface));

    iface.getSimTime = getSimulationTime;
    iface.getSimTimeMonotonic = getSimulationTimeMonotonic;
    iface.getSystemTime = getSystemTime;
    iface.getPhysicsNumSteps = getPhysicsNumSteps;

    iface.addHandle = addHandle;
    iface.getHandle = getHandle;
    iface.removeHandle = removeHandle;

    iface.getSimTimeAtTime = getSimulationTimeAtTime;
    iface.getSimTimeMonotonicAtTime = getSimulationTimeMonotonicAtTime;
    iface.getSystemTimeAtTime = getSystemTimeAtTime;
}
