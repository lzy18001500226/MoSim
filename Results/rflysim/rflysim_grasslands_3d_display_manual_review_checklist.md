# Manual UE Migration Review: rflysim_grasslands_3d_display

Fill this checklist while inspecting the temporary Unreal conversion project.
Do not copy assets into the competition repo until every blocking item is resolved.

## Scene Open Result

| Item | Result | Notes |
| --- | --- | --- |
| Temporary project path | TODO | `D:/UE_MigrationScratch/QuadrotorRflySimSceneProbe` or equivalent |
| Source map opens | TODO | `Grasslands/Maps/Grasslands/3DDisplay.umap` |
| Missing plugin warning | TODO | list exact plugin names or `none` |
| Missing asset warning | TODO | list exact assets or `none` |
| Core geometry visible | TODO | floor/walls/ring/terrain as applicable |
| Materials acceptable | TODO | transparent/black/missing material issues |
| Scale checked | TODO | compare one known dimension to MWORKS meters |
| Coordinate direction checked | TODO | X/Y/Z and handedness notes |

## Migration Package Readiness

| Item | Result | Notes |
| --- | --- | --- |
| Candidate content roots copied to staging only | TODO | not directly into `Content/` |
| `scene_asset_registry.json` created | TODO | must follow project schema |
| Collision proxies authored | TODO | every obstacle-like visible asset has proxy |
| Package checker passed | TODO | run `check_unreal_migration_package.py` |
| No `.pak`/installer/engine binary | TODO | required |
| No single file >100 MB | TODO | required before Git |
| License status recorded | TODO | `permitted` or `pending_review`, never blank |

## Playback Readiness

| Item | Result | Notes |
| --- | --- | --- |
| `map_id` selected | TODO | must match registry scene/map id |
| UAV scale and color acceptable | TODO | body, arms, propellers visible |
| Propeller RPM visual works | TODO | no static propellers unless source has no RPM |
| Local plan and trail visible | TODO | starts at UAV center |
| Radar sector visible | TODO | FOV/radius/yaw follows packet |
| Follow camera usable | TODO | no constant manual drag required |

## Decision

| Decision | Value |
| --- | --- |
| Import into project-owned UE5 renderer? | TODO yes/no |
| Reason | TODO |
| Next action | TODO |
