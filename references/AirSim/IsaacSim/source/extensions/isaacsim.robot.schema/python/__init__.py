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

import os

from pxr import Plug


def _register_plugin_path(path):
    result = Plug.Registry().RegisterPlugins(path)
    if not result:
        import carb

        carb.log_error(f"No plugins found at path {path}")


def _register_plugins(ext_path: str):
    _register_plugin_path(os.path.join(ext_path, "usd", "schema", "isaac", "robot_schema"))

    plugin_path = os.path.join(ext_path, "plugins", "plugins")
    _register_plugin_path(os.path.join(plugin_path, "isaacSensorSchema", "resources"))
    _register_plugin_path(os.path.join(plugin_path, "rangeSensorSchema", "resources"))


# carb.tokens.get_tokens_interface().resolve("${isaacsim.robot.schema}") can not be resolved by sphinx
ext_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_register_plugins(ext_path)


from . import robot_schema
