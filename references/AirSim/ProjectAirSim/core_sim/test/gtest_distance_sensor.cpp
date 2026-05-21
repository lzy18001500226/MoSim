// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// Tests for DistanceSensor sensors

#include "core_sim/config_json.hpp"
#include "core_sim/logger.hpp"
#include "core_sim/sensors/distance_sensor.hpp"
#include "core_sim/sensors/sensor.hpp"
#include "core_sim/service_manager.hpp"
#include "gtest/gtest.h"
#include "state_manager.hpp"
#include "topic_manager.hpp"

namespace microsoft {
namespace projectairsim {

class Robot {
 public:
  static DistanceSensor MakeDistanceSensor(const std::string& id, bool is_enabled,
                         const std::string& parent_link) {
    auto logger_callback = [](const std::string& component, LogLevel level,
                              const std::string& message) {};
    Logger logger(logger_callback);
    const std::string& parent_topic_path = "/DistanceSensor_test_topic";
    return DistanceSensor(id, is_enabled, parent_link, logger, TopicManager(logger),
                 parent_topic_path, ServiceManager(logger),
                 StateManager(logger));
  }

  static void LoadDistanceSensor(DistanceSensor& DistanceSensor, ConfigJson config_json) {
    DistanceSensor.Load(config_json);
  }

  static json GetBasicDistanceSensorConfig() {
    json config = R"({
      "id": "ID123",
      "type": "DistanceSensor",
      "enabled": true,
      "parent-link": "ParentLink",
      "min-distance": 0.5,
      "max-distance": 50.0,
      "draw-debug-points": false,
      "origin": {}
    })"_json;
    return config;
  }
};

}  // namespace projectairsim
}  // namespace microsoft

namespace projectairsim = microsoft::projectairsim;
using json = nlohmann::json;

// Test suit name should follow proper naming convention (no '_' strictly)

TEST(DistanceSensor, SetsDistanceSensorID) {
  // General description:
  // Verifies sets distance sensor id for DistanceSensor.
  // Arrange: prepare context for `auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();`.
  auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();
  auto id = DistanceSensor_json["id"];
  const auto& is_enabled = DistanceSensor_json["enabled"];
  const auto& parent_link = DistanceSensor_json["parent-link"];
  // Act: run `auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled...`.
  auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(DistanceSensor.GetId(), std::string("ID123"));`.
  EXPECT_EQ(DistanceSensor.GetId(), std::string("ID123"));
  id = "DistanceSensor123";
  DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  EXPECT_EQ(DistanceSensor.GetId(), std::string("DistanceSensor123"));
}

TEST(DistanceSensor, SetsSensorType) {
  // General description:
  // Verifies sets sensor type for DistanceSensor.
  // Arrange: prepare context for `auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();`.
  auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();
  auto id = DistanceSensor_json["id"];
  const auto& is_enabled = DistanceSensor_json["enabled"];
  const auto& parent_link = DistanceSensor_json["parent-link"];
  // Act: run `auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled...`.
  auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(DistanceSensor.GetType(), projectairsim::SensorType::kDistanceSensor);`.
  EXPECT_EQ(DistanceSensor.GetType(), projectairsim::SensorType::kDistanceSensor);
}

TEST(DistanceSensor, SetsIsEnabled) {
  // General description:
  // Verifies sets is enabled for DistanceSensor.
  // Arrange: prepare context for `auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();`.
  auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();
  auto id = DistanceSensor_json["id"];
  auto is_enabled = false;
  const auto& parent_link = DistanceSensor_json["parent-link"];
  // Act: run `auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled...`.
  auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(DistanceSensor.IsEnabled(), false);`.
  EXPECT_EQ(DistanceSensor.IsEnabled(), false);
  is_enabled = true;
  DistanceSensor = projectairsim::Robot::MakeDistanceSensor("TestDistanceSensor", is_enabled, parent_link);
  EXPECT_EQ(DistanceSensor.IsEnabled(), true);
}

TEST(DistanceSensor, SetsParentLink) {
  // General description:
  // Verifies sets parent link for DistanceSensor.
  // Arrange: prepare context for `auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();`.
  auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();
  auto id = DistanceSensor_json["id"];
  const auto& is_enabled = false;
  auto parent_link = DistanceSensor_json["parent-link"];
  // Act: run `auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled...`.
  auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(DistanceSensor.GetParentLink(), "ParentLink");`.
  EXPECT_EQ(DistanceSensor.GetParentLink(), "ParentLink");
  parent_link = "ParentLink123";
  DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  EXPECT_EQ(DistanceSensor.GetParentLink(), "ParentLink123");
}

TEST(DistanceSensor, LoadsDistanceSensor) {
  // General description:
  // Verifies loads distance sensor for DistanceSensor.
  // Arrange: prepare context for `auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();`.
  auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();
  auto id = DistanceSensor_json["id"];
  const auto& is_enabled = DistanceSensor_json["enabled"];
  const auto& parent_link = DistanceSensor_json["parent-link"];
  auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  // Act: run `projectairsim::Robot::LoadDistanceSensor(DistanceSensor, DistanceSensor_json);`.
  projectairsim::Robot::LoadDistanceSensor(DistanceSensor, DistanceSensor_json);
  // Assert: check result from `EXPECT_EQ(DistanceSensor.IsLoaded(), true);`.
  EXPECT_EQ(DistanceSensor.IsLoaded(), true);
}

TEST(DistanceSensor, SetsIsLoaded) {
  // General description:
  // Verifies sets is loaded for DistanceSensor.
  // Arrange: prepare context for `auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();`.
  auto DistanceSensor_json = projectairsim::Robot::GetBasicDistanceSensorConfig();
  auto id = DistanceSensor_json["id"];
  const auto& is_enabled = DistanceSensor_json["enabled"];
  const auto& parent_link = DistanceSensor_json["parent-link"];
  // Act: run `auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled...`.
  auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(DistanceSensor.IsLoaded(), false);`.
  EXPECT_EQ(DistanceSensor.IsLoaded(), false);
  projectairsim::Robot::LoadDistanceSensor(DistanceSensor, DistanceSensor_json);
  EXPECT_EQ(DistanceSensor.IsLoaded(), true);
}

TEST(DistanceSensor, DistanceSensorSetting) {
  // General description:
  // Verifies distance sensor setting for DistanceSensor.
  // Arrange: prepare context for `json DistanceSensor_json = R"({`.
  json DistanceSensor_json = R"({
      "id": "ID123",
      "type": "DistanceSensor",
      "enabled": true,
      "parent-link": "ParentLink",
      "min-distance": 0.5,
      "max-distance": 50.0,
      "draw-debug-points": false,
      "origin": {}
    })"_json;
  auto id = DistanceSensor_json["id"];
  const auto& is_enabled = DistanceSensor_json["enabled"];
  const auto& parent_link = DistanceSensor_json["parent-link"];
  // Act: run `auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled...`.
  auto DistanceSensor = projectairsim::Robot::MakeDistanceSensor(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(DistanceSensor.IsLoaded(), false);`.
  EXPECT_EQ(DistanceSensor.IsLoaded(), false);
  projectairsim::Robot::LoadDistanceSensor(DistanceSensor, DistanceSensor_json);
  const auto& DistanceSensor_settings = DistanceSensor.GetDistanceSensorSettings();
  EXPECT_EQ(DistanceSensor_settings.min_distance, 0.5);
  EXPECT_EQ(DistanceSensor_settings.max_distance, 50.0);
  EXPECT_EQ(DistanceSensor_settings.draw_debug_points, false);
}
