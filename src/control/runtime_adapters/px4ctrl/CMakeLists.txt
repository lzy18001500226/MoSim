cmake_minimum_required(VERSION 2.8.3)
project(px4ctrl)

set(CMAKE_VERBOSE_MAKEFILE "false")

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_FLAGS "-std=c++11")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall -g")

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  quadrotor_msgs
  geometry_msgs
  sensor_msgs
  uav_utils
  mavros
)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
find_package(Eigen3 REQUIRED)

catkin_package(
)

get_filename_component(MOSIM_PX4CTRL_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" REALPATH)
get_filename_component(MOSIM_PX4CTRL_CONTROL_SOURCE_DIR
  "${MOSIM_PX4CTRL_SOURCE_DIR}/../.." REALPATH)
set(MOSIM_PX4CTRL_GENERATED_BACKEND "legacy_px4ctrl"
  CACHE STRING "MoSim generated controller backend; see the selection chain below")
set(MOSIM_PX4CTRL_GENERATED_ROOT
  "${MOSIM_PX4CTRL_SOURCE_DIR}/generated"
  CACHE PATH "Project-local generated px4ctrl source root")

# FORCE removes historical cache values that pointed into Results. All backend
# selectors are intentionally constrained to package-local source directories.
set(MOSIM_PX4CTRL_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/legacy_px4ctrl"
  CACHE PATH "Project-local legacy px4ctrl generated source directory" FORCE)
set(MOSIM_PX4CTRL_GRAPHICAL_C99_SOURCE_DIR
  "${MOSIM_PX4CTRL_CONTROL_SOURCE_DIR}/codegen/px4ctrl"
  CACHE PATH "Project-local MWORKS graphical px4ctrl C99 export directory" FORCE)
set(MOSIM_PX4CTRL_G9_FAMILY_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/g9_family"
  CACHE PATH "Project-local G9 controller-family generated source directory" FORCE)
set(MOSIM_PX4CTRL_G10_BDE_FAMILY_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/g10_bde_family"
  CACHE PATH "Project-local G10-B/D/E controller-family generated source directory" FORCE)
set(MOSIM_PX4CTRL_PID_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/pid_attitude_thrust"
  CACHE PATH "Project-local PID ATTITUDE_THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_WAVE_A_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/wave_a_attitude_thrust"
  CACHE PATH "Project-local Wave A ATTITUDE/BODY_RATE THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_LINEAR_ROBUST_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/linear_robust_attitude_thrust"
  CACHE PATH "Project-local linear/robust ATTITUDE_THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_CLASSIC_CONTROLLER_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/classic_controller_attitude_thrust"
  CACHE PATH "Project-local classic-controller ATTITUDE_THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_SLIDING_MODE_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/sliding_mode_attitude_thrust"
  CACHE PATH "Project-local sliding-mode ATTITUDE_THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_MPC_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/mpc_attitude_thrust"
  CACHE PATH "Project-local MPC ATTITUDE_THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_ENHANCEMENT_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/enhancement_attitude_thrust"
  CACHE PATH "Project-local enhancement ATTITUDE_THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_LEARNING_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/learning_attitude_thrust"
  CACHE PATH "Project-local learning ATTITUDE_THRUST generated source directory" FORCE)
set(MOSIM_PX4CTRL_SAFETY_SUPERVISOR_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/safety_supervisor"
  CACHE PATH "Project-local SafetySupervisor generated source directory" FORCE)
set(MOSIM_PX4CTRL_P10_L1_AWFF_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/p10_l1_awff"
  CACHE PATH "Project-local P10 L1/AWFF generated source directory" FORCE)
set(MOSIM_PX4CTRL_P10_DFBC_FAMILY_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/p10_dfbc_family"
  CACHE PATH "Project-local P10 DFBC/DOB generated source directory" FORCE)
set(MOSIM_PX4CTRL_P10_HINF_WRENCH_GENERATED_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/p10_hinf_wrench"
  CACHE PATH "Project-local P10 frozen-hover H-infinity WRENCH adapter source directory" FORCE)
set(MOSIM_PX4CTRL_GOLDEN_SLICE_DIR
  "${MOSIM_PX4CTRL_GENERATED_ROOT}/golden_slice"
  CACHE PATH "Project-local px4ctrl controller-core source directory" FORCE)

function(mosim_require_path_within _label _root _candidate)
  get_filename_component(_mosim_root_abs "${_root}" ABSOLUTE)
  get_filename_component(_mosim_candidate_abs "${_candidate}" ABSOLUTE)
  if(EXISTS "${_mosim_root_abs}")
    get_filename_component(_mosim_root_abs "${_mosim_root_abs}" REALPATH)
  endif()
  if(EXISTS "${_mosim_candidate_abs}")
    get_filename_component(_mosim_candidate_abs "${_mosim_candidate_abs}" REALPATH)
  endif()
  file(RELATIVE_PATH _mosim_relative "${_mosim_root_abs}" "${_mosim_candidate_abs}")
  if(_mosim_relative STREQUAL ".." OR _mosim_relative MATCHES "^\\.\\./" OR IS_ABSOLUTE "${_mosim_relative}")
    message(FATAL_ERROR "${_label} must remain below ${_mosim_root_abs}: ${_mosim_candidate_abs}")
  endif()
endfunction()

mosim_require_path_within("px4ctrl generated root" "${MOSIM_PX4CTRL_SOURCE_DIR}" "${MOSIM_PX4CTRL_GENERATED_ROOT}")

if(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "legacy_px4ctrl")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "PX4CTRL_Core_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_LEGACY=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "graphical_px4ctrl_c99")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_GRAPHICAL_C99_SOURCE_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "PX4CTRL_Original_OuterLoop_Graphical_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_GRAPHICAL_PX4CTRL_C99=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "g9_family")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_G9_FAMILY_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "G9_Family_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "g10_bde_family")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_G10_BDE_FAMILY_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "G10_BDE_Family_CFunction_Sysblock_StateIso")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_G10_BDE_FAMILY=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "pid_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_PID_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_PID_AttitudeThrust_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "wave_a_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_WAVE_A_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_WaveA_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "linear_robust_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_LINEAR_ROBUST_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P2_LinearRobust_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "classic_controller_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_CLASSIC_CONTROLLER_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_Classic_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "sliding_mode_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_SLIDING_MODE_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P3_SlidingMode_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "mpc_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_MPC_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P4_Mpc_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "enhancement_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_ENHANCEMENT_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P5_Enhancement_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "learning_attitude_thrust")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_LEARNING_ATTITUDE_THRUST_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "safety_supervisor")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_SAFETY_SUPERVISOR_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P6_SafetySupervisor_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "p10_l1_awff")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_P10_L1_AWFF_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P10_G10_BDE_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "p10_dfbc_family")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_P10_DFBC_FAMILY_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P10_DFBC_Family_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY=1)
elseif(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "p10_hinf_wrench")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_P10_HINF_WRENCH_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH=1)
else()
  message(FATAL_ERROR "Unsupported MOSIM_PX4CTRL_GENERATED_BACKEND=${MOSIM_PX4CTRL_GENERATED_BACKEND}")
