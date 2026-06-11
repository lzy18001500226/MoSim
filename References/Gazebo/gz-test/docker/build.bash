#!/usr/bin/env bash

#
# Copyright (C) 2022 Open Source Robotics Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

# Builds a Docker image.

# if [ $# -eq 0 ]
# then
#     echo "Usage: $0 directory-name"
#     exit 1
# fi
#
# # get path to current directory
# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#
# if [ ! -d $DIR/$1 ]
# then
#   echo "image-name must be a directory in the same folder as this script"
#   exit 2
# fi

user_id=$(id -u)
image_name=gz-test
private_key=$(cat ~/.ssh/id_rsa)

# Get the repo name.
#repo="$(basename `git rev-parse --show-toplevel`)"
#if [[ "$repo" == *"private" ]]; then
#  if [[ -z "${FUEL_TOKEN}" ]]; then
#    echo -e "\e[1;31mError: FUEL_TOKEN is not set\e[0m"
#    exit 1
#  fi
#fi

shift

rm -rf gz-test
git clone git@github.com:gazebosim/gz-test -b main
DOCKER_BUILDKIT=1 docker build --rm -t $image_name --build-arg user_id=$user_id .
rm -rf gz-test
