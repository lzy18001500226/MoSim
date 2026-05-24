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
#include "isaacsim/robot/surface_gripper/SurfaceGripperComponent.h"

#include <extensions/PxJoint.h>
#include <omni/physics/tensors/BodyTypes.h>
#include <omni/physx/IPhysx.h>
#include <omni/physx/IPhysxSceneQuery.h>
#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/usdPhysics/filteredPairsAPI.h>

#include <PxConstraint.h>
#include <PxRigidActor.h>


namespace
{
omni::physx::IPhysx* g_physx = nullptr;
}

namespace isaacsim
{
namespace robot
{
namespace surface_gripper
{

inline const pxr::SdfPath& intToPath(const uint64_t& path)
{
    static_assert(sizeof(pxr::SdfPath) == sizeof(uint64_t), "Change to make the same size as pxr::SdfPath");

    return reinterpret_cast<const pxr::SdfPath&>(path);
}


void SurfaceGripperComponent::initialize(const pxr::UsdPrim& prim, const pxr::UsdStageWeakPtr stage, bool writeToUsd)
{
    g_physx = carb::getCachedInterface<omni::physx::IPhysx>();
    isaacsim::core::includes::ComponentBase<pxr::UsdPrim>::initialize(prim, stage);
    m_primPath = prim.GetPath();
    m_writeToUsd = writeToUsd;
    mDoStart = true;

    updateGripperProperties();
}

void SurfaceGripperComponent::onComponentChange()
{
    // Update surface gripper properties from the prim
    updateGripperProperties();
}

void SurfaceGripperComponent::onStart()
{

    onComponentChange();
    // Get attachment points (D6 joints)
    updateAttachmentPoints();
    if (m_status == GripperStatus::Closed)
    {
        updateClosedGripper();
    }
    else
    {
        updateOpenGripper();
    }
    m_isInitialized = true;
}

void SurfaceGripperComponent::onPhysicsStep(double dt)
{
    // Early return if component is not initialized
    if (!m_isInitialized)
        return;

    // Use SdfChangeBlock to batch USD changes for better performance
    // pxr::SdfChangeBlock changeBlock;


    // Update joint settling counters for inactive attachment points
    for (const auto& attachmentPath : m_inactiveAttachmentPoints)
    {
        if (m_jointSettlingCounters[attachmentPath] > 0)
        {
            m_jointSettlingCounters[attachmentPath] = m_jointSettlingCounters[attachmentPath] - 1;
        }
    }

    // Handle retry timeout for closing gripper
    if (m_status == GripperStatus::Closing && m_retryInterval > 0 && m_retryCloseActive &&
        !m_inactiveAttachmentPoints.empty())
    {
        m_retryElapsed += dt;
        if (m_retryElapsed > m_retryInterval)
        {
            // Timeout reached, stop trying to close
            m_retryCloseActive = false;
            m_retryElapsed = 0.0;
        }
    }

    // Update gripper state based on current status
    if (m_status == GripperStatus::Closed || m_status == GripperStatus::Closing)
    {
        if (m_retryCloseActive || !m_activeAttachmentPoints.empty())
        {
            updateClosedGripper();
        }
        else
        {
            updateOpenGripper();
        }
    }
    else
    {
        // For GripperStatus::Open or any other state
        updateOpenGripper();
    }
}

void SurfaceGripperComponent::preTick()
{
    // Nothing to do in preTick for now
}

void SurfaceGripperComponent::tick()
{
    if (!m_isInitialized || !m_isEnabled)
        return;

    // Update the visualization or any non-physics aspects
    // For example, we could update visual indicators of gripper state
}

void SurfaceGripperComponent::onStop()
{
    // First release all objects with physics changes
    releaseAllObjects();


    m_activeAttachmentPoints.clear();
    m_inactiveAttachmentPoints = m_attachmentPoints;
    m_grippedObjects.clear();
    m_isInitialized = false;
    mDoStart = true;
}

bool SurfaceGripperComponent::setGripperStatus(GripperStatus status)
{
    GripperStatus gripperStatus = status;
    if (gripperStatus != GripperStatus::Open && gripperStatus != GripperStatus::Closed &&
        gripperStatus != GripperStatus::Closing)
        return false;
    if (gripperStatus != m_status)
    {

        if (gripperStatus == GripperStatus::Open)
        {
            updateOpenGripper();
            m_status = GripperStatus::Open;
            m_retryCloseActive = false;
        }
        else if ((gripperStatus == GripperStatus::Closed && m_status != GripperStatus::Closing) ||
                 gripperStatus == GripperStatus::Closing)
        {
            m_status = GripperStatus::Closing;
            m_retryCloseActive = true;
            updateClosedGripper();
            if (m_retryInterval > 0)
            {
                // Start retry timer
                m_retryElapsed = 0.0;
            }
            else
            {
                m_retryCloseActive = false;
            }
        }
    }

    return true;
}

void SurfaceGripperComponent::updateGripperProperties()
{
    auto prim = m_stage->GetPrimAtPath(m_primPath);
    if (!prim)
    {
        return;
    }
    // Get forward axis
    pxr::UsdAttribute forwardAxisAttr =
        prim.GetAttribute(isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::FORWARD_AXIS));
    if (forwardAxisAttr)
    {
        pxr::TfToken forwardAxis;
        forwardAxisAttr.Get(&forwardAxis);
        m_forwardAxis = forwardAxis.GetString();
    }

