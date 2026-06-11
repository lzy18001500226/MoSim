cmake_minimum_required(VERSION 3.10.2 FATAL_ERROR)

#============================================================================
# Initialize the project
#============================================================================
project(ignition-pkg-create VERSION 1.0.0)

#============================================================================
# Find ignition-cmake
#============================================================================
# If you get an error at this line, you need to install ignition-cmake
find_package(ignition-cmake2 2.14.0 REQUIRED)
ign_find_package(TINYXML2 REQUIRED PRIVATE PRETTY tinyxml2)
ign_find_package(ignition-tools
  REQUIRED
  PKGCONFIG "ignition-tools")

find_program(HAVE_IGN_TOOLS ign)
set(IGN_TOOLS_VER 1)

#============================================================================
# Configure the project
#============================================================================
set(c++standard 17)
ign_configure_project(VERSION_SUFFIX)

#============================================================================
# Configure the build
#============================================================================
ign_configure_build(QUIT_IF_BUILD_ERRORS)

#============================================================================
# Create package information
#============================================================================
ign_create_packages()

#============================================================================
# Configure documentation
#============================================================================
# configure_file(${CMAKE_SOURCE_DIR}/api.md.in ${CMAKE_BINARY_DIR}/api.md)
# configure_file(${CMAKE_SOURCE_DIR}/tutorials.md.in ${CMAKE_BINARY_DIR}/tutorials.md)

# ign_create_docs(
#   API_MAINPAGE_MD "${CMAKE_BINARY_DIR}/api.md"
#   TUTORIALS_MAINPAGE_MD "${CMAKE_BINARY_DIR}/tutorials.md")
