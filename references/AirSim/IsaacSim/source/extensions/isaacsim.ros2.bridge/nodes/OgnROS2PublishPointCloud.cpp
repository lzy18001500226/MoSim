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

#ifdef _WIN32
#    pragma warning(push)
#    pragma warning(disable : 4996)
#endif

// clang-format off
#include <pch/UsdPCH.h>
// clang-format on
#include "isaacsim/core/includes/UsdUtilities.h"

#include <carb/profiler/Profile.h>
#include <carb/tasking/ITasking.h>
#include <carb/tasking/TaskingUtils.h>

#include <isaacsim/core/includes/ScopedCudaDevice.h>
#include <isaacsim/ros2/bridge/Ros2Node.h>

#include <OgnROS2PublishPointCloudDatabase.h>

using namespace isaacsim::ros2::bridge;

class PublishPointCloudThreadData
{
public:
    PublishPointCloudThreadData()
        : inputDataPtr(nullptr),
          outputDataPtr(nullptr),
          bufferSize(0),
          totalBytes(0),
          cudaDeviceIndex(-1),
          stream(nullptr),
          streamDevice(nullptr),
          mStreamNotCreated(nullptr)
    {
    }

    void* inputDataPtr;
    void* outputDataPtr;
    size_t bufferSize;
    size_t totalBytes;
    int cudaDeviceIndex;

    cudaStream_t* stream;
    int* streamDevice;
    bool* mStreamNotCreated;

    std::shared_ptr<Ros2Publisher> publisher;
    std::shared_ptr<Ros2PointCloudMessage> message;
};

class OgnROS2PublishPointCloud : public Ros2Node
{
public:
    static bool compute(OgnROS2PublishPointCloudDatabase& db)
    {
        auto& state = db.perInstanceState<OgnROS2PublishPointCloud>();

        // Spin once calls reset automatically if it was not successful
        const auto& nodeObj = db.abi_node();
        if (!state.isInitialized())
        {
            const GraphContextObj& context = db.abi_context();
            // Find our stage
            long stageId = context.iContext->getStageId(context);
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

            if (!state.initializeNodeHandle(
                    std::string(nodeObj.iNode->getPrimPath(nodeObj)),
                    collectNamespace(db.inputs.nodeNamespace(),
                                     stage->GetPrimAtPath(pxr::SdfPath(nodeObj.iNode->getPrimPath(nodeObj)))),
                    db.inputs.context()))
            {
                db.logError("Unable to create ROS2 node, please check that namespace is valid");
                return false;
            }
        }

        // Publisher was not valid, create a new one
        if (!state.m_publisher)
        {
            CARB_PROFILE_ZONE(0, "[IsaacSim] setup point cloud publisher");
            // Setup ROS publisher
            const std::string& topicName = db.inputs.topicName();
            std::string fullTopicName = addTopicPrefix(state.m_namespaceName, topicName);
            if (!state.m_factory->validateTopicName(fullTopicName))
            {
                db.logError("Unable to create ROS2 publisher, invalid topic name");
                return false;
            }

            state.m_message = state.m_factory->createPointCloudMessage();

            Ros2QoSProfile qos;
            const std::string& qosProfile = db.inputs.qosProfile();
            if (qosProfile.empty())
            {
                qos.depth = db.inputs.queueSize();
            }
            else
            {
                if (!jsonToRos2QoSProfile(qos, qosProfile))
                {
                    return false;
                }
            }

            state.m_publisher = state.m_factory->createPublisher(
                state.m_nodeHandle.get(), fullTopicName.c_str(), state.m_message->getTypeSupportHandle(), qos);

            state.m_frameId = db.inputs.frameId();

            // Get extension settings for multithreading
            carb::settings::ISettings* threadSettings = carb::getCachedInterface<carb::settings::ISettings>();
            static constexpr char s_kThreadDisable[] = "/exts/isaacsim.ros2.bridge/publish_multithreading_disabled";
            state.m_multithreadingDisabled = threadSettings->getAsBool(s_kThreadDisable);
            return true;
        }

        return state.publishLidar(db);
    }

    PublishPointCloudThreadData buildThreadData(OgnROS2PublishPointCloudDatabase& db,
                                                OgnROS2PublishPointCloud& state,
                                                void* dataPtr,
                                                size_t totalBytes)
    {
        PublishPointCloudThreadData threadData;

        threadData.inputDataPtr = reinterpret_cast<void*>(db.inputs.dataPtr());
        threadData.outputDataPtr = dataPtr;
        threadData.bufferSize = db.inputs.bufferSize();
        threadData.totalBytes = totalBytes;
        threadData.cudaDeviceIndex = db.inputs.cudaDeviceIndex();

        threadData.stream = &state.m_stream;
        threadData.streamDevice = &state.m_streamDevice;
        threadData.mStreamNotCreated = &state.m_streamNotCreated;

        threadData.publisher = state.m_publisher;
        threadData.message = state.m_message;

        return threadData;
    }

