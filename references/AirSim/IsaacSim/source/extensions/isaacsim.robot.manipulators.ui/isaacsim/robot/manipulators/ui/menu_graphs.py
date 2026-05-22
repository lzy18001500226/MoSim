# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import omni.graph.core as og
import omni.ui as ui
import omni.usd
import OmniGraphSchema
from isaacsim.core.utils.prims import get_all_matching_child_prims, get_prim_at_path
from isaacsim.core.utils.stage import get_next_free_path
from isaacsim.gui.components.callbacks import on_docs_link_clicked, on_open_IDE_clicked
from isaacsim.gui.components.style import get_style
from isaacsim.gui.components.widgets import ParamWidget, SelectPrimWidget
from numpy import pi as PI
from omni.kit.menu.utils import MenuHelperWindow
from omni.kit.notification_manager import NotificationStatus, post_notification
from omni.kit.window.extensions import SimpleCheckBox
from pxr import Usd, UsdPhysics

OG_DOCS_LINK = "https://docs.isaacsim.omniverse.nvidia.com/latest/omnigraph/omnigraph_shortcuts.html"


class ArticulationPositionWindow(MenuHelperWindow):
    def __init__(self):
        super().__init__("Articulation Position Controller", width=400, height=500)

        # Initialize parameters
        self._og_path = "/Graphs/Position_Controller"
        self._art_root_path = ""
        self._robot_prim_path = ""
        self._add_to_existing_graph = False
        self._num_dofs = None
        self._joint_names = []
        self._default_pos = []

        # build UI
        self._build_ui()

    def _build_ui(self):
        self._og_path = get_next_free_path(self._og_path, "")
        og_path_def = ParamWidget.FieldDef(
            name="og_path",
            label="Graph Path",
            type=ui.StringField,
            tooltip="Path to the graph on stage",
            default=self._og_path,
        )

        instructions = "Add Robot Prim. Press 'OK' to create graph. \n\n To move the joints, on the stage tree, highlight /World/Graphs/articulation_position_controller{_n}/JointCommandArray. \n\n Start simulation by pressing 'play', then change the joint angles in the Property Manager Tab -> Raw USD Properties\n\n NOTE: the articulation controller uses RADIANS, the usd properties (under the propert tabs) are in DEGREES"

        ## populate the popup window
        with self.frame:
            with ui.VStack(spacing=4):
                with ui.HStack(height=40):
                    ui.Label("Add to an existing graph?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._add_to_existing_graph)
                    SimpleCheckBox(self._add_to_existing_graph, self._on_use_existing_graph, model=cb)

                self.robot_prim_input = SelectPrimWidget(
                    label="Robot Prim",
                    default=self._robot_prim_path,
                    tooltip="the parent prim of the robot",
                )

                self.og_path_input = ParamWidget(field_def=og_path_def)
                ui.Spacer(height=2)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1), height=2)
                with ui.HStack():
                    ui.Label(
                        "Instructions:",
                        style_type_name_override="Label::label",
                        word_wrap=True,
                        width=ui.Percent(20),
                        alignment=ui.Alignment.LEFT_TOP,
                    )
                    with ui.ScrollingFrame(
                        height=180,
                        style_type_name_override="ScrollingFrame",
                        alignment=ui.Alignment.LEFT_TOP,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    ):
                        with ui.ZStack(style={"ZStack": {"margin": 10}}):
                            ui.Rectangle()
                            ui.Label(
                                instructions,
                                style_type_name_override="Label::label",
                                word_wrap=True,
                                alignment=ui.Alignment.LEFT_TOP,
                            )

                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1), height=2)
                ui.Spacer(height=2)
                with ui.HStack():
                    ui.Spacer(width=ui.Percent(10))
                    ui.Button("OK", height=40, width=ui.Percent(30), clicked_fn=self._on_ok)
                    ui.Spacer(width=ui.Percent(20))
                    ui.Button("Cancel", height=40, width=ui.Percent(30), clicked_fn=self._on_cancel)
                    ui.Spacer(width=ui.Percent(10))
                with ui.Frame(height=30):
                    with ui.VStack():
                        with ui.HStack():
                            ui.Label("Python Script for Graph Generation", width=ui.Percent(30))
                            ui.Button(
                                name="IconButton",
                                width=24,
                                height=24,
                                clicked_fn=lambda: on_open_IDE_clicked("", __file__),
                                style=get_style()["IconButton.Image::OpenConfig"],
                            )
                        with ui.HStack():
                            ui.Label("Documentations", width=0, word_wrap=True)
                            ui.Button(
                                name="IconButton",
                                width=24,
                                height=24,
                                clicked_fn=lambda: on_docs_link_clicked(OG_DOCS_LINK),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )
        return

    def make_graph(self):
        # stop simulation before adding the graph
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys

        # if creating a new graph. start with a blank graph with just a OnPlaybackTick node
        if not self._add_to_existing_graph:
            self._og_path = get_next_free_path(self._og_path, "")
            graph_handle = og.Controller.create_graph({"graph_path": self._og_path, "evaluator_name": "execution"})
            og.Controller.create_node(self._og_path + "/OnPlaybackTick", "omni.graph.action.OnPlaybackTick")
        else:
            graph_handle = og.get_graph_by_path(self._og_path)

        all_nodes = graph_handle.get_nodes()
        joint_command_array_node = None
        joint_command_array_name = "JointCommandArray"
        joint_names_array_node = None
        joint_names_array_name = "JointNameArray"
        art_controller_node = None
        art_controller_node_name = "ArticulationController"
        tick_node = None

        for node in all_nodes:
            node_path = node.get_prim_path()
            node_type = node.get_type_name()
            # find the tick node
            if node_type == "omni.graph.action.OnPlaybackTick" or node_type == "omni.graph.action.OnTick":
                tick_node = node_path

        # make sure joint_command and joint_names arrays will have unique names
        joint_command_array_base = self._og_path + "/JointCommandArray"
        joint_command_array_node = get_next_free_path(joint_command_array_base, "")
        joint_command_array_name = joint_command_array_node.split("/")[-1]
        joint_names_array_base = self._og_path + "/JointNameArray"
        joint_names_array_node = get_next_free_path(joint_names_array_base, "")
        joint_names_array_name = joint_names_array_node.split("/")[-1]
        art_controller_node_base = self._og_path + "/ArticulationController"
        art_controller_node = get_next_free_path(art_controller_node_base, "")
        art_controller_node_name = art_controller_node.split("/")[-1]

        # Add the nodes, set values and connect them
        og.Controller.edit(
            graph_handle,
            {
                keys.CREATE_NODES: [
                    (joint_command_array_name, "omni.graph.nodes.ConstructArray"),
                    (art_controller_node_name, "isaacsim.core.nodes.IsaacArticulationController"),
                    (joint_names_array_name, "omni.graph.nodes.ConstructArray"),
                ],
                keys.CREATE_ATTRIBUTES: [
                    # Create additional input attributes for joint command array
                    *[
                        (joint_command_array_name + ".inputs:input" + str(i), "double")
                        for i in range(1, self._num_dofs)
                    ],
                    # Create additional input attributes for joint names array
                    *[(joint_names_array_name + ".inputs:input" + str(i), "token") for i in range(1, self._num_dofs)],
                ],
                keys.SET_VALUES: [
                    (joint_command_array_name + ".inputs:arrayType", "double[]"),
                    (joint_command_array_name + ".inputs:arraySize", self._num_dofs),
                    (art_controller_node_name + ".inputs:robotPath", self._art_root_path),
                    (joint_names_array_name + ".inputs:arrayType", "token[]"),
                    (joint_names_array_name + ".inputs:arraySize", self._num_dofs),
                    *[
                        (joint_command_array_name + ".inputs:input" + str(i), self._default_pos[i])
                        for i in range(self._num_dofs)
                    ],
                    *[
                        (joint_names_array_name + ".inputs:input" + str(i), self._joint_names[i])
                        for i in range(self._num_dofs)
                    ],
                ],
                keys.CONNECT: [
                    (tick_node + ".outputs:tick", art_controller_node_name + ".inputs:execIn"),
                    (joint_command_array_name + ".outputs:array", art_controller_node_name + ".inputs:positionCommand"),
                    (joint_names_array_name + ".outputs:array", art_controller_node_name + ".inputs:jointNames"),
                ],
            },
        )

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()
        self._robot_prim_path = self.robot_prim_input.get_value()

        param_check = self._check_params()
        if param_check:
            self.make_graph()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _check_params(self):
        stage = omni.usd.get_context().get_stage()

        if self._add_to_existing_graph:
            # make sure the "existing" graph exist
            og_prim = stage.GetPrimAtPath(self._og_path)
            if og_prim.IsValid() and og_prim.IsA(OmniGraphSchema.OmniGraph):
                pass
            else:
                msg = self._og_path + " is not an existing graph, check the og path"
                post_notification(msg, status=NotificationStatus.WARNING)
                return False

        # from the robot parent prim, find the prim that contains the articulation root API
        art_root_prim = get_all_matching_child_prims(
            self._robot_prim_path, predicate=lambda path: get_prim_at_path(path).HasAPI(UsdPhysics.ArticulationRootAPI)
        )
        if len(art_root_prim) == 0:
            msg = "No articulation root prim found under robot parent prim, check if you need to give a different prim for robot"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        if len(art_root_prim) > 1:
            msg = "More than one articulation root prim found under robot parent prim, check if you need to give a different prim for robot"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        self._art_root_path = art_root_prim[0].GetPath().pathString

        ## get the joints by traversing through the robot prim

        self._joint_names = []
        self._default_vel = []

        robot_prim = stage.GetPrimAtPath(self._robot_prim_path)
        for prim in Usd.PrimRange(robot_prim, Usd.TraverseInstanceProxies()):
            if prim.IsA(UsdPhysics.RevoluteJoint) and prim.HasAPI(UsdPhysics.DriveAPI):
                self._joint_names.append(os.path.basename(prim.GetPath().pathString))
                joint_drive = UsdPhysics.DriveAPI.Get(prim, "angular")
                default_pos_deg = joint_drive.GetTargetPositionAttr().Get()
                self._default_pos.append(
                    default_pos_deg * PI / 180
                )  # USD property is in degrees, PhysX (articulation controller) is in radians
            elif prim.IsA(UsdPhysics.PrismaticJoint) and prim.HasAPI(UsdPhysics.DriveAPI):
                self._joint_names.append(os.path.basename(prim.GetPath().pathString))
                joint_drive = UsdPhysics.DriveAPI.Get(prim, "linear")
                self._default_pos.append(joint_drive.GetTargetPositionAttr().Get())
        self._num_dofs = len(self._joint_names)

        if self._num_dofs == 0:
            # this may not catch every case of the wrong art_root prim. such as when only a subset of the joints are under the root prim, hence flash a info about how many joints are found
            msg = "No valid joints found under the given articulation root prim, check if you need to give a different prim for robot root"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False

        msg = (
            "Found "
            + str(self._num_dofs)
            + " joints under the given articulation root prim. \nIf different than expected, check if need to give a different prim for robot root"
        )
        post_notification(msg, status=NotificationStatus.INFO)

        return True

    def _on_cancel(self):
        self.visible = False

    def _on_use_existing_graph(self, check_state):
        self._add_to_existing_graph = check_state


