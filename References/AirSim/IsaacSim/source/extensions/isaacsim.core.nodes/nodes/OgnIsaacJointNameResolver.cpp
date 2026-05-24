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

// clang-format off
#include <pch/UsdPCH.h>
// clang-format on

#include <carb/Defines.h>
#include <carb/Types.h>
#include <carb/events/EventsUtils.h>
#include <carb/logging/Logger.h>

#include <isaacsim/core/includes/BaseResetNode.h>
#include <isaacsim/core/includes/Conversions.h>
#include <isaacsim/core/includes/UsdUtilities.h>
#include <isaacsim/core/nodes/ICoreNodes.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/physics/tensors/IArticulationView.h>
#include <omni/physics/tensors/ISimulationView.h>
#include <omni/physics/tensors/TensorApi.h>
#include <omni/usd/UsdContext.h>
#include <omni/usd/UsdContextIncludes.h>

#include <OgnIsaacJointNameResolverDatabase.h>
#include <unordered_map>


namespace isaacsim
{
namespace core
{
namespace nodes
{

using namespace omni::physics::tensors;

class OgnIsaacJointNameResolver : public isaacsim::core::includes::BaseResetNode
{
public:
    static void initInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        auto& state =
            OgnIsaacJointNameResolverDatabase::sPerInstanceState<OgnIsaacJointNameResolver>(nodeObj, instanceId);

        state.m_tensorInterface = carb::getCachedInterface<TensorApi>();
        if (!state.m_tensorInterface)
        {
            CARB_LOG_ERROR("Failed to acquire Tensor Api interface\n");
            return;
        }
        state.m_robotPath = "";
    }

    static bool compute(OgnIsaacJointNameResolverDatabase& db)
    {
        const GraphContextObj& context = db.abi_context();

        auto& state = db.perInstanceState<OgnIsaacJointNameResolver>();
        if (state.m_firstFrame)
        {

            const auto& prim = db.inputs.targetPrim();
            state.m_robotPath = db.inputs.robotPath();

            // if robotPath field is empty
            if (state.m_robotPath.empty())
            {

                // if targetPrim field is populated
                if (!prim.empty())
                {

                    state.m_robotPath = omni::fabric::toSdfPath(prim[0]).GetText();
                }
                else
                {
                    db.logError("OmniGraph Error: no articulation root prim found");
                    return false;
                }
            }


            state.m_firstFrame = false;
            // Find our stage
            const auto stageId = context.iContext->getStageId(context);
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

            if (!stage)
            {
                db.logError("Could not find USD stage %ld", stageId);
                return false;
            }
            state.m_simView = state.m_tensorInterface->createSimulationView(stageId);

            const pxr::UsdPrim startPrim = stage->GetPrimAtPath(pxr::SdfPath(state.m_robotPath));

            if (!startPrim.IsValid())
            {
                db.logError("%s prim is invalid", state.m_robotPath);
                return false;
            }

            auto* articulation = state.m_simView->createArticulationView(state.m_robotPath.c_str());
            // Checking we have a valid articulation
            if (!articulation)
            {
                db.logError("Articulation not found for prim %s", state.m_robotPath);
                return false;
            }

            // Traverse from the starting prim
            for (const pxr::UsdPrim& currentPrim : pxr::UsdPrimRange(startPrim))
            {

                const std::string primNameOverride = isaacsim::core::includes::getName(currentPrim);
                const std::string primName = currentPrim.GetName();
                if (primNameOverride != primName)
                {
                    state.m_nameOverrideMap.emplace(primNameOverride, currentPrim);
                }
            }
        }

        state.resolvePrims(db);

        db.outputs.execOut() = kExecutionAttributeStateEnabled;
        return true;
    }

    void resolvePrims(OgnIsaacJointNameResolverDatabase& db)
    {
        // Check if the input string is a key in the dictionary
        const auto& inNames = db.inputs.jointNames();
        auto& outNames = db.outputs.jointNames();
        outNames.resize(inNames.size());

        for (size_t i = 0; i < inNames.size(); ++i)
        {
            const std::string primNameString = db.tokenToString(inNames[i]);
            const auto it = m_nameOverrideMap.find(primNameString);
            outNames[i] = db.stringToToken(it != m_nameOverrideMap.end() ? it->second.GetName().GetText() :
                                                                           primNameString.c_str());
        }

        db.outputs.robotPath() = m_robotPath;
    }

    void reset() override
    {
        m_firstFrame = true;
        m_robotPath = "";
        m_nameOverrideMap.clear();
    }

private:
    std::unordered_map<std::string, pxr::UsdPrim> m_nameOverrideMap;
    bool m_firstFrame = true;
    std::string m_robotPath;
    TensorApi* m_tensorInterface = nullptr;
    ISimulationView* m_simView = nullptr;
};

REGISTER_OGN_NODE()
}
}
}
