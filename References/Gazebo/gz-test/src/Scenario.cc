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
#include <regex>

#include <sdf/Model.hh>
#include <sdf/Root.hh>
#include <sdf/World.hh>

#include <gz/common/SignalHandler.hh>
#include <gz/fuel_tools/Interface.hh>
#include <gz/msgs/stringmsg.pb.h>
#include <gz/sim/Util.hh>
#include <gz/sim/Server.hh>
#include <gz/math/Stopwatch.hh>

#include <gz/transport/Node.hh>

#include "msgs/scenario.pb.h"
#include "ProcessManager.hh"
#include "Scenario.hh"
#include "Test.hh"
#include "TimeTrigger.hh"
#include "Util.hh"

using namespace gz;
using namespace test;

class Scenario::Implementation
{
  public: Implementation()
          {
            this->CreateSigHandler();
          }

  public: Implementation(const Scenario::Implementation &_impl)
          {
            *this = _impl;
            this->CreateSigHandler();
          }

  public: Implementation &operator=(const Implementation &_impl)
          {
            this->name = _impl.name;
            this->description = _impl.description;
            this->worldFilename = _impl.worldFilename;
            this->models = _impl.models;
            this->tests = _impl.tests;
            this->serverConfig = _impl.serverConfig;

            this->CreateSigHandler();
            return *this;
          }
  private: void CreateSigHandler()
           {
             // Create the signal handler
             if (!this->sigHandler.Initialized())
             {
               gzerr << "signal(2) failed while setting up for SIGINT"
                 << std::endl;
             }
             this->sigHandler.AddCallback(
                 std::bind(&Implementation::OnSigIntTerm, this,
                   std::placeholders::_1));
           }

  /// \brief Load the scenario configuration YAML section.
  /// \param[in] _config The YAML node holding the configuration data.
  public: void LoadConfiguration(const YAML::Node &_config);

  public: void OnSigIntTerm(int _sig);

  public: std::string name{""};
  public: std::string description{""};
  public: std::string worldFilename{""};
  public: std::vector<sdf::Model> models;
  public: std::vector<std::shared_ptr<Test>> tests;
  public: sim::ServerConfig serverConfig;

  public: std::string baseLogPath{""};
  public: bool recordSimState = true;

  /// \brief Gazebo Transport node.
  public: transport::Node node;

  public: transport::Node::Publisher statusPub;

  public: std::vector<std::string> beforeScript;
  public: ProcessManager processManager;

  public: common::SignalHandler sigHandler;
  public: std::unique_ptr<sim::Server> server{nullptr};
  public: bool run{false};

  public: class Param
          {
            public: std::string name;
            public: std::string type;
            public: std::string value;
          };

  public: typedef std::map<std::string, Param> ParameterMap;
  public: ParameterMap parameters;
  public: std::vector<ParameterMap> iterations;
  public: size_t iteration{0};

  public: std::vector<std::string> testYaml;
};

/////////////////////////////////////////////////
void Scenario::Implementation::LoadConfiguration(const YAML::Node &_config)
{
  // Get the world file name
  if (_config["world"])
    this->worldFilename = _config["world"].as<std::string>();

  if (_config["before_script"])
  {
    for (YAML::const_iterator it = _config["before_script"].begin();
        it!=_config["before_script"].end(); ++it)
    {
      beforeScript.push_back(it->as<std::string>());
    }
  }

  // Load all the models, if any
  if (_config["models"])
  {
    for (YAML::const_iterator it = _config["models"].begin();
        it!=_config["models"].end(); ++it)
    {
      sdf::Model model;

      // Get the model's URI
      if ((*it)["uri"])
      {
        std::string uri = (*it)["uri"].as<std::string>();
        std::string modelPath = fuel_tools::fetchResource(uri);
        std::string modelSdfFile = fuel_tools::sdfFromPath(modelPath);

        sdf::Root root;
        sdf::Errors errors = root.Load(modelSdfFile);

        for (sdf::Error &err : errors)
          gzerr << err.Message() << std::endl;

        model = *(root.Model());
        model.SetUri(uri);
      }
      else
      {
        gzerr << "model missing URI, skipping\n";
        continue;
      }

      // Get the model's name
      if ((*it)["name"])
      {
        model.SetName((*it)["name"].as<std::string>());
      }
      else
      {
        gzerr << "model missing name, skipping\n";
        continue;
      }

      // Get the model's pose
      if ((*it)["pose"])
        model.SetRawPose(yamlParsePose3d((*it)["pose"]));

      this->models.push_back(model);
    }
  }

  // Read log record configuration, if present.
  if (_config["record"])
  {
    YAML::Node recordNode = _config["record"];
    if (recordNode["sim-state"])
      this->recordSimState = recordNode["sim-state"].as<bool>();
  }

  if (_config["parameters"])
  {
    for (YAML::const_iterator it = _config["parameters"].begin();
         it != _config["parameters"].end(); ++it)
    {
      Implementation::Param param;

      param.name = it->first.as<std::string>();
      param.type = it->second["type"].as<std::string>();
      param.value = it->second["default"].as<std::string>();

      this->parameters[param.name] = param;
    }
  }

  if (_config["iterations"])
  {
    for (YAML::const_iterator it = _config["iterations"].begin();
         it != _config["iterations"].end(); ++it)
    {
      ParameterMap iterationParameters;
      for (YAML::const_iterator mapIt = it->begin();
           mapIt != it->end(); ++mapIt)
      {
        Implementation::Param param;
        param.name = mapIt->first.as<std::string>();
        param.value = mapIt->second.as<std::string>();

        iterationParameters[param.name] = param;
      }

      this->iterations.push_back(iterationParameters);
    }
  }
  else
  {
    // Add an empty iteration.
    this->iterations.push_back({});
  }
}

