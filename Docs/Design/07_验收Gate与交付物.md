# 07 验收 Gate 与交付物

Status: source design, 2026-06-10.

## 1. Gate Principle

Every acceptance claim needs evidence. A run is accepted only for the claim its
evidence can support.

Examples:

- nonzero FAST-LIO topics do not prove planner readiness;
- UE visual playback does not prove controller performance;
- MWORKS simulation results do not prove UE material acceptance;
- QGC status does not prove MWORKS metrics;
- truth-debug localization does not prove sensor-based localization.

## 2. Competition Control-Closure Gates

### Gate C0-A: MWORKS Plant And Control

Required evidence:

- model check or equivalent source/static gate;
- one short plant/controller run;
- controller input/output trace;
- plant truth state;
- actuator/motor model provenance labels;
- metrics for the claim being made.

### Gate C0-B: Official PID Baseline Coverage

Required evidence:

- Tongyuan-provided plant/controller case is labelled as the official baseline
  or the deviation from that case is documented;
- baseline controller id, parameter profile, and scenario config;
- hover or steady-hold trace;
- step-response trace for at least one controlled channel;
- spiral-climb trace;
- figure-8 trace;
- exported raw traces suitable for Syslab metric calculation;
- baseline limitation notes are tied to observed data, not visual impression.

This gate proves the reference point for later controller optimization. It does
not prove that any optimized controller is accepted.

### Gate C0-C: Syslab Metric Contract

Required metric capability:

- RMSE and maximum tracking error;
- steady-state error;
- overshoot and settling time for step-like commands;
- controller effort and saturation indicators;
- robustness comparison under at least one labelled perturbation, wind
  disturbance, or external disturbance scenario when robustness is claimed.

Required evidence:

- metric script or Syslab workflow reference;
- source trace labels and scenario id;
- controller id and parameter profile;
- metric output file with enough metadata to compare baseline and optimized
  runs.

This gate is about functional support for quantitative comparison. It is not a
requirement to write the final comparison report in this design document.

### Gate C0-D: Sensor Observation Boundary

Required evidence:

- sensor profile;
- timestamp and frame rules;
- extrinsic/source labels;
- proof that planner does not consume hidden global scene truth for final
  evidence;
- visual or file evidence for sensor generation route.

### Gate C0-E: Localization / Local Map / Planner Path

Required evidence depends on backend:

- truth-debug backend: label as debug only;
- FAST-LIO/ROS2 backend: topic rates, TF/extrinsic, nonzero outputs, and
  truth-error or quality evaluation;
- native backend: equivalent odometry/local-map validity evidence.

For ROS2/FAST-LIO map/world grounding, source/static repair readiness is not
acceptance. The accepted live evidence must show the same-run raw TF/static-TF
chain from `camera_init` to `map`, `world`, or `ue_world`. If the latest live
evidence only shows `camera_init->body` and no grounding chain, planner or
controller handoff remains blocked.

Planner evidence:

- setpoint or trajectory trace;
- local-map/odometry source;
- stale/fallback status;
- no direct global-truth shortcut.

### Gate C0-F: FlightControlAdapter

Required evidence:

- selected active backend;
- 20Hz target or measured setpoint stream;
- stale-command timeout;
- accepted/rejected command echo where UI/automation requests are used;
- control status and failsafe status.
- when ROS2/planner handoff is claimed, the controller input must pass through
  the shared controller ABI rather than backend-specific MWORKS variable names.

For UE command/echo surfaces, source/static build-readiness means only that a
future build-only gate may be separately authorized. It is not build success,
live runtime ack, MWORKS downlink, ROS2 runtime echo, final UI acceptance,
planner readiness, controller performance, mission success, or closed-loop
evidence.

### Gate C0-G: Evidence Bundle

Required evidence:

```text
RUN_MANIFEST
CONFIG_SNAPSHOT
model/source labels
sensor/log outputs
planner setpoint trace
controller/plant trace
metrics
screenshots/video where visual claims are made
acceptance or blocker note
```

## 3. Competition Optimized-Control Gates

Optimized-control acceptance requires repeatability and backend switching within
the competition scope:

- multiple controller configurations through the same interface;
- at least one Sysblock optimized controller can replace the official PID
  baseline in the MWORKS UAV model;
- optimized controller evidence includes controller input/output traces,
  plant truth traces, actuator/saturation state, and Syslab metrics;
- candidate algorithm labels match the implemented design route, such as
  improved PID, PID-INDI/INDI, MPC/NMPC, sliding-mode, fuzzy correction, neural
  compensation, or composite control;
- at least one credible local-map/planner path;
- scene/sensor profile switching without truth leakage;
- UE command/echo surface if a UI claim is made;
- automated metric generation;
- report asset export.

