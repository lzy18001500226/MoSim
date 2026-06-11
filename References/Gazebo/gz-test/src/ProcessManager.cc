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
#include <csignal> // NOLINT(*)
#include <fcntl.h>
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
#include <signal.h>

#include <filesystem>
#include <condition_variable>
#include <ctime>
#include <limits>
#include <list>
#include <mutex>
#include <numeric>
#include <queue>
#include <random>
#include <string>
#include <thread>
#include <unordered_set>
#include <utility>
#include <vector>

#include <gz/common/Console.hh>
#include <gz/common/Filesystem.hh>
#include <gz/common/TempDirectory.hh>

#include "ProcessManager.hh"
#include "vendor/backward.hpp"

using namespace gz::test;
using namespace std::chrono_literals;

#ifdef _WIN32
// Returns the last Win32 error, in string format. Returns an empty string if
// there is no error.
std::string GetLastErrorAsString()
{
  // Get the error message ID, if any.
  DWORD errorMessageID = ::GetLastError();
  if(errorMessageID == 0) {
    // No error message has been recorded
    return std::string();
  }

  LPSTR messageBuffer = nullptr;

  // Ask Win32 to give us the string version of that message ID.
  // The parameters we pass in, tell Win32 to create the buffer that holds the
  // message for us (because we don't yet know how long the message string.
  // will be).
  size_t size = FormatMessageA(
    FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |
    FORMAT_MESSAGE_IGNORE_INSERTS,
    NULL,
    errorMessageID,
    MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
    (LPSTR)&messageBuffer,
    0,
    NULL);

  // Copy the error message into a std::string.
  std::string message(messageBuffer, size);

  // Free the Win32's string's buffer.
  LocalFree(messageBuffer);

  return message;
}
#endif

class Executable
{
  /// \brief Default constructor
  public: Executable() = default;

  /// \brief Constructs a executable object with a name, process id,
  // /command, and other options.
  /// \param[in] _name Name of the executable. This is used for internal
  /// book keeping, it is not (necessarily) the name of the executable that
  /// will be run.
  /// \param[in] _pid The pid in which the executable is run.
  /// \param[in] _cmd The command and arguments that specify how to run the
  /// executable.
  /// \param[in] _autoRestart True if the executable should restart when it
  /// is is killed.
  /// \param[in] _envs Environment variables to set.
#ifndef _WIN32
  public: Executable(const std::string &_name, const pid_t _pid,
            const std::vector<std::string> &_cmd,
            const std::list<std::string> &_envs)
          : name(_name), pid(_pid), command(_cmd), envs(_envs)
          {}
#else
  public: Executable(const std::string &_name, const HANDLE _pi,
            const std::vector<std::string> &_cmd,
            const std::list<std::string> &_envs)
          : name(_name), pi(_pi), command(_cmd), envs(_envs)
          {}
#endif
  /// \brief Name of the executable
  public: std::string name = "";

  /// \brief Process id in which the executable is run.
#ifndef _WIN32
  public: pid_t pid = -1;
#else
  public: HANDLE pi;
#endif

  /// \brief The command to run.
  public: std::vector<std::string> command;

  /// \brief True will cause the command to restart on kill
  public: bool autoRestart = false;

  /// \brief Environment variables.
  public: std::list<std::string> envs;
};

/// \brief Private data variables for the Gazebo class.
class gz::test::ProcessManagerPrivate
{
  /// \brief Constructor.
  public: ProcessManagerPrivate();

  /// \brief Handle SIG_CHILD
  /// \param[in] _sig The signal
  public: static void OnSigChild(int _sig);

  /// \brief Set environment variables.
  /// \param[in] _envs List of environment variable name,value pairs.
  public: void SetEnvs(const std::list<std::string> &_envs);

  /// \brief A list of children that were stopped
#ifndef _WIN32
  public: std::queue<pid_t> stoppedChildren;
#else
  public: std::queue<HANDLE> stoppedChildren;
#endif

