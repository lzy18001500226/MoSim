# MoSim Ground Control

MoSim Ground Control is a QGroundControl custom build for MoSim experiment operation,
Factory 2D situational awareness, published-Profile selection, discrete fault
request staging, and evidence access. It renders copy-only foreground terminal
commands; it does not launch or supervise simulation processes.

Directory ownership:

```text
UPSTREAM.md                    retained legacy-vendor provenance and update policy
LICENSES/                      copied upstream license texts
vendor/qgroundcontrol/         retained rollback QGC snapshot, not active build source
vendor/qgroundcontrol.SHA256SUMS
mosim/                         retained rollback MoSim UI snapshot
```

The current release exposes published one- and three-UAV Profiles. Unsupported
vehicle scales and controllers without a compatible published Profile remain
visible but disabled. The active RunManifest locks the selected Profile.

The Windows baseline requires Qt 6.8.3, Ninja, Visual Studio 2022 C++ Build
Tools, a Windows SDK, and GStreamer 1.22.12. The current canonical-source
toolchain preflight is recorded in
`Results/static_audits/local_source_activation_20260801/QGC_WINDOWS_TOOLCHAIN_PREFLIGHT.json`.

## MoSim custom build

The active project-owned QGroundControl custom build lives under:

```text
src/ground_station/qgc/qgroundcontrol/
src/ground_station/qgc/mosim_extension/custom/
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
canonical-source preflight is `status=ready`, and a 2026-08-01 canonical
`-ConfigureOnly` run passed. Historical Release-build output from the retained
legacy vendor tree is not evidence that the canonical snapshot has completed a
full executable build. Neither result establishes QGC, ROS, Gazebo, PX4,
MAVROS, controller, planner, or flight-runtime success.

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

The build entrypoint verifies the canonical QGroundControl source manifest and
regenerates the custom overlay before CMake. It never installs system software.

To start only the QGC operation surface after a successful build, use the
separate visible-terminal entrypoint:

```powershell
powershell -ExecutionPolicy Bypass -File Scripts/ui/run_flight_console.ps1
```

This starts no simulator. Runtime commands shown in MoSim Ground Control are copied
for the operator to run in a visible terminal; each ROS1/Gazebo/PX4/MAVROS/UE
runtime acceptance remains a separately authorized step.
