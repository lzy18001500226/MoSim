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
from typing import Callable, List, Optional, Tuple, Union

import omni.kit.actions.core
import omni.ui as ui
from isaacsim.gui.components.element_wrappers import CheckBox, DropDown, Frame
from isaacsim.gui.components.widgets import DynamicComboBoxModel

LABEL_WIDTH = 160


class CheckBoxWithNoReset(CheckBox):
    def _create_ui_widget(self, label: str, default_value: bool, tooltip: str):
        containing_frame = Frame().frame
        with containing_frame:
            with ui.HStack():
                self._label = ui.Label(label, width=LABEL_WIDTH, alignment=ui.Alignment.LEFT_CENTER)
                model = ui.SimpleBoolModel()
                model.set_value(default_value)
                self._checkbox = ui.CheckBox(model=model, tooltip=tooltip)
                model.add_value_changed_fn(self._on_click_fn_wrapper)

        return containing_frame


class DropDownWithPicker(DropDown):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection_fn = kwargs.get("on_selection_fn", None)

    def _create_ui_widget(self, label, tooltip):
        items = []
        combobox_model = DynamicComboBoxModel(items)
        containing_frame = Frame().frame
        with containing_frame:
            with ui.HStack():
                self._label = ui.Label(
                    label, name="dropdown_label", width=LABEL_WIDTH, alignment=ui.Alignment.LEFT_CENTER, tooltip=tooltip
                )
                with ui.HStack():
                    self._picker = ui.Image(
                        name="picker",
                        width=18,
                        height=18,
                        tooltip="Click to show import dialog",
                        mouse_pressed_fn=lambda x, y, b, a: self._on_pressed_fn(b),
                    )
                    ui.Spacer(width=3)
                    self._combobox = ui.ComboBox(combobox_model)

        return containing_frame

    def _on_pressed_fn(self, b):
        if b != 0:
            return
        if self.selection_fn is not None:
            print("Selection fn")
            self.selection_fn(b)


class DropDownWithSelect(DropDown):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._articulation_path_to = None
        self.selection_fn = kwargs.get("on_selection_fn", None)
        self.populate_fn = kwargs.get("populate_fn", None)

    @property
    def articulation_path_to(self):
        return self._articulation_path_to

    @articulation_path_to.setter
    def articulation_path_to(self, path):
        self._articulation_path_to = path

    def _create_ui_widget(self, label, tooltip):
        items = []
        combobox_model = DynamicComboBoxModel(items)
        containing_frame = Frame().frame
        with containing_frame:
            with ui.HStack():
                self._label = ui.Label(
                    label, name="dropdown_label", width=LABEL_WIDTH, alignment=ui.Alignment.LEFT_CENTER, tooltip=tooltip
                )
                with ui.HStack(width=ui.Fraction(1)):
                    self._combobox = ui.ComboBox(combobox_model)
                    ui.Spacer(width=3)
                    self._select = ui.Image(
                        name="select",
                        width=18,
                        height=18,
                        tooltip="Click to select prim in viewport",
                        mouse_pressed_fn=lambda x, y, b, a: self._on_pressed_fn(b),
                    )

        return containing_frame

    def _on_pressed_fn(self, b):
        if b != 0:
            return
        if self.selection_fn is not None:
            print("Selection fn")
            self.selection_fn(b)


def help_frame_header(collapsed, title):
    with ui.HStack(height=22):
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
        ui.Label(title, name="collapsable_header", width=0)
        ui.Spacer()
        ui.Image(name="help", width=20, height=20, tooltip="Click to see help documentation")


class ButtonWithIcon:
    def __init__(self, text="", image_width=14, *args, **kwargs):
        with ui.ZStack(*args, **kwargs):
            self.button = ui.InvisibleButton(*args, **kwargs)
            self.rect = ui.Rectangle(style_type_name_override="Button.Rect", *args, **kwargs)
            with ui.HStack(spacing=8):
                ui.Spacer()
                if image_width > 0:
                    self.image = ui.Image(width=image_width, style_type_name_override=f"Button.Image", *args, **kwargs)
                self.label = ui.Label(text, width=0, style_type_name_override=f"Button.Label", *args, **kwargs)
                ui.Spacer()

    @property
    def enabled(self):
        return self.button.enabled

    @enabled.setter
    def enabled(self, value):
        self.button.enabled = value
        self.rect.enabled = value
        self.image.enabled = value
        self.label.enabled = value

    def set_clicked_fn(self, fn):
        self.button.set_clicked_fn(fn)
