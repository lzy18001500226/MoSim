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

import asyncio
import os

import omni.ext
import omni.ui as ui
from isaacsim.examples.browser import get_instance as get_browser_instance
from isaacsim.examples.interactive.base_sample.base_sample_extension_experimental import BaseSampleUITemplate
from isaacsim.examples.interactive.pick_place.pick_place_example import FrankaPickPlaceInteractive
from isaacsim.gui.components.ui_utils import btn_builder


class FrankaPickPlaceExtension(omni.ext.IExt):
    """Extension for simple pick-and-place interactive example."""

    def on_startup(self, ext_id: str):
        self.example_name = "Franka Pick Place"
        self.category = "Manipulation"

        ui_kwargs = {
            "ext_id": ext_id,
            "file_path": os.path.abspath(__file__),
            "title": "Simple Pick Place",
            # "doc_link": "https://docs.isaacsim.omniverse.nvidia.com/latest/core_api_tutorials/tutorial_core_adding_manipulator.html",
            "overview": "This sample demonstrates a flattened pick-and-place action sequence using Franka Robot.",
            "sample": FrankaPickPlaceInteractive(),
        }

        ui_handle = FrankaPickPlaceUI(**ui_kwargs)

        get_browser_instance().register_example(
            name=self.example_name,
            execute_entrypoint=ui_handle.build_window,
            ui_hook=ui_handle.build_ui,
            category=self.category,
        )

        return

    def on_shutdown(self):
        get_browser_instance().deregister_example(name=self.example_name, category=self.category)
        return


class FrankaPickPlaceUI(BaseSampleUITemplate):
    """UI for the simple pick-place interactive example."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_ui_elements = {}

    def build_extra_frames(self):
        """Build additional UI frames for task control."""
        extra_stacks = self.get_extra_frames_handle()

        with extra_stacks:
            with ui.CollapsableFrame(
                title="Task Control",
                width=ui.Fraction(0.33),
                height=0,
                visible=True,
                collapsed=False,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            ):
                self.build_task_controls_ui()

    def build_task_controls_ui(self):
        """Build the task control UI elements."""
        with ui.VStack(spacing=5):
            # Start Pick Place Button
            pick_place_dict = {
                "label": "Start Pick Place",
                "type": "button",
                "text": "Start Pick Place",
                "tooltip": "Execute the pick-and-place sequence",
                "on_clicked_fn": self._on_pick_place_button_event,
            }
            self.task_ui_elements["Start Pick Place"] = btn_builder(**pick_place_dict)

            # Status display
            with ui.HStack():
                ui.Label("Status:", width=60)
                self.task_ui_elements["Status"] = ui.Label("Ready", width=200)

            # Separator
            ui.Separator(height=5)

            # Information section
            with ui.CollapsableFrame(title="Information", collapsed=True):
                with ui.VStack(spacing=3):
                    ui.Label("This example demonstrates:", word_wrap=True)
                    ui.Label("• Simplified robot control", word_wrap=True)
                    ui.Label("• Direct pick-and-place actions", word_wrap=True)
                    ui.Label("• No complex layers or RL concepts", word_wrap=True)
                    ui.Label("• Easy to understand and modify", word_wrap=True)

            # Initially disable buttons
            self.task_ui_elements["Start Pick Place"].enabled = False

    def _on_pick_place_button_event(self):
        """Handle pick-place button click."""
        asyncio.ensure_future(self.sample.execute_pick_place_async())
        self.task_ui_elements["Start Pick Place"].enabled = False

    def _update_status(self, message: str):
        """Update the status label."""
        if "Status" in self.task_ui_elements:
            self.task_ui_elements["Status"].text = message
            print(f"Status: {message}")

    def post_reset_button_event(self):
        """Called after the reset button is pressed."""
        self.task_ui_elements["Start Pick Place"].enabled = True
        self._update_status("Ready")
        return

    def post_load_button_event(self):
        """Called after the load button is pressed."""
        self.task_ui_elements["Start Pick Place"].enabled = True
        self._update_status("Scene loaded - ready to start")
        return

    def post_clear_button_event(self):
        """Called after the clear button is pressed."""
        self.task_ui_elements["Start Pick Place"].enabled = False
        self._update_status("Scene cleared")
        return
