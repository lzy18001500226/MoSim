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

Current decision: do not keep porting the old Sysplorer/MWORKS blocky visual
map into Unreal as the primary video route. That map was a workaround for
MWORKS GUI limits. Before implementing more Unreal scene work, first understand
and experience RflySim itself:

```text
RflySim docs/API audit
  -> run native RflySim3D/CopterSim examples
  -> inspect scene/map/sensor parameter availability
  -> decide direct RflySim playback vs project-owned Unreal renderer
```

The first milestone is not "copy assets". It is to answer whether RflySim can
provide stable renderer behavior, scene parameters, vehicle visual models,
Mid360/lidar data, terrain service, and path-planning examples that are better
than the current project-owned renderer.

`D:\PX4PSP\HowToUse.pdf` establishes the official learning route:

1. Start with chapters `1.RflySimIntro` and `2.RflySimUsage` only as platform
   orientation.
2. For this project, jump directly to:
   - `3.RflySim3DUE` for scene/model loading, RflySim3D commands, terrain
     service, collision, camera/view, and UE-style rendering behavior;
   - `6.RflySimExtCtrl` for external control, trajectory, and MAVLink/UDP
     command interfaces;
   - `8.RflySimVision` for camera, depth, lidar, Mid360, point cloud, and
     perception-control loops;
   - `10.RflySimSwarm` for multi-UAV display, networking, and formation
     references.
3. Use each chapter in the official order `Intro.pdf -> PPT.pdf -> API.pdf ->
   Index.pdf -> selected Readme.pdf`. Do not start by editing our Unreal scene.
4. `HowToUse.pdf` also confirms RflySim3D accepts UDP commands from
   CopterSim/Python/Simulink and can return collision, terrain, and visual data.
   This is the key reason to test RflySim as a native renderer/runtime before
   building more custom UE logic.

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
| `D:\PX4PSP\CopterSim\ModelData.db` | Vehicle/component parameter database: motor, propeller, ESC, battery, frame presets |
| `D:\PX4PSP\CopterSim\external\XML\F450.xml` | Example quadrotor physical parameters: mass, inertia, arm radius, thrust/moment coefficients, hover RPM |

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
| Object/camera query | `RflyReqObjData` can request camera, vehicle, and object pose plus bounding-box origin/extent for named objects |
| Terrain service | `RflyScanTerrainH x0 y0 x1 y1 h interval` exports terrain PNG/TXT data; examples convert it to height query and PLY point cloud |

Known parameter limits:

1. Vehicle physical parameters are available from CopterSim XML and
   `ModelData.db`. Example F450 data includes mass `1.4 kg`, inertia
   `Jxx=0.0211`, `Jyy=0.0219`, `Jzz=0.0366`, arm radius `0.225 m`,
   thrust coefficient `1.105e-05`, torque coefficient `1.779e-07`, motor
   response time `0.05 s`, and hover motor speed `5235.8 rpm`.
2. Terrain height can be sampled through RflySim3D terrain scan files. This is
   useful for visual alignment and local height maps, but it is not yet proof
   that every scene object/collision mesh can be exported as clean planning
   truth.
3. Scene object geometry may be available only for named/requested actors via
   `RflyReqObjData`, returning `PosUE`, `angEuler`, `boxOrigin`, and
   `BoxExtent`. Full static-scene collision truth is not guaranteed until the
   target scene is tested.
4. Cooked RflySim scenes and `.pak` files are not project-owned assets. If the
   installed tree does not expose editable `.uasset/.umap` source with usable
   license terms, treat it as a renderer/runtime reference rather than a source
   asset library.

RflySim native experience path:

```text
1. RflySim3D command and map test
   - Start RflySim3D.
   - Use RflyChangeMapbyName, r.setres, t.MaxFPS, camera commands.
   - If sending commands from WSL, do not assume 127.0.0.1 is the Windows
     RflySim3D host. Use the WSL default gateway IP or run the command script
     with Windows Python/PowerShell from the Windows side.

2. Terrain service test
   - Run 3.RflySim3DUE/1.BasicExps/e3_RflySim3DTerrainPcd.
   - Verify RflyScanTerrainH output and height-query consistency.

3. Vehicle visual/control test
   - Use UE4CtrlAPI.sendUE4PosFull or RflySim3D built-in SITL example.
   - Check pose, scale, propeller RPM display, and camera following.

4. Mid360/lidar test
   - Run 8.RflySimVision/0.ApiExps/10.Mid360Demo.
   - Verify TypeID=23 point cloud path and update frequency.

5. Path-planning reference test
   - Run 8.RflySimVision/2.AdvExps/e16_ESDFPathPlan.
   - Record whether its ESDF/Voronoi path planner is usable as an algorithm
     reference, not as final MWORKS evidence.
```

Only after these pass should the project connect MWORKS outputs to RflySim3D or
continue building a project-owned Unreal scene.

Manual review gates for the native RflySim experience:

