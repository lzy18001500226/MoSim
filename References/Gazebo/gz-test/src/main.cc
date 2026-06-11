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
#include <chrono>
#include <iostream>
#include <gz/common/SignalHandler.hh>
#include <gz/common/Util.hh>
#include <gz/sim/Util.hh>
#include <gz/sim/Server.hh>
#include <gz/utils/cli/CLI.hpp>

#include "gz/test/config.hh"

#include "Scenario.hh"

using namespace gz;
using namespace test;

std::atomic<bool> kRun = true;

//////////////////////////////////////////////////
void onSigIntTerm(int)
{
  std::cout << "\n\nON SIG INT\n\n";
  kRun = false;
}

//////////////////////////////////////////////////
int main(int argc, char **argv)
{
  CLI::App app{"Test runner"};
  app.set_help_all_flag("--help-all", "Show all help");
  app.add_flag_callback("--version", [](){
      std::cout << GZ_TEST_VERSION_FULL << std::endl;
      throw CLI::Success();
  });

  std::string scenarioFilename = "";
  std::string outputPath = "";
  int verbose = 1;
  app.add_option("-s,--scenario-file",
      scenarioFilename, "Specify the scenario file")
    ->required()
    ->check(CLI::ExistingFile);

  app.add_option("-o,--output-path",
      outputPath, "Specify the ouput path");

  bool keepAlive = false;
  app.add_flag_callback("-k,--keep-alive", [&](){
      keepAlive = true;
      });

  app.add_option("-v,--verbose",
      verbose, "Verbosity level");

  CLI11_PARSE(app, argc, argv);

  // Set verbosity
  common::Console::SetVerbosity(verbose);

  // Create the signal handler
  common::SignalHandler sigHandler;
  if (!sigHandler.Initialized())
  {
    gzerr << "signal(2) failed while setting up for SIGINT" << std::endl;
    return -1;
  }
  sigHandler.AddCallback(std::bind(&onSigIntTerm, std::placeholders::_1));

  /*std::string expect = "x1-a.pose.x == 0.0";
  std::regex reg(R"(==)");
  auto expBegin = std::sregex_iterator(expect.begin(), expect.end(), reg);
  auto expEnd = std::sregex_iterator();
  for (std::sregex_iterator it = expBegin; it != expEnd; ++it)
  {
    std::smatch match = *it;
    if (it->str() == "==")
    {
      std::string prefix = it->prefix().str();
      std::string suffix = it->suffix().str();

      double pre = parseValue(prefix);
      double suf = parseValue(suffix);;
      std::cout << "Comparing[" << pre << "==" << suf << "]\n";

      if (math::equal(pre, suf))
        std::cout << "EQUAL\n";
      else
        std::cout << "NOT EQUAL\n";
    }

    //std::cout << match.prefix().str() << match.str() << match.suffix().str() << std::endl;
  }

  return 0;
  */

  // Load the scenario file.
  Scenario scenario;
  if (!scenario.Load(scenarioFilename, outputPath))
  {
    gzerr << "Failed to load the scenario file[" << scenarioFilename << "]\n";
    return -1;
  }

  // Run the tests
  if (kRun)
  {
    scenario.Run();

    // If keep alive, send done messages at 1hz
    if (keepAlive)
    {
      while (kRun)
      {
        scenario.SendRecordingCompleteMessage();
        scenario.SendFinishedMessage();
        GZ_SLEEP_S(1);
      }
    }
  }

  // On the side:
  //   1. Update documentation.
  //   2. Get bullet working
  //   3. Create alternative to smacc, tinysfm
  //   4. Unified return error codes, with hooks to state logging, and
  //   transport. Should also have boolean evaluation.
  return 0;
}
