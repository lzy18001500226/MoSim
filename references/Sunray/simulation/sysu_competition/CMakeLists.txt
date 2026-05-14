cmake_minimum_required(VERSION 3.0.2)
project(sysu_competition)

find_package(catkin REQUIRED COMPONENTS
  message_generation  
  gazebo_msgs
  gazebo_plugins
  gazebo_ros
  roscpp
  roslib
  rospy
  geometry_msgs
  nav_msgs
  sensor_msgs
  std_msgs
  std_srvs
  tf
  mavros_msgs
  tf2_ros
  tf2_eigen
  sunray_msgs
  tf2_geometry_msgs
  # serial
)

find_package(Boost REQUIRED COMPONENTS system)

## Generate added messages and services with any dependencies listed here
generate_messages(
  DEPENDENCIES
  geometry_msgs 
  nav_msgs
  sensor_msgs
  std_msgs
)


catkin_package(
  INCLUDE_DIRS include
  CATKIN_DEPENDS message_runtime
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(
  include
  src
  ${catkin_INCLUDE_DIRS}
  ${PROJECT_SOURCE_DIR}/../../General_Module/sunray_common/common_lib
)

###############################
##      声明可执行cpp文件     ##
###############################
add_library(gazebo_model src/gazebo_model.cpp)
add_executable(gazebo_model_node src/gazebo_model_node.cpp)
add_dependencies(gazebo_model_node sysu_competition_gencpp)
target_link_libraries(gazebo_model_node ${catkin_LIBRARIES} gazebo_model)

## Mark cpp header files for installation
install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
  FILES_MATCHING PATTERN "*.h"
)

## Mark other files for installation (e.g. launch and bag files, etc.)
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)