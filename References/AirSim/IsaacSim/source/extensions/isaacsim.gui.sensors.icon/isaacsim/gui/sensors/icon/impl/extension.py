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
from pathlib import Path

import carb.settings
import omni.ext
import omni.kit.widget.stage
from omni.kit.viewport.menubar.core import CategoryStateItem
from omni.kit.viewport.menubar.display import get_instance as get_menubar_display_instance
from omni.kit.viewport.registry import RegisterScene

from .model import IconModel
from .scene import VISIBLE_SETTING, IconScene

_extension = None


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class SensorIconExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        global _extension
        _extension = self
        self._vp2_scene = None
        self._vp2_scene = RegisterScene(IconScene, ext_id)

        # register sensor icon to stage widget
        self._sensor_icon_dir = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._sensor_icon_path = str(Path(self._sensor_icon_dir).joinpath("icons/icoSensors.svg"))

        self._sensor_tpye = IconModel.SENSOR_TYPES
        self._stage_icons = omni.kit.widget.stage.StageIcons()
        for sensor_type in self._sensor_tpye:
            self._stage_icons.set(sensor_type, self._sensor_icon_path)

        # TODO: should we distinguish different viewport?
        # viewport_api_id = str(get_active_viewport().id)
        # sensor_icon_visible_setting = f"/persistent/app/viewport/{viewport_api_id}/sensor_icon/visible"
        self._menubar_display_inst = get_menubar_display_instance()
        self._custom_item = CategoryStateItem("Sensors", setting_path=VISIBLE_SETTING)
        self._menubar_display_inst.register_custom_category_item("Show By Type", self._custom_item)

    def on_shutdown(self):  # pragma: no cover
        global _extension
        _extension = None
        self._vp2_scene = None

        # deregister sensor icon to stage widget
        for sensor_type in self._sensor_tpye:
            self._stage_icons.set(sensor_type, self._sensor_icon_path)

        self._menubar_display_inst.deregister_custom_category_item("Show By Type", self._custom_item)


def get_instance():
    return _extension
