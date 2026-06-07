cmake_minimum_required(VERSION 3.8)
project(mosim_setpoint_adapter)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(mosim_msgs REQUIRED)

add_executable(planner_setpoint_adapter_node src/planner_setpoint_adapter_node.cpp)
target_compile_features(planner_setpoint_adapter_node PUBLIC cxx_std_17)
ament_target_dependencies(planner_setpoint_adapter_node rclcpp std_msgs mosim_msgs)

add_executable(position_command_to_planner_setpoint_node src/position_command_to_planner_setpoint_node.cpp)
target_compile_features(position_command_to_planner_setpoint_node PUBLIC cxx_std_17)
ament_target_dependencies(position_command_to_planner_setpoint_node rclcpp std_msgs mosim_msgs)

install(TARGETS
  planner_setpoint_adapter_node
  position_command_to_planner_setpoint_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
