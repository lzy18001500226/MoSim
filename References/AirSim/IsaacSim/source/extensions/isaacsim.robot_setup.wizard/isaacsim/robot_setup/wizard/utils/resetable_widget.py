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


class ResetButton:
    def __init__(self, init_value, on_reset_fn):
        self._init_value = init_value
        self._on_reset_fn = on_reset_fn
        self._enable = True
        self._build_ui()

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, enable):
        self._enable = enable
        self._reset_button.enabled = enable

    def refresh(self, new_value):
        self._reset_button.visible = bool(self._init_value != new_value)

    def _build_ui(self):
        with ui.VStack(width=0, height=0):
            ui.Spacer()
            with ui.ZStack(width=15, height=15):
                with ui.HStack(style={"margin_width": 0}):
                    ui.Spacer()
                    with ui.VStack(width=0):
                        ui.Spacer()
                        ui.Rectangle(width=5, height=5, name="reset_invalid")
                        ui.Spacer()
                    ui.Spacer()
                self._reset_button = ui.Rectangle(width=12, height=12, name="reset", tooltip="Click to reset value")
                self._reset_button.visible = False
            self._reset_button.set_mouse_pressed_fn(lambda x, y, m, w: self._restore_defaults())
            ui.Spacer()

    def _restore_defaults(self):
        if not self._enable:
            return
        self._reset_button.visible = False
        if self._on_reset_fn:
            self._on_reset_fn()


class ResetableField:
    def __init__(self, value_model, field_type, alignment=ui.Alignment.LEFT):
        self._value_model = value_model
        self._init_value = self.get_model_value(value_model)
        self._field_type = field_type
        self._alignment = alignment
        self._enable = True
        self._build_ui()

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, enable):
        self._enable = enable
        self._field.enabled = enable
        self._reset_button.enable = enable

    def get_model_value(self, model):
        if isinstance(model, ui.SimpleStringModel):
            return model.get_value_as_string()
        if isinstance(model, ui.SimpleIntModel):
            return model.get_value_as_int()
        if isinstance(model, ui.SimpleFloatModel):
            return model.get_value_as_float()
        return ""

    def _build_ui(self):
        with ui.HStack(height=22, spacing=10):
            with ui.ZStack():
                self._field = self._field_type(name="resetable", alignment=self._alignment)
            self._field.model.set_value(self._init_value)
            self._field.model.add_value_changed_fn(lambda m: self._update_value(m))
            with ui.VStack(width=8):
                ui.Spacer()
                self._reset_button = ResetButton(self._init_value, self._on_reset_fn)
                ui.Spacer()

    def _on_reset_fn(self):
        current_value = self.get_model_value(self._field.model)
        if current_value != self._init_value:
            self._field.model.set_value(self._init_value)
            self._value_model.set_value(self._init_value)

    def _update_value(self, model):
        new_value = self.get_model_value(model)
        self._value_model.set_value(new_value)
        self._reset_button.refresh(new_value)


class ResetableComboBox:
    def __init__(self, value_model, values, on_change):
        self._value_model = value_model
        self._init_value = value_model.get_value_as_string()
        self._values = values
        self._init_index = values.index(self._init_value)
        self._on_change = on_change
        self._build_ui()

    def _build_ui(self):
        with ui.HStack(height=22, spacing=10):
            self._box = ui.ComboBox(self._init_index, *self._values)
            self._box.model.add_item_changed_fn(lambda m, i: self._update_value(m, i))
            with ui.VStack(width=8):
                ui.Spacer()
                self._reset_button = ResetButton(self._init_index, self._on_reset_fn)
                ui.Spacer()

    def _on_reset_fn(self):
        if self._current_index != self._init_index:
            self._box.model.get_item_value_model().set_value(self._init_index)
            self._value_model.set_value(self._init_value)
        if self._on_change:
            self._on_change()

    def _update_value(self, model, item):
        root_model = model.get_item_value_model(item)
        index = root_model.get_value_as_int()
        self._current_index = index
        value_str = self._values[index]
        self._value_model.set_value(value_str)
        self._reset_button.refresh(index)
        if self._on_change:
            self._on_change()


class ResetableLabelField:
    def __init__(self, value_model, field_type, alignment=ui.Alignment.RIGHT):
        self._value_model = value_model
        self._init_value = self.get_model_value(value_model)
        self._field_type = field_type
        self._alignment = alignment
        self._enable = True
        self._build_ui()

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, enable):
        self._enable = enable
        self._field.enabled = enable
        self._reset_button.enable = enable
        self._rect.enabled = enable
        self._label.enabled = enable
        # self._label_degree.enabled = enable

    def get_model_value(self, model):
        if isinstance(model, ui.SimpleStringModel):
            return model.get_value_as_string()
        if isinstance(model, ui.SimpleIntModel):
            return model.get_value_as_int()
        if isinstance(model, ui.SimpleFloatModel):
            return model.get_value_as_float()
        return ""

    def _build_ui(self):
        with ui.HStack(height=22, spacing=10):
            with ui.ZStack():
                self._field = self._field_type(name="resetable", alignment=self._alignment)
                self._rect = ui.Rectangle(
                    name="reset_mask",
                )
                self._rect.set_mouse_pressed_fn(lambda x, y, b, m: self._begin_edit())
                with ui.HStack():
                    ui.Spacer()
                    self._label = ui.Label(
                        format(self._init_value, ".1f"), name="resetable", alignment=self._alignment, width=0
                    )
                    # ui.Spacer(width=3)
                    # self._label_degree = ui.Label("o", name="degree", alignment=ui.Alignment.RIGHT_TOP, width=0)
                    ui.Spacer(width=4)
            self._field.model.set_value(self._init_value)
            self._field.model.add_value_changed_fn(lambda m: self._update_value(m))
            self.subscription = self._field.model.subscribe_end_edit_fn(lambda m: self._end_edit(m))
            self._field.visible = False
            with ui.VStack(width=8):
                ui.Spacer()
                self._reset_button = ResetButton(self._init_value, self._on_reset_fn)
                ui.Spacer()

    def _on_reset_fn(self):
        current_value = self.get_model_value(self._field.model)
        if current_value != self._init_value:
            self._field.model.set_value(self._init_value)
            self._value_model.set_value(self._init_value)
            self._label.text = format(self._init_value, ".1f")

    def _update_value(self, model):
        new_value = self.get_model_value(model)
        self._label.text = format(new_value, ".1f")
        self._value_model.set_value(new_value)
        self._reset_button.refresh(new_value)

    def _end_edit(self, model):
        self._rect.visible = True
        self._label.visible = True
        # self._label_degree.visible = True
        self._field.visible = False

    def _begin_edit(self):
        if not self._enable:
            return
        self._rect.visible = False
        self._label.visible = False
        # self._label_degree.visible = False
        self._field.visible = True
