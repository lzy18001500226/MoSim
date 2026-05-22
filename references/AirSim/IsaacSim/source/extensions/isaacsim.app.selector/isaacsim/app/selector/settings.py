# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import platform

# this file own the settings Strings so they can easily be shared and access from the other part of the App Selector
SHOW_CONSOLE_SETTING = "/persistent/ext/isaacsim.app.selector/show_console"
PERSISTENT_SELECTOR_SETTING = "/persistent/ext/isaacsim.app.selector/persistent_selector"

APPS_SETTING = "/ext/isaacsim.app.selector/apps"
EXPERIMENTAL_APPS_SETTING = "/ext/isaacsim.app.selector/experimental_apps"
AUTO_START_SETTING = "/persistent/ext/isaacsim.app.selector/auto_start"

DEFAULT_APP_SETTING = "/persistent/ext/isaacsim.app.selector/default_app"
EXTRA_ARGS_SETTING = "/persistent/ext/isaacsim.app.selector/extra_args"
ECO_MODE_SETTING = "/persistent/rtx/ecoMode/enabled"

PERSISTENT_ROS_BRIDGE_SETTING = "/persistent/ext/isaacsim.app.selector/ros_bridge_extension"
ROS_BRIDGE_EXTENSIONS = ["", "isaacsim.ros2.bridge"]

PERSISTENT_ROS_INTERNAL_LIBS_SETTING = "/persistent/ext/isaacsim.app.selector/ros_internal_libs"
