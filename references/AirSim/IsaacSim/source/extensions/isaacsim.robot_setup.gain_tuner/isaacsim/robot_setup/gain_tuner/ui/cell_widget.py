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
import omni.ui as ui


class CellLabelField:
    def __init__(self, value_model, field_type, format, alignment=ui.Alignment.LEFT_CENTER):
        self._value_model = value_model
        self._init_value = format % (self.get_model_value(value_model))
        self._field_type = field_type
        self._alignment = alignment
        self._enable = True
        self._frame = ui.HStack(height=26, spacing=2)
        self._format = format
        self._build_ui()

    @property
    def enabled(self):
        return self._enable

    def update_default_value(self):
        self._init_value = self.get_model_value(self._value_model)

    @property
    def visible(self):
        return self._frame.visible

    @visible.setter
    def visible(self, value):
        self._frame.visible = value

    @enabled.setter
    def enabled(self, enable):
        self._enable = enable
        self._field.enabled = enable

    @property
    def field(self):
        return self._field

    def get_model_value(self, model):
        if isinstance(model, ui.SimpleStringModel):
            return model.get_value_as_string()
        if isinstance(model, ui.SimpleIntModel):
            return model.get_value_as_int()
        if isinstance(model, ui.SimpleFloatModel):
            return model.get_value_as_float()
        return ""

    def _build_ui(self):
        with self._frame:
            ui.Spacer(width=1)
            with ui.ZStack():
                with ui.VStack(height=0):
                    ui.Spacer(height=2)
                    self._field = self._field_type(
                        name="cell", style_type_name_override="Field", alignment=self._alignment, height=18
                    )
                    ui.Spacer(height=2)
            self._field.model.set_value(self._init_value)
            self._field.model.add_value_changed_fn(lambda m: self._update_value(m))
            # it used to bulk edit, we need the field hook with the value model' value
            self._value_model.add_value_changed_fn(lambda m: self._update_field(m))

    def _update_value(self, model):
        new_value = self.get_model_value(model)
        current_value = self.get_model_value(self._value_model)
        if new_value != current_value:
            self._value_model.set_value(new_value)

    def _update_field(self, model):
        new_value = self.get_model_value(model)
        current_value = self.get_model_value(self._field.model)
        if new_value != current_value:
            self._field.model.set_value(new_value)

    def _end_edit(self, model):
        pass

    def _begin_edit(self):
        if not self._enable:
            return


class CellColor:
    def __init__(self, colors):
        self._colors = colors
        self._selected = ui.SimpleBoolModel(False)
        self._selected.add_value_changed_fn(lambda m: self._update_value(m))
        self._frame = ui.HStack(height=26, width=26, spacing=0)
        self._build_ui()

    @property
    def selected(self):
        return self._selected.get_value_as_bool()

    @selected.setter
    def selected(self, value):
        self._selected.set_value(value)

    @property
    def visible(self):
        return self._frame.visible

    @visible.setter
    def visible(self, value):
        self._frame.visible = value

    def _build_ui(self):
        with self._frame:
            ui.Spacer(width=1)
            if self.selected:
                ui.Rectangle(
                    name="selected_color",
                    height=26,
                    width=8,
                    style={"background_color": self._colors[0], "border_radius": 0},
                )
                ui.Rectangle(
                    name="selected_color",
                    height=26,
                    width=8,
                    style={"background_color": self._colors[1], "border_radius": 0},
                )
                ui.Rectangle(
                    name="selected_color",
                    height=26,
                    width=8,
                    style={"background_color": self._colors[2], "border_radius": 0},
                )
            else:
                ui.Rectangle(
                    name="selected_color",
                    height=26,
                    width=24,
                    style={"background_color": self._colors[0], "border_radius": 0},
                )

    def _update_value(self, model):
        self._frame.clear()
        self._build_ui()
