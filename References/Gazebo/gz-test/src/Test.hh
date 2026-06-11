/*
 * Copyright (C) 2022 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/
#ifndef GZ_TEST_TEST_HH_
#define GZ_TEST_TEST_HH_

#include <yaml-cpp/yaml.h>

#include <gz/sim/Server.hh>
#include <gz/sim/ServerConfig.hh>
#include <gz/sim/World.hh>

#include "msgs/test.pb.h"
#include "Trigger.hh"
#include "Util.hh"
#include "gz/test/config.hh"

using namespace std::chrono_literals;

namespace gz
{
  namespace test
  {
    // Inline bracket to help doxygen filtering.
    inline namespace GZ_TEST_VERSION_NAMESPACE {
    class Test :
            public sim::System,
            public sim::ISystemConfigure,
            public sim::ISystemPreUpdate,
            public sim::ISystemUpdate,
            public sim::ISystemPostUpdate

    {
      /// \brief Default constructor.
      public: Test();

      // Configure callback
      public: void Configure(const sim::Entity &_entity,
                             const std::shared_ptr<const sdf::Element> &_sdf,
                             sim::EntityComponentManager &_ecm,
                             sim::EventManager &_eventMgr) override;

      // Pre update update callback
      public: void PreUpdate(const sim::UpdateInfo &_info,
                  sim::EntityComponentManager &_ecm) override;

      // Documentation inherited
      public: void Update(const sim::UpdateInfo &_info,
                    sim::EntityComponentManager &_ecm) override;

      // Post update callback
      public: void PostUpdate(const sim::UpdateInfo &_info,
                    const sim::EntityComponentManager &_ecm) override;

      /// \brief Load a test.
      /// \param[in] _node The YAML node containing test information
      /// \return True if the test was loaded successfully.
      public: bool Load(const YAML::Node &_node);

      /// \brief Get the test's name.
      /// \return The name of the test.
      public: std::string Name() const;

      /// \brief Fill in a Test message with the results.
      /// \param[in] _msg The message to populate.
      /// \return True if the test passed, false otherwise.
      public: bool FillResults(domain::Test *_msg) const;

      /// \brief Check if a trigger with the given name exists.
      /// \return True if the trigger exists.
      public: bool HasTrigger(const std::string &_name) const;

      public: std::optional<bool> RunTriggerFunction(
                  const std::string &_triggerName,
                  const std::string &_functionName,
                  const std::string &_parameter);

      /// \brief Stop the test.
      public: void Stop();

      public: std::chrono::steady_clock::duration MaxDuration();

      /// \brief Get the time type (sim or real) associated with
      /// MaxDuration.
      /// \return The time type, sim or real, for max duration.
      public: TimeType MaxDurationType();

      public: void SetStopCallback(std::function<void()> &_cb);

      /// \brief Reset the test. This clears the results.
      public: void Reset();

      private: sim::World world;

      /// \brief Name of the test
      private: std::string name;

      /// \brief The list of triggers for the test.
      private: std::vector<std::unique_ptr<Trigger>> triggers;

      public: std::chrono::steady_clock::duration maxDuration{0s};
      public: TimeType maxDurationType{TimeType::SIM};

      public: std::function<void()> stopCb;
    };
    }
  }
}

#endif
