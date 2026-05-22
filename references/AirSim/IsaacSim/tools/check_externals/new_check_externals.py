"""Mad Science: Packman External Dependency and License Checker.

This module provides functionality to analyze packman XML files, extract
dependency information, verify their availability on remote servers, check
their public/private status, and analyze their license information.

The main workflow involves:
1. Parsing packman XML files to extract dependencies
2. Verifying dependencies exist on remote servers (cloudfront/artifactory)
3. Checking public/private status via omnipackages API
4. Finding and analyzing license files for each dependency
5. Generating CSV reports with comprehensive dependency information

Key classes:
    PullSettings: Configuration settings for packman dependency resolution
    DependencyInfo: Complete information about a packman dependency

Key functions:
    build_file_to_platform_map: Maps packman files to supported platforms
    get_dependencies: Extracts dependency info from packman XML files
    check_externals: Main function that orchestrates the entire process
    main: Command-line entry point with argument parsing
"""

import argparse
import glob
import os
from dataclasses import dataclass

import packman
import packmanapi
import requests
import tomli
from license_finder import find_license_file
from packman.schemaparser import Source
from tqdm import tqdm

PLATFORM_TO_PLATFORM_TARGET = {
    "manylinux_2_35_x86_64": "linux-x86_64",
    "manylinux_2_35_aarch64": "linux-aarch64",
    "linux-x86_64": "linux-x86_64",
    "linux-aarch64": "linux-aarch64",
    "windows-x86_64": "windows-x86_64",
}

LINUX_PAIRS = [
    ("manylinux_2_35_x86_64", "linux-x86_64"),
    ("manylinux_2_35_aarch64", "linux-aarch64"),
]

PLATFORM_TARGETS = ("linux-x86_64", "linux-aarch64", "windows-x86_64")

packman.main.set_verbosity_level(packman.main.VERBOSITY_NONE)


@dataclass
class PullSettings:
    """Settings for packman dependency resolution.

    Contains the configuration parameters used when resolving dependencies
    from packman XML files.

    Attributes:
        file: Path to the packman XML file being processed.
        config: Build configuration (e.g., 'release', 'debug').
        platform: Platform identifier (e.g., 'manylinux_2_35_x86_64').
        platform_target: Target platform for the build (e.g., 'linux-x86_64').
    """

    file: str
    config: str
    platform: str
    platform_target: str


@dataclass
class DependencyInfo:
    """Information about a packman dependency.

    Contains all relevant information about a dependency including its
    availability, licensing, and metadata.

    Attributes:
        name: Name of the dependency package.
        version: Version string of the dependency.
        platforms: List of supported platforms for this dependency.
        link_path: Relative path to the dependency installation directory.
        found: Whether the dependency was found on the remote server.
        expected_public: Whether this dependency is expected to be publicly available.
        public: Whether this dependency is actually publicly available.
        remote: Remote server where the dependency was found ('cloudfront' or 'artifactory').
        pull_settings: Configuration settings used to resolve this dependency.
        dependency_filename: Filename of the dependency package on the remote server.
        license_files: List of license file paths found for this dependency.
        license_type: Type of license for the main license file.
    """

    name: str
    version: str
    platforms: list[str]
    link_path: str
    found: bool
    expected_public: bool
    public: bool
    remote: str
    pull_settings: PullSettings
    dependency_filename: str
    license_files: list[str]
    license_type: str


def build_file_to_platform_map(files):
    """Build a mapping of packman XML files to their supported platforms.

    Analyzes each packman XML file to determine which platforms are referenced
    by parsing the file with different platform and configuration combinations.

    Args:
        files: List of packman XML file paths to analyze.

    Returns:
        Dictionary mapping file paths to lists of supported platform identifiers.

    Example:

    .. code-block:: python

        >>> files = ['deps/kit-sdk.packman.xml']
        >>> platform_map = build_file_to_platform_map(files)
        >>> platform_map['deps/kit-sdk.packman.xml']
        ['manylinux_2_35_x86_64', 'linux-x86_64']
    """
    file_to_platform_map = {}
    identical_count = 0
    for f in files:
        for kit_platform in PLATFORM_TARGETS:
            for config in ["release", "debug"]:
                test = packman.main.parse_project_file(
                    f,
                    None,
                    {
                        "config": config,
                        "platform": "",
                        "platform_target": kit_platform,
                        "platform_host": "",
                        "platform_target_abi": "",
                        "root": ".",
                        "local_path": ".",
                    },
                    "",
                )
                if f in file_to_platform_map and file_to_platform_map[f] != test.platforms_referenced:
                    file_to_platform_map[f].extend(test.platforms_referenced)
                elif f not in file_to_platform_map:
                    file_to_platform_map[f] = test.platforms_referenced
                else:
                    identical_count += 1

    return file_to_platform_map