    static bool publishPointCloudHelper(PublishPointCloudThreadData& data)
    {
        CARB_PROFILE_ZONE(1, "[IsaacSim] Publish PointCloud Thread");
        isaacsim::core::includes::ScopedDevice scopedDev(data.cudaDeviceIndex);

        // If the device doesn't match and we have created a stream, destroy it
        if (*data.streamDevice != data.cudaDeviceIndex && *data.mStreamNotCreated == false)
        {
            CARB_PROFILE_ZONE(1, "[IsaacSim] Destroy stream");
            CUDA_CHECK(cudaStreamDestroy(*data.stream));
            *data.mStreamNotCreated = true;
            *data.streamDevice = -1;
        }
        // Create a stream if it does not exist
        if (*data.mStreamNotCreated)
        {
            CARB_PROFILE_ZONE(1, "[IsaacSim] Create stream");
            CUDA_CHECK(cudaStreamCreate(data.stream));
            *data.mStreamNotCreated = false;
            *data.streamDevice = data.cudaDeviceIndex;
        }

        CARB_PROFILE_ZONE(1, "[IsaacSim] data in cuda memory");
        CUDA_CHECK(cudaMemcpyAsync(
            data.outputDataPtr, data.inputDataPtr, data.bufferSize, cudaMemcpyDeviceToHost, *data.stream));
        CUDA_CHECK(cudaStreamSynchronize(*data.stream));

        {
            CARB_PROFILE_ZONE(1, "[IsaacSim] pcl publisher publish");
            data.publisher.get()->publish(data.message->getPtr());
        }
        return true;
    }

    bool publishLidar(OgnROS2PublishPointCloudDatabase& db)
    {
        CARB_PROFILE_ZONE(0, "[IsaacSim] Lidar Point Cloud Pub");
        auto& state = db.perInstanceState<OgnROS2PublishPointCloud>();
        auto tasking = carb::getCachedInterface<carb::tasking::ITasking>();

        {
            CARB_PROFILE_ZONE(1, "[IsaacSim] wait for previous publish");
            // Wait for last message publish
            state.m_tasks.wait();
        }

        // Check if subscription count is 0
        if (!state.m_publishWithoutVerification && !state.m_publisher.get()->getSubscriptionCount())
        {
            return false;
        }

        size_t height = 1;
        uint32_t pointStep = sizeof(GfVec3f);
        size_t width = 0;
        size_t rowStep = 0;

        if (db.inputs.cudaDeviceIndex() == -1)
        {
            if (db.inputs.dataPtr() != 0)
            {
                width = db.inputs.bufferSize() / pointStep;
                rowStep = db.inputs.bufferSize();
                size_t totalBytes = rowStep;
                state.m_message->generateBuffer(db.inputs.timeStamp(), state.m_frameId, width, height, pointStep);
                // Data is on host as ptr, buffer size matches
                {
                    memcpy(state.m_message->getBufferPtr(), reinterpret_cast<void*>(db.inputs.dataPtr()), totalBytes);
                }
            }
            else if (db.inputs.dataPtr() == 0)
            {
                width = db.inputs.data.size();
                rowStep = pointStep * db.inputs.data.size();
                size_t totalBytes = rowStep;
                state.m_message->generateBuffer(db.inputs.timeStamp(), state.m_frameId, width, height, pointStep);
                // Data is on host as ogn data, copy from cpu
                {
                    memcpy(state.m_message->getBufferPtr(),
                           reinterpret_cast<const uint8_t*>(db.inputs.data.cpu().data()), totalBytes);
                }
            }

            if (state.m_multithreadingDisabled)
            {
                CARB_PROFILE_ZONE(1, "[IsaacSim] Publish PCL");
                state.m_publisher.get()->publish(state.m_message->getPtr());
            }
            else
            {
                tasking->addTask(carb::tasking::Priority::eHigh, state.m_tasks,
                                 [&state]
                                 {
                                     CARB_PROFILE_ZONE(1, "[IsaacSim] Publish PCL Thread");
                                     state.m_publisher.get()->publish(state.m_message->getPtr());
                                 });
            }
        }
        else
        {
            if (db.inputs.dataPtr() != 0)
            {
                width = db.inputs.bufferSize() / pointStep;
                rowStep = db.inputs.bufferSize();
                size_t totalBytes = rowStep;
                state.m_message->generateBuffer(db.inputs.timeStamp(), state.m_frameId, width, height, pointStep);

                PublishPointCloudThreadData publishPointCloudThreadData =
                    buildThreadData(db, state, state.m_message->getBufferPtr(), totalBytes);

                if (state.m_multithreadingDisabled)
                {
                    return publishPointCloudHelper(publishPointCloudThreadData);
                }
                else
                {
                    // In order to get the benefits of using a separate stream, do the work in a new thread
                    tasking->addTask(carb::tasking::Priority::eHigh, state.m_tasks,
                                     [data = publishPointCloudThreadData]() mutable
                                     { return publishPointCloudHelper(data); });
                }
            }
        }

        return true;
    }

    static void releaseInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        auto& state = OgnROS2PublishPointCloudDatabase::sPerInstanceState<OgnROS2PublishPointCloud>(nodeObj, instanceId);
        state.reset();
    }

    virtual void reset()
    {
        {
            CARB_PROFILE_ZONE(1, "[IsaacSim] wait for previous publish");
            // Wait for last message to publish before starting next
            m_tasks.wait();
        }
        if (m_streamNotCreated == false)
        {
            isaacsim::core::includes::ScopedDevice scopedDev(m_streamDevice);
            CUDA_CHECK(cudaStreamDestroy(m_stream));
            m_streamDevice = -1;
            m_streamNotCreated = true;
        }

        m_publisher.reset(); // This should be reset before we reset the handle.
        Ros2Node::reset();
    }

private:
    std::shared_ptr<Ros2Publisher> m_publisher = nullptr;
    std::shared_ptr<Ros2PointCloudMessage> m_message = nullptr;

    std::string m_frameId = "sim_lidar";

    carb::tasking::TaskGroup m_tasks;
    cudaStream_t m_stream;
    int m_streamDevice = -1;
    bool m_streamNotCreated = true;

    bool m_multithreadingDisabled = false;
};

REGISTER_OGN_NODE()

#ifdef _WIN32
#    pragma warning(pop)
#endif
