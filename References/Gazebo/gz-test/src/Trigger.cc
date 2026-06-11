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
#include <regex>
#ifndef _WIN32
  #include <semaphore.h>
  #include <sys/stat.h>
  #include <sys/wait.h>
  #include <unistd.h>
#else
  #include <process.h>
  /* Needed for std::min */
  #ifndef NOMINMAX
    #define NOMINMAX
  #endif
  #include <windows.h>
  #include <Processthreadsapi.h>
#endif

#include "gz/sim/Entity.hh"
#include "gz/sim/Model.hh"
#include "gz/sim/Util.hh"
#include "gz/sim/components/Pose.hh"
#include "Test.hh"
#include "Trigger.hh"
#include "Util.hh"

using namespace gz;
using namespace test;

/////////////////////////////////////////////////
Trigger::Trigger()
{
}

//////////////////////////////////////////////////
bool Trigger::Load(const YAML::Node &_node)
{
  // Load the on commands
  if (_node["on"])
    this->LoadOnCommands(_node["on"]);

  return false;
}


//////////////////////////////////////////////////
bool Trigger::LoadOnCommands(const YAML::Node &_node)
{
  if (!_node.IsSequence())
    return false;

  // Iterate over the sequence of commands.
  for (YAML::const_iterator it = _node.begin(); it!=_node.end(); ++it)
  {
    if ((*it)["script"])
    {
      for (YAML::const_iterator scriptIt = (*it)["script"].begin();
           scriptIt != (*it)["script"].end(); ++scriptIt)
      {
        this->commands.push_back(scriptIt->as<std::string>());
      }

    }
    else if ((*it)["expect"])
    {
      std::string expectation = (*it)["expect"].as<std::string>();
      this->expectations.push_back({expectation, false});
    }
    else if ((*it)["assert"])
    {
      std::string assertion = (*it)["assert"].as<std::string>();
      this->expectations.push_back({assertion, true});
    }

  }
  return true;
}

//////////////////////////////////////////////////
bool Trigger::CheckExpectations(const sim::UpdateInfo &_info, Test *_test,
    const sim::EntityComponentManager &_ecm)
{
  bool expResult = true;
  for (const std::pair<std::string, bool> &expect : this->expectations)
  {
    // Strip out the beginning "${{" and ending "}}"
    size_t startIdx = expect.first.find("${{")+3;
    size_t endIdx = expect.first.find("}}");
    std::string exp = expect.first.substr(startIdx, endIdx-startIdx);

    // Attempt to get a result from an expectation that is an equation.
    std::optional<bool> r = this->ParseEquation(_info, exp, _ecm);
    if (r)
    {
      expResult = expResult && *r;

      // Short circuit if assert and result was false
      if (expect.second && !(*r))
      {
        gzerr << "Assertion\n";
        return expResult;
      }

      if (!(*r))
        gzdbg << "Expecation[" << exp << "] failed\n";
      continue;
    }

    // Attempt to get a result from an expectation that is a function.
    r = this->ParseFunction(_test, exp);
    if (r)
    {
      expResult = expResult && *r;

      // Short circuit if assert and results was false
      if (expect.second && !(*r))
      {
        gzerr << "Assertion\n";
        return expResult;
      }

      if (!(*r))
        gzdbg << "Expecation[" << exp << "] failed\n";

      continue;
    }
    gzerr << "Invalid expectation[" << exp << "]\n";
  }
  return expResult;
}

//////////////////////////////////////////////////
bool Trigger::RunOnCommands(const sim::UpdateInfo &_info, Test *_test,
    const sim::EntityComponentManager &_ecm)
{
  if (!this->CheckExpectations(_info, _test, _ecm))
    return false;

  return this->processManager.RunExecutablesAsBash(this->commands);
}

//////////////////////////////////////////////////
std::string Trigger::Name() const
{
  return this->name;
}

//////////////////////////////////////////////////
void Trigger::SetName(const std::string &_name)
{
  this->name = _name;
}

//////////////////////////////////////////////////
Trigger::TriggerType Trigger::Type() const
{
  return this->type;
}

//////////////////////////////////////////////////
void Trigger::SetType(const TriggerType &_type)
{
  this->type = _type;
}

/////////////////////////////////////////////////


//////////////////////////////////////////////////
void Trigger::SetResult(bool _passed)
{
  this->result = _passed;
}

//////////////////////////////////////////////////
std::optional<bool> Trigger::Result() const
{
  return this->result;
}

//////////////////////////////////////////////////
std::optional<bool> Trigger::ParseFunction(Test *_test,
    const std::string &_str)
{
  std::string str = common::trimmed(_str);
  std::vector<std::string> parts = common::split(str, ".");
  if (parts.size() > 1)
  {
    std::string part1 = common::trimmed(parts[0]);

    // Check if there is a negation
    bool negate = false;
    if (part1[0] == '!')
    {
      negate = true;
      part1.erase(0,1);
    }

    // Make sure the named trigger exists.
    if (_test->HasTrigger(part1))
    {
      std::string function = common::trimmed(parts[1]);
      size_t parenStart = function.find("(");
      size_t parenEnd = function.find(")");
      std::string functionName = function.substr(0, parenStart);
      std::string param = function.substr(parenStart+1,
          parenEnd-parenStart-1);

      // Get the result of running the trigger's function.
      std::optional<bool> funcResult =
        _test->RunTriggerFunction(part1, functionName, param);

      // Negate the results if necessary.
      if (funcResult && negate)
        return !(*funcResult);

      return funcResult;
    }
  }

  return std::nullopt;
}

