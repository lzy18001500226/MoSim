# Gate Ring Indoor Staging Package

Project-owned metadata for the indoor gate/ring scene. This package does not
depend on RflySim assets. It starts from `map_corridor_gate` geometry and is the
first target for attitude-control video review.

Validation:

```bash
python3 scripts/check_unreal_migration_package.py --package-dir unreal/migration_staging/gate_ring_indoor
python3 scripts/export_unreal_scene_map.py --config planners/astar_min_snap/map_corridor_gate.yaml --output unreal/MworksUnrealRenderer/Content/MworksData/map_corridor_gate_render_map.json --terrain-cell-m 0.2
```

Manual review points:

- gate obstacles are visible in UE render map;
- UAV passes the gate opening without clipping collision proxies;
- local/reference path starts at the UAV body center;
- attitude visibly changes when later tilted-gate geometry is added.
