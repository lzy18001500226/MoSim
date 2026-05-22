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

import os
from typing import Optional

import carb.settings
import omni.ui as ui
from omni.kit.browser.core import TreeCategoryDelegate
from omni.kit.browser.folder.core import TreeFolderBrowserWidgetEx

from .delegate import AssetDetailDelegate
from .empty_property_delegate import EmptyPropertyDelegate
from .model import AssetBrowserModel
from .multi_property_delegate import MultiPropertyDelegate
from .options_menu import FolderOptionsMenu
from .prop_property_delegate import PropAssetPropertyDelegate
from .style import PROPERTY_STYLE


class BrowserWidget(TreeFolderBrowserWidgetEx):
    def _on_thumbnail_size_changed(self, thumbnail_size: int) -> None:
        self._delegate.hide_label = False  # thumbnail_size < 64
        self._delegate.item_changed(None, None)


class AssetBrowserWindow(ui.Window):
    """
    Represent a window to show Assets
    """

    WINDOW_TITLE = "Isaac Sim Assets [Beta]"

    def __init__(self, visible=True):
        super().__init__(self.WINDOW_TITLE, visible=visible)
        self.deferred_dock_in("Content")

        self._options_menu: Optional[FolderOptionsMenu] = None

        self.frame.set_build_fn(self._build_ui)

        self._browser_model = None
        self._delegate = None
        self._widget = None

        # Dock it to the same space where Stage is docked.
        self.deferred_dock_in("Content")

    def destroy(self):
        if self._browser_model:
            self._browser_model.destroy()
            self._browser_model = None
        if self._delegate:
            self._delegate.destroy()
            self._delegate = None
        if self._widget:
            self._widget.destroy()
            self._widget = None
        if self._options_menu:
            self._options_menu.destroy()
            self._options_menu = None

        super().destroy()

    def _build_ui(self):
        preload_folder = os.path.abspath(carb.tokens.get_tokens_interface().resolve("${app}/../predownload"))
        self._browser_model = AssetBrowserModel()
        self._delegate = AssetDetailDelegate(self._browser_model)
        self._options_menu = FolderOptionsMenu()

        with self.frame:
            with ui.VStack(spacing=15):
                self._widget = BrowserWidget(
                    self._browser_model,
                    detail_delegate=self._delegate,
                    options_menu=self._options_menu,
                    predownload_folder=preload_folder,
                    min_thumbnail_size=32,
                    max_thumbnail_size=128,
                    detail_thumbnail_size=64,
                    style=PROPERTY_STYLE,
                    property_delegates=[EmptyPropertyDelegate(), PropAssetPropertyDelegate(), MultiPropertyDelegate()],
                )