    // Get status
    pxr::UsdAttribute statusAttr =
        prim.GetAttribute(isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::STATUS));
    if (statusAttr)
    {
        pxr::TfToken status;
        statusAttr.Get(&status);
        m_status = GripperStatusFromToken(status);
    }

    // Get retry interval
    pxr::UsdAttribute retryIntervalAttr =
        prim.GetAttribute(isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::RETRY_INTERVAL));
    if (retryIntervalAttr)
    {
        retryIntervalAttr.Get(&m_retryInterval);
    }

    // Get force limits
    pxr::UsdAttribute shearForceLimitAttr = prim.GetAttribute(
        isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::SHEAR_FORCE_LIMIT));
    if (shearForceLimitAttr)
    {
        shearForceLimitAttr.Get(&m_shearForceLimit);
    }

    pxr::UsdAttribute coaxialForceLimitAttr = prim.GetAttribute(
        isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::COAXIAL_FORCE_LIMIT));
    if (coaxialForceLimitAttr)
    {
        coaxialForceLimitAttr.Get(&m_coaxialForceLimit);
    }

    pxr::UsdAttribute maxGripDistanceAttr = prim.GetAttribute(
        isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::MAX_GRIP_DISTANCE));
    if (maxGripDistanceAttr)
    {
        maxGripDistanceAttr.Get(&m_maxGripDistance);
    }
}

