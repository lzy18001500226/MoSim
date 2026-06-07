# Unreal Renderer Workflow

Unreal is the high-quality visual layer of the MoSim simulator product.
MWORKS/Sysplorer/Syslab remain the truth source for dynamics, control,
planning, collision checks, event logs, and metrics.

Current compact architecture boundary and Gate matrix entry:
`Docs/Design/10_架构边界与当前状态ADR.md`.

## Current Policy

The previous generated visual routes are retired:

- grid/STL/semantic-box maps;
- old MWORKS blockout maps as final visuals;
- RflySim `OldFactory` direct-open/direct-mount attempts;
- project-owned primitive factory review scenes;
- YunZong/Sunray primitive scene reconstruction;
- metadata-only migration-staging packages.

Do not spend more time polishing these routes. Keep them only as historical
lessons in `PROGRESS.md` or the task ledger when needed.

Current map work starts from real editable Unreal/Fab/Epic/open-source assets.
The target is an RflySim-like simulator experience, not a primitive blockout.
The map must first pass manual visual review as a believable physical-world
scene. Only after that should we reconnect quadrotor playback, radar overlays,
trajectory trails, MWORKS UDP streaming, planning truth, and video recording.

## 2026-06-02 Route Correction

User manual audit rejected the current hand-built RViz2 point-cloud/local-grid
display route. Do not continue polishing `publish_mosim_mapping_replay_ros2.py`,
project-authored local occupancy/voxel replay, browser previews, or RViz
display tuning as product work. These artifacts may remain as smoke/debug
references, but they are not accepted as the MoSim mapping/localization product
route.

The next implementation route is UAV-stack-first:

1. Study and reuse RflySim/native UAV simulator patterns before adding more
   visualization code.
2. Connect the UAV body/control/sensor interface first: MWORKS
   dynamics/controller/truth -> UE rendered vehicle/sensor source -> ROS2
   LiDAR/IMU topics.
3. Run upstream/native FAST-LIO and its own RViz/RViz2 configuration instead of
   hand-authoring a MoSim point-cloud/map display.
4. Only after the UAV and native FAST-LIO pipeline are connected should MoSim
   add wrappers, metrics, truth-error evaluation, and report evidence.

Any old section below that describes hand-built RViz2 mapping replay is
deprecated unless explicitly revalidated under this UAV-stack-first route.

## Factory-First UAV Body Gate

The current minimum review gate is Factory scene rendering plus a visible
YunZong/Sunray150 UAV body driven by the MWORKS/Bridge state path.

## RflySim-like Experiment Console

MoSim should provide a UE in-scene operator console similar in purpose to
RflySim's simulator front end: the user can start experiments, switch
controllers/planners, inject motor faults or wind disturbances, choose sensor
modes, and launch review/recording actions from the rendered simulator window.

Authority boundary:

- UE console owns operator intent, visible status, review ergonomics, and video
  capture.
- MWORKS owns controller selection, plant/fault/wind application, state truth,
  pass/fail metrics, and event logs.
- ROS2 owns planner selection, FAST-LIO/local-map runtime state, and RViz2
  review topics.
- UE must not directly teleport the UAV, overwrite MWORKS truth, feed full UE
  collision truth to planners, or label controller/planner success without
  MWORKS/ROS2 evidence.

Recommended first UI groups:

| Group | Controls | Confirmed state shown from |
|---|---|---|
| Scenario | scene, run id, start/goal, reset, pause/resume, record | MWORKS run state and UE renderer status |
| Controller | PID/AWFF/INDI/MPC/NMPC/L1/safety-filter selection, parameter profile | MWORKS/Sysblock or generated controller echo |
| Disturbance/Fault | wind profile, mass/payload profile, rotor efficiency/failure injection | MWORKS plant/fault wrapper echo |
| Planner | planner id, local-map source, goal queue, replan enable | ROS2 planner adapter and 20Hz setpoint stream health |
| Perception | LiDAR baseline/enhanced mode, IMU state, FAST-LIO candidate | ROS2 measured rates and FAST-LIO quality gate |
| Evidence | open RViz split layout, mark manual review, export run packet | evidence bundle and quality-status files |

Relationship to other review/control windows:

| Window | UE console relationship |
|---|---|
| MoSim Studio | UE console is the live rendered operation surface; Studio remains the batch experiment/result browser. |
| QGC/GCS-style window | Use only when a PX4/V6X/offboard adapter is active; display heartbeat/mode/failsafe, not MWORKS metrics. |
| RViz2 point-cloud/FAST-LIO | Open from UE/Studio as a review action, but the RViz window owns point-cloud/TF/odometry display. |
| RViz2 3D map/planner | Open from UE/Studio as a review action; planner state still comes from ROS2 topics. |
| Sysplorer/Syslab | Remain the model/result authority; UE only mirrors accepted runtime status. |

Department execution rule: `MoSim｜UE实验控制台与场景交互部` must plan every
non-trivial task with `department_local_goal`, `critical_path_steps`,
`parallelizable_slices`, `subagent_plan`, `subagent_plan_reason`,
`subagents_used`, `verification_gates`, and
`manual_review_or_blocker_triggers`. This is a planning requirement, not a
requirement to use at least one sub-agent. Disposable sub-agents may be used
only for bounded source/static/build/review slices; they are not durable UE
departments.

Each UE task must classify its scope before execution:

```text
source-static
build
editor/runtime
manual-review
```

The task packet must declare `expected_engineering_outputs` for that scope.
Completed UE work needs matching evidence: source/schema edits and tests,
build/log evidence, runtime command/echo/transport evidence, or review
screenshots/packets. Scene registry rows, schemas, JSON packets, and progress
notes are control-plane evidence; they are not runtime ack or visual
acceptance by themselves. If a review image/video/window is produced, ask PMO
to open/display it or send a concise review prompt rather than returning only
a path.

Recommended command/status route:

```text
UE operator action
  -> project command packet: requested_change, run_id, timestamp, source=UE_console
  -> MWORKS/ROS2 command adapter validates authority and current gate
  -> runtime applies or rejects the request
  -> next MWORKS/ROS2 status frame echoes active mode, reason, and evidence level
  -> UE console displays only echoed/confirmed state
```

Initial implementation should add a command schema and adapter smoke before a
full widget. The existing bridge already receives downlink fields such as
mission, motor command, controller mode, planner state, safety state, and
evidence level in `FQuadrotorMworksFrame`; the missing piece is a narrow uplink
command channel from UE to the MWORKS/ROS2 adapters.

Minimum command packet fields:

```text
schema: mosim.ue_command.v1
type: command
run_id
seq
time_s
requested_by: ue_experiment_console
command:
  kind: controller_select | planner_select | wind_profile | motor_fault |
        sensor_mode | scenario_reset | start_goal_update | recording
  payload: command-specific JSON object
guard:
  require_mworks_ack: true
  require_ros2_ack: true when planner/perception is touched
  reject_if_gate_open: named gate ids
```

Do not expose a UI button until its adapter can reject invalid requests and the
status frame can show the accepted state. For example, a "20Hz LiDAR" toggle
must show measured LiDAR/IMU rates and FAST-LIO gate status; it must not simply
change RViz or UE display rate.

### Scene And Map Switching UX

The user-facing map switcher should be designed as a stateful selector, not a
raw Unreal level dropdown. It should show at least:

- `scene_source_id`: editable asset source, Fab/Epic/local/reference provenance;
- `scene_id`: experiment scene identity used by scenarios and Results;
- `map_id`: renderer/planner/truth map identity;
- activation state: inactive, link-ready, UE-loaded, MWORKS-bound,
  ROS2-bound, headless-gate-passed, manual-review-ready;
- truth artifacts: collision/oracle JSON, local-map contract, FAST-LIO dataset
  availability;
- known blockers: black map, missing asset, primitive fallback, no truth export,
  no ROS2/FAST-LIO gate.

Expected switch flow:

```text
operator selects map card
  -> UE sends scene_switch request with scene_source_id/map_id/run_id
  -> scene adapter validates active_scene_links and registry entry
  -> UE loads or activates the render map
  -> MWORKS scenario binding is checked or generated
  -> ROS2 topic contract is selected for that scene
  -> headless gates run when required
  -> status frame echoes active scene/map/gate status
  -> UI enables review/run controls only for accepted states
```

Existing implementation hooks to reuse:

- `UE5/MoSimSceneLibrary/Content/MworksData/active_scene_links.json`;
- `UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json`;
- `UE5/MoSimSceneLibrary/Content/MworksData/unreal_scene_profiles.json`;
- `AQuadrotorMworksMapActor::ResolveMapId`;
- `AQuadrotorMworksMapActor::ResolveSceneSourceId`;
- `AQuadrotorMworksMapActor::ApplyFrameMapSelection`;
- `FQuadrotorMworksFrame.SceneId` and `FQuadrotorMworksFrame.MapId`.

Do not make map switching a visual-only UE operation. A selected UE map becomes
a valid simulation scene only when its MWORKS scenario, ROS2 topic contract,
truth artifacts, and evidence path are bound and echoed.

### Phased Implementation

1. Define command/status schemas for console actions, scene switching, and
   accepted-state echoes. Current P0 source: `Config/schemas/mosim_ue_command_v1.schema.json`
   and `Config/schemas/mosim_ue_command_echo_v1.schema.json`.
2. Add a minimal C++/Blueprint-callable UE command sender component. Current
   P0 source-level component:
   `UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h`
   and
   `UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp`.
3. Add an adapter smoke that accepts or rejects `controller_select`,
   `planner_select`, `wind_profile`, `motor_fault`, `sensor_mode`, and
   `scene_switch`. Current P0 source:
   `Scripts/UE5/smoke_ue_command_adapter.py`.
4. Build the first UMG/Slate panel with disabled states until ack is received.
5. Add scene cards using the existing scene registries and active links.
6. Add RViz/QGC/Studio launch buttons only as review/helper actions, never as
   substitute evidence.
7. Add evidence export and run packet display after MWORKS/ROS2 gates pass.

Current P0 status, 2026-06-06 CST:

- Source-level UE command sender contract passes
  `Scripts/UE5/check_ue_command_sender_contract.py`.
- UDP packet/transport loopback passes
  `Scripts/UE5/smoke_ue_command_sender_loopback.py`; the P0 bundle records
  `ue_command_sender_loopback_smoke.json` and received command JSONL.
- The sender builds and can UDP-send `mosim.ue_command.v1` packets for
  controller/planner/wind/fault/sensor/scenario/start-goal/recording/scene
  actions.
- The sender explicitly rejects `pose_override`, `teleport`, `set_uav_pose`,
  `actor_transform`, and `keyboard_pose`, and the source-level checker rejects
  direct Actor pose APIs in this component.
- This is not live UE Experiment Console evidence yet. Runtime acceptance still
  requires MWORKS/ROS2 `mosim.ue_command_echo.v1` rows and the P0 bundle keeps
  `not_runtime_ue_console=true` / `not_mworks_or_ros2_ack=true`.

## Sunray150 Material Review Rule

For Sunray150 appearance work, use the project skill
`Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md` before editing
Blender, DAE/FBX/glTF, UE materials, or material-generation scripts. That skill
is the current source of truth for component-first PBR texturing, material
library use, UV/atlas decisions, and audit gates.

Current accepted visual-asset route: use the DAE-derived Blender audit model as
the Sunray150 visual asset source line. The active review file is the
DAE-derived Blender scene under
`UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/`, currently
`sunray150_dae_mid360_realistic_material_audit.blend`. This confirms the route,
not final material acceptance. Primitive UAVs, temporary procedural aircraft,
and MWORKS STL animation remain forbidden as final vehicle visuals or review
evidence.

Current manual-review state: the USB camera lens/barrel overlay was removed
after user review because its position was wrong. The camera body remains a
black PartBody visual material, but the separate lens/barrel overlay should not
be regenerated unless a later reviewed geometry route places it correctly. The
MID-360 visual route currently uses a deep-blue mirror-coated dome plus white
strip reflection overlays for manual appearance review. These are visual/PBR
decisions only and must not change geometry assembly parameters, rotor centers,
mass, inertia, motor/thrust constants, FAST-LIO extrinsics, MWORKS/ROS2/UE
runtime behavior, controller, or planner evidence.

Do material work by component family, not by whole-aircraft renders first.
Whole-aircraft images are only final consistency checks after the individual
parts pass.

Required loop for each component family:

```text
identify physical part
  -> confirm source object names and reference images/docs
  -> research the single part's real product appearance before rendering
  -> assign material/texture only for that part family
  -> render isolated close-up audit image
  -> inspect for material realism and wrong fallback colors
  -> ask the user by WeChat if the part identity or physical role is unclear
```

Do not guess unknown parts from object names alone. If a part cannot be mapped
to a known Sunray150/MID-360/camera/PCB/motor/propeller/battery/connector
component with reasonable confidence, leave it neutral in the manifest and ask
for clarification through the project WeChat gateway before applying a final
material.

Material-library rule: prefer an existing PBR material/map set before manual
color tuning. A valid texture pass normally has albedo/base color, roughness,
normal/bump, and metallic when relevant. Color maps are sRGB; roughness,
metallic, AO, normal, height, and packed ARM maps are Non-Color data. If an STL
or DAE object lacks usable UVs for the needed detail, unwrap/atlas first
instead of painting broad procedural colors over the whole object.

For every reviewed part, first collect the real visual cues for that exact
component: material family, color, gloss/roughness, metal/plastic/glass
behavior, labels/markings, fasteners, connector faces, vents, seams, and
edge-wear. Only then tune Blender materials. Do not tune by whole-aircraft
appearance first.

Current component order is:

```text
MID-360 sensor and protection frame
carbon frame and plates
aluminum standoffs and steel fasteners
front/bottom cameras
electronics, connectors, and cables
motors and accepted tri-blade propellers
battery and payload blocks
landing gear and guards
whole-aircraft consistency render
```

Accepted UAV visual sources:

| Priority | Source | Notes |
|---|---|---|
| 1 | Imported UE StaticMesh generated from `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.fbx` or `.glb` | Required runtime vehicle visual. It must preserve the user-reviewed DAE-derived assembly, MID-360 placement, three-blade propellers, and material work. |
| Reference only | Source-model assets under `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360` plus the accepted Blender manifests | Allowed only for rebuilding or checking the DAE-derived UE asset. |
| Forbidden | MWORKS STL, MWORKS animation, runtime procedural vehicle mesh, primitive cube/cylinder UAV | Not accepted as UE runtime vehicle visuals or manual-review evidence. |

Primitive cube/cylinder UAV geometry is not accepted review evidence. The
default must keep fallback disabled. If the user sees a block/primitive UAV, or
if UE logs report that the DAE-derived StaticMesh asset is missing, treat the
stage as failed and import/fix the reviewed Sunray FBX/GLB asset path before
continuing. Do not fall back to MWORKS STL or MWORKS animation.

If the user reports a huge cylinder, broken/fragmented mesh, wrong scale, or
wrong initial position, the gate has failed. Do not ask for point-cloud,
FAST-LIO, or planner review. Diagnose with logs first:

```text
imported DAE-derived StaticMesh asset path
FBX/GLB source asset path and file size
imported mesh bounds and material slot count
BodyMesh visibility and hidden-in-game state
absence of primitive/STL vehicle fallback components
spawn transform and first UDP-driven transform
review camera initial transform
```

Before inventing a new UE/UAV behavior fix, check the local DAE-derived asset
route and its manifests first, then Sunray/YunZong SDF/mesh files for
dynamics/sensor references, then local RflySim/reference code for
renderer/simulation role split and review behavior. Only after those are
insufficient should the task go online for official docs or higher-quality
external references. Record the adopted pattern here or in `PROGRESS.md`
immediately.

Do not request manual review until the latest UE log confirms:

```text
vehicle loaded from the imported DAE-derived StaticMesh path
MWORKS STL/runtime animation fallback is not used
primitive cube/cylinder fallback is hidden
render-only helper geometry is disabled for the vehicle-visual gate
first UDP position maps to the accepted UAV task start
```

The bridge must fail loudly when the imported DAE-derived UE StaticMesh is
missing. Do not restore runtime STL loading, primitive geometry, or MWORKS animation as a
convenience fallback.

Build check note: when invoking Windows UnrealBuildTool from WSL, pass the
`.uproject` as a Windows path, for example from
`wslpath -w UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject`. Passing a raw
`/mnt/c/...` path to Windows UBT can be misread as `D:\mnt\c\...` and fail
before compilation. Prefer `Scripts/UE5/build_unreal_renderer.sh` or the same
Windows-path conversion when doing manual compile probes.

The review UAV initial position should match the accepted task start for this
gate. The review camera should start near that position but must not be placed
inside the UAV body. Keep a small camera offset so manual review can move
without the collision-constrained camera starting inside the vehicle or scene
geometry. If the UAV start changes, fix the replay CSV or spawn logic; if the
camera is trapped, fix the camera offset or collision radius, not the UAV
truth start.

For the vehicle-visual gate, the default review stream must not loop through
the old mission path. It should either hold the UAV at the first frame or run a
single bounded pose check, then stop. Continuous path replay belongs to later
controller/planner review after the vehicle visual gate is accepted.

The current Factory vehicle gate default is first-frame-only. Use
`STREAM_PATH_REPLAY=1` only after the vehicle body and propeller placement pass
manual review. If the user reports that the UAV runs to an old position or
loops a previous mission, treat that as a gate failure and return to the first
frame hold.

Propeller placement, MID-360 placement, heading, and materials for the current
UE vehicle visual must be traced to the user-reviewed DAE-derived assembly
manifests before tuning by eye. The MWORKS animation/STL route is forbidden as
a runtime or review vehicle visual source.

The current source split is:

