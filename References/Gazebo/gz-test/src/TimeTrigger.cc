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
#include <functional>
#include <gz/sim/Link.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/Pose.hh>

#include <gz/math/Helpers.hh>

#include "TimeTrigger.hh"

using namespace gz;
using namespace test;

//////////////////////////////////////////////////
TimeTrigger::TimeTrigger()
  : Trigger()
{
}

//////////////////////////////////////////////////
bool TimeTrigger::Load(const YAML::Node &_node)
{
  this->SetType(Trigger::TriggerType::TIME);

  if (_node["name"])
  {
    this->SetName(_node["name"].as<std::string>());
  }
  else
  {
    gzerr << "Time trigger is missing a name, skipping.\n";

    return false;
  }

  if (_node["time"])
  {
    YAML::Node timeNode = _node["time"];
    if (timeNode["duration"])
    {
      this->duration = math::stringToDuration(
          timeNode["duration"].as<std::string>());
    }
    else
    {
      gzerr << "Time trigger[" << this->Name()
        << "] is missing a duration, skipping.\n";
      return false;
    }

    if (timeNode["type"])
    {
      std::string timeType =
        common::lowercase(timeNode["type"].as<std::string>());
      if (timeType == "sim")
        this->type = TimeType::SIM;
      else if (timeType == "real")
        this->type = TimeType::REAL;
      else
      {
        gzerr << "Time trigger[" << this->Name()
          << "] is missing a time type, using simulation time.\n";
      }
    }
  }
  else
  {
    gzerr << "Time trigger[" << this->Name()
      << "] is missing a time, skipping.\n";
    return false;
  }

  Trigger::Load(_node);

  gzdbg << "\n\nCreated time trigger " << this->Name() << " with duration "
    << this->duration.count() << std::endl;

  return true;
}

//////////////////////////////////////////////////
void TimeTrigger::Update(const sim::UpdateInfo &_info,
    Test *_test, const sim::EntityComponentManager &_ecm)
{
  if (_info.simTime >= this->duration && !this->Triggered())
  {
    this->SetResult(this->RunOnCommands(_info, _test, _ecm));
    this->SetTriggered(true);
  }
}

//////////////////////////////////////////////////
void TimeTrigger::ResetImpl()
{
}
