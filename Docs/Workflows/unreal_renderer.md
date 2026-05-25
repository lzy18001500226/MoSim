# Unreal Renderer Workflow

Unreal is the high-quality visual layer of the MoSim simulator product.
MWORKS/Sysplorer/Syslab remain the truth source for dynamics, control,
planning, collision checks, event logs, and metrics.

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
mosim_epic_library MCP
  -> inspect Epic/Fab/Launcher inventory
  -> choose candidate scene asset
  -> verify local editable project/content
unreal_engine MCP
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

For the RflySim-like simulator goal, add two operational gates:

| Gate | Required Evidence |
|---|---|
| MCP automation | The selected route can be operated through `mosim_epic_library` and/or `unreal_engine` MCP, or the blocker is documented with an approved fallback |
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
| `DerelictCorridorMegascans` | `/Game/DerelictCorridor/Maps/DerelictCorridor` | Already has renderer load proof and first-pass AABB truth. |
| `DarkRuinsMegascansSample` | `/Game/Main` | Good cave/ruins candidate; still needs renderer reuse and truth export. |
| `ElectricDreamsEnv` | `/Game/Levels/PCG/ElectricDreams_PCGCloseRange` | Strong forest candidate; plugin/PCG risk is higher. |
| `FPS-Shooter-Unreal` | `/Game/FirstPerson/Maps/FirstPersonMap` | Lower priority; useful mostly as UE control/template smoke. |

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

Evidence from the latest run: UE 5.5 commandlet loaded
`/Game/DerelictCorridor/Maps/DerelictCorridor` and wrote
`derelictcorridormegascans_collision_truth.json` with 4753 assets and 4753
collision proxies. The scene-source audit then marked
`DerelictCorridorMegascans` as `ready_for_truth_backed_planning`. This proves
the local editable scene has an explicit first-pass planner-truth route; it
does not mean semantic labels or high-fidelity voxel occupancy are complete.

Current scene-source registry state:

```text
fab_route.status: inventory_visible_not_scene_accepted
local_editable_fallback.status: active
primary_scene_source_id: local_derelictcorridormegascans
```

Interpretation: Fab/Epic library entries are visible and useful for selecting
assets, but none is accepted yet as a MoSim scene source until it is imported or
reused in the MoSim UE sim project, editable through UE tooling, and paired with
planning truth. `DerelictCorridorMegascans` is the current validated fallback.

`AQuadrotorMworksMapActor` consumes this registry through:

```text
SceneSourceRegistryJson = MworksData/scene_source_registry.json
ResolveSceneSourceId(<scene_source_id>)
```

When the incoming frame `map_id` is `local_derelictcorridormegascans`, the map
actor now records the editable project path, `.uproject` path, truth artifact
list, acceptance gates, renderer-local content root, renderer map asset, and
renderer package name from the registry. For the current Derelict fallback it
sets `bCurrentSceneImportedIntoRenderer=true` because the scene is reused inside
the MoSim renderer through a local content junction rather than copied into Git.

Source-level gate:

```bash
uv run python Scripts/UE5/check_unreal_bridge.py
uv run python Scripts/UE5/check_scene_source_udp_contract.py
uv run python Scripts/UE5/check_ue_fab_goal_acceptance.py
```

This check verifies that the C++ bridge exposes the scene-source registry fields
and that the committed registry does not contain external Launcher/Fab absolute
paths. The scene-source UDP contract check generates one dry-run frame with
`map_id=local_derelictcorridormegascans` and verifies that this selected source
matches the registry primary scene id, carries truth artifacts, and keeps
`local_known_map` / preview `local_plan` marked as render-only. It is not visual
import evidence; it proves the packet path that triggers
`ResolveSceneSourceId`.

Use `check_ue_fab_goal_acceptance.py` as the current objective audit. It checks
the UE/Fab tool goal gate by gate: Epic/Fab inventory visibility, Fab-route
acceptance, local fallback readiness, truth-artifact validation, UDP
scene-source selection, live `unreal_engine` edit evidence, minimal Skills /
workflow presence, and visual import/reuse evidence. The default mode reports
partial progress without failing. Use `--require-complete` only when deciding
whether the full goal is ready to close.

Current expected status before visual import work:

```text
7/8 gates passed after local content-link reuse and renderer map-load proof
fab_route_acceptance: partial
scene_visual_import_or_reuse: passed
```

