# Changelog
## [1.0.9] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [1.0.8] - 2025-05-16
### Changed
- Make extension target a specific kit version

## [1.0.7] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [1.0.6] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [1.0.5] - 2025-03-25
### Changed
- Add import tests for deprecated extensions

## [1.0.4] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [1.0.3] - 2025-01-21
### Fixed
- Fix import issue after deprecation

## [1.0.2] - 2024-11-07
### Changed
- Fix minor typo

## [1.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [1.0.0] - 2024-09-23
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.asset.exporter.urdf.

## [0.3.2] - 2024-08-28
### Fixed

- Added missing dependency

## [0.3.1] - 2024-07-23
### Fixed

- removed unnecessary dependencies

## [0.3.0] - 2024-04-26
### Fixed

- Fix cylinder radii check
- Fix checking for duplicate prim names
- Fix issue with joint limits set to inf for revolute joints, set to continuous joint instead
- Fix cylinder scaling issue

### Added

- Replace absolute path and uri path options with mesh path prefix option
- Parse velocity and effort limits from USD and include in URDF
- Add UsdGeom.Cylinder to error message as one of the valid geom prim types
- Add hack to not include camera mesh files when exporting from isaac sim extension
- Add mesh file path char length check
- Add NodeType.SENSOR and functionality to include sensor frames in the URDF

## [0.2.0] - 2023-12-01
### Fixed

- Scaling bug when geometry prim is a child of Xform prim with scaling
- Cylinder scaling issue
- Joint frame alignment when child link transform is not identity
- Exporting revolute joints with inf limits, export as continuous joints now
- Too many root links
- Velocity and effort limits always being set to zero
- Large camera meshes added erroneously to URDF
- Terminal output labeled as error even when export is successful

### Added

- Exporting sensor prim frames to URDF
- Ability to set mesh path prefix
- Optionally setting output to directory (URDF file name automatically set to match USD file name)

## [0.1.1] - 2023-09-19
### Fixed

- Add missing dependencies and remove unused code

## [0.1.0] - 2023-07-27
### Added

- Initial version of Isaac Sim URDF exporter
