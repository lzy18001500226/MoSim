# Unreal Renderer Workflow

Unreal is a render-only layer. MWORKS/Sysplorer remains the simulation source
of truth for dynamics, control, planning, collision checks, and metrics.

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
