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
import os
import re
import threading
import time
from functools import partial

import carb
import omni
import omni.ui as ui
from isaacsim.asset.importer.urdf import UrdfImporter
from isaacsim.asset.importer.urdf.impl.ui import cb_builder, get_option_style, str_builder
from omni.kit.menu.utils import MenuItemDescription, add_menu_items, remove_menu_items

# from std_msgs.msg import String

EXTENSION_NAME = "Import from ROS2 URDF Node"


def package_path_to_system_path(package_name, relative_path=""):

    from ament_index_python.packages import get_package_share_directory

    package_share_path = get_package_share_directory(package_name)
    return package_share_path


def replace_package_urls_with_paths(input_string):

    # Define the regex pattern to match substrings starting with "package://" and ending with a quote mark
    pattern = r"package://([^/]+)"  # Capturing group to extract package name

    # Find all matches of the pattern in the input string
    matches = re.findall(pattern, input_string)

    # Iterate through matches and replace package URLs with file paths
    for package_name in matches:
        package_path = package_path_to_system_path(package_name)
        package_url = "package://" + package_name
        input_string = input_string.replace(package_url, package_path)

    return input_string


def Singleton(class_):
    """A singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@Singleton
class RobotDefinitionReader:
    def __init__(
        self,
    ):
        self.node_name = None
        self.node = None
        self.future = None
        self.description_received_fn = None
        self.urdf_doc = ""
        self.urdf_abs = ""

    def __del__(self):
        import rclpy

        if self.node:
            self.node.destroy_node()
        rclpy.try_shutdown()

    def on_description_received(self, _):
        if self.description_received_fn:
            self.description_received_fn(self.urdf_abs)

    def service_call(self, node):
        import rclpy
        from rcl_interfaces.srv import GetParameters

        client = node.create_client(GetParameters, f"/{self.node_name}/get_parameters")
        if client.wait_for_service(timeout_sec=1.0):

            request = GetParameters.Request()
            request.names = ["robot_description"]
            self.future = client.call_async(request)

            while rclpy.ok():
                if self.future.cancelled():
                    break
                rclpy.spin_once(node)
                if self.future.done():
                    break

            # rclpy.spin_until_future_complete(node, future)
            if self.future.done():
                try:
                    response = self.future.result()
                    if response.values:
                        # node.get_logger().info('Parameters received:')
                        for param in response.values:
                            self.urdf_doc = param.string_value
                            self.urdf_abs = replace_package_urls_with_paths(self.urdf_doc)
                            self.on_description_received(self.urdf_abs)
                    # else:
                    #     node.get_logger().info('No parameters received.')
                except Exception as e:
                    carb.log_error("Service call failed %r" % (e,))
        else:
            carb.log_error(f"node '{self.node_name}' not found. is the spelling correct?")

        node.destroy_node()
        rclpy.try_shutdown()

    def start_get_robot_description(self, node_name):
        import rclpy

        # Create a client for the service
        if self.future:
            self.future.cancel()

        if node_name:
            self.node_name = node_name
            try:
                rclpy.init()
            except RuntimeError as e:
                pass
            node = rclpy.create_node("service_client")

            # Run the service_call function in a separate thread
            thread = threading.Thread(target=self.service_call, args=(node,))
            thread.start()


class RobotDescription:
    def __init__(self):
        self.urdf_importer = UrdfImporter()
        self.urdf_description = None
        self._main_frame = self.urdf_importer.add_ui_frame("input", "ros2Node")
        with self._main_frame:
            with ui.VStack(height=ui.Pixel(20)):
                with ui.HStack(height=25):

                    self.node_frame = ui.Frame(style=get_option_style())
                # ui.Spacer(height=ui.Pixel(5))
        with self.node_frame:
            with ui.VStack():
                # ui.Spacer(height=ui.Pixel(5))
                with ui.HStack(height=ui.Pixel(0)):
                    with ui.HStack():
                        kwargs = {
                            "label": "Node",
                            "default_val": "",
                            "tooltip": "Ros Node containing the robot descriptor",
                            "use_folder_picker": False,
                            "style": {
                                "background_color": 0xFF23211F,
                                "font_size": 14.0,
                                "color": 0xFFD5D5D5,
                                "border_radius": 1.5,
                            },
                        }
                        self.node_model = str_builder(**kwargs)
                        self.node_model.add_end_edit_fn(self._on_node_changed)
                    ui.Spacer(width=ui.Pixel(5))
                    self.refresh = ui.Button(
                        "Refresh",
                        style=get_option_style(),
                        clicked_fn=lambda: self._on_node_changed(self.node_model),
                        enabled=False,
                        width=ui.Pixel(30),
                        height=24,
                    )
        self.node_frame.visible = True
        self.urdf_importer.set_file_input_visible(False)
        # self.urdf_importer.build_ui()

    def _on_description_received(self, urdf_description):
        self.urdf_description = urdf_description
        result, robot_model = omni.kit.commands.execute(
            "URDFParseText", urdf_string=urdf_description, import_config=self.urdf_importer.config
        )
        if result:
            self.refresh.enabled = True
            self.urdf_importer.update_robot_model(robot_model)

    def _on_node_changed(self, model):
        value = model.get_value_as_string()
        self.urdf_importer.robot_frame.visible = False
        lister = RobotDefinitionReader()
        lister.description_received_fn = partial(self._on_description_received)
        lister.start_get_robot_description(value)

    def shutdown(self):
        if self.urdf_importer:
            self._main_frame.visible = False
            self.urdf_importer.remove_ui_frame("ros2Node")
            # Cycle visibility so it forces redraw of parent
            self.urdf_importer.set_file_input_visible(False)
            self.urdf_importer.set_file_input_visible(True)


class Extension(omni.ext.IExt):
    def menu_click(self, menu, value):
        self.robot_description.urdf_importer._window.visible = True

    def on_startup(self, ext_id):
        # print("startup")
        self.ext_id = ext_id
        self.robot_description = RobotDescription()
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.register_action(
            self.ext_id,
            "import_from_ros2_urdf",
            partial(self.menu_click, None, True),
            display_name=EXTENSION_NAME,
            description="Import documents from a ros2 urdf description node",
            tag="Import from ROS2 Node",
        )
        self._menu_items = [
            MenuItemDescription(
                name=EXTENSION_NAME,
                glyph="none.svg",
                appear_after=["Import", "Reopen", "Open", "New From Stage Template"],
                onclick_action=(self.ext_id, "import_from_ros2_urdf"),
            )
        ]
        add_menu_items(self._menu_items, "File")

    def deregister_actions(
        self,
    ):
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self.ext_id)

    def on_shutdown(self):
        remove_menu_items(self._menu_items, "File")
        self.deregister_actions()
        self.robot_description.shutdown()
        pass
