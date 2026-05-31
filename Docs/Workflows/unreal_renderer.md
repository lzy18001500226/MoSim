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
| `DerelictCorridorMegascans` | `/Game/DerelictCorridor/Maps/DerelictCorridor` | Already has renderer load proof and first-pass AABB truth. |
| `FactoryEnvironmentCollect` | `/Game/Maps/Demonstration` | Best first factory/industrial candidate; still needs renderer reuse and truth export. |
| `CityParkEnvironmentCollec` | `/Game/CityPark/Maps/Showcase` | Park/open outdoor candidate; still needs renderer reuse and truth export. |
| `CitySample` | `/Game/Map/Big_City_LVL` | Large city candidate; high load/performance risk, use after smaller scenes. |
| `DarkRuinsMegascansSample` | `/Game/Main` | Good cave/ruins candidate; still needs renderer reuse and truth export. |
| `ElectricDreamsEnv` | `/Game/Levels/PCG/ElectricDreams_PCGCloseRange` | Strong forest candidate; plugin/PCG risk is higher. |
| `MedievalVillageMegascansS` | `/Game/Maps/MedievalVillage_P` | Village/building candidate; still needs renderer reuse and truth export. |
| `ABoyandHisKite` | `/Game/Maps/GoldenPath/GDC_Landscape_01` | Large outdoor reference; UE 4.x origin may need conversion review. |
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
are usable visual candidates. `FactoryEnvironmentCollect`,
`DerelictCorridorMegascans`, and `ElectricDreamsEnv` now have explicit
collision-truth exports and audit as `ready_for_truth_backed_planning`.
`FactoryEnvironmentCollect` passed manual visual review on 2026-05-31. The
active renderer content links can then be switched to the next candidate, such
as `DerelictCorridorMegascans`, for one-map-at-a-time review. UE assets with
collision/navigation names are treated only as proxy candidates; they are not
accepted as planner truth until exported to an explicit
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
same map as `/Game/Maps/Demonstration` with 11872 actors. Factory is the active
primary scene for the current integration round.

Validated ElectricDreams example: UE 5.5 commandlet wrote
`electricdreamsenv_collision_truth.json` with 247 assets and 247 collision
proxies. Full renderer load can exceed the default 60 second gate because UE is
building Nanite/static-mesh data on first use. Treat this as a slow path, not a
failed scene, until a longer approved load window or manual editor review says
otherwise.

Current scene-source registry state:

```text
fab_route.status: inventory_visible_not_scene_accepted
local_editable_fallback.status: active
primary_scene_source_id: local_factoryenvironmentcollect
```

Interpretation: Fab/Epic library entries are visible and useful for selecting
assets, but none is accepted yet as a MoSim scene source until it is imported or
reused in the MoSim UE sim project, editable through UE tooling, and paired with
planning truth. `FactoryEnvironmentCollect` is the current validated local
fallback and active renderer scene.

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

Current verified local renderer reuse on 2026-05-31:

| Scene source | Renderer package | Truth artifact | Load proof |
|---|---|---|---|
| `local_derelictcorridormegascans` | `/Game/DerelictCorridor/Maps/DerelictCorridor` | `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json` | `Results/tmp/renderer_map_load_probe_latest.json` |
| `local_factoryenvironmentcollect` | `/Game/Maps/Demonstration` | `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json` | `Results/tmp/renderer_map_load_probe_factory_active_20260531.json` |
| `local_electricdreamsenv` | `/Game/Levels/PCG/ElectricDreams_PCGCloseRange` | `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/electricdreamsenv_collision_truth.json` | truth OK; full renderer load is a slow first-time Nanite/static-mesh build path |

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
camera collision.

For scenes whose default camera position is wrong or whose interior is too dark
for review, first use balanced camera and fill-light overrides. Do not enable
forced exposure as the default review path because it can overexpose the whole
viewport to pure white.

```bash
RESTART_UNREAL_GAME=1 \
UNREAL_EXTRA_ARGS="/Game/Maps/Demonstration \
  -MoSimReviewCameraX=-4750 -MoSimReviewCameraY=3850 -MoSimReviewCameraZ=180 \
  -MoSimReviewCameraPitch=-8 -MoSimReviewCameraYaw=-34 -MoSimReviewCameraRoll=0 \
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

Current blocked or lower-priority candidates:

| Scene source | Status | Next action |
|---|---|---|
| `CityParkEnvironmentCollec` | 60 second truth export timed out while UE was still building static meshes | retry only with a longer approved build/export window or after manual editor warm-up |
| `DarkRuinsMegascansSample` | `/Game/Main` loads but commandlet only exposes global/camera/postprocess actors; World Partition editor subsystem is unavailable in the tested UE Python route | implement a proper World Partition cell/data-layer truth route or use manual editor-assisted review |
| `MedievalVillageMegascansS` | UE 4.27 origin; after exporter API compatibility fixes it can be retried, but it is lower priority than Factory/Derelict/Electric | retry only if a village map is needed |
| `FPS-Shooter-Unreal` | previous partial truth was misleading because required `/Game/AbandonedFactory/...` assets were missing | do not treat as formal scene source without asset repair |

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
