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
#ifndef GZ_TEST_PROCESSMANAGER_HH_
#define GZ_TEST_PROCESSMANAGER_HH_

#include "gz/test/config.hh"

namespace gz
{
  namespace test
  {
    // Inline bracket to help doxygen filtering.
    inline namespace GZ_TEST_VERSION_NAMESPACE {
    // Forward declaration of the private data class
    class ProcessManagerPrivate;

    class ProcessManager
    {
      /// \brief Constructor
      public: ProcessManager();

      /// \brief Deonstructor
      public: ~ProcessManager();

      public: bool RunExecutablesAsBash(const std::vector<std::string> &_cmds);
      public: bool RunExecutableAsBash(const std::string &_cmd);

      /// \brief Fork a new process for a command specific by _cmd.
      /// \param[in] _name A unique name given to the command. This name is
      /// used for book keeping and control of the process.
      /// \param[in] _cmd A vector of strings where the first string is
      /// expected to be the name of the executable to run, and subsequent
      /// strings are arguments.
      /// \param[in] _envs Environment variables to set.
      /// \return True on success.
      public: bool RunExecutable(const std::string &_name,
        const std::vector<std::string> &_cmd,
        const std::list<std::string> &_envs);

      public: void Stop();

      /// \brief Private data pointer.
      // GZ_COMMON_WARN_IGNORE__DLL_INTERFACE_MISSING
      private: std::unique_ptr<ProcessManagerPrivate> dataPtr;
      // GZ_COMMON_WARN_RESUME__DLL_INTERFACE_MISSING

    };
    }
  }
}
#endif
