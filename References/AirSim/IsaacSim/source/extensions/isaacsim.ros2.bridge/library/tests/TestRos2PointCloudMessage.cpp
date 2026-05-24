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
#include "TestBase.h"

#include <doctest/doctest.h>

TEST_SUITE("isaacsim.ros2.bridge.point_cloud_message_tests")
{
    TEST_CASE("Ros2PointCloudMessage: factory creates non-null message")
    {
        ROS2_TEST_SETUP();

        auto msg = testBase.getFactory()->createPointCloudMessage();
        CHECK(msg != nullptr);
    }

    TEST_CASE("Ros2PointCloudMessage: type support handle is valid")
    {
        ROS2_TEST_SETUP();

        auto msg = testBase.getFactory()->createPointCloudMessage();
        REQUIRE(msg != nullptr);

        const void* typeSupport = msg->getTypeSupportHandle();
        CHECK(typeSupport != nullptr);
    }

    TEST_CASE("Ros2PointCloudMessage: message pointer is valid")
    {
        ROS2_TEST_SETUP();

        auto msg = testBase.getFactory()->createPointCloudMessage();
        REQUIRE(msg != nullptr);

        const void* ptr = msg->getPtr();
        CHECK(ptr != nullptr);
    }

    TEST_CASE("Ros2PointCloudMessage: generate buffer for unorganized cloud")
    {
        ROS2_TEST_SETUP();

        auto msg = testBase.getFactory()->createPointCloudMessage();
        REQUIRE(msg != nullptr);

        double timestamp = 123.456;
        std::string frameId = "lidar_frame";
        size_t width = 1000; // Number of points
        size_t height = 1; // Unorganized cloud
        uint32_t pointStep = 12; // 3 floats (x, y, z) * 4 bytes each

        // Should not crash when generating buffer
        CHECK_NOTHROW(msg->generateBuffer(timestamp, frameId, width, height, pointStep));
    }

    TEST_CASE("Ros2PointCloudMessage: generate buffer for organized cloud")
    {
        ROS2_TEST_SETUP();

        auto msg = testBase.getFactory()->createPointCloudMessage();
        REQUIRE(msg != nullptr);

        double timestamp = 123.456;
        std::string frameId = "camera_frame";
        size_t width = 640; // Image width
        size_t height = 480; // Image height
        uint32_t pointStep = 16; // x, y, z, intensity * 4 bytes each

        // Should not crash when generating organized cloud buffer
        CHECK_NOTHROW(msg->generateBuffer(timestamp, frameId, width, height, pointStep));
    }

    TEST_CASE("Ros2PointCloudMessage: generate buffer with minimal data")
    {
        ROS2_TEST_SETUP();

        auto msg = testBase.getFactory()->createPointCloudMessage();
        REQUIRE(msg != nullptr);

        double timestamp = 0.0;
        std::string frameId = "base_link";
        size_t width = 1;
        size_t height = 1;
        uint32_t pointStep = 12; // Just x, y, z

        // Should not crash with minimal buffer
        CHECK_NOTHROW(msg->generateBuffer(timestamp, frameId, width, height, pointStep));
    }

    TEST_CASE("Ros2PointCloudMessage: use with publisher")
    {
        ROS2_TEST_SETUP();

        // Create context and node
        auto context = testBase.getFactory()->createContextHandle();
        REQUIRE(context != nullptr);
        context->init(0, nullptr);

        auto node = testBase.getFactory()->createNodeHandle("test_pointcloud_node", "test", context.get());
        REQUIRE(node != nullptr);

        auto msg = testBase.getFactory()->createPointCloudMessage();
        REQUIRE(msg != nullptr);

        // Create QoS profile appropriate for point clouds
        isaacsim::ros2::bridge::Ros2QoSProfile qos;
        qos.reliability = isaacsim::ros2::bridge::Ros2QoSReliabilityPolicy::eReliable;
        qos.durability = isaacsim::ros2::bridge::Ros2QoSDurabilityPolicy::eVolatile;
        qos.depth = 5; // Lower depth for large point cloud messages

        // Create publisher - should not crash
        auto publisher =
            testBase.getFactory()->createPublisher(node.get(), "test_pointcloud", msg->getTypeSupportHandle(), qos);
        CHECK(publisher != nullptr);

        // Generate buffer and publish - should not crash
        msg->generateBuffer(1.0, "lidar_frame", 100, 1, 12);
        if (publisher)
        {
            CHECK_NOTHROW(publisher->publish(msg->getPtr()));
        }
    }
}
