// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// Tests for Robot class

#include <memory>

#include "core_sim/actor/robot.hpp"
#include "core_sim/config_json.hpp"
#include "core_sim/error.hpp"
#include "core_sim/logger.hpp"
#include "core_sim/service_manager.hpp"
#include "gtest/gtest.h"
#include "json.hpp"
#include "state_manager.hpp"
#include "topic_manager.hpp"

using json = nlohmann::json;

namespace microsoft {
namespace projectairsim {

class Scene {
 public:
  static Robot MakeRobot(const std::string& id) {
    Transform origin = {{0, 0, 0}, {1, 0, 0, 0}};
    auto callback = [](const std::string& component, LogLevel level,
                       const std::string& message) {};
    Logger logger(callback);
    return Robot(id, origin, logger, TopicManager(logger), "",
                 ServiceManager(logger), StateManager(logger));
  }

  static void LoadRobot(Robot& robot, ConfigJson config_json) {
    robot.Load(config_json);
  }
};

}  // namespace projectairsim
}  // namespace microsoft

namespace projectairsim = microsoft::projectairsim;

TEST(Robot, Constructor) {
  // General description:
  // Verifies constructor for Robot.
  // Arrange: prepare context for `EXPECT_FALSE(projectairsim::Scene::MakeRobot("abc").IsLoaded());`.
  // Act: run `EXPECT_FALSE(projectairsim::Scene::MakeRobot("abc").IsLoaded());`.
  // Assert: check result from `EXPECT_FALSE(projectairsim::Scene::MakeRobot("abc").IsLoaded());`.
  EXPECT_FALSE(projectairsim::Scene::MakeRobot("abc").IsLoaded());
}

TEST(Robot, LoadRobot) {
  // General description:
  // Verifies load robot for Robot.
  // Arrange: prepare context for `json json = R"({`.
  json json = R"({
      "links": [ { "name": "Frame" } ]
    })"_json;
  auto robot = projectairsim::Scene::MakeRobot("a");
  // Act: run `projectairsim::Scene::LoadRobot(robot, json);`.
  projectairsim::Scene::LoadRobot(robot, json);
  // Assert: check result from `}`.
}

TEST(Robot, IsLoaded) {
  // General description:
  // Verifies is loaded for Robot.
  // Arrange: prepare context for `json json = R"({`.
  json json = R"({
      "links": [ { "name": "Frame" } ]
    })"_json;
  auto robot = projectairsim::Scene::MakeRobot("a");
  // Act: run `projectairsim::Scene::LoadRobot(robot, json);`.
  projectairsim::Scene::LoadRobot(robot, json);
  // Assert: check result from `EXPECT_TRUE(robot.IsLoaded());`.
  EXPECT_TRUE(robot.IsLoaded());
}

TEST(Robot, GetID) {
  // General description:
  // Verifies get id for Robot.
  // Arrange: prepare context for `json json = R"({`.
  json json = R"({
      "links": [ { "name": "Frame" } ]
    })"_json;
  auto robot = projectairsim::Scene::MakeRobot("a");
  // Act: run `projectairsim::Scene::LoadRobot(robot, json);`.
  projectairsim::Scene::LoadRobot(robot, json);
  // Assert: check result from `EXPECT_EQ(robot.GetID(), "a");`.
  EXPECT_EQ(robot.GetID(), "a");
}

TEST(Robot, GetType) {
  // General description:
  // Verifies get type for Robot.
  // Arrange: prepare context for `json json = R"({`.
  json json = R"({
      "links": [ { "name": "Frame" } ]
    })"_json;
  auto robot = projectairsim::Scene::MakeRobot("a");
  // Act: run `projectairsim::Scene::LoadRobot(robot, json);`.
  projectairsim::Scene::LoadRobot(robot, json);
  // Assert: check result from `EXPECT_EQ(robot.GetType(), projectairsim::ActorType::kRobot);`.
  EXPECT_EQ(robot.GetType(), projectairsim::ActorType::kRobot);
}

TEST(Robot, GetLinks) {
  // General description:
  // Verifies get links for Robot.
  // Arrange: prepare context for `json json = R"({`.
  json json = R"({
        "links": [
          {
            "name": "link1",
            "visual": {
              "geometry": {
                  "type": "unreal_mesh",
                  "name": "Link1"
              }
            }
          },
          {
            "name": "link2",
            "visual": {
                "geometry": {
                  "type": "unreal_mesh",
                  "name": "Link2"
              }
            }
          }
        ]
      })"_json;

  auto robot = projectairsim::Scene::MakeRobot("a");
  // Act: run `projectairsim::Scene::LoadRobot(robot, json);`.
  projectairsim::Scene::LoadRobot(robot, json);
  // Assert: check result from `EXPECT_EQ(robot.GetLinks().size(), 2);`.
  EXPECT_EQ(robot.GetLinks().size(), 2);
}
