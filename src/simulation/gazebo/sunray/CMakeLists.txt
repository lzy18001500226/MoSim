cmake_minimum_required(VERSION 2.8.3)
project(sunray_simulator)

find_package(catkin REQUIRED COMPONENTS
  gazebo_dev
  gazebo_msgs
  gazebo_ros
  message_generation      
  roscpp
  geometry_msgs
  nav_msgs
  sensor_msgs
  std_msgs
  sunray_msgs
  pcl_conversions
  pcl_ros
  laser_geometry
)

## System dependencies are found with CMake's conventions
find_package(Boost REQUIRED COMPONENTS system)

catkin_package(
  INCLUDE_DIRS include
  CATKIN_DEPENDS gazebo_msgs laser_geometry nav_msgs message_runtime roscpp std_msgs sunray_msgs tf
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)
###############################
##      声明可执行cpp文件     ##
###############################
add_executable(set_model_state_example src/set_model_state_example.cpp)
add_dependencies(set_model_state_example ${catkin_EXPORTED_TARGETS})
target_link_libraries(set_model_state_example ${catkin_LIBRARIES})

add_executable(ugv_circle src/ugv_circle.cpp)
add_dependencies(ugv_circle ${catkin_EXPORTED_TARGETS})
target_link_libraries(ugv_circle ${catkin_LIBRARIES})

## Mark cpp header files for installation
install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
  FILES_MATCHING PATTERN "*.h"
)

## Mark other files for installation (e.g. launch and bag files, etc.)
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)
