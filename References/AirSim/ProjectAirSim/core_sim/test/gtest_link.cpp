// Copyright (C) Microsoft Corporation. 
// Copyright (C) 2025 IAMAI CONSULTING CORP

// MIT License. All rights reserved.

#include "core_sim/config_json.hpp"
#include "core_sim/error.hpp"
#include "core_sim/link.hpp"
#include "core_sim/logger.hpp"
#include "gtest/gtest.h"
#include "json.hpp"
#include "topic_manager.hpp"

namespace microsoft {
namespace projectairsim {

class Robot {
 public:
  static Link MakeLink() {
    auto callback = [](const std::string& component, LogLevel level,
                       const std::string& message) {};
    Logger logger(callback);
    TopicManager topic_mgr(logger);
    return Link(logger, topic_mgr, "");
  }

  static void LoadLink(Link& link, ConfigJson config_json) {
    link.Load(config_json);
  }
};

}  // namespace projectairsim
}  // namespace microsoft

namespace projectairsim = microsoft::projectairsim;
using json = nlohmann::json;

TEST(Link, Constructor) {
  // General description:
  // Verifies constructor for Link.
  // Arrange: prepare context for `EXPECT_FALSE(projectairsim::Robot::MakeLink().IsLoaded());`.
  // Act: run `EXPECT_FALSE(projectairsim::Robot::MakeLink().IsLoaded());`.
  // Assert: check result from `EXPECT_FALSE(projectairsim::Robot::MakeLink().IsLoaded());`.
  EXPECT_FALSE(projectairsim::Robot::MakeLink().IsLoaded());
}

TEST(Link, Load) {
  // General description:
  // Verifies load for Link.
  // Arrange: prepare context for `json json =`.
  json json =
      "{ \
            \"name\": \"a\", \
            \"visual\" : { \
                \"geometry\" : { \
                    \"type\": \"unreal_mesh\", \
                    \"name\" : \"Link_a\" \
                } \
            } \
        }"_json;

  auto link = projectairsim::Robot::MakeLink();
  // Act: run `projectairsim::Robot::LoadLink(link, json);`.
  projectairsim::Robot::LoadLink(link, json);
  // Assert: check result from `}`.
}

TEST(Link, IsLoaded) {
  // General description:
  // Verifies is loaded for Link.
  // Arrange: prepare context for `json json =`.
  json json =
      "{ \
            \"name\": \"a\", \
            \"visual\" : { \
                \"geometry\" : { \
                    \"type\": \"unreal_mesh\", \
                    \"name\" : \"Link_a\" \
                } \
            } \
        }"_json;

  auto link = projectairsim::Robot::MakeLink();
  // Act: run `projectairsim::Robot::LoadLink(link, json);`.
  projectairsim::Robot::LoadLink(link, json);
  // Assert: check result from `EXPECT_TRUE(link.IsLoaded());`.
  EXPECT_TRUE(link.IsLoaded());
}

TEST(Link, GetID) {
  // General description:
  // Verifies get id for Link.
  // Arrange: prepare context for `json json =`.
  json json =
      "{ \
            \"name\": \"a\", \
            \"visual\" : { \
                \"geometry\" : { \
                    \"type\": \"unreal_mesh\", \
                    \"name\" : \"Link_a\" \
                } \
            } \
        }"_json;

  auto link = projectairsim::Robot::MakeLink();
  // Act: run `projectairsim::Robot::LoadLink(link, json);`.
  projectairsim::Robot::LoadLink(link, json);
  // Assert: check result from `EXPECT_EQ(link.GetID(), "a");`.
  EXPECT_EQ(link.GetID(), "a");
}
