# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

"""This module extends the Omniverse Kit editor with enhanced file operation capabilities, including handling recent files, saving and opening scenes, and managing USD stage events."""

__all__ = ["FileMenuDelegate", "FileMenuExtension"]

import os
import urllib.parse

import carb
import carb.input
import omni.client
import omni.kit.menu.utils
import omni.usd
from omni.kit.helper.file_utils import (
    FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT,
    asset_types,
    get_latest_urls_from_event_queue,
)
from omni.kit.menu.utils import IconMenuDelegate, LayoutSourceSearch, MenuItemDescription, MenuLayout
from omni.ui import color as cl

from .file_actions import deregister_actions, register_actions

_extension_instance = None
_extension_path = None
INTERACTIVE_TEXT = cl.shade(cl("#1A91C5"))


class FileMenuDelegate(IconMenuDelegate):
    """A delegate class for customizing the appearance and behavior of the File menu.

    This class provides methods to determine the length of displayed text in the menu, specifically
    for the 'Open Recent' menu, allowing for an ellipsis to be used on longer file paths."""

    # for recents menu
    def get_elided_length(self, menu_name):
        """Determines the maximum pixel width of text that can be displayed for a given menu.

        Args:
            menu_name (str): The name of the menu to check for text elision.

        Returns:
            int: The maximum pixel width of the text allowed in the menu or 0 if no limit."""

        if menu_name == "Open Recent":
            return 160
        return 0