This means the local Derelict fallback has truth, packet-level selection, and a
renderer-local content link at `UE5/MoSimSceneLibrary/Content/DerelictCorridor`.
Fab remains unaccepted until one Fab asset is created/imported with edit access
and planning truth. The local fallback route still satisfies the current goal
branch because the goal explicitly allows switching to `References/UnrealScenes`
when Fab cannot prove import/edit/truth.

The local fallback content link is created or verified with:

```bash
uv run python Scripts/UE5/link_renderer_scene_source.py
uv run python Scripts/UE5/build_scene_source_registry.py --write
```

`References/UnrealScenes` stays ignored. The link is a local runtime/editor
bridge, not a committed copy of third-party assets. On WSL/Windows, this must
be a Windows directory junction, not a Linux symlink. A WSL symlink can pass
Python `exists()` checks while Unreal cannot load the `.umap`.

Verify that the renderer can actually load the linked package:

```bash
uv run python Scripts/UE5/probe_renderer_map_load.py
```

The probe must report `ok=true`, `loaded_expected_map=true`, and
`actor_count>0` for `/Game/DerelictCorridor/Maps/DerelictCorridor`. A zero exit
code from Unreal alone is not enough, because commandlets can return success
after falling back to an empty temporary map.

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
Docs/Skills/Unreal/mosim-epic-fab-library/SKILL.md
Docs/Skills/Unreal/mosim-unreal-editor-mcp/SKILL.md
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

Current policy: `unreal_engine` is MoSim's own UE automation MCP. It should not
be a generic world-building MCP and should not own Epic/Fab downloads.
`mosim_epic_library` remains the separate read-only inventory MCP.

First-stage `unreal_engine` tools:

```text
ue_health
project_context
scene_source_registry
ue_fab_goal_acceptance
scene_truth_export_plan
epic_scene_library_view
tool_boundary
```

Wrapper layout:

```text
Scripts/UE5/unreal_mcp_wsl_wrapper.sh
  -> Scripts/UE5/mosim_unreal_engine_mcp_wsl_wrapper.sh
  -> Scripts/UE5/mosim_unreal_engine_mcp.py
```

Legacy rollback wrapper:

```text
Scripts/UE5/unreal_mcp_legacy_flopperam_wsl_wrapper.sh
```

Do not remove the legacy wrapper until the MoSim-native route has equivalent
read-only scene query, controlled actor edit, viewport capture, and editor-log
coverage. The current native route intentionally starts with stable MoSim
workflow tools rather than Flopperam's broad `create_town/create_castle` style
tool surface.

Open-source MCP audit decision:

| Source | Adopt | Reject For Phase 1 |
|---|---|---|
| `Docs/Skills/Unreal/Unreal_mcp-dev` | tool registry, schema discipline, C++ bridge, transport and safety patterns | broad game/GAS/networking/inventory tools |
| `Docs/Skills/Unreal/UnrealClientProtocol` | reflection and future Blueprint/graph editing ideas | arbitrary reflection as the default public tool |
| `Docs/Skills/Unreal/UnrealClaude` | game-thread task queue, project context, log/viewport ideas | Claude-specific chat/product shell and default script execution |
| `Docs/Skills/Unreal/UnrealGenAISupport` | small actor/Blueprint utility examples | inactive/broad GenAI plugin assumptions |
| `Docs/Skills/Unreal/unreal-engine-mcp` | rollback bridge and existing live-editor smoke path | final MoSim interface shape |

Target architecture:

```text
Codex / MCP client
  -> MoSim stdio or HTTP MCP server
  -> TCP/WebSocket/HTTP bridge
  -> C++ UE Editor plugin
  -> UE AssetRegistry / GEditor / PIE / package APIs on the editor thread
```

Phase order:

1. Read-only: `ue_health`, `project_context`, `asset_search`,
   `scene_source_registry`, `scene_truth_export_plan`, `editor_log`.
2. Controlled writes: reversible actor edit/delete, map open/save, material
   instance parameter edits, and viewport capture.
3. Simulator truth: collision/semantic/occupancy export and validation.
4. Advanced authoring: minimal Blueprint/material graph edits.

Do not implement arbitrary `python_execution`, Launcher button-clicking, raw
webcache parsing, OAuth/token reuse, or automatic Fab downloads in
`unreal_engine`.

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

When a linked scene source is active, prefer the scene-source scoped probe:

```bash
uv run python Scripts/UE5/probe_linked_scene_source_mcp.py \
  --json-output Results/tmp/linked_scene_source_mcp_probe_latest.json
```

This script uses the same UnrealMCP editor socket as the `unreal_engine` MCP
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
