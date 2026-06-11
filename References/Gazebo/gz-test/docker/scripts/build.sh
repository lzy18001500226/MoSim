#!/bin/bash

./scripts/build_gz.sh gazebosim gz-cmake gz-cmake3
./scripts/build_gz.sh gazebosim gz-tools gz-tools2
./scripts/build_gz.sh gazebosim gz-utils gz-utils2
./scripts/build_gz.sh gazebosim gz-math gz-math7
./scripts/build_gz.sh gazebosim gz-common gz-common5
./scripts/build_gz.sh gazebosim gz-msgs gz-msgs9
./scripts/build_gz.sh gazebosim gz-transport gz-transport12
./scripts/build_gz.sh gazebosim gz-fuel-tools gz-fuel-tools8
./scripts/build_gz.sh gazebosim sdformat sdf13
./scripts/build_gz.sh gazebosim gz-plugin gz-plugin2
./scripts/build_gz.sh gazebosim gz-physics gz-physics6
./scripts/build_gz.sh gazebosim gz-rendering gz-rendering7
./scripts/build_gz.sh gazebosim gz-gui gz-gui7
./scripts/build_gz.sh gazebosim gz-sensors gz-sensors7
./scripts/build_gz.sh gazebosim gz-sim sensor_plugin_autoload
# ./scripts/build_gz.sh gazebosim gz-launch gz-launch6
