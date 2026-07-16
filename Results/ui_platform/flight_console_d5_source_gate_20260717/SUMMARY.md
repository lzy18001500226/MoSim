# Flight Console D5a Source Gate

Status: `source_ready_build_blocked`

MoSim Flight Console now uses the official QGroundControl `v5.0.8` custom-build
extension. Project-owned C++/QML source lives under
`apps/flight_console/mosim/custom/`; a controlled script materializes the
generated `vendor/qgroundcontrol/custom/` overlay. The frozen 2638-file upstream
manifest still verifies.

The custom layer implements Run, Telemetry, Injection, Displays, and Evidence
surfaces. One- and three-UAV `px4ctrl` profiles are selectable. UAV counts four
through nine and controllers without runtime evidence remain visible but
disabled. Commands use the fixed Orchestrator client and do not directly issue
ROS/MAVROS setpoints.

Eight targeted tests pass. CMake detects `Enabling custom build` and then stops
at the expected infrastructure gate because Ninja and a C/C++ compiler are not
installed. Qt 6.8.3, VS2022 C++ Build Tools, Windows SDK, and GStreamer are also
absent. This packet does not claim a native build or GUI runtime pass.