| Gate | What to check | Pass condition |
| --- | --- | --- |
| `rflysim3d_map_view` | RflySim3D starts, changes map, camera/FPS commands work | User can see a stable scene and switch views without freezing |
| `rflysim_vehicle_visual` | Built-in or UDP-driven quadrotor model, propellers, scale, attitude | Vehicle model, propellers, and pose are visually credible |
| `rflysim_mid360` | Mid360/lidar example data path | Point cloud or ROS/RViz output appears at expected update rate |
| `rflysim_terrain_service` | Terrain scan and height lookup | Generated terrain files match selected scene region and can be queried |
| `rflysim_object_truth` | Object/camera query or scene metadata | Named object pose and bounding boxes can be obtained, or limitation is documented |
| `rflysim_esdf_path` | ESDF/Voronoi planning example | Path is not a hard-coded straight line and can be mapped to NED waypoints |

If `rflysim_object_truth` fails, RflySim can still be used for video rendering,
but not as the source of obstacle/planning truth. In that case MWORKS/scenario
files remain the truth source and RflySim is only the visual target.

### Verified RflySim Status

Current local verification status:

| Gate | Status | Evidence |
| --- | --- | --- |
| `rflysim3d_map_view` | Passed | RflySim3D launches from `D:\PX4PSP\RflySim3D\RflySim3D.exe`; map and UDP command tests are visible in the native window |
| `rflysim_vehicle_visual` | Passed | `tools/rflysim/rflysim_windows_smoke.py` creates and moves quadrotor actors through `UE4CtrlAPI` |
| `rflysim_lightweight_control` | Passed | Official `UAVCtrlNoPX4Demo.py` runs a point-mass control sequence without PX4/QGC |
| `rflysim_mid360` | Passed | `tools/rflysim/rflysim_mid360_smoke.py` receives direct UDP Mid360 point clouds: `80` frames, each `17408 x 4` |
| `rflysim_esdf_path` | Partly passed | `tools/rflysim/rflysim_esdf_path_smoke.py` validates official map-to-path logic: `15.86 m` path, `0.25 m` minimum clearance |
| `rflysim_esdf_playback` | Partly passed | `tools/rflysim/rflysim_esdf_path_playback.py` replays the generated `220`-point path into RflySim3D through `UE4CtrlAPI` |
| `rflysim_object_truth` | Not complete | Object/bounding-box truth still needs scene-specific verification before using RflySim as planning truth |

Use RflySim's bundled Python for local SDK smoke tests:

```text
D:\PX4PSP\Python38\python.exe
```

The project and Windows Anaconda environments may miss RflySim dependencies such
as `cv2`. Do not treat that as an RflySim API failure.

Radar and navigation scope:

```text
RflySim3D vehicle display
  -> Mid360 point cloud request/receive
  -> local point cloud / occupancy processing
  -> ESDF or Voronoi planner waypoint output
  -> controller / MWORKS trajectory replay
  -> RflySim3D video rendering
```

The display, sensor, and map-to-path layers are now verified separately.
Autonomous navigation is still not complete until the generated path is fed into
a flight/control loop and inspected in RflySim3D or MWORKS.

Validated local smoke commands:

```text
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_windows_smoke.py
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_mid360_smoke.py
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_esdf_path_smoke.py --json-output results\rflysim\esdf_path_smoke.json --path-output results\rflysim\esdf_path_smoke.npy
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_esdf_path_playback.py
```

WSL networking note:

RflySim3D runs on Windows and listens for UDP commands on `20010 + windowID`.
When Codex runs in WSL, `127.0.0.1` points to WSL itself, not necessarily the
Windows RflySim3D process. For WSL-driven smoke tests, resolve the Windows host
with:

```bash
ip route | awk '/default/ {print $3; exit}'
```

Prefer Windows-side Python/PowerShell for official RflySim examples when they
use RflySim's bundled Python environment or Windows-only dependencies. Use WSL
only for lightweight UDP packets, documentation extraction, and project file
updates.

Candidate integration path after RflySim native examples and MWORKS evidence are
stable:

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

Project-local prototype bridge:

```bash
python3 scripts/stream_rflysim3d.py \
  results/official/example3_figure8/official_example3_linear_mpc_sysblock/raw/official_example3_linear_mpc_sysblock.csv \
  --dry-run \
  --max-frames 2
```

Actual RflySim3D playback requires the installed RflySim3D window to be open:

```bash
python3 scripts/stream_rflysim3d.py \
  results/official/example3_figure8/official_example3_linear_mpc_sysblock/raw/official_example3_linear_mpc_sysblock.csv \
  --rflysim-root /mnt/d/PX4PSP \
  --transport direct \
  --host 127.0.0.1 \
  --window-id 0 \
  --vehicle-type 3 \
  --map-name MapData \
  --resolution 1280x720w \
  --max-fps 60 \
  --fps 30
```

Coordinate and rotor-display policy:

1. Project raw CSV uses `z` positive upward. RflySim3D examples use NED, so the
   bridge sends `PosE=[x, y, -z]`.
2. Project raw CSV `u1..u4` are controller/motor command channels, not verified
   physical RPM. The bridge defaults to a constant visual RPM. Use
   `--motor-mode command_magnitude` only for render-side rotor-speed variation,
   not for evidence claims.
3. If RflySim3D shows the vehicle underground, oversized, or mirrored, fix the
   bridge coordinate/scale arguments. Do not alter MWORKS raw evidence.
4. The bridge defaults to `--transport direct`, which sends the documented
   RflySim3D UDP structures without importing the RflySim Python SDK. Use
   `--transport sdk` only after the local Python environment has the SDK
   dependencies such as OpenCV available.

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
