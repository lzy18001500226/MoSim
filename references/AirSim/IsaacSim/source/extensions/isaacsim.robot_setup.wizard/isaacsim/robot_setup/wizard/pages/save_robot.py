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

import omni.ui as ui
import omni.usd
from pxr import Gf, Sdf, Usd

from ..builders.robot_templates import RobotRegistry
from ..builders.save_robot_helper import apply_articulation_apis, apply_robot_schema, create_variant_usd
from ..progress import ProgressColorState, ProgressRegistry
from ..utils.robot_asset_picker import RobotAssetPicker
from ..utils.ui_utils import ButtonWithIcon, custom_header, separator


class SaveRobot:
    def __init__(self, visible, *args, **kwargs):
        self.visible = visible
        self.frame = ui.Frame(visible=visible)
        self.frame.set_build_fn(self._build_frame)
        self._articulation_root_widget = None
        self._select_robot_asset_window = None

    def destroy(self):
        self.frame.destroy()
        if self._articulation_root_widget:
            self._articulation_root_widget.destroy()
        self._articulation_root_widget = None
        if self._select_robot_asset_window:
            self._select_robot_asset_window.destroy()
        self._select_robot_asset_window = None

    def _build_frame(self):
        with ui.CollapsableFrame("Save Robot", build_header_fn=custom_header):
            with ui.ScrollingFrame():
                with ui.VStack(name="setting_content_vstack"):

                    with ui.ZStack(height=0):
                        ui.Rectangle(name="save_stack")
                        with ui.VStack(spacing=2, name="margin_vstack"):
                            separator("Articulation Root")
                            ui.Spacer(height=4)
                            ui.Label(
                                "The Articulation Root defines the first link or joint in the articulation chain.",
                                name="sub_separator",
                                word_wrap=True,
                                height=0,
                            )
                            ui.Spacer(height=4)
                            with ui.HStack(height=0):
                                ui.Spacer(width=2)
                                self._articulation_root_widget = ui.StringField(width=300)
                                self._articulation_root_widget.model.set_value("Pick from the Robot")
                                ui.Spacer(width=2)
                                ui.Image(
                                    name="sample",
                                    width=24,
                                    mouse_pressed_fn=lambda x, y, b, a: self.select_robot_asset(),
                                )

                    with ui.ZStack(height=0):
                        ui.Rectangle(name="save_stack")
                        with ui.VStack(spacing=2, name="margin_vstack"):
                            separator("Minimal Environment")
                            ui.Spacer(height=4)
                            ui.Label(
                                "The minimal environment settings will be saved outside of the default robot prim, It is there to facilitate debugging and will not be loaded when adding the robot into other scenes by reference or payload.",
                                word_wrap=True,
                                height=0,
                                name="sub_separator",
                            )
                            ui.Spacer(height=10)
                            with ui.HStack(spacing=2):
                                ui.Label("Ground Plane", width=0, height=0, name="property")
                                ui.Spacer(width=2)
                                self._save_ground_check = ui.CheckBox(width=25, height=22)
                                self._save_ground_check.model.set_value(False)

                                ui.Spacer(width=10)
                                ui.Label("Default Light", width=0, height=0, name="property")
                                ui.Spacer(width=2)
                                self._save_light_check = ui.CheckBox(width=25, height=22)
                                self._save_light_check.model.set_value(False)

                                ui.Spacer(width=10)
                                ui.Label("Physics Scene", width=0, height=0, name="property")
                                ui.Spacer(width=2)
                                self._save_physics_scene_check = ui.CheckBox(width=25, height=22)
                                self._save_physics_scene_check.model.set_value(False)

                    with ui.ZStack(height=0):
                        ui.Rectangle(name="save_stack")

                        with ui.VStack(spacing=2, name="margin_vstack"):
                            separator("Save Robot")
                            ui.Spacer(height=4)
                            ui.Label(
                                "Once you are finished setting up your robot, you can save as a .usd file and use for training."
                                "If you make changes to the robot’s joints, drives or colliders, you will want to save your changes again",
                                word_wrap=True,
                                height=0,
                                name="sub_separator",
                            )
                            ui.Spacer(height=20)

                            ButtonWithIcon(
                                "Save Robot", name="save", image_width=18, height=44, clicked_fn=self.save_robot
                            )
                            ui.Spacer(height=10)

    def save_robot(self):
        ProgressRegistry().set_step_progress("Save Robot", ProgressColorState.COMPLETE)

        # save current layers
        robot = RobotRegistry().get()
        physics_filepath = f"{robot.name}_physics.usd"
        robot_schema_filepath = f"{robot.name}_robot.usd"
        config_dir = os.path.join(robot.robot_root_folder, "configurations")

        stage = omni.usd.get_context().get_stage()

        # set the default prim to the robot prim
        stage.SetDefaultPrim(stage.GetPrimAtPath(f"/{robot.name}"))

        # the current stage is the physics usd
        # base layer should already been saved during the hierarchy helper

        add_ground = self._save_ground_check.model.get_value_as_bool()
        add_lights = self._save_light_check.model.get_value_as_bool()
        add_physics_scene = self._save_physics_scene_check.model.get_value_as_bool()

        # set the articulation root
        robot_path = f"/{robot.name}"
        articulation_root_path = self._articulation_root_widget.model.get_value_as_string()
        apply_articulation_apis(robot_path=robot_path, articulation_root_path=articulation_root_path)
        omni.usd.get_context().save_as_stage(os.path.join(config_dir, physics_filepath))

        # create the robot schema

        # start a new layer for the robot schema
        stage = omni.usd.get_context().get_stage()
        stage.GetRootLayer().subLayerPaths.append(robot_schema_filepath)
        root_layer = stage.GetRootLayer()
        edit_target = stage.GetEditTargetForLocalLayer(root_layer)
        stage.SetEditTarget(edit_target)

        apply_robot_schema(robot_path)
        edit_target.GetLayer().Export(os.path.join(config_dir, robot_schema_filepath))

        # create the variant usd with the robot and physics
        create_variant_usd(add_ground, add_lights, add_physics_scene)
        omni.usd.get_context().save_as_stage(os.path.join(robot.robot_root_folder, f"{robot.name}.usd"))

    def set_visible(self, visible):
        if self.frame:
            self.frame.visible = visible

    def select(self, selected_paths):
        self._select_robot_asset_window.visible = False
        self._selected_paths = selected_paths
        if self._selected_paths:
            self._articulation_root_widget.model.set_value(self._selected_paths[0])
            self._articulation_root_widget.checked = True

    def select_robot_asset(self):
        if not self._select_robot_asset_window:
            stage = omni.usd.get_context().get_stage()
            self._select_robot_asset_window = RobotAssetPicker(
                "Select Robot Asset",
                stage,
                on_targets_selected=self.select,
                target_name="base of the robot",
            )
        self._select_robot_asset_window.visible = True
