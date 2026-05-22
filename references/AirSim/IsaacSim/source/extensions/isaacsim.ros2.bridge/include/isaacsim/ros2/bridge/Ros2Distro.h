// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/** @file
 * @brief ROS 2 distribution definitions and utilities
 * @details
 * This file provides enum definitions and utility functions for supported
 * ROS 2 distributions in the Isaac Sim ROS 2 bridge.
 */
#pragma once

#include <algorithm>
#include <array>
#include <cctype>
#include <optional>
#include <string>

namespace isaacsim::ros2::bridge
{

/**
 * @enum Ros2Distro
 * @brief Enumeration of supported ROS 2 distributions
 * @details
 * Defines the ROS 2 distributions that are supported by the Isaac Sim
 * ROS 2 bridge. Used for distribution-specific behavior and compatibility.
 */
enum class Ros2Distro
{
    /** @brief ROS 2 Humble Hawksbill distribution */
    eHumble,
    /** @brief ROS 2 Jazzy Jalisco distribution */
    eJazzy,
    // Add new distros here
    /** @brief Count of supported distributions, keep this last */
    eCount // Keep this last
};

namespace
{

/**
 * @struct Ros2DistroInfo
 * @brief Association between distribution name and enum value
 * @details
 * Maps string names of ROS 2 distributions to their corresponding
 * enum values for lookup and conversion purposes.
 */
struct Ros2DistroInfo
{
    /** @brief String name of the ROS 2 distribution */
    const char* name;
    /** @brief Enum value of the ROS 2 distribution */
    Ros2Distro distro;
};

/**
 * @brief Mapping between ROS 2 distribution names and enum values
 * @details
 * Constant array of mappings between distribution names and their
 * corresponding enum values for lookup operations.
 */
constexpr std::array<Ros2DistroInfo, 2> g_kDistroMapping{ { { "humble", Ros2Distro::eHumble },
                                                            { "jazzy", Ros2Distro::eJazzy } } };

/**
 * @brief Converts a string to lowercase
 * @details
 * Utility function to convert a string to lowercase for case-insensitive
 * comparison of ROS 2 distribution names.
 *
 * @param[in] input The string to convert to lowercase
 * @return std::string The lowercase version of the input string
 */
inline std::string toLower(const std::string& input)
{
    std::string result{ input };
    std::transform(result.begin(), result.end(), result.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    return result;
}

/**
 * @brief Converts a string to a Ros2Distro enum value
 * @details
 * Attempts to match a lowercase distribution name to a supported
 * ROS 2 distribution and returns the corresponding enum value if found.
 *
 * @param[in] lowerDistro The lowercase ROS 2 distribution name
 * @return std::optional<Ros2Distro> The corresponding enum value if found,
 *                                 or std::nullopt if not supported
 */
inline std::optional<Ros2Distro> stringToRos2Distro(const std::string& lowerDistro)
{
    auto it = std::find_if(g_kDistroMapping.begin(), g_kDistroMapping.end(),
                           [&lowerDistro](const auto& info) { return lowerDistro == info.name; });

    if (it != g_kDistroMapping.end())
    {
        return it->distro;
    }
    return std::nullopt;
}

} // namespace

/**
 * @brief Checks if a ROS 2 distribution is supported
 * @details
 * Determines whether a given ROS 2 distribution name is among
 * the supported distributions in the Isaac Sim ROS 2 bridge.
 *
 * @param[in] distro The name of the ROS 2 distribution to check
 * @return bool True if the distribution is supported, false otherwise
 */
inline bool isRos2DistroSupported(const std::string& distro)
{
    const std::string lowerDistro = toLower(distro);
    return stringToRos2Distro(lowerDistro).has_value();
}

} // namespace isaacsim::ros2::bridge
