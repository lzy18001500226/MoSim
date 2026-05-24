# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from typing import Optional

import carb.settings
import omni.ext
import omni.kit.menu.utils
import omni.ui as ui
from omni.kit.browser.folder.core import TreeFolderBrowserWidgetEx

from .window import AssetBrowserWindow

_extension_instance = None
BROWSER_MENU_ROOT = "Window"
SETTING_ROOT = "/exts/isaacsim.asset.browser/"
SETTING_VISIBLE_AFTER_STARTUP = SETTING_ROOT + "visible_after_startup"
EXTENSION_NAME = "Isaac Sim Asset Browser"


class AssetBrowserExtension(omni.ext.IExt):
    @property
    def window(self) -> Optional[AssetBrowserWindow]:
        return self._window

    @property
    def browser_widget(self) -> Optional[TreeFolderBrowserWidgetEx]:
        return self._window._widget

    def on_startup(self, ext_id):
        self._ext_id = ext_id
        self._window = None
        ui.Workspace.set_show_window_fn(
            AssetBrowserWindow.WINDOW_TITLE,
            self._show_window,  # pylint: disable=unnecessary-lambda
        )
        self._register_menuitem()

        visible = carb.settings.get_settings().get_as_bool(SETTING_VISIBLE_AFTER_STARTUP)
        if visible:
            self._show_window(True)
        else:
            # Warmup model
            warmup = carb.settings.get_settings().get("/app/warmupMode") or False
            if warmup:
                from .model import AssetBrowserModel

                self.__model = AssetBrowserModel(run_warmup=True)

        global _extension_instance
        _extension_instance = self

    def on_shutdown(self):
        ui.Workspace.set_show_window_fn(AssetBrowserWindow.WINDOW_TITLE, None)
        omni.kit.menu.utils.remove_menu_items(self._menu_entry, name=BROWSER_MENU_ROOT)
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_action(self._ext_id, f"open_isaac_sim_asset_browser")

        if self._window is not None:
            self._window.destroy()
            self._window = None

        global _extension_instance
        _extension_instance = None

    def _show_window(self, visible) -> None:
        if visible:
            if self._window is None:
                self._window = AssetBrowserWindow(visible=True)
                self._window.set_visibility_changed_fn(self._on_visibility_changed)
            else:
                self._window.visible = True
            self._window.focus()
        else:
            self._window.visible = False

    def _toggle_window(self):
        self._show_window(not self._is_visible())

    def _register_menuitem(self):

        ## register the menu action
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.register_action(
            "isaacsim.asset.browser",
            f"open_isaac_sim_asset_browser",
            lambda: self._show_window(True),
            description=f"Open Isaac Sim Asset Browser",
        )

        self._menu_entry = [
            omni.kit.menu.utils.MenuItemDescription(
                name="Browsers",
                sub_menu=[
                    omni.kit.menu.utils.MenuItemDescription(
                        name="Isaac Sim Assets", ticked=True, ticked_fn=self._is_visible, onclick_fn=self._toggle_window
                    )
                ],
            )
        ]
        omni.kit.menu.utils.add_menu_items(self._menu_entry, BROWSER_MENU_ROOT)

    def _is_visible(self):
        return self._window.visible if self._window else False

    def _on_visibility_changed(self, visible):
        omni.kit.menu.utils.refresh_menu_items(BROWSER_MENU_ROOT)


def get_instance():
    return _extension_instance
