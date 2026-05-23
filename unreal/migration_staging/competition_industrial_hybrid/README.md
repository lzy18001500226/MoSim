# Scene Profile Staging Package: competition_industrial_hybrid

This package is metadata-only. It is the review contract before UE scene
blockout work starts. It must not contain large meshes, textures, paks,
engine binaries, or imported third-party assets.

## Review Focus

- Stage: `S1`
- Purpose: first complete single-UAV navigation scene combining challenge objects, industrial inspection context, local perception, realtime replanning and trajectory tracking
- Planner visibility: `raycast_occluded_local_sensor_with_map_memory`
- Global map available to planner: `False`

## Validation

```bash
python3 scripts/check_unreal_migration_package.py --package-dir unreal/migration_staging/competition_industrial_hybrid
```

Replace placeholder bounds and asset paths only after the blockout is
measured in Unreal and reviewed.