endif()

if(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "graphical_px4ctrl_c99")
  mosim_require_path_within("px4ctrl graphical C99 source" "${MOSIM_PX4CTRL_CONTROL_SOURCE_DIR}" "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}")
else()
  mosim_require_path_within("px4ctrl active generated source" "${MOSIM_PX4CTRL_GENERATED_ROOT}" "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}")
endif()
mosim_require_path_within("px4ctrl core source" "${MOSIM_PX4CTRL_GENERATED_ROOT}" "${MOSIM_PX4CTRL_GOLDEN_SLICE_DIR}")

message(STATUS "MoSim px4ctrl generated backend: ${MOSIM_PX4CTRL_GENERATED_BACKEND}")
message(STATUS "MoSim px4ctrl generated dir: ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}")

set(MOSIM_PX4CTRL_REQUIRED_GENERATED_FILES
  "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}.c"
  "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}.h"
  "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_data.c"
  "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_private.h")
if(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "graphical_px4ctrl_c99")
  list(APPEND MOSIM_PX4CTRL_REQUIRED_GENERATED_FILES
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_extern_include.h"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/mwb_runtime.h"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/mwb_types.h"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/px4ctrl_graphical_generated_shared.c"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/px4ctrl_graphical_generated_shared.h"
    "${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock.c"
    "${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock.h"
    "${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock_data.c"
    "${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock_private.h"
    "${MOSIM_PX4CTRL_GENERATED_DIR}/extern_inc/momodel_extern_ince1.c")
