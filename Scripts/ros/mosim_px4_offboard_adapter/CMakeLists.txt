cmake_minimum_required(VERSION 3.8)
project(mosim_px4_offboard_adapter)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(mosim_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(px4_msgs REQUIRED)

add_executable(planner_setpoint_to_px4_offboard_node src/planner_setpoint_to_px4_offboard_node.cpp)
target_compile_features(planner_setpoint_to_px4_offboard_node PUBLIC cxx_std_17)
ament_target_dependencies(planner_setpoint_to_px4_offboard_node rclcpp mosim_msgs px4_msgs)

add_executable(fastlio_odometry_to_px4_visual_odometry_node src/fastlio_odometry_to_px4_visual_odometry_node.cpp)
target_compile_features(fastlio_odometry_to_px4_visual_odometry_node PUBLIC cxx_std_17)
ament_target_dependencies(fastlio_odometry_to_px4_visual_odometry_node rclcpp nav_msgs px4_msgs)

if(NOT DEFINED MOSIM_POSITION_OUTER_CODE_DIR)
  if(DEFINED ENV{MOSIM_PROJECT_ROOT})
    set(MOSIM_POSITION_OUTER_CODE_DIR
      "$ENV{MOSIM_PROJECT_ROOT}/Results/generated_mworks/AWFF_PositionOuterLoop_Sysblock_20260620_070500/QuadrotorControllerBlocks.AWFF_PositionOuterLoop_Sysblock"
    )
  else()
    set(MOSIM_POSITION_OUTER_CODE_DIR
      "${CMAKE_CURRENT_SOURCE_DIR}/../../../Results/generated_mworks/AWFF_PositionOuterLoop_Sysblock_20260620_070500/QuadrotorControllerBlocks.AWFF_PositionOuterLoop_Sysblock"
    )
  endif()
endif()
set(MOSIM_POSITION_OUTER_CODE_DIR "${MOSIM_POSITION_OUTER_CODE_DIR}" CACHE PATH "MWORKS generated AWFF position outer-loop C code directory")

add_executable(position_outer_loop_to_px4_attitude_node
  src/position_outer_loop_to_px4_attitude_node.cpp
  "${MOSIM_POSITION_OUTER_CODE_DIR}/AWFF_PositionOuterLoop_Sysblock.c"
  "${MOSIM_POSITION_OUTER_CODE_DIR}/AWFF_PositionOuterLoop_Sysblock_data.c"
)
target_compile_features(position_outer_loop_to_px4_attitude_node PUBLIC cxx_std_17)
target_include_directories(position_outer_loop_to_px4_attitude_node PRIVATE "${MOSIM_POSITION_OUTER_CODE_DIR}")
ament_target_dependencies(position_outer_loop_to_px4_attitude_node rclcpp mosim_msgs px4_msgs)

install(TARGETS
  planner_setpoint_to_px4_offboard_node
  fastlio_odometry_to_px4_visual_odometry_node
  position_outer_loop_to_px4_attitude_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
