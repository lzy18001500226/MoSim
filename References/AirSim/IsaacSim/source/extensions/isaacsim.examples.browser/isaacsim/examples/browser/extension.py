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

from .model import ExampleBrowserModel
from .window import ExampleBrowserWindow

_extension_instance = None
BROWSER_MENU_ROOT = "Window"
SETTING_ROOT = "/exts/isaacsim.examples.browser/"
SETTING_VISIBLE_AFTER_STARTUP = SETTING_ROOT + "visible_after_startup"


class ExampleBrowserExtension(omni.ext.IExt):
    @property
    def window(self) -> Optional[ExampleBrowserWindow]:
        return self._window

    @property
    def browser_widget(self) -> Optional[TreeFolderBrowserWidgetEx]:
        return self._window._widget

    def on_startup(self, ext_id):
        self._browser_model = ExampleBrowserModel()

        self._window = None
        ui.Workspace.set_show_window_fn(
            ExampleBrowserWindow.WINDOW_TITLE,
            self._show_window,  # pylint: disable=unnecessary-lambda
        )
        self._register_menuitem()

        visible = carb.settings.get_settings().get_as_bool(SETTING_VISIBLE_AFTER_STARTUP)
        if visible:
            self._show_window(True)

        global _extension_instance
        _extension_instance = self

    def on_shutdown(self):
        omni.kit.menu.utils.remove_menu_items(self._menu_entry, name=BROWSER_MENU_ROOT)
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_action("isaacsim.examples.browser", f"open_isaac_sim_examples_browser")

        self._browser_model.destroy()

        if self._window is not None:
            self._window.destroy()
            self._window = None

        global _extension_instance
        _extension_instance = None

    def register_example(self, **kwargs):
        """Register an example to the browser.

        Args:
            name: The name of the example to register.
            category: The category of the example to register.
        """
        if "name" not in kwargs:
            raise ValueError("Missing required parameter 'name' for register_example")
        if "category" not in kwargs:
            raise ValueError("Missing required parameter 'category' for register_example")
        self._browser_model.register_example(**kwargs)

    def deregister_example(self, **kwargs):
        """Deregister an example from the browser.

        Args:
            name: The name of the example to deregister.
            category: The category of the example to deregister.

        Raises:
            ValueError: If name or category parameters are missing.
            KeyError: If the category or example doesn't exist.
        """
        # Check if required parameters are provided
        if "name" not in kwargs:
            raise ValueError("Missing required parameter 'name' for deregister_example")
        if "category" not in kwargs:
            raise ValueError("Missing required parameter 'category' for deregister_example")

        name = kwargs["name"]
        category = kwargs["category"]

        # Check if the category exists
        if category not in self._browser_model._examples:
            raise KeyError(f"Category '{category}' does not exist")

        # Check if an example with the given name exists in the category
        examples_in_category = self._browser_model._examples[category]
        example_names = [example.example.name for example in examples_in_category]

        if name not in example_names:
            raise KeyError(f"Example '{name}' does not exist in category '{category}'")

        # If all validations pass, call the inner deregister_example function
        self._browser_model.deregister_example(**kwargs)

    def _show_window(self, visible) -> None:
        if visible:
            if self._window is None:
                self._window = ExampleBrowserWindow(self._browser_model, visible=True)
                self._window.set_visibility_changed_fn(self._on_visibility_changed)
            else:
                self._window.visible = True
        else:
            self._window.visible = False

    def _toggle_window(self):
        self._show_window(not self._is_visible())

    def _register_menuitem(self):
        ## register the menu action
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.register_action(
            "isaacsim.examples.browser",
            f"open_isaac_sim_examples_browser",
            lambda: self._show_window(True),
            description=f"Open Isaac Sim Examples Browser",
        )

        self._menu_entry = [
            omni.kit.menu.utils.MenuItemDescription(
                name="Examples",
                sub_menu=[
                    omni.kit.menu.utils.MenuItemDescription(
                        name="Robotics Examples",
                        ticked=True,
                        ticked_fn=self._is_visible,
                        onclick_fn=self._toggle_window,
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
