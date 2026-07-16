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

set(MOSIM_PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../../../..")
set(MOSIM_PX4CTRL_GENERATED_BACKEND "legacy_px4ctrl"
  CACHE STRING "MoSim generated controller backend: legacy_px4ctrl, g9_family, g10_bde_family, or pid_attitude_thrust")
set(MOSIM_PX4CTRL_GENERATED_DIR
  "${MOSIM_PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_mworks_goal5_m4a_cfunction_20260629_092411/px4ctrl_core_cfunction_codegen_strict/PX4CTRL_Core_CFunction_Sysblock"
  CACHE PATH "Accepted MoSim MWORKS CFunction generated px4ctrl_core directory")
set(MOSIM_PX4CTRL_G9_FAMILY_GENERATED_DIR
  "${MOSIM_PROJECT_ROOT}/Results/g9/controller_family_attitude_thrust_v1/g9_family_mworks_codegen_20260630_work/g9_family_cfunction_codegen_strict/G9_Family_CFunction_Sysblock"
  CACHE PATH "Accepted MoSim MWORKS CFunction generated G9 controller-family directory")
set(MOSIM_PX4CTRL_G10_BDE_FAMILY_GENERATED_DIR
  "${MOSIM_PROJECT_ROOT}/Results/g10/min_enhancements_v1/g10bde_mworks_codegen_stateiso_20260701_work/g10_bde_family_cfunction_codegen_strict/G10_BDE_Family_CFunction_Sysblock_StateIso"
  CACHE PATH "Accepted MoSim MWORKS CFunction generated G10-B/D/E controller-family directory")
set(MOSIM_PX4CTRL_PID_ATTITUDE_THRUST_GENERATED_DIR
  "${MOSIM_PROJECT_ROOT}/Results/control_platform/p1_pid_attitude_thrust_mworks_20260716/generated_c_v2/MoSim_PID_AttitudeThrust_CFunction_Sysblock"
  CACHE PATH "Accepted MoSim MWORKS CFunction generated PID ATTITUDE_THRUST directory")
set(MOSIM_PX4CTRL_GOLDEN_SLICE_DIR
  "${MOSIM_PROJECT_ROOT}/Scripts/sunray/px4ctrl_golden_slice"
  CACHE PATH "MoSim platform-independent px4ctrl/G9 controller core directory")

if(MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "legacy_px4ctrl")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR "${MOSIM_PX4CTRL_GENERATED_DIR}")
  set(MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL "PX4CTRL_Core_CFunction_Sysblock")
  add_definitions(-DMOSIM_PX4CTRL_GENERATED_BACKEND_LEGACY=1)
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
else()
  message(FATAL_ERROR "Unsupported MOSIM_PX4CTRL_GENERATED_BACKEND=${MOSIM_PX4CTRL_GENERATED_BACKEND}; expected legacy_px4ctrl, g9_family, g10_bde_family, or pid_attitude_thrust")
endif()

message(STATUS "MoSim px4ctrl generated backend: ${MOSIM_PX4CTRL_GENERATED_BACKEND}")
message(STATUS "MoSim px4ctrl generated dir: ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}")

foreach(_mosim_generated_file
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}.c"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}.h"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_data.c"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_private.h"
    "${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/extern_inc/momodel_extern_ince1.c")
  if(NOT EXISTS "${_mosim_generated_file}")
    message(FATAL_ERROR "Missing accepted MoSim px4ctrl generated file: ${_mosim_generated_file}")
  endif()
endforeach()

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${EIGEN_INCLUDE_DIRS}
  ${MOSIM_PX4CTRL_GOLDEN_SLICE_DIR}
  ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}
  ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/extern_inc
  include/${PROJECT_NAME}
  include
)

add_executable(px4ctrl_node 
  src/px4ctrl_node.cpp
  src/PX4CtrlFSM.cpp
  src/PX4CtrlParam.cpp
  src/controller.cpp
  src/input.cpp
  ${MOSIM_PX4CTRL_GOLDEN_SLICE_DIR}/px4ctrl_core.cpp
  ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}.c
  ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/${MOSIM_PX4CTRL_ACTIVE_GENERATED_MODEL}_data.c
  ${MOSIM_PX4CTRL_ACTIVE_GENERATED_DIR}/extern_inc/momodel_extern_ince1.c
)

add_dependencies(px4ctrl_node quadrotor_msgs)

target_link_libraries(px4ctrl_node
  ${catkin_LIBRARIES}
)

catkin_install_python(PROGRAMS thrust_calibrate_scrips/thrust_calibrate.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
