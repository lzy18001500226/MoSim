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
from functools import partial

import carb
import omni.ui as ui
import omni.usd
from omni.kit.widget.filter import FilterButton
from omni.kit.widget.options_button import OptionsButton
from omni.kit.widget.options_menu import OptionItem
from omni.kit.widget.searchfield import SearchField
from omni.usd import Sdf
from pxr import UsdGeom

from ..builders.joint_helper import (
    AXIS_LIST,
    DRIVE_TYPES,
    JOINT_TYPES,
    apply_drive_settings,
    apply_joint_apis,
    apply_joint_settings,
    define_joints,
    get_all_settings,
)
from ..builders.robot_templates import RobotRegistry
from ..style import get_popup_window_style
from ..utils.resetable_widget import ResetableComboBox, ResetableField, ResetableLabelField
from ..utils.robot_asset_picker import RobotAssetPicker
from ..utils.treeview_delegate import (
    SearchableItem,
    TreeViewIDColumn,
    TreeViewWithPlacerHolderDelegate,
    TreeViewWithPlacerHolderModel,
)
from ..utils.ui_utils import ButtonWithIcon, custom_header, info_frame, next_step, separator


class JointItem(SearchableItem):
    def __init__(
        self, name, joint_type, axis, drive_type="None", parent="body0", child="body1", editable=True, **kwargs
    ):
        super().__init__()
        self.name = ui.SimpleStringModel(name)
        self.joint_type = ui.SimpleStringModel(joint_type)  # Joint Type: prismatic, revolute, spherical, fixed, d6
        self.axis = ui.SimpleStringModel(axis)
        self.parent = ui.SimpleStringModel(parent)
        self.child = ui.SimpleStringModel(child)
        self.editable = ui.SimpleBoolModel(editable)

        # TODO: joint setting, should wrap it into a joint setting class?
        self.drive_type = ui.SimpleStringModel(drive_type)  # Drive TYPES: acceleration, force
        self.break_force = ui.SimpleFloatModel(float(kwargs.get("break_force", 1e6)))
        self.break_torque = ui.SimpleFloatModel(float(kwargs.get("break_torque", 1e6)))
        self.lower_limit = ui.SimpleFloatModel(float(kwargs.get("lower_limit", -360)))
        self.upper_limit = ui.SimpleFloatModel(float(kwargs.get("upper_limit", 360)))

        # TODO: drive setting, should wrap it into a drive setting class?
        self.max_force = ui.SimpleFloatModel(float(kwargs.get("max_force", 1e9)))
        self.target_position = ui.SimpleFloatModel(float(kwargs.get("target_position", 0.0)))
        self.target_velocity = ui.SimpleFloatModel(float(kwargs.get("target_velocity", 0.0)))
        self.damping = ui.SimpleFloatModel(float(kwargs.get("damping", 1e3)))
        self.stiffness = ui.SimpleFloatModel(float(kwargs.get("stiffness", 1e4)))
        self.text = " ".join((name, joint_type, axis, drive_type))

    def refresh_text(self):
        # TODO: should refresh text when item edited, so should add some on_item_changed callback in build function
        self.text = " ".join(
            (
                self.name.get_value_as_string(),
                self.joint_type.get_value_as_string(),
                self.axis.get_value_as_string(),
                self.drive_type.get_value_as_string(),
                self.parent.get_value_as_string(),
                self.child.get_value_as_string(),
            )
        )

    def set_property(self, property_name, value):
        """
        Sets the value of a specified property and refreshes the display text.

        Args:
            property_name (str): The name of the property to set (e.g., 'name', 'parent', 'child', 'axis', 'type', 'drive').
            value: The value to set for the property.
        """
        if hasattr(self, property_name):
            getattr(self, property_name).set_value(value)
            self.refresh_text()


