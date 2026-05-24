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
from .model import ExampleBrowserModel
from .property_delegate import EmptyPropertyDelegate, MultiPropertyDelegate, PropAssetPropertyDelegate
from .style import THUMBNAIL_STYLE


class BrowserWidget(TreeFolderBrowserWidgetEx):
    def _on_thumbnail_size_changed(self, thumbnail_size: int) -> None:
        # to keep the labels visible at all times
        self._delegate.hide_label = False  # thumbnail_size < 64
        self._delegate.item_changed(None, None)


class ExampleBrowserWindow(ui.Window):
    """
    Represent a window to show Assets
    """

    WINDOW_TITLE = "Robotics Examples"

    def __init__(self, model: ExampleBrowserModel, visible=True):
        super().__init__(self.WINDOW_TITLE, visible=visible)

        self.frame.set_build_fn(self._build_ui)

        self._browser_model = model
        self._delegate = None
        self._widget = None

        # Dock it to the same space where Stage is docked.
        self.deferred_dock_in("Content")

    def _build_ui(self):
        preload_folder = os.path.abspath(carb.tokens.get_tokens_interface().resolve("${app}/../predownload"))
        self._delegate = AssetDetailDelegate(self._browser_model)

        with self.frame:
            with ui.VStack(spacing=15):
                self._widget = BrowserWidget(
                    self._browser_model,
                    detail_delegate=self._delegate,
                    predownload_folder=preload_folder,
                    min_thumbnail_size=32,
                    max_thumbnail_size=128,
                    detail_thumbnail_size=64,
                    style=THUMBNAIL_STYLE,
                    property_delegates=[EmptyPropertyDelegate(), PropAssetPropertyDelegate(), MultiPropertyDelegate()],
                )
