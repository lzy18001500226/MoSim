#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RACER_ROOT="${RACER_ROOT:-${PROJECT_ROOT}/src/planning/racer}"
RACER_DEPS_ROOT="${RACER_DEPS_ROOT:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/fuel_deps}"
NLOPT_VERSION="${NLOPT_VERSION:-v2.7.1}"
NLOPT_ROOT="${NLOPT_ROOT:-${RACER_DEPS_ROOT}/install/nlopt-${NLOPT_VERSION}}"
RACER_BUILD_TYPE="${RACER_BUILD_TYPE:-Debug}"
RACER_BUILD_JOBS="${RACER_BUILD_JOBS:-2}"
RACER_BUILD_STEP_TIMEOUT_S="${RACER_BUILD_STEP_TIMEOUT_S:-280}"
RACER_RUN_LAUNCH_SMOKE="${RACER_RUN_LAUNCH_SMOKE:-false}"
RACER_WS_NAME="${RACER_WS_NAME:-racer_ws_d1_$(date +%Y%m%d_%H%M%S)}"
RACER_WS="${RACER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/${RACER_WS_NAME}}"

fail() {
  echo "RACER_D1_BUILD=FAIL"
  echo "reason=$1"
  exit 1
}

copy_pkg() {
  local src_rel="$1"
  local dst_rel="$2"
  local src="${RACER_ROOT}/${src_rel}"
  local dst="${RACER_WS}/src/${dst_rel}"
  [[ -d "${src}" ]] || fail "source_package_missing:${src_rel}"
  if [[ -e "${dst}" ]]; then
    fail "workspace_destination_exists:${dst}"
  fi
  mkdir -p "$(dirname "${dst}")"
  cp -a "${src}" "${dst}"
}

