# Blender LFS Pointer Manifest Cleanup - 2026-06-07

Scope: `References/Blender/blender/assets`, `References/Blender/blender/doc/python_api/static/favicon.png`, and `References/Blender/blender/scripts/startup/bl_app_templates_system`.

Decision: do not force-add these files now. The 21 reviewed ignored files are local Git LFS pointer placeholders, not restored Blender asset payloads.

Evidence:

- reviewed ignored target count: 21
- files whose first line is `version https://git-lfs.github.com/spec/v1`: 21
- non-pointer files in this reviewed target set: 0
- over-100MiB restored payloads present in this reviewed target set: 0

Action:

- collapsed the 21 per-file ignore entries into concise manifest-only rules for the affected Blender asset/template groups.
- left actual source/docs/config files outside this pointer set for later project-by-project drain batches.
