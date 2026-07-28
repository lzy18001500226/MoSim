# MoSim Flight Console

Flight Console is a QGroundControl custom build for MoSim experiment operation,
Factory 2D situational awareness, published-Profile selection, discrete fault
request staging, and evidence access. It renders copy-only foreground terminal
commands; it does not launch or supervise simulation processes.

Directory ownership:

```text
UPSTREAM.md                    frozen provenance and update policy
LICENSES/                      copied upstream license texts
vendor/qgroundcontrol/         immutable QGC source baseline
vendor/qgroundcontrol.SHA256SUMS
mosim/                         MoSim-owned UI and adapters
```

The current release exposes published one- and three-UAV Profiles. Unsupported
vehicle scales and controllers without a compatible published Profile remain
visible but disabled. The active RunManifest locks the selected Profile.

The Windows baseline requires Qt 6.8.3, Ninja, Visual Studio 2022 C++ Build
Tools, a Windows SDK, and GStreamer 1.22.12. The current machine preflight is
recorded in `Results/ui_platform/flight_console_windows_toolchain_preflight.json`.

## MoSim custom build

The project-owned QGroundControl custom build lives under:

```text
apps/flight_console/mosim/custom/
```

Materialize the generated overlay without editing upstream files:

```powershell
python Scripts/ui/materialize_qgc_custom_overlay.py
python Scripts/ui/generate_qgc_vendor_manifest.py --verify
```

The custom layer provides Factory Fly/Plan maps, published Profile selection,
rosbag-derived map replay, discrete fault request staging, and a visible
terminal-command area. QML does not execute arbitrary commands or publish
ROS/MAVROS setpoints. QGC does not depend on Orchestrator or embedded UE.

The D5 source gate is recorded at:

```text
Results/ui_platform/flight_console_d5_source_gate_20260717/GATE.json
```

The source/contract gate is not a Windows executable gate. The current
preflight is `status=ready`, and the 2026-07-28 Release build produced
`build/flight-console-qgc/Release/MoSimFlightConsole.exe`. This establishes
that the current custom source compiles and links on this machine. It does not
establish QGC, ROS, Gazebo, PX4, MAVROS, controller, planner, or flight-runtime
success.

Run the read-only preflight at any time:

```powershell
python Scripts/ui/check_qgc_windows_toolchain.py `
  --output Results/ui_platform/flight_console_windows_toolchain_preflight.json
```

When the preflight is `ready`, configure and build through the fixed project
entrypoint:

```powershell
powershell -ExecutionPolicy Bypass -File Scripts/ui/build_flight_console.ps1
```

The build entrypoint verifies the frozen upstream manifest and regenerates the
custom overlay before CMake. It never installs system software.

To start only the QGC operation surface after a successful build, use the
separate visible-terminal entrypoint:

```powershell
powershell -ExecutionPolicy Bypass -File Scripts/ui/run_flight_console.ps1
```

This starts no simulator. Runtime commands shown in Flight Console are copied
for the operator to run in a visible terminal; each ROS1/Gazebo/PX4/MAVROS/UE
runtime acceptance remains a separately authorized step.