void SurfaceGripperComponent::updateAttachmentPoints()
{
    auto prim = m_stage->GetPrimAtPath(m_primPath);
    m_attachmentPoints.clear();

    pxr::UsdRelationship attachmentPointsRel = prim.GetRelationship(
        isaacsim::robot::schema::relationNames.at(isaacsim::robot::schema::Relations::ATTACHMENT_POINTS));
    if (!attachmentPointsRel)
        return;

    std::vector<pxr::SdfPath> attachmentPaths;
    attachmentPointsRel.GetTargets(&attachmentPaths);
    // Preallocate buffers
    m_attachmentPoints.reserve(attachmentPaths.size());
    m_grippedObjectsBuffer.reserve(attachmentPaths.size());
    m_grippedObjects.reserve(attachmentPaths.size());
    m_activeAttachmentPoints.reserve(attachmentPaths.size());
    m_inactiveAttachmentPoints.reserve(attachmentPaths.size());
    m_jointSettlingCounters.reserve(attachmentPaths.size());
    m_jointForwardAxis.clear();
    m_jointClearanceOffset.clear();
    std::vector<std::string> applyApiPaths;
    std::vector<std::string> excludeFromArticulationPaths;
    std::vector<std::pair<std::string, float>> clearanceOffsets;
    applyApiPaths.reserve(attachmentPaths.size());
    excludeFromArticulationPaths.reserve(attachmentPaths.size());
    clearanceOffsets.reserve(attachmentPaths.size());
    for (const auto& path : attachmentPaths)
    {
        pxr::UsdPrim attachmentPrim = prim.GetPrimAtPath(path);
        if (attachmentPrim && attachmentPrim.IsA<pxr::UsdPhysicsJoint>())
        {
            if (!attachmentPrim.HasAPI(
                    isaacsim::robot::schema::className(isaacsim::robot::schema::Classes::ATTACHMENT_POINT_API)))
            {
                applyApiPaths.push_back(path.GetString());
            }
            pxr::UsdPhysicsJoint joint(attachmentPrim);

            bool excludeFromArticulation;
            joint.GetExcludeFromArticulationAttr().Get(&excludeFromArticulation);
            if (!excludeFromArticulation)
            {
                excludeFromArticulationPaths.push_back(path.GetString());
            }
            physx::PxJoint* px_joint =
                static_cast<physx::PxJoint*>(g_physx->getPhysXPtr((path), omni::physx::PhysXType::ePTJoint));
            if (!px_joint)
            {
                CARB_LOG_WARN("   Gripper %s has no joint at attachment point %s", m_primPath.GetText(), path.GetText());
                continue;
            }
            px_joint->setConstraintFlag(physx::PxConstraintFlag::eDISABLE_CONSTRAINT, m_status == GripperStatus::Open);
            m_attachmentPoints.insert(path.GetString());
            m_jointSettlingCounters[path.GetString()] = 0;

            // Cache per-joint forward axis
            pxr::TfToken jointAxisToken;
            attachmentPrim
                .GetAttribute(isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::FORWARD_AXIS))
                .Get(&jointAxisToken);
            Axis axisEnum = Axis::Z;
            if (!jointAxisToken.IsEmpty())
            {
                const char c = std::toupper(jointAxisToken.GetText()[0]);
                axisEnum = (c == 'X') ? Axis::X : (c == 'Y') ? Axis::Y : Axis::Z;
            }
            m_jointForwardAxis[path.GetString()] = axisEnum;

            // Cache clearance offset if present
            float clearanceOffset = 0.0f;
            pxr::UsdAttribute clearanceOffsetAttr = attachmentPrim.GetAttribute(
                isaacsim::robot::schema::getAttributeName(isaacsim::robot::schema::Attributes::CLEARANCE_OFFSET));
            if (clearanceOffsetAttr)
            {
                clearanceOffsetAttr.Get(&clearanceOffset);
            }
            m_jointClearanceOffset[path.GetString()] = clearanceOffset;

            // Cache body0 path for filtered pairs from the first joint
            if (m_body0PathForFilterPairs.empty())
            {
                pxr::SdfPathVector targets0;
                joint.GetBody0Rel().GetTargets(&targets0);
                if (!targets0.empty())
                {
                    m_body0PathForFilterPairs = targets0[0].GetString();
                }
            }
        }
    }
    m_activeAttachmentPoints.clear();
    m_inactiveAttachmentPoints = m_attachmentPoints;

    if (m_writeToUsd)
    {
        _queueWriteAttachmentPointBatch(applyApiPaths, excludeFromArticulationPaths, clearanceOffsets);
    }
}

void SurfaceGripperComponent::updateGrippedObjectsList()
{
    pxr::SdfPathVector objectPathsVec;
    // Early return if gripper is open - no need to track gripped objects
    if (m_activeAttachmentPoints.empty())
    {
        if (!m_grippedObjects.empty())
        {
            m_grippedObjects.clear();
            if (m_writeToUsd)
            {
                std::vector<std::string> objectPaths; // empty -> clear targets
                _queueWriteGrippedObjectsAndFilters(objectPaths, m_body0PathForFilterPairs);
            }
        }
    }
    else
    {
        // Create a new set for current gripped objects
        m_grippedObjectsBuffer.clear();

        // Iterate through active attachment points to find gripped objects
        for (const auto& attachmentPath : m_activeAttachmentPoints)
        {
            physx::PxJoint* px_joint = static_cast<physx::PxJoint*>(
                g_physx->getPhysXPtr(pxr::SdfPath(attachmentPath), omni::physx::PhysXType::ePTJoint));

            // Skip invalid or broken joints
            if (!px_joint || (px_joint->getConstraintFlags() &
                              (physx::PxConstraintFlag::eBROKEN | physx::PxConstraintFlag::eDISABLE_CONSTRAINT)))
            {
                continue;
            }

            // Get actors attached to the joint
            physx::PxRigidActor *px_actor0, *px_actor1;
            px_joint->getActors(px_actor0, px_actor1);

            // Add the second actor to gripped objects if it exists and has a name
            if (px_actor1 && px_actor1->getName())
            {
                m_grippedObjectsBuffer.insert(px_actor1->getName());
            }
        }

        // Check if the set of gripped objects has changed
        if (m_grippedObjects == m_grippedObjectsBuffer)
        {
            // No change in gripped objects, nothing to update
            return;
        }

        // Update the gripped objects
        m_grippedObjects = m_grippedObjectsBuffer;


        if (m_writeToUsd)
        {
            std::vector<std::string> objectPaths(m_grippedObjects.begin(), m_grippedObjects.end());
            _queueWriteGrippedObjectsAndFilters(objectPaths, m_body0PathForFilterPairs);
        }
    }
}

