# MoSim Flight Console

Flight Console is a QGroundControl custom build for MoSim experiment operation,
telemetry, disturbance and fault injection, display-session management, and
evidence access.

Directory ownership:

```text
UPSTREAM.md                    frozen provenance and update policy
LICENSES/                      copied upstream license texts
vendor/qgroundcontrol/         immutable QGC source baseline
vendor/qgroundcontrol.SHA256SUMS
mosim/                         MoSim-owned UI and adapters
```

The first release enables the accepted three-UAV profile. Vehicle counts four
through nine and controllers without accepted runtime evidence remain visible
but blocked by the Orchestrator capability registry.

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

The custom layer provides the Run, Telemetry, Injection, Displays, and Evidence
surfaces. It exposes accepted one- and three-UAV profiles while keeping UAV
counts four through nine and controllers without runtime evidence visible but
disabled. All experiment commands use the fixed project Orchestrator client;
QML does not execute arbitrary commands or publish ROS/MAVROS setpoints.

The D5 source gate is recorded at:

```text
Results/ui_platform/flight_console_d5_source_gate_20260717/GATE.json
```

The source/contract gate is not a Windows executable gate. Native configure is
currently blocked by missing Qt 6.8.3, Ninja, Visual Studio 2022 C++ Build
Tools, Windows SDK, and GStreamer. Installing these system dependencies requires
explicit infrastructure authorization.
