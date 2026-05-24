// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// Tests for IMU sensors

#include "core_sim/config_json.hpp"
#include "core_sim/logger.hpp"
#include "core_sim/sensors/gps.hpp"
#include "core_sim/sensors/sensor.hpp"
#include "core_sim/service_manager.hpp"
#include "gtest/gtest.h"
#include "state_manager.hpp"
#include "topic_manager.hpp"

namespace microsoft {
namespace projectairsim {

class Robot {
 public:
  static Gps MakeGps(const std::string& id, bool is_enabled,
                     const std::string& parent_link) {
    auto logger_callback = [](const std::string& component, LogLevel level,
                              const std::string& message) {};
    Logger logger(logger_callback);
    const std::string& parent_topic_path = "/gps_test_topic";
    return Gps(id, is_enabled, parent_link, logger, TopicManager(logger),
               parent_topic_path, ServiceManager(logger), StateManager(logger));
  }

  static void LoadGps(Gps& gps, ConfigJson config_json) {
    gps.Load(config_json);
  }

  static json GetBasicGpsConfig() {
    json config = R"({
      "id": "Gps1",
      "type": "gps",
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

TEST(Gps, SetsGpsID) {
  // General description:
  // Verifies sets gps id for Gps.
  // Arrange: prepare context for `const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();`.
  const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();
  const auto& id = gps_json["id"];
  const auto& is_enabled = gps_json["enabled"];
  const auto& parent_link = gps_json["parent-link"];
  // Act: run `auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);`.
  auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(gps.GetId(), std::string("Gps1"));`.
  EXPECT_EQ(gps.GetId(), std::string("Gps1"));
}

TEST(Gps, SetsSensorType) {
  // General description:
  // Verifies sets sensor type for Gps.
  // Arrange: prepare context for `const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();`.
  const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();
  const auto& id = gps_json["id"];
  const auto& is_enabled = gps_json["enabled"];
  const auto& parent_link = gps_json["parent-link"];
  // Act: run `auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);`.
  auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(gps.GetType(), projectairsim::SensorType::kGps);`.
  EXPECT_EQ(gps.GetType(), projectairsim::SensorType::kGps);
}

TEST(Gps, SetsIsEnabled) {
  // General description:
  // Verifies sets is enabled for Gps.
  // Arrange: prepare context for `const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();`.
  const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();
  const auto& id = gps_json["id"];
  auto is_enabled = gps_json["enabled"];
  const auto& parent_link = gps_json["parent-link"];
  // Act: run `auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);`.
  auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(gps.IsEnabled(), true);`.
  EXPECT_EQ(gps.IsEnabled(), true);
  is_enabled = false;
  gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  EXPECT_EQ(gps.IsEnabled(), false);
}

TEST(Gps, SetsParentLink) {
  // General description:
  // Verifies sets parent link for Gps.
  // Arrange: prepare context for `const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();`.
  const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();
  const auto& id = gps_json["id"];
  const auto& is_enabled = gps_json["enabled"];
  auto parent_link = gps_json["parent-link"];
  // Act: run `auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);`.
  auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(gps.GetParentLink(), std::string("ParentLink"));`.
  EXPECT_EQ(gps.GetParentLink(), std::string("ParentLink"));
  parent_link = std::string("NEW-PARENT-LINK-123");
  gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  EXPECT_EQ(gps.GetParentLink(), parent_link);
}

TEST(Gps, LoadsGps) {
  // General description:
  // Verifies loads gps for Gps.
  // Arrange: prepare context for `const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();`.
  const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();
  const auto& id = gps_json["id"];
  const auto& is_enabled = gps_json["enabled"];
  const auto& parent_link = gps_json["parent-link"];
  auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  // Act: run `projectairsim::Robot::LoadGps(gps, gps_json);`.
  projectairsim::Robot::LoadGps(gps, gps_json);
  // Assert: check result from `EXPECT_EQ(gps.IsLoaded(), true);`.
  EXPECT_EQ(gps.IsLoaded(), true);
}

TEST(Gps, SetsIsLoaded) {
  // General description:
  // Verifies sets is loaded for Gps.
  // Arrange: prepare context for `const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();`.
  const auto gps_json = projectairsim::Robot::GetBasicGpsConfig();
  const auto& id = gps_json["id"];
  const auto& is_enabled = gps_json["enabled"];
  const auto& parent_link = gps_json["parent-link"];
  // Act: run `auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);`.
  auto gps = projectairsim::Robot::MakeGps(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(gps.IsLoaded(), false);`.
  EXPECT_EQ(gps.IsLoaded(), false);
  projectairsim::Robot::LoadGps(gps, gps_json);
  EXPECT_EQ(gps.IsLoaded(), true);
}