void SurfaceGripperComponent::updateClosedGripper()
{
    // If we have no attachment points, we can't do anything
    if (m_attachmentPoints.empty())
    {
        return;
    }

    if (!m_inactiveAttachmentPoints.empty() && (m_status == GripperStatus::Closing || m_retryCloseActive))
    {
        findObjectsToGrip();
    }

    checkForceLimits();

    updateGrippedObjectsList();

    GripperStatus newStatus = m_status;

    if (m_inactiveAttachmentPoints.empty())
    {
        newStatus = GripperStatus::Closed;
    }
    else if (m_retryCloseActive)
    {
        newStatus = GripperStatus::Closing;
    }
    else if (m_activeAttachmentPoints.empty())
    {
        newStatus = GripperStatus::Open;
    }

    // Update status if it changed
    if (newStatus != m_status)
    {
        m_status = newStatus;

        // Reset retry elapsed time if we've finished closing
        if (newStatus == GripperStatus::Closed)
        {
            m_retryElapsed = 0.0f;
        }

        if (m_writeToUsd)
        {
            _queueWriteStatus(GripperStatusToToken(m_status).GetString());
        }
    }
}

void SurfaceGripperComponent::checkForceLimits()
{
    // Pre-allocate the vector to avoid resizing
    std::vector<std::string> apToRemove;
    apToRemove.reserve(m_activeAttachmentPoints.size());

    // Only check force limits if they are set
    const bool checkShearForce = m_shearForceLimit > 0.0f;
    const bool checkCoaxialForce = m_coaxialForceLimit > 0.0f;
    const bool checkForces = checkShearForce || checkCoaxialForce;

    for (const auto& attachmentPath : m_activeAttachmentPoints)
    {
        // Skip joints that are still settling
        if (m_jointSettlingCounters[attachmentPath] > 0)
        {
            m_jointSettlingCounters[attachmentPath]--;
            continue;
        }

        // Get PhysX joint
        physx::PxJoint* px_joint = static_cast<physx::PxJoint*>(
            g_physx->getPhysXPtr(pxr::SdfPath(attachmentPath), omni::physx::PhysXType::ePTJoint));

        if (!px_joint)
            continue;

        // Check if the joint is already disabled
        auto flags = px_joint->getConstraintFlags();
        if (flags & (physx::PxConstraintFlag::eDISABLE_CONSTRAINT | physx::PxConstraintFlag::eBROKEN))
        {
            apToRemove.push_back(attachmentPath);
            continue;
        }

        // Skip force checking if no limits are set
        if (!checkForces)
            continue;

        // Get force and actors
        physx::PxVec3 force, torque;
        physx::PxRigidActor *px_actor0, *px_actor1;
        px_joint->getActors(px_actor0, px_actor1);
        px_joint->getConstraint()->getForce(force, torque);


        // Compute world-space direction along joint axis
        Axis axis = _getJointForwardAxis(attachmentPath);
        physx::PxTransform worldTransform = _computeJointWorldTransform(px_joint, px_actor0);
        physx::PxVec3 direction = _directionFromAxisAndWorld(axis, worldTransform);

        // Calculate force components
        float coaxialForce = force.dot(direction);
        physx::PxVec3 shearForce;

        bool shouldRelease = false;

        // Only calculate shear force if needed
        if (checkShearForce)
        {
            shearForce = force - coaxialForce * direction;
            if (shearForce.magnitude() > m_shearForceLimit)
                shouldRelease = true;
        }

        // Check coaxial force if needed
        if (!shouldRelease && checkCoaxialForce && (coaxialForce) > m_coaxialForceLimit)
            shouldRelease = true;

        if (shouldRelease)
        {
            apToRemove.push_back(attachmentPath);
            _queueDetachJoint(attachmentPath);
        }
    }

    // Process all joints to be removed
    for (const auto& ap : apToRemove)
    {
        m_activeAttachmentPoints.erase(ap);
        m_inactiveAttachmentPoints.insert(ap);
        m_jointSettlingCounters[ap] = m_settlingDelay;
    }
}

