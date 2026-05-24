// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// Tests for IMU sensors

#include "core_sim/config_json.hpp"
#include "core_sim/logger.hpp"
#include "core_sim/sensors/imu.hpp"
#include "core_sim/sensors/sensor.hpp"
#include "core_sim/service_manager.hpp"
#include "gtest/gtest.h"
#include "state_manager.hpp"
#include "topic_manager.hpp"

namespace microsoft {
namespace projectairsim {

class Robot {  // : public ::testing::Test {
               // protected:
 public:
  static Imu MakeImu(const std::string& id, bool is_enabled,
                     const std::string& parent_link) {
    auto logger_callback = [](const std::string& component, LogLevel level,
                              const std::string& message) {};
    Logger logger(logger_callback);
    const std::string& parent_topic_path = "/imu_test_topic";
    return Imu(id, is_enabled, parent_link, logger, TopicManager(logger),
               parent_topic_path, ServiceManager(logger), StateManager(logger));
  }

  static void LoadImu(Imu& imu, ConfigJson config_json) {
    imu.Load(config_json);
  }

  static json GetBasicImuConfig() {
    json config = R"({
      "id": "IMU123",
      "type": "imu",
      "enabled": true,
      "parent-link": "ParentLink",
      "accelerometer": {},
      "gyroscope": {},
      "origin": {}
    })"_json;
    return config;
  }
};

}  // namespace projectairsim
}  // namespace microsoft

namespace projectairsim = microsoft::projectairsim;
using json = nlohmann::json;

TEST(Imu, SetsImuID) {
  // General description:
  // Validates that Imu::GetId returns the same identifier passed at
  // construction.
  // Arrange: prepare context for `const auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  const auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  // Arrange: prepare context for `const auto& id = imu_json["id"];`.
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  // Act: run `auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);`.
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(imu.GetId(), std::string("IMU123"));`.
  EXPECT_EQ(imu.GetId(), std::string("IMU123"));
}

TEST(Imu, SetsSensorType) {
  // General description:
  // Confirms IMU instances report sensor type kImu.
  // Arrange: prepare context for `const auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  const auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  // Act: run `auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);`.
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(imu.GetType(), projectairsim::SensorType::kImu);`.
  EXPECT_EQ(imu.GetType(), projectairsim::SensorType::kImu);
}

TEST(Imu, SetsIsEnabled) {
  // General description:
  // Verifies that enable state follows constructor input for both true and
  // false values.
  // Arrange: prepare context for `const auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  const auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  auto is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  // Act: run `auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);`.
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(imu.IsEnabled(), true);`.
  EXPECT_EQ(imu.IsEnabled(), true);
  // Act: run `is_enabled = false;`.
  is_enabled = false;
  imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(imu.IsEnabled(), false);`.
  EXPECT_EQ(imu.IsEnabled(), false);
}

TEST(Imu, SetsParentLink) {
  // General description:
  // Verifies parent-link propagation from constructor to accessor and confirms
  // updates when a different link is supplied.
  // Arrange: prepare context for `const auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  const auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  auto parent_link = imu_json["parent-link"];
  // Act: run `auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);`.
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(imu.GetParentLink(), std::string("ParentLink"));`.
  EXPECT_EQ(imu.GetParentLink(), std::string("ParentLink"));
  // Act: run `parent_link = std::string("NEW-PARENT-LINK-123");`.
  parent_link = std::string("NEW-PARENT-LINK-123");
  imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(imu.GetParentLink(), parent_link);`.
  EXPECT_EQ(imu.GetParentLink(), parent_link);
}

TEST(Imu, LoadsImu) {
  // General description:
  // Ensures Load() transitions the IMU from not-loaded to loaded.
  // Arrange: prepare context for `const auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  const auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Act: run `projectairsim::Robot::LoadImu(imu, imu_json);`.
  projectairsim::Robot::LoadImu(imu, imu_json);
  // Assert: check result from `EXPECT_EQ(imu.IsLoaded(), true);`.
  EXPECT_EQ(imu.IsLoaded(), true);
}

TEST(Imu, SetsIsLoaded) {
  // General description:
  // Verifies IsLoaded is false immediately after construction and true after
  // calling Load().
  // Arrange: prepare context for `const auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  const auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  // Act: run `auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);`.
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Assert: check result from `EXPECT_EQ(imu.IsLoaded(), false);`.
  EXPECT_EQ(imu.IsLoaded(), false);
  // Act: run `projectairsim::Robot::LoadImu(imu, imu_json);`.
  projectairsim::Robot::LoadImu(imu, imu_json);
  // Assert: check result from `EXPECT_EQ(imu.IsLoaded(), true);`.
  EXPECT_EQ(imu.IsLoaded(), true);
}