def check_public_private_status(dependency_filename):
    """Check if a dependency is publicly available using the omnipackages API.

    Queries the NVIDIA omnipackages API to determine if a dependency
    is publicly available or private.

    Args:
        dependency_filename: The filename of the dependency package to check.

    Returns:
        bool: True if the dependency is public, False if private or if the check fails.

    Example:

    .. code-block:: python

        >>> is_public = check_public_private_status('fmt@7.0.3+nv2.7z')
        >>> is_public
        True
    """
    try:
        response = requests.get(
            f"https://omnipackages.nvidia.com/api/v1/tags/cloudfront/{dependency_filename}", timeout=10
        )
        if response.status_code == 200:
            response_json = response.json()
            if len(response_json) and response_json[0] == {"Key": "public", "Value": "true"}:
                return True
    except Exception:
        # If the API call fails for any reason, assume private
        pass
    return False


def resolve_dependency(name, version):
    """Resolve a dependency using packmanapi.

    Attempts to resolve a dependency first from cloudfront, then from artifactory
    if not found on cloudfront.

    Args:
        name: Name of the dependency package.
        version: Version string of the dependency.

    Returns:
        Tuple containing:
            - found: Boolean indicating if the dependency was found.
            - remote: String indicating the remote server ('cloudfront', 'artifactory', or None).
            - dependency_filename: String filename of the dependency package (or None).

    Example:

    .. code-block:: python

        >>> found, remote, filename = resolve_dependency('fmt', '7.0.3+nv2')
        >>> found
        True
        >>> remote
        'cloudfront'
        >>> filename
        'fmt-7.0.3+nv2-linux-x86_64.zip'
    """
    # Try cloudfront first
    resolution = packmanapi.resolve(
        name,
        version,
        remotes=["cloudfront"],
        exclude_local=True,
    )

    if len(resolution) > 0:
        return True, "cloudfront", resolution["remote_filename"]

    # Try artifactory if not found on cloudfront
    artifactory_resolution = packmanapi.resolve(
        name,
        version,
        exclude_local=True,
    )

    if len(artifactory_resolution) > 0:
        return True, "artifactory", artifactory_resolution["remote_filename"]

    # Not found on either remote
    return False, None, None


def get_dependencies(f, platforms, configs=None, expected_private=None) -> dict:
    """Extract dependency information from a packman XML file.

    Parses a packman XML file with different platform and configuration combinations
    to extract all dependencies and their metadata.

    Args:
        f: Path to the packman XML file to parse.
        platforms: List of platform identifiers to test.
        configs: List of build configurations to test (default: ['release', 'debug']).
        expected_private: List of package names that are expected to be private.

    Returns:
        Dictionary mapping (name, version) tuples to DependencyInfo objects containing dependency metadata.

    Example:

    .. code-block:: python

        >>> platforms = ['linux-x86_64']
        >>> deps = get_dependencies('deps/kit-sdk.packman.xml', platforms)
        >>> len(deps)
        15
        >>> deps[0].name
        'carb_sdk_plugins'
    """
    if configs is None:
        configs = ["release", "debug"]
    if expected_private is None:
        expected_private = []
    dependencies = {}

    for config in configs:
        for platform in [p for p in platforms if p in PLATFORM_TO_PLATFORM_TARGET]:
            test = packman.main.parse_project_file(
                f,
                None,
                {
                    "config": config,
                    "platform": platform,
                    "platform_target": PLATFORM_TO_PLATFORM_TARGET[platform],
                    "platform_host": platform,
                    "platform_target_abi": platform,
                    "root": ".",
                    "local_path": ".",
                },
                platform,
            )
            for k, v in test.dependency_map.items():
                for child in v.children:
                    if not isinstance(child, Source):
                        if (child.name, child.version) not in dependencies:
                            if child.platforms and platform not in child.platforms:
                                continue
                            if f.endswith("-nv.packman.xml") or child.name in expected_private:
                                expected_public = False
                            else:
                                expected_public = True
                            # Convert absolute path to relative path anchored at current directory
                            link_path = v.link_path
                            if os.path.isabs(link_path):
                                try:
                                    link_path = os.path.relpath(link_path, ".")
                                except ValueError:
                                    # If relpath fails (e.g., different drives on Windows), keep original
                                    pass

                            dependencies[(child.name, child.version)] = DependencyInfo(
                                name=child.name,
                                version=child.version,
                                platforms=child.platforms if child.platforms else [],
                                link_path=link_path,
                                found=False,
                                expected_public=expected_public,
                                public=False,
                                remote="unknown",
                                pull_settings=PullSettings(
                                    file=f,
                                    config=config,
                                    platform=platform,
                                    platform_target=PLATFORM_TO_PLATFORM_TARGET[platform],
                                ),
                                dependency_filename="",
                                license_files=[],
                                license_type="",
                            )

    return dependencies


