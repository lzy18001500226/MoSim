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
#include <isaacsim/core/includes/Buffer.h>
#include <isaacsim/core/includes/Conversions.h>
#include <isaacsim/core/nodes/ICoreNodes.h>
#include <isaacsim/core/simulation_manager/ISimulationManager.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/physics/tensors/IArticulationView.h>
#include <omni/physics/tensors/IRigidBodyView.h>
#include <omni/physics/tensors/ISimulationView.h>
#include <omni/physics/tensors/TensorApi.h>
#include <omni/usd/UsdContext.h>
#include <omni/usd/UsdContextIncludes.h>

#include <OgnIsaacComputeOdometryDatabase.h>

namespace isaacsim
{
namespace core
{
namespace nodes
{
using namespace omni::physics::tensors;

using isaacsim::core::includes::conversions::asCarbFloat4;
using isaacsim::core::includes::conversions::asGfRotation;
using isaacsim::core::includes::conversions::asGfVec3d;

static void createTensorDesc(TensorDesc& tensorDesc, void* dataPtr, int numElements, TensorDataType type, int device)
{
    tensorDesc.dtype = type;
    tensorDesc.numDims = 1;
    tensorDesc.dims[0] = numElements;
    tensorDesc.data = dataPtr;
    tensorDesc.ownData = true;
    tensorDesc.device = device;
}

class OgnIsaacComputeOdometry : public isaacsim::core::includes::BaseResetNode
{
public:
    static void initInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        auto& state = OgnIsaacComputeOdometryDatabase::sPerInstanceState<OgnIsaacComputeOdometry>(nodeObj, instanceId);
        state.m_simulationManagerFramework =
            carb::getCachedInterface<isaacsim::core::simulation_manager::ISimulationManager>();

        // Resize buffers and arrays
        state.m_transformBuffer.resize(7);
        state.m_velocitiesBuffer.resize(6);
        state.m_transformData.resize(7);
        state.m_velocitiesData.resize(6);
    }

    static bool compute(OgnIsaacComputeOdometryDatabase& db)
    {
        const GraphContextObj& context = db.abi_context();
        auto& state = db.perInstanceState<OgnIsaacComputeOdometry>();
        if (state.m_firstFrame && state.m_simulationManagerFramework->isSimulating())
        {
            // Get the stage
            long stageId = context.iContext->getStageId(context);
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
            if (!stage)
            {
                db.logError("Could not find USD stage with ID %ld", stageId);
                return false;
            }

            // Get target prim
            const auto& prim = db.inputs.chassisPrim();
            const char* primPath;
            if (!prim.empty())
            {
                if (!stage->GetPrimAtPath(omni::fabric::toSdfPath(prim[0])))
                {
                    db.logError("The prim %s is not valid. Please specify at least one valid chassis prim",
                                omni::fabric::toSdfPath(prim[0]).GetText());
                    return false;
                }
                primPath = omni::fabric::toSdfPath(prim[0]).GetText();
            }
            else
            {
                db.logError("No chassis (target) prim found at path '%s'", primPath);
                return false;
            }

            // Create simulation view
            state.m_tensorInterface = carb::getCachedInterface<TensorApi>();
            if (!state.m_tensorInterface)
            {
                CARB_LOG_ERROR("Failed to acquire Tensor API interface\n");
                return false;
            }
            state.m_simulationView = state.m_tensorInterface->createSimulationView(stageId);

            // Create tensor descriptors
            int deviceOrdinal = state.m_simulationView->getDeviceOrdinal();
            state.m_transformBuffer.setDevice(deviceOrdinal);
            state.m_velocitiesBuffer.setDevice(deviceOrdinal);
            createTensorDesc(state.m_transformTensor, static_cast<void*>(state.m_transformBuffer.data()), 7,
                             TensorDataType::eFloat32, deviceOrdinal);
            createTensorDesc(state.m_velocitiesTensor, static_cast<void*>(state.m_velocitiesBuffer.data()), 6,
                             TensorDataType::eFloat32, deviceOrdinal);

            // Create view for the target prim
            ObjectType objectType = state.m_simulationView->getObjectType(primPath);
            if (objectType == ObjectType::eArticulation || objectType == ObjectType::eArticulationRootLink)
            {
                IArticulationView* articulation = state.m_simulationView->createArticulationView(primPath);
                state.m_articulation = articulation;
                state.m_articulation->getRootTransforms(&state.m_transformTensor);
            }
            else if (objectType == ObjectType::eRigidBody || objectType == ObjectType::eArticulationLink)
            {
                IRigidBodyView* rigidBody = state.m_simulationView->createRigidBodyView(primPath);
                state.m_rigidBody = rigidBody;
                state.m_rigidBody->getTransforms(&state.m_transformTensor);
            }
            else
            {
                db.logError("The prim at path '%s' is not a valid rigid body or articulation root", primPath);
                return false;
            }

            // Initialize other variables
            state.m_transformBuffer.copyTo(state.m_transformData.data(), 7);
            state.m_velocitiesBuffer.copyTo(state.m_velocitiesData.data(), 6);
            state.m_startingPose = ::physx::PxTransform(
                ::physx::PxVec3(state.m_transformData[0], state.m_transformData[1], state.m_transformData[2]),
                ::physx::PxQuat(state.m_transformData[3], state.m_transformData[4], state.m_transformData[5],
                                state.m_transformData[6]));
            state.m_unitScale = UsdGeomGetStageMetersPerUnit(stage);
            state.m_lastTime = state.m_simulationManagerFramework->getSimulationTime();
            state.m_firstFrame = false;
        }

        state.computeOdometry(db);

        db.outputs.execOut() = kExecutionAttributeStateEnabled;
        return true;
    }

