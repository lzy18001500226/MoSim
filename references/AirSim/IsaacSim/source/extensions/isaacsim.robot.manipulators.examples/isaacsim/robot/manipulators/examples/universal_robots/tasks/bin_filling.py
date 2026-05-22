# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import random

import carb
import numpy as np
from isaacsim.core.api.scenes.scene import Scene
from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.prims import SingleRigidPrim, SingleXFormPrim
from isaacsim.core.utils.rotations import euler_angles_to_quat
from isaacsim.core.utils.stage import add_reference_to_stage, get_stage_units
from isaacsim.robot.manipulators.examples.universal_robots import UR10
from isaacsim.storage.native import get_assets_root_path


class BinFilling(BaseTask):
    """Task using UR10 robot to fill a bin with screws and showcase the surface gripper torque/ force limits.

    Args:
        name (str, optional): Task name identifier. Should be unique if added to the World. Defaults to "bin_filling".
    """

    def __init__(self, name: str = "bin_filling") -> None:
        BaseTask.__init__(self, name=name, offset=None)
        self._ur10_robot = None
        self._packing_bin = None
        self._assets_root_path = get_assets_root_path()
        if self._assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
            return
        self._ur10_asset_path = self._assets_root_path + "/Isaac/Samples/Leonardo/Stage/ur10_bin_filling.usd"
        self._screw_asset_paths = [
            self._assets_root_path + "/Isaac/Props/Flip_Stack/large_corner_bracket_physics.usd",
            self._assets_root_path + "/Isaac/Props/Flip_Stack/screw_95_physics.usd",
            self._assets_root_path + "/Isaac/Props/Flip_Stack/screw_99_physics.usd",
            self._assets_root_path + "/Isaac/Props/Flip_Stack/small_corner_bracket_physics.usd",
            self._assets_root_path + "/Isaac/Props/Flip_Stack/t_connector_physics.usd",
        ]
        self._screws = []
        self._max_screws = 100
        self._screws_to_add = 0
        self._pipe_position = np.array([0, 0.85, 1.2]) / get_stage_units()
        self._target_position = np.array([0, 0.85, -0.44]) / get_stage_units()
        self._bin_initial_position = np.array([0.35, 0.15, -0.40]) / get_stage_units()
        self._bin_size = np.array([0.25, 0.35, 0.20]) / get_stage_units()
        return

    def get_current_num_of_screws_to_add(self) -> int:
        """
        Returns:
            int: Number of screws left to drop from the pipe
        """
        return self._screws_to_add

    def set_up_scene(self, scene: Scene) -> None:
        """Loads the stage USD and adds the robot and packing bin to the World's scene.

        Args:
            scene (Scene): The world's scene.
        """
        super().set_up_scene(scene)
        add_reference_to_stage(usd_path=self._ur10_asset_path, prim_path="/World/Scene")
        self._ur10_robot = scene.add(
            UR10(prim_path="/World/Scene/ur10", name="my_ur10", gripper_usd=None, attach_gripper=True)
        )
        self._ur10_robot.set_joints_default_state(
            positions=np.array([-np.pi / 2, -np.pi / 2, -np.pi / 2, -np.pi / 2, np.pi / 2, 0])
        )
        self._packing_bin = scene.add(
            SingleRigidPrim(
                prim_path="/World/Scene/bin",
                name="packing_bin",
                position=self._bin_initial_position,
                orientation=euler_angles_to_quat(np.array([0, 0, np.pi / 2])),
            )
        )
        return

    def get_observations(self) -> dict:
        """Returns current observations from the task needed for the behavioral layer at each time step.

           Observations:
            - packing_bin
                - position
                - orientation
                - target_position
                - size
            - my_ur10:
                - joint_positions
                - end_effector_position
                - end_effector_orientation

        Returns:
            dict: [description]
        """
        joints_state = self._ur10_robot.get_joints_state()
        bin_position, bin_orientation = self._packing_bin.get_world_pose()
        end_effector_position, end_effector_orientation = self._ur10_robot.end_effector.get_world_pose()
        # TODO: change values with USD
        return {
            "packing_bin": {
                "position": bin_position,
                "orientation": bin_orientation,
                "target_position": self._target_position,
                "size": self._bin_size,
            },
            "my_ur10": {
                "joint_positions": joints_state.positions,
                "end_effector_position": end_effector_position,
                "end_effector_orientation": end_effector_orientation,
            },
        }

    def pre_step(self, time_step_index: int, simulation_time: float) -> None:
        """Executed before the physics step.

        Args:
            time_step_index (int): Current time step index
            simulation_time (float): Current simulation time.
        """
        BaseTask.pre_step(self, time_step_index=time_step_index, simulation_time=simulation_time)
        if self._screws_to_add > 0 and len(self._screws) < self._max_screws and time_step_index % 30 == 0:
            self._add_screw()
        return

    def post_reset(self) -> None:
        """Executed after reseting the scene"""
        self._screws_to_add = 0
        self._screws = []
        return

    def add_screws(self, screws_number: int = 10) -> None:
        """Adds number of screws to be added by the pipe

        Args:
            screws_number (int, optional): number of screws to be added by the pipe. Defaults to 10.
        """
        self._screws_to_add += screws_number
        return

    def _add_screw(self):
        asset_path = self._screw_asset_paths[random.randint(0, len(self._screw_asset_paths) - 1)]
        prim_path = "/World/objects/object_{}".format(len(self._screws))
        orientation = np.array([random.random(), random.random(), random.random(), random.random()])
        orientation = orientation / np.linalg.norm(orientation)
        add_reference_to_stage(usd_path=asset_path, prim_path=prim_path)
        self._screws.append(
            self.scene.add(
                SingleXFormPrim(
                    prim_path=prim_path,
                    name="screw_{}".format(len(self._screws)),
                    translation=self._pipe_position,
                    orientation=orientation,
                )
            )
        )
        self._screws_to_add -= 1
        return

    def cleanup(self) -> None:
        """Removed the added screws when resetting."""
        for i in range(len(self._screws)):
            self.scene.remove_object(self._screws[i].name)
        self._screws = []
        return

    def get_params(self) -> dict:
        """Task parameters are
            - bin_name
            - robot_name

        Returns:
            dict: defined parameters of the task.
        """
        params_representation = dict()
        params_representation["bin_name"] = {"value": self._packing_bin.name, "modifiable": False}
        params_representation["robot_name"] = {"value": self._ur10_robot.name, "modifiable": False}
        return params_representation
