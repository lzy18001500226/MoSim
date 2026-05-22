// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <OgnIsaacConveyorDatabase.h>

///
#include <omni/usd/UsdContext.h>
///

#include <carb/eventdispatcher/IEventDispatcher.h>
#include <carb/events/IEvents.h>

#include <omni/fabric/FabricUSD.h>
#include <physxSchema/physxSurfaceVelocityAPI.h>
#include <pxr/pxr.h>
#include <pxr/usd/usdPhysics/rigidBodyAPI.h>

namespace isaacsim
{
namespace asset
{
namespace gen
{
namespace conveyor
{

/**
 * @brief Class that implements the conveyor belt node functionality
 */
class OgnIsaacConveyor
{
public:
    /**
     * @brief Initializes a new instance of the conveyor node
     * @param nodeObj Node object reference
     * @param instanceId Graph instance identifier
     */
    static void initInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        auto& state = OgnIsaacConveyorDatabase::sPerInstanceState<OgnIsaacConveyor>(nodeObj, instanceId);
        auto ed = carb::getCachedInterface<carb::eventdispatcher::IEventDispatcher>();

        // Create subscriptions to the stage event stream
        auto usdContext = omni::usd::UsdContext::getContext();
        state.m_eventSubscription[0] =
            ed->observeEvent(carb::RStringKey("isaacsim.asset.gen.conveyor/OgnIsaacConveyor/StopPlay"),
                             carb::eventdispatcher::kDefaultOrder,
                             usdContext->stageEventName(omni::usd::StageEventType::eAnimationStopPlay),
                             [nodeObj](const carb::eventdispatcher::Event& e)
                             {
                                 if (nodeObj.iNode->isValid(nodeObj))
                                 {
                                     nodeObj.iNode->requestCompute(nodeObj);
                                 }
                             });
        state.m_eventSubscription[1] =
            ed->observeEvent(carb::RStringKey("isaacsim.asset.gen.conveyor/OgnIsaacConveyor/StartPlay"),
                             carb::eventdispatcher::kDefaultOrder,
                             usdContext->stageEventName(omni::usd::StageEventType::eAnimationStartPlay),
                             [nodeObj](const carb::eventdispatcher::Event& e)
                             {
                                 if (nodeObj.iNode->isValid(nodeObj))
                                 {
                                     nodeObj.iNode->requestCompute(nodeObj);
                                 }
                             });
    }

