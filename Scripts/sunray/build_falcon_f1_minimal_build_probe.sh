#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-${ROOT_DIR}/Results/sunray_ros1/falcon_f1_minimal_build_probe_${STAMP}}"
WS_DIR="${OUT_DIR}/ws"
SRC_DIR="${WS_DIR}/src"
LOG_FILE="${OUT_DIR}/catkin_make.log"
LOCAL_DEPS_PREFIX="${FALCON_LOCAL_DEPS_PREFIX:-}"
LOCAL_DEPS_SHIM="${OUT_DIR}/local_deps_include"
CATKIN_JOBS="${FALCON_CATKIN_JOBS:-}"
mkdir -p "${SRC_DIR}"

set +u
source /opt/ros/noetic/setup.bash 2>/dev/null || true
set -u

copy_pkg() {
  local src="$1"
  local name="$2"
  if [ ! -e "${SRC_DIR}/${name}" ]; then
    cp -a "${ROOT_DIR}/${src}" "${SRC_DIR}/${name}"
  fi
}

copy_pkg "src/planning/falcon/uav_simulator/utils/cmake_utils" "cmake_utils"
copy_pkg "src/planning/falcon/uav_simulator/utils/quadrotor_msgs" "quadrotor_msgs"
copy_pkg "src/planning/falcon/falcon_planner/exploration_utils" "exploration_utils"
copy_pkg "src/planning/falcon/falcon_planner/pathfinding" "pathfinding"
copy_pkg "src/planning/falcon/falcon_planner/exploration_preprocessing" "exploration_preprocessing"
copy_pkg "src/planning/falcon/falcon_planner/voxel_mapping" "voxel_mapping"
copy_pkg "src/planning/falcon/falcon_planner/trajectory" "trajectory"
copy_pkg "src/planning/falcon/falcon_planner/fast_planner" "fast_planner"
copy_pkg "src/planning/falcon/falcon_planner/exploration_manager" "exploration_manager"

# FALCON package.xml references plan_env, but this local FALCON snapshot does
# not include that package and the audited FALCON source does not include its
# headers. Use the closest local HKUST-style compatible package for build
# probing without modifying the reference tree.
copy_pkg "src/planning/fuel/fuel_planner/plan_env" "plan_env"

{
  echo "ROOT_DIR=${ROOT_DIR}"
  echo "OUT_DIR=${OUT_DIR}"
  echo "ROS_DISTRO=${ROS_DISTRO:-}"
  echo "LOCAL_DEPS_PREFIX=${LOCAL_DEPS_PREFIX}"
  echo "CATKIN_JOBS=${CATKIN_JOBS}"
  echo "CMAKE=$(cmake --version 2>/dev/null | head -n 1 || true)"
  echo "PACKAGES:"
  find "${SRC_DIR}" -maxdepth 1 -mindepth 1 -printf "  %f\n" | sort
} > "${OUT_DIR}/BUILD_PROBE_CONTEXT.txt"