```text
Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json
  -> accepted DAE-derived geometry manifest
  -> MWORKS/SDF rotor centers:
     rotor_0 front-right `{0.053745,-0.05374,-0.014052}`
     rotor_1 back-left `{-0.053761,0.05376,-0.014052}`
     rotor_2 front-left `{0.053746,0.053759,-0.014052}`
     rotor_3 back-right `{-0.053761,-0.053739,-0.014052}`
  -> camera candidates:
     front `{0,0.1032,0.0185,0,0,0}`
     down `{0,0.0145,-0.0263,0,1.5707963,3.14}`
  -> conservative base collision box:
     pose `{0,0.001574,0.044965,0,0,0}`
     size `{0.211502,0.214651,0.16193}`
References/MWORKS/QuadrotorModel/package.mo
  -> body `r_shape={0,0,0.0525}`
  -> rotor translations now follow the DAE-derived geometry manifest above
References/Sunray/.../sunray150_with_mid360.sdf
  -> body visual pose and rotor visual mesh/pose references
  -> UE visual component order: `rotor_0` front-right
     `{0.053745,-0.05374,-0.014052}`, `rotor_1` back-left
     `{-0.053761,0.05376,-0.014052}`, `rotor_2` front-left
     `{0.053746,0.053759,-0.014052}`, `rotor_3` back-right
     `{-0.053761,-0.053739,-0.014052}`
```

DAE-reviewed geometry can update rotor centers, camera candidate poses, and
collision envelopes. It must not update mass, inertia, thrust/motor constants,
controller gains, or sensor timing without separate identification evidence.

MID-360 has a stricter split. Do not write a DAE mechanical mount center into
FAST-LIO or call it "LiDAR extrinsic". Track these quantities separately:

```text
mechanical mount pose: physical fit of the MID-360 body to the frame
point-cloud coordinate origin: Livox O-XYZ frame used for point data
built-in IMU position: official Livox offset in point-cloud coordinates
FAST-LIO extrinsic_T: LiDAR pose in IMU body frame
Gazebo/Sunray sensor pose: local ray/IMU plugin pose inside livox_mid360.sdf
```

Official Livox Mid-360 manual evidence records the built-in IMU at
`(11.0, 23.29, -44.12) mm` in the point-cloud coordinate system, so the
corresponding FAST-LIO LiDAR pose in IMU body frame is
`[-0.011, -0.02329, 0.04412] m` when axes are aligned. The local Sunray
`livox_mid360.sdf` additionally places its ray sensor at `base_link` local
`z=0.1`. These are not interchangeable with the mechanical mount pose.

Retired MWORKS visual-frame notes, retained only to prevent parameter
cross-contamination:

```text
body lengthDirection={0,-1,0}, widthDirection={1,0,0}
UE visual yaw offset = -90 deg
do not apply body STL visual yaw to rotor FixedTranslation positions
```

Runtime rule: do not load MWORKS STL or replay MWORKS animation as the UE
vehicle visual. The current accepted runtime route is the imported
DAE-derived StaticMesh generated from
`UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.fbx`
or `.glb`. If that asset is not imported into UE Content, fail the vehicle
visual gate and import/fix the asset.

The current DAE-derived asset material work is based on local physical
component/material evidence:

```text
References/CUAV/Sunray150-正.png
References/CUAV/Sunray150-侧.png
References/MWORKS/QuadrotorModel/package.mo
References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/150.dae
```

Confirmed DAE component/material cues:

```text
MAIN_STRUCTURE / TOP_PANNEL: dark graphite
PROTECTIVE_RING / LAND_GEAR: dark grey
MID360_PROTECT_ARC*: dark grey / black protective bracket
MID360_PROTECT_ARC_CONNECTOR*: dark graphite connector blocks
MID-360 dome / optical surface cue: blue glass
propellers: translucent plastic/grey visual cue from the accepted tri-blade source mesh and physical references
```

This is review coloring, not an original manufacturer texture. Preserve the
imported asset's material slots in UE; the bridge must not overwrite the
vehicle StaticMesh with `BasicShapeMaterial`. If exact appearance is required,
revise the Blender/FBX/GLB source asset and re-import it into UE instead of
adding runtime heuristic coloring.

2026-06-02 Blender/DAE asset route: Blender MCP is available, but Blender 5.0
in this environment does not expose the Collada/DAE import operator. Do not
retry `bpy.ops.wm.collada_import`; it fails because the operator is missing.
The earlier local route was:

```text
Scripts/UE5/assets/build_sunray150_with_mid360_blender_asset.py
  reads References/Sunray/.../meshes/150.dae
  parses 701 named geometries and visual-scene instances
  groups them by physical role/material cue
  writes a Blender/FBX/glTF asset bundle
```

Treat this generated asset as a historical diagnostic artifact, not a final
vehicle source. It parsed only the UAV `150.dae` file and added supplemental
MID-360 base/dome proxy geometry, which the user rejected because the radar
base was not source-faithful.

2026-06-03 MID-360 DAE assembly audit rule: for
`sunray150_dae_mid360_full_assembly_audit.blend`, keep the aircraft frame,
brackets, MID-360 protection arcs, and non-propeller parts visible. Remove only
the user-confirmed DAE propeller blade and propeller-hub/fixing-node objects
before adding the standalone Livox MID-360 body:

```text
CircPattern.1 | CircPattern.1Mesh
CircPattern.1_ncl1_1 | CircPattern.1_ncl1_1Mesh
CircPattern.1_ncl1_2 | CircPattern.1_ncl1_2Mesh
CircPattern.1_ncl1_3 | CircPattern.1_ncl1_3Mesh
CircPattern.2 | CircPattern.2Mesh
CircPattern.2_ncl1_1 | CircPattern.2_ncl1_1Mesh
PROPELLER_CCW.1\Scale1 | PROPELLER_CCW.1\Scale1Mesh
PROPELLER_CCW.2\Scale1 | PROPELLER_CCW.2\Scale1Mesh
PROPELLER_CW.1\NONE | PROPELLER_CW.1\NONEMesh
PROPELLER_CW.2\NONE | PROPELLER_CW.2\NONEMesh
```

Do not broaden this deletion rule to other DAE names without another manual
visual confirmation. The current assembly script is:

```text
Scripts/UE5/assets/build_sunray150_dae_mid360_full_assembly_audit_scene.py
```

2026-06-03 accepted assembly state: the radar mount and all four propellers
passed manual Blender audit. Future edits must preserve the accepted
mechanical references instead of re-solving from rough visual guesses:

2026-06-04 Sunray150 material workflow correction: material work must be
component-first, not whole-aircraft-first. The whole-aircraft render is only a
final consistency check after individual component families are readable.
Process each component family as an independent review unit:

```text
identify physical component
  -> record source names and material evidence
  -> assign material / texture maps without changing accepted geometry
  -> render component close-up
  -> inspect render and material probe
  -> pass / iterate / ask user by WeChat if identity is unknown
```

Do not treat a good or bad whole-aircraft view as sufficient evidence for
material quality. At minimum, review these component families separately:

```text
MID-360 housing/window/connector/protection frame
carbon-fiber plates and frame arms
gold aluminum standoffs/columns
front and bottom USB cameras
PCB / N150 / ESC / connectors / cables
motors / copper windings / screws
tri-blade propellers
smoked protective rings / landing gear
battery / heat-shrink / clip
```

If a DAE/SDF object cannot be confidently mapped to a physical component, do
not guess a final material. Send a sparse WeChat question with the object name,
close-up image path, and the decision needed. Continue with other independent
component families while waiting if no geometry or material conflict exists.

2026-06-03 Blender launch safety correction: do not open `.blend` files through
Windows file association, Windows MCP `App`, or `blender-launcher.exe` for
manual review. On this machine those routes can be intercepted by unrelated
Windows applications/installers, including Visual Studio Blend or Ansys APDL,
which is outside the MoSim project boundary. The currently verified Blender
route is command-line/background only:

```bash
"/mnt/d/Program Files/Blender Foundation/Blender 5.0/blender-launcher.exe" \
  --background --python Scripts/UE5/assets/build_sunray150_dae_mid360_full_assembly_audit_scene.py
```

For GUI review, first verify a direct Blender launch path in a separate
infrastructure task. Do not click or confirm any unrelated installer, repair,
or uninstall dialog that appears while opening Blender assets. If Ansys,
Visual Studio Blend, or any non-Blender installer/uninstaller appears, stop the
operation immediately, close only the unrelated prompt if it is safe to do so,
and report the exact window title before continuing with project-local
command-line Blender work.

2026-06-04 WSL/Windows Blender interop correction: if direct WSL execution of
`/mnt/d/Program Files/Blender Foundation/Blender 5.0/blender.exe` fails with
`UtilAcceptVsock: accept4 failed 110`, do not retry in a loop and do not start
parallel Blender renders. First test whether WSL can launch any Windows
executable (`cmd.exe /c ver` is enough). If WSL interop is broken, launch the
same Blender executable through Windows MCP `PowerShell` from
`C:\Users\HP\Desktop\MoSim`, with project scripts and outputs kept inside the
project. Do not use WSL `powershell.exe` for this recovery path when it returns
the same vsock error.

2026-06-04 Blender execution verification correction: WSL-launched
`powershell.exe` can return exit code 0 while Blender stdout is empty and target
review images are not updated. Treat that as an unverified attempt. Use Windows
MCP `PowerShell` for background Blender commands, redirect stdout/stderr to a
project log under `Results/unreal_scene_mapping/`, and verify saved image
timestamps before claiming a render pass succeeded.

2026-06-03 material route correction: the rejected material candidates were
mostly color assignment, not a real texture workflow. The current minimum
material workflow is:

```text
identify DAE/SDF component names
  -> map each component to physical material evidence
  -> generate or import PBR texture maps
  -> attach texture maps to Blender node materials
  -> inspect local close-up material views before whole-aircraft review
  -> only after manual acceptance export/import into UE
```

The local reference projects are used as follows:

```text
ArmorPaint: target editor for hand retouching/painting PBR maps and Unreal export presets
Material Maker: procedural material graph reference for texture map generation
xatlas: future UV atlas/unwrapping route when per-object UVs need baking/painting
Blender: assembly, node material hookup, preview rendering, and export staging
```

```text
MID-360 fit:
  use AUDIT_STANDALONE_MID360_000..003 object centers as radar mount holes
  fit them to user-selected frame holes:
    H20/H21/H22, H19/H23/H24, H44/H47/H48, H43/H45/H46
  accepted uniform scale after direct four-hole fit: 0.833527

Propellers:
  source mesh: sunray150_with_mid360/meshes/sunray_cw.stl
  orientation: flipped_around_screw_axis
  final translation_z: -0.014052 m
  preserve XY screw-hole fit to DAE M2 screw pairs
```

Texturing route: do not rely on broad STL position heuristics for final
appearance. Keep assembly geometry locked first, then assign named material
slots from DAE object names and physical component roles. If texture painting
is needed, use Blender/ArmorPaint-style UV texture painting after UV unwrap; if
procedural PBR materials are needed, use a Material Maker-style node material
source and export UE-compatible maps. AI/procedural texture tools may suggest
materials, but final component colors require manual audit against Sunray
photos and manufacturer references.

2026-06-03 material review candidate: generated
`sunray150_dae_mid360_realistic_material_audit.blend` from the same assembly
script without changing the accepted mechanical values above. This is pending
manual approval, not final UE runtime material evidence. The review candidate
uses named PBR-style material roles instead of a dark/stylized single-color
palette:

```text
aircraft carbon plates: graphite/carbon-fiber procedural roughness
motors/screws/standoffs: black anodized metal and brushed steel
propellers: black composite plastic; no red/blue audit colors
MID-360:
  015 = blue optical window
  013/014 = dark grey housing
  016 = black base
  017 and rear details = black connector/port housing
  000..003 = black mount-hole/inserts
  004..007 = dark metal bosses/standoffs
```

2026-06-03 material review update: WSL path handling must use
`Path(__file__).resolve().parents[3]` in Blender asset scripts; do not hardcode
`C:\Users\HP\Desktop\MoSim` inside scripts executed from WSL/Blender. Current
material scripts generate deterministic PBR-style maps under
`UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/`, rebuild
`sunray150_dae_mid360_realistic_material_audit.blend`, and render close-up
audit views under `Audit/material_closeups/`. Geometry invariants remain:
MID-360 four-hole fit scale `0.833527`, propeller source `sunray_cw.stl`,
propeller orientation `flipped_around_screw_axis`, and propeller
translation-z rule ending at `-0.014052 m`.

Known material audit status: close-up previews are generated for MID-360,
front USB camera/battery, PCB/connectors/cables, carbon/gold standoffs, and
motor/prop/guard. These images are audit candidates only. Do not export to UE
until manual review accepts the Blender material appearance. If the
manufacturer appearance still looks too synthetic, move from procedural maps
to a UV unwrap + ArmorPaint/Material-Maker style paint pass rather than adding
more broad color heuristics.

Current audit package:
`Results/unreal_scene_mapping/SUNRAY150_MID360_MATERIAL_AUDIT_PACKAGE_20260603.md`.
Treat that package and the referenced close-up PNGs as the review entry point.
If the front camera/module shell, propeller blades, or guards read too light,
fix only the corresponding component material assignment or texture map. Do not
change the accepted MID-360 mount fit or propeller placement while doing
material-only correction.

2026-06-04 audit result: the current material candidate is rejected. The
overall image still reads as a light-grey CAD model with partial coloring, not
as a realistic Sunray150. Specific failures: MID-360 housing is too white and
the connector area has a black artifact; front electronics/camera views are
underexposed and collapse into black blocks; carbon frame surfaces are mostly
light grey instead of visible woven carbon fiber; gold standoffs look like
yellow plastic; motor/propeller close-up is too dark to prove motor, winding,
screw, or propeller materials. Next material pass must reclassify the visible
neutral/grey DAE objects, fix connector material artifacts, and render readable
component close-ups before any UE export/import.

2026-06-04 component-material evidence matrix:
`Results/unreal_scene_mapping/SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md`.
Use this matrix as the next material-pass source of truth. It records the
current component families, DAE/source-name cues, target physical materials,
known visual risks, and the role of Blender/ArmorPaint/Material Maker/xatlas.
When adding a new material or changing a classifier, update that matrix in the
same task. Do not rely on unreachable shopping pages as confirmed evidence
unless the user provides local screenshots/media.

The generated review file hides gold/green audit markers by default via
`MATERIAL_REVIEW=1` and `SHOW_AUDIT_MARKERS=0`; set `SHOW_AUDIT_MARKERS=1`
only when rechecking the mount geometry. Do not export this candidate to UE
until the user explicitly accepts the material appearance.

2026-06-03 correction: the first realistic-material candidate was rejected by
the user as insufficient because it was still simple material coloring rather
than a real texture/material pipeline. Treat it as a failed candidate. Future
appearance work must start with a physical component inventory and material
evidence, then use the local texturing toolchain appropriately:

```text
ArmorPaint: 3D PBR texture painting workflow when hand-painted texture maps are needed
Material Maker: procedural texture/brush graph source for carbon fiber, plastic, metal, rubber, PCB, cable, and lens materials
xatlas: UV atlas generation when a mesh needs unique UVs for texture painting or baking
Blender: component grouping, material-slot assignment, shader-node construction, preview rendering, and export staging
```

Simple `Base Color` changes are not accepted as "贴图". For every visible
component family, either create a physically motivated material/texture slot or
record why the current source mesh does not expose that component separately.
The current DAE component probe file is:

```text
Results/unreal_scene_mapping/sunray150_material_component_probe_20260603.json
```

It confirms visible component families beyond the main frame and MID-360:
front camera, bottom camera, USB 9P/24P connectors, HDMI connector, FCU cable,
ESC board, TF Mini PLUS/ranging sensor, screws/nuts, aluminum standoffs, motor
stator/windings, landing gear, protective rings, and MID-360 protection arcs.
These must be explicitly classified in the next texture audit asset.

Current tri-blade propeller audit rule for the same scene:

```text
propeller source:
  References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/sunray_cw.stl
deleted/rejected source:
  DAE CircPattern* and PROPELLER_* objects listed above
rotor centers:
  rotor_0_front_right  0.065 -0.065 -0.025
  rotor_1_back_left   -0.065  0.065 -0.025
  rotor_2_front_left   0.065  0.065 -0.025
  rotor_3_back_right  -0.065 -0.065 -0.025
visual transform:
  scale 0.001 0.001 0.001
  rpy 0 0 0
```

This is still a manual assembly review gate. If the user reports the three-blade
propeller shaft/hole alignment is wrong, adjust by mechanical evidence against
the motor screw/shaft interface, not by arbitrary visual offsets.

STL hole-location note: `sunray_cw.stl` is an ASCII STL with no object names and
no boundary-hole loops after vertex welding; it is a closed mesh. Therefore
propeller screw holes cannot be found by Blender object names or open-boundary
loops. The current accepted measurement method is geometric feature detection:
inspect hub-local vertical cylindrical features. For this STL the two fixing
holes are identified at local coordinates:

```text
(0, -2.5, 2.5) mm
(0,  2.5, 2.5) mm
hole distance = 5.0 mm
```

The DAE aircraft contains eight `SCREW_BUTTON_HEAD_M2_8MM` objects. Nearest-two
selection per SDF rotor center gives target screw-pair distances of roughly
`4.998 mm` to `5.011 mm`, so the STL base scale `0.001` is dimensionally
consistent; only tiny per-rotor scale corrections from the measured screw-pair
distance ratio are recorded in the manifest. Current placement fits the two STL
hole centers to the two DAE screw centers for each rotor.

Hole fitting does not determine propeller front/back side. When side orientation
is under review, generate the audit scene with
`PROP_ORIENTATION_MODE=candidates`. This creates two variants per rotor:

```text
normal
flipped_around_screw_axis
```

The flipped candidate is rotated 180 deg around the propeller screw-hole axis,
so the two screw holes remain aligned. In candidates mode it is lifted +10 mm
only so both candidates can be inspected simultaneously. Do not treat that
review lift as a final assembly offset.

Manual review accepted `flipped_around_screw_axis` as the correct propeller
front/back side. The current default generation keeps only the four flipped
three-blade propellers and removes the original four `normal` candidates.

Propeller Z placement is not allowed to use screw-hole center height. Manual
review requires that, when viewed from above, the propeller physical lower
surface contacts the screw-head/nut plane with only a small clearance. The
current accepted DAE-derived visual assembly uses the manifest rule:

```text
base translation_z = -0.0161 m
target screw plane = -0.0193 m
measured propeller contact plane = -0.021098 m
nominal clearance = 0.0001 m
final user fine tune = +0.00015 m
final propeller translation_z = -0.014052 m
```

