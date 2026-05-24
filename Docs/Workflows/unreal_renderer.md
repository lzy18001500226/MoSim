# Unreal Renderer Workflow

Unreal is a render-only layer. MWORKS/Sysplorer/Syslab remain the truth source
for dynamics, control, planning, collision checks, and metrics.

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
The map must first pass manual visual review as a believable physical-world
scene. Only after that should we reconnect quadrotor playback, radar overlays,
trajectory trails, or MWORKS UDP streaming.

## Kept Project Components

```text
UE5/MworksUnrealRenderer/
UE5/QuadrotorMworksBridge/
```

`MworksUnrealRenderer` is the project-owned UE shell. `QuadrotorMworksBridge`
provides UDP reception and playback state for MWORKS simulation output.

Generated folders are disposable and must not be committed:

```text
UE5/**/Binaries/
UE5/**/Intermediate/
UE5/**/Saved/
UE5/**/DerivedDataCache/
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
```

The inventory separates:

| Field | Meaning |
|---|---|
| `launcher_items` / `launcher_installs` | Installed engines and plugins from Epic manifests |
| `account_library_items` | Owned library entries inferred from the local Launcher account cache; may not be installed |
| `fab_assets` | Local FabLibrary cached downloads |
| `vault_cache_projects` | Old-style VaultCache projects and any discovered `.uproject` |
| `epic_library_view.py` | Merged human-readable view across account/Fab/Vault sources |

Current verified local-library behavior on 2026-05-24:

```text
launcher_item_count: 11
launcher_install_count: 11
fab_asset_count: 5
vault_cache_project_count: 3
account_library_item_count: 17
```

This inventory is a selection and planning tool, not a downloader. If an asset
exists only in `account_library_items`, use Epic Launcher/Fab to create or add
it to a UE project before treating it as editable local content. Do not parse or
publish raw Launcher logs or webcache entries; only the allowlisted index output
is safe to record.

When Codex needs this inventory through MCP, register
`Scripts/UE5/mosim_epic_library_mcp_wsl_wrapper.sh` as `mosim_epic_library`.
Keep it separate from `unreal_engine`: library inventory selects candidate
assets, while `unreal_engine` edits a running UE project.

## Scene Acceptance Gates

A scene is not accepted just because it renders well. It must pass three gates:

| Gate | Required Evidence |
|---|---|
| Import/edit | Editable `.uproject`, `.umap`, `.uasset`, required plugin source or compatible installed plugins |
| Render | Opens in the target UE version and can be reviewed without missing modules/assets |
| Planning truth | Has or can generate explicit collision/semantic/occupancy truth for mapping, local planning, and path validation |

If a Fab entry only exposes a binary `manifest` and no editable project/content
files, it is only an account/cache listing. It is not yet a MoSim scene source.
Use Epic/Fab to create the local project, or switch to already available local
projects under `References/UnrealScenes`.

Current fallback source:

```text
References/UnrealScenes
```

Run:

```bash
python3 Scripts/UE5/audit_scene_source.py
```

Any scene with `needs_truth_extraction_or_proxy` may be visually useful, but it
still needs a truth-extraction or proxy-generation pipeline before it can prove
mapping/path-planning behavior.

Current audit result: the editable local projects under `References/UnrealScenes`
are usable visual candidates. `DerelictCorridorMegascans` now has an explicit
collision-truth export and audits as `ready_for_truth_backed_planning`; the
other local candidates still need truth extraction before planner validation.
UE assets with collision/navigation names are treated only as proxy candidates;
they are not accepted as planner truth until exported to an explicit
occupancy/collision/semantic artifact.

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
  --output UE5/MworksUnrealRenderer/Content/MworksData/scene_truth/<map_id>_collision_truth.json
```

Then validate from the normal project shell:

```bash
uv run python Scripts/UE5/export_unreal_scene_truth.py validate \
  UE5/MworksUnrealRenderer/Content/MworksData/scene_truth/<map_id>_collision_truth.json
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
  UE5/MworksUnrealRenderer/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json
uv run python Scripts/UE5/audit_scene_source.py
```

Evidence from the latest run: UE 5.5 commandlet loaded
`/Game/DerelictCorridor/Maps/DerelictCorridor` and wrote
`derelictcorridormegascans_collision_truth.json` with 4753 assets and 4753
collision proxies. The scene-source audit then marked
`DerelictCorridorMegascans` as `ready_for_truth_backed_planning`. This proves
the local editable scene has an explicit first-pass planner-truth route; it
does not mean semantic labels or high-fidelity voxel occupancy are complete.

Relevant current-phase skills:

```text
Docs/Skills/unreal/mosim-epic-fab-library/SKILL.md
Docs/Skills/unreal/mosim-unreal-editor-mcp/SKILL.md
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
unreal_engine
```

Before interactive editor work, run the smallest useful probe. Inventory alone
is not enough; the editor-side listener must be reachable:

```bash
python3 Scripts/UE5/probe_unreal_mcp_listener.py --timeout 1
```

If the probe fails, do not keep calling actor/Blueprint tools. Fix the editor
listener or continue with file-level work only.

After the listener is reachable, verify actual edit authority with the
reversible editor round-trip probe:

```bash
uv run python Scripts/UE5/probe_unreal_editor_mcp_tools.py \
  --json-output Results/tmp/unreal_mcp_editor_probe_<date>.json
```

This script uses the same UnrealMCP editor socket as the `unreal_engine` MCP
server. It reads level actors, spawns a temporary uniquely named
`MoSimMcpProbe_DoNotSave_*` static mesh actor, changes its transform, deletes
it, and checks cleanup. A passing listener probe alone is not enough to claim
map-edit capability; this round trip is the minimum evidence for live UE scene
modification. Do not reuse a fixed probe actor name in the same editor session:
UE can retain deleted actor names internally and may crash while generating a
unique name.

Current known project-owned renderer requirement:

```text
UE5/MworksUnrealRenderer/MworksUnrealRenderer.uproject
AdditionalPluginDirectories must include:
../../Docs/Skills/Unreal/unreal-engine-mcp/FlopperamUnrealMCP/Plugins
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
