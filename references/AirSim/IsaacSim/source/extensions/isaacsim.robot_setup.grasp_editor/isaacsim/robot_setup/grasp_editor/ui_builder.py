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

import asyncio
import os
from functools import partial

import carb
import numpy as np
import omni.timeline
import omni.ui as ui
from isaacsim.core.api.articulations import ArticulationSubset
from isaacsim.core.prims import RigidPrim, SingleArticulation
from isaacsim.core.utils.numpy.rotations import quats_to_rot_matrices, rot_matrices_to_quats
from isaacsim.core.utils.stage import set_stage_units, update_stage_async
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.xforms import get_world_pose
from isaacsim.gui.components.element_wrappers import (
    Button,
    CheckBox,
    CollapsableFrame,
    DropDown,
    FloatField,
    Frame,
    StateButton,
    StringField,
    TextBlock,
)
from isaacsim.gui.components.ui_utils import get_style
from pxr import Usd, UsdGeom

from .data_writer import DataWriter
from .grasp_tester import GraspTester, GraspTestResults, GraspTestSettings
from .util import (
    adjust_text_block_num_lines,
    convert_prim_to_collidable_rigid_body,
    find_all_articulations,
    mask_collisions,
    move_rb_subframe_to_position,
    show_physics_colliders,
    unmask_collisions,
)


def is_yaml(file_path):
    return file_path.lower()[-5:] == ".yaml" or file_path.lower()[-4:] == ".yml"


