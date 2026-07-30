cmake_minimum_required(VERSION 3.16)

project(mosim_px4ctrl_codegen LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(PX4CTRL_WRAPPER_SOURCE px4ctrl_graphical_generated_shared.c)

add_library(px4ctrl_graphical_generated_static STATIC ${PX4CTRL_WRAPPER_SOURCE})
add_library(px4ctrl_graphical_generated_shared SHARED ${PX4CTRL_WRAPPER_SOURCE})
set_target_properties(px4ctrl_graphical_generated_shared PROPERTIES
  OUTPUT_NAME px4ctrl_graphical_generated)

foreach(target IN ITEMS px4ctrl_graphical_generated_static px4ctrl_graphical_generated_shared)
  target_include_directories(${target} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
  if(UNIX)
    target_link_libraries(${target} PUBLIC m)
  endif()
  if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
  endif()
endforeach()

add_executable(test_px4ctrl_c test_px4ctrl_c.c)
target_link_libraries(test_px4ctrl_c PRIVATE px4ctrl_graphical_generated_static)
if(UNIX)
  target_link_libraries(test_px4ctrl_c PRIVATE m)
endif()
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(test_px4ctrl_c PRIVATE -Wall -Wextra -Wpedantic)
endif()

enable_testing()
add_test(NAME px4ctrl_c_fixed_vector COMMAND test_px4ctrl_c)
