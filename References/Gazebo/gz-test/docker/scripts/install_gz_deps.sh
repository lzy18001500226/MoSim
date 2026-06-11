#!/bin/bash

set -o errexit
set -o verbose

sudo apt-get update

# Things that are used all over the gz stack
sudo apt-get install --no-install-recommends -y \
  doxygen \
  libbullet-dev \
  libtinyxml2-dev \
  libprotoc-dev libprotobuf-dev \
  protobuf-compiler \
  ruby-ronn \
  ruby-dev \
  swig \
  uuid-dev

# gz-common dependencies
sudo apt-get install --no-install-recommends -y \
  libavcodec-dev \
  libavdevice-dev \
  libavformat-dev \
  libavutil-dev \
  libfreeimage-dev \
  libgts-dev \
  libswscale-dev

# gz-gui dependencies
sudo apt-get install --no-install-recommends -y \
  qtbase5-dev \
  qtdeclarative5-dev \
  qtquickcontrols2-5-dev \
  qml-module-qtquick2 \
  qml-module-qtquick-controls \
  qml-module-qtquick-controls2 \
  qml-module-qtquick-dialogs \
  qml-module-qtquick-layouts \
  qml-module-qt-labs-folderlistmodel \
  qml-module-qt-labs-settings \
  qml-module-qtgraphicaleffects

# gz-rendering dependencies
sudo apt-get install --no-install-recommends -y \
  libogre-1.9-dev \
  libogre-next-2.3-dev \
  libglew-dev \
  libfreeimage-dev \
  freeglut3-dev \
  libxmu-dev \
  libxi-dev

# gz-transport dependencies
sudo apt-get install --no-install-recommends -y \
  libzmq3-dev \
  libsqlite3-dev

# SDFormat dependencies
sudo apt-get install --no-install-recommends -y \
  libtinyxml-dev libxml2-dev

# gz-fuel_tools dependencies
sudo apt-get install --no-install-recommends -y \
  libcurl4-openssl-dev libjsoncpp-dev libzip-dev curl libyaml-dev

# gz-physics dependencies
sudo apt-get install --no-install-recommends -y \
  libeigen3-dev \
  libdart-collision-ode-dev \
  libdart-dev \
  libdart-external-ikfast-dev \
  libdart-external-odelcpsolver-dev \
  libdart-utils-urdf-dev \
  libbenchmark-dev

# gz-gazebo dependencies
sudo apt-get install --no-install-recommends -y \
  qml-module-qtqml-models2

sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*