class JointsModel(TreeViewWithPlacerHolderModel):  # the model for the tree view
    def __init__(self, items):
        super().__init__(items)
        self._edit_window = None

    def destroy(self):
        if self._edit_window:
            self._edit_window.destroy()
        self._edit_window = None

        super().destroy()

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel for the first column
        and SimpleFloatModel for the second column.
        """
        if isinstance(item, JointItem):
            if column_id == 1:
                return item.name
            elif column_id == 2:
                return item.joint_type
            elif column_id == 3:
                return item.axis
            elif column_id == 4:
                return item.drive_type
            elif column_id == 5:
                return item.parent
            elif column_id == 6:
                return item.child

    def edit_item(self, item):
        # This item is not necessarily the tree view selection.
        if not self._edit_window:
            self._edit_window = CreateJointWindow("Edit Joint", self, item)
        elif item:
            self._edit_window._window.visible = True
            self._edit_window._update_ui(item)


class JointsandDrives:
    """Frame for the `Add Joints & Drivers` page"""

    def __init__(self, visible, *args, **kwargs):
        self.visible = visible
        self._tree_view = None
        self._treeview_empty_page = None
        self._create_joint_window = None
        self._joint_settings_stack = None
        self._drive_settings_stack = None
        self.__subscription = None
        self._joint_model = None
        self._next_step_button = None
        self._treeview_initial_height = 200
        self.frame = ui.Frame(visible=visible)
        self.frame.set_build_fn(self._build_frame)
        self._previous_joint_item = None

    def destroy(self):
        self.__subscription = None
        if self._joint_model:
            self._joint_model.destroy()
        self._joint_model = None
        if self._create_joint_window:
            self._create_joint_window.destroy()
        self._create_joint_window = None
        if self._tree_view:
            self._tree_view.destroy()
        self._tree_view = None
        self._treeview_empty_page = None
        if self._joint_settings_stack:
            self._joint_settings_stack.destroy()
        self._joint_settings_stack = None
        if self._drive_settings_stack:
            self._drive_settings_stack.destroy()
        self._drive_settings_stack = None
        self._previous_joint_item = None

    def _build_frame(self):
        with ui.ScrollingFrame():
            with ui.CollapsableFrame("Joints and Drives", build_header_fn=custom_header):
                with ui.ScrollingFrame():
                    with ui.VStack():
                        with ui.VStack(spacing=2, name="margin_vstack"):
                            separator("Create Joint")
                            ui.Spacer(height=4)
                            ui.Label(
                                "Joints are used as articulation points betwwen two parts",
                                name="sub_separator",
                                height=0,
                                word_wrap=True,
                            )
                            ui.Spacer(height=20)
                            self._invalid_joint_name_label = ui.Label(
                                "Invalid Joint Name", visible=False, style={"color": "red"}
                            )
                            with ui.ZStack(height=0):
                                ui.Rectangle(name="treeview")
                                with ui.HStack():
                                    ui.Spacer(width=2)
                                    with ui.VStack():
                                        ui.Spacer(height=4)
                                        with ui.HStack(spacing=4, height=0):
                                            # Search field
                                            self._search = SearchField(on_search_fn=self._filter_by_text)
                                            # Filter button
                                            self._filter_button = FilterButton([], width=20)
                                        ui.Spacer(height=4)
                                        self._build_tree_view()
                                        ui.Spacer(height=4)
                                    ui.Spacer(width=2)

                            ButtonWithIcon(
                                "Create New Joint", name="add", height=44, clicked_fn=self.create_joint_window
                            )

                        with ui.VStack(spacing=20, name="setting_margin_vstack"):
                            self.joint_settings()
                            self.drive_settings()

                        with ui.VStack(spacing=2, name="margin_vstack"):
                            ui.Spacer(height=10)
                            separator("Next: Save Robot")
                            ui.Spacer(height=12)
                            self._next_step_button = ButtonWithIcon(
                                "Save Robot",
                                name="next",
                                clicked_fn=lambda: next_step(
                                    "Add Joints & Drivers", "Save Robot", self.add_joint_to_robot
                                ),
                                height=44,
                                enabled=False,
                            )

    def joint_settings(self):
        self._joint_settings_stack = ui.ZStack(visible=bool(self._tree_view.selection))
        if not self._tree_view.selection:
            return
        self.build_joint_settings_content(self._tree_view.selection[0])

    def build_joint_settings_content(self, current_item):
        self._joint_settings_stack.clear()
        with self._joint_settings_stack:
            ui.Rectangle(name="save_stack")
            with ui.VStack(spacing=8, name="setting_content_vstack"):
                separator("Joint Settings")
                ui.Spacer(height=6)
                with ui.HStack(height=22):
                    ui.Label("Parent Xform", name="property")
                    ui.Label("Child Xform", name="property")
                with ui.HStack(height=22):
                    self._parent_field = ui.StringField(name="resetable")
                    self._parent_field.model.set_value(current_item.parent.get_value_as_string())
                    self._parent_field.model.add_value_changed_fn(
                        lambda m: self._update_xform(current_item, current_item.parent, m)
                    )
                    ui.Spacer(width=30)
                    self._child_field = ui.StringField(name="resetable")
                    self._child_field.model.set_value(current_item.child.get_value_as_string())
                    self._child_field.model.add_value_changed_fn(
                        lambda m: self._update_xform(current_item, current_item.child, m)
                    )
                    ui.Spacer(width=30)
                ui.Spacer(height=4)
                with ui.HStack(height=22):
                    self._break_able_check = ui.CheckBox(width=25, height=22)
                    self._break_able_check.model.set_value(True)
                    self._break_able_check.model.add_value_changed_fn(
                        lambda m: self._set_joint_breakable(m.get_value_as_bool())
                    )
                    ui.Label("Joint is Breakable", width=0, height=0, name="property")
                with ui.HStack(height=0):
                    ui.Label("Break Force", name="property")
                    ui.Label("  Break Torque", name="property")
                with ui.HStack(height=22, spacing=10):
                    self._break_force_field = ResetableField(current_item.break_force, ui.FloatField)
                    self._break_torque_field = ResetableField(current_item.break_torque, ui.FloatField)
                ui.Spacer(height=4)
                with ui.HStack(height=30):
                    self._joint_limit_check = ui.CheckBox(width=25, height=22)
                    self._joint_limit_check.model.set_value(True)
                    self._joint_limit_check.model.add_value_changed_fn(
                        lambda m: self._set_joint_limit(m.get_value_as_bool())
                    )
                    ui.Label("Joint Range is Limited", width=0, height=0, name="property")
                with ui.HStack(height=0):
                    ui.Label("Lower Limit", name="property")
                    ui.Label("  Upper Limit", name="property")
                with ui.HStack(height=22, spacing=10):
                    self._lower_limit_field = ResetableLabelField(
                        current_item.lower_limit, ui.FloatField, alignment=ui.Alignment.RIGHT
                    )
                    self._upper_limit_field = ResetableLabelField(
                        current_item.upper_limit, ui.FloatField, alignment=ui.Alignment.RIGHT
                    )

    def _update_xform(self, current_item, value_model, model):
        new_value = model.get_value_as_string()
        value_model.set_value(new_value)
        self._joint_model._item_changed(current_item)

    def _set_joint_breakable(self, enable):
        if not enable:
            self._break_force_field._value_model.set_value(float("inf"))
            self._break_torque_field._value_model.set_value(float("inf"))
        self._break_force_field.enable = enable
        self._break_torque_field.enable = enable

    def _set_joint_limit(self, enable):
        if not enable:
            self._lower_limit_field._value_model.set_value(float("-inf"))
            self._upper_limit_field._value_model.set_value(float("inf"))
        self._lower_limit_field.enable = enable
        self._upper_limit_field.enable = enable

    def drive_settings(self):
        self._drive_settings_stack = ui.ZStack(visible=bool(self._tree_view.selection))
        if not self._tree_view.selection:
            return
        self.build_drive_settings_content(self._tree_view.selection[0])

    def build_drive_settings_content(self, current_item):
        self._drive_settings_stack.clear()
        with self._drive_settings_stack:
            ui.Rectangle(name="save_stack")
            with ui.VStack(spacing=8, name="setting_content_vstack"):
                separator("Drive Settings")
                ui.Spacer(height=6)
                with ui.HStack(height=0):
                    ui.Label("Type", name="property")
                    ui.Label("  Max Force", name="property")
                with ui.HStack(height=30, spacing=10):
                    self._drive_type_widget = ResetableComboBox(
                        current_item.drive_type, DRIVE_TYPES, partial(self._joint_model._item_changed, current_item)
                    )
                    ResetableField(current_item.max_force, ui.FloatField)
                with ui.HStack(height=0):
                    ui.Label("Target Position", name="property")
                    ui.Label("  Target Velocity", name="property")
                with ui.HStack(height=30, spacing=10):
                    ResetableField(current_item.target_position, ui.FloatField)
                    ResetableField(current_item.target_velocity, ui.FloatField)
                with ui.HStack(height=0):
                    ui.Label("Damping", name="property")
                    ui.Label("  Stiffness", name="property")
                with ui.HStack(height=30, spacing=10):
                    ResetableField(current_item.damping, ui.FloatField)
                    ResetableField(current_item.stiffness, ui.FloatField)

    def rebuild_settings(self, item):
        self.build_joint_settings_content(item)
        self.build_drive_settings_content(item)

    def _create_joint(self, current_item):
        """
        create joints and apply settings to the robot
        """
        robot = RobotRegistry().get()
        stage = omni.usd.get_context().get_stage()
        robot_name = robot.name
        if not robot or not stage:
            return

        # apply the settings to the selected joint
        joint_name = current_item.name.get_value_as_string()
        joint_type = current_item.joint_type.get_value_as_string()
        axis = current_item.axis.get_value_as_string()
        parent = current_item.parent.get_value_as_string()
        child = current_item.child.get_value_as_string()

        break_force = current_item.break_force.get_value_as_float()
        break_torque = current_item.break_torque.get_value_as_float()
        lower_limit = current_item.lower_limit.get_value_as_float()
        upper_limit = current_item.upper_limit.get_value_as_float()

        drive_type = current_item.drive_type.get_value_as_string()
        max_force = current_item.max_force.get_value_as_float()
        target_position = current_item.target_position.get_value_as_float()
        target_velocity = current_item.target_velocity.get_value_as_float()
        damping = current_item.damping.get_value_as_float()
        stiffness = current_item.stiffness.get_value_as_float()

        joint_path = f"/{robot_name}/Joints/{joint_name}"

        # if joint already exist at path, remove it
        joint_prim = stage.GetPrimAtPath(joint_path)
        if joint_prim:
            stage.RemovePrim(joint_prim)

        # create the joint
        define_joints(joint_path=joint_path, joint_type=joint_type, axis=axis, parent=parent, child=child)

        apply_joint_settings(
            joint_path=joint_path,
            break_force=break_force,
            break_torque=break_torque,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
        )

        apply_drive_settings(
            joint_path=joint_path,
            drive_type=drive_type,
            max_force=max_force,
            target_position=target_position,
            target_velocity=target_velocity,
            damping=damping,
            stiffness=stiffness,
        )

    def create_joint_window(self):
        if not self._create_joint_window:
            self._create_joint_window = CreateJointWindow("Create Joint", self._joint_model)
        self._create_joint_window._window.visible = True

    def _filter_by_text(self, filters):
        if self._joint_model:
            self._joint_model.filter_by_text(filters)

    def _model_changed(self, model, item):
        # item data changed
        if item:
            # we only update the settings panel when the item triggers the change is the same as the one selected in the
            # tree view, which means the item properties the settings panel is showing
            # check if the joint name is valid
            if not Sdf.Path.IsValidIdentifier(item.name.get_value_as_string()):
                self._invalid_joint_name_label.visible = True
                self._next_step_button.enabled = False
                carb.log_error(f"Invalid joint name: {item.name.get_value_as_string()}")
            else:
                self._invalid_joint_name_label.visible = False
                self._next_step_button.enabled = True

            if self._tree_view.selection and item == self._tree_view.selection[0]:
                # update the settings panel
                return
        # item=None, root is changing meaning item has been added or removed

        if self._joint_model._searchable_num > 0:
            if self._treeview_empty_page.visible:
                self._treeview_empty_page.visible = False
            self._next_step_button.enabled = True
        elif self._joint_model._searchable_num == 0:
            self._next_step_button.enabled = False
            if not self._treeview_empty_page.visible:
                self._treeview_empty_page.visible = True
            if self._joint_settings_stack.visible:
                self._joint_settings_stack.visible = False
            if self._drive_settings_stack.visible:
                self._drive_settings_stack.visible = False

        # when self._joint_model changes, we update the id_column delegate
        if self._joint_model._searchable_num < TreeViewIDColumn.DEFAULT_ITEM_NUM:
            return
        if self._joint_model._searchable_num > self.id_column.num:
            self.id_column.add_item()
        elif self._joint_model._searchable_num < self.id_column.num:
            self.id_column.remove_item()

    def set_visible(self, visible):
        if self.frame:
            if visible:
                self._parse_joints_params()
            self.frame.visible = visible

    def _parse_joints_params(self):
        """
        if there are already joints in the robot, we need to parse the joints params from the robot and display them in the tree view
        """

        robot = RobotRegistry().get()
        stage = omni.usd.get_context().get_stage()
        if not robot or not stage:
            return

        # get joints folder
        settings_dict = {}

        if not self._joint_model:
            self._joint_model = JointsModel([])

        robot_name = robot.name
        joints_scope_path = f"/{robot_name}/Joints"
        joints_scope_prim = stage.GetPrimAtPath(joints_scope_path)
        if not joints_scope_prim:
            return
        joint_prims = joints_scope_prim.GetChildren()
        if joint_prims:
            for joint_prim in joint_prims:
                settings_dict = get_all_settings(joint_prim.GetPath().pathString)
            if settings_dict:
                self._joint_model.add_item(
                    JointItem(
                        name=settings_dict["joint_name"],
                        joint_type=settings_dict["joint_type"],
                        axis=settings_dict["axis"],
                        parent=settings_dict["parent"],
                        child=settings_dict["child"],
                        drive_type=settings_dict["drive_type"],
                        break_force=settings_dict["break_force"],
                        break_torque=settings_dict["break_torque"],
                        lower_limit=settings_dict["lower_limit"],
                        upper_limit=settings_dict["upper_limit"],
                        max_force=settings_dict["max_force"],
                        target_position=settings_dict["target_position"],
                        target_velocity=settings_dict["target_velocity"],
                        damping=settings_dict["damping"],
                        stiffness=settings_dict["stiffness"],
                    )
                )

    def __selection_changed(self, selection):
        # save the settings of the previously selected joint
        if self._previous_joint_item:
            self._save_joint_settings(self._previous_joint_item)

        if selection:
            item = selection[0]
            if isinstance(item, JointItem):
                self._previous_joint_item = item
                if item.joint_type.get_value_as_string() == "Fixed":
                    self._joint_settings_stack.visible = False
                    self._drive_settings_stack.visible = False
                else:
                    self.rebuild_settings(item)
                    self._joint_settings_stack.visible = True
                    self._drive_settings_stack.visible = True
        else:
            self._previous_joint_item = None

    def treeview_empty_page(self):
        self._treeview_empty_page = ui.VStack(visible=True, height=self._treeview_initial_height)
        with self._treeview_empty_page:
            ui.Spacer(height=ui.Fraction(3))
            ui.Label("Joint list is empty", alignment=ui.Alignment.CENTER, name="empty_treeview_title")
            ui.Spacer(height=ui.Fraction(2))
            ui.Label("There are no joints created yet", alignment=ui.Alignment.CENTER)
            ui.Spacer(height=ui.Fraction(2))
            ui.Label("Click the 'Create New Joint' button", alignment=ui.Alignment.CENTER)
            ui.Label("to begin the joint creation process", alignment=ui.Alignment.CENTER)
            ui.Spacer(height=ui.Fraction(2))

        self._treeview_empty_page.visible = bool(self._joint_model._searchable_num == 0)

    def _build_tree_view(self):
        with ui.ZStack():
            scrolling_frame = ui.ScrollingFrame(name="treeview", height=self._treeview_initial_height)
            with scrolling_frame:
                if not self._joint_model:
                    self._joint_model = JointsModel([])
                self.__subscription = self._joint_model.subscribe_item_changed_fn(self._model_changed)
                headers = ["Joint Name", "Joint Type", "Axis", "Drive Type", "Parent (Body0)", "Child (Body1)"]
                self._delegate = TreeViewWithPlacerHolderDelegate(
                    headers, [JOINT_TYPES, AXIS_LIST, DRIVE_TYPES], [2, 3, 4], self._joint_model
                )
                with ui.HStack():
                    self.id_column = TreeViewIDColumn()
                    with ui.ZStack():
                        self._tree_view = ui.TreeView(
                            self._joint_model,
                            delegate=self._delegate,
                            root_visible=False,
                            header_visible=True,
                            column_widths=[
                                20,
                                ui.Fraction(1),
                                ui.Fraction(1),
                                55,
                                ui.Fraction(0.8),
                                ui.Fraction(1.2),
                                ui.Fraction(1.2),
                                25,
                            ],
                            selection_changed_fn=self.__selection_changed,
                        )
                        self.treeview_empty_page()
            placer = ui.Placer(drag_axis=ui.Axis.Y, offset_y=self._treeview_initial_height, draggable=True)
            with placer:
                with ui.ZStack(height=4):
                    splitter_highlight = ui.Rectangle(name="splitter_highlight")

            def move(y):
                placer.offset_y = max(20, y.value)
                scrolling_frame.height = y

            placer.set_offset_y_changed_fn(move)

    def _save_joint_settings(self, item):
        # saving joint and drive settings from ui to model
        if item:
            if item.joint_type.get_value_as_string() != "Fixed":
                item.set_property("drive_type", item.drive_type.get_value_as_string())
                item.set_property("parent", item.parent.get_value_as_string())
                item.set_property("child", item.child.get_value_as_string())
                item.set_property("break_force", item.break_force.get_value_as_float())
                item.set_property("break_torque", item.break_torque.get_value_as_float())
                item.set_property("lower_limit", item.lower_limit.get_value_as_float())
                item.set_property("upper_limit", item.upper_limit.get_value_as_float())
                item.set_property("max_force", item.max_force.get_value_as_float())
                item.set_property("target_position", item.target_position.get_value_as_float())
                item.set_property("target_velocity", item.target_velocity.get_value_as_float())
                item.set_property("damping", item.damping.get_value_as_float())
                item.set_property("stiffness", item.stiffness.get_value_as_float())

    def add_joint_to_robot(self):
        """
        When click next button, add all joints to the robot
        """
        robot = RobotRegistry().get()
        robot_name = robot.name
        if not robot or self._joint_model._searchable_num == 0:
            return
        for item in self._joint_model.get_item_children(None):
            if isinstance(item, JointItem):
                self._create_joint(item)
        robot_path = f"/{robot_name}"
        apply_joint_apis(robot_path)


class CreateJointWindow:
    """This is the pop up window of Create/Edit joint"""

    def __init__(self, window_title, model, item=None):
        self._is_edit = window_title == "Edit Joint"  # the same window is used for create and edit
        self._current_joint_item = item  # the joint that is currently being edited or created
        self._current_joint_model = model  # the model for displaying in the main page
        self._window_height = 410
        self._collapsed_height = 340
        self._parent_xform_model = None
        self._child_xform_stack = None
        self._joint_name_widget = None
        self._drive_widget = None
        self._axis_widget = None
        self._drive_type_widget = None
        self._joint_type_widget = None
        self._create_button = None
        self._create_close_button = None
        self.__subscription = self._current_joint_model.subscribe_item_changed_fn(self._model_changed)
        self.joint_types = JOINT_TYPES
        self._select_new_joint_target_window = None
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_RESIZE
        self._window = ui.Window(window_title, width=600, height=self._collapsed_height)
        self._window.frame.set_build_fn(self._rebuild_frame)

    def destroy(self):
        self.__subscription = None
        if self._select_new_joint_target_window:
            self._select_new_joint_target_window.destroy()
        self._select_new_joint_target_window = None
        if self._window:
            self._window.destroy()
        self._window = None

    def _model_changed(self, model, item):
        # when model item changes (such as being changed in the main window), we need to update the ui if the window is visible
        if item and self._window.visible:
            self._update_ui(item)

    def _update_ui(self, item):
        # update the main window from model item data
        # parent xform
        self._parent_xform_widget.checked = bool(item)
        self._parent_xform_model.set_value(item.parent.get_value_as_string() if item else "Pick Parent Xform")
        # child xform
        self._child_xform_widget.checked = bool(item)
        self._child_xform_model.set_value(item.child.get_value_as_string() if item else "Pick Child Xform")
        # name
        self._joint_name_widget.model.set_value(
            item.name.get_value_as_string() if item else f"Joint{self._current_joint_model._searchable_num + 1}"
        )
        # axis
        index = AXIS_LIST.index(item.axis.get_value_as_string()) if item else 0
        self._axis_collection.model.set_value(index)
        # joint type
        type_idx = self.joint_types.index(item.joint_type.get_value_as_string()) if item else 0
        self._joint_type_widget.model.get_item_value_model().set_value(type_idx)
        # drive type
        drive_idx = DRIVE_TYPES.index(item.drive_type.get_value_as_string()) if item else 0
        self._drive_type_widget.model.get_item_value_model().set_value(drive_idx)
        # force the frame to update
        self._window.frame.invalidate_raster()

    def _update_item(self):
        # update joint item from the create window ui
        if not self._current_joint_item:
            return

        self._current_joint_item.set_property("name", self._joint_name_widget.model.get_value_as_string())
        self._current_joint_item.set_property("axis", AXIS_LIST[self._axis_collection.model.get_value_as_int()])
        self._current_joint_item.set_property(
            "joint_type", self.joint_types[self._joint_type_widget.model.get_item_value_model().get_value_as_int()]
        )
        self._current_joint_item.set_property(
            "drive_type", DRIVE_TYPES[self._drive_type_widget.model.get_item_value_model().get_value_as_int()]
        )
        self._current_joint_item.set_property("parent", self._parent_xform_model.get_value_as_string())
        self._current_joint_item.set_property("child", self._child_xform_model.get_value_as_string())
        self._current_joint_model._item_changed(self._current_joint_item)

    def _switch_xforms(self):

        if not self._child_xform_stack.enabled:
            return
        parent_value = self._parent_xform_model.get_value_as_string()
        child_value = self._child_xform_model.get_value_as_string()
        self._parent_xform_model.set_value(child_value)
        self._child_xform_model.set_value(parent_value)

    def on_collapsed_changed(self, collapsed):
        if collapsed:
            self._window.height = self._collapsed_height
        else:
            self._window.height = self._window_height

    def _update_joint_type(self, model, root_item):
        root_model = model.get_item_value_model(root_item)
        value = root_model.get_value_as_int()
        joint_type = self.joint_types[value]

        if joint_type == "Fixed":
            self._parent_xform_model.set_value("World")
            self._parent_xform_widget.enabled = False  # don't need parent xform for fixed joint
            self._axis_widget.visible = False
            self._drive_widget.visible = False
        else:
            self._parent_xform_widget.enabled = True
            self._axis_widget.visible = True
            self._drive_widget.visible = True

    def _on_create_clicked(self, closed=False):
        # when create clicked, update the joint model
        joint_name = self._joint_name_widget.model.get_value_as_string()
        joint_type = JOINT_TYPES[self._joint_type_widget.model.get_item_value_model().get_value_as_int()]
        axis = AXIS_LIST[self._axis_collection.model.get_value_as_int()]
        drive_type = DRIVE_TYPES[self._drive_type_widget.model.get_item_value_model().get_value_as_int()]
        parent = self._parent_xform_model.get_value_as_string()
        child = self._child_xform_model.get_value_as_string()

        if self._current_joint_item is not None:
            self._update_item()
        else:
            self._current_joint_item = JointItem(
                name=joint_name,
                joint_type=joint_type,
                axis=axis,
                drive_type=drive_type,
                parent=parent,
                child=child,
            )
            self._update_item()

        self._current_joint_model.add_item(self._current_joint_item)
        if closed:
            self._window.visible = False

        # clear the current joint from the pop up window
        self._current_joint_item = None
        self._update_ui(None)

    def _on_cancel_clicked(self):
        self._window.visible = False
        self._update_ui(None)
        self._current_joint_item = None

    def _on_save_clicked(self):
        if not self._current_joint_item:
            return

        self._on_create_clicked(True)
        self._window.visible = False

    def _rebuild_frame(self):
        with ui.HStack(height=0):
            ui.Spacer(width=10)
            with ui.VStack(style=get_popup_window_style(), spacing=10):
                infos = [
                    "Select 2 rigid bodies, a joint will be created between them.",
                    "To fix a body in place, select parent to be the /World or leave blank.",
                    "Joints can only move on a single axis.",
                    "Joints with Drives are powered and can receive movement commands.",
                    "Unpowered joints move under gravity or inertial forces.",
                ]
                info_frame(infos, self.on_collapsed_changed)

                with ui.HStack(height=18):
                    ui.Label("Joint Name", width=80, height=20)
                    self._joint_name_widget = ui.StringField(enabled=True, checked=True)
                    idx = self._current_joint_model._searchable_num + 1
                    name_value = self._current_joint_item.name.get_value_as_string() if self._is_edit else f"Joint{idx}"
                    self._joint_name_widget.model.set_value(name_value)
                    self._joint_name_widget.model.add_value_changed_fn(lambda m: self._on_joint_name_changed(m))
                    ui.Spacer(width=10)
                    self._invalid_joint_name_label = ui.Label(
                        "Invalid Joint Name", visible=False, style={"color": "red"}
                    )
                with ui.HStack(height=30):
                    idx = (
                        self.joint_types.index(self._current_joint_item.joint_type.get_value_as_string())
                        if self._is_edit
                        else 0
                    )
                    ui.Label("Joint Type", width=80, height=20)
                    self._joint_type_widget = ui.ComboBox(idx, *self.joint_types, enabled=True)
                    self._joint_type_widget.model.add_item_changed_fn(lambda m, i: self._update_joint_type(m, i))
                    ui.Spacer(width=10)
                with ui.HStack(height=66):
                    ui.Image(name="switch", width=26, mouse_pressed_fn=lambda x, y, b, a: self._switch_xforms())
                    ui.Spacer(width=4)
                    with ui.VStack():

                        with ui.HStack(height=18, enabled=True):
                            self._parent_xform_widget = ui.StringField(checked=bool(self._is_edit))
                            self._parent_xform_model = self._parent_xform_widget.model
                            parent_value = (
                                self._current_joint_item.parent.get_value_as_string()
                                if self._is_edit
                                else "Pick Parent Xform"
                            )
                            self._parent_xform_model.set_value(parent_value)
                            ui.Image(
                                name="sample",
                                height=18,
                                width=25,
                                mouse_pressed_fn=lambda x, y, b, a: self.select_new_joint_target(
                                    self._parent_xform_model, "Select Parent Xform"
                                ),
                            )
                            ui.Spacer(width=5)
                        ui.Spacer()
                        self._child_xform_stack = ui.HStack(height=18, enabled=True)
                        with self._child_xform_stack:
                            self._child_xform_widget = ui.StringField(checked=bool(self._is_edit))
                            self._child_xform_model = self._child_xform_widget.model
                            child_value = (
                                self._current_joint_item.child.get_value_as_string()
                                if self._is_edit
                                else "Pick Child Xform"
                            )
                            self._child_xform_model.set_value(child_value)
                            ui.Image(
                                name="sample",
                                height=18,
                                width=25,
                                mouse_pressed_fn=lambda x, y, b, a: self.select_new_joint_target(
                                    self._child_xform_model, "Select Child Xform"
                                ),
                            )
                            ui.Spacer(width=5)
                ui.Spacer()

                self._axis_widget = ui.HStack(enabled=True, height=30, spacing=4)
                with self._axis_widget:
                    ui.Label("Moving Axis", width=80)
                    ui.Spacer(width=10)
                    self._axis_collection = ui.RadioCollection()
                    ui.RadioButton(width=18, radio_collection=self._axis_collection)
                    ui.Label("X Axis", width=80)
                    ui.RadioButton(width=18, radio_collection=self._axis_collection)
                    ui.Label("Y Axis", width=80)
                    ui.RadioButton(width=18, radio_collection=self._axis_collection)
                    ui.Label("Z Axis", width=80)
                    if self._is_edit:
                        axis_value = self._current_joint_item.axis.get_value_as_string()
                        idx = AXIS_LIST.index(axis_value)
                        self._axis_collection.model.set_value(idx)

                self._drive_widget = ui.HStack(enabled=True, height=30, spacing=4)
                with self._drive_widget:
                    ui.Label("Drive Type", width=80, height=20)
                    idx = (
                        DRIVE_TYPES.index(self._current_joint_item.drive_type.get_value_as_string())
                        if self._is_edit
                        else 0
                    )
                    self._drive_type_widget = ui.ComboBox(idx, *DRIVE_TYPES, enabled=True)
                    ui.Spacer(width=10)
                if not self._is_edit:
                    with ui.HStack(height=22):
                        ui.Spacer()
                        with ui.HStack(width=77):
                            ButtonWithIcon("Cancel", image_width=0, enabled=True, clicked_fn=self._on_cancel_clicked)
                        ui.Spacer(width=14)
                        with ui.HStack(width=77):
                            self._create_button = ButtonWithIcon(
                                "Create", name="add", image_width=12, enabled=True, clicked_fn=self._on_create_clicked
                            )
                        ui.Spacer(width=14)
                        with ui.HStack(width=123):
                            self._create_close_button = ButtonWithIcon(
                                "Create & Close",
                                name="add",
                                image_width=12,
                                enabled=True,
                                clicked_fn=lambda: self._on_create_clicked(True),
                            )
                        ui.Spacer(width=10)
                else:
                    with ui.HStack(height=22):
                        ui.Spacer()
                        with ui.HStack(width=77):
                            ButtonWithIcon("Cancel", image_width=0, enabled=True, clicked_fn=self._on_cancel_clicked)
                        ui.Spacer(width=14)
                        with ui.HStack(width=80):
                            self._create_button = ButtonWithIcon(
                                "Save", name="save", image_width=12, clicked_fn=lambda: self._on_save_clicked()
                            )
                        ui.Spacer(width=10)

    def select(self, model, selected_paths):
        self._select_new_joint_target_window.visible = False
        self._selected_paths = selected_paths
        if self._selected_paths:
            model.set_value(self._selected_paths[0])

    def select_new_joint_target(self, model, title):
        if not self._select_new_joint_target_window:
            stage = omni.usd.get_context().get_stage()
            self._select_new_joint_target_window = RobotAssetPicker(
                title,
                stage,
                # filter_type_list=[UsdGeom.Xform],
                on_targets_selected=partial(self.select, model),
                target_name="Path",
            )
        else:
            self._select_new_joint_target_window.set_on_selected(partial(self.select, model))
        self._select_new_joint_target_window.visible = True

    def _on_joint_name_changed(self, m):
        joint_name_value = m.get_value_as_string()
        if Sdf.Path.IsValidIdentifier(joint_name_value):
            self._invalid_joint_name_label.visible = False
        else:
            self._invalid_joint_name_label.visible = True
