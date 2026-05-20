# Migration Staging Package: rflysim_vision_ring

This directory is a metadata-only staging package. It intentionally does
not contain migrated RflySim assets yet.

## Use

1. Complete the temporary UE migration/manual review checklist.
2. Replace placeholder `asset_path`, `source_path`, materials, scale, and
   collision proxy bounds with measured values.
3. Run:

```bash
python3 scripts/check_unreal_migration_package.py --package-dir unreal/migration_staging/rflysim_vision_ring
```

Do not copy `.pak`, engine binaries, installers, or files over 100 MB into
this package.