Keep the screw-hole XY fit and accepted `flipped_around_screw_axis`
front/back orientation unchanged. Do not revert to older Z heuristics or to the
runtime MWORKS transparent-STL propeller position when editing the
DAE-derived UE visual asset.

Generated review/import assets:

```text
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.blend
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.fbx
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.glb
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured_manifest.json
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured_preview.png
```

The generated asset keeps these review groups:

```text
CarbonFrame
DarkGuards
LightPlastic
Mid360BaseGrey
Mid360DomeBlue
PCBGreen
ConnectorGold
MetalFasteners
CableBlack
```

Blender 5 localized UI note: do not find the material shader node by the
English node name `Principled BSDF`. In the Chinese UI it is named
`原理化 BSDF`. Asset scripts must find the node by
`node.type == "BSDF_PRINCIPLED"` before setting Base Color, Roughness,
Metallic, and Alpha.

Current source boundary correction: for the Sunray150 UE runtime visual,
`sunray150_with_mid360.sdf` is the authority. The SDF explicitly references
assets outside its own folder, so those explicit SDF references are allowed:

```text
base model:
  References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf
body:
  model://sunray150_with_mid360/meshes/sunray.stl
propeller:
  model://sunray150/meshes/sunray_cw.stl
MID-360:
  model://livox_mid360
```

Important visual-audit correction: `sunray150_with_mid360/meshes/sunray.stl`
already contains the visible MID-360 geometry on the aircraft body. Therefore
full-aircraft Blender/UE visual audits must not add a second visible
`model://livox_mid360` radar unless the task is explicitly testing the separate
sensor model. Keep the separate `model://livox_mid360` handling for standalone
sensor-origin/orientation audits and for later sensor-frame/runtime contracts,
not for duplicating visible geometry on the already-equipped aircraft STL.

Do not mix in `sunray150_D435i` or MWORKS runtime STL during this pass. The
`150.dae` files under `sunray150_with_mid360` and `sunray150_D435i` are byte
identical and should be treated as CAD/reference material. The accepted
runtime visual authority is now the reviewed DAE-derived UE asset. SDF remains
the dynamics/sensor-layout reference, not the runtime rendered-aircraft mesh.

The raw source audit scene is:

```text
Scripts/UE5/assets/build_sunray150_with_mid360_dae_source_audit_scene.py
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_with_mid360_dae_source_audit.blend
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_with_mid360_dae_source_audit_manifest.json
```

That audit scene imports only
`drone_models/sunray150_with_mid360/meshes/150.dae`; it is a CAD/source
reference audit only and must not be used as the runtime vehicle visual when it
contradicts the SDF chain.

The body STL visual orientation and the rotor physical translations are
separate. If the user reports that the camera looks forward while the UAV nose
points right, the body visual yaw offset is missing or overwritten. If the user
reports propeller positions are wrong after adding the body yaw offset, do not
rotate `Dronefixed1..4`.

Propeller placement is a mechanical assembly problem, not a visual tuning
problem. Final propeller placement must be solved by matching the propeller
mounting holes to the motor-top screw locations or mating faces. Manual yaw, Z,
or XY offsets are allowed only as temporary diagnostic values during a review
session; they must not be recorded as final runtime parameters unless a
hole-to-screw or face-to-face assembly check explains the value.

Current source-of-truth rule for the UE vehicle visual is SDF-first. Do not use
the MWORKS runtime transparent body/propeller STL as the placement authority for
new Sunray/UE asset work. Those STL files may be used only as historical
diagnostic references when explicitly comparing against the old MWORKS
animation.

```text
Actor/root frame = UAV body state frame
SDF/Jinja:
  References/Sunray/.../sunray150_with_mid360/sunray150_with_mid360.sdf
  References/Sunray/.../sunray150_with_mid360/sunray150_with_mid360.sdf.jinja
body visual:
  mesh model://sunray150_with_mid360/meshes/sunray.stl
  pose 0 0 0.0525 0 0 -1.57
  scale 0.03 0.03 0.03
rotor links:
  rotor_0 pose  0.065 -0.065 -0.025 0 0 0
  rotor_1 pose -0.065  0.065 -0.025 0 0 0
  rotor_2 pose  0.065  0.065 -0.025 0 0 0
  rotor_3 pose -0.065 -0.065 -0.025 0 0 0
rotor visual:
  use the tri-blade propeller file:
    References/Sunray/.../drone_models/sunray150_with_mid360/meshes/sunray_cw.stl
  do not use DAE PROPELLER_* objects and do not use the five-blade
  sunray150/meshes/sunray_cw.stl for the current visual asset
  current Blender asset creates four independent objects:
    sunray150_with_mid360_tri_blade_prop_front_right
    sunray150_with_mid360_tri_blade_prop_back_left
    sunray150_with_mid360_tri_blade_prop_front_left
    sunray150_with_mid360_tri_blade_prop_back_right
  unit rule:
    the Sunray upstream simulation repository was checked at HEAD
    26ed04aa35b47db638f34c60b15c68cc42e1b76d on 2026-06-03; the
    sunray150_with_mid360 SDF, SDF.jinja, 150.dae, and sunray_cw.stl match the
    local files, so upstream has no propeller assembly fix to pull
    150.dae declares unit meter=0.0254 and Y_UP
    SDF rotor centers are meters and must be converted to DAE units with
    center_dae = center_m / 0.0254
    the selected tri-blade STL is millimeter-scale and must be converted to DAE
    units with scale = 0.001 / 0.0254
    do not mix DAE-unit body geometry with meter-scale propeller geometry
front camera:
  pose 0.12 0 0.025 0 0 0
down camera:
  pose -0.01 0 -0.02 0 1.5707963 3.14
MID-360:
  include pose 0.036 -0.0155 0.075 0 0 0
  visual pose in livox_mid360.sdf 0 0 0 1.57 0 3.14159
  Blender/UE accepted visual orientation:
    body frame is +X nose, -X tail, +Y left, +Z up
    user visual audit requires the MID-360 connector/port to face tail (-X)
    accepted candidate is F_yaw180_only: 0 0 0 0 0 3.14159
    do not apply SDF roll=1.57 for the Blender/UE visual orientation unless a
    later Gazebo parity check proves the renderer axis conversion changed
  Blender/UE accepted visual origin:
    origin must be the circular radar base mounting center
    do not use the raw DAE/SDF origin if it is off-axis
    do not use the full visual bounding-box center; the top body/dome and cable
    connector can bias that center away from the base symmetry axis
    assembly order is: recenter the MID-360 visual mesh to this local base
    mounting-center origin first, then translate/rotate it to the SDF include
    pose; do not recenter the already-mounted radar back to world origin
    this assembly order applies only when separately auditing/importing
    `model://livox_mid360`; full-aircraft audits using `sunray.stl` must keep
    the built-in radar and skip the separate visible import
```

The SDF source above contains no 45 degree camera or vehicle pose. The visible
45 degree issue reported during review is therefore not a reason to patch the
SDF/Jinja directly. First check the review camera, Blender axis conversion,
FBX/glTF export transform, and UE import/component transform. Audit cameras are
review aids only and must never be copied into runtime UAV pose or camera-mount
parameters.

Current SDF runtime audit files:

```text
Scripts/UE5/assets/build_sunray150_with_mid360_sdf_runtime_audit_scene.py
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_with_mid360_sdf_runtime_audit.blend
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_with_mid360_sdf_runtime_audit_manifest.json
```

Manual review lock on 2026-06-03:

- The accepted full-aircraft visual body is
  `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/sunray.stl`.
- This body already includes the visible MID-360 radar; do not add a second
  visible radar in full-aircraft audit or runtime visual assets.
- The accepted propeller source for this aircraft visual is
  `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/sunray_cw.stl`.
- The current three-blade propeller orientation is manually accepted as
  visually correct. Future propeller work should only refine the two mounting
  holes against the two motor-top screws/mating faces. Do not change the
  aircraft body source, radar source, or propeller source while doing that
  refinement.
- 2026-06-04 user decision update: the manually assembled and reviewed
  DAE-derived aircraft may replace the STL route for the **UE rendered visual
  model**. This replacement applies only to the visible mesh/material asset in
  Unreal. It does not change MWORKS dynamics parameters, controller gains,
  sensor timing, collision/safety envelope, planner occupancy inflation, or
  any path-planning abstraction. Path planning should continue to use an
  abstract UAV body/envelope, not the detailed visual aircraft mesh.
- Do not transfer DAE mesh dimensions back into the simulation model as mass,
  inertia, collision, or control parameters. The DAE asset is accepted because
  it was manually assembled and visually reviewed for rendering, not because it
  is parameter-identical to the SDF/STL chain.
- STL has no native material, object hierarchy, UV, or part-name metadata, so
  detailed coloring requires a derived Blender/FBX/GLB asset with materials
  assigned by connected components, geometric regions, or manual masks. Keep
  that derived asset traceable to the accepted STL sources.
- `150.dae` is now allowed as the UE visual-flight asset through the manually
  audited assembly route, not as a raw direct import. The accepted DAE-derived
  asset must preserve the reviewed body orientation, radar placement,
  three-blade propeller replacement, propeller orientation/Z placement, material
  assignments, and camera/view behavior when imported into UE.
- Manual assembly parameters are **visual-asset parameters**, not MWORKS
  dynamics parameters. Current accepted values to preserve in the DAE-derived
  UE visual asset are:

  ```text
  MID-360:
    selected frame hole groups:
      H20/H21/H22, H19/H23/H24, H44/H47/H48, H43/H45/H46
    standalone MID-360 mount-hole source:
      AUDIT_STANDALONE_MID360_000..003 object centers
    accepted visual orientation:
      connector/port faces tail (-X), yaw180 candidate
    accepted uniform visual scale:
      0.833527
    accepted XY translation from four-hole fit:
      [0.012914, 0.032295, 0.0] m

  propellers:
    source:
      sunray150_with_mid360/meshes/sunray_cw.stl
    rejected/deleted:
      DAE CircPattern* and PROPELLER_* objects
    accepted orientation:
      flipped_around_screw_axis
    accepted final translation_z:
      -0.014052 m
    XY rule:
      fit STL screw holes (0,+/-2.5,2.5 mm) to each DAE M2 screw pair
  ```

  These values must be used when exporting/importing the accepted colored DAE
  aircraft into UE. They must not be pushed into `QuadChassis` mass/inertia,
  lift coefficient, controller parameters, planner collision envelope, or
  MWORKS rotor-center dynamics.
- 2026-06-04 propeller spin boundary: the current accepted UE vehicle visual is
  a whole-aircraft imported StaticMesh, so no separate UE propeller animation is
  active in this gate. `rotorVelocitySlowdownSim=10` and
  `lift_cofficient=0.000854858` remain dynamics/source-reference facts only.
  Do not retune `lift_cofficient`, `hover_motor_speed_cmd`, controller outputs,
  or MWORKS rotor centers to change render appearance. If visible spinning
  propellers become necessary later, create a new reviewed animated UE asset or
  approved componentized visual route; do not restore MWORKS animation/STL
  fallback.
- Official Sunray usage evidence: `sunray150_with_mid360.sdf` does not reference
  `meshes/150.dae` for runtime visuals. It references
  `model://sunray150_with_mid360/meshes/sunray.stl` for the base visual and
  includes `model://livox_mid360` for the sensor model. Therefore `150.dae` is
  treated as packaged CAD/Collada source material, not the official runtime
  flight visual for this vehicle.
- 2026-06-04 STL/DAE parameter check: before importing the high-quality visual
  asset into UE, run:

  ```bash
  python3 Scripts/UE5/assets/compare_sunray_stl_dae_parameters.py
  ```

  The generated evidence file is
  `Results/unreal_scene_mapping/sunray_stl_dae_parameter_compare_20260604.json`.
  Current result: `150.dae` is not parameter-identical to the SDF/STL runtime
  chain. It declares `unit meter=0.0254` and `Y_UP`, contains 701 geometry
  nodes, and its transformed total bbox is about
  `0.2115 x 0.1619 x 0.2147 m`. The accepted `sunray.stl` body with the SDF
  visual transform `pose 0 0 0.0525 0 0 -1.57`, `scale 0.03 0.03 0.03` has a
  bbox about `0.2537 x 0.2500 x 0.1912 m`. The two are same-class aircraft
  scale but not directly interchangeable in dimensions, origin, up axis, or
  component composition.
- Import rule from that check and later user decision: the bbox/unit mismatch
  is not a blocker for replacing the **rendered UE mesh**, because navigation
  and collision are not derived from the detailed aircraft mesh. Keep the
  mismatch recorded so future agents do not use the DAE visual model as a
  dynamics or planning-geometry source. UE import must still preserve the
  manually accepted visual assembly and keep the simulation/planning boundary
  separate.
- 2026-06-04 user decision for high-quality runtime rendering: use the
  manually reviewed DAE-derived aircraft as the UE runtime visual asset. Do not
  keep the STL route as runtime geometry fallback. While repairing the DAE
  route, preserve the DAE body/frame hierarchy, remove or replace only parts
  that are explicitly rejected in manual audit, and ask the user for targeted
  visual judgments rather than silently switching back to STL.
- The accepted higher-quality colored-aircraft route is the manually audited
  DAE-derived asset: keep the useful DAE body/frame geometry and material
  grouping, delete/hide the rejected DAE propellers/radar parts, and use the
  user-reviewed MID-360 and three-blade propeller assembly. Do not re-solve
  propeller or radar placement unless a later UE import review shows the
  exported asset changed transforms.
  In that scene, `Hxx` labels are TOP_PANNEL boundary-hole candidates and
  `Bxx` labels are standalone MID-360 bottom mount candidates. The user must
  choose ordered four-point sets before any transform/scale solve. Current
  user-selected carbon-plate hole groups are
  `H20/H21/H22`, `H19/H23/H24`, `H44/H47/H48`, and `H43/H45/H46`; each group is
  one physical hole represented by multiple boundary loops. Use
  `Scripts/UE5/assets/build_sunray150_mid360_selected_hole_fit_scene.py` for
  the diagnostic fit scene and check scale/yaw/RMS before accepting any MID-360
  replacement placement. User correction on 2026-06-03: the MID-360 connector
  must face the aircraft tail, so the selected-hole fit must present explicit
  90 deg and 270 deg radar-body rotation candidates instead of accepting a
  free-yaw automatic fit or merely changing point correspondence. The MID-360
  bottom face must sit on the TOP_PANNEL upper surface; compute XY from the
  selected holes, then snap the radar mesh minimum Z to the panel top Z. If
  neither 90/270 candidate aligns the radar bottom holes with the selected
  carbon-plate holes, stop and produce a radar-bottom hole pick scene; do not
  invent a scale or offset from uncertain B points. The older
  screw-object manual pick script is
  `Scripts/UE5/assets/build_sunray150_mid360_manual_pick_scene.py`; it creates
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_mid360_manual_pick.blend`.
  Keep it only for comparison if the carbon-plate holes are ambiguous. The
  earlier candidate-center audit script is
  `Scripts/UE5/assets/build_sunray150_dae_mid360_mount_audit_scene.py`; it
  creates the rejected/diagnostic candidate scene
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_mount_audit.blend`.
  Keep it only for diagnostic comparison, not as accepted placement.

The audit scene's active camera is a top orthographic camera named
`SDF_Audit_Top_Camera_No_Model_Rotation` so review-camera obliqueness cannot be
mistaken for model yaw.

Current propeller assembly audit files:

```text
Scripts/UE5/assets/build_sunray150_with_mid360_propeller_assembly_audit_scene.py
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_with_mid360_propeller_assembly_audit.blend
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_with_mid360_propeller_assembly_audit_manifest.json
```

The propeller assembly audit scene uses the DAE source to preserve part
semantics:

```text
gold = DAE `SCREW_BUTTON_HEAD_M2_8MM` candidate propeller screws
blue = DAE `PROPELLER_*` semantic propeller parts
red = DAE `CircPattern*` possible full propeller / blade pattern parts
green = rotor-center to screw-candidate lines for assembly review
```

Do not import MWORKS runtime STL into this propeller assembly audit. If MWORKS
parity is needed, open a separate historical-comparison task and do not use it
as the placement authority for the current `sunray150_with_mid360` visual.

Propeller offset must be treated as an assembly problem, not as an isolated STL
centering problem. Do not solve small propeller placement errors by calculating
the propeller STL bounding-box center or arbitrary mesh centroid. Use the
Sunray assembly source (`150.dae`) to preserve the part hierarchy and match the
propeller mounting holes/faces to the motor screw or shaft assembly references,
then export that assembled result to UE. If the assembly source and SDF visual
source disagree, stop at a manual review gate and record which source is being
used as the runtime visual authority.

Do not use a propeller placement pass to modify unrelated visual components.
The body, MID-360 scanner, scanner bracket, coloring, camera, and UE runtime
actor transforms must remain unchanged unless the task explicitly targets
those components. The June 3 manual DAE source review showed the standalone
MID-360/Livox direction is also wrong; track that as a separate radar-orientation
issue instead of mixing it with propeller assembly correction.

For the Factory visual placement gate, neutralize only the first-frame yaw to
`0 rad`. This is a manual body/propeller/heading review pose, not a controller
or trajectory truth claim. Full replay yaw belongs to later path/controller
review after this visual gate passes.

When the user reports a manual visual result, treat it as authoritative. Do not
spend additional time proving whether the review window is still open unless
the user explicitly asks; implement the reported correction or stop at the next
review gate.

The manual gate command is:

```bash
Scripts/UE5/review_factory_uav_platform.sh
```

To replay into an already-open Factory review window without restarting UE:

```bash
STREAM_ONLY=1 STREAM_MAX_FRAMES=1 STREAM_FPS=6 \
  Scripts/UE5/review_factory_uav_platform.sh
```

The Factory UAV review defaults to the follow/orbit camera view:

```bash
FOLLOW_UAV_CAMERA=1 STREAM_FPS=60 STREAM_RESAMPLE_HZ=60 STREAM_REPLAY_SPEED=1.0 \
  Scripts/UE5/review_factory_uav_platform.sh
```