status="failed"
exit_code=0
cmake_args=(
  -DCATKIN_WHITELIST_PACKAGES="cmake_utils;quadrotor_msgs;plan_env;exploration_utils;pathfinding;exploration_preprocessing;voxel_mapping;trajectory;fast_planner;exploration_manager"
)
if [ -n "${LOCAL_DEPS_PREFIX}" ]; then
  lib_paths=("${LOCAL_DEPS_PREFIX}/usr/lib/x86_64-linux-gnu" "${LOCAL_DEPS_PREFIX}/lib" "${LOCAL_DEPS_PREFIX}/lib64")
  nlopt_dir="${LOCAL_DEPS_PREFIX}/lib/cmake/nlopt"
  if [ ! -d "${nlopt_dir}" ] && [ -d "${LOCAL_DEPS_PREFIX}/usr/lib/x86_64-linux-gnu/cmake/nlopt" ]; then
    nlopt_dir="${LOCAL_DEPS_PREFIX}/usr/lib/x86_64-linux-gnu/cmake/nlopt"
  fi
  mkdir -p "${LOCAL_DEPS_SHIM}"
  for rel in glog gflags elfutils libdwarf; do
    if [ -e "${LOCAL_DEPS_PREFIX}/usr/include/${rel}" ] && [ ! -e "${LOCAL_DEPS_SHIM}/${rel}" ]; then
      ln -s "${LOCAL_DEPS_PREFIX}/usr/include/${rel}" "${LOCAL_DEPS_SHIM}/${rel}"
    fi
  done
  for rel in dwarf.h gelf.h libelf.h; do
    if [ -e "${LOCAL_DEPS_PREFIX}/usr/include/${rel}" ] && [ ! -e "${LOCAL_DEPS_SHIM}/${rel}" ]; then
      ln -s "${LOCAL_DEPS_PREFIX}/usr/include/${rel}" "${LOCAL_DEPS_SHIM}/${rel}"
    fi
  done
  if [ -e "${LOCAL_DEPS_PREFIX}/include/nlopt.hpp" ] && [ ! -e "${LOCAL_DEPS_SHIM}/nlopt.hpp" ]; then
    ln -s "${LOCAL_DEPS_PREFIX}/include/nlopt.hpp" "${LOCAL_DEPS_SHIM}/nlopt.hpp"
  fi
  python3 - "${SRC_DIR}" "${LOCAL_DEPS_SHIM}" "${LOCAL_DEPS_PREFIX}" <<'PY'
import sys
import re
from pathlib import Path

src = Path(sys.argv[1])
shim = sys.argv[2]
prefix = sys.argv[3]
marker = "MoSim FALCON local deps shim"
base_block = f'''

# {marker}: generated inside the Results build workspace only.
include_directories(SYSTEM
  "{shim}"
  "{prefix}/include"
)
link_directories(
  "{prefix}/usr/lib/x86_64-linux-gnu"
  "{prefix}/lib"
  "{prefix}/lib64"
)
'''
for cmake in sorted(src.glob("*/CMakeLists.txt")):
    text = cmake.read_text(errors="replace")
    if marker in text:
        continue
    lines = text.splitlines(keepends=True)
    inserted_include = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#") or not stripped.startswith("include_directories"):
            continue
        if ")" not in line[line.find("include_directories"):]:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip() == "SYSTEM":
                lines.insert(j + 1, f'  "{shim}"\n  "{prefix}/include"\n')
            else:
                lines.insert(i + 1, f'  SYSTEM\n  "{shim}"\n  "{prefix}/include"\n')
            inserted_include = True
        break
    if inserted_include:
        text = "".join(lines)
    else:
        text = (
            f'include_directories(SYSTEM "{shim}" "{prefix}/include")\n'
            + text
        )
    targets = []
    for match in re.finditer(r"add_(?:library|executable)\s*\(\s*([A-Za-z0-9_${}]+)", text, re.S):
        name = match.group(1)
        if name not in targets:
            targets.append(name)
    target_block = [
        base_block,
        "set(MOSIM_FALCON_LOCAL_DEP_LIBS)\n",
        f'foreach(_mosim_lib "{prefix}/usr/lib/x86_64-linux-gnu/libglog.so" "{prefix}/usr/lib/x86_64-linux-gnu/libgflags.so" "{prefix}/lib/libnlopt.so")\n',
        "  if(EXISTS \"${_mosim_lib}\")\n",
        "    list(APPEND MOSIM_FALCON_LOCAL_DEP_LIBS \"${_mosim_lib}\")\n",
        "  endif()\n",
        "endforeach()\n",
    ]
    for target in targets:
        target_block.extend([
            f"if(TARGET {target})\n",
            f"  target_include_directories({target} SYSTEM PRIVATE \"{shim}\" \"{prefix}/include\")\n",
            "  if(MOSIM_FALCON_LOCAL_DEP_LIBS)\n",
            f"    target_link_libraries({target} ${{MOSIM_FALCON_LOCAL_DEP_LIBS}})\n",
            "  endif()\n",
            "endif()\n",
        ])
    text = text + "\n" + "".join(target_block)
    cmake.write_text(text, encoding="utf-8")