class ArticulationVelocityWindow(MenuHelperWindow):
    def __init__(self):
        super().__init__("Articulation Velocity Controller", width=500, height=470)

        # Initialize parameters
        self._og_path = "/Graphs/Velocity_Controller"
        self._art_root_path = ""
        self._robot_prim_path = ""
        self._add_to_existing_graph = False
        self._num_dofs = None
        self._joint_names = []
        self._default_vel = []

        # build UI
        self._build_ui()

    def _build_ui(self):
        self._og_path = get_next_free_path(self._og_path, "")
        og_path_def = ParamWidget.FieldDef(
            name="og_path",
            label="Graph Path",
            type=ui.StringField,
            default=self._og_path,
            tooltip="Path to the graph on stage",
        )

        instructions = "Add Robot Prim.Press 'OK' to create graph. \n\n To move the joints, on the stage tree, highlight /World/Graphs/articulation_velocity_controller{_n}/JointCommandArray, \n\n Start simulation by pressing 'play', then change the joint angles in the Property Manager Tab -> Raw USD Properties. \n\n NOTE: the articulation controller uses RADIANS, the usd properties (under the propert tabs) are in DEGREES"
        ## populate the popup window
        with self.frame:
            with ui.VStack(spacing=4):
                with ui.HStack(height=40):
                    ui.Label("Add to an existing graph?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._add_to_existing_graph)
                    SimpleCheckBox(self._add_to_existing_graph, self._on_use_existing_graph, model=cb)

                self.robot_prim_input = SelectPrimWidget(
                    label="Robot Prim",
                    default=self._robot_prim_path,
                    tooltip="the outer most prim of the robot",
                )
                self.og_path_input = ParamWidget(field_def=og_path_def)
                ui.Spacer(height=2)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1), height=2)
                with ui.HStack():
                    ui.Label(
                        "Instructions:",
                        style_type_name_override="Label::label",
                        word_wrap=True,
                        width=ui.Percent(20),
                        alignment=ui.Alignment.LEFT_TOP,
                    )
                    with ui.ScrollingFrame(
                        height=180,
                        style_type_name_override="ScrollingFrame",
                        alignment=ui.Alignment.LEFT_TOP,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    ):
                        with ui.ZStack(style={"ZStack": {"margin": 10}}):
                            ui.Rectangle()
                            ui.Label(
                                instructions,
                                style_type_name_override="Label::label",
                                word_wrap=True,
                                alignment=ui.Alignment.LEFT_TOP,
                            )

                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1), height=2)
                ui.Spacer(height=2)
                with ui.HStack():
                    ui.Spacer(width=ui.Percent(10))
                    ui.Button("OK", height=40, width=ui.Percent(30), clicked_fn=self._on_ok)
                    ui.Spacer(width=ui.Percent(20))
                    ui.Button("Cancel", height=40, width=ui.Percent(30), clicked_fn=self._on_cancel)
                    ui.Spacer(width=ui.Percent(10))
                with ui.Frame(height=30):
                    with ui.VStack():
                        with ui.HStack():
                            ui.Label("Python Script for Graph Generation", width=ui.Percent(30))
                            ui.Button(
                                name="IconButton",
                                width=24,
                                height=24,
                                clicked_fn=lambda: on_open_IDE_clicked("", __file__),
                                style=get_style()["IconButton.Image::OpenConfig"],
                            )
                        with ui.HStack():
                            ui.Label("Documentations", width=0, word_wrap=True)
                            ui.Button(
                                name="IconButton",
                                width=24,
                                height=24,
                                clicked_fn=lambda: on_docs_link_clicked(OG_DOCS_LINK),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )

        return

    def make_graph(self):
        # stop simulation before adding the graph
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys

        # if creating a new graph. start with a blank graph with just a OnPlaybackTick node
        if not self._add_to_existing_graph:
            self._og_path = get_next_free_path(self._og_path, "")
            graph_handle = og.Controller.create_graph({"graph_path": self._og_path, "evaluator_name": "execution"})
            og.Controller.create_node(self._og_path + "/OnPlaybackTick", "omni.graph.action.OnPlaybackTick")
        else:
            graph_handle = og.get_graph_by_path(self._og_path)

        all_nodes = graph_handle.get_nodes()
        joint_command_array_node = None
        joint_command_array_name = "JointCommandArray"
        joint_names_array_node = None
        joint_names_array_name = "JointNameArray"
        art_controller_node = None
        art_controller_node_name = "ArticulationController"
        tick_node = None

        for node in all_nodes:
            node_path = node.get_prim_path()
            node_type = node.get_type_name()
            # find the tick node
            if node_type == "omni.graph.action.OnPlaybackTick" or node_type == "omni.graph.action.OnTick":
                tick_node = node_path

        # make sure joint_command and joint_names arrays will have unique names
        joint_command_array_base = self._og_path + "/JointCommandArray"
        joint_command_array_node = get_next_free_path(joint_command_array_base, "")
        joint_command_array_name = joint_command_array_node.split("/")[-1]
        joint_names_array_base = self._og_path + "/JointNameArray"
        joint_names_array_node = get_next_free_path(joint_names_array_base, "")
        joint_names_array_name = joint_names_array_node.split("/")[-1]
        art_controller_node_base = self._og_path + "/ArticulationController"
        art_controller_node = get_next_free_path(art_controller_node_base, "")
        art_controller_node_name = art_controller_node.split("/")[-1]

        # Add the nodes, set values and connect them
        og.Controller.edit(
            graph_handle,
            {
                keys.CREATE_NODES: [
                    (joint_command_array_name, "omni.graph.nodes.ConstructArray"),
                    (art_controller_node_name, "isaacsim.core.nodes.IsaacArticulationController"),
                    (joint_names_array_name, "omni.graph.nodes.ConstructArray"),
                ],
                keys.CREATE_ATTRIBUTES: [
                    # Create additional input attributes for joint command array
                    *[
                        (joint_command_array_name + ".inputs:input" + str(i), "double")
                        for i in range(1, self._num_dofs)
                    ],
                    # Create additional input attributes for joint names array
                    *[(joint_names_array_name + ".inputs:input" + str(i), "token") for i in range(1, self._num_dofs)],
                ],
                keys.SET_VALUES: [
                    (joint_command_array_name + ".inputs:arrayType", "double[]"),
                    (joint_command_array_name + ".inputs:arraySize", self._num_dofs),
                    (art_controller_node_name + ".inputs:targetPrim", self._art_root_path),
                    (joint_names_array_name + ".inputs:arrayType", "token[]"),
                    (joint_names_array_name + ".inputs:arraySize", self._num_dofs),
                    # Set the default values for all inputs
                    *[
                        (joint_command_array_name + ".inputs:input" + str(i), self._default_vel[i])
                        for i in range(self._num_dofs)
                    ],
                    *[
                        (joint_names_array_name + ".inputs:input" + str(i), self._joint_names[i])
                        for i in range(self._num_dofs)
                    ],
                ],
                keys.CONNECT: [
                    (tick_node + ".outputs:tick", art_controller_node_name + ".inputs:execIn"),
                    (joint_command_array_name + ".outputs:array", art_controller_node_name + ".inputs:velocityCommand"),
                    (joint_names_array_name + ".outputs:array", art_controller_node_name + ".inputs:jointNames"),
                ],
            },
        )

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()
        self._robot_prim_path = self.robot_prim_input.get_value()

        param_check = self._check_params()
        if param_check:
            self.make_graph()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _check_params(self):
        stage = omni.usd.get_context().get_stage()

        if self._add_to_existing_graph:
            # make sure the "existing" graph exist
            og_prim = stage.GetPrimAtPath(self._og_path)
            if og_prim.IsValid() and og_prim.IsA(OmniGraphSchema.OmniGraph):
                pass
            else:
                msg = self._og_path + " is not an existing graph, check the og path"
                post_notification(msg, status=NotificationStatus.WARNING)
                return False

        # from the robot parent prim, find the prim that contains the articulation root API
        art_root_prim = get_all_matching_child_prims(
            self._robot_prim_path, predicate=lambda path: get_prim_at_path(path).HasAPI(UsdPhysics.ArticulationRootAPI)
        )
        if len(art_root_prim) == 0:
            msg = "No articulation root prim found under robot parent prim, check if you need to give a different prim for robot"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        if len(art_root_prim) > 1:
            msg = "More than one articulation root prim found under robot parent prim, check if you need to give a different prim for robot"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        self._art_root_path = art_root_prim[0].GetPath().pathString

        ## get the joints by traversing through the robot/articulation prim
        ## TODO: should we check possibilities that the subsequent joints are not under the root prim on stage (but should be discoverable under the articulation chain)
        robot_prim = stage.GetPrimAtPath(self._robot_prim_path)
        self._joint_names = []
        self._default_vel = []
        for prim in Usd.PrimRange(robot_prim, Usd.TraverseInstanceProxies()):
            if prim.IsA(UsdPhysics.RevoluteJoint) and prim.HasAPI(UsdPhysics.DriveAPI):
                self._joint_names.append(os.path.basename(prim.GetPath().pathString))
                joint_drive = UsdPhysics.DriveAPI.Get(prim, "angular")
                default_vel_deg = joint_drive.GetTargetVelocityAttr().Get()
                self._default_vel.append(
                    default_vel_deg * PI / 180
                )  # USD property is in degrees, PhysX (articulation controller) is in radians
            elif prim.IsA(UsdPhysics.PrismaticJoint) and prim.HasAPI(UsdPhysics.DriveAPI):
                self._joint_names.append(os.path.basename(prim.GetPath().pathString))
                joint_drive = UsdPhysics.DriveAPI.Get(prim, "linear")
                self._default_vel.append(joint_drive.GetTargetVelocityAttr().Get())
        self._num_dofs = len(self._joint_names)

        if self._num_dofs == 0:
            msg = "No valid joints found under the given articulation root prim, check if you need to give a different prim for robot root"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False

        return True

    def _on_cancel(self):
        self.visible = False

    def _on_use_existing_graph(self, check_state):
        self._add_to_existing_graph = check_state


