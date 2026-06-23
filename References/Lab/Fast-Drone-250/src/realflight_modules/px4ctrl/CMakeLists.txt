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
set(MOSIM_PX4CTRL_GENERATED_DIR
  "${MOSIM_PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_g6_codegen_20260622_001/px4ctrl_core_cfunction_codegen_strict/PX4CTRL_Core_CFunction_Sysblock")

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${EIGEN_INCLUDE_DIRS}
  ${MOSIM_PX4CTRL_GENERATED_DIR}
  ${MOSIM_PX4CTRL_GENERATED_DIR}/extern_inc
  include/${PROJECT_NAME}
  include
)

add_executable(px4ctrl_node 
  src/px4ctrl_node.cpp
  src/PX4CtrlFSM.cpp
  src/PX4CtrlParam.cpp
  src/controller.cpp
  src/input.cpp
  ${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock.c
  ${MOSIM_PX4CTRL_GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock_data.c
  ${MOSIM_PX4CTRL_GENERATED_DIR}/extern_inc/momodel_extern_ince1.c
)

add_dependencies(px4ctrl_node quadrotor_msgs)

target_link_libraries(px4ctrl_node
  ${catkin_LIBRARIES}
)

catkin_install_python(PROGRAMS thrust_calibrate_scrips/thrust_calibrate.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
