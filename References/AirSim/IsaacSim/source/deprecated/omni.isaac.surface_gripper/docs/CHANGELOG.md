# Changelog
## [2.0.6] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [2.0.5] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [2.0.4] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [2.0.3] - 2025-03-25
### Changed
- Add import tests for deprecated extensions

## [2.0.2] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [2.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [2.0.0] - 2024-09-27
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.robot.surface_gripper

## [1.0.1] - 2024-04-01
### Changed
- Changed Dynamic Control Raycast into Physx scene query raycast.

## [1.0.0] - 2024-03-13
### Changed
- Extension refactored into multiple components.  See omni.isaac.surface_gripper.ui.

## [0.8.2] - 2024-03-07
### Changed
- Removed the usage of the deprecated dynamic_control extension

## [0.8.1] - 2024-03-04
### Changed
- Updated omnigraph nodes to use per instance state instead of internal state

## [0.8.0] - 2024-01-08
### Changed
- Moved header files to extension

## [0.7.0] - 2023-11-29
### Changed
- Location on the Menu reverted back to from Create->Isaac->End Effector

## [0.6.0] - 2023-11-20
### Changed
- Location on the Menu changed from Create->Isaac->End Effector to Create->Isaac->Robot.

## [0.5.0] - 2023-09-26
### Changed
- Updated ogn node to prevent issue where it would only call for close on first attempt.
- Automatically move gripper origin out of collision body, with a warning to tell how much to push it forward

## [0.4.1] - 2023-08-11
### Changed
- Updated ogn node prims types from bundle to ogn

## [0.4.0] - 2023-01-03
### Changed
- Update to new action based menu system

## [0.3.2] - 2022-12-01
### Fixed
- CreateSurfaceGripper command documentation update

## [0.3.1] - 2022-12-01
### Fixed
- CreateSurfaceGripper command .do() only returns the created prim and not a tuple

## [0.3.0] - 2022-10-27
### Added
- Moved surface gripper to Create -> Isaac -> End Effector menu
- More Robots, Environments to menu

## [0.2.0] - 2022-10-14
### Added
- Logic for keeping surface gripper attempting to close until it reaches some object

## [0.1.3] - 2022-09-07
### Fixed
- Fixes for kit 103.5

## [0.1.2] - 2022-05-10
### Changed
- Change Tests to use meters as distance unit

## [0.1.1] - 2022-05-03
### Added
- Surface Gripper Omnigraph Node

## [0.1.0] - 2021-07-31
### Added
- Initial version of extension
