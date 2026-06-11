add_subdirectory(msgs)

set_source_files_properties(
  ${PROTO_PRIVATE_SRC}
  ${PROTO_PRIVATE_HEADERS}
  PROPERTIES GENERATED TRUE
)

# Suppress compiler warnings in generated protobuf C++ code.
if(NOT MSVC)
  set_source_files_properties(
    ${PROTO_PRIVATE_SRC}
    COMPILE_FLAGS -Wno-unused-parameter
  )
endif()

set (sources
  ProcessManager.cc
  RegionTrigger.cc
  Scenario.cc
  Test.cc
  Trigger.cc
  TimeTrigger.cc
  Util.cc
  ${PROTO_PRIVATE_SRC}
)

# Create the library target
gz_create_core_library(SOURCES ${sources} CXX_STANDARD 17)
target_link_libraries(${PROJECT_LIBRARY_TARGET_NAME}
  PUBLIC
  gz-sim${GZ_SIM_VER}::gz-sim${GZ_SIM_VER}
  gz-utils${GZ_UTILS_VER}::cli
  gz-fuel_tools${GZ_FUEL_TOOLS_VER}::gz-fuel_tools${GZ_FUEL_TOOLS_VER}
  gz-msgs${GZ_MSGS_MAJOR_VER}::core
  gz-transport${GZ_TRANSPORT_MAJOR_VER}::core
  ${YAML_CPP_LIBRARIES}
  PRIVATE
  ${BACKWARD_LIBRARIES}
)
if (UNIX AND NOT APPLE)
  target_link_libraries(${PROJECT_LIBRARY_TARGET_NAME}
    PRIVATE stdc++fs)
endif()

target_compile_definitions(${PROJECT_LIBRARY_TARGET_NAME} PRIVATE ${BACKWARD_DEFINITIONS})

add_executable(gz-test main.cc)
target_include_directories(${PROJECT_LIBRARY_TARGET_NAME}
  PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
)
add_dependencies(${PROJECT_LIBRARY_TARGET_NAME}
  gz-test_private_msgs
)
target_link_libraries(gz-test
    ${PROJECT_LIBRARY_TARGET_NAME}
)

install (TARGETS gz-test DESTINATION ${BIN_INSTALL_DIR})
