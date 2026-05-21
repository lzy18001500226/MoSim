// Copyright (C) Microsoft Corporation. 
// Copyright (C) 2025 IAMAI CONSULTING CORP

// MIT License. All rights reserved.

#include "core_sim/actor/robot.hpp"
#include "core_sim/actuators/actuator.hpp"
#include "core_sim/config_json.hpp"
#include "core_sim/logger.hpp"
#include "core_sim/service_manager.hpp"
#include "gtest/gtest.h"
#include "json.hpp"
#include "state_manager.hpp"
#include "topic_manager.hpp"

namespace microsoft {
namespace projectairsim {

class Scene {  // : public ::testing::Test {
               // protected:
 public:
  static Robot MakeRobot(const std::string& id) {
    auto logger_callback = [](const std::string& component, LogLevel level,
                              const std::string& message) {};
    Logger logger(logger_callback);
    Transform origin = {{0, 0, 0}, {1, 0, 0, 0}};
    return Robot("TestRobotID", origin, logger, TopicManager(logger), "",
                 ServiceManager(logger), StateManager(logger));
  }

  static void LoadRobot(Robot& robot, ConfigJson config_json) {
    robot.Load(config_json);
  }

  static json get_actuator_config() {
    json config = R"({
            "links": [ { "name": "Frame" } ],
            "actuators": [ {
                    "name": "ID123",
                    "type": "rotor",
                    "enabled": true,
                    "parent-link": "ParentLink",
                    "child-link": "ChildLink",
                    "origin": {
                        "xyz": "0 0 0",
                        "rpy-deg": "0 0 0"
                    }
                }
            ]
        })"_json;
    return config;
  }
};

}  // namespace projectairsim
}  // namespace microsoft

namespace projectairsim = microsoft::projectairsim;
using json = nlohmann::json;

TEST(Actuator, HandlesNoActuators) {
  // General description:
  // Verifies handles no actuators for Actuator.
  // Arrange: prepare context for `auto config_json = R"({`.
  auto config_json = R"({
      "links": [ { "name": "Frame" } ]
    })"_json;
  auto robot = projectairsim::Scene::MakeRobot("TestRobot");
  projectairsim::Scene::LoadRobot(robot, config_json);
  // Act: run `auto& actuators = robot.GetActuators();`.
  auto& actuators = robot.GetActuators();
  // Assert: check result from `EXPECT_EQ(actuators.size(), 0);`.
  EXPECT_EQ(actuators.size(), 0);
}

TEST(Actuator, HandlesEmptyActuators) {
  // General description:
  // Verifies handles empty actuators for Actuator.
  // Arrange: prepare context for `auto config_json = projectairsim::Scene::get_actuator_config();`.
  auto config_json = projectairsim::Scene::get_actuator_config();
  //! Explicitly empty actuators for testing
  config_json["actuators"] = "[]"_json;
  auto robot = projectairsim::Scene::MakeRobot("TestRobot");
  projectairsim::Scene::LoadRobot(robot, config_json);
  // Act: run `auto& actuators = robot.GetActuators();`.
  auto& actuators = robot.GetActuators();
  // Assert: check result from `EXPECT_EQ(actuators.size(), 0);`.
  EXPECT_EQ(actuators.size(), 0);
}

TEST(Actuator, LoadsOneActuator) {
  // General description:
  // Verifies loads one actuator for Actuator.
  // Arrange: prepare context for `auto config_json = projectairsim::Scene::get_actuator_config();`.
  auto config_json = projectairsim::Scene::get_actuator_config();
  auto robot = projectairsim::Scene::MakeRobot("TestRobot");
  projectairsim::Scene::LoadRobot(robot, config_json);
  // Act: run `auto& actuators = robot.GetActuators();`.
  auto& actuators = robot.GetActuators();
  // Assert: check result from `EXPECT_EQ(actuators.size(), 1);`.
  EXPECT_EQ(actuators.size(), 1);
}

TEST(Actuator, LoadsTwoActuatorsSameID) {
  // General description:
  // Verifies loads two actuators same id for Actuator.
  // Arrange: prepare context for `auto config_json = projectairsim::Scene::get_actuator_config();`.
  auto config_json = projectairsim::Scene::get_actuator_config();
  //! Clone existing actuator
  config_json["actuators"].push_back(config_json["actuators"].at(0));
  auto robot = projectairsim::Scene::MakeRobot("TestRobot");
  projectairsim::Scene::LoadRobot(robot, config_json);
  // Act: run `auto& actuators = robot.GetActuators();`.
  auto& actuators = robot.GetActuators();
  // Assert: check result from `EXPECT_EQ(actuators.size(),`.
  EXPECT_EQ(actuators.size(),
            2);  // Multiple actuators can have the same ID, and each will refer
                 // to the same control output ID signal in the controller's
                 // "actuator-order" list (such as doubling a quadrotor to be a
                 // stacked octorotor). However, it is not possible to have
                 // multiple controller output signals tied to the same
                 // actuator, so the controller's "actuator-order" list can not
                 // have duplicate actuator IDs in it.
}

TEST(Actuator, LoadsTwoActuatorsDifferentID) {
  // General description:
  // Verifies loads two actuators different id for Actuator.
  // Arrange: prepare context for `json config_json = R"({`.
  json config_json = R"({
        "links": [ { "name": "Frame" } ],
        "actuators": [
          {
            "name": "ID123",
            "type": "rotor",
            "enabled": true,
            "parent-link": "ParentLink",
            "child-link": "ChildLink",
            "origin": {
              "xyz": "0 0 0",
              "rpy-deg": "0 0 0"
            }
          },
          {
            "name": "ID1234",
            "type": "rotor",
            "enabled": true,
            "parent-link": "ParentLink",
            "child-link": "ChildLink",
            "origin": {
              "xyz": "0 0 0",
              "rpy-deg": "0 0 0"
            }
          }
        ]
    })"_json;

  auto robot = projectairsim::Scene::MakeRobot("TestRobot");
  projectairsim::Scene::LoadRobot(robot, config_json);
  // Act: run `auto& actuators = robot.GetActuators();`.
  auto& actuators = robot.GetActuators();
  // Assert: check result from `EXPECT_EQ(actuators.size(), 2);`.
  EXPECT_EQ(actuators.size(), 2);
}
