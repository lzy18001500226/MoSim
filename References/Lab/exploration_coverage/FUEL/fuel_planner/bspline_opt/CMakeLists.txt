cmake_minimum_required(VERSION 2.8.3)
project(bspline_opt)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()
set(CMAKE_CXX_FLAGS "-std=c++11")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall")

find_package(Eigen3 REQUIRED)
find_package(PCL 1.7 REQUIRED)

set(NLOPT_ROOT "$ENV{NLOPT_ROOT}" CACHE PATH "NLopt install prefix")
find_path(NLOPT_INCLUDE_DIR
  NAMES nlopt.hpp nlopt.h
  HINTS
    "${NLOPT_ROOT}/include"
    "/usr/local/include"
    "/usr/include"
)
find_library(NLOPT_LIBRARY
  NAMES nlopt
  HINTS
    "${NLOPT_ROOT}/lib"
    "${NLOPT_ROOT}/lib64"
    "/usr/local/lib"
    "/usr/lib/x86_64-linux-gnu"
    "/usr/lib"
)
if(NOT NLOPT_INCLUDE_DIR OR NOT NLOPT_LIBRARY)
  message(FATAL_ERROR "NLopt not found. Install NLopt or set NLOPT_ROOT to a prefix containing include/nlopt.hpp and lib/libnlopt.so")
endif()

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  visualization_msgs
  plan_env
  active_perception
  cv_bridge
)

catkin_package(
 INCLUDE_DIRS include
 LIBRARIES bspline_opt
 CATKIN_DEPENDS plan_env active_perception
)


include_directories( 
    SYSTEM 
    include 
    ${catkin_INCLUDE_DIRS}
    ${Eigen3_INCLUDE_DIRS} 
    ${PCL_INCLUDE_DIRS}
    ${NLOPT_INCLUDE_DIR}  
)

add_library( bspline_opt 
    src/bspline_optimizer.cpp 
    )
target_link_libraries( bspline_opt
    ${catkin_LIBRARIES} 
    ${NLOPT_LIBRARY}   
    )