patch_workspace() {
  python3 - "${RACER_WS}" "${NLOPT_ROOT}" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path
import re

ws = Path(sys.argv[1])
nlopt = Path(sys.argv[2])

bspline = ws / "src" / "swarm_exploration" / "bspline_opt" / "CMakeLists.txt"
text = bspline.read_text(encoding="utf-8")
text = text.replace('set(NLOPT_INCLUDE_DIR "/usr/local/include")', f'set(NLOPT_INCLUDE_DIR "{nlopt / "include"}")')
lib = nlopt / "lib" / "libnlopt.so"
if not lib.exists():
    lib = nlopt / "lib64" / "libnlopt.so"
text = text.replace('set(NLOPT_LIBRARY "/usr/local/lib/libnlopt.so")', f'set(NLOPT_LIBRARY "{lib}")')
bspline.write_text(text, encoding="utf-8")

tsp = ws / "src" / "swarm_exploration" / "utils" / "lkh_tsp_solver" / "CMakeLists.txt"
text = tsp.read_text(encoding="utf-8")
needle = """# add_executable( tsp_node \n#   ${SRCS}\n#   src2/tsp_node.cpp\n# )\n# target_link_libraries(tsp_node ${catkin_LIBRARIES} -lm lkh_tsp_solver)\n"""
replacement = """add_executable( tsp_node \n  ${SRCS}\n  src2/tsp_node.cpp\n)\ntarget_link_libraries(tsp_node ${catkin_LIBRARIES} -lm lkh_tsp_solver)\n"""
if needle in text:
    text = text.replace(needle, replacement)
elif not re.search(r"(?m)^[ \t]*add_executable\([ \t]*tsp_node\b", text):
    text = text.rstrip() + "\n\n" + replacement
if "add_dependencies(tsp_node" not in text:
    text = text.rstrip() + "\nadd_dependencies(tsp_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})\n"
tsp.write_text(text, encoding="utf-8")

for rel in (
    "swarm_exploration/utils/lkh_tsp_solver/resource",
    "swarm_exploration/utils/lkh_mtsp_solver/resource",
):
    path = ws / "src" / rel
    path.mkdir(parents=True, exist_ok=True)
    keep = path / ".gitkeep"
    keep.touch(exist_ok=True)

mtsp_node = ws / "src" / "swarm_exploration" / "utils" / "lkh_mtsp_solver" / "src2" / "mtsp_node.cpp"
text = mtsp_node.read_text(encoding="utf-8")
text = text.replace(
    """  else if (req.prob == 3) {
    // solveMTSPWithLKH3(mtsp_dir3_.c_str());
    string cmd = "/usr/local/bin/LKH " + mtsp_dir3_;
    system(cmd.c_str());
  }
""",
    """  else if (req.prob == 3) {
    solveMTSPWithLKH3(mtsp_dir3_.c_str());
  }
""",
)
mtsp_node.write_text(text, encoding="utf-8")

uniform_grid_h = ws / "src" / "swarm_exploration" / "active_perception" / "include" / "active_perception" / "uniform_grid.h"
text = uniform_grid_h.read_text(encoding="utf-8")
if "mosim_d2_round_robin_init_" not in text:
    text = text.replace(
        """  double w_unknown_;

  // Swarm tf
""",
        """  double w_unknown_;
  bool mosim_d2_round_robin_init_;
  int mosim_d2_drone_num_;

  // Swarm tf
""",
    )
uniform_grid_h.write_text(text, encoding="utf-8")

uniform_grid_cpp = ws / "src" / "swarm_exploration" / "active_perception" / "src" / "uniform_grid.cpp"
text = uniform_grid_cpp.read_text(encoding="utf-8")
if "partitioning/mosim_d2_round_robin_init" not in text:
    text = text.replace(
        """  nh.param("partitioning/w_unknown", w_unknown_, 3.5);

  double grid_size;
""",
        """  nh.param("partitioning/w_unknown", w_unknown_, 3.5);
  nh.param("partitioning/mosim_d2_round_robin_init", mosim_d2_round_robin_init_, false);
  double mosim_d2_drone_num_param = 1.0;
  nh.param("exploration/drone_num", mosim_d2_drone_num_param, 1.0);
  mosim_d2_drone_num_ = int(mosim_d2_drone_num_param + 0.5);
  if (mosim_d2_drone_num_ < 1) mosim_d2_drone_num_ = 1;

  double grid_size;
""",
    )
    text = text.replace(
        """  // Update the dominance grid of ego drone
  if (!initialized_) {
    if (drone_id == 1 && level_ == 1) grid_ids = relevant_id_;
    // else
    //   grid_ids = {};
    ROS_WARN("Init grid allocation.");
    initialized_ = true;
  } else {
""",
        """  // Update the dominance grid of ego drone
  if (!initialized_) {
    if (mosim_d2_round_robin_init_ && level_ == 1 && mosim_d2_drone_num_ > 1) {
      grid_ids.clear();
      for (int i = 0; i < relevant_id_.size(); ++i) {
        if ((i % mosim_d2_drone_num_) + 1 == drone_id) grid_ids.push_back(relevant_id_[i]);
      }
      if (grid_ids.empty() && !relevant_id_.empty()) {
        grid_ids.push_back(relevant_id_[(drone_id - 1) % relevant_id_.size()]);
      }
      ROS_WARN("MoSim D2 round-robin init grid allocation.");
    } else if (drone_id == 1 && level_ == 1) {
      grid_ids = relevant_id_;
    }
    // else
    //   grid_ids = {};
    ROS_WARN("Init grid allocation.");
    initialized_ = true;
  } else {
""",
    )
uniform_grid_cpp.write_text(text, encoding="utf-8")

expl_data_h = ws / "src" / "swarm_exploration" / "exploration_manager" / "include" / "exploration_manager" / "expl_data.h"
text = expl_data_h.read_text(encoding="utf-8")
if "mosim_d2_disable_pair_opt_" not in text:
    text = text.replace(
        """  int repeat_send_num_;
};
""",
        """  int repeat_send_num_;
  bool mosim_d2_disable_pair_opt_;
};
""",
    )
expl_data_h.write_text(text, encoding="utf-8")

fast_exploration_fsm_cpp = ws / "src" / "swarm_exploration" / "exploration_manager" / "src" / "fast_exploration_fsm.cpp"
text = fast_exploration_fsm_cpp.read_text(encoding="utf-8")
if "fsm/mosim_d2_disable_pair_opt" not in text:
    text = text.replace(
        """  nh.param("fsm/pair_opt_interval", fp_->pair_opt_interval_, 1.0);
  nh.param("fsm/repeat_send_num", fp_->repeat_send_num_, 10);
""",
        """  nh.param("fsm/pair_opt_interval", fp_->pair_opt_interval_, 1.0);
  nh.param("fsm/repeat_send_num", fp_->repeat_send_num_, 10);
  nh.param("fsm/mosim_d2_disable_pair_opt", fp_->mosim_d2_disable_pair_opt_, false);
""",
    )
    text = text.replace(
        """void FastExplorationFSM::optTimerCallback(const ros::TimerEvent& e) {
  if (state_ == INIT) return;
""",
        """void FastExplorationFSM::optTimerCallback(const ros::TimerEvent& e) {
  if (fp_->mosim_d2_disable_pair_opt_) return;
  if (state_ == INIT) return;
""",
    )
fast_exploration_fsm_cpp.write_text(text, encoding="utf-8")

swarm2 = ws / "src" / "swarm_exploration" / "exploration_manager" / "launch" / "swarm_exploration_2.launch"
text = swarm2.read_text(encoding="utf-8")
text = text.replace(
    'args="$(find map_generator)/resource/explore1.pcd"',
    'args="$(find map_generator)/resource/pillar.pcd"',
)
text = text.replace(
    '<arg name="simulation" default="true"/>',
    '<arg name="simulation" value="false"/>',
)
swarm2.write_text(text, encoding="utf-8")

traj_utils = ws / "src" / "swarm_exploration" / "traj_utils" / "CMakeLists.txt"
text = traj_utils.read_text(encoding="utf-8")
text = text.replace(
    """add_executable(process_msg \n    src/process_msg.cpp\n)\ntarget_link_libraries( process_msg\n    ${catkin_LIBRARIES} \n    ${PCL_LIBRARIES}\n    )  \n""",
    """# MoSim RACER-D1 builds the planner library path only. The upstream\n# process_msg utility is not required for planner integration smoke.\n""",
)
traj_utils.write_text(text, encoding="utf-8")

plan_manage = ws / "src" / "swarm_exploration" / "plan_manage" / "CMakeLists.txt"
text = plan_manage.read_text(encoding="utf-8")
text = text.replace(
    """add_executable(fast_planner_node\n  src/fast_planner_node.cpp \n  src/kino_replan_fsm.cpp\n  src/topo_replan_fsm.cpp\n  test/local_explore_fsm.cpp\n  src/planner_manager.cpp\n  src/planner_manager_dev.cpp\n  )\ntarget_link_libraries(fast_planner_node \n  ${catkin_LIBRARIES}\n  )\n\n""",
    """# MoSim RACER-D1 uses exploration_manager/exploration_node as the\n# upstream autonomous-exploration entry, so fast_planner_node is skipped here.\n\n""",
)
text = text.replace(
    """add_executable(proc_msg \n    test/process_msg.cpp\n)\ntarget_link_libraries( proc_msg\n    ${catkin_LIBRARIES} \n    ${PCL_LIBRARIES}\n    )  \n\nadd_executable(proc_msg2 \n    test/process_msg2.cpp\n)\ntarget_link_libraries( proc_msg2\n    ${catkin_LIBRARIES} \n    ${PCL_LIBRARIES}\n    )  \n\n""",
    """# Upstream proc_msg/proc_msg2 are debug converters, not D1 gate executables.\n\n""",
)
plan_manage.write_text(text, encoding="utf-8")
PY
}

