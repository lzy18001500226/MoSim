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
#include <yaml-cpp/yaml.h>
#include "RegionTrigger.hh"
#include "TimeTrigger.hh"
#include "Test.hh"

using namespace gz;
using namespace test;

/////////////////////////////////////////////////
Test::Test()
{
}

/////////////////////////////////////////////////
bool Test::Load(const YAML::Node &_node)
{
  // The test name
  if (_node["name"])
    this->name = _node["name"].as<std::string>();

  if (_node["time-limit"])
  {
    YAML::Node timeNode = _node["time-limit"];
    if (timeNode["duration"])
    {
      this->maxDuration = math::stringToDuration(
          timeNode["duration"].as<std::string>());
    }
    else
    {
      gzerr << "Test [" << this->Name()
        << "] time-limit is missing a duration. "
        << "Unlimited duration will be used\n";
    }

    if (timeNode["type"])
    {
      std::string timeType =
        common::lowercase(timeNode["type"].as<std::string>());
      if (timeType == "sim")
        this->maxDurationType = TimeType::SIM;
      else if (timeType == "real")
        this->maxDurationType = TimeType::REAL;
      else
      {
        gzerr << "Test[" << this->Name()
          << "] time-limit is missing a time type, using simulation time.\n";
      }
    }
  }
  else
  {
    gzwarn << "Test[" << this->Name()
      << "] is missing a time-limit. Unlimited sim time will be used.\n";
  }

  // Load all the triggers
  for (YAML::const_iterator it = _node["triggers"].begin();
       it != _node["triggers"].end(); ++it)
  {
    std::string triggerType = (*it)["type"].as<std::string>();
    if (triggerType == "time")
    {
      auto trigger = std::make_unique<TimeTrigger>();
      trigger->Load(*it);
      this->triggers.push_back(std::move(trigger));
    }
    else if (triggerType == "region")
    {
      auto trigger = std::make_unique<RegionTrigger>();
      trigger->Load(*it);
      this->triggers.push_back(std::move(trigger));
    }
  }

  return true;
}

/////////////////////////////////////////////////
std::string Test::Name() const
{
  return this->name;
}

//////////////////////////////////////////////////
void Test::Configure(
    const sim::Entity &_entity,
    const std::shared_ptr<const sdf::Element> &,
    sim::EntityComponentManager &,
    sim::EventManager &)
{
  this->world = sim::World(_entity);
}

//////////////////////////////////////////////////
void Test::PreUpdate(const sim::UpdateInfo &,
    sim::EntityComponentManager &)
{
}

//////////////////////////////////////////////////
void Test::Update(const sim::UpdateInfo &,
    sim::EntityComponentManager &)
{
}

//////////////////////////////////////////////////
void Test::PostUpdate(const sim::UpdateInfo &_info,
    const sim::EntityComponentManager &_ecm)
{
  bool complete = true;
  for (std::unique_ptr<Trigger> &trigger : this->triggers)
  {
    trigger->Update(_info, this, _ecm);
    complete = complete && trigger->Result();
  }

  // If the test is complete, then stop.
  if (complete)
  {
    this->stopCb();
  }
}

//////////////////////////////////////////////////
bool Test::FillResults(domain::Test *_msg) const
{
  _msg->set_name(this->Name());

  bool failed = false;
  for (const std::unique_ptr<Trigger> &trigger : this->triggers)
  {
    domain::Trigger *triggerMsg = _msg->add_triggers();
    triggerMsg->set_name(trigger->Name());
    std::optional<bool> triggerResult = trigger->Result();

    bool triggerFailed = !triggerResult || !(*triggerResult);

    // Set failed if there is no result or the result is false.
    triggerMsg->set_failed(triggerFailed);

    failed = failed || triggerFailed;
  }

  _msg->set_failed(failed);
  return !failed;
}

//////////////////////////////////////////////////
bool Test::HasTrigger(const std::string &_name) const
{
  for (const std::unique_ptr<Trigger> &trigger : this->triggers)
  {
    if (trigger->Name() == _name)
      return true;
  }
  return false;
}

//////////////////////////////////////////////////
std::optional<bool> Test::RunTriggerFunction(
                  const std::string &_triggerName,
                  const std::string &_functionName,
                  const std::string &_parameter)
{
  for (std::unique_ptr<Trigger> &trigger : this->triggers)
  {
    if (trigger->Name() == _triggerName)
    {
      return trigger->RunFunction(_functionName, _parameter);
    }
  }
  return std::nullopt;
}

//////////////////////////////////////////////////
void Test::Stop()
{
  for (std::unique_ptr<Trigger> &trigger : this->triggers)
  {
    trigger->Stop();
  }
}

//////////////////////////////////////////////////
std::chrono::steady_clock::duration Test::MaxDuration()
{
  return this->maxDuration;
}

//////////////////////////////////////////////////
TimeType Test::MaxDurationType()
{
  return this->maxDurationType;
}

//////////////////////////////////////////////////
void Test::SetStopCallback(std::function<void()> &_cb)
{
  this->stopCb = _cb;
}

//////////////////////////////////////////////////
void Test::Reset()
{
  for (std::unique_ptr<Trigger> &trigger : this->triggers)
  {
    trigger->Reset();
  }
}
