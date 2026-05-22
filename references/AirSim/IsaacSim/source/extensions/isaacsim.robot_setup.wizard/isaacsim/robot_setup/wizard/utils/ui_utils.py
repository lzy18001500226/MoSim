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
import os
from typing import Callable, List

import isaacsim.robot_setup.wizard
import omni.ui as ui
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.filepicker import FilePickerDialog

from ..progress import ProgressColorState, ProgressRegistry
from .utils import Singleton


def custom_header(collapsed, title):
    with ui.HStack(height=30):
        ui.Spacer(width=8)
        with ui.VStack(width=13):
            ui.Spacer()
            triangle = ui.Triangle(height=12)
            if collapsed:
                triangle.alignment = ui.Alignment.RIGHT_CENTER
            else:
                triangle.alignment = ui.Alignment.CENTER_BOTTOM
            ui.Spacer()
        ui.Spacer(width=10)
        ui.Label(title, name="separator", width=0)
        ui.Spacer()
        # with ui.ZStack(content_clipping=True, width=38):
        #     ui.Image(name="help", width=28, height=28, mouse_pressed_fn=lambda x, y, b, a: print("Help button clicked"))


def info_header(collapsed, title):
    with ui.HStack(height=20):
        with ui.VStack(width=10):
            ui.Spacer()
            triangle = ui.Triangle(height=8)
            if collapsed:
                triangle.alignment = ui.Alignment.RIGHT_CENTER
            else:
                triangle.alignment = ui.Alignment.CENTER_BOTTOM
            ui.Spacer()
        ui.Spacer(width=10)
        ui.Label(title, name="collapsable_header", width=0)
        ui.Spacer()
        with ui.ZStack(content_clipping=True, width=20):
            ui.Image(name="info", width=20, height=20)


def separator(text):
    with ui.HStack(height=16, spacing=10):
        ui.Label(text, name="separator", width=0)
        ui.Line()


def info_frame(infos, collapse_fn):
    with ui.CollapsableFrame(
        "Info", name="info", height=0, collapsed=True, build_header_fn=info_header, collapsed_changed_fn=collapse_fn
    ):
        with ui.HStack():
            ui.Spacer(width=40)
            with ui.VStack(spacing=5):
                for info in infos:
                    with ui.HStack(height=15, spacing=10):
                        ui.Circle(name="dot", width=3)
                        ui.Label(info, height=0, width=0)


class ComboListItem(ui.AbstractItem):
    def __init__(self, item):
        """
        item is a string
        """
        super().__init__()
        self.model = ui.SimpleStringModel(item)
        self.item = item


class ComboListModel(ui.AbstractItemModel):
    def __init__(self, item_list, default_index):
        super().__init__()
        self._default_index = default_index
        self._current_index = ui.SimpleIntModel(default_index)
        self._current_index.add_value_changed_fn(self.selection_changed)
        self._item_list = item_list
        self._items = []
        if item_list:
            for item in item_list:
                self._items.append(ComboListItem(item))

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index
        return item.model

    def get_current_index(self):
        return self._current_index.get_value_as_int()

    def set_current_index(self, index):
        self._current_index.set_value(index)

    def get_current_string(self):
        return self._items[self._current_index.get_value_as_int()].model.get_value_as_string()

    def set_current_string(self, string):
        for index, item in enumerate(self._items):
            if item.model.get_value_as_string() == string:
                self.set_current_index(index)
                break

    def get_current_item(self):
        return self._items[self._current_index.get_value_as_int()].item

    def is_default(self):
        return self.get_current_index() == self._default_index

    def add_item(self, item):
        self._items.append(ComboListItem(item))
        self._item_changed(None)

    def selection_changed(self, index):
        #     """
        #     reset progress, parse progress on each page, and turn the ones that are updated to inprogress.

        #     """
        self._item_changed(None)
        # print("selection changed to ", self.get_current_item().name)
        # call the __parse_robot_param function in every single page, and update progress accordingly

    def has_item(self):
        return len(self._items) > 0


def create_combo_list_model(items_list, index):
    return ComboListModel(items_list, index)