    /**
     * @brief Computes the conveyor belt physics and animation state
     * @param db Database containing node state and parameters
     * @return True if computation succeeded, false otherwise
     */
    static bool compute(OgnIsaacConveyorDatabase& db)
    {
        if (db.inputs.enabled())
        {
            pxr::UsdStagePtr stage = omni::usd::UsdContext::getContext()->getStage();
            const auto& primPath = db.inputs.conveyorPrim();
            UsdPrim conveyorPrim;
            if (!primPath.empty())
            {
                conveyorPrim = stage->GetPrimAtPath(omni::fabric::toSdfPath(primPath[0]));
            }
            else
            {
                db.logError("No prim path found for the conveyor");
                return false;
            }

            auto& state = db.perInstanceState<OgnIsaacConveyor>();
            pxr::UsdPhysicsRigidBodyAPI physicsConveyor(conveyorPrim);
            pxr::GfVec3f currentVelocity;
            auto targetVelocity = db.inputs.direction() * db.inputs.velocity();

            if (physicsConveyor)
            {
                auto surfaceVelocity = pxr::PhysxSchemaPhysxSurfaceVelocityAPI::Apply(conveyorPrim);

                if (db.inputs.curved())
                {
                    surfaceVelocity.GetSurfaceAngularVelocityAttr().Get(&currentVelocity);
                }
                else
                {
                    surfaceVelocity.GetSurfaceVelocityAttr().Get(&currentVelocity);
                }
            }
            else
            {
                db.logError("Selected Prim is not a Rigid Body");
                return false;
            }

            bool hasVelocityChanged = (currentVelocity - targetVelocity).GetLengthSq() > 1e-6f;
            if (state.m_onStart || hasVelocityChanged)
            {
                state.m_velocity = db.inputs.velocity();

                auto surfaceVelocity = pxr::PhysxSchemaPhysxSurfaceVelocityAPI::Apply(conveyorPrim);
                // Cycle the enabled attr to hardwire it to work on first sim
                surfaceVelocity.GetSurfaceVelocityEnabledAttr().Set(false);
                surfaceVelocity.GetSurfaceVelocityEnabledAttr().Set(true);

                if (db.inputs.curved())
                {
                    surfaceVelocity.GetSurfaceAngularVelocityAttr().Set(targetVelocity);
                }
                else
                {
                    surfaceVelocity.GetSurfaceVelocityAttr().Set(targetVelocity);
                }

                if (state.m_onStart)
                {
                    state.m_onStart = false;
                    state.m_shaderAttributes.clear();
                    state.m_initialShaderStates.clear();

                    for (auto meshPrim : pxr::UsdPrimRange(conveyorPrim))
                    {
                        if (pxr::UsdGeomImageable(meshPrim))
                        {
                            auto material = pxr::UsdShadeMaterialBindingAPI(meshPrim).ComputeBoundMaterial();
                            for (auto shader : pxr::UsdPrimRange(material.GetPrim()))
                            {
                                auto shaderPrim = stage->OverridePrim(shader.GetPrim().GetPath());
                                auto textureAttribute = shaderPrim.GetAttribute(pxr::TfToken("inputs:texture_translate"));
                                if (!textureAttribute)
                                {
                                    pxr::UsdEditContext context(stage, stage->GetRootLayer());
                                    textureAttribute = shaderPrim.CreateAttribute(
                                        pxr::TfToken("inputs:texture_translate"), pxr::SdfValueTypeNames->Float2, false);
                                    textureAttribute.Set(pxr::GfVec2f(0.00000f, 0.0f));
                                }

                                if (textureAttribute)
                                {
                                    pxr::UsdEditContext context(stage, stage->GetRootLayer());
                                    state.m_shaderAttributes.push_back(textureAttribute);
                                    pxr::GfVec2f textureTranslation;
                                    textureAttribute.Get(&textureTranslation);
                                    state.m_initialShaderStates.push_back(textureTranslation);
                                    textureTranslation[0] += 0.0000f;
                                    textureAttribute.Set(textureTranslation);
                                }
                            }
                        }
                    }
                }

                if (state.m_onEnd)
                {
                    pxr::SdfChangeBlock changeBlock;
                    for (size_t i = 0; i < state.m_shaderAttributes.size(); i++)
                    {
                        state.m_shaderAttributes[i].Set(state.m_initialShaderStates[i]);
                    }
                }
            }

            if (db.inputs.animateTexture())
            {
                if (state.m_velocity != 0 && db.inputs.onStep())
                {
                    pxr::UsdStagePtr currentStage = omni::usd::UsdContext::getContext()->getStage();
                    pxr::UsdEditContext context(currentStage, currentStage->GetRootLayer());
                    pxr::SdfChangeBlock changeBlock;

                    for (auto& attribute : state.m_shaderAttributes)
                    {
                        pxr::GfVec2f textureTranslation;
                        attribute.Get(&textureTranslation);
                        textureTranslation += pxr::GfVec2f(db.inputs.delta() * db.inputs.animateDirection() *
                                                           state.m_velocity * db.inputs.animateScale());
                        attribute.Set(textureTranslation);
                    }
                }
            }
        }
        return true;
    }

private:
    std::vector<pxr::UsdAttribute> m_shaderAttributes;
    std::vector<pxr::GfVec2f> m_initialShaderStates;
    float m_velocity;
    pxr::GfVec3f m_direction;
    bool m_onStart;
    bool m_onEnd;
    carb::eventdispatcher::ObserverGuard m_eventSubscription[2];
};

REGISTER_OGN_NODE()

} // namespace conveyor
} // namespace gen
} // namespace asset
} // namespace isaacsim