else()
  list(APPEND MOSIM_PX4CTRL_REQUIRED_GENERATED_FILES
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/extern_inc/momodel_extern_ince1.c")
endif()
if(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "legacy_px4ctrl")
  list(APPEND MOSIM_PX4CTRL_REQUIRED_GENERATED_FILES
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_extern_include.h"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/mwb_runtime.h"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/mwb_types.h")
endif()
foreach(_mosim_generated_file ${MOSIM_PX4CTRL_REQUIRED_GENERATED_FILES})
  if(NOT EXISTS "${_mosim_generated_file}")
    message(FATAL_ERROR "Missing project-local px4ctrl generated file: ${_mosim_generated_file}")
  endif()
endforeach()
foreach(_mosim_core_file
    "${MOSIM_PX4CTRL_GOLDEN_SLICE_DIR}/px4ctrl_core.cpp"
    "${MOSIM_PX4CTRL_GOLDEN_SLICE_DIR}/px4ctrl_core.h")
  if(NOT EXISTS "${_mosim_core_file}")
    message(FATAL_ERROR "Missing project-local px4ctrl core file: ${_mosim_core_file}")
  endif()
endforeach()

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${EIGEN_INCLUDE_DIRS}
  ${MOSIM_PX4CTRL_GOLDEN_SLICE_DIR}
  ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}
  ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/extern_inc
  ${MOSIM_PX4CTRL_GENERATED_DIR}
  ${MOSIM_PX4CTRL_GENERATED_DIR}/extern_inc
  include/${PROJECT_NAME}
  include
)

set(MOSIM_PX4CTRL_NODE_SOURCES
  src/px4ctrl_node.cpp
  src/PX4CtrlFSM.cpp
  src/PX4CtrlParam.cpp
  src/controller.cpp
  src/input.cpp
  ${MOSIM_PX4CTRL_GOLDEN_SLICE_DIR}/px4ctrl_core.cpp)

if(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "graphical_px4ctrl_c99")
  # The graphical export owns the active C99 control path.  The renamed
  # wrapper avoids Init/Step symbol collisions with the legacy compatibility
  # source retained for inactive historical CFunction modes.
  list(APPEND MOSIM_PX4CTRL_NODE_SOURCES
    ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/px4ctrl_graphical_generated_shared.c
    ${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock.c
    ${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock_data.c
    ${MOSIM_PX4CTRL_GENERATED_DIR}/extern_inc/momodel_extern_ince1.c)
else()
  list(APPEND MOSIM_PX4CTRL_NODE_SOURCES
    ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}.c
    ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_data.c
    ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/extern_inc/momodel_extern_ince1.c)
endif()

add_executable(px4ctrl_node
  ${MOSIM_PX4CTRL_NODE_SOURCES}
)

add_dependencies(px4ctrl_node ${catkin_EXPORTED_TARGETS})

target_link_libraries(px4ctrl_node
  ${catkin_LIBRARIES}
)
if(UNIX)
  target_link_libraries(px4ctrl_node m)
endif()

catkin_install_python(PROGRAMS thrust_calibrate_scrips/thrust_calibrate.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
