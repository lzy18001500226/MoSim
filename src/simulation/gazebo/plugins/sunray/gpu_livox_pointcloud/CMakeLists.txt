cmake_minimum_required(VERSION 3.0.2)
project(mosim_gpu_livox_pointcloud)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(catkin REQUIRED COMPONENTS
  pcl_conversions
  roscpp
  sensor_msgs
)
find_package(gazebo REQUIRED)
find_package(PCL REQUIRED)

catkin_package(
  CATKIN_DEPENDS pcl_conversions roscpp sensor_msgs
  DEPENDS gazebo PCL
)

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${GAZEBO_INCLUDE_DIRS}
  ${PCL_INCLUDE_DIRS}
)
link_directories(${GAZEBO_LIBRARY_DIRS})

add_library(mosim_gpu_livox_pointcloud SHARED
  src/gpu_livox_pointcloud_plugin.cpp
)
target_link_libraries(mosim_gpu_livox_pointcloud
  ${catkin_LIBRARIES}
  ${GAZEBO_LIBRARIES}
  ${PCL_LIBRARIES}
  GpuRayPlugin
)