class UIBuilder:
    def __init__(self):
        # Frames are sub-windows that can contain multiple UI elements
        self.frames = []
        # UI elements created using a UIElementWrapper instance
        self.wrapped_ui_elements = []

        # Get access to the timeline to control stop/pause/play programmatically
        self._timeline = omni.timeline.get_timeline_interface()

        self._grasp_tester = GraspTester()
        self._data_writer = None
        self._import_data_editor = None
        self._joint_settings_ui_state = None

        self._articulation = None
        self._rigid_body = None
        self._pre_test_rb_pose = None
        self._collision_mask = None

        self._robot_joint_frames = []
        self._test_state_btn = None

        self._last_grasp_test_results = None

    ###################################################################################
    #           The Functions Below Are Called Automatically By extension.py
    ###################################################################################

    def on_menu_callback(self):
        """Callback for when the UI is opened from the toolbar.
        This is called directly after build_ui().
        """
        if not self._timeline.is_stopped():
            self._selection_frame.rebuild()

    def on_timeline_event(self, event):
        """Callback for Timeline events (Play, Pause, Stop)

        Args:
            event (omni.timeline.TimelineEventType): Event Type
        """
        pass

    def on_physics_step(self, step: float):
        """Callback for Physics Step.
        Physics steps only occur when the timeline is playing

        Args:
            step (float): Size of physics step
        """
        pass

    def on_stage_event(self, event):
        """Callback for Stage Events

        Args:
            event (omni.usd.StageEventType): Event Type
        """
        if event.type == int(omni.usd.StageEventType.ASSETS_LOADED):
            self._gripper_selection_dropdown.repopulate()
        elif event.type == int(omni.usd.StageEventType.SIMULATION_STOP_PLAY):  # Stopped or paused
            if self._timeline.is_stopped():  # Just stopped
                self.reset_extension()

    def cleanup(self):
        """
        Called when the stage is closed or the extension is hot reloaded.
        Perform any necessary cleanup such as removing active callback functions
        Buttons imported from isaacsim.gui.components.element_wrappers implement a cleanup function that should be called
        """
        for ui_elem in self.wrapped_ui_elements:
            ui_elem.cleanup()

    def build_ui(self):
        """
        Build a custom UI tool to run your extension.
        This function will be called any time the UI window is closed and reopened.
        """
        self._selection_frame = CollapsableFrame(
            "Selection Frame", collapsed=False, build_fn=self.build_selection_frame
        )

        self._reference_frame = CollapsableFrame(
            "Select Frames of Reference", collapsed=True, enabled=False, build_fn=self.build_reference_frame
        )

        # Enabled only when valid selections have been made
        self._settings_frame = Frame(enabled=False, build_fn=self.build_settings_frame)

        # Enabled only when valid settings have been specified, otherewise provide README
        self._test_frame = CollapsableFrame(
            "Author Grasp", collapsed=True, enabled=False, build_fn=self.build_test_frame
        )

        # Enabled only when a test has been run, but not yet reset.
        self._export_frame = CollapsableFrame(
            "Export Grasp To File", collapsed=True, enabled=False, build_fn=self.build_export_frame
        )

        self._import_frame = CollapsableFrame(
            "Import Grasps From File", collapsed=True, enabled=False, build_fn=self.build_import_frame
        )

    ############################### Frame Builder Functions #####################################

    def build_selection_frame(self):
        with ui.VStack(style=get_style(), spacing=5, height=0):
            self._gripper_selection_dropdown = DropDown(
                "Select Gripper",
                tooltip="Select the gripper or Articulation with the gripper",
                populate_fn=find_all_articulations,
                keep_old_selections=True,
            )
            self._gripper_selection_dropdown.repopulate()

            self._rb_conversion_stringfield = StringField(
                "Select Rigid Body",
                tooltip="Input a prim that should be converted to a rigid body for the sake of validating a grasp.",
            )

            def show_warning_if_existing(file_path):
                if not is_yaml(file_path):
                    self._selection_ready_btn.enabled = False
                else:
                    self._selection_ready_btn.enabled = True
                self._warning_box.visible = os.path.isfile(file_path)

            self._export_path = StringField(
                "Export File Path",
                use_folder_picker=True,
                item_filter_fn=is_yaml,
                on_value_changed_fn=show_warning_if_existing,
            )

            self._selection_ready_btn = StateButton(
                "Ready to Go",
                "READY",
                "START OVER",
                tooltip="Click when ready to move forward authoring grasps between the selected Articulation and selected prim.",
                on_a_click_fn=self._on_finished_selection_frame,
                on_b_click_fn=self._on_reset_selection_frame,
            )

            self._selection_frame_helper_text = TextBlock("README", "", num_lines=2)
            self._selection_frame_helper_text.visible = False

            self._warning_box = TextBlock(
                "README", "Exporting to an existing file will overwrite that file.", num_lines=1
            )
            self._warning_box.visible = False

    def build_reference_frame(self):
        if self._articulation is None:
            return

        def populate_subframes(prim, filter: StringField):
            frames = [
                str(p.GetPath())
                for p in Usd.PrimRange(prim)
                if UsdGeom.Xformable(p) and filter.get_value() in str(p.GetPath())
            ]
            if len(frames) == 1:
                return frames
            else:
                return ["Select A Frame of Reference"] + frames

        def on_subframe_selection(value):
            if len(self._rb_subframe.get_items()) > 1 and self._rb_subframe.get_selection_index() == 0:
                self._finalize_frame_btn.enabled = False
            elif len(self._gripper_subframe.get_items()) > 1 and self._gripper_subframe.get_selection_index() == 0:
                self._finalize_frame_btn.enabled = False
            else:
                self._finalize_frame_btn.enabled = True

        def on_highlight_gripper_subframe():
            if len(self._gripper_subframe.get_items()) == 1 or self._gripper_subframe.get_selection_index() > 0:
                omni.kit.commands.execute(
                    "SelectPrimsCommand",
                    old_selected_paths=[],
                    new_selected_paths=[self._gripper_subframe.get_selection()],
                    expand_in_stage=True,
                )

        def on_highlight_rb_subframe():
            if len(self._rb_subframe.get_items()) == 1 or self._rb_subframe.get_selection_index() > 0:
                omni.kit.commands.execute(
                    "SelectPrimsCommand",
                    old_selected_paths=[],
                    new_selected_paths=[self._rb_subframe.get_selection()],
                    expand_in_stage=True,
                )

        with ui.VStack(style=get_style(), spacing=6, height=0):
            tt = "Type the name of the gripper frame of reference to filter the Gripper Frame DropDown."
            self._gripper_subframe_filter = StringField("Gripper Frame Filter", tooltip=tt)

            self._gripper_subframe = DropDown(
                "Gripper Frame",
                populate_fn=partial(populate_subframes, self._articulation.prim, self._gripper_subframe_filter),
                tooltip="Frame of reference that will be saved for where the Gripper is relative to the Rigid Body.",
                keep_old_selections=True,
            )

            self._gripper_subframe.repopulate()
            self._gripper_subframe_filter.set_on_value_changed_fn(lambda _: self._gripper_subframe.repopulate())

            Button(
                "Highlight Subframe",
                "HIGHLIGHT",
                on_click_fn=on_highlight_gripper_subframe,
                tooltip="Highlight the pose of the selected gripper subframe on the stage.",
            )

            tt = "Type the name of the rigid body frame of reference to filter the Rigid Body Frame DropDown."
            self._rb_subframe_filter = StringField("Rigid Body Frame Filter", default_value="", tooltip=tt)

            self._rb_subframe = DropDown(
                "Rigid Body Frame",
                populate_fn=partial(populate_subframes, self._rigid_body.prims[0], self._rb_subframe_filter),
                tooltip="Frame that will be used as the origin when determining the relative position of the Gripper.",
                keep_old_selections=True,
            )
            self._rb_subframe.repopulate()
            self._rb_subframe_filter.set_on_value_changed_fn(lambda _: self._rb_subframe.repopulate())

            Button(
                "Highlight Subframe",
                "HIGHLIGHT",
                on_click_fn=on_highlight_rb_subframe,
                tooltip="Highlight the pose of the selected rigid body subframe on the stage.",
            )

            self._finalize_frame_btn = Button(
                "Finalize Selection", "FINALIZE", on_click_fn=self._finalize_reference_frame_selection
            )

            # These are delayed from initialization of the fields because they refer to the _finalize_frame_btn
            self._gripper_subframe.set_on_selection_fn(on_subframe_selection)
            self._rb_subframe.set_on_selection_fn(on_subframe_selection)

            self._gripper_subframe.trigger_on_selection_fn_with_current_selection()
            self._rb_subframe.trigger_on_selection_fn_with_current_selection()

            frame_explanation = CollapsableFrame("Explain This Panel", collapsed=True)
            with frame_explanation:
                TextBlock(
                    "README",
                    (
                        "Use this panel to select the frames of reference of the gripper "
                        + "and rigid body.  These selections will be used to compute the "
                        + "gripper position relative to the rigid body.  This is critical "
                        + "information for being able to import and export grasps accurately.\n\n"
                        + "Specifically, the frames selected must be consistent with the control "
                        + "point of the relevant motion generation algorithm that will be using "
                        + "these grasps.\n\nWhen importing into USD, there is typically a direct "
                        + "correspondence between the asset under import (the URDF or mesh) and "
                        + "frames of interest in the original asset."
                    ),
                    num_lines=11,
                )

    def build_settings_frame(self):
        if self._articulation is None or self._rigid_body is None or self._timeline.is_stopped():
            # This is for aesthetics only.
            CollapsableFrame("Grasp Test Configuration", collapsed=True, enabled=False)
            return

        def on_click_include_all_dofs():
            for dof_name in self._articulation.dof_names:
                self._joint_settings_ui_state.set_active_dof(self._articulation, dof_name)
            for joint_frame in self._robot_joint_frames:
                joint_frame.rebuild()
            self._test_frame.rebuild()

        def on_click_exclude_all_dofs():
            for dof_name in self._articulation.dof_names:
                self._joint_settings_ui_state.set_fixed_dof(self._articulation, dof_name)
            for joint_frame in self._robot_joint_frames:
                joint_frame.rebuild()
            self._test_frame.rebuild()

        def on_collapse_joint_frame():
            self._joint_settings_frame.collapsed = True

        def on_click_cb(index, value):
            dof_name = self._articulation.dof_names[index]
            if value:
                self._joint_settings_ui_state.set_active_dof(self._articulation, dof_name)
            else:
                self._joint_settings_ui_state.set_fixed_dof(self._articulation, dof_name)

            self._robot_joint_frames[index].rebuild()
            self._test_frame.rebuild()

        def on_change_joint_position(joint_index, value):
            dof_name = self._articulation.dof_names[joint_index]
            if self._joint_settings_ui_state.is_active(dof_name):
                self._joint_settings_ui_state.set_open_position(dof_name, value)
            else:
                self._joint_settings_ui_state.set_fixed_position(dof_name, value)
            robot_action = ArticulationAction(
                joint_positions=np.array([value]),
                joint_velocities=np.array([0]),
                joint_indices=np.array([joint_index]),
            )
            self._articulation.apply_action(robot_action)

        def on_change_close_position(joint_index, value):
            dof_name = self._articulation.dof_names[joint_index]
            self._joint_settings_ui_state.set_close_position(dof_name, value)

        def on_change_max_effort(joint_index, max_effort):
            dof_name = self._articulation.dof_names[joint_index]
            self._joint_settings_ui_state.set_max_effort(dof_name, max_effort)
            self._articulation.get_articulation_controller().set_max_efforts([max_effort], [joint_index])

        def on_change_max_speed(joint_index, max_speed):
            dof_name = self._articulation.dof_names[joint_index]
            self._joint_settings_ui_state.set_max_speed(dof_name, max_speed)

        def on_mask_collisions():
            self._collision_mask = mask_collisions(self._articulation.prim_path, self._rigid_body.prim_paths[0])

        def on_unmask_collisions():
            # Allow a frame for instantaneous deep collision to resolve, and then set rigid body velocty to zero.
            # This is repeated for good measure, as a miniscule residual velocity was observed after doing it once.
            async def unmask_over_time():
                unmask_collisions(self._collision_mask)
                self._collision_mask = None

                await update_stage_async()
                self._rigid_body.set_velocities(np.zeros((1, 6)))

                await update_stage_async()
                self._rigid_body.set_velocities(np.zeros((1, 6)))

            asyncio.ensure_future(unmask_over_time())

        def on_build_joint_frame(joint_index):
            if self._articulation is None:
                return

            dof_name = self._articulation.dof_names[joint_index]
            lower_joint_limits = self._articulation.dof_properties["lower"]
            upper_joint_limits = self._articulation.dof_properties["upper"]
            max_speeds = self._articulation.dof_properties["maxVelocity"]
            joint_positions = self._articulation.get_joint_positions()

            with ui.VStack(style=get_style(), spacing=6, height=0):
                CheckBox(
                    f"Part of Gripper:",
                    default_value=self._joint_settings_ui_state.is_active(dof_name),
                    tooltip="Select which DOFs are part of the gripper.",
                    on_click_fn=partial(on_click_cb, joint_index),
                )

                upper_limit = upper_joint_limits[joint_index]
                lower_limit = lower_joint_limits[joint_index]
                position_step = float(min(0.01, (upper_limit - lower_limit) / 10.0))
                num_position_decimals = -int(np.floor(np.log10(position_step)))
                position_format = f"%.{num_position_decimals}f"

                if self._joint_settings_ui_state.is_active(dof_name):
                    FloatField(
                        "Position When Open",
                        default_value=self._joint_settings_ui_state.get_open_position(dof_name),
                        lower_limit=lower_limit,
                        upper_limit=upper_limit,
                        on_value_changed_fn=partial(on_change_joint_position, joint_index),
                        tooltip="This DOF will start from the position specified here when testing a grasp.",
                        step=position_step,
                        format=position_format,
                    )

                    FloatField(
                        "Position When Closed",
                        default_value=self._joint_settings_ui_state.get_close_position(dof_name),
                        lower_limit=lower_limit,
                        upper_limit=upper_limit,
                        tooltip="This DOF will attempt to move to the specified close position when testing the grasp.",
                        on_value_changed_fn=partial(on_change_close_position, joint_index),
                        step=position_step,
                        format=position_format,
                    )

                    tt = (
                        "This DOF will move at the specified speed from the OPEN position to the CLOSED position.  "
                        + "If the Max Effort parameter for the DOF is very low, it may not reach this speed."
                    )
                    FloatField(
                        "Grasp Speed",
                        tooltip=tt,
                        lower_limit=0.001,
                        upper_limit=max_speeds[joint_index],
                        default_value=self._joint_settings_ui_state.get_max_speed(dof_name),
                        on_value_changed_fn=partial(on_change_max_speed, joint_index),
                        step=position_step,
                        format=position_format,
                    )

                    tt = f"The magnitude of the maximum effort that can be applied by this joint in standard SI units (N*m for revolute joints and N for prismatic joints)."
                    FloatField(
                        "Max Effort Magnitude",
                        tooltip=tt,
                        lower_limit=0.0,
                        upper_limit=1e15,
                        default_value=self._joint_settings_ui_state.get_max_effort(dof_name),
                        on_value_changed_fn=partial(on_change_max_effort, joint_index),
                    )
                else:
                    FloatField(
                        "Fixed Position",
                        default_value=joint_positions[joint_index],
                        lower_limit=lower_limit,
                        upper_limit=upper_limit,
                        on_value_changed_fn=partial(on_change_joint_position, joint_index),
                        tooltip="This DOF will be fixed to this position (with high gains) while the gripper DOFs move.",
                        step=position_step,
                        format=position_format,
                    )

        dof_names = self._articulation.dof_names

        self._robot_joint_frames = [None] * len(dof_names)

        with ui.VStack(style=get_style(), spacing=6, height=0):
            self._joint_settings_frame = CollapsableFrame("Joint Settings", collapsed=False)
            with self._joint_settings_frame:
                with ui.VStack(style=get_style(), spacing=6, height=0):
                    for index, dof_name in enumerate(dof_names):
                        joint_frame = CollapsableFrame(
                            f"{dof_name}", collapsed=False, build_fn=partial(on_build_joint_frame, index)
                        )
                        joint_frame.rebuild()
                        self._robot_joint_frames[index] = joint_frame

                    StateButton(
                        "Include All DOFs",
                        "INCLUDE ALL DOFS",
                        "EXCLUDE ALL DOFS",
                        tooltip="Mark that every DOF is part of the gripper.",
                        on_a_click_fn=on_click_include_all_dofs,
                        on_b_click_fn=on_click_exclude_all_dofs,
                    )

                    Button(
                        "Collapse Joint Settings",
                        "COLLAPSE",
                        tooltip="Hide the per-joint robot settings frame.",
                        on_click_fn=on_collapse_joint_frame,
                    )

            utils_frame = CollapsableFrame("Utils", collapsed=False)
            with utils_frame:
                with ui.VStack(style=get_style(), spacing=6, height=0):
                    self._collision_mask_btn = StateButton(
                        "Mask Collisions",
                        "MASK",
                        "UNMASK",
                        tooltip="Mask collisions between the Articulation and the Rigid Body.",
                        on_a_click_fn=on_mask_collisions,
                        on_b_click_fn=on_unmask_collisions,
                    )

                    self._show_colliders_btn = StateButton(
                        "Show Physics Colliders",
                        "SHOW",
                        "HIDE",
                        tooltip="Show colliders that are used for simulating collisions.",
                        on_a_click_fn=partial(show_physics_colliders, True),
                        on_b_click_fn=partial(show_physics_colliders, False),
                    )

            self._external_forces_frame = CollapsableFrame("Add External Rigid Body Forces")
            with self._external_forces_frame:
                with ui.VStack(style=get_style(), spacing=6, height=0):
                    self._force_magnitude_field = FloatField(
                        "External Force Magnitude",
                        default_value=0.0,
                        lower_limit=0.0,
                        tooltip="A force of the specified magnitude will be applied along each axis of the Rigid Body to test grasp quality.",
                    )
                    self._torque_magnitude_field = FloatField(
                        "External Torque Magnitude",
                        default_value=0.0,
                        lower_limit=0.0,
                        tooltip="A torque of the specified magnitude will be applied about each axis of the Rigid body to testgrasp quality.",
                    )

                    TextBlock(
                        "README",
                        (
                            "Setting one of these fields to a non-zero value will add two seconds to the "
                            + "grasp test duration.  A force or torque of the specified magnitude will be applied "
                            + "to the Rigid Body along each +- XYZ axis centered at its base frame for 1/3 seconds."
                        ),
                        num_lines=4,
                    )

    def build_test_frame(self):
        if self._articulation is None:
            return

        if len(self._joint_settings_ui_state._active_dof_settings) == 0:
            TextBlock(
                "README",
                "At least one DOF must be selected as part of the gripper in order to author a grasp.",
                num_lines=2,
            )
            return

        with ui.VStack(style=get_style(), spacing=5, height=0):
            self._test_state_btn = StateButton(
                "Simulate Grasp",
                "SIMULATE",
                "RESET",
                on_a_click_fn=self._on_run_test_a_text,
                on_b_click_fn=self._on_run_test_b_text,
                physics_callback_fn=self._update_test,
                tooltip="Physically simulate this grasp with collisions turned on.",
            )

            self._test_skip_btn = Button(
                "Export As Is",
                "SKIP SIM",
                tooltip="Export exactly what you see on the stage as the grasp that will be written to file.",
                on_click_fn=self._export_without_simulating,
            )

            self._status_text_block = TextBlock("Status", "", num_lines=1)

        self.wrapped_ui_elements.append(self._test_state_btn)

    def build_export_frame(self):
        with ui.VStack(style=get_style(), spacing=5, height=0):
            self._suggest_confidence_cb = CheckBox(
                "Auto Compute Confidence",
                default_value=True,
                tooltip="Automatically suggest confidence values based on grasp test results.",
            )
            self._confidence_field = FloatField(
                "Confidence",
                default_value=1.0,
                lower_limit=0.0,
                upper_limit=1.0,
                tooltip=(
                    "Confidence value for grasp quality that will guide the order in which "
                    + "a motion planner prioritizes grasps."
                ),
            )
            self._export_btn = Button("Export", "EXPORT", on_click_fn=self.export_to_file)

            self._export_txt = TextBlock("README", "Ready To Export Grasp", num_lines=1)

    def build_import_frame(self):
        def on_import_grasps():
            if not is_yaml(self._import_path.get_value()):
                return
            self._import_data_editor = DataWriter(
                self._gripper_subframe.get_selection(), self._rb_subframe.get_selection()
            )

            status = self._import_data_editor.import_grasps_from_file(self._import_path.get_value())
            if status != "":
                self._import_status_msg.set_text(status)
                self._import_status_msg.visible = True
                self._import_frame_tools.visible = False
                return
            else:
                self._import_status_msg.visible = False
                self._import_frame_tools.visible = True

            self._import_frame_tools.visible = True

            prev_sel = self._grasp_dropdown.get_selection()
            self._grasp_dropdown.repopulate()
            if prev_sel == self._grasp_dropdown.get_selection():
                self._grasp_dropdown.trigger_on_selection_fn_with_current_selection()

        def grasp_populate_fn():
            if self._import_data_editor is None:
                return []
            return list(self._import_data_editor.data["grasps"].keys())

        def on_grasp_selection(val):
            grasp = self._import_data_editor.data["grasps"][val]

            async def load_grasp(grasp):
                art_subset = ArticulationSubset(self._articulation, list(grasp["cspace_position"].keys()))
                for dof_name in self._articulation.dof_names:
                    if dof_name in grasp["cspace_position"]:
                        self._joint_settings_ui_state.set_active_dof(self._articulation, dof_name)
                    else:
                        self._joint_settings_ui_state.set_fixed_dof(self._articulation, dof_name)

                lower_joint_limits = self._articulation.dof_properties["lower"]
                upper_joint_limits = self._articulation.dof_properties["upper"]
                grasping_positions = np.zeros(art_subset.num_joints)
                for idx, dof_name in enumerate(grasp["cspace_position"].keys()):
                    grasping_position = grasp["cspace_position"][dof_name]
                    open_position = grasp["pregrasp_cspace_position"][dof_name]

                    # Set the close state of the gripper based on the direction of closing.
                    if abs(grasping_position - open_position) < 1e-10:
                        # The file does not specify which way the gripper closes, so don't make a guess.
                        self._joint_settings_ui_state.set_close_position(dof_name, open_position)
                    elif grasping_position - open_position < 0:
                        self._joint_settings_ui_state.set_close_position(
                            dof_name, lower_joint_limits[self._articulation.get_dof_index(dof_name)]
                        )
                    else:
                        self._joint_settings_ui_state.set_close_position(
                            dof_name, upper_joint_limits[self._articulation.get_dof_index(dof_name)]
                        )

                    self._joint_settings_ui_state.set_open_position(dof_name, grasping_position)

                    grasping_positions[idx] = grasping_position

                for joint_frame in self._robot_joint_frames:
                    joint_frame.rebuild()
                self._test_frame.rebuild()

                # Mask collisions on import.
                self._collision_mask_btn.trigger_click_if_a_state()

                # Teleport gripper to desired state
                art_subset.set_joint_positions(grasping_positions)
                art_subset.apply_action(grasping_positions)

                # Teleport rigid body to correct position relative to gripper.  This inverts the
                # transforms defined in grasp_tester.compute_relative_pose().
                art_trans, art_quat = get_world_pose(self._gripper_subframe.get_selection())

                art_quat_rel_rb = np.array([grasp["orientation"]["w"], *grasp["orientation"]["xyz"]])
                art_rot_rel_rb, art_rot = quats_to_rot_matrices(np.vstack([art_quat_rel_rb, art_quat]))
                art_trans_rel_rb = np.array(grasp["position"])

                rb_rot = art_rot @ art_rot_rel_rb.T
                rb_quat = rot_matrices_to_quats(rb_rot)
                rb_trans = art_trans - rb_rot @ art_trans_rel_rb

                move_rb_subframe_to_position(self._rigid_body, self._rb_subframe.get_selection(), rb_trans, rb_quat)
                # SingleXFormPrim(self._rb_subframe.get_selection()).set_world_pose(rb_trans, rb_quat)
                self.stop_rigid_body()

                await update_stage_async()

                self.stop_rigid_body()

            asyncio.ensure_future(load_grasp(grasp))

        def on_next_grasp_clicked():
            num_items = len(self._grasp_dropdown.get_items())
            if num_items == 1:
                self._grasp_dropdown.trigger_on_selection_fn_with_current_selection()
            else:
                self._grasp_dropdown.set_selection_by_index(
                    (self._grasp_dropdown.get_selection_index() + 1) % num_items
                )

        with ui.VStack(style=get_style(), spacing=5, height=0):
            self._import_path = StringField("Select File Path", use_folder_picker=True, item_filter_fn=is_yaml)

            self._import_btn = Button("Import Grasps", "IMPORT", on_click_fn=on_import_grasps)

            self._import_status_msg = TextBlock("README", "", num_lines=2)
            self._import_status_msg.visible = False

            self._import_frame_tools = Frame(visible=False)
            with self._import_frame_tools:
                with ui.VStack(style=get_style(), spacing=5, height=0):
                    self._grasp_dropdown = DropDown(
                        "Grasps", populate_fn=grasp_populate_fn, on_selection_fn=on_grasp_selection
                    )
                    Button("Next Grasp", "NEXT", on_click_fn=on_next_grasp_clicked)

    ############################# UI Control Functions ########################################
    def _on_reset_selection_frame(self):
        self._gripper_selection_dropdown.enabled = True
        self._rb_conversion_stringfield.enabled = True
        self._export_path.enabled = True

        self.reset_extension()

    def _on_finished_selection_frame(self):
        if self._gripper_selection_dropdown.get_selection() == "":
            self._selection_frame_helper_text.visible = True
            self._selection_frame_helper_text.set_text("An Articulation must be present on the stage to continue.")
            self._selection_ready_btn.reset()
            return
        elif self._rb_conversion_stringfield.get_value() == "":
            self._selection_frame_helper_text.visible = True
            self._selection_frame_helper_text.set_text("A valid prim must be selected on the stage to continue.")
            self._selection_ready_btn.reset()
            return
        elif not is_yaml(self._export_path.get_value()):
            self._selection_frame_helper_text.visible = True
            self._selection_frame_helper_text.set_text(
                "A valid export path must be selected to continue.  Make sure the path ends in '.yaml'."
            )
            self._selection_ready_btn.reset()
            return

        rb_prim_path = self._rb_conversion_stringfield.get_value()

        error_text = convert_prim_to_collidable_rigid_body(rb_prim_path, self._gripper_selection_dropdown.get_items())
        if error_text is not None:
            self._selection_frame_helper_text.visible = True
            self._selection_frame_helper_text.set_text(error_text)
            return

        # Ensure that stage units are in meters to give meaning to the effort and velocity values.
        set_stage_units(1.0)

        async def initialize_objects():
            self._timeline.play()

            await update_stage_async()

            self._articulation = SingleArticulation(self._gripper_selection_dropdown.get_selection())
            self._articulation.initialize()

            self._rigid_body = RigidPrim(rb_prim_path, reset_xform_properties=False)
            self._rigid_body.initialize()
            self._rigid_body.disable_gravities()

            self.stop_rigid_body()
            await update_stage_async()
            self.stop_rigid_body()

            self._selection_frame_helper_text.visible = False

            self._gripper_selection_dropdown.enabled = False
            self._rb_conversion_stringfield.enabled = False
            self._export_path.enabled = False

            self._reference_frame.enabled = True
            self._reference_frame.collapsed = False
            self._reference_frame.rebuild()

        asyncio.ensure_future(initialize_objects())

    def _finalize_reference_frame_selection(self):
        self._data_writer = DataWriter(self._gripper_subframe.get_selection(), self._rb_subframe.get_selection())

        self._joint_settings_ui_state = JointFrameUIState(self._articulation)

        self._reference_frame.collapsed = True
        self._reference_frame.enabled = False
        self._populate_settings_frame()

        self._test_frame.rebuild()

    def _populate_settings_frame(self):
        self._settings_frame.enabled = True
        self._settings_frame.collapsed = False
        self._settings_frame.rebuild()

        self._test_frame.enabled = True
        self._test_frame.collapsed = False
        self._test_frame.rebuild()

        self._export_frame.collapsed = True
        self._export_frame.enabled = False

        self._import_frame.enabled = True

    def reset_extension(self):
        if not self._timeline.is_stopped() and self._rigid_body is not None:
            self.stop_rigid_body()

        self._articulation = None
        self._rigid_body = None
        self._data_writer = None
        self._last_grasp_test_results = None
        self._joint_settings_ui_state = None

        self._gripper_selection_dropdown.enabled = True
        self._rb_conversion_stringfield.enabled = True
        self._export_path.enabled = True

        self._reference_frame.collapsed = True
        self._reference_frame.enabled = False

        self._settings_frame.enabled = False
        self._settings_frame.collapsed = True
        self._settings_frame.rebuild()

        self._test_frame.enabled = False
        self._test_frame.collapsed = True

        self._export_frame.enabled = False
        self._export_frame.collapsed = True

        self._import_frame.enabled = False
        self._import_frame.collapsed = True
        self._import_frame_tools.visible = False

        if self._test_state_btn is not None:
            self._test_state_btn.reset()
        self._selection_ready_btn.reset()

        self._warning_box.visible = os.path.isfile(self._export_path.get_value())

        if self._collision_mask is not None:
            unmask_collisions(self._collision_mask)
            self._collision_mask_btn.reset()

        show_physics_colliders(False)

    ##################################### Grasp Test ###############################################
    def get_current_grasp_test_settings(self):
        active_joint_names = []
        active_joint_open_positions = []
        active_joint_closed_positions = []
        active_joint_speeds = []

        inactive_joint_fixed_positions = []
        for dof_name in self._articulation.dof_names:
            if self._joint_settings_ui_state.is_active(dof_name):
                active_joint_names.append(dof_name)
                active_joint_open_positions.append(self._joint_settings_ui_state.get_open_position(dof_name))
                active_joint_closed_positions.append(self._joint_settings_ui_state.get_close_position(dof_name))
                active_joint_speeds.append(self._joint_settings_ui_state.get_max_speed(dof_name))
            else:
                inactive_joint_fixed_positions.append(self._joint_settings_ui_state.get_fixed_position(dof_name))

        grasp_test_settings = GraspTestSettings(
            self._articulation.prim_path,
            self._gripper_subframe.get_selection(),
            active_joint_names,
            active_joint_open_positions,
            active_joint_closed_positions,
            active_joint_speeds,
            inactive_joint_fixed_positions,
            self._rigid_body.prim_paths[0],
            self._rb_subframe.get_selection(),
            self._force_magnitude_field.get_value(),
            self._torque_magnitude_field.get_value(),
        )

        return grasp_test_settings

    def _update_test(self, step: float):
        result = self._grasp_tester.update_grasp_test(step)

        # The grasp test generates status messages until a final result.
        if isinstance(result, str):
            if self._status_text_block is None:
                return
            self._status_text_block.visible = True
            self._status_text_block.set_text(result)
            adjust_text_block_num_lines(self._status_text_block)
        elif isinstance(result, GraspTestResults):
            self._last_grasp_test_results = result
            self.ready_to_export_grasp(result.suggested_confidence, "Ready To Export Grasp")

    def _on_run_test_a_text(self):
        self._pre_test_rb_pose = self._rigid_body.get_world_poses()

        # Simulating a grasp is always done with collisions turned on.
        self._collision_mask_btn.trigger_click_if_b_state()

        grasp_test_settings = self.get_current_grasp_test_settings()

        self._grasp_tester.initialize_test_grasp_script(self._articulation, self._rigid_body, grasp_test_settings)

        self._export_frame.collapsed = True
        self._export_frame.enabled = False

    def _on_run_test_b_text(self):
        # Open the gripper and make sure that the object is not moved while this happens from
        # the contact forces.
        async def open_gripper():
            open_position = [
                self._joint_settings_ui_state.get_joint_position(dof_name) for dof_name in self._articulation.dof_names
            ]
            self._articulation.set_joint_positions(open_position)
            self._articulation.set_joint_velocities(np.zeros_like(open_position))
            await update_stage_async()

            self._articulation.apply_action(ArticulationAction(open_position))

            self.stop_rigid_body()

            await update_stage_async()

            self.stop_rigid_body()
            self._rigid_body.set_world_poses(*self._pre_test_rb_pose)

            self._test_state_btn.reset()
            self._status_text_block.set_text("")
            self._status_text_block.set_num_lines(1)

            self._export_frame.collapsed = True
            self._export_frame.enabled = False

        asyncio.ensure_future(open_gripper())

    def _export_without_simulating(self):
        x = self.get_current_grasp_test_settings()
        rel_trans, rel_quat = self._grasp_tester.compute_relative_pose(
            x.rigid_body_pose_frame, x.articulation_pose_frame
        )

        # Take the current position of the gripper joints on the stage to be the grasp under export
        art_subset = ArticulationSubset(self._articulation, x.active_joints)
        stable_positions = art_subset.get_joint_positions()

        # Set the pre_grasp position to be the same as stable_positions.  I.e. this grasp has no opinion
        # on which way the gripper closes because there is not enough information.
        x.active_joint_open_positions = stable_positions

        # Assume that anybody doing this is confident in what they are doing.
        suggested_confidence = 1.0

        self._last_grasp_test_results = GraspTestResults(
            x, rel_trans, rel_quat, stable_positions, suggested_confidence, True
        )

        self.ready_to_export_grasp(
            suggested_confidence,
            "Ready To Export Grasp.  Because you have opted to skip simulation, it is not "
            + "known which way the gripper closes.  The current state of the gripper "
            + "will be used as the value of cspace_position and pregrasp_cspace_position "
            + "in the exported file.  To use this with a motion generation algorithm, it will "
            + "be necessary to change one of these fields for this grasp in the export file.",
        )

    #################################### Export To File ###########################################

    def ready_to_export_grasp(self, suggested_confidence, export_txt):
        self._export_frame.collapsed = False
        self._export_frame.enabled = True
        self._export_txt.set_text(export_txt)
        adjust_text_block_num_lines(self._export_txt)
        self._export_btn.enabled = True
        if self._suggest_confidence_cb.get_value():
            self._confidence_field.set_value(suggested_confidence)

    def export_to_file(self):
        # Export self._last_grasp_test_results
        export_path = self._export_path.get_value()
        self._data_writer.write_grasp_to_file(
            self._last_grasp_test_results, self._confidence_field.get_value(), export_path
        )
        self._export_btn.enabled = False
        self._export_txt.set_text(f"Successfully exported grasp to file {export_path}")
        self._export_txt.set_num_lines(2)

    #################################### Shared Util ##############################################

    def stop_rigid_body(self):
        self._rigid_body.set_velocities(np.zeros((1, 6)))
        self._rigid_body.apply_forces_and_torques_at_pos(np.zeros((1, 3)), np.zeros((1, 3)))


