# 11 RflySim式 MoSim 最小闭环架构审核

Status: active audit, 2026-06-06 CST.

Scope: respond to the user audit document `C:\Users\HP\Downloads\Mosim审核.md`
by checking current MoSim against an RflySim-like UAV simulation platform. This
document is a planning and gap-control artifact. It is not evidence that the
closed loop has already been implemented.

Authoritative boundary remains:

```text
MWORKS/Sysplorer/Syslab
  -> dynamics, controller, generated controller runtime, truth, metrics

UE5/MoSimSceneLibrary
  -> rendering, scene, camera, collision and sensor oracle, operator console

ROS2/RViz2/FAST-LIO/planner stack
  -> LiDAR, IMU, TF, odometry, local 3D map, planner review/runtime

CoAgent/WeChat/task packets
  -> sparse coordination, human review, recoverable dispatch state
```

RflySim, Gazebo/PX4, Sunray/YunZong, FAST-LIO, and EGO-Planner are reference
stacks. Reuse their role split, message/timing contracts, and failure modes;
do not copy their numeric parameters into Sunray150 truth.

## 1. Overall Conclusion

MoSim has a credible architecture direction, but it is not yet a complete
RflySim-like minimum closed-loop simulation platform.

Current completion level: **partial, implementation-ready but not product
closed-loop**.

Strong pieces already exist:

- strict authority boundary: MWORKS owns dynamics/control/truth/metrics, UE owns
  rendering and sensor oracle, ROS2 owns native robotics review;
- accepted Sunray150 rotor-center geometry from DAE/Blender audit;
- Gazebo/Sunray SDF parameter seeds are documented as `source=SDF_migration`;
- Factory FAST-LIO Gate B reached headless manual-review readiness in current
  docs, with the important limitation that final planner/controller performance
  is still open;
- MWORKS controller codegen/SIL path is credible for the PID demo scope;
- UE/RViz window split and RflySim-like experiment console direction are
  documented.

Main gaps:

- the full live loop `UE sensor -> ROS2 FAST-LIO/local map -> planner -> 20Hz
  MWORKS controller -> MWORKS plant -> UE/ROS2 feedback` is not yet implemented
  as one authoritative run;
- PX4/V6X access is still an adapter design, not an integrated SITL/HIL layer;
- current MWORKS QuadChassis baseline still lacks explicit command-to-speed
  mapping, motor lag, yaw reaction torque, rotor gyro moment, drag, and angular
  damping in the official plant path;
- UE command/uplink channel for controller/planner/fault/wind/scene switching
  is not implemented;
- EGO-style planner output is not yet wired into a 20Hz MWORKS setpoint adapter;
- cross-layer run identity, clocks, logs, and metrics are not unified enough for
  MIL/SIL/SITL/HIL migration claims.

Therefore the next phase should not start with broad UI polish or controller
retuning. It should first build the smallest honest closed loop and enforce the
data contracts that RflySim-like systems rely on.

## 2. Nine-Module Completion Table