    void computeOdometry(OgnIsaacComputeOdometryDatabase& db)
    {
        // Get transform and velocities
        // - Query data from tensor API
        if (m_articulation)
        {
            m_articulation->getRootTransforms(&m_transformTensor);
        }
        else if (m_rigidBody)
        {
            m_rigidBody->getTransforms(&m_transformTensor);
        }
        if (m_articulation)
        {
            m_articulation->getRootVelocities(&m_velocitiesTensor);
        }
        else if (m_rigidBody)
        {
            m_rigidBody->getVelocities(&m_velocitiesTensor);
        }
        // - Copy data to host (CPU)
        m_transformBuffer.copyTo(m_transformData.data(), 7);
        m_velocitiesBuffer.copyTo(m_velocitiesData.data(), 6);

        auto p = ::physx::PxVec3(m_transformData[0], m_transformData[1], m_transformData[2]);
        auto q = ::physx::PxQuat(m_transformData[3], m_transformData[4], m_transformData[5], m_transformData[6]);
        auto linVel = ::physx::PxVec3(m_velocitiesData[0], m_velocitiesData[1], m_velocitiesData[2]);
        auto bodyLocalLinVel = ::physx::PxVec3(linVel.dot(q.rotate(::physx::PxVec3(1, 0, 0))),
                                               linVel.dot(q.rotate(::physx::PxVec3(0, 1, 0))),
                                               linVel.dot(q.rotate(::physx::PxVec3(0, 0, 1))));
        auto bodyAngVel = ::physx::PxVec3(m_velocitiesData[3], m_velocitiesData[4], m_velocitiesData[5]);

        if (m_simulationManagerFramework->getSimulationTime() != m_lastTime)
        {
            double dt = m_simulationManagerFramework->getSimulationTime() - m_lastTime;
            // Local accelerations
            m_linearAcceleration.x = static_cast<float>((bodyLocalLinVel.x - m_prevLinearVelocity.x) / dt);
            m_linearAcceleration.y = static_cast<float>((bodyLocalLinVel.y - m_prevLinearVelocity.y) / dt);
            m_linearAcceleration.z = static_cast<float>((bodyLocalLinVel.z - m_prevLinearVelocity.z) / dt);

            // Global accelerations
            m_globalLinearAcceleration.x = static_cast<float>((linVel.x - m_prevGlobalLinearVelocity.x) / dt);
            m_globalLinearAcceleration.y = static_cast<float>((linVel.y - m_prevGlobalLinearVelocity.y) / dt);
            m_globalLinearAcceleration.z = static_cast<float>((linVel.z - m_prevGlobalLinearVelocity.z) / dt);

            m_angularAcceleration.x = static_cast<float>((bodyAngVel.x - m_prevAngularVelocity.x) / dt);
            m_angularAcceleration.y = static_cast<float>((bodyAngVel.y - m_prevAngularVelocity.y) / dt);
            m_angularAcceleration.z = static_cast<float>((bodyAngVel.z - m_prevAngularVelocity.z) / dt);

            db.outputs.linearAcceleration().Set(m_linearAcceleration.x, m_linearAcceleration.y, m_linearAcceleration.z);
            db.outputs.globalLinearAcceleration().Set(
                m_globalLinearAcceleration.x, m_globalLinearAcceleration.y, m_globalLinearAcceleration.z);
            db.outputs.angularAcceleration().Set(
                m_angularAcceleration.x, m_angularAcceleration.y, m_angularAcceleration.z);
        }

        // Calculate odometry reading from starting position
        pxr::GfVec3d globalTranslation =
            pxr::GfVec3d(p.x - m_startingPose.p.x, p.y - m_startingPose.p.y, p.z - m_startingPose.p.z);

        auto qc = asCarbFloat4(q);
        auto qcStartingPose = asCarbFloat4(m_startingPose.q);
        db.outputs.position() = (asGfRotation(qcStartingPose).GetInverse()).TransformDir(globalTranslation) * m_unitScale;

        db.outputs.orientation() = (asGfRotation(qc) * asGfRotation(qcStartingPose).GetInverse()).GetQuat();

        db.outputs.linearVelocity().Set(bodyLocalLinVel.x, bodyLocalLinVel.y, bodyLocalLinVel.z);
        db.outputs.globalLinearVelocity().Set(linVel.x, linVel.y, linVel.z);
        db.outputs.angularVelocity().Set(bodyAngVel.x, bodyAngVel.y, bodyAngVel.z);

        m_prevLinearVelocity = bodyLocalLinVel;
        m_prevGlobalLinearVelocity = linVel;
        m_prevAngularVelocity = bodyAngVel;
        m_lastTime = m_simulationManagerFramework->getSimulationTime();
    }

