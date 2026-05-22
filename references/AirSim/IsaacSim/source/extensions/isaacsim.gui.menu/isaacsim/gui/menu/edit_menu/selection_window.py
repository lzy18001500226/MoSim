# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
"""This module provides a SelectionSetWindow class for creating a new selection set with a user-defined name through a UI window."""

__all__ = ["SelectionSetWindow"]

import omni.ui as ui


class SelectionSetWindow:
    """A window to input and create a new selection set name.

    This class provides a UI window that allows users to enter a name for a new selection set and create it using a callback function. The window includes a label, a text field, and 'Create' and 'Cancel' buttons.

    Args:
        callback (Callable[[str], None]): Function to call with the new selection set name."""

    def __init__(self, callback):
        """Initializes the SelectionSetWindow with a callback to be triggered upon creation."""
        self._callback = callback
        window = ui.Window(
            "Selection Set Name",
            width=300,
            height=110,
            flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_MODAL,
        )

        with window.frame:

            def on_create(widget):
                self._callback(widget.model.as_string)
                window.visible = False

            def on_cancel():
                window.visible = False

            with ui.VStack(
                height=0,
                spacing=5,
                name="top_level_stack",
                style={"VStack::top_level_stack": {"margin": 5}, "Button": {"margin": 0}},
            ):
                ui.Label("New selection set name:")
                widget = ui.StringField()
                ui.Spacer(width=5, height=5)
                with ui.HStack(spacing=5):
                    create_button = ui.Button("Create", enabled=False, clicked_fn=lambda w=widget: on_create(w))
                    ui.Button("Cancel", clicked_fn=on_cancel)

                def window_pressed_key(key_index, key_flags, key_down):
                    import carb.input

                    create_button.enabled = len(widget.model.as_string) > 0
                    key_mod = key_flags & ~ui.Widget.FLAG_WANT_CAPTURE_KEYBOARD
                    if (
                        create_button.enabled
                        and carb.input.KeyboardInput(key_index)
                        in [carb.input.KeyboardInput.ENTER, carb.input.KeyboardInput.NUMPAD_ENTER]
                        and key_mod == 0
                        and key_down
                    ):
                        on_create(widget)

                widget.focus_keyboard()
                window.set_key_pressed_fn(window_pressed_key)

        self._window = window
        self._widget = widget

    def shutdown(self):
        """Shuts down the SelectionSetWindow and cleans up resources."""
        self._callback = None
        del self._window

    def show(self):
        """Shows the SelectionSetWindow and resets the input field."""
        self._window.visible = True
        self._widget.model.set_value("")
        self._widget.focus_keyboard()
