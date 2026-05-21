// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include <string>
#include <vector>

#include "core_sim/message/rotor_message.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

TEST(RotorMessage, TypeIsRotorInfo) {
  // General description:
  // Verifies message type for RotorMessage.
  // Arrange: prepare context for `projectairsim::RotorMessage message;`.
  projectairsim::RotorMessage message;

  // Act: run `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kRotorInfo);`.
  // Assert: check result from `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kRotorInfo);`.
  EXPECT_EQ(message.GetType(), projectairsim::MessageType::kRotorInfo);
}

TEST(RotorMessage, SerializeDeserializeSerializePreservesPayload) {
  // General description:
  // Verifies that serialize->deserialize->serialize preserves payload.
  // Arrange: prepare context for `const std::vector<projectairsim::RotorInfo> rotor_info = {`.
  const std::vector<projectairsim::RotorInfo> rotor_info = {
      projectairsim::RotorInfo("rotor_0", 3000.0f, 0.2f, 0.1f, 4.0f),
      projectairsim::RotorInfo("rotor_1", 3100.0f, 0.3f, 0.12f, 4.1f),
      projectairsim::RotorInfo("rotor_2", 3200.0f, 0.4f, 0.14f, 4.2f),
      projectairsim::RotorInfo("rotor_3", 3300.0f, 0.5f, 0.16f, 4.3f)};

  // Arrange: prepare context for `projectairsim::RotorMessage original(1000, rotor_info);`.
  projectairsim::RotorMessage original(1000, rotor_info);

  // Act: run `const std::string packed = original.Serialize();`.
  const std::string packed = original.Serialize();

  // Assert: check result from `EXPECT_FALSE(packed.empty());`.
  EXPECT_FALSE(packed.empty());

  // Act: run `projectairsim::RotorMessage unpacked;`.
  projectairsim::RotorMessage unpacked;
  unpacked.Deserialize(packed);
  const std::string repacked = unpacked.Serialize();

  // Assert: check result from `EXPECT_EQ(packed, repacked);`.
  EXPECT_EQ(packed, repacked);
}

TEST(RotorMessage, HandlesEmptyRotorVector) {
  // General description:
  // Verifies correct behavior with an empty rotor vector.
  // Arrange: prepare context for `const std::vector<projectairsim::RotorInfo> empty_info;`.
  const std::vector<projectairsim::RotorInfo> empty_info;
  projectairsim::RotorMessage message(77, empty_info);

  // Act: run `const std::string packed = message.Serialize();`.
  const std::string packed = message.Serialize();

  // Assert: check result from `EXPECT_FALSE(packed.empty());`.
  EXPECT_FALSE(packed.empty());

  // Act: run `projectairsim::RotorMessage unpacked;`.
  projectairsim::RotorMessage unpacked;
  EXPECT_NO_THROW(unpacked.Deserialize(packed));
  EXPECT_EQ(unpacked.GetType(), projectairsim::MessageType::kRotorInfo);
}