def check_externals(args):
    """Check external dependencies and their licensing information.

    Main function that processes packman XML files to find dependencies,
    verify their availability on remote servers, check their public/private
    status, and analyze their license information. Results are written to
    CSV files for further analysis.

    Args:
        args: Parsed command line arguments containing configuration options.

    Example:

    .. code-block:: python

        >>> import argparse
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument('--file', help='Specific packman XML file')
        >>> args = parser.parse_args(['--file', 'deps/kit-sdk.packman.xml'])
        >>> check_externals(args)
        Processing complete. Results written to packman_full_results.csv
    """

    if args.file:
        files = glob.glob(args.file, root_dir=".", recursive=True)

    else:
        files = glob.glob("deps/**/*.packman.xml", root_dir=".", recursive=True)

    if args.allowed_external:
        expected_private = args.allowed_external
    else:
        expected_private = []

    if args.platform:
        files_to_platform_map = {x: [args.platform] for x in files}
    else:
        files_to_platform_map = build_file_to_platform_map(files)

    if args.skip_platform:
        for file, platforms in files_to_platform_map.items():
            platforms = [p for p in platforms if args.skip_platform not in p]
            files_to_platform_map[file] = platforms

    dependencies = []

    print("First pass processing ", len(files), "files to detect platforms")

    # If no platforms are found, set all platforms
    for file, platforms in files_to_platform_map.items():
        if len(platforms) == 0:
            files_to_platform_map[file] = PLATFORM_TO_PLATFORM_TARGET.keys()

    dependency_map = {}

    for f, platforms in files_to_platform_map.items():

        depends = get_dependencies(f, platforms, expected_private=expected_private)
        for dependency in depends:
            if dependency not in dependency_map:
                dependency_map[dependency] = depends[dependency]

    if args.package:
        dependency_map = {k: v for k, v in dependency_map.items() if v.name == args.package}

    print("Found", len(dependency_map), "unique dependencies")

    # Special case - We will check repo.toml for a python executable and add it to the map manually
    if not args.skip_repo_toml:
        with open("repo.toml", "rb") as repo_toml:
            repo_config = tomli.load(repo_toml)
            if "repo" in repo_config and "python_executable" in repo_config["repo"]:
                version_string = repo_config["repo"]["python_executable"]["packman_package_version"]
                package_name = repo_config["repo"]["python_executable"]["packman_package_name"]
                link_path = repo_config["repo"]["python_executable"]["packman_link_path"]
                # Substitue variablesfor different platforms
                for platform in PLATFORM_TARGETS:
                    temp_version_string = version_string.replace("${platform}", platform)
                    dependency_map[(package_name, temp_version_string)] = DependencyInfo(
                        name=package_name,
                        version=temp_version_string,
                        platforms=[platform],
                        link_path=link_path,
                        found=False,
                        expected_public=True,
                        public=False,
                        remote="",
                        pull_settings=PullSettings(
                            file="repo.toml", config="", platform=platform, platform_target=platform
                        ),
                        dependency_filename="",
                        license_files=[],
                        license_type="",
                    )

    # Alrighty, let's do our first great filter.  Let's just check for name, version
    # This just flags that the files exist on the server at all
    for name, version in tqdm(dependency_map, desc="Resolving dependencies"):
        found, remote, dependency_filename = resolve_dependency(name, version)

        dependency_map[(name, version)].found = found
        dependency_map[(name, version)].remote = remote or "unknown"
        dependency_map[(name, version)].dependency_filename = dependency_filename or ""
    print("Dependencies verified on server,", len([x for x in dependency_map.values() if not x.found]), "not found")
    for (name, version), dependency in dependency_map.items():
        if not dependency.found:
            print(f"Dependency {name} {version} not found on server")

    # This will handle situations where we can't discern the package ahead of time but
    # only one of the linux pairs has a package found
    found_pair = True
    popped_entries = []
    while found_pair:
        found_pair = False

        names = [x[0] for x in dependency_map.keys()]
        names = list(set(names))
        for name in names:
            # Find all dependencies that match this name
            dependencies = [x for x in dependency_map.values() if x.name == name]

            # Check for not found / found pairs against the linux pairs
            for a, b in LINUX_PAIRS:
                a_match = [x for x in dependencies if x.pull_settings.platform == a]
                b_match = [x for x in dependencies if x.pull_settings.platform == b]
                if not a_match or not b_match:
                    continue
                # See if one was not found and the other was
                if a_match[0].found and not b_match[0].found:
                    found_pair = True
                    popped_entries.append((name, b_match[0].version))
                    del dependency_map[(name, b_match[0].version)]
                elif not a_match[0].found and b_match[0].found:
                    found_pair = True
                    popped_entries.append((name, a_match[0].version))
                    del dependency_map[(name, a_match[0].version)]

    print("Removed", len(popped_entries), "entries that were manylinux / linux duplicates with one non-existent")

    # Use omnipackages v1 api to get public / private status
    cloudfront_deps = [
        (name, version) for (name, version), dep in dependency_map.items() if dep.found and dep.remote == "cloudfront"
    ]

    for name, version in tqdm(cloudfront_deps, desc="Checking public/private status"):
        dependency_map[(name, version)].public = check_public_private_status(
            dependency_map[(name, version)].dependency_filename
        )

    # Find license files for the dependencies
    for (name, version), dependency in tqdm(dependency_map.items(), desc="Finding license files"):
        license_info = find_license_file(
            dependency.link_path,
            name,
            config_tags={
                "config": dependency.pull_settings.config,
                "platform_target": dependency.pull_settings.platform_target,
            },
        )
        if license_info:
            # Get main license file if available
            main_license = license_info.get("main_license", "")
            if not main_license and license_info.get("package_licenses_count", 0) > 0:
                # If no main license but package licenses exist, indicate that
                main_license = f"PACKAGE-LICENSES ({license_info['package_licenses_count']} files)"

            dependency_map[(name, version)].license_files = main_license
            dependency_map[(name, version)].license_type = license_info.get("main_license_type", "Unknown")
        else:
            dependency_map[(name, version)].license_files = ""
            dependency_map[(name, version)].license_type = ""

    with open("packman_full_results.csv", "w") as full_csv, open("packman_private_results.csv", "w") as private_csv:
        header = "Package Name,Version,Public/Private,Expected Public/Private,License Files,License Type,\n"
        full_csv.write(header)
        private_csv.write(header)

        for (name, version), dependency in sorted(
            dependency_map.items(),
            key=lambda item: (
                item[1].found and item[1].expected_public and not item[1].public,
                not item[1].found,
                item[1].public,
                item[1].name,
                item[1].version,
            ),
            reverse=True,
        ):
            if not dependency.found:
                status_str = "not_found"
            elif dependency.public:
                status_str = "public"
            else:
                status_str = "private"
            expected_str = "public" if dependency.expected_public else "private"

            line = (
                f"{name},{version},{status_str},{expected_str},{dependency.license_files},{dependency.license_type},\n"
            )

            full_csv.write(line)

            if not dependency.public and dependency.expected_public:
                private_csv.write(line)

    print("Processing complete.  Results written to packman_full_results.csv")
    print("Found", len(dependency_map), "unique dependencies")
    print("Found", len([x for x in dependency_map.values() if not x.found]), "not found dependencies")
    print("Found", len([x for x in dependency_map.values() if x.public]), "public dependencies")
    print("Found", len([x for x in dependency_map.values() if not x.public]), "private dependencies")
    print(
        "Found",
        len([x for x in dependency_map.values() if not x.public and x.expected_public]),
        "private dependencies that were expected to be public",
    )