| Module | RflySim-like target | Current MoSim state | Completion | Next gate |
|---|---|---|---:|---|
| M1 Architecture and authority split | Solver/control, renderer, robotics middleware, logs, and operator UI are separate processes with clear ownership. | Boundary is documented in `Docs/Design/10_架构边界与当前状态ADR.md` and this audit. | 70% | freeze one run-state schema shared by MWORKS, UE, ROS2, Results. |
| M2 Minimum closed loop | UE/env sensor data -> ROS2 localization/map/planner -> controller -> dynamics -> feedback to UE/ROS/PX4-style interface. | Headless evidence exists for slices; one live end-to-end loop is not complete. | 35% | run one Factory continuous loop with source labels and no pose overwrite. |
| M3 ROS2 perception, FAST-LIO, and planning | MID360-like LiDAR + 200Hz IMU + TF -> FAST-LIO odometry/cloud/path -> 3D local map -> EGO-style trajectory. | Factory Gate B is ready for manual review in docs; planner adapter and final 3D local-map integration remain open. | 45% | ROS2 bag/evidence with LiDAR/IMU/TF rates, FAST-LIO truth error, local 3D map, planner setpoint. |
| M4 MWORKS control layer | 20Hz setpoint/control contract, robust controller chain, codegen/SIL, safety/fault state machine. | PID-demo codegen/SIL path exists; target controllers and planner-fed setpoints need equivalence and run evidence. | 45% | planner-to-MWORKS setpoint adapter plus one hover/yaw/step closed-loop check. |
| M5 PX4/V6X access layer | Offboard, internal module, SITL/HIL, uXRCE-DDS/MAVLink semantics, failsafe and estimator-valid gates. | Design reference only; not required for first MWORKS-owned loop. | 15% | define adapter contract and first read-only SITL/HIL spike before implementation. |
| M6 Sunray150 dynamics and actuator model | mass/inertia, rotor layout, motor command mapping, lag, thrust, yaw moment, drag, sensors. | Rotor centers are accepted; mass/inertia/thrust/yaw/motor lag remain `source=SDF_migration`; baseline lacks several actuator terms. | 40% | project-owned experimental chassis/wrapper with motor lag + yaw torque + rotor-center moment checked in MWORKS. |
| M7 Fault and disturbance | motor degradation, wind gust, sensor fault, payload/mass profiles, event log, allocation reconfiguration. | Scenario/report concepts exist; product console and unified plant injection route are not finished. | 35% | fault/wind command packet accepted by MWORKS wrapper and echoed with event log. |
| M8 UE map, display, and virtual MID360 | scene/map switching, high-quality UAV/scene rendering, camera/video, collision/raycast sensor oracle. | scene/map registry and actor hooks exist; experiment console/uplink and production MID360 raycast route remain open. | 50% | UE console command-adapter smoke with accepted/rejected echo; no direct actor teleport. |
| M9 Communication, time, logs, metrics, migration | one clock domain, run_id, source labels, ROS bag/MSR/UE logs, metrics, MIL/SIL/SITL/HIL promotion gates. | Evidence conventions exist but are not yet a unified run bundle across layers. | 40% | one run directory containing MWORKS result, ROS bag/summary, UE event log, metrics, and audit status. |

## 3. Breakpoint Analysis

### Breakpoint A: There Is No Single Authoritative Live Closed Loop Yet

Current evidence proves important slices, but the platform still lacks one
routine that starts a scenario, binds `run_id/scene_id/map_id`, streams sensor
data, runs ROS2 localization/map/planning, feeds 20Hz setpoints into MWORKS,
and records one aligned result bundle.

Action: build the first Factory loop with explicit degraded scope if needed:
manual goal, one planner candidate, one controller, one short trajectory, one
run bundle.

### Breakpoint B: Dynamics Upgrade Is Required Before Control Claims Expand

The accepted DAE/Blender rotor centers are geometry only:

```text
rotor_0: ( 0.053745, -0.053740, -0.014052)
rotor_1: (-0.053761,  0.053760, -0.014052)
rotor_2: ( 0.053746,  0.053759, -0.014052)
rotor_3: (-0.053761, -0.053739, -0.014052)
```

They may correct rotor-arm moment geometry. They do not identify mass,
inertia, thrust coefficient, yaw coefficient, motor time constants, drag,
angular damping, or controller gains. Those values remain `source=SDF_migration`
unless a PX4 ULog/bench identification bundle exists.

Action: use a project-owned MWORKS experimental chassis/wrapper first. Minimum
upgrade: command-to-speed mapping, first-order motor lag, `Ct * omega^2`
thrust, `Cm * omega^2` yaw reaction torque, and rotor-center moment. Add gyro
moment and drag/damping after hover/yaw/step gates pass.

### Breakpoint C: PX4 Is a Contract Reference, Not Current Runtime Authority

RflySim often places PX4/CopterSim in the motion/control loop. MoSim currently
places MWORKS there. That is acceptable, but the external-control contract must
still look like a real flight-control stream: continuous 20Hz setpoints, stale
command timeout, estimator-valid state, failsafe/hover/land behavior, and
clear mode echo.

Action: keep PX4/V6X as P1/P2 adapter work. Do not block P0 on PX4, but do not
claim SITL/HIL until the adapter is actually exercised.

### Breakpoint D: ROS2 Review Must Stay Native

Point cloud, TF, FAST-LIO odometry/path, and local 3D map review belong in
RViz2 or equivalent native robotics windows. UE debug overlays and browser HTML
previews are not accepted active evidence.

Action: every localization/planning claim needs topic rates, timestamp checks,
extrinsics, FAST-LIO outputs, truth-error evaluation, and a native RViz2 review
gate.

### Breakpoint E: UE Console Needs an Authority-Preserving Command Channel

The desired RflySim-like UI is correct: inject motor fault, wind disturbance,
switch controller, switch planner, switch map, start/stop recording. The danger
is wiring buttons directly into UE actor transforms or hidden truth.

