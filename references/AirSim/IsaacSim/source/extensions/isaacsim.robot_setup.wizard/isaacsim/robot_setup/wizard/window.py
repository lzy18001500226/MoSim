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
import asyncio

import carb
import omni.kit.actions
import omni.kit.app
import omni.ui as ui
from omni.ui import color as cl

from .builders.robot_templates import RobotRegistry
from .pages.add_colliders import AddColliders
from .pages.add_robot import AddRobot
from .pages.joints_and_drives import JointsandDrives
from .pages.prepare_files import PrepareFiles
from .pages.robot_hierarchy import RobotHierarchy
from .pages.save_robot import SaveRobot
from .progress import ProgressColorState, ProgressRegistry
from .splitter import Splitter
from .style import *
from .utils.ui_utils import create_combo_list_model


class RobotWizardWindow:
    def __init__(self, window_title):
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
        self._launch_on_startup = carb.settings.get_settings().get_as_bool(
            "/persistent/exts/isaacsim.robot_setup.wizard/launch_on_startup"
        )
        self._window_kwargs = {
            "title": window_title,
            "width": 400,
            "height": 600,
            "flags": window_flags,
            "dockPreference": ui.DockPreference.LEFT_BOTTOM,
            "visible": self._launch_on_startup,
        }
        self.window_title = window_title
        self._window = ui.Window(**self._window_kwargs)
        self._splitter = None
        self._window.frame.set_build_fn(self._rebuild_window)
        self._window.deferred_dock_in("Viewport", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.pages = {}
        self.steps = {}
        self._add_robot_page_name = "Add Robot"
        self._robot_hierarchy_page_name = "Robot Hierarchy"
        self._add_collider_page_name = "Add Colliders"
        self._add_joints_page_name = "Add Joints & Drivers"
        self._prepare_files_page_name = "Prepare Files"
        self._save_page_name = "Save Robot"
        self.pre_page_name = self._add_robot_page_name

        self.reset_progress()
        self.sub = ProgressRegistry().subscribe_progress_changed(self._change_style)

    def reset_progress(self):
        # progress steps, this should be changed to refect the data of the robot, to ProgressColorState.IN_PROGRESS or ProgressColorState.COMPLETE,
        self._progress = {
            self._add_robot_page_name: ProgressColorState.ACTIVE,
            self._prepare_files_page_name: ProgressColorState.REMAINING,
            self._robot_hierarchy_page_name: ProgressColorState.REMAINING,
            self._add_collider_page_name: ProgressColorState.REMAINING,
            self._add_joints_page_name: ProgressColorState.REMAINING,
            self._save_page_name: ProgressColorState.REMAINING,
        }
        ProgressRegistry().set_steps(self._progress)

    def destroy(self):
        """Destroy function. Class cleanup function"""
        self._visibility_changed_listener = None

        for p in self.pages.values():
            p.destroy()

        if self._window:
            self._window.destroy()
        self._window = None

    async def _dock_windows(self):
        viewport = ui.Workspace.get_window("Viewport")
        for _ in range(3):
            await omni.kit.app.get_app().next_update_async()
        if viewport:
            self._window.dock_in(viewport, ui.DockPosition.RIGHT)

    def set_visible(self, visible: bool):
        """Set window visibility state.

        Args:
            visible (bool): Visible state of the window.
        """
        if self._window:
            self._window.visible = visible
            if visible:
                asyncio.ensure_future(self._dock_windows())

    def _visibility_changed_fn(self, visible):
        if not visible:
            # schedule a rebuild of window frame. _rebuild_window won't be actually called until the window is visible again.
            self._window.frame.rebuild()

        if self._visibility_changed_listener:
            self._visibility_changed_listener(visible)

    def set_visibility_changed_listener(self, listener: callable):
        """Adds callback function for when window visibility is changed.

        Args:
            listener (callable): visibility changed callback.
        """
        self._visibility_changed_listener = listener

    def _on_help_button_clicked(self):
        """Opens an extension's documentation in a Web Browser"""
        import webbrowser

        doc_link = "https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/robot_wizard.html"
        try:
            webbrowser.open(doc_link, new=2)
        except Exception as e:
            carb.log_warn(f"Could not open browswer with url: {doc_link}, {e}")

    def _on_launch_on_startup_clicked(self, model):
        self._launch_on_startup = model.get_value_as_bool()
        carb.settings.get_settings().set_bool(
            "/persistent/exts/isaacsim.robot_setup.wizard/launch_on_startup", self._launch_on_startup
        )

    def _reset_wizard(self):
        RobotRegistry().reset()
        self.reset_progress()
        self._window.frame.rebuild()
        self.update_page("Add Robot")

    def __on_build_top(self):
        with ui.ZStack(height=56):
            ui.Rectangle(name="title_background")
            with ui.HStack(style={"HStack": {"margin_width": 10}}):
                ui.Label(self.window_title, width=0, name="title")
                ui.Spacer()
                with ui.VStack(width=28):
                    ui.Spacer(height=22)
                    launch_model = ui.SimpleBoolModel()
                    ui.CheckBox(model=launch_model, name="launch_on_startup")
                    launch_model.set_value(self._launch_on_startup)
                    launch_model.add_value_changed_fn(self._on_launch_on_startup_clicked)
                ui.Label("Launch on startup", name="launch_on_startup", width=130)
                with ui.VStack(width=30):
                    ui.Spacer()
                    ui.Image(
                        width=28,
                        height=28,
                        name="help",
                        mouse_pressed_fn=lambda x, y, b, a: self._on_help_button_clicked(),
                    )
                    ui.Spacer()
        reset_frame = ui.ZStack(height=46)
        with reset_frame:
            ui.Rectangle(name="title_background")
            with ui.HStack(style={"HStack": {"margin_width": 10}}):
                self._reset_button = ui.Button(
                    "Start Over",
                    visible=True,
                    clicked_fn=self._reset_wizard,
                    width=100,
                    name="start_over",
                )

        # def _configuring_robot_update(m, n):
        # rebuild the current page
        # current_active_page = ProgressRegistry().get_active_step()
        # print("current active step", current_active_page)
        # self.update_page(current_active_page)
        # self.pages[current_active_page].set_visible(True)

        # self.robot_picker_model.add_item_changed_fn(_configuring_robot_update)

    def on_build_steps(self):
        with ui.ScrollingFrame():
            with ui.ZStack():
                ui.Rectangle(name="step_background")
                with ui.VStack():
                    with ui.ZStack(height=34):
                        ui.Rectangle(name="title_background")
                        with ui.HStack(style={"HStack": {"margin_width": 10}}):
                            ui.Label("Wizard Steps", width=0, name="wizard_steps")
                            # ui.Spacer()
                            # with ui.VStack(width=28):
                            #     ui.Spacer()
                            #     ui.Image(
                            #         width=28,
                            #         height=28,
                            #         name="help",
                            #         mouse_pressed_fn=lambda x, y, b, a: self._on_help_button_clicked(),
                            #     )
                            #     ui.Spacer()
                    ui.Spacer(height=8)
                    self._build_steps()
                    ui.Spacer(height=25)
                    with ui.ZStack(height=34):
                        ui.Rectangle(name="title_background")
                        with ui.HStack(style={"HStack": {"margin_width": 10}}):
                            ui.Label("Additional Tools", width=0, name="wizard_steps")
                    ui.Spacer(height=5)
                    self._build_tools()

    def on_build_content(self):
        with ui.ZStack():
            self.pages[self._add_robot_page_name] = AddRobot(visible=True, window_title=self.window_title)
            self.pages[self._prepare_files_page_name] = PrepareFiles(visible=False)
            self.pages[self._robot_hierarchy_page_name] = RobotHierarchy(visible=False)
            self.pages[self._add_collider_page_name] = AddColliders(visible=False)
            self.pages[self._add_joints_page_name] = JointsandDrives(visible=False)
            self.pages[self._save_page_name] = SaveRobot(visible=False)

    def _rebuild_window(self):
        with ui.ScrollingFrame():
            with ui.VStack(style=get_style(), spacing=10):
                self.__on_build_top()
                self._splitter = Splitter(build_left_fn=self.on_build_steps, build_right_fn=self.on_build_content)

    def update_page(self, page_name):
        # set the current page to activea
        ProgressRegistry().set_step_progress(page_name, ProgressColorState.ACTIVE)
        try:
            self.pages[page_name].set_visible(True)
        except KeyError as e:
            print(e)

        if page_name != self.pre_page_name:
            if ProgressRegistry().get_progress_by_name(self.pre_page_name) == ProgressColorState.ACTIVE:
                ProgressRegistry().set_step_progress(self.pre_page_name, ProgressColorState.IN_PROGRESS)
            self.pages[self.pre_page_name].set_visible(False)
            if page_name in self.pages:
                self.pages[page_name].set_visible(True)
                self.pre_page_name = page_name

    def _add_step_item(self, step_name, step_num, use_img=False, click_fn=None):
        item_stack = ui.ZStack(height=47)
        with item_stack:
            ui.Rectangle(name="step_item_background")
            with ui.HStack():
                ui.Spacer(width=16)
                with ui.ZStack(width=36):
                    if use_img:
                        # ui.Image(name=step_name.lower().replace(" ", "_"))
                        ui.Image(name="generic_tool", image_url=f"{EXTENSION_FOLDER_PATH}/icons/icoGeneric.svg")
                    else:
                        with ui.VStack():
                            if step_num == 1:
                                ui.Spacer(height=20)
                            ui.Line(name="step_line", alignment=ui.Alignment.H_CENTER)
                            if step_num == 5:
                                ui.Spacer(height=20)
                        ui.Circle(
                            name="step_index",
                            radius=18,
                            mouse_pressed_fn=lambda x, y, m, b, step=step_name: self.update_page(step_name),
                        )
                        ui.Label(str(step_num), name="step_index", alignment=ui.Alignment.CENTER)
                ui.Spacer(width=10)
                tool_label = ui.Label(step_name, name="step_name", width=0)
                tool_label.set_mouse_pressed_fn(click_fn)

        return item_stack

    def _build_steps(self):
        with ui.VStack():
            i = 1
            for name, progress in self._progress.items():
                self.steps[name] = self._add_step_item(name, i)
                self._change_style(name, progress)
                i += 1

    def _build_tools(self):
        self._add_step_item("Joint Drive Gain Tuner", 2, use_img=True, click_fn=self._open_gain_tuner)
        self._add_step_item("Robot Assembler", 3, use_img=True, click_fn=self._open_robot_assembler)
        self._add_step_item("USD to URDF Exporter", 1, use_img=True, click_fn=self._open_usd_to_urdf_exporter)

    def _open_gain_tuner(self, *args, **kwargs):
        omni.kit.actions.core.get_action_registry().execute_action(
            "isaacsim.robot_setup.gain_tuner", "CreateUIExtension:Gain Tuner"
        )

    def _open_robot_assembler(self, *args, **kwargs):
        omni.kit.actions.core.get_action_registry().execute_action(
            "isaacsim.robot_setup.assembler", "CreateUIExtension:Robot Assembler"
        )

    def _open_usd_to_urdf_exporter(self, *args, **kwargs):
        # Open the USD to URDF exporter extension
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        extension_name = "isaacsim.asset.exporter.urdf"

        # Check if the extension is already enabled
        if not ext_manager.is_extension_enabled(extension_name):
            # Enable the extension if it's not already enabled
            ext_manager.set_extension_enabled_immediate(extension_name, True)

        # Execute the action to open the USD to URDF exporter UI
        omni.kit.actions.core.get_action_registry().execute_action("omni.kit.tool.asset_exporter", "file_export")

    def _change_style(self, name, state=ProgressColorState.REMAINING):
        if state == ProgressColorState.REMAINING:
            style = get_progress_none_style()
        elif state == ProgressColorState.IN_PROGRESS:
            style = get_progress_edit_style()
        elif state == ProgressColorState.COMPLETE:
            style = get_progress_complete_style()
        elif state == ProgressColorState.ACTIVE:
            style = get_progress_active_style()
        self.steps[name].style = style


class ProgressState(object):
    def __init__(self, name, handle, visible):
        self.step_name = name
        self.step_frame_handle = handle
        self.step_visible = visible
        self.completed = False

    def __repr__(self):
        return f"Progress Step: name:{self.step_name}, completed:{self.completed}, visibibility:{self.step_visible}"

    def set_frame_handle(self, frame_handle):
        self.step_frame_handle = frame_handle

    @property
    def completion(self) -> bool:
        return self.completed

    @completion.setter
    def completion(self, value: bool):
        self.completed = value
        # set the color of the circle to green if completed, gray if not

    @property
    def visibility(self) -> bool:
        return self.step_visible

    @visibility.setter
    def visibility(self, value: bool):
        self.step_visible = value
        self.step_frame_handle.visible = value