This mode enables `-MoSimFollowPlaybackCamera` and replays the existing short
MWORKS/Sysplorer smoke state source once. It must not use sparse
`render_replay.csv` path points as simulation evidence. The review camera
follows the playback actor with the
current accepted close-inspection offset of `80 cm` behind, `20 cm` left, and
`40 cm` above the UAV. The offset is
rotated by the UAV yaw, so if the UAV turns, the camera view turns with it.
In follow-camera mode, the arrow keys are not free-look keys: left/right orbit
the camera around the UAV azimuth in the manually accepted actual movement
direction, up/down orbit elevation, and the spherical camera-target radius from
the current `FollowOffsetCm` is preserved. The
default offset remains `FVector(-80.0f, -20.0f, 40.0f)`. The camera rotation is
recomputed to look back at the UAV after each orbit update.
The display contract is separate from the controller contract: controller/state
evidence is expected at 20 Hz or higher where the formal MWORKS/Sysplorer
scenario defines it, but the UE render review should receive 60 Hz visual pose
frames. Sparse review CSV rows must be resampled before UDP streaming. Do not
judge control smoothness from a 4 Hz path-point CSV replay; this display replay
is not MWORKS/Sysplorer simulation evidence. If the UAV appears to translate
without roll/pitch/yaw dynamics, stop this gate and verify that the source path
is `Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv`.
Tune only the camera distance with `FOLLOW_CAMERA_BACK_CM`,
`FOLLOW_CAMERA_RIGHT_CM`, and `FOLLOW_CAMERA_UP_CM`; do not use this mode to
change the UAV pose or vehicle visual mesh.

To deliberately replay the full path after the vehicle visual gate is accepted:

```bash
STREAM_ONLY=1 STREAM_PATH_REPLAY=1 STREAM_LOOP_COUNT=1 STREAM_FPS=6 \
  Scripts/UE5/review_factory_uav_platform.sh
```

The user should review only these facts at this gate:

```text
Factory map is visible in daytime review mode.
The UAV body is the YunZong/Sunray150 visual body, not primitive blocks.
The UAV pose updates through the MWORKS/Bridge replay or UDP path.
Keyboard/mouse controls only the view/camera, not the UAV pose.
In the movement follow gate, the UAV moves through the short Factory path, and
the camera follows UAV translation and yaw closely enough to inspect the body
without colliding into it.
```

Do not open RViz/FAST-LIO/point-cloud review as a substitute for this gate.
Those are later sensor/localization gates after the UE vehicle body is accepted.

## Native Mapping Window Policy

Point-cloud, grid-map, localization, and planner-state review must use a
separate native robotics visualization window. Do not route this review through
browser HTML.

The supporting research and local-source evidence live in
`Docs/Workflows/unreal_mapping_window_research.md`. Treat that file as the
source of truth for the UE/RViz window split, ROS topic contract, and evidence
boundary.

The accepted runtime layout is:

| Window | Role | Typical Content |
|---|---|---|
| Unreal / `MoSimSceneLibrary` | High-fidelity rendered scene and UAV review | real map, UAV model, camera view, optional trajectory/local debug overlays |
| RViz / RViz2 or equivalent native robotics viewer | Mapping, localization, and planning review | `PointCloud2`, `OccupancyGrid`, TF, odometry, FAST-LIO registered cloud, local plan |
| QGroundControl or controller UI, when needed | Flight-control and mission supervision | mode, arming state, mission/command monitor |

This matches the common UAV simulation architecture:

- RflySim keeps Unreal/RflySim3D as the 3D engine and sends LiDAR data by
  shared memory or UDP; its LiDAR workflow explicitly uses ROS/RViz
  visualization for point clouds.
- AirSim runs the simulator separately from `airsim_ros_pkgs`; its documented
  ROS route launches `airsim_node.launch` and a separate `rviz.launch`, and the
  LiDAR publisher uses `sensor_msgs/PointCloud2`.
- PX4's Gazebo SITL path keeps Gazebo as the simulation environment and uses
  ROS 2/DDS integration for vehicle state and tooling; PX4 documentation calls
  out RViz visualizers for state review.
- Gazebo Sim keeps Gazebo as the simulation window and exposes LiDAR/depth
  point clouds to ROS as `sensor_msgs/msg/PointCloud2` through `ros_gz_bridge`
  or `ros_gz_point_cloud`, then RViz2 consumes the ROS topics.
- Local FAST-LIO and FAST-LIVO2 references under `References/Lab/` also launch
  RViz from their mapping launch files and publish/consume ROS point-cloud,
  odometry, and path topics.

Therefore, MoSim evidence must be separated as follows:

| Evidence | Accepted Claim |
|---|---|
| UE rendered window | Map looks correct, UAV/camera/review movement works, scene is visually accepted |
| RViz/RViz2 live topics | LiDAR/local map/planner/FAST-LIO state is visible in a native robotics window |
| FAST-LIO topics `/velodyne_points`, `/imu/data`, `/cloud_registered`, `/Odometry`, `/path` | FAST-LIO runtime localization can be evaluated |
| Offline `.ply`, JSONL, CSV handoff files | Input/replay artifacts only; not runtime localization evidence |
| HTML report preview | Optional report artifact only; never the active point-cloud/map review surface |

The operator-facing default for the current keyboard-mapping smoke is two
simplified RViz2 windows with no left-side configuration panels:

```text
Point-cloud RViz2 window
  -> raw `/velodyne_points` small-point view, plus FAST-LIO output placeholders

Grid/map RViz2 window
  -> `/mosim/local_occupancy_grid`, `/mosim/local_occupancy_voxels`, TF,
     manual odometry, local plan, and trajectory
```

This is the same review style as the UE rendered scene window: the operator
sees the rendered content, not a configuration-heavy UI. Do not open an empty
RViz window for the normal smoke path, because that leaves topic/display setup
as manual work.

```text
RViz planning/grid window
  -> local occupancy/grid map, local known map cloud, local plan, UAV path, TF

RViz point-cloud/FAST-LIO window
  -> raw LiDAR PointCloud2, FAST-LIO registered cloud, odometry, path, TF
```

One combined RViz/RViz2 overview window is acceptable for smoke tests or small
screens, but active point-cloud/map review must still be a native robotics
window. A browser-based point-cloud window does not satisfy the runtime
evidence contract.

Project commands for the native mapping window:

```bash
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans
DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect

# After ROS1/RViz is installed and sourced:
RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect
Scripts/UE5/run_fastlio_rviz_replay_ros1.sh factoryenvironmentcollect
Scripts/UE5/check_fastlio_ros1_topics.sh
```

The ROS2 manual keyboard mapping loop is now smoke-only. It may be used to
check RViz2 window layout, topic display configuration, and basic publisher
plumbing, but it is not a mainline controller, mapping, localization, FAST-LIO,
or planning evidence path. The user rejected the grid-cell motion and synthetic
point-cloud route on 2026-06-02 because it cannot support continuous UAV
control tuning.

Do not invest product time in improving the keyboard/grid-step route. The
specific rejected failure modes are:

- pose changes are tied to cell-sized manual steps, so controller tuning cannot
  be evaluated from smooth physical motion;
- point clouds and grid cells are not driven by synchronized UAV dynamics,
  IMU, LiDAR, and estimator state;
- 2D `OccupancyGrid` review is not a substitute for a UAV local 3D map;
- RViz point size or marker tuning does not fix missing FAST-LIO/localization
  semantics;
- static or synthetic point clouds can only verify display plumbing, not
  mapping or navigation.

Any manual-control demo must be implemented as a continuous setpoint stream
into the MWORKS/controller layer. It must not directly overwrite UAV pose.

Before opening UE/RViz2 for a new mapping review, run the headless real-stack
gate:

```bash
python3 Scripts/UE5/check_realstack_miniloop_gate.py \
  --output-json Results/unreal_scene_mapping/factoryenvironmentcollect/realstack_miniloop_gate.json \
  --output-md Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE.md
```

Only open review windows when the gate reports
`ready_for_manual_rviz_ue_review`. A `blocked_before_manual_review` result means
the data/runtime stack must be fixed first, even if RViz could be made visually
prettier.

For this smoke-only loop, the command opens the two simplified RViz2 windows
and the ROS2 publisher:

```bash
set +u
source /opt/ros/humble/setup.bash
set -u
Scripts/UE5/open_keyboard_mapping_rviz_ros2.sh factory
```

To run only the publisher when RViz is already open:

```bash
OPEN_RVIZ=0 Scripts/UE5/open_keyboard_mapping_rviz_ros2.sh factory
```

Before opening the UE rendered window for an imported/local scene, activate the
matching scene source first:

```bash
python3 Scripts/UE5/activate_renderer_scene_source.py --scene-source-id local_factoryenvironmentcollect
UNREAL_EXTRA_ARGS="/Game/Maps/Demonstration -MoSimDayReview" \
  RESTART_UNREAL_GAME=1 Scripts/UE5/open_unreal_renderer.sh simulation-review

python3 Scripts/UE5/activate_renderer_scene_source.py --scene-source-id local_derelictcorridormegascans
UNREAL_EXTRA_ARGS="/Game/DerelictCorridor/Maps/DerelictCorridor -MoSimDayReview" \
  RESTART_UNREAL_GAME=1 Scripts/UE5/open_unreal_renderer.sh simulation-review
```

The renderer `Content/` links are scene-specific. If Factory is launched while
Derelict is still activated, UE reports that `/Game/Maps/Demonstration` cannot
be found. Treat that as a scene-source activation error, not as a bad map path.

If the point-cloud window appears blank, first verify that the data path is
actually alive before changing the publisher:

```bash
ros2 topic echo --once /velodyne_points
ros2 topic echo --once /mosim/manual_odometry
```

Point-cloud density and grid resolution are part of the review contract. A
hundred-point local scan is not a credible FAST-LIO-style visual input. Common
UAV/robot LiDAR setups publish tens of thousands to hundreds of thousands of
points per scan in RViz: for example, VLP-16-class sensors are roughly
300k points/s, Livox Mid-360-class sensors are roughly 200k points/s, and
high-line Ouster sensors can be much higher. The ROS `nav_msgs/OccupancyGrid`
`resolution` field is meters per cell, and 2D navigation examples commonly use
about `0.05` m/cell. Therefore the current manual-review publisher keeps the
20Hz review path bounded enough for Python/rclpy and WSLg:

```text
/velodyne_points: local surface-sampled PointCloud2, capped at 20000 points/frame, 20Hz target
/mosim/local_occupancy_grid: 0.05 m/cell local grid, 8 m radius by default
/mosim/local_occupancy_voxels: 3D occupied voxel cloud, capped at 30000 points/frame, 2Hz target
```

This is still a local scene-truth sensor/review oracle, not final FAST-LIO
localization or final MWORKS solver evidence. Final claims require MWORKS-side
dynamics/control input plus real FAST-LIO-family runtime output topics such as
registered cloud and odometry.

Do not improve the manual/keyboard loop as a substitute for the real
MWORKS/UE/ROS2 UAV loop. Mainline work must move the vehicle from continuous
MWORKS dynamics and controller output, publish IMU/odometry/LiDAR at measured
rates, and keep planner commands as position/velocity/acceleration/yaw
setpoints rather than grid-cell steps.

The current minimum MWORKS state bridge is:

```bash
python3 Scripts/ros/publish_mworks_uav_state_ros2.py \
  --mworks-raw-csv Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv \
  --lidar-point-frames-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/lidar_point_frames.jsonl \
  --dry-run --max-frames 20
```

With ROS2 Humble sourced, the same script publishes:

```text
/mosim/truth/odometry  about 20Hz
/mosim/imu             about 200Hz, currently resampled from 20Hz MWORKS rows
/mosim/lidar_points    about 10Hz
/tf
```

Measured on 2026-06-02 after fixing publisher timing: odometry held about
20.0Hz, IMU held about 200.0Hz, and LiDAR held about 10.0Hz. This proves the
ROS2 topic-rate bridge, not final co-simulation. The current Factory LiDAR
input has only about 160 points per frame and is therefore below the density
needed for credible FAST-LIO/Mid360 review.

Dense replay generation now exists for bounded tests:

```bash
python3 Scripts/UE5/generate_livox_like_lidar_replay.py \
  --scene factoryenvironmentcollect \
  --max-frames 5 \
  --points-per-frame 30000 \
  --raycast-step-m 0.15 \
  --max-range-m 35.0
```

This reuses Sunray's `mid360-real-centr.csv` scan mode and UE collision truth.
Factory produced about 25k points/frame in the initial probe. Do not use the
current Python/rclpy bridge as the final dense LiDAR transport: when publishing
these 25k-point frames, the point cloud topic was visible but `ros2 topic hz`
fell to about 0.3-0.5Hz in the current WSL/ROS2 path. Dense real-time LiDAR
requires a C++ ROS2 node, UE C++ sensor bridge, or direct reuse/adaptation of a
Livox-style plugin path.

The first C++ ROS2 dense publisher lives under:

```text
Scripts/ros/mosim_dense_lidar_cpp
```

Current ROS2 build command for the project-local C++ LiDAR/IMU/probe package:

```bash
set +u
source /opt/ros/humble/setup.bash
source Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash
set -u
colcon --log-base Results/tmp/spark_fast_lio_ros2_ws/log build \
  --base-paths Scripts/ros/mosim_dense_lidar_cpp \
  --build-base Results/tmp/spark_fast_lio_ros2_ws/build \
  --install-base Results/tmp/spark_fast_lio_ros2_ws/install \
  --packages-select mosim_dense_lidar_cpp \
  --parallel-workers 4 \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
```

The package contains three mainline nodes for the real-stack gate:

```text
dense_lidar_replay_node          publishes dense PointCloud2 plus Livox CustomMsg
mworks_state_imu_replay_node     publishes MWORKS truth odometry/TF and 200Hz IMU
livox_imu_probe_node             C++ subscriber-side Livox CustomMsg + IMU gate
```

Use `livox_imu_probe_node` for dense Livox+IMU input validation. The Python
probe `Scripts/UE5/probe_livox_custommsg_ros2.py` remains useful for lightweight
or single-topic debugging, but it should not be the primary 25k-point Livox +
200Hz IMU acceptance gate because Python deserialization/callback handling can
distort the observed IMU rate.

The ROS2 mainline LiDAR publishers must use the Livox-compatible
`PointCloud2` layout from Sunray `livox2Point.cpp`:

```text
offset_time:uint32, x/y/z:float32, intensity:float32, tag:uint8, line:uint8
```

Older Velodyne-style `x/y/z/intensity/time/ring` replay output is reference
only and is not accepted as FAST-LIO/Mid360 evidence for the MoSim ROS2 path.

Build smoke:

```bash
set +u
source /opt/ros/humble/setup.bash
set -u
mkdir -p Results/tmp/mosim_dense_lidar_cpp_ws/src
cp -a Scripts/ros/mosim_dense_lidar_cpp Results/tmp/mosim_dense_lidar_cpp_ws/src/
cd Results/tmp/mosim_dense_lidar_cpp_ws
colcon build --packages-select mosim_dense_lidar_cpp
```

The prepacked C++ publisher reached roughly 7-8Hz for 25k-point frames in the
current WSL/ROS2 path. That is much better than Python, but still below the
10Hz dense LiDAR target when measured through `ros2 topic hz`. Publisher-side
statistics are more encouraging: with about 21k points/frame, the same
prepacked C++ node reported about 9.73Hz and mean publish call time around
100-130 microseconds. Treat `ros2 topic hz` as a subscriber-side stress test for
large point clouds, not as the only publisher truth. Final validation still
requires FAST-LIO or a dedicated C++ subscriber to consume the stream.

The same package now includes a dedicated subscriber-side probe:

```bash
set +u
source /opt/ros/humble/setup.bash
source Results/tmp/mosim_dense_lidar_cpp_ws/install/setup.bash
set -u

ros2 run mosim_dense_lidar_cpp dense_lidar_replay_node --ros-args \
  -p lidar_jsonl:=Results/unreal_scene_mapping/factoryenvironmentcollect/livox_like_lidar_frames.jsonl \
  -p topic:=/mosim/lidar_points \
  -p rate_hz:=10.0 \
  -p max_frames:=5 \
  -p stats_interval_s:=0.0

ros2 run mosim_dense_lidar_cpp dense_lidar_subscriber_probe_node --ros-args \
  -p topic:=/mosim/lidar_points \
  -p max_messages:=8 \
  -p min_rate_hz:=5.0
```

Latest short probe output recorded about `9.69Hz` subscriber-side with roughly
`19.9k-21.0k` points/frame, `point_step=22`, Livox fields present, and monotonic
stamps. This is a transport gate only; it is not FAST-LIO evidence until the
actual FAST-LIO runtime consumes the same stream and publishes odometry,
registered cloud, path, logs, and truth-error metrics.

The current Factory headless real-stack gate is:

```bash
DURATION_SECONDS=12 PROBE_SECONDS=4 STARTUP_PRELOAD_SECONDS=8 \
  bash Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh
```

Latest successful run:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_cpp_livox_headless_20260602_090500
```

Result:

```text
input gate: passed
  /mosim/livox/lidar about 18.68Hz, 24.5k-25.9k points/frame
  /mosim/forward/imu about 187.89Hz
  latest LiDAR minus IMU stamp about -0.020s
FAST-LIO runtime: nonzero
  /Odometry=172, /path=17, /cloud_registered=172
truth evaluation: failed
  position RMSE=9.576m, max error=17.900m
manual review: blocked
```

Therefore nonzero FAST-LIO topics are not enough to open RViz/UE review. Run
`Scripts/UE5/check_realstack_miniloop_gate.py` against the latest recording and
evaluation files. The gate must remain `blocked_before_manual_review` until
truth evaluation passes.

2026-06-02 same-source/body-frame correction:

- The old Factory FAST-LIO replay mixed LiDAR, IMU/state, and truth sources.
  Some LiDAR frames came from `control_reference.csv` or older replay artifacts
  while IMU/state came from the MWORKS raw CSV and evaluation truth came from a
  separate dataset. This is not a valid localization-quality gate.
- The old LiDAR replay also wrote world-frame points but the C++ publisher sent
  them as if they were in `base/mid360_link`. FAST-LIO acceptance input must be
  body/lidar-frame points when the ROS frame is `base/mid360_link`.
- The corrected replay generator supports `--pose-stride`,
  `--points-frame body`, and `--truth-dataset-name` so LiDAR points and truth
  are generated from the same MWORKS raw trajectory.
- A low-density smoke dataset generated from the MWORKS raw trajectory with
  body-frame points produced nonzero FAST-LIO output and reduced the error to
  RMSE `1.019363m`, max error `1.437659m`:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_factory_mworks_body_smoke_20260602_120335`.
  This is still `blocked_before_manual_review` because the threshold is
  RMSE `<=1.0m` and the smoke input used only about `6.2k` points/frame.