Action: implement:

```text
UE command packet
  -> MWORKS/ROS2 adapter validation
  -> accepted/rejected echo
  -> UE displays echoed state only
```

No direct UAV pose overwrite, no global UE map truth as planner input, no UE
pass/fail labels without MWORKS/ROS2 evidence.

## 4. P0 / P1 / P2 Roadmap

### P0: Minimum Usable Closed Loop

Goal: one honest Factory single-UAV run that proves the architecture loop and
data alignment.

Deliverables:

- unified run schema: `run_id`, `scene_id`, `map_id`, controller/planner/fault
  ids, source labels, evidence level;
- MWORKS experimental chassis/wrapper with motor lag, yaw reaction torque, and
  rotor-center force moment;
- formal `MoSimQuadrotorModel` package entry points that classify the previous
  `QuadrotorExperiments` pool instead of continuing to expand a flat
  experiment namespace;
- 20Hz MWORKS controller/setpoint adapter and stale-command handling;
- ROS2 sensor bridge with 200Hz IMU and 10Hz hardware-faithful Mid360 baseline;
- optional 20Hz LiDAR enhanced mode only after throughput and FAST-LIO quality
  gates pass;
- FAST-LIO/local-map/planner evidence bundle;
- UE Experiment Console design plus command-adapter smoke;
- RViz2 review configs for FAST-LIO and local map;
- one complete result bundle under `Results/`.

Exit condition: one short run has source-labeled MWORKS result, ROS2 topic/rate
summary, FAST-LIO truth error, planner/setpoint trace, UE/RViz review packet,
and known blockers.

### P1: RflySim-like Platform Features

Goal: make the loop usable for experiments rather than one scripted demo.

Deliverables:

- controller switch profiles: PID/AWFF/INDI/MPC candidate ids with accepted
  echo and fallback;
- planner switch profiles: waypoint, EGO-style local planner, trajectory
  smoothing, replanning enable;
- fault/wind/sensor injection profiles with event log;
- scene/map switching state machine and evidence gate;
- codegen/SIL equivalence for target controller candidates;
- PX4/V6X adapter contract spike: Offboard/SITL/HIL feasibility, not yet main
  runtime authority;
- run browser and metrics comparison in MoSim Studio.

Exit condition: at least three scenario types run through the same framework:
hover/yaw/step, local-map planning, and one wind/fault case.

### P2: Migration, Fleet, and Hardware Readiness

Goal: promote from platform demo to competition/report/hardware migration
track.

Deliverables:

- PX4/V6X/SITL/HIL adapter evidence where needed;
- parameter identification from PX4 ULog/bench data;
- multi-UAV formation and swarm planner integration;
- QGC/GCS-style supervision window for flight-control modes;
- reproducible experiment campaign runner and report automation;
- real/bench sensor calibration and MID360 extrinsic review.

Exit condition: claims can be mapped to MIL/SIL/SITL/HIL/real-test levels with
evidence and source labels.

## 5. Ten Tasks For The Minimum Usable Version

| # | Task | Owner stream | Output |
|---:|---|---|---|
| 1 | Freeze the unified run-state schema and command/echo packet fields. | ArchitectureIntegrator | `Config/runtime/run_state.schema.json` or design-equivalent doc plus tests. |
| 2 | Build MWORKS experimental Sunray150 chassis/wrapper with motor lag, yaw reaction torque, and rotor-center force moment. | MWORKS-Control | checked model, hover/yaw/step smoke evidence. |
| 3 | Promote useful `QuadrotorExperiments` entries into `MoSimQuadrotorModel` categories with old-name aliases kept until checks pass. | MWORKS-Control / MWORKS-ModelAudit | class mapping, package tree, targeted `check_model` plan, no broken scenario/script references. |
| 4 | Implement 20Hz planner/controller setpoint stream into MWORKS with stale-command handling. | MWORKS-Control / ROS2-FASTLIO | adapter trace and timeout test. |
| 5 | Produce ROS2 Factory sensor run with 200Hz IMU, 10Hz Mid360 baseline, TF, and monotonic timestamp gate. | ROS2-FASTLIO | bag summary and rate/timestamp report. |
| 6 | Run FAST-LIO truth-error gate and publish local 3D map/planner state in RViz2. | ROS2-FASTLIO | FAST-LIO/local-map evidence bundle. |
| 7 | Wire one planner output into the 20Hz MWORKS setpoint adapter without hand-rolled planner replacement. | ROS2-Planning | planner trace, setpoint trace, no global-truth input audit. |
| 8 | Implement UE Experiment Console command-adapter smoke for scene/controller/planner/fault/wind requests. | UE-ExperimentConsole | UI mock/spec plus command echo test. |
| 9 | Create one complete run bundle linking MWORKS result, ROS2 summary, UE event/status, metrics, and review packet. | Evidence-Report | `Results/<run_id>/RUN_MANIFEST.json`. |
| 10 | Dispatch and close department task packets with evidence, unknowns, risks, local sub-agent planning decisions, and next validation. | PMO / departments | ledger rows and result/blocker packets. |