class JointFrameUIState:
    """This class stores the UI state of joint frames.  The natural thing to do is to rely on the
    UI itself in order to store values for joint settings.  But this runs into complications when
    you want to programmatically switch a joint from inactive to active.  Only the frames that
    are visible on the screen will update when you rebuild the joint frames, and so UI state cannot
    be relied upon as up to date in this case.

    This class makes sure that when the UI gets around to updating because the user scrolled or
    expanded the joint settings window, the latest settings are used in the building."""

    def __init__(self, articulation):
        self._fixed_dof_settings = {}
        self._active_dof_settings = {}

        for dof_name in articulation.dof_names:
            self.set_fixed_dof(articulation, dof_name)

    def _get_default_close_position(self, upper_limit, lower_limit, open_position):
        if np.abs(open_position - upper_limit) < np.abs(open_position - lower_limit):
            return lower_limit
        else:
            return upper_limit

    def is_active(self, dof_name):
        return dof_name in self._active_dof_settings

    def get_fixed_position(self, dof_name):
        if dof_name in self._fixed_dof_settings:
            return self._fixed_dof_settings[dof_name]["fixed_position"]
        else:
            carb.log_error("Attempted to access fixed joint setting for an active dof")

    def get_open_position(self, dof_name):
        if dof_name in self._active_dof_settings:
            return self._active_dof_settings[dof_name]["open_position"]
        else:
            carb.log_error("Attempted to access active joint setting for a fixed dof")

    def get_close_position(self, dof_name):
        if dof_name in self._active_dof_settings:
            return self._active_dof_settings[dof_name]["close_position"]
        else:
            carb.log_error("Attempted to access active joint setting for a fixed dof")

    def get_max_speed(self, dof_name):
        if dof_name in self._active_dof_settings:
            return self._active_dof_settings[dof_name]["max_speed"]
        else:
            carb.log_error("Attempted to access active joint setting for a fixed dof")

    def get_max_effort(self, dof_name):
        if dof_name in self._active_dof_settings:
            return self._active_dof_settings[dof_name]["max_effort"]
        else:
            carb.log_error("Attempted to access active joint setting for a fixed dof")

    def get_joint_position(self, dof_name):
        if self.is_active(dof_name):
            return self.get_open_position(dof_name)
        else:
            return self.get_fixed_position(dof_name)

    def set_fixed_position(self, dof_name, position):
        if dof_name in self._fixed_dof_settings:
            self._fixed_dof_settings[dof_name]["fixed_position"] = position
        else:
            carb.log_error("Attempted to set fixed joint setting for an active dof")

    def set_open_position(self, dof_name, position):
        if dof_name in self._active_dof_settings:
            self._active_dof_settings[dof_name]["open_position"] = position
        else:
            carb.log_error("Attempted to set active joint setting for a fixed dof")

    def set_close_position(self, dof_name, position):
        if dof_name in self._active_dof_settings:
            self._active_dof_settings[dof_name]["close_position"] = position
        else:
            carb.log_error("Attempted to set active joint setting for a fixed dof")

    def set_max_speed(self, dof_name, max_speed):
        if dof_name in self._active_dof_settings:
            self._active_dof_settings[dof_name]["max_speed"] = max_speed
        else:
            carb.log_error("Attempted to set active joint setting for a fixed dof")

    def set_max_effort(self, dof_name, max_effort):
        if dof_name in self._active_dof_settings:
            self._active_dof_settings[dof_name]["max_effort"] = max_effort
        else:
            carb.log_error("Attempted to set active joint setting for a fixed dof")

    def set_active_dof(
        self, articulation, dof_name, open_position=None, close_position=None, max_speed=None, max_effort=None
    ):
        if dof_name in self._fixed_dof_settings:
            del self._fixed_dof_settings[dof_name]
        d = {}
        self._active_dof_settings[dof_name] = d

        dof_index = articulation.get_dof_index(dof_name)
        lower_limit = articulation.dof_properties["lower"][dof_index]
        upper_limit = articulation.dof_properties["upper"][dof_index]
        if max_effort is None:
            max_effort = articulation.dof_properties["maxEffort"][dof_index]
        joint_position = articulation.get_joint_positions()[dof_index]

        if open_position is not None:
            d["open_position"] = open_position
        else:
            d["open_position"] = joint_position

        if close_position is not None:
            d["close_position"] = close_position
        else:
            d["close_position"] = self._get_default_close_position(upper_limit, lower_limit, d["open_position"])

        if max_speed is not None:
            d["max_speed"] = max_speed
        else:
            d["max_speed"] = abs(d["open_position"] - d["close_position"])

        d["max_effort"] = max_effort

    def set_fixed_dof(self, articulation, dof_name, fixed_position=None):
        if dof_name in self._active_dof_settings:
            del self._active_dof_settings[dof_name]
        d = {}
        self._fixed_dof_settings[dof_name] = d

        dof_index = articulation.get_dof_index(dof_name)
        joint_position = articulation.get_joint_positions()[dof_index]

        if fixed_position is None:
            fixed_position = joint_position

        d["fixed_position"] = fixed_position
