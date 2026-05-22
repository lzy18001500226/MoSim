# Changelog
## [1.0.11] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [1.0.10] - 2025-05-16
### Changed
- Make extension target a specific kit version

## [1.0.9] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [1.0.8] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [1.0.7] - 2025-03-25
### Changed
- Add import tests for deprecated extensions

## [1.0.6] - 2025-03-20
### Changed
- Fix issues with duplicate extension startup from extra imports

## [1.0.5] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [1.0.4] - 2025-01-08
### Changed
- Fix extension renaming

## [1.0.3] - 2024-12-11
### Changed
- Fix extension renaming

## [1.0.2] - 2024-11-07
### Changed
- Fix minor typo

## [1.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [1.0.0] - 2024-09-27
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.asset.gen.conveyor

## [0.4.0] - 2024-06-13
### Changed
- Updated Physics API to use SurfaceVelocity instead of rigid Body deprecated modified Velocities.
- Added Velocity Variable in omnigraph to control the conveyor speed

### Removed
- UI elements that didn't move over
- Forcing Kinematics Body on Conveyor Creation

# Changelog

## [0.3.14] - 2024-05-06
### Removed
- Unused config file

# Changelog

## [0.3.13] - 2023-11-01
### Fixed
- Error when Node starts for the first time if it doesn't have a Texture translate attribute.

## [0.3.12] - 2023-08-28
### Changed
- added standard out fail pattern for the expected no prim found edge case for the ogn test

## [0.3.11] - 2023-08-10
### Changed
- Changed conveyor prim node input type from bundle to target

## [0.3.10] - 2023-06-13
### Changed
- Update to kit 105.1, build system update, omni.usd.utils -> omni.usd, usdPhysics -> pxr/usd/usdPhysics

## [0.3.9] - 2023-02-15
### Fixed
- UI regression where selected track card was not updated correctly

## [0.3.8] - 2023-02-14
### Changed
- Update asset path

## [0.3.7] - 2023-02-09
### Fixed
- Tests Use Fabric to get physx updates
- Error message when generating UI with image URL and destroing element before image finished loading
- Create Conveyor own hidden scope instead of using /Render

## [0.3.6] - 2023-01-25
### Fixed
- remove un-needed cpp ogn files from extension

## [0.3.5] - 2023-01-06
### Fixed
- onclick_fn warning when creating UI

## [0.3.4] - 2022-12-02
### Fixed
- Adaptive scale for assets not in the same meters per unit than open stage

## [0.3.3] - 2022-12-01
### Fixed
- CreateConveyorBelt command documentation update

## [0.3.2] - 2022-12-01
### Fixed
- CreateConveyorBelt command .do() only returns the created prim and not a tuple

## [0.3.1] - 2022-11-29
### Fixed
- OG Node wouldn't update if the node direction changed
- Assets Reorganization

### Added
- Sorting Assets

## [0.3.0] - 2022-11-22
### Added
- Digital Twin Library Conveyor Authoring tool
- Support for curved conveyors

### Changed
- Default path for creating conveyor command is now at prim parent instead of rigid body prim.

## [0.2.1] - 2022-09-07
### Fixed
- Fixes for kit 103.5

## [0.2.0] - 2022-07-22
### Changed
- Convert node to cpp backend
- Conveyor node renamed to IsaacConveyor

### Added
- Simplified creating multiple conveyors, multiple prims can be selected on creation using menu

## [0.1.1] - 2022-05-10
### Changed
- Change Tests to use meters as distance unit

## [0.1.0] - 2022-03-30
- First Version