def next_step(curret_step_name, next_step_name, verify_fn=None):
    """
    verify_fn: function to verify the current step before moving to the next step
    """

    if verify_fn and callable(verify_fn):
        verify_fn()

    ProgressRegistry().set_step_progress(curret_step_name, ProgressColorState.COMPLETE)
    isaacsim.robot_setup.wizard.get_window().update_page(next_step_name)


def text_with_dot(text):
    with ui.HStack(height=15, spacing=10):
        ui.Circle(name="dot", width=4)
        ui.Label(text, height=0)


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


class FileSorter:
    # Define the valid extensions for each type
    SIM_READY_EXTENSIONS = {".urdf", ".xml"}
    MODEL_EXTENSIONS = {".usd", ".obj", ".stl", ".dae", ".fbx", ".usda"}

    # Define named parameters for the return values
    SIM_READY = 1
    MODEL = 2
    INVALID = 0

    @staticmethod
    def get_file_extension(filepath):
        """Extract the file extension from the filepath."""
        _, extension = os.path.splitext(filepath)
        return extension.lower()  # Return in lowercase to avoid case-sensitivity issues

    @staticmethod
    def classify_file(filepath):
        """Classify the file and return a numeric value with named parameters."""
        extension = FileSorter.get_file_extension(filepath)

        if extension in FileSorter.SIM_READY_EXTENSIONS:
            return FileSorter.SIM_READY
        elif extension in FileSorter.MODEL_EXTENSIONS:
            return FileSorter.MODEL
        else:
            return FileSorter.INVALID

    @staticmethod
    def is_sim_ready(filepath):
        """Return True if the file is 'sim-ready', otherwise False."""
        return FileSorter.classify_file(filepath) == FileSorter.SIM_READY

    @staticmethod
    def is_3d_model(filepath):
        """Return True if the file is a '3D model', otherwise False."""
        return FileSorter.classify_file(filepath) == FileSorter.MODEL

    @staticmethod
    def is_valid(filepath):
        """Return True if the file is either 'sim-ready' or a '3D model', otherwise False."""
        classification = FileSorter.classify_file(filepath)
        return classification == FileSorter.SIM_READY or classification == FileSorter.MODEL


def open_extension(ext_name, action_id=None):
    """
    Open the extension with the given name
    """
    import omni.kit.app

    ext_manager = omni.kit.app.get_app().get_extension_manager()
    extension_enabled = ext_manager.is_extension_enabled(ext_name)
    if not extension_enabled:
        result = ext_manager.set_extension_enabled_immediate(ext_name, True)

    action_registry = omni.kit.actions.core.get_action_registry()
    ext_id = ext_manager.get_extension_id_by_module(ext_name)
    if action_id is None:
        action_id = f'{ext_id.replace(" ", "_")}{ext_name.replace(" ", "_")}'
    action_registry.execute_action(ext_id, action_id)


@Singleton
class FilteredFileDialog:
    def __init__(self, formats: List[str], handler: Callable):
        self.formats = formats
        self.handler = handler
        self._filepicker = None
        self._initialize_filepicker()

    def _on_filter_files(self, item: FileBrowserItem) -> bool:
        """Callback to filter the choices of file names in the open or save dialog"""
        if not item or item.is_folder:
            return True
        # Show only files with listed extensions
        return os.path.splitext(item.path)[1].lower() in self.formats

    def _initialize_filepicker(self):
        self._filepicker = FilePickerDialog(
            "Select File",
            allow_multi_selection=False,
            apply_button_label="Open",
            click_apply_handler=self.handler,
            item_filter_options=[f"*{ext.lower()}" for ext in self.formats],
            item_filter_fn=self._on_filter_files,
        )
        self._filepicker.hide()

    def __call__(self, formats: List[str], handler: Callable):
        self.formats = formats
        self.handler = handler
        self._initialize_filepicker()

    def open_dialog(self):
        self._filepicker.show()

    def close_dialog(self):
        self._filepicker.hide()


def open_folder_picker(on_click_fn):
    def on_selected(filename, path):
        on_click_fn(filename, path)
        file_picker.hide()

    def on_canceled(a, b):
        file_picker.hide()

    file_picker = FilePickerDialog(
        "Select Output Folder",
        allow_multi_selection=False,
        apply_button_label="Select Folder",
        click_apply_handler=lambda a, b: on_selected(a, b),
        click_cancel_handler=lambda a, b: on_canceled(a, b),
    )