PY
  lib_joined="$(IFS=:; echo "${lib_paths[*]}")"
  export CMAKE_INCLUDE_PATH="${LOCAL_DEPS_SHIM}:${LOCAL_DEPS_PREFIX}/include:${CMAKE_INCLUDE_PATH:-}"
  export CMAKE_LIBRARY_PATH="${lib_joined}:${CMAKE_LIBRARY_PATH:-}"
  export LIBRARY_PATH="${lib_joined}:${LIBRARY_PATH:-}"
  export LD_LIBRARY_PATH="${lib_joined}:${LD_LIBRARY_PATH:-}"
  export LDFLAGS="-L${LOCAL_DEPS_PREFIX}/usr/lib/x86_64-linux-gnu -L${LOCAL_DEPS_PREFIX}/lib ${LDFLAGS:-}"
  local_dep_linker_flags="-L${LOCAL_DEPS_PREFIX}/usr/lib/x86_64-linux-gnu -L${LOCAL_DEPS_PREFIX}/lib"
  cmake_args+=(
    -DNLopt_DIR="${nlopt_dir}"
    -DCMAKE_INCLUDE_PATH="${CMAKE_INCLUDE_PATH}"
    -DCMAKE_LIBRARY_PATH="${CMAKE_LIBRARY_PATH}"
    -DCMAKE_EXE_LINKER_FLAGS="${local_dep_linker_flags} ${CMAKE_EXE_LINKER_FLAGS:-}"
    -DCMAKE_SHARED_LINKER_FLAGS="${local_dep_linker_flags} ${CMAKE_SHARED_LINKER_FLAGS:-}"
  )
fi
catkin_make_args=("${cmake_args[@]}")
if [ -n "${CATKIN_JOBS}" ]; then
  catkin_make_args+=("-j${CATKIN_JOBS}" "-l${CATKIN_JOBS}")
fi
(
  cd "${WS_DIR}"
  timeout 300s catkin_make "${catkin_make_args[@]}"
) > "${LOG_FILE}" 2>&1 || exit_code=$?

if [ "${exit_code}" = "0" ]; then
  status="passed"
elif [ "${exit_code}" = "124" ]; then
  status="timeout_300s"
else
  status="failed"
fi

python3 - "$OUT_DIR" "$status" "$exit_code" <<'PY'
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
status = sys.argv[2]
exit_code = int(sys.argv[3])
log = out / "catkin_make.log"
text = log.read_text(errors="replace") if log.exists() else ""
interesting = []
for line in text.splitlines():
    low = line.lower()
    if any(k in low for k in ["error:", "could not find", "not found", "nlopt", "glog", "dw", "failed", "no rule to make"]):
        interesting.append(line[-500:])
interesting = interesting[-80:]
payload = {
    "status": status,
    "exit_code": exit_code,
    "out_dir": str(out),
    "workspace": str(out / "ws"),
    "log": str(log),
    "interesting_log_tail": interesting,
}
(out / "FALCON_F1_MINIMAL_BUILD_PROBE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
summary = [
    "# FALCON F1 Minimal Build Probe",
    "",
    f"Status: `{status}`",
    f"Exit code: `{exit_code}`",
    "",
    "This probe uses an isolated Results workspace with symlinked local reference packages.",
    "It does not modify FALCON source and does not install system packages.",
    "",
    "Key files:",
    "",
    "- `BUILD_PROBE_CONTEXT.txt`",
    "- `catkin_make.log`",
    "- `FALCON_F1_MINIMAL_BUILD_PROBE.json`",
]
(out / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
print(json.dumps({"status": status, "exit_code": exit_code, "out_dir": str(out)}, ensure_ascii=False))
PY