class FileMenuExtension:
    """A class that extends the Omniverse Kit editor with file menu functionalities.

    This class provides enhanced file operation capabilities within the Omniverse Kit editor's file menu, including the ability to handle recent files, save and open scenes, and manage USD stage events. It is responsible for registering file actions, constructing the file menu, and updating the recent files list based on file events.
    """

    def __init__(self, ext_id=""):
        super().__init__()
        omni.kit.menu.utils.set_default_menu_priority("File", -10)
        self._ext_name = None
        self._max_recent_files = None
        self._file_delegate = None
        self._file_menu_list = None
        self._recent_menu_list = None
        self._event_sub = None
        self._stage_event_subscription = None
        self._stage_sub = None

        global _extension_instance
        _extension_instance = self

        global _extension_path
        _extension_path = omni.kit.app.get_app_interface().get_extension_manager().get_extension_path(ext_id)

        self._ext_name = "isaacsim.gui.menu.file_menu"
        register_actions(self._ext_name)

        settings = carb.settings.get_settings()
        self._max_recent_files = settings.get("exts/isaacsim.gui.menu/maxRecentFiles") or 10
        self._file_delegate = FileMenuDelegate()

        self._file_menu_list = None
        self._recent_menu_list = None
        self._build_file_menu()

        event_stream = carb.eventdispatcher.get_eventdispatcher()
        self._event_sub = event_stream.observe_event(
            event_name=FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT,
            on_event=self._build_recent_menu,
            observer_name="isaacsim.gui.menu file event watcher",
        )

        self._stage_event_subscription = event_stream.observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
            on_event=self._on_stage_event,
            observer_name="isaacsim.gui.menu stage watcher",
        )

        self.__menu_layout = [
            MenuLayout.Menu(
                "File",
                [
                    MenuLayout.Item(name="New", source="File/New"),
                    MenuLayout.Item(name="New From Stage Template", source="File/New From Stage Template"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(name="Open", source="File/Open"),
                    MenuLayout.Item(name="Open Recent", source="File/Open Recent"),
                    MenuLayout.Item(name="Re-open with New Edit Layer", source="File/Re-open with New Edit Layer"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(name="Save", source="File/Save"),
                    MenuLayout.Item(name="Save As...", source="File/Save As..."),
                    MenuLayout.Item(name="Save With Options", source="File/Save With Options"),
                    MenuLayout.Item(name="Save Flattened As...", source="File/Save Flattened As..."),
                    MenuLayout.Item(name="Collect and Save As...", source="File/Collect As..."),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(name="Import", source="File/Import"),
                    MenuLayout.Item(name="Import from Onshape", source="File/Import from Onshape"),
                    MenuLayout.Item(name="Import from ROS2 URDF Node", source="File/Import from ROS2 URDF Node"),
                    MenuLayout.Item(name="Export", source="File/Export"),
                    MenuLayout.Item(name="Export to URDF", source="File/URDF Exporter"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(name="Add Reference", source="File/Add Reference"),
                    MenuLayout.Item(name="Add Payload", source="File/Add Payload"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(name="Exit", source="File/Exit"),
                ],
            )
        ]

        omni.kit.menu.utils.add_layout(self.__menu_layout)

    def shutdown(self):
        global _extension_instance

        _extension_instance = None
        self._stage_sub = None
        omni.kit.menu.utils.remove_layout(self.__menu_layout)
        omni.kit.menu.utils.remove_menu_items(self._recent_menu_list, "File")
        omni.kit.menu.utils.remove_menu_items(self._file_menu_list, "File")
        deregister_actions(self._ext_name)
        self._recent_menu_list = None
        self._file_menu_list = None
        self._event_sub = None

    def _on_stage_event(self, event):
        self._build_file_menu()

    def _build_file_menu(self):
        # setup menu
        self._file_menu_list = [
            MenuItemDescription(
                name="New",
                onclick_action=("omni.kit.window.file", "new"),
                hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.N),
            ),
            MenuItemDescription(
                name="Open",
                onclick_action=("omni.kit.window.file", "open"),
                hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.O),
            ),
            MenuItemDescription(
                name="Re-open with New Edit Layer",
                # enable_fn=lambda: not FileMenuExtension.is_new_stage(),
                onclick_action=("isaacsim.gui.menu.file_menu", "open_stage_with_new_edit_layer"),
            ),
            MenuItemDescription(
                name="Save",
                # enable_fn=FileMenuExtension.can_close,
                onclick_action=("omni.kit.window.file", "save"),
                hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.S),
            ),
            MenuItemDescription(
                name="Save With Options",
                # enable_fn=FileMenuExtension.can_close,
                onclick_action=("omni.kit.window.file", "save_with_options"),
                hotkey=(
                    carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL | carb.input.KEYBOARD_MODIFIER_FLAG_ALT,
                    carb.input.KeyboardInput.S,
                ),
            ),
            MenuItemDescription(
                name="Save As...",
                # enable_fn=FileMenuExtension.can_close,
                onclick_action=("omni.kit.window.file", "save_as"),
                hotkey=(
                    carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL | carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT,
                    carb.input.KeyboardInput.S,
                ),
            ),
            MenuItemDescription(
                name="Save Flattened As...",
                enable_fn=FileMenuExtension.can_close,
                onclick_action=("omni.kit.window.file", "save_as_flattened"),
            ),
            MenuItemDescription(
                name="Add Reference",
                onclick_action=("omni.kit.window.file", "add_reference"),
            ),
            MenuItemDescription(name="Add Payload", onclick_action=("omni.kit.window.file", "add_payload")),
            MenuItemDescription(name="Exit", onclick_action=("isaacsim.gui.menu.file_menu", "quit")),
        ]
        if not carb.settings.get_settings().get("/app/fastShutdown"):
            self._file_menu_list.append(
                MenuItemDescription(
                    name="Exit Fast (Experimental)",
                    onclick_action=("isaacsim.gui.menu.file_menu", "quit_fast"),
                )
            )

        self._build_recent_menu()
        self._build_sample_menu()
        omni.kit.menu.utils.add_menu_items(self._file_menu_list, "File", -10, delegate=self._file_delegate)

    def _build_recent_menu(self, event: carb.events.IEvent = None):
        recent_files = get_latest_urls_from_event_queue(self._max_recent_files, asset_type=asset_types.ASSET_TYPE_USD)
        sub_menu = []
        # add reopen
        stage = omni.usd.get_context().get_stage()
        is_anonymous = stage.GetRootLayer().anonymous if stage else False
        filename_url = ""
        if not is_anonymous:
            filename_url = stage.GetRootLayer().identifier if stage else ""

        if filename_url:
            sub_menu.append(
                MenuItemDescription(
                    name=f"Current stage: {filename_url}",
                    onclick_action=("omni.kit.window.file", "reopen"),
                    user={"user_style": {"color": INTERACTIVE_TEXT}},
                )
            )
        elif not recent_files:
            sub_menu.append(MenuItemDescription(name="None", enabled=False))

        if recent_files:
            for recent_file in recent_files:
                # NOTE: not compatible with hotkeys as passing URL to open_stage
                sub_menu.append(
                    MenuItemDescription(
                        name=urllib.parse.unquote(recent_file),
                        onclick_action=("omni.kit.window.file", "open_stage", recent_file),
                    )
                )

        recent_menu_list = [MenuItemDescription(name="Open Recent", appear_after="Open", sub_menu=sub_menu)]

        if self._recent_menu_list:
            omni.kit.menu.utils.replace_menu_items(recent_menu_list, self._recent_menu_list, "File")
        else:
            omni.kit.menu.utils.add_menu_items(recent_menu_list, "File")

        self._recent_menu_list = recent_menu_list

    def _build_sample_menu(self):
        settings = carb.settings.get_settings()
        if settings.get("/exts/isaacsim.gui.menu/disableSampleMenu"):
            return

        samples = settings.get("/exts/isaacsim.gui.menu/sampleScenes")
        if not samples:
            return

        sub_menu = []
        token_interface = carb.tokens.get_tokens_interface()
        for sample in samples:
            sample_file = token_interface.resolve(sample)
            sample_name = os.path.basename(sample.replace("_", " "))
            sub_menu.append(
                MenuItemDescription(
                    name=urllib.parse.unquote(sample_name),
                    onclick_action=("omni.kit.window.file", "open_stage", sample_file),
                )
            )

        sample_menu_list = [MenuItemDescription(name="Samples", appear_after="Open Recent", sub_menu=sub_menu)]
        omni.kit.menu.utils.add_menu_items(sample_menu_list, "File")

    @staticmethod
    def is_new_stage():
        """Determines if the current USD stage is a new, unsaved stage.

        Returns:
            bool: True if the stage is new and unsaved, False otherwise."""
        return omni.usd.get_context().is_new_stage()

    @staticmethod
    def can_open():
        """Checks if the USD stage is in a state where it can be opened.

        Returns:
            bool: True if the stage can be opened, False otherwise."""
        stage_state = omni.usd.get_context().get_stage_state()
        return stage_state in [omni.usd.StageState.OPENED, omni.usd.StageState.CLOSED]

    @staticmethod
    def can_save():
        """Checks if the USD stage is in a state where it can be saved.

        Returns:
            bool: True if the stage can be saved, False otherwise."""
        return (
            omni.usd.get_context().get_stage_state() == omni.usd.StageState.OPENED
            and not FileMenuExtension.is_new_stage()
            and omni.usd.get_context().is_writable()
        )

    @staticmethod
    def can_close():
        """Checks if the USD stage is in a state where it can be closed.

        Returns:
            bool: True if the stage can be closed, False otherwise."""
        return omni.usd.get_context().get_stage_state() == omni.usd.StageState.OPENED

    @staticmethod
    def can_close_and_not_is_new_stage():
        """Checks if the USD stage can be closed and is not a new, unsaved stage.

        Returns:
            bool: True if the stage can be closed and is not new, False otherwise."""
        return FileMenuExtension.can_close() and not FileMenuExtension.is_new_stage()


def get_extension_path(sub_directory):
    """
    Returns the normalized path by joining the given sub-directory with the extension's base path.

    Args:
        sub_directory (str): The sub-directory to append to the base path of the extension. If empty, the base path is returned as is.

    Returns:
        str: The normalized path combining the extension's base path with the provided sub-directory.
    """
    path = _extension_path
    if sub_directory:
        path = os.path.normpath(os.path.join(path, sub_directory))
    return path
