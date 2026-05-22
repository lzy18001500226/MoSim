# AirSim Reference Migration Notes

> Source exception: copied from `C:\Users\HP\Desktop\AirSim` into
> `references/AirSim/` for research and architecture reference. Generated
> build outputs and files above GitHub hard limits are excluded.

## Migrated Project Families

```text
AirSim
AirSim360
Cosys-AirSim
IsaacSim
PEDRA
PegasusSimulator
ProjectAirSim
UESVONavigation-develop
carla-ue5-dev
spear
unrealcv-5.2
```

## Exclusion Policy

The migration keeps source, docs, configs, examples, and editable Unreal-style
project content where practical. It excludes generated/runtime artifacts such
as:

```text
.git/
Binaries/
Intermediate/
Saved/
DerivedDataCache/
build/
BUILD/
CMakeFiles/
node_modules/
venv/
*.pdb, *.pch, *.obj, *.lib, *.dll, *.exe, *.pak
```

## Recorded Risks

`references/AirSim/IsaacSim/` contains many Git LFS pointer files, mostly for
image, USD, STL, and other asset paths. These are useful as source/reference
metadata, but they are not the actual large assets. If IsaacSim assets become
execution-critical, fetch them through the upstream LFS workflow or exclude
them from Git and document the external source.

The following retained files are below GitHub's hard 100 MB limit but above
50 MB, so they are intentionally recorded:

| File | Approx Size | Reason Kept |
|---|---:|---|
| `Cosys-AirSim/Unreal/Plugins/AirSim/Content/VehicleAdv/SUV/SUV.uasset` | 94 MB | Editable UE asset reference |
| `Cosys-AirSim/docs/annsim23_tutorial/annsim23_windows_setup_tutorial.mp4` | 83 MB | Upstream tutorial evidence |
| `Cosys-AirSim/docs/annsim23_tutorial/annsim23_general_usage_demo.mp4` | 83 MB | Upstream tutorial evidence |
| `AirSim360/media/videos/airsim360_air_demo_0410_v2.mp4` | 83 MB | Upstream demo reference |
| `Cosys-AirSim/docs/annsim23_tutorial/annsim23_tutorial.pdf` | 67 MB | Upstream tutorial document |
| `carla-ue5-dev/Docs/img/tuto_content_authoring_vehicles/manual_control.gif` | 52 MB | Upstream documentation asset |

Small upstream `.exe` tools may exist in already-imported AirSim reference
folders. They are kept only as upstream reference files and should not become
project runtime dependencies without explicit review.

## Verification Gates

Before committing a new AirSim reference batch:

```bash
find references/AirSim -type f -size +100M -printf '%s\t%p\n'
find references/AirSim -type d -name .git -print
git ls-files -o --exclude-standard references/AirSim \
  | tr '\n' '\0' \
  | xargs -0 -r du -b \
  | awk '$1 > 100000000 {print}'
```

Expected result: no `>100MB` Git candidates and no nested `.git` directories.
