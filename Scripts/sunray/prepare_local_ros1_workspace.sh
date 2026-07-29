#!/usr/bin/env bash
# Assemble a generated Catkin workspace whose only project source inputs are under src/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
MANIFEST="${PROJECT_ROOT}/Config/runtime/ros1_local_source_manifest.v1.json"
WORKSPACE="${WORKSPACE:-${PROJECT_ROOT}/build/ros1/local_source_ws}"
PROFILE="foundation"
BUILD=false
VERIFY=false
# The generated Catkin tree lives on the Windows-mounted project volume.
# Single-threaded default avoids timestamp/dependency-file races on that mount.
CATKIN_JOBS="${CATKIN_JOBS:-1}"

usage() {
  cat <<'EOF'
Usage: bash Scripts/sunray/prepare_local_ros1_workspace.sh [options]

Creates or verifies build/ros1/local_source_ws from links that point only to
project src/ directories. The command never deletes an existing workspace,
does not start ROS/Gazebo/PX4, and does not use References, Results, or an old
WSL workspace as a source input.

Options:
  --profile <foundation|flight_adapter|perception|controller>
  --workspace <project-relative build/ros1 path>
  --build                 Run the profile's visible catkin_make command.
  --verify                Source the generated workspace and prove each profile
                          package resolves to project src/ through rospack.
  --jobs <count>          catkin_make parallel job count (default: 1).
  -h, --help              Show this help.
EOF
}

die() {
  echo "BLOCKER $*" >&2
  exit 2
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --profile)
      [[ "$#" -ge 2 ]] || die "--profile requires a value"
      PROFILE="$2"
      shift 2
      ;;
    --workspace)
      [[ "$#" -ge 2 ]] || die "--workspace requires a value"
      WORKSPACE="$2"
      shift 2
      ;;
    --build)
      BUILD=true
      shift
      ;;
    --verify)
      VERIFY=true
      shift
      ;;
    --jobs)
      [[ "$#" -ge 2 ]] || die "--jobs requires a value"
      CATKIN_JOBS="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

for command_name in python3 realpath ln mkdir; do
  command -v "${command_name}" >/dev/null 2>&1 || die "required command missing: ${command_name}"
done

PROJECT_ROOT="$(realpath "${PROJECT_ROOT}")"
SOURCE_ROOT="$(realpath "${PROJECT_ROOT}/src")"
[[ -f "${MANIFEST}" ]] || die "source manifest missing: ${MANIFEST}"

