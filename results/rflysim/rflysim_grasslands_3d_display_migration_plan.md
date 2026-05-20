# RflySim Scene Migration Plan: rflysim_grasslands_3d_display

- Priority: `P0`
- Purpose: open wind, motor-efficiency, and long-range trajectory scene
- Source map: `Grasslands/Maps/Grasslands/3DDisplay.umap`
- Source engine: `4.27`
- Target engine: `5.7`
- Direct use supported: `false`

## Source Content Roots

- `/Game/Grasslands` -> `/mnt/d/PX4PSP/RflySim3D/RflySim3D/Content/Grasslands`

## Acceptance

- scene opens in a temporary Unreal conversion project with no missing core geometry
- selected assets can be migrated into a project-owned UE5 test project without proprietary runtime dependency
- visual scale is measured against MWORKS meters and stored as a scene profile transform
- collision proxies are derived as simple boxes/convex hulls and linked to world_geometry ids
- MWORKS UDP playback drives UAV pose, motor visuals, radar sector, local plan, and trail without feeding data back
- no .pak, installer, engine binary, or unclear-license asset is committed

## Manual Steps

1. copy the RflySim UE project to the suggested temporary project path outside this repo
2. open the temporary copy in Unreal and let only the copy upgrade if needed
3. open the source map and record missing asset/plugin warnings
4. migrate only the required source content roots into a disposable UE5 test project
5. extract or author simplified collision proxies for visible obstacles, walls, gates, and terrain
6. update the project-owned scene registry entry from audit_only to migrated_tested only after visual and collision checks pass

## Stop Conditions

- required proprietary plugin is unavailable
- the map opens only in the packaged RflySim runtime
- core scene geometry is missing after migration
- asset size or license makes repository tracking impossible
- collision truth cannot be approximated without changing planner assumptions
