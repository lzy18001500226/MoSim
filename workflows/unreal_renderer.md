# Unreal Renderer Workflow

Unreal is a render-only layer. MWORKS/Sysplorer remains the simulation source
of truth for dynamics, control, planning, collision checks, and metrics.

## Asset-First Rendering Policy

Do not build the final Unreal scene by hand from low-poly boxes unless the goal
is a short collision/debug smoke test. The renderer must be asset-first:

```text
existing scene/model assets
  -> asset registry
  -> Unreal placement/material/collision proxy
  -> MWORKS state playback
  -> video review
```

MWORKS remains the truth source. Unreal is allowed to improve scene quality,
materials, camera, radar visualization, trail rendering, and video export. It is
not allowed to change controller output, planner truth, collision metrics, or
event logs.

Current asset-source priority:

| Priority | Source | Use |
| --- | --- | --- |
| P0 | `references/Sunray/simulation/sunray_simulator/models` | Immediate reusable Gazebo/SDF assets: Sunray150/Mid360, houses, trees, windows, gates, targets, terrain, AWS RoboMaker residential/retail assets |
| P0 | `references/Sunray/simulation/sunray_simulator/worlds/*.world` and `references/Sunray/simulation/sysu_competition/worlds/*.world` | Existing scene layout references such as competition maps, planning tests, houses, airport, outdoor, sand island |
| P1 | RflySim3D / RflySimUE installer or asset package, if available locally | UE-style scenario, camera, UDP/display workflow reference; reuse assets only after license/source confirmation |
| P1 | RflySim public GitHub repos | Interface/modeling reference, not primary visual assets. `CopterSim` is mainly Simulink multicopter/HIL model; `RflyExpCode` is experiment code |
| P2 | UE Marketplace / open UE environment assets | Optional visual upgrade after license and file-size checks |

Important finding: the public RflySim GitHub repositories inspected so far do
not contain a complete UE scene asset project. They are still useful for MBD,
MAVLink/HIL, fault-injection, and UDP/display interface ideas. `CopterSim` is a
Simulink multicopter model with MAVLink/PX4/HIL/fault-injection ports; it is not
a render scene repository. `RflyExpCode` is course/experiment code and also is
not a UE environment asset repository. For final visual quality, use the local
Sunray/AWS assets first, or ask the user to provide a local RflySim3D/RflySimUE
asset install if direct RflySim scene reuse is needed.

When the user installs RflySim locally, do not immediately copy files into this
project. First audit the install directory for:

```text
RflySim3D / RflySimUE / RflySimUE5 executable or project
Content / Paks / Maps / Plugins / Source / Config directories
RflySimAPIs / Python / MATLAB / Simulink communication examples
UDP / shared-memory / JSON / binary protocol examples
license / third-party notices / redistribution restrictions
single files larger than 100 MB
```

Classify the result before importing:

| Finding | Action |
| --- | --- |
| UE project with `.uproject`, `Content/`, `.umap`, meshes, materials | Candidate for direct scene reuse after license and size check |
| Cooked packaged executable only, no editable assets | Use as visual/reference target only; do not depend on direct asset import |
| API examples only | Port the UDP/shared-memory protocol ideas into `QuadrotorMworksBridge` |
| Large `.pak`, video, installer, or binary assets | Keep outside Git; document external dependency and local path |
| No license or unclear redistribution terms | Do not commit assets; use only as implementation reference |

### Local RflySim Audit: `D:\PX4PSP`

The user-installed RflySim tree at `D:\PX4PSP` is useful, but it must stay an
external dependency. Do not copy the tree into this repository and do not commit
RflySim `Content/` assets directly. Several RflySim3D files are larger than
100 MB, including built-data and texture payloads, so wholesale import is not
Git-safe.

Useful local entry points:

| Local path | Use |
| --- | --- |
| `D:\PX4PSP\RflySim3D\RflySim3D.exe` | Existing RflySim3D renderer executable |
| `D:\PX4PSP\RflySim3D\RflySim3D\RflySim3D.uproject` | UE project-style entry for scene inspection |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\*.umap` | Existing maps such as `MapData`, `MapSmall`, `MatchScene`, `MatchScene2025`, `MountainTerrain`, `OldFactory`, `CameraRoom`, `ExhibitionHall` |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\FSJ150\XML` | Small quadrotor visual model references |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\obstacle` | Box obstacle XML/PNG references |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\ExhibitionHall\XML` | Trees, stones, city, factory, solar panel, windmill, and power-tower visual references |
| `D:\PX4PSP\RflySimAPIs\RflySimSDK\ue\UE4CtrlAPI.py` | UDP command and pose-update API for RflySim3D |
| `D:\PX4PSP\RflySimAPIs\RflySimSDK\vision\VisionCaptureApi.py` | Camera, lidar, point-cloud, and Mid360-style sensor request API |
| `D:\PX4PSP\RflySimAPIs\3.RflySim3DUE` | RflySim3D command, map, model-load, viewport, collision, weather, and trajectory examples |
| `D:\PX4PSP\RflySimAPIs\8.RflySimVision` | Vision, lidar, Livox/Mid360, direct UDP, ROS bridge, SLAM, and ESDF/path-planning examples |
| `D:\PX4PSP\RflySimAPIs\10.RflySimSwarm` | Multi-UAV and swarm display/control references |

Most relevant RflySim3D examples:

```text
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/1.UECtrlPy/PythonSendUE4Pos.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/1.UECtrlPy/PythonSendUE4ExtDemo.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/3.LoadModelsByTxt/LoadModelsByTxt.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/4.TrajDemo/UE4MapTerrainDemo.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/6.RflySim3DViewPortDemo/UE4ViewPortDemo.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/9.RflySim3DPosGet/GetUE4PosAPI.py
3.RflySim3DUE/0.ApiExps/e5_UEMapCtrl/2.TargetCreatePy/code/TargetCreateDemo.py
3.RflySim3DUE/0.ApiExps/e5_UEMapCtrl/3.TargetPlace/code/TargetPlace.py
3.RflySim3DUE/0.ApiExps/e9_RflySim3DCollision
```

Most relevant vision/lidar examples:

```text
8.RflySimVision/0.ApiExps/10.Mid360Demo
8.RflySimVision/0.ApiExps/1-UsageAPI/3.PointCloudAPI
8.RflySimVision/0.ApiExps/1-UsageAPI/4.SendProtocolAPI
8.RflySimVision/0.ApiExps/4.Point-CloudVisualize
8.RflySimVision/0.ApiExps/7.LidarLivoxDemo
8.RflySimVision/2.AdvExps/e16_ESDFPathPlan
```

Confirmed communication facts from the local SDK:

| Item | Finding |
| --- | --- |
| RflySim3D command channel | `sendUE4Cmd(...)` sends UDP commands to `20010 + windowID` |
| RflySim3D pose channel | `sendUE4Pos(...)`, `sendUE4PosNew(...)`, `sendUE4PosFull(...)` create or update a vehicle by `copterID` and `vehicleType` |
| Rotor visual input | `sendUE4Pos(...)` accepts `MotorRPMSMean`; `sendUE4PosFull(...)` accepts eight motor RPM values |
| Scene switch | `RflyChangeMapbyName <map>` |
| Model switch | `RflyChange3DModel <CopterID> <veTypes>` |
| Camera/view | `RflyChangeViewKeyCmd`, `RflyCameraPosAng`, `RflyCameraFovDegrees` |
| Text overlay | `RflyShowTextTime`, `RflyShowText` |
| Terrain query | `RflyScanTerrainH ...` |
| Sensor request channel | Vision sensor requests are sent to the RflySim3D window and can return shared-memory or UDP data |
| Mid360 example | `TypeID=23`, `DataWidth=64`, `DataHeight=272`, `DataCheckFreq=10`, UDP return port example `9999` |

Candidate integration path after MWORKS evidence is stable:

```text
MWORKS raw/native result
  -> project bridge reads time, position, attitude, motor commands, local plan
  -> RflySimSDK UE4CtrlAPI sends vehicle pose/RPM to RflySim3D
  -> optional VisionCaptureApi requests Mid360/camera data for render-side display
  -> video review
```

This is an external-renderer route, not a replacement for the current UE bridge.
Use it only if the local RflySim3D scenes produce better video faster than
building a project-owned UE scene.

Do not rely on RflySim for controller truth unless a future task explicitly
builds and validates a bidirectional co-simulation. For the current competition
evidence chain, RflySim can only be:

1. a visual renderer driven by MWORKS results;
2. a protocol/API reference for our own Unreal bridge;
3. a source of scene and sensor design ideas, subject to license and file-size
   checks.

Repository crawl priority:

