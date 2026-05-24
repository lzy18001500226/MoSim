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
#include <isaacsim/core/nodes/ICoreNodes.h>
#include <omni/usd/UsdContextIncludes.h>
//
#include <omni/physx/IPhysx.h>
#include <omni/usd/UsdContext.h>

#include <OgnOnPhysicsStepDatabase.h>
#include <algorithm>
#include <chrono>

namespace isaacsim
{
namespace core
{
namespace nodes
{


omni::graph::core::INode* g_iNode;
omni::physx::IPhysx* g_physXInterface;
struct PhysicsStepData
{
    std::vector<NodeHandle> nodes;
    omni::physx::SubscriptionId stepSubscription;
};
struct HandleIdPair
{
    GraphHandle graphHandle;
    GraphInstanceID instanceId;
};
namespace
{
std::map<GraphHandle, PhysicsStepData> g_graphsWithPhysxStepNode;
}
class OgnOnPhysicsStep
{
public:
    OgnOnPhysicsStep()
    {
    }

    static void start(const NodeObj& nodeObj, GraphInstanceID instanceId)
    {
        auto& state = OgnOnPhysicsStepDatabase::sPerInstanceState<OgnOnPhysicsStep>(nodeObj, instanceId);
        auto graphObj = g_iNode->getGraph(nodeObj);
        auto pipelineStage = graphObj.iGraph->getPipelineStage(graphObj);
        if (pipelineStage != kGraphPipelineStage_OnDemand && state.m_initialized)
        {
            // NodeGraph changed from on-demand since last execution - unsubscribe node from step events
            unsubscribe(nodeObj);
        }
        else if (!state.m_initialized)
        {
            initialize(nodeObj, instanceId);
        }

        state.m_startTime = std::chrono::high_resolution_clock::now();
    }
    static void initialize(const NodeObj& nodeObj, GraphInstanceID instanceId)
    {
        // Acquire All interfaces
        if (!g_physXInterface)
        {
            g_physXInterface = carb::getCachedInterface<omni::physx::IPhysx>();
        }
        if (!g_iNode)
        {
            g_iNode = carb::getCachedInterface<omni::graph::core::INode>();
        }
        // Get information on the graph the node was inserted
        auto graphObj = g_iNode->getGraph(nodeObj);
        auto pipelineStage = graphObj.iGraph->getPipelineStage(graphObj);
        auto& state = OgnOnPhysicsStepDatabase::sPerInstanceState<OgnOnPhysicsStep>(nodeObj, instanceId);
        if (!state.m_timelineEventSub)
        {
            state.m_timeline = carb::getCachedInterface<omni::timeline::ITimeline>();
            state.m_timelineEventSub = carb::events::createSubscriptionToPopByType(
                state.m_timeline->getTimeline()->getTimelineEventStream(),
                static_cast<carb::events::EventType>(omni::timeline::TimelineEventType::ePlay),
                [nodeObj, instanceId](const carb::events::IEvent* e) { start(nodeObj, instanceId); }, 0,
                "IsaacSimOGNPhysicStepsTimelineEventHandler");
        }
        if (pipelineStage != kGraphPipelineStage_OnDemand)
        {
            CARB_LOG_ERROR(
                "Physics OnSimulationStep node detected in a non on-demand Graph. Node will only trigger events if the parent Graph is set to compute on-demand. (%s))",
                g_iNode->getPrimPath(nodeObj));
            // graphObj.iGraph->changePipelineStage(graphObj, kGraphPipelineStage_OnDemand);
        }
        else
        {
            // Check if another Step node was already inserted before subscribing

            if (g_graphsWithPhysxStepNode.find(graphObj.graphHandle) == g_graphsWithPhysxStepNode.end())
            {
                g_graphsWithPhysxStepNode[graphObj.graphHandle] = PhysicsStepData();
                state.m_graphHandlePair = HandleIdPair{ graphObj.graphHandle, instanceId };
                g_graphsWithPhysxStepNode[graphObj.graphHandle].stepSubscription =
                    g_physXInterface->subscribePhysicsOnStepEvents(
                        false, 0, onPhysicsStep, reinterpret_cast<void*>(&state.m_graphHandlePair));
            }
            g_graphsWithPhysxStepNode[graphObj.graphHandle].nodes.push_back(nodeObj.nodeHandle);
            state.m_initialized = true;
        }
    }
    static void initInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        initialize(nodeObj, instanceId);
    }


