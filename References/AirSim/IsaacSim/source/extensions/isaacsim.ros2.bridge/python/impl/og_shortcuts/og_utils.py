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


from pathlib import Path

import omni.graph.core as og
import omni.ui as ui
import omni.usd
import OmniGraphSchema
from isaacsim.core.utils.stage import get_next_free_path
from isaacsim.gui.components.callbacks import on_docs_link_clicked, on_open_IDE_clicked
from isaacsim.gui.components.style import get_style
from isaacsim.gui.components.ui_utils import dropdown_builder
from isaacsim.gui.components.widgets import ParamWidget, SelectPrimWidget
from omni.kit.menu.utils import MenuHelperWindow
from omni.kit.notification_manager import NotificationStatus, post_notification
from omni.kit.window.extensions import SimpleCheckBox
from pxr import Sdf


class Ros2ClockGraph(MenuHelperWindow):
    def __init__(self):
        super().__init__("ROS2 Clock Graph", width=300, height=150)
        self._og_path = "/Graph/ROS_Clock"

        # build UI
        self._build_ui()

    def make_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(
            {"graph_path": self._og_path, "evaluator_name": "execution"},
            {
                keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                    ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
                    ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                ],
                keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
                    ("Context.outputs:context", "PublishClock.inputs:context"),
                    ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
                ],
                keys.SET_VALUES: [
                    ("ReadSimTime.inputs:resetOnStop", False),
                ],
            },
        )

    def _build_ui(self):
        default_og_path = "/Graph/ROS_Clock"
        og_path_def = ParamWidget.FieldDef(
            name="og_path", label="Graph Path", type=ui.StringField, default=default_og_path
        )

        with self.frame:
            with ui.VStack(spacing=4):
                self.og_path_input = ParamWidget(field_def=og_path_def)
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
                                clicked_fn=lambda: on_docs_link_clicked(
                                    "https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_clock.html#graph-shortcut"
                                ),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )

        return

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()

        param_check = self._check_params()
        if param_check:
            self.make_graph()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _on_cancel(self):
        self.visible = False

    def _check_params(self):
        stage = omni.usd.get_context().get_stage()
        og_prim = stage.GetPrimAtPath(self._og_path)
        if og_prim.IsValid() and og_prim.IsA(OmniGraphSchema.OmniGraph):
            msg = self._og_path + "already exist. Delete the existing clock graph or change the graph path"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        else:
            pass

        return True