/////////////////////////////////////////////////
Scenario::Scenario()
  : dataPtr(utils::MakeImpl<Implementation>())
{
}

/////////////////////////////////////////////////
bool Scenario::Load(const std::string &_filename,
    const std::string &_outputPath)
{
  this->dataPtr->baseLogPath = _outputPath;
  if (!common::isDirectory(this->dataPtr->baseLogPath))
    common::createDirectory(this->dataPtr->baseLogPath);

  // Try to parse the scenario file.
  YAML::Node config;
  try
  {
    config = YAML::LoadFile(_filename);
  }
  catch (YAML::ParserException &_e)
  {
    gzerr << "Invalid scenario format. Error at line "
      << _e.mark.line + 1 << ", column " << _e.mark.column + 1 << ": "
      << _e.msg << std::endl;
    return false;
  }

  // The scenario name
  if (config["name"])
    this->dataPtr->name = config["name"].as<std::string>();

  // The scenario description
  if (config["description"])
    this->dataPtr->description = config["description"].as<std::string>();

  // Load the configuration section of the scenario
  if (config["configuration"])
    this->dataPtr->LoadConfiguration(config["configuration"]);

  // Load the yaml strings for all the tests
  for (YAML::const_iterator it = config["tests"].begin();
       it != config["tests"].end(); ++it)
  {
    std::ostringstream stream;
    stream << *it;
    this->dataPtr->testYaml.push_back(stream.str());
  }

  std::string worldFilePath = sim::resolveSdfWorldFile(
      this->dataPtr->worldFilename);
  if (worldFilePath.empty())
  {
    gzerr << "Unable to find world file ["
      << this->dataPtr->worldFilename << "]" << std::endl;
    return false;
  }
  igndbg << "Resolved world file path[" << worldFilePath << "]\n";

  // \todo I shouldn't have to call this function. The sim::Server's
  // constructor calls this function, but it's probably not suitable when
  // Gazebo is used a library.
  sdf::setFindCallback(
      std::bind(fuel_tools::fetchResource, std::placeholders::_1));

  sdf::Root root;
  sdf::Errors errors = root.Load(worldFilePath);
  if (!errors.empty())
  {
    gzerr << "Failed to load SDF world file[" << worldFilePath << "]\n";
    for (const sdf::Error &err : errors)
      gzerr << err.Message() << std::endl;

    return false;
  }

  // Add the models to the world.
  for (sdf::Model model : this->dataPtr->models)
    root.WorldByIndex(0)->AddModel(model);

  this->dataPtr->serverConfig.SetSdfRoot(root);
  this->dataPtr->serverConfig.SetHeadlessRendering(true);

  this->dataPtr->statusPub =
    this->dataPtr->node.Advertise<msgs::StringMsg>("/test/status");

  return true;
}

