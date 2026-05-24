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
#include <pch/UsdPCH.h>
// clang-format on
#include "isaacsim/robot/schema/robot_schema.h"
#include "isaacsim/robot/surface_gripper/SurfaceGripperManager.h"

#include <extensions/PxJoint.h>
#include <omni/physics/tensors/BodyTypes.h>
#include <omni/physx/IPhysx.h>
#include <omni/physx/IPhysxSceneQuery.h>
#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/usdPhysics/filteredPairsAPI.h>

#include <PxConstraint.h>
#include <PxRigidActor.h>

// Threading utilities
#include "isaacsim/robot/surface_gripper/ThreadUtils.h"
namespace isaacsim
{
namespace robot
{
namespace surface_gripper
{

std::vector<std::string> SurfaceGripperManager::getComponentIsAVector() const
{
    return { isaacsim::robot::schema::className(isaacsim::robot::schema::Classes::SURFACE_GRIPPER).GetString() };
}

void SurfaceGripperManager::onStop()
{
    for (auto& component : m_components)
    {
        component.second->mDoStart = true;
        component.second->onStop();
    }
    if (m_gripperLayer)
    {
        m_gripperLayer->Clear();
    }

    // Reset timers when stopped
    this->m_timeSeconds = 0;
    this->m_timeNanoSeconds = 0;
}

void SurfaceGripperManager::onComponentAdd(const pxr::UsdPrim& prim)
{
    CARB_PROFILE_ZONE(0, "[IsaacSim] SurfaceGripperManager::onComponentAdd");
    static const pxr::TfToken surfaceGripperToken(
        isaacsim::robot::schema::className(isaacsim::robot::schema::Classes::SURFACE_GRIPPER));

    if (pxr::TfToken(prim.GetTypeName()) == surfaceGripperToken)
    {
        std::unique_ptr<SurfaceGripperComponent> component = std::make_unique<SurfaceGripperComponent>();
        component->initialize(prim, m_stage, m_writeToUsd);

        m_components[prim.GetPath().GetString()] = std::move(component);
    }
    if (m_components.size() > 0)
    {
        if (!m_gripperLayer)
        {
            // Create a new anonymous layer for gripper operations to not persist after simulation stops
            m_gripperLayer = pxr::SdfLayer::CreateAnonymous("anon_gripper_ops_");

            auto sessionLayer = m_stage->GetSessionLayer();
            if (sessionLayer)
            {
                sessionLayer->GetSubLayerPaths().push_back(m_gripperLayer->GetIdentifier());
            }

            if (m_gripperLayer)
            {
                m_gripperLayer->Clear();
            }
        }
    }
}

void SurfaceGripperManager::initialize(const pxr::UsdStageWeakPtr stage)
{
    isaacsim::core::includes::PrimManagerBase<SurfaceGripperComponent>::initialize(stage);
    m_stage = stage;
    m_gripperLayer = nullptr;
}

void SurfaceGripperManager::onComponentChange(const pxr::UsdPrim& prim)
{
    isaacsim::core::includes::PrimManagerBase<SurfaceGripperComponent>::onComponentChange(prim);

    // Update properties of this prim
    if (m_components.find(prim.GetPath().GetString()) != m_components.end())
    {
        m_components[prim.GetPath().GetString()]->onComponentChange();
    }
}

void SurfaceGripperManager::onPhysicsStep(const double& dt)
{
    CARB_PROFILE_ZONE(0, "[IsaacSim] SurfaceGripperManager::onPhysicsStep");

    isaacsim::robot::surface_gripper::parallelForIndex(m_components.size(),
                                                       [&](size_t i)
                                                       {
                                                           auto it = m_components.begin();
                                                           std::advance(it, i);
                                                           it->second->onPhysicsStep(dt);
                                                       });
    // Collect all PhysX and USD actions from components
    std::vector<PhysxAction> actions;
    std::vector<UsdAction> usdActions;
    for (auto& kv : m_components)
    {
        kv.second->consumePhysxActions(actions);
        kv.second->consumeUsdActions(usdActions);
    }

    // Execute PhysX actions serially
    {
        CARB_PROFILE_ZONE(0, "[IsaacSim] SurfaceGripperManager::onPhysicsStep::PhysxAction");
        for (const PhysxAction& a : actions)
        {
            if (a.type == PhysxActionType::Attach)
            {
                physx::PxJoint* joint = static_cast<physx::PxJoint*>(
                    m_physXInterface->getPhysXPtr(pxr::SdfPath(a.jointPath), omni::physx::PhysXType::ePTJoint));
                if (!joint)
                    continue;
                physx::PxRigidActor* actor0 = a.actor0;
                physx::PxRigidActor* actor1 = a.actor1;
                if (!actor0 || !actor1)
                    continue;
                joint->setActors(actor0, actor1);
                joint->setLocalPose(physx::PxJointActorIndex::eACTOR1, a.localPose1);
                // On attach: constraints disabled, collision disabled
                joint->setConstraintFlag(physx::PxConstraintFlag::eDISABLE_CONSTRAINT, false);
                joint->setConstraintFlag(physx::PxConstraintFlag::eCOLLISION_ENABLED, false);
            }
            else if (a.type == PhysxActionType::Detach)
            {
                physx::PxJoint* joint = static_cast<physx::PxJoint*>(
                    m_physXInterface->getPhysXPtr(pxr::SdfPath(a.jointPath), omni::physx::PhysXType::ePTJoint));
                if (!joint)
                    continue;
                // On detach: constraints enabled, collision enabled
                joint->setConstraintFlag(physx::PxConstraintFlag::eDISABLE_CONSTRAINT, true);
                joint->setConstraintFlag(physx::PxConstraintFlag::eCOLLISION_ENABLED, true);
            }
        }
    }

    // Execute USD actions serially (one edit context scope)
    if (m_writeToUsd && !usdActions.empty() && m_stage)
    {
        CARB_PROFILE_ZONE(0, "[IsaacSim] SurfaceGripperManager::onPhysicsStep::UsdAction");
        pxr::SdfChangeBlock changeBlock;
        auto layer = m_stage->GetRootLayer();
        pxr::SdfLayerRefPtr refPtr(layer.operator->());
        pxr::UsdEditContext context(m_stage, m_gripperLayer ? m_gripperLayer : refPtr);
        for (const UsdAction& ua : usdActions)
        {
            switch (ua.type)
            {
            case UsdActionType::WriteStatus:
            {
                pxr::UsdPrim selfPrim = m_stage->GetPrimAtPath(pxr::SdfPath(ua.primPath));
                if (!selfPrim)
                    continue;
                pxr::UsdAttribute gripperStatusAttr = selfPrim.GetAttribute(
                    isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::STATUS));
                if (gripperStatusAttr)
                {
                    gripperStatusAttr.Set(pxr::TfToken(ua.statusToken));
                }
                break;
            }
            case UsdActionType::WriteGrippedObjectsAndFilters:
            {
                pxr::UsdPrim selfPrim = m_stage->GetPrimAtPath(pxr::SdfPath(ua.primPath));
                if (!selfPrim)
                    continue;
                pxr::SdfPathVector objectPathsVec;
                objectPathsVec.reserve(ua.grippedObjectPaths.size());
                for (const auto& p : ua.grippedObjectPaths)
                    objectPathsVec.push_back(pxr::SdfPath(p));

                pxr::UsdRelationship rel = selfPrim.GetRelationship(
                    isaacsim::robot::schema::relationNames.at(isaacsim::robot::schema::Relations::GRIPPED_OBJECTS));
                if (!rel)
                {
                    rel = selfPrim.CreateRelationship(
                        isaacsim::robot::schema::relationNames.at(isaacsim::robot::schema::Relations::GRIPPED_OBJECTS),
                        false);
                }
                if (ua.grippedObjectPaths.empty())
                    rel.ClearTargets(true);
                else
                    rel.SetTargets(objectPathsVec);

                if (!ua.body0PathForFilterPairs.empty())
                {
                    pxr::UsdPrim body0Prim = m_stage->GetPrimAtPath(pxr::SdfPath(ua.body0PathForFilterPairs));
                    if (body0Prim)
                    {
                        pxr::UsdPhysicsFilteredPairsAPI filterPairsAPI = pxr::UsdPhysicsFilteredPairsAPI(body0Prim);
                        if (!filterPairsAPI)
                            filterPairsAPI = pxr::UsdPhysicsFilteredPairsAPI::Apply(body0Prim);
                        if (ua.grippedObjectPaths.empty())
                            filterPairsAPI.GetFilteredPairsRel().ClearTargets(true);
                        else
                            filterPairsAPI.GetFilteredPairsRel().SetTargets(objectPathsVec);
                    }
                }
                break;
            }
            case UsdActionType::WriteAttachmentPointBatch:
            {
                // Apply AttachmentPointAPI
                for (const std::string& pathStr : ua.apiPathsToApply)
                {
                    pxr::UsdPrim p = m_stage->GetPrimAtPath(pxr::SdfPath(pathStr));
                    if (p && !p.HasAPI(isaacsim::robot::schema::className(
                                 isaacsim::robot::schema::Classes::ATTACHMENT_POINT_API)))
                    {
                        isaacsim::robot::schema::ApplyAttachmentPointAPI(p);
                    }
                }

                // Set ExcludeFromArticulation
                for (const std::string& pathStr : ua.excludeFromArticulationPaths)
                {
                    pxr::UsdPrim p = m_stage->GetPrimAtPath(pxr::SdfPath(pathStr));
                    if (p)
                    {
                        pxr::UsdPhysicsJoint joint(p);
                        joint.GetExcludeFromArticulationAttr().Set(true);
                    }
                }

                // Write clearance offsets
                for (const auto& kv : ua.clearanceOffsets)
                {
                    const std::string& pathStr = kv.first;
                    float value = kv.second;
                    pxr::UsdPrim p = m_stage->GetPrimAtPath(pxr::SdfPath(pathStr));
                    if (!p)
                        continue;
                    pxr::UsdAttribute attr = p.GetAttribute(isaacsim::robot::schema::getAttributeName(
                        isaacsim::robot::schema::Attributes::CLEARANCE_OFFSET));
                    if (!attr)
                    {
                        attr = p.CreateAttribute(isaacsim::robot::schema::getAttributeName(
                                                     isaacsim::robot::schema::Attributes::CLEARANCE_OFFSET),
                                                 pxr::SdfValueTypeNames->Float, false);
                    }
                    attr.Set(value);
                }
                break;
            }
            default:
                break;
            }
        }
    }
}

void SurfaceGripperManager::onStart()
{
    if (!m_stage)
    {
        return;
    }
    for (auto& component : m_components)
    {
        if (component.second->mDoStart == true)
        {
            component.second->onStart();
            component.second->mDoStart = false;
        }
    }
}
void SurfaceGripperManager::tick(double dt)
{
    if (!m_stage)
    {
        return;
    }

    for (auto& component : m_components)
    {
        component.second->preTick();
        component.second->tick();
    }
}

void SurfaceGripperManager::setWriteToUsd(bool writeToUsd)
{
    m_writeToUsd = writeToUsd;
    for (auto& component : m_components)
    {
        component.second->setWriteToUsd(writeToUsd);
    }
}

bool SurfaceGripperManager::setGripperStatus(const std::string& primPath, GripperStatus status)
{
    if (m_writeToUsd)
    {
        pxr::SdfChangeBlock changeBlock;
        auto layer = m_stage->GetRootLayer();
        pxr::SdfLayerRefPtr refPtr(layer.operator->());
        pxr::UsdEditContext context(m_stage, m_gripperLayer ? m_gripperLayer : refPtr);
        auto it = m_components.find(primPath);
        if (it != m_components.end())
        {
            return it->second->setGripperStatus(status);
        }
    }
    else
    {
        auto it = m_components.find(primPath);
        if (it != m_components.end())
        {
            return it->second->setGripperStatus(status);
        }
    }
    return false;
}

GripperStatus SurfaceGripperManager::getGripperStatus(const std::string& primPath)
{
    auto it = m_components.find(primPath);
    if (it != m_components.end())
    {
        return it->second->getGripperStatus();
    }
    else
    {
        CARB_LOG_ERROR("Gripper not found: %s", primPath.c_str());
    }
    return GripperStatus::Open; // default if not found
}

std::vector<std::string> SurfaceGripperManager::getAllGrippers() const
{
    std::vector<std::string> result;
    for (const auto& component : m_components)
    {
        result.push_back(component.first);
    }
    return result;
}

SurfaceGripperComponent* SurfaceGripperManager::getGripper(const std::string& primPath)
{
    auto it = m_components.find(primPath);
    if (it != m_components.end())
    {
        return it->second.get();
    }
    return nullptr;
}

SurfaceGripperComponent* SurfaceGripperManager::getGripper(const pxr::UsdPrim& prim)
{
    return getGripper(prim.GetPath().GetString());
}

} // namespace surface_gripper
} // namespace robot
} // namespace isaacsim
