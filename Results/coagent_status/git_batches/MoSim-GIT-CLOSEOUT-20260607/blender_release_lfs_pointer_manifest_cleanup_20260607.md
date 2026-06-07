# Blender Release LFS Pointer Manifest Cleanup - 2026-06-07

Scope:

- `References/Blender/blender/release/datafiles/`
- `References/Blender/blender/release/darwin/`
- `References/Blender/blender/release/windows/`

Decision: keep these release asset directories manifest-only for now. The
reviewed local files are Git LFS pointer placeholders, not restored release
payloads.

Evidence:

- `release/datafiles`: 197 ignored files, 197 Git LFS pointers, 0 files at or above 100 MiB.
- `release/darwin`: 5 ignored files, 5 Git LFS pointers, 0 files at or above 100 MiB.
- `release/windows`: 137 ignored files, 137 Git LFS pointers, 0 files at or above 100 MiB.

Action:

- replaced older narrower release/windows rules with concise release-directory
  manifest-only rules.
- did not force-add 130-byte pointer placeholders as real binary assets.