Formal Gate B runs must use:

```bash
python3 Scripts/UE5/generate_livox_like_lidar_replay.py \
  --scene factoryenvironmentcollect \
  --pose-csv Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv \
  --pose-stride 2 \
  --points-per-frame 20000 \
  --points-frame body \
  --truth-dataset-name fastlio_mworks_truth_dataset.jsonl \
  --lidar-rate-hz 10.0 \
  --point-rate-hz 200000.0
```

Then run the headless gate with matching input files and `MIN_LIVOX_POINTS`
at or above the accepted formal density:

```bash
LIVOX_FRAMES=Results/unreal_scene_mapping/factoryenvironmentcollect/livox_like_lidar_frames_mworks_body.jsonl \
TRUTH_DATASET=Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_mworks_truth_dataset.jsonl \
MIN_LIVOX_POINTS=15000 \
bash Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh
```

If a full replay generation times out and leaves a partial JSONL, do not use
that file as evidence. Regenerate it or delete it before running Gate B.

Formal Gate B pass on 2026-06-02:

```text
dataset:
  livox_like_lidar_frames_mworks_body.jsonl
  fastlio_mworks_truth_dataset.jsonl
  40 frames, body-frame points, min/avg/max points per frame 15607/16094.55/16515

runtime:
  Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_factory_mworks_body_formal_20260602_122033
  /Odometry=80, /path=8, /cloud_registered=80
  Livox probe: 9.887Hz, IMU 198.857Hz, monotonic stamps

evaluation:
  status=pass
  position RMSE=0.39454m
  max position error=0.611542m
  yaw RMSE=0.017802rad

gate:
  REALSTACK_MINILOOP_GATE.md -> ready_for_manual_rviz_ue_review
```

This permits opening the UE render window plus RViz2 FAST-LIO and RViz2 3D
map windows for manual review. It does not prove final controller integration,
planner performance, or final product acceptance.

Do not treat `/mosim/local_occupancy_grid` as the primary grid/map review
window. ROS `nav_msgs/OccupancyGrid` is inherently 2D; keep it as a reference
topic only. The native grid/map review window should primarily show
`/mosim/local_occupancy_voxels` as `PointCloud2` so vertical obstacle occupancy
is visible. The default planning RViz2 configs now use a 3D Orbit view; a
top-down view is only an auxiliary operator view, not proof that the planner
map is three-dimensional.

Keep RViz point rendering close to default FAST-LIO practice: `PointCloud2`
should use `Style=Points`, `Size (Pixels)=1`, and not large spheres/boxes unless
the user explicitly requests enlarged debugging points. The 2026-06-01 oversized
point-cloud issue was caused by review configs using `Style=Spheres` and
`Size (Pixels)=9`.

2026-06-02 runtime note: 80000-220000 points/frame in the Python review
publisher is visually dense but does not maintain 20Hz on the current
ROS2/WSLg path. A bounded 20000-point `/velodyne_points` stream reached measured
`ros2 topic hz` rates around 20Hz after the publisher cached pose-dependent
cloud/voxel data and refreshed only message headers while stationary. Raise
`LIDAR_MAX_POINTS` only for density screenshots, not for the default manual
motion audit.

The 2026-06-01 Derelict review failure was display-side, not topic-side:
`/velodyne_points` was publishing `sensor_msgs/msg/PointCloud2` in
`ue_world`, but RViz's Displays panel occupied most of the window and the camera
was pointed too narrowly for manual audit. The review configs therefore hide the
left panel and keep a close Derelict-centered view with large cyan point
spheres. Do not debug this case as a ROS2 publisher failure unless the topic
subscription itself is empty.

`RVIZ_PROFILE=overview` opens `Config/rviz/mosim_uav_mapping.rviz`.
`RVIZ_PROFILE=planning_grid` opens
`Config/rviz/mosim_uav_planning_grid.rviz`. `RVIZ_PROFILE=fastlio_pointcloud`
opens `Config/rviz/mosim_uav_fastlio_pointcloud.rviz`.
`RVIZ_PROFILE=split` opens both specialized windows.

`Scripts/UE5/open_native_pointcloud_preview.sh` is only a Windows-native manual
preview fallback for file artifacts when ROS/RViz is missing. It is not RViz,
not FAST-LIO runtime evidence, and must not be used to close localization or
navigation claims.

External references checked:

- RflySim Vision PPT:
  `https://rflysim.com/doc/en/RflySimAPIs/8.RflySimVision/PPT.pdf`
- RflySim system overview:
  `https://rflysim.com/doc/en/1/Intro.html`
- AirSim ROS wrapper:
  `https://microsoft.github.io/AirSim/airsim_ros_pkgs/`
- Gazebo ROS/Gazebo Sim demos:
  `https://docs.ros.org/en/rolling/p/ros_gz_sim_demos/index.html`
- ROS `nav_msgs/OccupancyGrid` / `MapMetaData`:
  `https://docs.ros.org/en/noetic/api/nav_msgs/html/msg/MapMetaData.html`
- Nav2 example costmap configuration:
  `https://docs.nav2.org/configuration/packages/configuring-costmaps.html`
- FAST-LIO / LiDAR families used as density references:
  `https://github.com/hku-mars/FAST_LIO`,
  `https://www.velodynelidar.com/products/puck/`,
  `https://www.livoxtech.com/mid-360`,
  `https://ouster.com/products/scanning-lidar/os1-sensor`

The current practical route separates manual Fab/Launcher actions from
project-local automation:

```text
Epic Launcher / Fab UI
  -> user manually creates/adds assets into UE5/MoSimSceneLibrary
MoSim scripts / MCP
  -> inspect the local scene-library project
  -> rank .uproject + .umap candidates
  -> export collision/planning truth
  -> link or migrate accepted scene content into MoSimSceneLibrary
```

The long-term preferred route is end-to-end MCP automation:

```text
mosim-epic
  -> inspect Epic/Fab/Launcher inventory
  -> choose candidate scene asset
  -> verify local editable project/content
mosim-unreal
  -> open/import/reuse scene in MoSimSceneLibrary
  -> modify scene components when needed
  -> run reversible edit probes
  -> export or verify map truth
MWORKS/Syslab MCP
  -> stream validated simulation states
  -> generate metrics/evidence
```

If any route cannot be automated reliably, stop that route early and record the
blocker. Do not spend hours retrying the same failing Launcher/UE/plugin path.
The approved local editable scene targets are:

```text
C:\Users\HP\Desktop\MoSim\UE5\MoSimSceneLibrary
C:\Users\HP\Desktop\MoSim\References\UnrealScenes
```

## Kept Project Components

```text
UE5/MoSimSceneLibrary/
UE5/Bridge/
```

`MoSimSceneLibrary` is the project-owned Unreal project for both Fab /
Marketplace scene staging and runtime rendering. Use it for manual Epic
Launcher **Create Project** / **Add To Project** actions. Imported scene assets
under `Content/` and project-local `Plugins/` are ignored by Git unless a
reviewed asset batch explicitly unignores them.

`Bridge` contains the `QuadrotorMworksBridge` plugin, which provides UDP
reception and playback state for MWORKS simulation output.

Generated folders are disposable and must not be committed:

```text
UE5/**/Binaries/
UE5/**/Intermediate/
UE5/**/Saved/
UE5/**/DerivedDataCache/
UE5/MoSimSceneLibrary/Content/
UE5/MoSimSceneLibrary/Plugins/
```

## Scene Source Selection

Preferred source order:

1. Downloaded Fab/Epic free assets with real scene content, such as factory,
   warehouse, forest, park, cave, corridor, city/building, and open outdoor
   scene packs.
2. Open-source UE projects with editable `.uproject`, `.umap`, `.uasset`,
   `Config/`, `Source/`, and plugin source when required.
3. RflySim, AirSim, Cosys, SPEAR, CARLA, Sunray, and YunZong scenes only as
   visual/API/layout references unless their editable assets and required
   plugins can be opened cleanly.

Route decision rule:

| Route | Accept When | Stop When |
|---|---|---|
| Fab/Launcher automated | Asset can be created/added to a local UE project, then imported/reused in `MoSimSceneLibrary`, edited through UE MCP, and paired with planning truth | Asset is account-visible only, plugin is incompatible, download requires manual login for this step, or no editable project/content is produced |
| Local `References/UnrealScenes` | `.uproject/.umap/.uasset` are already local, loadable, and can export truth | It is a one-room demo, runtime-only package, missing modules cannot be rebuilt, or manual visual review rejects it |
| Open-source external UE project | License is acceptable, editable content exists, required plugins/builds are available | Project only provides code without useful scenes, cooked assets, or unavailable plugins |
| RflySim native runtime | Useful for visual/API/reference behavior | Treating packaged runtime scenes as directly editable MoSim assets |

Reject as final scene sources:

- packaged runtime-only scenes that cannot be opened in the editor;
- cooked/unversioned `.umap` packages without compatible project/plugin source;
- primitive boxes used to approximate a factory or competition map;
- one-room demos when the requirement is a large flyable environment.

Before choosing a scene source, inspect the local Epic/Fab/Launcher inventory:

```bash
python3 Scripts/UE5/epic_library_index.py --compact
python3 Scripts/UE5/epic_library_view.py
python3 Scripts/UE5/epic_library_index.py --query Factory
python3 Scripts/UE5/epic_library_index.py --query City
python3 Scripts/UE5/check_epic_library_inventory.py
python3 Scripts/UE5/audit_scene_source.py
python3 Scripts/UE5/audit_scene_source.py --maps
uv run python Scripts/UE5/build_scene_source_registry.py --write
uv run python Scripts/UE5/build_scene_source_registry.py --validate \
  UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json
```

The inventory separates:

| Field | Meaning |
|---|---|
| `launcher_items` / `launcher_installs` | Installed engines and plugins from Epic manifests |
| `account_library_items` | Owned library entries inferred from the local Launcher account cache; may not be installed |
| `fab_assets` | Local FabLibrary cached downloads |
| `vault_cache_projects` | Old-style VaultCache projects and any discovered `.uproject` |
| `epic_library_view.py` | Merged human-readable view across account/Fab/Vault sources |

Current verified local-library behavior on 2026-05-26:

```text
launcher_item_count: 12
launcher_install_count: 12
fab_asset_count: 5
vault_cache_project_count: 8
account_library_item_count: 17
```

This inventory is a selection and planning tool, not a downloader. If an asset
exists only in `account_library_items`, use Epic Launcher/Fab to create or add
it to a UE project before treating it as editable local content. Do not parse or
publish raw Launcher logs or webcache entries; only the allowlisted index output
is safe to record.

Do not treat an owned Fab entry as an accepted scene. It becomes a scene source
only after it has local editable content, a renderer load proof, and a truth
export/proxy route.

`build_scene_source_registry.py` writes the project-owned handoff contract:

```text
UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json
```

This registry intentionally redacts external Launcher/Fab cache paths. It keeps
only sanitized inventory status, MoSim-local scene paths, the active fallback
scene id, and explicit truth-artifact links. Use it as the current decision
surface for whether the Fab route is accepted or the local editable fallback is
active.

When Codex needs this inventory through MCP, register
`Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh` as
`mosim-epic`.
Keep it separate from `mosim-unreal`: library inventory selects candidate
assets, while `mosim-unreal` edits a running UE project.

## Scene Acceptance Gates

A scene is not accepted just because it renders well. It must pass three gates:

| Gate | Required Evidence |
|---|---|
| Import/edit | Editable `.uproject`, `.umap`, `.uasset`, required plugin source or compatible installed plugins |
| Render | Opens in the target UE version and can be reviewed without missing modules/assets |
| Planning truth | Has or can generate explicit collision/semantic/occupancy truth for mapping, local planning, and path validation |

For the RflySim-like simulator goal, add two operational gates:

| Gate | Required Evidence |
|---|---|
| MCP automation | The selected route can be operated through `mosim-epic` and/or `mosim-unreal`, or the blocker is documented with an approved fallback |
| Manual review | The user confirms the map/animation/video view is visually acceptable before UAV/radar/planning work is layered on top |

If a Fab entry only exposes a binary `manifest` and no editable project/content
files, it is only an account/cache listing. It is not yet a MoSim scene source.
Use Epic/Fab to create the local project, or switch to already available local
projects under `References/UnrealScenes`.

## Main Map Selection

Do not guess the main `.umap` by directory order. Fab/Epic sample projects often
contain hundreds of component maps, packed-level maps, preview maps, and asset
zoos. Loading those maps produces misleading blank, partial, or non-scene
results.

Selection order:

1. Read `Config/DefaultEngine.ini`.
2. Prefer `GameDefaultMap`.
3. Fall back to `EditorStartupMap`.
4. Fall back to `ServerDefaultMap` only if it is a project `/Game/...` map.
5. Only if no configured map exists, use `audit_scene_source.py --maps` ranking.

Reject these as first-review maps unless explicitly requested:

```text
Content/**/PackedLevels/**/*.umap
Content/**/Packed/**/*.umap
Content/**/PLBPs/**/*.umap
Content/**/Asmbly/**/*.umap
Content/**/Previewer/**/*.umap
Content/**/AssetZoo*.umap
```

Current local review candidates:

| Scene | First Review Map | Notes |
|---|---|---|
| `DerelictCorridorMegascans` | `/Game/DerelictCorridor/Maps/DerelictCorridor` | Main candidate; passed manual rendered review and validates with 4753 collision proxies. |
| `FactoryEnvironmentCollect` | `/Game/Maps/Demonstration` | Main candidate; passed manual rendered review and validates with 8658 collision proxies. |
| `CityParkEnvironmentCollec` | `/Game/CityPark/Maps/Showcase`, `/Game/CityPark/Maps/Showcase_NotOptimized` | Deferred; Overview closed immediately, Showcase variants stayed black while merged park/fence/foliage static meshes built. |
| `CitySample` | `/Game/Map/Big_City_LVL`, `/Game/Map/Small_City_LVL` | Rejected for immediate linked-content use; both big and small city stayed black, and CitySample-specific C++/plugin classes are missing in `MoSimSceneLibrary`. |
| `DarkRuinsMegascansSample` | `/Game/Main` | Rejected for main daytime rendered scene use after manual review stayed fully black even with forced review lighting; keep only as a special dark/indoor/radar reference. |
| `ElectricDreamsEnv` | `/Game/Levels/PCG/ElectricDreams_PCGCloseRange` | Deferred; truth artifact exists, but rendered review stayed black/non-reviewable with PCG/Blueprint compatibility errors. |
| `MedievalVillageMegascansS` | `/Game/Maps/MedievalVillage_P` | Rejected for immediate main rendered scene use; second manual review stayed fully black and logs show UE 4.27-origin compatibility/static-mesh build issues. |
| `ABoyandHisKite` | `/Game/Maps/GoldenPath/GDC_Landscape_01`, `/Game/Maps/TutorialMap` | Rejected for immediate linked-content use; GoldenPath stalls with UE 4.27 compatibility issues, TutorialMap loads but is mostly black with only 3D text visible and missing KiteDemo C++ parent classes. |
| `FPS-Shooter-Unreal` | `/Game/FirstPerson/Maps/FirstPersonMap` | Rejected for formal scene-library use after manual visual review; keep only as a lightweight UE launch/control smoke test. |

Use the fast planner to produce the exact command without scanning the full
asset tree:

```bash
uv run python Scripts/UE5/plan_scene_truth_export.py --query Electric
uv run python Scripts/UE5/run_scene_truth_export.py --query Electric
```

`run_scene_truth_export.py` is dry-run by default. It now uses the configured
map package automatically; do not pass old guessed packages unless the user is
intentionally reviewing an alternate map.

Current fallback source:

```text
References/UnrealScenes
```

This fallback is not a downgrade of the product goal. It is the controlled path
when Fab/Launcher automation cannot produce editable local content quickly
enough. The final product can still look and operate like RflySim; the scene
source simply comes from local editable projects instead of directly from Fab.

Run:

```bash
python3 Scripts/UE5/audit_scene_source.py
```

Any scene with `needs_truth_extraction_or_proxy` may be visually useful, but it
still needs a truth-extraction or proxy-generation pipeline before it can prove
mapping/path-planning behavior.

Current audit result: the editable local projects under `References/UnrealScenes`
are not uniformly usable through simple linked-content reuse.
`FactoryEnvironmentCollect` and `DerelictCorridorMegascans` are the current main
rendered-map set because both passed manual visual review and both validate
against explicit collision-truth exports. `ElectricDreamsEnv` has a truth
artifact but failed rendered review, so it is not a current main map. UE assets
with collision/navigation names are treated only as proxy candidates; they are
not accepted as planner truth until exported to an explicit
occupancy/collision/semantic artifact and paired with a visible rendered review.

To promote an editable scene into a truth-backed scene, open it in Unreal Editor
and run the exporter through Editor Python:

```bash
uv run python Scripts/UE5/plan_scene_truth_export.py --query Derelict
```

The planner prints the project path, a map sample, the Unreal Editor Python
export command, and the normal-shell validation command.

For a command-line handoff, generate the Unreal commandlet command and the
temporary Editor Python batch script:

```bash
uv run python Scripts/UE5/run_scene_truth_export.py \
  --query Derelict \
  --map-package /Game/DerelictCorridor/Maps/DerelictCorridor
```

The default mode is dry-run. Add `--run` only after confirming the selected
scene opens with the matching UE version and required plugins.

```bash
# Run inside Unreal Editor Python, not normal Python:
py Scripts/UE5/export_unreal_scene_truth.py export \
  --scene-id <scene_id> \
  --map-id <map_id> \
  --output UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/<map_id>_collision_truth.json
```

Then validate from the normal project shell:

```bash
uv run python Scripts/UE5/export_unreal_scene_truth.py validate \
  UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/<map_id>_collision_truth.json
uv run python Scripts/UE5/audit_scene_source.py
```

