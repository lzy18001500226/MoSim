# Changelog
## [1.0.6] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [1.0.5] - 2025-05-16
### Changed
- Make extension target a specific kit version

## [1.0.4] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [1.0.3] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [1.0.2] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [1.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [1.0.0] - 2024-09-30
### Deprecated

- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.robot.manipulators.examples.franka

## [0.4.0] - 2024-08-09
### Changed
- Deprecating extension. moving all content to be under manipulators.examples.universal_robots

## [0.3.5] - 2024-03-06
### Changed
- Updated Path to UR10

## [0.3.4] - 2024-02-02
### Changed
- Updated path to the nucleus extension

## [0.3.3] - 2023-12-11
### Changed
- Minor tweaks in bin filling position so pieces don't hit robot when falling

### Added
- Random piece orientation on drop

## [0.3.2] - 2023-02-01
### Changed
- Values for surface griper torque and force limits for bin filling so that the gripper breaks after filling the bin.

## [0.3.1] - 2022-12-09
### Changed
- Values for surface griper torque and force limits.

## [0.3.0] - 2022-07-26
### Removed
- Removed GripperController class and used the new ParallelGripper class instead.

### Changed
- Changed gripper_dof_indices argument in PickPlaceController to gripper.
- Changed gripper_dof_indices argument in StackingController to gripper.

## [0.2.3] - 2022-07-22
### Fixed
- Bug with adding a custom usd for manipulator

## [0.2.2] - 2022-05-27
### Fixed
- Fixed bug: typo when loading UR10 RMPflow controller without suction gripper

## [0.2.1] - 2022-05-04
### Changed

- backwards compatible change to UR10's post_reset() implementation. Removed the hard coded override, and added the hard coded config as a default config in initialize(). Functionality equivalent but uses the underlying Articulation objects's default config functionality.

## [0.2.0] - 2022-05-02
### Changed
- Changed InverseKinematicsSolver class to KinematicsSolver class, using the new LulaKinematicsSolver class in motion_generation

## [0.1.5] - 2022-04-21
### Changed
-Updated RmpFlowController class init alongside modifying motion_generation extension

## [0.1.4] - 2022-04-07
### Fixed
- Adding a gripper to UR10

## [0.1.3] - 2022-03-25
### Changed
- Updated RmpFlowController class alongside changes to motion_generation extension

## [0.1.2] - 2022-03-16
### Changed
- Replaced find_nucleus_server() with get_assets_root_path()

## [0.1.1] - 2021-12-02
### Changed
- Propagation of core api changes

## [0.1.0] - 2021-09-01
### Added
- Added UR10 class
