# Gz_pkg_create : Tool for creating new gazebo package

[![GitHub open issues](https://img.shields.io/github/issues-raw/gazebosim/gz_pkg_create.svg)](https://github.com/gazebosim/gz_pkg_create/issues)
[![GitHub open pull requests](https://img.shields.io/github/issues-pr-raw/gazebosim/gz_pkg_create.svg)](https://github.com/gazebosim/gz_pkg_create/pulls)
[![Discourse topics](https://img.shields.io/discourse/https/community.gazebosim.org/topics.svg)](https://community.gazebosim.org)
[![Hex.pm](https://img.shields.io/hexpm/l/plug.svg)](https://www.apache.org/licenses/LICENSE-2.0)

Gazebo Package Create provides a subcommand which creates various template repositories based on user's requirements.
The tool uses Embedded Ruby files to create various templates.
You can get list of currently supported arguments at [tutorials](https://github.com/harshmahesheka/gz_pkg_create/blob/main/TUTORIALS.md).

[http://gazebosim.org](http://gazebosim.org)


# Install

Currently only source installation is supported.First build gazebo from souce ([link](https://gazebosim.org/docs/fortress/install_ubuntu_src)). Then clone this repository into src folder of your gazebo workspace. Then run  ``` colcon build --merge-install --packages-select ignition-pkg-create``` inside your gazebo workspace.

# Tutorials

Please see [TUTORIALS.md](https://github.com/harshmahesheka/gz_pkg_create/blob/main/TUTORIALS.md).

# Contributing

Please see the [contribution guide](https://gazebosim.org/docs/all/contributing).

# Code of Conduct

Please see
[CODE_OF_CONDUCT.md](https://github.com/gazebosim/gz-sim/blob/main/CODE_OF_CONDUCT.md).

# Versioning

This library uses [Semantic Versioning](https://semver.org/). Additionally, this library is part of the [Gazebo project](https://gazebosim.org) which periodically releases a versioned set of compatible and complimentary libraries. See the [Gazebo website](https://gazebosim.org) for version and release information.

# License

This library is licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). See also the [LICENSE](https://github.com/gazebosim/gz-sim/blob/main/LICENSE) file.
