set(QGC_APP_NAME "MoSimFlightConsole" CACHE STRING "CMake-safe app target name" FORCE)
# QGC v5.0.8 leaves this dependency on main. Use the private, hash-verified
# source installed by install_flight_console_toolchain.ps1.
get_filename_component(MOSIM_PROJECT_ROOT "${CMAKE_SOURCE_DIR}/../../../.." ABSOLUTE)
set(MOSIM_PX4_GPSDRIVERS_SHA "8fdef3bc0cb7820119abdb7320ad3992af2e440f")
set(MOSIM_PX4_GPSDRIVERS_SOURCE
    "${MOSIM_PROJECT_ROOT}/.tools/flight-console/sources/PX4-GPSDrivers-${MOSIM_PX4_GPSDRIVERS_SHA}"
)
if(NOT EXISTS "${MOSIM_PX4_GPSDRIVERS_SOURCE}/src/ubx.h")
    message(FATAL_ERROR
        "Pinned PX4-GPSDrivers source is missing. Run Scripts/ui/install_flight_console_toolchain.ps1"
    )
endif()
set("CPM_px4-gpsdrivers_SOURCE" "${MOSIM_PX4_GPSDRIVERS_SOURCE}")
set(QGC_DISABLE_APM_MAVLINK ON CACHE BOOL "Disable APM dialect" FORCE)
set(QGC_DISABLE_APM_PLUGIN ON CACHE BOOL "Disable APM plugin" FORCE)
set(QGC_DISABLE_APM_PLUGIN_FACTORY ON CACHE BOOL "Disable APM plugin factory" FORCE)