The exporter records world-space AABB collision proxies from collidable static
mesh components. This is a first explicit truth route, not final high-fidelity
mesh/voxel mapping. It is acceptable for deciding whether a candidate scene can
enter planner integration; detailed occupancy/semantic refinement can follow.

Validated example:

```bash
uv run python Scripts/UE5/run_scene_truth_export.py \
  --query Derelict \
  --map-package /Game/DerelictCorridor/Maps/DerelictCorridor \
  --run
uv run python Scripts/UE5/export_unreal_scene_truth.py validate \
  UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json
uv run python Scripts/UE5/audit_scene_source.py
```

Validated Derelict example: UE 5.5 commandlet loaded
`/Game/DerelictCorridor/Maps/DerelictCorridor` and wrote
`derelictcorridormegascans_collision_truth.json` with 4753 assets and 4753
collision proxies. The scene-source audit then marked
`DerelictCorridorMegascans` as `ready_for_truth_backed_planning`. This proves
the local editable scene has an explicit first-pass planner-truth route; it
does not mean semantic labels or high-fidelity voxel occupancy are complete.

Validated Factory example: UE 5.5 commandlet loaded `/Game/Maps/Demonstration`
and wrote `factoryenvironmentcollect_collision_truth.json` with 8658 assets and
8658 collision proxies. The project-owned renderer commandlet then loaded the
same map as `/Game/Maps/Demonstration` with 11872 actors. Factory has been the
active content-linked scene for integration/review rounds when
`active_scene_links.json` points to `local_factoryenvironmentcollect`; do not
describe it as the registry policy primary unless the registry is re-read in
that same round.

Validated ElectricDreams example: UE 5.5 commandlet wrote
`electricdreamsenv_collision_truth.json` with 247 assets and 247 collision
proxies. Full renderer load can exceed the default 60 second gate because UE is
building Nanite/static-mesh data on first use. Treat this as a slow path, not a
failed scene, until a longer approved load window or manual editor review says
otherwise.

Scene-source state fields must be interpreted separately. Do not answer
"current scene" from one field alone.

```text
fab_route.status: inventory_visible_not_scene_accepted
local_editable_fallback.status: active
scene_source_registry.policy.primary_scene_source_id: see scene_source_registry.json
active_scene_links.scene_source_id: see active_scene_links.json
```

Interpretation: Fab/Epic library entries are visible and useful for selecting
assets, but none is accepted yet as a MoSim scene source until it is imported or
reused in the MoSim UE sim project, editable through UE tooling, and paired
with planning truth. The registry policy primary, active renderer content
links, latest manual-review target, latest runtime/Gate-B bundle, and final
product acceptance are separate states.

Round-3 memory audit on 2026-06-04 found this split in the current files:

```text
scene_source_registry.policy.primary_scene_source_id: local_derelictcorridormegascans
active_scene_links.scene_source_id: local_factoryenvironmentcollect
factory runtime bundle: ready_for_manual_rviz_ue_review
Factory/Derelict closed-loop status: ready_smoke_validated with MWORKS smoke_only
```

Therefore, a future answer should say exactly which state it is referring to:
registry policy primary, currently linked renderer content, manual review
packet target, headless Gate-B/manual-review readiness, or final accepted
scene. Truth-backed, active-linked, loaded, visually reviewed, runtime reviewed,
and final product accepted are not synonyms.

`AQuadrotorMworksMapActor` consumes this registry through:

```text
SceneSourceRegistryJson = MworksData/scene_source_registry.json
ResolveSceneSourceId(<scene_source_id>)
```

When the incoming frame `map_id` is `local_factoryenvironmentcollect`, the map
actor now records the editable project path, `.uproject` path, truth artifact
list, acceptance gates, renderer-local content root, renderer map asset, and
renderer package name from the registry. For the current Factory fallback it
sets `bCurrentSceneImportedIntoRenderer=true` because the scene is reused inside
the MoSim renderer through local content junctions rather than copied into Git.

Source-level gate:

```bash
uv run python Scripts/UE5/check_unreal_bridge.py
uv run python Scripts/UE5/check_scene_source_udp_contract.py
uv run python Scripts/UE5/check_ue_fab_goal_acceptance.py
```

This check verifies that the C++ bridge exposes the scene-source registry fields
and that the committed registry does not contain external Launcher/Fab absolute
paths. The scene-source UDP contract check generates one dry-run frame with the
registry primary `map_id` and verifies that this selected source matches the
registry primary scene id, carries truth artifacts, and keeps
`local_known_map` / preview `local_plan` marked as render-only. It is not visual
import evidence; it proves the packet path that triggers
`ResolveSceneSourceId`.

Use `check_ue_fab_goal_acceptance.py` as the current objective audit. It checks
the UE/Fab tool goal gate by gate: Epic/Fab inventory visibility, Fab-route
acceptance, local fallback readiness, truth-artifact validation, UDP
scene-source selection, live `mosim-unreal` edit evidence, minimal Skills /
workflow presence, and visual import/reuse evidence. The default mode reports
partial progress without failing. Use `--require-complete` only when deciding
whether the full goal is ready to close.

Current expected status after local fallback activation:

```text
ok=true through the local editable fallback after scene activation and renderer map-load proof
fab_route_acceptance: partial
scene_visual_import_or_reuse: passed
```

This means the active local fallback has truth, packet-level selection, and
renderer-local content links under `UE5/MoSimSceneLibrary/Content/`.
Fab remains unaccepted until one Fab asset is created/imported with edit access
and planning truth. The local fallback route still satisfies the current goal
branch because the goal explicitly allows switching to `References/UnrealScenes`
when Fab cannot prove import/edit/truth.

The local fallback scene is activated with:

```bash
python3 Scripts/UE5/activate_renderer_scene_source.py \
  --scene-source-id local_factoryenvironmentcollect
uv run python Scripts/UE5/build_scene_source_registry.py --write
```

`MoSimSceneLibrary` is a unified shell, not a permanent mount of every scene
project at once. Many Marketplace/Fab/sample projects use conflicting hard-coded
packages such as `/Game/Blueprints`, `/Game/Meshes`, `/Game/Maps`, and
`/Game/Materials`. Keep only one local scene source active at a time. The
activation script removes renderer Content links that point into
`References/UnrealScenes`, preserves project-owned roots such as `MworksData`,
and then creates links for all top-level `Content` folders in the selected
source. World Partition companion folders under `Content/__ExternalActors__` and
`Content/__ExternalObjects__` are linked with the same top-level package names.

`References/UnrealScenes` stays ignored. These links are local runtime/editor
bridges, not committed copies of third-party assets. On WSL/Windows, links must
be Windows directory junctions when available, not Linux symlinks. A WSL symlink
can pass Python `exists()` checks while Unreal cannot load the `.umap`.

`mosim-unreal` asset/map search must also follow those Content junctions and
keep package paths renderer-local. For example, Factory's linked
`UE5/MoSimSceneLibrary/Content/Maps/Demonstration.umap` must report
`/Game/Maps/Demonstration`, not the resolved source-project path under
`References/UnrealScenes`.

Verify that the renderer can actually load the linked package:

```bash
uv run python Scripts/UE5/probe_renderer_map_load.py
uv run python Scripts/UE5/probe_renderer_map_load.py \
  --scene-source-id local_factoryenvironmentcollect \
  --engine-version 5.5 \
  --json-output Results/tmp/renderer_map_load_probe_factory_<date>.json
```

The probe must report `ok=true`, `loaded_expected_map=true`, and
`actor_count>0` for the selected source's recorded `renderer_map_package`.
A zero exit code from Unreal alone is not enough, because commandlets can return
success after falling back to an empty temporary map.

Current verified main local renderer reuse:

| Scene source | Renderer package | Truth artifact | Load proof |
|---|---|---|---|
| `local_derelictcorridormegascans` | `/Game/DerelictCorridor/Maps/DerelictCorridor` | `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json` | `Results/tmp/renderer_map_load_probe_latest.json` |
| `local_factoryenvironmentcollect` | `/Game/Maps/Demonstration` | `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json` | `Results/tmp/renderer_map_load_probe_factory_active_20260531.json` |

Factory currently loads with high actor count and valid collision truth, but UE
reports `PhysXVehicles`-related Blueprint warnings for forklift vehicle assets.
Treat those as vehicle/Blueprint compatibility debt, not as a blocker for
static scene truth and map planning.

Manual visual review: on 2026-05-31 the user confirmed the standalone
`MoSimSceneLibrary` view opened the Factory map correctly. Derelict was then
relaunched for manual review with the old generated preview map disabled. This
does not yet close semantic truth, occupancy-grid, UAV playback, radar overlay,
or route-planning evidence.

Current visual policy: the main rendered-map pool should be white/daytime
visible by default. Dark exploration-style maps are not accepted as primary
rendering scenes only because they load and have collision truth. If a scene is
usable only after radar-style darkness or emissive-object viewing, keep it as a
special indoor/radar candidate and continue reviewing brighter outdoor/factory
maps for the main product path.

For real scene visual review, use the scene-review launch mode:

```bash
RESTART_UNREAL_GAME=1 \
UNREAL_EXTRA_ARGS="/Game/Maps/Demonstration" \
Scripts/UE5/open_unreal_renderer.sh review-scene
```

`review-scene` passes `-MoSimSceneReview`, which disables automatic spawning of
the old `MworksData/map_open_blocks_render_map.json` preview/STL/blockout map
and the default playback actor. Without this flag,
`AMoSimSceneLibraryGameMode` may overlay the generated MWORKS preview map on
top of a real imported scene, causing a false visual-review failure.

Factory review must start inside the real factory navigation/review area. The
launcher and review pawn now provide a Factory-specific default camera for
`/Game/Maps/Demonstration`; do not work around a bad start point by disabling
camera collision. The previous `(-4750, 3850, 180) cm` review point was inside
a CargoCar collision proxy. The current accepted UAV task start is
`(-5533, 2423, 190) cm`, which corresponds to truth coordinates
`(-55.33, -24.23, 1.90) m`; the review camera starts offset at approximately
`(-5733, 2423, 280) cm` so the user is not trapped inside the UAV center.

Derelict review must also start inside the exported scene-truth bounds. The
current `/Game/DerelictCorridor/Maps/DerelictCorridor` default review camera is
`(8704, -2240, 220) cm` with yaw `90 deg`, chosen from a terrain/floor patch
near truth coordinates `(~87.04, 22.40, 2.20) m`. Do not use the generic
`(-3600, -2800, 1450) cm` MoSim preview-camera default for Derelict because it
is outside the real corridor scene.

Imported maps may carry their own GameMode or Pawn. `review-scene` must force
`/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode` for every `/Game/...`
review map so the project review camera, no-preview-map flag, no-playback flag,
and review lighting are active. It must also keep PlayerController possession
locked to `MworksReviewCameraPawn` and disable imported Pawn input during scene
review; Factory includes robot/forklift Pawns that can otherwise become the
controlled subject. In logs, acceptance requires `MWORKS scene-review control enforced`,
`pawn=MworksReviewCameraPawn`, `MWORKS review camera active`, and the
preview/playback auto-spawn disabled messages.

For scenes whose default camera position is wrong or whose interior is too dark
for review, first use balanced camera and fill-light overrides. Do not enable
forced exposure as the default review path because it can overexpose the whole
viewport to pure white.

```bash
RESTART_UNREAL_GAME=1 \
UNREAL_EXTRA_ARGS="/Game/Maps/Demonstration \
  -MoSimReviewCameraX=-5733 -MoSimReviewCameraY=2423 -MoSimReviewCameraZ=280 \
  -MoSimReviewCameraPitch=-12 -MoSimReviewCameraYaw=0 -MoSimReviewCameraRoll=0 \
  -MoSimReviewHeadLightIntensity=8 -MoSimReviewHeadLightRadius=25000 \
  -MoSimReviewSunIntensity=12 -MoSimReviewSkyLightIntensity=3" \
Scripts/UE5/open_unreal_renderer.sh review-scene
```

These overrides are for manual acceptance only. They do not change the source
map assets and do not prove final lighting quality. If forced exposure is ever
needed for diagnostics, use `-MoSimDayReview` deliberately and lower
`-MoSimReviewExposureBias` first; do not use it for normal visual approval.

The review camera must be collision-constrained. It uses a swept collision
sphere by default, so manual inspection cannot pass through walls or exterior
scene boundaries. If a scene can only be judged by disabling camera collision,
do not promote it as a main simulation map. Use
`-MoSimReviewCollisionRadius=<cm>` only to tune the reviewer body radius for a
specific map; `-MoSimNoReviewCollision` is for diagnostics only and must not be
used for acceptance.

Rendered visual approval is not planner approval. Before any UAV playback,
navigation, or path-planning claim, validate the route against exported
collision/occupancy truth. A trajectory that intersects a wall is invalid even
if the renderer camera or debug view can move through the geometry.

## Scene Truth Mapping Pipeline

After Factory and Derelict passed manual visual review, the current file-level
pipeline is:

```bash
python3 Scripts/UE5/scene_truth_pipeline.py
python3 Scripts/tests/test_scene_truth_pipeline.py
```

This consumes:

```text
UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json
UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json
```

and writes:

```text
Results/unreal_scene_mapping/RUN_SUMMARY.md
Results/unreal_scene_mapping/<scene_id>/occupancy_grid.json
Results/unreal_scene_mapping/<scene_id>/trajectory.csv
Results/unreal_scene_mapping/<scene_id>/render_replay.csv
Results/unreal_scene_mapping/<scene_id>/local_known_map_frames.jsonl
Results/unreal_scene_mapping/<scene_id>/local_plan_frames.jsonl
Results/unreal_scene_mapping/<scene_id>/lidar_point_frames.jsonl
Results/unreal_scene_mapping/<scene_id>/pointcloud_merged.ply
Results/unreal_scene_mapping/<scene_id>/fastlio_handoff.json
Results/unreal_scene_mapping/<scene_id>/fastlio_replay_dataset.jsonl
Results/unreal_scene_mapping/<scene_id>/fastlio_adapter_manifest.json
Results/unreal_scene_mapping/<scene_id>/navigation_control_handoff.json
Results/unreal_scene_mapping/<scene_id>/control_reference.csv
Results/unreal_scene_mapping/<scene_id>/planned_quintic_reference_params.json
Results/unreal_scene_mapping/<scene_id>/planned_quintic_reference_constructor.mo.txt
Results/unreal_scene_mapping/<scene_id>/control_interface_package.json
Results/unreal_scene_mapping/<scene_id>/scenario_draft.yaml
```

The planner uses `unknown_global_map_receding_astar_known_obstacles_only`.
The full collision truth is not provided to the planner; it is only used to
simulate sensing and validate `collision_free_against_truth=true`. The current
reference generator also applies a controller-tracking buffer before selecting
start/goal candidates, because the MWORKS smoke controller can otherwise track
outside a narrow corridor even when the reference itself is collision-free.

Current verified output on 2026-06-01:

| Scene | Path Cells | Replans | Lidar Points | Planner Truth |
|---|---:|---:|---:|---|
| `factoryenvironmentcollect` | 34 | 11 | 1934 | `global_truth_available_to_planner=false`, `collision_free_against_truth=true`, `buffered_collision_free_against_truth=true` |
| `derelictcorridormegascans` | 45 | 11 | 2068 | `global_truth_available_to_planner=false`, `collision_free_against_truth=true`, `buffered_collision_free_against_truth=true` |

The `fastlio_handoff.json` and `fastlio_adapter_manifest.json` files are input
contracts, not completed FAST-LIO localization results. They record
deterministic offline LiDAR frames, a merged point cloud, occupancy, path,
per-frame local planner outputs, `render_replay.csv`, and a ROS1 replay
dataset. The replay dataset includes synthetic finite-difference IMU derived
from the replay path; it is not measured flight IMU.

## Native Map and Point-Cloud Windows

Do not use a browser HTML page as the primary point-cloud solution. The product
architecture follows the common UAV simulation split:

```text
UE/MoSimSceneLibrary window
  -> real rendered scene, UAV body, camera view, radar/local-plan debug overlay,
     trajectory video

ROS/RViz/RViz2 or equivalent native window
  -> PointCloud2, local occupancy/grid map, TF, odometry, local/global path,
     FAST-LIO registered cloud and pose output
```

This matches the observed external and local references:

| Reference | Relevant behavior |
|---|---|
| RflySim Vision API docs | `https://rflysim.com/doc/en/RflySimAPIs/8.RflySimVision/PPT.pdf` says the Lidar-UDP ROS route uses RViz visualization for environment point-cloud data; `https://rflysim.com/doc/zh/RflySimAPIs/RflySimSDK/html/md_vision_2md_2VisionComm.html` lists ROS1/ROS2 `PointCloud2` lidar topics |
| AirSim ROS wrapper | `https://microsoft.github.io/AirSim/airsim_ros_pkgs/` documents `roslaunch airsim_ros_pkgs rviz.launch` and lidar topics as `sensor_msgs::PointCloud2`; `https://microsoft.github.io/AirSimExtensions/airsim_ros_pkgs/` documents the ROS2 `rviz.launch.py` flow |
| Gazebo + ROS2 | `https://gazebosim.org/docs/harmonic/ros2_integration/` documents the `ros_gz_bridge` ROS/Gazebo message bridge and separate RViz visualization; `https://docs.ros.org/en/ros2_packages/jazzy/api/ros_gz_bridge/index.html` lists `sensor_msgs/msg/PointCloud2` <-> `gz.msgs.PointCloudPacked` bridging |
| ROS RViz guide | `https://docs.ros.org/en/humble/Tutorials/Intermediate/RViz/RViz-User-Guide/RViz-User-Guide.html` describes RViz as a ROS 3D visualizer and Point Cloud(2) displays for `sensor_msgs/msg/PointCloud2` |
| Local FAST-LIO | `References/Lab/FAST_LIO/launch/mapping_mid360.launch` starts `fastlio_mapping` and optionally starts `rviz -d loam_livox.rviz`; `References/Lab/FAST_LIO/rviz_cfg/loam_livox.rviz` subscribes to `/cloud_registered`, `/Odometry`, `/path` |
| Local EGO-Planner/Sunray | `References/Lab/ego-planner/.../default.rviz` and `References/Sunray/.../launch_rviz/*.rviz` show planning markers, point clouds, occupancy/grid maps, robot state, and paths in a separate visualization window |

