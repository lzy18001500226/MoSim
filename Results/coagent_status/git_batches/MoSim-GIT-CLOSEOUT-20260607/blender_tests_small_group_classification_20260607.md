# Blender Tests Small Group Classification - 2026-06-07

Scope: small ignored groups under `References/Blender/blender/tests`.

Committed in this slice:

- `tests/files/invalid_blendfiles/README.md`
- `tests/files/sound/README`
- `tests/files/paint/lockingTestResults.txt`

Precheck for committed files:

- file count: 3
- total bytes: 2370
- files at or above 100 MiB: 0
- Git LFS pointer placeholders: 0
- generated/dependency/archive/binary risk class: 0

Classified as all Git LFS pointer placeholders:

- `tests/files/animation`: 21/21 pointers
- `tests/files/alembic`: 36/36 pointers
- `tests/files/constraints`: 1/1 pointer
- `tests/files/gameengine`: 1/1 pointer
- `tests/files/layers`: 1/1 pointer
- `tests/files/mesh_paint`: 1/1 pointer
- `tests/files/grease_pencil`: 2/2 pointers
- `tests/files/materials`: 3/3 pointers
- `tests/files/dupli`: 4/4 pointers
- `tests/files/ui_tests`: 5/5 pointers
- `tests/files/screenshot`: 6/6 pointers
- `tests/files/ffmpeg`: 6/6 pointers

Deferred:

- `tests/utils/bl_run_operators_event_simulate.py` is a real 19 KiB Python
  file, but line 27 contains an upstream docstring heading that trips Git's
  conflict-marker check. Import it only with an explicit third-party exception
  record or a reviewed normalization policy.
