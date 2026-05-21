// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// Tests for Gyroscope in IMU sensors

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

TEST(ImuGyroscope, SetsAngleRandomWalkValueByDefault) {
  // General description:
  // Verifies sets angle random walk value by default for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_imu_settings.gyro.angle_random_walk, 8.726646e-05);`.
  EXPECT_FLOAT_EQ(actual_imu_settings.gyro.angle_random_walk, 8.726646e-05);
}
TEST(ImuGyroscope, EnablesAngleRandomWalkConfigParam) {
  // General description:
  // Verifies enables angle random walk config param for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  imu_json["gyroscope"] = R"({
    "angle-random-walk": 0.0123
  })"_json;
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  projectairsim::Robot::LoadImu(imu, imu_json);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_imu_settings.gyro.angle_random_walk, 0.0123);`.
  EXPECT_FLOAT_EQ(actual_imu_settings.gyro.angle_random_walk, 0.0123);
}

TEST(ImuGyroscope, SetsTauByDefault) {
  // General description:
  // Verifies sets tau by default for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_imu_settings.gyro.tau, 500);`.
  EXPECT_FLOAT_EQ(actual_imu_settings.gyro.tau, 500);
}

TEST(ImuGyroscope, EnablesTauConfigParam) {
  // General description:
  // Verifies enables tau config param for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  imu_json["gyroscope"] = R"({
    "tau": 123
  })"_json;
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  projectairsim::Robot::LoadImu(imu, imu_json);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_imu_settings.gyro.tau, 123);`.
  EXPECT_FLOAT_EQ(actual_imu_settings.gyro.tau, 123);
}

TEST(ImuGyroscope, SetsBiasStabilityByDefault) {
  // General description:
  // Verifies sets bias stability by default for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_imu_settings.gyro.bias_stability, 2.2301429e-05);`.
  EXPECT_FLOAT_EQ(actual_imu_settings.gyro.bias_stability, 2.2301429e-05);
}

TEST(ImuGyroscope, EnablesBiasStabilityConfigParam) {
  // General description:
  // Verifies enables bias stability config param for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  imu_json["gyroscope"] = R"({
    "bias-stability": 0.0123
  })"_json;
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  projectairsim::Robot::LoadImu(imu, imu_json);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_imu_settings.gyro.bias_stability, 0.0123);`.
  EXPECT_FLOAT_EQ(actual_imu_settings.gyro.bias_stability, 0.0123);
}

TEST(ImuGyroscope, SetsTurnOnBiasByDefault) {
  // General description:
  // Verifies sets turn on bias by default for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_EQ(actual_imu_settings.gyro.turn_on_bias,`.
  EXPECT_EQ(actual_imu_settings.gyro.turn_on_bias,
            projectairsim::Vector3(0, 0, 0));
}

TEST(ImuGyroscope, EnablesTurnOnBiasConfigParam) {
  // General description:
  // Verifies enables turn on bias config param for ImuGyroscope.
  // Arrange: prepare context for `auto imu_json = projectairsim::Robot::GetBasicImuConfig();`.
  auto imu_json = projectairsim::Robot::GetBasicImuConfig();
  const auto& id = imu_json["id"];
  const auto& is_enabled = imu_json["enabled"];
  const auto& parent_link = imu_json["parent-link"];
  imu_json["gyroscope"] = R"({
    "turn-on-bias": "1 2 3"
  })"_json;
  auto imu = projectairsim::Robot::MakeImu(id, is_enabled, parent_link);
  projectairsim::Robot::LoadImu(imu, imu_json);
  // Act: run `auto actual_imu_settings = imu.GetImuSettings();`.
  auto actual_imu_settings = imu.GetImuSettings();
  // Assert: check result from `EXPECT_EQ(actual_imu_settings.gyro.turn_on_bias,`.
  EXPECT_EQ(actual_imu_settings.gyro.turn_on_bias,
            projectairsim::Vector3(1, 2, 3));
}
