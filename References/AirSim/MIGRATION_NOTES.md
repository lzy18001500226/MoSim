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

## Git Migration State

As of 2026-05-22, the Git-safe migration is complete under the project rule:
commit everything that is useful and safe for Git, exclude files above GitHub
limits, generated artifacts, dependency caches, and high-volume asset packs
that should be handled as external simulator assets.

Tracked content includes:

| Family | Tracked Scope |
|---|---|
| `AirSim` | Source/docs/config subset, with copied credential-like fields sanitized before commit. |
| `AirSim360` | Dataset/reference docs and media under the 100 MB hard limit. |
| `Cosys-AirSim` | Source/docs/config, tutorial media under 100 MB, and Unreal plugin content under 100 MB per file. |
| `PEDRA` | Source/reference content. |
| `PegasusSimulator` | Source/reference content. |
| `ProjectAirSim` | Source/reference content. |
| `UESVONavigation-develop` | Source/reference content. |
| `unrealcv-5.2` | Source/reference subset. |
| `carla-ue5-dev` | Root metadata, text docs, CMake/source/Python/Ros2Native/Util, and Unreal Source/Config only. |
| `spear` | Root metadata, docs, examples, Python/source, and Unreal Source/Config only. |
| `IsaacSim` | Root metadata, docs, tools/source text, manifests, and config only. |

Local ignored content remains available in the working tree where present, but
is intentionally not part of Git:

| Family | Ignored Scope | Reason |
|---|---|---|
| `carla-ue5-dev` | `Docs/img/`, `.github/`, Unreal `Content/`, generated/runtime assets | High-volume media/assets and project CI metadata; not needed for source study. |
| `IsaacSim` | LFS-managed image/USD/STL/DAE/PDF/ICO assets, golden data, cache/download/build products | Upstream LFS asset pointers and generated data should be fetched from upstream when execution-critical. |
| `spear` | `third_party/`, downloaded dependencies, Unreal Content assets, generated build/runtime artifacts | Large external dependencies and editable binary assets should be handled as external scene/runtime assets, not normal Git source. |

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

`carla-ue5-dev/Docs/img/tuto_content_authoring_vehicles/manual_control.gif`
is also below 100 MB, but it remains excluded with the rest of `Docs/img/`
because that directory is a high-volume image pack rather than a source or
execution-critical scene input.

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
