# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import argparse
import os
import platform
from typing import Callable, Dict


def setup_repo_tool(parser: argparse.ArgumentParser, config: Dict) -> Callable:
    """Setup the repository tool for editing sysconfig files.

    Configures the argument parser and returns a callable function to run the tool.
    This tool modifies Python sysconfig files to replace hardcoded build paths
    with relative paths based on the current repository structure.

    Args:
        parser: The argument parser to configure with tool-specific options.
        config: Configuration dictionary containing tool settings.

    Returns:
        A callable function that executes the sysconfig editing operation.
    """
    parser.description = "Edit sysconfig files to replace hardcoded build paths with relative paths."
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        required=False,
        default="release",
        help="Package configuration to use. (default: %(default)s)",
    )

    def run_repo_tool(options: Dict, config: Dict) -> None:
        """Execute the sysconfig editing operation.

        Modifies the sysconfig file by appending code that replaces hardcoded
        build paths with relative paths. Only runs on non-Windows systems.

        Args:
            options: Command line options containing the config setting.
            config: Configuration dictionary with tool-specific settings.
        """
        if platform.system().lower() == "windows":
            print("On Windows this command does nothing")
            return

        tool_config = config["repo_edit_sysconfig"]
        sysconfig_path = tool_config["sysconfig_path"]
        sysconfig_path = sysconfig_path.replace("${config}", options.config)

        print(f"Processing sysconfig file: {sysconfig_path}")

        sysconfig_file = os.path.abspath(sysconfig_path)

        if not os.path.exists(sysconfig_file):
            print(f"Error: Sysconfig file not found: {sysconfig_file}")
            return

        env_replace_string = _get_env_replace_string()

        if _is_already_modified(sysconfig_file):
            print("File already contains Isaac Sim modifications, skipping")
        else:
            _append_modifications(sysconfig_file, env_replace_string)
            print("Successfully added Isaac Sim path modifications")

    return run_repo_tool


def _get_env_replace_string() -> str:
    """Get the string to append to the sysconfig file.

    Returns:
        The formatted string containing the path replacement code.
    """
    return """
# ISAAC SIM BEGIN GENERATED PART
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
for k, v in build_time_vars.items():
    if isinstance(v, str):
        build_time_vars[k] = v.replace(
            "/builds/omniverse/externals/python-build/_build/repopackageroot", 
            base_directory
        )
# ISAAC SIM END GENERATED PART"""


def _is_already_modified(sysconfig_file: str) -> bool:
    """Check if the sysconfig file has already been modified.

    Args:
        sysconfig_file: Path to the sysconfig file to check.

    Returns:
        True if the file already contains Isaac Sim modifications, False otherwise.
    """
    try:
        with open(sysconfig_file, "r") as file:
            content = file.read()
            return "# ISAAC SIM END GENERATED PART" in content
    except IOError as e:
        print(f"Error reading file {sysconfig_file}: {e}")
        return False


def _append_modifications(sysconfig_file: str, env_replace_string: str) -> None:
    """Append the path replacement code to the sysconfig file.

    Args:
        sysconfig_file: Path to the sysconfig file to modify.
        env_replace_string: The string to append to the file.
    """
    try:
        with open(sysconfig_file, "a") as file:
            file.write(env_replace_string)
    except IOError as e:
        print(f"Error writing to file {sysconfig_file}: {e}")
