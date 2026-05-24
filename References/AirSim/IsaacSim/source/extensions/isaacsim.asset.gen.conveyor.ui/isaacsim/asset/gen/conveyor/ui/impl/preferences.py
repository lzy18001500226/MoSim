# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import asyncio
import os
from pathlib import Path
from typing import Callable

import carb
import omni
import omni.ui as ui
from isaacsim.storage.native import nucleus
from omni.kit.window.preferences import PERSISTENT_SETTINGS_PREFIX, PreferenceBuilder, SettingType

SETTINGS_PATH = "/persistent/exts/isaacsim.asset.gen.conveyor.ui.settings"

ASSETS_LOCATION = f"{SETTINGS_PATH}/assets_location"
CONFIG_LOCATION = f"{SETTINGS_PATH}/config_location"


def Singleton(class_):
    """A singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def create_filepicker(title: str, click_apply_fn: Callable = None, error_fn: Callable = None):
    from omni.kit.window.filepicker import FilePickerDialog

    async def on_click_handler(filename: str, dirname: str, dialog: FilePickerDialog, click_fn: Callable):
        dirname = dirname.strip()
        if filename and dirname and not dirname.endswith("/"):
            dirname += "/"
        fullpath = f"{dirname}{filename}"
        if click_fn:
            click_fn(fullpath)
        dialog.hide()

    dialog = FilePickerDialog(
        title,
        allow_multi_selection=False,
        apply_button_label="Select",
        click_apply_handler=lambda filename, dirname: asyncio.ensure_future(
            on_click_handler(filename, dirname, dialog, click_apply_fn)
        ),
        click_cancel_handler=lambda filename, dirname: dialog.hide(),
        error_handler=error_fn,
    )


@Singleton
class ConveyorBuilderPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Conveyor Builder")
        self._settings = carb.settings.get_settings()

    def reset_config_default(self):
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = ext_manager.get_enabled_extension_id("isaacsim.asset.gen.conveyor.ui")
        extension_path = ext_manager.get_extension_path(ext_id)
        cfg = Path(extension_path).joinpath("data").joinpath("track_types.json")
        self._settings.set(CONFIG_LOCATION, str(cfg))

    def reset_assets_default(self):
        timeout = carb.settings.get_settings().get("/persistent/isaac/asset_root/timeout")
        carb.settings.get_settings().set("/persistent/isaac/asset_root/timeout", 1.0)
        path = nucleus.get_assets_root_path()
        if timeout:
            carb.settings.get_settings().set("/persistent/isaac/asset_root/timeout", timeout)
        self._settings.set(ASSETS_LOCATION, f"{path}/Isaac/Props/Conveyors/")

    def cleanup_slashes(self, path: str, is_directory: bool = False) -> str:
        """
        Makes path/slashes uniform

        Args:
            path: path
            is_directory is path a directory, so final slash can be added

        Returns:
            path
        """
        # path = path.replace(":/", "://", 1)
        if is_directory:
            if path[-1] != "/":
                path += "/"
        return path.replace("\\", "/")

    def build(self):
        with ui.VStack(height=0):
            with self.add_frame("General"):
                with ui.VStack(height=0, spacing=5):
                    with ui.HStack(height=24, spacing=4):
                        ui.Label("Conveyor Assets Location", width=290)
                        widget = ui.StringField(height=20)
                        widget.model.set_value(self.assets_location)
                        widget.model.add_end_edit_fn(
                            lambda a, w=widget: self._on_file_pick(a.get_value_as_string(), w, ASSETS_LOCATION)
                        )

                        def reset():
                            self.reset_assets_default()
                            widget.model.set_value(self.assets_location)

                        ui.Button(
                            style={"image_url": "resources/icons/folder.png"},
                            clicked_fn=lambda p=self.cleanup_slashes(
                                self.assets_location
                            ), w=widget: self._on_browse_button_fn(p, w, ASSETS_LOCATION),
                            width=24,
                        )

                        def reset_asset(w):
                            self.reset_assets_default()
                            w.model.set_value(self.assets_location)

                        ui.Button(
                            "Reset to Default",
                            clicked_fn=lambda a=widget: reset_asset(a),
                            width=24,
                        )

                    with ui.HStack(height=24, spacing=4):
                        ui.Label("Conveyor Config", width=290)
                        widget = ui.StringField(height=20)
                        widget.model.set_value(self.config_file)
                        widget.model.add_end_edit_fn(
                            lambda a, w=widget: self._on_file_pick(a.get_value_as_string(), w, CONFIG_LOCATION)
                        )
                        ui.Button(
                            style={"image_url": "resources/icons/folder.png"},
                            clicked_fn=lambda p=self.cleanup_slashes(
                                self.config_file
                            ), w=widget: self._on_browse_button_fn(p, w, CONFIG_LOCATION),
                            width=24,
                        )

                        def reset_cfg(w):
                            self.reset_config_default()
                            w.model.set_value(self.config_file)

                        ui.Button(
                            "Reset to Default",
                            clicked_fn=lambda a=widget: reset_cfg(a),
                            width=24,
                        )
        ui.Spacer(height=ui.Fraction(1))

    def _on_browse_button_fn(self, path, widget, setting):
        """Called when the user picks the Browse button."""
        file_pick = create_filepicker(
            title="Select Directory" if setting == ASSETS_LOCATION else "Select Config File",
            click_apply_fn=lambda p=self.cleanup_slashes(path), w=widget: self._on_file_pick(
                p, widget=w, setting=setting
            ),
        )
        # file_pick.show(path)

    def _on_file_pick(self, full_path, widget, setting):
        """Called when the user accepts directory in the Select Directory dialog."""
        directory = self.cleanup_slashes(full_path, not full_path.endswith(".json"))
        self._settings.set(setting, directory)
        widget.model.set_value(directory)

    @property
    def assets_location(self):
        if self._settings.get(ASSETS_LOCATION) is None:
            self.reset_assets_default()

        return self._settings.get(ASSETS_LOCATION)

    @property
    def config_file(self):
        if self._settings.get(CONFIG_LOCATION) is None:
            self.reset_config_default()

        return self._settings.get(CONFIG_LOCATION)
