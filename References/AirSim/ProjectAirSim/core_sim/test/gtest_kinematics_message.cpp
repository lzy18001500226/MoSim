// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include <string>

#include "core_sim/message/kinematics_message.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

namespace {

void ExpectVectorEq(const projectairsim::Vector3& actual,
                    const projectairsim::Vector3& expected) {
  EXPECT_FLOAT_EQ(actual.x(), expected.x());
  EXPECT_FLOAT_EQ(actual.y(), expected.y());
  EXPECT_FLOAT_EQ(actual.z(), expected.z());
}

void ExpectQuaternionEq(const projectairsim::Quaternion& actual,
                        const projectairsim::Quaternion& expected) {
  EXPECT_FLOAT_EQ(actual.w(), expected.w());
  EXPECT_FLOAT_EQ(actual.x(), expected.x());
  EXPECT_FLOAT_EQ(actual.y(), expected.y());
  EXPECT_FLOAT_EQ(actual.z(), expected.z());
}

}  // namespace

TEST(KinematicsMessage, TypeIsKinematics) {
  // General description:
  // Verifies the message type identifier for KinematicsMessage.
  // Arrange: prepare context for `projectairsim::KinematicsMessage message;`.
  projectairsim::KinematicsMessage message;

  // Act: run `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kKinematics);`.
  // Assert: check result from `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kKinematics);`.
  EXPECT_EQ(message.GetType(), projectairsim::MessageType::kKinematics);
}

TEST(KinematicsMessage, SerializeDeserializeRoundTripPreservesFields) {
  // General description:
  // Verifies full kinematics round-trip (pose, twist, and accelerations).
  // Arrange: prepare context for `const projectairsim::Kinematics kinematics(`.
  const projectairsim::Kinematics kinematics(
      projectairsim::Pose(
          projectairsim::Vector3(1.0f, -2.0f, 3.0f),
          projectairsim::Quaternion(projectairsim::AngleAxis(
              0.35f, projectairsim::Vector3(0.0f, 0.0f, 1.0f)))),
      projectairsim::Twist(projectairsim::Vector3(4.0f, 5.0f, 6.0f),
                           projectairsim::Vector3(-1.0f, -2.0f, -3.0f)),
      projectairsim::Accelerations(projectairsim::Vector3(0.1f, 0.2f, 0.3f),
                                   projectairsim::Vector3(-0.4f, -0.5f, -0.6f)));

  // Arrange: prepare context for `projectairsim::KinematicsMessage original(987654321LL, kinematics);`.
  projectairsim::KinematicsMessage original(987654321LL, kinematics);

  // Act: run `const std::string packed = original.Serialize();`.
  const std::string packed = original.Serialize();

  // Assert: check result from `EXPECT_FALSE(packed.empty());`.
  EXPECT_FALSE(packed.empty());

  // Act: run `projectairsim::KinematicsMessage unpacked;`.
  projectairsim::KinematicsMessage unpacked;
  unpacked.Deserialize(packed);

  // Assert: check result from `EXPECT_EQ(unpacked.GetTimeStamp(), 987654321LL);`.
  EXPECT_EQ(unpacked.GetTimeStamp(), 987654321LL);

  // Assert: check result from `const auto unpacked_kinematics = unpacked.GetKinematics();`.
  const auto unpacked_kinematics = unpacked.GetKinematics();
  ExpectVectorEq(unpacked_kinematics.pose.position, kinematics.pose.position);
  ExpectQuaternionEq(unpacked_kinematics.pose.orientation,
                     kinematics.pose.orientation);
  ExpectVectorEq(unpacked_kinematics.twist.linear, kinematics.twist.linear);
  ExpectVectorEq(unpacked_kinematics.twist.angular, kinematics.twist.angular);
  ExpectVectorEq(unpacked_kinematics.accels.linear, kinematics.accels.linear);
  ExpectVectorEq(unpacked_kinematics.accels.angular, kinematics.accels.angular);
}

TEST(KinematicsMessage, SerializationIsDeterministicAfterRoundTrip) {
  // General description:
  // Verifies deterministic serialization after deserialization.
  // Arrange: prepare context for `const projectairsim::Kinematics kinematics(`.
  const projectairsim::Kinematics kinematics(
      projectairsim::Pose(projectairsim::Vector3(-3.0f, 2.5f, 1.5f),
                          projectairsim::Quaternion::Identity()),
      projectairsim::Twist(projectairsim::Vector3::Zero(),
                           projectairsim::Vector3(0.0f, 0.0f, 0.1f)),
      projectairsim::Accelerations::Zero());

  // Arrange: prepare context for `projectairsim::KinematicsMessage original(123LL, kinematics);`.
  projectairsim::KinematicsMessage original(123LL, kinematics);

  // Act: run `const std::string packed = original.Serialize();`.
  const std::string packed = original.Serialize();

  // Act: run `projectairsim::KinematicsMessage unpacked;`.
  projectairsim::KinematicsMessage unpacked;
  unpacked.Deserialize(packed);

  // Assert: check result from `EXPECT_EQ(unpacked.Serialize(), packed);`.
  EXPECT_EQ(unpacked.Serialize(), packed);
}
