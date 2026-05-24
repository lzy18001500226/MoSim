# Changelog

## [3.6.0] - 2025-07-10
### Added
- Added `robot_type`, `license`, `version`, `source`, and `changelog` to the Isaac Robot API.

## [3.5.1] - 2025-06-12
### Changed
- Get extension path using `os` module since carb tokens can not be resolved by Sphinx

## [3.5.0] - 2025-05-30
### Changed
- Added Isaac prefix to Robot Schema classes

## [3.4.2] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [3.4.1] - 2025-05-14
### Changed
- Fixed relationship names for robot links and joints.

## [3.4.0] - 2025-05-09
### Changed
- fixed minor errors on Applying surface gripper API types

### Added
- Added Robot Parsing Utils to generate  Robot Kinematic tree based on the joints available on the schema and their parent-child relationships.

## [3.3.3] - 2025-05-05
### Changed
- Fix API docs.

## [3.3.2] - 2025-04-18
### Changed
- Updates to surface gripper schema

## [3.3.1] - 2025-04-09
### Changed
- Update Isaac Sim robot asset path for the IsaacSim folder

## [3.3.0] - 2025-04-08
### Changed
- Updated Robot Schema to include Surface Gripper.

### Fixed
- Fixed build for robot schema include file

## [3.2.3] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [3.2.2] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [3.2.1] - 2025-03-26
### Changed
- Updates to work with Kit 107.2 and ABI=1

## [3.2.0] - 2025-03-06
### Added
- Added support for isaac:namespace attribute

## [3.1.4] - 2025-03-04
### Changed
- Update to kit 107.1 and fix build issues

## [3.1.3] - 2025-01-28
### Fixed
- Windows signing issue

## [3.1.2] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [3.1.1] - 2024-11-12
### Changed
- minor update to Robot Schema

## [3.1.0] - 2024-10-31
### Added
- First Version of Robot schema as a codeless implementation
- a few utilities in a c header and python utils fashion to deal with the codeless schema

## [3.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [3.0.0] - 2024-10-18
### Changed
- Extension renamed to isaacsim.robot.schema.

## [2.1.0] - 2024-06-28
### Added
- Added lightbeam sensor to Isaac Sensor Schema, bumping version

## [2.0.2] - 2024-04-19
### Changed
- Removed omni.usd.schema.physics dependency

## [2.0.1] - 2023-06-21
### Changed
- Direct inheritance for IsA schema IsaacContactSensor, IsaacImuSensor, Lidar, UltrasonicArray, Generic

## [2.0.0] - 2023-06-12
### Changed
- Updated to usd 22.11
- Update to kit 105.1
- Using omni-isaacsim-schema as dependency

## [1.1.0] - 2023-01-21
### Added
- named Override Attribute

## [1.0.0] - 2022-09-29
### Removed
- Remove DR and ROS bridge schemas

## [0.2.0] - 2022-03-21
### Added
- Add Isaac Sensor USD Schema
- Add Contact Sensor USD Schema
- Add IMU Sensor USD Schema

## [0.1.1] - 2021-08-02
### Added
- Add USS material support

## [0.1.0] - 2021-06-03
### Added
- Initial version of Isaac Sim Usd Schema Extension
