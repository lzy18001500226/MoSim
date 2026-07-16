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
