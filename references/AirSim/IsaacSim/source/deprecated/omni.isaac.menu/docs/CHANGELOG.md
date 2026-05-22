# Changelog
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

## [1.0.0] - 2024-09-30
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.gui.menu

## [0.7.3] - 2024-09-05
### Removed
- Grid Room from menu to match documentation

## [0.7.2] - 2024-09-03
### Added
- Missing robots to the menu

### Fixed
- some naming to match documentation

## [0.7.1] - 2024-08-26
### Added
- Missing environments to the menu

### Fixed
- Generation of April Tag

## [0.7.0] - 2024-08-23
### Added
- Several new robots to robot menu

### Changed
- Modifies robot menu to have multiple submenus based on robot type
- Aligns robot menu ordering with documentation

## [0.6.0] - 2024-08-21
### Changed
- Adds original Franka to robot asset menu
- Renames Franka -> Franka (alt. fingers)
- Moves Ant to Quadruped menu
- Adds Black Grid and Curved Grid menu options.

## [0.5.0] - 2024-07-10
### Removed
- Deprecated omni.isaac.dofbot and removed its usage.

## [0.4.1] - 2024-05-28
### Fixed
- Robotiq asset links

## [0.4.0] - 2024-05-24
### Changed
- Added leatherback

### Fixed
- broken USD paths

## [0.3.1] - 2024-05-11
### Changed
- Renamed Transporter to iw.hub

## [0.3.0] - 2024-05-07
### Added
- Added menu options for the new robots
- Added humanoid robot section

## [0.2.3] - 2024-04-22
### Fixed
- Sensor menu tests failing due to sensor extension now creates sensors on play, play timeline first before checking for values

## [0.2.2] - 2024-03-07
### Fixed
- Tests failing due to short delay when clicking, increased delay from 10 to 32 (default)

## [0.2.1] - 2024-02-20
### Fixed
- Extra dependencies from tests being incorrectly imported

## [0.2.0] - 2024-01-30
### Changed
- Changed sensor menu tests to verify sensor functionality through the sensor interfaces
- Added golden image test for the environment

## [0.1.0] - 2024-01-19
### Added
- Initial version of extension, moving menu code out of omni.isaac.utils extension
