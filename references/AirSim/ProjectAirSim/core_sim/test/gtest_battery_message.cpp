// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include <string>

#include "core_sim/message/battery_message.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

TEST(BatteryStateMessage, TypeIsBattery) {
  // General description:
  // Verifies that BatteryStateMessage exposes the expected message type.
  // Arrange: prepare context for `projectairsim::BatteryStateMessage message;`.
  projectairsim::BatteryStateMessage message;

  // Act: run `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kBattery);`.
  // Assert: check result from `EXPECT_EQ(message.GetType(), projectairsim::MessageType::kBattery);`.
  EXPECT_EQ(message.GetType(), projectairsim::MessageType::kBattery);
}

TEST(BatteryStateMessage, SerializeDeserializeRoundTripPreservesFields) {
  // General description:
  // Verifies serialization round-trip without field loss.
  // Arrange: prepare context for `const long long timestamp = 123456789LL;`.
  const long long timestamp = 123456789LL;
  const float battery_pct_remaining = 85.5f;
  const uint32_t estimated_time_remaining = 1200U;
  const std::string charge_state = "BATTERY_CHARGE_STATE_OK";

  // Arrange: prepare context for `projectairsim::BatteryStateMessage original(timestamp, battery_pct_remaining,`.
  projectairsim::BatteryStateMessage original(timestamp, battery_pct_remaining,
                                              estimated_time_remaining,
                                              charge_state);

  // Act: run `const std::string packed = original.Serialize();`.
  const std::string packed = original.Serialize();

  // Assert: check result from `EXPECT_FALSE(packed.empty());`.
  EXPECT_FALSE(packed.empty());

  // Act: run `projectairsim::BatteryStateMessage unpacked;`.
  projectairsim::BatteryStateMessage unpacked;
  unpacked.Deserialize(packed);

  // Assert: check result from `const auto data = unpacked.getData();`.
  const auto data = unpacked.getData();
  EXPECT_EQ(data.at("time_stamp").get<long long>(), timestamp);
  EXPECT_FLOAT_EQ(data.at("battery_pct_remaining").get<float>(),
                  battery_pct_remaining);
  EXPECT_EQ(data.at("estimated_time_remaining").get<uint32_t>(),
            estimated_time_remaining);
  EXPECT_EQ(data.at("battery_charge_state").get<std::string>(), charge_state);
}

TEST(BatteryStateMessage, SerializationIsDeterministic) {
  // General description:
  // Verifies that serializing the same object twice yields the same string.
  // Arrange: prepare context for `projectairsim::BatteryStateMessage message(42, 95.0f, 100U,`.
  projectairsim::BatteryStateMessage message(42, 95.0f, 100U,
                                             "BATTERY_CHARGE_STATE_OK");

  // Act: run `const std::string first = message.Serialize();`.
  const std::string first = message.Serialize();
  const std::string second = message.Serialize();

  // Assert: check result from `EXPECT_EQ(first, second);`.
  EXPECT_EQ(first, second);
}