//////////////////////////////////////////////////
void Scenario::Run()
{
  this->dataPtr->run = true;
  std::pair<int64_t, int64_t> timePair;

  domain::Scenario result;
  result.set_name(this->Name());
  result.set_description(this->Description());

  // Start a stop watch to record the duration of the run.
  math::Stopwatch watch;
  watch.Start();

  // Record the system start time
  timePair = timePointToSecNsec(std::chrono::system_clock::now());
  result.mutable_start_time()->set_seconds(timePair.first);
  result.mutable_start_time()->set_nanos(timePair.second);

  int scenarioTotalFailCount = 0;
  int scenarioTotalCount = 0;
  int scenarioIterationFailCount = 0;
  int scenarioIterationTotalCount = 0;

  math::Stopwatch iterationWatch, testWatch;
  // Run each iteration
  for (this->dataPtr->iteration= 0;
       this->dataPtr->iteration < this->dataPtr->iterations.size();
       ++this->dataPtr->iteration)
  {
    igndbg << "Running test iteration " << this->dataPtr->iteration << "\n";

    domain::Iteration *iterationResult = result.add_iterations();

    int iterationTestFailCount = 0;
    int iterationTestCount = 0;

    timePair = timePointToSecNsec(std::chrono::system_clock::now());
    iterationResult->mutable_start_time()->set_seconds(timePair.first);
    iterationResult->mutable_start_time()->set_nanos(timePair.second);
    iterationWatch.Start(true);

    // Create the tests.
    this->dataPtr->tests.clear();
    for (std::string yamlStr : this->dataPtr->testYaml)
    {
      for (const std::pair<const std::string, Implementation::Param> &param :
          this->dataPtr->iterations.at(this->dataPtr->iteration))
      {
        (*iterationResult->mutable_params())[param.first] =
          param.second.value;
        yamlStr = std::regex_replace(yamlStr,
            std::regex("\\$\\{\\{" + param.first +"\\}\\}"),
            param.second.value);
      }

      YAML::Node parsedNode = YAML::Load(yamlStr);

      std::shared_ptr<Test> test = std::make_shared<Test>();
      test->Load(parsedNode);
      this->dataPtr->tests.push_back(std::move(test));
    }

    // Run each test
    for (std::vector<std::shared_ptr<Test>>::iterator it =
        this->dataPtr->tests.begin();
        it != this->dataPtr->tests.end() && this->dataPtr->run; ++it)
    {
      testWatch.Start(true);

      igndbg << "Running Test[" << (*it)->Name() << "]\n";

      if (!this->dataPtr->baseLogPath.empty())
      {
        this->dataPtr->serverConfig.SetUseLogRecord(
            this->dataPtr->recordSimState);
        this->dataPtr->serverConfig.SetLogRecordPath(
            common::joinPaths(this->dataPtr->baseLogPath, (*it)->Name(),
              std::to_string(this->dataPtr->iteration)));
      }
      else
      {
        this->dataPtr->serverConfig.SetUseLogRecord(false);
      }

      domain::Test *testResult = iterationResult->add_tests();
      testResult->set_name((*it)->Name());
      timePair = timePointToSecNsec(std::chrono::system_clock::now());
      testResult->mutable_start_time()->set_seconds(timePair.first);
      testResult->mutable_start_time()->set_nanos(timePair.second);

      // HERE: Setup a correct region trigger.
      //       Capture console logs
      //       A trigger can trigger anohter trigger.
      //       Build and release docker image.
      //       Update ci-test repo so that multiple tests are triggered.
      //       Capture robot trajectory.
      //       Plot robot trajectory in browswer and show changes over time.

      bool beforeScriptSuccessful =
        this->dataPtr->processManager.RunExecutablesAsBash(
            this->dataPtr->beforeScript);

      if (beforeScriptSuccessful)
      {
        this->dataPtr->server =
          std::make_unique<sim::Server>(this->dataPtr->serverConfig);

        this->dataPtr->server->AddSystem((*it));

        // \todo I think a behavior tree, or state machine would serve us
        // better here.
        std::function<void()> stopCb = [&]() {
          this->dataPtr->server->Stop();
        };
        (*it)->SetStopCallback(stopCb);

        // \todo Support Running simulation with a simulation or
        // real time limit.
        if ((*it)->MaxDurationType() == TimeType::REAL)
          gzerr << "Real-time type not supported for time-limit\n";
        uint64_t iterations = 0;
        if ((*it)->MaxDuration() > 0s)
        {
          std::chrono::steady_clock::duration dt = 10ms;
          iterations = (*it)->MaxDuration() / dt;
        }

        this->dataPtr->server->Run(true, iterations, false);
        testWatch.Stop();

        timePair = math::durationToSecNsec(testWatch.ElapsedRunTime());
        testResult->mutable_duration()->set_seconds(timePair.first);
        testResult->mutable_duration()->set_nanos(timePair.second);

        // Fill results, and keep track of the fail count.
        if (!(*it)->FillResults(testResult))
          iterationTestFailCount++;
        iterationTestCount++;

        this->dataPtr->server.reset();
      }
    }

    iterationResult->set_failed(iterationTestFailCount > 0);
    iterationResult->set_test_fail_count(iterationTestFailCount);
    iterationResult->set_test_count(iterationTestCount);


    iterationWatch.Stop();
    timePair = math::durationToSecNsec(iterationWatch.ElapsedRunTime());
    iterationResult->mutable_duration()->set_seconds(timePair.first);
    iterationResult->mutable_duration()->set_nanos(timePair.second);

    scenarioTotalFailCount += iterationTestFailCount;
    scenarioTotalCount += iterationTestCount;

    scenarioIterationFailCount += iterationTestFailCount > 0 ? 1 : 0;
    scenarioIterationTotalCount++;
  }
  watch.Stop();

  timePair = math::durationToSecNsec(watch.ElapsedRunTime());
  result.mutable_duration()->set_seconds(timePair.first);
  result.mutable_duration()->set_nanos(timePair.second);

  result.set_test_count(scenarioTotalCount);
  result.set_test_fail_count(scenarioTotalFailCount);

  result.set_iteration_count(scenarioIterationTotalCount);
  result.set_iteration_fail_count(scenarioIterationFailCount);
  result.set_failed(scenarioTotalFailCount > 0);

  if (!this->dataPtr->baseLogPath.empty() &&
      common::isDirectory(this->dataPtr->baseLogPath))
  {
    std::string resultFilename =
      common::joinPaths(this->dataPtr->baseLogPath, "result.pbtxt");

    std::ofstream stream;
    stream.open(resultFilename, std::ofstream::out);
    stream << result.DebugString() << std::endl;
  }
  else
  {
    std::cout << result.DebugString() << std::endl;
  }

}

