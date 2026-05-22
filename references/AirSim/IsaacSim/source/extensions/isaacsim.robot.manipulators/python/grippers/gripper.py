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
from abc import abstractmethod

import omni.kit.app
from isaacsim.core.prims import SingleRigidPrim
from isaacsim.core.utils.types import ArticulationAction


class Gripper(SingleRigidPrim):
    """Provides high level functions to set/ get properties and actions of a gripper.

    Args:
        end_effector_prim_path (str): prim path of the Prim that corresponds to the gripper root/ end effector.
    """

    def __init__(self, end_effector_prim_path: str) -> None:
        SingleRigidPrim.__init__(self, prim_path=end_effector_prim_path, name="gripper")
        self._end_effector_prim_path = end_effector_prim_path
        self._default_state = None
        return

    def initialize(self, physics_sim_view: omni.physics.tensors.SimulationView = None) -> None:
        """Create a physics simulation view if not passed and creates a rigid prim view using physX tensor api.
            This needs to be called after each hard reset (i.e stop + play on the timeline) before interacting with any
            of the functions of this class.

        Args:
            physics_sim_view (omni.physics.tensors.SimulationView, optional): current physics simulation view. Defaults to None.
        """
        SingleRigidPrim.initialize(self, physics_sim_view=physics_sim_view)
        return

    @abstractmethod
    def open(self) -> None:
        """Applies actions to the articulation that opens the gripper (ex: to release an object held)."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Applies actions to the articulation that closes the gripper (ex: to hold an object)."""
        raise NotImplementedError

    @abstractmethod
    def set_default_state(self, *args, **kwargs):
        """Sets the default state of the gripper"""
        raise NotImplementedError

    @abstractmethod
    def get_default_state(self, *args, **kwargs):
        """Gets the default state of the gripper"""
        raise NotImplementedError

    @abstractmethod
    def forward(self, *args, **kwargs) -> ArticulationAction:
        """calculates the ArticulationAction for all of the articulation joints that corresponds to a specific action
           such as "open" for an example.

        Returns:
            ArticulationAction: articulation action to be passed to the articulation itself
                                (includes all joints of the articulation).
        """
        raise NotImplementedError
