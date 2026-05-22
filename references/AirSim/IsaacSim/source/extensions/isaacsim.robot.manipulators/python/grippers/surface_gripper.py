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
import carb
import isaacsim.robot.surface_gripper._surface_gripper as surface_gripper
import numpy as np
import omni.kit.app
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.robot.manipulators.grippers.gripper import Gripper


class SurfaceGripper(Gripper):
    """Provides high level functions to set/ get properties and actions of a surface gripper
    (a suction cup for example).

    Args:
        end_effector_prim_path (str): prim path of the Prim that corresponds to the gripper root/ end effector.
        translate (float, optional): _description_. Defaults to 0.
        direction (str, optional): _description_. Defaults to "x".
        grip_threshold (float, optional): _description_. Defaults to 0.01.
        force_limit (float, optional): _description_. Defaults to 1.0e6.
        torque_limit (float, optional): _description_. Defaults to 1.0e4.
        bend_angle (float, optional): _description_. Defaults to np.pi/24.
        kp (float, optional): _description_. Defaults to 1.0e2.
        kd (float, optional): _description_. Defaults to 1.0e2.
        disable_gravity (bool, optional): _description_. Defaults to True.
    """

    def __init__(
        self,
        end_effector_prim_path: str,
        surface_gripper_path: str,
    ) -> None:
        Gripper.__init__(self, end_effector_prim_path=end_effector_prim_path)
        self._surface_gripper_interface = surface_gripper.acquire_surface_gripper_interface()
        self._surface_gripper_path = surface_gripper_path
        return

    def initialize(
        self, physics_sim_view: omni.physics.tensors.SimulationView = None, articulation_num_dofs: int = None
    ) -> None:
        """Create a physics simulation view if not passed and creates a rigid prim view using physX tensor api.
            This needs to be called after each hard reset (i.e stop + play on the timeline) before interacting with any
            of the functions of this class.

        Args:
            physics_sim_view (omni.physics.tensors.SimulationView, optional): current physics simulation view. Defaults to None
            articulation_num_dofs (int, optional): num of dofs of the Articulation. Defaults to None.
        """
        Gripper.initialize(self, physics_sim_view=physics_sim_view)
        self._articulation_num_dofs = articulation_num_dofs

        if self._default_state is None:
            self._default_state = not self.is_closed()
        return

    def close(self) -> None:
        """Applies actions to the articulation that closes the gripper (ex: to hold an object)."""
        if not self.is_closed():
            self._surface_gripper_interface.close_gripper(self._surface_gripper_path)
        if not self.is_closed():
            carb.log_warn("gripper didn't close successfully")
        return

    def open(self) -> None:
        """Applies actions to the articulation that opens the gripper (ex: to release an object held)."""
        self._surface_gripper_interface.open_gripper(self._surface_gripper_path)
        if not self.is_open():
            carb.log_warn("gripper didn't open successfully")

        return

    def update(self) -> None:
        # self._virtual_gripper.update()
        return

    def is_closed(self) -> bool:
        return (
            self._surface_gripper_interface.get_gripper_status(self._surface_gripper_path)
            == surface_gripper.GripperStatus.Closed
        )

    def is_open(self) -> bool:
        return (
            self._surface_gripper_interface.get_gripper_status(self._surface_gripper_path)
            == surface_gripper.GripperStatus.Open
        )

    def set_default_state(self, opened: bool):
        """Sets the default state of the gripper

        Args:
            opened (bool): True if the surface gripper should start in an opened state. False otherwise.
        """
        self._default_state = opened
        return

    def get_default_state(self) -> dict:
        """Gets the default state of the gripper

        Returns:
            dict: key is "opened" and value would be true if the surface gripper should start in an opened state. False otherwise.
        """
        return {"opened": self._default_state}

    def post_reset(self):
        Gripper.post_reset(self)
        if self._default_state:  # means opened is true
            self.open()
        else:
            self.close()
        return

    def forward(self, action: str) -> ArticulationAction:
        """calculates the ArticulationAction for all of the articulation joints that corresponds to "open"
           or "close" actions.

        Args:
            action (str): "open" or "close" as an abstract action.

        Raises:
            Exception: _description_

        Returns:
            ArticulationAction: articulation action to be passed to the articulation itself
                                (includes all joints of the articulation).
        """
        if self._articulation_num_dofs is None:
            raise Exception(
                "Num of dofs of the articulation needs to be passed to initialize in order to use this method"
            )
        if action == "open":
            self.open()
        elif action == "close":
            self.close()
        else:
            raise Exception("action {} is not defined for SurfaceGripper".format(action))
        return ArticulationAction(joint_positions=[None] * self._articulation_num_dofs)
