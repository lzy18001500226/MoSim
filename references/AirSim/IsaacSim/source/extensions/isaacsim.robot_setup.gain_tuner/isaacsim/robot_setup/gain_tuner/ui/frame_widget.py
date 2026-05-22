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
from functools import partial
from typing import Callable, List, Optional, Tuple, Union

import numpy as np
import omni.ui as ui
from isaacsim.gui.components.element_wrappers import CollapsableFrame
from isaacsim.gui.components.ui_utils import get_style, on_copy_to_clipboard
from isaacsim.gui.components.widgets import DynamicComboBoxModel

from .style import get_style as get_custom_style

LABEL_WIDTH = 90


class CustomCollapsableFrame(CollapsableFrame):
    def __init__(self, *args, **kwargs):
        self._show_copy_button = kwargs.get("show_copy_button", False)
        kwargs.pop("show_copy_button", None)
        self._copy_content = None
        super().__init__(*args, **kwargs)

    def set_copy_content(self, copy_content: any):
        self._copy_content = copy_content

    def _build_header(self, collapsed: bool, title: str):
        with ui.HStack(height=34, style=get_custom_style()):
            ui.Spacer(width=4)
            with ui.VStack(width=10):
                ui.Spacer()
                if collapsed:
                    triangle = ui.Triangle(height=9, width=7)
                    triangle.alignment = ui.Alignment.RIGHT_CENTER
                else:
                    triangle = ui.Triangle(height=7, width=9)
                    triangle.alignment = ui.Alignment.CENTER_BOTTOM
                ui.Spacer()
            ui.Spacer(width=4)
            ui.Label(title, name="robot_header", width=0)
            ui.Spacer()
            if self._show_copy_button:
                with ui.VStack(width=0):
                    ui.Spacer(height=6)
                    ui.Image(
                        name="copy",
                        height=22,
                        width=22,
                        mouse_pressed_fn=lambda x, y, b, a: on_copy_to_clipboard(self._copy_content),
                    )

    def _create_frame(
        self, title: str, collapsed: bool, enabled: bool, visible: bool, build_fn: Callable
    ) -> ui.CollapsableFrame:
        frame = ui.CollapsableFrame(
            title=title,
            name=title,
            height=0,
            collapsed=collapsed,
            visible=visible,
            enabled=enabled,
            build_fn=build_fn,
            build_header_fn=self._build_header,
            style=get_style(),
            style_type_name_override="CollapsableFrame",
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        )

        return frame