//////////////////////////////////////////////////
std::optional<bool> Trigger::ParseEquation(const sim::UpdateInfo &_info,
    const std::string &_str,
    const sim::EntityComponentManager &_ecm)
{
  std::regex reg(R"(==|!=|>=|<=|<|>)");
  auto expBegin = std::sregex_iterator(_str.begin(), _str.end(), reg);
  auto expEnd = std::sregex_iterator();
  for (std::sregex_iterator it = expBegin; it != expEnd; ++it)
  {
    std::smatch match = *it;

    std::string prefix = it->prefix().str();
    std::string suffix = it->suffix().str();

    std::optional<double> preValue = this->ParseValue(prefix, _info, _ecm);
    std::optional<double> sufValue = this->ParseValue(suffix, _info, _ecm);

    if (preValue && sufValue)
    {
      if (it->str() == "==")
        return math::equal(*preValue, *sufValue);
      else if (it->str() == "!=")
        return !math::equal(*preValue, *sufValue);
      else if (it->str() == ">=")
        return *preValue >= *sufValue;
      else if (it->str() == "<=")
        return *preValue <= *sufValue;
      else if (it->str() == ">")
        return *preValue > *sufValue;
      else if (it->str() == "<")
      {
        std::cout << "Pre[" << *preValue << "] Suf[" << *sufValue << "]\n";
        return *preValue < *sufValue;
      }
      else
        gzerr << "Invalid equation operation[" << it->str() << "]\n";
    }
    else
      gzerr << "Unable to parse equation prefix or suffix\n";
  }
  return std::nullopt;
}

//////////////////////////////////////////////////
std::optional<double> Trigger::ParseValue(const std::string &_str,
    const sim::UpdateInfo &_info,
    const sim::EntityComponentManager &_ecm)
{
  std::string str = common::trimmed(_str);

  // Try to parse the string as a double.
  try
  {
    return std::stod(str);
  }
  catch(...)
  {
    // Do nothing here.
  }

  // Does the string contain dots?
  if (str.find(".") != std::string::npos)
  {
    std::vector<std::string> parts = common::split(str, ".");

    // Try to get Gazebo entities based on the name
    std::unordered_set<sim::Entity> entities =
      sim::entitiesFromScopedName(parts[0], _ecm);

    if (!entities.empty())
    {
      if (parts.size() == 3 && parts[1] == "pose")
      {
        // Get the pose of the entity
        math::Pose3d pose = sim::worldPose(*entities.begin(), _ecm);
        return ParsePoseProperty(pose, parts[2]);
      }
      else
      {
        gzerr << "Invalid expectation parameter[" << str << "]\n";
      }
    }
    else if (parts[0] == "simulation")
    {
      if (parts.size() == 2 && parts[1] == "time")
        return std::chrono::duration<double>(_info.simTime).count();
    }
  }
  else if (math::isTimeString(str))
  {
    return static_cast<double>(math::stringToDuration(str).count());
  }

  return std::nullopt;
}

//////////////////////////////////////////////////
std::optional<double> Trigger::ParsePoseProperty(const math::Pose3d &_pose,
    const std::string &_propertyStr)
{
  std::string prop = common::trimmed(_propertyStr);
  if (prop == "x")
    return _pose.Pos().X();
  else if (prop == "y")
    return _pose.Pos().Y();
  else if (prop == "z")
    return _pose.Pos().Z();
  else if (prop == "roll")
    return _pose.Rot().Euler().X();
  else if (prop == "pitch")
    return _pose.Rot().Euler().Y();
  else if (prop == "yaw")
    return _pose.Rot().Euler().Z();
  else
    gzerr << "Unable to get pose value for string[" << prop << "]\n";

  return std::nullopt;
}

//////////////////////////////////////////////////
void Trigger::RegisterFunction(const std::string &_name,
    std::function<bool(const std::string &)> &_func)
{
  this->functions[_name] = _func;
}

//////////////////////////////////////////////////
std::optional<bool> Trigger::RunFunction(const std::string &_name,
    const std::string &_param)
{
  if (this->functions.find(_name) != this->functions.end())
    return this->functions[_name](_param);
  gzerr << "Trigger[" << this->Name() << "] does not have function["
    << _name << "]\n";
  return std::nullopt;
}

//////////////////////////////////////////////////
void Trigger::Stop()
{
  this->processManager.Stop();
}

//////////////////////////////////////////////////
void Trigger::Reset()
{
  this->result = std::nullopt;
  this->triggered = false;
  this->ResetImpl();
}

//////////////////////////////////////////////////
void Trigger::SetTriggered(bool _triggered)
{
  this->triggered = _triggered;
}

//////////////////////////////////////////////////
bool Trigger::Triggered() const
{
  return this->triggered;
}