check_executable() {
  local rel="$1"
  [[ -x "${RACER_WS}/devel/lib/${rel}" ]] || fail "missing_executable:${rel}"
}

run_build_step() {
  local mode="$1"
  local name="$2"
  shift 2

  echo "build_step=${name}"
  set +e
  timeout --kill-after=10s "${RACER_BUILD_STEP_TIMEOUT_S}" "$@"
  local code=$?
  set -e

  if [[ "${code}" -eq 0 ]]; then
    echo "build_step_${name}=PASS"
    return 0
  fi

  if [[ "${code}" -eq 124 && "${mode}" == "allow_timeout" ]]; then
    echo "build_step_${name}=TIMEOUT_CONTINUE"
    return 0
  fi

  fail "build_step_failed:${name}:exit_${code}"
}

echo "RACER_D1_BUILD=START"
echo "project_root=${PROJECT_ROOT}"
echo "racer_root=${RACER_ROOT}"
echo "racer_ws=${RACER_WS}"
echo "nlopt_root=${NLOPT_ROOT}"
echo "racer_build_type=${RACER_BUILD_TYPE}"
echo "racer_build_jobs=${RACER_BUILD_JOBS}"
echo "racer_build_step_timeout_s=${RACER_BUILD_STEP_TIMEOUT_S}"
echo "racer_run_launch_smoke=${RACER_RUN_LAUNCH_SMOKE}"

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
[[ -d "${RACER_ROOT}" ]] || fail "racer_root_missing"
[[ ! -e "${RACER_WS}" ]] || fail "workspace_already_exists:${RACER_WS}"
[[ -f "${NLOPT_ROOT}/include/nlopt.hpp" || -f "${NLOPT_ROOT}/include/nlopt.h" ]] \
  || fail "nlopt_header_missing_run_setup_fuel_ros1_dependencies_first"
[[ -f "${NLOPT_ROOT}/lib/libnlopt.so" || -f "${NLOPT_ROOT}/lib64/libnlopt.so" ]] \
  || fail "nlopt_library_missing_run_setup_fuel_ros1_dependencies_first"

set +u
source /opt/ros/noetic/setup.bash
set -u

mkdir -p "${RACER_WS}/src"

