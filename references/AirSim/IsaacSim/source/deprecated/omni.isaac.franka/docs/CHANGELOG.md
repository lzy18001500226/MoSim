# Changelog
## [1.0.7] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [1.0.6] - 2025-05-16
### Changed
- Make extension target a specific kit version

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

## [1.0.0] - 2024-09-30
### Deprecated

- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.robot.manipulators.examples.franka

## [0.5.0] - 2024-08-07
### Changed
- removed most content, deprecating extension, rerouting imports.

## [0.4.1] - 2024-02-02
### Changed
- Updated path to the nucleus extension

## [0.4.0] - 2022-09-27
### Removed
- usd files local to extension

## [0.3.0] - 2022-07-26
### Removed
- Removed GripperController class and used the new ParallelGripper class instead.

### Changed
- Changed gripper_dof_indices argument in PickPlaceController to gripper
- Changed gripper_dof_indices argument in StackingController to gripper

### Added
- Added deltas argument in Franka class for the gripper action deltas when openning or closing.

## [0.2.1] - 2022-07-22
### Fixed
- Bug with adding a custom usd for manipulator

## [0.2.0] - 2022-05-02
### Changed
- Changed InverseKinematicsSolver class to KinematicsSolver class, using the new LulaKinematicsSolver class in motion_generation

## [0.1.4] - 2022-04-21
### Changed
- Updated RmpFlowController class init alongside modifying motion_generation extension

## [0.1.3] - 2022-04-13
### Changed
- Fix Franka units in gripper open config.

## [0.1.2] - 2022-03-25
### Changed
- Updated RmpFlowController class alongside changes to motion_generation extension

## [0.1.1] - 2022-03-16
### Changed
- Replaced find_nucleus_server() with get_assets_root_path()

## [0.1.0] - 2021-09-01
### Added
- Added Franka class and and Franka Task Follower Class
