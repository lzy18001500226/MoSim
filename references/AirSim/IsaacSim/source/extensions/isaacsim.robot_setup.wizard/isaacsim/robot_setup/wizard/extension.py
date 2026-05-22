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
import weakref

import carb
import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtension

from .window import RobotWizardWindow

_robot_window_instance = None


def get_window():
    """Get IsaacSim robot window."""
    return _robot_window_instance if not _robot_window_instance else _robot_window_instance()


class WizardExtension(omni.ext.IExt, MenuHelperExtension):

    WINDOW_NAME = "Robot Wizard [Beta]"
    """Isaac Sim robot window name"""

    MENU_GROUP = "Window"
    """Isaac Sim robot menu group"""

    def __init__(self):
        """Initialize WizardExtension"""
        super().__init__()
        self._window = None

    def on_startup(self, ext_id):
        self.ext_id = ext_id

        ui.Workspace.set_show_window_fn(WizardExtension.WINDOW_NAME, self.show_window)
        # ui.Workspace.show_window(WizardExtension.WINDOW_NAME)

        self.menu_startup(WizardExtension.WINDOW_NAME, WizardExtension.WINDOW_NAME, WizardExtension.MENU_GROUP)

        self._launch_on_startup = carb.settings.get_settings().get_as_bool(
            "/persistent/exts/isaacsim.robot_setup.wizard/launch_on_startup"
        )
        self.show_window(self._launch_on_startup)

    def on_shutdown(self):
        """Shutdown function"""
        self.menu_shutdown()

        if self._window:
            self._window.destroy()
            self._window = None

    def show_window(self, value: bool):
        """Show/hide Isaac Sim robot window function

        Args:
            value (bool): True if window will be shown or False if window will be hidden.
        """
        global _robot_window_instance

        if value:
            if self._window is None:
                self._window = RobotWizardWindow(WizardExtension.WINDOW_NAME)
                self._window.set_visibility_changed_listener(self._visiblity_changed_fn)
                _robot_window_instance = weakref.ref(self._window)
            self._window.set_visible(value)

        elif self._window:
            self._window.set_visible(value)

    def _visiblity_changed_fn(self, visible):
        self.menu_refresh()
