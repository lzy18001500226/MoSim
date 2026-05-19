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

Repository crawl priority:

| Priority | Repository / source | Decision |
| --- | --- | --- |
| P0 | User-installed RflySim3D/RflySimUE/RflySimUE5 folder | Highest value if it contains editable scenes or protocol docs |
| P0 | Local `references/Sunray/simulation/sunray_simulator/models` and `worlds` | Already available; convert SDF/DAE/PNG assets into UE scene registry |
| P1 | `RflySim/CopterSim` | Clone only if we need model/HIL/fault-injection reference; not for scene visuals |
| P1 | `RflySim/RflyExpCode` | Clone only if we need RflySim workflow examples or course docs |
| P2 | AirSim / Flightmare / RotorS / XTDrone / Pegasus | Use for architecture comparison only unless a specific reusable UE/Unity asset is identified |

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