void SurfaceGripperComponent::findObjectsToGrip()
{
    // Get physics query interface
    auto physxQuery = carb::getCachedInterface<omni::physx::IPhysxSceneQuery>();
    if (!physxQuery)
        return;

    std::set<pxr::SdfPath> targetSet(m_grippedObjects.begin(), m_grippedObjects.end());

    // Iterate through each attachment point sequentially
    std::vector<std::string> apToRemove;
    std::vector<std::pair<std::string, float>> clearanceOffsetsToPersist;

    for (const auto& attachmentPath : m_inactiveAttachmentPoints)
    {
        _processAttachmentForGrip(attachmentPath, apToRemove, clearanceOffsetsToPersist);
    }
    // Persist all clearance offset changes in one USD write
    if (!clearanceOffsetsToPersist.empty() && m_writeToUsd)
    {

        std::vector<std::string> emptyVec;
        _queueWriteAttachmentPointBatch(emptyVec, emptyVec, clearanceOffsetsToPersist);
    }
    for (const auto& ap : apToRemove)
    {
        m_inactiveAttachmentPoints.erase(ap);
        m_activeAttachmentPoints.insert(ap);

        m_jointSettlingCounters[ap] = m_settlingDelay; // Initialize settling counter
    }
}

void SurfaceGripperComponent::_processAttachmentForGrip(const std::string& attachmentPath,
                                                        std::vector<std::string>& apToRemove,
                                                        std::vector<std::pair<std::string, float>>& clearanceOffsetsToPersist)
{
    auto physxQuery = carb::getCachedInterface<omni::physx::IPhysxSceneQuery>();
    if (!physxQuery)
        return;

    if (m_jointSettlingCounters[attachmentPath] > 0)
    {
        m_jointSettlingCounters[attachmentPath]--;
        return;
    }

    physx::PxJoint* px_joint = static_cast<physx::PxJoint*>(
        g_physx->getPhysXPtr(pxr::SdfPath(attachmentPath), omni::physx::PhysXType::ePTJoint));
    if (!px_joint)
        return;

    physx::PxRigidActor *local_actor0 = nullptr, *local_actor1 = nullptr;
    px_joint->getActors(local_actor0, local_actor1);
    if (!local_actor0)
        return;

    physx::PxTransform worldTransform = _computeJointWorldTransform(px_joint, local_actor0);

    Axis axis = _getJointForwardAxis(attachmentPath);
    physx::PxVec3 dirPx = _directionFromAxisAndWorld(axis, worldTransform);
    pxr::GfVec3f direction(dirPx.x, dirPx.y, dirPx.z);

    pxr::GfVec3f worldPos(worldTransform.p.x, worldTransform.p.y, worldTransform.p.z);
    float clearanceOffset = 0.0f;
    auto itClear = m_jointClearanceOffset.find(attachmentPath);
    if (itClear != m_jointClearanceOffset.end())
    {
        clearanceOffset = itClear->second;
    }
    bool selfCollision = true;
    bool clearanceChanged = false;
    while (selfCollision)
    {
        pxr::GfVec3f rayStart = worldPos + direction * static_cast<float>(clearanceOffset);

        carb::Float3 _rayStart{ static_cast<float>(rayStart[0]), static_cast<float>(rayStart[1]),
                                static_cast<float>(rayStart[2]) };
        carb::Float3 _rayDir{ static_cast<float>(direction[0]), static_cast<float>(direction[1]),
                              static_cast<float>(direction[2]) };

        omni::physx::RaycastHit result;
        float rayLength = static_cast<float>(m_maxGripDistance) - clearanceOffset;
        if (rayLength <= 0.0f)
        {
            rayLength = 0.001f;
        }
        bool hit = physxQuery->raycastClosest(_rayStart, _rayDir, rayLength, result, false);

        if (hit)
        {
            pxr::SdfPath hitPath = pxr::SdfPath(intToPath(result.rigidBody).GetString());
            if (hitPath == pxr::SdfPath(local_actor0->getName()))
            {
                selfCollision = true;
                clearanceOffset += 0.001f;
                continue;
            }
            selfCollision = false;
            if (clearanceOffset > 0.0f)
            {
                float originalOffset = 0.0f;
                auto itC = m_jointClearanceOffset.find(attachmentPath);
                if (itC != m_jointClearanceOffset.end())
                {
                    originalOffset = itC->second;
                }
                if (originalOffset != clearanceOffset)
                {
                    clearanceChanged = true;
                    m_jointClearanceOffset[attachmentPath] = clearanceOffset;
                }
            }
            physx::PxRigidActor* hitActor =
                static_cast<physx::PxRigidActor*>(g_physx->getPhysXPtr(hitPath, omni::physx::PhysXType::ePTActor));
            if (!hitActor)
                return;
            physx::PxTransform hitWorldTransform = hitActor->getGlobalPose();

            physx::PxVec3 offsetTranslation =
                -physx::PxVec3(direction[0], direction[1], direction[2]) * (result.distance - clearanceOffset);
            physx::PxTransform offsetTransform(offsetTranslation, physx::PxQuat(physx::PxIdentity));
            physx::PxTransform adjustedWorldTransform = offsetTransform * worldTransform;
            physx::PxTransform hitLocalTransform = hitWorldTransform.transformInv(adjustedWorldTransform);

            _queueAttachJoint(attachmentPath, local_actor0, hitActor, hitLocalTransform);

            apToRemove.push_back(attachmentPath);
        }
        else
        {
            break;
        }
    }
    if (clearanceChanged)
    {
        clearanceOffsetsToPersist.emplace_back(attachmentPath, clearanceOffset);
    }
}

