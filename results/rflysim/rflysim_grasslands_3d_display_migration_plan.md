# RflySim Scene Migration Plan: rflysim_grasslands_3d_display

- Priority: `P0`
- Purpose: open wind, motor-efficiency, and long-range trajectory scene
- Source map: `Grasslands/Maps/Grasslands/3DDisplay.umap`
- Source engine: `4.27`
- Target engine: `5.7`
- Direct use supported: `false`
- Direct editor open supported: `false`

## Source Content Roots

- `/Game/Grasslands` -> `/mnt/d/PX4PSP/RflySim3D/RflySim3D/Content/Grasslands`

## Acceptance

- scene opens in a temporary Unreal conversion project with no missing core geometry
- selected assets can be migrated into a project-owned UE5 test project without proprietary runtime dependency
- visual scale is measured against MWORKS meters and stored as a scene profile transform
- collision proxies are derived as simple boxes/convex hulls and linked to world_geometry ids
- MWORKS UDP playback drives UAV pose, motor visuals, radar sector, local plan, and trail without feeding data back
- no .pak, installer, engine binary, or unclear-license asset is committed

## Direct Editor Open Blockers

- project module RflySim3D has no Source Build.cs and no Win64 editor DLL
- plugin Cesium for Unreal missing source/DLL for modules: CesiumRuntime, CesiumEditor
- plugin Color Wheel missing source/DLL for modules: ColorWheelPlugin
- plugin HZFRedis missing source/DLL for modules: DTRedisLib, DTRedis, DTRedisEditor
- plugin Rfly3DSimPlugin missing source/DLL for modules: Rfly3DSimPlugin
- plugin RuntimeTransformer missing source/DLL for modules: RuntimeTransformer
- plugin Datasmith Twinmotion Importer missing source/DLL for modules: TwinmotionBase, TwinmotionStorageLite, TwinmotionToUnreal

## Manual Steps

1. do not open the original RflySim UE project as the main route while direct_editor_open_supported is false
2. if a diagnostic editor test is still needed, copy the RflySim UE project to the suggested temporary path outside this repo
3. record every missing project module, plugin module, asset, and incompatible-engine warning from the temporary copy
4. migrate only the required source content roots into a disposable UE5 test project, never into the final renderer first
5. extract or author simplified collision proxies for visible obstacles, walls, gates, and terrain
6. update the project-owned scene registry entry from audit_only to migrated_tested only after visual and collision checks pass

## Stop Conditions

- project module or plugin module source/DLL remains missing and the scene requires that module
- required proprietary plugin is unavailable
- the map opens only in the packaged RflySim runtime
- core scene geometry is missing after migration
- asset size or license makes repository tracking impossible
- collision truth cannot be approximated without changing planner assumptions