  /// \brief A list of executables that are running, or have been run.
  public: std::list<Executable> executables;

  /// \brief Mutex to protect the executables list.
  public: std::mutex executablesMutex;

  /// \brief True indicates that this process is the main process.
  public: bool master = false;

  /// \brief Backward signal handler
  public: std::unique_ptr<backward::SignalHandling> backward = nullptr;

  /// \brief Top level environment variables.
  public: std::list<std::string> envs;

  /// \brief Pointer to myself. This is used in the signal handlers.
  /// A raw pointer is acceptable here since it is used only internally.
  public: static ProcessManagerPrivate *myself;
};

// Init the static pointer.
ProcessManagerPrivate *ProcessManagerPrivate::myself = nullptr;

/////////////////////////////////////////////////
ProcessManager::ProcessManager()
  :dataPtr(new ProcessManagerPrivate())
{
  this->dataPtr->myself = this->dataPtr.get();
}

/////////////////////////////////////////////////
ProcessManager::~ProcessManager()
{
  this->Stop();
}

/////////////////////////////////////////////////
bool ProcessManager::RunExecutablesAsBash(const std::vector<std::string> &_cmds)
{
  if (_cmds.empty())
    return true;

  std::string cmd = std::accumulate(
      std::next(_cmds.begin()), _cmds.end(), _cmds[0],
      [](std::string _ss, std::string _s)
      {
        return  _ss + ";" + _s;
      });

  return this->RunExecutableAsBash(cmd);
}

/////////////////////////////////////////////////
bool ProcessManager::RunExecutableAsBash(const std::string &_cmd)
{
  common::TempDirectory dir("before-script", "gz-test", false);
  std::string filename = common::joinPaths(dir.Path(), "script.bash");
  std::ofstream script(filename, std::ofstream::out);
  std::string scriptHeader = R"header(#!/bin/bash

list_descendants ()
{
  local children=$(ps -o pid= --ppid "$1")

  for pid in $children
  do
    list_descendants "$pid"
  done

  echo "$children"
}

function onSig {

  kill $(list_descendants $$) 2>/dev/null

  # Kill self
  pkill $$
}

trap onSig INT

# This function holds the script commands.
function userScript {
)header";

  std::string scriptFooter = R"footer(
}
# Run the script in the background so that we are able to trap signals.
userScript >/tmp/stdout.log 2>/tmp/stderr.log &
wait
)footer";

  script << scriptHeader << _cmd << scriptFooter;
  script.close();

  std::filesystem::permissions(filename, std::filesystem::perms::owner_all);
  this->RunExecutable(filename, {filename}, {});
  return true;
}


/////////////////////////////////////////////////
bool ProcessManager::RunExecutable(const std::string &_name,
    const std::vector<std::string> &_cmd,
    const std::list<std::string> &_envs)
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

  this->dataPtr->SetEnvs(_envs);

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

  pDataArray->stoppedChildSem = this->dataPtr->stoppedChildSem;

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
    std::lock_guard<std::mutex> mutex(this->dataPtr->executablesMutex);
    this->dataPtr->master = true;

    // Store the PID in the parent process.
    this->dataPtr->executables.push_back(Executable(
          _name, thread, _cmd, _autoRestart, _envs));
  }
#else
  // Fork a process for the command
  pid_t pid = fork();

  // If parent process...
  if (pid)
  {
    gzdbg << "Forked a process for [" << _name << "] command["
      << std::accumulate(std::next(_cmd.begin()), _cmd.end(), _cmd[0],
          [](std::string _ss, std::string _s)
          { return  _ss + " " + _s; }) << "]\n"
      << std::flush;

    std::lock_guard<std::mutex> mutex(this->dataPtr->executablesMutex);
    this->dataPtr->master = true;
    // Store the PID in the parent process.
    this->dataPtr->executables.push_back(Executable(_name, pid, _cmd, _envs));
  }
  // Else child process...
  else
  {
    // A child is not the master
    this->dataPtr->master = false;

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

    this->dataPtr->SetEnvs(_envs);

    // Run the command, replacing the current process image
    if (execvp(cstrings[0], &cstrings[0]) < 0)
    {
      gzerr << "Unable to run command["
        << std::accumulate(
            std::next(_cmd.begin()), _cmd.end(), _cmd[0],
            [](std::string _ss, std::string _s)
            {
              return  _ss + " " + _s;
            }) << "]\n";
      return false;
    }
  }
