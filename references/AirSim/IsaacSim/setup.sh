#!/usr/bin/env bash

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e
set -u

# Tested on bare installs of:
#  - Ubuntu 18.04 / bionic
#  - Ubuntu 16.04 / xenial
#  - CentOS7

install_hostdeps_ubuntu() {
    # Historically we take care of installing these deps for devs. We really
    # shouldn't be doing this given that installing some of these deps will
    # potentially uninstall other things (competing python versions for
    # example)
    echo "Warning: about to run potentially destructive apt-get commands."
    echo "         waiting 5 seconds..."
    sleep 5
    sudo apt-get update
    sudo apt-get install -y python2.7 curl
}

install_hostdeps_centos() {
    # libatomic needed by streamsdk at runtime
    sudo yum install -y libatomic
}

do_usermod_and_end() {
    # $USER can be unset, $(whoami) works more reliably.
    sudo usermod -aG docker $(whoami)
    echo "You need to log out and back in for your environment to pick up 'docker' group membership."
    sleep 3
    echo "Attempting to force group membership reload for this shell. You may be prompted for your account password."
    set -x
    exec su --login $(whoami)
}

install_docker_ubuntu() {
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce

    do_usermod_and_end
}

install_docker_centos() {
    sudo yum install -y yum-utils device-mapper-persistent-data lvm2
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker

    do_usermod_and_end
}

main() {
    sudo -V >& /dev/null && HAVE_SUDO=1 || HAVE_SUDO=0
    if [[ "$HAVE_SUDO" == "0" ]]; then
        echo "Install 'sudo' before running this script."
        exit 1
    fi

    local DOCKER=$(which docker >& /dev/null)

    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        if [[ "x$NAME" == "xUbuntu" ]]; then
            install_hostdeps_ubuntu
            [[ "x$DOCKER" = "x" ]] && install_docker_ubuntu
        elif [[ "x$NAME" == "xCentOS Linux" ]]; then
            install_hostdeps_centos
            [[ "x$DOCKER" = "x" ]] && install_docker_centos
        fi
    else
        echo "Unable to determine distribution. Can't read /etc/os-release" | tee /dev/stderr
        exit 1
    fi
}