//////////////////////////////////////////////////
void Scenario::SendRecordingCompleteMessage()
{
  msgs::StringMsg completeMsg;
  completeMsg.set_data("recording_complete");
  this->dataPtr->statusPub.Publish(completeMsg);
}

//////////////////////////////////////////////////
void Scenario::SendFinishedMessage()
{
  msgs::StringMsg completeMsg;
  completeMsg.set_data("finished");
  this->dataPtr->statusPub.Publish(completeMsg);
}

//////////////////////////////////////////////////
std::string Scenario::Name() const
{
  return this->dataPtr->name;
}

//////////////////////////////////////////////////
void Scenario::SetName(const std::string &_name)
{
  this->dataPtr->name = _name;
}

//////////////////////////////////////////////////
std::string Scenario::Description() const
{
  return this->dataPtr->description;
}

//////////////////////////////////////////////////
void Scenario::SetDescription(const std::string &_description)
{
  this->dataPtr->description = _description;
}

//////////////////////////////////////////////////
std::string Scenario::WorldFilename() const
{
  return this->dataPtr->worldFilename;
}

//////////////////////////////////////////////////
void Scenario::SetWorldFilename(const std::string &_worldFilename)
{
  this->dataPtr->worldFilename = _worldFilename;
}

//////////////////////////////////////////////////
std::vector<sdf::Model> Scenario::Models() const
{
  return this->dataPtr->models;
}

//////////////////////////////////////////////////
void Scenario::SetModels(const std::vector<sdf::Model> &_models)
{
  this->dataPtr->models = _models;
}

//////////////////////////////////////////////////
std::vector<std::shared_ptr<Test>> Scenario::Tests() const
{
  return this->dataPtr->tests;
}

//////////////////////////////////////////////////
void Scenario::SetTests(const std::vector<std::shared_ptr<Test>> &_tests)
{
  this->dataPtr->tests = _tests;
}

//////////////////////////////////////////////////
sim::ServerConfig Scenario::ServerConfig() const
{
  return this->dataPtr->serverConfig;
}

//////////////////////////////////////////////////
void Scenario::SetServerConfig(const sim::ServerConfig &_config)
{
  this->dataPtr->serverConfig = _config;
}

//////////////////////////////////////////////////
void Scenario::Implementation::OnSigIntTerm(int)
{
  this->run = false;
  igndbg << "SigInt handler triggered\n";

  // Stop the server
  if (this->server)
    this->server->Stop();

  // Stop the tests
  for (std::shared_ptr<Test> &test : this->tests)
    test->Stop();
  this->processManager.Stop();
}