class Ros2GenericPubGraph(MenuHelperWindow):
    def __init__(self):
        super().__init__("ROS2 Generic Publisher Graph", width=350, height=180)
        self._og_path = "/Graph/ROS_GenericPub"
        self._dropdown_model = None
        self._dropdown_operations_list = [
            ("Publish RTF as Float32", self.make_rtf_graph),
            ("Publish Bool", self.make_bool_graph),
            ("Publish Int64", self.make_int64_graph),
            ("Publish String", self.make_string_graph),
        ]

        # build UI
        self._build_ui()

    def make_rtf_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(
            {"graph_path": self._og_path, "evaluator_name": "execution"},
            {
                keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("GenericPublisher", "isaacsim.ros2.bridge.ROS2Publisher"),
                    ("RTF", "isaacsim.core.nodes.IsaacRealTimeFactor"),
                    ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                ],
                keys.SET_VALUES: [
                    ("GenericPublisher.inputs:messageName", "Float32"),
                    ("GenericPublisher.inputs:messagePackage", "std_msgs"),
                    ("GenericPublisher.inputs:messageSubfolder", "msg"),
                ],
                keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "GenericPublisher.inputs:execIn"),
                    ("Context.outputs:context", "GenericPublisher.inputs:context"),
                ],
            },
        )

        # Have a separate connection since we need GenericPublisher to run least one frame for it generate the input fields
        og.Controller.connect(
            og.Controller.attribute(self._og_path + "/RTF.outputs:rtf"),
            og.Controller.attribute(self._og_path + "/GenericPublisher.inputs:data"),
        )

    def make_bool_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(
            {"graph_path": self._og_path, "evaluator_name": "execution"},
            {
                keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("GenericPublisher", "isaacsim.ros2.bridge.ROS2Publisher"),
                    ("ConstBool", "omni.graph.nodes.ConstantBool"),
                    ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                ],
                keys.SET_VALUES: [
                    ("GenericPublisher.inputs:messageName", "Bool"),
                    ("GenericPublisher.inputs:messagePackage", "std_msgs"),
                    ("GenericPublisher.inputs:messageSubfolder", "msg"),
                    ("ConstBool.inputs:value", True),
                ],
                keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "GenericPublisher.inputs:execIn"),
                    ("Context.outputs:context", "GenericPublisher.inputs:context"),
                ],
            },
        )

        # Have a separate connection since we need GenericPublisher to run least one frame for it generate the input fields
        og.Controller.connect(
            og.Controller.attribute(self._og_path + "/ConstBool.inputs:value"),
            og.Controller.attribute(self._og_path + "/GenericPublisher.inputs:data"),
        )

    def make_int64_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(
            {"graph_path": self._og_path, "evaluator_name": "execution"},
            {
                keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("GenericPublisher", "isaacsim.ros2.bridge.ROS2Publisher"),
                    ("ConstInt", "omni.graph.nodes.ConstantInt64"),
                    ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                ],
                keys.SET_VALUES: [
                    ("GenericPublisher.inputs:messageName", "Int64"),
                    ("GenericPublisher.inputs:messagePackage", "std_msgs"),
                    ("GenericPublisher.inputs:messageSubfolder", "msg"),
                    ("ConstInt.inputs:value", 42),
                ],
                keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "GenericPublisher.inputs:execIn"),
                    ("Context.outputs:context", "GenericPublisher.inputs:context"),
                ],
            },
        )

        # Have a separate connection since we need GenericPublisher to run least one frame for it generate the input fields
        og.Controller.connect(
            og.Controller.attribute(self._og_path + "/ConstInt.inputs:value"),
            og.Controller.attribute(self._og_path + "/GenericPublisher.inputs:data"),
        )

    def make_string_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(
            {"graph_path": self._og_path, "evaluator_name": "execution"},
            {
                keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("GenericPublisher", "isaacsim.ros2.bridge.ROS2Publisher"),
                    ("ConstToken", "omni.graph.nodes.ConstantToken"),
                    ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                ],
                keys.SET_VALUES: [
                    ("GenericPublisher.inputs:messageName", "String"),
                    ("GenericPublisher.inputs:messagePackage", "std_msgs"),
                    ("GenericPublisher.inputs:messageSubfolder", "msg"),
                    ("ConstToken.inputs:value", "Hello from Isaac Sim!"),
                ],
                keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "GenericPublisher.inputs:execIn"),
                    ("Context.outputs:context", "GenericPublisher.inputs:context"),
                ],
            },
        )

        # Have a separate connection since we need GenericPublisher to run least one frame for it generate the input fields
        og.Controller.connect(
            og.Controller.attribute(self._og_path + "/ConstToken.inputs:value"),
            og.Controller.attribute(self._og_path + "/GenericPublisher.inputs:data"),
        )

    def _build_ui(self):
        default_og_path = "/Graph/ROS_GenericPub"
        og_path_def = ParamWidget.FieldDef(
            name="og_path", label="Graph Path", type=ui.StringField, default=default_og_path
        )

        with self.frame:
            with ui.VStack(spacing=4):
                self.og_path_input = ParamWidget(field_def=og_path_def)

                self._dropdown_model = dropdown_builder(
                    label="Generic Publisher Graph",
                    items=[names for (names, _) in self._dropdown_operations_list],
                    tooltip="Select an example generic publisher graph",
                )
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
                                clicked_fn=lambda: on_docs_link_clicked(
                                    "https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_generic_publisher_subscriber.html"
                                ),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )
        return

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()

        param_check = self._check_params()
        if param_check:
            # self.make_graph()
            self._dropdown_operations_list[self._dropdown_model.get_item_value_model().as_int][1]()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _on_cancel(self):
        self.visible = False

    def _check_params(self):
        stage = omni.usd.get_context().get_stage()
        og_prim = stage.GetPrimAtPath(self._og_path)
        if og_prim.IsValid() and og_prim.IsA(OmniGraphSchema.OmniGraph):
            msg = self._og_path + "already exist. Delete the existing clock graph or change the graph path"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False
        else:
            pass

        return True


