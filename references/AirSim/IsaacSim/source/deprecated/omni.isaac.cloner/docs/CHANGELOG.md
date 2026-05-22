# Changelog

## [1.0.7] - 2025-05-30
### Changed
- Update to match API changes in isaacsim.core.cloner

## [1.0.6] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [1.0.5] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [1.0.4] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [1.0.3] - 2025-03-25
### Changed
- Add import tests for deprecated extensions

## [1.0.2] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [1.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [1.0.0] - 2024-09-24
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.core.cloner

## [0.8.1] - 2024-02-07
### Changed
- Updated path to the nucleus extension

## [0.8.0] - 2024-02-02
### Changed
- Support executing cloner on non-context stage

## [0.7.3] - 2024-01-18
### Changed
- Changed get_assets_root_path to get_assets_root_path_async for the unit tests

## [0.7.2] - 2023-11-10
### Fixed
- Fixed error with GridCloner when offsets are passed
- Add test case with position and orientation offsets for GridCloner

## [0.7.1] - 2023-10-31
### Fixed
- Fixed the order in which xformop is set while cloning. Earlier a set was passed instead of list.

## [0.7.0] - 2023-07-26
### Added
- Exposed API for retrieving clone transorms from GridCloner
- Add unregister when physics replication is disabled

## [0.6.0] - 2023-07-19
### Changed
- When `positions` and `orientations` are None, the cloner keeps the Xform translation and orientation instead of using identity
- Makes the method `replicate_physics` public to allow users to have control over it

## [0.5.0] - 2023-04-27
### Added
- Added option to specify mode of cloning (inherit vs. copy)

## [0.4.1] - 2022-12-09
### Fixed
- Fixed crash when cloning with single environment

## [0.4.0] - 2022-11-18
### Added
- Added option to use omni.physics replication

## [0.3.0] - 2022-07-11
### Changed
- Added setting and deleting the different xform properties used by omni.isaac.core

## [0.2.1] - 2022-06-23
### Fixed
- Preserve scale property from source prim

## [0.2.0] - 2022-06-15
### Changed
- Optimized cloning and collision filtering logic
- Moved common utility functions to base Cloner class

## [0.1.2] - 2022-05-11
### Fixed
- Added dependency to omni.physx

## [0.1.1] - 2022-05-09
### Added
- Added documentation

### Changed
- Updated filter collision logic. Use inverted collision group filter for more efficient collision group generation.

## [0.1.0] - 2022-03-30
### Added
- Added Initial Classes
