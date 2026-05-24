# Changelog
## [2.0.8] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [2.0.7] - 2025-05-16
### Changed
- Make extension target a specific kit version

## [2.0.6] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [2.0.5] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [2.0.4] - 2025-03-25
### Changed
- Add import tests for deprecated extensions

## [2.0.3] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [2.0.2] - 2025-01-21
### Fixed
- Missing module import

## [2.0.1] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [2.0.0] - 2024-09-29
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.util.mergemesh.

## [1.0.2] - 2024-07-17
### Fixed
- Missing dependency for tests

## [1.0.1] - 2024-04-18
### Added
- Dependency for tests

## [1.0.0] - 2024-04-12
### Added
- Code-Accessible Merge Mesh functionality (API)
- Merge Command
- Unit Tests
- Disable source assets when merging

### Changed
- Combine Materials now Creates the materials in the provided path if they don't exist

## [0.1.5] - 2024-04-10
### Fixed
- Fix Broken empty Material binding check

## [0.1.4] - 2023-08-09
### Fixed
- Switch from ui.Window to ScrollingWindow wrapper for extension because scrolling was broken

## [0.1.3] - 2023-06-12
### Changed
- Update to kit 105.1, omni.usd.utils -> omni.usd

## [0.1.2] - 2023-02-08
### Fixed
- add primvars normals when merging

## [0.1.1] - 2023-01-06
### Fixed
- onclick_fn warning when creating UI

## [0.1.0] - 2021-07-29
### Added
- Initial version of extension