void SurfaceGripperComponent::updateOpenGripper()
{

    // Make sure we've released any gripped objects
    if (!m_grippedObjects.empty())
    {
        _queueReleaseAllObjectsActions();
        updateGrippedObjectsList();
        m_activeAttachmentPoints.clear();
        m_inactiveAttachmentPoints.insert(m_attachmentPoints.begin(), m_attachmentPoints.end());
    }
    if (m_status != GripperStatus::Open)
    {
        m_status = GripperStatus::Open;
        if (m_writeToUsd)
        {
            _queueWriteStatus(GripperStatusToToken(m_status).GetString());
        }
    }
}

void SurfaceGripperComponent::releaseAllObjects()
{
    // Early return if no attachment points exist
    if (m_attachmentPoints.empty())
    {
        return;
    }

    // Release all objects by disabling constraints on all attachment points
    for (const auto& attachmentPath : m_attachmentPoints)
    {
        // Immediate release used for non-physics-step flows (e.g., onStop)
        physx::PxJoint* px_joint = static_cast<physx::PxJoint*>(
            g_physx->getPhysXPtr(pxr::SdfPath(attachmentPath), omni::physx::PhysXType::ePTJoint));

        if (px_joint)
        {
            px_joint->setConstraintFlag(physx::PxConstraintFlag::eDISABLE_CONSTRAINT, true);
            px_joint->setConstraintFlag(physx::PxConstraintFlag::eCOLLISION_ENABLED, true);
        }
    }
    m_activeAttachmentPoints.clear();
    m_inactiveAttachmentPoints = m_attachmentPoints;


    // Reset settling counters for all attachment points
    for (const auto& ap : m_attachmentPoints)
    {
        m_jointSettlingCounters[ap] = m_settlingDelay;
    }
}

void SurfaceGripperComponent::consumePhysxActions(std::vector<PhysxAction>& outActions)
{
    if (!m_physxActions.empty())
    {
        outActions.insert(outActions.end(), std::make_move_iterator(m_physxActions.begin()),
                          std::make_move_iterator(m_physxActions.end()));
        m_physxActions.clear();
    }
}

