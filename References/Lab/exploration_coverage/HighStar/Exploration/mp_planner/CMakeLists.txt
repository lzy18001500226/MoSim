cmake_minimum_required(VERSION 3.0.2)
project(mp_planner)

add_definitions(-std=c++14)
set(CMAKE_BUILD_TYPE Release)

find_package(catkin_simple REQUIRED)
catkin_simple(ALL_DEPS_REQUIRED)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

cs_add_library(${PROJECT_NAME} src/mp_planner.cpp)
cs_add_library(${PROJECT_NAME}_quick src/mp_planner_quick.cpp)

target_link_libraries(${PROJECT_NAME}
    ${catkin_LIBRARIES})
target_link_libraries(${PROJECT_NAME}_quick
    ${catkin_LIBRARIES})
##########
# EXPORT #
##########
cs_install()
cs_export()