| Priority | Repository / source | Decision |
| --- | --- | --- |
| P0 | User-installed RflySim3D/RflySimUE/RflySimUE5 folder | Highest value if it contains editable scenes or protocol docs |
| P0 | Local `references/Sunray/simulation/sunray_simulator/models` and `worlds` | Already available; convert SDF/DAE/PNG assets into UE scene registry |
| P1 | Cosys-AirSim | Best AirSim-line candidate if we want a maintained Unreal plugin/API reference |
| P1 | Colosseum | AirSim-line open-source Unreal robotics simulator; inspect for reusable plugin/scene patterns |
| P1 | CARLA-Air | Strong UE urban-scene candidate for air-ground scenes, but likely heavy and Linux-oriented |
| P1 | `RflySim/CopterSim` | Clone only if we need model/HIL/fault-injection reference; not for scene visuals |
| P1 | `RflySim/RflyExpCode` | Clone only if we need RflySim workflow examples or course docs |
| P2 | Flightmare / FlightGoggles | Unity render/physics decoupling references; useful conceptually, less direct for UE5 |
| P2 | Pegasus Simulator | High-quality Isaac Sim/PX4 reference, but dependency stack is heavy and not aligned with UE5 |
| P3 | RotorS / XTDrone / Gazebo-only stacks | Use for multi-UAV, ROS/PX4, planning organization; not for final visual layer |

Open-source simulator reference notes:

| Platform | Engine | Useful for this project | Main risk |
| --- | --- | --- | --- |
| Cosys-AirSim | Unreal | Maintained AirSim-style Unreal plugin, drone/car APIs, PX4/HIL-style visual simulation ideas | Still a simulator stack; we should port only rendering/API patterns, not replace MWORKS |
| Colosseum | Unreal/Unity support | AirSim successor-style robotics simulator; useful for API, sensor, and UE integration patterns | Need inspect asset availability and license before reuse |
| CARLA-Air | Unreal | High-fidelity urban environments with drones in a CARLA world; useful if we want city/road scenes | Heavy; likely overkill for competition video unless prebuilt assets are easy to reuse |
| AirSim | Unreal/Unity | Mature API and UE plugin design; useful for camera/weather/segmentation/control examples | Upstream Microsoft repo is archived/no longer updated, so avoid making it the main dependency |
| Flightmare | Unity | Strong example of decoupling physics and rendering; good design reference for MWORKS + external renderer | Unity, not UE; less direct asset reuse |
| FlightGoggles | Unity/ROS | Photorealistic HIL agile-flight visualization reference | ROS/Unity stack, not aligned with current UE5 bridge |
| Pegasus Simulator | Isaac Sim | Modern multi-UAV/PX4/sensor simulation reference | Isaac/Omniverse is too heavy for the current workflow |
| XTDrone / RotorS | Gazebo | Multi-UAV organization, PX4/ROS interface, swarm examples | Gazebo visuals are not the desired final video layer |

For the current project, do not crawl all of these by default. Crawl only when
the target use is clear:

```text
need UE API/plugin reference       -> Cosys-AirSim or Colosseum
need high-quality urban UE scene   -> CARLA-Air / CARLA asset route
need render/physics decoupling     -> Flightmare
need agile-flight gate/drone logic -> Agilicious / FlightGoggles references
need ROS/PX4 multi-UAV organization -> XTDrone / RotorS
```

If RflySim download remains blocked, the recommended fallback is:

```text
Cosys-AirSim or Colosseum for Unreal API/sensor/rendering patterns
  + local Sunray/AWS Gazebo assets for actual scene meshes
  + project-owned QuadrotorMworksBridge for MWORKS state playback
```

## Gazebo Architecture Lessons

Gazebo is useful as an architecture reference even if it is not the final video
renderer. The important lesson is separation of concerns:

```text
backend server:
  physics system + sensor system + user command system + scene broadcaster

frontend client:
  GUI plugins + 3D view + visualization widgets

shared libraries:
  gz-physics + gz-rendering + gz-sensors + gz-transport + sdformat
```

This is why Gazebo can run efficiently with many visual objects:

1. Physics is a compiled native plugin, not a symbolic Modelica/Sysblock
   equation system containing all visual geometry.
2. Visual meshes and collision geometry are separate. A detailed `.dae` mesh can
   be rendered while physics uses a simpler collision proxy.
3. The GUI/client can be separated from the server/backend. Headless or reduced
   GUI runs avoid rendering overhead during batch simulation.
4. Rendering is handled by a rendering library and plugins such as OGRE /
   OGRE2 / OptiX, not by thousands of dynamic model components in the solver.
5. Sensors are plugin systems. Rendering sensors such as cameras and GPU lidar
   use the rendering pipeline, while physics/contact sensors can use physics
   state. Sensor update rates can be lower than the physics step.
