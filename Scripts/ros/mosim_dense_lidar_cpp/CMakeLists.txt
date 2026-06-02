cmake_minimum_required(VERSION 3.8)
project(mosim_dense_lidar_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(dense_lidar_replay_node src/dense_lidar_replay_node.cpp)
target_compile_features(dense_lidar_replay_node PUBLIC cxx_std_17)
ament_target_dependencies(dense_lidar_replay_node rclcpp sensor_msgs std_msgs)

install(TARGETS dense_lidar_replay_node DESTINATION lib/${PROJECT_NAME})

ament_package()