Project-local native RViz assets:

```text
Config/rviz/mosim_uav_mapping.rviz
Config/rviz/mosim_uav_planning_grid.rviz
Config/rviz/mosim_uav_fastlio_pointcloud.rviz
Scripts/ros/publish_mosim_mapping_replay_ros1.py
Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh
Scripts/UE5/check_ros_mapping_runtime_env.py
Scripts/UE5/open_unreal_editor_mcp_listener.sh
Scripts/UE5/open_mapping_rviz_ros1.sh
Scripts/UE5/run_fastlio_rviz_replay_ros1.sh
Scripts/UE5/check_fastlio_ros1_topics.sh
```

Dry-run without ROS:

```bash
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans
DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect
```

When ROS1/RViz is installed and sourced, open the native point-cloud/map window:

```bash
RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh factoryenvironmentcollect
RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros1.sh derelictcorridormegascans
```

The project publisher uses the same evidence-backed files as UE UDP replay:

```text
render_replay.csv
local_known_map_frames.jsonl
local_plan_frames.jsonl
lidar_point_frames.jsonl
```

and publishes:

```text
/velodyne_points
/mosim/local_known_map_cloud
/mosim/local_occupancy_grid
/mosim/local_plan
/mosim/replay_odometry
/mosim/uav_path
TF: ue_world -> base_link
```

FAST-LIO output remains separate: `/cloud_registered`, `/Odometry`, and
related FAST-LIO topics are accepted only after the ROS1/FAST-LIO runtime is
available and has produced runtime logs/pose/map output. Static PLY files and
offline JSONL frames are handoff evidence, not localization.
`/mosim/replay_odometry` is replay/reference pose for RViz2 review only; it is
not a substitute for FAST-LIO `/Odometry`.

HTML output is allowed only for explicitly requested offline report previews,
not for scene point-cloud review, FAST-LIO evidence, or the RflySim-like
runtime UI.

Hard implementation constraints:

1. Do not add a browser/HTML point-cloud viewer to the active runtime path.
2. Do not describe UE debug overlays, WPF previews, static `.ply` inspection, or
   report previews as completed mapping/localization evidence.
3. Any script that claims active point-cloud/map review must launch or prepare a
   native RViz/RViz2/equivalent robotics viewer and publish/consume ROS topics.
4. FAST-LIO acceptance requires `/velodyne_points` plus `/imu/data` input,
   `/cloud_registered` plus `/Odometry` output, a runtime recording, and
   `evaluate_fastlio_runtime.py` comparison against replay truth.
5. Global scene truth stays hidden from the planner and is used only for
   collision/safety validation and evaluator oracle checks.

Generate and inspect the FAST-LIO replay adapter state with:

```bash
python3 Scripts/UE5/prepare_fastlio_replay.py
python3 Scripts/tests/test_fastlio_replay_adapter.py
python3 Scripts/UE5/publish_fastlio_replay_ros1.py \
  --dataset Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_replay_dataset.jsonl \
  --dry-run --max-frames 2
```

Current status is recorded in:

```text
Results/unreal_scene_mapping/FASTLIO_REPLAY_STATUS.md
```

Generate and inspect local FAST-LIO-family ROS compatibility with:

```bash
source /opt/ros/humble/setup.bash
python3 Scripts/UE5/check_fastlio_family_compatibility.py --write
python3 Scripts/tests/test_fastlio_family_compatibility.py
```

Current status is recorded in:

```text
Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md
```

Current evidence reports no local ROS2 FAST-LIO-family candidate. `FAST_LIO`,
`FAST-LIVO2`, and `Point-LIO-point-lio-with-grid-map` are all
`ros1_catkin_only`, so `START_FASTLIO=1` must remain disabled for the ROS2
wrapper until a ROS2 package or an approved bridge route exists.

Use the ROS2 launch workflow when validating the package-style runtime path:

```bash
DRY_RUN=1 MAX_FRAMES=2 START_RVIZ=0 Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect
START_RVIZ=0 START_FASTLIO=0 MAX_FRAMES=3 LOOP=0 Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect
```

The wrapper builds the project-local `Scripts/ros/mosim_scene_replay` launch
package into ignored scene-specific
`Results/tmp/mosim_scene_replay_ros2_ws_<scene>` workspaces and runs `ros2
launch mosim_scene_replay mosim_scene_replay.launch.py`. Scene-specific
workspaces avoid Factory and Derelict parallel smoke tests deleting each
other's generated build files. It launches the MoSim mapping publisher and
FAST-LIO input replay publisher. `start_fastlio` remains false unless a real
ROS2 FAST-LIO-family launch command is supplied.

For the current native ROS2 FAST-LIO2 candidate, run:

```bash
Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh
```

The candidate is MIT SPARK `spark-fast-lio`, staged only under ignored
`Results/tmp`. The script can download/extract `ros-humble-pcl-ros` under
ignored `Results/tmp/ros2_overlay_pcl_ros` without sudo, making `pcl_ros`
visible for the project-local build. Current build status is recorded in
`Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md/json`; a build
attempt has started but can exceed the 60 second interactive timeout during
PCL/OpenNI discovery. After `BUILD=1
Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh` succeeds, source
`Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash` and pass a real
`FASTLIO_ROS2_LAUNCH_CMD` to the ROS2 launch wrapper. Validate its odometry
topic with `FASTLIO_ODOMETRY_TOPIC=/odometry` because this candidate publishes
relative `odometry`, not the older `/Odometry` spelling.

If a scene reports `blocked_missing_ros1_runtime`, install/source a ROS1 Catkin
environment with FAST-LIO dependencies before attempting a real FAST-LIO run.
When ROS1 is already installed but FAST-LIO is not visible to `rospack`, use:

```bash
source /opt/ros/noetic/setup.bash
Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh
source Results/tmp/fastlio_ros1_ws/devel/setup.bash
python3 Scripts/UE5/check_ros_mapping_runtime_env.py --write
```

`bootstrap_fastlio_ros1_workspace.sh` creates only generated workspace files
under ignored `Results/tmp/fastlio_ros1_ws` and symlinks the project-local
`References/Lab/FAST_LIO` package. A dry-run validates the contract without
creating files:

```bash
DRY_RUN=1 BUILD=0 Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh
```

Do not turn this into a planner input or localization claim until ROS publishes
runtime PointCloud2/IMU, FAST-LIO returns pose/map output, and the result is
compared against the replay truth.

When ROS1/Catkin/FAST-LIO is installed and sourced, run the integrated native
runtime wrapper:

```bash
Scripts/UE5/run_fastlio_rviz_replay_ros1.sh factoryenvironmentcollect
Scripts/UE5/run_fastlio_rviz_replay_ros1.sh derelictcorridormegascans
```

The wrapper starts or reuses `roscore`, launches `fast_lio
mapping_velodyne.launch rviz:=false`, opens RViz with
`Config/rviz/mosim_uav_mapping.rviz`, publishes MoSim mapping replay topics,
and publishes FAST-LIO replay PointCloud2/IMU topics. Validate a real run with:

```bash
Scripts/UE5/check_fastlio_ros1_topics.sh
```

The topic check requires `/velodyne_points`, `/imu/data`,
`/mosim/local_occupancy_grid`, `/mosim/local_plan`, `/cloud_registered`, and
`/Odometry` to exist and produce at least one message. A dry-run only validates
the command contract:

```bash
DRY_RUN=1 MAX_FRAMES=2 Scripts/UE5/run_fastlio_rviz_replay_ros1.sh factoryenvironmentcollect
DRY_RUN=1 Scripts/UE5/check_fastlio_ros1_topics.sh
```

Do not run `prepare_fastlio_replay.py` concurrently with any publisher or
dry-run reader for the same scene. It rewrites `fastlio_replay_dataset.jsonl`
and `fastlio_adapter_manifest.json`; concurrent readers can see a partial JSONL
line and report a false decode error.

Use the runtime readiness preflight whenever the boundary between file-level
evidence and real runtime evidence is unclear:

```bash
python3 Scripts/UE5/check_ros_mapping_runtime_env.py --write
python3 Scripts/UE5/check_unreal_scene_runtime_readiness.py --write
```

For interactive Unreal MCP work, the editor-side listener must be reachable
before actor/map modification claims. Use the project entrypoint instead of
guessing a running process:

```bash
DRY_RUN=1 Scripts/UE5/open_unreal_editor_mcp_listener.sh
Scripts/UE5/open_unreal_editor_mcp_listener.sh
```

The real command opens `UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject` in
Editor mode and polls the UnrealMCP listener for up to 60 seconds. If it times
out, continue with file-level work or request GUI/plugin review; do not claim
editor-side modification.

This writes:

```text
Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.json
Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.md
Results/unreal_scene_mapping/ROS_MAPPING_RUNTIME_ENV.json
Results/unreal_scene_mapping/ROS_MAPPING_RUNTIME_ENV.md
```

`file_loop_ready=true` means required artifacts, path validation, handoff
files, review packets, and smoke collision outputs exist. `runtime_ready=true`
additionally requires the native ROS1/RViz/Catkin path and the live UE editor
listener when editor-side automation is needed. The primary map/point-cloud
review route remains a native ROS/RViz window, not browser HTML.

Generate the navigation/control handoff after the scene truth and FAST-LIO
adapter files exist:

```bash
python3 Scripts/UE5/build_navigation_handoff.py
python3 Scripts/tests/test_navigation_handoff.py
```

This writes `NAVIGATION_HANDOFF_STATUS.md` plus per-scene control-interface
packages. The package converts the accepted UE path into a
`PlannedQuinticReference` parameter set and a sampled `control_reference.csv`.
The current reference speed is `0.8 m/s` with `min_segment_duration_s=0.9`;
raising speed must be followed by a new MWORKS smoke run and strict UE-truth
collision check. It deliberately writes an inactive `scenario_draft.yaml`; do
not promote a draft to formal evidence unless a concrete Sysplorer model
consumes the generated parameters and passes MCP `check_model` and
`simulate_model`.

Current generated MWORKS smoke models and reference sizes:

| Scene | PlannedQuinticReference Segments | Stop Time | Boundary |
|---|---:|---:|---|
| `factoryenvironmentcollect` | 33 | 31.3258252147 s | `QuadrotorExperiments.Sunray150UEFactoryLinearMPCSysblockSmoke`, smoke evidence only |
| `derelictcorridormegascans` | 44 | 39.6 s | `QuadrotorExperiments.Sunray150UEDerelictLinearMPCSysblockSmoke`, smoke evidence only |

After generating or changing these models, run:

```bash
python3 Scripts/mworks/run_mworks_scenario.py \
  Config/scenarios/planning/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.yaml \
  --no-gui-open --allow-readable-result-after-simulate-false
python3 Scripts/mworks/run_mworks_scenario.py \
  Config/scenarios/planning/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke.yaml \
  --no-gui-open --allow-readable-result-after-simulate-false
python3 Scripts/UE5/check_mworks_scene_truth_collision.py --fail-on-violation
python3 Scripts/UE5/build_mworks_ue_scene_smoke.py
```

Latest 2026-06-01 smoke status: both scenes passed `check_model` and
`simulate_model`, both metrics report `quality_status=smoke_only`, and strict
collision validation reports `actual_occupied=0` and `reference_occupied=0`.
Factory produced 628 result rows with minimum actual clearance about `0.95 m`;
Derelict produced 793 result rows with minimum actual clearance about `0.79 m`.
This validates the control-interface and truth-check chain only. It does not
claim final autonomous navigation, final FAST-LIO localization, or full
controller performance.

For a one-command status aggregate after any regeneration or smoke run:

```bash
python3 Scripts/UE5/summarize_scene_closed_loop.py --fail-on-issue
```

This writes:

```text
Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.json
Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.md
```

The latest aggregate reports both accepted scenes as
`ready_smoke_validated`; the remaining warning is
`fastlio_blocked_missing_ros1_runtime`. Treat that warning as a real blocker
for FAST-LIO localization claims, not as a failure of the scene-truth or
MWORKS smoke chain.

Generate the native runtime review bundles after readiness and handoff files
exist:

```bash
python3 Scripts/UE5/check_unreal_scene_runtime_readiness.py --write
python3 Scripts/UE5/build_scene_runtime_bundle.py
python3 Scripts/tests/test_scene_runtime_bundle.py
```

This writes:

```text
Results/unreal_scene_mapping/UE_SCENE_RUNTIME_BUNDLE_STATUS.md
Results/unreal_scene_mapping/<scene_id>/runtime_review_bundle.json
Results/unreal_scene_mapping/<scene_id>/runtime_review_bundle.md
Results/unreal_scene_mapping/<scene_id>/run_native_runtime_review.sh
```

The bundle is an execution contract, not runtime evidence. It gathers the UE
rendered-scene command, RViz mapping-window command, FAST-LIO runtime command,
FAST-LIO recording/evaluation commands, truth-policy flags, and manual
acceptance gates. On the current WSL session both accepted scenes correctly
report `blocked_runtime_dependencies` because ROS1/RViz/Catkin are unavailable
and the UE editor listener is not reachable. Once those dependencies are
available, the per-scene wrapper can run the native surfaces without adding a
browser point-cloud path:

```bash
Results/unreal_scene_mapping/factoryenvironmentcollect/run_native_runtime_review.sh
Results/unreal_scene_mapping/derelictcorridormegascans/run_native_runtime_review.sh
```

The `render_replay.csv` output is directly compatible with the project UDP
streamer. Use dry-run first:

```bash
python3 Scripts/UE5/stream_unreal_udp.py \
  Results/unreal_scene_mapping/factoryenvironmentcollect/render_replay.csv \
  --scene-id factoryenvironmentcollect_mapping_replay \
  --map-id local_factoryenvironmentcollect \
  --coordinate-policy ue_world_m_z_up \
  --local-plan-source evidence_backed_scene_truth_pipeline \
  --local-known-map-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/local_known_map_frames.jsonl \
  --local-plan-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/local_plan_frames.jsonl \
  --lidar-point-frames-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/lidar_point_frames.jsonl \
  --dry-run --max-frames 2 --no-sleep

python3 Scripts/UE5/stream_unreal_udp.py \
  Results/unreal_scene_mapping/derelictcorridormegascans/render_replay.csv \
  --scene-id derelictcorridormegascans_mapping_replay \
  --map-id local_derelictcorridormegascans \
  --coordinate-policy ue_world_m_z_up \
  --local-plan-source evidence_backed_scene_truth_pipeline \
  --local-known-map-jsonl Results/unreal_scene_mapping/derelictcorridormegascans/local_known_map_frames.jsonl \
  --local-plan-jsonl Results/unreal_scene_mapping/derelictcorridormegascans/local_plan_frames.jsonl \
  --lidar-point-frames-jsonl Results/unreal_scene_mapping/derelictcorridormegascans/lidar_point_frames.jsonl \
  --dry-run --max-frames 2 --no-sleep
```

For the current accepted scenes, use the UE review loop wrapper:

```bash
OPEN_UE=1 OPEN_RVIZ=0 STREAM_LOOP_COUNT=1 STREAM_FPS=12 WAIT_UDP_SECONDS=45 \
  Scripts/UE5/review_scene_mapping_loop.sh factoryenvironmentcollect

OPEN_UE=1 OPEN_RVIZ=0 STREAM_LOOP_COUNT=1 STREAM_FPS=12 WAIT_UDP_SECONDS=45 \
  Scripts/UE5/review_scene_mapping_loop.sh derelictcorridormegascans
```

Use `OPEN_RVIZ=1` only when ROS1/RViz is installed and sourced. Otherwise run
`DRY_RUN=1 Scripts/UE5/open_mapping_rviz_ros1.sh <scene>` to validate the
publisher contract without opening a GUI.

The playback actor spawns the UAV body, propellers, reference marker,
trajectory trail, radar sector, local-plan spline, optional local-known-map
debug mesh, and optional LiDAR debug mesh from UDP frames. These UE overlays
are for rendered-scene review and debugging; the primary point-cloud/grid-map
window remains RViz or an equivalent native robotics visualizer. The local-plan
spline comes from
`local_plan_frames.jsonl`, not from a global-truth prior. Latest smoke evidence:

```text
Factory:  /Game/Maps/Demonstration, local_map_cells=137, lidar_points=176, lidar_evidence=true
Derelict: /Game/DerelictCorridor/Maps/DerelictCorridor, local_map_cells=320, lidar_points=166, lidar_evidence=true
```

This proves runtime UDP playback into the standalone UE review window, not live
editor actor placement. `mosim-unreal` can read project context and detects
`UE_5.5` plus `UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject`, but the live
UE Editor listener remains unavailable in this session. The latest
`ue_health(host=127.0.0.1, port=55557)` probe returned connection refused for
`127.0.0.1:55557` and a timeout through the WSL gateway, and the current Codex
tool surface exposes no callable WindowsMCP namespace. Do not claim editor-side
actor placement or viewport capture until a reversible editor probe passes.

Current blocked or lower-priority candidates:

| Scene source | Status | Next action |
|---|---|---|
| `CityParkEnvironmentCollec` | Overview closed immediately; Showcase and Showcase_NotOptimized stayed black while logs built or waited on merged park/fence/foliage static meshes | retry only with a longer approved build/export window or after manual editor warm-up/prebuilt asset cache |
| `CitySample` | `/Game/Map/Big_City_LVL` and `/Game/Map/Small_City_LVL` stay black in linked-content review and logs show missing `/Script/CitySample...` and `/Script/CitySampleMassCrowd...` classes | retry only through a dedicated plugin/source integration or standalone CitySample-project review pass |
| `DarkRuinsMegascansSample` | `/Game/Main` can start after root-level `Content/Main.umap` linking, but manual rendered review stayed fully black even with forced daylight/skylight/exposure/headlight settings; commandlet also only exposes global/camera/postprocess actors | do not use for the main daytime rendered map set; keep only as a special dark/indoor/radar reference unless a later dedicated relighting pass is approved |
| `MedievalVillageMegascansS` | UE 4.27 origin; `/Game/Maps/MedievalVillage_P` starts but manual review stayed fully black and logs show Blueprint/input compatibility warnings, stale navmesh, and long static-mesh builds | retry only with a dedicated conversion/cache warm-up/lighting pass if a village map is needed |
| `ABoyandHisKite` | UE 4.27 origin; `/Game/Maps/GoldenPath/GDC_Landscape_01` did not reach `Load map complete`, `/Game/Maps/TutorialMap` loads but is mostly black with only 3D text visible, and logs show missing `/Script/KiteDemo...` C++ classes plus stale Blueprint functions/delegates | retry only with a dedicated KiteDemo source/project conversion/cache warm-up pass |
| `FPS-Shooter-Unreal` | manual visual review rejected the template/shooter map as unsuitable for MoSim scenes; previous partial truth was also misleading because required `/Game/AbandonedFactory/...` assets were missing | do not treat as a formal scene source; use only as a lightweight UE launch/control smoke test |

