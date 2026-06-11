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
#ifndef GZ_TEST_UTILS_HH_
#define GZ_TEST_UTILS_HH_

#include <yaml-cpp/yaml.h>
#include <gz/math/Vector3.hh>
#include <gz/math/Pose3.hh>

#include "gz/test/config.hh"

namespace gz
{
  namespace test
  {
    // Inline bracket to help doxygen filtering.
    inline namespace GZ_TEST_VERSION_NAMESPACE {
      enum class TimeType
      {
        // Simulation time trigger type
        SIM,
        // Real time trigger type
        REAL
      };

      math::Vector3d yamlParseVector3d(const YAML::Node &_node);
      math::Pose3d yamlParsePose3d(const YAML::Node &_node);

      bool runExecutablesAsBash(const std::vector<std::string> &_cmds);
      bool runExecutableAsBash(const std::string &_cmd);
      bool runExecutable(const std::string &_cmd);
      bool runExecutable(const std::vector<std::string> &_cmd);

      inline std::pair<int64_t, int64_t> timePointToSecNsec(
        const std::chrono::system_clock::time_point &_time)
      {
        auto now_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
            _time.time_since_epoch());
        auto now_s = std::chrono::duration_cast<std::chrono::seconds>(
            _time.time_since_epoch());
        int64_t seconds = now_s.count();
        int64_t nanoseconds = std::chrono::duration_cast
          <std::chrono::nanoseconds>(now_ns - now_s).count();
        return {seconds, nanoseconds};
      }

    }
  }
}

#endif
