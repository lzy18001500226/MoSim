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

import carb
import omni.graph.core as og

# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test
import usdrt.Sdf
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.extensions import get_extension_path_from_name
from isaacsim.core.utils.rotations import quat_to_euler_angles
from isaacsim.core.utils.stage import open_stage_async
from isaacsim.storage.native import get_assets_root_path_async


async def init_robot_sim(art_path, graph_path="/ActionGraph"):
    art = SingleArticulation(art_path)
    art._articulation_view.initialize()
    # reset
    art.set_world_pose(position=[0, 0, 0.1], orientation=[0, 0, 0, 1])
    art.set_world_velocity([0, 0, 0, 0, 0, 0])
    # reset controller
    og.Controller.attribute(graph_path + "/DifferentialController.inputs:linearVelocity").set(0)
    og.Controller.attribute(graph_path + "/DifferentialController.inputs:angularVelocity").set(0)
    # wait for robot to drop
    for i in range(10):
        await omni.kit.app.get_app().next_update_async()

    return


def setup_robot_og(graph_path, lwheel_name, rwheel_name, robot_path, wheel_rad, wheel_dist):
    keys = og.Controller.Keys
    (graph, nodes, _, _) = og.Controller.edit(
        {"graph_path": graph_path, "evaluator_name": "execution"},
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("DifferentialController", "isaacsim.robot.wheeled_robots.DifferentialController"),
                ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ("computeOdom", "isaacsim.core.nodes.IsaacComputeOdometry"),
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "DifferentialController.inputs:execIn"),
                ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                ("OnPlaybackTick.outputs:tick", "computeOdom.inputs:execIn"),
                ("DifferentialController.outputs:velocityCommand", "ArticulationController.inputs:velocityCommand"),
            ],
            keys.SET_VALUES: [
                ("ArticulationController.inputs:jointNames", [lwheel_name, rwheel_name]),
                ("ArticulationController.inputs:robotPath", robot_path),
                ("DifferentialController.inputs:wheelRadius", wheel_rad),
                ("DifferentialController.inputs:wheelDistance", wheel_dist),
                ("computeOdom.inputs:chassisPrim", [usdrt.Sdf.Path(robot_path)]),
            ],
        },
    )

    return graph, nodes[3]


def set_physics_frequency(frequency=60):
    carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", True)
    carb.settings.get_settings().set_int("/app/runLoops/main/rateLimitFrequency", int(frequency))
    carb.settings.get_settings().set_int("/persistent/simulation/minFrameRate", int(frequency))
