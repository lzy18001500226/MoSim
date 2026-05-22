# Changelog

## [2.10.0] - 2025-08-21
### Changed
- Deprecate app selector

## [2.9.6] - 2025-06-09
### Changed
- Use default icon if app specific icon is not found

## [2.9.5] - 2025-06-04
### Fixed
- App selector can now load ROS 2 Jazzy internal libraries in Ubuntu

## [2.9.4] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [2.9.3] - 2025-05-16
### Changed
- Make extension target a specific kit version

## [2.9.2] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [2.9.1] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [2.9.0] - 2025-03-05
### Changed
- Add support for ROS2 Jazzy

## [2.8.9] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [2.8.8] - 2024-12-30
### Fixed
- Errors due to missing icons when using this extension with app template

## [2.8.7] - 2024-12-12
### Changed
- Fixed combobox dropdown

## [2.8.6] - 2024-11-19
### Changed
- Updated icons

## [2.8.5] - 2024-10-28
### Changed
- Merge headless modes

## [2.8.4] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming
- Rename to isaacsim.app.selector

## [2.8.3] - 2024-09-23
### Changed
- Update dependency omni.isaac.version to isaacsim.core.version

## [2.8.2] - 2024-09-02
### Fixed
- Spelling mistake in UI

## [2.8.1] - 2024-05-23
### Fixed
- Forward the internal environment variables to support configuring the ROS bridge for x-terminal-emulator

## [2.8.0] - 2024-05-20
### Changed
- ROS1 bridge and ROS2 foxy are marked as deprecated

## [2.7.1] - 2024-05-16
### Changed
- Changed ROS2 Internal Libraries app selector setting to be persistent.

## [2.7.0] - 2024-04-19
### Added
- Added button to clear caches

## [2.6.3] - 2024-04-17
### Fixed
- Made App Selector window non-detachable

## [2.6.2] - 2024-04-16
### Fixed
- Working directory for wrapped gnome-terminal called using x-terminal-emulator

## [2.6.1] - 2024-04-15
### Changed
- Changed ecomode checkbox to persist if user checks or unchecks

## [2.6.0] - 2024-04-12
### Added
- Dropdown to use internal ros2 libraries when applicable
- Warning messages for when ROS2 bridge is selected and env vars are incorrectly configured.

## [2.5.0] - 2024-04-10
### Added
- Added checkbox to enable eco mode on startup

## [2.4.0] - 2024-03-11
### Changed
- Replace gnome-terminal with x-terminal-emulator to support non-gnome-based desktops

## [2.3.2] - 2023-10-13
### Changed
- Set ROS bridge field to blank so users can pick if they want to start with ROS1/ROS2

### Fixed
- source bash when starting sim so env vars are properly set

## [2.3.1] - 2023-08-16
### Fixed
- Make it clearer that text box for package path is not editable

## [2.3.0] - 2023-08-16
### Changed
- Deprecate WebSocket

## [2.2.1] - 2023-06-22
### Fixed
- Selector not starting with kit 105.1

## [2.2.0] - 2023-01-23
### Added
- dropdown menu to select ros bridge

## [2.1.2] - 2022-12-01
### Changed
- Fix show_console not persistent

## [2.1.1] - 2022-05-12
### Changed
- Use omni.isaac.version.get_version()

## [2.1.0] - 2022-04-29
### Changed
- Rename Headless Kit Remote app to Headless Native app

## [2.0.0] - 2022-04-28
### Changed
- Rename App Launcher to App Selector

## [1.0.0] - 2021-10-22
### Added
- Added first version of App Launcher.