    static void unsubscribe(const NodeObj& nodeObj)
    {
        const INode* const iNode = nodeObj.iNode;
        if (!iNode)
        {
            return;
        }
        auto graphObj = g_iNode->getGraph(nodeObj);
        auto graphData = g_graphsWithPhysxStepNode.find(graphObj.graphHandle);

        // Sanity check if graph still exists
        if (graphData != g_graphsWithPhysxStepNode.end())
        {
            // Remove node from list of nodes on this graph
            graphData->second.nodes.erase(
                std::remove(graphData->second.nodes.begin(), graphData->second.nodes.end(), nodeObj.nodeHandle),
                graphData->second.nodes.end());
            // If No more step nodes are present, remove graph from map
            if (graphData->second.nodes.empty())
            {
                g_physXInterface->unsubscribePhysicsOnStepEvents(graphData->second.stepSubscription);
                g_graphsWithPhysxStepNode.erase(graphData);
            }
        }
        auto& state = OgnOnPhysicsStepDatabase::sSharedState<OgnOnPhysicsStep>(nodeObj);
        state.m_initialized = false;
    }

    static void releaseInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        unsubscribe(nodeObj);
        auto& state = OgnOnPhysicsStepDatabase::sPerInstanceState<OgnOnPhysicsStep>(nodeObj, instanceId);
        state.m_timelineEventSub->unsubscribe();
    }


    static void onPhysicsStep(float timeElapsed, void* userData)
    {
        CARB_PROFILE_ZONE(0, "[IsaacSim] OgnOnPysicsStep::onPhysicsStep");
        HandleIdPair* idpair = reinterpret_cast<HandleIdPair*>(userData);
        auto graphHandle = idpair->graphHandle;
        auto instanceId = idpair->instanceId;
        auto graphData = g_graphsWithPhysxStepNode.find(graphHandle);
        // Sanity check if graph exists
        if (graphData != g_graphsWithPhysxStepNode.end())
        {
            // Double sanity check if there are step nodes in this graph
            if (!graphData->second.nodes.empty())
            {
                NodeObj node = g_iNode->getNodeFromHandle(graphData->second.nodes[0]);
                auto graphObj = g_iNode->getGraph(node);
                // Iterate over all step nodes enabling them to receive the evaluate input
                for (auto handle : graphData->second.nodes)
                {
                    NodeObj currentNode = g_iNode->getNodeFromHandle(handle);
                    auto& state = OgnOnPhysicsStepDatabase::sPerInstanceState<OgnOnPhysicsStep>(currentNode, instanceId);
                    state.m_dt = timeElapsed;
                    state.m_isSet = true;
                }

                graphObj.iGraph->evaluate(graphObj);
            }
        }
    }

    static bool compute(OgnOnPhysicsStepDatabase& db)
    {
        auto& state = db.perInstanceState<OgnOnPhysicsStep>();
        // Update node with trigger event
        if (state.m_isSet)
        {
            state.m_isSet = false;
            db.outputs.deltaSimulationTime() = state.m_dt;
            db.outputs.step() = kExecutionAttributeStateEnabled;
            auto end = std::chrono::high_resolution_clock::now();
            db.outputs.deltaSystemTime() =
                std::chrono::duration_cast<std::chrono::microseconds>(end - state.m_startTime).count() * 1.0e-6f;
            state.m_startTime = end;
        }
        else
        {
            CARB_LOG_INFO("Graph evaluated outside physics step. A step will not be triggered this time.(%s))",
                          g_iNode->getPrimPath(db.abi_node()));
        }
        return true;
    }


private:
    float m_dt = 0.0f;
    bool m_initialized = false;
    bool m_isSet = false;
    std::chrono::time_point<std::chrono::high_resolution_clock> m_startTime;
    HandleIdPair m_graphHandlePair;
    carb::events::ISubscriptionPtr m_timelineEventSub = nullptr;
    omni::timeline::ITimeline* m_timeline = nullptr;
};

REGISTER_OGN_NODE()
} // core_nodes
} // isaac
} // omni
