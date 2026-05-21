// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// Tests for IMU sensors

#include "core_sim/config_json.hpp"
#include "core_sim/logger.hpp"
#include "core_sim/sensors/barometer.hpp"
#include "core_sim/sensors/sensor.hpp"
#include "core_sim/service_manager.hpp"
#include "gtest/gtest.h"
#include "state_manager.hpp"
#include "topic_manager.hpp"

namespace microsoft {
namespace projectairsim {

class Robot {
 public:
  static Barometer MakeBarometer(const std::string& id, bool is_enabled,
                                 const std::string& parent_link) {
    auto logger_callback = [](const std::string& component, LogLevel level,
                              const std::string& message) {};
    Logger logger(logger_callback);
    const std::string& parent_topic_path = "/barometer_test_topic";
    return Barometer(id, is_enabled, parent_link, logger, TopicManager(logger),
                     parent_topic_path, ServiceManager(logger),
                     StateManager(logger));
  }

  static void LoadBarometer(Barometer& barometer, ConfigJson config_json) {
    barometer.Load(config_json);
  }

  static json GetBasicBarometerConfig() {
    json config = R"({
      "id": "Barometer1",
      "type": "barometer",
      "enabled": true,
      "parent-link": "ParentLink"
    })"_json;
    return config;
  }
};

}  // namespace projectairsim
}  // namespace microsoft

namespace projectairsim = microsoft::projectairsim;
using json = nlohmann::json;

TEST(Barometer, SetsBarometerID) {
  // General description:
  // Verifies sets barometer id for Barometer.
  // Arrange: prepare context for `const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();`.
  const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();
  const auto& id = barometer_json["id"];
  const auto& is_enabled = barometer_json["enabled"];
  const auto& parent_link = barometer_json["parent-link"];
      // Act: run `auto barometer =`.
  auto barometer =
      projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(barometer.GetId(), std::string("Barometer1"));`.
  EXPECT_EQ(barometer.GetId(), std::string("Barometer1"));
}

TEST(Barometer, SetsSensorType) {
  // General description:
  // Verifies sets sensor type for Barometer.
  // Arrange: prepare context for `const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();`.
  const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();
  const auto& id = barometer_json["id"];
  const auto& is_enabled = barometer_json["enabled"];
  const auto& parent_link = barometer_json["parent-link"];
      // Act: run `auto barometer =`.
  auto barometer =
      projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(barometer.GetType(), projectairsim::SensorType::kBarometer);`.
  EXPECT_EQ(barometer.GetType(), projectairsim::SensorType::kBarometer);
}

TEST(Barometer, SetsIsEnabled) {
  // General description:
  // Verifies sets is enabled for Barometer.
  // Arrange: prepare context for `const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();`.
  const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();
  const auto& id = barometer_json["id"];
  auto is_enabled = barometer_json["enabled"];
  const auto& parent_link = barometer_json["parent-link"];
      // Act: run `auto barometer =`.
  auto barometer =
      projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(barometer.IsEnabled(), true);`.
  EXPECT_EQ(barometer.IsEnabled(), true);
  is_enabled = false;
  barometer = projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  EXPECT_EQ(barometer.IsEnabled(), false);
}

TEST(Barometer, SetsParentLink) {
  // General description:
  // Verifies sets parent link for Barometer.
  // Arrange: prepare context for `const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();`.
  const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();
  const auto& id = barometer_json["id"];
  const auto& is_enabled = barometer_json["enabled"];
  auto parent_link = barometer_json["parent-link"];
      // Act: run `auto barometer =`.
  auto barometer =
      projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(barometer.GetParentLink(), std::string("ParentLink"));`.
  EXPECT_EQ(barometer.GetParentLink(), std::string("ParentLink"));
  parent_link = std::string("NEW-PARENT-LINK-123");
  barometer = projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  EXPECT_EQ(barometer.GetParentLink(), parent_link);
}

TEST(Barometer, LoadsBarometer) {
  // General description:
  // Verifies loads barometer for Barometer.
  // Arrange: prepare context for `const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();`.
  const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();
  const auto& id = barometer_json["id"];
  const auto& is_enabled = barometer_json["enabled"];
  const auto& parent_link = barometer_json["parent-link"];
  auto barometer =
      projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  // Act: run `projectairsim::Robot::LoadBarometer(barometer, barometer_json);`.
  projectairsim::Robot::LoadBarometer(barometer, barometer_json);
  // Assert: check result from `EXPECT_EQ(barometer.IsLoaded(), true);`.
  EXPECT_EQ(barometer.IsLoaded(), true);
}

TEST(Barometer, SetsIsLoaded) {
  // General description:
  // Verifies sets is loaded for Barometer.
  // Arrange: prepare context for `const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();`.
  const auto barometer_json = projectairsim::Robot::GetBasicBarometerConfig();
  const auto& id = barometer_json["id"];
  const auto& is_enabled = barometer_json["enabled"];
  const auto& parent_link = barometer_json["parent-link"];
      // Act: run `auto barometer =`.
  auto barometer =
      projectairsim::Robot::MakeBarometer(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(barometer.IsLoaded(), false);`.
  EXPECT_EQ(barometer.IsLoaded(), false);
  projectairsim::Robot::LoadBarometer(barometer, barometer_json);
  EXPECT_EQ(barometer.IsLoaded(), true);
}
