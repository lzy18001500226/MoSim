# Changelog
## [1.3.2] - 2025-10-04
### Changed
- Spawn Entity service now attempts to load given path with default asset root prefix if given path is initially not found.

## [1.3.1] - 2025-09-22
### Changed
- Minor updates to README

## [1.3.0] - 2025-09-18
### Changed
- Added rclpy executors for better performance.
- Added simulate_steps_cancel_callback function.
- Load world service now attempts to load given path with default asset root prefix if given path is initially not found.

### Fixed
- Modular service and action registration mechanism

## [1.2.0] - 2025-09-02
### Added
- Simulation Interfaces v1.1.0 (World services) now supported.

### Changed
- Hidden /Render* prims are excluded from Entity retrieval services
- Extension initialization such that missing ROS service dependencies no longer cause a fatal error.

## [1.1.6] - 2025-07-18
### Fixed
- Velocity states correctly retrieved for rigid body prims.

## [1.1.5] - 2025-07-10
### Fixed
- Prim filtering in entity_utils when retrieving states.

### Changed
- Instance Proxy prims are currently not supported.

## [1.1.4] - 2025-07-07
### Fixed
- Correctly enable omni.kit.loop-isaac in test dependency (fixes issue from 1.1.3)

## [1.1.3] - 2025-07-03
### Changed
- Make omni.kit.loop-isaac an explicit test dependency

## [1.1.2] - 2025-06-25
### Changed
- Add --reset-user to test args

## [1.1.1] - 2025-06-24
### Fixed
- Resolved an issue where ROS 2 spinning errors would occur upon closing Isaac Sim.

## [1.1.0] - 2025-06-03
### Changed
- Use isaacsim.core.experimental for prim operations
- Reshuffled extension files

### Added
- Unit tests

## [1.0.2] - 2025-05-31
### Changed
- Use default nucleus server for all tests

## [1.0.1] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [1.0.0] - 2025-04-30
### Added
- New ROS 2 Sim Control extension to control Isaac Sim using Simulation Interfaces (v1.0.0: https://github.com/ros-simulation/simulation_interfaces/releases/tag/1.0.0)
