cmake_minimum_required(VERSION 3.0.2)
project(murder)

add_definitions(-std=c++14)
set(CMAKE_BUILD_TYPE Release)

find_package(catkin_simple REQUIRED)
catkin_simple(ALL_DEPS_REQUIRED)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

cs_add_library(murder src/murder.cpp)

cs_add_library(${PROJECT_NAME}_fsm src/murderFSM.cpp)
target_link_libraries(${PROJECT_NAME}_fsm
    ${catkin_LIBRARIES} murder )

cs_add_executable(murder_node src/murder_node.cpp)

target_link_libraries(murder_node
    ${catkin_LIBRARIES} ${PROJECT_NAME}_fsm)
##########
# EXPORT #
##########
cs_install()
cs_export()