class GripperWindow(MenuHelperWindow):
    def __init__(self):
        super().__init__("Gripper Controller", width=400, height=550)

        self._og_path = "/Graphs/Gripper_Controller"
        self._art_root_path = ""
        self._parent_robot_path = ""
        self._gripper_root_path = ""
        self._add_to_existing_graph = False
        self._use_keyboard = False
        self._dof_actuation = None
        self._joint_names = ""
        self._open_position = None
        self._close_position = None
        self._speed = None

        # build UI
        self._build_ui()

    def _build_ui(self):

        self._og_path = get_next_free_path(self._og_path, "")
        og_path_def = ParamWidget.FieldDef(
            name="og_path",
            label="Graph Path",
            type=ui.StringField,
            default=self._og_path,
            tooltip="Path to the graph on stage",
        )
        speed_def = ParamWidget.FieldDef(
            name="gripper_speed",
            label="Gripper Speed",
            type=ui.FloatField,
            default=self._speed,
            tooltip="Distance per frame in meters",
        )
        joint_names_def = ParamWidget.FieldDef(
            name="joint_names",
            label="Gripper Joint Names",
            type=ui.StringField,
            default=self._joint_names,
            tooltip="Names of the joints that are included in the gripper, REQUIRED if not all joints inside the articulation are gripper joints",
        )
        open_position_def = ParamWidget.FieldDef(
            name="open_position",
            label="Open Position Limit",
            type=ui.FloatField,
            default=self._open_position,
            tooltip="the joint position that indicates open. Unit: meter or radian",
        )
        close_position_def = ParamWidget.FieldDef(
            name="close_position",
            label="Close Position Limit",
            type=ui.FloatField,
            default=self._close_position,
            tooltip="the joint position that indicates close. unit: meter or radian)",
        )

        ## populate the popup window
        with self.frame:
            with ui.VStack(spacing=4):
                with ui.HStack(height=40):
                    ui.Label("Add to an existing graph?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._add_to_existing_graph)
                    SimpleCheckBox(self._add_to_existing_graph, self._on_use_existing_graph, model=cb)

                self.parent_robot_input = SelectPrimWidget(
                    label="Parent Robot",
                    default=self._art_root_path,
                    tooltip="the parent robot prim. one and only one articulation root prim should be on this prim, or is a child of this prim",
                )
                self.gripper_root_input = SelectPrimWidget(
                    label="Gripper Root Prim",
                    default=self._gripper_root_path,
                    tooltip="the prim that contains the gripper joints",
                )
                self.og_path_input = ParamWidget(field_def=og_path_def)
                self.speed_input = ParamWidget(field_def=speed_def)
                ui.Spacer(height=2)
                ui.Label(
                    "If not all actuated joints are gripper joints, list all gripper joint names separated by a comma",
                    height=30,
                    width=ui.Percent(80),
                    style_type_name_override="Label.Label",
                    style={"font_size": 12, "color": 0xFFA8A8A8},
                    word_wrap=True,
                )
                self.joint_names_input = ParamWidget(field_def=joint_names_def)
                ui.Spacer(height=2)

                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1), height=2)
                ui.Label(
                    "OPTIONAL (Default to joint limits if not given)",
                    height=30,
                    style_type_name_override="Label.Label",
                    style={"font_size": 18, "color": 0xFFA8A8A8},
                )
                ui.Label(
                    "Only uniform joint limit (and speed) are supported in this popup, update the generated omnigraph if need finger-specific joint limits/speed",
                    height=30,
                    width=ui.Percent(80),
                    style_type_name_override="Label.Label",
                    style={"font_size": 12, "color": 0xFFA8A8A8},
                    word_wrap=True,
                )
                self.open_position_input = ParamWidget(field_def=open_position_def)
                self.close_position_input = ParamWidget(field_def=close_position_def)
                ui.Spacer(height=5)
                ui.Line(style={"color": 0x338A8777}, width=ui.Fraction(1), height=2)
                with ui.HStack():
                    ui.Label(
                        "Use Keyboard Control", width=ui.Percent(30), word_wrap=False, tooltip="O-open, C-close, N-stop"
                    )
                    cb = ui.SimpleBoolModel(default_value=self._use_keyboard)
                    SimpleCheckBox(self._use_keyboard, self._on_checked_box, model=cb)
                with ui.HStack():
                    ui.Spacer(width=ui.Percent(10))
                    ui.Button("OK", height=40, width=ui.Percent(30), clicked_fn=self._on_ok)
                    ui.Spacer(width=ui.Percent(20))
                    ui.Button("Cancel", height=40, width=ui.Percent(30), clicked_fn=self._on_cancel)
                    ui.Spacer(width=ui.Percent(10))
                with ui.Frame(height=30):
                    with ui.VStack():
                        with ui.HStack():
                            ui.Label("Python Script for Graph Generation", width=0)
                            ui.Button(
                                name="IconButton",
                                width=24,
                                height=24,
                                clicked_fn=lambda: on_open_IDE_clicked("", __file__),
                                style=get_style()["IconButton.Image::OpenConfig"],
                            )
                        with ui.HStack():
                            ui.Label("Documentations", width=0, word_wrap=True)
                            ui.Button(
                                name="IconButton",
                                width=24,
                                height=24,
                                clicked_fn=lambda: on_docs_link_clicked(OG_DOCS_LINK),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )

        return

    def make_graph(self):

        # stop physics before adding graphs
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys

        # if adding a new graph, start with a blank graph with just a OnPlaybackTick node
        if not self._add_to_existing_graph:
            self._og_path = get_next_free_path(self._og_path, "")
            graph_handle = og.Controller.create_graph({"graph_path": self._og_path, "evaluator_name": "execution"})
            og.Controller.create_node(self._og_path + "/OnPlaybackTick", "omni.graph.action.OnPlaybackTick")
        else:
            graph_handle = og.get_graph_by_path(self._og_path)

        all_nodes = graph_handle.get_nodes()
        tick_node = None

        for node in all_nodes:
            node_path = node.get_prim_path()
            node_type = node.get_type_name()
            # find the tick node
            if node_type == "omni.graph.action.OnPlaybackTick" or node_type == "omni.graph.action.OnTick":
                tick_node = node_path

        # the body of the graph
        og.Controller.edit(
            graph_handle,
            {
                keys.CREATE_NODES: [
                    ("GripperController", "isaacsim.robot.manipulators.IsaacGripperController"),
                    ("OpenPositionArray", "omni.graph.nodes.ConstructArray"),
                    ("ClosePositionArray", "omni.graph.nodes.ConstructArray"),
                    ("GripperSpeedArray", "omni.graph.nodes.ConstructArray"),
                    ("OpenJointLimit", "omni.graph.nodes.ConstantDouble"),
                    ("CloseJointLimit", "omni.graph.nodes.ConstantDouble"),
                    ("Speed", "omni.graph.nodes.ConstantDouble"),
                ],
                keys.SET_VALUES: [
                    ("GripperController.inputs:articulationRootPrim", self._art_root_path),
                    ("GripperController.inputs:gripperPrim", self._gripper_root_path),
                    ("Speed.inputs:value", self._speed),
                    ("OpenJointLimit.inputs:value", self._open_position),
                    ("CloseJointLimit.inputs:value", self._close_position),
                ],
                keys.CONNECT: [
                    (tick_node + ".outputs:tick", "GripperController.inputs:execIn"),
                    ("OpenJointLimit.inputs:value", "OpenPositionArray.inputs:input0"),
                    ("CloseJointLimit.inputs:value", "ClosePositionArray.inputs:input0"),
                    ("Speed.inputs:value", "GripperSpeedArray.inputs:input0"),
                    ("OpenPositionArray.outputs:array", "GripperController.inputs:openPosition"),
                    ("ClosePositionArray.outputs:array", "GripperController.inputs:closePosition"),
                    ("GripperSpeedArray.outputs:array", "GripperController.inputs:gripperSpeed"),
                ],
            },
        )

        # if user put in joint names:
        if self._joint_names:
            n_joints = len(self._joint_names)

            # Prepare all operations for a single edit call
            create_nodes = [("ArrayJointNames", "omni.graph.nodes.ConstructArray")]
            create_attributes = [
                # Create additional input attributes for array node (for i > 0)
                *[(f"ArrayJointNames.inputs:input{i}", "token") for i in range(1, n_joints)]
            ]
            set_values = [
                ("ArrayJointNames.inputs:arrayType", "token[]"),
                ("ArrayJointNames.inputs:arraySize", n_joints),
            ]
            create_connections = []

            # Create joint name nodes and their connections
            for i in range(n_joints):
                node_name = f"JointName{i}"
                joint_name = self._joint_names[i]
                create_nodes.append((node_name, "omni.graph.nodes.ConstantToken"))
                set_values.append((f"{node_name}.inputs:value", joint_name))

                # Connection from joint name node to array
                create_connections.append(
                    (f"{self._og_path}/{node_name}.inputs:value", f"{self._og_path}/ArrayJointNames.inputs:input{i}")
                )

            # Connection from array to gripper controller
            create_connections.append(
                (
                    f"{self._og_path}/ArrayJointNames.outputs:array",
                    f"{self._og_path}/GripperController.inputs:jointNames",
                )
            )

            # Execute all operations in a single edit call
            og.Controller.edit(
                graph_handle,
                {
                    keys.CREATE_NODES: create_nodes,
                    keys.CREATE_ATTRIBUTES: create_attributes,
                    keys.SET_VALUES: set_values,
                    keys.CONNECT: create_connections,
                },
            )
        else:
            print("defaulting to move all joints in the robot")

        # if user wants to use keyboard input
        if self._use_keyboard:
            print("using keyboard input to open/close gripper")
            og.Controller.edit(
                graph_handle,
                {
                    keys.CREATE_NODES: [
                        ("Open", "omni.graph.action.OnKeyboardInput"),
                        ("Close", "omni.graph.action.OnKeyboardInput"),
                        ("Stop", "omni.graph.action.OnKeyboardInput"),
                    ],
                    keys.SET_VALUES: [
                        ("Open.inputs:keyIn", "O"),
                        ("Close.inputs:keyIn", "C"),
                        ("Stop.inputs:keyIn", "N"),
                    ],
                },
            )

            og.Controller.connect(
                og.Controller.attribute(self._og_path + "/Open.outputs:pressed"),
                og.Controller.attribute(self._og_path + "/GripperController.inputs:open"),
            )

            og.Controller.connect(
                og.Controller.attribute(self._og_path + "/Close.outputs:pressed"),
                og.Controller.attribute(self._og_path + "/GripperController.inputs:close"),
            )

            og.Controller.connect(
                og.Controller.attribute(self._og_path + "/Stop.outputs:pressed"),
                og.Controller.attribute(self._og_path + "/GripperController.inputs:stop"),
            )

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()
        self._parent_robot_path = self.parent_robot_input.get_value()
        self._gripper_root_path = self.gripper_root_input.get_value()

        self._speed = self.speed_input.get_value()
        self._open_position = self.open_position_input.get_value()
        self._close_position = self.close_position_input.get_value()
        self._joint_names = self.joint_names_input.get_value()

        param_check = self._check_params()
        if param_check:
            self.make_graph()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _check_params(self):
        # turn joint names from tokens to a list
        self._joint_names = [item.strip() for item in self._joint_names.split(",")]

        # make sure the "existing" graph exist, and that there isn't already a gripper controller in it
        stage = omni.usd.get_context().get_stage()
        if self._add_to_existing_graph:
            og_prim = stage.GetPrimAtPath(self._og_path)
            if og_prim.IsValid() and og_prim.IsA(OmniGraphSchema.OmniGraph):
                graph_handle = og.get_graph_by_path(self._og_path)
                all_nodes = graph_handle.get_nodes()
                for node in all_nodes:
                    node_type = node.get_type_name()
                    # find the tick node
                    if node_type == "isaacsim.robot.manipulators.IsaacGripperController":
                        msg = "There already exist an GripperController in given graph. Use a different graph or manually add multiple gripper controllers to the same graph"
                        post_notification(msg, status=NotificationStatus.WARNING)
                        return False
            else:
                msg = self._og_path + " is not an existing graph, check the og path"
                post_notification(msg, status=NotificationStatus.WARNING)
                return False

        # from the robot parent prim, find the prim that contains the articulation root API
        art_root_prim = get_all_matching_child_prims(
            self._parent_robot_path,
            predicate=lambda path: get_prim_at_path(path).HasAPI(UsdPhysics.ArticulationRootAPI),
        )
        if len(art_root_prim) == 0:
            msg = "No articulation root prim found under robot parent prim, check if you need to give a different prim for robot"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        if len(art_root_prim) > 1:
            msg = "More than one articulation root prim found under robot parent prim, check if you need to give a different prim for robot"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        self._art_root_path = art_root_prim[0].GetPath().pathString

        return True

    def _on_cancel(self):
        self.visible = False

    def _on_checked_box(self, check_state):
        self._use_keyboard = check_state
        print(f"using keyboard set to {self._use_keyboard}\n O-open, C-close, N-stop")

    def _on_use_existing_graph(self, check_state):
        self._add_to_existing_graph = check_state
