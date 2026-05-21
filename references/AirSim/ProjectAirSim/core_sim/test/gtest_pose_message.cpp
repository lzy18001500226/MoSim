// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include <string>

#include "core_sim/message/pose_message.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

TEST(PoseMessage, TypeIsPoseStamped) {
  // General description:
  // Verifies message type for PoseMessage.
  // Arrange: prepare context for `projectairsim::PoseMessage message;`.
  projectairsim::PoseMessage message;

  // Act: run `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kPosestamped);`.
  // Assert: check result from `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kPosestamped);`.
  EXPECT_EQ(message.GetType(), projectairsim::MessageType::kPosestamped);
}

TEST(PoseMessage, SerializeDeserializeRoundTripPreservesFields) {
  // General description:
  // Verifies serialization round-trip preserving position and orientation.
  // Arrange: prepare context for `const projectairsim::Vector3 position(1.25f, -2.5f, 3.75f);`.
  const projectairsim::Vector3 position(1.25f, -2.5f, 3.75f);
  const projectairsim::Quaternion orientation(
      projectairsim::AngleAxis(0.1f, projectairsim::Vector3::UnitX()) *
      projectairsim::AngleAxis(-0.2f, projectairsim::Vector3::UnitY()) *
      projectairsim::AngleAxis(0.3f, projectairsim::Vector3::UnitZ()));

  // Arrange: prepare context for `projectairsim::PoseMessage original(position, orientation);`.
  projectairsim::PoseMessage original(position, orientation);

  // Act: run `const std::string packed = original.Serialize();`.
  const std::string packed = original.Serialize();

  // Assert: check result from `EXPECT_FALSE(packed.empty());`.
  EXPECT_FALSE(packed.empty());

  // Act: run `projectairsim::PoseMessage unpacked;`.
  projectairsim::PoseMessage unpacked;
  unpacked.Deserialize(packed);

  // Assert: check result from `const auto unpacked_position = unpacked.GetPosition();`.
  const auto unpacked_position = unpacked.GetPosition();
  const auto unpacked_orientation = unpacked.GetOrientation();
  EXPECT_FLOAT_EQ(unpacked_position.x(), position.x());
  EXPECT_FLOAT_EQ(unpacked_position.y(), position.y());
  EXPECT_FLOAT_EQ(unpacked_position.z(), position.z());
  EXPECT_FLOAT_EQ(unpacked_orientation.w(), orientation.w());
  EXPECT_FLOAT_EQ(unpacked_orientation.x(), orientation.x());
  EXPECT_FLOAT_EQ(unpacked_orientation.y(), orientation.y());
  EXPECT_FLOAT_EQ(unpacked_orientation.z(), orientation.z());
}

TEST(PoseMessage, SerializationIsDeterministicAfterRoundTrip) {
  // General description:
  // Verifies deterministic serialization after deserialization.
  // Arrange: prepare context for `const projectairsim::Vector3 position(-4.0f, 2.0f, 0.5f);`.
  const projectairsim::Vector3 position(-4.0f, 2.0f, 0.5f);
  const projectairsim::Quaternion orientation(
      projectairsim::AngleAxis(-0.4f, projectairsim::Vector3::UnitZ()));

  // Arrange: prepare context for `projectairsim::PoseMessage original(position, orientation);`.
  projectairsim::PoseMessage original(position, orientation);

  // Act: run `const std::string packed = original.Serialize();`.
  const std::string packed = original.Serialize();
  projectairsim::PoseMessage unpacked;
  unpacked.Deserialize(packed);

  // Assert: check result from `EXPECT_EQ(unpacked.Serialize(), packed);`.
  EXPECT_EQ(unpacked.Serialize(), packed);
}