    virtual void reset()
    {
        m_firstFrame = true;
    }

private:
    // Tensor API variables
    // - Views
    IArticulationView* m_articulation = nullptr;
    IRigidBodyView* m_rigidBody = nullptr;
    TensorApi* m_tensorInterface = nullptr;
    ISimulationView* m_simulationView = nullptr;
    // - Tensor descriptors, buffers (CPU/GPU attending view device) and arrays (CPU, for OmniGraph) containers
    TensorDesc m_transformTensor;
    TensorDesc m_velocitiesTensor;
    isaacsim::core::includes::GenericBufferBase<float> m_transformBuffer;
    isaacsim::core::includes::GenericBufferBase<float> m_velocitiesBuffer;
    std::vector<float> m_transformData;
    std::vector<float> m_velocitiesData;

    // Other variables
    isaacsim::core::simulation_manager::ISimulationManager* m_simulationManagerFramework = nullptr;
    bool m_firstFrame = true;
    double m_lastTime = 0.0;
    double m_unitScale = 1.0;

    ::physx::PxTransform m_startingPose;
    ::physx::PxVec3 m_linearAcceleration = { 0, 0, 0 };
    ::physx::PxVec3 m_angularAcceleration = { 0, 0, 0 };
    ::physx::PxVec3 m_prevLinearVelocity = { 0, 0, 0 };
    ::physx::PxVec3 m_prevAngularVelocity = { 0, 0, 0 };
    ::physx::PxVec3 m_globalLinearAcceleration = { 0, 0, 0 };
    ::physx::PxVec3 m_prevGlobalLinearVelocity = { 0, 0, 0 };
};

REGISTER_OGN_NODE()
}
}
}