if [[ "${WORKSPACE}" != /* ]]; then
  WORKSPACE="${PROJECT_ROOT}/${WORKSPACE}"
fi
WORKSPACE="$(realpath -m "${WORKSPACE}")"
case "${WORKSPACE}" in
  "${PROJECT_ROOT}"/build/ros1/*) ;;
  *) die "workspace must remain below ${PROJECT_ROOT}/build/ros1: ${WORKSPACE}" ;;
esac

[[ "${CATKIN_JOBS}" =~ ^[1-9][0-9]*$ ]] || die "--jobs must be a positive integer"

mkdir -p "${WORKSPACE}/src"

mapfile -t PROFILE_LINES < <(
  python3 - "${MANIFEST}" "${PROFILE}" <<'PY'
import json
import sys

manifest_path, requested_profile = sys.argv[1:]
payload = json.load(open(manifest_path, encoding="utf-8"))
profiles = payload["profiles"]
visited = set()

def collect(profile_id):
    if profile_id in visited:
        raise SystemExit(f"profile inheritance cycle: {profile_id}")
    if profile_id not in profiles:
        raise SystemExit(f"unknown profile: {profile_id}")
    visited.add(profile_id)
    profile = profiles[profile_id]
    links = []
    build_packages = []
    if "extends" in profile:
        parent_links, parent_packages = collect(profile["extends"])
        links.extend(parent_links)
        build_packages.extend(parent_packages)
    links.extend(profile.get("links", []))
    build_packages.extend(profile.get("build_packages", []))
    return links, build_packages

links, packages = collect(requested_profile)
seen_paths = set()
for link in links:
    workspace_path = link["workspace_path"]
    source_path = link["source_path"]
    if workspace_path in seen_paths:
        raise SystemExit(f"duplicate workspace link: {workspace_path}")
    seen_paths.add(workspace_path)
    print(f"LINK\t{workspace_path}\t{source_path}")
for package in dict.fromkeys(packages):
    print(f"PACKAGE\t{package}")
PY
)

safe_link() {
  local source="$1"
  local target="$2"
  local target_parent
  target_parent="$(dirname "${target}")"
  mkdir -p "${target_parent}"
  if [[ -L "${target}" ]]; then
    [[ "$(realpath "${target}")" == "${source}" ]] || die "workspace link already targets another path: ${target}"
    return
  fi
  [[ ! -e "${target}" ]] || die "workspace path already exists and is not a generated link: ${target}"
  ln -s "${source}" "${target}"
}

sanitize_ros_build_environment() {
  # WSL imports the Windows PATH by default. Keep this build process on the
  # Ubuntu toolchain so an Anaconda CMake package cannot override Gazebo's
  # system Protobuf dependency.
  unset CMAKE_PREFIX_PATH CMAKE_MODULE_PATH CMAKE_TOOLCHAIN_FILE CMAKE_GENERATOR
  unset CONDA_PREFIX CONDA_DEFAULT_ENV CONDA_EXE CONDA_PYTHON_EXE
  unset LD_LIBRARY_PATH PKG_CONFIG_PATH PYTHONHOME PYTHONPATH
  unset ROS_PACKAGE_PATH ROSLISP_PACKAGE_DIRECTORIES ROS_ETC_DIR ROS_DISTRO ROS_VERSION
  export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib"
}

# `--force-cmake` reconfigures a Catkin workspace but retains package-discovery
# cache entries. Remove the known host-IDE package roots so WSL resolves the
# Ubuntu ROS/Gazebo dependency set again.
CMAKE_SYSTEM_PACKAGE_RESET_ARGS=(
  -UGTest_DIR
  -UProtobuf_DIR
  -Uabsl_DIR
  -Uutf8_range_DIR
)

verify_workspace_packages() {
  [[ -f "${WORKSPACE}/devel/setup.bash" ]] || die "workspace has no generated setup.bash; build before --verify: ${WORKSPACE}"
  sanitize_ros_build_environment
  set +u
  source /opt/ros/noetic/setup.bash
  source "${WORKSPACE}/devel/setup.bash"
  set -u
  command -v rospack >/dev/null 2>&1 || die "rospack is unavailable after sourcing the workspace"

  printf 'ROSPACK_SOURCE_ROOT=%s\n' "${SOURCE_ROOT}"
  local package_name resolved_path canonical_path
  for package_name in "${BUILD_PACKAGES[@]}"; do
    resolved_path="$(rospack find "${package_name}")" || die "rospack cannot resolve profile package: ${package_name}"
    canonical_path="$(realpath "${resolved_path}")"
    case "${canonical_path}" in
      "${SOURCE_ROOT}"/*) ;;
      *) die "rospack resolved outside project src for ${package_name}: ${canonical_path}" ;;
    esac
    printf 'ROSPACK_PACKAGE=%s\n' "${package_name}"
    printf 'ROSPACK_PATH=%s\n' "${resolved_path}"
    printf 'ROSPACK_REALPATH=%s\n' "${canonical_path}"
  done
}

BUILD_PACKAGES=()
LINK_RECORDS=()
for line in "${PROFILE_LINES[@]}"; do
  IFS=$'\t' read -r kind first second <<< "${line}"
  case "${kind}" in
    LINK)
      source="$(realpath "${PROJECT_ROOT}/${second}")"
      case "${source}" in
        "${SOURCE_ROOT}"/*) ;;
        *) die "manifest source resolves outside src: ${second}" ;;
      esac
      [[ -d "${source}" ]] || die "manifest source directory is missing: ${source}"
      target="${WORKSPACE}/src/${first}"
      safe_link "${source}" "${target}"
      LINK_RECORDS+=("${first}:${second}")
      ;;
    PACKAGE)
      BUILD_PACKAGES+=("${first}")
      ;;
    *)
      die "unexpected manifest record: ${line}"
      ;;
  esac
done

CATKIN_TOPLEVEL="/opt/ros/noetic/share/catkin/cmake/toplevel.cmake"
[[ -f "${CATKIN_TOPLEVEL}" ]] || die "ROS Noetic catkin toplevel is missing: ${CATKIN_TOPLEVEL}"
safe_link "$(realpath "${CATKIN_TOPLEVEL}")" "${WORKSPACE}/src/CMakeLists.txt"

python3 - "${WORKSPACE}/workspace_manifest.json" "${PROFILE}" "${WORKSPACE}" "${MANIFEST}" "${LINK_RECORDS[@]}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

output = pathlib.Path(sys.argv[1])
profile = sys.argv[2]
workspace = sys.argv[3]
source_manifest = sys.argv[4]
links = []
for record in sys.argv[5:]:
    workspace_path, source_path = record.split(":", 1)
    links.append({"workspace_path": workspace_path, "source_path": source_path})
payload = {
    "schema": "mosim.ros1_local_workspace.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "profile": profile,
    "workspace": workspace,
    "source_manifest": source_manifest,
    "source_input_root": "src",
    "links": links,
}
output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY

printf 'LOCAL_ROS1_WORKSPACE=%s\n' "${WORKSPACE}"
printf 'PROFILE=%s\n' "${PROFILE}"
printf 'SOURCE_MANIFEST=%s\n' "${MANIFEST}"
printf 'WORKSPACE_MANIFEST=%s\n' "${WORKSPACE}/workspace_manifest.json"
printf 'CATKIN_COMMAND='
printf 'catkin_make -C %q --force-cmake --only-pkg-with-deps' "${WORKSPACE}"
printf ' %q' "${BUILD_PACKAGES[@]}"
printf ' -j%q --cmake-args' "${CATKIN_JOBS}"
printf ' %q' "${CMAKE_SYSTEM_PACKAGE_RESET_ARGS[@]}"
printf '\n'

if [[ "${BUILD}" == "true" ]]; then
  [[ -f /opt/ros/noetic/setup.bash ]] || die "ROS Noetic setup is missing: /opt/ros/noetic/setup.bash"
  sanitize_ros_build_environment
  set +u
  # ROS Noetic setup fragments can read variables before defining them.
  source /opt/ros/noetic/setup.bash
  set -u
  command -v catkin_make >/dev/null 2>&1 || die "catkin_make is unavailable after sourcing ROS Noetic"
  catkin_make -C "${WORKSPACE}" --force-cmake --only-pkg-with-deps "${BUILD_PACKAGES[@]}" \
    -j"${CATKIN_JOBS}" --cmake-args "${CMAKE_SYSTEM_PACKAGE_RESET_ARGS[@]}"
fi

if [[ "${VERIFY}" == "true" ]]; then
  verify_workspace_packages
fi
