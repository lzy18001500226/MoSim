# Flight Console QGC D2 Preflight

Status: `blocked`

The official QGroundControl `v5.0.8` source and its declared ArduPilot parameter
submodule were resolved to immutable commits, downloaded through official
GitHub archives, checksum-verified, and materialized in the project-owned
`apps/flight_console/vendor/qgroundcontrol/` directory without nested Git
metadata.

The current machine cannot run the required unmodified Windows build gate:

- QGC requires Qt 6.8.3; only Qt 5.15.2 is currently installed.
- Ninja is missing.
- Visual Studio 2022 C++ Build Tools are missing.
- Windows SDK is missing.
- GStreamer is missing; it can be disabled for the first non-video baseline.

Installing Visual Studio Build Tools and Windows SDK is a machine-level
infrastructure action and was not performed implicitly. Source-only
Orchestrator and custom-layer work may continue, but D2 remains blocked until a
real QGC Windows binary builds and starts.