### Gate C1-A: Optimized Sysblock Controller

Required evidence:

- graphical Sysblock model or Sysblock-compatible module for the optimized
  controller when graphical controller structure is claimed;
- stable adapter to the baseline flight-control interface or a typed adapter
  documenting every changed signal;
- if full-system execution uses an Equation controller because graphical
  Sysblock embedding is blocked, the run bundle must declare the Equation
  backend and provide behavior-equivalence evidence or an explicit equivalence
  review target against the graphical controller;
- closed-loop MWORKS run on at least one baseline scene;
- comparative metrics against the official PID baseline;
- fallback or stop condition for unstable candidate behavior;
- codegen/SIL equivalence only when generated C/C++ runtime authority is
  claimed. Current MWORKS-native simulation does not require generated C/C++.

### Gate C1-B: Robustness Function

Required evidence when robustness is claimed:

- nominal baseline and optimized runs;
- at least one parameter perturbation, wind disturbance, or external
  disturbance run;
- metric output for performance retention, recovery time, steady-state error,
  RMSE, and saturation/effort;
- event labels showing when the disturbance or perturbation was active.

## 4. Competition Formation Gates

Formation acceptance is part of competition closure after the single-UAV
control line is stable:

- multi-UAV scenario identity is defined;
- each UAV has separated truth, controller, and evidence traces;
- formation route and safety constraints are declared.

### Gate C2-A: Formation Control

Required evidence:

- multi-UAV scenario id and per-UAV run identity;
- `swarm_id`, `formation_id`, `uav_count`, and `uav_id` in the run manifest;
- formation route, with leader-follower as the minimum accepted route;
- target formation geometry and per-UAV reference traces;
- per-UAV controller traces and plant truth traces;
- formation error metric;
- minimum inter-UAV distance;
- collision/safety status;
- communication delay/dropout labels if they are part of the scenario.
- result layout that keeps each UAV's raw trace, controller trace, plant truth,
  and metrics inspectable by `uav_id`.

Formation acceptance proves only the specific formation route and scenario that
the evidence covers. It does not prove general swarm autonomy or final
multi-UAV product readiness.

Formation acceptance must not be based on animation alone, copied single-UAV
metrics, merged traces without `uav_id`, ROS2 topic presence without same-run
namespace/frame evidence, or database rows without raw trace and manifest
references.

## 5. Post-Competition Extension Gates

Post-competition acceptance requires migration-ready external stack integration:

- PX4 Offboard/SITL/HIL backend defined and tested for the stated scope;
- QGC monitoring only for PX4/QGC claims;
- MAVLink/DDS/ROS2 route evidence where used;
- hardware or real-sensor replay evidence where claimed;
- safety/failsafe behavior under latency, dropout, invalid estimator, or
  geofence/collision conditions.

## 6. Deliverables

Design deliverables:

- system design source documents;
- interface/schema definitions;
- ADRs for accepted/rejected architecture routes;
- scenario and backend capability maps.

Runtime deliverables:

- run manifest;
- config snapshot;
- official PID baseline run bundle;
- Sysblock optimized-controller model evidence where controller optimization
  is claimed;
- Equation controller run evidence where it is the declared current executable
  backend;
- generated C/C++ artifacts only where generated-runtime, SIL/HIL, PX4, or
  external deployment claims are made;
- controller ABI wrapper evidence where ROS2/PX4/generated-runtime/Simulink
  replacement claims are made;
- MWORKS result files;
- ROS2 bag or topic summary where ROS2 is used;
- FAST-LIO/localization outputs where localization is claimed;
- planner traces;
- Syslab or equivalent labelled metrics;
- formation traces and metrics where formation is claimed;
- figures;
- screenshots and videos;
- blocker or acceptance record.

Report deliverables:

- method description;
- architecture diagram;
- controller/planner/sensor evidence;
- metrics tables and plots;
- scenario videos;
- competition limitations and post-competition extension notes.

## 7. Failure And Blocker Rules

Return a blocker instead of stretching evidence when:

- a backend is missing;
- frames or timestamps are inconsistent;
- localization is truth-debug but final localization evidence is requested;
- planner consumed global truth unexpectedly;
- MWORKS model or plant evidence is unavailable;
- UE/ROS2/PX4/QGC surface proves only UI status, not the requested technical
  claim;
- a claim requires manual visual review and no reviewed artifact exists.

## 8. Minimum Useful Run Bundle

A minimum useful bundle should answer:

```text
What ran?
Which backend owned control?
Which backend generated observations?
Which backend localized and built local map?
Which planner generated setpoints?
Which parameters and sources were used?
What metrics and logs were produced?
What claim does this evidence support?
What claim remains blocked or unproven?
```
