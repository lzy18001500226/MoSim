#!/bin/bash

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

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -n "$ZSH_VERSION" ]; then
    SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
fi
MY_DIR="$(realpath -s "$SCRIPT_DIR")"
# path=$SCRIPT_DIR
# while [[ $path != / ]];
# do
    
#     if ! find "$path" -maxdepth 1 -mindepth 1 -iname "_build" -exec false {} +
#     then
#         break
#     fi
#     # Note: if you want to ignore symlinks, use "$(realpath -s "$path"/..)"
#     path="$(readlink -f "$path"/..)"
    
# done
# build_path=$path/_build
export CARB_APP_PATH=$SCRIPT_DIR/kit
export EXP_PATH=$MY_DIR/apps
export ISAAC_PATH=$MY_DIR

cd $SCRIPT_DIR
. ./setup_python_env.sh
cd $OLDPWD

# remove Kit Python from PYTHONPATH to avoid conflicts with conda
export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "$SCRIPT_DIR/kit/python/lib/python3.11" | tr '\n' ':' | sed 's/:$//')
