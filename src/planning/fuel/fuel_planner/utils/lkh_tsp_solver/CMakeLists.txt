cmake_minimum_required(VERSION 2.8.3)
project(lkh_tsp_solver)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()
set(CMAKE_CXX_FLAGS "-std=c++11")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall")

find_package(catkin REQUIRED COMPONENTS
  roscpp
)

catkin_package(
 INCLUDE_DIRS include
 LIBRARIES lkh_tsp_solver
 CATKIN_DEPENDS roscpp
#  DEPENDS system_lib
)

include_directories( 
    SYSTEM 
    include 
)

file( GLOB SRCS src/*.c )

# message("${SRCS}")

add_library( lkh_tsp_solver 
  ${SRCS}
  src/lkh_interface.cpp
)
target_link_libraries(lkh_tsp_solver -lm)

option(FUEL_BUILD_TEST_TOOLS "Build upstream FUEL test/helper executables" OFF)

if(FUEL_BUILD_TEST_TOOLS)
  add_executable( lkh_tsp 
    ${SRCS}
  )
  target_link_libraries(lkh_tsp ${catkin_LIBRARIES} -lm)
endif()
