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
Tools, and a Windows SDK. The current machine audit is recorded under
`Results/ui_platform/qgc_d2_gate_20260717/`.

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

The source/contract gate is not a Windows executable gate. The latest read-only
preflight found the existing VS2022 Community, MSVC, and Windows SDK 10.0.26100
toolchain. Native configure remains blocked by missing Qt 6.8.3, Ninja, and
GStreamer. Installing those system dependencies requires explicit
infrastructure authorization.

Run the read-only preflight at any time:

```powershell
python Scripts/ui/check_qgc_windows_toolchain.py `
  --output Results/ui_platform/flight_console_windows_toolchain_preflight.json
```

After the named dependencies have been installed, configure and build through
the fixed project entrypoint:

```powershell
powershell -ExecutionPolicy Bypass -File Scripts/ui/build_flight_console.ps1
```

The build entrypoint verifies the frozen upstream manifest and regenerates the
custom overlay before CMake. It never installs system software.
