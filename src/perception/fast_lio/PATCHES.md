# MoSim Patch Record

No FAST-LIO source, CMake, package metadata, launch, configuration, or sensor
file was changed while copying this component into `src/perception/fast_lio`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, this file,
and `Log/.gitkeep` plus `PCD/.gitkeep`. These files are outside the 49-file
payload represented by the SHA-256 in `UPSTREAM.md`.

The copy intentionally excludes upstream demonstration media under `doc/`,
historical runtime files under `Log/`, and the `PCD/` runtime output. The two
empty placeholders preserve the paths used by the existing source when logging
or PCD saving is enabled, without delivering old logs or point clouds.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact FAST-LIO and ikd-Tree revisions and license
   evidence;
2. update only audited FAST-LIO, Livox compatibility, and runtime entrypoints
   to the canonical path;
3. build the declared ROS1 package and validate the MID360/Sunray preflight;
   and
4. keep `References/Lab/localization_slam/FAST_LIO` intact as the retained
   legacy source unless a later user-approved archival task says otherwise.
