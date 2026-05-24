# Changelog

## [3.0.0] - 2025-08-25
### Changed
- Removed unused python packages: numpy-quaternion, selenium, construct, nvsmi, plotly

## [2.7.0] - 2025-08-08
### Changed
- Update to osqp==0.6.7.post3
- Remove jinja2 as its in omni.kit.pip_archive

## [2.6.2] - 2025-07-29
### Changed
- Update to qdldl==0.1.7.post5
- Update to tornado==6.5.1

## [2.6.1] - 2025-06-05
### Fixed
- Fixed broken test

## [2.6.0] - 2025-06-02
### Changed
- Remove webbot==0.34
- Update matplotlib==3.10.0, gunicorn==22.0.0, tornado==6.4.2

## [2.5.5] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [2.5.4] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [2.5.3] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [2.5.2] - 2025-03-04
### Changed
- Update to kit 107.1 and fix build issues

## [2.5.1] - 2025-01-30
### Changed
- Updated to latest release changes

## [2.5.0] - 2025-01-16
### Changed
- updated matplotlib==3.10.0,
- added contourpy==1.3.1, fonttools==4.55.3, python-dateutil==2.9.0.post0, six==1.17.0

## [2.4.0] - 2025-01-15
### Changed
- Update to Kit 107.x, Python 3.11

## [2.3.3] - 2025-01-14
### Changed
- Update extension description and add extension specific test settings

## [2.3.2] - 2024-12-01
### Changed
- Make this extension python version specific

## [2.3.1] - 2024-10-28
### Changed
- Remove test imports from runtime

## [2.3.0] - 2024-05-16
### Added
- pyperclip==1.8.0

## [2.2.2] - 2024-05-14
### Changed
- Update gunicorn to 22.0.0

## [2.2.1] - 2023-07-05
### Changed
- Removed unused omni.kit.pipapi dependency

## [2.2.0] - 2023-05-15
### Removed
- boto3, s3transfer to omni.pip.compute

## [2.1.0] - 2023-05-08
### Removed
- scipy, pyyaml to omni.pip.compute
- botocore, urllib3, charset-normalizer as they are already in omni.kit.pip_archive

## [2.0.1] - 2022-12-13
### Changed
- make extension os specific

## [2.0.0] - 2022-12-13
### Removed
- certifi install at runtime

## [1.2.0] - 2022-07-20
### Added
- boto3, s3transfer

## [1.1.0] - 2022-07-11
### Changed
- Make extension kit sdk version specific

## [1.0.0] - 2022-07-01
### Changed
- Updating version for publishing

## [0.3.0] - 2022-04-16
### Added
- osqp, qdldl

## [0.2.0] - 2022-01-13
### Added
- Split Isaac Pip Archive into Core and ML archives

## [0.1.0] - 2021-08-24
### Added
- Initial version of Isaac Pip Archive