void SurfaceGripperComponent::_queueReleaseAllObjectsActions()
{
    for (const auto& attachmentPath : m_attachmentPoints)
    {
        PhysxAction a;
        a.type = PhysxActionType::Detach;
        a.jointPath = attachmentPath;
        m_physxActions.push_back(std::move(a));
    }
}

void SurfaceGripperComponent::_queueDetachJoint(const std::string& jointPath)
{
    PhysxAction a;
    a.type = PhysxActionType::Detach;
    a.jointPath = jointPath;
    m_physxActions.push_back(std::move(a));
}

void SurfaceGripperComponent::_queueAttachJoint(const std::string& jointPath,
                                                physx::PxRigidActor* actor0,
                                                physx::PxRigidActor* actor1,
                                                const physx::PxTransform& localPose1)
{
    PhysxAction a;
    a.type = PhysxActionType::Attach;
    a.jointPath = jointPath;
    a.actor0 = actor0;
    a.actor1 = actor1;
    a.localPose1 = localPose1;
    m_physxActions.push_back(std::move(a));
}


// Removed unused direct USD writer helpers; writes are now queued and executed in the manager.


void SurfaceGripperComponent::consumeUsdActions(std::vector<UsdAction>& outActions)
{
    if (!m_usdActions.empty())
    {
        outActions.insert(outActions.end(), std::make_move_iterator(m_usdActions.begin()),
                          std::make_move_iterator(m_usdActions.end()));
        m_usdActions.clear();
    }
}

void SurfaceGripperComponent::_queueWriteStatus(const std::string& statusToken)
{
    UsdAction a;
    a.type = UsdActionType::WriteStatus;
    a.primPath = m_primPath.GetString();
    a.statusToken = statusToken;
    m_usdActions.push_back(std::move(a));
}

void SurfaceGripperComponent::_queueWriteGrippedObjectsAndFilters(const std::vector<std::string>& objectPaths,
                                                                  const std::string& body0PathForFilterPairs)
{
    UsdAction a;
    a.type = UsdActionType::WriteGrippedObjectsAndFilters;
    a.primPath = m_primPath.GetString();
    a.grippedObjectPaths = objectPaths;
    a.body0PathForFilterPairs = body0PathForFilterPairs;
    m_usdActions.push_back(std::move(a));
}

void SurfaceGripperComponent::_queueWriteAttachmentPointBatch(
    const std::vector<std::string>& applyApiPaths,
    const std::vector<std::string>& excludeFromArticulationPaths,
    const std::vector<std::pair<std::string, float>>& clearanceOffsets)
{
    UsdAction a;
    a.type = UsdActionType::WriteAttachmentPointBatch;
    a.primPath = m_primPath.GetString();
    a.apiPathsToApply = applyApiPaths;
    a.excludeFromArticulationPaths = excludeFromArticulationPaths;
    a.clearanceOffsets = clearanceOffsets;
    m_usdActions.push_back(std::move(a));
}

Axis SurfaceGripperComponent::_getJointForwardAxis(const std::string& attachmentPath) const
{
    auto itAxis = m_jointForwardAxis.find(attachmentPath);
    Axis axis = (itAxis != m_jointForwardAxis.end()) ? itAxis->second : Axis::Z;
    return axis;
}

physx::PxTransform SurfaceGripperComponent::_computeJointWorldTransform(physx::PxJoint* joint,
                                                                        physx::PxRigidActor* actor0) const
{
    physx::PxTransform localPose0 = joint->getLocalPose(physx::PxJointActorIndex::eACTOR0);
    physx::PxTransform actorPose = actor0->getGlobalPose();
    return actorPose * localPose0;
}

physx::PxVec3 SurfaceGripperComponent::_directionFromAxisAndWorld(Axis axis, const physx::PxTransform& worldTransform) const
{
    physx::PxVec3 local(0.0f, 0.0f, 0.0f);
    switch (axis)
    {
    case Axis::X:
        local.x = 1.0f;
        break;
    case Axis::Y:
        local.y = 1.0f;
        break;
    default:
        local.z = 1.0f;
        break;
    }
    physx::PxVec3 dir = worldTransform.q.rotate(local);
    dir.normalize();
    return dir;
}

} // namespace surface_gripper
} // namespace robot
} // namespace isaacsim
