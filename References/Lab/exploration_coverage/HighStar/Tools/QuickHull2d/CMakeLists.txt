cmake_minimum_required(VERSION 3.0.2)
project(quick_hull2d)

add_definitions(-std=c++14)
set(CMAKE_BUILD_TYPE Release)

find_package(catkin_simple REQUIRED)
catkin_simple(ALL_DEPS_REQUIRED)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

cs_add_library(${PROJECT_NAME} src/quick_hull2d.cpp)

cs_add_executable(demo_quickhull src/quick_hull2d_demo_node.cpp)

target_link_libraries(demo_quickhull
    ${catkin_LIBRARIES})# ${PROJECT_NAME})
##########
# EXPORT #
##########
cs_install()
cs_export()