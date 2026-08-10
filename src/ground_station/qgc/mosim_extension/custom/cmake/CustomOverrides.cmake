set(MOSIM_QGC_AUDIT_APP_NAME "" CACHE STRING "Optional isolated MoSim QGC audit identity")
if(MOSIM_QGC_AUDIT_APP_NAME)
    if(NOT MOSIM_QGC_AUDIT_APP_NAME STREQUAL "MoSimGroundControlAudit")
        message(FATAL_ERROR "Unsupported MoSim QGC audit identity: ${MOSIM_QGC_AUDIT_APP_NAME}")
    endif()
    set(QGC_APP_NAME "${MOSIM_QGC_AUDIT_APP_NAME}" CACHE STRING "CMake-safe app target name" FORCE)
else()
    set(QGC_APP_NAME "MoSimGroundControl" CACHE STRING "CMake-safe app target name" FORCE)
endif()
set(QGC_STABLE_BUILD ON CACHE BOOL "Use the MoSim Ground Control product identity" FORCE)
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