copy_pkg "swarm_exploration/plan_env" "swarm_exploration/plan_env"
copy_pkg "swarm_exploration/path_searching" "swarm_exploration/path_searching"
copy_pkg "swarm_exploration/active_perception" "swarm_exploration/active_perception"
copy_pkg "swarm_exploration/bspline" "swarm_exploration/bspline"
copy_pkg "swarm_exploration/bspline_opt" "swarm_exploration/bspline_opt"
copy_pkg "swarm_exploration/poly_traj" "swarm_exploration/poly_traj"
copy_pkg "swarm_exploration/traj_utils" "swarm_exploration/traj_utils"
copy_pkg "swarm_exploration/plan_manage" "swarm_exploration/plan_manage"
copy_pkg "swarm_exploration/exploration_manager" "swarm_exploration/exploration_manager"
copy_pkg "swarm_exploration/utils/lkh_tsp_solver" "swarm_exploration/utils/lkh_tsp_solver"
copy_pkg "swarm_exploration/utils/lkh_mtsp_solver" "swarm_exploration/utils/lkh_mtsp_solver"
copy_pkg "uav_simulator/Utils/quadrotor_msgs" "uav_simulator/Utils/quadrotor_msgs"
copy_pkg "uav_simulator/map_generator" "uav_simulator/map_generator"

patch_workspace

# RACER is large enough on the Windows-mounted workspace that a single
# catkin_make can exceed the normal live wait budget even when there is no
# compiler error. Seed the build tree, then finish the exact D1 entry targets in
# bounded stages. A timeout on the seed pass is acceptable only after CMake has
# created the build tree; target-stage timeouts still fail.
run_build_step allow_timeout seed_catkin_make \
  catkin_make -C "${RACER_WS}" \
    -j"${RACER_BUILD_JOBS}" \
    -DCMAKE_BUILD_TYPE="${RACER_BUILD_TYPE}" \
    -DNLOPT_ROOT="${NLOPT_ROOT}"

[[ -f "${RACER_WS}/build/Makefile" ]] || fail "build_makefile_missing_after_seed"

run_build_step required active_perception \
  make -C "${RACER_WS}/build" -j"${RACER_BUILD_JOBS}" active_perception
run_build_step required bspline_opt \
  make -C "${RACER_WS}/build" -j"${RACER_BUILD_JOBS}" bspline_opt
run_build_step required plan_manage \
  make -C "${RACER_WS}/build" -j"${RACER_BUILD_JOBS}" plan_manage
run_build_step required ground_node \
  make -C "${RACER_WS}/build" -j"${RACER_BUILD_JOBS}" ground_node
run_build_step required exploration_node_traj_server \
  make -C "${RACER_WS}/build" -j"${RACER_BUILD_JOBS}" exploration_node traj_server
run_build_step required tsp_mtsp_map \
  make -C "${RACER_WS}/build" -j"${RACER_BUILD_JOBS}" tsp_node mtsp_node map_pub

set +u
source "${RACER_WS}/devel/setup.bash"
set -u

for pkg in \
  plan_env path_searching active_perception bspline bspline_opt poly_traj \
  traj_utils plan_manage exploration_manager lkh_tsp_solver lkh_mtsp_solver \
  quadrotor_msgs map_generator
do
  rospack find "${pkg}" >/dev/null
  echo "rospack_${pkg}=$(rospack find "${pkg}")"
done

check_executable "exploration_manager/exploration_node"
check_executable "exploration_manager/ground_node"
check_executable "plan_manage/traj_server"
check_executable "lkh_tsp_solver/tsp_node"
check_executable "lkh_mtsp_solver/mtsp_node"
check_executable "map_generator/map_pub"

if [[ -x /usr/local/bin/LKH ]]; then
  echo "lkh_binary=/usr/local/bin/LKH"
else
  echo "lkh_binary_missing=/usr/local/bin/LKH"
fi

roslaunch exploration_manager single_drone_exploration.xml --nodes >/dev/null
echo "launch_nodes_single_drone_exploration=PASS"
roslaunch exploration_manager swarm_exploration_2.launch --nodes >/dev/null
echo "launch_nodes_swarm_exploration_2=PASS"

if [[ "${RACER_RUN_LAUNCH_SMOKE}" == "true" ]]; then
  timeout "${RACER_LAUNCH_SMOKE_TIMEOUT_S:-90}" \
    roslaunch exploration_manager swarm_exploration_2.launch >"${RACER_WS}/racer_launch_smoke.log" 2>&1 || {
      code=$?
      echo "launch_smoke_exit_code=${code}"
      fail "launch_smoke_failed_or_timed_out"
    }
  echo "launch_smoke=PASS"
else
  echo "launch_smoke=SKIPPED_static_nodes_only"
fi

echo "RACER_WS=${RACER_WS}"
echo "RACER_D1_BUILD=PASS"
