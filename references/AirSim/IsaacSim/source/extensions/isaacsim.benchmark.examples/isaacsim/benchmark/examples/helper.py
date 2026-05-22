# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


import time

import omni.graph.core as og
import omni.kit.commands
import omni.usd
from pxr import Gf, UsdGeom


def add_physx_lidar(prim_path, translation=Gf.Vec3f(0, 0, 0), orientation=Gf.Vec4f(0, 0, 0, 0)):
    _, lidar = omni.kit.commands.execute(
        "RangeSensorCreateLidar",
        path=prim_path,
        parent=None,
        min_range=0.4,
        max_range=100.0,
        draw_points=True,
        draw_lines=True,
        horizontal_fov=360.0,
        vertical_fov=30.0,
        horizontal_resolution=0.4,
        vertical_resolution=4.0,
        rotation_rate=0.0,
        high_lod=False,
        yaw_offset=0.0,
    )
    lidar_prim = lidar.GetPrim()

    if "xformOp:translate" not in lidar_prim.GetPropertyNames():
        UsdGeom.Xformable(lidar_prim).AddTranslateOp()
    if "xformOp:orient" not in lidar_prim.GetPropertyNames():
        UsdGeom.Xformable(lidar_prim).AddOrientOp()

    lidar_prim.GetAttribute("xformOp:translate").Set(translation)
    lidar_prim.GetAttribute("xformOp:orient").Set(orientation)


def add_ros2_camera(render_product_path, graph_path, camera_topic, sim_camera_id, type="rgb"):
    (ros_camera_graph, _, _, _) = og.Controller.edit(
        {"graph_path": graph_path, "evaluator_name": "execution"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("OnTick", "omni.graph.action.OnTick"),
                ("cameraHelperRgb", "isaacsim.ros2.bridge.ROS2CameraHelper"),
            ],
            og.Controller.Keys.CONNECT: [
                ("OnTick.outputs:tick", "cameraHelperRgb.inputs:execIn"),
            ],
            og.Controller.Keys.SET_VALUES: [
                ("cameraHelperRgb.inputs:renderProductPath", render_product_path),
                ("cameraHelperRgb.inputs:frameId", sim_camera_id),
                ("cameraHelperRgb.inputs:topicName", camera_topic),
                ("cameraHelperRgb.inputs:type", type),
            ],
        },
    )

    return ros_camera_graph
