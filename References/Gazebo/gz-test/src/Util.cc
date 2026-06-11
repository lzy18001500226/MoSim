/*
 * Copyright 2022 Open Source Robotics Foundation
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
#include <sys/types.h>
#include <unistd.h>
#include <filesystem>
#include <numeric>

#include <gz/common/Filesystem.hh>
#include <gz/common/TempDirectory.hh>
#include <gz/common/Console.hh>
#include <gz/math/Quaternion.hh>
#include "Util.hh"

namespace gz
{
namespace test
{
// Inline bracket to help doxygen filtering.
inline namespace GZ_TEST_VERSION_NAMESPACE {

//////////////////////////////////////////////////
math::Vector3d yamlParseVector3d(const YAML::Node &_node)
{
  math::Vector3d result;
  if (_node["x"])
    result.X(_node["x"].as<double>());
  if (_node["y"])
    result.Y(_node["y"].as<double>());
  if (_node["z"])
    result.Z(_node["z"].as<double>());

  return result;
}

//////////////////////////////////////////////////
math::Pose3d yamlParsePose3d(const YAML::Node &_node)
{
  math::Vector3d rpy;

  if (_node["roll"])
    rpy.X(_node["roll"].as<double>());
  if (_node["pitch"])
    rpy.Y(_node["pitch"].as<double>());
  if (_node["yaw"])
    rpy.Z(_node["yaw"].as<double>());

  return math::Pose3d(yamlParseVector3d(_node), math::Quaterniond(rpy));
}

bool runExecutablesAsBash(const std::vector<std::string> &_cmds)
{
  std::string cmd = std::accumulate(
      std::next(_cmds.begin()), _cmds.end(), _cmds[0],
      [](std::string _ss, std::string _s)
      {
        return  _ss + ";" + _s;
      });

  return runExecutableAsBash(cmd);
}

bool runExecutableAsBash(const std::string &_cmd)
{
  common::TempDirectory dir("before-script", "gz-test", false);
  std::string filename = common::joinPaths(dir.Path(), "script.bash");
  std::ofstream script(filename, std::ofstream::out);
  script << "#!/bin/bash\n";
  script << _cmd << std::endl;
  script.close();

  std::filesystem::permissions(filename, std::filesystem::perms::owner_all);
  runExecutable(filename);
  return true;
}

//////////////////////////////////////////////////
bool runExecutable(const std::string &_cmd)
{
  return runExecutable(common::split(_cmd, " "));
}

//////////////////////////////////////////////////
bool runExecutable(const std::vector<std::string> &_cmd)
{
  // Check for empty
  if (_cmd.empty())
  {
    gzerr << "Empty command.\n";
    return false;
  }

#ifdef _WIN32
  typedef struct MyData {
      std::vector<std::string> _cmd;
      HANDLE stoppedChildSem;
  } MYDATA, *PMYDATA;


  PMYDATA pDataArray = (PMYDATA) HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY,
                sizeof(MYDATA));
  if (pDataArray == nullptr)
  {
    gzerr << "allocation fails " << GetLastErrorAsString() << '\n';
    return false;
  }

  for (auto & cmd : _cmd){
    pDataArray->_cmd.push_back(cmd);
  }

  pDataArray->stoppedChildSem = this->stoppedChildSem;

  auto dontThreadOnMe = [](LPVOID lpParam) -> DWORD {
    PMYDATA pDataArray;
    pDataArray = (PMYDATA)lpParam;

    // Create a vector of char* in the child process
    std::vector<char*> cstrings;
    cstrings.push_back("C:\\WINDOWS\\SYSTEM32\\CMD.EXE");
    cstrings.push_back("cmd.exe ");
    cstrings.push_back("/c");
    for (const std::string &part : pDataArray->_cmd)
    {
      cstrings.push_back(const_cast<char *>(part.c_str()));
    }

    // Add the nullptr termination.
    cstrings.push_back(nullptr);

    // Run the command, replacing the current process image
    if (_spawnv(_P_WAIT , cstrings[0], &cstrings[0]) < 0)
    {
      gzerr << "Unable to run command["
        << std::accumulate(
            pDataArray->_cmd.begin(),
            pDataArray->_cmd.end(),
            std::string(""))
        << "] " << GetLastErrorAsString() << "\n";
      return -1;
    }

    if (!ReleaseSemaphore(pDataArray->stoppedChildSem, 1, nullptr))
    {
      gzerr << "Error Releasing Semaphore "
             << GetLastErrorAsString() << std::endl;
    }

    if(pDataArray != NULL)
    {
      HeapFree(GetProcessHeap(), 0, pDataArray);
      pDataArray = NULL;    // Ensure address is not reused.
    }

    return 0;
  };

  auto thread = CreateThread(
    nullptr, 0, dontThreadOnMe, pDataArray, 0, nullptr);

  if (thread == nullptr) {
    gzerr << "Error creating thread on Windows "
           << GetLastErrorAsString() << '\n';
  }
  else
  {
    // std::lock_guard<std::mutex> mutex(this->executablesMutex);

    // Store the PID in the parent process.
    // this->executables.push_back(Executable(thread, _cmd));
  }
#else
  // Fork a process for the command
  pid_t pid = fork();

  // If parent process...
  if (pid)
  {
    igndbg << "Forked a process for command["
      << std::accumulate(_cmd.begin(), _cmd.end(), std::string("")) << "]\n"
      << std::flush;

    // std::lock_guard<std::mutex> mutex(this->executablesMutex);
    // Store the PID in the parent process.
    // this->executables.push_back(Executable(pid, _cmd));
  }
  // Else child process...
  else
  {
    // A child is not the master
    // this->master = false;

    // Create a vector of char* in the child process
    std::vector<char*> cstrings;
    for (const std::string &part : _cmd)
    {
      cstrings.push_back(const_cast<char *>(part.c_str()));
    }

    // Add the nullptr termination.
    cstrings.push_back(nullptr);

    // Remove from foreground process group.
    setpgid(0, 0);

    // Run the command, replacing the current process image
    if (execvp(cstrings[0], &cstrings[0]) < 0)
    {
      gzerr << "Unable to run command["
             << std::accumulate(
                _cmd.begin(),
                _cmd.end(),
                std::string(" ")) << "]\n";
      return false;
    }
  }
#endif
  return true;
}
}
}
}