6. Transport messages broadcast pose, scene, sensor, and command data across
   process boundaries instead of coupling every visual object into the dynamics
   equations.

For this project, copy the architecture pattern, not Gazebo itself:

```text
MWORKS/Sysplorer:
  closed-loop dynamics, controller, planner, fault/safety truth

external renderer:
  UE5 scene, materials, camera, radar visualization, video

transport:
  TCP/UDP state frames or raw/native result playback

asset registry:
  visual mesh + material + collision proxy + truth obstacle id
```

Do not push dense terrain blocks, thousands of obstacle visuals, local radar
overlays, or camera behavior into the Sysplorer solver layer. Keep Sysplorer
animation as a low-complexity audit view and move video-quality rendering to
the external renderer.

Official Gazebo documentation entry points for study:

| Topic | Official source |
| --- | --- |
| Gazebo Sim architecture | `https://gazebosim.org/docs/harmonic/architecture/` |
| Gazebo documentation source repo | `https://github.com/gazebosim/docs` |
| Gazebo Rendering library | `https://gazebosim.org/libs/rendering/` |
| Gazebo Sensors library | `https://gazebosim.org/libs/sensors/` |
| Gazebo Physics plugin docs | `https://gazebosim.org/api/physics/9/physicsplugin.html` |
| Gazebo Sim physics engine selection | `https://gazebosim.org/api/sim/8/physics.html` |

There is no single authoritative PDF manual for current Gazebo Sim. The
official manual is the versioned website plus the `gazebosim/docs` repository.
If a local copy is needed for offline study, clone only the docs repository or
only the `harmonic/` and `common/` folders; do not commit built HTML, generated
Sphinx output, videos, or downloaded Gazebo Fuel assets.

Before importing any external scene asset, check:

1. license and attribution;
2. single-file size under GitHub limit;
3. mesh scale and coordinate axes;
4. material and texture dependencies;
5. collision proxy availability;
6. actor count, triangle count, texture memory, and LOD/performance risk.

Generated primitives remain useful for:

- collision truth debugging;
- planner occupancy visualization;
- radar sector and local-map overlays;
- fallback review scenes when asset conversion fails.

They are not the target visual quality for the final video.

## Project

Open:

```text
unreal/MworksUnrealRenderer/MworksUnrealRenderer.uproject
```

From WSL, use the project-local launcher:

```bash
scripts/build_unreal_renderer.sh
scripts/open_unreal_renderer.sh
```

Override `UE_EDITOR` only if Unreal is installed somewhere other than
`D:\Program Files\Epic Games\UE_5.7`.

When C++ files under `unreal/QuadrotorMworksBridge/Source` change, close the
running Unreal Editor before rebuilding. Otherwise Windows keeps
`UnrealEditor-QuadrotorMworksBridge.dll` locked and UBT will fail at the link
step.

The project enables:

```text
unreal/QuadrotorMworksBridge
Skills/unreal-engine-mcp/FlopperamUnrealMCP/Plugins/UnrealMCP
```

Do not copy engine binaries, `Binaries/`, `Intermediate/`, `Saved/`, packaged
builds, or Derived Data Cache into Git.

## Data Flow

```text
MWORKS raw CSV / native result
  -> scripts/stream_unreal_udp.py
  -> udp://127.0.0.1:5005
  -> QuadrotorMworksUdpReceiverComponent
  -> QuadrotorMworksPlaybackComponent
  -> UAV actor, propellers, radar material, local plan spline, trajectory trail, follow camera
```

The packet schema is `quadrotor.unreal_state.v1`.

## Map Export

Generate the render-only map JSON before building or refreshing the UE scene:

```bash
python3 scripts/export_unreal_scene_map.py --terrain-cell-m 1.0
```

Output:

```text
unreal/MworksUnrealRenderer/Content/MworksData/map_open_blocks_render_map.json
```

This JSON uses the same `map_open_blocks.yaml` random obstacle and L/T wall
expansion as the planner. It contains map bounds, terrain height grid, random
obstacle columns, wall boxes, start/goal, and material tags. It is display
input only and must not feed back into MWORKS.

For high-quality Unreal scenes, generate a second registry instead of only a
primitive map:

```text
scene_asset_registry:
  source_world: existing .world / handcrafted scenario profile
  asset_refs: mesh/material/texture references
  placements: transform + semantic tag
  collision_proxies: simplified boxes/capsules/convex hulls
  mworks_truth_link: obstacle_id / wall_id / gate_id
```

