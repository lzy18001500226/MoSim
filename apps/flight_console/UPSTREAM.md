# MoSim Ground Control Upstream Baseline

MoSim Ground Control uses the official QGroundControl custom-build extension
points. Upstream source is vendored so MoSim never modifies the read-only
reference snapshot.

## Frozen upstream

- Repository: `https://github.com/mavlink/QGroundControl`
- Release: `v5.0.8`
- Release commit: `e0816c957602789200ae5ba0af45217f0f2f1db4`
- Source archive SHA256:
  `74C7B9A183BBCBB0AB3DC97E4F88B80A10B0AB1B41847CDBF61B54F02FC5A5AC`
- License files: `LICENSE-APACHE`, `LICENSE-GPL`

The release contains one Git submodule:

- Repository: `https://github.com/ArduPilot/ArduPilot-Parameter-Repository`
- Path: `src/FirmwarePlugin/APM/ArduPilot-Parameter-Repository`
- Commit: `a458e8e86a8ffa3b7f52f4601adcdaaff0db5f42`
- Source archive SHA256:
  `041D6B0C16750C91CFDBFB65FD29AF29BF98ABECBC7BE0397B77BA5E0F0AF468`

## Product boundary

`vendor/qgroundcontrol/` is the immutable upstream baseline. MoSim-owned code
belongs in `mosim/` and in a generated `vendor/qgroundcontrol/custom/` overlay
that follows QGroundControl's supported custom-build contract. Do not make
ad-hoc edits in upstream source files.

The full file digest is stored in `vendor/qgroundcontrol.SHA256SUMS`. Run
`Scripts/ui/generate_qgc_vendor_manifest.py` to verify or regenerate it.

## Update procedure

1. Select an official stable release and resolve its immutable commit.
2. Download the official source archive and every declared submodule archive.
3. Verify archive SHA256 values and update this file.
4. Materialize the source without nested `.git` metadata.
5. Generate the vendor digest and run the unmodified Windows baseline gate.
6. Reapply the MoSim custom overlay and run the custom-build gate.

An upstream update is not accepted until both baseline and custom gates pass.
