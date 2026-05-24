# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import platform
import sys

import carb
import omni

# Bridge constants
BRIDGE_NAME = "isaacsim.ros2.bridge"
BRIDGE_PREFIX = "ROS2"

# Supported Ubuntu to ROS distribution mapping
SUPPORTED_ROS_DISTROS = {
    "22": "humble",  # Ubuntu 22.04 LTS -> ROS 2 Humble
    "24": "jazzy",  # Ubuntu 24.04 LTS -> ROS 2 Jazzy
}


def get_ubuntu_version():
    """Detect Ubuntu version and return the appropriate ROS distribution.

    Returns:
        str: 'humble' for Ubuntu 22.x, 'jazzy' for Ubuntu 24.x, None for other versions.
    """
    # Check if we're on Linux using sys.platform
    if not sys.platform.startswith("linux"):
        return None

    # Get Ubuntu version using platform.freedesktop_os_release().get("VERSION_ID")
    os_release = platform.freedesktop_os_release()
    version = os_release.get("VERSION_ID")
    major_version = version.split(".")[0]

    # Use the supported distros dictionary to get the ROS distribution
    ros_distro = SUPPORTED_ROS_DISTROS.get(major_version)
    if ros_distro:
        return ros_distro
    else:
        carb.log_error(f"Ubuntu version {version} is not supported for automatic ROS distribution selection")
        return None


def setup_ros2_environment(extension_path, ros_distro):
    """Set up ROS 2 environment variables and paths if required.

    Args:
        extension_path: Path to the extension directory.
        ros_distro: ROS distribution name (e.g., 'humble', 'jazzy').
    """
    if sys.platform == "win32":
        if os.environ.get("PATH"):
            os.environ["PATH"] = os.environ.get("PATH") + ";" + extension_path + f"/{ros_distro}/lib"
        else:
            os.environ["PATH"] = extension_path + f"/{ros_distro}/lib"
            os.environ["RMW_IMPLEMENTATION"] = "rmw_fastrtps_cpp"

    # For linux, manually setting up environment variables are not necessary as they are expected to be setup already in the terminal.


def print_environment_setup_instructions(extension_path, ros_distro):
    """Print instructions for setting up ROS 2 environment variables.

    Args:
        extension_path: Path to the extension directory.
        ros_distro: ROS distribution name (e.g., 'humble', 'jazzy').
    """
    if sys.platform == "linux":
        omni.kit.app.get_app().print_and_log(
            f"To use the internal libraries included with the extension please set the following environment variables to use with FastDDS (default) or CycloneDDS before starting Isaac Sim:\n\n"
            f"FastDDS (default):\n"
            f"export ROS_DISTRO={ros_distro}\n"
            f"export RMW_IMPLEMENTATION=rmw_fastrtps_cpp\n"
            f"export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{extension_path}/{ros_distro}/lib\n\n"
            f"OR\n\n"
            f"CycloneDDS:\n"
            f"export ROS_DISTRO={ros_distro}\n"
            f"export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp\n"
            f"export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{extension_path}/{ros_distro}/lib\n\n"
        )
    else:
        omni.kit.app.get_app().print_and_log(
            f"To use the internal libraries included with the extension, please set the environment variables using one of the following methods before starting Isaac Sim:\n\n"
            f"Command Prompt (CMD):\n"
            f"set ROS_DISTRO={ros_distro}\n"
            f"set RMW_IMPLEMENTATION=rmw_fastrtps_cpp\n"
            f"set PATH=%PATH%;{extension_path}/{ros_distro}/lib\n\n"
            f"PowerShell:\n"
            f'$env:ROS_DISTRO = "{ros_distro}"\n'
            f'$env:RMW_IMPLEMENTATION = "rmw_fastrtps_cpp"\n'
            f'$env:PATH = "$env:PATH;{extension_path}/{ros_distro}/lib"\n\n'
        )
