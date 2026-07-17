cmake_minimum_required(VERSION 3.0.2)
project(mosim_gazebo_ftc_actuator_plugin)

find_package(catkin REQUIRED COMPONENTS gazebo_ros roscpp std_msgs)
find_package(gazebo REQUIRED)

catkin_package(LIBRARIES mosim_gazebo_ftc_actuator_plugin)

include_directories(${catkin_INCLUDE_DIRS} ${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

add_library(mosim_gazebo_ftc_actuator_plugin SHARED src/ftc_actuator_plugin.cpp)
target_compile_features(mosim_gazebo_ftc_actuator_plugin PRIVATE cxx_std_14)
target_link_libraries(mosim_gazebo_ftc_actuator_plugin ${catkin_LIBRARIES} ${GAZEBO_LIBRARIES})

install(TARGETS mosim_gazebo_ftc_actuator_plugin
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION})