#endif
  return true;
}

/////////////////////////////////////////////////
void ProcessManager::Stop()
{
  std::lock_guard<std::mutex> mutex(this->dataPtr->executablesMutex);

#ifndef _WIN32
  // Remove the sigchld signal handler
  signal(SIGCHLD, nullptr);
#endif

  // Create a vector of monitor threads that wait for each process to stop.
  std::vector<std::thread> monitors;
  for (const Executable &exec : this->dataPtr->executables)
    monitors.push_back(std::thread([&] {
#ifndef _WIN32
      waitpid(exec.pid, nullptr, 0);
#else
      WaitForSingleObject(exec.pi, INFINITE);
      int retVal = ReleaseSemaphore(myself->stoppedChildSem, 1, nullptr);
      if (retVal != 0)
      {
        gzerr << "Error Releasing Semaphore: "
               << GetLastErrorAsString() << std::endl;
      }
#endif
    }));

  // Shutdown the processes
  for (const Executable &exec : this->dataPtr->executables)
  {
    gzdbg << "Killing the process[" << exec.name
#ifndef _WIN32
      << "] with PID[" << exec.pid << "]\n";
    kill(exec.pid, SIGINT);
#else
  << "]\n";
#endif
  }

  gzdbg << "Waiting for each process to end\n";

  // Wait for all the monitors to stop
  for (std::thread &m : monitors)
    m.join();
}

/////////////////////////////////////////////////
ProcessManagerPrivate::ProcessManagerPrivate()
{
#ifndef _WIN32
  // Register a signal handler to capture child process death events.
  if (signal(SIGCHLD, ProcessManagerPrivate::OnSigChild) == SIG_ERR)
    gzerr << "signal(2) failed while setting up for SIGCHLD" << std::endl;

  // Register backward signal handler for other signals
  std::vector<int> signals =
  {
    SIGABRT,    // Abort signal from abort(3)
    SIGBUS,     // Bus error (bad memory access)
    SIGFPE,     // Floating point exception
    SIGILL,     // Illegal Instruction
    SIGIOT,     // IOT trap. A synonym for SIGABRT
    // SIGQUIT, // Quit from keyboard
    SIGSEGV,    // Invalid memory reference
    SIGSYS,     // Bad argument to routine (SVr4)
    SIGTRAP,    // Trace/breakpoint trap
    SIGXCPU,    // CPU time limit exceeded (4.2BSD)
    SIGXFSZ,    // File size limit exceeded (4.2BSD)
  };

  this->backward = std::make_unique<backward::SignalHandling>(signals);
#else

#endif

}

/////////////////////////////////////////////////
void ProcessManagerPrivate::OnSigChild(int _sig)
{
  // Retreive the stopped child's PID, append, and signal the consumer.
#ifndef _WIN32
  // This is a signal handler, so be careful not to do any operations
  // that you are not allowed to do.
  // Ref: http://man7.org/linux/man-pages/man7/signal-safety.7.html
  (void) _sig;  // Commenting _sig above confuses codecheck
  pid_t p;
  int status;

  if ((p = waitpid(-1, &status, WNOHANG)) != -1)
  {
    myself->stoppedChildren.push(p);
  }
#endif
}

//////////////////////////////////////////////////
void ProcessManagerPrivate::SetEnvs(const std::list<std::string> &_envs)
{
  for (const std::string &env : _envs)
  {
    #ifdef _WIN32
      _putenv_s(const_cast<char*>(env.c_str()), "");
    #else
      putenv(const_cast<char*>(env.c_str()));
    #endif
  }
}
