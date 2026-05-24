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
import sys

import carb
import omni.ext
import omni.kit
from isaacsim.ros2.bridge.impl.ros2_common import (
    SUPPORTED_ROS_DISTROS,
    print_environment_setup_instructions,
    setup_ros2_environment,
)


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):
        ros_distro = os.environ.get("ROS_DISTRO")
        if ros_distro in SUPPORTED_ROS_DISTROS.values() and os.path.join(f"{ros_distro}", "rclpy") in os.path.join(
            os.path.dirname(__file__)
        ):
            omni.kit.app.get_app().print_and_log("Attempting to load system rclpy")
            ament_prefix = os.environ.get("AMENT_PREFIX_PATH")
            if ament_prefix is not None and os.environ.get("OLD_PYTHONPATH") is not None:
                for python_path in os.environ.get("OLD_PYTHONPATH").split(":"):
                    for ament_path in ament_prefix.split(":"):
                        if python_path.startswith(os.path.abspath(ament_path) + os.sep):
                            sys.path.append(os.path.join(python_path))
                            break
            try:
                import rclpy

                rclpy.init()
                rclpy.shutdown()
                omni.kit.app.get_app().print_and_log("rclpy loaded")
            except Exception as e:
                omni.kit.app.get_app().print_and_log(f"Could not import system rclpy: {e}")
                omni.kit.app.get_app().print_and_log(f"Attempting to load internal rclpy for ROS Distro: {ros_distro}")
                sys.path.append(os.path.join(os.path.dirname(__file__)))
                ext_manager = omni.kit.app.get_app().get_extension_manager()
                self._extension_path = ext_manager.get_extension_path(ext_id)

                setup_ros2_environment(self._extension_path, ros_distro)

                try:
                    import rclpy

                    rclpy.init()
                    rclpy.shutdown()
                    omni.kit.app.get_app().print_and_log("rclpy loaded")
                except Exception as e:
                    omni.kit.app.get_app().print_and_log(f"Could not import internal rclpy: {e}")
                    print_environment_setup_instructions(self._extension_path, ros_distro)
                try:
                    import rclpy

                    rclpy.init()
                    rclpy.shutdown()
                except Exception as e:
                    carb.log_warn("Could not import rclpy")
            return

    def on_shutdown(self):
        rclpy_path = os.path.join(os.path.dirname(__file__))
        if rclpy_path in sys.path:
            sys.path.remove(rclpy_path)