### P0 Runtime Adapter Boundary

Existing UE navigation/control handoff artifacts are offline interface packages.
They are allowed to generate `PlannedQuinticReference` parameters and inactive
scenario drafts, but they are not a runtime ROS2 planner-to-MWORKS adapter.

For a P0 planner or closed-loop claim, the run manifest must show a real
runtime adapter trace:

```text
planner.setpoint_trace_source = RUNTIME_20HZ_ADAPTER
planner.setpoint_adapter_status = pass
planner.setpoint_rate_hz >= 19
planner.stale_command_timeout_s > 0
planner.global_truth_used_as_input = false
```

This prevents an offline `control_reference.csv` or UE truth-derived handoff
from being reported as the RflySim-like closed loop.

Current executable contract:

```text
Scripts/ros/planner_setpoint_adapter.py
```

This script converts runtime-style planner commands into a 20Hz trace and echo
log with stale-command handling. It is not a live ROS2 node yet. Its role is to
freeze the contract for the P0 ROS2 adapter and to keep the `RUN_MANIFEST`
checker honest while the compiled ROS2 implementation is added.

## 6. Sub-Agent Dispatch Plan

The main PMO thread remains accountable for integration and final acceptance.
Parallel work should be split by subsystem, not by vague "research".

| Packet | Stream | Write set | Stop condition |
|---|---|---|---|
| `RFLY-MOSIM-AUDIT-ROS-FASTLIO-20260606-001.json` | ROS2-FASTLIO | docs/results only unless explicitly upgraded | return topic/timing/planner gap report and P0 gate recipe. |
| `RFLY-MOSIM-AUDIT-MWORKS-CONTROL-20260606-001.json` | MWORKS-Control | project-owned experimental models and result evidence only | return checked wrapper/chassis plan and smoke-gate status. |
| `RFLY-MOSIM-AUDIT-PX4-SILHIL-20260606-001.json` | PX4-SILHIL | design/result packet only | return PX4/V6X adapter contract and P1/P2 feasibility blockers. |
| `RFLY-MOSIM-AUDIT-UE-FRONTEND-MAP-20260606-001.json` | UE-ExperimentConsole | UE docs/specs and command schema only | return console/map-switch UI architecture and no-teleport command path. |
| `RFLY-MOSIM-AUDIT-EVIDENCE-LOGGING-20260606-001.json` | Evidence-Report | run manifest schema, evidence docs, checks | return unified run bundle schema and metrics/log acceptance gates. |

Only the architecture-design visible thread is known at the time of this
audit. Other packets are ready for later department/thread dispatch or bounded
local sub-agent execution.

## 7. Non-Adoption Guardrails

Do not regress into:

- fake/static point clouds as mapping/localization evidence;
- fake 2D grid map as UAV local 3D map;
- keyboard/mouse pose overwrite as control;
- browser HTML point cloud as active review surface;
- UE debug overlay as replacement for RViz2;
- RflySim/Gazebo/AirSim sample numbers as Sunray150 identified truth;
- DAE MID360 mechanical mount center as FAST-LIO extrinsic;
- `TranslateModel` or one PID demo SIL as proof for all generated controllers;
- direct edits to the official QuadChassis baseline when a wrapper/experiment
  boundary is sufficient.

## 8. Immediate PMO Goal

Current goal:

```text
Build P0-Loop-1:
Factory scene, one Sunray150 vehicle, one short trajectory, one controller,
one ROS2 FAST-LIO/local-map/planner chain, one UE/RViz review packet, one
source-labeled run bundle.
```

Definition of done:

```text
MWORKS check/smoke ok
ROS2 topic/rate/time gate ok
FAST-LIO truth-error reported
planner setpoint stream recorded at 20Hz
UE command echo path smoke ok
run manifest links all evidence
open blockers are explicit
```