class Ros2JointStatesGraph(MenuHelperWindow):
    def __init__(self):
        super().__init__("ROS2 Joint States Graph", width=450, height=350)
        self._og_path = "/Graph/ROS_JointStates"
        self._node_namespace = ""
        self._art_root_path = ""
        self._pub_topic = "/joint_states"
        self._sub_topic = "/joint_command"
        self._add_to_existing_graph = False
        self._publisher = False
        self._subscriber = False
        self._sub_move_robot = True  # does subscriber feeds into an articulation node to move the robot

        # build UI
        self._build_ui()

    def make_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys

        # if starting from a new graph, start it with just a tick,context, and sim_time node, the rest is the same for adding to exsiting graph
        if not self._add_to_existing_graph:
            self._og_path = get_next_free_path(self._og_path, "")
            (graph_handle, nodes, _, _) = og.Controller.edit(
                {"graph_path": self._og_path, "evaluator_name": "execution"},
                {
                    keys.CREATE_NODES: [
                        ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                        ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                        ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                    ],
                    keys.SET_VALUES: [
                        ("ReadSimTime.inputs:resetOnStop", False),
                    ],
                },
            )
        else:
            graph_handle = og.get_graph_by_path(self._og_path)

        # to an existin graph
        # traverse through the graph
        all_nodes = graph_handle.get_nodes()
        js_pub_node_name = "PublisherJointState"
        js_sub_node_name = "SubscriberJointState"
        art_node_name = "ArticulationController"
        tick_node = None
        context_node = None
        sim_time_node = None
        for node in all_nodes:
            node_path = node.get_prim_path()
            node_type = node.get_type_name()
            if node_type == "omni.graph.action.OnPlaybackTick" or node_type == "omni.graph.action.OnTick":
                tick_node = node_path
            elif node_type == "isaacsim.ros2.bridge.ROS2Context":
                context_node = node_path
            elif node_type == "isaacsim.core.nodes.IsaacReadSimulationTime":
                sim_time_node = node_path
            elif node_type == "isaacsim.ros2.bridge.ROS2PublishJointState":
                # if there already exist a js pub node, add a new one with a different name
                js_pub_node_path = get_next_free_path(node_path, "")
                js_pub_node_name = Path(js_pub_node_path).name
            elif node_type == "isaacsim.ros2.bridge.ROS2SubscribeJointState":
                # if there already exist a js sub node, add a new one with a different name
                js_sub_node_path = get_next_free_path(node_path, "")
                js_sub_node_name = Path(js_sub_node_path).name
            elif node_type == "isaacsim.core.nodes.IsaacArticulationController":
                msg = "already has an articulation controller node, CREATING A NEW ARTICULATION NODE"
                print(msg)
                post_notification(msg, status=NotificationStatus.WARNING)
                art_node = get_next_free_path(node_path, "")
                art_node_name = Path(art_node).name

        if self._publisher:
            og.Controller.edit(
                graph_handle,
                {
                    keys.CREATE_NODES: [
                        (js_pub_node_name, "isaacsim.ros2.bridge.ROS2PublishJointState"),
                    ],
                    keys.SET_VALUES: [
                        (js_pub_node_name + ".inputs:targetPrim", self._art_root_path),
                        (js_pub_node_name + ".inputs:topicName", self._pub_topic),
                        (js_pub_node_name + ".inputs:nodeNamespace", self._node_namespace),
                    ],
                },
            )

            if tick_node:
                og.Controller.connect(
                    og.Controller.attribute(tick_node + ".outputs:tick"),
                    og.Controller.attribute(self._og_path + "/" + js_pub_node_name + ".inputs:execIn"),
                )
            if context_node:
                og.Controller.connect(
                    og.Controller.attribute(context_node + ".outputs:context"),
                    og.Controller.attribute(self._og_path + "/" + js_pub_node_name + ".inputs:context"),
                )
            if sim_time_node:
                og.Controller.connect(
                    og.Controller.attribute(sim_time_node + ".outputs:simulationTime"),
                    og.Controller.attribute(self._og_path + "/" + js_pub_node_name + ".inputs:timeStamp"),
                )

        if self._subscriber:
            og.Controller.edit(
                graph_handle,
                {
                    keys.CREATE_NODES: [
                        (js_sub_node_name, "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
                    ],
                    keys.SET_VALUES: [
                        (js_sub_node_name + ".inputs:topicName", self._sub_topic),
                        (self._og_path + "/" + js_sub_node_name + ".inputs:nodeNamespace", self._node_namespace),
                    ],
                },
            )

            if tick_node:
                og.Controller.connect(
                    og.Controller.attribute(tick_node + ".outputs:tick"),
                    og.Controller.attribute(self._og_path + "/" + js_sub_node_name + ".inputs:execIn"),
                )
            if context_node:
                og.Controller.connect(
                    og.Controller.attribute(context_node + ".outputs:context"),
                    og.Controller.attribute(self._og_path + "/" + js_sub_node_name + ".inputs:context"),
                )

            if self._sub_move_robot:
                og.Controller.edit(
                    graph_handle,
                    {
                        keys.CREATE_NODES: [
                            (art_node_name, "isaacsim.core.nodes.IsaacArticulationController"),
                        ],
                        keys.SET_VALUES: [
                            (art_node_name + ".inputs:targetPrim", self._art_root_path),
                        ],
                        keys.CONNECT: [
                            (
                                tick_node + ".outputs:tick",
                                self._og_path + "/" + art_node_name + ".inputs:execIn",
                            ),
                            (
                                self._og_path + "/" + js_sub_node_name + ".outputs:positionCommand",
                                self._og_path + "/" + art_node_name + ".inputs:positionCommand",
                            ),
                            (
                                self._og_path + "/" + js_sub_node_name + ".outputs:velocityCommand",
                                self._og_path + "/" + art_node_name + ".inputs:velocityCommand",
                            ),
                            (
                                self._og_path + "/" + js_sub_node_name + ".outputs:effortCommand",
                                self._og_path + "/" + art_node_name + ".inputs:effortCommand",
                            ),
                            (
                                self._og_path + "/" + js_sub_node_name + ".outputs:jointNames",
                                self._og_path + "/" + art_node_name + ".inputs:jointNames",
                            ),
                        ],
                    },
                )

    def _build_ui(self):

        og_path_def = ParamWidget.FieldDef(
            name="og_path", label="Graph Path", type=ui.StringField, default=self._og_path
        )
        node_namespace_def = ParamWidget.FieldDef(
            name="node_namespace", label="Node Namespace", type=ui.StringField, default=self._node_namespace
        )
        pub_topic_def = ParamWidget.FieldDef(
            name="pub topic", label="Publisher Topic", type=ui.StringField, default=self._pub_topic
        )
        sub_topic_def = ParamWidget.FieldDef(
            name="sub topic", label="Subscriber Topic", type=ui.StringField, default=self._sub_topic
        )
        with self.frame:
            with ui.VStack(spacing=4):
                with ui.HStack():
                    ui.Label("Add to an existing graph?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._add_to_existing_graph)
                    SimpleCheckBox(self._add_to_existing_graph, self._on_use_existing_graph, model=cb)
                self.og_path_input = ParamWidget(field_def=og_path_def)
                self.node_namespace_input = ParamWidget(field_def=node_namespace_def)
                self.art_root_input = SelectPrimWidget(label="Articulation Root", default=self._art_root_path)
                ui.Spacer(height=5)
                with ui.HStack():
                    ui.Label("Publisher", width=ui.Percent(15))
                    cb = ui.SimpleBoolModel(default_value=self._publisher)
                    SimpleCheckBox(self._publisher, self._on_pub_graph, model=cb)
                    ui.Spacer(width=ui.Percent(5))
                    self.pub_topic_input = ParamWidget(field_def=pub_topic_def)
                    ui.Spacer(width=ui.Percent(20))
                with ui.HStack():
                    ui.Label("Subscriber", width=ui.Percent(15))
                    cb = ui.SimpleBoolModel(default_value=self._subscriber)
                    SimpleCheckBox(self._subscriber, self._on_sub_graph, model=cb)
                    ui.Spacer(width=ui.Percent(5))
                    self.sub_topic_input = ParamWidget(field_def=sub_topic_def)
                    ui.Label("Move Robot?", width=ui.Percent(15))
                    cb = ui.SimpleBoolModel(default_value=self._sub_move_robot)
                    SimpleCheckBox(self._sub_move_robot, self._on_sub_move_robot, model=cb)
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
                                clicked_fn=lambda: on_docs_link_clicked(
                                    "https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_manipulation.html#graph-shortcut"
                                ),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )
        return

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()
        self._node_namespace = self.node_namespace_input.get_value()
        self._art_root_path = self.art_root_input.get_value()
        self._pub_topic = self.pub_topic_input.get_value()
        self._sub_topic = self.sub_topic_input.get_value()

        param_check = self._check_params()
        if param_check:
            self.make_graph()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _on_cancel(self):
        self.visible = False

    def _check_params(self):
        stage = omni.usd.get_context().get_stage()

        if self._add_to_existing_graph:
            # make sure the "existing" graph exist
            og_prim = stage.GetPrimAtPath(self._og_path)
            if og_prim.IsValid() and og_prim.IsA(OmniGraphSchema.OmniGraph):
                pass
            else:
                msg = self._og_path + "is not an existing graph, check the og path"
                post_notification(msg, status=NotificationStatus.WARNING)
                return False

        return True

    def _on_use_existing_graph(self, check_state):
        self._add_to_existing_graph = check_state

    def _on_pub_graph(self, check_state):
        self._publisher = check_state

    def _on_sub_graph(self, check_state):
        self._subscriber = check_state

    def _on_sub_move_robot(self, check_state):
        self._sub_move_robot = check_state


class Ros2TfPubGraph(MenuHelperWindow):
    def __init__(self):
        super().__init__("ROS2 TF Publisher Graph", width=450, height=450)
        self._og_path = "/Graph/ROS_TF"
        self._node_namespace = ""
        self._existing_node_path = ""
        self._target_prim = ""
        self._parent_prim = ""
        self._pub_topic = "/tf"
        self._add_to_existing_graph = False
        self._add_to_existing_node = False
        self._has_existing_node = False

        # build UI
        self._build_ui()

    def make_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys
        # if starting from a new graph, start it with just a tick,context, and sim_time node, the rest is the same for adding to exsiting graph
        if not self._add_to_existing_graph:
            self._og_path = get_next_free_path(self._og_path, "")
            (graph_handle, nodes, _, _) = og.Controller.edit(
                {"graph_path": self._og_path, "evaluator_name": "execution"},
                {
                    keys.CREATE_NODES: [
                        ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                        ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                        ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                    ],
                    keys.SET_VALUES: [
                        ("ReadSimTime.inputs:resetOnStop", False),
                    ],
                },
            )
        else:
            graph_handle = og.get_graph_by_path(self._og_path)

        # to an existin graph
        # traverse through the graph
        all_nodes = graph_handle.get_nodes()
        tf_pub_name = "PublisherTF"
        tick_node = None
        context_node = None
        sim_time_node = None
        for node in all_nodes:
            node_path = node.get_prim_path()
            node_type = node.get_type_name()
            if node_type == "omni.graph.action.OnPlaybackTick" or node_type == "omni.graph.action.OnTick":
                tick_node = node_path
            elif node_type == "isaacsim.ros2.bridge.ROS2Context":
                context_node = node_path
            elif node_type == "isaacsim.core.nodes.IsaacReadSimulationTime":
                sim_time_node = node_path
            elif node_type == "isaacsim.ros2.bridge.ROS2PublishTransformTree":
                self._has_existing_node = True
                if self._add_to_existing_node:
                    # if adding to an existing node, simply append the target prim to the existing list of target prims
                    tf_pub_node = self._existing_node_path

                else:
                    # get ready to add a new tf node
                    tf_pub_node = get_next_free_path(node_path, "")
                    tf_pub_name = Path(tf_pub_node).name

        if self._has_existing_node and self._add_to_existing_node:
            ## if add to existing node, simply append it to the existing list of target prims
            existing_targets = og.Controller.attribute(tf_pub_node + ".inputs:targetPrims").get()
            existing_targets.append(Sdf.Path(self._target_prim))
            # must use this controller edit function, not og.controller.attribute().set() for some reason
            og.Controller.edit(
                graph_handle, {keys.SET_VALUES: [(self._og_path + "/PublisherTF.inputs:targetPrims", existing_targets)]}
            )

        else:
            ## if need to create a new tf node
            og.Controller.edit(
                graph_handle,
                {
                    keys.CREATE_NODES: [
                        (tf_pub_name, "isaacsim.ros2.bridge.ROS2PublishTransformTree"),
                    ],
                    keys.SET_VALUES: [
                        (tf_pub_name + ".inputs:parentPrim", self._parent_prim),
                        (tf_pub_name + ".inputs:targetPrims", self._target_prim),
                        (tf_pub_name + ".inputs:topicName", self._pub_topic),
                        (tf_pub_name + ".inputs:nodeNamespace", self._node_namespace),
                    ],
                    keys.CONNECT: [
                        (tick_node + ".outputs:tick", tf_pub_name + ".inputs:execIn"),
                        (sim_time_node + ".outputs:simulationTime", tf_pub_name + ".inputs:timeStamp"),
                        (context_node + ".outputs:context", tf_pub_name + ".inputs:context"),
                    ],
                },
            )

    def _build_ui(self):

        og_path_def = ParamWidget.FieldDef(
            name="og_path", label="Graph Path", type=ui.StringField, default=self._og_path
        )
        node_namespace_def = ParamWidget.FieldDef(
            name="node_namespace", label="Node Namespace", type=ui.StringField, default=self._node_namespace
        )
        pub_topic_def = ParamWidget.FieldDef(
            name="pub topic", label="Publisher Topic", type=ui.StringField, default=self._pub_topic
        )

        with self.frame:
            with ui.VStack(spacing=4):
                with ui.HStack():
                    ui.Label("Add to an existing graph?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._add_to_existing_graph)
                    SimpleCheckBox(self._add_to_existing_graph, self._on_use_existing_graph, model=cb)
                self.og_path_input = ParamWidget(field_def=og_path_def)
                self.node_namespace_input = ParamWidget(field_def=node_namespace_def)
                with ui.HStack():
                    ui.Label("Add to an existing node (i.e. same Parent)?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._add_to_existing_node)
                    SimpleCheckBox(self._add_to_existing_node, self._on_use_existing_node, model=cb)

                self.node_path_input = SelectPrimWidget(label="Node Path", default=self._existing_node_path)
                ui.Spacer(height=15)
                self.target_prim_input = SelectPrimWidget(label="Target Prim", default=self._target_prim)
                self.parent_prim_input = SelectPrimWidget(
                    label="Parent Prim (default to /World)", default=self._parent_prim
                )

                self.pub_topic_input = ParamWidget(field_def=pub_topic_def)
                ui.Spacer(width=ui.Percent(20))

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
                                clicked_fn=lambda: on_docs_link_clicked(
                                    "https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_tf.html"
                                ),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )
        return

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()
        self._node_namespace = self.node_namespace_input.get_value()
        self._existing_node_path = self.node_path_input.get_value()
        self._parent_prim = self.parent_prim_input.get_value()
        self._target_prim = self.target_prim_input.get_value()
        self._pub_topic = self.pub_topic_input.get_value()

        param_check = self._check_params()
        if param_check:
            self.make_graph()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _on_cancel(self):
        self.visible = False

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

        if self._add_to_existing_node:
            # make sure the "existing" node exist
            node_prim = stage.GetPrimAtPath(self._existing_node_path)
            if node_prim.IsValid() and node_prim.IsA(OmniGraphSchema.OmniGraphNode):
                pass
            else:
                msg = self._existing_node_path + " is not an existing node, check the node path"
                post_notification(msg, status=NotificationStatus.WARNING)
                return False

        if self._add_to_existing_node and not self._add_to_existing_graph:
            msg = "Adding to an existing node requires adding to an existing graph, check the add to existing graph checkbox"
            post_notification(msg, status=NotificationStatus.WARNING)
            return False

        return True

    def _on_use_existing_graph(self, check_state):
        self._add_to_existing_graph = check_state

    def _on_use_existing_node(self, check_state):
        self._add_to_existing_node = check_state


class Ros2OdometryGraph(MenuHelperWindow):
    def __init__(self):
        super().__init__("ROS2 Odometry Graph", width=450, height=350)
        self._og_path = "/Graph/ROS_Odometry"
        self._node_namespace = ""
        self._art_root_prim = ""
        self._odom_pub_topic = "/odom"
        self._tf_pub_topic = "/tf"
        self._add_to_existing_graph = False
        self._tf_robot_pub = True  # also publish TF tree of the robot
        self._chassis_prim = ""
        self._chassis_link_name = "base_link"

        # build UI
        self._build_ui()

    def make_graph(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()

        keys = og.Controller.Keys
        # if starting from a new graph, start it with just a tick,context, and sim_time node, the rest is the same for adding to exsiting graph
        if not self._add_to_existing_graph:
            self._og_path = get_next_free_path(self._og_path, "")
            (graph_handle, nodes, _, _) = og.Controller.edit(
                {"graph_path": self._og_path, "evaluator_name": "execution"},
                {
                    keys.CREATE_NODES: [
                        ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                        ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                        ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                    ],
                    keys.SET_VALUES: [
                        ("ReadSimTime.inputs:resetOnStop", False),
                    ],
                },
            )
        else:
            graph_handle = og.get_graph_by_path(self._og_path)

        # to an existin graph
        # traverse through the graph and pick out all the relevant nodes
        all_nodes = graph_handle.get_nodes()
        odom_compute_name = "ComputeOdometry"
        odom_pub_name = "PublisherOdometry"
        tf_odom2robot_name = "TFOdom2Robot"
        tf_world2odom_name = "TFWorld2Odom"
        tf_robot_name = "TFRobot"
        tf_robot_node = None
        tick_node = None
        context_node = None
        sim_time_node = None
        for node in all_nodes:
            node_path = node.get_prim_path()
            node_type = node.get_type_name()
            if node_type == "omni.graph.action.OnPlaybackTick" or node_type == "omni.graph.action.OnTick":
                tick_node = node_path
            elif node_type == "isaacsim.ros2.bridge.ROS2Context":
                context_node = node_path
            elif node_type == "isaacsim.core.nodes.IsaacReadSimulationTime":
                sim_time_node = node_path
            elif node_type == "isaacsim.ros2.bridge.ROS2PublishOdometry":
                # get ready to add a new odom publisher nodes
                odom_pub_node = get_next_free_path(node_path, "")
                odom_pub_name = Path(odom_pub_node).name
            elif node_type == "isaacsim.core.nodes.IsaacComputeOdometry":
                # get ready to add a new odom compute nodes
                odom_compute_node = get_next_free_path(node_path, "")
                odom_compute_name = Path(odom_compute_node).name
            elif node_type == "isaacsim.ros2.bridge.ROS2PublishRawTransformTree":
                # get ready to add two new raw tf publisher nodes
                tf_world2odom_node = get_next_free_path(self._og_path + "/" + tf_world2odom_name, "")
                tf_odom2robot_node = get_next_free_path(self._og_path + "/" + tf_odom2robot_name, "")
                tf_world2odom_name = Path(tf_world2odom_node).name
                tf_odom2robot_name = Path(tf_odom2robot_node).name
            elif node_type == "isaacsim.ros2.bridge.ROS2PublishTransformTree":
                tf_robot_node = get_next_free_path(node_path, "")
                tf_robot_name = Path(tf_robot_node).name

        # add odometry related nodes and connections:
        og.Controller.edit(
            graph_handle,
            {
                keys.CREATE_NODES: [
                    (tf_world2odom_name, "isaacsim.ros2.bridge.ROS2PublishRawTransformTree"),
                    (tf_odom2robot_name, "isaacsim.ros2.bridge.ROS2PublishRawTransformTree"),
                    (odom_compute_name, "isaacsim.core.nodes.IsaacComputeOdometry"),
                    (odom_pub_name, "isaacsim.ros2.bridge.ROS2PublishOdometry"),
                ],
                keys.SET_VALUES: [
                    (odom_compute_name + ".inputs:chassisPrim", self._art_root_prim),
                    (odom_pub_name + ".inputs:topicName", self._odom_pub_topic),
                    (odom_pub_name + ".inputs:chassisFrameId", self._chassis_link_name),
                    (odom_pub_name + ".inputs:nodeNamespace", self._node_namespace),
                    (tf_odom2robot_name + ".inputs:childFrameId", self._chassis_link_name),
                    (tf_world2odom_name + ".inputs:childFrameId", "odom"),
                    (tf_world2odom_name + ".inputs:parentFrameId", "world"),
                    (tf_odom2robot_name + ".inputs:nodeNamespace", self._node_namespace),
                    (tf_world2odom_name + ".inputs:nodeNamespace", self._node_namespace),
                ],
                keys.CONNECT: [
                    (tick_node + ".outputs:tick", tf_world2odom_name + ".inputs:execIn"),
                    (tick_node + ".outputs:tick", tf_odom2robot_name + ".inputs:execIn"),
                    (tick_node + ".outputs:tick", odom_compute_name + ".inputs:execIn"),
                    (odom_compute_name + ".outputs:execOut", odom_pub_name + ".inputs:execIn"),
                    (odom_compute_name + ".outputs:angularVelocity", odom_pub_name + ".inputs:angularVelocity"),
                    (odom_compute_name + ".outputs:linearVelocity", odom_pub_name + ".inputs:linearVelocity"),
                    (odom_compute_name + ".outputs:orientation", odom_pub_name + ".inputs:orientation"),
                    (odom_compute_name + ".outputs:position", odom_pub_name + ".inputs:position"),
                    (odom_compute_name + ".outputs:orientation", tf_odom2robot_name + ".inputs:rotation"),
                    (odom_compute_name + ".outputs:position", tf_odom2robot_name + ".inputs:translation"),
                ],
            },
        )

        if context_node:
            og.Controller.edit(
                graph_handle,
                {
                    keys.CONNECT: [
                        (
                            context_node + ".outputs:context",
                            self._og_path + "/" + tf_world2odom_name + ".inputs:context",
                        ),
                        (
                            context_node + ".outputs:context",
                            self._og_path + "/" + tf_odom2robot_name + ".inputs:context",
                        ),
                        (context_node + ".outputs:context", self._og_path + "/" + odom_pub_name + ".inputs:context"),
                    ]
                },
            )

        if sim_time_node:
            og.Controller.edit(
                graph_handle,
                {
                    keys.CONNECT: [
                        (
                            sim_time_node + ".outputs:simulationTime",
                            self._og_path + "/" + tf_world2odom_name + ".inputs:timeStamp",
                        ),
                        (
                            sim_time_node + ".outputs:simulationTime",
                            self._og_path + "/" + tf_odom2robot_name + ".inputs:timeStamp",
                        ),
                        (
                            sim_time_node + ".outputs:simulationTime",
                            self._og_path + "/" + odom_pub_name + ".inputs:timeStamp",
                        ),
                    ]
                },
            )

        # if user also wanted to publish TF tree of the robot
        if self._tf_robot_pub:
            og.Controller.edit(
                graph_handle,
                {
                    keys.CREATE_NODES: [
                        (tf_robot_name, "isaacsim.ros2.bridge.ROS2PublishTransformTree"),
                    ],
                    keys.SET_VALUES: [
                        (tf_robot_name + ".inputs:parentPrim", self._chassis_prim),
                        (tf_robot_name + ".inputs:targetPrims", self._art_root_prim),
                        (tf_robot_name + ".inputs:topicName", self._tf_pub_topic),
                        (tf_robot_name + ".inputs:nodeNamespace", self._node_namespace),
                    ],
                    keys.CONNECT: [
                        (tick_node + ".outputs:tick", tf_robot_name + ".inputs:execIn"),
                        (sim_time_node + ".outputs:simulationTime", tf_robot_name + ".inputs:timeStamp"),
                        (context_node + ".outputs:context", tf_robot_name + ".inputs:context"),
                    ],
                },
            )
            if context_node:
                og.Controller.connect(
                    og.Controller.attribute(context_node + ".outputs:context"),
                    og.Controller.attribute(self._og_path + "/" + tf_robot_name + ".inputs:context"),
                )

            if sim_time_node:
                og.Controller.connect(
                    og.Controller.attribute(sim_time_node + ".outputs:simulationTime"),
                    og.Controller.attribute(self._og_path + "/" + tf_robot_name + ".inputs:timeStamp"),
                )

    def _build_ui(self):

        og_path_def = ParamWidget.FieldDef(
            name="og_path", label="Graph Path", type=ui.StringField, default=self._og_path
        )
        node_namespace_def = ParamWidget.FieldDef(
            name="node_namespace", label="Node Namespace", type=ui.StringField, default=self._node_namespace
        )

        with self.frame:
            with ui.VStack(spacing=4):
                with ui.HStack():
                    ui.Label("Add to an existing graph?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._add_to_existing_graph)
                    SimpleCheckBox(self._add_to_existing_graph, self._on_use_existing_graph, model=cb)
                self.og_path_input = ParamWidget(field_def=og_path_def)
                self.node_namespace_input = ParamWidget(field_def=node_namespace_def)
                with ui.HStack():
                    ui.Label("Publish Robot's TF?", width=ui.Percent(30))
                    cb = ui.SimpleBoolModel(default_value=self._tf_robot_pub)
                    SimpleCheckBox(self._tf_robot_pub, self._on_publish_robot_tf, model=cb)
                self.art_root_input = SelectPrimWidget(label="Robot Articulation Root", default=self._art_root_prim)
                self.chassis_prim_input = SelectPrimWidget(label="Chassis Link Prim", default=self._chassis_prim)

                ui.Spacer(height=5)

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
                                clicked_fn=lambda: on_docs_link_clicked(
                                    "https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_tf.html#setting-up-odometry"
                                ),
                                style=get_style()["IconButton.Image::OpenLink"],
                            )
        return

    def _on_ok(self):
        self._og_path = self.og_path_input.get_value()
        self._node_namespace = self.node_namespace_input.get_value()
        self._art_root_prim = self.art_root_input.get_value()
        self._chassis_prim = self.chassis_prim_input.get_value()
        self._chassis_link_name = self._chassis_prim.split("/")[-1]

        param_check = self._check_params()
        if param_check:
            self.make_graph()
            self.visible = False
        else:
            post_notification("Parameter check failed", status=NotificationStatus.WARNING)

    def _on_cancel(self):
        self.visible = False

    def _check_params(self):
        stage = omni.usd.get_context().get_stage()

        if self._add_to_existing_graph:
            # make sure the "existing" graph exist
            og_prim = stage.GetPrimAtPath(self._og_path)
            if og_prim.IsValid() and og_prim.IsA(OmniGraphSchema.OmniGraph):
                pass
            else:
                msg = self._og_path + "is not an existing graph, check the og path"
                post_notification(msg, status=NotificationStatus.WARNING)
                return False

        return True

    def _on_use_existing_graph(self, check_state):
        self._add_to_existing_graph = check_state

    def _on_publish_robot_tf(self, check_state):
        self._tf_robot_pub = check_state
