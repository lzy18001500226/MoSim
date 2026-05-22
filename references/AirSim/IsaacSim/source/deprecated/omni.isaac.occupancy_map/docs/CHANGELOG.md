# Changelog
## [2.0.8] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [2.0.7] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [2.0.6] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [2.0.5] - 2025-03-25
### Changed
- Add import tests for deprecated extensions

## [2.0.4] - 2025-03-20
### Changed
- Fix issues with duplicate extension startup from extra imports

## [2.0.3] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [2.0.2] - 2025-01-08
### Changed
- Fix extension renaming

## [2.0.1] - 2024-11-24
### Changed
- Updated dependencies and imports after renaming

## [2.0.0] - 2024-11-07
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.asset.gen.omap

## [1.0.3] - 2024-09-03
### Fixed
- Prevent cell size being less than or equal to 0 by showing a warning message and using a default value

## [1.0.2] - 2024-07-08
### Changed
- Remove unused omni.debugdraw interface

## [1.0.1] - 2024-04-16
### Fixed
- Update IStageUpdate usage to fix deprecation error

## [1.0.0] - 2024-03-11
### Changed
- Refactored into components

## [0.4.3] - 2024-02-07
### Changed
- Updated path to the nucleus extension

## [0.4.2] - 2024-02-07
### Fixed
- Issues with instanceable assets when using non physx collision mesh option
- Cell size not updating based on the current stage units. On stage load the cell size is set to 5cm or 0.05m depending on the units.

## [0.4.1] - 2024-01-18
### Changed
- Changed get_assets_root_path to get_assets_root_path_async for the unit tests

## [0.4.0] - 2024-01-08
### Changed
- Moved header files to extension

## [0.3.2] - 2023-12-12
### Fixed
- Updated api docs to mention correct return types.

## [0.3.1] - 2023-08-09
### Fixed
- Switch from ui.Window to ScrollingWindow wrapper for extension because scrolling was broken

## [0.3.0] - 2023-07-14
### Added
- Checkbox to use USD triangle geometry instead of physx approx for occupancy map generation. Useful for generating occupancy maps for PhysX vs RTX lidar.

## [0.2.8] - 2023-06-12
### Changed
- Update to kit 105.1, update build system

## [0.2.7] - 2023-01-06
### Fixed
- onclick_fn warning when creating UI

## [0.2.6] - 2022-11-28
### Fixed
- Fix duplicate symbol issue by statically linking against octomap for linux

## [0.2.5] - 2022-09-07
### Fixed
- Fixes for kit 103.5

## [0.2.4] - 2022-05-24
### Fixed
- block world default to meters

## [0.2.3] - 2022-05-16
### Fixed
- scale_to_meters parameter

## [0.2.2] - 2022-05-14
### Fixed
- Deadlock when generating data

## [0.2.1] - 2022-03-16
### Changed
- Replaced find_nucleus_server() with get_assets_root_path()

## [0.2.0] - 2022-03-07
### Added
- Add ability to generate 3d occupancy data

### Changed
- Api's always return 3d point data

## [0.1.1] - 2020-09-15
### Added

- 3D Occupancy Map support that allow 2D maps to be generated from 3D volumes
- Block World Extension that allows a 2D map image to be converted to 3D geometry

### Changed

- Made UI Simpler
- Improved performance
- Added debug visualization

## [0.1.0] - 2020-07-08
### Added
- Initial version of Isaac Sim Occupancy Map Extension
