# Scene Profile Staging Package: renderer_framework

This package is metadata-only. It is the review contract before UE scene
blockout work starts. It must not contain large meshes, textures, paks,
engine binaries, or imported third-party assets.

## Review Focus

- Stage: `S0`
- Purpose: foundation for all later scenes: project-owned UE5 scene profile, object registry, collision proxy registry, MWORKS playback, UAV visual, camera, trail, radar sector and local plan overlays
- Planner visibility: `framework_only_no_planner_truth_leakage`
- Global map available to planner: `False`

## Validation

```bash
python3 scripts/check_unreal_migration_package.py --package-dir unreal/migration_staging/renderer_framework
```

Replace placeholder bounds and asset paths only after the blockout is
measured in Unreal and reviewed.