This registry is the bridge between SDF/world assets and Unreal actors. The
planner uses truth geometry from MWORKS/scenario files; Unreal uses the registry
to show a better-looking equivalent scene.

Preferred asset conversion path:

```text
Gazebo .world / .sdf
  -> parse model:// references, pose, scale, mesh URI
  -> resolve .dae/.stl/.png under references/Sunray/...
  -> convert mesh/materials through Blender/Assimp or UE import
  -> write scene_asset_registry with original source path and license tag
  -> spawn UE actors from registry
  -> link each visual actor to MWORKS obstacle_id / gate_id / terrain_id
```

Do not let the imported scene become the planning source of truth. If a tree,
building, gate, wall, or frame is visible in UE, it must have a corresponding
`world_geometry` primitive or collision proxy in the scenario file before it is
used for planning/collision claims.

## Playback

Stream the current planning raw CSV:

```bash
python3 scripts/stream_unreal_udp.py \
  results/planning/single_obstacle_astar_awff/sunray150_planning_open_blocks_linear_mpc_sysblock/raw/sunray150_planning_open_blocks_linear_mpc_height_profile_0p2_sensor_20hz.csv \
  --host 127.0.0.1 \
  --port 5005 \
  --scene-id planning_open_blocks_ue_review \
  --map-id map_open_blocks \
  --fps 20 \
  --near-radius-m 6 \
  --far-radius-m 9 \
  --fov-deg 120
```

Use `--dry-run --max-frames 2` to validate packets without sending UDP.

## UE Actor Setup

Minimum scene actors:

1. `AQuadrotorMworksPlaybackActor`
   - owns `QuadrotorMworksUdpReceiverComponent`;
   - owns `QuadrotorMworksPlaybackComponent`;
   - applies position/attitude from latest frame;
   - exposes propeller visual angles, `LocalPlanPointsUnreal`,
     `TrajectoryTrailUnreal`, reference point, and radar sector parameters.
2. `AQuadrotorMworksMapActor`
   - reads `Content/MworksData/map_open_blocks_render_map.json`;
   - instantiates stepped terrain, random obstacle columns, and L/T wall box
     segments with instanced static meshes;
   - exposes map bounds and obstacle counts;
   - serves as the stable anchor for generated map visualization.

Blueprints/materials should read from these actors rather than parsing raw CSV
again inside Unreal.

## Manual Review Checklist

Before recording or comparing against Sysplorer animation, check these items in
the Unreal viewport:

| Item | Expected result |
| --- | --- |
| UAV body | visible, centered on the MWORKS state, no scale mismatch |
| Propellers | four propellers visible and rotating from motor commands |
| Static map | terrain, random columns, and L/T walls visible from `AQuadrotorMworksMapActor` |
| Coordinate direction | start is lower-left, goal is upper-right, no X/Y swap |
| Local plan | spline starts at UAV center and stays in front of the current pose |
| Trail | history line follows the UAV, no detached yellow marker behavior |
| Radar sector | yaw follows UAV heading, radius and FOV match packet metadata |
| Camera | one follow view and one overview view are usable without manual dragging |
| Performance | playback is smooth enough for video; if viewport interaction stutters, export video rather than lowering MWORKS evidence fidelity |

If any item fails, fix Unreal rendering first. Do not alter MWORKS controller,
planner, or metrics to hide a renderer issue.

## Verification

Run:

```bash
python3 scripts/check_unreal_bridge.py
scripts/build_unreal_renderer.sh
python3 scripts/export_unreal_scene_map.py --terrain-cell-m 1.0
python3 scripts/stream_unreal_udp.py <raw.csv> --max-frames 2 --dry-run
```

If Unreal MCP is available, open the project first, then run a read-only probe
such as project context or scene brief. If the wrapper hangs or the editor is
not listening, do not modify the scene through MCP; continue with source-level
changes and report the MCP state.

Current WSL note: the Unreal editor plugin starts its TCP server on Windows
`127.0.0.1:55557`. A Python MCP server running inside WSL may not reach that
Windows loopback address directly. If `get_actors_in_level` reports
`Connection refused` while the UE log says `Server started on 127.0.0.1:55557`,
the plugin is loaded and the remaining issue is the WSL-to-Windows loopback
path. Use source-level C++ work or run the Python MCP server from Windows until
the plugin host binding is changed.

## Boundaries

- Coordinate conversion happens in Unreal only.
- Unreal may improve colors, terrain material, radar sector, local plan spline,
  trails, camera, and video capture.
- Unreal must not modify planner truth, controller output, metrics, or event
  logs.