def main():
    """Main entry point with argument parsing.

    Sets up command line argument parsing and calls the main check_externals
    function to process packman dependencies and generate license reports.

    Example:

    .. code-block:: python

        >>> main()
        # Processes all packman XML files and generates CSV reports
    """
    parser = argparse.ArgumentParser(description="Check packman external dependencies and licenses.")
    parser.add_argument(
        "--file",
        "-f",
        help="Specific packman XML file to scan. If not provided, scans all files in ./deps/*.packman.xml",
    )
    parser.add_argument(
        "--package", "-p", help="Specific package name to check licenses for. If not provided, checks all packages."
    )
    parser.add_argument(
        "--skip-platform", "-s", help="Skip platforms containing this string (e.g., 'linux' or 'aarch64')"
    )
    parser.add_argument(
        "--platform", "-t", help="Explicitly set platform target (e.g., 'linux-x86_64' or 'windows-x86_64')"
    )

    parser.add_argument(
        "--exclude-package", "-e", help="Exclude packages with this name (can be used multiple times)", action="append"
    )
    parser.add_argument(
        "--allowed-external",
        "-a",
        help="Package names that are allowed to be external/private (can be used multiple times)",
        action="append",
    )
    parser.add_argument("--skip-repo-toml", help="Skip checking repo.toml for python executable", action="store_true")
    args = parser.parse_args()

    check_externals(args)


if __name__ == "__main__":
    main()
