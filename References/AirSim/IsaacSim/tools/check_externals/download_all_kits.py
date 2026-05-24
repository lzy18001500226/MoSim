# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import glob
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

import packmanapi

PLATFORM_TARGETS = ["windows-x86_64", "linux-x86_64", "linux-aarch64"]


def match_platform(value):
    """Match a platform string to the closest PLATFORM_TARGET.

    For example: 'manylinux_2_35_x86_64' -> 'linux-x86_64'
    """
    # Look for direct matches first
    if value in PLATFORM_TARGETS:
        return value

    # Look for architecture matches
    if "x86_64" in value:
        if "windows" in value.lower():
            return "windows-x86_64"
        if "linux" in value.lower() or "manylinux" in value.lower():
            return "linux-x86_64"
    elif "arch64" in value:
        return "linux-aarch64"

    return None


def get_package_combinations(xml_path, platform_filter=None):
    """Parse XML and return list of valid package combinations.

    Args:
        xml_path: Path to the XML file to parse
        platform_filter: String to filter out platforms (e.g., 'linux' will skip all linux platforms)

    Returns:
        tuple: (package_name, full_version, list of valid combination dictionaries)
    """
    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find the package element and get name, version, and platforms
    package = root.find(".//package")
    package_name = package.get("name")
    full_version = package.get("version")
    platforms = package.get("platforms").split()

    # Filter platforms if requested
    if platform_filter:
        original_count = len(platforms)
        platforms = [p for p in platforms if platform_filter.lower() not in p.lower()]
        if len(platforms) < original_count:
            print(f"Filtered out {original_count - len(platforms)} platforms containing '{platform_filter}'")

    print("Supported platforms:", platforms)

    # Find all ${variable} patterns in the version string
    var_pattern = re.compile(r"\${([^}]+)}")
    variables = var_pattern.finditer(full_version)

    # Get the base pattern by replacing variables with capture groups
    pattern_string = full_version
    var_names = []
    for match in variables:
        var_name = match.group(1)
        var_names.append(var_name)
        pattern_string = pattern_string.replace(match.group(0), f"([^.]+)")

    # Create regex pattern that matches from the base version onwards
    base_version = full_version.split("${")[0]
    pattern_string = re.escape(base_version) + pattern_string[len(base_version) :]
    pattern = re.compile(pattern_string)

    print("Discerned variable names:", var_names)

    # Get list of available packages
    rtnval = packmanapi.list_files(f"{package_name}@{base_version}")
    packages = rtnval["packman:cloudfront"].keys()
    print(f"Found {len(packages)} available packages")

    # Extract variable values and keep track of valid combinations
    variables = defaultdict(set)
    valid_combinations = []
    for package in packages:
        # Remove the .zip extension and get just the version part
        package = package.removesuffix(".zip")
        version_part = package.split("@")[1]

        # Try to match the pattern
        match = pattern.match(version_part)
        if match:
            # Create a combination dictionary
            combination = {}
            skip_combination = False

            # Add each captured group to its corresponding variable
            for var_name, value in zip(var_names, match.groups()):
                # Check if this value should be filtered
                if platform_filter and "platform" in var_name.lower():
                    if platform_filter.lower() in value.lower():
                        skip_combination = True
                        break

                variables[var_name].add(value)
                combination[var_name] = value
                # If this looks like a platform variable, try to match it
                if "platform" in var_name.lower():
                    if platform_target := match_platform(value):
                        combination["platform_target"] = platform_target
                        # Find matching platform from XML platforms list
                        for plat in platforms:
                            if match_platform(plat) == platform_target:
                                combination["platform"] = plat
                                break

            if not skip_combination:
                valid_combinations.append(combination)

    print("\nDiscerned variable values:")
    for combo in valid_combinations:
        # Reconstruct the package path
        version = full_version
        for var_name, value in combo.items():
            if var_name not in ["platform_target", "platform"]:  # Skip our added fields
                version = version.replace(f"${{{var_name}}}", value)
        package_path = f"{package_name}@{version}.zip"
        print(f"  {combo} -> {package_path}")

    return package_name, full_version, valid_combinations


def download_combinations(xml_path, combinations):
    """Download all valid package combinations."""
    print("\nDownloading valid combinations:")
    for combo in combinations:
        print(f"Pulling with tokens {combo}")
        try:
            packmanapi.pull(
                project_path=xml_path, platform=combo.get("platform"), tokens=combo  # Use the matched platform from XML
            )
        except Exception as e:
            print(f"  Failed to pull: {e}")


def main():
    """Main entry point that processes all XML files."""
    parser = argparse.ArgumentParser(description="Download all packman kit dependencies.")
    parser.add_argument(
        "--skip-platform", "-s", help="Skip platforms containing this string (e.g., 'linux' or 'aarch64')"
    )
    args = parser.parse_args()

    # First process the main kit SDK
    xml_path = "./deps/kit-sdk.packman.xml"
    package_name, full_version, combinations = get_package_combinations(xml_path, args.skip_platform)
    download_combinations(xml_path, combinations)

    # Then process all other XML files
    print("\nProcessing additional XML files...")
    for xml_file in glob.glob("./deps/*.packman.xml"):
        if xml_file == xml_path:  # Skip the kit SDK we already processed
            continue

        print(f"\nProcessing {xml_file}")
        try:
            download_combinations(xml_file, combinations)
        except Exception as e:
            print(f"Failed to process {xml_file}: {e}")

    print("Finished downloading all kits")
    print("Combinations: ", combinations)


if __name__ == "__main__":
    main()