Binary build gate:

```bash
Scripts/UE5/build_unreal_renderer.sh
```

If this fails at `LINK : fatal error LNK1104` for
`UnrealEditor-QuadrotorMworksBridge.dll` or
`UnrealEditor-MoSimSceneLibrary.dll`, check for an open `UnrealEditor.exe`.
That state means the editor is holding the output DLLs. Close or restart the
editor and rerun; do not record it as a source compile failure.

Relevant current-phase skills:

```text
Docs/Skills/Unreal/mosim-epic/SKILL.md
Docs/Skills/Unreal/mosim-unreal/SKILL.md
```

## First-Pass Manual Review Gate

For each candidate scene, record:

```text
source path or Fab listing
engine version
project/open method
whether it opens without missing modules
visual class: factory / forest / park / indoor / city / open outdoor
scene scale: one room / small course / large map
asset editability: editable / runtime-only / unknown
manual review verdict
next action
```

The manual review should start with the map only. Do not spawn UAV, radar,
trajectory, or UDP playback until the map itself is acceptable.

## Renderer Build and Open

Build the project-owned renderer:

```bash
Scripts/UE5/build_unreal_renderer.sh
```

The build/open scripts resolve the engine from
`UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject` instead of hard-coding a UE
version. Current association is `5.5`, and the verified normal editor path is:

```text
D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe
```

UE 4.27 scene packs use `UE4Editor.exe` / `UE4Editor-Cmd.exe`; do not report
4.27 as missing merely because `UnrealEditor.exe` is absent.

Open the editor or standalone game:

```bash
Scripts/UE5/open_unreal_renderer.sh
Scripts/UE5/open_unreal_renderer.sh game
```

If the standalone game window was already open before a C++ or camera-control
change, restart only that game window:

```bash
RESTART_UNREAL_GAME=1 Scripts/UE5/open_unreal_renderer.sh game
```

Manual review controls:

```text
W / A / S / D     move review camera
Q / E             move down / up
Arrow keys        rotate view
Hold right mouse  drag to look around
Shift             faster movement
Ctrl              slower movement
```

## MCP Use

Expected MCP server name:

```text
mosim-unreal
```

Current policy: `mosim-unreal` is MoSim's own UE automation MCP. It should not
be a generic world-building MCP and should not own Epic/Fab downloads.
`mosim-epic` remains the separate inventory and scene-source readiness MCP.

Current `mosim-unreal` tools:

```text
ue_health
project_context
editor_listener_health
asset_search
list_maps
current_level_summary
find_level_actors
reversible_actor_probe
scene_source_status
scene_truth_export_plan
editor_log_summary
tool_boundary
```

Current `mosim-epic` tools:

```text
epic_library_inventory
epic_scene_library_view
scene_source_registry
scene_source_acceptance
scene_truth_export_plan
tool_boundary
```

Wrapper layout:

```text
Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh
  -> Docs/Skills/Unreal/mosim-unreal/wrappers/wsl.sh
  -> Docs/Skills/Unreal/mosim-unreal/mcp/server.py
```

Legacy rollback wrapper:

```text
Docs/Skills/Unreal/mosim-unreal/wrappers/legacy_flopperam_wsl.sh
```

Do not remove the legacy wrapper until the MoSim-native route has equivalent
read-only scene query, controlled actor edit, viewport capture, and editor-log
coverage. The current native route intentionally starts with stable MoSim
workflow tools rather than Flopperam's broad `create_town/create_castle` style
tool surface.

Open-source MCP audit decision:

| Source | Adopt | Reject For Phase 1 |
|---|---|---|
| `Docs/Skills/Unreal/mcp/Unreal_mcp-dev` | tool registry, schema discipline, C++ bridge, transport and safety patterns | broad game/GAS/networking/inventory tools |
| `Docs/Skills/Unreal/mcp/UnrealClientProtocol` | reflection and future Blueprint/graph editing ideas | arbitrary reflection as the default public tool |
| `Docs/Skills/Unreal/mcp/UnrealClaude` | game-thread task queue, project context, log/viewport ideas | Claude-specific chat/product shell and default script execution |
| `Docs/Skills/Unreal/mcp/UnrealGenAISupport` | small actor/Blueprint utility examples | inactive/broad GenAI plugin assumptions |
| `Docs/Skills/Unreal/mcp/unreal-engine-mcp` | rollback bridge and existing live-editor smoke path | final MoSim interface shape |

Target architecture:

```text
Codex / MCP client
  -> MoSim stdio or HTTP MCP server
  -> TCP/WebSocket/HTTP bridge
  -> C++ UE Editor plugin
  -> UE AssetRegistry / GEditor / PIE / package APIs on the editor thread
```

Phase order:

1. Read-only: `ue_health`, `project_context`, `asset_search`, `list_maps`,
   `current_level_summary`, `find_level_actors`, `editor_listener_health`,
   `editor_log_summary`, `scene_source_status`, and
   `scene_truth_export_plan`.
2. Controlled writes: `reversible_actor_probe` first. It defaults to plan-only;
   persistent map open/save, material instance parameter edits, and viewport
   capture remain later tools.
3. Simulator truth: collision/semantic/occupancy export and validation.
4. Advanced authoring: minimal Blueprint/material graph edits.

Do not implement arbitrary `python_execution`, Launcher button-clicking, raw
webcache parsing, OAuth/token reuse, or automatic Fab downloads in
`mosim-unreal`.

Before interactive editor work, run the smallest useful probe. Inventory alone
is not enough; the editor-side listener must be reachable:

```bash
Scripts/UE5/build_unreal_renderer.sh
Scripts/UE5/open_unreal_renderer.sh editor
python3 Scripts/UE5/probe_unreal_mcp_listener.py --wrapper-route-only --timeout 1
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-level --timeout 2 --limit 5
```

If the probe fails, do not keep calling actor/Blueprint tools. Fix the editor
listener or continue with file-level work only.

After the listener is reachable, verify actual edit authority with the
reversible editor round-trip probe:

```bash
uv run python Scripts/UE5/probe_unreal_editor_mcp_tools.py \
  --json-output Results/tmp/unreal_mcp_editor_probe_<date>.json
```

When a linked scene source is active, prefer the scene-source scoped probe:

```bash
uv run python Scripts/UE5/probe_linked_scene_source_mcp.py \
  --json-output Results/tmp/linked_scene_source_mcp_probe_latest.json
```

This script uses the same UnrealMCP editor socket as the `mosim-unreal` MCP
server. It reads level actors, spawns a temporary uniquely named
`MoSimMcpProbe_DoNotSave_*` static mesh actor, changes its transform, deletes
it, and checks cleanup. A passing listener probe alone is not enough to claim
map-edit capability; this round trip is the minimum evidence for live UE scene
modification. Do not reuse a fixed probe actor name in the same editor session:
UE can retain deleted actor names internally and may crash while generating a
unique name.

Do not run write probes on the engine default Entry map. The reversible probe
now refuses `/Engine/Maps/Entry` by default and also refuses to write when the
current map cannot be identified. Load the target review map first, then run the
scene-source scoped probe. If UE shows a recovery package for `Entry` after a
probe crash, choose **Skip Recovery** and remove ignored `Saved/Autosaves`
artifacts before reopening the editor. Only use `--allow-entry-map` or
`--allow-unknown-map` for deliberate smoke tests, not for normal scene-source
acceptance evidence.

Current known project-owned renderer requirement:

```text
UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject
AdditionalPluginDirectories must include:
../../Docs/Skills/Unreal/mcp/unreal-engine-mcp/FlopperamUnrealMCP/Plugins
```

If this path drifts after repository restructuring, the editor may open but
`UnrealMCP` will not compile/load, and actor tools will time out.

## MWORKS Playback Route

After a map passes visual review, MWORKS playback can be streamed through:

```bash
python3 Scripts/UE5/stream_unreal_udp.py <raw.csv> --host 127.0.0.1 --port 5005
```

Expected packet schema:

```text
quadrotor.unreal_state.v1
```

Coordinate policy:

```text
MWORKS: X/Y/Z in meters, roll/pitch/yaw in radians
Unreal: centimeters, with renderer-side coordinate conversion
```

Do not change simulation units or planner truth to satisfy rendering.

## Quality Rules

1. Unreal cannot change controller output, planner truth, collision metrics, or
   event logs.
2. Visual obstacles must eventually have explicit collision/planner truth
   mappings. A pretty obstacle with no truth proxy is a renderer bug.
3. Claims about local planning, radar occlusion, or avoidance require MWORKS or
   algorithm evidence, not only a rendered scene.
4. Large Fab/Epic asset downloads and runtime caches stay ignored unless a
   small, reviewed subset is intentionally promoted.
5. Do not commit generated Unreal build outputs.

## FAST-LIO Factory Diagnosis Gate

Factory FAST-LIO must pass a diagnosis gate before it is used as localization,
mapping, planner, or controller evidence. Topic existence is not sufficient:
the current Factory recordings publish `/odometry`, `/path`, and
`/cloud_registered`, but the measured localization error is still too large.

Run the diagnosis from the project root:

```bash
python3 Scripts/UE5/diagnose_fastlio_factory_failure.py
python3 Scripts/tests/test_fastlio_factory_failure_diagnosis.py
```

Current evidence paths:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md
Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_failure_diagnosis.json
```

Do not proceed from Factory FAST-LIO into planner closure until the report no
longer marks the scene as `not_claimable`. The current blockers are
Velodyne-like FAST-LIO config (`lidar_type=2`, `scan_line=16`) against a
Mid360/Livox target, low-density evaluated input of about 509 points/frame,
synthetic finite-difference IMU, missing per-point attributes in the evaluated
dataset, fixed yaw excitation, and nonmonotonic odometry timestamps.

## FAST-LIO Input Contract Gate

Before launching another Factory FAST-LIO run, check the input contract:

```bash
python3 Scripts/UE5/check_fastlio_input_contract.py \
  --scene-dir Results/unreal_scene_mapping/factoryenvironmentcollect \
  --config Config/ros2/mosim_spark_fast_lio_mid360.yaml \
  --output-json Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_input_contract.json \
  --output-md Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_INPUT_CONTRACT.md
python3 Scripts/tests/test_fastlio_input_contract.py
```

Current ROS2 FAST-LIO defaults now use the MoSim Mid360 route:

```text
config: Config/ros2/mosim_spark_fast_lio_mid360.yaml
lidar topic: /mosim/lidar_points
imu topic: /mosim/forward/imu
lidar frame: base/mid360_link
imu frame: base/forward_imu_optical_frame
mapping smoke lidar topic: /mosim/mapping_smoke/lidar_points
```

`/mosim/lidar_points` is reserved for the dense Mid360/FAST-LIO input. The
older sparse visualization-only mapping replay uses
`/mosim/mapping_smoke/lidar_points` in ROS2 so it cannot be confused with
claimable FAST-LIO input.

The dense Factory Livox-like replay is now contract-ready as sensor input:
about 20.5k points/frame, line ids 0-3, and per-point `offset_time_ns`,
`line`, `reflectivity`, and `tag`. The old `fastlio_replay_dataset.jsonl` is
not acceptable for localization claims because it has only 512 points/frame,
no per-point Livox attributes, and synthetic finite-difference IMU. The next
implementation step is to route the dense Mid360 frames and high-rate
MWORKS/PX4-equivalent IMU into the selected ROS2 FAST-LIO runtime, then rerun
truth-error evaluation.

Factory ROS2 replay now uses the dense route for FAST-LIO inputs when both
artifacts exist:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/livox_like_lidar_frames.jsonl
Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv
```

Dry-run evidence:

```bash
DRY_RUN=1 MAX_FRAMES=2 LOOP=0 START_RVIZ=0 \
  Scripts/UE5/run_fastlio_rviz_replay_ros2.sh factoryenvironmentcollect
```

Expected status includes `USE_DENSE_MWORKS_FASTLIO_INPUT=1` and
`mid360_density_claimable=true`. Derelict now has the same dense Mid360 replay
gate and should also report `USE_DENSE_MWORKS_FASTLIO_INPUT=1`.

Derelict contract evidence:

```text
Results/unreal_scene_mapping/derelictcorridormegascans/livox_like_lidar_frames.jsonl
Results/unreal_scene_mapping/derelictcorridormegascans/FASTLIO_INPUT_CONTRACT.md
```

The current Derelict dense sample averages about 24.3k points/frame and is
sensor-input ready, but it remains blocked for localization claims until the
FAST-LIO runtime uses synchronized high-rate IMU and passes truth-error
metrics.

Current implementation blocker:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_MID360_RUNTIME_BLOCKER.md
```

The local ROS2 `spark-fast-lio` candidate does not accept `lidar_type=1`
Livox/Mid360 data through its `sensor_msgs/PointCloud2` preprocessing path. It
handles `OUST64`, `KMOUST64`, and `VELO16`; Livox support is guarded behind a
CustomMsg compile path. A Factory dense Mid360 runtime smoke produced zero
FAST-LIO output topics and logged `Error LiDAR Type`. Therefore the next
runtime proof must first solve FAST-LIO implementation/message compatibility:
Livox `CustomMsg` support, a different Mid360-capable FAST-LIO runtime, or a
clearly degraded non-Mid360 smoke. Do not treat RViz visualization tuning as a
fix for this blocker.

## FAST-LIO Runtime Candidate Gate

Before selecting or patching a FAST-LIO runtime, run:

```bash
python3 Scripts/UE5/check_fastlio_runtime_candidates.py --write
python3 Scripts/tests/test_fastlio_runtime_candidates.py
```

Current report:

```text
Results/unreal_scene_mapping/FASTLIO_RUNTIME_CANDIDATES.md
Results/unreal_scene_mapping/FASTLIO_RUNTIME_CANDIDATES.json
```

Current decision is `patch_ros2_livox_custommsg_candidate_first`. The local
`spark-fast-lio` package is the only native ROS2 FAST-LIO-family candidate, but
it is a patch target rather than a claimable Mid360 runtime. The scan reports:

- standard `PointCloud2` path rejects Livox/Mid360 `lidar_type=1`;
- Livox CustomMsg code exists but is guarded;
- driver package/header naming mixes ROS1 `livox_ros_driver` and ROS2
  `livox_ros_driver2` conventions;
- one Livox callback macro is inconsistent.

Therefore the next valid runtime work is patch/build/prove this CustomMsg path
or switch to another Mid360-capable implementation. ROS1 `FAST_LIO` and Sunray
Livox Gazebo code remain strong semantic references or bridge candidates, but
they are not direct Ubuntu 22.04/ROS2 runtime evidence.

## 2026-06-02 Real UAV Stack Review Rule

Do not continue the rejected display-first mapping route. The following are
smoke-only and cannot be used as product evidence:

- keyboard movement that changes pose by a map-cell step;
- static or synthetic point clouds;
- a 2D-only occupancy-grid window;
- point-size or marker-size tuning as a substitute for FAST-LIO/local-map
  correctness;
- lowering point density only to make a fake visualization smoother.

Keyboard mappings may remain in UE/RViz review tools, but they control only the
view/camera. They must not move the UAV, overwrite MWORKS truth, publish
synthetic UAV odometry, or stand in for controller/setpoint input.

Manual-control demos must send continuous setpoints into the MWORKS/controller
layer. They must not overwrite UAV pose. Product review may open UE/RViz2 only
after the headless gate proves:

```text
MWORKS continuous state/truth
  + 200Hz IMU
  + 10Hz Mid360 baseline LiDAR with per-point timing
  + coherent TF/extrinsics
  + nonzero FAST-LIO registered cloud, odometry, and path
  + 3D local map topic
```

The accepted visual layout remains separate native windows:

```text
UE window
  -> accepted rendered Factory/Derelict scene, UAV body, smooth motion

RViz2 FAST-LIO window
  -> raw Livox cloud, registered cloud, odometry, path, TF

RViz2 local-map/planner window
  -> rotatable 3D voxel/SDF/ESDF-style local map and local plan
```

RflySim uses the same role split: CopterSim/PX4 handles dynamics/control,
RflySim3D/UE renders and generates perception data, and ROS/upper-layer
programs consume image, depth, and point-cloud streams. MoSim should mirror
that boundary with MWORKS replacing CopterSim as the solver/controller
authority.

## Factory UAV Platform Review

Before any point-cloud or FAST-LIO window review, Factory must first pass the
UE-only UAV platform gate:

```bash
Scripts/UE5/review_factory_uav_platform.sh
```

This script activates `local_factoryenvironmentcollect`, opens
`/Game/Maps/Demonstration` in `simulation-review`, waits for the bridge UDP
receiver on port 5005, and streams `render_replay.csv` to the
`AQuadrotorMworksPlaybackActor` visible UAV body. It does not open RViz/RViz2,
does not send the old hand-built point-cloud/grid overlays, and does not let
keyboard/mouse input drive UAV pose.

The Factory stream must use:

```text
--coordinate-policy mworks_world_m_z_up
```

Reason: the Factory collision-truth artifact declares
`mworks_x=unreal_x, mworks_y=-unreal_y, mworks_z=unreal_z`. The accepted
Factory review camera at approximately `UE (-5533, +2423, 190) cm` corresponds
to MWORKS/truth coordinates `(-55.33, -24.23, 1.90) m`. If the Factory replay
is streamed as `ue_world_m_z_up`, the UAV appears on the wrong Y side of the
scene and the manual review becomes misleading.

Manual acceptance for this gate is limited to:

- visible blue UAV body in the accepted Factory scene;
- UAV motion comes from the MWORKS/Bridge replay stream;
- keyboard/mouse controls only the review camera/view;
- UAV starts in the usable factory area and does not visibly clip through
  scene geometry.
