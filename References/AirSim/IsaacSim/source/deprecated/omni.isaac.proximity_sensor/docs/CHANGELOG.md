# Changelog
## [2.0.7] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [2.0.6] - 2025-05-16
### Changed
- Make extension target a specific kit version

## [2.0.5] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [2.0.4] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [2.0.3] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [2.0.2] - 2024-10-24
### Changed
- Renames ProximitySensor -> Sensor, ProximitySensorManager -> SensorManager in extension namespace.

- Updated dependencies and imports after renaming

## [2.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [2.0.0] - 2023-09-23
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.sensors.physx.

## [1.0.1] - 2023-06-12
### Changed
- Update to kit 105.1, omni.usd.utils -> omni.usd

## [1.0.0] - 2022-06-27
### Added
- Added callback functions for on_entered, on_exited, and is_inside
- Detects overlap for multiple collision meshes
- Tracks duration of overlap for multiple collision meshes

### Changed
- Extent is calculated internally and can be dynamic
