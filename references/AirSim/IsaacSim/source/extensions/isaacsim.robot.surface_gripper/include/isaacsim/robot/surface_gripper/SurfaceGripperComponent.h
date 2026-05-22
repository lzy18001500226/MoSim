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
// clang-format off
#include <pch/UsdPCH.h>
// clang-format on
#include "isaacsim/core/includes/Component.h"
#include "isaacsim/core/includes/UsdUtilities.h"
#include "isaacsim/robot/schema/robot_schema.h"

#include <extensions/PxJoint.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdPhysics/driveAPI.h>
#include <pxr/usd/usdPhysics/joint.h>
#include <pxr/usd/usdPhysics/scene.h>
// PhysX forward declarations/headers for pointer types used in queued actions
#include <PxRigidActor.h>
#include <chrono>
#include <map>
#include <mutex>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace isaacsim
{
namespace robot
{
namespace surface_gripper
{


// Replaced custom PhysxTransform with physx::PxTransform

/**
 * @brief Action kind for queued PhysX operations.
 */
enum class PhysxActionType
{
    Attach,
    Detach
};

/**
 * @brief Queued PhysX action to be executed serially by the manager.
 */
struct PhysxAction
{
    PhysxActionType type = PhysxActionType::Attach;

    // Common
    std::string jointPath;

    // For Attach
    physx::PxRigidActor* actor0 = nullptr;
    physx::PxRigidActor* actor1 = nullptr;
    physx::PxTransform localPose1;
};

/**
 * @brief USD action kind for queued USD operations.
 */
enum class UsdActionType
{
    WriteStatus,
    WriteGrippedObjectsAndFilters,
    WriteAttachmentPointBatch
};

/**
 * @brief Axis enumeration for forward direction.
 */
enum class Axis
{
    X,
    Y,
    Z
};

/**
 * @brief Queued USD action to be executed serially by the manager.
 */
struct UsdAction
{
    UsdActionType type = UsdActionType::WriteStatus;

    // Common
    std::string primPath;

    // For WriteStatus
    std::string statusToken; // "Open", "Closed", or "Closing"

    // For WriteGrippedObjectsAndFilters
    std::vector<std::string> grippedObjectPaths;
    std::string body0PathForFilterPairs;

    // For WriteAttachmentPointBatch
    std::vector<std::string> apiPathsToApply;
    std::vector<std::string> excludeFromArticulationPaths;
    std::vector<std::pair<std::string, float>> clearanceOffsets;
};

enum class GripperStatus
{
    Open,
    Closing,
    Closed,
};

// Add conversion functions for GripperStatus
inline GripperStatus GripperStatusFromToken(const pxr::TfToken& token)
{
    if (token == pxr::TfToken("Open"))
        return GripperStatus::Open;
    if (token == pxr::TfToken("Closed"))
        return GripperStatus::Closed;
    if (token == pxr::TfToken("Closing"))
        return GripperStatus::Closing;
    return GripperStatus::Open; // Default value
}

inline pxr::TfToken GripperStatusToToken(GripperStatus status)
{
    switch (status)
    {
    case GripperStatus::Open:
        return pxr::TfToken("Open");
    case GripperStatus::Closed:
        return pxr::TfToken("Closed");
    case GripperStatus::Closing:
        return pxr::TfToken("Closing");
    default:
        return pxr::TfToken("Unknown");
    }
}

inline std::string GripperStatusToString(GripperStatus status)
{

    switch (status)
    {
    case GripperStatus::Open:
        return "Open";
    case GripperStatus::Closed:
        return "Closed";
    case GripperStatus::Closing:
        return "Closing";
    default:
        return "Unknown";
    }
}

/**
 * @class SurfaceGripperComponent
 * @brief Component class for managing Surface Gripper functionality
 * @details
 * This class represents a surface gripper component that can be attached to
 * a robot to enable gripping functionality. It manages the D6 joints that
 * act as attachment points for the gripper.
 */
class SurfaceGripperComponent : public isaacsim::core::includes::ComponentBase<pxr::UsdPrim>
{
public:
    /**
     * @brief Default constructor
     */
    SurfaceGripperComponent() = default;

    /**
     * @brief Virtual destructor
     */
    virtual ~SurfaceGripperComponent() = default;

    /**
     * @brief Initializes the surface gripper component
     * @param[in] prim USD prim representing the surface gripper
     * @param[in] stage USD stage containing the prim
     */
    virtual void initialize(const pxr::UsdPrim& prim, const pxr::UsdStageWeakPtr stage, bool writeToUsd);

    /**
     * @brief Called when component properties change
     * @details Updates the gripper's configuration when component properties are modified
     */
    virtual void onComponentChange();

    /**
     * @brief Called when the gripper starts
     */
    virtual void onStart();

    /**
     * @brief Called each physics step to update gripper state
     */
    virtual void onPhysicsStep(double dt);

    /**
     * @brief Called before each tick to prepare sensor state
     */
    virtual void preTick();

    /**
     * @brief Called each tick to update the gripper state
     */
    virtual void tick();

    /**
     * @brief Called when the gripper stops
     */
    virtual void onStop();

    /**
     * @brief Sets the gripper status.
     * @param[in] status New status for the gripper.
     * @return True if the status was changed successfully.
     */
    virtual bool setGripperStatus(GripperStatus status);

    /**
     * @brief Drains this component's queued PhysX actions into the provided vector.
     * @param[out] outActions Destination vector where actions will be appended.
     */
    void consumePhysxActions(std::vector<PhysxAction>& outActions);

    /**
     * @brief Drains this component's queued USD actions into the provided vector.
     * @param[out] outActions Destination vector where actions will be appended.
     */
    void consumeUsdActions(std::vector<UsdAction>& outActions);

    /**
     * @brief Gets the current status of the gripper.
     * @return Current status.
     */
    GripperStatus getGripperStatus() const
    {
        return m_status;
    }

    /**
     * @brief Gets the prim path of this gripper
     * @return The USD prim path as a string
     */
    std::string getPrimPath() const
    {
        return m_primPath.GetString();
    }

    /**
     * @brief Gets the list of currently gripped objects
     * @return Vector of prim paths for gripped objects
     */
    std::vector<std::string> getGrippedObjects() const
    {
        return std::vector<std::string>(m_grippedObjects.begin(), m_grippedObjects.end());
    }

    /**
     * @brief Sets whether to write to USD or keep state in memory only
     * @param[in] writeToUsd Whether to write to USD or keep state in memory only
     */
    void setWriteToUsd(bool writeToUsd)
    {
        m_writeToUsd = writeToUsd;
    }

    bool hasPhysxActions() const
    {
        return !m_physxActions.empty();
    }

    bool hasUsdActions() const
    {
        return !m_usdActions.empty();
    }

private:
    /**
     * @brief Updates gripper properties from the USD prim
     */
    void updateGripperProperties();

    /**
     * @brief Updates the list of attachment points from the USD relationship
     */
    void updateAttachmentPoints();

    /**
     * @brief Updates the list of already gripped objects from the USD relationship
     */
    void updateGrippedObjectsList();

    /**
     * @brief Updates the gripper state when it's closed
     */
    void updateClosedGripper();

    /**
     * @brief Checks force limits on attachment joints and releases if limits are exceeded
     */
    void checkForceLimits();

    /**
     * @brief Finds objects that can be gripped and attaches them
     */
    void findObjectsToGrip();

    /**
     * @brief Processes a single attachment point to attempt a grip.
     * @details
     * Executes the raycast and attachment logic for one attachment point, updating
     * the provided collections under the given mutexes when changes are detected.
     *
     * @param[in] attachmentPath The USD path string of the attachment joint to process.
     * @param[out] apToRemove Collection to append the attachment path to when it should transition to active.
     * @param[out] clearanceOffsetsToPersist Collection to append clearance offset updates to persist to USD.
     * @param[in,out] apMutex Mutex protecting per-attachment shared maps and vectors.
     * @param[in,out] clearanceMutex Mutex protecting the clearance offsets collection.
     */
    void _processAttachmentForGrip(const std::string& attachmentPath,
                                   std::vector<std::string>& apToRemove,
                                   std::vector<std::pair<std::string, float>>& clearanceOffsetsToPersist);

    /**
     * @brief Updates the gripper state when it's open
     */
    void updateOpenGripper();

    /**
     * @brief Releases all objects currently gripped
     */
    void releaseAllObjects();

    /**
     * @brief Queue PhysX operations to release all objects. Executed during physics step.
     */
    void _queueReleaseAllObjectsActions();

    /**
     * @brief Queue helper: detach joint (will enable constraints and collisions).
     */
    void _queueDetachJoint(const std::string& jointPath);

    /**
     * @brief Queue helper: attach joint to actors and set pose/flags.
     */
    void _queueAttachJoint(const std::string& jointPath,
                           physx::PxRigidActor* actor0,
                           physx::PxRigidActor* actor1,
                           const physx::PxTransform& localPose1);

    /**
     * @brief Queue helper: write status token for this gripper.
     */
    void _queueWriteStatus(const std::string& statusToken);

    /**
     * @brief Queue helper: write gripped objects relationship and filtered pairs.
     */
    void _queueWriteGrippedObjectsAndFilters(const std::vector<std::string>& objectPaths,
                                             const std::string& body0PathForFilterPairs);

    /**
     * @brief Queue helper: write attachment point batch changes.
     */
    void _queueWriteAttachmentPointBatch(const std::vector<std::string>& applyApiPaths,
                                         const std::vector<std::string>& excludeFromArticulationPaths,
                                         const std::vector<std::pair<std::string, float>>& clearanceOffsets);

    /**
     * @brief Returns cached forward axis for an attachment or default 'Z'.
     */
    Axis _getJointForwardAxis(const std::string& attachmentPath) const;

    /**
     * @brief Computes world transform at joint actor0 frame.
     */
    physx::PxTransform _computeJointWorldTransform(physx::PxJoint* joint, physx::PxRigidActor* actor0) const;

    /**
     * @brief Computes normalized world-space direction vector from axis and world transform.
     */
    physx::PxVec3 _directionFromAxisAndWorld(Axis axis, const physx::PxTransform& worldTransform) const;

    pxr::SdfPath m_primPath; ///< The USD prim path of this gripper
    std::string m_activationRule = "FullSet"; ///< How the surface gripper is activated
    std::string m_forwardAxis = "X"; ///< Axis along which the gripper opens/closes
    GripperStatus m_status = GripperStatus::Open; ///< Current status of the gripper
    float m_retryInterval = 0.0; ///< Retry interval in seconds
    float m_shearForceLimit = -1.0f; ///< Maximum allowable shear force
    float m_coaxialForceLimit = -1.0f;
    double m_retryElapsed = 0.0; ///< Elapsed time for retry interval
    float m_maxGripDistance = 0.0f; ///< Maximum distance the gripper can check to grab an object


    std::unordered_set<std::string> m_attachmentPoints; ///< List of D6 joints as attachment points
    std::unordered_set<std::string> m_activeAttachmentPoints; ///< List of filtered bodies for gripping
    std::unordered_set<std::string> m_inactiveAttachmentPoints; ///< List of filtered bodies for gripping
    std::unordered_set<std::string> m_grippedObjects; ///< List of currently gripped objects
    std::unordered_set<std::string> m_grippedObjectsBuffer; ///< Buffer used to check currently gripped objects at
                                                            ///< runtime

    size_t m_settlingDelay = 10; ///< Number of physics steps to wait for the joint to settle
    std::unordered_map<std::string, size_t> m_jointSettlingCounters; ///< Map of joint paths to settling counters


    bool m_isInitialized = false; ///< Whether the component is initialized
    bool m_isEnabled = true; ///< Whether the component is enabled
    bool m_retryCloseActive = false; ///< Whether we're in retry mode for closing

    bool m_writeToUsd = false; ///< Whether to write to USD or keep state in memory only

    // Cached USD-derived data to avoid mid-step reads
    std::unordered_map<std::string, Axis> m_jointForwardAxis; ///< Per-joint forward axis
    std::unordered_map<std::string, float> m_jointClearanceOffset; ///< Per-joint clearance offset (meters)
    std::string m_body0PathForFilterPairs; ///< Cached body0 path used for filtered pairs updates

    // USD writes are handled via queued actions consumed by the manager

    // Queued PhysX action buffer (protected by mutex)
    std::vector<PhysxAction> m_physxActions;

    // Queued USD actions (protected by mutex)
    std::vector<UsdAction> m_usdActions;
};

} // namespace surface_gripper
} // namespace robot
} // namespace isaacsim
